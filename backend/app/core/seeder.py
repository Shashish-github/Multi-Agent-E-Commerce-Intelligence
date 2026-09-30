"""
Catalog seed loader for initializing PostgreSQL / SQLite database with canonical products, attributes, sources, and reviews.
"""
import json
from pathlib import Path
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.source import Source
from app.models.product import Product, ProductAttribute
from app.models.review import Review, ReviewAspect
from app.core.telemetry import logger


async def seed_catalog_if_empty(session: AsyncSession) -> None:
    """Check if products table is populated; if not, load seed_data/catalog.json."""
    result = await session.execute(select(Product))
    existing = result.scalars().first()
    if existing:
        logger.info("Database already seeded with product catalog.")
        return

    json_path = Path(__file__).parent.parent.parent / "seed_data" / "catalog.json"
    if not json_path.exists():
        logger.warning(f"Seed file not found at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Insert Sources
    for src in data.get("sources", []):
        source_obj = Source(
            id=src["id"],
            provider=src["provider"],
            source_url=src.get("source_url"),
            freshness_status=src.get("freshness_status", "FRESH")
        )
        session.add(source_obj)
    await session.flush()

    # 2. Insert Products, Attributes, Reviews, Aspects
    for prod in data.get("products", []):
        product_obj = Product(
            id=prod["id"],
            canonical_name=prod["canonical_name"],
            category=prod["category"],
            brand=prod["brand"],
            normalized_price=prod["normalized_price"],
            currency=prod.get("currency", "INR"),
            image_url=prod.get("image_url"),
            description=prod.get("description"),
            source_count=prod.get("source_count", 1)
        )
        session.add(product_obj)
        await session.flush()

        for attr in prod.get("attributes", []):
            attr_obj = ProductAttribute(
                product_id=product_obj.id,
                attribute_name=attr["attribute_name"],
                normalized_value=str(attr["normalized_value"]),
                raw_value=attr.get("raw_value"),
                unit=attr.get("unit"),
                confidence=attr.get("confidence", 1.0),
                source_id=attr.get("source_id")
            )
            session.add(attr_obj)

        for rev in prod.get("reviews", []):
            rev_obj = Review(
                id=rev["id"],
                product_id=product_obj.id,
                author=rev.get("author", "Anonymous"),
                rating=rev["rating"],
                review_text=rev["review_text"],
                language="en",
                source_id="src-amazon"
            )
            session.add(rev_obj)
            await session.flush()

            for asp in rev.get("aspects", []):
                aspect_obj = ReviewAspect(
                    review_id=rev_obj.id,
                    aspect=asp["aspect"],
                    sentiment=asp["sentiment"],
                    confidence=asp.get("confidence", 1.0)
                )
                session.add(aspect_obj)

    await session.commit()
    logger.info(f"Successfully seeded database with {len(data.get('products', []))} canonical products and reviews.")
