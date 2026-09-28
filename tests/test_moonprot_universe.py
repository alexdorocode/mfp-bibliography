"""MoonProt snapshot universe boundary and fail-closed behavior."""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp"

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "build_mfp_catalog_mvp", REPO_ROOT / "scripts" / "build_mfp_catalog_mvp.py")
build = importlib.util.module_from_spec(spec)
sys.modules["build_mfp_catalog_mvp"] = build
spec.loader.exec_module(build)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_universe_root(tmp_path: Path) -> Path:
    """Minimal root with in-scope raw/index/absent evidence only."""
    root = tmp_path / "mini"
    html = "<html><body>mpid 1</body></html>"
    _write(root / "data/raw/moonprot/mpid_1.html", html)
    _write(root / "data/raw/moonprot/artifact_index.csv",
           "mpid,url,retrieved_at,http_status,content_type,raw_file_path,sha256,file_size_bytes,parser_status,missing_fields\n"
           "1,http://x,2026-09-22T00:00:00Z,200,text/html,data/raw/moonprot/mpid_1.html,"
           + hashlib.sha256(html.encode()).hexdigest() + f",{len(html)},ok,\n")
    _write(root / "data/interim/moonprot_absent_log.csv",
           "mpid,url,http_status,absent_marker,detected_at\n"
           "103,http://x/mpid=103,200,soft_404_template,2026-09-24T07:34:36Z\n")
    return root


class TestUniverseConstant:

    def test_universe_is_1_to_706_and_declared_snapshot_scope(self):
        assert (build.MOONPROT_SNAPSHOT_MPID_MIN, build.MOONPROT_SNAPSHOT_MPID_MAX) == (1, 706)
        universe = build.moonprot_universe_mpids()
        assert len(universe) == 706 and "1" in universe and "706" in universe

    def test_coverage_builder_uses_the_universe_constant(self):
        coverage = build.build_coverage([], {})
        assert len(coverage) == 706
        assert {row["mpid"] for row in coverage} == build.moonprot_universe_mpids()


class TestUniverseValidation:

    def test_in_scope_root_passes(self, tmp_path):
        assert build.validate_moonprot_universe(make_universe_root(tmp_path)) == []

    def test_out_of_range_raw_file_detected_with_exact_id(self, tmp_path):
        root = make_universe_root(tmp_path)
        _write(root / "data/raw/moonprot/mpid_999.html", "<html>999</html>")
        errors = build.validate_moonprot_universe(root)
        assert any("raw MoonProt files outside" in e and "'999'" in e.replace('"', "'") for e in errors), errors

    def test_out_of_range_index_entry_detected_with_exact_id(self, tmp_path):
        root = make_universe_root(tmp_path)
        index = root / "data/raw/moonprot/artifact_index.csv"
        index.write_text(index.read_text() +
                         "800,http://x,2026-09-22T00:00:00Z,200,text/html,,dead,0,ok,\n")
        errors = build.validate_moonprot_universe(root)
        assert any("artifact index MPIDs outside" in e and "800" in e for e in errors), errors

    def test_out_of_range_absent_log_entry_detected_with_exact_id(self, tmp_path):
        root = make_universe_root(tmp_path)
        log = root / "data/interim/moonprot_absent_log.csv"
        log.write_text(log.read_text() +
                       "800,http://x/mpid=800,200,soft_404_template,2026-09-24T07:34:36Z\n")
        errors = build.validate_moonprot_universe(root)
        assert any("absent log MPIDs outside" in e and "800" in e for e in errors), errors


class TestBoundaryClassification:
    """Boundary and missing IDs are classified from evidence, never assumed."""

    def test_boundary_ids_1_and_706_classified_from_evidence(self):
        with open(OUTPUT_DIR / "mfp_coverage.csv", newline="") as f:
            coverage = {row["mpid"]: row["status"] for row in csv.DictReader(f)}
        assert coverage["1"] == "acquired"
        assert coverage["706"] == "acquired"
        with open(OUTPUT_DIR / "mfp_source_records.csv", newline="") as f:
            records = {row["mpid"] for row in csv.DictReader(f)
                       if row["source_name"] == "SRC_MOONPROT"}
        assert "1" in records and "706" in records

    def test_missing_in_range_id_is_unresolved_not_assumed_absent(self):
        coverage = {row["mpid"]: row["status"] for row in build.build_coverage([], {})}
        assert coverage["542"] == "unresolved"
        assert coverage["706"] == "unresolved"

    def test_known_absent_from_evidence_not_assumption(self):
        coverage = {row["mpid"]: row["status"]
                    for row in build.build_coverage([], {"103": {"reason": "absent log"}})}
        assert coverage["103"] == "known_absent"


class TestFailClosedBuild:
    """Out-of-scope input must fail the build without replacing valid outputs."""

    def _sandbox(self, tmp_path):
        sandbox = tmp_path / "repo"
        (sandbox / "scripts").mkdir(parents=True)
        (sandbox / "data/interim").mkdir(parents=True)
        (sandbox / "data/raw").mkdir(parents=True)
        (sandbox / "data/raw/moondb").mkdir(parents=True)
        (sandbox / "data/raw/plantmp").mkdir(parents=True)
        (sandbox / "data/manifests").mkdir(parents=True)
        shutil.copy(REPO_ROOT / "scripts/build_mfp_catalog_mvp.py", sandbox / "scripts/")
        shutil.copytree(REPO_ROOT / "src", sandbox / "src",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("source_claims_moondb.csv", "source_claims_plantmp.csv"):
            shutil.copy(REPO_ROOT / "data/interim" / name, sandbox / "data/interim/" / name)
        shutil.copy(REPO_ROOT / "data/interim/moonprot_absent_log.csv",
                    sandbox / "data/interim/moonprot_absent_log.csv")
        shutil.copy(REPO_ROOT / "data/manifests/source_manifest.csv",
                    sandbox / "data/manifests/")
        shutil.copy(REPO_ROOT / "data/raw/moondb/all_emf_and_curated.tsv",
                    sandbox / "data/raw/moondb/all_emf_and_curated.tsv")
        shutil.copy(REPO_ROOT / "data/raw/plantmp/PlantMP_all.csv",
                    sandbox / "data/raw/plantmp/PlantMP_all.csv")
        shutil.copytree(REPO_ROOT / "data/raw/moonprot", sandbox / "data/raw/moonprot")
        (sandbox / "data/raw/multifacetedprotdb").mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json",
                    sandbox / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json")
        shutil.copy(REPO_ROOT / "data/interim/source_records_multifacetedprotdb.csv",
                    sandbox / "data/interim/source_records_multifacetedprotdb.csv")
        (sandbox / "data/raw/multitaskprotdb-ii").mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / "data/raw/multitaskprotdb-ii/proteins.csv",
                    sandbox / "data/raw/multitaskprotdb-ii/proteins.csv")
        shutil.copy(REPO_ROOT / "data/interim/source_records_multitaskprotdb_ii.csv",
                    sandbox / "data/interim/source_records_multitaskprotdb_ii.csv")
        return sandbox

    @staticmethod
    def _run(sandbox):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(sandbox / "src")
        return subprocess.run(
            [sys.executable, str(sandbox / "scripts/build_mfp_catalog_mvp.py")],
            env=env, capture_output=True, text=True)

    @staticmethod
    def _state(out_dir):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(out_dir.iterdir()) if p.is_file()}

    def test_out_of_scope_mpid_fails_and_preserves_existing_outputs(self, tmp_path):
        sandbox = self._sandbox(tmp_path)
        result = self._run(sandbox)
        assert result.returncode == 0, result.stderr
        out_dir = sandbox / "data/processed/mfp_catalog_mvp"
        valid_state = self._state(out_dir)

        html999 = "<html>999</html>"
        _write(sandbox / "data/raw/moonprot/mpid_999.html", html999)
        index = sandbox / "data/raw/moonprot/artifact_index.csv"
        index.write_text(index.read_text() +
                         "999,http://x,2026-09-22T00:00:00Z,200,text/html,"
                         "data/raw/moonprot/mpid_999.html,"
                         + hashlib.sha256(html999.encode()).hexdigest()
                         + f",{len(html999)},ok,\n")
        result = self._run(sandbox)
        assert result.returncode != 0
        assert "999" in result.stderr
        assert "universe" in result.stderr
        assert self._state(out_dir) == valid_state, "failed build replaced valid outputs"
