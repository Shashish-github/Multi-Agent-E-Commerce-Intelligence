"""API v1 router: aggregates all sub-routers."""
from fastapi import APIRouter

from backend.app.api.v1.cameras import router as cameras_router
from backend.app.api.v1.zones import router as zones_router
from backend.app.api.v1.rules import router as rules_router
from backend.app.api.v1.events import router as events_router
from backend.app.api.v1.analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(cameras_router, prefix="/cameras", tags=["cameras"])
api_router.include_router(zones_router, prefix="/cameras/{camera_id}/zones", tags=["zones"])
api_router.include_router(rules_router, prefix="/cameras/{camera_id}/rules", tags=["rules"])
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
