"""Repository-level validation helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from mfp_bibliography.schemas import build_validator

EXPECTED_PATHS = [
    "README.md",
    "pyproject.toml",
    "data/raw/README.md",
    "data/manifests/source_manifest.csv",
    "data/curated/mfp_source_records.schema.json",
    "scripts/validate_repository.py",
    "src/mfp_bibliography/schemas.py",
    "tests/test_schema.py",
    ".github/workflows/ci.yml",
]

EXPECTED_MANIFEST_HEADER = (
    "source_id,source_name,source_status,source_version,retrieved_at,acquisition_method,"
    "original_artifact_path,original_artifact_url,sha256,file_size_bytes,row_count_raw,"
    "license_or_terms,notes"
)


@dataclass
class CheckResult:
    name: str
    ok: bool
    message: str


def _check_paths(root: Path) -> CheckResult:
    missing = [path for path in EXPECTED_PATHS if not (root / path).exists()]
    if missing:
        return CheckResult("required_paths", False, f"Missing required paths: {', '.join(missing)}")
    return CheckResult("required_paths", True, "All required paths exist.")


def _check_manifest_header(root: Path) -> CheckResult:
    manifest_path = root / "data" / "manifests" / "source_manifest.csv"
    header = manifest_path.read_text(encoding="utf-8").splitlines()[0] if manifest_path.exists() else ""
    if header != EXPECTED_MANIFEST_HEADER:
        return CheckResult("manifest_header", False, "source_manifest.csv header does not match required specification.")
    return CheckResult("manifest_header", True, "Manifest header matches expected value.")


def _check_schema(root: Path) -> CheckResult:
    schema_path = root / "data" / "curated" / "mfp_source_records.schema.json"
    try:
        build_validator(schema_path)
    except Exception as exc:  # pragma: no cover
        return CheckResult("json_schema", False, f"Schema validation failed: {exc}")
    return CheckResult("json_schema", True, "JSON Schema is valid Draft 2020-12.")


def validate_repository(root: str | Path) -> dict[str, Any]:
    """Validate scaffold structure, manifest header, and schema validity."""
    root_path = Path(root).resolve()
    checks = [_check_paths(root_path), _check_manifest_header(root_path), _check_schema(root_path)]
    return {
        "ok": all(check.ok for check in checks),
        "checks": [asdict(check) for check in checks],
    }
