import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from app.services.validator import validator_service
from app.services.job_service import job_service
from app.services.agent_manager import agent_manager
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["Autodesk MCP Gateway"])

# Official Model Context Protocol Tools Manifest
MCP_TOOLS_MANIFEST = [
    {
        "name": "inventor.create_box",
        "description": "Creates a parametric 3D solid box, cube, or plate in Autodesk Inventor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "length_mm": {"type": "number", "description": "Length along X axis in mm", "minimum": 0.01, "maximum": 50000.0},
                "width_mm": {"type": "number", "description": "Width along Y axis in mm", "minimum": 0.01, "maximum": 50000.0},
                "height_mm": {"type": "number", "description": "Height along Z axis in mm", "minimum": 0.01, "maximum": 50000.0},
                "centered": {"type": "boolean", "description": "Center on origin", "default": True},
                "workstation_ip": {"type": "string", "description": "Workstation IP", "default": "192.168.11.150"}
            },
            "required": ["length_mm", "width_mm", "height_mm"]
        }
    },
    {
        "name": "inventor.create_cylinder",
        "description": "Creates a parametric 3D solid cylinder, pin, or shaft in Autodesk Inventor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "diameter_mm": {"type": "number", "description": "Diameter in mm", "minimum": 0.01},
                "radius_mm": {"type": "number", "description": "Radius in mm", "minimum": 0.01},
                "height_mm": {"type": "number", "description": "Height/length in mm", "minimum": 0.01},
                "centered": {"type": "boolean", "default": True},
                "workstation_ip": {"type": "string", "default": "192.168.11.150"}
            },
            "required": ["height_mm"]
        }
    },
    {
        "name": "inventor.create_sphere",
        "description": "Creates a parametric 3D solid sphere in Autodesk Inventor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "radius_mm": {"type": "number", "description": "Radius in mm", "minimum": 0.01},
                "diameter_mm": {"type": "number", "description": "Diameter in mm", "minimum": 0.01},
                "workstation_ip": {"type": "string", "default": "192.168.11.150"}
            }
        }
    },
    {
        "name": "inventor.create_cone",
        "description": "Creates a parametric 3D solid cone in Autodesk Inventor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "base_radius_mm": {"type": "number", "description": "Base radius in mm", "minimum": 0.01},
                "height_mm": {"type": "number", "description": "Height in mm", "minimum": 0.01},
                "workstation_ip": {"type": "string", "default": "192.168.11.150"}
            },
            "required": ["base_radius_mm", "height_mm"]
        }
    },
    {
        "name": "inventor.create_compound",
        "description": "Creates a compound multi-feature solid (e.g. cube base with top cone) in Autodesk Inventor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "length_mm": {"type": "number", "description": "Base length in mm"},
                "width_mm": {"type": "number", "description": "Base width in mm"},
                "height_mm": {"type": "number", "description": "Base height in mm"},
                "top_feature": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["cone", "cylinder", "sphere", "hole"]},
                        "size_mm": {"type": "number"}
                    }
                },
                "workstation_ip": {"type": "string", "default": "192.168.11.150"}
            },
            "required": ["length_mm", "width_mm", "height_mm"]
        }
    }
]

class McpToolCallRequest(BaseModel):
    name: str = Field(..., description="Name of the MCP tool")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")

class McpJsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str
    params: Optional[Dict[str, Any]] = None

@router.get("/tools")
async def list_mcp_tools():
    """Lists all available Autodesk MCP tools."""
    return {"tools": MCP_TOOLS_MANIFEST}

@router.post("/tools/call")
async def call_mcp_tool(request: McpToolCallRequest, session_id: str = Query("default")):
    """Executes an MCP Tool Call and dispatches to Autodesk CAD agent."""
    tool_name = request.name
    args = request.arguments
    workstation_ip = args.get("workstation_ip", settings.DEFAULT_WORKSTATION_IP)

    job = await job_service.create_and_dispatch_job(
        prompt=f"MCP Tool Call: {tool_name}",
        tool_name=tool_name,
        parameters=args,
        workstation_ip=workstation_ip,
        session_id=session_id,
        user_name=settings.DEFAULT_USER_NAME
    )

    return {
        "content": [
            {
                "type": "text",
                "text": f"Successfully queued and dispatched {tool_name} to Autodesk Workstation ({workstation_ip}). Job ID: {job['job_id']}"
            }
        ],
        "isError": False,
        "job_id": job["job_id"],
        "status": job["status"],
        "parameters": args
    }

@router.post("/jsonrpc")
async def handle_jsonrpc(req: McpJsonRpcRequest = Body(...)):
    """Standard JSON-RPC 2.0 endpoint for MCP Clients."""
    if req.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {"tools": MCP_TOOLS_MANIFEST}
        }
    elif req.method == "tools/call":
        params = req.params or {}
        tool_name = params.get("name")
        args = params.get("arguments", {})
        workstation_ip = args.get("workstation_ip", settings.DEFAULT_WORKSTATION_IP)

        job = await job_service.create_and_dispatch_job(
            prompt=f"MCP JSON-RPC: {tool_name}",
            tool_name=tool_name,
            parameters=args,
            workstation_ip=workstation_ip,
            session_id="jsonrpc-session",
            user_name=settings.DEFAULT_USER_NAME
        )

        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Executed {tool_name} in Autodesk Inventor on {workstation_ip}."
                    }
                ],
                "job_id": job["job_id"],
                "status": job["status"]
            }
        }
    
    raise HTTPException(status_code=400, detail=f"Unsupported MCP method: {req.method}")
