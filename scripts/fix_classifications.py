"""
Script phân loại lại sinh viên sử dụng đúng pipeline:
1. Load dữ liệu từ Supabase
2. Extract features (12 features)
3. Normalize (MinMax/ZScore/Robust)
4. KMeans clustering
5. KNN learning từ KMeans
6. Lưu kết quả vào Supabase
"""
from supabase import create_client
from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
import numpy as np

SUPABASE_URL = 'https://odmtndvllclmrwczcyvs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    print("=" * 60)
    print("PHÂN LOẠI SINH VIÊN VỚI KMEANS + KNN")
    print("=" * 60)
    
    # 1. Load dữ liệu từ CSV (có đầy đủ features)
    print("\n📥 Bước 1: Load dữ liệu từ CSV (đầy đủ features)...")
    generator = StudentDataGenerator(
        seed=42, 
        csv_path='student_classification_supabase_ready_final.csv',
        use_supabase=False  # Dùng CSV để có đầy đủ features
    )
    students = generator.load_all_students()
    print(f"   Đã load {len(students)} sinh viên từ CSV")
    
    # 2. Khởi tạo classifier với MinMax normalization
    print("\n🔧 Bước 2: Khởi tạo classifier (MinMax normalization)...")
    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    
    # 3. Extract features và normalize
    print("\n📊 Bước 3: Extract features (12 features)...")
    features = classifier.extract_features(students)
    print(f"   Feature shape: {features.shape}")
    print(f"   Features: [total_score, midterm, final, homework, attendance,")
    print(f"              assignment, study_hours, behavior, participation,")
    print(f"              diligence, skill_score, anomaly_score]")
    
    # 4. Fit model (KMeans + KNN)
    print("\n🤖 Bước 4: Training KMeans + KNN...")
    classifier.fit(students)
    
    # 5. Predict
    print("\n🎯 Bước 5: Dự đoán phân loại...")
    classified_students = classifier.predict(students)
    
    # 6. Thống kê kết quả
    level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    anomaly_count = 0
    
    for student in classified_students:
        level = student.get("final_level", "Unknown")
        if level in level_counts:
            level_counts[level] += 1
        if student.get("anomaly_detected", False):
            anomaly_count += 1
    
    print("\n📈 Thống kê phân loại:")
    for level, count in level_counts.items():
        pct = (count / len(classified_students)) * 100
        print(f"   {level:15s}: {count:3d} ({pct:.1f}%)")
    print(f"   Bất thường     : {anomaly_count:3d}")
    
    # 7. Xóa classifications cũ
    print("\n🗑️  Bước 6: Xóa classifications cũ...")
    student_ids = [s['student_id'] for s in students]
    for sid in student_ids:
        supabase.table('classifications').delete().eq('student_id', sid).execute()
    print("   ✅ Đã xóa")
    
    # 8. Lưu classifications mới
    print("\n💾 Bước 7: Lưu classifications mới vào Supabase...")
    
    # Map level về tiếng Việt
    level_map = {
        "Xuat sac": "Xuất sắc",
        "Kha": "Khá",
        "Trung binh": "Trung bình",
        "Yeu": "Yếu"
    }
    
    new_classifications = []
    for student in classified_students:
        final_level = student.get("final_level", "Trung binh")
        final_level_vn = level_map.get(final_level, final_level)
        
        kmeans_pred = student.get("kmeans_prediction", final_level)
        kmeans_pred_vn = level_map.get(kmeans_pred, kmeans_pred)
        
        knn_pred = student.get("knn_prediction", final_level)
        knn_pred_vn = level_map.get(knn_pred, knn_pred)
        
        new_classifications.append({
            'student_id': student['student_id'],
            'kmeans_prediction': kmeans_pred_vn,
            'knn_prediction': knn_pred_vn,
            'final_level': final_level_vn,
            'normalization_method': 'minmax',
            'anomaly_detected': student.get('anomaly_detected', False)
        })
    
    # Insert theo batch
    for i in range(0, len(new_classifications), 100):
        batch = new_classifications[i:i+100]
        supabase.table('classifications').insert(batch).execute()
        print(f"   Inserted {min(i+100, len(new_classifications))}/{len(new_classifications)}")
    
    print("\n" + "=" * 60)
    print("✅ HOÀN THÀNH!")
    print("=" * 60)
    
    # Verify
    result = supabase.table('classifications').select('final_level').execute()
    from collections import Counter
    counts = Counter([x['final_level'] for x in result.data])
    print("\n📊 Verify từ Supabase:")
    for level, count in counts.items():
        print(f"   {level}: {count}")

if __name__ == '__main__':
    main()
