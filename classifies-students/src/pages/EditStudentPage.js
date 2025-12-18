import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { normalizeClassCode } from '../utils/classUtils';

export default function EditStudentPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [student, setStudent] = useState(null);
  const [error, setError] = useState(null);

  // Form fields
  const [formData, setFormData] = useState({
    name: '',
    student_id: '',
    class_id: '',
    level_prediction: '',
    course_avg: '',
    assignment_score: '',
    lmf_time: '',
    time_behavior: ''
  });

  // Load student data
  useEffect(() => {
    async function loadStudent() {
      const { data, error } = await supabase
        .from('students')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        console.error('Error loading student:', error);
        setError('Không thể tải thông tin sinh viên. Vui lòng thử lại.');
      } else if (data) {
        setStudent(data);
        setFormData(data);
      }
      setLoading(false);
    }

    if (id) loadStudent();
  }, [id]);

  // Handle form changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      // Convert numeric fields
      const numericFields = ['course_avg', 'assignment_score', 'lmf_time'];
      const dataToUpdate = { ...formData };
      numericFields.forEach(field => {
        if (dataToUpdate[field]) {
          dataToUpdate[field] = Number(dataToUpdate[field]);
        }
      });

      // Normalize class code and ensure Khoa is set
      const rawClass = dataToUpdate.class_id || dataToUpdate.class || '';
      const normalizedClass = normalizeClassCode(rawClass);
      dataToUpdate.class = normalizedClass;
      if (!dataToUpdate.Khoa) dataToUpdate.Khoa = 'Khoa Công Nghệ Thông Tin';

      const { error } = await supabase
        .from('students')
        .update(dataToUpdate)
        .eq('id', id);

      if (error) throw error;

      // Success - redirect back
      navigate('/');
    } catch (error) {
      console.error('Error updating student:', error);
      setError('Không thể cập nhật thông tin. Vui lòng thử lại.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Đang tải...</div>;
  if (!student) return <div>Không tìm thấy sinh viên</div>;

  return (
    <div className="edit-student">
      <div style={{ maxWidth: 600, margin: '0 auto', padding: '20px' }}>
        <h1>Chỉnh sửa Thông tin Sinh viên</h1>
        
        {error && (
          <div style={{ 
            padding: '12px', 
            marginBottom: '20px', 
            background: 'rgba(220,38,38,0.1)', 
            color: '#ef4444',
            borderRadius: '4px'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Họ tên:</label>
            <input
              type="text"
              name="name"
              value={formData.name || ''}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>MSSV:</label>
            <input
              type="text"
              name="student_id"
              value={formData.student_id || ''}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Lớp:</label>
            <input
              type="text"
              name="class_id"
              value={formData.class_id || ''}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Phân loại:</label>
            <select
              name="level_prediction"
              value={formData.level_prediction || ''}
              onChange={handleChange}
              required
            >
              <option value="">-- Chọn phân loại --</option>
              <option value="Xuất sắc">Xuất sắc</option>
              <option value="Giỏi">Giỏi</option>
              <option value="Khá">Khá</option>
              <option value="Trung bình">Trung bình</option>
              <option value="Yếu">Yếu</option>
            </select>
          </div>

          <div className="form-group">
            <label>Điểm trung bình:</label>
            <input
              type="number"
              step="0.01"
              name="course_avg"
              value={formData.course_avg || ''}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Điểm bài tập:</label>
            <input
              type="number"
              step="0.01"
              name="assignment_score"
              value={formData.assignment_score || ''}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Thời gian trên LMS:</label>
            <input
              type="number"
              step="0.01"
              name="lmf_time"
              value={formData.lmf_time || ''}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Hành vi thời gian:</label>
            <input
              type="text"
              name="time_behavior"
              value={formData.time_behavior || ''}
              onChange={handleChange}
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => navigate('/')}
              style={{
                marginRight: '12px',
                background: 'transparent'
              }}
            >
              Hủy
            </button>
            <button 
              type="submit"
              disabled={saving}
              style={{
                background: '#3b82f6'
              }}
            >
              {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
