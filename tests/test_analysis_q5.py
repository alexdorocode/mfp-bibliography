"""Focused tests for the Question 5 v2 analysis (corrected label provenance)."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from mfp_bibliography import analysis_q5

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/analyze_question5.py"
CANDIDATE = REPO_ROOT / "releases/mfp-catalog-candidate-v0.3.0"
RECORD_HEADER = ["source_name", "source_record_id", "protein_id",
                 "source_status", "operational_status",
                 "raw_claim_field", "raw_claim_value"]


def build_q5_candidate(tmp_path: Path, records: list[list[str]],
                       source_counts: dict[str, int]) -> Path:
    """Tiny candidate package with a sealed records table."""
    candidate = tmp_path / "mfp-catalog-candidate-v0.2.0"
    candidate.mkdir(parents=True)
    with (candidate / "mfp_source_records.csv").open("w", newline="") as handle:
        csv.writer(handle).writerows([RECORD_HEADER] + records)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = {
        "candidate_id": "mfp-catalog-candidate-v0.2.0",
        "catalog_contract": "TEST_CONTRACT",
        "protein_id_scheme": "TEST_SCHEME",
        "measured_counts": {
            "source_record_count": len(records),
            "protein_entity_count": len({r[2] for r in records}),
            "source_record_counts": source_counts,
        },
        "packaged_outputs": {
            "mfp_source_records.csv": {
                "sha256": sha(candidate / "mfp_source_records.csv")},
        },
    }
    (candidate / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (candidate / "checksums.sha256").write_text(
        f"{sha(candidate / 'mfp_source_records.csv')}  mfp_source_records.csv\n")
    return candidate


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


class TestRawVersusMapped:

    def test_raw_label_grouped_and_mapped_reported_separately(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[
                ["SRC_PLANTMP", "a1", "p1", "excluded_likely", "excluded_likely",
                 "type", "likely"],
                ["SRC_PLANTMP", "a2", "p2", "curated", "curated",
                 "type", "confirmed"],
                ["SRC_MOONDB", "b1", "p3", "predicted", "predicted",
                 "type", "Predicted"],
            ],
            source_counts={"SRC_PLANTMP": 2, "SRC_MOONDB": 1})
        output = tmp_path / "out"
        assert analysis_q5.run(candidate, output) == 0
        availability = read_rows(output / "q5_status_availability_v2.csv")
        # verbatim raw values, original spelling/case preserved
        assert {(r["source_name"], r["status_availability"], r["status_label"],
                 r["record_count"]) for r in availability} == {
            ("SRC_PLANTMP", "source_provided_label", "confirmed", "1"),
            ("SRC_PLANTMP", "source_provided_label", "likely", "1"),
            ("SRC_MOONDB", "source_provided_label", "Predicted", "1"),
        }
        policy = read_rows(output / "q5_policy_mapped_status_v2.csv")
        assert {(r["source_name"], r["policy_mapped_status"], r["record_count"])
                for r in policy} == {
            ("SRC_PLANTMP", "curated", "1"),
            ("SRC_PLANTMP", "excluded_likely", "1"),
            ("SRC_MOONDB", "predicted", "1"),
        }

    def test_wrong_raw_claim_field_fails(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONDB", "a1", "p1", "predicted", "predicted",
                      "Models", "Predicted"]],
            source_counts={"SRC_MOONDB": 1})
        assert analysis_q5.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_missing_raw_claim_value_fails(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONDB", "a1", "p1", "predicted", "predicted",
                      "type", ""]],
            source_counts={"SRC_MOONDB": 1})
        assert analysis_q5.run(candidate, tmp_path / "out") != 0


class TestMoonProtTechnicalStatus:

    def test_loader_generated_status_shown_as_technical_only(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONPROT", "m1", "p1", "valid", "valid", "", ""]],
            source_counts={"SRC_MOONPROT": 1})
        output = tmp_path / "out"
        assert analysis_q5.run(candidate, output) == 0
        availability = read_rows(output / "q5_status_availability_v2.csv")
        assert availability == [
            {"source_name": "SRC_MOONPROT",
             "status_availability": "loader_generated_technical_status",
             "status_label": "valid", "record_count": "1"},
        ]
        # no source-provided label, no policy-mapped row for MoonProt
        assert all(r["status_availability"] != "source_provided_label"
                   for r in availability)
        assert read_rows(output / "q5_policy_mapped_status_v2.csv") == []

    def test_moonprot_with_raw_claim_fails(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONPROT", "m1", "p1", "valid", "valid",
                      "type", "predicted"]],
            source_counts={"SRC_MOONPROT": 1})
        assert analysis_q5.run(candidate, tmp_path / "out") != 0


class TestPlantMPLikely:

    def test_likely_records_retained_with_source_exclusive_entities(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[
                ["SRC_PLANTMP", "a1", "p1", "excluded_likely", "excluded_likely",
                 "type", "likely"],
                ["SRC_PLANTMP", "a2", "p2", "excluded_likely", "excluded_likely",
                 "type", "likely"],
                # p2 also claimed by MoonDB: not source-exclusive
                ["SRC_MOONDB", "b1", "p2", "predicted", "predicted",
                 "type", "Predicted"],
            ],
            source_counts={"SRC_PLANTMP": 2, "SRC_MOONDB": 1})
        output = tmp_path / "out"
        assert analysis_q5.run(candidate, output) == 0
        availability = read_rows(output / "q5_status_availability_v2.csv")
        likely = [r for r in availability if r["status_label"] == "likely"]
        assert likely and likely[0]["record_count"] == "2"  # retained, not removed
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        plantmp = provenance["derived_totals"]["plantmp_likely"]
        assert plantmp["records"] == 2
        assert plantmp["source_exclusive_protein_ids"] == 1
        assert plantmp["retained_in_catalog"] is True


class TestMissingStatusAndConservation:

    def test_status_less_sources_counted_as_not_provided(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MULTIFACETEDPROTDB", "a1", "p1", "", "unresolved", "", ""],
                     ["SRC_MULTITASKPROTDB_II", "b1", "p2", "", "unresolved", "", ""]],
            source_counts={"SRC_MULTIFACETEDPROTDB": 1,
                           "SRC_MULTITASKPROTDB_II": 1})
        output = tmp_path / "out"
        assert analysis_q5.run(candidate, output) == 0
        availability = read_rows(output / "q5_status_availability_v2.csv")
        assert {r["status_availability"] for r in availability} == {"not_provided"}

    def test_administrative_status_relabeled_fails(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MULTIFACETEDPROTDB", "a1", "p1", "unresolved",
                      "unresolved", "", ""]],
            source_counts={"SRC_MULTIFACETEDPROTDB": 1})
        assert analysis_q5.run(candidate, tmp_path / "out") != 0

    def test_count_conservation_mismatch_fails(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONDB", "a1", "p1", "predicted", "predicted",
                      "type", "Predicted"]],
            source_counts={"SRC_MOONDB": 5})
        assert analysis_q5.run(candidate, tmp_path / "out") != 0

    def test_tampered_candidate_fails_on_hash(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONDB", "a1", "p1", "predicted", "predicted",
                      "type", "Predicted"]],
            source_counts={"SRC_MOONDB": 1})
        table = candidate / "mfp_source_records.csv"
        table.write_text(table.read_text() + "tampered\n")
        assert analysis_q5.run(candidate, tmp_path / "out") != 0

    def test_deterministic_rerun_and_refuse_different_bytes(self, tmp_path):
        candidate = build_q5_candidate(
            tmp_path,
            records=[["SRC_MOONDB", "a1", "p1", "predicted", "predicted",
                      "type", "Predicted"]],
            source_counts={"SRC_MOONDB": 1})
        output = tmp_path / "out"
        assert analysis_q5.run(candidate, output) == 0
        first = {p.name: p.read_bytes() for p in sorted(output.iterdir())}
        assert analysis_q5.run(candidate, output) == 0
        assert {p.name: p.read_bytes() for p in sorted(output.iterdir())} == first
        (output / "q5_status_availability_v2.csv").write_text("changed\n")
        assert analysis_q5.run(candidate, output) != 0


class TestCliAgainstRealCandidate:

    def test_gate_then_analysis_on_pinned_candidate(self, tmp_path):
        output = tmp_path / "q5v2"
        env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--candidate-dir", str(CANDIDATE), "--output-dir", str(output)],
            capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        availability = read_rows(output / "q5_status_availability_v2.csv")
        labels = {(r["source_name"], r["status_availability"], r["status_label"]):
                  int(r["record_count"]) for r in availability}
        assert labels == {
            ("SRC_MOONDB", "source_provided_label", "Curated"): 62,
            ("SRC_MOONDB", "source_provided_label", "Predicted"): 289,
            ("SRC_PLANTMP", "source_provided_label", "confirmed"): 62,
            ("SRC_PLANTMP", "source_provided_label", "likely"): 12,
            ("SRC_PLANTMP", "source_provided_label", "predicted"): 38,
            ("SRC_MOONPROT", "loader_generated_technical_status", "valid"): 702,
            ("SRC_MULTIFACETEDPROTDB", "not_provided", "not_provided"): 1103,
            ("SRC_MULTITASKPROTDB_II", "not_provided", "not_provided"): 694,
        }
        by_source: dict[str, int] = {}
        for row in availability:
            by_source[row["source_name"]] = \
                by_source.get(row["source_name"], 0) + int(row["record_count"])
        assert by_source == {"SRC_MOONDB": 351, "SRC_MOONPROT": 702,
                             "SRC_MULTIFACETEDPROTDB": 1103,
                             "SRC_MULTITASKPROTDB_II": 694, "SRC_PLANTMP": 112}
        assert sum(by_source.values()) == 2962
        policy = read_rows(output / "q5_policy_mapped_status_v2.csv")
        mapped = {(r["source_name"], r["policy_mapped_status"]): int(r["record_count"])
                  for r in policy}
        assert mapped == {
            ("SRC_MOONDB", "curated"): 62, ("SRC_MOONDB", "predicted"): 289,
            ("SRC_PLANTMP", "curated"): 62,
            ("SRC_PLANTMP", "excluded_likely"): 12,
            ("SRC_PLANTMP", "predicted"): 38,
        }
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["derived_totals"]["plantmp_likely"][
            "source_exclusive_protein_ids"] == 11
        assert provenance["candidate"]["catalog_contract"] == \
            "MFPB_0_19_MFP_CATALOG_MVP_V2"
