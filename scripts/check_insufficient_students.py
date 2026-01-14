"""
Script kiểm tra sinh viên thiếu dữ liệu
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

from data_generator import StudentDataGenerator

def check_insufficient_students():
    """Kiểm tra và liệt kê sinh viên thiếu dữ liệu"""
    
    # Load sinh viên từ Supabase
    generator = StudentDataGenerator(seed=42, use_supabase=True)
    students = generator.load_all_students()
    
    print(f"\n📊 Tổng số sinh viên: {len(students)}")
    print("=" * 80)
    
    insufficient = []
    
    for student in students:
        courses = student.get("courses", {})
        csv_data = student.get("csv_data", {})
        
        # Kiểm tra điểm
        has_course_score = False
        has_time = False
        
        course_scores = []
        course_times = []
        
        for course_name, course_data in courses.items():
            if isinstance(course_data, dict):
                score = float(course_data.get("score", 0))
                time_mins = float(course_data.get("time_minutes", 0))
                course_scores.append((course_name, score))
                course_times.append((course_name, time_mins))
                if score > 0:
                    has_course_score = True
                if time_mins > 0:
                    has_time = True
        
        # Hoặc có điểm từ csv_data
        total_score = float(csv_data.get("total_score", 0))
        if total_score > 0:
            has_course_score = True
        
        # Nếu thiếu dữ liệu
        if not (has_course_score and has_time):
            reason = []
            if not has_course_score:
                reason.append("Không có điểm")
            if not has_time:
                reason.append("Không có thời gian làm bài")
            
            insufficient.append({
                "student_id": student.get("student_id"),
                "name": student.get("name"),
                "class": student.get("class") or csv_data.get("class"),
                "reason": " + ".join(reason),
                "course_scores": course_scores,
                "course_times": course_times,
                "total_score": total_score
            })
    
    print(f"\n⚠️ Số sinh viên thiếu dữ liệu: {len(insufficient)}")
    print("=" * 80)
    
    # Phân loại theo lý do
    no_score = [s for s in insufficient if "Không có điểm" in s["reason"]]
    no_time = [s for s in insufficient if "Không có thời gian" in s["reason"] and "Không có điểm" not in s["reason"]]
    both = [s for s in insufficient if "Không có điểm" in s["reason"] and "Không có thời gian" in s["reason"]]
    
    print(f"\n📌 Phân loại:")
    print(f"   - Chỉ thiếu điểm: {len(no_score) - len(both)}")
    print(f"   - Chỉ thiếu thời gian: {len(no_time)}")
    print(f"   - Thiếu cả hai: {len(both)}")
    
    print("\n" + "=" * 80)
    print("📋 DANH SÁCH CHI TIẾT:")
    print("=" * 80)
    
    for i, s in enumerate(insufficient, 1):
        print(f"\n{i}. MSSV: {s['student_id']} - {s['name']}")
        print(f"   Lớp: {s['class']}")
        print(f"   Lý do: {s['reason']}")
        print(f"   Total score (csv): {s['total_score']}")
        print(f"   Điểm các môn: {s['course_scores']}")
        print(f"   Thời gian: {s['course_times']}")
    
    return insufficient

if __name__ == "__main__":
    check_insufficient_students()
