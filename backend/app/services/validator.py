import logging
from typing import Tuple, Optional, Dict, Any
from app.schemas import (
    StructuredIntent,
    CreateBoxParameters,
    CreateCylinderParameters,
    CreateSphereParameters,
    CreateConeParameters,
    CreateTorusParameters,
    CreateHoleParameters,
    CreateCompoundParameters,
    CreateTriangleParameters,
    CreateSprocketParameters,
    CreateBoxWithHoleParameters,
    CreateFlangeParameters,
    CreateHexBoltParameters,
    CreatePipeParameters,
    CreateIBeamParameters,
    CreatePulleyParameters,
    CreateRhombusParameters,
    CreatePyramidParameters,
    CreatePolygonParameters,
    CreateValveBodyParameters,
    CreateBracketParameters,
    CreatePRBConveyorParameters,
    CreateTurntableParameters
)

logger = logging.getLogger(__name__)

SUPPORTED_TOOLS = {
    "inventor.create_box": CreateBoxParameters,
    "inventor.create_cylinder": CreateCylinderParameters,
    "inventor.create_sphere": CreateSphereParameters,
    "inventor.create_cone": CreateConeParameters,
    "inventor.create_torus": CreateTorusParameters,
    "inventor.create_hole": CreateHoleParameters,
    "inventor.create_compound": CreateCompoundParameters,
    "inventor.create_triangle_prism": CreateTriangleParameters,
    "inventor.create_sprocket": CreateSprocketParameters,
    "inventor.create_box_with_hole": CreateBoxWithHoleParameters,
    "inventor.create_flange": CreateFlangeParameters,
    "inventor.create_bolt": CreateHexBoltParameters,
    "inventor.create_pipe": CreatePipeParameters,
    "inventor.create_ibeam": CreateIBeamParameters,
    "inventor.create_pulley": CreatePulleyParameters,
    "inventor.create_rhombus": CreateRhombusParameters,
    "inventor.create_pyramid": CreatePyramidParameters,
    "inventor.create_polygon": CreatePolygonParameters,
    "inventor.create_valve_body": CreateValveBodyParameters,
    "inventor.create_bracket": CreateBracketParameters,
    "inventor.create_prb_conveyor": CreatePRBConveyorParameters,
    "inventor.create_turntable": CreateTurntableParameters
}

class ValidationService:
    def validate_intent(self, intent: StructuredIntent) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validates structured intent against programmatic schemas.
        Returns: (is_valid, error_message, normalized_parameters)
        """
        tool = intent.tool.strip().lower()
        clean_params = dict(intent.parameters)

        # Auto-normalize zero or missing values into standard engineering proportions
        if tool == "inventor.create_sprocket":
            od = float(clean_params.get("outer_diameter_mm") or 50.0)
            if float(clean_params.get("bore_diameter_mm") or 0) <= 0:
                clean_params["bore_diameter_mm"] = round(od * 0.25, 2)
            if float(clean_params.get("thickness_mm") or 0) <= 0:
                clean_params["thickness_mm"] = round(od * 0.15, 2)
            if int(clean_params.get("teeth_count") or 0) <= 0:
                clean_params["teeth_count"] = 16

        elif tool == "inventor.create_cone":
            # Normalize radius / diameter
            r = clean_params.get("base_radius_mm") or clean_params.get("radius_mm")
            d = clean_params.get("base_diameter_mm") or clean_params.get("diameter_mm")
            if not r and d:
                clean_params["base_radius_mm"] = float(d) / 2.0
            elif not r:
                clean_params["base_radius_mm"] = 10.0
            if "top_radius_mm" not in clean_params:
                clean_params["top_radius_mm"] = 0.0
            if float(clean_params.get("height_mm") or 0) <= 0:
                clean_params["height_mm"] = float(clean_params["base_radius_mm"]) * 2.0

        elif tool == "inventor.create_rhombus":
            # Major and minor diagonals
            dx = clean_params.get("diagonal_x_mm")
            dy = clean_params.get("diagonal_y_mm")
            side = clean_params.get("side_mm")
            if not dx and side:
                clean_params["diagonal_x_mm"] = float(side) * 1.5
                clean_params["diagonal_y_mm"] = float(side) * 1.0
            elif not dx:
                clean_params["diagonal_x_mm"] = 20.0
                clean_params["diagonal_y_mm"] = 15.0
            if float(clean_params.get("thickness_mm") or clean_params.get("height_mm") or 0) <= 0:
                clean_params["thickness_mm"] = 10.0

        elif tool == "inventor.create_pyramid":
            if float(clean_params.get("base_length_mm") or 0) <= 0:
                clean_params["base_length_mm"] = 20.0
            if float(clean_params.get("base_width_mm") or 0) <= 0:
                clean_params["base_width_mm"] = float(clean_params["base_length_mm"])
            if float(clean_params.get("height_mm") or 0) <= 0:
                clean_params["height_mm"] = 30.0

        elif tool == "inventor.create_polygon":
            r = clean_params.get("radius_mm") or (float(clean_params.get("diameter_mm", 40.0)) / 2.0)
            clean_params["radius_mm"] = float(r or 20.0)
            if int(clean_params.get("sides") or 0) < 3:
                clean_params["sides"] = 6
            if float(clean_params.get("thickness_mm") or clean_params.get("height_mm") or 0) <= 0:
                clean_params["thickness_mm"] = 10.0

        if tool == "inventor.create_box_with_hole":
            l_val = float(clean_params.get("length_mm") or 10.0)
            if float(clean_params.get("hole_diameter_mm") or 0) <= 0:
                clean_params["hole_diameter_mm"] = round(l_val * 0.2, 2)

        if tool == "inventor.create_triangle_prism":
            b_val = float(clean_params.get("base_mm") or 20.0)
            if float(clean_params.get("thickness_mm") or 0) <= 0:
                clean_params["thickness_mm"] = round(b_val * 0.5, 2)

        param_schema = SUPPORTED_TOOLS[tool]
        try:
            validated_params = param_schema(**clean_params)
            return True, None, validated_params.model_dump()
        except Exception as e:
            return False, f"Parameter validation failed for {tool}: {str(e)}", None

    def validate_workstation(self, ip_address: str) -> bool:
        """
        Validates workstation IP format and LAN authorization.
        """
        if not ip_address:
            return False
        parts = ip_address.strip().split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

validator_service = ValidationService()
