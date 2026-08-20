# ATS Autodesk Agent (Windows Workstation)

This agent runs on the Autodesk Engineering Workstation (`192.168.11.150`), establishes an outbound WebSocket connection to the Central AI Server (`192.168.11.86`), and invokes Autodesk Inventor via official COM Interop APIs.

## Prerequisites on Windows Workstation (`192.168.11.150`):
1. **Windows 10 / 11** with active user session (**Koustubh Deodhar**).
2. **Autodesk Inventor 2024 / 2025** installed and licensed.
3. **.NET 8 SDK** installed (`dotnet --version`).

## Running the Agent:

### 1. Live Autodesk Inventor Execution
```powershell
cd agent-windows
$env:ATS_SERVER_URL="http://192.168.11.86:8005"
$env:WORKSTATION_IP="192.168.11.150"
dotnet run
```

### 2. Standalone Simulation / Mock Mode
```powershell
dotnet run -- --mock
```
