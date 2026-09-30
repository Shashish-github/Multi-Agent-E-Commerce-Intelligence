import React, { useState } from 'react';
import { Trophy, CheckCircle2, AlertCircle, ShieldCheck, Sparkles } from 'lucide-react';
import type { CandidateResult } from '../types';
import { ScoreMatrix } from './ScoreMatrix';
import { EvidenceDrawer } from './EvidenceDrawer';

interface WinnerSpotlightProps {
  winner: CandidateResult;
  onCompareToggle?: (productId: string) => void;
  isCompared?: boolean;
}

export const WinnerSpotlight: React.FC<WinnerSpotlightProps> = ({
  winner,
  onCompareToggle,
  isCompared = false
}) => {
  const [showEvidence, setShowEvidence] = useState(false);
  const { product, score_breakdown, explanation, evidence } = winner;

  return (
    <>
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-cyan-500/30 relative overflow-hidden glow-brand mb-8">
        
        {/* Ambient Top Glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

        {/* Top Header Badge */}
        <div className="flex items-center justify-between flex-wrap gap-3 pb-6 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-300 flex items-center justify-center text-slate-950 font-black shadow-lg">
              <Trophy className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-amber-400">
                #1 Top Recommended Choice
              </span>
              <h2 className="text-2xl font-extrabold text-white tracking-tight">{product.canonical_name}</h2>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="text-right">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Overall Match Score</span>
              <span className="text-2xl font-black font-mono bg-gradient-to-r from-cyan-300 to-emerald-300 bg-clip-text text-transparent">
                {(winner.score * 100).toFixed(1)}<span className="text-sm text-slate-400 font-normal">/100</span>
              </span>
            </div>
            <div className="px-4 py-2 rounded-2xl bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 font-mono font-bold text-sm">
              ₹{product.normalized_price.toLocaleString('en-IN')}
            </div>
          </div>
        </div>

        {/* Content Body Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 pt-6">
          
          {/* Left Column: Why It Won Narrative & Highlights */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* Why It Won Narrative Box */}
            <div className="p-4 rounded-2xl bg-gradient-to-br from-cyan-950/40 via-slate-900/60 to-slate-900/80 border border-cyan-800/40">
              <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold font-mono uppercase tracking-wider mb-2">
                <Sparkles className="w-4 h-4" />
                <span>Autonomous Recommendation Thesis</span>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed font-medium">
                {explanation.why_it_won}
              </p>
            </div>

            {/* Highlights & Trade-offs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              {/* Highlights */}
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2.5">
                <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase font-mono">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Key Strengths</span>
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {explanation.highlights.map((h, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-emerald-400 font-bold mt-0.5">•</span>
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Trade-offs */}
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2.5">
                <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold uppercase font-mono">
                  <AlertCircle className="w-4 h-4" />
                  <span>Realistic Trade-offs</span>
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {explanation.trade_offs.map((t, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-amber-400 font-bold mt-0.5">•</span>
                      <span>{t}</span>
                    </li>
                  ))}
                </ul>
              </div>

            </div>

            {/* Reason Codes Pills */}
            <div className="flex flex-wrap gap-2 pt-1">
              {explanation.reason_codes.map((code, i) => (
                <span key={i} className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300">
                  #{code}
                </span>
              ))}
            </div>

            {/* Evidence & Compare CTA buttons */}
            <div className="flex items-center space-x-3 pt-2">
              <button
                onClick={() => setShowEvidence(true)}
                className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs transition-all shadow-md hover:shadow-cyan-500/20"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Inspect Evidence Audit ({evidence.length} Claims)</span>
              </button>

              {onCompareToggle && (
                <button
                  onClick={() => onCompareToggle(product.id)}
                  className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all border ${
                    isCompared
                      ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
                      : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200'
                  }`}
                >
                  <span>{isCompared ? '✓ Added to Comparison' : '+ Add to Comparison'}</span>
                </button>
              )}
            </div>

          </div>

          {/* Right Column: 6-Factor Deterministic Score Breakdown */}
          <div className="lg:col-span-5 p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                  Transparent Score Breakdown
                </span>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">
                  Deterministic
                </span>
              </div>
              <ScoreMatrix scoreBreakdown={score_breakdown} />
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
              <span>Confidence Level:</span>
              <span className="font-mono text-emerald-400 font-bold">
                {explanation.confidence_level}
              </span>
            </div>
          </div>

        </div>

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
