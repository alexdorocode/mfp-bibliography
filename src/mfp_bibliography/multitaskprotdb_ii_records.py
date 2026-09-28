"""MultitaskProtDB-II interim source-record adapter (local-only, not catalog-integrated).

Reads ``data/raw/multitaskprotdb-ii/proteins.csv`` (UTF-8-SIG with BOM, CRLF
line terminators, no trailing newline) after verifying its bytes against the
registered manifest SHA-256, and emits one deterministic interim source record
per INPUT row.

Scope boundaries:
- Row grain is "protein annotation entry", not one-protein-per-row: 694 rows
  carry 685 distinct accessions; same-accession rows are distinct observations
  and are never merged or de-duplicated. Accessions are normalized for later
  exact-accession matching only.
- ``source_record_id = multitaskprotdb_ii_row_{1-based data-row position}`` is
  bound to source ID, pinned raw snapshot (SHA-256) and row position. A future
  snapshot with reordered rows requires a NEW transformation version; IDs are
  never silently reused across reordered snapshots.
- No source status field exists: ``status_original`` stays empty and
  ``operational_status`` is only the neutral policy default for unmapped
  sources. No evidence claim is invented.
- GO/GO_Moon text, references, functions and structure/model metadata are
  preserved verbatim as source data. They are NOT verified GO annotations
  and NOT GO–article support; a record-level reference never supports a GO term.
- ``Models``/``PDBs``/``PDB_UniProt``/``Human_Disease``/``Drugs`` are metadata,
  never evidence of multifunctionality. ``Long_Description``/``Induction`` are
  100% empty in this snapshot and are not emitted.
- Reference values that are not article-like identifiers are flagged at FIELD
  level (``reference_anomaly``) with their row retained; never converted to
  PMID/DOI.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path
from typing import Any

from mfp_bibliography.normalization import normalize_uniprot_accession

MULTITASKPROTDB_II_SOURCE_ID = "SRC_MULTITASKPROTDB_II"
TRANSFORMATION_ID = "multitaskprotdb_ii_source_records_v0"
RAW_RELATIVE_PATH = "data/raw/multitaskprotdb-ii/proteins.csv"

EXPECTED_HEADER = [
    "UniProt", "Protein_Name", "Long_Description", "Canonical_Function", "GO",
    "Moonlighting_function", "GO_Moon", "Organism", "Human_Disease", "Drugs",
    "Induction", "PDBs", "PDB_UniProt", "Models", "Reference",
]

RECORD_COLUMNS = [
    "source_id", "source_record_id", "row_index",
    "uniprot_raw", "uniprot_normalized", "protein_name_raw", "organism_raw",
    "canonical_function_raw", "moonlighting_function_raw",
    "go_raw", "go_moon_raw", "reference_raw", "reference_article_like",
    "reference_anomaly", "pdbs_raw", "pdb_uniprot_raw", "models_raw",
    "human_disease_raw", "drugs_raw",
    "status_original", "operational_status",
    "raw_file_path", "raw_file_sha256", "transformation_id", "record_status",
]

_ARTICLE_LIKE = re.compile(r"^[0-9]+(\s*[,;]\s*[0-9]+)*$")


class MultitaskProtDBIIRecordError(ValueError):
    """Raw bytes, schema or record validation failed; nothing is published."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def classify_reference(raw_value: str) -> tuple[str, str]:
    """Classify a Reference value as article-like or anomalous (field-level).

    Returns (article_like, anomaly): ('true'|'false', ''|'missing'|'not_article_identifier').
    Bare numeric PubMed-style identifiers are article-like; anything else
    (e.g. OMIM strings, PDB-like tokens) is flagged, never converted.
    """
    value = (raw_value or "").strip()
    if not value:
        return "false", "missing"
    if _ARTICLE_LIKE.match(value):
        return "true", ""
    return "false", "not_article_identifier"


def load_source_records(
    raw_path: str | Path,
    expected_sha256: str | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Load and validate interim source records.

    Returns (records, reference_anomalies). Fails before any output on hash
    mismatch, unexpected schema, missing/malformed accession, or duplicate
    source_record_id. Nothing is silently discarded.
    """
    raw_path = Path(raw_path)
    data = raw_path.read_bytes()
    actual_sha256 = _sha256_bytes(data)
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise MultitaskProtDBIIRecordError(
            f"raw artifact hash mismatch for {raw_path}: "
            f"manifest {expected_sha256}, actual {actual_sha256}"
        )

    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    header = reader.fieldnames or []
    if header != EXPECTED_HEADER:
        raise MultitaskProtDBIIRecordError(
            f"unexpected schema: expected header {EXPECTED_HEADER}, got {header}"
        )

    records: list[dict[str, str]] = []
    anomalies: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for row_index, row in enumerate(reader, start=1):
        source_record_id = f"multitaskprotdb_ii_row_{row_index}"
        if source_record_id in seen_ids:
            raise MultitaskProtDBIIRecordError(
                f"duplicate source_record_id {source_record_id!r}"
            )
        seen_ids.add(source_record_id)

        uniprot_raw = (row.get("UniProt") or "").strip()
        normalized = normalize_uniprot_accession(uniprot_raw)
        if normalized is None or not re.match(r"^[A-Z][A-Z0-9]{5}([A-Z0-9]{4})?$", normalized):
            raise MultitaskProtDBIIRecordError(
                f"row {row_index}: missing or malformed UniProt accession: {uniprot_raw!r}"
            )

        reference_raw = row.get("Reference") or ""
        article_like, anomaly = classify_reference(reference_raw)

        records.append({
            "source_id": MULTITASKPROTDB_II_SOURCE_ID,
            "source_record_id": source_record_id,
            "row_index": str(row_index),
            "uniprot_raw": uniprot_raw,
            "uniprot_normalized": normalized,
            "protein_name_raw": row.get("Protein_Name") or "",
            "organism_raw": row.get("Organism") or "",
            "canonical_function_raw": row.get("Canonical_Function") or "",
            "moonlighting_function_raw": row.get("Moonlighting_function") or "",
            "go_raw": row.get("GO") or "",
            "go_moon_raw": row.get("GO_Moon") or "",
            "reference_raw": reference_raw,
            "reference_article_like": article_like,
            "reference_anomaly": anomaly,
            "pdbs_raw": row.get("PDBs") or "",
            "pdb_uniprot_raw": row.get("PDB_UniProt") or "",
            "models_raw": row.get("Models") or "",
            "human_disease_raw": row.get("Human_Disease") or "",
            "drugs_raw": row.get("Drugs") or "",
            "status_original": "",
            "raw_file_path": str(raw_path),
            "raw_file_sha256": actual_sha256,
        })

        if anomaly:
            anomalies.append({
                "source_record_id": source_record_id,
                "row_index": str(row_index),
                "reference_raw": reference_raw,
                "anomaly": anomaly,
            })

    if not records:
        raise MultitaskProtDBIIRecordError(f"raw artifact {raw_path} contains no data rows")
    return records, anomalies


def resolve_operational_status(policy: dict[str, Any]) -> str:
    """Neutral operational status: the policy default for unmapped sources."""
    if MULTITASKPROTDB_II_SOURCE_ID not in policy.get("unmapped_sources", []):
        raise MultitaskProtDBIIRecordError(
            f"policy must list {MULTITASKPROTDB_II_SOURCE_ID} in unmapped_sources"
        )
    return policy["default_status"]


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
                "operational_status": operational_status,
                "transformation_id": TRANSFORMATION_ID,
                "record_status": "valid",
            })


def build_validation_report(
    records: list[dict[str, str]],
    reference_anomalies: list[dict[str, str]],
    operational_status: str,
    raw_path: str | Path,
) -> dict[str, Any]:
    return {
        "source_id": MULTITASKPROTDB_II_SOURCE_ID,
        "transformation_id": TRANSFORMATION_ID,
        "record_count": len(records),
        "distinct_normalized_accessions": len({r["uniprot_normalized"] for r in records}),
        "status_original": None,
        "operational_status": operational_status,
        "evidence_claims": 0,
        "reference_anomaly_count": len(reference_anomalies),
        "reference_anomalies": reference_anomalies,
        "raw_file_path": str(raw_path),
        "raw_file_sha256": records[0]["raw_file_sha256"] if records else None,
        "catalog_integrated": False,
    }
