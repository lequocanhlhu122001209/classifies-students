"""
He thong cham diem tich hop.
Ket hop diem bai tap chi tiet voi diem tong the tu SQL Server.
"""

import numpy as np
from collections import defaultdict


COURSE_NAME_TO_CODE = {
    'Nháº­p MÃ´n Láº­p TrÃ¬nh': 'NMLT',
    'KÄ© Thuáº­t Láº­p TrÃ¬nh': 'KTLT',
    'Cáº¥u trÃºc Dá»¯ Liá»‡u vÃ  Giáº£i Thuáº­t': 'CTDL',
    'Láº­p TrÃ¬nh HÆ°á»›ng Äá»‘i TÆ°á»£ng': 'OOP',
    'NMLT': 'NMLT',
    'KTLT': 'KTLT',
    'CTDL': 'CTDL',
    'OOP': 'OOP',
}


class IntegratedScoringSystem:
    """
    He thong cham diem tich hop.
    - Diem bai tap chi tiet (neu co)
    - Diem tong the
    """

    def __init__(self, students=None):
        print("Dang tai du lieu cho he thong tich hop...")
        self.students_data = {}
        self.exercises_data = {}
        self.course_scores_data = {}
        if students is not None:
            self._load_students(students, source="cache")
        else:
            self._load_from_sqlserver()

    def _ingest_students(self, students):
        for student in students:
            sid = student.get('student_id')
            if sid is None:
                continue

            self.students_data[sid] = student

            course_map = {}
            for course_name, course_data in (student.get('courses') or {}).items():
                course_code = COURSE_NAME_TO_CODE.get(course_name, course_name)
                course_map[course_code] = {
                    'student_id': sid,
                    'course_code': course_code,
                    'course_name': course_name,
                    'score': float(course_data.get('score', 0) or 0),
                    'midterm_score': float(course_data.get('midterm_score', 0) or 0),
                    'final_score': float(course_data.get('final_score', 0) or 0),
                    'homework_score': float(course_data.get('homework_score', 0) or 0),
                    'time_minutes': float(course_data.get('time_minutes', 0) or 0),
                }

            self.course_scores_data[sid] = course_map

    def _load_students(self, students, source):
        try:
            self._ingest_students(students)
            print(f"Loaded {len(self.students_data)} students from {source}")
            print(f"Loaded {len(self.exercises_data)} students with detailed exercises")
        except Exception as e:
            print(f"Warning: failed to load from {source}: {e}")
            self.students_data = {}
            self.exercises_data = {}
            self.course_scores_data = {}

    def _load_from_sqlserver(self):
        """Load data from SQL Server."""
        from sqlserver_sync import load_students_from_sqlserver

        students = load_students_from_sqlserver()
        self._load_students(students, source="sqlserver")

    def calculate_exercise_score(self, student_id):
        exercises = self.exercises_data.get(student_id, [])

        if not exercises:
            course_scores = self.course_scores_data.get(student_id, {})
            if not course_scores:
                return None

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

        course_avg = {c: sum(s) / len(s) for c, s in course_scores.items() if s}
        skill_avg = {
            c: {sk: sum(s) / len(s) for sk, s in skills.items() if s}
            for c, skills in skill_scores.items()
        }

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
        student = self.students_data.get(student_id)
        if not student:
            return None

        csv_data = student.get('csv_data', {})
        exercise_data = self.calculate_exercise_score(student_id)

        midterm = float(csv_data.get('midterm_score', 0) or 0)
        final = float(csv_data.get('final_score', 0) or 0)
        homework = float(csv_data.get('homework_score', 0) or 0)
        total_score = float(csv_data.get('total_score', 0) or 0)

        exercise_avg = exercise_data['exercise_avg'] if exercise_data else homework

        integrated_score = (
            exercise_avg * 0.30 +
            midterm * 0.30 +
            final * 0.40
        )

        if integrated_score >= 8.0:
            classification = "Giá»i"
        elif integrated_score >= 7.0:
            classification = "KhÃ¡"
        elif integrated_score >= 5.0:
            classification = "Trung BÃ¬nh"
        else:
            classification = "Yáº¿u"

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
        results = []

        print("\nDang phan tich tat ca sinh vien...")
        total = len(self.students_data)

        for idx, student_id in enumerate(self.students_data.keys()):
            result = self.calculate_integrated_score(student_id)
            if result:
                results.append(result)

            if (idx + 1) % 50 == 0:
                print(f"  Da xu ly {idx + 1}/{total} sinh vien...")

        print(f"Loaded integrated results for {len(results)} students")
        return results

    def print_student_report(self, student_id):
        result = self.calculate_integrated_score(student_id)

        if not result:
            print(f"Khong tim thay sinh vien {student_id}")
            return

        print("\n" + "=" * 80)
        print("BAO CAO CHI TIET SINH VIEN")
        print("=" * 80)

        print(f"\nThong tin co ban:")
        print(f"  Ma SV: {result['student_id']}")
        print(f"  Ho ten: {result['name']}")
        print(f"  Lop: {result['class']}")

        print(f"\nDiem so:")
        print(f"  Diem goc:      {result['original_score']:.2f}/10")
        print(f"  Diem tich hop: {result['integrated_score']:.2f}/10")
        print(f"  Chenh lech:    {result['score_difference']:+.2f}")
        print(f"  Phan loai:     {result['classification']}")

        print(f"\nCau thanh diem:")
        comp = result['components']
        print(f"  Bai tap (30%): {comp['exercise_avg']:.2f}")
        print(f"  Giua ky (30%): {comp['midterm']:.2f}")
        print(f"  Cuoi ky (40%): {comp['final']:.2f}")

        print("\n" + "=" * 80)


def main():
    print("=" * 80)
    print("HE THONG CHAM DIEM TICH HOP")
    print("=" * 80)

    system = IntegratedScoringSystem()
    results = system.analyze_all_students()

    if not results:
        print("Khong co du lieu de phan tich")
        return

    print("\n" + "=" * 80)
    print("THONG KE TONG QUAN")
    print("=" * 80)

    original_scores = [r['original_score'] for r in results]
    integrated_scores = [r['integrated_score'] for r in results]

    print(f"\nTong so sinh vien: {len(results)}")
    print(f"\nDiem trung binh:")
    print(f"  Diem goc:      {np.mean(original_scores):.2f}/10")
    print(f"  Diem tich hop: {np.mean(integrated_scores):.2f}/10")

    classifications = [r['classification'] for r in results]
    print(f"\nPhan loai:")
    for cls in ['Giá»i', 'KhÃ¡', 'Trung BÃ¬nh', 'Yáº¿u']:
        count = classifications.count(cls)
        pct = (count / len(results)) * 100
        print(f"  {cls:15s}: {count:3d} ({pct:5.1f}%)")


if __name__ == "__main__":
    main()
