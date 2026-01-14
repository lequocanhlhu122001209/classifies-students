"""
Script migrate dữ liệu từ Supabase sang SQL Server
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

# Force load từ Supabase
os.environ['DATABASE_TYPE'] = 'supabase'

from data_generator import StudentDataGenerator
from sqlserver_sync import sync_all_to_sqlserver, create_database, create_tables, save_student

def migrate():
    print("=" * 60)
    print("🔄 MIGRATE DỮ LIỆU TỪ SUPABASE SANG SQL SERVER")
    print("=" * 60)
    
    # 1. Tạo database và bảng
    print("\n[1] Tạo database và bảng trong SQL Server...")
    create_database()
    create_tables()
    
    # 2. Load dữ liệu từ Supabase
    print("\n[2] Load dữ liệu từ Supabase...")
    generator = StudentDataGenerator(seed=42, use_supabase=True)
    
    # Force load từ Supabase
    students = generator._load_from_supabase()
    print(f"   ✅ Đã load {len(students)} sinh viên từ Supabase")
    
    # 3. Lưu vào SQL Server
    print("\n[3] Lưu vào SQL Server...")
    success = 0
    for i, student in enumerate(students):
        if save_student(student):
            success += 1
        if (i + 1) % 50 == 0:
            print(f"   Đã xử lý {i + 1}/{len(students)} sinh viên...")
    
    print(f"\n✅ Hoàn thành! Đã migrate {success}/{len(students)} sinh viên")
    print("=" * 60)

if __name__ == "__main__":
    migrate()
