#!/usr/bin/env python3
"""Build and verify a persistent six-record MultitaskProtDB-II pilot package.

Usage:
    python scripts/build_multitask_slice.py [options]

Generates:
    - claims.csv
    - source_go_annotations.csv
    - coverage.csv
    - manifest.json
    - verification_report.json

All data artifacts are byte-stable and deterministically sorted.
Volatile execution metadata is strictly isolated in verification_report.json.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

from mfp_bibliography.functional_claims_multitask import (
    ANNOTATION_ID_SCHEME_VERSION,
    CLAIM_ID_SCHEME_VERSION,
    EXTRACTION_METHOD,
    SOURCE_ID,
    extract_multitask_slice_from_file,
)
from mfp_bibliography.normalization import make_protein_id_uniprot, normalize_uniprot_accession


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "functional_claims_multitask" / "multitask_real_extract.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "interim" / "pilot" / "multitask_slice"
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp" / "mfp_source_records.csv"
SCHEMAS_DIR = REPO_ROOT / "data" / "curated"

CLAIMS_SCHEMA_PATH = SCHEMAS_DIR / "functional_claims.schema.json"
ANNOTATIONS_SCHEMA_PATH = SCHEMAS_DIR / "source_go_annotations.schema.json"
COVERAGE_SCHEMA_PATH = SCHEMAS_DIR / "functional_coverage.schema.json"

GIT_COMMIT_BASELINE = "a6def6fef01f345f38532d30779d5b576b079580"

# Original row locators and characteristics from fixture documentation
RECORD_SCOPE_LOCATORS = [
    {
        "fixture_row": 1,
        "source_record_id": "multitaskprotdb_ii_row_1",
        "parent_row_locator": "row:1",
        "parent_source_record_id": "multitaskprotdb_ii_row_1",
        "uniprot_id": "A0A059U5R2",
        "protein_name": "60S ribosomal protein L44",
        "organism": "Aspergillus glaucus",
    },
    {
        "fixture_row": 2,
        "source_record_id": "multitaskprotdb_ii_row_2",
        "parent_row_locator": "row:2",
        "parent_source_record_id": "multitaskprotdb_ii_row_2",
        "uniprot_id": "A0A0H2Q1X0",
        "protein_name": "Glutamine synthetase",
        "organism": "Bifidobacterium bifidum",
    },
    {
        "fixture_row": 3,
        "source_record_id": "multitaskprotdb_ii_row_3",
        "parent_row_locator": "row:3",
        "parent_source_record_id": "multitaskprotdb_ii_row_3",
        "uniprot_id": "A0A0H3CDS3",
        "protein_name": "Bifunctional regulator KidO",
        "organism": "Caulobacter crescentus",
    },
    {
        "fixture_row": 4,
        "source_record_id": "multitaskprotdb_ii_row_4",
        "parent_row_locator": "row:55",
        "parent_source_record_id": "multitaskprotdb_ii_row_55",
        "uniprot_id": "B8GW64",
        "protein_name": "CTP synthase",
        "organism": "Caulobacter crescentus",
    },
    {
        "fixture_row": 5,
        "source_record_id": "multitaskprotdb_ii_row_5",
        "parent_row_locator": "row:239",
        "parent_source_record_id": "multitaskprotdb_ii_row_239",
        "uniprot_id": "P0ABS8",
        "protein_name": "DNA polymerase III subunit theta",
        "organism": "Escherichia coli",
    },
    {
        "fixture_row": 6,
        "source_record_id": "multitaskprotdb_ii_row_6",
        "parent_row_locator": "row:672",
        "parent_source_record_id": "multitaskprotdb_ii_row_672",
        "uniprot_id": "Q9Y3E5",
        "protein_name": "Bleomycin hydrolase (Bit1)",
        "organism": "Homo sapiens",
    },
]


def compute_sha256(path_or_bytes: Path | bytes) -> str:
    """Compute SHA-256 digest of a file or byte string."""
    if isinstance(path_or_bytes, Path):
        data = path_or_bytes.read_bytes()
    else:
        data = path_or_bytes
    return hashlib.sha256(data).hexdigest()


def load_validator(schema_path: Path) -> tuple[dict[str, Any], Draft202012Validator]:
    """Load JSON schema and build Draft 2020-12 validator."""
    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    return schema, Draft202012Validator(schema)


def load_catalog_protein_lookup(catalog_path: Path) -> dict[str, str]:
    """Load UniProt -> protein_id mapping from local mfp_source_records.csv."""
    lookup: dict[str, str] = {}
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")

    with catalog_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot = (row.get("uniprot_id") or "").strip()
            pid = (row.get("protein_id") or "").strip()
            if uniprot and pid:
                lookup[uniprot] = pid
    return lookup


def serialize_csv(records: list[dict[str, Any]], fieldnames: list[str]) -> bytes:
    """Serialize records into byte-stable RFC 4180 CSV."""
    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=fieldnames,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for record in records:
        row_dict = {k: ("" if record.get(k) is None else str(record[k])) for k in fieldnames}
        writer.writerow(row_dict)
    return out.getvalue().encode("utf-8")


def build_multitask_slice(
    input_fixture: Path,
    output_dir: Path,
    catalog_path: Path,
) -> dict[str, Any]:
    """Extract, validate, and write the persistent six-record MultitaskProtDB-II slice."""
    if not input_fixture.exists():
        raise FileNotFoundError(f"Input fixture not found: {input_fixture}")

    fixture_bytes = input_fixture.read_bytes()
    fixture_sha256 = compute_sha256(fixture_bytes)

    # 1. Load schemas and validators
    claims_schema, claims_validator = load_validator(CLAIMS_SCHEMA_PATH)
    annotations_schema, annotations_validator = load_validator(ANNOTATIONS_SCHEMA_PATH)
    coverage_schema, coverage_validator = load_validator(COVERAGE_SCHEMA_PATH)

    claims_fields = list(claims_schema["properties"].keys())
    annotations_fields = list(annotations_schema["properties"].keys())
    coverage_fields = list(coverage_schema["properties"].keys())

    # 2. Verify catalog linkage for all fixture records
    catalog_lookup = load_catalog_protein_lookup(catalog_path)
    verified_scope: list[dict[str, Any]] = []

    for entry in RECORD_SCOPE_LOCATORS:
        acc = entry["uniprot_id"]
        if acc not in catalog_lookup:
            raise ValueError(
                f"Catalog linkage failed: accession '{acc}' ({entry['protein_name']}) not found in catalog {catalog_path}"
            )
        expected_pid = catalog_lookup[acc]
        derived_pid = make_protein_id_uniprot(acc)
        if expected_pid != derived_pid:
            raise ValueError(
                f"Protein ID mismatch for '{acc}': catalog has '{expected_pid}', derived '{derived_pid}'"
            )
        verified_scope.append({
            **entry,
            "protein_id": expected_pid,
        })

    # 3. Extract claims, structured GO annotations, and coverage
    claims, annotations, coverage = extract_multitask_slice_from_file(
        input_fixture,
        catalog_lookup={e["source_record_id"]: e["protein_id"] for e in verified_scope},
    )

    if len(coverage) != 6:
        raise ValueError(f"Expected 6 coverage records, got {len(coverage)}")
    if len(claims) != 12:
        raise ValueError(f"Expected 12 claims, got {len(claims)}")

    # 4. Validate all records against Draft 2020-12 schemas
    for c in claims:
        claims_validator.validate(c)
    for a in annotations:
        annotations_validator.validate(a)
    for cov in coverage:
        coverage_validator.validate(cov)

    # 5. Verify total tie-breaking sort order
    claim_sort_keys = [
        (c["protein_id"], c["source_id"], c["source_record_id"], c["claim_index"], c["claim_id"])
        for c in claims
    ]
    if claim_sort_keys != sorted(claim_sort_keys):
        raise ValueError("Emitted claims violate deterministic total ordering")

    ann_sort_keys = [
        (a["protein_id"], a["source_id"], a["source_record_id"], a["source_field"], a["annotation_index"], a["annotation_id"])
        for a in annotations
    ]
    if ann_sort_keys != sorted(ann_sort_keys):
        raise ValueError("Emitted source GO annotations violate deterministic total ordering")

    cov_sort_keys = [
        (cov["protein_id"], cov["source_id"], cov["source_record_id"])
        for cov in coverage
    ]
    if cov_sort_keys != sorted(cov_sort_keys):
        raise ValueError("Emitted coverage records violate deterministic total ordering")

    # 6. Verify foreign key and optional claim link integrity
    claims_by_id = {c["claim_id"]: c for c in claims}
    for a in annotations:
        if a["claim_id"] is not None:
            if a["claim_id"] not in claims_by_id:
                raise ValueError(f"Annotation {a['annotation_id']} links to nonexistent claim {a['claim_id']}")
            linked_claim = claims_by_id[a["claim_id"]]
            if linked_claim["protein_id"] != a["protein_id"]:
                raise ValueError(f"Annotation {a['annotation_id']} protein_id mismatch with linked claim")

    # 7. Serialize CSVs
    claims_csv_bytes = serialize_csv(claims, claims_fields)
    annotations_csv_bytes = serialize_csv(annotations, annotations_fields)
    coverage_csv_bytes = serialize_csv(coverage, coverage_fields)

    claims_sha256 = compute_sha256(claims_csv_bytes)
    annotations_sha256 = compute_sha256(annotations_csv_bytes)
    coverage_sha256 = compute_sha256(coverage_csv_bytes)

    # 8. Create output directory and write CSVs
    output_dir.mkdir(parents=True, exist_ok=True)
    claims_path = output_dir / "claims.csv"
    annotations_path = output_dir / "source_go_annotations.csv"
    coverage_path = output_dir / "coverage.csv"

    claims_path.write_bytes(claims_csv_bytes)
    annotations_path.write_bytes(annotations_csv_bytes)
    coverage_path.write_bytes(coverage_csv_bytes)

    # 9. Build byte-stable manifest.json (contains zero volatile runtime timestamps)
    manifest = {
        "manifest_version": "1.0.0",
        "package_name": "multitask_slice",
        "package_type": "illustrative_fixture_slice",
        "description": "Illustrative fixture-based slice, not a representative sample or a release.",
        "record_scope": {
            "selected_records_count": len(verified_scope),
            "records": verified_scope,
        },
        "input_fixture": {
            "path": str(input_fixture.relative_to(REPO_ROOT) if input_fixture.is_relative_to(REPO_ROOT) else input_fixture),
            "sha256": fixture_sha256,
            "source_artifact": "data/raw/multitaskprotdb-ii/proteins.csv",
        },
        "schemas": {
            "functional_claims": {
                "id": claims_schema["$id"],
                "path": "data/curated/functional_claims.schema.json",
                "sha256": compute_sha256(CLAIMS_SCHEMA_PATH),
            },
            "source_go_annotations": {
                "id": annotations_schema["$id"],
                "path": "data/curated/source_go_annotations.schema.json",
                "sha256": compute_sha256(ANNOTATIONS_SCHEMA_PATH),
            },
            "functional_coverage": {
                "id": coverage_schema["$id"],
                "path": "data/curated/functional_coverage.schema.json",
                "sha256": compute_sha256(COVERAGE_SCHEMA_PATH),
            },
        },
        "code_provenance": {
            "git_commit": GIT_COMMIT_BASELINE,
            "source_id": SOURCE_ID,
            "extraction_method": EXTRACTION_METHOD,
            "claim_scheme": CLAIM_ID_SCHEME_VERSION,
            "annotation_scheme": ANNOTATION_ID_SCHEME_VERSION,
        },
        "artifacts": {
            "claims.csv": {
                "sha256": claims_sha256,
                "record_count": len(claims),
                "byte_stable": True,
            },
            "source_go_annotations.csv": {
                "sha256": annotations_sha256,
                "record_count": len(annotations),
                "byte_stable": True,
            },
            "coverage.csv": {
                "sha256": coverage_sha256,
                "record_count": len(coverage),
                "byte_stable": True,
            },
        },
        "byte_stability_notice": "claims.csv, source_go_annotations.csv, coverage.csv, and manifest.json are byte-stable across executions. Volatile execution metadata (timestamps, duration) is quarantined in verification_report.json.",
    }

    manifest_path = output_dir / "manifest.json"
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    manifest_path.write_bytes(manifest_bytes)

    # 10. Build verification_report.json (quarantines volatile timestamp and duration)
    report = {
        "report_id": "VR-MULTITASK-SLICE-001",
        "verification_status": "VERIFIED",
        "package_path": str(output_dir.relative_to(REPO_ROOT) if output_dir.is_relative_to(REPO_ROOT) else output_dir),
        "validation_checks": {
            "claims_schema_validation": "PASSED",
            "annotations_schema_validation": "PASSED",
            "coverage_schema_validation": "PASSED",
            "deterministic_ordering": "PASSED",
            "catalog_linkage_verification": "PASSED",
            "foreign_key_integrity": "PASSED",
        },
        "counts_reconciliation": {
            "selected_records_count": len(verified_scope),
            "coverage_records_count": len(coverage),
            "claims_extracted_count": len(claims),
            "source_go_annotations_count": len(annotations),
            "unresolved_identity_count": 0,
            "unlinked_annotations_count": sum(1 for a in annotations if a["claim_id"] is None),
        },
        "checksums": {
            "claims.csv": claims_sha256,
            "source_go_annotations.csv": annotations_sha256,
            "coverage.csv": coverage_sha256,
            "manifest.json": compute_sha256(manifest_bytes),
        },
        "volatile_execution_metadata": {
            "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "python_version": sys.version.split()[0],
        },
    }

    report_path = output_dir / "verification_report.json"
    report_bytes = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    report_path.write_bytes(report_bytes)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and verify persistent MultitaskProtDB-II pilot slice.")
    parser.add_argument("--input-fixture", type=Path, default=DEFAULT_FIXTURE_PATH, help="Path to input CSV fixture")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory to emit slice artifacts")
    parser.add_argument("--catalog-path", type=Path, default=DEFAULT_CATALOG_PATH, help="Path to mfp_source_records.csv")
    args = parser.parse_args()

    report = build_multitask_slice(
        input_fixture=args.input_fixture,
        output_dir=args.output_dir,
        catalog_path=args.catalog_path,
    )
    print(f"Slice built successfully at {args.output_dir}: status {report['verification_status']}")
    print(f"  Selected records: {report['counts_reconciliation']['selected_records_count']}")
    print(f"  Claims: {report['counts_reconciliation']['claims_extracted_count']}")
    print(f"  Source GO annotations: {report['counts_reconciliation']['source_go_annotations_count']}")
    print(f"  Coverage: {report['counts_reconciliation']['coverage_records_count']}")


if __name__ == "__main__":
    main()
