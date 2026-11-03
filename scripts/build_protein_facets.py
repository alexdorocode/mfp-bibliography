#!/usr/bin/env python3
"""Build functional facets (BP1, MF1, CC1, PMID1 vs BP2, MF2, CC2, PMID2) for all catalog proteins.

Integrates raw sources, the unified catalog MVP, and TargetData PostgreSQL database.

Usage:
    PYTHONPATH=src /home/alexdoro/.local/bin/python3.12 scripts/build_protein_facets.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from mfp_bibliography.functional_normalization import (
    ProteinFacetsRecord,
    load_ec2go_mappings,
    normalize_moonprot_record,
    normalize_multitaskprotdb_ii_record,
    normalize_plantmp_record,
    resolve_mono_source_record,
)
from mfp_bibliography.moonprot_parser import parse_moonprot_fixture
from mfp_bibliography.normalization import make_protein_id_uniprot, normalize_uniprot_accession
from mfp_bibliography.targetdata_client import TargetDataClient

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp"
CATALOG_RECORDS_PATH = CATALOG_DIR / "mfp_source_records.csv"
CATALOG_PROTEINS_PATH = CATALOG_DIR / "mfp_proteins.csv"

PLANTMP_RAW_PATH = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"
MULTITASK_RAW_PATH = REPO_ROOT / "data" / "raw" / "multitaskprotdb-ii" / "proteins.csv"
MOONPROT_RAW_DIR = REPO_ROOT / "data" / "raw" / "moonprot"

OUTPUT_FACETS_CSV = CATALOG_DIR / "mfp_protein_facets.csv"
OUTPUT_RECORD_FACETS_CSV = CATALOG_DIR / "mfp_source_record_facets.csv"
OUTPUT_SUMMARY_JSON = CATALOG_DIR / "mfp_protein_facets_summary.json"

FACET_HEADERS = [
    "protein_id",
    "canonical_uniprot_accession",
    "source_name",
    "source_record_id",
    "bp1",
    "mf1",
    "cc1",
    "pmid1",
    "func1_desc",
    "bp2",
    "mf2",
    "cc2",
    "pmid2",
    "func2_desc",
    "facet_status",
    "resolution_sources",
    "notes",
]


def write_csv_records(path: Path, records: list[ProteinFacetsRecord], headers: list[str]) -> None:
    """Write list of ProteinFacetsRecord to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in records:
            writer.writerow(r.to_dict())


def main() -> None:
    print("=" * 70)
    print("MFP Bibliography — Functional Normalization Pipeline (BP1/MF1/CC1 vs BP2/MF2/CC2)")
    print("=" * 70)

    # 1. Connect to TargetData and preload ontology / mappings
    print("\n[1/5] Connecting to TargetData PostgreSQL and loading ontology mappings...")
    ec2go = load_ec2go_mappings()
    print(f"  Loaded {len(ec2go)} EC-to-GO xref mappings from go-basic.obo")

    td_client = None
    aspect_lookup = {}
    try:
        td_client = TargetDataClient()
        td_client.connect()
        aspect_lookup = td_client.preload_go_aspects()
        print(f"  Connected to TargetData successfully. Preloaded {len(aspect_lookup)} GO aspect mappings.")
    except Exception as exc:
        print(f"  [WARNING] TargetData database connection failed ({exc}). Proceeding offline with source-raw mappings only.")
        td_client = None

    # 2. Process Rich Facet Sources (PlantMP, MultitaskProtDB-II, MoonProt)
    print("\n[2/5] Parsing rich facet datasets...")
    resolved_facets_by_protein_id: dict[str, ProteinFacetsRecord] = {}
    record_facets: list[ProteinFacetsRecord] = []

    # PlantMP
    if PLANTMP_RAW_PATH.exists():
        with PLANTMP_RAW_PATH.open("r", encoding="utf-8", newline="") as f:
            count_plantmp = 0
            for row in csv.DictReader(f):
                rec = normalize_plantmp_record(row, td_client)
                record_facets.append(rec)
                if rec.protein_id and rec.protein_id not in resolved_facets_by_protein_id:
                    resolved_facets_by_protein_id[rec.protein_id] = rec
                count_plantmp += 1
            print(f"  PlantMP: processed {count_plantmp} raw rows.")

    # MultitaskProtDB-II
    if MULTITASK_RAW_PATH.exists():
        with MULTITASK_RAW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
            count_multitask = 0
            for row in csv.DictReader(f):
                rec = normalize_multitaskprotdb_ii_record(row, aspect_lookup, td_client)
                record_facets.append(rec)
                if rec.protein_id and rec.protein_id not in resolved_facets_by_protein_id:
                    resolved_facets_by_protein_id[rec.protein_id] = rec
                count_multitask += 1
            print(f"  MultitaskProtDB-II: processed {count_multitask} raw rows.")

    # MoonProt
    moonprot_files = sorted(MOONPROT_RAW_DIR.glob("mpid_*.html"))
    count_moonprot = 0
    for fpath in moonprot_files:
        mpid = fpath.stem.replace("mpid_", "")
        try:
            m_rec = parse_moonprot_fixture(fpath, expected_mpid=mpid)
            rec = normalize_moonprot_record(m_rec, ec2go, aspect_lookup, td_client)
            record_facets.append(rec)
            if rec.protein_id and rec.protein_id not in resolved_facets_by_protein_id:
                resolved_facets_by_protein_id[rec.protein_id] = rec
            count_moonprot += 1
        except Exception:
            # Skip known absent or unparseable coverage files
            continue
    print(f"  MoonProt: processed {count_moonprot} HTML pages.")

    print(f"  Total rich proteins with resolved facets: {len(resolved_facets_by_protein_id)}")

    # 3. Process MoonDB and MultifacetedProtDB with Cross-Source Inheritance
    print("\n[3/5] Processing MoonDB and MultifacetedProtDB (inheritance & mono-source resolution)...")
    if not CATALOG_RECORDS_PATH.exists():
        print(f"  [ERROR] Catalog records not found at {CATALOG_RECORDS_PATH}. Run build_mfp_catalog_mvp.py first.")
        sys.exit(1)

    inherited_count = 0
    mono_source_count = 0

    with CATALOG_RECORDS_PATH.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            source_name = row["source_name"]
            if source_name not in ("SRC_MOONDB", "SRC_MULTIFACETEDPROTDB"):
                continue

            protein_id = row["protein_id"]
            accession = row["uniprot_id"]
            source_record_id = row["source_record_id"]

            if protein_id in resolved_facets_by_protein_id:
                # Inherit from rich source
                donor = resolved_facets_by_protein_id[protein_id]
                inherited_rec = ProteinFacetsRecord(
                    protein_id=protein_id,
                    canonical_uniprot_accession=accession,
                    source_name=source_name,
                    source_record_id=source_record_id,
                    bp1=donor.bp1,
                    mf1=donor.mf1,
                    cc1=donor.cc1,
                    pmid1=donor.pmid1,
                    func1_desc=donor.func1_desc,
                    bp2=donor.bp2,
                    mf2=donor.mf2,
                    cc2=donor.cc2,
                    pmid2=donor.pmid2,
                    func2_desc=donor.func2_desc,
                    facet_status=donor.facet_status,
                    resolution_sources=f"{donor.resolution_sources}; cross_source_inherited",
                    notes=f"Facet definition inherited from {donor.source_name} ({donor.source_record_id})",
                )
                record_facets.append(inherited_rec)
                inherited_count += 1
            else:
                # Mono-source without facet separation
                mono_rec = resolve_mono_source_record(source_name, source_record_id, accession, td_client)
                record_facets.append(mono_rec)
                mono_source_count += 1

    print(f"  MoonDB & MultifacetedProtDB: {inherited_count} inherited facets; {mono_source_count} mono-source unassigned.")

    # 4. Build Unified Protein-Level Facets (one row per protein entity)
    print("\n[4/5] Building unified protein entity facets (mfp_protein_facets.csv)...")
    protein_entities = []
    with CATALOG_PROTEINS_PATH.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            protein_entities.append(row)

    protein_facets: list[ProteinFacetsRecord] = []
    for pe in protein_entities:
        pid = pe["protein_id"]
        acc = pe.get("canonical_uniprot_accession") or ""
        if pid in resolved_facets_by_protein_id:
            best = resolved_facets_by_protein_id[pid]
            consensus_rec = ProteinFacetsRecord(
                protein_id=pid,
                canonical_uniprot_accession=acc,
                source_name=best.source_name,
                source_record_id=best.source_record_id,
                bp1=best.bp1,
                mf1=best.mf1,
                cc1=best.cc1,
                pmid1=best.pmid1,
                func1_desc=best.func1_desc,
                bp2=best.bp2,
                mf2=best.mf2,
                cc2=best.cc2,
                pmid2=best.pmid2,
                func2_desc=best.func2_desc,
                facet_status=best.facet_status,
                resolution_sources=best.resolution_sources,
                notes=best.notes,
            )
            protein_facets.append(consensus_rec)
        else:
            mono_rec = resolve_mono_source_record("CATALOG_CONSENSUS", "consensus", acc, td_client)
            protein_facets.append(mono_rec)

    # 5. Output writing and metrics summary
    print("\n[5/5] Writing outputs and computing metrics...")
    write_csv_records(OUTPUT_RECORD_FACETS_CSV, record_facets, FACET_HEADERS)
    print(f"  Wrote record-level facets: {len(record_facets)} rows -> {OUTPUT_RECORD_FACETS_CSV}")

    write_csv_records(OUTPUT_FACETS_CSV, protein_facets, FACET_HEADERS)
    print(f"  Wrote protein-level facets: {len(protein_facets)} rows -> {OUTPUT_FACETS_CSV}")

    # Summary metrics
    status_counts = defaultdict(int)
    has_bp1 = has_mf1 = has_cc1 = has_pmid1 = 0
    has_bp2 = has_mf2 = has_cc2 = has_pmid2 = 0
    has_both_mf = has_both_bp = has_both_pmid = 0

    for r in protein_facets:
        status_counts[r.facet_status] += 1
        if r.bp1: has_bp1 += 1
        if r.mf1: has_mf1 += 1
        if r.cc1: has_cc1 += 1
        if r.pmid1: has_pmid1 += 1
        if r.bp2: has_bp2 += 1
        if r.mf2: has_mf2 += 1
        if r.cc2: has_cc2 += 1
        if r.pmid2: has_pmid2 += 1
        if r.mf1 and r.mf2: has_both_mf += 1
        if r.bp1 and r.bp2: has_both_bp += 1
        if r.pmid1 and r.pmid2: has_both_pmid += 1

    summary = {
        "total_protein_entities": len(protein_facets),
        "total_source_records": len(record_facets),
        "facet_status_distribution": dict(status_counts),
        "attribute_coverage": {
            "facet_1": {
                "bp1_count": has_bp1,
                "mf1_count": has_mf1,
                "cc1_count": has_cc1,
                "pmid1_count": has_pmid1,
            },
            "facet_2": {
                "bp2_count": has_bp2,
                "mf2_count": has_mf2,
                "cc2_count": has_cc2,
                "pmid2_count": has_pmid2,
            },
            "paired_divergence_eligible": {
                "both_mf_count (B3 MF-MF eligibility)": has_both_mf,
                "both_bp_count": has_both_bp,
                "both_pmid_count": has_both_pmid,
            },
        },
    }

    OUTPUT_SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_SUMMARY_JSON.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary saved to {OUTPUT_SUMMARY_JSON}")

    if td_client:
        td_client.close()

    print("\n" + "=" * 70)
    print("Functional Normalization Completed Successfully!")
    print(f"  Total Proteins: {len(protein_facets)}")
    print(f"  Resolved Facets: {status_counts['resolved']}")
    print(f"  Eligible for B3 (MF1 and MF2): {has_both_mf} proteins")
    print(f"  Eligible for B4 (MF1/CC1 or MF2/CC2): {has_mf1} / {has_mf2} proteins")
    print("=" * 70)


if __name__ == "__main__":
    main()
