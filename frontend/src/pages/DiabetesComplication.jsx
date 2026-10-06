import React, { useState, useEffect } from 'react';
import {
  Activity,
  Heart,
  Eye,
  Footprints,
  Brain,
  AlertTriangle,
  CheckCircle,
  Clock,
  ShieldAlert,
  Info,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import {
  predictDiabetesComplications,
  getLatestDiabetesComplicationPrediction,
  getDiabetesComplicationsHistory
} from '../services/api';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import PageGuideModal from '../components/PageGuideModal';

const DiabetesComplication = () => {
  const [formData, setFormData] = useState({
    age: 55,
    systolic_bp: 140,
    diastolic_bp: 90,
    hba1c: 8.5,
    fasting_glucose: 165,
    diabetes_duration_years: 10,
    bmi: 28.5,
    serum_creatinine: 1.4,
    albumin_urine: 1,
    tingling_feet: 1,
    vibration_loss: 0,
    ankle_reflex: 1,
    loss_of_sensory_perception: 1,
    history_of_ulcer: 0,
    ankle_brachial_index: 0.85,
    intermittent_claudication: 1
  });

  const [latestResult, setLatestResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setFetching(true);
    try {
      const [latest, hist] = await Promise.allSettled([
        getLatestDiabetesComplicationPrediction(),
        getDiabetesComplicationsHistory()
      ]);

      if (latest.status === 'fulfilled') setLatestResult(latest.value);
      if (hist.status === 'fulfilled') setHistory(hist.value);
    } catch (err) {
      console.error("Error fetching initial complication data:", err);
    } finally {
      setFetching(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const handleQuickFill = () => {
    setFormData({
      age: 58,
      systolic_bp: 148,
      diastolic_bp: 94,
      hba1c: 9.2,
      fasting_glucose: 185,
      diabetes_duration_years: 14,
      bmi: 31.2,
      serum_creatinine: 1.9,
      albumin_urine: 2,
      tingling_feet: 1,
      vibration_loss: 1,
      ankle_reflex: 2,
      loss_of_sensory_perception: 1,
      history_of_ulcer: 0,
      ankle_brachial_index: 0.78,
      intermittent_claudication: 1
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      const result = await predictDiabetesComplications(formData);
      setLatestResult(result);
      setSuccessMsg('Multi-organ diabetes complication risk assessment generated successfully!');
      
      // Refresh history
      const updatedHistory = await getDiabetesComplicationsHistory();
      setHistory(updatedHistory);
    } catch (err) {
      setError(err.message || 'Failed to calculate complication risks. Please check inputs.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadge = (riskText) => {
    if (!riskText) return <span className="badge badge-secondary">Unknown</span>;
    const lower = riskText.toLowerCase();

    if (lower.includes('high') || lower.includes('severe') || lower.includes('elevated') || lower.includes('signs')) {
      return (
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
          padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600,
          backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)'
        }}>
          <AlertTriangle size={12} /> {riskText}
        </span>
      );
    }

    if (lower.includes('moderate') || lower.includes('category 1')) {
      return (
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
          padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600,
          backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.3)'
        }}>
          <Info size={12} /> {riskText}
        </span>
      );
    }

    return (
      <span style={{
        display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
        padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600,
        backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.3)'
      }}>
        <CheckCircle size={12} /> {riskText}
      </span>
    );
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-wrapper">
        <Navbar />
        <main className="content-area">
          <div className="page-header" style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '12px',
                  background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ffffff'
                }}>
                  <Activity size={26} />
                </div>
                <div>
                  <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                    Diabetes Complication Risk Assessment
                  </h1>
                  <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    Multi-organ secondary complication risk evaluation powered by clinical ML models
                  </p>
                </div>
              </div>

              <PageGuideModal
                title="Secondary Complications Risk Assessment"
                purpose="Evaluates risk levels across 6 major diabetes-related secondary complications: Retinopathy, Nephropathy, Neuropathy, Peripheral Artery Disease (PAD), Cardiovascular Disease, and Diabetic Foot Ulcer."
                howItWorks={[
                  "Processes 16 physiological parameters including HbA1c, Fasting Glucose, Blood Pressure, Serum Creatinine, Urine Albumin, and ABI index.",
                  "Evaluates multi-organ clinical risk matrices to compute individual risk scores for each of the 6 complication domains.",
                  "Provides organ-specific risk badges, clinical warnings, and targeted lifestyle recommendations."
                ]}
                howToUse={[
                  "Fill in clinical lab measurements or click 'Quick Fill Sample Data' for demonstration.",
                  "Click 'Run Complications Assessment' to compute multi-organ risk scores.",
                  "Review the risk breakdown cards for Retinopathy, Nephropathy, Neuropathy, PAD, Heart Disease, and Foot Health."
                ]}
              />
            </div>
          </div>

          {/* Educational Medical Disclaimer */}
          <div style={{
            backgroundColor: 'rgba(59, 130, 246, 0.08)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            borderRadius: '12px', padding: '1rem 1.25rem', marginBottom: '1.5rem',
            display: 'flex', alignItems: 'flex-start', gap: '0.75rem'
          }}>
            <ShieldAlert size={20} style={{ color: '#3b82f6', flexShrink: 0, marginTop: '2px' }} />
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong style={{ color: '#3b82f6' }}>Medical Disclaimer:</strong> This Diabetes Complication Assessment tool provides educational risk estimations across 6 secondary complication domains. It does NOT prescribe medication, change dosages, or replace professional diagnosis. Always consult a licensed medical professional for clinical diagnosis and management.
            </div>
          </div>

          {error && (
            <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
              <AlertTriangle size={18} /> {error}
            </div>
          )}

          {successMsg && (
            <div className="alert alert-success" style={{ marginBottom: '1.5rem' }}>
              <CheckCircle size={18} /> {successMsg}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
            {/* Left: Input Form */}
            <div className="card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h2 style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0 }}>Clinical Health Metrics</h2>
                <button
                  type="button"
                  onClick={handleQuickFill}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.75rem', padding: '0.4rem 0.75rem' }}
                >
                  Quick Fill Sample Values
                </button>
              </div>

              <form onSubmit={handleSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="form-group">
                    <label className="form-label">Age (years)</label>
                    <input
                      type="number" name="age" className="form-input"
                      value={formData.age} onChange={handleChange} required min="18" max="100"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">BMI (kg/m²)</label>
                    <input
                      type="number" step="0.1" name="bmi" className="form-input"
                      value={formData.bmi} onChange={handleChange} required min="15" max="55"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Systolic BP (mmHg)</label>
                    <input
                      type="number" name="systolic_bp" className="form-input"
                      value={formData.systolic_bp} onChange={handleChange} required min="80" max="220"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Diastolic BP (mmHg)</label>
                    <input
                      type="number" name="diastolic_bp" className="form-input"
                      value={formData.diastolic_bp} onChange={handleChange} required min="50" max="140"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">HbA1c Level (%)</label>
                    <input
                      type="number" step="0.1" name="hba1c" className="form-input"
                      value={formData.hba1c} onChange={handleChange} required min="4.0" max="16.0"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Fasting Glucose (mg/dL)</label>
                    <input
                      type="number" name="fasting_glucose" className="form-input"
                      value={formData.fasting_glucose} onChange={handleChange} required min="70" max="350"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Diabetes Duration (yrs)</label>
                    <input
                      type="number" name="diabetes_duration_years" className="form-input"
                      value={formData.diabetes_duration_years} onChange={handleChange} required min="0" max="60"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Serum Creatinine (mg/dL)</label>
                    <input
                      type="number" step="0.1" name="serum_creatinine" className="form-input"
                      value={formData.serum_creatinine} onChange={handleChange} required min="0.3" max="15.0"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Urine Albumin (0-4)</label>
                    <select
                      name="albumin_urine" className="form-select"
                      value={formData.albumin_urine} onChange={handleChange}
                    >
                      <option value={0}>0 - Normal / None</option>
                      <option value={1}>1 - Trace Microalbuminuria</option>
                      <option value={2}>2 - Moderate Proteinuria</option>
                      <option value={3}>3 - High Proteinuria</option>
                      <option value={4}>4 - Severe Proteinuria</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Ankle-Brachial Index (ABI)</label>
                    <input
                      type="number" step="0.01" name="ankle_brachial_index" className="form-input"
                      value={formData.ankle_brachial_index} onChange={handleChange} required min="0.3" max="1.5"
                    />
                  </div>
                </div>

                {/* Neurological & Foot Specific Factors */}
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Sensory & Reflex Identifiers
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox" name="tingling_feet"
                        checked={formData.tingling_feet === 1}
                        onChange={(e) => setFormData(p => ({ ...p, tingling_feet: e.target.checked ? 1 : 0 }))}
                      />
                      Foot Tingling / Numbness
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox" name="vibration_loss"
                        checked={formData.vibration_loss === 1}
                        onChange={(e) => setFormData(p => ({ ...p, vibration_loss: e.target.checked ? 1 : 0 }))}
                      />
                      Loss of Vibration Sensation
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox" name="loss_of_sensory_perception"
                        checked={formData.loss_of_sensory_perception === 1}
                        onChange={(e) => setFormData(p => ({ ...p, loss_of_sensory_perception: e.target.checked ? 1 : 0 }))}
                      />
                      Loss of Protective Sensation
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox" name="intermittent_claudication"
                        checked={formData.intermittent_claudication === 1}
                        onChange={(e) => setFormData(p => ({ ...p, intermittent_claudication: e.target.checked ? 1 : 0 }))}
                      />
                      Leg Pain While Walking (Claudication)
                    </label>
                  </div>
                </div>

                <button
                  type="submit" disabled={loading} className="btn btn-primary"
                  style={{ width: '100%', marginTop: '1.5rem', padding: '0.75rem' }}
                >
                  {loading ? 'Evaluating 6 Complication ML Models...' : 'Run Complication Risk Assessment'}
                </button>
              </form>
            </div>

            {/* Right: Latest Assessment Overview */}
            <div>
              {latestResult ? (
                <div className="card" style={{ padding: '1.5rem', background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
                        Latest Risk Assessment
                      </span>
                      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0.25rem 0 0 0', color: 'var(--text-primary)' }}>
                        {latestResult.overall_risk_summary}
                      </h2>
                    </div>
                    {getRiskBadge(latestResult.overall_risk_summary)}
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                    Generated on {new Date(latestResult.created_at).toLocaleString()}
                  </div>

                  {/* 6 Complication Cards Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    {/* ❤️ Heart Card */}
                    <div style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <Heart size={18} style={{ color: '#ef4444' }} />
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>❤️ Heart (Cardio)</span>
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{getRiskBadge(latestResult.heart_risk)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Probability: {(latestResult.heart_probability * 100).toFixed(1)}%
                      </div>
                    </div>

                    {/* 🫘 Kidney Card */}
                    <div style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <Activity size={18} style={{ color: '#3b82f6' }} />
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>🫘 Kidney (Nephro)</span>
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{getRiskBadge(latestResult.kidney_risk)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Probability: {(latestResult.kidney_probability * 100).toFixed(1)}%
                      </div>
                    </div>

                    {/* 🧠 Nerve Card */}
                    <div style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <Brain size={18} style={{ color: '#a855f7' }} />
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>🧠 Nerve (Neuro)</span>
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{getRiskBadge(latestResult.neuropathy_risk)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Probability: {(latestResult.neuropathy_probability * 100).toFixed(1)}%
                      </div>
                    </div>

                    {/* 👁️ Eye Card */}
                    <div style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <Eye size={18} style={{ color: '#06b6d4' }} />
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>👁️ Eye (Retino)</span>
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{getRiskBadge(latestResult.retinopathy_risk)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Probability: {(latestResult.retinopathy_probability * 100).toFixed(1)}%
                      </div>
                    </div>

                    {/* 🦶 Foot Card */}
                    <div style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <Footprints size={18} style={{ color: '#f59e0b' }} />
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>🦶 Foot Ulcer</span>
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{getRiskBadge(latestResult.foot_risk)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Probability: {(latestResult.foot_probability * 100).toFixed(1)}%
                      </div>
                    </div>

                    {/* 🩸 Vascular Card */}
                    <div style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <TrendingUp size={18} style={{ color: '#ec4899' }} />
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>🩸 Vascular</span>
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{getRiskBadge(latestResult.vascular_risk)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Probability: {(latestResult.vascular_probability * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="card" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <Activity size={48} style={{ margin: '0 auto 1rem auto', opacity: 0.4 }} />
                  <h3>No Assessment Generated Yet</h3>
                  <p style={{ fontSize: '0.85rem' }}>
                    Fill in your health parameters on the left and click "Run Complication Risk Assessment" to view detailed multi-organ risk analysis.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Prediction History Table */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={18} /> Assessment History
            </h3>

            {history.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.75rem' }}>Date</th>
                      <th style={{ padding: '0.75rem' }}>Overall Summary</th>
                      <th style={{ padding: '0.75rem' }}>Heart Risk</th>
                      <th style={{ padding: '0.75rem' }}>Kidney Risk</th>
                      <th style={{ padding: '0.75rem' }}>Neuropathy</th>
                      <th style={{ padding: '0.75rem' }}>Foot Ulcer</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((item) => (
                      <tr key={item.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.75rem' }}>{new Date(item.created_at).toLocaleDateString()}</td>
                        <td style={{ padding: '0.75rem' }}>{getRiskBadge(item.overall_risk_summary)}</td>
                        <td style={{ padding: '0.75rem' }}>{item.heart_risk}</td>
                        <td style={{ padding: '0.75rem' }}>{item.kidney_risk}</td>
                        <td style={{ padding: '0.75rem' }}>{item.neuropathy_risk}</td>
                        <td style={{ padding: '0.75rem' }}>{item.foot_risk}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>No past complication assessments recorded.</p>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DiabetesComplication;
