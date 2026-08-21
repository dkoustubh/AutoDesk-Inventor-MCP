from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal

class DimensionalRequirement(BaseModel):
    name: str
    value: float
    unit: str = "mm"
    tolerance: Optional[float] = 0.5
    description: Optional[str] = None

class FeatureRequirement(BaseModel):
    id: str
    feature_type: Literal[
        "base_cylinder", "base_box", "through_bore", "blind_hole",
        "raised_face", "circular_hole_pattern", "linear_hole_pattern",
        "boss", "fillet", "chamfer", "keyway", "flange", "rib", "custom"
    ]
    parameters: Dict[str, Any]
    dependencies: List[str] = []

class RequirementSpec(BaseModel):
    part_type: str = "custom_part"
    units: str = "mm"
    is_complete: bool = True
    missing_fields: List[str] = []
    dimensions: Dict[str, float] = {}
    features: List[FeatureRequirement] = []
    raw_prompt: str = ""
    notes: Optional[str] = None

class OperationStep(BaseModel):
    step_number: int
    operation_type: str
    feature_id: str
    parameters: Dict[str, Any]
    description: str

class FeaturePlan(BaseModel):
    part_type: str
    operations: List[OperationStep] = []
    named_parameters: Dict[str, float] = {}

class ConstraintCheck(BaseModel):
    name: str
    passed: bool
    expected: str
    actual: str
    message: str

class ConstraintReport(BaseModel):
    valid: bool
    checks: List[ConstraintCheck] = []
    warnings: List[str] = []

class CylinderFeatureMeasurement(BaseModel):
    diameter_mm: float
    radius_mm: float
    axis: List[float] = [0.0, 0.0, 1.0]
    center: List[float] = [0.0, 0.0, 0.0]
    height_mm: Optional[float] = None
    is_hole: bool = False

class HolePatternMeasurement(BaseModel):
    hole_count: int
    hole_diameter_mm: float
    pcd_mm: float
    hole_centers: List[List[float]] = []
    is_through: bool = True

class GeometricValidationResult(BaseModel):
    is_valid: bool
    is_solid: bool
    is_watertight: bool
    volume_mm3: float
    surface_area_mm2: float
    bounding_box: Dict[str, float] = {}
    solid_count: int = 1
    face_count: int = 0
    edge_count: int = 0
    measured_cylinders: List[CylinderFeatureMeasurement] = []
    detected_bolt_pattern: Optional[HolePatternMeasurement] = None
    detected_bore_diameter_mm: Optional[float] = None
    detected_outer_diameter_mm: Optional[float] = None
    detected_raised_face_diameter_mm: Optional[float] = None
    detected_raised_face_height_mm: Optional[float] = None
    detected_base_thickness_mm: Optional[float] = None
    checklist: Dict[str, bool] = {}
    errors: List[str] = []
    warnings: List[str] = []

class VisualValidationResult(BaseModel):
    passed: bool
    contact_sheet_path: Optional[str] = None
    views_generated: List[str] = []
    visual_score: float = 1.0
    detected_features: List[str] = []
    notes: str = "Visual inspection completed."

class RepairPatch(BaseModel):
    target_feature_id: str
    issue_diagnosed: str
    action: Literal["adjust_dimension", "reorder_operation", "fix_cut_depth", "recompute_pcd", "replace_feature"]
    corrected_parameters: Dict[str, Any]

class RepairPlan(BaseModel):
    needs_repair: bool
    iteration: int = 0
    patches: List[RepairPatch] = []
    diagnosis: str = ""

class PipelineResult(BaseModel):
    success: bool
    part_type: str
    prompt: str
    requirements: RequirementSpec
    feature_plan: FeaturePlan
    constraint_report: ConstraintReport
    validation_report: GeometricValidationResult
    visual_report: Optional[VisualValidationResult] = None
    repair_plan: Optional[RepairPlan] = None
    iterations_used: int = 1
    step_path: Optional[str] = None
    stl_path: Optional[str] = None
    glb_path: Optional[str] = None
    python_code: str = ""
    named_parameters: Dict[str, float] = {}
    message: str = ""
