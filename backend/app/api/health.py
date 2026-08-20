from fastapi import APIRouter
from app.config import settings
from app.redis_client import redis_manager
from app.services.agent_manager import agent_manager

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    connected_agents_count = len(agent_manager.agents_by_id)
    connected_ips = list(agent_manager.agents_by_ip.keys())
    
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "vllm_api_base": settings.VLLM_API_BASE,
        "vllm_model": settings.VLLM_MODEL,
        "redis_connected": redis_manager.redis is not None,
        "connected_autodesk_agents": connected_agents_count,
        "workstations_online": connected_ips
    }
