#!/usr/bin/env python3
"""Build GO Aspect Metadata Enrichment Pilot Slice (Task PIL-04.1A).

Reads source GO annotations, verifies and parses an immutable pinned
Gene Ontology snapshot, and writes derived_source_go_aspects_pilot.csv
with an execution manifest to an isolated output directory.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mfp_bibliography.go_aspect_enrichment import (
    compute_file_sha256,
    enrich_source_go_annotations_file,
    parse_obo_ontology,
    validate_derived_rows_against_schema,
    write_derived_source_go_aspects_csv,
)

DEFAULT_INPUT_CSV = Path("data/interim/pilot/source_go_annotations_pilot.csv")
DEFAULT_SCHEMA_PATH = Path("data/curated/derived_source_go_aspects.schema.json")
DEFAULT_OUTPUT_DIR = Path("data/interim/pilot/quickgo_slice_enriched")
DEFAULT_OBO_PATH = Path("/home/alexdoro/repositories/mfp-dataset-designer/go-basic.obo")
DEFAULT_OBO_SHA256 = "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute Task PIL-04.1A GO-Aspect Metadata Enrichment."
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=DEFAULT_INPUT_CSV,
        help="Path to source_go_annotations_pilot.csv",
    )
    parser.add_argument(
        "--ontology-obo",
        type=Path,
        default=DEFAULT_OBO_PATH,
        help="Path to pinned go-basic.obo ontology snapshot",
    )
    parser.add_argument(
        "--expected-ontology-sha256",
        type=str,
        default=DEFAULT_OBO_SHA256,
        help="Cryptographic SHA-256 digest expected for the ontology snapshot",
    )
    parser.add_argument(
        "--schema-path",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help="Path to Draft 2020-12 validation schema",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Isolated output directory for enriched artifacts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("=== Task PIL-04.1A: GO Aspect Metadata Enrichment ===")
    print(f"Input CSV:         {args.input_csv}")
    print(f"Ontology OBO:      {args.ontology_obo}")
    print(f"Expected SHA-256:  {args.expected_ontology_sha256}")
    print(f"Schema Path:       {args.schema_path}")
    print(f"Output Directory:  {args.output_dir}")

    # 1. Verify inputs exist
    if not args.input_csv.is_file():
        print(f"ERROR: Input CSV file does not exist: {args.input_csv}", file=sys.stderr)
        return 1
    if not args.ontology_obo.is_file():
        print(f"ERROR: Ontology OBO file does not exist: {args.ontology_obo}", file=sys.stderr)
        return 1
    if not args.schema_path.is_file():
        print(f"ERROR: Schema file does not exist: {args.schema_path}", file=sys.stderr)
        return 1

    input_sha256 = compute_file_sha256(args.input_csv)
    print(f"Verified Input SHA-256: {input_sha256}")

    # 2. Parse and verify ontology snapshot
    print("Parsing ontology snapshot...")
    try:
        ontology = parse_obo_ontology(
            args.ontology_obo,
            expected_sha256=args.expected_ontology_sha256,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Ontology Version:  {ontology.data_version}")
    print(f"Ontology SHA-256:  {ontology.sha256_digest}")
    print(f"Loaded Terms:      {len(ontology.terms)} primary terms, {len(ontology.alt_map)} alt_ids")

    # 3. Enrich annotations
    print("Enriching source GO annotations...")
    derived_rows, summary = enrich_source_go_annotations_file(args.input_csv, ontology)
    print(f"Processed {len(derived_rows)} rows.")

    # 4. Validate against JSON schema
    print("Validating derived rows against schema...")
    try:
        validate_derived_rows_against_schema(derived_rows, args.schema_path)
    except Exception as e:
        print(f"ERROR: Schema validation failed: {e}", file=sys.stderr)
        return 1
    print("Schema validation PASSED.")

    # 5. Write output CSV
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = args.output_dir / "derived_source_go_aspects_pilot.csv"
    print(f"Writing derived CSV to {out_csv}...")
    out_csv_sha256 = write_derived_source_go_aspects_csv(derived_rows, out_csv)
    print(f"Emitted CSV SHA-256: {out_csv_sha256}")

    # 6. Generate run manifest
    manifest_path = args.output_dir / "manifest.json"
    manifest = {
        "manifest_version": "v1.0",
        "task_id": "PIL-04.1A",
        "task_title": "Minimum GO-Aspect Metadata Enrichment",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "execution_mode": "offline_local",
        "inputs": {
            str(args.input_csv): {
                "sha256": input_sha256,
                "row_count": len(derived_rows),
            },
            str(args.ontology_obo): {
                "sha256": ontology.sha256_digest,
                "data_version": ontology.data_version,
                "terms_count": len(ontology.terms),
                "alt_ids_count": len(ontology.alt_map),
            },
            str(args.schema_path): {
                "sha256": compute_file_sha256(args.schema_path),
            },
        },
        "outputs": {
            str(out_csv): {
                "sha256": out_csv_sha256,
                "row_count": len(derived_rows),
            }
        },
        "summary": summary,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    manifest_sha256 = compute_file_sha256(manifest_path)
    print(f"Generated manifest at {manifest_path} (SHA-256: {manifest_sha256})")

    print("\n--- Summary Distribution ---")
    for st, count in sorted(summary["status_distribution"].items()):
        print(f"  {st:45s}: {count}")

    print("\nTask PIL-04.1A completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
