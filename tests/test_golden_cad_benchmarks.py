"""
Automated Golden CAD Test Runner for OmniCAD
Loads all golden benchmark JSON definitions from tests/golden_cad/ and runs geometric verification.
"""
import os
import json
import glob
import pytest
from app.pipeline.engine import engineering_pipeline
from app.pipeline.schemas import PipelineResult

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden_cad")
benchmark_files = sorted(glob.glob(os.path.join(GOLDEN_DIR, "*.json")))

def load_benchmarks():
    benchmarks = []
    for f in benchmark_files:
        with open(f, "r", encoding="utf-8") as fp:
            benchmarks.append(json.load(fp))
    return benchmarks

@pytest.mark.parametrize("benchmark", load_benchmarks(), ids=lambda b: b["test_id"])
def test_golden_cad_benchmark(benchmark):
    prompt = benchmark["prompt"]
    criteria = benchmark["validation_criteria"]
    
    result: PipelineResult = engineering_pipeline.run(prompt, model_id=f"test_{benchmark['test_id'].lower()}")
    
    # 1. Pipeline execution status
    assert result.success is True, f"Pipeline failed on {benchmark['name']}: {result.validation_report.errors}"
    
    # 2. Solid & Watertight integrity
    if criteria.get("must_be_single_solid", True):
        assert result.validation_report.is_solid is True, "Model is not a valid solid"
    if criteria.get("must_be_watertight", True):
        assert result.validation_report.is_watertight is True, "Model is not watertight"
        
    # 3. Volume verification if expected
    if "expected_volume_mm3" in criteria:
        expected_vol = criteria["expected_volume_mm3"]
        actual_vol = result.validation_report.volume_mm3
        tol_pct = criteria.get("volume_tolerance_pct", 1.0)
        tol_val = expected_vol * (tol_pct / 100.0)
        assert abs(actual_vol - expected_vol) <= tol_val, \
            f"Volume mismatch: expected {expected_vol} mm3 +- {tol_pct}%, got {actual_vol} mm3"
            
    # 4. Mandatory checklist criteria
    if "checklist" in criteria:
        for check_name, expected_val in criteria["checklist"].items():
            actual_val = result.validation_report.checklist.get(check_name)
            assert actual_val == expected_val, f"Checklist item '{check_name}' failed for {benchmark['name']}"
            
    # 5. STEP Export verification
    assert result.step_file_path != "", "STEP export path missing"
    assert os.path.exists(result.step_file_path), f"STEP file was not created at {result.step_file_path}"
