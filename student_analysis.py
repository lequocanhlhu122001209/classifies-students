import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

# Đọc dữ liệu
df = pd.read_csv('student_classification_supabase_ready_final.csv')

# Chọn các features cho việc phân loại
features = ['midterm_score', 'final_score', 'homework_score', 'attendance_rate', 
           'assignment_completion', 'study_hours_per_week', 'participation_score',
           'lms_usage_hours', 'behCTior_score_100', 'attendance_rate_100', 
           'assignment_completion_100']

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X = scaler.fit_transform(df[features])

# KMeans cho level_prediction
kmeans = KMeans(n_clusters=4, random_state=42)
df['level_prediction'] = kmeans.fit_predict(X)

# Chuyển đổi các nhãn số thành text
level_map = {
    0: 'Trung bình',
    1: 'Khá',
    2: 'Xuất sắc',
    3: 'Yếu'
}
df['level_prediction'] = df['level_prediction'].map(level_map)

# KNN cho predicted_level
# Sử dụng dữ liệu đã có nhãn làm training set
y = df['level_prediction']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
df['predicted_level'] = knn.predict(X)

# Tính toán risk_level
def calculate_risk_level(row):
    score = 0
    score += (row['attendance_rate_100'] < 70) * 2
    score += (row['behCTior_score_100'] < 70) * 2
    score += (row['assignment_completion_100'] < 70) * 2
    score += (row['study_hours_per_week'] < 15) * 1
    score += (row['late_submissions'] > 3) * 1
    
    if score >= 6:
        return 'Cao'
    elif score >= 3:
        return 'Trung bình'
    else:
        return 'Thấp'

df['risk_level'] = df.apply(calculate_risk_level, axis=1)

# Lưu kết quả
df.to_csv('student_classification_results.csv', index=False)
print("Phân loại hoàn tất. Kết quả đã được lưu vào file 'student_classification_results.csv'")