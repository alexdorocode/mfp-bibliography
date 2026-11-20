# Tasks: Three-Source Catalog Inventory & Biological Identity Audit

- **Document ID**: `TASKS-THREE-SOURCE-INVENTORY-AUDIT-001`
- **Feature Directory**: `specs/three-source-inventory-audit/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Task Inventory; Scoped Write Boundaries)
- **Status**: **Gate 0 Completed; Gates 1–4 Strictly Deferred Pending Authorization**
- **Baseline Git HEAD**: `f9d9fba58a5a03a949c346a5956b8795b312b24d`
- **Specification Reference**: [`specs/three-source-inventory-audit/spec.md`](spec.md)
- **Plan Reference**: [`specs/three-source-inventory-audit/plan.md`](plan.md)
- **Roadmap Reference**: [`docs/roadmap/pilot-to-three-source-validation-roadmap.md`](../../docs/roadmap/pilot-to-three-source-validation-roadmap.md) (Phase B, `TASK-EXT-04` through `TASK-EXT-07`)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Task Inventory & Authorization Gating

Every task declared below is bound to an explicit write boundary and governed by a strict authorization gate. No implementation, execution, or commit may proceed without explicit human sign-off at each gate.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AUDIT IMPLEMENTATION TASK INVENTORY                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ GATE 0: DOCUMENTATION CONTRACT & PLANNING (CURRENT INCREMENT)                          │
│ • spec.md, plan.md, tasks.md, verification.md                              [COMPLETED] │
│                                                                                        │
│ GATE 1: IMPLEMENTATION, SCHEMAS & SYNTHETIC TESTS (DEFERRED PENDING AUTH)              │
│ • TASK-AUD-01: Author Audit Schemas & Output Contracts                     [DEFERRED]  │
│ • TASK-AUD-02: Implement Core Audit Calculation Engine                     [DEFERRED]  │
│ • TASK-AUD-03: Implement CLI Audit Runner with Read-Only Guards            [DEFERRED]  │
│ • TASK-AUD-04: Author Tier A Synthetic Unit Test Suite (Mocks Only)        [DEFERRED]  │
│                                                                                        │
│ GATE 2: CODE REVIEW & TECHNICAL COMMIT (DEFERRED PENDING AUTH)                         │
│ • TASK-AUD-05: Technical Code Review & Pre-Commit Verification             [DEFERRED]  │
│                                                                                        │
│ GATE 3: OFFLINE AUDIT EXECUTION (DEFERRED PENDING AUTH)                                │
│ • TASK-AUD-06: Execute Read-Only Audit on Candidate v0.3.0 Release         [DEFERRED]  │
│                                                                                        │
│ GATE 4: SCIENTIFIC AUDIT REVIEW & CLOSEOUT (DEFERRED PENDING AUTH)                     │
│ • TASK-AUD-07: Author Descriptive Report & Quarantine Register Review      [DEFERRED]  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Task Specifications

### Gate 0: Specification & Planning (Current Increment)

#### `TASK-AUD-00`: Specification Package Authoring & Consistency Alignment
- **Roadmap Link**: Corresponds to `TASK-EXT-04`.
- **Preconditions**: Human authorization to draft SDD package; HEAD at `f9d9fba58a...`.
- **Write Boundaries**:
  * `specs/three-source-inventory-audit/spec.md`
  * `specs/three-source-inventory-audit/plan.md`
  * `specs/three-source-inventory-audit/tasks.md`
  * `specs/three-source-inventory-audit/verification.md`
- **Deliverables**: Complete, reviewed Level 5 specification package aligning offline identity, multiplicity, independent dimensions, error distinction, denominator conservation, reproducibility contracts, and gate scope.
- **Stop Criteria**: Stop if any target path collides with existing uncommitted work.
- **Responsible Role**: Software Architect & Scientific Auditor.
- **Status**: **Completed** (in current turn).

---

### Gate 1: Implementation, Schemas & Tier A Synthetic Tests (Deferred)

#### `TASK-AUD-01`: Author Audit Schemas & Output Contracts
- **Roadmap Link**: Subtask of `TASK-EXT-04`.
- **Preconditions**: Gate 0 approved; explicit human authorization for Gate 1 implementation.
- **Write Boundaries**:
  * `data/curated/schemas/three_source_inventory_summary.schema.json`
  * `data/curated/schemas/three_source_quarantine_register.schema.json`
- **Deliverables**: Draft 2020-12 JSON schemas defining structure, required columns, and types for summary and quarantine tables (quarantine schema specifying one row per incident event, compound primary key `(source_name, source_record_id, row_locator, primary_reason_code)` with `row_locator` field for key collision tracking, and deterministic detail aggregation).
- **Stop Criteria**: Stop if schema validation fails against Draft 2020-12 meta-schema.
- **Responsible Role**: Data Quality Specialist.
- **Status**: **Deferred** (requires Gate 1 authorization).

#### `TASK-AUD-02`: Implement Core Audit Calculation Engine
- **Roadmap Link**: Corresponds to `TASK-EXT-05` and `TASK-EXT-07`.
- **Preconditions**: `TASK-AUD-01` completed.
- **Write Boundaries**:
  * `src/mfp_bibliography/three_source_auditor.py`
- **Deliverables**: Pure Python library module implementing:
  * Compound key fallback `(source_name, source_record_id)`.
  * Primary row conservation invariant $N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$ without prior deduplication.
  * Strict separation of loaded physical rows ($N_{\text{loaded\_rows}}$), distinct keys ($N_{\text{unique\_keys}}$), accounted physical rows ($N_{\text{accounted\_rows}}$), affected source–record keys ($N_{\text{affected\_keys}}$), and logged incidents ($N_{\text{incidents}}$).
  * Separate key uniqueness validation: detects key collisions and records stable `row_locator` values (`<artifact_relative_path>#record:<data_record_index>`) without dropping colliding rows.
  * Separation of key collisions from legitimate source–entity multiplicity.
  * Scoped referential integrity validation restricted to the 3-source perimeter (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`).
  * Disjoint Venn partitioning and inclusion-exclusion verification.
  * Internal multiplicity categorization with `multiplicity_unclassified` enum; complete row preservation.
  * Offline identity resolution: syntax regex, relational consistency, and `biological_identity_unassessed_in_inventory` without local versioned references; active accession does not imply validated biological identity; zero network calls.
  * Typology of missingness (`field_empty`, `observed_absence`, `attribute_unrepresented_in_source`, `extraction_error`, `check_impossible_missing_dependency`).
  * Incident compound key `(source_name, source_record_id, row_locator, primary_reason_code)` with deterministic detail aggregation for duplicate findings on the same occurrence.
  * Evaluability defined per check; census reports affected source–record keys ($N_{\text{affected\_keys}}$) deduplicated by distinct source–record key, strictly distinguished from physical rows and total incident rows.
  * Independent status dimensions: execution status (operational halt vs success), verification coverage, and integrity conformance. An operational failure preventing integrity evaluation can never emit `integrity_conforming`.
- **Stop Criteria**: Stop if implementation attempts to write to disk or import external network libraries.
- **Responsible Role**: Senior Software Engineer.
- **Status**: **Deferred** (requires Gate 1 authorization).

#### `TASK-AUD-03`: Implement CLI Audit Runner with Read-Only Guards
- **Roadmap Link**: Subtask of `TASK-EXT-05`.
- **Preconditions**: `TASK-AUD-02` completed.
- **Write Boundaries**:
  * `scripts/audit_three_source_inventory.py`
- **Deliverables**: Executable Python CLI script with:
  * Destination directory non-existence check (no overwrite allowed; halts immediately if destination exists; each run requires a fresh destination).
  * Atomic staging directory handling and pre-publication schema validation.
  * Single coherent `--allow-missing-raw` degradation policy (records skipped checks, reports MoonProt coverage as `partial_verification_raw_missing`, does not crash runner).
  * Run manifest generation recording **ONLY** Gate 3 tabular outputs, with independent reporting of execution status, verification coverage, and integrity conformance.
- **Stop Criteria**: Stop if runner fails to enforce read-only execution on input datasets.
- **Responsible Role**: Pipeline & Software Architect.
- **Status**: **Deferred** (requires Gate 1 authorization).

#### `TASK-AUD-04`: Author Tier A Synthetic Unit Test Suite (Mocks Only)
- **Roadmap Link**: Subtask of `TASK-EXT-05`.
- **Preconditions**: `TASK-AUD-02` and `TASK-AUD-03` completed.
- **Write Boundaries**:
  * `tests/test_three_source_inventory_audit.py`
- **Deliverables**: Comprehensive pytest suite testing all audit functions on synthetic mock tables in isolated temporary directories.
- **Testing Scope Boundary**: Strictly limited to Tier A synthetic tests in isolation. Zero pipeline execution on candidate release tables or full catalog during Gate 1.
- **Test Scenarios**:
  * Complete bijection and inclusion-exclusion verification on mock 3-source inputs.
  * Detection of orphan records, foreign key mismatches, and scoped referential boundary checks.
  * Key collision test: verifies that two physical rows sharing the same `(source_name, source_record_id)` key are both preserved in accounting ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}} = 2$), exactly one unique source–record key exists ($N_{\text{unique\_keys}} = 1$), the two occurrences have distinct `row_locator` values (`#record:1` vs `#record:2`), and collision incidents are logged using compound key `(source_name, source_record_id, row_locator, primary_reason_code)` without colliding with each other or losing either occurrence.
  * Single source record with multiple incidents: verifies that a record triggering two distinct incidents produces two incident rows in `three_source_quarantine_register.csv` but counts as exactly one physical row in row conservation ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}} = 1$) and one key in affected source–record keys ($N_{\text{affected\_keys}} = 1$).
  * Conformance decoupling: verifies that internal multiplicity and partial verification do not mark the run non-conforming, while structural integrity invariant violations do.
  * Handling of internal multiplicity (asserting that records are never dropped or collapsed).
  * Categorization of missingness (empty field vs observed absence vs missing dependency).
  * Degradation test: clean run and `partial_verification_raw_missing` flag when MoonProt raw HTML directory is absent.
- **Stop Criteria**: Stop if any synthetic unit test fails.
- **Responsible Role**: Quality Assurance Engineer.
- **Status**: **Deferred** (requires Gate 1 authorization).

---

### Gate 2: Code Review & Technical Commit (Deferred)

#### `TASK-AUD-05`: Technical Code Review & Pre-Commit Verification
- **Roadmap Link**: Prerequisite for Phase B execution.
- **Preconditions**:
  * 100% of Tier A synthetic tests pass.
  * Full existing test suite regression passes.
  * Git index clean of unrelated foreign modifications (`0` staged files).
  * Untracked files and working tree edits preserved intact (clean index, not clean tree).
- **Write Boundaries**: None (Git commit operation only, upon explicit human sign-off).
- **Deliverables**: Isolated Git commit landing:
  * `src/mfp_bibliography/three_source_auditor.py`
  * `scripts/audit_three_source_inventory.py`
  * `tests/test_three_source_inventory_audit.py`
  * `data/curated/schemas/three_source_inventory_summary.schema.json`
  * `data/curated/schemas/three_source_quarantine_register.schema.json`
- **Stop Criteria**: Stop if git index contains foreign modifications or schemas are missing from staged deliverables.
- **Responsible Role**: Lead Maintainer / Software Architect.
- **Status**: **Deferred** (requires Gate 2 authorization).

---

### Gate 3: Offline Audit Execution (Deferred)

#### `TASK-AUD-06`: Execute Read-Only Audit on Candidate v0.3.0 Release
- **Roadmap Link**: Execution of `TASK-EXT-05` and `TASK-EXT-07`.
- **Preconditions**:
  * Gate 2 commit landed.
  * Candidate release `releases/mfp-catalog-candidate-v0.3.0/` verified intact via SHA-256.
  * Inputs, execution configuration, and Gate 3 authorization verified (findings reviewed in Gate 4).
  * Target output directory confirmed non-existent prior to execution (no overwrite allowed).
- **Write Boundaries**:
  * `data/curated/audit/three_source_inventory_summary.csv`
  * `data/curated/audit/three_source_quarantine_register.csv`
  * `data/curated/audit/manifest.json`
- **Deliverables**: Published summary table, itemized quarantine register (one row per incident event), and execution manifest recording ONLY these tabular outputs.
- **Stop Criteria & Conformance Rules**:
  * Operational halt (`execution_failure`): stops execution immediately on errors preventing reading, parsing, or publishing (e.g. missing files, bad CSV syntax, target directory exists). An operational failure preventing evaluation cannot produce `integrity_conforming`.
  * Evaluable integrity violations: if $N_{\text{loaded\_rows}} \neq N_{\text{accounted\_rows}}$, key collisions, or broken scoped foreign keys occur, complete execution, produce valid diagnostic tables, and flag integrity conformance as `non_conforming_integrity_violation`. Multiplicity, unclassified multiplicity, and curatorial incidents are recorded without implying structural non-conformance.
- **Responsible Role**: Scientific Bioinformatics Auditor.
- **Status**: **Deferred** (requires Gate 3 authorization).

---

### Gate 4: Scientific Audit Review & Closeout (Deferred)

#### `TASK-AUD-07`: Author Descriptive Report & Quarantine Register Review
- **Roadmap Link**: Corresponds to `TASK-EXT-06` and Phase B closeout.
- **Preconditions**: Gate 3 audit outputs published and verified against manifests.
- **Write Boundaries**:
  * `docs/reports/three-source-inventory-audit-report.md`
- **Deliverables**: Peer-reviewed narrative report evaluating census findings, internal multiplicity distributions, and curatorial recommendations for quarantined cases. Note that the indicative $>5\%$ quarantine threshold is an unapproved proposal and does not automatically block review.
- **Stop Criteria**: Stop if curatorial review identifies unresolved ambiguities without an assigned reason code.
- **Responsible Role**: Lead Maintainer / Principal Investigator & Scientific Auditor.
- **Status**: **Deferred** (requires Gate 4 authorization).
