"""
Script phân loại K-means + KNN với lưu lịch sử
- Lưu kết quả phân loại cũ vào bảng classification_history
- Đè kết quả mới lên bảng classifications
- Cho phép so sánh kết quả giữa các lần phân loại
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from supabase import create_client
from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from integrated_scoring_system import IntegratedScoringSystem

SUPABASE_URL = "https://odmtndvllclmrwczcyvs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA"

import json
import os

HISTORY_FILE = 'classification_history.json'

def load_local_history():
    """Load lịch sử từ file JSON local"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'versions': [], 'current_version': 0}

def save_local_history(history):
    """Lưu lịch sử vào file JSON local"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def create_history_table_if_not_exists(supabase):
    """Kiểm tra bảng classification_history trên Supabase"""
    print("📋 Kiểm tra bảng classification_history...")
    try:
        result = supabase.table('classification_history').select('id').limit(1).execute()
        print("   ✅ Bảng classification_history đã tồn tại trên Supabase")
        return True
    except Exception as e:
        print(f"   ⚠️ Bảng classification_history chưa tồn tại trên Supabase")
        print("   📝 Sẽ lưu lịch sử vào file local: classification_history.json")
        return False

def backup_current_classifications(supabase, use_supabase_history=False):
    """Sao lưu kết quả phân loại hiện tại"""
    print("\n📦 Đang sao lưu kết quả phân loại hiện tại...")
    
    # Lấy tất cả classifications hiện tại từ Supabase
    result = supabase.table('classifications').select('*').execute()
    current_classifications = result.data
    
    if not current_classifications:
        print("   ⚠️ Không có dữ liệu phân loại cũ để sao lưu")
        return 0
    
    # Load lịch sử local
    history = load_local_history()
    new_version = history['current_version'] + 1
    timestamp = datetime.now().isoformat()
    
    # Chuẩn bị dữ liệu history
    version_data = {
        'version': new_version,
        'timestamp': timestamp,
        'total_students': len(current_classifications),
        'classifications': []
    }
    
    # Thống kê
    stats = {'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0, 'anomaly': 0}
    
    for c in current_classifications:
        version_data['classifications'].append({
            'student_id': c['student_id'],
            'kmeans_prediction': c.get('kmeans_prediction', ''),
            'knn_prediction': c.get('knn_prediction', ''),
            'final_level': c.get('final_level', ''),
            'anomaly_detected': c.get('anomaly_detected', False),
            'anomaly_reasons': c.get('anomaly_reasons', [])
        })
        
        level = c.get('final_level', '')
        if level in stats:
            stats[level] += 1
        if c.get('anomaly_detected'):
            stats['anomaly'] += 1
    
    version_data['stats'] = stats
    
    # Lưu vào history
    history['versions'].append(version_data)
    history['current_version'] = new_version
    save_local_history(history)
    
    print(f"   ✅ Đã sao lưu {len(current_classifications)} bản ghi (version {new_version})")
    print(f"   📁 File: {HISTORY_FILE}")
    
    # Nếu có bảng Supabase, cũng lưu lên đó
    if use_supabase_history:
        history_records = []
        for c in current_classifications:
            history_records.append({
                'student_id': c['student_id'],
                'classification_date': timestamp,
                'kmeans_prediction': c.get('kmeans_prediction', ''),
                'knn_prediction': c.get('knn_prediction', ''),
                'final_level': c.get('final_level', ''),
                'anomaly_detected': c.get('anomaly_detected', False),
                'anomaly_reasons': c.get('anomaly_reasons', []),
                'version': new_version
            })
        
        batch_size = 100
        for i in range(0, len(history_records), batch_size):
            batch = history_records[i:i+batch_size]
            try:
                supabase.table('classification_history').insert(batch).execute()
            except Exception as e:
                pass
        print(f"   ☁️ Đã sync lên Supabase")
    
    return new_version

def sync_new_classifications(supabase, classified_students, version):
    """Đè kết quả phân loại mới lên bảng classifications"""
    print("\n📤 Đang cập nhật kết quả phân loại mới...")
    
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
    
    # Upsert (update nếu tồn tại, insert nếu chưa có)
    batch_size = 100
    for i in range(0, len(classification_records), batch_size):
        batch = classification_records[i:i+batch_size]
        try:
            supabase.table('classifications').upsert(batch).execute()
        except Exception as e:
            print(f"   ⚠️ Lỗi khi sync batch {i}: {str(e)[:100]}")
    
    print(f"   ✅ Đã cập nhật {len(classification_records)} kết quả phân loại")

def compare_versions(supabase, old_version, new_classifications):
    """So sánh kết quả giữa 2 phiên bản phân loại"""
    print(f"\n📊 So sánh kết quả phân loại (version {old_version} → mới)...")
    
    # Load lịch sử local
    history = load_local_history()
    
    # Tìm version cũ
    old_data = {}
    for v in history['versions']:
        if v['version'] == old_version:
            old_data = {c['student_id']: c for c in v['classifications']}
            break
    
    if not old_data:
        print(f"   ⚠️ Không tìm thấy version {old_version}")
        return []
    
    # Dữ liệu mới
    new_data = {s['student_id']: s for s in new_classifications}
    
    # So sánh
    changes = []
    for student_id, new_class in new_data.items():
        if student_id in old_data:
            old_class = old_data[student_id]
            if old_class['final_level'] != new_class.get('final_level', ''):
                changes.append({
                    'student_id': student_id,
                    'old_level': old_class['final_level'],
                    'new_level': new_class.get('final_level', ''),
                    'old_anomaly': old_class.get('anomaly_detected', False),
                    'new_anomaly': new_class.get('anomaly_detected', False)
                })
    
    print(f"   • Tổng sinh viên: {len(new_data)}")
    print(f"   • Số thay đổi xếp loại: {len(changes)}")
    
    if changes:
        print(f"\n   📋 Chi tiết thay đổi (top 20):")
        for i, c in enumerate(changes[:20], 1):
            arrow = "↑" if ['Yeu', 'Trung binh', 'Kha', 'Xuat sac'].index(c['new_level']) > ['Yeu', 'Trung binh', 'Kha', 'Xuat sac'].index(c['old_level']) else "↓"
            print(f"      {i}. ID {c['student_id']}: {c['old_level']} {arrow} {c['new_level']}")
    else:
        print("   ✅ Không có thay đổi xếp loại")
    
    return changes

def main():
    print("=" * 80)
    print("🔄 PHÂN LOẠI K-MEANS + KNN VỚI LƯU LỊCH SỬ")
    print("=" * 80)
    
    # Kết nối Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Kiểm tra/tạo bảng history
    has_history_table = create_history_table_if_not_exists(supabase)
    
    # Backup dữ liệu cũ (luôn lưu vào file local, và lên Supabase nếu có bảng)
    old_version = backup_current_classifications(supabase, use_supabase_history=has_history_table)
    
    # Load dữ liệu từ CSV
    print("\n📊 Bước 1: Đang tải dữ liệu từ CSV...")
    generator = StudentDataGenerator(
        seed=42, 
        csv_path='student_classification_supabase_ready_final.csv',
        use_supabase=False
    )
    students = generator.load_all_students()
    print(f"   ✅ Đã tải {len(students)} sinh viên")
    
    # Đánh giá kỹ năng
    print("\n📝 Bước 2: Đang đánh giá kỹ năng...")
    skill_evaluator = SkillEvaluator()
    for student in students:
        skill_evaluations = skill_evaluator.evaluate_all_courses(student)
        student["skill_evaluations"] = skill_evaluations
    print(f"   ✅ Đã đánh giá kỹ năng cho {len(students)} sinh viên")
    
    # Phân loại với K-means + KNN
    print("\n🤖 Bước 3: Đang phân loại với K-means + KNN...")
    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    classifier.fit(students)
    classified_students = classifier.predict(students)
    print(f"   ✅ Đã phân loại {len(classified_students)} sinh viên")
    
    # Thống kê
    level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    anomaly_count = 0
    for student in classified_students:
        level = student.get("final_level", "")
        if level in level_counts:
            level_counts[level] += 1
        if student.get("anomaly_detected"):
            anomaly_count += 1
    
    print("\n📊 Kết quả phân loại mới:")
    for level, count in level_counts.items():
        pct = count / len(classified_students) * 100
        print(f"   • {level}: {count} ({pct:.1f}%)")
    print(f"   • Bất thường: {anomaly_count}")
    
    # Sync lên Supabase
    sync_new_classifications(supabase, classified_students, old_version + 1)
    
    # So sánh với version cũ
    if old_version > 0:
        compare_versions(supabase, old_version, classified_students)
    
    print("\n" + "=" * 80)
    print("✅ HOÀN THÀNH!")
    print("=" * 80)

if __name__ == "__main__":
    main()
