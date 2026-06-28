# SabhaLekhan — Technical Specification

## 1. Overview

**Project Name:** SabhaLekhan  
**Type:** Offline-first Web App (Flask + PWA)  
**Input:** Audio files (.wav, .mp3, .ogg) — up to 30 minutes  
**Output:** Structured JSON record + SQLite persistence  
**Model Runtime:** faster-whisper (CPU) + Ollama llama3.2:3b (CPU)  
**License:** AGPLv3  

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Flask Web Server                   │
│                  localhost:5000                      │
│                                                     │
│  ┌──────────┐   ┌────────────┐   ┌──────────────┐  │
│  │  Upload  │──▶│  Whisper   │──▶│    Ollama    │  │
│  │ Handler  │   │  Engine    │   │  Extractor   │  │
│  └──────────┘   └────────────┘   └──────┬───────┘  │
│                                         │           │
│                                  ┌──────▼───────┐  │
│                                  │   SQLite DB  │  │
│                                  │  sessions.db │  │
│                                  └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 3. Input Specification

| Property | Detail |
|---|---|
| Accepted formats | `.wav`, `.mp3`, `.ogg` |
| Max file size | 100 MB |
| Max duration | 30 minutes |
| Language | English (Phase 1); Telugu planned (Phase 2) |
| Upload method | HTTP multipart form / drag-drop UI |

---

## 4. Processing Pipeline

### Stage 1 — Audio Ingestion
- Validate file format and size
- Convert to 16kHz mono WAV if needed (via `pydub`)
- Save to `uploads/` temp directory

### Stage 2 — Transcription (faster-whisper)
- Model: `tiny.en` (GGUF quantized, ~75MB)
- Device: `cpu`, compute_type: `int8`
- Output: raw transcript string + word-level timestamps
- Graceful failure: if model not found, return error JSON with `"status": "model_missing"`

### Stage 3 — Structured Extraction (Ollama + llama3.2:3b)
- Prompt template fills transcript into extraction prompt
- Model returns JSON matching output schema
- Validation via `jsonschema` — reject and retry once if invalid
- Graceful failure: if Ollama unreachable, return raw transcript with `"status": "extraction_failed"`

### Stage 4 — Persistence (SQLite)
- Insert validated record into `sessions` table
- Assign UUID session_id
- Index on `recorded_at`

---

## 5. Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema",
  "type": "object",
  "required": ["session_id", "recorded_at", "transcript_raw", "action_items"],
  "properties": {
    "session_id":           { "type": "string", "format": "uuid" },
    "recorded_at":          { "type": "string", "format": "date-time" },
    "duration_seconds":     { "type": "integer" },
    "language_detected":    { "type": "string" },
    "transcript_raw":       { "type": "string" },
    "participants_detected":{ "type": "array", "items": { "type": "string" } },
    "agenda_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "item":      { "type": "string" },
          "discussed": { "type": "boolean" }
        }
      }
    },
    "decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "decision":  { "type": "string" },
          "unanimous": { "type": "boolean" }
        }
      }
    },
    "action_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task":     { "type": "string" },
          "owner":    { "type": "string" },
          "deadline": { "type": "string" }
        }
      }
    },
    "summary": { "type": "string" },
    "status":  { "type": "string", "enum": ["ok", "extraction_failed", "model_missing"] }
  }
}
```

---

## 6. Database Schema

```sql
CREATE TABLE sessions (
    id              TEXT PRIMARY KEY,
    recorded_at     TEXT NOT NULL,
    duration_sec    INTEGER,
    audio_filename  TEXT,
    transcript_raw  TEXT,
    structured_json TEXT,
    status          TEXT DEFAULT 'ok',
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main upload UI |
| `POST` | `/upload` | Upload audio, trigger pipeline |
| `GET` | `/sessions` | List all past sessions |
| `GET` | `/sessions/<id>` | View single session JSON |
| `GET` | `/sessions/<id>/export` | Download as CSV |
| `GET` | `/health` | Health check (offline indicator) |

---

## 8. Offline Guarantee

- All models are downloaded once and stored locally
- No requests to `api.anthropic.com`, `api.openai.com`, or any external host during inference
- `GET /health` returns `{"offline_ready": true}` when both Whisper model and Ollama are available locally
- CI has an `offline_test` stage that asserts zero outbound network calls during inference using `mitmproxy` or `pytest-socket`

---

## 9. CI/CD Pipeline Stages

| Stage | Tool | Check |
|---|---|---|
| `lint` | `ruff` | PEP8 + code style |
| `format` | `black` | Auto-formatting |
| `type_check` | `mypy` | Static type validation |
| `security` | `bandit` | Security vulnerability scan |
| `test` | `pytest` | Unit + integration tests |
| `coverage` | `pytest-cov` | Minimum 80% coverage |
| `schema_validate` | `jsonschema` | Output schema conformance |
| `model_check` | custom script | Assert Ollama + Whisper available |
| `offline_test` | `pytest-socket` | Assert no network calls during inference |
| `build` | `pip check` | Dependency integrity |

---

## 10. Work Division

| Task | Owner | Estimate | Due |
|---|---|---|---|
| Flask app skeleton + routing | Charan | 1h | Phase 2 |
| SQLite models + DB init | Charan | 30min | Phase 2 |
| CI/CD pipeline (10 stages) | Charan | 1.5h | Phase 3 |
| Audio upload + validation | Srikar | 45min | Phase 2 |
| faster-whisper integration | Srikar | 1h | Phase 2 |
| Frontend UI (upload + results) | Srikar | 1h | Phase 2 |
| Ollama extraction + prompt | Charan | 1h | Phase 2 |
| JSON schema validation | Charan | 30min | Phase 2 |
| Tests (pytest) | Both | 1h | Phase 3 |
| Export (CSV/JSON) | Srikar | 30min | Phase 2 |
