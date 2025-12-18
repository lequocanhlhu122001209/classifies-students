// Utilities for normalizing and displaying student "level" values

export function canonicalizeLevel(v) {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  if (!s) return null;
  // remove diacritics and non-alphanumerics, lowercase
  const noDiac = s.normalize && s.normalize('NFD')
    ? s.normalize('NFD').replace(/\p{Diacritic}/gu, '')
    : s;
  const key = noDiac.toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!key) return null;
  if (key.includes('xuatsac') || key.includes('gioi') || key === 'xuat') return 'Xuat sac';
  if (key.includes('kha')) return 'Kha';
  if (key.includes('trungbinh') || key === 'trung' || key.includes('trung')) return 'Trung binh';
  if (key.includes('yeu') || key.includes('kem')) return 'Yeu';
  // last resort: match English-like words
  if (key.includes('excellent') || key.includes('distinction')) return 'Xuat sac';
  if (key.includes('good')) return 'Kha';
  if (key.includes('average') || key.includes('medium') || key.includes('mid')) return 'Trung binh';
  if (key.includes('weak') || key.includes('poor')) return 'Yeu';
  return null;
}

export function displayLabel(levelKey) {
  if (!levelKey) return '';
  return levelKey === 'Xuat sac' ? 'Xuất sắc'
    : levelKey === 'Kha' ? 'Khá'
    : levelKey === 'Trung binh' ? 'Trung bình'
    : levelKey === 'Yeu' ? 'Yếu'
    : String(levelKey);
}

export function getLevelColor(levelKey) {
  switch (levelKey) {
    case 'Xuat sac': return '#10B981';
    case 'Kha': return '#3B82F6';
    case 'Trung binh': return '#F59E0B';
    case 'Yeu': return '#EF4444';
    default: return 'inherit';
  }
}
