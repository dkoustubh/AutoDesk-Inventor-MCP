"""
OmniCAD Sprocket Geometry & Mathematical Tooth Profile Generator
Implements ISO 606 / ANSI B29.1 roller chain sprocket boundary curves and seating geometry.
"""
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

@dataclass(frozen=True)
class SprocketGeometry:
    pitch: float
    roller_diameter: float
    teeth: int
    clearance: float
    pitch_diameter: float
    outside_diameter: float
    root_diameter: float
    seat_radius: float

CHAIN_STANDARDS: Dict[str, Dict[str, float]] = {
    "06B": {"pitch": 9.525, "roller_diameter": 6.35, "width": 5.72},
    "08B": {"pitch": 12.70, "roller_diameter": 8.51, "width": 7.75},
    "10B": {"pitch": 15.875, "roller_diameter": 10.16, "width": 9.65},
    "12B": {"pitch": 19.05, "roller_diameter": 12.07, "width": 11.68},
    "ANSI_35": {"pitch": 9.525, "roller_diameter": 5.08, "width": 4.77},
    "ANSI_40": {"pitch": 12.70, "roller_diameter": 7.92, "width": 7.85},
    "ANSI_50": {"pitch": 15.875, "roller_diameter": 10.16, "width": 9.40},
    "ANSI_60": {"pitch": 19.05, "roller_diameter": 11.91, "width": 12.57},
}

def compute_sprocket_geometry(
    pitch: float,
    roller_diameter: float,
    teeth: int,
    clearance: float = 0.10,
) -> SprocketGeometry:
    pitch_diameter = pitch / math.sin(math.pi / teeth)
    outside_diameter = pitch_diameter + 1.25 * pitch - roller_diameter
    root_diameter = pitch_diameter - roller_diameter
    seat_radius = roller_diameter / 2.0 + clearance
    return SprocketGeometry(
        pitch=pitch,
        roller_diameter=roller_diameter,
        teeth=teeth,
        clearance=clearance,
        pitch_diameter=pitch_diameter,
        outside_diameter=outside_diameter,
        root_diameter=root_diameter,
        seat_radius=seat_radius,
    )

def generate_sprocket_2d_points(
    pitch: float,
    roller_diameter: float,
    teeth: int,
    clearance: float = 0.10,
    root_arc_samples: int = 5,
    crest_arc_samples: int = 3,
) -> List[Tuple[float, float]]:
    geom = compute_sprocket_geometry(pitch, roller_diameter, teeth, clearance)
    root_r = geom.root_diameter / 2.0
    od_r = geom.outside_diameter / 2.0
    half_tooth = math.pi / geom.teeth

    sin_ratio = geom.seat_radius / root_r
    if sin_ratio >= math.sin(half_tooth):
        sin_ratio = math.sin(half_tooth) * 0.95
        
    root_half_angle = float(math.asin(sin_ratio))
    crest_half_angle = half_tooth - root_half_angle

    points: List[Tuple[float, float]] = []
    for i in range(geom.teeth):
        seat_center = i * 2.0 * half_tooth
        crest_center = seat_center + half_tooth

        # Root arc samples
        for s in range(root_arc_samples):
            frac = s / max(root_arc_samples - 1, 1)
            a = -root_half_angle + frac * (2.0 * root_half_angle)
            ang = seat_center + a
            points.append((round(root_r * math.cos(ang), 4), round(root_r * math.sin(ang), 4)))

        # Crest arc samples
        for s in range(crest_arc_samples):
            frac = s / max(crest_arc_samples - 1, 1)
            a = -crest_half_angle + frac * (2.0 * crest_half_angle)
            ang = crest_center + a
            points.append((round(od_r * math.cos(ang), 4), round(od_r * math.sin(ang), 4)))

    return points
