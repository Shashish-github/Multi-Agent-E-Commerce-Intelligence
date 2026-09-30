"""
Query Understanding Agent.
Converts natural language shopping requests into structured, typed constraints.
"""
import re
from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent
from app.schemas.agent import HardConstraint, SoftPreference, ParsedConstraints


class QueryUnderstandingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="QueryUnderstandingAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "").strip()
        parsed = self.parse_query(query)
        state["parsed_constraints"] = parsed
        return state

    def parse_query(self, query: str) -> ParsedConstraints:
        lower_q = query.lower()
        
        # 1. Determine Category
        category = "laptop"  # default
        if any(w in lower_q for w in ["phone", "smartphone", "mobile", "android", "iphone", "pixel"]):
            category = "smartphone"
        elif any(w in lower_q for w in ["monitor", "display", "screen", "4k monitor"]):
            category = "monitor"
        elif any(w in lower_q for w in ["headphone", "earphone", "audio", "earbuds", "speaker"]):
            category = "audio"
        elif any(w in lower_q for w in ["laptop", "notebook", "ultrabook", "macbook", "thinkpad"]):
            category = "laptop"

        # 2. Extract Budget (INR / USD)
        budget_max: Optional[float] = None
        # Pattern: under 90000, under ₹90,000, below 90k, budget 80k, < 90000
        budget_match = re.search(r'(?:under|below|budget|within|max|<|<=)\s*(?:₹|rs\.?|inr)?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)\s*(k|lakh|thousand)?', lower_q)
        if budget_match:
            raw_val = budget_match.group(1).replace(",", "")
            multiplier_str = budget_match.group(2)
            val = float(raw_val)
            if multiplier_str == "k" or (multiplier_str is None and val < 500 and "k" in budget_match.group(0)):
                val *= 1000
            elif multiplier_str == "lakh":
                val *= 100000
            elif multiplier_str == "thousand":
                val *= 1000
            budget_max = val

        hard_constraints: List[HardConstraint] = []
        soft_preferences: List[SoftPreference] = []
        exclusions: List[str] = []

        if budget_max is not None:
            hard_constraints.append(
                HardConstraint(field="price", operator="<=", value=budget_max, unit="INR")
            )

        # 3. RAM Constraint
        ram_match = re.search(r'(?:at least|minimum|min|>=|with)?\s*([0-9]+)\s*(?:gb|gigabyte)\s*ram', lower_q)
        if ram_match:
            ram_val = float(ram_match.group(1))
            hard_constraints.append(
                HardConstraint(field="ram_gb", operator=">=", value=ram_val, unit="GB")
            )

        # 4. Storage Constraint
        storage_match = re.search(r'(?:at least|minimum|min|>=)?\s*([0-9]+)\s*(gb|tb)\s*(?:ssd|storage|disk)', lower_q)
        if storage_match:
            st_val = float(storage_match.group(1))
            unit = storage_match.group(2)
            if unit == "tb":
                st_val *= 1024
            hard_constraints.append(
                HardConstraint(field="storage_gb", operator=">=", value=st_val, unit="GB")
            )

        # 5. OS / Platform Constraint
        if "linux" in lower_q or "ubuntu" in lower_q:
            soft_preferences.append(
                SoftPreference(field="linux_compatibility", preferred_direction="MATCH", target_value="GOOD", importance="HIGH")
            )
        if "mac" in lower_q or "macos" in lower_q or "apple" in lower_q:
            if "not" in lower_q or "no apple" in lower_q:
                exclusions.append("Apple")
            else:
                soft_preferences.append(
                    SoftPreference(field="brand", preferred_direction="MATCH", target_value="Apple", importance="HIGH")
                )

        # 6. Battery Preference
        if any(w in lower_q for w in ["battery", "battery life", "all day", "long lasting"]):
            soft_preferences.append(
                SoftPreference(field="battery_life_hours", preferred_direction="MAX", importance="HIGH")
            )

        # 7. Weight / Portability Preference
        if any(w in lower_q for w in ["lightweight", "portable", "thin", "travel", "compact"]):
            soft_preferences.append(
                SoftPreference(field="weight_kg", preferred_direction="MIN", importance="MEDIUM")
            )

        # 8. Machine Learning / CUDA / Performance Preference
        if any(w in lower_q for w in ["machine learning", "ml", "deep learning", "cuda", "gaming", "video editing"]):
            soft_preferences.append(
                SoftPreference(field="gpu_acceleration", preferred_direction="MATCH", target_value="DISCRETE", importance="HIGH")
            )

        # 9. Exclusions (e.g. "no dell", "exclude hp", "not acer")
        exclusion_matches = re.findall(r'(?:no|not|exclude|without)\s+([a-zA-Z]+)', lower_q)
        for excl in exclusion_matches:
            if excl.lower() in ["dell", "hp", "lenovo", "asus", "acer", "apple", "samsung"]:
                exclusions.append(excl.capitalize())

        # Ambiguity calculation
        ambiguity = 0.0
        if not budget_max and not hard_constraints and not soft_preferences:
            ambiguity = 0.8
        elif not budget_max:
            ambiguity = 0.3

        return ParsedConstraints(
            category=category,
            budget_max=budget_max,
            currency="INR",
            hard_constraints=hard_constraints,
            soft_preferences=soft_preferences,
            exclusions=exclusions,
            ambiguity_score=ambiguity,
            confidence=round(1.0 - (ambiguity * 0.5), 2)
        )
