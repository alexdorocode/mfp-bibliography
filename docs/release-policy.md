# Release Policy

## Versioning

Semantic versioning is used for repository releases.

## Meaning of `v0.1.0-source-freeze`

`v0.1.0-source-freeze` establishes the first immutable source-foundation baseline, including governance, schema, manifests/checksum scaffolding, and validation tooling.

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
