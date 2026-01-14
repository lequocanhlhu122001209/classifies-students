"""
Data Generator - Load dữ liệu sinh viên từ SQL Server
"""

import os
import random
from dotenv import load_dotenv

load_dotenv()


class StudentDataGenerator:
    """
    Load và tạo dữ liệu sinh viên từ SQL Server
    """
    
    def __init__(self, seed=42, use_supabase=False, csv_path=None):
        self.seed = seed
        self.csv_path = csv_path
        random.seed(seed)
        
    def load_all_students(self):
        """Load tất cả sinh viên từ SQL Server"""
        return self._load_from_sqlserver()
    
    def _load_from_sqlserver(self):
        """Load dữ liệu từ SQL Server"""
        try:
            from sqlserver_sync import load_students_from_sqlserver
            
            print("Đang tải dữ liệu từ SQL Server...")
            students = load_students_from_sqlserver()
            
            if students:
                print(f"✓ Đã tải {len(students)} sinh viên từ SQL Server")
            else:
                print("⚠️ Không có dữ liệu, tạo dữ liệu mẫu...")
                students = self.generate_realistic_students(50)
            
            return students
            
        except Exception as e:
            print(f"⚠️ Lỗi load từ SQL Server: {e}")
            return self.generate_realistic_students(50)
    
    def generate_realistic_students(self, n_students=50):
        """Tạo dữ liệu sinh viên giả lập để test"""
        students = []
        
        courses = [
            "Nhập Môn Lập Trình",
            "Kĩ Thuật Lập Trình", 
            "Cấu trúc Dữ Liệu và Giải Thuật",
            "Lập Trình Hướng Đối Tượng"
        ]
        
        for i in range(n_students):
            student_id = 125001001 + i
            profile = random.choice(['excellent', 'good', 'average', 'weak'])
            
            if profile == 'excellent':
                base_score = random.uniform(8.0, 10.0)
                behavior = random.uniform(85, 100)
                attendance = random.uniform(0.9, 1.0)
            elif profile == 'good':
                base_score = random.uniform(7.0, 8.5)
                behavior = random.uniform(70, 90)
                attendance = random.uniform(0.8, 0.95)
            elif profile == 'average':
                base_score = random.uniform(5.0, 7.0)
                behavior = random.uniform(50, 75)
                attendance = random.uniform(0.6, 0.85)
            else:
                base_score = random.uniform(2.0, 5.5)
                behavior = random.uniform(30, 60)
                attendance = random.uniform(0.3, 0.7)
            
            course_data = {}
            for course in courses:
                score = max(0, min(10, base_score + random.uniform(-1, 1)))
                course_data[course] = {
                    'score': round(score, 2),
                    'midterm_score': round(max(0, min(10, score + random.uniform(-1.5, 1.5))), 2),
                    'final_score': round(max(0, min(10, score + random.uniform(-1, 1))), 2),
                    'homework_score': round(max(0, min(10, score + random.uniform(-0.5, 0.5))), 2),
                    'time_minutes': round(random.uniform(30, 180), 1)
                }
            
            students.append({
                'student_id': student_id,
                'name': f'Sinh viên {i + 1}',
                'class': f'22CT{111 + (i % 3)}',
                'courses': course_data,
                'csv_data': {
                    'total_score': round(base_score, 2),
                    'midterm_score': round(base_score + random.uniform(-1, 1), 2),
                    'final_score': round(base_score + random.uniform(-0.5, 0.5), 2),
                    'behavior_score_100': round(behavior, 1),
                    'attendance_rate': round(attendance, 2),
                    'late_submissions': random.randint(0, 15),
                    'assignment_completion': round(random.uniform(0.5, 1.0), 2),
                    'study_hours_per_week': round(random.uniform(5, 30), 1)
                }
            })
        
        return students
