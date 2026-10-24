
import React from 'react';
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';

const SHAPContribution = ({ features = [] }) => {
  if (!Array.isArray(features) || features.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-slate-500 bg-slate-50 rounded-lg">
        No feature explanation data returned by the prediction model.
      </div>
    );
  }

  // Backend uses shap_contribution and actual_value.
  // Support legacy field names too.
  const normalized = features.map((item) => ({
    ...item,
    featureName: item.feature_name ?? item.feature ?? 'Unknown feature',
    actualValue: item.actual_value ?? item.value ?? null,
    contribution: Number(
      item.shap_contribution ?? item.shap_value ?? item.contribution ?? 0
    ),
  }));

  const maxAbs = Math.max(
    ...normalized.map((item) => Math.abs(item.contribution)),
    0
  );

  return (
    <div className="space-y-3">
      {normalized.map((item, idx) => {
        const value = item.contribution;
        const isPositive = value > 0;
        const isNegative = value < 0;
        const isZero = value === 0;

        // Scale each bar relative to the largest absolute contribution.
        const barPct =
          maxAbs > 0 ? (Math.abs(value) / maxAbs) * 100 : 0;

        return (
          <div
            key={`${item.featureName}-${idx}`}
            className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm"
          >
            <div className="flex items-center justify-between gap-3 text-sm mb-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-semibold text-slate-800">
                  {item.featureName}
                </span>

                {item.actualValue !== null && (
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                    Value: {item.actualValue}
                  </span>
                )}
              </div>

              <span
                className={`flex-shrink-0 flex items-center gap-1 text-xs font-medium px-2 py-1 rounded ${
                  isPositive
                    ? 'text-amber-700 bg-amber-50'
                    : isNegative
                    ? 'text-emerald-700 bg-emerald-50'
                    : 'text-slate-600 bg-slate-100'
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="w-3.5 h-3.5" />
                ) : isNegative ? (
                  <TrendingDown className="w-3.5 h-3.5" />
                ) : (
                  <Minus className="w-3.5 h-3.5" />
                )}

                {value > 0 ? '+' : ''}
                {value.toFixed(4)}
                {isPositive
                  ? ' (Higher model output)'
                  : isNegative
                  ? ' (Lower model output)'
                  : ' (Zero contribution)'}
              </span>
            </div>

            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isPositive
                    ? 'bg-gradient-to-r from-amber-500 to-red-500'
                    : isNegative
                    ? 'bg-gradient-to-r from-emerald-400 to-teal-500'
                    : 'bg-slate-300'
                }`}
                style={{ width: `${barPct}%` }}
              />
            </div>

            <p className="text-[11px] text-slate-500 mt-2 flex items-start gap-1">
              <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
              <span>
                {isPositive
                  ? 'This feature contributed positively to the explained model output.'
                  : isNegative
                  ? 'This feature contributed negatively to the explained model output.'
                  : 'The reported SHAP contribution is zero.'}
                {' '}SHAP contribution is an explanation of model output, not proof of causation.
              </span>
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default SHAPContribution;
