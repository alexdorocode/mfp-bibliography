# Verification Record: Minimum GO-Aspect Metadata Enrichment (Task PIL-04.1A)

- **Document ID**: `VERIF-PIL-04.1-GO-ASPECT-ENRICHMENT-001`
- **Task Identifier**: `PIL-04.1A` (Route B Increment)
- **Specification Reference**: [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](spec.md)
- **Plan Reference**: [`specs/quickgo-pilot-go-aspect-enrichment/plan.md`](plan.md)
- **Tasks Reference**: [`specs/quickgo-pilot-go-aspect-enrichment/tasks.md`](tasks.md)
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Baseline Technical Commit**: [`98530b32cd13d0b8ff5b4ea7a626e691d9426d25`](file:///home/alexdoro/repositories/mfp-bibliography)
- **Parent Published Baseline**: `21a3c8ef6bc42ae2f7f51ecc6f9ac6b9d9579b7e`
- **Execution Date**: 2026-11-16
- **Status**: **VERIFIED / PASSED** (100% Offline)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Executive Summary & Verification Matrix

Task PIL-04.1A implemented and executed the minimum GO-aspect metadata enrichment for the pilot slice under strict offline conditions. The execution mapped 353 source annotation rows against a pinned Gene Ontology snapshot (`releases/2026-01-23`), producing an isolated derived dataset and run manifest under `data/interim/pilot/quickgo_slice_enriched/`.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   TASK PIL-04.1A ACCEPTANCE VERIFICATION               │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Complete Inventory Traceability (353 in, 353 out) ─► [PASSED / OK] │
│ 2. Immutable Source Preservation (Verbatim go_id/asp) ─► [PASSED / OK] │
│ 3. Deterministic Mapping Status Categorization ───────► [PASSED / OK] │
│ 4. Secondary alt_id Resolution Without Overwrite ─────► [PASSED / OK] │
│ 5. Obsolete Protection (No Auto-Substitution / No consider) [PASSED]   │
│ 6. Isolated Derived Outputs (Zero P3/P4 Overwrite) ───► [PASSED / OK] │
│ 7. Draft 2020-12 Schema Validation ───────────────────► [PASSED / OK] │
│ 8. Offline Bitwise Determinism & Checksum Stability ──► [PASSED / OK] │
│ 9. Historical P1–P4 Baseline Intact & Untouched ──────► [PASSED / OK] │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Verified Input Dependencies

All inputs were verified prior to pipeline execution:

| Dependency | Logical Role | Size (Bytes) | Full SHA-256 Digest | Verification Status |
|---|---|:---:|---|:---:|
| `data/interim/pilot/source_go_annotations_pilot.csv` | Frozen Input Slice | 81,927 | `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda` | **VERIFIED** |
| `/home/alexdoro/repositories/mfp-dataset-designer/go-basic.obo` | Pinned Ontology Snapshot | 31,933,366 | `eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391` | **VERIFIED** |
| `data/curated/derived_source_go_aspects.schema.json` | Contract Schema | 4,228 | `45249395d0e932c71f2d7ef6a5ae8701f7777b89df31d5aecdd82ace1cff8eb6` | **VERIFIED** |

---

## 3. Emitted Output Artifacts & Manifest

Generated artifacts reside exclusively in the isolated directory `data/interim/pilot/quickgo_slice_enriched/`:

| Output File Path | Row Count | File Size (Bytes) | Full SHA-256 Digest | Schema Compliance |
|---|:---:|:---:|---|:---:|
| `data/interim/pilot/quickgo_slice_enriched/derived_source_go_aspects_pilot.csv` | 353 | 68,542 | `e4500d3cf93f2e8861ab7ea5a91a5f9ef55617dd3c6413f4b3abd2c7cf6b204e` | **PASS (100%)** |
| `data/interim/pilot/quickgo_slice_enriched/manifest.json` | — | 1,770 | `5fe29c5fdefbbe0d14b755844dcecf9b6ca29afc460eb4aec7b3479b596b077f` | **PASS** |

---

## 4. Empirical Mapping Results Breakdown

### 4.1 Distribution by Mapping Status

Across all 353 processed annotation rows:

| Mapping Status | Row Count | Unique GO IDs | Percentage | Operational Meaning |
|---|:---:|:---:|:---:|---|
| `resolved_primary` | **336** | **193** | 95.18% | Term exists as active primary term; aspect derived from ontology namespace. |
| `resolved_secondary_alt_id` | **5** | **3** | 1.42% | Term exists as secondary `alt_id`; primary term resolved; source string preserved. |
| `obsolete_replaced_by` | **6** | **5** | 1.70% | Obsolete term with official `replaced_by` tag; replacement recorded in metadata; not substituted (`resolved_go_id = null`, `derived_aspect = null`). |
| `obsolete_unreplaced` | **6** | **4** | 1.70% | Obsolete term without replacement; `consider` tags captured as metadata; not substituted (`resolved_go_id = null`, `derived_aspect = null`). |
| `unresolved_unknown_id` | **0** | **0** | 0.00% | Zero unknown identifiers relative to this snapshot. |
| `unresolved_malformed_id` | **0** | **0** | 0.00% | Zero malformed identifiers in this slice. |
| `conflict_source_ontology_aspect_mismatch` | **0** | **0** | 0.00% | Zero conflicts across the 200 comparable active rows ($0/200 = 0.0\%$). Conflict check not applicable / not performed on the 8 non-comparable obsolete rows. |
| **Total Processed** | **353** | **205** | **100.00%** | Bijective 1:1 preservation of input rows. |

> [!NOTE]
> **Reconciled Accounting & Conflict Denominators**:
> - **Obsolete Term Accounting**: Exactly **12 obsolete annotation rows** were observed across the dataset, representing exactly **9 unique obsolete GO identifiers**:
>   - `obsolete_replaced_by`: 6 rows (5 unique GO IDs: `GO:0006537`, `GO:0019048`, `GO:0019419` [2 rows in PlantMP], `GO:0019907`, `GO:0044237`).
>   - `obsolete_unreplaced`: 6 rows (4 unique GO IDs: `GO:0000988` [Multitask, PlantMP], `GO:0006200` [MoonProt], `GO:0006919` [MoonProt], `GO:0010033` [Multitask, PlantMP]).
> - **Aspect Conflict Denominator**:
>   - Total rows with source-declared aspects (`BP`, `CC`, `MF`): **208 rows** (95 in MultitaskProtDB-II, 113 in PlantMP).
>   - Declared-aspect obsolete rows: **8 rows** (3 in Multitask, 5 in PlantMP). Because obsolete terms receive `derived_aspect = null`, conflict check is **not applicable / not performed** (not labeled as zero conflicts).
>   - Strictly comparable active rows: **200 rows** (92 in Multitask, 108 in PlantMP) with both declared aspect and active derived aspect.
>   - Conflict count among comparable rows: exactly **0** ($0/200 = 0.0\%$).
>   - Undeclared / unassigned rows: **145 rows** (141 in MoonProt with null aspect; 4 in MultitaskProtDB-II with `unassigned`, all 4 resolved to active `BP`).

### 4.2 Breakdown by Source Database

| Source Database | Total Rows | Null / Unassigned Aspect | Resolved Primary | Resolved Alt ID | Obsolete Replaced | Obsolete Unreplaced | Comparable Active Rows | Non-Comparable Obsolete Rows |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `SRC_MOONPROT` | 141 | 141 (null) | 134 | 3 | 2 | 2 | 0 | 4 |
| `SRC_MULTITASKPROTDB_II` | 99 | 4 (unassigned) | 94 | 2 | 1 | 2 | 92 | 3 |
| `SRC_PLANTMP` | 113 | 0 | 108 | 0 | 3 | 2 | 108 | 5 |
| **Total** | **353** | **145** | **336** | **5** | **6** | **6** | **200** | **12** |

### 4.3 Derived Aspect Distribution

| Derived Aspect | Row Count | Percentage |
|---|:---:|:---:|
| `BP` (Biological Process) | 162 | 45.89% |
| `MF` (Molecular Function) | 124 | 35.13% |
| `CC` (Cellular Component) | 55 | 15.58% |
| `null` (Obsolete terms not treated as active annotations) | 12 | 3.40% |
| **Total** | **353** | **100.00%** |

---

## 5. Audit of Edge Cases & Safeguards

### 5.1 Secondary Identifiers (`resolved_secondary_alt_id`, N = 5)
All 5 rows were resolved to active primary terms while strictly retaining the verbatim cited identifier in `source_go_id`:
1. `MFP:SGA:MOONPROT:0323a8ac464f5ec4`: cited `GO:0016021` $\to$ primary `GO:0016020` (CC, `membrane`).
2. `MFP:SGA:MULTITASKPROTDB_II:5aa20a95296ec4e2`: cited `GO:0016021` $\to$ primary `GO:0016020` (CC, `membrane`).
3. `MFP:SGA:MOONPROT:d4c9712e2e5c87e9`: cited `GO:0001124` $\to$ primary `GO:0006354` (BP, `RNA polymerase II transcription elongation`).
4. `MFP:SGA:MULTITASKPROTDB_II:9bc57b77b98a4893`: cited `GO:0001124` $\to$ primary `GO:0006354` (BP, `RNA polymerase II transcription elongation`).
5. `MFP:SGA:MOONPROT:2612fc7b4c3af600`: cited `GO:0044267` $\to$ primary `GO:0019538` (BP, `protein metabolic process`).

### 5.2 Obsolete Identifiers with Replacement (`obsolete_replaced_by`, N = 6)
All 6 rows recorded the replacement term in `replaced_by_go_id`, but strictly left `resolved_go_id = null` and `derived_aspect = null` per Rule C:
- `GO:0019048` (`SRC_MOONPROT`) $\to$ replaced by `GO:0044003`.
- `GO:0019907` (`SRC_MOONPROT`) $\to$ replaced by `GO:0005675`.
- `GO:0006537` (`SRC_MULTITASKPROTDB_II`) $\to$ replaced by `GO:0097054`.
- `GO:0019419` (`SRC_PLANTMP`, 2 rows) $\to$ replaced by `GO:0000103`.
- `GO:0044237` (`SRC_PLANTMP`) $\to$ replaced by `GO:0008152`.

### 5.3 Obsolete Identifiers without Replacement (`obsolete_unreplaced`, N = 6)
- `GO:0000988` (`SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`): `consider: GO:0005515;GO:0140110` captured as diagnostic string; never accepted as automated equivalence.
- `GO:0006200` (`SRC_MOONPROT`): `consider: GO:0016887` captured as diagnostic string; never accepted as automated equivalence.
- `GO:0010033` (`SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`) and `GO:0006919` (`SRC_MOONPROT`): obsolete without replacement or suggestions.

---

## 6. Automated Test Suite Execution & Portability Analysis

### 6.1 Test Execution Records (Separate Executions)
All unit, contract, and regression tests were executed locally and offline:

- **Run 1: Standalone Enrichment Tests**:
  - Command: `pytest tests/test_go_aspect_enrichment.py -v`
  - Results: **11 passed in 0.68s** (0 failures, 0 warnings, 0 skips).
- **Run 2: Combined Regression Suite**:
  - Command: `pytest tests/test_go_aspect_enrichment.py tests/test_quickgo_concordance.py tests/test_quickgo_raw_contracts.py -v`
  - Results: **50 passed in 0.77s** (initial execution 0.81s; both 100% passing).
  - Breakdown: `test_go_aspect_enrichment.py` (11/11), `test_quickgo_concordance.py` (13/13), `test_quickgo_raw_contracts.py` (26/26).

> [!NOTE]
> Elapsed times reflect separate test invocations (standalone module test vs combined multi-module regression suite), not variance within a single execution.

### 6.2 Test Portability & Clean-Clone Isolation
- **Self-Contained Unit Tests (10/11 tests)**:
  10 tests in `test_go_aspect_enrichment.py` are strictly self-contained. They depend exclusively on the committed synthetic fixture `tests/fixtures/test_go_aspect_enrichment/test_ontology.obo`. They execute and pass in any fresh repository clone with zero external dependencies.
- **Slice & Host-Dependent Integration Test (1/11 tests)**:
  Exactly 1 test (`test_full_pilot_slice_offline_enrichment`) exercises the uncommitted interim slice `source_go_annotations_pilot.csv` against the host ontology file. It is explicitly guarded by:
  `@pytest.mark.skipif(not CANONICAL_OBO_PATH.exists(), reason="Canonical OBO file not available on host")`
- **Portability Boundary**:
  Fresh-clone test portability cannot be claimed from successful local execution alone. Running the full test suite on a clean clone without host fixtures will execute the 10 self-contained unit tests and cleanly skip the integration test.
- **Zero Workstation Dependencies in Library Code**:
  Production library code in `src/mfp_bibliography/go_aspect_enrichment.py` accepts ontology paths as function arguments and contains zero hardcoded absolute workstation paths.

---

## 7. Execution Provenance Audit & Dated Verification Supplement

### 7.1 Generated Manifest Audit (`manifest.json`)
Inspection of the execution manifest generated at `data/interim/pilot/quickgo_slice_enriched/manifest.json`:
- **Captured at Execution Time**:
  - Source input digest: `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda` (353 rows).
  - Pinned ontology digest: `eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391` (`releases/2026-01-23`).
  - Output CSV digest: `e4500d3cf93f2e8861ab7ea5a91a5f9ef55617dd3c6413f4b3abd2c7cf6b204e` (353 rows).
  - Schema digest: `45249395d0e932c71f2d7ef6a5ae8701f7777b89df31d5aecdd82ace1cff8eb6`.
- **Identified Provenance Gap**:
  The generated `manifest.json` omitted the baseline Git HEAD commit and the code digests of the uncommitted implementation files (`go_aspect_enrichment.py` and `build_go_aspect_enrichment.py`).
- **Policy Compliance**:
  In accordance with repository provenance invariants, `manifest.json` is not silently rewritten retroactively. The provenance record is formally supplemented below.

### 7.2 Retrospective Provenance Audit & Timestamp Reconciliation

To preserve strict scientific auditability without inventing history:

1. **Chronological Distinction Across Evidence Sources**:
   - **Pipeline Execution Timestamp**: `2026-11-16 16:59:32 UTC` (`17:59:32 CET`), recorded contemporaneously inside `data/interim/pilot/quickgo_slice_enriched/manifest.json`.
   - **Generated Artifact Modification**: `2026-11-16 17:59:32 CET` (`16:59:32 UTC`), confirmed by local filesystem `stat`.
   - **Erroneous Conversational Annotation**: The prior handoff cited `18:10 UTC / 19:10 CET`. This was an erroneous drafting label caused by an inverted timezone conversion (confusing local CET with UTC, which produced a timestamp `19:10 CET` that was in the future relative to the user's receipt at 18:27 CET). Rather than fabricating a retroactive replacement time, that prior annotation is formally acknowledged here as erroneous.
   - **Current Verification & Reconciliation**: Dated to actual current execution: `2026-11-16 18:38 CET` (`17:38 UTC`).
   - **Historical Manifest Status**: The execution manifest `data/interim/pilot/quickgo_slice_enriched/manifest.json` remains completely unmodified.

2. **Retrospective Code Provenance & Proportionate Limitations**:
   - Because the execution manifest did not capture Git HEAD and code digests contemporaneously, this supplement records a retrospective, post-hoc inspection of code contents.
   - The inspected code digests match the technical commit [`98530b32cd13d0b8ff5b4ea7a626e691d9426d25`](file:///home/alexdoro/repositories/mfp-bibliography):
     - **Committed Technical HEAD**: `98530b32cd13d0b8ff5b4ea7a626e691d9426d25`
     - **Committed Parent Baseline**: `21a3c8ef6bc42ae2f7f51ecc6f9ac6b9d9579b7e`
     - **Module Implementation Digest** (`src/mfp_bibliography/go_aspect_enrichment.py`):
       `6699dc93db11a824167927608b47869d791f58ff14f88cfb1fecd9a8b2c80f40`
     - **CLI Runner Digest** (`scripts/build_go_aspect_enrichment.py`):
       `04f6632cf2f40cad16292f4c6ab34d310d3111a78d6bacdbe1ba52e9a60037c5`
     - **Contract Schema Digest** (`data/curated/derived_source_go_aspects.schema.json`):
       `45249395d0e932c71f2d7ef6a5ae8701f7777b89df31d5aecdd82ace1cff8eb6`
   - **Proportionate Operational Limitation**: Post-hoc digest matching alone does not prove which exact code bytes were executed historically. However, the cryptographic integrity of the inputs (`source_go_annotations_pilot.csv`, SHA-256 `949e5050...`), the ontology snapshot (`eee63704...`), and the generated output (`derived_source_go_aspects_pilot.csv`, SHA-256 `e4500d3c...`) is established independently by verified file hashes.
   - **Execution CLI Command**:
     `python3 scripts/build_go_aspect_enrichment.py --input-csv data/interim/pilot/source_go_annotations_pilot.csv --ontology-obo /home/alexdoro/repositories/mfp-dataset-designer/go-basic.obo --expected-ontology-sha256 eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391 --output-dir data/interim/pilot/quickgo_slice_enriched`

---

## 8. Baseline Immutability Check

Verification confirms that zero historical baseline artifacts were modified or overwritten:
- `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv`: SHA-256 `2a6255c5...` **VERIFIED MATCH**
- `data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv`: SHA-256 `981c592f...` **VERIFIED MATCH**
- `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv`: SHA-256 `12ce77f2...` **VERIFIED MATCH**
- `data/interim/pilot/quickgo_slice/quickgo_reference_concordance_pilot.csv`: SHA-256 `3c723626...` **VERIFIED MATCH**
- `data/interim/pilot/quickgo_slice/manifest.json`: SHA-256 `01c6b54a...` **VERIFIED MATCH**
- `releases/mfp-catalog-candidate-v0.3.0/`: **PRISTINE AND UNMODIFIED**
- Local preservation package `pkg-quickgo-p1-p4-20261116-v1`: **PRISTINE AND UNMODIFIED**
