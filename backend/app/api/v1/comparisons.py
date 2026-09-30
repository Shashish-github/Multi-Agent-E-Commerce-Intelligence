"""
Product Comparison API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.comparison_service import ComparisonService
from app.schemas.investigation import ComparisonRequest, ComparisonMatrixOut

router = APIRouter(prefix="/comparisons", tags=["Comparisons"])


@router.post("", response_model=ComparisonMatrixOut)
async def compare_products(
    data: ComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a side-by-side spec and aspect comparison matrix for 2-5 products."""
    return await ComparisonService.compare_products(db, data.product_ids)
