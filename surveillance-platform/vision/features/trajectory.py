"""Trajectory feature computation for temporal behavior analysis."""
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

import numpy as np


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STATIC = "static"


@dataclass
class TrajectoryFeatures:
    """Computed features for a single track trajectory."""
    track_id: int
    position: np.ndarray  # current center [x, y]
    velocity: np.ndarray  # [vx, vy]
    speed: float  # magnitude of velocity
    direction: Direction
    displacement: float  # total displacement from start
    path_length: float  # total distance traveled
    dwell_time: float  # time spent in current zone (seconds)
    zone_history: List[str]  # list of zones visited
    current_zone: Optional[str]
    acceleration: float  # acceleration proxy
    timestamp: float

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "position": self.position.tolist(),
            "velocity": self.velocity.tolist(),
            "speed": round(self.speed, 3),
            "direction": self.direction.value,
            "displacement": round(self.displacement, 3),
            "path_length": round(self.path_length, 3),
            "dwell_time": round(self.dwell_time, 3),
            "zone_history": self.zone_history,
            "current_zone": self.current_zone,
            "acceleration": round(self.acceleration, 3),
            "timestamp": self.timestamp,
        }


class TrajectoryAnalyzer:
    """
    Maintains per-track trajectory state and computes temporal features.
    """

    def __init__(self):
        self._positions: Dict[int, List[np.ndarray]] = {}
        self._timestamps: Dict[int, List[float]] = {}
        self._zones: Dict[int, List[str]] = {}
        self._velocities: Dict[int, List[np.ndarray]] = {}
        self._zone_entry_times: Dict[int, Dict[str, float]] = {}

    def update(
        self,
        track_id: int,
        bbox: np.ndarray,
        timestamp: float,
        current_zone: Optional[str] = None,
    ) -> TrajectoryFeatures:
        """
        Update trajectory for a track and compute features.

        Args:
            track_id: Unique track ID
            bbox: Bounding box [x1, y1, x2, y2]
            timestamp: Current timestamp (seconds)
            current_zone: Zone name the track is currently in (if any)

        Returns:
            Computed trajectory features
        """
        center = (bbox[:2] + bbox[2:]) / 2

        # Initialize if new track
        if track_id not in self._positions:
            self._positions[track_id] = []
            self._timestamps[track_id] = []
            self._zones[track_id] = []
            self._velocities[track_id] = []
            self._zone_entry_times[track_id] = {}

        self._positions[track_id].append(center)
        self._timestamps[track_id].append(timestamp)

        # Compute velocity
        velocity = np.array([0.0, 0.0])
        speed = 0.0
        acceleration = 0.0

        positions = self._positions[track_id]
        timestamps = self._timestamps[track_id]

        if len(positions) >= 2:
            dt = timestamps[-1] - timestamps[-2]
            if dt > 0:
                velocity = (positions[-1] - positions[-2]) / dt
                speed = float(np.linalg.norm(velocity))

                self._velocities[track_id].append(velocity)

                # Acceleration proxy
                if len(self._velocities[track_id]) >= 2:
                    vels = self._velocities[track_id]
                    dv = vels[-1] - vels[-2]
                    acceleration = float(np.linalg.norm(dv) / max(dt, 1e-6))

        # Direction
        direction = self._compute_direction(velocity)

        # Path length
        path_length = 0.0
        if len(positions) >= 2:
            diffs = np.diff(np.array(positions), axis=0)
            path_length = float(np.sum(np.linalg.norm(diffs, axis=1)))

        # Displacement
        displacement = float(np.linalg.norm(positions[-1] - positions[0]))

        # Zone tracking
        if current_zone:
            if current_zone not in self._zones[track_id]:
                self._zones[track_id].append(current_zone)
                self._zone_entry_times[track_id][current_zone] = timestamp
        elif current_zone is None and self._zones[track_id]:
            # Leaving zone
            pass

        # Dwell time in current zone
        dwell_time = 0.0
        if current_zone and current_zone in self._zone_entry_times.get(track_id, {}):
            dwell_time = timestamp - self._zone_entry_times[track_id][current_zone]

        return TrajectoryFeatures(
            track_id=track_id,
            position=center,
            velocity=velocity,
            speed=speed,
            direction=direction,
            displacement=displacement,
            path_length=path_length,
            dwell_time=dwell_time,
            zone_history=list(self._zones.get(track_id, [])),
            current_zone=current_zone,
            acceleration=acceleration,
            timestamp=timestamp,
        )

    def _compute_direction(self, velocity: np.ndarray) -> Direction:
        """Map velocity vector to a cardinal direction."""
        if np.linalg.norm(velocity) < 1.0:  # near-static threshold
            return Direction.STATIC

        vx, vy = velocity
        if abs(vx) > abs(vy):
            return Direction.RIGHT if vx > 0 else Direction.LEFT
        else:
            return Direction.DOWN if vy > 0 else Direction.UP

    def get_track_positions(self, track_id: int) -> Optional[np.ndarray]:
        """Get all recorded positions for a track."""
        positions = self._positions.get(track_id)
        if positions:
            return np.array(positions)
        return None

    def get_dwell_time(self, track_id: int, zone_name: str, current_time: float) -> float:
        """Get total dwell time for a track in a specific zone."""
        entry_times = self._zone_entry_times.get(track_id, {})
        if zone_name in entry_times:
            return current_time - entry_times[zone_name]
        return 0.0

    def get_zone_transitions(self, track_id: int) -> List[Dict]:
        """Get zone transition history for a track."""
        zones = self._zones.get(track_id, [])
        transitions = []
        for i in range(1, len(zones)):
            if zones[i] != zones[i - 1]:
                transitions.append({
                    "from": zones[i - 1],
                    "to": zones[i],
                    "index": i,
                })
        return transitions

    def remove_track(self, track_id: int):
        """Clean up state for a removed track."""
        self._positions.pop(track_id, None)
        self._timestamps.pop(track_id, None)
        self._zones.pop(track_id, None)
        self._velocities.pop(track_id, None)
        self._zone_entry_times.pop(track_id, None)

    def clear(self):
        """Clear all state."""
        self._positions.clear()
        self._timestamps.clear()
        self._zones.clear()
        self._velocities.clear()
        self._zone_entry_times.clear()
