// Script test cập nhật dữ liệu vào Supabase
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://sittebrxnurswedfoleb.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdHRlYnJ4bnVyc3dlZGZvbGViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyODg1ODksImV4cCI6MjA3Njg2NDU4OX0.Uawa5v1M7_z7KN2kP-fatBkET5KnDLdMzbCW4K-ktJg';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function testUpdate() {
  try {
    console.log('🔄 Bắt đầu test cập nhật dữ liệu...');
    
    // 1. Lấy một sinh viên để test
    const { data: students, error: fetchError } = await supabase
      .from('students')
      .select('id, name, student_id')
      .limit(1);
    
    if (fetchError) {
      console.error('❌ Lỗi lấy dữ liệu:', fetchError);
      return;
    }
    
    if (!students || students.length === 0) {
      console.log('⚠️ Không có sinh viên nào để test');
      return;
    }
    
    const testStudent = students[0];
    console.log('📝 Sinh viên test:', testStudent);
    
    // 2. Test cập nhật với dữ liệu mẫu
    const testData = {
      level_prediction: 'Xuat sac',
      predicted_level: 'Kha',
      level_key: 'Xuat sac',
      expertise_areas: 'Lập trình, Phát triển Web',
      expertise_list: ['Lập trình', 'Phát triển Web'],
      updated_at: new Date().toISOString()
    };
    
    console.log('🔄 Đang cập nhật với dữ liệu:', testData);
    
    // 3. Thử cập nhật từng cột một
    console.log('\n--- Test cập nhật từng cột ---');
    
    // Test level_prediction
    const { error: error1 } = await supabase
      .from('students')
      .update({ level_prediction: testData.level_prediction })
      .eq('id', testStudent.id);
    
    if (error1) {
      console.error('❌ Lỗi cập nhật level_prediction:', error1);
    } else {
      console.log('✅ Cập nhật level_prediction thành công');
    }
    
    // Test predicted_level
    const { error: error2 } = await supabase
      .from('students')
      .update({ predicted_level: testData.predicted_level })
      .eq('id', testStudent.id);
    
    if (error2) {
      console.error('❌ Lỗi cập nhật predicted_level:', error2);
    } else {
      console.log('✅ Cập nhật predicted_level thành công');
    }
    
    // Test level_key
    const { error: error3 } = await supabase
      .from('students')
      .update({ level_key: testData.level_key })
      .eq('id', testStudent.id);
    
    if (error3) {
      console.error('❌ Lỗi cập nhật level_key:', error3);
    } else {
      console.log('✅ Cập nhật level_key thành công');
    }
    
    // Test expertise_areas
    const { error: error4 } = await supabase
      .from('students')
      .update({ expertise_areas: testData.expertise_areas })
      .eq('id', testStudent.id);
    
    if (error4) {
      console.error('❌ Lỗi cập nhật expertise_areas:', error4);
    } else {
      console.log('✅ Cập nhật expertise_areas thành công');
    }
    
    // Test expertise_list
    const { error: error5 } = await supabase
      .from('students')
      .update({ expertise_list: testData.expertise_list })
      .eq('id', testStudent.id);
    
    if (error5) {
      console.error('❌ Lỗi cập nhật expertise_list:', error5);
    } else {
      console.log('✅ Cập nhật expertise_list thành công');
    }
    
    // Test updated_at
    const { error: error6 } = await supabase
      .from('students')
      .update({ updated_at: testData.updated_at })
      .eq('id', testStudent.id);
    
    if (error6) {
      console.error('❌ Lỗi cập nhật updated_at:', error6);
    } else {
      console.log('✅ Cập nhật updated_at thành công');
    }
    
    // 4. Kiểm tra kết quả
    console.log('\n--- Kiểm tra kết quả ---');
    const { data: updatedStudent, error: checkError } = await supabase
      .from('students')
      .select('id, name, level_prediction, predicted_level, level_key, expertise_areas, expertise_list, updated_at')
      .eq('id', testStudent.id)
      .single();
    
    if (checkError) {
      console.error('❌ Lỗi kiểm tra kết quả:', checkError);
    } else {
      console.log('📊 Kết quả sau cập nhật:');
      console.log('  level_prediction:', updatedStudent.level_prediction);
      console.log('  predicted_level:', updatedStudent.predicted_level);
      console.log('  level_key:', updatedStudent.level_key);
      console.log('  expertise_areas:', updatedStudent.expertise_areas);
      console.log('  expertise_list:', updatedStudent.expertise_list);
      console.log('  updated_at:', updatedStudent.updated_at);
    }
    
  } catch (err) {
    console.error('❌ Exception:', err);
  }
}

testUpdate();
