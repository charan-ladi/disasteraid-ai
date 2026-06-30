"""
utils/extractor.py
Sends extracted text to a local Ollama model (TinyLlama / Phi-3 Mini)
and parses the response into a validated structured JSON record.
Runs entirely on CPU, fully offline (assuming the model is already pulled).
"""

import json
import re

import ollama
from jsonschema import ValidationError, validate

MODEL_NAME = "tinyllama"

OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["disaster_type", "severity", "priority_score"],
    "properties": {
        "disaster_type": {"type": "string"},
        "severity": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"]},
        "people_trapped": {"type": "integer"},
        "children": {"type": "integer"},
        "elderly": {"type": "integer"},
        "injuries": {"type": "boolean"},
        "medical_help": {"type": "boolean"},
        "food_needed": {"type": "boolean"},
        "water_needed": {"type": "boolean"},
        "location": {"type": "string"},
        "priority_score": {"type": "integer"},
        "status": {"type": "string"},
    },
}

PROMPT_TEMPLATE = """You are an emergency report analyst. Read the disaster report below
and extract structured information. Respond with ONLY a valid JSON object,
no extra text, no markdown formatting.

Required JSON fields:
- disaster_type (string, e.g. Flood, Earthquake, Fire, Cyclone, Landslide)
- severity (one of: Critical, High, Medium, Low)
- people_trapped (integer)
- children (integer)
- elderly (integer)
- injuries (boolean)
- medical_help (boolean)
- food_needed (boolean)
- water_needed (boolean)
- location (string)
- priority_score (integer 0-100, higher = more urgent)
- status (string, e.g. "Immediate Rescue", "Monitoring", "Resolved")

Report:
\"\"\"{text}\"\"\"

JSON:"""


def _extract_json_block(raw_text: str) -> str:
    """Pull the first {...} block out of a model response."""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response")
    return match.group(0)


def extract_structured_data(text: str) -> dict:
    """
    Send raw extracted text to the local Ollama model and return
    a validated structured dict. Retries once on invalid JSON.
    Returns a dict with status='extraction_failed' if Ollama is unreachable.
    """
    prompt = PROMPT_TEMPLATE.format(text=text.strip()[:4000])

    for attempt in range(2):
        try:
            response = ollama.generate(model=MODEL_NAME, prompt=prompt)
            raw_output = response.get("response", "")
            json_str = _extract_json_block(raw_output)
            parsed = json.loads(json_str)
            validate(instance=parsed, schema=OUTPUT_SCHEMA)
            parsed["status"] = parsed.get("status", "ok")
            return parsed
        except (ValueError, json.JSONDecodeError, ValidationError):
            if attempt == 1:
                return {
                    "disaster_type": "Unknown",
                    "severity": "Unknown",
                    "priority_score": 0,
                    "status": "extraction_failed",
                    "raw_text": text[:500],
                }
            continue
        except Exception:
            # Ollama not running / model not pulled
            return {
                "disaster_type": "Unknown",
                "severity": "Unknown",
                "priority_score": 0,
                "status": "model_missing",
                "raw_text": text[:500],
            }

    return {"status": "extraction_failed", "raw_text": text[:500]}


if __name__ == "__main__":
    sample = (
        "Four people are trapped on the terrace near the old bridge. "
        "Water level is rising rapidly. One elderly person requires "
        "immediate medical assistance."
    )
    result = extract_structured_data(sample)
    print(json.dumps(result, indent=2))
