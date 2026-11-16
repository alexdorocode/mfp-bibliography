"""Unit and contract tests for GO Aspect Metadata Enrichment Engine (PIL-04.1A)."""

import json
import os
import tempfile
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from mfp_bibliography.go_aspect_enrichment import (
    compute_file_sha256,
    enrich_annotation_row,
    enrich_source_go_annotations_file,
    parse_obo_ontology,
    validate_derived_rows_against_schema,
    write_derived_source_go_aspects_csv,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "test_go_aspect_enrichment"
SYNTHETIC_OBO = FIXTURES_DIR / "test_ontology.obo"
SCHEMA_PATH = Path(__file__).parent.parent / "data" / "curated" / "derived_source_go_aspects.schema.json"
PILOT_INPUT_CSV = Path(__file__).parent.parent / "data" / "interim" / "pilot" / "source_go_annotations_pilot.csv"
CANONICAL_OBO_PATH = Path("/home/alexdoro/repositories/mfp-dataset-designer/go-basic.obo")
CANONICAL_OBO_SHA256 = "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391"


@pytest.fixture(scope="module")
def synthetic_ontology():
    """Load the synthetic test ontology fixture."""
    return parse_obo_ontology(SYNTHETIC_OBO)


def test_schema_is_valid_draft_2020_12():
    """Verify that derived_source_go_aspects.schema.json is a valid Draft 2020-12 schema."""
    assert SCHEMA_PATH.is_file(), f"Schema file not found at {SCHEMA_PATH}"
    with open(SCHEMA_PATH) as f:
        schema_json = json.load(f)
    Draft202012Validator.check_schema(schema_json)


def test_obo_digest_verification(tmp_path):
    """Verify that parse_obo_ontology verifies expected sha256 correctly."""
    valid_digest = compute_file_sha256(SYNTHETIC_OBO)
    ont = parse_obo_ontology(SYNTHETIC_OBO, expected_sha256=valid_digest)
    assert ont.sha256_digest == valid_digest
    assert ont.format_version == "1.2"
    assert ont.data_version == "releases/2026-test-snapshot"

    with pytest.raises(ValueError, match="digest mismatch"):
        parse_obo_ontology(SYNTHETIC_OBO, expected_sha256="0" * 64)


def test_active_primary_mapping(synthetic_ontology):
    """Active primary term resolves to namespace without overwriting source values."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_MOONPROT",
        "source_record_id": "test_rec_1",
        "claim_id": None,
        "annotation_index": "0",
        "raw_annotation_text": "GO:0003824 catalytic activity",
        "go_id": "GO:0003824",
        "go_aspect": None,
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "resolved_primary"
    assert res["source_go_id"] == "GO:0003824"
    assert res["resolved_go_id"] == "GO:0003824"
    assert res["derived_aspect"] == "MF"
    assert res["source_declared_aspect"] is None
    assert res["term_name_resolved"] == "catalytic activity"


def test_alternate_id_mapping(synthetic_ontology):
    """Alternate ID maps to primary term while retaining verbatim source_go_id."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_MOONPROT",
        "source_record_id": "test_rec_2",
        "claim_id": None,
        "annotation_index": "1",
        "raw_annotation_text": "GO:0016021 membrane (alt)",
        "go_id": "GO:0016021",
        "go_aspect": None,
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "resolved_secondary_alt_id"
    assert res["source_go_id"] == "GO:0016021"
    assert res["resolved_go_id"] == "GO:0016020"
    assert res["derived_aspect"] == "CC"
    assert "alt_id" in res["notes"]


def test_obsolete_with_replaced_by(synthetic_ontology):
    """Obsolete term with replaced_by records replacement in metadata, NOT as resolved_go_id."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_MOONPROT",
        "source_record_id": "test_rec_3",
        "claim_id": None,
        "annotation_index": "2",
        "raw_annotation_text": "GO:0019048 obsolete modulation",
        "go_id": "GO:0019048",
        "go_aspect": None,
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "obsolete_replaced_by"
    assert res["source_go_id"] == "GO:0019048"
    assert res["resolved_go_id"] is None
    assert res["derived_aspect"] is None
    assert res["replaced_by_go_id"] == "GO:0044003"
    assert res["consider_go_ids"] is None


def test_obsolete_unreplaced_with_consider(synthetic_ontology):
    """Obsolete term with consider records suggestions in metadata, never treating as equivalence."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_MOONPROT",
        "source_record_id": "test_rec_4",
        "claim_id": None,
        "annotation_index": "3",
        "raw_annotation_text": "GO:0000988 obsolete transcription factor",
        "go_id": "GO:0000988",
        "go_aspect": None,
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "obsolete_unreplaced"
    assert res["source_go_id"] == "GO:0000988"
    assert res["resolved_go_id"] is None
    assert res["derived_aspect"] is None
    assert res["replaced_by_go_id"] is None
    assert res["consider_go_ids"] == "GO:0005515;GO:0140110"


def test_obsolete_unreplaced_without_consider(synthetic_ontology):
    """Obsolete term without replacement or consider."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_PLANTMP",
        "source_record_id": "test_rec_5",
        "claim_id": None,
        "annotation_index": "4",
        "raw_annotation_text": "GO:0010033 obsolete response",
        "go_id": "GO:0010033",
        "go_aspect": "BP",
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "obsolete_unreplaced"
    assert res["source_declared_aspect"] == "BP"
    assert res["resolved_go_id"] is None
    assert res["derived_aspect"] is None
    assert res["replaced_by_go_id"] is None
    assert res["consider_go_ids"] is None


def test_unknown_identifier(synthetic_ontology):
    """Unknown term not found in ontology snapshot."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_PLANTMP",
        "source_record_id": "test_rec_6",
        "claim_id": None,
        "annotation_index": "5",
        "raw_annotation_text": "GO:0999999 unknown term",
        "go_id": "GO:0999999",
        "go_aspect": "BP",
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "unresolved_unknown_id"
    assert res["source_declared_aspect"] == "BP"
    assert res["resolved_go_id"] is None
    assert res["derived_aspect"] is None


def test_malformed_identifier(synthetic_ontology):
    """Malformed identifier failing regex pattern."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_PLANTMP",
        "source_record_id": "test_rec_7",
        "claim_id": None,
        "annotation_index": "6",
        "raw_annotation_text": "MALFORMED_GO_ID",
        "go_id": "MALFORMED_GO_ID",
        "go_aspect": "BP",
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "unresolved_malformed_id"
    assert res["resolved_go_id"] is None
    assert res["derived_aspect"] is None


def test_aspect_conflict_flagging(synthetic_ontology):
    """Source-declared aspect conflicting with ontology namespace retains both and flags mismatch."""
    row = {
        "annotation_id": "MFP:SGA:SRC_TEST:0123456789abcdef",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_PLANTMP",
        "source_record_id": "test_rec_8",
        "claim_id": None,
        "annotation_index": "7",
        "raw_annotation_text": "GO:0003824 catalytic activity (conflicted)",
        "go_id": "GO:0003824",
        "go_aspect": "BP",  # Source declared BP, but GO:0003824 is molecular_function (MF)
    }
    res = enrich_annotation_row(row, synthetic_ontology)
    assert res["mapping_status"] == "conflict_source_ontology_aspect_mismatch"
    assert res["source_declared_aspect"] == "BP"
    assert res["derived_aspect"] == "MF"
    assert res["resolved_go_id"] == "GO:0003824"
    assert "Conflict" in res["notes"]


@pytest.mark.skipif(not CANONICAL_OBO_PATH.exists(), reason="Canonical OBO file not available on host")
def test_full_pilot_slice_offline_enrichment():
    """End-to-end integration test on frozen source_go_annotations_pilot.csv."""
    assert PILOT_INPUT_CSV.is_file(), f"Input CSV missing: {PILOT_INPUT_CSV}"
    ontology = parse_obo_ontology(CANONICAL_OBO_PATH, expected_sha256=CANONICAL_OBO_SHA256)

    derived_rows, summary = enrich_source_go_annotations_file(PILOT_INPUT_CSV, ontology)

    # 1. Exact cardinality check: 353 rows in, 353 rows out
    assert len(derived_rows) == 353
    assert summary["total_input_rows"] == 353

    # 2. Schema validation
    validate_derived_rows_against_schema(derived_rows, SCHEMA_PATH)

    # 3. Exact verified status distribution
    dist = summary["status_distribution"]
    assert dist["resolved_primary"] == 336
    assert dist["resolved_secondary_alt_id"] == 5
    assert dist["obsolete_replaced_by"] == 6
    assert dist["obsolete_unreplaced"] == 6
    assert dist.get("unresolved_unknown_id", 0) == 0
    assert dist.get("unresolved_malformed_id", 0) == 0
    assert dist.get("conflict_source_ontology_aspect_mismatch", 0) == 0

    # 4. MoonProt specific verification
    moonprot_rows = [r for r in derived_rows if r["source_id"] == "SRC_MOONPROT"]
    assert len(moonprot_rows) == 141
    # Check that all MoonProt rows preserve source_declared_aspect as None
    for r in moonprot_rows:
        assert r["source_declared_aspect"] is None

    # 5. Deterministic serialization check
    with tempfile.TemporaryDirectory() as tmpdir:
        out1 = Path(tmpdir) / "run1.csv"
        out2 = Path(tmpdir) / "run2.csv"
        hash1 = write_derived_source_go_aspects_csv(derived_rows, out1)
        hash2 = write_derived_source_go_aspects_csv(derived_rows, out2)
        assert hash1 == hash2
        assert out1.read_bytes() == out2.read_bytes()
