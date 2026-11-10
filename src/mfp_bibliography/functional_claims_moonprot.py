"""MoonProt functional claims, coverage, and source GO annotations adapter.

Implements the Tier A source-preservation adapter for MoonProt
under scheme MFPB_FUNCTIONAL_CLAIM_V1, MFPB_SOURCE_GO_ANNOTATION_V1,
and functional_coverage.schema.json.

Key Preservation Invariants & Constraints:
1. Reuses Existing HTML Parser: Reuses MoonProtRecord and parser capabilities from
   mfp_bibliography.moonprot_parser without creating a redundant HTML parser.
2. Dynamic Function Blocks: Preserves one discrete claim per explicit function block
   in functions (functions[0], functions[1], ...); strictly avoids fixed two-function
   assumptions.
3. Reference Granularity: Function-specific PMIDs from "References for function" are
   preserved in linked_reference_ids with "PMID:" formatting (semicolon-space delimited);
   record_reference_ids remains None (MoonProt citations are function-specific).
4. No Triplet or Compartment Inference: Function cellular location text is preserved in
   claim notes without inferring cellular component (CC) terms or constructing triplets.
5. Protein-Level GO Terms Preservation: "GO terms" are protein-level in MoonProt; they
   are NOT distributed across individual function claims. Instead, they are emitted
   in source_go_annotations with claim_id = None, preserving them structurally.
6. Identity Resolution & Fallback Support: Authoritative catalog linkage via
   mfp_source_records.csv and mfp_proteins.csv. Supports both canonical UniProt-derived
   IDs (MFP:U:...) and valid catalog fallback IDs (MFP:F:SRC_MOONPROT:...).
7. Unresolved Identity: When an accession is missing, malformed, or absent from the
   catalog, emits protein_id = None and coverage_status = "unresolved_identity"
   without inventing fake sentinel entities (e.g. no MFP:U:0000000000000000).
8. Deterministic Ordering: Enforces total tie-breaking sort keys:
   - Claims: (protein_id ASC, source_id ASC, source_record_id ASC, claim_index ASC, claim_id ASC)
   - Annotations: (protein_id ASC, source_id ASC, source_record_id ASC, source_field ASC, annotation_index ASC, annotation_id ASC)
   - Coverage: (protein_id or "" ASC, source_id ASC, source_record_id ASC)
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import re
from typing import Any

from mfp_bibliography.moonprot_parser import (
    MoonProtFunctionDetail,
    MoonProtKnownAbsentError,
    MoonProtParseError,
    MoonProtRecord,
    parse_moonprot_fixture,
    parse_moonprot_html,
)
from mfp_bibliography.normalization import (
    make_protein_id_uniprot,
    normalize_uniprot_accession,
)

SOURCE_ID = "SRC_MOONPROT"
SOURCE_SUFFIX = "MOONPROT"
EXTRACTION_METHOD = "extract_moonprot_claims_v0.1"

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp" / "mfp_source_records.csv"
DEFAULT_PROTEINS_PATH = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp" / "mfp_proteins.csv"

_UNIPROT_ACC_REGEX = re.compile(r"^[A-Z][A-Z0-9]{5}([A-Z0-9]{4})?$")
_GO_ID_REGEX = re.compile(r"\b(GO:\d{7})\b")
_EC_PATTERN = re.compile(r"^\d+\.(?:\d+|-)\.(?:\d+|-)\.(?:\d+|-)$")


def derive_moonprot_claim_id(
    source_record_id: str, claim_index: int, raw_claim_field: str
) -> str:
    """Derive deterministic unique claim_id under scheme MFPB_FUNCTIONAL_CLAIM_V1.

    Payload format: {SOURCE_ID}::{source_record_id}::{claim_index}::{raw_claim_field}
    Returns: MFP:FC:MOONPROT:{16-char hex digest}
    """
    payload = f"{SOURCE_ID}::{source_record_id}::{claim_index}::{raw_claim_field}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"MFP:FC:{SOURCE_SUFFIX}:{digest}"


def derive_source_go_annotation_id(
    source_record_id: str,
    source_field: str,
    annotation_index: int,
    go_id: str,
) -> str:
    """Derive deterministic unique annotation_id under scheme MFPB_SOURCE_GO_ANNOTATION_V1.

    Payload format: {SOURCE_ID}::{source_record_id}::{source_field}::{annotation_index}::{go_id}
    Returns: MFP:SGA:MOONPROT:{16-char hex digest}
    """
    payload = f"{SOURCE_ID}::{source_record_id}::{source_field}::{annotation_index}::{go_id}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"MFP:SGA:{SOURCE_SUFFIX}:{digest}"


def load_moonprot_catalog_lookup(
    source_records_path: Path | str | None = None,
    proteins_path: Path | str | None = None,
) -> dict[str, str]:
    """Load authoritative source_record_id -> protein_id lookup for MoonProt from catalog.

    Verifies against mfp_source_records.csv and mfp_proteins.csv.
    Supports both canonical UniProt entities (MFP:U:...) and valid fallback entities (MFP:F:...).
    """
    s_path = Path(source_records_path) if source_records_path else DEFAULT_CATALOG_PATH
    p_path = Path(proteins_path) if proteins_path else DEFAULT_PROTEINS_PATH

    valid_proteins: set[str] = set()
    if p_path.exists():
        with p_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                pid = (row.get("protein_id") or "").strip()
                if pid:
                    valid_proteins.add(pid)

    lookup: dict[str, str] = {}
    if s_path.exists():
        with s_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row.get("source_name") == SOURCE_ID:
                    srid = (row.get("source_record_id") or "").strip()
                    pid = (row.get("protein_id") or "").strip()
                    if srid and pid:
                        if valid_proteins and pid not in valid_proteins:
                            raise ValueError(
                                f"Catalog integrity violation: source record {srid} references unknown protein {pid}"
                            )
                        lookup[srid] = pid

    return lookup


def parse_moonprot_go_annotations(raw_go_terms: str | None) -> list[dict[str, Any]]:
    """Parse protein-level GO terms text from MoonProt into structured annotation items.

    MoonProt GO terms are provided at the record level, formatted either as comma-separated
    or newline-separated fragments such as:
    'GO:0003824 catalytic activity, GO:0004459 L-lactate dehydrogenase (NAD+) activity'
    or multiline lines.
    Aspect is not declared in the text, so go_aspect is None.
    """
    if not raw_go_terms or not raw_go_terms.strip():
        return []

    text = raw_go_terms.strip()
    annotations: list[dict[str, Any]] = []

    # Find all occurrences of GO:0000000
    matches = list(_GO_ID_REGEX.finditer(text))
    for i, match in enumerate(matches):
        go_id = match.group(1)
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        fragment = text[start_pos:end_pos].strip()

        # Remove trailing commas or newlines
        fragment = fragment.rstrip(",").strip()

        # Extract term name after GO ID
        remainder = fragment[len(go_id):].strip()
        term_name: str | None = remainder if remainder else None

        annotations.append({
            "go_id": go_id,
            "raw_fragment": fragment,
            "term_name": term_name,
        })

    return annotations


def format_moonprot_references(pmids: tuple[str, ...]) -> str | None:
    """Format function-level PMIDs into standard semicolon-space delimited string.

    Prepends standard 'PMID:' prefix if bare numbers are present.
    """
    if not pmids:
        return None
    formatted = [f"PMID:{p.strip()}" if not p.strip().startswith("PMID:") else p.strip() for p in pmids if p.strip()]
    return "; ".join(formatted) if formatted else None


def extract_claims_from_moonprot_record(
    record: MoonProtRecord,
    source_record_id: str | None = None,
    protein_id: str | None = None,
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
    raw_file_path: str = "data/raw/moonprot/unknown.html",
    raw_row_or_url: str | None = None,
    return_annotations: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, Any]]:
    """Extract functional claims, coverage, and structured source GO annotations from a MoonProtRecord.

    Args:
        record: Parsed MoonProtRecord from moonprot_parser.
        source_record_id: Canonical source record identifier (e.g. 'moonprot_1').
        protein_id: Explicit catalog protein ID if already resolved.
        catalog_lookup: Dict mapping source_record_id -> protein_id.
        allow_unanchored: If True, allows deriving unanchored entity IDs for isolated tests.
        raw_file_path: Repository path to the raw HTML fixture.
        raw_row_or_url: URL or locator within raw data.
        return_annotations: Whether to include source_go_annotations in return tuple.

    Returns:
        (claims, annotations, coverage) if return_annotations is True;
        (claims, coverage) if return_annotations is False.
    """
    srid = source_record_id or f"moonprot_{record.moonprot_id}"
    url_locator = raw_row_or_url or f"http://www.moonlightingproteins.org/protein_detail/?mpid={record.moonprot_id}"

    # Extract and normalize accession
    raw_acc = record.uniprot_id or ""
    norm_acc = normalize_uniprot_accession(raw_acc)
    has_valid_acc = bool(norm_acc and _UNIPROT_ACC_REGEX.match(norm_acc))

    # Resolve protein_id and check catalog referential integrity
    resolved_protein_id: str | None = None
    coverage_status: str = "unresolved_identity"
    unresolved_reason: str | None = None

    if protein_id is not None:
        resolved_protein_id = protein_id
    elif catalog_lookup is not None:
        if srid in catalog_lookup:
            catalog_pid = catalog_lookup[srid]
            if has_valid_acc:
                derived_pid = make_protein_id_uniprot(norm_acc)  # type: ignore[arg-type]
                if catalog_pid.startswith("MFP:U:") and catalog_pid != derived_pid:
                    unresolved_reason = f"Catalog protein_id mismatch: catalog={catalog_pid}, derived={derived_pid}"
                    resolved_protein_id = None
                else:
                    resolved_protein_id = catalog_pid
            elif catalog_pid.startswith("MFP:F:"):
                # Valid catalog fallback identity
                resolved_protein_id = catalog_pid
            else:
                unresolved_reason = f"Source record {srid} has missing/invalid accession and catalog ID is not fallback"
                resolved_protein_id = None
        else:
            unresolved_reason = f"Record {srid} (accession {norm_acc or raw_acc!r}) absent from catalog lookup"
            resolved_protein_id = None
    elif allow_unanchored:
        if has_valid_acc:
            resolved_protein_id = make_protein_id_uniprot(norm_acc)  # type: ignore[arg-type]
        else:
            unresolved_reason = f"Missing or malformed UniProt accession: {raw_acc!r}"
            resolved_protein_id = None
    else:
        unresolved_reason = "Unanchored accession: no catalog lookup supplied and allow_unanchored=False"
        resolved_protein_id = None

    # Handle unresolvable identity
    if resolved_protein_id is None:
        coverage = {
            "source_record_id": srid,
            "protein_id": None,
            "source_id": SOURCE_ID,
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": unresolved_reason or "Unresolved MoonProt identity",
        }
        if return_annotations:
            return [], [], coverage
        return [], coverage

    claims: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []

    # 1. Extract claims from dynamic function blocks (functions[0], functions[1], ...)
    for fn in record.functions:
        desc = (fn.description or "").strip()
        if not desc:
            continue

        claim_idx = len(claims)
        raw_field = f"functions[{fn.function_index - 1}].description"
        claim_id = derive_moonprot_claim_id(srid, claim_idx, raw_field)
        claim_role_raw = f"Function {fn.function_index}"

        # Clean EC number
        raw_ec = (fn.ec_number or "").strip()
        ec_val: str | None = None
        ec_notes: str | None = None
        if raw_ec and raw_ec.lower() not in ("n/a", "na", "none"):
            if _EC_PATTERN.match(raw_ec):
                ec_val = raw_ec
            else:
                ec_notes = f"source_ec_raw: {raw_ec}"

        # References tied directly to this function
        linked_refs = format_moonprot_references(fn.pmids)

        # Function notes
        claim_notes_list: list[str] = []
        loc = (fn.cellular_location or "").strip()
        if loc and loc.lower() not in ("none", "n/a", "na"):
            claim_notes_list.append(f"cellular_location: {loc}")
        if fn.references_raw and not fn.pmids:
            claim_notes_list.append(f"ref_raw: {fn.references_raw.strip()}")
        if ec_notes:
            claim_notes_list.append(ec_notes)

        claim_notes = "; ".join(claim_notes_list) if claim_notes_list else None

        claims.append({
            "claim_id": claim_id,
            "protein_id": resolved_protein_id,
            "source_id": SOURCE_ID,
            "source_record_id": srid,
            "claim_index": claim_idx,
            "claim_role_raw": claim_role_raw,
            "raw_claim_field": raw_field,
            "raw_claim_value": desc,
            "claim_assertion_type": "curated",
            "source_go_ids": None,  # Protein-level GO terms not distributed to function claims
            "source_go_aspects": None,
            "source_ec_number": ec_val,
            "linked_reference_ids": linked_refs,
            "record_reference_ids": None,
            "raw_file_path": raw_file_path,
            "raw_row_or_url": url_locator,
            "extraction_method": EXTRACTION_METHOD,
            "claim_status": "valid",
            "notes": claim_notes,
        })

    # 2. Extract structured source GO annotations from protein-level GO terms
    parsed_go = parse_moonprot_go_annotations(record.raw_go_terms)
    for ann_idx, ann_item in enumerate(parsed_go):
        ann_id = derive_source_go_annotation_id(srid, "GO terms", ann_idx, ann_item["go_id"])
        annotations.append({
            "annotation_id": ann_id,
            "protein_id": resolved_protein_id,
            "source_id": SOURCE_ID,
            "source_record_id": srid,
            "claim_id": None,  # Explicitly unlinked to discrete function claims
            "source_field": "GO terms",
            "annotation_index": ann_idx,
            "raw_annotation_text": ann_item["raw_fragment"],
            "go_id": ann_item["go_id"],
            "go_aspect": None,  # Not declared in MoonProt text
            "term_name": ann_item["term_name"],
            "evidence_raw": None,
            "annotation_status": "parsed",
            "notes": "Protein-level MoonProt GO term unlinked to discrete function claims",
        })

    # 3. Denominator coverage accounting
    claims_count = len(claims)
    if claims_count > 0:
        coverage_status = "claims_extracted"
        cov_notes: str | None = None
        if annotations:
            cov_notes = f"{claims_count} claims extracted; {len(annotations)} protein-level GO annotations preserved with claim_id=null"
    else:
        coverage_status = "no_discrete_functional_statements"
        cov_notes = f"No discrete functional statements; {len(annotations)} protein-level GO annotations preserved with claim_id=null" if annotations else "No discrete functional statements"

    coverage = {
        "source_record_id": srid,
        "protein_id": resolved_protein_id,
        "source_id": SOURCE_ID,
        "claims_extracted_count": claims_count,
        "coverage_status": coverage_status,
        "metadata_annotation_raw": None,
        "notes": cov_notes,
    }

    if return_annotations:
        return claims, annotations, coverage
    return claims, coverage


def extract_moonprot_claims_from_file(
    file_path: str | Path,
    source_record_id: str | None = None,
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
    return_annotations: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, Any]]:
    """Extract claims and coverage from a single MoonProt HTML fixture or raw file."""
    path = Path(file_path)
    # Default catalog lookup if omitted and not explicitly unanchored
    if catalog_lookup is None and not allow_unanchored:
        catalog_lookup = load_moonprot_catalog_lookup()

    # Determine expected MPID from filename if standard pattern mpid_{id}.html
    m = re.search(r"mpid_(\d+)", path.name)
    expected_mpid = m.group(1) if m else None
    srid = source_record_id or (f"moonprot_{expected_mpid}" if expected_mpid else path.stem)

    try:
        record = parse_moonprot_fixture(path, expected_mpid=expected_mpid)
    except MoonProtKnownAbsentError as e:
        coverage = {
            "source_record_id": srid,
            "protein_id": None,
            "source_id": SOURCE_ID,
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": f"Known absent: {e}",
        }
        if return_annotations:
            return [], [], coverage
        return [], coverage
    except MoonProtParseError as e:
        coverage = {
            "source_record_id": srid,
            "protein_id": None,
            "source_id": SOURCE_ID,
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": f"Parse error: {e}",
        }
        if return_annotations:
            return [], [], coverage
        return [], coverage

    return extract_claims_from_moonprot_record(
        record=record,
        source_record_id=srid,
        catalog_lookup=catalog_lookup,
        allow_unanchored=allow_unanchored,
        raw_file_path=str(path),
        raw_row_or_url=f"http://www.moonlightingproteins.org/protein_detail/?mpid={record.moonprot_id}",
        return_annotations=return_annotations,
    )


def extract_moonprot_slice_from_files(
    file_paths: list[str | Path],
    catalog_lookup: dict[str, str] | None = None,
    allow_unanchored: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract claims, structured annotations, and coverage from a list of MoonProt HTML files.

    Applies deterministic total ordering:
    - Claims: (protein_id ASC, source_id ASC, source_record_id ASC, claim_index ASC, claim_id ASC)
    - Annotations: (protein_id ASC, source_id ASC, source_record_id ASC, source_field ASC, annotation_index ASC, annotation_id ASC)
    - Coverage: (protein_id or "" ASC, source_id ASC, source_record_id ASC)
    """
    if catalog_lookup is None and not allow_unanchored:
        catalog_lookup = load_moonprot_catalog_lookup()

    all_claims: list[dict[str, Any]] = []
    all_annotations: list[dict[str, Any]] = []
    all_coverage: list[dict[str, Any]] = []

    seen_claim_ids: set[str] = set()
    seen_annotation_ids: set[str] = set()

    for p in file_paths:
        res = extract_moonprot_claims_from_file(
            file_path=p,
            catalog_lookup=catalog_lookup,
            allow_unanchored=allow_unanchored,
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

    # Total tie-breaking sort order
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

    sorted_coverage = sorted(
        all_coverage,
        key=lambda cov: (
            cov["protein_id"] or "",
            cov["source_id"],
            cov["source_record_id"],
        ),
    )

    return sorted_claims, sorted_annotations, sorted_coverage
