
import React, { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import Layout from "../components/Layout";
import RiskGauge from "../components/RiskGauge";
import SHAPContribution from "../components/SHAPContribution";
import ModelInfoCard from "../components/ModelInfoCard";

import {
  predictDiabetesProduction,
  getDiabetesHistory,
} from "../services/api";

const INITIAL_FORM = {
  pregnancies: "0",
  glucose: "120",
  blood_pressure: "70",
  skin_thickness: "20",
  insulin: "80",
  bmi: "25",
  diabetes_pedigree_function: "0.5",
  age: "30",
};

const FIELDS = [
  {
    name: "pregnancies",
    label: "Pregnancies",
    description: "Number of pregnancies",
    min: 0,
    max: 20,
    step: 1,
    unit: "",
  },
  {
    name: "glucose",
    label: "Glucose",
    description: "Plasma glucose concentration",
    min: 0,
    max: 300,
    step: 1,
    unit: "mg/dL",
  },
  {
    name: "blood_pressure",
    label: "Blood Pressure",
    description: "Diastolic blood pressure",
    min: 0,
    max: 200,
    step: 1,
    unit: "mm Hg",
  },
  {
    name: "skin_thickness",
    label: "Skin Thickness",
    description: "Triceps skinfold thickness",
    min: 0,
    max: 100,
    step: 1,
    unit: "mm",
  },
  {
    name: "insulin",
    label: "Insulin",
    description: "2-hour serum insulin",
    min: 0,
    max: 1000,
    step: 1,
    unit: "mu U/mL",
  },
  {
    name: "bmi",
    label: "Body Mass Index",
    description: "Body mass index",
    min: 0,
    max: 100,
    step: 0.1,
    unit: "BMI",
  },
  {
    name: "diabetes_pedigree_function",
    label: "Diabetes Pedigree Function",
    description: "Family-history-related model feature",
    min: 0,
    max: 3,
    step: 0.01,
    unit: "",
  },
  {
    name: "age",
    label: "Age",
    description: "Age in years",
    min: 1,
    max: 120,
    step: 1,
    unit: "years",
  },
];

function normalizeHistory(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.history)) return data.history;
  if (Array.isArray(data?.predictions)) return data.predictions;
  if (Array.isArray(data?.items)) return data.items;

  return [];
}

function normalizeContributions(result) {
  if (Array.isArray(result?.top_contributing_features)) {
    return result.top_contributing_features;
  }

  if (Array.isArray(result?.shap_explanation)) {
    return result.shap_explanation;
  }

  return [];
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleString();
}

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  return (
    error?.message ||
    "Something went wrong. Please check the backend and try again."
  );
}

export default function DiabetesPrediction() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("prediction");

  async function loadHistory() {
    setHistoryLoading(true);

    try {
      const data = await getDiabetesHistory();
      setHistory(normalizeHistory(data));
    } catch (err) {
      console.error("Unable to load diabetes history:", err);
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function resetForm() {
    setForm(INITIAL_FORM);
    setResult(null);
    setError("");
    setActiveTab("prediction");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    for (const field of FIELDS) {
      const raw = form[field.name];
      const value = Number(raw);

      if (
        raw.trim() === "" ||
        !Number.isFinite(value) ||
        value < field.min ||
        value > field.max
      ) {
        setError(
          `${field.label}: enter a valid value between ${field.min} and ${field.max}.`
        );
        return;
      }
    }

    const payload = {
      pregnancies: Number(form.pregnancies),
      glucose: Number(form.glucose),
      blood_pressure: Number(form.blood_pressure),
      skin_thickness: Number(form.skin_thickness),
      insulin: Number(form.insulin),
      bmi: Number(form.bmi),
      diabetes_pedigree_function: Number(
        form.diabetes_pedigree_function
      ),
      age: Number(form.age),
    };

    setLoading(true);

    try {
      const response = await predictDiabetesProduction(payload);

      setResult(response);
      setActiveTab("result");

      await loadHistory();
    } catch (err) {
      console.error("Diabetes prediction failed:", err);
      setError(getErrorMessage(err));
      setActiveTab("prediction");
    } finally {
      setLoading(false);
    }
  }

  const contributions = normalizeContributions(result);

  const probability = Number(result?.probability);

  const validProbability =
    Number.isFinite(probability) &&
    probability >= 0 &&
    probability <= 1;

  const prediction = Number(result?.prediction);
  const isPositive = prediction === 1;

  const riskLabel =
    result?.risk_category ??
    result?.risk ??
    "Unavailable";

  const threshold = Number(
    result?.threshold ?? result?.decision_threshold
  );

  const hasThreshold = Number.isFinite(threshold);

  return (
    
      <div className="min-h-screen bg-slate-50 px-4 py-6 text-slate-800 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl space-y-6">
          {/* Page Header */}
          <header className="relative animate-fade-in overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-indigo-950 to-blue-900 p-6 text-white shadow-xl sm:p-9">
            <div className="pointer-events-none absolute -right-10 -top-20 h-64 w-64 rounded-full bg-blue-400/10 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-24 left-1/3 h-64 w-64 rounded-full bg-violet-400/10 blur-3xl" />

            <div className="relative flex flex-col justify-between gap-6 md:flex-row md:items-center">
              <div>
                <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold tracking-wide text-blue-100">
                  <Activity size={15} />
                  AI-POWERED HEALTHCARE
                </div>

                <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                  Diabetes Risk Prediction
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
                  Analyze clinical indicators using the PIMA
                  diabetes prediction model and view your
                  personalized model-generated risk estimate.
                </p>
              </div>

              <div className="flex shrink-0 items-center gap-3 rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                <div className="rounded-xl bg-emerald-400/15 p-3 text-emerald-300">
                  <ShieldCheck size={26} />
                </div>

                <div>
                  <p className="text-sm font-semibold">
                    Health Assessment
                  </p>
                  <p className="mt-1 text-xs text-slate-300">
                    Clinical input analysis
                  </p>
                </div>
              </div>
            </div>
          </header>

          {/* Navigation */}
          <div className="flex flex-wrap gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
            {[
              {
                id: "prediction",
                label: "Patient Information",
                icon: Activity,
              },
              {
                id: "result",
                label: "Prediction Result",
                icon: TrendingUp,
              },
              {
                id: "history",
                label: "Prediction History",
                icon: Clock,
              },
            ].map((tab) => {
              const Icon = tab.icon;

              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`inline-flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${
                    activeTab === tab.id
                      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
                      : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  <Icon size={17} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Error */}
          {error && (
            <div
              role="alert"
              className="animate-fade-in flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
            >
              <AlertCircle
                className="mt-0.5 shrink-0"
                size={20}
              />
              <div>
                <p className="font-semibold">
                  Unable to complete prediction
                </p>
                <p className="mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Patient Form */}
          {activeTab === "prediction" && (
            <section className="health-card animate-fade-in overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-6 sm:px-8">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-blue-50 p-3 text-blue-600">
                    <Activity size={23} />
                  </div>

                  <div>
                    <h2 className="text-xl font-bold text-slate-900">
                      Patient Information
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                      Enter all eight clinical features required by the model.
                    </p>
                  </div>
                </div>
              </div>

              <form
                onSubmit={handleSubmit}
                className="p-5 sm:p-8"
              >
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                  {FIELDS.map((field, index) => (
                    <div
                      key={field.name}
                      className="animate-fade-in"
                      style={{
                        animationDelay: `${index * 60}ms`,
                      }}
                    >
                      <label
                        htmlFor={field.name}
                        className="mb-2 block text-sm font-semibold text-slate-700"
                      >
                        {field.label}
                        {field.unit && (
                          <span className="ml-1 font-normal text-slate-400">
                            ({field.unit})
                          </span>
                        )}
                      </label>

                      <input
                        id={field.name}
                        name={field.name}
                        type="number"
                        min={field.min}
                        max={field.max}
                        step={field.step}
                        value={form[field.name]}
                        onChange={handleChange}
                        required
                        className="input-health w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition-all duration-200 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                      />

                      <p className="mt-2 text-xs leading-5 text-slate-500">
                        {field.description}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-7 rounded-2xl border border-blue-100 bg-blue-50/70 p-4">
                  <div className="flex items-start gap-3">
                    <ShieldCheck
                      size={20}
                      className="mt-0.5 shrink-0 text-blue-600"
                    />

                    <div>
                      <p className="text-sm font-semibold text-blue-900">
                        Clinical data privacy
                      </p>
                      <p className="mt-1 text-xs leading-5 text-blue-800">
                        Enter accurate information. This assessment
                        uses the eight features expected by the PIMA model.
                        Do not enter guessed medical measurements.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-7 flex flex-col gap-3 sm:flex-row">
                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex flex-1 items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-indigo-200 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0"
                  >
                    {loading ? (
                      <>
                        <RefreshCw
                          size={19}
                          className="animate-spin"
                        />
                        <span>
                          Analyzing Clinical Risk...
                        </span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={19} />
                        <span>Analyze My Risk</span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={resetForm}
                    disabled={loading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-6 py-4 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
                  >
                    <RotateCcw size={17} />
                    Reset Form
                  </button>
                </div>

                {loading && (
                  <div className="animate-fade-in mt-6">
                    <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
                      <span>Processing model prediction</span>
                      <span className="animate-pulse">
                        Please wait...
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                      <div className="h-full w-1/2 animate-pulse rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500" />
                    </div>

                    <p className="mt-3 text-center text-xs text-slate-500">
                      Sending clinical features to the prediction service.
                    </p>
                  </div>
                )}
              </form>
            </section>
          )}

          {/* Prediction Result */}
          {activeTab === "result" && (
            <section className="animate-fade-in space-y-6">
              {!result ? (
                <div className="health-card rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                    <TrendingUp size={30} />
                  </div>

                  <h2 className="text-xl font-bold text-slate-900">
                    No prediction yet
                  </h2>

                  <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                    Enter patient information and run the model to view
                    the prediction result.
                  </p>

                  <button
                    type="button"
                    onClick={() => setActiveTab("prediction")}
                    className="mt-6 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-3 text-sm font-semibold text-white"
                  >
                    Enter Patient Information
                  </button>
                </div>
              ) : (
                <>
                  <div className="health-card rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
                    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                      <div>
                        <div className="flex items-center gap-2 text-sm font-semibold text-blue-600">
                          <CheckCircle2 size={18} />
                          Analysis Complete
                        </div>

                        <h2 className="mt-2 text-2xl font-bold text-slate-900">
                          Prediction Result
                        </h2>

                        <p className="mt-2 text-sm text-slate-500">
                          Model-generated result based on the supplied data.
                        </p>
                      </div>

                      <span
                        className={`inline-flex w-fit items-center gap-2 rounded-full px-4 py-2 text-sm font-bold ${
                          isPositive
                            ? "bg-red-50 text-red-700"
                            : "bg-emerald-50 text-emerald-700"
                        }`}
                      >
                        <span
                          className={`h-2 w-2 rounded-full ${
                            isPositive
                              ? "bg-red-500"
                              : "bg-emerald-500"
                          }`}
                        />
                        {isPositive
                          ? "Positive prediction"
                          : "Negative prediction"}
                      </span>
                    </div>

                    <div className="mt-7 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                      <div className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          Model Probability
                        </p>
                        <p className="mt-3 text-3xl font-bold text-slate-900">
                          {validProbability
                            ? `${(probability * 100).toFixed(1)}%`
                            : "—"}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          Reported Risk
                        </p>
                        <p className="mt-3 text-2xl font-bold text-slate-900">
                          {String(riskLabel)}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          Prediction ID
                        </p>
                        <p className="mt-3 text-2xl font-bold text-slate-900">
                          {result.id ?? "—"}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                          Model
                        </p>
                        <p className="mt-3 text-base font-bold text-slate-900">
                          {result.model ??
                            result.model_name ??
                            result.model_version ??
                            "PIMA Classifier"}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* RiskGauge */}
                  <div className="health-card rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
                    <h3 className="text-lg font-bold text-slate-900">
                      Risk Assessment
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      Probability and classification reported by the model.
                    </p>

                    <div className="mt-6">
                      <RiskGauge
                        probability={result.probability}
                        threshold={
                          result.threshold ??
                          result.decision_threshold ??
                          0.5
                        }
                        category={riskLabel}
                      />
                    </div>

                    {validProbability && (
                      <div className="mt-6">
                        <div className="mb-2 flex justify-between text-sm">
                          <span className="text-slate-600">
                            Model probability
                          </span>
                          <span className="font-bold text-slate-900">
                            {(probability * 100).toFixed(1)}%
                          </span>
                        </div>

                        <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={`h-full rounded-full transition-all duration-1000 ${
                              isPositive
                                ? "bg-gradient-to-r from-orange-500 to-red-500"
                                : "bg-gradient-to-r from-blue-500 to-indigo-500"
                            }`}
                            style={{
                              width: `${probability * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    )}

                    {hasThreshold && (
                      <p className="mt-4 text-xs text-slate-500">
                        Model decision threshold: {threshold}
                      </p>
                    )}
                  </div>

                  {/* SHAP Feature Contributions */}
                  <div className="health-card rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
                    <h3 className="text-lg font-bold text-slate-900">
                      SHAP Feature Contributions
                    </h3>

                    <p className="mt-1 text-sm leading-6 text-slate-500">
                      Shows how each input contributes to the model output.
                      These explanations do not establish medical causation.
                    </p>

                    <div className="mt-5">
                      <SHAPContribution features={contributions} />
                    </div>

                    {result.shap_available === false &&
                      contributions.length === 0 && (
                        <p className="mt-3 text-sm text-amber-700">
                          SHAP explanations are currently unavailable.
                          Check the backend logs for the explanation error.
                        </p>
                      )}
                  </div>

                  {/* Model Information */}
                  <div className="health-card rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
                    <h3 className="text-lg font-bold text-slate-900">
                      Model Information
                    </h3>

                    <div className="mt-5">
                      <ModelInfoCard
                        modelName={
                          result.model ??
                          result.model_name ??
                          result.model_version ??
                          "PIMA Calibrated Classifier"
                        }
                        model={result.model}
                        modelVersion={result.model_version}
                        threshold={
                          result.threshold ??
                          result.decision_threshold ??
                          0.5
                        }
                        probability={result.probability}
                      />
                    </div>

                    <p className="mt-4 text-xs leading-5 text-slate-500">
                      The displayed probability is the model's estimate.
                      It is not a diagnosis and should not be interpreted
                      as an individual's guaranteed chance of developing
                      diabetes.
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => setActiveTab("prediction")}
                      className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-md transition hover:-translate-y-0.5"
                    >
                      <Activity size={17} />
                      New Prediction
                    </button>

                    <button
                      type="button"
                      onClick={() => setActiveTab("history")}
                      className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                    >
                      <Clock size={17} />
                      View History
                    </button>
                  </div>
                </>
              )}
            </section>
          )}

          {/* Prediction History */}
          {activeTab === "history" && (
            <section className="health-card animate-fade-in overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
              <div className="flex flex-col justify-between gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:p-8">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">
                    Prediction History
                  </h2>
                  <p className="mt-2 text-sm text-slate-500">
                    Previously saved diabetes predictions.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={loadHistory}
                  disabled={historyLoading}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
                >
                  <RefreshCw
                    size={16}
                    className={historyLoading ? "animate-spin" : ""}
                  />
                  Refresh History
                </button>
              </div>

              {historyLoading ? (
                <div className="flex flex-col items-center justify-center p-12">
                  <RefreshCw
                    size={28}
                    className="animate-spin text-blue-600"
                  />
                  <p className="mt-4 text-sm text-slate-500">
                    Loading prediction history...
                  </p>
                </div>
              ) : history.length === 0 ? (
                <div className="p-12 text-center">
                  <Clock
                    size={36}
                    className="mx-auto text-slate-300"
                  />
                  <p className="mt-4 font-semibold text-slate-700">
                    No prediction history found
                  </p>
                  <p className="mt-2 text-sm text-slate-500">
                    Your saved predictions will appear here.
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[720px] text-left text-sm">
                    <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="px-5 py-4 font-semibold">Date</th>
                        <th className="px-5 py-4 font-semibold">Glucose</th>
                        <th className="px-5 py-4 font-semibold">BMI</th>
                        <th className="px-5 py-4 font-semibold">Prediction</th>
                        <th className="px-5 py-4 font-semibold">Risk</th>
                        <th className="px-5 py-4 font-semibold">Probability</th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100">
                      {history.map((item, index) => {
                        const itemProbability = Number(item.probability);

                        return (
                          <tr
                            key={item.id ?? index}
                            className="transition-colors hover:bg-slate-50"
                          >
                            <td className="whitespace-nowrap px-5 py-4 text-slate-600">
                              {formatDate(item.created_at)}
                            </td>

                            <td className="px-5 py-4 font-medium text-slate-800">
                              {item.glucose ?? "—"}
                            </td>

                            <td className="px-5 py-4 text-slate-700">
                              {item.bmi ?? "—"}
                            </td>

                            <td className="px-5 py-4">
                              <span
                                className={`rounded-full px-3 py-1 text-xs font-bold ${
                                  Number(item.prediction) === 1
                                    ? "bg-red-50 text-red-700"
                                    : "bg-emerald-50 text-emerald-700"
                                }`}
                              >
                                {Number(item.prediction) === 1
                                  ? "Positive"
                                  : Number(item.prediction) === 0
                                    ? "Negative"
                                    : "—"}
                              </span>
                            </td>

                            <td className="px-5 py-4 text-slate-700">
                              {item.risk_category ?? item.risk ?? "—"}
                            </td>

                            <td className="px-5 py-4 font-semibold text-slate-800">
                              {Number.isFinite(itemProbability)
                                ? `${(itemProbability * 100).toFixed(1)}%`
                                : "—"}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {/* Medical Disclaimer */}
          <footer className="rounded-2xl border border-amber-200 bg-amber-50 p-4 sm:p-5">
            <div className="flex items-start gap-3">
              <AlertCircle
                size={20}
                className="mt-0.5 shrink-0 text-amber-600"
              />

              <div>
                <p className="text-sm font-bold text-amber-900">
                  Medical Disclaimer
                </p>
                <p className="mt-1 text-xs leading-6 text-amber-800">
                  This tool provides a machine-learning estimate for
                  informational and research purposes only. The PIMA dataset
                  represents a specific population, and model performance
                  may differ for other populations. A negative prediction
                  does not rule out diabetes, and a positive prediction
                  does not confirm it. Consult a qualified healthcare
                  professional for clinical assessment.
                </p>
              </div>
            </div>
          </footer>
        </div>
      </div>
    
  );
}
