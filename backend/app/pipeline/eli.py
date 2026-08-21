"""
OmniCAD Engineering Language Interpreter (ELI)
Converts natural/informal engineering requests into normalized specifications,
handles ambiguity detection, and performs conversational parametric editing.
"""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from app.pipeline.schemas import RequirementSpec, FeatureRequirement
from app.pipeline.requirement_analyzer import RequirementAnalyzer
from app.pipeline.feature_graph import FeatureGraph, FeatureNode

logger = logging.getLogger(__name__)

class ClarificationQuestion(BaseModel):
    is_ambiguous: bool
    parameter_name: str
    question: str
    options: List[str] = []

class ELIResult(BaseModel):
    is_edit: bool = False
    clarification: Optional[ClarificationQuestion] = None
    spec: RequirementSpec
    feature_graph: Optional[FeatureGraph] = None
    applied_changes: List[str] = []

class EngineeringLanguageInterpreter:
    def __init__(self):
        self.analyzer = RequirementAnalyzer()

    def detect_edit_command(self, prompt: str, current_graph: Optional[FeatureGraph] = None) -> Tuple[bool, Dict[str, float], List[str]]:
        """
        Detects if user is asking to modify an existing dimension (e.g. 'Change PCD to 125 mm', 'Increase thickness to 25mm').
        """
        p_lower = prompt.lower()
        edit_patterns = [
            r"(?:change|set|increase|decrease|make|modify)\s+(?:the\s+)?([a-z\s_]+?)\s+(?:from\s+\d+(?:\.\d+)?\s*(?:mm)?\s*)?(?:to|=)\s*(\d+(?:\.\d+)?)\s*(?:mm)?",
            r"(?:change|set|increase|decrease|make|modify)\s+(?:the\s+)?([a-z\s_]+?)\s+(\d+(?:\.\d+)?)\s*(?:mm)?",
            r"make\s+(?:the\s+)?([a-z\s_]+?)\s+(\d+(?:\.\d+)?)\s*(?:mm)?\s*(?:wider|thicker|larger|smaller)?",
        ]
        
        changes: Dict[str, float] = {}
        descriptions: List[str] = []
        
        for pat in edit_patterns:
            for match in re.finditer(pat, p_lower):
                param_raw = match.group(1).strip()
                val_raw = float(match.group(2))
                
                # Normalize parameter name
                norm_name = None
                if "pcd" in param_raw or "pitch circle" in param_raw or "bolt circle" in param_raw:
                    norm_name = "bolt_pcd_mm"
                elif "bore" in param_raw or "inner" in param_raw or "hole diameter" in param_raw:
                    norm_name = "inner_bore_mm"
                elif "thickness" in param_raw or "height" in param_raw:
                    norm_name = "thickness_mm"
                elif "outer" in param_raw or "od" in param_raw or "flange diameter" in param_raw:
                    norm_name = "outer_diameter_mm"
                elif "raised face" in param_raw and ("dia" in param_raw or "diameter" in param_raw):
                    norm_name = "raised_face_diameter_mm"
                elif "raised face" in param_raw and ("height" in param_raw or "extru" in param_raw):
                    norm_name = "raised_face_height_mm"
                elif "bolt" in param_raw and ("hole" in param_raw or "dia" in param_raw):
                    norm_name = "bolt_hole_diameter_mm"
                elif "bolt" in param_raw and ("count" in param_raw or "number" in param_raw):
                    norm_name = "bolt_count"
                elif "length" in param_raw:
                    norm_name = "length_mm"
                elif "width" in param_raw:
                    norm_name = "width_mm"
                else:
                    norm_name = param_raw.replace(" ", "_")
                
                changes[norm_name] = val_raw
                descriptions.append(f"Modified {norm_name} -> {val_raw}")
            if changes:
                break
        
        is_edit = len(changes) > 0 and (current_graph is not None or any(w in p_lower for w in ["change", "modify", "increase", "decrease", "make the"]))
        return is_edit, changes, descriptions

    def check_ambiguity(self, prompt: str) -> Optional[ClarificationQuestion]:
        """
        Detects highly ambiguous or underspecified prompts where guessing would produce incorrect engineering geometry.
        """
        p_lower = prompt.lower().strip()
        
        # Single-word generic prompts
        if p_lower in ["bracket", "make a bracket", "create bracket"]:
            return ClarificationQuestion(
                is_ambiguous=True,
                parameter_name="bracket_type",
                question="What type of bracket do you require?",
                options=["Ribbed Mounting Bracket", "L-Bracket", "U-Bracket", "Conveyor Support Bracket"]
            )
        
        # Incomplete "base" ambiguity
        if "7mm base" in p_lower and "width" not in p_lower and "length" not in p_lower:
            return ClarificationQuestion(
                is_ambiguous=True,
                parameter_name="base_dimension",
                question="Do you mean a 7 mm base width, base length, or square base plate?",
                options=["7 mm base width", "7 mm base length", "7x7 mm square base"]
            )
            
        return None

    def interpret(self, prompt: str, current_graph: Optional[FeatureGraph] = None) -> ELIResult:
        """
        Main ELI execution pipeline.
        """
        logger.info(f"[ELI] Interpreting engineering request: '{prompt}'")
        
        # 1. Check for conversational edit
        is_edit, changes, desc_list = self.detect_edit_command(prompt, current_graph)
        if is_edit and current_graph:
            logger.info(f"[ELI] Conversational parametric edit detected: {changes}")
            updated_graph = current_graph.model_copy(deep=True)
            for k, v in changes.items():
                updated_graph.update_parameter(k, v)
            
            # Reconstruct spec from updated graph
            spec = RequirementSpec(
                part_type=updated_graph.part_type,
                units=updated_graph.units,
                dimensions=updated_graph.global_parameters,
                raw_prompt=prompt
            )
            return ELIResult(
                is_edit=True,
                spec=spec,
                feature_graph=updated_graph,
                applied_changes=desc_list
            )

        # 2. Check for ambiguity
        clarification = self.check_ambiguity(prompt)
        if clarification and clarification.is_ambiguous:
            logger.info(f"[ELI] Ambiguity detected: {clarification.question}")
            dummy_spec = RequirementSpec(part_type="clarification_needed", is_complete=False, raw_prompt=prompt)
            return ELIResult(
                is_edit=False,
                clarification=clarification,
                spec=dummy_spec
            )

        # 3. Standard requirement extraction & normalization
        spec = self.analyzer.analyze(prompt)
        
        # Build initial feature graph
        fg = FeatureGraph(
            name=f"{spec.part_type}_model",
            part_type=spec.part_type,
            units=spec.units,
            global_parameters=spec.dimensions
        )
        
        for feat in spec.features:
            fg.nodes.append(FeatureNode(
                id=feat.id,
                feature_type=feat.feature_type,
                parameters=feat.parameters,
                dependencies=feat.dependencies,
                operation_mode="SUBTRACT" if "bore" in feat.id or "hole" in feat.id else "ADD"
            ))

        return ELIResult(
            is_edit=False,
            spec=spec,
            feature_graph=fg,
            applied_changes=["Extracted structured engineering specification"]
        )
