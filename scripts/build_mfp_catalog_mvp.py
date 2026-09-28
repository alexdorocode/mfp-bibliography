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
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# Contract and version IDs
MVP_CONTRACT_ID = "MFPB_0_19_MFP_CATALOG_MVP_V2"
MOONDB_SOURCE_ID = "SRC_MOONDB"
PLANTMP_SOURCE_ID = "SRC_PLANTMP"
MOONPROT_SOURCE_ID = "SRC_MOONPROT"
MULTIFACETEDPROTDB_SOURCE_ID = "SRC_MULTIFACETEDPROTDB"
MULTITASKPROTDB_II_SOURCE_ID = "SRC_MULTITASKPROTDB_II"

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
MOONDB_CLAIMS_PATH = REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv"
PLANTMP_CLAIMS_PATH = REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv"
MOONPROT_RAW_DIR = REPO_ROOT / "data" / "raw" / "moonprot"
MOONPROT_ABSENT_LOG = REPO_ROOT / "data" / "interim" / "moonprot_absent_log.csv"
MULTIFACETEDPROTDB_RECORDS_PATH = REPO_ROOT / "data" / "interim" / "source_records_multifacetedprotdb.csv"
MULTIFACETEDPROTDB_TRANSFORMATION_ID = "multifacetedprotdb_source_records_v0"
MULTIFACETEDPROTDB_RAW_PATH = "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json"
MULTITASKPROTDB_II_RECORDS_PATH = REPO_ROOT / "data" / "interim" / "source_records_multitaskprotdb_ii.csv"
MULTITASKPROTDB_II_TRANSFORMATION_ID = "multitaskprotdb_ii_source_records_v0"
MULTITASKPROTDB_II_RAW_PATH = "data/raw/multitaskprotdb-ii/proteins.csv"
MOONPROT_ERROR_LOG = REPO_ROOT / "data" / "interim" / "moonprot_smoke_error_log.csv"
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp"

# MoonProt snapshot universe: the MPID range covered by the current local
# acquisition snapshot. This is a snapshot-scope declaration, NOT MoonProt's
# permanent maximum. MPIDs outside this range are never silently included or
# dropped: the build fails closed and lists the offending IDs.
MOONPROT_SNAPSHOT_MPID_MIN = 1
MOONPROT_SNAPSHOT_MPID_MAX = 706


def moonprot_universe_mpids() -> set[str]:
    """The current snapshot universe of MoonProt MPIDs, as strings."""
    return {str(i) for i in range(MOONPROT_SNAPSHOT_MPID_MIN, MOONPROT_SNAPSHOT_MPID_MAX + 1)}


def validate_moonprot_universe(root: Path = REPO_ROOT) -> list[str]:
    """Detect MPIDs outside the snapshot universe in raw files, the artifact
    index and the absent log. Returns violation messages; empty means in scope.
    """
    root = Path(root)
    universe = moonprot_universe_mpids()
    errors: list[str] = []

    def _out_of_scope(ids: set[str]) -> list[str]:
        return sorted(ids - universe)

    raw_dir = root / "data" / "raw" / "moonprot"
    raw_mpids = {q.name[len("mpid_"):-len(".html")] for q in raw_dir.glob("mpid_*.html")}
    out_raw = _out_of_scope(raw_mpids)
    if out_raw:
        errors.append(f"raw MoonProt files outside snapshot universe "
                      f"{MOONPROT_SNAPSHOT_MPID_MIN}..{MOONPROT_SNAPSHOT_MPID_MAX}: {out_raw}")

    index, _ = parse_artifact_index(root)
    out_index = _out_of_scope(set(index))
    if out_index:
        errors.append(f"artifact index MPIDs outside snapshot universe "
                      f"{MOONPROT_SNAPSHOT_MPID_MIN}..{MOONPROT_SNAPSHOT_MPID_MAX}: {out_index}")

    absent_log = root / "data" / "interim" / "moonprot_absent_log.csv"
    absent_mpids: set[str] = set()
    if absent_log.exists():
        with absent_log.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("mpid"):
                    absent_mpids.add(row["mpid"].strip())
    out_absent = _out_of_scope(absent_mpids)
    if out_absent:
        errors.append(f"absent log MPIDs outside snapshot universe "
                      f"{MOONPROT_SNAPSHOT_MPID_MIN}..{MOONPROT_SNAPSHOT_MPID_MAX}: {out_absent}")

    return errors

# MoonProt parser
from mfp_bibliography.moonprot_parser import (
    parse_moonprot_html,
    MoonProtRecord,
    MoonProtParseError,
    MoonProtKnownAbsentError,
    MoonProtMalformedHtmlError,
)
from mfp_bibliography.provenance import sha256_file
from mfp_bibliography.raw_input_verification import (
    load_source_file_sha256,
    parse_artifact_index,
    verify_catalog_inputs,
)
from mfp_bibliography.normalization import (
    PROTEIN_ID_SCHEME_VERSION,
    make_protein_id_fallback,
    make_protein_id_uniprot,
    normalize_uniprot_accession,
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
    raw_file_sha256: Optional[str] = None
    record_payload_version: str = "v0"
    identity_resolution_method: str = "none"
    identity_resolution_confidence: str = "none"
    # Source-native fields
    uniprot_id: Optional[str] = None
    protein_name_raw: Optional[str] = None
    organism_raw: Optional[str] = None
    genes_raw: Optional[str] = None
    annotation_raw: Optional[str] = None
    canonical_function_raw: Optional[str] = None
    moonlighting_function_raw: Optional[str] = None
    go_raw: Optional[str] = None
    go_moon_raw: Optional[str] = None
    reference_raw: Optional[str] = None
    reference_article_like: Optional[str] = None
    reference_anomaly: Optional[str] = None
    pdbs_raw: Optional[str] = None
    pdb_uniprot_raw: Optional[str] = None
    models_raw: Optional[str] = None
    human_disease_raw: Optional[str] = None
    drugs_raw: Optional[str] = None
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


def load_moondb_claims(moondb_file_sha: str | None = None) -> list[SourceRecord]:
    """Load MoonDB source claims."""
    records = []
    with open(MOONDB_CLAIMS_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot_id = normalize_uniprot_accession(row.get("uniprot_id"))

            # Generate protein_id from UniProt if available, else from claim_id
            claim_id = row.get("claim_id", "")
            if uniprot_id:
                protein_id = make_protein_id_uniprot(uniprot_id)
            else:
                protein_id = make_protein_id_fallback(MOONDB_SOURCE_ID, claim_id)
            
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
                raw_file_sha256=moondb_file_sha,
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


def load_plantmp_claims(plantmp_file_sha: str | None = None) -> list[SourceRecord]:
    """Load PlantMP source claims."""
    records = []
    with open(PLANTMP_CLAIMS_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot_id = normalize_uniprot_accession(row.get("uniprot_id"))

            claim_id = row.get("claim_id", "")
            if uniprot_id:
                protein_id = make_protein_id_uniprot(uniprot_id)
            else:
                protein_id = make_protein_id_fallback(PLANTMP_SOURCE_ID, claim_id)
            
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
                raw_file_sha256=plantmp_file_sha,
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


def load_moonprot_records() -> tuple[list[SourceRecord], list[str], dict[str, dict], list[str]]:
    """Load MoonProt records from successfully parsed acquired HTML only.

    Returns (records, acquired_mpids, known_absent_info, unresolved_mpids).
    Known-absent MPIDs (fixture-detected or absent log) and unresolved MPIDs
    are coverage-only: they never create source records, protein entities,
    identifiers or assertions. Raw files that fail to parse fail the build
    loudly rather than being dropped silently.
    """
    records = []
    acquired_mpids = []
    unresolved_mpids = []
    parse_error_mpids = []
    known_absent_info: dict[str, dict] = {}

    # Load absent log with full provenance
    absent_log: dict[str, dict] = {}
    if MOONPROT_ABSENT_LOG.exists():
        with open(MOONPROT_ABSENT_LOG, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mpid = row.get("mpid", "")
                if mpid:
                    absent_log[mpid] = row

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

            # Compute per-record SHA-256 over the raw file bytes,
            # matching the authoritative artifact index grain
            raw_sha256 = sha256_file(raw_path)

            # Parse
            record = parse_moonprot_html(html, expected_mpid=mpid)

            # Extract UniProt ID and normalize
            uniprot_id = normalize_uniprot_accession(record.uniprot_id)
            if uniprot_id:
                protein_id = make_protein_id_uniprot(uniprot_id)
                resolution_method = "uniprot_accession"
                confidence = "high"
            else:
                protein_id = make_protein_id_fallback(MOONPROT_SOURCE_ID, f"MPID_{mpid}")
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
            # Fixture-detected known-absent raw file: coverage-only, no record
            known_absent_info[mpid] = {
                "raw_path": raw_path,
                "raw_sha256": sha256_file(raw_path),
                "source_url": f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}",
                "http_status": None,
                "reason": "Known absent per fixture soft-404 signature",
            }

        except Exception:
            # Parser errors must fail the build: the record would be silently lost
            parse_error_mpids.append(mpid)

    if parse_error_mpids:
        raise CatalogIntegrityError(
            f"MoonProt raw files failed to parse (records would be lost): {sorted(parse_error_mpids)}"
        )

    # Absent-log MPIDs without raw files: coverage-only known_absent
    for mpid in sorted(absent_log):
        if mpid not in raw_mpids and mpid not in acquired_mpids and mpid not in known_absent_info:
            row = absent_log[mpid]
            known_absent_info[mpid] = {
                "raw_path": None,
                "raw_sha256": None,
                "source_url": row.get("url") or f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}",
                "http_status": row.get("http_status") or None,
                "reason": (
                    f"Known absent per absent log "
                    f"({row.get('absent_marker', 'marker unknown')}, detected {row.get('detected_at', 'unknown')})"
                ),
            }

    # Check for MPIDs in 1..706 that are not in raw files and not in absent log
    all_mpids = moonprot_universe_mpids()
    processed_mpids = raw_mpids | set(absent_log)
    missing_mpids = all_mpids - processed_mpids
    for mpid in sorted(missing_mpids):
        if mpid not in acquired_mpids and mpid not in unresolved_mpids:
            unresolved_mpids.append(mpid)

    return records, sorted(acquired_mpids), known_absent_info, sorted(unresolved_mpids)


def load_multifacetedprotdb_records(
    records_path: Path = MULTIFACETEDPROTDB_RECORDS_PATH,
    expected_sha256: str | None = None,
) -> list[SourceRecord]:
    """Load validated interim MultifacetedProtDB source records.

    Binding is verified before consumption: every interim row must reference
    the registered raw path, the registered raw-file SHA-256 and the expected
    adapter transformation_id; otherwise the build fails closed. The source has
    no status field: source_status stays None and no status assertions are
    invented; operational_status is a derived administrative value only.
    """
    if expected_sha256 is None:
        expected_sha256 = load_source_file_sha256(REPO_ROOT, MULTIFACETEDPROTDB_SOURCE_ID)
    records: list[SourceRecord] = []
    with open(records_path, "r", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("source_id") != MULTIFACETEDPROTDB_SOURCE_ID:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: source_id mismatch"
                )
            if row.get("transformation_id") != MULTIFACETEDPROTDB_TRANSFORMATION_ID:
                raise CatalogIntegrityError(
                    f"stale or unrelated interim input at {records_path}: "
                    f"transformation_id {row.get('transformation_id')!r} "
                    f"!= {MULTIFACETEDPROTDB_TRANSFORMATION_ID!r}"
                )
            if row.get("raw_file_path") != MULTIFACETEDPROTDB_RAW_PATH:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: raw_file_path "
                    f"{row.get('raw_file_path')!r} != registered {MULTIFACETEDPROTDB_RAW_PATH!r}"
                )
            if row.get("raw_file_sha256") != expected_sha256:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: raw_file_sha256 "
                    f"{row.get('raw_file_sha256')!r} != registered {expected_sha256!r}"
                )
            uniprot = normalize_uniprot_accession(row.get("uniprot_normalized"))
            if uniprot is None or row.get("uniprot_normalized") != uniprot:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: accession is not canonical"
                )
            records.append(SourceRecord(
                source_name=MULTIFACETEDPROTDB_SOURCE_ID,
                source_record_id=row["source_record_id"],
                protein_id=make_protein_id_uniprot(uniprot),
                source_status=None,
                coverage_status="valid",
                source_url=None,
                raw_path=row["raw_file_path"],
                raw_sha256=None,
                raw_file_sha256=row["raw_file_sha256"],
                uniprot_id=uniprot,
                protein_name_raw=row.get("name_raw") or None,
                organism_raw=None,
                genes_raw=row.get("genes_raw") or None,
                annotation_raw=row.get("annotation_raw") or None,
                operational_status=row.get("operational_status") or None,
                raw_claim_field=None,
                raw_claim_value=None,
                claim_id=None,
                transformation_id=row["transformation_id"],
                retrieved_at=None,
                record_status="valid",
                notes=None,
            ))
    if not records:
        raise CatalogIntegrityError(f"interim input {records_path} contains no records")
    return records


def load_multitaskprotdb_ii_records(
    records_path: Path = MULTITASKPROTDB_II_RECORDS_PATH,
    expected_sha256: str | None = None,
) -> list[SourceRecord]:
    """Load validated interim MultitaskProtDB-II source records.

    Binding verified before consumption: every interim row must reference the
    registered raw path, the registered raw-file SHA-256 and the expected
    adapter transformation_id; otherwise the build fails closed. The source has
    no status field: source_status stays None and no status/evidence assertions
    are invented. GO/GO_Moon, references, functions and structure metadata are
    preserved verbatim as raw source data; reference anomalies stay attached to
    their rows and are never promoted to verified PMID/DOI.
    """
    if expected_sha256 is None:
        expected_sha256 = load_source_file_sha256(REPO_ROOT, MULTITASKPROTDB_II_SOURCE_ID)
    records: list[SourceRecord] = []
    with open(records_path, "r", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("source_id") != MULTITASKPROTDB_II_SOURCE_ID:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: source_id mismatch"
                )
            if row.get("transformation_id") != MULTITASKPROTDB_II_TRANSFORMATION_ID:
                raise CatalogIntegrityError(
                    f"stale or unrelated interim input at {records_path}: "
                    f"transformation_id {row.get('transformation_id')!r} "
                    f"!= {MULTITASKPROTDB_II_TRANSFORMATION_ID!r}"
                )
            if row.get("raw_file_path") != MULTITASKPROTDB_II_RAW_PATH:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: raw_file_path "
                    f"{row.get('raw_file_path')!r} != registered {MULTITASKPROTDB_II_RAW_PATH!r}"
                )
            if row.get("raw_file_sha256") != expected_sha256:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: raw_file_sha256 "
                    f"{row.get('raw_file_sha256')!r} != registered {expected_sha256!r}"
                )
            uniprot = normalize_uniprot_accession(row.get("uniprot_normalized"))
            if uniprot is None or row.get("uniprot_normalized") != uniprot:
                raise CatalogIntegrityError(
                    f"interim row {row.get('source_record_id')!r}: accession is not canonical"
                )
            records.append(SourceRecord(
                source_name=MULTITASKPROTDB_II_SOURCE_ID,
                source_record_id=row["source_record_id"],
                protein_id=make_protein_id_uniprot(uniprot),
                source_status=None,
                coverage_status="valid",
                source_url=None,
                raw_path=row["raw_file_path"],
                raw_sha256=None,
                raw_file_sha256=row["raw_file_sha256"],
                uniprot_id=uniprot,
                protein_name_raw=row.get("protein_name_raw") or None,
                organism_raw=row.get("organism_raw") or None,
                canonical_function_raw=row.get("canonical_function_raw") or None,
                moonlighting_function_raw=row.get("moonlighting_function_raw") or None,
                go_raw=row.get("go_raw") or None,
                go_moon_raw=row.get("go_moon_raw") or None,
                reference_raw=row.get("reference_raw") or None,
                reference_article_like=row.get("reference_article_like") or None,
                reference_anomaly=row.get("reference_anomaly") or None,
                pdbs_raw=row.get("pdbs_raw") or None,
                pdb_uniprot_raw=row.get("pdb_uniprot_raw") or None,
                models_raw=row.get("models_raw") or None,
                human_disease_raw=row.get("human_disease_raw") or None,
                drugs_raw=row.get("drugs_raw") or None,
                operational_status=row.get("operational_status") or None,
                raw_claim_field=None,
                raw_claim_value=None,
                claim_id=None,
                transformation_id=row["transformation_id"],
                retrieved_at=None,
                record_status="valid",
                notes=None,
            ))
    if not records:
        raise CatalogIntegrityError(f"interim input {records_path} contains no records")
    return records


def assign_protein_ids(all_records: list[SourceRecord]) -> dict[str, ProteinEntity]:
    """Assign deterministic protein IDs based on canonical UniProt accessions."""
    # Group records by canonical UniProt ID
    uniprot_to_records = defaultdict(list)
    no_uniprot_records = []

    for record in all_records:
        canonical = normalize_uniprot_accession(record.uniprot_id)
        if canonical:
            uniprot_to_records[canonical].append(record)
        else:
            no_uniprot_records.append(record)

    # Explicit collision detection: a protein_id must map to exactly one
    # canonical identity key, or the build must fail loudly.
    id_to_key: dict[str, str] = {}

    def claim_protein_id(protein_id: str, identity_key: str) -> None:
        previous = id_to_key.get(protein_id)
        if previous is not None and previous != identity_key:
            raise RuntimeError(
                f"protein_id collision under scheme {PROTEIN_ID_SCHEME_VERSION}: "
                f"{protein_id} claimed by {previous!r} and {identity_key!r}"
            )
        id_to_key[protein_id] = identity_key

    # Create protein entities
    entities = {}

    # For records with UniProt
    for uniprot_id, records in uniprot_to_records.items():
        # Deterministic ID based on canonical UniProt
        protein_id = make_protein_id_uniprot(uniprot_id)
        claim_protein_id(protein_id, f"uniprot::{uniprot_id}")
        
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
        # Use source-scoped fallback ID
        protein_id = record.protein_id
        claim_protein_id(protein_id, f"fallback::{record.source_name}::{_fallback_local_key(record)}")
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
            up = normalize_uniprot_accession(record.uniprot_id)
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
        
        # Source status assertion: emitted only when the source itself provides
        # a status value; a source without a status field never gets an
        # invented status or evidence assertion.
        if record.source_status is not None:
            assertions.append(Assertion(
                protein_id=protein_id,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                assertion_type="source_status",
                assertion_value=record.source_status,
                evidence_tier="source",
                source_status=record.source_status,
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
            up = normalize_uniprot_accession(record.uniprot_id)
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
        
        # Operational status assertion: only when the source itself provides
        # a status; operational_status is administrative for status-less sources
        # (e.g. MultifacetedProtDB) and is never emitted as source evidence.
        if record.operational_status and record.source_status is not None:
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


def build_coverage(all_records: list[SourceRecord], known_absent_info: dict[str, dict]) -> list[dict]:
    """Build coverage-only status rows for MoonProt MPIDs 1..706.

    Acquired MPIDs get their record provenance; known-absent MPIDs keep their
    fixture/absent-log provenance; the rest are unresolved. Coverage rows are
    status observations only: known_absent and unresolved MPIDs never create
    source records, protein entities, identifiers or assertions.
    """
    coverage = []

    record_by_mpid = {
        r.mpid: r for r in all_records
        if r.source_name == MOONPROT_SOURCE_ID and r.mpid
    }

    # All expected MPIDs
    all_mpids = moonprot_universe_mpids()

    for mpid in sorted(all_mpids):
        record = record_by_mpid.get(mpid)
        if record:
            coverage.append({
                "mpid": mpid,
                "status": record.coverage_status,
                "raw_path": record.raw_path,
                "source_url": record.source_url,
                "http_status": None,
                "reason": "raw file exists and parsed",
                "raw_sha256": record.raw_sha256,
            })
        elif mpid in known_absent_info:
            info = known_absent_info[mpid]
            coverage.append({
                "mpid": mpid,
                "status": "known_absent",
                "raw_path": info.get("raw_path"),
                "source_url": info.get("source_url"),
                "http_status": info.get("http_status"),
                "reason": info.get("reason"),
                "raw_sha256": info.get("raw_sha256"),
            })
        else:
            coverage.append({
                "mpid": mpid,
                "status": "unresolved",
                "raw_path": None,
                "source_url": f"http://www.moonlightingproteins.org/protein_detail/?mpid={mpid}",
                "http_status": None,
                "reason": "no raw file, not in absent log",
                "raw_sha256": None,
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


class CatalogIntegrityError(RuntimeError):
    """Raised when the built catalog violates integrity invariants."""


def _fallback_local_key(record: SourceRecord) -> str:
    """Local key for a source-scoped fallback identity (no UniProt)."""
    return record.claim_id or (f"MPID_{record.mpid}" if record.mpid else record.source_record_id)


def _identity_key(record: SourceRecord) -> str:
    """Canonical identity key of a record under MFPB_PROTEIN_ID_V1."""
    canonical = normalize_uniprot_accession(record.uniprot_id)
    if canonical:
        return f"uniprot::{canonical}"
    return f"fallback::{record.source_name}::{_fallback_local_key(record)}"


def compute_summary_metrics(all_records: list[SourceRecord], identifiers: list[Identifier]) -> dict:
    """Compute summary metrics from built rows; never hard-coded.

    - duplicate_identifier_count: identifier rows sharing the full identifier
      key (protein_id, namespace, value, source_name, source_record_id).
    - conflicting_identifier_count: (namespace, value) pairs claimed by more
      than one protein_id.
    - unresolved_identity_records: records with neither a canonical UniProt
      accession nor a usable source-scoped fallback key.
    - fallback_identity_records: records resolved via a source-scoped fallback
      ID (no UniProt). These are valid catalog identities, not unresolved ones.
    """
    identifier_keys = [
        (i.protein_id, i.identifier_namespace, i.identifier_value, i.source_name, i.source_record_id)
        for i in identifiers
    ]
    duplicate_identifier_count = len(identifier_keys) - len(set(identifier_keys))

    value_to_proteins = defaultdict(set)
    for i in identifiers:
        value_to_proteins[(i.identifier_namespace, i.identifier_value)].add(i.protein_id)
    conflicting_identifier_count = sum(1 for p in value_to_proteins.values() if len(p) > 1)

    unresolved_identity_records = 0
    fallback_identity_records = 0
    for r in all_records:
        if normalize_uniprot_accession(r.uniprot_id):
            continue
        fallback_identity_records += 1
        if not _fallback_local_key(r):
            unresolved_identity_records += 1

    return {
        "duplicate_identifier_count": duplicate_identifier_count,
        "conflicting_identifier_count": conflicting_identifier_count,
        "unresolved_identity_records": unresolved_identity_records,
        "fallback_identity_records": fallback_identity_records,
    }


def _count_csv_data_rows(path: Path) -> int:
    with open(path, "r", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def expected_source_record_counts(moonprot_acquired_count: int) -> dict[str, int]:
    """Expected per-source record counts: claims rows plus eligible acquired MoonProt records.

    Known-absent and unresolved MoonProt MPIDs are coverage-only status rows,
    never source records, so only successfully parsed acquired records count.
    """
    return {
        MOONDB_SOURCE_ID: _count_csv_data_rows(MOONDB_CLAIMS_PATH),
        PLANTMP_SOURCE_ID: _count_csv_data_rows(PLANTMP_CLAIMS_PATH),
        MOONPROT_SOURCE_ID: moonprot_acquired_count,
        MULTIFACETEDPROTDB_SOURCE_ID: _count_csv_data_rows(MULTIFACETEDPROTDB_RECORDS_PATH),
        MULTITASKPROTDB_II_SOURCE_ID: _count_csv_data_rows(MULTITASKPROTDB_II_RECORDS_PATH),
    }


def validate_catalog_integrity(
    all_records: list[SourceRecord],
    entities: dict[str, ProteinEntity],
    identifiers: list[Identifier],
    assertions: list[Assertion],
    expected_counts: dict[str, int],
) -> list[str]:
    """Return a list of integrity violations; empty means the catalog is sound."""
    errors: list[str] = []
    entity_ids = set(entities)
    record_keys = {(r.source_name, r.source_record_id) for r in all_records}

    # 1. every source record has exactly one existing protein_id
    for r in all_records:
        if not r.protein_id:
            errors.append(f"source record {r.source_name}/{r.source_record_id} has no protein_id")
        elif r.protein_id not in entity_ids:
            errors.append(f"orphan protein_id {r.protein_id} in source record {r.source_name}/{r.source_record_id}")

    # 2. every protein has at least one source record
    records_by_pid = {r.protein_id for r in all_records}
    for pid in entity_ids:
        if pid not in records_by_pid:
            errors.append(f"protein {pid} has no source record")

    # 3. identifiers and assertions reference existing proteins and source records
    for i in identifiers:
        if i.protein_id not in entity_ids:
            errors.append(f"identifier {i.identifier_namespace}/{i.identifier_value} references unknown protein {i.protein_id}")
        if (i.source_name, i.source_record_id) not in record_keys:
            errors.append(f"identifier {i.identifier_namespace}/{i.identifier_value} references unknown source record {i.source_name}/{i.source_record_id}")
    for a in assertions:
        if a.protein_id not in entity_ids:
            errors.append(f"assertion {a.assertion_type} references unknown protein {a.protein_id}")
        if (a.source_name, a.source_record_id) not in record_keys:
            errors.append(f"assertion {a.assertion_type} references unknown source record {a.source_name}/{a.source_record_id}")

    # 4. primary keys unique in every output table
    seen: dict[str, set] = {"record": set(), "identifier": set(), "assertion": set()}
    for r in all_records:
        key = (r.source_name, r.source_record_id)
        if key in seen["record"]:
            errors.append(f"duplicate source record key {key}")
        seen["record"].add(key)
    if len(entities) != len(entity_ids):
        errors.append("duplicate protein_id in mfp_proteins")
    for i in identifiers:
        key = (i.protein_id, i.identifier_namespace, i.identifier_value, i.source_name, i.source_record_id)
        if key in seen["identifier"]:
            errors.append(f"duplicate identifier key {key}")
        seen["identifier"].add(key)
    for a in assertions:
        key = (a.protein_id, a.source_name, a.source_record_id, a.assertion_type, a.assertion_value)
        if key in seen["assertion"]:
            errors.append(f"duplicate assertion key {key}")
        seen["assertion"].add(key)

    # 5. no distinct canonical identity keys share one protein_id
    key_by_pid: dict[str, str] = {}
    for r in all_records:
        identity_key = _identity_key(r)
        previous = key_by_pid.get(r.protein_id)
        if previous is not None and previous != identity_key:
            errors.append(
                f"protein_id {r.protein_id} claimed by distinct identity keys {previous!r} and {identity_key!r}"
            )
        key_by_pid[r.protein_id] = identity_key

    # conflicting identifiers: one (namespace, value) claimed by several proteins
    value_to_proteins = defaultdict(set)
    for i in identifiers:
        value_to_proteins[(i.identifier_namespace, i.identifier_value)].add(i.protein_id)
    for (namespace, value), proteins in sorted(value_to_proteins.items()):
        if len(proteins) > 1:
            errors.append(f"conflicting identifier {namespace}/{value} claimed by {sorted(proteins)}")

    # 6. source record counts conserved against the inputs
    actual_counts: dict[str, int] = defaultdict(int)
    for r in all_records:
        actual_counts[r.source_name] += 1
    for source, expected in expected_counts.items():
        actual = actual_counts.get(source, 0)
        if actual != expected:
            errors.append(
                f"source record count not conserved for {source}: expected {expected}, built {actual}"
            )
    return errors


def main() -> None:
    print("Verifying raw inputs against manifests and artifact index...")
    input_errors = verify_catalog_inputs(REPO_ROOT)
    if input_errors:
        for error in input_errors:
            print(f"[input] {error}", file=sys.stderr)
        raise SystemExit(
            f"Raw input verification failed with {len(input_errors)} error(s); no outputs written."
        )
    print("Raw input verification passed.")

    universe_errors = validate_moonprot_universe(REPO_ROOT)
    if universe_errors:
        for error in universe_errors:
            print(f"[universe] {error}", file=sys.stderr)
        raise SystemExit(
            f"MoonProt snapshot universe validation failed with {len(universe_errors)} error(s); "
            "no outputs written."
        )
    print("MoonProt snapshot universe validation passed.")

    moondb_file_sha = load_source_file_sha256(REPO_ROOT, MOONDB_SOURCE_ID)
    plantmp_file_sha = load_source_file_sha256(REPO_ROOT, PLANTMP_SOURCE_ID)

    print("Loading MoonDB claims...")
    moondb_records = load_moondb_claims(moondb_file_sha)
    print(f"  Loaded {len(moondb_records)} MoonDB records")
    
    print("Loading PlantMP claims...")
    plantmp_records = load_plantmp_claims(plantmp_file_sha)
    print(f"  Loaded {len(plantmp_records)} PlantMP records")
    
    print("Loading MultifacetedProtDB interim records...")
    multifacetedprotdb_records = load_multifacetedprotdb_records()
    print(f"  Loaded {len(multifacetedprotdb_records)} MultifacetedProtDB records")

    print("Loading MultitaskProtDB-II interim records...")
    multitaskprotdb_ii_records = load_multitaskprotdb_ii_records()
    print(f"  Loaded {len(multitaskprotdb_ii_records)} MultitaskProtDB-II records")

    print("Loading MoonProt records...")
    moonprot_records, acquired_mpids, known_absent_info, unresolved_mpids = load_moonprot_records()
    print(f"  Known absent MPIDs (coverage-only): {sorted(known_absent_info)}")
    print(f"  Loaded {len(moonprot_records)} MoonProt records")
    print(f"  Acquired MPIDs: {len(acquired_mpids)}")
    print(f"  Unresolved MPIDs: {unresolved_mpids}")
    
    # Combine all records
    all_records = (moondb_records + plantmp_records + moonprot_records
                   + multifacetedprotdb_records + multitaskprotdb_ii_records)
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
    coverage = build_coverage(all_records, known_absent_info)
    print(f"Total coverage rows: {len(coverage)}")

    # Integrity validation before any output is written
    integrity_errors = validate_catalog_integrity(
        all_records, entities, identifiers, assertions,
        expected_source_record_counts(len(moonprot_records)),
    )
    if integrity_errors:
        for error in integrity_errors:
            print(f"[integrity] {error}", file=sys.stderr)
        raise SystemExit(
            f"Catalog integrity validation failed with {len(integrity_errors)} error(s); no outputs written."
        )
    print("Integrity validation passed.")

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
        "source_url", "raw_path", "raw_sha256", "raw_file_sha256", "record_payload_version",
        "identity_resolution_method", "identity_resolution_confidence",
        "uniprot_id", "protein_name_raw", "organism_raw", "genes_raw", "annotation_raw", "canonical_function_raw", "moonlighting_function_raw", "go_raw", "go_moon_raw", "reference_raw", "reference_article_like", "reference_anomaly", "pdbs_raw", "pdb_uniprot_raw", "models_raw", "human_disease_raw", "drugs_raw", "operational_status",
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
            up = normalize_uniprot_accession(r.uniprot_id)
            uniprot_to_sources[up].add(r.source_name)
    exact_uniprot_merges = sum(1 for sources in uniprot_to_sources.values() if len(sources) > 1)
    
    # Compute metrics from built rows (never hard-coded)
    metrics = compute_summary_metrics(all_records, identifiers)

    summary = {
        "mvp_contract_id": MVP_CONTRACT_ID,
        "protein_id_scheme_version": PROTEIN_ID_SCHEME_VERSION,
        "generation_command": "PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py",
        "source_record_counts": source_record_counts,
        "protein_entity_count": len(entities),
        "source_record_count": len(all_records),
        "exact_uniprot_merges": exact_uniprot_merges,
        "unresolved_identity_records": metrics["unresolved_identity_records"],
        "fallback_identity_records": metrics["fallback_identity_records"],
        "duplicate_identifier_count": metrics["duplicate_identifier_count"],
        "conflicting_identifier_count": metrics["conflicting_identifier_count"],
        "moonprot_coverage": {
            "acquired": len(acquired_mpids),
            "known_absent": len(known_absent_info),
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
- MultifacetedProtDB: {source_record_counts.get(MULTIFACETEDPROTDB_SOURCE_ID, 0)} records from validated interim
  source records bound to the registered raw artifact and adapter transformation
- MultitaskProtDB-II: {source_record_counts.get(MULTITASKPROTDB_II_SOURCE_ID, 0)} records from validated interim
  source records (annotation-entry grain; repeated accessions are distinct
  observations) bound to the registered raw artifact and adapter transformation

## Outputs
- `mfp_source_records.csv`: {len(all_records)} source records with full provenance
- `mfp_proteins.csv`: {len(entities)} protein entities
- `mfp_identifiers.csv`: identifier mappings
- `mfp_assertions.csv`: MFP assertions
- `mfp_coverage.csv`: coverage-only statuses for MoonProt MPIDs
  {MOONPROT_SNAPSHOT_MPID_MIN}..{MOONPROT_SNAPSHOT_MPID_MAX}; known_absent
  and unresolved MPIDs never create source records, protein entities,
  identifiers or assertions. This range is the current local snapshot
  scope, not MoonProt's permanent maximum; out-of-scope MPIDs fail the
  build before publishing.
- `summary.json`: aggregation counts

## Identity Policy
- Protein ID scheme: {PROTEIN_ID_SCHEME_VERSION}. IDs are deterministic SHA-256
  digests (16 hex chars, collision-checked at build time) and are stable across
  runs and Python hash seeds.
- UniProt-resolved records get MFP:U:<digest>; records without UniProt get a
  source-scoped fallback ID MFP:F:<source>:<digest>, one entity per source record.
- Same normalized UniProt accession = same protein_id across sources.
- No name-only, gene-only, or organism-only merges.
- Unresolved identities preserved explicitly.

## Reproducibility
```bash
PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py
```

## Raw-Data Fields (contract MFPB_0_19_MFP_CATALOG_MVP_V2)
- MultitaskProtDB-II raw fields (canonical/moonlighting functions, GO and
  GO_Moon text, reference, PDBs, models, disease, drugs) are preserved
  verbatim per record. They are source data only: NOT verified GO
  annotations, NOT GO–article support, and never identity or evidence.
- `reference_article_like`/`reference_anomaly` flag non-article reference
  values on their original rows; anomalous values are never promoted to
  verified PMID/DOI.
- `genes_raw` / `annotation_raw`: optional, uninterpreted source raw data
  (MultifacetedProtDB); never used for identity, status or evidence.
- MultifacetedProtDB has no source status field: `source_status` stays empty,
  no status or evidence assertions are emitted for it, and
  `operational_status` is a derived administrative value only.

## Provenance Hash Fields
- `raw_sha256`: per-record hash of one specific MoonProt HTML file
  (raw_record_sha256 grain).
- `raw_file_sha256`: hash of the entire MoonDB/PlantMP source artifact
  (raw_file_sha256 grain, from data/manifests/source_manifest.csv); not a
  per-record checksum.

## Summary Metrics
- duplicate_identifier_count: identifier rows sharing the full identifier key
  (protein, namespace, value, source record). Computed from built rows.
- conflicting_identifier_count: identifier (namespace, value) pairs claimed by
  more than one protein. Computed from built rows.
- unresolved_identity_records: records with neither a canonical UniProt
  accession nor a usable source-scoped fallback key.
- fallback_identity_records: records resolved via a source-scoped fallback ID
  (no UniProt); these are valid catalog identities, not unresolved ones.
- The build validates cross-table integrity before writing any output and
  exits non-zero without publishing a catalog or summary on failure.

## Known Gaps
- MoonProt MPIDs 542, 543, 626 remain unresolved (no raw data, not in absent log)
- No P1.5E data included (out of scope)
- No external enrichment performed
- Protein IDs in the prior MVP snapshot used process-local hash() values and
  may differ from the IDs in this build. This build is not a final release.
"""
    
    (OUTPUT_DIR / "README.md").write_text(readme)
    
    # Write simple summaries
    # Source overlap
    source_pairs = set()
    for r in all_records:
        if r.uniprot_id:
            up = normalize_uniprot_accession(r.uniprot_id)
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
