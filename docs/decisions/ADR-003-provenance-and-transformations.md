# ADR-003: Provenance and Transformations

- **Status**: Accepted

## Context

Derived records must be traceable to source artifacts and transformation logic.

## Decision

Every derived record requires source locator metadata and a transformation identifier.

## Consequences

- Normalization pipelines must emit complete provenance fields.
- Validation checks include provenance completeness.

## Alternatives considered

- Partial provenance (rejected: inadequate reproducibility).

## Deferred questions

- Standard naming/versioning scheme for transformation identifiers.
