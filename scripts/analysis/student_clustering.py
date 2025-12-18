import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd

def prepare_student_data(student_data):
    """
    Chuẩn bị dữ liệu cho việc phân tích
    student_data: DataFrame với các cột về điểm số và thời gian học tập
    """
    # Tạo features cho phân tích
    features = []
    for student in student_data:
        student_features = []
        # Điểm trung bình các môn
        avg_score = np.mean([course['score'] for course in student['courses'].values()])
        # Thời gian trung bình mỗi bài
        avg_time = np.mean([course['time_minutes'] for course in student['courses'].values()])
        # Số bài tập hoàn thành
        completed_exercises = len([course for course in student['courses'].values() if course.get('completed', False)])
        # Tỷ lệ bài tập đúng
        correct_ratio = np.mean([course.get('correct_ratio', 0) for course in student['courses'].values()])
        
        student_features.extend([avg_score, avg_time, completed_exercises, correct_ratio])
        features.append(student_features)
    
    return np.array(features)

def kmeans_clustering(features, n_clusters=4):
    """
    Phân cụm sinh viên using K-means
    """
    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Áp dụng K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features_scaled)
    
    # Phân tích các cụm
    cluster_analysis = []
    for i in range(n_clusters):
        cluster_features = features[clusters == i]
        cluster_info = {
            'cluster_id': i,
            'size': len(cluster_features),
            'avg_score': np.mean(cluster_features[:, 0]),
            'avg_time': np.mean(cluster_features[:, 1]),
            'avg_completed': np.mean(cluster_features[:, 2]),
            'avg_correct_ratio': np.mean(cluster_features[:, 3])
        }
        cluster_analysis.append(cluster_info)
    
    # Sắp xếp cụm theo điểm trung bình để gán nhãn
    cluster_analysis.sort(key=lambda x: x['avg_score'], reverse=True)
    cluster_labels = {
        cluster_analysis[0]['cluster_id']: 'Xuat sac',
        cluster_analysis[1]['cluster_id']: 'Kha',
        cluster_analysis[2]['cluster_id']: 'Trung binh',
        cluster_analysis[3]['cluster_id']: 'Yeu'
    }
    
    return clusters, cluster_labels, cluster_analysis

def knn_classification(features, labels, n_neighbors=5):
    """
    Phân loại sinh viên using KNN dựa trên dữ liệu đã được gán nhãn
    """
    # Chia dữ liệu
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42
    )
    
    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Huấn luyện mô hình KNN
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train_scaled, y_train)
    
    # Đánh giá mô hình
    train_accuracy = knn.score(X_train_scaled, y_train)
    test_accuracy = knn.score(X_test_scaled, y_test)
    
    return knn, scaler, train_accuracy, test_accuracy

def analyze_student(student_features, knn_model, scaler, cluster_centers=None):
    """
    Phân tích một sinh viên sử dụng cả K-means và KNN
    """
    # Chuẩn hóa features của sinh viên
    student_scaled = scaler.transform([student_features])
    
    # Dự đoán sử dụng KNN
    knn_prediction = knn_model.predict(student_scaled)[0]
    
    # Tính khoảng cách tới các neighbors gần nhất
    distances, indices = knn_model.kneighbors(student_scaled)
    
    # Phân tích chi tiết
    analysis = {
        'predicted_level': knn_prediction,
        'confidence': 1 - (distances[0].mean() / distances[0].max()),
        'nearest_neighbors': indices[0].tolist(),
        'neighbor_distances': distances[0].tolist()
    }
    
    # Thêm phân tích với cluster centers nếu có
    if cluster_centers is not None:
        distances_to_centers = np.linalg.norm(
            student_scaled - cluster_centers, axis=1
        )
        analysis['closest_cluster'] = np.argmin(distances_to_centers)
        analysis['cluster_distances'] = distances_to_centers.tolist()
    
    return analysis

def get_improvement_suggestions(student_features, analysis):
    """
    Đưa ra gợi ý cải thiện dựa trên phân tích
    """
    suggestions = []
    avg_score, avg_time, completed_exercises, correct_ratio = student_features
    
    if avg_score < 5.0:
        suggestions.append("Cần tập trung cải thiện điểm số qua các bài tập thêm")
    
    if avg_time < 30:
        suggestions.append("Nên dành thêm thời gian cho mỗi bài tập để nắm vững kiến thức")
    
    if completed_exercises < 10:
        suggestions.append("Cần hoàn thành thêm bài tập để tích lũy kinh nghiệm")
    
    if correct_ratio < 0.7:
        suggestions.append("Tập trung vào chất lượng bài làm để tăng tỷ lệ làm đúng")
    
    return suggestions

# Example usage
if __name__ == "__main__":
    # Load data
    student_data = pd.read_json("student_data.json")
    
    # Prepare features
    features = prepare_student_data(student_data)
    
    # Clustering
    clusters, cluster_labels, cluster_analysis = kmeans_clustering(features)
    
    # Initial classification using clustering results
    initial_labels = [cluster_labels[c] for c in clusters]
    
    # Train KNN model
    knn_model, scaler, train_acc, test_acc = knn_classification(features, initial_labels)
    
    print(f"Training accuracy: {train_acc:.2f}")
    print(f"Testing accuracy: {test_acc:.2f}")
    
    # Analyze a specific student
    student_features = features[0]  # Example with first student
    analysis = analyze_student(student_features, knn_model, scaler)
    suggestions = get_improvement_suggestions(student_features, analysis)
    
    print("\nStudent Analysis:")
    print(f"Predicted Level: {analysis['predicted_level']}")
    print(f"Confidence: {analysis['confidence']:.2f}")
    print("\nImprovement Suggestions:")
    for suggestion in suggestions:
        print(f"- {suggestion}")