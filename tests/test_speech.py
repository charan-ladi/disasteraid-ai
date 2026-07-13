"""Unit tests for utils/speech.py"""

import os
from unittest.mock import MagicMock, patch
import pytest
from utils import speech


@pytest.fixture
def temp_audio_file(tmp_path):
    path = tmp_path / "test.wav"
    with open(path, "wb") as f:
        f.write(b"mock audio data")
    yield str(path)
    if os.path.exists(path):
        os.remove(path)


def test_transcribe_audio_nonexistent():
    with pytest.raises(FileNotFoundError):
        speech.transcribe_audio("nonexistent.wav")


def test_transcribe_audio_success(temp_audio_file):
    # Mock WhisperModel transcribe
    mock_segment = MagicMock()
    mock_segment.text = "Help, there is a flood here!"

    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([mock_segment], None)

    with patch("utils.speech._get_model", return_value=mock_model):
        res = speech.transcribe_audio(temp_audio_file)
        assert res["engine"] == "faster-whisper"
        assert res["text"] == "Help, there is a flood here!"
        assert res["mock"] is False


def test_transcribe_audio_fallback_to_mock(temp_audio_file):
    # Mock WhisperModel transcribe to return empty segment
    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([], None)

    with patch("utils.speech._get_model", return_value=mock_model):
        res = speech.transcribe_audio(temp_audio_file)
        assert res["engine"] == "mock"
        assert res["mock"] is True
        assert res["text"] in speech._MOCK_TRANSCRIPTS


def test_transcribe_audio_model_exception(temp_audio_file):
    # Mock transcribe raising exception
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = RuntimeError("Transcribe error")

    with patch("utils.speech._get_model", return_value=mock_model):
        res = speech.transcribe_audio(temp_audio_file)
        assert res["engine"] == "mock"
        assert res["mock"] is True


def test_transcribe_audio_no_model(temp_audio_file):
    # Mock _get_model to return None
    with patch("utils.speech._get_model", return_value=None):
        res = speech.transcribe_audio(temp_audio_file)
        assert res["engine"] == "mock"
        assert res["mock"] is True
