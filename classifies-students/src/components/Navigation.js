import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: '📊 Dashboard', icon: '📊' },
    { path: '/students', label: '👥 Quản lý sinh viên', icon: '👥' },
    { path: '/add-student', label: '➕ Thêm sinh viên', icon: '➕' }
  ];

  return (
    <nav style={{
      background: 'rgba(255,255,255,0.05)',
      padding: '16px 20px',
      marginBottom: '20px',
      borderRadius: '8px',
      border: '1px solid rgba(255,255,255,0.1)'
    }}>
      <div style={{
        display: 'flex',
        gap: '20px',
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              padding: '10px 16px',
              borderRadius: '6px',
              textDecoration: 'none',
              color: location.pathname === item.path ? '#10B981' : '#e6eef8',
              background: location.pathname === item.path ? 'rgba(16,185,129,0.1)' : 'transparent',
              border: location.pathname === item.path ? '1px solid #10B981' : '1px solid transparent',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
