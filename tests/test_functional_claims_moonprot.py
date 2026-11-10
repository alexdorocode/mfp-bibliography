"""Unit tests for MoonProt functional claims, coverage, and source GO annotations adapter.

Exercises src/mfp_bibliography/functional_claims_moonprot.py directly against:
1. Real-source-derived extracts (tests/fixtures/functional_claims_moonprot/real_mpid_*.html).
2. Synthetic edge cases (tests/fixtures/functional_claims_moonprot/synthetic_mpid_*.html).

Verifies contract compliance, schema validation, reference preservation,
multiplicity preservation, dynamic function blocks (no two-function assumption),
preservation of source-native locators and text, function-level references in
linked_reference_ids with "PMID:" prefix, protein-level GO terms preserved
structurally in source_go_annotations with claim_id = null (never distributed across
claims), cellular location text preserved in notes without inferring CC terms or triplets,
valid catalog fallback identities (MFP:F:...) respected, honest null for unresolved
identity under Draft 2020-12 coverage schema, and deterministic total ordering.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from mfp_bibliography.normalization import make_protein_id_uniprot
from mfp_bibliography.functional_claims_moonprot import (
    DEFAULT_CATALOG_PATH,
    EXTRACTION_METHOD,
    SOURCE_ID,
    SOURCE_SUFFIX,
    derive_moonprot_claim_id,
    derive_source_go_annotation_id,
    extract_claims_from_moonprot_record,
    extract_moonprot_claims_from_file,
    extract_moonprot_slice_from_files,
    format_moonprot_references,
    load_moonprot_catalog_lookup,
    parse_moonprot_go_annotations,
)
from mfp_bibliography.moonprot_parser import parse_moonprot_fixture

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_claims.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_coverage.schema.json"
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_go_annotations.schema.json"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "functional_claims_moonprot"

# Real extracts
REAL_MPID_1 = FIXTURES_DIR / "real_mpid_1.html"
REAL_MPID_2 = FIXTURES_DIR / "real_mpid_2.html"
REAL_MPID_7 = FIXTURES_DIR / "real_mpid_7.html"
REAL_MPID_10 = FIXTURES_DIR / "real_mpid_10.html"
REAL_MPID_288 = FIXTURES_DIR / "real_mpid_288.html"

# Synthetic edge cases
SYNTHETIC_901 = FIXTURES_DIR / "synthetic_mpid_901_three_functions.html"
SYNTHETIC_902 = FIXTURES_DIR / "synthetic_mpid_902_single_function.html"
SYNTHETIC_903 = FIXTURES_DIR / "synthetic_mpid_903_missing_uniprot.html"
SYNTHETIC_904 = FIXTURES_DIR / "synthetic_mpid_904_malformed_uniprot.html"
SYNTHETIC_905 = FIXTURES_DIR / "synthetic_mpid_905_fallback_identity.html"
SYNTHETIC_906 = FIXTURES_DIR / "synthetic_mpid_906_multi_pmids.html"
SYNTHETIC_907 = FIXTURES_DIR / "synthetic_mpid_907_empty_functions_with_go.html"
SYNTHETIC_908 = FIXTURES_DIR / "synthetic_mpid_908_known_absent.html"

# Synthetic catalog lookup backing synthetic edge cases
SYNTHETIC_CATALOG_LOOKUP = {
    "moonprot_901": make_protein_id_uniprot("P90101"),
    "moonprot_902": make_protein_id_uniprot("P90202"),
    "moonprot_905": "MFP:F:SRC_MOONPROT:0000000000000905",
    "moonprot_906": make_protein_id_uniprot("P90606"),
    "moonprot_907": make_protein_id_uniprot("P90707"),
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
# Unit Tests for Helpers and ID Derivation
# -----------------------------------------------------------------------------

def test_derive_moonprot_claim_id_determinism() -> None:
    """Verify deterministic derivation of claim_id under MFPB_FUNCTIONAL_CLAIM_V1."""
    cid1 = derive_moonprot_claim_id("moonprot_1", 0, "functions[0].description")
    cid2 = derive_moonprot_claim_id("moonprot_1", 0, "functions[0].description")
    assert cid1 == cid2
    assert cid1.startswith(f"MFP:FC:{SOURCE_SUFFIX}:")
    assert len(cid1.split(":")[-1]) == 16

    # Distinct field or index yields distinct ID
    cid3 = derive_moonprot_claim_id("moonprot_1", 1, "functions[1].description")
    assert cid1 != cid3


def test_derive_source_go_annotation_id_determinism() -> None:
    """Verify deterministic derivation of annotation_id under MFPB_SOURCE_GO_ANNOTATION_V1."""
    aid1 = derive_source_go_annotation_id("moonprot_1", "GO terms", 0, "GO:0003824")
    aid2 = derive_source_go_annotation_id("moonprot_1", "GO terms", 0, "GO:0003824")
    assert aid1 == aid2
    assert aid1.startswith(f"MFP:SGA:{SOURCE_SUFFIX}:")
    assert len(aid1.split(":")[-1]) == 16

    # Distinct index yields distinct ID
    aid3 = derive_source_go_annotation_id("moonprot_1", "GO terms", 1, "GO:0003824")
    assert aid1 != aid3


def test_format_moonprot_references() -> None:
    """Verify formatting of function-level PMIDs with PMID: prefix."""
    assert format_moonprot_references(()) is None
    assert format_moonprot_references(("12345678",)) == "PMID:12345678"
    assert format_moonprot_references(("PMID:12345678",)) == "PMID:12345678"
    assert (
        format_moonprot_references(("11111111", "22222222"))
        == "PMID:11111111; PMID:22222222"
    )


def test_parse_moonprot_go_annotations() -> None:
    """Verify parsing of protein-level GO terms text."""
    raw_text = "GO:0003824 catalytic activity, GO:0005515 protein binding"
    parsed = parse_moonprot_go_annotations(raw_text)
    assert len(parsed) == 2
    assert parsed[0]["go_id"] == "GO:0003824"
    assert parsed[0]["term_name"] == "catalytic activity"
    assert parsed[1]["go_id"] == "GO:0005515"
    assert parsed[1]["term_name"] == "protein binding"


# -----------------------------------------------------------------------------
# Real-Source Extract Tests
# -----------------------------------------------------------------------------

def test_real_extract_mpid_1(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
) -> None:
    """Verify extraction on real MPID 1 (L-lactate dehydrogenase)."""
    claims, annotations, coverage = extract_moonprot_claims_from_file(REAL_MPID_1)

    # 1. Coverage record validation
    coverage_validator.validate(coverage)
    assert coverage["source_record_id"] == "moonprot_1"
    assert coverage["source_id"] == SOURCE_ID
    assert coverage["coverage_status"] == "claims_extracted"
    assert coverage["claims_extracted_count"] == 2
    assert coverage["protein_id"] == make_protein_id_uniprot("P78007")

    # 2. Claims validation (exactly 2 claims)
    assert len(claims) == 2
    for c in claims:
        claims_validator.validate(c)
        assert c["protein_id"] == make_protein_id_uniprot("P78007")
        assert c["source_id"] == SOURCE_ID
        assert c["source_record_id"] == "moonprot_1"
        assert c["claim_assertion_type"] == "curated"
        assert c["record_reference_ids"] is None  # MoonProt references are function-level
        assert c["source_go_ids"] is None  # Not distributed across claims
        assert c["source_go_aspects"] is None

    # Function 1
    c1 = claims[0]
    assert c1["claim_index"] == 0
    assert c1["claim_role_raw"] == "Function 1"
    assert c1["raw_claim_field"] == "functions[0].description"
    assert c1["source_ec_number"] == "1.1.1.27"
    assert c1["linked_reference_ids"] == "PMID:27616280"
    assert "cellular_location: cytosol" in c1["notes"]

    # Function 2
    c2 = claims[1]
    assert c2["claim_index"] == 1
    assert c2["claim_role_raw"] == "Function 2"
    assert c2["raw_claim_field"] == "functions[1].description"
    assert c2["source_ec_number"] is None
    assert c2["linked_reference_ids"] == "PMID:27616280"

    # 3. Structured GO annotations
    assert len(annotations) > 0
    for a in annotations:
        annotations_validator.validate(a)
        assert a["protein_id"] == make_protein_id_uniprot("P78007")
        assert a["source_id"] == SOURCE_ID
        assert a["source_record_id"] == "moonprot_1"
        assert a["claim_id"] is None  # Explicitly unlinked to discrete claims
        assert a["source_field"] == "GO terms"
        assert a["go_aspect"] is None
        assert a["annotation_status"] == "parsed"


def test_real_extract_mpid_2_accession_normalization(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify normalization of raw accession with annotation residue ('P0AFW0 (RFAH_ECOLI), Reviewed')."""
    claims, _, coverage = extract_moonprot_claims_from_file(REAL_MPID_2)

    coverage_validator.validate(coverage)
    expected_pid = make_protein_id_uniprot("P0AFW0")
    assert coverage["protein_id"] == expected_pid
    assert coverage["coverage_status"] == "claims_extracted"
    assert coverage["claims_extracted_count"] == 2

    assert len(claims) == 2
    for c in claims:
        claims_validator.validate(c)
        assert c["protein_id"] == expected_pid

    # Function 1 has no PMIDs, cellular location 'bound to DNA', EC 'N/A' -> None
    c1 = claims[0]
    assert c1["linked_reference_ids"] is None
    assert c1["source_ec_number"] is None
    assert "cellular_location: bound to DNA" in c1["notes"]

    # Function 2 has PMID 22817892, cellular location 'cytoplasm'
    c2 = claims[1]
    assert c2["linked_reference_ids"] == "PMID:22817892"
    assert "cellular_location: cytoplasm" in c2["notes"]


def test_real_extract_mpid_7_hsp60_annotations(
    claims_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
) -> None:
    """Verify extensive protein-level GO annotations on real MPID 7 (Hsp60)."""
    claims, annotations, coverage = extract_moonprot_claims_from_file(REAL_MPID_7)

    assert len(claims) == 2
    for c in claims:
        claims_validator.validate(c)

    # Over 40 GO terms in Hsp60
    assert len(annotations) >= 40
    for a in annotations:
        annotations_validator.validate(a)
        assert a["claim_id"] is None
        assert a["source_field"] == "GO terms"
        assert a["go_id"].startswith("GO:")


def test_real_extract_mpid_288_zero_functions(
    coverage_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
) -> None:
    """Verify real-source zero-function case (MPID 288, Penicillin-binding protein 4).

    Exercises denominator accounting where a legitimate acquired record has 0 function
    blocks but populated GO terms.
    """
    claims, annotations, coverage = extract_moonprot_claims_from_file(REAL_MPID_288)

    # Exactly 0 claims
    assert len(claims) == 0

    # Coverage status must be no_discrete_functional_statements
    coverage_validator.validate(coverage)
    assert coverage["source_record_id"] == "moonprot_288"
    assert coverage["claims_extracted_count"] == 0
    assert coverage["coverage_status"] == "no_discrete_functional_statements"
    assert coverage["protein_id"] == make_protein_id_uniprot("P24228")
    assert "protein-level GO annotations preserved with claim_id=null" in (coverage["notes"] or "")

    # GO annotations are still preserved structurally
    assert len(annotations) > 0
    for a in annotations:
        annotations_validator.validate(a)
        assert a["claim_id"] is None


# -----------------------------------------------------------------------------
# Synthetic Edge Cases Tests
# -----------------------------------------------------------------------------

def test_synthetic_three_functions_no_two_function_assumption(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify dynamic K-block extraction with K=3 (no fixed two-function assumption)."""
    claims, _, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_901, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    coverage_validator.validate(coverage)
    assert coverage["claims_extracted_count"] == 3
    assert coverage["coverage_status"] == "claims_extracted"

    assert len(claims) == 3
    for idx, c in enumerate(claims):
        claims_validator.validate(c)
        assert c["claim_index"] == idx
        assert c["claim_role_raw"] == f"Function {idx + 1}"
        assert c["raw_claim_field"] == f"functions[{idx}].description"

    assert claims[0]["linked_reference_ids"] == "PMID:11111111"
    assert claims[0]["source_ec_number"] == "1.1.1.1"
    assert "cellular_location: cytoplasm" in claims[0]["notes"]

    assert claims[1]["linked_reference_ids"] == "PMID:22222222"
    assert claims[1]["source_ec_number"] is None
    assert "cellular_location: nucleus" in claims[1]["notes"]

    assert claims[2]["linked_reference_ids"] == "PMID:33333333"
    assert claims[2]["source_ec_number"] is None
    assert "cellular_location: plasma membrane" in claims[2]["notes"]


def test_synthetic_single_function(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify dynamic K-block extraction with K=1 single function block."""
    claims, _, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_902, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    coverage_validator.validate(coverage)
    assert coverage["claims_extracted_count"] == 1
    assert coverage["coverage_status"] == "claims_extracted"

    assert len(claims) == 1
    c = claims[0]
    claims_validator.validate(c)
    assert c["claim_index"] == 0
    assert c["claim_role_raw"] == "Function 1"
    assert c["raw_claim_field"] == "functions[0].description"
    assert c["source_ec_number"] == "2.7.1.1"
    assert c["linked_reference_ids"] == "PMID:44444444"


def test_synthetic_fallback_identity_respected(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify that valid catalog fallback identities (MFP:F:SRC_MOONPROT:...) are respected."""
    claims, _, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_905, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    expected_fallback_id = "MFP:F:SRC_MOONPROT:0000000000000905"

    # Coverage validation accepts valid fallback identity matching regex
    coverage_validator.validate(coverage)
    assert coverage["protein_id"] == expected_fallback_id
    assert coverage["coverage_status"] == "claims_extracted"

    # Claims validation accepts valid fallback identity matching regex
    assert len(claims) == 1
    c = claims[0]
    claims_validator.validate(c)
    assert c["protein_id"] == expected_fallback_id
    assert c["source_ec_number"] == "3.1.1.1"
    assert c["linked_reference_ids"] == "PMID:55555555"


def test_synthetic_multi_pmids_and_raw_text_reference(
    claims_validator: Draft202012Validator,
) -> None:
    """Verify function with multiple PMIDs and function with raw text citation without PMID."""
    claims, _, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_906, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    assert len(claims) == 2
    for c in claims:
        claims_validator.validate(c)

    # Function 1 has 3 PMIDs
    assert claims[0]["linked_reference_ids"] == "PMID:66666661; PMID:66666662; PMID:66666663"

    # Function 2 has no PMIDs; raw text is preserved in notes
    assert claims[1]["linked_reference_ids"] is None
    assert "ref_raw: Smith et al., J. Biol. Chem. (1998) without numeric PMID" in claims[1]["notes"]


def test_synthetic_empty_functions_with_go(
    coverage_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
) -> None:
    """Verify synthetic record with empty functions but explicit GO terms."""
    claims, annotations, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_907, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    assert len(claims) == 0
    coverage_validator.validate(coverage)
    assert coverage["claims_extracted_count"] == 0
    assert coverage["coverage_status"] == "no_discrete_functional_statements"

    assert len(annotations) == 2
    for a in annotations:
        annotations_validator.validate(a)
        assert a["claim_id"] is None


# -----------------------------------------------------------------------------
# Negative Identity Tests (Honest Null, No Sentinels, Referential Integrity)
# -----------------------------------------------------------------------------

def test_negative_missing_uniprot_unresolved_identity(
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify missing UniProt ID produces unresolved_identity with protein_id = null."""
    claims, annotations, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_903, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    assert len(claims) == 0
    assert len(annotations) == 0
    coverage_validator.validate(coverage)
    assert coverage["coverage_status"] == "unresolved_identity"
    assert coverage["protein_id"] is None
    assert coverage["claims_extracted_count"] == 0
    assert coverage["protein_id"] != "MFP:U:0000000000000000"


def test_negative_malformed_uniprot_unresolved_identity(
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify malformed UniProt ID produces unresolved_identity with protein_id = null."""
    claims, annotations, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_904, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    assert len(claims) == 0
    assert len(annotations) == 0
    coverage_validator.validate(coverage)
    assert coverage["coverage_status"] == "unresolved_identity"
    assert coverage["protein_id"] is None
    assert coverage["claims_extracted_count"] == 0
    assert coverage["protein_id"] != "MFP:U:0000000000000000"


def test_negative_valid_accession_absent_from_catalog(
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify valid-looking accession absent from catalog lookup is NOT silently promoted."""
    empty_catalog: dict[str, str] = {}
    claims, annotations, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_901, catalog_lookup=empty_catalog
    )

    assert len(claims) == 0
    assert len(annotations) == 0
    coverage_validator.validate(coverage)
    assert coverage["coverage_status"] == "unresolved_identity"
    assert coverage["protein_id"] is None
    assert coverage["claims_extracted_count"] == 0


def test_negative_mismatched_catalog_linkage(
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify that catalog protein ID conflicting with accession derivation is rejected."""
    mismatched_catalog = {
        "moonprot_901": make_protein_id_uniprot("P12345")  # Does not match P90101
    }
    claims, annotations, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_901, catalog_lookup=mismatched_catalog
    )

    assert len(claims) == 0
    assert len(annotations) == 0
    coverage_validator.validate(coverage)
    assert coverage["coverage_status"] == "unresolved_identity"
    assert coverage["protein_id"] is None
    assert coverage["claims_extracted_count"] == 0
    assert "Catalog protein_id mismatch" in coverage["notes"]


def test_negative_multiple_unresolved_not_collapsed() -> None:
    """Verify multiple unresolved records are accounted for distinctly without collapsing into a fake entity."""
    _, _, cov_a = extract_moonprot_claims_from_file(
        SYNTHETIC_903, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )
    _, _, cov_b = extract_moonprot_claims_from_file(
        SYNTHETIC_904, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    assert cov_a["source_record_id"] == "moonprot_903"
    assert cov_b["source_record_id"] == "moonprot_904"
    assert cov_a["protein_id"] is None
    assert cov_b["protein_id"] is None
    assert cov_a["source_record_id"] != cov_b["source_record_id"]
    assert cov_a["protein_id"] != "MFP:U:0000000000000000"
    assert cov_b["protein_id"] != "MFP:U:0000000000000000"


def test_negative_known_absent_soft_404_handling(
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify known-absent soft-404 fixture (e.g. captured MPID 103 template) produces unresolved_identity."""
    claims, annotations, coverage = extract_moonprot_claims_from_file(
        SYNTHETIC_908, catalog_lookup=SYNTHETIC_CATALOG_LOOKUP
    )

    assert len(claims) == 0
    assert len(annotations) == 0
    coverage_validator.validate(coverage)
    assert coverage["coverage_status"] == "unresolved_identity"
    assert coverage["protein_id"] is None
    assert coverage["claims_extracted_count"] == 0


def test_unanchored_mode_behavior() -> None:
    """Document and verify behavior with and without catalog_lookup and allow_unanchored."""
    # 1. Default (no catalog_lookup, allow_unanchored=False): automatically loads real catalog
    # Since MPID 901 is synthetic and not in real catalog, it is unresolved
    _, _, cov_default = extract_moonprot_claims_from_file(SYNTHETIC_901)
    assert cov_default["coverage_status"] == "unresolved_identity"
    assert cov_default["protein_id"] is None

    # 2. allow_unanchored=True: derives synthetic ID without catalog check
    claims_unanchored, _, cov_unanchored = extract_moonprot_claims_from_file(
        SYNTHETIC_901, allow_unanchored=True
    )
    assert cov_unanchored["coverage_status"] == "claims_extracted"
    assert cov_unanchored["protein_id"] == make_protein_id_uniprot("P90101")
    assert len(claims_unanchored) == 3


# -----------------------------------------------------------------------------
# Catalog Loading & Total Slice Ordering Tests
# -----------------------------------------------------------------------------

def test_load_moonprot_catalog_lookup() -> None:
    """Verify loading of authoritative MoonProt catalog lookup from MVP catalog."""
    lookup = load_moonprot_catalog_lookup()
    assert len(lookup) == 702
    assert "moonprot_1" in lookup
    assert lookup["moonprot_1"] == make_protein_id_uniprot("P78007")
    assert "moonprot_2" in lookup
    assert lookup["moonprot_2"] == make_protein_id_uniprot("P0AFW0")


def test_extract_moonprot_slice_total_ordering(
    claims_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
) -> None:
    """Verify batch slice extraction across real extract fixtures and check total ordering."""
    real_files = [REAL_MPID_1, REAL_MPID_2, REAL_MPID_7, REAL_MPID_10, REAL_MPID_288]
    claims, annotations, coverage = extract_moonprot_slice_from_files(real_files)

    # 5 files: MPID 1 (2), MPID 2 (2), MPID 7 (2), MPID 10 (2), MPID 288 (0) = 8 claims
    assert len(coverage) == 5
    assert len(claims) == 8
    assert len(annotations) > 0

    for c in claims:
        claims_validator.validate(c)
    for cov in coverage:
        coverage_validator.validate(cov)
    for a in annotations:
        annotations_validator.validate(a)

    # Verify claim total ordering: (protein_id, source_id, source_record_id, claim_index, claim_id)
    claim_keys = [
        (c["protein_id"], c["source_id"], c["source_record_id"], c["claim_index"], c["claim_id"])
        for c in claims
    ]
    assert claim_keys == sorted(claim_keys)

    # Verify annotation total ordering: (protein_id, source_id, source_record_id, source_field, annotation_index, annotation_id)
    annotation_keys = [
        (a["protein_id"], a["source_id"], a["source_record_id"], a["source_field"], a["annotation_index"], a["annotation_id"])
        for a in annotations
    ]
    assert annotation_keys == sorted(annotation_keys)

    # Verify coverage total ordering: (protein_id or "", source_id, source_record_id)
    coverage_keys = [
        (cov["protein_id"] or "", cov["source_id"], cov["source_record_id"])
        for cov in coverage
    ]
    assert coverage_keys == sorted(coverage_keys)
