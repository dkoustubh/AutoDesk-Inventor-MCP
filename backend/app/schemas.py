from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime

# --- CAD Parameters & Structured Intent ---

class CreateBoxParameters(BaseModel):
    length_mm: float = Field(..., gt=0, lt=50000, description="Dimension along X axis in mm")
    width_mm: float = Field(..., gt=0, lt=50000, description="Dimension along Y axis in mm")
    height_mm: float = Field(..., gt=0, lt=50000, description="Dimension along Z axis (extrusion) in mm")
    centered: Optional[bool] = Field(True, description="Center geometry on origin")

class CreateCylinderParameters(BaseModel):
    radius_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Radius in mm")
    diameter_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Diameter in mm")
    height_mm: float = Field(..., gt=0, lt=50000, description="Height / length of cylinder in mm")
    centered: Optional[bool] = Field(True, description="Center geometry on origin")

class CreateSphereParameters(BaseModel):
    radius_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Radius in mm")
    diameter_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Diameter in mm")

class CreateConeParameters(BaseModel):
    base_radius_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Base radius in mm")
    base_diameter_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Base diameter in mm")
    radius_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Base radius fallback")
    diameter_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Base diameter fallback")
    top_radius_mm: Optional[float] = Field(0.0, ge=0, lt=50000, description="Top radius in mm (0 for pointed cone)")
    height_mm: float = Field(..., gt=0, lt=50000, description="Height in mm")

class CreateRhombusParameters(BaseModel):
    diagonal_x_mm: Optional[float] = Field(20.0, gt=0, lt=50000, description="Diagonal along X in mm")
    diagonal_y_mm: Optional[float] = Field(15.0, gt=0, lt=50000, description="Diagonal along Y in mm")
    side_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Side length in mm")
    thickness_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Extrusion height/thickness in mm")
    height_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Extrusion height in mm")

class CreatePyramidParameters(BaseModel):
    base_length_mm: float = Field(20.0, gt=0, lt=50000, description="Base length along X in mm")
    base_width_mm: float = Field(20.0, gt=0, lt=50000, description="Base width along Y in mm")
    height_mm: float = Field(30.0, gt=0, lt=50000, description="Apex height in mm")

class CreatePolygonParameters(BaseModel):
    radius_mm: Optional[float] = Field(20.0, gt=0, lt=50000, description="Circumscribed radius in mm")
    diameter_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Circumscribed diameter in mm")
    sides: int = Field(6, ge=3, le=32, description="Number of polygon sides (6 for hexagon, 8 for octagon)")
    thickness_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Extrusion thickness in mm")
    height_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Extrusion height in mm")

class CreateTorusParameters(BaseModel):
    major_radius_mm: float = Field(..., gt=0, lt=50000, description="Major ring radius in mm")
    tube_radius_mm: float = Field(..., gt=0, lt=50000, description="Tube cross-section radius in mm")

class CreateHoleParameters(BaseModel):
    diameter_mm: float = Field(..., gt=0, lt=50000, description="Hole diameter in mm")
    depth_mm: Optional[float] = Field(None, gt=0, lt=50000, description="Hole depth in mm (or through)")
    through_all: Optional[bool] = Field(True, description="Drill through whole solid")

class CreateValveBodyParameters(BaseModel):
    flange_size_mm: Optional[float] = Field(120.0, gt=0, lt=50000, description="Square top and bottom flange size in mm (e.g. 120)")
    flange_thickness_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Thickness of each flange in mm (e.g. 10)")
    body_size_mm: Optional[float] = Field(80.0, gt=0, lt=50000, description="Central column width/length in mm (e.g. 80)")
    height_mm: Optional[float] = Field(90.0, gt=0, lt=50000, description="Total overall height in mm (e.g. 90)")
    bore_diameter_mm: Optional[float] = Field(50.0, gt=0, lt=50000, description="Center through bore hole diameter in mm (e.g. 50)")
    corner_radius_mm: Optional[float] = Field(15.0, ge=0, lt=50000, description="Corner fillet radius in mm (e.g. 15)")

class CreateBracketParameters(BaseModel):
    width_mm: Optional[float] = Field(70.0, gt=0, lt=50000, description="Base plate width in mm")
    length_mm: Optional[float] = Field(80.0, gt=0, lt=50000, description="Base plate length in mm")
    height_mm: Optional[float] = Field(55.0, gt=0, lt=50000, description="Vertical wall height in mm")
    rib_thickness_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Center rib thickness in mm")
    flange_thickness_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Base flange thickness in mm")
    boss_diameter_mm: Optional[float] = Field(30.0, gt=0, lt=50000, description="Top boss diameter in mm")
    bore_diameter_mm: Optional[float] = Field(15.0, gt=0, lt=50000, description="Top bore hole diameter in mm")
    hole_diameter_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Base mounting hole diameter in mm")

class CreateTriangleParameters(BaseModel):
    base_mm: float = Field(20.0, gt=0, lt=50000, description="Triangle base width in mm")
    height_mm: float = Field(30.0, gt=0, lt=50000, description="Triangle vertical height in mm")
    thickness_mm: Optional[float] = Field(10.0, gt=0, lt=50000, description="Extrusion depth in mm")

class CreateSprocketParameters(BaseModel):
    outer_diameter_mm: float = Field(50.0, gt=0, lt=50000, description="Outer tip diameter in mm")
    teeth_count: Optional[int] = Field(12, ge=4, le=120, description="Number of sprocket teeth")
    bore_diameter_mm: Optional[float] = Field(8.0, gt=0, description="Center shaft hole diameter in mm")
    thickness_mm: Optional[float] = Field(6.0, gt=0, lt=50000, description="Sprocket thickness in mm")

class CreateBoxWithHoleParameters(BaseModel):
    length_mm: float = Field(10.0, gt=0, lt=50000, description="Cube/box length in mm")
    width_mm: float = Field(10.0, gt=0, lt=50000, description="Cube/box width in mm")
    height_mm: float = Field(10.0, gt=0, lt=50000, description="Cube/box height in mm")
    hole_diameter_mm: Optional[float] = Field(2.0, gt=0, lt=50000, description="Drill hole diameter in mm")
    hole_direction: Optional[str] = Field("top_to_bottom", description="Drill axis")
    through: Optional[bool] = Field(True, description="Whether hole penetrates completely through")

class CreateCompoundParameters(BaseModel):
    length_mm: float = Field(..., gt=0, lt=50000)
    width_mm: float = Field(..., gt=0, lt=50000)
    height_mm: float = Field(..., gt=0, lt=50000)
    top_feature: Optional[Dict[str, Any]] = None
    features: Optional[List[Dict[str, Any]]] = None
    centered: Optional[bool] = True

class CreateFlangeParameters(BaseModel):
    outer_diameter_mm: float = Field(100.0, gt=0, description="Flange outer diameter in mm")
    inner_bore_mm: Optional[float] = Field(30.0, gt=0, description="Center fluid bore diameter in mm")
    bolt_circle_dia_mm: Optional[float] = Field(75.0, gt=0, description="Pitch circle diameter for bolt holes")
    bolt_count: Optional[int] = Field(4, ge=2, le=32, description="Number of bolt holes")
    bolt_hole_dia_mm: Optional[float] = Field(8.0, gt=0, description="Diameter of bolt holes")
    thickness_mm: Optional[float] = Field(12.0, gt=0, description="Flange flange thickness in mm")

class CreateHexBoltParameters(BaseModel):
    thread_diameter_mm: float = Field(10.0, gt=0, description="Bolt shank thread diameter (e.g. M10 = 10mm)")
    thread_length_mm: float = Field(40.0, gt=0, description="Shaft length in mm")
    hex_width_mm: Optional[float] = Field(16.0, gt=0, description="Hexagonal head width across flats")
    head_height_mm: Optional[float] = Field(7.0, gt=0, description="Hexagonal head thickness in mm")

class CreatePipeParameters(BaseModel):
    outer_diameter_mm: float = Field(50.0, gt=0, description="Pipe outer diameter in mm")
    wall_thickness_mm: Optional[float] = Field(3.0, gt=0, description="Pipe wall thickness in mm")
    length_mm: float = Field(100.0, gt=0, description="Pipe extrusion length in mm")

class CreateIBeamParameters(BaseModel):
    height_mm: float = Field(100.0, gt=0, description="Total beam height in mm")
    flange_width_mm: float = Field(60.0, gt=0, description="Flange width in mm")
    flange_thickness_mm: Optional[float] = Field(8.0, gt=0, description="Flange thickness in mm")
    web_thickness_mm: Optional[float] = Field(5.0, gt=0, description="Central web thickness in mm")
    length_mm: float = Field(200.0, gt=0, description="Beam length along extrusion in mm")

class CreatePulleyParameters(BaseModel):
    outer_diameter_mm: float = Field(80.0, gt=0, description="Pulley outer diameter in mm")
    bore_diameter_mm: Optional[float] = Field(15.0, gt=0, description="Center shaft bore diameter in mm")
    groove_width_mm: Optional[float] = Field(10.0, gt=0, description="Belt groove width in mm")
    thickness_mm: Optional[float] = Field(20.0, gt=0, description="Total pulley thickness in mm")

class CreatePRBConveyorParameters(BaseModel):
    length_mm: Optional[float] = Field(2000.0, gt=0, lt=50000, description="Overall conveyor bed frame length in mm (e.g. 2000mm)")
    width_mm: Optional[float] = Field(450.0, gt=0, lt=50000, description="Overall conveyor bed frame width in mm (e.g. 450mm)")
    height_mm: Optional[float] = Field(350.0, gt=0, lt=50000, description="Support leg elevation height in mm (e.g. 350mm)")
    roller_count: Optional[int] = Field(5, ge=2, le=50, description="Number of transverse roller shafts")
    roller_diameter_mm: Optional[float] = Field(50.0, gt=0, lt=5000, description="Roller tube diameter in mm")
    has_drive_motor: Optional[bool] = Field(True, description="Includes center mounted drive reducer motor unit")
    motor_position: Optional[str] = Field("center", description="Drive unit mount position: center | end")

class CreateTurntableParameters(BaseModel):
    bed_length_mm: Optional[float] = Field(1000.0, gt=0, lt=50000, description="Turntable roller bed length in mm (e.g. 1000mm)")
    bed_width_mm: Optional[float] = Field(1000.0, gt=0, lt=50000, description="Turntable roller bed width in mm (e.g. 1000mm)")
    height_mm: Optional[float] = Field(550.0, gt=0, lt=50000, description="Total elevation height from floor in mm (e.g. 550mm)")
    roller_count: Optional[int] = Field(8, ge=3, le=40, description="Number of parallel conveyor rollers on top carriage")
    roller_diameter_mm: Optional[float] = Field(60.0, gt=0, lt=5000, description="Roller tube diameter in mm")
    rotation_angle_deg: Optional[float] = Field(90.0, description="Rotary slew angle in degrees (90, 180, 360)")
    has_yellow_guard: Optional[bool] = Field(True, description="Includes Safety Warning Yellow drive guard plate")
    has_slewing_motor: Optional[bool] = Field(True, description="Includes undermounted rotary slewing drive gear motor")

class StructuredIntent(BaseModel):
    tool: str = Field(..., description="Target tool name e.g. inventor.create_box, inventor.create_cylinder, inventor.create_sphere, inventor.create_cone, inventor.create_torus")
    shape: Optional[str] = Field("box", description="Shape type e.g. box, cylinder, sphere, cone, torus, hole")
    parameters: Dict[str, Any] = Field(..., description="Tool specific parameters")
    confidence: Optional[float] = 1.0
    explanation: Optional[str] = None

# --- Chat API ---

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="Engineer natural language instruction")
    workstation_ip: Optional[str] = Field("192.168.11.150", description="Target engineer workstation IP")
    user_name: Optional[str] = Field("Koustubh Deodhar", description="Engineer user name")
    application: Optional[str] = Field("Inventor", description="Target CAD application")

class ChatResponse(BaseModel):
    success: bool
    job_id: str
    tool: str
    parameters: Dict[str, Any]
    workstation_ip: str
    status: str
    message: str

# --- Agent Registration & Heartbeat ---

class AgentRegistration(BaseModel):
    agent_id: Optional[str] = None
    workstation_ip: str
    hostname: Optional[str] = None
    application_name: str = "Inventor"
    application_version: Optional[str] = None
    status: str = "READY"

class AgentHeartbeat(BaseModel):
    agent_id: str
    workstation_ip: str
    status: str = "READY"
    current_job_id: Optional[str] = None
    memory_usage_mb: Optional[float] = None

class AgentInfo(BaseModel):
    id: str
    workstation_ip: str
    hostname: Optional[str] = None
    application_name: str
    application_version: Optional[str] = None
    status: str
    is_active: bool
    last_heartbeat: datetime

# --- Job Schemas ---

class JobCreate(BaseModel):
    prompt: str
    tool_name: str
    parameters: Dict[str, Any]
    workstation_ip: str
    user_name: Optional[str] = "Koustubh Deodhar"

class JobExecutionResult(BaseModel):
    job_id: str
    success: bool
    status: str # COMPLETED, FAILED
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    id: str
    prompt: str
    tool_name: str
    parameters: Dict[str, Any]
    workstation_ip: str
    status: str
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# --- WebSocket Messages ---

class WSMessage(BaseModel):
    type: str # step_update, job_status, agent_status, error
    job_id: Optional[str] = None
    step: Optional[str] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
