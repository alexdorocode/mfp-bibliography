# mfp-bibliography

Multifunctional Protein Bibliography and Evidence Registry.

This repository prioritizes traceability and reproducibility.

## Scope

This repository preserves, documents, versions, and harmonizes public source datasets and bibliographic evidence related to multifunctional / moonlighting proteins (MF/MFP).

It is a **bibliographic and provenance catalog**, currently materialized as the five-source candidate [`releases/mfp-catalog-candidate-v0.3.0/`](releases/mfp-catalog-candidate-v0.3.0/) (CANDIDATE — not the final v1 release).

It is **not**:

- an MF-vs-NMF dataset, classifier, ML benchmark, or negative set;
- a completed GO–article evidence graph: no verified article-to-GO relations exist in the candidate; all GO/reference text is raw, uninterpreted source data (laboratory GO integration is a planned future phase, see the [roadmap](docs/roadmap/mfp-catalog-implementation-plan.md));
- an ML/modeling repository, embedding pipeline, web app, API, or large-scale scraping workflow.

Python package version: `0.1.0` (PEP 440 compliant). Current repository milestone: the five-source catalog candidate `mfp-catalog-candidate-v0.3.0` (supersedes v0.2.0, which remains immutable and offline-verifiable).

## Start here: the candidate

New to the data? Read [docs/getting-started.md](docs/getting-started.md), then open the candidate directory: [`releases/mfp-catalog-candidate-v0.3.0/`](releases/mfp-catalog-candidate-v0.3.0/).

- **Primary table — [`mfp_proteins.csv`](releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv)**: one row per protein entity (one per normalized UniProt accession).
- The other packaged tables provide interpretation and provenance for those proteins:
  - `mfp_source_records.csv`: one row per source observation, with verbatim source labels and full raw-data provenance;
  - `mfp_identifiers.csv`: identifier claims per source record;
  - `mfp_assertions.csv`: administrative assertions (no invented evidence);
  - `mfp_coverage.csv`: MoonProt snapshot coverage-only statuses (never protein entities).
- Column meanings and table grains: [DATA_DICTIONARY.md](releases/mfp-catalog-candidate-v0.3.0/DATA_DICTIONARY.md).

Cross-source merging is only by exact normalized UniProt accession equality; absence from a source is never negative evidence.

## Included sources (five)

Measured counts are defined by the candidate manifest — [`releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json`](releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json) (`measured_counts`) — not by this README or any historical note. As packaged in v0.3.0 (identical to v0.2.0 for all catalog tables): 2,962 source records, 2,322 protein entities, 463 shared-accession merges.

| Source | Source records (v0.3.0 manifest) | Documentation |
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

## Known limitations (candidate v0.3.0)

Full statement: [candidate README](releases/mfp-catalog-candidate-v0.3.0/README.md) and [release notes](docs/releases/mfp-catalog-candidate-v0.3.0.md).

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

## Documentation and Specifications

- **Technical Architecture** ([`docs/architecture/`](docs/architecture/README.md)):
  - [Scientific Background](docs/architecture/scientific-background.md): explanatory reference on epistemic decoupling, evidence layers, and open-world GO limits.
  - [Data Flow](docs/architecture/data-flow.md): accepted technical architecture for candidate catalog assembly.
  - [Requirements Traceability](docs/architecture/requirements-traceability.md): matrix tracing catalog invariants (R1–R12) to code.
  - [GO Metrics Specification](docs/architecture/go-metrics-specification.md): recovered proposed analytical design for semantic dissimilarity.
- **Evidence Curation** ([`docs/curation/`](docs/curation/README.md)):
  - [Literature Curation Manual](docs/curation/literature-curation-manual.md): proposed procedure pending approval for primary literature adjudication.
  - [PTRH2 Case Dossier](docs/curation/Q9Y3E5_contextual_adjudication_dossier.md): reference contextual review profile.
- **Research Proposals & Planning**:
  - [Experimental Master Proposal](docs/roadmap/core/experimental-master-proposal.md): Maintained English research proposal — under review; not an implemented pipeline or approved experimental policy.
  - [Catalog Implementation Plan](docs/roadmap/mfp-catalog-implementation-plan.md): approved baseline roadmap for candidate catalog releases.
- **Governance & Operations**:
  - [Release Policy](docs/release-policy.md) | [Source Claims Contract](docs/source-claims-contract.md) | [Maintenance Guide](docs/maintenance/technical-maintenance-guide.md)

## Licensing

- Project-authored code and documentation: **GNU AGPL v3.0 only** (SPDX `AGPL-3.0-only`) — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
- AGPL does **not** apply to third-party source datasets, raw files, copied tables or derived outputs whose source terms are unknown: they retain their applicable upstream terms, recorded as `terms_not_recorded`, which is not a grant of redistribution permission.
- This repository does not claim redistribution permission for any third-party source dataset. Attribution and provenance are preserved (see [NOTICE](NOTICE) and `data/manifests/source_manifest.csv`).
