"""
Tạo dữ liệu mẫu để huấn luyện/phân loại KMeans + KNN.

Dữ liệu bao gồm:
- Điểm từng môn học (4 môn)
- Thời gian học / làm bài từng môn
- Dữ liệu hành vi: tham gia, nộp bài trễ, giờ học
- Một tỷ lệ nhỏ mẫu bất thường để kiểm thử rule chống gian lận
"""

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sqlserver_sync import test_connection, create_tables, sync_all_to_sqlserver, get_connection
from student_classifier import StudentClassifier

try:
    from supabase_sync import sync_all_to_supabase
except Exception:
    sync_all_to_supabase = None


COURSES = [
    "Nhập Môn Lập Trình",
    "Kĩ Thuật Lập Trình",
    "Cấu trúc Dữ Liệu và Giải Thuật",
    "Lập Trình Hướng Đối Tượng",
]

CLASSES = ["25CT111", "25CT112", "25CT113", "24CT111", "24CT112"]


def clamp(value, low=0.0, high=10.0):
    return max(low, min(high, value))


def _build_student(student_id: int, profile: str):
    if profile == "excellent":
        base = random.uniform(8.2, 9.8)
        attendance = random.uniform(0.85, 1.0)
        late = random.randint(0, 3)
        study_hours = random.uniform(15, 35)
        behavior = random.randint(82, 100)
    elif profile == "good":
        base = random.uniform(7.0, 8.4)
        attendance = random.uniform(0.75, 0.95)
        late = random.randint(1, 6)
        study_hours = random.uniform(10, 25)
        behavior = random.randint(70, 90)
    elif profile == "average":
        base = random.uniform(5.2, 7.2)
        attendance = random.uniform(0.6, 0.85)
        late = random.randint(3, 10)
        study_hours = random.uniform(6, 18)
        behavior = random.randint(55, 80)
    else:
        base = random.uniform(2.5, 5.5)
        attendance = random.uniform(0.4, 0.75)
        late = random.randint(8, 20)
        study_hours = random.uniform(2, 12)
        behavior = random.randint(35, 70)

    courses = {}
    total = 0.0
    total_mid = 0.0
    total_final = 0.0
    total_homework = 0.0

    # 8% mẫu bất thường: điểm cao nhưng thời gian quá ngắn
    anomaly_mode = random.random() < 0.08

    for course in COURSES:
        score = clamp(base + random.uniform(-0.8, 0.8))
        mid = clamp(score + random.uniform(-1.0, 0.8))
        fin = clamp(score + random.uniform(-0.6, 1.0))
        hw = clamp(score + random.uniform(-0.8, 0.8))

        if anomaly_mode and score >= 8.0:
            time_minutes = random.uniform(8, 28)
        else:
            time_minutes = random.uniform(80, 280)

        courses[course] = {
            "score": round(score, 2),
            "midterm_score": round(mid, 2),
            "final_score": round(fin, 2),
            "homework_score": round(hw, 2),
            "time_minutes": round(time_minutes, 1),
        }

        total += score
        total_mid += mid
        total_final += fin
        total_homework += hw

    count = len(COURSES)
    total_score = total / count

    student = {
        "student_id": student_id,
        "name": f"Sinh viên mẫu {student_id}",
        "class": random.choice(CLASSES),
        "Khoa": "Khoa Công Nghệ Thông Tin",
        "sex": random.choice(["Nam", "Nữ"]),
        "courses": courses,
        "csv_data": {
            "total_score": round(total_score, 2),
            "midterm_score": round(total_mid / count, 2),
            "final_score": round(total_final / count, 2),
            "homework_score": round(total_homework / count, 2),
            "attendance_rate": round(attendance, 2),
            "behavior_score_100": int(behavior),
            "late_submissions": int(late),
            "assignment_completion": round(max(0.3, min(1.0, 1 - late / 25)), 2),
            "study_hours_per_week": round(study_hours, 1),
            "participation_score": random.randint(50, 100),
            "lms_usage_hours": round(random.uniform(2, 20), 1),
            "response_quality": random.randint(40, 100),
        },
    }

    return student


def generate_sample_students(total_students: int, seed: int):
    random.seed(seed)

    profiles = (
        ["excellent"] * int(total_students * 0.2)
        + ["good"] * int(total_students * 0.35)
        + ["average"] * int(total_students * 0.3)
        + ["weak"] * (total_students - int(total_students * 0.2) - int(total_students * 0.35) - int(total_students * 0.3))
    )
    random.shuffle(profiles)

    start_id = 125001000
    students = []
    for i, profile in enumerate(profiles):
        students.append(_build_student(start_id + i + 1, profile))

    return students


def clear_existing_data():
    conn = get_connection()
    if not conn:
        raise RuntimeError("Không mở được kết nối SQL để xóa dữ liệu cũ")

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM classifications")
        cursor.execute("DELETE FROM course_scores")
        cursor.execute("DELETE FROM student_csv_data")
        cursor.execute("DELETE FROM students")
        conn.commit()
        print("✅ Đã xóa dữ liệu cũ trong SQL Server")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed dữ liệu mẫu cho KMeans + KNN")
    parser.add_argument("--count", type=int, default=300, help="Số sinh viên mẫu cần tạo")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--sync-supabase", action="store_true", help="Đồng bộ lên Supabase sau khi lưu SQL")
    parser.add_argument("--replace", action="store_true", help="Xóa dữ liệu cũ trước khi seed")
    args = parser.parse_args()

    print("=" * 70)
    print("SEED DỮ LIỆU MẪU KMEANS + KNN")
    print("=" * 70)

    if not test_connection():
        print("❌ Không kết nối được SQL Server")
        return

    create_tables()
    if args.replace:
        clear_existing_data()

    students = generate_sample_students(args.count, args.seed)

    classifier = StudentClassifier(n_clusters=4, normalization_method="minmax")
    classifier.fit(students)
    classified_students = classifier.predict(students)

    sync_all_to_sqlserver(students, classified_students)
    print(f"✅ Đã tạo và lưu {len(students)} sinh viên mẫu vào SQL Server")

    if args.sync_supabase:
        if sync_all_to_supabase is None:
            print("⚠️ Không import được supabase_sync, bỏ qua đồng bộ Supabase")
        else:
            try:
                stats = sync_all_to_supabase(students, classified_students, [])
                print(f"✅ Đồng bộ Supabase thành công: {stats}")
            except Exception as e:
                print(f"⚠️ Đồng bộ Supabase thất bại: {e}")


if __name__ == "__main__":
    main()
