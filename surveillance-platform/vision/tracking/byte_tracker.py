"""ByteTrack multi-object tracker integration."""
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import numpy as np

from vision.detection.yolo_detector import Detection


@dataclass
class TrackState:
    """State of a single tracked object."""
    track_id: int
    class_name: str
    class_id: int
    bbox: np.ndarray  # [x1, y1, x2, y2]
    confidence: float
    first_seen: float  # timestamp
    last_seen: float  # timestamp
    age: int = 0  # frames since first seen
    hits: int = 1  # total detections matched
    time_since_update: int = 0
    trajectory: List[np.ndarray] = field(default_factory=list)
    velocities: List[np.ndarray] = field(default_factory=list)

    @property
    def center(self) -> np.ndarray:
        return (self.bbox[:2] + self.bbox[2:]) / 2

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def is_confirmed(self) -> bool:
        return self.hits >= 3

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "bbox": self.bbox.tolist(),
            "confidence": float(self.confidence),
            "center": self.center.tolist(),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "age": self.age,
            "hits": self.hits,
            "trajectory_length": len(self.trajectory),
        }


class SimpleByteTracker:
    """
    Simplified ByteTrack-inspired tracker for real-time use.

    Uses IoU-based matching with a two-stage approach:
    1. Match high-confidence detections to existing tracks
    2. Match remaining low-confidence detections to unmatched tracks

    For production, consider using the official ByteTrack implementation:
    pip install byte-track
    """

    def __init__(
        self,
        track_thresh: float = 0.5,
        high_thresh: float = 0.6,
        match_thresh: float = 0.8,
        max_time_lost: int = 30,
        min_hits: int = 3,
    ):
        self.track_thresh = track_thresh
        self.high_thresh = high_thresh
        self.match_thresh = match_thresh
        self.max_time_lost = max_time_lost
        self.min_hits = min_hits

        self.tracks: Dict[int, TrackState] = {}
        self.next_id = 0
        self.frame_count = 0

    @staticmethod
    def _iou_batch(
        bb_detections: np.ndarray,
        bb_tracks: np.ndarray,
    ) -> np.ndarray:
        """Compute IoU between two sets of bounding boxes."""
        if len(bb_detections) == 0 or len(bb_tracks) == 0:
            return np.empty((len(bb_detections), len(bb_tracks)))

        # Expand dimensions for broadcasting
        det = bb_detections[:, np.newaxis, :]  # (N, 1, 4)
        trk = bb_tracks[np.newaxis, :, :]  # (1, M, 4)

        # Intersection
        inter_x1 = np.maximum(det[..., 0], trk[..., 0])
        inter_y1 = np.maximum(det[..., 1], trk[..., 1])
        inter_x2 = np.minimum(det[..., 2], trk[..., 2])
        inter_y2 = np.minimum(det[..., 3], trk[..., 3])
        inter_area = np.maximum(0, inter_x2 - inter_x1) * np.maximum(0, inter_y2 - inter_y1)

        # Union
        det_area = (det[..., 2] - det[..., 0]) * (det[..., 3] - det[..., 1])
        trk_area = (trk[..., 2] - trk[..., 0]) * (trk[..., 3] - trk[..., 1])
        union_area = det_area + trk_area - inter_area

        return inter_area / (union_area + 1e-6)

    @staticmethod
    def _hungarian_match(
        cost_matrix: np.ndarray,
        threshold: float,
    ) -> tuple:
        """
        Simple greedy matching (faster than scipy.optimize for real-time).
        Returns (matched_det_indices, matched_trk_indices, unmatched_dets, unmatched_trks).
        """
        matched_dets = set()
        matched_trks = set()
        matches = []

        # Sort by cost (ascending) for greedy matching
        cost_flat = cost_matrix.flatten()
        sorted_indices = np.argsort(cost_flat)

        for idx in sorted_indices:
            if cost_flat[idx] >= threshold:
                break
            det_idx = idx // cost_matrix.shape[1]
            trk_idx = idx % cost_matrix.shape[1]
            if det_idx not in matched_dets and trk_idx not in matched_trks:
                matches.append((det_idx, trk_idx))
                matched_dets.add(det_idx)
                matched_trks.add(trk_idx)

        unmatched_dets = [i for i in range(cost_matrix.shape[0]) if i not in matched_dets]
        unmatched_trks = [i for i in range(cost_matrix.shape[1]) if i not in matched_trks]

        return matches, unmatched_dets, unmatched_trks

    def update(self, detections: List[Detection], timestamp: float = 0.0) -> List[TrackState]:
        """
        Update tracker with new detections.

        Args:
            detections: List of Detection objects from the detector
            timestamp: Current frame timestamp

        Returns:
            List of active TrackState objects
        """
        self.frame_count += 1

        if len(detections) == 0 and len(self.tracks) == 0:
            return []

        # Separate high/low confidence detections
        dets_high = []
        dets_low = []
        for det in detections:
            if det.confidence >= self.high_thresh:
                dets_high.append(det)
            elif det.confidence >= self.track_thresh:
                dets_low.append(det)

        # Get existing track bounding boxes
        track_ids = list(self.tracks.keys())
        track_bboxes = np.array([self.tracks[tid].bbox for tid in track_ids]) if track_ids else np.empty((0, 4))

        # Stage 1: Match high-confidence detections to tracks
        if len(dets_high) > 0 and len(track_bboxes) > 0:
            det_bboxes = np.array([d.bbox for d in dets_high])
            iou_matrix = self._iou_batch(det_bboxes, track_bboxes)
            matches, unmatched_dets, unmatched_trks = self._hungarian_match(
                iou_matrix, self.match_thresh
            )

            for det_idx, trk_idx in matches:
                track = self.tracks[track_ids[trk_idx]]
                det = dets_high[det_idx]
                self._update_track(track, det, timestamp)
        else:
            unmatched_dets = list(range(len(dets_high)))
            unmatched_trks = list(range(len(track_ids)))

        # Stage 2: Match low-confidence detections to remaining unmatched tracks
        remaining_trk_ids = [track_ids[i] for i in unmatched_trks]
        remaining_trk_bboxes = np.array([self.tracks[tid].bbox for tid in remaining_trk_ids]) if remaining_trk_ids else np.empty((0, 4))

        if len(dets_low) > 0 and len(remaining_trk_bboxes) > 0:
            det_bboxes = np.array([d.bbox for d in dets_low])
            iou_matrix = self._iou_batch(det_bboxes, remaining_trk_bboxes)
            low_matches, _, still_unmatched_trks = self._hungarian_match(
                iou_matrix, self.match_thresh
            )

            for det_idx, trk_idx in low_matches:
                track = self.tracks[remaining_trk_ids[trk_idx]]
                det = dets_low[det_idx]
                self._update_track(track, det, timestamp)

            unmatched_trks = [remaining_trk_ids[i] for i in still_unmatched_trks]
        else:
            unmatched_trks = remaining_trk_ids

        # Mark unmatched tracks
        for trk_id in unmatched_trks:
            if trk_id in self.tracks:
                self.tracks[trk_id].time_since_update += 1
                self.tracks[trk_id].age += 1

        # Remove lost tracks
        lost_ids = [
            tid for tid, track in self.tracks.items()
            if track.time_since_update > self.max_time_lost
        ]
        for tid in lost_ids:
            del self.tracks[tid]

        # Create new tracks for unmatched high-confidence detections
        for det_idx in unmatched_dets:
            det = dets_high[det_idx]
            self._create_track(det, timestamp)

        # Return confirmed tracks
        active_tracks = [
            track for track in self.tracks.values()
            if track.time_since_update == 0 and track.hits >= self.min_hits
        ]
        return active_tracks

    def _create_track(self, detection: Detection, timestamp: float):
        """Create a new track from a detection."""
        track = TrackState(
            track_id=self.next_id,
            class_name=detection.class_name,
            class_id=detection.class_id,
            bbox=detection.bbox.copy(),
            confidence=detection.confidence,
            first_seen=timestamp,
            last_seen=timestamp,
            trajectory=[detection.bbox.copy()],
        )
        self.tracks[self.next_id] = track
        self.next_id += 1

    def _update_track(self, track: TrackState, detection: Detection, timestamp: float):
        """Update an existing track with a new detection."""
        # Compute velocity before updating bbox
        old_center = track.center
        new_bbox = detection.bbox
        new_center = (new_bbox[:2] + new_bbox[2:]) / 2
        velocity = new_center - old_center
        track.velocities.append(velocity)

        track.bbox = new_bbox.copy()
        track.confidence = detection.confidence
        track.last_seen = timestamp
        track.hits += 1
        track.time_since_update = 0
        track.age += 1
        track.trajectory.append(new_bbox.copy())

    def get_trajectory_summary(self, track_id: int) -> Optional[dict]:
        """Get summary statistics for a completed track."""
        # Look in both active and recently removed tracks
        track = self.tracks.get(track_id)
        if track is None:
            return None

        trajectory = np.array(track.trajectory) if track.trajectory else np.array([])
        velocities = np.array(track.velocities) if track.velocities else np.array([])

        summary = {
            "track_id": track.track_id,
            "class_name": track.class_name,
            "first_seen": track.first_seen,
            "last_seen": track.last_seen,
            "age_frames": track.age,
            "hits": track.hits,
            "trajectory_length": len(track.trajectory),
        }

        if len(trajectory) > 0:
            centers = (trajectory[:, :2] + trajectory[:, 2:]) / 2
            summary["start_position"] = centers[0].tolist()
            summary["end_position"] = centers[-1].tolist()

            # Path length
            diffs = np.diff(centers, axis=0)
            summary["path_length"] = float(np.sum(np.linalg.norm(diffs, axis=1)))

            # Displacement
            summary["displacement"] = float(np.linalg.norm(centers[-1] - centers[0]))

        if len(velocities) > 0:
            speeds = np.linalg.norm(velocities, axis=1)
            summary["avg_speed"] = float(np.mean(speeds))
            summary["max_speed"] = float(np.max(speeds))
            summary["avg_velocity"] = np.mean(velocities, axis=0).tolist()

        return summary

    def reset(self):
        """Reset the tracker state."""
        self.tracks.clear()
        self.next_id = 0
        self.frame_count = 0
