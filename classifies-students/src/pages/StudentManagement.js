import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { syncManager } from '../utils/syncManager';
import { normalizeClassCode, groupStudentsByBatch, sortClassCodes } from '../utils/classUtils';

export default function StudentManagement() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [message, setMessage] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('');
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);

  // Form data for add/edit
  const [formData, setFormData] = useState({
    student_id: '',
    name: '',
    class: '',
    sex: '',
    Khoa: '',
    midterm_score: '',
    final_score: '',
    homework_score: '',
    attendance_rate: '',
    assignment_completion: '',
    study_hours_per_week: '',
    participation_score: '',
    late_submissions: '',
    extra_activities: '',
    lms_usage_hours: '',
    response_quality: '',
    total_score: '',
    behavior_score: '',
    behavior_score_100: '',
    attendance_rate_100: '',
    assignment_completion_100: '',
    risk_level: ''
  });

  // Load students
  useEffect(() => {
    loadStudents();
    
    // Lắng nghe sự kiện đồng bộ
    const unsubscribe = syncManager.addSyncListener((event) => {
      if (event.type === 'sync_start') {
        setIsSyncing(true);
        setSyncStatus({ type: 'info', message: event.message });
      } else if (event.type === 'sync_complete') {
        setIsSyncing(false);
        setSyncStatus({ 
          type: 'success', 
          message: event.message,
          successful: event.successful,
          failed: event.failed
        });
        // Tự động tải lại dữ liệu sau khi đồng bộ
        setTimeout(() => {
          loadStudents();
          setSyncStatus(null);
        }, 2000);
      } else if (event.type === 'sync_error') {
        setIsSyncing(false);
        setSyncStatus({ type: 'error', message: event.message });
      }
    });

    return () => unsubscribe();
  }, []);

  // Read `level` query param and apply as filter when component mounts or when URL changes
  const location = useLocation();
  const tableRef = useRef(null);

  useEffect(() => {
    try {
      const params = new URLSearchParams(location.search);
      const lvl = params.get('level') || '';
      if (lvl !== filterLevel) {
        setFilterLevel(lvl);
        // Scroll to table so user sees the filtered list
        setTimeout(() => {
          if (tableRef.current) tableRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 250);
      }
    } catch (e) {
      console.warn('Error parsing level query param', e);
    }
  }, [location.search]);

  const loadStudents = async () => {
    try {
      setLoading(true);
      const data = await syncManager.loadAllStudents();
      setStudents(data);
    } catch (error) {
      console.error('Lỗi tải danh sách sinh viên:', error);
      setMessage({ type: 'error', text: 'Lỗi tải danh sách sinh viên' });
    } finally {
      setLoading(false);
    }
  };

  // Filter students
  const filteredStudents = students.filter(student => {
    const normalizedSearchTerm = searchTerm.toLowerCase();
    const normalizedClass = normalizeClassCode(student.class)?.toLowerCase();
    
    const matchesSearch = !searchTerm || 
      student.name?.toLowerCase().includes(normalizedSearchTerm) ||
      student.student_id?.toString().includes(normalizedSearchTerm) ||
      normalizedClass?.includes(normalizedSearchTerm);
    
    const matchesLevel = !filterLevel || 
      student.level_prediction === filterLevel || 
      student.predicted_level === filterLevel;
    
    return matchesSearch && matchesLevel;
  });

  // Handle form input
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Add student
  const handleAddStudent = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Chuẩn bị dữ liệu
      const submitData = {
        ...formData,
        student_id: parseInt(formData.student_id),
        midterm_score: parseFloat(formData.midterm_score) || 0,
        final_score: parseFloat(formData.final_score) || 0,
        homework_score: parseFloat(formData.homework_score) || 0,
        attendance_rate: parseFloat(formData.attendance_rate) || 0,
        assignment_completion: parseFloat(formData.assignment_completion) || 0,
        study_hours_per_week: parseFloat(formData.study_hours_per_week) || 0,
        participation_score: parseFloat(formData.participation_score) || 0,
        late_submissions: parseInt(formData.late_submissions) || 0,
        extra_activities: parseInt(formData.extra_activities) || 0,
        lms_usage_hours: parseFloat(formData.lms_usage_hours) || 0,
        response_quality: parseFloat(formData.response_quality) || 0,
        total_score: parseFloat(formData.total_score) || 0,
        behavior_score: parseFloat(formData.behavior_score) || 0,
        behavior_score_100: parseFloat(formData.behavior_score_100) || 0,
        attendance_rate_100: parseFloat(formData.attendance_rate_100) || 0,
        assignment_completion_100: parseFloat(formData.assignment_completion_100) || 0
      };

      // Sử dụng SyncManager để thêm sinh viên
      const newStudent = await syncManager.addStudent(submitData);

      setMessage({ type: 'success', text: 'Thêm sinh viên thành công!' });
      setShowAddForm(false);
      resetForm();
      loadStudents();
    } catch (error) {
      console.error('Lỗi thêm sinh viên:', error);
      setMessage({ type: 'error', text: `Lỗi thêm sinh viên: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  // Edit student
  const handleEditStudent = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      const submitData = {
        ...formData,
        student_id: parseInt(formData.student_id),
        midterm_score: parseFloat(formData.midterm_score) || 0,
        final_score: parseFloat(formData.final_score) || 0,
        homework_score: parseFloat(formData.homework_score) || 0,
        attendance_rate: parseFloat(formData.attendance_rate) || 0,
        assignment_completion: parseFloat(formData.assignment_completion) || 0,
        study_hours_per_week: parseFloat(formData.study_hours_per_week) || 0,
        participation_score: parseFloat(formData.participation_score) || 0,
        late_submissions: parseInt(formData.late_submissions) || 0,
        extra_activities: parseInt(formData.extra_activities) || 0,
        lms_usage_hours: parseFloat(formData.lms_usage_hours) || 0,
        response_quality: parseFloat(formData.response_quality) || 0,
        total_score: parseFloat(formData.total_score) || 0,
        behavior_score: parseFloat(formData.behavior_score) || 0,
        behavior_score_100: parseFloat(formData.behavior_score_100) || 0,
        attendance_rate_100: parseFloat(formData.attendance_rate_100) || 0,
        assignment_completion_100: parseFloat(formData.assignment_completion_100) || 0
      };

      // Sử dụng SyncManager để cập nhật sinh viên
      const updatedStudent = await syncManager.updateStudent(selectedStudent.id, submitData);

      setMessage({ type: 'success', text: 'Cập nhật sinh viên thành công!' });
      setShowEditForm(false);
      setSelectedStudent(null);
      resetForm();
      loadStudents();
    } catch (error) {
      console.error('Lỗi cập nhật sinh viên:', error);
      setMessage({ type: 'error', text: `Lỗi cập nhật sinh viên: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  // Delete student
  const handleDeleteStudent = async () => {
    try {
      setLoading(true);
      
      // Sử dụng SyncManager để xóa sinh viên
      await syncManager.deleteStudent(selectedStudent.id);

      setMessage({ type: 'success', text: 'Xóa sinh viên thành công!' });
      setShowDeleteConfirm(false);
      setSelectedStudent(null);
      loadStudents();
    } catch (error) {
      console.error('Lỗi xóa sinh viên:', error);
      setMessage({ type: 'error', text: `Lỗi xóa sinh viên: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      student_id: '',
      name: '',
      class: '',
      sex: '',
      Khoa: '',
      midterm_score: '',
      final_score: '',
      homework_score: '',
      attendance_rate: '',
      assignment_completion: '',
      study_hours_per_week: '',
      participation_score: '',
      late_submissions: '',
      extra_activities: '',
      lms_usage_hours: '',
      response_quality: '',
      total_score: '',
      behavior_score: '',
      behavior_score_100: '',
      attendance_rate_100: '',
      assignment_completion_100: '',
      risk_level: ''
    });
  };

  // Open edit form
  const openEditForm = (student) => {
    setSelectedStudent(student);
    setFormData(student);
    setShowEditForm(true);
  };

  // Open delete confirm
  const openDeleteConfirm = (student) => {
    setSelectedStudent(student);
    setShowDeleteConfirm(true);
  };

  if (loading && students.length === 0) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Đang tải...</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Quản lý Sinh viên</h1>
      
      {/* Message */}
      {message && (
        <div style={{
          padding: '12px',
          marginBottom: '20px',
          borderRadius: '8px',
          background: message.type === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
          border: `1px solid ${message.type === 'success' ? '#10B981' : '#EF4444'}`,
          color: message.type === 'success' ? '#10B981' : '#EF4444'
        }}>
          {message.text}
        </div>
      )}

      {/* Sync Status */}
      {syncStatus && (
        <div style={{
          padding: '12px',
          marginBottom: '20px',
          borderRadius: '8px',
          background: syncStatus.type === 'success' ? 'rgba(16,185,129,0.1)' : 
                     syncStatus.type === 'error' ? 'rgba(239,68,68,0.1)' : 
                     'rgba(59,130,246,0.1)',
          border: `1px solid ${syncStatus.type === 'success' ? '#10B981' : 
                                 syncStatus.type === 'error' ? '#EF4444' : 
                                 '#3B82F6'}`,
          color: syncStatus.type === 'success' ? '#10B981' : 
                 syncStatus.type === 'error' ? '#EF4444' : 
                 '#3B82F6'
        }}>
          {syncStatus.message}
          {syncStatus.successful !== undefined && (
            <div style={{ marginTop: '8px', fontSize: '14px' }}>
              ✅ Thành công: {syncStatus.successful} | ❌ Thất bại: {syncStatus.failed}
            </div>
          )}
        </div>
      )}

      {/* Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '16px', 
        marginBottom: '20px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <button
          onClick={() => setShowAddForm(true)}
          style={{
            padding: '10px 20px',
            background: '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ➕ Thêm sinh viên
        </button>

        <button
          onClick={async () => {
            if (isSyncing) return;
            try {
              await syncManager.classifyAndSyncAllStudents();
            } catch (error) {
              setMessage({ type: 'error', text: `Lỗi đồng bộ: ${error.message}` });
            }
          }}
          disabled={isSyncing}
          style={{
            padding: '10px 20px',
            background: isSyncing ? '#6B7280' : '#3B82F6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isSyncing ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          {isSyncing ? (
            <>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid white',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              Đang đồng bộ...
            </>
          ) : (
            <>
              🔄 Đồng bộ & Phân loại lại
            </>
          )}
        </button>

        <input
          type="text"
          placeholder="Tìm kiếm theo tên hoặc MSSV..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            minWidth: '250px'
          }}
        />

        <select
          value={filterLevel}
          onChange={(e) => setFilterLevel(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        >
          <option value="">Tất cả phân loại</option>
          <option value="Xuat sac">Xuất sắc</option>
          <option value="Kha">Khá</option>
          <option value="Trung binh">Trung bình</option>
          <option value="Yeu">Yếu</option>
        </select>
      </div>

      {/* Students Table */}
      <div ref={tableRef} style={{ 
        background: 'white', 
        borderRadius: '8px', 
        overflow: 'hidden',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f8f9fa' }}>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>ID</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>MSSV</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Họ tên</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Lớp</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Phân loại</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Lĩnh vực thế mạnh</th>
              <th style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map((student) => (
              <tr key={student.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                <td style={{ padding: '12px' }}>{student.id}</td>
                <td style={{ padding: '12px' }}>{student.student_id}</td>
                <td style={{ padding: '12px' }}>{student.name}</td>
                <td style={{ padding: '12px' }}>{normalizeClassCode(student.class)}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    background: student.level_prediction === 'Xuat sac' ? '#10B981' :
                               student.level_prediction === 'Kha' ? '#3B82F6' :
                               student.level_prediction === 'Trung binh' ? '#F59E0B' : '#EF4444',
                    color: 'white'
                  }}>
                    {student.level_prediction === 'Xuat sac' ? 'Xuất sắc' :
                     student.level_prediction === 'Kha' ? 'Khá' :
                     student.level_prediction === 'Trung binh' ? 'Trung bình' :
                     student.level_prediction === 'Yeu' ? 'Yếu' : student.level_prediction}
                  </span>
                </td>
                <td style={{ padding: '12px' }}>
                  {student.expertise_areas ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {student.expertise_areas.split(', ').map((area, idx) => (
                        <span key={idx} style={{
                          padding: '2px 6px',
                          background: '#e3f2fd',
                          color: '#1976d2',
                          borderRadius: '4px',
                          fontSize: '11px'
                        }}>
                          {area}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: '#999' }}>Chưa phân loại</span>
                  )}
                </td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                    <button
                      onClick={() => openEditForm(student)}
                      style={{
                        padding: '6px 12px',
                        background: '#3B82F6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      ✏️ Sửa
                    </button>
                    <button
                      onClick={() => openDeleteConfirm(student)}
                      style={{
                        padding: '6px 12px',
                        background: '#EF4444',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      🗑️ Xóa
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Form Modal */}
      {showAddForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '8px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <h2>Thêm sinh viên mới</h2>
            <form onSubmit={handleAddStudent}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <label>MSSV:</label>
                  <input
                    type="number"
                    name="student_id"
                    value={formData.student_id}
                    onChange={handleInputChange}
                    required
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Họ và tên:</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Lớp:</label>
                  <input
                    type="text"
                    name="class"
                    value={formData.class}
                    onChange={handleInputChange}
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Giới tính:</label>
                  <select
                    name="sex"
                    value={formData.sex}
                    onChange={handleInputChange}
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  >
                    <option value="">Chọn giới tính</option>
                    <option value="Nam">Nam</option>
                    <option value="Nữ">Nữ</option>
                  </select>
                </div>
                <div>
                  <label>Khoa:</label>
                  <input
                    type="text"
                    name="Khoa"
                    value={formData.Khoa}
                    onChange={handleInputChange}
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Điểm giữa kỳ:</label>
                  <input
                    type="number"
                    name="midterm_score"
                    value={formData.midterm_score}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Điểm cuối kỳ:</label>
                  <input
                    type="number"
                    name="final_score"
                    value={formData.final_score}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Điểm bài tập:</label>
                  <input
                    type="number"
                    name="homework_score"
                    value={formData.homework_score}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Tỷ lệ tham gia:</label>
                  <input
                    type="number"
                    name="attendance_rate"
                    value={formData.attendance_rate}
                    onChange={handleInputChange}
                    min="0"
                    max="1"
                    step="0.01"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Hoàn thành bài tập:</label>
                  <input
                    type="number"
                    name="assignment_completion"
                    value={formData.assignment_completion}
                    onChange={handleInputChange}
                    min="0"
                    max="1"
                    step="0.01"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Giờ học/tuần:</label>
                  <input
                    type="number"
                    name="study_hours_per_week"
                    value={formData.study_hours_per_week}
                    onChange={handleInputChange}
                    min="0"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Điểm tham gia:</label>
                  <input
                    type="number"
                    name="participation_score"
                    value={formData.participation_score}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Nộp muộn:</label>
                  <input
                    type="number"
                    name="late_submissions"
                    value={formData.late_submissions}
                    onChange={handleInputChange}
                    min="0"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Hoạt động ngoại khóa:</label>
                  <input
                    type="number"
                    name="extra_activities"
                    value={formData.extra_activities}
                    onChange={handleInputChange}
                    min="0"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Giờ sử dụng LMS:</label>
                  <input
                    type="number"
                    name="lms_usage_hours"
                    value={formData.lms_usage_hours}
                    onChange={handleInputChange}
                    min="0"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Chất lượng phản hồi:</label>
                  <input
                    type="number"
                    name="response_quality"
                    value={formData.response_quality}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Tổng điểm:</label>
                  <input
                    type="number"
                    name="total_score"
                    value={formData.total_score}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Điểm hành vi:</label>
                  <input
                    type="number"
                    name="behavior_score"
                    value={formData.behavior_score}
                    onChange={handleInputChange}
                    min="0"
                    max="10"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddForm(false);
                    resetForm();
                  }}
                  style={{
                    padding: '10px 20px',
                    background: '#6B7280',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: '10px 20px',
                    background: '#10B981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  {loading ? 'Đang thêm...' : 'Thêm sinh viên'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Form Modal */}
      {showEditForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '8px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <h2>Cập nhật sinh viên</h2>
            <form onSubmit={handleEditStudent}>
              {/* Form fields tương tự như Add Form */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <label>MSSV:</label>
                  <input
                    type="number"
                    name="student_id"
                    value={formData.student_id}
                    onChange={handleInputChange}
                    required
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                <div>
                  <label>Họ và tên:</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                  />
                </div>
                {/* Các trường khác tương tự... */}
              </div>
              
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowEditForm(false);
                    setSelectedStudent(null);
                    resetForm();
                  }}
                  style={{
                    padding: '10px 20px',
                    background: '#6B7280',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: '10px 20px',
                    background: '#3B82F6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  {loading ? 'Đang cập nhật...' : 'Cập nhật'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '8px',
            maxWidth: '400px',
            width: '90%'
          }}>
            <h2>Xác nhận xóa</h2>
            <p>Bạn có chắc chắn muốn xóa sinh viên <strong>{selectedStudent?.name}</strong>?</p>
            <p style={{ color: '#EF4444', fontSize: '14px' }}>Hành động này không thể hoàn tác!</p>
            
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setSelectedStudent(null);
                }}
                style={{
                  padding: '10px 20px',
                  background: '#6B7280',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Hủy
              </button>
              <button
                onClick={handleDeleteStudent}
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  background: '#EF4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                {loading ? 'Đang xóa...' : 'Xóa'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
