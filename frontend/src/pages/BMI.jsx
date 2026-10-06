import React, { useState, useEffect } from 'react';
import { calculateBMI, getBMIHistory } from '../services/api';
import { Scale, AlertCircle, CheckCircle2, History, Info, ArrowRight, Clock } from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const getCategoryColor = (category) => {
  switch (category) {
    case 'Underweight':
      return { bg: 'rgba(59, 130, 246, 0.15)', text: '#3b82f6', border: 'rgba(59, 130, 246, 0.3)' };
    case 'Normal weight':
      return { bg: 'rgba(16, 185, 129, 0.15)', text: '#10b981', border: 'rgba(16, 185, 129, 0.3)' };
    case 'Overweight':
      return { bg: 'rgba(245, 158, 11, 0.15)', text: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)' };
    case 'Obesity':
      return { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444', border: 'rgba(239, 68, 68, 0.3)' };
    default:
      return { bg: 'rgba(148, 163, 184, 0.15)', text: '#94a3b8', border: 'rgba(148, 163, 184, 0.3)' };
  }
};

const getGaugePercentage = (bmi) => {
  if (!bmi || bmi <= 0) return 0;
  if (bmi < 18.5) {
    // 0% to 25% range
    return Math.min(25, Math.max(2, (bmi / 18.5) * 25));
  } else if (bmi <= 24.9) {
    // 25% to 50% range
    return 25 + ((bmi - 18.5) / (24.9 - 18.5)) * 25;
  } else if (bmi <= 29.9) {
    // 50% to 75% range
    return 50 + ((bmi - 25.0) / (29.9 - 25.0)) * 25;
  } else {
    // 75% to 100% range
    return Math.min(98, 75 + ((bmi - 30.0) / 10) * 25);
  }
};

const BMI = () => {
  const [height, setHeight] = useState('');
  const [heightUnit, setHeightUnit] = useState('cm');
  const [weight, setWeight] = useState('');
  const [weightUnit, setWeightUnit] = useState('kg');

  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const fetchHistory = async () => {
    try {
      setLoadingHistory(true);
      const data = await getBMIHistory();
      setHistory(data || []);
      if (data && data.length > 0 && !result) {
        setResult(data[0]); // Default to latest record if available
      }
    } catch (err) {
      console.error('Failed to load BMI history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');

    const hNum = parseFloat(height);
    const wNum = parseFloat(weight);

    if (!height || isNaN(hNum) || hNum <= 0) {
      setError('Please enter a valid positive number for height.');
      return;
    }

    if (!weight || isNaN(wNum) || wNum <= 0) {
      setError('Please enter a valid positive number for weight.');
      return;
    }

    if (heightUnit === 'cm' && (hNum < 30 || hNum > 300)) {
      setError('Height in cm should be between 30 cm and 300 cm.');
      return;
    }

    if (heightUnit === 'ft' && (hNum < 1 || hNum > 10)) {
      setError('Height in feet should be between 1 ft and 10 ft.');
      return;
    }

    if (weightUnit === 'kg' && (wNum < 2 || wNum > 500)) {
      setError('Weight in kg should be between 2 kg and 500 kg.');
      return;
    }

    if (weightUnit === 'lb' && (wNum < 5 || wNum > 1100)) {
      setError('Weight in lb should be between 5 lb and 1100 lb.');
      return;
    }

    setLoading(true);

    try {
      const res = await calculateBMI({
        height: hNum,
        height_unit: heightUnit,
        weight: wNum,
        weight_unit: weightUnit,
      });

      setResult(res);
      await fetchHistory(); // Refresh history table
    } catch (err) {
      setError(err.message || 'Failed to calculate BMI.');
    } finally {
      setLoading(false);
    }
  };

  const categoryStyle = result ? getCategoryColor(result.category) : null;
  const gaugePos = result ? getGaugePercentage(result.bmi) : 0;

  return (
    <div style={{ maxWidth: 950, margin: '0 auto' }}>
      {/* Header Banner */}
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
              <Scale size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                BMI Calculator & Screening
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Calculate your Body Mass Index (BMI) and track your health category over time
              </p>
            </div>
          </div>

          <PageGuideModal
            title="Body Mass Index (BMI) Calculator"
            purpose="Calculates Body Mass Index (BMI) using height and weight, classifies into WHO standard categories, and updates your baseline patient profile for downstream ML models."
            howItWorks={[
              "Metric Formula: BMI = weight (kg) / [height (m)]².",
              "Imperial Formula: BMI = 703 × weight (lb) / [height (in)]².",
              "WHO Standard Categories: Underweight (<18.5), Normal weight (18.5-24.9), Overweight (25-29.9), Obesity (≥30).",
              "Saves measurement history and automatically updates patient profile height and weight."
            ]}
            howToUse={[
              "Select unit system (cm/kg or feet/inches/lbs).",
              "Enter your height and weight values.",
              "Click 'Calculate BMI' to see your classification category, gauge pointer, and clinical recommendation."
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

      {/* Main Grid: Calculator Form & Result Card */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2.5rem',
        }}
      >
        {/* Calculator Form */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            Enter Body Metrics
          </h2>

          <form onSubmit={handleCalculate}>
            {/* Height Input & Unit */}
            <div className="form-group">
              <label className="form-label">Height</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="number"
                  step="any"
                  className="form-input"
                  placeholder={heightUnit === 'cm' ? 'e.g. 170' : 'e.g. 5.6'}
                  value={height}
                  onChange={(e) => {
                    setHeight(e.target.value);
                    setError('');
                  }}
                  required
                />
                <select
                  className="form-select"
                  style={{ width: '100px' }}
                  value={heightUnit}
                  onChange={(e) => setHeightUnit(e.target.value)}
                >
                  <option value="cm">cm</option>
                  <option value="ft">ft</option>
                </select>
              </div>
            </div>

            {/* Weight Input & Unit */}
            <div className="form-group">
              <label className="form-label">Weight</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="number"
                  step="any"
                  className="form-input"
                  placeholder={weightUnit === 'kg' ? 'e.g. 68' : 'e.g. 150'}
                  value={weight}
                  onChange={(e) => {
                    setWeight(e.target.value);
                    setError('');
                  }}
                  required
                />
                <select
                  className="form-select"
                  style={{ width: '100px' }}
                  value={weightUnit}
                  onChange={(e) => setWeightUnit(e.target.value)}
                >
                  <option value="kg">kg</option>
                  <option value="lb">lb</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem' }}
              disabled={loading}
            >
              {loading ? 'Calculating...' : 'Calculate BMI'}
            </button>
          </form>

          {/* Medical Disclaimer */}
          <div
            style={{
              marginTop: '1.5rem',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              fontSize: '0.8rem',
              color: 'var(--text-muted)',
              display: 'flex',
              gap: '0.5rem',
              alignItems: 'flex-start',
            }}
          >
            <Info size={16} style={{ minWidth: 16, color: 'var(--primary-500)', marginTop: 2 }} />
            <span>
              <strong>Medical Disclaimer:</strong> BMI is a general screening measure and does not replace professional medical advice or clinical diagnosis.
            </span>
          </div>
        </div>

        {/* Result Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'between' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            BMI Calculation Result
          </h2>

          {result ? (
            <div>
              <div
                style={{
                  textAlign: 'center',
                  padding: '1.5rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'rgba(15, 23, 42, 0.7)',
                  border: `1px solid ${categoryStyle.border}`,
                  marginBottom: '1.5rem',
                }}
              >
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1 }}>
                  Calculated BMI
                </span>
                <div style={{ fontSize: '3rem', fontWeight: 800, color: categoryStyle.text, lineHeight: 1.1, margin: '0.35rem 0' }}>
                  {result.bmi.toFixed(1)}
                </div>

                <div
                  className="badge"
                  style={{
                    backgroundColor: categoryStyle.bg,
                    color: categoryStyle.text,
                    border: `1px solid ${categoryStyle.border}`,
                    fontSize: '0.95rem',
                    padding: '0.4rem 1rem',
                  }}
                >
                  Category: {result.category}
                </div>
              </div>

              {/* Visual BMI Gauge Spectrum */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  <span>Underweight (&lt;18.5)</span>
                  <span>Normal (18.5-24.9)</span>
                  <span>Overweight (25-29.9)</span>
                  <span>Obese (30+)</span>
                </div>

                <div
                  style={{
                    height: 12,
                    borderRadius: 6,
                    background: 'linear-gradient(to right, #3b82f6 0%, #3b82f6 25%, #10b981 25%, #10b981 50%, #f59e0b 50%, #f59e0b 75%, #ef4444 75%, #ef4444 100%)',
                    position: 'relative',
                  }}
                >
                  {/* Gauge Pointer */}
                  <div
                    style={{
                      position: 'absolute',
                      top: -4,
                      left: `calc(${gaugePos}% - 8px)`,
                      width: 16,
                      height: 20,
                      backgroundColor: '#ffffff',
                      borderRadius: 3,
                      boxShadow: '0 0 6px rgba(0,0,0,0.5)',
                      border: '2px solid #0f172a',
                      transition: 'left 0.3s ease',
                    }}
                  />
                </div>
              </div>

              {/* Metrics Summary breakdown */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '0.75rem',
                  fontSize: '0.85rem',
                  background: 'rgba(15, 23, 42, 0.5)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                }}
              >
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Input Height</span>
                  <strong>{result.height} {result.height_unit}</strong> ({result.height_m.toFixed(2)} m)
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Input Weight</span>
                  <strong>{result.weight} {result.weight_unit}</strong> ({result.weight_kg.toFixed(1)} kg)
                </div>
                <div style={{ gridColumn: 'span 2', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)', display: 'block' }}>Calculated At</span>
                  <strong>{new Date(result.created_at).toLocaleString()}</strong>
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{
                textAlign: 'center',
                padding: '3rem 1rem',
                color: 'var(--text-muted)',
                backgroundColor: 'rgba(15, 23, 42, 0.4)',
                borderRadius: 'var(--radius-md)',
                border: '1px dashed var(--border-color)',
              }}
            >
              <Scale size={40} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
              <p>Enter your height and weight on the left to compute your BMI result.</p>
            </div>
          )}
        </div>
      </div>

      {/* BMI Calculation History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--primary-500)' }} />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              BMI Calculation History
            </h2>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {history.length} Record{history.length !== 1 ? 's' : ''} Found
          </span>
        </div>

        {loadingHistory ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            Loading BMI history...
          </p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Clock size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 500 }}>No BMI records found.</p>
            <span style={{ fontSize: '0.85rem' }}>Calculate your BMI above to store your first record.</span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Height</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Weight</th>
                  <th style={{ padding: '0.75rem 1rem' }}>BMI Value</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Category</th>
                </tr>
              </thead>
              <tbody>
                {history.map((rec) => {
                  const style = getCategoryColor(rec.category);
                  return (
                    <tr
                      key={rec.id}
                      style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)', transition: 'background 0.2s' }}
                    >
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                        {new Date(rec.created_at).toLocaleString()}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                        {rec.height} {rec.height_unit}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                        {rec.weight} {rec.weight_unit}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: style.text }}>
                        {rec.bmi.toFixed(1)}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: style.bg,
                            color: style.text,
                            border: `1px solid ${style.border}`,
                          }}
                        >
                          {rec.category}
                        </span>
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

export default BMI;
