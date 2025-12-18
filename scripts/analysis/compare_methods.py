"""
So sánh 3 phương pháp phân loại:
1. K-means (phân cụm không giám sát)
2. KNN (phân loại có giám sát)
3. K-means + KNN (kết hợp)
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from data_generator import StudentDataGenerator

def extract_features(students):
    """Trích xuất features từ sinh viên"""
    features = []
    for student in students:
        csv_data = student.get("csv_data", {})
        courses = student.get("courses", {})
        
        total_score = float(csv_data.get("total_score", 0))
        midterm = float(csv_data.get("midterm_score", 0))
        final = float(csv_data.get("final_score", 0))
        attendance = float(csv_data.get("attendance_rate", 0))
        behavior = float(csv_data.get("behavior_score_100", 0)) / 100
        late_submissions = float(csv_data.get("late_submissions", 0))
        assignment = float(csv_data.get("assignment_completion", 0))
        
        total_time = sum(float(c.get("time_minutes", 0)) for c in courses.values() if isinstance(c, dict))
        avg_time = total_time / len(courses) if courses else 0
        punctuality = max(0, 1.0 - (late_submissions / 10.0))
        
        features.append([
            total_score / 10.0, midterm / 10.0, final / 10.0,
            behavior, attendance, punctuality, assignment,
            min(avg_time / 600, 1.0)
        ])
    return np.array(features)

def get_true_labels(students):
    """Lấy nhãn thực tế dựa trên điểm số"""
    labels = []
    for student in students:
        score = float(student.get("csv_data", {}).get("total_score", 0))
        if score >= 8.0: labels.append("Xuat sac")
        elif score >= 7.0: labels.append("Kha")
        elif score >= 5.0: labels.append("Trung binh")
        else: labels.append("Yeu")
    return labels

def method_kmeans_only(features_normalized, n_clusters=4):
    """Phương pháp 1: Chỉ dùng K-means"""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(features_normalized)
    
    # Tính điểm TB mỗi cụm
    cluster_means = {}
    for i, c in enumerate(clusters):
        if c not in cluster_means:
            cluster_means[c] = []
        cluster_means[c].append(features_normalized[i][0])  # Dùng điểm tổng
    
    cluster_means = {c: np.mean(scores) for c, scores in cluster_means.items()}
    sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
    
    level_order = ["Xuat sac", "Kha", "Trung binh", "Yeu"]
    cluster_labels = {}
    for i, (c, _) in enumerate(sorted_clusters):
        cluster_labels[c] = level_order[min(i, 3)]
    
    predictions = [cluster_labels[c] for c in clusters]
    return predictions, kmeans

def method_knn_only(features_normalized, true_labels):
    """Phương pháp 2: Chỉ dùng KNN (supervised)"""
    X_train, X_test, y_train, y_test = train_test_split(
        features_normalized, true_labels, test_size=0.3, random_state=42, stratify=true_labels
    )
    
    knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
    knn.fit(X_train, y_train)
    
    # Dự đoán trên toàn bộ dữ liệu
    predictions = knn.predict(features_normalized)
    test_accuracy = knn.score(X_test, y_test)
    
    return predictions.tolist(), knn, test_accuracy

def method_kmeans_knn(features_normalized, n_clusters=4):
    """Phương pháp 3: K-means + KNN"""
    # Bước 1: K-means phân cụm
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(features_normalized)
    
    # Gán nhãn cho cụm
    cluster_stats = {}
    for i, c in enumerate(clusters):
        if c not in cluster_stats:
            cluster_stats[c] = []
        # Điểm tổng hợp
        composite = (
            features_normalized[i][0] * 0.4 +  # Điểm
            features_normalized[i][3] * 0.2 +  # Hành vi
            features_normalized[i][4] * 0.2 +  # Tham gia
            features_normalized[i][5] * 0.2    # Chuyên cần
        )
        cluster_stats[c].append(composite)
    
    cluster_means = {c: np.mean(scores) for c, scores in cluster_stats.items()}
    sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
    
    level_order = ["Xuat sac", "Kha", "Trung binh", "Yeu"]
    cluster_labels = {}
    for i, (c, _) in enumerate(sorted_clusters):
        cluster_labels[c] = level_order[min(i, 3)]
    
    kmeans_labels = [cluster_labels[c] for c in clusters]
    
    # Bước 2: KNN học từ K-means
    X_train, X_test, y_train, y_test = train_test_split(
        features_normalized, kmeans_labels, test_size=0.3, random_state=42, stratify=kmeans_labels
    )
    
    knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
    knn.fit(X_train, y_train)
    
    predictions = knn.predict(features_normalized)
    test_accuracy = knn.score(X_test, y_test)
    
    return predictions.tolist(), kmeans, knn, test_accuracy

def compare_methods():
    print("=" * 80)
    print("SO SÁNH 3 PHƯƠNG PHÁP PHÂN LOẠI SINH VIÊN")
    print("=" * 80)
    
    # Load dữ liệu
    print("\n📊 Đang tải dữ liệu...")
    generator = StudentDataGenerator(seed=42, csv_path='student_classification_supabase_ready_final.csv')
    students = generator.load_all_students()
    print(f"   Đã tải {len(students)} sinh viên")
    
    # Trích xuất features
    features = extract_features(students)
    scaler = MinMaxScaler()
    features_normalized = scaler.fit_transform(features)
    
    # Lấy nhãn thực tế
    true_labels = get_true_labels(students)
    
    print("\n" + "=" * 80)
    print("PHƯƠNG PHÁP 1: CHỈ DÙNG K-MEANS (Không giám sát)")
    print("=" * 80)
    kmeans_pred, _ = method_kmeans_only(features_normalized)
    
    kmeans_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    for p in kmeans_pred: kmeans_counts[p] += 1
    
    print("\n📈 Kết quả phân loại K-means:")
    for level, count in kmeans_counts.items():
        pct = count / len(students) * 100
        print(f"   {level:15s}: {count:3d} SV ({pct:5.1f}%)")
    
    # So sánh với nhãn thực tế
    kmeans_match = sum(1 for i in range(len(students)) if kmeans_pred[i] == true_labels[i])
    kmeans_accuracy = kmeans_match / len(students) * 100
    print(f"\n   Độ chính xác so với nhãn thực tế: {kmeans_accuracy:.1f}%")
    
    print("\n" + "=" * 80)
    print("PHƯƠNG PHÁP 2: CHỈ DÙNG KNN (Có giám sát)")
    print("=" * 80)
    knn_pred, _, knn_test_acc = method_knn_only(features_normalized, true_labels)
    
    knn_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    for p in knn_pred: knn_counts[p] += 1
    
    print("\n📈 Kết quả phân loại KNN:")
    for level, count in knn_counts.items():
        pct = count / len(students) * 100
        print(f"   {level:15s}: {count:3d} SV ({pct:5.1f}%)")
    
    knn_match = sum(1 for i in range(len(students)) if knn_pred[i] == true_labels[i])
    knn_accuracy = knn_match / len(students) * 100
    print(f"\n   Độ chính xác trên tập test: {knn_test_acc*100:.1f}%")
    print(f"   Độ chính xác tổng thể: {knn_accuracy:.1f}%")
    
    print("\n" + "=" * 80)
    print("PHƯƠNG PHÁP 3: K-MEANS + KNN (Kết hợp)")
    print("=" * 80)
    combined_pred, _, _, combined_test_acc = method_kmeans_knn(features_normalized)
    
    combined_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    for p in combined_pred: combined_counts[p] += 1
    
    print("\n📈 Kết quả phân loại K-means + KNN:")
    for level, count in combined_counts.items():
        pct = count / len(students) * 100
        print(f"   {level:15s}: {count:3d} SV ({pct:5.1f}%)")
    
    combined_match = sum(1 for i in range(len(students)) if combined_pred[i] == true_labels[i])
    combined_accuracy = combined_match / len(students) * 100
    print(f"\n   Độ chính xác KNN trên tập test: {combined_test_acc*100:.1f}%")
    print(f"   Độ chính xác tổng thể: {combined_accuracy:.1f}%")
    
    # BẢNG SO SÁNH
    print("\n" + "=" * 80)
    print("BẢNG SO SÁNH TỔNG HỢP")
    print("=" * 80)
    
    print("\n┌─────────────────────┬───────────┬───────────┬───────────┬───────────┐")
    print("│ Phương pháp         │ Xuất sắc  │ Khá       │ Trung bình│ Yếu       │")
    print("├─────────────────────┼───────────┼───────────┼───────────┼───────────┤")
    print(f"│ K-means             │ {kmeans_counts['Xuat sac']:4d} ({kmeans_counts['Xuat sac']/len(students)*100:4.1f}%)│ {kmeans_counts['Kha']:4d} ({kmeans_counts['Kha']/len(students)*100:4.1f}%)│ {kmeans_counts['Trung binh']:4d} ({kmeans_counts['Trung binh']/len(students)*100:4.1f}%) │ {kmeans_counts['Yeu']:4d} ({kmeans_counts['Yeu']/len(students)*100:4.1f}%)│")
    print(f"│ KNN                 │ {knn_counts['Xuat sac']:4d} ({knn_counts['Xuat sac']/len(students)*100:4.1f}%)│ {knn_counts['Kha']:4d} ({knn_counts['Kha']/len(students)*100:4.1f}%)│ {knn_counts['Trung binh']:4d} ({knn_counts['Trung binh']/len(students)*100:4.1f}%) │ {knn_counts['Yeu']:4d} ({knn_counts['Yeu']/len(students)*100:4.1f}%)│")
    print(f"│ K-means + KNN       │ {combined_counts['Xuat sac']:4d} ({combined_counts['Xuat sac']/len(students)*100:4.1f}%)│ {combined_counts['Kha']:4d} ({combined_counts['Kha']/len(students)*100:4.1f}%)│ {combined_counts['Trung binh']:4d} ({combined_counts['Trung binh']/len(students)*100:4.1f}%) │ {combined_counts['Yeu']:4d} ({combined_counts['Yeu']/len(students)*100:4.1f}%)│")
    print("└─────────────────────┴───────────┴───────────┴───────────┴───────────┘")
    
    print("\n┌─────────────────────┬─────────────────┐")
    print("│ Phương pháp         │ Độ chính xác    │")
    print("├─────────────────────┼─────────────────┤")
    print(f"│ K-means             │ {kmeans_accuracy:6.1f}%         │")
    print(f"│ KNN                 │ {knn_accuracy:6.1f}%         │")
    print(f"│ K-means + KNN       │ {combined_accuracy:6.1f}%         │")
    print("└─────────────────────┴─────────────────┘")
    
    print("\n" + "=" * 80)
    print("NHẬN XÉT")
    print("=" * 80)
    print("""
    1. K-MEANS (Không giám sát):
       - Tự động phân cụm dựa trên đặc điểm dữ liệu
       - Không cần nhãn trước
       - Phù hợp khi chưa biết phân loại
    
    2. KNN (Có giám sát):
       - Học từ nhãn thực tế (điểm số)
       - Độ chính xác cao hơn
       - Cần có dữ liệu đã gán nhãn
    
    3. K-MEANS + KNN (Kết hợp):
       - K-means phân cụm dựa trên điểm + hành vi
       - KNN học từ kết quả K-means
       - Cân bằng giữa điểm số và hành vi
       - Phát hiện được sinh viên điểm cao nhưng hành vi xấu
    """)

if __name__ == "__main__":
    compare_methods()
