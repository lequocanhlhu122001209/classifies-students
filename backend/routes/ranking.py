"""
API Routes - Ranking & Statistics by Course
"""

from flask import Blueprint, jsonify, request

ranking_bp = Blueprint('ranking', __name__)

data_store = {}

def init_data_store(store):
    global data_store
    data_store = store


def get_best_skills(student_id, skill_evaluations, courses):
    """Lấy kỹ năng tốt nhất của sinh viên theo từng môn"""
    student_skills = skill_evaluations.get(str(student_id), {})
    
    best_skills = {}
    course_scores = {}
    
    for course_name, course_data in courses.items():
        course_scores[course_name] = course_data.get('score', 0)
        
        # Lấy kỹ năng của môn này
        course_skills = student_skills.get(course_name, {})
        if course_skills:
            # Tìm kỹ năng có điểm cao nhất
            best_skill = max(course_skills.items(), key=lambda x: x[1].get('score', 0) if isinstance(x[1], dict) else 0)
            skill_name = best_skill[0]
            skill_data = best_skill[1] if isinstance(best_skill[1], dict) else {'score': 0, 'level': 'N/A'}
            best_skills[course_name] = {
                'skill': skill_name,
                'score': round(skill_data.get('score', 0), 1),
                'level': skill_data.get('level', 'N/A')
            }
    
    return best_skills, course_scores


@ranking_bp.route('/top-students', methods=['GET'])
def get_top_students():
    """Lấy top sinh viên xuất sắc nhất dựa trên điểm số + hành vi"""
    limit = request.args.get('limit', 10, type=int)
    course = request.args.get('course', '')  # Lọc theo môn
    class_filter = request.args.get('class', '')  # Lọc theo lớp
    
    classifications = data_store.get('classifications', [])
    integrated_dict = {r['student_id']: r for r in data_store.get('integrated_results', [])}
    skill_evaluations = data_store.get('skill_evaluations', {})
    
    # Tính điểm tổng hợp cho mỗi sinh viên
    students_with_scores = []
    
    for student in classifications:
        student_id = student.get('student_id')
        courses = student.get('courses', {})
        csv_data = student.get('csv_data', {})
        
        if not courses:
            continue
        
        # Lọc theo lớp nếu có
        student_class = student.get('class') or csv_data.get('class', '')
        if class_filter and student_class != class_filter:
            continue
        
        # === TÍNH ĐIỂM SỐ (50%) ===
        # Luôn tính điểm TB tất cả môn (để đồng bộ với chi tiết)
        scores = [c.get('score', 0) for c in courses.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Nếu lọc theo môn, chỉ lọc sinh viên có môn đó (không thay đổi avg_score)
        if course and course not in courses:
            continue
        
        # Điểm số: 0-10 -> 0-50 điểm
        score_points = (avg_score / 10) * 50
        
        # === TÍNH HÀNH VI (50%) ===
        # 1. Tham gia lớp (40 điểm)
        attendance = csv_data.get('attendance_rate', 0)
        if isinstance(attendance, (int, float)) and attendance <= 1:
            attendance = attendance * 100
        attendance_points = (attendance / 100) * 40
        
        # 2. Nộp bài đúng hạn (30 điểm) - Ít nộp trễ = điểm cao
        late_submissions = int(csv_data.get('late_submissions', 0))
        # Giả sử tối đa 30 bài/môn * 4 môn = 120 bài
        total_assignments = len(courses) * 30
        on_time_rate = max(0, (total_assignments - late_submissions) / total_assignments) if total_assignments > 0 else 1
        ontime_points = on_time_rate * 30
        
        # 3. Thời gian học (30 điểm) - Thời gian hợp lý = điểm cao
        total_time = sum(c.get('time_minutes', 0) for c in courses.values())
        time_hours = total_time / 60
        # Thời gian lý tưởng: 10-20h, quá ít hoặc quá nhiều đều bị trừ
        if time_hours >= 10 and time_hours <= 25:
            time_points = 30  # Tối đa
        elif time_hours >= 5:
            time_points = 20
        elif time_hours >= 2:
            time_points = 10
        else:
            time_points = 5  # Quá ít
        
        # === TỔNG ĐIỂM XẾP HẠNG (thang 100) ===
        # Điểm số: 50% (0-50 điểm) + Hành vi: 50% (0-50 điểm từ 100 chia 2)
        behavior_score = attendance_points + ontime_points + time_points  # Max 100
        ranking_score = score_points + (behavior_score / 2)  # Max 50 + 50 = 100
        
        # === XẾP LOẠI THEO ĐIỂM HỌC (không phụ thuộc hành vi) ===
        # Điểm < 5 = Yếu, 5-6.99 = Trung bình, 7-7.99 = Khá, >= 8 = Xuất sắc
        if avg_score < 5.0:
            final_level = 'Yeu'
        elif avg_score < 7.0:
            final_level = 'Trung binh'
        elif avg_score < 8.0:
            final_level = 'Kha'
        else:
            final_level = 'Xuat sac'
        
        # Lấy kỹ năng tốt nhất
        best_skills, course_scores = get_best_skills(student_id, skill_evaluations, courses)
        
        students_with_scores.append({
            'student_id': student_id,
            'name': student.get('name', 'N/A'),
            'class': student_class or 'N/A',
            'avg_score': round(avg_score, 2),
            'ranking_score': round(ranking_score, 1),
            'score_points': round(score_points, 1),
            'attendance': round(attendance, 1),
            'attendance_points': round(attendance_points, 1),
            'late_submissions': late_submissions,
            'ontime_points': round(ontime_points, 1),
            'total_time_hours': round(time_hours, 1),
            'time_points': round(time_points, 1),
            'behavior_score': round(behavior_score, 1),  # Điểm hành vi tổng hợp (max 100)
            'final_level': final_level,  # Xếp loại theo điểm học
            'anomaly_detected': student.get('anomaly_detected', False),
            'best_skills': best_skills,
            'course_scores': course_scores
        })
    
    # Sắp xếp theo điểm xếp hạng (điểm số + hành vi) giảm dần
    students_with_scores.sort(key=lambda x: x['ranking_score'], reverse=True)
    
    # Lấy top N (loại bỏ sinh viên bất thường)
    top_students = [s for s in students_with_scores if not s['anomaly_detected']][:limit]
    
    return jsonify({
        'top_students': top_students,
        'total': len(top_students),
        'filter': {
            'course': course,
            'class': class_filter,
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
