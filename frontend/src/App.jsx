import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import BMI from './pages/BMI';
import DiabetesPrediction from './pages/DiabetesPrediction';
import DiabetesComplication from './pages/DiabetesComplication';
import DiseasePrediction from './pages/DiseasePrediction';
import HealthRisk from './pages/HealthRisk';
import DietRecommendation from './pages/DietRecommendation';
import ExerciseRecommendation from './pages/ExerciseRecommendation';
import MedicineReminders from './pages/MedicineReminders';
import DoctorAppointments from './pages/DoctorAppointments';
import AdminDashboard from './pages/AdminDashboard';
import ResearchValidation from './pages/ResearchValidation';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Patient Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/research" element={<ResearchValidation />} />
            <Route path="/health-risk" element={<HealthRisk />} />
            <Route path="/appointments" element={<DoctorAppointments />} />
            <Route path="/diet" element={<DietRecommendation />} />
            <Route path="/exercise" element={<ExerciseRecommendation />} />
            <Route path="/medicines" element={<MedicineReminders />} />
            <Route path="/bmi" element={<BMI />} />
            <Route path="/diabetes-prediction" element={<DiabetesPrediction />} />
            <Route path="/diabetes-complications" element={<DiabetesComplication />} />
            <Route path="/disease-prediction" element={<DiseasePrediction />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Route>

          {/* Admin Protected Routes */}
          <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminDashboard />} />
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
