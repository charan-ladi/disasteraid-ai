"""
video.py
--------
Processes disaster-report videos by:
  1. Extracting key frames and running OCR on them (reuses utils/ocr.py)
  2. Extracting the audio track and transcribing it (reuses utils/speech.py)
  3. Merging both into one combined text block for the parser

REAL ENGINE: OpenCV (frame extraction) + ffmpeg (audio extraction) +
the same PaddleOCR / faster-whisper engines used elsewhere.
    pip install opencv-python
    (ffmpeg must be installed and on PATH)

MOCK MODE: If OpenCV / ffmpeg / the underlying OCR & speech engines aren't
available, falls back to mock text so the pipeline keeps working end-to-end.
"""

import os
import subprocess
import tempfile

from . import ocr as ocr_module
from . import speech as speech_module

_CV2_AVAILABLE = False
try:
    import cv2  # noqa: F401

    _CV2_AVAILABLE = True
except Exception:
    _CV2_AVAILABLE = False


def _extract_frames(video_path, max_frames=5):
    """Extract up to `max_frames` evenly spaced frames as temp jpg files."""
    if not _CV2_AVAILABLE:
        return []

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if total <= 0:
        cap.release()
        return []

    step = max(total // max_frames, 1)
    frame_paths = []
    tmp_dir = tempfile.mkdtemp(prefix="disasteraid_frames_")
    for i in range(0, total, step):
        if len(frame_paths) >= max_frames:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if not ok:
            continue
        out_path = os.path.join(tmp_dir, f"frame_{i}.jpg")
        cv2.imwrite(out_path, frame)
        frame_paths.append(out_path)
    cap.release()
    return frame_paths


def _extract_audio(video_path):
    """Use ffmpeg to pull a .wav audio track out of the video, if ffmpeg exists."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            out_path = f.name
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                out_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return out_path
    except Exception:
        return None


_MOCK_VIDEO_TEXT = [
    "Video shows a collapsed roof after the storm. Residents report two people "
    "missing and request urgent search and rescue support near the village school.",
    "Footage from the flood zone shows rising water levels surrounding several "
    "homes. Families are waving for help from rooftops, food supplies are low.",
]


def process_video(video_path):
    """
    Returns a combined text summary extracted from a video's frames (OCR)
    and audio track (speech-to-text). Falls back to mock text if OpenCV/
    ffmpeg/the underlying engines aren't available.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    combined_parts = []
    used_mock = False

    frames = _extract_frames(video_path)
    for frame_path in frames:
        result = ocr_module.extract_text_from_image(frame_path)
        if result["text"]:
            combined_parts.append(result["text"])
        used_mock = used_mock or result["mock"]

    audio_path = _extract_audio(video_path)
    if audio_path:
        result = speech_module.transcribe_audio(audio_path)
        if result["text"]:
            combined_parts.append(result["text"])
        used_mock = used_mock or result["mock"]

    if not combined_parts:
        seed = abs(hash(os.path.basename(video_path))) % len(_MOCK_VIDEO_TEXT)
        combined_parts.append(_MOCK_VIDEO_TEXT[seed])
        used_mock = True

    return {
        "text": " ".join(combined_parts),
        "engine": "opencv+ocr+whisper" if not used_mock else "mock",
        "mock": used_mock,
    }


if __name__ == "__main__":
    print(process_video("sample.mp4"))
