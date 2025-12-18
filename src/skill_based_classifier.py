"""
He thong phan loai sinh vien theo ki nang cu the cho tung mon hoc
Ket hop K-means + KNN + Phat hien bat thuong
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
import random


# DINH NGHIA KI NANG CHO TUNG MON HOC
COURSE_SKILLS = {
    "Nhap Mon Lap Trinh": {
        "skills": [
            "Bien va Kieu Du Lieu",      # Bien, int, float, string
            "Cau Truc Dieu Khien",       # if-else, switch-case
            "Vong Lap",                  # for, while, do-while
            "Ham Co Ban"                 # Dinh nghia ham, tham so, return
        ],
        "weight": 0.2  # Trong so mon hoc
    },
    "Ki Thuat Lap Trinh": {
        "skills": [
            "Xu Ly Mang",               # Mang 1 chieu, 2 chieu
            "Con Tro",                  # Pointer, tham chieu
            "Chuoi Ky Tu",              # String manipulation
            "File I/O"                  # Doc/ghi file
        ],
        "weight": 0.25
    },
    "Cau Truc Du Lieu va Giai Thuat": {
        "skills": [
            "Mang va Danh Sach",        # Array, ArrayList
            "Danh Sach Lien Ket",       # Linked List
            "Stack va Queue",           # Ngan xep, hang doi
            "Cay (Trees)"               # Binary Tree, BST
        ],
        "weight": 0.3
    },
    "Lap Trinh Huong Doi Tuong": {
        "skills": [
            "Lop va Doi Tuong",         # Class, Object
            "Ke Thua",                  # Inheritance
            "Da Hinh",                  # Polymorphism
            "Truu Tuong"                # Abstraction, Interface
        ],
        "weight": 0.25
    }
}


class SkillBasedClassifier:
    """
    Phan loai sinh vien dua tren ki nang cu the
    """
    
    def __init__(self, normalization_method='minmax'):
        self.normalization_method = normalization_method
        self.scaler = MinMaxScaler()
        self.kmeans = None
        self.knn = None
        self.cluster_labels = {}
        
    def generate_skill_scores(self, student, course_name):
        """
        Gia lap diem ki nang cho sinh vien
        
        NOTE: GIA LAP DIEM KI NANG
        ==========================
        - Dua tren diem tong mon hoc
        - Co bien dong ngau nhien
        - Phat hien bat thuong: diem cao + thoi gian ngan
        """
        csv_data = student.get("csv_data", {})
        total_score = float(csv_data.get("total_score", 7.0))
        study_hours = float(csv_data.get("study_hours_per_week", 20))
        
        # Kiem tra bat thuong
        is_anomaly = False
        if total_score >= 9.0 and study_hours < 15:
            is_anomaly = True
        elif total_score >= 8.0 and study_hours < 20:
            is_anomaly = True
        
        skills = COURSE_SKILLS.get(course_name, {}).get("skills", [])
        skill_scores = {}
        
        for skill in skills:
            # Diem ki nang dao dong quanh diem tong
            base_score = total_score
            
            # Them bien dong ngau nhien
            variation = random.uniform(-1.5, 1.5)
            skill_score = base_score + variation
            
            # Neu phat hien bat thuong, giam diem ki nang
            if is_anomaly:
                skill_score = skill_score * random.uniform(0.5, 0.8)
            
            # Gioi han trong khoang [0, 10]
            skill_score = max(0, min(10, skill_score))
            
            skill_scores[skill] = round(skill_score, 1)
        
        return skill_scores, is_anomaly
    
    def classify_skill_level(self, skill_score):
        """
        Phan loai muc do ki nang
        
        NOTE: QUY TAC PHAN LOAI KI NANG
        ================================
        - Xuat sac: >= 8.5
        - Kha: >= 7.0
        - Trung binh: >= 5.5
        - Yeu: < 5.5
        """
        if skill_score >= 8.5:
            return "Xuat sac"
        elif skill_score >= 7.0:
            return "Kha"
        elif skill_score >= 5.5:
            return "Trung binh"
        else:
            return "Yeu"
    
    def evaluate_course_skills(self, student, course_name):
        """
        Danh gia ki nang cho 1 mon hoc
        
        Returns:
            dict: {
                'skills': {skill_name: score},
                'skill_levels': {skill_name: level},
                'average_skill_score': float,
                'overall_skill_level': str,
                'weak_skills': [skill_name],
                'strong_skills': [skill_name],
                'is_anomaly': bool
            }
        """
        skill_scores, is_anomaly = self.generate_skill_scores(student, course_name)
        
        # Phan loai tung ki nang
        skill_levels = {}
        for skill, score in skill_scores.items():
            skill_levels[skill] = self.classify_skill_level(score)
        
        # Tinh diem trung binh ki nang
        avg_skill_score = np.mean(list(skill_scores.values()))
        overall_skill_level = self.classify_skill_level(avg_skill_score)
        
        # Xac dinh ki nang yeu va manh
        weak_skills = [skill for skill, score in skill_scores.items() if score < 5.5]
        strong_skills = [skill for skill, score in skill_scores.items() if score >= 8.5]
        
        return {
            'skills': skill_scores,
            'skill_levels': skill_levels,
            'average_skill_score': round(avg_skill_score, 2),
            'overall_skill_level': overall_skill_level,
            'weak_skills': weak_skills,
            'strong_skills': strong_skills,
            'is_anomaly': is_anomaly
        }
    
    def evaluate_all_courses(self, student):
        """
        Danh gia ki nang cho tat ca cac mon hoc
        """
        all_evaluations = {}
        
        for course_name in COURSE_SKILLS.keys():
            evaluation = self.evaluate_course_skills(student, course_name)
            all_evaluations[course_name] = evaluation
        
        return all_evaluations
    
    def extract_features_from_skills(self, students):
        """
        Trich xuat dac trung tu danh gia ki nang
        
        NOTE: DAC TRUNG TU KI NANG
        ===========================
        - Diem trung binh tung mon
        - Diem trung binh tung ki nang
        - So ki nang yeu
        - So ki nang manh
        - Ty le ki nang dat
        - Phat hien bat thuong
        """
        features = []
        
        for student in students:
            csv_data = student.get("csv_data", {})
            
            # Danh gia ki nang
            skill_evaluations = self.evaluate_all_courses(student)
            
            # Tinh cac dac trung
            course_avg_scores = []
            all_skill_scores = []
            weak_skill_count = 0
            strong_skill_count = 0
            anomaly_count = 0
            
            for course_name, evaluation in skill_evaluations.items():
                course_avg_scores.append(evaluation['average_skill_score'])
                all_skill_scores.extend(evaluation['skills'].values())
                weak_skill_count += len(evaluation['weak_skills'])
                strong_skill_count += len(evaluation['strong_skills'])
                if evaluation['is_anomaly']:
                    anomaly_count += 1
            
            # Tinh diem tong hop
            overall_avg = np.mean(course_avg_scores)
            skill_std = np.std(all_skill_scores)
            pass_rate = sum(1 for s in all_skill_scores if s >= 5.5) / len(all_skill_scores)
            
            # Cac chi so khac
            total_score = float(csv_data.get("total_score", 0))
            study_hours = float(csv_data.get("study_hours_per_week", 0))
            attendance = float(csv_data.get("attendance_rate", 0))
            behavior = float(csv_data.get("behavior_score_100", 0)) / 100
            
            # Vector dac trung (12 features)
            feature_vector = [
                overall_avg / 10.0,              # 1. Diem TB ki nang tong hop
                total_score / 10.0,              # 2. Diem tong mon hoc
                pass_rate,                       # 3. Ty le ki nang dat
                weak_skill_count / 16.0,         # 4. Ty le ki nang yeu (16 ki nang tong)
                strong_skill_count / 16.0,       # 5. Ty le ki nang manh
                min(study_hours / 50.0, 1.0),    # 6. Gio hoc
                attendance,                      # 7. Tham gia
                behavior,                        # 8. Hanh vi
                min(skill_std / 5.0, 1.0),       # 9. Do lech chuan ki nang
                anomaly_count / 4.0,             # 10. Ty le bat thuong
                max(course_avg_scores) / 10.0,   # 11. Diem ki nang cao nhat
                min(course_avg_scores) / 10.0    # 12. Diem ki nang thap nhat
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def fit(self, students):
        """
        Huan luyen K-means + KNN dua tren ki nang
        """
        print("\nDang trich xuat dac trung tu ki nang...")
        features = self.extract_features_from_skills(students)
        
        print("Dang chuan hoa du lieu...")
        features_normalized = self.scaler.fit_transform(features)
        
        # K-means clustering
        print("\nK-MEANS: Dang phan cum dua tren ki nang...")
        self.kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(features_normalized)
        
        # Phan tich cum
        cluster_stats = {}
        for i, cluster in enumerate(clusters):
            if cluster not in cluster_stats:
                cluster_stats[cluster] = []
            cluster_stats[cluster].append(features_normalized[i])
        
        # Gan nhan cho cum
        cluster_means = {}
        for cluster, cluster_features in cluster_stats.items():
            features_array = np.array(cluster_features)
            # Tinh diem tong hop: 50% ki nang + 30% diem tong + 20% ty le dat
            composite_score = (
                features_array[:, 0] * 0.5 +   # Diem TB ki nang
                features_array[:, 1] * 0.3 +   # Diem tong
                features_array[:, 2] * 0.2     # Ty le dat
            )
            cluster_means[cluster] = np.mean(composite_score)
            print(f"  Cum {cluster}: diem tong hop = {cluster_means[cluster]:.3f}")
        
        # Gan nhan
        sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
        for cluster, mean_score in sorted_clusters:
            if mean_score >= 0.85:
                level = "Xuat sac"
            elif mean_score >= 0.70:
                level = "Kha"
            elif mean_score >= 0.55:
                level = "Trung binh"
            else:
                level = "Yeu"
            self.cluster_labels[cluster] = level
            print(f"  Cum {cluster} -> {level}")
        
        # KNN
        print("\nKNN: Dang hoc tu ket qua K-means...")
        labels = [self.cluster_labels[c] for c in clusters]
        self.knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
        self.knn.fit(features_normalized, labels)
        print("  KNN da hoc xong")
    
    def predict(self, students):
        """
        Du doan phan loai ket hop ki nang
        """
        features = self.extract_features_from_skills(students)
        features_normalized = self.scaler.transform(features)
        
        # Du doan
        kmeans_clusters = self.kmeans.predict(features_normalized)
        kmeans_predictions = [self.cluster_labels[c] for c in kmeans_clusters]
        knn_predictions = self.knn.predict(features_normalized).tolist()
        
        results = []
        
        for i, student in enumerate(students):
            # Danh gia ki nang chi tiet
            skill_evaluations = self.evaluate_all_courses(student)
            
            # Kiem tra bat thuong tong the
            anomaly_detected = False
            anomaly_reasons = []
            
            for course_name, evaluation in skill_evaluations.items():
                if evaluation['is_anomaly']:
                    anomaly_detected = True
                    anomaly_reasons.append(f"{course_name}: Diem cao nhung thoi gian hoc thap")
                
                if len(evaluation['weak_skills']) >= 2:
                    anomaly_reasons.append(f"{course_name}: Co {len(evaluation['weak_skills'])} ki nang yeu")
            
            # Dieu chinh phan loai neu co bat thuong
            final_level = kmeans_predictions[i]
            
            if anomaly_detected:
                level_order = ["Xuat sac", "Kha", "Trung binh", "Yeu"]
                current_idx = level_order.index(final_level) if final_level in level_order else 3
                
                # Ha 1-2 muc tuy theo muc do nghiem trong
                severity = len(anomaly_reasons)
                if severity >= 3:
                    new_idx = min(current_idx + 2, len(level_order) - 1)
                else:
                    new_idx = min(current_idx + 1, len(level_order) - 1)
                
                final_level = level_order[new_idx]
            
            result = {
                **student,
                "kmeans_prediction": kmeans_predictions[i],
                "knn_prediction": knn_predictions[i],
                "final_level": final_level,
                "skill_evaluations": skill_evaluations,
                "anomaly_detected": anomaly_detected,
                "anomaly_reasons": anomaly_reasons
            }
            
            results.append(result)
        
        return results


def demo_skill_based_classification():
    """
    Demo he thong phan loai theo ki nang
    """
    print("=" * 100)
    print("HE THONG PHAN LOAI SINH VIEN THEO KI NANG")
    print("=" * 100)
    
    from data_generator import StudentDataGenerator
    
    # Tai du lieu
    print("\nDang tai du lieu...")
    generator = StudentDataGenerator(seed=42, csv_path='student_classification_supabase_ready_final.csv')
    students = generator.load_all_students()
    print(f"Da tai {len(students)} sinh vien")
    
    # Phan loai
    classifier = SkillBasedClassifier(normalization_method='minmax')
    classifier.fit(students)
    results = classifier.predict(students)
    
    # Thong ke
    print("\n" + "=" * 100)
    print("THONG KE KET QUA")
    print("=" * 100)
    
    level_counts = {"Xuat sac": 0, "Kha": 0, "Trung binh": 0, "Yeu": 0}
    for r in results:
        level_counts[r["final_level"]] += 1
    
    print("\nPhan loai tong hop:")
    for level, count in level_counts.items():
        pct = (count / len(results)) * 100
        print(f"  {level:15s}: {count:3d} sinh vien ({pct:5.1f}%)")
    
    # Hien thi mot so vi du
    print("\n" + "=" * 100)
    print("VI DU CHI TIET - 5 SINH VIEN DAU TIEN")
    print("=" * 100)
    
    for i, result in enumerate(results[:5], 1):
        name = result['name'].encode('ascii', 'ignore').decode('ascii') if result['name'] else 'N/A'
        print(f"\n{i}. SV ID: {result['student_id']}")
        print(f"   Phan loai: {result['final_level']}")
        print(f"   Diem tong: {result['csv_data'].get('total_score', 0):.1f}/10")
        
        print(f"\n   Danh gia ki nang theo mon:")
        for course_name, evaluation in result['skill_evaluations'].items():
            print(f"\n   {course_name}:")
            print(f"     Diem TB ki nang: {evaluation['average_skill_score']:.1f}/10 ({evaluation['overall_skill_level']})")
            print(f"     Chi tiet ki nang:")
            for skill, score in evaluation['skills'].items():
                level = evaluation['skill_levels'][skill]
                status = "✓" if score >= 5.5 else "✗"
                print(f"       {status} {skill:30s}: {score:4.1f}/10 ({level})")
            
            if evaluation['weak_skills']:
                print(f"     Ki nang yeu: {', '.join(evaluation['weak_skills'])}")
            if evaluation['strong_skills']:
                print(f"     Ki nang manh: {', '.join(evaluation['strong_skills'])}")
        
        if result['anomaly_detected']:
            print(f"\n   ⚠️ Phat hien bat thuong:")
            for reason in result['anomaly_reasons']:
                print(f"     - {reason}")
    
    print("\n" + "=" * 100)
    print("HOAN THANH!")
    print("=" * 100)


if __name__ == "__main__":
    demo_skill_based_classification()
