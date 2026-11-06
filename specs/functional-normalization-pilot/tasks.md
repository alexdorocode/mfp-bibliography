# Tasks: Functional-Normalization Pilot

- **Document ID**: `TASKS-001-FUNCTIONAL-NORMALIZATION-PILOT`
- **Specification Reference**: [`specs/functional-normalization-pilot/spec.md`](spec.md)
- **Plan Reference**: [`specs/functional-normalization-pilot/plan.md`](plan.md)
- **Status**: Scoped implementation completed for TASK-01, TASK-02, and TASK-03; subsequent tasks unauthorized.
- **Implementation Authorization**: Scoped authorization granted exclusively for **TASK-01, TASK-02, and TASK-03**. Subsequent tasks (TASK-04 to TASK-08) remain **strictly unauthorized** pending human review and approval. ADR-008 remains `Proposed` (not globally accepted).

---

## Task Inventory Overview

| Task ID | Stage | Title | Requirement IDs | Allowed Files | Status / Human Approval | Dependencies |
|---|---|---|---|---|---|---|
| **TASK-01** | P1 | Author Schemas for Claims and Coverage | R-NORM-01, R-NORM-02, R-NORM-04, R-NORM-07 | `data/curated/functional_claims.schema.json`, `data/curated/functional_coverage.schema.json` | **COMPLETED** (Verified via Draft202012Validator) | None |
| **TASK-02** | P1 | Implement Executable Contract Tests | R-NORM-01 to R-NORM-07 | `tests/test_functional_contracts.py`, `tests/fixtures/functional_contracts/` | **COMPLETED** (33 tests passed) | TASK-01 |
| **TASK-03** | P2 | Implement MultitaskProtDB-II Slice Adapter | R-NORM-01, R-NORM-02, R-NORM-03 | `src/mfp_bibliography/functional_claims_multitask.py`, `tests/test_functional_claims_multitask.py`, `tests/fixtures/functional_claims_multitask/` | **COMPLETED** (11 tests passed) | TASK-02 |
| **TASK-04** | P3 | Implement PlantMP Tabular Adapter | R-NORM-01, R-NORM-02, R-NORM-04 | `src/mfp_bibliography/functional_claims_plantmp.py`, `tests/test_functional_claims_plantmp.py` | **UNAUTHORIZED** (Awaits human approval) | TASK-03 |
| **TASK-05** | P3 | Implement MoonProt Dynamic Block Adapter | R-NORM-01, R-NORM-02, R-NORM-03 | `src/mfp_bibliography/functional_claims_moonprot.py`, `tests/test_functional_claims_moonprot.py` | **UNAUTHORIZED** (Awaits human approval) | TASK-04 |
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

### First Real-Source Vertical Slice (TASK-03 — COMPLETED)

#### TASK-03: Implement MultitaskProtDB-II Slice Adapter
- **Stage**: P2 (First Offline Vertical Slice)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-03`
- **Status**: **COMPLETED**
- **Allowed Files Created**:
  - `src/mfp_bibliography/functional_claims_multitask.py`
  - `tests/test_functional_claims_multitask.py`
  - `tests/fixtures/functional_claims_multitask/` (`README.md`, `multitask_real_extract.csv`, `multitask_synthetic_edge_cases.csv`)
- **Delivered Outcome**:
  - Extracted separate claim records for `Canonical_Function` and `Moonlighting_function`, preserving source-native roles.
  - Parsed source-explicit GO lines and native aspects (`C:`, `F:`, `P:`, or text descriptors) without querying external ontologies or databases.
  - Kept row-level references strictly in `record_reference_ids`, with `linked_reference_ids = None`.
  - Produced 100% denominator coverage records (`coverage_status = "claims_extracted"`, `"no_discrete_functional_statements"`, or `"unresolved_identity"`).
  - Enforced deterministic total ordering: claims sorted by `(protein_id, source_id, source_record_id, claim_index, claim_id)` and coverage by `(protein_id, source_id, source_record_id)`.
  - 100% of emitted records validate against Draft 2020-12 JSON Schemas.
- **Verification Command & Result**:
  ```bash
  PYTHONPATH=src pytest -v tests/test_functional_claims_multitask.py
  ```
  *Result: PASSED (11 passed in 0.05s).*

---

### Subsequent Incremental Tasks (Awaiting Authorization & Sign-off)

> [!IMPORTANT]
> The following tasks (TASK-04 to TASK-08) are **STRICTLY UNAUTHORIZED**. No code, adapters, or pipeline modifications may be undertaken without explicit human approval.

#### TASK-04: Implement PlantMP Tabular Adapter
- **Stage**: P3 (Capability Expansion)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-04`
- **Status**: **UNAUTHORIZED**
- **Allowed Files**:
  - `src/mfp_bibliography/functional_claims_plantmp.py`
  - `tests/test_functional_claims_plantmp.py`
- **Dependencies**: TASK-03
- **Human Approval Required**: Yes.

---

#### TASK-05: Implement MoonProt Dynamic Block Adapter
- **Stage**: P3 (Capability Expansion)
- **Requirement IDs**: `R-NORM-01`, `R-NORM-02`, `R-NORM-03`
- **Status**: **UNAUTHORIZED**
- **Allowed Files**:
  - `src/mfp_bibliography/functional_claims_moonprot.py`
  - `tests/test_functional_claims_moonprot.py`
- **Dependencies**: TASK-04
- **Human Approval Required**: Yes.

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
