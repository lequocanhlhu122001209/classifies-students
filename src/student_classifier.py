"""
Phân loại sinh viên bằng K-means + KNN:
- K-means phân cụm dựa trên điểm số + hành vi
- KNN dự đoán cho sinh viên mới
- Phát hiện bất thường (gian lận)
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import unicodedata
import warnings
warnings.filterwarnings('ignore')

COURSE_SKILLS = {
    "Nhập Môn Lập Trình": ["Biến và Kiểu dữ liệu", "Cấu trúc điều khiển", "Vòng lặp", "Hàm cơ bản"],
    "Kĩ Thuật Lập Trình": ["Mảng và xử lý mảng", "Con trỏ", "Chuỗi ký tự", "File I/O"],
    "Cấu trúc Dữ Liệu và Giải Thuật": ["Mảng (Arrays)", "Danh sách liên kết", "Stack và Queue", "Cây (Trees)"],
    "Lập Trình Hướng Đối Tượng": ["Lớp và Đối tượng", "Kế thừa", "Đa hình", "Đóng gói"]
}

COURSE_NAME_MAPPING = {
    "Cấu Trúc Dữ Liệu": "Cấu trúc Dữ Liệu và Giải Thuật",
    "Kỹ Thuật Lập Trình": "Kĩ Thuật Lập Trình"
}

COURSE_CODE_TO_NAME = {
    "NMLT": "Nhập Môn Lập Trình",
    "KTLT": "Kĩ Thuật Lập Trình",
    "CTDL": "Cấu trúc Dữ Liệu và Giải Thuật",
    "OOP": "Lập Trình Hướng Đối Tượng"
}


def _parse_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(" ", "").replace(",", ".")
    filtered = "".join(ch for ch in normalized if ch.isdigit() or ch in ".+-")
    if not filtered:
        return None

    try:
        return float(filtered)
    except (TypeError, ValueError):
        return None


def _normalize_text(value):
    if value is None:
        return ""

    text = str(value)
    normalized = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in no_accents.lower() if ch.isalnum())


def _is_placeholder_course_name(course_name):
    normalized = _normalize_text(course_name)
    if not normalized:
        return True
    return normalized in {"null", "none", "undefined", "unknown", "na", "nan"}


def _to_canonical_course_name(course_name):
    if not course_name:
        return None

    raw_name = str(course_name).strip()
    if not raw_name:
        return None

    if raw_name in COURSE_SKILLS:
        return raw_name

    mapped = COURSE_NAME_MAPPING.get(raw_name)
    if mapped in COURSE_SKILLS:
        return mapped

    code_mapped = COURSE_CODE_TO_NAME.get(raw_name.upper())
    if code_mapped in COURSE_SKILLS:
        return code_mapped

    normalized_raw = _normalize_text(raw_name)
    if not normalized_raw:
        return None

    for canonical_name in COURSE_SKILLS:
        aliases = [canonical_name]

        for alias, standard in COURSE_NAME_MAPPING.items():
            if standard == canonical_name:
                aliases.append(alias)
            if alias == canonical_name:
                aliases.append(standard)

        for code, standard in COURSE_CODE_TO_NAME.items():
            if standard == canonical_name:
                aliases.append(code)

        if any(_normalize_text(alias) == normalized_raw for alias in aliases):
            return canonical_name

    for canonical_name in COURSE_SKILLS:
        normalized_canonical = _normalize_text(canonical_name)
        if normalized_raw in normalized_canonical or normalized_canonical in normalized_raw:
            return canonical_name

    return None


def _extract_course_entries(courses):
    if not courses:
        return []

    entries = []
    if isinstance(courses, list):
        for index, course_data in enumerate(courses):
            if not isinstance(course_data, dict):
                continue
            entries.append({
                "raw_course_name": course_data.get("course_name") or course_data.get("course") or course_data.get("course_code") or course_data.get("name") or str(index),
                "original_key": str(index),
                "course_data": course_data
            })
        return entries

    if isinstance(courses, dict):
        for key, course_data in courses.items():
            if not isinstance(course_data, dict):
                continue
            entries.append({
                "raw_course_name": course_data.get("course_name") or course_data.get("course") or course_data.get("course_code") or course_data.get("name") or key,
                "original_key": key,
                "course_data": course_data
            })
        return entries

    return []


def _build_canonical_course_map(student):
    courses = student.get("courses", {}) if isinstance(student, dict) else {}
    entries = _extract_course_entries(courses)
    canonical_map = {}
    unmatched_entries = []

    for entry in entries:
        canonical = _to_canonical_course_name(entry["raw_course_name"]) or _to_canonical_course_name(entry["original_key"])
        if canonical and canonical not in canonical_map:
            canonical_map[canonical] = entry["course_data"]
        else:
            unmatched_entries.append(entry)

    canonical_names = list(COURSE_SKILLS.keys())

    if not canonical_map and len(entries) == len(canonical_names):
        for index, course_name in enumerate(canonical_names):
            canonical_map[course_name] = entries[index]["course_data"]
    elif unmatched_entries and len(entries) == len(canonical_names):
        missing_courses = [name for name in canonical_names if name not in canonical_map]
        if len(missing_courses) == len(unmatched_entries):
            for index, course_name in enumerate(missing_courses):
                canonical_map[course_name] = unmatched_entries[index]["course_data"]

    placeholder_entries = [
        entry for entry in entries
        if _is_placeholder_course_name(entry["raw_course_name"]) or _is_placeholder_course_name(entry["original_key"])
    ]

    if placeholder_entries:
        fallback_data = placeholder_entries[0].get("course_data")
        if isinstance(fallback_data, dict):
            if not canonical_map and len(entries) == 1:
                for course_name in canonical_names:
                    canonical_map[course_name] = fallback_data
            else:
                for course_name in canonical_names:
                    if course_name not in canonical_map:
                        canonical_map[course_name] = fallback_data

    return canonical_map

class StudentClassifier:
    def __init__(self, n_clusters=4, normalization_method='minmax'):
        self.n_clusters = n_clusters
        self.normalization_method = normalization_method
        self.scaler = MinMaxScaler() if normalization_method == 'minmax' else StandardScaler()
        self.kmeans = None
        self.knn = None
        self.cluster_labels = {}
    
    def _evaluate_skill(self, score, time_minutes, skill_name):
        """Đánh giá kỹ năng + phát hiện gian lận"""
        anomaly = False
        anomaly_reason = ""
        penalty = 0
        
        # Phát hiện gian lận: điểm cao + thời gian ngắn (ngưỡng nới lỏng hơn)
        # Chỉ cảnh báo khi thời gian CỰC ngắn so với điểm số
        if score >= 9.5 and time_minutes < 3:
            anomaly, penalty = True, 0.4
            anomaly_reason = f"Điểm {score}/10, thời gian {time_minutes:.0f}p (nghi gian lận)"
        elif score >= 9.0 and time_minutes < 5:
            anomaly, penalty = True, 0.25
            anomaly_reason = f"Điểm {score}/10, thời gian {time_minutes:.0f}p (đáng nghi)"
        elif score >= 8.5 and time_minutes < 8:
            anomaly, penalty = True, 0.1
            anomaly_reason = f"Điểm {score}/10, thời gian {time_minutes:.0f}p"
        
        skill_score = score * (1 - penalty)
        np.random.seed(hash(skill_name) % 2**32)
        skill_score = max(0, min(10, skill_score + np.random.uniform(-0.3, 0.3)))
        
        if skill_score >= 8.0: level = "Xuất sắc"
        elif skill_score >= 7.0: level = "Khá"
        elif skill_score >= 5.0: level = "Trung bình"
        else: level = "Yếu"
        
        return {"score": round(skill_score, 2), "level": level, "passed": skill_score >= 5.0,
                "anomaly": anomaly, "anomaly_reason": anomaly_reason}
    
    def evaluate_course_skills(self, student, course_name):
        """Đánh giá 4 kỹ năng của 1 môn học"""
        canonical_courses = _build_canonical_course_map(student)
        course_data = canonical_courses.get(course_name, {}) if isinstance(canonical_courses, dict) else {}

        score = _parse_number(
            course_data.get("score")
            if isinstance(course_data, dict)
            else None
        )
        if score is None and isinstance(course_data, dict):
            score = _parse_number(course_data.get("total_score"))
        if score is None and isinstance(course_data, dict):
            score = _parse_number(course_data.get("avg_score"))
        if score is None and isinstance(course_data, dict):
            score = _parse_number(course_data.get("course_score"))
        if score is None:
            score = 0.0

        time_minutes = _parse_number(
            course_data.get("time_minutes")
            if isinstance(course_data, dict)
            else None
        )
        if time_minutes is None and isinstance(course_data, dict):
            time_minutes = _parse_number(course_data.get("avg_time_minutes"))
        if time_minutes is None and isinstance(course_data, dict):
            time_minutes = _parse_number(course_data.get("time"))
        if time_minutes is None:
            time_minutes = 0.0
        
        skills = COURSE_SKILLS.get(course_name, [])
        skill_evaluations = {}
        for skill in skills:
            skill_evaluations[skill] = self._evaluate_skill(score, time_minutes, skill)
        
        skill_scores = [s["score"] for s in skill_evaluations.values()]
        return {
            "course_score": score, "time_minutes": time_minutes, "skills": skill_evaluations,
            "summary": {
                "avg_skill_score": round(np.mean(skill_scores), 2) if skill_scores else 0,
                "total_skills": len(skills),
                "passed_skills": sum(1 for s in skill_evaluations.values() if s["passed"]),
                "anomaly_skills": sum(1 for s in skill_evaluations.values() if s["anomaly"])
            }
        }

    def has_sufficient_data(self, student):
        """
        Kiểm tra sinh viên có đủ dữ liệu để phân loại không.
        Yêu cầu tối thiểu:
        - Có ít nhất 1 môn học với điểm > 0
        - Có thời gian làm bài > 0
        """
        courses = student.get("courses", {})
        csv_data = student.get("csv_data", {})
        
        # Kiểm tra có điểm môn học không
        has_course_score = False
        has_time = False
        
        for course_data in courses.values():
            if isinstance(course_data, dict):
                score = float(course_data.get("score", 0))
                time_mins = float(course_data.get("time_minutes", 0))
                if score > 0:
                    has_course_score = True
                if time_mins > 0:
                    has_time = True
        
        # Hoặc có điểm từ csv_data
        total_score = float(csv_data.get("total_score", 0))
        if total_score > 0:
            has_course_score = True
        
        return has_course_score and has_time
    
    def extract_features(self, students):
        """
        Trích xuất features để K-means phân cụm:
        - Điểm số (50%): điểm TB, giữa kỳ, cuối kỳ, bài tập từng môn
        - Hành vi (50%): tham gia, hành vi, chuyên cần, hoàn thành bài tập, thời gian làm bài
        Chỉ xử lý sinh viên có đủ dữ liệu.
        """
        features = []
        for student in students:
            csv_data = student.get("csv_data", {})
            courses = student.get("courses", {})
            
            # ĐIỂM SỐ - Tính từ các môn học
            course_scores = []
            course_midterms = []
            course_finals = []
            course_homeworks = []
            
            for course_data in courses.values():
                if isinstance(course_data, dict):
                    course_scores.append(float(course_data.get("score", 0)))
                    course_midterms.append(float(course_data.get("midterm_score", 0)))
                    course_finals.append(float(course_data.get("final_score", 0)))
                    course_homeworks.append(float(course_data.get("homework_score", 0)))
            
            # Tính trung bình
            total_score = sum(course_scores) / len(course_scores) if course_scores else float(csv_data.get("total_score", 0))
            midterm = sum(course_midterms) / len(course_midterms) if course_midterms else float(csv_data.get("midterm_score", 0))
            final = sum(course_finals) / len(course_finals) if course_finals else float(csv_data.get("final_score", 0))
            homework = sum(course_homeworks) / len(course_homeworks) if course_homeworks else 0
            
            # HÀNH VI
            attendance = float(csv_data.get("attendance_rate", 0))
            behavior = float(csv_data.get("behavior_score_100", 0)) / 100
            late_submissions = float(csv_data.get("late_submissions", 0))
            assignment = float(csv_data.get("assignment_completion", 0))
            
            # THỜI GIAN LÀM BÀI
            total_time = sum(float(c.get("time_minutes", 0)) for c in courses.values() if isinstance(c, dict))
            avg_time = total_time / len(courses) if courses else 0
            
            # Điểm chuyên cần (không nộp muộn = tốt)
            punctuality = max(0, 1.0 - (late_submissions / 10.0))
            
            # Điểm bất thường (điểm cao + thời gian ngắn = xấu) - Ngưỡng nới lỏng
            anomaly_score = 0
            if total_score >= 9.5 and avg_time < 30: anomaly_score = 1.0
            elif total_score >= 9.0 and avg_time < 60: anomaly_score = 0.6
            elif total_score >= 8.5 and avg_time < 90: anomaly_score = 0.3
            
            # Vector 12 features chuẩn hóa [0,1]
            features.append([
                total_score / 10.0,           # 1. Điểm TB các môn
                midterm / 10.0,               # 2. Điểm giữa kỳ TB
                final / 10.0,                 # 3. Điểm cuối kỳ TB
                homework / 10.0,              # 4. Điểm bài tập TB
                behavior,                     # 5. Điểm hành vi
                attendance,                   # 6. Tỷ lệ tham gia
                punctuality,                  # 7. Chuyên cần (không nộp muộn)
                assignment,                   # 8. Hoàn thành bài tập
                min(avg_time / 600, 1.0),     # 9. Thời gian làm bài
                1.0 - anomaly_score,          # 10. Điểm "sạch" (không bất thường)
                min(late_submissions / 10, 1.0),  # 11. Tỷ lệ nộp muộn
                # 12. Độ ổn định điểm (điểm các môn không chênh lệch nhiều)
                1.0 - (np.std(course_scores) / 5.0 if len(course_scores) > 1 else 0)
            ])
        return np.array(features)
    
    def normalize_features(self, features, fit=True):
        if fit: return self.scaler.fit_transform(features)
        return self.scaler.transform(features)

    def fit(self, students):
        """
        Training: K-means phân cụm -> Gán nhãn theo điểm tổng hợp -> KNN học
        CHỈ phân loại sinh viên có đủ dữ liệu (điểm + thời gian)
        """
        # Lọc sinh viên có đủ dữ liệu
        valid_students = [s for s in students if self.has_sufficient_data(s)]
        insufficient_count = len(students) - len(valid_students)
        
        print("=" * 60)
        print("K-MEANS + KNN: Phan loai dua tren DIEM SO + HANH VI")
        print("=" * 60)
        print(f"\n📊 Tong so sinh vien: {len(students)}")
        print(f"   ✅ Du du lieu de phan loai: {len(valid_students)}")
        if insufficient_count > 0:
            print(f"   ⚠️ Chua du du lieu: {insufficient_count} (bo qua)")
        
        if len(valid_students) < 4:
            print("   ❌ Khong du sinh vien de phan loai (can it nhat 4)")
            return
        
        features = self.extract_features(valid_students)
        features_normalized = self.normalize_features(features, fit=True)
        
        # Lưu lại danh sách sinh viên hợp lệ để dùng cho predict
        self.valid_student_ids = [s.get('student_id') for s in valid_students]
        
        # BƯỚC 1: K-means phân cụm
        print("\n[1] K-MEANS: Phan cum sinh vien...")
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(features_normalized)
        
        # Tính điểm tổng hợp cho mỗi cụm (50% điểm + 50% hành vi)
        cluster_stats = {}
        for i, cluster in enumerate(clusters):
            if cluster not in cluster_stats:
                cluster_stats[cluster] = []
            # Điểm tổng hợp = 50% điểm số + 50% hành vi
            composite = (
                # ĐIỂM SỐ (50%)
                features_normalized[i][0] * 0.15 +  # Điểm TB các môn
                features_normalized[i][1] * 0.10 +  # Giữa kỳ
                features_normalized[i][2] * 0.15 +  # Cuối kỳ (quan trọng)
                features_normalized[i][3] * 0.10 +  # Bài tập
                # HÀNH VI (50%)
                features_normalized[i][4] * 0.10 +  # Hành vi
                features_normalized[i][5] * 0.10 +  # Tham gia
                features_normalized[i][6] * 0.10 +  # Chuyên cần
                features_normalized[i][7] * 0.05 +  # Hoàn thành BT
                features_normalized[i][9] * 0.10 +  # Không bất thường
                features_normalized[i][11] * 0.05   # Độ ổn định điểm
            )
            cluster_stats[cluster].append(composite)
        
        # Tính điểm trung bình mỗi cụm
        cluster_means = {c: np.mean(scores) for c, scores in cluster_stats.items()}
        
        # Sắp xếp cụm theo điểm từ cao -> thấp
        sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
        
        # Gán nhãn theo thứ tự cụm (cụm cao nhất = Xuất sắc, ...)
        level_order = ["Xuat sac", "Kha", "Trung binh", "Yeu"]
        self.cluster_labels = {}
        
        print("\n   Ket qua phan cum:")
        for i, (cluster, mean_score) in enumerate(sorted_clusters):
            level = level_order[min(i, len(level_order) - 1)]
            self.cluster_labels[cluster] = level
            count = len(cluster_stats[cluster])
            print(f"   Cum {cluster}: diem TB = {mean_score:.3f} -> {level} ({count} SV)")
        
        # BƯỚC 2: Gán nhãn cho tất cả sinh viên theo K-means
        labels = [self.cluster_labels[c] for c in clusters]
        
        # Thống kê
        level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
        for label in labels: level_counts[label] += 1
        
        print("\n   Thong ke phan loai (chi tinh SV du du lieu):")
        for level, count in level_counts.items():
            pct = count / len(valid_students) * 100
            print(f"   {level}: {count} SV ({pct:.1f}%)")
        
        # BƯỚC 3: KNN học từ kết quả K-means
        print("\n[2] KNN: Hoc tu ket qua K-means...")
        if len(valid_students) >= 5:
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    features_normalized, labels, test_size=0.3, random_state=42, stratify=labels
                )
                k = max(1, min(5, len(X_train) // 10))
                self.knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
                self.knn.fit(X_train, y_train)
                acc = self.knn.score(X_test, y_test)
                print(f"   KNN: k={k}, accuracy={acc:.2%}")
            except:
                self.knn = KNeighborsClassifier(n_neighbors=3, weights='distance')
                self.knn.fit(features_normalized, labels)
                print("   KNN: fallback mode (k=3)")
        else:
            self.knn = None
            print("   KNN: khong du du lieu")
        
        print("=" * 60)

    def predict(self, students):
        """
        Dự đoán dựa trên điểm số + hành vi, có điều chỉnh theo bất thường.
        CHỈ phân loại sinh viên có đủ dữ liệu.
        """
        # Tách sinh viên có đủ dữ liệu và không đủ
        valid_students = []
        insufficient_students = []
        valid_indices = []
        
        for i, student in enumerate(students):
            if self.has_sufficient_data(student):
                valid_students.append(student)
                valid_indices.append(i)
            else:
                insufficient_students.append(student)
        
        # Nếu không có sinh viên hợp lệ
        if not valid_students:
            return [{
                **s,
                "kmeans_prediction": "Chua du du lieu",
                "knn_prediction": "Chua du du lieu", 
                "final_level": "Chua du du lieu",
                "anomaly_detected": False,
                "anomaly_reason": "Sinh viên chưa có đủ dữ liệu để phân loại",
                "anomaly_reasons": ["Chưa có điểm hoặc thời gian làm bài"],
                "insufficient_data": True
            } for s in students]
        
        features = self.extract_features(valid_students)
        features_normalized = self.normalize_features(features, fit=False)
        
        # Dự đoán K-means (tham khảo)
        kmeans_clusters = self.kmeans.predict(features_normalized)
        kmeans_predictions = [self.cluster_labels[c] for c in kmeans_clusters]
        
        # Dự đoán KNN (tham khảo)
        knn_predictions = self.knn.predict(features_normalized).tolist() if self.knn else kmeans_predictions
        
        # Tính điểm tổng hợp và phân loại theo ngưỡng (chỉ cho valid_students)
        composite_predictions = []
        for i, student in enumerate(valid_students):
            csv_data = student.get("csv_data", {})
            courses = student.get("courses", {})
            
            # Tính điểm từ các môn học
            course_scores = []
            course_midterms = []
            course_finals = []
            course_homeworks = []
            
            for course_data in courses.values():
                if isinstance(course_data, dict):
                    course_scores.append(float(course_data.get("score", 0)))
                    course_midterms.append(float(course_data.get("midterm_score", 0)))
                    course_finals.append(float(course_data.get("final_score", 0)))
                    course_homeworks.append(float(course_data.get("homework_score", 0)))
            
            # KIỂM TRA: Nếu có bất kỳ điểm nào = 0 → tự động phân loại Yếu
            has_zero_score = False
            zero_score_reason = []
            
            # Kiểm tra điểm các môn
            for idx, score in enumerate(course_scores):
                if score == 0:
                    has_zero_score = True
                    course_name = list(courses.keys())[idx] if idx < len(courses) else f"Môn {idx+1}"
                    zero_score_reason.append(f"Điểm môn {course_name} = 0")
            
            # Kiểm tra điểm giữa kỳ
            for idx, score in enumerate(course_midterms):
                if score == 0:
                    has_zero_score = True
                    course_name = list(courses.keys())[idx] if idx < len(courses) else f"Môn {idx+1}"
                    zero_score_reason.append(f"Điểm giữa kỳ {course_name} = 0")
            
            # Kiểm tra điểm cuối kỳ
            for idx, score in enumerate(course_finals):
                if score == 0:
                    has_zero_score = True
                    course_name = list(courses.keys())[idx] if idx < len(courses) else f"Môn {idx+1}"
                    zero_score_reason.append(f"Điểm cuối kỳ {course_name} = 0")
            
            # Kiểm tra điểm bài tập
            for idx, score in enumerate(course_homeworks):
                if score == 0:
                    has_zero_score = True
                    course_name = list(courses.keys())[idx] if idx < len(courses) else f"Môn {idx+1}"
                    zero_score_reason.append(f"Điểm bài tập {course_name} = 0")
            
            total_score = sum(course_scores) / len(course_scores) if course_scores else float(csv_data.get("total_score", 0))
            midterm_avg = sum(course_midterms) / len(course_midterms) if course_midterms else 0
            final_avg = sum(course_finals) / len(course_finals) if course_finals else 0
            homework_avg = sum(course_homeworks) / len(course_homeworks) if course_homeworks else 0
            
            behavior = float(csv_data.get("behavior_score_100", 50))
            attendance = float(csv_data.get("attendance_rate", 0.8))
            late_submissions = float(csv_data.get("late_submissions", 0))
            
            # Điểm tổng hợp = 50% điểm + 50% hành vi
            # Điểm số: 15% TB + 10% giữa kỳ + 15% cuối kỳ + 10% bài tập
            # Hành vi: 15% hành vi + 15% tham gia + 10% chuyên cần + 10% ổn định
            score_component = (
                total_score * 0.15 +
                midterm_avg * 0.10 +
                final_avg * 0.15 +
                homework_avg * 0.10
            )
            
            punctuality = max(0, 1.0 - (late_submissions / 10.0))
            stability = 1.0 - (np.std(course_scores) / 5.0 if len(course_scores) > 1 else 0)
            
            behavior_component = (
                (behavior / 100) * 10 * 0.15 +
                attendance * 10 * 0.15 +
                punctuality * 10 * 0.10 +
                stability * 10 * 0.10
            )
            
            composite = score_component + behavior_component
            
            # PHÂN LOẠI THEO ĐIỂM TỔNG HỢP (điểm số + hành vi)
            # Điểm tổng hợp tối đa = 5 (điểm) + 5 (hành vi) = 10
            
            # Trừ điểm nếu nộp trễ nhiều
            late_penalty = 0
            if late_submissions >= 20:
                late_penalty = 2.0
            elif late_submissions >= 15:
                late_penalty = 1.5
            elif late_submissions >= 10:
                late_penalty = 1.0
            elif late_submissions >= 5:
                late_penalty = 0.5
            
            # Trừ điểm nếu vắng nhiều
            attendance_penalty = 0
            if attendance < 0.4:
                attendance_penalty = 2.0  # Vắng > 60%: trừ 2 điểm
            elif attendance < 0.5:
                attendance_penalty = 1.5  # Vắng > 50%: trừ 1.5 điểm
            elif attendance < 0.6:
                attendance_penalty = 1.0  # Vắng > 40%: trừ 1 điểm
            elif attendance < 0.7:
                attendance_penalty = 0.5  # Vắng > 30%: trừ 0.5 điểm
            
            # Trừ điểm nếu thời gian học quá ngắn so với điểm số
            time_hours = sum(float(c.get("time_minutes", 0)) for c in courses.values() if isinstance(c, dict)) / 60
            time_penalty = 0
            if total_score >= 8.0 and time_hours < 5:
                time_penalty = 1.5  # Điểm cao + thời gian ngắn
            elif total_score >= 8.0 and time_hours < 8:
                time_penalty = 0.5
            
            # Điểm cuối cùng sau khi trừ penalty
            total_penalty = late_penalty + attendance_penalty + time_penalty
            final_composite = max(0, composite - total_penalty)
            
            # Phân loại theo điểm tổng hợp (thang 10)
            # >= 8: Xuất sắc | 7-7.9: Khá | 5-6.9: Trung bình | < 5: Yếu
            if final_composite >= 8.0:
                level = "Xuat sac"
            elif final_composite >= 7.0:
                level = "Kha"
            elif final_composite >= 5.0:
                level = "Trung binh"
            else:
                level = "Yeu"
            
            composite_predictions.append(level)
        
        # Xử lý kết quả cho valid_students
        valid_results = []
        for i, student in enumerate(valid_students):
            csv_data = student.get("csv_data", {})
            courses = student.get("courses", {})
            
            total_score = float(csv_data.get("total_score", 0))
            late_submissions = float(csv_data.get("late_submissions", 0))
            attendance = float(csv_data.get("attendance_rate", 0))
            behavior = float(csv_data.get("behavior_score_100", 0))
            
            # Đánh giá kỹ năng từng môn
            skill_evaluations = {}
            for course_name in COURSE_SKILLS.keys():
                skill_evaluations[course_name] = self.evaluate_course_skills(student, course_name)
            
            # Tính thời gian làm bài
            total_time = sum(float(c.get("time_minutes", 0)) for c in courses.values() if isinstance(c, dict))
            avg_time = total_time / len(courses) if courses else 0
            
            # Tính điểm trung bình từ các môn học
            course_scores = [float(c.get("score", 0)) for c in courses.values() if isinstance(c, dict)]
            avg_course_score = sum(course_scores) / len(course_scores) if course_scores else total_score
            
            # Tính thời gian theo giờ
            time_hours = total_time / 60
            
            # PHÁT HIỆN BẤT THƯỜNG - Dựa trên mối quan hệ điểm-thời gian-hành vi
            anomaly_detected = False
            anomaly_reasons = []
            anomaly_severity = 0
            
            # Tính tỷ lệ hiệu quả (efficiency ratio) = điểm / thời gian
            # Sinh viên bình thường: ~0.8-1.2 điểm/giờ
            # Nghi ngờ: > 1.5 điểm/giờ với điểm >= 8
            efficiency_ratio = avg_course_score / time_hours if time_hours > 0 else 999
            
            # 1. Điểm cao + thời gian quá ngắn (nghi gian lận/dùng AI)
            if avg_course_score >= 8.5 and time_hours < 5:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 3)
                anomaly_reasons.append(f"Điểm {avg_course_score:.1f}/10 nhưng thời gian chỉ {time_hours:.1f}h (nghi gian lận)")
            elif avg_course_score >= 8.0 and time_hours < 4:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 3)
                anomaly_reasons.append(f"Điểm {avg_course_score:.1f}/10 nhưng thời gian chỉ {time_hours:.1f}h (đáng nghi)")
            # MỚI: Phát hiện dựa trên tỷ lệ hiệu quả bất thường
            elif avg_course_score >= 8.0 and efficiency_ratio > 1.5:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 2)
                anomaly_reasons.append(f"Tỷ lệ điểm/thời gian cao bất thường ({efficiency_ratio:.1f} điểm/h) - cần xem xét")
            
            # 2. Điểm cao + vắng nhiều (nghi gian lận) - QUAN TRỌNG
            if avg_course_score >= 8.0 and attendance < 0.5:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 3)
                anomaly_reasons.append(f"Điểm cao ({avg_course_score:.1f}/10) nhưng vắng {(1-attendance)*100:.0f}% (nghi gian lận)")
            elif avg_course_score >= 8.0 and attendance < 0.7:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 2)
                anomaly_reasons.append(f"Điểm cao ({avg_course_score:.1f}/10) nhưng vắng {(1-attendance)*100:.0f}%")
            
            # 3. Điểm cao + thời gian ngắn + vắng nhiều = RẤT ĐÁNG NGỜ
            if avg_course_score >= 8.0 and time_hours < 6 and attendance < 0.7:
                anomaly_severity = max(anomaly_severity, 3)
                if not any("nghi gian lận" in r for r in anomaly_reasons):
                    anomaly_reasons.append(f"Kết hợp: điểm cao + thời gian ngắn + vắng nhiều (rất đáng ngờ)")
            
            # 4. Nộp muộn nhiều - phạt theo mức độ
            if late_submissions >= 20:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 3)
                anomaly_reasons.append(f"Nộp muộn quá nhiều ({int(late_submissions)} lần)")
            elif late_submissions >= 15:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 3)
                anomaly_reasons.append(f"Nộp muộn rất nhiều ({int(late_submissions)} lần)")
            elif late_submissions >= 10:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 2)
                anomaly_reasons.append(f"Nộp muộn nhiều ({int(late_submissions)} lần)")
            elif late_submissions >= 5:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 1)
                anomaly_reasons.append(f"Nộp muộn {int(late_submissions)} lần")
            
            # 5. Vắng rất nhiều (< 50%)
            if attendance < 0.5:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 2)
                if not any("vắng" in r.lower() for r in anomaly_reasons):
                    anomaly_reasons.append(f"Tham gia chỉ {attendance*100:.0f}%")
            
            # 5. Điểm thấp nhưng chăm chỉ (cần hỗ trợ)
            if avg_course_score < 5.0 and behavior >= 85 and attendance >= 0.95:
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 1)
                anomaly_reasons.append(f"Điểm thấp ({avg_course_score:.1f}) nhưng rất chăm chỉ - cần hỗ trợ")
            
            # Sử dụng phân loại theo điểm tổng hợp
            final_level = composite_predictions[i]
            level_order = ["Xuat sac", "Kha", "Trung binh", "Yeu"]
            
            # KIỂM TRA ƯU TIÊN: Nếu có điểm = 0 → tự động Yếu
            if has_zero_score:
                final_level = "Yeu"
                anomaly_detected = True
                anomaly_severity = max(anomaly_severity, 3)
                for reason in zero_score_reason:
                    if reason not in anomaly_reasons:
                        anomaly_reasons.append(reason)
            
            # ĐIỀU CHỈNH XẾP LOẠI theo bất thường (chỉ áp dụng nếu chưa bị hạ do điểm 0)
            # Severity 1: hạ 1 bậc (nộp muộn 5-9 lần, vắng nhẹ)
            # Severity 2: hạ 2 bậc (nộp muộn 10-14 lần, vắng nhiều)
            # Severity 3: hạ xuống Yếu (nghi gian lận, nộp muộn >= 15)
            elif anomaly_detected and anomaly_severity >= 1:
                current_idx = level_order.index(final_level) if final_level in level_order else 0
                
                if anomaly_severity >= 3:
                    # Nghiêm trọng: hạ xuống Yếu
                    new_idx = 3
                elif anomaly_severity >= 2:
                    # Trung bình: hạ 2 bậc
                    new_idx = min(current_idx + 2, 3)
                else:
                    # Nhẹ: hạ 1 bậc
                    new_idx = min(current_idx + 1, 3)
                
                final_level = level_order[new_idx]
            
            valid_results.append({
                **student,
                "kmeans_prediction": kmeans_predictions[i],
                "knn_prediction": knn_predictions[i],
                "final_level": final_level,
                "skill_evaluations": skill_evaluations,
                "anomaly_detected": anomaly_detected,
                "anomaly_reason": " | ".join(anomaly_reasons),
                "anomaly_reasons": anomaly_reasons,
                "anomaly_severity": anomaly_severity,
                "insufficient_data": False,
                "detailed_scores": {
                    "total_score": total_score,
                    "midterm_score": float(csv_data.get("midterm_score", 0)),
                    "final_score": float(csv_data.get("final_score", 0)),
                    "attendance_rate": attendance * 100,
                    "behavior_score": behavior,
                    "late_submissions": int(late_submissions),
                    "avg_time_minutes": avg_time
                }
            })
        
        # Thêm kết quả cho sinh viên không đủ dữ liệu
        insufficient_results = []
        for student in insufficient_students:
            insufficient_results.append({
                **student,
                "kmeans_prediction": "Chua du du lieu",
                "knn_prediction": "Chua du du lieu",
                "final_level": "Chua du du lieu",
                "skill_evaluations": {},
                "anomaly_detected": False,
                "anomaly_reason": "Sinh viên chưa có đủ dữ liệu để phân loại",
                "anomaly_reasons": ["Chưa có điểm hoặc thời gian làm bài"],
                "anomaly_severity": 0,
                "insufficient_data": True,
                "detailed_scores": {}
            })
        
        # Kết hợp kết quả theo thứ tự ban đầu
        all_results = []
        valid_idx = 0
        insuff_idx = 0
        for i, student in enumerate(students):
            if i in valid_indices:
                all_results.append(valid_results[valid_idx])
                valid_idx += 1
            else:
                all_results.append(insufficient_results[insuff_idx])
                insuff_idx += 1
        
        return all_results

    def analyze_student_skills(self, student):
        """Phân tích chi tiết kỹ năng yếu/mạnh của sinh viên"""
        skill_evaluations = {}
        for course_name in COURSE_SKILLS.keys():
            skill_evaluations[course_name] = self.evaluate_course_skills(student, course_name)
        
        strong_skills = []
        weak_skills = []
        need_improvement = []
        course_analysis = {}
        
        for course_name, course_eval in skill_evaluations.items():
            course_strong, course_weak, course_improve = [], [], []
            
            for skill_name, skill_data in course_eval["skills"].items():
                skill_info = {
                    "course": course_name, "skill": skill_name,
                    "score": skill_data["score"], "level": skill_data["level"],
                    "anomaly": skill_data["anomaly"], "anomaly_reason": skill_data["anomaly_reason"]
                }
                
                if skill_data["score"] >= 8.0:
                    strong_skills.append(skill_info)
                    course_strong.append(skill_name)
                elif skill_data["score"] < 5.0:
                    weak_skills.append(skill_info)
                    course_weak.append(skill_name)
                elif skill_data["score"] < 7.0:
                    need_improvement.append(skill_info)
                    course_improve.append(skill_name)
            
            avg_score = course_eval["summary"]["avg_skill_score"]
            if avg_score >= 8.0: course_level = "Xuất sắc"
            elif avg_score >= 7.0: course_level = "Khá"
            elif avg_score >= 5.0: course_level = "Trung bình"
            else: course_level = "Yếu"
            
            course_analysis[course_name] = {
                "avg_score": avg_score, "level": course_level,
                "time_minutes": course_eval["time_minutes"],
                "strong_skills": course_strong, "weak_skills": course_weak,
                "need_improvement": course_improve,
                "passed_skills": course_eval["summary"]["passed_skills"],
                "total_skills": course_eval["summary"]["total_skills"],
                "anomaly_count": course_eval["summary"]["anomaly_skills"]
            }
        
        recommendations = self._generate_recommendations(weak_skills, need_improvement, course_analysis)
        
        all_scores = [s["score"] for s in strong_skills + weak_skills + need_improvement]
        overall_skill_score = np.mean(all_scores) if all_scores else 0
        
        if overall_skill_score >= 8.0: overall_level = "Xuất sắc"
        elif overall_skill_score >= 7.0: overall_level = "Khá"
        elif overall_skill_score >= 5.0: overall_level = "Trung bình"
        else: overall_level = "Yếu"
        
        return {
            "student_id": student.get("student_id"), "name": student.get("name"),
            "overall_skill_score": round(overall_skill_score, 2), "overall_level": overall_level,
            "total_skills": len(all_scores),
            "strong_skills_count": len(strong_skills), "weak_skills_count": len(weak_skills),
            "strong_skills": sorted(strong_skills, key=lambda x: x["score"], reverse=True),
            "weak_skills": sorted(weak_skills, key=lambda x: x["score"]),
            "need_improvement": sorted(need_improvement, key=lambda x: x["score"]),
            "course_analysis": course_analysis, "recommendations": recommendations
        }
    
    def _generate_recommendations(self, weak_skills, need_improvement, course_analysis):
        """Tạo đề xuất cải thiện"""
        recommendations = []
        
        if weak_skills:
            for course in set(s["course"] for s in weak_skills):
                skills = [s["skill"] for s in weak_skills if s["course"] == course]
                recommendations.append({
                    "priority": "Cao", "type": "Kỹ năng yếu", "course": course, "skills": skills,
                    "message": f"Cần tập trung ôn luyện {', '.join(skills)} trong môn {course}"
                })
        
        if need_improvement:
            for course in set(s["course"] for s in need_improvement):
                skills = [s["skill"] for s in need_improvement if s["course"] == course]
                recommendations.append({
                    "priority": "Trung bình", "type": "Cần cải thiện", "course": course, "skills": skills,
                    "message": f"Nên củng cố thêm {', '.join(skills)} trong môn {course}"
                })
        
        for course_name, analysis in course_analysis.items():
            if analysis["anomaly_count"] > 0:
                recommendations.append({
                    "priority": "Cảnh báo", "type": "Bất thường", "course": course_name, "skills": [],
                    "message": f"Phát hiện {analysis['anomaly_count']} kỹ năng bất thường trong môn {course_name}"
                })
        
        if not weak_skills and not need_improvement:
            recommendations.append({
                "priority": "Thấp", "type": "Duy trì", "course": "Tất cả", "skills": [],
                "message": "Tiếp tục duy trì phong độ học tập tốt!"
            })
        
        return recommendations
