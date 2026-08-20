import pytest
import asyncio
from app.services.llm_service import llm_service
from app.schemas import CreateBoxParameters

def test_heuristic_cube_intent():
    intent1 = llm_service._heuristic_intent_fallback("Create a cube of 3 cm.")
    assert intent1.tool == "inventor.create_box"
    assert intent1.parameters["length_mm"] == 30.0
    assert intent1.parameters["width_mm"] == 30.0
    assert intent1.parameters["height_mm"] == 30.0

def test_heuristic_box_dimensions():
    intent2 = llm_service._heuristic_intent_fallback("Create a box 50 x 25 x 10 mm")
    assert intent2.tool == "inventor.create_box"
    assert intent2.parameters["length_mm"] == 50.0
    assert intent2.parameters["width_mm"] == 25.0
    assert intent2.parameters["height_mm"] == 10.0

def test_pydantic_box_validation():
    valid_box = CreateBoxParameters(length_mm=30, width_mm=30, height_mm=30)
    assert valid_box.length_mm == 30.0
    assert valid_box.centered is True

def test_pydantic_negative_dimension_fails():
    with pytest.raises(Exception):
        CreateBoxParameters(length_mm=-5, width_mm=30, height_mm=30)
