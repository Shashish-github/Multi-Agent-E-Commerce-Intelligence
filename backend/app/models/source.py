import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String(100), nullable=False)  # e.g., "Amazon", "BestBuy", "DirectManufacturer", "VerifiedLab"
    source_url = Column(String(1024), nullable=True)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    freshness_status = Column(String(50), default="FRESH", nullable=False)  # FRESH, STALE, ARCHIVED

    product_attributes = relationship("ProductAttribute", back_populates="source")
    reviews = relationship("Review", back_populates="source")
    evidence_items = relationship("Evidence", back_populates="source")
