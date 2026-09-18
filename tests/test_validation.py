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
