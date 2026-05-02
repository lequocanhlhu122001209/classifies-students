# 🎓 Hệ Thống Phân Loại & Chấm Điểm Sinh Viên Tích Hợp

Hệ thống phân loại sinh viên thông minh sử dụng **K-means + KNN + Chuẩn hóa dữ liệu** kết hợp với **hệ thống chấm điểm tích hợp** để đánh giá toàn diện sinh viên dựa trên điểm số, hành vi và kỹ năng.

## 📋 Tính Năng Chính

- **Phân loại tự động**: K-means phân cụm + KNN dự đoán → 4 mức: Xuất sắc, Khá, Trung bình, Yếu
- **Chấm điểm tích hợp**: Kết hợp điểm bài tập (30%) + Giữa kỳ (30%) + Cuối kỳ (40%)
- **Phát hiện bất thường**: Tự động phát hiện gian lận (điểm cao + thời gian ngắn + vắng nhiều)
- **Đánh giá kỹ năng**: 4 kỹ năng/môn học × 4 môn = 16 kỹ năng được đánh giá
- **Sync Supabase**: Lưu trữ và đồng bộ dữ liệu lên cloud

## 🏗️ Kiến Trúc Hệ Thống

```
Dữ liệu sinh viên (Supabase)
         ↓
[1] CHUẨN HÓA DỮ LIỆU
    ├─ MinMax: (x - min) / (max - min) → [0, 1]
    ├─ ZScore: (x - mean) / std
    └─ Robust: (x - median) / IQR
         ↓
[2] K-MEANS PHÂN CỤM (Unsupervised)
    ├─ 12 features: điểm số + hành vi
    ├─ Phân thành 4 cụm
    └─ Gán nhãn theo điểm tổng hợp
         ↓
[3] KNN DỰ ĐOÁN (Supervised)
    ├─ Học từ nhãn K-means
    └─ Dự đoán cho sinh viên mới
         ↓
[4] PHÁT HIỆN BẤT THƯỜNG
    ├─ Điểm cao + Thời gian ngắn
    ├─ Điểm cao + Vắng nhiều
    └─ Nộp muộn nhiều
         ↓
[5] ĐIỂM TÍCH HỢP
    ├─ Bài tập: 30%
    ├─ Giữa kỳ: 30%
    └─ Cuối kỳ: 40%
         ↓
    KẾT QUẢ PHÂN LOẠI
```

## 🚀 Cài Đặt & Chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Supabase
Tạo file `.env` (copy từ `.env.example`):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. Chạy server
```bash
python app.py
```

Server chạy tại: **http://localhost:5000**

### 4. Tạo dữ liệu mẫu cho KMeans + KNN
```bash
python scripts/seed_sample_students_for_kmeans_knn.py --count 300
```

Tuỳ chọn:
- `--count`: số lượng sinh viên mẫu
- `--seed`: random seed
- `--sync-supabase`: đồng bộ thêm lên Supabase
- `--replace`: xóa dữ liệu cũ trước khi tạo dữ liệu mẫu mới

## 📡 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/students` | Danh sách sinh viên (có điểm tích hợp) |
| GET | `/api/students?class=22CT112` | Lọc theo lớp |
| GET | `/api/student/<id>` | Chi tiết sinh viên |
| GET | `/api/statistics` | Thống kê tổng quan |
| GET | `/api/courses` | Danh sách môn học & kỹ năng |
| POST | `/api/classify` | Phân loại lại với phương pháp chuẩn hóa |
| POST | `/api/sync-supabase` | Đồng bộ dữ liệu lên Supabase |

### Ví dụ API
```bash
# Phân loại với Robust Scaling
curl -X POST http://localhost:5000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"normalization_method": "robust"}'
```

## 📊 Đặc Trưng Phân Loại (12 Features)

**Điểm số (50%)**
- Điểm TB các môn, Giữa kỳ, Cuối kỳ, Bài tập

**Hành vi (50%)**
- Tham gia, Hành vi, Chuyên cần, Hoàn thành BT, Thời gian làm bài, Độ ổn định điểm

## 🎯 Phát Hiện Bất Thường

| Mức độ | Điều kiện | Hành động |
|--------|-----------|-----------|
| Nghiêm trọng | Điểm ≥8.5 + Thời gian <5h | Hạ xuống Yếu |
| Nghiêm trọng | Điểm ≥8.0 + Vắng >50% | Hạ xuống Yếu |
| Trung bình | Nộp muộn 10-14 lần | Hạ 2 bậc |
| Nhẹ | Nộp muộn 5-9 lần | Hạ 1 bậc |

## 📚 Môn Học & Kỹ Năng

| Môn học | Kỹ năng |
|---------|---------|
| Nhập Môn Lập Trình | Biến & Kiểu dữ liệu, Cấu trúc điều khiển, Vòng lặp, Hàm cơ bản |
| Kĩ Thuật Lập Trình | Mảng, Con trỏ, Chuỗi ký tự, File I/O |
| Cấu trúc Dữ Liệu & Giải Thuật | Arrays, Linked List, Stack/Queue, Trees |
| Lập Trình Hướng Đối Tượng | Lớp & Đối tượng, Kế thừa, Đa hình, Đóng gói |

## 📁 Cấu Trúc Project

```
├── app.py                      # Flask API server chính
├── main.py                     # Script chạy phân loại
├── requirements.txt            # Dependencies
├── .env.example                # Mẫu cấu hình
│
├── src/                        # Core modules
│   ├── student_classifier.py   # K-means + KNN + Chuẩn hóa
│   ├── integrated_scoring_system.py
│   ├── skill_evaluator.py
│   ├── skill_based_classifier.py
│   ├── course_definitions.py
│   ├── data_generator.py       # Load data từ Supabase
│   └── supabase_sync.py
│
├── scripts/                    # Utility scripts
│   ├── analysis/               # Scripts phân tích
│   └── utils/                  # Scripts tiện ích
│
├── templates/                  # Giao diện web
├── static/                     # CSS, JS
└── models/                     # Trained models (.pkl)
```

## 🛠️ Công Nghệ

- **Backend**: Flask, Python 3.x
- **ML**: scikit-learn (K-means, KNN, MinMaxScaler, StandardScaler)
- **Database**: Supabase (PostgreSQL)
- **Data**: NumPy, Pandas

## 📈 Kết Quả Thực Tế

Với 201 sinh viên:

| Mức độ | Số lượng | Tỷ lệ |
|--------|----------|-------|
| Xuất sắc | 19 | 9.5% |
| Khá | 111 | 55.2% |
| Trung bình | 30 | 14.9% |
| Yếu | 41 | 20.4% |

**Độ chính xác KNN:** 100%

## 📝 License

MIT License
