import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

const levelConfig = [
  { key: 'Xuat sac', label: 'Xuất sắc', color: '#10B981' },
  { key: 'Kha', label: 'Khá', color: '#3B82F6' },
  { key: 'Trung binh', label: 'Trung bình', color: '#F59E0B' },
  { key: 'Yeu', label: 'Yếu', color: '#EF4444' }
];

function canonicalizeLevel(v) {
  if (!v && v !== 0) return null;
  const s = String(v).normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!s) return null;
  if (s === 'xuatsac' || s === 'gioi' || s === 'xuat') return 'Xuat sac';
  if (s === 'kha') return 'Kha';
  if (s === 'trungbinh' || s === 'trung' || s === 'trungbin') return 'Trung binh';
  if (s === 'yeu' || s === 'kem') return 'Yeu';
  return null;
}

export default function LevelCards({ students = [], onLevelFilter = () => {}, currentFilter = '' }) {
  const navigate = useNavigate();

  const counts = useMemo(() => {
    const map = { 'Xuat sac': 0, 'Kha': 0, 'Trung binh': 0, 'Yeu': 0 };
    for (const s of students) {
      const raw = s.level_key ?? s.level_prediction ?? s.predicted_level ?? s.level ?? s.level_pred ?? '';
      const key = canonicalizeLevel(raw) || raw;
      if (map[key] !== undefined) map[key]++;
    }
    return map;
  }, [students]);

  const handleClick = (key) => {
    try {
      onLevelFilter(currentFilter === key ? '' : key);
      if (currentFilter === key) navigate('/students');
      else navigate(`/students?level=${encodeURIComponent(key)}`);
    } catch (e) {
      console.warn('LevelCards click error', e);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20, marginBottom: 20 }}>
      {levelConfig.map(cfg => (
        <div
          key={cfg.key}
          onClick={() => handleClick(cfg.key)}
          role="button"
          tabIndex={0}
          style={{
            cursor: 'pointer',
            background: 'linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02))',
            borderRadius: 12,
            padding: 18,
            boxShadow: '0 6px 18px rgba(2,6,23,0.6)',
            position: 'relative',
            overflow: 'hidden',
            border: currentFilter === cfg.key ? `2px solid ${cfg.color}` : '1px solid rgba(255,255,255,0.06)'
          }}
        >
          <div style={{ height: 6, background: cfg.color, borderRadius: 6, position: 'absolute', top: 8, left: 16, right: 16 }} />
          <div style={{ paddingTop: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 16, color: '#93c5fd', fontWeight: 600 }}>{cfg.label}</div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', marginTop: 6 }}>Sinh viên</div>
            </div>
            <div style={{ fontSize: 40, fontWeight: 800, color: cfg.color }}>{counts[cfg.key] || 0}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
