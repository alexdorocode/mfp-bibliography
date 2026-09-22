#!/usr/bin/env python3
"""Run the read-only MoonDB/PlantMP overlap audit (offline).

Reads data/interim/source_claims_moondb.csv and
data/interim/source_claims_plantmp.csv, validates every claim against the
source-claims contract, and writes the deterministic overlap audit to
data/interim/reports/moondb_plantmp_overlap_audit.json and .md. The claim
CSVs, raw data, manifests, checksums, policies, and schemas are never
modified; claims are not deduplicated and no canonical data is produced.

Usage:
    python scripts/audit_moondb_plantmp_overlap.py
    python scripts/audit_moondb_plantmp_overlap.py --output-dir <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mfp_bibliography.overlap_audit import (
    MOONDB_CLAIMS_PATH,
    MOONDB_SOURCE_ID,
    PLANTMP_CLAIMS_PATH,
    PLANTMP_SOURCE_ID,
    build_overlap_audit,
    load_validated_claims,
    write_audit_outputs,
)
from mfp_bibliography.provenance import sha256_file

REPORT_JSON_NAME = "moondb_plantmp_overlap_audit.json"
REPORT_MD_NAME = "moondb_plantmp_overlap_audit.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit MoonDB/PlantMP UniProt overlap read-only and reproducibly."
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
        help="Output directory (default: <root>/data/interim/reports).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir or (root / "data" / "interim" / "reports")

    moondb_path = root / MOONDB_CLAIMS_PATH
    plantmp_path = root / PLANTMP_CLAIMS_PATH
    moondb_claims = load_validated_claims(moondb_path, MOONDB_SOURCE_ID)
    plantmp_claims = load_validated_claims(plantmp_path, PLANTMP_SOURCE_ID)

    inputs = {
        "moondb_claims": {
            "path": MOONDB_CLAIMS_PATH,
            "sha256": sha256_file(moondb_path),
        },
        "plantmp_claims": {
            "path": PLANTMP_CLAIMS_PATH,
            "sha256": sha256_file(plantmp_path),
        },
    }
    report = build_overlap_audit(moondb_claims, plantmp_claims, inputs=inputs)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_audit_outputs(
        report, output_dir / REPORT_JSON_NAME, output_dir / REPORT_MD_NAME
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
