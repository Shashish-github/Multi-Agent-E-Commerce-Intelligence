"""Frame preprocessing utilities for the detection pipeline."""
import cv2
import numpy as np
from typing import Tuple, Optional


class FramePreprocessor:
    """
    Handles frame preprocessing before detection:
    - Resize to model input size
    - Normalize pixel values
    - Color space conversion
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = (640, 640),
        normalize: bool = True,
    ):
        self.target_size = target_size
        self.normalize = normalize

    def resize(self, frame: np.ndarray) -> np.ndarray:
        """Resize frame to target dimensions."""
        return cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)

    def letterbox(
        self,
        frame: np.ndarray,
        new_shape: Optional[Tuple[int, int]] = None,
        color: tuple = (114, 114, 114),
    ) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Letterbox resize maintaining aspect ratio.
        Returns (resized_frame, ratio, (pad_w, pad_h)).
        """
        shape = frame.shape[:2]  # h, w
        new_shape = new_shape or self.target_size

        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))

        dw = (new_shape[1] - new_unpad[0]) / 2
        dh = (new_shape[0] - new_unpad[1]) / 2

        if shape[::-1] != new_unpad:
            frame = cv2.resize(frame, new_unpad, interpolation=cv2.INTER_LINEAR)

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        frame = cv2.copyMakeBorder(
            frame, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=color,
        )
        return frame, r, (dw, dh)

    def normalize_pixels(self, frame: np.ndarray) -> np.ndarray:
        """Normalize pixel values to [0, 1]."""
        return frame.astype(np.float32) / 255.0

    def to_rgb(self, frame: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def preprocess(
        self,
        frame: np.ndarray,
        use_letterbox: bool = True,
    ) -> Tuple[np.ndarray, dict]:
        """
        Full preprocessing pipeline.

        Args:
            frame: Input BGR frame
            use_letterbox: Whether to use letterbox resize

        Returns:
            (preprocessed_frame, metadata)
        """
        metadata = {"original_shape": frame.shape}

        if use_letterbox:
            processed, ratio, (dw, dh) = self.letterbox(frame)
            metadata["ratio"] = ratio
            metadata["pad"] = (dw, dh)
        else:
            processed = self.resize(frame)

        metadata["processed_shape"] = processed.shape

        if self.normalize:
            processed = self.normalize_pixels(processed)

        return processed, metadata

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: list,
        show_labels: bool = True,
        show_conf: bool = True,
        line_thickness: int = 2,
    ) -> np.ndarray:
        """
        Draw detection bounding boxes on a frame.
        """
        overlay = frame.copy()

        color_map = {
            "person": (0, 255, 0),
            "car": (255, 0, 0),
            "truck": (255, 128, 0),
            "bus": (255, 255, 0),
            "motorcycle": (128, 0, 255),
            "bicycle": (0, 128, 255),
        }

        for det in detections:
            x1, y1, x2, y2 = det.bbox.astype(int)
            color = color_map.get(det.class_name, (0, 255, 0))

            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, line_thickness)

            label_parts = []
            if show_labels:
                label_parts.append(det.class_name)
            if show_conf:
                label_parts.append(f"{det.confidence:.2f}")
            label = " ".join(label_parts)

            if label:
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(overlay, (x1, y1 - th - 8), (x1 + tw, y1), color, -1)
                cv2.putText(
                    overlay, label, (x1, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                )

        return overlay
