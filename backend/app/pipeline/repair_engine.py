import logging
from typing import Dict, Any, List, Optional
from app.pipeline.schemas import (
    RequirementSpec,
    FeaturePlan,
    GeometricValidationResult,
    RepairPlan,
    RepairPatch
)

logger = logging.getLogger(__name__)

class ClosedLoopRepairEngine:
    """
    Stage 10: Closed-Loop Local Feature Repair Engine.
    Diagnoses exact validation errors and produces minimal, localized feature patches
    without discarding previously validated geometry.
    """

    def diagnose_and_repair(
        self,
        spec: RequirementSpec,
        plan: FeaturePlan,
        val_result: GeometricValidationResult,
        iteration: int = 1
    ) -> RepairPlan:
        patches: List[RepairPatch] = []

        if val_result.is_valid:
            return RepairPlan(needs_repair=False, iteration=iteration, patches=[], diagnosis="All validation checks passed.")

        # Diagnose specific errors
        for error in val_result.errors:
            err_lower = error.lower()

            # 1. Height mismatch
            if "height mismatch" in err_lower or "thickness" in err_lower:
                req_thick = spec.dimensions.get("thickness", 20.0)
                patches.append(RepairPatch(
                    target_feature_id="base_flange",
                    issue_diagnosed="Base flange thickness height did not match specification.",
                    action="adjust_dimension",
                    corrected_parameters={"FLANGE_THICKNESS": req_thick}
                ))

            # 2. Bore mismatch
            elif "bore mismatch" in err_lower or "through_bore" in err_lower:
                req_bore = spec.dimensions.get("bore_diameter", 65.0)
                patches.append(RepairPatch(
                    target_feature_id="center_bore",
                    issue_diagnosed="Center bore cut depth or diameter mismatch.",
                    action="fix_cut_depth",
                    corrected_parameters={"BORE_DIAMETER": req_bore}
                ))

            # 3. Bolt pattern mismatch
            elif "bolt pattern mismatch" in err_lower or "pcd" in err_lower:
                req_pcd = spec.dimensions.get("bolt_pcd", 120.0)
                req_count = int(spec.dimensions.get("bolt_count", 6))
                req_dia = spec.dimensions.get("bolt_hole_diameter", 14.0)
                patches.append(RepairPatch(
                    target_feature_id="bolt_pattern",
                    issue_diagnosed="Bolt pattern count, PCD, or hole diameter error.",
                    action="recompute_pcd",
                    corrected_parameters={
                        "BOLT_PCD": req_pcd,
                        "BOLT_PATTERN_COUNT": float(req_count),
                        "BOLT_HOLE_DIAMETER": req_dia
                    }
                ))

            # 4. Raised face mismatch
            elif "raised face" in err_lower:
                req_rf_dia = spec.dimensions.get("raised_face_diameter", 95.0)
                req_rf_h = spec.dimensions.get("raised_face_height", 4.0)
                patches.append(RepairPatch(
                    target_feature_id="raised_face",
                    issue_diagnosed="Raised face boss dimensions offset mismatch.",
                    action="adjust_dimension",
                    corrected_parameters={
                        "RAISED_FACE_DIAMETER": req_rf_dia,
                        "RAISED_FACE_HEIGHT": req_rf_h
                    }
                ))

        diagnosis = f"Identified {len(patches)} targeted geometric corrections."
        return RepairPlan(
            needs_repair=(len(patches) > 0),
            iteration=iteration,
            patches=patches,
            diagnosis=diagnosis
        )

    def apply_repair_to_plan(self, plan: FeaturePlan, repair_plan: RepairPlan) -> FeaturePlan:
        """
        Applies repair patches directly to the named parameters and operations of the FeaturePlan.
        """
        updated_params = dict(plan.named_parameters)
        for patch in repair_plan.patches:
            for k, v in patch.corrected_parameters.items():
                updated_params[k] = v

        plan.named_parameters = updated_params
        return plan

repair_engine = ClosedLoopRepairEngine()
