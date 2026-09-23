"""Effective Status Aggregation (MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0).

Pure aggregation helper that derives per-UniProt effective status from validated
source claims. No network, no real data mutation, no source-claim modification.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

CONTRACT_ID = "MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0"

# Precedence order: highest to lowest
PRECEDENCE_ORDER = ("curated", "predicted", "excluded_likely", "unresolved")

VALID_OPERATIONAL_STATUSES = frozenset(PRECEDENCE_ORDER)


@dataclass(frozen=True)
class EffectiveStatusRecord:
    """Derived aggregation record for one UniProt ID."""

    uniprot_id: str
    effective_status: str
    source_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    status_set: tuple[str, ...]
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "uniprot_id": self.uniprot_id,
            "effective_status": self.effective_status,
            "source_ids": list(self.source_ids),
            "claim_ids": list(self.claim_ids),
            "status_set": list(self.status_set),
            "has_curated_claim": self.has_curated_claim,
            "has_predicted_claim": self.has_predicted_claim,
            "has_excluded_likely_claim": self.has_excluded_likely_claim,
            "has_unresolved_claim": self.has_unresolved_claim,
            "claim_count": self.claim_count,
            "source_count": self.source_count,
            "aggregation_policy_id": self.aggregation_policy_id,
            "transformation_id": self.transformation_id,
            "record_status": self.record_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class SourceClaim:
    """Minimal source claim for aggregation input."""

    claim_id: str
    source_id: str
    uniprot_id: str | None
    operational_status: str


def _resolve_effective_status(statuses: set[str]) -> str:
    """Resolve effective status from set of operational statuses using precedence."""
    for status in PRECEDENCE_ORDER:
        if status in statuses:
            return status
    # This should never happen if input is validated, but fallback to unresolved
    return "unresolved"


def aggregate_effective_status(
    claims: list[SourceClaim],
    *,
    aggregation_policy_id: str = CONTRACT_ID,
    transformation_id: str = "effective_status_aggregation_v0",
) -> list[EffectiveStatusRecord]:
    """Aggregate validated source claims into per-UniProt effective status records.

    Args:
        claims: List of validated source claims. Must have non-null operational_status
            and valid operational_status values.
        aggregation_policy_id: Policy identifier (default: contract ID).
        transformation_id: Transformation identifier.

    Returns:
        List of EffectiveStatusRecord, one per non-empty uniprot_id. Claims with
        blank/missing uniprot_id produce excluded records.

    Raises:
        ValueError: If any claim has invalid operational_status or null claim_id/source_id.
    """
    # Validate input
    for i, claim in enumerate(claims):
        if not claim.claim_id:
            raise ValueError(f"Claim at index {i} has empty claim_id")
        if not claim.source_id:
            raise ValueError(f"Claim at index {i} has empty source_id")
        if claim.operational_status not in VALID_OPERATIONAL_STATUSES:
            raise ValueError(
                f"Claim {claim.claim_id} has invalid operational_status: "
                f"{claim.operational_status!r}"
            )

    # Group by uniprot_id
    groups: dict[str | None, list[SourceClaim]] = defaultdict(list)
    for claim in claims:
        groups[claim.uniprot_id].append(claim)

    records: list[EffectiveStatusRecord] = []

    for uniprot_id, group_claims in groups.items():
        if uniprot_id is None or uniprot_id.strip() == "":
            # Blank UniProt: produce excluded record for each
            for claim in group_claims:
                records.append(
                    EffectiveStatusRecord(
                        uniprot_id="",
                        effective_status="unresolved",
                        source_ids=(claim.source_id,),
                        claim_ids=(claim.claim_id,),
                        status_set=("unresolved",),
                        has_curated_claim=False,
                        has_predicted_claim=False,
                        has_excluded_likely_claim=False,
                        has_unresolved_claim=True,
                        claim_count=1,
                        source_count=1,
                        aggregation_policy_id=aggregation_policy_id,
                        transformation_id=transformation_id,
                        record_status="excluded",
                        notes="Blank/missing UniProt ID",
                    )
                )
        else:
            # Valid UniProt: aggregate
            statuses: set[str] = set()
            source_ids: list[str] = []
            claim_ids: list[str] = []

            for claim in group_claims:
                statuses.add(claim.operational_status)
                source_ids.append(claim.source_id)
                claim_ids.append(claim.claim_id)

            # Sort for deterministic output
            source_ids.sort()
            claim_ids.sort()

            effective_status = _resolve_effective_status(statuses)

            # Boolean flags
            has_curated = "curated" in statuses
            has_predicted = "predicted" in statuses
            has_excluded_likely = "excluded_likely" in statuses
            has_unresolved = "unresolved" in statuses

            # Sort status_set for deterministic output
            sorted_statuses = tuple(sorted(statuses, key=lambda s: PRECEDENCE_ORDER.index(s)))

            records.append(
                EffectiveStatusRecord(
                    uniprot_id=uniprot_id,
                    effective_status=effective_status,
                    source_ids=tuple(source_ids),
                    claim_ids=tuple(claim_ids),
                    status_set=sorted_statuses,
                    has_curated_claim=has_curated,
                    has_predicted_claim=has_predicted,
                    has_excluded_likely_claim=has_excluded_likely,
                    has_unresolved_claim=has_unresolved,
                    claim_count=len(group_claims),
                    source_count=len(set(source_ids)),
                    aggregation_policy_id=aggregation_policy_id,
                    transformation_id=transformation_id,
                    record_status="valid",
                    notes=None,
                )
            )

    return records
