# Extraction Prompt (used by utils/parser.py -> llm_parse)

This is the prompt sent to a local Ollama model (e.g. `phi3:mini` or
`tinyllama`) when you enable LLM-based extraction (`parse_text(text, prefer_llm=True)`).

```
You are an offline disaster-report extraction engine.
Read the report below and return ONLY a single valid JSON object (no prose,
no markdown fences) with these exact keys:

disaster_type (string), people_trapped (int), children (int), elderly (int),
injuries (bool), medical_help (bool), food_needed (bool), water_needed (bool),
location (string), severity (one of "Low","Moderate","High","Critical"),
priority_score (int 0-100)

Report:
"""{text}"""

JSON:
```

## To enable this:
1. Install Ollama: https://ollama.com
2. Pull a small CPU-friendly model: `ollama pull phi3:mini`
3. In `utils/parser.py`, the app will automatically use the LLM when
   `parse_text(text, prefer_llm=True)` is called and Ollama is reachable on
   `localhost:11434`. If unreachable, it silently falls back to the
   rule-based engine — the app never breaks.
