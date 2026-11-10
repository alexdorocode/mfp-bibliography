# Tasks: Functional-Normalization Pilot

- **Document ID**: `TASKS-001-FUNCTIONAL-NORMALIZATION-PILOT`
- **Specification Reference**: [`specs/functional-normalization-pilot/spec.md`](spec.md)
- **Plan Reference**: [`specs/functional-normalization-pilot/plan.md`](plan.md)
- **Status**: Scoped implementation completed for TASK-01, TASK-02, TASK-03, and TASK-04; subsequent tasks unauthorized.
- **Implementation Authorization**: Scoped authorization granted exclusively for **TASK-01, TASK-02, TASK-03, and TASK-04**. Subsequent tasks (TASK-05 to TASK-08) remain **strictly unauthorized** pending human review and approval. ADR-008 remains `Proposed` (not globally accepted).

---

## Task Inventory Overview

| Task ID | Stage | Title | Requirement IDs | Allowed Files | Status / Human Approval | Dependencies |
|---|---|---|---|---|---|---|
| **TASK-01** | P1 | Author Schemas for Claims and Coverage | R-NORM-01, R-NORM-02, R-NORM-04, R-NORM-07 | `data/curated/functional_claims.schema.json`, `data/curated/functional_coverage.schema.json` | **COMPLETED** (Verified via Draft202012Validator) | None |
| **TASK-02** | P1 | Implement Executable Contract Tests | R-NORM-01 to R-NORM-07 | `tests/test_functional_contracts.py`, `tests/fixtures/functional_contracts/` | **COMPLETED** (33 tests passed) | TASK-01 |
| **TASK-03** | P2 | Implement MultitaskProtDB-II Slice Adapter | R-NORM-01, R-NORM-02, R-NORM-03 | `src/mfp_bibliography/functional_claims_multitask.py`, `tests/test_functional_claims_multitask.py`, `tests/fixtures/functional_claims_multitask/` | **COMPLETED** (11 tests passed) | TASK-02 |
| **TASK-04** | P3 | Implement PlantMP Tabular Adapter | R-NORM-01, R-NORM-02, R-NORM-04 | `src/mfp_bibliography/functional_claims_plantmp.py`, `tests/test_functional_claims_plantmp.py`, `tests/fixtures/functional_claims_plantmp/` | **COMPLETED** (39 tests passed) | TASK-03 |
| **TASK-05** | P3 | Implement MoonProt Dynamic Block Adapter | R-NORM-01, R-NORM-02, R-NORM-03 | `src/mfp_bibliography/functional_claims_moonprot.py`, `tests/test_functional_claims_moonprot.py`, `tests/fixtures/functional_claims_moonprot/` | **COMPLETED** (22 tests passed) | TASK-04 |
| **TASK-06** | P3 | Implement MoonDB and MultifacetedProtDB Adapters | R-NORM-04, R-NORM-07 | `src/mfp_bibliography/functional_claims_moondb.py`, `src/mfp_bibliography/functional_coverage_multifaceted.py`, `tests/test_functional_claims_complex.py` | **UNAUTHORIZED** (Awaits human approval) | TASK-05 |
| **TASK-07** | P4 | Implement Pilot Pipeline CLI & Dual Baseline Check | AC-NORM-04, AC-NORM-05, AC-NORM-06 | `scripts/build_functional_claims_pilot.py`, `tests/test_functional_pilot_pipeline.py` | **UNAUTHORIZED** (Awaits human approval) | TASK-06 |
| **TASK-08** | P4 | Execute Integrated Pilot & Produce Validation Report | AC-NORM-05, AC-NORM-06 | `data/interim/pilot/`, `data/interim/reports/` | **UNAUTHORIZED** (Awaits Gate 3 sign-off) | TASK-07 |

---

## Detailed Task Specifications

### Executable Contract Batch (TASK-01 & TASK-02 — COMPLETED)

#### TASK-01: Author Schemas for Claims and Coverage
- **Stage**: P1 (Contract Preparation)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-04`, `R-NORM-07`
- **Status**: **COMPLETED**
- **Allowed Files Created/Modified**:
  - `data/curated/functional_claims.schema.json`
  - `data/curated/functional_coverage.schema.json`
- **Delivered Outcome**:
  - Valid JSON Schemas (Draft 2020-12) defining the relational `functional_claims` and `functional_coverage` models.
  - Enforces required fields, string length constraints (`minLength: 1`), and `additionalProperties: false`.
  - Disallows legacy binary slot fields (`bp1`, `mf1`, `cc1`, `facet_1`).
  - Distinguishes record-level references (`record_reference_ids`) from claim-specific citations (`linked_reference_ids`).
- **Verification Command & Result**:
  ```bash
  python3 -c "import json, jsonschema; [jsonschema.Draft202012Validator.check_schema(json.load(open(p))) for p in ['data/curated/functional_claims.schema.json', 'data/curated/functional_coverage.schema.json']]"
  ```
  *Result: PASSED.*

---

#### TASK-02: Implement Executable Contract Tests
- **Stage**: P1 (Contract Preparation)
- **Requirement IDs**: `R-NORM-01` through `R-NORM-07`
- **Status**: **COMPLETED**
- **Allowed Files Created/Modified**:
  - `tests/test_functional_contracts.py`
  - `tests/fixtures/functional_contracts/`
- **Delivered Outcome**:
  A comprehensive pytest suite covering synthetic positive and negative contract cases:
  1. *Multiplicity*: Single statement and three-or-more statement records pass without slot collapsing.
  2. *Coverage Boundary*: Accession-only records pass coverage schema; numeric float scores are stored as metadata and rejected as functional claims.
  3. *Provenance*: Missing `raw_file_path`, `raw_claim_field`, or other provenance fails validation.
  4. *Reference Granularity*: Disallows promoting record-level references to claim-level support.
  5. *Status Vocabulary*: Accepts `curated`, `predicted`, `unresolved`; rejects arbitrary status strings.
  6. *Foreign Keys*: Synthesizes foreign key mismatch failures against catalog.
  7. *Serialization*: Asserts RFC 4180 CSV round-trip fidelity, null serialization, and delimiter escaping.
  8. *Total Ordering*: Verifies 5-tuple tie-breaking sort key `(protein_id, source_id, source_record_id, claim_index, claim_id)`.
  9. *Total Coverage Ordering*: Verifies 3-tuple sort key `(protein_id, source_id, source_record_id)`.
  10. *Deterministic ID Derivation*: Verifies SHA-256 derivation and dataset collision detection.
  11. *No Co-annotation CC*: Asserts failure on unevidenced cellular component injection.
- **Verification Command & Result**:
  ```bash
  pytest -v tests/test_functional_contracts.py
  ```
  *Result: PASSED (33 passed in 0.17s).*

---

### First Real-Source Vertical Slice (TASK-03 — COMPLETED, EXTENDED & CONSOLIDATED)

#### TASK-03: Implement MultitaskProtDB-II Slice Adapter & Persistent Package
- **Stage**: P2 (First Offline Vertical Slice)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-03`
- **Status**: **COMPLETED, EXTENDED & CONSOLIDATED**
- **Allowed Files Created/Modified**:
  - `data/curated/source_go_annotations.schema.json`
  - `src/mfp_bibliography/functional_claims_multitask.py`
  - `tests/test_source_go_annotations_contract.py`
  - `tests/test_functional_claims_multitask.py`
  - `tests/test_build_multitask_slice.py`
  - `scripts/build_multitask_slice.py`
  - `tests/fixtures/functional_claims_multitask/` (`README.md`, `multitask_real_extract.csv`, `multitask_synthetic_edge_cases.csv`)
  - `data/interim/pilot/multitask_slice/` (`claims.csv`, `source_go_annotations.csv`, `coverage.csv`, `manifest.json`, `verification_report.json`)
- **Delivered Outcome**:
  - Defined bounded contract extension `source_go_annotations.schema.json` (Draft 2020-12) preserving source GO annotations structurally with verbatim raw fragments, evidence codes, and optional claim linkages.
  - Implemented `derive_source_go_annotation_id()` under scheme `MFPB_SOURCE_GO_ANNOTATION_V1`.
  - Extracted separate claim records for `Canonical_Function` and `Moonlighting_function`, preserving source-native roles.
  - Implemented `MultitaskGOAnnotation` preserving tight binding between GO ID, aspect (`BP`, `MF`, `CC`), term name, and evidence code (`IEA`, `IDA`, etc.).
  - Preserved CC explicitly present in `GO_Moon` as a source assertion (e.g. Row 672 / `Q9Y3E5` nucleoplasm) while strictly excluding canonical CC terms from moonlighting claims.
  - Preserved verbatim raw `Reference` strings in `record_reference_ids` without artificial `PMID:` prefix injection (e.g. `24814782`, `11111111, 22222222`, `HIV-1...`), with `linked_reference_ids = None`.
  - Handled records with missing function text but populated GO annotations by preserving structured GO annotations with `claim_id = null` and accounting for unextracted annotations in `coverage["notes"]` without fabricating fake text claims.
  - Handled multiple occurrences, including repeated GO IDs with distinct evidence codes (e.g. `P78901`).
  - Produced 100% denominator coverage records (`coverage_status = "claims_extracted"`, `"no_discrete_functional_statements"`, or `"unresolved_identity"`).
  - Enforced deterministic total ordering: claims sorted by `(protein_id, source_id, source_record_id, claim_index, claim_id)`, annotations sorted by `(protein_id, source_id, source_record_id, source_field, annotation_index, annotation_id)`, and coverage sorted by `(protein_id, source_id, source_record_id)`.
  - Generated persistent, verified six-record package under `data/interim/pilot/multitask_slice/` using `scripts/build_multitask_slice.py`.
  - Proved byte-level reproducibility via independent double generation in temporary directories (100% identical SHA-256 digests across `claims.csv`, `source_go_annotations.csv`, `coverage.csv`, and `manifest.json`).
  - 100% of emitted records validate against Draft 2020-12 JSON Schemas.
- **Verification Commands & Results**:
  ```bash
  PYTHONPATH=src pytest -v tests/test_source_go_annotations_contract.py tests/test_functional_claims_multitask.py tests/test_build_multitask_slice.py
  ```
  *Result: PASSED (67 passed in 0.50s).*
  ```bash
  PYTHONPATH=src python3 scripts/build_multitask_slice.py
  ```
  *Result: PASSED (Status VERIFIED: 6 records, 12 claims, 45 annotations, 6 coverage).*

---

### Capability Expansion (TASK-04 — COMPLETED UNDER BOUNDED AUTHORIZATION)

#### TASK-04: Implement PlantMP Tabular Adapter & Correct Identity Resolution
- **Stage**: P3 (Capability Expansion)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-04`
- **Status**: **COMPLETED & VERIFIED UNDER BOUNDED AUTHORIZATION** (Contract amendment resolved and verified)
- **Allowed Files Created/Modified**:
  - `data/curated/functional_coverage.schema.json`
  - `src/mfp_bibliography/functional_claims_plantmp.py`
  - `tests/test_functional_claims_plantmp.py`
  - `tests/test_functional_contracts.py`
  - `tests/fixtures/functional_claims_plantmp/` (`README.md`, `plantmp_real_extract.csv`, `plantmp_synthetic_edge_cases.csv`)
- **Delivered Outcome**:
  - Implemented source-grounded bounded PlantMP adapter adhering to relational claims model (`functional_claims.schema.json`), structured source GO annotations model (`source_go_annotations.schema.json`), and coverage model (`functional_coverage.schema.json`).
  - **Authoritative Input Convention**: Uses `PlantMP_all.csv` (112 rows, SHA-256 `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`) as pinned in `source_manifest.csv`. Rejects combining overlapping raw exports without explicit deduplication and provenance rules.
  - **Source-Native Roles & Pre-Split Aspects**: Preserves verbatim role names (`canonical`, `moonlighting`) and raw claim fields (`canonical_function_bp`, `canonical_function_mf`, `moonlighting_function_bp`, `moonlighting_function_mf`).
  - **No Independent Function Assumption**: Pre-partitioned BP and MF statements are grouped under native role labels via `group_claims_by_role()` without assuming that BP and MF fields represent independent biological functions.
  - **Curation Tier Policy & Status Handling**:
    - `confirmed` -> `claim_assertion_type = "curated"`, native status recorded in `notes = "source_type: confirmed"`.
    - `likely` -> `claim_assertion_type = "unresolved"` with `notes = "source_type: likely; policy_status: excluded_likely"`. Strictly enforces that "likely" candidate status is never silently promoted to curated.
    - `predicted` -> `claim_assertion_type = "predicted"`, native status recorded in `notes = "source_type: predicted"`.
    - Unmapped / disputed -> `claim_assertion_type = "unresolved"`.
  - **Record-Level References**: Preserves verbatim `pubmed_id` strings (including bare numeric PMIDs, comma-separated lists, and annotated strings like `26638082 (Homolog of POT7)`) in `record_reference_ids` without synthetic `PMID:` prefix injection. `linked_reference_ids` remains `None` (record-level citations are not promoted to claim support).
  - **Source-Explicit GO Annotations**: Emits structured annotations under `MFPB_SOURCE_GO_ANNOTATION_V1` with explicit GO IDs and aspects (`BP`, `MF`). Unavailable metadata (`term_name`, `evidence_raw`, `notes`) remains `None`. No cellular components (CC) are inferred, and no contextual triplets are constructed.
  - **Missing Text with GO Data Accounting**: For records with empty functional text descriptions but populated GO fields (e.g. synthetic edge case 5), emits structured annotations with `claim_id = None` and notes unextracted annotations in `coverage["notes"]` without fabricating fake text claims.
  - **Identity Resolution Defect Correction & Referential Integrity**:
    - Removed fabricated sentinel entity `MFP:U:0000000000000000`. Emits `protein_id = None` on `coverage_status = "unresolved_identity"` so that no non-existent entities are fabricated.
    - Stopped silent promotion: when `catalog_lookup` is omitted and `allow_unanchored=False` (default), rows are not promoted to resolved entities; they are marked `unresolved_identity`. When `catalog_lookup` is supplied, syntactically valid accessions absent from the catalog are marked `unresolved_identity`.
    - Verified catalog presence and linkage agreement: verified that catalog protein entity matches the entity derived from row accession, rejecting mismatched linkages.
    - Preserved legitimate shared entities across duplicate source records (Orders 62 and 68).
    - Added negative tests covering missing accession, malformed accession, valid accession absent from catalog, mismatched linkage, and multiple unresolved records not collapsed into one fake entity.
    - Added catalog loader `load_plantmp_catalog_lookup()` verifying all 112 records load from catalog.
  - **Coverage Schema Conditional Nullability Amendment (Completed)**:
    - Amended `data/curated/functional_coverage.schema.json` via Draft 2020-12 conditional validation:
      - `protein_id` kept in `required`.
      - When `coverage_status == "unresolved_identity"`, `protein_id` must be `null`.
      - For all other coverage statuses, `protein_id` must match `^MFP:(U:[0-9a-f]{16}|F:[A-Za-z0-9_]+:[0-9a-f]{16})$`.
      - Missing property and empty string rejected.
    - Contract test suite updated with syntax tests (valid and invalid cases) and referential-integrity tests (rejecting well-formed IDs absent from catalog). Blocker fully resolved.
  - **100% Denominator Coverage**: Emits `coverage_status = "claims_extracted"`, `"no_discrete_functional_statements"`, or `"unresolved_identity"` for every input record.
  - **Deterministic Total Ordering**: Enforces 5-tuple claim sorting `(protein_id, source_id, source_record_id, claim_index, claim_id)`, 6-tuple annotation sorting `(protein_id, source_id, source_record_id, source_field, annotation_index, annotation_id)`, and 3-tuple coverage sorting `(protein_id or "", source_id, source_record_id)`.
- **Verification Command & Result**:
  ```bash
  PYTHONPATH=src pytest -v tests/test_functional_claims_plantmp.py tests/test_functional_contracts.py
  ```
  *Result: PASSED (39 passed in plantmp, 37 passed in contracts).*

---

#### TASK-05: Implement MoonProt Dynamic Block Adapter
- **Stage**: P3 (Capability Expansion)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-03`
- **Status**: **COMPLETED & VERIFIED UNDER BOUNDED AUTHORIZATION**
- **Allowed Files Created/Modified**:
  - `src/mfp_bibliography/functional_claims_moonprot.py`
  - `tests/test_functional_claims_moonprot.py`
  - `tests/fixtures/functional_claims_moonprot/` (`README.md`, `real_mpid_*.html`, `synthetic_mpid_*.html`)
- **Delivered Outcome**:
  - Implemented source-grounded bounded MoonProt adapter adhering to relational claims model (`functional_claims.schema.json`), structured source GO annotations model (`source_go_annotations.schema.json`), and coverage model (`functional_coverage.schema.json`).
  - **Reusable Existing Parser**: Reuses `MoonProtRecord` and parser logic from `src/mfp_bibliography/moonprot_parser.py` without creating a redundant HTML parser.
  - **Dynamic Function Blocks**: Preserves one claim per explicit function block in `functions` (`functions[0].description`, `functions[1].description`, ...) without assuming a fixed two-function structure (verified on real-source $K=0$ case MPID 288, $K=1$, $K=2$, and $K=3$ synthetic cases).
  - **Function-Level References**: PMIDs extracted directly from function blocks are preserved in `linked_reference_ids` with standard `PMID:` prefix; `record_reference_ids` remains `None` (MoonProt citations are function-specific).
  - **No Triplet or Compartment Inference**: Cellular location text is preserved in claim `notes` (`cellular_location: ...`) without inferring cellular component (CC) terms or constructing contextual triplets.
  - **Protein-Level GO Terms Preservation**: Top-level `GO terms` in MoonProt HTML apply to the protein as a whole and are NOT distributed across individual function claims. Instead, they are emitted in `source_go_annotations` with `claim_id = None`, preserving them structurally.
  - **Catalog Linkage & Fallback Entities**: Authoritative catalog linkage via `load_moonprot_catalog_lookup()` (702 records in `mfp_source_records.csv`). Supports both canonical UniProt entities (`MFP:U:...`) and valid catalog fallback identities (`MFP:F:SRC_MOONPROT:...`).
  - **Honest Null on Unresolved Identity**: Missing/malformed accessions or uncataloged records emit `protein_id = None` and `coverage_status = "unresolved_identity"` with 0 claims/annotations, fully adhering to Draft 2020-12 coverage contract without fabricating sentinels.
  - **Deterministic Total Ordering**: Enforces 5-tuple claim sorting `(protein_id, source_id, source_record_id, claim_index, claim_id)`, 6-tuple annotation sorting `(protein_id, source_id, source_record_id, source_field, annotation_index, annotation_id)`, and 3-tuple coverage sorting `(protein_id or "", source_id, source_record_id)`.
- **Verification Command & Result**:
  ```bash
  PYTHONPATH=src pytest -v tests/test_functional_claims_moonprot.py
  ```
  *Result: PASSED (22 passed in 0.42s).*

---

### Subsequent Incremental Tasks (Awaiting Authorization & Sign-off)

> [!IMPORTANT]
> The following tasks (TASK-06 to TASK-08) remain **STRICTLY UNAUTHORIZED / DEFERRED**. No code, adapters, or pipeline modifications may be undertaken without explicit human approval.

---

#### TASK-06: Implement MoonDB and MultifacetedProtDB Adapters
- **Stage**: P3 (Capability Expansion)
- **Requirement IDs**: `R-NORM-04`, `R-NORM-07`
- **Status**: **UNAUTHORIZED**
- **Allowed Files**:
  - `src/mfp_bibliography/functional_claims_moondb.py`
  - `src/mfp_bibliography/functional_coverage_multifaceted.py`
  - `tests/test_functional_claims_complex.py`
- **Dependencies**: TASK-05
- **Human Approval Required**: Yes.

---

#### TASK-07: Implement Pilot Pipeline CLI & Dual Baseline Check
- **Stage**: P4 (Integrated Review)
- **Requirement IDs**: `AC-NORM-04`, `AC-NORM-05`, `AC-NORM-06`
- **Status**: **UNAUTHORIZED**
- **Allowed Files**:
  - `scripts/build_functional_claims_pilot.py`
  - `tests/test_functional_pilot_pipeline.py`
- **Dependencies**: TASK-06
- **Human Approval Required**: Yes.

---

#### TASK-08: Execute Integrated Pilot & Produce Validation Report
- **Stage**: P4 (Integrated Review)
- **Requirement IDs**: `AC-NORM-05`, `AC-NORM-06`
- **Status**: **UNAUTHORIZED**
- **Allowed Files**:
  - `data/interim/pilot/functional_claims_pilot.csv`
  - `data/interim/pilot/functional_coverage_pilot.csv`
  - `data/interim/reports/functional_claims_pilot_report.json`
- **Dependencies**: TASK-07
- **Human Approval Required**: **Yes (Gate 3)** — Formal human review and sign-off on the completed Tier A pilot.
