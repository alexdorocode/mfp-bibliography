# Tasks: QuickGO Pilot Concordance Recomparison & Transition Analysis (Task PIL-04.1B)

- **Document ID**: `TASKS-PIL-04.1B-CONCORDANCE-RECOMPARISON-001`
- **Feature Directory**: `specs/quickgo-pilot-concordance-recomparison/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Task Inventory; Gate 1 & Technical Commit Completed; Documentary Commit Authorized)
- **Status**: **Gate 1 & Technical Commit Completed; Documentary Commit Authorized** (Technical commit `0789e4a7ccb9a0fb37de258a82c03b851d619e95`; 37 Tier A tests passed; Gate 3 & 4 strictly unauthorized)
- **Baseline Git HEAD**: `421da7e81c450b4bbeca2c637bbbfe0c8db002b4` (Historical baseline)
- **Technical Commit**: `0789e4a7ccb9a0fb37de258a82c03b851d619e95`
- **Specification Reference**: [`specs/quickgo-pilot-concordance-recomparison/spec.md`](spec.md)
- **Plan Reference**: [`specs/quickgo-pilot-concordance-recomparison/plan.md`](plan.md)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Task Inventory & Authorization Gating

Every implementation task is bound to a strict file write boundary and requires explicit human sign-off at its governing authorization gate before execution.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PIL-04.1B IMPLEMENTATION TASK INVENTORY                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ GATE 0: DOCUMENTATION CONTRACT & PLANNING (COMPLETED / AUTHORIZED)                     │
│ • spec.md, plan.md, tasks.md, verification.md                                          │
│                                                                                        │
│ GATE 1: IMPLEMENTATION & SYNTHETIC TESTS (CORRECTIVE PASS VERIFIED)                    │
│ • TASK-PIL04.1B-01: Author Transition Schema                               [COMPLETED] │
│ • TASK-PIL04.1B-02: Implement Enriched Concordance Engine & Join Logic     [COMPLETED] │
│ • TASK-PIL04.1B-03: Implement Transition Matrix Evaluator                  [COMPLETED] │
│ • TASK-PIL04.1B-04: Author Test Suite with Inline Fixtures & Local Regres. [COMPLETED] │
│ • TASK-PIL04.1B-05: Implement Recomparison CLI Runner                      [COMPLETED] │
│                                                                                        │
│ GATE 2: CODE REVIEW & TECHNICAL COMMIT (COMPLETED / AUTHORIZED)                        │
│ • TASK-PIL04.1B-06: Technical Review & Git Commit of Implementation Code   [COMPLETED] │
│ • Documentary commit of specification package authorized in this turn                  │
│                                                                                        │
│ GATE 3: PILOT EXECUTION & PROVENANCE RECORDING (STRICTLY UNAUTHORIZED)                 │
│ • TASK-PIL04.1B-07: Execute Offline Pipeline & Generate Outputs                        │
│ • TASK-PIL04.1B-08: Complete Technical Verification Record Update                      │
│                                                                                        │
│ GATE 4: RESULTS REVIEW & DOCUMENTARY CLOSURE (STRICTLY UNAUTHORIZED)                   │
│ • TASK-PIL04.1B-09: Descriptive Synthesis Report & Milestone Closure                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Task Specifications

| Task ID | Title & Objective | Allowed Write Scope | Prerequisites & Gate | Status |
|---|---|---|---|:---:|
| **TASK-PIL04.1B-01** | **Author Draft 2020-12 Transition Schema**: Author the row-level validation contract for the 72-row transition matrix, enforcing categorical transitions, null-safe four-decimal Jaccard ranges, integer count types, and foreign key patterns. (Relational and delta arithmetic invariants are enforced programmatically in TASK-PIL04.1B-03/04). | `data/curated/quickgo_concordance_transition.schema.json` | Gate 1 Sign-Off; `spec.md` §5 | **COMPLETED & VERIFIED** |
| **TASK-PIL04.1B-02** | **Implement Enriched Concordance Engine & Join Logic**: Enhance `quickgo_concordance.py` with strict 1:1 join verification on `annotation_id` (no fallback key; verifying `source_declared_aspect` against `go_aspect`), obsolete-term rules (Cases A–D), conflict quarantine with schema-compatible `source_aspect_indeterminate` and explicit secondary conflict diagnostic, and legacy backward compatibility. | `src/mfp_bibliography/quickgo_concordance.py` | Gate 1 Sign-Off; TASK-PIL04.1B-01 | **COMPLETED & VERIFIED** |
| **TASK-PIL04.1B-03** | **Implement Transition Matrix Generator**: Add `build_concordance_transition_matrix()` to `quickgo_concordance.py` evaluating paired baseline vs recomparison rows, computing four-decimal score deltas ($\Delta J$), orthogonal indicators (including `source_set_content_changed`), and `overall_transition_classification` with explicit precedence. | `src/mfp_bibliography/quickgo_concordance.py` | Gate 1 Sign-Off; TASK-PIL04.1B-02 | **COMPLETED & VERIFIED** |
| **TASK-PIL04.1B-04** | **Author Test Suite with Inline Fixtures**: Create unit tests in `tests/test_quickgo_concordance_recomparison.py` with inline synthetic fixtures for Tier A portable tests (join failure injection, obsolete cases, conflict quarantine, transition states, programmatic invariants) and Tier B local baseline regression (skipped if pilot artifacts absent; checking DataFrame equality and bitwise CSV SHA-256 serialization). | `tests/test_quickgo_concordance_recomparison.py` | Gate 1 Sign-Off; TASK-PIL04.1B-03 | **COMPLETED & VERIFIED** |
| **TASK-PIL04.1B-05** | **Implement Recomparison CLI Runner**: Author `scripts/build_quickgo_concordance_recomparison.py` with initial target refusal, run-unique staging directory (`.staging_recomparison_<timestamp>_<pid>/`), path overlap checks, CSV parsing/null conversion, schema + programmatic validation, safe atomic publication, and isolated staging cleanup. | `scripts/build_quickgo_concordance_recomparison.py` | Gate 1 Sign-Off; TASK-PIL04.1B-04 | **COMPLETED & VERIFIED** |
| **TASK-PIL04.1B-06** | **Technical Review & Code Commit**: Verify clean working tree, review diff against write boundaries, and commit code, schema, and test suite. | Git commit only (no new files) | Gate 2 Sign-Off; TASK-PIL04.1B-05 passed offline | **COMPLETED & VERIFIED** (Technical commit `0789e4a7ccb9a0fb37de258a82c03b851d619e95` on 2026-11-19; documentary commit authorized) |
| **TASK-PIL04.1B-07** | **Offline Pipeline Execution**: Execute runner offline, generating recomputed concordance matrix, transition table, and run manifest under `quickgo_slice_recomparison/`. | `data/interim/pilot/quickgo_slice_recomparison/quickgo_concordance_pilot_recomputed.csv`<br>`data/interim/pilot/quickgo_slice_recomparison/quickgo_concordance_transition_pilot.csv`<br>`data/interim/pilot/quickgo_slice_recomparison/manifest.json` | Gate 3 Sign-Off; TASK-PIL04.1B-06 committed | **PENDING AUTHORIZATION** (Strictly unauthorized; Tier B and real pilot unexecuted; no empirical outcomes) |
| **TASK-PIL04.1B-08** | **Author Technical Verification Record Update**: Update `verification.md` with verified execution digests, actual observed row transitions, schema validation results, and execution provenance. | `specs/quickgo-pilot-concordance-recomparison/verification.md` | Gate 3 Sign-Off; TASK-PIL04.1B-07 completed | **PENDING AUTHORIZATION** |
| **TASK-PIL04.1B-09** | **Descriptive Synthesis & Milestone Closure**: Author descriptive analysis report synthesizing empirical transition findings, evaluating pre-execution hypotheses against observed metrics, and closing PIL-04.1. | `docs/reports/quickgo-pilot-p5-concordance-recomparison-report.md` | Gate 4 Sign-Off; TASK-PIL04.1B-08 verified | **PENDING AUTHORIZATION** |

---

## 3. Strict Boundary Prohibitions

During any future implementation task:
1. **Never edit files outside the declared task scope**.
2. **Never modify or overwrite files in**:
   - `data/interim/pilot/quickgo_slice/` (Frozen Stage P3 baseline)
   - `data/interim/pilot/quickgo_slice_enriched/` (Frozen PIL-04.1A baseline)
   - `data/raw/` (Immutable raw inputs per ADR-002)
   - `releases/` (Packaged release candidates)
   - `docs/decisions/` (Accepted ADRs)
3. **Never execute live network requests, ontology downloads, or live database queries**.
4. **Never advance to subsequent gates without explicit human sign-off**.
