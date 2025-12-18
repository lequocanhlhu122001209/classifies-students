"""
Phân loại sinh viên mới (không có trong CSV) dựa trên điểm course_scores
"""
from supabase import create_client
import numpy as np

SUPABASE_URL = 'https://odmtndvllclmrwczcyvs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def classify_by_score(avg_score):
    """Phân loại dựa trên điểm trung bình"""
    if avg_score >= 8.5:
        return 'Xuất sắc'
    elif avg_score >= 7.0:
        return 'Khá'
    elif avg_score >= 5.0:
        return 'Trung bình'
    else:
        return 'Yếu'

def main():
    print("=" * 50)
    print("PHÂN LOẠI SINH VIÊN MỚI")
    print("=" * 50)
    
    # Lấy sinh viên đã có classification
    existing = supabase.table('classifications').select('student_id').execute().data
    existing_ids = set(c['student_id'] for c in existing)
    print(f"Sinh viên đã phân loại: {len(existing_ids)}")
    
    # Lấy tất cả sinh viên
    all_students = supabase.table('students').select('student_id').execute().data
    all_ids = set(s['student_id'] for s in all_students)
    print(f"Tổng sinh viên: {len(all_ids)}")
    
    # Sinh viên chưa phân loại
    new_ids = all_ids - existing_ids
    print(f"Sinh viên chưa phân loại: {len(new_ids)}")
    
    if not new_ids:
        print("✅ Tất cả sinh viên đã được phân loại!")
        return
    
    # Lấy điểm của sinh viên mới
    scores = supabase.table('course_scores').select('student_id, score').execute().data
    student_scores = {}
    for s in scores:
        sid = s['student_id']
        if sid in new_ids:
            if sid not in student_scores:
                student_scores[sid] = []
            if s['score']:
                student_scores[sid].append(s['score'])
    
    # Phân loại
    new_classifications = []
    level_counts = {'Xuất sắc': 0, 'Khá': 0, 'Trung bình': 0, 'Yếu': 0}
    
    for sid in new_ids:
        scores_list = student_scores.get(sid, [])
        avg_score = np.mean(scores_list) if scores_list else 5.0
        level = classify_by_score(avg_score)
        level_counts[level] += 1
        
        new_classifications.append({
            'student_id': sid,
            'kmeans_prediction': level,
            'knn_prediction': level,
            'final_level': level,
            'normalization_method': 'minmax',
            'anomaly_detected': False
        })
    
    # Insert
    if new_classifications:
        supabase.table('classifications').insert(new_classifications).execute()
        print(f"✅ Đã phân loại {len(new_classifications)} sinh viên mới")
    
    print("\nThống kê sinh viên mới:")
    for level, count in level_counts.items():
        print(f"  {level}: {count}")
    
    # Verify tổng
    total = supabase.table('classifications').select('student_id', count='exact').execute()
    print(f"\nTổng classifications: {total.count}")

if __name__ == '__main__':
    main()
