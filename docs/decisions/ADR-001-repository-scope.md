# ADR-001: Repository Scope

- **Status**: Accepted

## Context

The project needs an auditable source-evidence foundation before downstream modeling tasks.

## Decision

This repository is dedicated to source-evidence and bibliographic infrastructure, not ML/modeling implementation.

## Consequences

- Prioritize governance, provenance, schema, and release reproducibility.
- Defer classifier/embedding workflows to downstream repositories.

## Alternatives considered

- Combined source + ML repository (rejected: scope coupling and weaker audit boundaries).

## Deferred questions

- Interface contracts for downstream benchmark/model repositories.
