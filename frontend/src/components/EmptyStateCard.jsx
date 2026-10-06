import React from 'react';

const EmptyStateCard = ({ title, message, icon: Icon }) => {
  return (
    <div
      className="card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2.5rem 1.5rem',
        textAlign: 'center',
        background: 'rgba(19, 28, 46, 0.5)',
        borderStyle: 'dashed',
      }}
    >
      {Icon && (
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            backgroundColor: 'rgba(30, 45, 74, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            marginBottom: '0.75rem',
          }}
        >
          <Icon size={24} />
        </div>
      )}
      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
        {title}
      </h4>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: 360 }}>
        {message}
      </p>
    </div>
  );
};

export default EmptyStateCard;
