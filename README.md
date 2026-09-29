# mfp-bibliography

Multifunctional Protein Bibliography and Evidence Registry.

Aquest repositori prioritza traçabilitat i reproductibilitat.

## Scope

This repository preserves, documents, versions, and harmonizes public source datasets and bibliographic evidence related to multifunctional / moonlighting proteins (MF/MFP).

It is a **bibliographic and provenance catalog**, currently materialized as the five-source candidate [`releases/mfp-catalog-candidate-v0.2.0/`](releases/mfp-catalog-candidate-v0.2.0/) (CANDIDATE — not the final v1 release).

It is **not**:

- an MF-vs-NMF dataset, classifier, ML benchmark, or negative set;
- a completed GO–article evidence graph: no verified article-to-GO relations exist in the candidate; all GO/reference text is raw, uninterpreted source data (laboratory GO integration is a planned future phase, see the [roadmap](docs/roadmap/mfp-catalog-implementation-plan.md));
- an ML/modeling repository, embedding pipeline, web app, API, or large-scale scraping workflow.

Python package version: `0.1.0` (PEP 440 compliant). Current repository milestone: the five-source catalog candidate `mfp-catalog-candidate-v0.2.0`.

## Start here: the candidate

New to the data? Read [docs/getting-started.md](docs/getting-started.md), then open the candidate directory: [`releases/mfp-catalog-candidate-v0.2.0/`](releases/mfp-catalog-candidate-v0.2.0/).

- **Primary table — [`mfp_proteins.csv`](releases/mfp-catalog-candidate-v0.2.0/mfp_proteins.csv)**: one row per protein entity (one per normalized UniProt accession).
- The other packaged tables provide interpretation and provenance for those proteins:
  - `mfp_source_records.csv`: one row per source observation, with verbatim source labels and full raw-data provenance;
  - `mfp_identifiers.csv`: identifier claims per source record;
  - `mfp_assertions.csv`: administrative assertions (no invented evidence);
  - `mfp_coverage.csv`: MoonProt snapshot coverage-only statuses (never protein entities).
- Column meanings and table grains: [DATA_DICTIONARY.md](releases/mfp-catalog-candidate-v0.2.0/DATA_DICTIONARY.md).

Cross-source merging is only by exact normalized UniProt accession equality; absence from a source is never negative evidence.

## Included sources (five)

Measured counts are defined by the candidate manifest — [`releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json`](releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json) (`measured_counts`) — not by this README or any historical note. As packaged in v0.2.0: 2,962 source records, 2,322 protein entities, 463 shared-accession merges.

| Source | Source records (v0.2.0 manifest) | Documentation |
|---|---|---|
| MoonDB | 351 | [source profile](docs/source-profiles/moondb.md) |
| MoonProt | 702 | [acquisition protocol](docs/acquisition-protocols/moonprot.md) |
| MultifacetedProtDB | 1,103 | [source profile](docs/source-profiles/multifacetedprotdb.md) |
| MultitaskProtDB-II | 694 | [source profile](docs/source-profiles/multitaskprotdb-ii.md) |
| PlantMP | 112 | [source profile](docs/source-profiles/plantmp.md) |

MoonProt coverage within its local snapshot is 702 acquired / 1 known absent / 3 unresolved (see Limitations).

## Three user paths

1. **Inspect the packaged CSVs** — no installation or rebuild needed; the candidate directory is self-contained. See [docs/getting-started.md](docs/getting-started.md).
2. **Verify the packaged bytes offline** — checks inventory, SHA-256 hashes, row counts, primary and foreign keys against the candidate manifest, reading nothing outside the candidate directory:

   ```bash
   PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
   ```

   This is `PACKAGE_VERIFY`, distinct from `--verify` (`REBUILD_COMPARE`), which compares the package against a locally rebuilt `data/processed/mfp_catalog_mvp/` catalog and therefore requires inputs that are not all in Git.

3. **Rebuild from raw/interim inputs** — only possible with local inputs beyond Git (MoonProt HTML artifacts, interim source-record CSVs, prior processed outputs are ignored by `.gitignore`). Prerequisites and caveats: [docs/getting-started.md](docs/getting-started.md).

## Known limitations (candidate v0.2.0)

Full statement: [candidate README](releases/mfp-catalog-candidate-v0.2.0/README.md) and [release notes](docs/releases/mfp-catalog-candidate-v0.2.0.md).

- MoonProt snapshot gaps: MPID 103 is known absent; MPIDs 542, 543 and 626 are unresolved. Coverage-only; no complete MoonProt coverage and no complete bibliography is claimed.
- Three unverified MultitaskProtDB-II reference anomalies (rows `multitaskprotdb_ii_row_239/349/422`) remain raw; they are not PMIDs/DOIs.
- No verified article-to-GO relations exist; GO and reference text is verbatim source data.
- MultifacetedProtDB and MultitaskProtDB-II provide no source evidence status; their `operational_status=unresolved` is a neutral administrative value, not a scientific label.

## Data layers

`raw → interim → processed → release`

- `data/raw/`: immutable source artifacts (never manually edited)
- `data/interim/`: reproducible intermediate outputs
- `data/curated/`: schemas and normalized record definitions
- `data/processed/`: rebuilt catalog outputs (ignored by Git; rebuilt locally)
- `releases/`: immutable packaged candidates and release documentation

Note: `.gitignore` ignores `data/*`; only files tracked before that rule remain in Git. Which inputs are in Git, and which are not, is enumerated in [docs/getting-started.md](docs/getting-started.md).

## Core principles

- Raw source data is immutable.
- Provenance is mandatory for all derived records.
- Scientific label, evidence tier, and benchmark role are separate concepts.
- `benchmark_role` exists for downstream compatibility only; records remain `unassigned` unless a separately approved benchmark protocol assigns a role.
- Transformations must be script-based and reproducible.

Architecture and data flow: [docs/architecture/data-flow.md](docs/architecture/data-flow.md). Release rules: [docs/release-policy.md](docs/release-policy.md). Surgical maintenance: [docs/maintenance/technical-maintenance-guide.md](docs/maintenance/technical-maintenance-guide.md).

## Licensing boundaries (pre-release)

- Repository-owned code and documentation remain in pre-release status and are currently marked as all rights reserved pending a final repository license decision.
- Third-party source datasets are governed by their own source-specific licensing and redistribution terms, which remain `to_be_verified`.
- This repository does not currently claim redistribution permission for any third-party source dataset.

## Repository status caveat

At the time of writing, the packaged candidate and the verifier script are working-tree files not yet committed. `git archive HEAD` therefore does not include them, and offline verification has not been demonstrated in a literal clean clone of this repository. The offline command was tested in an extraction containing tracked plus untracked (non-ignored) files — the state a clean clone will have once these files are committed.
