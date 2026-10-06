import React from 'react';
import { NavLink } from 'react-router-dom';
import { HeartPulse, LayoutDashboard, Scale, Activity, Stethoscope, TrendingUp, Utensils, Dumbbell, Pill, Calendar, User, LogIn, UserPlus, ShieldCheck, Heart, Layers } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Sidebar = () => {
  const { user, isAuthenticated } = useAuth();
  const isAdmin = user?.role === 'ADMIN';

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <HeartPulse size={28} />
          <span>Diabetes AI</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {isAuthenticated ? (
          <>
            {isAdmin && (
              <NavLink
                to="/admin"
                className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                style={{ backgroundColor: 'rgba(239, 68, 68, 0.12)', color: 'var(--accent-red)' }}
              >
                <ShieldCheck size={20} />
                <span>Admin Console</span>
              </NavLink>
            )}

            <NavLink
              to="/dashboard"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <LayoutDashboard size={20} />
              <span>Dashboard</span>
            </NavLink>

            <NavLink
              to="/research"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              style={{ backgroundColor: 'rgba(37, 99, 235, 0.08)', color: 'var(--primary-600)' }}
            >
              <Layers size={20} />
              <span>External Validation & Fairness</span>
            </NavLink>

            <NavLink
              to="/health-risk"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <TrendingUp size={20} />
              <span>Health Risk Score</span>
            </NavLink>

            <NavLink
              to="/appointments"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Calendar size={20} />
              <span>Appointments</span>
            </NavLink>

            <NavLink
              to="/diet"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Utensils size={20} />
              <span>Diet Guidance</span>
            </NavLink>

            <NavLink
              to="/exercise"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Dumbbell size={20} />
              <span>Exercise Plan</span>
            </NavLink>

            <NavLink
              to="/medicines"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Pill size={20} />
              <span>Medicine Reminders</span>
            </NavLink>

            <NavLink
              to="/bmi"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Scale size={20} />
              <span>BMI Calculator</span>
            </NavLink>

            <NavLink
              to="/diabetes-prediction"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Activity size={20} />
              <span>Diabetes Assessment</span>
            </NavLink>

            <NavLink
              to="/diabetes-complications"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Heart size={20} />
              <span>Complication Risk</span>
            </NavLink>

            <NavLink
              to="/disease-prediction"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Stethoscope size={20} />
              <span>Disease Prediction</span>
            </NavLink>

            <NavLink
              to="/profile"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <User size={20} />
              <span>Patient Profile</span>
            </NavLink>
          </>
        ) : (
          <>
            <NavLink
              to="/login"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <LogIn size={20} />
              <span>Login</span>
            </NavLink>
            <NavLink
              to="/register"
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <UserPlus size={20} />
              <span>Register</span>
            </NavLink>
          </>
        )}
      </nav>

      <div className="sidebar-footer">
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          AI Smart Healthcare v1.0
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
