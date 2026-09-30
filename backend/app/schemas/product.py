from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class SourceOut(BaseModel):
    id: str
    provider: str
    source_url: Optional[str] = None
    freshness_status: str
    model_config = ConfigDict(from_attributes=True)


class ProductAttributeOut(BaseModel):
    id: str
    attribute_name: str
    normalized_value: str
    raw_value: Optional[str] = None
    unit: Optional[str] = None
    confidence: float
    model_config = ConfigDict(from_attributes=True)


class ReviewAspectOut(BaseModel):
    id: str
    aspect: str
    sentiment: str
    confidence: float
    model_config = ConfigDict(from_attributes=True)


class ReviewOut(BaseModel):
    id: str
    product_id: str
    author: Optional[str] = None
    rating: float
    review_text: str
    language: str
    created_at: datetime
    aspects: List[ReviewAspectOut] = []
    model_config = ConfigDict(from_attributes=True)


class ProductOut(BaseModel):
    id: str
    canonical_name: str
    category: str
    brand: str
    normalized_price: float
    currency: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    source_count: int
    model_config = ConfigDict(from_attributes=True)


class ProductDetailOut(ProductOut):
    attributes: List[ProductAttributeOut] = []
    reviews: List[ReviewOut] = []
    rating_average: Optional[float] = None
    review_count: int = 0
