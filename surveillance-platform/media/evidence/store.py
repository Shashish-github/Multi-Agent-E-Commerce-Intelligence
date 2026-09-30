"""Evidence storage: save clips, thumbnails, and event frames."""
import os
import time
from pathlib import Path
from typing import Optional, Protocol, List
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class EvidenceMetadata:
    """Metadata for a stored evidence piece."""
    event_id: str
    camera_id: str
    evidence_type: str  # clip, frame, thumbnail
    file_path: str
    file_size: int
    created_at: float
    duration_seconds: Optional[float] = None


class EvidenceStore:
    """
    File-based evidence storage with configurable retention.

    Stores event-triggered evidence clips, frames, and thumbnails.
    """

    def __init__(
        self,
        base_path: str = "./media/evidence",
        retention_days: int = 30,
        max_clip_seconds: int = 30,
        max_clip_size_mb: int = 50,
    ):
        self.base_path = Path(base_path)
        self.retention_days = retention_days
        self.max_clip_seconds = max_clip_seconds
        self.max_clip_size_mb = max_clip_size_mb

        # Create directory structure
        self.clips_dir = self.base_path / "clips"
        self.frames_dir = self.base_path / "frames"
        self.thumbnails_dir = self.base_path / "thumbnails"

        for d in [self.clips_dir, self.frames_dir, self.thumbnails_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def save_frame(
        self,
        event_id: str,
        camera_id: str,
        frame: np.ndarray,
    ) -> EvidenceMetadata:
        """Save a single frame as evidence."""
        filename = f"{event_id}_{camera_id}.jpg"
        filepath = self.frames_dir / filename

        cv2.imwrite(str(filepath), frame)
        file_size = filepath.stat().st_size

        return EvidenceMetadata(
            event_id=event_id,
            camera_id=camera_id,
            evidence_type="frame",
            file_path=str(filepath),
            file_size=file_size,
            created_at=time.time(),
        )

    def save_clip(
        self,
        event_id: str,
        camera_id: str,
        frames: List[np.ndarray],
        fps: float = 24.0,
    ) -> EvidenceMetadata:
        """Save a video clip from a list of frames."""
        if not frames:
            raise ValueError("No frames to save")

        filename = f"{event_id}_{camera_id}.mp4"
        filepath = self.clips_dir / filename

        # Limit clip duration
        max_frames = int(self.max_clip_seconds * fps)
        if len(frames) > max_frames:
            frames = frames[-max_frames:]

        h, w = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(filepath), fourcc, fps, (w, h))

        for frame in frames:
            writer.write(frame)
        writer.release()

        file_size = filepath.stat().st_size
        duration = len(frames) / fps

        return EvidenceMetadata(
            event_id=event_id,
            camera_id=camera_id,
            evidence_type="clip",
            file_path=str(filepath),
            file_size=file_size,
            created_at=time.time(),
            duration_seconds=duration,
        )

    def save_thumbnail(
        self,
        event_id: str,
        camera_id: str,
        frame: np.ndarray,
        max_size: tuple = (320, 240),
    ) -> EvidenceMetadata:
        """Save a resized thumbnail."""
        filename = f"{event_id}_{camera_id}_thumb.jpg"
        filepath = self.thumbnails_dir / filename

        thumb = cv2.resize(frame, max_size, interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(filepath), thumb)
        file_size = filepath.stat().st_size

        return EvidenceMetadata(
            event_id=event_id,
            camera_id=camera_id,
            evidence_type="thumbnail",
            file_path=str(filepath),
            file_size=file_size,
            created_at=time.time(),
        )

    def get_evidence_path(self, event_id: str, camera_id: str) -> Optional[str]:
        """Get the path to stored evidence for an event."""
        # Try clip first, then frame
        for ext in ["mp4", "jpg"]:
            pattern = f"{event_id}_{camera_id}"
            if ext == "jpg":
                pattern += ".jpg"
            else:
                pattern += ".mp4"

            for dir_path in [self.clips_dir, self.frames_dir]:
                path = dir_path / pattern
                if path.exists():
                    return str(path)
        return None

    def cleanup_expired(self) -> int:
        """Remove evidence older than retention period. Returns count of removed files."""
        cutoff = time.time() - (self.retention_days * 86400)
        removed = 0

        for dir_path in [self.clips_dir, self.frames_dir, self.thumbnails_dir]:
            for path in dir_path.iterdir():
                if path.is_file() and path.stat().st_mtime < cutoff:
                    path.unlink()
                    removed += 1

        return removed

    def get_stats(self) -> dict:
        """Get storage statistics."""
        total_size = 0
        file_count = 0

        for dir_path in [self.clips_dir, self.frames_dir, self.thumbnails_dir]:
            for path in dir_path.iterdir():
                if path.is_file():
                    total_size += path.stat().st_size
                    file_count += 1

        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "clips_count": len(list(self.clips_dir.iterdir())),
            "frames_count": len(list(self.frames_dir.iterdir())),
            "thumbnails_count": len(list(self.thumbnails_dir.iterdir())),
            "retention_days": self.retention_days,
        }
