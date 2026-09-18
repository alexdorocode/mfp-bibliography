from __future__ import annotations

import shutil
from pathlib import Path

from mfp_bibliography.validation import validate_repository


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_validator_succeeds_for_scaffold() -> None:
    result = validate_repository(REPO_ROOT)
    assert result["ok"] is True


def test_repository_validator_fails_for_invalid_manifest_header(tmp_path) -> None:
    copied = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, copied)
    manifest = copied / "data" / "manifests" / "source_manifest.csv"
    manifest.write_text("bad,header\n", encoding="utf-8")

    result = validate_repository(copied)
    assert result["ok"] is False
    names = {check["name"]: check for check in result["checks"]}
    assert names["manifest_header"]["ok"] is False


def test_repository_validator_succeeds_with_data_rows(tmp_path) -> None:
    copied = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, copied)
    manifest = copied / "data" / "manifests" / "source_manifest.csv"
    with manifest.open("a", encoding="utf-8") as handle:
        handle.write("SRC_MOONDB,MoonDB,imported,unknown,unknown,local_import,data/raw/moondb/all_emf_and_curated.tsv,unknown,c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55,8331,351,to_be_verified,test\n")

    result = validate_repository(copied)
    assert result["ok"] is True
    names = {check["name"]: check for check in result["checks"]}
    assert names["manifest_bootstrap_state"]["ok"] is True


def test_repository_validator_fails_when_expected_raw_source_dir_missing(tmp_path) -> None:
    copied = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, copied)
    shutil.rmtree(copied / "data" / "raw" / "plantmp")

    result = validate_repository(copied)
    assert result["ok"] is False
    names = {check["name"]: check for check in result["checks"]}
    assert names["raw_source_directories"]["ok"] is False


def test_repository_validator_fails_when_governance_file_missing(tmp_path) -> None:
    copied = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, copied)
    (copied / "docs" / "source-policy.md").unlink()

    result = validate_repository(copied)
    assert result["ok"] is False
    names = {check["name"]: check for check in result["checks"]}
    assert names["required_paths"]["ok"] is False
