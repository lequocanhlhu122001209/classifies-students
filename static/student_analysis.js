// Ham phan tich chi tiet sinh vien
function analyzeStudent(student) {
    const csvData = student.csv_data || {};
    const totalScore = parseFloat(csvData.total_score || 0);
    const studyHours = parseFloat(csvData.study_hours_per_week || 0);
    const attendance = parseFloat(csvData.attendance_rate || 0) * 100;
    const lateSubmissions = parseInt(csvData.late_submissions || 0);
    const participation = parseFloat(csvData.participation_score || 0);
    const assignment = parseFloat(csvData.assignment_completion || 0) * 100;
    const level = student.final_level;
    
    let html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;">';
    html += '<h4 style="color: #667eea; margin-bottom: 12px;">📊 Thống kê chi tiết:</h4>';
    html += '<table style="width: 100%; border-collapse: collapse;">';
    html += `<tr><td style="padding: 8px; border-bottom: 1px solid #e0e0e0;"><strong>Điểm trung bình:</strong></td><td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: right;"><strong>${totalScore.toFixed(1)}/10</strong></td></tr>`;
    html += `<tr><td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">Thời gian học tập:</td><td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: right;">${studyHours.toFixed(0)}h/tuần</td></tr>`;
    html += `<tr><td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">Tham gia lớp:</td><td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: right;">${attendance.toFixed(0)}%</td></tr>`;
    html += `<tr><td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">Hoàn thành bài tập:</td><td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: right;">${assignment.toFixed(0)}%</td></tr>`;
    html += `<tr><td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">Tham gia thảo luận:</td><td style="padding: 8px; border-bottom: 1px solid #e0e0e0; text-align: right;">${participation.toFixed(0)}/10</td></tr>`;
    html += `<tr><td style="padding: 8px;">Nộp muộn:</td><td style="padding: 8px; text-align: right; color: ${lateSubmissions >= 5 ? '#f44336' : '#666'};">${lateSubmissions} lần</td></tr>`;
    html += '</table>';
    html += '</div>';
    
    // Giai thich xep loai
    if (level === 'Xuat sac') {
        html += '<div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;">';
        html += '<h4 style="color: #2e7d32; margin-bottom: 10px;">🏆 Giải thích xếp loại: XUẤT SẮC</h4>';
        html += '<p style="color: #1b5e20; line-height: 1.8; margin-bottom: 10px;">';
        html += `<strong>✓ Điểm số xuất sắc:</strong> ${totalScore.toFixed(1)}/10<br>`;
        html += `<strong>✓ Thời gian học đầy đủ:</strong> ${studyHours.toFixed(0)}h/tuần<br>`;
        html += `<strong>✓ Tham gia tích cực:</strong> ${attendance.toFixed(0)}%`;
        html += '</p>';
        html += '<p style="color: #2e7d32; font-weight: 600;">💪 Đề xuất: Tiếp tục duy trì và chia sẻ kinh nghiệm học tập với các bạn.</p>';
        html += '</div>';
    } else if (level === 'Kha') {
        html += '<div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #2196F3;">';
        html += '<h4 style="color: #1565c0; margin-bottom: 10px;">📘 Giải thích xếp loại: KHÁ</h4>';
        html += '<p style="color: #0d47a1; line-height: 1.8; margin-bottom: 10px;">';
        html += `<strong>✓ Điểm số tốt:</strong> ${totalScore.toFixed(1)}/10<br>`;
        html += `<strong>✓ Thời gian học hợp lý:</strong> ${studyHours.toFixed(0)}h/tuần<br>`;
        html += `<strong>✓ Tham gia:</strong> ${attendance.toFixed(0)}%`;
        html += '</p>';
        html += '<p style="color: #1565c0; font-weight: 600;">💪 Đề xuất: Tăng cường thực hành và tham gia thảo luận để đạt mức xuất sắc.</p>';
        html += '</div>';
    } else if (level === 'Trung binh') {
        html += '<div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #FF9800;">';
        html += '<h4 style="color: #e65100; margin-bottom: 10px;">📙 Giải thích xếp loại: TRUNG BÌNH</h4>';
        
        // Phan tich ly do
        if (totalScore >= 9.0 && studyHours < 15) {
            html += '<div style="background: #ffebee; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #f44336;">';
            html += '<p style="color: #c62828; line-height: 1.8; margin-bottom: 8px;">';
            html += `<strong>⚠️ Phát hiện bất thường:</strong><br>`;
            html += `• Điểm cao (${totalScore.toFixed(1)}/10) nhưng học quá ít (${studyHours.toFixed(0)}h/tuần)<br>`;
            html += `• Nghi vấn: Có thể sử dụng AI, xem bài giải hoặc sao chép`;
            html += '</p>';
            html += '</div>';
            html += '<p style="color: #e65100; font-weight: 600;">💪 Đề xuất: Cần kiểm tra đánh giá trực tiếp (vấn đáp, làm bài trực tiếp) để xác nhận năng lực thực tế.</p>';
        } else {
            html += '<p style="color: #e65100; line-height: 1.8; margin-bottom: 10px;">';
            html += `<strong>Lý do xếp loại:</strong><br>`;
            html += `• Điểm số: ${totalScore.toFixed(1)}/10<br>`;
            html += `• Thời gian học: ${studyHours.toFixed(0)}h/tuần`;
            if (lateSubmissions >= 3) {
                html += `<br>• Nộp muộn: ${lateSubmissions} lần`;
            }
            html += '</p>';
            html += '<p style="color: #e65100; font-weight: 600;">💪 Đề xuất: Tăng thời gian học và tham gia thảo luận nhiều hơn.</p>';
        }
        html += '</div>';
    } else if (level === 'Yeu') {
        html += '<div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #f44336;">';
        html += '<h4 style="color: #c62828; margin-bottom: 10px;">📕 Giải thích xếp loại: YẾU</h4>';
        
        let reasons = [];
        if (totalScore < 5.5) {
            reasons.push(`Điểm thấp (${totalScore.toFixed(1)}/10) - Dưới mức đạt`);
        }
        if (totalScore >= 8.0 && studyHours < 15) {
            reasons.push(`<strong style="color: #d32f2f;">Điểm cao (${totalScore.toFixed(1)}/10) nhưng học quá ít (${studyHours.toFixed(0)}h/tuần) - Nghi vấn gian lận</strong>`);
        }
        if (lateSubmissions >= 5) {
            reasons.push(`Nộp muộn quá nhiều (${lateSubmissions} lần) - Thiếu kỷ luật`);
        }
        if (attendance < 70) {
            reasons.push(`Vắng học nhiều (${attendance.toFixed(0)}%) - Không theo dõi bài`);
        }
        if (assignment < 70) {
            reasons.push(`Không làm bài tập (${assignment.toFixed(0)}%) - Thiếu thực hành`);
        }
        
        html += '<p style="color: #c62828; line-height: 1.8; margin-bottom: 10px;">';
        html += '<strong>Lý do xếp loại:</strong><br>';
        html += '• ' + reasons.join('<br>• ');
        html += '</p>';
        html += '<p style="color: #c62828; font-weight: 600;">💪 Đề xuất: Cần gặp giảng viên ngay để được hỗ trợ và lập kế hoạch học tập cụ thể.</p>';
        html += '</div>';
    }
    
    return html;
}


// Hàm hiển thị chi tiết bài tập
function displayExerciseDetails(integratedData) {
    if (!integratedData || !integratedData.exercise_data || !integratedData.exercise_data.detailed_exercises) {
        return '<p>Không có dữ liệu bài tập chi tiết.</p>';
    }
    
    const detailedExercises = integratedData.exercise_data.detailed_exercises;
    let html = '<div style="margin-top: 20px;">';
    html += '<h3 style="color: #667eea; margin-bottom: 15px;">📝 Chi tiết bài tập từng môn học</h3>';
    
    // Duyệt qua từng môn học
    for (const [course, skills] of Object.entries(detailedExercises)) {
        html += `<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #667eea;">`;
        html += `<h4 style="color: #667eea; margin-bottom: 15px;">📚 ${course}</h4>`;
        
        // Duyệt qua từng kỹ năng
        for (const [skill, skillData] of Object.entries(skills)) {
            const avgScore = skillData.avg_score;
            const totalExercises = skillData.total_exercises;
            const exercises = skillData.exercises;
            
            // Màu sắc theo điểm
            let scoreColor = '#4CAF50'; // Giỏi
            if (avgScore < 5.0) scoreColor = '#f44336'; // Yếu
            else if (avgScore < 7.0) scoreColor = '#FF9800'; // Trung bình
            else if (avgScore < 8.0) scoreColor = '#2196F3'; // Khá
            
            html += `<div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e0e0e0;">`;
            html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">`;
            html += `<h5 style="color: #333; margin: 0;">✏️ ${skill}</h5>`;
            html += `<span style="background: ${scoreColor}; color: white; padding: 4px 12px; border-radius: 15px; font-weight: bold;">`;
            html += `${avgScore.toFixed(2)}/10`;
            html += `</span>`;
            html += `</div>`;
            
            html += `<p style="color: #666; font-size: 14px; margin-bottom: 10px;">Tổng số bài: ${totalExercises}</p>`;
            
            // Bảng chi tiết bài tập
            html += `<div style="overflow-x: auto;">`;
            html += `<table style="width: 100%; border-collapse: collapse; font-size: 13px;">`;
            html += `<thead>`;
            html += `<tr style="background: #f5f5f5;">`;
            html += `<th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Bài</th>`;
            html += `<th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Điểm</th>`;
            html += `<th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Thời gian</th>`;
            html += `<th style="padding: 8px; text-align: center; border: 1px solid #ddd;">Trạng thái</th>`;
            html += `</tr>`;
            html += `</thead>`;
            html += `<tbody>`;
            
            exercises.forEach(ex => {
                const score = ex.score;
                const time = ex.completion_time;
                const isAnomaly = ex.is_anomaly;
                
                // Màu điểm
                let scoreStyle = 'color: #4CAF50;';
                if (score < 5.0) scoreStyle = 'color: #f44336; font-weight: bold;';
                else if (score < 7.0) scoreStyle = 'color: #FF9800;';
                else if (score < 8.0) scoreStyle = 'color: #2196F3;';
                
                // Icon trạng thái
                let statusIcon = '✓';
                let statusColor = '#4CAF50';
                let statusText = 'Bình thường';
                
                if (isAnomaly) {
                    statusIcon = '⚠️';
                    statusColor = '#f44336';
                    statusText = ex.anomaly_reasons || 'Bất thường';
                }
                
                html += `<tr style="border-bottom: 1px solid #eee;">`;
                html += `<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">${ex.exercise_number}</td>`;
                html += `<td style="padding: 8px; text-align: center; border: 1px solid #ddd; ${scoreStyle}">${score.toFixed(1)}</td>`;
                html += `<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">${time.toFixed(1)} phút</td>`;
                html += `<td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: ${statusColor};" title="${statusText}">`;
                html += `${statusIcon}`;
                html += `</td>`;
                html += `</tr>`;
            });
            
            html += `</tbody>`;
            html += `</table>`;
            html += `</div>`;
            
            // Thống kê kỹ năng
            const avgTime = exercises.reduce((sum, ex) => sum + ex.completion_time, 0) / exercises.length;
            const passedCount = exercises.filter(ex => ex.score >= 5.0).length;
            const passRate = (passedCount / exercises.length * 100).toFixed(0);
            
            html += `<div style="margin-top: 10px; padding: 8px; background: #f9f9f9; border-radius: 5px; font-size: 12px; color: #666;">`;
            html += `<strong>Thống kê:</strong> `;
            html += `Điểm TB: ${avgScore.toFixed(2)} | `;
            html += `Thời gian TB: ${avgTime.toFixed(1)} phút | `;
            html += `Tỷ lệ đạt: ${passRate}% (${passedCount}/${exercises.length})`;
            html += `</div>`;
            
            html += `</div>`; // End skill div
        }
        
        html += `</div>`; // End course div
    }
    
    html += '</div>';
    return html;
}

// Hàm hiển thị điểm tích hợp
function displayIntegratedScore(integratedData) {
    if (!integratedData) {
        return '';
    }
    
    const originalScore = integratedData.original_score;
    const integratedScore = integratedData.integrated_score;
    const scoreDiff = integratedData.score_difference;
    const classification = integratedData.classification;
    const components = integratedData.components;
    
    let html = '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;">';
    html += '<h3 style="margin-bottom: 15px;">🎯 Điểm tích hợp (Công thức mới)</h3>';
    
    html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px;">';
    
    // Điểm gốc
    html += '<div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">';
    html += '<div style="font-size: 14px; opacity: 0.9;">Điểm gốc</div>';
    html += `<div style="font-size: 28px; font-weight: bold;">${originalScore.toFixed(2)}</div>`;
    html += '</div>';
    
    // Điểm tích hợp
    html += '<div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">';
    html += '<div style="font-size: 14px; opacity: 0.9;">Điểm tích hợp</div>';
    html += `<div style="font-size: 28px; font-weight: bold;">${integratedScore.toFixed(2)}</div>`;
    html += '</div>';
    
    // Chênh lệch
    const diffColor = scoreDiff >= 0 ? '#4CAF50' : '#f44336';
    const diffIcon = scoreDiff >= 0 ? '↑' : '↓';
    html += '<div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">';
    html += '<div style="font-size: 14px; opacity: 0.9;">Chênh lệch</div>';
    html += `<div style="font-size: 28px; font-weight: bold; color: ${diffColor};">${diffIcon} ${Math.abs(scoreDiff).toFixed(2)}</div>`;
    html += '</div>';
    
    // Phân loại
    html += '<div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">';
    html += '<div style="font-size: 14px; opacity: 0.9;">Phân loại</div>';
    html += `<div style="font-size: 24px; font-weight: bold;">${classification}</div>`;
    html += '</div>';
    
    html += '</div>';
    
    // Cấu thành điểm
    html += '<div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px;">';
    html += '<h4 style="margin-bottom: 10px;">📊 Cấu thành điểm:</h4>';
    html += '<div style="display: grid; gap: 8px;">';
    html += `<div>• Điểm bài tập (30%): <strong>${components.exercise_avg.toFixed(2)}</strong> → ${(components.exercise_avg * 0.3).toFixed(2)}</div>`;
    html += `<div>• Điểm giữa kỳ+lớp (30%): <strong>${components.midterm.toFixed(2)}</strong> → ${(components.midterm * 0.3).toFixed(2)}</div>`;
    html += `<div>• Điểm cuối kỳ (40%): <strong>${components.final.toFixed(2)}</strong> → ${(components.final * 0.4).toFixed(2)}</div>`;
    html += '</div>';
    html += '</div>';
    
    html += '</div>';
    
    return html;
}
