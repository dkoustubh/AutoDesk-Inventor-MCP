"""
Unit & Integration Tests for Engineering Language Interpreter (ELI)
Verifies conversational parametric editing, ambiguity detection, and feature graph updating.
"""
import pytest
from app.pipeline.eli import EngineeringLanguageInterpreter, ELIResult
from app.pipeline.feature_graph import FeatureGraph, FeatureNode

def test_eli_initial_interpretation():
    eli = EngineeringLanguageInterpreter()
    prompt = "Create a pipe flange with 150 mm outer diameter and 20 mm flange thickness. Add a 65 mm center through-bore, a raised face of 95 mm diameter extruded 4 mm, and a circular pattern of 6 bolt holes of 14 mm diameter on a 120 mm pitch circle diameter (PCD)."
    
    result: ELIResult = eli.interpret(prompt)
    assert result.is_edit is False
    assert result.spec.part_type == "pipe_flange"
    assert result.spec.dimensions["outer_diameter_mm"] == 150.0
    assert result.spec.dimensions["bolt_pcd_mm"] == 120.0
    assert result.feature_graph is not None
    assert len(result.feature_graph.nodes) >= 3

def test_eli_conversational_parametric_edit():
    eli = EngineeringLanguageInterpreter()
    initial_prompt = "Create a pipe flange with 150 mm outer diameter and 20 mm flange thickness. Add a 65 mm center through-bore, a raised face of 95 mm diameter extruded 4 mm, and a circular pattern of 6 bolt holes of 14 mm diameter on a 120 mm pitch circle diameter (PCD)."
    initial_res = eli.interpret(initial_prompt)
    graph = initial_res.feature_graph
    
    # 1. Edit PCD from 120 mm to 125 mm
    edit_prompt_1 = "Change the PCD from 120 mm to 125 mm"
    edit_res_1 = eli.interpret(edit_prompt_1, current_graph=graph)
    
    assert edit_res_1.is_edit is True
    assert edit_res_1.feature_graph.global_parameters["bolt_pcd_mm"] == 125.0
    
    # 2. Edit thickness to 25 mm
    edit_prompt_2 = "Increase flange thickness to 25 mm"
    edit_res_2 = eli.interpret(edit_prompt_2, current_graph=edit_res_1.feature_graph)
    
    assert edit_res_2.is_edit is True
    assert edit_res_2.feature_graph.global_parameters["thickness_mm"] == 25.0

def test_eli_ambiguity_detection():
    eli = EngineeringLanguageInterpreter()
    
    # Generic ambiguous prompt
    ambiguous_prompt = "Make a bracket"
    result = eli.interpret(ambiguous_prompt)
    
    assert result.clarification is not None
    assert result.clarification.is_ambiguous is True
    assert "What type of bracket" in result.clarification.question
    assert len(result.clarification.options) > 0
