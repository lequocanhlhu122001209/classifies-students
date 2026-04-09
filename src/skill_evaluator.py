"""
Module đánh giá kỹ năng cho từng môn học
"""

import numpy as np
import unicodedata
from course_definitions import COURSES, CLASSIFICATION_LEVELS


COURSE_NAME_MAPPING = {
    "Cấu Trúc Dữ Liệu": "Cấu trúc Dữ Liệu và Giải Thuật",
    "Kỹ Thuật Lập Trình": "Kĩ Thuật Lập Trình"
}

COURSE_CODE_TO_NAME = {
    "NMLT": "Nhập Môn Lập Trình",
    "KTLT": "Kĩ Thuật Lập Trình",
    "CTDL": "Cấu trúc Dữ Liệu và Giải Thuật",
    "OOP": "Lập Trình Hướng Đối Tượng"
}


def _parse_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(" ", "").replace(",", ".")
    filtered = "".join(ch for ch in normalized if ch.isdigit() or ch in ".+-")
    if not filtered:
        return None

    try:
        return float(filtered)
    except (TypeError, ValueError):
        return None


def _normalize_text(value):
    if value is None:
        return ""

    text = str(value)
    normalized = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in no_accents.lower() if ch.isalnum())


def _is_placeholder_course_name(course_name):
    normalized = _normalize_text(course_name)
    if not normalized:
        return True
    return normalized in {"null", "none", "undefined", "unknown", "na", "nan"}


def _to_canonical_course_name(course_name):
    if not course_name:
        return None

    raw_name = str(course_name).strip()
    if not raw_name:
        return None

    if raw_name in COURSES:
        return raw_name

    mapped = COURSE_NAME_MAPPING.get(raw_name)
    if mapped in COURSES:
        return mapped

    code_mapped = COURSE_CODE_TO_NAME.get(raw_name.upper())
    if code_mapped in COURSES:
        return code_mapped

    normalized_raw = _normalize_text(raw_name)
    if not normalized_raw:
        return None

    for canonical_name in COURSES:
        aliases = [canonical_name]

        for alias, standard in COURSE_NAME_MAPPING.items():
            if standard == canonical_name:
                aliases.append(alias)
            if alias == canonical_name:
                aliases.append(standard)

        for code, standard in COURSE_CODE_TO_NAME.items():
            if standard == canonical_name:
                aliases.append(code)

        if any(_normalize_text(alias) == normalized_raw for alias in aliases):
            return canonical_name

    for canonical_name in COURSES:
        normalized_canonical = _normalize_text(canonical_name)
        if normalized_raw in normalized_canonical or normalized_canonical in normalized_raw:
            return canonical_name

    return None


def _extract_course_entries(courses):
    if not courses:
        return []

    entries = []
    if isinstance(courses, list):
        for index, course_data in enumerate(courses):
            if not isinstance(course_data, dict):
                continue
            entries.append({
                "raw_course_name": course_data.get("course_name") or course_data.get("course") or course_data.get("course_code") or course_data.get("name") or str(index),
                "original_key": str(index),
                "course_data": course_data
            })
        return entries

    if isinstance(courses, dict):
        for key, course_data in courses.items():
            if not isinstance(course_data, dict):
                continue
            entries.append({
                "raw_course_name": course_data.get("course_name") or course_data.get("course") or course_data.get("course_code") or course_data.get("name") or key,
                "original_key": key,
                "course_data": course_data
            })
        return entries

    return []


def _build_canonical_course_map(courses):
    entries = _extract_course_entries(courses)
    canonical_map = {}
    unmatched_entries = []

    for entry in entries:
        canonical = _to_canonical_course_name(entry["raw_course_name"]) or _to_canonical_course_name(entry["original_key"])
        if canonical and canonical not in canonical_map:
            canonical_map[canonical] = entry["course_data"]
        else:
            unmatched_entries.append(entry)

    canonical_names = list(COURSES.keys())

    if not canonical_map and len(entries) == len(canonical_names):
        for index, course_name in enumerate(canonical_names):
            canonical_map[course_name] = entries[index]["course_data"]
    elif unmatched_entries and len(entries) == len(canonical_names):
        missing_courses = [name for name in canonical_names if name not in canonical_map]
        if len(missing_courses) == len(unmatched_entries):
            for index, course_name in enumerate(missing_courses):
                canonical_map[course_name] = unmatched_entries[index]["course_data"]

    placeholder_entries = [
        entry for entry in entries
        if _is_placeholder_course_name(entry["raw_course_name"]) or _is_placeholder_course_name(entry["original_key"])
    ]

    if placeholder_entries:
        fallback_data = placeholder_entries[0].get("course_data")
        if isinstance(fallback_data, dict):
            if not canonical_map and len(entries) == 1:
                for course_name in canonical_names:
                    canonical_map[course_name] = fallback_data
            else:
                for course_name in canonical_names:
                    if course_name not in canonical_map:
                        canonical_map[course_name] = fallback_data

    return canonical_map


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
        canonical_courses = _build_canonical_course_map(student_data.get("courses", {}))
        
        for course_name in COURSES.keys():
            if course_name in canonical_courses:
                course_info = canonical_courses[course_name]
                score = _parse_number(course_info.get("score")) if isinstance(course_info, dict) else None
                if score is None and isinstance(course_info, dict):
                    score = _parse_number(course_info.get("total_score"))
                if score is None and isinstance(course_info, dict):
                    score = _parse_number(course_info.get("avg_score"))
                if score is None and isinstance(course_info, dict):
                    score = _parse_number(course_info.get("course_score"))
                if score is None:
                    score = 0.0

                time_minutes = _parse_number(course_info.get("time_minutes")) if isinstance(course_info, dict) else None
                if time_minutes is None and isinstance(course_info, dict):
                    time_minutes = _parse_number(course_info.get("avg_time_minutes"))
                if time_minutes is None and isinstance(course_info, dict):
                    time_minutes = _parse_number(course_info.get("time"))
                if time_minutes is None:
                    time_minutes = 0.0
                
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

