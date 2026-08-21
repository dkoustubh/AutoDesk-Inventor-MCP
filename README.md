# OmniCAD — Professional AI-Native Parametric Mechanical CAD Platform

[![Contributor](https://img.shields.io/badge/Contributor-dkoustubh-blue.svg)](https://github.com/dkoustubh)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Autodesk](https://img.shields.io/badge/CAD-Autodesk%20Inventor-E51A24.svg)](https://www.autodesk.com/products/inventor/overview)
[![Kernel](https://img.shields.io/badge/CAD%20Kernel-OpenCASCADE%20%2F%20build123d-FF6F00.svg)](https://build123d.readthedocs.io/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-8A2BE2.svg)](https://modelcontextprotocol.io/)
[![Three.js](https://img.shields.io/badge/Viewport-Three.js%20%2F%20WebGL-000000.svg)](https://threejs.org/)
[![Pytest](https://img.shields.io/badge/Tests-19%20Passed%20(100%25)-brightgreen.svg)](tests/)

An enterprise-grade **Industrial AI-Native Parametric Mechanical CAD Platform** and **Model Context Protocol (MCP) Server** that translates natural language engineering requests into geometrically validated, dimensionally accurate 3D CAD models and executes them live in **Autodesk Inventor**.

---

## 🧭 Core Architectural Philosophy

> **"Gemma is NOT the CAD kernel. Gemma is the Interpreter and Planner. Deterministic CAD engines construct the geometry. Validators verify. Repair engines fix. Only 100% verified geometry reaches the engineer."**

```
Natural Language Engineering Request
                 │
                 ▼
1. Engineering Language Interpreter (ELI)
   • Lossless requirement normalization
   • Non-blocking ambiguity detection
   • Conversational parametric editing
                 │
                 ▼
2. Engineering Knowledge Base (EKB)
   • ISO 606, DIN 8187, ASME B16.5, ISO 2768-m
   • Conveyor, ASRS, Sprocket, Gear, Flange templates
                 │
                 ▼
3. Parametric Feature Graph (DAG)
   • Nodes: Primitives, Extrusions, Holes, Patterns
   • Edges: Dependencies and workplane constraints
                 │
                 ▼
4. Deterministic Math & Constraint Solver
   • PCD bolt trigonometry: (R·cos θ, R·sin θ)
   • Hierarchy check: D_bore < D_raised_face < PCD < D_outer
   • Wall thickness & edge margin assertions (> 2.0 mm)
                 │
                 ▼
5. Parametric CAD Code Generator
   • Named engineering constants in Python build123d DSL
                 │
                 ▼
6. OpenCASCADE CAD Kernel Execution
   • B-Rep solid construction in isolated sandbox
   • Export STEP (ISO-10303), STL, GLB, and JSON metadata
                 │
                 ▼
7. Dual Geometric & Visual Validation
   • BRepCheck_Analyzer watertightness & manifold verification
   • Cylindrical surface radius measurement & PCD hole counting
   • 4-View (ISO, Top, Front, Right) contact sheet projection
                 │
                 ▼
8. Closed-Loop Feature Repair Engine
   • Localized diagnostic & targeted non-destructive patch
                 │
                 ▼
9. Verified Artifacts Dispatched to Autodesk Inventor
   • Live desktop execution via C# / PowerShell COM Agent
```

---

## 🌟 Key Capabilities

### 1. Lossless Engineering Language Interpreter (ELI)
- Extracts 100% of explicit and implicit dimensions without losing constraints.
- Identifies underspecified inputs (e.g. *"Make a bracket"*) and asks targeted clarification questions rather than guessing arbitrary geometry.
- Supports **Conversational Parametric Editing** (e.g. *"Change the PCD from 120 mm to 125 mm"*, *"Increase flange thickness to 25 mm"*) by modifying existing Feature Graph nodes without regenerating the entire part.

### 2. Parametric Feature Graph (DAG)
- Complete internal tree representation of all atomic operations (`box`, `cylinder`, `through_hole`, `circular_pattern`, `raised_face`, `fillet`, `chamfer`, `boss`, `slot`, `pocket`).
- Generates clean, human-readable Python `build123d` source code that mechanical engineers can review and inspect.

### 3. Industrial Part & Mechanical Knowledge Base
- **Pipe Flanges**: ASME B16.5 / ISO 7005-1 (base disc, center through-bore, raised face, circular PCD bolt pattern).
- **Conveyor & Material Handling**: Conveyor Rollers (ISO 1537 / CEMA), Mounting Plates (ISO 2768-m), Ribbed Brackets, Powered Roller Beds (PRB), Rotary Turntables.
- **Power Transmission**: ISO 606 & ANSI B29.1 Roller Chain Sprockets (06B, 08B, 10B, 12B, ANSI 35, 40, 50, 60), Involute Planetary & Spur Gear kinematics ($Z_{\text{ring}} = Z_{\text{sun}} + 2 \cdot Z_{\text{planet}}$).

### 4. Dual-Engine Validation & Closed-Loop Repair
- **Topological B-Rep Validation**: Explores OpenCASCADE face topology, measures inner/outer cylinder radii, verifies through-hole penetration, computes exact analytical volume ($V \pm 1\%$).
- **Multi-View Visual Inspection**: Generates 4-view orthographic contact sheets (Isometric, Top, Front, Right).
- **Localized Repair Loop**: If any check fails, the repair engine diagnoses the failing constraint and patches only the target feature.

### 5. Multi-Provider LLM Abstraction & Model Router
- **Gemma 31B Local**: Hosted on-premise at `http://192.168.11.86:8000/v1` (96 GB VRAM server).
- **Mistral API Reviewer**: Cloud second-opinion reviewer for safety-critical or high-risk mechanical checks.

---

## 🏗️ Hardware Topology & Deployment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Central AI Server (192.168.11.86)                      │
│  • 96 GB VRAM GPU Cluster                                                   │
│  • Gemma 31B (vLLM Engine :8000)                                            │
│  • Open WebUI & Local Model Inference                                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ High-Speed LAN
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 Central CAD Gateway (Mac / Linux 192.168.11.94)             │
│  • FastAPI REST & WebSocket Backend (:8005)                                 │
│  • ELI & 10-Stage CAD Reasoning Pipeline                                    │
│  • OpenCASCADE 7.9 B-Rep Kernel & build123d Sandbox                         │
│  • Redis Job Queue & Workstation Dispatcher                                 │
│  • OmniCAD 3-Pane Web Studio (React + Three.js :8085 / :9999)               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ WebSocket Dispatcher (:8005/ws/agent)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 Windows CAD Workstation (192.168.11.150)                    │
│  • Autodesk Inventor 2026 Desktop Session                                   │
│  • ATS Workstation Agent (.NET 8 C# / PowerShell COM Bridge)                │
│  • Live sketch extrusion, boolean features, holes, pattern execution        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
├── backend/                    # Central AI & CAD Gateway (FastAPI)
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint & router registration
│   │   ├── config.py           # Server & workstation configuration
│   │   ├── api/                # REST & WS endpoints (/api/chat, /ws/agent, etc.)
│   │   ├── pipeline/           # 10-Stage Contract-Driven CAD Reasoning Engine
│   │   │   ├── eli.py                  # Engineering Language Interpreter & Parametric Editor
│   │   │   ├── feature_graph.py        # Parametric Feature Graph (DAG) & Code Gen
│   │   │   ├── knowledge_base.py       # Part Templates (Conveyor, ASRS, Mechanical)
│   │   │   ├── math_solver.py          # Analytical trigonometry & constraint validation
│   │   │   ├── math_sprocket.py        # ISO 606 / ANSI roller chain sprocket math
│   │   │   ├── math_gear.py            # Involute planetary & spur gear kinematics
│   │   │   ├── feature_planner.py      # Ordered atomic CAD construction planning
│   │   │   ├── cad_generator.py        # Parametric build123d DSL generator
│   │   │   ├── kernel_runner.py        # OpenCASCADE execution sandbox & exporter
│   │   │   ├── geometric_validator.py  # OpenCASCADE B-Rep surface inspection
│   │   │   ├── visual_validator.py     # 4-view contact sheet generator
│   │   │   ├── repair_engine.py        # Closed-loop targeted repair planner
│   │   │   └── engine.py               # Master 10-Stage Pipeline Coordinator
│   │   └── services/           # Redis queue, Job manager, LLM connector
│   └── requirements.txt
│
├── frontend/                   # OmniCAD 3-Pane Web Studio (React + Vite + TailwindCSS)
│   ├── src/
│   │   ├── components/         # CadViewport3D, LeftProjectSidebar, RightInspector, TopToolbar
│   │   ├── types/              # TypeScript CAD interfaces & validation schemas
│   │   └── App.tsx             # Studio layout with blank canvas initialization
│   └── package.json
│
├── autodesk-agent/             # Windows Workstation Agent (.NET 8 & PowerShell)
│   ├── src/                    # C# WebSocket Client & Inventor COM interop
│   ├── agent.ps1               # Standalone PowerShell COM automation agent
│   ├── run.bat                 # One-click launch script
│   └── install.bat             # Service / Add-in installer
│
├── aps-mcp-server/             # Model Context Protocol (MCP) Server (Node.js/TS)
│   └── src/index.ts            # MCP Tools for Claude Desktop, Cursor, and OpenWebUI
│
└── tests/                      # Automated Verification & Benchmark Suites
    ├── golden_cad/             # Golden benchmark JSON definitions
    │   ├── flange.json         # ASME/ISO pipe flange golden benchmark
    │   ├── plate.json          # Mounting plate benchmark
    │   ├── cube.json           # Prismatic block benchmark
    │   ├── bolt_pattern.json   # PCD circular pattern benchmark
    │   └── sprocket.json       # ISO 606 drive sprocket benchmark
    ├── test_golden_pipe_flange.py
    ├── test_benchmark_suite.py
    ├── test_golden_cad_benchmarks.py
    ├── test_eli_conversational_editing.py
    └── test_math_gears_sprockets.py
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/dkoustubh/AutoDesk-Inventor-MCP.git
cd AutoDesk-Inventor-MCP
```

### 2. Configure Environment
Create `.env` inside `backend/`:
```env
PROJECT_NAME="OmniCAD Industrial Engineering Platform"
API_V1_STR="/api"
VLLM_API_BASE="http://192.168.11.86:8000/v1"
VLLM_MODEL="gemma-31b"
REDIS_URL="redis://localhost:6379/0"
DEFAULT_WORKSTATION_IP="192.168.11.150"
```

### 3. Start Central AI Gateway (Backend)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

### 4. Start OmniCAD Web Studio (Frontend)
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173` or `http://localhost:9999`.

### 5. Launch Autodesk Inventor Workstation Agent (Windows)
On your Windows CAD workstation (`192.168.11.150`):
```powershell
cd autodesk-agent
.\run.bat
```
The agent automatically connects to `ws://192.168.11.94:8005/ws/agent/192.168.11.150` and hooks into active Autodesk Inventor sessions.

---

## 🧪 Automated Testing & Benchmarks

Run the complete 19-test verification suite:
```bash
pytest tests/ -v
```

### Test Coverage Summary:
```text
tests/test_golden_pipe_flange.py::test_stage_1_requirement_analyzer PASSED
tests/test_golden_pipe_flange.py::test_stage_3_engineering_math_solver PASSED
tests/test_golden_pipe_flange.py::test_stage_4_6_code_generation PASSED
tests/test_golden_pipe_flange.py::test_stage_7_8_kernel_and_geometric_validation PASSED
tests/test_golden_pipe_flange.py::test_golden_pipe_flange_full_pipeline_run PASSED
tests/test_benchmark_suite.py::test_cad_benchmark_item[BASIC_CUBE_001] PASSED
tests/test_benchmark_suite.py::test_cad_benchmark_item[BASIC_PLATE_002] PASSED
tests/test_benchmark_suite.py::test_cad_benchmark_item[FEATURE_DRILLED_BLOCK_003] PASSED
tests/test_benchmark_suite.py::test_cad_benchmark_item[GOLDEN_FLANGE_001] PASSED
tests/test_golden_cad_benchmarks.py::test_golden_cad_benchmark[GOLDEN_BOLT_PATTERN_004] PASSED
tests/test_golden_cad_benchmarks.py::test_golden_cad_benchmark[GOLDEN_CUBE_003] PASSED
tests/test_golden_cad_benchmarks.py::test_golden_cad_benchmark[GOLDEN_FLANGE_001] PASSED
tests/test_golden_cad_benchmarks.py::test_golden_cad_benchmark[GOLDEN_PLATE_002] PASSED
tests/test_golden_cad_benchmarks.py::test_golden_cad_benchmark[GOLDEN_SPROCKET_005] PASSED
tests/test_eli_conversational_editing.py::test_eli_initial_interpretation PASSED
tests/test_eli_conversational_editing.py::test_eli_conversational_parametric_edit PASSED
tests/test_eli_conversational_editing.py::test_eli_ambiguity_detection PASSED
tests/test_math_gears_sprockets.py::test_sprocket_math_08b PASSED
tests/test_math_gears_sprockets.py::test_planetary_gear_kinematics PASSED

============================== 19 passed in 4.79s ==============================
```

---

## 🤝 Author & Contributor

- **dkoustubh** — Lead Architect & Developer ([GitHub Profile](https://github.com/dkoustubh))

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
