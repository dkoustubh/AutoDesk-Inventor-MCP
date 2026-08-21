import uuid
import logging
from fastapi import APIRouter, HTTPException, Query
from app.schemas import ChatRequest, ChatResponse
from app.services.validator import validator_service
from app.services.job_service import job_service
from app.pipeline.engine import engineering_pipeline
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat & Intent"])

# Active Part Memory per Session
ACTIVE_SESSION_PARTS: dict = {}

@router.post("", response_model=ChatResponse)
async def process_chat(request: ChatRequest, session_id: str = Query("default")):
    workstation_ip = request.workstation_ip or settings.DEFAULT_WORKSTATION_IP

    # 1. Validate Workstation
    if not validator_service.validate_workstation(workstation_ip):
        raise HTTPException(status_code=400, detail=f"Invalid workstation IP: {workstation_ip}")

    # 2. Multi-turn AI Reasoning through 10-Stage Pipeline
    active_context = ACTIVE_SESSION_PARTS.get(session_id)
    job_uuid = str(uuid.uuid4())[:8]
    model_id = f"cad_{job_uuid}"

    logger.info(f"[Chat API] Executing 10-Stage Engineering CAD Pipeline for: '{request.prompt}'")
    pipeline_res = engineering_pipeline.run(
        prompt=request.prompt,
        model_id=model_id,
        context=active_context
    )

    # Determine tool and parameters for Autodesk agent dispatch
    if pipeline_res.part_type == "pipe_flange":
        tool_name = "inventor.create_flange"
        tool_params = {
            "outer_diameter_mm": pipeline_res.named_parameters.get("FLANGE_OD", 150.0),
            "inner_bore_mm": pipeline_res.named_parameters.get("BORE_DIAMETER", 65.0),
            "thickness_mm": pipeline_res.named_parameters.get("FLANGE_THICKNESS", 20.0),
            "raised_face_diameter_mm": pipeline_res.named_parameters.get("RAISED_FACE_DIAMETER", 95.0),
            "raised_face_height_mm": pipeline_res.named_parameters.get("RAISED_FACE_HEIGHT", 4.0),
            "bolt_circle_dia_mm": pipeline_res.named_parameters.get("BOLT_PCD", 120.0),
            "pcd_mm": pipeline_res.named_parameters.get("BOLT_PCD", 120.0),
            "bolt_count": int(pipeline_res.named_parameters.get("BOLT_PATTERN_COUNT", 6)),
            "bolt_hole_dia_mm": pipeline_res.named_parameters.get("BOLT_HOLE_DIAMETER", 14.0)
        }
    elif pipeline_res.part_type == "prismatic_block":
        if "HOLE_DIAMETER" in pipeline_res.named_parameters:
            tool_name = "inventor.create_box_with_hole"
            tool_params = {
                "length_mm": pipeline_res.named_parameters.get("BLOCK_LENGTH", 30.0),
                "width_mm": pipeline_res.named_parameters.get("BLOCK_WIDTH", 30.0),
                "height_mm": pipeline_res.named_parameters.get("BLOCK_HEIGHT", 30.0),
                "hole_diameter_mm": pipeline_res.named_parameters.get("HOLE_DIAMETER", 5.0),
                "through": True,
                "centered": True
            }
        else:
            tool_name = "inventor.create_box"
            tool_params = {
                "length_mm": pipeline_res.named_parameters.get("BLOCK_LENGTH", 30.0),
                "width_mm": pipeline_res.named_parameters.get("BLOCK_WIDTH", 30.0),
                "height_mm": pipeline_res.named_parameters.get("BLOCK_HEIGHT", 30.0),
                "centered": True
            }
    else:
        tool_name = "inventor.create_box"
        tool_params = {
            "length_mm": 50.0,
            "width_mm": 50.0,
            "height_mm": 20.0,
            "centered": True
        }

    # 3. Update Session Memory
    ACTIVE_SESSION_PARTS[session_id] = {
        "tool": tool_name,
        "parameters": tool_params,
        "named_parameters": pipeline_res.named_parameters
    }

    # 4. Job Creation & Dispatch
    job = await job_service.create_and_dispatch_job(
        prompt=request.prompt,
        tool_name=tool_name,
        parameters=tool_params,
        workstation_ip=workstation_ip,
        session_id=session_id,
        user_name=request.user_name or settings.DEFAULT_USER_NAME
    )

    return ChatResponse(
        success=pipeline_res.success,
        job_id=job["job_id"],
        tool=tool_name,
        parameters=tool_params,
        workstation_ip=workstation_ip,
        status=job["status"],
        message=pipeline_res.message,
        validation_report=pipeline_res.validation_report.model_dump(),
        step_url=f"/exports/{model_id}.step" if pipeline_res.step_path else None,
        stl_url=f"/exports/{model_id}.stl" if pipeline_res.stl_path else None,
        glb_url=f"/exports/{model_id}.glb" if pipeline_res.glb_path else None,
        named_parameters=pipeline_res.named_parameters
    )
