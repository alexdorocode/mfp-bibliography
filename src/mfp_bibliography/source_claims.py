"""Validation helpers for the normalized per-source claims contract."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

from mfp_bibliography.schemas import RecordValidationError, build_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_claims.schema.json"

CLAIM_FIELDNAMES = [
    "claim_id",
    "source_id",
    "source_record_id",
    "uniprot_id",
    "protein_name_raw",
    "organism_raw",
    "raw_claim_field",
    "raw_claim_value",
    "operational_status",
    "primary_target_eligible",
    "control_eligible",
    "raw_file_path",
    "raw_row_or_url",
    "source_version",
    "retrieved_at",
    "transformation_id",
    "record_status",
    "notes",
]
_BOOL_FIELDS = ("primary_target_eligible", "control_eligible")


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


def load_claim_policy(policy_path: str | Path) -> dict[str, Any]:
    """Load the declarative source claim policy YAML."""
    import yaml

    return yaml.safe_load(Path(policy_path).read_text(encoding="utf-8"))


def write_claims_csv(claims: list[dict[str, Any]], output_path: str | Path) -> None:
    """Write claims to CSV using the contract field order."""
    with Path(output_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLAIM_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for claim in claims:
            writer.writerow({name: _to_csv_value(claim[name]) for name in CLAIM_FIELDNAMES})


def read_claims_csv(csv_path: str | Path) -> list[dict[str, Any]]:
    """Read claims from CSV back into contract-shaped records."""
    claims: list[dict[str, Any]] = []
    with Path(csv_path).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            claim: dict[str, Any] = {}
            for name in CLAIM_FIELDNAMES:
                value = row[name]
                if name in _BOOL_FIELDS:
                    claim[name] = value.strip().lower() == "true"
                elif value == "":
                    claim[name] = None
                else:
                    claim[name] = value
            claims.append(claim)
    return claims


def _to_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
