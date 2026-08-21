import os
import sys
import pytest

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.pipeline.engine import engineering_pipeline
from app.pipeline.requirement_analyzer import requirement_analyzer
from app.pipeline.math_solver import math_solver
from app.pipeline.feature_planner import feature_planner
from app.pipeline.cad_generator import cad_generator
from app.pipeline.kernel_runner import kernel_runner
from app.pipeline.geometric_validator import geometric_validator

GOLDEN_FLANGE_PROMPT = (
    "Create a pipe flange with 150 mm outer diameter and 20 mm flange thickness. "
    "Add a 65 mm center through-bore, a raised face of 95 mm diameter extruded 4 mm, "
    "and a circular pattern of 6 bolt holes of 14 mm diameter on a 120 mm pitch circle diameter (PCD)."
)

def test_stage_1_requirement_analyzer():
    spec = requirement_analyzer.analyze(GOLDEN_FLANGE_PROMPT)
    assert spec.part_type == "pipe_flange"
    assert spec.is_complete is True

    dims = spec.dimensions
    assert dims.get("outer_diameter") == 150.0
    assert dims.get("thickness") == 20.0
    assert dims.get("bore_diameter") == 65.0
    assert dims.get("raised_face_diameter") == 95.0
    assert dims.get("raised_face_height") == 4.0
    assert dims.get("bolt_count") == 6
    assert dims.get("bolt_hole_diameter") == 14.0
    assert dims.get("bolt_pcd") == 120.0

def test_stage_3_engineering_math_solver():
    spec = requirement_analyzer.analyze(GOLDEN_FLANGE_PROMPT)
    report, math_data = math_solver.evaluate_constraints(spec)
    
    assert report.valid is True
    assert len(math_data.get("bolt_coordinates", [])) == 6
    # Theoretical volume ~ 283,670 mm3
    theo_vol = math_data.get("theoretical_volume_mm3", 0.0)
    assert 280000.0 < theo_vol < 290000.0

def test_stage_4_6_code_generation():
    spec = requirement_analyzer.analyze(GOLDEN_FLANGE_PROMPT)
    report, math_data = math_solver.evaluate_constraints(spec)
    plan = feature_planner.plan(spec, math_data)
    code = cad_generator.generate_code(plan)

    assert "FLANGE_OD = 150.00" in code
    assert "FLANGE_THICKNESS = 20.00" in code
    assert "BORE_DIAMETER = 65.00" in code
    assert "RAISED_FACE_DIAMETER = 95.00" in code
    assert "RAISED_FACE_HEIGHT = 4.00" in code
    assert "BOLT_PATTERN_COUNT = 6" in code
    assert "BOLT_PCD = 120.00" in code

def test_stage_7_8_kernel_and_geometric_validation():
    spec = requirement_analyzer.analyze(GOLDEN_FLANGE_PROMPT)
    report, math_data = math_solver.evaluate_constraints(spec)
    plan = feature_planner.plan(spec, math_data)
    code = cad_generator.generate_code(plan)

    success, solid, meta, err = kernel_runner.execute(code, model_id="golden_flange_test")
    assert success is True
    assert solid is not None
    assert err is None

    # Check volume within 1% of analytical expectation (283,670 mm³)
    vol = meta.get("volume_mm3", 0.0)
    assert 280000.0 < vol < 290000.0

    # Geometric Validation
    val_res = geometric_validator.validate(solid, spec, meta)
    assert val_res.is_valid is True
    assert val_res.is_watertight is True
    assert val_res.checklist.get("outer_diameter_150mm") is True
    assert val_res.checklist.get("center_bore_65mm") is True
    assert val_res.checklist.get("raised_face_95mm") is True
    assert val_res.checklist.get("bolt_pattern_6_holes_on_pcd") is True

def test_golden_pipe_flange_full_pipeline_run():
    result = engineering_pipeline.run(GOLDEN_FLANGE_PROMPT, model_id="golden_flange_e2e")

    assert result.success is True
    assert result.part_type == "pipe_flange"
    assert result.validation_report.is_valid is True
    assert result.validation_report.is_watertight is True
    assert 280000.0 < result.validation_report.volume_mm3 < 290000.0
    assert result.step_path is not None
    assert os.path.exists(result.step_path)
