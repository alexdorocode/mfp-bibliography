"""MultifacetedProtDB interim source-record adapter (local-only, not catalog-integrated).

Reads the canonical artifact ``MultifacetedProtDB_data.json`` — a single-quoted
Python literal, NOT strict JSON — with ``ast.literal_eval`` (never ``eval``),
validates shape and accessions, and emits one deterministic interim source
record per valid entry.

Scope boundaries:
- The output is a SOURCE-RECORD artifact, not a claims artifact and not a
  catalog input. MultifacetedProtDB is NOT YET INCLUDED in the catalog.
- The source provides no explicit status field; ``status_original`` stays
  empty (absent) and ``operational_status`` is only the neutral default
  allowed by the source-claim policy for unmapped sources. Inclusion is
  membership, not evidence; no claim is invented.
- ``annotation`` numeric values are preserved verbatim; their semantics are
  unknown and are never interpreted as status or evidence.
"""

from __future__ import annotations

import ast
import csv
import hashlib
from pathlib import Path
from typing import Any

from mfp_bibliography.normalization import normalize_uniprot_accession

MULTIFACETEDPROTDB_SOURCE_ID = "SRC_MULTIFACETEDPROTDB"
TRANSFORMATION_ID = "multifacetedprotdb_source_records_v0"
EXPECTED_FIELDS = ("uniprot", "name", "genes", "annotation")

RECORD_COLUMNS = [
    "source_id", "source_record_id", "row_index",
    "uniprot_raw", "uniprot_normalized", "name_raw", "genes_raw",
    "annotation_raw", "status_original", "operational_status",
    "raw_file_path", "raw_file_sha256", "transformation_id", "record_status",
]


class MultifacetedProtDBFormatError(ValueError):
    """The artifact is not the expected single-quoted Python-literal structure."""


class MultifacetedProtDBRecordError(ValueError):
    """A record fails accession or integrity validation."""


def parse_literal_payload(text: str) -> dict[str, Any]:
    """Parse the artifact with ``ast.literal_eval`` (never ``eval``).

    The artifact is a single-quoted Python literal and is not strict JSON;
    ``json.loads`` must not be used.
    """
    try:
        payload = ast.literal_eval(text)
    except (SyntaxError, ValueError) as exc:
        raise MultifacetedProtDBFormatError(
            f"artifact is not a parseable Python literal (it is not strict JSON): {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise MultifacetedProtDBFormatError(
            f"top level must be a dict, got {type(payload).__name__}"
        )
    if set(payload.keys()) != {"protein"}:
        raise MultifacetedProtDBFormatError(
            f"top level must contain exactly the 'protein' key, got {sorted(payload.keys())}"
        )
    if not isinstance(payload["protein"], list):
        raise MultifacetedProtDBFormatError(
            f"'protein' must be a list, got {type(payload['protein']).__name__}"
        )
    return payload


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_source_records(
    raw_path: str | Path,
    expected_sha256: str | None = None,
) -> list[dict[str, str]]:
    """Load and validate source records from the canonical artifact.

    Rejects hash mismatch, malformed shape, missing/extra fields, missing or
    malformed accessions, and duplicate normalized accessions — always with
    exact diagnostics; nothing is silently discarded or merged.
    """
    raw_path = Path(raw_path)
    data = raw_path.read_bytes()
    actual_sha256 = _sha256_bytes(data)
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise MultifacetedProtDBRecordError(
            f"raw artifact hash mismatch for {raw_path}: "
            f"manifest {expected_sha256}, actual {actual_sha256}"
        )

    payload = parse_literal_payload(data.decode("utf-8"))
    entries = payload["protein"]

    records: list[dict[str, str]] = []
    seen: dict[str, int] = {}
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise MultifacetedProtDBRecordError(
                f"record {index}: entry must be a dict, got {type(entry).__name__}"
            )
        if set(entry.keys()) != set(EXPECTED_FIELDS):
            raise MultifacetedProtDBRecordError(
                f"record {index}: expected exactly fields {sorted(EXPECTED_FIELDS)}, "
                f"got {sorted(entry.keys())}"
            )
        uniprot_raw = entry["uniprot"]
        if not isinstance(uniprot_raw, str) or not uniprot_raw.strip():
            raise MultifacetedProtDBRecordError(
                f"record {index}: 'uniprot' must be a non-empty string, got {uniprot_raw!r}"
            )
        normalized = normalize_uniprot_accession(uniprot_raw)
        if normalized is None:
            raise MultifacetedProtDBRecordError(
                f"record {index}: 'uniprot' does not normalize to an accession: {uniprot_raw!r}"
            )
        if normalized in seen:
            raise MultifacetedProtDBRecordError(
                f"record {index}: duplicate normalized accession {normalized!r} "
                f"(also at record {seen[normalized]})"
            )
        seen[normalized] = index
        for field in ("name", "genes"):
            if not isinstance(entry[field], str):
                raise MultifacetedProtDBRecordError(
                    f"record {index}: {field!r} must be a string, got {entry[field]!r}"
                )
        annotation = entry["annotation"]
        if not isinstance(annotation, (int, float)) or isinstance(annotation, bool):
            raise MultifacetedProtDBRecordError(
                f"record {index}: 'annotation' must be numeric, got {annotation!r}"
            )
        records.append({
            "source_id": MULTIFACETEDPROTDB_SOURCE_ID,
            "source_record_id": f"multifacetedprotdb_row_{index}",
            "row_index": str(index),
            "uniprot_raw": uniprot_raw,
            "uniprot_normalized": normalized,
            "name_raw": entry["name"],
            "genes_raw": entry["genes"],
            "annotation_raw": str(annotation),
            "raw_file_path": str(raw_path),
            "raw_file_sha256": actual_sha256,
        })
    return records


def resolve_operational_status(policy: dict[str, Any]) -> str:
    """Neutral operational status: the policy default for unmapped sources."""
    unmapped = policy.get("unmapped_sources", [])
    if MULTIFACETEDPROTDB_SOURCE_ID not in unmapped:
        raise MultifacetedProtDBRecordError(
            f"policy must list {MULTIFACETEDPROTDB_SOURCE_ID} in unmapped_sources"
        )
    return policy["default_status"]


def cross_check_txt_companion(
    txt_path: str | Path, records: list[dict[str, str]]
) -> list[str]:
    """Verify the identifier-only TXT companion matches the canonical artifact.

    The TXT is never ingested as records; divergence is reported exactly.
    """
    txt_path = Path(txt_path)
    accessions = [token for token in txt_path.read_text(encoding="utf-8").split(",") if token]
    txt_set = {normalize_uniprot_accession(token) for token in accessions}
    txt_set.discard(None)
    record_set = {record["uniprot_normalized"] for record in records}
    divergences: list[str] = []
    extra_txt = sorted(txt_set - record_set)
    missing_txt = sorted(record_set - txt_set)
    if extra_txt:
        divergences.append(f"accessions in TXT but not in canonical JSON: {extra_txt}")
    if missing_txt:
        divergences.append(f"accessions in canonical JSON but not in TXT: {missing_txt}")
    return divergences


def write_records_csv(
    records: list[dict[str, str]],
    path: str | Path,
    operational_status: str,
) -> None:
    """Write the interim source-record CSV; status_original stays empty (absent)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RECORD_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow({
                **record,
                "status_original": "",
                "operational_status": operational_status,
                "transformation_id": TRANSFORMATION_ID,
                "record_status": "valid",
            })


def build_validation_report(
    records: list[dict[str, str]],
    operational_status: str,
    cross_check_divergences: list[str],
    raw_path: str | Path,
) -> dict[str, Any]:
    return {
        "source_id": MULTIFACETEDPROTDB_SOURCE_ID,
        "record_count": len(records),
        "unique_normalized_accessions": len({r["uniprot_normalized"] for r in records}),
        "status_original": None,
        "operational_status": operational_status,
        "annotation_semantics": "unknown; preserved verbatim, never interpreted",
        "cross_check_divergences": cross_check_divergences,
        "raw_file_path": str(raw_path),
        "raw_file_sha256": records[0]["raw_file_sha256"] if records else None,
        "transformation_id": TRANSFORMATION_ID,
        "catalog_integrated": False,
    }
