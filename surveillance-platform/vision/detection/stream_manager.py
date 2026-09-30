"""Stream manager: handles video capture with frame buffering and reconnection."""
import asyncio
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Callable, Deque
from enum import Enum

import cv2
import numpy as np


class StreamState(str, Enum):
    OFFLINE = "OFFLINE"
    CONNECTING = "CONNECTING"
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"


@dataclass
class CameraHealth:
    """Health status of a camera stream."""
    camera_id: str
    state: StreamState
    fps: float = 0.0
    frames_captured: int = 0
    frames_dropped: int = 0
    last_frame_time: float = 0.0
    error_message: Optional[str] = None
    reconnect_attempts: int = 0

    def to_dict(self) -> dict:
        return {
            "camera_id": self.camera_id,
            "state": self.state.value,
            "fps": round(self.fps, 2),
            "frames_captured": self.frames_captured,
            "frames_dropped": self.frames_dropped,
            "last_frame_time": self.last_frame_time,
            "error_message": self.error_message,
            "reconnect_attempts": self.reconnect_attempts,
        }


class StreamManager:
    """
    Manages a single video stream with:
    - Async frame capture
    - Bounded frame buffer
    - Automatic reconnection with exponential backoff
    - Health monitoring
    """

    def __init__(
        self,
        camera_id: str,
        source: str,
        buffer_size: int = 64,
        reconnect_delay: float = 5.0,
        max_reconnect_attempts: int = 10,
        health_check_interval: float = 10.0,
    ):
        self.camera_id = camera_id
        self.source = source
        self.buffer_size = buffer_size
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        self.health_check_interval = health_check_interval

        self.health = CameraHealth(camera_id=camera_id, state=StreamState.OFFLINE)
        self._buffer: Deque[np.ndarray] = deque(maxlen=buffer_size)
        self._cap: Optional[cv2.VideoCapture] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._on_frame_callback: Optional[Callable[[str, np.ndarray, float], None]] = None
        self._fps_counter: Deque[float] = deque(maxlen=60)

    def start(self, on_frame: Optional[Callable] = None):
        """Start the stream capture in a background thread."""
        self._on_frame_callback = on_frame
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the stream capture."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self._release_capture()
        self.health.state = StreamState.OFFLINE

    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame from the buffer."""
        with self._lock:
            if self._buffer:
                return self._buffer[-1].copy()
            return None

    def _capture_loop(self):
        """Main capture loop with reconnection logic."""
        backoff = self.reconnect_delay

        while self._running:
            try:
                self.health.state = StreamState.CONNECTING
                self._connect()

                if self._cap is None or not self._cap.isOpened():
                    raise ConnectionError("Failed to open video source")

                self.health.state = StreamState.ONLINE
                self.health.reconnect_attempts = 0
                backoff = self.reconnect_delay

                while self._running and self._cap.isOpened():
                    ret, frame = self._cap.read()
                    if not ret:
                        raise ConnectionError("Frame read failed")

                    timestamp = time.perf_counter()
                    self.health.frames_captured += 1
                    self.health.last_frame_time = timestamp

                    # FPS calculation
                    self._fps_counter.append(timestamp)
                    if len(self._fps_counter) >= 2:
                        dt = self._fps_counter[-1] - self._fps_counter[0]
                        if dt > 0:
                            self.health.fps = len(self._fps_counter) / dt

                    # Add to buffer (drop oldest if full)
                    with self._lock:
                        if len(self._buffer) >= self.buffer_size:
                            self.health.frames_dropped += 1
                        self._buffer.append(frame.copy())

                    # Callback
                    if self._on_frame_callback:
                        try:
                            self._on_frame_callback(self.camera_id, frame, timestamp)
                        except Exception as e:
                            print(f"[StreamManager] Callback error: {e}")

            except Exception as e:
                self.health.state = StreamState.DEGRADED
                self.health.error_message = str(e)
                self._release_capture()

                if self.health.reconnect_attempts >= self.max_reconnect_attempts:
                    self.health.state = StreamState.OFFLINE
                    break

                self.health.reconnect_attempts += 1
                time.sleep(min(backoff * (2 ** self.health.reconnect_attempts), 60.0))

    def _connect(self):
        """Connect to the video source."""
        self._release_capture()
        self._cap = cv2.VideoCapture(self.source)

        # Set buffer size to reduce latency
        if self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def _release_capture(self):
        """Release the video capture."""
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None


class StreamManagerRegistry:
    """Registry of active stream managers."""

    def __init__(self):
        self._managers: dict[str, StreamManager] = {}

    def create(
        self,
        camera_id: str,
        source: str,
        **kwargs,
    ) -> StreamManager:
        """Create and register a new stream manager."""
        if camera_id in self._managers:
            self._managers[camera_id].stop()

        manager = StreamManager(camera_id=camera_id, source=source, **kwargs)
        self._managers[camera_id] = manager
        return manager

    def get(self, camera_id: str) -> Optional[StreamManager]:
        """Get a stream manager by camera ID."""
        return self._managers.get(camera_id)

    def stop(self, camera_id: str):
        """Stop a specific stream manager."""
        if camera_id in self._managers:
            self._managers[camera_id].stop()
            del self._managers[camera_id]

    def stop_all(self):
        """Stop all stream managers."""
        for manager in self._managers.values():
            manager.stop()
        self._managers.clear()

    def get_all_health(self) -> list:
        """Get health status of all streams."""
        return [m.health.to_dict() for m in self._managers.values()]

    @property
    def active_count(self) -> int:
        return sum(
            1 for m in self._managers.values()
            if m.health.state == StreamState.ONLINE
        )
