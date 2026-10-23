import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getHealthStatus } from '../services/api';
import { Activity, LogOut, User as UserIcon, Shield, Layers, Home, Sparkles, LineChart } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const checkServer = async () => {
      try {
        const res = await getHealthStatus();
        if (isMounted) setBackendHealthy(res && (res.status === 'healthy' || res.message));
      } catch (err) {
        // Retry once after 1 second before marking disconnected
        setTimeout(async () => {
          if (!isMounted) return;
          try {
            const retryRes = await getHealthStatus();
            if (isMounted) setBackendHealthy(retryRes && (retryRes.status === 'healthy' || retryRes.message));
          } catch (retryErr) {
            if (isMounted) setBackendHealthy(false);
          }
        }, 1000);
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

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-slate-900 text-white border-b border-slate-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-6">
          <div 
            className="flex items-center gap-2.5 cursor-pointer group"
            onClick={() => navigate('/dashboard')}
          >
            <div className="p-2 bg-blue-600 rounded-xl group-hover:bg-blue-500 transition-colors shadow-lg shadow-blue-500/30">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-tight text-white">
                  AI Health <span className="text-blue-400">Intelligence</span>
                </span>
                <span className="badge-pill bg-blue-500/20 text-blue-300 border border-blue-400/30 text-[10px] px-2 py-0.5">
                  RESEARCH v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Diabetes Risk Prediction & Explainable AI System</p>
            </div>
          </div>

          {/* Nav Quick Links */}
          <nav className="hidden md:flex items-center gap-1 ml-4 border-l border-slate-800 pl-4">
            <button
              onClick={() => navigate('/home')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive('/home') ? 'bg-blue-600/20 text-blue-400 font-semibold' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Home className="w-3.5 h-3.5" />
              Home
            </button>

            <button
              onClick={() => navigate('/dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive('/dashboard') ? 'bg-blue-600/20 text-blue-400 font-semibold' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Dashboard
            </button>

            <button
              onClick={() => navigate('/diabetes-prediction')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive('/diabetes-prediction') ? 'bg-blue-600 text-white font-semibold shadow-sm' : 'text-blue-400 hover:bg-slate-800'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              Risk Assessment
            </button>

            <button
              onClick={() => navigate('/research')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive('/research') ? 'bg-blue-600/20 text-blue-400 font-semibold' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <LineChart className="w-3.5 h-3.5" />
              Research & Model
            </button>
          </nav>
        </div>

        {/* Right Status & Profile Controls */}
        <div className="flex items-center gap-4">
          {/* Backend Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 text-xs bg-slate-800/80 border border-slate-700/80 px-2.5 py-1 rounded-full">
            <span className={`w-2 h-2 rounded-full ${backendHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-slate-300">
              {checking ? 'Checking server...' : backendHealthy ? 'API Connected' : 'Server Disconnected'}
            </span>
          </div>

          {/* User Controls */}
          {user ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate('/profile')}
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors border border-slate-700"
                title="View User Profile"
              >
                <UserIcon className="w-3.5 h-3.5 text-blue-400" />
                <span className="hidden lg:inline">{user.full_name || 'User'}</span>
              </button>

              <button
                onClick={logout}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 text-xs font-semibold border border-red-500/30 transition-colors"
                title="Logout"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition-colors"
            >
              Sign In
            </button>
          )}
        </div>

      </div>
    </header>
  );
};

export default Navbar;
