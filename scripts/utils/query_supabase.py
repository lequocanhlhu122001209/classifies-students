"""
Script để query dữ liệu từ Supabase
"""

from supabase import create_client, Client
from pprint import pprint
import json

# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================

SUPABASE_URL = "https://odmtndvllclmrwczcyvs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA"

# Khởi tạo Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_all_students():
    """Lấy tất cả sinh viên"""
    print("\n📋 Danh sách sinh viên:")
    response = supabase.table('students').select('*').execute()
    print(f"Tổng: {len(response.data)} sinh viên")
    return response.data

def get_student_by_id(student_id):
    """Lấy thông tin chi tiết một sinh viên"""
    print(f"\n👤 Thông tin sinh viên ID: {student_id}")
    
    # Thông tin cơ bản
    student = supabase.table('students').select('*').eq('student_id', student_id).execute()
    
    # Dữ liệu CSV
    csv_data = supabase.table('student_csv_data').select('*').eq('student_id', student_id).execute()
    
    # Điểm môn học
    courses = supabase.table('course_scores').select('*').eq('student_id', student_id).execute()
    
    # Phân loại
    classification = supabase.table('classifications').select('*').eq('student_id', student_id).execute()
    
    # Điểm tích hợp
    integrated = supabase.table('integrated_scores').select('*').eq('student_id', student_id).execute()
    
    result = {
        'student': student.data[0] if student.data else None,
        'csv_data': csv_data.data[0] if csv_data.data else None,
        'courses': courses.data,
        'classification': classification.data[0] if classification.data else None,
        'integrated_score': integrated.data[0] if integrated.data else None
    }
    
    return result

def get_statistics():
    """Lấy thống kê tổng quan"""
    print("\n📊 Thống kê tổng quan:")
    
    # Tổng sinh viên
    students = supabase.table('students').select('*', count='exact').execute()
    total_students = students.count
    
    # Phân loại
    classifications = supabase.table('classifications').select('*').execute()
    
    # Map tên level từ database (không dấu) sang hiển thị (có dấu)
    level_mapping = {
        'Xuat sac': 'Xuất sắc',
        'Kha': 'Khá',
        'Trung binh': 'Trung bình',
        'Yeu': 'Yếu'
    }
    
    level_counts = {
        'Xuất sắc': 0,
        'Khá': 0,
        'Trung bình': 0,
        'Yếu': 0
    }
    
    anomaly_count = 0
    
    for c in classifications.data:
        level = c.get('final_level', '')
        # Map level từ database sang tên hiển thị
        display_level = level_mapping.get(level, level)
        if display_level in level_counts:
            level_counts[display_level] += 1
        if c.get('anomaly_detected', False):
            anomaly_count += 1
    
    stats = {
        'total_students': total_students,
        'level_distribution': level_counts,
        'anomaly_count': anomaly_count
    }
    
    return stats

def get_students_by_class(class_name):
    """Lấy sinh viên theo lớp"""
    print(f"\n📚 Sinh viên lớp {class_name}:")
    response = supabase.table('students').select('*').eq('class', class_name).execute()
    print(f"Tổng: {len(response.data)} sinh viên")
    return response.data

def get_students_by_level(level):
    """Lấy sinh viên theo mức độ"""
    print(f"\n🎯 Sinh viên mức độ {level}:")
    
    # Lấy student_ids từ classifications
    classifications = supabase.table('classifications').select('student_id').eq('final_level', level).execute()
    student_ids = [c['student_id'] for c in classifications.data]
    
    # Lấy thông tin sinh viên
    students = supabase.table('students').select('*').in_('student_id', student_ids).execute()
    print(f"Tổng: {len(students.data)} sinh viên")
    return students.data

def get_anomaly_students():
    """Lấy sinh viên có bất thường"""
    print("\n⚠️  Sinh viên có bất thường:")
    
    # Lấy classifications có anomaly
    classifications = supabase.table('classifications').select('*').eq('anomaly_detected', True).execute()
    
    results = []
    for c in classifications.data:
        student_id = c['student_id']
        student = supabase.table('students').select('*').eq('student_id', student_id).execute()
        
        if student.data:
            results.append({
                'student': student.data[0],
                'classification': c
            })
    
    print(f"Tổng: {len(results)} sinh viên")
    return results

def get_course_statistics():
    """Thống kê theo môn học"""
    print("\n📈 Thống kê theo môn học:")
    
    courses = ['NMLT', 'KTLT', 'CTDL', 'OOP']
    course_names = {
        'NMLT': 'Nhập Môn Lập Trình',
        'KTLT': 'Kĩ Thuật Lập Trình',
        'CTDL': 'Cấu trúc Dữ Liệu và Giải Thuật',
        'OOP': 'Lập Trình Hướng Đối Tượng'
    }
    
    stats = {}
    for course_code in courses:
        scores = supabase.table('course_scores').select('score').eq('course_code', course_code).execute()
        
        if scores.data:
            score_list = [s['score'] for s in scores.data]
            stats[course_names[course_code]] = {
                'total_students': len(score_list),
                'avg_score': round(sum(score_list) / len(score_list), 2),
                'min_score': min(score_list),
                'max_score': max(score_list)
            }
    
    return stats

def get_top_students(limit=10):
    """Lấy top sinh viên"""
    print(f"\n🏆 Top {limit} sinh viên:")
    
    # Lấy từ integrated_scores
    top = supabase.table('integrated_scores').select('*').order('integrated_score', desc=True).limit(limit).execute()
    
    results = []
    for score in top.data:
        student_id = score['student_id']
        student = supabase.table('students').select('*').eq('student_id', student_id).execute()
        
        if student.data:
            results.append({
                'student': student.data[0],
                'integrated_score': score
            })
    
    return results

def search_students(keyword):
    """Tìm kiếm sinh viên theo tên"""
    print(f"\n🔍 Tìm kiếm: {keyword}")
    
    response = supabase.table('students').select('*').ilike('name', f'%{keyword}%').execute()
    print(f"Tìm thấy: {len(response.data)} sinh viên")
    return response.data

# ============================================================================
# DEMO QUERIES
# ============================================================================

def demo_queries():
    """Demo các query"""
    print("=" * 80)
    print("🔍 DEMO QUERIES - SUPABASE")
    print("=" * 80)
    
    # 1. Thống kê tổng quan
    stats = get_statistics()
    print(f"\nTổng sinh viên: {stats['total_students']}")
    print("\nPhân bố mức độ:")
    for level, count in stats['level_distribution'].items():
        pct = (count / stats['total_students']) * 100 if stats['total_students'] > 0 else 0
        print(f"  • {level:15s}: {count:3d} ({pct:5.1f}%)")
    print(f"\nBất thường: {stats['anomaly_count']}")
    
    # 2. Thống kê môn học
    course_stats = get_course_statistics()
    print("\nĐiểm trung bình theo môn:")
    for course, stat in course_stats.items():
        print(f"  • {course:40s}: {stat['avg_score']:.2f}")
    
    # 3. Top sinh viên
    top_students = get_top_students(5)
    print("\nTop 5 sinh viên:")
    for i, item in enumerate(top_students, 1):
        student = item['student']
        score = item['integrated_score']
        print(f"  {i}. {student['name']:30s} - {score['integrated_score']:.2f}")
    
    # 4. Sinh viên có bất thường
    anomalies = get_anomaly_students()
    if anomalies:
        print("\nSinh viên có bất thường:")
        for item in anomalies[:5]:
            student = item['student']
            classification = item['classification']
            print(f"  • {student['name']:30s} - {classification['final_level']}")
            for reason in classification.get('anomaly_reasons', []):
                print(f"    - {reason}")
    
    # 5. Chi tiết một sinh viên
    if top_students:
        student_id = top_students[0]['student']['student_id']
        detail = get_student_by_id(student_id)
        
        print(f"\nChi tiết sinh viên ID {student_id}:")
        print(f"  Tên: {detail['student']['name']}")
        print(f"  Lớp: {detail['student']['class']}")
        print(f"  Phân loại: {detail['classification']['final_level']}")
        print(f"  Điểm tích hợp: {detail['integrated_score']['integrated_score']:.2f}")
        print(f"  Số môn: {len(detail['courses'])}")
    
    print("\n" + "=" * 80)
    print("✅ HOÀN THÀNH DEMO!")
    print("=" * 80)

# ============================================================================
# INTERACTIVE MENU
# ============================================================================

def interactive_menu():
    """Menu tương tác"""
    while True:
        print("\n" + "=" * 80)
        print("📊 SUPABASE QUERY MENU")
        print("=" * 80)
        print("\n1. Thống kê tổng quan")
        print("2. Danh sách sinh viên")
        print("3. Chi tiết sinh viên (theo ID)")
        print("4. Sinh viên theo lớp")
        print("5. Sinh viên theo mức độ")
        print("6. Sinh viên có bất thường")
        print("7. Thống kê môn học")
        print("8. Top sinh viên")
        print("9. Tìm kiếm sinh viên")
        print("0. Thoát")
        
        choice = input("\nChọn (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 Tạm biệt!")
            break
        
        elif choice == '1':
            stats = get_statistics()
            pprint(stats)
        
        elif choice == '2':
            students = get_all_students()
            for s in students[:10]:
                print(f"  • {s['student_id']} - {s['name']} - {s['class']}")
            if len(students) > 10:
                print(f"  ... và {len(students) - 10} sinh viên khác")
        
        elif choice == '3':
            student_id = input("Nhập student_id: ").strip()
            try:
                detail = get_student_by_id(int(student_id))
                print("\n" + json.dumps(detail, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"❌ Lỗi: {str(e)}")
        
        elif choice == '4':
            class_name = input("Nhập tên lớp: ").strip()
            students = get_students_by_class(class_name)
            for s in students:
                print(f"  • {s['student_id']} - {s['name']}")
        
        elif choice == '5':
            print("\nMức độ: Xuất sắc, Khá, Trung bình, Yếu")
            level = input("Nhập mức độ: ").strip()
            students = get_students_by_level(level)
            for s in students[:10]:
                print(f"  • {s['student_id']} - {s['name']} - {s['class']}")
        
        elif choice == '6':
            anomalies = get_anomaly_students()
            for item in anomalies:
                student = item['student']
                classification = item['classification']
                print(f"\n  • {student['name']} ({student['class']})")
                print(f"    Phân loại: {classification['final_level']}")
                for reason in classification.get('anomaly_reasons', []):
                    print(f"    - {reason}")
        
        elif choice == '7':
            stats = get_course_statistics()
            pprint(stats)
        
        elif choice == '8':
            limit = input("Số lượng (mặc định 10): ").strip()
            limit = int(limit) if limit else 10
            top = get_top_students(limit)
            for i, item in enumerate(top, 1):
                student = item['student']
                score = item['integrated_score']
                print(f"  {i}. {student['name']:30s} - {score['integrated_score']:.2f}")
        
        elif choice == '9':
            keyword = input("Nhập từ khóa: ").strip()
            students = search_students(keyword)
            for s in students:
                print(f"  • {s['student_id']} - {s['name']} - {s['class']}")
        
        else:
            print("❌ Lựa chọn không hợp lệ!")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_queries()
    else:
        interactive_menu()
