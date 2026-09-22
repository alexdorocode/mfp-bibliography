"""Deterministic read-only MoonDB/PlantMP overlap audit (MFPB_0_10_MOONDB_PLANTMP_OVERLAP_AUDIT).

Cross-source overlap analysis keyed by `uniprot_id` over the two committed
per-source claims artifacts. Claims are read as-is: no deduplication, no
merging, no canonical records, and no NMF/control labeling. The precedence
outcome is reported under `simulated_effective_status`; it is a simulation
only and is never written as an `effective_status` field.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from mfp_bibliography.schemas import RecordValidationError
from mfp_bibliography.source_claims import read_claims_csv, validate_claim

CONTRACT_ID = "MFPB_0_10_MOONDB_PLANTMP_OVERLAP_AUDIT"
MOONDB_SOURCE_ID = "SRC_MOONDB"
PLANTMP_SOURCE_ID = "SRC_PLANTMP"
MOONDB_CLAIMS_PATH = "data/interim/source_claims_moondb.csv"
PLANTMP_CLAIMS_PATH = "data/interim/source_claims_plantmp.csv"
PRECEDENCE = ("curated", "predicted", "excluded_likely", "unresolved")
SIMULATED_STATUS_FIELD = "simulated_effective_status"
STRONG_STATUSES = ("curated", "predicted")
SIMULATION_NOTE = (
    "Simulation only. Precedence resolves a hypothetical cross-source outcome; "
    "source claims are neither merged nor deduplicated, and no effective_status "
    "is assigned."
)

_SOURCE_KEYS = (MOONDB_SOURCE_ID, PLANTMP_SOURCE_ID)


def load_validated_claims(csv_path: str | Path, expected_source_id: str) -> list[dict[str, Any]]:
    """Read a claims CSV and validate every claim against the contract schema.

    Raises RecordValidationError naming the offending CSV rows if any claim is
    schema-invalid, and ValueError if any claim carries an unexpected source_id.
    """
    claims = read_claims_csv(csv_path)
    invalid: list[str] = []
    wrong_source: list[str] = []
    for index, claim in enumerate(claims, start=2):
        try:
            validate_claim(claim)
        except RecordValidationError as exc:
            invalid.append(f"CSV row {index} (claim_id={claim.get('claim_id')!r}): {exc}")
        if claim.get("source_id") != expected_source_id:
            wrong_source.append(f"CSV row {index} (claim_id={claim.get('claim_id')!r})")
    if invalid:
        raise RecordValidationError(
            "Claims artifact failed contract validation:\n" + "\n".join(invalid)
        )
    if wrong_source:
        raise ValueError(
            f"Claims artifact contains rows with source_id other than {expected_source_id}: "
            + ", ".join(wrong_source)
        )
    return claims


def simulated_effective_status(statuses: Iterable[str]) -> str:
    """Resolve the highest-precedence status from an iterable of statuses."""
    present = set(statuses)
    for status in PRECEDENCE:
        if status in present:
            return status
    return PRECEDENCE[-1]


def _best_strong_status(statuses: Iterable[str]) -> str | None:
    """Return the highest-precedence curated/predicted status, or None."""
    present = set(statuses) & set(STRONG_STATUSES)
    if not present:
        return None
    for status in STRONG_STATUSES:
        if status in present:
            return status
    return None


def _statuses_by_uniprot(claims: list[dict[str, Any]]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = defaultdict(set)
    for claim in claims:
        uniprot_id = claim["uniprot_id"]
        if uniprot_id:
            mapping[uniprot_id].add(claim["operational_status"])
    return mapping


def _per_source_summary(
    source_id: str, claims: list[dict[str, Any]]
) -> dict[str, Any]:
    claim_counts = Counter(claim["uniprot_id"] for claim in claims if claim["uniprot_id"])
    duplicate_ids = sorted(uid for uid, count in claim_counts.items() if count > 1)
    return {
        "claim_count": len(claims),
        "unique_uniprot_count": len(claim_counts),
        "duplicate_claim_count": sum(count - 1 for count in claim_counts.values() if count > 1),
        "uniprot_ids_with_duplicate_claims": duplicate_ids,
        "counts_by_operational_status": dict(
            sorted(Counter(claim["operational_status"] for claim in claims).items())
        ),
    }


def build_overlap_audit(
    moondb_claims: list[dict[str, Any]],
    plantmp_claims: list[dict[str, Any]],
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the deterministic overlap audit report from validated claim lists."""
    moondb_statuses = _statuses_by_uniprot(moondb_claims)
    plantmp_statuses = _statuses_by_uniprot(plantmp_claims)

    moondb_ids = set(moondb_statuses)
    plantmp_ids = set(plantmp_statuses)
    shared_ids = sorted(moondb_ids & plantmp_ids)
    moondb_only = sorted(moondb_ids - plantmp_ids)
    plantmp_only = sorted(plantmp_ids - moondb_ids)

    status_combinations: Counter[str] = Counter()
    disagreement_details: list[dict[str, Any]] = []
    for uniprot_id in shared_ids:
        moondb_set = moondb_statuses[uniprot_id]
        plantmp_set = plantmp_statuses[uniprot_id]
        key = (
            f"{MOONDB_SOURCE_ID}={'+'.join(sorted(moondb_set))}"
            f"|{PLANTMP_SOURCE_ID}={'+'.join(sorted(plantmp_set))}"
        )
        status_combinations[key] += 1
        moondb_best = _best_strong_status(moondb_set)
        plantmp_best = _best_strong_status(plantmp_set)
        if (
            moondb_best is not None
            and plantmp_best is not None
            and moondb_best != plantmp_best
        ):
            disagreement_details.append(
                {
                    "uniprot_id": uniprot_id,
                    MOONDB_SOURCE_ID: sorted(moondb_set),
                    PLANTMP_SOURCE_ID: sorted(plantmp_set),
                }
            )

    moondb_likely = sorted(
        uid for uid, statuses in moondb_statuses.items() if "excluded_likely" in statuses
    )
    plantmp_likely = sorted(
        uid for uid, statuses in plantmp_statuses.items() if "excluded_likely" in statuses
    )
    # Shared means overlap-shared: IDs present in both sources with an
    # excluded_likely claim in either one.
    shared_likely = sorted(
        uid
        for uid in shared_ids
        if "excluded_likely" in moondb_statuses[uid] | plantmp_statuses[uid]
    )

    blank_by_source: dict[str, list[str]] = {}
    for source_id, claims in (
        (MOONDB_SOURCE_ID, moondb_claims),
        (PLANTMP_SOURCE_ID, plantmp_claims),
    ):
        blank_by_source[source_id] = sorted(
            claim["claim_id"] for claim in claims if not claim["uniprot_id"]
        )

    all_statuses = {
        uid: moondb_statuses.get(uid, set()) | plantmp_statuses.get(uid, set())
        for uid in moondb_ids | plantmp_ids
    }
    simulated_counts: Counter[str] = Counter(
        simulated_effective_status(statuses) for statuses in all_statuses.values()
    )

    report: dict[str, Any] = {
        "contract_id": CONTRACT_ID,
        "per_source": {
            source_id: _per_source_summary(
                source_id,
                moondb_claims if source_id == MOONDB_SOURCE_ID else plantmp_claims,
            )
            for source_id in _SOURCE_KEYS
        },
        "overlap": {
            "shared_uniprot_count": len(shared_ids),
            "shared_uniprot_ids": shared_ids,
            "moondb_exclusive_uniprot_count": len(moondb_only),
            "moondb_exclusive_uniprot_ids": moondb_only,
            "plantmp_exclusive_uniprot_count": len(plantmp_only),
            "plantmp_exclusive_uniprot_ids": plantmp_only,
            "status_combinations": dict(sorted(status_combinations.items())),
            "curated_predicted_disagreements": {
                "count": len(disagreement_details),
                "uniprot_ids": [detail["uniprot_id"] for detail in disagreement_details],
                "details": disagreement_details,
            },
        },
        "excluded_likely": {
            "count_by_source": {
                MOONDB_SOURCE_ID: len(moondb_likely),
                PLANTMP_SOURCE_ID: len(plantmp_likely),
            },
            "uniprot_ids_by_source": {
                MOONDB_SOURCE_ID: moondb_likely,
                PLANTMP_SOURCE_ID: plantmp_likely,
            },
            "shared_uniprot_count": len(shared_likely),
            "shared_uniprot_ids": shared_likely,
        },
        "missing_or_blank_uniprot": {
            "claim_count_by_source": {
                source_id: len(claim_ids)
                for source_id, claim_ids in blank_by_source.items()
            },
            "claim_ids_by_source": blank_by_source,
        },
        "simulated_precedence": {
            "status_field": SIMULATED_STATUS_FIELD,
            "precedence": list(PRECEDENCE),
            "note": SIMULATION_NOTE,
            "unique_uniprot_count": len(all_statuses),
            "counts_by_simulated_effective_status": dict(sorted(simulated_counts.items())),
            "by_shared_uniprot_id": {
                uid: simulated_effective_status(all_statuses[uid]) for uid in shared_ids
            },
        },
    }
    if inputs is not None:
        report["inputs"] = inputs
        # Keep inputs directly after contract_id for a stable, readable layout.
        ordered: dict[str, Any] = {"contract_id": report.pop("contract_id")}
        ordered["inputs"] = report.pop("inputs")
        ordered.update(report)
        return ordered
    return report


def _render_id_block(ids: list[str]) -> str:
    if not ids:
        return "_None._\n"
    return "```\n" + "\n".join(ids) + "\n```\n"


def render_overlap_audit_markdown(report: dict[str, Any]) -> str:
    """Render the audit report as deterministic Markdown."""
    lines: list[str] = []
    lines.append("# MoonDB / PlantMP overlap audit")
    lines.append("")
    lines.append(f"- **Contract ID**: `{report['contract_id']}`")
    lines.append("- **Mode**: deterministic, read-only cross-source audit keyed by `uniprot_id`")
    lines.append("- **Inputs**: source-claims contract CSVs; validated before analysis, never modified")
    lines.append("- **Claims handling**: no deduplication, no merging, no canonical records, no NMF/control labels")
    if "inputs" in report:
        lines.append("")
        lines.append("| Input | Path | SHA-256 |")
        lines.append("|---|---|---|")
        for name, info in sorted(report["inputs"].items()):
            lines.append(f"| {name} | `{info['path']}` | `{info['sha256']}` |")

    lines.append("")
    lines.append("## Per-source summary")
    lines.append("")
    lines.append(
        "| Source | Claims | Unique UniProt IDs | Duplicate claims |"
        " curated | predicted | excluded_likely | unresolved |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for source_id, summary in report["per_source"].items():
        by_status = summary["counts_by_operational_status"]
        cells = [str(summary[claim]) for claim in (
            "claim_count", "unique_uniprot_count", "duplicate_claim_count",
        )]
        cells += [str(by_status.get(status, 0)) for status in PRECEDENCE]
        lines.append(f"| {source_id} | " + " | ".join(cells) + " |")
    for source_id, summary in report["per_source"].items():
        if summary["uniprot_ids_with_duplicate_claims"]:
            lines.append("")
            lines.append(f"UniProt IDs with duplicate claims in {source_id}:")
            lines.append("")
            lines.append(
                _render_id_block(summary["uniprot_ids_with_duplicate_claims"]).rstrip("\n")
            )
            lines.append("")

    overlap = report["overlap"]
    lines.append("")
    lines.append("## Overlap by UniProt ID")
    lines.append("")
    lines.append(f"- Shared UniProt IDs: **{overlap['shared_uniprot_count']}**")
    lines.append(
        f"- {MOONDB_SOURCE_ID}-exclusive UniProt IDs: **{overlap['moondb_exclusive_uniprot_count']}**"
    )
    lines.append(
        f"- {PLANTMP_SOURCE_ID}-exclusive UniProt IDs: **{overlap['plantmp_exclusive_uniprot_count']}**"
    )
    for label, ids in (
        ("Shared UniProt IDs", overlap["shared_uniprot_ids"]),
        (f"{MOONDB_SOURCE_ID}-exclusive UniProt IDs", overlap["moondb_exclusive_uniprot_ids"]),
        (f"{PLANTMP_SOURCE_ID}-exclusive UniProt IDs", overlap["plantmp_exclusive_uniprot_ids"]),
    ):
        lines.append("")
        lines.append(f"### {label}")
        lines.append("")
        lines.append(_render_id_block(ids).rstrip("\n"))
        lines.append("")

    lines.append("")
    lines.append("### Status combinations for shared UniProt IDs")
    lines.append("")
    combinations = overlap["status_combinations"]
    if combinations:
        lines.append("| Combination | Count |")
        lines.append("|---|---|")
        for key, count in combinations.items():
            lines.append(f"| `{key}` | {count} |")
    else:
        lines.append("No shared UniProt IDs, so no status combinations to report.")

    disagreements = overlap["curated_predicted_disagreements"]
    lines.append("")
    lines.append("### Curated/predicted disagreements for shared UniProt IDs")
    lines.append("")
    if disagreements["count"]:
        lines.append("| UniProt ID | MoonDB statuses | PlantMP statuses |")
        lines.append("|---|---|---|")
        for detail in disagreements["details"]:
            lines.append(
                f"| {detail['uniprot_id']} | {', '.join(detail[MOONDB_SOURCE_ID])}"
                f" | {', '.join(detail[PLANTMP_SOURCE_ID])} |"
            )
    else:
        lines.append("No shared UniProt ID has a curated/predicted disagreement.")

    excluded = report["excluded_likely"]
    lines.append("")
    lines.append("## UniProt IDs with `excluded_likely` claims")
    lines.append("")
    for source_id in _SOURCE_KEYS:
        lines.append(f"### {source_id} ({excluded['count_by_source'][source_id]})")
        lines.append("")
        lines.append(_render_id_block(excluded["uniprot_ids_by_source"][source_id]).rstrip("\n"))
        lines.append("")
    lines.append("")
    lines.append(
        f"Shared UniProt IDs with `excluded_likely` in either source: {excluded['shared_uniprot_count']}"
    )

    missing = report["missing_or_blank_uniprot"]
    lines.append("")
    lines.append("## Missing or blank UniProt IDs")
    lines.append("")
    for source_id in _SOURCE_KEYS:
        count = missing["claim_count_by_source"][source_id]
        lines.append(f"- {source_id}: {count} claim(s) with missing/blank `uniprot_id`")
        if missing["claim_ids_by_source"][source_id]:
            lines.append(
                "  - claim_ids: "
                + ", ".join(f"`{claim_id}`" for claim_id in missing["claim_ids_by_source"][source_id])
            )

    simulated = report["simulated_precedence"]
    lines.append("")
    lines.append("## Simulated precedence outcome")
    lines.append("")
    lines.append(
        f"Precedence `{' > '.join(simulated['precedence'])}` applied per UniProt ID "
        f"as `{simulated['status_field']}`."
    )
    lines.append("")
    lines.append(f"> {simulated['note']}")
    lines.append("")
    lines.append(f"Unique UniProt IDs across both sources: {simulated['unique_uniprot_count']}")
    lines.append("")
    counts = simulated["counts_by_simulated_effective_status"]
    if counts:
        lines.append(f"| `{SIMULATED_STATUS_FIELD}` | Count |")
        lines.append("|---|---|")
        for status, count in counts.items():
            lines.append(f"| {status} | {count} |")
    else:
        lines.append("No UniProt IDs to resolve.")
    by_shared = simulated["by_shared_uniprot_id"]
    lines.append("")
    lines.append(f"`{SIMULATED_STATUS_FIELD}` for shared UniProt IDs:")
    lines.append("")
    if by_shared:
        lines.append("| UniProt ID | Simulated outcome |")
        lines.append("|---|---|")
        for uniprot_id, status in by_shared.items():
            lines.append(f"| {uniprot_id} | {status} |")
    else:
        lines.append("No shared UniProt IDs to resolve.")
    lines.append("")
    return "\n".join(lines)


def write_audit_outputs(
    report: dict[str, Any], json_path: str | Path, markdown_path: str | Path
) -> None:
    """Write the audit report as JSON and Markdown with stable formatting."""
    Path(json_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(
        render_overlap_audit_markdown(report), encoding="utf-8"
    )
