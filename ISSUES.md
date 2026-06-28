# GitLab Issues — SabhaLekhan Phase 1
# Create these one by one at: code.swecha.org/charanladi/sabhalekhana/-/issues/new

---

## ISSUE 1
Title:       Set up Flask app skeleton and routing
Assignee:    charanladi (Charan)
Label:       backend
Estimate:    1h
Due date:    2026-06-28
Description:
  Create Flask app factory, register blueprints for upload, sessions, and health routes.
  Includes __init__.py, routes.py, and app config.

---

## ISSUE 2
Title:       Design and initialize SQLite database schema
Assignee:    charanladi (Charan)
Label:       backend, database
Estimate:    30min
Due date:    2026-06-28
Description:
  Create models.py with sessions table schema (id, recorded_at, duration_sec,
  audio_filename, transcript_raw, structured_json, status, created_at).
  Include DB init script.

---

## ISSUE 3
Title:       Integrate faster-whisper for CPU transcription
Assignee:    srikar
Label:       ai, audio
Estimate:    1h
Due date:    2026-06-28
Description:
  Wrap faster-whisper (tiny.en model, CPU, int8) in whisper_engine.py.
  Accept audio file path, return raw transcript string + duration_seconds.
  Handle model-not-found gracefully.

---

## ISSUE 4
Title:       Audio upload handler with format validation
Assignee:    srikar
Label:       backend, audio
Estimate:    45min
Due date:    2026-06-28
Description:
  POST /upload endpoint. Validate .wav/.mp3/.ogg, max 100MB.
  Convert to 16kHz mono WAV via pydub. Save to uploads/ temp dir.
  Return 400 with error JSON on invalid input.

---

## ISSUE 5
Title:       Ollama extraction module (llama3.2:3b → structured JSON)
Assignee:    charanladi (Charan)
Label:       ai, extraction
Estimate:    1h
Due date:    2026-06-28
Description:
  Create ollama_extractor.py. Send transcript to llama3.2:3b with extraction
  prompt. Parse JSON response. Validate against schema (jsonschema).
  Retry once on invalid JSON. Return status=extraction_failed if Ollama down.

---

## ISSUE 6
Title:       Frontend UI — upload page and results view
Assignee:    srikar
Label:       frontend
Estimate:    1h
Due date:    2026-06-28
Description:
  Single HTML page (Tailwind CSS). Drag-drop audio upload, progress indicator,
  structured results display (transcript, decisions, action items table).
  Export buttons (JSON, CSV).

---

## ISSUE 7
Title:       CSV/JSON export endpoint
Assignee:    srikar
Label:       backend
Estimate:    30min
Due date:    2026-06-28
Description:
  GET /sessions/<id>/export?format=csv and ?format=json.
  CSV flattens action_items rows. JSON returns full structured record.

---

## ISSUE 8
Title:       Set up 10-stage CI/CD pipeline on GitLab Runner
Assignee:    charanladi (Charan)
Label:       ci, devops
Estimate:    1.5h
Due date:    2026-06-28
Description:
  Configure .gitlab-ci.yml with all 10 stages: lint, format, type_check,
  security, test, coverage (≥80%), schema_validate, model_check,
  offline_test, build. All must run on local shell runner (not Docker).

---

## ISSUE 9
Title:       Write pytest tests (unit + offline assertion)
Assignee:    charanladi (Charan) + srikar
Label:       testing
Estimate:    1h
Due date:    2026-06-28
Description:
  tests/test_extraction.py — test JSON schema validation logic.
  tests/test_routes.py — test upload endpoint with mock audio.
  tests/test_offline.py — use pytest-socket to assert no network calls
  during whisper + ollama inference.

---

## ISSUE 10
Title:       Phase 1 — README, SPEC, CONTRIBUTING, CHANGELOG
Assignee:    charanladi (Charan)
Label:       docs, phase-1
Estimate:    30min
Due date:    2026-06-28
Description:
  Complete all Phase 1 documentation files. Push to main.
  Submit repo link to mentor Rajasekhar.
  ✅ DONE — closing this issue on first commit.
