# Implementation Plan: Three-Source Catalog Inventory & Biological Identity Audit

- **Document ID**: `PLAN-THREE-SOURCE-INVENTORY-AUDIT-001`
- **Feature Directory**: `specs/three-source-inventory-audit/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Implementation Plan; Staged Execution Strategy)
- **Status**: **Draft Plan — Pending Human Review & Authorization to Implement**
- **Baseline Git HEAD**: `f9d9fba58a5a03a949c346a5956b8795b312b24d`
- **Specification Reference**: [`specs/three-source-inventory-audit/spec.md`](spec.md)
- **Roadmap Reference**: [`docs/roadmap/pilot-to-three-source-validation-roadmap.md`](../../docs/roadmap/pilot-to-three-source-validation-roadmap.md) (Phase B, `TASK-EXT-04` through `TASK-EXT-07`)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Architectural Strategy & Phased Stages

This plan outlines the staged, gated approach for implementing and executing the Three-Source Catalog Inventory & Biological Identity Audit specified in [`spec.md`](spec.md).

To prevent accidental modification of existing production code or catalog releases, the implementation is organized into four sequential stages, separated by explicit human authorization gates:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              STAGED EXECUTION ARCHITECTURE                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [STAGE 1: CODE, SCHEMAS & SYNTHETIC TESTS] ──► Isolated module, schemas, runner &     │
│                                                 Tier A mock tests (no pipeline run)    │
│                    │                                                                   │
│                    ▼ (GATE 2: CODE REVIEW & APPROVAL)                                  │
│  [STAGE 2: TECHNICAL CODE COMMIT]           ──► Git commit landing code, tests &       │
│                                                 both JSON output schemas               │
│                    │                                                                   │
│                    ▼ (GATE 3: EXECUTION AUTHORIZATION)                                 │
│  [STAGE 3: READ-ONLY AUDIT RUN]             ──► Offline execution on candidate v0.3.0  │
│                                                 tables; tabular outputs & manifest     │
│                    │                                                                   │
│                    ▼ (GATE 4: SCIENTIFIC REVIEW & CLOSURE)                             │
│  [STAGE 4: SYNTHESIS & REPORT]              ──► Human review, report publication &      │
│                                                 closeout narrative                     │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Reuse & Existing Architecture Mapping

To maximize reproducibility and minimize code duplication, the audit engine reuses existing, tested library modules from `src/mfp_bibliography/`:

| Subsystem | Existing Module / Function | Path in Repository | Reused Functionality |
|---|---|---|---|
| **Cryptographic Integrity** | `compute_file_sha256`, `verify_manifest_digests` | [`src/mfp_bibliography/raw_input_verification.py`](../../src/mfp_bibliography/raw_input_verification.py) | Offline SHA-256 verification of inputs and output manifests |
| **Run Provenance** | `build_run_manifest`, `validate_output_inventory` | [`src/mfp_bibliography/provenance.py`](../../src/mfp_bibliography/provenance.py) | Generating deterministic execution manifests |
| **Identity Resolution** | `derive_protein_id_v1`, `validate_uniprot_accession` | [`src/mfp_bibliography/normalization.py`](../../src/mfp_bibliography/normalization.py) | Validating UniProtKB regex and checking deterministic hashes |
| **Claims Policies** | `load_claim_policy`, `validate_claim_schema` | [`src/mfp_bibliography/source_claims.py`](../../src/mfp_bibliography/source_claims.py) | Validating assertions against source claim rules |
| **Ontology Mapping** | `load_go_aspect_lookup` | [`src/mfp_bibliography/go_aspect_enrichment.py`](../../src/mfp_bibliography/go_aspect_enrichment.py) | Loading `go.obo` snapshot and resolving active terms vs alt_ids |
| **Multitask Ingestion** | `load_source_records`, `classify_reference` | [`src/mfp_bibliography/multitaskprotdb_ii_records.py`](../../src/mfp_bibliography/multitaskprotdb_ii_records.py) | Cross-checking Multitask raw table fields |
| **PlantMP Extraction** | `extract_plantmp_row_records`, `parse_plantmp_go_field` | [`src/mfp_bibliography/functional_claims_plantmp.py`](../../src/mfp_bibliography/functional_claims_plantmp.py) | Parsing plant GO terms and function fields |
| **MoonProt Parsing** | `parse_moonprot_go_annotations` | [`src/mfp_bibliography/functional_claims_moonprot.py`](../../src/mfp_bibliography/functional_claims_moonprot.py) | Parsing free-text GO strings in MoonProt |

---

## 3. Proposed New Components (Future Implementation)

The audit requires dedicated components and schemas, to be authored only after Gate 1 authorization:

### 3.1 Output JSON Schemas
- `data/curated/schemas/three_source_inventory_summary.schema.json`: Structural contract for summary metrics table.
- `data/curated/schemas/three_source_quarantine_register.schema.json`: Structural contract for quarantine table (one row per incident event; compound primary key `(source_name, source_record_id, row_locator, primary_reason_code)` with stable `row_locator` for key collision tracking and deterministic detail aggregation).

### 3.2 Audit Calculation Engine (`src/mfp_bibliography/three_source_auditor.py`)
- **Role**: Pure library module containing audit calculation logic, disjoint set partitioning, referential integrity checkers, and multiplicity categorizers.
- **Architectural Rules**:
  * *Referential Key*: Enforces compound key `(source_name, source_record_id)` as fallback for all record-level references.
  * *Scoped Integrity*: Bounds referential integrity checks to the perimeter of the three target sources (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`) before asserting table integrity.
  * *Row Conservation & Key Uniqueness*: Enforces total row conservation $N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$ ($1,508$, $1,452$, $1,179$ as empirical `v0.3.0` baselines). Strictly separates loaded physical rows ($N_{\text{loaded\_rows}}$), distinct keys ($N_{\text{unique\_keys}}$), accounted physical rows ($N_{\text{accounted\_rows}}$), affected source–record keys ($N_{\text{affected\_keys}}$), and logged incidents ($N_{\text{incidents}}$). Validates key uniqueness separately; retains all colliding rows without deduplication, recording stable `row_locator` values (`<artifact_relative_path>#record:<data_record_index>`) and logging key collisions. Distinguishes key collisions from legitimate source–entity multiplicity.
  * *Multiplicity Categorization*: Classifies occurrences into `multi_role_entries`, `isoform_disambiguation`, `re_annotation_history`, and explicit `multiplicity_unclassified` enum when evidence is insufficient. Never collapses records.
  * *Offline Identity*: Separates syntax regex, relational integrity, and biological identity. An active accession does not imply a validated biological identity. In the absence of an authoritative, versioned local reference, classifies biological identity as `biological_identity_unassessed_in_inventory`. Never issues network calls.
  * *Missingness Typology*: Classifies non-evaluable fields into `field_empty`, `observed_absence`, `attribute_unrepresented_in_source`, `extraction_error`, and `check_impossible_missing_dependency`. Never deduces underlying cause solely from an empty field.
  * *Independent Dimensions*: Decouples source vertical slice inclusion from QuickGO capture slice coverage; does not treat absence from source slice as evidence of absence in QuickGO.
  * *Incident Recording & Conformance*: Data incidents are recorded in quarantine register (one row per incident event, compound key `(source_name, source_record_id, row_locator, primary_reason_code)`) with deterministic detail aggregation for duplicate codes on the same occurrence, without row drops. Multiplicity, unclassified multiplicity, or partial verification do not cause non-conformance; structural integrity invariant violations trigger `non_conforming_integrity_violation`.

### 3.3 CLI Runner (`scripts/audit_three_source_inventory.py`)
- **Role**: Command-line entry point enforcing input verification, read-only guarantees, safe staging, and output artifact publishing.
- **CLI Arguments**:
  * `--release-dir`: Path to candidate release (default: `releases/mfp-catalog-candidate-v0.3.0/`).
  * `--ontology-path`: Path to pinned `go.obo` (default: `data/raw/go/go.obo` or fixture).
  * `--raw-dir`: Optional path to raw files directory (default: `data/raw/`).
  * `--output-dir`: Destination path for audit outputs; halts immediately if directory already exists (no overwrite option in this increment; each run requires a new destination).
  * `--allow-missing-raw`: Single coherent degradation policy: records skipped checks, reports MoonProt raw audit as `partial_verification_raw_missing`, and proceeds without runner failure.
- **Publishing & Provenance**:
  * Stages all outputs in a temporary directory on the same filesystem.
  * Validates generated CSV tables against Draft 2020-12 JSON schemas before promotion.
  * Generates `manifest.json` recording **ONLY** Gate 3 outputs (`three_source_inventory_summary.csv`, `three_source_quarantine_register.csv`). Narrative reports from Gate 4 are strictly excluded from the Gate 3 run manifest.
  * Reports execution status (`execution_success`/`failure`), verification coverage (`complete_verification`/`partial_verification_raw_missing`), and integrity conformance (`integrity_conforming`/`non_conforming_integrity_violation`) as independent dimensions in `manifest.json`. An operational failure preventing evaluation never yields `integrity_conforming`.
  * Exact bitwise determinism applies to tabular datasets given identical inputs and CLI arguments. Manifest identity is evaluated by its embedded `input_dataset_digests` and `output_dataset_digests`.

### 3.4 Synthetic Unit Test Suite (`tests/test_three_source_inventory_audit.py`)
- **Role**: Tier A synthetic test suite validating all audit logic in isolated temporary directories using small mocks.
- **Testing Boundary**: Strictly limited to Tier A synthetic tests in isolation. Zero pipeline runs on candidate release tables or full catalog during Gate 1.
- **Test Scenarios**:
  * Complete bijection and inclusion-exclusion verification on mock 3-source inputs.
  * Detection of orphan records, foreign key mismatches, and broken Curated references within scoped perimeter.
  * Key collision test: two physical rows sharing the exact same `(source_name, source_record_id)` key: verifies that (1) both physical rows are preserved in accounting ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}} = 2$), (2) there is exactly one unique source–record key ($N_{\text{unique\_keys}} = 1$), (3) the two physical occurrences have distinct `row_locator` values (`#record:1` vs `#record:2`, where record index counts parsed CSV data records excluding header), and (4) collision incidents are represented in the quarantine register under compound key `(source_name, source_record_id, row_locator, primary_reason_code)` without colliding with each other or dropping either occurrence.
  * Single source record with multiple incidents: verifies that a record triggering two distinct incidents produces two incident rows in the quarantine register while counting as exactly one physical row in total row conservation ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}} = 1$) and exactly one key in affected source–record keys ($N_{\text{affected\_keys}} = 1$).
  * Conformance decoupling: verifies that internal multiplicity and partial verification do not mark the run non-conforming, while structural integrity invariant violations do.
  * Handling of internal multiplicity (asserting that records are never dropped or collapsed).
  * Categorization of missingness (empty field vs observed absence vs missing dependency).
  * Degradation test: clean run and `partial_verification_raw_missing` flag when MoonProt raw HTML directory is absent.

---

## 4. Operational Boundaries & Protection Guards

To ensure non-destructive execution:
1. **Input Immutability**: All input files are opened in read-only mode (`r` with UTF-8 encoding). No script may write to `releases/` or `data/raw/`.
2. **Safe Staging & Destination Non-Existence**:
   - The CLI runner checks that `--output-dir` does not exist prior to execution; halts immediately if it already exists (no overwrite option).
   - Outputs are staged in a temporary working directory on the same filesystem.
   - On unhandled failure, the staging directory is cleaned up immediately, leaving the target directory untouched.
   - Outputs are promoted atomically only after all tables validate against JSON schemas.
3. **No Network Access**: The script strictly operates offline. Any attempt to query UniProt, QuickGO, or external URLs raises a fatal configuration error.
4. **Git Index Preservation**: Gate 2 technical commit requires an index clean of foreign changes (`0` staged files) and preserves existing untracked files and working tree edits.
5. **Policy Thresholds**: The indicative $>5\%$ quarantine threshold is documented as an unapproved proposal and does not block running descriptive audits.

---

## 5. Review & Authorization Gates

| Gate | Milestone | Prerequisites | Authorized Deliverables |
|---|---|---|---|
| **Gate 0** | **Contract & Planning** | Human authorization of roadmap | `spec.md`, `plan.md`, `tasks.md`, `verification.md` [CURRENT PASS] |
| **Gate 1** | **Implementation & Tier A Tests** | Human approval of Gate 0 package | `three_source_inventory_summary.schema.json`, `three_source_quarantine_register.schema.json`, `three_source_auditor.py`, `audit_three_source_inventory.py`, `test_three_source_inventory_audit.py` (Tier A mock tests only; zero pipeline runs) |
| **Gate 2** | **Code Review & Git Commit** | 100% Tier A tests pass; AST valid; index empty (`0` foreign staged files) | Git commit landing implementation code, tests, and both JSON schemas |
| **Gate 3** | **Read-Only Audit Execution** | Gate 2 commit landed; inputs, configuration & execution authorized (findings reviewed in Gate 4); output directory non-existent | Execution of runner; generation of `three_source_inventory_summary.csv`, quarantine register, manifest (Gate 3 tables only) |
| **Gate 4** | **Scientific Review & Closeout** | Gate 3 outputs verified; digests recorded; audit findings reviewed | Publication of `docs/reports/three-source-inventory-audit-report.md`; human sign-off |
