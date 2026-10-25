
import React from "react";
import {
  Activity,
  TrendingUp,
  TrendingDown,
} from "lucide-react";

const FEATURE_LABELS = {
  Pregnancies: "Pregnancies",
  Glucose: "Glucose Level",
  BloodPressure: "Blood Pressure",
  SkinThickness: "Skin Thickness",
  Insulin: "Insulin",
  BMI: "Body Mass Index (BMI)",
  DiabetesPedigreeFunction: "Diabetes Pedigree Function",
  Age: "Age",
};

function normalizeFeature(feature) {
  const rawValue =
    feature.actual_value ?? feature.value;

  const rawContribution =
    feature.shap_contribution ??
    feature.shap_value ??
    feature.contribution;

  const value = Number(rawValue);
  const contribution = Number(rawContribution);

  return {
    name:
      feature.feature ??
      feature.feature_name ??
      feature.name ??
      "Unknown feature",
    value,
    contribution,
  };
}

export default function SHAPContribution({ features = [] }) {
  const normalized = Array.isArray(features)
    ? features
        .filter((feature) => feature && typeof feature === "object")
        .map(normalizeFeature)
        .filter(
          (item) =>
            Number.isFinite(item.value) &&
            Number.isFinite(item.contribution)
        )
    : [];

  const sorted = [...normalized].sort(
    (a, b) =>
      Math.abs(b.contribution) - Math.abs(a.contribution)
  );

  const maxMagnitude = Math.max(
    ...sorted.map((item) => Math.abs(item.contribution)),
    0.000001
  );

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-3">
        <div className="rounded-xl bg-blue-50 p-2 text-blue-600">
          <Activity size={22} />
        </div>

        <div>
          <h2 className="text-lg font-semibold text-slate-900">
            SHAP Feature Contributions
          </h2>
          <p className="text-sm text-slate-500">
            How each input influences the model output
          </p>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-4 text-sm">
        <span className="flex items-center gap-2 text-emerald-700">
          <TrendingDown size={16} />
          Negative contribution
        </span>

        <span className="flex items-center gap-2 text-rose-700">
          <TrendingUp size={16} />
          Positive contribution
        </span>
      </div>

      {sorted.length === 0 ? (
        <div className="rounded-xl bg-slate-50 p-5 text-sm text-slate-600">
          SHAP contributions are not available for this prediction.
          Check the backend terminal for SHAP errors and verify the
          background dataset.
        </div>
      ) : (
        <div className="space-y-5">
          {sorted.map((item, index) => {
            const positive = item.contribution >= 0;

            const width =
              (Math.abs(item.contribution) / maxMagnitude) * 100;

            const displayName =
              FEATURE_LABELS[item.name] ?? item.name;

            return (
              <div key={`${item.name}-${index}`}>
                <div className="mb-2 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium text-slate-800">
                      {displayName}
                    </p>

                    <p className="text-xs text-slate-500">
                      Input value: {item.value.toFixed(2)}
                    </p>
                  </div>

                  <span
                    className={`whitespace-nowrap text-sm font-semibold ${
                      positive
                        ? "text-rose-600"
                        : "text-emerald-600"
                    }`}
                  >
                    {positive ? "+" : ""}
                    {item.contribution.toFixed(5)}
                  </span>
                </div>

                <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full ${
                      positive ? "bg-rose-500" : "bg-emerald-500"
                    }`}
                    style={{ width: `${width}%` }}
                    title={`SHAP value: ${item.contribution}`}
                  />
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  {positive
                    ? "Pushes the model output upward"
                    : "Pushes the model output downward"}
                </p>
              </div>
            );
          })}
        </div>
      )}

      <p className="mt-5 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-900">
        SHAP explains the model output, not medical causation.
        Positive and negative values indicate the direction in which
        each feature moves the explained output relative to the
        explainer baseline.
      </p>
    </section>
  );
}
