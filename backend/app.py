"""
Flask API backend for student classification.
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from sqlserver_sync import load_students_from_sqlserver, create_tables, test_connection, sync_all_to_sqlserver
from supabase_sync import sync_all_to_supabase, load_students_from_supabase
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator
from integrated_scoring_system import IntegratedScoringSystem
from course_definitions import COURSES, CLASSIFICATION_LEVELS

from routes.students import students_bp, init_data_store as init_students
from routes.statistics import stats_bp, init_data_store as init_stats
from routes.classify import classify_bp, init_data_store as init_classify
from routes.ranking import ranking_bp, init_data_store as init_ranking
from routes.lazy_classifier import ensure_classifications, ensure_integrated_scores

load_dotenv()

app = Flask(__name__)
CORS(app)

data_store = {
    'students': [],
    'classifications': [],
    'skill_evaluations': {},
    'integrated_system': None,
    'integrated_results': []
}

app.register_blueprint(students_bp, url_prefix='/api')
app.register_blueprint(stats_bp, url_prefix='/api')
app.register_blueprint(classify_bp, url_prefix='/api')
app.register_blueprint(ranking_bp, url_prefix='/api')


@app.route('/')
def index():
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'database': 'SQL Server',
        'total_students': len(data_store['students'])
    })


@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify({
        'courses': COURSES,
        'levels': CLASSIFICATION_LEVELS
    })


@app.route('/api/sync-sqlserver', methods=['POST'])
def sync_to_sqlserver():
    """Load from Supabase, classify, then persist into SQL Server."""
    try:
        students = load_students_from_supabase()
        if not students:
            return jsonify({
                'success': False,
                'error': 'Khong co du lieu sinh vien trong Supabase'
            }), 404

        skill_evaluator = SkillEvaluator()
        skill_evaluations = {}
        for student in students:
            evals = skill_evaluator.evaluate_all_courses(student)
            student['skill_evaluations'] = evals
            skill_evaluations[student['student_id']] = evals

        classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
        classifier.fit(students)
        classifications = classifier.predict(students)

        integrated_system = IntegratedScoringSystem(students)
        integrated_results = integrated_system.analyze_all_students()

        success = sync_all_to_sqlserver(students, classifications)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Loi khi dong bo du lieu xuong SQL Server'
            }), 500

        data_store['students'] = students
        data_store['classifications'] = classifications
        data_store['skill_evaluations'] = skill_evaluations
        data_store['integrated_system'] = integrated_system
        data_store['integrated_results'] = integrated_results
        data_store['classifier'] = classifier

        return jsonify({
            'success': True,
            'message': 'Da dong bo thanh cong tu Supabase xuong SQL Server',
            'stats': {
                'students': len(students),
                'classifications': len(classifications),
                'skill_evaluations': len(skill_evaluations),
                'integrated_scores': len(integrated_results),
                'course_scores': sum(len(s.get('courses', {})) for s in students),
                'anomalies': sum(1 for s in classifications if s.get('anomaly_detected'))
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sync-supabase', methods=['POST'])
def sync_to_supabase():
    """Sync data from SQL Server to Supabase."""
    try:
        students = data_store.get('students', [])
        if not students:
            students = load_students_from_sqlserver()
            data_store['students'] = students

        classifications = ensure_classifications(data_store)

        sync_all_to_supabase(students, classifications, [])

        data_store['integrated_system'] = None
        data_store['integrated_results'] = []
        integrated_results = ensure_integrated_scores(data_store)

        stats = sync_all_to_supabase(students, classifications, integrated_results)

        return jsonify({
            'success': True,
            'message': 'Da dong bo thanh cong tu SQL Server len Supabase',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def init_data():
    global data_store

    print("=" * 60)
    print("BACKEND API - SQL Server Database")
    print("=" * 60)

    students = []
    data_source = "SQL Server"

    if test_connection():
        create_tables()
        students = load_students_from_sqlserver()
        if students:
            print(f"Da tai {len(students)} sinh vien tu SQL Server")
    else:
        print("Khong the ket noi SQL Server, thu fallback sang Supabase")

    if not students:
        students = load_students_from_supabase()
        data_source = "Supabase"
        if students:
            print(f"Da tai {len(students)} sinh vien tu Supabase")

    if not students:
        print("Khong co du lieu trong SQL Server hoac Supabase")
        return

    data_store['students'] = students
    data_store['classifications'] = []
    data_store['skill_evaluations'] = {}
    data_store['integrated_results'] = []
    data_store['integrated_system'] = None
    data_store['classifier'] = None
    data_store['data_source'] = data_source

    init_students(data_store)
    init_stats(data_store)
    init_classify(data_store)
    init_ranking(data_store)

    print(f"San sang phuc vu {len(students)} sinh vien tu {data_source}")
    print("Phan loai se duoc thuc hien khi can")


if __name__ == '__main__':
    init_data()
    app.run(debug=False, host='0.0.0.0', port=5000)
