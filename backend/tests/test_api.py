"""
API integration tests for authentication, products, and investigations.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db, AsyncSessionLocal
from app.core.seeder import seed_catalog_if_empty


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_catalog_if_empty(session)


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_products_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/products?category=laptop")
        assert res.status_code == 200
        products = res.json()
        assert len(products) > 0
        assert all(p["category"] == "laptop" for p in products)


@pytest.mark.asyncio
async def test_investigation_e2e_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Investigation
        payload = {
            "query": "Find a laptop under 90000 for ML with 16GB RAM and great battery life"
        }
        res = await client.post("/api/v1/investigations", json=payload)
        assert res.status_code == 200
        data = res.json()
        inv_id = data["id"]
        assert data["status"] == "COMPLETED"
        assert len(data["candidates"]) > 0
        assert data["candidates"][0]["rank"] == 1
        assert len(data["agent_runs"]) > 0

        # 2. Inspect Results endpoint
        res_results = await client.get(f"/api/v1/investigations/{inv_id}/results")
        assert res_results.status_code == 200
        cands = res_results.json()
        assert len(cands) > 0

        # 3. Test What-If Re-ranking
        rerank_payload = {
            "override_budget_max": 140000.0,
            "weights": {
                "weight_requirement_fit": 0.2,
                "weight_review_quality": 0.2,
                "weight_price_value": 0.1,
                "weight_spec_strength": 0.3,
                "weight_reliability": 0.1,
                "weight_preference_match": 0.1
            }
        }
        res_rerank = await client.post(f"/api/v1/investigations/{inv_id}/rerank", json=rerank_payload)
        assert res_rerank.status_code == 200
        rerank_data = res_rerank.json()
        assert len(rerank_data["candidates"]) > 0
