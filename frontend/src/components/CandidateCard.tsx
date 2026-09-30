import React, { useState } from 'react';
import { ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import type { CandidateResult } from '../types';
import { ScoreMatrix } from './ScoreMatrix';
import { EvidenceDrawer } from './EvidenceDrawer';

interface CandidateCardProps {
  candidate: CandidateResult;
  onCompareToggle?: (productId: string) => void;
  isCompared?: boolean;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  onCompareToggle,
  isCompared = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  const { product, rank, score, fit_status, score_breakdown, explanation, evidence } = candidate;

  const isCompliant = fit_status === 'COMPLIANT';

  return (
    <>
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 glass-panel-hover transition-all">
        <div className="flex items-start justify-between flex-wrap gap-3">
          
          <div className="flex items-start space-x-3.5">
            <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-mono font-bold text-slate-300 text-sm">
              #{rank}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">{product.canonical_name}</h3>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                    isCompliant
                      ? 'bg-emerald-950/60 border-emerald-800/80 text-emerald-400'
                      : 'bg-amber-950/60 border-amber-800/80 text-amber-400'
                  }`}
                >
                  {fit_status}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{product.brand} • {product.category.toUpperCase()}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="text-right">
              <span className="text-[10px] font-mono text-slate-400 block">Score</span>
              <span className="text-lg font-bold font-mono text-cyan-300">
                {(score * 100).toFixed(1)}
              </span>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 font-mono font-semibold text-xs">
              ₹{product.normalized_price.toLocaleString('en-IN')}
            </div>
          </div>

        </div>

        {/* Narrative & Highlights Summary */}
        <p className="text-xs text-slate-300 mt-3 leading-relaxed">
          {explanation.why_it_won}
        </p>

        {/* Compact Metrics Bar */}
        <div className="mt-4 pt-3 border-t border-slate-800/70">
          <ScoreMatrix scoreBreakdown={score_breakdown} compact={true} />
        </div>

        {/* Expand / Actions footer */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowEvidence(true)}
              className="flex items-center space-x-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium py-1 px-2.5 rounded-lg hover:bg-cyan-950/40 transition-colors"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Evidence ({evidence.length})</span>
            </button>

            {onCompareToggle && (
              <button
                onClick={() => onCompareToggle(product.id)}
                className={`text-xs py-1 px-2.5 rounded-lg font-medium transition-colors ${
                  isCompared
                    ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {isCompared ? '✓ Comparing' : '+ Compare'}
              </button>
            )}
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 py-1 px-2 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <span>{isExpanded ? 'Hide Details' : 'Full Specs'}</span>
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Expanded Full Details */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-slate-800 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="text-emerald-400 font-bold uppercase font-mono text-[10px] mb-1">Strengths</div>
                <ul className="space-y-1 text-slate-300">
                  {explanation.highlights.map((h, i) => (
                    <li key={i}>• {h}</li>
                  ))}
                </ul>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="text-amber-400 font-bold uppercase font-mono text-[10px] mb-1">Trade-offs</div>
                <ul className="space-y-1 text-slate-300">
                  {explanation.trade_offs.map((t, i) => (
                    <li key={i}>• {t}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

      </div>

      <EvidenceDrawer
        isOpen={showEvidence}
        onClose={() => setShowEvidence(false)}
        productName={product.canonical_name}
        evidenceItems={evidence}
      />
    </>
  );
};
