"""
utils/speech.py
Offline audio transcription using OpenAI Whisper (tiny model, CPU).
"""

import os

import whisper
from pydub import AudioSegment

_model = None


def _get_model():
    """Lazily load the Whisper tiny model (CPU) once."""
    global _model
    if _model is None:
        _model = whisper.load_model("tiny")
    return _model


def _convert_to_wav(input_path: str) -> str:
    """Convert any supported audio format to 16kHz mono WAV."""
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio.export(output_path, format="wav")
    return output_path


def transcribe_audio(file_path: str) -> str:
    """
    Convert the input audio to 16kHz mono WAV and run local Whisper
    transcription. Returns the raw transcript string.
    """
    try:
        wav_path = _convert_to_wav(file_path)
    except Exception as e:
        raise ValueError(f"Could not process audio file: {e}") from e

    try:
        model = _get_model()
        result = model.transcribe(wav_path, fp16=False)
        return result.get("text", "").strip()
    finally:
        if os.path.exists(wav_path) and wav_path != file_path:
            os.remove(wav_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(transcribe_audio(sys.argv[1]))
