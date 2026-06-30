# DisasterAid AI — Technical Specification

## 1. Overview

**Project Name:** DisasterAid AI
**Type:** Offline-first Web App (Streamlit)
**Input:** Image, Audio, Video, PDF, Text
**Output:** Structured JSON + SQLite persistence
**Model Runtime:** PaddleOCR (CPU) + Whisper.cpp (CPU) + TinyLlama/Phi-3 Mini via Ollama (CPU)
**License:** AGPLv3

---

## 2. System Architecture

```
+------------------+
|   Upload Input   |
+--------+---------+
         |
+--------+---------+-----------+----------+
|        |         |           |          |
Image  Audio    Video         PDF       Text
|        |         |           |          |
PaddleOCR  Whisper.cpp  Frame+OCR  PyMuPDF  Direct
|        |         |           |          |
+--------+---------+-----------+----------+
                   |
             Extracted Text
                   |
            Prompt Builder
                   |
         TinyLlama / Phi-3 Mini
         (Ollama, CPU-only)
                   |
           Structured JSON
                   |
       SQLite + CSV Export + Dashboard
```

---

## 3. Input Specification

| Input Type | Format | Tool |
|---|---|---|
| Image | .jpg, .png, .webp | PaddleOCR |
| Audio | .wav, .mp3, .ogg | Whisper.cpp (tiny model) |
| Video | .mp4, .avi | Frame extractor + PaddleOCR |
| PDF | .pdf | PyMuPDF |
| Text | Plain text | Direct to LLM |

---

## 4. Processing Pipeline

### Stage 1 — Upload & Validation
- Accept all 5 input types via Streamlit file uploader
- Validate format and file size (max 100MB)
- Save to `uploads/` temp directory

### Stage 2 — Preprocessing
- Image: resize, normalize for OCR
- Audio: convert to 16kHz mono WAV
- Video: extract 1 frame per 5 seconds
- PDF: extract text per page via PyMuPDF
- Text: clean and normalize

### Stage 3 — OCR / Speech-to-Text
- Image/Video frames → PaddleOCR → raw text
- Audio → Whisper.cpp (tiny, CPU, int8) → raw transcript
- PDF/Text → direct extracted text

### Stage 4 — LLM Extraction (Ollama)
- Build prompt with extracted text
- Send to TinyLlama or Phi-3 Mini via Ollama
- Parse JSON response
- Validate against schema (jsonschema)
- Retry once on invalid JSON
- Graceful failure: return raw text with status=extraction_failed

### Stage 5 — Storage
- Insert validated record into SQLite `incidents` table
- Assign incident_id
- Index on timestamp and severity

---

## 5. Database Schema

```sql
CREATE TABLE incidents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    disaster_type   TEXT,
    severity        TEXT,
    people_trapped  INTEGER,
    children        INTEGER,
    elderly         INTEGER,
    injured         BOOLEAN,
    food_needed     BOOLEAN,
    water_needed    BOOLEAN,
    medicine_needed BOOLEAN,
    location        TEXT,
    latitude        REAL,
    longitude       REAL,
    timestamp       TEXT DEFAULT CURRENT_TIMESTAMP,
    status          TEXT DEFAULT 'Pending',
    priority_score  INTEGER
);

CREATE TABLE reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id     INTEGER REFERENCES incidents(id),
    source_type     TEXT,
    filename        TEXT,
    extracted_text  TEXT
);
```

---

## 6. Output Schema

```json
{
  "incident_id": 1032,
  "disaster_type": "Flood",
  "severity": "Critical",
  "people_trapped": 4,
  "children": 2,
  "elderly": 1,
  "injuries": true,
  "medical_help": true,
  "food_needed": true,
  "water_needed": true,
  "location": "Old Bridge",
  "priority_score": 96,
  "status": "Immediate Rescue"
}
```

---

## 7. API Endpoints (Streamlit Internal)

| Method | Endpoint | Description |
|---|---|---|
| POST | /upload | Upload any input type |
| POST | /extract | Run AI extraction pipeline |
| GET | /dashboard | View all incidents |
| GET | /incident/{id} | View single incident |
| GET | /export/json | Download all as JSON |
| GET | /export/csv | Download all as CSV |

---

## 8. Offline Guarantee

- All models downloaded once, stored locally in `models/`
- No requests to any external API during inference
- Streamlit runs fully on localhost
- CI has `offline_test` stage asserting zero outbound network calls using `pytest-socket`

---

## 9. CI/CD Pipeline Stages (10 checks)

| Stage | Tool | Check |
|---|---|---|
| `lint` | `ruff` | Code style |
| `format` | `black` | Auto-formatting |
| `type_check` | `mypy` | Static types |
| `security` | `bandit` | Vulnerability scan |
| `test` | `pytest` | Unit + integration |
| `coverage` | `pytest-cov` | Min 80% coverage |
| `schema_validate` | `jsonschema` | Output schema check |
| `model_check` | custom script | Ollama + Whisper available |
| `offline_test` | `pytest-socket` | No network during inference |
| `build` | `pip check` | Dependency integrity |

---

## 10. Work Division

| Task | Owner | Estimate | Due |
|---|---|---|---|
| Streamlit app skeleton + routing | Srikar | 1h | Phase 2 |
| SQLite database + models | Srikar | 30min | Phase 2 |
| PaddleOCR integration (image/video) | Srikar | 1h | Phase 2 |
| Whisper.cpp audio transcription | Srikar | 1h | Phase 2 |
| PDF extraction (PyMuPDF) | Charan | 45min | Phase 2 |
| Ollama LLM extraction + prompt | Charan | 1h | Phase 2 |
| JSON schema validation | Charan | 30min | Phase 2 |
| Dashboard UI + severity colors | Srikar | 1h | Phase 2 |
| CSV/JSON export | Charan | 30min | Phase 2 |
| CI/CD pipeline (10 stages) | Charan | 1.5h | Phase 3 |
| pytest tests + offline assertion | Both | 1h | Phase 3 |
