#!/usr/bin/env python3
"""Build interim MultitaskProtDB-II source records offline (not catalog-integrated).

Usage:
    PYTHONPATH=src python scripts/build_source_records_multitaskprotdb_ii.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mfp_bibliography.multitaskprotdb_ii_records import (
    MULTITASKPROTDB_II_SOURCE_ID,
    RAW_RELATIVE_PATH,
    MultitaskProtDBIIRecordError,
    build_validation_report,
    load_source_records,
    resolve_operational_status,
    write_records_csv,
)
from mfp_bibliography.raw_input_verification import load_source_file_sha256
from mfp_bibliography.source_claims import load_claim_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build interim MultitaskProtDB-II source records offline, reproducibly."
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
    raw_path = root / RAW_RELATIVE_PATH
    policy = load_claim_policy(root / "configs" / "source_claim_policy_v0.1.yaml")

    try:
        expected_sha256 = load_source_file_sha256(root, MULTITASKPROTDB_II_SOURCE_ID)
        records, anomalies = load_source_records(raw_path, expected_sha256=expected_sha256)
        operational_status = resolve_operational_status(policy)
    except (MultitaskProtDBIIRecordError, ValueError, OSError) as exc:
        print(f"[multitaskprotdb-ii] {exc}", file=sys.stderr)
        return 1

    # Repo-relative provenance paths (matches the claims-adapter convention)
    for record in records:
        record["raw_file_path"] = RAW_RELATIVE_PATH

    output_path = root / "data/interim/source_records_multitaskprotdb_ii.csv"
    report_path = root / "data/interim/source_records_multitaskprotdb_ii_validation_report.json"
    write_records_csv(records, output_path, operational_status)

    report = build_validation_report(records, anomalies, operational_status, RAW_RELATIVE_PATH)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
