"""Focused tests for the Question 2 analysis (exact source-set overlap)."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography import analysis_q2

from tests.test_analysis_q1 import build_candidate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/analyze_question2.py"
CANDIDATE = REPO_ROOT / "releases/mfp-catalog-candidate-v0.2.0"


def build_q2_candidate(tmp_path: Path, records: list[list[str]],
                       proteins: list[list[str]]) -> Path:
    """Q1 fixture plus the exact_uniprot_merge_count Q2 requires."""
    candidate = build_candidate(tmp_path, records, proteins)
    source_sets: dict[str, set[str]] = {}
    for source_name, _, protein_id in records:
        source_sets.setdefault(protein_id, set()).add(source_name)
    merges = sum(1 for sources in source_sets.values() if len(sources) >= 2)
    manifest_path = candidate / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["measured_counts"]["exact_uniprot_merge_count"] = merges
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return candidate


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


class TestAggregation:

    def test_repeated_rows_in_one_source_count_once(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_A", "a2", "p1"],
                     ["SRC_B", "b1", "p2"]],
            proteins=[["p1"], ["p2"]])
        output = tmp_path / "out"
        assert analysis_q2.run(candidate, output) == 0
        rows = read_rows(output / "q2_exclusive_combinations.csv")
        # p1 (two SRC_A rows) counts once in the SRC_A combination, not twice
        assert rows == [
            {"source_set": "SRC_A", "protein_count": "1"},
            {"source_set": "SRC_B", "protein_count": "1"},
        ]
        assert sum(int(r["protein_count"]) for r in rows) == 2

    def test_entity_in_three_sources_one_combination_three_pairs(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"],
                     ["SRC_C", "c1", "p1"]],
            proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q2.run(candidate, output) == 0
        exclusive = read_rows(output / "q2_exclusive_combinations.csv")
        assert exclusive == [{"source_set": "SRC_A|SRC_B|SRC_C", "protein_count": "1"}]
        pairwise = read_rows(output / "q2_pairwise_overlap_secondary_inclusive.csv")
        inclusive = {f'{r["source_a"]}|{r["source_b"]}': int(r["inclusive_protein_count"])
                     for r in pairwise}
        assert inclusive == {"SRC_A|SRC_B": 1, "SRC_A|SRC_C": 1, "SRC_B|SRC_C": 1}
        # a 3-source protein contributes to 3 pairs but exactly one combination
        assert sum(int(r["protein_count"]) for r in exclusive) == 1

    def test_all_pairs_listed_including_zero_counts(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"],
                     ["SRC_C", "c1", "p2"]],
            proteins=[["p1"], ["p2"]])
        output = tmp_path / "out"
        assert analysis_q2.run(candidate, output) == 0
        pairwise = read_rows(output / "q2_pairwise_overlap_secondary_inclusive.csv")
        assert len(pairwise) == 3  # all pairs of 3 sources, zeros included
        by_pair = {f'{r["source_a"]}|{r["source_b"]}': r["inclusive_protein_count"]
                   for r in pairwise}
        assert by_pair["SRC_B|SRC_C"] == "0"


class TestFailureBehavior:

    def test_orphan_protein_id_fails_without_outputs(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p_missing"]],
            proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q2.run(candidate, output) != 0
        assert not output.exists()

    def test_unsourced_packaged_protein_fails(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"]],
            proteins=[["p1"], ["p2"]])  # p2 has no source records
        assert analysis_q2.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_merge_count_mismatch_vs_manifest_fails(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"]],
            proteins=[["p1"]])
        manifest_path = candidate / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["measured_counts"]["exact_uniprot_merge_count"] = 99
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        assert analysis_q2.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_expected_bins_mismatch_fails(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"]],
            proteins=[["p1"]])
        assert analysis_q2.run(
            candidate, tmp_path / "out", expected_bins={1: 5}) != 0
        assert not (tmp_path / "out").exists()


class TestDeterminism:

    def test_source_order_invariance(self, tmp_path):
        records = [["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"],
                   ["SRC_A", "a2", "p2"], ["SRC_C", "c1", "p3"]]
        out1, out2 = tmp_path / "out1", tmp_path / "out2"
        assert analysis_q2.run(
            build_q2_candidate(tmp_path / "c1", records, [["p1"], ["p2"], ["p3"]]),
            out1) == 0
        assert analysis_q2.run(
            build_q2_candidate(
                tmp_path / "c2", list(reversed(records)), [["p1"], ["p2"], ["p3"]]),
            out2) == 0
        assert (out1 / "q2_exclusive_combinations.csv").read_bytes() == \
            (out2 / "q2_exclusive_combinations.csv").read_bytes()
        assert (out1 / "q2_pairwise_overlap_secondary_inclusive.csv").read_bytes() == \
            (out2 / "q2_pairwise_overlap_secondary_inclusive.csv").read_bytes()

    def test_idempotent_rerun_and_refuse_different_bytes(self, tmp_path):
        candidate = build_q2_candidate(
            tmp_path,
            records=[["SRC_A", "a1", "p1"], ["SRC_B", "b1", "p1"]],
            proteins=[["p1"]])
        output = tmp_path / "out"
        assert analysis_q2.run(candidate, output) == 0
        first = (output / "q2_exclusive_combinations.csv").read_bytes()
        assert analysis_q2.run(candidate, output) == 0
        assert (output / "q2_exclusive_combinations.csv").read_bytes() == first
        (output / "q2_exclusive_combinations.csv").write_text("changed\n")
        assert analysis_q2.run(candidate, output) != 0


class TestCliAgainstRealCandidate:

    def test_gate_then_analysis_on_pinned_candidate(self, tmp_path):
        output = tmp_path / "q2"
        env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--candidate-dir", str(CANDIDATE), "--output-dir", str(output)],
            capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        exclusive = read_rows(output / "q2_exclusive_combinations.csv")
        assert sum(int(r["protein_count"]) for r in exclusive) == 2322
        assert sum(int(r["protein_count"]) for r in exclusive
                   if "|" in r["source_set"]) == 463
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["derived_totals"]["distinct_source_count_bins"] == \
            {"1": 1859, "2": 361, "3": 83, "4": 19, "5": 0}
        assert provenance["derived_totals"]["protein_entity_count"] == 2322
        assert provenance["candidate"]["catalog_contract"] == \
            "MFPB_0_19_MFP_CATALOG_MVP_V2"
        pairwise = read_rows(output / "q2_pairwise_overlap_secondary_inclusive.csv")
        assert len(pairwise) == 10  # all pairs of five sources, zeros included
        assert (output / "q2_source_overlap.svg").is_file()
