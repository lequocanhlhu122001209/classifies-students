"""
Dọn dẹp và chuẩn hóa classifications
"""
from supabase import create_client

SUPABASE_URL = 'https://odmtndvllclmrwczcyvs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    print("Đang xóa tất cả classifications...")
    
    # Lấy tất cả student_id
    students = supabase.table('students').select('student_id').execute().data
    student_ids = [s['student_id'] for s in students]
    
    # Xóa tất cả
    for sid in student_ids:
        supabase.table('classifications').delete().eq('student_id', sid).execute()
    
    # Xóa thêm các bản ghi còn sót
    remaining = supabase.table('classifications').select('id').execute().data
    for r in remaining:
        supabase.table('classifications').delete().eq('id', r['id']).execute()
    
    print(f"✅ Đã xóa tất cả classifications")
    
    # Verify
    count = supabase.table('classifications').select('id', count='exact').execute()
    print(f"Còn lại: {count.count}")

if __name__ == '__main__':
    main()
