import React, { useState, useEffect } from 'react';
import { GitCompare, X } from 'lucide-react';
import type { ComparisonMatrix } from '../types';
import { compareProducts } from '../lib/api';

interface ComparisonViewProps {
  selectedProductIds: string[];
  onRemoveProduct: (id: string) => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  selectedProductIds,
  onRemoveProduct
}) => {
  const [matrix, setMatrix] = useState<ComparisonMatrix | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedProductIds.length >= 2) {
      setLoading(true);
      setError(null);
      compareProducts(selectedProductIds)
        .then(data => setMatrix(data))
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    } else {
      setMatrix(null);
    }
  }, [selectedProductIds]);

  if (selectedProductIds.length < 2) {
    return (
      <div className="text-center py-24 glass-panel rounded-3xl border border-slate-800 p-8 max-w-2xl mx-auto space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500">
          <GitCompare className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-white">Select at least 2 products to compare</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          Navigate to the <span className="text-cyan-400 font-semibold">Investigate</span> tab and click <span className="text-slate-200 font-mono text-[11px] bg-slate-800 px-1.5 py-0.5 rounded">+ Compare</span> on candidate cards to generate a synchronized attribute & review aspect matrix.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-24 text-cyan-400 font-mono animate-pulse">
        Generating multi-product comparison matrix...
      </div>
    );
  }

  if (error || !matrix) {
    return (
      <div className="text-center py-16 text-rose-400 font-mono">
        {error || 'Failed to load comparison'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <GitCompare className="w-5 h-5 text-cyan-400" />
            <h2 className="text-xl font-bold text-white">Synchronized Product Comparison Matrix</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">{matrix.comparison_summary}</p>
        </div>
      </div>

      <div className="glass-panel rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            
            {/* Header: Products */}
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/80">
                <th className="p-4 text-xs font-mono font-bold text-slate-400 uppercase w-1/4">
                  Feature / Aspect
                </th>
                {matrix.products.map(p => (
                  <th key={p.id} className="p-4 text-xs font-bold text-white min-w-[220px]">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-extrabold">{p.canonical_name}</span>
                        <button
                          onClick={() => onRemoveProduct(p.id)}
                          className="text-slate-500 hover:text-rose-400 p-1"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-cyan-300 font-bold">
                          ₹{p.normalized_price.toLocaleString('en-IN')}
                        </span>
                        <span className="text-[10px] text-slate-400 uppercase font-mono">{p.brand}</span>
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>

            {/* Technical Specification Matrix */}
            <tbody className="divide-y divide-slate-800/60 text-xs">
              <tr className="bg-slate-950/40">
                <td colSpan={matrix.products.length + 1} className="py-2.5 px-4 font-mono font-bold text-cyan-400 text-[11px] uppercase tracking-wider">
                  Technical Specifications
                </td>
              </tr>
              {Object.entries(matrix.attribute_matrix).map(([attrName, productMap]) => (
                <tr key={attrName} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-mono text-slate-400 capitalize">
                    {attrName.replace(/_/g, ' ')}
                  </td>
                  {matrix.products.map(p => (
                    <td key={p.id} className="p-4 text-slate-200 font-medium">
                      {productMap[p.id] || '—'}
                    </td>
                  ))}
                </tr>
              ))}

              {/* Aspect Sentiment Consensus Matrix */}
              <tr className="bg-slate-950/40">
                <td colSpan={matrix.products.length + 1} className="py-2.5 px-4 font-mono font-bold text-emerald-400 text-[11px] uppercase tracking-wider">
                  Review Aspect Sentiment Consensus
                </td>
              </tr>
              {Object.entries(matrix.aspect_matrix).map(([aspectName, productMap]) => (
                <tr key={aspectName} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-mono text-slate-400 capitalize">
                    {aspectName.replace(/_/g, ' ')}
                  </td>
                  {matrix.products.map(p => (
                    <td key={p.id} className="p-4 text-slate-200 font-medium">
                      {productMap[p.id] || '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>

          </table>
        </div>
      </div>
    </div>
  );
};
