import React, { useState, useEffect } from 'react';
import {
  getAdminDashboardStats,
  getAdminPatients,
  togglePatientStatus,
  getAdminPredictions,
  getAdminAppointments
} from '../services/api';
import {
  ShieldCheck,
  Users,
  Activity,
  Stethoscope,
  Scale,
  Calendar,
  Pill,
  Search,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ToggleLeft,
  ToggleRight,
  TrendingUp
} from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('patients'); // 'patients', 'predictions', 'appointments'
  const [stats, setStats] = useState(null);
  const [patients, setPatients] = useState([]);
  const [predictionsData, setPredictionsData] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState('');

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [statsRes, patList, predRes, apptList] = await Promise.all([
        getAdminDashboardStats(),
        getAdminPatients(searchQuery),
        getAdminPredictions(),
        getAdminAppointments(),
      ]);
      setStats(statsRes);
      setPatients(patList || []);
      setPredictionsData(predRes);
      setAppointments(apptList || []);
    } catch (err) {
      console.error('Failed to load admin data:', err);
      setError(err.message || 'Failed to load administrative data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, [searchQuery]);

  const handleToggleStatus = async (patient) => {
    try {
      const res = await togglePatientStatus(patient.id);
      setActionMessage(res.message);
      await loadAdminData();
    } catch (err) {
      setError(err.message || 'Failed to update patient status.');
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Admin Header */}
      <div className="card" style={{ marginBottom: '1.5rem', background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9))' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-red)',
              }}
            >
              <ShieldCheck size={30} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                <span className="badge badge-admin">ADMINISTRATOR</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Role-Based Access Control Active</span>
              </div>
              <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)' }}>
                System Administration Console
              </h1>
            </div>
          </div>

          <PageGuideModal
            title="Administrator Control & Analytics Center"
            purpose="Provides system administrators with aggregate usage metrics, patient management, role-based access controls (RBAC), and diagnostic activity monitoring."
            howItWorks={[
              "Restricted to users with ADMIN role via JWT authentication middleware.",
              "Aggregates platform statistics: total registered patients, total diabetes predictions run, disease assessments, and doctor appointments.",
              "Allows toggling patient account status (Active/Suspended) and managing user permissions."
            ]}
            howToUse={[
              "Monitor real-time system metrics in the top statistics cards.",
              "Browse registered patient list and search by name or email.",
              "Toggle patient account status or perform administrative management actions."
            ]}
          />
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {actionMessage && (
        <div className="alert alert-success">
          <CheckCircle2 size={18} />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Real Statistics Overview Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem',
        }}
      >
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
            <Users size={16} style={{ color: 'var(--primary-500)' }} />
            <span>Total Patients</span>
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            {stats ? stats.total_patients : '-'}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
            <Activity size={16} style={{ color: 'var(--accent-amber)' }} />
            <span>Diabetes ML Tests</span>
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            {stats ? stats.total_diabetes_predictions : '-'}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
            <Stethoscope size={16} style={{ color: 'var(--primary-500)' }} />
            <span>Disease ML Tests</span>
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            {stats ? stats.total_disease_predictions : '-'}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
            <Scale size={16} style={{ color: 'var(--accent-green)' }} />
            <span>BMI Calculations</span>
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            {stats ? stats.total_bmi_records : '-'}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
            <Calendar size={16} style={{ color: 'var(--primary-500)' }} />
            <span>Appointments</span>
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            {stats ? stats.total_appointments : '-'}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
            <Pill size={16} style={{ color: 'var(--accent-red)' }} />
            <span>Active Medicines</span>
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            {stats ? stats.active_medicine_reminders : '-'}
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        <button
          className={`btn ${activeTab === 'patients' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('patients')}
          style={{ fontSize: '0.875rem', padding: '0.45rem 1.15rem' }}
        >
          Patient Accounts ({patients.length})
        </button>

        <button
          className={`btn ${activeTab === 'predictions' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('predictions')}
          style={{ fontSize: '0.875rem', padding: '0.45rem 1.15rem' }}
        >
          Prediction Activity Logs
        </button>

        <button
          className={`btn ${activeTab === 'appointments' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('appointments')}
          style={{ fontSize: '0.875rem', padding: '0.45rem 1.15rem' }}
        >
          System Appointments ({appointments.length})
        </button>
      </div>

      {/* TAB 1: Patients Directory */}
      {activeTab === 'patients' && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Registered Patients Management
            </h2>

            <div style={{ position: 'relative', minWidth: 260 }}>
              <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-muted)' }} />
              <input
                type="text"
                className="form-input"
                style={{ paddingLeft: '2.3rem', fontSize: '0.85rem' }}
                placeholder="Search patient name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {loading ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Loading patient accounts...</p>
          ) : patients.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No patients found.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>ID</th>
                    <th style={{ padding: '0.75rem' }}>Patient Name</th>
                    <th style={{ padding: '0.75rem' }}>Email</th>
                    <th style={{ padding: '0.75rem' }}>Phone</th>
                    <th style={{ padding: '0.75rem' }}>Age/Gender</th>
                    <th style={{ padding: '0.75rem' }}>Status</th>
                    <th style={{ padding: '0.75rem', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((p) => (
                    <tr key={p.id} style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)' }}>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>#{p.id}</td>
                      <td style={{ padding: '0.75rem', fontWeight: 600, color: 'var(--text-main)' }}>{p.full_name}</td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{p.email}</td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{p.phone}</td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{p.age} yrs, {p.gender}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: p.is_active ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                            color: p.is_active ? '#10b981' : 'var(--accent-red)',
                            border: `1px solid ${p.is_active ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                          }}
                        >
                          {p.is_active ? 'Active' : 'Deactivated'}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '0.3rem 0.65rem', fontSize: '0.775rem' }}
                          onClick={() => handleToggleStatus(p)}
                        >
                          {p.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Prediction Activity Logs */}
      {activeTab === 'predictions' && predictionsData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
              Recent Disease Risk Predictions
            </h3>
            {predictionsData.recent_disease_predictions.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No disease predictions logged.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.65rem' }}>Date</th>
                      <th style={{ padding: '0.65rem' }}>Patient</th>
                      <th style={{ padding: '0.65rem' }}>Predicted Disease</th>
                      <th style={{ padding: '0.65rem' }}>Confidence</th>
                      <th style={{ padding: '0.65rem' }}>Model</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictionsData.recent_disease_predictions.map((ds) => (
                      <tr key={`ad-dis-${ds.id}`} style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)' }}>
                        <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{new Date(ds.created_at).toLocaleString()}</td>
                        <td style={{ padding: '0.65rem', fontWeight: 600 }}>{ds.patient_name} ({ds.patient_email})</td>
                        <td style={{ padding: '0.65rem', color: 'var(--primary-500)', fontWeight: 700 }}>{ds.predicted_disease}</td>
                        <td style={{ padding: '0.65rem' }}>{(ds.probability * 100).toFixed(0)}%</td>
                        <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{ds.model}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="card">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
              Recent Diabetes Risk Predictions
            </h3>
            {predictionsData.recent_diabetes_predictions.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No diabetes predictions logged.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.65rem' }}>Date</th>
                      <th style={{ padding: '0.65rem' }}>Patient</th>
                      <th style={{ padding: '0.65rem' }}>Risk Outcome</th>
                      <th style={{ padding: '0.65rem' }}>Probability</th>
                      <th style={{ padding: '0.65rem' }}>Glucose / BMI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictionsData.recent_diabetes_predictions.map((db) => (
                      <tr key={`ad-diab-${db.id}`} style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)' }}>
                        <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{new Date(db.created_at).toLocaleString()}</td>
                        <td style={{ padding: '0.65rem', fontWeight: 600 }}>{db.patient_name} ({db.patient_email})</td>
                        <td style={{ padding: '0.65rem', fontWeight: 700, color: db.risk.includes('High') ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                          {db.risk}
                        </td>
                        <td style={{ padding: '0.65rem' }}>{(db.probability * 100).toFixed(0)}%</td>
                        <td style={{ padding: '0.65rem', color: 'var(--text-muted)' }}>{db.glucose} mg/dL / {db.bmi} BMI</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: System Appointments */}
      {activeTab === 'appointments' && (
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1.25rem' }}>
            System-Wide Appointments Overview
          </h2>

          {appointments.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No system appointments found.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>Date & Time</th>
                    <th style={{ padding: '0.75rem' }}>Patient Name</th>
                    <th style={{ padding: '0.75rem' }}>Doctor Name</th>
                    <th style={{ padding: '0.75rem' }}>Specialization</th>
                    <th style={{ padding: '0.75rem' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((a) => (
                    <tr key={`ad-appt-${a.id}`} style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)' }}>
                      <td style={{ padding: '0.75rem', color: 'var(--primary-500)', fontWeight: 600 }}>
                        {a.appointment_date} at {a.appointment_time}
                      </td>
                      <td style={{ padding: '0.75rem', fontWeight: 600, color: 'var(--text-main)' }}>
                        {a.patient_name} ({a.patient_email})
                      </td>
                      <td style={{ padding: '0.75rem', fontWeight: 500 }}>{a.doctor_name}</td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{a.specialization}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: a.status === 'Scheduled' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                            color: a.status === 'Scheduled' ? '#10b981' : 'var(--text-muted)',
                            border: `1px solid ${a.status === 'Scheduled' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(148, 163, 184, 0.3)'}`,
                          }}
                        >
                          {a.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
