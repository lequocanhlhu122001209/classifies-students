import { useState, useEffect, useMemo } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { syncManager } from './utils/syncManager';
import './App.css';
import Charts from './components/Charts';
import StudentsTable from './components/StudentsTable';
import DepartmentStats from './components/DepartmentStats';
import Navigation from './components/Navigation';
import LevelCards from './components/LevelCards';
import StudentManagement from './pages/StudentManagement';
import AddStudent from './pages/AddStudent';
import EditStudentPage from './pages/EditStudentPage';


function Dashboard() {
  const [students, setStudents] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [levelFilter, setLevelFilter] = useState('');
  const [classFilter, setClassFilter] = useState('');

  // Filtered students for both table and charts
  const filteredStudents = useMemo(() => {
    return students.filter(student => {
      // Search by name or ID
      const searchLower = searchText.toLowerCase();
      const matchesSearch = !searchText || 
        (student.name?.toLowerCase().includes(searchLower) || 
         student.student_id?.toString().includes(searchText));

  // Filter by level (prefer normalized key)
  const studentLevel = student.level_key ?? student.level_prediction ?? student.predicted_level ?? student.level ?? student.level_pred;
  const matchesLevel = !levelFilter || studentLevel === levelFilter;

      // Filter by class
      const matchesClass = !classFilter || 
        student.class_id === classFilter;

      return matchesSearch && matchesLevel && matchesClass;
    });
  }, [students, searchText, levelFilter, classFilter]);

  // Debug: log filter state and distribution when students or filters change
  useEffect(() => {
    try {
      const distByKey = students.reduce((acc, s) => {
        const k = s.level_key ?? '<<null>>';
        acc[k] = (acc[k] || 0) + 1;
        return acc;
      }, {});
      const distByRaw = students.reduce((acc, s) => {
        const k = (s.level_prediction ?? s.predicted_level ?? s.level ?? s.level_pred) || '<<none>>';
        acc[k] = (acc[k] || 0) + 1;
        return acc;
      }, {});

  console.log('--- FILTER DEBUG ---');
  console.log('filters -> levelFilter:', levelFilter, ', classFilter:', classFilter, ', searchText:', searchText);
  console.log('students total:', students.length);
  console.log('distribution by level_key:', distByKey);
  console.log('distribution by raw prediction/level:', distByRaw);
  // More verbose diagnostics to help find mismatches
  const uniqueLevelKeys = [...new Set(students.map(s => s.level_key ?? '<<null>>'))];
  const uniqueRawValues = [...new Set(students.flatMap(s => [s.level_prediction, s.predicted_level, s.level, s.level_pred].filter(v => v !== undefined && v !== null && v !== '')))].slice(0, 200);
  console.log('unique level_key values:', uniqueLevelKeys);
  console.log('unique raw label values (sample up to 200):', uniqueRawValues);
  const sample = students.slice(0, 12).map(s => ({ id: s.id, name: s.name, level_key: s.level_key, level_prediction: s.level_prediction, predicted_level: s.predicted_level, level: s.level, level_pred: s.level_pred }));
  console.log('sample students (first 12):', sample);

      const computed = students.filter(student => {
        const searchLower = searchText.toLowerCase();
        const matchesSearch = !searchText || (student.name?.toLowerCase().includes(searchLower) || student.student_id?.toString().includes(searchText));
  const studentLevel = student.level_key ?? student.level_prediction ?? student.predicted_level ?? student.level ?? student.level_pred;
        const matchesLevel = !levelFilter || studentLevel === levelFilter;
        const matchesClass = !classFilter || student.class_id === classFilter;
        return matchesSearch && matchesLevel && matchesClass;
      });
      console.log('computed filtered count:', computed.length);
      console.log('--- end debug ---');
    } catch (e) {
      console.warn('Error while logging filter debug', e);
    }
  }, [students, levelFilter, classFilter, searchText]);

  // Available filters (unique values)
  const filterOptions = useMemo(() => {
    const levels = new Set();
    const classes = new Set();
    
    students.forEach(student => {
      const lv = student.level_key ?? student.level_prediction ?? student.level ?? student.level_pred;
      if (lv) levels.add(lv);
      if (student.class_id) classes.add(student.class_id);
    });

    return {
      levels: Array.from(levels).sort(),
      classes: Array.from(classes).sort()
    };
  }, [students]);

  useEffect(() => {
    async function getStudents() {
      try {
        setLoading(true);
        const data = await syncManager.loadAllStudents();
        setStudents(data);
      } catch (error) {
        console.error('Lỗi tải dữ liệu:', error);
        setSaveStatus({ 
          type: 'error', 
          message: `❌ Lỗi tải dữ liệu: ${error.message}` 
        });
      } finally {
        setLoading(false);
      }
    }

    getStudents();
  }, []);

  if (loading) {
    return <div>Đang tải dữ liệu từ Supabase...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Dashboard Phân loại Sinh viên</h1>
        <p>
          Đã kết nối và tải thành công {students.length} sinh viên
          {filteredStudents.length !== students.length && 
            ` (đang hiển thị ${filteredStudents.length})`
          }
        </p>
        
        {/* Trạng thái lưu dữ liệu */}
        {saveStatus && (
          <div style={{
            marginBottom: '16px',
            padding: '12px 16px',
            borderRadius: '8px',
            background: saveStatus.type === 'success' ? 'rgba(16,185,129,0.1)' : 
                        saveStatus.type === 'error' ? 'rgba(239,68,68,0.1)' : 
                        'rgba(59,130,246,0.1)',
            border: `1px solid ${saveStatus.type === 'success' ? '#10B981' : 
                                 saveStatus.type === 'error' ? '#EF4444' : 
                                 '#3B82F6'}`,
            color: saveStatus.type === 'success' ? '#10B981' : 
                   saveStatus.type === 'error' ? '#EF4444' : 
                   '#3B82F6',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            {saveStatus.message}
          </div>
        )}
        
        {/* Trạng thái đang lưu */}
        {saving && (
          <div style={{
            marginBottom: '16px',
            padding: '12px 16px',
            borderRadius: '8px',
            background: 'rgba(59,130,246,0.1)',
            border: '1px solid #3B82F6',
            color: '#3B82F6',
            fontSize: '14px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <div style={{
              width: '16px',
              height: '16px',
              border: '2px solid #3B82F6',
              borderTop: '2px solid transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
            Đang lưu dữ liệu vào Supabase...
          </div>
        )}
        
        {/* Thống kê theo lớp */}
        {filterOptions.classes.length > 0 && (
          <div style={{
            background: 'rgba(255,255,255,0.03)',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
            border: '1px solid rgba(255,255,255,0.08)'
          }}>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontWeight: 'bold', color: '#60a5fa' }}>📊 Phân bố theo lớp:</span>
              {filterOptions.classes.map(cls => {
                const count = students.filter(s => s.class_id === cls).length;
                return (
                  <span key={cls} style={{ 
                    padding: '4px 8px', 
                    background: 'rgba(96,165,250,0.1)', 
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}>
                    {cls}: <strong>{count}</strong>
                  </span>
                );
              })}
            </div>
          </div>
        )}
        
        {/* Giải thích về 2 cột phân loại */}
        <div style={{
          background: 'rgba(255,255,255,0.05)',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '24px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#60a5fa' }}>Giải thích về 2 cột phân loại:</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '14px' }}>
            <div>
              <h4 style={{ margin: '0 0 8px 0', color: '#10B981' }}>🔵 Phân loại (K-means)</h4>
              <p style={{ margin: '0', lineHeight: '1.5' }}>
                Sử dụng thuật toán K-means clustering để nhóm sinh viên thành 4 cụm dựa trên 
                <strong> Điểm giữa kỳ, Điểm cuối kỳ, Điểm bài tập, Tỷ lệ tham gia, Hoàn thành bài tập, Giờ học/tuần, Điểm tham gia, Nộp muộn, Hoạt động ngoại khóa, Giờ sử dụng LMS, Chất lượng phản hồi, Tổng điểm, Điểm hành vi</strong>. 
                Các cụm được sắp xếp theo thứ tự từ cao xuống thấp: Xuất sắc → Khá → Trung bình → Yếu.
              </p>
            </div>
            <div>
              <h4 style={{ margin: '0 0 8px 0', color: '#3B82F6' }}>🔵 Phân loại (KNN)</h4>
              <p style={{ margin: '0', lineHeight: '1.5' }}>
                Sử dụng thuật toán K-Nearest Neighbors để dự đoán phân loại dựa trên 
                <strong> Điểm giữa kỳ (20%), Điểm cuối kỳ (30%), Điểm bài tập (20%), Tỷ lệ tham gia (10%), Điểm hành vi (10%), Tổng điểm (10%)</strong>. 
                KNN tìm k sinh viên gần nhất để đưa ra dự đoán chính xác hơn.
              </p>
            </div>
          </div>
          <div style={{ marginTop: '12px', padding: '8px', background: 'rgba(59,130,246,0.1)', borderRadius: '4px', fontSize: '13px' }}>
            <strong>💡 Lưu ý:</strong> So sánh 2 cột để đánh giá độ chính xác của từng thuật toán. 
            K-means tốt cho phân nhóm tự nhiên, KNN tốt cho dự đoán dựa trên mẫu tương tự.
            <br/><strong>📊 Ngưỡng phân loại nghiêm ngặt:</strong> Xuất sắc (≥9.0 + tham gia ≥90% + hoàn thành ≥80%), Khá (≥7.5 + tham gia ≥80% + hoàn thành ≥60%), Trung bình (≥6.0 + tham gia ≥70%), Yếu (&lt;6.0).
            <br/><strong>⚠️ Trừ điểm:</strong> Mỗi lần nộp muộn trừ 0.5 điểm.
          </div>
        </div>

        {/* Manual Re-classification Button */}
        <div style={{ 
          marginBottom: '16px',
          display: 'flex',
          justifyContent: 'center',
          gap: '12px'
        }}>
          <button
            onClick={async () => {
              if (saving) return;
              
              setSaving(true);
              setSaveStatus({ type: 'info', message: 'Đang thực hiện phân loại lại...' });
              
              try {
                const result = await syncManager.classifyAndSyncAllStudents();
                setStudents(await syncManager.loadAllStudents());
                
                setSaveStatus({ 
                  type: 'success', 
                  message: `✅ Đã phân loại lại và lưu thành công ${result.successful} sinh viên!` 
                });
              } catch (error) {
                console.error("Lỗi khi phân loại lại:", error);
                setSaveStatus({ 
                  type: 'error', 
                  message: `❌ Lỗi khi phân loại lại: ${error.message}` 
                });
              } finally {
                setSaving(false);
              }
            }}
            disabled={saving}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              border: '1px solid rgba(16,185,129,0.3)',
              background: saving ? 'rgba(16,185,129,0.1)' : 'rgba(16,185,129,0.2)',
              color: saving ? '#6B7280' : '#10B981',
              cursor: saving ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            {saving ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #6B7280',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Đang xử lý...
              </>
            ) : (
              <>
                🔄 Phân loại lại & Lưu vào Supabase
              </>
            )}
          </button>
        </div>

        {/* Search and Filter UI */}
        <div style={{ 
          display: 'flex', 
          gap: 16, 
          marginBottom: 24,
          flexWrap: 'wrap',
          alignItems: 'center'
        }}>
          {/* Search */}
          <div style={{ flex: 1, minWidth: 200 }}>
            <input
              type="text"
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              placeholder="Tìm theo tên hoặc MSSV..."
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 4,
                border: '1px solid rgba(255,255,255,0.2)',
                background: 'rgba(255,255,255,0.05)',
                color: 'inherit'
              }}
            />
          </div>

          {/* Level Filter */}
          <div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <select
                value={levelFilter}
                onChange={e => setLevelFilter(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: 4,
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'inherit'
                }}
              >
                <option value="">Tất cả Level</option>
                {['Xuat sac', 'Kha', 'Trung binh', 'Yeu'].map(level => (
                  <option key={level} value={level}>
                    {level === 'Xuat sac' ? 'Xuất sắc' :
                     level === 'Kha' ? 'Khá' :
                     level === 'Trung binh' ? 'Trung bình' :
                     level === 'Yeu' ? 'Yếu' : level}
                  </option>
                ))}
              </select>

              {/* Quick filter buttons */}
              <div style={{ display: 'flex', gap: 6 }}>
                {[
                  { key: 'Xuat sac', label: 'Xuất sắc', color: '#10B981' },
                  { key: 'Kha', label: 'Khá', color: '#3B82F6' },
                  { key: 'Trung binh', label: 'Trung bình', color: '#F59E0B' },
                  { key: 'Yeu', label: 'Yếu', color: '#EF4444' }
                ].map(btn => (
                  <button
                    key={btn.key}
                    onClick={() => setLevelFilter(levelFilter === btn.key ? '' : btn.key)}
                    title={btn.label}
                    style={{
                      padding: '6px 10px',
                      borderRadius: 6,
                      border: levelFilter === btn.key ? `2px solid ${btn.color}` : '1px solid rgba(255,255,255,0.08)',
                      background: levelFilter === btn.key ? btn.color : 'transparent',
                      color: levelFilter === btn.key ? '#062617' : '#e6eef8',
                      cursor: 'pointer'
                    }}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Class Filter */}
          <div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
              <select
                value={classFilter}
                onChange={e => setClassFilter(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: 4,
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'inherit'
                }}
              >
                <option value="">Tất cả Lớp</option>
                {filterOptions.classes.map(cls => (
                  <option key={cls} value={cls}>{cls}</option>
                ))}
              </select>
              
              {/* Quick class filter buttons */}
              {filterOptions.classes.length > 0 && filterOptions.classes.length <= 8 && (
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {filterOptions.classes.map(cls => (
                    <button
                      key={cls}
                      onClick={() => setClassFilter(classFilter === cls ? '' : cls)}
                      title={`Lọc lớp ${cls}`}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 6,
                        border: classFilter === cls ? '2px solid #60a5fa' : '1px solid rgba(255,255,255,0.08)',
                        background: classFilter === cls ? '#60a5fa' : 'transparent',
                        color: classFilter === cls ? '#fff' : '#e6eef8',
                        cursor: 'pointer',
                        fontSize: '13px'
                      }}
                    >
                      {cls}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Clear Filters */}
          {(searchText || levelFilter || classFilter) && (
            <button
              onClick={() => {
                setSearchText('');
                setLevelFilter('');
                setClassFilter('');
              }}
              style={{
                padding: '8px 16px',
                borderRadius: 4,
                border: '1px solid rgba(255,255,255,0.2)',
                background: 'rgba(255,255,255,0.1)',
                color: 'inherit',
                cursor: 'pointer'
              }}
            >
              Xóa bộ lọc
            </button>
          )}
        </div>

        {/* Department Statistics */}
        <DepartmentStats students={students} />

        {/* Large level cards (Xuất sắc / Khá / Trung bình / Yếu) */}
        <LevelCards students={students} onLevelFilter={setLevelFilter} currentFilter={levelFilter} />

        {/* Charts section */}
        <Charts
          students={students}                // full dataset for distribution table
          filteredStudents={filteredStudents} // data after filters for charts
          onLevelFilter={setLevelFilter}
          currentFilter={levelFilter}
        />

        {/* Table section */}
        <div style={{ marginTop: 32 }}>
          <h2>Danh sách chi tiết</h2>
          <StudentsTable students={filteredStudents} />
        </div>
      </header>
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/students" element={<StudentManagement />} />
          <Route path="/add-student" element={<AddStudent />} />
          <Route path="/edit/:id" element={<EditStudentPage />} />
        </Routes>
      </header>
    </div>
  );
}

export default App;