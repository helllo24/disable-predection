import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  LineChart,
  ShieldCheck,
  Heart,
  Stethoscope,
  TrendingUp,
  Utensils,
  Dumbbell,
  Pill,
  Calendar,
  User,
  LogIn,
  UserPlus,
  Home,
  Sparkles,
  Scale
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Sidebar = () => {
  const { user, isAuthenticated } = useAuth();
  const isAdmin = user?.role === 'ADMIN';

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
      isActive
        ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
    }`;

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between flex-shrink-0 min-h-screen">
      <div className="p-4 space-y-6">
        
        {/* Navigation Categories */}
        <div className="space-y-4">
          
          {/* Main ML Pipeline Category */}
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-3 block mb-2">
              AI ML Research Core
            </span>
            <div className="space-y-1">
              <NavLink to="/home" className={linkClass}>
                <Home className="w-4 h-4 text-blue-500" />
                <span>Home Showcase</span>
              </NavLink>

              <NavLink to="/dashboard" className={linkClass}>
                <LayoutDashboard className="w-4 h-4 text-blue-500" />
                <span>Dashboard</span>
              </NavLink>

              <NavLink to="/diabetes-prediction" className={linkClass}>
                <Sparkles className="w-4 h-4 text-amber-500" />
                <div className="flex items-center justify-between w-full">
                  <span>Diabetes Risk ML</span>
                  <span className="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.5 rounded font-bold">
                    Primary
                  </span>
                </div>
              </NavLink>

              <NavLink to="/research" className={linkClass}>
                <LineChart className="w-4 h-4 text-teal-500" />
                <span>Research & Model</span>
              </NavLink>
            </div>
          </div>

          {/* Patient Health Services */}
          {isAuthenticated && (
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-3 block mb-2">
                Patient Clinical Services
              </span>
              <div className="space-y-1">
                <NavLink to="/diabetes-complications" className={linkClass}>
                  <Heart className="w-4 h-4 text-rose-500" />
                  <span>Complication Risks</span>
                </NavLink>

                <NavLink to="/disease-prediction" className={linkClass}>
                  <Stethoscope className="w-4 h-4 text-indigo-500" />
                  <span>Disease Symptom ML</span>
                </NavLink>

                <NavLink to="/health-risk" className={linkClass}>
                  <TrendingUp className="w-4 h-4 text-emerald-500" />
                  <span>Health Risk Score</span>
                </NavLink>

                <NavLink to="/diet" className={linkClass}>
                  <Utensils className="w-4 h-4 text-orange-500" />
                  <span>Diet Guidance</span>
                </NavLink>

                <NavLink to="/exercise" className={linkClass}>
                  <Dumbbell className="w-4 h-4 text-sky-500" />
                  <span>Exercise Plan</span>
                </NavLink>

                <NavLink to="/medicines" className={linkClass}>
                  <Pill className="w-4 h-4 text-purple-500" />
                  <span>Medicine Reminders</span>
                </NavLink>

                <NavLink to="/bmi" className={linkClass}>
                  <Scale className="w-4 h-4 text-slate-500" />
                  <span>BMI Calculator</span>
                </NavLink>
              </div>
            </div>
          )}

          {/* Admin Section */}
          {isAdmin && (
            <div>
              <span className="text-[10px] font-bold text-red-500 uppercase tracking-wider px-3 block mb-2">
                Administration
              </span>
              <NavLink to="/admin" className={linkClass}>
                <ShieldCheck className="w-4 h-4 text-red-500" />
                <span>Admin Console</span>
              </NavLink>
            </div>
          )}

        </div>
      </div>

      {/* Footer / Account */}
      <div className="p-4 border-t border-slate-100 bg-slate-50">
        {isAuthenticated ? (
          <NavLink to="/profile" className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-200 transition-colors">
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="overflow-hidden text-ellipsis whitespace-nowrap">
              <p className="text-xs font-bold text-slate-800">{user?.full_name || 'Patient'}</p>
              <p className="text-[10px] text-slate-500 uppercase">{user?.role || 'User'}</p>
            </div>
          </NavLink>
        ) : (
          <div className="space-y-1">
            <NavLink to="/login" className={linkClass}>
              <LogIn className="w-4 h-4" />
              <span>Login</span>
            </NavLink>
            <NavLink to="/register" className={linkClass}>
              <UserPlus className="w-4 h-4" />
              <span>Register</span>
            </NavLink>
          </div>
        )}
        <p className="text-[10px] text-slate-400 text-center mt-3">
          AI Risk Intelligence v2.0
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
