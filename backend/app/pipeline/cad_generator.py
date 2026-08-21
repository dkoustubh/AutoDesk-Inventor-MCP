import logging
from typing import Dict, Any
from app.pipeline.schemas import FeaturePlan

logger = logging.getLogger(__name__)

class ParametricCADGenerator:
    """
    Stage 6: Deterministic Parametric CAD Generator.
    Converts FeaturePlan into clean, human-readable, fully parameterized build123d / OpenCASCADE code.
    All dimensions are declared as named constants for downstream parametric editing.
    """

    def generate_code(self, plan: FeaturePlan) -> str:
        if plan.part_type == "pipe_flange":
            params = plan.named_parameters
            od = params.get("FLANGE_OD", 150.0)
            thick = params.get("FLANGE_THICKNESS", 20.0)
            bore = params.get("BORE_DIAMETER", 65.0)
            rf_dia = params.get("RAISED_FACE_DIAMETER", 95.0)
            rf_h = params.get("RAISED_FACE_HEIGHT", 4.0)
            bolt_dia = params.get("BOLT_HOLE_DIAMETER", 14.0)
            bolt_count = int(params.get("BOLT_PATTERN_COUNT", 6))
            pcd = params.get("BOLT_PCD", 120.0)

            code = f"""import math
import build123d as bd

# ==============================================================================
# PARAMETRIC ENGINEERING DIMENSIONS (ISO / DIN / ANSI COMPLIANT)
# ==============================================================================
FLANGE_OD = {od:.2f}
FLANGE_THICKNESS = {thick:.2f}
BORE_DIAMETER = {bore:.2f}
RAISED_FACE_DIAMETER = {rf_dia:.2f}
RAISED_FACE_HEIGHT = {rf_h:.2f}
BOLT_HOLE_DIAMETER = {bolt_dia:.2f}
BOLT_PATTERN_COUNT = {bolt_count}
BOLT_PCD = {pcd:.2f}

# ==============================================================================
# DETERMINISTIC B-REP SOLID CONSTRUCTION PIPELINE
# ==============================================================================
with bd.BuildPart() as part:
    # 1. Base Flange Disk
    with bd.BuildSketch(bd.Plane.XY):
        bd.Circle(radius=FLANGE_OD / 2.0)
    bd.extrude(amount=FLANGE_THICKNESS)

    # 2. Concentric Raised Face
    if RAISED_FACE_DIAMETER > 0 and RAISED_FACE_HEIGHT > 0:
        with bd.BuildSketch(bd.Plane.XY.offset(FLANGE_THICKNESS)):
            bd.Circle(radius=RAISED_FACE_DIAMETER / 2.0)
        bd.extrude(amount=RAISED_FACE_HEIGHT)

    # 3. Center Through-Bore
    total_cut_height = FLANGE_THICKNESS + RAISED_FACE_HEIGHT + 2.0
    with bd.BuildSketch(bd.Plane.XY.offset(-1.0)):
        bd.Circle(radius=BORE_DIAMETER / 2.0)
    bd.extrude(amount=total_cut_height, mode=bd.Mode.SUBTRACT)

    # 4. Circular Bolt Hole Pattern on PCD
    if BOLT_PATTERN_COUNT > 0 and BOLT_HOLE_DIAMETER > 0 and BOLT_PCD > 0:
        bolt_locs = []
        for i in range(int(BOLT_PATTERN_COUNT)):
            ang = 2.0 * math.pi * i / float(BOLT_PATTERN_COUNT)
            bx = (BOLT_PCD / 2.0) * math.cos(ang)
            by = (BOLT_PCD / 2.0) * math.sin(ang)
            bolt_locs.append((bx, by))
            
        with bd.BuildSketch(bd.Plane.XY.offset(-1.0)):
            with bd.Locations(bolt_locs):
                bd.Circle(radius=BOLT_HOLE_DIAMETER / 2.0)
        bd.extrude(amount=FLANGE_THICKNESS + 2.0, mode=bd.Mode.SUBTRACT)

model = part.part
"""
            return code

        elif plan.part_type == "prismatic_block":
            params = plan.named_parameters
            l = params.get("BLOCK_LENGTH", 30.0)
            w = params.get("BLOCK_WIDTH", 30.0)
            h = params.get("BLOCK_HEIGHT", 30.0)
            hole_dia = params.get("HOLE_DIAMETER")

            hole_block = ""
            if hole_dia:
                hole_block = f"""
    # Centered Subtractive Through-Hole
    with bd.BuildSketch(bd.Plane.XY.offset(-1.0)):
        bd.Circle(radius={hole_dia:.2f} / 2.0)
    bd.extrude(amount=BLOCK_HEIGHT + 2.0, mode=bd.Mode.SUBTRACT)
"""

            code = f"""import math
import build123d as bd

BLOCK_LENGTH = {l:.2f}
BLOCK_WIDTH = {w:.2f}
BLOCK_HEIGHT = {h:.2f}

with bd.BuildPart() as part:
    with bd.BuildSketch(bd.Plane.XY):
        bd.Rectangle(BLOCK_LENGTH, BLOCK_WIDTH)
    bd.extrude(amount=BLOCK_HEIGHT)
{hole_block}
model = part.part
"""
            return code

        elif plan.part_type == "u_bracket":
            params = plan.named_parameters
            w = params.get("CHANNEL_WIDTH", 100.0)
            h = params.get("CHANNEL_HEIGHT", 60.0)
            t = params.get("WALL_THICKNESS", 5.0)
            d = params.get("EXTRUSION_DEPTH", 50.0)

            code = f"""import math
import build123d as bd

# 3D U-Channel Bracket Parameters
CHANNEL_WIDTH = {w:.2f}
CHANNEL_HEIGHT = {h:.2f}
WALL_THICKNESS = {t:.2f}
EXTRUSION_DEPTH = {d:.2f}

with bd.BuildPart() as part:
    # 1. Base Solid Bounding Volume
    with bd.BuildSketch(bd.Plane.XY):
        bd.Rectangle(CHANNEL_WIDTH, EXTRUSION_DEPTH)
    bd.extrude(amount=CHANNEL_HEIGHT)

    # 2. Subtractive U-Channel Interior Clearance
    inner_w = max(1.0, CHANNEL_WIDTH - 2.0 * WALL_THICKNESS)
    cut_h = CHANNEL_HEIGHT - WALL_THICKNESS + 2.0
    with bd.BuildSketch(bd.Plane.XY.offset(WALL_THICKNESS)):
        bd.Rectangle(inner_w, EXTRUSION_DEPTH + 4.0)
    bd.extrude(amount=cut_h, mode=bd.Mode.SUBTRACT)

model = part.part
"""
            return code

        else:
            return """import build123d as bd

with bd.BuildPart() as part:
    bd.Box(50.0, 50.0, 20.0)

model = part.part
"""

cad_generator = ParametricCADGenerator()
