"""Application settings loaded from environment variables."""
import os
from typing import List

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://surveillance:surveillance@localhost:5432/surveillance"
    DATABASE_URL_SYNC: str = "postgresql://surveillance:surveillance@localhost:5432/surveillance"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # YOLO
    YOLO_MODEL: str = "yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    YOLO_DEVICE: str = "cpu"

    # Tracker
    TRACKER_MATCH_THRESHOLD: float = 0.8
    TRACKER_BUFFER: int = 30

    # Video
    FRAME_BUFFER_SIZE: int = 64
    FRAME_SKIP_INTERVAL: int = 2
    MAX_CAMERAS: int = 16

    # Evidence
    EVIDENCE_STORAGE_PATH: str = "./media/evidence"
    EVIDENCE_RETENTION_DAYS: int = 30
    EVIDENCE_MAX_CLIP_SECONDS: int = 30

    # Camera
    CAMERA_RECONNECT_DELAY_SECONDS: int = 5
    CAMERA_HEALTH_CHECK_INTERVAL_SECONDS: int = 10

    # Performance
    MAX_INFERENCE_WORKERS: int = 4
    DETECTION_BATCH_SIZE: int = 1

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Default admin
    DEFAULT_ADMIN_EMAIL: str = "admin@surveillance.local"
    DEFAULT_ADMIN_PASSWORD: str = "changeme"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
