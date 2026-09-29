"""Offline PACKAGE_VERIFY tests for the packaged catalog candidate.

Unlike ``test_catalog_candidate.py`` (packaging + REBUILD_COMPARE), these
tests require nothing outside ``releases/mfp-catalog-candidate-v0.2.0/`` —
no ``data/processed/``, raw or interim inputs — so they run in a clean
clone.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/package_catalog_candidate.py"
CANDIDATE_ID = "mfp-catalog-candidate-v0.2.0"
REPO_RELEASES = REPO_ROOT / "releases"
TABLES = [
    "mfp_proteins.csv", "mfp_source_records.csv", "mfp_identifiers.csv",
    "mfp_assertions.csv", "mfp_coverage.csv",
]


def run_verify_package(releases_root: Path):
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--verify-package",
         "--releases-root", str(releases_root)],
        capture_output=True, text=True, env=env)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def candidate_copy(tmp_path):
    """Temporary copy of the packaged candidate; failures never touch the real one."""
    releases_root = tmp_path / "releases"
    releases_root.mkdir()
    shutil.copytree(REPO_RELEASES / CANDIDATE_ID, releases_root / CANDIDATE_ID)
    return releases_root / CANDIDATE_ID


def reseal_hashes(candidate: Path, table: str) -> None:
    """Update MANIFEST.json and checksums.sha256 for a re-sealed tampered table."""
    manifest_path = candidate / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["packaged_outputs"][table]["sha256"] = sha(candidate / table)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    lines = []
    for line in (candidate / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        if name == table or name == "MANIFEST.json":
            digest = sha(candidate / name)
        lines.append(f"{digest}  {name}")
    (candidate / "checksums.sha256").write_text("\n".join(lines) + "\n")


class TestPackageVerifyOffline:

    def test_pristine_candidate_passes_offline(self):
        result = run_verify_package(REPO_RELEASES)
        assert result.returncode == 0, result.stderr
        assert "PACKAGE_VERIFY OK" in result.stdout

    def test_tampered_csv_fails_with_hash_diagnostic(self, candidate_copy):
        table = candidate_copy / "mfp_proteins.csv"
        table.write_text(table.read_text() + "tampered\n")
        result = run_verify_package(candidate_copy.parent)
        assert result.returncode != 0
        assert "mfp_proteins.csv" in result.stderr
        assert "mismatch" in result.stderr

    def test_missing_csv_fails_with_missing_diagnostic(self, candidate_copy):
        (candidate_copy / "mfp_assertions.csv").unlink()
        result = run_verify_package(candidate_copy.parent)
        assert result.returncode != 0
        assert "missing packaged files" in result.stderr
        assert "mfp_assertions.csv" in result.stderr

    def test_missing_manifest_fails(self, candidate_copy):
        (candidate_copy / "MANIFEST.json").unlink()
        result = run_verify_package(candidate_copy.parent)
        assert result.returncode != 0
        assert "MANIFEST.json" in result.stderr
        assert "missing" in result.stderr

    def test_hash_consistent_tamper_caught_by_foreign_key_check(self, candidate_copy):
        """A tampered CSV re-sealed into MANIFEST/checksums must still fail."""
        table = candidate_copy / "mfp_source_records.csv"
        with table.open(newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames
            rows = list(reader)
        rows[0]["protein_id"] = "MFP:U:000000000000000"  # orphan FK target
        with table.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        reseal_hashes(candidate_copy, "mfp_source_records.csv")
        result = run_verify_package(candidate_copy.parent)
        assert result.returncode != 0
        assert "missing proteins" in result.stderr

    def test_failure_never_writes_into_candidate(self, candidate_copy):
        table = candidate_copy / "mfp_coverage.csv"
        table.write_text(table.read_text() + "tampered\n")
        before = {p.name: sha(p) for p in sorted(candidate_copy.iterdir()) if p.is_file()}
        result = run_verify_package(candidate_copy.parent)
        assert result.returncode != 0
        after = {p.name: sha(p) for p in sorted(candidate_copy.iterdir()) if p.is_file()}
        assert after == before

    def test_requires_no_data_processed_directory(self, tmp_path):
        """PACKAGE_VERIFY must not read data/processed even if absent (clean clone)."""
        sandbox = tmp_path / "clean-clone"
        (sandbox / "src").mkdir(parents=True)
        shutil.copytree(REPO_ROOT / "src/mfp_bibliography", sandbox / "src/mfp_bibliography")
        shutil.copytree(REPO_ROOT / "scripts", sandbox / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(REPO_RELEASES / CANDIDATE_ID, sandbox / "releases" / CANDIDATE_ID)
        assert not (sandbox / "data").exists()  # no raw, interim or processed inputs
        env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(sandbox / "src")}
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts/package_catalog_candidate.py"),
             "--verify-package"],
            capture_output=True, text=True, env=env, cwd=sandbox)
        assert result.returncode == 0, result.stderr
        assert "PACKAGE_VERIFY OK" in result.stdout
