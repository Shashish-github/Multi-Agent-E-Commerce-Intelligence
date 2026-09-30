"""
Multi-product side-by-side comparison service.
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.errors import NotFoundException
from app.models.product import Product
from app.models.review import Review
from app.schemas.product import ProductOut
from app.schemas.investigation import ComparisonMatrixOut


class ComparisonService:
    @staticmethod
    async def compare_products(
        db: AsyncSession,
        product_ids: List[str]
    ) -> ComparisonMatrixOut:
        query = select(Product).options(
            selectinload(Product.attributes),
            selectinload(Product.reviews).selectinload(Review.aspects)
        ).filter(Product.id.in_(product_ids))

        res = await db.execute(query)
        products = res.scalars().all()
        if not products:
            raise NotFoundException("None of the specified products were found")

        prod_outs = [ProductOut.model_validate(p) for p in products]

        # Build attribute matrix
        all_attr_names = set()
        for p in products:
            for a in p.attributes:
                all_attr_names.add(a.attribute_name)

        attribute_matrix: Dict[str, Dict[str, Any]] = {}
        for attr_name in sorted(all_attr_names):
            attribute_matrix[attr_name] = {}
            for p in products:
                val = next((a.normalized_value for a in p.attributes if a.attribute_name == attr_name), "—")
                unit = next((a.unit for a in p.attributes if a.attribute_name == attr_name and a.unit), "")
                attribute_matrix[attr_name][p.id] = f"{val} {unit}".strip()

        # Build aspect sentiment matrix
        aspect_matrix: Dict[str, Dict[str, Any]] = {
            "battery": {},
            "performance": {},
            "build_quality": {},
            "display": {},
            "value": {}
        }
        for p in products:
            ratings = [r.rating for r in p.reviews]
            avg_r = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

            for aspect_key in aspect_matrix.keys():
                matching_aspects = [
                    asp for r in p.reviews for asp in r.aspects if asp.aspect.lower() == aspect_key
                ]
                pos = sum(1 for a in matching_aspects if a.sentiment == "POSITIVE")
                neg = sum(1 for a in matching_aspects if a.sentiment == "NEGATIVE")
                total = len(matching_aspects)
                sentiment_label = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")
                aspect_matrix[aspect_key][p.id] = f"{sentiment_label} ({pos}👍 / {neg}👎)" if total > 0 else "No data"

        # Determine winner
        winner = min(products, key=lambda p: p.normalized_price) if products else None
        winner_id = winner.id if winner else None

        summary = f"Comparing {len(products)} products across {len(attribute_matrix)} technical specifications and review aspects."

        return ComparisonMatrixOut(
            products=prod_outs,
            attribute_matrix=attribute_matrix,
            aspect_matrix=aspect_matrix,
            winner_id=winner_id,
            comparison_summary=summary
        )
