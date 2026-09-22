"""Validation helpers for the normalized per-source claims contract."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from mfp_bibliography.schemas import RecordValidationError, build_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_claims.schema.json"


def make_claim_id(
    source_id: str,
    source_record_id: str,
    raw_file_path: str,
    raw_row_or_url: str,
    raw_claim_field: str,
) -> str:
    """Create a deterministic claim identifier from source identity and locator.

    The locator payload combines the source identity (source_id plus
    source_record_id), the raw artifact locator (raw_file_path plus
    raw_row_or_url), and the claim field, so distinct claim fields observed
    in the same source row yield distinct claim IDs.
    """
    payload = "::".join(
        part.strip()
        for part in (source_id, source_record_id, raw_file_path, raw_row_or_url, raw_claim_field)
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{source_id.strip()}:{digest}"


def validate_claim(claim: dict[str, Any], schema_path: Path = SOURCE_CLAIMS_SCHEMA_PATH) -> None:
    """Validate a single in-memory source claim and raise actionable errors if invalid."""
    validator = build_validator(schema_path)
    errors = sorted(validator.iter_errors(claim), key=lambda err: list(err.path))
    if not errors:
        return

    lines = ["Source claim validation failed:"]
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        lines.append(f"- {location}: {error.message}")
    raise RecordValidationError("\n".join(lines))
