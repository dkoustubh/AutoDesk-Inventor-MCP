import uuid
import logging
from fastapi import APIRouter, HTTPException, Query
from app.schemas import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.services.validator import validator_service
from app.services.job_service import job_service
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

    # 2. Multi-turn AI Reasoning with Active Session Context Memory
    active_context = ACTIVE_SESSION_PARTS.get(session_id)
    logger.info(f"Parsing intent for prompt: '{request.prompt}' (Session Context: {active_context})")
    intent = await llm_service.parse_intent(request.prompt, context=active_context)

    # 3. Strict Validation & Normalization Layer
    is_valid, error_msg, validated_params = validator_service.validate_intent(intent)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error_msg)

    # 4. Update Session Memory
    ACTIVE_SESSION_PARTS[session_id] = {
        "tool": intent.tool,
        "parameters": validated_params
    }

    # 5. Job Creation & Dispatch
    job = await job_service.create_and_dispatch_job(
        prompt=request.prompt,
        tool_name=intent.tool,
        parameters=validated_params,
        workstation_ip=workstation_ip,
        session_id=session_id,
        user_name=request.user_name or settings.DEFAULT_USER_NAME
    )

    return ChatResponse(
        success=True,
        job_id=job["job_id"],
        tool=intent.tool,
        parameters=validated_params,
        workstation_ip=workstation_ip,
        status=job["status"],
        message=intent.explanation or "Intent validated and job dispatched."
    )
