"""
Xem danh sách sinh viên xuất sắc và bất thường
"""
from supabase import create_client

SUPABASE_URL = 'https://odmtndvllclmrwczcyvs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lấy tất cả students
students = {s['student_id']: s for s in supabase.table('students').select('*').execute().data}

# Lấy classifications
classifications = supabase.table('classifications').select('*').execute().data

print("=" * 60)
print("SINH VIÊN XUẤT SẮC")
print("=" * 60)
excellent = [c for c in classifications if c['final_level'] == 'Xuất sắc']
for c in excellent:
    s = students.get(c['student_id'], {})
    print(f"  {c['student_id']} - {s.get('name', 'N/A')} - {s.get('class', 'N/A')}")
print(f"Tổng: {len(excellent)}")

print("\n" + "=" * 60)
print("SINH VIÊN BẤT THƯỜNG")
print("=" * 60)
anomalies = [c for c in classifications if c['anomaly_detected']]
for c in anomalies:
    s = students.get(c['student_id'], {})
    print(f"  {c['student_id']} - {s.get('name', 'N/A')} - Level: {c['final_level']}")
print(f"Tổng: {len(anomalies)}")
