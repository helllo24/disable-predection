import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import {
  createExerciseRecommendation,
  getLatestExerciseRecommendation,
  getExerciseRecommendationHistory
} from '../services/api';
import {
  Dumbbell,
  AlertCircle,
  ShieldAlert,
  History,
  Clock,
  CheckCircle2,
  Calendar,
  Zap,
  Activity,
  HeartPulse
} from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const ExerciseRecommendation = () => {
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    fitness_level: 'Beginner',
    goal: 'General Fitness',
  });

  const [currentRec, setCurrentRec] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    try {
      setLoadingInitial(true);
      const [latest, hist] = await Promise.all([
        getLatestExerciseRecommendation(),
        getExerciseRecommendationHistory(),
      ]);
      setCurrentRec(latest);
      setHistory(hist || []);
    } catch (err) {
      console.error('Failed to load exercise recommendation data:', err);
    } finally {
      setLoadingInitial(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await createExerciseRecommendation(formData);
      setCurrentRec(res);
      const updatedHist = await getExerciseRecommendationHistory();
      setHistory(updatedHist || []);
    } catch (err) {
      setError(err.message || 'Failed to generate exercise recommendation.');
    } finally {
      setLoading(false);
    }
  };

  const recs = currentRec ? currentRec.recommendations : null;

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
              <Dumbbell size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Personalized Exercise Guidance
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Rule-based physical activity & workout routines tailored to your fitness level, goals, and age demographic
              </p>
            </div>
          </div>

          <PageGuideModal
            title="Personalized Physical Activity Plan"
            purpose="Recommends tailored exercise routines and workout intensity levels based on fitness experience, age, and health conditions."
            howItWorks={[
              "Evaluates fitness level (Beginner, Intermediate, Advanced) and target health outcome.",
              "Computes safe target heart rate zones and outputs weekly workout schedules (Cardio, Strength, Flexibility) adjusted for diabetic safety."
            ]}
            howToUse={[
              "Select your current activity level and primary fitness goal.",
              "Indicate available workout time per day.",
              "Click 'Get Exercise Plan' to view your customized weekly activity guide."
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

      {/* Main Grid: Input Form & Recommendation Output */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2.5rem',
        }}
      >
        {/* Form Selection Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            Select Fitness Parameters
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Current Fitness Level</label>
              <select
                name="fitness_level"
                className="form-input"
                value={formData.fitness_level}
                onChange={handleChange}
                required
              >
                <option value="Beginner">Beginner (New to exercise / light activity)</option>
                <option value="Intermediate">Intermediate (Active 2-3 times/week)</option>
                <option value="Advanced">Advanced (Regular structured training)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Primary Fitness Goal</label>
              <select
                name="goal"
                className="form-input"
                value={formData.goal}
                onChange={handleChange}
                required
              >
                <option value="General Fitness">General Fitness & Overall Wellness</option>
                <option value="Weight Management">Weight Management & Calorie Burn</option>
                <option value="Mobility">Mobility, Flexibility & Joint Health</option>
                <option value="Strength">Strength & Muscle Endurance</option>
              </select>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem' }}
              disabled={loading}
            >
              {loading ? 'Generating Routine Plan...' : 'Generate Exercise Plan'}
            </button>
          </form>

          {/* Mandated Safety Inclusion */}
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
              <strong>Mandated Safety Note:</strong> Consult a healthcare professional before starting a new exercise program, especially if you have a medical condition.
            </span>
          </div>
        </div>

        {/* Recommendation Results Display Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            Exercise Guidance Plan Output
          </h2>

          {recs ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* Recommended Activities */}
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: '0.5rem' }}>
                  Recommended Physical Activities:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {recs.recommended_activities && recs.recommended_activities.map((act, idx) => (
                    <span
                      key={`act-${idx}`}
                      style={{
                        fontSize: '0.8rem',
                        padding: '0.3rem 0.65rem',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'rgba(20, 184, 166, 0.15)',
                        color: 'var(--primary-500)',
                        border: '1px solid rgba(20, 184, 166, 0.3)',
                        fontWeight: 600,
                      }}
                    >
                      {act}
                    </span>
                  ))}
                </div>
              </div>

              {/* Prescription Guidance Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.75rem' }}>
                <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                  <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                    <Calendar size={16} /> Recommended Frequency:
                  </strong>
                  <span style={{ color: 'var(--text-main)' }}>{recs.frequency_guidance}</span>
                </div>

                <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                  <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                    <Clock size={16} /> Target Duration:
                  </strong>
                  <span style={{ color: 'var(--text-main)' }}>{recs.duration_guidance}</span>
                </div>

                <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                  <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                    <Zap size={16} /> Target Intensity:
                  </strong>
                  <span style={{ color: 'var(--text-main)' }}>{recs.intensity_guidance}</span>
                </div>
              </div>

              {/* Safety Guidelines List */}
              {recs.safety_notes && (
                <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '0.5rem' }}>
                    Safety Guidelines & Warm-Up Notes:
                  </span>
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, color: 'var(--text-muted)' }}>
                    {recs.safety_notes.map((note, i) => (
                      <li key={`note-${i}`} style={{ marginBottom: '0.25rem' }}>{note}</li>
                    ))}
                  </ul>
                </div>
              )}
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
              <Dumbbell size={44} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
              <p>Select your fitness parameters on the left to generate personalized exercise guidance.</p>
            </div>
          )}
        </div>
      </div>

      {/* Exercise History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--primary-500)' }} />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Exercise Recommendation History
            </h2>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {history.length} Plan{history.length !== 1 ? 's' : ''} Stored
          </span>
        </div>

        {loadingInitial ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            Loading exercise history...
          </p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Clock size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 500 }}>No exercise recommendation history found.</p>
            <span style={{ fontSize: '0.85rem' }}>Generate an exercise plan above to record your first recommendation.</span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Fitness Level</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Fitness Goal</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Prescribed Activities</th>
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
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: 'var(--primary-500)' }}>
                      {rec.fitness_level}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                      {rec.goal}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                      {rec.recommendations && rec.recommendations.recommended_activities
                        ? rec.recommendations.recommended_activities.slice(0, 3).join(', ')
                        : 'Activities'}
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

export default ExerciseRecommendation;
