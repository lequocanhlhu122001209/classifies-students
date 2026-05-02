"""
Module kết nối và đồng bộ dữ liệu từ SQL Server lên Supabase.
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

COURSE_NAME_TO_CODE = {
    "Nhập Môn Lập Trình": "NMLT",
    "Kĩ Thuật Lập Trình": "KTLT",
    "Cấu trúc Dữ Liệu và Giải Thuật": "CTDL",
    "Lập Trình Hướng Đối Tượng": "OOP",
    "NMLT": "NMLT",
    "KTLT": "KTLT",
    "CTDL": "CTDL",
    "OOP": "OOP",
}

INVALID_COURSE_CODE_VALUES = {"", "none", "null", "undefined", "na", "nan"}

SKILL_NAME_TO_CODE = {
    "Cú pháp cơ bản (Syntax)": "SYNTAX",
    "Biến và Kiểu dữ liệu (Variables & Data Types)": "VARIABLES",
    "Cấu trúc điều khiển (Control Structures)": "CONTROL",
    "Hàm cơ bản (Basic Functions)": "FUNCTIONS",
    "Thiết kế thuật toán (Algorithm Design)": "ALGORITHM_DESIGN",
    "Tối ưu hóa mã nguồn (Code Optimization)": "CODE_OPTIMIZATION",
    "Xử lý lỗi và Debugging (Error Handling)": "ERROR_HANDLING",
    "Lập trình có cấu trúc (Structured Programming)": "STRUCTURED_PROGRAMMING",
    "Mảng (Arrays)": "ARRAYS",
    "Danh sách liên kết (Linked Lists)": "LINKED_LISTS",
    "Stack và Queue": "STACK_QUEUE",
    "Cây (Trees)": "TREES",
    "Lớp và Đối tượng (Classes & Objects)": "CLASSES",
    "Kế thừa (Inheritance)": "INHERITANCE",
    "Đa hình (Polymorphism)": "POLYMORPHISM",
    "Đóng gói (Encapsulation)": "ENCAPSULATION",
}


def _create_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong file .env")

    from supabase import create_client

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def _chunked(items: List[Any], size: int = 500):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def load_students_from_supabase() -> List[Dict[str, Any]]:
    """Load student, csv, course, and classification data from Supabase."""
    supabase = _create_supabase_client()

    students_rows = supabase.table("students").select("*").execute().data or []
    csv_rows = supabase.table("student_csv_data").select("*").execute().data or []
    course_rows = supabase.table("course_scores").select("*").execute().data or []

    try:
        classification_rows = supabase.table("classifications").select("*").execute().data or []
    except Exception:
        classification_rows = []

    csv_by_student = {int(row.get("student_id", 0)): row for row in csv_rows}
    classifications_by_student = {int(row.get("student_id", 0)): row for row in classification_rows}

    students: List[Dict[str, Any]] = []
    student_lookup: Dict[int, Dict[str, Any]] = {}
    for row in students_rows:
        student_id = _safe_int(row.get("student_id"))
        student = {
            "student_id": student_id,
            "name": row.get("name", ""),
            "class": row.get("class", ""),
            "Khoa": row.get("khoa", "Khoa Cong Nghe Thong Tin"),
            "sex": row.get("sex", "Khong ro"),
            "csv_data": {
                "class": row.get("class", ""),
            },
            "courses": {},
        }

        csv_data = csv_by_student.get(student_id, {})
        if csv_data:
            student["csv_data"].update({
                "total_score": _safe_float(csv_data.get("total_score")),
                "midterm_score": _safe_float(csv_data.get("midterm_score")),
                "final_score": _safe_float(csv_data.get("final_score")),
                "homework_score": _safe_float(csv_data.get("homework_score")),
                "attendance_rate": _safe_float(csv_data.get("attendance_rate")),
                "behavior_score_100": _safe_int(csv_data.get("behavior_score_100"), 50),
                "late_submissions": _safe_int(csv_data.get("late_submissions")),
                "assignment_completion": _safe_float(csv_data.get("assignment_completion")),
                "study_hours_per_week": _safe_float(csv_data.get("study_hours_per_week")),
                "participation_score": _safe_float(csv_data.get("participation_score")),
                "lms_usage_hours": _safe_float(csv_data.get("lms_usage_hours")),
                "response_quality": _safe_float(csv_data.get("response_quality")),
            })

        classification = classifications_by_student.get(student_id, {})
        if classification:
            reasons = classification.get("anomaly_reasons") or []
            if not isinstance(reasons, list):
                reasons = [str(reasons)]
            student.update({
                "kmeans_prediction": classification.get("kmeans_prediction"),
                "knn_prediction": classification.get("knn_prediction"),
                "final_level": classification.get("final_level"),
                "anomaly_detected": bool(classification.get("anomaly_detected", False)),
                "anomaly_reasons": reasons,
                "anomaly_reason": " | ".join(reasons) if reasons else "",
            })

        students.append(student)
        student_lookup[student_id] = student

    reverse_course_map = {
        "NMLT": "Nhập Môn Lập Trình",
        "KTLT": "Kĩ Thuật Lập Trình",
        "CTDL": "Cấu trúc Dữ Liệu và Giải Thuật",
        "OOP": "Lập Trình Hướng Đối Tượng",
    }

    for row in course_rows:
        student_id = _safe_int(row.get("student_id"))
        student = student_lookup.get(student_id)
        if not student:
            continue

        raw_code = row.get("course_code") or row.get("course_name") or ""
        course_code = str(raw_code).strip()
        if not course_code:
            continue

        course_name = reverse_course_map.get(course_code, course_code)
        student["courses"][course_name] = {
            "course_code": course_code,
            "score": _safe_float(row.get("score")),
            "midterm_score": _safe_float(row.get("midterm_score")),
            "final_score": _safe_float(row.get("final_score")),
            "homework_score": _safe_float(row.get("homework_score")),
            "time_minutes": _safe_float(row.get("time_minutes")),
        }

    return students


def _normalize_course_code(course_name: Any, course_data: Dict[str, Any]) -> Optional[str]:
    candidates = [course_data.get("course_code"), course_name]

    for candidate in candidates:
        if candidate is None:
            continue

        text = str(candidate).strip()
        if not text:
            continue

        if text.lower() in INVALID_COURSE_CODE_VALUES:
            continue

        mapped = COURSE_NAME_TO_CODE.get(text) or COURSE_NAME_TO_CODE.get(text.upper())
        if mapped:
            return mapped

        return text

    return None


def _normalize_skill_code(skill_name: Any) -> Optional[str]:
    if skill_name is None:
        return None

    text = str(skill_name).strip()
    if not text:
        return None

    mapped = SKILL_NAME_TO_CODE.get(text)
    if mapped:
        return mapped

    # Remove accents and non-ascii, convert spaces to underscores
    import unicodedata
    normalized = unicodedata.normalize('NFD', text)
    no_accents = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    # Keep only ASCII letters/digits and underscores
    result = ''.join(ch for ch in no_accents.upper().replace(' ', '_') if (ord(ch) < 128 and (ch.isalnum() or ch == '_')))
    return (result or None)


def _to_students_rows(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for student in students:
        rows.append(
            {
                "student_id": int(student.get("student_id", 0)),
                "name": (student.get("name") or "")[:100],
                # Ensure class length fits DB schema
                "class": (student.get("class") or student.get("csv_data", {}).get("class", ""))[:20],
                "khoa": (student.get("Khoa") or student.get("khoa", "Khoa Công Nghệ Thông Tin"))[:100],
                "sex": (student.get("sex") or student.get("csv_data", {}).get("sex") or "Không rõ")[:10],
            }
        )
    return rows


def _to_csv_rows(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for student in students:
        csv_data = student.get("csv_data", {})
        rows.append(
            {
                "student_id": int(student.get("student_id", 0)),
                "midterm_score": float(csv_data.get("midterm_score", 0) or 0),
                "final_score": float(csv_data.get("final_score", 0) or 0),
                "homework_score": float(csv_data.get("homework_score", 0) or 0),
                "total_score": float(csv_data.get("total_score", 0) or 0),
                "attendance_rate": float(csv_data.get("attendance_rate", 0) or 0),
                "assignment_completion": float(csv_data.get("assignment_completion", 0) or 0),
                "study_hours_per_week": int(float(csv_data.get("study_hours_per_week", 0) or 0)),
                "participation_score": int(float(csv_data.get("participation_score", 0) or 0)),
                "late_submissions": int(float(csv_data.get("late_submissions", 0) or 0)),
                "lms_usage_hours": int(float(csv_data.get("lms_usage_hours", 0) or 0)),
                "response_quality": int(float(csv_data.get("response_quality", 0) or 0)),
                "behavior_score_100": int(float(csv_data.get("behavior_score_100", 0) or 0)),
            }
        )
    return rows


def _to_course_rows(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for student in students:
        sid = int(student.get("student_id", 0))
        courses = student.get("courses", {})
        for course_name, course_data in courses.items():
            if not isinstance(course_data, dict):
                continue

            course_code = _normalize_course_code(course_name, course_data)
            if not course_code:
                continue

            rows.append(
                {
                    "student_id": sid,
                    "course_code": course_code,
                    "score": float(course_data.get("score", 0) or 0),
                    "time_minutes": int(float(course_data.get("time_minutes", 0) or 0)),
                    "midterm_score": float(course_data.get("midterm_score", 0) or 0),
                    "final_score": float(course_data.get("final_score", 0) or 0),
                    "homework_score": float(course_data.get("homework_score", 0) or 0),
                }
            )
    return rows


def _to_classification_rows(classifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for row in classifications:
        reasons = row.get("anomaly_reasons")
        if reasons is None:
            reason = row.get("anomaly_reason")
            if reason:
                reasons = [reason]
            else:
                reasons = []

        rows.append(
            {
                "student_id": int(row.get("student_id", 0)),
                "kmeans_prediction": row.get("kmeans_prediction", ""),
                "knn_prediction": row.get("knn_prediction", ""),
                "final_level": row.get("final_level", ""),
                "normalization_method": row.get("normalization_method", "minmax"),
                "anomaly_detected": bool(row.get("anomaly_detected", False)),
                "anomaly_reasons": reasons,
            }
        )
    return rows


def _to_skill_rows(classifications: List[Dict[str, Any]], students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build skill_evaluations rows. Prefer `classifications` data (which contains
    evaluated skills for students with sufficient data). If a classification
    row lacks `skill_evaluations`, fall back to the original `students` list
    which may contain pre-computed `skill_evaluations` for all students.
    """
    rows = []

    # Build a lookup of students by id to allow fallback
    student_lookup = {int(s.get("student_id", 0)): s for s in (students or [])}

    source = classifications or students or []
    for row in source:
        student_id = int(row.get("student_id", 0))

        # Try classification's skill_evaluations first, then fallback to student entry
        skill_evaluations = row.get("skill_evaluations") if isinstance(row, dict) else None
        if not skill_evaluations:
            fallback = student_lookup.get(student_id)
            if fallback and isinstance(fallback, dict):
                skill_evaluations = fallback.get("skill_evaluations", {})

        skill_evaluations = skill_evaluations or {}

        for course_name, course_info in skill_evaluations.items():
            if not isinstance(course_info, dict):
                continue

            course_code = COURSE_NAME_TO_CODE.get(course_name) or _normalize_course_code(course_name, course_info)
            if not course_code:
                continue

            skills = course_info.get("skills", {}) or {}
            for skill_name, skill_info in skills.items():
                if not isinstance(skill_info, dict):
                    continue

                skill_code = _normalize_skill_code(skill_name)
                if not skill_code:
                    continue
                # Truncate fields to match Supabase schema limits
                skill_code = skill_code[:20]
                course_code = (course_code or '')[:10]
                level_val = (str(skill_info.get("level", "")) or "")[:20]

                rows.append(
                    {
                        "student_id": student_id,
                        "course_code": course_code,
                        "skill_code": skill_code,
                        "score": float(skill_info.get("score", 0) or 0),
                        "level": level_val,
                        "passed": bool(skill_info.get("passed", False)),
                    }
                )

    return rows


def _to_integrated_rows(integrated_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for row in integrated_results:
        components = row.get("components", {})
        exercise_data = row.get("exercise_data", {})
        rows.append(
            {
                "student_id": int(row.get("student_id", 0)),
                "original_score": float(row.get("original_score", 0) or 0),
                "integrated_score": float(row.get("integrated_score", 0) or 0),
                "score_difference": float(row.get("score_difference", 0) or 0),
                "classification": row.get("classification", ""),
                "exercise_avg": float(components.get("exercise_avg", 0) or 0),
                "midterm_avg": float(components.get("midterm", 0) or 0),
                "final_avg": float(components.get("final", 0) or 0),
                "total_exercises": int(float(exercise_data.get("total_exercises", 0) or 0)),
            }
        )
    return rows


def _sync_course_scores_rows(supabase, course_rows: List[Dict[str, Any]], student_ids: List[int]) -> None:
    try:
        for chunk in _chunked(course_rows):
            supabase.table("course_scores").upsert(chunk, on_conflict="student_id,course_code").execute()
        return
    except Exception as exc:
        # Some environments still use course_scores schema without a composite unique key.
        if "42P10" not in str(exc):
            raise

    for id_chunk in _chunked(student_ids):
        supabase.table("course_scores").delete().in_("student_id", id_chunk).execute()

    for chunk in _chunked(course_rows):
        supabase.table("course_scores").insert(chunk).execute()


def _sync_skill_rows(supabase, skill_rows: List[Dict[str, Any]], student_ids: List[int]) -> int:
    if not skill_rows:
        return 0

    try:
        for chunk in _chunked(skill_rows):
            supabase.table("skill_evaluations").upsert(chunk, on_conflict="student_id,course_code,skill_code").execute()
        return len(skill_rows)
    except Exception as exc:
        if "PGRST205" in str(exc):
            return 0
        if "42P10" not in str(exc):
            raise

    for id_chunk in _chunked(student_ids):
        supabase.table("skill_evaluations").delete().in_("student_id", id_chunk).execute()

    for chunk in _chunked(skill_rows):
        supabase.table("skill_evaluations").insert(chunk).execute()

    return len(skill_rows)


def sync_all_to_supabase(
    students: List[Dict[str, Any]],
    classifications: List[Dict[str, Any]] = None,
    integrated_results: List[Dict[str, Any]] = None,
) -> Dict[str, int]:
    """Đồng bộ dữ liệu từ SQL Server lên Supabase."""
    if not students:
        return {
            "students": 0,
            "student_csv_data": 0,
            "course_scores": 0,
            "classifications": 0,
            "integrated_scores": 0,
        }

    supabase = _create_supabase_client()

    student_rows = _to_students_rows(students)
    csv_rows = _to_csv_rows(students)
    course_rows = _to_course_rows(students)
    classification_rows = _to_classification_rows(classifications or [])
    # Use students as the authoritative source for skill_evaluations to ensure
    # we include evaluations computed before/independent of classification.
    skill_rows = _to_skill_rows([], students)
    integrated_rows = _to_integrated_rows(integrated_results or [])

    # Chống ghi trùng khi có nhiều request đồng thời.
    # Lấy bản ghi cuối cùng cho mỗi student_id.
    classification_rows = list({r["student_id"]: r for r in classification_rows}.values())

    student_ids = [r["student_id"] for r in student_rows]

    for chunk in _chunked(student_rows):
        supabase.table("students").upsert(chunk, on_conflict="student_id").execute()

    for chunk in _chunked(csv_rows):
        supabase.table("student_csv_data").upsert(chunk, on_conflict="student_id").execute()

    _sync_course_scores_rows(supabase, course_rows, student_ids)
    skill_synced_count = _sync_skill_rows(supabase, skill_rows, student_ids)

    if classification_rows:
        for chunk in _chunked(classification_rows):
            supabase.table("classifications").upsert(chunk, on_conflict="student_id").execute()

    if integrated_rows:
        for chunk in _chunked(integrated_rows):
            supabase.table("integrated_scores").upsert(chunk, on_conflict="student_id").execute()

    return {
        "students": len(student_rows),
        "student_csv_data": len(csv_rows),
        "course_scores": len(course_rows),
        "skill_evaluations": skill_synced_count,
        "classifications": len(classification_rows),
        "integrated_scores": len(integrated_rows),
    }

