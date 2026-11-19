# Implementation Plan: QuickGO Pilot Concordance Recomparison & Transition Analysis (Task PIL-04.1B)

- **Document ID**: `PLAN-PIL-04.1B-CONCORDANCE-RECOMPARISON-001`
- **Feature Directory**: `specs/quickgo-pilot-concordance-recomparison/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Implementation Plan; Staged Execution Strategy)
- **Status**: **Gate 1 & Technical Commit Completed; Documentary Commit Authorized; Pipeline Execution Strictly Deferred**
- **Baseline Git HEAD**: `421da7e81c450b4bbeca2c637bbbfe0c8db002b4` (Historical baseline)
- **Technical Commit**: `0789e4a7ccb9a0fb37de258a82c03b851d619e95`
- **Specification Reference**: [`specs/quickgo-pilot-concordance-recomparison/spec.md`](spec.md)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Architectural Strategy & Design Principles

This plan details the phased technical implementation strategy for executing **Task PIL-04.1B: Concordance Recomparison & Transition Analysis**.

### 1.1 Non-Destructive Extension via Dual-Pipeline Recomparison
To preserve the scientific authority of the historical Stage P3 baseline while evaluating the impact of ontology-derived aspect metadata, the system executes a non-destructive parallel evaluation:

```
┌────────────────────────────────────────────────────────────────────────┐
│               PARALLEL CONCORDANCE EVALUATION ARCHITECTURE             │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [Frozen Baseline P3 Inputs]                                           │
│  • source_go_annotations_pilot.csv (N=353)                             │
│  • quickgo_annotations_pilot.csv (N=156)                               │
│  • quickgo_coverage_pilot.csv (N=8)                                    │
│                            │                                           │
│                            ├──────────────────────────┐                │
│                            │                          │                │
│                            ▼ (Legacy Path)            ▼ (Enriched Path)│
│                 [Stage P3 Engine]          [PIL-04.1B Join Engine]     │
│                            │                          ▲                │
│                            │                          │                │
│                            │        [PIL-04.1A Derived Metadata]       │
│                            │        • derived_source_go_aspects.csv    │
│                            │                                           │
│                            ▼                                           │
│                 [Frozen P3 Baseline]       [Recomparison Matrix]       │
│                 • quickgo_concordance_     • quickgo_concordance_      │
│                   pilot.csv (72 rows)        pilot_recomputed.csv      │
│                            │                 (72 rows)                 │
│                            │                          │                │
│                            └──────────┬───────────────┘                │
│                                       ▼                                │
│                          [Transition Matrix Engine]                    │
│                          • quickgo_concordance_                        │
│                            transition_pilot.csv (72 rows)              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Architectural Principles
1. **Zero Overwrite Guarantee**: The historical directories `data/interim/pilot/quickgo_slice/` and `data/interim/pilot/quickgo_slice_enriched/` are strictly read-only.
2. **Backward Compatibility**: If invoked without derived aspect metadata, the concordance engine must reproduce the frozen Stage P3 baseline bit-for-bit.
3. **Atomic Publication**: Recomputed datasets are staged in a temporary directory, validated against schemas and invariants, and published only upon full verification.
4. **Offline Determinism**: The entire pipeline operates 100% offline with zero live network calls and bit-for-bit mathematical reproducibility.

---

## 2. Explicit Future Write Scope

When authorized for implementation by human approval, file modifications must be strictly confined to the following paths. No wildcards, unlisted files, or out-of-scope edits are permitted.

### 2.1 Code & Runner Components
- `src/mfp_bibliography/quickgo_concordance.py`:
  - Enhance `build_concordance_matrix()` to accept optional `derived_aspects_rows` parameter.
  - Implement strict 1:1 join integrity validator between source annotations and derived aspect metadata.
  - Implement obsolete-term semantics (Cases A, B, C, D) and conflict quarantine logic.
  - Implement `build_concordance_transition_matrix()` generating the 72-row transition table.
  - Retain legacy mode ensuring 100% backward compatibility when `derived_aspects_rows` is omitted.
- `scripts/build_quickgo_concordance_recomparison.py`:
  - New dedicated CLI pipeline runner orchestrating verified input loading, hash verification, staging directory creation, recomparison matrix generation, transition matrix generation, JSON schema validation, manifest authoring, and atomic publishing.

### 2.2 Formal Schemas
- `data/curated/quickgo_concordance_transition.schema.json`:
  - New Draft 2020-12 validation contract governing row-level structure of the 72-row transition table: data types, required fields, regex patterns, closed categorical enums, numeric ranges, and row-level conditionals.
  *(Note: Relational accounting, cross-row key uniqueness, and delta arithmetic are enforced programmatically by Python validators, not by JSON Schema alone. `data/curated/quickgo_concordance.schema.json` is preserved without mutation; the recomputed matrix conforms to the existing schema).*

### 2.3 Automated Tests & Fixtures
- `tests/test_quickgo_concordance_recomparison.py`:
  - Single authorized test file containing all unit and regression tests.
  - **Inline Synthetic Fixtures**: All synthetic fixtures for join failure injection, obsolete-term rules, aspect conflict quarantine, and transition state evaluations are defined **inline** within this test file. No new fixture directories or external fixture files are created.
  - Tier A (Portable Synthetic Tests): Run 100% in-memory with zero local pilot file dependencies.
  - Tier B (Local Regression Tests): Validate semantic DataFrame equality and deterministic serialization against frozen pilot baseline; cleanly skipped via `pytest.mark.skipif` if pilot artifacts are absent.

### 2.4 Emitted Output Artifacts
All generated outputs reside strictly in `data/interim/pilot/quickgo_slice_recomparison/`:
1. `data/interim/pilot/quickgo_slice_recomparison/quickgo_concordance_pilot_recomputed.csv` (72 rows; schema: `quickgo_concordance.schema.json`)
2. `data/interim/pilot/quickgo_slice_recomparison/quickgo_concordance_transition_pilot.csv` (72 rows; schema: `quickgo_concordance_transition.schema.json`)
3. `data/interim/pilot/quickgo_slice_recomparison/manifest.json` (runtime execution manifest with complete provenance)

---

## 3. Sequential Human Authorization Gates

Execution must not proceed monolithically. Implementation and analytical execution are strictly separated across four discrete authorization gates:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SEQUENTIAL AUTHORIZATION GATES                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [GATE 1: Implementation & Portable Synthetic Tests]     [COMPLETED]   │
│  • Transition schema, engine extensions, runner, and tests authored    │
│  • Tier A portable synthetic unit tests passed (37 passed, 1 desel.)   │
│                               │                                        │
│                               ▼                                        │
│                                                                        │
│  [GATE 2: Technical Review & Code Commit]                [COMPLETED]   │
│  • Implementation code, schema, and tests reviewed                     │
│  • Technical commit: 0789e4a7ccb9a0fb37de258a82c03b851d619e95          │
│  • Documentary commit authorized in this turn                          │
│                               │                                        │
│                               ▼ (Pending Human Sign-Off / Deferred)    │
│                                                                        │
│  [GATE 3: Pilot Execution & Provenance Recording]        [UNAUTHORIZED]│
│  • Execute build_quickgo_concordance_recomparison.py offline           │
│  • Generate recomputed concordance matrix and transition matrix        │
│  • Run Tier B local regression and verification checks                 │
│  • Record complete runtime provenance in manifest.json                 │
│                               │                                        │
│                               ▼ (Pending Human Sign-Off / Deferred)    │
│                                                                        │
│  [GATE 4: Results Review & Descriptive Synthesis Closure][UNAUTHORIZED]│
│  • Review empirical transition results and limitation analysis         │
│  • Author descriptive completion report (Report PIL-04.1B)             │
│  • Close task documentation                                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> Gate 1 implementation and Gate 2 technical commit (`0789e4a7ccb9a0fb37de258a82c03b851d619e95`) are complete.
> Documentary commit of the specification package is authorized in this turn.
> Tier B regression is implemented but unexecuted; frozen-baseline byte-level compatibility remains pending Tier B execution.
> Gate 3 (full pilot pipeline execution and output generation) and Gate 4 (results review and synthesis report) remain **strictly unauthorized** pending separate explicit human sign-off; no empirical PIL-04.1B concordance outcomes exist yet.

---

## 4. Detailed Component Design & Testing Strategy

### 4.1 Join Engine & Invariant Checking
```python
def join_source_annotations_with_derived_aspects(
    source_annotations: List[Dict[str, Any]],
    derived_aspects: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Join source annotations to derived aspects with strict 1:1 bijection enforcement.

    Join Key:
      - Strictly requires non-null, valid annotation_id in both inputs.
      - Prohibits heuristic or fallback join keys.

    Cross-Table Field Verification:
      - protein_id == protein_id
      - source_id == source_id
      - source_record_id == source_record_id
      - go_id == source_go_id
      - parse_csv_value(go_aspect) == source_declared_aspect (verifying source-declared
        aspect across differing schema column names).

    Aborts immediately on:
      - Count mismatch (len(source) != len(derived) != 353)
      - Missing, null, or duplicate annotation_id in either dataset
      - Unmatched IDs in either direction
      - Divergence in any invariant source field
    """
```

### 4.2 Concordance Aspect Partitioning & Conflict Quarantine Logic
For each annotation row:
1. If `source_declared_aspect` is in `{"BP", "CC", "MF"}`:
   - Check `mapping_status`.
   - If `mapping_status == "conflict_source_ontology_aspect_mismatch"`:
     - Flag row as quarantined from both declared and derived aspect buckets.
     - Affected comparison unit receives:
       - `source_inventory_status = "indeterminate"`
       - `concordance_status = "not_evaluable"`
       - `primary_non_evaluable_reason = "source_aspect_indeterminate"` (compatible with `quickgo_concordance.schema.json`)
       - Appends `"source_aspect_conflict"` to `secondary_non_evaluable_reasons`.
   - Otherwise, assign row to declared aspect bucket using verbatim `source_go_id` (even if obsolete or secondary).
2. If `source_declared_aspect` is null or `"unassigned"`:
   - If `derived_aspect` is in `{"BP", "CC", "MF"}` and `mapping_status` in `{"resolved_primary", "resolved_secondary_alt_id"}`:
     - Assign row to `derived_aspect` bucket using verbatim `source_go_id`.
   - If `derived_aspect` is null (e.g. obsolete term, unknown ID, malformed ID):
     - Term remains unassigned; omitted from aspect buckets.

### 4.3 Testing & Regression Matrix (Two-Tier Structure)

#### Tier A: Portable Synthetic Unit Tests (In-Memory, Inline Fixtures)
- **Join Failure Injection Tests**:
  - Dropping 1 row from derived aspects $\to$ raises `JoinIntegrityError`.
  - Duplicating 1 row in derived aspects $\to$ raises `JoinIntegrityError`.
  - Mutating `source_go_id` in 1 row $\to$ raises `JoinIntegrityError`.
  - Mutating `source_declared_aspect` vs `go_aspect` $\to$ raises `JoinIntegrityError`.
- **Obsolete-Term Semantics Tests**:
  - Case A: Declared BP with obsolete `GO:0006537` $\to$ retained in BP bucket as `GO:0006537`.
  - Case B: Unassigned with obsolete `GO:0019048` $\to$ aspect remains null; omitted from BP/CC/MF.
  - Case C: Unassigned with active `GO:0003824` $\to$ assigned to MF bucket as `GO:0003824`.
  - Case D: Synthetic unknown GO ID with declared MF $\to$ retained in MF; unknown GO ID without aspect $\to$ omitted.
- **Aspect Conflict Quarantine Test**:
  - Synthetic annotation with declared `BP` and ontology namespace `molecular_function` $\to$ quarantined; `source_inventory_status = "indeterminate"`; `primary_non_evaluable_reason = "source_aspect_indeterminate"`; secondary reason contains `"source_aspect_conflict"`.
- **Transition Evaluator Unit Tests**:
  - Evaluable row with identical scores and identical inventory $\to$ `evaluable_fully_identical`, $\Delta J = 0.0000$.
  - Evaluable row with identical scores but modified source term set $\to$ `evaluable_score_identical_inventory_changed`, `source_set_content_changed = true`.
  - Evaluable row with increased score $\to$ `evaluable_score_increased`, $\Delta J > 0.0000$.
  - Previously non-evaluable row becoming evaluable $\to$ `newly_evaluable`, $\Delta J = \text{null}$, `metric_transition = "score_newly_defined"`.
  - Non-evaluable row remaining non-evaluable with identical reason $\to$ `non_evaluable_fully_identical`.
  - Non-evaluable row remaining non-evaluable with changed reason $\to$ `non_evaluable_reason_changed`.
- **Programmatic Transition Invariant Tests**:
  - Delta arithmetic consistency across all 72 rows.
  - Cross-row `transition_id` uniqueness (72 distinct keys).
  - Precedence validation for `overall_transition_classification`.

#### Tier B: Local Baseline Regression Tests (Ignored Interim Artifact Dependent)
- **Execution Condition & Skip Logic**:
  - If `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` is absent, the regression test is cleanly skipped via `pytest.mark.skipif(..., reason="Local interim pilot artifact not present")`.
- **Semantic Comparison**:
  - Run `build_concordance_matrix()` in legacy mode (no enrichment).
  - Assert output DataFrame matches frozen baseline semantically via `pandas.testing.assert_frame_equal`.
- **Deterministic Serialization & Byte-Level Verification**:
  - Serialize legacy output to CSV using fixed encoding (`utf-8`), standard newline (`\n`), fixed float formatting (`%.4f`), and standard quoting (`csv.QUOTE_MINIMAL`).
  - Compute SHA-256 digest and verify bit-for-bit identity against expected baseline digest `12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7`.

### 4.4 Safe Staging & Publication Protocol
1. **Refusal on Existing Target**:
   The runner checks if `data/interim/pilot/quickgo_slice_recomparison/` exists. If present, it aborts immediately to prevent clobbering previously evaluated data.
2. **Run-Unique Staging Path**:
   All outputs and manifest are staged in `data/interim/pilot/.staging_recomparison_<timestamp>_<pid>/`.
3. **Disjoint Path Verification**:
   The runner resolves canonical paths and confirms that neither staging nor destination paths overlap with or nest within historical input directories.
4. **Validation Before Publishing**:
   - Parse CSV rows (converting empty strings to `None`, numbers to numeric types).
   - Validate each row against Draft 2020-12 JSON Schemas.
   - Run programmatic validators checking arithmetic, relational, and fixed-universe invariants.
5. **Atomic Publication & Directory Replacement**:
   - If destination does not exist: rename staging directory to destination path (`Path.rename`).
   - If destination exists and overwrite was explicitly authorized: back up or remove existing destination, then move verified staging directory into destination.
   - If an exception occurs: remove only the run's own unique staging directory.
