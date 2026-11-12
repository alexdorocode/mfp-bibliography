# Curated Data & Schema Dictionary

This directory contains formal JSON Schemas governing normalized data structures, source claim models, and curation contracts within the `mfp-bibliography` repository.

> [!IMPORTANT]
> **Directory Name & Scientific Authority Disclaimer**:
> The directory name `data/curated` is an internal architectural convention designating structured schemas, relational contracts, and normalized pipeline outputs. **The directory name does NOT itself establish local scientific review, laboratory verification, or clinical approval of every represented assertion.**
> 
> **Production Integration Caveat**:
> The presence of a schema in `data/curated/` **does not prove or imply production integration** into the packaged candidate release (`releases/mfp-catalog-candidate-v0.3.0/`). The released catalog candidate is governed separately by contract `MFPB_0_19_MFP_CATALOG_MVP_V2`, whereas several schemas below govern experimental pilot artifacts under proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md) Level 2.

---

## Schema Inventory Revalidation

Rather than assuming six schemas, revalidation of the repository identifies **seven formal JSON Schemas**:
- **Six schemas located directly in `data/curated/`**:
  1. [`effective_status.schema.json`](effective_status.schema.json)
  2. [`functional_claims.schema.json`](functional_claims.schema.json)
  3. [`functional_coverage.schema.json`](functional_coverage.schema.json)
  4. [`mfp_source_records.schema.json`](mfp_source_records.schema.json)
  5. [`source_claims.schema.json`](source_claims.schema.json)
  6. [`source_go_annotations.schema.json`](source_go_annotations.schema.json)
- **One schema located in `data/interim/reports/`** (cross-referenced for complete inventory coverage):
  7. [`effective_status_snapshot.schema.json`](../interim/reports/effective_status_snapshot.schema.json)

All seven schemas adhere to the JSON Schema Draft 2020-12 specification (`https://json-schema.org/draft/2020-12/schema`).

---

## Schema Dictionary

### 1. MFP Source Record Schema
- **File path**: `data/curated/mfp_source_records.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Source Record`
- **Purpose**: Defines the initial canonical source record model for individual source observations, capturing source identity, evidence tiers, benchmark roles, and raw file provenance.
- **Target artifacts**: Canonical source record tables (e.g., initial catalog records).
- **Governing contract & status**: Scaffold Canonical Contract (`docs/canonical-schema.md`).
- **Production integration status**: Baseline schema. Note that packaged candidate v0.3.0 produces `mfp_source_records.csv` via `scripts/build_mfp_catalog_mvp.py` under release contract `MFPB_0_19_MFP_CATALOG_MVP_V2`, which incorporates source-specific fields beyond this initial scaffold.
- **Known producers**: `scripts/build_mfp_catalog_mvp.py`, `src/mfp_bibliography/raw_input_verification.py`.
- **Known validators**:
  - `src/mfp_bibliography/validation.py` (`_check_schema`).
  - Executable check: `PYTHONPATH=src python3 scripts/validate_repository.py`.
  - Test suite: `tests/test_schema.py`.
- **Required fields**: `record_id`, `source_id`, `source_record_id`, `scientific_label`, `evidence_tier`, `benchmark_role`, `source_version`, `retrieved_at`, `raw_file_path`, `raw_row_or_url`, `transformation_id`, `record_status`.

---

### 2. MFP Source Claim Schema
- **File path**: `data/curated/source_claims.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Source Claim`
- **Purpose**: Normalizes per-source categorical claims into discrete rows, enforcing exact UniProt accession formatting, raw claim value preservation, and operational status mapping (`confirmed`, `predicted`, `excluded_likely`, `unresolved`).
- **Target artifacts**:
  - `data/interim/source_claims_moondb.csv` (351 rows).
  - `data/interim/source_claims_plantmp.csv` (112 rows).
- **Governing contract & status**: `MFPB_0_8_SOURCE_CLAIMS_CONTRACT_V0` (`docs/source-claims-contract.md`). **Active / Committed Baseline**.
- **Production integration status**: Fully integrated as intermediate claim inputs for MoonDB and PlantMP in the catalog build pipeline.
- **Known producers**:
  - `scripts/build_source_claims_moondb.py` (`src/mfp_bibliography/moondb_claims.py`).
  - `scripts/build_source_claims_plantmp.py` (`src/mfp_bibliography/plantmp_claims.py`).
- **Known validators**:
  - `src/mfp_bibliography/validation.py` (`_check_source_claims_schema` and row-level validator).
  - Executable check: `PYTHONPATH=src python3 scripts/validate_repository.py`.
  - Test suite: `tests/test_source_claims.py`, `tests/test_source_claim_policy.py`.
- **Required fields**: `claim_id`, `source_id`, `source_record_id`, `uniprot_id`, `protein_name_raw`, `organism_raw`, `raw_claim_field`, `raw_claim_value`, `operational_status`, `primary_target_eligible`, `control_eligible`, `raw_file_path`, `raw_row_or_url`, `source_version`, `retrieved_at`, `transformation_id`, `record_status`, `notes`.

---

### 3. MFP Effective Status Aggregation Record Schema
- **File path**: `data/curated/effective_status.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Effective Status Aggregation Record`
- **Purpose**: Governs derived per-UniProt aggregation records, combining multiple source claims for a given UniProt ID into a single highest-precedence operational status (`curated` > `predicted` > `excluded_likely` > `unresolved`).
- **Target artifacts**: `data/interim/effective_status_moondb_plantmp.csv`.
- **Governing contract & status**: `MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0` (`docs/effective-status-contract.md`). **Active / Committed Derived Baseline**.
- **Production integration status**: Derived interim artifact; not directly emitted as a table in catalog candidate v0.3.0 (which emits `mfp_assertions.csv` per source observation).
- **Known producers**: `scripts/generate_effective_status_moondb_plantmp.py` (`src/mfp_bibliography/effective_status.py`).
- **Known validators**:
  - Test suite: `tests/test_effective_status.py`, `tests/test_audit_moondb_plantmp_snapshot.py`.
- **Required fields**: `uniprot_id`, `effective_status`, `source_ids`, `claim_ids`, `status_set`, `has_curated_claim`, `has_predicted_claim`, `has_excluded_likely_claim`, `has_unresolved_claim`, `claim_count`, `source_count`, `aggregation_policy_id`, `transformation_id`, `record_status`, `notes`.

---

### 4. MFP Functional Claim Schema
- **File path**: `data/curated/functional_claims.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Functional Claim`
- **Purpose**: Multiplicity-preserving relational model for discrete functional statements extracted from source records. Replaces ad-hoc 2-facet binary slot models (`BP1/MF1/CC1` vs `BP2/MF2/CC2`) with a flexible one-to-many claim architecture.
- **Target artifacts**:
  - `data/interim/pilot/functional_claims_pilot.csv` (20-record empirical cohort).
  - `data/interim/pilot/multitask_slice/functional_claims_slice.csv` (6-record MultitaskProtDB-II slice).
- **Governing contract & status**: Scheme `MFPB_FUNCTIONAL_CLAIM_V1`. **Experimental SDD Pilot Contract** under proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md) Level 2.
- **Production integration status**: **Not integrated into candidate v0.3.0**. Release candidate v0.3.0 preserves function text as uninterpreted raw strings in `mfp_source_records.csv`; discrete functional claim extraction is isolated to pilot packages.
- **Known producers**:
  - `scripts/build_functional_claims_pilot.py`.
  - `scripts/build_multitask_slice.py`.
  - Adapters: `src/mfp_bibliography/functional_claims_plantmp.py`, `functional_claims_multitask.py`, `functional_claims_moonprot.py`.
- **Known validators**:
  - Test suites: `tests/test_functional_contracts.py`, `tests/test_functional_claims_plantmp.py`, `tests/test_functional_claims_multitask.py`, `tests/test_functional_claims_moonprot.py`, `tests/test_build_multitask_slice.py`.
- **Required fields**: `claim_id`, `protein_id`, `source_id`, `source_record_id`, `claim_index`, `claim_role_raw`, `raw_claim_field`, `raw_claim_value`, `claim_assertion_type`, `source_go_ids`, `source_go_aspects`, `source_ec_number`, `linked_reference_ids`, `record_reference_ids`, `raw_file_path`, `raw_row_or_url`, `extraction_method`, `claim_status`, `notes`.

---

### 5. MFP Functional Coverage Schema
- **File path**: `data/curated/functional_coverage.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Functional Coverage`
- **Purpose**: Enforces 100% denominator completeness across all source records in a functional extraction cohort, tracking extracted claim counts and explicit coverage statuses (`fully_extracted`, `partially_extracted`, `no_statements_found`, `unresolved_identity`).
- **Target artifacts**:
  - `data/interim/pilot/functional_coverage_pilot.csv`.
  - `data/interim/pilot/multitask_slice/functional_coverage_slice.csv`.
- **Governing contract & status**: Scheme `MFPB_FUNCTIONAL_COVERAGE_V1`. **Experimental SDD Pilot Contract** under proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md) Level 2.
- **Production integration status**: **Not integrated into candidate v0.3.0**.
- **Known producers**: `scripts/build_functional_claims_pilot.py`, `scripts/build_multitask_slice.py`.
- **Known validators**:
  - Test suites: `tests/test_functional_contracts.py`, `tests/test_functional_claims_plantmp.py`, `tests/test_functional_claims_multitask.py`, `tests/test_functional_claims_moonprot.py`.
- **Required fields**: `source_record_id`, `protein_id`, `source_id`, `claims_extracted_count`, `coverage_status`, `metadata_annotation_raw`, `notes`.

---

### 6. MFP Source GO Annotation Schema
- **File path**: `data/curated/source_go_annotations.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Source GO Annotation`
- **Purpose**: Structurally decomposes source-explicit Gene Ontology terms, aspects (`molecular_function`, `biological_process`, `cellular_component`), and evidence codes without inferring ungrounded function-compartment links or contextual triplets.
- **Target artifacts**:
  - `data/interim/pilot/source_go_annotations_pilot.csv`.
  - `data/interim/pilot/multitask_slice/source_go_annotations_slice.csv`.
- **Governing contract & status**: Scheme `MFPB_SOURCE_GO_ANNOTATION_V1`. **Experimental SDD Pilot Contract** under proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md) Level 2.
- **Production integration status**: **Not integrated into candidate v0.3.0**. Release candidate v0.3.0 preserves GO text verbatim; structured GO decomposition is isolated to pilot packages.
- **Known producers**: `scripts/build_functional_claims_pilot.py`, `scripts/build_multitask_slice.py`.
- **Known validators**:
  - Test suites: `tests/test_source_go_annotations_contract.py`, `tests/test_functional_claims_plantmp.py`, `tests/test_functional_claims_multitask.py`, `tests/test_build_multitask_slice.py`.
- **Required fields**: `annotation_id`, `protein_id`, `source_id`, `source_record_id`, `claim_id`, `source_field`, `annotation_index`, `raw_annotation_text`, `go_id`, `go_aspect`, `term_name`, `evidence_raw`, `annotation_status`, `notes`.

---

### 7. MFP Effective Status Snapshot Manifest Schema (Interim Reporting)
- **File path**: `data/interim/reports/effective_status_snapshot.schema.json`
- **Metaschema**: `https://json-schema.org/draft/2020-12/schema`
- **Title**: `MFP Effective Status Snapshot Manifest`
- **Purpose**: Validates the metadata manifest documenting locally generated derived effective-status snapshots, recording input files, SHA-256 hashes, input/output record counts, and status breakdowns.
- **Target artifacts**: `data/interim/reports/effective_status_moondb_plantmp_snapshot.json`.
- **Governing contract & status**: `MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT`. **Active / Committed Derived Baseline**.
- **Production integration status**: Internal reporting and verification manifest for the MoonDB + PlantMP effective-status snapshot.
- **Known producers**: `scripts/generate_effective_status_moondb_plantmp.py`.
- **Known validators**:
  - Audit script: `scripts/audit_moondb_plantmp_snapshot.py`.
  - Test suite: `tests/test_audit_moondb_plantmp_snapshot.py`.
- **Required fields**: `snapshot_id`, `generated_at`, `schema_version`, `aggregation_policy_id`, `transformation_id`, `input_files`, `input_total_claims`, `input_claims_by_source`, `output_path`, `output_sha256`, `output_record_count`, `effective_status_counts`, `exclusions_count`, `reproducibility_statement`.
