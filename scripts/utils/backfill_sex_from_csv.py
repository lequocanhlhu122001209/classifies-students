"""
Backfill student sex from CSV into SQL Server, then optionally sync to Supabase.

Usage:
  python scripts/utils/backfill_sex_from_csv.py --export-template db/migrations/sex_backfill_template.csv
  python scripts/utils/backfill_sex_from_csv.py --apply db/migrations/sex_backfill_template.csv --sync-supabase

CSV format:
  student_id,sex
  122001001,Nam
  122001002,Nữ
"""

import argparse
import csv
import os
import random
import sys
import unicodedata
from typing import Dict, List, Tuple

from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sqlserver_sync import get_connection, load_students_from_sqlserver  # noqa: E402
from supabase_sync import sync_all_to_supabase  # noqa: E402


def normalize_sex(value: str) -> str:
    text = (value or "").strip().lower()
    if not text:
        return ""

    # Remove accents for robust matching (e.g. "Nữ" -> "nu")
    no_accent = "".join(
        ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn"
    )

    if no_accent in {"nam", "male", "m"}:
        return "Nam"
    if no_accent in {"nu", "female", "f"}:
        return "Nữ"
    if no_accent in {"khong ro", "unknown", "", "na", "n/a"}:
        return "Không rõ"

    return ""


def get_unknown_students() -> List[Tuple[int, str, str, str]]:
    students = load_students_from_sqlserver()
    unknown_rows: List[Tuple[int, str, str, str]] = []

    for st in students:
        sid = int(st.get("student_id", 0))
        name = st.get("name", "")
        class_name = st.get("class", "")
        sex = st.get("sex", "")
        normalized = normalize_sex(str(sex))
        if normalized not in {"Nam", "Nữ"}:
            unknown_rows.append((sid, name, class_name, sex or ""))

    return unknown_rows


def export_template(csv_path: str) -> int:
    rows = get_unknown_students()
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "class", "sex"])
        for row in rows:
            writer.writerow(row)

    return len(rows)


def apply_csv(csv_path: str) -> Dict[str, int]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Không tìm thấy file CSV: {csv_path}")

    conn = get_connection()
    if not conn:
        raise RuntimeError("Không kết nối được SQL Server")

    cursor = conn.cursor()
    updated = 0
    skipped = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid_raw = (row.get("student_id") or "").strip()
            sex_raw = (row.get("sex") or "").strip()

            if not sid_raw:
                skipped += 1
                continue

            try:
                sid = int(sid_raw)
            except ValueError:
                skipped += 1
                continue

            sex = normalize_sex(sex_raw)
            if sex not in {"Nam", "Nữ"}:
                skipped += 1
                continue

            cursor.execute("UPDATE students SET sex = ? WHERE student_id = ?", sex, sid)
            updated += cursor.rowcount

    conn.commit()
    conn.close()

    return {"updated": updated, "skipped": skipped}


def random_fill_unknown(seed: int = 42) -> Dict[str, int]:
    conn = get_connection()
    if not conn:
        raise RuntimeError("Không kết nối được SQL Server")

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT student_id
        FROM students
        WHERE sex IS NULL
           OR LTRIM(RTRIM(sex)) = ''
           OR LTRIM(RTRIM(sex)) = N'Không rõ'
        ORDER BY student_id
        """
    )
    student_ids = [int(row[0]) for row in cursor.fetchall()]

    if not student_ids:
        conn.close()
        return {"updated": 0}

    rng = random.Random(seed)
    updates: List[Tuple[str, int]] = []
    for sid in student_ids:
        sex = rng.choice(["Nam", "Nữ"])
        updates.append((sex, sid))

    cursor.executemany("UPDATE students SET sex = ? WHERE student_id = ?", updates)
    conn.commit()
    conn.close()

    return {"updated": len(student_ids)}


def main() -> None:
    load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

    parser = argparse.ArgumentParser(description="Backfill sex from CSV")
    parser.add_argument("--export-template", dest="export_template_path", help="Path to export unknown-sex template CSV")
    parser.add_argument("--apply", dest="apply_csv_path", help="Path to CSV containing student_id,sex")
    parser.add_argument("--random-fill-unknown", action="store_true", help="Random fill Nam/Nữ for unknown sex in SQL Server")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for --random-fill-unknown")
    parser.add_argument("--sync-supabase", action="store_true", help="Sync SQL data to Supabase after apply")
    args = parser.parse_args()

    if args.export_template_path:
        count = export_template(args.export_template_path)
        print(f"Đã xuất template: {args.export_template_path}")
        print(f"Số sinh viên cần cập nhật sex: {count}")

    if args.apply_csv_path:
        result = apply_csv(args.apply_csv_path)
        print(f"Đã cập nhật: {result['updated']}")
        print(f"Bỏ qua: {result['skipped']}")

        if args.sync_supabase:
            students = load_students_from_sqlserver()
            stats = sync_all_to_supabase(students, [])
            print("Đã sync lên Supabase:", stats)

    if args.random_fill_unknown:
        result = random_fill_unknown(seed=args.seed)
        print(f"Đã random giới tính cho: {result['updated']}")

        if args.sync_supabase:
            students = load_students_from_sqlserver()
            stats = sync_all_to_supabase(students, [])
            print("Đã sync lên Supabase:", stats)

    if not args.export_template_path and not args.apply_csv_path and not args.random_fill_unknown:
        parser.print_help()


if __name__ == "__main__":
    main()
