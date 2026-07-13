"""
parser.py
----------
Converts free-text disaster reports into structured emergency JSON records.

This module is FULLY OFFLINE and requires NO external model, NO internet,
and NO GPU. It works out of the box using regex + keyword rules.

If a local LLM (Ollama / TinyLlama / Phi-3 Mini) is available, `parse_text()`
will automatically prefer it for higher accuracy and fall back to the
rule-based engine if the LLM is unreachable. This gives you:
  - guaranteed output even with zero setup (rule-based)
  - higher quality output once you wire up a local LLM (optional upgrade)
"""

import re
import json

try:
    import requests

    _REQUESTS_AVAILABLE = True
except Exception:
    _REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Optional local LLM (Ollama) integration
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:mini"  # or "tinyllama"
OLLAMA_TIMEOUT = 4  # seconds - fail fast, fall back to rules

LLM_PROMPT_TEMPLATE = """You are an offline disaster-report extraction engine.
Read the report below and return ONLY a single valid JSON object (no prose,
no markdown fences) with these exact keys:

disaster_type (string), people_trapped (int), children (int), elderly (int),
injuries (bool), medical_help (bool), food_needed (bool), water_needed (bool),
location (string), severity (one of "Low","Moderate","High","Critical"),
priority_score (int 0-100)

Report:
\"\"\"{text}\"\"\"

JSON:"""


DISASTER_KEYWORDS = {
    "Flood": [
        "flood",
        "water level",
        "rising water",
        "submerged",
        "waterlogged",
        "inundat",
    ],
    "Earthquake": ["earthquake", "tremor", "collapsed building", "aftershock", "quake"],
    "Cyclone": ["cyclone", "hurricane", "storm surge", "high wind", "typhoon"],
    "Landslide": ["landslide", "mudslide", "slope collapse", "debris flow"],
    "Fire": ["fire", "blaze", "burning", "smoke", "wildfire"],
}

SEVERITY_KEYWORDS = {
    "Critical": [
        "immediate",
        "critical",
        "dying",
        "trapped",
        "drowning",
        "unconscious",
        "life-threatening",
        "urgent",
    ],
    "High": ["severe", "serious", "rapidly rising", "many people", "injured"],
    "Moderate": ["moderate", "some damage", "minor injuries"],
    "Low": ["minor", "stable", "under control"],
}

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "a": 1,
    "single": 1,
    "couple": 2,
    "few": 3,
    "several": 5,
}


def _word_to_number(token):
    token = token.lower().strip()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def _find_count_near(text, keywords, window=6):
    """Look for a number within `window` words before/after any keyword."""
    words = re.findall(r"[A-Za-z]+|\d+", text.lower())
    for kw in keywords:
        kw_tokens = kw.split()
        kw_len = len(kw_tokens)
        for i in range(len(words) - kw_len + 1):
            if words[i : i + kw_len] == kw_tokens:
                lo, hi = max(0, i - window), min(len(words), i + kw_len + window)
                for j in list(range(i - 1, lo - 1, -1)) + list(range(i + kw_len, hi)):
                    n = _word_to_number(words[j])
                    if n:
                        return n
    return 0


def _detect_disaster_type(text):
    text_l = text.lower()
    scores = {}
    for dtype, kws in DISASTER_KEYWORDS.items():
        scores[dtype] = sum(text_l.count(kw) for kw in kws)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Unspecified"


def _detect_severity(text):
    text_l = text.lower()
    for level in ["Critical", "High", "Moderate", "Low"]:
        for kw in SEVERITY_KEYWORDS[level]:
            if kw in text_l:
                return level
    return "Moderate"


def _detect_location(text):
    # Looks for "near <place>", "at <place>", "in <place>"
    m = re.search(
        r"\b(?:near|at|in)\s+(?:the\s+)?([A-Za-z][A-Za-z\s]{2,40}?)(?:[.,]|$)", text
    )
    if m:
        return m.group(1).strip().title()
    return "Unknown"


def _yes_no(text, keywords):
    text_l = text.lower()
    return any(kw in text_l for kw in keywords)


def _priority_score(severity, people_trapped, medical_help, injuries):
    base = {"Critical": 80, "High": 60, "Moderate": 35, "Low": 15}.get(severity, 35)
    base += min(people_trapped * 3, 15)
    base += 5 if medical_help else 0
    base += 5 if injuries else 0
    return min(base, 100)


def clean_text(text: str) -> str:
    """Normalize whitespace and newlines."""
    if not text:
        return ""
    return " ".join(text.split())


def rule_based_parse(text):
    """Deterministic, offline, no-dependency extraction. Always works."""
    disaster_type = _detect_disaster_type(text)
    severity = _detect_severity(text)
    people_trapped = _find_count_near(text, ["trapped", "stranded", "stuck"])
    children = _find_count_near(text, ["child", "children", "kids"])
    elderly = _find_count_near(text, ["elderly", "old", "aged"])
    injuries = _yes_no(text, ["injur", "wound", "hurt", "bleeding"])
    medical_help = _yes_no(
        text, ["medical", "ambulance", "doctor", "first aid", "hospital"]
    )
    food_needed = _yes_no(text, ["food", "hungry", "ration", "starving"])
    water_needed = _yes_no(
        text, ["no water", "drinking water", "water shortage", "need water", "thirsty"]
    )
    location = _detect_location(text)
    priority = _priority_score(severity, people_trapped, medical_help, injuries)

    return {
        "disaster_type": disaster_type,
        "people_trapped": people_trapped,
        "children": children,
        "elderly": elderly,
        "injuries": injuries,
        "medical_help": medical_help,
        "food_needed": food_needed,
        "water_needed": water_needed,
        "location": location,
        "severity": severity,
        "priority_score": priority,
        "status": (
            "Immediate Rescue"
            if priority >= 75
            else "Urgent" if priority >= 50 else "Monitor"
        ),
        "engine": "rule_based",
    }


def llm_parse(text):
    """Try a local Ollama model for higher-quality extraction. Raises on failure."""
    if not _REQUESTS_AVAILABLE:
        raise RuntimeError("requests library not installed")
    prompt = LLM_PROMPT_TEMPLATE.format(text=text.strip())
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    raw = resp.json().get("response", "")
    raw = raw.strip().strip("`")
    if raw.lower().startswith("json"):
        raw = raw[4:]
    data = json.loads(raw)
    data["engine"] = "local_llm:" + OLLAMA_MODEL
    if "status" not in data:
        score = data.get("priority_score", 50)
        data["status"] = (
            "Immediate Rescue"
            if score >= 75
            else "Urgent" if score >= 50 else "Monitor"
        )
    return data


def parse_text(text, prefer_llm=False):
    """
    Main entry point. Tries the local LLM first (if prefer_llm=True and Ollama
    is reachable), otherwise instantly falls back to the rule-based engine.
    This means the app ALWAYS produces output, with or without a local model.
    """
    if not text or not text.strip():
        raise ValueError("Empty text supplied to parse_text()")

    text = clean_text(text)

    if prefer_llm:
        try:
            return llm_parse(text)
        except Exception:
            pass  # silently fall back - no internet / no Ollama running locally

    return rule_based_parse(text)


if __name__ == "__main__":
    sample = (
        "Four people are trapped on the terrace near the old bridge. "
        "Water level is rising rapidly. One elderly person requires "
        "immediate medical assistance."
    )
    print(json.dumps(parse_text(sample, prefer_llm=False), indent=2))
