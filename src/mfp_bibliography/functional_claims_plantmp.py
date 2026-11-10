"""PlantMP Functional Claims and Coverage Adapter.

This module implements the source-grounded claim, source GO annotation, and
coverage extraction adapter for PlantMP (SRC_PLANTMP), adhering to contract
specifications defined in spec.md and JSON Schemas in data/curated/.

Key Architectural & Scientific Invariants:
1. Multiplicity Preservation: Extracts distinct claim records for non-empty
   canonical and moonlighting fields across BP and MF aspects; never collapses
   into fixed binary facet slots.
2. Source-Native Roles & Pre-Split Aspects: Preserves verbatim role names
   ('canonical', 'moonlighting') and field-level provenance ('canonical_function_bp',
   'canonical_function_mf', 'moonlighting_function_bp', 'moonlighting_function_mf').
3. No Independent Function Assumption: Pre-partitioned BP and MF statements are
   grouped under their native role labels ('canonical' or 'moonlighting') but
   are NOT assumed to represent independent biological functions.
4. Reference Granularity & Exact Preservation: References in PlantMP (pubmed_id)
   apply at record level; stored verbatim in record_reference_ids without
   artificial prefixing (no synthetic 'PMID:' injection) and NEVER promoted
   to linked_reference_ids without direct claim linkage evidence.
5. Curation Tier Policy & Status Handling:
   - 'confirmed' -> claim_assertion_type = 'curated'
   - 'predicted' -> claim_assertion_type = 'predicted'
   - 'likely'    -> claim_assertion_type = 'unresolved' (candidate/likely moonlighting;
     never silently promoted to curated; policy status excluded_likely noted)
   - Disputed/unknown -> claim_assertion_type = 'unresolved'
   Original raw status values are strictly preserved in notes.
6. Source-Explicit GO Annotations: Parses explicit GO IDs and native aspects
   (BP, MF) into structured PlantMPGOAnnotation objects under scheme
   MFPB_SOURCE_GO_ANNOTATION_V1. PlantMP provides no cellular component (CC)
   terms and no evidence codes; evidence_raw and term_name remain null.
   Never infers CC terms or synthesizes contextual triplets.
7. Missing Text with GO Data Accounting: If a function description is empty
   but GO annotations are present, emits structured source_go_annotations with
   claim_id = None and accounts for the unextracted annotations in coverage notes
   without fabricating fake text statements.
8. Deterministic Total Ordering: Emits claims sorted by (protein_id, source_id,
   source_record_id, claim_index, claim_id), annotations sorted by (protein_id,
   source_id, source_record_id, source_field, annotation_index, annotation_id),
   and coverage sorted by (protein_id, source_id, source_record_id).
9. 100% Denominator Accounting: Emits one functional_coverage record for every
   input row.
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

SOURCE_ID = "SRC_PLANTMP"
SOURCE_SUFFIX = "PLANTMP"
CLAIM_ID_SCHEME_VERSION = "MFPB_FUNCTIONAL_CLAIM_V1"
ANNOTATION_ID_SCHEME_VERSION = "MFPB_SOURCE_GO_ANNOTATION_V1"
EXTRACTION_METHOD = "extract_plantmp_claims_v0.1"
DEFAULT_RAW_FILE_PATH = "data/raw/plantmp/PlantMP_all.csv"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp" / "mfp_source_records.csv"

_UNIPROT_ACC_REGEX = re.compile(r"^[A-Z][A-Z0-9]{5}([A-Z0-9]{4})?$")
_ARTICLE_LIKE_REGEX = re.compile(r"^[0-9]+(\s*[,;]\s*[0-9]+)*$")
_DIGITS_REGEX = re.compile(r"(\d+)")


def load_plantmp_catalog_lookup(
    catalog_path: str | Path = DEFAULT_CATALOG_PATH,
) -> dict[str, str]:
    """Load mapping of source_record_id -> protein_id for PlantMP from catalog."""
    path = Path(catalog_path)
    if not path.exists():
        return {}
    lookup: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("source_name") == SOURCE_ID:
                srid = row.get("source_record_id")
                pid = row.get("protein_id")
                if srid and pid:
                    lookup[srid] = pid
    return lookup

# Field pair definition: (role, text_field, go_field, default_aspect)
PLANTMP_FIELD_PAIRS: tuple[tuple[str, str, str, str], ...] = (
    ("canonical", "canonical_function_bp", "go_canonical_bp", "BP"),
    ("canonical", "canonical_function_mf", "go_canonical_mf", "MF"),
    ("moonlighting", "moonlighting_function_bp", "go_moonlighting_bp", "BP"),
    ("moonlighting", "moonlighting_function_mf", "go_moonlighting_mf", "MF"),
)


class PlantMPGOAnnotation(NamedTuple):
    """Structured representation of a source-explicit PlantMP GO annotation."""

    go_id: str
    aspect: str  # 'BP' or 'MF'
    term_name: str | None = None
    evidence: str | None = None
    raw_text: str = ""


def derive_plantmp_claim_id(
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


def parse_plantmp_go_field(
    raw_text: str | None,
    default_aspect: str,
) -> list[PlantMPGOAnnotation]:
    """Parse comma-separated PlantMP GO field into structured annotation objects.

    PlantMP encodes GO terms as comma-separated lists prefixed by aspect
    (e.g. 'BP 0042254, 0006412' or 'MF 0003729, 0019843'). This parser
    extracts each explicit term, preserves the raw token string, and formats
    the 7-digit identifier into canonical 'GO:0000000'.
    """
    if not raw_text or not raw_text.strip():
        return []

    annotations: list[PlantMPGOAnnotation] = []
    tokens = [tok.strip() for tok in raw_text.split(",") if tok.strip()]

    for tok in tokens:
        aspect = default_aspect
        if tok.startswith("BP"):
            aspect = "BP"
        elif tok.startswith("MF"):
            aspect = "MF"

        m = _DIGITS_REGEX.search(tok)
        if not m:
            continue
        digits = m.group(1)
        go_id = f"GO:{digits.zfill(7)}"

        annotations.append(
            PlantMPGOAnnotation(
                go_id=go_id,
                aspect=aspect,
                term_name=None,
                evidence=None,
                raw_text=tok,
            )
        )

    return annotations


def format_plantmp_go_terms(
    annotations: list[PlantMPGOAnnotation],
) -> tuple[str | None, str | None]:
    """Format structured annotations into deduplicated parallel delimited strings.

    Returns:
        (source_go_ids, source_go_aspects)
    """
    if not annotations:
        return None, None

    unique_ids: list[str] = []
    unique_aspects: list[str] = []
    seen: set[str] = set()

    for a in annotations:
        if a.go_id not in seen:
            seen.add(a.go_id)
            unique_ids.append(a.go_id)
            unique_aspects.append(a.aspect)

    go_ids = "; ".join(unique_ids) if unique_ids else None
    aspects = "; ".join(unique_aspects) if unique_aspects else None
    return go_ids, aspects


def format_plantmp_reference(raw_reference: str | None) -> tuple[str | None, str | None]:
    """Preserve raw reference exactly at extracted-field level.

    Returns:
        (record_reference_ids, note)
    """
    if not raw_reference or not raw_reference.strip():
        return None, None

    clean_ref = raw_reference.strip()
    note = None
    if not _ARTICLE_LIKE_REGEX.match(clean_ref):
        note = f"anomalous_reference: {clean_ref}"

    return clean_ref, note


def resolve_plantmp_assertion_type(raw_type: str | None) -> tuple[str, str | None]:
    """Resolve normalized claim_assertion_type and status note from PlantMP raw type.

    In accordance with R-NORM-04 and configs/source_claim_policy_v0.1.yaml:
    - 'confirmed' maps to 'curated' (supported by source manual curation).
    - 'predicted' maps to 'predicted' (computational predictions).
    - 'likely' is candidate/likely; under scientific rules it MUST NOT be
      silently mapped to 'curated'. It maps to 'unresolved' under the
      schema enum while preserving its native status in notes.
    - Missing or unrecognized values map to 'unresolved'.

    Returns:
        (claim_assertion_type, status_note)
    """
    clean_type = (raw_type or "").strip().lower()
    if clean_type == "confirmed":
        return "curated", "source_type: confirmed"
    elif clean_type == "predicted":
        return "predicted", "source_type: predicted"
    elif clean_type == "likely":
        return "unresolved", "source_type: likely; policy_status: excluded_likely"
    else:
        label = clean_type if clean_type else "unknown"
        return "unresolved", f"source_type: {label}; policy_status: unresolved"


def group_claims_by_role(claims: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group extracted claim records by their native functional role.

    A helper verifying that BP and MF statements are grouped by functional role
    ('canonical' or 'moonlighting') without assuming that partitioned fields
    represent independent biological functions.
    """
    grouped: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        role = claim.get("claim_role_raw") or "unassigned"
        grouped.setdefault(role, []).append(claim)
    return grouped


def extract_claims_from_plantmp_row(
    row: dict[str, str],
    row_index: int,
    protein_id: str | None = None,
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
    raw_file_path: str = DEFAULT_RAW_FILE_PATH,
    return_annotations: bool = False,
) -> (
    tuple[list[dict[str, Any]], dict[str, Any]]
    | tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]
):
    """Extract functional claims, coverage, and optionally source GO annotations from a row.

    Args:
        row: Dict containing raw PlantMP columns.
        row_index: 1-based data row index.
        protein_id: Explicit catalog entity ID override.
        catalog_lookup: Optional dict mapping source_record_id -> protein_id.
        allow_unanchored: If True, permits syntax-only accession derivation when
                          catalog_lookup and protein_id are omitted. Default is False.
        raw_file_path: Path of the source artifact for provenance tracking.
        return_annotations: If True, returns (claims, annotations, coverage). If False, returns (claims, coverage).

    Returns:
        (claims, coverage) if return_annotations is False;
        (claims, annotations, coverage) if return_annotations is True.
    """
    order = (row.get("order") or "").strip()
    source_record_id = f"plantmp_order_{order}" if order else f"plantmp_order_{row_index}"
    raw_row_locator = f"order:{order}" if order else f"row:{row_index + 1}"

    raw_acc = (row.get("uniport_id") or "").strip()
    norm_acc = normalize_uniprot_accession(raw_acc)
    has_valid_acc = bool(norm_acc and _UNIPROT_ACC_REGEX.match(norm_acc))
    derived_pid = make_protein_id_uniprot(norm_acc) if has_valid_acc else None

    resolved_protein_id: str | None = None
    unresolved_reason: str | None = None

    if not has_valid_acc:
        unresolved_reason = f"Missing or malformed UniProt accession ({raw_acc!r}); identity unresolved"
    elif catalog_lookup is not None:
        # A catalog is supplied: verify presence and linkage agreement
        if source_record_id not in catalog_lookup:
            unresolved_reason = (
                f"Source record {source_record_id} absent from supplied catalog; "
                f"accession {norm_acc or raw_acc!r} not promoted to resolved entity"
            )
        else:
            catalog_pid = catalog_lookup[source_record_id]
            if catalog_pid != derived_pid:
                unresolved_reason = (
                    f"Mismatched source-record linkage: catalog protein_id {catalog_pid} "
                    f"does not agree with row accession {norm_acc} ({derived_pid}); identity unresolved"
                )
            else:
                resolved_protein_id = catalog_pid
    elif protein_id is not None:
        # An explicit protein_id was supplied
        if protein_id != derived_pid:
            unresolved_reason = (
                f"Mismatched protein linkage: supplied protein_id {protein_id} "
                f"does not agree with row accession {norm_acc} ({derived_pid}); identity unresolved"
            )
        else:
            resolved_protein_id = protein_id
    else:
        # Neither catalog_lookup nor protein_id was supplied.
        if not allow_unanchored:
            unresolved_reason = (
                f"No catalog lookup or protein_id supplied; accession {norm_acc or raw_acc!r} "
                f"not promoted to resolved entity without catalog referential backing"
            )
        else:
            resolved_protein_id = derived_pid

    # Reference formatting - preserves exact original reference string
    raw_ref = row.get("pubmed_id")
    rec_refs, ref_note = format_plantmp_reference(raw_ref)

    # Status resolution
    raw_type = row.get("type")
    assertion_type, status_note = resolve_plantmp_assertion_type(raw_type)

    claims: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []
    unextracted_notes: list[str] = []

    # If identity is unresolved, cannot emit valid claims tied to catalog
    if resolved_protein_id is None:
        cov_notes: list[str] = []
        if unresolved_reason:
            cov_notes.append(unresolved_reason)
        else:
            cov_notes.append("Unresolved UniProt accession; no claims emitted")
        if status_note:
            cov_notes.append(status_note)
        coverage = {
            "source_record_id": source_record_id,
            "protein_id": None,  # Scientifically honest representation: no entity exists in mfp_proteins
            "source_id": SOURCE_ID,
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": "; ".join(cov_notes),
        }
        if return_annotations:
            return [], [], coverage
        return [], coverage

    # Extract claims and annotations across the 4 pre-split field pairs
    for role, text_field, go_field, default_aspect in PLANTMP_FIELD_PAIRS:
        raw_val = (row.get(text_field) or "").strip()
        raw_go = row.get(go_field)
        parsed_annotations = parse_plantmp_go_field(raw_go, default_aspect=default_aspect)
        go_ids, go_aspects = format_plantmp_go_terms(parsed_annotations)

        linked_claim_id: str | None = None

        if raw_val:
            claim_idx = len(claims)
            linked_claim_id = derive_plantmp_claim_id(
                source_record_id, claim_idx, text_field
            )

            claim_notes: list[str] = []
            if status_note:
                claim_notes.append(status_note)
            if ref_note:
                claim_notes.append(ref_note)

            claims.append(
                {
                    "claim_id": linked_claim_id,
                    "protein_id": resolved_protein_id,
                    "source_id": SOURCE_ID,
                    "source_record_id": source_record_id,
                    "claim_index": claim_idx,
                    "claim_role_raw": role,
                    "raw_claim_field": text_field,
                    "raw_claim_value": raw_val,
                    "claim_assertion_type": assertion_type,
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
                }
            )
        elif go_ids:
            # Function description is empty but GO annotations are present.
            # Account for information in coverage notes without fabricating a fake text claim.
            unextracted_notes.append(
                f"unextracted_annotations_without_text: {text_field} has no text statement but contains GO annotations ({go_ids})"
            )

        # Structured source GO annotations
        for idx, ann in enumerate(parsed_annotations):
            ann_id = derive_source_go_annotation_id(
                source_record_id, go_field, idx, ann.go_id
            )
            annotations.append(
                {
                    "annotation_id": ann_id,
                    "protein_id": resolved_protein_id,
                    "source_id": SOURCE_ID,
                    "source_record_id": source_record_id,
                    "claim_id": linked_claim_id,
                    "source_field": go_field,
                    "annotation_index": idx,
                    "raw_annotation_text": ann.raw_text,
                    "go_id": ann.go_id,
                    "go_aspect": ann.aspect,
                    "term_name": None,
                    "evidence_raw": None,
                    "annotation_status": "parsed",
                    "notes": None,
                }
            )

    # Denominator Coverage record
    coverage_status = (
        "claims_extracted" if claims else "no_discrete_functional_statements"
    )
    all_cov_notes: list[str] = []
    if status_note:
        all_cov_notes.append(status_note)
    if ref_note:
        all_cov_notes.append(ref_note)
    if unextracted_notes:
        all_cov_notes.extend(unextracted_notes)

    coverage = {
        "source_record_id": source_record_id,
        "protein_id": resolved_protein_id,
        "source_id": SOURCE_ID,
        "claims_extracted_count": len(claims),
        "coverage_status": coverage_status,
        "metadata_annotation_raw": None,
        "notes": "; ".join(all_cov_notes) if all_cov_notes else None,
    }

    if return_annotations:
        return claims, annotations, coverage
    return claims, coverage


def extract_plantmp_row_records(
    row: dict[str, str],
    row_index: int,
    protein_id: str | None = None,
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
    raw_file_path: str = DEFAULT_RAW_FILE_PATH,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Extract claims, structured source GO annotations, and coverage from a single row.

    Returns:
        tuple (claims, annotations, coverage)
    """
    res = extract_claims_from_plantmp_row(
        row=row,
        row_index=row_index,
        protein_id=protein_id,
        catalog_lookup=catalog_lookup,
        allow_unanchored=allow_unanchored,
        raw_file_path=raw_file_path,
        return_annotations=True,
    )
    return res  # type: ignore[return-value]


def extract_plantmp_claims_from_file(
    raw_path: str | Path,
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
    return_annotations: bool = False,
) -> (
    tuple[list[dict[str, Any]], list[dict[str, Any]]]
    | tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]
):
    """Extract claims and coverage (and optionally source GO annotations) from PlantMP CSV file.

    Args:
        raw_path: Path to the PlantMP CSV file.
        catalog_lookup: Optional dict mapping source_record_id -> protein_id.
                        If None and allow_unanchored is False, automatically loads
                        the authoritative MVP catalog via load_plantmp_catalog_lookup().
        allow_unanchored: If True, permits syntax-only derivation without catalog anchoring.
                          Default is False (strictly catalog-anchored).
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

    if catalog_lookup is None and not allow_unanchored:
        catalog_lookup = load_plantmp_catalog_lookup()

    all_claims: list[dict[str, Any]] = []
    all_annotations: list[dict[str, Any]] = []
    all_coverage: list[dict[str, Any]] = []
    seen_claim_ids: set[str] = set()
    seen_annotation_ids: set[str] = set()

    for row_index, row in enumerate(reader, start=1):
        res = extract_claims_from_plantmp_row(
            row=row,
            row_index=row_index,
            catalog_lookup=catalog_lookup,
            allow_unanchored=allow_unanchored,
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

    # Coverage: (protein_id ASC, source_id ASC, source_record_id ASC)
    # Note: protein_id may be None for unresolved identity records; sort None first deterministically.
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


def extract_plantmp_slice_from_file(
    raw_path: str | Path,
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract claims, structured source GO annotations, and coverage from PlantMP file.

    Returns:
        tuple (sorted_claims, sorted_annotations, sorted_coverage)
    """
    res = extract_plantmp_claims_from_file(
        raw_path=raw_path,
        catalog_lookup=catalog_lookup,
        allow_unanchored=allow_unanchored,
        return_annotations=True,
    )
    return res  # type: ignore[return-value]
