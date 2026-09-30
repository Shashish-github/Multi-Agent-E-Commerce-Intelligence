"""
Product and Review query service.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.errors import NotFoundException
from app.models.product import Product, ProductAttribute
from app.models.review import Review, ReviewAspect
from app.schemas.product import ProductOut, ProductDetailOut, ReviewOut, ProductAttributeOut, ReviewAspectOut


class ProductService:
    @staticmethod
    async def list_products(
        db: AsyncSession,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        limit: int = 50
    ) -> List[ProductOut]:
        query = select(Product)
        if category:
            query = query.filter(Product.category == category.lower())
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        if max_price:
            query = query.filter(Product.normalized_price <= max_price)
        query = query.limit(limit)

        res = await db.execute(query)
        products = res.scalars().all()
        return [ProductOut.model_validate(p) for p in products]

    @staticmethod
    async def get_product_detail(db: AsyncSession, product_id: str) -> ProductDetailOut:
        query = select(Product).options(
            selectinload(Product.attributes),
            selectinload(Product.reviews).selectinload(Review.aspects)
        ).filter(Product.id == product_id)

        res = await db.execute(query)
        p = res.scalars().first()
        if not p:
            raise NotFoundException(f"Product with ID {product_id} not found")

        ratings = [r.rating for r in p.reviews]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        attr_outs = [ProductAttributeOut.model_validate(a) for a in p.attributes]
        rev_outs = []
        for r in p.reviews:
            asp_outs = [ReviewAspectOut.model_validate(asp) for asp in r.aspects]
            rev_outs.append(ReviewOut(
                id=r.id,
                product_id=r.product_id,
                author=r.author,
                rating=r.rating,
                review_text=r.review_text,
                language=r.language,
                created_at=r.created_at,
                aspects=asp_outs
            ))

        return ProductDetailOut(
            id=p.id,
            canonical_name=p.canonical_name,
            category=p.category,
            brand=p.brand,
            normalized_price=p.normalized_price,
            currency=p.currency,
            image_url=p.image_url,
            description=p.description,
            source_count=p.source_count,
            attributes=attr_outs,
            reviews=rev_outs,
            rating_average=avg_rating,
            review_count=len(p.reviews)
        )
