# 📊 MÔ HÌNH DỮ LIỆU - HỆ THỐNG PHÂN LOẠI SINH VIÊN

## Tổng Quan

Hệ thống sử dụng **Supabase (PostgreSQL)** làm database với 7 bảng chính.

---

## 📐 SƠ ĐỒ QUAN HỆ (ERD)

```
┌─────────────────┐
│    students     │ (Bảng chính)
│─────────────────│
│ student_id (PK) │◄──────────────────────────────────────────┐
│ name            │                                           │
│ class           │                                           │
│ khoa            │                                           │
│ sex             │                                           │
└────────┬────────┘                                           │
         │                                                    │
         │ 1:1                                                │
         ▼                                                    │
┌─────────────────────┐                                       │
│  student_csv_data   │ (Dữ liệu hành vi)                     │
│─────────────────────│                                       │
│ student_id (PK, FK) │                                       │
│ midterm_score       │                                       │
│ final_score         │                                       │
│ attendance_rate     │                                       │
│ behavior_score_100  │                                       │
│ late_submissions    │                                       │
│ ...                 │                                       │
└─────────────────────┘                                       │
         │                                                    │
         │ 1:N                                                │
         ▼                                                    │
┌─────────────────────┐     ┌─────────────────────┐          │
│   course_scores     │     │  skill_evaluations  │          │
│─────────────────────│     │─────────────────────│          │
│ student_id (FK)     │────►│ student_id (FK)     │──────────┤
│ course_code         │     │ course_code         │          │
│ score               │     │ skill_code          │          │
│ time_minutes        │     │ score               │          │
│ midterm_score       │     │ level               │          │
│ final_score         │     │ passed              │          │
└─────────────────────┘     └─────────────────────┘          │
                                                              │
┌─────────────────────┐     ┌─────────────────────┐          │
│  classifications    │     │  integrated_scores  │          │
│─────────────────────│     │─────────────────────│          │
│ student_id (FK)     │────►│ student_id (FK)     │──────────┤
│ kmeans_prediction   │     │ original_score      │          │
│ knn_prediction      │     │ integrated_score    │          │
│ final_level         │     │ score_difference    │          │
│ anomaly_detected    │     │ classification      │          │
│ anomaly_reasons     │     │ exercise_avg        │          │
└─────────────────────┘     └─────────────────────┘          │
                                                              │
┌─────────────────────┐                                       │
│  exercise_details   │                                       │
│─────────────────────│                                       │
│ student_id (FK)     │───────────────────────────────────────┘
│ course_code         │
│ skill_code          │
│ exercise_number     │
│ score               │
│ completion_time     │
│ is_anomaly          │
└─────────────────────┘
```

---

## 📋 CHI TIẾT CÁC BẢNG

### 1. `students` - Thông tin sinh viên

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (PK) | Mã sinh viên (VD: 125001001) |
| `name` | VARCHAR | Họ tên sinh viên |
| `class` | VARCHAR | Lớp (VD: 22CT111, 22CT112) |
| `khoa` | VARCHAR | Khoa |
| `sex` | VARCHAR | Giới tính |

---

### 2. `student_csv_data` - Dữ liệu hành vi học tập

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (PK, FK) | Mã sinh viên |
| `midterm_score` | FLOAT | Điểm giữa kỳ (0-10) |
| `final_score` | FLOAT | Điểm cuối kỳ (0-10) |
| `homework_score` | FLOAT | Điểm bài tập (0-10) |
| `total_score` | FLOAT | Điểm tổng kết (0-10) |
| `attendance_rate` | FLOAT | Tỷ lệ tham gia (0-1) |
| `assignment_completion` | FLOAT | Tỷ lệ hoàn thành BT (0-1) |
| `study_hours_per_week` | INTEGER | Số giờ học/tuần |
| `participation_score` | INTEGER | Điểm tham gia (0-100) |
| `late_submissions` | INTEGER | Số lần nộp muộn |
| `lms_usage_hours` | INTEGER | Giờ sử dụng LMS |
| `response_quality` | INTEGER | Chất lượng phản hồi (0-100) |
| `behavior_score_100` | INTEGER | Điểm hành vi (0-100) |

---

### 3. `course_scores` - Điểm từng môn học

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (FK) | Mã sinh viên |
| `course_code` | VARCHAR | Mã môn (NMLT, KTLT, CTDL, OOP) |
| `score` | FLOAT | Điểm tổng môn (0-10) |
| `time_minutes` | INTEGER | Thời gian làm bài (phút) |
| `midterm_score` | FLOAT | Điểm giữa kỳ môn |
| `final_score` | FLOAT | Điểm cuối kỳ môn |
| `homework_score` | FLOAT | Điểm bài tập môn |

**Mã môn học:**
- `NMLT` - Nhập Môn Lập Trình
- `KTLT` - Kĩ Thuật Lập Trình
- `CTDL` - Cấu trúc Dữ Liệu và Giải Thuật
- `OOP` - Lập Trình Hướng Đối Tượng

---

### 4. `skill_evaluations` - Đánh giá kỹ năng

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (FK) | Mã sinh viên |
| `course_code` | VARCHAR | Mã môn học |
| `skill_code` | VARCHAR | Mã kỹ năng |
| `score` | FLOAT | Điểm kỹ năng (0-10) |
| `level` | VARCHAR | Mức độ (Xuất sắc/Khá/TB/Yếu) |
| `passed` | BOOLEAN | Đạt hay không (≥5 điểm) |

**Mã kỹ năng theo môn:**

| Môn | Kỹ năng | Mã |
|-----|---------|-----|
| NMLT | Biến và Kiểu dữ liệu | VARIABLES |
| NMLT | Cấu trúc điều khiển | CONTROL |
| NMLT | Vòng lặp | LOOPS |
| NMLT | Hàm cơ bản | FUNCTIONS |
| KTLT | Mảng | ARRAYS |
| KTLT | Con trỏ | POINTERS |
| KTLT | Chuỗi ký tự | STRINGS |
| KTLT | File I/O | FILE_IO |
| CTDL | Danh sách liên kết | LINKED_LIST |
| CTDL | Stack và Queue | STACK_QUEUE |
| CTDL | Cây | TREES |
| CTDL | Bảng băm | HASH_TABLE |
| OOP | Lớp và Đối tượng | CLASSES |
| OOP | Kế thừa | INHERITANCE |
| OOP | Đa hình | POLYMORPHISM |
| OOP | Đóng gói | ENCAPSULATION |

---

### 5. `classifications` - Kết quả phân loại

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (FK) | Mã sinh viên |
| `kmeans_prediction` | VARCHAR | Dự đoán K-means |
| `knn_prediction` | VARCHAR | Dự đoán KNN |
| `final_level` | VARCHAR | Kết quả cuối cùng |
| `normalization_method` | VARCHAR | Phương pháp chuẩn hóa |
| `anomaly_detected` | BOOLEAN | Có bất thường không |
| `anomaly_reasons` | JSONB | Danh sách lý do bất thường |

**Các mức phân loại:**
- `Xuat sac` - Xuất sắc (≥8.0)
- `Kha` - Khá (7.0-7.9)
- `Trung binh` - Trung bình (5.0-6.9)
- `Yeu` - Yếu (<5.0)

---

### 6. `integrated_scores` - Điểm tích hợp

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (FK) | Mã sinh viên |
| `original_score` | FLOAT | Điểm gốc |
| `integrated_score` | FLOAT | Điểm tích hợp |
| `score_difference` | FLOAT | Chênh lệch |
| `classification` | VARCHAR | Phân loại (Giỏi/Khá/TB/Yếu) |
| `exercise_avg` | FLOAT | Điểm TB bài tập |
| `midterm_avg` | FLOAT | Điểm TB giữa kỳ |
| `final_avg` | FLOAT | Điểm TB cuối kỳ |
| `total_exercises` | INTEGER | Tổng số bài tập |

**Công thức điểm tích hợp:**
```
integrated_score = exercise_avg × 30% + midterm_avg × 30% + final_avg × 40%
```

---

### 7. `exercise_details` - Chi tiết bài tập

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `student_id` | INTEGER (FK) | Mã sinh viên |
| `course_code` | VARCHAR | Mã môn học |
| `skill_code` | VARCHAR | Mã kỹ năng |
| `exercise_number` | INTEGER | Số thứ tự bài tập |
| `score` | FLOAT | Điểm bài tập (0-10) |
| `completion_time` | FLOAT | Thời gian hoàn thành (phút) |
| `is_anomaly` | BOOLEAN | Có bất thường không |

---

## 📊 THỐNG KÊ DỮ LIỆU

| Bảng | Số bản ghi (ước tính) |
|------|----------------------|
| students | ~300 |
| student_csv_data | ~300 |
| course_scores | ~1,200 (300 × 4 môn) |
| skill_evaluations | ~4,800 (300 × 16 kỹ năng) |
| classifications | ~300 |
| integrated_scores | ~300 |
| exercise_details | ~15,000+ |

---

## 🔗 QUAN HỆ GIỮA CÁC BẢNG

1. **students** là bảng trung tâm, các bảng khác tham chiếu qua `student_id`
2. **1:1** - students ↔ student_csv_data, classifications, integrated_scores
3. **1:N** - students → course_scores (4 môn/sinh viên)
4. **1:N** - students → skill_evaluations (16 kỹ năng/sinh viên)
5. **1:N** - students → exercise_details (nhiều bài tập/sinh viên)

---

## 🛠️ SQL TẠO BẢNG (Supabase)

```sql
-- 1. Students
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    class VARCHAR(20),
    khoa VARCHAR(100),
    sex VARCHAR(10)
);

-- 2. Student CSV Data
CREATE TABLE student_csv_data (
    student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
    midterm_score FLOAT DEFAULT 0,
    final_score FLOAT DEFAULT 0,
    homework_score FLOAT DEFAULT 0,
    total_score FLOAT DEFAULT 0,
    attendance_rate FLOAT DEFAULT 0,
    assignment_completion FLOAT DEFAULT 0,
    study_hours_per_week INTEGER DEFAULT 0,
    participation_score INTEGER DEFAULT 0,
    late_submissions INTEGER DEFAULT 0,
    lms_usage_hours INTEGER DEFAULT 0,
    response_quality INTEGER DEFAULT 0,
    behavior_score_100 INTEGER DEFAULT 0
);

-- 3. Course Scores
CREATE TABLE course_scores (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_code VARCHAR(10),
    score FLOAT DEFAULT 0,
    time_minutes INTEGER DEFAULT 0,
    midterm_score FLOAT DEFAULT 0,
    final_score FLOAT DEFAULT 0,
    homework_score FLOAT DEFAULT 0,
    UNIQUE(student_id, course_code)
);

-- 4. Skill Evaluations
CREATE TABLE skill_evaluations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_code VARCHAR(10),
    skill_code VARCHAR(20),
    score FLOAT DEFAULT 0,
    level VARCHAR(20),
    passed BOOLEAN DEFAULT FALSE,
    UNIQUE(student_id, course_code, skill_code)
);

-- 5. Classifications
CREATE TABLE classifications (
    student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
    kmeans_prediction VARCHAR(20),
    knn_prediction VARCHAR(20),
    final_level VARCHAR(20),
    normalization_method VARCHAR(20),
    anomaly_detected BOOLEAN DEFAULT FALSE,
    anomaly_reasons JSONB DEFAULT '[]'
);

-- 6. Integrated Scores
CREATE TABLE integrated_scores (
    student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
    original_score FLOAT DEFAULT 0,
    integrated_score FLOAT DEFAULT 0,
    score_difference FLOAT DEFAULT 0,
    classification VARCHAR(20),
    exercise_avg FLOAT DEFAULT 0,
    midterm_avg FLOAT DEFAULT 0,
    final_avg FLOAT DEFAULT 0,
    total_exercises INTEGER DEFAULT 0
);

-- 7. Exercise Details
CREATE TABLE exercise_details (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_code VARCHAR(10),
    skill_code VARCHAR(20),
    exercise_number INTEGER,
    score FLOAT DEFAULT 0,
    completion_time FLOAT DEFAULT 0,
    is_anomaly BOOLEAN DEFAULT FALSE,
    UNIQUE(student_id, course_code, skill_code, exercise_number)
);

-- Indexes
CREATE INDEX idx_course_scores_student ON course_scores(student_id);
CREATE INDEX idx_skill_evaluations_student ON skill_evaluations(student_id);
CREATE INDEX idx_exercise_details_student ON exercise_details(student_id);
```

---

## 📝 GHI CHÚ

- Database được host trên **Supabase** (PostgreSQL)
- Sử dụng **UPSERT** để tránh duplicate khi sync
- Dữ liệu được sync từ local lên cloud qua API `/api/sync-supabase`
- Tất cả điểm số đều theo thang 10
