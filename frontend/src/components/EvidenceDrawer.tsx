import React from 'react';
import { X, ShieldCheck, HelpCircle, AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { EvidenceItem } from '../types';

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  productName: string;
  evidenceItems: EvidenceItem[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  isOpen,
  onClose,
  productName,
  evidenceItems
}) => {
  if (!isOpen) return null;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/80 text-[10px] font-mono text-emerald-300">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span>VERIFIED FACT</span>
          </span>
        );
      case 'INFERRED':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-800/80 text-[10px] font-mono text-cyan-300">
            <CheckCircle2 className="w-3 h-3 text-cyan-400" />
            <span>INFERRED EVIDENCE</span>
          </span>
        );
      case 'UNCERTAIN':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-950/60 border border-amber-800/80 text-[10px] font-mono text-amber-300">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span>UNCERTAIN</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-400">
            <HelpCircle className="w-3 h-3" />
            <span>UNAVAILABLE</span>
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-slate-700 p-6 shadow-2xl relative max-h-[85vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-bold text-white">Verifiable Evidence Audit Dossier</h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">Grounding claims & verified sources for <span className="text-cyan-300 font-semibold">{productName}</span></p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Evidence List */}
        <div className="mt-4 overflow-y-auto space-y-4 pr-1 flex-1">
          {evidenceItems.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-sm">
              No evidence claims recorded for this candidate.
            </div>
          ) : (
            evidenceItems.map((item, idx) => (
              <div
                key={item.id || idx}
                className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
                    [{item.evidence_type.replace('_', ' ')}]
                  </span>
                  {getStatusBadge(item.status)}
                </div>

                <h4 className="text-sm font-semibold text-slate-100">{item.claim}</h4>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/60">
                  "{item.supporting_text}"
                </p>

                <div className="flex items-center justify-between pt-1 text-[11px] text-slate-400 font-mono">
                  <span>Confidence: <strong className="text-cyan-400">{(item.confidence * 100).toFixed(0)}%</strong></span>
                  {item.source_provider && (
                    <span className="flex items-center space-x-1 text-slate-300">
                      <span>Source:</span>
                      <span className="text-cyan-300">{item.source_provider}</span>
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
          >
            Close Dossier
          </button>
        </div>

      </div>
    </div>
  );
};
