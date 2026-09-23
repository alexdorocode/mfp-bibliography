#!/usr/bin/env python3
"""Quality audit for local MoonDB + PlantMP effective-status snapshot.

MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT

Reads:
- local effective-status CSV
- local snapshot manifest
- source_claims_moondb.csv
- source_claims_plantmp.csv

Generates:
- data/interim/reports/moondb_plantmp_snapshot_quality_audit.json
- data/interim/reports/moondb_plantmp_snapshot_quality_audit.md

No network. No modifications to inputs, labels, raw artifacts, manifests, policies.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

# Input paths
EFFECTIVE_STATUS_CSV = REPO_ROOT / "data" / "interim" / "effective_status_moondb_plantmp.csv"
SNAPSHOT_MANIFEST = REPO_ROOT / "data" / "interim" / "reports" / "effective_status_moondb_plantmp_snapshot.json"
MOONDB_CLAIMS = REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv"
PLANTMP_CLAIMS = REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv"

# Output paths
AUDIT_JSON_PATH = REPO_ROOT / "data" / "interim" / "reports" / "moondb_plantmp_snapshot_quality_audit.json"
AUDIT_MD_PATH = REPO_ROOT / "data" / "interim" / "reports" / "moondb_plantmp_snapshot_quality_audit.md"


@dataclass
class EffectiveStatusRecord:
    uniprot_id: str
    effective_status: str
    source_ids: str  # semicolon-separated
    claim_ids: str  # semicolon-separated
    status_set: str  # semicolon-separated
    has_curated_claim: bool
    has_predicted_claim: bool
    has_excluded_likely_claim: bool
    has_unresolved_claim: bool
    claim_count: int
    source_count: int
    aggregation_policy_id: str
    transformation_id: str
    record_status: str
    notes: str | None


@dataclass
class SourceClaim:
    claim_id: str
    source_id: str
    uniprot_id: str | None
    operational_status: str


def read_effective_status_csv(path: Path) -> list[EffectiveStatusRecord]:
    """Read effective status CSV and return list of records."""
    records: list[EffectiveStatusRecord] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(EffectiveStatusRecord(
                uniprot_id=row["uniprot_id"],
                effective_status=row["effective_status"],
                source_ids=row["source_ids"],
                claim_ids=row["claim_ids"],
                status_set=row["status_set"],
                has_curated_claim=row["has_curated_claim"].lower() == "true",
                has_predicted_claim=row["has_predicted_claim"].lower() == "true",
                has_excluded_likely_claim=row["has_excluded_likely_claim"].lower() == "true",
                has_unresolved_claim=row["has_unresolved_claim"].lower() == "true",
                claim_count=int(row["claim_count"]),
                source_count=int(row["source_count"]),
                aggregation_policy_id=row["aggregation_policy_id"],
                transformation_id=row["transformation_id"],
                record_status=row["record_status"],
                notes=row["notes"] if row["notes"] else None,
            ))
    return records


def read_source_claims(path: Path) -> list[SourceClaim]:
    """Read source claims CSV and return list of SourceClaim objects."""
    claims: list[SourceClaim] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot_id = row["uniprot_id"] if row["uniprot_id"] else None
            claims.append(SourceClaim(
                claim_id=row["claim_id"],
                source_id=row["source_id"],
                uniprot_id=uniprot_id,
                operational_status=row["operational_status"],
            ))
    return claims


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def analyze_snapshot(records: list[EffectiveStatusRecord], claims: list[SourceClaim]) -> dict[str, Any]:
    """Analyze the snapshot and return audit statistics."""
    # Count by effective status
    effective_status_counts: Counter = Counter()
    for r in records:
        effective_status_counts[r.effective_status] += 1

    # Source coverage
    source_coverage: Counter = Counter()
    for r in records:
        sources = r.source_ids.split(";") if r.source_ids else []
        for s in sources:
            source_coverage[s] += 1

    # IDs by claim count
    ids_by_claim_count: Counter = Counter()
    for r in records:
        ids_by_claim_count[r.claim_count] += 1

    # IDs by source count
    ids_by_source_count: Counter = Counter()
    for r in records:
        ids_by_source_count[r.source_count] += 1

    # IDs with each source-claim status set
    status_set_counts: Counter = Counter()
    for r in records:
        statuses = r.status_set.split(";") if r.status_set else []
        status_set_counts[tuple(sorted(statuses))] += 1

    # IDs where excluded_likely coexists with curated or predicted
    excluded_likely_with_stronger: int = 0
    for r in records:
        if r.has_excluded_likely_claim and (r.has_curated_claim or r.has_predicted_claim):
            excluded_likely_with_stronger += 1

    # Source-local duplicate claims
    # Group by (source_id, uniprot_id) to find duplicates
    source_uniprot_claims: dict[tuple[str, str], list[str]] = defaultdict(list)
    for claim in claims:
        if claim.uniprot_id:
            source_uniprot_claims[(claim.source_id, claim.uniprot_id)].append(claim.claim_id)

    source_local_duplicates: int = 0
    source_local_duplicate_details: list[dict[str, Any]] = []
    for (source_id, uniprot_id), claim_ids in source_uniprot_claims.items():
        if len(claim_ids) > 1:
            source_local_duplicates += 1
            source_local_duplicate_details.append({
                "source_id": source_id,
                "uniprot_id": uniprot_id,
                "claim_count": len(claim_ids),
                "claim_ids": claim_ids,
            })

    # All predicted IDs (candidate set for MoonProt reconciliation)
    predicted_ids: list[str] = []
    for r in records:
        if r.has_predicted_claim:
            predicted_ids.append(r.uniprot_id)

    # Input checksums
    input_checksums = {
        "effective_status_csv": compute_sha256(EFFECTIVE_STATUS_CSV),
        "snapshot_manifest": compute_sha256(SNAPSHOT_MANIFEST),
        "source_claims_moondb": compute_sha256(MOONDB_CLAIMS),
        "source_claims_plantmp": compute_sha256(PLANTMP_CLAIMS),
    }

    # Snapshot manifest info
    with open(SNAPSHOT_MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)

    return {
        "audit_metadata": {
            "audit_id": "moondb_plantmp_snapshot_quality_v0",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "aggregation_policy_id": manifest.get("aggregation_policy_id", "unknown"),
            "transformation_id": manifest.get("transformation_id", "unknown"),
        },
        "input_checksums": input_checksums,
        "record_count": len(records),
        "effective_status_counts": dict(effective_status_counts),
        "source_coverage": dict(source_coverage),
        "ids_by_claim_count": {
            "one_claim": ids_by_claim_count.get(1, 0),
            "multiple_claims": ids_by_claim_count.get("multiple", 0) if "multiple" in ids_by_claim_count else sum(
                v for k, v in ids_by_claim_count.items() if k > 1
            ),
        },
        "ids_by_source_count": {
            "one_source": ids_by_source_count.get(1, 0),
            "multiple_sources": sum(v for k, v in ids_by_source_count.items() if k > 1),
        },
        "status_set_distribution": {
            ";".join(tuple_str): count for tuple_str, count in status_set_counts.items()
        },
        "excluded_likely_with_stronger_count": excluded_likely_with_stronger,
        "source_local_duplicate_count": source_local_duplicates,
        "source_local_duplicate_details": source_local_duplicate_details,
        "predicted_ids_count": len(predicted_ids),
        "predicted_ids": sorted(predicted_ids),
        "output_checksums": {
            "audit_json": None,  # Will be filled after writing
            "audit_md": None,    # Will be filled after writing
        },
    }


def write_json_audit(audit: dict[str, Any], path: Path) -> str:
    """Write audit as JSON and return SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, default=str)
        f.write("\n")
    
    return compute_sha256(path)


def write_md_audit(audit: dict[str, Any], path: Path) -> str:
    """Write audit as Markdown and return SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        "# MoonDB + PlantMP Snapshot Quality Audit",
        "",
        f"- **Audit ID**: {audit['audit_metadata']['audit_id']}",
        f"- **Generated**: {audit['audit_metadata']['generated_at']}",
        f"- **Aggregation Policy**: {audit['audit_metadata']['aggregation_policy_id']}",
        f"- **Transformation ID**: {audit['audit_metadata']['transformation_id']}",
        "",
        "## Input Checksums",
        "",
    ]
    
    for name, sha in audit["input_checksums"].items():
        lines.append(f"- {name}: `{sha}`")
    
    lines.extend([
        "",
        "## Summary",
        "",
        f"- **Record count**: {audit['record_count']}",
        "",
        "## Effective Status Distribution",
        "",
    ])
    for status, count in sorted(audit["effective_status_counts"].items()):
        lines.append(f"- {status}: {count}")
    
    lines.extend([
        "",
        "## Source Coverage",
        "",
    ])
    for source, count in sorted(audit["source_coverage"].items()):
        lines.append(f"- {source}: {count}")
    
    lines.extend([
        "",
        "## IDs by Claim Count",
        "",
        f"- **One claim**: {audit['ids_by_claim_count']['one_claim']}",
        f"- **Multiple claims**: {audit['ids_by_claim_count']['multiple_claims']}",
        "",
        "## IDs by Source Count",
        "",
        f"- **One source**: {audit['ids_by_source_count']['one_source']}",
        f"- **Multiple sources**: {audit['ids_by_source_count']['multiple_sources']}",
        "",
        "## Status Set Distribution",
        "",
    ])
    for status_set, count in sorted(
        audit["status_set_distribution"].items(),
        key=lambda x: (len(x[0]), x[0])
    ):
        lines.append(f"- {'; '.join(status_set)}: {count}")
    
    lines.extend([
        "",
        f"## Excluded Likely with Stronger Status: {audit['excluded_likely_with_stronger_count']}",
        "",
        f"## Source-Local Duplicate Claims: {audit['source_local_duplicate_count']}",
        "",
    ])
    if audit["source_local_duplicate_count"] > 0:
        lines.append("### Details:")
        for detail in audit["source_local_duplicate_details"]:
            lines.append(
                f"- {detail['source_id']}: {detail['uniprot_id']} "
                f"({detail['claim_count']} claims: {', '.join(detail['claim_ids'])})"
            )
        lines.append("")
    
    lines.extend([
        "## Predicted IDs (MoonProt Reconciliation Candidates)",
        "",
        f"- **Count**: {audit['predicted_ids_count']}",
        f"- **IDs**: {', '.join(audit['predicted_ids'][:10])}{'...' if len(audit['predicted_ids']) > 10 else ''}",
        "",
    ])
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return compute_sha256(path)


if __name__ == "__main__":
    import sys
    
    print("Starting MoonDB + PlantMP snapshot quality audit...")
    
    # Read inputs
    records = read_effective_status_csv(EFFECTIVE_STATUS_CSV)
    moondb_claims = read_source_claims(MOONDB_CLAIMS)
    plantmp_claims = read_source_claims(PLANTMP_CLAIMS)
    all_claims = moondb_claims + plantmp_claims
    
    # Analyze
    audit = analyze_snapshot(records, all_claims)
    
    # Write outputs
    audit_json_sha = write_json_audit(audit, AUDIT_JSON_PATH)
    audit_md_sha = write_md_audit(audit, AUDIT_MD_PATH)
    
    # Update audit with output checksums
    audit["output_checksums"]["audit_json"] = audit_json_sha
    audit["output_checksums"]["audit_md"] = audit_md_sha
    
    # Re-write JSON with updated checksums
    write_json_audit(audit, AUDIT_JSON_PATH)
    
    print(f"Quality audit complete.")
    print(f"  Records analyzed: {audit['record_count']}")
    print(f"  Effective status: {audit['effective_status_counts']}")
    print(f"  Source coverage: {audit['source_coverage']}")
    print(f"  JSON audit: {AUDIT_JSON_PATH.relative_to(REPO_ROOT)}")
    print(f"  MD audit: {AUDIT_MD_PATH.relative_to(REPO_ROOT)}")
    print(f"  JSON SHA-256: {audit_json_sha}")
    print(f"  MD SHA-256: {audit_md_sha}")
    
    sys.exit(0)
