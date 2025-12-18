import { supabase } from '../supabaseClient';
import { classifyStudents, classifyByExpertise } from './classification';
import { canonicalizeLevel } from './level';

/**
 * Quản lý đồng bộ hóa dữ liệu giữa frontend và Supabase
 */
export class SyncManager {
  constructor() {
    this.isSyncing = false;
    this.syncQueue = [];
    this.listeners = [];
  }

  /**
   * Thêm listener để theo dõi trạng thái đồng bộ
   */
  addSyncListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  /**
   * Thông báo cho tất cả listeners
   */
  notifyListeners(event) {
    this.listeners.forEach(callback => callback(event));
  }

  /**
   * Tải tất cả dữ liệu sinh viên từ Supabase
   */
  async loadAllStudents() {
    try {
      console.log("🔄 Đang tải dữ liệu sinh viên từ Supabase...");
      
      const { data, error } = await supabase
        .from('students')
        .select('*')
        .order('id', { ascending: true });

      if (error) {
        console.error("❌ Lỗi tải dữ liệu:", error);
        throw error;
      }

      console.log(`✅ Đã tải thành công ${data.length} sinh viên`);
      return data || [];
    } catch (error) {
      console.error("❌ Lỗi khi tải dữ liệu sinh viên:", error);
      throw error;
    }
  }

  /**
   * Phân loại và cập nhật tất cả sinh viên
   */
  async classifyAndSyncAllStudents() {
    if (this.isSyncing) {
      console.log("⚠️ Đang trong quá trình đồng bộ, bỏ qua yêu cầu mới");
      return;
    }

    this.isSyncing = true;
    this.notifyListeners({ type: 'sync_start', message: 'Bắt đầu phân loại và đồng bộ dữ liệu...' });

    try {
      // 1. Tải dữ liệu gốc
      const students = await this.loadAllStudents();
      if (students.length === 0) {
        this.notifyListeners({ type: 'sync_complete', message: 'Không có dữ liệu để xử lý', successful: 0, failed: 0 });
        return;
      }

      // 2. Phân loại sinh viên
      console.log("🧠 Đang phân loại sinh viên...");
      const classifiedStudents = classifyStudents(students);
      const classifiedByExpertise = classifyByExpertise(classifiedStudents);
      
      // 3. Thêm level_key đã chuẩn hóa
      const mapped = classifiedByExpertise.map(s => ({
        ...s,
        level_key: canonicalizeLevel(s.level_prediction) || s.level_prediction
      }));

      // 4. Cập nhật vào database
      console.log("💾 Đang cập nhật dữ liệu vào Supabase...");
      const result = await this.batchUpdateStudents(mapped);

      this.notifyListeners({ 
        type: 'sync_complete', 
        message: `Hoàn thành đồng bộ: ${result.successful} thành công, ${result.failed} thất bại`,
        successful: result.successful,
        failed: result.failed,
        results: result.results
      });

      return result;
    } catch (error) {
      console.error("❌ Lỗi trong quá trình đồng bộ:", error);
      this.notifyListeners({ 
        type: 'sync_error', 
        message: `Lỗi đồng bộ: ${error.message}`,
        error: error
      });
      throw error;
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Cập nhật hàng loạt sinh viên
   */
  async batchUpdateStudents(students) {
    const updatePromises = students.map(async (student, index) => {
      try {
        console.log(`🔄 Cập nhật sinh viên ${index + 1}/${students.length} - ID: ${student.id}`);
        
        const updateData = {
          level_prediction: student.level_prediction,
          predicted_level: student.predicted_level,
          level_key: student.level_key,
          expertise_areas: student.expertise_areas,
          expertise_list: student.expertise_list,
          updated_at: new Date().toISOString()
        };

        const { data, error } = await supabase
          .from('students')
          .update(updateData)
          .eq('id', student.id)
          .select('id');

        if (error) {
          console.error(`❌ Lỗi cập nhật sinh viên ID ${student.id}:`, error);
          return { success: false, id: student.id, error: error.message };
        }

        console.log(`✅ Cập nhật thành công sinh viên ID ${student.id}`);
        return { success: true, id: student.id, data };
      } catch (err) {
        console.error(`❌ Exception khi cập nhật sinh viên ID ${student.id}:`, err);
        return { success: false, id: student.id, error: err.message };
      }
    });

    // Chờ tất cả cập nhật hoàn thành
    const results = await Promise.all(updatePromises);
    
    const successful = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;
    
    console.log(`✅ Hoàn thành cập nhật: ${successful} thành công, ${failed} thất bại`);
    
    if (failed > 0) {
      const failedIds = results.filter(r => !r.success).map(r => r.id);
      const failedErrors = results.filter(r => !r.success).map(r => r.error);
      console.warn("⚠️ Các bản ghi cập nhật thất bại:", failedIds);
      console.warn("⚠️ Chi tiết lỗi:", failedErrors);
    }
    
    return { successful, failed, results };
  }

  /**
   * Thêm sinh viên mới và phân loại tự động
   */
  async addStudent(studentData) {
    try {
      console.log("➕ Đang thêm sinh viên mới...");
      
      // 1. Thêm sinh viên vào database
      const { data: newStudent, error: insertError } = await supabase
        .from('students')
        .insert([studentData])
        .select()
        .single();

      if (insertError) {
        throw insertError;
      }

      // 2. Phân loại sinh viên mới
      const classifiedStudents = classifyStudents([newStudent]);
      const classifiedByExpertise = classifyByExpertise(classifiedStudents);
      const mapped = classifiedByExpertise.map(s => ({
        ...s,
        level_key: canonicalizeLevel(s.level_prediction) || s.level_prediction
      }));

      // 3. Cập nhật kết quả phân loại
      const { error: updateError } = await supabase
        .from('students')
        .update({
          level_prediction: mapped[0].level_prediction,
          predicted_level: mapped[0].predicted_level,
          level_key: mapped[0].level_key,
          expertise_areas: mapped[0].expertise_areas,
          expertise_list: mapped[0].expertise_list,
          updated_at: new Date().toISOString()
        })
        .eq('id', newStudent.id);

      if (updateError) {
        console.warn("⚠️ Lỗi cập nhật phân loại:", updateError);
      }

      console.log("✅ Thêm sinh viên thành công");
      return { ...newStudent, ...mapped[0] };
    } catch (error) {
      console.error("❌ Lỗi thêm sinh viên:", error);
      throw error;
    }
  }

  /**
   * Cập nhật sinh viên và phân loại lại
   */
  async updateStudent(studentId, studentData) {
    try {
      console.log(`🔄 Đang cập nhật sinh viên ID ${studentId}...`);
      
      // 1. Cập nhật dữ liệu cơ bản
      const { error: updateError } = await supabase
        .from('students')
        .update(studentData)
        .eq('id', studentId);

      if (updateError) {
        throw updateError;
      }

      // 2. Lấy dữ liệu đã cập nhật
      const { data: updatedStudent, error: fetchError } = await supabase
        .from('students')
        .select('*')
        .eq('id', studentId)
        .single();

      if (fetchError) {
        throw fetchError;
      }

      // 3. Phân loại lại
      const classifiedStudents = classifyStudents([updatedStudent]);
      const classifiedByExpertise = classifyByExpertise(classifiedStudents);
      const mapped = classifiedByExpertise.map(s => ({
        ...s,
        level_key: canonicalizeLevel(s.level_prediction) || s.level_prediction
      }));

      // 4. Cập nhật kết quả phân loại
      const { error: classificationError } = await supabase
        .from('students')
        .update({
          level_prediction: mapped[0].level_prediction,
          predicted_level: mapped[0].predicted_level,
          level_key: mapped[0].level_key,
          expertise_areas: mapped[0].expertise_areas,
          expertise_list: mapped[0].expertise_list,
          updated_at: new Date().toISOString()
        })
        .eq('id', studentId);

      if (classificationError) {
        console.warn("⚠️ Lỗi cập nhật phân loại:", classificationError);
      }

      console.log("✅ Cập nhật sinh viên thành công");
      return { ...updatedStudent, ...mapped[0] };
    } catch (error) {
      console.error("❌ Lỗi cập nhật sinh viên:", error);
      throw error;
    }
  }

  /**
   * Xóa sinh viên
   */
  async deleteStudent(studentId) {
    try {
      console.log(`🗑️ Đang xóa sinh viên ID ${studentId}...`);
      
      const { error } = await supabase
        .from('students')
        .delete()
        .eq('id', studentId);

      if (error) {
        throw error;
      }

      console.log("✅ Xóa sinh viên thành công");
      return true;
    } catch (error) {
      console.error("❌ Lỗi xóa sinh viên:", error);
      throw error;
    }
  }

  /**
   * Lấy thống kê đồng bộ
   */
  async getSyncStats() {
    try {
      const { data, error } = await supabase
        .from('students')
        .select('id, level_prediction, predicted_level, expertise_areas, updated_at');

      if (error) {
        throw error;
      }

      const stats = {
        total: data.length,
        classified: data.filter(s => s.level_prediction).length,
        withExpertise: data.filter(s => s.expertise_areas && s.expertise_areas !== 'Toàn diện').length,
        lastUpdated: data.length > 0 ? Math.max(...data.map(s => new Date(s.updated_at).getTime())) : null
      };

      return stats;
    } catch (error) {
      console.error("❌ Lỗi lấy thống kê:", error);
      throw error;
    }
  }

  /**
   * Kiểm tra trạng thái đồng bộ
   */
  isCurrentlySyncing() {
    return this.isSyncing;
  }
}

// Tạo instance singleton
export const syncManager = new SyncManager();
