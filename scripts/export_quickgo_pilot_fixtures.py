#!/usr/bin/env python3
"""Export bounded, frozen raw QuickGO fixtures from MFP_QuickV1 for the 8-protein pilot cohort.

Executes Query A (actual annotation rows) and Query B (denominator coverage) inside
a single connection under a REPEATABLE READ, READ ONLY transaction.

Validates the export against Draft 2020-12 schemas and dataset-level invariants before
publishing to tests/fixtures/quickgo_pilot/ alongside a dedicated manifest.json.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mfp_bibliography.quickgo_raw_validator import (
    EXPECTED_COHORT,
    compute_sha256,
    validate_export_pair,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "raw_quickgo_annotations.schema.json"
COVERAGE_SCHEMA_PATH = REPO_ROOT / "data" / "curated" / "raw_quickgo_coverage.schema.json"
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "quickgo_pilot"


EXPORT_SQL_TEMPLATE = """-- Bounded, read-only extraction of QuickGO pilot cohort fixtures
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;

-- 1. Query A: Raw Annotations Export (inner joins, actual annotation rows only)
\\copy (SELECT pga.id AS database_annotation_id, a.code AS accession, p.id AS database_protein_id, pga.go_id, gt.category AS raw_category, pga.evidence_code, pga.publication_id FROM (VALUES ('Q42525'), ('Q9Y3E5'), ('P0AFW0'), ('P34788'), ('P78007'), ('P24228'), ('A0A0H3CDS3'), ('E6KMA1')) AS cohort(accession) JOIN accession a ON a.code = cohort.accession JOIN protein p ON a.protein_id = p.id JOIN protein_go_term_annotation pga ON pga.protein_id = p.id JOIN go_terms gt ON pga.go_id = gt.go_id ORDER BY a.code, gt.category, pga.go_id, pga.evidence_code, pga.publication_id, pga.id) TO '{annotations_csv_path}' WITH CSV HEADER;

-- 2. Query B: Raw Denominator Coverage Export (left joins, all 8 cohort members retained)
\\copy (SELECT cohort.accession, p.id AS database_protein_id, CASE WHEN a.code IS NULL THEN 'absent_from_database' WHEN a.protein_id IS NULL THEN 'unlinked_in_database' WHEN COUNT(pga.id) = 0 THEN 'zero_annotations_found' ELSE 'annotations_available' END AS quickgo_coverage_status, CASE WHEN cohort.accession = 'P34788' THEN 'flagged_taxonomic_discrepancy' ELSE 'no_discrepancy_noted' END AS identity_review_status, COUNT(pga.id) AS stored_annotation_rows, COUNT(DISTINCT pga.go_id) AS distinct_go_terms, CASE WHEN cohort.accession = 'P34788' THEN 'PlantMP/Multitask cite Spinacia oleracea; UniProt/QuickGO indexes RS18_ARATH from Arabidopsis thaliana; technical accession join succeeds but biological identity remains an unresolved upstream issue' WHEN cohort.accession = 'E6KMA1' THEN 'Accession present in accession table but unlinked (protein_id IS NULL)' WHEN cohort.accession = 'A0A0H3CDS3' THEN 'Linked protein found in protein table but zero annotations stored in protein_go_term_annotation' ELSE NULL END AS notes FROM (VALUES ('Q42525'), ('Q9Y3E5'), ('P0AFW0'), ('P34788'), ('P78007'), ('P24228'), ('A0A0H3CDS3'), ('E6KMA1')) AS cohort(accession) LEFT JOIN accession a ON a.code = cohort.accession LEFT JOIN protein p ON a.protein_id = p.id LEFT JOIN protein_go_term_annotation pga ON pga.protein_id = p.id GROUP BY cohort.accession, a.code, a.protein_id, p.id ORDER BY cohort.accession) TO '{coverage_csv_path}' WITH CSV HEADER;

COMMIT;
"""


def get_git_info() -> Dict[str, Any]:
    """Retrieve current Git commit and working-tree status."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        status_output = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
        ).strip()
        return {
            "git_commit": commit,
            "working_tree_clean": len(status_output) == 0,
            "modified_files": [
                line.strip() for line in status_output.splitlines() if line.strip()
            ],
        }
    except Exception as exc:
        return {"git_commit": "unknown", "error": str(exc)}


def run_export(
    target_dir: Path,
    host: str = "localhost",
    port: str = "5432",
    user: str = "usuario",
    dbname: str = "MFP_QuickV1",
    force: bool = False,
) -> Dict[str, Any]:
    """Execute single-transaction export, validate, and write fixtures and manifest."""
    raw_ann_file = target_dir / "raw_quickgo_annotations.csv"
    raw_cov_file = target_dir / "raw_quickgo_coverage.csv"
    manifest_file = target_dir / "manifest.json"

    if not force and (raw_ann_file.exists() or raw_cov_file.exists()):
        raise FileExistsError(
            f"Frozen fixture files already exist in {target_dir}. Refusing to overwrite silently. Pass --force to replace."
        )

    db_password = os.environ.get("DB_PASSWORD") or os.environ.get("PGPASSWORD")
    if not db_password:
        raise ValueError(
            "Database password not supplied. Set environment variable DB_PASSWORD or PGPASSWORD."
        )

    export_timestamp = datetime.now(timezone.utc).isoformat()

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        tmp_ann_csv = tmp_dir / "raw_quickgo_annotations.csv"
        tmp_cov_csv = tmp_dir / "raw_quickgo_coverage.csv"
        sql_file = tmp_dir / "export.sql"

        # Format SQL script with temporary destination paths
        sql_content = EXPORT_SQL_TEMPLATE.format(
            annotations_csv_path=str(tmp_ann_csv.resolve()),
            coverage_csv_path=str(tmp_cov_csv.resolve()),
        )
        sql_file.write_text(sql_content, encoding="utf-8")
        sql_sha256 = compute_sha256(sql_file)

        env = dict(os.environ)
        env["PGPASSWORD"] = db_password

        cmd = [
            "psql",
            "-h",
            host,
            "-p",
            port,
            "-U",
            user,
            "-d",
            dbname,
            "-v",
            "ON_ERROR_STOP=1",
            "-q",
            "-f",
            str(sql_file),
        ]

        print(f"Executing bounded export against {dbname}@{host}:{port} under REPEATABLE READ READ ONLY transaction...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"psql execution failed (code {result.returncode}):\n{result.stderr}\n{result.stdout}"
            )

        print("Export completed into temporary files. Running schema and invariant validation...")
        val_report = validate_export_pair(
            tmp_ann_csv,
            tmp_cov_csv,
            ANNOTATIONS_SCHEMA_PATH,
            COVERAGE_SCHEMA_PATH,
        )
        print("Validation PASSED cleanly!")

        # Create target directory and publish verified fixtures
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tmp_ann_csv, raw_ann_file)
        shutil.copy2(tmp_cov_csv, raw_cov_file)

        # Assemble dedicated manifest
        git_info = get_git_info()
        manifest_data = {
            "manifest_schema_version": "1.0",
            "fixture_name": "quickgo_pilot_raw_inputs",
            "export_timestamp_utc": export_timestamp,
            "database_provenance": {
                "database_name": dbname,
                "host": host,
                "port": int(port),
                "user": user,
                "transaction_isolation": "REPEATABLE READ READ ONLY",
                "export_query_sha256": sql_sha256,
            },
            "repository_context": git_info,
            "cohort": list(EXPECTED_COHORT),
            "files": {
                "raw_quickgo_annotations.csv": {
                    "path": "tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv",
                    "sha256": val_report["annotations_sha256"],
                    "total_rows": val_report["annotation_stats"]["total_rows"],
                    "pmid_rows": val_report["annotation_stats"]["pmid_rows"],
                    "go_ref_rows": val_report["annotation_stats"]["go_ref_rows"],
                    "null_ref_rows": val_report["annotation_stats"]["null_ref_rows"],
                },
                "raw_quickgo_coverage.csv": {
                    "path": "tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv",
                    "sha256": val_report["coverage_sha256"],
                    "total_rows": val_report["coverage_stats"]["total_coverage_rows"],
                    "status_counts": val_report["coverage_stats"]["status_counts"],
                },
            },
            "reconciliation_summary": val_report["reconciliation"],
            "known_capture_limitations": {
                "qualifiers_captured": False,
                "qualifier_status_policy": "not_captured",
                "eco_codes_captured": False,
                "assigned_by_captured": False,
                "annotation_dates_captured": False,
                "extensions_captured": False,
                "biological_identity_warnings": [
                    {
                        "accession": "P34788",
                        "status": "flagged_taxonomic_discrepancy",
                        "issue": "Source databases cite Spinacia oleracea; UniProt/QuickGO indexes RS18_ARATH from Arabidopsis thaliana. Technical join succeeds; biological identity remains unreviewed upstream issue.",
                    }
                ],
            },
        }

        with manifest_file.open("w", encoding="utf-8") as handle:
            json.dump(manifest_data, handle, indent=2, sort_keys=False)
            handle.write("\n")

        print(f"Published verified fixtures and manifest to {target_dir}")
        return manifest_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Export raw QuickGO pilot fixtures from MFP_QuickV1.")
    parser.add_argument("--target-dir", type=Path, default=DEFAULT_FIXTURE_DIR, help="Destination fixture directory")
    parser.add_argument("--host", default=os.environ.get("DB_HOST", "localhost"), help="PostgreSQL host")
    parser.add_argument("--port", default=os.environ.get("DB_PORT", "5432"), help="PostgreSQL port")
    parser.add_argument("--user", default=os.environ.get("DB_USER", "usuario"), help="PostgreSQL user")
    parser.add_argument("--dbname", default=os.environ.get("DB_NAME", "MFP_QuickV1"), help="Database name")
    parser.add_argument("--force", action="store_true", help="Overwrite existing fixtures")
    args = parser.parse_args()

    try:
        manifest = run_export(
            target_dir=args.target_dir,
            host=args.host,
            port=args.port,
            user=args.user,
            dbname=args.dbname,
            force=args.force,
        )
        print("Summary:")
        print(f"  Annotations rows: {manifest['files']['raw_quickgo_annotations.csv']['total_rows']}")
        print(f"  Coverage rows:    {manifest['files']['raw_quickgo_coverage.csv']['total_rows']}")
        print(f"  Status breakdown: {manifest['files']['raw_quickgo_coverage.csv']['status_counts']}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
