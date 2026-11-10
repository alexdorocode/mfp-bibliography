"""Executable contract tests for source GO annotations schema and invariants.

Validates data/curated/source_go_annotations.schema.json under Draft 2020-12 rules.
Tests structural integrity, identifier syntax, aspect enums, optional claim linkages,
and deterministic total ordering.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_go_annotations.schema.json"


def load_annotations_validator() -> Draft202012Validator:
    """Load and compile Draft 2020-12 validator for source GO annotations schema."""
    with ANNOTATIONS_SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


VALID_ANNOTATION_SAMPLE: dict[str, Any] = {
    "annotation_id": "MFP:SGA:MULTITASKPROTDB_II:0123456789abcdef",
    "protein_id": "MFP:U:ac159de80a38c3e3",
    "source_id": "SRC_MULTITASKPROTDB_II",
    "source_record_id": "multitaskprotdb_ii_row_1",
    "claim_id": "MFP:FC:MULTITASKPROTDB_II:fedcba9876543210",
    "source_field": "GO",
    "annotation_index": 0,
    "raw_annotation_text": "GO:0005840; C:ribosome; IEA:UniProtKB-KW.",
    "go_id": "GO:0005840",
    "go_aspect": "CC",
    "term_name": "ribosome",
    "evidence_raw": "IEA:UniProtKB-KW",
    "annotation_status": "parsed",
    "notes": None,
}


def test_source_go_annotations_schema_syntax() -> None:
    """Verify source_go_annotations.schema.json is a valid Draft 2020-12 schema."""
    validator = load_annotations_validator()
    assert validator is not None


def test_valid_annotation_sample() -> None:
    """Verify that a canonical valid annotation record passes schema validation."""
    validator = load_annotations_validator()
    validator.validate(VALID_ANNOTATION_SAMPLE)


def test_annotation_with_null_claim_id() -> None:
    """A GO annotation may be preserved without a linked text claim (claim_id = null)."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["claim_id"] = None
    validator.validate(sample)


def test_annotation_with_null_optional_fields() -> None:
    """Verify that term_name, evidence_raw, go_aspect, and notes can be null."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["term_name"] = None
    sample["evidence_raw"] = None
    sample["go_aspect"] = None
    sample["annotation_status"] = "unassigned_aspect"
    sample["notes"] = None
    validator.validate(sample)


@pytest.mark.parametrize("missing_field", [
    "annotation_id",
    "protein_id",
    "source_id",
    "source_record_id",
    "claim_id",
    "source_field",
    "annotation_index",
    "raw_annotation_text",
    "go_id",
    "go_aspect",
    "term_name",
    "evidence_raw",
    "annotation_status",
    "notes",
])
def test_annotation_missing_required_fields(missing_field: str) -> None:
    """Verify that omitting any required field fails closed validation."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    del sample[missing_field]
    with pytest.raises(ValidationError):
        validator.validate(sample)


@pytest.mark.parametrize("invalid_id", [
    "SGA:12345",
    "MFP:FC:MULTITASKPROTDB_II:0123456789abcdef",  # FC prefix instead of SGA
    "MFP:SGA:MULTITASKPROTDB_II:012345",  # Too short digest
    "MFP:SGA:MULTITASKPROTDB_II:0123456789abcdef01",  # Too long digest
    "MFP:SGA:MULTITASKPROTDB_II:0123456789ABCDEF",  # Uppercase hex
])
def test_annotation_invalid_annotation_id_pattern(invalid_id: str) -> None:
    """Verify strict pattern enforcement on annotation_id."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["annotation_id"] = invalid_id
    with pytest.raises(ValidationError):
        validator.validate(sample)


@pytest.mark.parametrize("invalid_claim_id", [
    "CLAIM:12345",
    "MFP:SGA:MULTITASKPROTDB_II:0123456789abcdef",  # SGA prefix instead of FC
    "MFP:FC:MULTITASKPROTDB_II:012345",  # Short digest
])
def test_annotation_invalid_claim_id_pattern(invalid_claim_id: str) -> None:
    """Verify that non-null claim_id must match MFP:FC pattern."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["claim_id"] = invalid_claim_id
    with pytest.raises(ValidationError):
        validator.validate(sample)


@pytest.mark.parametrize("invalid_go_id", [
    "0005840",
    "GO:5840",
    "GO:00058401",
    "go:0005840",
    "GO:ABCDEFG",
])
def test_annotation_invalid_go_id_pattern(invalid_go_id: str) -> None:
    """Verify strict pattern enforcement on go_id (7 digits)."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["go_id"] = invalid_go_id
    with pytest.raises(ValidationError):
        validator.validate(sample)


@pytest.mark.parametrize("invalid_aspect", [
    "cellular_component",
    "C",
    "F",
    "P",
    "biological_process",
    "molecular_function",
    "UNKNOWN",
])
def test_annotation_invalid_aspect_enum(invalid_aspect: str) -> None:
    """Verify enum enforcement on go_aspect (BP, MF, CC, unassigned, or null)."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["go_aspect"] = invalid_aspect
    with pytest.raises(ValidationError):
        validator.validate(sample)


@pytest.mark.parametrize("empty_field", [
    "raw_annotation_text",
    "term_name",
    "evidence_raw",
    "notes",
])
def test_annotation_rejects_empty_strings(empty_field: str) -> None:
    """Verify that empty strings are rejected; nullable fields must be explicit null."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample[empty_field] = ""
    with pytest.raises(ValidationError):
        validator.validate(sample)


def test_annotation_rejects_additional_properties() -> None:
    """Verify closed schema constraint (additionalProperties: false)."""
    validator = load_annotations_validator()
    sample = copy.deepcopy(VALID_ANNOTATION_SAMPLE)
    sample["unexpected_field"] = "extraneous"
    with pytest.raises(ValidationError):
        validator.validate(sample)


def test_annotation_total_ordering_rule() -> None:
    """Verify deterministic total ordering key for annotations."""
    records = [
        {
            "protein_id": "MFP:U:bbbbbbbbbbbbbbbb",
            "source_id": "SRC_MULTITASKPROTDB_II",
            "source_record_id": "multitaskprotdb_ii_row_2",
            "source_field": "GO",
            "annotation_index": 0,
            "annotation_id": "MFP:SGA:MULTITASKPROTDB_II:1111111111111111",
        },
        {
            "protein_id": "MFP:U:aaaaaaaaaaaaaaaa",
            "source_id": "SRC_MULTITASKPROTDB_II",
            "source_record_id": "multitaskprotdb_ii_row_1",
            "source_field": "GO",
            "annotation_index": 0,
            "annotation_id": "MFP:SGA:MULTITASKPROTDB_II:2222222222222222",
        },
        {
            "protein_id": "MFP:U:aaaaaaaaaaaaaaaa",
            "source_id": "SRC_MULTITASKPROTDB_II",
            "source_record_id": "multitaskprotdb_ii_row_1",
            "source_field": "GO",
            "annotation_index": 1,
            "annotation_id": "MFP:SGA:MULTITASKPROTDB_II:3333333333333333",
        },
    ]

    key_fn = lambda r: (
        r["protein_id"],
        r["source_id"],
        r["source_record_id"],
        r["source_field"],
        r["annotation_index"],
        r["annotation_id"],
    )

    sorted_records = sorted(records, key=key_fn)
    assert sorted_records[0]["annotation_id"] == "MFP:SGA:MULTITASKPROTDB_II:2222222222222222"
    assert sorted_records[1]["annotation_id"] == "MFP:SGA:MULTITASKPROTDB_II:3333333333333333"
    assert sorted_records[2]["annotation_id"] == "MFP:SGA:MULTITASKPROTDB_II:1111111111111111"
