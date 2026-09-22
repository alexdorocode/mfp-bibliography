"""Reproducible MoonDB source-claims adapter (MFPB_0_9_MOONDB_SOURCE_CLAIMS).

Maps each raw data row of the MoonDB artifact to one normalized per-source
claim per the source_claims contract. Status resolution goes only through
source_claim_policy_v0.1.yaml. One claim per raw row; duplicates are
preserved. No cross-source joins, no derived effective status.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from mfp_bibliography.provenance import sha256_file
from mfp_bibliography.schemas import RecordValidationError
from mfp_bibliography.source_claims import (
    load_claim_policy,
    make_claim_id,
    read_claims_csv,
    validate_claim,
    write_claims_csv,
)

CONTRACT_ID = "MFPB_0_9_MOONDB_SOURCE_CLAIMS"
MOONDB_SOURCE_ID = "SRC_MOONDB"
MOONDB_TRANSFORMATION_ID = "moondb_source_claims_v0"
UNIPROT_FIELD = "UniProtKB_ac"
RAW_CLAIM_FIELD = "type"


@dataclass(frozen=True)
class MoonDBProvenance:
    """Provenance metadata for the MoonDB raw artifact, from the source manifest."""

    source_version: str
    retrieved_at: str
    raw_file_path: str
    raw_sha256: str
    raw_row_count: int


def load_moondb_provenance(root: str | Path) -> MoonDBProvenance:
    """Load MoonDB provenance metadata from the source manifest."""
    manifest_path = Path(root) / "data" / "manifests" / "source_manifest.csv"
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["source_id"] == MOONDB_SOURCE_ID:
                return MoonDBProvenance(
                    source_version=row["source_version"],
                    retrieved_at=row["retrieved_at"],
                    raw_file_path=row["original_artifact_path"],
                    raw_sha256=row["sha256"],
                    raw_row_count=int(row["row_count_raw"]),
                )
    raise ValueError(f"No manifest row for source '{MOONDB_SOURCE_ID}'.")


def load_policy(policy_path: str | Path) -> dict[str, Any]:
    """Load the declarative source claim policy YAML."""
    return load_claim_policy(policy_path)


def resolve_operational_status(policy: dict[str, Any], raw_value: str | None) -> str:
    """Resolve an operational status strictly through the MoonDB policy mapping."""
    default_status = policy["default_status"]
    if raw_value is None or raw_value.strip() == "":
        return default_status
    mapping = policy["source_mappings"].get(MOONDB_SOURCE_ID, {})
    return mapping.get("value_map", {}).get(raw_value, default_status)


def iter_moondb_rows(raw_path: str | Path) -> Iterator[tuple[int, str, str]]:
    """Yield (file_line_number, uniprot_id, raw_type) for each raw data row.

    The line number is 1-based over the raw artifact file, so the first data
    row is line 2. Empty lines are skipped.
    """
    with Path(raw_path).open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return
        names = {name.lstrip("#").strip(): index for index, name in enumerate(header)}
        uniprot_index = names[UNIPROT_FIELD]
        type_index = names[RAW_CLAIM_FIELD]
        for line_number, row in enumerate(reader, start=2):
            if not row:
                continue
            yield line_number, row[uniprot_index].strip(), row[type_index].strip()


def build_moondb_claim(
    line_number: int,
    uniprot_id: str,
    raw_type: str,
    provenance: MoonDBProvenance,
    operational_status: str,
) -> dict[str, Any]:
    """Build one contract-compliant claim from a single raw data row."""
    raw_row_or_url = f"row:{line_number}"
    source_record_id = f"moondb_row_{line_number}"
    return {
        "claim_id": make_claim_id(
            MOONDB_SOURCE_ID,
            source_record_id,
            provenance.raw_file_path,
            raw_row_or_url,
            RAW_CLAIM_FIELD,
        ),
        "source_id": MOONDB_SOURCE_ID,
        "source_record_id": source_record_id,
        "uniprot_id": uniprot_id or None,
        "protein_name_raw": None,
        "organism_raw": None,
        "raw_claim_field": RAW_CLAIM_FIELD,
        "raw_claim_value": raw_type or "unknown",
        "operational_status": operational_status,
        "primary_target_eligible": operational_status == "curated",
        "control_eligible": False,
        "raw_file_path": provenance.raw_file_path,
        "raw_row_or_url": raw_row_or_url,
        "source_version": provenance.source_version,
        "retrieved_at": provenance.retrieved_at,
        "transformation_id": MOONDB_TRANSFORMATION_ID,
        "record_status": "valid",
        "notes": None,
    }


def adapt_moondb_claims(
    raw_path: str | Path,
    policy: dict[str, Any],
    provenance: MoonDBProvenance,
) -> list[dict[str, Any]]:
    """Adapt every raw data row into one claim; duplicates are preserved."""
    policy_field = policy["source_mappings"].get(MOONDB_SOURCE_ID, {}).get("field")
    if policy_field != RAW_CLAIM_FIELD:
        raise ValueError(
            f"Policy claim field '{policy_field}' is not a permitted MoonDB raw field."
        )
    claims: list[dict[str, Any]] = []
    for line_number, uniprot_id, raw_type in iter_moondb_rows(raw_path):
        status = resolve_operational_status(policy, raw_type)
        claims.append(
            build_moondb_claim(line_number, uniprot_id, raw_type, provenance, status)
        )
    return claims


def build_validation_report(
    claims: list[dict[str, Any]],
    raw_path: str | Path,
    provenance: MoonDBProvenance,
) -> dict[str, Any]:
    """Build the claims validation report with counts and integrity checks."""
    schema_invalid: list[int] = []
    for index, claim in enumerate(claims):
        try:
            validate_claim(claim)
        except RecordValidationError:
            schema_invalid.append(index)

    raw_sha256 = sha256_file(raw_path)
    claim_ids = [claim["claim_id"] for claim in claims]
    ids_deterministic = all(
        claim["claim_id"]
        == make_claim_id(
            claim["source_id"],
            claim["source_record_id"],
            claim["raw_file_path"],
            claim["raw_row_or_url"],
            claim["raw_claim_field"],
        )
        for claim in claims
    )
    provenance_complete = all(
        claim["raw_file_path"] == provenance.raw_file_path
        and claim["raw_row_or_url"]
        and claim["source_version"]
        and claim["retrieved_at"]
        and claim["transformation_id"]
        for claim in claims
    )
    counts_by_raw_type = dict(sorted(Counter(c["raw_claim_value"] for c in claims).items()))
    counts_by_status = dict(sorted(Counter(c["operational_status"] for c in claims).items()))

    checks = {
        "raw_sha256_matches_manifest": raw_sha256 == provenance.raw_sha256,
        "claim_count_matches_manifest_row_count": len(claims) == provenance.raw_row_count,
        "all_claims_pass_schema": not schema_invalid,
        "claim_ids_unique": len(set(claim_ids)) == len(claim_ids),
        "claim_ids_deterministic": ids_deterministic,
        "provenance_complete": provenance_complete,
        "no_control_eligible": not any(c["control_eligible"] for c in claims),
        "primary_target_eligible_only_curated": all(
            c["primary_target_eligible"] == (c["operational_status"] == "curated") for c in claims
        ),
    }
    return {
        "contract_id": CONTRACT_ID,
        "source_id": MOONDB_SOURCE_ID,
        "raw_artifact_path": provenance.raw_file_path,
        "raw_sha256": raw_sha256,
        "manifest_row_count_raw": provenance.raw_row_count,
        "claim_count": len(claims),
        "counts_by_raw_type": counts_by_raw_type,
        "counts_by_operational_status": counts_by_status,
        "primary_target_eligible_count": sum(
            1 for c in claims if c["primary_target_eligible"]
        ),
        "schema_invalid_indices": schema_invalid,
        "checks": checks,
        "reconciliation_ok": all(checks.values()),
    }
