"""
Script tạo dữ liệu random cho sinh viên chưa đủ dữ liệu
"""

import pyodbc
import random
import os
from dotenv import load_dotenv

load_dotenv()

SQL_SERVER = os.getenv("SQL_SERVER", "(local)")
SQL_DATABASE = os.getenv("SQL_DATABASE", "StudentClassification")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

def get_connection():
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def get_students_missing_data():
    """Lấy danh sách sinh viên chưa đủ dữ liệu"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tìm sinh viên không có trong student_csv_data hoặc không có course_scores
    cursor.execute("""
        SELECT s.student_id, s.name, s.class
        FROM students s
        WHERE NOT EXISTS (
            SELECT 1 FROM student_csv_data c WHERE c.student_id = s.student_id
        )
        OR NOT EXISTS (
            SELECT 1 FROM course_scores cs WHERE cs.student_id = s.student_id
        )
    """)
    
    students = cursor.fetchall()
    conn.close()
    return students

def generate_random_profile():
    """Tạo profile ngẫu nhiên cho sinh viên"""
    profile_type = random.choices(
        ['excellent', 'good', 'average', 'weak'],
        weights=[15, 25, 40, 20]  # Phân bố thực tế
    )[0]
    
    if profile_type == 'excellent':
        return {
            'base_score': random.uniform(8.5, 10.0),
            'attendance': random.uniform(0.90, 1.0),
            'behavior': random.randint(85, 100),
            'late_submissions': random.randint(0, 3),
            'study_hours': random.randint(20, 35),
            'time_per_course': random.uniform(150, 300)
        }
    elif profile_type == 'good':
        return {
            'base_score': random.uniform(7.0, 8.5),
            'attendance': random.uniform(0.80, 0.95),
            'behavior': random.randint(70, 90),
            'late_submissions': random.randint(2, 8),
            'study_hours': random.randint(15, 25),
            'time_per_course': random.uniform(100, 200)
        }
    elif profile_type == 'average':
        return {
            'base_score': random.uniform(5.0, 7.0),
            'attendance': random.uniform(0.60, 0.85),
            'behavior': random.randint(50, 75),
            'late_submissions': random.randint(5, 15),
            'study_hours': random.randint(8, 18),
            'time_per_course': random.uniform(60, 150)
        }
    else:  # weak
        return {
            'base_score': random.uniform(2.0, 5.0),
            'attendance': random.uniform(0.30, 0.65),
            'behavior': random.randint(30, 55),
            'late_submissions': random.randint(10, 25),
            'study_hours': random.randint(3, 12),
            'time_per_course': random.uniform(20, 80)
        }

def fill_student_csv_data(cursor, student_id, profile):
    """Thêm dữ liệu vào bảng student_csv_data"""
    base = profile['base_score']
    
    # Tạo điểm với độ biến thiên nhỏ
    midterm = max(0, min(10, base + random.uniform(-1.5, 1.0)))
    final = max(0, min(10, base + random.uniform(-1.0, 1.5)))
    homework = max(0, min(10, base + random.uniform(-0.5, 0.5)))
    total = (midterm * 0.3 + final * 0.5 + homework * 0.2)
    
    cursor.execute("""
        MERGE INTO student_csv_data AS target
        USING (SELECT ? AS student_id) AS source
        ON target.student_id = source.student_id
        WHEN MATCHED THEN
            UPDATE SET 
                midterm_score = ?,
                final_score = ?,
                homework_score = ?,
                total_score = ?,
                attendance_rate = ?,
                assignment_completion = ?,
                study_hours_per_week = ?,
                participation_score = ?,
                late_submissions = ?,
                lms_usage_hours = ?,
                response_quality = ?,
                behavior_score_100 = ?
        WHEN NOT MATCHED THEN
            INSERT (student_id, midterm_score, final_score, homework_score, total_score,
                    attendance_rate, assignment_completion, study_hours_per_week,
                    participation_score, late_submissions, lms_usage_hours,
                    response_quality, behavior_score_100)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
        student_id,
        round(midterm, 2), round(final, 2), round(homework, 2), round(total, 2),
        round(profile['attendance'], 2),
        round(random.uniform(0.6, 1.0), 2),  # assignment_completion
        profile['study_hours'],
        random.randint(5, 10),  # participation_score
        profile['late_submissions'],
        random.randint(5, 30),  # lms_usage_hours
        random.randint(5, 10),  # response_quality
        profile['behavior'],
        # INSERT values
        student_id,
        round(midterm, 2), round(final, 2), round(homework, 2), round(total, 2),
        round(profile['attendance'], 2),
        round(random.uniform(0.6, 1.0), 2),
        profile['study_hours'],
        random.randint(5, 10),
        profile['late_submissions'],
        random.randint(5, 30),
        random.randint(5, 10),
        profile['behavior']
    )

def fill_course_scores(cursor, student_id, profile):
    """Thêm điểm các môn học"""
    courses = ['NMLT', 'KTLT', 'CTDL', 'OOP']
    base = profile['base_score']
    
    for course in courses:
        # Điểm mỗi môn dao động quanh base_score
        score = max(0, min(10, base + random.uniform(-1.5, 1.5)))
        midterm = max(0, min(10, score + random.uniform(-1.0, 1.0)))
        final = max(0, min(10, score + random.uniform(-0.5, 0.5)))
        homework = max(0, min(10, score + random.uniform(-0.3, 0.3)))
        time_minutes = profile['time_per_course'] + random.uniform(-30, 30)
        
        cursor.execute("""
            MERGE INTO course_scores AS target
            USING (SELECT ? AS student_id, ? AS course_code) AS source
            ON target.student_id = source.student_id AND target.course_code = source.course_code
            WHEN MATCHED THEN
                UPDATE SET 
                    score = ?,
                    midterm_score = ?,
                    final_score = ?,
                    homework_score = ?,
                    time_minutes = ?
            WHEN NOT MATCHED THEN
                INSERT (student_id, course_code, score, midterm_score, final_score, homework_score, time_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
            student_id, course,
            round(score, 2), round(midterm, 2), round(final, 2), round(homework, 2), round(time_minutes, 1),
            student_id, course,
            round(score, 2), round(midterm, 2), round(final, 2), round(homework, 2), round(time_minutes, 1)
        )

def main():
    print("=" * 60)
    print("🔧 Fill Missing Data - Tạo dữ liệu cho sinh viên thiếu")
    print("=" * 60)
    
    # Lấy danh sách sinh viên thiếu dữ liệu
    students = get_students_missing_data()
    print(f"\n📊 Tìm thấy {len(students)} sinh viên chưa đủ dữ liệu")
    
    if not students:
        print("✅ Tất cả sinh viên đã có đủ dữ liệu!")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    success = 0
    for student_id, name, class_name in students:
        try:
            profile = generate_random_profile()
            fill_student_csv_data(cursor, student_id, profile)
            fill_course_scores(cursor, student_id, profile)
            success += 1
            print(f"  ✓ {student_id} - {name} ({class_name})")
        except Exception as e:
            print(f"  ✗ {student_id} - Lỗi: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Đã tạo dữ liệu cho {success}/{len(students)} sinh viên")
    print("=" * 60)

if __name__ == "__main__":
    random.seed(42)  # Để kết quả nhất quán
    main()
