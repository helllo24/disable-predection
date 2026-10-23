import React from 'react';

/**
 * RiskGauge Component
 * Renders a high-resolution SVG circular risk gauge with gradient stroke,
 * decision threshold marker, and clear probability percentage.
 */
const RiskGauge = ({ probability = 0, threshold = 0.30, category = 'Low Risk' }) => {
  const pct = Math.min(Math.max(probability * 100, 0), 100);
  const strokeDasharray = 283; // 2 * pi * 45
  const strokeDashoffset = strokeDasharray - (strokeDasharray * pct) / 100;
  
  // Color configuration based on category
  let gradientId = 'gradientGreen';
  let badgeColor = 'badge-success';
  if (pct >= 50 || category.toLowerCase().includes('high')) {
    gradientId = 'gradientRed';
    badgeColor = 'badge-danger';
  } else if (pct >= threshold * 100 || category.toLowerCase().includes('moderate')) {
    gradientId = 'gradientAmber';
    badgeColor = 'badge-warning';
  }

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative w-48 h-48 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="gradientGreen" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
            <linearGradient id="gradientAmber" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#d97706" />
            </linearGradient>
            <linearGradient id="gradientRed" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>
          {/* Track Circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="#e2e8f0"
            strokeWidth="8"
            fill="transparent"
          />
          {/* Progress Arc */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke={`url(#${gradientId})`}
            strokeWidth="8"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {pct.toFixed(1)}%
          </span>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider mt-0.5">
            Model Risk
          </span>
        </div>
      </div>

      {/* Category Badge & Threshold Note */}
      <div className="mt-3 text-center">
        <span className={`badge-pill ${badgeColor} text-sm px-3 py-1`}>
          {category}
        </span>
        <p className="text-xs text-slate-500 mt-2">
          Configured Decision Threshold: <span className="font-semibold text-slate-700">{(threshold * 100).toFixed(1)}%</span>
        </p>
      </div>
    </div>
  );
};

export default RiskGauge;
