"""
scripts/check_models.py
CI check: verifies that the local model runtimes (Ollama + Whisper)
are installed and importable. Does not require the models to be
pulled in CI (that would need network); just checks the runtime
libraries are present so the app can run on a properly set-up machine.
"""

import importlib
import sys


def check_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} is importable.")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False


def main() -> int:
    required_modules = ["ollama", "whisper", "paddleocr", "fitz", "cv2", "pydub"]
    results = [check_import(m) for m in required_modules]

    if all(results):
        print("✅ All required model runtime libraries are available.")
        return 0

    print("❌ One or more required libraries are missing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
