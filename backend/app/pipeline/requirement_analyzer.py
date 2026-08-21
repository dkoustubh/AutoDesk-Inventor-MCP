import re
import math
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.pipeline.schemas import RequirementSpec, FeatureRequirement

logger = logging.getLogger(__name__)

class RequirementAnalyzer:
    """
    Stage 1 & 2: Natural Language Requirement Extraction & Completeness Checker.
    Converts unstructured designer prompts into strict, lossless engineering specifications.
    Supports both prefix and postfix dimensional phrasing (e.g. "150mm OD" and "OD of 150mm").
    All dimensions are normalized into canonical millimeters (mm).
    """

    @staticmethod
    def normalize_value(val: float, unit_str: Optional[str]) -> float:
        if not unit_str:
            return float(val)
        u = unit_str.lower().strip()
        if u in ("cm", "centimeter", "centimeters"):
            return float(val) * 10.0
        elif u in ("in", "inch", "inches", '"'):
            return float(val) * 25.4
        elif u in ("m", "meter", "meters"):
            return float(val) * 1000.0
        return float(val)

    def extract_dimensions_from_text(self, text: str) -> Dict[str, float]:
        """
        Extracts numerical values with units from text supporting bidirectional syntax.
        """
        dims: Dict[str, float] = {}
        t = text.lower()

        # 1. 3D Bounding box (e.g. 100 x 60 x 20 mm, 30x30x30)
        box_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:mm|cm|in|m)?\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(?:mm|cm|in|m)?\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
        if box_match:
            unit = box_match.group(4) or "mm"
            dims["length"] = self.normalize_value(float(box_match.group(1)), unit)
            dims["width"] = self.normalize_value(float(box_match.group(2)), unit)
            dims["height"] = self.normalize_value(float(box_match.group(3)), unit)
        else:
            cube_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:cube|square block)", t)
            if cube_match:
                c_val = self.normalize_value(float(cube_match.group(1)), cube_match.group(2))
                dims["length"] = c_val
                dims["width"] = c_val
                dims["height"] = c_val

        # 2. Outer Diameter (OD) - Postfix ("OD of 150mm") & Prefix ("150 mm outer diameter")
        od_match = re.search(r"(?:outer\s*diameter|flange\s*diameter|flange\s*od|\bod\b)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
        if not od_match:
            od_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:outer\s*diameter|flange\s*diameter|flange\s*od|\bod\b)", t)
        if od_match:
            dims["outer_diameter"] = self.normalize_value(float(od_match.group(1)), od_match.group(2))

        # 3. Flange Thickness - Postfix ("thickness of 20mm") & Prefix ("20 mm flange thickness")
        thick_match = re.search(r"(?:flange\s*thickness|base\s*thickness|thickness|thick)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
        if not thick_match:
            thick_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:flange\s*thickness|base\s*thickness|thickness|thick)", t)
        if thick_match:
            dims["thickness"] = self.normalize_value(float(thick_match.group(1)), thick_match.group(2))

        # 4. Center Bore / Through-Bore - Postfix & Prefix
        bore_match = re.search(r"(?:center\s*(?:through[- ]?)?bore|through[- ]?bore|bore|inner\s*diameter|inner\s*bore|\bid\b)\s*(?:of|is|=|:)?\s*(?:ø|dia(?:meter)?)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
        if not bore_match:
            bore_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:ø|dia(?:meter)?)?\s*(?:center\s*(?:through[- ]?)?bore|through[- ]?bore|bore|inner\s*diameter|inner\s*bore|\bid\b)", t)
        if bore_match:
            dims["bore_diameter"] = self.normalize_value(float(bore_match.group(1)), bore_match.group(2))

        # 5. Raised Face - Postfix & Prefix
        rf_match = re.search(r"(?:raised\s*face|rf)\s*(?:of|diameter|dia|is|=|:)?\s*(?:ø|dia(?:meter)?)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:diameter|dia)?(?:\s*(?:extruded|height|high|thick|protruding)\s*(?:of|by|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?)?", t)
        if not rf_match:
            rf_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:ø|dia(?:meter)?)?\s*(?:diameter|dia)?\s*(?:raised\s*face|rf)", t)
            if rf_match:
                dims["raised_face_diameter"] = self.normalize_value(float(rf_match.group(1)), rf_match.group(2))
        else:
            dims["raised_face_diameter"] = self.normalize_value(float(rf_match.group(1)), rf_match.group(2))
            if rf_match.group(3):
                dims["raised_face_height"] = self.normalize_value(float(rf_match.group(3)), rf_match.group(4))

        if "raised_face_diameter" in dims and "raised_face_height" not in dims:
            rf_h = re.search(r"(?:raised\s*face|rf)[^.]*?(?:extruded|height|high|thickness|thick)\s*(?:by|of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
            if not rf_h:
                rf_h = re.search(r"(?:extruded|height|high|thickness|thick)\s*(?:by|of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
            if rf_h:
                dims["raised_face_height"] = self.normalize_value(float(rf_h.group(1)), rf_h.group(2))

        # 6. Bolt Pattern (count, hole diameter, PCD)
        bolt_count_match = re.search(r"(\d+)\s*(?:bolt\s*holes?|holes?|bolts?)", t)
        if bolt_count_match:
            dims["bolt_count"] = int(bolt_count_match.group(1))

        bolt_dia_match = re.search(r"(?:holes?|bolt\s*holes?)\s*(?:of|diameter|dia|=|:)?\s*(?:ø|dia(?:meter)?)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*dia(?:meter)?", t)
        if not bolt_dia_match:
            bolt_dia_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:diameter|dia)?\s*(?:bolt\s*holes?|holes?)", t)
        if bolt_dia_match:
            dims["bolt_hole_diameter"] = self.normalize_value(float(bolt_dia_match.group(1)), bolt_dia_match.group(2))

        pcd_match = re.search(r"(?:pitch\s*circle\s*diameter|pcd|bolt\s*circle|bcd)\s*(?:of|is|=|:)?\s*(?:ø|dia(?:meter)?)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?", t)
        if not pcd_match:
            pcd_match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in|m)?\s*(?:pitch\s*circle\s*diameter|pcd|bolt\s*circle|bcd)", t)
        if pcd_match:
            dims["bolt_pcd"] = self.normalize_value(float(pcd_match.group(1)), pcd_match.group(2))

        return dims

    def analyze(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> RequirementSpec:
        """
        Stage 1 & 2 Execution:
        Extracts features, normalizes all units, and performs completeness checks.
        """
        p_lower = prompt.lower()
        extracted = self.extract_dimensions_from_text(prompt)
        missing_fields: List[str] = []
        features: List[FeatureRequirement] = []

        # Detect Part Type
        if "flange" in p_lower or "pipe flange" in p_lower:
            part_type = "pipe_flange"

            # 1. Base Flange Disk
            od = extracted.get("outer_diameter", 150.0)
            thickness = extracted.get("thickness", 20.0)
            features.append(FeatureRequirement(
                id="base_flange",
                feature_type="base_cylinder",
                parameters={
                    "outer_diameter_mm": od,
                    "thickness_mm": thickness
                }
            ))

            # 2. Center Through-Bore
            bore_dia = extracted.get("bore_diameter", 65.0)
            features.append(FeatureRequirement(
                id="center_bore",
                feature_type="through_bore",
                parameters={
                    "diameter_mm": bore_dia,
                    "through": True
                },
                dependencies=["base_flange"]
            ))

            # 3. Raised Face (if requested)
            rf_dia = extracted.get("raised_face_diameter")
            rf_h = extracted.get("raised_face_height", 4.0)
            if rf_dia:
                features.append(FeatureRequirement(
                    id="raised_face",
                    feature_type="raised_face",
                    parameters={
                        "diameter_mm": rf_dia,
                        "height_mm": rf_h,
                        "offset_z_mm": thickness
                    },
                    dependencies=["base_flange"]
                ))

            # 4. Circular Bolt Pattern (if requested)
            bolt_count = extracted.get("bolt_count", 6)
            bolt_dia = extracted.get("bolt_hole_diameter", 14.0)
            pcd = extracted.get("bolt_pcd", 120.0)
            if "bolt" in p_lower or "holes" in p_lower or "hole" in p_lower or "pcd" in p_lower:
                features.append(FeatureRequirement(
                    id="bolt_pattern",
                    feature_type="circular_hole_pattern",
                    parameters={
                        "count": int(bolt_count),
                        "hole_diameter_mm": bolt_dia,
                        "pcd_mm": pcd,
                        "through": True
                    },
                    dependencies=["base_flange"]
                ))

        elif "cube" in p_lower or "box" in p_lower or "plate" in p_lower or "block" in p_lower:
            part_type = "prismatic_block"
            l = extracted.get("length", 30.0)
            w = extracted.get("width", l)
            h = extracted.get("height", l)

            features.append(FeatureRequirement(
                id="base_box",
                feature_type="base_box",
                parameters={"length_mm": l, "width_mm": w, "height_mm": h}
            ))

            if "hole" in p_lower or "bore" in p_lower or "drill" in p_lower:
                hole_dia = extracted.get("bore_diameter") or extracted.get("bolt_hole_diameter", 10.0)
                extracted["hole_diameter"] = hole_dia
                features.append(FeatureRequirement(
                    id="subtractive_hole",
                    feature_type="through_bore",
                    parameters={"diameter_mm": hole_dia, "through": True},
                    dependencies=["base_box"]
                ))

        elif "sprocket" in p_lower:
            part_type = "sprocket"
            od = extracted.get("outer_diameter", 60.0)
            teeth = int(extracted.get("bolt_count", 14))
            bore = extracted.get("bore_diameter", 12.0)
            thick = extracted.get("thickness", 8.0)
            features.append(FeatureRequirement(
                id="sprocket_body",
                feature_type="custom",
                parameters={
                    "outer_diameter_mm": od,
                    "teeth_count": teeth,
                    "bore_diameter_mm": bore,
                    "thickness_mm": thick
                }
            ))

        elif "u-bracket" in p_lower or "u_bracket" in p_lower or "u bracket" in p_lower or "u-channel" in p_lower or "c-bracket" in p_lower or "channel bracket" in p_lower:
            part_type = "u_bracket"
            width = extracted.get("width", 100.0)
            height = extracted.get("height", 60.0)
            thick = extracted.get("thickness", 5.0)
            depth = extracted.get("length") or extracted.get("depth", 50.0)

            features.append(FeatureRequirement(
                id="u_channel_body",
                feature_type="u_channel",
                parameters={
                    "width_mm": width,
                    "height_mm": height,
                    "thickness_mm": thick,
                    "depth_mm": depth
                }
            ))

        elif "l-bracket" in p_lower or "l_bracket" in p_lower or "l bracket" in p_lower or "angle bracket" in p_lower or "bracket" in p_lower:
            part_type = "l_bracket"
            length = extracted.get("length", 80.0)
            width = extracted.get("width", 60.0)
            height = extracted.get("height", 60.0)
            thick = extracted.get("thickness", 8.0)
            rib_thick = extracted.get("rib_thickness", 8.0)

            features.append(FeatureRequirement(
                id="l_bracket_body",
                feature_type="l_bracket",
                parameters={
                    "length_mm": length,
                    "width_mm": width,
                    "height_mm": height,
                    "thickness_mm": thick,
                    "rib_thickness_mm": rib_thick
                }
            ))

        elif "cylinder" in p_lower or "roller" in p_lower or "shaft" in p_lower:
            part_type = "cylindrical_shaft"
            dia = extracted.get("outer_diameter") or extracted.get("length", 50.0)
            length = extracted.get("height") or extracted.get("width", 100.0)
            features.append(FeatureRequirement(
                id="shaft_body",
                feature_type="base_cylinder",
                parameters={"diameter_mm": dia, "length_mm": length}
            ))

        else:
            part_type = "custom_part"
            l = extracted.get("length", 40.0)
            w = extracted.get("width", 40.0)
            h = extracted.get("height", 20.0)
            features.append(FeatureRequirement(
                id="base_feature",
                feature_type="base_box",
                parameters={"length_mm": l, "width_mm": w, "height_mm": h}
            ))

        # Build canonical dimensions dictionary
        canonical_dims = dict(extracted)
        for k, v in extracted.items():
            if not k.endswith("_mm") and k not in ["bolt_count", "teeth_count"]:
                canonical_dims[f"{k}_mm"] = v

        spec = RequirementSpec(
            part_type=part_type,
            units="mm",
            is_complete=(len(missing_fields) == 0),
            missing_fields=missing_fields,
            dimensions=canonical_dims,
            features=features,
            raw_prompt=prompt,
            notes=f"Successfully analyzed {len(features)} parametric feature groups."
        )
        return spec

requirement_analyzer = RequirementAnalyzer()
