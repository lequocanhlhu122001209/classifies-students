import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { useNavigate } from 'react-router-dom';
import { validateClassCode, validateStudentId, validateScore } from '../utils/validation';

export default function AddStudent() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  
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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Validate class code
    const classValidation = validateClassCode(formData.class);
    if (!classValidation.isValid) {
      setMessage({ type: 'error', text: classValidation.error });
      setLoading(false);
      return;
    }

    // Validate student ID
    const studentIdValidation = validateStudentId(formData.student_id);
    if (!studentIdValidation.isValid) {
      setMessage({ type: 'error', text: studentIdValidation.error });
      setLoading(false);
      return;
    }

    try {
      // Chuẩn bị dữ liệu để gửi
      const submitData = {
        ...formData,
        // Chuyển đổi số
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
        assignment_completion_100: parseFloat(formData.assignment_completion_100) || 0,
        // Tính toán các trường chuẩn hóa
        attendance_normalized: Math.round((parseFloat(formData.attendance_rate) || 0) * 100),
        assignment_normalized: Math.round((parseFloat(formData.assignment_completion) || 0) * 100),
        study_intensity: Math.round((parseFloat(formData.study_hours_per_week) || 0) * 10),
        punctuality_score: Math.max(0, 100 - ((parseInt(formData.late_submissions) || 0) * 10)),
        lms_engagement: Math.round((parseFloat(formData.lms_usage_hours) || 0) * 10),
        response_quality_normalized: Math.round((parseFloat(formData.response_quality) || 0) * 10)
      };

      // Ensure class is normalized and Khoa is set to IT faculty if empty
      if (classValidation && classValidation.normalizedCode) {
        submitData.class = classValidation.normalizedCode;
      }
      if (!submitData.Khoa) submitData.Khoa = 'Khoa Công Nghệ Thông Tin';

      console.log('🔄 Đang thêm sinh viên mới...', submitData);

      const { data, error } = await supabase
        .from('students')
        .insert([submitData])
        .select();

      if (error) {
        throw error;
      }

      console.log('✅ Thêm sinh viên thành công:', data);
      setMessage({ type: 'success', text: `✅ Đã thêm sinh viên ${formData.name} thành công!` });
      
      // Reset form
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

      // Chuyển về trang chủ sau 2 giây
      setTimeout(() => {
        navigate('/');
      }, 2000);

    } catch (error) {
      console.error('❌ Lỗi khi thêm sinh viên:', error);
      setMessage({ type: 'error', text: `❌ Lỗi: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      padding: '20px',
      background: '#0f172a',
      color: '#f1f5f9',
      minHeight: '100vh'
    }}>
      <div style={{ marginBottom: '20px' }}>
        <h1 style={{ color: '#60a5fa', marginBottom: '8px' }}>➕ Thêm Sinh Viên Mới</h1>
        <p style={{ color: '#94a3b8', fontSize: '14px' }}>
          Nhập thông tin sinh viên mới vào hệ thống
        </p>
      </div>

      {/* Thông báo */}
      {message && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '20px',
          background: message.type === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
          border: `1px solid ${message.type === 'success' ? '#10B981' : '#EF4444'}`,
          color: message.type === 'success' ? '#10B981' : '#EF4444',
          fontSize: '14px'
        }}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Thông tin cơ bản */}
        <div style={{ 
          background: 'rgba(255,255,255,0.05)', 
          padding: '20px', 
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ color: '#60a5fa', marginBottom: '16px' }}>📋 Thông tin cơ bản</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                MSSV *
              </label>
              <input
                type="number"
                name="student_id"
                value={formData.student_id}
                onChange={handleInputChange}
                required
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: '#f1f5f9',
                  fontSize: '14px'
                }}
                placeholder="Nhập MSSV"
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                Họ và tên *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: '#f1f5f9',
                  fontSize: '14px'
                }}
                placeholder="Nhập họ và tên"
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                Lớp
              </label>
              <input
                type="text"
                name="class"
                value={formData.class}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: '#f1f5f9',
                  fontSize: '14px'
                }}
                placeholder="VD: 22IT1"
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                Giới tính
              </label>
              <select
                name="sex"
                value={formData.sex}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: '#f1f5f9',
                  fontSize: '14px'
                }}
              >
                <option value="">Chọn giới tính</option>
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                Khoa
              </label>
              <select
                name="Khoa"
                value={formData.Khoa}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)',
                  color: '#f1f5f9',
                  fontSize: '14px'
                }}
              >
                <option value="">Chọn khoa</option>
                <option value="Công nghệ thông tin">Công nghệ thông tin</option>
                <option value="Anh Văn">Anh Văn</option>
                <option value="Kế toán">Kế toán</option>
                <option value="Quản trị kinh doanh">Quản trị kinh doanh</option>
                <option value="Xây dựng">Xây dựng</option>
              </select>
            </div>
          </div>
        </div>

        {/* Điểm số */}
        <div style={{ 
          background: 'rgba(255,255,255,0.05)', 
          padding: '20px', 
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ color: '#60a5fa', marginBottom: '16px' }}>📊 Điểm số</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {[
              { name: 'midterm_score', label: 'Điểm giữa kỳ', type: 'number', step: '0.1', max: '10' },
              { name: 'final_score', label: 'Điểm cuối kỳ', type: 'number', step: '0.1', max: '10' },
              { name: 'homework_score', label: 'Điểm bài tập', type: 'number', step: '0.1', max: '10' },
              { name: 'total_score', label: 'Tổng điểm', type: 'number', step: '0.1', max: '10' },
              { name: 'behavior_score', label: 'Điểm hành vi', type: 'number', step: '0.1', max: '10' },
              { name: 'participation_score', label: 'Điểm tham gia', type: 'number', step: '0.1', max: '10' },
              { name: 'response_quality', label: 'Chất lượng phản hồi', type: 'number', step: '0.1', max: '10' }
            ].map(field => (
              <div key={field.name}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                  {field.label}
                </label>
                <input
                  type={field.type}
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleInputChange}
                  step={field.step}
                  max={field.max}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    border: '1px solid rgba(255,255,255,0.2)',
                    background: 'rgba(255,255,255,0.05)',
                    color: '#f1f5f9',
                    fontSize: '14px'
                  }}
                  placeholder={`0-${field.max}`}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Tỷ lệ và thống kê */}
        <div style={{ 
          background: 'rgba(255,255,255,0.05)', 
          padding: '20px', 
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ color: '#60a5fa', marginBottom: '16px' }}>📈 Tỷ lệ và thống kê</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {[
              { name: 'attendance_rate', label: 'Tỷ lệ tham gia (%)', type: 'number', step: '0.01', max: '1' },
              { name: 'assignment_completion', label: 'Hoàn thành bài tập (%)', type: 'number', step: '0.01', max: '1' },
              { name: 'study_hours_per_week', label: 'Giờ học/tuần', type: 'number', step: '0.1' },
              { name: 'lms_usage_hours', label: 'Giờ sử dụng LMS', type: 'number', step: '0.1' },
              { name: 'late_submissions', label: 'Số lần nộp muộn', type: 'number' },
              { name: 'extra_activities', label: 'Hoạt động ngoại khóa', type: 'number' }
            ].map(field => (
              <div key={field.name}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                  {field.label}
                </label>
                <input
                  type={field.type}
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleInputChange}
                  step={field.step}
                  max={field.max}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    border: '1px solid rgba(255,255,255,0.2)',
                    background: 'rgba(255,255,255,0.05)',
                    color: '#f1f5f9',
                    fontSize: '14px'
                  }}
                  placeholder={field.max ? `0-${field.max}` : 'Nhập số'}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Nút submit */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={() => navigate('/')}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(255,255,255,0.05)',
              color: '#f1f5f9',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            ← Quay lại
          </button>
          
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              border: '1px solid rgba(16,185,129,0.3)',
              background: loading ? 'rgba(16,185,129,0.1)' : 'rgba(16,185,129,0.2)',
              color: loading ? '#6B7280' : '#10B981',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            {loading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #6B7280',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Đang thêm...
              </>
            ) : (
              '➕ Thêm sinh viên'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
