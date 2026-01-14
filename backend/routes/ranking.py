"""
API Routes - Ranking & Statistics by Course
"""

from flask import Blueprint, jsonify, request

ranking_bp = Blueprint('ranking', __name__)

data_store = {}

def init_data_store(store):
    global data_store
    data_store = store


@ranking_bp.route('/top-students', methods=['GET'])
def get_top_students():
    """Lấy top sinh viên xuất sắc nhất"""
    limit = request.args.get('limit', 10, type=int)
    course = request.args.get('course', '')  # Lọc theo môn
    skill = request.args.get('skill', '')    # Lọc theo kỹ năng
    
    classifications = data_store.get('classifications', [])
    integrated_dict = {r['student_id']: r for r in data_store.get('integrated_results', [])}
    
    # Tính điểm tổng hợp cho mỗi sinh viên
    students_with_scores = []
    
    for student in classifications:
        student_id = student.get('student_id')
        courses = student.get('courses', {})
        
        if not courses:
            continue
        
        # Tính điểm trung bình
        if course and course in courses:
            avg_score = courses[course].get('score', 0)
        else:
            scores = [c.get('score', 0) for c in courses.values()]
            avg_score = sum(scores) / len(scores) if scores else 0
        
        # Lấy điểm tích hợp
        integrated_score = avg_score
        if student_id in integrated_dict:
            integrated_score = integrated_dict[student_id].get('integrated_score', avg_score)
        
        # Tính tổng thời gian học
        total_time = sum(c.get('time_minutes', 0) for c in courses.values())
        
        # Lấy thông tin hành vi
        csv_data = student.get('csv_data', {})
        attendance = csv_data.get('attendance_rate', 0)
        if isinstance(attendance, (int, float)) and attendance <= 1:
            attendance = attendance * 100
        
        students_with_scores.append({
            'student_id': student_id,
            'name': student.get('name', 'N/A'),
            'class': student.get('class') or csv_data.get('class', 'N/A'),
            'avg_score': round(avg_score, 2),
            'integrated_score': round(integrated_score, 2),
            'final_level': student.get('final_level', 'N/A'),
            'total_time_hours': round(total_time / 60, 1),
            'attendance': round(attendance, 1),
            'anomaly_detected': student.get('anomaly_detected', False)
        })
    
    # Sắp xếp theo điểm tích hợp giảm dần
    students_with_scores.sort(key=lambda x: x['integrated_score'], reverse=True)
    
    # Lấy top N (loại bỏ sinh viên bất thường nếu cần)
    top_students = [s for s in students_with_scores if not s['anomaly_detected']][:limit]
    
    return jsonify({
        'top_students': top_students,
        'total': len(top_students),
        'filter': {
            'course': course,
            'skill': skill,
            'limit': limit
        }
    })


@ranking_bp.route('/course-statistics', methods=['GET'])
def get_course_statistics():
    """Thống kê số lượng sinh viên theo từng môn và mức điểm"""
    classifications = data_store.get('classifications', [])
    
    # Định nghĩa các môn học
    course_names = [
        'Nhập Môn Lập Trình',
        'Kĩ Thuật Lập Trình',
        'Cấu trúc Dữ Liệu và Giải Thuật',
        'Lập Trình Hướng Đối Tượng'
    ]
    
    # Khởi tạo thống kê
    stats = {}
    for course in course_names:
        stats[course] = {
            'total_students': 0,
            'avg_score': 0,
            'scores': [],
            'levels': {
                'Xuất sắc (≥8.5)': 0,
                'Khá (7.0-8.4)': 0,
                'Trung bình (5.0-6.9)': 0,
                'Yếu (<5.0)': 0
            },
            'time_stats': {
                'avg_time_minutes': 0,
                'total_time': 0
            }
        }
    
    # Tính toán thống kê
    for student in classifications:
        courses = student.get('courses', {})
        
        for course_name, course_data in courses.items():
            if course_name not in stats:
                continue
                
            score = course_data.get('score', 0)
            time_minutes = course_data.get('time_minutes', 0)
            
            stats[course_name]['total_students'] += 1
            stats[course_name]['scores'].append(score)
            stats[course_name]['time_stats']['total_time'] += time_minutes
            
            # Phân loại theo điểm
            if score >= 8.5:
                stats[course_name]['levels']['Xuất sắc (≥8.5)'] += 1
            elif score >= 7.0:
                stats[course_name]['levels']['Khá (7.0-8.4)'] += 1
            elif score >= 5.0:
                stats[course_name]['levels']['Trung bình (5.0-6.9)'] += 1
            else:
                stats[course_name]['levels']['Yếu (<5.0)'] += 1
    
    # Tính trung bình
    for course_name in stats:
        scores = stats[course_name]['scores']
        total = stats[course_name]['total_students']
        
        if scores:
            stats[course_name]['avg_score'] = round(sum(scores) / len(scores), 2)
            stats[course_name]['min_score'] = round(min(scores), 2)
            stats[course_name]['max_score'] = round(max(scores), 2)
        
        if total > 0:
            stats[course_name]['time_stats']['avg_time_minutes'] = round(
                stats[course_name]['time_stats']['total_time'] / total, 1
            )
        
        # Xóa danh sách scores để response gọn hơn
        del stats[course_name]['scores']
    
    return jsonify({
        'course_statistics': stats,
        'total_courses': len(stats)
    })


@ranking_bp.route('/skill-ranking', methods=['GET'])
def get_skill_ranking():
    """Xếp hạng sinh viên theo kỹ năng cụ thể"""
    skill_name = request.args.get('skill', '')
    course_name = request.args.get('course', '')
    limit = request.args.get('limit', 20, type=int)
    
    skill_evaluations = data_store.get('skill_evaluations', {})
    classifications = data_store.get('classifications', [])
    
    # Tạo dict để tra cứu nhanh
    student_dict = {s['student_id']: s for s in classifications}
    
    skill_scores = []
    
    for student_id, evaluations in skill_evaluations.items():
        student_id = int(student_id)
        student = student_dict.get(student_id, {})
        
        if not student:
            continue
        
        # Lọc theo môn nếu có
        for course, skills in evaluations.items():
            if course_name and course != course_name:
                continue
            
            for skill, skill_data in skills.items():
                if skill_name and skill != skill_name:
                    continue
                
                score = skill_data.get('score', 0)
                level = skill_data.get('level', 'N/A')
                
                skill_scores.append({
                    'student_id': student_id,
                    'name': student.get('name', 'N/A'),
                    'class': student.get('class') or student.get('csv_data', {}).get('class', 'N/A'),
                    'course': course,
                    'skill': skill,
                    'score': round(score, 2),
                    'level': level
                })
    
    # Sắp xếp theo điểm giảm dần
    skill_scores.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'skill_ranking': skill_scores[:limit],
        'total': len(skill_scores),
        'filter': {
            'skill': skill_name,
            'course': course_name,
            'limit': limit
        }
    })


@ranking_bp.route('/class-comparison', methods=['GET'])
def get_class_comparison():
    """So sánh điểm trung bình giữa các lớp"""
    classifications = data_store.get('classifications', [])
    
    class_stats = {}
    
    for student in classifications:
        class_name = student.get('class') or student.get('csv_data', {}).get('class', 'Unknown')
        courses = student.get('courses', {})
        
        if not courses:
            continue
        
        # Tính điểm trung bình của sinh viên
        scores = [c.get('score', 0) for c in courses.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if class_name not in class_stats:
            class_stats[class_name] = {
                'total_students': 0,
                'scores': [],
                'levels': {'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0}
            }
        
        class_stats[class_name]['total_students'] += 1
        class_stats[class_name]['scores'].append(avg_score)
        
        level = student.get('final_level', 'Unknown')
        if level in class_stats[class_name]['levels']:
            class_stats[class_name]['levels'][level] += 1
    
    # Tính trung bình và sắp xếp
    result = []
    for class_name, stats in class_stats.items():
        scores = stats['scores']
        result.append({
            'class': class_name,
            'total_students': stats['total_students'],
            'avg_score': round(sum(scores) / len(scores), 2) if scores else 0,
            'min_score': round(min(scores), 2) if scores else 0,
            'max_score': round(max(scores), 2) if scores else 0,
            'levels': stats['levels']
        })
    
    # Sắp xếp theo điểm trung bình giảm dần
    result.sort(key=lambda x: x['avg_score'], reverse=True)
    
    return jsonify({
        'class_comparison': result,
        'total_classes': len(result)
    })
