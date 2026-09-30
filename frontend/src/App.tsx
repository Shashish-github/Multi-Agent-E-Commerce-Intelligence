import React, { useState, useEffect } from 'react';
import { Search, Sparkles, ArrowRight, AlertCircle, Layers } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { LivePipeline } from './components/LivePipeline';
import { WinnerSpotlight } from './components/WinnerSpotlight';
import { CandidateCard } from './components/CandidateCard';
import { WhatIfWorkspace } from './components/WhatIfWorkspace';
import { ComparisonView } from './components/ComparisonView';
import { ObservabilityView } from './components/ObservabilityView';
import type { InvestigationDetail, RankingWeights } from './types';
import { createInvestigation, rerankInvestigation } from './lib/api';

const PRESET_PROMPTS = [
  "Find a laptop under ₹90,000 for machine learning with at least 16GB RAM and great battery life",
  "Need a lightweight coding laptop below 85k with 16GB RAM and Linux support",
  "Affordable student laptop under 70000 with OLED screen and 16GB RAM",
  "Dell 4K monitor under 55000 with 90W USB-C PD hub",
  "Google Pixel phone under 85000 for low light photography"
];

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'investigate' | 'compare' | 'observability'>('investigate');
  const [query, setQuery] = useState(PRESET_PROMPTS[0]);
  const [investigation, setInvestigation] = useState<InvestigationDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isReranking, setIsReranking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comparedProductIds, setComparedProductIds] = useState<string[]>([]);

  // Trigger default investigation on first mount
  useEffect(() => {
    handleSearch(PRESET_PROMPTS[0]);
  }, []);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await createInvestigation(searchQuery);
      setInvestigation(result);
      // Auto populate first 2 candidates for comparison if empty
      if (result.candidates.length >= 2 && comparedProductIds.length === 0) {
        setComparedProductIds([result.candidates[0].product.id, result.candidates[1].product.id]);
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while running the investigation.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRerank = async (options: { weights: RankingWeights; override_budget_max?: number }) => {
    if (!investigation) return;
    setIsReranking(true);
    try {
      const updated = await rerankInvestigation(investigation.id, options);
      setInvestigation(updated);
    } catch (err: any) {
      console.error('Re-rank failed:', err);
    } finally {
      setIsReranking(false);
    }
  };

  const handleCompareToggle = (productId: string) => {
    setComparedProductIds(prev =>
      prev.includes(productId) ? prev.filter(id => id !== productId) : [...prev, productId]
    );
  };

  const winner = investigation?.candidates?.[0];
  const alternatives = investigation?.candidates?.slice(1) || [];

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-slate-950">
      
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-8">
        
        {/* Tab 1: Investigate Workspace */}
        {activeTab === 'investigate' && (
          <div className="space-y-8">
            
            {/* Search Query Command Center */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 relative overflow-hidden shadow-2xl">
              <div className="max-w-3xl">
                <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-800/80 text-[11px] font-mono text-cyan-300 mb-3">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Autonomous Multi-Agent Query Decomposer</span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  What product are you researching today?
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 mt-1">
                  Submit natural-language requirements. Our 7 AI agents extract hard constraints, audit reviews, calculate value indices, and build a verifiable evidence dossier.
                </p>
              </div>

              {/* Input Form */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearch(query);
                }}
                className="mt-6 flex flex-col sm:flex-row gap-3"
              >
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. Find a laptop under ₹90,000 for machine learning with 16GB RAM and great battery life..."
                    className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 text-sm transition-all shadow-inner"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 font-extrabold text-sm flex items-center justify-center space-x-2 transition-all shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 cursor-pointer"
                >
                  <span>{isLoading ? 'Agents Analyzing...' : 'Investigate'}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>

              {/* Preset Quick Chips */}
              <div className="mt-4 flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
                <span className="text-slate-500 font-mono text-[11px] whitespace-nowrap">Examples:</span>
                {PRESET_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setQuery(prompt);
                      handleSearch(prompt);
                    }}
                    className="whitespace-nowrap px-3 py-1 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-cyan-300 transition-colors text-[11px]"
                  >
                    {prompt.length > 55 ? prompt.slice(0, 55) + '...' : prompt}
                  </button>
                ))}
              </div>

              {/* Auto-extracted Constraint Badges */}
              {investigation?.parsed_constraints && (
                <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
                  <span className="text-xs font-mono text-slate-400 font-semibold mr-1">Extracted Constraints:</span>
                  <span className="px-2.5 py-1 rounded-lg bg-cyan-950/80 border border-cyan-800/80 text-cyan-300 font-mono text-xs font-bold uppercase">
                    Category: {investigation.parsed_constraints.category}
                  </span>
                  {investigation.parsed_constraints.budget_max && (
                    <span className="px-2.5 py-1 rounded-lg bg-emerald-950/80 border border-emerald-800/80 text-emerald-300 font-mono text-xs font-bold">
                      Budget: ≤ ₹{investigation.parsed_constraints.budget_max.toLocaleString('en-IN')}
                    </span>
                  )}
                  {investigation.parsed_constraints.hard_constraints.filter(h => h.field !== 'price').map((hc, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 font-mono text-xs">
                      {hc.field.toUpperCase()} {hc.operator} {String(hc.value)}{hc.unit || ''}
                    </span>
                  ))}
                  {investigation.parsed_constraints.soft_preferences.map((sp, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg bg-purple-950/60 border border-purple-800/60 text-purple-300 font-mono text-xs">
                      Pref: {sp.field.replace(/_/g, ' ')} ({sp.preferred_direction || sp.target_value})
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Live Agent Execution Pipeline */}
            <LivePipeline
              agentRuns={investigation?.agent_runs || []}
              isRunning={isLoading}
            />

            {/* Error Message if any */}
            {error && (
              <div className="p-4 rounded-2xl bg-rose-950/60 border border-rose-800 text-rose-300 text-sm flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Results Grid (Winner Spotlight + Alternatives + What-If Workspace) */}
            {investigation && winner && (
              <div className="space-y-8">
                
                {/* Winner #1 Spotlight */}
                <WinnerSpotlight
                  winner={winner}
                  onCompareToggle={handleCompareToggle}
                  isCompared={comparedProductIds.includes(winner.product.id)}
                />

                {/* 2-Column Split: Alternative Ranked Candidates & What-If Workspace */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                  
                  {/* Left Column: Alternatives */}
                  <div className="lg:col-span-8 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Layers className="w-4 h-4 text-cyan-400" />
                        <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
                          Ranked Alternatives & Non-Compliant Candidates ({alternatives.length})
                        </h3>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {alternatives.map((cand) => (
                        <CandidateCard
                          key={cand.product.id}
                          candidate={cand}
                          onCompareToggle={handleCompareToggle}
                          isCompared={comparedProductIds.includes(cand.product.id)}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Right Column: Interactive What-If Console */}
                  <div className="lg:col-span-4 sticky top-24">
                    <WhatIfWorkspace
                      initialWeights={investigation.weights}
                      initialBudget={investigation.parsed_constraints?.budget_max}
                      onRerank={handleRerank}
                      isReranking={isReranking}
                    />
                  </div>

                </div>

              </div>
            )}

          </div>
        )}

        {/* Tab 2: Synchronized Comparison Matrix */}
        {activeTab === 'compare' && (
          <ComparisonView
            selectedProductIds={comparedProductIds}
            onRemoveProduct={(id) => setComparedProductIds(prev => prev.filter(pId => pId !== id))}
          />
        )}

        {/* Tab 3: Agent Observability & Telemetry */}
        {activeTab === 'observability' && (
          <ObservabilityView agentRuns={investigation?.agent_runs || []} />
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#0B0F17] py-6 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Autonomous Multi-Agent E-Commerce Intelligence Platform v1.0.0</span>
          <span>FastAPI • PostgreSQL • Redis • React • Deterministic Multi-Factor Ranking</span>
        </div>
      </footer>

    </div>
  );
};

export default App;
