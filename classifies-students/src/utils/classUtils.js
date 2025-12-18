// Normalize and format class codes (e.g., "23ct111" -> "23CT111")
export const normalizeClassCode = (code) => {
  if (!code) return code;
  return code.trim().toUpperCase().replace(/\s+/g, '');
};

// Get batch/year from class code (e.g., "23CT111" -> "23")
export const getBatchFromClassCode = (code) => {
  if (!code) return null;
  const match = code.match(/^(\d{2})/);
  return match ? match[1] : null;
};

// Get base class code (e.g., "23CT111" -> "23CT11")
export const getBaseClassCode = (code) => {
  if (!code) return null;
  const normalized = normalizeClassCode(code);
  const match = normalized.match(/^(\d{2}CT\d{2})/);
  return match ? match[1] : null;
};

// Group students by batch year
export const groupStudentsByBatch = (students) => {
  const groups = {};
  students.forEach(student => {
    const batch = getBatchFromClassCode(student.class);
    if (batch) {
      if (!groups[batch]) {
        groups[batch] = [];
      }
      groups[batch].push(student);
    }
  });
  return groups;
};

// Sort class codes properly
export const sortClassCodes = (codes) => {
  return [...codes].sort((a, b) => {
    const normalizedA = normalizeClassCode(a);
    const normalizedB = normalizeClassCode(b);
    return normalizedA.localeCompare(normalizedB);
  });
};