# Technical Audit Report: Comprehensive Documentation Architecture, Repository Drift, and Evidence-Based English Migration Plan

## Document Control

| Attribute | Audit Record |
|---|---|
| **Document Title** | Technical Audit Report: Comprehensive Documentation Architecture, Repository Drift, and Evidence-Based English Migration Plan |
| **Audit Execution Date** | 2026-11-09 |
| **Auditor Role** | Senior Scientific-Software Auditor & Documentation Architect |
| **Target Repository** | `mfp-bibliography` (`/home/alexdoro/repositories/mfp-bibliography`) |
| **Current Branch** | `feature/functional-normalization` (tracking `origin/feature/functional-normalization`) |
| **Base Commit SHA** | `a6def6fef01f345f38532d30779d5b576b079580` (`Add functional tests for MultitaskProtDB-II claims and coverage schemas`) |
| **Commit Timestamp** | `2026-11-06 20:04:28 +0100` |
| **Author** | alexdorocode <alexdoro2024@gmail.com> |
| **Working Tree State** | Dirty working tree with 9 tracked modifications and 5 untracked files; preserved without alteration |
| **Production Language** | English (per repository policy and user request) |
| **Operational Boundaries** | Read-only static inspection; zero modifications to existing project files; single authorized write: this audit report |

---

## 1. Executive Diagnosis and Exact Audit Baseline

### 1.1 Executive Diagnosis
The `mfp-bibliography` repository demonstrates a pronounced **two-tier reality** across its software implementation and documentation corpus:

1. **A Highly Rigorous, Provenance-Preserving Catalog Foundation**:
   The core five-source catalog pipeline (`MoonDB`, `MoonProt`, `MultifacetedProtDB`, `MultitaskProtDB-II`, `PlantMP`) is exceptionally well-engineered, immutable, and byte-reproducible. The packaged candidate release at `releases/mfp-catalog-candidate-v0.3.0/` unifies 2,962 source records, 2,322 protein entities, and 463 cross-source shared accessions under deterministic SHA-256 digests (`MFPB_PROTEIN_ID_V1`, [ADR-005](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-005-deterministic-protein-ids.md)). Offline cryptographic package verification (`scripts/package_catalog_candidate.py --verify-package`) executes cleanly without external network access, live database connections, or uncommitted files.
2. **Deep Documentation Drift and Unapproved Scope Expansion in Research Roadmaps**:
   A sharp bifurcation exists between the catalog documentation (largely English, grounded in ADR-001 through ADR-007) and an extensive body of unapproved research dossiers and presentation materials (over 7,500 lines across 13 Spanish files in `docs/roadmap/01-07` and `docs/roadmap/core/`, plus 4 Catalan files). These unapproved proposals detail complex downstream research—including semantic similarity metrics (Wang, Lin, MBL), functional divergence calculations, inter-aspect association matrices, and direct PostgreSQL queries against `BioData` and `TargetData`—even though [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) explicitly descoped external bibliographic relations and Gene Ontology (GO) enrichment from the repository's initial catalog baseline.
3. **Active Course Correction via Specification-Driven Development (SDD)**:
   The working branch `feature/functional-normalization` previously contained a fragile, unapproved heuristic 2-facet model (`src/mfp_bibliography/functional_normalization.py`, `scripts/build_protein_facets.py`, `targetdata_client.py`) that used ad-hoc regex matching (e.g. `nucleus` $	o$ `GO:0005634`), hardcoded external filesystem paths (`/home/alexdoro/.../go-basic.obo`), and unmocked database credentials. However, between commit `a6def6f` and the current working-tree state, the repository successfully initiated an SDD course correction under proposed [ADR-008](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-008-functional-normalization-pilot-scope.md) and [`specs/functional-normalization-pilot/`](file:///home/alexdoro/repositories/mfp-bibliography/specs/functional-normalization-pilot/). Scoped authorization for TASK-01 (schemas), TASK-02 (executable contract tests), and TASK-03 (offline MultitaskProtDB-II vertical slice) has been implemented and verified (98 passing contract tests), leaving subsequent tasks strictly unauthorized.
4. **Maintenance Deficits in Active First-Party Documentation**:
   Despite the strength of the catalog architecture, the active documentation suffers from concrete maintenance defects:
   - **5 broken relative markdown links** resulting from deleted bibliographic contract documents and broken snapshot dump links.
   - **Stale working-tree caveats** in [README.md](file:///home/alexdoro/repositories/mfp-bibliography/README.md) and [docs/getting-started.md](file:///home/alexdoro/repositories/mfp-bibliography/docs/getting-started.md) claiming the packaged candidate and verifier script are uncommitted files (they have been tracked in Git for weeks).
   - **Mismatched candidate version references** where markdown link text says `v0.2.0` while target paths point to `v0.3.0`, or where obsolete candidate paths are referenced in active study plans and release contract drafts.
   - **Internal contradictions** in source profiles and implementation roadmaps where sources are described simultaneously as "integrated" and "not implemented / raw data only".
   - **Script index omissions** in [scripts/README.md](file:///home/alexdoro/repositories/mfp-bibliography/scripts/README.md), which omits the six descriptive analysis scripts (`analyze_question1.py` through `analyze_question6.py`) and new SDD pilot scripts.
   - **Linguistic fragmentation**, including an isolated Catalan sentence in the primary English [README.md](file:///home/alexdoro/repositories/mfp-bibliography/README.md) and extensive untranslated Spanish dossiers.
   - **File duplication and mojibake corruption**, specifically `docs/roadmap/core/experiment_guio_v1.md`, which is an 874-line corrupted copy of `docs/roadmap/core/experiment_definition.md` with broken UTF-8 encoding.

### 1.2 Exact Audit Baseline

| Parameter | Value | Verification Command / Evidence |
|---|---|---|
| **Repository Root** | `/home/alexdoro/repositories/mfp-bibliography` | `git rev-parse --show-toplevel` |
| **Repository Name** | `mfp-bibliography` | `basename $(git rev-parse --show-toplevel)` |
| **Current Branch** | `feature/functional-normalization` | `git branch --show-current` (tracks `origin/feature/functional-normalization`) |
| **HEAD Commit SHA** | `a6def6fef01f345f38532d30779d5b576b079580` | `git rev-parse HEAD` |
| **HEAD Date** | `2026-11-06 20:04:28 +0100` | `git log -1 --format="%ci"` |
| **Audit Date** | `2026-11-09` | Current inspection execution date |
| **Package Name** | `mfp-bibliography` | `pyproject.toml` line 6 |
| **Package Version** | `0.1.0` (PEP 440 compliant) | `pyproject.toml` line 7 |
| **Declared Python Version** | `>=3.11` | `pyproject.toml` line 11 |
| **Runtime Dependencies** | `jsonschema>=4.22.0` | `pyproject.toml` lines 12-14 |
| **Development Extras** | `pytest>=8.2.0`, `pyyaml>=6.0` | `pyproject.toml` lines 16-20 |
| **Build Backend** | `setuptools.build_meta` (setuptools >=68, wheel) | `pyproject.toml` lines 1-3 |
| **Console Entrypoints** | None declared in `pyproject.toml` | Execution relies on standalone `scripts/*.py` |
| **CI Workflow** | `.github/workflows/ci.yml` | Push & PR triggers on Ubuntu-latest, Python 3.11: `pip install -e .[dev]`, `pytest`, `python scripts/validate_repository.py` |

### 1.3 Working Tree Status: Committed vs Local Modifications
A rigorous comparison between committed Git HEAD artifacts and the local working tree was conducted:

#### Tracked Modifications (9 files)
- `specs/functional-normalization-pilot/plan.md`: Updated Stage P2 MultitaskProtDB-II slice execution status.
- `specs/functional-normalization-pilot/spec.md`: Refined dimensional analysis, schema nullability rules, and 6-level epistemological distinctions.
- `specs/functional-normalization-pilot/tasks.md`: Recorded completion of TASK-01, TASK-02, and TASK-03; retained strict unauthorization for TASK-04 through TASK-08.
- `specs/functional-normalization-pilot/verification.md`: Logged passing checks DOC-CHK-01 to DOC-CHK-06 and verified contract test outcomes.
- `src/mfp_bibliography/functional_claims_multitask.py`: Core adapter logic implementing extraction, parsing of GO terms/aspects/evidence, reference classification, and total ordering.
- `tests/fixtures/functional_claims_multitask/README.md`: Fixture documentation for real and synthetic Multitask extracts.
- `tests/fixtures/functional_claims_multitask/multitask_real_extract.csv`: 6-row real extract slice from raw `proteins.csv`.
- `tests/fixtures/functional_claims_multitask/multitask_synthetic_edge_cases.csv`: Edge-case synthetic fixture for testing malformed and boundary inputs.
- `tests/test_functional_claims_multitask.py`: Unit and regression test suite for MultitaskProtDB-II slice adapter.

#### Untracked Working-Tree Files (5 files)
- `data/curated/source_go_annotations.schema.json`: Formal JSON Schema (Draft 2020-12) for extracted per-source Gene Ontology annotations.
- `docs/reports/multitask-six-record-context-readiness-review.md`: Scientific review report (`REV-MULTITASK-6REC-001`) evaluating the 6-record MultitaskProtDB-II pilot package against parent raw data.
- `scripts/build_multitask_slice.py`: Standalone CLI script executing Stage P2 extraction for the 6-record MultitaskProtDB-II slice.
- `tests/test_build_multitask_slice.py`: Integration test verifying execution of `scripts/build_multitask_slice.py`.
- `tests/test_source_go_annotations_contract.py`: Executable contract test suite (43 tests) validating schema compliance and total ordering for `source_go_annotations`.

#### Committed Baseline Artifacts (Stable Evidence)
All packaged catalog releases (`releases/mfp-catalog-candidate-v0.3.0/` and `releases/mfp-catalog-candidate-v0.2.0/`), raw data files (`data/raw/`), manifest files (`data/manifests/`), interim source claims (`data/interim/`), core schemas (`data/curated/`), and descriptive analysis outputs (`analysis/five-source-v0.2.0/`) are committed in Git history and verifiable offline.

---

## 2. Current Repository Capabilities, Development Stage, and Verification Limits

### 2.1 Reconstructed Pipeline and Component Responsibilities
The actual data processing and verification pipeline operating within `mfp-bibliography` was reconstructed through static inspection of source modules, scripts, and build manifests:

```
[1. Controlled Acquisition (Manual / Network)]
  scripts/acquire_moonprot_smoke.py / acquire_moonprot_batch.py
    └─> mfp_bibliography/moonprot_client.py (HTTP Transport)
          └─> data/raw/moonprot/mpid_*.html (702 pages) + artifact_index.csv
  (MoonDB, MultifacetedProtDB, MultitaskProtDB-II, PlantMP are static local raw files)

[2. Pre-Build Gates & Input Verification (Offline)]
  scripts/build_mfp_catalog_mvp.py
    ├─> mfp_bibliography/raw_input_verification.py::verify_catalog_inputs
    │     └─> Validates consumed raw artifacts against data/manifests/source_manifest.csv
    └─> validate_moonprot_universe (bounds check MPIDs 1..706)

[3. Source Normalization & Interim Claims/Records (Offline)]
  scripts/build_source_claims_moondb.py       --> data/interim/source_claims_moondb.csv (351 rows)
  scripts/build_source_claims_plantmp.py      --> data/interim/source_claims_plantmp.csv (112 rows)
  scripts/build_source_records_multifaceted.. --> data/interim/source_records_multifacetedprotdb.csv (1,103 rows)
  scripts/build_source_records_multitask..    --> data/interim/source_records_multitaskprotdb_ii.csv (694 rows)
  moonprot_parser.py (inline parse)           --> parsed MoonProt HTML records (702 rows)

[4. Deterministic Identity Resolution & Catalog Assembly (Offline)]
  scripts/build_mfp_catalog_mvp.py (Contract: MFPB_0_19_MFP_CATALOG_MVP_V2)
    ├─> mfp_bibliography/normalization.py (MFPB_PROTEIN_ID_V1 deterministic SHA-256 digests)
    ├─> Resolves canonical UniProt accessions: exact-equality merging only
    ├─> Generates coverage-only status rows for MPIDs 103, 542, 543, 626 (ADR-006)
    ├─> Pre-write gate: validate_catalog_integrity (PK, FK, and conservation checks)
    └─> Emits data/processed/mfp_catalog_mvp/ tables + summary.json

[5. Candidate Packaging & Offline Verification (Offline)]
  scripts/package_catalog_candidate.py
    ├─> Generates releases/mfp-catalog-candidate-v0.3.0/ (5 CSV tables, MANIFEST.json, checksums.sha256)
    └─> PACKAGE_VERIFY: offline check of inventory, hashes, row counts, PK/FK referential integrity

[6. Five-Source Descriptive Study (Offline)]
  scripts/analyze_question1.py ... analyze_question6.py
    └─> Emits deterministic aggregate CSVs, escaped SVGs, and analysis_manifest.json to analysis/five-source-v0.2.0/

[7. Active SDD Functional Normalization Pilot (Offline / In-Progress)]
  scripts/build_multitask_slice.py (Stage P2 vertical slice)
    └─> Emits data/interim/pilot/multitask_slice/ (claims.csv, source_go_annotations.csv, coverage.csv)
```

### 2.2 Distinctions Across Development Stages

#### 1. Current Behavior Supported by Inspected Code
- Ingestion of five distinct biological datasets preserving raw locators, original values, and whole-file or per-record SHA-256 hashes.
- Deterministic accession-to-protein mapping generating stable 16-character hexadecimal IDs prefixed with `MFP:U:` (or fallback `MFP:F:<source>:`).
- Segregation of MoonProt administrative non-proteins (known-absent MPID 103, unresolved MPIDs 542, 543, 626) into `mfp_coverage.csv` so they never enter `mfp_proteins.csv`.
- Offline packaging and cryptographic verification guaranteeing byte-reproducibility across clean repository checkouts.
- Standard-library generation of descriptive metric figures (SVG) and summary tables for catalog coverage, source overlap, sources per protein, MoonProt status distribution, source label inventory, and field completeness.
- Tier A functional claims and structured Gene Ontology annotation extraction for the MultitaskProtDB-II vertical slice.

#### 2. Behavior Supported by Executed Tests vs Historical Records
- **Executed Checks (During this Audit)**:
  * `PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package`: **PASSED** (Candidate `v0.3.0` verified).
  * `PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package --candidate-id mfp-catalog-candidate-v0.2.0`: **PASSED** (Immutable historical candidate `v0.2.0` verified).
  * `PYTHONPATH=src python scripts/validate_repository.py`: **PASSED** (All 9 repository structure, manifest, and schema checks passed).
  * `tests/test_candidate_package_verify.py`: **8 passed in 0.61s** (Offline package verifier test suite passed).
  * `tests/test_functional_contracts.py`, `tests/test_functional_claims_multitask.py`, `tests/test_source_go_annotations_contract.py`: **98 passed in 0.36s** (Functional normalization contract and slice adapter test suite passed).
  * `tests/test_functional_normalization.py`: **11 passed in 0.16s** (Unit tests for existing normalization utilities passed).
- **Historical Records / Full Suite Caveat**:
  * The full test suite collects **543 tests**.
  * Complete end-to-end execution of `pytest` across all 35 test files requires uncommitted local data artifacts that are explicitly ignored by `.gitignore` (specifically the 702 raw MoonProt HTML pages in `data/raw/moonprot/`, interim files in `data/interim/`, and processed outputs in `data/processed/mfp_catalog_mvp/`). Therefore, while package verification (`PACKAGE_VERIFY`) passes in a clean clone, running the complete historical test suite requires external or cached data artifacts.

#### 3. Approved Requirements Not Yet Implemented
- **Phase E Formal Release (`mfp_catalog_v1`)**: Documented in [`docs/releases/mfp-catalog-v1-contract-draft.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/releases/mfp-catalog-v1-contract-draft.md). Awaiting final resolution of third-party raw data license terms (`terms_not_recorded` in manifest) and packaging of a formal validation report.
- **Automated Whole-Manifest Sweep**: Requirements Traceability row R11 records that while consumed inputs are verified at build time, a complete repository-wide check against `data/manifests/file_checksums.sha256` is not yet automated into CI.

#### 4. Proposed Future Work (Unimplemented Proposals)
- **ADR-008 Stages P3–P4 (Functional Normalization Expansion)**: Expanding functional claims extraction to PlantMP (TASK-04), MoonProt (TASK-05), MoonDB and MultifacetedProtDB (TASK-06), followed by the integrated pilot CLI (TASK-07) and interim reporting (TASK-08). Status: `Proposed` / `Unauthorized`.
- **Phase D0 / D (Bibliographic Evidence Graph)**: Sourced relations linking proteins, functional assertions, Gene Ontology terms, and primary literature citations (PMID/DOI) with assertion-level provenance. Formally descoped from `mfp_catalog_v1` per [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) and deferred to post-v1.
- **Downstream Characterization Proposals**: Spanish dossiers (`docs/roadmap/01-07`) and `experiment-guio-v2.md` proposals for Wang/Lin/MBL semantic distance calculations, inter-aspect co-occurrence matrices, and triplet context adjudication.

#### 5. Superseded Decisions and Unknowns
- **Superseded Release Candidate**: `mfp-catalog-candidate-v0.2.0` is superseded by `v0.3.0` due to imprecise source-status terminology in its data dictionary. (The 5 CSV tables are byte-identical).
- **Superseded Metric Output**: `analysis/five-source-v0.2.0/q5_status_labels/` (v1) is superseded by `q5_status_labels_v2/` (which groups by verbatim `raw_claim_value` rather than policy status).
- **Superseded Heuristic Normalization**: The 2-facet model in `src/mfp_bibliography/functional_normalization.py` and `scripts/build_protein_facets.py` is superseded by the relational SDD model in `specs/functional-normalization-pilot/`.
- **Unknowns**:
  * Upstream retrieval date of the raw MultifacetedProtDB JSON artifact remains unknown.
  * Formal license terms for third-party raw datasets remain classified as `terms_not_recorded`.
  * Profile completeness review for MultitaskProtDB-II remains pending against the raw artifact.

---

## 3. Complete Documentation Inventory and Coverage Totals

### 3.1 Inventory Scope and Exclusions
The inventory encompasses every first-party and third-party document across the repository.

#### Explicit Exclusions (Recorded per Boundary Rules)
1. **Version Control Internals**: `.git/` directory and Git object databases.
2. **Environment & Dependency Trees**: Virtual environments (`.venv/`), site-packages, and system binaries.
3. **Build & Python Caches**: `src/mfp_bibliography.egg-info/`, `__pycache__/`, `.pytest_cache/`.
4. **Large Data Bodies & Raw Artifacts**:
   - Immutable raw data files under `data/raw/` (`all_emf_and_curated.tsv`, `PlantMP_all.csv`, `MultifacetedProtDB_data.json`, `proteins.csv`, and the 702 HTML files in `data/raw/moonprot/`).
   - Packaged catalog CSV tables under `releases/` (`mfp_proteins.csv`, `mfp_source_records.csv`, `mfp_identifiers.csv`, `mfp_assertions.csv`, `mfp_coverage.csv`).
   - Fixture CSV/TSV/HTML files under `data/fixtures/` and `tests/fixtures/`.
   - Raw database dumps (`data/snapshots/biodata_mfp_snapshot_20261014.dump` — not tracked).

### 3.2 Inventory Summary Totals
- **Total In-Scope Text/Markdown Documents Reviewed**: **98**
  - English First-Party Documents: **80**
  - Spanish Proposal/Roadmap Documents: **13**
  - Catalan Audit/Proposal Documents: **4**
  - Mixed Language Documents: **1**
- **Documentation Assets (Binary Reference Materials)**: **22**
  - Literature Reference PDFs (`docs/bibliography/*.pdf`): **20**
  - Presentation Proposal Assets (`docs/roadmap/core/presentation/*.pdf`, `*.pptx`): **2**
- **Machine-Readable Formal Contracts & Schemas**: **13**
  - JSON Schemas in `data/curated/` & `data/interim/`: **7**
  - Manifests & Checksum Files in `data/manifests/` & `releases/`: **5**
  - YAML Policy Configurations in `configs/`: **1**

### 3.3 Complete Document Classification Matrix (98 Documents)

The table below lists all 98 discovered documents classified according to the required 8 dimensions:
`path | purpose/role | language | accuracy status | reuse value | evidence/confidence | proposed action | destination/canonical owner`
| Path | Purpose / Role | Language | Accuracy Status | Reuse Value | Evidence & Confidence | Proposed Action | Destination / Canonical Owner |
|---|---|---|---|---|---|---|---|
| `.github/workflows/ci.yml` | operational guide | en | **CURRENT** | HIGH: Active CI configuration executing pytest and repository validation | Verified passing in GitHub Actions and local environment; runs pytest and validate_repository.py | Retain; add package verification step if desired | .github/workflows/ |
| `AGENTS.md` | operational guide | en | **CURRENT** | HIGH: Authoritative operational guidance, authority hierarchy, and scientific invariants for coding agents | Commit a6def6f; grounded in ADR-001 through ADR-007; consulted by user prompt rules | Retain as canonical operational governance document | Repository root / Maintainers |
| `CHANGELOG.md` | historical record | en | **PARTIALLY_CURRENT** | MEDIUM: Records unreleased changes, but omits release candidates v0.2.0, v0.3.0, and baseline v0.1 | Lines 1-39 contain only [Unreleased] section; violates release policy checklist requiring candidate tracking | Update to document candidate release milestones v0.2.0 and v0.3.0 | Repository root / Release Maintainer |
| `CITATION.cff` | operational guide | en | **CURRENT** | HIGH: Standard machine-readable citation metadata | Matches pyproject.toml version 0.1.0 and charter milestone v0.1.0-source-freeze | Retain; update version when v1 is published | Repository root / Scientific Lead |
| `CONTRIBUTING.md` | operational guide | en | **CURRENT** | HIGH: Core contributor principles (immutability, provenance, script-based transformations) | Aligns with ADR-002, ADR-003, and ADR-004 | Retain; add explicit reference to AGENTS.md SDD workflow | Repository root / Maintainers |
| `LICENSE` | legal reference | en | **CURRENT** | HIGH: Legal terms for project-authored code and documentation (AGPL-3.0-only) | Aligns with pyproject.toml, NOTICE, and ADR-001 | Retain immutable legal license text | Repository root / Maintainers |
| `NOTICE` | legal reference | en | **CURRENT** | HIGH: Classifies third-party data as terms_not_recorded, strictly excluded from AGPL grant | Aligns with source_manifest.csv and project licensing boundaries | Retain; update when upstream terms are clarified | Repository root / Maintainers |
| `README.md` | operational guide | en (mixed) | **PARTIALLY_CURRENT** | HIGH: Primary entry point for human readers and new contributors | Line 5 contains isolated Catalan sentence; lines 23 and 37 link text says v0.2.0 but target is v0.3.0; line 64 links to v0.2.0 notes; lines 99-101 contain obsolete caveat that candidate is uncommitted | Batch 1 edit: translate line 5 to English; fix link text to v0.3.0; remove obsolete clone caveat | Repository root / Maintainers |
| `SECURITY.md` | operational guide | en | **CURRENT** | MEDIUM: Standard vulnerability reporting protocol | States repo contains scaffolding and governance; no secrets expected | Retain | Repository root / Maintainers |
| `analysis/five-source-v0.2.0/q1_records_vs_entities/README.md` | generated output | en | **CURRENT** | HIGH: Analytical documentation for Q1 candidate metrics (records vs entities) | Generated by src/mfp_bibliography/analysis_q1.py; checksums recorded in analysis_manifest.json | Retain; trace to generator script; do not manually edit | src/mfp_bibliography/analysis_q1.py |
| `analysis/five-source-v0.2.0/q2_source_overlap/README.md` | generated output | en | **CURRENT** | HIGH: Analytical documentation for Q2 candidate metrics (exclusive and pairwise overlap) | Generated by src/mfp_bibliography/analysis_q2.py; verified against candidate MANIFEST.json | Retain; trace to generator script; do not manually edit | src/mfp_bibliography/analysis_q2.py |
| `analysis/five-source-v0.2.0/q3_sources_per_protein/README.md` | generated output | en | **CURRENT** | HIGH: Analytical documentation for Q3 candidate metrics (sources per entity) | Generated by src/mfp_bibliography/analysis_q3.py; verified against candidate MANIFEST.json | Retain; trace to generator script; do not manually edit | src/mfp_bibliography/analysis_q3.py |
| `analysis/five-source-v0.2.0/q4_moonprot_coverage/README.md` | generated output | en | **CURRENT** | HIGH: Analytical documentation for Q4 candidate metrics (MoonProt snapshot coverage) | Generated by src/mfp_bibliography/analysis_q4.py; verified against mfp_coverage.csv | Retain; trace to generator script; do not manually edit | src/mfp_bibliography/analysis_q4.py |
| `analysis/five-source-v0.2.0/q5_status_labels/README.md` | generated output | en | **SUPERSEDED** | MEDIUM: Historical Q5 v1 output; superseded by q5_status_labels_v2 | Superseded by q5_status_labels_v2, which corrects provenance by grouping verbatim raw_claim_value | Retain byte-unchanged as historical analytical record; label as superseded | src/mfp_bibliography/analysis_q5.py |
| `analysis/five-source-v0.2.0/q5_status_labels_v2/README.md` | generated output | en | **CURRENT** | HIGH: Authoritative Q5 v2 documentation of source-provided status labels | Generated by src/mfp_bibliography/analysis_q5.py; verified against candidate source records | Retain; trace to generator script; do not manually edit | src/mfp_bibliography/analysis_q5.py |
| `analysis/five-source-v0.2.0/q6_canonical_completeness/README.md` | generated output | en | **CURRENT** | HIGH: Analytical documentation for Q6 candidate metrics (canonical field completeness) | Generated by src/mfp_bibliography/analysis_q6.py; verified against candidate mfp_proteins.csv | Retain; trace to generator script; do not manually edit | src/mfp_bibliography/analysis_q6.py |
| `data/curated/README.md` | implemented-system reference | en | **OUTDATED** | HIGH: Location of repository-level formal JSON Schemas | Only 3 lines; completely omits documentation for the 6 JSON Schemas residing in data/curated/ | Expand to document each schema, its draft version, purpose, and validation command | Data Architect / Maintainers |
| `data/fixtures/README.md` | implemented-system reference | en | **CURRENT** | MEDIUM: Explains role of offline test fixtures | Matches data/fixtures/ contents used by unit tests | Retain | Test Maintainer |
| `data/interim/README.md` | implemented-system reference | en | **CURRENT** | MEDIUM: Explains role of interim reproducible data directory | Matches data/interim/ contents (claims, reports, pilot slices) | Retain; add directory inventory table | Data Architect |
| `data/interim/reports/effective_status_moondb_plantmp_report.md` | generated output | en | **CURRENT** | MEDIUM: Markdown summary of MoonDB/PlantMP effective status aggregation | Generated by scripts/generate_effective_status_moondb_plantmp.py | Retain as reproducible interim output | scripts/generate_effective_status_moondb_plantmp.py |
| `data/interim/reports/mfp_catalog_mvp_protein_id_migration_v1.notes.md` | historical record | en | **CURRENT** | MEDIUM: Explains protein ID hash migration and retirement of MPID 103 entity | Cites ADR-005 and ADR-006; matches migration CSV data | Retain as historical migration record | docs/decisions/ADR-005-deterministic-protein-ids.md |
| `data/interim/reports/moondb_plantmp_overlap_audit.md` | generated output | en | **CURRENT** | MEDIUM: Markdown summary of MoonDB/PlantMP overlap audit | Generated by scripts/audit_moondb_plantmp_overlap.py | Retain as reproducible interim output | scripts/audit_moondb_plantmp_overlap.py |
| `data/manifests/README.md` | implemented-system reference | en | **CURRENT** | MEDIUM: Explains role of source artifact manifests and checksums | Matches data/manifests/ contents (source_manifest.csv, file_checksums.sha256) | Retain; document column definitions | Data Architect |
| `data/processed/mfp_catalog_mvp/README.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | HIGH: Documents local MVP catalog build contract, tables, and gaps | Lines 11-13 contain hardcoded absolute paths (/home/alexdoro/...); line 6 Scope omits Multifaceted and Multitask; lines 85-86 discuss old hash() | Batch 2 edit: replace absolute paths with repo-relative paths; update Scope to list all 5 sources | scripts/build_mfp_catalog_mvp.py |
| `data/raw/README.md` | operational guide | en | **CURRENT** | HIGH: Documents raw data immutability policy and .gitignore tracking rules | Matches ADR-002 and .gitignore behavior | Retain | Data Architect |
| `docs/acquisition-protocols/README.md` | operational guide | en | **CURRENT** | MEDIUM: Introduces source acquisition protocols | Only MoonProt requires acquisition protocol in current baseline | Retain | Data Architect |
| `docs/acquisition-protocols/moonprot-artifact-index.md` | approved specification | en | **PARTIALLY_CURRENT** | HIGH: Data contract for data/raw/moonprot/artifact_index.csv | Line 3 states 'No index data exists yet... created only by a future run'; however, artifact_index.csv exists with 702 entries | Update status note to reflect that artifact_index.csv exists and covers MPIDs 1..706 | Data Architect |
| `docs/acquisition-protocols/moonprot-contact-decision-log.md` | operational guide | en | **PARTIALLY_CURRENT** | MEDIUM: Tracking log for maintainer contact and acquisition approval | Snapshot was acquired on 2026-09-24, but decision log still shows initial draft state | Record actual acquisition execution parameters and date | Data Architect / Maintainers |
| `docs/acquisition-protocols/moonprot-maintainer-contact-draft.md` | operational guide | en | **HISTORICAL_RECORD** | LOW: Draft text for maintainer communication | Represents outreach text prepared for MoonProt maintainers | Retain in acquisition-protocols/ as historical reference | Maintainers |
| `docs/acquisition-protocols/moonprot.md` | operational guide | en | **PARTIALLY_CURRENT** | HIGH: Primary acquisition protocol for MoonProt web endpoints | States bulk acquisition is blocked and real acquisition for MPIDs 4-706 is a future task, whereas all 702 HTML files exist locally | Update to clarify that 1..706 snapshot acquisition was completed on 2026-09-24 and is now frozen under ADR-002 | Data Architect |
| `docs/analysis/five-source-descriptive-study-plan.md` | approved specification | en | **PARTIALLY_CURRENT** | HIGH: Design document for Q1-Q6 catalog coverage and overlap study | Line 9 link text says v0.3.0/ but target is ../../releases/mfp-catalog-candidate-v0.2.0/ | Batch 1 edit: update markdown link target to v0.3.0 | Scientific Lead |
| `docs/architecture/data-flow.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | HIGH: Architectural map of acquisition, offline transformation, and catalog build | Line 53 broken link to deleted go-annotation-evidence-contract.md; table at line 25 omits MultitaskProtDB-II step | Batch 1/2 edit: remove broken link; add MultitaskProtDB-II row to pipeline table | System Architect |
| `docs/architecture/requirements-traceability.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | HIGH: Traceability matrix mapping requirements R1-R21 to code, tests, and evidence | Line 7 cites v0.2.0 MANIFEST; rows R14-R17 cite deleted go-annotation-evidence-contract.md | Batch 1/2 edit: update candidate reference to v0.3.0; update R14-R17 contract references to ADR-007 / Phase D0 | System Architect |
| `docs/audits/2026-11-06_repository-sdd-functional-normalization-audit.md` | historical record | en (mixed) | **CURRENT** | HIGH: Authoritative audit diagnosing 2-facet model flaws, unapproved roadmap, and SDD course correction | Base commit 9729c3c; provided blueprint for AGENTS.md, ADR-008, and SDD pilot | Retain as immutable Level 6 historical audit report | System Auditor |
| `docs/audits/MFP_DATA_AUDITABILITY_MATRIX.md` | historical record | ca | **CURRENT** | HIGH: Critical audit establishing loss of NOT qualifiers in QuickGO and BioData constraints | Valid historical analysis; cited in AGENTS.md and Nov 6 audit | Retain as immutable historical audit; provide English summary in recovery map | System Auditor |
| `docs/audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md` | historical record | ca | **CURRENT** | HIGH: Unification audit diagnosing phantom dependencies on CBBIO.GO and QuickGO gaps | Essential evidence justifying descope of external GO relations in ADR-007 | Retain as immutable historical audit; provide English summary in recovery map | System Auditor |
| `docs/curation/Q9Y3E5_contextual_adjudication_dossier.md` | implemented-system reference | en | **CURRENT** | HIGH: Rigorous manual evidence curation dossier for human PTRH2 / Bit1 (Q9Y3E5) | Dated 2026-11-09; cites PMIDs 15342468, 11481330; strictly separates raw statements from literature adjudication | Retain in docs/curation/ as canonical evidence dossier model for pilot Stage P2 | docs/curation/ / Scientific Evidence Curator |
| `docs/canonical-schema.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | MEDIUM: Preliminary canonical source record schema | Line contains malformed markdown link [Z|±HH:MM](Z|±HH:MM); schema superseded in practice by Draft 2020-12 JSON Schema | Batch 1 edit: repair malformed link; add header referencing data/curated/mfp_source_records.schema.json | Data Architect |
| `docs/data-governance.md` | operational guide | en | **CURRENT** | HIGH: Governance roles (Importer, Reviewer, Release maintainer) and non-rewrite correction rules | Level 2 authority in AGENTS.md hierarchy | Retain as canonical governance policy | Repository Maintainers |
| `docs/decisions/ADR-001-repository-scope.md` | approved specification | en | **CURRENT** | HIGH: Establishes repo scope: source-evidence/cataloging, not ML modeling or negative sets | Accepted ADR; Level 1 authority; cited in charter and AGENTS.md | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-002-raw-data-immutability.md` | approved specification | en | **CURRENT** | HIGH: Establishes raw data immutability: append-only, zero in-place edits | Accepted ADR; Level 1 authority; enforced by raw_input_verification.py | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-003-provenance-and-transformations.md` | approved specification | en | **CURRENT** | HIGH: Requires source locators, transformation IDs, and checksums for all derived records | Accepted ADR; Level 1 authority; enforced by build_mfp_catalog_mvp.py | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-004-evidence-label-benchmark-separation.md` | approved specification | en | **CURRENT** | HIGH: Forbids conflation of scientific label, evidence tier, and benchmark role | Accepted ADR; Level 1 authority; enforced by source_claims.py | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-005-deterministic-protein-ids.md` | approved specification | en | **CURRENT** | HIGH: Mandates deterministic SHA-256 protein IDs under MFPB_PROTEIN_ID_V1 | Accepted ADR; Level 1 authority; eliminates salted hash() collisions | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-006-coverage-only-moonprot-status-rows.md` | approved specification | en | **CURRENT** | HIGH: Mandates that known-absent and unresolved MPIDs are coverage-only, not entities | Accepted ADR; Level 1 authority; verified in mfp_coverage.csv | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md` | approved specification | en | **CURRENT** | HIGH: Formally descopes external bibliographic relations and GO enrichment from catalog v1 | Accepted ADR; Level 1 authority; decouples v1 release from Phase D0/D | Retain immutable architectural decision record | Repository Maintainers |
| `docs/decisions/ADR-008-functional-normalization-pilot-scope.md` | proposal/roadmap | en | **CURRENT** | HIGH: Bounded scope extension for source-grounded functional normalization pilot (Stages P0-P4) | Proposed ADR (Level 6 awaiting Level 2 approval); cited in specs/functional-normalization-pilot/ | Retain; track through human decision gate | Repository Maintainers / Architects |
| `docs/effective-status-contract.md` | approved specification | en | **CURRENT** | HIGH: Specification for cross-source effective status aggregation (MFPB_0_13) | Implemented in src/mfp_bibliography/effective_status.py; tested in test_effective_status.py | Retain as active contract | Data Architect |
| `docs/experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md` | proposal/roadmap | ca | **OUTDATED** | MEDIUM: October 2026 Catalan roadmap detailing BioData PostgreSQL dump and goatools metrics | Proposes live Docker pg_dump, which is prohibited by AGENTS.md; superseded by ADR-007 and candidate v0.3.0 | Archive in docs/archive/ with English status banner linking to ADR-007 and mfp-catalog-implementation-plan.md | Scientific Lead |
| `docs/getting-started.md` | operational guide | en | **PARTIALLY_CURRENT** | HIGH: Primary user onboarding guide (inspect -> verify -> tests -> rebuild) | Lines 124-131 contain obsolete caveat that candidate is an uncommitted working-tree file | Batch 1 edit: remove obsolete clone caveat; verify all internal links | Repository Maintainers |
| `docs/maintenance/biodata-snapshot-and-restore-guide.md` | operational guide | en | **PARTIALLY_CURRENT** | MEDIUM: Operational guide for restoring BioData PostgreSQL snapshot | Line 15 broken link to non-existent data/snapshots/biodata_mfp_snapshot_20261014.dump | Batch 1 edit: fix link; clarify that the 4.8 MB .dump file is external and not tracked in Git | Database Administrator / Maintainers |
| `docs/maintenance/technical-maintenance-guide.md` | operational guide | en | **PARTIALLY_CURRENT** | HIGH: Surgical maintenance guide for adapters, policies, and catalog builds | Lines 46 and 101 contain broken links to deleted go-annotation-evidence-contract.md | Batch 1 edit: replace broken links with reference to ADR-007 and Phase D0 | System Architect |
| `docs/project-charter.md` | operational guide | en | **CURRENT** | HIGH: Project mission, scope boundaries, and first release definition | Level 2 authority in AGENTS.md; cited in README.md | Retain as canonical charter | Repository Maintainers |
| `docs/reconciliation-baseline-contract.md` | approved specification | en | **CURRENT** | HIGH: Baseline reconciliation contract (MFPB_0_16) for pre-MoonProt baseline | Implemented and tested; governs reconciliation comparisons | Retain as active contract | Data Architect |
| `docs/release-policy.md` | operational guide | en | **CURRENT** | HIGH: Defines package versioning (PEP 440) vs repository milestone labels (v0.1.0-source-freeze, v0.3.0) | Level 2 authority in AGENTS.md; matches pyproject.toml and candidate metadata | Retain as canonical release policy | Release Maintainer |
| `docs/releases/mfp-catalog-candidate-v0.2.0.md` | historical record | en | **CURRENT** | HIGH: Release notes for candidate v0.2.0; documents source-status erratum | Cites MANIFEST.json and explains why v0.3.0 was created to fix documentation | Retain immutable historical release notes | Release Maintainer |
| `docs/releases/mfp-catalog-candidate-v0.3.0.md` | implemented-system reference | en | **CURRENT** | HIGH: Authoritative release notes for active candidate v0.3.0 | Matches releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json and checksums.sha256 | Retain as active candidate release notes | Release Maintainer |
| `docs/releases/mfp-catalog-v1-contract-draft.md` | proposal/roadmap | en | **PARTIALLY_CURRENT** | HIGH: Draft release contract for upcoming mfp_catalog_v1 release | Line 27 points to v0.2.0 MANIFEST instead of v0.3.0; lists 8 release gates | Batch 1 edit: update manifest link to v0.3.0; retain as active draft | Release Maintainer |
| `docs/releases/pre-moonprot-baseline-v0.1.md` | historical record | en | **CURRENT** | HIGH: Checksum-pinned release notes for pre-MoonProt baseline v0.1 | Cites contract MFPB_0_16; historical milestone record | Retain immutable historical release notes | Release Maintainer |
| `docs/reports/moondb_plantmp_effective_status_snapshot.md` | historical record | en | **CURRENT** | MEDIUM: Technical report on MoonDB/PlantMP effective status snapshot | Matches interim claims and reports; verified data snapshot | Retain | Data Architect |
| `docs/reports/moonprot_smoke_test_report.md` | historical record | en | **CURRENT** | MEDIUM: Technical report on MoonProt MPIDs 1-3 smoke acquisition | Verifies initial smoke run on 2026-09-22; accurate for that snapshot | Retain as historical record | Data Architect |
| `docs/reports/multitask-six-record-context-readiness-review.md` | implemented-system reference | en | **CURRENT** | HIGH: Scientific review (REV-MULTITASK-6REC-001) evaluating 6-record Multitask slice against raw source | Untracked file in working tree; provides evidence for TASK-03 consolidation | Commit as part of SDD pilot documentation | Scientific Data Reviewer |
| `docs/roadmap/01_dossier_experimento.md` | proposal/roadmap | es | **OUTDATED** | HIGH: Comprehensive Spanish experimental dossier (functional characterization & positive corpus audit) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; assumes live BioData/TargetData queries | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner; preserve methodology in recovery map | Scientific Lead |
| `docs/roadmap/02_protocolo_cientifico_y_analisis.md` | proposal/roadmap | es | **OUTDATED** | HIGH: Spanish scientific protocol (EEC vs ALL evidence codes, statistical contrasts, hypothesis tests) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; details valuable biological rationale | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner; preserve methodology in recovery map | Scientific Lead |
| `docs/roadmap/03_contrato_datos_y_recursos.md` | proposal/roadmap | es | **OUTDATED** | HIGH: Spanish data contract proposal (distinguishes raw statements, claims, and external GO evidence) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; informs SDD epistemological levels | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner; preserve methodology in recovery map | Scientific Lead |
| `docs/roadmap/04_especificacion_metricas.md` | proposal/roadmap | es | **OUTDATED** | HIGH: Spanish GO metrics specification (Wang graph-based, Lin information-theoretic, MBL measures) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; rigorous mathematical definitions | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner; preserve methodology in recovery map | Scientific Lead |
| `docs/roadmap/04a_asociaciones_interaspecto.md` | proposal/roadmap | es | **OUTDATED** | HIGH: Spanish annex on inter-aspect GO associations (MF-MF, MF-CC co-occurrence matrices) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; establishes non-conflation of MF and CC | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner; preserve methodology in recovery map | Scientific Lead |
| `docs/roadmap/05_diseno_tecnico.md` | proposal/roadmap | es | **OUTDATED** | MEDIUM: Spanish technical architecture proposal (relational schemas, caching, execution blocks) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; assumes PostgreSQL infrastructure | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner | Scientific Lead |
| `docs/roadmap/06_manual_revision_bibliografica.md` | proposal/roadmap | es | **OUTDATED** | HIGH: Spanish literature review manual (protocols for manual adjudication of moonlighting claims) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; valuable curation guidelines | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner; extract English summary for Phase D0 | Scientific Lead |
| `docs/roadmap/07_plan_implementacion_y_validacion.md` | proposal/roadmap | es | **OUTDATED** | MEDIUM: Spanish implementation schedule and task assignments (20 tasks, stages 1-5) | Draft v0.1 (2026-10-26); unapproved Level 6 proposal; superseded by SDD pilot plan | Archive in docs/archive/proposals-2026-10-spanish/ with English status banner | Scientific Lead |
| `docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md` | proposal/roadmap | ca | **SUPERSEDED** | MEDIUM: Catalan research plan detailing 6 research questions and comparison with BioData | Incorporated verbatim into experiment-guio-v2.md as Annex 2 | Archive in docs/archive/proposals-2026-10-core/ with English status banner | Scientific Lead |
| `docs/roadmap/core/experiment-guio-v2.md` | proposal/roadmap | ca (mixed) | **PROPOSED** | HIGH: Master experimental guide PEC-EXP-001 v0.2.1 (2,147 lines, blocks B0-B6, 29 open decisions) | Estat: Proposta de revisió; no aprovada per a execució completa; awaiting Gate G0 sign-off | Retain in docs/roadmap/core/ as primary active research proposal; add English header banner; separate embedded annexes | Scientific Lead |
| `docs/roadmap/core/experiment_definition.md` | proposal/roadmap | es | **SUPERSEDED** | MEDIUM: Clean Spanish master proposal PEC-EXP-001 v0.1.0 (874 lines) | Clean UTF-8 predecessor to experiment-guio-v2.md; superseded by v0.2.1 | Archive in docs/archive/proposals-2026-10-core/ with English status banner | Scientific Lead |
| `docs/roadmap/core/experiment_guio_v1.md` | proposal/roadmap | es (corrupted) | **SUPERSEDED** | NONE: Mojibake-corrupted duplicate of experiment_definition.md | Contains broken UTF-8 encoding (â€”, terminologÃ­a, diseÃ±o); identical content to experiment_definition.md | Quarantine or delete to prevent accidental propagation of corrupted text | Scientific Lead |
| `docs/roadmap/core/guion_propuesta.md` | proposal/roadmap | es | **HISTORICAL_RECORD** | MEDIUM: 15-slide presentation storyboard (v0.4, 28 Oct 2026) for research defense | Presentation script corresponding to propuesta_investigacion.pptx and .pdf | Move to docs/roadmap/core/presentation/ alongside presentation slides; add English status banner | Scientific Lead |
| `docs/roadmap/core/presentation/decisiones_abiertas.md` | proposal/roadmap | es | **HISTORICAL_RECORD** | LOW: 40-line summary of open decisions for presentation rehearsal | Superseded by formal decision register DEC-01..DEC-29 in experiment-guio-v2.md | Retain in presentation/ directory with status note | Scientific Lead |
| `docs/roadmap/mfp-catalog-implementation-plan.md` | approved specification | en | **PARTIALLY_CURRENT** | HIGH: Level 4 implementation roadmap tracking catalog milestones and rules | Line 37 lists all 5 sources as included, but line 39 contradicts this by stating Multifaceted and Multitask are raw data only; line 96 broken link | Batch 1/2 edit: remove contradictory line 39; fix broken link to ADR-007 / Phase D0; align with v0.3.0 | Repository Maintainers |
| `docs/source-catalog.md` | implemented-system reference | en | **OUTDATED** | HIGH: Authoritative source registry and metadata catalog | Lists MoonProt as smoke_tested (MPIDs 1-3 only) rather than 702 acquired records; lists Multifaceted artifact as TXT rather than JSON | Batch 2 edit: update source statuses, counts, and canonical artifact paths to reflect 5-source reality | Data Architect |
| `docs/source-claim-policy.md` | approved specification | en | **CURRENT** | HIGH: Declarative policy (MFPB_0_7) mapping source labels to repository statuses | Matches configs/source_claim_policy_v0.1.yaml; tested in test_source_claim_policy.py | Retain as active policy specification | Data Architect |
| `docs/source-claims-contract.md` | approved specification | en | **CURRENT** | HIGH: Data contract (MFPB_0_8) defining normalized per-source claim model | Matches data/curated/source_claims.schema.json | Retain as active contract | Data Architect |
| `docs/source-policy.md` | operational guide | en | **CURRENT** | HIGH: Eight fundamental source rules (raw immutability, provenance, claim separation) | Level 2 authority in AGENTS.md; cited across all source profiles | Retain as canonical source policy | Repository Maintainers |
| `docs/source-profiles/moondb.md` | implemented-system reference | en | **CURRENT** | HIGH: Authoritative source profile for MoonDB (all_emf_and_curated.tsv, 351 records) | Matches raw artifact and interim claims; verified counts and hashes | Retain as canonical source profile | Data Architect |
| `docs/source-profiles/multifacetedprotdb.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | HIGH: Authoritative source profile for MultifacetedProtDB (JSON artifact, 1,103 records) | Contains contradictory headings: 'Proposed ingestion contract (not implemented)' at line 45 vs 'Adapter status (integrated into the catalog)' at line 59 | Batch 2 edit: harmonize sections by marking proposal as completed and removing 'not implemented' banner | Data Architect |
| `docs/source-profiles/multitaskprotdb-ii.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | HIGH: Authoritative source profile for MultitaskProtDB-II (proteins.csv, 694 records) | Contains contradictory headings: 'Ingestion contract (proposed; NOT implemented)' at line 139 vs 'Adapter status (integrated into the catalog)' at line 151 | Batch 2 edit: harmonize sections by marking proposal as completed and removing 'not implemented' banner | Data Architect |
| `docs/source-profiles/plantmp.md` | implemented-system reference | en | **CURRENT** | HIGH: Authoritative source profile for PlantMP (PlantMP_all.csv, 112 records) | Matches raw artifact and interim claims; verified counts and hashes | Retain as canonical source profile | Data Architect |
| `releases/README.md` | operational guide | en | **CURRENT** | HIGH: Instructions for offline candidate package verification vs rebuild-compare | Accurately references v0.3.0 and package_catalog_candidate.py --verify-package | Retain as active release directory guide | Release Maintainer |
| `releases/mfp-catalog-candidate-v0.2.0/DATA_DICTIONARY.md` | historical record | en | **SUPERSEDED** | HIGH: Data dictionary for historical candidate v0.2.0 (contains source-status erratum) | Immutable release artifact; passes --verify-package --candidate-id mfp-catalog-candidate-v0.2.0 | Retain byte-unchanged per ADR-002 immutability rules | Release Maintainer |
| `releases/mfp-catalog-candidate-v0.2.0/README.md` | historical record | en | **SUPERSEDED** | HIGH: Release README for historical candidate v0.2.0 | Immutable release artifact; superseded by v0.3.0 | Retain byte-unchanged per ADR-002 immutability rules | Release Maintainer |
| `releases/mfp-catalog-candidate-v0.3.0/DATA_DICTIONARY.md` | implemented-system reference | en | **CURRENT** | HIGH: Authoritative data dictionary for active five-source candidate v0.3.0 | Corrects source-status semantics; verified against candidate CSV tables | Retain as authoritative data dictionary for v0.3.0 | Release Maintainer |
| `releases/mfp-catalog-candidate-v0.3.0/README.md` | implemented-system reference | en | **CURRENT** | HIGH: Authoritative release README for active five-source candidate v0.3.0 | Passes --verify-package; defines measured counts (2,962 records, 2,322 entities, 463 merges) | Retain as authoritative candidate overview | Release Maintainer |
| `scripts/README.md` | operational guide | en | **PARTIALLY_CURRENT** | HIGH: Script navigation table documenting purposes, inputs, and outputs | Line 19 lists candidate output as v0.2.0; omits analyze_question1.py through analyze_question6.py, build_protein_facets.py, and build_multitask_slice.py | Batch 2 edit: update candidate to v0.3.0; add entries for analysis scripts, multitask slice, and flag facets script as unapproved | Tooling Maintainer |
| `specs/functional-normalization-pilot/plan.md` | approved specification | en | **CURRENT** | HIGH: SDD Implementation Plan for Functional Normalization Pilot (Stages P0-P4) | Active SDD plan on feature/functional-normalization; Stage P2 complete | Retain as active feature plan | Scientific Software Architect |
| `specs/functional-normalization-pilot/spec.md` | approved specification | en | **CURRENT** | HIGH: SDD Functional Specification for source-grounded claims extraction and coverage | Establishes 6 epistemological levels, 3-axis analysis, and total ordering rules | Retain as active feature specification | Scientific Software Architect |
| `specs/functional-normalization-pilot/tasks.md` | approved specification | en | **CURRENT** | HIGH: Sequenced task list for pilot; records completion of TASK-01..03 and unauthorization of TASK-04..08 | Strictly enforces write boundaries; audited in VERIF-001 | Retain as active task tracking document | Scientific Software Architect |
| `specs/functional-normalization-pilot/verification.md` | approved specification | en | **CURRENT** | HIGH: Automated verification log for SDD pilot checks (DOC-CHK-01..06, tests) | Records passing checks and test results for TASK-01..03 | Retain as active verification record | Scientific Software Architect |
| `tests/fixtures/README.md` | implemented-system reference | en | **CURRENT** | MEDIUM: Documents offline unit test fixtures | Matches tests/fixtures/ contents | Retain | Test Maintainer |
| `tests/fixtures/functional_claims_multitask/README.md` | implemented-system reference | en | **PARTIALLY_CURRENT** | HIGH: Documents MultitaskProtDB-II test fixtures and row extraction locators | Line 7 cites data/raw/source_manifest.csv (should be data/manifests/source_manifest.csv) | Batch 1 edit: correct manifest path to data/manifests/source_manifest.csv | Data Architect |
| `tests/fixtures/functional_contracts/README.md` | implemented-system reference | en | **CURRENT** | HIGH: Documents synthetic fixtures and explicitly disclaims biological reality | Guarantees synthetic nature of test data (P00001, MFP:U:0123...) | Retain | Data Architect |

---

## 4. Evidence-Backed Drift, Conflicts, Duplication, and Missing Guidance

### 4.1 Broken Internal Links
A comprehensive relative path resolution scan across all 98 documents revealed **5 broken internal links**:

1. **`docs/canonical-schema.md` (Table row `last_updated_at`)**:
   - **Broken Target**: `[Z|±HH:MM](Z|±HH:MM)`
   - **Diagnosis**: Malformed markdown syntax representing an ISO 8601 timezone pattern rather than an actual file link.
   - **Correction**: Replace with code span `` `Z|±HH:MM` ``.
2. **`docs/maintenance/biodata-snapshot-and-restore-guide.md` (Line 15)**:
   - **Broken Target**: `[`data/snapshots/biodata_mfp_snapshot_20261014.dump`](../../data/snapshots/biodata_mfp_snapshot_20261014.dump)`
   - **Diagnosis**: The target directory `data/snapshots/` does not exist in the repository; the 4.8 MB PostgreSQL custom dump file was never tracked in Git. However, its manifest is tracked at `releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json`.
   - **Correction**: Update text to explicitly declare that the `.dump` file is an external artifact, remove the broken link, and reference the tracked manifest.
3. **`docs/maintenance/technical-maintenance-guide.md` (Line 46 & Line 101)**:
   - **Broken Target**: `[`GO annotation contract`](../bibliography/go-annotation-evidence-contract.md)`
   - **Diagnosis**: The file `docs/bibliography/go-annotation-evidence-contract.md` was deleted in commit `a6def6f` when bibliographic relations were descoped from the catalog baseline per [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md).
   - **Correction**: Replace link with reference to [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) and roadmap Phase D0.
4. **`docs/roadmap/mfp-catalog-implementation-plan.md` (Line 96)**:
   - **Broken Target**: `[`GO annotation, evidence-code and bibliography contract`](../bibliography/go-annotation-evidence-contract.md)`
   - **Diagnosis**: Same root cause as above (file deleted in commit `a6def6f`).
   - **Correction**: Replace link with reference to [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) and Phase D0.

### 4.2 Obsolete Working-Tree and Clone Status Caveats
Both `README.md` and `docs/getting-started.md` contain identical stale caveats that contradict the actual Git state:

- **`README.md` (Lines 99–101)**:
  > *"At the time of writing, the packaged candidate and the verifier script are working-tree files not yet committed. `git archive HEAD` therefore does not include them, and offline verification has not been demonstrated in a literal clean clone of this repository..."*
- **`docs/getting-started.md` (Lines 124–131)**:
  > *"The packaged candidate and the verifier script were working-tree files not yet committed at the time of writing. `git archive HEAD` therefore omits them..."*
- **Concrete Evidence**: Both `releases/mfp-catalog-candidate-v0.3.0/` and `scripts/package_catalog_candidate.py` were committed in Git weeks ago (`git ls-files` tracks them completely). Offline verification passes cleanly in any fresh clone. These caveats represent historical drafting notes that should have been deleted upon commit.

### 4.3 Mismatched Candidate Version References
Documentation drift exists where text and links still point to superseded candidate `v0.2.0` instead of current candidate `v0.3.0`:

| File | Exact Location | Stale Text / Target | Correct Target / Action |
|---|---|---|---|
| `README.md` | Line 23 | `[releases/mfp-catalog-candidate-v0.2.0/](releases/mfp-catalog-candidate-v0.3.0/)` | Align link text to `releases/mfp-catalog-candidate-v0.3.0/` |
| `README.md` | Line 37 | `[releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json](releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)` | Align link text to `releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json` |
| `README.md` | Line 39 | `Source records (v0.2.0 manifest)` | Update text to `Source records (v0.3.0 manifest)` |
| `README.md` | Line 64 | `[release notes](docs/releases/mfp-catalog-candidate-v0.2.0.md)` | Update link to `docs/releases/mfp-catalog-candidate-v0.3.0.md` |
| `docs/analysis/five-source-descriptive-study-plan.md` | Line 9 | `[`releases/mfp-catalog-candidate-v0.3.0/`](../../releases/mfp-catalog-candidate-v0.2.0/)` | Update link target to `../../releases/mfp-catalog-candidate-v0.3.0/` |
| `docs/releases/mfp-catalog-v1-contract-draft.md` | Line 27 | `[`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json)` | Update link target to `../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json` |
| `docs/architecture/requirements-traceability.md` | Line 7 | `releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json` | Update citation to `releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json` |
| `scripts/README.md` | Line 19 | Table row outputs to `releases/mfp-catalog-candidate-v0.2.0/` | Update output path to `releases/mfp-catalog-candidate-v0.3.0/` |

### 4.4 Internal Contradictions in Implementation Plans and Source Profiles
1. **Contradiction in Implementation Plan (`docs/roadmap/mfp-catalog-implementation-plan.md`)**:
   - **Line 37**: Declares that the catalog includes `MultifacetedProtDB 1,103` and `MultitaskProtDB-II 694`.
   - **Lines 54–75**: Marks Phase B (MultifacetedProtDB) and Phase C (MultitaskProtDB-II) as **completed** under contracts `MFPB_0_18` and `MFPB_0_19`.
   - **Line 39**: In the very same snapshot section, asserts: `"[MultifacetedProtDB] and [MultitaskProtDB-II]: raw data only, not ingested."`
   - **Resolution**: Line 39 is a stale residue from the earlier MVP baseline and must be deleted.
2. **Contradiction in MultifacetedProtDB Profile (`docs/source-profiles/multifacetedprotdb.md`)**:
   - **Line 45**: Heading reads `## Proposed ingestion contract (not implemented)`.
   - **Line 59**: Heading reads `## Adapter status (integrated into the catalog, contract MFPB_0_18_MFP_CATALOG_MVP_V1)`.
   - **Resolution**: Retitle Section 45 as `## Ingestion Contract Design` and update status to completed.
3. **Contradiction in MultitaskProtDB-II Profile (`docs/source-profiles/multitaskprotdb-ii.md`)**:
   - **Line 139**: Heading reads `### Ingestion contract (proposed; NOT implemented — fifth source NOT integrated)`.
   - **Line 151**: Heading reads `### Adapter status (integrated into the catalog, contract MFPB_0_19_MFP_CATALOG_MVP_V2)`.
   - **Resolution**: Harmonize headings by removing the "NOT implemented" statement.
4. **Outdated Source Catalog Registry (`docs/source-catalog.md`)**:
   - **MoonProt**: Listed as `source_status: smoke_tested` and `Dataset availability: smoke_sample_only` (MPIDs 1-3), ignoring the 702 acquired records present in `data/raw/moonprot/`.
   - **MultifacetedProtDB**: Artifact listed as `data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt` (SHA `23a68fe6...`), whereas canonical ingestion uses the JSON artifact `MultifacetedProtDB_data.json` (SHA `94bc65de...`).

### 4.5 Incomplete Indices and Undocumented Schemas
- **`scripts/README.md`**: Fails to document 8 existing scripts:
  * `analyze_question1.py` through `analyze_question6.py` (the 6 descriptive study CLIs).
  * `build_protein_facets.py` (the unapproved 2-facet script).
  * `build_multitask_slice.py` (the newly developed Stage P2 vertical slice script).
- **`data/curated/README.md`**: Consists of only 3 lines and completely fails to document the repository's 6 formal JSON schemas:
  * `mfp_source_records.schema.json`
  * `source_claims.schema.json`
  * `effective_status.schema.json`
  * `functional_claims.schema.json`
  * `functional_coverage.schema.json`
  * `source_go_annotations.schema.json`
- **`tests/fixtures/functional_claims_multitask/README.md`**: Line 7 contains an erroneous path: `Registered in data/raw/source_manifest.csv` (the file is actually at `data/manifests/source_manifest.csv`).

### 4.6 File Duplication and Encoding Corruption
- **`docs/roadmap/core/experiment_guio_v1.md`**:
  An 874-line file that is an exact duplicate of `docs/roadmap/core/experiment_definition.md` but was saved with corrupted UTF-8 mojibake encoding:
  * Em-dashes corrupted: `â€”` instead of `—`
  * Spanish accents corrupted: `terminologÃ­a` instead of `terminología`, `diseÃ±o` instead of `diseño`
  * This corrupted text was then copied verbatim into Annex 1 of `experiment-guio-v2.md`.
- **`docs/roadmap/core/experiment-guio-v2.md` Annex Bloat**:
  This 2,147-line document embeds `experiment_guio_v1.md` (874 lines) and `Pla de recerca` (349 lines) as massive appendices, inflating the document and creating duplicate maintenance burdens.

---

## 5. Recovery Map for Reusable Outdated Material

Historical proposals and Spanish dossiers contain significant scientific reasoning, literature curation protocols, and mathematical formalizations that should be preserved. They must not be deleted blindly. The recovery map below establishes how to extract and preserve valid methodology while discarding obsolete assumptions:

| Source Document & Section | Content Worth Preserving | Obsolete Assumptions to Discard | Necessary Correction / Validation | Target Canonical Document | Prerequisite Gate |
|---|---|---|---|---|---|
| `docs/roadmap/01_dossier_experimento.md` (§3–§6) | Scientific justification for decoupling sequence homology from functional divergence; annotation lag characterization | Direct queries to live `BioData` PostgreSQL database; assuming BioData is a negative class | Frame BioData as an external reference population; decouple analysis from live DB | `docs/architecture/scientific-background.md` (or downstream repo) | Gate G0 Approval |
| `docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§4–§8) | Rigorous biological distinction between Experimental Evidence Codes (EEC: EXP, IDA, IPI, IMP, IGI, IEP) vs ALL annotations | Assuming co-annotation of MF and CC constitutes contextual localization without literature proof | Formalize rule forbidding Cartesian product synthesis $	au = (m, b, c)$ | `specs/functional-normalization-pilot/spec.md` (§1.2) | Accepted in SDD Spec |
| `docs/roadmap/03_contrato_datos_y_recursos.md` (§2–§5) | Epistemological separation: raw statement $
e$ normalized claim $
e$ external GO annotation | Fixed 2-facet model (`BP1/MF1/CC1` vs `BP2/MF2/CC2`) | Replace rigid 2-facet model with multi-claim relational model (`functional_claims`) | `specs/functional-normalization-pilot/spec.md` | Completed in TASK-01 |
| `docs/roadmap/04_especificacion_metricas.md` (§3–§12) | Exact mathematical definitions of Wang (graph topology), Lin (information content), and MBL semantic distances | Combining disparate metric scales into a composite multifunctionality index | Enforce metric isolation; evaluate metrics independently without composite scores | Future metric specification (downstream repo or Phase F) | Post-v1 Decision |
| `docs/roadmap/04a_asociaciones_interaspecto.md` (All) | Mathematical formulation of inter-aspect associations (MF-MF, MF-CC) via co-occurrence matrices | Assuming low co-occurrence proves moonlighting behavior | Retain as an exploratory descriptive metric only; not evidence of multifunctionality | Downstream analytical package | Post-v1 Decision |
| `docs/roadmap/06_manual_revision_bibliografica.md` (§2–§7) | Exhaustive curation protocol for primary literature review: identifying experimental assays, resolving conflicting claims | Assuming automated scripts can replace human literature adjudication | Retain as the gold-standard protocol for manual evidence curation (Phase D0) | `docs/curation/literature-curation-manual.md` | Human Review Gate |
| `docs/roadmap/core/experiment-guio-v2.md` (§Marc científic & DEC-01..29) | Consolidated decision register (DEC-01 to DEC-29); formal definitions of experimental blocks B0–B6 | Assuming G0 gate approval; assuming automated triplet extraction from raw abstracts | Retain as active comprehensive research proposal; separate massive annexes into archive | `docs/roadmap/core/experiment-guio-v2.md` | Gate G0 Approval |
| `docs/audits/MFP_DATA_AUDITABILITY_MATRIX.md` | Critical finding: total loss of `NOT` qualifiers during QuickGO parsing and BioData ingestion | None (historical audit findings remain fully valid) | English executive summary highlighting the risk of negative assertions in QuickGO | `docs/audits/README.md` (summary index) | Documentation-only |
| `docs/audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md` | Diagnosis of phantom dependency on `CBBIO.GO` and missing columns in legacy extraction schemas | None (historical audit findings remain fully valid) | English executive summary explaining rationale for ADR-007 descope | `docs/audits/README.md` (summary index) | Documentation-only |
| Deleted `docs/bibliography/go-annotation-evidence-contract.md` | Controlled vocabulary for GO evidence codes, reference scopes, and attribution metadata | Immediate implementation in v1 catalog (descoped per ADR-007) | Recover schema concepts for future Phase D0 contract when authorized | `docs/contracts/phase-d0-annotation-contract.md` | Phase D0 Authorization |

---

## 6. Minimal Canonical Documentation and Navigation Proposal

To eliminate duplication, prevent drift, and establish maintainable boundaries, the repository documentation should be organized into a single canonical hierarchy where every topic has exactly one authoritative owner:

```
mfp-bibliography/
├── README.md                               <-- Primary repo entry point: scope, v0.3.0 candidate, offline verify
├── AGENTS.md                                <-- Agent governance, authority hierarchy, SDD workflow, rules
├── CONTRIBUTING.md                          <-- Principles: immutability, provenance, script-based changes
├── LICENSE & NOTICE                         <-- AGPL-3.0-only for code/docs; terms_not_recorded for 3P data
├── CHANGELOG.md                             <-- Versioned release history (v0.1, v0.2.0, v0.3.0, unreleased)
│
├── configs/
│   └── source_claim_policy_v0.1.yaml        <-- Canonical policy mapping raw source labels to operational statuses
│
├── data/
│   ├── manifests/                           <-- Checksums and raw source manifests (source_manifest.csv)
│   └── curated/
│       ├── README.md                        <-- Canonical schema dictionary documenting all 6 JSON Schemas
│       ├── mfp_source_records.schema.json   <-- Core catalog source records schema
│       ├── source_claims.schema.json        <-- Normalized per-source claims schema
│       ├── effective_status.schema.json     <-- Derived effective status schema
│       ├── functional_claims.schema.json    <-- Pilot functional claims schema
│       ├── functional_coverage.schema.json  <-- Pilot functional coverage schema
│       └── source_go_annotations.schema.json<-- Pilot source-grounded GO annotations schema
│
├── docs/
│   ├── getting-started.md                   <-- New user onboarding (Inspect -> Verify -> Test -> Rebuild)
│   ├── project-charter.md                   <-- Mission, scope boundaries, and first release definition
│   ├── data-governance.md                   <-- Governance roles and non-rewrite correction rules
│   ├── release-policy.md                    <-- Package versioning (PEP 440) vs milestone labels
│   ├── source-policy.md                     <-- 8 immutable source rules
│   ├── source-catalog.md                    <-- Authoritative source registry (updated to 5 sources)
│   ├── architecture/
│   │   ├── data-flow.md                     <-- Pipeline map (acquisition -> gates -> adapters -> build)
│   │   └── requirements-traceability.md     <-- Technical satisfaction of requirements R1-R21
│   ├── decisions/                           <-- Accepted Architectural Decision Records (ADR-001..007; ADR-008 proposed)
│   ├── source-profiles/                     <-- One profile per source: moondb, moonprot, multifaceted, multitask, plantmp
│   ├── acquisition-protocols/               <-- Controlled web acquisition protocols (moonprot.md)
│   ├── releases/                            <-- Release notes (v0.1 baseline, v0.2.0, v0.3.0 candidate, v1 draft)
│   ├── maintenance/                         <-- Surgical maintenance guide and external snapshot instructions
│   ├── audits/                              <-- Immutable technical and data audit reports (English & historical Catalan)
│   ├── specs/                               <-- Active SDD feature specifications (specs/functional-normalization-pilot/)
│   └── archive/                             <-- Formal archive for unapproved historical proposals
│       ├── README.md                        <-- English index explaining status of archived research proposals
│       ├── proposals-2026-10-spanish/       <-- Dossiers 01-07 and technical proposals (retained with header banners)
│       └── proposals-2026-10-core/          <-- Legacy Catalan research plan and clean Spanish experiment_definition
│
└── releases/
    └── mfp-catalog-candidate-v0.3.0/        <-- Active packaged candidate (5 CSVs, MANIFEST.json, checksums.sha256)
```

---

## 7. Prioritized Action Matrix

The recommended remediation measures are categorized using four decoupled dimensions:
- **Priority**: **P0** (blocking / misleading guidance), **P1** (required for next milestone), **P2** (consolidation / debt reduction), **P3** (optional polish).
- **Feasibility**: **F3** (ready now, documentation-only), **F2** (feasible after bounded verification), **F1** (requires human decision gate), **F0** (unjustified).
- **Effort**: **S** (small, <1 hour), **M** (medium, 1–4 hours), **L** (large, >4 hours).
- **Risk**: **low**, **medium**, **high** (with rationale).

| ID | Exact Files / Sections | Change Summary | Priority | Feasibility | Effort | Risk | Dependencies / Approval | Acceptance Criterion |
|---|---|---|---|---|---|---|---|---|
| **ACT-01** | `README.md` (lines 5, 23, 37, 64, 99–101) | Translate Catalan line 5 to English; fix link text pointing to v0.2.0 so it reflects v0.3.0; update release notes link to v0.3.0; delete obsolete clone status caveat | **P0** | **F3** | **S** | low (no code changes) | None (doc-only) | README is 100% English, all links resolve to v0.3.0, and clone caveat is removed |
| **ACT-02** | `docs/canonical-schema.md` (table row `last_updated_at`) | Fix broken relative link `[Z|±HH:MM](Z|±HH:MM)` by converting to code span | **P0** | **F3** | **S** | low | None (doc-only) | Markdown link checker finds zero broken links in canonical-schema.md |
| **ACT-03** | `docs/maintenance/biodata-snapshot-and-restore-guide.md` (line 15) | Fix broken link to `.dump` file; explicitly document that the 4.8 MB dump file is external; link to tracked `releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json` | **P0** | **F3** | **S** | low | None (doc-only) | Zero broken links in document; clear statement on dump file external status |
| **ACT-04** | `docs/maintenance/technical-maintenance-guide.md` (lines 46, 101) and `docs/roadmap/mfp-catalog-implementation-plan.md` (line 96) | Replace 3 broken links pointing to deleted `go-annotation-evidence-contract.md` with citations to ADR-007 and roadmap Phase D0 | **P0** | **F3** | **S** | low | None (doc-only) | All 3 broken links resolved; no references to deleted file |
| **ACT-05** | `docs/getting-started.md` (lines 124–131) | Remove obsolete clone status caveat asserting candidate is an uncommitted working-tree file | **P0** | **F3** | **S** | low | None (doc-only) | Section removed; verification instructions match committed repository state |
| **ACT-06** | `docs/analysis/five-source-descriptive-study-plan.md` (line 9) & `docs/releases/mfp-catalog-v1-contract-draft.md` (line 27) | Correct link targets pointing to `v0.2.0` so they target `releases/mfp-catalog-candidate-v0.3.0/` | **P1** | **F3** | **S** | low | None (doc-only) | Links target active candidate v0.3.0 |
| **ACT-07** | `docs/roadmap/mfp-catalog-implementation-plan.md` (line 39) | Delete contradictory line 39 stating Multifaceted and Multitask are not ingested; align snapshot text with lines 37 and 54–75 | **P1** | **F3** | **S** | low | None (doc-only) | Roadmap snapshot section is internally consistent; reflects 5-source baseline |
| **ACT-08** | `docs/source-profiles/multifacetedprotdb.md` & `multitaskprotdb-ii.md` | Retitle historical proposal headings; remove "NOT implemented" and "fifth source NOT integrated" banners | **P1** | **F3** | **S** | low | None (doc-only) | Headings accurately reflect completed catalog integration |
| **ACT-09** | `scripts/README.md` | Update table row 19 to v0.3.0; add missing entries for `analyze_question1..6.py` and `build_multitask_slice.py`; add warning banner to `build_protein_facets.py` | **P1** | **F3** | **M** | low | None (doc-only) | Table documents all 28 scripts currently in `scripts/` |
| **ACT-10** | `data/curated/README.md` | Expand 3-line README into a complete schema dictionary documenting all 6 formal JSON schemas | **P1** | **F3** | **M** | low | None (doc-only) | Every JSON schema in `data/curated/` is indexed with draft version, purpose, and CLI check |
| **ACT-11** | `tests/fixtures/functional_claims_multitask/README.md` (line 7) | Correct path `data/raw/source_manifest.csv` to `data/manifests/source_manifest.csv` | **P1** | **F3** | **S** | low | None (doc-only) | Path points to existing manifest file |
| **ACT-12** | `docs/source-catalog.md` | Update source registry to reflect five-source reality: MoonProt status as 702 acquired records; MultifacetedProtDB artifact as JSON | **P1** | **F3** | **M** | low | None (doc-only) | Registry matches candidate MANIFEST.json counts and artifacts |
| **ACT-13** | `docs/acquisition-protocols/moonprot.md` & `moonprot-artifact-index.md` | Update status sections to clarify that 1..706 snapshot acquisition was completed on 2026-09-24 and is frozen under ADR-002 | **P1** | **F3** | **S** | low | None (doc-only) | Protocols accurately reflect historical acquisition completion |
| **ACT-14** | `docs/roadmap/core/experiment_guio_v1.md` | Quarantine or remove corrupted mojibake file; retain clean `experiment_definition.md` | **P1** | **F2** | **S** | low (lossless, duplicate) | Maintainer approval | Zero corrupted encoding files in repository |
| **ACT-15** | `docs/roadmap/01-07` & `docs/roadmap/core/` | Create `docs/archive/` hierarchy; add English metadata header blocks and status banners explicitly identifying documents as unapproved proposals | **P1** | **F2** | **M** | low | Gate G0 Review | All Spanish/Catalan proposals carry clear English status banners |
| **ACT-16** | `CHANGELOG.md` | Add release entries for milestones `v0.1.0-source-freeze`, `pre-moonprot-baseline-v0.1`, `mfp-catalog-candidate-v0.2.0`, and `v0.3.0` | **P2** | **F3** | **M** | low | None (doc-only) | CHANGELOG contains complete milestone history |
| **ACT-17** | `docs/roadmap/core/experiment-guio-v2.md` | Extract embedded Annex 1 and Annex 2 into separate archive references; add English executive summary and status notice | **P2** | **F2** | **M** | low | Gate G0 Review | Document reduced from 2,147 lines to clean proposal body; zero duplication |
| **ACT-18** | Pre-commit doc checking | Add lightweight markdown link check and trailing whitespace/BOM check to CI (`ci.yml`) | **P3** | **F3** | **S** | low | None | Broken links and mojibake caught automatically before commit |

---

## 8. English Migration Plan and Reviewable Change Batches

### 8.1 English Migration Rules
In accordance with the repository language policy defined in [AGENTS.md](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md):
1. **Production Language Mandate**: All maintained first-party documentation, specifications, schemas, ADRs, source code, docstrings, tests, and CLI help messages must be written in **English**.
2. **Explicit Language Exceptions (Preservation of Provenance)**:
   - Original source values, verbatim raw fields, extraction locators, and error strings must remain in their original language. Never silently translate raw source data.
   - Historical audit reports (`MFP_DATA_AUDITABILITY_MATRIX.md`, `MFP_EXTRACTION_UNIFICATION_AUDIT.md`) and pre-existing Catalan/Spanish research dossiers remain in their original language to preserve historical audit trails and document integrity.
   - Instead of translating 7,500 lines of unapproved research proposals, each non-English proposal receives an **English Metadata Header and Status Banner** contextualizing its status, scope, and lack of implementation approval.

### 8.2 Sequenced Change Batches

#### Batch 1: Critical Entry-Point Correction, Broken Link Repair, and Version Realignment (Priority P0 / Feasibility F3)
- **Scope**: Documentation-only fixes addressing misleading guidance, broken navigation, and version mismatches.
- **Target Files**:
  * `README.md`
  * `docs/canonical-schema.md`
  * `docs/maintenance/biodata-snapshot-and-restore-guide.md`
  * `docs/maintenance/technical-maintenance-guide.md`
  * `docs/roadmap/mfp-catalog-implementation-plan.md`
  * `docs/getting-started.md`
  * `docs/analysis/five-source-descriptive-study-plan.md`
  * `docs/releases/mfp-catalog-v1-contract-draft.md`
  * `tests/fixtures/functional_claims_multitask/README.md`
- **Permitted Edits**:
  * Translate Catalan line 5 in `README.md` to English: *"This repository prioritizes traceability and reproducibility."*
  * Correct link text in `README.md` lines 23 and 37 from `v0.2.0` to `v0.3.0`.
  * Update release notes link in `README.md` line 64 to `docs/releases/mfp-catalog-candidate-v0.3.0.md`.
  * Delete obsolete clone status caveats in `README.md` (lines 99–101) and `docs/getting-started.md` (lines 124–131).
  * Repair broken link `[Z|±HH:MM](Z|±HH:MM)` in `docs/canonical-schema.md`.
  * Fix broken link to `.dump` file in `docs/maintenance/biodata-snapshot-and-restore-guide.md`.
  * Replace 3 broken links to deleted `go-annotation-evidence-contract.md` in `docs/maintenance/technical-maintenance-guide.md` and `docs/roadmap/mfp-catalog-implementation-plan.md`.
  * Correct candidate link target in `docs/analysis/five-source-descriptive-study-plan.md` and `docs/releases/mfp-catalog-v1-contract-draft.md`.
  * Fix manifest path typo in `tests/fixtures/functional_claims_multitask/README.md`.
- **Exclusions**: No code changes; no data changes; no edits to ADRs or releases.
- **Verification Check**: Automated relative link scan passes with 0 broken links; `git diff` touches only declared files.

#### Batch 2: Catalog Governance, Source Profiles, and Script Index Alignment (Priority P1 / Feasibility F3)
- **Scope**: Aligning source profiles, roadmap text, and script navigation with five-source reality.
- **Target Files**:
  * `docs/roadmap/mfp-catalog-implementation-plan.md`
  * `docs/source-profiles/multifacetedprotdb.md`
  * `docs/source-profiles/multitaskprotdb-ii.md`
  * `docs/source-catalog.md`
  * `docs/acquisition-protocols/moonprot.md`
  * `docs/acquisition-protocols/moonprot-artifact-index.md`
  * `scripts/README.md`
  * `data/curated/README.md`
  * `data/processed/mfp_catalog_mvp/README.md`
  * `docs/architecture/data-flow.md`
  * `docs/architecture/requirements-traceability.md`
- **Permitted Edits**:
  * Delete contradictory line 39 in `docs/roadmap/mfp-catalog-implementation-plan.md`.
  * Retitle proposal headings in `multifacetedprotdb.md` and `multitaskprotdb-ii.md` to reflect completed integration.
  * Update `docs/source-catalog.md` to reflect 5-source status and canonical JSON artifact for Multifaceted.
  * Update MoonProt acquisition protocols to reflect completed 2026-09-24 snapshot.
  * Expand `scripts/README.md` to include all 28 scripts.
  * Expand `data/curated/README.md` into a complete schema dictionary.
  * Replace absolute paths in `data/processed/mfp_catalog_mvp/README.md` with relative paths.
  * Update `data-flow.md` and `requirements-traceability.md` to reference v0.3.0.
- **Verification Check**: `PYTHONPATH=src python scripts/validate_repository.py` passes all checks; script inventory matches filesystem.

#### Batch 3: Research Proposal Archival, Mojibake Deduplication, and Status Banners (Priority P1 / Feasibility F2)
- **Scope**: Segregating unapproved Spanish/Catalan proposals into `docs/archive/` and eliminating mojibake corruption.
- **Target Files**:
  * `docs/roadmap/01_dossier_experimento.md` through `07_plan_implementacion_y_validacion.md`
  * `docs/roadmap/core/experiment_guio_v1.md`
  * `docs/roadmap/core/experiment_definition.md`
  * `docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`
  * `docs/roadmap/core/experiment-guio-v2.md`
  * `docs/roadmap/core/guion_propuesta.md`
  * `docs/experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md`
- **Permitted Edits**:
  * Move Spanish dossiers `01`–`07` to `docs/archive/proposals-2026-10-spanish/`.
  * Move legacy Catalan research plan to `docs/archive/proposals-2026-10-core/`.
  * Move presentation storyboard `guion_propuesta.md` to `docs/roadmap/core/presentation/`.
  * Quarantine or delete corrupted file `docs/roadmap/core/experiment_guio_v1.md`.
  * Add standardized English Metadata Header and Warning Banner to all archived documents:
    > `> [!WARNING]`
    > `> **Unapproved Research Proposal (Historical Archive)**`
    > `> This document is a research proposal for human review. It is NOT an approved specification or architectural decision record. Implementation code, database queries, and metric pipelines described herein are NOT authorized.`
- **Verification Check**: All archived documents carry English warning banners; no broken internal links created.

#### Batch 4: English Synthesis of Reusable Methodology and Schema Documentation (Priority P2 / Feasibility F2)
- **Scope**: Authoring clean, maintainable English syntheses of valuable scientific methodology from archived dossiers.
- **Deliverables**:
  * `docs/curation/literature-curation-manual.md`: English synthesis of manual adjudication protocols from `06_manual_revision_bibliografica.md`.
  * `docs/architecture/scientific-background.md`: English synthesis of biological rationale, annotation lag, and metric definitions from dossiers `01`, `02`, and `04`.
  * `CHANGELOG.md`: Full version history consolidation.
- **Verification Check**: Peer review by scientific lead; full consistency with ADR-001 through ADR-007.

---

## 9. Unresolved Decisions Requiring Human Approval

The following five architectural and scientific decision gates require formal human review and approval before execution:

1. **Decision Gate G0 (Scope & Roadmap Delimitation)**:
   - *Question*: Does the research team formally approve `docs/roadmap/core/experiment-guio-v2.md` (PEC-EXP-001 v0.2.1) as the future experimental roadmap for downstream phases, or should it remain strictly an unapproved advisory proposal?
   - *Governance Rule*: Until G0 is formally approved in writing, no agent or developer may implement metric calculations, semantic similarity pipelines, or inter-aspect co-occurrence matrices.
2. **Decision Gate G1 (Disposition of Proposed ADR-008 & Pilot Tasks P3–P4)**:
   - *Question*: Should proposed [ADR-008](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-008-functional-normalization-pilot-scope.md) be transitioned from `Proposed` to `Accepted`, formally authorizing the extension of the functional normalization pilot across PlantMP (TASK-04), MoonProt (TASK-05), MoonDB/Multifaceted (TASK-06), and the integrated pilot pipeline (TASK-07, TASK-08)?
   - *Current Status*: Scoped authorization is strictly confined to TASK-01, TASK-02, and TASK-03.
3. **Decision Gate G2 (Retirement of Unapproved Heuristic 2-Facet Model)**:
   - *Question*: Should the heuristic 2-facet files (`src/mfp_bibliography/functional_normalization.py`, `scripts/build_protein_facets.py`, `src/mfp_bibliography/targetdata_client.py`) be formally deleted or moved to an isolated quarantine branch?
   - *Rationale*: They violate SDD governance, hardcode external filesystem paths (`go-basic.obo`), and rely on unmocked PostgreSQL database credentials.
4. **Decision Gate G3 (Third-Party Data Licensing Resolution for `mfp_catalog_v1`)**:
   - *Question*: How should maintainers resolve the `terms_not_recorded` status for the four tracked raw artifacts in `data/manifests/source_manifest.csv` prior to tagging the formal `mfp_catalog_v1` release?
   - *Context*: Release contract draft gate 2 requires resolution of source terms before public distribution.
5. **Decision Gate G4 (Disposition of Mojibake Duplicate `experiment_guio_v1.md`)**:
   - *Question*: Should the corrupted mojibake file `docs/roadmap/core/experiment_guio_v1.md` be permanently deleted from the working branch, given that `docs/roadmap/core/experiment_definition.md` preserves the identical text with clean UTF-8 encoding?

---

## 10. Immediate Next Actions (Max 5)

In priority order, the next five recommended actions for the repository maintainers are:

1. **Review and Approve Batch 1 Documentation Edits**:
   Execute the documentation-only fixes in [Batch 1 Specification](#appendix-proposed-first-documentation-only-change-batch) to immediately eliminate the 5 broken links, correct candidate v0.3.0 version references in `README.md`, remove stale clone caveats, and fix manifest path typos.
2. **Review and Decide Gate G1 (ADR-008 Pilot Extension)**:
   Conduct a human review of the completed MultitaskProtDB-II vertical slice (`multitask_slice/` data and review report `REV-MULTITASK-6REC-001`) to decide whether to authorize TASK-04 (PlantMP adapter) under proposed ADR-008.
3. **Quarantine the Unapproved 2-Facet Model**:
   Deprecate and remove `scripts/build_protein_facets.py` and remove references to external database credentials in `src/mfp_bibliography/targetdata_client.py`.
4. **Execute Batch 2 Alignment (Source Profiles & Script Index)**:
   Harmonize source profiles, expand `scripts/README.md` to document all 28 scripts, expand `data/curated/README.md` into a formal schema dictionary, and delete contradictory line 39 in the implementation roadmap.
5. **Organize the Proposal Archive (`docs/archive/`)**:
   Segregate the 13 unapproved Spanish dossiers (`docs/roadmap/01-07`) and legacy Catalan plans into `docs/archive/`, prepending standardized English warning banners to protect the active baseline.

---

## Appendix: Proposed First Documentation-Only Change Batch

### Batch 1 Execution Specification (Awaiting Human Approval)

- **Batch Identifier**: `DOC-BATCH-001-ENTRYPOINT-AND-LINKS`
- **Authorization Status**: **PROPOSED — AWAITING APPROVAL** (Not executed during this audit)
- **Target Files (9 files)**:
  1. `README.md`
  2. `docs/canonical-schema.md`
  3. `docs/maintenance/biodata-snapshot-and-restore-guide.md`
  4. `docs/maintenance/technical-maintenance-guide.md`
  5. `docs/roadmap/mfp-catalog-implementation-plan.md`
  6. `docs/getting-started.md`
  7. `docs/analysis/five-source-descriptive-study-plan.md`
  8. `docs/releases/mfp-catalog-v1-contract-draft.md`
  9. `tests/fixtures/functional_claims_multitask/README.md`

### Permitted Exact Edits
1. **`README.md`**:
   - Line 5: Replace `"Aquest repositori prioritza traçabilitat i reproductibilitat."` with `"This repository prioritizes traceability and reproducibility."`
   - Line 23: Replace link text `[releases/mfp-catalog-candidate-v0.2.0/](releases/mfp-catalog-candidate-v0.3.0/)` with `[releases/mfp-catalog-candidate-v0.3.0/](releases/mfp-catalog-candidate-v0.3.0/)`.
   - Line 37: Replace link text `[releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json](releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)` with `[releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json](releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)`.
   - Line 39: Replace `"Source records (v0.2.0 manifest)"` with `"Source records (v0.3.0 manifest)"`.
   - Line 64: Replace `[release notes](docs/releases/mfp-catalog-candidate-v0.2.0.md)` with `[release notes](docs/releases/mfp-catalog-candidate-v0.3.0.md)`.
   - Lines 99–101: Delete Section `## Repository status caveat` and its text entirely.
2. **`docs/canonical-schema.md`**:
   - Line with `[Z|±HH:MM](Z|±HH:MM)`: Replace with code span `` `Z|±HH:MM` ``.
3. **`docs/maintenance/biodata-snapshot-and-restore-guide.md`**:
   - Line 15: Replace `[`data/snapshots/biodata_mfp_snapshot_20261014.dump`](../../data/snapshots/biodata_mfp_snapshot_20261014.dump)` with `` `data/snapshots/biodata_mfp_snapshot_20261014.dump` (external uncommitted file; see manifest below) ``.
4. **`docs/maintenance/technical-maintenance-guide.md`**:
   - Line 46: Replace `[GO annotation contract](../bibliography/go-annotation-evidence-contract.md)` with `[ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) (Phase D0)`.
   - Line 101: Replace `[go-annotation-evidence-contract.md](../bibliography/go-annotation-evidence-contract.md)` with `[ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)`.
5. **`docs/roadmap/mfp-catalog-implementation-plan.md`**:
   - Line 96: Replace `[GO annotation, evidence-code and bibliography contract](../bibliography/go-annotation-evidence-contract.md)` with `[ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) (Phase D0 contract)`.
6. **`docs/getting-started.md`**:
   - Lines 124–131: Delete Section `## Clone status caveat` and its text entirely.
7. **`docs/analysis/five-source-descriptive-study-plan.md`**:
   - Line 9: Replace `[`releases/mfp-catalog-candidate-v0.3.0/`](../../releases/mfp-catalog-candidate-v0.2.0/)` with `[`releases/mfp-catalog-candidate-v0.3.0/`](../../releases/mfp-catalog-candidate-v0.3.0/)`.
   - Line 11: Replace `[`DATA_DICTIONARY.md`](../../releases/mfp-catalog-candidate-v0.2.0/DATA_DICTIONARY.md)` with `[`DATA_DICTIONARY.md`](../../releases/mfp-catalog-candidate-v0.3.0/DATA_DICTIONARY.md)`.
   - Line 13: Replace `[`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json)` with `[`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)`.
8. **`docs/releases/mfp-catalog-v1-contract-draft.md`**:
   - Line 27: Replace `[`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json)` with `[`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)`.
9. **`tests/fixtures/functional_claims_multitask/README.md`**:
   - Line 7: Replace `data/raw/source_manifest.csv` with `data/manifests/source_manifest.csv`.

### Prohibited Actions and Exclusions
- Do NOT edit any source code file under `src/` or `scripts/`.
- Do NOT edit any JSON schema under `data/curated/`.
- Do NOT edit any packaged release file under `releases/`.
- Do NOT edit any raw data file under `data/raw/`.
- Do NOT stage or commit changes to Git.

### Bounded Verification Commands
```bash
# 1. Run repository structural verification
PYTHONPATH=src python3 scripts/validate_repository.py

# 2. Run offline package verification
PYTHONPATH=src python3 scripts/package_catalog_candidate.py --verify-package

# 3. Verify zero broken markdown links remain across the 9 modified files
python3 -c '
import re
from pathlib import Path
files = [
    "README.md", "docs/canonical-schema.md", "docs/maintenance/biodata-snapshot-and-restore-guide.md",
    "docs/maintenance/technical-maintenance-guide.md", "docs/roadmap/mfp-catalog-implementation-plan.md",
    "docs/getting-started.md", "docs/analysis/five-source-descriptive-study-plan.md",
    "docs/releases/mfp-catalog-v1-contract-draft.md", "tests/fixtures/functional_claims_multitask/README.md"
]
broken = 0
for f in files:
    p = Path(f)
    content = p.read_text()
    for text, link in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content):
        if link.startswith(("http", "mailto", "#", "file:", "conversation:", "sidecar:")): continue
        tgt = (p.parent / link.split("#")[0]).resolve()
        if not tgt.exists():
            print(f"Broken link in {f}: {link}")
            broken += 1
print(f"Batch 1 check complete. Broken links in modified files: {broken}")
assert broken == 0
'
```

### Completion Criteria
1. The 9 declared target files are updated strictly per the permitted edits.
2. `git diff --stat` shows changes confined exclusively to the 9 declared files.
3. The relative link verification script reports 0 broken links in the affected files.
4. `PYTHONPATH=src python scripts/validate_repository.py` returns `{"ok": true}` with exit code 0.
