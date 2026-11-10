"""MultitaskProtDB-II Functional Claims and Coverage Adapter.

This module implements the source-grounded claim and coverage extraction adapter
for MultitaskProtDB-II (SRC_MULTITASKPROTDB_II), adhering to contract specifications
defined in spec.md and JSON Schemas in data/curated/.

Key Architectural & Scientific Invariants:
1. Multiplicity Preservation: Extracts distinct claim records for Canonical_Function
   and Moonlighting_function; never collapses into fixed binary facet slots.
2. Source-Native Roles: Preserves verbatim role names ('Canonical_Function', 'Moonlighting_function').
3. Reference Granularity & Exact Preservation: References in MultitaskProtDB-II apply
   at record level; stored verbatim in record_reference_ids without artificial prefixing
   (e.g. no synthetic 'PMID:' injection) and NEVER promoted to linked_reference_ids.
4. Source-Explicit Aspects & Evidence: Parses explicit GO IDs, native aspects (BP, MF, CC),
   and evidence codes (IEA, IDA, etc.) into structured MultitaskGOAnnotation objects.
   Never copies canonical CC terms to Moonlighting claims; preserves CC explicitly present
   in GO_Moon as a source assertion without interpreting source grouping as a validated triplet.
5. Missing Text with GO Data Accounting: If a function description is empty but GO annotations
   are present, accounts for the unextracted annotations in coverage notes without fabricating
   text statements.
6. Deterministic Total Ordering: Emits claims sorted by (protein_id, source_id,
   source_record_id, claim_index, claim_id), and coverage sorted by (protein_id,
   source_id, source_record_id).
7. 100% Denominator Accounting: Emits one functional_coverage record for every input row.
"""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
import re
from typing import Any, NamedTuple

from mfp_bibliography.normalization import (
    make_protein_id_uniprot,
    normalize_uniprot_accession,
)

SOURCE_ID = "SRC_MULTITASKPROTDB_II"
SOURCE_SUFFIX = "MULTITASKPROTDB_II"
CLAIM_ID_SCHEME_VERSION = "MFPB_FUNCTIONAL_CLAIM_V1"
ANNOTATION_ID_SCHEME_VERSION = "MFPB_SOURCE_GO_ANNOTATION_V1"
EXTRACTION_METHOD = "extract_multitask_claims_v0.1"
DEFAULT_RAW_FILE_PATH = "data/raw/multitaskprotdb-ii/proteins.csv"

_GO_ID_REGEX = re.compile(r"GO:\d{7}")
_ARTICLE_LIKE_REGEX = re.compile(r"^[0-9]+(\s*[,;]\s*[0-9]+)*$")
_UNIPROT_ACC_REGEX = re.compile(r"^[A-Z][A-Z0-9]{5}([A-Z0-9]{4})?$")


class MultitaskGOAnnotation(NamedTuple):
    """Structured representation of a source-explicit GO annotation line."""

    go_id: str
    aspect: str  # 'CC', 'MF', 'BP', or 'unassigned'
    term_name: str | None
    evidence: str | None
    raw_text: str = ""


def derive_multitask_claim_id(
    source_record_id: str,
    claim_index: int,
    raw_claim_field: str,
) -> str:
    """Derive deterministic claim ID under scheme MFPB_FUNCTIONAL_CLAIM_V1."""
    payload = f"{SOURCE_ID}::{source_record_id}::{claim_index}::{raw_claim_field}"
    digest = hashlib.sha256(f"{CLAIM_ID_SCHEME_VERSION}::{payload}".encode("utf-8")).hexdigest()[:16]
    return f"MFP:FC:{SOURCE_SUFFIX}:{digest}"


def derive_source_go_annotation_id(
    source_record_id: str,
    source_field: str,
    annotation_index: int,
    go_id: str,
) -> str:
    """Derive deterministic annotation ID under scheme MFPB_SOURCE_GO_ANNOTATION_V1."""
    payload = f"{SOURCE_ID}::{source_record_id}::{source_field}::{annotation_index}::{go_id}"
    digest = hashlib.sha256(f"{ANNOTATION_ID_SCHEME_VERSION}::{payload}".encode("utf-8")).hexdigest()[:16]
    return f"MFP:SGA:{SOURCE_SUFFIX}:{digest}"


def parse_multitask_go_annotations(go_text: str | None) -> list[MultitaskGOAnnotation]:
    """Parse MultitaskProtDB-II GO text into structured annotation objects.

    Preserves the tight association between each GO identifier, aspect,
    term description, evidence string, and raw text line as explicitly provided.
    Preserves multiple occurrences, including repeated GO IDs with distinct evidence.
    """
    if not go_text or not go_text.strip():
        return []

    annotations: list[MultitaskGOAnnotation] = []

    for line in go_text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _GO_ID_REGEX.search(line)
        if not m:
            continue
        go_id = m.group(0)

        # 1. Native aspect
        aspect = "unassigned"
        if re.search(r"(?:^|[;\s\"\'=])C:(?!\s*\d)", line) or "cellular_component" in line:
            aspect = "CC"
        elif re.search(r"(?:^|[;\s\"\'=])F:(?!\s*\d)", line) or "molecular_function" in line:
            aspect = "MF"
        elif re.search(r"(?:^|[;\s\"\'=])P:(?!\s*\d)", line) or "biological_process" in line:
            aspect = "BP"

        # 2. Evidence code (e.g. IEA:..., IDA:..., TAS:...)
        ev_m = re.search(r"\b([A-Z]{3}:[^\s;]+)", line)
        evidence = ev_m.group(1).rstrip(".") if ev_m else None

        # 3. Term name if present in structured semicolon segments
        parts = [p.strip() for p in line.split(";") if p.strip()]
        term_name: str | None = None
        for p in parts:
            if re.match(r"^[CFP]:", p):
                term_name = re.sub(r"^[CFP]:\s*", "", p)
                break
            elif p.startswith("Synonyms:"):
                continue
            elif not _GO_ID_REGEX.search(p) and not (ev_m and ev_m.group(1) in p):
                term_name = p

        annotations.append(MultitaskGOAnnotation(
            go_id=go_id,
            aspect=aspect,
            term_name=term_name,
            evidence=evidence,
            raw_text=line,
        ))

    return annotations


def parse_multitask_go_terms(go_text: str | None) -> tuple[str | None, str | None, str | None]:
    """Parse GO text into parallel semicolon-delimited ID/aspect strings and evidence note.

    Returns:
        (source_go_ids, source_go_aspects, evidence_note)
    """
    annotations = parse_multitask_go_annotations(go_text)
    if not annotations:
        return None, None, None

    # Deduplicate IDs in order of appearance for functional_claims delimited strings
    unique_ids: list[str] = []
    unique_aspects: list[str] = []
    seen: set[str] = set()
    for a in annotations:
        if a.go_id not in seen:
            seen.add(a.go_id)
            unique_ids.append(a.go_id)
            unique_aspects.append(a.aspect)

    go_ids = "; ".join(unique_ids)
    aspects = "; ".join(unique_aspects)

    ev_tokens = [f"{a.go_id}={a.evidence}" for a in annotations if a.evidence]
    evidence_note = f"go_evidence: {'; '.join(ev_tokens)}" if ev_tokens else None

    return go_ids, aspects, evidence_note


def format_multitask_reference(raw_reference: str | None) -> tuple[str | None, str | None]:
    """Preserve raw reference exactly at extracted-field level.

    Returns:
        (record_reference_ids, note)
    """
    if not raw_reference or not raw_reference.strip():
        return None, None

    clean_ref = raw_reference.strip()

    # Original Reference values survive exactly without artificial prefixing
    note = None
    if not _ARTICLE_LIKE_REGEX.match(clean_ref):
        note = f"anomalous_reference: {clean_ref}"

    return clean_ref, note


def extract_claims_from_multitask_row(
    row: dict[str, str],
    row_index: int,
    protein_id: str | None = None,
    raw_file_path: str = DEFAULT_RAW_FILE_PATH,
    return_annotations: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]] | tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Extract functional claims, coverage, and optionally source GO annotations from a row.

    Args:
        row: Dict containing raw MultitaskProtDB-II columns.
        row_index: 1-based data row index.
        protein_id: Resolved catalog entity ID. If None, derived from normalized UniProt accession.
        raw_file_path: Path of the source artifact for provenance tracking.
        return_annotations: If True, returns (claims, annotations, coverage). If False, returns (claims, coverage).

    Returns:
        (claims, coverage) if return_annotations is False;
        (claims, annotations, coverage) if return_annotations is True.
    """
    source_record_id = f"multitaskprotdb_ii_row_{row_index}"
    raw_row_locator = f"row:{row_index + 1}"

    # Resolve protein_id if not supplied
    if protein_id is None:
        raw_acc = (row.get("UniProt") or "").strip()
        norm_acc = normalize_uniprot_accession(raw_acc)
        if norm_acc and _UNIPROT_ACC_REGEX.match(norm_acc):
            protein_id = make_protein_id_uniprot(norm_acc)

    # Reference formatting - preserves exact original reference string
    raw_ref = row.get("Reference")
    rec_refs, ref_note = format_multitask_reference(raw_ref)

    claims: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []
    unextracted_notes: list[str] = []

    # If identity is unresolved, cannot emit valid claims or annotations tied to catalog
    if protein_id is None:
        coverage = {
            "source_record_id": source_record_id,
            "protein_id": None,
            "source_id": SOURCE_ID,
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": "Unresolved UniProt accession; no claims emitted",
        }
        if return_annotations:
            return [], [], coverage
        return [], coverage

    # 1. Canonical Function & GO annotations
    canonical_val = (row.get("Canonical_Function") or "").strip()
    raw_go = row.get("GO")
    parsed_canonical_annotations = parse_multitask_go_annotations(raw_go)
    go_ids, go_aspects, go_ev_note = parse_multitask_go_terms(raw_go)

    canonical_claim_id: str | None = None
    if canonical_val:
        claim_idx = len(claims)
        canonical_claim_id = derive_multitask_claim_id(source_record_id, claim_idx, "Canonical_Function")

        claim_notes: list[str] = []
        if ref_note:
            claim_notes.append(ref_note)
        if go_ev_note:
            claim_notes.append(go_ev_note)

        claims.append({
            "claim_id": canonical_claim_id,
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
            "notes": "; ".join(claim_notes) if claim_notes else None,
        })
    elif go_ids:
        # Check 3: Function description is empty but GO annotations are present.
        # Account for information in coverage without fabricating a text claim.
        unextracted_notes.append(f"unextracted_annotations_without_text: Canonical_Function has no text statement but contains GO annotations ({go_ids})")

    # Structured source GO annotations for Canonical (GO)
    for idx, ann in enumerate(parsed_canonical_annotations):
        ann_id = derive_source_go_annotation_id(source_record_id, "GO", idx, ann.go_id)
        annotations.append({
            "annotation_id": ann_id,
            "protein_id": protein_id,
            "source_id": SOURCE_ID,
            "source_record_id": source_record_id,
            "claim_id": canonical_claim_id,
            "source_field": "GO",
            "annotation_index": idx,
            "raw_annotation_text": ann.raw_text,
            "go_id": ann.go_id,
            "go_aspect": ann.aspect if ann.aspect in ("BP", "MF", "CC", "unassigned") else None,
            "term_name": ann.term_name,
            "evidence_raw": ann.evidence,
            "annotation_status": "parsed" if ann.aspect in ("BP", "MF", "CC") else "unassigned_aspect",
            "notes": None,
        })

    # 2. Moonlighting Function & GO_Moon annotations
    moon_val = (row.get("Moonlighting_function") or "").strip()
    raw_go_moon = row.get("GO_Moon")
    parsed_moon_annotations = parse_multitask_go_annotations(raw_go_moon)
    go_moon_ids, go_moon_aspects, go_moon_ev_note = parse_multitask_go_terms(raw_go_moon)

    moon_claim_id: str | None = None
    if moon_val:
        claim_idx = len(claims)
        moon_claim_id = derive_multitask_claim_id(source_record_id, claim_idx, "Moonlighting_function")

        claim_notes = []
        if ref_note:
            claim_notes.append(ref_note)
        if go_moon_ev_note:
            claim_notes.append(go_moon_ev_note)

        claims.append({
            "claim_id": moon_claim_id,
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
            "notes": "; ".join(claim_notes) if claim_notes else None,
        })
    elif go_moon_ids:
        unextracted_notes.append(f"unextracted_annotations_without_text: Moonlighting_function has no text statement but contains GO annotations ({go_moon_ids})")

    # Structured source GO annotations for Moonlighting (GO_Moon)
    for idx, ann in enumerate(parsed_moon_annotations):
        ann_id = derive_source_go_annotation_id(source_record_id, "GO_Moon", idx, ann.go_id)
        annotations.append({
            "annotation_id": ann_id,
            "protein_id": protein_id,
            "source_id": SOURCE_ID,
            "source_record_id": source_record_id,
            "claim_id": moon_claim_id,
            "source_field": "GO_Moon",
            "annotation_index": idx,
            "raw_annotation_text": ann.raw_text,
            "go_id": ann.go_id,
            "go_aspect": ann.aspect if ann.aspect in ("BP", "MF", "CC", "unassigned") else None,
            "term_name": ann.term_name,
            "evidence_raw": ann.evidence,
            "annotation_status": "parsed" if ann.aspect in ("BP", "MF", "CC") else "unassigned_aspect",
            "notes": None,
        })

    # Denominator Coverage record
    coverage_status = "claims_extracted" if claims else "no_discrete_functional_statements"
    all_cov_notes: list[str] = []
    if ref_note:
        all_cov_notes.append(ref_note)
    if unextracted_notes:
        all_cov_notes.extend(unextracted_notes)

    coverage = {
        "source_record_id": source_record_id,
        "protein_id": protein_id,
        "source_id": SOURCE_ID,
        "claims_extracted_count": len(claims),
        "coverage_status": coverage_status,
        "metadata_annotation_raw": None,
        "notes": "; ".join(all_cov_notes) if all_cov_notes else None,
    }

    if return_annotations:
        return claims, annotations, coverage
    return claims, coverage


def extract_multitask_row_records(
    row: dict[str, str],
    row_index: int,
    protein_id: str | None = None,
    raw_file_path: str = DEFAULT_RAW_FILE_PATH,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Extract claims, structured source GO annotations, and coverage from a single row.

    Returns:
        tuple (claims, annotations, coverage)
    """
    res = extract_claims_from_multitask_row(
        row=row,
        row_index=row_index,
        protein_id=protein_id,
        raw_file_path=raw_file_path,
        return_annotations=True,
    )
    return res  # type: ignore[return-value]


def extract_multitask_claims_from_file(
    raw_path: str | Path,
    catalog_lookup: dict[str, str] | None = None,
    return_annotations: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract claims and coverage (and optionally source GO annotations) from MultitaskProtDB-II CSV file.

    Args:
        raw_path: Path to the MultitaskProtDB-II CSV file.
        catalog_lookup: Optional dict mapping source_record_id -> protein_id.
        return_annotations: If True, returns (sorted_claims, sorted_annotations, sorted_coverage).
                            If False (default), returns (sorted_claims, sorted_coverage).

    Returns:
        (sorted_claims, sorted_coverage) if return_annotations is False;
        (sorted_claims, sorted_annotations, sorted_coverage) if return_annotations is True.
    """
    raw_path = Path(raw_path)
    data = raw_path.read_bytes()
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    all_claims: list[dict[str, Any]] = []
    all_annotations: list[dict[str, Any]] = []
    all_coverage: list[dict[str, Any]] = []
    seen_claim_ids: set[str] = set()
    seen_annotation_ids: set[str] = set()

    for row_index, row in enumerate(reader, start=1):
        srid = f"multitaskprotdb_ii_row_{row_index}"
        protein_id = catalog_lookup.get(srid) if catalog_lookup else None

        res = extract_claims_from_multitask_row(
            row=row,
            row_index=row_index,
            protein_id=protein_id,
            raw_file_path=str(raw_path),
            return_annotations=True,
        )
        claims, annotations, cov = res  # type: ignore[misc]

        for claim in claims:
            cid = claim["claim_id"]
            if cid in seen_claim_ids:
                raise ValueError(f"Deterministic claim_id collision detected: {cid}")
            seen_claim_ids.add(cid)
            all_claims.append(claim)

        for ann in annotations:
            aid = ann["annotation_id"]
            if aid in seen_annotation_ids:
                raise ValueError(f"Deterministic annotation_id collision detected: {aid}")
            seen_annotation_ids.add(aid)
            all_annotations.append(ann)

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

    # Annotations: (protein_id ASC, source_id ASC, source_record_id ASC, source_field ASC, annotation_index ASC, annotation_id ASC)
    sorted_annotations = sorted(
        all_annotations,
        key=lambda a: (
            a["protein_id"],
            a["source_id"],
            a["source_record_id"],
            a["source_field"],
            a["annotation_index"],
            a["annotation_id"],
        ),
    )

    # Coverage: (protein_id or "" ASC, source_id ASC, source_record_id ASC)
    sorted_coverage = sorted(
        all_coverage,
        key=lambda cov: (
            cov["protein_id"] or "",
            cov["source_id"],
            cov["source_record_id"],
        ),
    )

    if return_annotations:
        return sorted_claims, sorted_annotations, sorted_coverage
    return sorted_claims, sorted_coverage


def extract_multitask_slice_from_file(
    raw_path: str | Path,
    catalog_lookup: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract claims, structured source GO annotations, and coverage from MultitaskProtDB-II file.

    Returns:
        tuple (sorted_claims, sorted_annotations, sorted_coverage)
    """
    res = extract_multitask_claims_from_file(
        raw_path=raw_path,
        catalog_lookup=catalog_lookup,
        return_annotations=True,
    )
    return res  # type: ignore[return-value]
