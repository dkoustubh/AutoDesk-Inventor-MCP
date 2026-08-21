"""
Unit Tests for Sprocket and Planetary Gear Mathematical Modules
"""
import pytest
from app.pipeline.math_sprocket import compute_sprocket_geometry, generate_sprocket_2d_points, CHAIN_STANDARDS
from app.pipeline.math_gear import compute_involute_gear_geometry, compute_planetary_gear_set

def test_sprocket_math_08b():
    std = CHAIN_STANDARDS["08B"]
    geom = compute_sprocket_geometry(pitch=std["pitch"], roller_diameter=std["roller_diameter"], teeth=14)
    
    assert geom.teeth == 14
    assert geom.pitch_diameter > geom.root_diameter
    assert geom.outside_diameter > geom.pitch_diameter
    
    pts = generate_sprocket_2d_points(pitch=std["pitch"], roller_diameter=std["roller_diameter"], teeth=14)
    assert len(pts) > 50

def test_planetary_gear_kinematics():
    # Module 1.5, Sun = 12 teeth, Planet = 18 teeth -> Ring = 12 + 2*18 = 48 teeth
    p_set = compute_planetary_gear_set(module=1.5, sun_teeth=12, planet_teeth=18, planet_count=3)
    
    assert p_set["sun"].teeth == 12
    assert p_set["planet"].teeth == 18
    assert p_set["ring"].teeth == 48
    assert p_set["gear_ratio"] == 1.0 + (48 / 12)  # 5:1 ratio
    assert len(p_set["planet_positions"]) == 3
