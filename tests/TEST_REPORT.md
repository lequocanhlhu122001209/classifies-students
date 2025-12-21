# 📊 BÁO CÁO KẾT QUẢ TEST - HỆ THỐNG PHÂN LOẠI SINH VIÊN

**Ngày test:** 2025-12-21  
**Tổng số mẫu:** 300 sinh viên  
**Features:** 12 đặc trưng (điểm số + hành vi)

---

## 1. PHÂN BỐ DỮ LIỆU

| Mức độ | Số lượng | Tỷ lệ |
|--------|----------|-------|
| Xuất sắc | 105 | 35.0% |
| Khá | 108 | 36.0% |
| Trung bình | 87 | 29.0% |
| Yếu | 0 | 0.0% |

---

## 2. TEST TRAIN/TEST SPLIT

| Tỷ lệ Train/Test | Train | Test | Accuracy | Precision | Recall | F1-Score |
|------------------|-------|------|----------|-----------|--------|----------|
| **80%/20%** | 240 | 60 | **81.67%** | 82.02% | 81.67% | 81.81% |
| 70%/30% | 210 | 90 | 78.89% | 78.45% | 78.89% | 78.54% |
| 60%/40% | 180 | 120 | 77.50% | 77.33% | 77.50% | 77.26% |

**Kết luận:** Tỷ lệ 80%/20% cho kết quả tốt nhất với Accuracy 81.67%

---

## 3. SO SÁNH PHƯƠNG PHÁP CHUẨN HÓA

| Phương pháp | Accuracy | F1-Score |
|-------------|----------|----------|
| MinMax | 78.89% | 78.54% |
| **ZScore (Standard)** | **81.11%** | **81.21%** |
| Robust | 76.67% | 76.84% |

**Kết luận:** ZScore cho kết quả tốt nhất với Accuracy 81.11%

---

## 4. CROSS-VALIDATION (5-Fold)

| Fold | Accuracy |
|------|----------|
| 1 | 85.0% |
| 2 | 88.3% |
| 3 | 88.3% |
| 4 | 91.7% |
| 5 | 83.3% |

**Mean Accuracy:** 87.33% ± 2.91%

---

## 5. TEST GIÁ TRỊ K (KNN)

| k | Accuracy | F1-Score |
|---|----------|----------|
| 1 | 84.44% | 84.49% |
| **3** | **86.67%** | **86.80%** |
| 5 | 78.89% | 78.54% |
| 7 | 77.78% | 77.45% |
| 9 | 78.89% | 78.33% |
| 11 | 77.78% | 77.52% |

**Kết luận:** k=3 cho kết quả tốt nhất với Accuracy 86.67%

---

## 6. CLASSIFICATION REPORT (Chi tiết)

**Cấu hình:** Train 70% (210) | Test 30% (90)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Xuất sắc | 0.86 | 0.94 | 0.90 | 32 |
| Khá | 0.72 | 0.66 | 0.69 | 32 |
| Trung bình | 0.77 | 0.77 | 0.77 | 26 |
| **Weighted Avg** | **0.78** | **0.79** | **0.79** | 90 |

---

## 7. CONFUSION MATRIX

```
Actual \ Pred    Xuất sắc    Khá    Trung bình
Xuất sắc            30        2         0
Khá                  5       21         6
Trung bình           0        6        20
```

**Phân tích:**
- **Xuất sắc:** 30/32 đúng (93.75%) - Phân loại rất tốt
- **Khá:** 21/32 đúng (65.63%) - Có nhầm lẫn với Xuất sắc và Trung bình
- **Trung bình:** 20/26 đúng (76.92%) - Khá tốt

---

## 8. KẾT LUẬN

### Cấu hình tối ưu:
- **Train/Test Split:** 80%/20%
- **Chuẩn hóa:** ZScore (Standard Scaler)
- **KNN k:** 3
- **Accuracy tổng thể:** ~87% (Cross-validation)

### Điểm mạnh:
- Phân loại "Xuất sắc" rất chính xác (>90%)
- Cross-validation ổn định (std = 2.91%)
- 12 features đủ để phân loại hiệu quả

### Điểm cần cải thiện:
- Phân loại "Khá" còn nhầm lẫn với các class khác
- Cần thêm dữ liệu class "Yếu" để cân bằng

---

## 9. CHẠY LẠI TEST

```bash
python tests/test_classifier.py
```

Kết quả được lưu tại: `tests/test_results.json`
