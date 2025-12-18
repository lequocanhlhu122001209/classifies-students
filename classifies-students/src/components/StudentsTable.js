import React, { useState, useMemo } from 'react';

// Định nghĩa các trường hiển thị và nhãn tương ứng - đưa ra ngoài component
const fieldLabels = {
  'id': 'ID',
  'student_id': 'MSSV',
  'name': 'Họ và tên',
  'level_prediction': 'Phân loại (K-means)',
  'predicted_level': 'Phân loại (KNN)',
  'midterm_score': 'Điểm giữa kỳ',
  'final_score': 'Điểm cuối kỳ',
  'homework_score': 'Điểm bài tập',
  'attendance_rate': 'Tỷ lệ tham gia',
  'assignment_completion': 'Hoàn thành bài tập',
  'study_hours_per_week': 'Giờ học/tuần',
  'participation_score': 'Điểm tham gia',
  'late_submissions': 'Nộp muộn',
  'extra_activities': 'Hoạt động ngoại khóa',
  'lms_usage_hours': 'Giờ sử dụng LMS',
  'response_quality': 'Chất lượng phản hồi',
  'total_score': 'Tổng điểm',
  'attendance_normalized': 'Tham gia chuẩn hóa',
  'assignment_normalized': 'Bài tập chuẩn hóa',
  'study_intensity': 'Cường độ học tập',
  'punctuality_score': 'Điểm đúng giờ',
  'lms_engagement': 'Tương tác LMS',
  'response_quality_normalized': 'Phản hồi chuẩn hóa',
  'behavior_score': 'Điểm hành vi',
  'behavior_score_100': 'Hành vi (100)',
  'attendance_rate_100': 'Tham gia (100)',
  'assignment_completion_100': 'Hoàn thành (100)',
  'expertise_areas': 'Lĩnh vực thế mạnh'
};

export default function StudentsTable({ students = [] }) {
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [selectedExpertise, setSelectedExpertise] = useState('');
  const [minScore, setMinScore] = useState('');
  const [maxScore, setMaxScore] = useState('');
  const rowsPerPage = 10;

  // Hàm định dạng giá trị cho từng loại trường
  const formatFieldValue = (field, value, student) => {
    if (value === null || value === undefined) return '';

    switch (field) {
      case 'midterm_score':
      case 'final_score':
      case 'homework_score':
        // Hiển thị điểm số dạng số nguyên
        return Math.round(Number(value) || 0);
      case 'attendance_rate':
        // Hiển thị chi tiết: tỷ lệ tham gia và số buổi
        const attendanceRate = Number(value) || 0;
        // Đảm bảo giá trị phần trăm nằm trong khoảng 0-100%
        const attendancePercent = Math.min(Math.max(attendanceRate * 100, 0), 100);
        const totalClasses = 30; // Giả sử có 30 buổi học
        const attendedClasses = Math.round(attendanceRate * totalClasses);
        const missedClasses = totalClasses - attendedClasses;
        return `${attendancePercent.toFixed(1)}% (${attendedClasses}/${totalClasses} buổi, vắng ${missedClasses})`;
      case 'assignment_completion':
        // Hiển thị chi tiết: tỷ lệ hoàn thành và số bài
        const completionRate = Number(value) || 0;
        // Đảm bảo giá trị phần trăm nằm trong khoảng 0-100%
        const completionPercent = Math.min(Math.max(completionRate * 100, 0), 100);
        const totalAssignments = 10; // Giả sử có 10 bài tập
        const completedAssignments = Math.round(completionRate * totalAssignments);
        const remainingAssignments = totalAssignments - completedAssignments;
        return `${completionPercent.toFixed(1)}% (${completedAssignments}/${totalAssignments} bài, còn ${remainingAssignments})`;
      case 'attendance_normalized':
      case 'assignment_normalized':
      case 'study_intensity':
      case 'punctuality_score':
      case 'lms_engagement':
      case 'response_quality_normalized':
        // Hiển thị dạng số nguyên
        return Math.round(Number(value) || 0);
      case 'participation_score':
        return Number(value).toFixed(2);
      case 'response_quality':
      case 'total_score':
      case 'behavior_score':
        // Hiển thị dạng số nguyên
        return Math.round(Number(value) || 0);
      case 'behavior_score_100':
      case 'attendance_rate_100':
      case 'assignment_completion_100':
        // Hiển thị dạng phần trăm, đảm bảo trong khoảng 0-100%
        const score100 = Number(value) || 0;
        const clampedScore = Math.min(Math.max(score100, 0), 100);
        return `${clampedScore.toFixed(1)}%`;
      case 'study_hours_per_week':
      case 'lms_usage_hours':
        // Hiển thị dạng số nguyên
        const hours = Math.max(Math.round(Number(value) || 0), 0);
        return `${hours} giờ`;
      case 'late_submissions':
        const lateCount = Number(value) || 0;
        const penalty = lateCount * 0.5;
        return `${lateCount} lần (trừ ${penalty.toFixed(1)} điểm)`;
      case 'extra_activities':
        return Number(value).toFixed(0);
      case 'expertise_areas':
        // Hiển thị lĩnh vực thế mạnh
        if (!value || value === 'Toàn diện') return 'Toàn diện';
        return value; // Trả về chuỗi, sẽ được render trong td
      case 'level_prediction':
      case 'predicted_level':
        // Prefer normalized key stored on student.level_key; support both DB columns
        const levelKey = student?.level_key ?? value ?? student?.level ?? student?.level_pred ?? student?.predicted_level;
        return {
          'Xuat sac': 'Xuất sắc',
          'Kha': 'Khá',
          'Trung binh': 'Trung bình',
          'Yeu': 'Yếu'
        }[levelKey] || levelKey || '';
      default:
        return value.toString();
    }
  };

  // Hàm lấy màu sắc cho từng level
  const getLevelColor = (level) => {
    switch (level) {
      case 'Xuat sac': return '#10B981'; // Xanh lá
      case 'Kha': return '#3B82F6';      // Xanh dương
      case 'Trung binh': return '#F59E0B'; // Cam
      case 'Yeu': return '#EF4444';      // Đỏ
      default: return 'inherit';
    }
  };

  // Lấy danh sách tất cả lĩnh vực thế mạnh có trong dữ liệu
  const allExpertiseAreas = useMemo(() => {
    const expertiseSet = new Set();
    students.forEach(student => {
      if (student.expertise_areas && student.expertise_areas !== 'Toàn diện') {
        student.expertise_areas.split(', ').forEach(area => {
          expertiseSet.add(area.trim());
        });
      }
    });
    return Array.from(expertiseSet).sort();
  }, [students]);

  // Lấy danh sách tất cả level có trong dữ liệu
  const allLevels = useMemo(() => {
    const levelSet = new Set();
    students.forEach(student => {
      if (student.level_prediction) levelSet.add(student.level_prediction);
      if (student.predicted_level) levelSet.add(student.predicted_level);
    });
    return Array.from(levelSet).sort();
  }, [students]);

  // Auto-detect fields to show in table
  const columns = useMemo(() => {
    if (!students.length) return [];
    const sample = students[0] || {};
    
    // Get all fields from data
    const allFields = new Set(
      students.reduce((acc, student) => [...acc, ...Object.keys(student)], [])
    );

    // Đảm bảo các trường quan trọng luôn hiển thị theo thứ tự
    const requiredFields = [
      'id', 
      'student_id', 
      'name', 
      'level_prediction', 
      'predicted_level',
      'midterm_score',           // Điểm giữa kỳ
      'final_score',             // Điểm cuối kỳ
      'homework_score',          // Điểm bài tập
      'attendance_rate',         // Tỷ lệ tham gia
      'assignment_completion',   // Hoàn thành bài tập
      'study_hours_per_week',    // Giờ học/tuần
      'participation_score',     // Điểm tham gia
      'late_submissions',        // Nộp muộn
      'extra_activities',        // Hoạt động ngoại khóa
      'lms_usage_hours',         // Giờ sử dụng LMS
      'response_quality',       // Chất lượng phản hồi
      'total_score',            // Tổng điểm
      'behavior_score',         // Điểm hành vi
      'behavior_score_100',     // Hành vi (100)
      'attendance_rate_100',    // Tham gia (100)
      'assignment_completion_100', // Hoàn thành (100)
      'expertise_areas'         // Lĩnh vực thế mạnh
    ];
    
    // Lọc các trường bắt buộc và thêm các trường khác
    const finalFields = [
      ...requiredFields,
      ...Array.from(allFields).filter(field => !requiredFields.includes(field))
    ];
    
    return finalFields;
  }, [students]);

  // Filter and search data
  const filteredData = useMemo(() => {
    return students.filter(student => {
      // Tìm kiếm theo tên, MSSV
      const matchesSearch = !searchTerm || 
        (student.name && student.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (student.student_id && student.student_id.toLowerCase().includes(searchTerm.toLowerCase()));
      
      // Lọc theo level
      const matchesLevel = !selectedLevel || 
        student.level_prediction === selectedLevel || 
        student.predicted_level === selectedLevel;
      
      // Lọc theo lĩnh vực thế mạnh
      const matchesExpertise = !selectedExpertise || 
        (student.expertise_areas && student.expertise_areas.includes(selectedExpertise));
      
      // Lọc theo điểm số
      const totalScore = Number(student.total_score) || 0;
      const matchesMinScore = !minScore || totalScore >= Number(minScore);
      const matchesMaxScore = !maxScore || totalScore <= Number(maxScore);
      
      return matchesSearch && matchesLevel && matchesExpertise && matchesMinScore && matchesMaxScore;
    });
  }, [students, searchTerm, selectedLevel, selectedExpertise, minScore, maxScore]);

  // Sort and paginate data
  const displayData = useMemo(() => {
    let sorted = [...filteredData];
    if (sortField) {
      sorted.sort((a, b) => {
        const aVal = a[sortField];
        const bVal = b[sortField];
        if (aVal === bVal) return 0;
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        const comp = aVal < bVal ? -1 : 1;
        return sortDirection === 'asc' ? comp : -comp;
      });
    }
    const start = (page - 1) * rowsPerPage;
    return sorted.slice(start, start + rowsPerPage);
  }, [filteredData, sortField, sortDirection, page]);

  const totalPages = Math.ceil(filteredData.length / rowsPerPage);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Reset page when filters change
  React.useEffect(() => {
    setPage(1);
  }, [searchTerm, selectedLevel, selectedExpertise, minScore, maxScore]);

  if (!students.length) {
    return <div>Không có dữ liệu sinh viên.</div>;
  }

  return (
    <div style={{ width: '100%' }}>
      {/* Search and Filter Controls */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '16px', 
        background: 'rgba(255,255,255,0.05)', 
        borderRadius: '8px',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px',
        alignItems: 'center'
      }}>
        {/* Search Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500' }}>Tìm kiếm:</label>
          <input
            type="text"
            placeholder="Tên hoặc MSSV..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.1)',
              color: 'white',
              fontSize: '14px',
              minWidth: '200px'
            }}
          />
        </div>

        {/* Level Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500' }}>Phân loại:</label>
          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.1)',
              color: 'white',
              fontSize: '14px',
              minWidth: '120px'
            }}
          >
            <option value="">Tất cả</option>
            {allLevels.map(level => (
              <option key={level} value={level} style={{ background: '#1f2937', color: 'white' }}>
                {level === 'Xuat sac' ? 'Xuất sắc' :
                 level === 'Kha' ? 'Khá' :
                 level === 'Trung binh' ? 'Trung bình' :
                 level === 'Yeu' ? 'Yếu' : level}
              </option>
            ))}
          </select>
        </div>

        {/* Expertise Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500' }}>Lĩnh vực:</label>
          <select
            value={selectedExpertise}
            onChange={(e) => setSelectedExpertise(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.1)',
              color: 'white',
              fontSize: '14px',
              minWidth: '150px'
            }}
          >
            <option value="">Tất cả lĩnh vực</option>
            {allExpertiseAreas.map(expertise => (
              <option key={expertise} value={expertise} style={{ background: '#1f2937', color: 'white' }}>
                {expertise}
              </option>
            ))}
          </select>
        </div>

        {/* Score Range Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500' }}>Điểm:</label>
          <input
            type="number"
            placeholder="Từ"
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.1)',
              color: 'white',
              fontSize: '14px',
              width: '80px'
            }}
          />
          <span style={{ color: 'rgba(255,255,255,0.7)' }}>-</span>
          <input
            type="number"
            placeholder="Đến"
            value={maxScore}
            onChange={(e) => setMaxScore(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.1)',
              color: 'white',
              fontSize: '14px',
              width: '80px'
            }}
          />
        </div>

        {/* Clear Filters Button */}
        <button
          onClick={() => {
            setSearchTerm('');
            setSelectedLevel('');
            setSelectedExpertise('');
            setMinScore('');
            setMaxScore('');
          }}
          style={{
            padding: '8px 16px',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '4px',
            background: 'rgba(239,68,68,0.1)',
            color: '#f87171',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Xóa bộ lọc
        </button>
      </div>

      {/* Results Summary */}
      <div style={{ 
        marginBottom: '12px', 
        fontSize: '14px', 
        color: 'rgba(255,255,255,0.8)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          Hiển thị {displayData.length} / {filteredData.length} sinh viên
          {filteredData.length !== students.length && ` (đã lọc từ ${students.length} sinh viên)`}
        </div>
        {(searchTerm || selectedLevel || selectedExpertise || minScore || maxScore) && (
          <div style={{ color: '#10B981' }}>
            ✓ Đang áp dụng bộ lọc
          </div>
        )}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
        <thead>
          <tr>
            {columns.map(field => (
              <th 
                key={field}
                onClick={() => handleSort(field)}
                style={{ 
                  padding: '12px 8px',
                  textAlign: 'left',
                  background: 'rgba(255,255,255,0.05)',
                  cursor: 'pointer',
                  position: 'relative',
                  whiteSpace: 'nowrap'
                }}
              >
                {fieldLabels[field] || field}
                {sortField === field && (
                  <span style={{ marginLeft: 4 }}>
                    {sortDirection === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
            <th 
              style={{ 
                padding: '12px 8px',
                textAlign: 'right',
                background: 'rgba(255,255,255,0.05)',
                whiteSpace: 'nowrap',
                width: '100px'
              }}
            >
              Thao tác
            </th>
          </tr>
        </thead>
        <tbody>
          {displayData.map((student, idx) => (
            <tr 
              key={student.id || idx}
              style={{ 
                background: idx % 2 ? 'rgba(255,255,255,0.02)' : 'transparent'
              }}
            >
                {columns.map(field => {
                  // Resolve level value to prefer normalized key
                  const rawVal = student[field];
                  // When rendering either level field, use normalized key for color/label
                  const resolvedLevelKey = (field === 'level_prediction' || field === 'predicted_level')
                    ? (student.level_key ?? student.level_prediction ?? student.predicted_level ?? student.level ?? student.level_pred)
                    : null;
                  // Render expertise areas with badges
                  const isExpertiseField = field === 'expertise_areas';
                  const formattedValue = formatFieldValue(field, rawVal, student);
                  
                  return (
                    <td 
                      key={field}
                      style={{ 
                        padding: '8px',
                        borderBottom: '1px solid rgba(255,255,255,0.1)',
                        whiteSpace: isExpertiseField ? 'normal' : 'nowrap',
                        color: (field === 'level_prediction' || field === 'predicted_level') ? getLevelColor(resolvedLevelKey) : 'inherit'
                      }}
                    >
                      {isExpertiseField && formattedValue && formattedValue !== 'Toàn diện' ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                          {formattedValue.split(', ').map((area, idx) => {
                            const colors = ['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];
                            const color = colors[idx % colors.length];
                            return (
                              <span 
                                key={idx} 
                                style={{ 
                                  display: 'inline-block',
                                  padding: '2px 8px',
                                  background: color + '20',
                                  color: color,
                                  borderRadius: '4px',
                                  fontSize: '11px',
                                  fontWeight: '500'
                                }}
                              >
                                {area}
                              </span>
                            );
                          })}
                        </div>
                      ) : (
                        formattedValue
                      )}
                    </td>
                  );
                })}
              <td
                style={{ 
                  padding: '8px',
                  borderBottom: '1px solid rgba(255,255,255,0.1)',
                  textAlign: 'right'
                }}
              >
                <button
                  onClick={() => window.location.href = `/edit/${student.id}`}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '4px',
                    border: '1px solid rgba(255,255,255,0.2)',
                    background: 'rgba(59,130,246,0.1)',
                    color: '#60a5fa',
                    cursor: 'pointer'
                  }}
                >
                  Sửa
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div style={{ 
        marginTop: 16,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '14px'
      }}>
        <div>
          Tổng: {filteredData.length} sinh viên
          {filteredData.length > rowsPerPage && ` (${(page-1)*rowsPerPage + 1}-${Math.min(page*rowsPerPage, filteredData.length)})`}
          {filteredData.length !== students.length && ` (đã lọc từ ${students.length} sinh viên)`}
        </div>
        {totalPages > 1 && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              style={{ padding: '4px 12px' }}
            >
              ←
            </button>
            <span>Trang {page}/{totalPages}</span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              style={{ padding: '4px 12px' }}
            >
              →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}