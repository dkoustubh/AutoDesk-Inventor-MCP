"""
OmniCAD Parametric Feature Graph
Enables structured, non-destructive editing of CAD features without full regeneration.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class FeatureNode(BaseModel):
    id: str
    feature_type: str  # 'cylinder', 'box', 'through_hole', 'circular_pattern', 'raised_face', 'fillet', 'chamfer'
    parameters: Dict[str, Any]
    dependencies: List[str] = []
    operation_mode: str = "ADD"  # 'ADD', 'SUBTRACT', 'INTERSECT'
    description: str = ""

class FeatureGraph(BaseModel):
    name: str = "ParametricPart"
    part_type: str = "custom"
    units: str = "mm"
    nodes: List[FeatureNode] = []
    global_parameters: Dict[str, float] = {}

    def get_node(self, node_id: str) -> Optional[FeatureNode]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def update_parameter(self, param_name: str, new_value: float) -> bool:
        """
        Updates a named parameter globally or inside a feature node.
        """
        updated = False
        p_clean = param_name.lower().replace("_mm", "")
        
        # Check global parameters
        for k in list(self.global_parameters.keys()):
            k_clean = k.lower().replace("_mm", "")
            if k_clean == p_clean or k_clean in p_clean or p_clean in k_clean:
                self.global_parameters[k] = new_value
                updated = True
        
        self.global_parameters[param_name] = new_value
        if not param_name.endswith("_mm"):
            self.global_parameters[f"{param_name}_mm"] = new_value
        updated = True

        # Check nodes
        for node in self.nodes:
            for k in list(node.parameters.keys()):
                k_clean = k.lower().replace("_mm", "")
                if k_clean == p_clean or k_clean in p_clean or p_clean in k_clean:
                    node.parameters[k] = new_value
                    updated = True
        return updated

    def to_build123d_code(self) -> str:
        """
        Synthesizes executable build123d code from the feature graph.
        """
        lines = [
            "from build123d import *",
            "import math",
            "",
            "# === Parametric Variables ==="
        ]
        for k, v in self.global_parameters.items():
            lines.append(f"{k} = {v}")
        
        lines.extend([
            "",
            "with BuildPart() as model:",
        ])
        
        for node in self.nodes:
            ft = node.feature_type
            p = node.parameters
            lines.append(f"    # Feature: {node.id} ({ft})")
            
            if ft == "cylinder":
                dia = p.get("diameter", p.get("outer_diameter_mm", 100.0))
                h = p.get("height", p.get("thickness_mm", 20.0))
                mode = "Mode.ADD" if node.operation_mode == "ADD" else "Mode.SUBTRACT"
                lines.append(f"    with BuildSketch(Plane.XY) as sk_{node.id}:")
                lines.append(f"        Circle(radius=({dia}) / 2.0)")
                lines.append(f"    extrude(amount={h}, mode={mode})")
                
            elif ft == "box":
                l = p.get("length", p.get("length_mm", 100.0))
                w = p.get("width", p.get("width_mm", 60.0))
                h = p.get("height", p.get("height_mm", 20.0))
                mode = "Mode.ADD" if node.operation_mode == "ADD" else "Mode.SUBTRACT"
                lines.append(f"    Box({l}, {w}, {h}, mode={mode})")
                
            elif ft == "through_hole":
                dia = p.get("diameter", p.get("inner_bore_mm", 50.0))
                lines.append(f"    with BuildSketch(Plane.XY.offset(-1)) as sk_{node.id}:")
                lines.append(f"        Circle(radius=({dia}) / 2.0)")
                lines.append(f"    extrude(amount=100.0, mode=Mode.SUBTRACT)")
                
            elif ft == "raised_face":
                dia = p.get("diameter", p.get("raised_face_diameter_mm", 95.0))
                h = p.get("height", p.get("raised_face_height_mm", 4.0))
                base_h = p.get("base_thickness_mm", 20.0)
                lines.append(f"    with BuildSketch(Plane.XY.offset({base_h})) as sk_{node.id}:")
                lines.append(f"        Circle(radius=({dia}) / 2.0)")
                lines.append(f"    extrude(amount={h}, mode=Mode.ADD)")
                
            elif ft == "circular_pattern":
                count = int(p.get("count", p.get("bolt_count", 6)))
                dia = p.get("hole_diameter", p.get("bolt_hole_diameter_mm", 14.0))
                pcd = p.get("pcd", p.get("bolt_pcd_mm", 120.0))
                lines.append(f"    _bolt_pts = []")
                lines.append(f"    for _i in range({count}):")
                lines.append(f"        _angle = _i * (2.0 * math.pi / {count})")
                lines.append(f"        _bolt_pts.append((({pcd}/2.0) * math.cos(_angle), ({pcd}/2.0) * math.sin(_angle)))")
                lines.append(f"    with BuildSketch(Plane.XY.offset(-1)) as sk_{node.id}:")
                lines.append(f"        with Locations(_bolt_pts):")
                lines.append(f"            Circle(radius=({dia}) / 2.0)")
                lines.append(f"    extrude(amount=100.0, mode=Mode.SUBTRACT)")
        
        return "\n".join(lines)
