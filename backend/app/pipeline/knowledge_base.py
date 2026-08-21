"""
OmniCAD Engineering Knowledge Base - Part Templates & Schemas
"""
from typing import Dict, Any, List
from pydantic import BaseModel

class ParameterRule(BaseModel):
    name: str
    param_type: str
    unit: str = "mm"
    default: Any
    min_value: Any = None
    max_value: Any = None
    description: str = ""

class PartTemplate(BaseModel):
    category: str
    part_type: str
    name: str
    standard: str = "ISO"
    description: str
    parameters: Dict[str, ParameterRule]
    required_features: List[str]
    default_features: List[Dict[str, Any]]

# Library of standard industrial parts
PART_LIBRARY: Dict[str, PartTemplate] = {
    "pipe_flange": PartTemplate(
        category="mechanical",
        part_type="pipe_flange",
        name="Industrial Pipe Flange",
        standard="ASME B16.5 / ISO 7005-1",
        description="Standard circular pipe flange with central bore, raised face, and circular bolt hole pattern.",
        parameters={
            "outer_diameter_mm": ParameterRule(name="outer_diameter_mm", param_type="float", default=150.0, min_value=20.0, max_value=2000.0, description="Outer diameter of flange disc"),
            "thickness_mm": ParameterRule(name="thickness_mm", param_type="float", default=20.0, min_value=3.0, max_value=200.0, description="Base flange disc thickness"),
            "inner_bore_mm": ParameterRule(name="inner_bore_mm", param_type="float", default=65.0, min_value=5.0, max_value=1800.0, description="Center through-bore diameter"),
            "raised_face_diameter_mm": ParameterRule(name="raised_face_diameter_mm", param_type="float", default=95.0, min_value=10.0, max_value=1900.0, description="Diameter of raised face sealing surface"),
            "raised_face_height_mm": ParameterRule(name="raised_face_height_mm", param_type="float", default=4.0, min_value=0.5, max_value=50.0, description="Extrusion height of raised face boss"),
            "bolt_pcd_mm": ParameterRule(name="bolt_pcd_mm", param_type="float", default=120.0, min_value=15.0, max_value=1950.0, description="Pitch Circle Diameter (PCD) for bolt pattern"),
            "bolt_count": ParameterRule(name="bolt_count", param_type="int", default=6, min_value=3, max_value=64, description="Number of circular pattern bolt holes"),
            "bolt_hole_diameter_mm": ParameterRule(name="bolt_hole_diameter_mm", param_type="float", default=14.0, min_value=2.0, max_value=80.0, description="Diameter of each bolt hole"),
        },
        required_features=["base_disc", "center_bore", "bolt_pattern"],
        default_features=[
            {"id": "base", "type": "cylinder", "diameter": 150.0, "height": 20.0},
            {"id": "raised_face", "type": "cylinder", "diameter": 95.0, "height": 4.0, "offset_z": 20.0},
            {"id": "bore", "type": "through_hole", "diameter": 65.0},
            {"id": "bolt_pattern", "type": "circular_pattern", "pcd": 120.0, "count": 6, "hole_diameter": 14.0}
        ]
    ),
    "mounting_plate": PartTemplate(
        category="conveyor",
        part_type="mounting_plate",
        name="Industrial Mounting Plate",
        standard="ISO 2768-m",
        description="Prismatic rectangular mounting plate with 4 corner through holes.",
        parameters={
            "length_mm": ParameterRule(name="length_mm", param_type="float", default=100.0, min_value=10.0, max_value=3000.0, description="Plate length"),
            "width_mm": ParameterRule(name="width_mm", param_type="float", default=60.0, min_value=10.0, max_value=2000.0, description="Plate width"),
            "thickness_mm": ParameterRule(name="thickness_mm", param_type="float", default=20.0, min_value=2.0, max_value=200.0, description="Plate thickness"),
            "hole_diameter_mm": ParameterRule(name="hole_diameter_mm", param_type="float", default=8.0, min_value=2.0, max_value=50.0, description="Mounting hole diameter"),
            "hole_count": ParameterRule(name="hole_count", param_type="int", default=4, min_value=1, max_value=32, description="Number of holes"),
        },
        required_features=["base_box", "hole_pattern"],
        default_features=[
            {"id": "base", "type": "box", "length": 100.0, "width": 60.0, "height": 20.0},
            {"id": "holes", "type": "linear_pattern", "count": 4, "diameter": 8.0}
        ]
    ),
    "conveyor_roller": PartTemplate(
        category="conveyor",
        part_type="conveyor_roller",
        name="Conveyor Roller Assembly",
        standard="ISO 1537 / CEMA",
        description="Industrial conveyor roller tube with stepped central shaft.",
        parameters={
            "tube_diameter_mm": ParameterRule(name="tube_diameter_mm", param_type="float", default=50.0, min_value=20.0, max_value=300.0, description="Roller tube outer diameter"),
            "tube_length_mm": ParameterRule(name="tube_length_mm", param_type="float", default=450.0, min_value=50.0, max_value=3000.0, description="Roller tube length"),
            "shaft_diameter_mm": ParameterRule(name="shaft_diameter_mm", param_type="float", default=15.0, min_value=8.0, max_value=80.0, description="Shaft extension diameter"),
            "shaft_length_mm": ParameterRule(name="shaft_length_mm", param_type="float", default=500.0, min_value=70.0, max_value=3200.0, description="Total shaft length"),
        },
        required_features=["tube", "shaft"],
        default_features=[
            {"id": "tube", "type": "cylinder", "diameter": 50.0, "height": 450.0},
            {"id": "shaft", "type": "cylinder", "diameter": 15.0, "height": 500.0}
        ]
    ),
    "drive_sprocket": PartTemplate(
        category="mechanical",
        part_type="drive_sprocket",
        name="Power Transmission Sprocket",
        standard="ISO 606 / DIN 8187",
        description="Roller chain drive sprocket with teeth, central hub, and keyway bore.",
        parameters={
            "teeth_count": ParameterRule(name="teeth_count", param_type="int", default=14, min_value=8, max_value=120, description="Number of sprocket teeth"),
            "outer_diameter_mm": ParameterRule(name="outer_diameter_mm", param_type="float", default=70.0, min_value=20.0, max_value=1000.0, description="Tip outer diameter"),
            "thickness_mm": ParameterRule(name="thickness_mm", param_type="float", default=8.0, min_value=2.0, max_value=100.0, description="Sprocket face thickness"),
            "bore_diameter_mm": ParameterRule(name="bore_diameter_mm", param_type="float", default=18.0, min_value=5.0, max_value=300.0, description="Shaft bore diameter"),
        },
        required_features=["sprocket_disc", "teeth", "bore"],
        default_features=[
            {"id": "disc", "type": "cylinder", "diameter": 70.0, "height": 8.0},
            {"id": "bore", "type": "through_hole", "diameter": 18.0}
        ]
    ),
    "ribbed_bracket": PartTemplate(
        category="structural",
        part_type="ribbed_bracket",
        name="Ribbed Mounting Bracket",
        standard="ISO 2768-m",
        description="L-shaped or ribbed structural mounting bracket for machine frame attachment.",
        parameters={
            "width_mm": ParameterRule(name="width_mm", param_type="float", default=70.0, min_value=10.0, max_value=1000.0, description="Bracket width"),
            "length_mm": ParameterRule(name="length_mm", param_type="float", default=80.0, min_value=10.0, max_value=1000.0, description="Base length"),
            "height_mm": ParameterRule(name="height_mm", param_type="float", default=55.0, min_value=10.0, max_value=1000.0, description="Vertical wall height"),
            "rib_thickness_mm": ParameterRule(name="rib_thickness_mm", param_type="float", default=10.0, min_value=2.0, max_value=100.0, description="Stiffening rib thickness"),
            "bore_diameter_mm": ParameterRule(name="bore_diameter_mm", param_type="float", default=15.0, min_value=3.0, max_value=200.0, description="Pivot or mounting bore diameter"),
        },
        required_features=["base_plate", "vertical_wall", "stiffening_rib"],
        default_features=[
            {"id": "base", "type": "box", "length": 80.0, "width": 70.0, "height": 10.0},
            {"id": "wall", "type": "box", "length": 10.0, "width": 70.0, "height": 55.0}
        ]
    )
}
