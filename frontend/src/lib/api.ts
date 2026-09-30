import type { InvestigationDetail, ComparisonMatrix, RankingWeights } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function createInvestigation(query: string, weights?: RankingWeights): Promise<InvestigationDetail> {
  const res = await fetch(`${API_BASE}/investigations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, weights })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error?.message || 'Failed to create investigation');
  }
  return res.json();
}

export async function getInvestigation(id: string): Promise<InvestigationDetail> {
  const res = await fetch(`${API_BASE}/investigations/${id}`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error?.message || 'Failed to fetch investigation');
  }
  return res.json();
}

export async function rerankInvestigation(
  id: string,
  options: { weights?: RankingWeights; override_budget_max?: number; additional_exclusions?: string[] }
): Promise<InvestigationDetail> {
  const res = await fetch(`${API_BASE}/investigations/${id}/rerank`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error?.message || 'Failed to re-rank investigation');
  }
  return res.json();
}

export async function compareProducts(productIds: string[]): Promise<ComparisonMatrix> {
  const res = await fetch(`${API_BASE}/comparisons`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_ids: productIds })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error?.message || 'Failed to generate product comparison');
  }
  return res.json();
}
