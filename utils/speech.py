"""
speech.py
---------
Converts voice/audio disaster reports into text using offline speech
recognition.

REAL ENGINE: faster-whisper (CTranslate2-based, CPU-only, fully offline
once the model is downloaded once).
    pip install faster-whisper

MOCK MODE: If faster-whisper isn't installed, falls back to a deterministic
mock transcript so the pipeline keeps working end-to-end.
"""

import os

_whisper_model = None
_WHISPER_AVAILABLE = False

try:
    from faster_whisper import WhisperModel  # noqa: F401
    _WHISPER_AVAILABLE = True
except Exception:
    _WHISPER_AVAILABLE = False

WHISPER_MODEL_SIZE = "base"  # tiny / base / small - base is a good CPU tradeoff


def _get_model():
    global _whisper_model
    if _whisper_model is None and _WHISPER_AVAILABLE:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _whisper_model


_MOCK_TRANSCRIPTS = [
    "There is heavy flooding near the market area. Around six families are stuck "
    "on rooftops and need a boat immediately.",
    "We have a fire in building number twelve. Smoke is spreading and two people "
    "are injured. Please send fire brigade and ambulance.",
    "Landslide blocked the main road near the hill village. No injuries reported "
    "but the village is cut off and needs food and water supplies.",
]


def _mock_transcribe(audio_path):
    seed = abs(hash(os.path.basename(audio_path))) % len(_MOCK_TRANSCRIPTS)
    return _MOCK_TRANSCRIPTS[seed]


def transcribe_audio(audio_path):
    """
    Returns transcribed text from an audio file.
    Uses real faster-whisper if installed; otherwise returns a mock transcript.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)

    model = _get_model()
    if model is not None:
        try:
            segments, _info = model.transcribe(audio_path, beam_size=5)
            text = " ".join(seg.text.strip() for seg in segments).strip()
            if text:
                return {"text": text, "engine": "faster-whisper", "mock": False}
        except Exception:
            pass  # fall through to mock

    return {"text": _mock_transcribe(audio_path), "engine": "mock", "mock": True}


if __name__ == "__main__":
    print(transcribe_audio("sample.wav"))
