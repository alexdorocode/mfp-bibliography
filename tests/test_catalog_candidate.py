"""Packaging tests for the five-source catalog CANDIDATE."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = REPO_ROOT / "data/processed/mfp_catalog_mvp"
SCRIPT = REPO_ROOT / "scripts/package_catalog_candidate.py"
CANDIDATE_ID = "mfp-catalog-candidate-v0.2.0"
TABLES = [
    "mfp_proteins.csv", "mfp_source_records.csv", "mfp_identifiers.csv",
    "mfp_assertions.csv", "mfp_coverage.csv",
]


def run(catalog_dir: Path, releases_root: Path, verify: bool = False):
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(["--verify"] if verify else []),
         "--catalog-dir", str(catalog_dir), "--releases-root", str(releases_root)],
        capture_output=True, text=True, env=env)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def workspace(tmp_path):
    releases_root = tmp_path / "releases"
    releases_root.mkdir()
    return releases_root


class TestPackaging:

    def test_package_succeeds_and_contains_required_files(self, workspace):
        result = run(CATALOG_DIR, workspace)
        assert result.returncode == 0, result.stderr
        candidate = workspace / CANDIDATE_ID
        for name in TABLES + ["MANIFEST.json", "README.md", "DATA_DICTIONARY.md", "checksums.sha256"]:
            assert (candidate / name).is_file(), name

    def test_manifest_contract_counts_and_hash_sections(self, workspace):
        run(CATALOG_DIR, workspace)
        manifest = json.loads((workspace / CANDIDATE_ID / "MANIFEST.json").read_text())
        assert manifest["candidate_id"] == CANDIDATE_ID
        assert manifest["catalog_contract"] == "MFPB_0_19_MFP_CATALOG_MVP_V2"
        assert manifest["status"].startswith("CANDIDATE")
        counts = manifest["measured_counts"]
        assert counts["source_record_count"] == 2962
        assert counts["protein_entity_count"] == 2322
        assert counts["exact_uniprot_merge_count"] == 463
        assert counts["source_record_counts"]["SRC_MULTITASKPROTDB_II"] == 694
        assert "NOT source_record_count minus protein_entity_count" in \
            counts["metric_definitions"]["exact_uniprot_merge_count"]
        # whole-file vs per-MPID hash distinction
        assert manifest["inputs"]["raw_input_files"]["SRC_MOONDB"]["grain"] == "whole_file"
        assert "artifact_index_sha256_whole_file" in manifest["inputs"]["moonprot_per_mpid_hashes"]
        assert "Per-MPID" in manifest["inputs"]["moonprot_per_mpid_hashes"]["note"]
        # manifest does not hash itself
        assert "MANIFEST.json" not in manifest["packaged_outputs"]

    def test_packaged_tables_match_catalog_and_are_byte_identical_on_rerun(self, workspace):
        run(CATALOG_DIR, workspace)
        candidate = workspace / CANDIDATE_ID
        first = {p.name: sha(p) for p in sorted(candidate.iterdir()) if p.is_file()}
        for name in TABLES:
            assert sha(candidate / name) == sha(CATALOG_DIR / name)
        result = run(CATALOG_DIR, workspace)
        assert result.returncode == 0
        second = {p.name: sha(p) for p in sorted(candidate.iterdir()) if p.is_file()}
        assert first == second  # no volatile fields

    def test_multitask_rows_and_five_source_totals_in_packaged_candidate(self, workspace):
        run(CATALOG_DIR, workspace)
        candidate = workspace / CANDIDATE_ID
        with (candidate / "mfp_source_records.csv").open(newline="") as f:
            rows = list(csv.DictReader(f))
        counts = {}
        for r in rows:
            counts[r["source_name"]] = counts.get(r["source_name"], 0) + 1
        assert counts == {"SRC_MOONDB": 351, "SRC_MOONPROT": 702,
                          "SRC_MULTIFACETEDPROTDB": 1103,
                          "SRC_MULTITASKPROTDB_II": 694, "SRC_PLANTMP": 112}
        mt = [r for r in rows if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
        assert len({r["source_record_id"] for r in mt}) == 694

    def test_readme_states_candidate_and_limitations(self, workspace):
        run(CATALOG_DIR, workspace)
        readme = (workspace / CANDIDATE_ID / "README.md").read_text()
        assert "NOT the final v1 release" in readme
        assert "No verified article-to-GO relationships" in readme
        assert "542, 543 and 626 are unresolved" in readme
        assert "MPID 103 is known absent" in readme
        assert "NOT a scientific label" in readme
        assert "complete bibliography is claimed" in readme


class TestFailureBehavior:

    def test_tampered_catalog_fails_without_publishing(self, tmp_path):
        catalog_copy = tmp_path / "catalog"
        shutil.copytree(CATALOG_DIR, catalog_copy)
        summary = json.loads((catalog_copy / "summary.json").read_text())
        summary["protein_entity_count"] = 9999
        (catalog_copy / "summary.json").write_text(json.dumps(summary))
        releases_root = tmp_path / "releases"
        releases_root.mkdir()
        result = run(catalog_copy, releases_root)
        assert result.returncode != 0
        assert not (releases_root / CANDIDATE_ID).exists()
        assert not list(releases_root.glob("*.staging"))

    def test_verify_detects_tampered_packaged_file(self, workspace):
        run(CATALOG_DIR, workspace)
        candidate = workspace / CANDIDATE_ID
        table = candidate / "mfp_proteins.csv"
        table.write_text(table.read_text() + "tampered\n")
        result = run(CATALOG_DIR, workspace, verify=True)
        assert result.returncode != 0
        assert "hash mismatch" in result.stderr

    def test_never_overwrites_existing_candidate_with_different_bytes(self, tmp_path):
        releases_root = tmp_path / "releases"
        releases_root.mkdir()
        assert run(CATALOG_DIR, releases_root).returncode == 0
        candidate = releases_root / CANDIDATE_ID
        before = {p.name: sha(p) for p in sorted(candidate.iterdir()) if p.is_file()}
        # tamper one packaged byte, then attempt to repackage from the same catalog:
        # staged bytes would differ from the existing directory -> must refuse
        (candidate / "README.md").write_text(
            (candidate / "README.md").read_text() + "\ntampered\n")
        result = run(CATALOG_DIR, releases_root)
        assert result.returncode != 0
        assert "different bytes" in result.stderr
        after = {p.name: sha(p) for p in sorted(candidate.iterdir()) if p.is_file()}
        assert after["README.md"] != before["README.md"]  # existing dir left as-is (untouched by packager)
