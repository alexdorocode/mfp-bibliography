#!/usr/bin/env python3
"""Build and verify the integrated three-source functional normalization pilot package.

Usage:
    python scripts/build_functional_claims_pilot.py [options]

Generates:
    - data/interim/pilot/functional_claims_pilot.csv
    - data/interim/pilot/source_go_annotations_pilot.csv
    - data/interim/pilot/functional_coverage_pilot.csv
    - data/interim/pilot/manifest.json
    - data/interim/reports/functional_claims_pilot_report.json

Cohort includes real-source records from:
    1. MultitaskProtDB-II (6 records: rows 1, 2, 242, 337, 524, 672)
    2. PlantMP (8 records: orders 1, 2, 25, 62, 64, 68, 75, 85)
    3. MoonProt (6 records: MPIDs 1, 2, 7, 10, 288, 359)

Demonstrates:
    - 3-source shared protein entity (MFP:U:8272bae0e8df8149 / Q42525)
    - 2-source shared proteins (MFP:U:d0cd1a882c7acdf3 / P34788, MFP:U:9023923ecdd9d57f / P0AFW0)
    - 100% denominator reconciliation across 20 empirical source records
    - Draft 2020-12 schema validation across claims, annotations, and coverage
    - Deterministic total tie-breaking sort keys
    - Zero volatile runtime metadata in CSVs and manifest.json
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

from mfp_bibliography.functional_claims_moonprot import (
    ANNOTATION_ID_SCHEME_VERSION as MOONPROT_ANN_SCHEME,
    CLAIM_ID_SCHEME_VERSION as MOONPROT_CLAIM_SCHEME,
    EXTRACTION_METHOD as MOONPROT_EXTRACTION_METHOD,
    SOURCE_ID as MOONPROT_SOURCE_ID,
    extract_moonprot_slice_from_files,
    load_moonprot_catalog_lookup,
)
from mfp_bibliography.functional_claims_multitask import (
    ANNOTATION_ID_SCHEME_VERSION as MULTITASK_ANN_SCHEME,
    CLAIM_ID_SCHEME_VERSION as MULTITASK_CLAIM_SCHEME,
    EXTRACTION_METHOD as MULTITASK_EXTRACTION_METHOD,
    SOURCE_ID as MULTITASK_SOURCE_ID,
    extract_multitask_row_records,
)
from mfp_bibliography.functional_claims_plantmp import (
    ANNOTATION_ID_SCHEME_VERSION as PLANTMP_ANN_SCHEME,
    CLAIM_ID_SCHEME_VERSION as PLANTMP_CLAIM_SCHEME,
    EXTRACTION_METHOD as PLANTMP_EXTRACTION_METHOD,
    SOURCE_ID as PLANTMP_SOURCE_ID,
    extract_plantmp_row_records,
    load_plantmp_catalog_lookup,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_PILOT_DIR = REPO_ROOT / "data" / "interim" / "pilot"
DEFAULT_REPORTS_DIR = REPO_ROOT / "data" / "interim" / "reports"
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp" / "mfp_source_records.csv"
DEFAULT_PROTEINS_CATALOG_PATH = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp" / "mfp_proteins.csv"

RAW_MULTITASK_PATH = REPO_ROOT / "data" / "raw" / "multitaskprotdb-ii" / "proteins.csv"
RAW_PLANTMP_PATH = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"
RAW_MOONPROT_DIR = REPO_ROOT / "data" / "raw" / "moonprot"

SCHEMAS_DIR = REPO_ROOT / "data" / "curated"
CLAIMS_SCHEMA_PATH = SCHEMAS_DIR / "functional_claims.schema.json"
ANNOTATIONS_SCHEMA_PATH = SCHEMAS_DIR / "source_go_annotations.schema.json"
COVERAGE_SCHEMA_PATH = SCHEMAS_DIR / "functional_coverage.schema.json"

GIT_COMMIT_BASELINE = "6b76dd04f6e3c0b02e70757a3e5c9428784fc118"

# Empirical cohort specification across 3 sources (20 real source records)
PILOT_COHORT_SPECIFICATION = [
    # --- MultitaskProtDB-II (6 records) ---
    {
        "source_id": MULTITASK_SOURCE_ID,
        "source_record_id": "multitaskprotdb_ii_row_1",
        "row_index": 1,
        "uniprot_accession": "A0A059U5R2",
        "rationale": "Standard canonical/moonlighting functional extraction with 14 GO terms",
    },
    {
        "source_id": MULTITASK_SOURCE_ID,
        "source_record_id": "multitaskprotdb_ii_row_2",
        "row_index": 2,
        "uniprot_accession": "A0A0H2Q1X0",
        "rationale": "Standard two-function block with 7 GO terms",
    },
    {
        "source_id": MULTITASK_SOURCE_ID,
        "source_record_id": "multitaskprotdb_ii_row_242",
        "row_index": 242,
        "uniprot_accession": "P0AFW0",
        "rationale": "Shared protein with MoonProt MPID 2 (MFP:U:9023923ecdd9d57f)",
    },
    {
        "source_id": MULTITASK_SOURCE_ID,
        "source_record_id": "multitaskprotdb_ii_row_337",
        "row_index": 337,
        "uniprot_accession": "P34788",
        "rationale": "Shared protein with PlantMP Order 1 (MFP:U:d0cd1a882c7acdf3)",
    },
    {
        "source_id": MULTITASK_SOURCE_ID,
        "source_record_id": "multitaskprotdb_ii_row_524",
        "row_index": 524,
        "uniprot_accession": "Q42525",
        "rationale": "3-way shared protein across MoonProt, PlantMP, and Multitask (MFP:U:8272bae0e8df8149)",
    },
    {
        "source_id": MULTITASK_SOURCE_ID,
        "source_record_id": "multitaskprotdb_ii_row_672",
        "row_index": 672,
        "uniprot_accession": "Q9Y3E5",
        "rationale": "Source-explicit CC annotation on moonlighting function (GO:0005654 nucleoplasm)",
    },
    # --- PlantMP (8 records) ---
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_1",
        "order": "1",
        "uniprot_accession": "P34788",
        "rationale": "Confirmed curation status; shared protein with Multitask row 337",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_2",
        "order": "2",
        "uniprot_accession": "P92980",
        "rationale": "Input normalization (raw accession non-breaking space \\xa0 cleaned)",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_25",
        "order": "25",
        "uniprot_accession": "Q42525",
        "rationale": "3-way shared protein across MoonProt, PlantMP, and Multitask (MFP:U:8272bae0e8df8149)",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_62",
        "order": "62",
        "uniprot_accession": "Q8VYA3",
        "rationale": "Predicted status; duplicate accession sharing entity with order 68",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_64",
        "order": "64",
        "uniprot_accession": "Q9LIA4",
        "rationale": "Likely -> excluded_likely policy; missing text with explicit GO (0 claims, 2 annotations)",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_68",
        "order": "68",
        "uniprot_accession": "Q8VYA3",
        "rationale": "Predicted status; shared entity with order 62 proving shared-accession preservation",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_75",
        "order": "75",
        "uniprot_accession": "Q9SJE9",
        "rationale": "Likely -> excluded_likely; missing text with explicit GO (coverage: no_discrete_functional_statements)",
    },
    {
        "source_id": PLANTMP_SOURCE_ID,
        "source_record_id": "plantmp_order_85",
        "order": "85",
        "uniprot_accession": "Q9XIU3",
        "rationale": "Likely -> excluded_likely policy with text present (coverage: claims_extracted)",
    },
    # --- MoonProt (6 records) ---
    {
        "source_id": MOONPROT_SOURCE_ID,
        "source_record_id": "moonprot_1",
        "mpid": "1",
        "file_name": "mpid_1.html",
        "uniprot_accession": "P78007",
        "rationale": "K=2 dynamic function blocks, function-specific PMIDs, 12 protein-level GO terms",
    },
    {
        "source_id": MOONPROT_SOURCE_ID,
        "source_record_id": "moonprot_2",
        "mpid": "2",
        "file_name": "mpid_2.html",
        "uniprot_accession": "P0AFW0",
        "rationale": "Shared protein with Multitask row 242 (MFP:U:9023923ecdd9d57f)",
    },
    {
        "source_id": MOONPROT_SOURCE_ID,
        "source_record_id": "moonprot_7",
        "mpid": "7",
        "file_name": "mpid_7.html",
        "uniprot_accession": "P10809",
        "rationale": "K=2 dynamic function blocks, cellular location in notes, 6 GO terms",
    },
    {
        "source_id": MOONPROT_SOURCE_ID,
        "source_record_id": "moonprot_10",
        "mpid": "10",
        "file_name": "mpid_10.html",
        "uniprot_accession": "E6KMA1",
        "rationale": "K=2 dynamic function blocks with zero GO terms",
    },
    {
        "source_id": MOONPROT_SOURCE_ID,
        "source_record_id": "moonprot_288",
        "mpid": "288",
        "file_name": "mpid_288.html",
        "uniprot_accession": "P24228",
        "rationale": "Extraction failure caused by upstream HTML syntax defect (parse_failure); 22 protein GO terms preserved with claim_id=null",
    },
    {
        "source_id": MOONPROT_SOURCE_ID,
        "source_record_id": "moonprot_359",
        "mpid": "359",
        "file_name": "mpid_359.html",
        "uniprot_accession": "Q42525",
        "rationale": "3-way shared protein across MoonProt, PlantMP, and Multitask (MFP:U:8272bae0e8df8149)",
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


def load_full_catalog_lookups(catalog_path: Path) -> tuple[dict[str, str], set[str]]:
    """Load source_record_id -> protein_id mapping and set of valid protein IDs."""
    record_to_protein: dict[str, str] = {}
    valid_proteins: set[str] = set()
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")

    with catalog_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            srid = (row.get("source_record_id") or "").strip()
            pid = (row.get("protein_id") or "").strip()
            if srid and pid:
                record_to_protein[srid] = pid
                valid_proteins.add(pid)
    return record_to_protein, valid_proteins


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


def build_functional_claims_pilot(
    pilot_dir: Path = DEFAULT_PILOT_DIR,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
) -> dict[str, Any]:
    """Execute integrated functional normalization pilot across the 3 authorized sources."""
    # 1. Load schemas and validators
    claims_schema, claims_validator = load_validator(CLAIMS_SCHEMA_PATH)
    annotations_schema, annotations_validator = load_validator(ANNOTATIONS_SCHEMA_PATH)
    coverage_schema, coverage_validator = load_validator(COVERAGE_SCHEMA_PATH)

    claims_fields = list(claims_schema["properties"].keys())
    annotations_fields = list(annotations_schema["properties"].keys())
    coverage_fields = list(coverage_schema["properties"].keys())

    # 2. Load catalog mappings and verify cohort referential integrity
    catalog_lookup, valid_protein_ids = load_full_catalog_lookups(catalog_path)

    verified_cohort: list[dict[str, Any]] = []
    for spec in PILOT_COHORT_SPECIFICATION:
        srid = spec["source_record_id"]
        if srid not in catalog_lookup:
            raise ValueError(f"Cohort record {srid} missing from catalog {catalog_path}")
        pid = catalog_lookup[srid]
        verified_cohort.append({**spec, "protein_id": pid})

    # 3. Extract MultitaskProtDB-II cohort records
    if not RAW_MULTITASK_PATH.exists():
        raise FileNotFoundError(f"Raw Multitask file missing: {RAW_MULTITASK_PATH}")
    with RAW_MULTITASK_PATH.open("r", encoding="utf-8-sig") as f:
        all_multi_rows = list(csv.DictReader(f))

    multitask_specs = [s for s in verified_cohort if s["source_id"] == MULTITASK_SOURCE_ID]
    multi_claims: list[dict[str, Any]] = []
    multi_annotations: list[dict[str, Any]] = []
    multi_coverage: list[dict[str, Any]] = []

    for spec in multitask_specs:
        idx = spec["row_index"]
        row = all_multi_rows[idx - 1]
        c, a, cov = extract_multitask_row_records(
            row=row,
            row_index=idx,
            protein_id=spec["protein_id"],
            raw_file_path=str(RAW_MULTITASK_PATH.relative_to(REPO_ROOT)),
        )
        multi_claims.extend(c)
        multi_annotations.extend(a)
        multi_coverage.append(cov)

    # 4. Extract PlantMP cohort records
    if not RAW_PLANTMP_PATH.exists():
        raise FileNotFoundError(f"Raw PlantMP file missing: {RAW_PLANTMP_PATH}")
    with RAW_PLANTMP_PATH.open("r", encoding="utf-8") as f:
        all_plant_rows = list(csv.DictReader(f))

    plantmp_specs = [s for s in verified_cohort if s["source_id"] == PLANTMP_SOURCE_ID]
    plant_by_order = {r["order"]: r for r in all_plant_rows}
    plant_claims: list[dict[str, Any]] = []
    plant_annotations: list[dict[str, Any]] = []
    plant_coverage: list[dict[str, Any]] = []

    plant_catalog = load_plantmp_catalog_lookup()
    for spec in plantmp_specs:
        order_key = spec["order"]
        row = plant_by_order[order_key]
        idx = int(order_key)
        c, a, cov = extract_plantmp_row_records(
            row=row,
            row_index=idx,
            catalog_lookup=plant_catalog,
            raw_file_path=str(RAW_PLANTMP_PATH.relative_to(REPO_ROOT)),
        )
        plant_claims.extend(c)
        plant_annotations.extend(a)
        plant_coverage.append(cov)

    # 5. Extract MoonProt cohort records
    moonprot_specs = [s for s in verified_cohort if s["source_id"] == MOONPROT_SOURCE_ID]
    moon_files = [RAW_MOONPROT_DIR / s["file_name"] for s in moonprot_specs]
    for mf in moon_files:
        if not mf.exists():
            raise FileNotFoundError(f"Raw MoonProt file missing: {mf}")

    moon_catalog = load_moonprot_catalog_lookup()
    moon_claims, moon_annotations, moon_coverage = extract_moonprot_slice_from_files(
        file_paths=moon_files,
        catalog_lookup=moon_catalog,
    )

    # 6. Combine all three sources
    all_claims = multi_claims + plant_claims + moon_claims
    all_annotations = multi_annotations + plant_annotations + moon_annotations
    all_coverage = multi_coverage + plant_coverage + moon_coverage

    # 7. Denominator & reconciliations checks
    if len(all_coverage) != len(PILOT_COHORT_SPECIFICATION):
        raise ValueError(
            f"Denominator mismatch: expected {len(PILOT_COHORT_SPECIFICATION)} coverage rows, got {len(all_coverage)}"
        )

    # 8. Schema validation
    for c in all_claims:
        claims_validator.validate(c)
    for a in all_annotations:
        annotations_validator.validate(a)
    for cov in all_coverage:
        coverage_validator.validate(cov)

    # 9. Catalog referential integrity
    claims_by_id = {c["claim_id"]: c for c in all_claims}
    for c in all_claims:
        if c["protein_id"] not in valid_protein_ids:
            raise ValueError(f"Claim {c['claim_id']} protein_id {c['protein_id']} not found in catalog")

    for a in all_annotations:
        if a["protein_id"] not in valid_protein_ids:
            raise ValueError(f"Annotation {a['annotation_id']} protein_id {a['protein_id']} not found in catalog")
        if a["claim_id"] is not None:
            if a["claim_id"] not in claims_by_id:
                raise ValueError(f"Annotation {a['annotation_id']} references missing claim_id {a['claim_id']}")
            linked_claim = claims_by_id[a["claim_id"]]
            if linked_claim["protein_id"] != a["protein_id"]:
                raise ValueError(f"Annotation {a['annotation_id']} protein_id mismatch with linked claim")

    for cov in all_coverage:
        pid = cov["protein_id"]
        if pid is not None and pid not in valid_protein_ids:
            raise ValueError(f"Coverage record {cov['source_record_id']} protein_id {pid} not found in catalog")

    # 10. Enforce total tie-breaking sort order across combined multi-source datasets
    sorted_claims = sorted(
        all_claims,
        key=lambda c: (
            c["protein_id"],
            c["source_id"],
            c["source_record_id"],
            c["claim_index"],
            c["claim_id"],
        ),
    )
    sorted_annotations = sorted(
        all_annotations,
        key=lambda a: (
            a["protein_id"],
            a["source_id"],
            a["source_record_id"],
            a["source_field"],
            a["annotation_index"],
            a["annotation_id"],
        ),
    )
    sorted_coverage = sorted(
        all_coverage,
        key=lambda cov: (
            cov["protein_id"] or "",
            cov["source_id"],
            cov["source_record_id"],
        ),
    )

    # 11. Serialize CSVs
    claims_csv_bytes = serialize_csv(sorted_claims, claims_fields)
    annotations_csv_bytes = serialize_csv(sorted_annotations, annotations_fields)
    coverage_csv_bytes = serialize_csv(sorted_coverage, coverage_fields)

    claims_sha256 = compute_sha256(claims_csv_bytes)
    annotations_sha256 = compute_sha256(annotations_csv_bytes)
    coverage_sha256 = compute_sha256(coverage_csv_bytes)

    # 12. Write output CSVs
    pilot_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    claims_path = pilot_dir / "functional_claims_pilot.csv"
    annotations_path = pilot_dir / "source_go_annotations_pilot.csv"
    coverage_path = pilot_dir / "functional_coverage_pilot.csv"
    manifest_path = pilot_dir / "manifest.json"
    report_path = reports_dir / "functional_claims_pilot_report.json"

    claims_path.write_bytes(claims_csv_bytes)
    annotations_path.write_bytes(annotations_csv_bytes)
    coverage_path.write_bytes(coverage_csv_bytes)

    # 13. Build byte-stable manifest.json (contains zero volatile runtime timestamps)
    manifest = {
        "manifest_version": "1.0.0",
        "package_name": "functional_claims_pilot",
        "package_type": "integrated_three_source_pilot",
        "description": "Integrated Tier A functional normalization pilot across MultitaskProtDB-II, PlantMP, and MoonProt.",
        "record_scope": {
            "selected_records_count": len(verified_cohort),
            "breakdown_by_source": {
                MULTITASK_SOURCE_ID: len(multitask_specs),
                PLANTMP_SOURCE_ID: len(plantmp_specs),
                MOONPROT_SOURCE_ID: len(moonprot_specs),
            },
            "records": verified_cohort,
        },
        "raw_artifacts": {
            "multitaskprotdb_ii": {
                "path": "data/raw/multitaskprotdb-ii/proteins.csv",
                "sha256": compute_sha256(RAW_MULTITASK_PATH),
            },
            "plantmp": {
                "path": "data/raw/plantmp/PlantMP_all.csv",
                "sha256": compute_sha256(RAW_PLANTMP_PATH),
            },
            "moonprot": {
                "path": "data/raw/moonprot/",
                "file_count": len(moon_files),
            },
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
            "multitask": {
                "source_id": MULTITASK_SOURCE_ID,
                "extraction_method": MULTITASK_EXTRACTION_METHOD,
                "claim_scheme": MULTITASK_CLAIM_SCHEME,
                "annotation_scheme": MULTITASK_ANN_SCHEME,
            },
            "plantmp": {
                "source_id": PLANTMP_SOURCE_ID,
                "extraction_method": PLANTMP_EXTRACTION_METHOD,
                "claim_scheme": PLANTMP_CLAIM_SCHEME,
                "annotation_scheme": PLANTMP_ANN_SCHEME,
            },
            "moonprot": {
                "source_id": MOONPROT_SOURCE_ID,
                "extraction_method": MOONPROT_EXTRACTION_METHOD,
                "claim_scheme": MOONPROT_CLAIM_SCHEME,
                "annotation_scheme": MOONPROT_ANN_SCHEME,
            },
        },
        "artifacts": {
            "functional_claims_pilot.csv": {
                "sha256": claims_sha256,
                "record_count": len(sorted_claims),
                "byte_stable": True,
            },
            "source_go_annotations_pilot.csv": {
                "sha256": annotations_sha256,
                "record_count": len(sorted_annotations),
                "byte_stable": True,
            },
            "functional_coverage_pilot.csv": {
                "sha256": coverage_sha256,
                "record_count": len(sorted_coverage),
                "byte_stable": True,
            },
        },
    }

    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)

    # 14. Build volatile validation report (isolated in reports/)
    report = {
        "execution_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "verification_status": "VERIFIED",
        "cohort_summary": {
            "total_selected_records": len(verified_cohort),
            "by_source": {
                MULTITASK_SOURCE_ID: {
                    "source_records": len(multitask_specs),
                    "claims": len(multi_claims),
                    "annotations": len(multi_annotations),
                    "coverage": len(multi_coverage),
                },
                PLANTMP_SOURCE_ID: {
                    "source_records": len(plantmp_specs),
                    "claims": len(plant_claims),
                    "annotations": len(plant_annotations),
                    "coverage": len(plant_coverage),
                },
                MOONPROT_SOURCE_ID: {
                    "source_records": len(moonprot_specs),
                    "claims": len(moon_claims),
                    "annotations": len(moon_annotations),
                    "coverage": len(moon_coverage),
                },
            },
            "totals": {
                "source_records": len(verified_cohort),
                "claims": len(sorted_claims),
                "annotations": len(sorted_annotations),
                "coverage": len(sorted_coverage),
            },
        },
        "cross_source_shared_entities": [
            {
                "protein_id": "MFP:U:8272bae0e8df8149",
                "uniprot_accession": "Q42525",
                "sources_present": [MULTITASK_SOURCE_ID, PLANTMP_SOURCE_ID, MOONPROT_SOURCE_ID],
                "claims_count": len([c for c in sorted_claims if c["protein_id"] == "MFP:U:8272bae0e8df8149"]),
            },
            {
                "protein_id": "MFP:U:d0cd1a882c7acdf3",
                "uniprot_accession": "P34788",
                "sources_present": [MULTITASK_SOURCE_ID, PLANTMP_SOURCE_ID],
                "claims_count": len([c for c in sorted_claims if c["protein_id"] == "MFP:U:d0cd1a882c7acdf3"]),
            },
            {
                "protein_id": "MFP:U:9023923ecdd9d57f",
                "uniprot_accession": "P0AFW0",
                "sources_present": [MULTITASK_SOURCE_ID, MOONPROT_SOURCE_ID],
                "claims_count": len([c for c in sorted_claims if c["protein_id"] == "MFP:U:9023923ecdd9d57f"]),
            },
        ],
        "extraction_diagnostics": [
            {
                "source_record_id": cov["source_record_id"],
                "source_id": cov["source_id"],
                "protein_id": cov["protein_id"],
                "coverage_status": cov["coverage_status"],
                "raw_artifact_locator": (
                    f"data/raw/moonprot/mpid_{cov['source_record_id'].split('_')[1]}.html"
                    if cov["source_id"] == MOONPROT_SOURCE_ID
                    else None
                ),
                "failure_reason": (
                    "malformed markup: unclosed quote in PDB ID link prevented table parser from recovering Function 1 and Function 2 statements present in raw source"
                    if cov["source_record_id"] == "moonprot_288"
                    else cov["notes"]
                ),
                "claims_extracted_count": cov["claims_extracted_count"],
                "source_go_annotations_count": len(
                    [a for a in all_annotations if a["source_record_id"] == cov["source_record_id"]]
                ),
            }
            for cov in all_coverage
            if cov["coverage_status"] in ("parse_failure", "unresolved_identity")
        ],
        "artifact_hashes": {
            "functional_claims_pilot.csv": claims_sha256,
            "source_go_annotations_pilot.csv": annotations_sha256,
            "functional_coverage_pilot.csv": coverage_sha256,
            "manifest.json": compute_sha256(manifest_bytes),
        },
    }
    report_bytes = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
    report_path.write_bytes(report_bytes)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and verify integrated functional claims pilot.")
    parser.add_argument("--pilot-dir", type=Path, default=DEFAULT_PILOT_DIR, help="Output directory for pilot artifacts")
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR, help="Output directory for validation reports")
    parser.add_argument("--catalog-path", type=Path, default=DEFAULT_CATALOG_PATH, help="Path to mfp_source_records.csv")
    args = parser.parse_args()

    try:
        report = build_functional_claims_pilot(
            pilot_dir=args.pilot_dir,
            reports_dir=args.reports_dir,
            catalog_path=args.catalog_path,
        )
        print(f"PILOT BUILD SUCCESS: status={report['verification_status']}")
        print(f"Total records: {report['cohort_summary']['totals']['source_records']}")
        print(f"Total claims: {report['cohort_summary']['totals']['claims']}")
        print(f"Total annotations: {report['cohort_summary']['totals']['annotations']}")
        print(f"Total coverage: {report['cohort_summary']['totals']['coverage']}")
        print("Breakdown by source:")
        for s, stats in report["cohort_summary"]["by_source"].items():
            print(f"  {s}: records={stats['source_records']}, claims={stats['claims']}, annotations={stats['annotations']}, coverage={stats['coverage']}")
        sys.exit(0)
    except Exception as exc:
        print(f"PILOT BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
