"""
Định nghĩa các thành phần đánh giá và phân loại sinh viên dựa trên dữ liệu thực tế
"""

PERFORMANCE_METRICS = {
    "Học Tập": {
        "components": [
            "midterm_score",
            "final_score",
            "homework_score",
            "total_score"
        ],
        "weights": {
            "midterm_score": 0.3,
            "final_score": 0.4,
            "homework_score": 0.3,
            "total_score": 1.0  # Được sử dụng như điểm tổng hợp
        }
    },
    "Thái Độ": {
        "components": [
            "attendance_rate",
            "participation_score",
            "extra_activities",
            "behavior_score"
        ],
        "weights": {
            "attendance_rate": 0.3,
            "participation_score": 0.3,
            "extra_activities": 0.2,
            "behavior_score": 0.2
        }
    },
    "Nỗ Lực": {
        "components": [
            "study_hours_per_week",
            "lms_usage_hours",
            "assignment_completion",
            "late_submissions"
        ],
        "weights": {
            "study_hours_per_week": 0.3,
            "lms_usage_hours": 0.2,
            "assignment_completion": 0.3,
            "late_submissions": 0.2  # Điểm này sẽ được tính ngược (càng ít càng tốt)
        }
    }
}

# Định nghĩa ngưỡng chuẩn hóa cho các chỉ số
NORMALIZATION_THRESHOLDS = {
    "study_hours_per_week": {"min": 0, "max": 50},
    "lms_usage_hours": {"min": 0, "max": 20},
    "late_submissions": {"min": 0, "max": 10},
    "extra_activities": {"min": 0, "max": 5}
}

# Định nghĩa mức độ phân loại
CLASSIFICATION_LEVELS = {
    "Xuat sac": {
        "min_academic_score": 8.5,
        "min_behavior_score": 8.0,
        "min_effort_score": 8.0,
        "description": "Xuất sắc"
    },
    "Kha": {
        "min_academic_score": 7.0,
        "min_behavior_score": 7.0,
        "min_effort_score": 7.0,
        "description": "Khá"
    },
    "Trung binh": {
        "min_academic_score": 5.5,
        "min_behavior_score": 5.5,
        "min_effort_score": 5.5,
        "description": "Trung bình"
    },
    "Yeu": {
        "min_academic_score": 0.0,
        "min_behavior_score": 0.0,
        "min_effort_score": 0.0,
        "description": "Yếu"
    }
}

# Định nghĩa tính toán điểm tổng hợp
COMPOSITE_SCORE_WEIGHTS = {
    "academic": 0.5,    # Trọng số cho điểm học tập
    "behavior": 0.25,   # Trọng số cho điểm thái độ
    "effort": 0.25      # Trọng số cho điểm nỗ lực
}

# Danh sách môn học và kỹ năng tương ứng (đồng bộ với `templates/index.html`)
COURSES = {
    "Nhập Môn Lập Trình": {
        "skills": [
            "Cú pháp cơ bản (Syntax)", "Biến và Kiểu dữ liệu (Variables & Data Types)",
            "Cấu trúc điều khiển (Control Structures)", "Hàm cơ bản (Basic Functions)"
        ],
        "icon": "📝"
    },
    "Kĩ Thuật Lập Trình": {
        "skills": [
            "Thiết kế thuật toán (Algorithm Design)", "Tối ưu hóa mã nguồn (Code Optimization)",
            "Xử lý lỗi và Debugging (Error Handling)", "Lập trình có cấu trúc (Structured Programming)"
        ],
        "icon": "⚙️"
    },
    "Cấu trúc Dữ Liệu và Giải Thuật": {
        "skills": [
            "Mảng (Arrays)", "Danh sách liên kết (Linked Lists)",
            "Stack và Queue", "Cây (Trees)"
        ],
        "icon": "🌳"
    },
    "Lập Trình Hướng Đối Tượng": {
        "skills": [
            "Lớp và Đối tượng (Classes & Objects)", "Kế thừa (Inheritance)",
            "Đa hình (Polymorphism)", "Đóng gói (Encapsulation)"
        ],
        "icon": "🎯"
    }
}

