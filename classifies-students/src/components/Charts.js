import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from 'chart.js';
import '../App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function safeToNumber(v) {
  if (v === null || v === undefined) return NaN;
  if (typeof v === 'number') return v;
  const n = Number(v);
  return Number.isNaN(n) ? NaN : n;
}

function detectNumericFields(items = []) {
  const counts = {};
  if (!items || items.length === 0) return [];
  for (const it of items) {
    for (const key of Object.keys(it)) {
      const val = safeToNumber(it[key]);
      if (!Number.isNaN(val)) counts[key] = (counts[key] || 0) + 1;
    }
  }
  // keep fields that have numeric values in at least 30% of records
  const min = Math.max(1, Math.floor(items.length * 0.3));
  return Object.entries(counts).filter(([k, c]) => c >= min).map(([k]) => k);
}

export default function Charts({ students = [], filteredStudents = [], onLevelFilter = () => {}, currentFilter = '' }) {
  const navigate = useNavigate();
  const [metric, setMetric] = useState(null);
  const [viewMode, setViewMode] = useState('charts'); // 'charts' or 'table'
  const [showCharts, setShowCharts] = useState(true);
  const [alwaysShowAllLevels, setAlwaysShowAllLevels] = useState(true);
  const [showLegend, setShowLegend] = useState(true);

  const displayLabel = (level) => {
    if (!level) return '';
    return level === 'Xuat sac' ? 'Xuất sắc'
      : level === 'Kha' ? 'Khá'
      : level === 'Trung binh' ? 'Trung bình'
      : level === 'Yeu' ? 'Yếu'
      : level;
  };

  // Chuẩn hóa giá trị level từ database -> trả về key nội bộ ('Xuat sac','Kha','Trung binh','Yeu')
  const canonicalizeLevel = (v) => {
    if (!v && v !== 0) return null;
    const s = String(v).normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().replace(/[^a-z0-9]/g, '');
    if (!s) return null;
    if (s === 'xuatsac' || s === 'gioi' || s === 'xuat') return 'Xuat sac';
    if (s === 'kha') return 'Kha';
    if (s === 'trungbinh' || s === 'trung' || s === 'trungbin') return 'Trung binh';
    if (s === 'yeu' || s === 'kem') return 'Yeu';
    // if already matches internal keys (without accent)
    if (s === 'xuatsac' || s === 'kha' || s === 'trungbinh' || s === 'yeu') return s === 'xuatsac' ? 'Xuat sac' : s === 'kha' ? 'Kha' : s === 'trungbinh' ? 'Trung binh' : 'Yeu';
    return null;
  };
  const levels = useMemo(() => {
    // Định nghĩa thứ tự cố định cho các level
    const levelOrder = ['Xuat sac', 'Kha', 'Trung binh', 'Yeu'];
    const map = new Map();
    
    // Khởi tạo tất cả các level với giá trị 0
    levelOrder.forEach(level => map.set(level, 0));
    
    // Đếm số lượng sinh viên cho mỗi level
    for (const s of students) {
      const raw = (s && (s.level_prediction ?? s.predicted_level ?? s.level ?? s.level_pred)) || '';
      const lv = canonicalizeLevel(raw) || raw;
      if (levelOrder.includes(lv)) {
        map.set(lv, (map.get(lv) || 0) + 1);
      }
    }
    
    // Trả về mảng với thứ tự cố định
    return levelOrder.map(level => [level, map.get(level)]);
  }, [students]);

  // Use filteredStudents for charting, but keep `students` (full set) for distribution table
  const dataSource = (filteredStudents && filteredStudents.length) ? filteredStudents : students;
  const numericFields = useMemo(() => detectNumericFields(dataSource), [dataSource]);

  // choose a default metric: look for common names
  useMemo(() => {
    if (metric) return;
    const prefs = ['course_avg', 'avg_course', 'subject_avg', 'avg_score', 'score', 'assignment_score', 'hw_score', 'lmf_time'];
    for (const p of prefs) if (numericFields.includes(p)) { setMetric(p); return; }
    if (numericFields.length > 0) setMetric(numericFields[0]);
  }, [numericFields]);

  const pieData = useMemo(() => {
    // Build counts from current dataSource (so pie reflects current filters)
    const levelOrder = ['Xuat sac', 'Kha', 'Trung binh', 'Yeu'];
    const counts = levelOrder.reduce((acc, k) => ({ ...acc, [k]: 0 }), {});
    for (const s of dataSource) {
      const raw = (s && (s.level_prediction ?? s.predicted_level ?? s.level ?? s.level_pred)) || '';
      const lv = canonicalizeLevel(raw) || raw;
      if (levelOrder.includes(lv)) counts[lv] = (counts[lv] || 0) + 1;
    }
    const present = levelOrder.filter(k => counts[k] > 0);
    // If user requested always show all levels, return fixed 4 slices (zeros allowed)
    if (alwaysShowAllLevels) {
      return {
        labels: levelOrder.map(k => displayLabel(k)),
        datasets: [{ label: 'Số sinh viên', data: levelOrder.map(k => counts[k] || 0), backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'], hoverOffset: 8 }]
      };
    }

    if (present.length === 1) {
      const k = present[0];
      const color = k === 'Xuat sac' ? '#10B981' : k === 'Kha' ? '#3B82F6' : k === 'Trung binh' ? '#F59E0B' : '#EF4444';
      return { labels: [displayLabel(k)], datasets: [{ label: 'Số sinh viên', data: [counts[k]], backgroundColor: [color], hoverOffset: 8 }] };
    }
    return {
      labels: levelOrder.map(k => displayLabel(k)),
      datasets: [{ label: 'Số sinh viên', data: levelOrder.map(k => counts[k] || 0), backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'], hoverOffset: 8 }]
    };
  }, [dataSource]);

  const barData = useMemo(() => {
    if (!metric) return null;
    const levelOrder = ['Xuat sac', 'Kha', 'Trung binh', 'Yeu'];
    const sums = levelOrder.reduce((acc, k) => ({ ...acc, [k]: 0 }), {});
    const counts = levelOrder.reduce((acc, k) => ({ ...acc, [k]: 0 }), {});
    for (const s of dataSource) {
      const raw = (s && (s.level_prediction ?? s.predicted_level ?? s.level ?? s.level_pred)) || '';
      const lv = canonicalizeLevel(raw) || raw;
      const v = safeToNumber(s ? s[metric] : NaN);
      if (!Number.isNaN(v) && levelOrder.includes(lv)) {
        sums[lv] += v;
        counts[lv] += 1;
      }
    }
  const nonZero = levelOrder.filter(l => counts[l] > 0);
  const keys = (!alwaysShowAllLevels && nonZero.length === 1) ? nonZero : levelOrder;
    const averages = keys.map(k => counts[k] === 0 ? 0 : +(sums[k] / counts[k]).toFixed(2));
    const labels = keys.map(k => displayLabel(k));
    const colors = keys.map(k => k === 'Xuat sac' ? '#10B981' : k === 'Kha' ? '#3B82F6' : k === 'Trung binh' ? '#F59E0B' : '#EF4444');
    return { labels, datasets: [{ label: `Trung bình ${metric}`, data: averages, backgroundColor: colors }] };
  }, [dataSource, metric, levels]);

  // preferred metrics to auto-plot
  const preferredMetrics = ['course_avg','avg_course','subject_avg','avg_score','score','assignment_score','assignment_avg','hw_score','lmf_time','time_spent','time_behavior'];
  const autoMetrics = preferredMetrics.filter(m => numericFields.includes(m));

  const buildBarFor = (m) => {
    // Định nghĩa thứ tự cố định cho các level
    const levelOrder = ['Xuat sac', 'Kha', 'Trung binh', 'Yeu'];
    const sums = {};
    const counts = {};
    
    // Khởi tạo với giá trị 0 cho tất cả các level
    levelOrder.forEach(level => {
      sums[level] = 0;
      counts[level] = 0;
    });

    // Tính tổng và đếm cho mỗi level
    for (const s of dataSource) {
      const raw = (s && (s.level_prediction ?? s.predicted_level ?? s.level ?? s.level_pred)) || '';
      const lv = canonicalizeLevel(raw) || raw;
      const v = safeToNumber(s ? s[m] : NaN);
      if (!Number.isNaN(v) && levelOrder.includes(lv)) {
        sums[lv] = (sums[lv] || 0) + v;
        counts[lv] = (counts[lv] || 0) + 1;
      }
    }

    // Nếu dữ liệu đã được lọc chỉ còn một level, chỉ vẽ level đó
  const nonZeroLevels = levelOrder.filter(l => counts[l] && counts[l] > 0);
  const keys = (!alwaysShowAllLevels && nonZeroLevels.length === 1) ? nonZeroLevels : levelOrder;
    const averages = keys.map(k => {
      const s = sums[k] || 0;
      const c = counts[k] || 0;
      return c === 0 ? 0 : +(s / c).toFixed(2);
    });
    const labels = keys.map(k => displayLabel(k));
    const colors = keys.map(k => k === 'Xuat sac' ? '#10B981' : k === 'Kha' ? '#3B82F6' : k === 'Trung binh' ? '#F59E0B' : '#EF4444');
    return {
      labels,
      datasets: [
        {
          label: `Trung bình ${m}`,
          data: averages,
          backgroundColor: colors,
        }
      ]
    };
  };

  if ((!students || students.length === 0) && (!filteredStudents || filteredStudents.length === 0)) {
    return <div>Không có dữ liệu sinh viên để vẽ biểu đồ.</div>;
  }

  return (
    <div style={{ width: '100%', marginTop: 20 }}>
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'center' }}>
        <div style={{ width: '100%', display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 8 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#e6eef8' }}>
            <input type="checkbox" checked={showCharts} onChange={e => setShowCharts(e.target.checked)} />
            <span>Hiển thị biểu đồ</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#e6eef8' }}>
            <input type="checkbox" checked={alwaysShowAllLevels} onChange={e => setAlwaysShowAllLevels(e.target.checked)} />
            <span>Luôn hiển thị 4 mức</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#e6eef8' }}>
            <input type="checkbox" checked={showLegend} onChange={e => setShowLegend(e.target.checked)} />
            <span>Hiển thị chú giải</span>
          </label>
        </div>
        <div style={{ width: 380, background: 'rgba(255,255,255,0.03)', padding: 12, borderRadius: 8 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Phân bố theo Level (Pie)</h3>
            <div>
              <button onClick={() => setViewMode('charts')} style={{ marginRight: 6, padding: '6px 10px' , borderRadius:6, cursor:'pointer' , background: viewMode==='charts' ? '#334155' : 'transparent', color: viewMode==='charts' ? '#fff' : '#e6eef8' }}>Biểu đồ</button>
              <button onClick={() => setViewMode('table')} style={{ padding: '6px 10px', borderRadius:6, cursor:'pointer', background: viewMode==='table' ? '#334155' : 'transparent', color: viewMode==='table' ? '#fff' : '#e6eef8' }}>Bảng</button>
            </div>
          </div>
          {viewMode === 'charts' ? (showCharts ? (
            <div style={{ cursor: 'pointer' }}>
              {/* Khi click vào một slice của Pie, react-chartjs-2 cung cấp mảng 'elements' */}
              <Pie
                data={pieData}
                options={{ plugins: { legend: { display: showLegend } } }}
                onClick={(evt, elements) => {
                  try {
                    if (elements && elements.length > 0) {
                      const idx = elements[0].index;
                      const levelOrder = ['Xuat sac', 'Kha', 'Trung binh', 'Yeu'];
                      const key = levelOrder[idx];
                      if (key) {
                        // Toggle local dashboard filter
                        onLevelFilter(currentFilter === key ? '' : key);
                        // Navigate to students page with level query param (toggle)
                        if (currentFilter === key) {
                          navigate('/students');
                        } else {
                          navigate(`/students?level=${encodeURIComponent(key)}`);
                        }
                      }
                    }
                  } catch (e) {
                    console.warn('Lỗi khi xử lý click Pie:', e);
                  }
                }}
              />
            </div>
          ) : <div style={{ padding: 10 }}>Biểu đồ đang ẩn (bật "Hiển thị biểu đồ" để xem).</div>) : (
            <div style={{ marginTop: 12 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Level</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>Số lượng</th>
                    <th style={{ padding: '8px' }}></th>
                  </tr>
                </thead>
                <tbody>
                  {levels.map(([key, cnt]) => {
                    const isActive = currentFilter === key;
                    const bg = isActive ? (key === 'Xuat sac' ? '#10B981' : key === 'Kha' ? '#3B82F6' : key === 'Trung binh' ? '#F59E0B' : '#EF4444') : 'transparent';
                    const txtColor = isActive ? '#062617' : '#e6eef8';
                    const bd = isActive ? '2px solid rgba(0,0,0,0.08)' : '1px solid rgba(255,255,255,0.06)';
                    return (
                      <tr key={key} style={{ borderTop: '1px solid rgba(255,255,255,0.03)' }}>
                        <td style={{ padding: '8px' }}>{displayLabel(key)}</td>
                        <td style={{ padding: '8px', textAlign: 'right' }}>{cnt}</td>
                        <td style={{ padding: '8px', textAlign: 'right' }}>
                          <button
                            onClick={() => onLevelFilter(isActive ? '' : key)}
                            style={{ padding: '6px 10px', borderRadius: 6, cursor: 'pointer', background: bg, color: txtColor, border: bd }}
                          >
                            {isActive ? 'Bỏ chọn' : 'Xem'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div style={{ minWidth: 420, flex: 1, background: 'rgba(255,255,255,0.03)', padding: 12, borderRadius: 8 }}>
          <h3>Trung bình theo Level (Bar)</h3>

          <div style={{ marginBottom: 8 }}>
            <label style={{ marginRight: 8 }}>Chọn metric:</label>
            <select value={metric || ''} onChange={e => setMetric(e.target.value)}>
              <option value="">-- Chọn metric --</option>
              {numericFields.map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <span style={{ marginLeft: 12, color: '#94a3b8' }}>{numericFields.length === 0 ? 'Không tìm thấy trường số nào tự động.' : ''}</span>
          </div>

          {barData ? <Bar data={barData} options={{ plugins: { legend: { display: showLegend } }, scales: { y: { beginAtZero: true } } }} /> : <div>Chọn metric để hiển thị biểu đồ cột.</div>}
        </div>
      </div>

      {/* Auto render additional bar charts for preferred metrics */}
      {autoMetrics.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3>Các metric tự động (multiple Bar charts)</h3>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {autoMetrics.map(m => (
              <div key={m} style={{ width: 360, background: 'rgba(255,255,255,0.03)', padding: 12, borderRadius: 8 }}>
                <h4 style={{ marginTop: 0 }}>{m}</h4>
                <Bar data={buildBarFor(m)} options={{ plugins: { legend: { display: showLegend } }, scales: { y: { beginAtZero: true } } }} />
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 18, color: '#9ca3af' }}>
        <strong>Ghi chú:</strong> Component tự dò các trường số trong dữ liệu (ví dụ: điểm, trung bình, thời gian). Nếu bạn muốn tên trường chính xác (ví dụ `level_prediction`, `course_avg`, `assignment_score`), hãy đảm bảo dữ liệu trả về chứa các trường đó.
      </div>
    </div>
  );
}
