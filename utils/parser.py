"""
utils/parser.py
Extracts plain text from PDF reports using PyMuPDF (fitz).
Runs entirely locally / offline.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract and concatenate text from every page of a PDF.
    Returns an empty string if the PDF is encrypted or has no text layer.
    """
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Could not open PDF: {e}") from e

    if doc.is_encrypted:
        try:
            doc.authenticate("")
        except Exception:
            doc.close()
            return ""

    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()

    return "\n".join(pages_text).strip()


def clean_text(raw_text: str) -> str:
    """Normalize whitespace in plain text input (used for direct text reports)."""
    return " ".join(raw_text.split())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(extract_text_from_pdf(sys.argv[1]))
