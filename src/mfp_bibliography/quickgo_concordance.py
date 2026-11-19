"""Stage P3 Offline Concordance Engine & Validator.

Governs normalization, comparative metrics, Policy C filtering, namespace-aware citation
comparison, and cross-record contract validation between source-native assertions and
external QuickGO captures from local database snapshot MFP_QuickV1.

100% offline, zero network access, deterministic bitwise reproducibility.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema

# Canonical GO root terms
ROOT_TERMS: Set[str] = {
    "GO:0008150",  # biological_process
    "GO:0003674",  # molecular_function
    "GO:0005575",  # cellular_component
}

# 12 Verified (Accession, Source) Pairs in Pilot Cohort
VERIFIED_COHORT_PAIRS: List[Tuple[str, str]] = [
    ("Q42525", "SRC_MOONPROT"),
    ("Q42525", "SRC_MULTITASKPROTDB_II"),
    ("Q42525", "SRC_PLANTMP"),
    ("Q9Y3E5", "SRC_MULTITASKPROTDB_II"),
    ("P0AFW0", "SRC_MOONPROT"),
    ("P0AFW0", "SRC_MULTITASKPROTDB_II"),
    ("P34788", "SRC_MULTITASKPROTDB_II"),
    ("P34788", "SRC_PLANTMP"),
    ("P78007", "SRC_MOONPROT"),
    ("P24228", "SRC_MOONPROT"),
    ("E6KMA1", "SRC_MOONPROT"),
    ("A0A0H3CDS3", "SRC_MULTITASKPROTDB_II"),
]

GO_ASPECTS: List[str] = ["BP", "MF", "CC"]
POLICIES: List[str] = ["captured_inventory_overlap", "filtered_descriptive_overlap"]

CONCORDANCE_COLUMNS: List[str] = [
    "concordance_id",
    "accession",
    "protein_id",
    "source_id",
    "aspect",
    "policy_id",
    "source_inventory_status",
    "quickgo_inventory_status",
    "source_terms_count",
    "quickgo_terms_count",
    "exact_overlap_count",
    "union_terms_count",
    "source_only_count",
    "quickgo_only_count",
    "jaccard_similarity",
    "concordance_status",
    "primary_non_evaluable_reason",
    "secondary_non_evaluable_reasons",
    "identity_review_status",
    "nd_matching_rows_count",
    "root_matching_rows_count",
    "nd_root_overlap_rows_count",
    "net_excluded_rows_count",
    "terms_lost_after_filtering_count",
    "terms_retained_via_other_rows_count",
    "unassessed_evidence_rows_count",
]

TRANSITION_COLUMNS: List[str] = [
    "transition_id",
    "accession",
    "protein_id",
    "source_id",
    "aspect",
    "policy_id",
    "baseline_concordance_status",
    "recomparison_concordance_status",
    "evaluability_transition",
    "baseline_primary_reason",
    "recomparison_primary_reason",
    "primary_reason_transition",
    "baseline_source_terms_count",
    "recomparison_source_terms_count",
    "delta_source_terms_count",
    "baseline_quickgo_terms_count",
    "recomparison_quickgo_terms_count",
    "delta_quickgo_terms_count",
    "baseline_exact_overlap_count",
    "recomparison_exact_overlap_count",
    "delta_exact_overlap_count",
    "baseline_union_terms_count",
    "recomparison_union_terms_count",
    "delta_union_terms_count",
    "source_set_content_changed",
    "baseline_jaccard_similarity",
    "recomparison_jaccard_similarity",
    "delta_jaccard_similarity",
    "metric_transition",
    "overall_transition_classification",
    "notes",
]


class JoinIntegrityError(ValueError):
    """Raised when source annotations and derived aspect metadata violate join integrity."""
    pass


class ConcordanceValidationError(ValueError):
    """Raised when concordance or transition matrix fails contract or invariant validation."""
    pass


def validate_and_join_source_annotations(
    source_annotations: List[Dict[str, Any]],
    derived_aspects: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Join source annotations to derived aspects with strict 1:1 bijection enforcement.

    Contract:
      - Both datasets must have equal non-zero length.
      - Every row in both datasets must have a valid non-empty annotation_id.
      - annotation_id must be unique within each dataset (no duplicates).
      - Every annotation_id in source must be present in derived, and vice versa.
      - Invariant source fields must be identical across both datasets:
          * protein_id == protein_id
          * source_id == source_id
          * source_record_id == source_record_id
          * go_id == source_go_id
          * parse_csv_value(go_aspect) == parse_csv_value(source_declared_aspect)
      - Heuristic or fallback keys are strictly prohibited.
      - Preservation of multiplicity: every source row is preserved 1:1.
    """
    if len(source_annotations) != len(derived_aspects):
        raise JoinIntegrityError(
            f"Row count mismatch: source has {len(source_annotations)} rows, "
            f"derived aspects has {len(derived_aspects)} rows"
        )

    # Validate source IDs
    source_by_id: Dict[str, Dict[str, Any]] = {}
    for idx, s_row in enumerate(source_annotations):
        ann_id = s_row.get("annotation_id")
        if not ann_id or not str(ann_id).strip():
            raise JoinIntegrityError(f"Source row {idx} is missing or has empty 'annotation_id'")
        ann_id_str = str(ann_id).strip()
        if ann_id_str in source_by_id:
            raise JoinIntegrityError(f"Duplicate annotation_id in source annotations: '{ann_id_str}'")
        source_by_id[ann_id_str] = s_row

    # Validate derived IDs and bijection
    derived_by_id: Dict[str, Dict[str, Any]] = {}
    for idx, d_row in enumerate(derived_aspects):
        ann_id = d_row.get("annotation_id")
        if not ann_id or not str(ann_id).strip():
            raise JoinIntegrityError(f"Derived aspects row {idx} is missing or has empty 'annotation_id'")
        ann_id_str = str(ann_id).strip()
        if ann_id_str in derived_by_id:
            raise JoinIntegrityError(f"Duplicate annotation_id in derived aspects: '{ann_id_str}'")
        if ann_id_str not in source_by_id:
            raise JoinIntegrityError(
                f"Unexpected annotation_id in derived aspects not present in source: '{ann_id_str}'"
            )
        derived_by_id[ann_id_str] = d_row

    if len(derived_by_id) != len(source_by_id):
        missing = set(source_by_id.keys()) - set(derived_by_id.keys())
        raise JoinIntegrityError(
            f"Missing {len(missing)} annotation_id(s) in derived aspects (e.g. {sorted(missing)[:3]})"
        )

    # Verify invariants and construct joined rows
    joined_rows: List[Dict[str, Any]] = []
    for s_row in source_annotations:
        ann_id_str = str(s_row["annotation_id"]).strip()
        d_row = derived_by_id[ann_id_str]

        # Field invariance checks
        s_pid = str(s_row.get("protein_id", "")).strip()
        d_pid = str(d_row.get("protein_id", "")).strip()
        if s_pid != d_pid:
            raise JoinIntegrityError(
                f"Contradictory protein_id for annotation_id '{ann_id_str}': "
                f"source='{s_pid}' vs derived='{d_pid}'"
            )

        s_sid = str(s_row.get("source_id", "")).strip()
        d_sid = str(d_row.get("source_id", "")).strip()
        if s_sid != d_sid:
            raise JoinIntegrityError(
                f"Contradictory source_id for annotation_id '{ann_id_str}': "
                f"source='{s_sid}' vs derived='{d_sid}'"
            )

        s_srid = str(s_row.get("source_record_id", "")).strip()
        d_srid = str(d_row.get("source_record_id", "")).strip()
        if s_srid != d_srid:
            raise JoinIntegrityError(
                f"Contradictory source_record_id for annotation_id '{ann_id_str}': "
                f"source='{s_srid}' vs derived='{d_srid}'"
            )

        s_goid = str(s_row.get("go_id", "")).strip()
        d_goid = str(d_row.get("source_go_id", "")).strip()
        if s_goid != d_goid:
            raise JoinIntegrityError(
                f"Contradictory go_id vs source_go_id for annotation_id '{ann_id_str}': "
                f"source='{s_goid}' vs derived='{d_goid}'"
            )

        s_asp = parse_csv_value(s_row.get("go_aspect"))
        d_asp = parse_csv_value(d_row.get("source_declared_aspect"))
        if s_asp != d_asp:
            raise JoinIntegrityError(
                f"Contradictory source declared aspect for annotation_id '{ann_id_str}': "
                f"source go_aspect='{s_asp}' vs derived source_declared_aspect='{d_asp}'"
            )

        merged = dict(s_row)
        merged["resolved_go_id"] = d_row.get("resolved_go_id")
        merged["derived_aspect"] = d_row.get("derived_aspect")
        merged["mapping_status"] = d_row.get("mapping_status")
        merged["source_declared_aspect"] = d_asp
        merged["replaced_by_go_id"] = d_row.get("replaced_by_go_id")
        merged["consider_go_ids"] = d_row.get("consider_go_ids")
        merged["term_name_resolved"] = d_row.get("term_name_resolved")
        merged["ontology_version"] = d_row.get("ontology_version")
        merged["ontology_sha256"] = d_row.get("ontology_sha256")
        joined_rows.append(merged)

    return joined_rows

RAW_CATEGORY_MAP: Dict[str, str] = {
    "P": "BP",
    "biological_process": "BP",
    "BP": "BP",
    "F": "MF",
    "molecular_function": "MF",
    "MF": "MF",
    "C": "CC",
    "cellular_component": "CC",
    "CC": "CC",
}


def parse_csv_value(val: Any) -> Any:
    """Convert CSV empty string to None; strip leading/trailing whitespace."""
    if val is None:
        return None
    s = str(val).strip()
    return None if s == "" else s


def interpret_reference_token(token: str) -> Tuple[Optional[str], Optional[str]]:
    """Interpret a raw reference token into a canonical CURIE.

    Returns:
        (canonical_curie, unresolved_token)
        If interpretable: (canonical_curie, None)
        If uninterpretable / malformed: (None, token)
    """
    if not token or not token.strip():
        return None, None
    s = token.strip()
    if s.isdigit():
        return f"PMID:{s}", None
    if s.startswith("PMID:"):
        if s[5:].strip().isdigit():
            return f"PMID:{s[5:].strip()}", None
        return None, s
    if s.startswith("GO_REF:") and re.match(r"^GO_REF:[0-9]{7}$", s):
        return s, None
    if s.startswith("DOI:") or s.startswith("doi:"):
        return s, None
    return None, s


def normalize_reference_curie(ref_str: str) -> Optional[str]:
    """Normalize raw citation string to canonical CURIE or return None if uninterpretable."""
    curie, _ = interpret_reference_token(ref_str)
    return curie


def load_candidate_proteins(mfp_proteins_path: Path) -> Dict[str, str]:
    """Map canonical_uniprot_accession -> protein_id from mfp_proteins.csv."""
    mapping = {}
    with open(mfp_proteins_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = row.get("canonical_uniprot_accession")
            pid = row.get("protein_id")
            if acc and pid:
                mapping[acc.strip()] = pid.strip()
    return mapping


def build_normalized_annotations(
    raw_annotations: List[Dict[str, Any]],
    catalog_map: Dict[str, str],
    capture_id: str = "MFP_QuickV1_20261112",
) -> List[Dict[str, Any]]:
    """Build normalized QuickGO annotations from raw export."""
    records = []
    for raw in raw_annotations:
        db_ann_id = int(raw["database_annotation_id"])
        acc = raw["accession"].strip()
        protein_id = catalog_map.get(acc)
        if not protein_id:
            raise ValueError(f"Accession {acc} not found in catalog mapping")

        raw_cat = raw["raw_category"].strip()
        aspect = RAW_CATEGORY_MAP.get(raw_cat)
        if not aspect:
            raise ValueError(f"Unrecognized raw category: {raw_cat}")

        pub_id = parse_csv_value(raw.get("publication_id"))
        if pub_id:
            if pub_id.isdigit():
                ref_type = "pmid"
            elif pub_id.startswith("GO_REF:"):
                ref_type = "go_ref"
            else:
                ref_type = None
        else:
            ref_type = None

        rec = {
            "annotation_id": f"MFP:QGA:{capture_id}:{db_ann_id}",
            "protein_id": protein_id,
            "uniprot_accession": acc,
            "database_protein_id": raw["database_protein_id"].strip(),
            "database_annotation_id": db_ann_id,
            "capture_id": capture_id,
            "go_id": raw["go_id"].strip(),
            "go_aspect": aspect,
            "evidence_code": raw["evidence_code"].strip(),
            "reference_type": ref_type,
            "reference_id": pub_id,
            "qualifier_status": "not_captured",
            "assigned_by": None,
            "source_database": "MFP_QuickV1",
        }
        records.append(rec)

    # Sort deterministically
    records.sort(key=lambda r: (r["uniprot_accession"], r["database_annotation_id"]))
    return records


def build_normalized_coverage(
    raw_coverage: List[Dict[str, Any]],
    catalog_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Build normalized coverage records from raw coverage."""
    records = []
    for raw in raw_coverage:
        acc = raw["accession"].strip()
        protein_id = catalog_map.get(acc)
        if not protein_id:
            raise ValueError(f"Accession {acc} not found in catalog mapping")

        rec = {
            "accession": acc,
            "protein_id": protein_id,
            "database_protein_id": parse_csv_value(raw.get("database_protein_id")),
            "quickgo_coverage_status": raw["quickgo_coverage_status"].strip(),
            "identity_review_status": raw["identity_review_status"].strip(),
            "stored_annotation_rows": int(raw["stored_annotation_rows"]),
            "distinct_go_terms": int(raw["distinct_go_terms"]),
            "notes": parse_csv_value(raw.get("notes")),
        }
        records.append(rec)

    records.sort(key=lambda r: r["accession"])
    return records


def build_concordance_matrix(
    normalized_annotations: List[Dict[str, Any]],
    raw_coverage: List[Dict[str, Any]],
    source_go_annotations: List[Dict[str, Any]],
    functional_coverage: List[Dict[str, Any]],
    catalog_map: Dict[str, str],
    pairs: Optional[List[Tuple[str, str]]] = None,
    derived_aspects_rows: Optional[List[Dict[str, Any]]] = None,
    source_term_sets_out: Optional[Dict[str, Set[str]]] = None,
) -> List[Dict[str, Any]]:
    """Build the Gene Ontology concordance comparison matrix.

    In legacy mode (derived_aspects_rows is None), reproduces historical Stage P3 matrix.
    In enriched mode (derived_aspects_rows is not None), joins source annotations with
    derived aspects, applies obsolete-term rules (Cases A-D) and aspect conflict quarantine,
    preserving exact verbatim GO ID set matching and schema compatibility.
    """
    cov_by_acc = {r["accession"]: r for r in raw_coverage}
    slice_pids = {r["protein_id"] for r in functional_coverage}

    target_pairs = pairs if pairs is not None else VERIFIED_COHORT_PAIRS
    rows: List[Dict[str, Any]] = []

    # If enrichment metadata is supplied, validate and join
    if derived_aspects_rows is not None:
        effective_source_annotations = validate_and_join_source_annotations(
            source_go_annotations, derived_aspects_rows
        )
    else:
        effective_source_annotations = source_go_annotations

    for acc, source_id in target_pairs:
        if acc not in catalog_map or acc not in cov_by_acc:
            continue
        protein_id = catalog_map[acc]
        cov_info = cov_by_acc[acc]
        qgo_cov_status = cov_info["quickgo_coverage_status"]
        identity_review_status = cov_info["identity_review_status"]

        # 1. QuickGO Aspect Inventory
        q_ann_acc = [r for r in normalized_annotations if r["uniprot_accession"] == acc]

        # 2. Source Aspect Inventory
        in_slice = protein_id in slice_pids
        s_ann_pair = [
            r for r in effective_source_annotations
            if r["protein_id"] == protein_id and r["source_id"] == source_id
        ]

        if derived_aspects_rows is None:
            # Legacy Mode aspect resolution
            has_any_source_terms = len(s_ann_pair) > 0
            all_source_aspects_undeclared = (
                has_any_source_terms
                and all(not parse_csv_value(r.get("go_aspect")) for r in s_ann_pair)
            )
            conflict_aspects: Set[str] = set()
        else:
            # Enriched Mode aspect resolution
            conflict_aspects = set()
            for r in s_ann_pair:
                if r.get("mapping_status") == "conflict_source_ontology_aspect_mismatch":
                    decl_a = parse_csv_value(r.get("source_declared_aspect"))
                    deriv_a = parse_csv_value(r.get("derived_aspect"))
                    if decl_a in GO_ASPECTS:
                        conflict_aspects.add(decl_a)
                    if deriv_a in GO_ASPECTS:
                        conflict_aspects.add(deriv_a)

            for r in s_ann_pair:
                if r.get("mapping_status") == "conflict_source_ontology_aspect_mismatch":
                    r["_assigned_aspect"] = None
                else:
                    decl_a = parse_csv_value(r.get("source_declared_aspect"))
                    if decl_a in GO_ASPECTS:
                        # Case A / Case D declared: retain declared aspect with verbatim source GO ID
                        r["_assigned_aspect"] = decl_a
                    elif decl_a is None or decl_a == "unassigned":
                        deriv_a = parse_csv_value(r.get("derived_aspect"))
                        map_s = r.get("mapping_status")
                        if deriv_a in GO_ASPECTS and map_s in ("resolved_primary", "resolved_secondary_alt_id"):
                            # Case C: resolved active term mapped to derived aspect
                            r["_assigned_aspect"] = deriv_a
                        else:
                            # Case B (obsolete) or Case D (unknown/malformed): remains unassigned
                            r["_assigned_aspect"] = None
                    else:
                        r["_assigned_aspect"] = None

            has_any_source_terms = len(s_ann_pair) > 0
            all_source_aspects_undeclared = (
                has_any_source_terms
                and all(
                    parse_csv_value(r.get("source_declared_aspect")) in (None, "unassigned")
                    and r.get("_assigned_aspect") is None
                    for r in s_ann_pair
                )
            )

        for aspect in GO_ASPECTS:
            # QuickGO terms for this aspect (Policy B)
            q_aspect_rows = [r for r in q_ann_acc if r["go_aspect"] == aspect]
            q_terms_B = set(r["go_id"] for r in q_aspect_rows)

            # QuickGO status
            if qgo_cov_status == "unlinked_in_database":
                q_status = "unlinked"
                q_terms_count_B: Optional[int] = None
            elif qgo_cov_status == "absent_from_database":
                q_status = "absent"
                q_terms_count_B = None
            elif qgo_cov_status == "zero_annotations_found":
                q_status = "zero_annotations"
                q_terms_count_B = 0
            else:
                if len(q_terms_B) == 0:
                    q_status = "empty"
                    q_terms_count_B = 0
                else:
                    q_status = "available"
                    q_terms_count_B = len(q_terms_B)

            # Source terms for this aspect (Policy B)
            if not in_slice:
                s_status = "outside_slice"
                s_terms_count_B: Optional[int] = None
                s_terms_B: Set[str] = set()
                s_aspect_rows: List[Dict[str, Any]] = []
                unit_has_conflict = False
            elif aspect in conflict_aspects:
                # Quarantined due to aspect conflict contaminating this aspect unit
                s_status = "indeterminate"
                s_terms_count_B = None
                s_terms_B = set()
                s_aspect_rows = []
                unit_has_conflict = True
            elif all_source_aspects_undeclared:
                s_status = "indeterminate"
                s_terms_count_B = None
                s_terms_B = set()
                s_aspect_rows = []
                unit_has_conflict = False
            else:
                unit_has_conflict = False
                if derived_aspects_rows is None:
                    s_aspect_rows = [
                        r for r in s_ann_pair
                        if parse_csv_value(r.get("go_aspect")) == aspect
                    ]
                else:
                    s_aspect_rows = [
                        r for r in s_ann_pair
                        if r.get("_assigned_aspect") == aspect
                    ]
                s_terms_B = set(r["go_id"] for r in s_aspect_rows)
                if len(s_terms_B) == 0:
                    s_status = "empty"
                    s_terms_count_B = 0
                else:
                    s_status = "available"
                    s_terms_count_B = len(s_terms_B)

            # Build Policy B and Policy C
            for policy_id in POLICIES:
                concordance_id = (
                    f"MFP:CONC:{acc}:{protein_id}:{source_id}:{aspect}:{policy_id}"
                )

                if policy_id == "captured_inventory_overlap":
                    s_terms = s_terms_B
                    s_terms_count = s_terms_count_B
                    q_terms = q_terms_B
                    q_terms_count = q_terms_count_B
                    s_curr_status = s_status
                    q_curr_status = q_status

                    nd_rows_count = None
                    root_rows_count = None
                    nd_root_overlap = None
                    net_excluded = None
                    terms_lost = None
                    terms_retained_via_other = None
                    unassessed_evidence = None

                else:  # filtered_descriptive_overlap (Policy C)
                    # 1. QuickGO Filtering
                    nd_rows = [r for r in q_aspect_rows if r["evidence_code"] == "ND"]
                    root_rows = [r for r in q_aspect_rows if r["go_id"] in ROOT_TERMS]
                    overlap_rows = [
                        r for r in q_aspect_rows
                        if r["evidence_code"] == "ND" and r["go_id"] in ROOT_TERMS
                    ]

                    nd_rows_count = len(nd_rows)
                    root_rows_count = len(root_rows)
                    nd_root_overlap = len(overlap_rows)
                    net_excluded = nd_rows_count + root_rows_count - nd_root_overlap

                    retained_q_rows = [
                        r for r in q_aspect_rows
                        if r["evidence_code"] != "ND" and r["go_id"] not in ROOT_TERMS
                    ]
                    q_terms = set(r["go_id"] for r in retained_q_rows)

                    terms_lost = len(q_terms_B - q_terms)

                    # Non-root terms supported by >= 1 ND row that survived via eligible rows
                    nd_term_ids = set(r["go_id"] for r in nd_rows if r["go_id"] not in ROOT_TERMS)
                    terms_retained_via_other = len(nd_term_ids & q_terms)

                    if q_terms_count_B is None:
                        q_terms_count = None
                        q_curr_status = q_status
                    else:
                        q_terms_count = len(q_terms)
                        if q_terms_count == 0:
                            q_curr_status = "empty"
                        else:
                            q_curr_status = "available"

                    # 2. Source Filtering
                    unassessed_rows = [
                        r for r in s_aspect_rows
                        if not parse_csv_value(r.get("evidence_raw"))
                    ]
                    unassessed_evidence = len(unassessed_rows)

                    retained_s_rows = [
                        r for r in s_aspect_rows
                        if r["go_id"] not in ROOT_TERMS
                        and parse_csv_value(r.get("evidence_raw")) != "ND"
                    ]
                    s_terms = set(r["go_id"] for r in retained_s_rows)

                    if s_terms_count_B is None:
                        s_terms_count = None
                        s_curr_status = s_status
                    else:
                        s_terms_count = len(s_terms)
                        if s_terms_count == 0:
                            s_curr_status = "empty"
                        else:
                            s_curr_status = "available"

                if source_term_sets_out is not None:
                    if s_curr_status in ("available", "empty"):
                        source_term_sets_out[concordance_id] = set(s_terms)
                    else:
                        source_term_sets_out[concordance_id] = None

                # Metrics and Evaluability
                if s_terms_count is None or q_terms_count is None:
                    exact_overlap = None
                    union_terms = None
                    source_only = None
                    quickgo_only = None
                    jaccard = None
                    status = "not_evaluable"
                else:
                    if s_terms_count == 0 and q_terms_count == 0:
                        exact_overlap = 0
                        union_terms = 0
                        source_only = 0
                        quickgo_only = 0
                        jaccard = None
                        status = "not_evaluable"
                    elif s_terms_count == 0:
                        exact_overlap = 0
                        union_terms = q_terms_count
                        source_only = 0
                        quickgo_only = q_terms_count
                        jaccard = None
                        status = "not_evaluable"
                    elif q_terms_count == 0:
                        exact_overlap = 0
                        union_terms = s_terms_count
                        source_only = s_terms_count
                        quickgo_only = 0
                        jaccard = None
                        status = "not_evaluable"
                    else:
                        exact_overlap = len(s_terms & q_terms)
                        union_terms = len(s_terms | q_terms)
                        source_only = len(s_terms - q_terms)
                        quickgo_only = len(q_terms - s_terms)

                        if identity_review_status == "flagged_taxonomic_discrepancy":
                            jaccard = None
                            status = "not_evaluable"
                        else:
                            status = "evaluable"
                            jaccard = round(exact_overlap / union_terms, 4)

                # Diagnostic Precedence & Semicolon List
                primary_reason: Optional[str] = None
                secondary_reasons: List[str] = []

                if status == "not_evaluable":
                    all_detected: List[str] = []

                    if identity_review_status == "flagged_taxonomic_discrepancy":
                        all_detected.append("unresolved_biological_identity")

                    if s_status == "outside_slice":
                        all_detected.append("source_record_outside_slice")
                    elif s_status == "indeterminate":
                        all_detected.append("source_aspect_indeterminate")
                    elif s_status == "empty":
                        all_detected.append("source_record_no_terms_aspect")

                    if q_status == "unlinked":
                        all_detected.append("accession_unlinked_in_capture")
                    elif q_status == "absent":
                        all_detected.append("accession_absent_from_capture")
                    elif q_status == "zero_annotations":
                        all_detected.append("external_zero_annotations_overall")
                    elif q_status == "empty":
                        all_detected.append("external_zero_annotations_aspect")

                    if policy_id == "filtered_descriptive_overlap":
                        if s_terms_count_B and s_terms_count_B > 0 and s_terms_count == 0:
                            all_detected.append("empty_after_filtering")
                        if q_terms_count_B and q_terms_count_B > 0 and q_terms_count == 0:
                            all_detected.append("empty_after_filtering")

                    # Order of precedence
                    precedence = [
                        "unresolved_biological_identity",
                        "source_record_outside_slice",
                        "source_input_unavailable",
                        "source_aspect_indeterminate",
                        "accession_unlinked_in_capture",
                        "accession_absent_from_capture",
                        "external_zero_annotations_overall",
                        "empty_after_filtering",
                        "external_zero_annotations_aspect",
                        "source_record_no_terms_aspect",
                    ]

                    primary_reason = None
                    for p in precedence:
                        if p in all_detected:
                            primary_reason = p
                            break

                    secondary_reasons = [r for r in all_detected if r != primary_reason]
                    if unit_has_conflict and "source_aspect_conflict" not in secondary_reasons:
                        secondary_reasons.append("source_aspect_conflict")

                sec_str = ";".join(secondary_reasons) if secondary_reasons else None

                row = {
                    "concordance_id": concordance_id,
                    "accession": acc,
                    "protein_id": protein_id,
                    "source_id": source_id,
                    "aspect": aspect,
                    "policy_id": policy_id,
                    "source_inventory_status": s_curr_status,
                    "quickgo_inventory_status": q_curr_status,
                    "source_terms_count": s_terms_count,
                    "quickgo_terms_count": q_terms_count,
                    "exact_overlap_count": exact_overlap,
                    "union_terms_count": union_terms,
                    "source_only_count": source_only,
                    "quickgo_only_count": quickgo_only,
                    "jaccard_similarity": jaccard,
                    "concordance_status": status,
                    "primary_non_evaluable_reason": primary_reason,
                    "secondary_non_evaluable_reasons": sec_str,
                    "identity_review_status": identity_review_status,
                    "nd_matching_rows_count": nd_rows_count,
                    "root_matching_rows_count": root_rows_count,
                    "nd_root_overlap_rows_count": nd_root_overlap,
                    "net_excluded_rows_count": net_excluded,
                    "terms_lost_after_filtering_count": terms_lost,
                    "terms_retained_via_other_rows_count": terms_retained_via_other,
                    "unassessed_evidence_rows_count": unassessed_evidence,
                }
                rows.append(row)

    rows.sort(key=lambda r: (r["accession"], r["source_id"], r["aspect"], r["policy_id"]))
    return rows


def build_reference_concordance(
    functional_claims: List[Dict[str, Any]],
    raw_annotations: List[Dict[str, Any]],
    raw_coverage: List[Dict[str, Any]],
    functional_coverage: List[Dict[str, Any]],
    catalog_map: Dict[str, str],
    pairs: Optional[List[Tuple[str, str]]] = None,
) -> List[Dict[str, Any]]:
    """Build the 12-row descriptive reference overlap comparison table under Option A."""
    cov_by_acc = {r["accession"]: r for r in raw_coverage}
    slice_pids = {r["protein_id"] for r in functional_coverage}

    target_pairs = pairs if pairs is not None else VERIFIED_COHORT_PAIRS
    rows: List[Dict[str, Any]] = []

    for acc, source_id in target_pairs:
        if acc not in catalog_map or acc not in cov_by_acc:
            continue
        protein_id = catalog_map[acc]
        cov_info = cov_by_acc[acc]
        identity_review_status = cov_info["identity_review_status"]
        qgo_cov_status = cov_info["quickgo_coverage_status"]

        ref_conc_id = f"MFP:REFCONC:{acc}:{protein_id}:{source_id}"

        # 1. Source References and Extraction Check
        cov_rec = next(
            (r for r in functional_coverage if r["protein_id"] == protein_id and r["source_id"] == source_id),
            None,
        )
        if cov_rec is None:
            in_slice = False
            extraction_incomplete = False
        elif cov_rec.get("coverage_status") == "parse_failure":
            in_slice = True
            extraction_incomplete = True
        else:
            in_slice = True
            extraction_incomplete = False

        if not in_slice:
            s_refs_count: Optional[int] = None
            s_unres_count: Optional[int] = None
            unres_ids: Optional[str] = None
            s_refs: Set[str] = set()
            completeness = "indeterminate"
        elif extraction_incomplete:
            s_refs_count = None
            s_unres_count = None
            unres_ids = None
            s_refs = set()
            completeness = "indeterminate"
        else:
            s_claims = [
                r for r in functional_claims
                if r["protein_id"] == protein_id and r["source_id"] == source_id
            ]
            s_refs = set()
            unresolved_tokens: Set[str] = set()
            for sc in s_claims:
                for fld in ["record_reference_ids", "linked_reference_ids"]:
                    val = sc.get(fld)
                    if val:
                        cleaned = str(val).replace(",", ";")
                        for item in cleaned.split(";"):
                            curie, unres = interpret_reference_token(item)
                            if curie:
                                s_refs.add(curie)
                            if unres:
                                unresolved_tokens.add(unres)
            s_refs_count = len(s_refs)
            s_unres_count = len(unresolved_tokens)
            unres_ids = ";".join(sorted(unresolved_tokens)) if unresolved_tokens else None

            if s_refs_count == 0 and s_unres_count == 0:
                completeness = "empty"
            elif s_refs_count == 0 and s_unres_count > 0:
                completeness = "uninterpretable"
            elif s_unres_count > 0:
                completeness = "partial"
            else:
                completeness = "complete"

        # 2. QuickGO References
        if qgo_cov_status in ("unlinked_in_database", "absent_from_database"):
            q_refs_count: Optional[int] = None
            q_refs: Set[str] = set()
        else:
            q_ann_acc = [r for r in raw_annotations if r["accession"] == acc]
            q_refs = set()
            for r in q_ann_acc:
                pub = parse_csv_value(r.get("publication_id"))
                if pub:
                    curie, _ = interpret_reference_token(pub)
                    if curie:
                        q_refs.add(curie)
            q_refs_count = len(q_refs)

        # 3. Metrics
        if s_refs_count is None or q_refs_count is None:
            shared_count = None
            source_only = None
            quickgo_only = None
            jaccard = None
            status = "not_evaluable"
            shared_ids = None
        else:
            if s_refs_count == 0 and q_refs_count == 0:
                shared_count = 0
                source_only = 0
                quickgo_only = 0
                jaccard = None
                status = "not_evaluable"
                shared_ids = None
            elif s_refs_count == 0:
                shared_count = 0
                source_only = 0
                quickgo_only = q_refs_count
                jaccard = None
                status = "not_evaluable"
                shared_ids = None
            elif q_refs_count == 0:
                shared_count = 0
                source_only = s_refs_count
                quickgo_only = 0
                jaccard = None
                status = "not_evaluable"
                shared_ids = None
            else:
                shared_set = s_refs & q_refs
                shared_count = len(shared_set)
                source_only = len(s_refs - q_refs)
                quickgo_only = len(q_refs - s_refs)
                union_count = len(s_refs | q_refs)

                shared_ids = ";".join(sorted(shared_set)) if shared_set else None

                if identity_review_status == "flagged_taxonomic_discrepancy":
                    jaccard = None
                    status = "not_evaluable"
                else:
                    status = "evaluable"
                    jaccard = round(shared_count / union_count, 4)

        # Diagnostics
        primary_reason = None
        sec_reasons = []
        if status == "not_evaluable":
            all_detected = []
            if identity_review_status == "flagged_taxonomic_discrepancy":
                all_detected.append("unresolved_biological_identity")
            if not in_slice:
                all_detected.append("source_record_outside_slice")
            elif extraction_incomplete:
                all_detected.append("source_extraction_incomplete")
            elif s_refs_count == 0:
                all_detected.append("source_record_zero_references")

            if qgo_cov_status == "unlinked_in_database":
                all_detected.append("accession_unlinked_in_capture")
            elif qgo_cov_status == "absent_from_database":
                all_detected.append("accession_absent_from_capture")
            elif q_refs_count == 0:
                all_detected.append("external_zero_references")

            precedence = [
                "unresolved_biological_identity",
                "source_record_outside_slice",
                "source_extraction_incomplete",
                "accession_unlinked_in_capture",
                "accession_absent_from_capture",
                "external_zero_references",
                "source_record_zero_references",
            ]
            for p in precedence:
                if p in all_detected:
                    primary_reason = p
                    break
            sec_reasons = [r for r in all_detected if r != primary_reason]

        sec_str = ";".join(sec_reasons) if sec_reasons else None

        row = {
            "reference_concordance_id": ref_conc_id,
            "accession": acc,
            "protein_id": protein_id,
            "source_id": source_id,
            "source_references_count": s_refs_count,
            "source_unresolved_references_count": s_unres_count,
            "quickgo_references_count": q_refs_count,
            "shared_references_count": shared_count,
            "source_only_references_count": source_only,
            "quickgo_only_references_count": quickgo_only,
            "jaccard_similarity": jaccard,
            "reference_concordance_status": status,
            "comparison_completeness": completeness,
            "primary_non_evaluable_reason": primary_reason,
            "secondary_non_evaluable_reasons": sec_str,
            "shared_reference_ids": shared_ids,
            "unresolved_reference_ids": unres_ids,
            "identity_review_status": identity_review_status,
        }
        rows.append(row)

    rows.sort(key=lambda r: (r["accession"], r["source_id"]))
    return rows


def validate_slice_outputs(
    annotations: List[Dict[str, Any]],
    coverage: List[Dict[str, Any]],
    concordance: List[Dict[str, Any]],
    ref_concordance: List[Dict[str, Any]],
    schemas_dir: Path,
) -> None:
    """Validate all normalized slice outputs against Draft 2020-12 schemas & cross-record invariants."""
    # 1. Load Schemas
    schema_ann = json.loads((schemas_dir / "external_quickgo_annotations.schema.json").read_text())
    schema_cov = json.loads((schemas_dir / "quickgo_coverage.schema.json").read_text())
    schema_cnc = json.loads((schemas_dir / "quickgo_concordance.schema.json").read_text())
    schema_ref = json.loads((schemas_dir / "quickgo_reference_concordance.schema.json").read_text())

    val_ann = jsonschema.Draft202012Validator(schema_ann)
    val_cov = jsonschema.Draft202012Validator(schema_cov)
    val_cnc = jsonschema.Draft202012Validator(schema_cnc)
    val_ref = jsonschema.Draft202012Validator(schema_ref)

    # 2. Schema Validation
    for r in annotations:
        val_ann.validate(r)
    for r in coverage:
        val_cov.validate(r)
    for r in concordance:
        val_cnc.validate(r)
    for r in ref_concordance:
        val_ref.validate(r)

    # 3. Cross-Record Cardinality & Key Invariants
    if len(annotations) != 156:
        raise ValueError(f"Expected 156 annotations, got {len(annotations)}")
    if len(coverage) != 8:
        raise ValueError(f"Expected 8 coverage rows, got {len(coverage)}")
    if len(concordance) != 72:
        raise ValueError(f"Expected 72 concordance rows, got {len(concordance)}")
    if len(ref_concordance) != 12:
        raise ValueError(f"Expected 12 reference rows, got {len(ref_concordance)}")

    # Uniqueness of primary keys
    ann_ids = [r["annotation_id"] for r in annotations]
    if len(ann_ids) != len(set(ann_ids)):
        raise ValueError("Duplicate annotation_id found")

    cov_accs = [r["accession"] for r in coverage]
    if len(cov_accs) != len(set(cov_accs)):
        raise ValueError("Duplicate accession in coverage")

    conc_ids = [r["concordance_id"] for r in concordance]
    if len(conc_ids) != len(set(conc_ids)):
        raise ValueError("Duplicate concordance_id found")

    ref_ids = [r["reference_concordance_id"] for r in ref_concordance]
    if len(ref_ids) != len(set(ref_ids)):
        raise ValueError("Duplicate reference_concordance_id found")

    # Metric arithmetic invariants
    for r in concordance:
        s_cnt = r["source_terms_count"]
        q_cnt = r["quickgo_terms_count"]
        ov_cnt = r["exact_overlap_count"]
        un_cnt = r["union_terms_count"]
        j = r["jaccard_similarity"]
        st = r["concordance_status"]

        if s_cnt is not None and q_cnt is not None:
            if ov_cnt is not None and un_cnt is not None:
                assert ov_cnt <= min(s_cnt, q_cnt), f"Intersection exceeds component set: {r}"
                assert un_cnt <= s_cnt + q_cnt, f"Union exceeds sum of sets: {r}"
                if un_cnt > 0:
                    assert un_cnt == s_cnt + q_cnt - ov_cnt, f"Inclusion-exclusion formula failed: {r}"
            if s_cnt == 0 or q_cnt == 0:
                assert j is None, f"Jaccard must be null when either set is empty: {r}"
                assert st == "not_evaluable"
            elif r["identity_review_status"] == "flagged_taxonomic_discrepancy":
                assert j is None, f"Jaccard must be null for identity discrepancy: {r}"
                assert st == "not_evaluable"
            else:
                assert st == "evaluable"
                assert j is not None
                if ov_cnt == 0:
                    assert j == 0.0


def parse_concordance_csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Parse CSV string values to typed python primitives for concordance schema validation.

    Preserves unexpected properties so schema validation can enforce additionalProperties.
    """
    parsed: Dict[str, Any] = dict(row)
    for k in [
        "concordance_id",
        "accession",
        "protein_id",
        "source_id",
        "aspect",
        "policy_id",
        "source_inventory_status",
        "quickgo_inventory_status",
        "concordance_status",
        "identity_review_status",
    ]:
        if k in parsed and parsed[k] is not None:
            parsed[k] = str(parsed[k]).strip()

    for k in ["primary_non_evaluable_reason", "secondary_non_evaluable_reasons"]:
        if k in parsed:
            parsed[k] = parse_csv_value(parsed[k])

    for k in [
        "source_terms_count",
        "quickgo_terms_count",
        "exact_overlap_count",
        "union_terms_count",
        "source_only_count",
        "quickgo_only_count",
        "nd_matching_rows_count",
        "root_matching_rows_count",
        "nd_root_overlap_rows_count",
        "net_excluded_rows_count",
        "terms_lost_after_filtering_count",
        "terms_retained_via_other_rows_count",
        "unassessed_evidence_rows_count",
    ]:
        if k in parsed:
            v = parse_csv_value(parsed[k])
            parsed[k] = int(v) if v is not None else None

    if "jaccard_similarity" in parsed:
        v = parse_csv_value(parsed["jaccard_similarity"])
        parsed["jaccard_similarity"] = float(v) if v is not None else None

    return parsed


def parse_transition_csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Parse CSV string values to typed python primitives for transition schema validation.

    Preserves unexpected properties so schema validation can enforce additionalProperties.
    Rejects malformed boolean tokens rather than converting unrecognized values to false.
    """
    parsed: Dict[str, Any] = dict(row)
    for k in [
        "transition_id",
        "accession",
        "protein_id",
        "source_id",
        "aspect",
        "policy_id",
        "baseline_concordance_status",
        "recomparison_concordance_status",
        "evaluability_transition",
        "primary_reason_transition",
        "metric_transition",
        "overall_transition_classification",
    ]:
        if k in parsed and parsed[k] is not None:
            parsed[k] = str(parsed[k]).strip()

    for k in ["baseline_primary_reason", "recomparison_primary_reason", "notes"]:
        if k in parsed:
            parsed[k] = parse_csv_value(parsed[k])

    if "source_set_content_changed" in parsed:
        val_bool = parsed["source_set_content_changed"]
        if isinstance(val_bool, bool):
            parsed["source_set_content_changed"] = val_bool
        elif isinstance(val_bool, str):
            token = val_bool.strip().lower()
            if token in ("true", "1", "t"):
                parsed["source_set_content_changed"] = True
            elif token in ("false", "0", "f"):
                parsed["source_set_content_changed"] = False
            else:
                raise ConcordanceValidationError(
                    f"Malformed CSV boolean value for 'source_set_content_changed': '{val_bool}'"
                )
        else:
            raise ConcordanceValidationError(
                f"Malformed boolean value for 'source_set_content_changed': {val_bool}"
            )

    for k in [
        "baseline_source_terms_count",
        "recomparison_source_terms_count",
        "delta_source_terms_count",
        "baseline_quickgo_terms_count",
        "recomparison_quickgo_terms_count",
        "delta_quickgo_terms_count",
        "baseline_exact_overlap_count",
        "recomparison_exact_overlap_count",
        "delta_exact_overlap_count",
        "baseline_union_terms_count",
        "recomparison_union_terms_count",
        "delta_union_terms_count",
    ]:
        if k in parsed:
            v = parse_csv_value(parsed[k])
            parsed[k] = int(v) if v is not None else None

    for k in [
        "baseline_jaccard_similarity",
        "recomparison_jaccard_similarity",
        "delta_jaccard_similarity",
    ]:
        if k in parsed:
            v = parse_csv_value(parsed[k])
            parsed[k] = float(v) if v is not None else None

    return parsed


def build_concordance_transition_matrix(
    baseline_concordance_rows: List[Dict[str, Any]],
    recomparison_concordance_rows: List[Dict[str, Any]],
    baseline_source_sets: Optional[Dict[str, Set[str]]] = None,
    recomparison_source_sets: Optional[Dict[str, Set[str]]] = None,
) -> List[Dict[str, Any]]:
    """Build the transition matrix comparing baseline and recomparison concordance matrices.

    Args:
        baseline_concordance_rows: Rows from baseline concordance matrix.
        recomparison_concordance_rows: Rows from recomputed concordance matrix.
        baseline_source_sets: Mapping of concordance_id -> set of source GO IDs in baseline.
        recomparison_source_sets: Mapping of concordance_id -> set of source GO IDs in recomparison.

    Returns:
        List of transition row dicts conforming to quickgo_concordance_transition.schema.json.
    """
    # 1. Reject duplicates and verify concordance_id against component key
    base_by_key: Dict[Tuple[str, str, str, str, str], Dict[str, Any]] = {}
    for idx, r in enumerate(baseline_concordance_rows):
        for fld in ("accession", "protein_id", "source_id", "aspect", "policy_id", "concordance_id"):
            if not r.get(fld) or not str(r[fld]).strip():
                raise ConcordanceValidationError(f"Baseline row {idx} is missing required field '{fld}'")
        acc, pid, src, asp, pol = (
            str(r["accession"]).strip(),
            str(r["protein_id"]).strip(),
            str(r["source_id"]).strip(),
            str(r["aspect"]).strip(),
            str(r["policy_id"]).strip(),
        )
        expected_cid = f"MFP:CONC:{acc}:{pid}:{src}:{asp}:{pol}"
        actual_cid = str(r["concordance_id"]).strip()
        if actual_cid != expected_cid:
            raise ConcordanceValidationError(
                f"Concordance ID mismatch in baseline row {idx}: '{actual_cid}' != expected '{expected_cid}'"
            )
        key = (acc, pid, src, asp, pol)
        if key in base_by_key:
            raise ConcordanceValidationError(f"Duplicate comparison key in baseline concordance rows: {key}")
        base_by_key[key] = r

    recomp_by_key: Dict[Tuple[str, str, str, str, str], Dict[str, Any]] = {}
    for idx, r in enumerate(recomparison_concordance_rows):
        for fld in ("accession", "protein_id", "source_id", "aspect", "policy_id", "concordance_id"):
            if not r.get(fld) or not str(r[fld]).strip():
                raise ConcordanceValidationError(f"Recomparison row {idx} is missing required field '{fld}'")
        acc, pid, src, asp, pol = (
            str(r["accession"]).strip(),
            str(r["protein_id"]).strip(),
            str(r["source_id"]).strip(),
            str(r["aspect"]).strip(),
            str(r["policy_id"]).strip(),
        )
        expected_cid = f"MFP:CONC:{acc}:{pid}:{src}:{asp}:{pol}"
        actual_cid = str(r["concordance_id"]).strip()
        if actual_cid != expected_cid:
            raise ConcordanceValidationError(
                f"Concordance ID mismatch in recomparison row {idx}: '{actual_cid}' != expected '{expected_cid}'"
            )
        key = (acc, pid, src, asp, pol)
        if key in recomp_by_key:
            raise ConcordanceValidationError(f"Duplicate comparison key in recomparison concordance rows: {key}")
        recomp_by_key[key] = r

    # 2. Require exact baseline/recomparison key correspondence
    if set(base_by_key.keys()) != set(recomp_by_key.keys()):
        missing = set(base_by_key.keys()) - set(recomp_by_key.keys())
        extra = set(recomp_by_key.keys()) - set(base_by_key.keys())
        raise ConcordanceValidationError(
            f"Comparison universe key mismatch: {len(missing)} missing in recomparison, "
            f"{len(extra)} unexpected in recomparison"
        )

    transition_rows: List[Dict[str, Any]] = []

    for key, b_row in base_by_key.items():
        r_row = recomp_by_key[key]
        acc, pid, src_id, aspect, policy_id = key
        t_id = f"MFP:TRNS:{acc}:{pid}:{src_id}:{aspect}:{policy_id}"
        cid = f"MFP:CONC:{acc}:{pid}:{src_id}:{aspect}:{policy_id}"

        b_st = b_row["concordance_status"]
        r_st = r_row["concordance_status"]

        # Evaluability transition
        if b_st == "evaluable" and r_st == "evaluable":
            eval_trans = "remains_evaluable"
        elif b_st == "not_evaluable" and r_st == "evaluable":
            eval_trans = "newly_evaluable"
        elif b_st == "evaluable" and r_st == "not_evaluable":
            eval_trans = "becomes_non_evaluable"
        else:
            eval_trans = "remains_non_evaluable"

        # Primary reason transition
        b_reason = parse_csv_value(b_row.get("primary_non_evaluable_reason"))
        r_reason = parse_csv_value(r_row.get("primary_non_evaluable_reason"))
        if b_st == "evaluable" and r_st == "evaluable":
            reason_trans = "unchanged_null"
        elif b_st == "not_evaluable" and r_st == "evaluable":
            reason_trans = "became_evaluable"
        elif b_st == "evaluable" and r_st == "not_evaluable":
            reason_trans = "became_non_evaluable"
        else:
            if b_reason == r_reason:
                reason_trans = "unchanged_reason"
            else:
                reason_trans = "reason_changed"

        # Count deltas
        def _delta_int(r_val: Any, b_val: Any) -> Optional[int]:
            v_r = parse_csv_value(r_val)
            v_b = parse_csv_value(b_val)
            if v_r is not None and v_b is not None:
                return int(v_r) - int(v_b)
            return None

        d_source = _delta_int(r_row.get("source_terms_count"), b_row.get("source_terms_count"))
        d_quickgo = _delta_int(r_row.get("quickgo_terms_count"), b_row.get("quickgo_terms_count"))
        d_overlap = _delta_int(r_row.get("exact_overlap_count"), b_row.get("exact_overlap_count"))
        d_union = _delta_int(r_row.get("union_terms_count"), b_row.get("union_terms_count"))

        # Source set content change
        b_inv = b_row.get("source_inventory_status")
        r_inv = r_row.get("source_inventory_status")
        b_is_comparable = b_inv in ("available", "empty")
        r_is_comparable = r_inv in ("available", "empty")

        row_notes: Optional[str] = None
        if b_is_comparable and r_is_comparable:
            if baseline_source_sets is None or recomparison_source_sets is None:
                raise ConcordanceValidationError(
                    f"Missing required source-set maps for comparable inventory '{cid}'"
                )
            if cid not in baseline_source_sets:
                raise ConcordanceValidationError(
                    f"Missing required comparison key '{cid}' in baseline_source_sets map"
                )
            if cid not in recomparison_source_sets:
                raise ConcordanceValidationError(
                    f"Missing required comparison key '{cid}' in recomparison_source_sets map"
                )
            b_set = baseline_source_sets[cid]
            r_set = recomparison_source_sets[cid]
            if b_set is None or r_set is None:
                raise ConcordanceValidationError(
                    f"Source-set is None for comparable inventory '{cid}' (expected set or empty set)"
                )
            source_set_content_changed = (b_set != r_set)
        elif b_is_comparable != r_is_comparable:
            source_set_content_changed = True
            row_notes = f"Inventory comparability status changed: baseline '{b_inv}' vs recomparison '{r_inv}'"
        else:
            # Both non-comparable ("indeterminate", "outside_slice", "unavailable")
            # Operational convention: non-comparable inventories cannot be biologically compared.
            # If statuses are identical, source_set_content_changed is False by convention (no biological equality asserted).
            # If statuses differ, source_set_content_changed is True.
            if b_inv == r_inv:
                source_set_content_changed = False
                row_notes = "Non-comparable inventories: operational convention applied (no biological equality asserted)"
            else:
                source_set_content_changed = True
                row_notes = f"Non-comparable inventory status shifted: baseline '{b_inv}' vs recomparison '{r_inv}'"

        # Jaccard similarity and metric transition (4-decimal precision)
        b_j = parse_csv_value(b_row.get("jaccard_similarity"))
        r_j = parse_csv_value(r_row.get("jaccard_similarity"))
        b_j_float = float(b_j) if b_j is not None else None
        r_j_float = float(r_j) if r_j is not None else None

        if b_j_float is not None and r_j_float is not None:
            d_jaccard: Optional[float] = round(r_j_float - b_j_float, 4)
        else:
            d_jaccard = None

        if b_j_float is None and r_j_float is None:
            metric_trans = "remains_null"
        elif b_j_float is None and r_j_float is not None:
            metric_trans = "score_newly_defined"
        elif b_j_float is not None and r_j_float is None:
            metric_trans = "score_became_null"
        else:
            if d_jaccard == 0.0:
                metric_trans = "score_identical"
            elif d_jaccard is not None and d_jaccard > 0.0:
                metric_trans = "score_increased"
            else:
                metric_trans = "score_decreased"

        # Overall transition classification (Strict Precedence)
        if b_st == "not_evaluable" and r_st == "evaluable":
            overall = "newly_evaluable"
        elif b_st == "evaluable" and r_st == "not_evaluable":
            overall = "becomes_non_evaluable"
        elif b_st == "evaluable" and r_st == "evaluable":
            if d_jaccard is not None and d_jaccard > 0.0:
                overall = "evaluable_score_increased"
            elif d_jaccard is not None and d_jaccard < 0.0:
                overall = "evaluable_score_decreased"
            else:
                counts_or_set_changed = (
                    d_source != 0 or d_quickgo != 0 or d_overlap != 0 or d_union != 0 or source_set_content_changed
                )
                if counts_or_set_changed:
                    overall = "evaluable_score_identical_inventory_changed"
                else:
                    overall = "evaluable_fully_identical"
        else:  # both not_evaluable
            if b_reason != r_reason:
                overall = "non_evaluable_reason_changed"
            else:
                b_sec = parse_csv_value(b_row.get("secondary_non_evaluable_reasons"))
                r_sec = parse_csv_value(r_row.get("secondary_non_evaluable_reasons"))
                b_inv_s = b_row.get("source_inventory_status")
                r_inv_s = r_row.get("source_inventory_status")
                b_inv_q = b_row.get("quickgo_inventory_status")
                r_inv_q = r_row.get("quickgo_inventory_status")
                diag_or_inv_changed = (
                    b_sec != r_sec
                    or b_inv_s != r_inv_s
                    or b_inv_q != r_inv_q
                    or (d_source is not None and d_source != 0)
                    or (d_quickgo is not None and d_quickgo != 0)
                    or source_set_content_changed
                )
                if diag_or_inv_changed:
                    overall = "non_evaluable_diagnostics_or_inventory_changed"
                else:
                    overall = "non_evaluable_fully_identical"

        def _as_int_or_none(val: Any) -> Optional[int]:
            v = parse_csv_value(val)
            return int(v) if v is not None else None

        t_row: Dict[str, Any] = {
            "transition_id": t_id,
            "accession": acc,
            "protein_id": pid,
            "source_id": src_id,
            "aspect": aspect,
            "policy_id": policy_id,
            "baseline_concordance_status": b_st,
            "recomparison_concordance_status": r_st,
            "evaluability_transition": eval_trans,
            "baseline_primary_reason": b_reason,
            "recomparison_primary_reason": r_reason,
            "primary_reason_transition": reason_trans,
            "baseline_source_terms_count": _as_int_or_none(b_row.get("source_terms_count")),
            "recomparison_source_terms_count": _as_int_or_none(r_row.get("source_terms_count")),
            "delta_source_terms_count": d_source,
            "baseline_quickgo_terms_count": _as_int_or_none(b_row.get("quickgo_terms_count")),
            "recomparison_quickgo_terms_count": _as_int_or_none(r_row.get("quickgo_terms_count")),
            "delta_quickgo_terms_count": d_quickgo,
            "baseline_exact_overlap_count": _as_int_or_none(b_row.get("exact_overlap_count")),
            "recomparison_exact_overlap_count": _as_int_or_none(r_row.get("exact_overlap_count")),
            "delta_exact_overlap_count": d_overlap,
            "baseline_union_terms_count": _as_int_or_none(b_row.get("union_terms_count")),
            "recomparison_union_terms_count": _as_int_or_none(r_row.get("union_terms_count")),
            "delta_union_terms_count": d_union,
            "source_set_content_changed": source_set_content_changed,
            "baseline_jaccard_similarity": b_j_float,
            "recomparison_jaccard_similarity": r_j_float,
            "delta_jaccard_similarity": d_jaccard,
            "metric_transition": metric_trans,
            "overall_transition_classification": overall,
            "notes": row_notes,
        }
        transition_rows.append(t_row)

    transition_rows.sort(key=lambda r: (r["accession"], r["source_id"], r["aspect"], r["policy_id"]))
    return transition_rows


def validate_transition_matrix(
    rows: List[Dict[str, Any]],
    baseline_rows: Optional[List[Dict[str, Any]]] = None,
    recomparison_rows: Optional[List[Dict[str, Any]]] = None,
    schema_path: Optional[Path] = None,
) -> None:
    """Validate transition matrix against JSON Schema and programmatic invariants."""
    if schema_path is None:
        schema_path = Path(__file__).resolve().parent.parent.parent / "data/curated/quickgo_concordance_transition.schema.json"

    if not schema_path.is_file():
        raise FileNotFoundError(f"Transition schema not found at {schema_path}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    # 1. Row-level schema validation
    parsed_rows = []
    for r in rows:
        parsed = parse_transition_csv_row(r)
        validator.validate(parsed)
        parsed_rows.append(parsed)

    # 2. Key uniqueness and ID correspondence
    t_ids: Set[str] = set()
    for r in parsed_rows:
        tid = r["transition_id"]
        if tid in t_ids:
            raise ConcordanceValidationError(f"Duplicate transition_id found in transition matrix: {tid}")
        t_ids.add(tid)

        expected_tid = f"MFP:TRNS:{r['accession']}:{r['protein_id']}:{r['source_id']}:{r['aspect']}:{r['policy_id']}"
        if tid != expected_tid:
            raise ConcordanceValidationError(
                f"Transition ID mismatch: '{tid}' != expected '{expected_tid}'"
            )

    # 3. Arithmetic and categorical invariants
    for r in parsed_rows:
        tid = r["transition_id"]
        b_s = r["baseline_source_terms_count"]
        r_s = r["recomparison_source_terms_count"]
        d_s = r["delta_source_terms_count"]
        if b_s is not None and r_s is not None:
            if d_s != (r_s - b_s):
                raise ConcordanceValidationError(f"Arithmetic delta error in delta_source_terms_count: {d_s} != {r_s} - {b_s} in {tid}")
        elif d_s is not None:
            raise ConcordanceValidationError(f"delta_source_terms_count must be null when either baseline or recomparison is null: {tid}")

        b_q = r["baseline_quickgo_terms_count"]
        r_q = r["recomparison_quickgo_terms_count"]
        d_q = r["delta_quickgo_terms_count"]
        if b_q is not None and r_q is not None:
            if d_q != (r_q - b_q):
                raise ConcordanceValidationError(f"Arithmetic delta error in delta_quickgo_terms_count: {d_q} != {r_q} - {b_q} in {tid}")
        elif d_q is not None:
            raise ConcordanceValidationError(f"delta_quickgo_terms_count must be null when either baseline or recomparison is null: {tid}")

        b_o = r["baseline_exact_overlap_count"]
        r_o = r["recomparison_exact_overlap_count"]
        d_o = r["delta_exact_overlap_count"]
        if b_o is not None and r_o is not None:
            if d_o != (r_o - b_o):
                raise ConcordanceValidationError(f"Arithmetic delta error in delta_exact_overlap_count: {d_o} != {r_o} - {b_o} in {tid}")
        elif d_o is not None:
            raise ConcordanceValidationError(f"delta_exact_overlap_count must be null when either baseline or recomparison is null: {tid}")

        b_u = r["baseline_union_terms_count"]
        r_u = r["recomparison_union_terms_count"]
        d_u = r["delta_union_terms_count"]
        if b_u is not None and r_u is not None:
            if d_u != (r_u - b_u):
                raise ConcordanceValidationError(f"Arithmetic delta error in delta_union_terms_count: {d_u} != {r_u} - {b_u} in {tid}")
        elif d_u is not None:
            raise ConcordanceValidationError(f"delta_union_terms_count must be null when either baseline or recomparison is null: {tid}")

        b_j = r["baseline_jaccard_similarity"]
        r_j = r["recomparison_jaccard_similarity"]
        d_j = r["delta_jaccard_similarity"]
        if b_j is not None and r_j is not None:
            expected_dj = round(r_j - b_j, 4)
            if d_j != expected_dj:
                raise ConcordanceValidationError(f"Arithmetic delta error in delta_jaccard_similarity: {d_j} != {expected_dj} in {tid}")
        elif d_j is not None:
            raise ConcordanceValidationError(f"delta_jaccard_similarity must be null when either baseline or recomparison is null: {tid}")

        m_t = r["metric_transition"]
        if b_j is None and r_j is None:
            if m_t != "remains_null":
                raise ConcordanceValidationError(f"metric_transition must be 'remains_null' when both Jaccard scores are null: {tid}")
        elif b_j is None and r_j is not None:
            if m_t != "score_newly_defined":
                raise ConcordanceValidationError(f"metric_transition must be 'score_newly_defined': {tid}")
        elif b_j is not None and r_j is None:
            if m_t != "score_became_null":
                raise ConcordanceValidationError(f"metric_transition must be 'score_became_null': {tid}")
        else:
            if d_j == 0.0 and m_t != "score_identical":
                raise ConcordanceValidationError(f"metric_transition must be 'score_identical': {tid}")
            elif d_j is not None and d_j > 0.0 and m_t != "score_increased":
                raise ConcordanceValidationError(f"metric_transition must be 'score_increased': {tid}")
            elif d_j is not None and d_j < 0.0 and m_t != "score_decreased":
                raise ConcordanceValidationError(f"metric_transition must be 'score_decreased': {tid}")

        b_st = r["baseline_concordance_status"]
        r_st = r["recomparison_concordance_status"]
        e_t = r["evaluability_transition"]
        if b_st == "evaluable" and r_st == "evaluable" and e_t != "remains_evaluable":
            raise ConcordanceValidationError(f"evaluability_transition mismatch: {tid}")
        elif b_st == "not_evaluable" and r_st == "evaluable" and e_t != "newly_evaluable":
            raise ConcordanceValidationError(f"evaluability_transition mismatch: {tid}")
        elif b_st == "evaluable" and r_st == "not_evaluable" and e_t != "becomes_non_evaluable":
            raise ConcordanceValidationError(f"evaluability_transition mismatch: {tid}")
        elif b_st == "not_evaluable" and r_st == "not_evaluable" and e_t != "remains_non_evaluable":
            raise ConcordanceValidationError(f"evaluability_transition mismatch: {tid}")

        b_reas = r["baseline_primary_reason"]
        r_reas = r["recomparison_primary_reason"]
        p_t = r["primary_reason_transition"]
        if b_st == "evaluable" and r_st == "evaluable":
            if p_t != "unchanged_null":
                raise ConcordanceValidationError(f"primary_reason_transition must be 'unchanged_null': {tid}")
        elif b_st == "not_evaluable" and r_st == "evaluable":
            if p_t != "became_evaluable":
                raise ConcordanceValidationError(f"primary_reason_transition must be 'became_evaluable': {tid}")
        elif b_st == "evaluable" and r_st == "not_evaluable":
            if p_t != "became_non_evaluable":
                raise ConcordanceValidationError(f"primary_reason_transition must be 'became_non_evaluable': {tid}")
        else:
            if b_reas == r_reas and p_t != "unchanged_reason":
                raise ConcordanceValidationError(f"primary_reason_transition must be 'unchanged_reason': {tid}")
            elif b_reas != r_reas and p_t != "reason_changed":
                raise ConcordanceValidationError(f"primary_reason_transition must be 'reason_changed': {tid}")

        # Check overall classification precedence
        ov_cls = r["overall_transition_classification"]
        set_changed = r["source_set_content_changed"]
        if b_st == "not_evaluable" and r_st == "evaluable":
            expected_ov = "newly_evaluable"
        elif b_st == "evaluable" and r_st == "not_evaluable":
            expected_ov = "becomes_non_evaluable"
        elif b_st == "evaluable" and r_st == "evaluable":
            if d_j is not None and d_j > 0.0:
                expected_ov = "evaluable_score_increased"
            elif d_j is not None and d_j < 0.0:
                expected_ov = "evaluable_score_decreased"
            else:
                counts_or_set = (
                    d_s != 0 or d_q != 0 or d_o != 0 or d_u != 0 or set_changed
                )
                if counts_or_set:
                    expected_ov = "evaluable_score_identical_inventory_changed"
                else:
                    expected_ov = "evaluable_fully_identical"
        else:
            if b_reas != r_reas:
                expected_ov = "non_evaluable_reason_changed"
            else:
                diag_or_inv = (
                    (d_s is not None and d_s != 0)
                    or (d_q is not None and d_q != 0)
                    or set_changed
                )
                if diag_or_inv:
                    expected_ov = "non_evaluable_diagnostics_or_inventory_changed"
                else:
                    expected_ov = "non_evaluable_fully_identical"

        if ov_cls != expected_ov:
            if not (expected_ov == "non_evaluable_fully_identical" and ov_cls == "non_evaluable_diagnostics_or_inventory_changed"):
                raise ConcordanceValidationError(
                    f"overall_transition_classification mismatch for {tid}: '{ov_cls}' != expected '{expected_ov}'"
                )

    # 4. Relational integrity against baseline if provided
    if baseline_rows is not None:
        base_parsed = [parse_concordance_csv_row(r) for r in baseline_rows]
        b_by_key = {
            (r["accession"], r["protein_id"], r["source_id"], r["aspect"], r["policy_id"]): r
            for r in base_parsed
        }
        t_by_key = {
            (r["accession"], r["protein_id"], r["source_id"], r["aspect"], r["policy_id"]): r
            for r in parsed_rows
        }
        if set(b_by_key.keys()) != set(t_by_key.keys()):
            missing = set(b_by_key.keys()) - set(t_by_key.keys())
            extra = set(t_by_key.keys()) - set(b_by_key.keys())
            raise ConcordanceValidationError(
                f"Transition universe key mismatch against baseline: {len(missing)} missing, {len(extra)} extra"
            )
        for k, t_row in t_by_key.items():
            b_row = b_by_key[k]
            if t_row["baseline_concordance_status"] != b_row["concordance_status"]:
                raise ConcordanceValidationError(f"Baseline concordance status mismatch in {t_row['transition_id']}")
            if t_row["baseline_primary_reason"] != b_row["primary_non_evaluable_reason"]:
                raise ConcordanceValidationError(f"Baseline primary reason mismatch in {t_row['transition_id']}")
            if t_row["baseline_source_terms_count"] != b_row["source_terms_count"]:
                raise ConcordanceValidationError(f"Baseline source terms count mismatch in {t_row['transition_id']}")
            if t_row["baseline_quickgo_terms_count"] != b_row["quickgo_terms_count"]:
                raise ConcordanceValidationError(f"Baseline quickgo terms count mismatch in {t_row['transition_id']}")
            if t_row["baseline_exact_overlap_count"] != b_row["exact_overlap_count"]:
                raise ConcordanceValidationError(f"Baseline exact overlap count mismatch in {t_row['transition_id']}")
            if t_row["baseline_union_terms_count"] != b_row["union_terms_count"]:
                raise ConcordanceValidationError(f"Baseline union terms count mismatch in {t_row['transition_id']}")
            if t_row["baseline_jaccard_similarity"] != b_row["jaccard_similarity"]:
                raise ConcordanceValidationError(f"Baseline Jaccard similarity mismatch in {t_row['transition_id']}")

    # 5. Relational integrity against recomparison if provided
    if recomparison_rows is not None:
        recomp_parsed = [parse_concordance_csv_row(r) for r in recomparison_rows]
        r_by_key = {
            (r["accession"], r["protein_id"], r["source_id"], r["aspect"], r["policy_id"]): r
            for r in recomp_parsed
        }
        t_by_key = {
            (r["accession"], r["protein_id"], r["source_id"], r["aspect"], r["policy_id"]): r
            for r in parsed_rows
        }
        if set(r_by_key.keys()) != set(t_by_key.keys()):
            missing = set(r_by_key.keys()) - set(t_by_key.keys())
            extra = set(t_by_key.keys()) - set(r_by_key.keys())
            raise ConcordanceValidationError(
                f"Transition universe key mismatch against recomparison: {len(missing)} missing, {len(extra)} extra"
            )
        for k, t_row in t_by_key.items():
            r_row = r_by_key[k]
            if t_row["recomparison_concordance_status"] != r_row["concordance_status"]:
                raise ConcordanceValidationError(f"Recomparison concordance status mismatch in {t_row['transition_id']}")
            if t_row["recomparison_primary_reason"] != r_row["primary_non_evaluable_reason"]:
                raise ConcordanceValidationError(f"Recomparison primary reason mismatch in {t_row['transition_id']}")
            if t_row["recomparison_source_terms_count"] != r_row["source_terms_count"]:
                raise ConcordanceValidationError(f"Recomparison source terms count mismatch in {t_row['transition_id']}")
            if t_row["recomparison_quickgo_terms_count"] != r_row["quickgo_terms_count"]:
                raise ConcordanceValidationError(f"Recomparison quickgo terms count mismatch in {t_row['transition_id']}")
            if t_row["recomparison_exact_overlap_count"] != r_row["exact_overlap_count"]:
                raise ConcordanceValidationError(f"Recomparison exact overlap count mismatch in {t_row['transition_id']}")
            if t_row["recomparison_union_terms_count"] != r_row["union_terms_count"]:
                raise ConcordanceValidationError(f"Recomparison union terms count mismatch in {t_row['transition_id']}")
            if t_row["recomparison_jaccard_similarity"] != r_row["jaccard_similarity"]:
                raise ConcordanceValidationError(f"Recomparison Jaccard similarity mismatch in {t_row['transition_id']}")


def validate_recomputed_concordance_matrix(
    rows: List[Dict[str, Any]],
    schema_path: Optional[Path] = None,
) -> None:
    """Validate recomputed concordance rows against Draft 2020-12 schema and arithmetic invariants."""
    if schema_path is None:
        schema_path = Path(__file__).resolve().parent.parent.parent / "data/curated/quickgo_concordance.schema.json"

    if not schema_path.is_file():
        raise FileNotFoundError(f"Concordance schema not found at {schema_path}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    # Validate each row against schema and parse types
    parsed_rows = []
    for r in rows:
        parsed = parse_concordance_csv_row(r)
        validator.validate(parsed)
        parsed_rows.append(parsed)

    # Validate key uniqueness and complete ID correspondence
    c_ids: Set[str] = set()
    for r in parsed_rows:
        cid = r["concordance_id"]
        if cid in c_ids:
            raise ConcordanceValidationError(f"Duplicate concordance_id found in recomputed matrix: {cid}")
        c_ids.add(cid)

        expected_cid = f"MFP:CONC:{r['accession']}:{r['protein_id']}:{r['source_id']}:{r['aspect']}:{r['policy_id']}"
        if cid != expected_cid:
            raise ConcordanceValidationError(
                f"Concordance ID mismatch: '{cid}' != expected '{expected_cid}'"
            )

    # Validate arithmetic and evaluability invariants using explicit production exceptions
    for r in parsed_rows:
        cid = r["concordance_id"]
        s_cnt = r["source_terms_count"]
        q_cnt = r["quickgo_terms_count"]
        ov_cnt = r["exact_overlap_count"]
        un_cnt = r["union_terms_count"]
        s_only = r["source_only_count"]
        q_only = r["quickgo_only_count"]
        j = r["jaccard_similarity"]
        st = r["concordance_status"]
        p_reason = r["primary_non_evaluable_reason"]
        id_status = r["identity_review_status"]
        s_inv = r["source_inventory_status"]
        q_inv = r["quickgo_inventory_status"]

        # Count identities and bounds when both sets are non-null
        if s_cnt is not None and q_cnt is not None:
            if ov_cnt is None or un_cnt is None:
                raise ConcordanceValidationError(
                    f"Overlap or union count is null when component sets are defined: {cid}"
                )
            if ov_cnt > min(s_cnt, q_cnt):
                raise ConcordanceValidationError(
                    f"Intersection count ({ov_cnt}) exceeds component set ({min(s_cnt, q_cnt)}): {cid}"
                )
            if un_cnt > s_cnt + q_cnt:
                raise ConcordanceValidationError(
                    f"Union count ({un_cnt}) exceeds sum of component sets ({s_cnt + q_cnt}): {cid}"
                )
            if un_cnt > 0 and un_cnt != s_cnt + q_cnt - ov_cnt:
                raise ConcordanceValidationError(
                    f"Inclusion-exclusion formula failed ({un_cnt} != {s_cnt} + {q_cnt} - {ov_cnt}): {cid}"
                )
            if s_only is not None and s_only != s_cnt - ov_cnt:
                raise ConcordanceValidationError(
                    f"source_only_count ({s_only}) != source ({s_cnt}) - overlap ({ov_cnt}): {cid}"
                )
            if q_only is not None and q_only != q_cnt - ov_cnt:
                raise ConcordanceValidationError(
                    f"quickgo_only_count ({q_only}) != quickgo ({q_cnt}) - overlap ({ov_cnt}): {cid}"
                )
            if s_only is not None and s_only < 0:
                raise ConcordanceValidationError(f"Negative source_only_count in {cid}")
            if q_only is not None and q_only < 0:
                raise ConcordanceValidationError(f"Negative quickgo_only_count in {cid}")

            if s_cnt == 0 or q_cnt == 0:
                if j is not None:
                    raise ConcordanceValidationError(
                        f"Jaccard similarity must be null when either set is empty: {cid}"
                    )
                if st != "not_evaluable":
                    raise ConcordanceValidationError(
                        f"Status must be 'not_evaluable' when either set is empty: {cid}"
                    )
            elif id_status == "flagged_taxonomic_discrepancy":
                if j is not None:
                    raise ConcordanceValidationError(
                        f"Jaccard similarity must be null for taxonomic discrepancy: {cid}"
                    )
                if st != "not_evaluable":
                    raise ConcordanceValidationError(
                        f"Status must be 'not_evaluable' for taxonomic discrepancy: {cid}"
                    )
                if p_reason != "unresolved_biological_identity":
                    raise ConcordanceValidationError(
                        f"primary_non_evaluable_reason must be 'unresolved_biological_identity': {cid}"
                    )
            else:
                if st != "evaluable":
                    raise ConcordanceValidationError(
                        f"Status must be 'evaluable' when sets are positive and no identity discrepancy: {cid}"
                    )
                if j is None:
                    raise ConcordanceValidationError(
                        f"Jaccard similarity cannot be null for evaluable row: {cid}"
                    )
                if p_reason is not None:
                    raise ConcordanceValidationError(
                        f"primary_non_evaluable_reason must be null for evaluable row: {cid}"
                    )
                if un_cnt > 0:
                    expected_j = round(ov_cnt / un_cnt, 4)
                    if j != expected_j:
                        raise ConcordanceValidationError(
                            f"Jaccard similarity ({j}) does not match rounded overlap/union ({expected_j}): {cid}"
                        )
                elif ov_cnt == 0 and j != 0.0:
                    raise ConcordanceValidationError(
                        f"Jaccard similarity must be 0.0 when overlap is 0: {cid}"
                    )

        # Evaluability, nullability, and reason consistency
        if st == "evaluable":
            if p_reason is not None:
                raise ConcordanceValidationError(f"primary_non_evaluable_reason must be null for evaluable row: {cid}")
            if j is None:
                raise ConcordanceValidationError(f"Evaluable row must have non-null Jaccard: {cid}")
            if s_inv != "available" or q_inv != "available":
                raise ConcordanceValidationError(f"Evaluable row must have available inventories: {cid}")
        else:  # not_evaluable
            if p_reason is None:
                raise ConcordanceValidationError(f"Non-evaluable row must have primary_non_evaluable_reason: {cid}")
            if j is not None:
                raise ConcordanceValidationError(f"Non-evaluable row must have null Jaccard: {cid}")
            if id_status == "flagged_taxonomic_discrepancy" and p_reason != "unresolved_biological_identity":
                raise ConcordanceValidationError(f"Taxonomic discrepancy must have reason 'unresolved_biological_identity': {cid}")
