"""
Data Generator - Load dữ liệu sinh viên từ Supabase
"""

import os
import random
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')


class StudentDataGenerator:
    """
    Load và tạo dữ liệu sinh viên
    - Load từ Supabase (production)
    - Tạo dữ liệu giả lập (testing)
    """
    
    def __init__(self, seed=42, use_supabase=True, csv_path=None):
        self.seed = seed
        self.use_supabase = use_supabase
        self.csv_path = csv_path
        random.seed(seed)
        
    def load_all_students(self):
        """Load tất cả sinh viên từ Supabase"""
        if self.use_supabase:
            return self._load_from_supabase()
        return self.generate_realistic_students(50)
    
    def _load_from_supabase(self):
        """Load dữ liệu từ Supabase"""
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Load students
            students_result = supabase.table('students').select('*').execute()
            students = {s['student_id']: s for s in students_result.data}
            
            # Load csv_data (hành vi)
            csv_result = supabase.table('student_csv_data').select('*').execute()
            for c in csv_result.data:
                sid = c['student_id']
                if sid in students:
                    students[sid]['csv_data'] = c
            
            # Load course_scores
            scores_result = supabase.table('course_scores').select('*').execute()
            for score in scores_result.data:
                sid = score['student_id']
                if sid in students:
                    if 'courses' not in students[sid]:
                        students[sid]['courses'] = {}
                    students[sid]['courses'][score['course_code']] = {
                        'score': float(score.get('score', 0) or 0),
                        'midterm_score': float(score.get('midterm_score', 0) or 0),
                        'final_score': float(score.get('final_score', 0) or 0),
                        'homework_score': float(score.get('homework_score', 0) or 0),
                        'time_minutes': float(score.get('time_minutes', 0) or 0)
                    }
            
            return list(students.values())
            
        except Exception as e:
            print(f"⚠️ Lỗi load từ Supabase: {e}")
            return []
    
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
            
            # Random profile
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
            
            # Generate course scores
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
