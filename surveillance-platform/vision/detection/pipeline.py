"""Main processing pipeline: orchestrates capture → detection → tracking → events."""
import time
import asyncio
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field

import numpy as np

from vision.detection.yolo_detector import YOLODetector, DetectionResult
from vision.detection.preprocessor import FramePreprocessor
from vision.tracking.byte_tracker import SimpleByteTracker, TrackState
from vision.features.trajectory import TrajectoryAnalyzer, TrajectoryFeatures
from vision.features.zone_geometry import point_in_polygon, is_bbox_in_zone
from vision.anomaly.event_engine import (
    EventEngine, GeneratedEvent, ZoneConfig, RuleConfig, EventType, Severity
)
from vision.anomaly.temporal_model import TemporalAnomalyDetector


@dataclass
class PipelineStats:
    """Processing pipeline statistics."""
    frames_processed: int = 0
    total_detections: int = 0
    total_events: int = 0
    avg_detection_latency_ms: float = 0.0
    avg_tracking_latency_ms: float = 0.0
    avg_event_latency_ms: float = 0.0
    avg_fps: float = 0.0
    active_tracks: int = 0
    _fps_window: list = field(default_factory=list)
    _detection_latencies: list = field(default_factory=list)
    _tracking_latencies: list = field(default_factory=list)
    _event_latencies: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "frames_processed": self.frames_processed,
            "total_detections": self.total_detections,
            "total_events": self.total_events,
            "avg_detection_latency_ms": round(self.avg_detection_latency_ms, 2),
            "avg_tracking_latency_ms": round(self.avg_tracking_latency_ms, 2),
            "avg_event_latency_ms": round(self.avg_event_latency_ms, 2),
            "avg_fps": round(self.avg_fps, 2),
            "active_tracks": self.active_tracks,
        }


class ProcessingPipeline:
    """
    Full video processing pipeline.

    Flow:
        Frame → Preprocess → Detect → Track → Feature Extract → Event Check → Persist

    Features:
    - Frame skipping for performance
    - Bounded processing queues
    - Camera health monitoring
    - Explainable event generation
    """

    def __init__(
        self,
        camera_id: str,
        detector: YOLODetector,
        frame_skip_interval: int = 2,
        confidence_threshold: float = 0.5,
        enable_anomaly_model: bool = False,
    ):
        self.camera_id = camera_id
        self.detector = detector
        self.frame_skip_interval = frame_skip_interval
        self.confidence_threshold = confidence_threshold
        self.enable_anomaly_model = enable_anomaly_model

        # Components
        self.preprocessor = FramePreprocessor()
        self.tracker = SimpleByteTracker(
            match_thresh=0.8,
            max_time_lost=30,
        )
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.event_engine = EventEngine()
        self.anomaly_detector = TemporalAnomalyDetector() if enable_anomaly_model else None

        # State
        self.stats = PipelineStats()
        self._frame_count = 0
        self._active_features: List[TrajectoryFeatures] = []
        self._frame_buffer: List[np.ndarray] = []
        self._max_frame_buffer = 300  # ~10 seconds at 30fps

        # Callbacks
        self._on_event: Optional[Callable] = None
        self._on_tracks: Optional[Callable] = None

    def set_callbacks(
        self,
        on_event: Optional[Callable] = None,
        on_tracks: Optional[Callable] = None,
    ):
        """Set callback functions for events and track updates."""
        self._on_event = on_event
        self._on_tracks = on_tracks

    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: float,
    ) -> Optional[dict]:
        """
        Process a single frame through the full pipeline.

        Args:
            frame: BGR image (H, W, 3)
            timestamp: Frame timestamp

        Returns:
            Processing result dict, or None if frame was skipped
        """
        self._frame_count += 1
        self.stats.frames_processed += 1

        # Frame skipping: detect every N frames, track every frame
        should_detect = (self._frame_count % self.frame_skip_interval == 0)

        # Store frame for evidence
        self._frame_buffer.append(frame)
        if len(self._frame_buffer) > self._max_frame_buffer:
            self._frame_buffer.pop(0)

        result = {
            "camera_id": self.camera_id,
            "timestamp": timestamp,
            "frame_count": self._frame_count,
            "detections": [],
            "tracks": [],
            "events": [],
            "stats": {},
        }

        # ── Detection ──
        detection_result: Optional[DetectionResult] = None
        if should_detect:
            det_start = time.perf_counter()
            detection_result = self.detector.detect(frame, timestamp)
            det_latency = (time.perf_counter() - det_start) * 1000
            self.stats._detection_latencies.append(det_latency)
            self.stats.total_detections += len(detection_result.detections)
            result["detections"] = [d.__dict__ for d in detection_result.detections]

        # ── Tracking ──
        track_start = time.perf_counter()
        if detection_result is not None:
            active_tracks = self.tracker.update(detection_result.detections, timestamp)
        else:
            # Use last detections for tracking (same frame, no re-detection)
            active_tracks = self.tracker.update([], timestamp)

        track_latency = (time.perf_counter() - track_start) * 1000
        self.stats._tracking_latencies.append(track_latency)
        self.stats.active_tracks = len(active_tracks)

        result["tracks"] = [t.to_dict() for t in active_tracks]

        # ── Feature Extraction ──
        self._active_features = []
        for track in active_tracks:
            features = self.trajectory_analyzer.update(
                track_id=track.track_id,
                bbox=track.bbox,
                timestamp=timestamp,
            )
            self._active_features.append(features)

        # ── Event Detection ──
        event_start = time.perf_counter()
        all_events: List[GeneratedEvent] = []

        for features in self._active_features:
            events = self.event_engine.evaluate(
                camera_id=self.camera_id,
                features=features,
                timestamp=timestamp,
            )
            all_events.extend(events)

        # Crowd detection (needs all features)
        for rule in self.event_engine.rules.values():
            if rule.rule_type == "crowd":
                crowd_event = self.event_engine.evaluate_crowd(
                    camera_id=self.camera_id,
                    all_features=self._active_features,
                    rule=rule,
                    timestamp=timestamp,
                )
                if crowd_event:
                    all_events.append(crowd_event)

        # Anomaly model (if enabled)
        if self.anomaly_detector:
            for features in self._active_features:
                feat_vector = self._extract_anomaly_features(features)
                anomaly_result = self.anomaly_detector.update_and_score(
                    features.track_id, feat_vector
                )
                if anomaly_result and anomaly_result.is_anomaly:
                    all_events.append(GeneratedEvent(
                        id=f"anomaly_{features.track_id}_{int(timestamp)}",
                        camera_id=self.camera_id,
                        event_type=EventType.ANOMALY,
                        severity=Severity.WARNING,
                        confidence=anomaly_result.anomaly_score,
                        occurred_at=timestamp,
                        track_id=str(features.track_id),
                        explanation=(
                            f"Track {features.track_id} shows anomalous behavior "
                            f"(score: {anomaly_result.anomaly_score:.2f}, "
                            f"threshold: {anomaly_result.threshold})."
                        ),
                        metadata={
                            "reconstruction_error": anomaly_result.reconstruction_error,
                            "sequence_length": anomaly_result.sequence_length,
                        },
                    ))

        event_latency = (time.perf_counter() - event_start) * 1000
        self.stats._event_latencies.append(event_latency)
        self.stats.total_events += len(all_events)

        result["events"] = [
            {
                "id": e.id,
                "event_type": e.event_type.value,
                "severity": e.severity.value,
                "confidence": round(e.confidence, 3),
                "track_id": e.track_id,
                "explanation": e.explanation,
                "metadata": e.metadata,
            }
            for e in all_events
        ]

        # ── Update Stats ──
        self._update_stats(timestamp)

        result["stats"] = self.stats.to_dict()

        # ── Callbacks ──
        if all_events and self._on_event:
            for event in all_events:
                self._on_event(event)

        if self._on_tracks and active_tracks:
            self._on_tracks(active_tracks, self._active_features)

        return result

    def _extract_anomaly_features(self, features: TrajectoryFeatures) -> np.ndarray:
        """Extract feature vector for anomaly detection."""
        direction_map = {"up": 0, "down": 1, "left": 2, "right": 3, "static": 4}
        return np.array([
            features.position[0],
            features.position[1],
            features.velocity[0],
            features.velocity[1],
            features.speed,
            features.displacement,
            features.path_length,
            features.dwell_time,
            features.acceleration,
            direction_map.get(features.direction.value, 4),
        ], dtype=np.float32)

    def _update_stats(self, timestamp: float):
        """Update running statistics."""
        # FPS
        self.stats._fps_window.append(timestamp)
        if len(self.stats._fps_window) >= 2:
            dt = self.stats._fps_window[-1] - self.stats._fps_window[0]
            if dt > 0:
                self.stats.avg_fps = len(self.stats._fps_window) / dt

        # Latency averages
        if self.stats._detection_latencies:
            self.stats.avg_detection_latency_ms = np.mean(self.stats._detection_latencies[-100:])
        if self.stats._tracking_latencies:
            self.stats.avg_tracking_latency_ms = np.mean(self.stats._tracking_latencies[-100:])
        if self.stats._event_latencies:
            self.stats.avg_event_latency_ms = np.mean(self.stats._event_latencies[-100:])

    def get_frame_for_evidence(self, lookback_seconds: float = 10.0) -> Optional[np.ndarray]:
        """Get a frame from the buffer for evidence storage."""
        if self._frame_buffer:
            return self._frame_buffer[-1]
        return None

    def get_clip_for_evidence(self, lookback_seconds: float = 10.0) -> List[np.ndarray]:
        """Get frames for an evidence clip."""
        return list(self._frame_buffer[-int(lookback_seconds * 30):])

    def reset(self):
        """Reset pipeline state."""
        self._frame_count = 0
        self.stats = PipelineStats()
        self.tracker.reset()
        self.trajectory_analyzer.clear()
        self._active_features.clear()
        self._frame_buffer.clear()
