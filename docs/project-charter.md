# Project Charter

## Mission

Build an auditable, reproducible, and versioned source-evidence foundation for multifunctional/moonlighting protein datasets and bibliography.

## First release scope (`v0.1.0-source-freeze`)

- Establish repository governance and policies.
- Define canonical schema and controlled vocabularies.
- Prepare source catalog templates and manifest/checksum structure.
- Provide offline validation tooling.

## Explicit non-goals

No classifier, embedding workflow, paper parser, web app, API, graph database, or large-scale ingestion/scraping.

## Relationship to downstream repositories

This repository is an upstream source-evidence foundation. Future repositories (for example, a Protein Embedding Classifier workflow) consume reviewed release artifacts from here and must not redefine raw provenance.

## Definition of source freeze

A source freeze is an immutable release snapshot containing source catalog state, manifest/checksum artifacts, validation outputs, and any approved derived artifacts.

## Success conditions for `v0.1.0-source-freeze`

- Governance and ADR baseline approved.
- Source catalog entries present with `to_be_verified` placeholders.
- Canonical schema and validators pass offline tests.
- No real source datasets committed yet.
