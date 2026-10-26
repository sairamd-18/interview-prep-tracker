import React from 'react';

export default function ReadinessGauge({ score = 0, size = 180, strokeWidth = 14 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let color = '#ef4444'; // Red for < 50
  let label = 'Needs Focus';
  let badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/20';

  if (score >= 75) {
    color = '#10b981'; // Emerald
    label = 'Interview Ready';
    badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  } else if (score >= 55) {
    color = '#6366f1'; // Indigo
    label = 'Good Progress';
    badgeColor = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
  } else if (score >= 40) {
    color = '#f59e0b'; // Amber
    label = 'Developing';
    badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  }

  return (
    <div className="flex flex-col items-center justify-center relative select-none">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="w-full h-full transform -rotate-90" viewBox={`0 0 ${size} ${size}`}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            {score}%
          </span>
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mt-0.5">
            Readiness
          </span>
        </div>
      </div>

      <div className={`mt-3 px-3 py-1 rounded-full text-xs font-semibold border ${badgeColor}`}>
        {label}
      </div>
    </div>
  );
}
