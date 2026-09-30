from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RankingWeights(BaseModel):
    weight_requirement_fit: float = Field(0.30, ge=0.0, le=1.0)
    weight_review_quality: float = Field(0.20, ge=0.0, le=1.0)
    weight_price_value: float = Field(0.15, ge=0.0, le=1.0)
    weight_spec_strength: float = Field(0.15, ge=0.0, le=1.0)
    weight_reliability: float = Field(0.10, ge=0.0, le=1.0)
    weight_preference_match: float = Field(0.10, ge=0.0, le=1.0)


class ScoreBreakdown(BaseModel):
    requirement_fit: float       # 0.0 to 1.0 (Hard constraints satisfaction)
    review_quality: float        # 0.0 to 1.0
    price_value: float           # 0.0 to 1.0
    spec_strength: float         # 0.0 to 1.0
    reliability_evidence: float  # 0.0 to 1.0
    preference_match: float      # 0.0 to 1.0
    final_score: float           # 0.0 to 1.0


class ExplanationDetail(BaseModel):
    why_it_won: str
    highlights: List[str] = []
    trade_offs: List[str] = []
    reason_codes: List[str] = []
    failed_constraints: List[str] = []
    confidence_level: str = "VERIFIED"  # VERIFIED, INFERRED, UNCERTAIN, UNAVAILABLE


class ReRankRequest(BaseModel):
    weights: Optional[RankingWeights] = None
    override_budget_max: Optional[float] = None
    additional_exclusions: Optional[List[str]] = None
