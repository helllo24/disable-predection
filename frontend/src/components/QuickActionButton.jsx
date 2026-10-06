import React from 'react';

const QuickActionButton = ({ label, icon: Icon, onClick, isComingSoon = true }) => {
  return (
    <button
      onClick={isComingSoon ? undefined : onClick}
      className={`card ${isComingSoon ? 'disabled' : ''}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '1rem 1.25rem',
        cursor: isComingSoon ? 'not-allowed' : 'pointer',
        opacity: isComingSoon ? 0.65 : 1,
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        textAlign: 'left',
        width: '100%',
        transition: 'all 0.2s ease',
      }}
      disabled={isComingSoon}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {Icon && (
          <div style={{ color: isComingSoon ? 'var(--text-muted)' : 'var(--primary-500)' }}>
            <Icon size={20} />
          </div>
        )}
        <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>
          {label}
        </span>
      </div>

      {isComingSoon && (
        <span
          className="badge"
          style={{
            fontSize: '0.7rem',
            backgroundColor: 'rgba(148, 163, 184, 0.1)',
            color: 'var(--text-muted)',
            border: '1px solid var(--border-color)',
          }}
        >
          Coming Soon
        </span>
      )}
    </button>
  );
};

export default QuickActionButton;
