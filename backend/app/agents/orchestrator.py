"""
Multi-Agent Graph Orchestrator.
Coordinates the end-to-end execution of specialized agents, ranking calculation, and database persistence.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.telemetry import logger, set_investigation_id
from app.agents.query_understanding import QueryUnderstandingAgent
from app.agents.discovery import ProductDiscoveryAgent
from app.agents.specification import SpecificationAgent
from app.agents.review_intelligence import ReviewIntelligenceAgent
from app.agents.price_value import PriceValueAgent
from app.agents.trust_evidence import TrustEvidenceAgent
from app.agents.recommendation import RecommendationAgent
from app.ranking.engine import DeterministicRankingEngine

from app.models.investigation import Investigation, InvestigationCandidate, Evidence, AgentRun
from app.models.product import Product
from app.schemas.ranking import RankingWeights


class MultiAgentOrchestrator:
    def __init__(self):
        self.query_agent = QueryUnderstandingAgent()
        self.discovery_agent = ProductDiscoveryAgent()
        self.spec_agent = SpecificationAgent()
        self.review_agent = ReviewIntelligenceAgent()
        self.price_agent = PriceValueAgent()
        self.trust_agent = TrustEvidenceAgent()
        self.rec_agent = RecommendationAgent()

    async def run_investigation(
        self,
        investigation_id: str,
        query: str,
        weights: Optional[RankingWeights],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Execute all agent stages, compute ranking, and save results."""
        set_investigation_id(investigation_id)
        ranking_weights = weights or RankingWeights()

        state: Dict[str, Any] = {
            "investigation_id": investigation_id,
            "query": query,
            "weights": ranking_weights,
            "db_session": session,
            "agent_runs": []
        }

        try:
            # 1. Query Understanding
            state = await self.query_agent.execute(state)

            # 2. Product Discovery
            state = await self.discovery_agent.execute(state)

            # 3. Specification Analysis & Constraint Validation
            state = await self.spec_agent.execute(state)

            # 4. Review Intelligence
            state = await self.review_agent.execute(state)

            # 5. Price / Value Analysis
            state = await self.price_agent.execute(state)

            # 6. Trust & Evidence Verification
            state = await self.trust_agent.execute(state)

            # 7. Deterministic Ranking
            scored_candidates = DeterministicRankingEngine.rank_candidates(
                candidates=state.get("candidate_products", []),
                spec_evals=state.get("spec_evaluations", {}),
                review_intel=state.get("review_intelligence", {}),
                price_values=state.get("price_value_map", {}),
                trust_audits=state.get("trust_audits", {}),
                parsed=state["parsed_constraints"],
                weights=ranking_weights
            )
            state["ranked_candidates"] = scored_candidates

            # 8. Recommendation & Narrative Synthesis
            state = await self.rec_agent.execute(state)

            # Persist results to DB
            await self._persist_investigation_results(investigation_id, state, session)
            return state

        except Exception as e:
            logger.error(f"Orchestration failed for investigation {investigation_id}: {e}", exc_info=True)
            # Update investigation as failed
            inv_res = await session.execute(select(Investigation).filter(Investigation.id == investigation_id))
            inv = inv_res.scalars().first()
            if inv:
                inv.status = "FAILED"
                inv.error_message = str(e)
                await session.commit()
            raise e

    async def _persist_investigation_results(
        self,
        investigation_id: str,
        state: Dict[str, Any],
        session: AsyncSession
    ) -> None:
        """Save parsed constraints, candidates, evidence items, and agent run telemetry."""
        inv_res = await session.execute(select(Investigation).filter(Investigation.id == investigation_id))
        inv = inv_res.scalars().first()
        if not inv:
            return

        inv.status = "COMPLETED"
        inv.completed_at = datetime.now(timezone.utc)
        inv.parsed_constraints = state["parsed_constraints"].model_dump()
        inv.weights = state["weights"].model_dump()

        # Delete any previous candidates or evidence for idempotency
        # Save Candidates
        for item in state.get("ranked_candidates", []):
            cand_product = item["candidate"]
            cand_obj = InvestigationCandidate(
                investigation_id=investigation_id,
                product_id=cand_product["product_id"],
                score=item["score"],
                rank=item["rank"],
                fit_status=item["fit_status"],
                score_breakdown=item["score_breakdown"].model_dump(),
                explanation=item["explanation"].model_dump()
            )
            session.add(cand_obj)

        # Save Evidence Items
        all_evidence = state.get("evidence_items", {})
        for prod_id, ev_list in all_evidence.items():
            for ev in ev_list:
                ev_obj = Evidence(
                    investigation_id=investigation_id,
                    product_id=prod_id,
                    evidence_type=ev["evidence_type"],
                    claim=ev["claim"],
                    supporting_text=ev["supporting_text"],
                    confidence=ev["confidence"],
                    status=ev["status"]
                )
                session.add(ev_obj)

        # Save Agent Runs Telemetry
        for ar in state.get("agent_runs", []):
            run_obj = AgentRun(
                investigation_id=investigation_id,
                agent_name=ar["agent_name"],
                status=ar["status"],
                started_at=datetime.fromtimestamp(ar["started_at"], timezone.utc) if ar.get("started_at") else None,
                completed_at=datetime.fromtimestamp(ar["completed_at"], timezone.utc) if ar.get("completed_at") else None,
                duration_ms=ar.get("duration_ms", 0.0),
                error_code=ar.get("error_code"),
                token_usage=ar.get("token_usage", 0),
                metadata_json=ar.get("metadata", {})
            )
            session.add(run_obj)

        await session.commit()
        logger.info(f"Successfully committed investigation {investigation_id} results to database.")
