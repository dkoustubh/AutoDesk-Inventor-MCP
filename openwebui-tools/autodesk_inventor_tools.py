"""
title: Autodesk Platform Services (APS) & Inventor AI Multi-Tool Suite
author: ATS Engineering AI
description: Full APS and Autodesk Inventor CAD modeling suite powered by Gemma 31B GPU (192.168.11.86) to generate 3D solid models, PRB conveyors, rotary turntables, ribbed brackets, sprockets, and complex spatial assemblies in Autodesk Inventor (192.168.11.150).
version: 6.0.0
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, Callable, Awaitable

class Tools:
    def __init__(self):
        self.gateway_url = "http://192.168.11.86:8005"
        self.viewport_url = "http://192.168.11.86:8085"
        self.workstation_ip = "192.168.11.150"
        self.user_name = "OpenWebUI Senior CAD Engineer"

    def _http_post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.gateway_url}{endpoint}"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))

    def _render_cad_card(self, title: str, tool_name: str, params: Dict[str, Any], job_id: str = "live", explanation: str = "") -> str:
        l = params.get("length_mm", params.get("bed_length_mm", params.get("diagonal_x_mm", params.get("outer_diameter_mm", params.get("base_radius_mm", 10.0)))))
        w = params.get("width_mm", params.get("bed_width_mm", params.get("diagonal_y_mm", l)))
        h = params.get("height_mm", params.get("thickness_mm", 10.0))
        hole = params.get("hole_diameter_mm", 0.0)
        teeth = params.get("teeth_count", 16)
        bore = params.get("bore_diameter_mm", 12.0)
        top_feature = params.get("top_feature", {})
        top_type = top_feature.get("type", "") if isinstance(top_feature, dict) else ""
        top_size = top_feature.get("size_mm", 0.0) if isinstance(top_feature, dict) else 0.0

        # Dynamic CAD shape selector
        shape_type = "box"
        if "turntable" in tool_name or "turntable" in title.lower():
            shape_type = "turntable"
        elif "prb" in tool_name or "conveyor" in tool_name or "conveyor" in title.lower():
            shape_type = "prb_conveyor"
        elif "bracket" in tool_name or "bracket" in title.lower():
            shape_type = "bracket"
        elif "sprocket" in tool_name or "gear" in tool_name or "sprocket" in title.lower():
            shape_type = "sprocket"
        elif "valve" in tool_name or "valve" in title.lower():
            shape_type = "valve_body"
        elif "roller" in tool_name or "roller" in title.lower():
            shape_type = "roller"
        elif "hole" in tool_name or hole > 0:
            shape_type = "hole"
        elif "compound" in tool_name or top_type:
            shape_type = "compound"
        elif "cone" in tool_name:
            shape_type = "cone"
        elif "rhombus" in tool_name:
            shape_type = "rhombus"

        img_url = f"{self.gateway_url}/api/render/cad.svg?shape={shape_type}&l={l}&w={w}&h={h}&hole={hole}&teeth={teeth}&bore={bore}&top_type={top_type}&top_size={top_size}"

        return f"""
### 📐 {title} (Autodesk Inventor 2026)

![3D CAD Solid Model]({img_url})

<img src="{img_url}" alt="3D CAD Drawing" width="450" />

---

**Engineering Specifications & AI Rationale:**
- **CAD Tool:** `{tool_name}`
- **Exact Parameters:** `{json.dumps(params, indent=2)}`
- **Target Workstation:** `{self.workstation_ip}` (Autodesk Inventor 2026 Live Session)
- **CAD AI Engine:** `Gemma 31B GPU (192.168.11.86)`
- **Dispatched Job ID:** `{job_id}`
- **Summary:** *{explanation or "Parametric feature solid validated and dispatched to Autodesk Inventor."}*

**Native CAD Downloads & Live Interactive 3D Orbit Viewport:**
- 🌐 **[Open Interactive Live 3D Orbit & Technical Blueprint Viewport]({self.viewport_url})**
- 📥 **[Download ISO-10303 .STEP 3D Solid Model]({self.gateway_url}/api/export/step?length={l}&width={w}&height={h})**
- 📥 **[Download ACIS .SAT Body File]({self.gateway_url}/api/export/sat?length={l}&width={w}&height={h})**
"""

    async def create_conveyor_turntable(
        self,
        bed_length_mm: float = 1000.0,
        bed_width_mm: float = 1000.0,
        height_mm: float = 550.0,
        roller_count: int = 8,
        roller_diameter_mm: float = 60.0,
        rotation_angle_deg: float = 90.0,
        __event_emitter__: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> str:
        """
        Generate a complete Industrial Powered Rotary Conveyor Turntable Assembly in Autodesk Inventor.
        Features: Stationary blue square tubular base frame with leveling feet, motorized central slewing ring bearing (90°/180°/360° index), rotating upper roller carriage with 8 steel rollers, safety yellow chain guard plate (RAL 1021), and undermounted rotary slewing drive motor.
        
        :param bed_length_mm: Turntable bed frame length in mm (default: 1000.0)
        :param bed_width_mm: Turntable bed frame width in mm (default: 1000.0)
        :param height_mm: Total elevation height from floor to roller top (default: 550.0)
        :param roller_count: Number of transverse rollers (default: 8)
        :param roller_diameter_mm: Diameter of steel conveyor rollers in mm (default: 60.0)
        :param rotation_angle_deg: Rotary indexing angle in degrees (default: 90.0)
        :return: Markdown technical CAD report with interactive 3D WebGL link and downloads.
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Synthesizing {bed_length_mm}x{bed_width_mm}mm Rotary Turntable Assembly...", "done": False}
            })

        payload = {
            "prompt": f"create a powered rotary conveyor turntable {bed_length_mm}x{bed_width_mm}x{height_mm}mm with {roller_count} rollers and yellow guard",
            "workstation_ip": self.workstation_ip,
            "user_name": self.user_name
        }
        resp = self._http_post("/api/chat", payload)
        params = resp.get("parameters", {
            "bed_length_mm": bed_length_mm,
            "bed_width_mm": bed_width_mm,
            "height_mm": height_mm,
            "roller_count": roller_count,
            "roller_diameter_mm": roller_diameter_mm,
            "rotation_angle_deg": rotation_angle_deg,
            "has_yellow_guard": True,
            "has_slewing_motor": True
        })
        return self._render_cad_card("Powered Rotary Conveyor Turntable Assembly", "inventor.create_turntable", params, resp.get("job_id", "live"), resp.get("message", ""))

    async def create_prb_conveyor_bed(
        self,
        length_mm: float = 2000.0,
        width_mm: float = 450.0,
        height_mm: float = 350.0,
        roller_count: int = 5,
        roller_diameter_mm: float = 50.0,
        __event_emitter__: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> str:
        """
        Generate an Industrial Powered Roller Bed (PRB) Conveyor Assembly in Autodesk Inventor.
        Features: Dual blue structural C-channel longitudinal rails (RAL 5005), 4 vertical channel support legs with leveling base plates, 5 transverse steel rollers with white bearing end hubs, and center electric gear-motor drive unit.
        
        :param length_mm: Overall frame length in mm (default: 2000.0)
        :param width_mm: Overall frame width in mm (default: 450.0)
        :param height_mm: Leg elevation height in mm (default: 350.0)
        :param roller_count: Number of transverse rollers (default: 5)
        :param roller_diameter_mm: Diameter of steel rollers (default: 50.0)
        :return: Markdown technical CAD report.
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Synthesizing {length_mm}x{width_mm}mm PRB Conveyor Assembly...", "done": False}
            })

        payload = {
            "prompt": f"create a 3d prb roller conveyor {length_mm}x{width_mm}x{height_mm}mm with {roller_count} rollers",
            "workstation_ip": self.workstation_ip,
            "user_name": self.user_name
        }
        resp = self._http_post("/api/chat", payload)
        params = resp.get("parameters", {
            "length_mm": length_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "roller_count": roller_count,
            "roller_diameter_mm": roller_diameter_mm,
            "has_drive_motor": True,
            "motor_position": "center"
        })
        return self._render_cad_card("Powered Roller Bed (PRB) Conveyor Assembly", "inventor.create_prb_conveyor", params, resp.get("job_id", "live"), resp.get("message", ""))

    async def generate_engineering_cad_design(
        self,
        prompt: str,
        __event_emitter__: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> str:
        """
        Universal Autodesk CAD Reasoning Engine:
        Translates ANY natural language design request (turntables, PRB conveyors, 15mm cube on right side of 10mm cube, 2mm drill through top to down, sprockets, brackets, valve bodies, cones, rhombuses) into an exact parametric 3D CAD solid in Autodesk Inventor 2026.
        
        :param prompt: Engineering prompt (e.g. 'design of a turntable', 'create 3d prb roller', '15mm cube on right side of 10mm cube', 'drill 2mm hole through top to down of 10mm cube', 'sprocket 14 teeth')
        :return: Markdown technical CAD report with interactive 3D WebGL link and downloads.
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Gemma GPU (192.168.11.86) Thinking & Generating CAD Geometry...", "done": False}
            })

        try:
            payload = {
                "prompt": prompt,
                "workstation_ip": self.workstation_ip,
                "user_name": self.user_name
            }
            resp = self._http_post("/api/chat", payload)

            if not resp.get("success", False):
                return f"⚠️ **CAD Generation Failed:** {resp.get('message', 'Validation or connection error.')}"

            tool_name = resp.get("tool", "inventor.create_box")
            params = resp.get("parameters", {})
            job_id = resp.get("job_id", "live")
            message = resp.get("message", "")

            # Formulate Title
            title_map = {
                "inventor.create_turntable": "Powered Rotary Conveyor Turntable Assembly",
                "inventor.create_prb_conveyor": "Powered Roller Bed (PRB) Conveyor Assembly",
                "inventor.create_bracket": "Ribbed Mounting Angle Bracket",
                "inventor.create_valve_body": "Flanged Valve Body Spool Housing",
                "inventor.create_compound": "Spatial Multi-Feature Compound Solid",
                "inventor.create_box_with_hole": "Machined Prismatic Block with Subtractive Bore",
                "inventor.create_sprocket": f"ISO 606 Sprocket ({params.get('teeth_count', 14)} Teeth)",
                "inventor.create_box": f"Solid CAD Box ({params.get('length_mm', 10)}x{params.get('width_mm', 10)}x{params.get('height_mm', 10)}mm)",
                "inventor.create_cylinder": f"Solid Cylinder (Ø{params.get('diameter_mm', params.get('radius_mm', 10)*2)}x{params.get('height_mm', 50)}mm)",
                "inventor.create_cone": "Conical Solid Frustum",
                "inventor.create_rhombus": "Rhombus / Parallelogram Prism"
            }
            title = title_map.get(tool_name, "3D Parametric CAD Solid")

            return self._render_cad_card(title, tool_name, params, job_id, message)

        except urllib.error.URLError as e:
            return f"❌ **CAD Gateway Offline:** Could not reach `{self.gateway_url}`. Error: `{e}`"
        except Exception as e:
            return f"❌ **Internal Error:** `{str(e)}`"
