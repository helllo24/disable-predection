import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { predictDiabetes, getDiabetesHistory } from '../services/api';
import { Activity, AlertCircle, CheckCircle2, History, Info, Stethoscope, Clock, ShieldAlert, Cpu } from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const DiabetesPrediction = () => {
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    pregnancies: '0',
    glucose: '120',
    blood_pressure: '70',
    skin_thickness: '20',
    insulin: '79',
    bmi: '25.0',
    diabetes_pedigree_function: '0.47',
    age: '30',
  });

  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Pre-fill Age and BMI from user profile if available
  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        age: user.age ? String(user.age) : prev.age,
        bmi: user.weight && user.height ? (user.weight / Math.pow(user.height / 100, 2)).toFixed(1) : prev.bmi
      }));
    }
  }, [user]);

  const fetchHistory = async () => {
    try {
      setLoadingHistory(true);
      const data = await getDiabetesHistory();
      setHistory(data || []);
      if (data && data.length > 0 && !result) {
        setResult(data[0]); // Default to latest record
      }
    } catch (err) {
      console.error('Failed to load diabetes prediction history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const preg = parseInt(formData.pregnancies, 10);
    const gluc = parseFloat(formData.glucose);
    const bp = parseFloat(formData.blood_pressure);
    const skin = parseFloat(formData.skin_thickness);
    const ins = parseFloat(formData.insulin);
    const bmiVal = parseFloat(formData.bmi);
    const dpf = parseFloat(formData.diabetes_pedigree_function);
    const ageVal = parseInt(formData.age, 10);

    if (isNaN(preg) || preg < 0 || preg > 25) {
      setError('Pregnancies must be a valid number between 0 and 25.');
      return;
    }
    if (isNaN(gluc) || gluc < 0 || gluc > 500) {
      setError('Glucose level must be a valid non-negative number (0-500 mg/dL).');
      return;
    }
    if (isNaN(bp) || bp < 0 || bp > 250) {
      setError('Blood pressure must be a valid non-negative number (0-250 mm Hg).');
      return;
    }
    if (isNaN(skin) || skin < 0 || skin > 150) {
      setError('Skin thickness must be a valid non-negative number (0-150 mm).');
      return;
    }
    if (isNaN(ins) || ins < 0 || ins > 1200) {
      setError('Insulin level must be a valid non-negative number (0-1200 mu U/ml).');
      return;
    }
    if (isNaN(bmiVal) || bmiVal < 0 || bmiVal > 120) {
      setError('BMI must be a valid non-negative number (0-120).');
      return;
    }
    if (isNaN(dpf) || dpf < 0 || dpf > 5) {
      setError('Diabetes Pedigree Function must be a valid number between 0.0 and 5.0.');
      return;
    }
    if (isNaN(ageVal) || ageVal < 1 || ageVal > 120) {
      setError('Age must be a valid number between 1 and 120.');
      return;
    }

    setLoading(true);

    try {
      const payload = {
        pregnancies: preg,
        glucose: gluc,
        blood_pressure: bp,
        skin_thickness: skin,
        insulin: ins,
        bmi: bmiVal,
        diabetes_pedigree_function: dpf,
        age: ageVal,
      };

      const res = await predictDiabetes(payload);
      setResult(res);
      setLoading(false);
      fetchHistory().catch(err => console.error('Background history update error:', err));
    } catch (err) {
      setError(err.message || 'Failed to generate diabetes prediction.');
      setLoading(false);
    }
  };

  const isHighRisk = result && (result.prediction === 1 || result.risk.toLowerCase().includes('high'));
  const riskColor = isHighRisk ? '#ef4444' : '#10b981';
  const riskBg = isHighRisk ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)';
  const riskBorder = isHighRisk ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)';

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                backgroundColor: 'rgba(20, 184, 166, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary-500)',
              }}
            >
              <Activity size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                AI Diabetes Risk Prediction
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Machine Learning prediction module powered by trained XGBoost / Random Forest models
              </p>
            </div>
          </div>

          <PageGuideModal
            title="AI Diabetes Risk Prediction"
            purpose="Predicts 5-year risk of Type 2 Diabetes based on 8 clinical health parameters using trained XGBoost and Random Forest ML classification models."
            howItWorks={[
              "Accepts 8 clinical parameters: Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree Function, and Age.",
              "Input features are normalized with StandardScaler and passed into a pre-trained XGBoost Classifier.",
              "Backend outputs probability score (0-100%), binary risk prediction (High Risk / Low Risk), and top 3 feature importance factors.",
              "Saves prediction record in database and updates patient history table."
            ]}
            howToUse={[
              "Enter your clinical health values or click 'Fill Sample High Risk' / 'Fill Sample Normal' for testing.",
              "Click 'Run Diabetes Risk Prediction' to process.",
              "View your probability percentage, risk assessment gauge, and historical log below."
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

      {/* Main Grid: Form & Result */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2.5rem',
        }}
      >
        {/* Physiological Metrics Input Form */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            Enter Physiological Indicators
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Pregnancies</label>
                <input
                  type="number"
                  name="pregnancies"
                  className="form-input"
                  value={formData.pregnancies}
                  onChange={handleChange}
                  min="0"
                  max="25"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Glucose (mg/dL)</label>
                <input
                  type="number"
                  step="any"
                  name="glucose"
                  className="form-input"
                  placeholder="e.g. 120"
                  value={formData.glucose}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Blood Pressure (mm Hg)</label>
                <input
                  type="number"
                  step="any"
                  name="blood_pressure"
                  className="form-input"
                  placeholder="e.g. 70"
                  value={formData.blood_pressure}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Skin Thickness (mm)</label>
                <input
                  type="number"
                  step="any"
                  name="skin_thickness"
                  className="form-input"
                  placeholder="e.g. 20"
                  value={formData.skin_thickness}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Insulin (mu U/ml)</label>
                <input
                  type="number"
                  step="any"
                  name="insulin"
                  className="form-input"
                  placeholder="e.g. 79"
                  value={formData.insulin}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">BMI (kg/m²)</label>
                <input
                  type="number"
                  step="any"
                  name="bmi"
                  className="form-input"
                  placeholder="e.g. 25.5"
                  value={formData.bmi}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Diabetes Pedigree Func</label>
                <input
                  type="number"
                  step="0.01"
                  name="diabetes_pedigree_function"
                  className="form-input"
                  placeholder="e.g. 0.35"
                  value={formData.diabetes_pedigree_function}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Age (years)</label>
                <input
                  type="number"
                  name="age"
                  className="form-input"
                  value={formData.age}
                  onChange={handleChange}
                  min="1"
                  max="120"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem' }}
              disabled={loading}
            >
              {loading ? 'Running ML Inference...' : 'Predict Diabetes Risk'}
            </button>
          </form>

          {/* Prominent Medical Disclaimer */}
          <div
            style={{
              marginTop: '1.5rem',
              padding: '0.85rem 1rem',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid var(--border-color)',
              fontSize: '0.8rem',
              color: 'var(--text-muted)',
              display: 'flex',
              gap: '0.65rem',
              alignItems: 'flex-start',
            }}
          >
            <ShieldAlert size={18} style={{ minWidth: 18, color: 'var(--accent-amber)', marginTop: 2 }} />
            <span>
              <strong>Medical Disclaimer:</strong> This prediction is generated by a machine-learning model for educational/informational purposes and is not a medical diagnosis. Please consult a qualified healthcare professional for medical advice, diagnosis, or treatment.
            </span>
          </div>
        </div>

        {/* Prediction Result Display Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'between' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            ML Risk Assessment Output
          </h2>

          {result ? (
            <div>
              <div
                style={{
                  textAlign: 'center',
                  padding: '1.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'rgba(15, 23, 42, 0.8)',
                  border: `1px solid ${riskBorder}`,
                  marginBottom: '1.5rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Cpu size={18} style={{ color: 'var(--primary-500)' }} />
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1 }}>
                    Model: {result.model}
                  </span>
                </div>

                <div
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: 800,
                    color: riskColor,
                    marginBottom: '0.5rem',
                  }}
                >
                  {result.risk}
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                  {isHighRisk
                    ? 'The model predicts a higher diabetes risk based on the entered values.'
                    : 'The model predicts a lower diabetes risk based on the entered values.'}
                </p>

                {/* Risk Probability Bar */}
                <div style={{ maxWidth: 300, margin: '0 auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Risk Probability</span>
                    <strong style={{ color: riskColor }}>{(result.probability * 100).toFixed(1)}%</strong>
                  </div>
                  <div
                    style={{
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: 'rgba(30, 45, 74, 0.8)',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        width: `${Math.min(100, Math.max(5, result.probability * 100))}%`,
                        backgroundColor: riskColor,
                        transition: 'width 0.5s ease',
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Patient Input Parameters Snapshot */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '0.65rem',
                  fontSize: '0.825rem',
                  background: 'rgba(15, 23, 42, 0.5)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                }}
              >
                <div><span style={{ color: 'var(--text-muted)' }}>Glucose:</span> <strong>{result.glucose} mg/dL</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Blood Pressure:</span> <strong>{result.blood_pressure} mm Hg</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>BMI:</span> <strong>{result.bmi}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Insulin:</span> <strong>{result.insulin}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Pedigree Func:</span> <strong>{result.diabetes_pedigree_function}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Age:</span> <strong>{result.age} yrs</strong></div>

                {result.created_at && (
                  <div style={{ gridColumn: 'span 2', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Assessed At: </span>
                    <strong>{new Date(result.created_at).toLocaleString()}</strong>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div
              style={{
                textAlign: 'center',
                padding: '3.5rem 1rem',
                color: 'var(--text-muted)',
                backgroundColor: 'rgba(15, 23, 42, 0.4)',
                borderRadius: 'var(--radius-md)',
                border: '1px dashed var(--border-color)',
              }}
            >
              <Stethoscope size={40} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
              <p>Enter physiological metrics on the left to run ML risk prediction.</p>
            </div>
          )}
        </div>
      </div>

      {/* Diabetes Prediction History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--primary-500)' }} />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Diabetes Prediction History
            </h2>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {history.length} Assessment{history.length !== 1 ? 's' : ''} Stored
          </span>
        </div>

        {loadingHistory ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            Loading prediction history...
          </p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Clock size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 500 }}>No diabetes prediction history found.</p>
            <span style={{ fontSize: '0.85rem' }}>Run a prediction above to record your first assessment.</span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Glucose</th>
                  <th style={{ padding: '0.75rem 1rem' }}>BMI</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Age</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Predicted Risk</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Probability</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Model</th>
                </tr>
              </thead>
              <tbody>
                {history.map((rec) => {
                  const isHigh = rec.prediction === 1 || rec.risk.toLowerCase().includes('high');
                  const badgeColor = isHigh ? '#ef4444' : '#10b981';
                  const badgeBg = isHigh ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)';
                  const badgeBorder = isHigh ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)';

                  return (
                    <tr
                      key={rec.id}
                      style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)', transition: 'background 0.2s' }}
                    >
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                        {new Date(rec.created_at).toLocaleString()}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                        {rec.glucose} mg/dL
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                        {rec.bmi}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                        {rec.age}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: badgeBg,
                            color: badgeColor,
                            border: `1px solid ${badgeBorder}`,
                          }}
                        >
                          {rec.risk}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: badgeColor }}>
                        {(rec.probability * 100).toFixed(1)}%
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                        {rec.model}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiabetesPrediction;
