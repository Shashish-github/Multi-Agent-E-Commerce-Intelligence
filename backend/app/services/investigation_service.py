"""
Investigation workflow management service.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundException, AuthorizationException
from app.models.investigation import Investigation, InvestigationCandidate, Evidence, AgentRun
from app.models.product import Product
from app.models.user import User
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationSummaryOut,
    InvestigationDetailOut,
    CandidateResultOut,
    EvidenceOut
)
from app.schemas.ranking import RankingWeights, ReRankRequest, ScoreBreakdown, ExplanationDetail
from app.schemas.agent import ParsedConstraints, AgentRunOut
from app.schemas.product import ProductOut
from app.agents.orchestrator import MultiAgentOrchestrator
from app.ranking.what_if import WhatIfEngine


class InvestigationService:
    @staticmethod
    async def create_and_run(
        db: AsyncSession,
        user: User,
        data: InvestigationCreate
    ) -> InvestigationDetailOut:
        # Create investigation
        inv = Investigation(
            user_id=user.id,
            original_query=data.query,
            weights=data.weights.model_dump() if data.weights else None,
            status="RUNNING"
        )
        db.add(inv)
        await db.commit()
        await db.refresh(inv)

        # Run multi-agent orchestrator
        orchestrator = MultiAgentOrchestrator()
        await orchestrator.run_investigation(
            investigation_id=inv.id,
            query=data.query,
            weights=data.weights,
            session=db
        )

        return await InvestigationService.get_investigation_detail(db, inv.id, user)

    @staticmethod
    async def get_investigation_detail(
        db: AsyncSession,
        investigation_id: str,
        user: User
    ) -> InvestigationDetailOut:
        query = select(Investigation).options(
            selectinload(Investigation.candidates).selectinload(InvestigationCandidate.product),
            selectinload(Investigation.evidence_items),
            selectinload(Investigation.agent_runs)
        ).filter(Investigation.id == investigation_id)

        res = await db.execute(query)
        inv = res.scalars().first()
        if not inv:
            raise NotFoundException(f"Investigation {investigation_id} not found")

        if inv.user_id != user.id and user.role != "ADMIN":
            raise AuthorizationException("You do not have permission to view this investigation")

        # Map candidates
        cand_outs: List[CandidateResultOut] = []
        for c in sorted(inv.candidates, key=lambda x: x.rank):
            p = c.product
            p_out = ProductOut.model_validate(p) if p else None
            
            ev_list = [
                EvidenceOut(
                    id=e.id,
                    product_id=e.product_id,
                    evidence_type=e.evidence_type,
                    claim=e.claim,
                    supporting_text=e.supporting_text,
                    confidence=e.confidence,
                    status=e.status,
                    source_provider=None
                )
                for e in inv.evidence_items if e.product_id == c.product_id
            ]

            sb = ScoreBreakdown(**c.score_breakdown) if c.score_breakdown else ScoreBreakdown(
                requirement_fit=1.0, review_quality=0.5, price_value=0.5, spec_strength=0.5, reliability_evidence=0.8, preference_match=0.8, final_score=c.score
            )
            exp = ExplanationDetail(**c.explanation) if c.explanation else ExplanationDetail(why_it_won="Ranked candidate")

            cand_outs.append(CandidateResultOut(
                product=p_out,
                rank=c.rank,
                score=c.score,
                fit_status=c.fit_status,
                score_breakdown=sb,
                explanation=exp,
                evidence=ev_list
            ))

        agent_outs = [
            AgentRunOut(
                id=ar.id,
                agent_name=ar.agent_name,
                status=ar.status,
                started_at=ar.started_at,
                completed_at=ar.completed_at,
                duration_ms=ar.duration_ms,
                error_code=ar.error_code,
                token_usage=ar.token_usage,
                metadata_json=ar.metadata_json
            )
            for ar in inv.agent_runs
        ]

        parsed = ParsedConstraints(**inv.parsed_constraints) if inv.parsed_constraints else None
        weights = RankingWeights(**inv.weights) if inv.weights else RankingWeights()

        return InvestigationDetailOut(
            id=inv.id,
            original_query=inv.original_query,
            parsed_constraints=parsed,
            weights=weights,
            status=inv.status,
            created_at=inv.created_at,
            completed_at=inv.completed_at,
            candidates=cand_outs,
            agent_runs=agent_outs
        )

    @staticmethod
    async def list_user_investigations(
        db: AsyncSession,
        user: User
    ) -> List[InvestigationSummaryOut]:
        query = select(Investigation).options(
            selectinload(Investigation.candidates).selectinload(InvestigationCandidate.product)
        ).filter(Investigation.user_id == user.id).order_by(Investigation.created_at.desc())

        res = await db.execute(query)
        invs = res.scalars().all()

        summaries: List[InvestigationSummaryOut] = []
        for inv in invs:
            top_cand = min(inv.candidates, key=lambda c: c.rank) if inv.candidates else None
            top_name = top_cand.product.canonical_name if top_cand and top_cand.product else None
            summaries.append(InvestigationSummaryOut(
                id=inv.id,
                original_query=inv.original_query,
                status=inv.status,
                created_at=inv.created_at,
                completed_at=inv.completed_at,
                candidate_count=len(inv.candidates),
                top_recommendation_name=top_name
            ))
        return summaries

    @staticmethod
    async def rerank_investigation(
        db: AsyncSession,
        investigation_id: str,
        user: User,
        rerank_req: ReRankRequest
    ) -> InvestigationDetailOut:
        inv_detail = await InvestigationService.get_investigation_detail(db, investigation_id, user)
        if not inv_detail.parsed_constraints:
            return inv_detail

        # Format candidates data for WhatIfEngine
        candidates_data = []
        for c in inv_detail.candidates:
            candidates_data.append({
                "product_id": c.product.id,
                "canonical_name": c.product.canonical_name,
                "brand": c.product.brand,
                "category": c.product.category,
                "price": c.product.normalized_price,
                "attributes": {},  # cached
                "previous_spec_strength": c.score_breakdown.spec_strength,
                "previous_review_score": c.score_breakdown.review_quality,
                "previous_reliability_score": c.score_breakdown.reliability_evidence
            })

        re_scored = WhatIfEngine.rerank(
            candidates_data=candidates_data,
            parsed_constraints=inv_detail.parsed_constraints,
            new_weights=rerank_req.weights,
            override_budget=rerank_req.override_budget_max,
            additional_exclusions=rerank_req.additional_exclusions
        )

        # Update candidates in in-memory detail response
        re_ranked_outs: List[CandidateResultOut] = []
        for item in re_scored:
            pid = item["candidate"]["product_id"]
            original_cand = next((c for c in inv_detail.candidates if c.product.id == pid), None)
            if original_cand:
                original_cand.rank = item["rank"]
                original_cand.score = item["score"]
                original_cand.fit_status = item["fit_status"]
                original_cand.score_breakdown = item["score_breakdown"]
                re_ranked_outs.append(original_cand)

        inv_detail.candidates = re_ranked_outs
        if rerank_req.weights:
            inv_detail.weights = rerank_req.weights

        return inv_detail
