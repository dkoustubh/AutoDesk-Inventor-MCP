"""
Build123d & OpenCascade Engine Service
Allows Gemma and the AI Gateway to generate, execute, and export complex 3D CAD geometries (STEP, STL, GLB) using pure Python build123d scripts.
"""

import os
import sys
import logging
import tempfile
import traceback
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Build123dService:
    def __init__(self):
        self.export_dir = os.path.join(os.path.dirname(__file__), "..", "..", "exports")
        os.makedirs(self.export_dir, exist_ok=True)

    def execute_cad_script(self, python_code: str, output_name: str = "cad_model") -> Dict[str, Any]:
        """
        Executes a build123d Python script in a controlled namespace and exports to .STEP and .STL.
        """
        step_path = os.path.join(self.export_dir, f"{output_name}.step")
        stl_path = os.path.join(self.export_dir, f"{output_name}.stl")

        # Global execution context
        local_scope: Dict[str, Any] = {}
        
        try:
            # Inject standard build123d imports
            preamble = "from build123d import *\n"
            full_code = preamble + python_code

            exec(full_code, {}, local_scope)

            # Look for Part, Compound, or Solid in scope
            result_obj = None
            for var_name, var_val in local_scope.items():
                if hasattr(var_val, "wrapped") or hasattr(var_val, "part") or hasattr(var_val, "solid"):
                    result_obj = getattr(var_val, "part", getattr(var_val, "solid", var_val))
                    break

            if result_obj is not None:
                export_func = local_scope.get("export_step")
                export_stl_func = local_scope.get("export_stl")
                if export_func:
                    export_func(result_obj, step_path)
                if export_stl_func:
                    export_stl_func(result_obj, stl_path)

                return {
                    "success": True,
                    "step_path": step_path,
                    "stl_path": stl_path,
                    "message": f"Successfully generated CAD solid using OpenCascade & build123d ({output_name}.step)"
                }
            else:
                return {
                    "success": True,
                    "step_path": step_path,
                    "message": "Script executed successfully."
                }

        except Exception as e:
            err_msg = traceback.format_exc()
            logger.error(f"build123d execution error: {err_msg}")
            return {
                "success": False,
                "error": str(e),
                "traceback": err_msg
            }

build123d_service = Build123dService()
