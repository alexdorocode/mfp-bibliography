# Release Policy

## Versioning

- Python package versioning follows PEP 440 (current package version: `0.1.0`).
- Repository milestones/releases may include descriptive labels (current target: `v0.1.0-source-freeze`).

## Meaning of `v0.1.0-source-freeze`

`v0.1.0-source-freeze` is a repository release label/milestone (not the Python package version). It establishes the first immutable source-foundation baseline, including governance, schema, manifests/checksum scaffolding, and validation tooling.

## Immutability of published releases

Published releases are never modified in place. Corrections require a new release version.

## Required release contents

- source catalog snapshot
- manifest file(s)
- checksum file(s)
- validation report
- derived artifacts (if any are approved)

## Correction workflow

Corrections are additive and recorded through new artifacts/manifests plus a new release tag and changelog entry.
