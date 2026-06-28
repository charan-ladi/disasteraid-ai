# Work Division — DisasterAid AI

## Team

| Member | GitLab Username | Role |
|---|---|---|
| Srikar | @srikarrao | Frontend, OCR, Audio, Dashboard |
| Charan Ladi | @charanladi | Backend, LLM, DB, CI/CD |

---

## Phase 1 — Plan & Spec

| Task | Owner | Status |
|---|---|---|
| README | Srikar | ✅ Done |
| SPEC.md | Charan | ✅ Done |
| CONTRIBUTING.md | Charan | ✅ Done |
| CHANGELOG.md | Charan | ✅ Done |
| LICENSE (AGPLv3) | Srikar | ✅ Done |
| .gitlab-ci.yml | Charan | ✅ Done |
| requirements.txt | Charan | ✅ Done |
| .gitignore | Charan | ✅ Done |
| GitLab Issues (10) | Both | 🔄 In Progress |
| Work Division Plan | Charan | ✅ Done |

---

## Phase 2 — MVP

| Task | Owner | Estimate |
|---|---|---|
| Streamlit app skeleton + routing | Srikar | 1h |
| SQLite database + models | Srikar | 30min |
| PaddleOCR (image + video frames) | Srikar | 1h |
| Whisper audio transcription | Srikar | 1h |
| Dashboard UI + severity colors | Srikar | 1h |
| PDF extraction (PyMuPDF) | Charan | 45min |
| Ollama LLM extraction + prompt | Charan | 1h |
| JSON schema validation | Charan | 30min |
| CSV/JSON export | Charan | 30min |

---

## Phase 3 — Repo Audit

| Task | Owner | Estimate |
|---|---|---|
| CI/CD pipeline (10 stages) | Charan | 1.5h |
| pytest unit tests | Both | 1h |
| offline_test (pytest-socket) | Charan | 30min |
| pre-commit hooks setup | Charan | 20min |
| Final documentation cleanup | Both | 30min |

---

## Module Ownership

```
disasteraid-ai/
├── app.py                  → Srikar
├── database.py             → Srikar
├── utils/
│   ├── ocr.py              → Srikar
│   ├── speech.py           → Srikar
│   ├── video.py            → Srikar
│   ├── parser.py           → Charan
│   └── extractor.py        → Charan
├── scripts/
│   ├── validate_schema.py  → Charan
│   └── check_models.py     → Charan
├── tests/                  → Both
├── .gitlab-ci.yml          → Charan
└── requirements.txt        → Charan
```
