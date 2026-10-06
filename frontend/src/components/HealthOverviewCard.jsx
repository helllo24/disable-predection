import React from 'react';

const HealthOverviewCard = ({ title, value, status, icon: Icon, badgeText = "Not available yet" }) => {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {Icon && (
            <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
              <Icon size={20} />
            </div>
          )}
          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>{title}</span>
        </div>

        <span className="badge" style={{ backgroundColor: 'rgba(148, 163, 184, 0.1)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
          {badgeText}
        </span>
      </div>

      <div style={{ marginTop: '0.25rem' }}>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-muted)' }}>
          {value || "Not available yet"}
        </div>
        {status && (
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {status}
          </p>
        )}
      </div>
    </div>
  );
};

export default HealthOverviewCard;
