"""
Script chính để chạy hệ thống phân loại sinh viên
"""

import json
from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from course_definitions import COURSES


def print_separator(char="=", length=80):
    """In dòng phân cách"""
    print(char * length)


def print_student_detail(student, skill_evaluations):
    """
    In chi tiết thông tin sinh viên
    
    Args:
        student: Dictionary chứa thông tin sinh viên
        skill_evaluations: Dictionary chứa đánh giá kỹ năng
    """
    print_separator()
    print(f"\n📊 THÔNG TIN SINH VIÊN: {student.get('name', 'N/A')} (ID: {student.get('student_id', 'N/A')})")
    print_separator("-")
    
    # Phân loại tổng quan
    print(f"\n🎯 PHÂN LOẠI TỔNG QUAN:")
    print(f"  • K-means: {student.get('kmeans_prediction', 'N/A')}")
    print(f"  • KNN: {student.get('knn_prediction', 'N/A')}")
    print(f"  • Kết quả cuối cùng: {student.get('final_level', 'N/A')}")
    
    if student.get('anomaly_detected', False):
        print(f"  ⚠️  CẢNH BÁO: {student.get('anomaly_reason', 'Phát hiện bất thường')}")
    
    # Thông tin từng môn học
    print(f"\n📚 KẾT QUẢ CÁC MÔN HỌC:")
    
    for course_name in COURSES.keys():
        if course_name in student.get("courses", {}):
            course_data = student["courses"][course_name]
            course_score = course_data.get("score", 0)
            time_minutes = course_data.get("time_minutes", 0)
            
            print(f"\n  📖 {course_name}:")
            print(f"     • Điểm số: {course_score:.2f}/10")
            print(f"     • Thời gian làm bài: {time_minutes:.1f} phút")
            
            # Đánh giá kỹ năng
            if course_name in skill_evaluations:
                skill_info = skill_evaluations[course_name]
                skills_summary = skill_info.get("skills_summary", {})
                
                print(f"     • Kỹ năng: {skills_summary.get('passed_skills', 0)}/{skills_summary.get('total_skills', 0)} đạt")
                print(f"     • Điểm kỹ năng trung bình: {skills_summary.get('average_skill_score', 0):.2f}/10")
                
                print(f"\n     🔍 CHI TIẾT KỸ NĂNG:")
                for skill_name, skill_data in skill_info.get("skills", {}).items():
                    level_emoji = {
                        "Xuất sắc": "🌟",
                        "Khá": "✅",
                        "Đạt": "✓",
                        "Trung bình": "⚠️",
                        "Chưa đạt": "❌"
                    }
                    emoji = level_emoji.get(skill_data.get("level", ""), "•")
                    passed = "✓" if skill_data.get("passed", False) else "✗"
                    print(f"       {emoji} {skill_name}: {skill_data.get('score', 0):.2f}/10 "
                          f"({skill_data.get('level', 'N/A')}) [{passed}]")


def print_summary(students, skill_evaluations_all):
    """
    In tổng kết kết quả phân loại
    
    Args:
        students: Danh sách sinh viên đã được phân loại
        skill_evaluations_all: Dictionary chứa đánh giá kỹ năng cho tất cả sinh viên
    """
    print_separator("=", 100)
    print("\n📈 TỔNG KẾT PHÂN LOẠI SINH VIÊN")
    print_separator("=", 100)
    
    # Thống kê theo mức độ
    level_counts = {
        "Xuat sac": 0,
        "Kha": 0,
        "Trung binh": 0,
        "Yeu": 0
    }
    
    anomaly_count = 0
    
    for student in students:
        final_level = student.get("final_level", "Unknown")
        if final_level in level_counts:
            level_counts[final_level] += 1
        
        if student.get("anomaly_detected", False):
            anomaly_count += 1
    
    print(f"\n📊 Phân bố theo mức độ:")
    level_names = {
        "Xuat sac": "Xuất sắc",
        "Kha": "Khá",
        "Trung binh": "Trung bình",
        "Yeu": "Yếu"
    }
    
    total = len(students)
    for level, count in level_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  • {level_names.get(level, level)}: {count} sinh viên ({percentage:.1f}%)")
    
    print(f"\n⚠️  Số sinh viên có dấu hiệu bất thường: {anomaly_count}")
    
    # Thống kê theo môn học
    print(f"\n📚 Thống kê kỹ năng theo môn học:")
    
    for course_name in COURSES.keys():
        total_students = 0
        total_passed_skills = 0
        total_skills = 0
        total_avg_skill_score = 0
        
        for student_id, skill_eval in skill_evaluations_all.items():
            if course_name in skill_eval:
                total_students += 1
                skill_info = skill_eval[course_name]
                skills_summary = skill_info.get("skills_summary", {})
                total_passed_skills += skills_summary.get("passed_skills", 0)
                total_skills += skills_summary.get("total_skills", 0)
                total_avg_skill_score += skills_summary.get("average_skill_score", 0)
        
        if total_students > 0:
            avg_passed_ratio = (total_passed_skills / total_skills * 100) if total_skills > 0 else 0
            avg_skill_score = total_avg_skill_score / total_students
            print(f"  • {course_name}:")
            print(f"     - Tỷ lệ kỹ năng đạt: {avg_passed_ratio:.1f}%")
            print(f"     - Điểm kỹ năng trung bình: {avg_skill_score:.2f}/10")


def main():
    """Hàm chính"""
    print_separator("=", 100)
    print("🎓 HỆ THỐNG PHÂN LOẠI SINH VIÊN THEO KỸ NĂNG")
    print("   Sử dụng K-means và KNN để phát hiện bất thường")
    print_separator("=", 100)
    
    # 1. Tạo dữ liệu sinh viên giả lập
    print("\n📝 Đang tạo dữ liệu sinh viên giả lập...")
    generator = StudentDataGenerator(seed=42)
    students = generator.generate_realistic_students(n_students=50)
    print(f"✅ Đã tạo {len(students)} sinh viên")
    
    # 2. Đánh giá kỹ năng cho từng sinh viên
    print("\n🔍 Đang đánh giá kỹ năng cho từng sinh viên...")
    skill_evaluator = SkillEvaluator()
    skill_evaluations_all = {}
    
    for student in students:
        skill_evaluations = skill_evaluator.evaluate_all_courses(student)
        student["skill_evaluations"] = skill_evaluations
        skill_evaluations_all[student["student_id"]] = skill_evaluations
    
    print(f"✅ Đã đánh giá kỹ năng cho {len(students)} sinh viên")
    
    # 3. Phân loại sinh viên bằng K-means và KNN
    print("\n🤖 Đang phân loại sinh viên bằng K-means và KNN...")
    classifier = StudentClassifier(n_clusters=4)
    classifier.fit(students)
    classified_students = classifier.predict(students)
    print(f"✅ Đã phân loại {len(classified_students)} sinh viên")
    
    # 4. Hiển thị kết quả
    print_summary(classified_students, skill_evaluations_all)
    
    # 5. Hiển thị chi tiết một vài sinh viên
    print("\n\n" + "=" * 100)
    print("📋 CHI TIẾT MỘT SỐ SINH VIÊN (mẫu)")
    print("=" * 100)
    
    # Hiển thị 5 sinh viên đầu tiên
    for student in classified_students[:5]:
        student_id = student.get("student_id")
        if student_id in skill_evaluations_all:
            print_student_detail(student, skill_evaluations_all[student_id])
    
    # Hiển thị một số sinh viên có bất thường
    anomaly_students = [s for s in classified_students if s.get("anomaly_detected", False)]
    if anomaly_students:
        print("\n\n" + "=" * 100)
        print("⚠️  SINH VIÊN CÓ DẤU HIỆU BẤT THƯỜNG")
        print("=" * 100)
        
        for student in anomaly_students[:3]:  # Hiển thị 3 sinh viên có bất thường
            student_id = student.get("student_id")
            if student_id in skill_evaluations_all:
                print_student_detail(student, skill_evaluations_all[student_id])
    
    # Lưu kết quả vào file JSON
    print("\n\n💾 Đang lưu kết quả vào file...")
    output_data = {
        "students": classified_students,
        "skill_evaluations": skill_evaluations_all,
        "summary": {
            "total_students": len(classified_students),
            "level_counts": {
                "Xuat sac": sum(1 for s in classified_students if s.get("final_level") == "Xuat sac"),
                "Kha": sum(1 for s in classified_students if s.get("final_level") == "Kha"),
                "Trung binh": sum(1 for s in classified_students if s.get("final_level") == "Trung binh"),
                "Yeu": sum(1 for s in classified_students if s.get("final_level") == "Yeu")
            },
            "anomaly_count": sum(1 for s in classified_students if s.get("anomaly_detected", False))
        }
    }
    
    with open("classification_results.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("✅ Đã lưu kết quả vào file 'classification_results.json'")
    print("\n" + "=" * 100)
    print("✨ Hoàn thành!")
    print("=" * 100)


if __name__ == "__main__":
    main()

