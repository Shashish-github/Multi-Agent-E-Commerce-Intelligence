"""
What-If Re-Ranking Engine.
Allows instantaneous recalculation of product rankings when weights or constraints are adjusted.
"""
from typing import Dict, Any, List, Optional
from app.schemas.ranking import RankingWeights, ScoreBreakdown
from app.schemas.agent import ParsedConstraints, HardConstraint
from app.ranking.engine import DeterministicRankingEngine


class WhatIfEngine:
    @classmethod
    def rerank(
        cls,
        candidates_data: List[Dict[str, Any]],
        parsed_constraints: ParsedConstraints,
        new_weights: Optional[RankingWeights] = None,
        override_budget: Optional[float] = None,
        additional_exclusions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Recalculate ranks in-memory instantly using updated parameters."""
        weights = new_weights or RankingWeights()
        
        # Modify constraints if overrides are provided
        updated_parsed = parsed_constraints.model_copy(deep=True)
        if override_budget is not None:
            updated_parsed.budget_max = override_budget
            # Update price hard constraint
            updated_parsed.hard_constraints = [
                hc for hc in updated_parsed.hard_constraints if hc.field.lower() != "price"
            ]
            updated_parsed.hard_constraints.append(
                HardConstraint(field="price", operator="<=", value=override_budget, unit="INR")
            )

        if additional_exclusions:
            for excl in additional_exclusions:
                if excl not in updated_parsed.exclusions:
                    updated_parsed.exclusions.append(excl)

        # Filter out excluded brands
        active_candidates = [
            c for c in candidates_data
            if not any(excl.lower() in c.get("brand", "").lower() for excl in updated_parsed.exclusions)
        ]

        # Re-evaluate specs, price values, and preferences
        spec_evals: Dict[str, Dict[str, Any]] = {}
        price_values: Dict[str, Dict[str, Any]] = {}
        review_intel: Dict[str, Dict[str, Any]] = {}
        trust_audits: Dict[str, Dict[str, Any]] = {}

        budget = updated_parsed.budget_max
        prices = [c.get("price", 0.0) for c in active_candidates]
        min_p = min(prices) if prices else 0.0
        max_p = max(prices) if prices else 0.0

        for cand in active_candidates:
            prod_id = cand["product_id"]
            price = cand.get("price", 0.0)
            attrs = cand.get("attributes", {})

            # 1. Spec check
            passed: List[str] = []
            failed: List[str] = []
            for hc in updated_parsed.hard_constraints:
                if hc.field.lower() == "price":
                    if price <= float(hc.value):
                        passed.append(f"Price ₹{price:,.0f} within budget")
                    else:
                        failed.append(f"Price ₹{price:,.0f} exceeds budget")
                elif hc.field.lower() in attrs:
                    try:
                        if float(attrs[hc.field.lower()]) >= float(hc.value):
                            passed.append(f"{hc.field.upper()} satisfied")
                        else:
                            failed.append(f"{hc.field.upper()} below required")
                    except ValueError:
                        passed.append(f"{hc.field}: {attrs[hc.field.lower()]}")

            fit_score = len(passed) / len(updated_parsed.hard_constraints) if updated_parsed.hard_constraints else 1.0
            fit_status = "COMPLIANT" if len(failed) == 0 else ("PARTIALLY_COMPLIANT" if fit_score >= 0.5 else "NON_COMPLIANT")
            spec_strength = float(cand.get("previous_spec_strength", 0.7))

            spec_evals[prod_id] = {
                "fit_score": round(fit_score, 2),
                "fit_status": fit_status,
                "spec_strength": spec_strength,
                "passed_constraints": passed,
                "failed_constraints": failed
            }

            # 2. Price check
            if budget and budget > 0:
                budget_fit = 1.0 - (0.2 * (1.0 - (price / budget))) if price <= budget else max(0.0, 1.0 - (((price - budget) / budget) * 2.0))
            else:
                budget_fit = 0.8
            p_percentile = (price - min_p) / (max_p - min_p) if max_p > min_p else 0.5
            val_idx = round((spec_strength * 0.7) + ((1.0 - p_percentile) * 0.3), 2)
            price_values[prod_id] = {
                "price_value_score": round(0.6 * budget_fit + 0.4 * val_idx, 2)
            }

            # 3. Review & Trust inherit cached metrics
            review_intel[prod_id] = {"review_score": cand.get("previous_review_score", 0.8)}
            trust_audits[prod_id] = {"reliability_score": cand.get("previous_reliability_score", 0.9)}

        # Run Deterministic Ranking
        ranked = DeterministicRankingEngine.rank_candidates(
            candidates=active_candidates,
            spec_evals=spec_evals,
            review_intel=review_intel,
            price_values=price_values,
            trust_audits=trust_audits,
            parsed=updated_parsed,
            weights=weights
        )

        return ranked
