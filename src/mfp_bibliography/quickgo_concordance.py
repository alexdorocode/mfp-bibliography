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
) -> List[Dict[str, Any]]:
    """Build the 72-row Gene Ontology concordance comparison matrix."""
    cov_by_acc = {r["accession"]: r for r in raw_coverage}
    slice_pids = {r["protein_id"] for r in functional_coverage}

    target_pairs = pairs if pairs is not None else VERIFIED_COHORT_PAIRS
    rows: List[Dict[str, Any]] = []

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
            r for r in source_go_annotations
            if r["protein_id"] == protein_id and r["source_id"] == source_id
        ]
        has_any_source_terms = len(s_ann_pair) > 0
        all_source_aspects_undeclared = (
            has_any_source_terms
            and all(not parse_csv_value(r.get("go_aspect")) for r in s_ann_pair)
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
            elif all_source_aspects_undeclared:
                s_status = "indeterminate"
                s_terms_count_B = None
                s_terms_B = set()
                s_aspect_rows = []
            else:
                s_aspect_rows = [
                    r for r in s_ann_pair
                    if parse_csv_value(r.get("go_aspect")) == aspect
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
