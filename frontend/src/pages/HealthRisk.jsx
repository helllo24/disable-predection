import React, { useState, useEffect } from 'react';
import { calculateHealthRisk, getHealthRiskHistory, getLatestHealthRisk } from '../services/api';
import { TrendingUp, AlertCircle, ShieldAlert, History, Clock, CheckCircle2, Award, Info } from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const HealthRisk = () => {
  const [currentScore, setCurrentScore] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [error, setError] = useState('');

  const fetchScoreData = async () => {
    try {
      setLoadingInitial(true);
      const [latest, hist] = await Promise.all([
        getLatestHealthRisk(),
        getHealthRiskHistory(),
      ]);
      setCurrentScore(latest);
      setHistory(hist || []);
    } catch (err) {
      console.error('Failed to load health risk data:', err);
    } finally {
      setLoadingInitial(false);
    }
  };

  useEffect(() => {
    fetchScoreData();
  }, []);

  const handleCalculate = async () => {
    setError('');
    setLoading(true);

    try {
      const res = await calculateHealthRisk();
      setCurrentScore(res);
      const updatedHist = await getHealthRiskHistory();
      setHistory(updatedHist || []);
    } catch (err) {
      setError(err.message || 'Failed to compute health risk score.');
    } finally {
      setLoading(false);
    }
  };

  // Color mappings based on category/score
  const getCategoryStyles = (cat, scoreVal) => {
    if (cat === 'High Risk' || scoreVal >= 67) {
      return {
        color: '#ef4444',
        bg: 'rgba(239, 68, 68, 0.15)',
        border: 'rgba(239, 68, 68, 0.3)',
      };
    } else if (cat === 'Moderate Risk' || scoreVal >= 34) {
      return {
        color: '#f59e0b',
        bg: 'rgba(245, 158, 11, 0.15)',
        border: 'rgba(245, 158, 11, 0.3)',
      };
    } else {
      return {
        color: '#10b981',
        bg: 'rgba(16, 185, 129, 0.15)',
        border: 'rgba(16, 185, 129, 0.3)',
      };
    }
  };

  const currentStyles = currentScore
    ? getCategoryStyles(currentScore.category, currentScore.score)
    : { color: 'var(--primary-500)', bg: 'rgba(20, 184, 166, 0.15)', border: 'rgba(20, 184, 166, 0.3)' };

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
              <TrendingUp size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Composite Health Risk Score
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Transparent scoring methodology evaluating age demographics, BMI profile, and AI ML predictions
              </p>
            </div>
          </div>

          <PageGuideModal
            title="Composite Health Risk Score"
            purpose="Calculates an explainable 0–100 total health risk score for the patient by combining age demographics, BMI category, primary diabetes ML prediction, and multi-class disease ML prediction."
            howItWorks={[
              "Age Demographics (Max 20 pts): Age ≥60 (+20 pts), Age 45-59 (+10 pts), Age <45 (+0 pts).",
              "Body Mass Index (Max 25 pts): Obese ≥30 (+25 pts), Overweight ≥25 (+15 pts), Underweight <18.5 (+10 pts).",
              "Diabetes ML Risk (Max 35 pts): Points = Diabetes Probability × 35.",
              "Disease ML Risk (Max 20 pts): Points = Disease Confidence × 20.",
              "Categories: 0-33 Low Risk (Green), 34-66 Moderate Risk (Amber), 67-100 High Risk (Red)."
            ]}
            howToUse={[
              "Ensure your Age is filled in your Patient Profile.",
              "Calculate your BMI using the BMI Calculator module.",
              "Run the Diabetes Risk Assessment and Disease Risk Prediction modules.",
              "Click 'Recalculate Health Risk Score' to generate your overall score and view factor breakdown."
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

      {/* Main Grid: Score Gauge & Breakdown */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2.5rem',
        }}
      >
        {/* Score Visual Gauge Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
              Risk Score Indicator
            </h2>

            {currentScore ? (
              <div style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
                {/* Circular Score Gauge representation */}
                <div
                  style={{
                    position: 'relative',
                    width: 170,
                    height: 170,
                    borderRadius: '50%',
                    background: `conic-gradient(${currentStyles.color} ${currentScore.score * 3.6}deg, rgba(30, 45, 74, 0.6) 0deg)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.25rem',
                    boxShadow: `0 0 20px ${currentStyles.bg}`,
                  }}
                >
                  <div
                    style={{
                      width: 140,
                      height: 140,
                      borderRadius: '50%',
                      backgroundColor: 'var(--card-bg)',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <span style={{ fontSize: '2.5rem', fontWeight: 800, color: currentStyles.color, lineHeight: 1 }}>
                      {currentScore.score}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1 }}>
                      out of 100
                    </span>
                  </div>
                </div>

                <div
                  style={{
                    display: 'inline-block',
                    padding: '0.4rem 1.25rem',
                    borderRadius: 20,
                    backgroundColor: currentStyles.bg,
                    color: currentStyles.color,
                    border: `1px solid ${currentStyles.border}`,
                    fontWeight: 700,
                    fontSize: '1.1rem',
                    marginBottom: '0.75rem',
                  }}
                >
                  {currentScore.category}
                </div>

                {currentScore.created_at && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Calculated on {new Date(currentScore.created_at).toLocaleString()}
                  </p>
                )}
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
                  marginBottom: '1rem',
                }}
              >
                <TrendingUp size={44} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
                <p style={{ fontWeight: 500 }}>Not calculated yet</p>
                <span style={{ fontSize: '0.85rem' }}>Click below to generate your composite risk score.</span>
              </div>
            )}
          </div>

          <button
            type="button"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem' }}
            onClick={handleCalculate}
            disabled={loading}
          >
            {loading ? 'Computing Risk Factors...' : 'Recalculate Health Risk Score'}
          </button>
        </div>

        {/* Contributing Factors Breakdown Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            Main Contributing Factors
          </h2>

          {currentScore && currentScore.contributing_factors ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {currentScore.contributing_factors.map((item, idx) => (
                <div
                  key={`factor-${idx}`}
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)', display: 'block' }}>
                      {item.factor}
                    </strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {item.detail}
                    </span>
                  </div>
                  <div
                    style={{
                      fontSize: '0.9rem',
                      fontWeight: 700,
                      color: item.points > 0 ? 'var(--accent-amber)' : 'var(--primary-500)',
                      backgroundColor: 'rgba(30, 45, 74, 0.6)',
                      padding: '0.25rem 0.6rem',
                      borderRadius: 6,
                      minWidth: 55,
                      textAlign: 'center',
                    }}
                  >
                    +{item.points} pt{item.points !== 1 ? 's' : ''}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', padding: '2rem 0', textAlign: 'center' }}>
              Contributing factor breakdown will appear here after calculation.
            </p>
          )}

          {/* Mandated Safety Disclaimer */}
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
              <strong>Safety Disclaimer:</strong> This score is an informational estimate and is not a medical diagnosis or clinically validated risk assessment. Please consult a qualified healthcare professional for proper medical evaluation.
            </span>
          </div>
        </div>
      </div>

      {/* Health Risk History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--primary-500)' }} />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Health Risk Score History
            </h2>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {history.length} Assessment{history.length !== 1 ? 's' : ''} Stored
          </span>
        </div>

        {loadingInitial ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            Loading risk score history...
          </p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Clock size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 500 }}>No health risk score calculated yet.</p>
            <span style={{ fontSize: '0.85rem' }}>Click recalculate above to compute your score.</span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Risk Score</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Category</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Main Factors Count</th>
                </tr>
              </thead>
              <tbody>
                {history.map((rec) => {
                  const st = getCategoryStyles(rec.category, rec.score);
                  return (
                    <tr
                      key={rec.id}
                      style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)', transition: 'background 0.2s' }}
                    >
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                        {new Date(rec.created_at).toLocaleString()}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 800, fontSize: '1rem', color: st.color }}>
                        {rec.score} / 100
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: st.bg,
                            color: st.color,
                            border: `1px solid ${st.border}`,
                          }}
                        >
                          {rec.category}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                        {rec.contributing_factors ? rec.contributing_factors.length : 0} Factors Analyzed
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

export default HealthRisk;
