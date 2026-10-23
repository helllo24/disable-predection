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
        backgroundColor: '#f8fafc',
        borderColor: '#cbd5e1',
        borderStyle: 'dashed',
      }}
    >
      {Icon && (
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            backgroundColor: '#e0f2fe',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#0284c7',
            marginBottom: '0.75rem',
          }}
        >
          <Icon size={24} />
        </div>
      )}
      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#0f172a', marginBottom: '0.25rem' }}>
        {title}
      </h4>
      <p style={{ fontSize: '0.85rem', color: '#64748b', maxWidth: 360 }}>
        {message}
      </p>
    </div>
  );
};

export default EmptyStateCard;
