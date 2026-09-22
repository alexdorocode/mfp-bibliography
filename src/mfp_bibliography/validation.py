"""Repository-level validation helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from mfp_bibliography.moondb_claims import load_moondb_provenance, read_claims_csv
from mfp_bibliography.schemas import build_validator
from mfp_bibliography.source_claims import validate_claim

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
    "docs/source-claim-policy.md",
    "configs/source_claim_policy_v0.1.yaml",
    "docs/source-claims-contract.md",
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
    "data/curated/source_claims.schema.json",
    "data/interim/source_claims_moondb.csv",
    "data/interim/source_claims_moondb_validation_report.json",
    "scripts/validate_repository.py",
    "scripts/build_source_claims_moondb.py",
    "src/mfp_bibliography/schemas.py",
    "src/mfp_bibliography/moondb_claims.py",
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


def _check_raw_directory_hygiene(root: Path) -> CheckResult:
    raw_root = root / "data" / "raw"
    offenders = sorted(
        path.relative_to(root).as_posix() for path in raw_root.rglob(".~lock.*")
    )
    if offenders:
        return CheckResult(
            "raw_directory_hygiene",
            False,
            f"Lock files are not allowed in data/raw: {', '.join(offenders)}",
        )
    return CheckResult("raw_directory_hygiene", True, "No lock files present in data/raw.")


def _check_schema(root: Path) -> CheckResult:
    schema_path = root / "data" / "curated" / "mfp_source_records.schema.json"
    try:
        build_validator(schema_path)
    except Exception as exc:  # pragma: no cover
        return CheckResult("json_schema", False, f"Schema validation failed: {exc}")
    return CheckResult("json_schema", True, "JSON Schema is valid Draft 2020-12.")


def _check_source_claims_schema(root: Path) -> CheckResult:
    schema_path = root / "data" / "curated" / "source_claims.schema.json"
    try:
        build_validator(schema_path)
    except Exception as exc:  # pragma: no cover
        return CheckResult("source_claims_json_schema", False, f"Schema validation failed: {exc}")
    return CheckResult(
        "source_claims_json_schema", True, "Source claims JSON Schema is valid Draft 2020-12."
    )


def _check_moondb_claims_artifact(root: Path) -> CheckResult:
    claims_path = root / "data" / "interim" / "source_claims_moondb.csv"
    if not claims_path.exists():
        return CheckResult(
            "moondb_claims_artifact",
            False,
            "data/interim/source_claims_moondb.csv is missing.",
        )
    try:
        provenance = load_moondb_provenance(root)
        claims = read_claims_csv(claims_path)
    except Exception as exc:  # pragma: no cover
        return CheckResult(
            "moondb_claims_artifact", False, f"MoonDB claims artifact check failed: {exc}"
        )

    problems: list[str] = []
    invalid_rows: list[str] = []
    for index, claim in enumerate(claims, start=2):
        try:
            validate_claim(claim)
        except Exception:
            invalid_rows.append(str(index))
    if invalid_rows:
        problems.append(f"schema-invalid CSV rows: {', '.join(invalid_rows[:5])}")
    if len(claims) != provenance.raw_row_count:
        problems.append(
            f"claim count {len(claims)} does not match manifest row_count_raw "
            f"{provenance.raw_row_count}"
        )
    claim_ids = [claim["claim_id"] for claim in claims]
    if len(set(claim_ids)) != len(claim_ids):
        problems.append("duplicate claim_id values present")
    if any(claim["control_eligible"] for claim in claims):
        problems.append("control_eligible=true found")

    if problems:
        return CheckResult("moondb_claims_artifact", False, "; ".join(problems))
    return CheckResult(
        "moondb_claims_artifact",
        True,
        f"MoonDB claims artifact reconciles: {len(claims)} claims, all valid.",
    )


def validate_repository(root: str | Path) -> dict[str, Any]:
    """Validate scaffold structure, manifest header, and schema validity."""
    root_path = Path(root).resolve()
    checks = [
        _check_paths(root_path),
        _check_raw_source_directories(root_path),
        _check_raw_directory_hygiene(root_path),
        _check_manifest_header(root_path),
        _check_manifest_bootstrap_state(root_path),
        _check_schema(root_path),
        _check_source_claims_schema(root_path),
        _check_moondb_claims_artifact(root_path),
    ]
    return {
        "ok": all(check.ok for check in checks),
        "checks": [asdict(check) for check in checks],
    }
