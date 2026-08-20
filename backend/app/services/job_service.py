import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models import Job, AuditLog, User, Workstation, AutodeskAgent
from app.redis_client import redis_manager
from app.services.agent_manager import agent_manager
from app.schemas import JobExecutionResult

logger = logging.getLogger(__name__)

def utc_now():
    return datetime.now(timezone.utc)

class JobService:
    async def create_and_dispatch_job(
        self,
        prompt: str,
        tool_name: str,
        parameters: Dict[str, Any],
        workstation_ip: str,
        session_id: str,
        user_name: str = "Koustubh Deodhar"
    ) -> Dict[str, Any]:
        job_id = f"job-{uuid.uuid4().hex[:8]}"

        # 1. Emit Step: Request Received
        await agent_manager.broadcast_to_session(session_id, {
            "type": "step_update",
            "job_id": job_id,
            "step": "REQUEST_RECEIVED",
            "detail": f"Request received: '{prompt}'",
            "status": "in_progress"
        })

        # 2. Save Job to DB
        job_record = Job(
            id=job_id,
            prompt=prompt,
            tool_name=tool_name,
            parameters=parameters,
            workstation_ip=workstation_ip,
            status="QUEUED"
        )
        
        try:
            async with AsyncSessionLocal() as db:
                db.add(job_record)
                # Audit log
                audit = AuditLog(
                    event_type="JOB_CREATED",
                    user_identifier=user_name,
                    workstation_ip=workstation_ip,
                    details={"job_id": job_id, "tool": tool_name, "parameters": parameters}
                )
                db.add(audit)
                await db.commit()
        except Exception as e:
            logger.warning(f"Could not persist job {job_id} to DB: {e}")

        # 3. Save initial state in Redis
        job_payload = {
            "job_id": job_id,
            "prompt": prompt,
            "tool_name": tool_name,
            "parameters": parameters,
            "workstation_ip": workstation_ip,
            "session_id": session_id,
            "user_name": user_name,
            "status": "QUEUED",
            "created_at": utc_now().isoformat()
        }
        await redis_manager.set_job_state(job_id, job_payload)

        # 4. Emit Step: Inventor Selected & Workstation Verified
        await agent_manager.broadcast_to_session(session_id, {
            "type": "step_update",
            "job_id": job_id,
            "step": "AI_INTERPRETED",
            "detail": f"AI selected tool: {tool_name} with dimensions: {parameters.get('length_mm')}x{parameters.get('width_mm')}x{parameters.get('height_mm')} mm",
            "status": "done"
        })

        # Broadcast live 3D CAD updates to all active browser dashboards (including 5173)
        await agent_manager.broadcast_to_all_browsers({
            "type": "job_status",
            "job_id": job_id,
            "tool": tool_name,
            "parameters": parameters,
            "status": "COMPLETED",
            "message": prompt,
            "workstation_ip": workstation_ip
        })

        # 5. Push to Per-Workstation Redis Queue
        await redis_manager.push_job(workstation_ip, job_payload)

        # 6. Check if Agent is connected and dispatch
        is_ready = agent_manager.is_agent_ready(workstation_ip)
        if is_ready:
            await agent_manager.broadcast_to_session(session_id, {
                "type": "step_update",
                "job_id": job_id,
                "step": "WORKSTATION_DISPATCHED",
                "detail": f"Connected to workstation {workstation_ip}. Sending CAD instructions...",
                "status": "in_progress"
            })
            dispatched = await agent_manager.dispatch_job_to_agent(workstation_ip, job_payload)
            if dispatched:
                await redis_manager.set_job_state(job_id, {**job_payload, "status": "EXECUTING"})
        else:
            await agent_manager.broadcast_to_session(session_id, {
                "type": "step_update",
                "job_id": job_id,
                "step": "WAITING_FOR_AGENT",
                "detail": f"Workstation {workstation_ip} agent is not currently connected. Job queued in Redis.",
                "status": "warning"
            })

        return job_payload

    async def handle_agent_execution_result(self, result: JobExecutionResult):
        job_id = result.job_id
        state = await redis_manager.get_job_state(job_id) or {}
        session_id = state.get("session_id", "default")
        workstation_ip = state.get("workstation_ip", "192.168.11.150")

        # Mark agent as READY again
        agent = agent_manager.get_agent_by_ip(workstation_ip)
        if agent:
            agent.status = "READY"
            agent.current_job_id = None

        # Update DB
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Job)
                    .where(Job.id == job_id)
                    .values(
                        status=result.status,
                        result_data=result.result_data,
                        error_message=result.error_message,
                        execution_time_ms=result.execution_time_ms,
                        completed_at=utc_now()
                    )
                )
                audit = AuditLog(
                    event_type="JOB_COMPLETED" if result.success else "JOB_FAILED",
                    workstation_ip=workstation_ip,
                    details={"job_id": job_id, "success": result.success, "result": result.result_data, "error": result.error_message}
                )
                db.add(audit)
                await db.commit()
        except Exception as e:
            logger.warning(f"Could not update DB for job {job_id}: {e}")

        # Update Redis State
        state["status"] = result.status
        state["result_data"] = result.result_data
        state["error_message"] = result.error_message
        state["completed_at"] = utc_now().isoformat()
        await redis_manager.set_job_state(job_id, state)

        # Broadcast Step & Final Result to Browser Session
        if result.success:
            await agent_manager.broadcast_to_session(session_id, {
                "type": "step_update",
                "job_id": job_id,
                "step": "GEOMETRY_CREATED",
                "detail": f"Autodesk Inventor created geometry successfully in {result.execution_time_ms or 0}ms.",
                "status": "done"
            })
            await agent_manager.broadcast_to_session(session_id, {
                "type": "job_completed",
                "job_id": job_id,
                "status": "COMPLETED",
                "application": "Autodesk Inventor",
                "workstation_ip": workstation_ip,
                "parameters": state.get("parameters", {}),
                "result_data": result.result_data
            })
        else:
            await agent_manager.broadcast_to_session(session_id, {
                "type": "step_update",
                "job_id": job_id,
                "step": "EXECUTION_FAILED",
                "detail": f"Error: {result.error_message}",
                "status": "error"
            })
            await agent_manager.broadcast_to_session(session_id, {
                "type": "job_failed",
                "job_id": job_id,
                "status": "FAILED",
                "error": result.error_message
            })

job_service = JobService()
