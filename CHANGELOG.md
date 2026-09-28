# Changelog

## [Unreleased]

### Fixed
- MoonProt known-absent and unresolved MPIDs (103, 542, 543, 626) are now coverage-only status rows and no longer materialize as source records or protein entities (ADR-006).

### Changed
- MVP catalog counts after the correction: 1,165 source records (MoonProt 702), 1,073 protein entities, 45 exact UniProt merges, `fallback_identity_records = 0`.

## [v0.1.0-source-freeze] - Unreleased

### Added
- Initial repository scaffold for governance, source cataloging, schema definition, validation scripts, and offline tests.

### Clarified
- Python package version remains `0.1.0` (PEP 440), while `v0.1.0-source-freeze` is the repository release milestone label.
