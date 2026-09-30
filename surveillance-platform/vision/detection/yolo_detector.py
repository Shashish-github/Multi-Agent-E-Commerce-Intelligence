"""YOLO-based object detector with configurable classes and thresholds."""
import time
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    """Single detection result."""
    bbox: np.ndarray  # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    class_name: str
    timestamp: float = 0.0


@dataclass
class DetectionResult:
    """Result from processing a single frame."""
    detections: List[Detection]
    inference_time_ms: float
    frame_timestamp: float
    frame_shape: tuple


class YOLODetector:
    """
    Wraps Ultralytics YOLO for real-time object detection.

    Supports class filtering, confidence thresholds, and batch inference.
    """

    DEFAULT_CLASSES = ["person", "car", "truck", "bus", "motorcycle", "bicycle"]

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        device: str = "cpu",
        target_classes: Optional[List[str]] = None,
        batch_size: int = 1,
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.target_classes = target_classes or self.DEFAULT_CLASSES
        self.batch_size = batch_size

        # Load model
        self.model = YOLO(model_path)
        # Build class filter: only keep these class IDs
        self._class_filter = self._build_class_filter()

    def _build_class_filter(self) -> set:
        """Map target class names to YOLO class IDs."""
        names = self.model.names  # {0: "person", 1: "bicycle", ...}
        name_to_id = {v: k for k, v in names.items()}
        return {name_to_id[c] for c in self.target_classes if c in name_to_id}

    def detect(
        self,
        frame: np.ndarray,
        timestamp: float = 0.0,
    ) -> DetectionResult:
        """
        Run detection on a single frame.

        Args:
            frame: BGR image (H, W, 3)
            timestamp: frame timestamp for tracking

        Returns:
            DetectionResult with filtered detections and timing
        """
        start = time.perf_counter()

        results = self.model(
            frame,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False,
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())
                if cls_id not in self._class_filter:
                    continue

                bbox = boxes.xyxy[i].cpu().numpy()  # [x1, y1, x2, y2]
                class_name = result.names[cls_id]

                detections.append(
                    Detection(
                        bbox=bbox,
                        confidence=conf,
                        class_id=cls_id,
                        class_name=class_name,
                        timestamp=timestamp,
                    )
                )

        inference_time_ms = (time.perf_counter() - start) * 1000

        return DetectionResult(
            detections=detections,
            inference_time_ms=inference_time_ms,
            frame_timestamp=timestamp,
            frame_shape=frame.shape,
        )

    def detect_batch(
        self,
        frames: List[np.ndarray],
        timestamps: Optional[List[float]] = None,
    ) -> List[DetectionResult]:
        """Run detection on a batch of frames."""
        if timestamps is None:
            timestamps = [0.0] * len(frames)

        results = self.model(
            frames,
            conf=self.confidence_threshold,
            device=self.device,
            batch=self.batch_size,
            verbose=False,
        )

        detection_results = []
        for frame, ts, result in zip(frames, timestamps, results):
            detections = []
            if result.boxes is not None:
                for i in range(len(result.boxes)):
                    cls_id = int(result.boxes.cls[i].item())
                    if cls_id not in self._class_filter:
                        continue
                    detections.append(
                        Detection(
                            bbox=result.boxes.xyxy[i].cpu().numpy(),
                            confidence=float(result.boxes.conf[i].item()),
                            class_id=cls_id,
                            class_name=result.names[cls_id],
                            timestamp=ts,
                        )
                    )
            detection_results.append(
                DetectionResult(
                    detections=detections,
                    inference_time_ms=0.0,  # TODO: measure per-frame
                    frame_timestamp=ts,
                    frame_shape=frame.shape,
                )
            )
        return detection_results

    def warmup(self, input_shape: tuple = (1, 640, 640, 3)):
        """Warm up the model with a dummy forward pass."""
        dummy = np.random.randint(0, 255, input_shape, dtype=np.uint8)
        self.detect(dummy)
