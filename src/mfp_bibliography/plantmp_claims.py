"""Reproducible PlantMP source-claims adapter.

Maps each raw data row of the PlantMP artifact to one normalized per-source
claim per the source_claims contract. Status resolution goes only through
source_claim_policy_v0.1.yaml (confirmed -> curated, predicted -> predicted,
likely -> excluded_likely; unmapped or missing values -> unresolved). One
claim per raw row; duplicate uniport_id values are preserved. No cross-source
joins, no derived effective status, no NMF controls.
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
    validate_claim,
)

CONTRACT_ID = "MFPB_0_10_PLANTMP_SOURCE_CLAIMS"
PLANTMP_SOURCE_ID = "SRC_PLANTMP"
PLANTMP_TRANSFORMATION_ID = "plantmp_source_claims_v0"
ORDER_FIELD = "order"
NAME_FIELD = "protein name, gene"
UNIPROT_FIELD = "uniport_id"
ORGANISM_FIELD = "plant_species"
RAW_CLAIM_FIELD = "type"


@dataclass(frozen=True)
class PlantMPProvenance:
    """Provenance metadata for the PlantMP raw artifact, from the source manifest."""

    source_version: str
    retrieved_at: str
    raw_file_path: str
    raw_sha256: str
    raw_row_count: int


def load_plantmp_provenance(root: str | Path) -> PlantMPProvenance:
    """Load PlantMP provenance metadata from the source manifest."""
    manifest_path = Path(root) / "data" / "manifests" / "source_manifest.csv"
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["source_id"] == PLANTMP_SOURCE_ID:
                return PlantMPProvenance(
                    source_version=row["source_version"],
                    retrieved_at=row["retrieved_at"],
                    raw_file_path=row["original_artifact_path"],
                    raw_sha256=row["sha256"],
                    raw_row_count=int(row["row_count_raw"]),
                )
    raise ValueError(f"No manifest row for source '{PLANTMP_SOURCE_ID}'.")


def load_policy(policy_path: str | Path) -> dict[str, Any]:
    """Load the declarative source claim policy YAML."""
    return load_claim_policy(policy_path)


def resolve_operational_status(policy: dict[str, Any], raw_value: str | None) -> str:
    """Resolve an operational status strictly through the PlantMP policy mapping."""
    default_status = policy["default_status"]
    if raw_value is None or raw_value.strip() == "":
        return default_status
    mapping = policy["source_mappings"].get(PLANTMP_SOURCE_ID, {})
    return mapping.get("value_map", {}).get(raw_value, default_status)


def iter_plantmp_rows(raw_path: str | Path) -> Iterator[dict[str, str]]:
    """Yield one stripped-field dict per raw data row, in file order.

    Rows are keyed by the native ``order`` column, which uniquely identifies
    each raw row. The raw artifact contains embedded newlines inside quoted
    fields, so physical line numbers are not reliable row locators.
    """
    with Path(raw_path).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not any((value or "").strip() for value in row.values()):
                continue
            yield {
                name: (value or "").strip() for name, value in row.items() if name is not None
            }


def build_plantmp_claim(
    raw_row: dict[str, str],
    provenance: PlantMPProvenance,
    operational_status: str,
) -> dict[str, Any]:
    """Build one contract-compliant claim from a single raw data row."""
    order = raw_row[ORDER_FIELD]
    if not order:
        raise ValueError("PlantMP raw row is missing its 'order' identifier.")
    raw_row_or_url = f"order:{order}"
    source_record_id = f"plantmp_order_{order}"
    raw_type = raw_row.get(RAW_CLAIM_FIELD, "")
    return {
        "claim_id": make_claim_id(
            PLANTMP_SOURCE_ID,
            source_record_id,
            provenance.raw_file_path,
            raw_row_or_url,
            RAW_CLAIM_FIELD,
        ),
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": source_record_id,
        "uniprot_id": raw_row.get(UNIPROT_FIELD, "") or None,
        "protein_name_raw": raw_row.get(NAME_FIELD, "") or None,
        "organism_raw": raw_row.get(ORGANISM_FIELD, "") or None,
        "raw_claim_field": RAW_CLAIM_FIELD,
        "raw_claim_value": raw_type or "unknown",
        "operational_status": operational_status,
        "primary_target_eligible": operational_status == "curated",
        "control_eligible": False,
        "raw_file_path": provenance.raw_file_path,
        "raw_row_or_url": raw_row_or_url,
        "source_version": provenance.source_version,
        "retrieved_at": provenance.retrieved_at,
        "transformation_id": PLANTMP_TRANSFORMATION_ID,
        "record_status": "valid",
        "notes": None,
    }


def adapt_plantmp_claims(
    raw_path: str | Path,
    policy: dict[str, Any],
    provenance: PlantMPProvenance,
) -> list[dict[str, Any]]:
    """Adapt every raw data row into one claim; duplicates are preserved."""
    policy_field = policy["source_mappings"].get(PLANTMP_SOURCE_ID, {}).get("field")
    if policy_field != RAW_CLAIM_FIELD:
        raise ValueError(
            f"Policy claim field '{policy_field}' is not a permitted PlantMP raw field."
        )
    claims: list[dict[str, Any]] = []
    for raw_row in iter_plantmp_rows(raw_path):
        status = resolve_operational_status(policy, raw_row.get(RAW_CLAIM_FIELD, ""))
        claims.append(build_plantmp_claim(raw_row, provenance, status))
    return claims


def build_validation_report(
    claims: list[dict[str, Any]],
    raw_path: str | Path,
    provenance: PlantMPProvenance,
    policy: dict[str, Any],
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
        and claim["source_record_id"]
        and claim["raw_claim_value"]
        and claim["source_version"]
        and claim["retrieved_at"]
        and claim["transformation_id"]
        for claim in claims
    )
    status_matches_policy = all(
        claim["operational_status"]
        == resolve_operational_status(policy, claim["raw_claim_value"])
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
        "status_matches_policy": status_matches_policy,
    }
    return {
        "contract_id": CONTRACT_ID,
        "source_id": PLANTMP_SOURCE_ID,
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
