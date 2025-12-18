"""
Flask web application để hiển thị kết quả phân loại sinh viên
Tự động lưu dữ liệu lên Supabase khi khởi động
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from skill_based_classifier import SkillBasedClassifier, COURSE_SKILLS
from integrated_scoring_system import IntegratedScoringSystem
from course_definitions import COURSES, CLASSIFICATION_LEVELS
import base64
import re
import sys

# Load environment variables from .env
load_dotenv()

# Supabase integration
try:
    from supabase import create_client, Client
    SUPABASE_ENABLED = True
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://odmtndvllclmrwczcyvs.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        SUPABASE_ENABLED = False
        print("⚠️  SUPABASE_URL hoặc SUPABASE_KEY chưa được cấu hình trong .env")
except ImportError:
    SUPABASE_ENABLED = False
    print("⚠️  Supabase không được cài đặt. Chạy: pip install supabase")

# Ensure stdout/stderr use UTF-8 on Windows consoles so unicode prints (emoji) don't raise
try:
    # Python 3.7+: reconfigure will change the encoding of the text stream
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    # If reconfigure isn't available or fails, fall back silently
    pass

app = Flask(__name__)
CORS(app)

# Lưu trữ dữ liệu hiện tại
current_students = []
current_classifications = []
skill_evaluations_all = {}
skill_based_evaluations = {}  # Danh gia ki nang chi tiet
integrated_system = None  # Hệ thống chấm điểm tích hợp
integrated_results = []  # Kết quả điểm tích hợp

@app.route('/')
def index():
    """Trang chủ với danh sách sinh viên"""
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    """Trả về favicon nhúng (nhỏ, dạng PNG) để tránh 404 trên /favicon.ico"""
    # Một PNG nhỏ (16x16) được nhúng dưới dạng base64 để không cần tệp ngoài
    # 1x1 transparent PNG (valid base64)
    png_base64 = (
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
    )
    return Response(base64.b64decode(png_base64), mimetype='image/png')

@app.route('/api/students', methods=['GET'])
def get_students():
    """API lấy danh sách sinh viên với điểm tích hợp"""
    class_filter = request.args.get('class')

    def _normalize(code):
        if not code:
            return None
        return re.sub(r"\s+", "", str(code)).upper()

    class_filter_norm = _normalize(class_filter)
    
    # Tạo dictionary để tra cứu nhanh
    integrated_dict = {r['student_id']: r for r in integrated_results}
    
    # Kết hợp dữ liệu
    enhanced_students = []
    for student in current_classifications:
        student_id = student.get('student_id')
        
        # Lọc theo lớp nếu có
        if class_filter_norm:
            student_class = student.get('class') or student.get('csv_data', {}).get('class')
            if not student_class or _normalize(student_class) != class_filter_norm:
                continue
        
        # Thêm điểm tích hợp
        if student_id in integrated_dict:
            integrated_data = integrated_dict[student_id]
            student['integrated_score'] = integrated_data['integrated_score']
            student['score_difference'] = integrated_data['score_difference']
            student['integrated_classification'] = integrated_data['classification']
            student['exercise_avg'] = integrated_data['components']['exercise_avg']
            student['total_exercises'] = integrated_data['exercise_data']['total_exercises']
        
        enhanced_students.append(student)

    # Lọc skill_evaluations tương ứng
    filtered_ids = {s.get('student_id') for s in enhanced_students}
    filtered_skill_evals = {k: v for k, v in skill_evaluations_all.items() if int(k) in filtered_ids}

    return jsonify({
        'students': enhanced_students,
        'skill_evaluations': filtered_skill_evals,
        'total': len(enhanced_students)
    })

@app.route('/api/classify', methods=['POST'])
def classify_students():
    """
    API phân loại sinh viên với K-means + KNN và chuẩn hóa dữ liệu
    
    NOTE: KIẾN TRÚC HỆ THỐNG
    ========================
    1. CHUẨN HÓA: MinMax/ZScore/Robust
    2. K-MEANS: Phân cụm không giám sát
    3. KNN: Học từ K-means (có giám sát)
    4. PHÁT HIỆN BẤT THƯỜNG: Gian lận
    5. ĐIỂM TÍCH HỢP: Bài tập + Thi + Hành vi
    """
    global current_students, current_classifications, skill_evaluations_all, integrated_results
    
    try:
        # Lấy tham số từ request
        data = request.get_json() or {}
        normalization_method = data.get('normalization_method', 'minmax')
        
        # Validate phương pháp chuẩn hóa
        if normalization_method not in ['minmax', 'zscore', 'robust']:
            normalization_method = 'minmax'
        
        print(f"📊 Phương pháp chuẩn hóa: {normalization_method.upper()}")
        
        # 1. Đọc tất cả sinh viên từ Supabase
        generator = StudentDataGenerator(seed=42, use_supabase=True)
        students = generator.load_all_students()
        
        # 2. Đánh giá kỹ năng
        skill_evaluator = SkillEvaluator()
        skill_evaluations_all = {}
        
        for student in students:
            skill_evaluations = skill_evaluator.evaluate_all_courses(student)
            student["skill_evaluations"] = skill_evaluations
            skill_evaluations_all[student["student_id"]] = skill_evaluations
        
        # 3. Phân loại với K-means + KNN + Chuẩn hóa
        classifier = StudentClassifier(n_clusters=4, normalization_method=normalization_method)
        classifier.fit(students)
        classified_students = classifier.predict(students)
        
        # 4. Tính điểm tích hợp
        print("📝 Đang tính điểm tích hợp...")
        integrated_results = integrated_system.analyze_all_students()
        
        current_students = students
        current_classifications = classified_students
        
        # Tính toán thống kê
        level_counts = {
            "Xuat sac": 0,
            "Kha": 0,
            "Trung binh": 0,
            "Yeu": 0
        }
        
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
            'students': classified_students,
            'skill_evaluations': skill_evaluations_all,
            'statistics': {
                'total': len(classified_students),
                'level_counts': level_counts,
                'anomaly_count': anomaly_count
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/student/<int:student_id>', methods=['GET'])
def get_student_detail(student_id):
    """API lấy chi tiết sinh viên với điểm tích hợp"""
    student = next((s for s in current_classifications if s.get('student_id') == student_id), None)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    skill_eval = skill_evaluations_all.get(student_id, {})
    
    # Lấy điểm tích hợp
    integrated_data = integrated_system.calculate_integrated_score(student_id)
    
    result = {
        'student': student,
        'skill_evaluations': skill_eval
    }
    
    if integrated_data:
        result['integrated_data'] = integrated_data
    
    return jsonify(result)


@app.route('/student/<int:student_id>')
def student_detail_json(student_id):
    """
    API tra ve thong tin chi tiet sinh vien (JSON)
    Frontend se xu ly hien thi trong modal
    """
    # Tim sinh vien
    student = next((s for s in current_students if s.get('student_id') == student_id), None)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Danh gia ki nang
    classifier = SkillBasedClassifier()
    skill_evaluations = classifier.evaluate_all_courses(student)
    
    # Lay ket qua phan loai
    classified = next((s for s in current_classifications if s.get('student_id') == student_id), None)
    
    result = {
        'student_id': student_id,
        'name': student.get('name'),
        'class': student.get('class'),
        'csv_data': student.get('csv_data', {}),
        'courses': student.get('courses', {}),
        'skill_evaluations': skill_evaluations
    }
    
    if classified:
        result.update({
            'kmeans_prediction': classified.get('kmeans_prediction'),
            'knn_prediction': classified.get('knn_prediction'),
            'final_level': classified.get('final_level'),
            'anomaly_detected': classified.get('anomaly_detected'),
            'anomaly_reason': classified.get('anomaly_reason'),
            'anomaly_reasons': classified.get('anomaly_reasons', [])
        })
    
    return jsonify(result)

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """API lấy danh sách môn học và kỹ năng"""
    return jsonify({
        'courses': COURSES,
        'levels': CLASSIFICATION_LEVELS
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API lấy thống kê với điểm tích hợp"""
    if not current_classifications:
        return jsonify({'error': 'No data available'}), 404
    
    class_filter = request.args.get('class')

    def _normalize(code):
        if not code:
            return None
        return re.sub(r"\s+", "", str(code)).upper()

    class_filter_norm = _normalize(class_filter)
    
    level_counts = {
        "Xuat sac": 0,
        "Kha": 0,
        "Trung binh": 0,
        "Yeu": 0
    }
    
    integrated_level_counts = {
        "Giỏi": 0,
        "Khá": 0,
        "Trung Bình": 0,
        "Yếu": 0
    }
    
    anomaly_count = 0
    original_scores = []
    integrated_scores = []
    
    integrated_dict = {r['student_id']: r for r in integrated_results}
    
    for student in current_classifications:
        # Lọc theo lớp
        if class_filter_norm:
            student_class = student.get('class') or student.get('csv_data', {}).get('class')
            if not student_class or _normalize(student_class) != class_filter_norm:
                continue

        final_level = student.get("final_level", "Unknown")
        if final_level in level_counts:
            level_counts[final_level] += 1

        if student.get("anomaly_detected", False):
            anomaly_count += 1
        
        # Thống kê điểm tích hợp
        student_id = student.get('student_id')
        if student_id in integrated_dict:
            integrated_data = integrated_dict[student_id]
            integrated_level = integrated_data['classification']
            if integrated_level in integrated_level_counts:
                integrated_level_counts[integrated_level] += 1
            
            original_scores.append(integrated_data['original_score'])
            integrated_scores.append(integrated_data['integrated_score'])
    
    total_count = sum(level_counts.values())
    
    # Tính điểm trung bình
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

@app.route('/api/skill-evaluation/<int:student_id>', methods=['GET'])
def get_skill_evaluation(student_id):
    """
    API lay danh gia ki nang chi tiet cho sinh vien
    """
    # Tim sinh vien
    student = next((s for s in current_students if s.get('student_id') == student_id), None)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Danh gia ki nang
    classifier = SkillBasedClassifier()
    skill_evaluations = classifier.evaluate_all_courses(student)
    
    return jsonify({
        'success': True,
        'student_id': student_id,
        'skill_evaluations': skill_evaluations,
        'course_skills': COURSE_SKILLS
    })


@app.route('/api/all-skills', methods=['GET'])
def get_all_skills():
    """
    API lay danh sach tat ca ki nang
    """
    return jsonify({
        'success': True,
        'course_skills': COURSE_SKILLS
    })


@app.route('/api/sync-supabase', methods=['POST'])
def sync_supabase():
    """
    API để sync dữ liệu lên Supabase từ web
    """
    global current_students, current_classifications, integrated_results
    
    if not SUPABASE_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Supabase không được cài đặt. Chạy: pip install supabase'
        }), 500
    
    try:
        from supabase_sync import sync_to_supabase
        
        # Sync dữ liệu
        success = sync_to_supabase(current_students, current_classifications, integrated_results)
        
        if success:
            # Đếm số bài tập từ CSV
            import os
            exercise_count = 0
            csv_path = 'student_exercises_detailed.csv'
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as f:
                    exercise_count = sum(1 for _ in f) - 1  # Trừ header
            
            return jsonify({
                'success': True,
                'message': 'Đã sync thành công lên Supabase',
                'stats': {
                    'students': len(current_students),
                    'course_scores': len(current_students) * 4,
                    'skill_evaluations': len(current_students) * 16,
                    'classifications': len(current_classifications),
                    'integrated_scores': len(integrated_results),
                    'exercise_details': exercise_count
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Không thể sync lên Supabase'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Tự động phân loại khi khởi động
    print("=" * 80)
    print("🎓 HỆ THỐNG CHẤM ĐIỂM TÍCH HỢP - K-MEANS + KNN + BÀI TẬP")
    print("=" * 80)
    print("\n📊 Khởi tạo hệ thống...")
    
    # Khởi tạo hệ thống tích hợp
    integrated_system = IntegratedScoringSystem()
    
    # Load từ Supabase
    generator = StudentDataGenerator(
        seed=42, 
        use_supabase=True  # Load từ Supabase
    )
    students = generator.load_all_students()
    
    print(f"✅ Đã tải {len(students)} sinh viên")
    
    skill_evaluator = SkillEvaluator()
    skill_evaluations_all = {}
    
    for student in students:
        skill_evaluations = skill_evaluator.evaluate_all_courses(student)
        student["skill_evaluations"] = skill_evaluations
        skill_evaluations_all[student["student_id"]] = skill_evaluations
    
    # Luôn chạy phân loại mới khi khởi động (không dùng dữ liệu cũ từ Supabase)
    print("\n🔧 Đang phân loại sinh viên với thuật toán mới...")
    print("   Phương pháp chuẩn hóa: MINMAX")
    classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
    classifier.fit(students)
    classified_students = classifier.predict(students)
    
    # Tính điểm tích hợp
    print("\n📝 Đang tính điểm tích hợp...")
    integrated_results = integrated_system.analyze_all_students()
    
    current_students = students
    current_classifications = classified_students
    
    # Thống kê
    level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    integrated_level_counts = {"Giỏi": 0, "Khá": 0, "Trung Bình": 0, "Yếu": 0}
    anomaly_count = 0
    
    for student in classified_students:
        level = student.get("final_level", "Unknown")
        if level in level_counts:
            level_counts[level] += 1
        if student.get("anomaly_detected", False):
            anomaly_count += 1
    
    for result in integrated_results:
        level = result['classification']
        if level in integrated_level_counts:
            integrated_level_counts[level] += 1
    
    print("\n📊 Thống kê phân loại gốc:")
    for level, count in level_counts.items():
        pct = (count / len(classified_students)) * 100
        print(f"  • {level:15s}: {count:3d} sinh viên ({pct:5.1f}%)")
    
    print("\n📊 Thống kê phân loại tích hợp:")
    for level, count in integrated_level_counts.items():
        pct = (count / len(integrated_results)) * 100
        print(f"  • {level:15s}: {count:3d} sinh viên ({pct:5.1f}%)")
    
    print(f"\n  • Bất thường    : {anomaly_count:3d} trường hợp")
    
    # Không sync tự động khi khởi động - chỉ sync khi gọi API /api/sync-supabase
    print("\n💡 Để sync dữ liệu lên Supabase, sử dụng nút 'Lưu Dữ Liệu' trên giao diện web")
    
    print("\n" + "=" * 80)
    print("✅ Hệ thống đã sẵn sàng!")
    print("🌐 Mở trình duyệt tại: http://localhost:5000")
    print("\n📝 API Endpoints:")
    print("  • POST /api/classify - Phân loại")
    print("  • GET  /api/students - Danh sách sinh viên (có điểm tích hợp)")
    print("  • GET  /api/student/<id> - Chi tiết sinh viên (có điểm tích hợp)")
    print("  • GET  /api/statistics - Thống kê (có so sánh điểm)")
    print("=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

