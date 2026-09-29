#!/usr/bin/env python3
"""Package the validated five-source catalog as a reproducible CANDIDATE.

Not the final v1 release. Packages byte-identical copies of the validated
catalog outputs plus manifest, checksums, data dictionary and README under
``releases/<candidate-id>/``. Fails without publishing anything if counts,
integrity, hashes or schema checks fail; never overwrites an existing
candidate directory with different bytes.

Usage:
    PYTHONPATH=src python scripts/package_catalog_candidate.py                 # package (REBUILD required)
    PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package  # PACKAGE_VERIFY (offline, clean clone)
    PYTHONPATH=src python scripts/package_catalog_candidate.py --verify       # REBUILD_COMPARE (requires rebuilt catalog)

Modes:
    PACKAGE_VERIFY  (--verify-package): internal package integrity only; reads
        nothing outside the candidate directory. Works in a clean, offline clone.
    REBUILD_COMPARE (--verify): compares the packaged candidate against locally
        rebuilt outputs in ``data/processed/mfp_catalog_mvp``; requires external,
        hash-identical raw/interim inputs (not available in a clean clone).

Any change to packaged bytes requires a new candidate version; this script
never modifies an existing candidate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

CANDIDATE_ID = "mfp-catalog-candidate-v0.2.0"
CATALOG_CONTRACT_ID = "MFPB_0_19_MFP_CATALOG_MVP_V2"
PROTEIN_ID_SCHEME = "MFPB_PROTEIN_ID_V1"

TABLES = [
    "mfp_proteins.csv",
    "mfp_source_records.csv",
    "mfp_identifiers.csv",
    "mfp_assertions.csv",
    "mfp_coverage.csv",
]

EXPECTED_SOURCES = {
    "SRC_MOONDB": 351,
    "SRC_MOONPROT": 702,
    "SRC_MULTIFACETEDPROTDB": 1103,
    "SRC_MULTITASKPROTDB_II": 694,
    "SRC_PLANTMP": 112,
}
EXPECTED_TOTAL_RECORDS = 2962
EXPECTED_PROTEINS = 2322
EXPECTED_MERGES = 463
EXPECTED_MOONPROT_COVERAGE = {"acquired": 702, "known_absent": 1, "unresolved": 3}

PACKAGE_FILES = TABLES + ["MANIFEST.json", "checksums.sha256", "README.md", "DATA_DICTIONARY.md"]


class PackagingError(RuntimeError):
    """Candidate packaging or verification failed; nothing is published."""


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_catalog(catalog_dir: Path) -> tuple[dict, dict[str, list[dict]]]:
    summary_path = catalog_dir / "summary.json"
    if not summary_path.is_file():
        raise PackagingError(f"missing {summary_path}")
    summary = json.loads(summary_path.read_text())
    tables: dict[str, list[dict]] = {}
    for name in TABLES:
        path = catalog_dir / name
        if not path.is_file():
            raise PackagingError(f"missing catalog table {name}")
        with path.open(newline="") as handle:
            tables[name] = list(csv.DictReader(handle))
    return summary, tables


def check_candidate_preconditions(summary: dict, tables: dict[str, list[dict]], catalog_dir: Path) -> dict:
    """Verify counts, contract, and PK/FK integrity before packaging."""
    if summary.get("mvp_contract_id") != CATALOG_CONTRACT_ID:
        raise PackagingError(
            f"catalog contract {summary.get('mvp_contract_id')!r} != expected {CATALOG_CONTRACT_ID!r}")
    counts = dict(summary.get("source_record_counts", {}))
    if counts != EXPECTED_SOURCES:
        raise PackagingError(f"source counts differ from expected five-source state: {counts}")
    if summary.get("source_record_count") != EXPECTED_TOTAL_RECORDS:
        raise PackagingError(f"total source records {summary.get('source_record_count')} != {EXPECTED_TOTAL_RECORDS}")
    if summary.get("protein_entity_count") != EXPECTED_PROTEINS:
        raise PackagingError(f"protein entities {summary.get('protein_entity_count')} != {EXPECTED_PROTEINS}")
    if summary.get("exact_uniprot_merges") != EXPECTED_MERGES:
        raise PackagingError(f"exact UniProt merges {summary.get('exact_uniprot_merges')} != {EXPECTED_MERGES}")
    if summary.get("moonprot_coverage") != EXPECTED_MOONPROT_COVERAGE:
        raise PackagingError(
            f"MoonProt coverage {summary.get('moonprot_coverage')} != {EXPECTED_MOONPROT_COVERAGE}")

    records = tables["mfp_source_records.csv"]
    proteins = tables["mfp_proteins.csv"]
    if len(records) != EXPECTED_TOTAL_RECORDS:
        raise PackagingError(f"mfp_source_records rows {len(records)} != {EXPECTED_TOTAL_RECORDS}")
    if len(proteins) != EXPECTED_PROTEINS:
        raise PackagingError(f"mfp_proteins rows {len(proteins)} != {EXPECTED_PROTEINS}")

    # MultitaskProtDB-II: 694 distinct rows
    mt = [r for r in records if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
    if len(mt) != 694 or len({r["source_record_id"] for r in mt}) != 694:
        raise PackagingError("MultitaskProtDB-II rows are not 694 distinct source records")

    # PK uniqueness
    if len({(r["source_name"], r["source_record_id"]) for r in records}) != len(records):
        raise PackagingError("duplicate source-record primary key")
    if len({p["protein_id"] for p in proteins}) != len(proteins):
        raise PackagingError("duplicate protein_id primary key")

    # FK integrity: every source record / identifier / assertion maps to one protein row
    protein_ids = {p["protein_id"] for p in proteins}
    orphan = [r["source_record_id"] for r in records if r["protein_id"] not in protein_ids]
    if orphan:
        raise PackagingError(f"{len(orphan)} source records reference missing proteins")
    for table in ("mfp_identifiers.csv", "mfp_assertions.csv"):
        orphans = [row for row in tables[table] if row["protein_id"] not in protein_ids]
        if orphans:
            raise PackagingError(f"{len(orphans)} orphan protein_id rows in {table}")

    # Measured metric decomposition (kept separate by definition)
    acc_sources = defaultdict(set)
    for r in records:
        if r["uniprot_id"]:
            acc_sources[r["uniprot_id"]].add(r["source_name"])
    merges = sum(1 for s in acc_sources.values() if len(s) > 1)
    repeated_obs = {a: c for a, c in Counter(
        r["uniprot_id"] for r in records if r["uniprot_id"]).items() if c > 1}
    return {
        "merge_count_measured": merges,
        "repeated_observation_accessions": len(repeated_obs),
        "repeated_observation_extra_rows": sum(repeated_obs.values()) - len(repeated_obs),
    }


def input_hashes(root: Path) -> dict:
    """Whole-file raw input hashes (distinguished from per-MPID MoonProt hashes)."""
    manifest_path = root / "data/manifests/source_manifest.csv"
    hashes = {}
    with manifest_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            hashes[row["source_id"]] = {
                "path": row["original_artifact_path"],
                "sha256_whole_file": row["sha256"],
                "grain": "whole_file",
            }
    artifact_index = root / "data/raw/moonprot/artifact_index.csv"
    return {
        "raw_input_files": hashes,
        "moonprot_per_mpid_hashes": {
            "note": "Per-MPID MoonProt HTML hashes are per-record (raw_sha256 in "
                    "mfp_source_records.csv) and authoritative in "
                    "data/raw/moonprot/artifact_index.csv; they are NOT whole-file hashes.",
            "artifact_index_sha256_whole_file": sha256_file(artifact_index),
        },
        "interim_source_record_files": {
            "SRC_MULTIFACETEDPROTDB": {
                "path": "data/interim/source_records_multifacetedprotdb.csv",
                "sha256": sha256_file(root / "data/interim/source_records_multifacetedprotdb.csv"),
            },
            "SRC_MULTITASKPROTDB_II": {
                "path": "data/interim/source_records_multitaskprotdb_ii.csv",
                "sha256": sha256_file(root / "data/interim/source_records_multitaskprotdb_ii.csv"),
            },
        },
    }


def build_manifest(root: Path, catalog_dir: Path, metrics: dict) -> dict:
    packaged_hashes = {name: sha256_file(catalog_dir / name) for name in TABLES}
    summary = json.loads((catalog_dir / "summary.json").read_text())
    return {
        "candidate_id": CANDIDATE_ID,
        "status": "CANDIDATE — not the final v1 release",
        "catalog_contract": CATALOG_CONTRACT_ID,
        "protein_id_scheme": PROTEIN_ID_SCHEME,
        "build_commands": [
            "PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py",
            "PYTHONPATH=src python scripts/package_catalog_candidate.py",
        ],
        "verification_command": "PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package",
        "rebuild_compare_command": "PYTHONPATH=src python scripts/package_catalog_candidate.py --verify",
        "measured_counts": {
            "source_record_count": summary["source_record_count"],
            "source_record_counts": summary["source_record_counts"],
            "protein_entity_count": summary["protein_entity_count"],
            "exact_uniprot_merge_count": summary["exact_uniprot_merges"],
            "moonprot_coverage": summary["moonprot_coverage"],
            "metric_definitions": {
                "source_record_count": "one row per source observation (row grain per source)",
                "protein_entity_count": "unique normalized UniProt accession entities",
                "exact_uniprot_merge_count": "accessions claimed by >= 2 sources; NOT "
                                             "source_record_count minus protein_entity_count",
                "repeated_observations": f"{metrics['repeated_observation_accessions']} accessions with "
                                        f"{metrics['repeated_observation_extra_rows']} extra rows within one source",
            },
        },
        "inputs": input_hashes(root),
        "packaged_outputs": {name: {"sha256": packaged_hashes[name]} for name in TABLES},
        "checksums_file": "checksums.sha256",
    }


def write_candidate_files(staging: Path, catalog_dir: Path, root: Path, metrics: dict) -> None:
    for name in TABLES:
        shutil.copyfile(catalog_dir / name, staging / name)
    manifest = build_manifest(root, catalog_dir, metrics)
    (staging / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (staging / "README.md").write_text(build_readme(manifest["measured_counts"]))
    (staging / "DATA_DICTIONARY.md").write_text(build_data_dictionary())
    checksum_lines = [
        f"{sha256_file(staging / name)}  {name}" for name in TABLES
    ] + [f"{sha256_file(staging / 'MANIFEST.json')}  MANIFEST.json"]
    (staging / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n")


def build_readme(counts: dict) -> str:
    return f"""# MFP Catalog Candidate {CANDIDATE_ID}

**STATUS: CANDIDATE — this is NOT the final v1 release.**

Accession-first bibliographic and analytical candidate catalog of
multifunctional/moonlighting proteins (MF/MFP) from five sources:
MoonDB ({counts['source_record_counts']['SRC_MOONDB']}),
MoonProt ({counts['source_record_counts']['SRC_MOONPROT']}),
MultifacetedProtDB ({counts['source_record_counts']['SRC_MULTIFACETEDPROTDB']}),
MultitaskProtDB-II ({counts['source_record_counts']['SRC_MULTITASKPROTDB_II']}),
PlantMP ({counts['source_record_counts']['SRC_PLANTMP']}).

## Scope and identity
- Catalog contract: {CATALOG_CONTRACT_ID}; protein ID scheme: {PROTEIN_ID_SCHEME}.
- Identity rule: cross-source merging ONLY by exact normalized UniProt accession
  equality. No name, gene, organism or fuzzy matching; no external enrichment.
- Every source observation links to its protein via `protein_id`; per-source
  labels are preserved verbatim and are source-specific claims, never global
  truth labels. Absence from a source is never negative evidence.

## Count definitions (kept separate)
- Source-record count: {counts['source_record_count']} — one row per source observation.
- Unique protein entities: {counts['protein_entity_count']} — one per normalized accession.
- Shared-accession merges: {counts['exact_uniprot_merge_count']} — accessions claimed by
  two or more sources. This is a separate metric; it is NOT
  source-record-count minus protein-entity-count.
- Repeated observations within a source also exist (e.g. MultitaskProtDB-II
  annotation-entry grain: 9 accessions with 2 rows each).

## Source statuses
- MoonDB and PlantMP carry explicit source labels (curated/predicted etc.),
  preserved verbatim.
- MultifacetedProtDB and MultitaskProtDB-II have NO explicit source evidence
  status. Their `operational_status=unresolved` is a neutral administrative
  policy value, NOT a scientific label and NOT evidence.

## Limitations
- No verified article-to-GO relationships exist in this candidate. All
  reference and GO text is raw, uninterpreted source data.
- MultitaskProtDB-II reference anomalies (rows
  multitaskprotdb_ii_row_239/349/422) remain raw and unverified; they are not
  PMIDs/DOIs.
- MoonProt MPIDs 542, 543 and 626 are unresolved; MPID 103 is known absent
  (coverage-only). MoonProt coverage is 702/1/3 — NOT complete MoonProt
  coverage is claimed, and no complete bibliography is claimed.
- Known-absent and unresolved MoonProt MPIDs never create protein entities
  (ADR-006).
- Not an MF-vs-NMF dataset; no negative set; no classifier or ML benchmark.

## Reproduction
See `MANIFEST.json` (`build_commands`, `verification_command` = offline
PACKAGE_VERIFY, `rebuild_compare_command` = REBUILD_COMPARE against locally
rebuilt outputs) and `checksums.sha256`. Byte-stable across runs and Python
hash seeds.
"""


def build_data_dictionary() -> str:
    return """# Data Dictionary (Candidate mfp-catalog-candidate-v0.2.0)

## mfp_proteins.csv — grain: one protein entity
- `protein_id` (PK): deterministic SHA-256 digest, scheme MFPB_PROTEIN_ID_V1.
  `MFP:U:<16 hex>` = UniProt-resolved; `MFP:F:<source>:<16 hex>` = source-scoped
  fallback (no accession). One row per normalized UniProt accession.
- `canonical_uniprot_accession`: normalized accession (nullable: fallback entities).
- `canonical_name`, `canonical_organism`: representative raw values (nullable).
- `entity_status`: `resolved` (accession) or `unresolved_identity` (fallback).

## mfp_source_records.csv — grain: one source observation (row)
- PK: (`source_name`, `source_record_id`); `source_record_id` is stable per source
  (row-position based for Multitask/MultitaskProtDB-II snapshots).
- `protein_id` (FK -> mfp_proteins.protein_id): exactly one per record.
- `source_status`: source-provided label, verbatim; EMPTY (null) for
  MultifacetedProtDB and MultitaskProtDB-II — never invented.
- `operational_status`: repository administrative bucket (policy-mapped for
  MoonDB/PlantMP; neutral `unresolved` for status-less sources). NOT a
  scientific label.
- `raw_path`, `raw_sha256` (per-record MoonProt HTML), `raw_file_sha256`
  (whole-file MoonDB/PlantMP/Multifaceted/Multitask artifacts).
- Raw-data columns (`genes_raw`, `annotation_raw`, `go_raw`, `go_moon_raw`,
  `reference_raw`, function/structure metadata): verbatim source data; empty
  (null) when the source provides nothing. Not verified annotations; not
  GO–article support.
- `reference_article_like` / `reference_anomaly`: field-level flags for
  non-article reference values; flagged values are never promoted to
  PMID/DOI.

## mfp_identifiers.csv — grain: one identifier claim per source record
- Natural key: (`protein_id`, `identifier_namespace`, `identifier_value`,
  `source_name`, `source_record_id`); `is_primary` marks the canonical UniProt row.

## mfp_assertions.csv — grain: one administrative assertion per source record
- Types: `source_status` (only when the source provides a status),
  `coverage_status`, `protein_name`, `uniprot_accession`, `operational_status`
  (only for sources with their own status). MultifacetedProtDB and
  MultitaskProtDB-II have zero evidence/status assertions: types limited to
  `coverage_status`, `protein_name`, `uniprot_accession`.
- No scientific evidence claims are created for status-less sources.

## mfp_coverage.csv — grain: one MoonProt MPID (snapshot universe 1..706)
- `status`: `acquired` (702), `known_absent` (1: MPID 103), `unresolved`
  (3: MPIDs 542/543/626). Coverage-only rows: never source records or proteins.
"""


def package(root: Path, catalog_dir: Path, releases_root: Path) -> int:
    try:
        summary, tables = load_catalog(catalog_dir)
        metrics = check_candidate_preconditions(summary, tables, catalog_dir)
        target = releases_root / CANDIDATE_ID
        if target.exists():
            existing = {p.name: sha256_file(p) for p in sorted(target.iterdir()) if p.is_file()}
            # Idempotent if identical; never overwrite with different bytes
            staging = Path(str(target) + ".staging")
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            write_candidate_files(staging, catalog_dir, root, metrics)
            staged = {p.name: sha256_file(p) for p in sorted(staging.iterdir()) if p.is_file()}
            if staged == existing:
                shutil.rmtree(staging)
                print(f"Candidate {CANDIDATE_ID} already packaged with identical bytes.")
                return 0
            shutil.rmtree(staging)
            raise PackagingError(
                f"refusing to overwrite existing candidate {target} with different bytes")
        staging = releases_root / (CANDIDATE_ID + ".staging")
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        write_candidate_files(staging, catalog_dir, root, metrics)
        staging.rename(target)
        print(f"Packaged candidate at {target}")
        return 0
    except (PackagingError, OSError, KeyError, ValueError) as exc:
        print(f"[candidate] {exc}", file=sys.stderr)
        return 1


def load_packaged_table(target: Path, name: str) -> list[dict]:
    path = target / name
    if not path.is_file():
        raise PackagingError(f"missing packaged table {name}")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise PackagingError(f"packaged table {name} is empty")
    return rows


def check_packaged_tables(target: Path, manifest: dict) -> None:
    """Structural self-consistency of the packaged CSVs against the manifest.

    Reads only files inside the candidate directory.
    """
    counts = manifest["measured_counts"]
    records = load_packaged_table(target, "mfp_source_records.csv")
    proteins = load_packaged_table(target, "mfp_proteins.csv")
    identifiers = load_packaged_table(target, "mfp_identifiers.csv")
    assertions = load_packaged_table(target, "mfp_assertions.csv")
    coverage = load_packaged_table(target, "mfp_coverage.csv")

    # Row counts against the manifest
    if len(records) != counts["source_record_count"]:
        raise PackagingError(
            f"packaged mfp_source_records.csv has {len(records)} rows, "
            f"manifest says {counts['source_record_count']}")
    if len(proteins) != counts["protein_entity_count"]:
        raise PackagingError(
            f"packaged mfp_proteins.csv has {len(proteins)} rows, "
            f"manifest says {counts['protein_entity_count']}")
    per_source = dict(Counter(r["source_name"] for r in records))
    if per_source != counts["source_record_counts"]:
        raise PackagingError(
            f"per-source row counts {per_source} != manifest "
            f"{counts['source_record_counts']}")

    # Coverage table: status counts and contiguous MPID universe
    coverage_expected = {
        "acquired": counts["moonprot_coverage"]["acquired"],
        "known_absent": counts["moonprot_coverage"]["known_absent"],
        "unresolved": counts["moonprot_coverage"]["unresolved"],
    }
    coverage_status = dict(Counter(c["status"] for c in coverage))
    if coverage_status != coverage_expected:
        raise PackagingError(
            f"mfp_coverage.csv status counts {coverage_status} != manifest "
            f"{coverage_expected}")
    mpids = sorted(int(c["mpid"]) for c in coverage)
    if len(set(mpids)) != len(mpids):
        raise PackagingError("duplicate mpid primary key in mfp_coverage.csv")
    if mpids and (mpids[0] != 1 or mpids[-1] != len(mpids)):
        raise PackagingError(
            f"mfp_coverage.csv MPID universe is not contiguous 1..{len(mpids)}")

    # Primary keys
    if len({(r["source_name"], r["source_record_id"]) for r in records}) != len(records):
        raise PackagingError("duplicate source-record primary key in mfp_source_records.csv")
    if len({p["protein_id"] for p in proteins}) != len(proteins):
        raise PackagingError("duplicate protein_id primary key in mfp_proteins.csv")
    identifier_keys = {
        (i["protein_id"], i["identifier_namespace"], i["identifier_value"],
         i["source_name"], i["source_record_id"]) for i in identifiers}
    if len(identifier_keys) != len(identifiers):
        raise PackagingError("duplicate identifier natural key in mfp_identifiers.csv")
    assertion_keys = {
        (a["protein_id"], a["source_name"], a["source_record_id"],
         a["assertion_type"]) for a in assertions}
    if len(assertion_keys) != len(assertions):
        raise PackagingError(
            "duplicate (protein_id, source_name, source_record_id, assertion_type) "
            "key in mfp_assertions.csv")

    # Foreign keys
    protein_ids = {p["protein_id"] for p in proteins}
    orphan_records = [r["source_record_id"] for r in records
                      if r["protein_id"] not in protein_ids]
    if orphan_records:
        raise PackagingError(
            f"{len(orphan_records)} packaged source records reference missing "
            f"proteins (first: {orphan_records[0]})")
    record_keys = {(r["source_name"], r["source_record_id"]) for r in records}
    for name, rows in (("mfp_identifiers.csv", identifiers),
                       ("mfp_assertions.csv", assertions)):
        orphan_proteins = [row for row in rows if row["protein_id"] not in protein_ids]
        if orphan_proteins:
            raise PackagingError(
                f"{len(orphan_proteins)} rows in packaged {name} reference "
                "missing proteins")
        orphan_records = [row for row in rows
                          if (row["source_name"], row["source_record_id"]) not in record_keys]
        if orphan_records:
            raise PackagingError(
                f"{len(orphan_records)} rows in packaged {name} reference "
                "missing source records")

    # Recomputed merge metric against the manifest
    acc_sources = defaultdict(set)
    for r in records:
        if r["uniprot_id"]:
            acc_sources[r["uniprot_id"]].add(r["source_name"])
    merges = sum(1 for s in acc_sources.values() if len(s) > 1)
    if merges != counts["exact_uniprot_merge_count"]:
        raise PackagingError(
            f"recomputed shared-accession merge count {merges} != manifest "
            f"{counts['exact_uniprot_merge_count']}")


def verify_package(releases_root: Path) -> int:
    """PACKAGE_VERIFY: offline integrity check of the packaged candidate.

    Reads only files inside ``releases/<CANDIDATE_ID>/``. Requires no raw
    inputs, interim files, ``data/processed/`` outputs, network, Git tags or
    catalog rebuild. Never writes into the candidate.
    """
    try:
        target = releases_root / CANDIDATE_ID
        if not target.is_dir():
            raise PackagingError(f"candidate directory {target} not found")

        # Inventory
        present = {p.name for p in target.iterdir() if p.is_file()}
        missing = [name for name in PACKAGE_FILES if name not in present]
        if missing:
            raise PackagingError(f"missing packaged files: {', '.join(sorted(missing))}")
        unexpected = sorted(present - set(PACKAGE_FILES))
        if unexpected:
            raise PackagingError(f"unexpected files in candidate: {', '.join(unexpected)}")

        # checksums.sha256: this candidate's checksum file covers the five
        # tables plus MANIFEST.json (README.md and DATA_DICTIONARY.md are
        # inventory-checked but not hash-listed by the existing package).
        listed: dict[str, str] = {}
        for line in (target / "checksums.sha256").read_text().splitlines():
            digest, name = line.split("  ", 1)
            listed[name] = digest
        for name in TABLES + ["MANIFEST.json"]:
            if name not in listed:
                raise PackagingError(f"checksums.sha256 does not list packaged file {name}")
        for name, digest in listed.items():
            path = target / name
            if not path.is_file():
                raise PackagingError(f"checksums.sha256 lists missing file {name}")
            actual = sha256_file(path)
            if actual != digest:
                raise PackagingError(
                    f"checksums.sha256 mismatch for {name}: file is {actual}, "
                    f"checksums say {digest}")

        # MANIFEST.json: identity, contract, packaged-table hashes.
        manifest = json.loads((target / "MANIFEST.json").read_text())
        if manifest.get("candidate_id") != CANDIDATE_ID:
            raise PackagingError(
                f"MANIFEST candidate_id {manifest.get('candidate_id')!r} != {CANDIDATE_ID!r}")
        if manifest.get("catalog_contract") != CATALOG_CONTRACT_ID:
            raise PackagingError(
                f"MANIFEST catalog_contract {manifest.get('catalog_contract')!r} != "
                f"{CATALOG_CONTRACT_ID!r}")
        for name, meta in manifest["packaged_outputs"].items():
            actual = sha256_file(target / name)
            if actual != meta["sha256"]:
                raise PackagingError(
                    f"packaged file {name} hash mismatch vs MANIFEST.json: "
                    f"file is {actual}, manifest says {meta['sha256']}")

        # Structural self-consistency of the packaged CSVs
        check_packaged_tables(target, manifest)

        print(
            f"Candidate {CANDIDATE_ID} PACKAGE_VERIFY OK: inventory, hashes, "
            "row counts, primary keys and foreign keys consistent with MANIFEST.json.")
        return 0
    except (PackagingError, OSError, KeyError, ValueError) as exc:
        print(f"[candidate] {exc}", file=sys.stderr)
        return 1


def verify(root: Path, catalog_dir: Path, releases_root: Path) -> int:
    try:
        target = releases_root / CANDIDATE_ID
        if not target.is_dir():
            raise PackagingError(f"candidate directory {target} not found")
        manifest = json.loads((target / "MANIFEST.json").read_text())
        for name, meta in manifest["packaged_outputs"].items():
            actual = sha256_file(target / name)
            if actual != meta["sha256"]:
                raise PackagingError(f"packaged file {name} hash mismatch")
        checksums = (target / "checksums.sha256").read_text().splitlines()
        for line in checksums:
            digest, name = line.split("  ", 1)
            if sha256_file(target / name) != digest:
                raise PackagingError(f"checksums.sha256 mismatch for {name}")
        summary, tables = load_catalog(catalog_dir)
        check_candidate_preconditions(summary, tables, catalog_dir)
        counts = manifest["measured_counts"]
        for name in TABLES:
            if sha256_file(catalog_dir / name) != manifest["packaged_outputs"][name]["sha256"]:
                raise PackagingError(
                    f"catalog table {name} differs from packaged candidate")
        print(f"Candidate {CANDIDATE_ID} REBUILD_COMPARE OK: packaged bytes are "
              "hash-identical to the locally rebuilt catalog outputs.")
        return 0
    except (PackagingError, OSError, KeyError, ValueError) as exc:
        print(f"[candidate] {exc}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--verify", action="store_true",
        help="REBUILD_COMPARE: compare the packaged candidate against locally "
             "rebuilt data/processed outputs (requires external hash-identical "
             "raw/interim inputs; not available in a clean clone)")
    mode.add_argument(
        "--verify-package", action="store_true",
        help="PACKAGE_VERIFY: offline integrity check of the packaged candidate; "
             "reads only files inside the candidate directory (clean-clone safe)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--catalog-dir", type=Path, default=None)
    parser.add_argument("--releases-root", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    catalog_dir = (args.catalog_dir or root / "data/processed/mfp_catalog_mvp").resolve()
    releases_root = (args.releases_root or root / "releases").resolve()
    if args.verify_package:
        return verify_package(releases_root)
    if args.verify:
        return verify(root, catalog_dir, releases_root)
    return package(root, catalog_dir, releases_root)


if __name__ == "__main__":
    raise SystemExit(main())
