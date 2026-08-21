"""
OmniCAD Involute Gear Geometry & Profile Calculator
Implements standard AGMA / DIN / ISO involute spur gear, sun/planet gears, and internal ring gear math.
"""
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

@dataclass(frozen=True)
class InvoluteGearGeometry:
    module: float
    teeth: int
    pressure_angle_deg: float
    pitch_radius: float
    base_radius: float
    tip_radius: float
    root_radius: float
    addendum: float
    dedendum: float
    internal: bool = False

def compute_involute_gear_geometry(
    module: float,
    teeth: int,
    pressure_angle_deg: float = 20.0,
    addendum_factor: float = 1.0,
    dedendum_factor: float = 1.25,
    internal: bool = False
) -> InvoluteGearGeometry:
    alpha = math.radians(pressure_angle_deg)
    rp = module * teeth / 2.0
    rb = rp * math.cos(alpha)
    
    if internal:
        r_tip = rp - addendum_factor * module
        r_root = rp + dedendum_factor * module
    else:
        r_tip = rp + addendum_factor * module
        r_root = rp - dedendum_factor * module
        
    return InvoluteGearGeometry(
        module=module,
        teeth=teeth,
        pressure_angle_deg=pressure_angle_deg,
        pitch_radius=rp,
        base_radius=rb,
        tip_radius=r_tip,
        root_radius=r_root,
        addendum=addendum_factor * module,
        dedendum=dedendum_factor * module,
        internal=internal
    )

def compute_planetary_gear_set(
    module: float,
    sun_teeth: int,
    planet_teeth: int,
    planet_count: int = 3
) -> Dict[str, Any]:
    """
    Computes an exact kinematic planetary gear set (Sun, Planets, Ring, Carrier).
    Constraint: Ring Teeth = Sun Teeth + 2 * Planet Teeth.
    """
    ring_teeth = sun_teeth + 2 * planet_teeth
    sun_geom = compute_involute_gear_geometry(module, sun_teeth)
    planet_geom = compute_involute_gear_geometry(module, planet_teeth)
    ring_geom = compute_involute_gear_geometry(module, ring_teeth, internal=True)
    
    center_distance = (sun_geom.pitch_radius + planet_geom.pitch_radius)
    ratio_ring_fixed = 1.0 + (ring_teeth / sun_teeth)
    
    planet_positions = []
    for i in range(planet_count):
        ang = i * (2.0 * math.pi / planet_count)
        planet_positions.append((
            round(center_distance * math.cos(ang), 3),
            round(center_distance * math.sin(ang), 3)
        ))
        
    return {
        "module": module,
        "sun": sun_geom,
        "planet": planet_geom,
        "ring": ring_geom,
        "planet_count": planet_count,
        "center_distance_mm": center_distance,
        "gear_ratio": ratio_ring_fixed,
        "planet_positions": planet_positions
    }
