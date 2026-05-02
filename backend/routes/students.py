"""
API Routes - Students
"""

from flask import Blueprint, jsonify, request
import re
import sys
import os

# Import lazy classifier
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from lazy_classifier import ensure_classifications, ensure_integrated_scores

students_bp = Blueprint('students', __name__)

# Reference to data (will be set from app.py)
data_store = {}

def init_data_store(store):
    global data_store
    data_store = store

@students_bp.route('/students', methods=['GET'])
def get_students():
    """Lấy danh sách sinh viên - LAZY LOADING"""
    class_filter = request.args.get('class')
    
    # Đảm bảo đã phân loại (lazy)
    classifications = ensure_classifications(data_store)
    integrated_results = ensure_integrated_scores(data_store)
    
    def _normalize(code):
        if not code:
            return None
        return re.sub(r"\s+", "", str(code)).upper()
    
    class_filter_norm = _normalize(class_filter)
    integrated_dict = {r['student_id']: r for r in integrated_results}
    
    enhanced_students = []
    for student in classifications:
        student_id = student.get('student_id')
        
        if class_filter_norm:
            student_class = student.get('class') or student.get('csv_data', {}).get('class')
            if not student_class or _normalize(student_class) != class_filter_norm:
                continue
        
        student_copy = student.copy()
        if student_id in integrated_dict:
            integrated_data = integrated_dict[student_id]
            student_copy['integrated_score'] = integrated_data['integrated_score']
            student_copy['score_difference'] = integrated_data['score_difference']
            student_copy['integrated_classification'] = integrated_data['classification']
            student_copy['exercise_avg'] = integrated_data['components']['exercise_avg']
            student_copy['total_exercises'] = integrated_data['exercise_data']['total_exercises']
        
        enhanced_students.append(student_copy)
    
    filtered_ids = {s.get('student_id') for s in enhanced_students}
    filtered_skill_evals = {k: v for k, v in data_store.get('skill_evaluations', {}).items() if int(k) in filtered_ids}
    
    return jsonify({
        'students': enhanced_students,
        'skill_evaluations': filtered_skill_evals,
        'total': len(enhanced_students)
    })


@students_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_detail(student_id):
    """Lấy chi tiết sinh viên - LAZY LOADING"""
    # Đảm bảo đã phân loại (lazy)
    classifications = ensure_classifications(data_store)
    
    student = next((s for s in classifications if s.get('student_id') == student_id), None)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    skill_eval = data_store.get('skill_evaluations', {}).get(student_id, {})
    
    # Tính điểm tích hợp cho sinh viên này
    integrated_system = data_store.get('integrated_system')
    if not integrated_system:
        from integrated_scoring_system import IntegratedScoringSystem
        integrated_system = IntegratedScoringSystem()
        data_store['integrated_system'] = integrated_system
    
    integrated_data = integrated_system.calculate_integrated_score(student_id)
    
    return jsonify({
        'student': student,
        'skill_evaluations': skill_eval,
        'integrated_data': integrated_data
    })
