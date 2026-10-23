import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import Layout from '../components/Layout';
import RiskGauge from '../components/RiskGauge';
import SHAPContribution from '../components/SHAPContribution';
import ModelInfoCard from '../components/ModelInfoCard';
import { predictDiabetesProduction, getDiabetesHistory } from '../services/api';
import {
  Activity,
  Sparkles,
  RotateCcw,
  Info,
  User,
  HeartPulse,
  Clock,
  ShieldCheck,
  AlertCircle,
  TrendingUp,
  Cpu,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  History
} from 'lucide-react';

const DEFAULT_FORM = {
  gender: 'Female',
  age: '45',
  hypertension: '0',
  heart_disease: '0',
  smoking_history: 'never',
  bmi: '25.0',
  HbA1c_level: '5.5',
  blood_glucose_level: '100'
};

const DiabetesPrediction = () => {
  const { user } = useAuth();

  const [formData, setFormData] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);

  // Auto-populate from user profile if available
  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        gender: user.gender && ['Female', 'Male', 'Other'].includes(user.gender) ? user.gender : prev.gender,
        age: user.age ? String(user.age) : prev.age,
        bmi: user.weight && user.height ? (user.weight / Math.pow(user.height / 100, 2)).toFixed(1) : prev.bmi
      }));
    }
    fetchHistory();
  }, [user]);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setHistory([]);
      return;
    }
    try {
      const records = await getDiabetesHistory();
      if (Array.isArray(records)) setHistory(records);
    } catch (err) {
      console.warn("Could not load diabetes prediction history:", err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleReset = () => {
    setFormData(DEFAULT_FORM);
    setResult(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Range Validation
    const ageNum = parseFloat(formData.age);
    const bmiNum = parseFloat(formData.bmi);
    const hba1cNum = parseFloat(formData.HbA1c_level);
    const glucoseNum = parseFloat(formData.blood_glucose_level);

    if (isNaN(ageNum) || ageNum < 0.1 || ageNum > 80.0) {
      setError('Please enter a valid age between 0.1 and 80.0 years.');
      return;
    }
    if (isNaN(bmiNum) || bmiNum < 10.0 || bmiNum > 65.0) {
      setError('Please enter a valid BMI between 10.0 and 65.0 kg/m².');
      return;
    }
    if (isNaN(hba1cNum) || hba1cNum < 3.5 || hba1cNum > 9.0) {
      setError('Please enter a valid HbA1c level between 3.5% and 9.0%.');
      return;
    }
    if (isNaN(glucoseNum) || glucoseNum < 80 || glucoseNum > 300) {
      setError('Please enter a valid blood glucose level between 80 and 300 mg/dL.');
      return;
    }

    setLoading(true);
    setLoadingStep('Preparing clinical indicators...');

    try {
      const payload = {
        gender: formData.gender,
        age: ageNum,
        hypertension: parseInt(formData.hypertension, 10),
        heart_disease: parseInt(formData.heart_disease, 10),
        smoking_history: formData.smoking_history,
        bmi: bmiNum,
        HbA1c_level: hba1cNum,
        blood_glucose_level: Math.round(glucoseNum)
      };

      // Simulated smooth progress updates during real API call
      setTimeout(() => setLoadingStep('Executing production XGBoost model...'), 200);
      setTimeout(() => setLoadingStep('Calculating SHAP feature explanations...'), 400);

      const res = await predictDiabetesProduction(payload);
      setResult(res);
      fetchHistory();
    } catch (err) {
      console.error("Prediction API Error:", err);
      const errMsg = err.response?.data?.detail || err.message || 'Failed to generate risk prediction. Please try again.';
      setError(typeof errMsg === 'string' ? errMsg : JSON.stringify(errMsg));
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
        
        {/* PAGE HEADER */}
        <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/30 text-blue-300 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>CLINICAL DECISION SUPPORT</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Diabetes Risk Assessment
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-xl">
              Analyze key health indicators using our calibrated machine-learning prediction model.
            </p>
          </div>

          <button
            onClick={handleReset}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Inputs</span>
          </button>
        </div>

        {/* ERROR NOTIFICATION */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* INPUT FORM CONTAINER */}
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* SECTION 1: PERSONAL PROFILE */}
          <div className="health-card p-6 space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
                01
              </div>
              <h3 className="font-bold text-slate-900 text-base">Personal Profile</h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Gender Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Gender Identification *
                </label>
                <div className="segmented-control">
                  {['Female', 'Male', 'Other'].map(option => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, gender: option }))}
                      className={`segmented-option ${formData.gender === option ? 'active' : ''}`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>

              {/* Age Field */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Patient Age (Years) *
                </label>
                <input
                  type="number"
                  name="age"
                  step="0.1"
                  min="0.1"
                  max="80.0"
                  value={formData.age}
                  onChange={handleChange}
                  className="input-health"
                  placeholder="e.g. 45"
                  required
                />
                <p className="text-[11px] text-slate-500 mt-1">Valid range: 0.1 to 80.0 years</p>
              </div>
            </div>
          </div>

          {/* SECTION 2: CLINICAL INDICATORS */}
          <div className="health-card p-6 space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <div className="w-7 h-7 rounded-lg bg-cyan-50 text-cyan-600 flex items-center justify-center font-bold text-xs">
                02
              </div>
              <h3 className="font-bold text-slate-900 text-base">Clinical Measurements</h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              
              {/* Blood Glucose Level */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/60 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-800">Blood Glucose *</label>
                  <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono">mg/dL</span>
                </div>
                <input
                  type="number"
                  name="blood_glucose_level"
                  step="1"
                  min="80"
                  max="300"
                  value={formData.blood_glucose_level}
                  onChange={handleChange}
                  className="input-health text-lg font-bold"
                  required
                />
                <p className="text-[11px] text-slate-500">Fasting reference: &lt;100 mg/dL</p>
              </div>

              {/* HbA1c Level */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/60 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-800">HbA1c Level *</label>
                  <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono">%</span>
                </div>
                <input
                  type="number"
                  name="HbA1c_level"
                  step="0.1"
                  min="3.5"
                  max="9.0"
                  value={formData.HbA1c_level}
                  onChange={handleChange}
                  className="input-health text-lg font-bold"
                  required
                />
                <p className="text-[11px] text-slate-500">Normal reference: &lt;5.7%</p>
              </div>

              {/* BMI */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/60 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-800">Body Mass Index *</label>
                  <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono">kg/m²</span>
                </div>
                <input
                  type="number"
                  name="bmi"
                  step="0.1"
                  min="10.0"
                  max="65.0"
                  value={formData.bmi}
                  onChange={handleChange}
                  className="input-health text-lg font-bold"
                  required
                />
                <p className="text-[11px] text-slate-500">Normal range: 18.5 - 24.9 kg/m²</p>
              </div>

            </div>
          </div>

          {/* SECTION 3: MEDICAL HISTORY */}
          <div className="health-card p-6 space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <div className="w-7 h-7 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center font-bold text-xs">
                03
              </div>
              <h3 className="font-bold text-slate-900 text-base">Medical History & Factors</h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              
              {/* Hypertension Toggle */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Hypertension History *
                </label>
                <div className="segmented-control">
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, hypertension: '0' }))}
                    className={`segmented-option ${formData.hypertension === '0' ? 'active' : ''}`}
                  >
                    No (0)
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, hypertension: '1' }))}
                    className={`segmented-option ${formData.hypertension === '1' ? 'active' : ''}`}
                  >
                    Yes (1)
                  </button>
                </div>
              </div>

              {/* Heart Disease Toggle */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Heart Disease History *
                </label>
                <div className="segmented-control">
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, heart_disease: '0' }))}
                    className={`segmented-option ${formData.heart_disease === '0' ? 'active' : ''}`}
                  >
                    No (0)
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, heart_disease: '1' }))}
                    className={`segmented-option ${formData.heart_disease === '1' ? 'active' : ''}`}
                  >
                    Yes (1)
                  </button>
                </div>
              </div>

              {/* Smoking History Select */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Smoking History Status *
                </label>
                <select
                  name="smoking_history"
                  value={formData.smoking_history}
                  onChange={handleChange}
                  className="input-health font-medium"
                >
                  <option value="never">Never Smoked</option>
                  <option value="no info">No Info / Unknown</option>
                  <option value="current">Current Smoker</option>
                  <option value="former">Former Smoker</option>
                  <option value="ever">Ever Smoked</option>
                  <option value="not current">Not Current Smoker</option>
                </select>
              </div>

            </div>
          </div>

          {/* SUBMIT BUTTON */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 text-white font-extrabold text-base rounded-2xl shadow-xl shadow-blue-500/25 flex items-center justify-center gap-3 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>{loadingStep || 'Analyzing Clinical Risk...'}</span>
                </>
              ) : (
                <>
                  <span>Analyze My Risk →</span>
                  <Sparkles className="w-5 h-5 text-cyan-300" />
                </>
              )}
            </button>
          </div>

        </form>

        {/* RESULT PRESENTATION SECTION */}
        {result && (
          <div className="space-y-6 pt-6 animate-fade-in">
            
            {/* MAIN RESULT CARD */}
            <div className="health-card p-6 sm:p-8 space-y-6">
              
              <div className="flex flex-col sm:flex-row items-center justify-between gap-6 border-b border-slate-100 pb-6">
                <div>
                  <span className="badge-pill badge-blue mb-2">Risk Assessment Complete</span>
                  <h2 className="text-2xl font-extrabold text-slate-900">Your Model Risk Summary</h2>
                  <p className="text-xs text-slate-500 mt-1">Calculated via Isotonic Calibrated XGBoost Model</p>
                </div>

                <div className="flex-shrink-0">
                  <RiskGauge
                    probability={result.probability}
                    threshold={result.threshold || 0.30}
                    category={result.risk_category}
                  />
                </div>
              </div>

              {/* SHAP EXPLAINABLE AI SECTION */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-600" />
                    <span>Why did the model predict this?</span>
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">SHAP TreeExplainer</span>
                </div>

                <p className="text-xs text-slate-600">
                  Top contributing clinical factors that influenced the model prediction for this patient:
                </p>

                <SHAPContribution
                  features={result.top_contributing_features || result.shap_explanation || []}
                />
              </div>

              {/* CLINICAL DISCLAIMER */}
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1">
                <p className="font-bold flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-amber-600 flex-shrink-0" />
                  Medical Disclaimer
                </p>
                <p>
                  {result.disclaimer || 'This risk prediction is generated by a machine-learning decision-support model and does not constitute a medical diagnosis. Please consult a qualified healthcare professional.'}
                </p>
              </div>

            </div>

            {/* MODEL INSIGHT METADATA CARD */}
            <ModelInfoCard
              metadata={{
                algorithm: 'XGBoost Classifier',
                dataset_name: '100K Healthcare EHR Split',
                model_version: result.model_version || '2.0.0',
                features: new Array(8),
                metrics: { roc_auc: 0.9985 },
                external_validation_status: 'Verified Benchmark'
              }}
            />

          </div>
        )}

        {/* RECENT HISTORY DRAWER TOGGLE */}
        {history.length > 0 && (
          <div className="health-card p-4">
            <button
              onClick={() => setHistoryOpen(!historyOpen)}
              className="w-full flex items-center justify-between text-xs font-bold text-slate-700"
            >
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-blue-600" />
                <span>Recent Prediction History ({history.length} Saved Records)</span>
              </div>
              {historyOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {historyOpen && (
              <div className="mt-4 space-y-2 border-t border-slate-100 pt-3 text-xs">
                {history.slice(0, 5).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg">
                    <div>
                      <span className="font-bold text-slate-800">
                        {item.risk_category || item.risk} ({(item.probability * 100).toFixed(1)}%)
                      </span>
                      <span className="text-[10px] text-slate-400 block">
                        {item.prediction_date ? new Date(item.prediction_date).toLocaleString() : 'Recent'}
                      </span>
                    </div>
                    <span className="text-slate-500 font-mono">
                      Glucose: {item.blood_glucose_level} | HbA1c: {item.HbA1c_level}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
  );
};

export default DiabetesPrediction;
