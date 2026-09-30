"""
Product Discovery Agent.
Retrieves candidate products matching category, exclusions, and broad constraints.
"""
from typing import Dict, Any, List
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.agents.base import BaseAgent
from app.models.product import Product, ProductAttribute
from app.models.review import Review, ReviewAspect
from app.schemas.agent import ParsedConstraints


class ProductDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ProductDiscoveryAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        parsed: ParsedConstraints = state["parsed_constraints"]
        session = state.get("db_session")

        candidates: List[Dict[str, Any]] = []

        if session is not None:
            # Query from DB with attributes and reviews preloaded
            query = select(Product).options(
                selectinload(Product.attributes),
                selectinload(Product.reviews).selectinload(Review.aspects)
            )

            # Category filter
            if parsed.category:
                query = query.filter(Product.category == parsed.category.lower())

            result = await session.execute(query)
            products = result.scalars().all()

            for p in products:
                # Check exclusions (e.g. brand)
                if any(excl.lower() in p.brand.lower() for excl in parsed.exclusions):
                    continue

                # Map to candidate object
                attrs = {attr.attribute_name: attr.normalized_value for attr in p.attributes}
                raw_attrs = {attr.attribute_name: attr.raw_value for attr in p.attributes}

                rev_list = []
                for r in p.reviews:
                    rev_aspects = [{"aspect": asp.aspect, "sentiment": asp.sentiment, "confidence": asp.confidence} for asp in r.aspects]
                    rev_list.append({
                        "id": r.id,
                        "rating": r.rating,
                        "author": r.author,
                        "review_text": r.review_text,
                        "aspects": rev_aspects
                    })

                candidates.append({
                    "product_id": p.id,
                    "canonical_name": p.canonical_name,
                    "category": p.category,
                    "brand": p.brand,
                    "price": p.normalized_price,
                    "currency": p.currency,
                    "image_url": p.image_url,
                    "description": p.description,
                    "source_count": p.source_count,
                    "attributes": attrs,
                    "raw_attributes": raw_attrs,
                    "reviews": rev_list
                })

        state["candidate_products"] = candidates
        return state
