import { kmeans } from 'ml-kmeans';
import KNN from 'ml-knn';

// Chuẩn hóa dữ liệu về khoảng [0, 1]
export function normalizeData(value, min, max) {
  if (max === min) return 0;
  return (value - min) / (max - min);
}

// Phân tích và phân loại sinh viên
export function classifyStudents(students) {
  if (!students || students.length === 0) return [];

  // 1. Chuẩn bị dữ liệu với các cột mới
  const features = students.map(student => {
    // Tìm min/max của các metrics mới
    const metrics = students.reduce((acc, s) => {
      acc.midterm_score.values.push(Number(s.midterm_score) || 0);
      acc.final_score.values.push(Number(s.final_score) || 0);
      acc.homework_score.values.push(Number(s.homework_score) || 0);
      acc.attendance_rate.values.push(Number(s.attendance_rate) || 0);
      acc.assignment_completion.values.push(Number(s.assignment_completion) || 0);
      acc.study_hours_per_week.values.push(Number(s.study_hours_per_week) || 0);
      acc.participation_score.values.push(Number(s.participation_score) || 0);
      acc.late_submissions.values.push(Number(s.late_submissions) || 0);
      acc.extra_activities.values.push(Number(s.extra_activities) || 0);
      acc.lms_usage_hours.values.push(Number(s.lms_usage_hours) || 0);
      acc.response_quality.values.push(Number(s.response_quality) || 0);
      acc.total_score.values.push(Number(s.total_score) || 0);
      acc.behavior_score.values.push(Number(s.behavior_score) || 0);
      acc.behavior_score_100.values.push(Number(s.behavior_score_100) || 0);
      acc.attendance_rate_100.values.push(Number(s.attendance_rate_100) || 0);
      acc.assignment_completion_100.values.push(Number(s.assignment_completion_100) || 0);
      return acc;
    }, {
      midterm_score: { values: [] },
      final_score: { values: [] },
      homework_score: { values: [] },
      attendance_rate: { values: [] },
      assignment_completion: { values: [] },
      study_hours_per_week: { values: [] },
      participation_score: { values: [] },
      late_submissions: { values: [] },
      extra_activities: { values: [] },
      lms_usage_hours: { values: [] },
      response_quality: { values: [] },
      total_score: { values: [] },
      behavior_score: { values: [] },
      behavior_score_100: { values: [] },
      attendance_rate_100: { values: [] },
      assignment_completion_100: { values: [] }
    });

    // Tính min/max cho mỗi metric
    Object.keys(metrics).forEach(key => {
      const values = metrics[key].values;
      metrics[key].min = Math.min(...values);
      metrics[key].max = Math.max(...values);
    });

    // Chuẩn hóa các đặc trưng quan trọng nhất
    const normalizedFeatures = [
      normalizeData(Number(student.midterm_score) || 0, metrics.midterm_score.min, metrics.midterm_score.max),
      normalizeData(Number(student.final_score) || 0, metrics.final_score.min, metrics.final_score.max),
      normalizeData(Number(student.homework_score) || 0, metrics.homework_score.min, metrics.homework_score.max),
      normalizeData(Number(student.attendance_rate) || 0, metrics.attendance_rate.min, metrics.attendance_rate.max),
      normalizeData(Number(student.assignment_completion) || 0, metrics.assignment_completion.min, metrics.assignment_completion.max),
      normalizeData(Number(student.study_hours_per_week) || 0, metrics.study_hours_per_week.min, metrics.study_hours_per_week.max),
      normalizeData(Number(student.participation_score) || 0, metrics.participation_score.min, metrics.participation_score.max),
      normalizeData(Number(student.late_submissions) || 0, metrics.late_submissions.min, metrics.late_submissions.max),
      normalizeData(Number(student.extra_activities) || 0, metrics.extra_activities.min, metrics.extra_activities.max),
      normalizeData(Number(student.lms_usage_hours) || 0, metrics.lms_usage_hours.min, metrics.lms_usage_hours.max),
      normalizeData(Number(student.response_quality) || 0, metrics.response_quality.min, metrics.response_quality.max),
      normalizeData(Number(student.total_score) || 0, metrics.total_score.min, metrics.total_score.max),
      normalizeData(Number(student.behavior_score) || 0, metrics.behavior_score.min, metrics.behavior_score.max),
      normalizeData(Number(student.behavior_score_100) || 0, metrics.behavior_score_100.min, metrics.behavior_score_100.max),
      normalizeData(Number(student.attendance_rate_100) || 0, metrics.attendance_rate_100.min, metrics.attendance_rate_100.max),
      normalizeData(Number(student.assignment_completion_100) || 0, metrics.assignment_completion_100.min, metrics.assignment_completion_100.max)
    ];

    return normalizedFeatures;
  });

  // 2. Thực hiện K-means clustering (k=4 cho 4 mức độ)
  const { clusters } = kmeans(features, 4, {
    maxIterations: 100,
    tolerance: 0.0001,
    withIterations: true
  });

  // 3. Phân tích các cụm để gán nhãn
  const clusterStats = clusters.reduce((acc, cluster, idx) => {
    const studentData = students[idx];
    if (!acc[cluster]) {
      acc[cluster] = {
        count: 0,
        total_midterm: 0,
        total_final: 0,
        total_homework: 0,
        total_attendance: 0,
        total_assignment_completion: 0,
        total_study_hours: 0,
        total_participation: 0,
        total_behavior: 0,
        total_score: 0
      };
    }
    acc[cluster].count++;
    acc[cluster].total_midterm += Number(studentData.midterm_score) || 0;
    acc[cluster].total_final += Number(studentData.final_score) || 0;
    acc[cluster].total_homework += Number(studentData.homework_score) || 0;
    acc[cluster].total_attendance += Number(studentData.attendance_rate) || 0;
    acc[cluster].total_assignment_completion += Number(studentData.assignment_completion) || 0;
    acc[cluster].total_study_hours += Number(studentData.study_hours_per_week) || 0;
    acc[cluster].total_participation += Number(studentData.participation_score) || 0;
    acc[cluster].total_behavior += Number(studentData.behavior_score) || 0;
    acc[cluster].total_score += Number(studentData.total_score) || 0;
    return acc;
  }, {});

  // Tính trung bình và xếp hạng các cụm dựa trên điểm và hành vi
  const clusterRanks = Object.keys(clusterStats).map(cluster => ({
    cluster: Number(cluster),
    avg_midterm: clusterStats[cluster].total_midterm / clusterStats[cluster].count,
    avg_final: clusterStats[cluster].total_final / clusterStats[cluster].count,
    avg_homework: clusterStats[cluster].total_homework / clusterStats[cluster].count,
    avg_attendance: clusterStats[cluster].total_attendance / clusterStats[cluster].count,
    avg_assignment_completion: clusterStats[cluster].total_assignment_completion / clusterStats[cluster].count,
    avg_study_hours: clusterStats[cluster].total_study_hours / clusterStats[cluster].count,
    avg_participation: clusterStats[cluster].total_participation / clusterStats[cluster].count,
    avg_behavior: clusterStats[cluster].total_behavior / clusterStats[cluster].count,
    avg_total_score: clusterStats[cluster].total_score / clusterStats[cluster].count
  }));

  // Sắp xếp các cụm: ưu tiên theo tổng điểm, sau đó theo hành vi và tham gia
  clusterRanks.sort((a, b) => {
    if (b.avg_total_score !== a.avg_total_score) return b.avg_total_score - a.avg_total_score;
    if (b.avg_behavior !== a.avg_behavior) return b.avg_behavior - a.avg_behavior;
    if (b.avg_attendance !== a.avg_attendance) return b.avg_attendance - a.avg_attendance;
    return b.avg_participation - a.avg_participation;
  });

  // Map clusters to levels theo thứ tự rank (top -> Xuất sắc, ...)
  const clusterToLevel = {};
  clusterRanks.forEach((rank, idx) => {
    if (idx === 0) clusterToLevel[rank.cluster] = 'Xuat sac';
    else if (idx === 1) clusterToLevel[rank.cluster] = 'Kha';
    else if (idx === 2) clusterToLevel[rank.cluster] = 'Trung binh';
    else clusterToLevel[rank.cluster] = 'Yeu';
  });

  // 4. Thực hiện KNN classification
  const knnPredictions = performKNNClassification(students, features);

  // 5. Return classified students với cả K-means và KNN
  return students.map((student, idx) => ({
    ...student,
    level_prediction: clusterToLevel[clusters[idx]], // K-means result
    predicted_level: knnPredictions[idx] // KNN result
  }));
}

// Hàm thực hiện KNN classification
function performKNNClassification(students, features) {
  if (students.length < 5) {
    // Nếu ít dữ liệu, sử dụng heuristic đơn giản
    return students.map(student => {
      const midterm = Number(student.midterm_score) || 0;
      const final = Number(student.final_score) || 0;
      const homework = Number(student.homework_score) || 0;
      const attendance = Number(student.attendance_rate) || 0;
      const behavior = Number(student.behavior_score) || 0;
      const total = Number(student.total_score) || 0;
      
      // Tính điểm trừ cho nộp muộn (mỗi lần nộp muộn trừ 0.5 điểm)
      const latePenalty = (Number(student.late_submissions) || 0) * 0.5;
      
      // Tính điểm cơ bản
      const baseScore = (midterm * 0.2 + final * 0.3 + homework * 0.2 + attendance * 0.1 + behavior * 0.1 + total * 0.1);
      
      // Áp dụng điểm trừ
      const finalScore = Math.max(0, baseScore - latePenalty);
      
      // Ngưỡng phân loại nghiêm ngặt hơn
      if (finalScore >= 9.0 && attendance >= 0.9 && (Number(student.assignment_completion) || 0) >= 0.8) return 'Xuat sac';
      if (finalScore >= 7.5 && attendance >= 0.8 && (Number(student.assignment_completion) || 0) >= 0.6) return 'Kha';
      if (finalScore >= 6.0 && attendance >= 0.7) return 'Trung binh';
      return 'Yeu';
    });
  }

  // Tạo training data từ 70% dữ liệu đầu tiên
  const trainingSize = Math.floor(students.length * 0.7);
  const trainingData = features.slice(0, trainingSize);
  const trainingLabels = students.slice(0, trainingSize).map(student => {
    const midterm = Number(student.midterm_score) || 0;
    const final = Number(student.final_score) || 0;
    const homework = Number(student.homework_score) || 0;
    const attendance = Number(student.attendance_rate) || 0;
    const behavior = Number(student.behavior_score) || 0;
    const total = Number(student.total_score) || 0;
    
    // Tính điểm trừ cho nộp muộn
    const latePenalty = (Number(student.late_submissions) || 0) * 0.5;
    const baseScore = (midterm * 0.2 + final * 0.3 + homework * 0.2 + attendance * 0.1 + behavior * 0.1 + total * 0.1);
    const finalScore = Math.max(0, baseScore - latePenalty);
    
    // Ngưỡng phân loại nghiêm ngặt hơn
    if (finalScore >= 9.0 && attendance >= 0.9 && (Number(student.assignment_completion) || 0) >= 0.8) return 'Xuat sac';
    if (finalScore >= 7.5 && attendance >= 0.8 && (Number(student.assignment_completion) || 0) >= 0.6) return 'Kha';
    if (finalScore >= 6.0 && attendance >= 0.7) return 'Trung binh';
    return 'Yeu';
  });

  // Tạo test data từ 30% dữ liệu còn lại
  const testData = features.slice(trainingSize);
  
  try {
    // Khởi tạo và train KNN model
    const knn = new KNN({
      k: Math.min(5, Math.floor(trainingSize / 2))
    });
    
    knn.train(trainingData, trainingLabels);
    
    // Dự đoán cho test data
    const testPredictions = knn.predict(testData);
    
    // Kết hợp training labels với test predictions
    const allPredictions = [...trainingLabels, ...testPredictions];
    
    return allPredictions;
  } catch (error) {
    console.warn('KNN classification failed, using heuristic fallback:', error);
    // Fallback to heuristic method
    return students.map(student => {
      const midterm = Number(student.midterm_score) || 0;
      const final = Number(student.final_score) || 0;
      const homework = Number(student.homework_score) || 0;
      const attendance = Number(student.attendance_rate) || 0;
      const behavior = Number(student.behavior_score) || 0;
      const total = Number(student.total_score) || 0;
      
      // Tính điểm trừ cho nộp muộn
      const latePenalty = (Number(student.late_submissions) || 0) * 0.5;
      const baseScore = (midterm * 0.2 + final * 0.3 + homework * 0.2 + attendance * 0.1 + behavior * 0.1 + total * 0.1);
      const finalScore = Math.max(0, baseScore - latePenalty);
      
      // Ngưỡng phân loại nghiêm ngặt hơn
      if (finalScore >= 9.0 && attendance >= 0.9 && (Number(student.assignment_completion) || 0) >= 0.8) return 'Xuat sac';
      if (finalScore >= 7.5 && attendance >= 0.8 && (Number(student.assignment_completion) || 0) >= 0.6) return 'Kha';
      if (finalScore >= 6.0 && attendance >= 0.7) return 'Trung binh';
      return 'Yeu';
    });
  }
}

// New function to classify students by expertise areas with department-specific logic
export function classifyByExpertise(students) {
  if (!students || students.length === 0) return [];
  
  return students.map(student => {
    const expertise = [];
    
    // Lấy thông tin khoa của sinh viên
    const department = (student.Khoa || student.department || '').toLowerCase();
    const studentName = (student.name || '').toLowerCase();
    
    // Tính toán các chỉ số trung bình để so sánh
    const avgLMS = students.reduce((sum, s) => sum + (Number(s.lms_usage_hours) || 0), 0) / students.length;
    const avgResponse = students.reduce((sum, s) => sum + (Number(s.response_quality) || 0), 0) / students.length;
    const avgScore = students.reduce((sum, s) => sum + (Number(s.total_score) || 0), 0) / students.length;
    const avgExtra = students.reduce((sum, s) => sum + (Number(s.extra_activities) || 0), 0) / students.length;
    const avgStudy = students.reduce((sum, s) => sum + (Number(s.study_hours_per_week) || 0), 0) / students.length;
    
    // Tạo random seed dựa trên ID sinh viên để đảm bảo tính nhất quán
    const randomSeed = (student.id || 0) * 12345;
    const random = (seed) => {
      const x = Math.sin(seed) * 10000;
      return x - Math.floor(x);
    };
    
    // Hàm tạo random nhưng có trọng số theo khoa
    const getRandomExpertise = (departmentExpertise, generalExpertise = []) => {
      const allOptions = [...departmentExpertise, ...generalExpertise];
      const departmentWeight = 0.7; // Trọng số cho lĩnh vực của khoa
      const generalWeight = 0.3;   // Trọng số cho lĩnh vực chung
      
      const randomValue = random(randomSeed + expertise.length);
      
      if (randomValue < departmentWeight && departmentExpertise.length > 0) {
        const index = Math.floor(random(randomSeed + expertise.length + 100) * departmentExpertise.length);
        return departmentExpertise[index];
      } else if (generalExpertise.length > 0) {
        const index = Math.floor(random(randomSeed + expertise.length + 200) * generalExpertise.length);
        return generalExpertise[index];
      }
      return null;
    };
    
    // Định nghĩa lĩnh vực theo khoa
    const departmentExpertise = {
      // Công nghệ thông tin
      'cntt': ['Lập trình', 'Phát triển Web', 'Cơ sở dữ liệu', 'Mạng máy tính', 'An ninh mạng', 'Trí tuệ nhân tạo', 'Phát triển ứng dụng di động', 'Quản lý dự án CNTT'],
      'công nghệ thông tin': ['Lập trình', 'Phát triển Web', 'Cơ sở dữ liệu', 'Mạng máy tính', 'An ninh mạng', 'Trí tuệ nhân tạo', 'Phát triển ứng dụng di động', 'Quản lý dự án CNTT'],
      'it': ['Lập trình', 'Phát triển Web', 'Cơ sở dữ liệu', 'Mạng máy tính', 'An ninh mạng', 'Trí tuệ nhân tạo', 'Phát triển ứng dụng di động', 'Quản lý dự án CNTT'],
      'computer science': ['Lập trình', 'Phát triển Web', 'Cơ sở dữ liệu', 'Mạng máy tính', 'An ninh mạng', 'Trí tuệ nhân tạo', 'Phát triển ứng dụng di động', 'Quản lý dự án CNTT'],
      
      // Anh văn
      'anh văn': ['Giao tiếp tiếng Anh', 'Dịch thuật', 'Viết học thuật', 'Thuyết trình', 'Giao tiếp đa văn hóa', 'Biên phiên dịch'],
      'english': ['Giao tiếp tiếng Anh', 'Dịch thuật', 'Viết học thuật', 'Thuyết trình', 'Giao tiếp đa văn hóa', 'Biên phiên dịch'],
      'ngôn ngữ anh': ['Giao tiếp tiếng Anh', 'Dịch thuật', 'Viết học thuật', 'Thuyết trình', 'Giao tiếp đa văn hóa', 'Biên phiên dịch'],
      
      // Kế toán
      'kế toán': ['Kế toán tài chính', 'Kế toán quản trị', 'Kiểm toán', 'Thuế', 'Phân tích tài chính', 'Kế toán doanh nghiệp'],
      'accounting': ['Kế toán tài chính', 'Kế toán quản trị', 'Kiểm toán', 'Thuế', 'Phân tích tài chính', 'Kế toán doanh nghiệp'],
      'tài chính': ['Kế toán tài chính', 'Kế toán quản trị', 'Kiểm toán', 'Thuế', 'Phân tích tài chính', 'Kế toán doanh nghiệp'],
      
      // Quản trị kinh doanh
      'quản trị kinh doanh': ['Quản lý nhân sự', 'Marketing', 'Quản lý dự án', 'Kinh doanh quốc tế', 'Quản lý chuỗi cung ứng', 'Quản lý bán hàng'],
      'business': ['Quản lý nhân sự', 'Marketing', 'Quản lý dự án', 'Kinh doanh quốc tế', 'Quản lý chuỗi cung ứng', 'Quản lý bán hàng'],
      'marketing': ['Marketing', 'Quản lý nhân sự', 'Quản lý dự án', 'Kinh doanh quốc tế', 'Quản lý chuỗi cung ứng', 'Quản lý bán hàng'],
      
      // Xây dựng
      'xây dựng': ['Thiết kế kiến trúc', 'Kết cấu xây dựng', 'Quản lý dự án xây dựng', 'Vật liệu xây dựng', 'An toàn lao động', 'Môi trường xây dựng'],
      'construction': ['Thiết kế kiến trúc', 'Kết cấu xây dựng', 'Quản lý dự án xây dựng', 'Vật liệu xây dựng', 'An toàn lao động', 'Môi trường xây dựng'],
      'kiến trúc': ['Thiết kế kiến trúc', 'Kết cấu xây dựng', 'Quản lý dự án xây dựng', 'Vật liệu xây dựng', 'An toàn lao động', 'Môi trường xây dựng'],
      
      // Kỹ thuật
      'kỹ thuật': ['Lập trình', 'Thiết kế kỹ thuật', 'Quản lý dự án', 'Nghiên cứu', 'Giải quyết vấn đề', 'Sáng tạo'],
      'engineering': ['Lập trình', 'Thiết kế kỹ thuật', 'Quản lý dự án', 'Nghiên cứu', 'Giải quyết vấn đề', 'Sáng tạo'],
      
      // Y tế
      'y tế': ['Giao tiếp', 'Làm việc nhóm', 'Nghiên cứu', 'Giải quyết vấn đề', 'Quản lý thời gian', 'Chăm sóc bệnh nhân'],
      'medicine': ['Giao tiếp', 'Làm việc nhóm', 'Nghiên cứu', 'Giải quyết vấn đề', 'Quản lý thời gian', 'Chăm sóc bệnh nhân'],
      'y khoa': ['Giao tiếp', 'Làm việc nhóm', 'Nghiên cứu', 'Giải quyết vấn đề', 'Quản lý thời gian', 'Chăm sóc bệnh nhân']
    };
    
    // Lĩnh vực chung cho tất cả sinh viên
    const generalExpertise = ['Lãnh đạo', 'Làm việc nhóm', 'Giải quyết vấn đề', 'Sáng tạo', 'Giao tiếp', 'Quản lý thời gian', 'Nghiên cứu', 'Thuyết trình'];
    
    // Xác định lĩnh vực theo khoa
    let studentDepartmentExpertise = [];
    for (const [key, value] of Object.entries(departmentExpertise)) {
      if (department.includes(key) || studentName.includes(key)) {
        studentDepartmentExpertise = value;
        break;
      }
    }
    
    // Nếu không tìm thấy khoa phù hợp, sử dụng lĩnh vực chung
    if (studentDepartmentExpertise.length === 0) {
      studentDepartmentExpertise = generalExpertise;
    }
    
    // Tính điểm tổng hợp để xác định số lượng lĩnh vực
    const totalScore = Number(student.total_score) || 0;
    const midtermScore = Number(student.midterm_score) || 0;
    const finalScore = Number(student.final_score) || 0;
    const homeworkScore = Number(student.homework_score) || 0;
    const attendance = Number(student.attendance_rate) || 0;
    const participation = Number(student.participation_score) || 0;
    const behavior = Number(student.behavior_score) || 0;
    
    // Tính điểm trung bình
    const averageScore = (totalScore + midtermScore + finalScore + homeworkScore) / 4;
    const engagementScore = (attendance + participation + behavior) / 3;
    const overallScore = (averageScore + engagementScore) / 2;
    
    // Xác định số lượng lĩnh vực dựa trên điểm số
    let numExpertise = 1; // Mặc định 1 lĩnh vực
    if (overallScore >= 9.0) numExpertise = 4; // Xuất sắc: 4 lĩnh vực
    else if (overallScore >= 8.0) numExpertise = 3; // Giỏi: 3 lĩnh vực
    else if (overallScore >= 7.0) numExpertise = 2; // Khá: 2 lĩnh vực
    else if (overallScore >= 6.0) numExpertise = 1; // Trung bình: 1 lĩnh vực
    else numExpertise = 1; // Yếu: 1 lĩnh vực
    
    // Tạo danh sách lĩnh vực ngẫu nhiên nhưng có trọng số
    const selectedExpertise = new Set();
    
    // Ưu tiên lĩnh vực của khoa (70% cơ hội)
    for (let i = 0; i < numExpertise * 2; i++) {
      const randomValue = random(randomSeed + i);
      if (randomValue < 0.7 && studentDepartmentExpertise.length > 0) {
        const index = Math.floor(random(randomSeed + i + 100) * studentDepartmentExpertise.length);
        selectedExpertise.add(studentDepartmentExpertise[index]);
      } else if (generalExpertise.length > 0) {
        const index = Math.floor(random(randomSeed + i + 200) * generalExpertise.length);
        selectedExpertise.add(generalExpertise[index]);
      }
      
      if (selectedExpertise.size >= numExpertise) break;
    }
    
    // Nếu chưa đủ số lượng, thêm lĩnh vực chung
    while (selectedExpertise.size < numExpertise && generalExpertise.length > 0) {
      const index = Math.floor(random(randomSeed + selectedExpertise.size + 300) * generalExpertise.length);
      selectedExpertise.add(generalExpertise[index]);
    }
    
    // Chuyển Set thành Array
    const expertiseArray = Array.from(selectedExpertise);
    
    // Nếu không có lĩnh vực nào, gán "Toàn diện"
    const expertiseStr = expertiseArray.length > 0 ? expertiseArray.join(', ') : 'Toàn diện';
    
    return {
      ...student,
      expertise_areas: expertiseStr,
      expertise_list: expertiseArray
    };
  });
}