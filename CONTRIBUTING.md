# Contributing to DisasterAid AI

## Getting Started

1. Clone the repo:
   ```bash
   git clone https://code.swecha.org/srikarrao/disasteraid-ai.git
   cd disasteraid-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

3. Pull local models (one-time, needs internet):
   ```bash
   ollama pull tinyllama
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Run tests:
   ```bash
   pytest tests/
   ```

---

## Commit Message Format (Semantic Commits)

```
feat: add PDF extraction via PyMuPDF
fix: handle empty audio file gracefully
docs: update SPEC with new schema fields
test: add unit test for ollama extractor
ci: add offline_test stage to pipeline
refactor: clean up OCR preprocessing logic
```

## Branch Naming

```
feat/ocr-integration
fix/empty-audio-crash
docs/spec-update
charan/pdf-extraction
srikar/dashboard-ui
```

## Code Standards

- Formatter: `black` (line length 88)
- Linter: `ruff`
- Type checker: `mypy`
- Security: `bandit`
- All commits must pass pre-commit hooks
- All PRs must pass the full CI pipeline before merge

## Pre-commit Setup

```bash
pip install pre-commit --break-system-packages
pre-commit install
```

## Reporting Issues

Open a GitLab issue with:
- Steps to reproduce
- Expected vs actual behavior
- OS + Python version
- Input type that caused the issue (image/audio/video/pdf/text)
