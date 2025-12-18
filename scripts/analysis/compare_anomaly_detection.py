"""
Script so sánh kết quả phát hiện bất thường trước và sau khi điều chỉnh logic
- Chạy phân loại với logic mới
- So sánh với kết quả cũ trong classification_history.json
- Đánh giá độ chính xác và ổn định
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
from datetime import datetime
from supabase import create_client
from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator

SUPABASE_URL = "https://odmtndvllclmrwczcyvs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA"

HISTORY_FILE = 'classification_history.json'
COMPARISON_FILE = 'anomaly_comparison_result.json'

def load_history():
    """Load lịch sử phân loại"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'versions': [], 'current_version': 0}

def get_current_classifications(supabase):
    """Lấy kết quả phân loại hiện tại từ Supabase"""
    result = supabase.table('classifications').select('*').execute()
    return {c['student_id']: c for c in result.data}

def run_new_classification():
    """Chạy phân loại với logic mới"""
    print("\n🔄 Đang chạy phân loại với logic mới...")
    
    generator = StudentDataGenerator(
        seed=42, 
        csv_path='student_classification_supabase_ready_final.csv',
        use_supabase=False
    )
    students = generator.load_all_students()
    
    skill_evaluator = SkillEvaluator()
    for student in students:
        skill_evaluations = skill_evaluator.evaluate_all_courses(student)
        student["skill_evaluations"] = skill_evaluations
    
    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    classifier.fit(students)
    classified_students = classifier.predict(students)
    
    return {s['student_id']: s for s in classified_students}

def compare_results(old_data, new_data, students_info):
    """So sánh kết quả cũ và mới"""
    comparison = {
        'timestamp': datetime.now().isoformat(),
        'total_students': len(new_data),
        'level_changes': [],
        'anomaly_changes': [],
        'stats': {
            'old': {'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0, 'anomaly': 0},
            'new': {'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0, 'anomaly': 0}
        },
        'improvements': [],
        'regressions': []
    }
    
    level_order = ['Yeu', 'Trung binh', 'Kha', 'Xuat sac']
    
    for student_id, new_class in new_data.items():
        new_level = new_class.get('final_level', '')
        new_anomaly = new_class.get('anomaly_detected', False)
        
        # Thống kê mới
        if new_level in comparison['stats']['new']:
            comparison['stats']['new'][new_level] += 1
        if new_anomaly:
            comparison['stats']['new']['anomaly'] += 1
        
        if student_id in old_data:
            old_class = old_data[student_id]
            old_level = old_class.get('final_level', '')
            old_anomaly = old_class.get('anomaly_detected', False)
            
            # Thống kê cũ
            if old_level in comparison['stats']['old']:
                comparison['stats']['old'][old_level] += 1
            if old_anomaly:
                comparison['stats']['old']['anomaly'] += 1
            
            # Lấy thông tin sinh viên
            student_info = students_info.get(student_id, {})
            csv_data = student_info.get('csv_data', {})
            courses = student_info.get('courses', {})
            
            total_score = float(csv_data.get('total_score', 0))
            avg_time = sum(float(c.get('time_minutes', 0)) for c in courses.values() if isinstance(c, dict)) / len(courses) if courses else 0
            attendance = float(csv_data.get('attendance_rate', 0)) * 100
            late_submissions = int(csv_data.get('late_submissions', 0))
            
            # So sánh level
            if old_level != new_level:
                old_idx = level_order.index(old_level) if old_level in level_order else -1
                new_idx = level_order.index(new_level) if new_level in level_order else -1
                
                change = {
                    'student_id': student_id,
                    'old_level': old_level,
                    'new_level': new_level,
                    'direction': 'up' if new_idx > old_idx else 'down',
                    'total_score': total_score,
                    'avg_time_hours': round(avg_time / 60, 1),
                    'attendance': round(attendance, 1),
                    'late_submissions': late_submissions,
                    'old_anomaly': old_anomaly,
                    'new_anomaly': new_anomaly
                }
                comparison['level_changes'].append(change)
                
                # Phân loại cải thiện/thoái lui
                if new_idx > old_idx:
                    comparison['improvements'].append(change)
                else:
                    comparison['regressions'].append(change)
            
            # So sánh anomaly
            if old_anomaly != new_anomaly:
                comparison['anomaly_changes'].append({
                    'student_id': student_id,
                    'old_anomaly': old_anomaly,
                    'new_anomaly': new_anomaly,
                    'level': new_level,
                    'total_score': total_score,
                    'avg_time_hours': round(avg_time / 60, 1),
                    'attendance': round(attendance, 1),
                    'late_submissions': late_submissions
                })
    
    return comparison

def print_comparison_report(comparison):
    """In báo cáo so sánh"""
    print("\n" + "=" * 80)
    print("📊 BÁO CÁO SO SÁNH KẾT QUẢ PHÁT HIỆN BẤT THƯỜNG")
    print("=" * 80)
    
    # Thống kê tổng quan
    print("\n📈 THỐNG KÊ TỔNG QUAN:")
    print(f"   Tổng sinh viên: {comparison['total_students']}")
    
    print("\n   Phân loại CŨ vs MỚI:")
    for level in ['Xuat sac', 'Kha', 'Trung binh', 'Yeu']:
        old_count = comparison['stats']['old'].get(level, 0)
        new_count = comparison['stats']['new'].get(level, 0)
        diff = new_count - old_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"   • {level:12}: {old_count:3} → {new_count:3} ({diff_str})")
    
    old_anomaly = comparison['stats']['old'].get('anomaly', 0)
    new_anomaly = comparison['stats']['new'].get('anomaly', 0)
    diff = new_anomaly - old_anomaly
    diff_str = f"+{diff}" if diff > 0 else str(diff)
    print(f"   • {'Bất thường':12}: {old_anomaly:3} → {new_anomaly:3} ({diff_str})")
    
    # Thay đổi xếp loại
    print(f"\n🔄 THAY ĐỔI XẾP LOẠI: {len(comparison['level_changes'])} sinh viên")
    
    if comparison['improvements']:
        print(f"\n   ✅ Cải thiện ({len(comparison['improvements'])} SV):")
        for i, c in enumerate(comparison['improvements'][:10], 1):
            print(f"      {i}. ID {c['student_id']}: {c['old_level']} → {c['new_level']}")
            print(f"         Điểm: {c['total_score']}/10, Thời gian: {c['avg_time_hours']}h, Tham gia: {c['attendance']}%")
    
    if comparison['regressions']:
        print(f"\n   ⚠️ Thoái lui ({len(comparison['regressions'])} SV):")
        for i, c in enumerate(comparison['regressions'][:10], 1):
            print(f"      {i}. ID {c['student_id']}: {c['old_level']} → {c['new_level']}")
            print(f"         Điểm: {c['total_score']}/10, Thời gian: {c['avg_time_hours']}h, Tham gia: {c['attendance']}%")
    
    # Thay đổi phát hiện bất thường
    print(f"\n🔍 THAY ĐỔI PHÁT HIỆN BẤT THƯỜNG: {len(comparison['anomaly_changes'])} sinh viên")
    
    removed_anomaly = [c for c in comparison['anomaly_changes'] if c['old_anomaly'] and not c['new_anomaly']]
    added_anomaly = [c for c in comparison['anomaly_changes'] if not c['old_anomaly'] and c['new_anomaly']]
    
    if removed_anomaly:
        print(f"\n   ✅ Bỏ cảnh báo bất thường ({len(removed_anomaly)} SV):")
        for i, c in enumerate(removed_anomaly[:10], 1):
            print(f"      {i}. ID {c['student_id']} ({c['level']})")
            print(f"         Điểm: {c['total_score']}/10, Thời gian: {c['avg_time_hours']}h")
    
    if added_anomaly:
        print(f"\n   ⚠️ Thêm cảnh báo bất thường ({len(added_anomaly)} SV):")
        for i, c in enumerate(added_anomaly[:10], 1):
            print(f"      {i}. ID {c['student_id']} ({c['level']})")
            print(f"         Điểm: {c['total_score']}/10, Thời gian: {c['avg_time_hours']}h")
    
    # Đánh giá độ ổn định
    print("\n" + "=" * 80)
    print("📋 ĐÁNH GIÁ ĐỘ ỔN ĐỊNH:")
    
    total = comparison['total_students']
    unchanged = total - len(comparison['level_changes'])
    stability = (unchanged / total * 100) if total > 0 else 0
    
    print(f"   • Tỷ lệ giữ nguyên xếp loại: {unchanged}/{total} ({stability:.1f}%)")
    print(f"   • Số cải thiện: {len(comparison['improvements'])}")
    print(f"   • Số thoái lui: {len(comparison['regressions'])}")
    print(f"   • Giảm cảnh báo bất thường: {len(removed_anomaly)}")
    print(f"   • Tăng cảnh báo bất thường: {len(added_anomaly)}")
    
    if stability >= 90:
        print("\n   ✅ Kết quả: RẤT ỔN ĐỊNH (>90% không đổi)")
    elif stability >= 80:
        print("\n   ✅ Kết quả: ỔN ĐỊNH (>80% không đổi)")
    elif stability >= 70:
        print("\n   ⚠️ Kết quả: TƯƠNG ĐỐI ỔN ĐỊNH (>70% không đổi)")
    else:
        print("\n   ❌ Kết quả: KHÔNG ỔN ĐỊNH (<70% không đổi)")
    
    print("=" * 80)

def main():
    print("=" * 80)
    print("🔬 SO SÁNH KẾT QUẢ PHÁT HIỆN BẤT THƯỜNG (TRƯỚC vs SAU ĐIỀU CHỈNH)")
    print("=" * 80)
    
    # Kết nối Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Load dữ liệu sinh viên
    print("\n📊 Đang tải dữ liệu sinh viên...")
    generator = StudentDataGenerator(
        seed=42, 
        csv_path='student_classification_supabase_ready_final.csv',
        use_supabase=False
    )
    students = generator.load_all_students()
    students_info = {s['student_id']: s for s in students}
    print(f"   ✅ Đã tải {len(students)} sinh viên")
    
    # Lấy kết quả cũ từ Supabase
    print("\n📦 Đang lấy kết quả phân loại cũ từ Supabase...")
    old_data = get_current_classifications(supabase)
    print(f"   ✅ Đã lấy {len(old_data)} bản ghi cũ")
    
    # Chạy phân loại mới
    new_data = run_new_classification()
    print(f"   ✅ Đã phân loại {len(new_data)} sinh viên với logic mới")
    
    # So sánh
    comparison = compare_results(old_data, new_data, students_info)
    
    # In báo cáo
    print_comparison_report(comparison)
    
    # Lưu kết quả
    with open(COMPARISON_FILE, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    print(f"\n📁 Đã lưu kết quả so sánh vào: {COMPARISON_FILE}")
    
    # Hỏi có muốn cập nhật không
    print("\n" + "-" * 80)
    response = input("❓ Bạn có muốn cập nhật kết quả mới lên Supabase? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n📤 Đang cập nhật kết quả mới...")
        
        classification_records = []
        for student_id, student in new_data.items():
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
        
        batch_size = 100
        for i in range(0, len(classification_records), batch_size):
            batch = classification_records[i:i+batch_size]
            supabase.table('classifications').upsert(batch).execute()
        
        print(f"   ✅ Đã cập nhật {len(classification_records)} bản ghi")
    else:
        print("   ⏭️ Bỏ qua cập nhật")
    
    print("\n✅ HOÀN THÀNH!")

if __name__ == "__main__":
    main()
