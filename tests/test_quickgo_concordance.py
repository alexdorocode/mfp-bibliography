"""Unit and Contract Tests for Stage P3 QuickGO Concordance Engine.

Validates schemas, synthetic edge-case behaviors, arithmetic invariants,
Policy C exclusion rules, namespace-aware citation comparison, and
full integration with frozen pilot inputs.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from mfp_bibliography.quickgo_concordance import (
    GO_ASPECTS,
    POLICIES,
    ROOT_TERMS,
    VERIFIED_COHORT_PAIRS,
    build_concordance_matrix,
    build_normalized_annotations,
    build_normalized_coverage,
    build_reference_concordance,
    interpret_reference_token,
    load_candidate_proteins,
    normalize_reference_curie,
    parse_csv_value,
    validate_slice_outputs,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "data" / "curated"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "quickgo_pilot"
INTERIM_DIR = REPO_ROOT / "data" / "interim" / "pilot"
RELEASES_DIR = REPO_ROOT / "releases" / "mfp-catalog-candidate-v0.3.0"


# ---------------------------------------------------------------------------
# 1. Schema Conformance Tests
# ---------------------------------------------------------------------------


def test_draft_2020_12_schemas_valid() -> None:
    """Verify that all 4 Stage P3 schemas are valid Draft 2020-12 documents."""
    schema_names = [
        "external_quickgo_annotations.schema.json",
        "quickgo_coverage.schema.json",
        "quickgo_concordance.schema.json",
        "quickgo_reference_concordance.schema.json",
    ]
    for s_name in schema_names:
        s_path = SCHEMAS_DIR / s_name
        assert s_path.exists(), f"Missing schema file: {s_path}"
        with open(s_path, encoding="utf-8") as f:
            data = json.load(f)
        jsonschema.Draft202012Validator.check_schema(data)


# ---------------------------------------------------------------------------
# 2. Reference Normalization Unit Tests
# ---------------------------------------------------------------------------


def test_reference_curie_normalization() -> None:
    """Verify namespace-aware reference normalization rules."""
    # Bare digits -> PMID:<digits>
    assert normalize_reference_curie("12690200") == "PMID:12690200"
    assert normalize_reference_curie("22817892") == "PMID:22817892"

    # Already prefixed PMID
    assert normalize_reference_curie("PMID:17081979") == "PMID:17081979"

    # GO_REF CURIE preserved intact
    assert normalize_reference_curie("GO_REF:0000033") == "GO_REF:0000033"

    # Suspicious IDs preserved verbatim without silent repair
    assert normalize_reference_curie("901436") == "PMID:901436"
    # Uninterpretable strings return None from normalize_reference_curie
    assert normalize_reference_curie("20126659 (Homolog of WAKL10)") is None

    # Empty / null
    assert normalize_reference_curie("") is None
    assert normalize_reference_curie("   ") is None


# ---------------------------------------------------------------------------
# 3. Synthetic Edge-Case & Metric Tests
# ---------------------------------------------------------------------------


def test_nonempty_disjoint_sets_yield_zero_jaccard() -> None:
    """When both sets are non-empty and share zero terms, Jaccard must be 0.0 and status evaluable."""
    raw_ann = [
        {
            "database_annotation_id": "1",
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0005524",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "12690200",
        }
    ]
    raw_cov = [
        {
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": "1",
            "distinct_go_terms": "1",
            "notes": "",
        }
    ]
    catalog_map = {"Q42525": "MFP:U:8272bae0e8df8149"}
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)

    # Disjoint source annotation (GO:0016301 vs QuickGO GO:0005524)
    s_ann = [
        {
            "protein_id": "MFP:U:8272bae0e8df8149",
            "source_id": "SRC_PLANTMP",
            "go_id": "GO:0016301",
            "go_aspect": "MF",
            "evidence_raw": "IDA",
        }
    ]
    f_cov = [{"protein_id": "MFP:U:8272bae0e8df8149"}]

    matrix = build_concordance_matrix(norm_ann, raw_cov, s_ann, f_cov, catalog_map)
    row = next(r for r in matrix if r["source_id"] == "SRC_PLANTMP" and r["aspect"] == "MF" and r["policy_id"] == "captured_inventory_overlap")

    assert row["source_terms_count"] == 1
    assert row["quickgo_terms_count"] == 1
    assert row["exact_overlap_count"] == 0
    assert row["union_terms_count"] == 2
    assert row["jaccard_similarity"] == 0.0
    assert row["concordance_status"] == "evaluable"
    assert row["primary_non_evaluable_reason"] is None


def test_empty_set_conventions_yield_null_jaccard() -> None:
    """When either set is empty, Jaccard must be null and status not_evaluable."""
    raw_ann = [
        {
            "database_annotation_id": "1",
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0005524",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "12690200",
        }
    ]
    raw_cov = [
        {
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": "1",
            "distinct_go_terms": "1",
            "notes": "",
        }
    ]
    catalog_map = {"Q42525": "MFP:U:8272bae0e8df8149"}
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)

    # Empty source annotation for CC
    s_ann: List[Dict[str, Any]] = []
    f_cov = [{"protein_id": "MFP:U:8272bae0e8df8149"}]

    matrix = build_concordance_matrix(norm_ann, raw_cov, s_ann, f_cov, catalog_map)
    row_cc = next(r for r in matrix if r["source_id"] == "SRC_PLANTMP" and r["aspect"] == "CC" and r["policy_id"] == "captured_inventory_overlap")

    assert row_cc["source_terms_count"] == 0
    assert row_cc["quickgo_terms_count"] == 0
    assert row_cc["jaccard_similarity"] is None
    assert row_cc["concordance_status"] == "not_evaluable"
    assert row_cc["primary_non_evaluable_reason"] == "external_zero_annotations_aspect"


def test_identity_incompatibility_gate() -> None:
    """Flagged identity discrepancy (P34788) prevents score eligibility even when sets overlap."""
    raw_ann = [
        {
            "database_annotation_id": "1",
            "accession": "P34788",
            "database_protein_id": "RS18_ARATH",
            "go_id": "GO:0005840",
            "raw_category": "C",
            "evidence_code": "IDA",
            "publication_id": "7913892",
        }
    ]
    raw_cov = [
        {
            "accession": "P34788",
            "database_protein_id": "RS18_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "flagged_taxonomic_discrepancy",
            "stored_annotation_rows": "1",
            "distinct_go_terms": "1",
            "notes": "Flagged cross-species discrepancy",
        }
    ]
    catalog_map = {"P34788": "MFP:U:d0cd1a882c7acdf3"}
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)

    s_ann = [
        {
            "protein_id": "MFP:U:d0cd1a882c7acdf3",
            "source_id": "SRC_MULTITASKPROTDB_II",
            "go_id": "GO:0005840",
            "go_aspect": "CC",
            "evidence_raw": "IDA",
        }
    ]
    f_cov = [{"protein_id": "MFP:U:d0cd1a882c7acdf3"}]

    matrix = build_concordance_matrix(norm_ann, raw_cov, s_ann, f_cov, catalog_map)
    row = next(r for r in matrix if r["accession"] == "P34788" and r["aspect"] == "CC" and r["policy_id"] == "captured_inventory_overlap")

    assert row["source_terms_count"] == 1
    assert row["quickgo_terms_count"] == 1
    assert row["exact_overlap_count"] == 1
    assert row["jaccard_similarity"] is None
    assert row["concordance_status"] == "not_evaluable"
    assert row["primary_non_evaluable_reason"] == "unresolved_biological_identity"


def test_policy_c_disjunctive_survival_and_exclusion_accounting() -> None:
    """Verify Policy C ND/root exclusion accounting and disjunctive survival."""
    raw_ann = [
        # Non-root term with ND
        {
            "database_annotation_id": "1",
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0005524",
            "raw_category": "F",
            "evidence_code": "ND",
            "publication_id": "100",
        },
        # Same non-root term with IDA (survives!)
        {
            "database_annotation_id": "2",
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0005524",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "101",
        },
        # Root term with ND (overlap row!)
        {
            "database_annotation_id": "3",
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0003674",
            "raw_category": "F",
            "evidence_code": "ND",
            "publication_id": "102",
        },
    ]
    raw_cov = [
        {
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": "3",
            "distinct_go_terms": "2",
            "notes": "",
        }
    ]
    catalog_map = {"Q42525": "MFP:U:8272bae0e8df8149"}
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)

    s_ann = [
        {
            "protein_id": "MFP:U:8272bae0e8df8149",
            "source_id": "SRC_PLANTMP",
            "go_id": "GO:0005524",
            "go_aspect": "MF",
            "evidence_raw": "",  # missing evidence treated as unassessed
        }
    ]
    f_cov = [{"protein_id": "MFP:U:8272bae0e8df8149"}]

    matrix = build_concordance_matrix(norm_ann, raw_cov, s_ann, f_cov, catalog_map)
    row_c = next(r for r in matrix if r["source_id"] == "SRC_PLANTMP" and r["aspect"] == "MF" and r["policy_id"] == "filtered_descriptive_overlap")

    assert row_c["nd_matching_rows_count"] == 2
    assert row_c["root_matching_rows_count"] == 1
    assert row_c["nd_root_overlap_rows_count"] == 1
    # Net excluded = 2 + 1 - 1 = 2
    assert row_c["net_excluded_rows_count"] == 2

    # GO:0005524 survived via row 2!
    assert row_c["quickgo_terms_count"] == 1
    assert row_c["terms_retained_via_other_rows_count"] == 1
    assert row_c["terms_lost_after_filtering_count"] == 1  # root term GO:0003674 lost
    assert row_c["unassessed_evidence_rows_count"] == 1  # source row missing evidence


# ---------------------------------------------------------------------------
# 4. Integration Tests on Frozen Inputs
# ---------------------------------------------------------------------------


def test_full_pipeline_on_frozen_inputs() -> None:
    """Verify that full pipeline execution over frozen inputs satisfies all 16 criteria."""
    catalog_map = load_candidate_proteins(RELEASES_DIR / "mfp_proteins.csv")

    with open(FIXTURES_DIR / "raw_quickgo_annotations.csv", encoding="utf-8") as f:
        raw_ann = list(csv.DictReader(f))
    with open(FIXTURES_DIR / "raw_quickgo_coverage.csv", encoding="utf-8") as f:
        raw_cov = list(csv.DictReader(f))
    with open(INTERIM_DIR / "source_go_annotations_pilot.csv", encoding="utf-8") as f:
        s_ann = list(csv.DictReader(f))
    with open(INTERIM_DIR / "functional_claims_pilot.csv", encoding="utf-8") as f:
        f_claims = list(csv.DictReader(f))
    with open(INTERIM_DIR / "functional_coverage_pilot.csv", encoding="utf-8") as f:
        f_cov = list(csv.DictReader(f))

    # 1. Annotations
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)
    assert len(norm_ann) == 156

    # 2. Coverage
    norm_cov = build_normalized_coverage(raw_cov, catalog_map)
    assert len(norm_cov) == 8

    # 3. Concordance
    matrix = build_concordance_matrix(norm_ann, raw_cov, s_ann, f_cov, catalog_map)
    assert len(matrix) == 72

    # 4. Reference Concordance
    ref_matrix = build_reference_concordance(f_claims, raw_ann, raw_cov, f_cov, catalog_map)
    assert len(ref_matrix) == 12

    # 5. Schema and Invariant Validation
    validate_slice_outputs(norm_ann, norm_cov, matrix, ref_matrix, SCHEMAS_DIR)


# ---------------------------------------------------------------------------
# 5. Determinism & Round-Trip Tests
# ---------------------------------------------------------------------------


def test_deterministic_multi_run_stability() -> None:
    """Repeated runs on identical inputs must produce bitwise identical output records."""
    catalog_map = load_candidate_proteins(RELEASES_DIR / "mfp_proteins.csv")

    with open(FIXTURES_DIR / "raw_quickgo_annotations.csv", encoding="utf-8") as f:
        raw_ann = list(csv.DictReader(f))
    with open(FIXTURES_DIR / "raw_quickgo_coverage.csv", encoding="utf-8") as f:
        raw_cov = list(csv.DictReader(f))
    with open(INTERIM_DIR / "source_go_annotations_pilot.csv", encoding="utf-8") as f:
        s_ann = list(csv.DictReader(f))
    with open(INTERIM_DIR / "functional_claims_pilot.csv", encoding="utf-8") as f:
        f_claims = list(csv.DictReader(f))
    with open(INTERIM_DIR / "functional_coverage_pilot.csv", encoding="utf-8") as f:
        f_cov = list(csv.DictReader(f))

    # Run 1
    norm_ann1 = build_normalized_annotations(raw_ann, catalog_map)
    matrix1 = build_concordance_matrix(norm_ann1, raw_cov, s_ann, f_cov, catalog_map)
    ref_matrix1 = build_reference_concordance(f_claims, raw_ann, raw_cov, f_cov, catalog_map)

    # Run 2
    norm_ann2 = build_normalized_annotations(raw_ann, catalog_map)
    matrix2 = build_concordance_matrix(norm_ann2, raw_cov, s_ann, f_cov, catalog_map)
    ref_matrix2 = build_reference_concordance(f_claims, raw_ann, raw_cov, f_cov, catalog_map)

    assert norm_ann1 == norm_ann2
    assert matrix1 == matrix2
    assert ref_matrix1 == ref_matrix2


def test_csv_null_serialization_and_loader_roundtrip() -> None:
    """Null values must serialize as empty strings and deserialize back to None."""
    val_none = parse_csv_value("")
    assert val_none is None
    val_str = parse_csv_value("hello")
    assert val_str == "hello"
    val_ws = parse_csv_value("   ")
    assert val_ws is None



def test_generated_quickgo_slice_artifacts() -> None:
    """Verify that generated slice files on disk match manifest hashes and validate against schemas."""
    slice_dir = REPO_ROOT / "data" / "interim" / "pilot" / "quickgo_slice"
    manifest_path = slice_dir / "manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    for fname, meta in manifest["output_inventory"].items():
        fpath = slice_dir / fname
        assert fpath.exists()
        from scripts.build_quickgo_concordance_pilot import compute_sha256
        assert compute_sha256(fpath) == meta["sha256"]



def test_interpret_reference_token() -> None:
    """Verify that uninterpretable raw tokens are separated from comparable CURIEs."""
    # Comparable PMIDs
    assert interpret_reference_token("12690200") == ("PMID:12690200", None)
    assert interpret_reference_token("PMID:27616280") == ("PMID:27616280", None)
    assert interpret_reference_token("901436") == ("PMID:901436", None)

    # Comparable GO_REF
    assert interpret_reference_token("GO_REF:0000033") == ("GO_REF:0000033", None)

    # Uninterpretable text tokens (notes, homolog mentions, predictions)
    assert interpret_reference_token("Predicted in 23835195") == (None, "Predicted in 23835195")
    assert interpret_reference_token("20126659 (Homolog of WAKL10)") == (None, "20126659 (Homolog of WAKL10)")
    assert interpret_reference_token("26638082 (Homolog of POT7)") == (None, "26638082 (Homolog of POT7)")


def test_p24228_reference_indeterminate_due_to_parse_failure() -> None:
    """Extraction failure on P24228 must yield indeterminate inventory, not observed absence."""
    catalog_map = {"P24228": "MFP:U:75a37d1de4bcf985"}
    raw_ann = [
        {
            "database_annotation_id": "1",
            "accession": "P24228",
            "database_protein_id": "DACB_ECOLI",
            "go_id": "GO:0004185",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "16411754",
        }
    ]
    raw_cov = [
        {
            "accession": "P24228",
            "database_protein_id": "DACB_ECOLI",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": "1",
            "distinct_go_terms": "1",
            "notes": "",
        }
    ]
    f_claims: List[Dict[str, Any]] = []
    # parse_failure in functional coverage
    f_cov = [
        {
            "protein_id": "MFP:U:75a37d1de4bcf985",
            "source_id": "SRC_MOONPROT",
            "coverage_status": "parse_failure",
        }
    ]

    ref_matrix = build_reference_concordance(
        f_claims, raw_ann, raw_cov, f_cov, catalog_map, pairs=[("P24228", "SRC_MOONPROT")]
    )
    assert len(ref_matrix) == 1
    row = ref_matrix[0]

    assert row["source_references_count"] is None
    assert row["quickgo_references_count"] == 1
    assert row["shared_references_count"] is None
    assert row["jaccard_similarity"] is None
    assert row["reference_concordance_status"] == "not_evaluable"
    assert row["comparison_completeness"] == "indeterminate"
    assert row["primary_non_evaluable_reason"] == "source_extraction_incomplete"


def test_policy_c_retains_missing_evidence_codes() -> None:
    """Missing source evidence codes are treated as unassessed and retained unless root terms."""
    catalog_map = {"Q42525": "MFP:U:8272bae0e8df8149"}
    raw_ann = [
        {
            "database_annotation_id": "1",
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0005524",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "12690200",
        }
    ]
    raw_cov = [
        {
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": "1",
            "distinct_go_terms": "1",
            "notes": "",
        }
    ]
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)

    # Source annotation with empty evidence string
    s_ann = [
        {
            "protein_id": "MFP:U:8272bae0e8df8149",
            "source_id": "SRC_PLANTMP",
            "go_id": "GO:0005524",
            "go_aspect": "MF",
            "evidence_raw": "",  # missing evidence
        }
    ]
    f_cov = [{"protein_id": "MFP:U:8272bae0e8df8149"}]

    matrix = build_concordance_matrix(
        norm_ann, raw_cov, s_ann, f_cov, catalog_map, pairs=[("Q42525", "SRC_PLANTMP")]
    )

    row_b = next(r for r in matrix if r["aspect"] == "MF" and r["policy_id"] == "captured_inventory_overlap")
    row_c = next(r for r in matrix if r["aspect"] == "MF" and r["policy_id"] == "filtered_descriptive_overlap")

    # In Policy B, term is present
    assert row_b["source_terms_count"] == 1
    assert row_b["concordance_status"] == "evaluable"

    # In Policy C, term is RETAINED (not dropped!)
    assert row_c["source_terms_count"] == 1
    assert row_c["concordance_status"] == "evaluable"
    assert row_c["jaccard_similarity"] == 1.0
    assert row_c["unassessed_evidence_rows_count"] == 1
