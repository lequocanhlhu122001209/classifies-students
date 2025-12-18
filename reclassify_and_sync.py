"""
Script chạy lại phân loại K-means + KNN và sync lên Supabase
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from integrated_scoring_system import IntegratedScoringSystem
from supabase_sync import sync_to_supabase

def main():
    print("=" * 80)
    print("🔄 CHẠY LẠI PHÂN LOẠI K-MEANS + KNN VÀ SYNC LÊN SUPABASE")
    print("=" * 80)
    
    # 1. Load dữ liệu từ Supabase
    print("\n📊 Bước 1: Đang tải dữ liệu từ Supabase...")
    generator = StudentDataGenerator(
        seed=42, 
        csv_path=None,
        use_supabase=True  # Load từ Supabase
    )
    students = generator.load_all_students()
    print(f"   ✅ Đã tải {len(students)} sinh viên")
    
    # 2. Đánh giá kỹ năng
    print("\n📝 Bước 2: Đang đánh giá kỹ năng...")
    skill_evaluator = SkillEvaluator()
    for student in students:
        skill_evaluations = skill_evaluator.evaluate_all_courses(student)
        student["skill_evaluations"] = skill_evaluations
    print(f"   ✅ Đã đánh giá kỹ năng cho {len(students)} sinh viên")
    
    # 3. Phân loại với K-means + KNN
    print("\n🤖 Bước 3: Đang phân loại với K-means + KNN...")
    print("   Phương pháp chuẩn hóa: MINMAX")
    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    classifier.fit(students)
    classified_students = classifier.predict(students)
    print(f"   ✅ Đã phân loại {len(classified_students)} sinh viên")
    
    # 4. Tính điểm tích hợp
    print("\n📈 Bước 4: Đang tính điểm tích hợp...")
    integrated_system = IntegratedScoringSystem()
    integrated_results = integrated_system.analyze_all_students()
    print(f"   ✅ Đã tính điểm tích hợp cho {len(integrated_results)} sinh viên")
    
    # 5. Thống kê kết quả
    print("\n" + "=" * 80)
    print("📊 THỐNG KÊ KẾT QUẢ PHÂN LOẠI")
    print("=" * 80)
    
    level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    anomaly_count = 0
    anomaly_students = []
    
    for student in classified_students:
        level = student.get("final_level", "Unknown")
        if level in level_counts:
            level_counts[level] += 1
        if student.get("anomaly_detected", False):
            anomaly_count += 1
            anomaly_students.append({
                'id': student['student_id'],
                'name': student['name'],
                'score': student.get('csv_data', {}).get('total_score', 0),
                'reason': student.get('anomaly_reason', ''),
                'kmeans': student.get('kmeans_prediction', ''),
                'final': student.get('final_level', '')
            })
    
    print("\n📈 Phân loại cuối cùng (sau điều chỉnh bất thường):")
    for level, count in level_counts.items():
        pct = (count / len(classified_students)) * 100
        print(f"   • {level:15s}: {count:3d} sinh viên ({pct:5.1f}%)")
    
    print(f"\n⚠️  Số trường hợp bất thường: {anomaly_count}")
    
    if anomaly_students:
        print("\n📋 Danh sách sinh viên bất thường (top 10):")
        for i, s in enumerate(anomaly_students[:10], 1):
            print(f"   {i}. ID {s['id']} - {s['name']}")
            print(f"      Điểm: {s['score']:.1f} | K-means: {s['kmeans']} → Kết luận: {s['final']}")
            print(f"      Lý do: {s['reason']}")
    
    # 6. Sync lên Supabase
    print("\n" + "=" * 80)
    print("☁️  Bước 5: Đang sync lên Supabase...")
    success = sync_to_supabase(students, classified_students, integrated_results)
    
    if success:
        print("\n✅ HOÀN THÀNH! Dữ liệu đã được cập nhật trên Supabase.")
    else:
        print("\n❌ Có lỗi khi sync lên Supabase.")
    
    return success

if __name__ == "__main__":
    main()
