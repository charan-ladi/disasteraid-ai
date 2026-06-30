"""
tests/test_offline.py
Asserts that core extraction logic makes ZERO network calls.
Uses pytest-socket to block all sockets except localhost (for Ollama,
which itself runs as a local CPU service on 127.0.0.1).
"""

import pytest

from utils.parser import clean_text


@pytest.mark.disable_socket
def test_text_cleaning_is_fully_offline():
    """Pure text processing must never touch the network."""
    result = clean_text("  Four people trapped near the bridge  ")
    assert result == "Four people trapped near the bridge"


@pytest.mark.disable_socket
def test_schema_validation_is_fully_offline():
    """Schema validation is pure local computation."""
    from jsonschema import Draft7Validator

    from utils.extractor import OUTPUT_SCHEMA

    Draft7Validator.check_schema(OUTPUT_SCHEMA)


@pytest.mark.disable_socket
def test_extract_json_block_is_fully_offline():
    """JSON block extraction is pure string processing."""
    from utils.extractor import _extract_json_block

    raw = '{"disaster_type": "Flood"}'
    result = _extract_json_block(raw)
    assert result == raw
