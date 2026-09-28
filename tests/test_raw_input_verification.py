"""Pre-build raw input verification gate for the MVP catalog."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

from mfp_bibliography.raw_input_verification import (  # noqa: E402
    load_source_file_sha256,
    verify_catalog_inputs,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _sha(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def make_minimal_root(tmp_path: Path) -> Path:
    """A minimal repository root whose consumed inputs verify cleanly."""
    root = tmp_path / "mini"
    moondb = "A\tP00001\tPredicted\n"
    plantmp = "id,uniport_id,type\n1,P00002,confirmed\n"
    html = "<html><body>mpid 1</body></html>"
    _write(root / "data/raw/moondb/all_emf_and_curated.tsv", moondb)
    _write(root / "data/raw/plantmp/PlantMP_all.csv", plantmp)
    _write(root / "data/raw/moonprot/mpid_1.html", html)
    _write(root / "data/raw/moonprot/artifact_index.csv",
           "mpid,url,retrieved_at,http_status,content_type,raw_file_path,sha256,file_size_bytes,parser_status,missing_fields\n"
           f"1,http://x/mpid=1,2026-09-22T00:00:00Z,200,text/html,data/raw/moonprot/mpid_1.html,{_sha(html)},{len(html)},ok,\n")
    mf_json = "{'protein': []}"
    _write(root / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json", mf_json)
    mt_csv = "UniProt,Protein_Name,Long_Description,Canonical_Function,GO,Moonlighting_function,GO_Moon,Organism,Human_Disease,Drugs,Induction,PDBs,PDB_UniProt,Models,Reference\nP00001,Alpha,,Kinase,GO:0000001,,GO:0000002,Human,,,,,,,Phyre,24814782\r\n"
    _write(root / "data/raw/multitaskprotdb-ii/proteins.csv", mt_csv)
    _write(root / "data/manifests/source_manifest.csv",
           "source_id,source_name,source_status,source_version,retrieved_at,acquisition_method,original_artifact_path,original_artifact_url,sha256,file_size_bytes,row_count_raw,license_or_terms,notes\n"
           f"SRC_MOONDB,MoonDB,imported,unknown,unknown,local_import,data/raw/moondb/all_emf_and_curated.tsv,unknown,{_sha(moondb)},{len(moondb)},1,to_be_verified,x\n"
           f"SRC_PLANTMP,PlantMP,imported,unknown,unknown,local_import,data/raw/plantmp/PlantMP_all.csv,unknown,{_sha(plantmp)},{len(plantmp)},1,to_be_verified,x\n"
           f"SRC_MULTIFACETEDPROTDB,MultifacetedProtDB,imported,unknown,unknown,local_import,data/raw/multifacetedprotdb/MultifacetedProtDB_data.json,unknown,{_sha(mf_json)},{len(mf_json)},0,to_be_verified,x\n"
           f"SRC_MULTITASKPROTDB_II,MultitaskProtDB-II,imported,unknown,unknown,local_import,data/raw/multitaskprotdb-ii/proteins.csv,unknown,{_sha(mt_csv)},{len(mt_csv)},1,to_be_verified,x\n")
    return root


class TestVerifyCatalogInputs:

    def test_valid_inputs_produce_no_errors(self, tmp_path):
        assert verify_catalog_inputs(make_minimal_root(tmp_path)) == []

    def test_real_repository_inputs_verify(self):
        assert verify_catalog_inputs(REPO_ROOT) == []

    def test_changed_byte_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        target = root / "data/raw/moondb/all_emf_and_curated.tsv"
        target.write_text("A\tP00009\tCurated\n", encoding="utf-8")
        errors = verify_catalog_inputs(root)
        assert any("hash mismatch for 'SRC_MOONDB'" in e for e in errors)

    def test_changed_moonprot_html_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        (root / "data/raw/moonprot/mpid_1.html").write_text(
            "<html><body>tampered</body></html>", encoding="utf-8")
        errors = verify_catalog_inputs(root)
        assert any("MoonProt HTML hash mismatch for MPID 1" in e for e in errors)

    def test_missing_consumed_file_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        (root / "data/raw/plantmp/PlantMP_all.csv").unlink()
        errors = verify_catalog_inputs(root)
        assert any("consumed raw artifact missing" in e for e in errors)

    def test_missing_manifest_entry_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        manifest = root / "data/manifests/source_manifest.csv"
        rows = list(csv.reader(manifest.read_text().splitlines()))
        rows = [rows[0]] + [r for r in rows[1:] if r[0] != "SRC_PLANTMP"]
        manifest.write_text("\n".join(",".join(r) for r in rows) + "\n")
        errors = verify_catalog_inputs(root)
        assert any("missing" in e and "SRC_PLANTMP" in e for e in errors)

    def test_duplicate_manifest_entry_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        manifest = root / "data/manifests/source_manifest.csv"
        duplicate = [r for r in manifest.read_text().splitlines() if r.startswith("SRC_MOONDB")][0]
        manifest.write_text(manifest.read_text() + duplicate + "\n")
        errors = verify_catalog_inputs(root)
        assert any("duplicate entry for source 'SRC_MOONDB'" in e for e in errors)

    def test_duplicate_moonprot_index_entry_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        index = root / "data/raw/moonprot/artifact_index.csv"
        duplicate = index.read_text().splitlines()[1]
        index.write_text(index.read_text() + duplicate + "\n")
        errors = verify_catalog_inputs(root)
        assert any("duplicate entry for MPID 1" in e for e in errors)

    def test_consumed_html_missing_from_index_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        _write(root / "data/raw/moonprot/mpid_2.html", "<html>2</html>")
        errors = verify_catalog_inputs(root)
        assert any("missing from" in e and "mpid_2.html" in e for e in errors)

    def test_index_entry_without_file_detected(self, tmp_path):
        root = make_minimal_root(tmp_path)
        (root / "data/raw/moonprot/mpid_1.html").unlink()
        errors = verify_catalog_inputs(root)
        assert any("has no raw file" in e for e in errors)

    def test_load_source_file_sha256_read_only(self, tmp_path):
        root = make_minimal_root(tmp_path)
        expected = _sha("A\tP00001\tPredicted\n")
        assert load_source_file_sha256(root, "SRC_MOONDB") == expected


class TestGateBlocksPublication:
    """A tampered raw input must fail the build before any output is written."""

    def test_build_fails_before_publishing_on_tampered_input(self, tmp_path):
        sandbox = tmp_path / "repo"
        (sandbox / "scripts").mkdir(parents=True)
        (sandbox / "data/interim").mkdir(parents=True)
        (sandbox / "data/raw").mkdir(parents=True)
        (sandbox / "data/manifests").mkdir(parents=True)
        import shutil
        shutil.copy(REPO_ROOT / "scripts/build_mfp_catalog_mvp.py", sandbox / "scripts/")
        shutil.copytree(REPO_ROOT / "src", sandbox / "src",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("source_claims_moondb.csv", "source_claims_plantmp.csv"):
            shutil.copy(REPO_ROOT / "data/interim" / name, sandbox / "data/interim/" / name)
        shutil.copy(REPO_ROOT / "data/manifests/source_manifest.csv",
                    sandbox / "data/manifests/")
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
        # Tamper with one acquired HTML after acquisition
        target = sandbox / "data/raw/moonprot/mpid_1.html"
        target.write_text(target.read_text(encoding="utf-8") + "<!--tampered-->", encoding="utf-8")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(sandbox / "src")
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts/build_mfp_catalog_mvp.py")],
            env=env, capture_output=True, text=True)
        assert result.returncode != 0
        assert "hash mismatch" in result.stderr
        out_dir = sandbox / "data/processed/mfp_catalog_mvp"
        assert not out_dir.exists() or not any(out_dir.iterdir()), \
            "outputs published despite input verification failure"
