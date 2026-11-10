"""Unit tests for PlantMP functional claims and coverage adapter.

Exercises src/mfp_bibliography/functional_claims_plantmp.py directly against:
1. Real-source-derived extract (tests/fixtures/functional_claims_plantmp/plantmp_real_extract.csv).
2. Synthetic edge cases (tests/fixtures/functional_claims_plantmp/plantmp_synthetic_edge_cases.csv).

Verifies contract compliance, schema validation, reference preservation,
multiplicity preservation, native role preservation, BP/MF grouping without
assuming independent functions, curation tier policy handling (confirmed -> curated,
likely -> unresolved / excluded_likely, predicted -> predicted), source GO annotations
with unavailable metadata remaining null, no CC inference, and no triplet construction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from mfp_bibliography.normalization import make_protein_id_uniprot
from mfp_bibliography.functional_claims_plantmp import (
    DEFAULT_RAW_FILE_PATH,
    EXTRACTION_METHOD,
    PLANTMP_FIELD_PAIRS,
    SOURCE_ID,
    SOURCE_SUFFIX,
    PlantMPGOAnnotation,
    derive_plantmp_claim_id,
    derive_source_go_annotation_id,
    extract_claims_from_plantmp_row,
    extract_plantmp_claims_from_file,
    extract_plantmp_row_records,
    extract_plantmp_slice_from_file,
    format_plantmp_go_terms,
    format_plantmp_reference,
    group_claims_by_role,
    load_plantmp_catalog_lookup,
    parse_plantmp_go_field,
    resolve_plantmp_assertion_type,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_claims.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_coverage.schema.json"
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_go_annotations.schema.json"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "functional_claims_plantmp"
REAL_EXTRACT_CSV = FIXTURES_DIR / "plantmp_real_extract.csv"
EDGE_CASES_CSV = FIXTURES_DIR / "plantmp_synthetic_edge_cases.csv"

# Synthetic catalog lookup backing the synthetic edge cases fixture:
# Maps order -> deterministic protein_id for synthetic accessions P11111..P99999.
# Note: Record 6 (order 6, INVALID_ACC) is uncataloged and unresolvable.
SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP = {
    f"plantmp_order_{i}": make_protein_id_uniprot(f"P{i}{i}{i}{i}{i}")
    for i in (1, 2, 3, 4, 5, 7, 8, 9)
}


@pytest.fixture
def claims_validator() -> Draft202012Validator:
    with CLAIMS_SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def coverage_validator() -> Draft202012Validator:
    with COVERAGE_SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def annotations_validator() -> Draft202012Validator:
    with ANNOTATIONS_SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


# -----------------------------------------------------------------------------
# Unit Tests for Helper Functions
# -----------------------------------------------------------------------------

def test_derive_plantmp_claim_id_determinism() -> None:
    """Verify claim_id derivation is deterministic and format-compliant."""
    id_1 = derive_plantmp_claim_id("plantmp_order_1", 0, "canonical_function_bp")
    id_2 = derive_plantmp_claim_id("plantmp_order_1", 0, "canonical_function_bp")
    id_3 = derive_plantmp_claim_id("plantmp_order_1", 1, "canonical_function_mf")
    id_4 = derive_plantmp_claim_id("plantmp_order_2", 0, "canonical_function_bp")

    assert id_1 == id_2
    assert id_1 != id_3
    assert id_1 != id_4
    assert id_1.startswith(f"MFP:FC:{SOURCE_SUFFIX}:")
    assert len(id_1.split(":")[-1]) == 16


def test_derive_source_go_annotation_id_determinism() -> None:
    """Verify annotation_id derivation is deterministic and format-compliant."""
    aid_1 = derive_source_go_annotation_id("plantmp_order_1", "go_canonical_bp", 0, "GO:0042254")
    aid_2 = derive_source_go_annotation_id("plantmp_order_1", "go_canonical_bp", 0, "GO:0042254")
    aid_3 = derive_source_go_annotation_id("plantmp_order_1", "go_canonical_bp", 1, "GO:0006412")
    aid_4 = derive_source_go_annotation_id("plantmp_order_1", "go_canonical_mf", 0, "GO:0003729")

    assert aid_1 == aid_2
    assert aid_1 != aid_3
    assert aid_1 != aid_4
    assert aid_1.startswith(f"MFP:SGA:{SOURCE_SUFFIX}:")
    assert len(aid_1.split(":")[-1]) == 16


def test_parse_plantmp_go_field() -> None:
    """Verify parsing of PlantMP comma-separated GO terms and aspect prefixes."""
    # 1. Standard BP field with aspect prefix on first token
    raw_bp = "BP 0042254, 0006412, 0006413"
    parsed_bp = parse_plantmp_go_field(raw_bp, default_aspect="BP")
    assert len(parsed_bp) == 3
    assert parsed_bp[0].go_id == "GO:0042254"
    assert parsed_bp[0].aspect == "BP"
    assert parsed_bp[0].raw_text == "BP 0042254"
    assert parsed_bp[1].go_id == "GO:0006412"
    assert parsed_bp[1].aspect == "BP"
    assert parsed_bp[1].raw_text == "0006412"
    assert parsed_bp[2].go_id == "GO:0006413"
    assert parsed_bp[2].aspect == "BP"

    # 2. Standard MF field with aspect prefix
    raw_mf = "MF 0003729, 0019843"
    parsed_mf = parse_plantmp_go_field(raw_mf, default_aspect="MF")
    assert len(parsed_mf) == 2
    assert parsed_mf[0].go_id == "GO:0003729"
    assert parsed_mf[0].aspect == "MF"
    assert parsed_mf[1].go_id == "GO:0019843"
    assert parsed_mf[1].aspect == "MF"

    # 3. Empty text handling
    assert parse_plantmp_go_field("", default_aspect="BP") == []
    assert parse_plantmp_go_field("   ", default_aspect="MF") == []
    assert parse_plantmp_go_field(None, default_aspect="BP") == []


def test_format_plantmp_go_terms() -> None:
    """Verify deduplication and parallel semicolon-space formatting."""
    annotations = [
        PlantMPGOAnnotation(go_id="GO:0042254", aspect="BP", raw_text="BP 0042254"),
        PlantMPGOAnnotation(go_id="GO:0006412", aspect="BP", raw_text="0006412"),
        PlantMPGOAnnotation(go_id="GO:0042254", aspect="BP", raw_text="0042254"),  # duplicate
    ]
    go_ids, aspects = format_plantmp_go_terms(annotations)
    assert go_ids == "GO:0042254; GO:0006412"
    assert aspects == "BP; BP"

    # Empty list
    empty_ids, empty_aspects = format_plantmp_go_terms([])
    assert empty_ids is None
    assert empty_aspects is None


def test_format_plantmp_reference_exact_preservation() -> None:
    """Verify exact reference preservation without artificial prefixing."""
    # Standard numeric PMID survives without synthetic 'PMID:' prefix
    ref_1, note_1 = format_plantmp_reference("7913892")
    assert ref_1 == "7913892"
    assert note_1 is None

    # Delimiter-bearing numeric string survives exactly
    ref_2, note_2 = format_plantmp_reference("11111111, 22222222")
    assert ref_2 == "11111111, 22222222"
    assert note_2 is None

    # Non-numeric annotated reference survives with anomaly note
    ref_3, note_3 = format_plantmp_reference("26638082 (Homolog of POT7)")
    assert ref_3 == "26638082 (Homolog of POT7)"
    assert note_3 == "anomalous_reference: 26638082 (Homolog of POT7)"

    ref_4, note_4 = format_plantmp_reference("Predicted in 23835195")
    assert ref_4 == "Predicted in 23835195"
    assert note_4 == "anomalous_reference: Predicted in 23835195"

    # Empty reference
    assert format_plantmp_reference("") == (None, None)
    assert format_plantmp_reference(None) == (None, None)


def test_resolve_plantmp_assertion_type_policy() -> None:
    """Verify curation tier policy resolution per R-NORM-04 and claim policy."""
    # 1. Confirmed maps to curated
    assert_type, note = resolve_plantmp_assertion_type("confirmed")
    assert assert_type == "curated"
    assert note == "source_type: confirmed"

    # 2. Predicted maps to predicted
    assert_type, note = resolve_plantmp_assertion_type("predicted")
    assert assert_type == "predicted"
    assert note == "source_type: predicted"

    # 3. Likely maps to unresolved (policy excluded_likely; NEVER silently mapped to curated)
    assert_type, note = resolve_plantmp_assertion_type("likely")
    assert assert_type == "unresolved"
    assert "source_type: likely" in note
    assert "policy_status: excluded_likely" in note

    # 4. Unknown / disputed / empty maps to unresolved
    assert_type, note = resolve_plantmp_assertion_type("disputed")
    assert assert_type == "unresolved"
    assert "source_type: disputed" in note
    assert "policy_status: unresolved" in note

    assert_type, note = resolve_plantmp_assertion_type("")
    assert assert_type == "unresolved"
    assert "source_type: unknown" in note


# -----------------------------------------------------------------------------
# Tests on Real-Source-Derived Fixture
# -----------------------------------------------------------------------------

def test_real_extract_claims_and_coverage_schemas(
    claims_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Exercise adapter against real PlantMP 7-row extract and assert schema validity."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    assert len(coverage) == 7
    assert len(claims) == 20
    assert len(annotations) == 83

    # Schema validation for all emitted records
    for claim in claims:
        claims_validator.validate(claim)
    for ann in annotations:
        annotations_validator.validate(ann)
    for cov in coverage:
        coverage_validator.validate(cov)


def test_real_extract_canonical_moonlighting_preservation() -> None:
    """Verify source-native role preservation and field-level raw claim fields."""
    claims, _, _ = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    valid_roles = {"canonical", "moonlighting"}
    valid_raw_fields = {
        "canonical_function_bp",
        "canonical_function_mf",
        "moonlighting_function_bp",
        "moonlighting_function_mf",
    }

    for claim in claims:
        assert claim["claim_role_raw"] in valid_roles
        assert claim["raw_claim_field"] in valid_raw_fields
        assert len(claim["raw_claim_value"]) > 0
        assert claim["claim_status"] == "valid"
        assert claim["extraction_method"] == EXTRACTION_METHOD
        assert claim["source_id"] == SOURCE_ID


def test_real_extract_bpmf_grouping_no_independent_function_assumption() -> None:
    """Verify BP and MF grouping under native roles without assuming independent functions."""
    claims, _, _ = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    # 1. Check helper function groups correctly
    grouped = group_claims_by_role(claims)
    assert set(grouped.keys()) == {"canonical", "moonlighting"}

    # 2. Check Order 1: has 2 canonical claims (BP and MF) and 1 moonlighting claim (BP)
    order_1_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_1"]
    assert len(order_1_claims) == 3
    order_1_grouped = group_claims_by_role(order_1_claims)
    assert len(order_1_grouped["canonical"]) == 2  # BP + MF facets
    assert len(order_1_grouped["moonlighting"]) == 1  # BP facet

    # Invariant: Having both BP and MF statements for 'canonical' role does NOT
    # prove two independent biological functions; they are pre-partitioned aspects
    canon_fields = {c["raw_claim_field"] for c in order_1_grouped["canonical"]}
    assert canon_fields == {"canonical_function_bp", "canonical_function_mf"}

    # 3. Check Order 5: all 4 fields populated (2 canonical + 2 moonlighting)
    order_5_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_5"]
    assert len(order_5_claims) == 4
    order_5_grouped = group_claims_by_role(order_5_claims)
    assert len(order_5_grouped["canonical"]) == 2
    assert len(order_5_grouped["moonlighting"]) == 2


def test_real_extract_native_status_and_policy_handling() -> None:
    """Verify native status handling: confirmed -> curated, likely -> unresolved, predicted -> predicted."""
    claims, _, coverage = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    # Order 1 (confirmed) -> claim_assertion_type = 'curated'
    order_1_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_1"]
    for c in order_1_claims:
        assert c["claim_assertion_type"] == "curated"
        assert "source_type: confirmed" in c["notes"]

    # Order 64 (likely) -> claim_assertion_type = 'unresolved' (policy excluded_likely)
    # CRUCIAL: 'likely' must NEVER be silently mapped to 'curated'
    order_64_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_64"]
    assert len(order_64_claims) == 2  # canonical_function_mf and moonlighting_function_mf
    for c in order_64_claims:
        assert c["claim_assertion_type"] == "unresolved"
        assert "source_type: likely" in c["notes"]
        assert "policy_status: excluded_likely" in c["notes"]

    # Order 68 (likely) -> claim_assertion_type = 'unresolved'
    order_68_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_68"]
    for c in order_68_claims:
        assert c["claim_assertion_type"] == "unresolved"
        assert "source_type: likely" in c["notes"]

    # Order 75 (predicted) -> claim_assertion_type = 'predicted'
    order_75_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_75"]
    assert len(order_75_claims) == 2  # canonical_function_mf and moonlighting_function_mf
    for c in order_75_claims:
        assert c["claim_assertion_type"] == "predicted"
        assert "source_type: predicted" in c["notes"]


def test_real_extract_record_level_references() -> None:
    """Verify that pubmed_id remains at record level and is NEVER promoted to claim level."""
    claims, _, _ = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    for claim in claims:
        # Crucial invariant: PlantMP references apply at record level
        assert claim["linked_reference_ids"] is None
        assert claim["record_reference_ids"] is not None

    # Check Order 1: standard numeric PMID
    order_1_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_1"]
    for c in order_1_claims:
        assert c["record_reference_ids"] == "7913892"

    # Check Order 64: non-numeric annotated reference
    order_64_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_64"]
    for c in order_64_claims:
        assert c["record_reference_ids"] == "26638082 (Homolog of POT7)"
        assert "anomalous_reference: 26638082 (Homolog of POT7)" in c["notes"]

    # Check Order 75: non-numeric textual reference
    order_75_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_75"]
    for c in order_75_claims:
        assert c["record_reference_ids"] == "Predicted in 23835195"
        assert "anomalous_reference: Predicted in 23835195" in c["notes"]


def test_real_extract_missing_metadata_null() -> None:
    """Verify that unavailable metadata fields remain null, not copied or invented."""
    claims, annotations, _ = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    # 1. Claims lack EC numbers in PlantMP
    for c in claims:
        assert c["source_ec_number"] is None

    # 2. PlantMP GO annotations lack term descriptions and evidence codes
    for a in annotations:
        assert a["term_name"] is None
        assert a["evidence_raw"] is None
        assert a["notes"] is None


def test_real_extract_no_cc_inference_and_no_triplets() -> None:
    """Verify strict prohibition of CC inference and contextual triplet construction."""
    claims, annotations, _ = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    # 1. In claims, aspects contain only 'BP' and/or 'MF', never 'CC'
    for c in claims:
        if c["source_go_aspects"] is not None:
            aspect_set = set(a.strip() for a in c["source_go_aspects"].split(";"))
            assert "CC" not in aspect_set
            assert aspect_set.issubset({"BP", "MF"})

    # 2. In structured annotations, go_aspect is strictly 'BP' or 'MF'
    for a in annotations:
        assert a["go_aspect"] in ("BP", "MF")
        assert a["go_aspect"] != "CC"


def test_real_extract_accession_normalization_nonbreaking_space() -> None:
    """Verify that raw non-breaking space in accession (Order 2) normalizes to catalog entity."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    order_2_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_2"]
    assert len(order_2_claims) == 3
    # P92980 normalizes to MFP:U:f3d2cc26494101eb
    for c in order_2_claims:
        assert c["protein_id"] == "MFP:U:f3d2cc26494101eb"

    order_2_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_2")
    assert order_2_cov["protein_id"] == "MFP:U:f3d2cc26494101eb"


def test_real_extract_multi_record_shared_accession_ordering() -> None:
    """Verify deterministic total ordering across records sharing the same UniProt accession."""
    claims, _, coverage = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    from mfp_bibliography.normalization import make_protein_id_uniprot

    q8_pid = make_protein_id_uniprot("Q8VYA3")
    # Order 62 and Order 68 both share Q8VYA3
    q8_cov = [c for c in coverage if c["protein_id"] == q8_pid]
    assert len(q8_cov) == 2
    # In coverage, sorted by (protein_id, source_id, source_record_id)
    # plantmp_order_62 must precede plantmp_order_68
    assert q8_cov[0]["source_record_id"] == "plantmp_order_62"
    assert q8_cov[1]["source_record_id"] == "plantmp_order_68"

    q8_claims = [c for c in claims if c["protein_id"] == q8_pid]
    # plantmp_order_62 claims must all precede plantmp_order_68 claims
    seen_68 = False
    for c in q8_claims:
        if c["source_record_id"] == "plantmp_order_68":
            seen_68 = True
        elif seen_68:
            pytest.fail("Found plantmp_order_62 claim after plantmp_order_68 claim")


# -----------------------------------------------------------------------------
# Tests on Synthetic Edge Cases Fixture
# -----------------------------------------------------------------------------

def test_synthetic_edge_cases_schemas_conformance(
    claims_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Exercise synthetic edge cases fixture against JSON schemas.

    Demonstrates that all records (both resolved records and unresolved identity
    records with protein_id = null) conform strictly to JSON schemas under
    the Draft 2020-12 conditional nullability rule.
    """
    claims, annotations, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    assert len(coverage) == 9
    assert len(claims) == 11
    assert len(annotations) == 11

    for claim in claims:
        claims_validator.validate(claim)
    for ann in annotations:
        annotations_validator.validate(ann)
    for cov in coverage:
        coverage_validator.validate(cov)


def test_synthetic_single_statement_preservation() -> None:
    """Verify single-statement entries are preserved without binary slot filling."""
    claims, _, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 1 (P11111): only canonical_function_bp populated
    rec_1_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_1")
    assert rec_1_cov["claims_extracted_count"] == 1
    assert rec_1_cov["coverage_status"] == "claims_extracted"
    rec_1_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_1"]
    assert len(rec_1_claims) == 1
    assert rec_1_claims[0]["claim_role_raw"] == "canonical"
    assert rec_1_claims[0]["raw_claim_field"] == "canonical_function_bp"

    # Record 2 (P22222): only moonlighting_function_mf populated
    rec_2_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_2")
    assert rec_2_cov["claims_extracted_count"] == 1
    assert rec_2_cov["coverage_status"] == "claims_extracted"
    rec_2_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_2"]
    assert len(rec_2_claims) == 1
    assert rec_2_claims[0]["claim_role_raw"] == "moonlighting"
    assert rec_2_claims[0]["raw_claim_field"] == "moonlighting_function_mf"


def test_synthetic_text_without_go() -> None:
    """Verify entries with text statements but no GO terms emit valid claims with null GO."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 3 (P33333): 2 text statements (canonical BP and MF), no GO annotations
    rec_3_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_3"]
    assert len(rec_3_claims) == 2
    for c in rec_3_claims:
        assert c["source_go_ids"] is None
        assert c["source_go_aspects"] is None

    rec_3_anns = [a for a in annotations if a["source_record_id"] == "plantmp_order_3"]
    assert len(rec_3_anns) == 0


def test_synthetic_no_statement_record_denominator_coverage() -> None:
    """Verify 100% denominator coverage on records with no discrete functional statements."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 4 (P44444): all text and GO fields empty
    rec_4_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_4")
    assert rec_4_cov["claims_extracted_count"] == 0
    assert rec_4_cov["coverage_status"] == "no_discrete_functional_statements"

    rec_4_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_4"]
    assert len(rec_4_claims) == 0
    rec_4_anns = [a for a in annotations if a["source_record_id"] == "plantmp_order_4"]
    assert len(rec_4_anns) == 0


def test_synthetic_function_text_empty_with_explicit_go() -> None:
    """Verify handling when text is empty but GO annotations are present.

    In Record 5 (P55555):
    - All 4 function text fields are empty.
    - go_canonical_bp has GO:0006412.
    - go_moonlighting_mf has GO:0003729.
    Invariants:
    1. Zero fake claims fabricated in functional_claims (claims_extracted_count = 0).
    2. Structured source_go_annotations emitted with claim_id = null.
    3. functional_coverage notes unextracted annotations without text.
    """
    claims, annotations, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    rec_5_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_5"]
    assert len(rec_5_claims) == 0

    rec_5_anns = [a for a in annotations if a["source_record_id"] == "plantmp_order_5"]
    assert len(rec_5_anns) == 2
    for a in rec_5_anns:
        assert a["claim_id"] is None
        assert a["protein_id"].startswith("MFP:U:")

    rec_5_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_5")
    assert rec_5_cov["claims_extracted_count"] == 0
    assert rec_5_cov["coverage_status"] == "no_discrete_functional_statements"
    assert "unextracted_annotations_without_text" in rec_5_cov["notes"]
    assert "GO:0006412" in rec_5_cov["notes"]
    assert "GO:0003729" in rec_5_cov["notes"]


def test_synthetic_unresolved_identity() -> None:
    """Verify invalid UniProt accession triggers unresolved_identity coverage with protein_id = None."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 6 (INVALID_ACC):
    rec_6_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_6")
    assert rec_6_cov["claims_extracted_count"] == 0
    assert rec_6_cov["coverage_status"] == "unresolved_identity"
    assert rec_6_cov["protein_id"] is None
    assert "Unresolved UniProt accession" in (rec_6_cov["notes"] or "") or "Missing or malformed" in (rec_6_cov["notes"] or "")

    rec_6_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_6"]
    assert len(rec_6_claims) == 0
    rec_6_anns = [a for a in annotations if a["source_record_id"] == "plantmp_order_6"]
    assert len(rec_6_anns) == 0


def test_synthetic_unmapped_native_status() -> None:
    """Verify unmapped native status (disputed) maps to unresolved."""
    claims, _, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 7: type = 'disputed'
    rec_7_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_7"]
    assert len(rec_7_claims) == 2
    for c in rec_7_claims:
        assert c["claim_assertion_type"] == "unresolved"
        assert "source_type: disputed" in c["notes"]


def test_synthetic_multi_reference_preservation() -> None:
    """Verify comma-separated PMIDs preserved exactly in record_reference_ids."""
    claims, _, _ = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 8: pubmed_id = '11111111, 22222222'
    rec_8_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_8"]
    assert len(rec_8_claims) == 2
    for c in rec_8_claims:
        assert c["record_reference_ids"] == "11111111, 22222222"
        assert c["linked_reference_ids"] is None


def test_synthetic_likely_annotated_reference() -> None:
    """Verify likely status with annotated reference maps to unresolved and preserves string."""
    claims, _, _ = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV, catalog_lookup=SYNTHETIC_EDGE_CASES_CATALOG_LOOKUP
    )

    # Record 9: type = 'likely', pubmed_id = '21088220 (Homolog of PEPR1)'
    rec_9_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_9"]
    assert len(rec_9_claims) == 3
    for c in rec_9_claims:
        assert c["claim_assertion_type"] == "unresolved"
        assert "source_type: likely" in c["notes"]
        assert c["record_reference_ids"] == "21088220 (Homolog of PEPR1)"
        assert "anomalous_reference" in c["notes"]


# -----------------------------------------------------------------------------
# Tests for Catalog Integration, Foreign Keys, Determinism, Ordering
# -----------------------------------------------------------------------------

def test_catalog_lookup_integration() -> None:
    """Verify supplied catalog_lookup resolves records when linkage agrees."""
    pid_1 = make_protein_id_uniprot("P11111")
    custom_lookup = {
        "plantmp_order_1": pid_1,
    }
    claims, _, coverage = extract_plantmp_slice_from_file(
        EDGE_CASES_CSV,
        catalog_lookup=custom_lookup,
    )

    rec_1_claims = [c for c in claims if c["source_record_id"] == "plantmp_order_1"]
    assert len(rec_1_claims) == 1
    assert rec_1_claims[0]["protein_id"] == pid_1

    rec_1_cov = next(c for c in coverage if c["source_record_id"] == "plantmp_order_1")
    assert rec_1_cov["protein_id"] == pid_1


def test_foreign_key_linkages() -> None:
    """Verify foreign key linkages between claims, annotations, and coverage."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)
    claims_by_id = {c["claim_id"]: c for c in claims}
    cov_by_srid = {c["source_record_id"]: c for c in coverage}

    # 1. Claims foreign keys
    for c in claims:
        assert c["source_record_id"] in cov_by_srid
        cov_rec = cov_by_srid[c["source_record_id"]]
        assert cov_rec["protein_id"] == c["protein_id"]

    # 2. Annotations foreign keys
    for a in annotations:
        assert a["source_record_id"] in cov_by_srid
        cov_rec = cov_by_srid[a["source_record_id"]]
        assert cov_rec["protein_id"] == a["protein_id"]

        # If linked to a claim, claim must exist and match protein/source_record
        if a["claim_id"] is not None:
            assert a["claim_id"] in claims_by_id
            linked_claim = claims_by_id[a["claim_id"]]
            assert linked_claim["protein_id"] == a["protein_id"]
            assert linked_claim["source_record_id"] == a["source_record_id"]


def test_total_ordering_claims_annotations_coverage() -> None:
    """Verify total deterministic tie-breaking sort order across all emitted records."""
    claims, annotations, coverage = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    # 1. Claims: (protein_id ASC, source_id ASC, source_record_id ASC, claim_index ASC, claim_id ASC)
    claim_keys = [
        (c["protein_id"], c["source_id"], c["source_record_id"], c["claim_index"], c["claim_id"])
        for c in claims
    ]
    assert claim_keys == sorted(claim_keys), "Claims not sorted by total tie-breaking rule"

    # 2. Annotations: (protein_id ASC, source_id ASC, source_record_id ASC, source_field ASC, annotation_index ASC, annotation_id ASC)
    ann_keys = [
        (
            a["protein_id"],
            a["source_id"],
            a["source_record_id"],
            a["source_field"],
            a["annotation_index"],
            a["annotation_id"],
        )
        for a in annotations
    ]
    assert ann_keys == sorted(ann_keys), "Annotations not sorted by total tie-breaking rule"

    # 3. Coverage: (protein_id ASC, source_id ASC, source_record_id ASC)
    cov_keys = [(c["protein_id"], c["source_id"], c["source_record_id"]) for c in coverage]
    assert cov_keys == sorted(cov_keys), "Coverage not sorted by total tie-breaking rule"


def test_determinism_across_runs() -> None:
    """Verify independent repeated extractions produce identical outputs."""
    claims_1, anns_1, cov_1 = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)
    claims_2, anns_2, cov_2 = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)

    assert claims_1 == claims_2
    assert anns_1 == anns_2
    assert cov_1 == cov_2


def test_backward_compatibility_interface() -> None:
    """Verify extract_plantmp_claims_from_file returns 2 elements by default and 3 when requested."""
    # Default 2-element unpack
    res2 = extract_plantmp_claims_from_file(REAL_EXTRACT_CSV)
    assert len(res2) == 2
    claims2, cov2 = res2
    assert isinstance(claims2, list)
    assert isinstance(cov2, list)

    # Explicit return_annotations=True
    res3 = extract_plantmp_claims_from_file(REAL_EXTRACT_CSV, return_annotations=True)
    assert len(res3) == 3
    claims3, anns3, cov3 = res3
    assert len(claims3) == len(claims2)
    assert len(cov3) == len(cov2)
    assert len(anns3) > 0

    # Dedicated slice helper
    res_slice = extract_plantmp_slice_from_file(REAL_EXTRACT_CSV)
    assert len(res_slice) == 3
    assert res_slice[0] == claims3
    assert res_slice[1] == anns3
    assert res_slice[2] == cov3


def test_extract_plantmp_row_records() -> None:
    """Verify single-row convenience extractor returns (claims, annotations, coverage)."""
    raw_row = {
        "order": "1",
        "protein name, gene": "40S ribosomal protein S18, RPS18A",
        "uniport_id": "P34788",
        "canonical_function_bp": "translation initiation",
        "canonical_function_mf": "RNA binding",
        "moonlighting_function_bp": "leaf development",
        "moonlighting_function_mf": "",
        "go_canonical_bp": "BP 0042254",
        "go_canonical_mf": "MF 0003729",
        "go_moonlighting_bp": "BP 0008150",
        "go_moonlighting_mf": "",
        "plant_species": "Arabidopsis thaliana",
        "pubmed_id": "7913892",
        "type": "confirmed",
    }
    catalog = load_plantmp_catalog_lookup()
    claims, anns, cov = extract_plantmp_row_records(raw_row, row_index=1, catalog_lookup=catalog)
    assert len(claims) == 3
    assert len(anns) == 3
    assert cov["claims_extracted_count"] == 3
    assert cov["coverage_status"] == "claims_extracted"


# -----------------------------------------------------------------------------
# Focused Negative Tests & Identity Contract Blocker Verification
# -----------------------------------------------------------------------------

def test_negative_missing_accession() -> None:
    """Verify row with missing UniProt accession emits unresolved_identity with protein_id = None."""
    row = {
        "order": "991",
        "protein name, gene": "Missing accession protein",
        "uniport_id": "",
        "canonical_function_bp": "some process",
        "pubmed_id": "12345678",
        "type": "confirmed",
    }
    claims, anns, cov = extract_plantmp_row_records(row, row_index=991)
    assert len(claims) == 0
    assert len(anns) == 0
    assert cov["coverage_status"] == "unresolved_identity"
    assert cov["protein_id"] is None
    assert cov["claims_extracted_count"] == 0
    assert "Missing or malformed" in (cov["notes"] or "")


def test_negative_malformed_accession() -> None:
    """Verify row with malformed accession emits unresolved_identity with protein_id = None."""
    row = {
        "order": "992",
        "protein name, gene": "Malformed accession protein",
        "uniport_id": "NOT_A_VALID_ACCESSION",
        "canonical_function_bp": "some process",
        "pubmed_id": "12345678",
        "type": "confirmed",
    }
    claims, anns, cov = extract_plantmp_row_records(row, row_index=992)
    assert len(claims) == 0
    assert len(anns) == 0
    assert cov["coverage_status"] == "unresolved_identity"
    assert cov["protein_id"] is None
    assert cov["claims_extracted_count"] == 0
    assert "Missing or malformed" in (cov["notes"] or "")


def test_negative_valid_accession_absent_from_catalog() -> None:
    """Verify syntactically valid accession absent from supplied catalog is NOT silently promoted."""
    catalog_lookup = {
        "plantmp_order_1": make_protein_id_uniprot("P34788"),
    }
    # Row 993 has a valid UniProt accession 'P12345', but its source_record_id is NOT in catalog_lookup
    row = {
        "order": "993",
        "protein name, gene": "Absent from catalog protein",
        "uniport_id": "P12345",
        "canonical_function_bp": "some process",
        "pubmed_id": "12345678",
        "type": "confirmed",
    }
    claims, anns, cov = extract_plantmp_row_records(
        row, row_index=993, catalog_lookup=catalog_lookup
    )
    assert len(claims) == 0
    assert len(anns) == 0
    assert cov["coverage_status"] == "unresolved_identity"
    assert cov["protein_id"] is None
    assert cov["claims_extracted_count"] == 0
    assert "absent from supplied catalog" in (cov["notes"] or "")
    assert "not promoted" in (cov["notes"] or "")


def test_negative_mismatched_source_record_linkage() -> None:
    """Verify mismatched catalog linkage (catalog protein_id != derived protein_id) is rejected."""
    catalog_lookup = {
        "plantmp_order_994": "MFP:U:0000000000000001",
    }
    row = {
        "order": "994",
        "protein name, gene": "Mismatched linkage protein",
        "uniport_id": "P34788",
        "canonical_function_bp": "translation initiation",
        "pubmed_id": "7913892",
        "type": "confirmed",
    }
    claims, anns, cov = extract_plantmp_row_records(
        row, row_index=994, catalog_lookup=catalog_lookup
    )
    assert len(claims) == 0
    assert len(anns) == 0
    assert cov["coverage_status"] == "unresolved_identity"
    assert cov["protein_id"] is None
    assert cov["claims_extracted_count"] == 0
    assert "Mismatched source-record linkage" in (cov["notes"] or "")


def test_negative_multiple_unresolved_records_not_collapsed() -> None:
    """Verify multiple unresolved records are not collapsed into a single fake entity."""
    row_a = {
        "order": "995",
        "protein name, gene": "Unresolved protein A",
        "uniport_id": "INVALID_A",
        "canonical_function_bp": "process A",
        "type": "confirmed",
    }
    row_b = {
        "order": "996",
        "protein name, gene": "Unresolved protein B",
        "uniport_id": "INVALID_B",
        "canonical_function_bp": "process B",
        "type": "confirmed",
    }
    _, _, cov_a = extract_plantmp_row_records(row_a, row_index=995)
    _, _, cov_b = extract_plantmp_row_records(row_b, row_index=996)

    assert cov_a["source_record_id"] == "plantmp_order_995"
    assert cov_b["source_record_id"] == "plantmp_order_996"
    assert cov_a["protein_id"] is None
    assert cov_b["protein_id"] is None
    assert cov_a["source_record_id"] != cov_b["source_record_id"]
    # Verify no fake sentinel entity was assigned
    assert cov_a["protein_id"] != "MFP:U:0000000000000000"
    assert cov_b["protein_id"] != "MFP:U:0000000000000000"


def test_real_catalog_lookup_loading() -> None:
    """Verify load_plantmp_catalog_lookup loads all 112 records from real catalog."""
    lookup = load_plantmp_catalog_lookup()
    assert len(lookup) == 112
    assert "plantmp_order_1" in lookup
    assert lookup["plantmp_order_1"] == make_protein_id_uniprot("P34788")
    assert "plantmp_order_62" in lookup
    assert "plantmp_order_68" in lookup
    # Duplicate source records legitimately share protein entity
    assert lookup["plantmp_order_62"] == lookup["plantmp_order_68"]


def test_coverage_schema_conditional_nullability_plantmp(
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify coverage records adhere to conditional nullability under Draft 2020-12.

    Valid cases:
    - unresolved_identity + protein_id: null
    - claims_extracted (or other resolved status) + catalog-backed protein_id

    Invalid syntax cases:
    - unresolved_identity + non-null protein_id
    - claims_extracted + protein_id null
    - missing protein_id
    - empty string protein_id
    - malformed non-null protein_id
    """
    # 1. Valid: unresolved_identity + protein_id null
    row_unres = {
        "order": "997",
        "protein name, gene": "Unresolved protein",
        "uniport_id": "",
        "canonical_function_bp": "process",
        "type": "confirmed",
    }
    _, _, cov_unres = extract_plantmp_row_records(row_unres, row_index=997)
    assert cov_unres["coverage_status"] == "unresolved_identity"
    assert cov_unres["protein_id"] is None
    coverage_validator.validate(cov_unres)

    # 2. Valid: resolved status + catalog-backed protein_id
    catalog = load_plantmp_catalog_lookup()
    row_res = {
        "order": "1",
        "protein name, gene": "40S ribosomal protein S18, RPS18A",
        "uniport_id": "P34788",
        "canonical_function_bp": "translation initiation",
        "canonical_function_mf": "RNA binding",
        "moonlighting_function_bp": "leaf development",
        "moonlighting_function_mf": "",
        "go_canonical_bp": "BP 0042254",
        "go_canonical_mf": "MF 0003729",
        "go_moonlighting_bp": "BP 0008150",
        "go_moonlighting_mf": "",
        "plant_species": "Arabidopsis thaliana",
        "pubmed_id": "7913892",
        "type": "confirmed",
    }
    _, _, cov_res = extract_plantmp_row_records(row_res, row_index=1, catalog_lookup=catalog)
    assert cov_res["coverage_status"] == "claims_extracted"
    assert cov_res["protein_id"] == make_protein_id_uniprot("P34788")
    coverage_validator.validate(cov_res)

    # Invalid 1: unresolved_identity + non-null protein_id
    bad_unres_nonnull = dict(cov_unres, protein_id=make_protein_id_uniprot("P34788"))
    with pytest.raises(Exception):
        coverage_validator.validate(bad_unres_nonnull)

    # Invalid 2: resolved status + protein_id null
    bad_res_null = dict(cov_res, protein_id=None)
    with pytest.raises(Exception):
        coverage_validator.validate(bad_res_null)

    # Invalid 3: missing protein_id
    bad_missing = {k: v for k, v in cov_res.items() if k != "protein_id"}
    with pytest.raises(Exception):
        coverage_validator.validate(bad_missing)

    # Invalid 4: empty protein_id
    bad_empty = dict(cov_res, protein_id="")
    with pytest.raises(Exception):
        coverage_validator.validate(bad_empty)

    # Invalid 5: malformed non-null protein_id
    bad_malformed = dict(cov_res, protein_id="INVALID_FORMAT_ID")
    with pytest.raises(Exception):
        coverage_validator.validate(bad_malformed)


def test_coverage_dataset_level_referential_integrity_rejection(tmp_path: Path) -> None:
    """Verify referential integrity rejection of well-formed IDs absent from catalog.

    This test explicitly demonstrates that referential-integrity validation
    is separate and distinct from schema syntax validation. A syntactically
    valid MFP ID passes schema validation, but MUST be rejected at dataset-level
    if the ID is missing from the catalog or mismatched with source records.
    """
    from tests.test_functional_contracts import assert_catalog_referential_integrity

    proteins_path = tmp_path / "mfp_proteins.csv"
    proteins_path.write_text(
        "protein_id,uniprot_accession\n"
        f"{make_protein_id_uniprot('P34788')},P34788\n",
        encoding="utf-8",
    )
    records_path = tmp_path / "mfp_source_records.csv"
    records_path.write_text(
        "source_record_id,source_id,protein_id\n"
        f"plantmp_order_1,plantmp,{make_protein_id_uniprot('P34788')}\n",
        encoding="utf-8",
    )

    # 1. Valid honest unresolved record (protein_id is None) passes referential integrity
    cov_valid_unresolved = [
        {
            "source_id": "plantmp",
            "source_record_id": "plantmp_order_999",
            "protein_id": None,
            "coverage_status": "unresolved_identity",
            "claims_extracted_count": 0,
            "notes": "Unresolved accession",
        }
    ]
    assert_catalog_referential_integrity([], cov_valid_unresolved, proteins_path, records_path)

    # 2. Well-formed ID absent from the synthetic catalog -> rejected by dataset-level validation
    well_formed_absent_id = make_protein_id_uniprot("P99999")
    cov_absent_id = [
        {
            "source_id": "plantmp",
            "source_record_id": "plantmp_order_999",
            "protein_id": well_formed_absent_id,
            "coverage_status": "claims_extracted",
            "claims_extracted_count": 1,
            "notes": None,
        }
    ]
    with pytest.raises(ValueError, match="references unknown protein_id"):
        assert_catalog_referential_integrity([], cov_absent_id, proteins_path, records_path)


def test_plantmp_adapter_unanchored_mode_behavior() -> None:
    """Document and test behavior of PlantMP adapter with and without catalog_lookup.

    - Default (catalog_lookup=None, allow_unanchored=False): row extractor refuses to silently
      promote valid-looking accession; returns unresolved_identity with protein_id=None.
    - Explicit unanchored (allow_unanchored=True): row extractor syntactically derives protein_id
      without requiring catalog backing (used for isolated syntax testing).
    - Catalog-anchored (catalog_lookup provided): row extractor verifies accession in catalog.
      If absent, returns unresolved_identity with protein_id=None.
    """
    raw_row = {
        "order": "1",
        "protein name, gene": "40S ribosomal protein S18, RPS18A",
        "uniport_id": "P34788",
        "canonical_function_bp": "translation initiation",
        "canonical_function_mf": "RNA binding",
        "moonlighting_function_bp": "leaf development",
        "moonlighting_function_mf": "",
        "go_canonical_bp": "BP 0042254",
        "go_canonical_mf": "MF 0003729",
        "go_moonlighting_bp": "BP 0008150",
        "go_moonlighting_mf": "",
        "plant_species": "Arabidopsis thaliana",
        "pubmed_id": "7913892",
        "type": "confirmed",
    }

    # 1. Default (no catalog_lookup, allow_unanchored=False): strictly unresolved
    claims_no_cat, _, cov_no_cat = extract_plantmp_row_records(
        raw_row, row_index=1, allow_unanchored=False
    )
    assert cov_no_cat["coverage_status"] == "unresolved_identity"
    assert cov_no_cat["protein_id"] is None
    assert len(claims_no_cat) == 0

    # 2. Explicit unanchored (allow_unanchored=True): derives synthetic protein_id
    claims_unanchored, _, cov_unanchored = extract_plantmp_row_records(
        raw_row, row_index=1, allow_unanchored=True
    )
    assert cov_unanchored["coverage_status"] == "claims_extracted"
    assert cov_unanchored["protein_id"] == make_protein_id_uniprot("P34788")
    assert len(claims_unanchored) == 3

    # 3. Catalog-anchored: found in catalog -> resolved
    catalog = {"plantmp_order_1": make_protein_id_uniprot("P34788")}
    claims_cat, _, cov_cat = extract_plantmp_row_records(
        raw_row, row_index=1, catalog_lookup=catalog
    )
    assert cov_cat["coverage_status"] == "claims_extracted"
    assert cov_cat["protein_id"] == make_protein_id_uniprot("P34788")
    assert len(claims_cat) == 3

    # 4. Catalog-anchored: absent from catalog -> unresolved
    empty_catalog: dict[str, str] = {}
    claims_miss, _, cov_miss = extract_plantmp_row_records(
        raw_row, row_index=1, catalog_lookup=empty_catalog
    )
    assert cov_miss["coverage_status"] == "unresolved_identity"
    assert cov_miss["protein_id"] is None
    assert len(claims_miss) == 0
