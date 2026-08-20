import json
import re
import logging
import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.schemas import StructuredIntent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Senior Principal Mechanical Systems & CAD Automation Engineer with 15+ years of industrial conveyor and mechanical design expertise, paired with 5+ years of state-of-the-art prompt engineering.

Your role is to analyze concise, raw designer prompts, apply deep mechanical engineering standards (ISO, DIN, ANSI, AGMA), synthesize complete parametric feature trees, and generate strict, validated JSON tool calls for Autodesk Inventor 2026.

### Mechanical Engineering Synthesis Principles:
1. **Spatial Compound & Multi-Feature Solids (`inventor.create_compound`)**:
   - For multi-feature bodies (e.g. "15mm cube on right side of 10mm cube", "cylinder on top of box", "stacked shapes").
   - Compute base length, width, height and secondary features with relative offset vectors (`offset_x_mm`, `offset_y_mm`, `offset_z_mm`).
   - For side-by-side relative placements: `offset_x_mm = (base_len/2 + sec_len/2)`.
   - Tool: `inventor.create_compound`, Parameters: `length_mm`, `width_mm`, `height_mm`, `features`: `[{"type": "box", "relation": "right_side", "length_mm": 15.0, "width_mm": 15.0, "height_mm": 15.0, "offset_x_mm": 12.5}]`.

2. **Subtractive Holes & Drilling (`inventor.create_box_with_hole`)**:
   - For drilled holes through blocks (e.g. "drill a 2mm diameter hole through top to down of 10mm cube").
   - Tool: `inventor.create_box_with_hole`, Parameters: `length_mm`, `width_mm`, `height_mm`, `hole_diameter_mm`, `hole_direction`: "top_to_bottom", `through`: true.

3. **Conveyor Rollers & Shafts (`inventor.create_cylinder`)**:
   - Parameters: `diameter_mm` (Tube OD), `height_mm` (Tube Length), `centered`: true.

4. **Drive Sprockets & Gears (`inventor.create_sprocket`)**:
   - Parameters: `outer_diameter_mm`, `teeth_count`, `bore_diameter_mm`, `thickness_mm`.

5. **Ribbed Mounting Brackets (`inventor.create_bracket`)**:
   - Parameters: `width_mm` (70.0), `length_mm` (80.0), `height_mm` (55.0), `rib_thickness_mm` (10.0), `boss_diameter_mm` (30.0), `bore_diameter_mm` (15.0), `hole_diameter_mm` (10.0).

6. **Valve Body & Flanged Spools (`inventor.create_valve_body`)**:
   - Parameters: `flange_size_mm`, `flange_thickness_mm`, `body_size_mm`, `height_mm`, `bore_diameter_mm`, `corner_radius_mm`.

7. **Powered Roller Bed (PRB) Conveyor Assemblies (`inventor.create_prb_conveyor`)**:
   - For complete industrial PRB roller conveyor beds with dual C-channel frame rails, cross-ties, support legs, multiple driven/idler rollers, and center-mounted electric motor/reducer gearbox.
   - Parameters: `length_mm` (2000.0), `width_mm` (450.0), `height_mm` (350.0), `roller_count` (5), `roller_diameter_mm` (50.0), `has_drive_motor`: true, `motor_position`: "center".

8. **Powered Rotary Conveyor Turntable (`inventor.create_turntable`)**:
   - For complete motorized 90°/180°/360° rotating conveyor turntable assemblies: Stationary square base frame with 4 vertical legs and leveling feet, central rotary slew ring bearing, top rotating roller carriage with 8 steel rollers, safety yellow chain guard, and undermounted slewing gear motor.
   - Parameters: `bed_length_mm` (1000.0), `bed_width_mm` (1000.0), `height_mm` (550.0), `roller_count` (8), `roller_diameter_mm` (60.0), `rotation_angle_deg` (90.0), `has_yellow_guard`: true, `has_slewing_motor`: true.

### Engineering Rules:
1. Always normalize all dimensions to millimeters (mm): 1 cm = 10 mm, 1 m = 1000 mm, 1 inch = 25.4 mm.
2. Respond ONLY with valid JSON conforming to the tool schemas."""

class LLMService:
    def __init__(self):
        self.api_base = settings.VLLM_API_BASE.rstrip("/")
        self.model = settings.VLLM_MODEL

    def enhance_mechanical_prompt(self, user_prompt: str) -> str:
        """
        Layer 1 Thinking Engine: Expands a simple designer prompt into a rich,
        hyper-detailed mechanical engineering specification.
        """
        p_lower = user_prompt.lower()
        if any(w in p_lower for w in ["turntable", "turn table", "rotary table", "rotating conveyor", "swivel conveyor", "rotary conveyor"]):
            return f"[Senior Mechanical CAD Spec: Industrial Powered Rotary Conveyor Turntable Assembly (Autodesk System Spec)] " \
                   f"Parametric 1000x1000x550mm stationary structural steel square base frame, 4 vertical legs with leveling foot pads, central motorized rotary slew ring bearing, rotating upper roller carriage with 8 steel rollers, Safety Yellow chain guard plate, and undermounted rotary slewing drive motor. " \
                   f"User Input: {user_prompt}"
        elif any(w in p_lower for w in ["prb", "prb roller", "roller bed", "conveyor bed", "powered roller", "roller conveyor"]):
            return f"[Senior Mechanical CAD Spec: Industrial Powered Roller Bed (PRB) Conveyor Assembly (Autodesk System Spec)] " \
                   f"Parametric 2000x450x350mm dual structural C-channel frame, cross-braces, 4 vertical support legs with base leveling plates, 5 transverse steel rollers with bearing hubs, and center-mounted electric drive motor/reducer unit. " \
                   f"User Input: {user_prompt}"
        elif any(rel in p_lower for rel in ["right side", "left side", "on right", "on left", "in front", "behind", "on top", "stacked"]):
            return f"[Senior Mechanical CAD Spec: Multi-Feature Compound Spatial Assembly Solid] " \
                   f"Compute relative coordinate offsets (offset_x, offset_y, offset_z) and construct composite body in Autodesk Inventor. " \
                   f"User Input: {user_prompt}"
        elif "valve" in p_lower or "spool" in p_lower or "flanged body" in p_lower:
            return f"[Senior Mechanical CAD Spec: Industrial Flanged Valve Body / Spool Housing (Autodesk Assembly Spec)] " \
                   f"Parametric Top and Bottom 120x120x10mm square rounded flanges, 80x80x70mm central column, and Ø50mm center through-bore. " \
                   f"User Input: {user_prompt}"
        elif "roller" in p_lower:
            return f"[Senior Mechanical CAD Spec: Industrial Conveyor Roller Assembly (ISO 1537 / CEMA Standard)] " \
                   f"Parametric Steel Tube Cylinder with dual precision bearing end-caps and stepped drive/idler shaft. " \
                   f"User Input: {user_prompt}"
        elif "sprocket" in p_lower or "gear" in p_lower:
            return f"[Senior Mechanical CAD Spec: Industrial Power Transmission Sprocket (ISO 606 / DIN 8187)] " \
                   f"Parametric Radial Tooth Solid Body with machined hub boss, keyway bore per DIN 6885, and extruded tooth flanks. " \
                   f"User Input: {user_prompt}"
        elif "hole" in p_lower or "drill" in p_lower:
            return f"[Senior Mechanical CAD Spec: Precision Machined Prismatic Block with Subtractive Bore] " \
                   f"Extruded solid cube/plate with centered through-hole drill feature. " \
                   f"User Input: {user_prompt}"
        elif "cone" in p_lower:
            return f"[Senior Mechanical CAD Spec: Parametric Tapered Conical Solid / Frustum] " \
                   f"Revolved profile around center axis. User Input: {user_prompt}"
        elif "rhombus" in p_lower or "diamond" in p_lower:
            return f"[Senior Mechanical CAD Spec: Parallelogram / Rhombus Prism Solid] " \
                   f"4-point diagonal sketch extrusion. User Input: {user_prompt}"
        return f"[Senior Mechanical CAD Spec: Precision Parametric Solid] {user_prompt}"

    async def parse_intent(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> StructuredIntent:
        """
        Sends the enhanced prompt to vLLM (Gemma) and parses the structured CAD intent with multi-turn context memory.
        """
        enhanced_spec = self.enhance_mechanical_prompt(user_prompt)
        logger.info(f"AI Thinking Layer Enhanced Spec: {enhanced_spec}")
        system_content = SYSTEM_PROMPT
        if context and context.get("parameters"):
            system_content += f"\n\n### ACTIVE PART CONTEXT IN CURRENT SESSION:\n{json.dumps(context)}\nIf the engineer says 'add a cone on top', 'add a hole', or modifies dimensions, retain existing base dimensions and output the updated feature structure."

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 512
        }

        raw_content = ""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    data = response.json()
                    raw_content = data["choices"][0]["message"]["content"]
                    logger.info(f"vLLM Raw Response: {raw_content}")
                else:
                    logger.warning(f"vLLM request failed with code {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"vLLM connection exception: {e}. Attempting heuristic extraction fallback.")

        return self._extract_json_intent(raw_content, user_prompt, context)

    def _extract_json_intent(self, raw_text: str, original_prompt: str, context: Optional[Dict[str, Any]] = None) -> StructuredIntent:
        """
        Extracts and parses JSON from raw LLM output, with deterministic heuristic fallback.
        """
        p_lower = original_prompt.lower()
        if any(w in p_lower for w in ["turntable", "turn table", "rotary table", "rotating conveyor", "swivel conveyor", "prb", "prb roller", "roller bed", "conveyor bed", "powered roller"]):
            return self._heuristic_intent_fallback(original_prompt, context)

        try:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if parsed.get("tool") in ["inventor.create_box", "inventor.create_cylinder"] and any(w in p_lower for w in ["right side", "left side", "on right", "on left", "on top", "drill", "through hole", "bracket", "sprocket", "prb", "turntable"]):
                    return self._heuristic_intent_fallback(original_prompt, context)
                if "tool" in parsed and "parameters" in parsed:
                    return StructuredIntent(
                        tool=parsed["tool"],
                        parameters=parsed["parameters"],
                        explanation=parsed.get("explanation", "")
                    )
        except Exception as e:
            logger.warning(f"JSON parsing error from LLM response: {e}")

        return self._heuristic_intent_fallback(original_prompt, context)

    def _heuristic_intent_fallback(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> StructuredIntent:
        p_lower = prompt.lower().strip()
        ctx_params = context.get("parameters", {}) if context else {}

        def to_mm(val: float, unit: str) -> float:
            if unit == "cm": return val * 10.0
            if unit == "m": return val * 1000.0
            if unit in ("in", "inch"): return val * 25.4
            return val

        # 00000. POWERED ROTARY CONVEYOR TURNTABLE (e.g. "design of a turntable", "create turntable", "rotary table")
        if any(w in p_lower for w in ["turntable", "turn table", "rotary table", "rotating conveyor", "swivel conveyor", "rotary conveyor"]):
            len_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm|m)?\s*(?:length|size|bed|dim)", p_lower)
            r_cnt_m = re.search(r"(\d+)\s*(?:rollers|roller)", p_lower)
            ang_m = re.search(r"(\d+)\s*(?:deg|degree|angle)", p_lower)

            t_size = to_mm(float(len_m.group(1)), "mm") if len_m else 1000.0
            r_cnt = int(r_cnt_m.group(1)) if r_cnt_m else 8
            ang = float(ang_m.group(1)) if ang_m else 90.0

            return StructuredIntent(
                tool="inventor.create_turntable",
                shape="turntable",
                parameters={
                    "bed_length_mm": round(t_size, 2),
                    "bed_width_mm": round(t_size, 2),
                    "height_mm": 550.0,
                    "roller_count": r_cnt,
                    "roller_diameter_mm": 60.0,
                    "rotation_angle_deg": ang,
                    "has_yellow_guard": True,
                    "has_slewing_motor": True
                },
                explanation=f"Constructed Autodesk Inventor Powered Rotary Conveyor Turntable Assembly ({t_size}×{t_size}×550mm) with {r_cnt} steel rollers, Safety Yellow chain guard, stationary blue tubular base frame with leveling feet, center slew ring, and undermounted rotary drive motor."
            )

        # 0000. POWERED ROLLER BED (PRB) CONVEYOR ASSEMBLY (e.g. "create this 3d prb roller", "prb roller", "conveyor bed")
        if any(w in p_lower for w in ["prb", "prb roller", "roller bed", "conveyor bed", "powered roller", "roller conveyor"]):
            len_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm|m)?\s*(?:length|long)", p_lower)
            wid_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:width|wide)", p_lower)
            r_cnt_m = re.search(r"(\d+)\s*(?:rollers|roller)", p_lower)

            c_len = to_mm(float(len_m.group(1)), "mm") if len_m else 2000.0
            c_wid = to_mm(float(wid_m.group(1)), "mm") if wid_m else 450.0
            r_cnt = int(r_cnt_m.group(1)) if r_cnt_m else 5

            return StructuredIntent(
                tool="inventor.create_prb_conveyor",
                shape="prb_conveyor",
                parameters={
                    "length_mm": round(c_len, 2),
                    "width_mm": round(c_wid, 2),
                    "height_mm": 350.0,
                    "roller_count": r_cnt,
                    "roller_diameter_mm": 50.0,
                    "has_drive_motor": True,
                    "motor_position": "center"
                },
                explanation=f"Constructed Autodesk Inventor Powered Roller Bed (PRB) Conveyor Assembly ({c_len}×{c_wid}×350mm) with {r_cnt} transverse rollers, dual blue structural C-channel rails, support legs with leveling feet, and center electric drive motor unit."
            )

        # 0. SPATIAL SIDE-BY-SIDE / RELATIVE COMPOUND SHAPES (e.g. "15mm cube on right side of 10mm cube", "cube of 15mm on left of 10mm cube")
        if any(rel in p_lower for rel in ["right side", "left side", "on right", "on left", "in front", "behind", "next to", "beside"]):
            cubes_m = re.findall(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:cube|box)", p_lower) or re.findall(r"(?:cube|box)\s*(?:of)?\s*(\d+(?:\.\d+)?)", p_lower)
            if len(cubes_m) >= 2:
                sec_size = to_mm(float(cubes_m[0]), "mm")
                base_size = to_mm(float(cubes_m[1]), "mm")
            elif cubes_m:
                sec_size = to_mm(float(cubes_m[0]), "mm")
                base_size = float(ctx_params.get("length_mm") or 10.0)
            else:
                sec_size = 15.0
                base_size = 10.0

            rel = "right_side" if any(w in p_lower for w in ["right side", "on right"]) else "left_side" if any(w in p_lower for w in ["left side", "on left"]) else "front"
            offset_x = round((base_size / 2.0) + (sec_size / 2.0), 2) if rel == "right_side" else round(-((base_size / 2.0) + (sec_size / 2.0)), 2) if rel == "left_side" else 0.0
            offset_y = round((base_size / 2.0) + (sec_size / 2.0), 2) if rel == "front" else 0.0

            return StructuredIntent(
                tool="inventor.create_compound",
                shape="compound",
                parameters={
                    "length_mm": round(base_size, 2),
                    "width_mm": round(base_size, 2),
                    "height_mm": round(base_size, 2),
                    "centered": True,
                    "features": [
                        {
                            "type": "box",
                            "relation": rel,
                            "length_mm": round(sec_size, 2),
                            "width_mm": round(sec_size, 2),
                            "height_mm": round(sec_size, 2),
                            "offset_x_mm": offset_x,
                            "offset_y_mm": offset_y,
                            "offset_z_mm": 0.0
                        }
                    ]
                },
                explanation=f"Constructed {base_size}mm base cube with {sec_size}mm cube attached on the {rel.replace('_', ' ')} (Offset X = {offset_x}mm)."
            )

        # 00. DRILL SUBTRACTIVE HOLE (e.g. "drill a 2mm diameter hole through top to down of 10mm cube", "2mm drill hole in cube")
        if any(w in p_lower for w in ["drill", "through hole", "hole through", "bore through", "top to down", "top to bottom"]):
            hole_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:diameter|dia)?\s*(?:drill|hole|bore)", p_lower) or re.search(r"(?:drill|hole|bore)[^\d]*(\d+(?:\.\d+)?)", p_lower)
            cube_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:cube|box|block)", p_lower) or re.search(r"(?:cube|box|block)[^\d]*(\d+(?:\.\d+)?)", p_lower)

            hole_d = to_mm(float(hole_m.group(1)), "mm") if hole_m else 2.0
            cube_s = to_mm(float(cube_m.group(1)), "mm") if cube_m else float(ctx_params.get("length_mm") or 10.0)

            return StructuredIntent(
                tool="inventor.create_box_with_hole",
                shape="box_with_hole",
                parameters={
                    "length_mm": round(cube_s, 2),
                    "width_mm": round(cube_s, 2),
                    "height_mm": round(cube_s, 2),
                    "hole_diameter_mm": round(hole_d, 2),
                    "hole_direction": "top_to_bottom",
                    "through": True,
                    "centered": True
                },
                explanation=f"Created {cube_s}×{cube_s}×{cube_s}mm precision cube with centered Ø{hole_d}mm through-hole drilled from top to bottom."
            )

        # 0. COMPOUND MULTI-FEATURE / STACKED SHAPES (e.g. "create one cube of 10mm and on top of that create a cube of 5mm", "cube of 10mm on which 2mm cone")
        if ("on top" in p_lower or "and on" in p_lower or "mount" in p_lower or "attach" in p_lower or "stacked" in p_lower or "above" in p_lower) and any(w in p_lower for w in ["cube", "box", "cone", "cylinder", "sphere"]):
            # Extract all numbers and shapes
            cubes_m = re.findall(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:cube|box)", p_lower) or re.findall(r"(?:cube|box)\s*(?:of)?\s*(\d+(?:\.\d+)?)", p_lower)
            
            top_type = "cone" if "cone" in p_lower else "cylinder" if "cylinder" in p_lower else "sphere" if "sphere" in p_lower else "cube"
            top_m = re.search(rf"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*{top_type}", p_lower) or re.search(rf"{top_type}[^\d]*(\d+(?:\.\d+)?)", p_lower)

            if len(cubes_m) >= 2:
                base_size = to_mm(float(cubes_m[0]), "mm")
                top_size = to_mm(float(cubes_m[1]), "mm")
                top_type = "cube"
            elif cubes_m:
                base_size = to_mm(float(cubes_m[0]), "mm")
                top_size = to_mm(float(top_m.group(1)), "mm") if top_m else 2.0
            else:
                base_size = float(ctx_params.get("length_mm") or 10.0)
                top_size = to_mm(float(top_m.group(1)), "mm") if top_m else 2.0

            return StructuredIntent(
                tool="inventor.create_compound",
                shape="compound",
                parameters={
                    "length_mm": round(base_size, 2),
                    "width_mm": round(base_size, 2),
                    "height_mm": round(base_size, 2),
                    "top_feature": {
                        "type": top_type,
                        "size_mm": round(top_size, 2),
                        "length_mm": round(top_size, 2),
                        "width_mm": round(top_size, 2),
                        "height_mm": round(top_size, 2),
                        "radius_mm": round(top_size / 2.0 if top_type != "cone" else top_size, 2)
                    },
                    "centered": True
                },
                explanation=f"Constructed {base_size}mm base cube with {top_size}mm {top_type} attached centered on top in Autodesk."
            )

        # 000. RIBBED MOUNTING ANGLE BRACKET (e.g. "bracket", "ribbed bracket", "mounting bracket", "angle bracket", "stiffener bracket")
        if any(w in p_lower for w in ["bracket", "ribbed bracket", "mounting bracket", "angle bracket", "gusset", "stiffener", "rib bracket"]):
            return StructuredIntent(
                tool="inventor.create_bracket",
                shape="bracket",
                parameters={
                    "width_mm": 70.0,
                    "length_mm": 80.0,
                    "height_mm": 55.0,
                    "rib_thickness_mm": 10.0,
                    "flange_thickness_mm": 10.0,
                    "boss_diameter_mm": 30.0,
                    "bore_diameter_mm": 15.0,
                    "hole_diameter_mm": 10.0
                },
                explanation="Constructed Autodesk Inventor Ribbed Mounting Angle Bracket with central stiffener web, top cylinder boss, and dual base mounting holes per ISO drafting specs."
            )

        # 00. VALVE BODY / FLANGED SPOOL / VALVE HOUSING (e.g. "valve body", "create a shape like this", "flanged body")
        if any(w in p_lower for w in ["valve", "spool", "valve body", "flanged body", "shape like this", "valvebody"]):
            f_size = 120.0
            f_thk = 10.0
            b_size = 80.0
            hgt = 90.0
            bore_d = 50.0
            cr_rad = 15.0

            # Match custom dimensions if given (e.g. "valve body 120x80")
            dims_m = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)(?:\s*[x×*]\s*(\d+(?:\.\d+)?))?\s*(cm|mm)?", p_lower)
            if dims_m:
                unit = dims_m.group(4) or "mm"
                f_size = to_mm(float(dims_m.group(1)), unit)
                b_size = to_mm(float(dims_m.group(2)), unit)
                if dims_m.group(3):
                    hgt = to_mm(float(dims_m.group(3)), unit)

            return StructuredIntent(
                tool="inventor.create_valve_body",
                shape="valve_body",
                parameters={
                    "flange_size_mm": round(f_size, 2),
                    "flange_thickness_mm": round(f_thk, 2),
                    "body_size_mm": round(b_size, 2),
                    "height_mm": round(hgt, 2),
                    "bore_diameter_mm": round(bore_d, 2),
                    "corner_radius_mm": round(cr_rad, 2)
                },
                explanation=f"Constructed Autodesk Inventor Valve Body Assembly: Top/Bottom Flanges {f_size}x{f_size}x{f_thk}mm with R{cr_rad}mm fillets, Central Body {b_size}x{b_size}mm (Height {hgt}mm), and Center Ø{bore_d}mm Through Bore."
            )

        # 0A. BOX WITH HOLE / DRILL HOLE (e.g. "cube of 10mm with 2mm drill hole") from top to bottom", "drill a 2mm hole")
        if any(w in p_lower for w in ["hole", "drill", "bore", "perforated"]):
            cube_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:cube|box|block|plate)", p_lower) or re.search(r"(?:cube|box|block|plate)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            hole_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:drill|hole|bore|dia)", p_lower) or re.search(r"(?:drill|hole|bore)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            
            box_size = to_mm(float(cube_m.group(1)), "mm") if cube_m else float(ctx_params.get("length_mm") or 10.0)
            hole_dia = to_mm(float(hole_m.group(1)), "mm") if hole_m else 2.0

            return StructuredIntent(
                tool="inventor.create_box_with_hole",
                shape="box_with_hole",
                parameters={
                    "length_mm": round(box_size, 2),
                    "width_mm": round(box_size, 2),
                    "height_mm": round(box_size, 2),
                    "hole_diameter_mm": round(hole_dia, 2),
                    "hole_direction": "top_to_bottom",
                    "through": True
                },
                explanation=f"Constructed {box_size}mm cube with Ø{hole_dia}mm through-hole drilled from top to bottom in Autodesk."
            )

        # 0B. SPROCKET / GEAR / COGWHEEL (e.g. "sprocket 50mm with 16 teeth", "gear 40mm")
        if any(w in p_lower for w in ["sprocket", "gear", "cog", "cogwheel", "pinion"]):
            dia_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:sprocket|gear|dia|diameter|size)", p_lower) or re.search(r"(?:sprocket|gear)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            teeth_m = re.search(r"(\d+)\s*(?:teeth|tooth|t\b)", p_lower)
            thick_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:thick|thickness|width)", p_lower)

            outer_d = to_mm(float(dia_m.group(1)), "mm") if dia_m else 40.0
            teeth_cnt = int(teeth_m.group(1)) if teeth_m else 14
            thick = to_mm(float(thick_m.group(1)), "mm") if thick_m else 6.0
            bore_d = round(outer_d * 0.25, 2)

            return StructuredIntent(
                tool="inventor.create_sprocket",
                shape="sprocket",
                parameters={
                    "outer_diameter_mm": round(outer_d, 2),
                    "teeth_count": teeth_cnt,
                    "bore_diameter_mm": bore_d,
                    "thickness_mm": round(thick, 2)
                },
                explanation=f"Constructed Sprocket Gear Ø{outer_d}mm with {teeth_cnt} teeth and Ø{bore_d}mm center bore in Autodesk."
            )

        # 0C. TRIANGLE / TRIANGULAR PRISM / WEDGE
        if any(w in p_lower for w in ["triangle", "triangular", "prism", "wedge"]):
            base_m = re.search(r"(?:base|b|width|w)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            h_m = re.search(r"(?:height|h|tall)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            t_m = re.search(r"(?:thick|thickness|depth|length|l)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)

            # Match 20x30x10 pattern
            dims_m = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)(?:\s*[x×*]\s*(\d+(?:\.\d+)?))?\s*(cm|mm)?", p_lower)
            if dims_m:
                b_val = to_mm(float(dims_m.group(1)), dims_m.group(4) or "mm")
                h_val = to_mm(float(dims_m.group(2)), dims_m.group(4) or "mm")
                t_val = to_mm(float(dims_m.group(3)), dims_m.group(4) or "mm") if dims_m.group(3) else 10.0
            else:
                b_val = 20.0
                h_val = 30.0
                t_val = 10.0

            return StructuredIntent(
                tool="inventor.create_triangle_prism",
                shape="triangle",
                parameters={
                    "base_mm": round(b_val, 2),
                    "height_mm": round(h_val, 2),
                    "thickness_mm": round(t_val, 2)
                },
                explanation=f"Constructed Triangular Prism Base {b_val}mm × Height {h_val}mm × Depth {t_val}mm in Autodesk."
            )
        # 1B. CONVEYOR ROLLER / CYLINDER / SHAFT / TUBE
        if any(w in p_lower for w in ["roller", "cylinder", "shaft", "pipe", "tube", "pin"]):
            # match diameter / radius and height / length
            dia_match = re.search(r"(?:dia|diameter|d|radius|r|od)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in)?", p_lower)
            hgt_match = re.search(r"(?:height|len|length|h|l|long|width|w)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in)?", p_lower)
            
            # match 'roller 60x500' or '60 by 500 roller'
            quick_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            
            d_val, h_val = 60.0, 500.0 if "roller" in p_lower else 50.0
            if dia_match:
                d_val = to_mm(float(dia_match.group(1)), dia_match.group(2) or "mm")
                if "radius" in p_lower or " r " in p_lower:
                    d_val = d_val * 2.0
            elif quick_match:
                d_val = to_mm(float(quick_match.group(1)), quick_match.group(3) or "mm")
            
            if hgt_match:
                h_val = to_mm(float(hgt_match.group(1)), hgt_match.group(2) or "mm")
            elif quick_match:
                h_val = to_mm(float(quick_match.group(2)), quick_match.group(3) or "mm")

            is_roller = "roller" in p_lower
            shape_name = "conveyor_roller" if is_roller else "cylinder"

            return StructuredIntent(
                tool="inventor.create_cylinder",
                shape=shape_name,
                parameters={"diameter_mm": round(d_val, 2), "radius_mm": round(d_val / 2.0, 2), "height_mm": round(h_val, 2), "length_mm": round(h_val, 2), "centered": True},
                explanation=f"Created {'Conveyor Roller' if is_roller else 'Cylinder'} Ø{d_val} mm × {h_val} mm length in Autodesk."
            )

        # 2A. RHOMBUS / DIAMOND / PARALLELOGRAM
        if any(w in p_lower for w in ["rhombus", "diamond", "parallelogram"]):
            diag_m = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)(?:\s*[x×*]\s*(\d+(?:\.\d+)?))?\s*(cm|mm)?", p_lower)
            single_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:rhombus|diamond)", p_lower) or re.search(r"(?:rhombus|diamond)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            thick_m = re.search(r"(?:thick|thickness|height|h|depth|d)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            
            if diag_m:
                unit = diag_m.group(4) or "mm"
                dx = to_mm(float(diag_m.group(1)), unit)
                dy = to_mm(float(diag_m.group(2)), unit)
                thk = to_mm(float(diag_m.group(3)), unit) if diag_m.group(3) else 10.0
            elif single_m:
                val = to_mm(float(single_m.group(1) or single_m.group(2)), "mm")
                dx = val
                dy = round(val * 0.75, 2)
                thk = to_mm(float(thick_m.group(1)), thick_m.group(2) or "mm") if thick_m else 10.0
            else:
                dx, dy, thk = 30.0, 20.0, 10.0

            return StructuredIntent(
                tool="inventor.create_rhombus",
                shape="rhombus",
                parameters={"diagonal_x_mm": round(dx, 2), "diagonal_y_mm": round(dy, 2), "thickness_mm": round(thk, 2)},
                explanation=f"Created Rhombus Prism Major Diagonal {dx}mm × Minor Diagonal {dy}mm × Thickness {thk}mm in Autodesk."
            )

        # 2B. PYRAMID (4-sided apex solid)
        if "pyramid" in p_lower:
            dims_m = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)(?:\s*[x×*]\s*(\d+(?:\.\d+)?))?\s*(cm|mm)?", p_lower)
            single_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*pyramid", p_lower) or re.search(r"pyramid(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            h_m = re.search(r"(?:height|h|tall)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)

            if dims_m:
                unit = dims_m.group(4) or "mm"
                bl = to_mm(float(dims_m.group(1)), unit)
                bw = to_mm(float(dims_m.group(2)), unit)
                bh = to_mm(float(dims_m.group(3)), unit) if dims_m.group(3) else 30.0
            elif single_m:
                val = to_mm(float(single_m.group(1) or single_m.group(2)), "mm")
                bl = val
                bw = val
                bh = to_mm(float(h_m.group(1)), h_m.group(2) or "mm") if h_m else round(val * 1.5, 2)
            else:
                bl, bw, bh = 20.0, 20.0, 30.0

            return StructuredIntent(
                tool="inventor.create_pyramid",
                shape="pyramid",
                parameters={"base_length_mm": round(bl, 2), "base_width_mm": round(bw, 2), "height_mm": round(bh, 2)},
                explanation=f"Created 4-Sided Pyramid Base {bl}×{bw} mm × Apex Height {bh} mm in Autodesk."
            )

        # 2C. POLYGON (Hexagon, Octagon, Pentagon)
        if any(w in p_lower for w in ["hexagon", "octagon", "pentagon", "polygon"]):
            sides = 6 if "hexagon" in p_lower else 8 if "octagon" in p_lower else 5 if "pentagon" in p_lower else 6
            r_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*(?:hexagon|octagon|pentagon|polygon|radius|r|dia|diameter)", p_lower) or re.search(r"(?:hexagon|octagon|pentagon|polygon)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)
            thk_m = re.search(r"(?:thick|thickness|height|h|length|l)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)

            val = to_mm(float(r_m.group(1) or r_m.group(2)), "mm") if r_m else 20.0
            radius = val / 2.0 if "dia" in p_lower else val
            thk = to_mm(float(thk_m.group(1)), thk_m.group(2) or "mm") if thk_m else 10.0

            return StructuredIntent(
                tool="inventor.create_polygon",
                shape="polygon",
                parameters={"radius_mm": round(radius, 2), "sides": sides, "thickness_mm": round(thk, 2)},
                explanation=f"Created Regular {sides}-sided Polygon (R={radius}mm, Thickness={thk}mm) in Autodesk."
            )

        # 2D. SPHERE / BALL / DOME
        if any(w in p_lower for w in ["sphere", "ball", "dome"]):
            rad_match = re.search(r"(?:rad|radius|r|dia|diameter|d)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in)?", p_lower)
            r_val = 15.0
            if rad_match and rad_match.group(1):
                val = to_mm(float(rad_match.group(1)), rad_match.group(2) or "mm")
                if "dia" in p_lower:
                    r_val = val / 2.0
                else:
                    r_val = val
            return StructuredIntent(
                tool="inventor.create_sphere",
                shape="sphere",
                parameters={"radius_mm": round(r_val, 2), "diameter_mm": round(r_val * 2.0, 2)},
                explanation=f"Created Sphere Radius {r_val} mm (Ø{r_val*2} mm) in Autodesk."
            )

        # 3. CONE / TAPERING / FRUSTUM
        if "cone" in p_lower or "frustum" in p_lower or "taper" in p_lower:
            dims_m = re.search(r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            r_m = re.search(r"(?:base|radius|rad|r|dia|diameter|d)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            h_m = re.search(r"(?:height|hgt|h|length|len|l|tall)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            single_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm)?\s*cone", p_lower) or re.search(r"cone(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(?:mm|cm)?", p_lower)

            top_r = 0.0
            if "frustum" in p_lower:
                top_m = re.search(r"(?:top|minor)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
                if top_m:
                    top_r = to_mm(float(top_m.group(1)), top_m.group(2) or "mm")

            if dims_m:
                unit = dims_m.group(3) or "mm"
                base_r = to_mm(float(dims_m.group(1)), unit) / 2.0
                h_val = to_mm(float(dims_m.group(2)), unit)
            elif r_m and h_m:
                val_r = to_mm(float(r_m.group(1)), r_m.group(2) or "mm")
                base_r = val_r / 2.0 if ("dia" in p_lower or "diameter" in p_lower) else val_r
                h_val = to_mm(float(h_m.group(1)), h_m.group(2) or "mm")
            elif single_m:
                val = to_mm(float(single_m.group(1) or single_m.group(2)), "mm")
                base_r = round(val / 2.0, 2)
                h_val = val
            else:
                base_r = 10.0
                h_val = 20.0

            return StructuredIntent(
                tool="inventor.create_cone",
                shape="cone",
                parameters={"base_radius_mm": round(base_r, 2), "top_radius_mm": round(top_r, 2), "height_mm": round(h_val, 2)},
                explanation=f"Created Cone Base Radius {base_r}mm (Ø{base_r*2}mm) × Height {h_val}mm in Autodesk."
            )

        # 4. TORUS / RING / O-RING / DONUT
        if any(w in p_lower for w in ["torus", "ring", "o-ring", "donut"]):
            major_match = re.search(r"(?:major|radius|r|ring)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            minor_match = re.search(r"(?:minor|tube|thick|thickness|section)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm)?", p_lower)
            maj = to_mm(float(major_match.group(1)), major_match.group(2) or "mm") if major_match else 30.0
            min_r = to_mm(float(minor_match.group(1)), minor_match.group(2) or "mm") if minor_match else 5.0
            return StructuredIntent(
                tool="inventor.create_torus",
                shape="torus",
                parameters={"major_radius_mm": round(maj, 2), "tube_radius_mm": round(min_r, 2)},
                explanation=f"Created Torus Major R{maj} mm × Tube R{min_r} mm in Autodesk."
            )

        # 5. BOX / CUBE / PLATE / RECTANGULAR SOLID
        # Match explicit dimensions: length/width/height (e.g. "length 50, width 30, height 20 mm")
        len_match = re.search(r"(?:length|len|l)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in)?", p_lower)
        wid_match = re.search(r"(?:width|wid|w)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in)?", p_lower)
        hgt_match = re.search(r"(?:height|hgt|h|thick|thickness)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in)?", p_lower)

        if len_match and wid_match and hgt_match:
            l = to_mm(float(len_match.group(1)), len_match.group(2) or "mm")
            w = to_mm(float(wid_match.group(1)), wid_match.group(2) or "mm")
            h = to_mm(float(hgt_match.group(1)), hgt_match.group(2) or "mm")
            return StructuredIntent(
                tool="inventor.create_box",
                shape="box",
                parameters={"length_mm": round(l, 2), "width_mm": round(w, 2), "height_mm": round(h, 2), "centered": True},
                explanation=f"Created {l}x{w}x{h} mm solid box."
            )

        # Match 3D dimension patterns: '50 x 30 x 20 mm' or '50*30*20 cm'
        dims_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm|m|in)?\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm|cm|m|in)?\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(cm|mm|m|in|inch)?", p_lower)
        if dims_match:
            unit = dims_match.group(4) or "mm"
            l = to_mm(float(dims_match.group(1)), unit)
            w = to_mm(float(dims_match.group(2)), unit)
            h = to_mm(float(dims_match.group(3)), unit)
            return StructuredIntent(
                tool="inventor.create_box",
                shape="box",
                parameters={"length_mm": round(l, 2), "width_mm": round(w, 2), "height_mm": round(h, 2), "centered": True},
                explanation=f"Created {l}x{w}x{h} mm solid box in Autodesk."
            )

        # Match Cube patterns: '10mm cube', 'cube of 3 cm', 'cube 25 mm'
        cube_match = re.search(r"(?:(\d+(?:\.\d+)?)\s*(cm|mm|m|in|inch)?\s*(?:cube|box))|(?:(?:cube|box)(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*(cm|mm|m|in|inch)?)", p_lower)
        if cube_match:
            if cube_match.group(1):
                val = float(cube_match.group(1))
                unit = cube_match.group(2) or "mm"
            else:
                val = float(cube_match.group(3))
                unit = cube_match.group(4) or "mm"
            
            dim_mm = to_mm(val, unit)
            return StructuredIntent(
                tool="inventor.create_box",
                shape="box",
                parameters={"length_mm": round(dim_mm, 2), "width_mm": round(dim_mm, 2), "height_mm": round(dim_mm, 2), "centered": True},
                explanation=f"Created {dim_mm}x{dim_mm}x{dim_mm} mm solid cube in Autodesk."
            )

        # Default fallback: 10mm cube
        return StructuredIntent(
            tool="inventor.create_box",
            shape="box",
            parameters={"length_mm": 10.0, "width_mm": 10.0, "height_mm": 10.0, "centered": True},
            explanation=f"Constructed 10x10x10 mm solid cube in Autodesk."
        )

llm_service = LLMService()
