"""Unit tests for utils/extractor.py schema validation logic."""

import pytest
from unittest.mock import MagicMock
from jsonschema import Draft7Validator


from utils.extractor import OUTPUT_SCHEMA, _extract_json_block


def test_schema_is_valid():
    Draft7Validator.check_schema(OUTPUT_SCHEMA)


def test_extract_json_block_finds_object():
    raw = 'Some preamble text {"disaster_type": "Flood", "severity": "High"} trailing'
    result = _extract_json_block(raw)
    assert result.startswith("{")
    assert result.endswith("}")


def test_extract_json_block_raises_when_missing():
    with pytest.raises(ValueError):
        _extract_json_block("no json here at all")


def test_sample_record_matches_schema():
    sample = {
        "disaster_type": "Earthquake",
        "severity": "High",
        "people_trapped": 2,
        "children": 0,
        "elderly": 1,
        "injuries": False,
        "medical_help": False,
        "food_needed": True,
        "water_needed": True,
        "location": "Sector 9",
        "priority_score": 70,
        "status": "Monitoring",
    }
    validator = Draft7Validator(OUTPUT_SCHEMA)
    errors = list(validator.iter_errors(sample))
    assert errors == []


def test_extract_structured_data_success():
    import ollama
    from utils.extractor import extract_structured_data

    ollama.generate = MagicMock(
        return_value={
            "response": '{"disaster_type": "Flood", "severity": "High", "priority_score": 80}'
        }
    )
    res = extract_structured_data("some report text")
    assert res["disaster_type"] == "Flood"
    assert res["status"] == "ok"


def test_extract_structured_data_json_error():
    import ollama
    from utils.extractor import extract_structured_data

    ollama.generate = MagicMock(
        side_effect=[
            {"response": "invalid json"},
            {
                "response": '{"disaster_type": "Flood", "severity": "High", "priority_score": 80}'
            },
        ]
    )
    res = extract_structured_data("some report text")
    assert res["disaster_type"] == "Flood"


def test_extract_structured_data_persistent_error():
    import ollama
    from utils.extractor import extract_structured_data

    ollama.generate = MagicMock(return_value={"response": "invalid json"})
    res = extract_structured_data("some report text")
    assert res["status"] == "extraction_failed"


def test_extract_structured_data_model_missing():
    import ollama
    from utils.extractor import extract_structured_data

    ollama.generate = MagicMock(side_effect=RuntimeError("Connection refused"))
    res = extract_structured_data("some report text")
    assert res["status"] == "model_missing"
