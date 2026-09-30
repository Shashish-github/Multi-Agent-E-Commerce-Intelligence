export interface HardConstraint {
  field: string;
  operator: string;
  value: number | string | string[];
  unit?: string;
}

export interface SoftPreference {
  field: string;
  preferred_direction?: string;
  target_value?: string;
  importance: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface ParsedConstraints {
  category: string;
  budget_max?: number;
  currency: string;
  hard_constraints: HardConstraint[];
  soft_preferences: SoftPreference[];
  exclusions: string[];
  ambiguity_score: number;
  confidence: number;
}

export interface ProductAttribute {
  id: string;
  attribute_name: string;
  normalized_value: string;
  raw_value?: string;
  unit?: string;
  confidence: number;
}

export interface Product {
  id: string;
  canonical_name: string;
  category: string;
  brand: string;
  normalized_price: number;
  currency: string;
  image_url?: string;
  description?: string;
  source_count: number;
}

export interface ScoreBreakdown {
  requirement_fit: number;
  review_quality: number;
  price_value: number;
  spec_strength: number;
  reliability_evidence: number;
  preference_match: number;
  final_score: number;
}

export interface ExplanationDetail {
  why_it_won: string;
  highlights: string[];
  trade_offs: string[];
  reason_codes: string[];
  failed_constraints: string[];
  confidence_level: 'VERIFIED' | 'INFERRED' | 'UNCERTAIN' | 'UNAVAILABLE';
}

export interface EvidenceItem {
  id: string;
  product_id: string;
  evidence_type: string;
  claim: string;
  supporting_text: string;
  confidence: number;
  status: 'VERIFIED' | 'INFERRED' | 'UNCERTAIN' | 'UNAVAILABLE';
  source_provider?: string;
}

export interface CandidateResult {
  product: Product;
  rank: number;
  score: number;
  fit_status: 'COMPLIANT' | 'PARTIALLY_COMPLIANT' | 'NON_COMPLIANT' | 'UNCERTAIN';
  score_breakdown: ScoreBreakdown;
  explanation: ExplanationDetail;
  evidence: EvidenceItem[];
}

export interface AgentRun {
  id: string;
  agent_name: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  duration_ms: number;
  error_code?: string;
  token_usage: number;
  metadata_json?: Record<string, any>;
}

export interface RankingWeights {
  weight_requirement_fit: number;
  weight_review_quality: number;
  weight_price_value: number;
  weight_spec_strength: number;
  weight_reliability: number;
  weight_preference_match: number;
}

export interface InvestigationDetail {
  id: string;
  original_query: string;
  parsed_constraints?: ParsedConstraints;
  weights?: RankingWeights;
  status: 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  created_at: string;
  completed_at?: string;
  candidates: CandidateResult[];
  agent_runs: AgentRun[];
}

export interface ComparisonMatrix {
  products: Product[];
  attribute_matrix: Record<string, Record<string, any>>;
  aspect_matrix: Record<string, Record<string, any>>;
  winner_id?: string;
  comparison_summary: string;
}
