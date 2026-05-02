"""
Verify Supabase table counts and sample rows.
"""
import json
import sys
import os

# Ensure project root is on sys.path so `src` is importable when running from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.supabase_sync import _create_supabase_client

supabase = _create_supabase_client()

TABLES = [
    "students",
    "student_csv_data",
    "course_scores",
    "skill_evaluations",
    "classifications",
    "integrated_scores",
]

results = {}

for t in TABLES:
    try:
        count_res = supabase.table(t).select('student_id', count='exact').execute()
        total = getattr(count_res, 'count', None)
    except Exception:
        total = None

    try:
        sample_res = supabase.table(t).select('*').limit(5).execute()
        sample = sample_res.data if hasattr(sample_res, 'data') else None
    except Exception:
        sample = None

    results[t] = {"count": total, "sample": sample}

# Check skill_evaluations for null/empty course_code
try:
    skill_rows = supabase.table('skill_evaluations').select('student_id,course_code,skill_code,score').limit(20000).execute()
    skill_data = skill_rows.data if hasattr(skill_rows, 'data') else []
    null_course = [r for r in (skill_data or []) if not r.get('course_code')]
    results['skill_evaluations']['fetched_rows'] = len(skill_data)
    results['skill_evaluations']['null_course_code_count'] = len(null_course)
    results['skill_evaluations']['null_course_sample'] = null_course[:5]
except Exception as exc:
    results['skill_evaluations']['error'] = str(exc)

print(json.dumps(results, ensure_ascii=False, indent=2))
