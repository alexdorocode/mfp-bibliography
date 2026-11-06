"""MultitaskProtDB-II Functional Claims and Coverage Adapter.

This module implements the source-grounded claim and coverage extraction adapter
for MultitaskProtDB-II (SRC_MULTITASKPROTDB_II), adhering to contract specifications
defined in spec.md and JSON Schemas in data/curated/.

Key Architectural & Scientific Invariants:
1. Multiplicity Preservation: Extracts distinct claim records for Canonical_Function
   and Moonlighting_function; never collapses into fixed binary facet slots.
2. Source-Native Roles: Preserves verbatim role names ('Canonical_Function', 'Moonlighting_function').
3. Reference Granularity: References in MultitaskProtDB-II apply at record level;
   stored in record_reference_ids and NEVER promoted to linked_reference_ids.
4. No Inferred Relationships: Source-explicit GO IDs and aspects (BP, MF, CC) are
   extracted verbatim from source lines; no ontology lookups, QuickGO reconciliation,
   or function-compartment inferences are made.
5. Deterministic Total Ordering: Emits claims sorted by (protein_id, source_id,
   source_record_id, claim_index, claim_id), and coverage sorted by (protein_id,
   source_id, source_record_id).
6. 100% Denominator Accounting: Emits one functional_coverage record for every input row.
"""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
import re
from typing import Any

from mfp_bibliography.normalization import (
    make_protein_id_uniprot,
    normalize_uniprot_accession,
)

SOURCE_ID = "SRC_MULTITASKPROTDB_II"
SOURCE_SUFFIX = "MULTITASKPROTDB_II"
CLAIM_ID_SCHEME_VERSION = "MFPB_FUNCTIONAL_CLAIM_V1"
EXTRACTION_METHOD = "extract_multitask_claims_v0.1"
DEFAULT_RAW_FILE_PATH = "data/raw/multitaskprotdb-ii/proteins.csv"

_GO_ID_REGEX = re.compile(r"GO:\d{7}")
_ARTICLE_LIKE_REGEX = re.compile(r"^[0-9]+(\s*[,;]\s*[0-9]+)*$")
_UNIPROT_ACC_REGEX = re.compile(r"^[A-Z][A-Z0-9]{5}([A-Z0-9]{4})?$")


def derive_multitask_claim_id(
    source_record_id: str,
    claim_index: int,
    raw_claim_field: str,
) -> str:
    """Derive deterministic claim ID under scheme MFPB_FUNCTIONAL_CLAIM_V1."""
    payload = f"{SOURCE_ID}::{source_record_id}::{claim_index}::{raw_claim_field}"
    digest = hashlib.sha256(f"{CLAIM_ID_SCHEME_VERSION}::{payload}".encode("utf-8")).hexdigest()[:16]
    return f"MFP:FC:{SOURCE_SUFFIX}:{digest}"


def parse_multitask_go_terms(go_text: str | None) -> tuple[str | None, str | None]:
    """Parse source-explicit GO IDs and native aspects from MultitaskProtDB-II GO text.

    Returns:
        (source_go_ids, source_go_aspects) as semicolon-space delimited strings or (None, None).
    """
    if not go_text or not go_text.strip():
        return None, None

    go_ids: list[str] = []
    aspects: list[str] = []
    seen: set[str] = set()

    for line in go_text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _GO_ID_REGEX.search(line)
        if not m:
            continue
        go_id = m.group(0)
        if go_id in seen:
            continue
        seen.add(go_id)

        # Extract explicit native aspect if stated by the source line
        aspect = "unassigned"
        if re.search(r"(?:^|[;\s\"\'=])C:(?!\s*\d)", line) or "cellular_component" in line:
            aspect = "CC"
        elif re.search(r"(?:^|[;\s\"\'=])F:(?!\s*\d)", line) or "molecular_function" in line:
            aspect = "MF"
        elif re.search(r"(?:^|[;\s\"\'=])P:(?!\s*\d)", line) or "biological_process" in line:
            aspect = "BP"

        go_ids.append(go_id)
        aspects.append(aspect)

    if not go_ids:
        return None, None

    # If all aspects are unassigned, aspect string is unassigned for all to preserve 1:1 alignment
    return "; ".join(go_ids), "; ".join(aspects)


def format_multitask_reference(raw_reference: str | None) -> tuple[str | None, str | None]:
    """Format row-level reference as record_reference_ids and optional anomaly note.

    Returns:
        (record_reference_ids, note)
    """
    if not raw_reference or not raw_reference.strip():
        return None, None

    clean_ref = raw_reference.strip()
    if _ARTICLE_LIKE_REGEX.match(clean_ref):
        # Extract numeric tokens and prefix with PMID:
        tokens = re.split(r"[,;]\s*", clean_ref)
        pmid_tokens = [f"PMID:{t.strip()}" for t in tokens if t.strip()]
        return "; ".join(pmid_tokens), None

    # Non-numeric reference (e.g. OMIM text, PDB code): preserve verbatim
    return clean_ref, f"anomalous_reference: {clean_ref}"


def extract_claims_from_multitask_row(
    row: dict[str, str],
    row_index: int,
    protein_id: str | None = None,
    raw_file_path: str = DEFAULT_RAW_FILE_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Extract functional claims and coverage record from a single MultitaskProtDB-II row.

    Args:
        row: Dict containing raw MultitaskProtDB-II columns.
        row_index: 1-based data row index.
        protein_id: Resolved catalog entity ID. If None, derived from normalized UniProt accession.
        raw_file_path: Path of the source artifact for provenance tracking.

    Returns:
        tuple (claims_list, coverage_dict)
    """
    source_record_id = f"multitaskprotdb_ii_row_{row_index}"
    raw_row_locator = f"row:{row_index + 1}"

    # Resolve protein_id if not supplied
    if protein_id is None:
        raw_acc = (row.get("UniProt") or "").strip()
        norm_acc = normalize_uniprot_accession(raw_acc)
        if norm_acc and _UNIPROT_ACC_REGEX.match(norm_acc):
            protein_id = make_protein_id_uniprot(norm_acc)

    # Reference formatting
    raw_ref = row.get("Reference")
    rec_refs, ref_note = format_multitask_reference(raw_ref)

    claims: list[dict[str, Any]] = []

    # If identity is unresolved, cannot emit valid claims tied to catalog
    if protein_id is None:
        coverage = {
            "source_record_id": source_record_id,
            "protein_id": "MFP:U:0000000000000000",  # Placeholder required by schema pattern if unassigned
            "source_id": SOURCE_ID,
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": "Unresolved UniProt accession; no claims emitted",
        }
        return [], coverage

    # 1. Canonical Function
    canonical_val = (row.get("Canonical_Function") or "").strip()
    if canonical_val:
        claim_idx = len(claims)
        go_ids, go_aspects = parse_multitask_go_terms(row.get("GO"))
        claim_id = derive_multitask_claim_id(source_record_id, claim_idx, "Canonical_Function")
        claims.append({
            "claim_id": claim_id,
            "protein_id": protein_id,
            "source_id": SOURCE_ID,
            "source_record_id": source_record_id,
            "claim_index": claim_idx,
            "claim_role_raw": "Canonical_Function",
            "raw_claim_field": "Canonical_Function",
            "raw_claim_value": canonical_val,
            "claim_assertion_type": "curated",
            "source_go_ids": go_ids,
            "source_go_aspects": go_aspects,
            "source_ec_number": None,
            "linked_reference_ids": None,
            "record_reference_ids": rec_refs,
            "raw_file_path": raw_file_path,
            "raw_row_or_url": raw_row_locator,
            "extraction_method": EXTRACTION_METHOD,
            "claim_status": "valid",
            "notes": ref_note,
        })

    # 2. Moonlighting Function
    moon_val = (row.get("Moonlighting_function") or "").strip()
    if moon_val:
        claim_idx = len(claims)
        go_moon_ids, go_moon_aspects = parse_multitask_go_terms(row.get("GO_Moon"))
        claim_id = derive_multitask_claim_id(source_record_id, claim_idx, "Moonlighting_function")
        claims.append({
            "claim_id": claim_id,
            "protein_id": protein_id,
            "source_id": SOURCE_ID,
            "source_record_id": source_record_id,
            "claim_index": claim_idx,
            "claim_role_raw": "Moonlighting_function",
            "raw_claim_field": "Moonlighting_function",
            "raw_claim_value": moon_val,
            "claim_assertion_type": "curated",
            "source_go_ids": go_moon_ids,
            "source_go_aspects": go_moon_aspects,
            "source_ec_number": None,
            "linked_reference_ids": None,
            "record_reference_ids": rec_refs,
            "raw_file_path": raw_file_path,
            "raw_row_or_url": raw_row_locator,
            "extraction_method": EXTRACTION_METHOD,
            "claim_status": "valid",
            "notes": ref_note,
        })

    # Denominator Coverage record
    coverage_status = "claims_extracted" if claims else "no_discrete_functional_statements"
    coverage_notes = ref_note

    coverage = {
        "source_record_id": source_record_id,
        "protein_id": protein_id,
        "source_id": SOURCE_ID,
        "claims_extracted_count": len(claims),
        "coverage_status": coverage_status,
        "metadata_annotation_raw": None,
        "notes": coverage_notes,
    }

    return claims, coverage


def extract_multitask_claims_from_file(
    raw_path: str | Path,
    catalog_lookup: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract claims and coverage from a MultitaskProtDB-II CSV file.

    Args:
        raw_path: Path to the MultitaskProtDB-II CSV file.
        catalog_lookup: Optional dict mapping source_record_id -> protein_id.

    Returns:
        tuple (sorted_claims, sorted_coverage) conforming to total ordering rules.
    """
    raw_path = Path(raw_path)
    data = raw_path.read_bytes()
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    all_claims: list[dict[str, Any]] = []
    all_coverage: list[dict[str, Any]] = []
    seen_claim_ids: set[str] = set()

    for row_index, row in enumerate(reader, start=1):
        srid = f"multitaskprotdb_ii_row_{row_index}"
        protein_id = catalog_lookup.get(srid) if catalog_lookup else None

        claims, cov = extract_claims_from_multitask_row(
            row=row,
            row_index=row_index,
            protein_id=protein_id,
            raw_file_path=str(raw_path),
        )

        for claim in claims:
            cid = claim["claim_id"]
            if cid in seen_claim_ids:
                raise ValueError(f"Deterministic claim_id collision detected: {cid}")
            seen_claim_ids.add(cid)
            all_claims.append(claim)

        all_coverage.append(cov)

    # Apply total tie-breaking sort order
    # Claims: (protein_id ASC, source_id ASC, source_record_id ASC, claim_index ASC, claim_id ASC)
    sorted_claims = sorted(
        all_claims,
        key=lambda c: (
            c["protein_id"],
            c["source_id"],
            c["source_record_id"],
            c["claim_index"],
            c["claim_id"],
        ),
    )

    # Coverage: (protein_id ASC, source_id ASC, source_record_id ASC)
    sorted_coverage = sorted(
        all_coverage,
        key=lambda cov: (
            cov["protein_id"],
            cov["source_id"],
            cov["source_record_id"],
        ),
    )

    return sorted_claims, sorted_coverage
