# Autodesk Inventor MCP & Industrial CAD Automation Platform

[![Contributor](https://img.shields.io/badge/Contributor-dkoustubh-blue.svg)](https://github.com/dkoustubh)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Autodesk](https://img.shields.io/badge/CAD-Autodesk%20Inventor-E51A24.svg)](https://www.autodesk.com/products/inventor/overview)
[![MCP Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-8A2BE2.svg)](https://modelcontextprotocol.io/)
[![Three.js](https://img.shields.io/badge/Viewport-Three.js%20%2F%20WebGL-000000.svg)](https://threejs.org/)

An enterprise-grade **Industrial CAD Automation Platform** and **Model Context Protocol (MCP) Server** that bridges Large Language Models (LLMs) with native desktop **Autodesk Inventor** CAD sessions across local networks.

Translate natural language engineering specifications into structured, B-Rep validated solid geometry executed live inside Autodesk Inventor on engineer workstations.

---

## 🌟 Key Highlights

- 🧠 **Natural Language to Parametric CAD**: Direct translation of engineering intents into precise 3D solid operations (cubes, cylinders, cones, sprockets, complex extrusions, boolean cuts, fillets, chamfers, and compound assemblies).
- 🔌 **Model Context Protocol (MCP) Server**: Official Node.js/TypeScript MCP implementation compatible with **Claude Desktop**, **Cursor IDE**, and **OpenWebUI**.
- ⚡ **Real-Time WebSocket Agent Engine**: Lightweight C# .NET 8 and PowerShell workstation agents that attach to active Autodesk Inventor COM interfaces and execute commands with sub-second latency.
- 📐 **B-Rep & OpenCASCADE Kernel Validation**: Dual-layer verification utilizing Build123d / OpenCASCADE to check volume, face counts, watertight solid integrity, and STEP exports before execution.
- 🖥️ **Industrial 3-Pane Web Studio**: Interactive 3D WebGL CAD viewport (Three.js), project version management, real-time pipeline progress telemetry, and geometric inspection.

---

## 🏗️ Architecture & Topology

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI & IDE Client Interfaces                            │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐  │
│  │   Industrial CAD      │  │    Claude Desktop    │  │     Cursor IDE /     │  │
│  │   Web Studio (:8085)  │  │      / OpenWebUI     │  │      Any MCP Host    │  │
│  └───────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘  │
└──────────────┼─────────────────────────┼─────────────────────────┼──────────────┘
               │ HTTP / WS               │ Stdio / MCP             │ MCP
               ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                 Central CAD Gateway & AI Server (FastAPI :8005)                 │
│  ┌─────────────────────────┐ ┌─────────────────────────┐ ┌───────────────────┐  │
│  │  Prompt / Intent Engine │ │  OpenCASCADE Validator  │ │  APS MCP Server   │  │
│  │  (Gemma / vLLM / Claude)│ │  (Build123d Kernel)     │ │  (Node.js / TS)   │  │
│  └───────────┬─────────────┘ └───────────┬─────────────┘ └─────────┬─────────┘  │
│              └─────────────────────┬─────┘                         │            │
│                                    ▼                               │            │
│                     ┌─────────────────────────────┐                │            │
│                     │  Workstation Redis Queue    │◄───────────────┘            │
│                     │  & WebSocket Dispatcher     │                             │
│                     └──────────────┬──────────────┘                             │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │ WebSocket (:8005/ws/agent/{ip})
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│             Windows CAD Workstation (e.g., 192.168.11.150)                      │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │  ATS Autodesk Agent (C# .NET 8 / PowerShell COM Bridge)                   │  │
│  │  - Attaches to running Autodesk Inventor COM API (`Inventor.Application`) │  │
│  │  - Executes sketches, extrusions, boolean solids, holes, patterns         │  │
│  │  - Captures viewport telemetry and export artifacts (STEP/STL/DWG)        │  │
│  └───────────────────────────────────┬───────────────────────────────────────┘  │
│                                      ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                   Autodesk Inventor Desktop Application                   │  │
│  │                   (Active Part / Assembly Document)                       │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
├── aps-mcp-server/         # Node.js / TypeScript Model Context Protocol (MCP) server
│   ├── src/index.ts        # MCP Tools (inventor_create_box, sprockets, compound, etc.)
│   └── package.json        # MCP Server configuration
│
├── autodesk-agent/         # Windows Workstation Agent (.NET 8 & PowerShell)
│   ├── ATS.AutodeskAgent.sln
│   ├── src/                # C# WebSocket Client & Inventor COM interop
│   ├── agent.ps1           # Standalone PowerShell COM automation agent
│   ├── run.bat             # Quick launch script for Windows workstation
│   └── install.bat         # Service/Add-in installer
│
├── backend/                # Central AI & CAD Gateway (FastAPI)
│   ├── app/
│   │   ├── main.py         # FastAPI application entrypoint
│   │   ├── api/            # REST & WebSocket endpoints (chat, jobs, agents, render)
│   │   ├── services/       # LLM intent parser, Build123d kernel validator, Redis queue
│   │   └── models.py       # SQLAlchemy & Pydantic schemas
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container definition
│
├── frontend/               # Industrial 3-Pane Web Studio (React + Vite + TailwindCSS)
│   ├── src/
│   │   ├── components/     # CadViewport3D, LeftProjectSidebar, RightInspector, etc.
│   │   ├── types/          # CAD feature & project interfaces
│   │   └── App.tsx         # Main application layout
│   └── Dockerfile          # Nginx production container
│
├── openwebui-tools/        # Custom OpenWebUI Tools & CAD Skills
│   ├── autodesk_inventor_tools.py  # Python function calling tools for OpenWebUI
│   └── autodesk_cad_skill.md       # CAD design system prompt & engineering rules
│
├── exports/                # Export artifacts (STEP, STL, GLB, DWG)
├── docker-compose.yml      # Multi-container orchestration (Backend + Frontend)
└── .env.example            # Environment template
```

---

## 🚀 Deployment Guide

### Prerequisites

| Machine / Node | Requirements |
|---|---|
| **Central Server / Cloud** | Linux / macOS / Windows with Docker & Docker Compose **OR** Python 3.11+, Node.js 20+, Redis, PostgreSQL |
| **CAD Workstation** | Windows 10/11 with **Autodesk Inventor** (2022+), .NET 8 SDK / Runtime or PowerShell 5.1+ |
| **AI LLM Backend** | Local vLLM instance (e.g. `google/gemma-4-31B-it`), Ollama, or OpenAI/Anthropic API key |

---

### Step 1: Central Server Setup (Docker Compose)

1. Clone the repository:
   ```bash
   git clone https://github.com/dkoustubh/AutoDesk-Inventor-MCP.git
   cd AutoDesk-Inventor-MCP
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to match your network topology:
   ```env
   HOST=0.0.0.0
   PORT=8005
   VLLM_API_BASE=http://192.168.11.86:8000/v1
   VLLM_MODEL=google/gemma-4-31B-it
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@192.168.11.86:5432/ats_engineering
   REDIS_URL=redis://192.168.11.86:6380/0
   DEFAULT_WORKSTATION_IP=192.168.11.150
   DEFAULT_USER_NAME=Koustubh Deodhar
   ```

3. Launch services using Docker Compose:
   ```bash
   docker compose up -d --build
   ```

4. Verify backend health:
   ```bash
   curl http://localhost:8005/health
   # Expected: {"status": "ok", "active_agents": [...]}
   ```

5. Access the Web Studio:
   ```
   http://<SERVER_IP>:8085
   ```

---

### Step 2: Native Local Development Setup (Alternative)

If running without Docker:

#### 1. Backend (Python FastAPI)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

#### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev -- --host
```

---

### Step 3: Windows Workstation Agent Setup

Run this on the Windows machine where Autodesk Inventor is installed.

1. Transfer or clone the `autodesk-agent` directory to your Windows workstation.
2. Launch **Autodesk Inventor** (open a blank Part document `.ipt` or leave Inventor running).
3. Open PowerShell or Command Prompt inside `autodesk-agent`:

   **Option A: Using the Compiled C# Agent**
   ```cmd
   build.bat
   run.bat
   ```

   **Option B: Using the Standalone PowerShell Agent**
   ```powershell
   powershell -ExecutionPolicy Bypass -File agent.ps1 -ServerUrl "ws://<SERVER_IP>:8005/ws/agent/<WORKSTATION_IP>"
   ```

4. The console will display:
   ```text
   [InventorAdapter] Attached to active Autodesk Inventor session.
   [AgentWS] Connected to Central AI Server at ws://192.168.11.86:8005/ws/agent/192.168.11.150...
   [AgentWS] Registered successfully on Central Server. Status: READY.
   ```

---

### Step 4: Model Context Protocol (MCP) Server Setup

Integrate Autodesk Inventor directly with your favorite AI tools.

1. Build the MCP Server:
   ```bash
   cd aps-mcp-server
   npm install
   npm run build
   ```

2. Add to **Claude Desktop**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "autodesk-inventor": {
         "command": "node",
         "args": ["<PATH_TO_REPO>/aps-mcp-server/dist/index.js"],
         "env": {
           "CAD_GATEWAY_URL": "http://192.168.11.86:8005",
           "WORKSTATION_IP": "192.168.11.150"
         }
       }
     }
   }
   ```

3. Add to **Cursor IDE** (`.cursor/mcp.json`):
   ```json
   {
     "mcpServers": {
       "autodesk-inventor": {
         "command": "node",
         "args": ["./aps-mcp-server/dist/index.js"],
         "env": {
           "CAD_GATEWAY_URL": "http://192.168.11.86:8005",
           "WORKSTATION_IP": "192.168.11.150"
         }
       }
     }
   }
   ```

4. Available MCP Tools:
   - `inventor_create_box`: Create boxes, plates, blocks with custom dimensions (mm/cm).
   - `inventor_create_cone`: Create cones and frustums.
   - `inventor_create_rhombus`: Create rhombus/diamond 3D prisms.
   - `inventor_create_sprocket`: Parametric sprockets and gears with teeth and pitch specifications.
   - `inventor_create_compound`: Multi-feature complex boolean geometries.
   - `aps_translate_model`: Translate STEP/IPT models for 3D web viewing.

---

### Step 5: OpenWebUI Integration

1. In OpenWebUI, navigate to **Workspace ➔ Tools**.
2. Create a new tool and import `openwebui-tools/autodesk_inventor_tools.py`.
3. Set the `CAD_GATEWAY_URL` to `http://<SERVER_IP>:8005`.
4. In System Prompt or Model Knowledge, attach `openwebui-tools/autodesk_cad_skill.md`.

---

## 🧪 End-to-End Verification Test

1. Open the Web Studio at `http://<SERVER_IP>:8085`.
2. Confirm the workstation indicator shows **ONLINE / READY** for target IP `192.168.11.150`.
3. In the prompt bar, enter:
   ```text
   Create a 30 x 30 x 30 mm cube with 4mm mounting holes on each corner.
   ```
4. Click **Generate Design**.
5. Observe:
   - Real-time pipeline stage progress (**Planning ➔ Generating ➔ Kernel Validation ➔ Workstation Dispatch**).
   - 3D WebGL preview render in the viewport.
   - The solid cube created in real-time inside **Autodesk Inventor** on the Windows machine.

---

## 🛠️ API & WebSocket Reference

### HTTP REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server and agent connection status |
| `POST` | `/api/chat` | Natural language CAD generation endpoint |
| `GET` | `/api/agents` | List connected workstation agents |
| `GET` | `/api/jobs` | Retrieve CAD job history and status |
| `POST` | `/api/export/{job_id}` | Export geometry as STEP, STL, or GLB |

### WebSocket Endpoints

| Endpoint | Protocol | Description |
|---|---|---|
| `/ws/agent/{client_ip}` | JSON RPC / Telemetry | Bidirectional channel for workstation CAD agents |
| `/ws/ui/{client_id}` | Event Stream | Real-time telemetry feed for Web Studio UI |

---

## 🤝 Contributors

- **dkoustubh** ([@dkoustubh](https://github.com/dkoustubh)) — Creator & Lead Maintainer

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
