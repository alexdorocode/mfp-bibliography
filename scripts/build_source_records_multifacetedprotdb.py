#!/usr/bin/env python3
"""Build interim MultifacetedProtDB source records offline (not catalog-integrated).

Usage:
    PYTHONPATH=src python scripts/build_source_records_multifacetedprotdb.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mfp_bibliography.multifacetedprotdb_records import (
    MULTIFACETEDPROTDB_SOURCE_ID,
    build_validation_report,
    cross_check_txt_companion,
    load_source_records,
    resolve_operational_status,
    write_records_csv,
)
from mfp_bibliography.raw_input_verification import load_source_file_sha256
from mfp_bibliography.source_claims import load_claim_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build interim MultifacetedProtDB source records offline, reproducibly."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path (default: script parent repository).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    raw_path = root / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json"
    txt_path = root / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt"
    policy = load_claim_policy(root / "configs" / "source_claim_policy_v0.1.yaml")

    try:
        expected_sha256 = load_source_file_sha256(root, MULTIFACETEDPROTDB_SOURCE_ID)
        records = load_source_records(raw_path, expected_sha256=expected_sha256)
        divergences = cross_check_txt_companion(txt_path, records)
    except (ValueError, OSError) as exc:
        print(f"[multifacetedprotdb] {exc}", file=sys.stderr)
        return 1

    if divergences:
        for divergence in divergences:
            print(f"[multifacetedprotdb] cross-check: {divergence}", file=sys.stderr)
        return 1

    operational_status = resolve_operational_status(policy)

    # Record repo-relative provenance paths (matches the claims-adapter convention)
    rel_raw_path = raw_path.relative_to(root)
    for record in records:
        record["raw_file_path"] = str(rel_raw_path)

    output_path = root / "data/interim/source_records_multifacetedprotdb.csv"
    report_path = root / "data/interim/source_records_multifacetedprotdb_validation_report.json"
    write_records_csv(records, output_path, operational_status)

    report = build_validation_report(records, operational_status, divergences, rel_raw_path)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
