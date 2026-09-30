import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, Loader2, Terminal } from 'lucide-react';
import type { AgentRun } from '../types';

interface LivePipelineProps {
  agentRuns: AgentRun[];
  isRunning: boolean;
}

const AGENT_SEQUENCE = [
  { id: 'QueryUnderstandingAgent', label: 'Query Understanding', desc: 'Category, constraints & intent extraction' },
  { id: 'ProductDiscoveryAgent', label: 'Product Discovery', desc: 'Catalog retrieval & deduplication' },
  { id: 'SpecificationAgent', label: 'Specification Validation', desc: 'Hardware spec compliance audit' },
  { id: 'ReviewIntelligenceAgent', label: 'Review Intelligence', desc: 'Aspect sentiment & pros/cons extraction' },
  { id: 'PriceValueAgent', label: 'Price / Value Analysis', desc: 'Budget fit & spec-to-price index' },
  { id: 'TrustEvidenceAgent', label: 'Trust & Evidence Verification', desc: 'Multi-source audit & fact checking' },
  { id: 'RecommendationAgent', label: 'Recommendation Synthesis', desc: 'Deterministic ranking & explainability' }
];

export const LivePipeline: React.FC<LivePipelineProps> = ({ agentRuns, isRunning }) => {
  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 mb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold tracking-wide uppercase text-slate-200 font-mono">
            Autonomous Multi-Agent Orchestrator Pipeline
          </h3>
        </div>
        {isRunning && (
          <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-800/60 animate-pulse">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>ORCHESTRATING WORKFLOW...</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
        {AGENT_SEQUENCE.map((agent, index) => {
          const run = agentRuns.find(r => r.agent_name === agent.id);
          const isCompleted = run && run.status === 'COMPLETED';
          const isDegraded = run && run.status === 'DEGRADED';
          const isFailed = run && run.status === 'FAILED';
          const isExecuting = isRunning && !run && (index === 0 || !!agentRuns[index - 1]);

          let statusBg = 'bg-slate-900/60 border-slate-800 text-slate-500';
          let icon = <Clock className="w-4 h-4 text-slate-600" />;

          if (isCompleted) {
            statusBg = 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300 shadow-sm';
            icon = <CheckCircle2 className="w-4 h-4 text-cyan-400" />;
          } else if (isExecuting) {
            statusBg = 'bg-cyan-900/30 border-cyan-400 text-cyan-300 animate-pulse';
            icon = <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />;
          } else if (isDegraded) {
            statusBg = 'bg-amber-950/40 border-amber-500/40 text-amber-300';
            icon = <AlertTriangle className="w-4 h-4 text-amber-400" />;
          } else if (isFailed) {
            statusBg = 'bg-rose-950/40 border-rose-500/40 text-rose-300';
            icon = <AlertTriangle className="w-4 h-4 text-rose-400" />;
          }

          return (
            <div
              key={agent.id}
              className={`p-3 rounded-xl border transition-all flex flex-col justify-between ${statusBg}`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] text-slate-400 font-bold">0{index + 1}</span>
                  {icon}
                </div>
                <h4 className="text-xs font-semibold text-slate-100 leading-snug mb-1">{agent.label}</h4>
                <p className="text-[10px] text-slate-400 leading-tight">{agent.desc}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono">
                <span className="text-slate-400">Duration</span>
                <span className="text-cyan-400 font-semibold">{run ? `${run.duration_ms}ms` : '—'}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
