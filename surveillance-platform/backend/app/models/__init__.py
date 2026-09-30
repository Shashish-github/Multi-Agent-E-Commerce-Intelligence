"""SQLAlchemy database models."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="OPERATOR")  # ADMIN or OPERATOR
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    cameras = relationship("Camera", back_populates="owner")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # file, rtsp, webcam
    source_reference = Column(Text, nullable=False)
    location_label = Column(String(255), nullable=True)
    enabled = Column(Boolean, default=True)
    status = Column(String(20), default="OFFLINE")  # ONLINE, OFFLINE, DEGRADED
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    owner = relationship("User", back_populates="cameras")
    zones = relationship("Zone", back_populates="camera", cascade="all, delete-orphan")
    rules = relationship("Rule", back_populates="camera", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="camera")
    tracks = relationship("Track", back_populates="camera")


class Zone(Base):
    __tablename__ = "zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # restricted, entry_exit, high_risk, counting
    polygon = Column(JSONB, nullable=False)  # [{"x": 0, "y": 0}, ...]
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    camera = relationship("Camera", back_populates="zones")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    rule_type = Column(String(50), nullable=False)  # dwell, restricted_entry, line_crossing, crowd
    configuration = Column(JSONB, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    camera = relationship("Camera", back_populates="rules")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # RESTRICTED_ENTRY, LOITERING, LINE_CROSSING, CROWD, ABANDONED_OBJECT, ANOMALY
    severity = Column(String(20), nullable=False, default="INFO")  # INFO, WARNING, CRITICAL
    confidence = Column(Float, nullable=False, default=0.0)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    track_id = Column(String(50), nullable=True)
    evidence_uri = Column(Text, nullable=True)
    status = Column(String(20), default="NEW")  # NEW, ACKNOWLEDGED, DISMISSED
    metadata = Column(JSONB, nullable=True)

    camera = relationship("Camera", back_populates="events")

    __table_args__ = (
        Index("ix_events_camera_occurred", "camera_id", "occurred_at"),
        Index("ix_events_type_occurred", "event_type", "occurred_at"),
        Index("ix_events_severity", "severity"),
        Index("ix_events_status", "status"),
    )


class Track(Base):
    __tablename__ = "tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False)
    track_id = Column(String(50), nullable=False)
    object_class = Column(String(50), nullable=False)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    summary = Column(JSONB, nullable=True)  # trajectory summary, avg speed, etc.

    camera = relationship("Camera", back_populates="tracks")

    __table_args__ = (
        Index("ix_tracks_camera_track", "camera_id", "track_id"),
    )
