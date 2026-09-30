import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_query = Column(Text, nullable=False)
    parsed_constraints = Column(JSON, nullable=True)  # category, budget_max, hard_constraints, soft_preferences, exclusions
    weights = Column(JSON, nullable=True)             # custom scoring weights
    status = Column(String(50), default="QUEUED", nullable=False)  # QUEUED, RUNNING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="investigations")
    candidates = relationship("InvestigationCandidate", back_populates="investigation", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="investigation", cascade="all, delete-orphan")


class InvestigationCandidate(Base):
    __tablename__ = "investigation_candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.0)
    rank = Column(Integer, nullable=False, default=0)
    fit_status = Column(String(50), default="COMPLIANT", nullable=False)  # COMPLIANT, NON_COMPLIANT, UNCERTAIN
    score_breakdown = Column(JSON, nullable=True)  # fit_score, review_score, price_score, spec_score, reliability_score, pref_score
    explanation = Column(JSON, nullable=True)      # why_it_won, trade_offs, highlights, reason_codes

    investigation = relationship("Investigation", back_populates="candidates")
    product = relationship("Product", back_populates="candidates")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False)  # SPECIFICATION, REVIEW_CONSENSUS, PRICE_VALUE, TRUST_AUDIT
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    claim = Column(String(255), nullable=False)
    supporting_text = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    status = Column(String(50), default="VERIFIED", nullable=False)  # VERIFIED, INFERRED, UNCERTAIN, UNAVAILABLE
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    investigation = relationship("Investigation", back_populates="evidence_items")
    product = relationship("Product", back_populates="evidence_items")
    source = relationship("Source", back_populates="evidence_items")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, RUNNING, COMPLETED, FAILED, DEGRADED
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, default=0.0, nullable=False)
    error_code = Column(String(100), nullable=True)
    token_usage = Column(Integer, default=0, nullable=False)
    metadata_json = Column(JSON, nullable=True)

    investigation = relationship("Investigation", back_populates="agent_runs")
