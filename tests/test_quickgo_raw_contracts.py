"""Offline unit and contract tests for raw QuickGO export validation.

Tests stages P1-P2 raw export schemas, invariants, null handling, and cross-file reconciliation.
All tests run 100% offline without database or network dependencies.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import tempfile
from typing import Any, Dict, List

import pytest
from jsonschema import ValidationError

from mfp_bibliography.quickgo_raw_validator import (
    EXPECTED_COHORT,
    QuickGORawValidationError,
    build_validator,
    parse_csv_value,
    read_raw_annotations_csv,
    read_raw_coverage_csv,
    validate_cross_file_consistency,
    validate_export_pair,
    validate_raw_annotations_invariants,
    validate_raw_annotations_schema,
    validate_raw_coverage_invariants,
    validate_raw_coverage_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "raw_quickgo_annotations.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "raw_quickgo_coverage.schema.json"


# -----------------------------------------------------------------------------
# Fixtures for Schema Validators
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def annotations_validator():
    return build_validator(ANNOTATIONS_SCHEMA_PATH)


@pytest.fixture(scope="module")
def coverage_validator():
    return build_validator(COVERAGE_SCHEMA_PATH)


# -----------------------------------------------------------------------------
# Synthetic In-Memory Valid Data
# -----------------------------------------------------------------------------

@pytest.fixture
def valid_synthetic_coverage_rows() -> List[Dict[str, Any]]:
    return [
        {
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 2,
            "distinct_go_terms": 2,
            "notes": None,
        },
        {
            "accession": "Q9Y3E5",
            "database_protein_id": "PTRH2_HUMAN",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 1,
            "distinct_go_terms": 1,
            "notes": None,
        },
        {
            "accession": "P0AFW0",
            "database_protein_id": "RFAH_ECOLI",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 1,
            "distinct_go_terms": 1,
            "notes": None,
        },
        {
            "accession": "P34788",
            "database_protein_id": "RS18_ARATH",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "flagged_taxonomic_discrepancy",
            "stored_annotation_rows": 1,
            "distinct_go_terms": 1,
            "notes": "Upstream species conflict: Spinach vs Arabidopsis",
        },
        {
            "accession": "P78007",
            "database_protein_id": "LDH_MYCPN",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 1,
            "distinct_go_terms": 1,
            "notes": None,
        },
        {
            "accession": "P24228",
            "database_protein_id": "DACB_ECOLI",
            "quickgo_coverage_status": "annotations_available",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 1,
            "distinct_go_terms": 1,
            "notes": None,
        },
        {
            "accession": "A0A0H3CDS3",
            "database_protein_id": "A0A0H3CDS3_CAUVN",
            "quickgo_coverage_status": "zero_annotations_found",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 0,
            "distinct_go_terms": 0,
            "notes": "Linked protein found but zero annotations in database",
        },
        {
            "accession": "E6KMA1",
            "database_protein_id": None,
            "quickgo_coverage_status": "unlinked_in_database",
            "identity_review_status": "no_discrepancy_noted",
            "stored_annotation_rows": 0,
            "distinct_go_terms": 0,
            "notes": "Accession present but protein_id is NULL",
        },
    ]


@pytest.fixture
def valid_synthetic_annotations_rows() -> List[Dict[str, Any]]:
    return [
        {
            "database_annotation_id": 101,
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0004396",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "12690200",
        },
        {
            "database_annotation_id": 102,
            "accession": "Q42525",
            "database_protein_id": "HXK1_ARATH",
            "go_id": "GO:0005634",
            "raw_category": "cellular_component",
            "evidence_code": "IDA",
            "publication_id": "GO_REF:0000033",
        },
        {
            "database_annotation_id": 201,
            "accession": "Q9Y3E5",
            "database_protein_id": "PTRH2_HUMAN",
            "go_id": "GO:0004045",
            "raw_category": "molecular_function",
            "evidence_code": "IDA",
            "publication_id": "14660562",
        },
        {
            "database_annotation_id": 301,
            "accession": "P0AFW0",
            "database_protein_id": "RFAH_ECOLI",
            "go_id": "GO:0001000",
            "raw_category": "F",
            "evidence_code": "IDA",
            "publication_id": "22817892",
        },
        {
            "database_annotation_id": 401,
            "accession": "P34788",
            "database_protein_id": "RS18_ARATH",
            "go_id": "GO:0003735",
            "raw_category": "F",
            "evidence_code": "IEA",
            "publication_id": "GO_REF:0000002",
        },
        {
            "database_annotation_id": 501,
            "accession": "P78007",
            "database_protein_id": "LDH_MYCPN",
            "go_id": "GO:0006096",
            "raw_category": "biological_process",
            "evidence_code": "TAS",
            "publication_id": None,
        },
        {
            "database_annotation_id": 601,
            "accession": "P24228",
            "database_protein_id": "DACB_ECOLI",
            "go_id": "GO:0004185",
            "raw_category": "molecular_function",
            "evidence_code": "IDA",
            "publication_id": "15297880",
        },
    ]


# -----------------------------------------------------------------------------
# Unit Tests: Schema Conformance
# -----------------------------------------------------------------------------

def test_schemas_are_valid_draft202012():
    """Verify both schemas compile cleanly under Draft 2020-12."""
    build_validator(ANNOTATIONS_SCHEMA_PATH)
    build_validator(COVERAGE_SCHEMA_PATH)


def test_valid_synthetic_data_passes_all_checks(
    valid_synthetic_annotations_rows,
    valid_synthetic_coverage_rows,
    annotations_validator,
    coverage_validator,
):
    """Verify clean synthetic cohort passes schema and dataset invariant checks."""
    validate_raw_annotations_schema(valid_synthetic_annotations_rows, annotations_validator)
    validate_raw_coverage_schema(valid_synthetic_coverage_rows, coverage_validator)

    ann_stats = validate_raw_annotations_invariants(valid_synthetic_annotations_rows)
    assert ann_stats["total_rows"] == 7
    assert ann_stats["pmid_rows"] == 4
    assert ann_stats["go_ref_rows"] == 2
    assert ann_stats["null_ref_rows"] == 1

    cov_stats = validate_raw_coverage_invariants(valid_synthetic_coverage_rows)
    assert cov_stats["total_coverage_rows"] == 8
    assert cov_stats["status_counts"]["annotations_available"] == 6
    assert cov_stats["status_counts"]["zero_annotations_found"] == 1
    assert cov_stats["status_counts"]["unlinked_in_database"] == 1

    recon = validate_cross_file_consistency(
        valid_synthetic_annotations_rows, valid_synthetic_coverage_rows
    )
    assert len(recon) == 8
    assert recon["P34788"]["identity_review_status"] == "flagged_taxonomic_discrepancy"
    assert recon["Q42525"]["annotation_rows"] == 2
    assert recon["A0A0H3CDS3"]["annotation_rows"] == 0
    assert recon["E6KMA1"]["annotation_rows"] == 0


# -----------------------------------------------------------------------------
# Unit Tests: Preserving All Eight Cohort Members & Denominator Accounting
# -----------------------------------------------------------------------------

def test_coverage_rejects_missing_cohort_member(valid_synthetic_coverage_rows, coverage_validator):
    """Coverage must have exactly all 8 cohort members; dropping one must fail."""
    incomplete = [r for r in valid_synthetic_coverage_rows if r["accession"] != "E6KMA1"]
    with pytest.raises(QuickGORawValidationError, match="Coverage row count 7 does not match cohort size 8"):
        validate_raw_coverage_invariants(incomplete)


def test_coverage_rejects_duplicate_accession(valid_synthetic_coverage_rows):
    """Coverage must not contain duplicated accession entries."""
    dup = [dict(r) for r in valid_synthetic_coverage_rows]
    dup[-1]["accession"] = dup[0]["accession"]  # duplicate Q42525 while keeping length 8
    with pytest.raises(QuickGORawValidationError, match="Duplicate accessions in coverage export"):
        validate_raw_coverage_invariants(dup)


def test_coverage_rejects_unrecognized_accession(valid_synthetic_coverage_rows):
    """Coverage must not substitute an accession with an uncataloged code."""
    mod = [dict(r) for r in valid_synthetic_coverage_rows]
    mod[0]["accession"] = "P99999"
    with pytest.raises(QuickGORawValidationError, match="Coverage accessions mismatch"):
        validate_raw_coverage_invariants(mod)


# -----------------------------------------------------------------------------
# Unit Tests: Database Coverage vs Biological Identity Review
# -----------------------------------------------------------------------------

def test_p34788_must_be_flagged_for_taxonomic_discrepancy(valid_synthetic_coverage_rows):
    """P34788 must be flagged as taxonomic discrepancy even though annotations exist."""
    mod = [dict(r) for r in valid_synthetic_coverage_rows]
    for r in mod:
        if r["accession"] == "P34788":
            r["identity_review_status"] = "no_discrepancy_noted"
    with pytest.raises(QuickGORawValidationError, match="P34788 must have identity_review_status 'flagged_taxonomic_discrepancy'"):
        validate_raw_coverage_invariants(mod)


def test_other_cohort_members_not_falsely_flagged(valid_synthetic_coverage_rows):
    """Other cohort members without discrepancy must be no_discrepancy_noted."""
    mod = [dict(r) for r in valid_synthetic_coverage_rows]
    for r in mod:
        if r["accession"] == "Q42525":
            r["identity_review_status"] = "flagged_taxonomic_discrepancy"
    with pytest.raises(QuickGORawValidationError, match="Q42525 must have identity_review_status 'no_discrepancy_noted'"):
        validate_raw_coverage_invariants(mod)


# -----------------------------------------------------------------------------
# Unit Tests: Actual Annotations Only & Zero Artificial Rows
# -----------------------------------------------------------------------------

def test_annotations_rejects_unlinked_accession_with_artificial_row(
    valid_synthetic_annotations_rows, valid_synthetic_coverage_rows
):
    """If an accession is unlinked in coverage, annotations must NOT have fake rows."""
    fake_row = {
        "database_annotation_id": 999,
        "accession": "E6KMA1",
        "database_protein_id": "FAKE_PROTEIN",
        "go_id": "GO:0005515",
        "raw_category": "F",
        "evidence_code": "IDA",
        "publication_id": "12345678",
    }
    with_fake = valid_synthetic_annotations_rows + [fake_row]
    with pytest.raises(QuickGORawValidationError, match="Accession 'E6KMA1' has annotations but coverage_status is 'unlinked_in_database'"):
        validate_cross_file_consistency(with_fake, valid_synthetic_coverage_rows)


def test_annotations_rejects_zero_annotations_found_with_row(
    valid_synthetic_annotations_rows, valid_synthetic_coverage_rows
):
    """If an accession is zero_annotations_found in coverage, annotations must have 0 rows."""
    fake_row = {
        "database_annotation_id": 999,
        "accession": "A0A0H3CDS3",
        "database_protein_id": "A0A0H3CDS3_CAUVN",
        "go_id": "GO:0005515",
        "raw_category": "F",
        "evidence_code": "IDA",
        "publication_id": "12345678",
    }
    with_fake = valid_synthetic_annotations_rows + [fake_row]
    with pytest.raises(QuickGORawValidationError, match="Accession 'A0A0H3CDS3' has annotations but coverage_status is 'zero_annotations_found'"):
        validate_cross_file_consistency(with_fake, valid_synthetic_coverage_rows)


# -----------------------------------------------------------------------------
# Unit Tests: Publication ID Formats & Unexpected Values
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "pub_id",
    [
        "12345678",          # numeric PMID
        "901436",            # bare numeric text
        "GO_REF:0000033",    # canonical GO_REF
        "GO_REF:0000002",    # canonical GO_REF with leading zeros
        None,                # null reference (e.g. TAS)
    ],
)
def test_valid_publication_ids(pub_id, annotations_validator):
    """Verify standard valid reference formats pass schema."""
    row = {
        "database_annotation_id": 1,
        "accession": "Q42525",
        "database_protein_id": "HXK1_ARATH",
        "go_id": "GO:0004396",
        "raw_category": "F",
        "evidence_code": "IDA",
        "publication_id": pub_id,
    }
    validate_raw_annotations_schema([row], annotations_validator)


@pytest.mark.parametrize(
    "invalid_pub_id",
    [
        "PMID:12345678",     # prefixed PMID not expected in raw MFP_QuickV1
        "GO_REF:33",         # non-7-digit GO_REF
        "DOI:10.1016/xxx",   # unhandled namespace
        "unspecified",       # text string
        "",                  # empty string (must be converted to None before validation)
    ],
)
def test_invalid_publication_ids_rejected(invalid_pub_id, annotations_validator):
    """Verify invalid reference formats fail schema."""
    row = {
        "database_annotation_id": 1,
        "accession": "Q42525",
        "database_protein_id": "HXK1_ARATH",
        "go_id": "GO:0004396",
        "raw_category": "F",
        "evidence_code": "IDA",
        "publication_id": invalid_pub_id,
    }
    with pytest.raises(QuickGORawValidationError, match="failed schema validation"):
        validate_raw_annotations_schema([row], annotations_validator)


# -----------------------------------------------------------------------------
# Unit Tests: Duplicate Detection & Database Row Tracing
# -----------------------------------------------------------------------------

def test_duplicate_database_annotation_id_rejected(valid_synthetic_annotations_rows):
    """Database annotation primary keys must be strictly unique."""
    dup_id = list(valid_synthetic_annotations_rows)
    dup_id.append(dict(valid_synthetic_annotations_rows[0]))
    dup_id[-1]["go_id"] = "GO:0009999"  # different GO, same db_id
    with pytest.raises(QuickGORawValidationError, match="Duplicate database_annotation_id 101"):
        validate_raw_annotations_invariants(dup_id)


def test_duplicate_annotation_tuple_rejected(valid_synthetic_annotations_rows):
    """Identical (accession, go_id, evidence_code, publication_id) tuples must fail."""
    dup_tuple = list(valid_synthetic_annotations_rows)
    cloned = dict(valid_synthetic_annotations_rows[0])
    cloned["database_annotation_id"] = 9999  # different db_id, same tuple
    dup_tuple.append(cloned)
    with pytest.raises(QuickGORawValidationError, match="Duplicate annotation tuple"):
        validate_raw_annotations_invariants(dup_tuple)


# -----------------------------------------------------------------------------
# Unit Tests: Cross-File Reconciliation Counts
# -----------------------------------------------------------------------------

def test_cross_file_reconciliation_detects_row_count_mismatch(
    valid_synthetic_annotations_rows, valid_synthetic_coverage_rows
):
    """Coverage stored_annotation_rows must match actual annotation row count."""
    mod_cov = [dict(r) for r in valid_synthetic_coverage_rows]
    for r in mod_cov:
        if r["accession"] == "Q42525":
            r["stored_annotation_rows"] = 5  # actual is 2
    with pytest.raises(QuickGORawValidationError, match="Accession 'Q42525' annotation row count mismatch: coverage claims 5, actual is 2"):
        validate_cross_file_consistency(valid_synthetic_annotations_rows, mod_cov)


def test_cross_file_reconciliation_detects_distinct_go_mismatch(
    valid_synthetic_annotations_rows, valid_synthetic_coverage_rows
):
    """Coverage distinct_go_terms must match actual distinct GO count."""
    mod_cov = [dict(r) for r in valid_synthetic_coverage_rows]
    for r in mod_cov:
        if r["accession"] == "Q42525":
            r["distinct_go_terms"] = 10  # actual is 2
    with pytest.raises(QuickGORawValidationError, match="Accession 'Q42525' distinct GO count mismatch: coverage claims 10, actual is 2"):
        validate_cross_file_consistency(valid_synthetic_annotations_rows, mod_cov)


# -----------------------------------------------------------------------------
# Unit Tests: CSV Null Parsing & Empty String Handling
# -----------------------------------------------------------------------------

def test_csv_reader_maps_empty_string_to_none():
    """CSV reader must correctly deserialize empty string fields as None."""
    csv_data = """database_annotation_id,accession,database_protein_id,go_id,raw_category,evidence_code,publication_id
501,P78007,LDH_MYCPN,GO:0006096,biological_process,TAS,
"""
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".csv") as tmp:
        tmp.write(csv_data)
        tmp.flush()
        rows = read_raw_annotations_csv(Path(tmp.name))
        assert len(rows) == 1
        assert rows[0]["publication_id"] is None


# -----------------------------------------------------------------------------
# Unit Tests: Absent Accession Synthetic Coverage State
# -----------------------------------------------------------------------------

def test_coverage_schema_handles_absent_accession_state(coverage_validator):
    """Schema must validate absent_from_database state with null protein and 0 rows."""
    row = {
        "accession": "Q9LIA4",
        "database_protein_id": None,
        "quickgo_coverage_status": "absent_from_database",
        "identity_review_status": "no_discrepancy_noted",
        "stored_annotation_rows": 0,
        "distinct_go_terms": 0,
        "notes": "Accession completely absent from database",
    }
    validate_raw_coverage_schema([row], coverage_validator)


# -----------------------------------------------------------------------------
# Integration Tests: Frozen Fixtures on Disk & Dedicated Manifest
# -----------------------------------------------------------------------------

FROZEN_DIR = REPO_ROOT / "tests" / "fixtures" / "quickgo_pilot"


def test_frozen_pilot_fixtures_exist_and_pass_validation():
    """Verify published frozen fixtures in tests/fixtures/quickgo_pilot/ pass all checks."""
    ann_file = FROZEN_DIR / "raw_quickgo_annotations.csv"
    cov_file = FROZEN_DIR / "raw_quickgo_coverage.csv"
    manifest_file = FROZEN_DIR / "manifest.json"

    assert ann_file.exists(), f"Missing frozen annotations fixture: {ann_file}"
    assert cov_file.exists(), f"Missing frozen coverage fixture: {cov_file}"
    assert manifest_file.exists(), f"Missing frozen manifest: {manifest_file}"

    report = validate_export_pair(
        ann_file, cov_file, ANNOTATIONS_SCHEMA_PATH, COVERAGE_SCHEMA_PATH
    )

    with manifest_file.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    assert manifest["files"]["raw_quickgo_annotations.csv"]["sha256"] == report["annotations_sha256"]
    assert manifest["files"]["raw_quickgo_coverage.csv"]["sha256"] == report["coverage_sha256"]
    assert report["coverage_stats"]["total_coverage_rows"] == 8
    assert report["annotation_stats"]["total_rows"] == 156
    assert report["annotation_stats"]["pmid_rows"] == 93
    assert report["annotation_stats"]["go_ref_rows"] == 63
    assert report["annotation_stats"]["null_ref_rows"] == 0
    assert report["reconciliation"]["P34788"]["identity_review_status"] == "flagged_taxonomic_discrepancy"
    assert report["reconciliation"]["E6KMA1"]["quickgo_coverage_status"] == "unlinked_in_database"
    assert report["reconciliation"]["A0A0H3CDS3"]["quickgo_coverage_status"] == "zero_annotations_found"

