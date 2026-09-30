"""Rule management routes scoped to a camera."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models import Rule, Camera, User
from backend.app.schemas import RuleCreate, RuleUpdate, RuleResponse
from backend.app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[RuleResponse])
async def list_rules(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all rules for a camera."""
    result = await db.execute(
        select(Rule).where(Rule.camera_id == camera_id).order_by(Rule.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    camera_id: uuid.UUID,
    body: RuleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new event rule on a camera."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    rule = Rule(
        camera_id=camera_id,
        rule_type=body.rule_type,
        configuration=body.configuration,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    camera_id: uuid.UUID,
    rule_id: uuid.UUID,
    body: RuleUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a rule."""
    rule = await db.get(Rule, rule_id)
    if not rule or rule.camera_id != camera_id:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.flush()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    camera_id: uuid.UUID,
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a rule."""
    rule = await db.get(Rule, rule_id)
    if not rule or rule.camera_id != camera_id:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
