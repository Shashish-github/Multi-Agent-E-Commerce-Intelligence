"""Temporal anomaly detection model using LSTM autoencoder."""
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AnomalyResult:
    """Result from anomaly scoring."""
    track_id: int
    anomaly_score: float  # 0.0 = normal, 1.0 = highly anomalous
    reconstruction_error: float
    is_anomaly: bool
    threshold: float
    features_used: int
    sequence_length: int


class TemporalAnomalyDetector:
    """
    LSTM autoencoder for trajectory anomaly detection.

    Architecture:
    - Encoder: LSTM layers that compress trajectory features
    - Decoder: LSTM layers that reconstruct the input
    - Anomaly score: reconstruction error

    This is a placeholder that can be replaced with a trained model.
    For production, train on normal trajectory data from the target deployment.
    """

    def __init__(
        self,
        input_dim: int = 10,  # [x, y, vx, vy, speed, displacement, path_length, dwell_time, acceleration, direction_encoded]
        sequence_length: int = 30,
        hidden_dim: int = 64,
        threshold: float = 0.15,
    ):
        self.input_dim = input_dim
        self.sequence_length = sequence_length
        self.hidden_dim = hidden_dim
        self.threshold = threshold

        # Simple statistics-based fallback (replace with trained LSTM autoencoder)
        self._feature_mean: Optional[np.ndarray] = None
        self._feature_std: Optional[np.ndarray] = None
        self._is_trained = False

        # Per-track buffers
        self._track_buffers: dict = {}

    def train(self, normal_sequences: List[np.ndarray]):
        """
        Train the model on normal trajectory sequences.

        Args:
            normal_sequences: List of (seq_len, input_dim) arrays of normal behavior
        """
        if not normal_sequences:
            return

        # Stack all sequences and compute statistics
        all_data = np.concatenate(normal_sequences, axis=0)
        self._feature_mean = np.mean(all_data, axis=0)
        self._feature_std = np.std(all_data, axis=0) + 1e-8
        self._is_trained = True

        print(f"Anomaly detector trained on {len(normal_sequences)} sequences "
              f"({all_data.shape[0]} total frames)")

    def update_and_score(
        self,
        track_id: int,
        features: np.ndarray,
    ) -> Optional[AnomalyResult]:
        """
        Add a feature vector for a track and score it.

        Args:
            track_id: Unique track ID
            features: Feature vector of shape (input_dim,)

        Returns:
            AnomalyResult if enough data, None otherwise
        """
        if track_id not in self._track_buffers:
            self._track_buffers[track_id] = []

        self._track_buffers[track_id].append(features)

        # Keep only the last sequence_length features
        if len(self._track_buffers[track_id]) > self.sequence_length:
            self._track_buffers[track_id] = self._track_buffers[track_id][-self.sequence_length:]

        buffer = self._track_buffers[track_id]
        if len(buffer) < self.sequence_length // 2:
            return None  # Not enough data yet

        return self._score(track_id, np.array(buffer))

    def _score(self, track_id: int, sequence: np.ndarray) -> AnomalyResult:
        """Compute anomaly score for a feature sequence."""
        if not self._is_trained:
            # Use simple statistics-based scoring
            return self._statistics_score(track_id, sequence)

        # Normalize
        normalized = (sequence - self._feature_mean) / self._feature_std

        # Simple reconstruction: use mean as "reconstruction"
        reconstructed = np.zeros_like(normalized)
        reconstruction_error = float(np.mean((normalized - reconstructed) ** 2))

        is_anomaly = reconstruction_error > self.threshold

        return AnomalyResult(
            track_id=track_id,
            anomaly_score=min(1.0, reconstruction_error / (self.threshold * 3)),
            reconstruction_error=reconstruction_error,
            is_anomaly=is_anomaly,
            threshold=self.threshold,
            features_used=sequence.shape[1],
            sequence_length=len(sequence),
        )

    def _statistics_score(self, track_id: int, sequence: np.ndarray) -> AnomalyResult:
        """Simple statistics-based anomaly scoring."""
        # Compute Z-scores for each feature
        mean = np.mean(sequence, axis=0)
        std = np.std(sequence, axis=0) + 1e-8

        # High std relative to mean suggests unusual behavior
        cv = std / (np.abs(mean) + 1e-6)
        anomaly_score = float(np.mean(np.clip(cv, 0, 5)) / 5.0)

        # Also check for sudden changes
        if len(sequence) >= 2:
            diffs = np.abs(np.diff(sequence, axis=0))
            max_change = float(np.max(np.mean(diffs, axis=1)))
            change_score = min(1.0, max_change / 100.0)
            anomaly_score = max(anomaly_score, change_score)

        is_anomaly = anomaly_score > self.threshold

        return AnomalyResult(
            track_id=track_id,
            anomaly_score=anomaly_score,
            reconstruction_error=anomaly_score,
            is_anomaly=is_anomaly,
            threshold=self.threshold,
            features_used=sequence.shape[1],
            sequence_length=len(sequence),
        )

    def remove_track(self, track_id: int):
        """Clean up buffer for a removed track."""
        self._track_buffers.pop(track_id, None)

    def clear(self):
        """Clear all buffers."""
        self._track_buffers.clear()
