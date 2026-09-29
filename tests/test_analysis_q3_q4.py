"""Focused tests for the Question 3 and Question 4 analyses."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from mfp_bibliography import analysis_q3, analysis_q4

from tests.test_analysis_q2 import build_q2_candidate
from tests.test_analysis_q1 import build_candidate

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = REPO_ROOT / "releases/mfp-catalog-candidate-v0.2.0"
COVERAGE_HEADER = ["mpid", "status"]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def add_coverage(candidate: Path, coverage_rows: list[list[str]],
                 status_counts: dict[str, int]) -> None:
    """Attach a sealed mfp_coverage.csv to a tiny candidate package."""
    with (candidate / "mfp_coverage.csv").open("w", newline="") as handle:
        csv.writer(handle).writerows([COVERAGE_HEADER] + coverage_rows)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest_path = candidate / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["measured_counts"]["moonprot_coverage"] = status_counts
    manifest["packaged_outputs"]["mfp_coverage.csv"] = {
        "sha256": sha(candidate / "mfp_coverage.csv")}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    lines = (candidate / "checksums.sha256").read_text().splitlines()
    lines.append(f"{sha(candidate / 'mfp_coverage.csv')}  mfp_coverage.csv")
    (candidate / "checksums.sha256").write_text("\n".join(lines) + "\n")


class TestQ3:

    def test_repeated_same_source_rows_count_once(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_A", "a2", "p1"],
                     ["SRC_B", "b1", "p2"]],
            proteins=[["p1"], ["p2"]])
        output = tmp_path / "out"
        assert analysis_q3.run(candidate, output) == 0
        rows = read_rows(output / "q3_sources_per_protein.csv")
        # p1 has two SRC_A rows but counts once in bin 1
        assert rows == [
            {"distinct_source_count": "1", "protein_count": "2"},
            {"distinct_source_count": "2", "protein_count": "0"},
        ]

    def test_zero_bins_included_and_pinned_mismatch_fails(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p2"]],
            proteins=[["p1"], ["p2"]])
        output = tmp_path / "out"
        assert analysis_q3.run(candidate, output) == 0
        rows = read_rows(output / "q3_sources_per_protein.csv")
        assert [r["distinct_source_count"] for r in rows] == ["1", "2"]
        assert rows[1]["protein_count"] == "0"  # zero bin present
        assert analysis_q3.run(
            candidate, tmp_path / "out2",
            expected_bins={1: 1, 2: 1}) != 0  # wrong pinned expectation

    def test_deterministic_and_refuses_different_bytes(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"]],
            proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q3.run(candidate, output) == 0
        first = (output / "q3_sources_per_protein.csv").read_bytes()
        assert analysis_q3.run(candidate, output) == 0
        assert (output / "q3_sources_per_protein.csv").read_bytes() == first
        (output / "q3_sources_per_protein.csv").write_text("changed\n")
        assert analysis_q3.run(candidate, output) != 0


class TestQ4:

    def build(self, tmp_path, coverage_rows, status_counts, records=None):
        candidate = build_candidate(
            tmp_path,
            records=records or [["SRC_A", "a1", "p1"]],
            proteins=[["p1"]])
        add_coverage(candidate, coverage_rows, status_counts)
        return candidate

    def test_status_counts_and_denominator(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["2", "acquired"],
                           ["3", "unresolved"], ["4", "known_absent"]],
            status_counts={"acquired": 2, "known_absent": 1, "unresolved": 1})
        output = tmp_path / "out"
        assert analysis_q4.run(
            candidate, output,
            expected_known_absent=(4,), expected_unresolved=(3,)) == 0
        rows = read_rows(output / "q4_moonprot_coverage_status.csv")
        assert rows == [
            {"status": "acquired", "mpid_count": "2"},
            {"status": "known_absent", "mpid_count": "1"},
            {"status": "unresolved", "mpid_count": "1"},
        ]

    def test_duplicate_mpid_fails(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["1", "acquired"]],
            status_counts={"acquired": 2, "known_absent": 0, "unresolved": 0})
        assert analysis_q4.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_missing_mpid_fails(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["3", "acquired"]],
            status_counts={"acquired": 2, "known_absent": 0, "unresolved": 0})
        assert analysis_q4.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_unexpected_status_fails(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["2", "maybe"]],
            status_counts={"acquired": 2, "known_absent": 0, "unresolved": 0})
        assert analysis_q4.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_wrong_specific_mpid_status_fails(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["2", "unresolved"]],
            status_counts={"acquired": 1, "known_absent": 0, "unresolved": 1})
        assert analysis_q4.run(
            candidate, tmp_path / "out",
            expected_known_absent=(2,)) != 0  # MPID 2 is unresolved, not absent

    def test_tampered_coverage_fails_on_hash(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["2", "unresolved"]],
            status_counts={"acquired": 1, "known_absent": 0, "unresolved": 1})
        table = candidate / "mfp_coverage.csv"
        table.write_text(table.read_text() + "tampered\n")
        assert analysis_q4.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_deterministic_rerun(self, tmp_path):
        candidate = self.build(
            tmp_path,
            coverage_rows=[["1", "acquired"], ["2", "unresolved"]],
            status_counts={"acquired": 1, "known_absent": 0, "unresolved": 1})
        output = tmp_path / "out"
        assert analysis_q4.run(candidate, output) == 0
        first = {p.name: p.read_bytes() for p in sorted(output.iterdir())}
        assert analysis_q4.run(candidate, output) == 0
        assert {p.name: p.read_bytes() for p in sorted(output.iterdir())} == first


class TestCliAgainstRealCandidate:

    def run_cli(self, question: str, output: Path) -> int:
        env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / f"analyze_question{question}.py"),
             "--candidate-dir", str(CANDIDATE), "--output-dir", str(output)],
            capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        return result.returncode

    def test_q3_on_pinned_candidate(self, tmp_path):
        output = tmp_path / "q3"
        self.run_cli("3", output)
        rows = read_rows(output / "q3_sources_per_protein.csv")
        assert rows == [
            {"distinct_source_count": "1", "protein_count": "1859"},
            {"distinct_source_count": "2", "protein_count": "361"},
            {"distinct_source_count": "3", "protein_count": "83"},
            {"distinct_source_count": "4", "protein_count": "19"},
            {"distinct_source_count": "5", "protein_count": "0"},
        ]
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["derived_totals"]["protein_entity_count"] == 2322

    def test_q4_on_pinned_candidate(self, tmp_path):
        output = tmp_path / "q4"
        self.run_cli("4", output)
        rows = read_rows(output / "q4_moonprot_coverage_status.csv")
        assert rows == [
            {"status": "acquired", "mpid_count": "702"},
            {"status": "known_absent", "mpid_count": "1"},
            {"status": "unresolved", "mpid_count": "3"},
        ]
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["derived_totals"]["universe_size"] == 706
        assert provenance["derived_totals"]["known_absent_mpids"] == [103]
        assert provenance["derived_totals"]["unresolved_mpids"] == [542, 543, 626]
        assert provenance["candidate"]["catalog_contract"] == \
            "MFPB_0_19_MFP_CATALOG_MVP_V2"
