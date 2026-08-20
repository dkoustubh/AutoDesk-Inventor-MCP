import asyncio
import json
import websockets

async def run_mock_agent(server_url="ws://localhost:8005", workstation_ip="192.168.11.150"):
    uri = f"{server_url}/ws/agent/{workstation_ip}"
    print(f"[MockAgent] Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        print("[MockAgent] Connected to server as Autodesk Agent!")
        
        while True:
            raw_msg = await ws.recv()
            data = json.loads(raw_msg)
            print(f"[MockAgent] Received event: {data}")
            
            if data.get("type") == "EXECUTE_JOB":
                job = data.get("job", {})
                job_id = job.get("job_id")
                action = job.get("action")
                params = job.get("parameters", {})
                print(f"[MockAgent] >>> Executing CAD job: {action} ({params})")
                
                # Step 1: Send progress
                await ws.send(json.dumps({
                    "type": "JOB_PROGRESS",
                    "job_id": job_id,
                    "step": "INVENTOR_EXECUTING",
                    "detail": "Creating PartDocument and Extruding 30x30x30 mm box in Inventor..."
                }))
                
                await asyncio.sleep(1.0)
                
                # Step 2: Send completion result
                await ws.send(json.dumps({
                    "type": "JOB_RESULT",
                    "job_id": job_id,
                    "success": True,
                    "message": f"Successfully created {params.get('length_mm')}x{params.get('width_mm')}x{params.get('height_mm')} mm solid box in Autodesk Inventor",
                    "execution_time_ms": 780,
                    "data": {
                        "application": "Autodesk Inventor",
                        "dimensions": f"{params.get('length_mm')} x {params.get('width_mm')} x {params.get('height_mm')} mm",
                        "status": "SOLID_CREATED"
                    }
                }))
                print(f"[MockAgent] <<< Job {job_id} completed successfully.")

if __name__ == "__main__":
    asyncio.run(run_mock_agent())
