"""
Module sử dụng KNN để phân cụm và chuẩn hóa dữ liệu sinh viên
Hỗ trợ nhiều phương pháp chuẩn hóa: Min-Max, Z-Score, Robust Scaler

KIẾN TRÚC: CHỈ DÙNG KNN (Không dùng K-means)
=============================================
Module này khác với student_classifier.py:
- student_classifier.py: Dùng K-MEANS + KNN (KNN hỗ trợ K-means)
- Module này: CHỈ DÙNG KNN (Supervised Learning thuần túy)

LÝ DO DÙNG CHỈ KNN:
===================
1. Dữ liệu đã có nhãn sẵn (từ CSV: predicted_level)
2. Không cần K-means để tạo nhãn ban đầu
3. KNN học trực tiếp từ nhãn có sẵn
4. Tập trung vào chuẩn hóa dữ liệu để tăng độ chính xác

3 PHƯƠNG PHÁP CHUẨN HÓA:
========================
1. MIN-MAX SCALING:
   - Công thức: (x - min) / (max - min)
   - Kết quả: Dữ liệu trong khoảng [0, 1]
   - Ưu điểm: Đơn giản, giữ nguyên phân phối
   - Nhược điểm: Nhạy cảm với outliers

2. Z-SCORE (STANDARD SCALING):
   - Công thức: (x - mean) / std
   - Kết quả: Mean = 0, Std = 1
   - Ưu điểm: Phù hợp với phân phối chuẩn
   - Nhược điểm: Nhạy cảm với outliers

3. ROBUST SCALING:
   - Công thức: (x - median) / IQR
   - Kết quả: Median = 0, IQR = 1
   - Ưu điểm: Chống nhiễu tốt, dùng median thay vì mean
   - Nhược điểm: Phức tạp hơn

KNN PHÂN LOẠI SINH VIÊN:
========================
- Đầu vào: 13 đặc trưng (điểm số, thời gian, hành vi)
- Đầu ra: 4 mức độ (Xuất sắc, Khá, Trung bình, Yếu)
- Phương pháp: Tìm k láng giềng gần nhất và vote
"""

import numpy as np
from sklearn.neighbors import KNeighborsClassifier  # NOTE: CHỈ DÙNG KNN - Không dùng K-means
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler  # NOTE: 3 phương pháp chuẩn hóa
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')


class KNNClusteringNormalizer:
    """
    Lớp phân cụm sinh viên sử dụng KNN với nhiều phương pháp chuẩn hóa
    """
    
    def __init__(self, n_neighbors=5, normalization_method='minmax'):
        """
        Khởi tạo KNN Clustering với phương pháp chuẩn hóa
        
        NOTE: CHỈ DÙNG KNN - Không dùng K-means
        ========================================
        Module này khác với StudentClassifier:
        - StudentClassifier: K-means (tạo nhãn) + KNN (học từ nhãn)
        - Module này: CHỈ KNN (học từ nhãn có sẵn trong CSV)
        
        Args:
            n_neighbors: Số lượng láng giềng cho KNN (mặc định 5)
            normalization_method: Phương pháp chuẩn hóa ('minmax', 'zscore', 'robust')
        """
        self.n_neighbors = n_neighbors
        self.normalization_method = normalization_method
        
        # NOTE: Scaler - Chuẩn hóa dữ liệu
        # Chọn 1 trong 3: MinMaxScaler, StandardScaler, RobustScaler
        self.scaler = self._get_scaler()
        
        # NOTE: CHỈ DÙNG KNN - Không có K-means
        self.knn = None
        
        self.feature_names = []
        
        # NOTE: Mapping nhãn text -> số để KNN có thể học
        self.label_mapping = {
            "Xuat sac": 3,
            "Kha": 2,
            "Trung binh": 1,
            "Yeu": 0
        }
        self.reverse_label_mapping = {v: k for k, v in self.label_mapping.items()}
    
    def _get_scaler(self):
        """
        Lấy scaler dựa trên phương pháp chuẩn hóa
        
        NOTE: 3 PHƯƠNG PHÁP CHUẨN HÓA
        ==============================
        1. MIN-MAX: Chuẩn hóa về [0, 1]
           - Công thức: (x - min) / (max - min)
           - Dùng khi: Dữ liệu không có outliers
        
        2. Z-SCORE: Chuẩn hóa theo phân phối chuẩn
           - Công thức: (x - mean) / std
           - Dùng khi: Dữ liệu có phân phối chuẩn
        
        3. ROBUST: Chuẩn hóa chống nhiễu
           - Công thức: (x - median) / IQR
           - Dùng khi: Dữ liệu có nhiều outliers
        """
        if self.normalization_method == 'minmax':
            # NOTE: MIN-MAX SCALER - Chuẩn hóa về [0, 1]
            return MinMaxScaler()
        elif self.normalization_method == 'zscore':
            # NOTE: STANDARD SCALER (Z-Score) - Chuẩn hóa theo phân phối chuẩn
            return StandardScaler()
        elif self.normalization_method == 'robust':
            # NOTE: ROBUST SCALER - Chuẩn hóa chống nhiễu
            return RobustScaler()
        else:
            raise ValueError(f"Phương pháp chuẩn hóa không hợp lệ: {self.normalization_method}")
    
    def extract_features(self, students):
        """
        Trích xuất đặc trưng từ dữ liệu sinh viên
        
        Args:
            students: Danh sách sinh viên
            
        Returns:
            numpy array các đặc trưng
        """
        features = []
        self.feature_names = [
            'avg_score', 'avg_time', 'score_std', 'time_std',
            'midterm', 'final', 'homework', 'attendance',
            'assignment_completion', 'study_hours', 'lms_usage',
            'behavior_score', 'num_passed'
        ]
        
        for student in students:
            csv_data = student.get("csv_data", {})
            
            if csv_data:
                # Lấy dữ liệu từ CSV
                midterm = float(csv_data.get("midterm_score", 0))
                final = float(csv_data.get("final_score", 0))
                homework = float(csv_data.get("homework_score", 0))
                attendance = float(csv_data.get("attendance_rate", 0))
                assignment = float(csv_data.get("assignment_completion", 0))
                study_hours = float(csv_data.get("study_hours", 0))
                lms_usage = float(csv_data.get("lms_usage", 0))
                behavior = float(csv_data.get("behavior_score", 0))
                
                # Tính điểm trung bình
                course_scores = [midterm, final, homework]
                avg_score = np.mean(course_scores)
                score_std = np.std(course_scores)
                
                # Thời gian học
                avg_time = study_hours * 60 / 4  # Chia cho 4 môn
                time_std = study_hours * 10  # Giả định độ lệch
                
                # Số môn đạt
                num_passed = sum(1 for s in course_scores if s >= 5.5)
                
            else:
                # Fallback: tính từ dữ liệu courses
                course_scores = []
                course_times = []
                
                for course_name in ["Nhập Môn Lập Trình", "Kĩ Thuật Lập Trình",
                                   "Cấu trúc Dữ Liệu và Giải Thuật", "Lập Trình Hướng Đối Tượng"]:
                    if course_name in student.get("courses", {}):
                        course_data = student["courses"][course_name]
                        course_scores.append(course_data.get("score", 0))
                        course_times.append(course_data.get("time_minutes", 0))
                
                avg_score = np.mean(course_scores) if course_scores else 0
                score_std = np.std(course_scores) if course_scores else 0
                avg_time = np.mean(course_times) if course_times else 0
                time_std = np.std(course_times) if course_times else 0
                
                # Giá trị mặc định
                midterm = avg_score
                final = avg_score
                homework = avg_score
                attendance = 0.8
                assignment = 0.8
                study_hours = avg_time / 15
                lms_usage = study_hours * 0.5
                behavior = 80
                
                num_passed = sum(1 for s in course_scores if s >= 5.5)
            
            feature_vector = [
                avg_score, avg_time, score_std, time_std,
                midterm, final, homework, attendance,
                assignment, study_hours, lms_usage,
                behavior, num_passed
            ]
            
            features.append(feature_vector)
        
        return np.array(features)

    def normalize_features(self, features, fit=True):
        """
        Chuẩn hóa đặc trưng
        
        Args:
            features: Mảng đặc trưng
            fit: True nếu cần fit scaler, False nếu chỉ transform
            
        Returns:
            Mảng đã chuẩn hóa
        """
        if fit:
            return self.scaler.fit_transform(features)
        else:
            return self.scaler.transform(features)
    
    def get_labels(self, students):
        """
        Lấy nhãn từ dữ liệu sinh viên
        
        Args:
            students: Danh sách sinh viên
            
        Returns:
            Mảng nhãn số
        """
        labels = []
        for student in students:
            # Ưu tiên lấy từ CSV
            csv_data = student.get("csv_data", {})
            if csv_data and "predicted_level" in csv_data:
                level = csv_data["predicted_level"]
                # Chuẩn hóa tên level
                level = level.replace("Xuất sắc", "Xuat sac").replace("Yếu", "Yeu")
            else:
                level = student.get("base_level", "Trung binh")
            
            labels.append(self.label_mapping.get(level, 1))
        
        return np.array(labels)
    
    def fit(self, students):
        """
        Huấn luyện mô hình KNN
        
        NOTE: QUY TRÌNH HUẤN LUYỆN CHỈ DÙNG KNN
        ========================================
        1. Trích xuất 13 đặc trưng từ dữ liệu sinh viên
        2. Chuẩn hóa đặc trưng (minmax/zscore/robust)
        3. Lấy nhãn từ CSV (predicted_level)
        4. Huấn luyện KNN với nhãn có sẵn
        
        KHÁC BIỆT VỚI student_classifier.py:
        - student_classifier.py: K-means tạo nhãn -> KNN học từ nhãn đó
        - Module này: Nhãn có sẵn trong CSV -> KNN học trực tiếp
        
        Args:
            students: Danh sách sinh viên để huấn luyện
        """
        # NOTE: BƯỚC 1 - Trích xuất đặc trưng
        # 13 đặc trưng: điểm số, thời gian, hành vi, tham gia...
        features = self.extract_features(students)
        
        # NOTE: BƯỚC 2 - Chuẩn hóa đặc trưng
        # Sử dụng 1 trong 3 phương pháp: minmax, zscore, robust
        # Mục đích: Đưa các đặc trưng về cùng thang đo
        features_normalized = self.normalize_features(features, fit=True)
        
        # NOTE: BƯỚC 3 - Lấy nhãn từ CSV
        # Nhãn đã có sẵn trong dữ liệu (predicted_level)
        # Không cần K-means để tạo nhãn
        labels = self.get_labels(students)
        
        # NOTE: BƯỚC 4 - Điều chỉnh k cho KNN
        # k = số láng giềng gần nhất để xem xét
        # k nhỏ: Nhạy cảm với nhiễu
        # k lớn: Mượt hơn nhưng mất chi tiết
        k = min(self.n_neighbors, len(students) // 2)
        k = max(1, k)
        
        # NOTE: BƯỚC 5 - Huấn luyện KNN
        # weights='distance': Láng giềng gần có trọng số cao hơn
        self.knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
        self.knn.fit(features_normalized, labels)
        
        print(f"✅ Đã huấn luyện KNN với k={k}, phương pháp chuẩn hóa: {self.normalization_method}")
    
    def predict(self, students):
        """
        Dự đoán phân loại cho sinh viên
        
        Args:
            students: Danh sách sinh viên cần phân loại
            
        Returns:
            Danh sách sinh viên kèm kết quả phân loại
        """
        if self.knn is None:
            raise ValueError("Mô hình chưa được huấn luyện. Gọi fit() trước.")
        
        # Trích xuất và chuẩn hóa đặc trưng
        features = self.extract_features(students)
        features_normalized = self.normalize_features(features, fit=False)
        
        # Dự đoán
        predictions = self.knn.predict(features_normalized)
        probabilities = self.knn.predict_proba(features_normalized)
        
        # Lấy các classes mà KNN đã học
        classes = self.knn.classes_
        
        # Tạo kết quả
        results = []
        for i, student in enumerate(students):
            predicted_label = self.reverse_label_mapping[predictions[i]]
            
            # Tìm index của prediction trong classes
            pred_idx = np.where(classes == predictions[i])[0][0]
            confidence = probabilities[i][pred_idx]
            
            # Tạo dict probabilities với đúng classes
            prob_dict = {}
            for j, class_label in enumerate(classes):
                level_name = self.reverse_label_mapping[class_label]
                prob_dict[level_name] = float(probabilities[i][j])
            
            result = {
                **student,
                "knn_prediction": predicted_label,
                "confidence": float(confidence),
                "probabilities": prob_dict
            }
            results.append(result)
        
        return results
    
    def evaluate(self, students):
        """
        Đánh giá mô hình với cross-validation
        
        Args:
            students: Danh sách sinh viên để đánh giá
            
        Returns:
            Dictionary chứa các metrics đánh giá
        """
        features = self.extract_features(students)
        features_normalized = self.normalize_features(features, fit=True)
        labels = self.get_labels(students)
        
        # Cross-validation
        cv_scores = cross_val_score(self.knn, features_normalized, labels, cv=5)
        
        # Train-test split để có confusion matrix
        X_train, X_test, y_train, y_test = train_test_split(
            features_normalized, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        self.knn.fit(X_train, y_train)
        y_pred = self.knn.predict(X_test)
        
        # Lấy các labels thực sự có trong y_test
        unique_labels = sorted(set(y_test) | set(y_pred))
        target_names = [self.reverse_label_mapping[label] for label in unique_labels]
        
        # Classification report
        report = classification_report(
            y_test, y_pred,
            labels=unique_labels,
            target_names=target_names,
            output_dict=True,
            zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=unique_labels)
        
        return {
            "cv_scores": cv_scores.tolist(),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "labels": target_names
        }
    
    def get_feature_importance(self, students):
        """
        Tính độ quan trọng của các đặc trưng (dựa trên phương sai)
        
        Args:
            students: Danh sách sinh viên
            
        Returns:
            Dictionary mapping tên đặc trưng -> độ quan trọng
        """
        features = self.extract_features(students)
        features_normalized = self.normalize_features(features, fit=True)
        
        # Tính phương sai của mỗi đặc trưng
        variances = np.var(features_normalized, axis=0)
        
        # Chuẩn hóa về tổng = 1
        total_var = np.sum(variances)
        importances = variances / total_var if total_var > 0 else variances
        
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names, importances)
        }


def compare_normalization_methods(students):
    """
    So sánh các phương pháp chuẩn hóa khác nhau
    
    Args:
        students: Danh sách sinh viên
        
    Returns:
        Dictionary chứa kết quả so sánh
    """
    methods = ['minmax', 'zscore', 'robust']
    results = {}
    
    for method in methods:
        print(f"\n📊 Đánh giá phương pháp: {method.upper()}")
        classifier = KNNClusteringNormalizer(n_neighbors=5, normalization_method=method)
        classifier.fit(students)
        
        evaluation = classifier.evaluate(students)
        results[method] = {
            "cv_mean": evaluation["cv_mean"],
            "cv_std": evaluation["cv_std"],
            "classification_report": evaluation["classification_report"]
        }
        
        print(f"  ✓ Độ chính xác trung bình: {evaluation['cv_mean']:.4f} (±{evaluation['cv_std']:.4f})")
    
    return results
