"""
Module đánh giá kỹ năng cho từng môn học
"""

import numpy as np
from course_definitions import COURSES, CLASSIFICATION_LEVELS


class SkillEvaluator:
    """Đánh giá kỹ năng của sinh viên theo từng môn học"""
    
    @staticmethod
    def evaluate_skills_for_course(course_name, score, time_minutes):
        """
        Đánh giá từng kỹ năng trong môn học
        
        Args:
            course_name: Tên môn học
            score: Điểm số môn học (0-10)
            time_minutes: Thời gian làm bài (phút)
            
        Returns:
            Dictionary với điểm từng kỹ năng
        """
        if course_name not in COURSES:
            return {}
        
        skills = COURSES[course_name]["skills"]
        skill_scores = {}
        
        # Điểm cơ bản dựa trên điểm môn học
        base_score = score
        
        # Điều chỉnh dựa trên thời gian (thời gian quá ngắn -> điểm kỹ năng thấp hơn)
        time_factor = 1.0
        # Rất nghiêm trọng: điểm >= 9.5 nhưng < 2 phút (có thể gian lận)
        if score >= 9.5 and time_minutes < 2:
            time_factor = 0.4  # Giảm 60% - nghiêm trọng nhất
        # Nghiêm trọng: điểm >= 9.0 nhưng < 5 phút
        elif score >= 9.0 and time_minutes < 5:
            time_factor = 0.5  # Giảm 50% - nghiêm trọng
        # Đáng nghi: điểm >= 8.0 nhưng < 10 phút
        elif score >= 8.0 and time_minutes < 10:
            time_factor = 0.7  # Giảm 30% - đáng nghi
        elif score >= 8.0 and time_minutes < 15:
            time_factor = 0.85  # Giảm 15% - hơi đáng nghi
        elif score >= 7.0 and time_minutes < 20:
            time_factor = 0.9  # Giảm 10% - ít đáng nghi
        
        # Tính điểm cho từng kỹ năng với một chút biến thiên
        np.random.seed(int(score * 100 + len(course_name)))  # Seed dựa trên điểm và tên môn
        
        for skill in skills:
            # Điểm kỹ năng = điểm cơ bản * time_factor + biến thiên nhỏ (-0.5 đến 0.5)
            variation = np.random.uniform(-0.5, 0.5)
            skill_score = max(0, min(10, base_score * time_factor + variation))
            skill_scores[skill] = round(skill_score, 2)
        
        return skill_scores
    
    @staticmethod
    def get_skill_level(skill_score):
        """
        Xác định mức độ kỹ năng
        
        Args:
            skill_score: Điểm kỹ năng (0-10)
            
        Returns:
            Mức độ: "Đạt", "Chưa đạt", "Xuất sắc", "Khá", "Trung bình", "Yếu"
        """
        if skill_score >= 8.5:
            return "Xuất sắc"
        elif skill_score >= 7.0:
            return "Khá"
        elif skill_score >= 5.5:
            return "Đạt"
        elif skill_score >= 4.0:
            return "Trung bình"
        else:
            return "Chưa đạt"
    
    @staticmethod
    def evaluate_all_courses(student_data):
        """
        Đánh giá tất cả kỹ năng cho tất cả môn học của sinh viên
        
        Args:
            student_data: Dictionary chứa thông tin các môn học và điểm số
            
        Returns:
            Dictionary với đánh giá kỹ năng cho từng môn
        """
        skill_evaluations = {}
        
        for course_name in COURSES.keys():
            if course_name in student_data.get("courses", {}):
                course_info = student_data["courses"][course_name]
                score = course_info.get("score", 0)
                time_minutes = course_info.get("time_minutes", 0)
                
                # Đánh giá kỹ năng
                skills = SkillEvaluator.evaluate_skills_for_course(
                    course_name, score, time_minutes
                )
                
                # Thêm mức độ cho từng kỹ năng
                skill_details = {}
                for skill_name, skill_score in skills.items():
                    skill_details[skill_name] = {
                        "score": skill_score,
                        "level": SkillEvaluator.get_skill_level(skill_score),
                        "passed": skill_score >= 5.5
                    }
                
                skill_evaluations[course_name] = {
                    "course_score": score,
                    "time_minutes": time_minutes,
                    "skills": skill_details,
                    "skills_summary": {
                        "total_skills": len(skills),
                        "passed_skills": sum(1 for s in skill_details.values() if s["passed"]),
                        "average_skill_score": np.mean(list(skills.values())) if skills else 0
                    }
                }
        
        return skill_evaluations

