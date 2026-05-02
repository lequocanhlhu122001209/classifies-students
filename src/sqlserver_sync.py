"""
Module kết nối và đồng bộ dữ liệu với SQL Server
"""

import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình SQL Server
SQL_SERVER = os.getenv("SQL_SERVER", "QUOC-ANH\\HP")
SQL_DATABASE = os.getenv("SQL_DATABASE", "StudentClassification")
SQL_USERNAME = os.getenv("SQL_USERNAME", "")  # Để trống nếu dùng Windows Auth
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")  # Để trống nếu dùng Windows Auth
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

def get_connection(database=None):
    """Tạo kết nối đến SQL Server"""
    try:
        db = database or SQL_DATABASE
        if SQL_USERNAME and SQL_PASSWORD:
            # SQL Server Authentication
            conn_str = (
                f"DRIVER={{{SQL_DRIVER}}};"
                f"SERVER={SQL_SERVER};"
                f"DATABASE={db};"
                f"UID={SQL_USERNAME};"
                f"PWD={SQL_PASSWORD};"
                "TrustServerCertificate=yes;"
            )
        else:
            # Windows Authentication
            conn_str = (
                f"DRIVER={{{SQL_DRIVER}}};"
                f"SERVER={SQL_SERVER};"
                f"DATABASE={db};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
        
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"❌ Lỗi kết nối SQL Server: {e}")
        return None

def create_database():
    """Tạo database nếu chưa tồn tại"""
    try:
        # Kết nối đến master database
        if SQL_USERNAME and SQL_PASSWORD:
            conn_str = (
                f"DRIVER={{{SQL_DRIVER}}};"
                f"SERVER={SQL_SERVER};"
                f"DATABASE=master;"
                f"UID={SQL_USERNAME};"
                f"PWD={SQL_PASSWORD};"
                "TrustServerCertificate=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{{SQL_DRIVER}}};"
                f"SERVER={SQL_SERVER};"
                f"DATABASE=master;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
        
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Kiểm tra và tạo database
        cursor.execute(f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{SQL_DATABASE}')
            BEGIN
                CREATE DATABASE [{SQL_DATABASE}]
            END
        """)
        
        conn.close()
        print(f"✅ Database '{SQL_DATABASE}' đã sẵn sàng")
        return True
    except Exception as e:
        print(f"❌ Lỗi tạo database: {e}")
        return False

def test_connection():
    """Test kết nối SQL Server"""
    # Tạo database trước
    if not create_database():
        return False
    
    conn = get_connection()
    if conn:
        print(f"✅ Kết nối thành công đến SQL Server: {SQL_SERVER}")
        print(f"   Database: {SQL_DATABASE}")
        conn.close()
        return True
    return False

def create_tables():
    """Tạo các bảng cần thiết trong SQL Server"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Bảng students - Thông tin sinh viên
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='students' AND xtype='U')
        CREATE TABLE students (
            student_id INT PRIMARY KEY,
            name NVARCHAR(100),
            class NVARCHAR(20),
            khoa NVARCHAR(100) DEFAULT N'Khoa Công Nghệ Thông Tin',
            sex NVARCHAR(10) DEFAULT N'Không rõ',
            total_score FLOAT DEFAULT 0,
            midterm_score FLOAT DEFAULT 0,
            final_score FLOAT DEFAULT 0,
            attendance_rate FLOAT DEFAULT 0,
            behavior_score_100 INT DEFAULT 50,
            late_submissions INT DEFAULT 0,
            assignment_completion FLOAT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
    """)

    # Bổ sung cột sex cho DB cũ (nếu bảng students đã tồn tại từ trước)
    cursor.execute("""
        IF COL_LENGTH('students', 'sex') IS NULL
        BEGIN
            ALTER TABLE students
            ADD sex NVARCHAR(10) DEFAULT N'Không rõ'
        END
    """)

    cursor.execute("""
        UPDATE students
        SET sex = N'Không rõ'
        WHERE sex IS NULL OR LTRIM(RTRIM(sex)) = ''
    """)
    
    # Bảng course_scores - Điểm từng môn học
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='course_scores' AND xtype='U')
        CREATE TABLE course_scores (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id INT,
            course_name NVARCHAR(100),
            score FLOAT DEFAULT 0,
            midterm_score FLOAT DEFAULT 0,
            final_score FLOAT DEFAULT 0,
            homework_score FLOAT DEFAULT 0,
            time_minutes FLOAT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    
    # Bảng classifications - Kết quả phân loại
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='classifications' AND xtype='U')
        CREATE TABLE classifications (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id INT,
            kmeans_prediction NVARCHAR(50),
            knn_prediction NVARCHAR(50),
            final_level NVARCHAR(50),
            anomaly_detected BIT DEFAULT 0,
            anomaly_reason NVARCHAR(500),
            classified_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    
    # Bảng skill_evaluations - Đánh giá kỹ năng
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='skill_evaluations' AND xtype='U')
        CREATE TABLE skill_evaluations (
            id INT IDENTITY(1,1) PRIMARY KEY,
            student_id INT,
            course_name NVARCHAR(100),
            skill_name NVARCHAR(100),
            score FLOAT DEFAULT 0,
            level NVARCHAR(50),
            passed BIT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Đã tạo các bảng trong SQL Server")
    return True

def load_students_from_sqlserver():
    """Load danh sách sinh viên từ SQL Server"""
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    students = []
    
    # Mapping course_code -> tên đầy đủ
    COURSE_CODE_TO_NAME = {
        'NMLT': 'Nhập Môn Lập Trình',
        'KTLT': 'Kĩ Thuật Lập Trình',
        'CTDL': 'Cấu trúc Dữ Liệu và Giải Thuật',
        'OOP': 'Lập Trình Hướng Đối Tượng'
    }
    
    try:
        # Load thông tin sinh viên + csv_data (JOIN 2 bảng)
        cursor.execute("""
            SELECT s.student_id, s.name, s.class, s.khoa, s.sex,
                   c.total_score, c.midterm_score, c.final_score, 
                   c.attendance_rate, c.behavior_score_100, 
                   c.late_submissions, c.assignment_completion,
                   c.study_hours_per_week, c.participation_score
            FROM students s
            LEFT JOIN student_csv_data c ON s.student_id = c.student_id
        """)
        
        rows = cursor.fetchall()

        # Hỗ trợ cả 2 schema course_scores: course_code (mới) hoặc course_name (cũ)
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'course_scores'
        """)
        course_columns = {c[0].lower() for c in cursor.fetchall()}
        course_col = 'course_code' if 'course_code' in course_columns else 'course_name'
        
        for row in rows:
            student = {
                "student_id": row[0],
                "name": row[1],
                "class": row[2],
                "Khoa": row[3],
                "sex": row[4] or "Không rõ",
                "csv_data": {
                    "total_score": row[5] or 0,
                    "midterm_score": row[6] or 0,
                    "final_score": row[7] or 0,
                    "attendance_rate": row[8] or 0,
                    "behavior_score_100": row[9] or 50,
                    "late_submissions": row[10] or 0,
                    "assignment_completion": row[11] or 0,
                    "study_hours_per_week": row[12] or 0,
                    "participation_score": row[13] or 0,
                    "class": row[2]
                },
                "courses": {}
            }
            
            # Load điểm các môn học
            cursor.execute(f"""
                SELECT {course_col}, score, midterm_score, final_score,
                       homework_score, time_minutes
                FROM course_scores
                WHERE student_id = ?
            """, row[0])
            
            course_rows = cursor.fetchall()
            for course in course_rows:
                course_code = course[0]
                course_name = COURSE_CODE_TO_NAME.get(course_code, course_code)
                student["courses"][course_name] = {
                    "score": course[1] or 0,
                    "midterm_score": course[2] or 0,
                    "final_score": course[3] or 0,
                    "homework_score": course[4] or 0,
                    "time_minutes": course[5] or 0
                }
            
            students.append(student)
        
        print(f"✅ Đã load {len(students)} sinh viên từ SQL Server")
        
    except Exception as e:
        print(f"❌ Lỗi load dữ liệu: {e}")
    
    conn.close()
    return students

def save_student(student):
    """Lưu thông tin 1 sinh viên vào SQL Server"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    csv_data = student.get("csv_data", {})
    
    try:
        # Upsert student
        cursor.execute("""
            MERGE INTO students AS target
            USING (SELECT ? AS student_id) AS source
            ON target.student_id = source.student_id
            WHEN MATCHED THEN
                UPDATE SET 
                    name = ?,
                    class = ?,
                    khoa = ?,
                    sex = ?,
                    total_score = ?,
                    midterm_score = ?,
                    final_score = ?,
                    attendance_rate = ?,
                    behavior_score_100 = ?,
                    late_submissions = ?,
                    assignment_completion = ?,
                    updated_at = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (student_id, name, class, khoa, sex, total_score, midterm_score, 
                        final_score, attendance_rate, behavior_score_100, 
                        late_submissions, assignment_completion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, 
            student.get("student_id"),
            student.get("name"),
            student.get("class") or csv_data.get("class"),
            student.get("Khoa", "Khoa Công Nghệ Thông Tin"),
            student.get("sex") or csv_data.get("sex") or "Không rõ",
            csv_data.get("total_score", 0),
            csv_data.get("midterm_score", 0),
            csv_data.get("final_score", 0),
            csv_data.get("attendance_rate", 0),
            csv_data.get("behavior_score_100", 50),
            csv_data.get("late_submissions", 0),
            csv_data.get("assignment_completion", 0),
            # Values for INSERT
            student.get("student_id"),
            student.get("name"),
            student.get("class") or csv_data.get("class"),
            student.get("Khoa", "Khoa Công Nghệ Thông Tin"),
            student.get("sex") or csv_data.get("sex") or "Không rõ",
            csv_data.get("total_score", 0),
            csv_data.get("midterm_score", 0),
            csv_data.get("final_score", 0),
            csv_data.get("attendance_rate", 0),
            csv_data.get("behavior_score_100", 50),
            csv_data.get("late_submissions", 0),
            csv_data.get("assignment_completion", 0)
        )
        
        # Lưu điểm các môn học
        courses = student.get("courses", {})
        for course_name, course_data in courses.items():
            cursor.execute("""
                MERGE INTO course_scores AS target
                USING (SELECT ? AS student_id, ? AS course_name) AS source
                ON target.student_id = source.student_id AND target.course_name = source.course_name
                WHEN MATCHED THEN
                    UPDATE SET 
                        score = ?,
                        midterm_score = ?,
                        final_score = ?,
                        homework_score = ?,
                        time_minutes = ?
                WHEN NOT MATCHED THEN
                    INSERT (student_id, course_name, score, midterm_score, final_score, homework_score, time_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
                student.get("student_id"),
                course_name,
                course_data.get("score", 0),
                course_data.get("midterm_score", 0),
                course_data.get("final_score", 0),
                course_data.get("homework_score", 0),
                course_data.get("time_minutes", 0),
                # Values for INSERT
                student.get("student_id"),
                course_name,
                course_data.get("score", 0),
                course_data.get("midterm_score", 0),
                course_data.get("final_score", 0),
                course_data.get("homework_score", 0),
                course_data.get("time_minutes", 0)
            )
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Lỗi lưu sinh viên {student.get('student_id')}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def save_classification(student):
    """Lưu kết quả phân loại vào SQL Server"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Xóa kết quả cũ
        cursor.execute("DELETE FROM classifications WHERE student_id = ?", student.get("student_id"))
        
        # Thêm kết quả mới
        cursor.execute("""
            INSERT INTO classifications (student_id, kmeans_prediction, knn_prediction, 
                                        final_level, anomaly_detected, anomaly_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            student.get("student_id"),
            student.get("kmeans_prediction"),
            student.get("knn_prediction"),
            student.get("final_level"),
            1 if student.get("anomaly_detected") else 0,
            student.get("anomaly_reason", "")
        )
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Lỗi lưu phân loại: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def sync_all_to_sqlserver(students, classifications):
    """Đồng bộ tất cả dữ liệu lên SQL Server"""
    print("\n📤 Đang đồng bộ dữ liệu lên SQL Server...")
    
    # Tạo bảng nếu chưa có
    create_tables()
    
    success_count = 0
    
    # Lưu sinh viên
    for student in students:
        if save_student(student):
            success_count += 1
    
    print(f"   ✅ Đã lưu {success_count}/{len(students)} sinh viên")
    
    # Lưu kết quả phân loại
    class_count = 0
    for student in classifications:
        if save_classification(student):
            class_count += 1
    
    print(f"   ✅ Đã lưu {class_count}/{len(classifications)} kết quả phân loại")
    
    return True


if __name__ == "__main__":
    # Test kết nối
    print("🔌 Testing SQL Server connection...")
    if test_connection():
        print("\n📊 Tạo bảng...")
        create_tables()
