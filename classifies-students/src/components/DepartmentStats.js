import React, { useMemo } from 'react';

export default function DepartmentStats({ students = [] }) {
  // Thống kê theo khoa
  const departmentStats = useMemo(() => {
    const stats = {};
    
    students.forEach(student => {
      const department = student.Khoa || student.department || 'Chưa xác định';
      if (!stats[department]) {
        stats[department] = {
          total: 0,
          expertise: {},
          levels: {},
          avgScore: 0,
          totalScore: 0
        };
      }
      
      stats[department].total++;
      stats[department].totalScore += Number(student.total_score) || 0;
      
      // Thống kê phân loại
      const level = student.level_key || student.level_prediction || 'Chưa phân loại';
      stats[department].levels[level] = (stats[department].levels[level] || 0) + 1;
      
      // Thống kê lĩnh vực thế mạnh
      if (student.expertise_areas && student.expertise_areas !== 'Toàn diện') {
        student.expertise_areas.split(', ').forEach(area => {
          const trimmedArea = area.trim();
          stats[department].expertise[trimmedArea] = (stats[department].expertise[trimmedArea] || 0) + 1;
        });
      }
    });
    
    // Tính điểm trung bình
    Object.keys(stats).forEach(dept => {
      if (stats[dept].total > 0) {
        stats[dept].avgScore = (stats[dept].totalScore / stats[dept].total).toFixed(2);
      }
    });
    
    return stats;
  }, [students]);

  // Sắp xếp khoa theo số lượng sinh viên
  const sortedDepartments = Object.entries(departmentStats)
    .sort(([,a], [,b]) => b.total - a.total);

  // Màu sắc cho các level
  const getLevelColor = (level) => {
    switch (level) {
      case 'Xuat sac': return '#10B981';
      case 'Kha': return '#3B82F6';
      case 'Trung binh': return '#F59E0B';
      case 'Yeu': return '#EF4444';
      default: return '#6B7280';
    }
  };

  // Màu sắc cho các lĩnh vực
  const getExpertiseColor = (index) => {
    const colors = ['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];
    return colors[index % colors.length];
  };

  if (students.length === 0) {
    return <div>Không có dữ liệu sinh viên</div>;
  }

  return (
    <div style={{ 
      background: 'rgba(255,255,255,0.05)', 
      borderRadius: '12px', 
      padding: '20px',
      marginBottom: '20px',
      border: '1px solid rgba(255,255,255,0.1)'
    }}>
      <h3 style={{ 
        margin: '0 0 20px 0', 
        color: '#60a5fa',
        fontSize: '18px',
        fontWeight: '600'
      }}>
        📊 Thống kê theo Khoa
      </h3>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '20px' 
      }}>
        {sortedDepartments.map(([department, stats]) => (
          <div key={department} style={{
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '8px',
            padding: '16px',
            border: '1px solid rgba(255,255,255,0.08)'
          }}>
            {/* Header khoa */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '12px'
            }}>
              <h4 style={{ 
                margin: 0, 
                color: '#e6eef8',
                fontSize: '16px',
                fontWeight: '600'
              }}>
                🏫 {department}
              </h4>
              <div style={{ 
                background: '#3B82F6',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: '500'
              }}>
                {stats.total} sinh viên
              </div>
            </div>

            {/* Điểm trung bình */}
            <div style={{ 
              marginBottom: '12px',
              fontSize: '14px',
              color: 'rgba(255,255,255,0.8)'
            }}>
              📈 Điểm TB: <strong style={{ color: '#10B981' }}>{stats.avgScore}</strong>
            </div>

            {/* Phân bố level */}
            <div style={{ marginBottom: '12px' }}>
              <div style={{ 
                fontSize: '13px', 
                color: 'rgba(255,255,255,0.7)',
                marginBottom: '8px'
              }}>
                Phân loại:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {Object.entries(stats.levels).map(([level, count]) => (
                  <span key={level} style={{
                    padding: '3px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '500',
                    background: getLevelColor(level) + '20',
                    color: getLevelColor(level),
                    border: `1px solid ${getLevelColor(level)}40`
                  }}>
                    {level === 'Xuat sac' ? 'Xuất sắc' :
                     level === 'Kha' ? 'Khá' :
                     level === 'Trung binh' ? 'Trung bình' :
                     level === 'Yeu' ? 'Yếu' : level}: {count}
                  </span>
                ))}
              </div>
            </div>

            {/* Top lĩnh vực thế mạnh */}
            <div>
              <div style={{ 
                fontSize: '13px', 
                color: 'rgba(255,255,255,0.7)',
                marginBottom: '8px'
              }}>
                Lĩnh vực nổi bật:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {Object.entries(stats.expertise)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 5)
                  .map(([expertise, count], index) => (
                    <span key={expertise} style={{
                      padding: '2px 6px',
                      borderRadius: '3px',
                      fontSize: '10px',
                      fontWeight: '500',
                      background: getExpertiseColor(index) + '20',
                      color: getExpertiseColor(index),
                      border: `1px solid ${getExpertiseColor(index)}40`
                    }}>
                      {expertise} ({count})
                    </span>
                  ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tổng kết */}
      <div style={{ 
        marginTop: '20px',
        padding: '16px',
        background: 'rgba(59,130,246,0.1)',
        borderRadius: '8px',
        border: '1px solid rgba(59,130,246,0.2)'
      }}>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
          gap: '16px',
          textAlign: 'center'
        }}>
          <div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#60a5fa' }}>
              {students.length}
            </div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>
              Tổng sinh viên
            </div>
          </div>
          <div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10B981' }}>
              {Object.keys(departmentStats).length}
            </div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>
              Số khoa
            </div>
          </div>
          <div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#F59E0B' }}>
              {Object.values(departmentStats).reduce((sum, stats) => sum + Object.keys(stats.expertise).length, 0)}
            </div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>
              Lĩnh vực khác nhau
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
