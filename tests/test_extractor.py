"""Unit tests for utils/extractor.py schema validation logic."""

import pytest
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
