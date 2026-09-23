#!/usr/bin/env python3
"""Generate effective-status artifact from MoonDB and PlantMP source claims.

MFPB_0_14_REAL_EFFECTIVE_STATUS_MOONDB_PLANTMP

Reads validated source-claim CSVs, aggregates by UniProt ID using precedence,
and produces:
- data/interim/effective_status_moondb_plantmp.csv
- data/interim/reports/effective_status_moondb_plantmp_report.json
- data/interim/reports/effective_status_moondb_plantmp_report.md

No network. No raw data mutation. No source-claim modification.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from mfp_bibliography.effective_status import (
    CONTRACT_ID,
    SourceClaim,
    aggregate_effective_status,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Input paths
MOONDB_CLAIMS_PATH = REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv"
PLANTMP_CLAIMS_PATH = REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv"

# Output paths
OUTPUT_CSV_PATH = REPO_ROOT / "data" / "interim" / "effective_status_moondb_plantmp.csv"
REPORT_JSON_PATH = REPO_ROOT / "data" / "interim" / "reports" / "effective_status_moondb_plantmp_report.json"
REPORT_MD_PATH = REPO_ROOT / "data" / "interim" / "reports" / "effective_status_moondb_plantmp_report.md"

TRANSFORMATION_ID = "effective_status_moondb_plantmp_v0"


@dataclass
class InputFileInfo:
    path: Path
    sha256: str
    claim_count: int
    sources: Counter
    statuses: Counter
    uniprot_count: int
    blank_uniprot_count: int


@dataclass
class AggregationReport:
    input_files: dict[str, InputFileInfo]
    total_input_claims: int
    total_unique_uniprot: int
    total_blank_uniprot: int
    aggregated_records: int
    excluded_records: int
    effective_status_counts: Counter
    source_combination_counts: Counter
    multi_status_uniprot_count: int
    aggregation_policy_id: str
    transformation_id: str
    output_csv_sha256: str | None = None


def read_claims(path: Path) -> list[SourceClaim]:
    """Read source claims CSV and return list of SourceClaim objects."""
    claims: list[SourceClaim] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uniprot_id = row["uniprot_id"] if row["uniprot_id"] else None
            claims.append(
                SourceClaim(
                    claim_id=row["claim_id"],
                    source_id=row["source_id"],
                    uniprot_id=uniprot_id,
                    operational_status=row["operational_status"],
                )
            )
    return claims


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def analyze_claims(claims: list[SourceClaim], source_id: str) -> InputFileInfo:
    """Analyze a list of claims and return statistics."""
    sha256 = compute_sha256(MOONDB_CLAIMS_PATH if source_id == "SRC_MOONDB" else PLANTMP_CLAIMS_PATH)
    
    uniprot_ids: set[str] = set()
    blank_count = 0
    sources: Counter = Counter()
    statuses: Counter = Counter()

    for claim in claims:
        sources[claim.source_id] += 1
        statuses[claim.operational_status] += 1
        if claim.uniprot_id and claim.uniprot_id.strip():
            uniprot_ids.add(claim.uniprot_id)
        else:
            blank_count += 1

    return InputFileInfo(
        path=MOONDB_CLAIMS_PATH if source_id == "SRC_MOONDB" else PLANTMP_CLAIMS_PATH,
        sha256=sha256,
        claim_count=len(claims),
        sources=sources,
        statuses=statuses,
        uniprot_count=len(uniprot_ids),
        blank_uniprot_count=blank_count,
    )


def write_csv_records(records: list, path: Path) -> str:
    """Write records to CSV and return SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        "uniprot_id",
        "effective_status",
        "source_ids",
        "claim_ids",
        "status_set",
        "has_curated_claim",
        "has_predicted_claim",
        "has_excluded_likely_claim",
        "has_unresolved_claim",
        "claim_count",
        "source_count",
        "aggregation_policy_id",
        "transformation_id",
        "record_status",
        "notes",
    ]
    
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for record in records:
            row = asdict(record)
            # Convert tuples to semicolon-separated strings
            row["source_ids"] = ";".join(row["source_ids"])
            row["claim_ids"] = ";".join(row["claim_ids"])
            row["status_set"] = ";".join(row["status_set"])
            writer.writerow(row)
    
    return compute_sha256(path)


def write_json_report(report: AggregationReport, path: Path) -> None:
    """Write report as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    report_dict = {
        "aggregation_policy_id": report.aggregation_policy_id,
        "transformation_id": report.transformation_id,
        "input_files": {
            name: {
                "path": str(info.path.relative_to(REPO_ROOT)),
                "sha256": info.sha256,
                "claim_count": info.claim_count,
                "sources": dict(info.sources),
                "statuses": dict(info.statuses),
                "unique_uniprot_count": info.uniprot_count,
                "blank_uniprot_count": info.blank_uniprot_count,
            }
            for name, info in report.input_files.items()
        },
        "total_input_claims": report.total_input_claims,
        "total_unique_uniprot": report.total_unique_uniprot,
        "total_blank_uniprot": report.total_blank_uniprot,
        "aggregated_records": report.aggregated_records,
        "excluded_records": report.excluded_records,
        "effective_status_counts": dict(report.effective_status_counts),
        "source_combination_counts": dict(report.source_combination_counts),
        "multi_status_uniprot_count": report.multi_status_uniprot_count,
        "output_csv_sha256": report.output_csv_sha256,
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)
        f.write("\n")


def write_md_report(report: AggregationReport, path: Path) -> None:
    """Write human-readable report as Markdown."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        "# Effective Status Report: MoonDB + PlantMP",
        "",
        f"- **Aggregation Policy**: {report.aggregation_policy_id}",
        f"- **Transformation ID**: {report.transformation_id}",
        "",
        "## Input Claims",
        "",
    ]
    
    for name, info in report.input_files.items():
        lines.extend([
            f"### {name}",
            f"- **Path**: `{info.path.relative_to(REPO_ROOT)}`",
            f"- **SHA-256**: `{info.sha256}`",
            f"- **Claim count**: {info.claim_count}",
            f"- **Unique UniProt IDs**: {info.uniprot_count}",
            f"- **Blank UniProt IDs**: {info.blank_uniprot_count}",
            "",
            "#### Sources:",
        ])
        for source, count in sorted(info.sources.items()):
            lines.append(f"- {source}: {count}")
        lines.extend([
            "",
            "#### Statuses:",
        ])
        for status, count in sorted(info.statuses.items()):
            lines.append(f"- {status}: {count}")
        lines.append("")
    
    lines.extend([
        "## Summary",
        "",
        f"- **Total input claims**: {report.total_input_claims}",
        f"- **Total unique UniProt IDs**: {report.total_unique_uniprot}",
        f"- **Total blank UniProt IDs**: {report.total_blank_uniprot}",
        f"- **Aggregated records**: {report.aggregated_records}",
        f"- **Excluded records**: {report.excluded_records}",
        "",
        "## Effective Status Distribution",
        "",
    ])
    for status, count in sorted(report.effective_status_counts.items()):
        lines.append(f"- {status}: {count}")
    
    lines.extend([
        "",
        "## Source Combinations",
        "",
    ])
    for combo, count in sorted(report.source_combination_counts.items()):
        lines.append(f"- {combo}: {count}")
    
    lines.extend([
        "",
        f"## Multi-Status UniProt IDs: {report.multi_status_uniprot_count}",
        "",
        f"## Output",
        "",
        f"- **CSV**: `{OUTPUT_CSV_PATH.relative_to(REPO_ROOT)}`",
        f"- **SHA-256**: `{report.output_csv_sha256}`",
        "",
    ])
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    """Main entry point. Returns exit code."""
    # Read input claims
    moondb_claims = read_claims(MOONDB_CLAIMS_PATH)
    plantmp_claims = read_claims(PLANTMP_CLAIMS_PATH)
    
    all_claims = moondb_claims + plantmp_claims
    
    # Analyze inputs
    moondb_info = analyze_claims(moondb_claims, "SRC_MOONDB")
    plantmp_info = analyze_claims(plantmp_claims, "SRC_PLANTMP")
    
    # Aggregate
    records = aggregate_effective_status(
        all_claims,
        aggregation_policy_id=CONTRACT_ID,
        transformation_id=TRANSFORMATION_ID,
    )
    
    # Separate valid and excluded records
    valid_records = [r for r in records if r.record_status == "valid"]
    excluded_records = [r for r in records if r.record_status == "excluded"]
    
    # Write CSV
    output_sha256 = write_csv_records(valid_records, OUTPUT_CSV_PATH)
    
    # Compute statistics for report
    effective_status_counts: Counter = Counter()
    for r in valid_records:
        effective_status_counts[r.effective_status] += 1
    
    # Source combination counts
    source_combos: Counter = Counter()
    for r in valid_records:
        combo = ";".join(sorted(set(r.source_ids)))
        source_combos[combo] += 1
    
    # Multi-status UniProt count
    multi_status_count = sum(
        1 for r in valid_records if len(r.status_set) > 1
    )
    
    # Count unique UniProt IDs
    all_uniprot_ids: set[str] = set()
    for r in valid_records:
        if r.uniprot_id:
            all_uniprot_ids.add(r.uniprot_id)
    
    report = AggregationReport(
        input_files={
            "moondb": moondb_info,
            "plantmp": plantmp_info,
        },
        total_input_claims=len(all_claims),
        total_unique_uniprot=len(all_uniprot_ids),
        total_blank_uniprot=moondb_info.blank_uniprot_count + plantmp_info.blank_uniprot_count,
        aggregated_records=len(valid_records),
        excluded_records=len(excluded_records),
        effective_status_counts=effective_status_counts,
        source_combination_counts=source_combos,
        multi_status_uniprot_count=multi_status_count,
        aggregation_policy_id=CONTRACT_ID,
        transformation_id=TRANSFORMATION_ID,
        output_csv_sha256=output_sha256,
    )
    
    # Write reports
    write_json_report(report, REPORT_JSON_PATH)
    write_md_report(report, REPORT_MD_PATH)
    
    # Print summary
    print(f"Effective status aggregation complete.")
    print(f"  Input: {report.total_input_claims} claims ({moondb_info.claim_count} MoonDB + {plantmp_info.claim_count} PlantMP)")
    print(f"  Aggregated: {report.aggregated_records} records")
    print(f"  Excluded: {report.excluded_records} records")
    print(f"  Output CSV: {OUTPUT_CSV_PATH.relative_to(REPO_ROOT)}")
    print(f"  Output SHA-256: {output_sha256}")
    print(f"  JSON report: {REPORT_JSON_PATH.relative_to(REPO_ROOT)}")
    print(f"  MD report: {REPORT_MD_PATH.relative_to(REPO_ROOT)}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
