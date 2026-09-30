"""Background worker: runs the processing pipeline for a camera stream."""
import time
import threading
from typing import Optional

from vision.detection.yolo_detector import YOLODetector
from vision.detection.stream_manager import StreamManager, StreamState
from vision.detection.pipeline import ProcessingPipeline
from vision.anomaly.event_engine import ZoneConfig, RuleConfig
from backend.app.core.config import settings


class StreamWorker:
    """
    Worker that connects a StreamManager to a ProcessingPipeline.

    Runs the capture → detection → tracking → event pipeline
    in a background thread.
    """

    def __init__(
        self,
        camera_id: str,
        source: str,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        frame_skip: Optional[int] = None,
    ):
        self.camera_id = camera_id

        # Initialize detector
        self.detector = YOLODetector(
            model_path=model_path or settings.YOLO_MODEL,
            device=device or settings.YOLO_DEVICE,
            confidence_threshold=confidence_threshold or settings.YOLO_CONFIDENCE_THRESHOLD,
        )

        # Initialize pipeline
        self.pipeline = ProcessingPipeline(
            camera_id=camera_id,
            detector=self.detector,
            frame_skip_interval=frame_skip or settings.FRAME_SKIP_INTERVAL,
        )

        # Initialize stream manager
        self.stream_manager = StreamManager(
            camera_id=camera_id,
            source=source,
            buffer_size=settings.FRAME_BUFFER_SIZE,
            reconnect_delay=settings.CAMERA_RECONNECT_DELAY_SECONDS,
        )

        self._running = False

    def configure_zones(self, zones: list):
        """Configure detection zones."""
        for zone_data in zones:
            zone = ZoneConfig(
                zone_id=zone_data["id"],
                name=zone_data["name"],
                zone_type=zone_data["type"],
                polygon=zone_data["polygon"],
                enabled=zone_data.get("enabled", True),
            )
            self.pipeline.event_engine.add_zone(zone)

    def configure_rules(self, rules: list):
        """Configure event rules."""
        for rule_data in rules:
            rule = RuleConfig(
                rule_id=rule_data["id"],
                rule_type=rule_data["rule_type"],
                zone_id=rule_data.get("zone_id"),
                dwell_threshold_seconds=rule_data.get("dwell_threshold_seconds", 30.0),
                crowd_threshold=rule_data.get("crowd_threshold", 5),
                confidence_threshold=rule_data.get("confidence_threshold", 0.5),
                enabled=rule_data.get("enabled", True),
            )
            self.pipeline.event_engine.add_rule(rule)

    def start(self):
        """Start the worker: stream capture + processing."""
        self._running = True
        self.stream_manager.start(on_frame=self._on_frame)
        print(f"[Worker] Started for camera {self.camera_id}")

    def stop(self):
        """Stop the worker."""
        self._running = False
        self.stream_manager.stop()
        self.pipeline.reset()
        print(f"[Worker] Stopped for camera {self.camera_id}")

    def _on_frame(self, camera_id: str, frame, timestamp: float):
        """Called by StreamManager when a new frame is available."""
        if not self._running:
            return

        result = self.pipeline.process_frame(frame, timestamp)
        # In production: push result to WebSocket / Redis pub-sub

    def get_stats(self) -> dict:
        """Get worker statistics."""
        return {
            "camera_id": self.camera_id,
            "stream_health": self.stream_manager.health.to_dict(),
            "pipeline_stats": self.pipeline.stats.to_dict(),
        }
