"""Unit and regression tests for PIL-04.1B QuickGO Concordance Recomparison & Transition Analysis.

Tier A tests are 100% self-contained with inline synthetic fixtures, zero local pilot
dataset dependencies, and execute fully in memory.
Tier B tests are authored for local frozen baseline regression and require Gate 3 authorization.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema
import pytest

from mfp_bibliography.quickgo_concordance import (
    CONCORDANCE_COLUMNS,
    TRANSITION_COLUMNS,
    ConcordanceValidationError,
    JoinIntegrityError,
    build_concordance_matrix,
    build_concordance_transition_matrix,
    load_candidate_proteins,
    parse_concordance_csv_row,
    parse_transition_csv_row,
    validate_and_join_source_annotations,
    validate_recomputed_concordance_matrix,
    validate_transition_matrix,
)
from scripts.build_quickgo_concordance_recomparison import (
    PilotInputContract,
    compute_file_sha256,
    run_recomparison_pipeline,
)


# ==============================================================================
# INLINE SYNTHETIC FIXTURE GENERATORS
# ==============================================================================

def make_synthetic_source_annotation(
    ann_id: str,
    protein_id: str = "MFP:U:0000000000000001",
    source_id: str = "SRC_MOONPROT",
    source_record_id: str = "REC_1",
    index: int = 0,
    go_id: str = "GO:0001111",
    go_aspect: Any = "BP",
    evidence_raw: Any = "IDA",
) -> Dict[str, Any]:
    return {
        "annotation_id": ann_id,
        "protein_id": protein_id,
        "source_id": source_id,
        "source_record_id": source_record_id,
        "claim_id": None,
        "source_field": "GO",
        "annotation_index": index,
        "raw_annotation_text": f"Raw {ann_id}",
        "go_id": go_id,
        "go_aspect": go_aspect,
        "term_name": "Test Term",
        "evidence_raw": evidence_raw,
        "annotation_status": "parsed",
        "notes": None,
    }


def make_synthetic_derived_aspect(
    ann_id: str,
    protein_id: str = "MFP:U:0000000000000001",
    source_id: str = "SRC_MOONPROT",
    source_record_id: str = "REC_1",
    index: int = 0,
    source_go_id: str = "GO:0001111",
    source_declared_aspect: Any = "BP",
    resolved_go_id: Any = "GO:0001111",
    derived_aspect: Any = "BP",
    mapping_status: str = "resolved_primary",
    replaced_by_go_id: Any = None,
    consider_go_ids: Any = None,
) -> Dict[str, Any]:
    return {
        "annotation_id": ann_id,
        "protein_id": protein_id,
        "source_id": source_id,
        "source_record_id": source_record_id,
        "claim_id": None,
        "annotation_index": index,
        "raw_annotation_text": f"Raw {ann_id}",
        "source_go_id": source_go_id,
        "source_declared_aspect": source_declared_aspect,
        "resolved_go_id": resolved_go_id,
        "derived_aspect": derived_aspect,
        "mapping_status": mapping_status,
        "replaced_by_go_id": replaced_by_go_id,
        "consider_go_ids": consider_go_ids,
        "term_name_resolved": "Resolved Test Term",
        "ontology_version": "releases/2026-01-23",
        "ontology_sha256": "0" * 64,
        "notes": None,
    }


def make_synthetic_concordance_row(
    acc: str = "P12345",
    pid: str = "MFP:U:0000000000000001",
    source_id: str = "SRC_MOONPROT",
    aspect: str = "BP",
    policy_id: str = "captured_inventory_overlap",
    source_status: str = "available",
    quickgo_status: str = "available",
    s_cnt: Any = 2,
    q_cnt: Any = 2,
    ov_cnt: Any = 1,
    un_cnt: Any = 3,
    jaccard: Any = 0.3333,
    status: str = "evaluable",
    primary_reason: Any = None,
    sec_reasons: Any = None,
    identity_status: str = "no_discrepancy_noted",
) -> Dict[str, Any]:
    cid = f"MFP:CONC:{acc}:{pid}:{source_id}:{aspect}:{policy_id}"
    s_only = (s_cnt - ov_cnt) if (s_cnt is not None and ov_cnt is not None) else None
    q_only = (q_cnt - ov_cnt) if (q_cnt is not None and ov_cnt is not None) else None
    return {
        "concordance_id": cid,
        "accession": acc,
        "protein_id": pid,
        "source_id": source_id,
        "aspect": aspect,
        "policy_id": policy_id,
        "source_inventory_status": source_status,
        "quickgo_inventory_status": quickgo_status,
        "source_terms_count": s_cnt,
        "quickgo_terms_count": q_cnt,
        "exact_overlap_count": ov_cnt,
        "union_terms_count": un_cnt,
        "source_only_count": s_only,
        "quickgo_only_count": q_only,
        "jaccard_similarity": jaccard,
        "concordance_status": status,
        "primary_non_evaluable_reason": primary_reason,
        "secondary_non_evaluable_reasons": sec_reasons,
        "identity_review_status": identity_status,
        "nd_matching_rows_count": None,
        "root_matching_rows_count": None,
        "nd_root_overlap_rows_count": None,
        "net_excluded_rows_count": None,
        "terms_lost_after_filtering_count": None,
        "terms_retained_via_other_rows_count": None,
        "unassessed_evidence_rows_count": None,
    }


# ==============================================================================
# TIER A: PORTABLE SYNTHETIC TESTS (IN-MEMORY)
# ==============================================================================

def test_tier_a_join_missing_or_empty_annotation_id():
    """Verify join engine fails fast when annotation_id is missing or empty."""
    s_rows = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001")]
    s_rows[0]["annotation_id"] = ""
    d_rows = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001")]

    with pytest.raises(JoinIntegrityError, match="missing or has empty 'annotation_id'"):
        validate_and_join_source_annotations(s_rows, d_rows)


def test_tier_a_join_duplicate_annotation_id():
    """Verify join engine fails fast on duplicate annotation_id in either dataset."""
    s_rows = [
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"),
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"),
    ]
    d_rows = [
        make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001"),
        make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000002"),
    ]

    with pytest.raises(JoinIntegrityError, match="Duplicate annotation_id in source"):
        validate_and_join_source_annotations(s_rows, d_rows)


def test_tier_a_join_count_mismatch():
    """Verify join engine fails fast when input row counts differ."""
    s_rows = [
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"),
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000002"),
    ]
    d_rows = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001")]

    with pytest.raises(JoinIntegrityError, match="Row count mismatch"):
        validate_and_join_source_annotations(s_rows, d_rows)


def test_tier_a_join_unexpected_id_in_derived():
    """Verify join engine fails fast when derived contains key absent from source."""
    s_rows = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001")]
    d_rows = [make_synthetic_derived_aspect("MFP:SGA:SRC1:9999999999999999")]

    with pytest.raises(JoinIntegrityError, match="Unexpected annotation_id in derived"):
        validate_and_join_source_annotations(s_rows, d_rows)


def test_tier_a_join_contradictory_fields():
    """Verify join engine fails fast when invariant fields conflict across datasets."""
    # 1. protein_id mismatch
    s1 = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", protein_id="MFP:U:0000000000000001")]
    d1 = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", protein_id="MFP:U:9999999999999999")]
    with pytest.raises(JoinIntegrityError, match="Contradictory protein_id"):
        validate_and_join_source_annotations(s1, d1)

    # 2. source_id mismatch
    s2 = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", source_id="SRC_MOONPROT")]
    d2 = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", source_id="SRC_PLANTMP")]
    with pytest.raises(JoinIntegrityError, match="Contradictory source_id"):
        validate_and_join_source_annotations(s2, d2)

    # 3. go_id mismatch
    s3 = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", go_id="GO:0001111")]
    d3 = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", source_go_id="GO:0002222")]
    with pytest.raises(JoinIntegrityError, match="Contradictory go_id vs source_go_id"):
        validate_and_join_source_annotations(s3, d3)

    # 4. aspect mismatch
    s4 = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", go_aspect="BP")]
    d4 = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", source_declared_aspect="MF")]
    with pytest.raises(JoinIntegrityError, match="Contradictory source declared aspect"):
        validate_and_join_source_annotations(s4, d4)


def test_tier_a_join_valid_bijection():
    """Verify valid 1:1 join returns merged dictionaries with verbatim fields preserved."""
    s = [
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", index=0),
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000002", index=1),
    ]
    d = [
        make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", index=0),
        make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000002", index=1),
    ]
    merged = validate_and_join_source_annotations(s, d)
    assert len(merged) == 2
    assert merged[0]["annotation_id"] == "MFP:SGA:SRC1:0000000000000001"
    assert merged[0]["derived_aspect"] == "BP"
    assert merged[1]["annotation_id"] == "MFP:SGA:SRC1:0000000000000002"


def test_tier_a_case_a_obsolete_with_declared_aspect():
    """Case A: Obsolete term with source-declared aspect is retained under declared aspect."""
    s_rows = [
        make_synthetic_source_annotation(
            "MFP:SGA:SRC1:0000000000000001",
            go_aspect="BP",
            go_id="GO:0000001",
        )
    ]
    d_rows = [
        make_synthetic_derived_aspect(
            "MFP:SGA:SRC1:0000000000000001",
            source_declared_aspect="BP",
            source_go_id="GO:0000001",
            resolved_go_id=None,
            derived_aspect=None,
            mapping_status="obsolete_unreplaced",
        )
    ]
    term_sets: Dict[str, Optional[Set[str]]] = {}
    rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=d_rows,
        source_term_sets_out=term_sets,
    )
    bp_b = next(r for r in rows if r["aspect"] == "BP" and r["policy_id"] == "captured_inventory_overlap")
    assert bp_b["source_terms_count"] == 1
    assert bp_b["source_inventory_status"] == "available"
    assert "GO:0000001" in term_sets[bp_b["concordance_id"]]


def test_tier_a_case_b_obsolete_unassigned_aspect_omitted():
    """Case B: Obsolete term with unassigned aspect is omitted from all aspect comparison units."""
    s_rows = [
        make_synthetic_source_annotation(
            "MFP:SGA:SRC1:0000000000000001",
            go_aspect=None,  # missing/unassigned
            go_id="GO:0000001",
        ),
        make_synthetic_source_annotation(
            "MFP:SGA:SRC1:0000000000000002",
            go_aspect="MF",  # valid other annotation
            go_id="GO:0003824",
        ),
    ]
    d_rows = [
        make_synthetic_derived_aspect(
            "MFP:SGA:SRC1:0000000000000001",
            source_declared_aspect=None,
            source_go_id="GO:0000001",
            resolved_go_id=None,
            derived_aspect=None,
            mapping_status="obsolete_unreplaced",
        ),
        make_synthetic_derived_aspect(
            "MFP:SGA:SRC1:0000000000000002",
            source_declared_aspect="MF",
            source_go_id="GO:0003824",
            resolved_go_id="GO:0003824",
            derived_aspect="MF",
            mapping_status="resolved_primary",
        ),
    ]
    term_sets: Dict[str, Optional[Set[str]]] = {}
    rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=d_rows,
        source_term_sets_out=term_sets,
    )
    mf_b = next(r for r in rows if r["aspect"] == "MF" and r["policy_id"] == "captured_inventory_overlap")
    assert mf_b["source_terms_count"] == 1
    assert mf_b["source_inventory_status"] == "available"
    assert "GO:0003824" in term_sets[mf_b["concordance_id"]]

    bp_b = next(r for r in rows if r["aspect"] == "BP" and r["policy_id"] == "captured_inventory_overlap")
    assert bp_b["source_terms_count"] == 0
    assert bp_b["source_inventory_status"] == "empty"
    assert term_sets[bp_b["concordance_id"]] == set()


def test_tier_a_case_c_active_alt_id_verbatim_matching():
    """Case C: Active secondary alt_id retains verbatim source ID during set comparison."""
    s_rows = [
        make_synthetic_source_annotation(
            "MFP:SGA:SRC1:0000000000000001",
            go_aspect=None,
            go_id="GO:0000001",  # secondary alt_id
        )
    ]
    d_rows = [
        make_synthetic_derived_aspect(
            "MFP:SGA:SRC1:0000000000000001",
            source_declared_aspect=None,
            source_go_id="GO:0000001",
            resolved_go_id="GO:0000002",  # primary ID
            derived_aspect="CC",
            mapping_status="resolved_secondary_alt_id",
        )
    ]
    term_sets: Dict[str, Optional[Set[str]]] = {}
    rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=d_rows,
        source_term_sets_out=term_sets,
    )
    cc_b = next(r for r in rows if r["aspect"] == "CC" and r["policy_id"] == "captured_inventory_overlap")
    assert cc_b["source_terms_count"] == 1
    assert "GO:0000001" in term_sets[cc_b["concordance_id"]]
    assert "GO:0000002" not in term_sets[cc_b["concordance_id"]]


def test_tier_a_case_d_unknown_malformed_terms():
    """Case D: Unknown or malformed GO IDs."""
    s_rows = [
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", go_aspect="MF", go_id="GO:9999999"),
        make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000002", go_aspect=None, go_id="GO:8888888"),
    ]
    d_rows = [
        make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", source_declared_aspect="MF", source_go_id="GO:9999999", resolved_go_id=None, derived_aspect=None, mapping_status="unresolved_unknown_id"),
        make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000002", source_declared_aspect=None, source_go_id="GO:8888888", resolved_go_id=None, derived_aspect=None, mapping_status="unresolved_unknown_id"),
    ]
    term_sets: Dict[str, Optional[Set[str]]] = {}
    rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=d_rows,
        source_term_sets_out=term_sets,
    )
    mf_b = next(r for r in rows if r["aspect"] == "MF" and r["policy_id"] == "captured_inventory_overlap")
    assert mf_b["source_terms_count"] == 1
    assert "GO:9999999" in term_sets[mf_b["concordance_id"]]

    bp_b = next(r for r in rows if r["aspect"] == "BP" and r["policy_id"] == "captured_inventory_overlap")
    assert bp_b["source_terms_count"] == 0
    assert bp_b["source_inventory_status"] == "empty"
    assert term_sets[bp_b["concordance_id"]] == set()


def test_tier_a_conflict_quarantine_both_aspects():
    """Verify aspect conflict quarantines row and marks both declared and derived units indeterminate."""
    s_rows = [
        make_synthetic_source_annotation(
            "MFP:SGA:SRC1:0000000000000001",
            go_aspect="BP",
            go_id="GO:0003824",
        )
    ]
    d_rows = [
        make_synthetic_derived_aspect(
            "MFP:SGA:SRC1:0000000000000001",
            source_declared_aspect="BP",
            source_go_id="GO:0003824",
            resolved_go_id="GO:0003824",
            derived_aspect="MF",
            mapping_status="conflict_source_ontology_aspect_mismatch",
        )
    ]
    term_sets: Dict[str, Optional[Set[str]]] = {}
    rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=d_rows,
        source_term_sets_out=term_sets,
    )

    bp_b = next(r for r in rows if r["aspect"] == "BP" and r["policy_id"] == "captured_inventory_overlap")
    mf_b = next(r for r in rows if r["aspect"] == "MF" and r["policy_id"] == "captured_inventory_overlap")
    cc_b = next(r for r in rows if r["aspect"] == "CC" and r["policy_id"] == "captured_inventory_overlap")

    assert bp_b["source_inventory_status"] == "indeterminate"
    assert bp_b["concordance_status"] == "not_evaluable"
    assert bp_b["primary_non_evaluable_reason"] == "source_aspect_indeterminate"
    assert "source_aspect_conflict" in (bp_b["secondary_non_evaluable_reasons"] or "")
    assert term_sets[bp_b["concordance_id"]] is None

    assert mf_b["source_inventory_status"] == "indeterminate"
    assert mf_b["concordance_status"] == "not_evaluable"
    assert mf_b["primary_non_evaluable_reason"] == "source_aspect_indeterminate"
    assert "source_aspect_conflict" in (mf_b["secondary_non_evaluable_reasons"] or "")
    assert term_sets[mf_b["concordance_id"]] is None

    assert cc_b["source_inventory_status"] == "empty"
    assert term_sets[cc_b["concordance_id"]] == set()


def test_tier_a_biological_identity_gate_preserved():
    """Verify flagged taxonomic discrepancy remains not_evaluable even with valid matching terms."""
    s_rows = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", go_aspect="BP", go_id="GO:0001111")]
    d_rows = [make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001", source_declared_aspect="BP", source_go_id="GO:0001111", derived_aspect="BP")]
    q_rows = [{
        "annotation_id": "MFP:EXT:QGO:1",
        "uniprot_accession": "P34788",
        "go_id": "GO:0001111",
        "go_aspect": "BP",
        "evidence_code": "IDA",
    }]
    rows = build_concordance_matrix(
        normalized_annotations=q_rows,
        raw_coverage=[{"accession": "P34788", "quickgo_coverage_status": "annotations_available", "identity_review_status": "flagged_taxonomic_discrepancy"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P34788": "MFP:U:0000000000000001"},
        pairs=[("P34788", "SRC_MOONPROT")],
        derived_aspects_rows=d_rows,
    )
    bp_b = next(r for r in rows if r["aspect"] == "BP" and r["policy_id"] == "captured_inventory_overlap")
    assert bp_b["concordance_status"] == "not_evaluable"
    assert bp_b["jaccard_similarity"] is None
    assert bp_b["primary_non_evaluable_reason"] == "unresolved_biological_identity"


def test_tier_a_legacy_mode_synthetic_inputs():
    """Verify legacy mode reproduces expected counts when derived_aspects_rows is None."""
    s_rows = [make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001", go_aspect="BP", go_id="GO:0001111")]
    term_sets: Dict[str, Optional[Set[str]]] = {}
    rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=s_rows,
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=None,
        source_term_sets_out=term_sets,
    )
    bp_b = next(r for r in rows if r["aspect"] == "BP" and r["policy_id"] == "captured_inventory_overlap")
    assert bp_b["source_terms_count"] == 1
    assert "GO:0001111" in term_sets[bp_b["concordance_id"]]


def test_tier_a_transition_evaluability_categories():
    """Test all 4 evaluability_transition states with coherent fixtures."""
    # 1. remains_evaluable
    b1 = [make_synthetic_concordance_row(status="evaluable")]
    r1 = [make_synthetic_concordance_row(status="evaluable")]
    cid = b1[0]["concordance_id"]
    t1 = build_concordance_transition_matrix(b1, r1, {cid: {"GO:01", "GO:02"}}, {cid: {"GO:01", "GO:02"}})[0]
    assert t1["evaluability_transition"] == "remains_evaluable"

    # 2. newly_evaluable
    b2 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_aspect_indeterminate", jaccard=None, source_status="indeterminate", s_cnt=None, ov_cnt=None, un_cnt=None)]
    r2 = [make_synthetic_concordance_row(status="evaluable", jaccard=0.5, s_cnt=2, q_cnt=2, ov_cnt=1, un_cnt=3)]
    cid2 = b2[0]["concordance_id"]
    t2 = build_concordance_transition_matrix(b2, r2, {cid2: None}, {cid2: {"GO:01", "GO:02"}})[0]
    assert t2["evaluability_transition"] == "newly_evaluable"

    # 3. becomes_non_evaluable
    b3 = [make_synthetic_concordance_row(status="evaluable", jaccard=0.5, s_cnt=2, q_cnt=2, ov_cnt=1, un_cnt=3)]
    r3 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="empty_after_filtering", jaccard=None, quickgo_status="empty", q_cnt=0, ov_cnt=0, un_cnt=2)]
    cid3 = b3[0]["concordance_id"]
    t3 = build_concordance_transition_matrix(b3, r3, {cid3: {"GO:01", "GO:02"}}, {cid3: {"GO:01", "GO:02"}})[0]
    assert t3["evaluability_transition"] == "becomes_non_evaluable"

    # 4. remains_non_evaluable
    b4 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", jaccard=None, source_status="empty", s_cnt=0, ov_cnt=0, un_cnt=2)]
    r4 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", jaccard=None, source_status="empty", s_cnt=0, ov_cnt=0, un_cnt=2)]
    cid4 = b4[0]["concordance_id"]
    t4 = build_concordance_transition_matrix(b4, r4, {cid4: set()}, {cid4: set()})[0]
    assert t4["evaluability_transition"] == "remains_non_evaluable"


def test_tier_a_transition_primary_reason_categories():
    """Test all 5 primary_reason_transition states."""
    # 1. unchanged_null
    b1 = [make_synthetic_concordance_row(status="evaluable")]
    r1 = [make_synthetic_concordance_row(status="evaluable")]
    cid = b1[0]["concordance_id"]
    assert build_concordance_transition_matrix(b1, r1, {cid: {"GO:01"}}, {cid: {"GO:01"}})[0]["primary_reason_transition"] == "unchanged_null"

    # 2. became_evaluable
    b2 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_aspect_indeterminate", jaccard=None, source_status="indeterminate", s_cnt=None)]
    r2 = [make_synthetic_concordance_row(status="evaluable", jaccard=0.5)]
    cid2 = b2[0]["concordance_id"]
    assert build_concordance_transition_matrix(b2, r2, {cid2: None}, {cid2: {"GO:01"}})[0]["primary_reason_transition"] == "became_evaluable"

    # 3. became_non_evaluable
    b3 = [make_synthetic_concordance_row(status="evaluable", jaccard=0.5)]
    r3 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="empty_after_filtering", jaccard=None, quickgo_status="empty", q_cnt=0)]
    cid3 = b3[0]["concordance_id"]
    assert build_concordance_transition_matrix(b3, r3, {cid3: {"GO:01"}}, {cid3: {"GO:01"}})[0]["primary_reason_transition"] == "became_non_evaluable"

    # 4. unchanged_reason
    b4 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", jaccard=None, source_status="empty", s_cnt=0)]
    r4 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", jaccard=None, source_status="empty", s_cnt=0)]
    cid4 = b4[0]["concordance_id"]
    assert build_concordance_transition_matrix(b4, r4, {cid4: set()}, {cid4: set()})[0]["primary_reason_transition"] == "unchanged_reason"

    # 5. reason_changed
    b5 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_aspect_indeterminate", jaccard=None, source_status="indeterminate", s_cnt=None)]
    r5 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", jaccard=None, source_status="empty", s_cnt=0)]
    cid5 = b5[0]["concordance_id"]
    assert build_concordance_transition_matrix(b5, r5, {cid5: None}, {cid5: set()})[0]["primary_reason_transition"] == "reason_changed"


def test_tier_a_transition_metric_categories_and_precision():
    """Test all 6 metric_transition categories and 4-decimal precision delta."""
    cid = make_synthetic_concordance_row()["concordance_id"]
    sets = {cid: {"GO:01"}}

    # score_identical
    b = [make_synthetic_concordance_row(jaccard=0.3333)]
    r = [make_synthetic_concordance_row(jaccard=0.3333)]
    t = build_concordance_transition_matrix(b, r, sets, sets)[0]
    assert t["metric_transition"] == "score_identical"
    assert t["delta_jaccard_similarity"] == 0.0

    # score_increased: 0.5 - 0.3333 = 0.1667
    r_inc = [make_synthetic_concordance_row(jaccard=0.5)]
    t_inc = build_concordance_transition_matrix(b, r_inc, sets, sets)[0]
    assert t_inc["metric_transition"] == "score_increased"
    assert t_inc["delta_jaccard_similarity"] == 0.1667

    # score_decreased: 0.2 - 0.3333 = -0.1333
    r_dec = [make_synthetic_concordance_row(jaccard=0.2)]
    t_dec = build_concordance_transition_matrix(b, r_dec, sets, sets)[0]
    assert t_dec["metric_transition"] == "score_decreased"
    assert t_dec["delta_jaccard_similarity"] == -0.1333

    # score_newly_defined
    b_null = [make_synthetic_concordance_row(status="not_evaluable", jaccard=None, source_status="indeterminate", primary_reason="source_aspect_indeterminate", s_cnt=None)]
    t_new = build_concordance_transition_matrix(b_null, r, {cid: None}, sets)[0]
    assert t_new["metric_transition"] == "score_newly_defined"
    assert t_new["delta_jaccard_similarity"] is None

    # score_became_null
    r_null = [make_synthetic_concordance_row(status="not_evaluable", jaccard=None, source_status="indeterminate", primary_reason="source_aspect_indeterminate", s_cnt=None)]
    t_null = build_concordance_transition_matrix(b, r_null, sets, {cid: None})[0]
    assert t_null["metric_transition"] == "score_became_null"
    assert t_null["delta_jaccard_similarity"] is None

    # remains_null
    t_rem = build_concordance_transition_matrix(b_null, r_null, {cid: None}, {cid: None})[0]
    assert t_rem["metric_transition"] == "remains_null"
    assert t_rem["delta_jaccard_similarity"] is None


def test_tier_a_transition_set_content_changed_with_equal_counts_and_scores():
    """Verify that term set differences are detected even when counts and Jaccard scores match."""
    b = [make_synthetic_concordance_row(s_cnt=2, jaccard=0.5)]
    r = [make_synthetic_concordance_row(s_cnt=2, jaccard=0.5)]
    cid = b[0]["concordance_id"]

    b_sets = {cid: {"GO:0001", "GO:0002"}}
    r_sets = {cid: {"GO:0001", "GO:0003"}}  # Same count (2), but different content

    t = build_concordance_transition_matrix(
        baseline_concordance_rows=b,
        recomparison_concordance_rows=r,
        baseline_source_sets=b_sets,
        recomparison_source_sets=r_sets,
    )[0]

    assert t["source_set_content_changed"] is True
    assert t["overall_transition_classification"] == "evaluable_score_identical_inventory_changed"


def test_tier_a_transition_missing_source_set_maps_or_keys():
    """Verify that missing source-set maps or missing keys for comparable units raise ConcordanceValidationError."""
    b = [make_synthetic_concordance_row(s_cnt=2, source_status="available")]
    r = [make_synthetic_concordance_row(s_cnt=2, source_status="available")]
    cid = b[0]["concordance_id"]

    # 1. Missing map entirely
    with pytest.raises(ConcordanceValidationError, match="Missing required source-set maps"):
        build_concordance_transition_matrix(b, r, baseline_source_sets=None, recomparison_source_sets=None)

    # 2. Key missing in baseline map
    with pytest.raises(ConcordanceValidationError, match="Missing required comparison key"):
        build_concordance_transition_matrix(b, r, baseline_source_sets={}, recomparison_source_sets={cid: set()})

    # 3. Value is None for comparable inventory
    with pytest.raises(ConcordanceValidationError, match="Source-set is None for comparable inventory"):
        build_concordance_transition_matrix(b, r, baseline_source_sets={cid: None}, recomparison_source_sets={cid: set()})


def test_tier_a_transition_non_comparable_operational_convention():
    """Verify operational convention for non-comparable inventories."""
    # Both indeterminate -> convention false, explanatory note
    b = [make_synthetic_concordance_row(status="not_evaluable", source_status="indeterminate", primary_reason="source_aspect_indeterminate", s_cnt=None, jaccard=None)]
    r = [make_synthetic_concordance_row(status="not_evaluable", source_status="indeterminate", primary_reason="source_aspect_indeterminate", s_cnt=None, jaccard=None)]
    cid = b[0]["concordance_id"]

    t = build_concordance_transition_matrix(b, r, {cid: None}, {cid: None})[0]
    assert t["source_set_content_changed"] is False
    assert "operational convention applied" in (t["notes"] or "")

    # Status shifted from outside_slice to indeterminate -> changed True
    r2 = [make_synthetic_concordance_row(status="not_evaluable", source_status="outside_slice", primary_reason="source_record_outside_slice", s_cnt=None, jaccard=None)]
    t2 = build_concordance_transition_matrix(b, r2, {cid: None}, {cid: None})[0]
    assert t2["source_set_content_changed"] is True


def test_tier_a_transition_overall_precedence_all_nine_states():
    """Verify all 9 overall_transition_classification states according to strict precedence."""
    cid = make_synthetic_concordance_row()["concordance_id"]
    sets = {cid: {"GO:01"}}

    # 1. newly_evaluable
    b1 = [make_synthetic_concordance_row(status="not_evaluable", source_status="indeterminate", primary_reason="source_aspect_indeterminate", s_cnt=None, jaccard=None)]
    r1 = [make_synthetic_concordance_row(status="evaluable", jaccard=0.5)]
    assert build_concordance_transition_matrix(b1, r1, {cid: None}, sets)[0]["overall_transition_classification"] == "newly_evaluable"

    # 2. becomes_non_evaluable
    assert build_concordance_transition_matrix(r1, b1, sets, {cid: None})[0]["overall_transition_classification"] == "becomes_non_evaluable"

    # 3. evaluable_score_increased
    b3 = [make_synthetic_concordance_row(jaccard=0.2)]
    r3 = [make_synthetic_concordance_row(jaccard=0.4)]
    assert build_concordance_transition_matrix(b3, r3, sets, sets)[0]["overall_transition_classification"] == "evaluable_score_increased"

    # 4. evaluable_score_decreased
    assert build_concordance_transition_matrix(r3, b3, sets, sets)[0]["overall_transition_classification"] == "evaluable_score_decreased"

    # 5. evaluable_score_identical_inventory_changed
    b5 = [make_synthetic_concordance_row(jaccard=0.5, s_cnt=2)]
    r5 = [make_synthetic_concordance_row(jaccard=0.5, s_cnt=2)]
    assert build_concordance_transition_matrix(b5, r5, {cid: {"GO:01", "GO:02"}}, {cid: {"GO:01", "GO:03"}})[0]["overall_transition_classification"] == "evaluable_score_identical_inventory_changed"

    # 6. evaluable_fully_identical
    assert build_concordance_transition_matrix(b5, r5, {cid: {"GO:01", "GO:02"}}, {cid: {"GO:01", "GO:02"}})[0]["overall_transition_classification"] == "evaluable_fully_identical"

    # 7. non_evaluable_reason_changed
    b7 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_aspect_indeterminate", source_status="indeterminate", s_cnt=None, jaccard=None)]
    r7 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", source_status="empty", s_cnt=0, jaccard=None)]
    assert build_concordance_transition_matrix(b7, r7, {cid: None}, {cid: set()})[0]["overall_transition_classification"] == "non_evaluable_reason_changed"

    # 8. non_evaluable_diagnostics_or_inventory_changed
    b8 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", source_status="empty", s_cnt=0, q_cnt=2, jaccard=None)]
    r8 = [make_synthetic_concordance_row(status="not_evaluable", primary_reason="source_record_no_terms_aspect", source_status="empty", s_cnt=0, q_cnt=5, jaccard=None)]
    assert build_concordance_transition_matrix(b8, r8, {cid: set()}, {cid: set()})[0]["overall_transition_classification"] == "non_evaluable_diagnostics_or_inventory_changed"

    # 9. non_evaluable_fully_identical
    assert build_concordance_transition_matrix(b8, b8, {cid: set()}, {cid: set()})[0]["overall_transition_classification"] == "non_evaluable_fully_identical"


def test_tier_a_transition_duplicate_keys_rejected():
    """Verify duplicate comparison keys on baseline or recomparison are rejected before dict construction."""
    row1 = make_synthetic_concordance_row()
    row2 = make_synthetic_concordance_row()

    # Duplicate in baseline
    with pytest.raises(ConcordanceValidationError, match="Duplicate comparison key in baseline"):
        build_concordance_transition_matrix([row1, row2], [row1])

    # Duplicate in recomparison
    with pytest.raises(ConcordanceValidationError, match="Duplicate comparison key in recomparison"):
        build_concordance_transition_matrix([row1], [row1, row2])


def test_tier_a_transition_id_and_concordance_id_mismatch_rejected():
    """Verify that concordance_id and transition_id mismatches against component keys are rejected."""
    r = make_synthetic_concordance_row()
    r["concordance_id"] = "MFP:CONC:WRONG:ID"
    with pytest.raises(ConcordanceValidationError, match="Concordance ID mismatch in baseline"):
        build_concordance_transition_matrix([r], [r])


def test_tier_a_transition_malformed_boolean_rejected():
    """Verify malformed boolean token in CSV is rejected rather than silently coerced to false."""
    row = {
        "transition_id": "MFP:TRNS:P12345:MFP:U:0000000000000001:SRC_MOONPROT:BP:captured_inventory_overlap",
        "accession": "P12345",
        "protein_id": "MFP:U:0000000000000001",
        "source_id": "SRC_MOONPROT",
        "aspect": "BP",
        "policy_id": "captured_inventory_overlap",
        "source_set_content_changed": "not_a_valid_bool",
    }
    with pytest.raises(ConcordanceValidationError, match="Malformed CSV boolean value"):
        parse_transition_csv_row(row)


def test_tier_a_transition_unexpected_properties_rejected():
    """Verify additional unexpected fields are preserved during parsing and rejected by schema."""
    b = [make_synthetic_concordance_row()]
    cid = b[0]["concordance_id"]
    t_rows = build_concordance_transition_matrix(b, b, {cid: {"GO:01"}}, {cid: {"GO:01"}})
    t_rows[0]["unexpected_rogue_property"] = "malicious_payload"

    with pytest.raises(jsonschema.ValidationError, match="Additional properties are not allowed"):
        validate_transition_matrix(t_rows)


def test_tier_a_transition_programmatic_validator_arithmetic_errors():
    """Verify validate_transition_matrix rejects arithmetic discrepancies using explicit exceptions."""
    b = [make_synthetic_concordance_row(s_cnt=3, jaccard=0.5)]
    r = [make_synthetic_concordance_row(s_cnt=5, jaccard=0.5)]
    cid = b[0]["concordance_id"]
    t_rows = build_concordance_transition_matrix(b, r, {cid: {"GO:01", "GO:02", "GO:03"}}, {cid: {"GO:01", "GO:02", "GO:03", "GO:04", "GO:05"}})

    # Valid matrix passes
    validate_transition_matrix(t_rows, baseline_rows=b, recomparison_rows=r)

    # Tamper with count delta
    t_rows[0]["delta_source_terms_count"] = 99
    with pytest.raises(ConcordanceValidationError, match="Arithmetic delta error in delta_source_terms_count"):
        validate_transition_matrix(t_rows, baseline_rows=b)
    t_rows[0]["delta_source_terms_count"] = 2

    # Tamper with Jaccard delta
    t_rows[0]["delta_jaccard_similarity"] = 0.5
    with pytest.raises(ConcordanceValidationError, match="Arithmetic delta error in delta_jaccard_similarity"):
        validate_transition_matrix(t_rows, baseline_rows=b)


def test_tier_a_transition_relational_integrity_against_underlying_matrices():
    """Verify relational checks against underlying baseline and recomparison matrices."""
    b = [make_synthetic_concordance_row(s_cnt=3, jaccard=0.5)]
    r = [make_synthetic_concordance_row(s_cnt=5, jaccard=0.5)]
    cid = b[0]["concordance_id"]
    t_rows = build_concordance_transition_matrix(b, r, {cid: {"GO:01"}}, {cid: {"GO:01"}})

    # Pass underlying matrices: valid
    validate_transition_matrix(t_rows, baseline_rows=b, recomparison_rows=r)

    # Corrupt baseline Jaccard
    corrupt_b = [dict(b[0])]
    corrupt_b[0]["jaccard_similarity"] = 0.9999
    with pytest.raises(ConcordanceValidationError, match="Baseline Jaccard similarity mismatch"):
        validate_transition_matrix(t_rows, baseline_rows=corrupt_b)

    # Corrupt recomparison status
    corrupt_r = [dict(r[0])]
    corrupt_r[0]["concordance_status"] = "not_evaluable"
    with pytest.raises(ConcordanceValidationError, match="Recomparison concordance status mismatch"):
        validate_transition_matrix(t_rows, recomparison_rows=corrupt_r)


def test_tier_a_concordance_validator_count_identities_and_reason_consistency():
    """Verify programmatic validator for recomputed concordance matrix."""
    row = make_synthetic_concordance_row(s_cnt=3, q_cnt=4, ov_cnt=2, un_cnt=5, jaccard=0.4000)
    # Valid row passes
    validate_recomputed_concordance_matrix([row])

    # 1. Inclusion-exclusion failure: un_cnt != 3 + 4 - 2 = 5
    bad_un = dict(row)
    bad_un["union_terms_count"] = 6
    with pytest.raises(ConcordanceValidationError, match="Inclusion-exclusion formula failed"):
        validate_recomputed_concordance_matrix([bad_un])

    # 2. Intersection exceeds component set
    bad_ov = dict(row)
    bad_ov["exact_overlap_count"] = 5
    with pytest.raises(ConcordanceValidationError, match="Intersection count .* exceeds"):
        validate_recomputed_concordance_matrix([bad_ov])

    # 3. Evaluable row with primary reason
    bad_reas = dict(row)
    bad_reas["primary_non_evaluable_reason"] = "source_aspect_indeterminate"
    with pytest.raises(ConcordanceValidationError, match="primary_non_evaluable_reason must be null for evaluable row"):
        validate_recomputed_concordance_matrix([bad_reas])

    # 4. Taxonomic discrepancy marked evaluable
    bad_tax = dict(row)
    bad_tax["identity_review_status"] = "flagged_taxonomic_discrepancy"
    with pytest.raises(ConcordanceValidationError, match="Jaccard similarity must be null for taxonomic discrepancy"):
        validate_recomputed_concordance_matrix([bad_tax])


def test_tier_a_concordance_validator_unexpected_properties_rejected():
    """Verify unexpected fields are rejected by concordance schema."""
    row = make_synthetic_concordance_row()
    row["extra_field_not_in_schema"] = "disallowed"
    with pytest.raises(jsonschema.ValidationError, match="Additional properties are not allowed"):
        validate_recomputed_concordance_matrix([row])


def test_tier_a_runner_frozen_digest_cardinality_and_universe_rejection(tmp_path: Path):
    """Verify runner rejects wrong digests, wrong cardinality, wrong universe, and empty pairs."""
    base_dir = tmp_path / "inputs"
    base_dir.mkdir()

    # Setup valid minimal files
    s_ann = base_dir / "source_go_annotations.csv"
    with open(s_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"))

    d_asp = base_dir / "derived_aspects.csv"
    with open(d_asp, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001"))

    norm_ann = base_dir / "norm_annotations.csv"
    with open(norm_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["annotation_id", "uniprot_accession", "go_id", "go_aspect", "evidence_code"], lineterminator="\n")
        writer.writeheader()

    raw_cov = base_dir / "raw_coverage.csv"
    with open(raw_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["accession", "quickgo_coverage_status", "identity_review_status"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"})

    func_cov = base_dir / "func_coverage.csv"
    with open(func_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"protein_id": "MFP:U:0000000000000001"})

    cat_prot = base_dir / "catalog_proteins.csv"
    with open(cat_prot, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["canonical_uniprot_accession", "protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"canonical_uniprot_accession": "P12345", "protein_id": "MFP:U:0000000000000001"})

    base_conc = base_dir / "base_concordance.csv"
    mock_base_rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=[make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001")],
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=None,
    )
    with open(base_conc, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONCORDANCE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for r in mock_base_rows:
            writer.writerow({k: ("" if r.get(k) is None else str(r[k])) for k in CONCORDANCE_COLUMNS})

    repo_root = Path(__file__).resolve().parents[1]
    conc_schema = repo_root / "data/curated/quickgo_concordance.schema.json"
    trans_schema = repo_root / "data/curated/quickgo_concordance_transition.schema.json"

    # 1. Wrong Digest Failure
    contract_wrong_digest = PilotInputContract(
        expected_digests={"source_annotations": "0" * 64},
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(mock_base_rows),
        enforce_upstream_manifest_verification=False,
    )
    with pytest.raises(ConcordanceValidationError, match="Cryptographic hash mismatch"):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=tmp_path / "out1",
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=contract_wrong_digest,
        )

    # 2. Wrong Cardinality Failure
    contract_wrong_card = PilotInputContract(
        expected_source_cardinality=999,
        expected_derived_cardinality=1,
        expected_universe_count=len(mock_base_rows),
        enforce_upstream_manifest_verification=False,
    )
    with pytest.raises(ConcordanceValidationError, match="Source annotations row count 1 != expected 999"):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=tmp_path / "out2",
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=contract_wrong_card,
        )

    # 3. Wrong Universe Failure
    contract_wrong_universe = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(mock_base_rows),
        expected_canonical_pairs=[("WRONG_ACC", "WRONG_SRC")],
        enforce_upstream_manifest_verification=False,
    )
    with pytest.raises(ConcordanceValidationError, match="Comparison universe pairs do not match canonical contract"):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=tmp_path / "out3",
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=contract_wrong_universe,
        )


def test_tier_a_runner_protections_staging_cleanup_and_reload_validation(tmp_path: Path):
    """Test CLI runner behavior: refusal on existing destination, collision protection, and staging cleanup."""
    base_dir = tmp_path / "inputs"
    base_dir.mkdir()

    s_ann = base_dir / "source_go_annotations.csv"
    with open(s_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"))

    d_asp = base_dir / "derived_aspects.csv"
    with open(d_asp, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001"))

    norm_ann = base_dir / "norm_annotations.csv"
    with open(norm_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["annotation_id", "uniprot_accession", "go_id", "go_aspect", "evidence_code"], lineterminator="\n")
        writer.writeheader()

    raw_cov = base_dir / "raw_coverage.csv"
    with open(raw_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["accession", "quickgo_coverage_status", "identity_review_status"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"})

    func_cov = base_dir / "func_coverage.csv"
    with open(func_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"protein_id": "MFP:U:0000000000000001"})

    cat_prot = base_dir / "catalog_proteins.csv"
    with open(cat_prot, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["canonical_uniprot_accession", "protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"canonical_uniprot_accession": "P12345", "protein_id": "MFP:U:0000000000000001"})

    base_conc = base_dir / "base_concordance.csv"
    mock_base_rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=[make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001")],
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=None,
    )
    with open(base_conc, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONCORDANCE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for r in mock_base_rows:
            writer.writerow({k: ("" if r.get(k) is None else str(r[k])) for k in CONCORDANCE_COLUMNS})

    repo_root = Path(__file__).resolve().parents[1]
    conc_schema = repo_root / "data/curated/quickgo_concordance.schema.json"
    trans_schema = repo_root / "data/curated/quickgo_concordance_transition.schema.json"

    # Synthetic lineage in tmp_path (independent of repo pilot manifests)
    mock_p3_man = tmp_path / "mock_p3_manifest.json"
    mock_p3_man.write_text(json.dumps({
        "output_inventory": {
            "quickgo_concordance_pilot.csv": {"sha256": compute_file_sha256(base_conc)}
        }
    }), encoding="utf-8")

    mock_pil_man = tmp_path / "mock_pil041a_manifest.json"
    mock_pil_man.write_text(json.dumps({
        "outputs": {
            "derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(d_asp)}
        },
        "summary": {
            "ontology_version": "releases/2026-01-23",
            "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391",
        }
    }), encoding="utf-8")

    synthetic_contract = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(mock_base_rows),
        expected_upstream_manifest_digests={
            "stage_p3_manifest_sha256": compute_file_sha256(mock_p3_man),
            "pil041a_manifest_sha256": compute_file_sha256(mock_pil_man),
        },
        p3_manifest_path=mock_p3_man,
        pil041a_manifest_path=mock_pil_man,
        enforce_upstream_manifest_verification=True,
    )

    out_dir = tmp_path / "synthetic_output"

    # Test 1: Successful execution to non-existent directory
    manifest = run_recomparison_pipeline(
        baseline_concordance_path=base_conc,
        normalized_annotations_path=norm_ann,
        raw_coverage_path=raw_cov,
        source_annotations_path=s_ann,
        derived_aspects_path=d_asp,
        functional_coverage_path=func_cov,
        catalog_proteins_path=cat_prot,
        output_dir=out_dir,
        concordance_schema_path=conc_schema,
        transition_schema_path=trans_schema,
        contract=synthetic_contract,
    )
    assert out_dir.is_dir()
    assert (out_dir / "quickgo_concordance_pilot_recomputed.csv").is_file()
    assert (out_dir / "quickgo_concordance_transition_pilot.csv").is_file()
    assert (out_dir / "manifest.json").is_file()
    assert manifest["upstream_lineage_manifests"]["pinned_ontology_data_version"] == "releases/2026-01-23"

    # Test 2: Refusal when output_dir already exists
    with pytest.raises(FileExistsError, match="Refusing to execute: initial pilot execution requires a non-existent destination"):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=out_dir,
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=synthetic_contract,
        )

    # Test 3: Destination collision with input file
    with pytest.raises(ValueError, match="collides with protected path"):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=base_conc,
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=synthetic_contract,
        )

    # Test 4: Failure before publication cleans up staging and touches nothing
    fail_dir = tmp_path / "failed_output"
    sentinel_file = tmp_path / "sentinel.txt"
    sentinel_file.write_text("sentinel_data", encoding="utf-8")
    sentinel_dir = tmp_path / "unrelated_dir"
    sentinel_dir.mkdir()
    (sentinel_dir / "keep.txt").write_text("keep_data", encoding="utf-8")

    # Create invalid derived aspect that causes join failure
    bad_d_asp = base_dir / "bad_derived_aspects.csv"
    with open(bad_d_asp, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_derived_aspect("MFP:SGA:SRC1:WRONG").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_derived_aspect("MFP:SGA:SRC1:WRONG"))

    with pytest.raises(JoinIntegrityError):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=bad_d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=fail_dir,
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=synthetic_contract,
        )
    assert not fail_dir.exists()
    # Ensure no staging directory leaked in parent
    staging_leaks = list(tmp_path.glob(".staging_recomparison_*"))
    assert len(staging_leaks) == 0
    # Ensure unrelated sentinel files and directories are completely untouched
    assert sentinel_file.read_text(encoding="utf-8") == "sentinel_data"
    assert (sentinel_dir / "keep.txt").read_text(encoding="utf-8") == "keep_data"


@pytest.mark.parametrize("corrupt_target", [
    "recomputed_concordance",
    "transition_matrix",
])
def test_tier_a_runner_staged_csv_corruption_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corrupt_target: str
):
    """Verify that corrupting staged CSV files before read-back validation causes pipeline rejection.

    Ensures:
      - The runner rejects the staged artifact (ConcordanceValidationError).
      - No final output directory is published.
      - The run-unique staging directory is cleaned up.
      - Unrelated sentinel files and sibling directories remain completely intact.
    """
    from scripts import build_quickgo_concordance_recomparison as runner_module

    base_dir = tmp_path / "inputs"
    base_dir.mkdir()

    s_ann = base_dir / "source_go_annotations.csv"
    with open(s_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"))

    d_asp = base_dir / "derived_aspects.csv"
    with open(d_asp, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001"))

    norm_ann = base_dir / "norm_annotations.csv"
    with open(norm_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["annotation_id", "uniprot_accession", "go_id", "go_aspect", "evidence_code"], lineterminator="\n")
        writer.writeheader()

    raw_cov = base_dir / "raw_coverage.csv"
    with open(raw_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["accession", "quickgo_coverage_status", "identity_review_status"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"})

    func_cov = base_dir / "func_coverage.csv"
    with open(func_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"protein_id": "MFP:U:0000000000000001"})

    cat_prot = base_dir / "catalog_proteins.csv"
    with open(cat_prot, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["canonical_uniprot_accession", "protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"canonical_uniprot_accession": "P12345", "protein_id": "MFP:U:0000000000000001"})

    base_conc = base_dir / "base_concordance.csv"
    mock_base_rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=[make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001")],
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=None,
    )
    with open(base_conc, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONCORDANCE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for r in mock_base_rows:
            writer.writerow({k: ("" if r.get(k) is None else str(r[k])) for k in CONCORDANCE_COLUMNS})

    repo_root = Path(__file__).resolve().parents[1]
    conc_schema = repo_root / "data/curated/quickgo_concordance.schema.json"
    trans_schema = repo_root / "data/curated/quickgo_concordance_transition.schema.json"

    mock_p3_man = tmp_path / "mock_p3_manifest.json"
    mock_p3_man.write_text(json.dumps({
        "output_inventory": {
            "quickgo_concordance_pilot.csv": {"sha256": compute_file_sha256(base_conc)}
        }
    }), encoding="utf-8")

    mock_pil_man = tmp_path / "mock_pil041a_manifest.json"
    mock_pil_man.write_text(json.dumps({
        "outputs": {
            "derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(d_asp)}
        },
        "summary": {
            "ontology_version": "releases/2026-01-23",
            "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391",
        }
    }), encoding="utf-8")

    synthetic_contract = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(mock_base_rows),
        expected_upstream_manifest_digests={
            "stage_p3_manifest_sha256": compute_file_sha256(mock_p3_man),
            "pil041a_manifest_sha256": compute_file_sha256(mock_pil_man),
        },
        p3_manifest_path=mock_p3_man,
        pil041a_manifest_path=mock_pil_man,
        enforce_upstream_manifest_verification=True,
    )

    # Setup unrelated sentinel files and directories
    sentinel_file = tmp_path / "sentinel.txt"
    sentinel_file.write_text("sentinel_preserve", encoding="utf-8")
    sentinel_dir = tmp_path / "sentinel_dir"
    sentinel_dir.mkdir()
    (sentinel_dir / "keep.txt").write_text("keep_preserve", encoding="utf-8")

    out_dir = tmp_path / "corrupted_output"

    # Intercept load_csv_rows: corrupt the target file on disk after writing but before validation
    orig_load_csv_rows = runner_module.load_csv_rows

    def corrupting_load_csv_rows(path: Path) -> List[Dict[str, str]]:
        if corrupt_target == "recomputed_concordance" and path.name == "quickgo_concordance_pilot_recomputed.csv":
            # Tamper with union_terms_count to violate inclusion-exclusion formula
            rows = orig_load_csv_rows(path)
            for r in rows:
                r["union_terms_count"] = "999"
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=CONCORDANCE_COLUMNS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        elif corrupt_target == "transition_matrix" and path.name == "quickgo_concordance_transition_pilot.csv":
            # Tamper with delta_source_terms_count to violate arithmetic delta
            rows = orig_load_csv_rows(path)
            for r in rows:
                r["delta_source_terms_count"] = "99"
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=TRANSITION_COLUMNS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        return orig_load_csv_rows(path)

    monkeypatch.setattr(runner_module, "load_csv_rows", corrupting_load_csv_rows)

    with pytest.raises(ConcordanceValidationError):
        run_recomparison_pipeline(
            baseline_concordance_path=base_conc,
            normalized_annotations_path=norm_ann,
            raw_coverage_path=raw_cov,
            source_annotations_path=s_ann,
            derived_aspects_path=d_asp,
            functional_coverage_path=func_cov,
            catalog_proteins_path=cat_prot,
            output_dir=out_dir,
            concordance_schema_path=conc_schema,
            transition_schema_path=trans_schema,
            contract=synthetic_contract,
        )

    # 1. Output directory was NOT published
    assert not out_dir.exists()
    # 2. Staging directory was cleaned up and did not leak
    assert len(list(tmp_path.glob(".staging_recomparison_*"))) == 0
    # 3. Sentinel file and directory were completely untouched
    assert sentinel_file.read_text(encoding="utf-8") == "sentinel_preserve"
    assert (sentinel_dir / "keep.txt").read_text(encoding="utf-8") == "keep_preserve"


def _create_synthetic_runner_fixture(tmp_path: Path) -> Dict[str, Any]:
    """Helper creating minimal coherent synthetic inputs for CLI runner tests."""
    base_dir = tmp_path / "inputs"
    base_dir.mkdir(parents=True, exist_ok=True)

    s_ann = base_dir / "source_go_annotations.csv"
    with open(s_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001"))

    d_asp = base_dir / "derived_aspects.csv"
    with open(d_asp, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001").keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(make_synthetic_derived_aspect("MFP:SGA:SRC1:0000000000000001"))

    norm_ann = base_dir / "norm_annotations.csv"
    with open(norm_ann, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["annotation_id", "uniprot_accession", "go_id", "go_aspect", "evidence_code"], lineterminator="\n")
        writer.writeheader()

    raw_cov = base_dir / "raw_coverage.csv"
    with open(raw_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["accession", "quickgo_coverage_status", "identity_review_status"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"})

    func_cov = base_dir / "func_coverage.csv"
    with open(func_cov, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"protein_id": "MFP:U:0000000000000001"})

    cat_prot = base_dir / "catalog_proteins.csv"
    with open(cat_prot, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["canonical_uniprot_accession", "protein_id"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"canonical_uniprot_accession": "P12345", "protein_id": "MFP:U:0000000000000001"})

    base_conc = base_dir / "base_concordance.csv"
    mock_base_rows = build_concordance_matrix(
        normalized_annotations=[],
        raw_coverage=[{"accession": "P12345", "quickgo_coverage_status": "zero_annotations_found", "identity_review_status": "no_discrepancy_noted"}],
        source_go_annotations=[make_synthetic_source_annotation("MFP:SGA:SRC1:0000000000000001")],
        functional_coverage=[{"protein_id": "MFP:U:0000000000000001"}],
        catalog_map={"P12345": "MFP:U:0000000000000001"},
        pairs=[("P12345", "SRC_MOONPROT")],
        derived_aspects_rows=None,
    )
    with open(base_conc, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONCORDANCE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for r in mock_base_rows:
            writer.writerow({k: ("" if r.get(k) is None else str(r[k])) for k in CONCORDANCE_COLUMNS})

    repo_root = Path(__file__).resolve().parents[1]
    conc_schema = repo_root / "data/curated/quickgo_concordance.schema.json"
    trans_schema = repo_root / "data/curated/quickgo_concordance_transition.schema.json"

    return {
        "base_conc": base_conc,
        "norm_ann": norm_ann,
        "raw_cov": raw_cov,
        "s_ann": s_ann,
        "d_asp": d_asp,
        "func_cov": func_cov,
        "cat_prot": cat_prot,
        "conc_schema": conc_schema,
        "trans_schema": trans_schema,
        "mock_base_rows": mock_base_rows,
    }


def test_tier_a_runner_upstream_manifest_verification_valid(tmp_path: Path):
    """Verify that valid synthetic upstream manifests pass verification and populate lineage."""
    ctx = _create_synthetic_runner_fixture(tmp_path)

    p3_man = tmp_path / "p3_man.json"
    p3_man.write_text(json.dumps({
        "output_inventory": {
            "quickgo_concordance_pilot.csv": {"sha256": compute_file_sha256(ctx["base_conc"])}
        }
    }), encoding="utf-8")

    pil_man = tmp_path / "pil_man.json"
    pil_man.write_text(json.dumps({
        "inputs": {
            "source_go_annotations_pilot.csv": {"sha256": compute_file_sha256(ctx["s_ann"])}
        },
        "outputs": {
            "derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(ctx["d_asp"])}
        },
        "summary": {
            "ontology_version": "releases/2026-01-23",
            "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391",
        }
    }), encoding="utf-8")

    contract = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        expected_upstream_manifest_digests={
            "stage_p3_manifest_sha256": compute_file_sha256(p3_man),
            "pil041a_manifest_sha256": compute_file_sha256(pil_man),
        },
        p3_manifest_path=p3_man,
        pil041a_manifest_path=pil_man,
        enforce_upstream_manifest_verification=True,
    )

    out_dir = tmp_path / "output_valid"
    manifest = run_recomparison_pipeline(
        baseline_concordance_path=ctx["base_conc"],
        normalized_annotations_path=ctx["norm_ann"],
        raw_coverage_path=ctx["raw_cov"],
        source_annotations_path=ctx["s_ann"],
        derived_aspects_path=ctx["d_asp"],
        functional_coverage_path=ctx["func_cov"],
        catalog_proteins_path=ctx["cat_prot"],
        output_dir=out_dir,
        concordance_schema_path=ctx["conc_schema"],
        transition_schema_path=ctx["trans_schema"],
        contract=contract,
    )
    assert out_dir.is_dir()
    assert manifest["upstream_lineage_manifests"]["stage_p3_manifest_sha256"] == compute_file_sha256(p3_man)
    assert manifest["upstream_lineage_manifests"]["pil041a_manifest_sha256"] == compute_file_sha256(pil_man)
    assert manifest["upstream_lineage_manifests"]["pinned_ontology_data_version"] == "releases/2026-01-23"


def test_tier_a_runner_upstream_manifest_wrong_digest(tmp_path: Path):
    """Verify runner rejects upstream manifests whose cryptographic hashes do not match contract."""
    ctx = _create_synthetic_runner_fixture(tmp_path)

    p3_man = tmp_path / "p3_man.json"
    p3_man.write_text(json.dumps({
        "output_inventory": {
            "quickgo_concordance_pilot.csv": {"sha256": compute_file_sha256(ctx["base_conc"])}
        }
    }), encoding="utf-8")

    pil_man = tmp_path / "pil_man.json"
    pil_man.write_text(json.dumps({
        "outputs": {
            "derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(ctx["d_asp"])}
        },
        "summary": {
            "ontology_version": "releases/2026-01-23",
            "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391",
        }
    }), encoding="utf-8")

    # 1. Wrong P3 digest
    contract_bad_p3 = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        expected_upstream_manifest_digests={
            "stage_p3_manifest_sha256": "0" * 64,
            "pil041a_manifest_sha256": compute_file_sha256(pil_man),
        },
        p3_manifest_path=p3_man,
        pil041a_manifest_path=pil_man,
        enforce_upstream_manifest_verification=True,
    )
    with pytest.raises(ConcordanceValidationError, match="Stage P3 upstream manifest cryptographic hash mismatch"):
        run_recomparison_pipeline(
            baseline_concordance_path=ctx["base_conc"],
            normalized_annotations_path=ctx["norm_ann"],
            raw_coverage_path=ctx["raw_cov"],
            source_annotations_path=ctx["s_ann"],
            derived_aspects_path=ctx["d_asp"],
            functional_coverage_path=ctx["func_cov"],
            catalog_proteins_path=ctx["cat_prot"],
            output_dir=tmp_path / "out_bad_p3",
            concordance_schema_path=ctx["conc_schema"],
            transition_schema_path=ctx["trans_schema"],
            contract=contract_bad_p3,
        )

    # 2. Wrong PIL-04.1A digest
    contract_bad_pil = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        expected_upstream_manifest_digests={
            "stage_p3_manifest_sha256": compute_file_sha256(p3_man),
            "pil041a_manifest_sha256": "1" * 64,
        },
        p3_manifest_path=p3_man,
        pil041a_manifest_path=pil_man,
        enforce_upstream_manifest_verification=True,
    )
    with pytest.raises(ConcordanceValidationError, match="PIL-04.1A upstream manifest cryptographic hash mismatch"):
        run_recomparison_pipeline(
            baseline_concordance_path=ctx["base_conc"],
            normalized_annotations_path=ctx["norm_ann"],
            raw_coverage_path=ctx["raw_cov"],
            source_annotations_path=ctx["s_ann"],
            derived_aspects_path=ctx["d_asp"],
            functional_coverage_path=ctx["func_cov"],
            catalog_proteins_path=ctx["cat_prot"],
            output_dir=tmp_path / "out_bad_pil",
            concordance_schema_path=ctx["conc_schema"],
            transition_schema_path=ctx["trans_schema"],
            contract=contract_bad_pil,
        )


def test_tier_a_runner_upstream_manifest_missing_required_fields(tmp_path: Path):
    """Verify runner rejects upstream manifests missing required structural sections or lineage fields."""
    ctx = _create_synthetic_runner_fixture(tmp_path)

    # 1. P3 missing output_inventory
    bad_p3 = tmp_path / "bad_p3.json"
    bad_p3.write_text(json.dumps({"manifest_version": "v1.1"}), encoding="utf-8")

    good_pil = tmp_path / "good_pil.json"
    good_pil.write_text(json.dumps({
        "outputs": {"derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(ctx["d_asp"])}},
        "summary": {"ontology_version": "releases/2026-01-23", "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391"}
    }), encoding="utf-8")

    contract_missing_p3_out = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        p3_manifest_path=bad_p3,
        pil041a_manifest_path=good_pil,
        enforce_upstream_manifest_verification=True,
    )
    with pytest.raises(ConcordanceValidationError, match="Stage P3 manifest missing required 'output_inventory'"):
        run_recomparison_pipeline(
            baseline_concordance_path=ctx["base_conc"],
            normalized_annotations_path=ctx["norm_ann"],
            raw_coverage_path=ctx["raw_cov"],
            source_annotations_path=ctx["s_ann"],
            derived_aspects_path=ctx["d_asp"],
            functional_coverage_path=ctx["func_cov"],
            catalog_proteins_path=ctx["cat_prot"],
            output_dir=tmp_path / "out_mis1",
            concordance_schema_path=ctx["conc_schema"],
            transition_schema_path=ctx["trans_schema"],
            contract=contract_missing_p3_out,
        )

    # 2. PIL-04.1A missing summary / ontology metadata
    good_p3 = tmp_path / "good_p3.json"
    good_p3.write_text(json.dumps({
        "output_inventory": {"quickgo_concordance_pilot.csv": {"sha256": compute_file_sha256(ctx["base_conc"])}}
    }), encoding="utf-8")

    bad_pil_summary = tmp_path / "bad_pil_summary.json"
    bad_pil_summary.write_text(json.dumps({
        "outputs": {"derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(ctx["d_asp"])}},
        "summary": {"ontology_version": ""}
    }), encoding="utf-8")

    contract_missing_ont = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        p3_manifest_path=good_p3,
        pil041a_manifest_path=bad_pil_summary,
        enforce_upstream_manifest_verification=True,
    )
    with pytest.raises(ConcordanceValidationError, match="Missing or empty required lineage field 'ontology_version'"):
        run_recomparison_pipeline(
            baseline_concordance_path=ctx["base_conc"],
            normalized_annotations_path=ctx["norm_ann"],
            raw_coverage_path=ctx["raw_cov"],
            source_annotations_path=ctx["s_ann"],
            derived_aspects_path=ctx["d_asp"],
            functional_coverage_path=ctx["func_cov"],
            catalog_proteins_path=ctx["cat_prot"],
            output_dir=tmp_path / "out_mis2",
            concordance_schema_path=ctx["conc_schema"],
            transition_schema_path=ctx["trans_schema"],
            contract=contract_missing_ont,
        )


def test_tier_a_runner_upstream_manifest_output_relationship_mismatch(tmp_path: Path):
    """Verify runner rejects upstream manifests whose recorded output digests conflict with consumed inputs."""
    ctx = _create_synthetic_runner_fixture(tmp_path)

    good_pil = tmp_path / "good_pil.json"
    good_pil.write_text(json.dumps({
        "outputs": {"derived_source_go_aspects_pilot.csv": {"sha256": compute_file_sha256(ctx["d_asp"])}},
        "summary": {"ontology_version": "releases/2026-01-23", "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391"}
    }), encoding="utf-8")

    # 1. P3 recorded output digest does not match consumed baseline concordance
    bad_p3_mismatch = tmp_path / "bad_p3_mismatch.json"
    bad_p3_mismatch.write_text(json.dumps({
        "output_inventory": {"quickgo_concordance_pilot.csv": {"sha256": "f" * 64}}
    }), encoding="utf-8")

    contract_p3_mismatch = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        p3_manifest_path=bad_p3_mismatch,
        pil041a_manifest_path=good_pil,
        enforce_upstream_manifest_verification=True,
    )
    with pytest.raises(ConcordanceValidationError, match="P3 manifest output digest mismatch for baseline concordance"):
        run_recomparison_pipeline(
            baseline_concordance_path=ctx["base_conc"],
            normalized_annotations_path=ctx["norm_ann"],
            raw_coverage_path=ctx["raw_cov"],
            source_annotations_path=ctx["s_ann"],
            derived_aspects_path=ctx["d_asp"],
            functional_coverage_path=ctx["func_cov"],
            catalog_proteins_path=ctx["cat_prot"],
            output_dir=tmp_path / "out_rel1",
            concordance_schema_path=ctx["conc_schema"],
            transition_schema_path=ctx["trans_schema"],
            contract=contract_p3_mismatch,
        )

    # 2. PIL-04.1A recorded output digest does not match consumed derived aspects
    good_p3 = tmp_path / "good_p3.json"
    good_p3.write_text(json.dumps({
        "output_inventory": {"quickgo_concordance_pilot.csv": {"sha256": compute_file_sha256(ctx["base_conc"])}}
    }), encoding="utf-8")

    bad_pil_mismatch = tmp_path / "bad_pil_mismatch.json"
    bad_pil_mismatch.write_text(json.dumps({
        "outputs": {"derived_source_go_aspects_pilot.csv": {"sha256": "e" * 64}},
        "summary": {"ontology_version": "releases/2026-01-23", "ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391"}
    }), encoding="utf-8")

    contract_pil_mismatch = PilotInputContract(
        expected_source_cardinality=1,
        expected_derived_cardinality=1,
        expected_universe_count=len(ctx["mock_base_rows"]),
        p3_manifest_path=good_p3,
        pil041a_manifest_path=bad_pil_mismatch,
        enforce_upstream_manifest_verification=True,
    )
    with pytest.raises(ConcordanceValidationError, match="PIL-04.1A manifest output digest mismatch for derived aspects"):
        run_recomparison_pipeline(
            baseline_concordance_path=ctx["base_conc"],
            normalized_annotations_path=ctx["norm_ann"],
            raw_coverage_path=ctx["raw_cov"],
            source_annotations_path=ctx["s_ann"],
            derived_aspects_path=ctx["d_asp"],
            functional_coverage_path=ctx["func_cov"],
            catalog_proteins_path=ctx["cat_prot"],
            output_dir=tmp_path / "out_rel2",
            concordance_schema_path=ctx["conc_schema"],
            transition_schema_path=ctx["trans_schema"],
            contract=contract_pil_mismatch,
        )


def test_tier_a_deterministic_serialization(tmp_path: Path):
    """Verify that serialization to CSV produces bit-for-bit bitwise identical SHA-256 digests."""
    b = [make_synthetic_concordance_row(s_cnt=3, jaccard=0.5)]
    r = [make_synthetic_concordance_row(s_cnt=5, jaccard=0.5)]
    cid = b[0]["concordance_id"]
    t_rows = build_concordance_transition_matrix(b, r, {cid: {"GO:01"}}, {cid: {"GO:01"}})

    file1 = tmp_path / "trans1.csv"
    with open(file1, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRANSITION_COLUMNS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writeheader()
        for row in t_rows:
            writer.writerow({k: ("" if row.get(k) is None else ("true" if row[k] is True else ("false" if row[k] is False else (f"{row[k]:.4f}" if isinstance(row[k], float) else str(row[k]))))) for k in TRANSITION_COLUMNS})

    file2 = tmp_path / "trans2.csv"
    with open(file2, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRANSITION_COLUMNS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writeheader()
        for row in t_rows:
            writer.writerow({k: ("" if row.get(k) is None else ("true" if row[k] is True else ("false" if row[k] is False else (f"{row[k]:.4f}" if isinstance(row[k], float) else str(row[k]))))) for k in TRANSITION_COLUMNS})

    h1 = hashlib.sha256(file1.read_bytes()).hexdigest()
    h2 = hashlib.sha256(file2.read_bytes()).hexdigest()
    assert h1 == h2


# ==============================================================================
# TIER B: LOCAL BASELINE REGRESSION (IGNORED INTERIM ARTIFACT DEPENDENT)
# ==============================================================================

def test_tier_b_local_baseline_regression():
    """Tier B: Local regression test asserting bit-for-bit identity against frozen Stage P3 baseline.

    Requires Gate 3 authorization to execute via explicit opt-in RUN_TIER_B_LOCAL_REGRESSION=1.
    Performs full semantic column-by-column comparison and serialized-byte SHA-256 baseline check.
    """
    if os.environ.get("RUN_TIER_B_LOCAL_REGRESSION") != "1":
        pytest.skip(
            "Tier B local baseline regression requires explicit opt-in via "
            "RUN_TIER_B_LOCAL_REGRESSION=1 (Gate 3 authorized execution only)"
        )

    repo_root = Path(__file__).resolve().parents[1]
    required_artifacts = [
        repo_root / "data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv",
        repo_root / "data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv",
        repo_root / "data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv",
        repo_root / "data/interim/pilot/source_go_annotations_pilot.csv",
        repo_root / "data/interim/pilot/functional_coverage_pilot.csv",
        repo_root / "releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv",
    ]

    for p in required_artifacts:
        if not p.is_file():
            pytest.skip(f"Required local artifact absent for Tier B regression: {p}")

    # Load frozen inputs
    norm_ann_rows = []
    with open(required_artifacts[1], encoding="utf-8") as f:
        norm_ann_rows = list(csv.DictReader(f))

    raw_cov_rows = []
    with open(required_artifacts[2], encoding="utf-8") as f:
        raw_cov_rows = list(csv.DictReader(f))

    source_ann_rows = []
    with open(required_artifacts[3], encoding="utf-8") as f:
        source_ann_rows = list(csv.DictReader(f))

    func_cov_rows = []
    with open(required_artifacts[4], encoding="utf-8") as f:
        func_cov_rows = list(csv.DictReader(f))

    catalog_map = load_candidate_proteins(required_artifacts[5])

    # Reconstruct legacy matrix
    reconstructed_rows = build_concordance_matrix(
        normalized_annotations=norm_ann_rows,
        raw_coverage=raw_cov_rows,
        source_go_annotations=source_ann_rows,
        functional_coverage=func_cov_rows,
        catalog_map=catalog_map,
        pairs=None,  # Use VERIFIED_COHORT_PAIRS
        derived_aspects_rows=None,
    )

    # Load frozen baseline
    frozen_baseline_rows = []
    with open(required_artifacts[0], encoding="utf-8") as f:
        frozen_baseline_rows = list(csv.DictReader(f))

    assert len(reconstructed_rows) == 72
    assert len(frozen_baseline_rows) == 72

    # Semantic comparison
    base_by_cid = {r["concordance_id"]: r for r in frozen_baseline_rows}
    for r in reconstructed_rows:
        cid = r["concordance_id"]
        assert cid in base_by_cid, f"Missing concordance_id: {cid}"
        b_r = base_by_cid[cid]
        for col in CONCORDANCE_COLUMNS:
            r_val = r.get(col)
            b_val = b_r.get(col)
            if r_val is None:
                assert b_val == "" or b_val is None, (
                    f"Expected null for {cid} column '{col}', got '{b_val}'"
                )
            elif b_val == "" or b_val is None:
                pytest.fail(
                    f"Expected non-null value {r_val!r} for {cid} column '{col}', got empty string"
                )
            elif isinstance(r_val, float):
                assert float(b_val) == r_val, (
                    f"Numerical mismatch in {cid} column '{col}': {float(b_val)} != {r_val}"
                )
            elif isinstance(r_val, int) and not isinstance(r_val, bool):
                assert int(b_val) == r_val, (
                    f"Numerical mismatch in {cid} column '{col}': {int(b_val)} != {r_val}"
                )
            else:
                assert str(r_val) == b_val, (
                    f"Semantic mismatch in {cid} column '{col}': {r_val!r} != {b_val!r}"
                )

    # Serialized-byte comparison using historical P3 serialization contract
    output_buf = io.StringIO(newline="")
    writer = csv.DictWriter(output_buf, fieldnames=CONCORDANCE_COLUMNS)
    writer.writeheader()
    for r in reconstructed_rows:
        clean_row = {
            col: ("" if r.get(col) is None else str(r.get(col)))
            for col in CONCORDANCE_COLUMNS
        }
        writer.writerow(clean_row)

    computed_bytes = output_buf.getvalue().encode("utf-8")
    computed_digest = hashlib.sha256(computed_bytes).hexdigest()

    with open(required_artifacts[0], "rb") as f:
        original_bytes = f.read()
    expected_digest = hashlib.sha256(original_bytes).hexdigest()

    assert computed_digest == expected_digest, (
        f"Bitwise serialized digest mismatch: {computed_digest} != {expected_digest}"
    )
    assert computed_bytes == original_bytes, (
        f"Bitwise byte content mismatch against frozen baseline {required_artifacts[0]}"
    )
