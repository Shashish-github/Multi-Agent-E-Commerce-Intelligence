"""
Specification Extraction and Constraint Validation Agent.
Normalizes attributes and strictly verifies hard constraints against candidate products.
"""
from typing import Dict, Any, List, Tuple, Optional
from app.agents.base import BaseAgent
from app.schemas.agent import HardConstraint, ParsedConstraints


class SpecificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SpecificationAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        parsed: ParsedConstraints = state["parsed_constraints"]
        candidates = state.get("candidate_products", [])

        spec_evaluations: Dict[str, Dict[str, Any]] = {}

        for cand in candidates:
            prod_id = cand["product_id"]
            attrs = cand.get("attributes", {})
            price = cand.get("price", 0.0)

            passed_constraints: List[str] = []
            failed_constraints: List[str] = []
            unknown_constraints: List[str] = []

            # 1. Evaluate Hard Constraints
            for hc in parsed.hard_constraints:
                passed, reason = self.evaluate_hard_constraint(hc, price, attrs)
                if passed is True:
                    passed_constraints.append(reason)
                elif passed is False:
                    failed_constraints.append(reason)
                else:
                    unknown_constraints.append(reason)

            # Compute Requirement Fit Score (0.0 to 1.0)
            total_hc = len(parsed.hard_constraints)
            if total_hc == 0:
                fit_score = 1.0
                fit_status = "COMPLIANT"
            else:
                passed_count = len(passed_constraints)
                fit_score = round(passed_count / total_hc, 2)
                if len(failed_constraints) == 0:
                    fit_status = "COMPLIANT"
                elif fit_score >= 0.5:
                    fit_status = "PARTIALLY_COMPLIANT"
                else:
                    fit_status = "NON_COMPLIANT"

            # Compute Specification Strength Score (Hardware tier analysis)
            spec_strength = self.compute_spec_strength(attrs)

            spec_evaluations[prod_id] = {
                "fit_score": fit_score,
                "fit_status": fit_status,
                "spec_strength": spec_strength,
                "passed_constraints": passed_constraints,
                "failed_constraints": failed_constraints,
                "unknown_constraints": unknown_constraints,
                "normalized_specs": attrs
            }

        state["spec_evaluations"] = spec_evaluations
        return state

    def evaluate_hard_constraint(self, hc: HardConstraint, price: float, attrs: Dict[str, Any]) -> Tuple[Optional[bool], str]:
        field = hc.field.lower()
        op = hc.operator

        # Price check
        if field == "price":
            target_val = float(hc.value)
            if op in ["<=", "<"]:
                if price <= target_val:
                    return True, f"Price ₹{price:,.0f} is within budget ₹{target_val:,.0f}"
                else:
                    return False, f"Price ₹{price:,.0f} exceeds budget ₹{target_val:,.0f}"
            return True, f"Price ₹{price:,.0f}"

        # Attribute check (e.g. ram_gb, storage_gb)
        if field in attrs:
            raw_val = attrs[field]
            try:
                num_val = float(raw_val)
                target_num = float(hc.value)
                if op == ">=":
                    if num_val >= target_num:
                        return True, f"{field.upper()}: {num_val}{hc.unit or ''} satisfies required >={target_num}{hc.unit or ''}"
                    else:
                        return False, f"{field.upper()}: {num_val}{hc.unit or ''} is below required {target_num}{hc.unit or ''}"
                elif op == "<=":
                    if num_val <= target_num:
                        return True, f"{field.upper()}: {num_val}{hc.unit or ''} is within {target_num}{hc.unit or ''}"
                    else:
                        return False, f"{field.upper()}: {num_val}{hc.unit or ''} exceeds {target_num}{hc.unit or ''}"
                elif op == "==":
                    return (num_val == target_num), f"{field}: {num_val}"
            except ValueError:
                # String comparison
                str_target = str(hc.value).lower()
                if op in ["contains", "=="]:
                    if str_target in str(raw_val).lower():
                        return True, f"{field}: contains {hc.value}"
                    else:
                        return False, f"{field}: missing required {hc.value}"

        return None, f"{field}: value unknown or not specified"

    def compute_spec_strength(self, attrs: Dict[str, Any]) -> float:
        """Score hardware tier (e.g. RAM, GPU, Battery, Storage) on 0.0 - 1.0 scale."""
        score = 0.5
        ram = float(attrs.get("ram_gb", 8))
        if ram >= 32:
            score += 0.25
        elif ram >= 16:
            score += 0.15
        elif ram < 8:
            score -= 0.15

        gpu = str(attrs.get("gpu", "")).lower()
        if "rtx" in gpu or "dedicated" in gpu or "discrete" in gpu:
            score += 0.15
        elif "arc" in gpu or "m2" in gpu:
            score += 0.08

        battery = float(attrs.get("battery_life_hours", 7))
        if battery >= 12:
            score += 0.10
        elif battery >= 9:
            score += 0.05

        return min(1.0, max(0.0, round(score, 2)))
