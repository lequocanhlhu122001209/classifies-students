"""
Phân tích lý do thay đổi xếp loại
"""
from supabase import create_client

SUPABASE_URL = "https://odmtndvllclmrwczcyvs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lấy dữ liệu version cũ (version 1)
old_result = supabase.table('classification_history').select('*').eq('version', 1).execute()
old_data = {r['student_id']: r for r in old_result.data}

# Lấy dữ liệu mới
new_result = supabase.table('classifications').select('*').execute()
new_data = {r['student_id']: r for r in new_result.data}

print("=" * 80)
print("PHÂN TÍCH LÝ DO THAY ĐỔI XẾP LOẠI")
print("=" * 80)

# Thống kê version cũ
old_stats = {'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0}
for r in old_data.values():
    level = r.get('final_level', '')
    if level in old_stats:
        old_stats[level] += 1

print("\n📊 THỐNG KÊ VERSION CŨ (trước khi phân loại lại):")
for level, count in old_stats.items():
    pct = count / len(old_data) * 100 if old_data else 0
    print(f"   {level}: {count} ({pct:.1f}%)")

# Thống kê version mới
new_stats = {'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0}
for r in new_data.values():
    level = r.get('final_level', '')
    if level in new_stats:
        new_stats[level] += 1

print("\n📊 THỐNG KÊ VERSION MỚI (sau khi phân loại lại):")
for level, count in new_stats.items():
    pct = count / len(new_data) * 100 if new_data else 0
    print(f"   {level}: {count} ({pct:.1f}%)")

# Phân tích thay đổi
print("\n" + "=" * 80)
print("📈 PHÂN TÍCH THAY ĐỔI")
print("=" * 80)

changes = {'up': [], 'down': [], 'same': 0}
level_order = ['Yeu', 'Trung binh', 'Kha', 'Xuat sac']

for student_id, new_class in new_data.items():
    if student_id in old_data:
        old_class = old_data[student_id]
        old_level = old_class.get('final_level', '')
        new_level = new_class.get('final_level', '')
        
        if old_level == new_level:
            changes['same'] += 1
        elif old_level in level_order and new_level in level_order:
            old_idx = level_order.index(old_level)
            new_idx = level_order.index(new_level)
            
            if new_idx > old_idx:
                changes['up'].append({
                    'student_id': student_id,
                    'old': old_level,
                    'new': new_level,
                    'kmeans_old': old_class.get('kmeans_prediction', ''),
                    'kmeans_new': new_class.get('kmeans_prediction', ''),
                    'anomaly_old': old_class.get('anomaly_detected', False),
                    'anomaly_new': new_class.get('anomaly_detected', False)
                })
            else:
                changes['down'].append({
                    'student_id': student_id,
                    'old': old_level,
                    'new': new_level,
                    'kmeans_old': old_class.get('kmeans_prediction', ''),
                    'kmeans_new': new_class.get('kmeans_prediction', ''),
                    'anomaly_old': old_class.get('anomaly_detected', False),
                    'anomaly_new': new_class.get('anomaly_detected', False)
                })

print(f"\n📊 Tổng kết thay đổi:")
print(f"   • Giữ nguyên: {changes['same']}")
print(f"   • Tăng hạng: {len(changes['up'])}")
print(f"   • Giảm hạng: {len(changes['down'])}")

# Phân tích lý do tăng hạng
print(f"\n🔼 CHI TIẾT TĂNG HẠNG (top 10):")
for i, c in enumerate(changes['up'][:10], 1):
    reason = ""
    if c['anomaly_old'] and not c['anomaly_new']:
        reason = "Không còn bị đánh dấu bất thường"
    elif c['kmeans_old'] != c['kmeans_new']:
        reason = f"K-means phân cụm lại: {c['kmeans_old']} -> {c['kmeans_new']}"
    else:
        reason = "Điều chỉnh sau phân loại"
    
    print(f"   {i}. ID {c['student_id']}: {c['old']} -> {c['new']}")
    print(f"      Lý do: {reason}")

# Phân tích lý do giảm hạng
if changes['down']:
    print(f"\n🔽 CHI TIẾT GIẢM HẠNG (top 10):")
    for i, c in enumerate(changes['down'][:10], 1):
        reason = ""
        if not c['anomaly_old'] and c['anomaly_new']:
            reason = "Bị phát hiện bất thường"
        elif c['kmeans_old'] != c['kmeans_new']:
            reason = f"K-means phân cụm lại: {c['kmeans_old']} -> {c['kmeans_new']}"
        else:
            reason = "Điều chỉnh sau phân loại"
        
        print(f"   {i}. ID {c['student_id']}: {c['old']} -> {c['new']}")
        print(f"      Lý do: {reason}")

print("\n" + "=" * 80)
print("💡 GIẢI THÍCH:")
print("=" * 80)
print("""
K-means là thuật toán phân cụm TƯƠNG ĐỐI, không dựa trên ngưỡng cố định.

Khi chạy lại phân loại:
1. K-means phân 300 sinh viên thành 4 cụm dựa trên điểm số + hành vi
2. Cụm có điểm TB cao nhất -> Xuất sắc, thấp nhất -> Yếu
3. Nếu dữ liệu thay đổi (thêm/bớt sinh viên), ranh giới cụm sẽ thay đổi
""")
