import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { Bar, Line, Radar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const StudentDetail = () => {
  // Hàm cập nhật điểm tổng quát
  const updateCourseScores = (studentData) => {
    const scores = [
      studentData.intro_to_programming || 0,
      studentData.programming_techniques || 0,
      studentData.data_structures || 0,
      studentData.oop || 0
    ];
    setCourseScores(scores);
  };

  // Hàm cập nhật điểm kỹ năng
  const updateSkillScores = (skillData) => {
    setSkillScores({
      nmlt: [
        skillData.nmlt_variables || 0,
        skillData.nmlt_syntax || 0,
        skillData.nmlt_control || 0,
        skillData.nmlt_functions || 0
      ],
      ktlt: [
        skillData.ktlt_structured || 0,
        skillData.ktlt_algorithms || 0,
        skillData.ktlt_optimization || 0,
        skillData.ktlt_debugging || 0
      ],
      ctdl: [
        skillData.ctdl_trees || 0,
        skillData.ctdl_linkedlists || 0,
        skillData.ctdl_arrays || 0,
        skillData.ctdl_stacks_queues || 0
      ],
      oop: [
        skillData.oop_inheritance || 0,
        skillData.oop_classes_objects || 0,
        skillData.oop_polymorphism || 0,
        skillData.oop_encapsulation || 0
      ]
    });
  };
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendData, setTrendData] = useState(null);
  const [courseScores, setCourseScores] = useState(null);
  const [skillScores, setSkillScores] = useState({
    nmlt: [],
    ktlt: [],
    ctdl: [],
    oop: []
  });

  // Dữ liệu điểm kỹ năng Nhập môn lập trình
  const nmltSkillData = {
    labels: [
      'Biến và Kiểu dữ liệu',
      'Cú pháp cơ bản',
      'Cấu trúc điều khiển',
      'Hàm cơ bản'
    ],
    datasets: [{
      label: 'Điểm kỹ năng',
      data: skillScores.nmlt,
      backgroundColor: 'rgba(54, 162, 235, 0.6)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }]
  };

  // Dữ liệu điểm kỹ năng Kỹ thuật lập trình
  const ktltSkillData = {
    labels: [
      'Lập trình có cấu trúc',
      'Thiết kế thuật toán',
      'Tối ưu hóa mã nguồn',
      'Xử lý lỗi và Debugging'
    ],
    datasets: [{
      label: 'Điểm kỹ năng',
      data: skillScores.ktlt,
      backgroundColor: 'rgba(75, 192, 192, 0.6)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1
    }]
  };

  // Dữ liệu điểm kỹ năng CTDL & GT
  const ctdlSkillData = {
    labels: [
      'Cây',
      'Danh sách liên kết',
      'Mảng',
      'Stack và Queue'
    ],
    datasets: [{
      label: 'Điểm kỹ năng',
      data: skillScores.ctdl,
      backgroundColor: 'rgba(255, 159, 64, 0.6)',
      borderColor: 'rgba(255, 159, 64, 1)',
      borderWidth: 1
    }]
  };

  // Dữ liệu điểm kỹ năng OOP
  const oopSkillData = {
    labels: [
      'Kế thừa',
      'Lớp và Đối tượng',
      'Đa hình',
      'Đóng gói'
    ],
    datasets: [{
      label: 'Điểm kỹ năng',
      data: skillScores.oop,
      backgroundColor: 'rgba(153, 102, 255, 0.6)',
      borderColor: 'rgba(153, 102, 255, 1)',
      borderWidth: 1
    }]
  };

  // Options cho biểu đồ kỹ năng
  const skillChartOptions = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 1
        }
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };

  // Dữ liệu điểm số các môn học
  const courseData = {
    labels: [
      'Nhập Môn Lập Trình',
      'Kỹ Thuật Lập Trình',
      'Cấu Trúc Dữ Liệu và Giải Thuật',
      'Lập Trình Hướng Đối Tượng'
    ],
    datasets: [{
      label: 'Điểm trung bình',
      data: courseScores || [0, 0, 0, 0],
      backgroundColor: [
        'rgba(54, 162, 235, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(153, 102, 255, 0.6)'
      ],
      borderColor: [
        'rgba(54, 162, 235, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(153, 102, 255, 1)'
      ],
      borderWidth: 1
    }]
  };

  // Options cho biểu đồ cột
  const courseChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Điểm số các môn học',
        font: {
          size: 16
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 1
        }
      }
    }
  };

  // Dữ liệu cho biểu đồ radar
  const radarData = {
    labels: ['Kỹ năng học tập', 'Tham gia lớp học', 'Hoàn thành bài tập', 'Điểm danh', 'Hoạt động online', 'Kết quả học tập'],
    datasets: [
      {
        label: 'Hiệu suất học tập',
        data: [85, 90, 78, 88, 95, 82],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        fill: true
      }
    ]
  };

  // Hàm tạo dữ liệu xu hướng
  const generateTrendData = () => {
    return {
      labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10'],
      datasets: [
        {
          label: 'Điểm tổng hợp',
          data: [75, 78, 80, 79, 85, 83, 86, 87, 88, 90],
          fill: true,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4
        }
      ]
    };
  };

  // Dữ liệu kỹ năng cho từng môn học
  // Dữ liệu phân bổ thời gian học tập
  const timeDistributionData = {
    labels: [
      'Học trên lớp',
      'Tự học',
      'Làm bài tập',
      'Thực hành/Thí nghiệm',
      'Học nhóm',
      'Tham khảo tài liệu'
    ],
    datasets: [{
      data: [30, 25, 20, 10, 8, 7],
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
      ],
      borderWidth: 1
    }]
  };

  const subjectSkillsData = {
    Toán: {
      labels: ['Tư duy logic', 'Kỹ năng tính toán', 'Giải quyết vấn đề', 'Tư duy trừu tượng', 'Ứng dụng thực tế', 'Tốc độ xử lý'],
      datasets: [{
        label: 'Kỹ năng Toán học',
        data: [85, 90, 88, 92, 75, 87],
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
        fill: true
      }]
    },
    Lý: {
      labels: ['Phân tích hiện tượng', 'Thực hành thí nghiệm', 'Tính toán vật lý', 'Ứng dụng công thức', 'Quan sát', 'Giải thích nguyên lý'],
      datasets: [{
        label: 'Kỹ năng Vật lý',
        data: [82, 88, 85, 90, 95, 87],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        fill: true
      }]
    },
    Hóa: {
      labels: ['Hiểu phản ứng', 'Thực hành thí nghiệm', 'Tính toán hóa học', 'An toàn phòng thí nghiệm', 'Quan sát', 'Phân tích định tính'],
      datasets: [{
        label: 'Kỹ năng Hóa học',
        data: [88, 92, 85, 95, 90, 83],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        fill: true
      }]
    },
    Sinh: {
      labels: ['Quan sát sinh học', 'Thực hành thí nghiệm', 'Phân tích số liệu', 'Hiểu cấu trúc', 'Phân loại sinh vật', 'Vẽ sơ đồ'],
      datasets: [{
        label: 'Kỹ năng Sinh học',
        data: [90, 85, 80, 88, 92, 85],
        backgroundColor: 'rgba(255, 206, 86, 0.2)',
        borderColor: 'rgba(255, 206, 86, 1)',
        borderWidth: 1,
        fill: true
      }]
    }
  };
  
  // Màu sắc cho biểu đồ
  const chartColors = {
    red: 'rgba(255, 99, 132, 0.5)',
    blue: 'rgba(54, 162, 235, 0.5)',
    green: 'rgba(75, 192, 192, 0.5)',
    yellow: 'rgba(255, 206, 86, 0.5)',
    purple: 'rgba(153, 102, 255, 0.5)',
    orange: 'rgba(255, 159, 64, 0.5)'
  };
  
  // Dữ liệu điểm 4 môn chính
  const mainSubjectScores = {
    labels: ['Toán', 'Lý', 'Hóa', 'Sinh'],
    datasets: [
      {
        label: 'Điểm quá trình',
        data: [8.5, 7.5, 8.0, 7.8],
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      },
      {
        label: 'Điểm giữa kỳ',
        data: [8.0, 8.5, 7.5, 8.2],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      },
      {
        label: 'Điểm cuối kỳ',
        data: [9.0, 8.0, 8.5, 7.5],
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      },
      {
        label: 'Điểm trung bình',
        data: [8.5, 8.0, 8.0, 7.8],
        backgroundColor: 'rgba(255, 206, 86, 0.5)',
        borderColor: 'rgba(255, 206, 86, 1)',
        borderWidth: 1,
        type: 'line',
        order: 0
      }
    ]
  };

  // Dữ liệu điểm chi tiết cho từng môn
  const detailedSubjectScores = {
    labels: [
      'Chuyên cần', 
      'Bài tập', 
      'Thực hành', 
      'Thuyết trình', 
      'Kiểm tra 15p', 
      'Kiểm tra 1 tiết',
      'Giữa kỳ',
      'Cuối kỳ'
    ],
    datasets: [
      {
        label: 'Toán',
        data: [9.0, 8.5, 8.0, 8.5, 9.0, 8.5, 8.0, 9.0],
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      },
      {
        label: 'Lý',
        data: [8.5, 8.0, 9.0, 8.0, 8.5, 8.0, 8.5, 8.0],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      },
      {
        label: 'Hóa',
        data: [8.0, 8.5, 8.5, 8.0, 7.5, 8.0, 7.5, 8.5],
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      },
      {
        label: 'Sinh',
        data: [8.5, 7.5, 8.0, 7.5, 8.0, 7.8, 8.2, 7.5],
        backgroundColor: 'rgba(255, 206, 86, 0.5)',
        borderColor: 'rgba(255, 206, 86, 1)',
        borderWidth: 1
      }
    ]
  };

  // Dữ liệu phân tích chi tiết từng môn
  const subjectAnalysis = {
    Toán: {
      labels: ['Đại số', 'Giải tích', 'Hình học', 'Thống kê'],
      data: [85, 78, 92, 88],
      color: 'rgba(255, 99, 132, 0.5)'
    },
    Lý: {
      labels: ['Cơ học', 'Nhiệt học', 'Điện từ', 'Quang học'],
      data: [75, 82, 88, 85],
      color: 'rgba(54, 162, 235, 0.5)'
    },
    Hóa: {
      labels: ['Vô cơ', 'Hữu cơ', 'Phân tích', 'Thực hành'],
      data: [80, 85, 75, 90],
      color: 'rgba(75, 192, 192, 0.5)'
    },
    Sinh: {
      labels: ['Di truyền', 'Sinh thái', 'Sinh lý', 'Thực hành'],
      data: [78, 85, 80, 88],
      color: 'rgba(255, 206, 86, 0.5)'
    }
  };

  // Dữ liệu so sánh với trung bình lớp
  const subjectComparison = {
    labels: ['Toán', 'Lý', 'Hóa', 'Sinh'],
    datasets: [
      {
        label: 'Điểm số của bạn',
        data: [8.5, 8.0, 8.0, 7.8],
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      },
      {
        label: 'Trung bình lớp',
        data: [7.5, 7.2, 7.8, 7.5],
        backgroundColor: 'rgba(153, 102, 255, 0.5)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 1
      }
    ]
  };

  // State cho kỹ năng môn học
  const [subjectSkills, setSubjectSkills] = useState(null);

  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        // 1. Lấy thông tin sinh viên từ Supabase
        const { data: studentData, error: studentError } = await supabase
          .from('students')
          .select('*')
          .eq('id', id)
          .single();

        if (studentError) throw studentError;
        setStudent(studentData);

        // 2. Lấy điểm chi tiết từ API
        const { data: scoresData, error: scoresError } = await supabase
          .from('student_scores')
          .select('*')
          .eq('student_id', id)
          .single();
        
        if (!scoresError && scoresData) {
          updateCourseScores(scoresData);
        }

        // 3. Lấy dữ liệu kỹ năng
        const { data: skillsData, error: skillsError } = await supabase
          .from('student_skills')
          .select('*')
          .eq('student_id', id)
          .single();

        if (!skillsError && skillsData) {
          updateSkillScores(skillsData);
        }

        // 4. Cập nhật xu hướng học tập
        setTrendData(generateTrendData());

      } catch (error) {
        console.error('Error fetching student data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStudentData();
  }, [id]);

  if (loading) return <div>Đang tải...</div>;
  if (!student) return <div>Không tìm thấy học sinh</div>;

  const scoreData = {
    labels: ['Điểm giữa kỳ', 'Điểm cuối kỳ', 'Điểm bài tập'],
    datasets: [
      {
        label: 'Điểm số',
        data: [student.midterm_score, student.final_score, student.homework_score],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(75, 192, 192, 0.5)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Biểu đồ điểm số tổng quan',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
      },
    },
  };

  const subjectOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Chi tiết điểm theo môn học',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        title: {
          display: true,
          text: 'Điểm'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Môn học'
        }
      }
    },
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Thông tin chi tiết học sinh</h1>
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">{student.name}</h2>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p><strong>MSSV:</strong> {student.student_id}</p>
            <p><strong>Lớp:</strong> {student.class}</p>
            <p><strong>Khoa:</strong> {student.Khoa}</p>
          </div>
          <div>
            <p><strong>Mức độ:</strong> {student.predicted_level}</p>
            <p><strong>Mức độ rủi ro:</strong> {student.risk_level}</p>
            <p><strong>Tỷ lệ điểm danh:</strong> {student.attendance_rate * 100}%</p>
          </div>
        </div>

        {/* Grid layout cho các biểu đồ */}
        <div className="space-y-6">
          {/* Biểu đồ điểm số 4 môn chính */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Điểm số 4 môn chính</h3>
            <Bar 
              data={mainSubjectScores} 
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Phân tích điểm số theo môn học'
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 10
                  }
                }
              }} 
            />
          </div>

          {/* Biểu đồ điểm chi tiết các môn */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Chi tiết điểm thành phần các môn</h3>
            <Bar
              data={detailedSubjectScores}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top'
                  },
                  title: {
                    display: true,
                    text: 'So sánh điểm thành phần giữa các môn'
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                      display: true,
                      text: 'Điểm'
                    }
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Thành phần điểm'
                    }
                  }
                }
              }}
            />
            <div className="mt-4 text-sm text-gray-600">
              <p className="text-center">Biểu đồ thể hiện chi tiết điểm thành phần của từng môn học, giúp so sánh hiệu quả học tập ở các khía cạnh khác nhau.</p>
            </div>
          </div>

          {/* Grid cho phân tích chi tiết từng môn */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(subjectAnalysis).map(([subject, data]) => (
              <div key={subject} className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Chi tiết môn {subject}</h3>
                <Bar
                  data={{
                    labels: data.labels,
                    datasets: [{
                      label: subject,
                      data: data.data,
                      backgroundColor: data.color,
                      borderColor: data.color.replace('0.5', '1'),
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        display: false
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100
                      }
                    }
                  }}
                />
              </div>
            ))}
          </div>

          {/* Grid cho phân tích kỹ năng từng môn */}
          {subjectSkills && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(subjectSkills).map(([subject, skills]) => {
                // Chuyển đổi dữ liệu kỹ năng thành format phù hợp cho biểu đồ radar
                const skillData = {
                  labels: Object.keys(skills),
                  datasets: [{
                    label: `Kỹ năng môn ${subject}`,
                    data: Object.values(skills),
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: true
                  }]
                };

                return (
                  <div key={subject} className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4">Phân tích kỹ năng môn {subject}</h3>
                    <div className="aspect-square">
                      <Radar
                        data={skillData}
                        options={{
                          responsive: true,
                          scales: {
                            r: {
                              beginAtZero: true,
                              max: 100,
                              ticks: {
                                stepSize: 20
                              },
                              pointLabels: {
                                font: {
                                  size: 10
                                }
                              }
                            }
                          },
                          plugins: {
                            legend: {
                              display: true,
                              position: 'top'
                            }
                          }
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
            </div>

            {/* Phân bổ thời gian học tập */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Phân bổ thời gian học tập (giờ/tuần)</h3>
              <div className="w-full md:w-3/4 mx-auto">
                <Doughnut
                  data={timeDistributionData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'right'
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${value} giờ`;
                          }
                        }
                      }
                    }
                  }}
                />
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-600 text-center">
                  Tổng số giờ học tập: {timeDistributionData.datasets[0].data.reduce((a, b) => a + b, 0)} giờ/tuần
                </p>
              </div>
            </div>

          {/* So sánh với trung bình lớp */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">So sánh với trung bình lớp</h3>
            <Bar
              data={subjectComparison}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top'
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 10
                  }
                }
              }}
            />
          </div>

          {/* Biểu đồ radar phân tích hiệu suất */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Phân tích hiệu suất</h3>
            <Radar
              data={radarData}
              options={{
                scales: {
                  r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                      stepSize: 20
                    }
                  }
                }
              }}
            />
          </div>

          {/* Biểu đồ điểm số các môn học */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Điểm số các môn học</h3>
            <Bar
              data={courseData}
              options={courseChartOptions}
            />
          </div>

          {/* Biểu đồ kỹ năng các môn học */}
          <div className="grid grid-cols-2 gap-4 mt-4">
            {/* Nhập môn lập trình */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Kỹ năng Nhập Môn Lập Trình</h3>
              <Bar
                data={nmltSkillData}
                options={skillChartOptions}
              />
            </div>

            {/* Kỹ thuật lập trình */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Kỹ năng Kỹ Thuật Lập Trình</h3>
              <Bar
                data={ktltSkillData}
                options={skillChartOptions}
              />
            </div>

            {/* CTDL và GT */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Kỹ năng Cấu Trúc Dữ Liệu & Giải Thuật</h3>
              <Bar
                data={ctdlSkillData}
                options={skillChartOptions}
              />
            </div>

            {/* OOP */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Kỹ năng Lập Trình Hướng Đối Tượng</h3>
              <Bar
                data={oopSkillData}
                options={skillChartOptions}
              />
            </div>
          </div>

          {/* Biểu đồ xu hướng */}
          <div className="bg-gray-50 p-4 rounded-lg mt-4">
            <h3 className="text-lg font-semibold mb-4">Xu hướng học tập</h3>
            <Line
              data={trendData}
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                      display: true,
                      text: 'Điểm số'
                    }
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Thời gian'
                    }
                  }
                },
                plugins: {
                  legend: {
                    position: 'top'
                  },
                  title: {
                    display: true,
                    text: 'Xu hướng theo thời gian'
                  }
                }
              }}
            />
          </div>

        {/* Bảng chi tiết điểm theo môn học */}
        <div className="mb-6">
          <h3 className="font-semibold mb-4">Bảng điểm chi tiết theo môn học</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="py-2 px-4 border-b">Môn học</th>
                  <th className="py-2 px-4 border-b">Điểm quá trình</th>
                  <th className="py-2 px-4 border-b">Điểm giữa kỳ</th>
                  <th className="py-2 px-4 border-b">Điểm cuối kỳ</th>
                  <th className="py-2 px-4 border-b">Điểm trung bình</th>
                </tr>
              </thead>
              <tbody>
                {mainSubjectScores.labels.map((subject, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                    <td className="py-2 px-4 border-b">{subject}</td>
                    <td className="py-2 px-4 border-b text-center">{mainSubjectScores.datasets[0].data[index]}</td>
                    <td className="py-2 px-4 border-b text-center">{mainSubjectScores.datasets[1].data[index]}</td>
                    <td className="py-2 px-4 border-b text-center">{mainSubjectScores.datasets[2].data[index]}</td>
                    <td className="py-2 px-4 border-b text-center">{mainSubjectScores.datasets[3].data[index]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Thông tin chi tiết khác */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="font-semibold mb-2">Hoạt động học tập</h3>
            <p><strong>Số giờ học/tuần:</strong> {student.study_hours_per_week}</p>
            <p><strong>Điểm tham gia:</strong> {student.participation_score}</p>
            <p><strong>Hoàn thành bài tập:</strong> {student.assignment_completion * 100}%</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Hoạt động trực tuyến</h3>
            <p><strong>Giờ sử dụng LMS:</strong> {student.lms_usage_hours}</p>
            <p><strong>Số lần nộp muộn:</strong> {student.late_submissions}</p>
            <p><strong>Điểm hành vi:</strong> {student.behCTior_score_100}/100</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDetail;
