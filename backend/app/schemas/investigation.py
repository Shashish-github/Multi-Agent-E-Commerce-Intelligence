from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.agent import ParsedConstraints, AgentRunOut
from app.schemas.ranking import RankingWeights, ScoreBreakdown, ExplanationDetail
from app.schemas.product import ProductOut


class InvestigationCreate(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    weights: Optional[RankingWeights] = None


class EvidenceOut(BaseModel):
    id: str
    product_id: str
    evidence_type: str
    claim: str
    supporting_text: str
    confidence: float
    status: str
    source_provider: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CandidateResultOut(BaseModel):
    product: ProductOut
    rank: int
    score: float
    fit_status: str              # COMPLIANT, NON_COMPLIANT, UNCERTAIN
    score_breakdown: ScoreBreakdown
    explanation: ExplanationDetail
    evidence: List[EvidenceOut] = []


class InvestigationSummaryOut(BaseModel):
    id: str
    original_query: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    candidate_count: int = 0
    top_recommendation_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class InvestigationDetailOut(BaseModel):
    id: str
    original_query: str
    parsed_constraints: Optional[ParsedConstraints] = None
    weights: Optional[RankingWeights] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    candidates: List[CandidateResultOut] = []
    agent_runs: List[AgentRunOut] = []


class ComparisonRequest(BaseModel):
    product_ids: List[str] = Field(..., min_length=2, max_length=5)
    investigation_id: Optional[str] = None


class ComparisonMatrixOut(BaseModel):
    products: List[ProductOut]
    attribute_matrix: Dict[str, Dict[str, Any]]  # { attribute_name: { product_id: value } }
    aspect_matrix: Dict[str, Dict[str, Any]]     # { aspect_name: { product_id: sentiment_score } }
    winner_id: Optional[str] = None
    comparison_summary: str
