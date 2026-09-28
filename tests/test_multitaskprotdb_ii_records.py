"""MultitaskProtDB-II interim source-record adapter tests."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from mfp_bibliography.multitaskprotdb_ii_records import (
    MULTITASKPROTDB_II_SOURCE_ID,
    EXPECTED_HEADER,
    MultitaskProtDBIIRecordError,
    build_validation_report,
    classify_reference,
    load_source_records,
    resolve_operational_status,
    write_records_csv,
)
from mfp_bibliography.raw_input_verification import load_source_file_sha256

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data/raw/multitaskprotdb-ii/proteins.csv"

HEADER = ",".join(EXPECTED_HEADER)


def make_csv(tmp_path: Path, rows: list[list[str]], with_bom: bool = True) -> Path:
    """Write a fixture CSV with UTF-8-SIG BOM and CRLF terminators."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(EXPECTED_HEADER)
    for row in rows:
        writer.writerow(row)
    path = tmp_path / "proteins.csv"
    path.write_bytes(buffer.getvalue().encode("utf-8-sig" if with_bom else "utf-8"))
    return path


def full_row(uniprot="P00001", name="Alpha", function="Kinase", moon="Receptor",
             ref="24814782", organism="Human", go="GO:0005840; C:ribosome; IEA:UniProtKB-KW."):
    return [uniprot, name, "", function, go, moon, "", organism, "", "", "", "", "", "Phyre", ref]


class TestFormatAndBinding:

    def test_real_input_loads_with_bom_and_crlf(self):
        expected = load_source_file_sha256(REPO_ROOT, MULTITASKPROTDB_II_SOURCE_ID)
        records, anomalies = load_source_records(RAW, expected_sha256=expected)
        assert len(records) == 694
        assert len({r["uniprot_normalized"] for r in records}) == 685
        assert len(anomalies) == 3

    def test_hash_failure_blocks_before_output(self, tmp_path):
        path = make_csv(tmp_path, [full_row()])
        with pytest.raises(MultitaskProtDBIIRecordError, match="hash mismatch"):
            load_source_records(path, expected_sha256="0" * 64)

    def test_unexpected_schema_rejected(self, tmp_path):
        path = tmp_path / "bad.csv"
        path.write_text("Wrong,Header\r\n1,2\r\n", encoding="utf-8-sig")
        with pytest.raises(MultitaskProtDBIIRecordError, match="unexpected schema"):
            load_source_records(path)

    def test_malformed_or_missing_accession_rejected(self, tmp_path):
        for bad in ("", "not an accession!", "P0000"):
            path = make_csv(tmp_path, [full_row(uniprot=bad)])
            with pytest.raises(MultitaskProtDBIIRecordError, match="malformed UniProt"):
                load_source_records(path)


class TestRowGrainAndStableIds:

    def test_repeated_accession_rows_are_distinct_records(self, tmp_path):
        path = make_csv(tmp_path, [
            full_row(uniprot="A1KFR2", name="Variant A", ref="11111111"),
            full_row(uniprot="A1KFR2", name="Variant B", ref="22222222"),
        ])
        records, _ = load_source_records(path)
        assert len(records) == 2
        assert [r["source_record_id"] for r in records] == [
            "multitaskprotdb_ii_row_1", "multitaskprotdb_ii_row_2"]
        assert {r["uniprot_normalized"] for r in records} == {"A1KFR2"}
        assert records[0]["protein_name_raw"] != records[1]["protein_name_raw"]

    def test_ids_stable_across_identical_runs(self, tmp_path):
        path = make_csv(tmp_path, [full_row(), full_row(uniprot="P00002")])
        first, _ = load_source_records(path)
        second, _ = load_source_records(path)
        assert [r["source_record_id"] for r in first] == [r["source_record_id"] for r in second]

    def test_go_text_preserved_verbatim(self, tmp_path):
        go = "GO:0003735; F:structural constituent of ribosome; IEA:UniProtKB-KW.\nGO:0006412; P:translation; IDA:PMID:123."
        path = make_csv(tmp_path, [full_row(go=go)])
        records, _ = load_source_records(path)
        assert records[0]["go_raw"] == go


class TestStatusAndAnomalies:

    def test_null_source_status_no_invented_claims(self, tmp_path):
        path = make_csv(tmp_path, [full_row()])
        records, _ = load_source_records(path)
        out = tmp_path / "out.csv"
        policy = {"default_status": "unresolved",
                  "unmapped_sources": [MULTITASKPROTDB_II_SOURCE_ID]}
        write_records_csv(records, out, operational_status=resolve_operational_status(policy))
        rows = list(csv.DictReader(out.open(newline="")))
        assert all(r["status_original"] == "" for r in rows)
        assert all(r["operational_status"] == "unresolved" for r in rows)
        report = build_validation_report(records, [], "unresolved", path)
        assert report["evidence_claims"] == 0
        assert report["status_original"] is None

    def test_policy_must_list_source_as_unmapped(self):
        with pytest.raises(MultitaskProtDBIIRecordError):
            resolve_operational_status({"default_status": "unresolved", "unmapped_sources": []})

    def test_reference_anomalies_flagged_at_field_level(self, tmp_path):
        rows = [
            full_row(uniprot="P00001", ref="24814782"),
            full_row(uniprot="P00002", ref="HIV-1 and murine leukemia virus infection (omim:600534)"),
            full_row(uniprot="P00003", ref="4ENL"),
            full_row(uniprot="P00004", ref=""),
        ]
        path = make_csv(tmp_path, rows)
        records, anomalies = load_source_records(path)
        assert len(records) == 4  # no row excluded
        flags = {r["source_record_id"]: (r["reference_article_like"], r["reference_anomaly"])
                 for r in records}
        assert flags["multitaskprotdb_ii_row_1"] == ("true", "")
        assert flags["multitaskprotdb_ii_row_2"] == ("false", "not_article_identifier")
        assert flags["multitaskprotdb_ii_row_3"] == ("false", "not_article_identifier")
        assert flags["multitaskprotdb_ii_row_4"] == ("false", "missing")
        # verbatim text retained; never converted to PMID/DOI
        assert records[1]["reference_raw"].startswith("HIV-1")
        assert records[2]["reference_raw"] == "4ENL"
        assert len(anomalies) == 3

    def test_classify_reference_boundaries(self):
        assert classify_reference("24814782") == ("true", "")
        assert classify_reference("24814782, 20167618") == ("true", "")
        assert classify_reference("") == ("false", "missing")
        assert classify_reference("4ENL") == ("false", "not_article_identifier")


class TestRegisteredInputAndOutput:

    def test_interim_output_matches_real_input(self):
        out = REPO_ROOT / "data/interim/source_records_multitaskprotdb_ii.csv"
        assert out.exists()
        with out.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 694
        assert len({r["source_record_id"] for r in rows}) == 694
        assert all(r["status_original"] == "" for r in rows)
        assert all(r["raw_file_sha256"] ==
                   "84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482"
                   for r in rows)
        report = json.loads(
            (REPO_ROOT / "data/interim/source_records_multitaskprotdb_ii_validation_report.json").read_text())
        assert report["record_count"] == 694
        assert report["catalog_integrated"] is False
