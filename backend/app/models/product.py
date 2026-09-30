import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # e.g., "laptop", "smartphone", "monitor", "audio"
    brand = Column(String(100), nullable=False, index=True)
    normalized_price = Column(Float, nullable=False, index=True)
    currency = Column(String(10), default="INR", nullable=False)
    image_url = Column(String(1024), nullable=True)
    description = Column(Text, nullable=True)
    source_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    candidates = relationship("InvestigationCandidate", back_populates="product", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="product", cascade="all, delete-orphan")


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_name = Column(String(100), nullable=False, index=True)  # e.g., "ram_gb", "storage_gb", "cpu", "battery_life_hours", "weight_kg"
    normalized_value = Column(String(255), nullable=False)
    raw_value = Column(String(255), nullable=True)
    unit = Column(String(50), nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    product = relationship("Product", back_populates="attributes")
    source = relationship("Source", back_populates="product_attributes")
