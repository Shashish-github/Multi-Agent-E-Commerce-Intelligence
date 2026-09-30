"""
Review Intelligence Agent.
Performs aspect-based sentiment analysis, pros/cons clustering, and review credibility assessment.
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.agent import ReviewIntelligenceOutput, AspectSummary


class ReviewIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ReviewIntelligenceAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidates = state.get("candidate_products", [])
        review_intel_map: Dict[str, Dict[str, Any]] = {}

        for cand in candidates:
            prod_id = cand["product_id"]
            reviews = cand.get("reviews", [])

            aspect_map: Dict[str, Dict[str, Any]] = {
                "performance": {"pos": 0, "neg": 0, "neu": 0, "quotes": []},
                "battery": {"pos": 0, "neg": 0, "neu": 0, "quotes": []},
                "build_quality": {"pos": 0, "neg": 0, "neu": 0, "quotes": []},
                "display": {"pos": 0, "neg": 0, "neu": 0, "quotes": []},
                "thermals": {"pos": 0, "neg": 0, "neu": 0, "quotes": []},
                "value": {"pos": 0, "neg": 0, "neu": 0, "quotes": []}
            }

            total_rating = 0.0
            for rev in reviews:
                rating = rev.get("rating", 3.0)
                total_rating += rating
                text = rev.get("review_text", "")
                aspects = rev.get("aspects", [])

                for asp in aspects:
                    name = asp.get("aspect", "").lower()
                    sent = asp.get("sentiment", "NEUTRAL").upper()
                    if name in aspect_map:
                        if sent == "POSITIVE":
                            aspect_map[name]["pos"] += 1
                        elif sent == "NEGATIVE":
                            aspect_map[name]["neg"] += 1
                        else:
                            aspect_map[name]["neu"] += 1
                        
                        if len(aspect_map[name]["quotes"]) < 2 and len(text) > 10:
                            aspect_map[name]["quotes"].append(text[:140] + ("..." if len(text) > 140 else ""))

            # Calculate Aspect summaries and overall review score
            aspect_summaries: Dict[str, Dict[str, Any]] = {}
            recurring_strengths: List[str] = []
            recurring_complaints: List[str] = []

            total_pos = 0
            total_neg = 0

            for aspect_name, counts in aspect_map.items():
                p = counts["pos"]
                n = counts["neg"]
                total_pos += p
                total_neg += n
                total_asp = p + n + counts["neu"]
                
                score = (p - n) / total_asp if total_asp > 0 else 0.0
                aspect_summaries[aspect_name] = {
                    "aspect": aspect_name,
                    "positive_count": p,
                    "negative_count": n,
                    "neutral_count": counts["neu"],
                    "aspect_score": round(score, 2),
                    "key_quotes": counts["quotes"]
                }

                if p >= 1 and score > 0.3:
                    recurring_strengths.append(f"Highly rated {aspect_name.replace('_', ' ')}")
                elif n >= 1 and score < -0.3:
                    recurring_complaints.append(f"Recurring criticism in {aspect_name.replace('_', ' ')}")

            # Normalized Review Score (0.0 to 1.0)
            avg_rating = (total_rating / len(reviews)) if reviews else 3.5
            rating_norm = avg_rating / 5.0
            sentiment_delta = (total_pos - total_neg) / max(1, (total_pos + total_neg)) if (total_pos + total_neg) > 0 else 0.0
            review_score = round(min(1.0, max(0.0, 0.7 * rating_norm + 0.3 * ((sentiment_delta + 1) / 2))), 2)

            review_intel_map[prod_id] = {
                "review_count": len(reviews),
                "average_rating": round(avg_rating, 2),
                "review_score": review_score,
                "aspect_summaries": aspect_summaries,
                "recurring_strengths": recurring_strengths,
                "recurring_complaints": recurring_complaints,
                "suspicious_volume_flag": (len(reviews) == 0)
            }

        state["review_intelligence"] = review_intel_map
        return state
