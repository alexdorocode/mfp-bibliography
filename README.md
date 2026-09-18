# mfp-bibliography

Multifunctional Protein Bibliography and Evidence Registry.

Aquest repositori prioritza traçabilitat i reproductibilitat.

## Purpose

This repository preserves, documents, versions, and harmonizes public source datasets and bibliographic evidence related to multifunctional / moonlighting proteins.

Current objective: **`v0.1.0-source-freeze`**.

## Non-goals

This repository is **not** currently an ML/modeling repository, classifier, embedding pipeline, web app, API, RAG system, or large-scale scraping workflow.

## Sources in scope

| Source | Status |
|---|---|
| MoonProt | planned_acquisition |
| MoonDB | to_be_imported |
| MultifacetedProtDB | to_be_imported |
| PlantMP | to_be_imported |
| MultitaskProtDB-II | to_be_imported |

## Data layers

`raw → interim → curated → release`

- `data/raw/`: immutable source artifacts (never manually edited)
- `data/interim/`: reproducible intermediate outputs
- `data/curated/`: normalized records and schemas
- `releases/`: release documentation and immutable release artifacts

## Core principles

- Raw source data is immutable.
- Provenance is mandatory for all derived records.
- Scientific label, evidence tier, and benchmark role are separate concepts.
- Transformations must be script-based and reproducible.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
python scripts/validate_repository.py
```

## Current PR scope

This initial scaffold includes **no real scientific datasets**, performs **no external scraping**, and does **not** contact MoonProt or any other external source.
MoonProt scraping is documented as a future, controlled task.
