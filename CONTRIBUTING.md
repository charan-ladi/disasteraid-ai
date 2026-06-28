# Contributing to SabhaLekhan

## Getting Started

1. Fork the repo and clone it locally
2. Install dependencies: `pip install -r requirements.txt --break-system-packages`
3. Pull the local model: `ollama pull llama3.2:3b`
4. Run tests: `pytest tests/`
5. Run the app: `flask run`

## Commit Message Format (Semantic Commits)

```
feat: add Telugu language support
fix: handle empty audio file gracefully
docs: update SPEC with new schema fields
test: add unit test for ollama extractor
ci: add offline_test stage to pipeline
```

## Branch Naming

```
feat/whisper-integration
fix/empty-audio-crash
docs/spec-update
```

## Code Standards

- Formatter: `black` (line length 88)
- Linter: `ruff`
- Type checker: `mypy`
- Security: `bandit`
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
