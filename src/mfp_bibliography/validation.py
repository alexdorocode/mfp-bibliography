"""Repository-level validation helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from mfp_bibliography.schemas import build_validator

EXPECTED_PATHS = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/project-charter.md",
    "docs/source-catalog.md",
    "docs/source-policy.md",
    "docs/data-governance.md",
    "docs/canonical-schema.md",
    "docs/release-policy.md",
    "docs/decisions/ADR-001-repository-scope.md",
    "docs/decisions/ADR-002-raw-data-immutability.md",
    "docs/decisions/ADR-003-provenance-and-transformations.md",
    "docs/decisions/ADR-004-evidence-label-benchmark-separation.md",
    "pyproject.toml",
    "data/raw/README.md",
    "data/manifests/source_manifest.csv",
    "data/curated/mfp_source_records.schema.json",
    "scripts/validate_repository.py",
    "src/mfp_bibliography/schemas.py",
    "tests/test_schema.py",
    ".github/workflows/ci.yml",
]

EXPECTED_RAW_SOURCE_DIRS = [
    "moonprot",
    "moondb",
    "multifacetedprotdb",
    "plantmp",
    "multitaskprotdb-ii",
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
    if not manifest_path.exists():
        return CheckResult("manifest_header", False, "source_manifest.csv is missing.")

    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != EXPECTED_MANIFEST_HEADER:
        return CheckResult("manifest_header", False, "source_manifest.csv header does not match required specification.")
    return CheckResult("manifest_header", True, "Manifest header matches expected value.")


def _check_raw_source_directories(root: Path) -> CheckResult:
    raw_root = root / "data" / "raw"
    missing = [name for name in EXPECTED_RAW_SOURCE_DIRS if not (raw_root / name).is_dir()]
    if missing:
        return CheckResult(
            "raw_source_directories",
            False,
            f"Missing required data/raw source directories: {', '.join(missing)}",
        )
    return CheckResult("raw_source_directories", True, "All expected data/raw source directories exist.")


def _check_manifest_bootstrap_state(root: Path) -> CheckResult:
    manifest_path = root / "data" / "manifests" / "source_manifest.csv"
    if not manifest_path.exists():
        return CheckResult("manifest_bootstrap_state", False, "source_manifest.csv is missing.")

    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 1:
        return CheckResult(
            "manifest_bootstrap_state",
            False,
            "source_manifest.csv must contain at least the header row.",
        )
    
    # Check header is present
    if lines[0] != EXPECTED_MANIFEST_HEADER:
        return CheckResult(
            "manifest_bootstrap_state",
            False,
            "source_manifest.csv header does not match expected specification.",
        )
    
    # If there are more lines, validate they have the correct number of columns
    if len(lines) > 1:
        for idx, line in enumerate(lines[1:], start=2):
            # Parse the line (basic CSV parsing - handle quoted fields if needed)
            # For now, just check it's not empty
            if not line.strip():
                return CheckResult(
                    "manifest_bootstrap_state",
                    False,
                    f"source_manifest.csv line {idx} is empty.",
                )
    
    return CheckResult("manifest_bootstrap_state", True, "Manifest structure is valid.")


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
    checks = [
        _check_paths(root_path),
        _check_raw_source_directories(root_path),
        _check_manifest_header(root_path),
        _check_manifest_bootstrap_state(root_path),
        _check_schema(root_path),
    ]
    return {
        "ok": all(check.ok for check in checks),
        "checks": [asdict(check) for check in checks],
    }
