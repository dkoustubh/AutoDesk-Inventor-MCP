import os
import sys
import pytest

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.pipeline.engine import engineering_pipeline

BENCHMARKS = [
    {
        "id": "BASIC_CUBE_001",
        "prompt": "Create a 30 mm cube",
        "expected_part": "prismatic_block",
        "min_vol": 26000.0,
        "max_vol": 28000.0
    },
    {
        "id": "BASIC_PLATE_002",
        "prompt": "Create a 100 x 60 x 20 mm plate",
        "expected_part": "prismatic_block",
        "min_vol": 115000.0,
        "max_vol": 125000.0
    },
    {
        "id": "FEATURE_DRILLED_BLOCK_003",
        "prompt": "Create a 40 x 40 x 20 mm block with a 10 mm through hole",
        "expected_part": "prismatic_block",
        "min_vol": 29000.0,
        "max_vol": 32000.0
    },
    {
        "id": "GOLDEN_FLANGE_001",
        "prompt": "Create a pipe flange with 150 mm outer diameter and 20 mm flange thickness. Add a 65 mm center through-bore, a raised face of 95 mm diameter extruded 4 mm, and a circular pattern of 6 bolt holes of 14 mm diameter on a 120 mm pitch circle diameter (PCD).",
        "expected_part": "pipe_flange",
        "min_vol": 280000.0,
        "max_vol": 290000.0
    }
]

@pytest.mark.parametrize("bench", BENCHMARKS, ids=[b["id"] for b in BENCHMARKS])
def test_cad_benchmark_item(bench):
    res = engineering_pipeline.run(bench["prompt"], model_id=f"bench_{bench['id']}")

    assert res.success is True, f"Benchmark {bench['id']} failed: {res.message}"
    assert res.part_type == bench["expected_part"]
    assert res.validation_report.is_valid is True
    assert res.validation_report.is_watertight is True
    
    vol = res.validation_report.volume_mm3
    assert bench["min_vol"] <= vol <= bench["max_vol"], (
        f"Volume out of expected range for {bench['id']}: got {vol}, expected [{bench['min_vol']}, {bench['max_vol']}]"
    )
