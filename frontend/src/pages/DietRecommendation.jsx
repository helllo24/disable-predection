import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import {
  createDietRecommendation,
  getLatestDietRecommendation,
  getDietRecommendationHistory
} from '../services/api';
import {
  Utensils,
  AlertCircle,
  ShieldAlert,
  History,
  Clock,
  CheckCircle2,
  XCircle,
  Droplet,
  Coffee,
  Sun,
  Moon,
  Cookie
} from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const DietRecommendation = () => {
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    dietary_preference: 'Vegetarian',
    goal: 'Weight Management',
    custom_allergies: '',
  });

  const [currentRec, setCurrentRec] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [error, setError] = useState('');

  // Pre-fill allergies from user profile if available
  useEffect(() => {
    if (user && user.allergies) {
      setFormData((prev) => ({
        ...prev,
        custom_allergies: user.allergies,
      }));
    }
  }, [user]);

  const fetchData = async () => {
    try {
      setLoadingInitial(true);
      const [latest, hist] = await Promise.all([
        getLatestDietRecommendation(),
        getDietRecommendationHistory(),
      ]);
      setCurrentRec(latest);
      setHistory(hist || []);
    } catch (err) {
      console.error('Failed to load diet recommendation data:', err);
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
      const res = await createDietRecommendation(formData);
      setCurrentRec(res);
      const updatedHist = await getDietRecommendationHistory();
      setHistory(updatedHist || []);
    } catch (err) {
      setError(err.message || 'Failed to generate diet recommendation.');
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
              <Utensils size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Personalized Diet Guidance
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Rule-based informational dietary recommendations tailored to your preferences, goals, and health profile
              </p>
            </div>
          </div>

          <PageGuideModal
            title="Personalized Diet & Nutrition Guidance"
            purpose="Generates customized dietary recommendations based on dietary preferences, health goals, and medical conditions (e.g. Diabetes, Hypertension)."
            howItWorks={[
              "Processes user preferences (Veg/Non-Veg/Vegan, Weight Loss/Maintenance, Diabetes management).",
              "Applies clinical nutrition guidelines to recommend daily calorie targets, macronutrient split (Carbs, Protein, Fats), foods to embrace, and foods to limit."
            ]}
            howToUse={[
              "Select your diet type (Vegetarian, Vegan, Non-Vegetarian, Low Carb).",
              "Choose primary health goal and specify medical conditions.",
              "Click 'Generate Diet Plan' to receive daily meal suggestions and nutritional rules."
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
            Select Dietary Preferences
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Dietary Preference</label>
              <select
                name="dietary_preference"
                className="form-input"
                value={formData.dietary_preference}
                onChange={handleChange}
                required
              >
                <option value="Vegetarian">Vegetarian (Plant-based + Dairy/Eggs)</option>
                <option value="Non-Vegetarian">Non-Vegetarian (Includes Poultry/Fish/Meat)</option>
                <option value="Vegan">Vegan (Strictly 100% Plant-Based)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Primary Health Goal</label>
              <select
                name="goal"
                className="form-input"
                value={formData.goal}
                onChange={handleChange}
                required
              >
                <option value="Weight Management">Weight Management & Balanced Nutrition</option>
                <option value="Weight Loss">Weight Loss & Fat Reduction</option>
                <option value="General Healthy Eating">General Healthy Eating & Vitality</option>
                <option value="Weight Gain">Weight Gain & Muscle Building</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Food Allergies / Intolerances</label>
              <input
                type="text"
                name="custom_allergies"
                className="form-input"
                placeholder="e.g. Dairy, Nuts, Gluten, Eggs, Soy"
                value={formData.custom_allergies}
                onChange={handleChange}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                Separate multiple food allergies with commas.
              </span>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem' }}
              disabled={loading}
            >
              {loading ? 'Generating Guidance Plan...' : 'Generate Diet Guidance'}
            </button>
          </form>

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
              <strong>Safety Guidance:</strong> This diet recommendation is for general informational and educational guidance only and is not a medical nutrition prescription. Please consult a registered dietitian or healthcare professional for medical nutrition therapy.
            </span>
          </div>
        </div>

        {/* Recommendation Results Display Card */}
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-main)' }}>
            Dietary Guidance Output
          </h2>

          {recs ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* Recommended Food Groups */}
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: '0.5rem' }}>
                  Recommended Food Groups:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {recs.recommended_food_groups && recs.recommended_food_groups.map((group, idx) => (
                    <span
                      key={`group-${idx}`}
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
                      {group}
                    </span>
                  ))}
                </div>
              </div>

              {/* Foods to Consider vs Foods to Limit Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#10b981', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                    <CheckCircle2 size={16} />
                    <span>Foods to Consider</span>
                  </div>
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.8rem', color: 'var(--text-main)' }}>
                    {recs.foods_to_consider && recs.foods_to_consider.map((food, i) => (
                      <li key={`consider-${i}`} style={{ marginBottom: '0.25rem' }}>{food}</li>
                    ))}
                  </ul>
                </div>

                <div style={{ background: 'rgba(239, 68, 68, 0.08)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#ef4444', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                    <XCircle size={16} />
                    <span>Foods to Limit</span>
                  </div>
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.8rem', color: 'var(--text-main)' }}>
                    {recs.foods_to_limit && recs.foods_to_limit.map((food, i) => (
                      <li key={`limit-${i}`} style={{ marginBottom: '0.25rem' }}>{food}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Sample Meal Ideas */}
              {recs.general_meal_ideas && (
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '0.65rem' }}>
                    General Sample Meal Ideas:
                  </span>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem' }}>
                    <div>
                      <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Coffee size={14} /> Breakfast:
                      </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{recs.general_meal_ideas.breakfast}</span>
                    </div>

                    <div>
                      <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Sun size={14} /> Lunch:
                      </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{recs.general_meal_ideas.lunch}</span>
                    </div>

                    <div>
                      <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Moon size={14} /> Dinner:
                      </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{recs.general_meal_ideas.dinner}</span>
                    </div>

                    <div>
                      <strong style={{ color: 'var(--primary-500)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Cookie size={14} /> Snacks:
                      </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{recs.general_meal_ideas.snacks}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Hydration Guidance Card */}
              {recs.hydration_guidance && (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'rgba(59, 130, 246, 0.12)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    color: 'var(--text-main)',
                    fontSize: '0.85rem',
                  }}
                >
                  <Droplet size={22} style={{ color: '#3b82f6', minWidth: 22 }} />
                  <div>
                    <strong style={{ color: '#3b82f6', display: 'block', fontSize: '0.85rem' }}>Hydration Guidance</strong>
                    <span style={{ color: 'var(--text-muted)' }}>{recs.hydration_guidance}</span>
                  </div>
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
              <Utensils size={44} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
              <p>Select your preferences on the left to generate personalized diet guidance.</p>
            </div>
          )}
        </div>
      </div>

      {/* Diet History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} style={{ color: 'var(--primary-500)' }} />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Diet Recommendation History
            </h2>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {history.length} Guidance Plan{history.length !== 1 ? 's' : ''} Stored
          </span>
        </div>

        {loadingInitial ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            Loading diet history...
          </p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Clock size={32} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 500 }}>No diet recommendation history found.</p>
            <span style={{ fontSize: '0.85rem' }}>Generate a diet plan above to record your first recommendation.</span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Preference</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Health Goal</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Allergies Excluded</th>
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
                      {rec.dietary_preference}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                      {rec.goal}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>
                      {rec.allergies ? rec.allergies : 'None'}
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

export default DietRecommendation;
