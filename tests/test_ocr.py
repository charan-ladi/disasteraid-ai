"""Unit tests for utils/ocr.py"""

import os
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from utils import ocr


@pytest.fixture
def temp_image_generator(tmp_path):
    def _generator(color, size=(100, 100)):
        path = tmp_path / f"temp_{color}.png"
        img = Image.new("RGB", size, color=color)
        img.save(path)
        return str(path)

    return _generator


def test_extract_text_from_image_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        ocr.extract_text_from_image("does_not_exist.jpg")


def test_paddle_ocr_success(temp_image_generator):
    path = temp_image_generator("blue")

    # Mock engine to return text
    mock_engine = MagicMock()
    mock_engine.ocr.return_value = [[[None, ("people trapped near bridge", 0.99)]]]

    with patch("utils.ocr._get_engine", return_value=mock_engine):
        res = ocr.extract_text_from_image(path)
        assert res["engine"] == "paddleocr"
        assert res["text"] == "people trapped near bridge"
        assert res["mock"] is False


def test_lite_vision_fallback_flood(temp_image_generator):
    # Pure blue image
    path = temp_image_generator((0, 0, 255))
    with patch("utils.ocr._get_engine", return_value=None):
        res = ocr.extract_text_from_image(path)
        assert res["engine"] == "lite_vision_heuristic"
        assert "FLOOD" in res["text"]
        assert res["mock"] is True


def test_lite_vision_fallback_fire(temp_image_generator):
    # Red-dominant image
    # Note: Fire requires red > 0.37 and contrast > 55.
    # To get contrast > 55, we can make an image with half red, half black.
    path = temp_image_generator((255, 0, 0))
    # Let's create a red/black gradient or block image to increase standard deviation (contrast).
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    for x in range(50):
        for y in range(100):
            img.putpixel((x, y), (0, 0, 0))
    path = os.path.join(os.path.dirname(path), "fire.png")
    img.save(path)

    with patch("utils.ocr._get_engine", return_value=None):
        res = ocr.extract_text_from_image(path)
        assert res["engine"] == "lite_vision_heuristic"
        assert "FIRE" in res["text"]


def test_lite_vision_fallback_earthquake(temp_image_generator):
    # Dark gray low-contrast image (brightness < 80, contrast < 40)
    path = temp_image_generator((30, 30, 30))
    with patch("utils.ocr._get_engine", return_value=None):
        res = ocr.extract_text_from_image(path)
        assert res["engine"] == "lite_vision_heuristic"
        assert "EARTHQUAKE" in res["text"]


def test_lite_vision_fallback_landslide(temp_image_generator):
    # Green-dominant image (green > 0.36)
    path = temp_image_generator((0, 255, 0))
    with patch("utils.ocr._get_engine", return_value=None):
        res = ocr.extract_text_from_image(path)
        assert res["engine"] == "lite_vision_heuristic"
        assert "LANDSLIDE" in res["text"]


def test_lite_vision_fallback_cyclone(temp_image_generator):
    # Cyclone is the fallback when no other conditions are met
    # Neutral gray image with some contrast (so contrast >= 40)
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    # Give it half black, half white to make contrast high, and color ratio 1/3 each
    for x in range(50):
        for y in range(100):
            img.putpixel((x, y), (0, 0, 0))
    for x in range(50, 100):
        for y in range(100):
            img.putpixel((x, y), (255, 255, 255))
    path = os.path.join(os.path.dirname(temp_image_generator("blue")), "cyclone.png")
    img.save(path)

    with patch("utils.ocr._get_engine", return_value=None):
        res = ocr.extract_text_from_image(path)
        assert res["engine"] == "lite_vision_heuristic"
        assert "CYCLONE" in res["text"]


def test_lite_vision_no_libs_fallback(temp_image_generator):
    path = temp_image_generator("blue")
    with patch("utils.ocr._get_engine", return_value=None):
        with patch("utils.ocr._VISION_LIBS_AVAILABLE", False):
            res = ocr.extract_text_from_image(path)
            assert "Pillow/numpy not installed" in res["text"]


def test_lite_vision_decode_error():
    # Pass a file path that cannot be opened as an image (e.g. empty file)
    with patch("utils.ocr._get_engine", return_value=None):
        # We can write an empty file
        path = "empty_file.jpg"
        with open(path, "w") as f:
            f.write("")
        try:
            res = ocr.extract_text_from_image(path)
            assert "could not be decoded" in res["text"]
        finally:
            if os.path.exists(path):
                os.remove(path)
