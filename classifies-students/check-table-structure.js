// Script kiểm tra cấu trúc bảng students
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://sittebrxnurswedfoleb.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdHRlYnJ4bnVyc3dlZGZvbGViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODg1ODksImV4cCI6MjA3Njg2NDU4OX0.Uawa5v1M7_z7KN2kP-fatBkET5KnDLdMzbCW4K-ktJg';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function checkTableStructure() {
  try {
    console.log('🔄 Đang kiểm tra cấu trúc bảng students...');
    
    // Lấy một bản ghi để xem cấu trúc
    const { data, error } = await supabase
      .from('students')
      .select('*')
      .limit(1);
    
    if (error) {
      console.error('❌ Lỗi:', error);
      return;
    }
    
    if (data && data.length > 0) {
      console.log('✅ Cấu trúc bảng students:');
      const columns = Object.keys(data[0]);
      columns.forEach((col, index) => {
        console.log(`  ${index + 1}. ${col}: ${typeof data[0][col]}`);
      });
      
      // Kiểm tra các cột cần thiết
      const requiredColumns = [
        'level_prediction', 'predicted_level', 'level_key', 
        'expertise_areas', 'expertise_list', 'updated_at'
      ];
      
      console.log('\n🔍 Kiểm tra các cột cần thiết:');
      requiredColumns.forEach(col => {
        const exists = columns.includes(col);
        console.log(`  ${exists ? '✅' : '❌'} ${col}: ${exists ? 'Có' : 'Thiếu'}`);
      });
      
      // Test cập nhật với cột có sẵn
      console.log('\n🔄 Test cập nhật với cột có sẵn...');
      const { error: updateError } = await supabase
        .from('students')
        .update({ 
          updated_at: new Date().toISOString()
        })
        .eq('id', data[0].id);
      
      if (updateError) {
        console.error('❌ Lỗi cập nhật:', updateError);
      } else {
        console.log('✅ Cập nhật thành công!');
      }
      
    } else {
      console.log('⚠️ Không có dữ liệu trong bảng');
    }
    
  } catch (err) {
    console.error('❌ Exception:', err);
  }
}

checkTableStructure();
