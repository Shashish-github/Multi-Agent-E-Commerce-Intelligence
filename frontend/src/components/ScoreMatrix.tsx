import React from 'react';
import type { ScoreBreakdown } from '../types';

interface ScoreMatrixProps {
  scoreBreakdown: ScoreBreakdown;
  compact?: boolean;
}

export const ScoreMatrix: React.FC<ScoreMatrixProps> = ({ scoreBreakdown, compact = false }) => {
  const metrics = [
    { label: 'Requirement Fit', score: scoreBreakdown.requirement_fit, weight: '30%', color: 'from-cyan-500 to-blue-500' },
    { label: 'Review Quality', score: scoreBreakdown.review_quality, weight: '20%', color: 'from-emerald-500 to-teal-500' },
    { label: 'Price Value', score: scoreBreakdown.price_value, weight: '15%', color: 'from-amber-500 to-yellow-500' },
    { label: 'Spec Strength', score: scoreBreakdown.spec_strength, weight: '15%', color: 'from-indigo-500 to-purple-500' },
    { label: 'Reliability Trust', score: scoreBreakdown.reliability_evidence, weight: '10%', color: 'from-teal-500 to-cyan-500' },
    { label: 'Preference Match', score: scoreBreakdown.preference_match, weight: '10%', color: 'from-fuchsia-500 to-pink-500' },
  ];

  if (compact) {
    return (
      <div className="grid grid-cols-3 gap-2 text-xs">
        {metrics.map(m => (
          <div key={m.label} className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div className="flex justify-between text-[10px] text-slate-400 mb-1">
              <span>{m.label}</span>
              <span className="font-mono text-cyan-400">{(m.score * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${m.color} rounded-full`}
                style={{ width: `${Math.min(100, Math.max(5, m.score * 100))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {metrics.map(m => (
        <div key={m.label} className="space-y-1">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-300 font-medium flex items-center space-x-1.5">
              <span>{m.label}</span>
              <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.2 rounded">
                w: {m.weight}
              </span>
            </span>
            <span className="font-mono font-bold text-cyan-300 text-xs">
              {(m.score * 100).toFixed(0)} <span className="text-[10px] text-slate-400">/100</span>
            </span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden p-0.5">
            <div
              className={`h-full bg-gradient-to-r ${m.color} rounded-full transition-all duration-500`}
              style={{ width: `${Math.min(100, Math.max(4, m.score * 100))}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};
