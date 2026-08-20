from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.redis_client import redis_manager
from app.database import AsyncSessionLocal
from app.models import Job
from sqlalchemy import select

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    # Check Redis first
    state = await redis_manager.get_job_state(job_id)
    if state:
        return state

    # Fallback to DB
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                return {
                    "job_id": job.id,
                    "prompt": job.prompt,
                    "tool_name": job.tool_name,
                    "parameters": job.parameters,
                    "workstation_ip": job.workstation_ip,
                    "status": job.status,
                    "result_data": job.result_data,
                    "error_message": job.error_message,
                    "execution_time_ms": job.execution_time_ms,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Job not found")
