import os
import json
import logging
from typing import Dict, Any, Optional
from app.pipeline.schemas import (
    RequirementSpec,
    FeaturePlan,
    ConstraintReport,
    GeometricValidationResult,
    VisualValidationResult,
    RepairPlan,
    PipelineResult
)
from app.pipeline.requirement_analyzer import requirement_analyzer
from app.pipeline.math_solver import math_solver
from app.pipeline.feature_planner import feature_planner
from app.pipeline.cad_generator import cad_generator
from app.pipeline.kernel_runner import kernel_runner
from app.pipeline.geometric_validator import geometric_validator
from app.pipeline.visual_validator import visual_validator
from app.pipeline.repair_engine import repair_engine

logger = logging.getLogger(__name__)

class EngineeringCADPipeline:
    """
    Master 10-Stage Engineering Reasoning & Validation Pipeline Coordinator.
    Enforces contract-driven execution from natural language to verified B-Rep CAD solids.
    """

    def __init__(self, max_repair_iterations: int = 3):
        self.max_repair_iterations = max_repair_iterations

    def run(self, prompt: str, model_id: str = "cad_model", context: Optional[Dict[str, Any]] = None) -> PipelineResult:
        logger.info(f"[Pipeline] Starting 10-stage CAD reasoning for: '{prompt}'")

        # -------------------------------------------------------------
        # STAGE 1 & 2: REQUIREMENT ANALYZER & COMPLETENESS CHECK
        # -------------------------------------------------------------
        req_spec: RequirementSpec = requirement_analyzer.analyze(prompt, context=context)
        logger.info(f"[Pipeline Stage 1-2] Requirements extracted: {len(req_spec.features)} features, Complete={req_spec.is_complete}")

        # -------------------------------------------------------------
        # STAGE 3: ENGINEERING SANITY & MATH SOLVER
        # -------------------------------------------------------------
        constraint_report, calculated_math = math_solver.evaluate_constraints(req_spec)
        logger.info(f"[Pipeline Stage 3] Constraints checked: Valid={constraint_report.valid}")

        if not constraint_report.valid:
            logger.warning(f"[Pipeline Stage 3] Constraint warnings: {[c.message for c in constraint_report.checks if not c.passed]}")

        # -------------------------------------------------------------
        # STAGE 4 & 5: DESIGN & FEATURE PLANNER
        # -------------------------------------------------------------
        plan: FeaturePlan = feature_planner.plan(req_spec, calculated_math)
        logger.info(f"[Pipeline Stage 4-5] Construction plan generated: {len(plan.operations)} operations, Named Params={list(plan.named_parameters.keys())}")

        iteration = 1
        final_solid = None
        final_meta = {}
        val_result = None
        vis_result = None
        python_code = ""

        # -------------------------------------------------------------
        # STAGE 6 - 10: GENERATE -> KERNEL -> VALIDATE -> REPAIR LOOP
        # -------------------------------------------------------------
        while iteration <= self.max_repair_iterations:
            logger.info(f"[Pipeline Loop] Iteration {iteration}/{self.max_repair_iterations}")

            # STAGE 6: CAD Code Generation
            python_code = cad_generator.generate_code(plan)

            # STAGE 7: Deterministic CAD Kernel Execution
            success, solid_obj, meta, err = kernel_runner.execute(python_code, model_id=model_id)

            if not success or solid_obj is None:
                logger.error(f"[Pipeline Stage 7] Kernel execution failed on iteration {iteration}: {err}")
                iteration += 1
                continue

            final_solid = solid_obj
            final_meta = meta

            # STAGE 8: Geometric Validation
            val_result = geometric_validator.validate(solid_obj, req_spec, meta)
            logger.info(f"[Pipeline Stage 8] Geometric Validation: Valid={val_result.is_valid}, Checklist={val_result.checklist}")

            # STAGE 9: Visual Validation
            vis_result = visual_validator.validate(solid_obj, model_id=model_id)

            # STAGE 10: Closed-Loop Repair Check
            if val_result.is_valid:
                logger.info(f"[Pipeline Stage 10] Geometry 100% verified on iteration {iteration}!")
                break
            else:
                logger.warning(f"[Pipeline Stage 10] Validation failed. Diagnosing errors: {val_result.errors}")
                repair_plan: RepairPlan = repair_engine.diagnose_and_repair(
                    req_spec, plan, val_result, iteration=iteration
                )
                if not repair_plan.needs_repair:
                    break
                plan = repair_engine.apply_repair_to_plan(plan, repair_plan)
                iteration += 1

        is_overall_success = (val_result is not None and val_result.is_valid)

        return PipelineResult(
            success=is_overall_success,
            part_type=req_spec.part_type,
            prompt=prompt,
            requirements=req_spec,
            feature_plan=plan,
            constraint_report=constraint_report,
            validation_report=val_result or GeometricValidationResult(
                is_valid=False, is_solid=False, is_watertight=False,
                volume_mm3=0.0, surface_area_mm2=0.0
            ),
            visual_report=vis_result,
            iterations_used=iteration,
            step_path=final_meta.get("step_path"),
            stl_path=final_meta.get("stl_path"),
            glb_path=final_meta.get("glb_path"),
            python_code=python_code,
            named_parameters=plan.named_parameters,
            message="CAD generation and geometric validation succeeded." if is_overall_success else "Validation failed after repair attempts."
        )

engineering_pipeline = EngineeringCADPipeline()
