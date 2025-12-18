# -*- coding: utf-8 -*-
"""
Tạo hình ảnh so sánh chi tiết để thuyết trình
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import rcParams

rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Tạo figure lớn với 3x2 subplot
fig = plt.figure(figsize=(16, 14))
fig.suptitle('HE THONG PHAN LOAI SINH VIEN - SO SANH CHI TIET', fontsize=18, fontweight='bold', y=0.98)

# ========== 1. QUY TRÌNH PHÂN LOẠI ==========
ax1 = fig.add_subplot(3, 2, 1)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title('1. QUY TRINH PHAN LOAI SINH VIEN', fontweight='bold', fontsize=12, pad=10)

# Vẽ các bước
boxes = [
    (1, 7.5, 'DU LIEU\nSINH VIEN', '#3498db'),
    (4, 7.5, 'CHUAN HOA\n(MinMax)', '#9b59b6'),
    (7, 7.5, 'K-MEANS\nPhan cum', '#e74c3c'),
    (4, 4, 'KNN\nTinh chinh', '#2ecc71'),
    (7, 4, 'PHAT HIEN\nBat thuong', '#f39c12'),
    (4, 0.5, 'KET QUA\nXuat sac/Kha/TB/Yeu', '#1abc9c'),
]

for x, y, text, color in boxes:
    rect = mpatches.FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, boxstyle="round,pad=0.05", 
                                    facecolor=color, edgecolor='black', linewidth=2)
    ax1.add_patch(rect)
    ax1.text(x, y, text, ha='center', va='center', fontsize=8, fontweight='bold', color='white')

# Vẽ mũi tên
arrows = [(2.2, 7.5, 1.2, 0), (5.2, 7.5, 1.2, 0), (7, 6.5, 0, -1.2),
          (5.2, 4, 1.2, 0), (4, 3, 0, -1.2)]
for x, y, dx, dy in arrows:
    ax1.annotate('', xy=(x+dx, y+dy), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))


# ========== 2. SO SÁNH K-MEANS vs KNN ==========
ax2 = fig.add_subplot(3, 2, 2)
ax2.axis('off')
ax2.set_title('2. SO SANH K-MEANS va KNN', fontweight='bold', fontsize=12, pad=10)

comparison_text = """
┌─────────────────────────────────────────────────────────────────┐
│                    K-MEANS (Phan cum)                           │
├─────────────────────────────────────────────────────────────────┤
│  • Khong can du lieu da gan nhan                                │
│  • Tu dong chia thanh 4 nhom                                    │
│  • Dua tren khoang cach den tam cum                             │
│  • Do chinh xac: 85.2%                                          │
│  • Nhuoc diem: Nham lan o ranh gioi                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    KNN (Phan loai)                              │
├─────────────────────────────────────────────────────────────────┤
│  • Can du lieu da gan nhan (tu K-means)                         │
│  • Tim 5 sinh vien gan nhat (k=5)                               │
│  • Bo phieu da so de phan loai                                  │
│  • Do chinh xac: 100%                                           │
│  • Xu ly tot truong hop ranh gioi                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 KET HOP (K-means + KNN)                         │
├─────────────────────────────────────────────────────────────────┤
│  K-means tao nhan ban dau → KNN hoc va tinh chinh               │
│  Do chinh xac: 98.1% | Dong thuan: 98.1%                        │
└─────────────────────────────────────────────────────────────────┘
"""
ax2.text(0.5, 0.5, comparison_text, transform=ax2.transAxes, fontsize=9,
         verticalalignment='center', horizontalalignment='center',
         fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))


# ========== 3. VÍ DỤ KNN HOẠT ĐỘNG ==========
ax3 = fig.add_subplot(3, 2, 3)
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.set_xlabel('Diem trung binh', fontweight='bold')
ax3.set_ylabel('Gio hoc/tuan', fontweight='bold')
ax3.set_title('3. VI DU: KNN PHAN LOAI SINH VIEN MOI', fontweight='bold', fontsize=12, pad=10)

# Vẽ các sinh viên đã có (đã được phân loại)
np.random.seed(42)
# Xuất sắc (điểm cao, giờ học nhiều)
xs_x = np.random.uniform(8, 9.5, 8)
xs_y = np.random.uniform(30, 40, 8)
ax3.scatter(xs_x, xs_y, c='#2ecc71', s=100, label='Xuat sac', marker='o', edgecolors='black')

# Khá
kha_x = np.random.uniform(6.5, 8, 10)
kha_y = np.random.uniform(20, 32, 10)
ax3.scatter(kha_x, kha_y, c='#3498db', s=100, label='Kha', marker='o', edgecolors='black')

# Trung bình
tb_x = np.random.uniform(5, 7, 8)
tb_y = np.random.uniform(12, 22, 8)
ax3.scatter(tb_x, tb_y, c='#f39c12', s=100, label='Trung binh', marker='o', edgecolors='black')

# Yếu
yeu_x = np.random.uniform(3, 5.5, 6)
yeu_y = np.random.uniform(5, 15, 6)
ax3.scatter(yeu_x, yeu_y, c='#e74c3c', s=100, label='Yeu', marker='o', edgecolors='black')

# Sinh viên MỚI cần phân loại
new_x, new_y = 7.2, 26
ax3.scatter(new_x, new_y, c='yellow', s=300, marker='*', edgecolors='red', linewidths=2, label='SV MOI (?)', zorder=5)

# Vẽ vòng tròn k=5 láng giềng
circle = plt.Circle((new_x, new_y), 3.5, fill=False, color='red', linestyle='--', linewidth=2)
ax3.add_patch(circle)
ax3.text(new_x+0.3, new_y+4, 'Tim 5 SV\ngan nhat', fontsize=9, color='red', fontweight='bold')

# Kết quả
ax3.text(8.5, 2, '5 SV gan nhat:\n3 Kha, 1 XS, 1 TB\n→ KET QUA: KHA', fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9), fontweight='bold')

ax3.legend(loc='upper left', fontsize=9)
ax3.grid(True, alpha=0.3)


# ========== 4. PHÁT HIỆN BẤT THƯỜNG ==========
ax4 = fig.add_subplot(3, 2, 4)
ax4.axis('off')
ax4.set_title('4. PHAT HIEN BAT THUONG (GIAN LAN)', fontweight='bold', fontsize=12, pad=10)

anomaly_text = """
+------------------------------------------------------------------+
|  DIEU KIEN PHAT HIEN GIAN LAN                                    |
+------------------------------------------------------------------+
|                                                                  |
|  [1] MUC DO 1 - RAT NGHIEM TRONG:                                |
|      Diem >= 9.5 + Thoi gian < 2 phut                            |
|      -> Ha xuong YEU                                             |
|                                                                  |
|  [2] MUC DO 2 - NGHIEM TRONG:                                    |
|      Diem >= 9.0 + Thoi gian < 5 phut                            |
|      -> Ha xuong TRUNG BINH                                      |
|                                                                  |
|  [3] MUC DO 3 - DANG NGHI:                                       |
|      Diem >= 8.0 + Thoi gian < 10 phut                           |
|      -> Ha 1 muc                                                 |
|                                                                  |
|  [4] HANH VI XAU:                                                |
|      Vang mat > 50% hoac Hanh vi < 50 diem                       |
|      -> Ha 1-2 muc                                               |
|                                                                  |
+------------------------------------------------------------------+
|  KET QUA: Phat hien 38/300 sinh vien bat thuong (12.7%)          |
+------------------------------------------------------------------+
"""
ax4.text(0.5, 0.5, anomaly_text, transform=ax4.transAxes, fontsize=9,
         verticalalignment='center', horizontalalignment='center',
         fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='#ffebee', alpha=0.9))


# ========== 5. KẾT QUẢ PHÂN LOẠI ==========
ax5 = fig.add_subplot(3, 2, 5)
categories = ['Xuat sac', 'Kha', 'Trung binh', 'Yeu']
old_data = [7, 126, 131, 22]
new_data = [58, 95, 109, 29]
changes = ['+51', '-31', '-22', '+7']

x = np.arange(len(categories))
width = 0.35

bars1 = ax5.bar(x - width/2, old_data, width, label='TRUOC (286 SV)', 
                color=['#a8e6cf', '#88d8b0', '#ffeaa7', '#fab1a0'], edgecolor='black', linewidth=1)
bars2 = ax5.bar(x + width/2, new_data, width, label='SAU (300 SV)', 
                color=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'], edgecolor='black', linewidth=1)

ax5.set_ylabel('So luong sinh vien', fontweight='bold')
ax5.set_title('5. KET QUA: TRUOC va SAU PHAN LOAI LAI', fontweight='bold', fontsize=12, pad=10)
ax5.set_xticks(x)
ax5.set_xticklabels(categories)
ax5.legend(loc='upper right')
ax5.grid(axis='y', alpha=0.3)

# Thêm số liệu và thay đổi
for i, (bar1, bar2, change) in enumerate(zip(bars1, bars2, changes)):
    ax5.annotate(f'{int(bar1.get_height())}', xy=(bar1.get_x() + bar1.get_width()/2, bar1.get_height()),
                 ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax5.annotate(f'{int(bar2.get_height())}', xy=(bar2.get_x() + bar2.get_width()/2, bar2.get_height()),
                 ha='center', va='bottom', fontsize=10, fontweight='bold')
    # Hiển thị thay đổi
    color = 'green' if change.startswith('+') else 'red'
    ax5.annotate(change, xy=(x[i], max(bar1.get_height(), bar2.get_height()) + 8),
                 ha='center', fontsize=11, fontweight='bold', color=color)

# ========== 6. THỐNG KÊ TỔNG HỢP ==========
ax6 = fig.add_subplot(3, 2, 6)
ax6.axis('off')
ax6.set_title('6. THONG KE TONG HOP', fontweight='bold', fontsize=12, pad=10)

summary_text = """
+==================================================================+
|                    KET QUA HE THONG                              |
+==================================================================+
|                                                                  |
|   * TONG SO SINH VIEN:           300 sinh vien                   |
|   * SO MON HOC:                  4 mon                           |
|   * SO KY NANG:                  16 ky nang                      |
|                                                                  |
+------------------------------------------------------------------+
|                    DO CHINH XAC                                  |
+------------------------------------------------------------------+
|                                                                  |
|   [OK] K-means:                   85.2%                          |
|   [OK] KNN:                       100%                           |
|   [OK] K-means + KNN dong thuan:  98.1%                          |
|                                                                  |
+------------------------------------------------------------------+
|                    PHAT HIEN BAT THUONG                          |
+------------------------------------------------------------------+
|                                                                  |
|   [!] So truong hop bat thuong:   38 sinh vien (12.7%)           |
|   [1] Muc do 1 (nghiem trong):    13 truong hop                  |
|   [2] Muc do 2:                   5 truong hop                   |
|   [3] Muc do 3:                   20 truong hop                  |
|                                                                  |
+==================================================================+
"""
ax6.text(0.5, 0.5, summary_text, transform=ax6.transAxes, fontsize=9,
         verticalalignment='center', horizontalalignment='center',
         fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='#e8f5e9', alpha=0.9))


# Footer
fig.text(0.5, 0.01, 
         'He thong Phan loai Sinh vien Thong minh | K-means + KNN + Phat hien Bat thuong | Thanh vien: Le Quoc Anh, Le Quoc Bao',
         ha='center', fontsize=10, style='italic', 
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('reports/so_sanh_chi_tiet.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig('so_sanh_chi_tiet.png', dpi=150, bbox_inches='tight', facecolor='white')
print('✅ Đã tạo hình ảnh: so_sanh_chi_tiet.png')
print('✅ Đã lưu vào: reports/so_sanh_chi_tiet.png')
