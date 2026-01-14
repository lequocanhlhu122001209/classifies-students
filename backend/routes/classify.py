"""
API Routes - Classification
"""

from flask import Blueprint, jsonify, request
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sqlserver_sync import load_students_from_sqlserver, save_classification
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator

classify_bp = Blueprint('classify', __name__)

data_store = {}

def init_data_store(store):
    global data_store
    data_store = store


@classify_bp.route('/classify', methods=['POST'])
def classify_students():
    """Phân loại sinh viên"""
    try:
        req_data = request.get_json() or {}
        normalization_method = req_data.get('normalization_method', 'minmax')
        
        if normalization_method not in ['minmax', 'zscore', 'robust']:
            normalization_method = 'minmax'
        
        # Load từ SQL Server
        students = load_students_from_sqlserver()
        
        if not students:
            return jsonify({'success': False, 'error': 'Không có dữ liệu trong SQL Server'}), 500
        
        # Đánh giá kỹ năng
        skill_evaluator = SkillEvaluator()
        skill_evaluations = {}
        
        for student in students:
            evals = skill_evaluator.evaluate_all_courses(student)
            student["skill_evaluations"] = evals
            skill_evaluations[student["student_id"]] = evals
        
        # Phân loại
        classifier = StudentClassifier(n_clusters=4, normalization_method=normalization_method)
        classifier.fit(students)
        classified_students = classifier.predict(students)
        
        # Tính điểm tích hợp
        integrated_system = data_store.get('integrated_system')
        integrated_results = integrated_system.analyze_all_students() if integrated_system else []
        
        # Cập nhật data store
        data_store['students'] = students
        data_store['classifications'] = classified_students
        data_store['skill_evaluations'] = skill_evaluations
        data_store['integrated_results'] = integrated_results
        
        # Lưu vào SQL Server
        for student in classified_students:
            save_classification(student)
        
        # Thống kê
        level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
        anomaly_count = 0
        
        for student in classified_students:
            final_level = student.get("final_level", "Unknown")
            if final_level in level_counts:
                level_counts[final_level] += 1
            if student.get("anomaly_detected", False):
                anomaly_count += 1
        
        return jsonify({
            'success': True,
            'normalization_method': normalization_method,
            'statistics': {
                'total': len(classified_students),
                'level_counts': level_counts,
                'anomaly_count': anomaly_count
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
