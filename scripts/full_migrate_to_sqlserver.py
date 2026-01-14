"""
Script migrate ĐẦY ĐỦ cấu trúc và dữ liệu từ Supabase sang SQL Server
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pyodbc
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

# Supabase config
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# SQL Server config
SQL_SERVER = os.getenv('SQL_SERVER', '(local)')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'StudentClassification')
SQL_DRIVER = os.getenv('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')

def get_sql_connection(database='master'):
    """Kết nối SQL Server"""
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, autocommit=True)

def create_database():
    """Tạo database"""
    print("\n[1] Tạo database...")
    conn = get_sql_connection('master')
    cursor = conn.cursor()
    
    cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{SQL_DATABASE}')
        CREATE DATABASE [{SQL_DATABASE}]
    """)
    
    conn.close()
    print(f"   ✅ Database '{SQL_DATABASE}' đã sẵn sàng")

def create_tables():
    """Tạo tất cả các bảng theo cấu trúc Supabase"""
    print("\n[2] Tạo các bảng...")
    conn = get_sql_connection(SQL_DATABASE)
    cursor = conn.cursor()
    
    # Drop existing tables (theo thứ tự FK)
    tables_to_drop = [
        'exercise_details', 'integrated_scores', 'classifications',
        'skill_evaluations', 'course_scores', 'student_csv_data', 'students'
    ]
    
    for table in tables_to_drop:
        cursor.execute(f"IF OBJECT_ID('{table}', 'U') IS NOT NULL DROP TABLE {table}")
    
    # 1. students
    cursor.execute("""
        CREATE TABLE students (
            student_id INT PRIMARY KEY,
            name NVARCHAR(100),
            class NVARCHAR(20),
            khoa NVARCHAR(100) DEFAULT N'Khoa Công Nghệ Thông Tin',
            sex NVARCHAR(10),
            created_at DATETIME DEFAULT GETDATE()
        )
    """)
    print("   ✅ Bảng students")
    
    # 2. student_csv_data
    cursor.execute("""
        CREATE TABLE student_csv_data (
            student_id INT PRIMARY KEY,
            midterm_score FLOAT DEFAULT 0,
            final_score FLOAT DEFAULT 0,
            homework_score FLOAT DEFAULT 0,
            total_score FLOAT DEFAULT 0,
            attendance_rate FLOAT DEFAULT 0,
            assignment_completion FLOAT DEFAULT 0,
            study_hours_per_week INT DEFAULT 0,
            participation_score INT DEFAULT 0,
            late_submissions INT DEFAULT 0,
            lms_usage_hours INT DEFAULT 0,
            response_quality INT DEFAULT 0,
            behavior_score_100 INT DEFAULT 50,
            class NVARCHAR(20),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    print("   ✅ Bảng student_csv_data")
    
    # 3. course_scores
    cursor.execute("""
        CREATE TABLE course_scores (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id INT,
            course_code NVARCHAR(10),
            score FLOAT DEFAULT 0,
            time_minutes FLOAT DEFAULT 0,
            midterm_score FLOAT DEFAULT 0,
            final_score FLOAT DEFAULT 0,
            homework_score FLOAT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            CONSTRAINT UQ_course_scores UNIQUE (student_id, course_code)
        )
    """)
    print("   ✅ Bảng course_scores")
    
    # 4. skill_evaluations
    cursor.execute("""
        CREATE TABLE skill_evaluations (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id INT,
            course_code NVARCHAR(10),
            skill_code NVARCHAR(30),
            score FLOAT DEFAULT 0,
            level NVARCHAR(20),
            passed BIT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            CONSTRAINT UQ_skill_evaluations UNIQUE (student_id, course_code, skill_code)
        )
    """)
    print("   ✅ Bảng skill_evaluations")
    
    # 5. classifications
    cursor.execute("""
        CREATE TABLE classifications (
            student_id INT PRIMARY KEY,
            kmeans_prediction NVARCHAR(30),
            knn_prediction NVARCHAR(30),
            final_level NVARCHAR(30),
            normalization_method NVARCHAR(20) DEFAULT 'minmax',
            anomaly_detected BIT DEFAULT 0,
            anomaly_reasons NVARCHAR(MAX),
            classified_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    print("   ✅ Bảng classifications")
    
    # 6. integrated_scores
    cursor.execute("""
        CREATE TABLE integrated_scores (
            student_id INT PRIMARY KEY,
            original_score FLOAT DEFAULT 0,
            integrated_score FLOAT DEFAULT 0,
            score_difference FLOAT DEFAULT 0,
            classification NVARCHAR(30),
            exercise_avg FLOAT DEFAULT 0,
            midterm_avg FLOAT DEFAULT 0,
            final_avg FLOAT DEFAULT 0,
            total_exercises INT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    print("   ✅ Bảng integrated_scores")
    
    # 7. exercise_details
    cursor.execute("""
        CREATE TABLE exercise_details (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id INT,
            course_code NVARCHAR(10),
            skill_code NVARCHAR(30),
            exercise_number INT,
            score FLOAT DEFAULT 0,
            completion_time FLOAT DEFAULT 0,
            is_anomaly BIT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            CONSTRAINT UQ_exercise_details UNIQUE (student_id, course_code, skill_code, exercise_number)
        )
    """)
    print("   ✅ Bảng exercise_details")
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_course_scores_student ON course_scores(student_id)")
    cursor.execute("CREATE INDEX idx_skill_evaluations_student ON skill_evaluations(student_id)")
    cursor.execute("CREATE INDEX idx_exercise_details_student ON exercise_details(student_id)")
    print("   ✅ Đã tạo indexes")
    
    conn.close()

def migrate_data():
    """Migrate dữ liệu từ Supabase"""
    print("\n[3] Migrate dữ liệu từ Supabase...")
    
    # Kết nối Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    conn = get_sql_connection(SQL_DATABASE)
    cursor = conn.cursor()
    
    # 3.1 Students
    print("\n   📥 Đang load bảng students...")
    result = supabase.table('students').select('*').execute()
    students = result.data
    print(f"      Tìm thấy {len(students)} sinh viên")
    
    for s in students:
        cursor.execute("""
            INSERT INTO students (student_id, name, class, khoa, sex)
            VALUES (?, ?, ?, ?, ?)
        """, s.get('student_id'), s.get('name'), s.get('class'), 
            s.get('khoa', 'Khoa Công Nghệ Thông Tin'), s.get('sex'))
    print(f"      ✅ Đã insert {len(students)} sinh viên")
    
    # 3.2 Student CSV Data
    print("\n   📥 Đang load bảng student_csv_data...")
    result = supabase.table('student_csv_data').select('*').execute()
    csv_data = result.data
    print(f"      Tìm thấy {len(csv_data)} bản ghi")
    
    for c in csv_data:
        cursor.execute("""
            INSERT INTO student_csv_data (
                student_id, midterm_score, final_score, homework_score, total_score,
                attendance_rate, assignment_completion, study_hours_per_week,
                participation_score, late_submissions, lms_usage_hours,
                response_quality, behavior_score_100, class
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, 
            c.get('student_id'),
            c.get('midterm_score', 0),
            c.get('final_score', 0),
            c.get('homework_score', 0),
            c.get('total_score', 0),
            c.get('attendance_rate', 0),
            c.get('assignment_completion', 0),
            c.get('study_hours_per_week', 0),
            c.get('participation_score', 0),
            c.get('late_submissions', 0),
            c.get('lms_usage_hours', 0),
            c.get('response_quality', 0),
            c.get('behavior_score_100', 50),
            c.get('class')
        )
    print(f"      ✅ Đã insert {len(csv_data)} bản ghi")
    
    # 3.3 Course Scores
    print("\n   📥 Đang load bảng course_scores...")
    result = supabase.table('course_scores').select('*').execute()
    scores = result.data
    print(f"      Tìm thấy {len(scores)} bản ghi")
    
    for s in scores:
        cursor.execute("""
            INSERT INTO course_scores (
                student_id, course_code, score, time_minutes,
                midterm_score, final_score, homework_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            s.get('student_id'),
            s.get('course_code'),
            s.get('score', 0),
            s.get('time_minutes', 0),
            s.get('midterm_score', 0),
            s.get('final_score', 0),
            s.get('homework_score', 0)
        )
    print(f"      ✅ Đã insert {len(scores)} bản ghi")
    
    # 3.4 Skill Evaluations
    print("\n   📥 Đang load bảng skill_evaluations...")
    result = supabase.table('skill_evaluations').select('*').execute()
    skills = result.data
    print(f"      Tìm thấy {len(skills)} bản ghi")
    
    for s in skills:
        cursor.execute("""
            INSERT INTO skill_evaluations (
                student_id, course_code, skill_code, score, level, passed
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            s.get('student_id'),
            s.get('course_code'),
            s.get('skill_code'),
            s.get('score', 0),
            s.get('level'),
            1 if s.get('passed') else 0
        )
    print(f"      ✅ Đã insert {len(skills)} bản ghi")
    
    # 3.5 Classifications
    print("\n   📥 Đang load bảng classifications...")
    result = supabase.table('classifications').select('*').execute()
    classifications = result.data
    print(f"      Tìm thấy {len(classifications)} bản ghi")
    
    inserted = 0
    seen_ids = set()
    for c in classifications:
        student_id = c.get('student_id')
        if student_id in seen_ids:
            continue  # Skip duplicate
        seen_ids.add(student_id)
        
        import json
        anomaly_reasons = c.get('anomaly_reasons', [])
        if isinstance(anomaly_reasons, list):
            anomaly_reasons = json.dumps(anomaly_reasons, ensure_ascii=False)
        
        try:
            cursor.execute("""
                INSERT INTO classifications (
                    student_id, kmeans_prediction, knn_prediction, final_level,
                    normalization_method, anomaly_detected, anomaly_reasons
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                student_id,
                c.get('kmeans_prediction'),
                c.get('knn_prediction'),
                c.get('final_level'),
                c.get('normalization_method', 'minmax'),
                1 if c.get('anomaly_detected') else 0,
                anomaly_reasons
            )
            inserted += 1
        except:
            pass  # Skip duplicates
    print(f"      ✅ Đã insert {inserted} bản ghi")
    
    # 3.6 Integrated Scores
    print("\n   📥 Đang load bảng integrated_scores...")
    result = supabase.table('integrated_scores').select('*').execute()
    integrated = result.data
    print(f"      Tìm thấy {len(integrated)} bản ghi")
    
    inserted = 0
    seen_ids = set()
    for i in integrated:
        student_id = i.get('student_id')
        if student_id in seen_ids:
            continue
        seen_ids.add(student_id)
        
        try:
            cursor.execute("""
                INSERT INTO integrated_scores (
                    student_id, original_score, integrated_score, score_difference,
                    classification, exercise_avg, midterm_avg, final_avg, total_exercises
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                student_id,
                i.get('original_score', 0),
                i.get('integrated_score', 0),
                i.get('score_difference', 0),
                i.get('classification'),
                i.get('exercise_avg', 0),
                i.get('midterm_avg', 0),
                i.get('final_avg', 0),
                i.get('total_exercises', 0)
            )
            inserted += 1
        except:
            pass
    print(f"      ✅ Đã insert {inserted} bản ghi")
    
    # 3.7 Exercise Details
    print("\n   📥 Đang load bảng exercise_details...")
    result = supabase.table('exercise_details').select('*').execute()
    exercises = result.data
    print(f"      Tìm thấy {len(exercises)} bản ghi")
    
    batch_size = 1000
    for idx in range(0, len(exercises), batch_size):
        batch = exercises[idx:idx + batch_size]
        for e in batch:
            try:
                cursor.execute("""
                    INSERT INTO exercise_details (
                        student_id, course_code, skill_code, exercise_number,
                        score, completion_time, is_anomaly
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    e.get('student_id'),
                    e.get('course_code'),
                    e.get('skill_code'),
                    e.get('exercise_number'),
                    e.get('score', 0),
                    e.get('completion_time', 0),
                    1 if e.get('is_anomaly') else 0
                )
            except:
                pass  # Skip duplicates
        print(f"      Đã xử lý {min(idx + batch_size, len(exercises))}/{len(exercises)}...")
    
    print(f"      ✅ Đã insert exercise_details")
    
    conn.close()

def print_summary():
    """In tổng kết"""
    print("\n" + "=" * 60)
    print("📊 TỔNG KẾT")
    print("=" * 60)
    
    conn = get_sql_connection(SQL_DATABASE)
    cursor = conn.cursor()
    
    tables = [
        'students', 'student_csv_data', 'course_scores',
        'skill_evaluations', 'classifications', 'integrated_scores', 'exercise_details'
    ]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} bản ghi")
    
    conn.close()
    print("\n✅ Migration hoàn tất!")

def main():
    print("=" * 60)
    print("🔄 MIGRATE ĐẦY ĐỦ TỪ SUPABASE SANG SQL SERVER")
    print("=" * 60)
    print(f"   Server: {SQL_SERVER}")
    print(f"   Database: {SQL_DATABASE}")
    
    create_database()
    create_tables()
    migrate_data()
    print_summary()

if __name__ == "__main__":
    main()
