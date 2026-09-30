"""Analytics and metrics endpoints."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models import Event, Camera, Track, User
from backend.app.schemas import AnalyticsSummary
from backend.app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return aggregated operational metrics."""
    # Total events
    total_result = await db.execute(select(func.count(Event.id)))
    total_events = total_result.scalar() or 0

    # Events by type
    type_result = await db.execute(
        select(Event.event_type, func.count(Event.id)).group_by(Event.event_type)
    )
    events_by_type = {row[0]: row[1] for row in type_result.all()}

    # Events by severity
    sev_result = await db.execute(
        select(Event.severity, func.count(Event.id)).group_by(Event.severity)
    )
    events_by_severity = {row[0]: row[1] for row in sev_result.all()}

    # Active cameras
    cam_result = await db.execute(
        select(func.count(Camera.id)).where(Camera.status == "ONLINE")
    )
    active_cameras = cam_result.scalar() or 0

    # Total tracks
    track_result = await db.execute(select(func.count(Track.id)))
    total_tracks = track_result.scalar() or 0

    # Average confidence
    conf_result = await db.execute(select(func.avg(Event.confidence)))
    avg_confidence = round(float(conf_result.scalar() or 0), 3)

    # Uptime (simplified: count of online camera-hours in last 24h)
    uptime_hours = float(active_cameras * 24)

    return AnalyticsSummary(
        total_events=total_events,
        events_by_type=events_by_type,
        events_by_severity=events_by_severity,
        active_cameras=active_cameras,
        total_tracks=total_tracks,
        avg_confidence=avg_confidence,
        uptime_hours=uptime_hours,
    )


@router.get("/events-over-time")
async def events_over_time(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Event count bucketed by hour for the last N hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(
            func.date_trunc("hour", Event.occurred_at).label("hour"),
            func.count(Event.id).label("count"),
        )
        .where(Event.occurred_at >= since)
        .group_by("hour")
        .order_by("hour")
    )
    return [{"hour": row[0].isoformat(), "count": row[1]} for row in result.all()]


@router.get("/camera-health")
async def camera_health(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return health status for all cameras."""
    result = await db.execute(select(Camera.id, Camera.name, Camera.status, Camera.enabled))
    return [
        {"id": str(row[0]), "name": row[1], "status": row[2], "enabled": row[3]}
        for row in result.all()
    ]
