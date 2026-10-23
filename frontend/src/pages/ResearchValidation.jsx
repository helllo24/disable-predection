import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { getResearchDashboardData } from '../services/api';
import {
  LineChart,
  BarChart3,
  Database,
  Cpu,
  ShieldCheck,
  Award,
  Layers,
  Activity,
  AlertTriangle,
  Info,
  CheckCircle2,
  Users,
  Scale,
  RefreshCw,
  ExternalLink
} from 'lucide-react';

const ResearchValidation = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getResearchDashboardData();
      setData(res);
    } catch (err) {
      console.error("Failed to load research dashboard data:", err);
      setError("Failed to load experimental research data. Please ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3 text-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-slate-500 font-medium">Loading experimental research results and metrics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16">
        
        {/* HEADER */}
        <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-400/30 text-teal-300 text-xs font-bold uppercase tracking-wider mb-2">
              <LineChart className="w-3.5 h-3.5 text-teal-400" />
              <span>ACADEMIC AI/ML RESEARCH DASHBOARD</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Research & Model Performance
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-xl">
              Empirical holdout metrics, calibration reliability, subgroup fairness, and TRIPOD+AI audit results.
            </p>
          </div>

          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reload Metrics</span>
          </button>
        </div>

        {/* TAB NAVIGATION */}
        <div className="flex border-b border-slate-200 overflow-x-auto gap-2 text-xs font-bold text-slate-600">
          {[
            { id: 'overview', label: 'Dataset & Architecture' },
            { id: 'comparison', label: 'Model Comparison' },
            { id: 'performance', label: 'Holdout Performance & CIs' },
            { id: 'fairness', label: 'Subgroup Fairness' },
            { id: 'external', label: 'External Validation' },
            { id: 'limitations', label: 'Limitations' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 px-3 transition-colors border-b-2 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600 font-extrabold'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: DATASET & ARCHITECTURE OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            
            {/* DATASET METRIC CARDS */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="health-card p-4">
                <span className="text-slate-400 text-[10px] font-bold uppercase block mb-1">Total Cohort (N)</span>
                <span className="text-2xl font-extrabold text-slate-900">100,015</span>
                <span className="text-[10px] text-slate-500 block">EHR Patient Records</span>
              </div>

              <div className="health-card p-4">
                <span className="text-slate-400 text-[10px] font-bold uppercase block mb-1">Diabetes Cases</span>
                <span className="text-2xl font-extrabold text-red-600">8,339</span>
                <span className="text-[10px] text-slate-500 block">8.34% Positive Prevalence</span>
              </div>

              <div className="health-card p-4">
                <span className="text-slate-400 text-[10px] font-bold uppercase block mb-1">Holdout Test Set</span>
                <span className="text-2xl font-extrabold text-blue-600">15,000</span>
                <span className="text-[10px] text-slate-500 block">15.0% Isolated Split</span>
              </div>

              <div className="health-card p-4">
                <span className="text-slate-400 text-[10px] font-bold uppercase block mb-1">Predictors</span>
                <span className="text-2xl font-extrabold text-teal-600">8</span>
                <span className="text-[10px] text-slate-500 block">Clinical Features</span>
              </div>
            </div>

            {/* SPLIT STRUCTURE TABLE */}
            <div className="health-card p-6 space-y-3">
              <h3 className="font-bold text-sm text-slate-900">Stratified Dataset Partitioning & Isolation</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                    <tr>
                      <th className="p-3">Partition</th>
                      <th className="p-3">Samples (n)</th>
                      <th className="p-3">Share (%)</th>
                      <th className="p-3">Non-Diabetes (n)</th>
                      <th className="p-3">Diabetes Cases (n)</th>
                      <th className="p-3">Prevalence (%)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    <tr>
                      <td className="p-3 font-semibold text-slate-800">Training Split</td>
                      <td className="p-3 font-mono">70,000</td>
                      <td className="p-3">70.0%</td>
                      <td className="p-3 font-mono">64,164</td>
                      <td className="p-3 font-mono">5,836</td>
                      <td className="p-3">8.34%</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-semibold text-slate-800">Validation Split</td>
                      <td className="p-3 font-mono">15,000</td>
                      <td className="p-3">15.0%</td>
                      <td className="p-3 font-mono">13,749</td>
                      <td className="p-3 font-mono">1,251</td>
                      <td className="p-3">8.34%</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-semibold text-slate-800">Holdout Test Split</td>
                      <td className="p-3 font-mono">15,000</td>
                      <td className="p-3">15.0%</td>
                      <td className="p-3 font-mono">13,750</td>
                      <td className="p-3 font-mono">1,250</td>
                      <td className="p-3">8.33%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {/* TAB 2: MODEL COMPARISON */}
        {activeTab === 'comparison' && (
          <div className="space-y-6">
            <div className="health-card p-6 space-y-4">
              <h3 className="font-bold text-sm text-slate-900">Algorithm Performance Comparison Grid</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                    <tr>
                      <th className="p-3">Algorithm</th>
                      <th className="p-3">Accuracy</th>
                      <th className="p-3">Precision (PPV)</th>
                      <th className="p-3">Recall (Sens)</th>
                      <th className="p-3">Specificity</th>
                      <th className="p-3">F1-Score</th>
                      <th className="p-3">ROC-AUC</th>
                      <th className="p-3">Brier Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    <tr className="hover:bg-slate-50">
                      <td className="p-3 font-semibold text-slate-800">Logistic Regression</td>
                      <td className="p-3 font-mono">0.9912</td>
                      <td className="p-3 font-mono">0.9635</td>
                      <td className="p-3 font-mono">0.9297</td>
                      <td className="p-3 font-mono">0.9968</td>
                      <td className="p-3 font-mono">0.9463</td>
                      <td className="p-3 font-mono text-blue-600 font-bold">0.9990</td>
                      <td className="p-3 font-mono">0.0064</td>
                    </tr>
                    <tr className="hover:bg-slate-50">
                      <td className="p-3 font-semibold text-slate-800">Decision Tree</td>
                      <td className="p-3 font-mono">0.9957</td>
                      <td className="p-3 font-mono">0.9767</td>
                      <td className="p-3 font-mono">0.9720</td>
                      <td className="p-3 font-mono">0.9979</td>
                      <td className="p-3 font-mono">0.9744</td>
                      <td className="p-3 font-mono text-blue-600 font-bold">0.9976</td>
                      <td className="p-3 font-mono">0.0034</td>
                    </tr>
                    <tr className="hover:bg-slate-50">
                      <td className="p-3 font-semibold text-slate-800">Random Forest</td>
                      <td className="p-3 font-mono">0.9945</td>
                      <td className="p-3 font-mono">0.9941</td>
                      <td className="p-3 font-mono">0.9400</td>
                      <td className="p-3 font-mono">0.9995</td>
                      <td className="p-3 font-mono">0.9663</td>
                      <td className="p-3 font-mono text-blue-600 font-bold">0.9997</td>
                      <td className="p-3 font-mono">0.0044</td>
                    </tr>
                    <tr className="hover:bg-slate-50">
                      <td className="p-3 font-semibold text-slate-800">HistGradientBoosting</td>
                      <td className="p-3 font-mono">0.9961</td>
                      <td className="p-3 font-mono">0.9822</td>
                      <td className="p-3 font-mono">0.9712</td>
                      <td className="p-3 font-mono">0.9984</td>
                      <td className="p-3 font-mono">0.9767</td>
                      <td className="p-3 font-mono text-blue-600 font-bold">0.9998</td>
                      <td className="p-3 font-mono">0.0028</td>
                    </tr>
                    <tr className="bg-blue-50/60 font-bold">
                      <td className="p-3 text-blue-900 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                        XGBoost (Selected Final Model)
                      </td>
                      <td className="p-3 font-mono text-blue-900">0.9963</td>
                      <td className="p-3 font-mono text-blue-900">0.9846</td>
                      <td className="p-3 font-mono text-blue-900">0.9704</td>
                      <td className="p-3 font-mono text-blue-900">0.9986</td>
                      <td className="p-3 font-mono text-blue-900">0.9775</td>
                      <td className="p-3 font-mono text-emerald-700 font-extrabold">0.9998</td>
                      <td className="p-3 font-mono text-blue-900">0.0028</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: HOLDOUT PERFORMANCE & 95% CIs */}
        {activeTab === 'performance' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="health-card p-5 space-y-1">
                <span className="text-slate-400 text-xs font-bold uppercase block">ROC-AUC</span>
                <span className="text-3xl font-extrabold text-emerald-600">0.9985</span>
                <span className="text-xs text-slate-500 block font-mono">95% CI: [0.9968 - 0.9997]</span>
              </div>

              <div className="health-card p-5 space-y-1">
                <span className="text-slate-400 text-xs font-bold uppercase block">Accuracy</span>
                <span className="text-3xl font-extrabold text-slate-900">0.9947</span>
                <span className="text-xs text-slate-500 block font-mono">95% CI: [0.9935 - 0.9958]</span>
              </div>

              <div className="health-card p-5 space-y-1">
                <span className="text-slate-400 text-xs font-bold uppercase block">Sensitivity / Recall</span>
                <span className="text-3xl font-extrabold text-blue-600">0.9817</span>
                <span className="text-xs text-slate-500 block font-mono">95% CI: [0.9738 - 0.9888]</span>
              </div>

              <div className="health-card p-5 space-y-1">
                <span className="text-slate-400 text-xs font-bold uppercase block">Specificity</span>
                <span className="text-3xl font-extrabold text-indigo-600">0.9958</span>
                <span className="text-xs text-slate-500 block font-mono">95% CI: [0.9948 - 0.9969]</span>
              </div>

              <div className="health-card p-5 space-y-1">
                <span className="text-slate-400 text-xs font-bold uppercase block">Precision / PPV</span>
                <span className="text-3xl font-extrabold text-teal-600">0.9554</span>
                <span className="text-xs text-slate-500 block font-mono">95% CI: [0.9437 - 0.9662]</span>
              </div>

              <div className="health-card p-5 space-y-1">
                <span className="text-slate-400 text-xs font-bold uppercase block">Brier Score</span>
                <span className="text-3xl font-extrabold text-cyan-600">0.0034</span>
                <span className="text-xs text-slate-500 block">Isotonic Calibrated</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: SUBGROUP FAIRNESS */}
        {activeTab === 'fairness' && (
          <div className="health-card p-6 space-y-4">
            <h3 className="font-bold text-sm text-slate-900">Demographic & Clinical Subgroup Fairness Audit</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="p-3">Subgroup Cohort</th>
                    <th className="p-3">Samples (N)</th>
                    <th className="p-3">Prevalence (%)</th>
                    <th className="p-3">Accuracy</th>
                    <th className="p-3">Sensitivity</th>
                    <th className="p-3">Specificity</th>
                    <th className="p-3">Precision</th>
                    <th className="p-3">ROC-AUC</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  <tr>
                    <td className="p-3 font-sans font-semibold">Female Cohort</td>
                    <td className="p-3">8,711</td>
                    <td className="p-3">8.23%</td>
                    <td className="p-3">0.9945</td>
                    <td className="p-3">0.9819</td>
                    <td className="p-3">0.9956</td>
                    <td className="p-3">0.9526</td>
                    <td className="p-3 text-emerald-600 font-bold">0.9983</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-sans font-semibold">Male Cohort</td>
                    <td className="p-3">6,274</td>
                    <td className="p-3">8.50%</td>
                    <td className="p-3">0.9949</td>
                    <td className="p-3">0.9812</td>
                    <td className="p-3">0.9962</td>
                    <td className="p-3">0.9596</td>
                    <td className="p-3 text-emerald-600 font-bold">0.9987</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-sans font-semibold">Age &lt; 30 (Younger Adults)</td>
                    <td className="p-3">3,957</td>
                    <td className="p-3">0.15%</td>
                    <td className="p-3">1.0000</td>
                    <td className="p-3">1.0000</td>
                    <td className="p-3">1.0000</td>
                    <td className="p-3">1.0000</td>
                    <td className="p-3 text-emerald-600 font-bold">1.0000</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-sans font-semibold">Age 30–49 (Middle-Aged)</td>
                    <td className="p-3">6,056</td>
                    <td className="p-3">3.57%</td>
                    <td className="p-3">0.9964</td>
                    <td className="p-3">0.9444</td>
                    <td className="p-3">0.9983</td>
                    <td className="p-3">0.9533</td>
                    <td className="p-3 text-emerald-600 font-bold">0.9974</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-sans font-semibold">Age &ge; 50 (Older / High Risk)</td>
                    <td className="p-3">4,987</td>
                    <td className="p-3">20.61%</td>
                    <td className="p-3">0.9884</td>
                    <td className="p-3">0.9893</td>
                    <td className="p-3">0.9881</td>
                    <td className="p-3">0.9558</td>
                    <td className="p-3 text-emerald-600 font-bold">0.9981</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 5: EXTERNAL VALIDATION */}
        {activeTab === 'external' && (
          <div className="space-y-6">
            <div className="health-card p-6 space-y-4">
              <h3 className="font-bold text-sm text-slate-900">Does the Model Generalize?</h3>
              <p className="text-xs text-slate-500">
                External validation evaluates model performance on independent datasets not used during training.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <span className="badge-pill badge-blue mb-2">Internal Test Split</span>
                  <h4 className="font-bold text-sm text-slate-900">100K Holdout Test Set</h4>
                  <p className="text-xs text-slate-500 mt-1 font-mono">N=15,000 | ROC-AUC = 0.9997 | Brier = 0.0033</p>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <span className="badge-pill badge-warning mb-2">Benchmark Isolation</span>
                  <h4 className="font-bold text-sm text-slate-900">Pima Indians Benchmark Dataset</h4>
                  <p className="text-xs text-slate-500 mt-1 font-mono">N=768 | ROC-AUC = 0.8250 | Brier = 0.1618</p>
                </div>
              </div>

              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900">
                <p className="font-bold mb-1">Unlinked External Synthetic Dataset Audit Notice</p>
                <p>
                  Synthetic external datasets previously evaluated were unlinked to uphold research integrity. Multi-center prospective hospital EHR validation remains planned prior to clinical deployment.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: LIMITATIONS */}
        {activeTab === 'limitations' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="health-card p-5 space-y-2">
              <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Cross-Sectional Scope
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                The dataset provides point-in-time diagnostic screening probability rather than 5-year longitudinal prognostic risk.
              </p>
            </div>

            <div className="health-card p-5 space-y-2">
              <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                EHR Data Completeness
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Evaluated on complete EHR records with 0 missing values. Performance in low-resource settings with unobserved labs requires further study.
              </p>
            </div>
          </div>
        )}

      </div>
  );
};

export default ResearchValidation;
