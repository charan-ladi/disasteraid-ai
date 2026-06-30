"""
scripts/validate_schema.py
CI check: validates that the extractor's output schema is well-formed
and that a sample extraction produces schema-valid output structure
(without requiring Ollama to be running, using a mock response).
"""

import sys

from jsonschema import Draft7Validator

from utils.extractor import OUTPUT_SCHEMA


def main() -> int:
    try:
        Draft7Validator.check_schema(OUTPUT_SCHEMA)
        print("✅ OUTPUT_SCHEMA is a valid JSON Schema.")
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return 1

    sample_record = {
        "disaster_type": "Flood",
        "severity": "Critical",
        "people_trapped": 4,
        "children": 2,
        "elderly": 1,
        "injuries": True,
        "medical_help": True,
        "food_needed": True,
        "water_needed": True,
        "location": "Old Bridge",
        "priority_score": 96,
        "status": "Immediate Rescue",
    }

    validator = Draft7Validator(OUTPUT_SCHEMA)
    errors = list(validator.iter_errors(sample_record))
    if errors:
        print(f"❌ Sample record failed validation: {errors}")
        return 1

    print("✅ Sample record passes schema validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
