"""
Investigation API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.investigation_service import InvestigationService
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationDetailOut,
    InvestigationSummaryOut,
    CandidateResultOut
)
from app.schemas.ranking import ReRankRequest
from app.schemas.agent import AgentRunOut
from app.models.user import User

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.post("", response_model=InvestigationDetailOut)
async def create_investigation(
    data: InvestigationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AuthService.get_current_user)
):
    """Initiate a multi-agent shopping investigation."""
    return await InvestigationService.create_and_run(db, user, data)


@router.get("", response_model=List[InvestigationSummaryOut])
async def list_investigations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AuthService.get_current_user)
):
    """List historical investigations for the authenticated user."""
    return await InvestigationService.list_user_investigations(db, user)


@router.get("/{investigation_id}", response_model=InvestigationDetailOut)
async def get_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AuthService.get_current_user)
):
    """Retrieve full details of an investigation."""
    return await InvestigationService.get_investigation_detail(db, investigation_id, user)


@router.get("/{investigation_id}/results", response_model=List[CandidateResultOut])
async def get_investigation_results(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AuthService.get_current_user)
):
    """Retrieve ranked candidate products and evidence."""
    detail = await InvestigationService.get_investigation_detail(db, investigation_id, user)
    return detail.candidates


@router.get("/{investigation_id}/agents", response_model=List[AgentRunOut])
async def get_investigation_agents(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AuthService.get_current_user)
):
    """Retrieve observability metrics for all agents executed in this investigation."""
    detail = await InvestigationService.get_investigation_detail(db, investigation_id, user)
    return detail.agent_runs


@router.post("/{investigation_id}/rerank", response_model=InvestigationDetailOut)
async def rerank_investigation(
    investigation_id: str,
    rerank_req: ReRankRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AuthService.get_current_user)
):
    """Perform What-If recalculation of rankings with updated criteria or weights."""
    return await InvestigationService.rerank_investigation(db, investigation_id, user, rerank_req)
