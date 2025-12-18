"""
Sync sinh viên mới từ CSV lên Supabase
"""

import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://odmtndvllclmrwczcyvs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Đọc CSV
df = pd.read_csv('student_classification_supabase_ready_final.csv', encoding='utf-8')
print(f"Tổng số sinh viên trong CSV: {len(df)}")

# Lấy danh sách student_id đã có trên Supabase
existing = supabase.table('students').select('student_id').execute()
existing_ids = set(s['student_id'] for s in existing.data)
print(f"Số sinh viên đã có trên Supabase: {len(existing_ids)}")

# Lọc sinh viên mới
new_students = df[~df['student_id'].isin(existing_ids)]
print(f"Số sinh viên mới cần sync: {len(new_students)}")

if len(new_students) == 0:
    print("Không có sinh viên mới!")
    exit()

# 1. Sync bảng students
print("\n1️⃣ Sync bảng students...")
student_records = []
for _, row in new_students.iterrows():
    student_records.append({
        'student_id': int(row['student_id']),
        'name': row['name'],
        'class': row['class'],
        'khoa': row.get('Khoa', 'CT'),
        'sex': row.get('sex', '')
    })

supabase.table('students').insert(student_records).execute()
print(f"   ✅ Đã thêm {len(student_records)} sinh viên")

# 2. Sync bảng student_csv_data
print("\n2️⃣ Sync bảng student_csv_data...")
csv_records = []
for _, row in new_students.iterrows():
    csv_records.append({
        'student_id': int(row['student_id']),
        'midterm_score': float(row.get('midterm_score', 0)),
        'final_score': float(row.get('final_score', 0)),
        'homework_score': float(row.get('homework_score', 0)),
        'total_score': float(row.get('total_score', 0)),
        'attendance_rate': float(row.get('attendance_rate', 0)),
        'assignment_completion': float(row.get('assignment_completion', 0)),
        'study_hours_per_week': int(row.get('study_hours_per_week', 0)),
        'participation_score': int(row.get('participation_score', 0)),
        'late_submissions': int(row.get('late_submissions', 0)),
        'lms_usage_hours': int(row.get('lms_usage_hours', 0)),
        'response_quality': int(row.get('response_quality', 0)),
        'behavior_score_100': int(row.get('behCTior_score_100', 0))
    })

supabase.table('student_csv_data').insert(csv_records).execute()
print(f"   ✅ Đã thêm {len(csv_records)} bản ghi CSV")

# 3. Sync bảng course_scores
print("\n3️⃣ Sync bảng course_scores...")
COURSES = ["NMLT", "KTLT", "CTDL", "OOP"]
course_records = []
for _, row in new_students.iterrows():
    midterm = float(row.get('midterm_score', 0))
    final = float(row.get('final_score', 0))
    homework = float(row.get('homework_score', 0))
    score = float(row.get('total_score', 0))
    study_hours = float(row.get('study_hours_per_week', 20))
    lms_hours = float(row.get('lms_usage_hours', 10))
    time_minutes = (study_hours + lms_hours) * 60 / 4  # Chia cho 4 môn
    
    for course_code in COURSES:
        course_records.append({
            'student_id': int(row['student_id']),
            'course_code': course_code,
            'score': score,
            'time_minutes': int(time_minutes),
            'midterm_score': midterm,
            'final_score': final,
            'homework_score': homework
        })

# Insert theo batch
batch_size = 100
for i in range(0, len(course_records), batch_size):
    batch = course_records[i:i+batch_size]
    supabase.table('course_scores').insert(batch).execute()
print(f"   ✅ Đã thêm {len(course_records)} điểm môn học")

# 4. Sync bảng classifications (phân loại ban đầu)
print("\n4️⃣ Sync bảng classifications...")
class_records = []
for _, row in new_students.iterrows():
    level = row.get('predicted_level', 'Trung bình')
    # Chuẩn hóa level
    level_map = {
        'Xuất sắc': 'Xuat sac',
        'Khá': 'Kha', 
        'Trung bình': 'Trung binh',
        'Yếu': 'Yeu'
    }
    final_level = level_map.get(level, level)
    
    class_records.append({
        'student_id': int(row['student_id']),
        'kmeans_prediction': final_level,
        'knn_prediction': final_level,
        'final_level': final_level,
        'normalization_method': 'minmax',
        'anomaly_detected': False,
        'anomaly_reasons': []
    })

supabase.table('classifications').insert(class_records).execute()
print(f"   ✅ Đã thêm {len(class_records)} kết quả phân loại")

print("\n" + "=" * 50)
print("✅ HOÀN THÀNH SYNC!")
print("=" * 50)

# Kiểm tra lại
total = supabase.table('students').select('student_id', count='exact').execute()
print(f"\n📊 Tổng số sinh viên trên Supabase: {total.count}")
