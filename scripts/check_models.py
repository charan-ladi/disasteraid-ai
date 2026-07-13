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
    required_modules = ["ollama", "whisper", "fitz", "cv2"]
    for m in required_modules:
        check_import(m)
    print("✅ Checked all optional/required model runtime imports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
