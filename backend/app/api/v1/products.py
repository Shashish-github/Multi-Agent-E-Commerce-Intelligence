"""
Product and Review API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductOut, ProductDetailOut, ReviewOut

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductOut])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    max_price: Optional[float] = Query(None, description="Filter by maximum price"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List canonical catalog products."""
    return await ProductService.list_products(db, category, brand, max_price, limit)


@router.get("/{product_id}", response_model=ProductDetailOut)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve detailed product specifications and reviews."""
    return await ProductService.get_product_detail(db, product_id)


@router.get("/{product_id}/reviews", response_model=List[ReviewOut])
async def get_product_reviews(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve customer reviews for a product."""
    detail = await ProductService.get_product_detail(db, product_id)
    return detail.reviews
