"""Focused tests for the Question 1 analysis (records vs unique proteins).

Tiny fixture candidates exercise the library gates (input hashes, FK
integrity, conservation) without the real package; one CLI test runs the
full PACKAGE_VERIFY gate against the real candidate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography import analysis_q1

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/analyze_question1.py"
CANDIDATE = REPO_ROOT / "releases/mfp-catalog-candidate-v0.2.0"
RECORD_HEADER = ["source_name", "source_record_id", "protein_id"]
PROTEIN_HEADER = ["protein_id"]


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="") as handle:
        csv.writer(handle).writerows([header] + rows)


def build_candidate(tmp_path: Path, records: list[list[str]],
                   proteins: list[list[str]]) -> Path:
    """Tiny candidate package with consistent MANIFEST and checksums."""
    candidate = tmp_path / "mfp-catalog-candidate-v0.2.0"
    candidate.mkdir(parents=True)
    _write_csv(candidate / "mfp_source_records.csv", RECORD_HEADER, records)
    _write_csv(candidate / "mfp_proteins.csv", PROTEIN_HEADER, proteins)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    per_source: dict[str, int] = {}
    for row in records:
        per_source[row[0]] = per_source.get(row[0], 0) + 1
    manifest = {
        "candidate_id": "mfp-catalog-candidate-v0.2.0",
        "catalog_contract": "TEST_CONTRACT",
        "protein_id_scheme": "TEST_SCHEME",
        "measured_counts": {
            "source_record_count": len(records),
            "protein_entity_count": len(set(p[0] for p in proteins)),
            "source_record_counts": per_source,
        },
        "packaged_outputs": {
            "mfp_source_records.csv": {"sha256": sha(candidate / "mfp_source_records.csv")},
            "mfp_proteins.csv": {"sha256": sha(candidate / "mfp_proteins.csv")},
        },
    }
    (candidate / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    lines = [
        f"{sha(candidate / name)}  {name}"
        for name in ("mfp_source_records.csv", "mfp_proteins.csv")]
    (candidate / "checksums.sha256").write_text("\n".join(lines) + "\n")
    return candidate


class TestAggregation:

    def test_shared_proteins_counted_per_source_not_summed_globally(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_A", "a2", "p2"],
                     ["SRC_B", "b1", "p2"], ["SRC_B", "b2", "p3"]],
            proteins=[["p1"], ["p2"], ["p3"]])
        manifest = analysis_q1.load_manifest(candidate)
        rows, totals = analysis_q1.aggregate(candidate, manifest)
        by_source = {r["source_name"]: r for r in rows}
        assert by_source["SRC_A"]["unique_protein_count"] == 2
        assert by_source["SRC_B"]["unique_protein_count"] == 2
        assert totals["protein_entity_count"] == 3
        # per-source unique counts sum to 4, global entities are 3: not additive
        assert sum(r["unique_protein_count"] for r in rows) != totals["protein_entity_count"]

    def test_repeated_rows_within_source_count_once_as_protein(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_A", "a2", "p1"], ["SRC_B", "b1", "p2"]],
            proteins=[["p1"], ["p2"]])
        rows, totals = analysis_q1.aggregate(
            candidate, analysis_q1.load_manifest(candidate))
        by_source = {r["source_name"]: r for r in rows}
        assert by_source["SRC_A"]["source_record_count"] == 2
        assert by_source["SRC_A"]["unique_protein_count"] == 1
        assert totals["source_record_count"] == 3

    def test_deterministic_source_order(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_B", "b1", "p1"], ["SRC_A", "a1", "p1"]],
            proteins=[["p1"]])
        rows, _ = analysis_q1.aggregate(
            candidate, analysis_q1.load_manifest(candidate))
        assert [r["source_name"] for r in rows] == ["SRC_A", "SRC_B"]


class TestFailureBehavior:

    def test_malformed_fk_fails_without_outputs(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p_missing"]],
            proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q1.run(candidate, output) != 0
        assert not output.exists()

    def test_tampered_candidate_fails_on_input_hash(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"]], proteins=[["p1"]])
        table = candidate / "mfp_source_records.csv"
        table.write_text(table.read_text() + "tampered\n")
        assert analysis_q1.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_totals_mismatch_vs_manifest_fails(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"]], proteins=[["p1"]])
        manifest = json.loads((candidate / "MANIFEST.json").read_text())
        manifest["measured_counts"]["source_record_count"] = 99
        (candidate / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
        # re-seal checksums for MANIFEST is not needed: input hashes still match
        assert analysis_q1.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()


class TestOutputs:

    def test_deterministic_bytes_and_idempotent_rerun(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"]],
            proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q1.run(candidate, output) == 0
        first = {p.name: p.read_bytes()
                 for p in sorted(output.iterdir()) if p.is_file()}
        assert analysis_q1.run(candidate, output) == 0  # identical bytes: idempotent
        second = {p.name: p.read_bytes()
                  for p in sorted(output.iterdir()) if p.is_file()}
        assert first == second

    def test_refuses_overwrite_with_different_bytes(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"]], proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q1.run(candidate, output) == 0
        (output / "q1_records_vs_entities.csv").write_text("changed\n")
        assert analysis_q1.run(candidate, output) != 0

    def test_provenance_records_contract_hashes_and_rule(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"]], proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q1.run(candidate, output) == 0
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["candidate"]["catalog_contract"] == "TEST_CONTRACT"
        assert "not additive" in provenance["aggregation_rule"]
        for name in analysis_q1.INPUT_TABLES:
            assert provenance["inputs"][name]["sha256"]
        assert provenance["outputs"]["q1_records_vs_entities.svg"]["sha256"]
        assert "timestamp" not in json.dumps(provenance).lower().replace(
            "timestamps", "")

    def test_svg_escapes_untrusted_text(self, tmp_path):
        candidate = build_candidate(
            tmp_path,
            records=[["SRC_<&x>", "a1", "p1"]], proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q1.run(candidate, output) == 0
        svg = (output / "q1_records_vs_entities.svg").read_text()
        assert "SRC_&lt;&amp;x&gt;" in svg
        assert "SRC_<&x>" not in svg


class TestCliAgainstRealCandidate:

    def test_gate_then_analysis_on_pinned_candidate(self, tmp_path):
        output = tmp_path / "q1"
        env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--candidate-dir", str(CANDIDATE), "--output-dir", str(output)],
            capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        rows = list(csv.DictReader(
            (output / "q1_records_vs_entities.csv").open(newline="")))
        assert len(rows) == 5
        by_source = {r["source_name"]: r for r in rows}
        assert by_source["SRC_MOONDB"]["source_record_count"] == "351"
        assert by_source["SRC_MULTIFACETEDPROTDB"]["source_record_count"] == "1103"
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["candidate"]["catalog_contract"] == \
            "MFPB_0_19_MFP_CATALOG_MVP_V2"
        assert provenance["derived_totals"]["protein_entity_count"] == 2322
        assert provenance["derived_totals"]["source_record_count"] == 2962
