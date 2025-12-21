"""
Test Suite cho Hệ Thống Phân Loại Sinh Viên
==========================================
- Test với nhiều tỷ lệ train/test khác nhau
- Đánh giá accuracy, precision, recall, f1-score
- So sánh các phương pháp chuẩn hóa
"""

import sys
import os
import numpy as np
from collections import Counter
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler

from data_generator import StudentDataGenerator


class ClassifierTester:
    """Test và đánh giá hệ thống phân loại"""
    
    def __init__(self):
        self.results = []
        self.level_order = ["Xuat sac", "Kha", "Trung binh", "Yeu"]
        
    def load_data(self, use_supabase=True, n_generated=200):
        """Load dữ liệu từ Supabase hoặc generate"""
        print("=" * 70)
        print("📊 LOADING DATA")
        print("=" * 70)
        
        generator = StudentDataGenerator(seed=42, use_supabase=use_supabase)
        
        if use_supabase:
            students = generator.load_all_students()
            if not students:
                print("⚠️ Không load được từ Supabase, generate dữ liệu...")
                students = generator.generate_realistic_students(n_generated)
        else:
            students = generator.generate_realistic_students(n_generated)
        
        print(f"✅ Loaded {len(students)} sinh viên")
        return students
    
    def extract_features(self, students):
        """Trích xuất 12 features từ sinh viên"""
        features = []
        labels = []
        valid_students = []
        
        for student in students:
            csv_data = student.get("csv_data", {})
            courses = student.get("courses", {})
            
            # Kiểm tra dữ liệu hợp lệ
            course_scores = []
            for course_data in courses.values():
                if isinstance(course_data, dict):
                    score = float(course_data.get("score", 0))
                    if score > 0:
                        course_scores.append(score)
            
            total_score = float(csv_data.get("total_score", 0))
            if not course_scores and total_score == 0:
                continue
            
            # Tính features
            course_midterms = [float(c.get("midterm_score", 0)) for c in courses.values() if isinstance(c, dict)]
            course_finals = [float(c.get("final_score", 0)) for c in courses.values() if isinstance(c, dict)]
            course_homeworks = [float(c.get("homework_score", 0)) for c in courses.values() if isinstance(c, dict)]
            
            avg_score = sum(course_scores) / len(course_scores) if course_scores else total_score
            midterm = sum(course_midterms) / len(course_midterms) if course_midterms else float(csv_data.get("midterm_score", 0))
            final = sum(course_finals) / len(course_finals) if course_finals else float(csv_data.get("final_score", 0))
            homework = sum(course_homeworks) / len(course_homeworks) if course_homeworks else 0
            
            attendance = float(csv_data.get("attendance_rate", 0.8))
            behavior = float(csv_data.get("behavior_score_100", 50)) / 100
            late_submissions = float(csv_data.get("late_submissions", 0))
            assignment = float(csv_data.get("assignment_completion", 0.7))
            
            total_time = sum(float(c.get("time_minutes", 0)) for c in courses.values() if isinstance(c, dict))
            avg_time = total_time / len(courses) if courses else 60
            
            punctuality = max(0, 1.0 - (late_submissions / 10.0))
            stability = 1.0 - (np.std(course_scores) / 5.0 if len(course_scores) > 1 else 0)
            
            # Tính anomaly score
            anomaly_score = 0
            if avg_score >= 9.5 and avg_time < 30: anomaly_score = 1.0
            elif avg_score >= 9.0 and avg_time < 60: anomaly_score = 0.6
            elif avg_score >= 8.5 and avg_time < 90: anomaly_score = 0.3
            
            # 12 features
            features.append([
                avg_score / 10.0,
                midterm / 10.0,
                final / 10.0,
                homework / 10.0,
                behavior,
                attendance,
                punctuality,
                assignment,
                min(avg_time / 600, 1.0),
                1.0 - anomaly_score,
                min(late_submissions / 10, 1.0),
                stability
            ])
            
            # Ground truth label dựa trên điểm tổng hợp
            composite = avg_score * 0.5 + behavior * 10 * 0.3 + attendance * 10 * 0.2
            if composite >= 8.0:
                label = "Xuat sac"
            elif composite >= 7.0:
                label = "Kha"
            elif composite >= 5.0:
                label = "Trung binh"
            else:
                label = "Yeu"
            
            labels.append(label)
            valid_students.append(student)
        
        return np.array(features), labels, valid_students
    
    def test_train_test_split(self, features, labels, test_sizes=[0.2, 0.3, 0.4]):
        """Test với các tỷ lệ train/test khác nhau"""
        print("\n" + "=" * 70)
        print("🧪 TEST 1: TRAIN/TEST SPLIT RATIOS")
        print("=" * 70)
        
        results = []
        
        for test_size in test_sizes:
            train_size = 1 - test_size
            
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    features, labels, 
                    test_size=test_size, 
                    random_state=42, 
                    stratify=labels
                )
                
                # Chuẩn hóa
                scaler = MinMaxScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # K-means clustering
                kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
                kmeans.fit(X_train_scaled)
                
                # Gán nhãn cho clusters
                cluster_labels = {}
                for cluster in range(4):
                    cluster_mask = kmeans.labels_ == cluster
                    cluster_y = [y_train[i] for i in range(len(y_train)) if cluster_mask[i]]
                    if cluster_y:
                        cluster_labels[cluster] = Counter(cluster_y).most_common(1)[0][0]
                    else:
                        cluster_labels[cluster] = "Trung binh"
                
                # KNN
                k = max(1, min(5, len(X_train) // 10))
                knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
                knn.fit(X_train_scaled, y_train)
                
                # Predict
                y_pred = knn.predict(X_test_scaled)
                
                # Metrics
                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                
                result = {
                    'test_size': test_size,
                    'train_size': train_size,
                    'n_train': len(X_train),
                    'n_test': len(X_test),
                    'k': k,
                    'accuracy': acc,
                    'precision': prec,
                    'recall': rec,
                    'f1_score': f1
                }
                results.append(result)
                
                print(f"\n📊 Train: {train_size*100:.0f}% ({len(X_train)}) | Test: {test_size*100:.0f}% ({len(X_test)})")
                print(f"   KNN k={k}")
                print(f"   Accuracy:  {acc*100:.2f}%")
                print(f"   Precision: {prec*100:.2f}%")
                print(f"   Recall:    {rec*100:.2f}%")
                print(f"   F1-Score:  {f1*100:.2f}%")
                
            except Exception as e:
                print(f"\n❌ Error với test_size={test_size}: {e}")
        
        return results
    
    def test_normalization_methods(self, features, labels):
        """So sánh các phương pháp chuẩn hóa"""
        print("\n" + "=" * 70)
        print("🧪 TEST 2: NORMALIZATION METHODS")
        print("=" * 70)
        
        scalers = {
            'MinMax': MinMaxScaler(),
            'ZScore (Standard)': StandardScaler(),
            'Robust': RobustScaler()
        }
        
        results = []
        
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.3, random_state=42, stratify=labels
        )
        
        for name, scaler in scalers.items():
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # KNN
            k = max(1, min(5, len(X_train) // 10))
            knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
            knn.fit(X_train_scaled, y_train)
            y_pred = knn.predict(X_test_scaled)
            
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            results.append({
                'method': name,
                'accuracy': acc,
                'f1_score': f1
            })
            
            print(f"\n📊 {name}")
            print(f"   Accuracy: {acc*100:.2f}%")
            print(f"   F1-Score: {f1*100:.2f}%")
        
        return results
    
    def test_cross_validation(self, features, labels, n_folds=5):
        """Cross-validation test"""
        print("\n" + "=" * 70)
        print(f"🧪 TEST 3: {n_folds}-FOLD CROSS VALIDATION")
        print("=" * 70)
        
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(features)
        
        k = max(1, min(5, len(features) // 10))
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
        
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores = cross_val_score(knn, X_scaled, labels, cv=cv, scoring='accuracy')
        
        print(f"\n📊 KNN (k={k}) với {n_folds}-Fold CV")
        print(f"   Scores: {[f'{s*100:.1f}%' for s in scores]}")
        print(f"   Mean:   {scores.mean()*100:.2f}%")
        print(f"   Std:    {scores.std()*100:.2f}%")
        
        return {
            'n_folds': n_folds,
            'scores': scores.tolist(),
            'mean': scores.mean(),
            'std': scores.std()
        }
    
    def test_k_values(self, features, labels):
        """Test các giá trị k khác nhau cho KNN"""
        print("\n" + "=" * 70)
        print("🧪 TEST 4: KNN K-VALUES")
        print("=" * 70)
        
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.3, random_state=42, stratify=labels
        )
        
        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        results = []
        k_values = [1, 3, 5, 7, 9, 11]
        
        print(f"\n{'k':<5} {'Accuracy':<12} {'F1-Score':<12}")
        print("-" * 30)
        
        for k in k_values:
            if k > len(X_train):
                continue
                
            knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
            knn.fit(X_train_scaled, y_train)
            y_pred = knn.predict(X_test_scaled)
            
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            results.append({'k': k, 'accuracy': acc, 'f1_score': f1})
            print(f"{k:<5} {acc*100:<12.2f} {f1*100:<12.2f}")
        
        # Best k
        best = max(results, key=lambda x: x['accuracy'])
        print(f"\n✅ Best k={best['k']} với Accuracy={best['accuracy']*100:.2f}%")
        
        return results
    
    def generate_classification_report(self, features, labels):
        """Tạo báo cáo phân loại chi tiết"""
        print("\n" + "=" * 70)
        print("📋 CLASSIFICATION REPORT")
        print("=" * 70)
        
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.3, random_state=42, stratify=labels
        )
        
        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        k = max(1, min(5, len(X_train) // 10))
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
        knn.fit(X_train_scaled, y_train)
        y_pred = knn.predict(X_test_scaled)
        
        print(f"\n📊 Dataset: {len(features)} samples")
        print(f"   Train: {len(X_train)} ({len(X_train)/len(features)*100:.0f}%)")
        print(f"   Test:  {len(X_test)} ({len(X_test)/len(features)*100:.0f}%)")
        
        print("\n📊 Label Distribution (Train):")
        train_dist = Counter(y_train)
        for level in self.level_order:
            count = train_dist.get(level, 0)
            print(f"   {level:<12}: {count:>4} ({count/len(y_train)*100:>5.1f}%)")
        
        print("\n📊 Label Distribution (Test):")
        test_dist = Counter(y_test)
        for level in self.level_order:
            count = test_dist.get(level, 0)
            print(f"   {level:<12}: {count:>4} ({count/len(y_test)*100:>5.1f}%)")
        
        print("\n" + "-" * 70)
        print("CLASSIFICATION REPORT:")
        print("-" * 70)
        # Chỉ lấy các labels có trong dữ liệu
        unique_labels = sorted(set(y_test) | set(y_pred), key=lambda x: self.level_order.index(x) if x in self.level_order else 99)
        print(classification_report(y_test, y_pred, labels=unique_labels, zero_division=0))
        
        print("\n" + "-" * 70)
        print("CONFUSION MATRIX:")
        print("-" * 70)
        unique_labels = sorted(set(y_test) | set(y_pred), key=lambda x: self.level_order.index(x) if x in self.level_order else 99)
        cm = confusion_matrix(y_test, y_pred, labels=unique_labels)
        
        # Header
        print(f"{'Actual \\ Pred':<15}", end="")
        for level in unique_labels:
            print(f"{level[:8]:<10}", end="")
        print()
        
        # Matrix
        for i, level in enumerate(unique_labels):
            print(f"{level:<15}", end="")
            for j in range(len(unique_labels)):
                print(f"{cm[i][j]:<10}", end="")
            print()
        
        return {
            'train_size': len(X_train),
            'test_size': len(X_test),
            'train_distribution': dict(train_dist),
            'test_distribution': dict(test_dist),
            'confusion_matrix': cm.tolist()
        }
    
    def run_all_tests(self, use_supabase=True):
        """Chạy tất cả các test"""
        print("\n" + "=" * 70)
        print("🚀 STUDENT CLASSIFIER - FULL TEST SUITE")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Load data
        students = self.load_data(use_supabase=use_supabase)
        features, labels, valid_students = self.extract_features(students)
        
        print(f"\n📊 Valid samples: {len(features)}")
        print(f"   Features: 12 dimensions")
        
        # Distribution
        dist = Counter(labels)
        print("\n📊 Label Distribution:")
        for level in self.level_order:
            count = dist.get(level, 0)
            print(f"   {level:<12}: {count:>4} ({count/len(labels)*100:>5.1f}%)")
        
        # Run tests
        results = {
            'total_samples': len(features),
            'label_distribution': dict(dist)
        }
        
        results['train_test_split'] = self.test_train_test_split(features, labels)
        results['normalization'] = self.test_normalization_methods(features, labels)
        results['cross_validation'] = self.test_cross_validation(features, labels)
        results['k_values'] = self.test_k_values(features, labels)
        results['classification_report'] = self.generate_classification_report(features, labels)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        
        best_split = max(results['train_test_split'], key=lambda x: x['accuracy'])
        best_norm = max(results['normalization'], key=lambda x: x['accuracy'])
        best_k = max(results['k_values'], key=lambda x: x['accuracy'])
        
        print(f"\n✅ Best Train/Test Split: {best_split['train_size']*100:.0f}%/{best_split['test_size']*100:.0f}%")
        print(f"   Accuracy: {best_split['accuracy']*100:.2f}%")
        
        print(f"\n✅ Best Normalization: {best_norm['method']}")
        print(f"   Accuracy: {best_norm['accuracy']*100:.2f}%")
        
        print(f"\n✅ Best KNN k: {best_k['k']}")
        print(f"   Accuracy: {best_k['accuracy']*100:.2f}%")
        
        print(f"\n✅ Cross-Validation ({results['cross_validation']['n_folds']}-Fold):")
        print(f"   Mean Accuracy: {results['cross_validation']['mean']*100:.2f}% ± {results['cross_validation']['std']*100:.2f}%")
        
        print("\n" + "=" * 70)
        print("✨ TEST COMPLETED!")
        print("=" * 70)
        
        return results


def main():
    """Main function"""
    tester = ClassifierTester()
    
    # Thử load từ Supabase trước, nếu không được thì generate
    results = tester.run_all_tests(use_supabase=True)
    
    # Lưu kết quả
    import json
    with open('tests/test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n💾 Results saved to tests/test_results.json")


if __name__ == "__main__":
    main()
