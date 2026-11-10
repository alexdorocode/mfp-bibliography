"""Unit tests for MultitaskProtDB-II functional claims adapter.

Exercises src/mfp_bibliography/functional_claims_multitask.py directly against:
1. Real-source-derived extract (tests/fixtures/functional_claims_multitask/multitask_real_extract.csv).
2. Synthetic edge cases (tests/fixtures/functional_claims_multitask/multitask_synthetic_edge_cases.csv).

Verifies contract compliance, schema validation, reference preservation,
multiplicity preservation, source-explicit CC preservation in GO_Moon,
structured annotation associations, and missing text with GO data accounting.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from mfp_bibliography.functional_claims_multitask import (
    DEFAULT_RAW_FILE_PATH,
    EXTRACTION_METHOD,
    SOURCE_ID,
    MultitaskGOAnnotation,
    derive_multitask_claim_id,
    derive_source_go_annotation_id,
    extract_claims_from_multitask_row,
    extract_multitask_claims_from_file,
    extract_multitask_row_records,
    extract_multitask_slice_from_file,
    format_multitask_reference,
    parse_multitask_go_annotations,
    parse_multitask_go_terms,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_claims.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_coverage.schema.json"
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_go_annotations.schema.json"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "functional_claims_multitask"
REAL_EXTRACT_CSV = FIXTURES_DIR / "multitask_real_extract.csv"
EDGE_CASES_CSV = FIXTURES_DIR / "multitask_synthetic_edge_cases.csv"


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

def test_derive_multitask_claim_id_determinism() -> None:
    """Verify claim_id derivation is deterministic and format-compliant."""
    id_1 = derive_multitask_claim_id("multitaskprotdb_ii_row_1", 0, "Canonical_Function")
    id_2 = derive_multitask_claim_id("multitaskprotdb_ii_row_1", 0, "Canonical_Function")
    id_3 = derive_multitask_claim_id("multitaskprotdb_ii_row_1", 1, "Moonlighting_function")

    assert id_1 == id_2
    assert id_1 != id_3
    assert id_1.startswith("MFP:FC:MULTITASKPROTDB_II:")
    assert len(id_1.split(":")[-1]) == 16


def test_parse_multitask_go_terms_aspects() -> None:
    """Verify parsing of explicit source aspects (C, F, P) and evidence."""
    raw_go = (
        "GO:0005840; C:ribosome; IEA:UniProtKB-KW.\n"
        "GO:0003735; F:structural constituent of ribosome; IEA:InterPro.\n"
        "GO:0006412; P:translation; IEA:InterPro."
    )
    go_ids, aspects, ev_note = parse_multitask_go_terms(raw_go)
    assert go_ids == "GO:0005840; GO:0003735; GO:0006412"
    assert aspects == "CC; MF; BP"
    assert ev_note is not None
    assert "GO:0005840=IEA:UniProtKB-KW" in ev_note
    assert "GO:0003735=IEA:InterPro" in ev_note

    # Empty text handling
    empty_ids, empty_aspects, empty_ev = parse_multitask_go_terms("")
    assert empty_ids is None
    assert empty_aspects is None
    assert empty_ev is None


def test_structured_go_annotation_associations() -> None:
    """Verify tight binding between GO ID, aspect, term name, and evidence (Check 4)."""
    raw_go = (
        "GO:0005840; C:ribosome; IEA:UniProtKB-KW.\n"
        "GO:0005654; C:nucleoplasm; IDA:HPA.\n"
        "GO:0008150 biological_process"
    )
    annotations = parse_multitask_go_annotations(raw_go)
    assert len(annotations) == 3

    ann_0 = annotations[0]
    assert ann_0.go_id == "GO:0005840"
    assert ann_0.aspect == "CC"
    assert ann_0.term_name == "ribosome"
    assert ann_0.evidence == "IEA:UniProtKB-KW"

    ann_1 = annotations[1]
    assert ann_1.go_id == "GO:0005654"
    assert ann_1.aspect == "CC"
    assert ann_1.term_name == "nucleoplasm"
    assert ann_1.evidence == "IDA:HPA"

    ann_2 = annotations[2]
    assert ann_2.go_id == "GO:0008150"
    assert ann_2.aspect == "BP"
    assert ann_2.evidence is None


def test_format_multitask_reference_exact_preservation() -> None:
    """Verify exact reference preservation without artificial prefixing (Check 2)."""
    # Bare numeric Reference survives exactly without synthetic 'PMID:' prefix
    ref_1, note_1 = format_multitask_reference("24814782")
    assert ref_1 == "24814782"
    assert note_1 is None

    # Delimiter-bearing numeric string survives exactly
    ref_2, note_2 = format_multitask_reference("11111111, 22222222")
    assert ref_2 == "11111111, 22222222"
    assert note_2 is None

    # Non-numeric reference survives exactly with anomaly note
    ref_3, note_3 = format_multitask_reference("HIV-1 infection (omim:600534)")
    assert ref_3 == "HIV-1 infection (omim:600534)"
    assert note_3 == "anomalous_reference: HIV-1 infection (omim:600534)"

    # PDB-like reference survives exactly
    ref_4, note_4 = format_multitask_reference("4ENL")
    assert ref_4 == "4ENL"
    assert note_4 == "anomalous_reference: 4ENL"

    # Empty reference
    ref_5, note_5 = format_multitask_reference("")
    assert ref_5 is None
    assert note_5 is None


# -----------------------------------------------------------------------------
# Tests on Real-Source-Derived Fixture
# -----------------------------------------------------------------------------

def test_real_extract_claims_and_coverage(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Exercise adapter against real MultitaskProtDB-II extracted rows."""
    claims, coverage = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    # 6 real rows extracted (rows 1, 2, 3, 55, 239, 672)
    assert len(coverage) == 6
    # 6 rows with both canonical and moonlighting -> 12 claims
    assert len(claims) == 12

    # Schema validation for all emitted records
    for claim in claims:
        claims_validator.validate(claim)
    for cov in coverage:
        coverage_validator.validate(cov)


def test_real_extract_reference_granularity() -> None:
    """Verify that record references remain unpromoted to claim-specific support."""
    claims, _ = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    for claim in claims:
        # Crucial invariant: MultitaskProtDB-II references are record-level
        assert claim["linked_reference_ids"] is None
        assert claim["record_reference_ids"] is not None


def test_real_extract_native_roles_and_multiplicity() -> None:
    """Verify source-native role preservation and 2 distinct claims per entry."""
    claims, _ = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    roles = {c["claim_role_raw"] for c in claims}
    assert roles == {"Canonical_Function", "Moonlighting_function"}

    for claim in claims:
        assert claim["claim_assertion_type"] == "curated"
        assert claim["claim_status"] == "valid"
        assert claim["extraction_method"] == EXTRACTION_METHOD
        assert claim["source_id"] == SOURCE_ID


def test_real_extract_row_1_aspect_presence() -> None:
    """Verify aspect extraction on Row 1 (A0A059U5R2).

    Canonical has CC, MF, BP. Moonlighting has BP only.
    """
    claims, _ = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    row_1_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_1"]
    assert len(row_1_claims) == 2

    canonical = next(c for c in row_1_claims if c["claim_role_raw"] == "Canonical_Function")
    moonlighting = next(c for c in row_1_claims if c["claim_role_raw"] == "Moonlighting_function")

    # Canonical carries CC, MF, BP
    assert "CC" in canonical["source_go_aspects"]
    assert "MF" in canonical["source_go_aspects"]
    assert "BP" in canonical["source_go_aspects"]

    # Moonlighting carries BP only (CC and MF absent in raw record)
    assert "BP" in moonlighting["source_go_aspects"]
    assert "CC" not in moonlighting["source_go_aspects"]
    assert "MF" not in moonlighting["source_go_aspects"]


def test_real_extract_row_672_explicit_moon_cc() -> None:
    """Verify source-explicit CC preservation in GO_Moon for Row 672 (Check 1).

    In Row 672 (Q9Y3E5, Bit1):
    - Canonical GO has CC (cytosol, membrane, mitochondrion), MF, BP.
    - GO_Moon explicitly contains CC: 'GO:0005654; C:nucleoplasm; IDA:HPA.' alongside MF and BP.
    Invariants:
    1. Canonical CC terms (cytosol, membrane, mitochondrion) are NOT copied to moonlighting claim.
    2. Explicit CC present in GO_Moon (nucleoplasm) IS faithfully preserved in moonlighting claim.
    3. The co-presence of CC, MF, BP in GO_Moon is NOT interpreted as a validated contextual triplet.
    """
    claims, _ = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    row_672_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_6"]
    assert len(row_672_claims) == 2

    canonical = next(c for c in row_672_claims if c["claim_role_raw"] == "Canonical_Function")
    moonlighting = next(c for c in row_672_claims if c["claim_role_raw"] == "Moonlighting_function")

    # 1. Canonical CC contains cytosol (GO:0005829), membrane (GO:0016020), mitochondrion (GO:0005739)
    assert "GO:0005829" in canonical["source_go_ids"]
    assert "GO:0016020" in canonical["source_go_ids"]
    assert "GO:0005739" in canonical["source_go_ids"]

    # 2. Moonlighting DOES NOT contain canonical CC terms
    assert "GO:0005829" not in moonlighting["source_go_ids"]
    assert "GO:0016020" not in moonlighting["source_go_ids"]
    assert "GO:0005739" not in moonlighting["source_go_ids"]

    # 3. Moonlighting FAITHFULLY preserves explicit GO_Moon CC: nucleoplasm (GO:0005654)
    assert "GO:0005654" in moonlighting["source_go_ids"]
    assert "CC" in moonlighting["source_go_aspects"]

    # 4. Moonlighting also preserves MF (GO:0003677) and BP (GO:0006355)
    assert "MF" in moonlighting["source_go_aspects"]
    assert "BP" in moonlighting["source_go_aspects"]


def test_real_extract_row_239_anomalous_reference() -> None:
    """Verify exact preservation of non-numeric reference string in Row 239."""
    claims, coverage = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    row_239_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_5"]
    assert len(row_239_claims) == 2
    for c in row_239_claims:
        # Survives exactly without modification
        assert c["record_reference_ids"] == "HIV-1 and murine leukemia virus infection (omim:600534)"
        assert "anomalous_reference" in c["notes"]


# -----------------------------------------------------------------------------
# Tests on Synthetic Edge Cases
# -----------------------------------------------------------------------------

def test_synthetic_edge_cases(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Exercise edge cases: missing statements, unresolved identity, multi-PMID references."""
    claims, coverage = extract_multitask_claims_from_file(EDGE_CASES_CSV)

    assert len(coverage) == 8
    # Row 1 (1 claim), Row 2 (1 claim), Row 3 (0), Row 4 (0), Row 5 (2 claims), Row 6 (1 claim), Row 7 (0), Row 8 (2 claims)
    assert len(claims) == 7

    for claim in claims:
        claims_validator.validate(claim)
    for cov in coverage:
        coverage_validator.validate(cov)

    # 1. Row 1 has only Canonical_Function
    row_1_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_1")
    assert row_1_cov["claims_extracted_count"] == 1
    assert row_1_cov["coverage_status"] == "claims_extracted"

    # 2. Row 2 has only Moonlighting_function
    row_2_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_2")
    assert row_2_cov["claims_extracted_count"] == 1
    assert row_2_cov["coverage_status"] == "claims_extracted"

    # 3. Row 3 has neither function -> 0 claims, coverage status no_discrete_functional_statements
    row_3_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_3")
    assert row_3_cov["claims_extracted_count"] == 0
    assert row_3_cov["coverage_status"] == "no_discrete_functional_statements"

    # 4. Row 4 has invalid accession -> unresolved_identity, 0 claims, protein_id is None
    row_4_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_4")
    assert row_4_cov["claims_extracted_count"] == 0
    assert row_4_cov["coverage_status"] == "unresolved_identity"
    assert row_4_cov["protein_id"] is None

    # 5. Row 5 has multi-reference string preserved exactly
    row_5_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_5"]
    assert len(row_5_claims) == 2
    for c in row_5_claims:
        assert c["record_reference_ids"] == "11111111, 22222222"

    # 6. Row 8 has repeated GO IDs with distinct evidence
    row_8_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_8")
    assert row_8_cov["claims_extracted_count"] == 2
    assert row_8_cov["coverage_status"] == "claims_extracted"
    row_8_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_8"]
    assert len(row_8_claims) == 2


def test_missing_function_text_with_explicit_go_annotations() -> None:
    """Verify accounting of records with empty text descriptions but populated GO (Check 3).

    In Row 6:
    - Canonical_Function is empty, but GO contains GO:0003824 (catalytic activity).
    - Moonlighting_function is populated.
    Invariants:
    1. Zero fake text claims are fabricated for Canonical_Function.
    2. Exactly 1 claim is extracted (for Moonlighting_function).
    3. coverage['notes'] explicitly accounts for unextracted GO annotations.
    """
    claims, coverage = extract_multitask_claims_from_file(EDGE_CASES_CSV)

    row_6_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_6")
    assert row_6_cov["claims_extracted_count"] == 1
    assert "unextracted_annotations_without_text" in row_6_cov["notes"]
    assert "GO:0003824" in row_6_cov["notes"]

    row_6_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_6"]
    assert len(row_6_claims) == 1
    assert row_6_claims[0]["claim_role_raw"] == "Moonlighting_function"

    # In Row 7: Both function descriptions are empty, but GO contains GO:0004000
    row_7_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_7")
    assert row_7_cov["claims_extracted_count"] == 0
    assert row_7_cov["coverage_status"] == "no_discrete_functional_statements"
    assert "unextracted_annotations_without_text" in row_7_cov["notes"]
    assert "GO:0004000" in row_7_cov["notes"]


def test_catalog_lookup_linkage() -> None:
    """Verify that supplied catalog_lookup overrides default accession hashing."""
    custom_catalog = {
        "multitaskprotdb_ii_row_1": "MFP:U:custom_canonical_entity_01",
    }
    claims, coverage = extract_multitask_claims_from_file(
        EDGE_CASES_CSV,
        catalog_lookup=custom_catalog,
    )

    row_1_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_1"]
    assert len(row_1_claims) == 1
    assert row_1_claims[0]["protein_id"] == "MFP:U:custom_canonical_entity_01"


def test_total_ordering_of_extracted_file() -> None:
    """Verify that extract_multitask_claims_from_file returns deterministically sorted lists."""
    claims, coverage = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    claim_keys = [
        (c["protein_id"], c["source_id"], c["source_record_id"], c["claim_index"], c["claim_id"])
        for c in claims
    ]
    assert claim_keys == sorted(claim_keys), "Emitted claims are not sorted by total tie-breaking rule"

    cov_keys = [(c["protein_id"], c["source_id"], c["source_record_id"]) for c in coverage]
    assert cov_keys == sorted(cov_keys), "Emitted coverage records are not sorted by total rule"


# -----------------------------------------------------------------------------
# Tests on Structured Source GO Annotations
# -----------------------------------------------------------------------------

def test_real_extract_annotations_schema_validation(
    annotations_validator: Draft202012Validator,
) -> None:
    """Verify that all source GO annotations from real extract validate against schema."""
    claims, annotations, coverage = extract_multitask_slice_from_file(REAL_EXTRACT_CSV)

    assert len(annotations) > 0
    for ann in annotations:
        annotations_validator.validate(ann)


def test_annotations_total_ordering() -> None:
    """Verify total tie-breaking sort order on emitted source GO annotations."""
    claims, annotations, coverage = extract_multitask_slice_from_file(REAL_EXTRACT_CSV)

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
    assert ann_keys == sorted(ann_keys), "Annotations are not sorted by total rule"


def test_annotations_row_672_explicit_moon_cc() -> None:
    """Verify that GO_Moon CC is preserved in annotations without canonical CC copying."""
    claims, annotations, coverage = extract_multitask_slice_from_file(REAL_EXTRACT_CSV)

    row_672_anns = [a for a in annotations if a["source_record_id"] == "multitaskprotdb_ii_row_6"]
    assert len(row_672_anns) > 0

    canonical_anns = [a for a in row_672_anns if a["source_field"] == "GO"]
    moon_anns = [a for a in row_672_anns if a["source_field"] == "GO_Moon"]

    # Canonical CC annotations present under GO
    canon_cc_ids = {a["go_id"] for a in canonical_anns if a["go_aspect"] == "CC"}
    assert "GO:0005829" in canon_cc_ids  # cytosol
    assert "GO:0016020" in canon_cc_ids  # membrane
    assert "GO:0005739" in canon_cc_ids  # mitochondrion

    # Canonical CC terms must NOT appear in GO_Moon annotations
    moon_go_ids = {a["go_id"] for a in moon_anns}
    assert "GO:0005829" not in moon_go_ids
    assert "GO:0016020" not in moon_go_ids
    assert "GO:0005739" not in moon_go_ids

    # Explicit CC in GO_Moon (nucleoplasm) is preserved with IDA:HPA evidence
    moon_cc = [a for a in moon_anns if a["go_aspect"] == "CC"]
    assert len(moon_cc) == 1
    assert moon_cc[0]["go_id"] == "GO:0005654"
    assert moon_cc[0]["term_name"] == "nucleoplasm"
    assert moon_cc[0]["evidence_raw"] == "IDA:HPA"
    assert moon_cc[0]["claim_id"] is not None  # linked to Moonlighting_function claim


def test_annotations_when_text_is_absent() -> None:
    """Verify that GO annotations are preserved even when the functional text statement is absent."""
    claims, annotations, coverage = extract_multitask_slice_from_file(EDGE_CASES_CSV)

    # Row 6: Canonical text is absent, but GO:0003824 is present
    row_6_anns = [a for a in annotations if a["source_record_id"] == "multitaskprotdb_ii_row_6"]
    assert len(row_6_anns) == 1
    assert row_6_anns[0]["go_id"] == "GO:0003824"
    assert row_6_anns[0]["source_field"] == "GO"
    assert row_6_anns[0]["claim_id"] is None  # no text claim to link to
    assert row_6_anns[0]["protein_id"].startswith("MFP:U:")

    # Row 7: Both functional texts are absent, but GO:0004000 is present
    row_7_anns = [a for a in annotations if a["source_record_id"] == "multitaskprotdb_ii_row_7"]
    assert len(row_7_anns) == 1
    assert row_7_anns[0]["go_id"] == "GO:0004000"
    assert row_7_anns[0]["claim_id"] is None


def test_annotations_repeated_go_ids_with_distinct_evidence() -> None:
    """Verify that multiple annotations with repeated GO IDs and distinct evidence are preserved."""
    claims, annotations, coverage = extract_multitask_slice_from_file(EDGE_CASES_CSV)

    row_8_anns = [a for a in annotations if a["source_record_id"] == "multitaskprotdb_ii_row_8"]
    assert len(row_8_anns) == 2

    # Both have the same GO ID
    assert row_8_anns[0]["go_id"] == "GO:0005840"
    assert row_8_anns[1]["go_id"] == "GO:0005840"

    # Distinct occurrence indices and evidence
    assert row_8_anns[0]["annotation_index"] == 0
    assert row_8_anns[0]["evidence_raw"] == "IEA:UniProtKB-KW"
    assert row_8_anns[1]["annotation_index"] == 1
    assert row_8_anns[1]["evidence_raw"] == "IDA:HPA"

    # Stable, unique annotation IDs
    assert row_8_anns[0]["annotation_id"] != row_8_anns[1]["annotation_id"]
    assert row_8_anns[0]["annotation_id"].startswith("MFP:SGA:MULTITASKPROTDB_II:")
    assert row_8_anns[1]["annotation_id"].startswith("MFP:SGA:MULTITASKPROTDB_II:")


def test_annotations_foreign_key_and_claim_link_integrity() -> None:
    """Verify foreign key linkages: protein_id, source_record_id, and optional claim_id."""
    claims, annotations, coverage = extract_multitask_slice_from_file(REAL_EXTRACT_CSV)
    claims_by_id = {c["claim_id"]: c for c in claims}

    for ann in annotations:
        # Every annotation has valid protein_id
        assert ann["protein_id"].startswith("MFP:U:")
        assert ann["source_id"] == SOURCE_ID

        # If claim_id is present, it must link to an existing claim with matching protein_id
        if ann["claim_id"] is not None:
            linked_claim = claims_by_id[ann["claim_id"]]
            assert linked_claim["protein_id"] == ann["protein_id"]
            assert linked_claim["source_record_id"] == ann["source_record_id"]


def test_backward_compatibility_interface() -> None:
    """Verify that extract_multitask_claims_from_file returns 2 elements by default and 3 when requested."""
    # Default 2-element unpack
    res2 = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)
    assert len(res2) == 2
    claims2, cov2 = res2
    assert isinstance(claims2, list)
    assert isinstance(cov2, list)

    # Explicit return_annotations=True
    res3 = extract_multitask_claims_from_file(REAL_EXTRACT_CSV, return_annotations=True)
    assert len(res3) == 3
    claims3, anns3, cov3 = res3
    assert len(claims3) == len(claims2)
    assert len(cov3) == len(cov2)
    assert len(anns3) > 0

    # Dedicated slice helper
    res_slice = extract_multitask_slice_from_file(REAL_EXTRACT_CSV)
    assert len(res_slice) == 3
    assert res_slice[0] == claims3
    assert res_slice[1] == anns3
    assert res_slice[2] == cov3

