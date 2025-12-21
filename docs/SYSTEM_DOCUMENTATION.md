# 📚 TÀI LIỆU HỆ THỐNG PHÂN LOẠI SINH VIÊN

## PHẦN 1: MÔ HÌNH DỮ LIỆU

### 1.1. Tổng Quan

Hệ thống sử dụng **7 đối tượng (bảng)** với **6 quan hệ** để lưu trữ và xử lý dữ liệu sinh viên.

---

### 1.2. Chi Tiết 7 Đối Tượng

#### 📌 Đối tượng 1: `students` (Sinh viên)

**Mục đích:** Lưu thông tin cơ bản của sinh viên - là bảng trung tâm.

| Thuộc tính | Kiểu | Ý nghĩa | Ví dụ |
|------------|------|---------|-------|
| `student_id` | INTEGER (PK) | Mã sinh viên duy nhất | 125001001 |
| `name` | VARCHAR | Họ và tên | "Nguyễn Văn A" |
| `class` | VARCHAR | Lớp học | "22CT111" |
| `khoa` | VARCHAR | Khoa | "CNTT" |
| `sex` | VARCHAR | Giới tính | "Nam" |

---

#### 📌 Đối tượng 2: `student_csv_data` (Dữ liệu hành vi)

**Mục đích:** Lưu các chỉ số hành vi học tập của sinh viên.

| Thuộc tính | Kiểu | Ý nghĩa | Giá trị |
|------------|------|---------|---------|
| `student_id` | INTEGER (FK) | Liên kết với students | 125001001 |
| `midterm_score` | FLOAT | Điểm giữa kỳ | 0-10 |
| `final_score` | FLOAT | Điểm cuối kỳ | 0-10 |
| `homework_score` | FLOAT | Điểm bài tập | 0-10 |
| `total_score` | FLOAT | Điểm tổng kết | 0-10 |
| `attendance_rate` | FLOAT | Tỷ lệ đi học | 0-1 (0%=0, 100%=1) |
| `assignment_completion` | FLOAT | Tỷ lệ hoàn thành BT | 0-1 |
| `study_hours_per_week` | INTEGER | Giờ học/tuần | 0-40 |
| `late_submissions` | INTEGER | Số lần nộp muộn | 0-30 |
| `behavior_score_100` | INTEGER | Điểm hành vi | 0-100 |

---

#### 📌 Đối tượng 3: `course_scores` (Điểm môn học)

**Mục đích:** Lưu điểm chi tiết của 4 môn học lập trình.

| Thuộc tính | Kiểu | Ý nghĩa | Giá trị |
|------------|------|---------|---------|
| `student_id` | INTEGER (FK) | Liên kết với students | 125001001 |
| `course_code` | VARCHAR | Mã môn học | NMLT, KTLT, CTDL, OOP |
| `score` | FLOAT | Điểm tổng môn | 0-10 |
| `time_minutes` | INTEGER | Thời gian làm bài | 0-300 phút |
| `midterm_score` | FLOAT | Điểm giữa kỳ môn | 0-10 |
| `final_score` | FLOAT | Điểm cuối kỳ môn | 0-10 |

**4 Môn học:**
- `NMLT` - Nhập Môn Lập Trình
- `KTLT` - Kĩ Thuật Lập Trình  
- `CTDL` - Cấu trúc Dữ Liệu và Giải Thuật
- `OOP` - Lập Trình Hướng Đối Tượng

---

#### 📌 Đối tượng 4: `skill_evaluations` (Đánh giá kỹ năng)

**Mục đích:** Lưu đánh giá 16 kỹ năng (4 kỹ năng × 4 môn).

| Thuộc tính | Kiểu | Ý nghĩa | Giá trị |
|------------|------|---------|---------|
| `student_id` | INTEGER (FK) | Liên kết với students | 125001001 |
| `course_code` | VARCHAR | Mã môn | NMLT, KTLT, CTDL, OOP |
| `skill_code` | VARCHAR | Mã kỹ năng | VARIABLES, LOOPS, ... |
| `score` | FLOAT | Điểm kỹ năng | 0-10 |
| `level` | VARCHAR | Mức độ | Xuất sắc/Khá/TB/Yếu |
| `passed` | BOOLEAN | Đạt hay không | true (≥5), false (<5) |

**16 Kỹ năng:**
| Môn | Kỹ năng 1 | Kỹ năng 2 | Kỹ năng 3 | Kỹ năng 4 |
|-----|-----------|-----------|-----------|-----------|
| NMLT | Biến & Kiểu DL | Điều khiển | Vòng lặp | Hàm |
| KTLT | Mảng | Con trỏ | Chuỗi | File I/O |
| CTDL | Linked List | Stack/Queue | Cây | Hash |
| OOP | Class | Kế thừa | Đa hình | Đóng gói |

---

#### 📌 Đối tượng 5: `classifications` (Kết quả phân loại)

**Mục đích:** Lưu kết quả phân loại từ thuật toán ML.

| Thuộc tính | Kiểu | Ý nghĩa | Giá trị |
|------------|------|---------|---------|
| `student_id` | INTEGER (FK) | Liên kết với students | 125001001 |
| `kmeans_prediction` | VARCHAR | Dự đoán K-means | Xuat sac/Kha/TB/Yeu |
| `knn_prediction` | VARCHAR | Dự đoán KNN | Xuat sac/Kha/TB/Yeu |
| `final_level` | VARCHAR | Kết quả cuối cùng | Xuat sac/Kha/TB/Yeu |
| `normalization_method` | VARCHAR | Phương pháp chuẩn hóa | minmax/zscore/robust |
| `anomaly_detected` | BOOLEAN | Phát hiện bất thường | true/false |
| `anomaly_reasons` | JSONB | Lý do bất thường | ["Nộp muộn 15 lần"] |

---

#### 📌 Đối tượng 6: `integrated_scores` (Điểm tích hợp)

**Mục đích:** Lưu điểm tổng hợp theo công thức tích hợp.

| Thuộc tính | Kiểu | Ý nghĩa | Giá trị |
|------------|------|---------|---------|
| `student_id` | INTEGER (FK) | Liên kết với students | 125001001 |
| `original_score` | FLOAT | Điểm gốc | 0-10 |
| `integrated_score` | FLOAT | Điểm tích hợp | 0-10 |
| `score_difference` | FLOAT | Chênh lệch | -5 đến +5 |
| `classification` | VARCHAR | Phân loại | Giỏi/Khá/TB/Yếu |
| `exercise_avg` | FLOAT | TB bài tập | 0-10 |
| `midterm_avg` | FLOAT | TB giữa kỳ | 0-10 |
| `final_avg` | FLOAT | TB cuối kỳ | 0-10 |

**Công thức:**
```
integrated_score = exercise_avg × 30% + midterm_avg × 30% + final_avg × 40%
```

---

#### 📌 Đối tượng 7: `exercise_details` (Chi tiết bài tập)

**Mục đích:** Lưu chi tiết từng bài tập của sinh viên.

| Thuộc tính | Kiểu | Ý nghĩa | Giá trị |
|------------|------|---------|---------|
| `student_id` | INTEGER (FK) | Liên kết với students | 125001001 |
| `course_code` | VARCHAR | Mã môn | NMLT, KTLT, ... |
| `skill_code` | VARCHAR | Mã kỹ năng | VARIABLES, ... |
| `exercise_number` | INTEGER | Số bài tập | 1, 2, 3, ... |
| `score` | FLOAT | Điểm bài | 0-10 |
| `completion_time` | FLOAT | Thời gian làm | phút |
| `is_anomaly` | BOOLEAN | Bất thường | true/false |

---

### 1.3. Quan Hệ Giữa Các Đối Tượng (6 Quan Hệ)

```
                         ┌─────────────────┐
                         │    STUDENTS     │
                         │   (Bảng chính)  │
                         │   student_id    │
                         └────────┬────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ student_csv_data│    │ classifications │    │integrated_scores│
│     (1:1)       │    │     (1:1)       │    │     (1:1)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘

         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  course_scores  │    │skill_evaluations│    │exercise_details │
│     (1:N)       │    │     (1:N)       │    │     (1:N)       │
│   4 bản ghi/SV  │    │  16 bản ghi/SV  │    │ Nhiều bản ghi/SV│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

| # | Quan hệ | Loại | Giải thích |
|---|---------|------|------------|
| 1 | students → student_csv_data | **1:1** | Mỗi SV có đúng 1 bản ghi hành vi |
| 2 | students → classifications | **1:1** | Mỗi SV có đúng 1 kết quả phân loại |
| 3 | students → integrated_scores | **1:1** | Mỗi SV có đúng 1 điểm tích hợp |
| 4 | students → course_scores | **1:N** | Mỗi SV có 4 bản ghi (4 môn học) |
| 5 | students → skill_evaluations | **1:N** | Mỗi SV có 16 bản ghi (16 kỹ năng) |
| 6 | students → exercise_details | **1:N** | Mỗi SV có nhiều bài tập |

---

## PHẦN 2: THUẬT TOÁN SỬ DỤNG

### 2.1. Tổng Quan Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE XỬ LÝ DỮ LIỆU                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [1] DỮ LIỆU THÔ                                               │
│       │                                                         │
│       ▼                                                         │
│  [2] TRÍCH XUẤT 12 FEATURES ──────────────────────────────────┐│
│       │                                                        ││
│       ▼                                                        ││
│  [3] CHUẨN HÓA (MinMax/ZScore/Robust)                         ││
│       │                                                        ││
│       ├──────────────┐                                         ││
│       ▼              ▼                                         ││
│  [4] K-MEANS    [5] KNN                                        ││
│   (Phân cụm)    (Phân loại)                                    ││
│       │              │                                         ││
│       └──────┬───────┘                                         ││
│              ▼                                                  ││
│  [6] PHÁT HIỆN BẤT THƯỜNG                                      ││
│              │                                                  ││
│              ▼                                                  ││
│  [7] KẾT QUẢ PHÂN LOẠI CUỐI CÙNG                              ││
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2.2. Thuật Toán 1: CHUẨN HÓA DỮ LIỆU (Normalization)

**Mục đích:** Đưa các features về cùng thang đo để thuật toán ML hoạt động tốt hơn.

#### a) MinMax Scaling (Mặc định)
```
X_normalized = (X - X_min) / (X_max - X_min)
```
- **Kết quả:** Giá trị trong khoảng [0, 1]
- **Ưu điểm:** Đơn giản, giữ phân phối gốc
- **Nhược điểm:** Nhạy cảm với outliers

#### b) Z-Score (Standard Scaling)
```
X_normalized = (X - mean) / std
```
- **Kết quả:** Mean = 0, Std = 1
- **Ưu điểm:** Phù hợp phân phối chuẩn
- **Nhược điểm:** Nhạy cảm với outliers

#### c) Robust Scaling
```
X_normalized = (X - median) / IQR
```
- **Kết quả:** Median = 0
- **Ưu điểm:** Chống nhiễu tốt (dùng median thay mean)
- **Nhược điểm:** Phức tạp hơn

---

### 2.3. Thuật Toán 2: K-MEANS CLUSTERING

**Loại:** Unsupervised Learning (Học không giám sát)

**Mục đích:** Phân cụm sinh viên thành 4 nhóm dựa trên đặc điểm tương đồng.

#### Cách hoạt động:
```
1. Khởi tạo 4 centroids ngẫu nhiên
2. Lặp lại:
   a. Gán mỗi điểm vào cụm có centroid gần nhất
   b. Cập nhật centroid = trung bình các điểm trong cụm
3. Dừng khi centroids không đổi
```

#### Công thức khoảng cách (Euclidean):
```
d(x, c) = √[(x₁-c₁)² + (x₂-c₂)² + ... + (x₁₂-c₁₂)²]
```

#### Tham số:
- `n_clusters = 4` (4 mức: Xuất sắc, Khá, TB, Yếu)
- `n_init = 10` (chạy 10 lần, chọn kết quả tốt nhất)
- `random_state = 42` (đảm bảo reproducible)

#### Gán nhãn cho cụm:
```python
# Tính điểm tổng hợp mỗi cụm
composite = điểm_số × 50% + hành_vi × 50%

# Sắp xếp cụm theo điểm từ cao → thấp
# Cụm cao nhất → "Xuất sắc"
# Cụm thấp nhất → "Yếu"
```

---

### 2.4. Thuật Toán 3: K-NEAREST NEIGHBORS (KNN)

**Loại:** Supervised Learning (Học có giám sát)

**Mục đích:** Dự đoán nhãn cho sinh viên mới dựa trên k láng giềng gần nhất.

#### Cách hoạt động:
```
1. Tìm k sinh viên gần nhất với sinh viên cần dự đoán
2. Đếm số lượng mỗi nhãn trong k láng giềng
3. Gán nhãn có số lượng nhiều nhất (voting)
```

#### Công thức (Distance-weighted voting):
```
weight = 1 / distance
prediction = argmax(Σ weight_i × label_i)
```

#### Tham số:
- `k = 3-5` (số láng giềng, tự động chọn dựa trên dữ liệu)
- `weights = 'distance'` (láng giềng gần có trọng số cao hơn)
- `metric = 'euclidean'` (khoảng cách Euclidean)

---

### 2.5. Thuật Toán 4: PHÁT HIỆN BẤT THƯỜNG (Anomaly Detection)

**Loại:** Rule-based Detection

**Mục đích:** Phát hiện sinh viên có dấu hiệu gian lận hoặc bất thường.

#### Các quy tắc:

| Điều kiện | Mức độ | Hành động |
|-----------|--------|-----------|
| Điểm ≥8.5 + Thời gian <5h | Nghiêm trọng (3) | Hạ xuống Yếu |
| Điểm ≥8.0 + Vắng >50% | Nghiêm trọng (3) | Hạ xuống Yếu |
| Nộp muộn ≥15 lần | Nghiêm trọng (3) | Hạ xuống Yếu |
| Nộp muộn 10-14 lần | Trung bình (2) | Hạ 2 bậc |
| Nộp muộn 5-9 lần | Nhẹ (1) | Hạ 1 bậc |
| Vắng >40% | Trung bình (2) | Hạ 2 bậc |

#### Logic xử lý:
```python
if anomaly_severity >= 3:
    final_level = "Yeu"  # Hạ xuống Yếu
elif anomaly_severity >= 2:
    final_level = hạ_2_bậc(current_level)
elif anomaly_severity >= 1:
    final_level = hạ_1_bậc(current_level)
```

---

### 2.6. 12 Features Sử Dụng

| # | Feature | Nguồn | Trọng số | Ý nghĩa |
|---|---------|-------|----------|---------|
| 1 | total_score | csv_data | 15% | Điểm TB các môn |
| 2 | midterm | csv_data | 10% | Điểm giữa kỳ |
| 3 | final | csv_data | 15% | Điểm cuối kỳ |
| 4 | homework | csv_data | 10% | Điểm bài tập |
| 5 | behavior | csv_data | 10% | Điểm hành vi |
| 6 | attendance | csv_data | 10% | Tỷ lệ tham gia |
| 7 | punctuality | csv_data | 10% | Chuyên cần (không nộp muộn) |
| 8 | assignment | csv_data | 5% | Hoàn thành bài tập |
| 9 | avg_time | courses | 5% | Thời gian làm bài |
| 10 | clean_score | tính toán | 10% | Điểm "sạch" (không bất thường) |
| 11 | late_ratio | csv_data | - | Tỷ lệ nộp muộn |
| 12 | stability | courses | 5% | Độ ổn định điểm |

**Phân bổ:** 50% Điểm số + 50% Hành vi

---

## PHẦN 3: ĐÁNH GIÁ THUẬT TOÁN

### 3.1. Phương Pháp Đánh Giá

#### a) Train/Test Split
- Chia dữ liệu thành tập Train và Test
- Test các tỷ lệ: 60/40, 70/30, 80/20

#### b) Cross-Validation (K-Fold)
- Chia dữ liệu thành K phần
- Lần lượt dùng 1 phần làm Test, còn lại làm Train
- Tính trung bình kết quả

#### c) Các Metrics Đánh Giá

| Metric | Công thức | Ý nghĩa |
|--------|-----------|---------|
| **Accuracy** | (TP+TN)/(TP+TN+FP+FN) | Tỷ lệ dự đoán đúng |
| **Precision** | TP/(TP+FP) | Độ chính xác khi dự đoán Positive |
| **Recall** | TP/(TP+FN) | Tỷ lệ tìm được Positive thực sự |
| **F1-Score** | 2×(P×R)/(P+R) | Trung bình điều hòa P và R |

---

### 3.2. Kết Quả Đánh Giá Thực Tế

#### Test 1: Train/Test Split

| Tỷ lệ | Train | Test | Accuracy | Precision | Recall | F1 |
|-------|-------|------|----------|-----------|--------|-----|
| 80/20 | 240 | 60 | **81.67%** | 82.02% | 81.67% | 81.81% |
| 70/30 | 210 | 90 | 78.89% | 78.45% | 78.89% | 78.54% |
| 60/40 | 180 | 120 | 77.50% | 77.33% | 77.50% | 77.26% |

**Kết luận:** Tỷ lệ 80/20 cho kết quả tốt nhất.

---

#### Test 2: So Sánh Phương Pháp Chuẩn Hóa

| Phương pháp | Accuracy | F1-Score |
|-------------|----------|----------|
| MinMax | 78.89% | 78.54% |
| **ZScore** | **81.11%** | **81.21%** |
| Robust | 76.67% | 76.84% |

**Kết luận:** ZScore cho kết quả tốt nhất.

---

#### Test 3: Cross-Validation (5-Fold)

| Fold | Accuracy |
|------|----------|
| 1 | 85.0% |
| 2 | 88.3% |
| 3 | 88.3% |
| 4 | 91.7% |
| 5 | 83.3% |

**Mean: 87.33% ± 2.91%**

---

#### Test 4: Tối Ưu Giá Trị K (KNN)

| k | Accuracy | F1-Score |
|---|----------|----------|
| 1 | 84.44% | 84.49% |
| **3** | **86.67%** | **86.80%** |
| 5 | 78.89% | 78.54% |
| 7 | 77.78% | 77.45% |
| 9 | 78.89% | 78.33% |

**Kết luận:** k=3 cho kết quả tốt nhất.

---

#### Test 5: Classification Report Chi Tiết

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Xuất sắc | 0.86 | 0.94 | 0.90 | 32 |
| Khá | 0.72 | 0.66 | 0.69 | 32 |
| Trung bình | 0.77 | 0.77 | 0.77 | 26 |
| **Weighted Avg** | **0.78** | **0.79** | **0.79** | 90 |

---

#### Test 6: Confusion Matrix

```
Actual \ Pred    Xuất sắc    Khá    Trung bình
─────────────────────────────────────────────
Xuất sắc            30        2         0
Khá                  5       21         6
Trung bình           0        6        20
```

**Phân tích:**
- **Xuất sắc:** 30/32 đúng = 93.75% ✅ Rất tốt
- **Khá:** 21/32 đúng = 65.63% ⚠️ Có nhầm lẫn
- **Trung bình:** 20/26 đúng = 76.92% ✅ Khá tốt

---

### 3.3. Tổng Kết Đánh Giá

```
┌─────────────────────────────────────────────────────────────┐
│                    KẾT QUẢ ĐÁNH GIÁ                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Dữ liệu: 300 sinh viên, 12 features                    │
│                                                             │
│  ✅ Accuracy tổng thể: 87.33% (Cross-validation)           │
│  ✅ Best Train/Test: 80%/20%                                │
│  ✅ Best Normalization: ZScore                              │
│  ✅ Best KNN k: 3                                           │
│                                                             │
│  📈 Điểm mạnh:                                              │
│     • Phân loại "Xuất sắc" rất chính xác (>90%)            │
│     • Cross-validation ổn định (std = 2.91%)               │
│     • Pipeline xử lý hoàn chỉnh                            │
│                                                             │
│  ⚠️ Điểm cần cải thiện:                                    │
│     • Phân loại "Khá" còn nhầm lẫn với các class khác      │
│     • Cần thêm dữ liệu class "Yếu" để cân bằng             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PHẦN 4: TÓM TẮT

### 4.1. Mô Hình Dữ Liệu
- **7 đối tượng** (tables)
- **6 quan hệ** (3 quan hệ 1:1, 3 quan hệ 1:N)
- Bảng trung tâm: `students`

### 4.2. Thuật Toán
- **Chuẩn hóa:** MinMax, ZScore, Robust
- **Phân cụm:** K-means (Unsupervised)
- **Phân loại:** KNN (Supervised)
- **Phát hiện bất thường:** Rule-based

### 4.3. Đánh Giá
- **Accuracy:** 87.33%
- **Cấu hình tối ưu:** ZScore + KNN(k=3) + Train/Test 80/20
