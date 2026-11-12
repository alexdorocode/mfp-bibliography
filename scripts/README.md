# Script Index

This directory contains utility, pipeline, validation, and analysis scripts supporting the `mfp-bibliography` repository.

## Inventory Summary & Exclusions
- **Total inventoried Python scripts accounted for**: 25 scripts.
  - **Committed active baseline & verification scripts (18 scripts)**: Core catalog builders, source adapters, status generator, audit scripts, analysis CLIs, profiler, and verification tools (`validate_repository.py`, `package_catalog_candidate.py`, `build_mfp_catalog_mvp.py`, `build_source_claims_moondb.py`, `build_source_claims_plantmp.py`, `build_source_records_multifacetedprotdb.py`, `build_source_records_multitaskprotdb_ii.py`, `generate_effective_status_moondb_plantmp.py`, `profile_source.py`, `parse_moonprot_fixture.py`, `audit_moondb_plantmp_overlap.py`, `audit_moondb_plantmp_snapshot.py`, `analyze_question1.py` through `analyze_question6.py`).
  - **Frozen controlled acquisition scripts (2 scripts)**: `acquire_moonprot_smoke.py` and `acquire_moonprot_batch.py` (operational snapshot completed 2026-09-24; live network execution frozen under accepted [ADR-002](../docs/decisions/ADR-002-raw-data-immutability.md)).
  - **Experimental pilot tooling (2 scripts)**: `build_multitask_slice.py` (committed pilot tool under proposed ADR-008 Level 2) and `build_functional_claims_pilot.py` (untracked in git working tree; formal repository approval status not established). Neither is included in packaged candidate v0.3.0.
  - **Non-operational placeholder / skeleton scripts (2 scripts)**: `build_manifest.py` and `normalize_source_records.py`.
  - **Superseded experimental script (1 script)**: `build_protein_facets.py` (heuristic 2-facet collapsing; superseded by the relational claim architecture in proposed [ADR-008](../docs/decisions/ADR-008-functional-normalization-pilot-scope.md)).
- **Explicit exclusions**:
  - `scripts/__pycache__/`: Directory containing compiled Python bytecode (`.pyc`) files (runtime execution artifacts; excluded from inventory).
  - `scripts/README.md`: This documentation index file.

All scripts operate **strictly offline** (no network requests) except for the two policy-governed MoonProt acquisition CLIs (`acquire_moonprot_smoke.py` and `acquire_moonprot_batch.py`), which contain HTTP client code and are currently frozen under accepted [ADR-002](../docs/decisions/ADR-002-raw-data-immutability.md).

---

## Script Inventory Table

| Script | Subsystem / Lifecycle | Purpose | Main Inputs | Main Outputs / Write Effects | Network | Status / Verification |
|---|---|---|---|---|---|---|
| `validate_repository.py` | Repository Integrity | Validate scaffold structure, manifest header, JSON schemas, and interim claim integrity | `data/curated/` schemas, `data/manifests/` | JSON report to stdout; exit code 0/1 | Offline | Committed baseline; active CI/pre-commit check |
| `package_catalog_candidate.py` | Release Engineering | Package validated catalog candidate or run offline release verification | `data/processed/mfp_catalog_mvp/` or `releases/` candidate | `releases/mfp-catalog-candidate-v0.3.0/` or stdout | Offline | Committed baseline; verifies candidate v0.3.0 |
| `build_mfp_catalog_mvp.py` | Catalog Pipeline | Build unified five-source catalog tables and summary statistics | `data/raw/`, `data/interim/`, absent log | `data/processed/mfp_catalog_mvp/` (6 CSVs, 2 JSONs) | Offline | Committed baseline (Contract `MFPB_0_19_MFP_CATALOG_MVP_V2`) |
| `build_source_claims_moondb.py` | Source Adapter | Adapt MoonDB raw TSV artifact to interim source claims | `data/raw/moondb/all_emf_and_curated.tsv`, manifest, policy | `data/interim/source_claims_moondb.csv`, validation report | Offline | Committed baseline |
| `build_source_claims_plantmp.py` | Source Adapter | Adapt PlantMP raw CSV artifact to interim source claims | `data/raw/plantmp/PlantMP_all.csv`, manifest, policy | `data/interim/source_claims_plantmp.csv`, validation report | Offline | Committed baseline |
| `build_source_records_multifacetedprotdb.py` | Source Adapter | Ingest MultifacetedProtDB JSON to interim source records | `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` | `data/interim/source_records_multifacetedprotdb.csv`, report | Offline | Committed baseline (Contract `MFPB_0_18_MFP_CATALOG_MVP_V1`) |
| `build_source_records_multitaskprotdb_ii.py` | Source Adapter | Ingest MultitaskProtDB-II CSV to interim source records | `data/raw/multitaskprotdb-ii/proteins.csv` | `data/interim/source_records_multitaskprotdb_ii.csv`, report | Offline | Committed baseline (Contract `MFPB_0_19_MFP_CATALOG_MVP_V2`) |
| `generate_effective_status_moondb_plantmp.py` | Derived Pipeline | Generate effective-status derived artifact and snapshot manifest | `data/interim/source_claims_{moondb,plantmp}.csv` | `data/interim/effective_status_moondb_plantmp.csv`, snapshot JSON, reports | Offline | Committed baseline (Contract `MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0`) |
| `profile_source.py` | Source Profiling | Read-only structural profiling of raw tabular artifacts | Local raw source artifact path | Structured JSON profiling report to stdout or file | Offline | Committed baseline utility |
| `parse_moonprot_fixture.py` | Fixture Parsing | Parse local MoonProt HTML fixtures deterministically | Local HTML fixture file(s) | JSON parsed record to stdout | Offline | Committed baseline (MFPB_0_11_MOONPROT_OFFLINE_PARSER) |
| `audit_moondb_plantmp_overlap.py` | Quality Audit | Compute two-source overlap audit between MoonDB and PlantMP | `data/interim/source_claims_{moondb,plantmp}.csv` | `data/interim/reports/moondb_plantmp_overlap_audit.{json,md}` | Offline | Committed baseline |
| `audit_moondb_plantmp_snapshot.py` | Quality Audit | Quality audit of local MoonDB + PlantMP snapshot against schema | `data/interim/reports/effective_status_moondb_plantmp_snapshot.json` | Validation report to stdout; exit code 0/1 | Offline | Committed baseline |
| `analyze_question1.py` | Descriptive Study | Question 1 CLI: Source records vs unique protein entities by source | `releases/` candidate directory | JSON report to stdout or `--output-dir` | Offline | Committed baseline (supports 5-source descriptive study) |
| `analyze_question2.py` | Descriptive Study | Question 2 CLI: Exact source-set overlap combinations | `releases/` candidate directory | JSON report to stdout or `--output-dir` | Offline | Committed baseline |
| `analyze_question3.py` | Descriptive Study | Question 3 CLI: Distinct sources per protein entity distribution | `releases/` candidate directory | JSON report to stdout or `--output-dir` | Offline | Committed baseline |
| `analyze_question4.py` | Descriptive Study | Question 4 CLI: MoonProt MPID snapshot coverage by status | `releases/` candidate directory | JSON report to stdout or `--output-dir` | Offline | Committed baseline |
| `analyze_question5.py` | Descriptive Study | Question 5 CLI: Status-label inventory and provenance distribution | `releases/` candidate directory | JSON report to stdout or `--output-dir` | Offline | Committed baseline |
| `analyze_question6.py` | Descriptive Study | Question 6 CLI: Completeness of canonical protein fields | `releases/` candidate directory | JSON report to stdout or `--output-dir` | Offline | Committed baseline |
| `build_multitask_slice.py` | SDD Pilot Tooling | Build and verify persistent 6-record MultitaskProtDB-II pilot slice | Fixture CSV or raw `proteins.csv`, catalog | `data/interim/pilot/multitask_slice/` (3 CSVs, 1 manifest) | Offline | Committed experimental pilot tooling ([ADR-008](../docs/decisions/ADR-008-functional-normalization-pilot-scope.md)) |
| `build_functional_claims_pilot.py` | SDD Pilot Tooling | Build and verify integrated 3-source functional normalization pilot package | Catalog MVP, raw artifacts, `data/curated/` schemas | `data/interim/pilot/` (3 CSVs, manifest) and JSON report | Offline | Untracked experimental pilot tooling; not in candidate v0.3.0; approval status not established |
| `build_protein_facets.py` | Experimental (Superseded) | Build binary 2-facet model (BP1/MF1/CC1 vs BP2/MF2/CC2) | `data/processed/mfp_catalog_mvp/`, auxiliary TSVs | `data/processed/mfp_catalog_mvp/mfp_protein_facets.csv`, summary | Offline | Superseded by relational claim model in proposed [ADR-008](../docs/decisions/ADR-008-functional-normalization-pilot-scope.md); not for candidate pipeline |
| `acquire_moonprot_smoke.py` | Controlled Acquisition | Smoke acquisition CLI (MPIDs 1–3 only; dry-run default) | MoonProt web endpoints (HTTP) | `data/raw/moonprot/` HTML files + smoke logs | Network (HTTP) | Operational protocol complete; execution closed |
| `acquire_moonprot_batch.py` | Controlled Acquisition | Controlled batch acquisition CLI (explicit IDs/ranges, max 100) | MoonProt web endpoints (HTTP) | `data/raw/moonprot/` HTML files + index + logs | Network (HTTP) | Snapshot 1..706 complete (2026-09-24); frozen under [ADR-002](../docs/decisions/ADR-002-raw-data-immutability.md) |
| `build_manifest.py` | Utility Skeleton | Safe skeleton CLI for source manifest generation | `--input-dir` raw sources | Manifest CSV scaffold to `--output` | Offline | Placeholder / skeleton utility |
| `normalize_source_records.py` | Utility Skeleton | Placeholder CLI for source-specific normalization adapters | None (stubbed) | Informational stdout message | Offline | Placeholder stub |

---

## Detailed Script Specifications

### 1. Repository Validation & Candidate Release Packaging

#### `validate_repository.py`
- **Purpose**: Validates repository structural invariants, directory hygiene, manifest header format, Draft 2020-12 JSON schema validity in `data/curated/` (`mfp_source_records.schema.json` and `source_claims.schema.json`), and interim claim reconciliation for MoonDB and PlantMP.
- **CLI Arguments**:
  - `--root`: Path to repository root (defaults to parent directory of script).
- **Inputs**: File system paths, manifest, schemas, interim claims.
- **Outputs / Write Effects**: None (read-only; outputs JSON validation report to stdout; returns exit code 0 on success, non-zero on error).
- **External Dependencies**: Python standard library (`argparse`, `json`, `pathlib`), `jsonschema`, `mfp_bibliography.validation`.
- **Network Behavior**: Strictly offline.

#### `package_catalog_candidate.py`
- **Purpose**: Builds and packages the candidate release directory `releases/mfp-catalog-candidate-v0.3.0/` from `data/processed/mfp_catalog_mvp/`, computing SHA-256 checksums, generating `MANIFEST.json` and `DATA_DICTIONARY.md`, and enforcing candidate immutability. Also provides two offline verification modes.
- **CLI Arguments**:
  - `--verify-package`: Offline verification mode. Validates packaged files in `releases/mfp-catalog-candidate-v0.3.0/` against its `MANIFEST.json` (checks inventory, SHA-256 hashes, row counts, primary keys, and foreign keys).
  - `--verify`: Rebuild-compare verification mode. Compares packaged candidate bytes against locally rebuilt tables in `data/processed/mfp_catalog_mvp/`.
  - `--candidate-id`: Target candidate ID (default: `mfp-catalog-candidate-v0.3.0`).
  - `--root`, `--catalog-dir`, `--releases-root`: Path configuration overrides.
- **Inputs**: `data/processed/mfp_catalog_mvp/` (packaging mode); `releases/mfp-catalog-candidate-v0.3.0/` (verify modes).
- **Outputs / Write Effects**: In packaging mode, creates directory `releases/mfp-catalog-candidate-{candidate_id}/` and writes packaged CSVs, checksums, manifest, and data dictionary. In verification modes, read-only.
- **External Dependencies**: Python standard library (`argparse`, `csv`, `hashlib`, `json`, `pathlib`).
- **Network Behavior**: Strictly offline.

---

### 2. Catalog Construction & Baseline Adapters

#### `build_mfp_catalog_mvp.py`
- **Purpose**: Main assembly script for the unified five-source catalog. Enforces universe and raw-input gates, creates deterministic protein IDs (`MFPB_PROTEIN_ID_V1`), performs exact normalized UniProt accession merging, and executes pre-write integrity checks before persisting tables.
- **CLI Arguments**: None.
- **Inputs**:
  - Canonical raw inputs: `data/raw/moondb/all_emf_and_curated.tsv`, `data/raw/plantmp/PlantMP_all.csv`, `data/raw/moonprot/*.html`, `data/raw/moonprot/artifact_index.csv`.
  - Interim source records: `data/interim/source_records_multifacetedprotdb.csv`, `data/interim/source_records_multitaskprotdb_ii.csv`.
  - Tracking logs: `data/interim/moonprot_absent_log.csv`.
- **Outputs / Write Effects**: Overwrites tables and summaries in `data/processed/mfp_catalog_mvp/`:
  - `mfp_proteins.csv`, `mfp_source_records.csv`, `mfp_identifiers.csv`, `mfp_assertions.csv`, `mfp_coverage.csv`.
  - `summary.json`, `organism_summary.csv`, `source_overlap_summary.csv`.
- **External Dependencies**: Standard library, `mfp_bibliography.raw_input_verification`, `mfp_bibliography.protein_id`.
- **Network Behavior**: Strictly offline.

#### `build_source_claims_moondb.py`
- **Purpose**: Generates interim source claims from the MoonDB raw TSV artifact under contract `MFPB_0_8_SOURCE_CLAIMS_CONTRACT_V0`.
- **CLI Arguments**:
  - `--root`: Repository root path.
  - `--output-dir`: Output directory (defaults to `data/interim`).
- **Inputs**: `data/raw/moondb/all_emf_and_curated.tsv`, `data/manifests/source_manifest.csv`, `configs/source_claim_policy_v0.1.yaml`.
- **Outputs / Write Effects**: Writes `data/interim/source_claims_moondb.csv` (351 rows) and `source_claims_moondb_validation_report.json`.
- **External Dependencies**: Standard library, `mfp_bibliography.moondb_claims`.
- **Network Behavior**: Strictly offline.

#### `build_source_claims_plantmp.py`
- **Purpose**: Generates interim source claims from the PlantMP raw CSV artifact under contract `MFPB_0_8_SOURCE_CLAIMS_CONTRACT_V0`.
- **CLI Arguments**:
  - `--root`: Repository root path.
  - `--output-dir`: Output directory (defaults to `data/interim`).
- **Inputs**: `data/raw/plantmp/PlantMP_all.csv`, `data/manifests/source_manifest.csv`, `configs/source_claim_policy_v0.1.yaml`.
- **Outputs / Write Effects**: Writes `data/interim/source_claims_plantmp.csv` (112 rows) and `source_claims_plantmp_validation_report.json`.
- **External Dependencies**: Standard library, `mfp_bibliography.plantmp_claims`.
- **Network Behavior**: Strictly offline.

#### `build_source_records_multifacetedprotdb.py`
- **Purpose**: Ingests MultifacetedProtDB raw JSON artifact into interim source records under contract `MFPB_0_18_MFP_CATALOG_MVP_V1`.
- **CLI Arguments**:
  - `--root`: Repository root path.
- **Inputs**: `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` (verified against manifest hash).
- **Outputs / Write Effects**: Writes `data/interim/source_records_multifacetedprotdb.csv` (1,103 rows) and `source_records_multifacetedprotdb_validation_report.json`.
- **External Dependencies**: Standard library (`ast.literal_eval`), `mfp_bibliography.multifacetedprotdb_records`.
- **Network Behavior**: Strictly offline.

#### `build_source_records_multitaskprotdb_ii.py`
- **Purpose**: Ingests MultitaskProtDB-II raw CSV artifact into interim source records under contract `MFPB_0_19_MFP_CATALOG_MVP_V2`.
- **CLI Arguments**:
  - `--root`: Repository root path.
- **Inputs**: `data/raw/multitaskprotdb-ii/proteins.csv` (verified against manifest hash).
- **Outputs / Write Effects**: Writes `data/interim/source_records_multitaskprotdb_ii.csv` (694 rows) and `source_records_multitaskprotdb_ii_validation_report.json`.
- **External Dependencies**: Standard library, `mfp_bibliography.multitaskprotdb_ii_records`.
- **Network Behavior**: Strictly offline.

#### `generate_effective_status_moondb_plantmp.py`
- **Purpose**: Computes derived effective operational status aggregation across MoonDB and PlantMP claims, producing an effective status artifact and snapshot manifest under `MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0` and `MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT`.
- **CLI Arguments**: None (uses standard repository paths).
- **Inputs**: `data/interim/source_claims_moondb.csv`, `data/interim/source_claims_plantmp.csv`, `configs/source_claim_policy_v0.1.yaml`.
- **Outputs / Write Effects**: Writes `data/interim/effective_status_moondb_plantmp.csv`, `data/interim/reports/effective_status_moondb_plantmp_snapshot.json`, and report files.
- **External Dependencies**: Standard library, `mfp_bibliography.effective_status`.
- **Network Behavior**: Strictly offline.

---

### 3. Profiling, Quality Audits, & Fixtures

#### `profile_source.py`
- **Purpose**: Read-only structural profiler for raw tabular artifacts; measures line counts, encoding, delimiter, missingness, and column cardinality.
- **CLI Arguments**:
  - `file_path`: Positional path to raw artifact.
  - `--source-id`: Mandatory source identifier string (e.g. `SRC_MOONDB`).
  - `--output`: Optional file path for JSON output.
- **Inputs**: Raw tabular file.
- **Outputs / Write Effects**: Writes JSON report to `--output` if specified, else stdout.
- **External Dependencies**: Standard library.
- **Network Behavior**: Strictly offline.

#### `parse_moonprot_fixture.py`
- **Purpose**: Offline parser CLI for MoonProt local HTML files; extracts `MoonProt ID`, `UniProt ID`, and `Name(s)` using visible label matching.
- **CLI Arguments**:
  - `fixtures`: One or more paths to HTML files.
  - `--expected-mpid`: Optional expected integer MPID.
- **Inputs**: Local HTML fixture files.
- **Outputs / Write Effects**: JSON record printed to stdout.
- **External Dependencies**: Standard library, `mfp_bibliography.moonprot_parser`.
- **Network Behavior**: Strictly offline.

#### `audit_moondb_plantmp_overlap.py`
- **Purpose**: Performs read-only overlap audit between MoonDB and PlantMP interim claims.
- **CLI Arguments**:
  - `--root`: Repository root path.
  - `--output-dir`: Output directory for audit reports (defaults to `data/interim/reports`).
- **Inputs**: Interim claim CSVs for MoonDB and PlantMP.
- **Outputs / Write Effects**: Writes `moondb_plantmp_overlap_audit.json` and `.md`.
- **External Dependencies**: Standard library, `mfp_bibliography.overlap_audit`.
- **Network Behavior**: Strictly offline.

#### `audit_moondb_plantmp_snapshot.py`
- **Purpose**: Validates the local MoonDB + PlantMP effective-status snapshot against `data/interim/reports/effective_status_snapshot.schema.json`.
- **CLI Arguments**: None.
- **Inputs**: `data/interim/reports/effective_status_moondb_plantmp_snapshot.json`, `data/interim/effective_status_moondb_plantmp.csv`.
- **Outputs / Write Effects**: None (prints validation results to stdout; exit code 0 on pass).
- **External Dependencies**: Standard library, `jsonschema`.
- **Network Behavior**: Strictly offline.

---

### 4. Descriptive Study Analysis CLIs (`analyze_question1.py` through `analyze_question6.py`)

These six CLIs support the five-source descriptive study plan (`docs/analysis/five-source-descriptive-study-plan.md`), evaluating the packaged candidate release without mutating data.

#### Common CLI Arguments & Behavior
- `--candidate-dir`: Path to candidate package directory (defaults to `releases/mfp-catalog-candidate-v0.3.0`).
- `--output-dir`: Optional directory to write JSON analysis reports. If omitted, outputs JSON to stdout.
- **Network**: Strictly offline.

- **`analyze_question1.py`**: Computes source records vs unique protein entities by source. (Input: `mfp_source_records.csv`, `mfp_proteins.csv`).
- **`analyze_question2.py`**: Computes exact source-set overlap across all exclusive combinations of the five sources. (Input: `mfp_source_records.csv`, `mfp_proteins.csv`).
- **`analyze_question3.py`**: Evaluates sharing degree distribution (number of distinct sources claiming each protein entity). (Input: `mfp_source_records.csv`, `mfp_proteins.csv`).
- **`analyze_question4.py`**: Analyzes MoonProt MPID snapshot coverage and status breakdown (`acquired`, `known_absent`, `unresolved`). (Input: `mfp_coverage.csv`, `MANIFEST.json`).
- **`analyze_question5.py`**: Compiles an inventory of source-provided labels and mapped operational statuses. (Input: `mfp_assertions.csv`, `mfp_source_records.csv`).
- **`analyze_question6.py`**: Measures completeness of canonical protein fields across all entities. (Input: `mfp_source_records.csv`, `mfp_proteins.csv`).

---

### 5. Functional Normalization Pilot Tooling (SDD Pilot under ADR-008 Level 2)

#### `build_multitask_slice.py`
- **Purpose**: Builds and verifies a persistent 6-record MultitaskProtDB-II pilot slice package demonstrating multiplicity-preserving functional claim extraction and source GO annotation decomposition.
- **CLI Arguments**:
  - `--input-fixture`: Path to fixture or raw CSV (defaults to `tests/fixtures/functional_claims_multitask/multitask_sample_six_records.csv`).
  - `--output-dir`: Target directory (defaults to `data/interim/pilot/multitask_slice`).
  - `--catalog-path`: Path to catalog source records (defaults to `data/processed/mfp_catalog_mvp/mfp_source_records.csv`).
- **Inputs**: Fixture CSV, catalog table, schemas in `data/curated/`.
- **Outputs / Write Effects**: Writes `functional_claims_slice.csv`, `functional_coverage_slice.csv`, `source_go_annotations_slice.csv`, and `manifest.json`.
- **External Dependencies**: Standard library, `jsonschema`, `mfp_bibliography.functional_claims_multitask`.
- **Network Behavior**: Strictly offline.

#### `build_functional_claims_pilot.py`
- **Purpose**: Builds and verifies the integrated three-source functional normalization pilot package across an empirical cohort of 20 real records (MultitaskProtDB-II, PlantMP, and MoonProt).
- **CLI Arguments**:
  - `--pilot-dir`: Target pilot directory (defaults to `data/interim/pilot`).
  - `--reports-dir`: Target reports directory (defaults to `data/interim/reports`).
  - `--catalog-path`: Path to catalog source records.
- **Inputs**: Catalog source records, raw source artifacts (`data/raw/`), JSON schemas in `data/curated/`.
- **Outputs / Write Effects**: Writes `functional_claims_pilot.csv`, `functional_coverage_pilot.csv`, `source_go_annotations_pilot.csv`, `manifest.json`, and `functional_claims_pilot_report.json`.
- **External Dependencies**: Standard library, `jsonschema`, `mfp_bibliography.functional_claims_plantmp`, `mfp_bibliography.functional_claims_multitask`, `mfp_bibliography.functional_claims_moonprot`.
- **Network Behavior**: Strictly offline.
- **Implementation Status**: **Untracked / Experimental Pilot Tooling**. This script is currently an untracked working-tree file implementing the Level 2 SDD pilot under proposed [ADR-008](../docs/decisions/ADR-008-functional-normalization-pilot-scope.md). It is not included in packaged candidate v0.3.0, and its formal repository approval status is not established in accepted governance records.

---

### 6. Controlled Web Acquisition CLIs (MoonProt Snapshot)

> [!CAUTION]
> These two scripts contain network HTTP client code. They are policy-governed by `docs/acquisition-protocols/moonprot.md`. Because the MoonProt 1..706 snapshot was completed on 2026-09-24, these tools are **frozen** under [ADR-002](../docs/decisions/ADR-002-raw-data-immutability.md). Do not execute live network calls.

#### `acquire_moonprot_smoke.py`
- **Purpose**: Historical smoke acquisition CLI targeting MPIDs 1, 2, and 3 only.
- **CLI Arguments**:
  - `--mpid`: Restricted to `1`, `2`, or `3`.
  - `--user-agent`: Mandatory honest project user agent.
  - `--execute-smoke-test`: Mandatory flag to enable live network requests; defaults to dry-run mode.
  - `--root`: Repository root path.
- **Outputs / Write Effects**: Writes raw HTML to `data/raw/moonprot/` and appends to `data/interim/moonprot_smoke_results.csv` and error log.
- **Status**: Smoke test completed and closed.

#### `acquire_moonprot_batch.py`
- **Purpose**: Controlled batch acquisition CLI targeting explicit MPID ranges (max 100 per invocation) with mandatory 10-second request delays and strict persistence gating.
- **CLI Arguments**:
  - `--mpid`: Explicit comma-separated IDs or ranges (e.g. `4-100`).
  - `--user-agent`: Mandatory honest project user agent.
  - `--execute`: Mandatory flag to perform live requests; defaults to dry-run mode.
  - `--continue-on-error`: Continue processing remaining IDs if an individual request fails.
  - `--root`: Repository root path.
- **Outputs / Write Effects**: Writes verified HTML files to `data/raw/moonprot/mpid_{id}.html`, updates `data/raw/moonprot/artifact_index.csv`, and appends to error log.
- **Status**: Full snapshot (MPIDs 1–706) completed on 2026-09-24; frozen under ADR-002.

---

### 7. Deprecated / Superseded Experimental Scripts

#### `build_protein_facets.py`
- **Purpose**: Experimental script attempting to extract binary functional facets (BP1, MF1, CC1, PMID1 vs BP2, MF2, CC2, PMID2) across catalog entities.
- **CLI Arguments**: None.
- **Inputs**: `data/processed/mfp_catalog_mvp/`, auxiliary raw MoonDB annotation files.
- **Outputs / Write Effects**: Writes `mfp_protein_facets.csv`, `mfp_source_record_facets.csv`, and `mfp_protein_facets_summary.json` to `data/processed/mfp_catalog_mvp/`.
- **Status**: **SUPERSEDED EXPERIMENTAL SCRIPT**. This script collapsed biological multiplicity into an ad-hoc 2-facet model, used unvalidated keyword regexes, and performed arbitrary cellular component assignments. It was documented as defective in repository audit `docs/audits/2026-11-06_repository-sdd-functional-normalization-audit.md` and is superseded by the relational claim model defined in proposed [ADR-008](../docs/decisions/ADR-008-functional-normalization-pilot-scope.md). It is not included in candidate release pipelines.

---

### 8. Skeleton / Placeholder Utilities

#### `build_manifest.py`
- **Purpose**: Safe skeleton CLI for future automated generation of source manifests.
- **CLI Arguments**: `--input-dir`, `--output`, `--force`.
- **Status**: Skeleton / non-operational placeholder.

#### `normalize_source_records.py`
- **Purpose**: Placeholder CLI for future source-specific normalization adapters.
- **CLI Arguments**: `--adapter`.
- **Status**: Non-operational stub; prints informational message.

---

## Verification Modes of `package_catalog_candidate.py`

- `--verify-package` — **PACKAGE_VERIFY** (offline; works in any clean clone): checks inventory, packaged SHA-256 hashes, CSV row counts, primary keys and cross-table foreign keys against the candidate `MANIFEST.json`. Reads only files inside `releases/mfp-catalog-candidate-v0.3.0/`.
- `--verify` — **REBUILD_COMPARE**: compares packaged candidate bytes against locally rebuilt tables in `data/processed/mfp_catalog_mvp/`; requires external raw and interim inputs.
- Default (no flag) — **PACKAGE**: rebuilds and packages the candidate into `releases/mfp-catalog-candidate-{candidate_id}/`. Refuses to overwrite an existing candidate directory if bytes differ.
