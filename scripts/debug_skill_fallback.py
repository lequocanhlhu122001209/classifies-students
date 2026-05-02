import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from sqlserver_sync import load_students_from_sqlserver
from skill_evaluator import SkillEvaluator
from student_classifier import StudentClassifier

students = load_students_from_sqlserver()
se = SkillEvaluator()
for s in students:
    s['skill_evaluations'] = se.evaluate_all_courses(s)

clf = StudentClassifier()
clf.fit(students)
classified = clf.predict(students)

student_lookup = {int(s.get('student_id',0)): s for s in students}

empty_count = 0
fallback_has = 0
for row in classified:
    sid = int(row.get('student_id',0))
    skills = row.get('skill_evaluations') or {}
    if not skills:
        empty_count += 1
        if student_lookup.get(sid) and student_lookup[sid].get('skill_evaluations'):
            fallback_has += 1

print('classified_len=', len(classified))
print('students_len=', len(students))
print('empty_skill_in_classified=', empty_count)
print('fallback_has_entries=', fallback_has)
print('expected_total_skill_rows_if_fallback=', len(students)*16)
