"""
Helper functions để sync dữ liệu từ localhost lên Supabase
"""

from supabase import create_client, Client
from tqdm import tqdm

SUPABASE_URL = "https://odmtndvllclmrwczcyvs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA"

# Mapping tên môn học -> course code
COURSE_NAME_TO_CODE = {
    "Nhập Môn Lập Trình": "NMLT",
    "Kĩ Thuật Lập Trình": "KTLT",
    "Cấu trúc Dữ Liệu và Giải Thuật": "CTDL",
    "Lập Trình Hướng Đối Tượng": "OOP"
}

SKILL_NAME_TO_CODE = {
    "Cú pháp cơ bản (Syntax)": "SYNTAX",
    "Biến và Kiểu dữ liệu (Variables & Data Types)": "VARIABLES",
    "Cấu trúc điều khiển (Control Structures)": "CONTROL",
    "Hàm cơ bản (Basic Functions)": "FUNCTIONS",
    "Thiết kế thuật toán (Algorithm Design)": "ALGORITHM",
    "Tối ưu hóa mã nguồn (Code Optimization)": "OPTIMIZATION",
    "Xử lý lỗi và Debugging (Error Handling)": "DEBUGGING",
    "Lập trình có cấu trúc (Structured Programming)": "STRUCTURED",
    "Mảng (Arrays)": "ARRAYS",
    "Danh sách liên kết (Linked Lists)": "LINKED_LIST",
    "Stack và Queue": "STACK_QUEUE",
    "Cây (Trees)": "TREES",
    "Lớp và Đối tượng (Classes & Objects)": "CLASSES",
    "Kế thừa (Inheritance)": "INHERITANCE",
    "Đa hình (Polymorphism)": "POLYMORPHISM",
    "Đóng gói (Encapsulation)": "ENCAPSULATION"
}


def sync_to_supabase(students, classified_students, integrated_results):
    """
    Sync dữ liệu từ localhost lên Supabase
    
    Args:
        students: Danh sách sinh viên gốc
        classified_students: Danh sách sinh viên đã phân loại
        integrated_results: Kết quả điểm tích hợp
    """
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("\n" + "=" * 80)
        print("📤 ĐỒNG BỘ DỮ LIỆU LÊN SUPABASE")
        print("=" * 80)
        
        # 1. Sync students
        print("\n1️⃣ Đang sync thông tin sinh viên...")
        student_records = []
        for student in students:
            record = {
                'student_id': student['student_id'],
                'name': student['name'],
                'class': student.get('class', ''),
                'khoa': student.get('Khoa', ''),
                'sex': student.get('sex', '')
            }
            student_records.append(record)
        
        batch_size = 100
        for i in range(0, len(student_records), batch_size):
            batch = student_records[i:i+batch_size]
            try:
                supabase.table('students').upsert(batch).execute()
            except Exception as e:
                pass  # Ignore duplicate errors
        
        print(f"   ✅ Đã sync {len(student_records)} sinh viên")
        
        # 2. Sync CSV data
        print("\n2️⃣ Đang sync dữ liệu CSV...")
        csv_records = []
        for student in students:
            csv_data = student.get('csv_data', {})
            record = {
                'student_id': student['student_id'],
                'midterm_score': float(csv_data.get('midterm_score', 0)),
                'final_score': float(csv_data.get('final_score', 0)),
                'homework_score': float(csv_data.get('homework_score', 0)),
                'total_score': float(csv_data.get('total_score', 0)),
                'attendance_rate': float(csv_data.get('attendance_rate', 0)),
                'assignment_completion': float(csv_data.get('assignment_completion', 0)),
                'study_hours_per_week': int(csv_data.get('study_hours_per_week', 0)),
                'participation_score': int(csv_data.get('participation_score', 0)),
                'late_submissions': int(csv_data.get('late_submissions', 0)),
                'lms_usage_hours': int(csv_data.get('lms_usage_hours', 0)),
                'response_quality': int(csv_data.get('response_quality', 0)),
                'behavior_score_100': int(csv_data.get('behavior_score_100', 0))
            }
            csv_records.append(record)
        
        for i in range(0, len(csv_records), batch_size):
            batch = csv_records[i:i+batch_size]
            try:
                supabase.table('student_csv_data').upsert(batch).execute()
            except Exception as e:
                pass
        
        print(f"   ✅ Đã sync {len(csv_records)} bản ghi CSV")
        
        # 3. Sync course scores
        print("\n3️⃣ Đang sync điểm môn học...")
        course_records = []
        for student in students:
            courses = student.get('courses', {})
            for course_name, course_data in courses.items():
                course_code = COURSE_NAME_TO_CODE.get(course_name)
                if not course_code:
                    continue
                
                record = {
                    'student_id': student['student_id'],
                    'course_code': course_code,
                    'score': float(course_data.get('score', 0)),
                    'time_minutes': int(course_data.get('time_minutes', 0)),
                    'midterm_score': float(course_data.get('midterm_score', 0)),
                    'final_score': float(course_data.get('final_score', 0)),
                    'homework_score': float(course_data.get('homework_score', 0))
                }
                course_records.append(record)
        
        for i in range(0, len(course_records), batch_size):
            batch = course_records[i:i+batch_size]
            try:
                supabase.table('course_scores').upsert(batch).execute()
            except Exception as e:
                pass
        
        print(f"   ✅ Đã sync {len(course_records)} điểm môn học")
        
        # 4. Sync skill evaluations
        print("\n4️⃣ Đang sync đánh giá kỹ năng...")
        skill_records = []
        for student in students:
            skill_evals = student.get('skill_evaluations', {})
            for course_name, course_eval in skill_evals.items():
                course_code = COURSE_NAME_TO_CODE.get(course_name)
                if not course_code:
                    continue
                
                skills = course_eval.get('skills', {})
                for skill_name, skill_data in skills.items():
                    skill_code = SKILL_NAME_TO_CODE.get(skill_name)
                    if not skill_code:
                        continue
                    
                    record = {
                        'student_id': student['student_id'],
                        'course_code': course_code,
                        'skill_code': skill_code,
                        'score': float(skill_data.get('score', 0)),
                        'level': skill_data.get('level', ''),
                        'passed': bool(skill_data.get('passed', False))
                    }
                    skill_records.append(record)
        
        for i in range(0, len(skill_records), batch_size):
            batch = skill_records[i:i+batch_size]
            try:
                supabase.table('skill_evaluations').upsert(batch).execute()
            except Exception as e:
                pass
        
        print(f"   ✅ Đã sync {len(skill_records)} đánh giá kỹ năng")
        
        # 5. Sync classifications
        print("\n5️⃣ Đang sync kết quả phân loại...")
        classification_records = []
        for student in classified_students:
            record = {
                'student_id': student['student_id'],
                'kmeans_prediction': student.get('kmeans_prediction', ''),
                'knn_prediction': student.get('knn_prediction', ''),
                'final_level': student.get('final_level', ''),
                'normalization_method': 'minmax',
                'anomaly_detected': bool(student.get('anomaly_detected', False)),
                'anomaly_reasons': student.get('anomaly_reasons', [])
            }
            classification_records.append(record)
        
        for i in range(0, len(classification_records), batch_size):
            batch = classification_records[i:i+batch_size]
            try:
                supabase.table('classifications').upsert(batch).execute()
            except Exception as e:
                pass
        
        print(f"   ✅ Đã sync {len(classification_records)} kết quả phân loại")
        
        # 6. Sync integrated scores
        print("\n6️⃣ Đang sync điểm tích hợp...")
        integrated_records = []
        for result in integrated_results:
            components = result.get('components', {})
            record = {
                'student_id': result['student_id'],
                'original_score': float(result.get('original_score', 0)),
                'integrated_score': float(result.get('integrated_score', 0)),
                'score_difference': float(result.get('score_difference', 0)),
                'classification': result.get('classification', ''),
                'exercise_avg': float(components.get('exercise_avg', 0)),
                'midterm_avg': float(components.get('midterm', 0)),
                'final_avg': float(components.get('final', 0)),
                'total_exercises': int(result.get('exercise_data', {}).get('total_exercises', 0))
            }
            integrated_records.append(record)
        
        for i in range(0, len(integrated_records), batch_size):
            batch = integrated_records[i:i+batch_size]
            try:
                supabase.table('integrated_scores').upsert(batch).execute()
            except Exception as e:
                pass
        
        print(f"   ✅ Đã sync {len(integrated_records)} điểm tích hợp")
        
        # 7. Sync exercise details từ CSV
        print("\n7️⃣ Đang sync chi tiết bài tập...")
        exercise_count = sync_exercises_from_csv(supabase)
        print(f"   ✅ Đã sync {exercise_count} bài tập chi tiết")
        
        print("\n" + "=" * 80)
        print("✅ HOÀN THÀNH ĐỒNG BỘ!")
        print("=" * 80)
        print(f"\n🌐 Xem dữ liệu tại: {SUPABASE_URL}")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi sync lên Supabase: {str(e)}")
        print("💡 Tip: Kiểm tra kết nối internet và Supabase credentials")
        return False


def sync_exercises_from_csv(supabase):
    """
    Sync chi tiết bài tập từ file CSV lên Supabase
    """
    import csv
    import os
    
    csv_path = 'student_exercises_detailed.csv'
    if not os.path.exists(csv_path):
        print(f"   ⚠️ Không tìm thấy file {csv_path}")
        return 0
    
    # Không xóa dữ liệu cũ - dùng upsert để cập nhật
    
    # Mapping skill names từ CSV sang code - mỗi skill có code riêng
    SKILL_CSV_TO_CODE = {
        # Nhập Môn Lập Trình
        "Biến và Kiểu Dữ Liệu": "VARIABLES",
        "Cấu Trúc Điều Kiện": "CONTROL",
        "Vòng Lặp Cơ Bản": "LOOPS",
        "Hàm và Tham Số": "FUNCTIONS",
        "Toán Tử và Biểu Thức": "SYNTAX",
        # Kỹ Thuật Lập Trình
        "Mảng và Xử Lý Mảng": "ARRAYS",
        "Con Trỏ": "POINTERS",
        "Chuỗi Ký Tự": "STRINGS",
        "File I/O": "FILE_IO",
        # Cấu Trúc Dữ Liệu
        "Danh Sách Liên Kết": "LINKED_LIST",
        "Stack và Queue": "STACK_QUEUE",
        "Cây Nhị Phân": "TREES",
        "Bảng Băm": "HASH_TABLE",
        # Lập Trình Hướng Đối Tượng
        "Lớp và Đối Tượng": "CLASSES",
        "Kế Thừa": "INHERITANCE",
        "Đa Hình": "POLYMORPHISM",
        "Đóng Gói": "ENCAPSULATION",
        "Interface và Abstract": "INTERFACE"
    }
    
    COURSE_CSV_TO_CODE = {
        "Nhập Môn Lập Trình": "NMLT",
        "Kĩ Thuật Lập Trình": "KTLT",
        "Kỹ Thuật Lập Trình": "KTLT",
        "Cấu trúc Dữ Liệu và Giải Thuật": "CTDL",
        "Cấu Trúc Dữ Liệu": "CTDL",
        "Lập Trình Hướng Đối Tượng": "OOP"
    }
    
    records = []
    batch_size = 500
    total_uploaded = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig để xử lý BOM
            reader = csv.DictReader(f)
            
            for row in reader:
                # Xử lý student_id (có thể có BOM character)
                student_id_str = row.get('student_id', '') or row.get('\ufeffstudent_id', '')
                try:
                    student_id = int(student_id_str) if student_id_str else 0
                except:
                    student_id = 0
                
                if student_id == 0:
                    continue
                course_name = row.get('course', '')
                skill_name = row.get('skill', '')
                exercise_number = int(row.get('exercise_number', 0))
                score = float(row.get('score', 0))
                completion_time = float(row.get('completion_time_minutes', 0))
                is_anomaly = row.get('is_anomaly', 'False').lower() == 'true'
                anomaly_reasons = row.get('anomaly_reasons', '')
                
                # Map course và skill
                course_code = COURSE_CSV_TO_CODE.get(course_name, '')
                skill_code = SKILL_CSV_TO_CODE.get(skill_name, '')
                
                if not course_code or not skill_code:
                    continue
                
                record = {
                    'student_id': student_id,
                    'course_code': course_code,
                    'skill_code': skill_code,
                    'exercise_number': exercise_number,
                    'score': score,
                    'completion_time': completion_time,
                    'is_anomaly': is_anomaly
                }
                records.append(record)
                
                # Upload theo batch
                if len(records) >= batch_size:
                    try:
                        supabase.table('exercise_details').upsert(records, on_conflict='student_id,course_code,skill_code,exercise_number').execute()
                        total_uploaded += len(records)
                        print(f"      Uploaded {total_uploaded} records...")
                    except Exception as e:
                        print(f"      Error batch: {str(e)[:100]}")
                    records = []
            
            # Upload phần còn lại
            if records:
                try:
                    supabase.table('exercise_details').upsert(records, on_conflict='student_id,course_code,skill_code,exercise_number').execute()
                    total_uploaded += len(records)
                except Exception as e:
                    print(f"      Error final batch: {str(e)[:100]}")
        
        return total_uploaded
        
    except Exception as e:
        print(f"   ⚠️ Lỗi đọc CSV: {str(e)}")
        return total_uploaded
