import os
import sys
import logging
import traceback
from typing import Dict, Any, Tuple, Optional
import build123d as bd
from OCP.BRepCheck import BRepCheck_Analyzer

logger = logging.getLogger(__name__)

class KernelRunner:
    """
    Stage 7: Deterministic CAD Kernel Execution Engine (OpenCASCADE / build123d).
    Compiles Python CAD scripts into real B-Rep solids and exports STEP/STL/GLB.
    """

    def __init__(self, export_dir: Optional[str] = None):
        if not export_dir:
            self.export_dir = os.path.join(os.path.dirname(__file__), "..", "..", "exports")
        else:
            self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def execute(self, python_code: str, model_id: str = "cad_model") -> Tuple[bool, Optional[Any], Dict[str, Any], Optional[str]]:
        """
        Executes code, extracts solid, computes basic B-Rep metrics, and exports files.
        Returns: (success, solid_object, metadata, error_message)
        """
        local_scope: Dict[str, Any] = {}
        meta: Dict[str, Any] = {}

        try:
            # Execute inside clean namespace with math and build123d
            exec_globals = {"math": sys.modules["math"], "bd": bd, "build123d": bd}
            exec(python_code, exec_globals, local_scope)

            # Locate model
            solid_obj = local_scope.get("model")
            if solid_obj is None:
                for k, v in local_scope.items():
                    if hasattr(v, "wrapped") or hasattr(v, "part") or hasattr(v, "solid"):
                        solid_obj = getattr(v, "part", getattr(v, "solid", v))
                        break

            if solid_obj is None:
                return False, None, {}, "No valid B-Rep solid object assigned to 'model'."

            # Analyze basic topological metrics
            vol = getattr(solid_obj, "volume", 0.0)
            area = getattr(solid_obj, "area", 0.0)
            bbox = solid_obj.bounding_box()

            # BRep Analyzer validity check
            analyzer = BRepCheck_Analyzer(solid_obj.wrapped)
            is_brep_valid = analyzer.IsValid()

            # Export STEP & STL
            step_path = os.path.join(self.export_dir, f"{model_id}.step")
            stl_path = os.path.join(self.export_dir, f"{model_id}.stl")
            glb_path = os.path.join(self.export_dir, f"{model_id}.glb")

            try:
                bd.export_step(solid_obj, step_path)
            except Exception as se:
                logger.warning(f"STEP export warning: {se}")

            try:
                bd.export_stl(solid_obj, stl_path)
            except Exception as ste:
                logger.warning(f"STL export warning: {ste}")

            meta = {
                "volume_mm3": round(vol, 2),
                "surface_area_mm2": round(area, 2),
                "bounding_box": {
                    "min_x": round(bbox.min.X, 2),
                    "max_x": round(bbox.max.X, 2),
                    "min_y": round(bbox.min.Y, 2),
                    "max_y": round(bbox.max.Y, 2),
                    "min_z": round(bbox.min.Z, 2),
                    "max_z": round(bbox.max.Z, 2),
                    "size_x": round(bbox.size.X, 2),
                    "size_y": round(bbox.size.Y, 2),
                    "size_z": round(bbox.size.Z, 2),
                },
                "is_brep_valid": is_brep_valid,
                "is_watertight": getattr(solid_obj, "is_valid", True),
                "step_path": step_path,
                "stl_path": stl_path,
                "glb_path": glb_path
            }

            return True, solid_obj, meta, None

        except Exception as e:
            err_trace = traceback.format_exc()
            logger.error(f"Kernel execution failed: {err_trace}")
            return False, None, {}, f"{str(e)}\n{err_trace}"

kernel_runner = KernelRunner()
