"""Unit tests for utils/parser.py"""

from utils.parser import clean_text


def test_clean_text_normalizes_whitespace():
    raw = "  Four   people   trapped\n\non the   terrace  "
    assert clean_text(raw) == "Four people trapped on the terrace"


def test_clean_text_handles_empty_string():
    assert clean_text("") == ""


def test_clean_text_single_word():
    assert clean_text("flood") == "flood"
