"""Event search, detail, evidence, and status update routes."""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models import Event, User
from backend.app.schemas import EventResponse, EventListResponse, EventStatusUpdate
from backend.app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=EventListResponse)
async def list_events(
    camera_id: Optional[uuid.UUID] = Query(None),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Paginated event search with filters."""
    query = select(Event)
    count_query = select(func.count(Event.id))

    if camera_id:
        query = query.where(Event.camera_id == camera_id)
        count_query = count_query.where(Event.camera_id == camera_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
        count_query = count_query.where(Event.event_type == event_type)
    if severity:
        query = query.where(Event.severity == severity)
        count_query = count_query.where(Event.severity == severity)
    if status:
        query = query.where(Event.status == status)
        count_query = count_query.where(Event.status == status)
    if start_date:
        query = query.where(Event.occurred_at >= start_date)
        count_query = count_query.where(Event.occurred_at >= start_date)
    if end_date:
        query = query.where(Event.occurred_at <= end_date)
        count_query = count_query.where(Event.occurred_at <= end_date)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(Event.occurred_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    events = result.scalars().all()

    return EventListResponse(
        items=events,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get event details with explanation."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/evidence")
async def get_event_evidence(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return authorized evidence reference (clip path or URL)."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not event.evidence_uri:
        raise HTTPException(status_code=404, detail="No evidence available")
    return {
        "event_id": str(event.id),
        "evidence_uri": event.evidence_uri,
        "event_type": event.event_type,
        "occurred_at": event.occurred_at.isoformat(),
    }


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event_status(
    event_id: uuid.UUID,
    body: EventStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Acknowledge or dismiss an event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if body.status not in ("ACKNOWLEDGED", "DISMISSED"):
        raise HTTPException(status_code=400, detail="Invalid status")
    event.status = body.status
    await db.flush()
    await db.refresh(event)
    return event
