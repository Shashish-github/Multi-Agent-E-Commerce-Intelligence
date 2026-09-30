"""Zone geometry utilities for spatial event detection."""
import numpy as np
from typing import List, Tuple, Optional
from shapely.geometry import Polygon, Point, LineString


def point_in_polygon(point: Tuple[float, float], polygon: List[dict]) -> bool:
    """
    Check if a point is inside a polygon.

    Args:
        point: (x, y) coordinates
        polygon: List of {"x": float, "y": float} vertices

    Returns:
        True if point is inside polygon
    """
    if len(polygon) < 3:
        return False

    coords = [(v["x"], v["y"]) for v in polygon]
    poly = Polygon(coords)
    return poly.contains(Point(point[0], point[1]))


def line_crosses(
    trajectory: List[Tuple[float, float]],
    line_start: Tuple[float, float],
    line_end: Tuple[float, float],
) -> bool:
    """
    Check if a trajectory crosses a line segment.

    Args:
        trajectory: List of (x, y) points
        line_start: Start of the crossing line
        line_end: End of the crossing line

    Returns:
        True if trajectory crosses the line
    """
    if len(trajectory) < 2:
        return False

    crossing_line = LineString([line_start, line_end])

    for i in range(len(trajectory) - 1):
        segment = LineString([trajectory[i], trajectory[i + 1]])
        if segment.intersects(crossing_line):
            return True

    return False


def line_crossing_direction(
    trajectory: List[Tuple[float, float]],
    line_start: Tuple[float, float],
    line_end: Tuple[float, float],
) -> Optional[str]:
    """
    Determine the direction a trajectory crosses a line.

    Returns:
        "forward", "backward", or None if no crossing
    """
    if len(trajectory) < 2:
        return None

    crossing_line = LineString([line_start, line_end])

    # Compute line normal for direction
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]
    normal = np.array([-dy, dx])
    normal = normal / (np.linalg.norm(normal) + 1e-6)

    for i in range(len(trajectory) - 1):
        segment = LineString([trajectory[i], trajectory[i + 1]])
        if segment.intersects(crossing_line):
            # Direction is based on movement at crossing point
            movement = np.array(trajectory[i + 1]) - np.array(trajectory[i])
            dot = np.dot(movement, normal)
            return "forward" if dot > 0 else "backward"

    return None


def compute_zone_overlap(
    polygon_a: List[dict],
    polygon_b: List[dict],
) -> float:
    """
    Compute overlap ratio between two zones (0.0 to 1.0).
    """
    coords_a = [(v["x"], v["y"]) for v in polygon_a]
    coords_b = [(v["x"], v["y"]) for v in polygon_b]

    poly_a = Polygon(coords_a)
    poly_b = Polygon(coords_b)

    if not poly_a.is_valid or not poly_b.is_valid:
        return 0.0

    intersection = poly_a.intersection(poly_b)
    area_a = poly_a.area

    if area_a == 0:
        return 0.0

    return intersection.area / area_a


def get_polygon_centroid(polygon: List[dict]) -> Tuple[float, float]:
    """Get the centroid of a polygon."""
    coords = [(v["x"], v["y"]) for v in polygon]
    poly = Polygon(coords)
    return (poly.centroid.x, poly.centroid.y)


def is_bbox_in_zone(
    bbox: np.ndarray,
    polygon: List[dict],
    threshold: float = 0.5,
) -> bool:
    """
    Check if a bounding box is sufficiently inside a zone.

    Args:
        bbox: [x1, y1, x2, y2]
        polygon: Zone polygon vertices
        threshold: Minimum fraction of bbox center that must be in zone

    Returns:
        True if bbox center is inside the polygon
    """
    center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    return point_in_polygon(center, polygon)


def estimate_zone_density(
    bboxes: List[np.ndarray],
    polygon: List[dict],
    zone_area: Optional[float] = None,
) -> float:
    """
    Estimate object density inside a zone.

    Args:
        bboxes: List of bounding boxes [x1, y1, x2, y2]
        polygon: Zone polygon vertices
        zone_area: Optional pre-computed zone area in pixels

    Returns:
        Density as objects per unit area
    """
    if not bboxes:
        return 0.0

    # Count objects inside zone
    inside_count = 0
    for bbox in bboxes:
        if is_bbox_in_zone(bbox, polygon):
            inside_count += 1

    # Compute zone area
    if zone_area is None:
        coords = [(v["x"], v["y"]) for v in polygon]
        zone_area = Polygon(coords).area

    if zone_area == 0:
        return 0.0

    return inside_count / zone_area
