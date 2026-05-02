"""
Lazy Classification - Phân loại khi cần thiết
Tránh phân loại lại toàn bộ mỗi lần khởi động
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from integrated_scoring_system import IntegratedScoringSystem
from sqlserver_sync import save_classification
from supabase_sync import sync_all_to_supabase


def ensure_classifications(data_store):
    """
    Đảm bảo dữ liệu đã được phân loại
    Chỉ phân loại 1 lần, sau đó cache lại
    """
    # Nếu đã có phân loại, return ngay
    if data_store.get('classifications') and len(data_store['classifications']) > 0:
        return data_store['classifications']
    
    print("\n⚡ Đang phân loại sinh viên lần đầu...")
    students = data_store.get('students', [])
    
    if not students:
        return []
    
    # Đánh giá kỹ năng
    print("  📊 Đánh giá kỹ năng...")
    skill_evaluator = SkillEvaluator()
    skill_evaluations = {}
    for student in students:
        evals = skill_evaluator.evaluate_all_courses(student)
        student["skill_evaluations"] = evals
        skill_evaluations[student["student_id"]] = evals
    
    # Phân loại
    print("  🤖 Phân loại K-means + KNN...")
    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    classifier.fit(students)
    classified_students = classifier.predict(students)
    
    # Cache lại
    data_store['classifications'] = classified_students
    data_store['skill_evaluations'] = skill_evaluations
    data_store['classifier'] = classifier

    # Lưu kết quả phân loại vào SQL Server để đảm bảo đồng bộ với DB mới
    saved_count = 0
    for student in classified_students:
        if save_classification(student):
            saved_count += 1

    if saved_count < len(classified_students):
        print(f"  ⚠️ Lưu SQL: {saved_count}/{len(classified_students)} bản ghi")
    else:
        print(f"  ✅ Lưu SQL: {saved_count}/{len(classified_students)} bản ghi")

    # Đồng bộ classifications sang Supabase để giữ dữ liệu ở cả 2 nơi
    try:
        sync_all_to_supabase(students, classified_students, data_store.get('integrated_results', []))
        print("  ✅ Đã đồng bộ classifications lên Supabase")
    except Exception as supabase_error:
        print(f"  ⚠️ Đồng bộ Supabase thất bại: {supabase_error}")
    
    print(f"  ✅ Đã phân loại {len(classified_students)} sinh viên")
    
    return classified_students


def ensure_integrated_scores(data_store):
    """
    Đảm bảo điểm tích hợp đã được tính
    Chỉ tính 1 lần, sau đó cache lại
    """
    # Nếu đã có, return ngay
    if data_store.get('integrated_results') and len(data_store['integrated_results']) > 0:
        return data_store['integrated_results']
    
    print("\n⚡ Đang tính điểm tích hợp lần đầu...")
    
    # Khởi tạo integrated system nếu chưa có hoặc instance cũ không có dữ liệu
    if (
        not data_store.get('integrated_system')
        or len(getattr(data_store.get('integrated_system'), 'students_data', {})) == 0
    ):
        data_store['integrated_system'] = IntegratedScoringSystem(data_store.get('students', []))
    
    # Tính điểm
    integrated_results = data_store['integrated_system'].analyze_all_students()
    
    # Cache lại
    data_store['integrated_results'] = integrated_results
    
    print(f"  ✅ Đã tính điểm tích hợp cho {len(integrated_results)} sinh viên")
    
    return integrated_results


def get_student_classification(data_store, student_id):
    """
    Lấy phân loại của 1 sinh viên cụ thể
    Nếu chưa có, phân loại toàn bộ và cache
    """
    classifications = ensure_classifications(data_store)
    
    for student in classifications:
        if student.get('student_id') == student_id:
            return student
    
    return None


def invalidate_cache(data_store):
    """
    Xóa cache khi có thay đổi dữ liệu
    Buộc phân loại lại lần sau
    """
    data_store['classifications'] = []
    data_store['skill_evaluations'] = {}
    data_store['integrated_results'] = []
    data_store['classifier'] = None
    print("🔄 Đã xóa cache, sẽ phân loại lại lần sau")
