"""
Deterministic Multi-Factor Ranking Engine.
Enforces hard constraints, calculates multi-criteria score matrix, and produces transparent factor breakdowns.
"""
from typing import Dict, Any, List
from app.schemas.ranking import RankingWeights, ScoreBreakdown
from app.schemas.agent import ParsedConstraints


class DeterministicRankingEngine:
    @staticmethod
    def calculate_preference_match(cand: Dict[str, Any], parsed: ParsedConstraints) -> float:
        """Calculate soft preference score (0.0 to 1.0)."""
        if not parsed.soft_preferences:
            return 0.8  # Neutral high baseline if no specific soft preferences

        attrs = cand.get("attributes", {})
        matched = 0.0
        total_weight = 0.0

        for pref in parsed.soft_preferences:
            importance_weight = 1.0 if pref.importance == "HIGH" else 0.5
            total_weight += importance_weight

            field = pref.field.lower()
            if field == "battery_life_hours":
                bat = float(attrs.get("battery_life_hours", 6))
                if bat >= 10:
                    matched += 1.0 * importance_weight
                elif bat >= 8:
                    matched += 0.8 * importance_weight
                else:
                    matched += 0.4 * importance_weight

            elif field == "weight_kg":
                wt = float(attrs.get("weight_kg", 2.0))
                if wt <= 1.4:
                    matched += 1.0 * importance_weight
                elif wt <= 1.8:
                    matched += 0.7 * importance_weight
                else:
                    matched += 0.3 * importance_weight

            elif field == "gpu_acceleration":
                gpu = str(attrs.get("gpu", "")).lower()
                if "rtx" in gpu or "nvidia" in gpu or "discrete" in gpu:
                    matched += 1.0 * importance_weight
                elif "arc" in gpu or "m2" in gpu:
                    matched += 0.6 * importance_weight
                else:
                    matched += 0.2 * importance_weight

            elif field == "linux_compatibility":
                compat = str(attrs.get("linux_compatibility", "")).upper()
                if compat in ["EXCELLENT", "GOOD"]:
                    matched += 1.0 * importance_weight
                elif compat == "FAIR":
                    matched += 0.5 * importance_weight
                else:
                    matched += 0.2 * importance_weight

            elif field == "brand":
                brand = cand.get("brand", "").lower()
                if pref.target_value and pref.target_value.lower() in brand:
                    matched += 1.0 * importance_weight

        return round(matched / total_weight, 2) if total_weight > 0 else 0.8

    @classmethod
    def rank_candidates(
        cls,
        candidates: List[Dict[str, Any]],
        spec_evals: Dict[str, Dict[str, Any]],
        review_intel: Dict[str, Dict[str, Any]],
        price_values: Dict[str, Dict[str, Any]],
        trust_audits: Dict[str, Dict[str, Any]],
        parsed: ParsedConstraints,
        weights: RankingWeights
    ) -> List[Dict[str, Any]]:
        """Compute final deterministic score and sort candidates."""
        scored_candidates: List[Dict[str, Any]] = []

        # Normalize weights so sum is 1.0
        w_sum = (
            weights.weight_requirement_fit +
            weights.weight_review_quality +
            weights.weight_price_value +
            weights.weight_spec_strength +
            weights.weight_reliability +
            weights.weight_preference_match
        )
        if w_sum <= 0:
            w_sum = 1.0
        w_fit = weights.weight_requirement_fit / w_sum
        w_rev = weights.weight_review_quality / w_sum
        w_prc = weights.weight_price_value / w_sum
        w_spc = weights.weight_spec_strength / w_sum
        w_rel = weights.weight_reliability / w_sum
        w_prf = weights.weight_preference_match / w_sum

        for cand in candidates:
            prod_id = cand["product_id"]
            spec_info = spec_evals.get(prod_id, {})
            rev_info = review_intel.get(prod_id, {})
            prc_info = price_values.get(prod_id, {})
            trust_info = trust_audits.get(prod_id, {})

            s_fit = float(spec_info.get("fit_score", 1.0))
            s_rev = float(rev_info.get("review_score", 0.5))
            s_prc = float(prc_info.get("price_value_score", 0.5))
            s_spc = float(spec_info.get("spec_strength", 0.5))
            s_rel = float(trust_info.get("reliability_score", 0.8))
            s_prf = cls.calculate_preference_match(cand, parsed)

            # Strict hard constraint handling: If a product fails mandatory constraints,
            # apply non-linear penalty so compliant items always win out
            is_compliant = (spec_info.get("fit_status") == "COMPLIANT")
            raw_score = (
                (w_fit * s_fit) +
                (w_rev * s_rev) +
                (w_prc * s_prc) +
                (w_spc * s_spc) +
                (w_rel * s_rel) +
                (w_prf * s_prf)
            )

            final_score = raw_score if is_compliant else (raw_score * 0.4)

            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "is_compliant": is_compliant,
                "fit_status": spec_info.get("fit_status", "COMPLIANT"),
                "score_breakdown": ScoreBreakdown(
                    requirement_fit=s_fit,
                    review_quality=s_rev,
                    price_value=s_prc,
                    spec_strength=s_spc,
                    reliability_evidence=s_rel,
                    preference_match=s_prf,
                    final_score=round(final_score, 4)
                )
            })

        # Sort primarily by compliance (compliant first), then by final_score descending
        scored_candidates.sort(
            key=lambda item: (1 if item["is_compliant"] else 0, item["score"]),
            reverse=True
        )

        # Assign ranks
        for idx, item in enumerate(scored_candidates):
            item["rank"] = idx + 1

        return scored_candidates
