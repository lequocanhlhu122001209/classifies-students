"""
Check sample students from cohorts 22/23/24/25 with detailed scores and skill evaluations.
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sqlserver_sync import load_students_from_sqlserver
from skill_evaluator import SkillEvaluator
from student_classifier import StudentClassifier

students = load_students_from_sqlserver()
se = SkillEvaluator()

# Compute skill_evaluations for all students
for s in students:
    s['skill_evaluations'] = se.evaluate_all_courses(s)

# Classify students
clf = StudentClassifier()
clf.fit(students)
classified = clf.predict(students)
classified_by_id = {int(c.get('student_id', 0)): c for c in classified}

# Group by cohort
cohorts = {'22': [], '23': [], '24': [], '25': []}
for s in students:
    class_code = s.get('class') or ''
    for cohort_key in cohorts:
        if cohort_key in class_code:
            cohorts[cohort_key].append(s)
            break

# Print samples from each cohort
for cohort_key in sorted(cohorts.keys()):
    cohort_students = cohorts[cohort_key]
    print(f"\n{'='*80}")
    print(f"COHORT {cohort_key}: {len(cohort_students)} students")
    print(f"{'='*80}")
    
    # Pick first 1-2 with sufficient data
    samples_shown = 0
    for s in cohort_students:
        if samples_shown >= 2:
            break
        sid = int(s.get('student_id', 0))
        courses = s.get('courses', {})
        has_scores = any(float(c.get('score', 0) or 0) > 0 for c in courses.values())
        if not has_scores:
            continue
        
        classified_entry = classified_by_id.get(sid) or {}
        
        print(f"\nStudent ID: {sid} ({s.get('name', 'N/A')}, Class: {s.get('class')})")
        print(f"Final Level: {classified_entry.get('final_level', 'N/A')}")
        print(f"Anomaly: {classified_entry.get('anomaly_detected', False)}")
        
        # Courses
        print(f"\nCourse Scores:")
        for course_name, course_data in sorted(courses.items()):
            score = float(course_data.get('score', 0) or 0)
            time_mins = float(course_data.get('time_minutes', 0) or 0)
            print(f"  {course_name}: {score:.2f}/10 ({time_mins:.0f} min)")
        
        # Skills
        skills = s.get('skill_evaluations', {})
        if skills:
            print(f"\nSkill Evaluations (sample):")
            for course_name in list(skills.keys())[:1]:
                course_skills = skills.get(course_name, {}).get('skills', {})
                print(f"  {course_name}:")
                for skill_name in list(course_skills.keys())[:2]:
                    skill_info = course_skills[skill_name]
                    print(f"    {skill_name}: {skill_info.get('score', 0):.2f} ({skill_info.get('level', 'N/A')})")
        
        samples_shown += 1
    
    if samples_shown == 0:
        print("  (No students with sufficient course score data)")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
for cohort_key in sorted(cohorts.keys()):
    count = len(cohorts[cohort_key])
    print(f"Cohort {cohort_key}: {count} students")
