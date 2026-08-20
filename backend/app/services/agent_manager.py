import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, Set
from fastapi import WebSocket
from app.schemas import AgentRegistration, AgentHeartbeat, JobExecutionResult

logger = logging.getLogger(__name__)

def utc_now():
    return datetime.now(timezone.utc)

class ConnectedAgent:
    def __init__(self, agent_id: str, workstation_ip: str, websocket: WebSocket, application_name: str = "Inventor"):
        self.agent_id = agent_id
        self.workstation_ip = workstation_ip
        self.websocket = websocket
        self.application_name = application_name
        self.status = "READY" # READY, BUSY, DISCONNECTED
        self.last_heartbeat = utc_now()
        self.current_job_id: Optional[str] = None

class AgentManager:
    def __init__(self):
        # Map: workstation_ip -> ConnectedAgent
        self.agents_by_ip: Dict[str, ConnectedAgent] = {}
        # Map: agent_id -> ConnectedAgent
        self.agents_by_id: Dict[str, ConnectedAgent] = {}
        # Browser client websockets: session_id -> Set[WebSocket]
        self.browser_sockets: Dict[str, Set[WebSocket]] = {}

    # --- Agent WebSocket Connection Management ---

    async def register_agent(self, websocket: WebSocket, reg: AgentRegistration) -> ConnectedAgent:
        agent_id = reg.agent_id or f"agent-{reg.workstation_ip.replace('.', '-')}"
        agent = ConnectedAgent(
            agent_id=agent_id,
            workstation_ip=reg.workstation_ip,
            websocket=websocket,
            application_name=reg.application_name
        )
        self.agents_by_ip[reg.workstation_ip] = agent
        self.agents_by_id[agent_id] = agent
        logger.info(f"Autodesk Agent registered: {agent_id} on {reg.workstation_ip} ({reg.application_name})")
        
        # Notify browser clients of agent status update
        await self.broadcast_to_all_browsers({
            "type": "agent_status",
            "agent_id": agent_id,
            "workstation_ip": reg.workstation_ip,
            "status": "READY",
            "application": reg.application_name
        })
        return agent

    async def unregister_agent(self, agent_id: str):
        if agent_id in self.agents_by_id:
            agent = self.agents_by_id.pop(agent_id)
            if agent.workstation_ip in self.agents_by_ip:
                del self.agents_by_ip[agent.workstation_ip]
            logger.info(f"Autodesk Agent disconnected: {agent_id} ({agent.workstation_ip})")
            
            await self.broadcast_to_all_browsers({
                "type": "agent_status",
                "agent_id": agent_id,
                "workstation_ip": agent.workstation_ip,
                "status": "OFFLINE",
                "application": agent.application_name
            })

    def get_agent_by_ip(self, workstation_ip: str) -> Optional[ConnectedAgent]:
        return self.agents_by_ip.get(workstation_ip)

    def is_agent_ready(self, workstation_ip: str) -> bool:
        agent = self.agents_by_ip.get(workstation_ip)
        return agent is not None and agent.status == "READY"

    async def dispatch_job_to_agent(self, workstation_ip: str, job_payload: dict) -> bool:
        agent = self.get_agent_by_ip(workstation_ip)
        if not agent:
            logger.warning(f"No connected Autodesk Agent found for workstation {workstation_ip}")
            return False
        
        try:
            agent.status = "BUSY"
            agent.current_job_id = job_payload.get("job_id")
            await agent.websocket.send_json({
                "type": "execute_job",
                "job": job_payload
            })
            logger.info(f"Dispatched job {job_payload.get('job_id')} to agent on {workstation_ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch job to agent on {workstation_ip}: {e}")
            agent.status = "OFFLINE"
            return False

    # --- Browser WebSocket Management ---

    def register_browser_client(self, session_id: str, websocket: WebSocket):
        if session_id not in self.browser_sockets:
            self.browser_sockets[session_id] = set()
        self.browser_sockets[session_id].add(websocket)

    def unregister_browser_client(self, session_id: str, websocket: WebSocket):
        if session_id in self.browser_sockets:
            self.browser_sockets[session_id].discard(websocket)
            if not self.browser_sockets[session_id]:
                del self.browser_sockets[session_id]

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.browser_sockets:
            dead_sockets = set()
            for ws in self.browser_sockets[session_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.browser_sockets[session_id].discard(ws)

    async def broadcast_to_all_browsers(self, message: dict):
        for session_id in list(self.browser_sockets.keys()):
            await self.broadcast_to_session(session_id, message)

agent_manager = AgentManager()
