import React from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import {
  Sparkles,
  ArrowRight,
  LineChart,
  ShieldCheck,
  Activity,
  Cpu,
  Database,
  BarChart3,
  HeartPulse,
  CheckCircle2,
  Lock
} from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-12 pb-12">
        
        {/* HERO SECTION */}
        <section className="relative overflow-hidden rounded-3xl bg-slate-900 text-white p-8 sm:p-12 border border-slate-800 shadow-2xl">
          {/* Background Decorative Gradients */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-cyan-600/20 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* LEFT HERO COLUMN */}
            <div className="lg:col-span-7 space-y-6">
              
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/30 text-blue-300 text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>AI-POWERED HEALTH INTELLIGENCE</span>
              </div>

              {/* Main Heading */}
              <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                Understand Your Diabetes Risk{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-teal-300 to-cyan-400">
                  Before It Becomes a Problem.
                </span>
              </h1>

              {/* Subheading */}
              <p className="text-slate-300 text-base sm:text-lg max-w-2xl leading-relaxed">
                An advanced machine-learning decision-support pipeline evaluated on over 100,000 patient records.
                Quantifies individual screening probability using validated clinical indicators and transparent SHAP explanations.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={() => navigate('/diabetes-prediction')}
                  className="px-6 py-3.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-blue-500/25 flex items-center gap-2 transition-all transform hover:-translate-y-0.5"
                >
                  <span>Check My Risk</span>
                  <ArrowRight className="w-4 h-4" />
                </button>

                <button
                  onClick={() => navigate('/research')}
                  className="px-6 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm rounded-xl border border-slate-700 flex items-center gap-2 transition-all"
                >
                  <LineChart className="w-4 h-4 text-teal-400" />
                  <span>Explore Research</span>
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center gap-6 pt-4 text-xs text-slate-400 border-t border-slate-800/80">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 100K EHR Validation Split
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> TRIPOD+AI Compliant
                </span>
                <span className="flex items-center gap-1.5">
                  <Lock className="w-4 h-4 text-blue-400" /> Local Model Execution
                </span>
              </div>

            </div>

            {/* RIGHT HERO COLUMN: UI-BASED AI MEDICAL VISUALIZATION */}
            <div className="lg:col-span-5 relative">
              <div className="bg-slate-950/80 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-2xl space-y-4">
                
                {/* Visualizer Top Bar */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-cyan-400 animate-pulse" />
                    <span className="text-xs font-bold text-slate-200 tracking-wider">AI ANALYSIS ENGINE</span>
                  </div>
                  <span className="badge-pill bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px]">
                    XGBoost v2.0 Active
                  </span>
                </div>

                {/* Floating Health Cards UI Representation */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Blood Glucose</span>
                    <span className="text-lg font-bold text-white">145 <span className="text-xs text-slate-400 font-normal">mg/dL</span></span>
                    <span className="text-[10px] text-amber-400 block mt-0.5">High Contribution</span>
                  </div>

                  <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">HbA1c Level</span>
                    <span className="text-lg font-bold text-white">7.2 <span className="text-xs text-slate-400 font-normal">%</span></span>
                    <span className="text-[10px] text-red-400 block mt-0.5">Top SHAP Predictor</span>
                  </div>

                  <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">BMI Indicator</span>
                    <span className="text-lg font-bold text-white">28.4 <span className="text-xs text-slate-400 font-normal">kg/m²</span></span>
                    <span className="text-[10px] text-blue-400 block mt-0.5">Overweight Range</span>
                  </div>

                  <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Patient Age</span>
                    <span className="text-lg font-bold text-white">54 <span className="text-xs text-slate-400 font-normal">Years</span></span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Demographic Factor</span>
                  </div>
                </div>

                {/* Live Model Status Indicator */}
                <div className="p-3 bg-blue-950/40 border border-blue-800/40 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs">
                    <Activity className="w-4 h-4 text-blue-400" />
                    <div>
                      <p className="font-semibold text-slate-200">Evaluating Patient Risk...</p>
                      <p className="text-[10px] text-slate-400">Calibrated Isotonic Probability</p>
                    </div>
                  </div>
                  <span className="text-xs font-extrabold text-cyan-400 bg-cyan-950 px-2.5 py-1 rounded border border-cyan-800">
                    ROC-AUC 0.9985
                  </span>
                </div>

              </div>
            </div>

          </div>
        </section>

        {/* 4 FEATURE CARDS */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div className="health-card p-6 space-y-3 relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900">AI Risk Prediction</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Trained on 70,000 patients and tested on 15,000 holdout records using gradient boosted tree ensembles.
            </p>
          </div>

          <div className="health-card p-6 space-y-3 relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-cyan-50 text-cyan-600 flex items-center justify-center font-bold group-hover:bg-cyan-600 group-hover:text-white transition-colors">
              <BarChart3 className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900">Explainable AI (SHAP)</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Provides instance-level SHAP attributions so patients and clinicians see which factors influenced the prediction.
            </p>
          </div>

          <div className="health-card p-6 space-y-3 relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center font-bold group-hover:bg-teal-600 group-hover:text-white transition-colors">
              <Activity className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900">Clinical Indicators</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Utilizes 8 non-invasive clinical features (glucose, HbA1c, BMI, age, hypertension, heart disease, smoking).
            </p>
          </div>

          <div className="health-card p-6 space-y-3 relative overflow-hidden group">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold group-hover:bg-indigo-600 group-hover:text-white transition-colors">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-900">Research Validated</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Complete TRIPOD+AI reporting compliance, subgroup fairness audit, and isolated benchmark testing.
            </p>
          </div>

        </section>

      </div>
  );
};

export default Home;
