"""
Fill missing course scores and skill_evaluations for students in selected cohorts.
- Targets classes containing '22', '23', or '24'.
- For students with empty or all-zero course scores, generate plausible course scores
  (based on seed logic) and compute skill evaluations via `SkillEvaluator`.
- Upsert into SQL Server and sync to Supabase.
"""
import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sqlserver_sync import load_students_from_sqlserver, sync_all_to_sqlserver
from skill_evaluator import SkillEvaluator

TARGET_COHORT_KEYWORDS = ('22', '23', '24')
COURSES = [
    "Nhập Môn Lập Trình",
    "Kĩ Thuật Lập Trình",
    "Cấu trúc Dữ Liệu và Giải Thuật",
    "Lập Trình Hướng Đối Tượng",
]

def needs_fill(student):
    courses = student.get('courses') or {}
    if not courses:
        return True
    # If all course scores are zero or missing
    all_zero = True
    for c in courses.values():
        try:
            if float(c.get('score', 0) or 0) > 0:
                all_zero = False
                break
        except Exception:
            continue
    return all_zero


def generate_course_values(profile_base=6.5):
    # profile_base ~ mean score to center generated values
    data = {}
    for course in COURSES:
        score = max(0.0, min(10.0, round(random.normalvariate(profile_base, 1.0), 2)))
        mid = max(0.0, min(10.0, round(score + random.normalvariate(0, 0.8), 2)))
        fin = max(0.0, min(10.0, round(score + random.normalvariate(0, 0.8), 2)))
        hw = max(0.0, min(10.0, round(score + random.normalvariate(0, 0.8), 2)))
        time_minutes = round(random.uniform(80, 240), 1)
        data[course] = {
            'score': score,
            'midterm_score': mid,
            'final_score': fin,
            'homework_score': hw,
            'time_minutes': time_minutes,
        }
    return data


def main():
    print('🔍 Loading students from SQL Server...')
    students = load_students_from_sqlserver()
    print(f'Loaded {len(students)} students')

    # Filter target cohorts
    targets = [s for s in students if any(k in (s.get('class') or '') for k in TARGET_COHORT_KEYWORDS)]
    print(f'Found {len(targets)} students in target cohorts')

    to_update = []
    random.seed(42)
    se = SkillEvaluator()

    for s in targets:
        if needs_fill(s):
            # Choose profile base by student's existing csv total_score if present
            csv_total = (s.get('csv_data') or {}).get('total_score') or 0
            profile_base = csv_total if csv_total > 0 else 6.5
            s['courses'] = generate_course_values(profile_base=profile_base)

            # Update csv_data totals
            scores = [c['score'] for c in s['courses'].values()]
            s['csv_data']['total_score'] = round(sum(scores) / len(scores), 2)
            s['csv_data']['midterm_score'] = round(sum(c['midterm_score'] for c in s['courses'].values()) / len(scores), 2)
            s['csv_data']['final_score'] = round(sum(c['final_score'] for c in s['courses'].values()) / len(scores), 2)
            s['csv_data']['homework_score'] = round(sum(c['homework_score'] for c in s['courses'].values()) / len(scores), 2)
            s['csv_data']['attendance_rate'] = s['csv_data'].get('attendance_rate', 0.8) or 0.8

            # Compute skill evaluations
            s['skill_evaluations'] = se.evaluate_all_courses(s)
            to_update.append(s)

    print(f'Will update {len(to_update)} students with generated scores')

    if not to_update:
        print('Nothing to update')
        return

    # Persist to SQL Server
    print('\n📤 Syncing to SQL Server...')
    sync_all_to_sqlserver(to_update, [])

    # Try to sync to Supabase if available
    try:
        from supabase_sync import sync_all_to_supabase
        print('\n📤 Syncing to Supabase...')
        sync_all_to_supabase(to_update, [], [])
    except Exception as e:
        print(f'⚠️ Could not sync to Supabase: {e}')

    print('\n✅ Done')

if __name__ == "__main__":
    main()
