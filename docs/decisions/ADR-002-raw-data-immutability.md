# ADR-002: Raw Data Immutability

- **Status**: Accepted

## Context

Raw source artifacts must remain auditable and reproducible.

## Decision

Raw artifacts are append-only and never manually edited in place.

## Consequences

- Corrections are additive and documented through new artifacts/releases.
- Direct edits under `data/raw/` are disallowed.

## Alternatives considered

- In-place raw file correction (rejected: destroys audit trail).

## Deferred questions

- Policy details for redaction or legal takedown exceptions.
