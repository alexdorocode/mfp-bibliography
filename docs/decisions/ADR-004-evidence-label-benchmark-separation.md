# ADR-004: Evidence/Label/Benchmark Separation

- **Status**: Accepted

## Context

Sources use heterogeneous evidence semantics; conflation can create scientific errors.

## Decision

Scientific label, evidence tier, and benchmark role are separate fields and must not be conflated.

## Consequences

- Validation enforces independent controlled vocabularies.
- Repository-level assertions require explicit curation steps.

## Alternatives considered

- Single combined classification field (rejected: loses semantic separation).

## Deferred questions

- Governance process for benchmark-role assignment criteria.
