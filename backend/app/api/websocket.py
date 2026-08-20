import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.agent_manager import agent_manager
from app.services.job_service import job_service
from app.schemas import AgentRegistration, JobExecutionResult

logger = logging.getLogger(__name__)

def utc_now():
    return datetime.now(timezone.utc)

router = APIRouter(tags=["WebSockets"])

# --- Browser Client WebSocket Endpoint ---

@router.websocket("/ws/{session_id}")
async def browser_websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    agent_manager.register_browser_client(session_id, websocket)
    logger.info(f"Browser WebSocket connected: session_id={session_id}")
    
    # Send initial welcome & connected agent status
    current_agents = [
        {
            "id": a.agent_id,
            "workstation_ip": a.workstation_ip,
            "status": a.status,
            "application": a.application_name
        }
        for a in agent_manager.agents_by_id.values()
    ]
    await websocket.send_json({
        "type": "connection_established",
        "session_id": session_id,
        "agents": current_agents
    })

    try:
        while True:
            data = await websocket.receive_text()
            # Heartbeat or client ping
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": utc_now().isoformat()})
            except Exception:
                pass
    except WebSocketDisconnect:
        agent_manager.unregister_browser_client(session_id, websocket)
        logger.info(f"Browser WebSocket disconnected: session_id={session_id}")

# --- Autodesk Agent WebSocket Endpoint ---

@router.websocket("/ws/agent/{workstation_ip}")
async def agent_websocket_endpoint(websocket: WebSocket, workstation_ip: str):
    await websocket.accept()
    agent_instance = None
    logger.info(f"Autodesk Agent connecting from workstation IP: {workstation_ip}")

    try:
        # 1. Expect Registration Message
        initial_msg = await websocket.receive_json()
        if initial_msg.get("type") == "register":
            reg = AgentRegistration(
                agent_id=initial_msg.get("agent_id"),
                workstation_ip=workstation_ip,
                hostname=initial_msg.get("hostname"),
                application_name=initial_msg.get("application_name", "Inventor"),
                application_version=initial_msg.get("application_version"),
                status="READY"
            )
            agent_instance = await agent_manager.register_agent(websocket, reg)
            await websocket.send_json({
                "type": "registered",
                "status": "READY",
                "message": f"Successfully registered Autodesk Agent for {workstation_ip}"
            })
            
            # Immediately drain any queued jobs waiting for this workstation
            pending_job = await redis_manager.pop_job(workstation_ip)
            if pending_job:
                logger.info(f"Draining queued job {pending_job.get('job_id')} to freshly connected agent {workstation_ip}")
                await agent_manager.dispatch_job_to_agent(workstation_ip, pending_job)
        else:
            await websocket.close(code=1008, reason="First message must be registration")
            return

        # 2. Agent Message Loop (Heartbeats & Job Results)
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get("type")

            if msg_type == "heartbeat":
                if agent_instance:
                    agent_instance.last_heartbeat = utc_now()
                await websocket.send_json({"type": "heartbeat_ack", "timestamp": utc_now().isoformat()})

            elif msg_type == "job_result":
                logger.info(f"Received job result from agent on {workstation_ip}: {msg}")
                result = JobExecutionResult(
                    job_id=msg.get("job_id"),
                    success=msg.get("success", False),
                    status=msg.get("status", "COMPLETED" if msg.get("success") else "FAILED"),
                    error_message=msg.get("error_message"),
                    execution_time_ms=msg.get("execution_time_ms"),
                    result_data=msg.get("result_data")
                )
                await job_service.handle_agent_execution_result(result)
                await websocket.send_json({"type": "job_result_ack", "job_id": result.job_id})

            elif msg_type == "step_progress":
                # Forward intermediate step progress to browser
                session_id = msg.get("session_id", "default")
                await agent_manager.broadcast_to_session(session_id, {
                    "type": "step_update",
                    "job_id": msg.get("job_id"),
                    "step": msg.get("step"),
                    "detail": msg.get("detail"),
                    "status": msg.get("status", "in_progress")
                })

    except WebSocketDisconnect:
        if agent_instance:
            await agent_manager.unregister_agent(agent_instance.agent_id)
        logger.info(f"Autodesk Agent disconnected: {workstation_ip}")
    except Exception as e:
        logger.error(f"Error in agent websocket connection ({workstation_ip}): {e}")
        if agent_instance:
            await agent_manager.unregister_agent(agent_instance.agent_id)
