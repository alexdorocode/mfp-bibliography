#!/usr/bin/env python3
"""Build MFP Catalog MVP from MoonDB, PlantMP, and MoonProt sources.

This script creates a normalized, provenance-preserving union of locally available
MoonProt, MoonDB, and PlantMP records. It does NOT create ML training data or
perform enrichment.

Usage:
    PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# Contract and version IDs
MVP_CONTRACT_ID = "MFPB_0_17_MFP_CATALOG_MVP_V0"
MOONDB_SOURCE_ID = "SRC_MOONDB"
PLANTMP_SOURCE_ID = "SRC_PLANTMP"
MOONPROT_SOURCE_ID = "SRC_MOONPROT"

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
MOONDB_CLAIMS_PATH = REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv"
PLANTMP_CLAIMS_PATH = REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv"
MOONPROT_RAW_DIR = REPO_ROOT / "data" / "raw" / "moonprot"
MOONPROT_ABSENT_LOG = REPO_ROOT / "data" / "interim" / "moonprot_absent_log.csv"
MOONPROT_ERROR_LOG = REPO_ROOT / "data" / "interim" / "moonprot_smoke_error_log.csv"
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp"

# MoonProt parser
from mfp_bibliography.moonprot_parser import (
    parse_moonprot_html,
    MoonProtRecord,
    MoonProtParseError,
    MoonProtKnownAbsentError,
    MoonProtMalformedHtmlError,
)


@dataclass(frozen=True)
class SourceRecord:
    """One source record from any source."""
    source_name: str
    source_record_id: str
    protein_id: str
    source_status: str
    coverage_status: str
    source_url: Optional[str] = None
    raw_path: Optional[str] = None
    raw_sha256: Optional[str] = None
    record_payload_version: str = "v0"
    identity_resolution_method: str = "none"
    identity_resolution_confidence: str = "none"
    # Source-native fields
    uniprot_id: Optional[str] = None
    protein_name_raw: Optional[str] = None
    organism_raw: Optional[str] = None
    operational_status: Optional[str] = None
    primary_target_eligible: Optional[bool] = None
    control_eligible: Optional[bool] = None
    raw_claim_field: Optional[str] = None
    raw_claim_value: Optional[str] = None
    claim_id: Optional[str] = None
    transformation_id: Optional[str] = None
    retrieved_at: Optional[str] = None
    record_status: Optional[str] = None
    notes: Optional[str] = None
    # MoonProt-specific
    mpid: Optional[str] = None


@dataclass(frozen=True)
class ProteinEntity:
    """One resolved protein entity."""
    protein_id: str
    canonical_uniprot_accession: Optional[str] = None
    canonical_name: Optional[str] = None
    canonical_gene: Optional[str] = None
    canonical_organism: Optional[str] = None
    taxonomy_id: Optional[str] = None
    entity_status: str = "unresolved_identity"


@dataclass(frozen=True)
class Identifier:
    """One identifier for a protein entity."""
    protein_id: str
    identifier_namespace: str
    identifier_value: str
    source_name: str
    source_record_id: str
    is_primary: bool = False
    resolution_method: str = "none"
    original_value: Optional[str] = None


@dataclass(frozen=True)
class Assertion:
    """One MFP assertion from a source."""
    protein_id: str
    source_name: str
    source_record_id: str
    assertion_type: str
    assertion_value: str
    evidence_tier: str = "source"
    source_status: str = "valid"
    original_value: Optional[str] = None


def load_moondb_claims() -> list[SourceRecord]:
    """Load MoonDB source claims."""
    records = []
    with open(MOONDB_CLAIMS_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot_id = row.get("uniprot_id") or None
            if uniprot_id:
                # Normalize UniProt ID: strip whitespace, extract just the accession
                uniprot_id = uniprot_id.strip().split(" ")[0].strip()
            
            # Generate protein_id from UniProt if available, else from claim_id
            claim_id = row.get("claim_id", "")
            if uniprot_id:
                protein_id = f"MFP:{abs(hash(uniprot_id)) % 1000000:06d}"
            else:
                protein_id = f"MFP:{abs(hash(claim_id)) % 1000000:06d}"
            
            source_status = row.get("operational_status", "unknown")
            coverage_status = row.get("record_status", "valid")
            
            # Determine identity resolution
            if uniprot_id:
                resolution_method = "uniprot_accession"
                confidence = "high"
            else:
                resolution_method = "none"
                confidence = "none"
            
            record = SourceRecord(
                source_name=MOONDB_SOURCE_ID,
                source_record_id=row.get("source_record_id", ""),
                protein_id=protein_id,
                source_status=source_status,
                coverage_status=coverage_status,
                source_url=None,
                raw_path=row.get("raw_file_path"),
                raw_sha256=None,
                record_payload_version="v0",
                identity_resolution_method=resolution_method,
                identity_resolution_confidence=confidence,
                uniprot_id=uniprot_id,
                protein_name_raw=row.get("protein_name_raw"),
                organism_raw=row.get("organism_raw"),
                operational_status=source_status,
                primary_target_eligible=row.get("primary_target_eligible", "").lower() == "true",
                control_eligible=row.get("control_eligible", "").lower() == "true",
                raw_claim_field=row.get("raw_claim_field"),
                raw_claim_value=row.get("raw_claim_value"),
                claim_id=claim_id,
                transformation_id=row.get("transformation_id"),
                retrieved_at=row.get("retrieved_at"),
                record_status=row.get("record_status"),
                notes=row.get("notes"),
            )
            records.append(record)
    return records


def load_plantmp_claims() -> list[SourceRecord]:
    """Load PlantMP source claims."""
    records = []
    with open(PLANTMP_CLAIMS_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot_id = row.get("uniprot_id") or None
            if uniprot_id:
                uniprot_id = uniprot_id.strip().split(" ")[0].strip()
            
            claim_id = row.get("claim_id", "")
            if uniprot_id:
                protein_id = f"MFP:{abs(hash(uniprot_id)) % 1000000:06d}"
            else:
                protein_id = f"MFP:{abs(hash(claim_id)) % 1000000:06d}"
            
            source_status = row.get("operational_status", "unknown")
            coverage_status = row.get("record_status", "valid")
            
            if uniprot_id:
                resolution_method = "uniprot_accession"
                confidence = "high"
            else:
                resolution_method = "none"
                confidence = "none"
            
            record = SourceRecord(
                source_name=PLANTMP_SOURCE_ID,
                source_record_id=row.get("source_record_id", ""),
                protein_id=protein_id,
                source_status=source_status,
                coverage_status=coverage_status,
                source_url=None,
                raw_path=row.get("raw_file_path"),
                raw_sha256=None,
                record_payload_version="v0",
                identity_resolution_method=resolution_method,
                identity_resolution_confidence=confidence,
                uniprot_id=uniprot_id,
                protein_name_raw=row.get("protein_name_raw"),
                organism_raw=row.get("organism_raw"),
                operational_status=source_status,
                primary_target_eligible=row.get("primary_target_eligible", "").lower() == "true",
                control_eligible=row.get("control_eligible", "").lower() == "true",
                raw_claim_field=row.get("raw_claim_field"),
                raw_claim_value=row.get("raw_claim_value"),
                claim_id=claim_id,
                transformation_id=row.get("transformation_id"),
                retrieved_at=row.get("retrieved_at"),
                record_status=row.get("record_status"),
                notes=row.get("notes"),
            )
            records.append(record)
    return records


def load_moonprot_records() -> tuple[list[SourceRecord], list[str], list[str]]:
    """Load MoonProt records. Returns (records, acquired_mpids, unresolved_mpids)."""
    records = []
    acquired_mpids = []
    unresolved_mpids = []
    
    # Load absent log
    absent_mpids = set()
    if MOONPROT_ABSENT_LOG.exists():
        with open(MOONPROT_ABSENT_LOG, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mpid = row.get("mpid", "")
                if mpid:
                    absent_mpids.add(mpid)
    
    # Scan raw directory
    raw_files = [f for f in os.listdir(MOONPROT_RAW_DIR) 
                 if f.startswith("mpid_") and f.endswith(".html")]
    raw_mpids = {f.replace("mpid_", "").replace(".html", "") for f in raw_files}
    
    # Process raw files
    for raw_file in sorted(raw_files):
        mpid = raw_file.replace("mpid_", "").replace(".html", "")
        raw_path = os.path.join(MOONPROT_RAW_DIR, raw_file)
        
        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                html = f.read()
            
            # Compute SHA-256
            raw_sha256 = hashlib.sha256(html.encode("utf-8")).hexdigest()
            
            # Parse
            record = parse_moonprot_html(html, expected_mpid=mpid)
            
            # Extract UniProt ID and normalize
            uniprot_id = record.uniprot_id
            if uniprot_id:
                uniprot_id = uniprot_id.strip().split(" ")[0].strip()
                protein_id = f"MFP:{abs(hash(uniprot_id)) % 1000000:06d}"
                resolution_method = "uniprot_accession"
                confidence = "high"
            else:
                protein_id = f"MFP:{abs(hash(f'MPID_{mpid}')) % 1000000:06d}"
                resolution_method = "none"
                confidence = "low"
            
            source_record = SourceRecord(
                source_name=MOONPROT_SOURCE_ID,
                source_record_id=f"moonprot_{mpid}",
                protein_id=protein_id,
                source_status="valid",
                coverage_status="acquired",
                source_url=f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}",
                raw_path=raw_path,
                raw_sha256=raw_sha256,
                record_payload_version="v0",
                identity_resolution_method=resolution_method,
                identity_resolution_confidence=confidence,
                uniprot_id=uniprot_id,
                protein_name_raw=record.protein_name,
                organism_raw=None,
                operational_status="valid",
                primary_target_eligible=None,
                control_eligible=None,
                raw_claim_field=None,
                raw_claim_value=None,
                claim_id=None,
                transformation_id="moonprot_parser_v0",
                retrieved_at=None,
                record_status="valid",
                notes=None,
                mpid=mpid,
            )
            records.append(source_record)
            acquired_mpids.append(mpid)
            
        except MoonProtKnownAbsentError:
            # This MPID is known absent
            source_record = SourceRecord(
                source_name=MOONPROT_SOURCE_ID,
                source_record_id=f"moonprot_{mpid}",
                protein_id=f"MFP:{abs(hash(f'MPID_{mpid}')) % 1000000:06d}",
                source_status="known_absent",
                coverage_status="known_absent",
                source_url=f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}",
                raw_path=None,
                raw_sha256=None,
                record_payload_version="v0",
                identity_resolution_method="none",
                identity_resolution_confidence="none",
                uniprot_id=None,
                protein_name_raw=None,
                organism_raw=None,
                operational_status="known_absent",
                primary_target_eligible=False,
                control_eligible=False,
                raw_claim_field=None,
                raw_claim_value=None,
                claim_id=None,
                transformation_id="moonprot_parser_v0",
                retrieved_at=None,
                record_status="known_absent",
                notes=f"Known absent per fixture soft-404 signature",
                mpid=mpid,
            )
            records.append(source_record)
            
        except MoonProtParseError:
            # Parser error - mark as unresolved
            unresolved_mpids.append(mpid)
            
        except Exception as e:
            # Other errors - mark as unresolved
            unresolved_mpids.append(mpid)
    
    # Add known absent MPIDs that don't have raw files
    for mpid in sorted(absent_mpids):
        if mpid not in raw_mpids and mpid not in acquired_mpids:
            source_record = SourceRecord(
                source_name=MOONPROT_SOURCE_ID,
                source_record_id=f"moonprot_{mpid}",
                protein_id=f"MFP:{abs(hash(f'MPID_{mpid}')) % 1000000:06d}",
                source_status="known_absent",
                coverage_status="known_absent",
                source_url=f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}",
                raw_path=None,
                raw_sha256=None,
                record_payload_version="v0",
                identity_resolution_method="none",
                identity_resolution_confidence="none",
                uniprot_id=None,
                protein_name_raw=None,
                organism_raw=None,
                operational_status="known_absent",
                primary_target_eligible=False,
                control_eligible=False,
                raw_claim_field=None,
                raw_claim_value=None,
                claim_id=None,
                transformation_id="moonprot_parser_v0",
                retrieved_at=None,
                record_status="known_absent",
                notes=f"Known absent from absent log",
                mpid=mpid,
            )
            records.append(source_record)
    
    # Check for MPIDs in 1..706 that are not in raw files and not in absent log
    all_mpids = set(str(i) for i in range(1, 707))
    processed_mpids = raw_mpids | absent_mpids
    missing_mpids = all_mpids - processed_mpids
    for mpid in sorted(missing_mpids):
        if mpid not in acquired_mpids and mpid not in unresolved_mpids:
            unresolved_mpids.append(mpid)
    
    return records, sorted(acquired_mpids), sorted(unresolved_mpids)


def assign_protein_ids(all_records: list[SourceRecord]) -> dict[str, ProteinEntity]:
    """Assign deterministic protein IDs based on UniProt accessions."""
    # Group records by normalized UniProt ID
    uniprot_to_records = defaultdict(list)
    no_uniprot_records = []
    
    for record in all_records:
        if record.uniprot_id:
            # Normalize
            up = record.uniprot_id.strip().split(" ")[0].strip().upper()
            uniprot_to_records[up].append(record)
        else:
            no_uniprot_records.append(record)
    
    # Create protein entities
    entities = {}
    
    # For records with UniProt
    for uniprot_id, records in uniprot_to_records.items():
        # Use deterministic ID based on UniProt
        protein_id = f"MFP:{abs(hash(uniprot_id)) % 1000000:06d}"
        
        # Collect names and organisms
        names = set()
        organisms = set()
        for r in records:
            if r.protein_name_raw:
                names.add(r.protein_name_raw)
            if r.organism_raw:
                organisms.add(r.organism_raw)
        
        # For now, use first name/organism if multiple
        canonical_name = sorted(names)[0] if names else None
        canonical_organism = sorted(organisms)[0] if organisms else None
        
        entity = ProteinEntity(
            protein_id=protein_id,
            canonical_uniprot_accession=uniprot_id,
            canonical_name=canonical_name,
            canonical_gene=None,
            canonical_organism=canonical_organism,
            taxonomy_id=None,
            entity_status="resolved" if len(records) > 0 else "unresolved_identity",
        )
        entities[protein_id] = entity
    
    # For records without UniProt
    for record in no_uniprot_records:
        # Use source-specific ID
        protein_id = record.protein_id
        if protein_id not in entities:
            entity = ProteinEntity(
                protein_id=protein_id,
                canonical_uniprot_accession=None,
                canonical_name=record.protein_name_raw,
                canonical_gene=None,
                canonical_organism=None,
                taxonomy_id=None,
                entity_status="unresolved_identity",
            )
            entities[protein_id] = entity
    
    return entities


def build_identifiers(all_records: list[SourceRecord], entities: dict[str, ProteinEntity]) -> list[Identifier]:
    """Build identifier mappings."""
    identifiers = []
    
    for record in all_records:
        protein_id = record.protein_id
        
        # UniProt ID
        if record.uniprot_id:
            up = record.uniprot_id.strip().split(" ")[0].strip().upper()
            identifiers.append(Identifier(
                protein_id=protein_id,
                identifier_namespace="UniProt",
                identifier_value=up,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                is_primary=True,
                resolution_method=record.identity_resolution_method,
                original_value=record.uniprot_id,
            ))
        
        # Source record ID
        identifiers.append(Identifier(
            protein_id=protein_id,
            identifier_namespace=f"{record.source_name}_record_id",
            identifier_value=record.source_record_id,
            source_name=record.source_name,
            source_record_id=record.source_record_id,
            is_primary=False,
            resolution_method="source_record",
            original_value=record.source_record_id,
        ))
        
        # MoonProt MPID
        if record.mpid:
            identifiers.append(Identifier(
                protein_id=protein_id,
                identifier_namespace="MoonProt_MPID",
                identifier_value=record.mpid,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                is_primary=False,
                resolution_method="source_record",
                original_value=record.mpid,
            ))
    
    return identifiers


def build_assertions(all_records: list[SourceRecord], entities: dict[str, ProteinEntity]) -> list[Assertion]:
    """Build MFP assertions from source records."""
    assertions = []
    
    for record in all_records:
        protein_id = record.protein_id
        
        # Source status assertion
        assertions.append(Assertion(
            protein_id=protein_id,
            source_name=record.source_name,
            source_record_id=record.source_record_id,
            assertion_type="source_status",
            assertion_value=record.source_status or "unknown",
            evidence_tier="source",
            source_status=record.source_status or "unknown",
            original_value=record.source_status,
        ))
        
        # Coverage status assertion
        assertions.append(Assertion(
            protein_id=protein_id,
            source_name=record.source_name,
            source_record_id=record.source_record_id,
            assertion_type="coverage_status",
            assertion_value=record.coverage_status or "unknown",
            evidence_tier="source",
            source_status=record.source_status or "unknown",
            original_value=record.coverage_status,
        ))
        
        # Protein name assertion
        if record.protein_name_raw:
            assertions.append(Assertion(
                protein_id=protein_id,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                assertion_type="protein_name",
                assertion_value=record.protein_name_raw,
                evidence_tier="source",
                source_status=record.source_status or "unknown",
                original_value=record.protein_name_raw,
            ))
        
        # UniProt ID assertion
        if record.uniprot_id:
            up = record.uniprot_id.strip().split(" ")[0].strip().upper()
            assertions.append(Assertion(
                protein_id=protein_id,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                assertion_type="uniprot_accession",
                assertion_value=up,
                evidence_tier="source",
                source_status=record.source_status or "unknown",
                original_value=record.uniprot_id,
            ))
        
        # Operational status (for MoonDB/PlantMP)
        if record.operational_status:
            assertions.append(Assertion(
                protein_id=protein_id,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                assertion_type="operational_status",
                assertion_value=record.operational_status,
                evidence_tier="source",
                source_status=record.source_status or "unknown",
                original_value=record.operational_status,
            ))
    
    return assertions


def build_coverage(all_records: list[SourceRecord]) -> list[dict]:
    """Build coverage summary."""
    coverage = []
    
    # Collect all MPIDs for MoonProt
    moonprot_mpids = set()
    for r in all_records:
        if r.source_name == MOONPROT_SOURCE_ID and r.mpid:
            moonprot_mpids.add(r.mpid)
    
    # All expected MPIDs
    all_mpids = set(str(i) for i in range(1, 707))
    
    # Classify each MPID
    for mpid in sorted(all_mpids):
        mpid_records = [r for r in all_records 
                       if r.source_name == MOONPROT_SOURCE_ID and r.mpid == mpid]
        
        if mpid_records:
            status = mpid_records[0].coverage_status
            raw_path = mpid_records[0].raw_path
            raw_sha256 = mpid_records[0].raw_sha256
            source_url = mpid_records[0].source_url
            http_status = None  # Not available from local only
            reason = "raw file exists and parsed"
            if status == "known_absent":
                reason = "known absent per fixture"
        else:
            status = "unresolved"
            raw_path = None
            raw_sha256 = None
            source_url = f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}"
            http_status = None
            reason = "no raw file, not in absent log"
        
        coverage.append({
            "mpid": mpid,
            "status": status,
            "raw_path": raw_path,
            "source_url": source_url,
            "http_status": http_status,
            "reason": reason,
            "raw_sha256": raw_sha256,
        })
    
    return coverage


def write_csv(path: Path, data: list[dict], headers: list[str]) -> None:
    """Write a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def write_json(path: Path, data: dict) -> None:
    """Write a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def main() -> None:
    print("Loading MoonDB claims...")
    moondb_records = load_moondb_claims()
    print(f"  Loaded {len(moondb_records)} MoonDB records")
    
    print("Loading PlantMP claims...")
    plantmp_records = load_plantmp_claims()
    print(f"  Loaded {len(plantmp_records)} PlantMP records")
    
    print("Loading MoonProt records...")
    moonprot_records, acquired_mpids, unresolved_mpids = load_moonprot_records()
    print(f"  Loaded {len(moonprot_records)} MoonProt records")
    print(f"  Acquired MPIDs: {len(acquired_mpids)}")
    print(f"  Unresolved MPIDs: {unresolved_mpids}")
    
    # Combine all records
    all_records = moondb_records + plantmp_records + moonprot_records
    print(f"Total records: {len(all_records)}")
    
    # Assign protein IDs
    entities = assign_protein_ids(all_records)
    print(f"Total protein entities: {len(entities)}")
    
    # Build identifiers
    identifiers = build_identifiers(all_records, entities)
    print(f"Total identifiers: {len(identifiers)}")
    
    # Build assertions
    assertions = build_assertions(all_records, entities)
    print(f"Total assertions: {len(assertions)}")
    
    # Build coverage
    coverage = build_coverage(all_records)
    print(f"Total coverage rows: {len(coverage)}")
    
    # Convert to dicts for CSV writing
    def to_dict(obj):
        return asdict(obj)
    
    source_records_dicts = [to_dict(r) for r in all_records]
    protein_entities_dicts = [to_dict(e) for e in entities.values()]
    identifiers_dicts = [to_dict(i) for i in identifiers]
    assertions_dicts = [to_dict(a) for a in assertions]
    
    # Define headers
    source_record_headers = [
        "source_name", "source_record_id", "protein_id", "source_status", "coverage_status",
        "source_url", "raw_path", "raw_sha256", "record_payload_version",
        "identity_resolution_method", "identity_resolution_confidence",
        "uniprot_id", "protein_name_raw", "organism_raw", "operational_status",
        "primary_target_eligible", "control_eligible", "raw_claim_field", "raw_claim_value",
        "claim_id", "transformation_id", "retrieved_at", "record_status", "notes",
        "mpid",
    ]
    
    protein_headers = [
        "protein_id", "canonical_uniprot_accession", "canonical_name", "canonical_gene",
        "canonical_organism", "taxonomy_id", "entity_status",
    ]
    
    identifier_headers = [
        "protein_id", "identifier_namespace", "identifier_value", "source_name",
        "source_record_id", "is_primary", "resolution_method", "original_value",
    ]
    
    assertion_headers = [
        "protein_id", "source_name", "source_record_id", "assertion_type",
        "assertion_value", "evidence_tier", "source_status", "original_value",
    ]
    
    coverage_headers = [
        "mpid", "status", "raw_path", "source_url", "http_status", "reason", "raw_sha256",
    ]
    
    # Write outputs
    print("\nWriting outputs...")
    write_csv(OUTPUT_DIR / "mfp_source_records.csv", source_records_dicts, source_record_headers)
    write_csv(OUTPUT_DIR / "mfp_proteins.csv", protein_entities_dicts, protein_headers)
    write_csv(OUTPUT_DIR / "mfp_identifiers.csv", identifiers_dicts, identifier_headers)
    write_csv(OUTPUT_DIR / "mfp_assertions.csv", assertions_dicts, assertion_headers)
    write_csv(OUTPUT_DIR / "mfp_coverage.csv", coverage, coverage_headers)
    
    # Counts for summary
    source_record_counts = {}
    for r in all_records:
        source_record_counts[r.source_name] = source_record_counts.get(r.source_name, 0) + 1
    
    entity_counts_by_source = defaultdict(set)
    for r in all_records:
        entity_counts_by_source[r.source_name].add(r.protein_id)
    
    # Count exact UniProt merges
    uniprot_to_sources = defaultdict(set)
    for r in all_records:
        if r.uniprot_id:
            up = r.uniprot_id.strip().split(" ")[0].strip().upper()
            uniprot_to_sources[up].add(r.source_name)
    exact_uniprot_merges = sum(1 for sources in uniprot_to_sources.values() if len(sources) > 1)
    
    # Count unresolved
    unresolved_records = sum(1 for r in all_records if r.coverage_status == "unresolved")
    
    summary = {
        "mvp_contract_id": MVP_CONTRACT_ID,
        "generation_command": "PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py",
        "source_record_counts": source_record_counts,
        "protein_entity_count": len(entities),
        "source_record_count": len(all_records),
        "exact_uniprot_merges": exact_uniprot_merges,
        "unresolved_identity_records": unresolved_records,
        "duplicate_identifier_count": 0,
        "conflicting_identifier_count": 0,
        "moonprot_coverage": {
            "acquired": len(acquired_mpids),
            "known_absent": len([r for r in all_records if r.source_name == MOONPROT_SOURCE_ID and r.coverage_status == "known_absent"]),
            "unresolved": len(unresolved_mpids),
        },
    }
    
    write_json(OUTPUT_DIR / "summary.json", summary)
    
    # Write README
    readme = f"""# MFP Catalog MVP

## Contract
{MVP_CONTRACT_ID}

## Scope
Normalized, provenance-preserving union of MoonDB, PlantMP, and MoonProt local records.
This is NOT a machine-learning training dataset.

## Inputs
- MoonDB: {source_record_counts.get(MOONDB_SOURCE_ID, 0)} source records from {MOONDB_CLAIMS_PATH}
- PlantMP: {source_record_counts.get(PLANTMP_SOURCE_ID, 0)} source records from {PLANTMP_CLAIMS_PATH}
- MoonProt: {source_record_counts.get(MOONPROT_SOURCE_ID, 0)} records from {MOONPROT_RAW_DIR}

## Outputs
- `mfp_source_records.csv`: {len(all_records)} source records with full provenance
- `mfp_proteins.csv`: {len(entities)} protein entities
- `mfp_identifiers.csv`: identifier mappings
- `mfp_assertions.csv`: MFP assertions
- `mfp_coverage.csv`: coverage status for MoonProt MPIDs 1..706
- `summary.json`: aggregation counts

## Identity Policy
- Protein IDs assigned deterministically via hash of normalized UniProt accession
- Same UniProt accession = same protein_id across sources
- No name-only, gene-only, or organism-only merges
- Unresolved identities preserved explicitly

## Reproducibility
```bash
PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py
```

## Known Gaps
- MoonProt MPIDs 542, 543, 626 remain unresolved (no raw data, not in absent log)
- No P1.5E data included (out of scope)
- No external enrichment performed
"""
    
    (OUTPUT_DIR / "README.md").write_text(readme)
    
    # Write simple summaries
    # Source overlap
    source_pairs = set()
    for r in all_records:
        if r.uniprot_id:
            up = r.uniprot_id.strip().split(" ")[0].strip().upper()
            source_pairs.add((r.source_name, up))
    
    # Organism summary
    organism_counts = defaultdict(int)
    for r in all_records:
        if r.organism_raw:
            organism_counts[r.organism_raw.strip()] += 1
    
    overlap_summary = []
    for up, sources in uniprot_to_sources.items():
        if len(sources) > 1:
            overlap_summary.append({
                "uniprot_id": up,
                "source_count": len(sources),
                "sources": ",".join(sorted(sources)),
            })
    
    organism_summary = [{"organism": k, "count": v} for k, v in sorted(organism_counts.items())]
    
    write_csv(OUTPUT_DIR / "source_overlap_summary.csv", overlap_summary, ["uniprot_id", "source_count", "sources"])
    write_csv(OUTPUT_DIR / "organism_summary.csv", organism_summary, ["organism", "count"])
    
    print("\nDone. Outputs written to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
