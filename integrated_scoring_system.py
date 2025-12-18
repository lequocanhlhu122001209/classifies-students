"""
Hệ thống chấm điểm tích hợp
Kết hợp điểm bài tập chi tiết với điểm tổng thể từ Supabase
"""

import os
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')


class IntegratedScoringSystem:
    """
    Hệ thống chấm điểm tích hợp
    - Điểm bài tập chi tiết (từ Supabase)
    - Điểm tổng thể (từ Supabase)
    """
    
    def __init__(self):
        print("Đang tải dữ liệu từ Supabase...")
        self.students_data = {}
        self.exercises_data = {}
        self.course_scores_data = {}
        self._load_from_supabase()
        
    def _load_from_supabase(self):
        """Load dữ liệu từ Supabase"""
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Load students
            students_result = supabase.table('students').select('*').execute()
            for s in students_result.data:
                self.students_data[s['student_id']] = s
            
            # Load student_csv_data (hành vi)
            csv_data_result = supabase.table('student_csv_data').select('*').execute()
            for c in csv_data_result.data:
                sid = c['student_id']
                if sid in self.students_data:
                    self.students_data[sid]['csv_data'] = c
            
            # Load course_scores
            scores_result = supabase.table('course_scores').select('*').execute()
            for score in scores_result.data:
                sid = score['student_id']
                if sid not in self.course_scores_data:
                    self.course_scores_data[sid] = {}
                self.course_scores_data[sid][score['course_code']] = score
            
            # Load exercise_details
            exercises_result = supabase.table('exercise_details').select('*').execute()
            for ex in exercises_result.data:
                sid = ex['student_id']
                if sid not in self.exercises_data:
                    self.exercises_data[sid] = []
                self.exercises_data[sid].append(ex)
            
            print(f"✓ Đã tải {len(self.students_data)} sinh viên từ Supabase")
            print(f"✓ Đã tải {len(self.exercises_data)} sinh viên có bài tập")
            
        except Exception as e:
            print(f"⚠️ Lỗi khi load từ Supabase: {e}")
            self.students_data = {}
            self.exercises_data = {}
            self.course_scores_data = {}
        
    def calculate_exercise_score(self, student_id):
        """
        Tính điểm từ bài tập chi tiết
        """
        exercises = self.exercises_data.get(student_id, [])
        
        if not exercises:
            # Nếu không có bài tập chi tiết, dùng điểm từ course_scores
            course_scores = self.course_scores_data.get(student_id, {})
            if not course_scores:
                return None
            
            # Tính điểm trung bình từ course_scores
            scores = [float(c.get('score', 0) or 0) for c in course_scores.values()]
            exercise_avg = sum(scores) / len(scores) if scores else 0
            
            return {
                'exercise_avg': round(exercise_avg, 2),
                'course_scores': {c: float(d.get('score', 0) or 0) for c, d in course_scores.items()},
                'skill_scores': {},
                'total_exercises': 0,
                'anomaly_count': 0,
                'detailed_exercises': {}
            }
        
        # Tính điểm từ bài tập chi tiết
        course_scores = defaultdict(list)
        skill_scores = defaultdict(lambda: defaultdict(list))
        anomaly_count = 0
        
        for ex in exercises:
            course = ex.get('course_code', '')
            skill = ex.get('skill_code', '')
            score = float(ex.get('score', 0) or 0)
            is_anomaly = ex.get('is_anomaly', False)
            
            course_scores[course].append(score)
            skill_scores[course][skill].append(score)
            if is_anomaly:
                anomaly_count += 1
        
        # Tính trung bình
        course_avg = {c: sum(s)/len(s) for c, s in course_scores.items() if s}
        skill_avg = {c: {sk: sum(s)/len(s) for sk, s in skills.items() if s} 
                     for c, skills in skill_scores.items()}
        
        all_scores = [s for scores in course_scores.values() for s in scores]
        exercise_avg = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return {
            'exercise_avg': round(exercise_avg, 2),
            'course_scores': course_avg,
            'skill_scores': skill_avg,
            'total_exercises': len(exercises),
            'anomaly_count': anomaly_count,
            'detailed_exercises': {}
        }
    
    def calculate_integrated_score(self, student_id):
        """
        Tính điểm tích hợp
        
        Công thức:
        - Điểm bài tập: 30%
        - Điểm giữa kỳ + trên lớp: 30%
        - Điểm cuối kỳ: 40%
        """
        student = self.students_data.get(student_id)
        if not student:
            return None
        
        csv_data = student.get('csv_data', {})
        
        # Lấy điểm bài tập
        exercise_data = self.calculate_exercise_score(student_id)
        
        # Lấy điểm từ csv_data hoặc course_scores
        midterm = float(csv_data.get('midterm_score', 0) or 0)
        final = float(csv_data.get('final_score', 0) or 0)
        homework = float(csv_data.get('homework_score', 0) or 0)
        total_score = float(csv_data.get('total_score', 0) or 0)
        
        # Nếu không có exercise_data, dùng homework
        exercise_avg = exercise_data['exercise_avg'] if exercise_data else homework
        
        # Công thức tích hợp
        integrated_score = (
            exercise_avg * 0.30 +      # 30% điểm bài tập
            midterm * 0.30 +            # 30% giữa kỳ
            final * 0.40                # 40% cuối kỳ
        )
        
        # Phân loại
        if integrated_score >= 8.0:
            classification = "Giỏi"
        elif integrated_score >= 7.0:
            classification = "Khá"
        elif integrated_score >= 5.0:
            classification = "Trung Bình"
        else:
            classification = "Yếu"
        
        # So sánh với điểm gốc
        original_score = total_score if total_score > 0 else (midterm * 0.3 + final * 0.5 + homework * 0.2)
        score_difference = integrated_score - original_score
        
        return {
            'student_id': student_id,
            'name': student.get('name', ''),
            'class': student.get('class', ''),
            'original_score': round(original_score, 2),
            'integrated_score': round(integrated_score, 2),
            'score_difference': round(score_difference, 2),
            'classification': classification,
            'components': {
                'exercise_avg': exercise_avg,
                'midterm': midterm,
                'final': final,
                'homework': homework
            },
            'exercise_data': exercise_data or {
                'exercise_avg': homework,
                'course_scores': {},
                'skill_scores': {},
                'total_exercises': 0,
                'anomaly_count': 0
            },
            'original_data': {
                'attendance_rate': float(csv_data.get('attendance_rate', 0) or 0),
                'study_hours': float(csv_data.get('study_hours_per_week', 0) or 0),
                'assignment_completion': float(csv_data.get('assignment_completion', 0) or 0),
                'behavior_score': float(csv_data.get('behavior_score_100', 0) or 0)
            }
        }
    
    def analyze_all_students(self):
        """Phân tích tất cả sinh viên"""
        results = []
        
        print("\nĐang phân tích tất cả sinh viên...")
        total = len(self.students_data)
        
        for idx, student_id in enumerate(self.students_data.keys()):
            result = self.calculate_integrated_score(student_id)
            if result:
                results.append(result)
            
            if (idx + 1) % 50 == 0:
                print(f"  Đã xử lý {idx + 1}/{total} sinh viên...")
        
        print(f"✓ Đã phân tích {len(results)} sinh viên")
        return results
    
    def print_student_report(self, student_id):
        """In báo cáo chi tiết cho 1 sinh viên"""
        result = self.calculate_integrated_score(student_id)
        
        if not result:
            print(f"Không tìm thấy sinh viên {student_id}")
            return
        
        print("\n" + "="*80)
        print(f"BÁO CÁO CHI TIẾT SINH VIÊN")
        print("="*80)
        
        print(f"\nThông tin cơ bản:")
        print(f"  Mã SV: {result['student_id']}")
        print(f"  Họ tên: {result['name']}")
        print(f"  Lớp: {result['class']}")
        
        print(f"\nĐiểm số:")
        print(f"  Điểm gốc:        {result['original_score']:.2f}/10")
        print(f"  Điểm tích hợp:   {result['integrated_score']:.2f}/10")
        print(f"  Chênh lệch:      {result['score_difference']:+.2f}")
        print(f"  Phân loại:       {result['classification']}")
        
        print(f"\nCấu thành điểm:")
        comp = result['components']
        print(f"  Bài tập (30%):   {comp['exercise_avg']:.2f}")
        print(f"  Giữa kỳ (30%):   {comp['midterm']:.2f}")
        print(f"  Cuối kỳ (40%):   {comp['final']:.2f}")
        
        print("\n" + "="*80)


def main():
    """Demo hệ thống"""
    print("="*80)
    print("HỆ THỐNG CHẤM ĐIỂM TÍCH HỢP")
    print("="*80)
    
    system = IntegratedScoringSystem()
    results = system.analyze_all_students()
    
    if not results:
        print("Không có dữ liệu để phân tích")
        return
    
    # Thống kê
    print("\n" + "="*80)
    print("THỐNG KÊ TỔNG QUAN")
    print("="*80)
    
    original_scores = [r['original_score'] for r in results]
    integrated_scores = [r['integrated_score'] for r in results]
    
    print(f"\nTổng số sinh viên: {len(results)}")
    print(f"\nĐiểm trung bình:")
    print(f"  Điểm gốc:      {np.mean(original_scores):.2f}/10")
    print(f"  Điểm tích hợp: {np.mean(integrated_scores):.2f}/10")
    
    # Phân loại
    classifications = [r['classification'] for r in results]
    print(f"\nPhân loại:")
    for cls in ['Giỏi', 'Khá', 'Trung Bình', 'Yếu']:
        count = classifications.count(cls)
        pct = (count / len(results)) * 100
        print(f"  {cls:15s}: {count:3d} ({pct:5.1f}%)")


if __name__ == "__main__":
    main()
