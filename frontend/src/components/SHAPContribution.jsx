import React from 'react';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';

/**
 * SHAPContribution Component
 * Renders individual feature SHAP contribution bars with neutral non-causal descriptions.
 */
const SHAPContribution = ({ features = [] }) => {
  if (!features || features.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-slate-500 bg-slate-50 rounded-lg">
        No feature explanation data returned by the prediction model.
      </div>
    );
  }

  // Calculate max absolute SHAP value for scaling bars
  const maxAbsShap = Math.max(...features.map(f => Math.abs(f.shap_value || f.contribution || 0)), 0.001);

  return (
    <div className="space-y-3">
      {features.map((item, idx) => {
        const val = item.shap_value ?? item.contribution ?? 0;
        const absVal = Math.abs(val);
        const barPct = Math.min((absVal / maxAbsShap) * 100, 100);
        const isPositive = val >= 0;
        
        return (
          <div key={idx} className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm hover:border-slate-300 transition-colors">
            <div className="flex items-center justify-between text-sm mb-1.5">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-800">
                  {item.feature_name || item.feature}
                </span>
                {item.value !== undefined && item.value !== null && (
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                    Val: {String(item.value)}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5 font-medium text-xs">
                {isPositive ? (
                  <span className="text-amber-700 flex items-center gap-1 bg-amber-50 px-2 py-0.5 rounded">
                    <TrendingUp className="w-3.5 h-3.5 text-amber-600" />
                    +{val.toFixed(4)} (Higher Risk Shift)
                  </span>
                ) : (
                  <span className="text-emerald-700 flex items-center gap-1 bg-emerald-50 px-2 py-0.5 rounded">
                    <TrendingDown className="w-3.5 h-3.5 text-emerald-600" />
                    {val.toFixed(4)} (Lower Risk Shift)
                  </span>
                )}
              </div>
            </div>

            {/* Progress Bar Container */}
            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isPositive ? 'bg-gradient-to-r from-amber-500 to-red-500' : 'bg-gradient-to-r from-emerald-400 to-teal-500'
                }`}
                style={{ width: `${Math.max(barPct, 6)}%` }}
              />
            </div>

            {/* Non-causal explanatory wording */}
            <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
              <Info className="w-3 h-3 text-slate-400 flex-shrink-0" />
              <span>
                Feature value <strong className="text-slate-700">{item.value ?? 'observed'}</strong> {isPositive ? 'contributed positively to the model prediction probability.' : 'contributed towards lowering the model prediction probability.'}
              </span>
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default SHAPContribution;
