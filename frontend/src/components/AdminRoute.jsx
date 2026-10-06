import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { ShieldAlert } from 'lucide-react';

const AdminRoute = () => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="layout-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Verifying administrative security credentials...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== 'ADMIN') {
    return (
      <div className="layout-container">
        <Sidebar />
        <div className="main-wrapper">
          <Navbar />
          <main className="main-content">
            <div className="card" style={{ textAlign: 'center', padding: '4rem 1rem', maxWidth: 600, margin: '2rem auto' }}>
              <ShieldAlert size={56} style={{ color: 'var(--accent-red)', margin: '0 auto 1rem' }} />
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                403 Forbidden — Admin Access Required
              </h1>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                Your patient account does not have permission to view administrative controls.
              </p>
              <button className="btn btn-primary" onClick={() => window.location.href = '/dashboard'}>
                Return to Patient Dashboard
              </button>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="layout-container">
      <Sidebar />
      <div className="main-wrapper">
        <Navbar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminRoute;
