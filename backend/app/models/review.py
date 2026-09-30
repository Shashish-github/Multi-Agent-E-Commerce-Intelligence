import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    author = Column(String(100), nullable=True)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    review_text = Column(Text, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    product = relationship("Product", back_populates="reviews")
    source = relationship("Source", back_populates="reviews")
    aspects = relationship("ReviewAspect", back_populates="review", cascade="all, delete-orphan")


class ReviewAspect(Base):
    __tablename__ = "review_aspects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect = Column(String(100), nullable=False, index=True)  # e.g., "battery", "performance", "build_quality", "display", "thermals", "value"
    sentiment = Column(String(20), nullable=False)  # "POSITIVE", "NEGATIVE", "NEUTRAL"
    confidence = Column(Float, default=1.0, nullable=False)

    review = relationship("Review", back_populates="aspects")
