import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

class AdvancedStudentClassifier:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=4, random_state=42)
        self.knn = KNeighborsClassifier(n_neighbors=5)
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def preprocess_data(self, df):
        """Tiền xử lý và chuẩn hóa dữ liệu"""
        # Chuyển đổi cột categorical sang numerical
        df['sex_encoded'] = df['sex'].map({'Nam': 1, 'Nữ': 0})
        
        # Tính toán các chỉ số học tập tổng hợp
        df['academic_score'] = (df['midterm_score'] + df['final_score'] + df['homework_score']) / 3
        df['engagement_score'] = (df['attendance_rate_100'] + df['participation_score'] * 10) / 2
        df['behavior_index'] = (df['behCTior_score_100'] + df['assignment_completion_100']) / 2
        
        # Tính toán chỉ số rủi ro
        df['risk_index'] = (
            (df['attendance_rate_100'] < 70).astype(int) * 3 +
            (df['behCTior_score_100'] < 50).astype(int) * 2 +
            (df['late_submissions'] > 5).astype(int) * 1
        )
        
        return df
    
    def extract_features(self, df):
        """Trích xuất đặc trưng cho mô hình"""
        features = [
            'academic_score', 'engagement_score', 'behavior_index',
            'study_hours_per_week', 'lms_usage_hours', 'assignment_completion_100',
            'attendance_rate_100', 'behCTior_score_100', 'participation_score',
            'late_submissions', 'risk_index', 'sex_encoded'
        ]
        return df[features]
    
    def train_models(self, df):
        """Huấn luyện các mô hình phân loại"""
        # Tiền xử lý dữ liệu
        processed_df = self.preprocess_data(df)
        X = self.extract_features(processed_df)
        
        # Chuẩn hóa dữ liệu
        X_scaled = self.scaler.fit_transform(X)
        
        # Huấn luyện KMeans cho level_prediction
        self.kmeans.fit(X_scaled)
        
        # Ánh xạ các cụm vào các mức độ
        cluster_centers = self.kmeans.cluster_centers_
        academic_means = cluster_centers[:, 0]  # Lấy điểm học tập trung bình của mỗi cụm
        cluster_mapping = {
            np.argmax(academic_means): 'Xuất sắc',
            np.argsort(academic_means)[-2]: 'Khá',
            np.argsort(academic_means)[1]: 'Trung bình',
            np.argmin(academic_means): 'Yếu'
        }
        
        # Tạo nhãn cho KNN
        kmeans_labels = [cluster_mapping[label] for label in self.kmeans.labels_]
        
        # Huấn luyện KNN
        self.knn.fit(X_scaled, kmeans_labels)
        
        # Huấn luyện RandomForest cho risk_level
        risk_mapping = {0: 'Thấp', 1: 'Trung bình', 2: 'Cao'}
        risk_labels = processed_df['risk_index'].apply(
            lambda x: 'Cao' if x >= 4 else 'Trung bình' if x >= 2 else 'Thấp'
        )
        self.rf_classifier.fit(X_scaled, risk_labels)
        
        return processed_df
    
    def predict(self, student_data):
        """Dự đoán mức độ và rủi ro cho sinh viên mới"""
        # Tiền xử lý dữ liệu
        processed_data = self.preprocess_data(student_data)
        X = self.extract_features(processed_data)
        X_scaled = self.scaler.transform(X)
        
        # Dự đoán mức độ
        level_predictions = self.knn.predict(X_scaled)
        
        # Dự đoán rủi ro
        risk_predictions = self.rf_classifier.predict(X_scaled)
        
        return level_predictions, risk_predictions
    
    def analyze_student(self, student_data):
        """Phân tích chi tiết một sinh viên"""
        processed_data = self.preprocess_data(student_data)
        X = self.extract_features(processed_data)
        X_scaled = self.scaler.transform(X)
        
        level_pred, risk_pred = self.predict(student_data)
        
        # Tính toán điểm mạnh yếu
        strengths = []
        weaknesses = []
        
        for idx, student in processed_data.iterrows():
            if student['academic_score'] >= 8:
                strengths.append('Học tập tốt')
            elif student['academic_score'] < 6:
                weaknesses.append('Cần cải thiện điểm số')
                
            if student['engagement_score'] >= 80:
                strengths.append('Tham gia tích cực')
            elif student['engagement_score'] < 60:
                weaknesses.append('Cần tăng cường tham gia học tập')
                
            if student['behavior_index'] >= 80:
                strengths.append('Hành vi học tập tốt')
            elif student['behavior_index'] < 60:
                weaknesses.append('Cần cải thiện hành vi học tập')
        
        return {
            'level': level_pred[0],
            'risk': risk_pred[0],
            'strengths': strengths,
            'weaknesses': weaknesses,
            'metrics': {
                'academic_score': processed_data['academic_score'].values[0],
                'engagement_score': processed_data['engagement_score'].values[0],
                'behavior_index': processed_data['behavior_index'].values[0]
            }
        }
    
    def generate_report(self, df):
        """Tạo báo cáo phân tích tổng thể"""
        processed_df = self.preprocess_data(df)
        
        # Thống kê phân bố mức độ
        level_dist = processed_df['level_prediction'].value_counts()
        
        # Thống kê phân bố rủi ro
        risk_dist = processed_df['risk_level'].value_counts()
        
        # Phân tích theo khoa
        dept_stats = processed_df.groupby('Khoa').agg({
            'academic_score': 'mean',
            'engagement_score': 'mean',
            'behavior_index': 'mean'
        }).round(2)
        
        # Tạo biểu đồ
        plt.figure(figsize=(15, 10))
        
        # Biểu đồ phân bố mức độ
        plt.subplot(2, 2, 1)
        sns.barplot(x=level_dist.index, y=level_dist.values)
        plt.title('Phân bố mức độ học tập')
        
        # Biểu đồ phân bố rủi ro
        plt.subplot(2, 2, 2)
        sns.barplot(x=risk_dist.index, y=risk_dist.values)
        plt.title('Phân bố mức độ rủi ro')
        
        # Biểu đồ điểm trung bình theo khoa
        plt.subplot(2, 2, 3)
        sns.barplot(x=dept_stats.index, y=dept_stats['academic_score'])
        plt.title('Điểm trung bình theo khoa')
        
        plt.tight_layout()
        plt.savefig('analysis_report.png')
        
        return {
            'level_distribution': level_dist.to_dict(),
            'risk_distribution': risk_dist.to_dict(),
            'department_statistics': dept_stats.to_dict(),
            'plot_path': 'analysis_report.png'
        }
    
    def save_models(self, path='models/'):
        """Lưu các mô hình đã huấn luyện"""
        import os
        if not os.path.exists(path):
            os.makedirs(path)
            
        joblib.dump(self.scaler, f'{path}scaler.pkl')
        joblib.dump(self.kmeans, f'{path}kmeans.pkl')
        joblib.dump(self.knn, f'{path}knn.pkl')
        joblib.dump(self.rf_classifier, f'{path}rf_classifier.pkl')
    
    def load_models(self, path='models/'):
        """Tải các mô hình đã lưu"""
        self.scaler = joblib.load(f'{path}scaler.pkl')
        self.kmeans = joblib.load(f'{path}kmeans.pkl')
        self.knn = joblib.load(f'{path}knn.pkl')
        self.rf_classifier = joblib.load(f'{path}rf_classifier.pkl')

# Hàm chính để chạy phân tích
def run_analysis():
    # Đọc dữ liệu
    df = pd.read_csv('student_classification_supabase_ready_final.csv')
    
    # Khởi tạo classifier
    classifier = AdvancedStudentClassifier()
    
    # Huấn luyện mô hình
    processed_df = classifier.train_models(df)
    
    # Tạo báo cáo
    report = classifier.generate_report(df)
    
    # Lưu mô hình
    classifier.save_models()
    
    # In kết quả tổng quan
    print("\n=== BÁO CÁO PHÂN TÍCH SINH VIÊN ===")
    print("\nPhân bố mức độ học tập:")
    for level, count in report['level_distribution'].items():
        print(f"{level}: {count} sinh viên")
    
    print("\nPhân bố mức độ rủi ro:")
    for risk, count in report['risk_distribution'].items():
        print(f"{risk}: {count} sinh viên")
    
    print("\nĐiểm trung bình theo khoa:")
    for dept, stats in report['department_statistics'].items():
        print(f"\n{dept}:")
        for metric, value in stats.items():
            print(f"- {metric}: {value:.2f}")

if __name__ == "__main__":
    run_analysis()