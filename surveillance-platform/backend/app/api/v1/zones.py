"""Zone management routes scoped to a camera."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models import Zone, Camera, User
from backend.app.schemas import ZoneCreate, ZoneUpdate, ZoneResponse
from backend.app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[ZoneResponse])
async def list_zones(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all zones for a camera."""
    result = await db.execute(
        select(Zone).where(Zone.camera_id == camera_id).order_by(Zone.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(
    camera_id: uuid.UUID,
    body: ZoneCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new zone on a camera."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    zone = Zone(
        camera_id=camera_id,
        name=body.name,
        type=body.type,
        polygon=[p.model_dump() for p in body.polygon],
    )
    db.add(zone)
    await db.flush()
    await db.refresh(zone)
    return zone


@router.patch("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    camera_id: uuid.UUID,
    zone_id: uuid.UUID,
    body: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a zone."""
    zone = await db.get(Zone, zone_id)
    if not zone or zone.camera_id != camera_id:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = body.model_dump(exclude_unset=True)
    if "polygon" in update_data and update_data["polygon"] is not None:
        update_data["polygon"] = [p.model_dump() for p in update_data["polygon"]]
    for field, value in update_data.items():
        setattr(zone, field, value)

    await db.flush()
    await db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(
    camera_id: uuid.UUID,
    zone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a zone."""
    zone = await db.get(Zone, zone_id)
    if not zone or zone.camera_id != camera_id:
        raise HTTPException(status_code=404, detail="Zone not found")
    await db.delete(zone)
