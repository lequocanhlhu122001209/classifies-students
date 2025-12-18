// Validate class code format (e.g., 22CT111, 23CT112)
export const validateClassCode = (classCode) => {
  const pattern = /^(20|21|22|23|24|25)\s*CT\s*\d{2,3}$/i;
  if (!pattern.test(classCode.trim())) {
    return {
      isValid: false,
      error: 'Mã lớp không hợp lệ. Mã lớp phải có định dạng như: 22CT111, 23CT112, etc.'
    };
  }
  return {
    isValid: true,
    normalizedCode: classCode.trim().toUpperCase().replace(/\s+/g, '') // Chuẩn hóa mã lớp
  };
};

// Validate student ID format
export const validateStudentId = (studentId) => {
  if (!studentId || typeof studentId !== 'string') {
    return {
      isValid: false,
      error: 'Mã sinh viên không được để trống'
    };
  }
  return {
    isValid: true,
    normalizedId: studentId.trim().toUpperCase()
  };
};

// Validate numeric score in range 0-100
export const validateScore = (score) => {
  const numScore = parseFloat(score);
  if (isNaN(numScore) || numScore < 0 || numScore > 100) {
    return {
      isValid: false,
      error: 'Điểm phải là số từ 0 đến 100'
    };
  }
  return {
    isValid: true,
    normalizedScore: numScore
  };
};