"""
utils/ocr.py
Extracts text from images using Tesseract OCR (CPU), and from video by
sampling frames and running OCR on each one.
"""

import cv2
import pytesseract
from PIL import Image


def extract_text_from_image(image_path: str) -> str:
    """Run OCR on a single image and return detected text."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text.strip()


def extract_text_from_video(video_path: str, frame_interval_sec: int = 5) -> str:
    """
    Sample one frame every frame_interval_sec seconds, run OCR on each,
    and return the concatenated, de-duplicated text.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_step = int(fps * frame_interval_sec)

    collected_text = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            text = pytesseract.image_to_string(pil_image).strip()
            if text and text not in collected_text:
                collected_text.append(text)
        frame_idx += 1

    cap.release()
    return " ".join(collected_text)
