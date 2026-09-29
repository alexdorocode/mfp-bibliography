"""Focused tests for the Question 6 analysis (canonical-field completeness)."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from mfp_bibliography import analysis_q6

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/analyze_question6.py"
CANDIDATE = REPO_ROOT / "releases/mfp-catalog-candidate-v0.2.0"
PROTEIN_HEADER = ["protein_id", "canonical_uniprot_accession", "canonical_name",
                  "canonical_gene", "canonical_organism", "taxonomy_id",
                  "entity_status"]


def build_q6_candidate(tmp_path: Path, proteins: list[list[str]],
                       entity_count: int | None = None) -> Path:
    """Tiny candidate package with a sealed proteins table."""
    candidate = tmp_path / "mfp-catalog-candidate-v0.2.0"
    candidate.mkdir(parents=True)
    with (candidate / "mfp_proteins.csv").open("w", newline="") as handle:
        csv.writer(handle).writerows([PROTEIN_HEADER] + proteins)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = {
        "candidate_id": "mfp-catalog-candidate-v0.2.0",
        "catalog_contract": "TEST_CONTRACT",
        "protein_id_scheme": "TEST_SCHEME",
        "measured_counts": {
            "protein_entity_count": entity_count if entity_count is not None
            else len(proteins),
        },
        "packaged_outputs": {
            "mfp_proteins.csv": {"sha256": sha(candidate / "mfp_proteins.csv")},
        },
    }
    (candidate / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (candidate / "checksums.sha256").write_text(
        f"{sha(candidate / 'mfp_proteins.csv')}  mfp_proteins.csv\n")
    return candidate


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def make_rows() -> list[list[str]]:
    return [
        ["MFP:U:1", "P12345", "Protein A", "", "Human", "", "resolved"],
        # whitespace-only name counts as empty
        ["MFP:U:2", "P67890", "   ", "", "", "", "resolved"],
        # all optional fields empty
        ["MFP:U:3", "P11111", "", "", "", "", "resolved"],
    ]


class TestMeasurement:

    def test_four_fields_with_blank_and_whitespace_handling(self, tmp_path):
        candidate = build_q6_candidate(tmp_path, make_rows())
        output = tmp_path / "out"
        assert analysis_q6.run(candidate, output) == 0
        rows = {r["field"]: r for r in
                read_rows(output / "q6_canonical_completeness.csv")}
        assert set(rows) == {
            "canonical_uniprot_accession", "entity_status",
            "canonical_name", "canonical_organism"}
        assert rows["canonical_uniprot_accession"]["populated"] == "3"
        assert rows["entity_status"]["populated"] == "3"
        assert rows["canonical_name"]["populated"] == "1"  # whitespace-only = empty
        assert rows["canonical_organism"]["populated"] == "1"
        for row in rows.values():
            assert int(row["populated"]) + int(row["empty"]) == \
                int(row["denominator"]) == 3

    def test_deferred_fields_not_charged(self, tmp_path):
        candidate = build_q6_candidate(tmp_path, make_rows())
        output = tmp_path / "out"
        assert analysis_q6.run(candidate, output) == 0
        fields = {r["field"] for r in
                  read_rows(output / "q6_canonical_completeness.csv")}
        assert "canonical_gene" not in fields
        assert "taxonomy_id" not in fields
        readme = (output / "README.md").read_text()
        assert "canonical_gene" in readme and "DEFERRED" in readme


class TestFailureBehavior:

    def test_duplicate_protein_id_fails(self, tmp_path):
        proteins = make_rows()
        proteins.append(list(proteins[0]))  # duplicate protein_id
        candidate = build_q6_candidate(tmp_path, proteins, entity_count=4)
        assert analysis_q6.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_denominator_mismatch_vs_manifest_fails(self, tmp_path):
        candidate = build_q6_candidate(tmp_path, make_rows(), entity_count=99)
        assert analysis_q6.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()

    def test_missing_column_fails(self, tmp_path):
        candidate = tmp_path / "mfp-catalog-candidate-v0.2.0"
        candidate.mkdir(parents=True)
        with (candidate / "mfp_proteins.csv").open("w", newline="") as handle:
            csv.writer(handle).writerows([["protein_id", "entity_status"],
                                          ["MFP:U:1", "resolved"]])
        sha = hashlib.sha256((candidate / "mfp_proteins.csv").read_bytes()).hexdigest()
        manifest = {
            "candidate_id": "x", "catalog_contract": "T", "protein_id_scheme": "S",
            "measured_counts": {"protein_entity_count": 1},
            "packaged_outputs": {"mfp_proteins.csv": {"sha256": sha}},
        }
        (candidate / "MANIFEST.json").write_text(json.dumps(manifest))
        (candidate / "checksums.sha256").write_text(f"{sha}  mfp_proteins.csv\n")
        assert analysis_q6.run(candidate, tmp_path / "out") != 0

    def test_tampered_package_rejected_on_hash(self, tmp_path):
        candidate = build_q6_candidate(tmp_path, make_rows())
        table = candidate / "mfp_proteins.csv"
        table.write_text(table.read_text() + "tampered\n")
        assert analysis_q6.run(candidate, tmp_path / "out") != 0
        assert not (tmp_path / "out").exists()


class TestDeterminism:

    def test_deterministic_rerun_and_refuse_different_bytes(self, tmp_path):
        candidate = build_q6_candidate(tmp_path, make_rows())
        output = tmp_path / "out"
        assert analysis_q6.run(candidate, output) == 0
        first = {p.name: p.read_bytes() for p in sorted(output.iterdir())}
        assert analysis_q6.run(candidate, output) == 0
        assert {p.name: p.read_bytes() for p in sorted(output.iterdir())} == first
        (output / "q6_canonical_completeness.csv").write_text("changed\n")
        assert analysis_q6.run(candidate, output) != 0


class TestCliAgainstRealCandidate:

    def test_gate_then_analysis_on_pinned_candidate(self, tmp_path):
        output = tmp_path / "q6"
        env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--candidate-dir", str(CANDIDATE), "--output-dir", str(output)],
            capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        rows = {r["field"]: r for r in
                read_rows(output / "q6_canonical_completeness.csv")}
        assert rows["canonical_uniprot_accession"]["populated"] == "2322"
        assert rows["canonical_uniprot_accession"]["empty"] == "0"
        assert rows["entity_status"]["populated"] == "2322"
        assert rows["entity_status"]["empty"] == "0"
        assert rows["canonical_name"]["populated"] == "2056"
        assert rows["canonical_name"]["empty"] == "266"
        assert rows["canonical_organism"]["populated"] == "763"
        assert rows["canonical_organism"]["empty"] == "1559"
        for row in rows.values():
            assert int(row["populated"]) + int(row["empty"]) == \
                int(row["denominator"]) == 2322
        assert rows["canonical_name"]["percentage"] == "88.5"
        assert rows["canonical_organism"]["percentage"] == "32.9"
        provenance = json.loads((output / "analysis_manifest.json").read_text())
        assert provenance["derived_totals"]["protein_entity_count"] == 2322
        assert provenance["candidate"]["catalog_contract"] == \
            "MFPB_0_19_MFP_CATALOG_MVP_V2"
        readme = (output / "README.md").read_text()
        assert "NOT consensus" in readme
        assert "cannot" in readme.lower() or "CANNOT" in readme
