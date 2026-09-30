"""Camera management routes."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models import Camera, User
from backend.app.schemas import CameraCreate, CameraUpdate, CameraResponse
from backend.app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[CameraResponse])
async def list_cameras(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all cameras the user has access to."""
    result = await db.execute(select(Camera).order_by(Camera.created_at.desc()))
    cameras = result.scalars().all()
    return cameras


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    body: CameraCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register a new camera source."""
    camera = Camera(
        name=body.name,
        source_type=body.source_type,
        source_reference=body.source_reference,
        location_label=body.location_label,
        owner_id=user.id,
    )
    db.add(camera)
    await db.flush()
    await db.refresh(camera)
    return camera


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get camera details."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: uuid.UUID,
    body: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update camera metadata/configuration."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)

    await db.flush()
    await db.refresh(camera)
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a camera and all associated data."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    await db.delete(camera)


@router.post("/{camera_id}/test")
async def test_camera(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Test camera source connectivity."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Import here to avoid circular imports at module level
    import cv2
    try:
        cap = cv2.VideoCapture(camera.source_reference)
        if not cap.isOpened():
            return {"status": "error", "message": "Could not open stream"}
        ret, frame = cap.read()
        cap.release()
        if ret:
            return {"status": "ok", "message": "Stream accessible"}
        return {"status": "error", "message": "Could not read frame"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/{camera_id}/status")
async def get_camera_status(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return camera health and processing metrics."""
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    return {
        "camera_id": str(camera.id),
        "status": camera.status,
        "last_seen_at": camera.last_seen_at.isoformat() if camera.last_seen_at else None,
        "enabled": camera.enabled,
    }
