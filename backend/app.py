"""
Flask API Backend - Hệ thống phân loại sinh viên
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from sqlserver_sync import load_students_from_sqlserver, create_tables, test_connection, sync_all_to_sqlserver
from supabase_sync import sync_all_to_supabase
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from integrated_scoring_system import IntegratedScoringSystem
from course_definitions import COURSES, CLASSIFICATION_LEVELS

# Import routes
from routes.students import students_bp, init_data_store as init_students
from routes.statistics import stats_bp, init_data_store as init_stats
from routes.classify import classify_bp, init_data_store as init_classify
from routes.ranking import ranking_bp, init_data_store as init_ranking
from routes.lazy_classifier import ensure_classifications, ensure_integrated_scores

load_dotenv()

app = Flask(__name__)
CORS(app)

# Shared data store
data_store = {
    'students': [],
    'classifications': [],
    'skill_evaluations': {},
    'integrated_system': None,
    'integrated_results': []
}

# Register blueprints
app.register_blueprint(students_bp, url_prefix='/api')
app.register_blueprint(stats_bp, url_prefix='/api')
app.register_blueprint(classify_bp, url_prefix='/api')
app.register_blueprint(ranking_bp, url_prefix='/api')


# ============== ROUTES ==============

@app.route('/')
def index():
    """Serve frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'database': 'SQL Server',
        'total_students': len(data_store['students'])
    })


@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Lấy danh sách môn học"""
    return jsonify({
        'courses': COURSES,
        'levels': CLASSIFICATION_LEVELS
    })


@app.route('/api/sync-sqlserver', methods=['POST'])
def sync_to_sqlserver():
    """Đồng bộ dữ liệu lên SQL Server"""
    try:
        students = data_store.get('students', [])
        classifications = data_store.get('classifications', [])
        skill_evaluations = data_store.get('skill_evaluations', {})
        integrated_results = data_store.get('integrated_results', [])
        
        # Sync lên SQL Server
        success = sync_all_to_sqlserver(students, classifications)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Đã đồng bộ thành công lên SQL Server',
                'stats': {
                    'students': len(students),
                    'classifications': len(classifications),
                    'skill_evaluations': len(skill_evaluations),
                    'integrated_scores': len(integrated_results),
                    'course_scores': sum(len(s.get('courses', {})) for s in students)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Lỗi khi đồng bộ dữ liệu'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sync-supabase', methods=['POST'])
def sync_to_supabase():
    """Đồng bộ dữ liệu từ SQL Server lên Supabase"""
    try:
        students = data_store.get('students', [])

        # Nếu cache rỗng, nạp lại từ SQL Server
        if not students:
            students = load_students_from_sqlserver()
            data_store['students'] = students

        # Đảm bảo có dữ liệu phân loại
        classifications = ensure_classifications(data_store)

        # Phase 1: Đồng bộ dữ liệu nền trước
        sync_all_to_supabase(students, classifications, [])

        # Phase 2: Tính lại điểm tích hợp sau khi Supabase đã có dữ liệu nền
        data_store['integrated_system'] = None
        data_store['integrated_results'] = []
        integrated_results = ensure_integrated_scores(data_store)

        # Đồng bộ đầy đủ lần cuối (bao gồm integrated_scores)
        stats = sync_all_to_supabase(students, classifications, integrated_results)

        return jsonify({
            'success': True,
            'message': 'Đã đồng bộ thành công từ SQL Server lên Supabase',
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============== INIT ==============

def init_data():
    """Khởi tạo dữ liệu từ SQL Server - CHỈ LOAD, KHÔNG PHÂN LOẠI"""
    global data_store
    
    print("=" * 60)
    print("🎓 BACKEND API - SQL Server Database")
    print("=" * 60)
    
    if not test_connection():
        print("❌ Không thể kết nối SQL Server!")
        return
    
    create_tables()
    
    # Load từ SQL Server
    students = load_students_from_sqlserver()
    
    if not students:
        print("⚠️ Không có dữ liệu trong SQL Server")
        return
    
    print(f"✅ Đã tải {len(students)} sinh viên từ SQL Server")
    
    # CHỈ LƯU DỮ LIỆU, KHÔNG PHÂN LOẠI NGAY
    # Phân loại sẽ được thực hiện lazy (khi cần thiết)
    data_store['students'] = students
    data_store['classifications'] = []
    data_store['skill_evaluations'] = {}
    data_store['integrated_results'] = []
    data_store['integrated_system'] = None
    data_store['classifier'] = None  # Lưu classifier để tái sử dụng
    
    # Init routes với data store
    init_students(data_store)
    init_stats(data_store)
    init_classify(data_store)
    init_ranking(data_store)
    
    print(f"✅ Sẵn sàng phục vụ {len(students)} sinh viên")
    print("⚡ Phân loại sẽ được thực hiện khi cần (lazy loading)")
    print("=" * 60)
    print("🌐 API Endpoints:")
    print("  GET  /                    - Frontend")
    print("  GET  /api/health          - Health check")
    print("  GET  /api/students        - Danh sách sinh viên")
    print("  GET  /api/student/<id>    - Chi tiết sinh viên")
    print("  GET  /api/statistics      - Thống kê")
    print("  POST /api/classify        - Phân loại lại")
    print("  POST /api/sync-supabase   - Đồng bộ SQL Server -> Supabase")
    print("  GET  /api/courses         - Danh sách môn học")
    print("  GET  /api/top-students    - Top sinh viên xuất sắc")
    print("  GET  /api/course-statistics - Thống kê theo môn")
    print("  GET  /api/skill-ranking   - Xếp hạng theo kỹ năng")
    print("  GET  /api/class-comparison - So sánh giữa các lớp")
    print("=" * 60)


if __name__ == '__main__':
    init_data()
    app.run(debug=False, host='0.0.0.0', port=5000)
