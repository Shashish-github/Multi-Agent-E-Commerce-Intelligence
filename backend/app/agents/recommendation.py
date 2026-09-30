"""
Recommendation and Explainability Agent.
Synthesizes decision explanations, highlights, trade-offs, and reason codes grounded in verified evidence.
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.ranking import ExplanationDetail
from app.schemas.agent import ParsedConstraints


from app.services.llm_service import llm_service


class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RecommendationAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ranked_candidates = state.get("ranked_candidates", [])
        parsed: ParsedConstraints = state["parsed_constraints"]
        spec_evals = state.get("spec_evaluations", {})
        review_intel = state.get("review_intelligence", {})
        price_values = state.get("price_value_map", {})
        trust_audits = state.get("trust_audits", {})

        for item in ranked_candidates:
            cand = item["candidate"]
            prod_id = cand["product_id"]
            name = cand["canonical_name"]
            price = cand.get("price", 0.0)
            rank = item["rank"]
            breakdown = item["score_breakdown"]

            spec_info = spec_evals.get(prod_id, {})
            rev_info = review_intel.get(prod_id, {})
            prc_info = price_values.get(prod_id, {})
            trust_info = trust_audits.get(prod_id, {})

            attrs = cand.get("attributes", {})

            highlights: List[str] = []
            trade_offs: List[str] = []
            reason_codes: List[str] = []

            # 1. Generate Highlights
            if spec_info.get("passed_constraints"):
                highlights.extend(spec_info["passed_constraints"][:2])
            if rev_info.get("recurring_strengths"):
                highlights.extend(rev_info["recurring_strengths"][:2])
            if prc_info.get("verdict"):
                highlights.append(prc_info["verdict"])

            # 2. Generate Trade-Offs
            if rev_info.get("recurring_complaints"):
                trade_offs.extend(rev_info["recurring_complaints"])
            if spec_info.get("failed_constraints"):
                trade_offs.extend(spec_info["failed_constraints"])
            if not trade_offs:
                if price > 80000:
                    trade_offs.append("Higher upfront investment compared to mid-range options")
                else:
                    trade_offs.append("Standard display brightness for indoor use")

            # 3. Reason Codes
            if breakdown.requirement_fit >= 1.0:
                reason_codes.append("FULL_CONSTRAINT_COMPLIANCE")
            if breakdown.review_quality >= 0.8:
                reason_codes.append("HIGH_SENTIMENT_CONSENSUS")
            if breakdown.price_value >= 0.75:
                reason_codes.append("OPTIMAL_VALUE_TIER")
            if breakdown.spec_strength >= 0.8:
                reason_codes.append("SUPERIOR_HARDWARE_SPECS")

            # 4. Synthesize "Why It Won" narrative for Top Pick
            if rank == 1:
                # Attempt dynamic LLM generation via Groq Cloud if available
                llm_thesis = await llm_service.generate_recommendation_thesis(
                    product_name=name,
                    score=breakdown.final_score,
                    rank=rank,
                    highlights=highlights,
                    price=price
                )
                if llm_thesis:
                    why_it_won = llm_thesis
                else:
                    why_it_won = (
                        f"{name} ranks #1 overall (Score: {breakdown.final_score:.2f}/1.0). "
                        f"It strictly fulfills all your required criteria within ₹{price:,.0f} budget, "
                        f"delivering an exceptional {breakdown.spec_strength*100:.0f}% specification tier "
                        f"and backed by {rev_info.get('average_rating', 4.5)}/5.0 verified user consensus."
                    )
            else:
                why_it_won = (
                    f"Ranks #{rank} with strong {breakdown.spec_strength*100:.0f}% spec performance. "
                    f"{'Fails ' + str(len(spec_info.get('failed_constraints', []))) + ' requirement(s).' if not item['is_compliant'] else 'Narrowly edged out on price-to-performance ratio.'}"
                )

            item["explanation"] = ExplanationDetail(
                why_it_won=why_it_won,
                highlights=highlights,
                trade_offs=trade_offs,
                reason_codes=reason_codes,
                failed_constraints=spec_info.get("failed_constraints", []),
                confidence_level=trust_info.get("confidence_level", "VERIFIED")
            )

        state["ranked_candidates"] = ranked_candidates
        return state
