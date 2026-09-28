"""MultifacetedProtDB interim source-record adapter tests."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography.multifacetedprotdb_records import (
    MULTIFACETEDPROTDB_SOURCE_ID,
    MultifacetedProtDBFormatError,
    MultifacetedProtDBRecordError,
    cross_check_txt_companion,
    load_source_records,
    parse_literal_payload,
    resolve_operational_status,
    write_records_csv,
)
from mfp_bibliography.raw_input_verification import load_source_file_sha256

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_JSON = REPO_ROOT / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json"
RAW_TXT = REPO_ROOT / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt"
POLICY = {
    "default_status": "unresolved",
    "unmapped_sources": [MULTIFACETEDPROTDB_SOURCE_ID],
}

VALID_LITERAL = (
    "{'protein': [{'uniprot': 'P00001', 'name': 'Alpha', 'annotation': 5.0, 'genes': 'AAA'},"
    "{'uniprot': 'P00002', 'name': 'Beta', 'annotation': 4.0, 'genes': 'BBB'}]}"
)


def write_fixture(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "artifact.json"
    path.write_text(content, encoding="utf-8")
    return path


class TestLiteralFormat:

    def test_artifact_is_python_literal_not_strict_json(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        with pytest.raises(json.JSONDecodeError):
            json.loads(path.read_text(encoding="utf-8"))
        payload = parse_literal_payload(path.read_text(encoding="utf-8"))
        assert len(payload["protein"]) == 2

    def test_malformed_shapes_rejected(self, tmp_path):
        for bad in (
            "[]",                                  # top-level list
            "{'proteins': []}",                    # wrong key
            "{'protein': [], 'extra': 1}",         # extra top-level key
            "{'protein': 'not-a-list'}",           # protein not a list
            "not a literal at all (",              # unparseable
        ):
            with pytest.raises(MultifacetedProtDBFormatError):
                parse_literal_payload(bad)

    def test_eval_is_never_used(self):
        # ast.literal_eval refuses expressions; a payload containing a function
        # call must fail rather than execute
        with pytest.raises(MultifacetedProtDBFormatError):
            parse_literal_payload("{'protein': [__import__('os').listdir('.')]}")


class TestRecordValidation:

    def test_valid_records_parsed_with_stable_ids(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        records = load_source_records(path)
        assert [r["source_record_id"] for r in records] == [
            "multifacetedprotdb_row_1", "multifacetedprotdb_row_2"]
        assert records[0]["uniprot_raw"] == "P00001"
        assert records[0]["uniprot_normalized"] == "P00001"

    def test_duplicate_accession_rejected_with_exact_diagnostics(self, tmp_path):
        path = write_fixture(tmp_path,
            "{'protein': [{'uniprot': 'P00001', 'name': 'A', 'annotation': 5.0, 'genes': 'G'},"
            "{'uniprot': 'p00001', 'name': 'A2', 'annotation': 5.0, 'genes': 'G'}]}")
        with pytest.raises(MultifacetedProtDBRecordError, match="record 2.*record 1"):
            load_source_records(path)

    def test_missing_or_malformed_accession_rejected(self, tmp_path):
        for bad_entry in (
            "{'uniprot': '', 'name': 'A', 'annotation': 5.0, 'genes': 'G'}",
            "{'uniprot': None, 'name': 'A', 'annotation': 5.0, 'genes': 'G'}",
            "{'uniprot': 'P00001', 'name': 'A', 'genes': 'G'}",
            "{'uniprot': 'P00001', 'name': 'A', 'annotation': 'high', 'genes': 'G'}",
        ):
            content = "{'protein': [" + bad_entry + "]}"
            with pytest.raises(MultifacetedProtDBRecordError):
                load_source_records(write_fixture(tmp_path, content))

    def test_hash_mismatch_rejected_before_any_output(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        wrong = "0" * 64
        with pytest.raises(MultifacetedProtDBRecordError, match="hash mismatch"):
            load_source_records(path, expected_sha256=wrong)

    def test_correct_hash_accepted(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records = load_source_records(path, expected_sha256=digest)
        assert records[0]["raw_file_sha256"] == digest


class TestStatusSemantics:

    def test_no_status_invented_and_annotation_preserved_verbatim(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        records = load_source_records(path)
        out = tmp_path / "out.csv"
        write_records_csv(records, out, operational_status=resolve_operational_status(POLICY))
        rows = list(csv.DictReader(out.open(newline="")))
        assert all(row["status_original"] == "" for row in rows)
        assert all(row["operational_status"] == "unresolved" for row in rows)
        assert rows[0]["annotation_raw"] == "5.0"  # verbatim, semantics unknown

    def test_policy_must_declare_source_unmapped(self):
        with pytest.raises(MultifacetedProtDBRecordError):
            resolve_operational_status({"default_status": "unresolved", "unmapped_sources": []})


class TestDeterminism:

    def test_output_bytes_are_deterministic(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        out1, out2 = tmp_path / "a.csv", tmp_path / "b.csv"
        for out in (out1, out2):
            write_records_csv(load_source_records(path), out,
                              operational_status=resolve_operational_status(POLICY))
        assert out1.read_bytes() == out2.read_bytes()


class TestTxtCrossCheck:

    def test_disagreement_reported_exactly(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        records = load_source_records(path)
        txt = tmp_path / "companion.txt"
        txt.write_text("P00001,P00003", encoding="utf-8")
        divergences = cross_check_txt_companion(txt, records)
        assert any("P00003" in d for d in divergences)
        assert any("P00002" in d for d in divergences)

    def test_agreeing_companion_passes(self, tmp_path):
        path = write_fixture(tmp_path, VALID_LITERAL)
        records = load_source_records(path)
        txt = tmp_path / "companion.txt"
        txt.write_text("P00002,P00001", encoding="utf-8")
        assert cross_check_txt_companion(txt, records) == []


class TestRegisteredInput:

    def test_real_registered_artifact_loads(self):
        expected = load_source_file_sha256(REPO_ROOT, MULTIFACETEDPROTDB_SOURCE_ID)
        records = load_source_records(RAW_JSON, expected_sha256=expected)
        assert len(records) == 1103
        assert len({r["uniprot_normalized"] for r in records}) == 1103
        assert all(r["source_record_id"].startswith("multifacetedprotdb_row_") for r in records)

    def test_real_txt_companion_matches_canonical_artifact(self):
        records = load_source_records(RAW_JSON)
        assert cross_check_txt_companion(RAW_TXT, records) == []

    def test_interim_output_now_integrated_in_catalog(self):
        out = REPO_ROOT / "data/interim/source_records_multifacetedprotdb.csv"
        assert out.exists()
        with out.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 1103
        catalog = REPO_ROOT / "data/processed/mfp_catalog_mvp/mfp_source_records.csv"
        with catalog.open(newline="") as handle:
            catalog_rows = [r for r in csv.DictReader(handle)
                            if r["source_name"] == MULTIFACETEDPROTDB_SOURCE_ID]
        assert len(catalog_rows) == 1103
