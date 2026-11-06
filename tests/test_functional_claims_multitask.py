"""Unit tests for MultitaskProtDB-II functional claims adapter.

Exercises src/mfp_bibliography/functional_claims_multitask.py directly against:
1. Real-source-derived extract (tests/fixtures/functional_claims_multitask/multitask_real_extract.csv).
2. Synthetic edge cases (tests/fixtures/functional_claims_multitask/multitask_synthetic_edge_cases.csv).

Verifies contract compliance, schema validation, reference granularity,
multiplicity preservation, catalog identity resolution, and determinism.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from mfp_bibliography.functional_claims_multitask import (
    DEFAULT_RAW_FILE_PATH,
    EXTRACTION_METHOD,
    SOURCE_ID,
    derive_multitask_claim_id,
    extract_claims_from_multitask_row,
    extract_multitask_claims_from_file,
    format_multitask_reference,
    parse_multitask_go_terms,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_claims.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_coverage.schema.json"
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
    """Verify parsing of explicit source aspects (C, F, P)."""
    raw_go = (
        "GO:0005840; C:ribosome; IEA:UniProtKB-KW.\n"
        "GO:0003735; F:structural constituent of ribosome; IEA:InterPro.\n"
        "GO:0006412; P:translation; IEA:InterPro."
    )
    go_ids, aspects = parse_multitask_go_terms(raw_go)
    assert go_ids == "GO:0005840; GO:0003735; GO:0006412"
    assert aspects == "CC; MF; BP"

    # Empty text handling
    empty_ids, empty_aspects = parse_multitask_go_terms("")
    assert empty_ids is None
    assert empty_aspects is None


def test_format_multitask_reference_numeric_and_anomalous() -> None:
    """Verify reference classification into record_reference_ids and anomaly notes."""
    # Standard PMID
    ref_1, note_1 = format_multitask_reference("24814782")
    assert ref_1 == "PMID:24814782"
    assert note_1 is None

    # Comma-separated PMIDs
    ref_2, note_2 = format_multitask_reference("11111111, 22222222")
    assert ref_2 == "PMID:11111111; PMID:22222222"
    assert note_2 is None

    # Anomalous reference string
    ref_3, note_3 = format_multitask_reference("HIV-1 infection (omim:600534)")
    assert ref_3 == "HIV-1 infection (omim:600534)"
    assert note_3 == "anomalous_reference: HIV-1 infection (omim:600534)"

    # Empty reference
    ref_4, note_4 = format_multitask_reference("")
    assert ref_4 is None
    assert note_4 is None


# -----------------------------------------------------------------------------
# Tests on Real-Source-Derived Fixture
# -----------------------------------------------------------------------------

def test_real_extract_claims_and_coverage(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Exercise adapter against real MultitaskProtDB-II extracted rows."""
    claims, coverage = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    assert len(coverage) == 5
    # 5 rows with both canonical and moonlighting -> 10 claims
    assert len(claims) == 10

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

    # Invariants for claim index and assertion type
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

    # Row 1 corresponds to UniProt A0A059U5R2
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


def test_real_extract_row_239_anomalous_reference() -> None:
    """Verify preservation of non-numeric reference in Row 239."""
    claims, coverage = extract_multitask_claims_from_file(REAL_EXTRACT_CSV)

    row_239_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_5"]
    assert len(row_239_claims) == 2
    for c in row_239_claims:
        assert "omim:600534" in c["record_reference_ids"]
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

    assert len(coverage) == 5
    assert len(claims) == 4

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

    # 4. Row 4 has invalid accession -> unresolved_identity, 0 claims
    row_4_cov = next(c for c in coverage if c["source_record_id"] == "multitaskprotdb_ii_row_4")
    assert row_4_cov["claims_extracted_count"] == 0
    assert row_4_cov["coverage_status"] == "unresolved_identity"

    # 5. Row 5 has multi-PMID reference
    row_5_claims = [c for c in claims if c["source_record_id"] == "multitaskprotdb_ii_row_5"]
    assert len(row_5_claims) == 2
    for c in row_5_claims:
        assert c["record_reference_ids"] == "PMID:11111111; PMID:22222222"


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
