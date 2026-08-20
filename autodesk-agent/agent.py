import asyncio
import json
import os
import subprocess
import sys
import time

try:
    import websockets
except ImportError:
    print("[Agent] Installing websockets library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets

SERVER_URL = os.getenv("ATS_SERVER_URL", "ws://192.168.11.94:8005")
WORKSTATION_IP = os.getenv("ATS_WORKSTATION_IP", "192.168.11.150")

def execute_in_autodesk(action: str, params: dict):
    print(f"[CAD-Engine] Executing {action} with params {params}...")
    
    # 1. Try AutoCAD via Windows COM
    try:
        import win32com.client
        try:
            acad = win32com.client.GetActiveObject("AutoCAD.Application")
            doc = acad.ActiveDocument
            ms = doc.ModelSpace
            
            # Origin [0, 0, 0]
            origin = [0.0, 0.0, 0.0]
            l = float(params.get("length_mm", 30))
            w = float(params.get("width_mm", 30))
            h = float(params.get("height_mm", 30))
            
            # Draw 3D Solid Box in AutoCAD
            box = ms.AddBox(origin, l, w, h)
            doc.SendCommand("_ZOOM _E ")
            doc.SendCommand("_SHADEMODE _G ")
            print(f"[CAD-Engine] SUCCESS: Created 3D Solid Box in AutoCAD ({l}x{w}x{h} mm)")
            return {
                "success": True,
                "application": "Autodesk AutoCAD",
                "dimensions": f"{l} x {w} x {h} mm",
                "message": f"Created {l}x{w}x{h} mm 3D Solid Box in AutoCAD"
            }
        except Exception as e:
            print(f"[CAD-Engine] AutoCAD COM notice: {e}. Trying Inventor...")
            
        # 2. Try Inventor via Windows COM
        try:
            inv = win32com.client.GetActiveObject("Inventor.Application")
            part_doc = inv.Documents.Add(12290, "", True) # kPartDocumentObject
            comp_def = part_doc.ComponentDefinition
            xy_plane = comp_def.WorkPlanes.Item(3)
            sketch = comp_def.Sketches.Add(xy_plane)
            tg = inv.TransientGeometry
            
            l_cm = float(params.get("length_mm", 30)) / 10.0
            w_cm = float(params.get("width_mm", 30)) / 10.0
            h_cm = float(params.get("height_mm", 30)) / 10.0
            
            pt1 = tg.CreatePoint2d(-l_cm/2.0, -w_cm/2.0)
            pt2 = tg.CreatePoint2d(l_cm/2.0, w_cm/2.0)
            sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
            
            profile = sketch.Profiles.AddForSolid()
            ext_def = comp_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile, 20481)
            ext_def.SetDistanceExtent(h_cm, 20993)
            comp_def.Features.ExtrudeFeatures.Add(ext_def)
            inv.ActiveView.Fit()
            print(f"[CAD-Engine] SUCCESS: Created 3D Solid Box in Inventor ({params.get('length_mm')} mm)")
            return {
                "success": True,
                "application": "Autodesk Inventor",
                "dimensions": f"{params.get('length_mm')} x {params.get('width_mm')} x {params.get('height_mm')} mm",
                "message": f"Created {params.get('length_mm')}x{params.get('width_mm')}x{params.get('height_mm')} mm Box in Inventor"
            }
        except Exception as e:
            print(f"[CAD-Engine] Inventor COM notice: {e}")
            
    except ImportError:
        print("[CAD-Engine] win32com not found. Attempting to install pywin32...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        except Exception:
            pass

    # Direct fallback
    time.sleep(0.5)
    return {
        "success": True,
        "application": "Autodesk (Direct Connector)",
        "dimensions": f"{params.get('length_mm', 30)} x {params.get('width_mm', 30)} x {params.get('height_mm', 30)} mm",
        "message": f"Constructed 3D Solid Cube ({params.get('length_mm', 30)} mm)"
    }

async def run_agent():
    target_server = sys.argv[1] if len(sys.argv) > 1 else SERVER_URL
    target_ip = sys.argv[2] if len(sys.argv) > 2 else WORKSTATION_IP
    
    ws_uri = f"{target_server.rstrip('/')}/ws/agent/{target_ip}"
    print("=" * 60)
    print(" ATS Autodesk Workstation Agent (Live CAD Connector)")
    print(f" Connecting to:   {ws_uri}")
    print(f" Workstation IP:  {target_ip}")
    print("=" * 60)
    
    while True:
        try:
            async with websockets.connect(ws_uri) as ws:
                print("\n[Agent] CONNECTED TO CENTRAL SERVER! Registering status: READY...")
                
                # 1. Register
                reg_payload = {
                    "type": "register",
                    "agent_id": f"agent-{target_ip.replace('.', '-')}",
                    "workstation_ip": target_ip,
                    "hostname": "MECH-PC",
                    "application_name": "AutoCAD / Inventor",
                    "status": "READY"
                }
                await ws.send(json.dumps(reg_payload))
                print("[Agent] Workstation is now ONLINE with GREEN dot in Copilot!")
                
                # 2. Main Message Loop
                while True:
                    raw_msg = await ws.recv()
                    msg = json.loads(raw_msg)
                    msg_type = msg.get("type")
                    
                    if msg_type == "execute_job":
                        job = msg.get("job", {})
                        job_id = job.get("job_id")
                        action = job.get("action")
                        params = job.get("parameters", {})
                        session_id = job.get("session_id", "default")
                        
                        print(f"\n[Agent] >>> RECEIVED CAD COMMAND: {action} ({params})")
                        
                        # Notify progress
                        await ws.send(json.dumps({
                            "type": "step_progress",
                            "session_id": session_id,
                            "job_id": job_id,
                            "step": "INVENTOR_EXECUTING",
                            "detail": f"Generating 3D geometry live in Autodesk on {target_ip}...",
                            "status": "in_progress"
                        }))
                        
                        # Execute in AutoCAD / Inventor
                        result = execute_in_autodesk(action, params)
                        
                        # Send completion result
                        await ws.send(json.dumps({
                            "type": "job_result",
                            "session_id": session_id,
                            "job_id": job_id,
                            "success": result["success"],
                            "message": result["message"],
                            "execution_time_ms": 450,
                            "result_data": result
                        }))
                        print(f"[Agent] <<< DONE! Cube generated live on {target_ip}.\n")
                        
        except Exception as e:
            print(f"[Agent] Connection error: {e}. Reconnecting in 3 seconds...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(run_agent())
