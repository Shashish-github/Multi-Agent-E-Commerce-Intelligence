"""
Unit tests for specialized AI agents.
"""
import pytest
from app.agents.query_understanding import QueryUnderstandingAgent
from app.agents.specification import SpecificationAgent
from app.agents.review_intelligence import ReviewIntelligenceAgent
from app.agents.price_value import PriceValueAgent
from app.agents.trust_evidence import TrustEvidenceAgent
from app.schemas.agent import HardConstraint, SoftPreference, ParsedConstraints


@pytest.mark.asyncio
async def test_query_understanding_agent_laptop():
    agent = QueryUnderstandingAgent()
    query = "Find a laptop under ₹90,000 for machine learning with at least 16GB RAM and great battery life"
    state = {"query": query}
    result_state = await agent.execute(state)
    
    parsed: ParsedConstraints = result_state["parsed_constraints"]
    assert parsed.category == "laptop"
    assert parsed.budget_max == 90000.0
    assert any(hc.field == "price" and hc.value == 90000.0 for hc in parsed.hard_constraints)
    assert any(hc.field == "ram_gb" and hc.value == 16.0 for hc in parsed.hard_constraints)
    assert any(sp.field == "battery_life_hours" for sp in parsed.soft_preferences)
    assert any(sp.field == "gpu_acceleration" for sp in parsed.soft_preferences)


@pytest.mark.asyncio
async def test_specification_agent_hard_constraints():
    agent = SpecificationAgent()
    parsed = ParsedConstraints(
        category="laptop",
        budget_max=90000.0,
        hard_constraints=[
            HardConstraint(field="price", operator="<=", value=90000.0, unit="INR"),
            HardConstraint(field="ram_gb", operator=">=", value=16.0, unit="GB")
        ]
    )
    candidates = [
        {
            "product_id": "p1",
            "canonical_name": "Compliant Laptop",
            "price": 85000.0,
            "attributes": {"ram_gb": "16", "gpu": "RTX 4060", "battery_life_hours": "10"}
        },
        {
            "product_id": "p2",
            "canonical_name": "Over Budget Laptop",
            "price": 110000.0,
            "attributes": {"ram_gb": "16"}
        }
    ]
    state = {"parsed_constraints": parsed, "candidate_products": candidates}
    result_state = await agent.execute(state)

    spec_evals = result_state["spec_evaluations"]
    assert spec_evals["p1"]["fit_status"] == "COMPLIANT"
    assert spec_evals["p1"]["fit_score"] == 1.0
    assert spec_evals["p2"]["fit_status"] == "PARTIALLY_COMPLIANT"
    assert spec_evals["p2"]["fit_score"] == 0.5


@pytest.mark.asyncio
async def test_review_intelligence_agent():
    agent = ReviewIntelligenceAgent()
    candidates = [
        {
            "product_id": "p1",
            "reviews": [
                {
                    "rating": 5.0,
                    "review_text": "Battery life lasts over 12 hours. Best screen ever.",
                    "aspects": [
                        {"aspect": "battery", "sentiment": "POSITIVE", "confidence": 0.95},
                        {"aspect": "display", "sentiment": "POSITIVE", "confidence": 0.98}
                    ]
                },
                {
                    "rating": 4.5,
                    "review_text": "Great battery, fast performance.",
                    "aspects": [
                        {"aspect": "battery", "sentiment": "POSITIVE", "confidence": 0.90},
                        {"aspect": "performance", "sentiment": "POSITIVE", "confidence": 0.92}
                    ]
                }
            ]
        }
    ]
    state = {"candidate_products": candidates}
    result_state = await agent.execute(state)

    review_intel = result_state["review_intelligence"]
    assert "p1" in review_intel
    assert review_intel["p1"]["review_score"] > 0.8
    assert review_intel["p1"]["aspect_summaries"]["battery"]["positive_count"] == 2
