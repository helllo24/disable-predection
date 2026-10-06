import React, { useState, useEffect } from 'react';
import { predictDisease, getDiseaseHistory, getSupportedSymptoms } from '../services/api';
import {
  Stethoscope,
  AlertCircle,
  History,
  ShieldAlert,
  Cpu,
  Search,
  Check,
  X,
  Clock,
  CheckCircle2
} from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

// Utility helper to format raw symptom snake_case to user-friendly Title Case
const formatSymptomName = (sym) => {
  if (!sym) return '';
  return sym
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
};

const DiseasePrediction = () => {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingSymptoms, setLoadingSymptoms] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Quick preset common symptoms
  const commonPresets = [
    'itching', 'skin_rash', 'continuous_sneezing', 'joint_pain',
    'stomach_pain', 'vomiting', 'fatigue', 'fever', 'cough',
    'headache', 'chest_pain', 'chills', 'acidity', 'nausea'
  ];

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoadingSymptoms(true);
        const syms = await getSupportedSymptoms();
        setAllSymptoms(syms || []);
      } catch (err) {
        console.error('Failed to load supported symptoms:', err);
        // Fallback default symptoms list
        setAllSymptoms(commonPresets);
      } finally {
        setLoadingSymptoms(false);
      }

      try {
        setLoadingHistory(true);
        const historyData = await getDiseaseHistory();
        setHistory(historyData || []);
        if (historyData && historyData.length > 0 && !result) {
          setResult(historyData[0]); // Default to latest prediction
        }
      } catch (err) {
        console.error('Failed to load disease history:', err);
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchInitialData();
  }, []);

  const toggleSymptom = (sym) => {
    setError('');
    if (selectedSymptoms.includes(sym)) {
      setSelectedSymptoms(selectedSymptoms.filter((s) => s !== sym));
    } else {
      setSelectedSymptoms([...selectedSymptoms, sym]);
    }
  };

  const handleClearAll = () => {
    setSelectedSymptoms([]);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (selectedSymptoms.length === 0) {
      setError('Please select at least one symptom to run disease prediction.');
      return;
    }

    setLoading(true);

    try {
      const res = await predictDisease({ symptoms: selectedSymptoms });
      setResult(res);
      setLoading(false); // Unblock UI & reset button state instantly!
      getDiseaseHistory().then((updatedHistory) => {
        setHistory(updatedHistory || []);
      }).catch(err => console.error('Background history update error:', err));
    } catch (err) {
      setError(err.message || 'Failed to predict disease. Please try again.');
      setLoading(false);
    }
  };

  const filteredSymptoms = allSymptoms.filter((sym) =>
    formatSymptomName(sym).toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div style={{ maxWidth: 1050, margin: '0 auto' }}>
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
              <Stethoscope size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                AI Multi-Class Disease Prediction
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Select patient symptoms to evaluate probability across 41 clinical conditions using trained ML classification models
              </p>
            </div>
          </div>

          <PageGuideModal
            title="AI Multi-Class Disease Prediction"
            purpose="Analyzes user-selected symptoms to evaluate diagnostic probability across 41 common clinical diseases using a Multi-Class Logistic Regression model trained on 132 symptoms."
            howItWorks={[
              "Takes user-selected symptoms and converts them into a 132-element binary symptom vector.",
              "Evaluates the vector through trained Multi-Class Logistic Regression model.",
              "Returns top-matching disease, prediction confidence percentage, disease summary, and precautions.",
              "Logs evaluation result to patient history for long-term health tracking."
            ]}
            howToUse={[
              "Search or click symptom chips (e.g., fever, cough, joint pain, fatigue) to select your symptoms.",
              "Click 'Run Disease Prediction' to analyze.",
              "View predicted disease, confidence level, descriptions, and recommended precautions."
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

      {/* Main Grid: Symptom Selector & Prediction Output */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2.5rem',
        }}
      >
        {/* Symptom Selection Panel */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Select Patient Symptoms ({selectedSymptoms.length})
            </h2>
            {selectedSymptoms.length > 0 && (
              <button
                type="button"
                onClick={handleClearAll}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--accent-red)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                }}
              >
                Clear All
              </button>
            )}
          </div>

          {/* Search Box */}
          <div style={{ position: 'relative', marginBottom: '1rem' }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: '2.25rem' }}
              placeholder="Search symptoms (e.g. Fever, Cough, Headache)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Quick Common Presets */}
          <div style={{ marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Frequent Symptoms:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
              {commonPresets.map((sym) => {
                const isSelected = selectedSymptoms.includes(sym);
                return (
                  <button
                    key={`preset-${sym}`}
                    type="button"
                    onClick={() => toggleSymptom(sym)}
                    style={{
                      fontSize: '0.75rem',
                      padding: '0.25rem 0.6rem',
                      borderRadius: 12,
                      border: isSelected ? '1px solid var(--primary-500)' : '1px solid var(--border-color)',
                      backgroundColor: isSelected ? 'rgba(20, 184, 166, 0.2)' : 'rgba(30, 45, 74, 0.4)',
                      color: isSelected ? 'var(--primary-500)' : 'var(--text-muted)',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    {isSelected ? '✓ ' : '+ '}{formatSymptomName(sym)}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Selected Symptoms Badges */}
          {selectedSymptoms.length > 0 && (
            <div style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--primary-500)', fontWeight: 600, display: 'block', marginBottom: '0.4rem' }}>
                Selected Symptoms ({selectedSymptoms.length}):
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                {selectedSymptoms.map((sym) => (
                  <span
                    key={`selected-${sym}`}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      fontSize: '0.75rem',
                      padding: '0.2rem 0.55rem',
                      borderRadius: 10,
                      backgroundColor: 'rgba(20, 184, 166, 0.25)',
                      color: 'var(--text-main)',
                      border: '1px solid rgba(20, 184, 166, 0.4)',
                    }}
                  >
                    {formatSymptomName(sym)}
                    <X size={12} style={{ cursor: 'pointer' }} onClick={() => toggleSymptom(sym)} />
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Symptom Checklist Window */}
          <div
            style={{
              maxHeight: 240,
              overflowY: 'auto',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.5rem',
              backgroundColor: 'rgba(15, 23, 42, 0.4)',
              marginBottom: '1.25rem',
            }}
          >
            {loadingSymptoms ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '1rem' }}>
                Loading symptom checklist...
              </p>
            ) : filteredSymptoms.length === 0 ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '1rem' }}>
                No symptoms matching "{searchQuery}".
              </p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.25rem' }}>
                {filteredSymptoms.map((sym) => {
                  const isChecked = selectedSymptoms.includes(sym);
                  return (
                    <label
                      key={sym}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.35rem 0.6rem',
                        borderRadius: 'var(--radius-sm)',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        backgroundColor: isChecked ? 'rgba(20, 184, 166, 0.12)' : 'transparent',
                        color: isChecked ? 'var(--primary-500)' : 'var(--text-main)',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleSymptom(sym)}
                        style={{ accentColor: 'var(--primary-500)' }}
                      />
                      <span>{formatSymptomName(sym)}</span>
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          <button
            type="button"
            className="btn btn-primary"
            style={{ width: '100%' }}
            onClick={handleSubmit}
            disabled={loading || selectedSymptoms.length === 0}
          >
            {loading ? 'Running ML Inference...' : 'Predict Disease Condition'}
          </button>

          {/* Medical Disclaimer */}
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
              <strong>Medical Disclaimer:</strong> This prediction is generated by a machine-learning model for informational purposes and is not a medical diagnosis. Please consult a qualified healthcare professional for proper evaluation.
            </span>
          </div>
        </div>

        {/* Prediction Result Display Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'between' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            ML Disease Assessment Result
          </h2>

          {result ? (
            <div>
              <div
                style={{
                  textAlign: 'center',
                  padding: '1.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'rgba(15, 23, 42, 0.85)',
                  border: '1px solid var(--primary-700)',
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
                    fontSize: '1.65rem',
                    fontWeight: 800,
                    color: 'var(--primary-500)',
                    marginBottom: '0.5rem',
                  }}
                >
                  {result.predicted_disease}
                </div>

                {/* Mandated exact wording constraint */}
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.25rem', padding: '0 0.5rem' }}>
                  The model predicts this condition based on the selected symptoms.
                </p>

                {/* Confidence Bar */}
                <div style={{ maxWidth: 300, margin: '0 auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Confidence Score</span>
                    <strong style={{ color: 'var(--primary-500)' }}>{(result.probability * 100).toFixed(1)}%</strong>
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
                        width: `${Math.min(100, Math.max(10, result.probability * 100))}%`,
                        backgroundColor: 'var(--primary-500)',
                        transition: 'width 0.5s ease',
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Symptoms Evaluated Snapshot */}
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.5)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  fontSize: '0.825rem',
                }}
              >
                <span style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                  Evaluated Symptoms ({result.symptoms ? result.symptoms.length : 0}):
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {result.symptoms && result.symptoms.map((sym) => (
                    <span
                      key={`eval-${sym}`}
                      style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: 8,
                        backgroundColor: 'rgba(30, 45, 74, 0.6)',
                        color: 'var(--text-main)',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      {formatSymptomName(sym)}
                    </span>
                  ))}
                </div>

                {result.created_at && (
                  <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.75rem', color: 'var(--text-muted)' }}>
                    Assessment Time: <strong>{new Date(result.created_at).toLocaleString()}</strong>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div
              style={{
                textAlign: 'center',
                padding: '4rem 1rem',
                color: 'var(--text-muted)',
                backgroundColor: 'rgba(15, 23, 42, 0.4)',
                borderRadius: 'var(--radius-md)',
                border: '1px dashed var(--border-color)',
              }}
            >
              <Stethoscope size={44} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
              <p>Select symptoms on the left to evaluate potential medical conditions.</p>
            </div>
          )}
        </div>
      </div>

      {/* Disease Prediction History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--primary-500)' }} />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Disease Prediction History
            </h2>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {history.length} Record{history.length !== 1 ? 's' : ''} Stored
          </span>
        </div>

        {loadingHistory ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            Loading prediction history...
          </p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Clock size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 500 }}>No disease prediction history found.</p>
            <span style={{ fontSize: '0.85rem' }}>Run a prediction above to record your first assessment.</span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Selected Symptoms</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Predicted Disease</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Confidence</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Model</th>
                </tr>
              </thead>
              <tbody>
                {history.map((rec) => (
                  <tr
                    key={rec.id}
                    style={{ borderBottom: '1px solid rgba(30, 45, 74, 0.5)', transition: 'background 0.2s' }}
                  >
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                      {new Date(rec.created_at).toLocaleString()}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', maxWidth: 260 }}>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.2rem' }}>
                        {rec.symptoms && rec.symptoms.slice(0, 4).map((s) => (
                          <span
                            key={`hist-sym-${rec.id}-${s}`}
                            style={{
                              fontSize: '0.725rem',
                              padding: '0.15rem 0.4rem',
                              borderRadius: 6,
                              backgroundColor: 'rgba(30, 45, 74, 0.6)',
                              color: 'var(--text-muted)',
                            }}
                          >
                            {formatSymptomName(s)}
                          </span>
                        ))}
                        {rec.symptoms && rec.symptoms.length > 4 && (
                          <span style={{ fontSize: '0.725rem', color: 'var(--primary-500)', fontWeight: 600 }}>
                            +{rec.symptoms.length - 4} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: 'var(--primary-500)' }}>
                      {rec.predicted_disease}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: 'var(--accent-green)' }}>
                      {(rec.probability * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                      {rec.model}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiseasePrediction;
