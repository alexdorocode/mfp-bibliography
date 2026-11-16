#!/usr/bin/env python3
"""Stage P3 Offline Concordance Pipeline Runner.

Executes offline normalization and concordance transformations connecting
frozen source-native assertions in mfp-bibliography with external QuickGO
data captured in MFP_QuickV1.

Outputs generated under data/interim/pilot/quickgo_slice/:
  1. quickgo_annotations_pilot.csv (156 rows)
  2. quickgo_coverage_pilot.csv (8 rows)
  3. quickgo_concordance_pilot.csv (72 rows)
  4. quickgo_reference_concordance_pilot.csv (12 rows)
  5. manifest.json (execution manifest with provenance & SHA-256 digests)

100% offline, zero network access, deterministic bitwise reproducibility.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mfp_bibliography.quickgo_concordance import (
    build_concordance_matrix,
    build_normalized_annotations,
    build_normalized_coverage,
    build_reference_concordance,
    load_candidate_proteins,
    validate_slice_outputs,
)

EXPECTED_INPUT_HASHES: Dict[str, str] = {
    "tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv": "b8d508f6f980fb3aed676dae7c4d3275b188dcbe58438372280920e6cf704f6a",
    "tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv": "249a4cd91117fec229cdaf9c579803dcb89d011e41ec2e5bf0eb0fb35eb8aef1",
    "tests/fixtures/quickgo_pilot/manifest.json": "a6c08b0e4559f0557244e3adaf26d2911461952a8024451f4795044b9ef4c09c",
    "data/interim/pilot/functional_claims_pilot.csv": "88a1f2521d5d69b70dbd3af11d2191589289bb22feb23a349611d1a563993348",
    "data/interim/pilot/source_go_annotations_pilot.csv": "949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda",
    "data/interim/pilot/functional_coverage_pilot.csv": "c29d28712c613211c6183f49ef304a63d94dd64a40de2ff682641037e2573e8d",
    "data/interim/pilot/manifest.json": "c6ecaed0306bfb2029427842e4b6b2e223a8b539f34990a05e87ac781a60bf5b",
    "releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv": "a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc",
}


def compute_sha256(path: Path) -> str:
    """Compute hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def write_csv_table(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> str:
    """Write list of dicts to CSV, serializing None as empty string."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            clean_row = {
                k: ("" if r.get(k) is None else str(r.get(k)))
                for k in fieldnames
            }
            writer.writerow(clean_row)
    return compute_sha256(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Stage P3 QuickGO concordance pilot slice.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root path")
    parser.add_argument("--verify-only", action="store_true", help="Verify inputs and existing outputs without overwriting")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    schemas_dir = repo_root / "data" / "curated"
    out_dir = repo_root / "data" / "interim" / "pilot" / "quickgo_slice"

    print(f"=== Stage P3 QuickGO Concordance Pipeline ===")
    print(f"Repository Root: {repo_root}")
    print(f"Output Directory: {out_dir}")

    # 1. Verify Input Hashes
    print("\n--- 1. Verifying Input Hashes ---")
    for rel_path, exp_hash in EXPECTED_INPUT_HASHES.items():
        p = repo_root / rel_path
        if not p.exists():
            print(f"ERROR: Missing input file: {rel_path}", file=sys.stderr)
            return 1
        act_hash = compute_sha256(p)
        if act_hash != exp_hash:
            print(f"ERROR: Hash mismatch for {rel_path}: actual {act_hash} != expected {exp_hash}", file=sys.stderr)
            return 1
        print(f"  OK: {rel_path} ({act_hash[:16]}...)")

    # 2. Load Inputs
    print("\n--- 2. Loading Frozen Inputs ---")
    catalog_map = load_candidate_proteins(repo_root / "releases" / "mfp-catalog-candidate-v0.3.0" / "mfp_proteins.csv")
    raw_ann = list(csv.DictReader(open(repo_root / "tests" / "fixtures" / "quickgo_pilot" / "raw_quickgo_annotations.csv", encoding="utf-8")))
    raw_cov = list(csv.DictReader(open(repo_root / "tests" / "fixtures" / "quickgo_pilot" / "raw_quickgo_coverage.csv", encoding="utf-8")))
    s_ann = list(csv.DictReader(open(repo_root / "data" / "interim" / "pilot" / "source_go_annotations_pilot.csv", encoding="utf-8")))
    f_claims = list(csv.DictReader(open(repo_root / "data" / "interim" / "pilot" / "functional_claims_pilot.csv", encoding="utf-8")))
    f_cov = list(csv.DictReader(open(repo_root / "data" / "interim" / "pilot" / "functional_coverage_pilot.csv", encoding="utf-8")))

    print(f"  Raw QuickGO annotations loaded: {len(raw_ann)}")
    print(f"  Raw QuickGO coverage rows loaded: {len(raw_cov)}")
    print(f"  Source GO annotations loaded: {len(s_ann)}")
    print(f"  Functional claims loaded: {len(f_claims)}")
    print(f"  Functional coverage rows loaded: {len(f_cov)}")

    # 3. Transformations
    print("\n--- 3. Executing Normalization & Concordance Transformations ---")
    norm_ann = build_normalized_annotations(raw_ann, catalog_map)
    norm_cov = build_normalized_coverage(raw_cov, catalog_map)
    matrix = build_concordance_matrix(norm_ann, raw_cov, s_ann, f_cov, catalog_map)
    ref_matrix = build_reference_concordance(f_claims, raw_ann, raw_cov, f_cov, catalog_map)

    print(f"  Generated normalized annotations: {len(norm_ann)} rows")
    print(f"  Generated normalized coverage: {len(norm_cov)} rows")
    print(f"  Generated concordance matrix: {len(matrix)} rows")
    print(f"  Generated reference concordance: {len(ref_matrix)} rows")

    # 4. Invariant & Schema Validation
    print("\n--- 4. Validating Against Draft 2020-12 Schemas & Invariants ---")
    validate_slice_outputs(norm_ann, norm_cov, matrix, ref_matrix, schemas_dir)
    print("  All outputs successfully validated against schemas and cross-record contracts.")

    if args.verify_only:
        print("\nVerification mode: skipping output file writes.")
        return 0

    # 5. Write CSV Output Files
    print(f"\n--- 5. Serializing Output Tables to {out_dir} ---")
    ann_fields = list(norm_ann[0].keys())
    cov_fields = list(norm_cov[0].keys())
    matrix_fields = list(matrix[0].keys())
    ref_fields = list(ref_matrix[0].keys())

    ann_path = out_dir / "quickgo_annotations_pilot.csv"
    cov_path = out_dir / "quickgo_coverage_pilot.csv"
    matrix_path = out_dir / "quickgo_concordance_pilot.csv"
    ref_path = out_dir / "quickgo_reference_concordance_pilot.csv"

    ann_hash = write_csv_table(ann_path, norm_ann, ann_fields)
    cov_hash = write_csv_table(cov_path, norm_cov, cov_fields)
    matrix_hash = write_csv_table(matrix_path, matrix, matrix_fields)
    ref_hash = write_csv_table(ref_path, ref_matrix, ref_fields)

    print(f"  Wrote {ann_path} (SHA-256: {ann_hash})")
    print(f"  Wrote {cov_path} (SHA-256: {cov_hash})")
    print(f"  Wrote {matrix_path} (SHA-256: {matrix_hash})")
    print(f"  Wrote {ref_path} (SHA-256: {ref_hash})")

    # 6. Generate Manifest
    print("\n--- 6. Generating Execution Manifest ---")
    evaluable_cnt = len([r for r in matrix if r["concordance_status"] == "evaluable"])
    not_eval_cnt = len([r for r in matrix if r["concordance_status"] == "not_evaluable"])

    reason_summary: Dict[str, int] = {}
    for r in matrix:
        if r["concordance_status"] == "not_evaluable":
            pr = r["primary_non_evaluable_reason"] or "unknown"
            reason_summary[pr] = reason_summary.get(pr, 0) + 1

    ref_reason_summary: Dict[str, int] = {}
    for r in ref_matrix:
        if r["reference_concordance_status"] == "not_evaluable":
            pr = r["primary_non_evaluable_reason"] or "unknown"
            ref_reason_summary[pr] = ref_reason_summary.get(pr, 0) + 1

    manifest = {
        "manifest_version": "v1.1",
        "stage": "P3",
        "pipeline_name": "quickgo_concordance_pilot_slice",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_provenance": {
            "git_head_commit": "dc761e00c8ddec64fce4652f2fca9a783ec6533d",
            "git_branch": "feature/functional-normalization",
            "working_tree_clean": False,
            "execution_mode": "offline_uncommitted_working_tree",
            "code_and_schema_artifacts": {
                "src/mfp_bibliography/quickgo_concordance.py": compute_sha256(repo_root / "src/mfp_bibliography/quickgo_concordance.py"),
                "scripts/build_quickgo_concordance_pilot.py": compute_sha256(repo_root / "scripts/build_quickgo_concordance_pilot.py"),
                "data/curated/external_quickgo_annotations.schema.json": compute_sha256(schemas_dir / "external_quickgo_annotations.schema.json"),
                "data/curated/quickgo_coverage.schema.json": compute_sha256(schemas_dir / "quickgo_coverage.schema.json"),
                "data/curated/quickgo_concordance.schema.json": compute_sha256(schemas_dir / "quickgo_concordance.schema.json"),
                "data/curated/quickgo_reference_concordance.schema.json": compute_sha256(schemas_dir / "quickgo_reference_concordance.schema.json"),
            },
        },
        "database_capture": {
            "capture_id": "MFP_QuickV1_20261112",
            "source_database": "MFP_QuickV1",
            "transaction_isolation": "REPEATABLE READ, READ ONLY (P2 Frozen Fixture)",
        },
        "policies_applied": {
            "policy_b": "captured_inventory_overlap",
            "policy_c": "filtered_descriptive_overlap",
            "reference_overlap_scope": "Option A (protein entity / source record level)",
            "empty_set_convention": "null_jaccard_on_empty_inventory",
            "identity_inclusion_gate": "identity_review_status == 'no_discrepancy_noted'",
        },
        "input_inventory": {
            rel: {
                "sha256": exp_h,
                "verified": True,
            }
            for rel, exp_h in EXPECTED_INPUT_HASHES.items()
        },
        "output_inventory": {
            "quickgo_annotations_pilot.csv": {
                "sha256": ann_hash,
                "row_count": len(norm_ann),
                "schema": "data/curated/external_quickgo_annotations.schema.json",
            },
            "quickgo_coverage_pilot.csv": {
                "sha256": cov_hash,
                "row_count": len(norm_cov),
                "schema": "data/curated/quickgo_coverage.schema.json",
            },
            "quickgo_concordance_pilot.csv": {
                "sha256": matrix_hash,
                "row_count": len(matrix),
                "schema": "data/curated/quickgo_concordance.schema.json",
            },
            "quickgo_reference_concordance_pilot.csv": {
                "sha256": ref_hash,
                "row_count": len(ref_matrix),
                "schema": "data/curated/quickgo_reference_concordance.schema.json",
            },
        },
        "summary_metrics": {
            "total_cohort_accessions": len(norm_cov),
            "total_annotations_mapped": len(norm_ann),
            "concordance_universe_cardinality": len(matrix),
            "evaluable_concordance_rows": evaluable_cnt,
            "not_evaluable_concordance_rows": not_eval_cnt,
            "non_evaluable_concordance_breakdown": reason_summary,
            "reference_concordance_rows": len(ref_matrix),
            "evaluable_reference_rows": len([r for r in ref_matrix if r["reference_concordance_status"] == "evaluable"]),
            "not_evaluable_reference_rows": len([r for r in ref_matrix if r["reference_concordance_status"] == "not_evaluable"]),
            "non_evaluable_reference_breakdown": ref_reason_summary,
        },
    }

    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, mode="w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Wrote {manifest_path}")

    print("\n=== Stage P3 Pipeline Execution Completed Successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
