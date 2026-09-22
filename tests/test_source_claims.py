from __future__ import annotations

import pytest

from mfp_bibliography.schemas import RecordValidationError
from mfp_bibliography.source_claims import make_claim_id, validate_claim

SOURCE_ID = "SRC_MOONDB"
SOURCE_RECORD_ID = "MDB_001"
RAW_FILE_PATH = "data/raw/moondb/all_emf_and_curated.tsv"
RAW_ROW_OR_URL = "row:1"
RAW_CLAIM_FIELD = "type"


def _claim(**overrides: object) -> dict[str, object]:
    claim: dict[str, object] = {
        "source_id": SOURCE_ID,
        "source_record_id": SOURCE_RECORD_ID,
        "uniprot_id": "P12345",
        "protein_name_raw": "Example protein",
        "organism_raw": "Homo sapiens",
        "raw_claim_field": RAW_CLAIM_FIELD,
        "raw_claim_value": "Curated",
        "operational_status": "curated",
        "primary_target_eligible": True,
        "control_eligible": False,
        "raw_file_path": RAW_FILE_PATH,
        "raw_row_or_url": RAW_ROW_OR_URL,
        "source_version": "unknown",
        "retrieved_at": "2026-09-22T10:00:00Z",
        "transformation_id": "claim_normalization_v0",
        "record_status": "valid",
        "notes": None,
    }
    claim.update(overrides)
    claim["claim_id"] = make_claim_id(
        str(claim["source_id"]),
        str(claim["source_record_id"]),
        str(claim["raw_file_path"]),
        str(claim["raw_row_or_url"]),
        str(claim["raw_claim_field"]),
    )
    return claim


def test_valid_curated_claim() -> None:
    validate_claim(_claim())


def test_valid_predicted_claim() -> None:
    validate_claim(
        _claim(
            raw_claim_value="Predicted",
            operational_status="predicted",
            primary_target_eligible=False,
        )
    )


def test_valid_excluded_likely_claim() -> None:
    validate_claim(
        _claim(
            raw_claim_value="likely",
            operational_status="excluded_likely",
            primary_target_eligible=False,
        )
    )


def test_valid_unresolved_claim() -> None:
    validate_claim(
        _claim(
            raw_claim_field="annotation",
            raw_claim_value="unmapped_value",
            operational_status="unresolved",
            primary_target_eligible=False,
        )
    )


def test_rejects_curated_with_primary_target_eligible_false() -> None:
    claim = _claim(primary_target_eligible=False)
    with pytest.raises(RecordValidationError):
        validate_claim(claim)


@pytest.mark.parametrize("status", ["predicted", "excluded_likely", "unresolved"])
def test_rejects_primary_target_eligible_true_for_non_curated(status: str) -> None:
    claim = _claim(
        operational_status=status,
        primary_target_eligible=True,
    )
    with pytest.raises(RecordValidationError):
        validate_claim(claim)


@pytest.mark.parametrize(
    "status", ["curated", "predicted", "excluded_likely", "unresolved"]
)
def test_rejects_control_eligible_true_for_any_status(status: str) -> None:
    claim = _claim(
        operational_status=status,
        primary_target_eligible=status == "curated",
        control_eligible=True,
    )
    with pytest.raises(RecordValidationError):
        validate_claim(claim)


def test_claim_id_is_deterministic() -> None:
    first = make_claim_id(
        SOURCE_ID, SOURCE_RECORD_ID, RAW_FILE_PATH, RAW_ROW_OR_URL, RAW_CLAIM_FIELD
    )
    second = make_claim_id(
        SOURCE_ID, SOURCE_RECORD_ID, RAW_FILE_PATH, RAW_ROW_OR_URL, RAW_CLAIM_FIELD
    )
    assert first == second
    assert first.startswith(f"{SOURCE_ID}:")

    other_row = make_claim_id(
        SOURCE_ID, SOURCE_RECORD_ID, RAW_FILE_PATH, "row:2", RAW_CLAIM_FIELD
    )
    other_field = make_claim_id(
        SOURCE_ID, SOURCE_RECORD_ID, RAW_FILE_PATH, RAW_ROW_OR_URL, "function"
    )
    other_source_record = make_claim_id(
        SOURCE_ID, "MDB_002", RAW_FILE_PATH, RAW_ROW_OR_URL, RAW_CLAIM_FIELD
    )
    assert len({first, other_row, other_field, other_source_record}) == 4


@pytest.mark.parametrize(
    "field", ["raw_file_path", "raw_row_or_url", "raw_claim_field", "raw_claim_value"]
)
def test_rejects_missing_raw_provenance_fields(field: str) -> None:
    claim = _claim()
    del claim[field]
    with pytest.raises(RecordValidationError):
        validate_claim(claim)


@pytest.mark.parametrize(
    "field", ["raw_file_path", "raw_row_or_url", "raw_claim_field", "raw_claim_value"]
)
def test_rejects_empty_raw_provenance_fields(field: str) -> None:
    claim = _claim(**{field: ""})
    with pytest.raises(RecordValidationError):
        validate_claim(claim)


def test_rejects_effective_status() -> None:
    claim = _claim()
    claim["effective_status"] = "curated"
    with pytest.raises(RecordValidationError) as excinfo:
        validate_claim(claim)
    assert "effective_status" in str(excinfo.value)
