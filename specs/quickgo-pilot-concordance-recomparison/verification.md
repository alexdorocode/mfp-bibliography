# Verification Record: QuickGO Pilot Concordance Recomparison Contract (Task PIL-04.1B)

- **Document ID**: `VERIF-PIL-04.1B-CONCORDANCE-RECOMPARISON-001`
- **Feature Directory**: `specs/quickgo-pilot-concordance-recomparison/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Verification Record; Gate 1 & Technical Commit Verified)
- **Status**: **Gate 1 Completed & Verified; Technical Commit Landed (0789e4a); Documentary Commit Authorized; Gate 3 & Gate 4 Unauthorized**
- **Baseline Git HEAD**: `421da7e81c450b4bbeca2c637bbbfe0c8db002b4` (Historical baseline)
- **Technical Commit**: `0789e4a7ccb9a0fb37de258a82c03b851d619e95`
- **Specification Reference**: [`specs/quickgo-pilot-concordance-recomparison/spec.md`](spec.md)
- **Plan Reference**: [`specs/quickgo-pilot-concordance-recomparison/plan.md`](plan.md)
- **Tasks Reference**: [`specs/quickgo-pilot-concordance-recomparison/tasks.md`](tasks.md)
- **Verification Date**: 2026-11-17 (Initial Gate 1); 2026-11-18 (Corrective Pass Completed & Verified); 2026-11-19 (Technical Commit 0789e4a & Documentary Alignment)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Executive Summary & Verification Matrix

This verification record documents the documentary checks, read-only baseline matrix inspections, and contract reconciliations performed for **Task PIL-04.1B: QuickGO Pilot Concordance Recomparison & Transition Analysis**, including the bounded corrective pass completed on 2026-11-18.

```
┌────────────────────────────────────────────────────────────────────────┐
│            PIL-04.1B GATE 1 & 2 VERIFICATION STATUS (2026-11-19)       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Git Repository HEAD & State Audit ────────────────► [VERIFIED / OK] │
│ 2. Frozen Stage P3 Matrix Inspection (72 rows) ──────► [VERIFIED / OK] │
│ 3. Baseline Evaluability Reconciliation (10 vs 9) ───► [VERIFIED / OK] │
│ 4. PIL-04.1A 1:1 Join Key Integrity Audit (N=353) ───► [VERIFIED / OK] │
│ 5. Join-Contract Contradiction Resolution ───────────► [VERIFIED / OK] │
│ 6. Upstream mapping_status Enums & Conflict Audit ───► [VERIFIED / OK] │
│ 7. Schema Compatibility for Aspect Conflicts ────────► [VERIFIED / OK] │
│ 8. Transition Semantics & 4-Decimal Precision ───────► [VERIFIED / OK] │
│ 9. Schema vs Programmatic Validation Boundary ───────► [VERIFIED / OK] │
│ 10. Safe Staging & Publication Boundary ─────────────► [VERIFIED / OK] │
│ 11. Implementation Code Modifications (4 files) ─────► [COMMITTED:0789]│
│ 12. In-Memory Python AST & JSON Syntax Checks ───────► [4/4 PASSED/OK] │
│ 13. Pre-Commit Test Execution (Tier A) ──────────────► [37 PASSED / OK]│
│ 14. Full Repository Test Suite Regression (Hist.) ───► [686 PASSED/OK] │
│ 15. Tier B Baseline Regression ──────────────────────► [GATED: GATE 3] │
│ 16. Pilot Pipeline Recomparison Execution ───────────► [GATED: GATE 3] │
│ 17. Historical Baseline Immutability ────────────────► [INTACT / OK]   │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Honest Operational Status (Gate 1 & Technical Commit Completed; Documentary Commit Authorized)**:
> In strict compliance with repository operational boundaries and human authorizations:
> - **Provider Interruption & Recovery**: The initial corrective pass was interrupted on 2026-11-17 by a provider 503 capacity error. Recovery inspection and resumption occurred on 2026-11-18 from the exact files on disk without loss or restart.
> - **Syntax & AST Verification**: In-memory compilation and AST parsing (`ast.parse`) for the 3 Python files and JSON schema parsing (`json.load`) were explicitly executed by the Python runtime and passed with 0 syntax errors.
> - **Historical Progression & Failure Resolution**: An intermediate test run registered 28 passed, 3 failed, 1 skipped. Failures were diagnosed and resolved:
>   * Stale test error regexes in `test_tier_a_join_contradictory_fields` were corrected to match actual join exception messages (`Contradictory protein_id`, etc.).
>   * Stale match pattern in `test_tier_a_concordance_validator_count_identities_and_reason_consistency` was updated to match normalized validator wording.
>   * In `build_quickgo_concordance_recomparison.py`, protected path and ancestor collision checks were reordered before the destination existence check, resolving an issue where collision with an existing protected file raised `FileExistsError` instead of `ValueError`.
> - **Upstream Manifest & Lineage Verification**: Reconciled and enforced explicit expected-versus-actual cryptographic digest checks for upstream manifests (Stage P3: `01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7`; PIL-04.1A: `5fe29c5fdefbbe0d14b755844dcecf9b6ca29afc460eb4aec7b3479b596b077f`). Verified structural artifact relationships (P3 baseline output digest, PIL-04.1A derived aspects output digest, source annotations input digest, and mandatory ontology lineage metadata).
> - **Pre-Commit Tier A Synthetic Test Suite**:
>   Executed command:
>   ```bash
>   RUN_TIER_B_LOCAL_REGRESSION=0 pytest tests/test_quickgo_concordance_recomparison.py -v -k "tier_a"
>   ```
>   Reported result: **37 passed, 1 deselected in 0.13s** (100% offline, zero network access, isolated temporary directories).
> - **Staged-CSV Corruption Coverage**: Parameterized test `test_tier_a_runner_staged_csv_corruption_rejected` verifies that contract corruption injected into either staged CSV before read-back validation causes immediate rejection, aborts publication, cleans up staging, and preserves unrelated files and directories.
> - **Upstream Manifest Test Coverage**: Targeted synthetic tests verify valid synthetic lineage, wrong manifest digests, missing required lineage fields, and upstream output-to-consumed-input relationship mismatches.
> - **Gate 2 Technical Commit Landed**: Commit `0789e4a7ccb9a0fb37de258a82c03b851d619e95` (parent `421da7e81c450b4bbeca2c637bbbfe0c8db002b4`) on branch `feature/functional-normalization` committed exactly the 4 technical files (`data/curated/quickgo_concordance_transition.schema.json`, `src/mfp_bibliography/quickgo_concordance.py`, `scripts/build_quickgo_concordance_recomparison.py`, `tests/test_quickgo_concordance_recomparison.py`).
> - **Documentary Scope Authorized**: This turn authorizes updating and committing exactly the 4 specification files (`spec.md`, `plan.md`, `tasks.md`, `verification.md`).
> - **Tier B Regression Test**: Authored with full semantic column-by-column check and serialized-byte SHA-256 baseline check (`12ce77f...`), gated behind explicit opt-in `RUN_TIER_B_LOCAL_REGRESSION=1`. Unexecuted per Gate 1 and Gate 2 scopes; historical bit-for-bit compatibility remains pending Tier B authorized execution.
> - **Pipeline execution**: **Not performed**. In accordance with Gate 3 restrictions, no recomputations or data mutations occurred in `data/interim/pilot/quickgo_slice_recomparison/`. No empirical PIL-04.1B concordance outcomes exist yet.
> - **Git state**: Technical commit landed; pending documentary commit in this turn. Gate 3 remains unauthorized.

---

## 2. Documentary & Read-Only Checks Actually Performed

### 2.1 Git Working Status & Baseline HEAD
- Historical baseline Git HEAD prior to increment implementation:
  `421da7e81c450b4bbeca2c637bbbfe0c8db002b4`
- Implemented technical commit Git HEAD:
  `0789e4a7ccb9a0fb37de258a82c03b851d619e95` (parent `421da7e81c450b4bbeca2c637bbbfe0c8db002b4` on branch `feature/functional-normalization`)
- Pre-existing untracked and modified files were identified and preserved intact without alteration:
  - `docs/reports/pending-work-triage-2026-11-12.md`
  - `docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`
  - `docs/reports/quickgo-pilot-preservation-record.md`
  - `docs/roadmap/draft-pilot-preservation-communication-and-operational-roadmap.md`

### 2.2 Frozen Baseline Concordance Matrix Audit
A read-only inspection of `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` (SHA-256 `12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7`) confirmed:
- Total rows: exactly **72 rows**.
- Evaluated comparison units: exactly **36 units** ($12\text{ pairs} \times 3\text{ aspects}$).
- Policies evaluated: exactly 2 (`captured_inventory_overlap`, `filtered_descriptive_overlap`).
- Total evaluable rows: exactly **20 rows** (10 units under Policy B, 10 units under Policy C).
- Total non-evaluable rows: exactly **52 rows** (26 units under Policy B, 26 units under Policy C).

### 2.3 Reconciliation of Baseline Evaluability Discrepancy
The preliminary proposal claimed 10 previously evaluable comparison units, but its narrative text enumerated only 9:
1. Multitask `Q42525`: BP, MF (2 units)
2. Multitask `Q9Y3E5`: BP, MF (2 units)
3. Multitask `P0AFW0`: BP, CC, MF (3 units)
4. PlantMP `Q42525`: BP, MF (2 units)

Direct inspection of the frozen records confirmed the following reconciliation:
- **Discrepancy 1 (`P0AFW0` CC)**: In the baseline matrix, `P0AFW0` / `SRC_MULTITASKPROTDB_II` / `CC` has `source_terms_count = 0` and is marked `not_evaluable` with `primary_non_evaluable_reason = "source_record_no_terms_aspect"`. It was mistakenly counted in the draft narrative. Actual evaluable units for `P0AFW0` Multitask: **2** (BP, MF).
- **Discrepancy 2 (`Q42525` CC and `Q9Y3E5` CC)**: Both `Q42525` / Multitask / `CC` ($J = 0.3333$) and `Q9Y3E5` / Multitask / `CC` ($J = 0.6000$) are fully evaluable in the baseline matrix with non-empty inventories and non-zero overlap. Both were mistakenly omitted from the draft narrative. Actual evaluable units for Multitask `Q42525`: **3** (BP, CC, MF). Actual evaluable units for Multitask `Q9Y3E5`: **3** (BP, CC, MF).
- **Actual Total**: Exactly **10 evaluable comparison units** (20 concordance rows), verified bit-for-bit from the records.

### 2.4 Resolution of Join-Contract Contradiction
Inspection of `data/curated/source_go_annotations.schema.json`, `data/curated/derived_source_go_aspects.schema.json`, and the interim pilot data files verified:
- Both schemas declare `annotation_id` as a **mandatory required field** matching pattern `^MFP:SGA:[A-Za-z0-9_]+:[0-9a-f]{16}$`.
- In `source_go_annotations_pilot.csv` and `derived_source_go_aspects_pilot.csv`, all 353 rows possess valid, non-null, unique `annotation_id` values.
- **Contract Resolution**: The specification contradiction between `spec.md` (which allowed a fallback key) and `plan.md` (which failed fast on missing ID) is resolved by adopting the strict contract:
  - Require valid, unique `annotation_id` in both tables.
  - Enforce exact 1:1 matching across all 353 rows.
  - Fail fast on missing, duplicate, unexpected, or contradictory records.
  - Heuristic or fallback keys are strictly prohibited.
- **Source-Declared Aspect Verification**:
  In `source_go_annotations_pilot.csv`, the source aspect column is named `go_aspect`.
  In `derived_source_go_aspects_pilot.csv`, it is named `source_declared_aspect`.
  The join validator explicitly asserts: `row_derived["source_declared_aspect"] == parse_csv_value(row_source["go_aspect"])`.

### 2.5 Verification of Actual Upstream Status Enums & Conflict Representation
Read-only inspection of `data/curated/derived_source_go_aspects.schema.json` and `src/mfp_bibliography/go_aspect_enrichment.py` confirmed:
- The committed `mapping_status` enum contains exactly 7 values:
  1. `resolved_primary`
  2. `resolved_secondary_alt_id`
  3. `obsolete_replaced_by`
  4. `obsolete_unreplaced`
  5. `unresolved_unknown_id`
  6. `unresolved_malformed_id`
  7. `conflict_source_ontology_aspect_mismatch`
- Upstream conflict representation: A source-declared vs. ontology namespace conflict is encoded via `mapping_status = "conflict_source_ontology_aspect_mismatch"`. The source aspect is retained in `source_declared_aspect`, the ontology aspect is in `derived_aspect`, and a descriptive message is recorded in `notes`.

### 2.6 Schema Compatibility Resolution for `quickgo_concordance.schema.json`
Inspection of `data/curated/quickgo_concordance.schema.json` confirmed:
- `primary_non_evaluable_reason` has an immutable closed enum of 11 values (or null); `"source_aspect_conflict"` is not present.
- `source_inventory_status` contains enum `"indeterminate"`.
- `secondary_non_evaluable_reasons` accepts arbitrary diagnostic strings.
- **Resolution**: An aspect conflict quarantines the row and sets `source_inventory_status = "indeterminate"`, `concordance_status = "not_evaluable"`, and governing `primary_non_evaluable_reason = "source_aspect_indeterminate"`. Explicit conflict diagnostic `"source_aspect_conflict"` is appended to `secondary_non_evaluable_reasons`. This provides 100% schema compliance without mutating historical schemas or disguising conflicts.

### 2.7 Transition Semantics & 4-Decimal Precision Verification
- Evaluated universe: exactly 72 rows.
- Deterministic 1:1 key mapping: `MFP:CONC:<acc>:<pid>:<src>:<asp>:<pol>` $\to$ `MFP:TRNS:<acc>:<pid>:<src>:<asp>:<pol>`.
- Orthogonal dimensions: `evaluability_transition`, `primary_reason_transition`, count deltas, `source_set_content_changed` (detecting term changes when counts match), and `metric_transition`.
- Precision consistency: Score delta is strictly computed on serialized 4-decimal scores: $\Delta J = \text{round}(J_{\text{recomp}} - J_{\text{base}}, 4)$.
- Overall classification precedence: 9 mutually exclusive summary states evaluated in strict order, distinguishing identical scores with inventory changes from fully identical records.

### 2.8 Separation of Schema and Programmatic Validation
- JSON Schema (Draft 2020-12) is formally restricted to row-level structural validation: types, required properties, nullability, enums, regex patterns, and range bounds. CSV empty strings are converted to `None` prior to validation.
- Programmatic Python validators and automated tests are explicitly assigned: delta arithmetic equality ($\Delta S, \Delta Q, \Delta J$), cross-row key uniqueness across all 72 rows, foreign-key integrity against baseline and catalog, and fixed 72-unit universe cardinality.

### 2.9 Safe Publication, Staging & Authorization Invariants
- Historical directories `data/interim/pilot/quickgo_slice/` and `data/interim/pilot/quickgo_slice_enriched/` are verified strictly read-only.
- Runner enforces initial target refusal if destination exists. Overwrite flags are technical checks, not human authorization.
- Staging directory is run-unique: `data/interim/pilot/.staging_recomparison_<timestamp>_<pid>/`. Cleanup on failure deletes only this directory.
- POSIX non-empty directory replacement limitations are explicitly documented.

---

## 3. Implementation and Automated Testing Results (Gate 1 Execution)

Pursuant to Gate 1 human authorization, implementation and portable synthetic verification were executed within the strict 4-file write boundary:

### 3.1 Transition Schema
- **File**: `data/curated/quickgo_concordance_transition.schema.json`
- **Specification**: JSON Schema Draft 2020-12 validating all 31 properties of the 72-row transition matrix.
- **Constraints Enforced**: Mandatory compound `transition_id` pattern `^MFP:TRNS:[A-Z0-9]+:MFP:(U:[0-9a-f]{16}|F:[A-Za-z0-9_]+:[0-9a-f]{16}):SRC_[A-Z0-9_]+:(BP|MF|CC):[a-z_]+$`, baseline `concordance_id` pattern, non-empty categorical enums for `evaluability_transition`, `primary_reason_transition`, `overall_transition_classification`, boolean `source_set_content_changed`, integer count boundaries, and null-safe 4-decimal score delta ranges `[-1.0000, 1.0000]`.
- **Validation**: Schema validated against Draft 2020-12 meta-schema via `jsonschema.Draft202012Validator.check_schema()`.

### 3.2 Enhanced Concordance Engine & Join Logic
- **File**: `src/mfp_bibliography/quickgo_concordance.py`
- **Key Enhancements**:
  - `validate_and_join_source_annotations()`: Enforces strict 1:1 join on `annotation_id`, verifying `source_declared_aspect == go_aspect` and `source_go_id == go_id`. Rejects missing, duplicate, mismatched, or cardinality-violating records with `JoinIntegrityError`. Supports arbitrary length inputs for unit testing.
  - Obsolete-term semantics (Cases A–D): Preserves source-declared aspect; fills unassigned aspects only from eligible active mappings. Preserves original verbatim GO IDs for set comparisons without canonical replacement or automatic obsolete term substitution.
  - Conflict quarantine: Any conflicting annotation (`conflict_source_ontology_aspect_mismatch`) sets `source_aspect_indeterminate` and records explicit `source_aspect_conflict` in `secondary_non_evaluable_reasons`, affecting both declared and derived aspect units.
  - Legacy backward compatibility: When `derived_aspects_rows is None`, reproduces historical Stage P3 matrix bit-for-bit.
  - `source_term_sets_out`: Reconstructs exact source term sets per comparison unit to enable direct set-equality comparison.
  - `build_concordance_transition_matrix()`:
    * Rejects duplicate comparison keys on baseline and recomparison sides with `ConcordanceValidationError`.
    * Validates `concordance_id` against the complete component key tuple before constructing lookup maps.
    * Enforces exact baseline/recomparison key correspondence across the entire comparison universe.
    * Requires complete `baseline_source_sets` and `recomparison_source_sets` maps for comparable inventories (`available`, `empty`); rejects missing keys and `None` values without falling back to count comparison.
    * Applies explicit operational convention for non-comparable inventories (`indeterminate`, `outside_slice`, `unavailable`), recording descriptive notes without claiming biological equality.
    * Generates 72-row transition matrix with four-decimal rounding on score deltas $\Delta J = \text{round}(J_{\text{recomp}} - J_{\text{base}}, 4)$, orthogonal indicator flags, and 9-level `overall_transition_classification` precedence.
  - Typed CSV row parsers (`parse_concordance_csv_row`, `parse_transition_csv_row`): Converts empty strings to `None`, preserves unexpected properties for strict `additionalProperties: false` schema enforcement, and rejects malformed boolean tokens rather than silently coercing them to `False`.
  - `validate_transition_matrix()` and `validate_recomputed_concordance_matrix()`: Enforces structural schema conformity, delta arithmetic invariants ($\Delta S = S_{\text{recomp}} - S_{\text{base}}$, $\Delta Q = Q_{\text{recomp}} - Q_{\text{base}}$, $\Delta J$), inclusion-exclusion set identities, reason consistency, key uniqueness, and relational integrity against both underlying matrices using `ConcordanceValidationError`.

### 3.3 Recomparison CLI Runner
- **File**: `scripts/build_quickgo_concordance_recomparison.py`
- **Features**:
  - Full CLI interface with `--output-dir`, `--baseline-concordance`, `--derived-aspects`, `--source-annotations`, `--raw-coverage`, `--functional-coverage`, `--catalog-proteins`, `--dry-run`, `--verbose`.
  - `PilotInputContract` and `PILOT_PRODUCTION_CONTRACT`: Explicit hardcoded expected SHA-256 digests for all 7 frozen pilot inputs and upstream manifests, unconditional source/derived cardinality checks ($N=353$), and exact 72-unit canonical comparison universe pair matching without silent fallbacks.
  - Legacy matrix reconstruction and semantic verification: Recomputes the legacy matrix without derived aspects and asserts column-by-column semantic equality against the frozen baseline before proceeding.
  - Initial target refusal: Fails fast if the destination directory already exists (no automated overwrite/deletion).
  - Path collision and overlap detection: Ensures destination does not collide with inputs, schemas, manifests, or protected repository directories (`data/raw`, `releases`, `docs`, `src`, etc.), evaluated prior to target directory checks.
  - Run-unique staging directory: Operates exclusively inside `.staging_recomparison_<timestamp>_<pid>/` and only cleans up its own staging directory upon failure.
  - Staged CSV read-back validation: Reloads staged CSVs from disk and validates them against schemas and programmatic invariants prior to computing output digests or finalizing the manifest.
  - Prospective provenance: Manifest records UTC execution timestamp, duration, git HEAD, git status, exact effective configuration, CLI arguments, dependency versions, code/schema digests, verified upstream manifest references (PIL-04.1A and Stage P3), and pinned ontology metadata obtained directly from upstream provenance.
  - Atomic publication: Moves validated staging directory to destination atomically (`rename`).

### 3.4 Automated Test Suite Execution
- **File**: `tests/test_quickgo_concordance_recomparison.py`
- **Syntax & In-Memory AST Checks**:
  Executed explicitly via Python runtime (`ast.parse` and `json.load`) with zero syntax errors:
  - `src/mfp_bibliography/quickgo_concordance.py`: AST OK
  - `scripts/build_quickgo_concordance_recomparison.py`: AST OK
  - `tests/test_quickgo_concordance_recomparison.py`: AST OK
  - `data/curated/quickgo_concordance_transition.schema.json`: JSON OK
- **Tier A Portable Synthetic Tests** (37 tests, all inline fixtures, 100% offline):
  - Join integrity: valid 1:1 join, length mismatch, key duplication, missing key, column mismatch, aspect mismatch with exact contradictory field match verification.
  - Enrichment semantics: Case A active primary, Case B obsolete replaced, Case C obsolete unreplaced, Case D unresolved, conflict quarantine of both aspect units.
  - Legacy backward compatibility: identical output when derived aspects omitted.
  - Transition matrix evaluation: delta arithmetic, score changes, identical score with inventory change, non-evaluable transitions, 9-state precedence ordering.
  - Transition input integrity: duplicate key rejection, ID mismatch rejection, required source-set maps, operational conventions for non-comparables, malformed boolean rejection, unexpected property rejection.
  - Programmatic validators: delta arithmetic corruption rejection, relational checks against underlying baseline and recomparison matrices, inclusion-exclusion set identities, reason consistency.
  - CLI runner protections: destination refusal, path collision refusal, isolated staging lifecycle with sentinel file/directory preservation, frozen digest / cardinality / canonical universe rejection.
  - Staged-CSV corruption rejection: Parameterized test verifying that contract violations injected into either `quickgo_concordance_pilot_recomputed.csv` or `quickgo_concordance_transition_pilot.csv` before read-back validation cause immediate pipeline rejection, abort publication, remove staging, and preserve unrelated files.
  - Upstream manifest verification: Targeted synthetic test suite verifying valid synthetic lineage recording, rejection of wrong P3 and PIL-04.1A manifest digests, rejection of missing required sections or lineage fields (`output_inventory`, `summary`, `ontology_version`), and rejection of upstream output-to-consumed-input relationship mismatches.
  - Deterministic serialization: bit-for-bit identical SHA-256 digests across repeated serializations.
- **Tier B Local Baseline Regression Test**: Fully authored test body performing semantic column-by-column comparison and serialized-byte SHA-256 check against Stage P3 baseline. Gated behind explicit `RUN_TIER_B_LOCAL_REGRESSION=1` opt-in; skipped per Gate 1 scope.
- **Execution Command & Output**:
  ```bash
  RUN_TIER_B_LOCAL_REGRESSION=0 pytest tests/test_quickgo_concordance_recomparison.py -v -k "tier_a"
  # Result: 37 passed, 1 deselected in 0.13s (100% pass rate)
  ```
- **Historical Intermediate Results & Regression Note**:
  During the initial corrective pass, an intermediate test execution returned 28 passed, 3 failed, 1 skipped due to stale test error message regexes and overly strict reason invariants. Following resolution of error wording, removal of contradictory invariants, runner path check reordering, and the addition of targeted manifest/staging corruption tests, all 37 Tier A tests pass cleanly. The full 686-test repository regression suite was executed and passed (686 passed, 1 skipped in 52.37s) during Gate 1 baseline verification and was preserved without regression.

### 3.5 Components Deferred to Subsequent Gates
1. **Gate 2 Technical Review & Commit**: Technical commit `0789e4a7ccb9a0fb37de258a82c03b851d619e95` completed on 2026-11-19; documentary commit authorized in this turn.
2. **Gate 3 Pilot Execution**: Running the real pipeline to generate `data/interim/pilot/quickgo_slice_recomparison/` (recomputed matrix, transition matrix, manifest.json) and executing Tier B regression remains strictly unauthorized and unexecuted; no empirical PIL-04.1B concordance outcomes exist yet.
3. **Gate 4 Synthesis**: Descriptive synthesis report remains pending observed recomparison results.

---

## 4. Preservation of Historical Baselines

All historical and upstream datasets were verified to be completely untouched:

| Target Baseline Directory / File | Pre-Task Status | Post-Task Status | Immutability State |
|---|:---:|:---:|:---:|
| `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` | `12ce77f...` | `12ce77f...` | **UNTOUCHED / FROZEN** |
| `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv` | `2a6255c...` | `2a6255c...` | **UNTOUCHED / FROZEN** |
| `data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv` | `981c592...` | `981c592...` | **UNTOUCHED / FROZEN** |
| `data/interim/pilot/quickgo_slice/manifest.json` | `01c6b54...` | `01c6b54...` | **UNTOUCHED / FROZEN** |
| `data/interim/pilot/quickgo_slice_enriched/derived_source_go_aspects_pilot.csv` | `e4500d3...` | `e4500d3...` | **UNTOUCHED / FROZEN** |
| `data/interim/pilot/quickgo_slice_enriched/manifest.json` | `5fe29c5...` | `5fe29c5...` | **UNTOUCHED / FROZEN** |
| `releases/mfp-catalog-candidate-v0.3.0/` | Frozen | Frozen | **UNTOUCHED / FROZEN** |
