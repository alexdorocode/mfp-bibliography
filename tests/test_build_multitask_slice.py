"""Unit tests for MultitaskProtDB-II slice builder script.

Verifies:
1. Execution of build_multitask_slice against real extract fixture.
2. Production of all 5 required artifacts.
3. Schema compliance of emitted CSV rows.
4. Total deterministic ordering.
5. Byte-reproducibility across repeated runs in separate directories.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from scripts.build_multitask_slice import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_FIXTURE_PATH,
    build_multitask_slice,
    compute_sha256,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CLAIMS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_claims.schema.json"
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "source_go_annotations.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "functional_coverage.schema.json"


@pytest.fixture
def claims_validator() -> Draft202012Validator:
    with CLAIMS_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema)


@pytest.fixture
def annotations_validator() -> Draft202012Validator:
    with ANNOTATIONS_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema)


@pytest.fixture
def coverage_validator() -> Draft202012Validator:
    with COVERAGE_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema)


def test_build_multitask_slice_produces_all_artifacts(
    claims_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify build_multitask_slice generates valid, verified package artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir)
        report = build_multitask_slice(
            input_fixture=DEFAULT_FIXTURE_PATH,
            output_dir=out_path,
            catalog_path=DEFAULT_CATALOG_PATH,
        )

        assert report["verification_status"] == "VERIFIED"
        assert report["counts_reconciliation"]["selected_records_count"] == 6
        assert report["counts_reconciliation"]["claims_extracted_count"] == 12
        assert report["counts_reconciliation"]["source_go_annotations_count"] == 45
        assert report["counts_reconciliation"]["coverage_records_count"] == 6

        # Check file existence
        claims_csv = out_path / "claims.csv"
        annotations_csv = out_path / "source_go_annotations.csv"
        coverage_csv = out_path / "coverage.csv"
        manifest_json = out_path / "manifest.json"
        report_json = out_path / "verification_report.json"

        assert claims_csv.exists()
        assert annotations_csv.exists()
        assert coverage_csv.exists()
        assert manifest_json.exists()
        assert report_json.exists()

        # Validate rows in claims.csv against Draft 2020-12
        with claims_csv.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            claims_rows = list(reader)
        assert len(claims_rows) == 12
        for r in claims_rows:
            obj = {k: (None if v == "" else (int(v) if k == "claim_index" else v)) for k, v in r.items()}
            claims_validator.validate(obj)

        # Validate rows in source_go_annotations.csv
        with annotations_csv.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ann_rows = list(reader)
        assert len(ann_rows) == 45
        for r in ann_rows:
            obj = {k: (None if v == "" else (int(v) if k == "annotation_index" else v)) for k, v in r.items()}
            annotations_validator.validate(obj)

        # Validate rows in coverage.csv
        with coverage_csv.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cov_rows = list(reader)
        assert len(cov_rows) == 6
        for r in cov_rows:
            obj = {k: (None if v == "" else (int(v) if k == "claims_extracted_count" else v)) for k, v in r.items()}
            coverage_validator.validate(obj)


def test_build_multitask_slice_byte_reproducibility() -> None:
    """Verify that building the slice twice produces byte-identical deterministic artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        out1 = Path(tmpdir1)
        out2 = Path(tmpdir2)

        build_multitask_slice(
            input_fixture=DEFAULT_FIXTURE_PATH,
            output_dir=out1,
            catalog_path=DEFAULT_CATALOG_PATH,
        )
        build_multitask_slice(
            input_fixture=DEFAULT_FIXTURE_PATH,
            output_dir=out2,
            catalog_path=DEFAULT_CATALOG_PATH,
        )

        for filename in ["claims.csv", "source_go_annotations.csv", "coverage.csv", "manifest.json"]:
            file1 = out1 / filename
            file2 = out2 / filename
            assert file1.read_bytes() == file2.read_bytes(), f"Byte mismatch in {filename}"
            assert compute_sha256(file1) == compute_sha256(file2)
