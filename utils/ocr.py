"""
utils/ocr.py
Extracts text from images using PaddleOCR (CPU), and from video by
sampling frames and running OCR on each one.
"""

import cv2
from paddleocr import PaddleOCR

_ocr_engine = None


def _get_engine() -> PaddleOCR:
    """Lazily initialize the PaddleOCR engine (CPU only, loaded once)."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=False)
    return _ocr_engine


def extract_text_from_image(image_path: str) -> str:
    """Run OCR on a single image and return concatenated detected text."""
    engine = _get_engine()
    result = engine.ocr(image_path, cls=True)
    if not result or not result[0]:
        return ""
    lines = [line[1][0] for line in result[0]]
    return " ".join(lines)


def extract_text_from_video(video_path: str, frame_interval_sec: int = 5) -> str:
    """
    Sample one frame every `frame_interval_sec` seconds, run OCR on each,
    and return the concatenated, de-duplicated text.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_step = int(fps * frame_interval_sec)

    engine = _get_engine()
    collected_text = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            result = engine.ocr(frame, cls=True)
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    if text not in collected_text:
                        collected_text.append(text)
        frame_idx += 1

    cap.release()
    return " ".join(collected_text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(extract_text_from_image(sys.argv[1]))
