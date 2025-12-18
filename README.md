# 🎓 Hệ Thống Phân Loại Sinh Viên

## 📊 Tổng Quan

Hệ thống phân loại sinh viên thông minh sử dụng **K-means + KNN + Chuẩn hóa dữ liệu** để đánh giá và phân loại sinh viên thành 4 mức độ: Xuất sắc, Khá, Trung bình, Yếu.

### ✨ Kiến Trúc Hệ Thống

```
Dữ liệu sinh viên (201 sinh viên)
         ↓
BƯỚC 1: CHUẨN HÓA DỮ LIỆU
├─ MinMax: (x - min) / (max - min) → [0, 1]
├─ ZScore: (x - mean) / std → Mean=0, Std=1
└─ Robust: (x - median) / IQR → Chống nhiễu
         ↓
BƯỚC 2: K-MEANS PHÂN CỤM (Unsupervised)
├─ Phân thành 4 cụm dựa trên điểm số và hành vi
├─ Tự động gán nhãn: Xuất sắc, Khá, TB, Yếu
└─ Tạo nhãn ban đầu cho KNN
         ↓
BƯỚC 3: KNN HỌC VÀ TINH CHỈNH (Supervised)
├─ Học từ nhãn K-means
├─ Xử lý trường hợp biên
└─ Độ chính xác: 100%
         ↓
BƯỚC 4: PHÁT HIỆN BẤT THƯỜNG
├─ Điểm cao + Thời gian ngắn = Gian lận
└─ Điều chỉnh phân loại nếu phát hiện
         ↓
    KẾT QUẢ CUỐI CÙNG
```

## 🚀 Chạy Hệ Thống

### 1. Cài Đặt
```bash
pip install -r requirements.txt
```

### 2. Setup Supabase (Chỉ làm 1 lần)
```
1. Truy cập: https://odmtndvllclmrwczcyvs.supabase.co
2. Vào SQL Editor
3. Chạy file: supabase_all_in_one.sql
```

### 3. Chạy Server
```bash
python app.py
```

Server sẽ:
- ✅ Tự động phân loại sinh viên
- ✅ Tự động sync dữ liệu lên Supabase
- ✅ Chạy tại: **http://localhost:5000**

**Xem hướng dẫn chi tiết:** [HUONG_DAN_SUPABASE.md](HUONG_DAN_SUPABASE.md)

### 3. Kết Quả Khởi Động

```
================================================================================
🎓 HỆ THỐNG PHÂN LOẠI SINH VIÊN - K-MEANS + KNN + CHUẨN HÓA
================================================================================

📊 Khởi tạo hệ thống...
✅ Đã tải 201 sinh viên

🔧 Phương pháp chuẩn hóa mặc định: MINMAX

🔵 K-MEANS: Đang phân cụm sinh viên...
  Cụm 2 (điểm TB: 0.820) -> Xuat sac
  Cụm 0 (điểm TB: 0.793) -> Kha
  Cụm 1 (điểm TB: 0.763) -> Trung binh
  Cụm 3 (điểm TB: 0.617) -> Yeu

🟢 KNN: Đang học từ kết quả K-means...
  ✓ KNN đã học xong với k=5, độ chính xác: 100.00%

📊 Thống kê ban đầu:
  • Xuất sắc    :  19 sinh viên (  9.5%)
  • Khá         : 111 sinh viên ( 55.2%)
  • Trung bình  :  30 sinh viên ( 14.9%)
  • Yếu         :  41 sinh viên ( 20.4%)
  • Bất thường  :   0 trường hợp

✅ Hệ thống đã sẵn sàng!
🌐 http://localhost:5000
```

## 📡 API Endpoints

### Web Application API (Port 5000)

#### 1. Phân Loại Sinh Viên
```bash
POST http://localhost:5000/api/classify
Content-Type: application/json

{
  "normalization_method": "minmax"
}
```

**Phương pháp chuẩn hóa:**
- `"minmax"` - Min-Max Scaling (mặc định)
- `"zscore"` - Z-Score Normalization
- `"robust"` - Robust Scaling

**Response:**
```json
{
  "success": true,
  "normalization_method": "minmax",
  "students": [...],
  "skill_evaluations": {...},
  "statistics": {
    "total": 201,
    "level_counts": {
      "Xuat sac": 19,
      "Kha": 111,
      "Trung binh": 30,
      "Yeu": 41
    },
    "anomaly_count": 0
  }
}
```

#### 2. Lấy Danh Sách Sinh Viên
```bash
GET http://localhost:5000/api/students
GET http://localhost:5000/api/students?class=22CT112
```

#### 3. Thống Kê
```bash
GET http://localhost:5000/api/statistics
GET http://localhost:5000/api/statistics?class=22CT112
```

#### 4. Chi Tiết Sinh Viên
```bash
GET http://localhost:5000/api/student/125001001
```

#### 5. Danh Sách Môn Học
```bash
GET http://localhost:5000/api/courses
```

---

### 🔌 REST API cho Bên Thứ 3 (Port 5001)

**Để cung cấp API cho người khác sử dụng:**

#### Khởi động API Server:
```bash
# Windows
run_api_server.bat

# Hoặc
python api_server.py
```

Server chạy tại: **http://localhost:5001**

#### Tài liệu API:
- **Quickstart:** [API_QUICKSTART.md](API_QUICKSTART.md)
- **Hướng dẫn đầy đủ:** [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)
- **Postman Collection:** [Student_Classification_API.postman_collection.json](Student_Classification_API.postman_collection.json)

#### API Key Demo:
```
X-API-Key: demo_key_12345
```

#### Ví dụ sử dụng:
```bash
# Phân loại 1 sinh viên
curl -X POST http://localhost:5001/api/classify \
  -H "X-API-Key: demo_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 999999001,
    "name": "Nguyễn Văn A",
    "csv_data": {...},
    "courses": {...}
  }'

# Lấy thống kê
curl -X GET http://localhost:5001/api/statistics \
  -H "X-API-Key: demo_key_12345"
```

#### Test API:
```bash
python test_api_client.py
```

## 🔬 3 Phương Pháp Chuẩn Hóa

### 1. Min-Max Scaling (Mặc định)
```python
# Công thức: (x - min) / (max - min)
# Kết quả: [0, 1]
# Ưu điểm: Đơn giản, giữ phân phối gốc
# Nhược điểm: Nhạy cảm với outliers
```

### 2. Z-Score (Standard Scaling)
```python
# Công thức: (x - mean) / std
# Kết quả: Mean = 0, Std = 1
# Ưu điểm: Phù hợp với phân phối chuẩn
# Nhược điểm: Nhạy cảm với outliers
```

### 3. Robust Scaling
```python
# Công thức: (x - median) / IQR
# Kết quả: Median = 0, IQR = 1
# Ưu điểm: Chống nhiễu tốt, dùng median
# Nhược điểm: Phức tạp hơn
```

## 📊 Đặc Trưng Sử Dụng

Hệ thống sử dụng 7 đặc trưng chính:

1. **avg_course_score** - Điểm trung bình các môn
2. **study_hours** - Số giờ học/tuần
3. **behavior** - Điểm hành vi
4. **anomaly_score** - Mức độ bất thường
5. **num_passed** - Tỷ lệ môn đạt
6. **midterm** - Điểm giữa kỳ
7. **final** - Điểm cuối kỳ

## 🎯 Phát Hiện Bất Thường

Hệ thống tự động phát hiện gian lận dựa trên:

```python
# Rất nghiêm trọng: Điểm 10 nhưng làm < 2 phút
if điểm >= 9.5 and thời_gian < 2:
    → Hạ xuống "Yếu"

# Nghiêm trọng: Điểm >= 9.0 nhưng làm < 5 phút
elif điểm >= 9.0 and thời_gian < 5:
    → Hạ xuống "Trung bình"

# Đáng nghi: Điểm >= 8.0 nhưng làm < 10 phút
elif điểm >= 8.0 and thời_gian < 10:
    → Hạ 1 mức
```

## 💻 Sử Dụng Trong Code

```python
from data_generator import StudentDataGenerator
from student_classifier import StudentClassifier

# Tải dữ liệu
generator = StudentDataGenerator(
    seed=42,
    csv_path='student_classification_supabase_ready_final.csv'
)
students = generator.load_all_students()

# Khởi tạo classifier với phương pháp chuẩn hóa
classifier = StudentClassifier(
    n_clusters=4,
    normalization_method='minmax'  # hoặc 'zscore', 'robust'
)

# Huấn luyện (K-means + KNN)
classifier.fit(students)

# Dự đoán
results = classifier.predict(students)

# Hiển thị kết quả
for student in results[:5]:
    print(f"{student['name']}: {student['final_level']}")
    if student['anomaly_detected']:
        print(f"  ⚠️ {student['anomaly_reason']}")
```

## 📁 Cấu Trúc Files

```
classifies-students/
├── app.py                          # Flask API server
├── student_classifier.py           # K-means + KNN + Chuẩn hóa
├── data_generator.py               # Tạo/tải dữ liệu
├── skill_evaluator.py              # Đánh giá kỹ năng
├── course_definitions.py           # Định nghĩa môn học
├── knn_clustering_normalizer.py    # Module KNN riêng
├── requirements.txt                # Dependencies
├── README.md                       # File này
└── student_classification_supabase_ready_final.csv
```

## 🌐 Web Interface

Mở trình duyệt tại: **http://localhost:5000**

Giao diện web cho phép:
- ✅ Xem danh sách sinh viên đã phân loại
- ✅ Xem thống kê theo mức độ
- ✅ Xem chi tiết từng sinh viên
- ✅ Lọc theo lớp
- ✅ Phân loại lại với phương pháp khác

## 🔧 Tùy Chỉnh

### Thay đổi phương pháp chuẩn hóa:
```python
classifier = StudentClassifier(
    n_clusters=4,
    normalization_method='robust'  # Chống nhiễu tốt hơn
)
```

### Thay đổi số cụm:
```python
classifier = StudentClassifier(
    n_clusters=5,  # 5 mức độ thay vì 4
    normalization_method='minmax'
)
```

## 📈 Kết Quả Thực Tế

Với 201 sinh viên:

| Mức độ | Số lượng | Tỷ lệ |
|--------|----------|-------|
| Xuất sắc | 19 | 9.5% |
| Khá | 111 | 55.2% |
| Trung bình | 30 | 14.9% |
| Yếu | 41 | 20.4% |

**Độ chính xác KNN:** 100%  
**Phát hiện bất thường:** 0 trường hợp

## 🐛 Troubleshooting

### Lỗi: Port đã được sử dụng
```bash
# Tìm và kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Hoặc đổi port
app.run(port=5001)
```

### Lỗi: File CSV không tồn tại
```bash
# Đảm bảo file CSV nằm cùng thư mục
ls student_classification_supabase_ready_final.csv
```

## 📚 Tài Liệu Tham Khảo

- [Scikit-learn K-means](https://scikit-learn.org/stable/modules/clustering.html#k-means)
- [Scikit-learn KNN](https://scikit-learn.org/stable/modules/neighbors.html)
- [Feature Scaling](https://scikit-learn.org/stable/modules/preprocessing.html)

## 📝 License

MIT License - Tự do sử dụng cho mục đích học tập và nghiên cứu.
