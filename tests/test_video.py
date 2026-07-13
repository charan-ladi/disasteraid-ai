"""Unit tests for utils/video.py"""

import os
from unittest.mock import MagicMock, patch
import pytest
from utils import video


@pytest.fixture
def temp_video_file(tmp_path):
    path = tmp_path / "test.mp4"
    with open(path, "wb") as f:
        f.write(b"mock video data")
    yield str(path)
    if os.path.exists(path):
        os.remove(path)


def test_process_video_nonexistent():
    with pytest.raises(FileNotFoundError):
        video.process_video("nonexistent.mp4")


def test_process_video_success(temp_video_file):
    # Mock extract frames to return a fake frame path
    # Mock extract audio to return a fake audio path
    fake_frames = ["/tmp/fake_frame.jpg"]
    fake_audio = "/tmp/fake_audio.wav"

    mock_ocr_res = {"text": "visual fire text", "engine": "paddleocr", "mock": False}
    mock_speech_res = {
        "text": "spoken help text",
        "engine": "faster-whisper",
        "mock": False,
    }

    with patch("utils.video._extract_frames", return_value=fake_frames), patch(
        "utils.video._extract_audio", return_value=fake_audio
    ), patch("utils.ocr.extract_text_from_image", return_value=mock_ocr_res), patch(
        "utils.speech.transcribe_audio", return_value=mock_speech_res
    ):

        res = video.process_video(temp_video_file)
        assert res["engine"] == "opencv+ocr+whisper"
        assert "visual fire text" in res["text"]
        assert "spoken help text" in res["text"]
        assert res["mock"] is False


def test_process_video_fallback(temp_video_file):
    # Mock both extractions to return nothing, triggering fallback mock text
    with patch("utils.video._extract_frames", return_value=[]), patch(
        "utils.video._extract_audio", return_value=None
    ):

        res = video.process_video(temp_video_file)
        assert res["engine"] == "mock"
        assert res["mock"] is True
        assert res["text"] in video._MOCK_VIDEO_TEXT


def test_extract_frames_no_cv2(temp_video_file):
    with patch("utils.video._CV2_AVAILABLE", False):
        res = video._extract_frames(temp_video_file)
        assert res == []


def test_extract_frames_cv2_success(temp_video_file):
    mock_cap = MagicMock()
    mock_cap.get.return_value = 10  # 10 frames
    mock_cap.read.return_value = (True, MagicMock())

    with patch("utils.video._CV2_AVAILABLE", True), patch(
        "cv2.VideoCapture", return_value=mock_cap
    ), patch("cv2.imwrite", return_value=True), patch(
        "tempfile.mkdtemp", return_value="/tmp/test_frames"
    ):

        res = video._extract_frames(temp_video_file, max_frames=2)
        assert len(res) == 2
        mock_cap.release.assert_called_once()


def test_extract_frames_cv2_empty(temp_video_file):
    mock_cap = MagicMock()
    mock_cap.get.return_value = 0  # 0 frames

    with patch("utils.video._CV2_AVAILABLE", True), patch(
        "cv2.VideoCapture", return_value=mock_cap
    ):

        res = video._extract_frames(temp_video_file)
        assert res == []
        mock_cap.release.assert_called_once()


def test_extract_audio_ffmpeg_success(temp_video_file):
    with patch("subprocess.run") as mock_run:
        res = video._extract_audio(temp_video_file)
        assert res is not None
        mock_run.assert_called_once()


def test_extract_audio_ffmpeg_failure(temp_video_file):
    with patch("subprocess.run", side_effect=Exception("ffmpeg missing")):
        res = video._extract_audio(temp_video_file)
        assert res is None
