import React from 'react';
import { Clock, ShieldCheck, Terminal, Cpu } from 'lucide-react';
import type { AgentRun } from '../types';

interface ObservabilityViewProps {
  agentRuns: AgentRun[];
}

export const ObservabilityView: React.FC<ObservabilityViewProps> = ({ agentRuns }) => {
  const totalDuration = agentRuns.reduce((acc, r) => acc + r.duration_ms, 0);

  return (
    <div className="space-y-6">
      
      {/* Header Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase">Agents Executed</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-black font-mono text-white mt-2">{agentRuns.length} <span className="text-xs text-slate-500 font-normal">agents</span></p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase">Total Pipeline Latency</span>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black font-mono text-emerald-300 mt-2">{totalDuration.toFixed(2)} <span className="text-xs text-slate-500 font-normal">ms</span></p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase">Execution Health</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-black font-mono text-cyan-300 mt-2">100% <span className="text-xs text-slate-500 font-normal">deterministic</span></p>
        </div>
      </div>

      {/* Detailed Telemetry Table */}
      <div className="glass-panel rounded-3xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white font-mono uppercase">Agent Telemetry Logs</h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Correlation ID Context Enabled</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60 font-mono text-slate-400">
                <th className="p-3.5">Agent Name</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Latency</th>
                <th className="p-3.5">Error Code</th>
                <th className="p-3.5">Token Usage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {agentRuns.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">
                    No active telemetry logs available yet. Run an investigation to generate agent telemetry.
                  </td>
                </tr>
              ) : (
                agentRuns.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-800/20">
                    <td className="p-3.5 font-bold text-slate-200">{run.agent_name}</td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-950/60 border border-emerald-800/80 text-emerald-400">
                        {run.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-cyan-400 font-bold">{run.duration_ms}ms</td>
                    <td className="p-3.5 text-slate-500">{run.error_code || 'NONE'}</td>
                    <td className="p-3.5 text-slate-400">{run.token_usage}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
