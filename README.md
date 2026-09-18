# mfp-bibliography

Multifunctional Protein Bibliography and Evidence Registry.

Aquest repositori prioritza traçabilitat i reproductibilitat.

## Purpose

This repository preserves, documents, versions, and harmonizes public source datasets and bibliographic evidence related to multifunctional / moonlighting proteins.

Current objective: **`v0.1.0-source-freeze`**.

Python package version: **`0.1.0`** (PEP 440 compliant).  
Repository release label/milestone: **`v0.1.0-source-freeze`**.

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
- `benchmark_role` exists for downstream compatibility only; records remain `unassigned` unless a separately approved benchmark protocol assigns a role.
- Transformations must be script-based and reproducible.

## Licensing boundaries (pre-release)

- Repository-owned code and documentation remain in pre-release status and are currently marked as all rights reserved pending a final repository license decision.
- Third-party source datasets are governed by their own source-specific licensing and redistribution terms, which remain `to_be_verified`.
- This repository does not currently claim redistribution permission for any third-party source dataset.

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
