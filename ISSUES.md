# GitLab Issues — DisasterAid AI
# Create at: code.swecha.org/srikarrao/disasteraid-ai/-/issues/new

---

## ISSUE 1
Title:       Set up Streamlit app skeleton and routing
Assignee:    srikar
Label:       frontend, backend
Estimate:    1h
Due date:    2026-06-28
Description:
  Create app.py with Streamlit pages: Home (upload), Processing, Dashboard,
  Incident Details, Search, Export. Wire up navigation between pages.

---

## ISSUE 2
Title:       Initialize SQLite database schema
Assignee:    srikar
Label:       backend, database
Estimate:    30min
Due date:    2026-06-28
Description:
  Create database.py with incidents and reports tables as per data-model spec.
  Include DB init function called on app startup.
  Fields: id, disaster_type, severity, people_trapped, children, elderly,
  injured, food_needed, water_needed, medicine_needed, location, lat, lon,
  timestamp, status, priority_score.

---

## ISSUE 3
Title:       Integrate PaddleOCR for image and video frame extraction
Assignee:    srikar
Label:       ai, ocr
Estimate:    1h
Due date:    2026-06-28
Description:
  Create utils/ocr.py. Accept image file path, run PaddleOCR (CPU),
  return extracted text string. For video: extract 1 frame per 5 seconds
  via OpenCV, run OCR on each frame, concatenate results.

---

## ISSUE 4
Title:       Integrate Whisper for offline audio transcription
Assignee:    srikar
Label:       ai, audio
Estimate:    1h
Due date:    2026-06-28
Description:
  Create utils/speech.py. Accept audio file (.wav/.mp3/.ogg).
  Convert to 16kHz mono WAV via pydub. Run openai-whisper (tiny model, CPU).
  Return raw transcript string. Handle model-not-found gracefully.

---

## ISSUE 5
Title:       PDF text extraction via PyMuPDF
Assignee:    charanladi (Charan)
Label:       backend
Estimate:    45min
Due date:    2026-06-28
Description:
  Create utils/parser.py. Accept PDF file path, extract text per page
  using PyMuPDF (fitz). Concatenate all pages. Return clean text string.
  Handle encrypted/empty PDFs gracefully.

---

## ISSUE 6
Title:       Ollama LLM extraction module (TinyLlama → structured JSON)
Assignee:    charanladi (Charan)
Label:       ai, extraction
Estimate:    1h
Due date:    2026-06-28
Description:
  Create utils/extractor.py. Build prompt with extracted text.
  Send to TinyLlama via Ollama. Parse JSON response.
  Validate against output schema using jsonschema.
  Retry once on invalid JSON. Return status=extraction_failed if Ollama down.
  Output must include: disaster_type, severity, people_trapped, children,
  elderly, injuries, medical_help, food_needed, water_needed, location,
  priority_score, status.

---

## ISSUE 7
Title:       Dashboard UI with severity color coding
Assignee:    srikar
Label:       frontend
Estimate:    1h
Due date:    2026-06-28
Description:
  Streamlit dashboard page showing all incidents as cards.
  Color coding: Red=Critical, Orange=High, Yellow=Medium, Green=Low.
  Show incident_id, disaster_type, severity, people_trapped, location,
  priority_score. Click card to open incident details page.

---

## ISSUE 8
Title:       CSV and JSON export endpoints
Assignee:    charanladi (Charan)
Label:       backend
Estimate:    30min
Due date:    2026-06-28
Description:
  Add export buttons on dashboard. JSON: download all incidents as JSON array.
  CSV: flatten incidents table using pandas, download as .csv file.
  Use Streamlit download_button component.

---

## ISSUE 9
Title:       Set up 10-stage CI/CD pipeline on GitLab Runner
Assignee:    charanladi (Charan)
Label:       ci, devops
Estimate:    1.5h
Due date:    2026-06-28
Description:
  Configure .gitlab-ci.yml with all 10 stages: lint, format, type_check,
  security, test, coverage (≥80%), schema_validate, model_check,
  offline_test, build. All must run on local shell runner (not Docker).
  Create scripts/validate_schema.py and scripts/check_models.py.

---

## ISSUE 10
Title:       Write pytest tests (unit + offline assertion)
Assignee:    charanladi (Charan) + srikar
Label:       testing
Estimate:    1h
Due date:    2026-06-28
Description:
  tests/test_parser.py — test PDF and text extraction.
  tests/test_extractor.py — test JSON schema validation logic.
  tests/test_database.py — test SQLite insert and fetch.
  tests/test_offline.py — use pytest-socket to assert no network calls
  during OCR + Whisper + Ollama inference.
