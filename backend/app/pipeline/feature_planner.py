import logging
from typing import Dict, Any, List, Tuple
from app.pipeline.schemas import RequirementSpec, FeaturePlan, OperationStep

logger = logging.getLogger(__name__)

class FeaturePlanner:
    """
    Stage 4 & 5: Design & Feature Planner.
    Converts RequirementSpec into an explicit, inspectable sequence of parametric CAD operations.
    """

    def plan(self, spec: RequirementSpec, calculated_math: Dict[str, Any]) -> FeaturePlan:
        operations: List[OperationStep] = []
        named_params: Dict[str, float] = {}

        if spec.part_type == "pipe_flange":
            # Extract parameters
            od = 150.0
            thick = 20.0
            bore = 65.0
            has_rf = any(f.id == "raised_face" for f in spec.features)
            rf_dia = 95.0 if has_rf else 0.0
            rf_h = 4.0 if has_rf else 0.0
            bolt_count = 6
            bolt_dia = 14.0
            pcd = 120.0

            for f in spec.features:
                if f.id == "base_flange":
                    od = float(f.parameters.get("outer_diameter_mm", od))
                    thick = float(f.parameters.get("thickness_mm", thick))
                elif f.id == "center_bore":
                    bore = float(f.parameters.get("diameter_mm", bore))
                elif f.id == "raised_face":
                    rf_dia = float(f.parameters.get("diameter_mm", rf_dia))
                    rf_h = float(f.parameters.get("height_mm", rf_h))
                elif f.id == "bolt_pattern":
                    bolt_count = int(f.parameters.get("count", bolt_count))
                    bolt_dia = float(f.parameters.get("hole_diameter_mm", bolt_dia))
                    pcd = float(f.parameters.get("pcd_mm", pcd))

            named_params = {
                "FLANGE_OD": od,
                "FLANGE_THICKNESS": thick,
                "BORE_DIAMETER": bore,
                "RAISED_FACE_DIAMETER": rf_dia,
                "RAISED_FACE_HEIGHT": rf_h,
                "BOLT_HOLE_DIAMETER": bolt_dia,
                "BOLT_PATTERN_COUNT": float(bolt_count),
                "BOLT_PCD": pcd
            }

            # Step 1: Base Flange Solid Disk
            operations.append(OperationStep(
                step_number=1,
                operation_type="create_base_cylinder",
                feature_id="base_flange",
                parameters={"diameter_mm": od, "height_mm": thick},
                description=f"Extrude base circular flange disk of Ø{od}mm x {thick}mm thickness along +Z."
            ))

            # Step 2: Raised Face Boss
            if any(f.id == "raised_face" for f in spec.features):
                operations.append(OperationStep(
                    step_number=2,
                    operation_type="create_raised_face",
                    feature_id="raised_face",
                    parameters={"diameter_mm": rf_dia, "height_mm": rf_h, "offset_z_mm": thick},
                    description=f"Extrude concentric raised face boss of Ø{rf_dia}mm x {rf_h}mm from Z={thick}mm plane."
                ))

            # Step 3: Center Through-Bore
            total_h = thick + (rf_h if any(f.id == "raised_face" for f in spec.features) else 0.0)
            operations.append(OperationStep(
                step_number=3,
                operation_type="cut_through_bore",
                feature_id="center_bore",
                parameters={"diameter_mm": bore, "depth_mm": total_h, "through": True},
                description=f"Subtractive boolean cut center fluid bore of Ø{bore}mm through full height ({total_h}mm)."
            ))

            # Step 4: Circular Bolt Hole Pattern
            if any(f.id == "bolt_pattern" for f in spec.features):
                operations.append(OperationStep(
                    step_number=4,
                    operation_type="cut_circular_bolt_pattern",
                    feature_id="bolt_pattern",
                    parameters={
                        "count": bolt_count,
                        "hole_diameter_mm": bolt_dia,
                        "pcd_mm": pcd,
                        "depth_mm": thick,
                        "through": True,
                        "coordinates": calculated_math.get("bolt_coordinates", [])
                    },
                    description=f"Subtractive circular drill pattern of {bolt_count}x Ø{bolt_dia}mm holes on Ø{pcd}mm PCD."
                ))

        elif spec.part_type == "prismatic_block":
            l = 30.0
            w = 30.0
            h = 30.0
            for f in spec.features:
                if f.id == "base_box":
                    l = float(f.parameters.get("length_mm", l))
                    w = float(f.parameters.get("width_mm", w))
                    h = float(f.parameters.get("height_mm", h))

            named_params = {"BLOCK_LENGTH": l, "BLOCK_WIDTH": w, "BLOCK_HEIGHT": h}

            operations.append(OperationStep(
                step_number=1,
                operation_type="create_box",
                feature_id="base_box",
                parameters={"length_mm": l, "width_mm": w, "height_mm": h},
                description=f"Create rectangular solid block {l}x{w}x{h}mm."
            ))

            if any(f.id == "subtractive_hole" for f in spec.features):
                hole_dia = 5.0
                for f in spec.features:
                    if f.id == "subtractive_hole":
                        hole_dia = float(f.parameters.get("diameter_mm", hole_dia))
                named_params["HOLE_DIAMETER"] = hole_dia
                operations.append(OperationStep(
                    step_number=2,
                    operation_type="cut_through_bore",
                    feature_id="subtractive_hole",
                    parameters={"diameter_mm": hole_dia, "depth_mm": h, "through": True},
                    description=f"Cut centered through-hole of Ø{hole_dia}mm."
                ))

        elif spec.part_type == "u_bracket":
            width = 100.0
            height = 60.0
            thick = 5.0
            depth = 50.0
            for f in spec.features:
                if f.id == "u_channel_body":
                    width = float(f.parameters.get("width_mm", width))
                    height = float(f.parameters.get("height_mm", height))
                    thick = float(f.parameters.get("thickness_mm", thick))
                    depth = float(f.parameters.get("depth_mm", depth))

            named_params = {
                "CHANNEL_WIDTH": width,
                "CHANNEL_HEIGHT": height,
                "WALL_THICKNESS": thick,
                "EXTRUSION_DEPTH": depth
            }

            operations.append(OperationStep(
                step_number=1,
                operation_type="create_u_channel",
                feature_id="u_channel_body",
                parameters={
                    "width_mm": width,
                    "height_mm": height,
                    "thickness_mm": thick,
                    "depth_mm": depth
                },
                description=f"Construct 3D U-bracket ({width}mm wide x {height}mm high x {depth}mm depth x {thick}mm wall thickness)."
            ))

        elif spec.part_type == "l_bracket":
            l = 80.0
            w = 60.0
            h = 60.0
            t = 8.0
            rib_t = 8.0
            for f in spec.features:
                if f.id == "l_bracket_body":
                    l = float(f.parameters.get("length_mm", l))
                    w = float(f.parameters.get("width_mm", w))
                    h = float(f.parameters.get("height_mm", h))
                    t = float(f.parameters.get("thickness_mm", t))
                    rib_t = float(f.parameters.get("rib_thickness_mm", rib_t))

            named_params = {
                "BASE_LENGTH": l,
                "BRACKET_WIDTH": w,
                "WALL_HEIGHT": h,
                "WALL_THICKNESS": t,
                "RIB_THICKNESS": rib_t
            }

            operations.append(OperationStep(
                step_number=1,
                operation_type="create_l_bracket",
                feature_id="l_bracket_body",
                parameters={"length_mm": l, "width_mm": w, "height_mm": h, "thickness_mm": t, "rib_thickness_mm": rib_t},
                description=f"Construct L-bracket ({l}x{w}x{h}mm, {t}mm thickness, {rib_t}mm rib)."
            ))

        else:
            # Generic fallback
            named_params = {"LENGTH": 50.0, "WIDTH": 50.0, "HEIGHT": 20.0}
            operations.append(OperationStep(
                step_number=1,
                operation_type="create_box",
                feature_id="base_box",
                parameters={"length_mm": 50.0, "width_mm": 50.0, "height_mm": 20.0},
                description="Construct baseline parametric solid."
            ))

        return FeaturePlan(
            part_type=spec.part_type,
            operations=operations,
            named_parameters=named_params
        )

feature_planner = FeaturePlanner()
