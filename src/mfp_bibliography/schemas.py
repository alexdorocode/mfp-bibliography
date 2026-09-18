"""Schema loading and record validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "mfp_source_records.schema.json"


class RecordValidationError(ValueError):
    """Raised when a record fails schema validation."""


def load_schema(schema_path: Path = SCHEMA_PATH) -> dict[str, Any]:
    """Load and return the canonical JSON schema."""
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_validator(schema_path: Path = SCHEMA_PATH) -> Draft202012Validator:
    """Build a JSON Schema Draft 2020-12 validator for source records."""
    schema = load_schema(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_record(record: dict[str, Any], schema_path: Path = SCHEMA_PATH) -> None:
    """Validate a single in-memory record and raise actionable errors if invalid."""
    validator = build_validator(schema_path)
    errors = sorted(validator.iter_errors(record), key=lambda err: list(err.path))
    if not errors:
        return

    lines = ["Record validation failed:"]
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        lines.append(f"- {location}: {error.message}")
    raise RecordValidationError("\n".join(lines))
