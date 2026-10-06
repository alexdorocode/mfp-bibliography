# Changelog

## [Unreleased]

### Changed
- Repository license clarified: project-authored code and documentation are
  AGPL-3.0-only (`LICENSE`, `NOTICE`); third-party data and derived outputs
  are NOT relicensed — their terms remain recorded as `terms_not_recorded`,
  which is not a redistribution grant.

### Added
- Five-source catalog candidate `mfp-catalog-candidate-v0.3.0` under
  `releases/` — documentation-only correction of source-status semantics
  (policy-mapped `source_status` vs verbatim `raw_claim_value`; MoonProt
  `valid` as loader-generated technical status; no cross-source evidence
  scale). All five catalog CSVs are byte-identical to v0.2.0; counts, input
  hashes and catalog contract `MFPB_0_19_MFP_CATALOG_MVP_V2` unchanged.
  v0.2.0 remains immutable and offline-verifiable
  (`--verify-package --candidate-id mfp-catalog-candidate-v0.2.0`).
- Five-source catalog candidate `mfp-catalog-candidate-v0.2.0` under `releases/` (catalog contract `MFPB_0_19_MFP_CATALOG_MVP_V2`, protein ID scheme `MFPB_PROTEIN_ID_V1`). Measured counts are defined by the candidate manifest, `releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json` (key `measured_counts`): five sources (MoonDB, MoonProt, MultifacetedProtDB, MultitaskProtDB-II, PlantMP); 2,962 source records; 2,322 protein entities; 463 cross-source shared accessions; MoonProt coverage 702 acquired / 1 known absent / 3 unresolved. Status: CANDIDATE — not a tagged or published release; see `docs/releases/mfp-catalog-candidate-v0.2.0.md`.
- Offline `PACKAGE_VERIFY` mode for the packaged candidate (`scripts/package_catalog_candidate.py --verify-package`), checks inventory, hashes, row counts, primary and foreign keys against the candidate manifest without rebuilt outputs; tests in `tests/test_candidate_package_verify.py`. The pre-existing `--verify` mode is `REBUILD_COMPARE` and requires a locally rebuilt catalog.

## [Three-source MVP catalog milestone] - date not recorded; superseded by the five-source candidate above

Three-source MVP catalog (MoonDB, MoonProt, PlantMP), before MultifacetedProtDB and MultitaskProtDB-II ingestion.

### Fixed
- MoonProt known-absent and unresolved MPIDs (103, 542, 543, 626) are now coverage-only status rows and no longer materialize as source records or protein entities (ADR-006).

### Changed
- MVP catalog counts after that correction: 1,165 source records (MoonProt 702), 1,073 protein entities, 45 exact UniProt merges, `fallback_identity_records = 0`. Historical values; superseded by the five-source candidate counts in the [Unreleased] section.

## [v0.1.0-source-freeze] - Unreleased

### Added
- Initial repository scaffold for governance, source cataloging, schema definition, validation scripts, and offline tests.

### Clarified
- Python package version remains `0.1.0` (PEP 440), while `v0.1.0-source-freeze` is the repository release milestone label.
