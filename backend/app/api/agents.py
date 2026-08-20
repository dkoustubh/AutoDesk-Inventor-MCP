from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.agent_manager import agent_manager
from app.config import settings

router = APIRouter(prefix="/agents", tags=["Autodesk Agents"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_agents():
    result = []
    # If no agents connected yet, provide registered workstation default info
    if not agent_manager.agents_by_id:
        result.append({
            "id": "agent-192-168-11-150",
            "workstation_ip": settings.DEFAULT_WORKSTATION_IP,
            "hostname": "MECH-PC-150",
            "application_name": "Inventor",
            "application_version": "2025",
            "status": "OFFLINE",
            "is_active": False,
            "user_name": settings.DEFAULT_USER_NAME
        })
        return result

    for agent_id, agent in agent_manager.agents_by_id.items():
        result.append({
            "id": agent.agent_id,
            "workstation_ip": agent.workstation_ip,
            "hostname": "MECH-PC",
            "application_name": agent.application_name,
            "status": agent.status,
            "is_active": True,
            "last_heartbeat": agent.last_heartbeat.isoformat(),
            "user_name": settings.DEFAULT_USER_NAME
        })
    return result

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    if agent_id in agent_manager.agents_by_id:
        agent = agent_manager.agents_by_id[agent_id]
        return {
            "id": agent.agent_id,
            "workstation_ip": agent.workstation_ip,
            "application_name": agent.application_name,
            "status": agent.status,
            "is_active": True,
            "last_heartbeat": agent.last_heartbeat.isoformat()
        }
    raise HTTPException(status_code=404, detail="Agent not found")
