"""
Check sample students from Supabase with detailed scores, skills, and classification.
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from supabase_sync import _create_supabase_client

supabase = _create_supabase_client()

# Fetch students from each cohort
cohorts = {'22': [], '23': [], '24': [], '25': []}

# Get all students
students_res = supabase.table('students').select('*').execute()
all_students = students_res.data if hasattr(students_res, 'data') else []

# Group by cohort
for s in all_students:
    class_code = s.get('class') or ''
    for cohort_key in cohorts:
        if cohort_key in class_code:
            cohorts[cohort_key].append(s)
            break

print(f"Loaded {len(all_students)} students from Supabase\n")

# Sample a few students from each cohort and show their details
for cohort_key in sorted(cohorts.keys()):
    cohort_students = cohorts[cohort_key]
    print(f"{'='*80}")
    print(f"COHORT {cohort_key}: {len(cohort_students)} students")
    print(f"{'='*80}")
    
    samples_shown = 0
    for s in cohort_students:
        if samples_shown >= 2:
            break
        
        sid = s.get('student_id')
        
        # Get course_scores
        courses_res = supabase.table('course_scores').select('*').eq('student_id', sid).execute()
        courses = courses_res.data if hasattr(courses_res, 'data') else []
        
        # Skip if no course scores
        if not courses:
            continue
        
        # Get skill_evaluations (first 3)
        skills_res = supabase.table('skill_evaluations').select('*').eq('student_id', sid).limit(3).execute()
        skills = skills_res.data if hasattr(skills_res, 'data') else []
        
        # Get classification
        class_res = supabase.table('classifications').select('*').eq('student_id', sid).execute()
        classification = (class_res.data[0] if hasattr(class_res, 'data') and class_res.data else {})
        
        print(f"\nStudent ID: {sid} (Class: {s.get('class')})")
        print(f"Final Level: {classification.get('final_level', 'N/A')}")
        print(f"Anomaly: {classification.get('anomaly_detected', False)}")
        
        # Show courses
        print(f"\nCourse Scores ({len(courses)} total):")
        for c in courses[:4]:
            score = c.get('score', 0)
            time_mins = c.get('time_minutes', 0)
            course_code = c.get('course_code', 'N/A')
            print(f"  {course_code}: {score:.2f}/10 ({time_mins:.0f} min)")
        
        # Show skills
        if skills:
            print(f"\nSkill Evaluations (showing {len(skills)}):")
            for skill in skills:
                course = skill.get('course_code', 'N/A')
                skill_code = skill.get('skill_code', 'N/A')
                score = skill.get('score', 0)
                level = skill.get('level', 'N/A')
                print(f"  {course}/{skill_code}: {score:.2f} ({level})")
        
        samples_shown += 1
    
    if samples_shown == 0:
        print("  (No students with course scores)")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
for cohort_key in sorted(cohorts.keys()):
    count = len(cohorts[cohort_key])
    print(f"Cohort {cohort_key}: {count} students")
