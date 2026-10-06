import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getHealthStatus } from '../services/api';
import { Activity, LogOut, User as UserIcon } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const checkServer = async () => {
      try {
        const res = await getHealthStatus();
        if (isMounted) {
          setBackendHealthy(res && res.status === 'healthy');
        }
      } catch (err) {
        if (isMounted) {
          setBackendHealthy(false);
        }
      } finally {
        if (isMounted) setChecking(false);
      }
    };

    checkServer();
    const interval = setInterval(checkServer, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="navbar">
      <div className="navbar-brand" style={{ cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
        <Activity style={{ color: 'var(--primary-500)' }} size={24} />
        <span style={{ fontWeight: 700 }}>Diabetes Prediction Using Machine Learning</span>
      </div>

      <div className="navbar-status">
        {/* Backend Health Status Badge */}
        <span className={`badge ${backendHealthy ? 'badge-connected' : 'badge-disconnected'}`}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: backendHealthy ? 'var(--accent-green)' : 'var(--accent-red)',
              display: 'inline-block',
            }}
          />
          Backend Status: {checking ? 'Checking...' : backendHealthy ? 'Connected' : 'Disconnected'}
        </span>

        {/* User Info & Profile Direct Link */}
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                fontSize: '0.9rem',
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                cursor: 'pointer',
                padding: '0.25rem 0.5rem',
                borderRadius: 'var(--radius-sm)',
                transition: 'background 0.2s'
              }}
              onClick={() => navigate('/profile')}
              title="Click to view/edit profile"
            >
              <UserIcon size={16} />
              <strong style={{ color: 'var(--text-main)' }}>{user.full_name}</strong>
              <span className="badge badge-patient">{user.role}</span>
            </div>

            <button className="btn btn-danger" style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem' }} onClick={logout}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
