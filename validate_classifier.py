"""
Hệ thống kiểm tra độ chính xác của thuật toán phân loại sinh viên
Sử dụng K-means + KNN + Phát hiện bất thường
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from datetime import datetime
import json
import os

from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier
from skill_evaluator import SkillEvaluator


class ClassifierValidator:
    """Kiểm tra độ chính xác của hệ thống phân loại sinh viên"""
    
    def __init__(self):
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_data(self):
        """Load dữ liệu sinh viên từ Supabase"""
        print("📊 Đang tải dữ liệu từ Supabase...")
        generator = StudentDataGenerator(
            seed=42, 
            use_supabase=True  # Dùng Supabase
        )
        students = generator.load_all_students()
        print(f"   ✅ Đã tải {len(students)} sinh viên từ Supabase")
        return students
    
    def evaluate_skills(self, students):
        """Đánh giá kỹ năng cho tất cả sinh viên"""
        print("🔍 Đang đánh giá kỹ năng...")
        skill_evaluator = SkillEvaluator()
        for student in students:
            skill_evaluations = skill_evaluator.evaluate_all_courses(student)
            student["skill_evaluations"] = skill_evaluations
        print(f"   ✅ Đã đánh giá kỹ năng cho {len(students)} sinh viên")
        return students
    
    def run_classification(self, students, normalization_method='minmax'):
        """Chạy phân loại với K-means + KNN"""
        print(f"🤖 Đang phân loại (chuẩn hóa: {normalization_method})...")
        classifier = StudentClassifier(n_clusters=4, normalization_method=normalization_method)
        classifier.fit(students)
        classified = classifier.predict(students)
        print(f"   ✅ Đã phân loại {len(classified)} sinh viên")
        return classified, classifier
    
    def calculate_metrics(self, classified_students):
        """Tính các chỉ số đánh giá"""
        # Lấy labels
        levels = [s.get('final_level', 'Unknown') for s in classified_students]
        kmeans_pred = [s.get('kmeans_prediction', 'Unknown') for s in classified_students]
        knn_pred = [s.get('knn_prediction', 'Unknown') for s in classified_students]
        
        # Đếm phân bố
        level_counts = {}
        for level in levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Đếm bất thường
        anomaly_count = sum(1 for s in classified_students if s.get('anomaly_detected', False))
        
        # Tính độ đồng thuận giữa K-means và KNN
        agreement = sum(1 for k, n in zip(kmeans_pred, knn_pred) if k == n)
        agreement_rate = agreement / len(classified_students) if classified_students else 0
        
        return {
            'total_students': len(classified_students),
            'level_distribution': level_counts,
            'anomaly_count': anomaly_count,
            'anomaly_rate': anomaly_count / len(classified_students) if classified_students else 0,
            'kmeans_knn_agreement': agreement_rate
        }
    
    def cross_validate(self, students, n_folds=5):
        """Cross-validation để đánh giá độ ổn định"""
        print(f"🔄 Đang chạy {n_folds}-fold cross-validation...")
        
        # Chuẩn bị dữ liệu
        n = len(students)
        fold_size = n // n_folds
        fold_results = []
        
        for fold in range(n_folds):
            # Chia train/test
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < n_folds - 1 else n
            
            test_students = students[start_idx:end_idx]
            train_students = students[:start_idx] + students[end_idx:]
            
            # Train trên train set
            classifier = StudentClassifier(n_clusters=4, normalization_method='minmax')
            classifier.fit(train_students)
            
            # Predict trên test set
            test_classified = classifier.predict(test_students)
            
            # Tính metrics cho fold này
            metrics = self.calculate_metrics(test_classified)
            fold_results.append(metrics)
            
            print(f"   Fold {fold+1}: {metrics['level_distribution']}")
        
        # Tính trung bình
        avg_agreement = np.mean([r['kmeans_knn_agreement'] for r in fold_results])
        std_agreement = np.std([r['kmeans_knn_agreement'] for r in fold_results])
        
        print(f"   ✅ Cross-validation hoàn thành")
        print(f"   📊 Độ đồng thuận K-means/KNN: {avg_agreement:.2%} ± {std_agreement:.2%}")
        
        return {
            'n_folds': n_folds,
            'fold_results': fold_results,
            'avg_agreement': avg_agreement,
            'std_agreement': std_agreement
        }
    
    def test_normalization_methods(self, students):
        """So sánh các phương pháp chuẩn hóa"""
        print("📈 So sánh các phương pháp chuẩn hóa...")
        
        methods = ['minmax', 'zscore', 'robust']
        results = {}
        
        for method in methods:
            classified, _ = self.run_classification(students.copy(), method)
            metrics = self.calculate_metrics(classified)
            results[method] = metrics
            print(f"   {method.upper()}: {metrics['level_distribution']}")
        
        return results
    
    def analyze_anomalies(self, classified_students):
        """Phân tích chi tiết các trường hợp bất thường"""
        print("⚠️ Phân tích bất thường...")
        
        anomalies = [s for s in classified_students if s.get('anomaly_detected', False)]
        
        if not anomalies:
            print("   ✅ Không có trường hợp bất thường")
            return {'count': 0, 'details': []}
        
        # Phân loại theo severity
        severity_counts = {1: 0, 2: 0, 3: 0}
        reason_counts = {}
        
        details = []
        for s in anomalies:
            severity = s.get('anomaly_severity', 1)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            reasons = s.get('anomaly_reasons', [])
            for reason in reasons:
                # Lấy loại lý do (phần đầu)
                reason_type = reason.split('(')[0].strip() if '(' in reason else reason[:30]
                reason_counts[reason_type] = reason_counts.get(reason_type, 0) + 1
            
            details.append({
                'student_id': s.get('student_id'),
                'name': s.get('name'),
                'final_level': s.get('final_level'),
                'severity': severity,
                'reasons': reasons
            })
        
        print(f"   Tổng số bất thường: {len(anomalies)}")
        print(f"   Theo mức độ: Nhẹ={severity_counts.get(1,0)}, Trung bình={severity_counts.get(2,0)}, Nghiêm trọng={severity_counts.get(3,0)}")
        print(f"   Top lý do:")
        for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"      - {reason}: {count}")
        
        return {
            'count': len(anomalies),
            'severity_distribution': severity_counts,
            'reason_counts': reason_counts,
            'details': details[:10]  # Top 10
        }
    
    def validate_consistency(self, students):
        """Kiểm tra tính nhất quán của phân loại"""
        print("🔍 Kiểm tra tính nhất quán...")
        
        # Chạy phân loại 3 lần với cùng dữ liệu
        results = []
        for i in range(3):
            classified, _ = self.run_classification(students.copy(), 'minmax')
            levels = [s.get('final_level') for s in classified]
            results.append(levels)
        
        # So sánh kết quả
        consistent = 0
        for i in range(len(results[0])):
            if results[0][i] == results[1][i] == results[2][i]:
                consistent += 1
        
        consistency_rate = consistent / len(results[0]) if results[0] else 0
        print(f"   ✅ Tỷ lệ nhất quán: {consistency_rate:.2%}")
        
        return {'consistency_rate': consistency_rate}
    
    def run_full_validation(self):
        """Chạy toàn bộ quy trình validation"""
        print("=" * 70)
        print("🎓 HỆ THỐNG KIỂM TRA ĐỘ CHÍNH XÁC PHÂN LOẠI SINH VIÊN")
        print("   Thuật toán: K-means + KNN + Phát hiện bất thường")
        print("=" * 70)
        
        # 1. Load dữ liệu
        students = self.load_data()
        
        # 2. Đánh giá kỹ năng
        students = self.evaluate_skills(students)
        
        # 3. Phân loại chính
        classified, classifier = self.run_classification(students)
        
        # 4. Tính metrics cơ bản
        print("\n📊 KẾT QUẢ PHÂN LOẠI:")
        metrics = self.calculate_metrics(classified)
        self.results['basic_metrics'] = metrics
        
        print(f"   Tổng số sinh viên: {metrics['total_students']}")
        print(f"   Phân bố:")
        for level, count in metrics['level_distribution'].items():
            pct = count / metrics['total_students'] * 100
            print(f"      - {level}: {count} ({pct:.1f}%)")
        print(f"   Bất thường: {metrics['anomaly_count']} ({metrics['anomaly_rate']:.1%})")
        print(f"   Độ đồng thuận K-means/KNN: {metrics['kmeans_knn_agreement']:.1%}")
        
        # 5. Cross-validation
        print("\n" + "-" * 70)
        cv_results = self.cross_validate(students)
        self.results['cross_validation'] = cv_results
        
        # 6. So sánh phương pháp chuẩn hóa
        print("\n" + "-" * 70)
        norm_results = self.test_normalization_methods(students)
        self.results['normalization_comparison'] = norm_results
        
        # 7. Phân tích bất thường
        print("\n" + "-" * 70)
        anomaly_analysis = self.analyze_anomalies(classified)
        self.results['anomaly_analysis'] = anomaly_analysis
        
        # 8. Kiểm tra tính nhất quán
        print("\n" + "-" * 70)
        consistency = self.validate_consistency(students)
        self.results['consistency'] = consistency
        
        # 9. Tổng kết
        print("\n" + "=" * 70)
        print("📋 TỔNG KẾT VALIDATION")
        print("=" * 70)
        
        print(f"""
✅ Kết quả:
   - Tổng sinh viên: {metrics['total_students']}
   - Độ đồng thuận K-means/KNN: {metrics['kmeans_knn_agreement']:.1%}
   - Cross-validation: {cv_results['avg_agreement']:.1%} ± {cv_results['std_agreement']:.1%}
   - Tính nhất quán: {consistency['consistency_rate']:.1%}
   - Tỷ lệ bất thường: {metrics['anomaly_rate']:.1%}

📊 Phân bố xếp loại:
   - Xuất sắc: {metrics['level_distribution'].get('Xuat sac', 0)}
   - Khá: {metrics['level_distribution'].get('Kha', 0)}
   - Trung bình: {metrics['level_distribution'].get('Trung binh', 0)}
   - Yếu: {metrics['level_distribution'].get('Yeu', 0)}
        """)
        
        # 10. Lưu kết quả
        self.save_results()
        
        return self.results
    
    def save_results(self):
        """Lưu kết quả validation ra file"""
        output_file = f'validation_results_{self.timestamp}.json'
        
        # Convert numpy types to Python types
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj
        
        results_to_save = convert(self.results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_to_save, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Đã lưu kết quả vào: {output_file}")


def main():
    """Chạy validation"""
    validator = ClassifierValidator()
    results = validator.run_full_validation()
    return results


if __name__ == "__main__":
    main()
