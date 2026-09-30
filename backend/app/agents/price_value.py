"""
Price and Value Agent.
Calculates budget fit, category price percentiles, and spec-to-price value index.
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.agent import ParsedConstraints


class PriceValueAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PriceValueAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        parsed: ParsedConstraints = state["parsed_constraints"]
        candidates = state.get("candidate_products", [])
        spec_evals = state.get("spec_evaluations", {})

        if not candidates:
            state["price_value_map"] = {}
            return state

        prices = [c.get("price", 0.0) for c in candidates]
        min_price = min(prices)
        max_price = max(prices)
        budget = parsed.budget_max

        price_value_map: Dict[str, Dict[str, Any]] = {}

        for cand in candidates:
            prod_id = cand["product_id"]
            price = cand.get("price", 0.0)
            spec_strength = spec_evals.get(prod_id, {}).get("spec_strength", 0.5)

            # 1. Budget Fit Score
            if budget is not None and budget > 0:
                if price <= budget:
                    # Within budget: reward remaining headroom slightly while ensuring adequate tier
                    budget_ratio = price / budget
                    budget_fit_score = 1.0 - (0.2 * (1.0 - budget_ratio))  # 0.8 to 1.0
                else:
                    # Over budget: penalize proportionally
                    overrun = (price - budget) / budget
                    budget_fit_score = max(0.0, 1.0 - (overrun * 2.0))
            else:
                budget_fit_score = 0.8  # No budget constraint specified

            # 2. Relative Price Percentile
            if max_price > min_price:
                price_percentile = (price - min_price) / (max_price - min_price)
            else:
                price_percentile = 0.5

            # 3. Feature-to-Price Value Index (Higher spec strength at lower relative price = higher value)
            value_index = round(min(1.0, max(0.0, (spec_strength * 0.7) + ((1.0 - price_percentile) * 0.3))), 2)

            # Combined Price Value Score (0.0 to 1.0)
            combined_price_score = round(min(1.0, max(0.0, 0.6 * budget_fit_score + 0.4 * value_index)), 2)

            # Verdict text
            if price <= (budget or price) and value_index >= 0.7:
                verdict = "Excellent Price-to-Performance Value"
            elif price <= (budget or price):
                verdict = "Fair Value within Budget"
            else:
                verdict = f"Priced above target budget by ₹{(price - (budget or price)):,.0f}"

            price_value_map[prod_id] = {
                "price": price,
                "budget_fit_score": budget_fit_score,
                "price_percentile": round(price_percentile, 2),
                "value_index": value_index,
                "price_value_score": combined_price_score,
                "verdict": verdict
            }

        state["price_value_map"] = price_value_map
        return state
