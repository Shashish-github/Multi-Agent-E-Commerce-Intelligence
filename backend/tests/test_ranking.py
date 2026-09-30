"""
Unit tests for deterministic multi-factor ranking and What-If engine.
"""
from app.ranking.engine import DeterministicRankingEngine
from app.ranking.what_if import WhatIfEngine
from app.schemas.ranking import RankingWeights
from app.schemas.agent import ParsedConstraints, HardConstraint, SoftPreference


def test_deterministic_ranking_compliance_priority():
    candidates = [
        {"product_id": "p1", "canonical_name": "Laptop Compliant", "price": 80000.0, "attributes": {"ram_gb": "16"}},
        {"product_id": "p2", "canonical_name": "Laptop Non-Compliant", "price": 120000.0, "attributes": {"ram_gb": "8"}}
    ]
    spec_evals = {
        "p1": {"fit_score": 1.0, "fit_status": "COMPLIANT", "spec_strength": 0.8},
        "p2": {"fit_score": 0.0, "fit_status": "NON_COMPLIANT", "spec_strength": 0.9}
    }
    review_intel = {
        "p1": {"review_score": 0.9},
        "p2": {"review_score": 0.95}
    }
    price_values = {
        "p1": {"price_value_score": 0.85},
        "p2": {"price_value_score": 0.40}
    }
    trust_audits = {
        "p1": {"reliability_score": 0.95},
        "p2": {"reliability_score": 0.95}
    }
    parsed = ParsedConstraints(
        category="laptop",
        budget_max=90000.0,
        hard_constraints=[HardConstraint(field="price", operator="<=", value=90000.0)]
    )
    weights = RankingWeights()

    ranked = DeterministicRankingEngine.rank_candidates(
        candidates=candidates,
        spec_evals=spec_evals,
        review_intel=review_intel,
        price_values=price_values,
        trust_audits=trust_audits,
        parsed=parsed,
        weights=weights
    )

    assert len(ranked) == 2
    assert ranked[0]["candidate"]["product_id"] == "p1"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["is_compliant"] is True
    assert ranked[1]["candidate"]["product_id"] == "p2"
    assert ranked[1]["rank"] == 2
    assert ranked[1]["is_compliant"] is False


def test_what_if_budget_expansion():
    candidates_data = [
        {"product_id": "p1", "price": 80000.0, "brand": "BrandA", "attributes": {"ram_gb": "16"}, "previous_spec_strength": 0.7, "previous_review_score": 0.8, "previous_reliability_score": 0.9},
        {"product_id": "p2", "price": 100000.0, "brand": "BrandB", "attributes": {"ram_gb": "32"}, "previous_spec_strength": 0.95, "previous_review_score": 0.95, "previous_reliability_score": 0.95}
    ]
    parsed = ParsedConstraints(
        category="laptop",
        budget_max=85000.0,
        hard_constraints=[HardConstraint(field="price", operator="<=", value=85000.0)]
    )

    # Initial ranking at 85k budget -> p1 wins because p2 is over budget
    initial_ranked = WhatIfEngine.rerank(candidates_data, parsed, override_budget=85000.0)
    assert initial_ranked[0]["candidate"]["product_id"] == "p1"

    # Expanded budget at 110k -> p2 becomes compliant and wins due to higher specs & review score
    expanded_ranked = WhatIfEngine.rerank(candidates_data, parsed, override_budget=110000.0)
    assert expanded_ranked[0]["candidate"]["product_id"] == "p2"
    assert expanded_ranked[0]["is_compliant"] is True
