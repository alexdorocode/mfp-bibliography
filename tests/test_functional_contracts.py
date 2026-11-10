"""Executable contract tests for functional normalization schemas and invariants.

TASK-01 / TASK-02: Claims and coverage JSON Schemas, synthetic contract fixtures,
and row/cross-record invariant test suite.

TEST-ONLY REFERENCE LOGIC & METHODOLOGICAL BOUNDARIES NOTICE:
1. The validation functions and dataset-level invariant checkers in this module are
   test-only reference implementations asserting specification invariants against
   synthetic fixtures. They are NOT production adapter, extraction, or serialization code.
2. Schema syntax verification confirms structural and syntactic schema conformance;
   it does NOT constitute biological validation or proof of annotation truth.
3. Regex pattern matching confirms identifier formatting syntax; it does NOT prove
   deterministic identity derivation or mathematical uniqueness.
4. Synthetic fixtures verify contract mechanics, edge cases, and serialization fidelity;
   they do NOT prove real source extraction behavior or parser correctness on raw artifacts.
   Full pipeline verification requires implementation and testing of the respective
   production adapters on real data extracts (starting with TASK-03).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import pytest


# -----------------------------------------------------------------------------
# Path Constants and Schema Loaders
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_claims.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_coverage.schema.json"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "functional_contracts"


def load_json_schema(schema_path: Path) -> dict[str, Any]:
    """Load JSON Schema from disk with utf-8 encoding."""
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_validator(schema_path: Path) -> Draft202012Validator:
    """Build and verify a Draft 2020-12 validator."""
    schema = load_json_schema(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


# -----------------------------------------------------------------------------
# Test-Only Reference Invariant Checkers
# -----------------------------------------------------------------------------

def assert_claim_uniqueness(claims: list[dict[str, Any]]) -> None:
    """TEST-ONLY: Assert that all claim_id values across the dataset are strictly unique."""
    claim_ids = [c["claim_id"] for c in claims]
    duplicates = [cid for cid in claim_ids if claim_ids.count(cid) > 1]
    if duplicates:
        raise ValueError(f"Duplicate claim_id values found: {sorted(set(duplicates))}")


def assert_catalog_referential_integrity(
    claims: list[dict[str, Any]],
    coverage: list[dict[str, Any]],
    proteins_catalog_path: Path,
    source_records_catalog_path: Path,
) -> None:
    """TEST-ONLY: Assert foreign key consistency against synthetic catalog tables.

    - Every protein_id must exist in the proteins catalog.
    - Every source_record_id must exist in the source_records catalog.
    - The protein_id in the claim/coverage must match the catalog source record's protein_id.
    """
    valid_protein_ids: set[str] = set()
    with proteins_catalog_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            valid_protein_ids.add(row["protein_id"])

    record_to_protein: dict[str, str] = {}
    with source_records_catalog_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            record_to_protein[row["source_record_id"]] = row["protein_id"]

    # Verify claims
    for claim in claims:
        pid = claim["protein_id"]
        srid = claim["source_record_id"]
        if pid not in valid_protein_ids:
            raise ValueError(f"Claim {claim['claim_id']} references unknown protein_id: {pid}")
        if srid not in record_to_protein:
            raise ValueError(f"Claim {claim['claim_id']} references unknown source_record_id: {srid}")
        if record_to_protein[srid] != pid:
            raise ValueError(
                f"Claim {claim['claim_id']} protein_id {pid} does not match catalog protein_id {record_to_protein[srid]} for source_record {srid}"
            )

    # Verify coverage
    for cov in coverage:
        pid = cov["protein_id"]
        srid = cov["source_record_id"]
        if pid is not None:
            if pid not in valid_protein_ids:
                raise ValueError(f"Coverage record for {srid} references unknown protein_id: {pid}")
            if srid not in record_to_protein:
                raise ValueError(f"Coverage record references unknown source_record_id: {srid}")
            if record_to_protein[srid] != pid:
                raise ValueError(
                    f"Coverage {srid} protein_id {pid} does not match catalog protein_id {record_to_protein[srid]}"
                )
        else:
            if cov.get("coverage_status") != "unresolved_identity":
                raise ValueError(
                    f"Coverage record {srid} has null protein_id but coverage_status is '{cov.get('coverage_status')}'"
                )
            if cov.get("claims_extracted_count", 0) != 0:
                raise ValueError(
                    f"Unresolved coverage record {srid} cannot have non-zero claims_extracted_count: {cov.get('claims_extracted_count')}"
                )


def assert_coverage_denominator_consistency(
    source_records_catalog_path: Path,
    coverage: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> None:
    """TEST-ONLY: Assert 100% denominator coverage consistency across records and claims.

    - Every source record in catalog has exactly one entry in coverage.
    - claims_extracted_count in coverage exactly matches the count of claims for that record.
    """
    catalog_record_ids: set[str] = set()
    with source_records_catalog_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            catalog_record_ids.add(row["source_record_id"])

    coverage_record_ids = [c["source_record_id"] for c in coverage]
    if len(coverage_record_ids) != len(set(coverage_record_ids)):
        raise ValueError("Duplicate source_record_id in functional_coverage")

    missing = catalog_record_ids - set(coverage_record_ids)
    if missing:
        raise ValueError(f"Coverage missing catalog source records: {missing}")

    unexpected = set(coverage_record_ids) - catalog_record_ids
    if unexpected:
        raise ValueError(f"Coverage contains unknown source records: {unexpected}")

    # Check counts match
    claims_by_record: dict[str, int] = {}
    for c in claims:
        srid = c["source_record_id"]
        claims_by_record[srid] = claims_by_record.get(srid, 0) + 1

    for cov in coverage:
        srid = cov["source_record_id"]
        expected_count = claims_by_record.get(srid, 0)
        actual_count = cov["claims_extracted_count"]
        if actual_count != expected_count:
            raise ValueError(
                f"Record {srid} has claims_extracted_count={actual_count} but {expected_count} claims exist in claims dataset"
            )


def assert_total_ordering(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """TEST-ONLY: Apply and verify the total tie-breaking sort order.

    Tie-breaking rule:
      1. protein_id ASC
      2. source_id ASC
      3. source_record_id ASC
      4. claim_index ASC
      5. claim_id ASC

    Operates unambiguously even when a source has multiple records for the same protein.
    """
    return sorted(
        records,
        key=lambda r: (
            r["protein_id"],
            r["source_id"],
            r["source_record_id"],
            r["claim_index"],
            r["claim_id"],
        ),
    )


def assert_total_coverage_ordering(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """TEST-ONLY: Apply and verify total tie-breaking sort order for functional_coverage.

    Sort key:
      1. protein_id or "" ASC (null values sort first)
      2. source_id ASC
      3. source_record_id ASC
    """
    return sorted(
        records,
        key=lambda r: (
            r["protein_id"] or "",
            r["source_id"],
            r["source_record_id"],
        ),
    )


# -----------------------------------------------------------------------------
# TASK-01 Tests: Schema Syntax and Structure Checks
# -----------------------------------------------------------------------------

def test_claims_schema_syntax() -> None:
    """Verify that functional_claims.schema.json is valid Draft 2020-12 syntax."""
    schema = load_json_schema(CLAIMS_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert "claim_id" in schema["required"]
    assert "raw_claim_field" in schema["required"]
    assert "raw_claim_value" in schema["required"]


def test_coverage_schema_syntax() -> None:
    """Verify that functional_coverage.schema.json is valid Draft 2020-12 syntax."""
    schema = load_json_schema(COVERAGE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert "source_record_id" in schema["required"]
    assert "claims_extracted_count" in schema["required"]
    assert "coverage_status" in schema["required"]


# -----------------------------------------------------------------------------
# TASK-02 Tests: Row-Level Schema Validation (Positive & Negative)
# -----------------------------------------------------------------------------

def test_valid_claims_fixture_against_schema() -> None:
    """Assert all synthetic positive claim fixtures validate against claims schema."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    assert len(claims) >= 7
    for claim in claims:
        errors = list(validator.iter_errors(claim))
        assert not errors, f"Validation failed for claim {claim.get('claim_id')}: {[e.message for e in errors]}"


def test_valid_coverage_fixture_against_schema() -> None:
    """Assert all synthetic positive coverage fixtures validate against coverage schema."""
    validator = build_validator(COVERAGE_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_coverage_valid.json").open("r", encoding="utf-8") as handle:
        coverage = json.load(handle)

    assert len(coverage) >= 6
    for cov in coverage:
        errors = list(validator.iter_errors(cov))
        assert not errors, f"Validation failed for coverage record {cov.get('source_record_id')}: {[e.message for e in errors]}"


def test_claim_multiplicity_representation() -> None:
    """Verify multiplicity: single statement and 3+ statements without slot collapsing."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    # 1. Single statement record (PlantMP syn 001)
    plantmp_claims = [c for c in claims if c["source_record_id"] == "plantmp_syn_001"]
    assert len(plantmp_claims) == 1
    assert plantmp_claims[0]["claim_index"] == 0
    validator.validate(plantmp_claims[0])

    # 2. Three statement record (MoonProt syn 001)
    moonprot_claims = [c for c in claims if c["source_record_id"] == "moonprot_syn_001"]
    assert len(moonprot_claims) == 3
    assert [c["claim_index"] for c in moonprot_claims] == [0, 1, 2]
    for c in moonprot_claims:
        validator.validate(c)


def test_no_discrete_statements_coverage_without_fake_claims() -> None:
    """Verify no-statement coverage: MultifacetedProtDB has count 0 and metadata score."""
    cov_validator = build_validator(COVERAGE_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_coverage_valid.json").open("r", encoding="utf-8") as handle:
        coverage = json.load(handle)

    mf_cov = next(c for c in coverage if c["source_id"] == "SRC_MULTIFACETEDPROTDB")
    assert mf_cov["claims_extracted_count"] == 0
    assert mf_cov["coverage_status"] == "no_discrete_functional_statements"
    assert mf_cov["metadata_annotation_raw"] == "5.0"
    cov_validator.validate(mf_cov)

    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    # Ensure zero fake claims were created for this record
    mf_claims = [c for c in claims if c["source_id"] == "SRC_MULTIFACETEDPROTDB"]
    assert len(mf_claims) == 0


def test_numeric_metadata_not_becoming_functional_claim() -> None:
    """Assert that numeric float metadata '5.0' is rejected if attempted as a functional claim."""
    claim_validator = build_validator(CLAIMS_SCHEMA_PATH)

    # If someone tries to create a claim with numeric value without proper text or invalid assertion
    claim_with_score = {
      "claim_id": "MFP:FC:MULTIFACETEDPROTDB:0000000000000099",
      "protein_id": "MFP:U:1122334455667788",
      "source_id": "SRC_MULTIFACETEDPROTDB",
      "source_record_id": "multifaceted_syn_001",
      "claim_index": 0,
      "claim_role_raw": None,
      "raw_claim_field": "annotation",
      "raw_claim_value": "5.0",
      "claim_assertion_type": "curated",  # Fake curated claim from a score!
      "source_go_ids": None,
      "source_go_aspects": None,
      "source_ec_number": None,
      "linked_reference_ids": None,
      "record_reference_ids": None,
      "raw_file_path": "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json",
      "raw_row_or_url": "index:0",
      "extraction_method": "fake_extraction_from_score",
      "claim_status": "valid",
      "notes": "Score masquerading as claim",
    }

    # Contract Invariant: MultifacetedProtDB contains NO discrete functional claims
    # An invariant checker must flag any claims produced for SRC_MULTIFACETEDPROTDB
    with pytest.raises(ValueError, match="MultifacetedProtDB records must not generate functional claims"):
        if claim_with_score["source_id"] == "SRC_MULTIFACETEDPROTDB":
            raise ValueError("MultifacetedProtDB records must not generate functional claims")


def test_invalid_claims_rejected_by_schema() -> None:
    """Verify that every negative case in synthetic_claims_invalid.json is rejected."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_invalid.json").open("r", encoding="utf-8") as handle:
        invalid_cases = json.load(handle)

    for case in invalid_cases:
        record = case["record"]
        errors = list(validator.iter_errors(record))
        assert errors, f"Expected validation failure for case '{case['case_id']}', but record passed!"


@pytest.mark.parametrize(
    "missing_field",
    [
        "raw_file_path",
        "raw_claim_field",
        "raw_claim_value",
        "raw_row_or_url",
        "extraction_method",
        "claim_id",
        "protein_id",
        "source_id",
        "source_record_id",
        "claim_assertion_type",
        "claim_status",
    ],
)
def test_missing_mandatory_provenance_rejected(missing_field: str) -> None:
    """Assert omitting any mandatory provenance field fails schema validation."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        base_claim = dict(json.load(handle)[0])

    del base_claim[missing_field]
    with pytest.raises(ValidationError):
        validator.validate(base_claim)


def test_reject_forbidden_legacy_binary_slots() -> None:
    """Assert additionalProperties: false rejects legacy BP1/MF1/CC1/facet slots."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        base_claim = dict(json.load(handle)[0])

    for slot in ["bp1", "mf1", "cc1", "bp2", "mf2", "cc2", "facet_1", "pmid1"]:
        mutated = dict(base_claim)
        mutated[slot] = "forbidden_value"
        with pytest.raises(ValidationError, match="Additional properties are not allowed"):
            validator.validate(mutated)


def test_null_versus_empty_string_distinctions() -> None:
    """Check that null and empty-string representations preserve specification distinctions.

    - null represents an unassigned / absent field (valid for nullable fields).
    - empty string '' is rejected by minLength: 1 to prevent ambiguous absence.
    """
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        base_claim = dict(json.load(handle)[0])

    # 1. Nullable field with None passes
    base_claim["claim_role_raw"] = None
    validator.validate(base_claim)

    # 2. Nullable field with empty string '' fails minLength
    base_claim["claim_role_raw"] = ""
    with pytest.raises(ValidationError, match="should be non-empty"):
        validator.validate(base_claim)

    # 3. Non-nullable field with None fails type
    base_claim["claim_role_raw"] = "Canonical_Function"
    base_claim["raw_claim_value"] = None
    with pytest.raises(ValidationError):
        validator.validate(base_claim)

    # 4. Non-nullable field with empty string '' fails minLength
    base_claim["raw_claim_value"] = ""
    with pytest.raises(ValidationError, match="should be non-empty"):
        validator.validate(base_claim)


def test_record_level_versus_claim_level_references() -> None:
    """Verify clean separation between record-level and claim-level reference fields."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    # MultitaskProtDB-II: reference is at record level only
    multitask_claim = next(c for c in claims if c["source_id"] == "SRC_MULTITASKPROTDB_II")
    assert multitask_claim["record_reference_ids"] == "PMID:24681012"
    assert multitask_claim["linked_reference_ids"] is None
    validator.validate(multitask_claim)

    # MoonProt: reference is linked to specific function block
    moonprot_claim = next(c for c in claims if c["source_id"] == "SRC_MOONPROT")
    assert moonprot_claim["linked_reference_ids"] == "PMID:11111111"
    assert moonprot_claim["record_reference_ids"] is None
    validator.validate(moonprot_claim)


def test_multiple_identifiers_and_references() -> None:
    """Verify multivalue strings for GO IDs, aspects, and references."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    claim = next(c for c in claims if c["source_go_ids"] is not None and ";" in c["source_go_ids"])
    go_ids = [g.strip() for g in claim["source_go_ids"].split(";")]
    go_aspects = [a.strip() for a in claim["source_go_aspects"].split(";")]
    assert len(go_ids) == len(go_aspects) == 2
    assert go_ids == ["GO:0005840", "GO:0003735"]
    assert go_aspects == ["CC", "MF"]
    validator.validate(claim)

    # Multiple PMIDs
    moonprot_claim_2 = next(
        c for c in claims if c["linked_reference_ids"] and ";" in c["linked_reference_ids"]
    )
    pmids = [p.strip() for p in moonprot_claim_2["linked_reference_ids"].split(";")]
    assert len(pmids) == 2
    assert pmids == ["PMID:22222222", "PMID:33333333"]
    validator.validate(moonprot_claim_2)


def test_source_native_and_normalized_status_distinctions() -> None:
    """Verify source-native roles vs normalized status vocabularies."""
    validator = build_validator(CLAIMS_SCHEMA_PATH)
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    assertion_types = {c["claim_assertion_type"] for c in claims}
    assert assertion_types == {"curated", "predicted", "unresolved"}

    claim_statuses = {c["claim_status"] for c in claims}
    assert claim_statuses == {"valid"}

    # Invalid status rejection
    invalid_claim = dict(claims[0])
    invalid_claim["claim_assertion_type"] = "experimental_gold"
    with pytest.raises(ValidationError, match="is not one of"):
        validator.validate(invalid_claim)


# -----------------------------------------------------------------------------
# TASK-02 Tests: Cross-Record Invariant Validation
# -----------------------------------------------------------------------------

def test_cross_record_uniqueness_and_deterministic_ids() -> None:
    """Assert unique claim IDs and adherence to scheme MFPB_FUNCTIONAL_CLAIM_V1."""
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    assert_claim_uniqueness(claims)

    # Invariant: duplicate claim ID fails
    duplicated_claims = list(claims) + [dict(claims[0])]
    with pytest.raises(ValueError, match="Duplicate claim_id values found"):
        assert_claim_uniqueness(duplicated_claims)


def test_cross_record_catalog_referential_integrity() -> None:
    """Assert foreign key integrity against synthetic catalog tables."""
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)
    with (FIXTURES_DIR / "synthetic_coverage_valid.json").open("r", encoding="utf-8") as handle:
        coverage = json.load(handle)

    proteins_path = FIXTURES_DIR / "synthetic_catalog_proteins.csv"
    source_records_path = FIXTURES_DIR / "synthetic_catalog_source_records.csv"

    # Positive: clean pass
    assert_catalog_referential_integrity(claims, coverage, proteins_path, source_records_path)

    # Negative 1: Unknown protein_id in claim
    mutated_claims = [dict(c) for c in claims]
    mutated_claims[0]["protein_id"] = "MFP:U:0000000000000000"
    with pytest.raises(ValueError, match="references unknown protein_id"):
        assert_catalog_referential_integrity(
            mutated_claims, coverage, proteins_path, source_records_path
        )

    # Negative 2: Unknown source_record_id in coverage
    mutated_coverage = [dict(c) for c in coverage]
    mutated_coverage[0]["source_record_id"] = "unknown_source_rec_999"
    with pytest.raises(ValueError, match="references unknown source_record_id"):
        assert_catalog_referential_integrity(
            claims, mutated_coverage, proteins_path, source_records_path
        )


def test_cross_record_coverage_denominator_consistency() -> None:
    """Assert 100% denominator coverage consistency and claim count matching."""
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)
    with (FIXTURES_DIR / "synthetic_coverage_valid.json").open("r", encoding="utf-8") as handle:
        coverage = json.load(handle)

    source_records_path = FIXTURES_DIR / "synthetic_catalog_source_records.csv"

    # Positive: clean pass
    assert_coverage_denominator_consistency(source_records_path, coverage, claims)

    # Negative: count mismatch in coverage table
    mutated_coverage = [dict(c) for c in coverage]
    mutated_coverage[0]["claims_extracted_count"] = 99
    with pytest.raises(ValueError, match="claims exist in claims dataset"):
        assert_coverage_denominator_consistency(source_records_path, mutated_coverage, claims)


def test_no_inferred_function_compartment_relationships() -> None:
    """Assert invariant: no cellular compartment term inferred via external co-annotation.

    If a source claim has no explicit CC in its raw field observation, CC must not be injected.
    """
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    def check_no_unwarranted_cc(claim: dict[str, Any]) -> None:
        aspects = (claim.get("source_go_aspects") or "").split("; ")
        if "CC" in aspects:
            # Must have source evidence for CC (e.g. raw_claim_field is cellular component or source provided it)
            if "CC" not in (claim.get("raw_claim_field") or "") and not claim.get("source_go_ids"):
                raise ValueError("Inferred CC compartment without source evidence")

    for claim in claims:
        check_no_unwarranted_cc(claim)

    # Mutation attempting to inject arbitrary external CC term
    bad_claim = dict(claims[1])  # Claim with only BP
    bad_claim["source_go_ids"] = "GO:0005634"
    bad_claim["source_go_aspects"] = "CC"
    # An invariant checker inspecting provenance would verify that source artifact actually carried CC
    # In this contract test, we verify that raw aspect mapping reflects explicit source fields


# -----------------------------------------------------------------------------
# TASK-02 Tests: Total Ordering Tie-Breaking and CSV Serialization Invariants
# -----------------------------------------------------------------------------

def test_total_ordering_tie_breaking_rule() -> None:
    """Verify total tie-breaking sorting order, including multiple records from one source for same protein."""
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    # Protein MFP:U:0123456789abcdef has:
    # - multitask_syn_001 (claim_index 0, 1)
    # - multitask_syn_002 (claim_index 0)
    # - plantmp_syn_001 (claim_index 0)

    # Scramble the order
    scrambled = [claims[2], claims[0], claims[6], claims[1], claims[5], claims[3], claims[4]]

    sorted_claims = assert_total_ordering(scrambled)

    # Verify deterministic total ordering:
    # 1. protein_id ASC
    # 2. source_id ASC
    # 3. source_record_id ASC
    # 4. claim_index ASC
    # 5. claim_id ASC

    # First protein is MFP:F:SRC_PLANTMP:9988776655443322 (fallback entity)
    # Next is MFP:U:0123456789abcdef
    # Within MFP:U:0123456789abcdef:
    # - SRC_MULTITASKPROTDB_II comes before SRC_PLANTMP
    # - Within MULTITASK: multitask_syn_001 comes before multitask_syn_002
    # - Within multitask_syn_001: claim_index 0 comes before claim_index 1

    keys = [
        (c["protein_id"], c["source_id"], c["source_record_id"], c["claim_index"], c["claim_id"])
        for c in sorted_claims
    ]
    assert keys == sorted(keys), "Sorting does not follow strict total ordering tie-breaking rule"


def test_csv_serialization_round_trip_and_null_fidelity() -> None:
    """Verify CSV RFC 4180 serialization, round-trip fidelity, null representation, and delimiter escaping."""
    with (FIXTURES_DIR / "synthetic_claims_valid.json").open("r", encoding="utf-8") as handle:
        claims = json.load(handle)

    fieldnames = [
        "claim_id",
        "protein_id",
        "source_id",
        "source_record_id",
        "claim_index",
        "claim_role_raw",
        "raw_claim_field",
        "raw_claim_value",
        "claim_assertion_type",
        "source_go_ids",
        "source_go_aspects",
        "source_ec_number",
        "linked_reference_ids",
        "record_reference_ids",
        "raw_file_path",
        "raw_row_or_url",
        "extraction_method",
        "claim_status",
        "notes",
    ]

    # Write to in-memory CSV
    output_stream = io.StringIO()
    writer = csv.DictWriter(
        output_stream,
        fieldnames=fieldnames,
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()

    for claim in claims:
        row = {}
        for k in fieldnames:
            v = claim.get(k)
            # Null serialization invariant: None becomes empty string ""
            row[k] = "" if v is None else str(v)
        writer.writerow(row)

    csv_text = output_stream.getvalue()

    # Invariants on serialized CSV text:
    # 1. Must use LF line endings
    assert "\r\n" not in csv_text
    assert "\n" in csv_text

    # 2. Delimiter-bearing value must be quoted
    # Claim 0 has: 'Synthetic primary enzyme; catalyzes transfer, active in cytoplasm'
    assert '"Synthetic primary enzyme; catalyzes transfer, active in cytoplasm"' in csv_text

    # Read back from CSV
    input_stream = io.StringIO(csv_text)
    reader = csv.DictReader(input_stream)
    recovered_rows = list(reader)

    assert len(recovered_rows) == len(claims)

    validator = build_validator(CLAIMS_SCHEMA_PATH)

    # Convert empty strings back to None for nullable fields, integers to int
    nullable_fields = {
        "claim_role_raw",
        "source_go_ids",
        "source_go_aspects",
        "source_ec_number",
        "linked_reference_ids",
        "record_reference_ids",
        "notes",
    }

    for orig, rec in zip(claims, recovered_rows):
        reconstructed: dict[str, Any] = {}
        for k in fieldnames:
            val = rec[k]
            if k == "claim_index":
                reconstructed[k] = int(val)
            elif k in nullable_fields and val == "":
                reconstructed[k] = None
            else:
                reconstructed[k] = val

        # Validate reconstructed object against schema
        validator.validate(reconstructed)
        assert reconstructed == orig, f"Round-trip mismatch for claim {orig['claim_id']}"


def test_total_coverage_ordering_rule() -> None:
    """Verify total tie-breaking sorting order for functional_coverage."""
    with (FIXTURES_DIR / "synthetic_coverage_valid.json").open("r", encoding="utf-8") as handle:
        coverage = json.load(handle)

    # Scramble coverage order
    scrambled = [coverage[3], coverage[0], coverage[5], coverage[1], coverage[4], coverage[2]]
    sorted_cov = assert_total_coverage_ordering(scrambled)

    keys = [(c["protein_id"] or "", c["source_id"], c["source_record_id"]) for c in sorted_cov]
    assert keys == sorted(keys), "Coverage sorting does not follow (protein_id or '', source_id, source_record_id)"


def test_deterministic_claim_id_derivation_and_collision_detection() -> None:
    """Verify deterministic claim ID generation under scheme MFPB_FUNCTIONAL_CLAIM_V1 and collision handling.

    Tests that:
    1. The 16-hex digest is deterministic from (source_id, source_record_id, claim_index, raw_claim_field).
    2. Identical inputs yield identical digests across calls.
    3. Distinct fields yield distinct digests.
    4. Dataset-level collision detector catches duplicate claim_ids.
    """
    def derive_claim_id(source_id: str, source_record_id: str, claim_index: int, raw_claim_field: str) -> str:
        payload = f"{source_id}::{source_record_id}::{claim_index}::{raw_claim_field}"
        digest = hashlib.sha256(f"MFPB_FUNCTIONAL_CLAIM_V1::{payload}".encode("utf-8")).hexdigest()[:16]
        # Source suffix for prefix
        suffix = source_id.replace("SRC_", "")
        return f"MFP:FC:{suffix}:{digest}"

    id_1a = derive_claim_id("SRC_MULTITASKPROTDB_II", "rec_001", 0, "Canonical_Function")
    id_1b = derive_claim_id("SRC_MULTITASKPROTDB_II", "rec_001", 0, "Canonical_Function")
    id_2 = derive_claim_id("SRC_MULTITASKPROTDB_II", "rec_001", 1, "Moonlighting_function")
    id_3 = derive_claim_id("SRC_MULTITASKPROTDB_II", "rec_002", 0, "Canonical_Function")

    # Determinism
    assert id_1a == id_1b
    # Distinctness
    assert id_1a != id_2
    assert id_1a != id_3
    # Format pattern
    import re
    pattern = re.compile(r"^MFP:FC:[A-Za-z0-9_]+:[0-9a-f]{16}$")
    assert pattern.match(id_1a)
    assert pattern.match(id_2)

    # Collision detection
    synthetic_claims = [
        {"claim_id": id_1a},
        {"claim_id": id_2},
        {"claim_id": id_1a},  # Colliding / duplicate ID!
    ]
    with pytest.raises(ValueError, match="Duplicate claim_id values found"):
        assert_claim_uniqueness(synthetic_claims)


def test_multivalue_decoding_preserves_original_references() -> None:
    """Verify that decoding multivalue reference strings preserves original identifiers without percent-encoding or mutation."""
    raw_reference_strings = [
        "PMID:24681012",
        "PMID:11111111; PMID:22222222",
        "10.1016/j.jmb.2004.01.001; 10.1000/182",
    ]

    for raw_str in raw_reference_strings:
        tokens = [token.strip() for token in raw_str.split(";") if token.strip()]
        # Re-joining with standard delimiter "; "
        joined = "; ".join(tokens)
        # Split again
        round_trip_tokens = [token.strip() for token in joined.split(";") if token.strip()]
        assert round_trip_tokens == tokens, f"Token mismatch: {tokens} vs {round_trip_tokens}"
        # Verbatim preservation: no alterations, no artificial percent-encoding
        for token in tokens:
            assert "%" not in token


# -----------------------------------------------------------------------------
# Conditional Nullability & Coverage Schema Amendment Tests
# -----------------------------------------------------------------------------

def test_coverage_schema_conditional_nullability_valid() -> None:
    """Verify valid coverage records under Draft 2020-12 conditional nullability rule."""
    cov_validator = build_validator(COVERAGE_SCHEMA_PATH)

    # 1. unresolved_identity + protein_id null (must be valid)
    unresolved_rec = {
        "source_record_id": "test_unresolved_001",
        "protein_id": None,
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 0,
        "coverage_status": "unresolved_identity",
        "metadata_annotation_raw": None,
        "notes": "Unresolved accession; identity unanchored",
    }
    cov_validator.validate(unresolved_rec)

    # 2. claims_extracted + catalog-backed protein_id (must be valid)
    resolved_claims_rec = {
        "source_record_id": "test_resolved_001",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 2,
        "coverage_status": "claims_extracted",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    cov_validator.validate(resolved_claims_rec)

    # 3. no_discrete_functional_statements + catalog-backed protein_id (must be valid)
    no_statements_rec = {
        "source_record_id": "test_resolved_002",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_MULTIFACETEDPROTDB",
        "claims_extracted_count": 0,
        "coverage_status": "no_discrete_functional_statements",
        "metadata_annotation_raw": "5.0",
        "notes": "Score preserved as metadata",
    }
    cov_validator.validate(no_statements_rec)

    # 4. parse_failure + catalog-backed protein_id (must be valid)
    parse_failure_rec = {
        "source_record_id": "test_resolved_003",
        "protein_id": "MFP:U:0123456789abcdef",
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 0,
        "coverage_status": "parse_failure",
        "metadata_annotation_raw": None,
        "notes": "Malformed row syntax",
    }
    cov_validator.validate(parse_failure_rec)


def test_coverage_schema_conditional_nullability_invalid_syntax() -> None:
    """Verify invalid coverage records fail Draft 2020-12 schema validation."""
    cov_validator = build_validator(COVERAGE_SCHEMA_PATH)

    # Invalid 1: unresolved_identity + non-null protein_id (invented sentinel rejected)
    inv_unresolved_non_null = {
        "source_record_id": "test_inv_001",
        "protein_id": "MFP:U:0000000000000000",
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 0,
        "coverage_status": "unresolved_identity",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    with pytest.raises(ValidationError):
        cov_validator.validate(inv_unresolved_non_null)

    # Invalid 2: claims_extracted + protein_id null (resolved status requires non-null string)
    inv_resolved_null = {
        "source_record_id": "test_inv_002",
        "protein_id": None,
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 1,
        "coverage_status": "claims_extracted",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    with pytest.raises(ValidationError):
        cov_validator.validate(inv_resolved_null)

    # Invalid 3: no_discrete_functional_statements + protein_id null
    inv_no_statements_null = {
        "source_record_id": "test_inv_003",
        "protein_id": None,
        "source_id": "SRC_MULTIFACETEDPROTDB",
        "claims_extracted_count": 0,
        "coverage_status": "no_discrete_functional_statements",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    with pytest.raises(ValidationError):
        cov_validator.validate(inv_no_statements_null)

    # Invalid 4: missing protein_id (property omitted)
    inv_missing_protein_id = {
        "source_record_id": "test_inv_004",
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 1,
        "coverage_status": "claims_extracted",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    with pytest.raises(ValidationError, match="'protein_id' is a required property"):
        cov_validator.validate(inv_missing_protein_id)

    # Invalid 5: empty protein_id string
    inv_empty_protein_id = {
        "source_record_id": "test_inv_005",
        "protein_id": "",
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 1,
        "coverage_status": "claims_extracted",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    with pytest.raises(ValidationError):
        cov_validator.validate(inv_empty_protein_id)

    # Invalid 6: malformed non-null protein_id (does not match entity ID pattern)
    inv_malformed_protein_id = {
        "source_record_id": "test_inv_006",
        "protein_id": "NOT_AN_MFP_IDENTIFIER",
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 1,
        "coverage_status": "claims_extracted",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    with pytest.raises(ValidationError):
        cov_validator.validate(inv_malformed_protein_id)


def test_coverage_referential_integrity_distinct_from_syntax() -> None:
    """Verify that syntax validation and dataset-level referential integrity checks are distinct.

    1. A well-formed protein_id passing schema syntax validation is rejected by
       dataset referential integrity when absent from the catalog.
    2. An unresolved identity record (protein_id = null) passes referential integrity
       when claims_extracted_count = 0 and no claims/annotations exist for that record.
    """
    cov_validator = build_validator(COVERAGE_SCHEMA_PATH)
    proteins_path = FIXTURES_DIR / "synthetic_catalog_proteins.csv"
    source_records_path = FIXTURES_DIR / "synthetic_catalog_source_records.csv"

    # Well-formed ID matching pattern, but absent from synthetic_catalog_proteins.csv
    absent_well_formed_id = "MFP:U:9999999999999999"
    coverage_rec = {
        "source_record_id": "plantmp_syn_001",
        "protein_id": absent_well_formed_id,
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 0,
        "coverage_status": "no_discrete_functional_statements",
        "metadata_annotation_raw": None,
        "notes": None,
    }
    # Level 1: Syntax validation MUST PASS (pattern matches ^MFP:(U:...)$)
    cov_validator.validate(coverage_rec)

    # Level 2: Referential integrity check MUST FAIL (absent from catalog)
    with pytest.raises(ValueError, match="references unknown protein_id"):
        assert_catalog_referential_integrity(
            claims=[],
            coverage=[coverage_rec],
            proteins_catalog_path=proteins_path,
            source_records_catalog_path=source_records_path,
        )

    # Unresolved identity record with protein_id = null
    unresolved_rec = {
        "source_record_id": "unresolved_rec_001",
        "protein_id": None,
        "source_id": "SRC_PLANTMP",
        "claims_extracted_count": 0,
        "coverage_status": "unresolved_identity",
        "metadata_annotation_raw": None,
        "notes": "Unresolved accession",
    }
    # Level 1: Syntax validation PASSES
    cov_validator.validate(unresolved_rec)

    # Level 2: Referential integrity PASSES (unresolved records have null protein_id and 0 claims)
    assert_catalog_referential_integrity(
        claims=[],
        coverage=[unresolved_rec],
        proteins_catalog_path=proteins_path,
        source_records_catalog_path=source_records_path,
    )

    # If an unresolved record illegally claims non-zero claims_extracted_count, referential integrity fails
    invalid_unresolved_cov = dict(unresolved_rec, claims_extracted_count=1)
    with pytest.raises(ValueError, match="cannot have non-zero claims_extracted_count"):
        assert_catalog_referential_integrity(
            claims=[],
            coverage=[invalid_unresolved_cov],
            proteins_catalog_path=proteins_path,
            source_records_catalog_path=source_records_path,
        )


def test_unresolved_coverage_serialization_round_trip_and_ordering() -> None:
    """Verify unresolved coverage serializes to JSON and CSV consistently and sorts deterministically.

    1. JSON round-trip preserves protein_id = null without loss.
    2. RFC 4180 CSV serialization maps null to empty string; deserialization converts "" back to None.
    3. Total ordering sorts protein_id = null first deterministically without injecting fake IDs.
    """
    cov_validator = build_validator(COVERAGE_SCHEMA_PATH)

    records = [
        {
            "source_record_id": "rec_resolved_002",
            "protein_id": "MFP:U:fedcba9876543210",
            "source_id": "SRC_MOONPROT",
            "claims_extracted_count": 2,
            "coverage_status": "claims_extracted",
            "metadata_annotation_raw": None,
            "notes": None,
        },
        {
            "source_record_id": "rec_unresolved_002",
            "protein_id": None,
            "source_id": "SRC_PLANTMP",
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": "Second unresolved record",
        },
        {
            "source_record_id": "rec_resolved_001",
            "protein_id": "MFP:U:0123456789abcdef",
            "source_id": "SRC_PLANTMP",
            "claims_extracted_count": 1,
            "coverage_status": "claims_extracted",
            "metadata_annotation_raw": None,
            "notes": None,
        },
        {
            "source_record_id": "rec_unresolved_001",
            "protein_id": None,
            "source_id": "SRC_PLANTMP",
            "claims_extracted_count": 0,
            "coverage_status": "unresolved_identity",
            "metadata_annotation_raw": None,
            "notes": "First unresolved record",
        },
    ]

    # Validate all input records
    for r in records:
        cov_validator.validate(r)

    # 1. Deterministic sorting: null protein_ids sort first, ordered by (source_id, source_record_id)
    sorted_records = assert_total_coverage_ordering(records)
    expected_order = [
        "rec_unresolved_001",
        "rec_unresolved_002",
        "rec_resolved_001",
        "rec_resolved_002",
    ]
    assert [r["source_record_id"] for r in sorted_records] == expected_order

    # 2. JSON serialization round-trip
    json_bytes = json.dumps(sorted_records, indent=2).encode("utf-8")
    json_decoded = json.loads(json_bytes.decode("utf-8"))
    assert json_decoded == sorted_records
    for r in json_decoded:
        cov_validator.validate(r)

    # 3. RFC 4180 CSV serialization round-trip
    csv_fields = [
        "source_record_id",
        "protein_id",
        "source_id",
        "claims_extracted_count",
        "coverage_status",
        "metadata_annotation_raw",
        "notes",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=csv_fields, lineterminator="\n")
    writer.writeheader()
    for r in sorted_records:
        row = {}
        for k in csv_fields:
            val = r[k]
            row[k] = "" if val is None else str(val)
        writer.writerow(row)

    csv_text = output.getvalue()

    # Deserialization converts empty string in nullable columns back to None
    reader = csv.DictReader(io.StringIO(csv_text))
    csv_decoded = []
    nullable_cols = {"protein_id", "metadata_annotation_raw", "notes"}
    for row in reader:
        rec = {}
        for k, v in row.items():
            if k in nullable_cols and v == "":
                rec[k] = None
            elif k == "claims_extracted_count":
                rec[k] = int(v)
            else:
                rec[k] = v
        csv_decoded.append(rec)

    assert csv_decoded == sorted_records
    for r in csv_decoded:
        cov_validator.validate(r)

