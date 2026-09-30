from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict


class HardConstraint(BaseModel):
    field: str                       # e.g. "price", "ram_gb", "storage_gb", "brand", "os", "screen_size_inch"
    operator: str                    # "<=", ">=", "==", "contains", "in"
    value: Union[float, int, str, List[str]]
    unit: Optional[str] = None


class SoftPreference(BaseModel):
    field: str                       # e.g. "battery_life", "lightweight", "brand", "build_quality"
    preferred_direction: Optional[str] = "MAX"  # "MAX", "MIN", "MATCH"
    target_value: Optional[str] = None
    importance: str = "MEDIUM"       # "HIGH", "MEDIUM", "LOW"


class ParsedConstraints(BaseModel):
    category: str
    budget_max: Optional[float] = None
    currency: str = "INR"
    hard_constraints: List[HardConstraint] = []
    soft_preferences: List[SoftPreference] = []
    exclusions: List[str] = []
    ambiguity_score: float = 0.0     # 0.0 (crystal clear) to 1.0 (highly ambiguous)
    confidence: float = 1.0


class AspectSummary(BaseModel):
    aspect: str
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    aspect_score: float = 0.0        # -1.0 to 1.0
    key_quotes: List[str] = []


class ReviewIntelligenceOutput(BaseModel):
    product_id: str
    aspect_summaries: Dict[str, AspectSummary] = {}
    overall_sentiment_score: float = 0.0   # 0.0 to 1.0
    recurring_strengths: List[str] = []
    recurring_complaints: List[str] = []
    suspicious_volume_flag: bool = False
    evidence_confidence: float = 1.0


class PriceValueOutput(BaseModel):
    product_id: str
    price: float
    budget_fit_ratio: float          # <= 1.0 within budget
    price_percentile_in_category: float
    feature_to_price_index: float    # 0.0 to 1.0
    value_verdict: str


class TrustAuditOutput(BaseModel):
    product_id: str
    confidence_level: str            # "VERIFIED", "INFERRED", "UNCERTAIN", "UNAVAILABLE"
    confidence_score: float          # 0.0 to 1.0
    flags: List[str] = []
    data_freshness: str = "FRESH"


class AgentRunOut(BaseModel):
    id: str
    agent_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    error_code: Optional[str] = None
    token_usage: int = 0
    metadata_json: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)
