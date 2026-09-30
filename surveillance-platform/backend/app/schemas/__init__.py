"""Pydantic schemas for request/response validation."""
import uuid
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    role: str = "OPERATOR"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Camera ────────────────────────────────────────────
class CameraCreate(BaseModel):
    name: str
    source_type: str  # file, rtsp, webcam
    source_reference: str
    location_label: Optional[str] = None


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    location_label: Optional[str] = None
    enabled: Optional[bool] = None


class CameraResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    source_reference: str
    location_label: Optional[str]
    enabled: bool
    status: str
    last_seen_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Zone ──────────────────────────────────────────────
class PolygonPoint(BaseModel):
    x: float
    y: float


class ZoneCreate(BaseModel):
    name: str
    type: str  # restricted, entry_exit, high_risk, counting
    polygon: List[PolygonPoint]


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    polygon: Optional[List[PolygonPoint]] = None
    enabled: Optional[bool] = None


class ZoneResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    name: str
    type: str
    polygon: List[PolygonPoint]
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Rule ──────────────────────────────────────────────
class RuleCreate(BaseModel):
    rule_type: str  # dwell, restricted_entry, line_crossing, crowd
    configuration: dict  # rule-specific settings


class RuleUpdate(BaseModel):
    rule_type: Optional[str] = None
    configuration: Optional[dict] = None
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    rule_type: str
    configuration: dict
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Event ─────────────────────────────────────────────
class EventResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    event_type: str
    severity: str
    confidence: float
    occurred_at: datetime
    track_id: Optional[str]
    evidence_uri: Optional[str]
    status: str
    metadata: Optional[dict]

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    page_size: int


class EventStatusUpdate(BaseModel):
    status: str  # ACKNOWLEDGED, DISMISSED


# ── Analytics ─────────────────────────────────────────
class AnalyticsSummary(BaseModel):
    total_events: int
    events_by_type: dict
    events_by_severity: dict
    active_cameras: int
    total_tracks: int
    avg_confidence: float
    uptime_hours: float


# ── Track ─────────────────────────────────────────────
class TrackResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    track_id: str
    object_class: str
    first_seen: datetime
    last_seen: datetime
    summary: Optional[dict]

    model_config = {"from_attributes": True}
