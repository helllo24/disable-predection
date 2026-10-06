import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import {
  getLatestBMI,
  getLatestDiabetesPrediction,
  getLatestDiseasePrediction,
  getLatestHealthRisk,
  getTodayMedicineReminders,
  getNextUpcomingAppointment,
  getUserAppointments,
  downloadHealthReportPDF
} from '../services/api';
import HealthOverviewCard from '../components/HealthOverviewCard';
import QuickActionButton from '../components/QuickActionButton';
import EmptyStateCard from '../components/EmptyStateCard';
import PageGuideModal from '../components/PageGuideModal';
import {
  Activity,
  HeartPulse,
  ShieldCheck,
  Scale,
  Stethoscope,
  Utensils,
  Dumbbell,
  Pill,
  Calendar,
  FileText,
  AlertCircle,
  TrendingUp,
  ExternalLink,
  ArrowRight,
  Download
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [latestBMI, setLatestBMI] = useState(null);
  const [loadingBMI, setLoadingBMI] = useState(true);

  const [latestDiabetes, setLatestDiabetes] = useState(null);
  const [loadingDiabetes, setLoadingDiabetes] = useState(true);

  const [latestDisease, setLatestDisease] = useState(null);
  const [loadingDisease, setLoadingDisease] = useState(true);

  const [latestRisk, setLatestRisk] = useState(null);
  const [loadingRisk, setLoadingRisk] = useState(true);

  const [todayMedicines, setTodayMedicines] = useState([]);
  const [loadingMedicines, setLoadingMedicines] = useState(true);

  const [upcomingAppointment, setUpcomingAppointment] = useState(null);
  const [allAppointments, setAllAppointments] = useState([]);
  const [loadingAppointments, setLoadingAppointments] = useState(true);

  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [pdfError, setPdfError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const fetchLatestMetrics = async () => {
      try {
        const bmiRec = await getLatestBMI();
        if (isMounted) setLatestBMI(bmiRec);
      } catch (err) {
        console.error('Failed to fetch latest BMI record:', err);
      } finally {
        if (isMounted) setLoadingBMI(false);
      }

      try {
        const diabRec = await getLatestDiabetesPrediction();
        if (isMounted) setLatestDiabetes(diabRec);
      } catch (err) {
        console.error('Failed to fetch latest Diabetes prediction record:', err);
      } finally {
        if (isMounted) setLoadingDiabetes(false);
      }

      try {
        const disRec = await getLatestDiseasePrediction();
        if (isMounted) setLatestDisease(disRec);
      } catch (err) {
        console.error('Failed to fetch latest Disease prediction record:', err);
      } finally {
        if (isMounted) setLoadingDisease(false);
      }

      try {
        const riskRec = await getLatestHealthRisk();
        if (isMounted) setLatestRisk(riskRec);
      } catch (err) {
        console.error('Failed to fetch latest Health Risk record:', err);
      } finally {
        if (isMounted) setLoadingRisk(false);
      }

      try {
        const medsToday = await getTodayMedicineReminders();
        if (isMounted) setTodayMedicines(medsToday || []);
      } catch (err) {
        console.error('Failed to fetch today medicine reminders:', err);
      } finally {
        if (isMounted) setLoadingMedicines(false);
      }

      try {
        const [nextAppt, allAppts] = await Promise.all([
          getNextUpcomingAppointment(),
          getUserAppointments(),
        ]);
        if (isMounted) {
          setUpcomingAppointment(nextAppt);
          setAllAppointments(allAppts || []);
        }
      } catch (err) {
        console.error('Failed to fetch upcoming appointment:', err);
      } finally {
        if (isMounted) setLoadingAppointments(false);
      }
    };

    fetchLatestMetrics();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleDownloadPDF = async () => {
    setDownloadingPDF(true);
    setPdfError('');

    try {
      const blob = await downloadHealthReportPDF();
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Health_Report_Patient_${user?.id || 'Record'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF report:', err);
      setPdfError(err.message || 'Failed to generate PDF report.');
    } finally {
      setDownloadingPDF(false);
    }
  };

  const heightText = user?.height ? `${user.height} cm` : 'Not set';
  const weightText = user?.weight ? `${user.weight} kg` : 'Not set';
  const bloodGroupText = user?.blood_group || 'Not set';

  const isProfileIncomplete = !user?.height || !user?.weight || !user?.blood_group;

  return (
    <div>
      {/* 1. Welcome Card */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(13, 148, 136, 0.22), rgba(19, 28, 46, 0.95))',
          borderColor: 'var(--primary-700)',
          marginBottom: '2rem',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <span className="badge badge-patient">{user?.role || 'PATIENT'}</span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Patient ID #{user?.id}</span>
            </div>

            <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Diabetes Prediction Using Machine Learning
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.25rem' }}>
              Welcome, {user?.full_name || 'Patient'} • Multi-Dataset External Validation & Algorithmic Fairness Portal
            </p>

            {isProfileIncomplete && (
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginTop: '1rem',
                  padding: '0.4rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(245, 158, 11, 0.15)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  color: 'var(--accent-amber)',
                  fontSize: '0.85rem',
                  cursor: 'pointer'
                }}
                onClick={() => navigate('/profile')}
              >
                <AlertCircle size={16} />
                <span>Complete your height, weight & blood group profile</span>
                <ExternalLink size={14} />
              </div>
            )}
          </div>

          {/* Quick Health Summary Chips & PDF Button */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <PageGuideModal
                title="Patient Health Overview Dashboard"
                purpose="Provides a centralized real-time view of your health metrics, AI diagnostic results, upcoming appointments, daily medication schedule, and one-click health PDF export."
                howItWorks={[
                  "Aggregates latest records from database for BMI, Diabetes prediction, Multi-class Disease prediction, and Composite Health Risk.",
                  "Displays upcoming doctor appointment schedules filtered by user account ID.",
                  "Monitors daily medicine schedules and alerts when doses match current system time.",
                  "Generates comprehensive PDF health reports on-the-fly using Python ReportLab backend engine."
                ]}
                howToUse={[
                  "Review key summary chips for instant health status across all modules.",
                  "Click 'Download Health Report PDF' to generate an offline medical summary report.",
                  "Use Quick Action buttons to navigate directly to specific AI diagnostic & guidance modules."
                ]}
              />

              <button
                className="btn btn-primary"
                onClick={handleDownloadPDF}
                disabled={downloadingPDF}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', padding: '0.55rem 1.25rem' }}
              >
                <Download size={18} />
                <span>{downloadingPDF ? 'Generating PDF...' : 'Download Health Report PDF'}</span>
              </button>
            </div>

            <div
              style={{
                display: 'flex',
                gap: '1.25rem',
                background: 'rgba(15, 23, 42, 0.7)',
                padding: '0.85rem 1.25rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                flexWrap: 'wrap'
              }}
            >
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>AGE / GENDER</span>
                <strong style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>{user?.age} yrs, {user?.gender}</strong>
              </div>

              <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>HEIGHT</span>
                <strong style={{ color: user?.height ? 'var(--primary-500)' : 'var(--text-muted)', fontSize: '0.95rem' }}>
                  {heightText}
                </strong>
              </div>

              <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>WEIGHT</span>
                <strong style={{ color: user?.weight ? 'var(--primary-500)' : 'var(--text-muted)', fontSize: '0.95rem' }}>
                  {weightText}
                </strong>
              </div>

              <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>BLOOD GROUP</span>
                <strong style={{ color: user?.blood_group ? 'var(--accent-red)' : 'var(--text-muted)', fontSize: '0.95rem' }}>
                  {bloodGroupText}
                </strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {pdfError && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          <AlertCircle size={18} />
          <span>{pdfError}</span>
        </div>
      )}

      {/* 2. Health Overview Cards */}
      <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-main)' }}>
        Health Overview
      </h2>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2.5rem',
        }}
      >
        {/* Real Health Risk Score Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                <TrendingUp size={20} />
              </div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>Health Risk Score</span>
            </div>
            <span className="badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: 'var(--primary-500)', border: '1px solid rgba(20, 184, 166, 0.3)' }}>
              Active Score
            </span>
          </div>

          <div style={{ marginTop: '0.25rem' }}>
            {loadingRisk ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Loading...</span>
            ) : latestRisk ? (
              <div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: latestRisk.score >= 67 ? 'var(--accent-red)' : latestRisk.score >= 34 ? 'var(--accent-amber)' : 'var(--accent-green)', lineHeight: 1.1 }}>
                  {latestRisk.score} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>/ 100</span>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.25rem' }}>
                  {latestRisk.category}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                Not calculated yet
              </div>
            )}
          </div>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.45rem 0.85rem', display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}
            onClick={() => navigate('/health-risk')}
          >
            <span>View Risk Score</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Real BMI Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                <Scale size={20} />
              </div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>BMI</span>
            </div>
            <span className="badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: 'var(--primary-500)', border: '1px solid rgba(20, 184, 166, 0.3)' }}>
              Active Module
            </span>
          </div>

          <div style={{ marginTop: '0.25rem' }}>
            {loadingBMI ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Loading...</span>
            ) : latestBMI ? (
              <div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary-500)', lineHeight: 1.1 }}>
                  {latestBMI.bmi.toFixed(1)}
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.25rem' }}>
                  {latestBMI.category}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                Not calculated yet
              </div>
            )}
          </div>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.45rem 0.85rem', display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}
            onClick={() => navigate('/bmi')}
          >
            <span>Calculate BMI</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Real Disease Prediction Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                <Stethoscope size={20} />
              </div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>Disease Risk</span>
            </div>
            <span className="badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: 'var(--primary-500)', border: '1px solid rgba(20, 184, 166, 0.3)' }}>
              ML Active
            </span>
          </div>

          <div style={{ marginTop: '0.25rem' }}>
            {loadingDisease ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Loading...</span>
            ) : latestDisease ? (
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-500)', lineHeight: 1.2 }}>
                  {latestDisease.predicted_disease}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Confidence: <strong>{(latestDisease.probability * 100).toFixed(0)}%</strong> ({latestDisease.model})
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                Not calculated yet
              </div>
            )}
          </div>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.45rem 0.85rem', display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}
            onClick={() => navigate('/disease-prediction')}
          >
            <span>Predict Disease</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Real Diabetes Risk Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                <Activity size={20} />
              </div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>Diabetes Risk</span>
            </div>
            <span className="badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: 'var(--primary-500)', border: '1px solid rgba(20, 184, 166, 0.3)' }}>
              ML Active
            </span>
          </div>

          <div style={{ marginTop: '0.25rem' }}>
            {loadingDiabetes ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Loading...</span>
            ) : latestDiabetes ? (
              <div>
                <div
                  style={{
                    fontSize: '1.15rem',
                    fontWeight: 700,
                    color: latestDiabetes.prediction === 1 ? 'var(--accent-red)' : 'var(--accent-green)',
                    lineHeight: 1.2
                  }}
                >
                  {latestDiabetes.risk}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Probability: <strong>{(latestDiabetes.probability * 100).toFixed(0)}%</strong> ({latestDiabetes.model})
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                Not calculated yet
              </div>
            )}
          </div>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.45rem 0.85rem', display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}
            onClick={() => navigate('/diabetes-prediction')}
          >
            <span>Predict Risk</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Real Upcoming Appointment Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                <Calendar size={20} />
              </div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>Upcoming Appointment</span>
            </div>
            <span className="badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: 'var(--primary-500)', border: '1px solid rgba(20, 184, 166, 0.3)' }}>
              Scheduled
            </span>
          </div>

          <div style={{ marginTop: '0.25rem' }}>
            {loadingAppointments ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Loading...</span>
            ) : upcomingAppointment ? (
              <div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--primary-500)', lineHeight: 1.2 }}>
                  {upcomingAppointment.doctor ? upcomingAppointment.doctor.name : 'Doctor'}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', marginTop: '0.2rem', fontWeight: 600 }}>
                  {upcomingAppointment.appointment_date} at {upcomingAppointment.appointment_time}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>
                  {upcomingAppointment.doctor ? upcomingAppointment.doctor.specialization : ''}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                No upcoming appointments.
              </div>
            )}
          </div>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.45rem 0.85rem', display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}
            onClick={() => navigate('/appointments')}
          >
            <span>Book / Manage</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Real Today's Medicines Overview Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ background: 'rgba(20, 184, 166, 0.12)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                <Pill size={20} />
              </div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>Medicines Today</span>
            </div>
            <span className="badge" style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', color: 'var(--primary-500)', border: '1px solid rgba(20, 184, 166, 0.3)' }}>
              Schedule
            </span>
          </div>

          <div style={{ marginTop: '0.25rem' }}>
            {loadingMedicines ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Loading...</span>
            ) : todayMedicines.length > 0 ? (
              <div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary-500)', lineHeight: 1.1 }}>
                  {todayMedicines.length}
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-main)', marginTop: '0.25rem' }}>
                  {todayMedicines.slice(0, 2).map(m => `${m.medicine_name} (${m.dosage})`).join(', ')}
                  {todayMedicines.length > 2 ? ` +${todayMedicines.length - 2} more` : ''}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                No medicine reminders today.
              </div>
            )}
          </div>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.45rem 0.85rem', display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}
            onClick={() => navigate('/medicines')}
          >
            <span>Manage Schedule</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {/* 3. Quick Actions */}
      <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-main)' }}>
        Quick Actions
      </h2>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1rem',
          marginBottom: '2.5rem',
        }}
      >
        <QuickActionButton label="Calculate BMI" icon={Scale} isComingSoon={false} onClick={() => navigate('/bmi')} />
        <QuickActionButton label="Disease Prediction" icon={Stethoscope} isComingSoon={false} onClick={() => navigate('/disease-prediction')} />
        <QuickActionButton label="Diabetes Prediction" icon={Activity} isComingSoon={false} onClick={() => navigate('/diabetes-prediction')} />
        <QuickActionButton label="Diet Guidance" icon={Utensils} isComingSoon={false} onClick={() => navigate('/diet')} />
        <QuickActionButton label="Exercise Plan" icon={Dumbbell} isComingSoon={false} onClick={() => navigate('/exercise')} />
        <QuickActionButton label="Book Appointment" icon={Calendar} isComingSoon={false} onClick={() => navigate('/appointments')} />
        <QuickActionButton label="Add Medicine" icon={Pill} isComingSoon={false} onClick={() => navigate('/medicines')} />
        <QuickActionButton label="Generate Health Report" icon={FileText} isComingSoon={false} onClick={handleDownloadPDF} />
      </div>

      {/* 4. Dashboard Grid: Recent Predictions, Appointments, Medicine Reminders */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}
      >
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.85rem', color: 'var(--text-main)' }}>
            Recent Predictions
          </h3>
          {latestDisease || latestDiabetes ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {latestDisease && (
                <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1rem' }}>
                  <div>
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>DISEASE PREDICTION</span>
                    <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--primary-500)', marginTop: '0.1rem' }}>
                      {latestDisease.predicted_disease} ({(latestDisease.probability * 100).toFixed(0)}%)
                    </div>
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      {new Date(latestDisease.created_at).toLocaleString()}
                    </span>
                  </div>
                  <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.775rem' }} onClick={() => navigate('/disease-prediction')}>
                    View Details
                  </button>
                </div>
              )}

              {latestDiabetes && (
                <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1rem' }}>
                  <div>
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>DIABETES RISK PREDICTION</span>
                    <div style={{ fontSize: '0.95rem', fontWeight: 700, color: latestDiabetes.prediction === 1 ? 'var(--accent-red)' : 'var(--accent-green)', marginTop: '0.1rem' }}>
                      {latestDiabetes.risk} ({(latestDiabetes.probability * 100).toFixed(0)}%)
                    </div>
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      {new Date(latestDiabetes.created_at).toLocaleString()}
                    </span>
                  </div>
                  <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.775rem' }} onClick={() => navigate('/diabetes-prediction')}>
                    View Details
                  </button>
                </div>
              )}
            </div>
          ) : (
            <EmptyStateCard
              title="No Recent Predictions"
              message="AI disease risk prediction modules will record your assessments here."
              icon={Stethoscope}
            />
          )}
        </div>

        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.85rem', color: 'var(--text-main)' }}>
            Upcoming Appointments
          </h3>
          {allAppointments.filter(a => a.status === 'Scheduled').length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {allAppointments.filter(a => a.status === 'Scheduled').map((appt) => (
                <div key={`dash-appt-${appt.id}`} className="card" style={{ padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <strong style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>
                      {appt.doctor ? appt.doctor.name : 'Doctor'}
                    </strong>
                    <div style={{ fontSize: '0.775rem', color: 'var(--primary-500)', fontWeight: 600 }}>
                      {appt.appointment_date} at {appt.appointment_time}
                    </div>
                  </div>
                  <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.775rem' }} onClick={() => navigate('/appointments')}>
                    Details
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <EmptyStateCard
              title="No Scheduled Appointments"
              message="No upcoming appointments."
              icon={Calendar}
            />
          )}
        </div>

        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.85rem', color: 'var(--text-main)' }}>
            Medicine Reminders
          </h3>
          {todayMedicines.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {todayMedicines.map((m) => (
                <div key={`dash-med-${m.id}`} className="card" style={{ padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <strong style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>{m.medicine_name}</strong> ({m.dosage})
                    <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>Time: <strong style={{ color: 'var(--primary-500)' }}>{m.reminder_time}</strong> • {m.frequency}</div>
                  </div>
                  <span className="badge badge-patient">Active</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyStateCard
              title="No Active Reminders"
              message="No medicine reminders today."
              icon={Pill}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
