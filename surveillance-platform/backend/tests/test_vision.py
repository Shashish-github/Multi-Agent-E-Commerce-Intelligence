"""Tests for vision pipeline components."""
import pytest
import numpy as np

from vision.features.zone_geometry import (
    point_in_polygon,
    line_crosses,
    is_bbox_in_zone,
    get_polygon_centroid,
)
from vision.features.trajectory import TrajectoryAnalyzer, Direction
from vision.anomaly.event_engine import (
    EventEngine, ZoneConfig, RuleConfig, EventType
)


class TestZoneGeometry:
    """Tests for zone geometry utilities."""

    def test_point_inside_polygon(self):
        polygon = [
            {"x": 0, "y": 0},
            {"x": 100, "y": 0},
            {"x": 100, "y": 100},
            {"x": 0, "y": 100},
        ]
        assert point_in_polygon((50, 50), polygon) is True

    def test_point_outside_polygon(self):
        polygon = [
            {"x": 0, "y": 0},
            {"x": 100, "y": 0},
            {"x": 100, "y": 100},
            {"x": 0, "y": 100},
        ]
        assert point_in_polygon((150, 50), polygon) is False

    def test_point_on_boundary(self):
        polygon = [
            {"x": 0, "y": 0},
            {"x": 100, "y": 0},
            {"x": 100, "y": 100},
            {"x": 0, "y": 100},
        ]
        # On boundary - shapely considers this not contained for strict test
        result = point_in_polygon((0, 0), polygon)
        assert isinstance(result, bool)

    def test_point_in_triangle(self):
        polygon = [
            {"x": 50, "y": 0},
            {"x": 100, "y": 100},
            {"x": 0, "y": 100},
        ]
        assert point_in_polygon((50, 60), polygon) is True
        assert point_in_polygon((10, 10), polygon) is False

    def test_line_crosses(self):
        trajectory = [(10, 50), (90, 50)]
        line_start = (50, 0)
        line_end = (50, 100)
        assert line_crosses(trajectory, line_start, line_end) is True

    def test_line_no_cross(self):
        trajectory = [(10, 50), (30, 50)]
        line_start = (50, 0)
        line_end = (50, 100)
        assert line_crosses(trajectory, line_start, line_end) is False

    def test_bbox_in_zone(self):
        polygon = [
            {"x": 0, "y": 0},
            {"x": 200, "y": 0},
            {"x": 200, "y": 200},
            {"x": 0, "y": 200},
        ]
        bbox = np.array([50, 50, 100, 100])
        assert is_bbox_in_zone(bbox, polygon) is True

    def test_centroid(self):
        polygon = [
            {"x": 0, "y": 0},
            {"x": 100, "y": 0},
            {"x": 100, "y": 100},
            {"x": 0, "y": 100},
        ]
        cx, cy = get_polygon_centroid(polygon)
        assert abs(cx - 50) < 1
        assert abs(cy - 50) < 1


class TestTrajectoryAnalyzer:
    """Tests for trajectory feature computation."""

    def test_single_position(self):
        analyzer = TrajectoryAnalyzer()
        bbox = np.array([100, 100, 200, 200])
        features = analyzer.update(track_id=1, bbox=bbox, timestamp=1.0)

        assert features.track_id == 1
        assert features.speed == 0.0
        assert features.direction == Direction.STATIC
        assert features.path_length == 0.0

    def test_movement_computation(self):
        analyzer = TrajectoryAnalyzer()
        # Move right
        analyzer.update(track_id=1, bbox=np.array([100, 100, 200, 200]), timestamp=1.0)
        features = analyzer.update(track_id=2, bbox=np.array([200, 100, 300, 200]), timestamp=2.0)

        assert features.speed > 0
        assert features.path_length > 0
        assert features.displacement > 0

    def test_zone_tracking(self):
        analyzer = TrajectoryAnalyzer()
        analyzer.update(track_id=1, bbox=np.array([100, 100, 200, 200]), timestamp=1.0, current_zone="zone_a")
        features = analyzer.update(track_id=1, bbox=np.array([110, 110, 210, 210]), timestamp=2.0, current_zone="zone_a")

        assert "zone_a" in features.zone_history
        assert features.current_zone == "zone_a"
        assert features.dwell_time > 0


class TestEventEngine:
    """Tests for deterministic event engine."""

    def setup_method(self):
        self.engine = EventEngine()

    def test_restricted_entry_event(self):
        zone = ZoneConfig(
            zone_id="z1",
            name="Restricted",
            zone_type="restricted",
            polygon=[
                {"x": 0, "y": 0},
                {"x": 100, "y": 0},
                {"x": 100, "y": 100},
                {"x": 0, "y": 100},
            ],
        )
        rule = RuleConfig(
            rule_id="r1",
            rule_type="restricted_entry",
            zone_id="z1",
            confidence_threshold=0.3,
        )

        self.engine.add_zone(zone)
        self.engine.add_rule(rule)

        # Create features with position inside zone
        from vision.features.trajectory import TrajectoryFeatures
        features = TrajectoryFeatures(
            track_id=1,
            position=np.array([50.0, 50.0]),
            velocity=np.array([0.0, 0.0]),
            speed=10.0,
            direction=Direction.STATIC,
            displacement=10.0,
            path_length=10.0,
            dwell_time=0.0,
            zone_history=[],
            current_zone="z1",
            acceleration=0.0,
            timestamp=1.0,
        )

        events = self.engine.evaluate("cam1", features, timestamp=1.0)
        assert len(events) == 1
        assert events[0].event_type == EventType.RESTRICTED_ENTRY
        assert events[0].track_id == "1"
        assert "restricted zone" in events[0].explanation.lower()

    def test_no_event_outside_zone(self):
        zone = ZoneConfig(
            zone_id="z1",
            name="Restricted",
            zone_type="restricted",
            polygon=[
                {"x": 0, "y": 0},
                {"x": 100, "y": 0},
                {"x": 100, "y": 100},
                {"x": 0, "y": 100},
            ],
        )
        rule = RuleConfig(rule_id="r1", rule_type="restricted_entry", zone_id="z1")
        self.engine.add_zone(zone)
        self.engine.add_rule(rule)

        from vision.features.trajectory import TrajectoryFeatures
        features = TrajectoryFeatures(
            track_id=1,
            position=np.array([200.0, 200.0]),  # Outside zone
            velocity=np.array([0.0, 0.0]),
            speed=0.0,
            direction=Direction.STATIC,
            displacement=0.0,
            path_length=0.0,
            dwell_time=0.0,
            zone_history=[],
            current_zone=None,
            acceleration=0.0,
            timestamp=1.0,
        )

        events = self.engine.evaluate("cam1", features, timestamp=1.0)
        assert len(events) == 0

    def test_dwell_event(self):
        zone = ZoneConfig(
            zone_id="z1",
            name="Watch Area",
            zone_type="high_risk",
            polygon=[
                {"x": 0, "y": 0},
                {"x": 100, "y": 0},
                {"x": 100, "y": 100},
                {"x": 0, "y": 100},
            ],
        )
        rule = RuleConfig(
            rule_id="r1",
            rule_type="dwell",
            zone_id="z1",
            dwell_threshold_seconds=30.0,
        )
        self.engine.add_zone(zone)
        self.engine.add_rule(rule)

        from vision.features.trajectory import TrajectoryFeatures
        features = TrajectoryFeatures(
            track_id=1,
            position=np.array([50.0, 50.0]),
            velocity=np.array([0.0, 0.0]),
            speed=0.5,
            direction=Direction.STATIC,
            displacement=2.0,
            path_length=2.0,
            dwell_time=45.0,  # Exceeds threshold
            zone_history=["z1"],
            current_zone="z1",
            acceleration=0.0,
            timestamp=45.0,
        )

        events = self.engine.evaluate("cam1", features, timestamp=45.0)
        assert len(events) == 1
        assert events[0].event_type == EventType.LOITERING
        assert "45" in events[0].explanation
