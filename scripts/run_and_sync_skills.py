#!/usr/bin/env python3
import sys
import json
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sqlserver_sync import load_students_from_sqlserver
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from integrated_scoring_system import IntegratedScoringSystem
from supabase_sync import sync_all_to_supabase


def main():
    students = load_students_from_sqlserver()
    print(f"Loaded students: {len(students)}")

    skill_evaluator = SkillEvaluator()
    for s in students:
        s['skill_evaluations'] = skill_evaluator.evaluate_all_courses(s)

    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    classifier.fit(students)
    classified_students = classifier.predict(students)

    integrated_system = IntegratedScoringSystem()
    integrated_results = integrated_system.analyze_all_students()

    stats = sync_all_to_supabase(students, classified_students, integrated_results)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
