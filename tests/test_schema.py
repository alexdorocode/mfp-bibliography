from __future__ import annotations

import pytest

from mfp_bibliography.schemas import RecordValidationError, validate_record


def _valid_record() -> dict[str, object]:
    return {
        "record_id": "SRC_MOONDB:abc123",
        "source_id": "SRC_MOONDB",
        "source_record_id": "MDB_001",
        "uniprot_id": "P12345",
        "protein_name": "Example protein",
        "organism_raw": "unknown",
        "scientific_label": "unknown",
        "evidence_tier": "unresolved",
        "benchmark_role": "unassigned",
        "source_version": "unknown",
        "retrieved_at": "unknown",
        "raw_file_path": "data/raw/moondb/example.csv",
        "raw_row_or_url": "row:1",
        "transformation_id": "bootstrap_placeholder",
        "record_status": "incomplete",
        "notes": None,
    }


def test_schema_accepts_valid_minimal_record() -> None:
    validate_record(_valid_record())


def test_schema_rejects_invalid_controlled_vocabulary() -> None:
    record = _valid_record()
    record["scientific_label"] = "INVALID"
    with pytest.raises(RecordValidationError):
        validate_record(record)


def test_schema_rejects_missing_mandatory_provenance_field() -> None:
    record = _valid_record()
    del record["raw_file_path"]
    with pytest.raises(RecordValidationError):
        validate_record(record)
