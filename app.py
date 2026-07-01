"""
app.py
------
DisasterAid AI - Flask backend.

Frontend is plain HTML/CSS/JS (templates/ + static/) - NOT Streamlit.
All processing is local: text, image (OCR), audio (speech-to-text), and
video are converted into structured emergency JSON via utils/parser.py,
then stored in SQLite (utils/db.py) and shown on the dashboard.
"""

import os
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename

from utils import db, parser, ocr, speech, video

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

ALLOWED_EXT = {
    "text": {"txt"},
    "image": {"png", "jpg", "jpeg", "bmp", "webp"},
    "audio": {"wav", "mp3", "m4a", "ogg", "flac"},
    "video": {"mp4", "mov", "avi", "mkv"},
    "document": {"pdf"},
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB


def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _detect_category(filename):
    e = _ext(filename)
    for category, exts in ALLOWED_EXT.items():
        if e in exts:
            return category
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/process/text", methods=["POST"])
def process_text():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    record = parser.parse_text(text)
    incident_id = db.save_incident(record, source_type="text", raw_text=text)
    record["incident_id"] = incident_id
    return jsonify(record)


@app.route("/api/process/file", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    category = _detect_category(f.filename)
    if category is None:
        return jsonify({"error": "Unsupported file type"}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = secure_filename(f.filename)
    save_path = os.path.join(UPLOAD_DIR, filename)
    f.save(save_path)

    try:
        if category == "image":
            result = ocr.extract_text_from_image(save_path)
        elif category == "audio":
            result = speech.transcribe_audio(save_path)
        elif category == "video":
            result = video.process_video(save_path)
        elif category == "document":
            result = _extract_pdf_text(save_path)
        else:
            result = {"text": "", "engine": "none", "mock": False}

        extracted_text = result["text"]
        record = parser.parse_text(extracted_text)
        record["extraction_engine"] = result["engine"]
        record["mock_mode"] = result["mock"]
        record["extracted_text"] = extracted_text

        incident_id = db.save_incident(
            record, source_type=category, source_file=filename, raw_text=extracted_text
        )
        record["incident_id"] = incident_id
        return jsonify(record)

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def _extract_pdf_text(pdf_path):
    """Lightweight offline PDF text extraction using pypdf, with mock fallback."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        if text.strip():
            return {"text": text, "engine": "pypdf", "mock": False}
    except Exception:
        pass
    return {
        "text": "Government relief notice: Camp established for flood-affected "
                "families. Approximately 80 people sheltered, food and clean "
                "water urgently required.",
        "engine": "mock",
        "mock": True,
    }


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    return jsonify(db.get_all_incidents())


@app.route("/api/incidents/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    record = db.get_incident(incident_id)
    if record is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(record)


@app.route("/api/incidents/<int:incident_id>", methods=["DELETE"])
def delete_incident(incident_id):
    db.delete_incident(incident_id)
    return jsonify({"deleted": incident_id})


@app.route("/api/export/<fmt>", methods=["GET"])
def export(fmt):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    if fmt == "json":
        path = os.path.join(EXPORT_DIR, "incidents_export.json")
        db.export_json(path)
    elif fmt == "csv":
        path = os.path.join(EXPORT_DIR, "incidents_export.csv")
        db.export_csv(path)
    else:
        return jsonify({"error": "format must be json or csv"}), 400
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
