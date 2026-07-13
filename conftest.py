"""
conftest.py
Mock heavy dependencies (ollama, faster_whisper, paddleocr) in tests.
"""

import sys
from unittest.mock import MagicMock

# Mock faster-whisper
mock_whisper = MagicMock()
class MockWhisperModel:
    def __init__(self, *args, **kwargs):
        pass
    def transcribe(self, *args, **kwargs):
        return [], None
mock_whisper.WhisperModel = MockWhisperModel
sys.modules["faster_whisper"] = mock_whisper

# Mock paddleocr
mock_paddleocr = MagicMock()
class MockPaddleOCR:
    def __init__(self, *args, **kwargs):
        pass
    def ocr(self, *args, **kwargs):
        return []
mock_paddleocr.PaddleOCR = MockPaddleOCR
sys.modules["paddleocr"] = mock_paddleocr

# Mock paddlepaddle
mock_paddlepaddle = MagicMock()
sys.modules["paddlepaddle"] = mock_paddlepaddle

# Mock ollama
mock_ollama = MagicMock()
sys.modules["ollama"] = mock_ollama
