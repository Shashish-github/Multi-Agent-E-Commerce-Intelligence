import React, { useState } from 'react';
import { Sliders, RefreshCw, DollarSign } from 'lucide-react';
import type { RankingWeights } from '../types';

interface WhatIfWorkspaceProps {
  initialWeights?: RankingWeights;
  initialBudget?: number;
  onRerank: (options: { weights: RankingWeights; override_budget_max?: number }) => void;
  isReranking: boolean;
}

export const WhatIfWorkspace: React.FC<WhatIfWorkspaceProps> = ({
  initialWeights,
  initialBudget,
  onRerank,
  isReranking
}) => {
  const [weights, setWeights] = useState<RankingWeights>(
    initialWeights || {
      weight_requirement_fit: 0.30,
      weight_review_quality: 0.20,
      weight_price_value: 0.15,
      weight_spec_strength: 0.15,
      weight_reliability: 0.10,
      weight_preference_match: 0.10,
    }
  );

  const [budget, setBudget] = useState<number | undefined>(initialBudget);

  const handleWeightChange = (key: keyof RankingWeights, val: number) => {
    const updated = { ...weights, [key]: val };
    setWeights(updated);
    onRerank({ weights: updated, override_budget_max: budget });
  };

  const handleBudgetChange = (newBudget: number) => {
    setBudget(newBudget);
    onRerank({ weights, override_budget_max: newBudget });
  };

  const resetDefaults = () => {
    const defaults: RankingWeights = {
      weight_requirement_fit: 0.30,
      weight_review_quality: 0.20,
      weight_price_value: 0.15,
      weight_spec_strength: 0.15,
      weight_reliability: 0.10,
      weight_preference_match: 0.10,
    };
    setWeights(defaults);
    setBudget(initialBudget);
    onRerank({ weights: defaults, override_budget_max: initialBudget });
  };

  return (
    <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-cyan-950/80 border border-cyan-800/80 flex items-center justify-center text-cyan-400">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              "What-If" Re-ranking Console
            </h3>
            <p className="text-[11px] text-slate-400">Live dynamic re-weighting with zero-latency re-evaluation</p>
          </div>
        </div>

        <button
          onClick={resetDefaults}
          className="flex items-center space-x-1 text-xs text-slate-400 hover:text-cyan-300 font-mono py-1 px-2.5 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      {/* Budget Override Slider */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="font-semibold text-slate-300 flex items-center space-x-1.5">
            <DollarSign className="w-3.5 h-3.5 text-amber-400" />
            <span>Target Budget Ceiling</span>
          </span>
          <span className="font-mono font-bold text-amber-400 text-sm">
            ₹{(budget || 90000).toLocaleString('en-IN')}
          </span>
        </div>
        <input
          type="range"
          min="50000"
          max="150000"
          step="5000"
          value={budget || 90000}
          onChange={(e) => handleBudgetChange(Number(e.target.value))}
          className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
        />
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>₹50,000</span>
          <span>₹1,00,000</span>
          <span>₹1,50,000</span>
        </div>
      </div>

      {/* Weight Sliders */}
      <div className="space-y-4">
        <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
          Factor Scoring Weights
        </h4>

        {[
          { key: 'weight_requirement_fit', label: 'Requirement Fit', desc: 'Hard constraint compliance' },
          { key: 'weight_review_quality', label: 'Review Consensus', desc: 'Verified customer sentiment' },
          { key: 'weight_price_value', label: 'Price-to-Value', desc: 'Feature-to-price ratio' },
          { key: 'weight_spec_strength', label: 'Hardware Specs', desc: 'Raw CPU/GPU/RAM tier' },
          { key: 'weight_reliability', label: 'Source Reliability', desc: 'Verified lab audits' },
          { key: 'weight_preference_match', label: 'Preferences', desc: 'Battery, OS & portability' },
        ].map((item) => {
          const val = weights[item.key as keyof RankingWeights];
          return (
            <div key={item.key} className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <div>
                  <span className="text-slate-200 font-medium">{item.label}</span>
                  <span className="text-[10px] text-slate-500 ml-1.5 font-mono">({item.desc})</span>
                </div>
                <span className="font-mono text-cyan-400 font-bold">{(val * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.6"
                step="0.05"
                value={val}
                onChange={(e) => handleWeightChange(item.key as keyof RankingWeights, Number(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>
          );
        })}
      </div>

      {/* Status indicator */}
      {isReranking && (
        <div className="text-center text-xs text-cyan-400 font-mono py-1 animate-pulse">
          Recalculating rank matrix...
        </div>
      )}

    </div>
  );
};
