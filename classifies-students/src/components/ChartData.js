  // Dữ liệu cho biểu đồ radar
  const radarData = {
    labels: ['Điểm số', 'Chuyên cần', 'Hành vi', 'Tham gia', 'Hoàn thành', 'Tương tác'],
    datasets: [
      {
        label: 'Hiệu suất học tập',
        data: [
          student?.academic_score * 10 || 0,
          student?.attendance_rate_100 || 0,
          student?.behCTior_score_100 || 0,
          student?.participation_score * 10 || 0,
          student?.assignment_completion * 100 || 0,
          student?.response_quality * 20 || 0
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  };

  // Dữ liệu cho biểu đồ tròn phân tích rủi ro
  const riskData = {
    labels: ['Điểm danh tốt', 'Vắng mặt', 'Nộp muộn', 'Hoàn thành đúng hạn'],
    datasets: [
      {
        data: [
          student?.attendance_rate * 100 || 0,
          100 - (student?.attendance_rate * 100) || 0,
          student?.late_submissions * 10 || 0,
          100 - (student?.late_submissions * 10) || 0
        ],
        backgroundColor: [
          chartColors.green,
          chartColors.red,
          chartColors.yellow,
          chartColors.blue
        ],
        borderWidth: 1
      }
    ]
  };

  // Dữ liệu cho biểu đồ xu hướng
  const generateTrendData = () => {
    const weeks = Array.from({ length: 16 }, (_, i) => `Tuần ${i + 1}`);
    const attendance = Array.from({ length: 16 }, () => 
      (student?.attendance_rate * 100 + (Math.random() * 10 - 5)));
    const behavior = Array.from({ length: 16 }, () => 
      (student?.behCTior_score_100 + (Math.random() * 10 - 5)));
    const academic = Array.from({ length: 16 }, () => 
      (student?.academic_score * 10 + (Math.random() * 10 - 5)));

    return {
      labels: weeks,
      datasets: [
        {
          label: 'Điểm danh',
          data: attendance,
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Hành vi',
          data: behavior,
          borderColor: 'rgba(54, 162, 235, 1)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Học tập',
          data: academic,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          fill: true,
          tension: 0.4
        }
      ]
    };
  };