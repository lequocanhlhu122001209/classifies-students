"""
Script xem dữ liệu từ Supabase
"""
from supabase import create_client
from collections import Counter

SUPABASE_URL = 'https://odmtndvllclmrwczcyvs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 50)
print("DỮ LIỆU SUPABASE")
print("=" * 50)

# Students
students = supabase.table('students').select('*', count='exact').limit(10).execute()
print(f"\n📚 STUDENTS: {students.count} tổng")
print("10 sinh viên đầu tiên:")
for s in students.data:
    print(f"  {s['student_id']} - {s['name']} - {s['class']}")

# Classifications
classifications = supabase.table('classifications').select('final_level, anomaly_detected', count='exact').execute()
print(f"\n📊 CLASSIFICATIONS: {classifications.count} tổng")
levels = Counter([x['final_level'] for x in classifications.data])
anomalies = sum(1 for x in classifications.data if x['anomaly_detected'])
print("Phân loại:")
for level, count in sorted(levels.items()):
    print(f"  {level}: {count}")
print(f"  Bất thường: {anomalies}")

# Course scores
scores = supabase.table('course_scores').select('*', count='exact').limit(1).execute()
print(f"\n📝 COURSE_SCORES: {scores.count} tổng")

# Skill evaluations
skills = supabase.table('skill_evaluations').select('*', count='exact').limit(1).execute()
print(f"\n🎯 SKILL_EVALUATIONS: {skills.count} tổng")

print("\n" + "=" * 50)
