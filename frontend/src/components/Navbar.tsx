import React from 'react';
import { Cpu, Search, GitCompare, Activity } from 'lucide-react';

interface NavbarProps {
  activeTab: 'investigate' | 'compare' | 'observability';
  setActiveTab: (tab: 'investigate' | 'compare' | 'observability') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 bg-[#080C14]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Identity */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('investigate')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-cyan-400 to-emerald-400 p-0.5 glow-brand">
            <div className="w-full h-full bg-[#0B0F17] rounded-[10px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                NEXUS<span className="text-cyan-400 font-mono text-sm ml-1 px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/60">AGENTS</span>
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">Autonomous Commerce Intelligence</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('investigate')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'investigate'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Investigate</span>
          </button>

          <button
            onClick={() => setActiveTab('compare')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'compare'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>Comparison Matrix</span>
          </button>

          <button
            onClick={() => setActiveTab('observability')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'observability'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Agent Telemetry</span>
          </button>
        </nav>

        {/* System Health / Badge */}
        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/50 text-[11px] text-emerald-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>7 AGENTS ACTIVE</span>
          </div>
        </div>

      </div>
    </header>
  );
};
