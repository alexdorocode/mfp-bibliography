#!/usr/bin/env python3
"""Build the MoonDB source-claims artifact from the raw artifact (offline).

Reads only data/raw/moondb/all_emf_and_curated.tsv, the declarative source
claim policy, and source manifest metadata. Emits one claim per raw row into
data/interim/source_claims_moondb.csv plus a validation report. Raw
artifacts, manifests, checksums, policy, and schemas are never modified.

Usage:
    python scripts/build_source_claims_moondb.py
    python scripts/build_source_claims_moondb.py --output-dir <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mfp_bibliography.moondb_claims import (
    adapt_moondb_claims,
    build_validation_report,
    load_moondb_provenance,
    load_policy,
    write_claims_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the MoonDB source-claims artifact offline, reproducibly."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path (default: script parent repository).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <root>/data/interim).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir or (root / "data" / "interim")

    provenance = load_moondb_provenance(root)
    policy = load_policy(root / "configs" / "source_claim_policy_v0.1.yaml")
    raw_path = root / provenance.raw_file_path

    claims = adapt_moondb_claims(raw_path, policy, provenance)
    report = build_validation_report(claims, raw_path, provenance)

    output_dir.mkdir(parents=True, exist_ok=True)
    claims_path = output_dir / "source_claims_moondb.csv"
    report_path = output_dir / "source_claims_moondb_validation_report.json"
    write_claims_csv(claims, claims_path)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["reconciliation_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
