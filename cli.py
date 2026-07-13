#!/usr/bin/env python3
"""
cli.py
------
CLI tool to process disaster reports (text, image, audio, PDF, video)
into structured JSON/CSV using fully offline, CPU-only models.
"""

import argparse
import csv
import json
import os
import sys

from utils import db, parser, ocr, speech, video


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


def main():
    arg_parser = argparse.ArgumentParser(description="DisasterAid AI CLI tool")
    arg_parser.add_argument("--input", required=True, help="Path to input report file")
    arg_parser.add_argument(
        "--type",
        required=True,
        choices=["image", "audio", "pdf", "text", "video"],
        help="Type of report file",
    )
    arg_parser.add_argument(
        "--output",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )

    args = arg_parser.parse_args()

    input_path = args.input
    file_type = args.type
    output_format = args.output

    if file_type != "text" and not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # 1. Initialize DB
    db.init_db()

    # 2. Extract Text based on Type
    try:
        if file_type == "text":
            if os.path.exists(input_path):
                with open(input_path, "r", encoding="utf-8") as f:
                    extracted_text = f.read()
            else:
                extracted_text = input_path
            result = {"text": extracted_text, "engine": "raw_text", "mock": False}
        elif file_type == "image":
            result = ocr.extract_text_from_image(input_path)
        elif file_type == "audio":
            result = speech.transcribe_audio(input_path)
        elif file_type == "video":
            result = video.process_video(input_path)
        elif file_type == "pdf":
            result = _extract_pdf_text(input_path)
        else:
            result = {"text": "", "engine": "none", "mock": False}

        extracted_text = result["text"]

        # 3. Parse text using rule-based/LLM parser
        record = parser.parse_text(extracted_text)
        record["extraction_engine"] = result["engine"]
        record["mock_mode"] = result["mock"]
        record["extracted_text"] = extracted_text

        # 4. Save to Database
        filename = (
            os.path.basename(input_path)
            if os.path.exists(input_path)
            else "direct_text"
        )
        incident_id = db.save_incident(
            record,
            source_type=file_type,
            source_file=filename,
            raw_text=extracted_text,
        )
        record["incident_id"] = incident_id

        # 5. Output Result to stdout
        if output_format == "json":
            print(json.dumps(record, indent=2))
        elif output_format == "csv":
            # Write CSV to stdout
            writer = csv.DictWriter(sys.stdout, fieldnames=record.keys())
            writer.writeheader()
            writer.writerow(record)

    except Exception as exc:
        print(f"Error processing report: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
