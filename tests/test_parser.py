"""Unit tests for utils/parser.py"""

from unittest.mock import MagicMock, patch
import pytest
from utils.parser import (
    clean_text,
    _word_to_number,
    _find_count_near,
    _detect_disaster_type,
    _detect_severity,
    _detect_location,
    _yes_no,
    _priority_score,
    rule_based_parse,
    llm_parse,
    parse_text,
)


def test_clean_text_normalizes_whitespace():
    raw = "  Four   people   trapped\n\non the   terrace  "
    assert clean_text(raw) == "Four people trapped on the terrace"


def test_clean_text_handles_empty_string():
    assert clean_text("") == ""


def test_clean_text_single_word():
    assert clean_text("flood") == "flood"


def test_word_to_number():
    assert _word_to_number("5") == 5
    assert _word_to_number("two") == 2
    assert _word_to_number("unknown") is None


def test_find_count_near():
    assert _find_count_near("six people trapped", ["trapped"]) == 6
    assert _find_count_near("trapped for 10 hours", ["trapped"]) == 10
    assert _find_count_near("no one trapped", ["trapped"]) == 1


def test_detect_disaster_type():
    assert _detect_disaster_type("The flood water is rising.") == "Flood"
    assert _detect_disaster_type("An earthquake tremor was felt.") == "Earthquake"
    assert _detect_disaster_type("A severe cyclone storm surge.") == "Cyclone"
    assert _detect_disaster_type("Landslide blocked the road.") == "Landslide"
    assert _detect_disaster_type("Fire blaze in building.") == "Fire"
    assert _detect_disaster_type("General emergency.") == "Unspecified"


def test_detect_severity():
    assert _detect_severity("This is immediate and critical.") == "Critical"
    assert _detect_severity("Many people are injured.") == "High"
    assert _detect_severity("Some moderate damage.") == "Moderate"
    assert _detect_severity("The situation is stable under control.") == "Low"
    assert _detect_severity("Nothing specific.") == "Moderate"


def test_detect_location():
    assert _detect_location("trapped near the old bridge.") == "Old Bridge"
    assert _detect_location("at downtown market") == "Downtown Market"
    assert _detect_location("in Riverside") == "Riverside"
    assert _detect_location("no location mentioned") == "Unknown"


def test_yes_no():
    assert _yes_no("medical aid needed", ["medical", "doctor"]) is True
    assert _yes_no("we are fine", ["medical", "doctor"]) is False


def test_priority_score():
    assert _priority_score("Critical", 5, True, True) == 100
    assert _priority_score("Low", 0, False, False) == 15
    assert _priority_score("Moderate", 2, True, False) == 46


def test_rule_based_parse():
    res = rule_based_parse(
        "Five people are trapped near Riverside due to flood. Injuries reported."
    )
    assert res["disaster_type"] == "Flood"
    assert res["people_trapped"] == 5
    assert res["location"] == "Riverside Due To Flood"
    assert res["injuries"] is True
    assert res["engine"] == "rule_based"


def test_llm_parse_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response": '{"disaster_type": "Flood", "people_trapped": 3, "priority_score": 80}'
    }
    with patch("requests.post", return_value=mock_resp):
        res = llm_parse("some report")
        assert res["disaster_type"] == "Flood"
        assert res["people_trapped"] == 3
        assert res["status"] == "Immediate Rescue"
        assert "local_llm:" in res["engine"]


def test_llm_parse_no_requests():
    with patch("utils.parser._REQUESTS_AVAILABLE", False):
        with pytest.raises(RuntimeError):
            llm_parse("some report")


def test_parse_text_empty():
    with pytest.raises(ValueError):
        parse_text("")
    with pytest.raises(ValueError):
        parse_text("   ")


def test_parse_text_prefer_llm_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response": '{"disaster_type": "Fire", "people_trapped": 2, "priority_score": 60}'
    }
    with patch("requests.post", return_value=mock_resp):
        res = parse_text("fire report", prefer_llm=True)
        assert res["disaster_type"] == "Fire"
        assert "local_llm:" in res["engine"]


def test_parse_text_prefer_llm_fallback():
    # If requests raises exception, fall back to rule_based
    with patch("requests.post", side_effect=Exception("Timeout")):
        res = parse_text(
            "Five people trapped near Riverside due to flood.", prefer_llm=True
        )
        assert res["engine"] == "rule_based"
        assert res["disaster_type"] == "Flood"
        assert res["people_trapped"] == 5
