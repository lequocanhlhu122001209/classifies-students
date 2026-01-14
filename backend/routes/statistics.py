"""
API Routes - Statistics
"""

from flask import Blueprint, jsonify, request
import re

stats_bp = Blueprint('statistics', __name__)

data_store = {}

def init_data_store(store):
    global data_store
    data_store = store


@stats_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Lấy thống kê"""
    classifications = data_store.get('classifications', [])
    if not classifications:
        return jsonify({'error': 'No data available'}), 404
    
    class_filter = request.args.get('class')
    
    def _normalize(code):
        if not code:
            return None
        return re.sub(r"\s+", "", str(code)).upper()
    
    class_filter_norm = _normalize(class_filter)
    
    level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    integrated_level_counts = {"Giỏi": 0, "Khá": 0, "Trung Bình": 0, "Yếu": 0}
    anomaly_count = 0
    original_scores = []
    integrated_scores = []
    
    integrated_dict = {r['student_id']: r for r in data_store.get('integrated_results', [])}
    
    for student in classifications:
        if class_filter_norm:
            student_class = student.get('class') or student.get('csv_data', {}).get('class')
            if not student_class or _normalize(student_class) != class_filter_norm:
                continue
        
        final_level = student.get("final_level", "Unknown")
        if final_level in level_counts:
            level_counts[final_level] += 1
        
        if student.get("anomaly_detected", False):
            anomaly_count += 1
        
        student_id = student.get('student_id')
        if student_id in integrated_dict:
            integrated_data = integrated_dict[student_id]
            integrated_level = integrated_data['classification']
            if integrated_level in integrated_level_counts:
                integrated_level_counts[integrated_level] += 1
            original_scores.append(integrated_data['original_score'])
            integrated_scores.append(integrated_data['integrated_score'])
    
    total_count = sum(level_counts.values())
    avg_original = sum(original_scores) / len(original_scores) if original_scores else 0
    avg_integrated = sum(integrated_scores) / len(integrated_scores) if integrated_scores else 0
    
    return jsonify({
        'level_counts': level_counts,
        'integrated_level_counts': integrated_level_counts,
        'anomaly_count': anomaly_count,
        'total_students': total_count,
        'score_statistics': {
            'avg_original_score': round(avg_original, 2),
            'avg_integrated_score': round(avg_integrated, 2),
            'score_difference': round(avg_integrated - avg_original, 2)
        }
    })
