# Specification: QuickGO Pilot Concordance Recomparison & Transition Analysis (Task PIL-04.1B)

- **Document ID**: `SPEC-PIL-04.1B-CONCORDANCE-RECOMPARISON-001`
- **Feature Directory**: `specs/quickgo-pilot-concordance-recomparison/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Specification; Contract & Implementation Defined)
- **Status**: **Contract Implemented & Verified; Technical Commit Completed; Pipeline Execution Strictly Deferred**
- **Baseline Git HEAD**: `421da7e81c450b4bbeca2c637bbbfe0c8db002b4` (Historical baseline)
- **Technical Commit**: `0789e4a7ccb9a0fb37de258a82c03b851d619e95`
- **Upstream Milestone Dependencies**:
  - Stage P3 Concordance Baseline ([`specs/quickgo-pilot-p3/spec.md`](../quickgo-pilot-p3/spec.md); Commit `4906b2ee0fded7060038b0055d430ee1297c2f6a`)
  - Stage P4 Descriptive Analysis Report ([`docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`](../../docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md))
  - Stage PIL-04.1A GO Aspect Metadata Enrichment ([`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../quickgo-pilot-go-aspect-enrichment/spec.md); Commit `98530b32cd13d0b8ff5b4ea7a626e691d9426d25` / `421da7e81c450b4bbeca2c637bbbfe0c8db002b4`)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Scope, Operational Boundaries & Design Decisions

### 1.1 Scope Authorization
This specification defines the strict scientific, data, and architectural contracts for **Task PIL-04.1B: QuickGO Pilot Concordance Recomparison & Transition Analysis**.

> [!IMPORTANT]
> **Implementation and Execution Gating**:
> In accordance with repository governance and human review authorizations:
> - Authoring this specification package (`spec.md`, `plan.md`, `tasks.md`, `verification.md`) and the contract schema was authorized and completed.
> - Gate 1 implementation and pre-commit Tier A verification were authorized and completed (37 passed, 1 deselected).
> - Technical commit `0789e4a7ccb9a0fb37de258a82c03b851d619e95` landed the implementation code, runner, test suite, and transition schema.
> - Documentary commit for this specification package is authorized in this turn.
> - Tier B regression testing is implemented but unexecuted; frozen-baseline byte-level compatibility remains pending Tier B execution.
> - Pipeline execution (Gate 3), empirical output generation, and descriptive synthesis (Gate 4) remain **strictly unauthorized** pending separate human sign-off; no empirical PIL-04.1B concordance outcomes exist yet.

### 1.2 Formal Design Decisions (PIL-04.1B Contract)
The recomparison engine and data structures specified herein are governed by the following binding design decisions:

1. **Preserve Baseline Exact Textual GO-ID Matching**:
   Concordance set comparisons between source inventories and external QuickGO annotations must continue to operate strictly on verbatim GO identifiers (e.g., `GO:0016021`). No implicit identifier mapping or replacement substitution is performed during set intersection.
2. **Defer Symmetric Identifier Canonicalization**:
   Resolving secondary alternative identifiers (`alt_id`) to primary canonical identifiers remains decoupled from concordance evaluation. Canonicalization across both source claims and external databases is deferred to a future symmetric harmonization milestone to avoid introducing asymmetric bias.
3. **Preserve Valid Source-Declared Aspects**:
   Where a source database explicitly declared a biological aspect (`BP`, `CC`, or `MF`), that declared aspect is preserved as the governing aspect bucket.
4. **Fill Missing or Unassigned Aspects Strictly from Active Ontology Lookups**:
   Annotations lacking a source aspect (e.g., MoonProt unassigned rows, or MultitaskProtDB-II `unassigned` records) receive an aspect assignment **if and only if** the cited identifier resolves to an eligible, active primary Gene Ontology term in the pinned ontology snapshot.
5. **Never Substitute Obsolete Identifiers**:
   Obsolete Gene Ontology identifiers must never be replaced with `replaced_by` targets or mapped via `consider` suggestions. They remain non-substitutable historical assertions.
6. **Preserve Existing Biological Identity Gates**:
   Proteins with unresolved biological identity or flagged taxonomic discrepancies (specifically `P34788`) must remain `concordance_status = "not_evaluable"` with `primary_non_evaluable_reason = "unresolved_biological_identity"`. Ontology aspect derivation does not circumvent or alter biological identity gating.
7. **Absolute Immutability of Historical Outputs & PIL-04.1A Artifacts**:
   The baseline Stage P3 outputs in `data/interim/pilot/quickgo_slice/` and the PIL-04.1A enrichment artifacts in `data/interim/pilot/quickgo_slice_enriched/` are frozen, immutable baselines. The recomparison pipeline must strictly refuse to overwrite or mutate any existing artifact in those directories.
8. **Isolated Future Output Directory**:
   All prospective outputs of Task PIL-04.1B must be isolated in a dedicated, distinct directory: `data/interim/pilot/quickgo_slice_recomparison/`.

---

## 2. Baseline Reconciliation: 10 Evaluable Comparison Units

### 2.1 Resolution of Enumeration Discrepancy
Preliminary review drafts of the PIL-04.1B proposal stated that 10 comparison units were evaluable in the baseline, but the informal text enumerated only 9:
- Multitask `Q42525`: BP, MF (2 units)
- Multitask `Q9Y3E5`: BP, MF (2 units)
- Multitask `P0AFW0`: BP, CC, MF (3 units)
- PlantMP `Q42525`: BP, MF (2 units)
Total informal count: $2 + 2 + 3 + 2 = 9\text{ units}$.

A direct, read-only audit of the frozen baseline dataset (`data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv`) resolves this discrepancy definitively by identifying two compensating errors in the informal draft:

1. **Erroneous Inclusion of `P0AFW0` CC**:
   In the frozen baseline matrix, `P0AFW0` / `SRC_MULTITASKPROTDB_II` has **zero** source terms for Cellular Component (`source_terms_count = 0`). Consequently, under both Policy B and Policy C, this unit is `concordance_status = "not_evaluable"` with `primary_non_evaluable_reason = "source_record_no_terms_aspect"`. Multitask `P0AFW0` provides only **2** evaluable units (BP and MF), not 3.
2. **Erroneous Omission of `Q42525` CC and `Q9Y3E5` CC**:
   In the frozen baseline matrix, both `Q42525` / Multitask and `Q9Y3E5` / Multitask have non-empty, valid Cellular Component inventories with non-zero overlap and valid Jaccard similarities:
   - `(Q42525, SRC_MULTITASKPROTDB_II, CC)`: $|S| = 9$, $|Q| = 7$, $|S \cap Q| = 4$, $J = 0.3333$ (`evaluable`).
   - `(Q9Y3E5, SRC_MULTITASKPROTDB_II, CC)`: $|S| = 4$, $|Q| = 4$, $|S \cap Q| = 3$, $J = 0.6000$ (`evaluable`).
   Both were omitted from the informal narrative text.

### 2.2 Complete Roster of Actually Evaluable Baseline Units
Across the 36 comparison units ($12\text{ pairs} \times 3\text{ aspects}$) evaluated in Stage P3, exactly **10 units** (20 rows, exactly 10 under Policy B and 10 under Policy C) are evaluable:

| Unit Index | Accession | Canonical Gene / Protein | Source Database (`source_id`) | Aspect | Policy B Status ($J_B$) | Policy C Status ($J_C$) | Baseline Concordance ID |
|:---:|---|---|---|:---:|:---:|:---:|---|
| **1** | `P0AFW0` | RfaH (*E. coli*) | `SRC_MULTITASKPROTDB_II` | `BP` | `evaluable` (0.4000) | `evaluable` (0.4000) | `MFP:CONC:P0AFW0:MFP:U:9023923ecdd9d57f:SRC_MULTITASKPROTDB_II:BP:*` |
| **2** | `P0AFW0` | RfaH (*E. coli*) | `SRC_MULTITASKPROTDB_II` | `MF` | `evaluable` (0.4444) | `evaluable` (0.5000) | `MFP:CONC:P0AFW0:MFP:U:9023923ecdd9d57f:SRC_MULTITASKPROTDB_II:MF:*` |
| **3** | `Q42525` | HXK1 (*A. thaliana*) | `SRC_MULTITASKPROTDB_II` | `BP` | `evaluable` (0.2917) | `evaluable` (0.3043) | `MFP:CONC:Q42525:MFP:U:8272bae0e8df8149:SRC_MULTITASKPROTDB_II:BP:*` |
| **4** | `Q42525` | HXK1 (*A. thaliana*) | `SRC_MULTITASKPROTDB_II` | `CC` | `evaluable` (0.3333) | `evaluable` (0.3333) | `MFP:CONC:Q42525:MFP:U:8272bae0e8df8149:SRC_MULTITASKPROTDB_II:CC:*` |
| **5** | `Q42525` | HXK1 (*A. thaliana*) | `SRC_MULTITASKPROTDB_II` | `MF` | `evaluable` (0.4615) | `evaluable` (0.5000) | `MFP:CONC:Q42525:MFP:U:8272bae0e8df8149:SRC_MULTITASKPROTDB_II:MF:*` |
| **6** | `Q42525` | HXK1 (*A. thaliana*) | `SRC_PLANTMP` | `BP` | `evaluable` (0.0938) | `evaluable` (0.0968) | `MFP:CONC:Q42525:MFP:U:8272bae0e8df8149:SRC_PLANTMP:BP:*` |
| **7** | `Q42525` | HXK1 (*A. thaliana*) | `SRC_PLANTMP` | `MF` | `evaluable` (0.2308) | `evaluable` (0.2500) | `MFP:CONC:Q42525:MFP:U:8272bae0e8df8149:SRC_PLANTMP:MF:*` |
| **8** | `Q9Y3E5` | PTH2 / Bit1 (*H. sapiens*) | `SRC_MULTITASKPROTDB_II` | `BP` | `evaluable` (0.5000) | `evaluable` (0.5000) | `MFP:CONC:Q9Y3E5:MFP:U:c382ca456ad5a4db:SRC_MULTITASKPROTDB_II:BP:*` |
| **9** | `Q9Y3E5` | PTH2 / Bit1 (*H. sapiens*) | `SRC_MULTITASKPROTDB_II` | `CC` | `evaluable` (0.6000) | `evaluable` (0.6000) | `MFP:CONC:Q9Y3E5:MFP:U:c382ca456ad5a4db:SRC_MULTITASKPROTDB_II:CC:*` |
| **10** | `Q9Y3E5` | PTH2 / Bit1 (*H. sapiens*) | `SRC_MULTITASKPROTDB_II` | `MF` | `evaluable` (0.3333) | `evaluable` (0.3333) | `MFP:CONC:Q9Y3E5:MFP:U:c382ca456ad5a4db:SRC_MULTITASKPROTDB_II:MF:*` |

### 2.3 Distinction: Structural Invariants vs. Pre-Execution Expectations
To preserve scientific integrity:
- **Mandatory Structural Invariants**: The recomparison table must contain exactly 72 rows corresponding 1:1 to the frozen comparison universe. Exact key identity, non-null set count reportability, deterministic diagnostic precedence, and schema compliance are mandatory pass/fail criteria.
- **Pre-Execution Hypotheses (Non-Mandatory Outcomes)**: Preliminary projections suggesting that "42 rows will become evaluable" or that there will be a "+22 evaluable row gain" are **pre-execution hypotheses**, NOT contractual implementation acceptance criteria.
  - Actual evaluability depends on whether derived terms map into nonempty aspect buckets, whether database unlinking persists (`E6KMA1`), whether biological identity gates remain closed (`P34788`), and whether external QuickGO inventories are non-empty.
  - Scientific results must be observed empirically and reported objectively, never manufactured or asserted as synthetic test assertions.

---

## 3. Strict Obsolete-Term Semantics

To ensure consistent curatorial behavior across both declared and derived aspect pipelines, the recomparison engine enforces four explicit cases:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   OBSOLETE-TERM GO ASPECT POLICY                       │
├────────────────────────────────────────────────────────────────────────┤
│ Case A: Declared Aspect + Obsolete GO ID                               │
│   ──► Retain in declared aspect; verbatim source GO ID; no exclusion   │
│                                                                        │
│ Case B: Missing/Unassigned Aspect + Obsolete GO ID                     │
│   ──► Aspect remains null; no active bucket assignment                 │
│                                                                        │
│ Case C: Missing/Unassigned Aspect + Active GO ID                       │
│   ──► Bucket into derived aspect; retain verbatim source GO ID         │
│                                                                        │
│ Case D: Unknown / Malformed GO ID                                      │
│   ──► Declared: retained in declared aspect with diagnostic flag       │
│   ──► Missing: aspect remains null; omitted from aspect buckets        │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Case A: Valid Declared Source Aspect + Obsolete GO ID
- **Condition**: Source record declared a valid aspect (`BP`, `CC`, or `MF`), but the cited GO ID is obsolete in the pinned ontology snapshot (`mapping_status` in `{"obsolete_replaced_by", "obsolete_unreplaced"}`).
- **Semantics**:
  1. The annotation is **retained** in its source-declared aspect bucket.
  2. The term used for exact textual concordance matching is the verbatim `source_go_id`.
  3. Obsolescence is recorded as metadata/diagnostics, but **no new ontology-status exclusion is introduced**.
  4. Baseline inclusion/filtering semantics are strictly preserved for this aspect-only increment.

### 3.2 Case B: Missing/Unassigned Source Aspect + Obsolete GO ID
- **Condition**: Source record has missing or unassigned aspect (`source_declared_aspect` is null or `"unassigned"`), and the cited GO ID is obsolete in the ontology snapshot.
- **Semantics**:
  1. In PIL-04.1A, obsolete terms receive `derived_aspect = null`.
  2. In PIL-04.1B, the engine **must not** derive an active aspect, and **must never** follow `replaced_by_go_id` or `consider_go_ids` metadata to guess an aspect.
  3. The annotation remains unassigned to any aspect (`aspect = null`) and is **omitted from all aspect comparison units** (`BP`, `CC`, `MF`).

### 3.3 Case C: Missing/Unassigned Source Aspect + Active GO ID
- **Condition**: Source record has missing or unassigned aspect, and the cited GO ID resolves to an active primary term (or secondary `alt_id` mapping to an active primary term) in the ontology snapshot (`mapping_status` in `{"resolved_primary", "resolved_secondary_alt_id"}`).
- **Semantics**:
  1. The annotation is assigned to the aspect bucket matching `derived_aspect` (`BP`, `CC`, or `MF`).
  2. For concordance matching against QuickGO, the term used is the **verbatim `source_go_id`** (preserving baseline exact textual matching).
  3. Canonical replacement or secondary-to-primary substitution is **not** performed during set operations.

### 3.4 Case D: Unknown or Malformed GO ID
- **Condition**: The cited GO ID is not present in the pinned ontology snapshot or is syntactically malformed (`mapping_status` in `{"unresolved_unknown_id", "unresolved_malformed_id"}`).
- **Semantics**:
  1. **Declared Aspect**: If the source explicitly declared an aspect, the term is retained under that declared aspect using verbatim `source_go_id`, logging a diagnostic note.
  2. **Missing/Unassigned Aspect**: If the source had no declared aspect, no aspect can be derived (`derived_aspect = null`). The term cannot be assigned to `BP`, `CC`, or `MF` and is excluded from aspect comparison sets.

### 3.5 Repository Contract Alignment
This policy strictly adheres to repository contracts:
- [ADR-002](../../docs/decisions/ADR-002-raw-data-immutability.md) (verbatim values preserved).
- [`AGENTS.md`](../../AGENTS.md) §5 (no fabricated GO mappings; no Cartesian product functional synthesis).
- Stage P3 Concordance Policy ([`specs/quickgo-pilot-p3/spec.md`](../quickgo-pilot-p3/spec.md)).
There is zero conflict between this policy and repository invariants.

---

## 4. Join Integrity & Conflict Propagation

### 4.1 Annotation Matching & Multiplicity Preservation
Every source annotation in `source_go_annotations_pilot.csv` (353 rows) must be joined to its enrichment record in `derived_source_go_aspects_pilot.csv` (353 rows):

1. **Mandatory Primary Join Key**:
   The join must be executed strictly on the deterministic primary key `annotation_id` (`MFPB_SOURCE_GO_ANNOTATION_V1`, pattern `^MFP:SGA:[A-Za-z0-9_]+:[0-9a-f]{16}$`, e.g. `MFP:SGA:MOONPROT:21231b6ec0a0696d`).
   - Both input datasets are required by their respective schemas (`source_go_annotations.schema.json` and `derived_source_go_aspects.schema.json`) to provide a valid, non-null, unique `annotation_id` on every row.
   - The join engine enforces an exact **1:1 bijective match** across all 353 rows ($N = 353$).
2. **Prohibition of Fallback Join Keys**:
   No heuristic or secondary fallback key (e.g. tuple matching on raw text or indices) is permitted. A missing, null, or unindexed `annotation_id` represents an unrecoverable contract violation in the input artifacts, not a condition to be masked by fallback matching.
3. **Preservation of Multiplicity**:
   - Distinct annotation rows must never be collapsed through dictionary lookups or grouped hash maps.
   - Every input row must participate in exactly one joined row.
4. **Cross-Table Invariant & Source-Declared Aspect Verification**:
   The join engine must verify that source-native fields are identical across both tables for each `annotation_id`:
   - `protein_id` in source == `protein_id` in enrichment
   - `source_id` in source == `source_id` in enrichment
   - `source_record_id` in source == `source_record_id` in enrichment
   - `go_id` in source == `source_go_id` in enrichment
   - Source-declared aspect verification across differing column names:
     In `source_go_annotations_pilot.csv`, the source-declared aspect is stored under column `go_aspect` (enum `["BP", "MF", "CC", "unassigned", null]` per `source_go_annotations.schema.json`).
     In `derived_source_go_aspects_pilot.csv`, it is stored under column `source_declared_aspect` (enum `["BP", "CC", "MF", "unassigned", null]` per `derived_source_go_aspects.schema.json`).
     The join engine must verify that `row_enrichment["source_declared_aspect"] == parse_csv_value(row_source["go_aspect"])` (normalizing empty strings to `null`). Any divergence must trigger an immediate fatal join error.

### 4.2 Fail-Fast Join Integrity Checks
The recomparison engine must abort immediately with a non-zero exit code if any of the following join integrity violations are detected:
- **Missing Enrichment Record**: Any source annotation lacks an enrichment record with matching `annotation_id`.
- **Duplicated Enrichment Record**: More than one enrichment record shares the same `annotation_id`.
- **Contradictory Record**: Invariant source fields (`protein_id`, `source_id`, `source_record_id`, `go_id` vs `source_go_id`, or `go_aspect` vs `source_declared_aspect`) diverge between source and enrichment tables.
- **Unexpected Record**: The enrichment table contains an `annotation_id` not present in the source table.

### 4.3 Declared vs. Derived Aspect Conflict Propagation & Schema Compatibility

#### 4.3.1 Verified Upstream Status Representation
In Task PIL-04.1A, active comparable rows showed zero aspect mismatches ($0/200 = 0.0\%$). However, to ensure rigorous general contract integrity, the exact upstream contract is verified against the committed `derived_source_go_aspects.schema.json` and `src/mfp_bibliography/go_aspect_enrichment.py`:
- The committed `mapping_status` enum contains exactly 7 values:
  1. `resolved_primary`
  2. `resolved_secondary_alt_id`
  3. `obsolete_replaced_by`
  4. `obsolete_unreplaced`
  5. `unresolved_unknown_id`
  6. `unresolved_malformed_id`
  7. `conflict_source_ontology_aspect_mismatch`
- Upstream conflict representation: When a source-declared aspect (`BP`, `CC`, or `MF`) contradicts the ontology-derived aspect from the term's namespace, PIL-04.1A records:
  - `mapping_status = "conflict_source_ontology_aspect_mismatch"`
  - `source_declared_aspect` retains the verbatim source declaration
  - `derived_aspect` retains the ontology-derived aspect
  - `notes` records the explicit mismatch diagnostic.

#### 4.3.2 Schema Compatibility Resolution for `quickgo_concordance.schema.json`
The recomputed concordance table `quickgo_concordance_pilot_recomputed.csv` must validate against the existing, unmutated `data/curated/quickgo_concordance.schema.json`.
Inspection of `quickgo_concordance.schema.json` reveals that `primary_non_evaluable_reason` has a closed enum of 11 allowed values (or null):
`"unresolved_biological_identity"`, `"source_record_outside_slice"`, `"source_input_unavailable"`, `"source_aspect_indeterminate"`, `"source_record_no_terms_aspect"`, `"accession_absent_from_capture"`, `"accession_unlinked_in_capture"`, `"ambiguous_entity_mapping"`, `"external_zero_annotations_overall"`, `"external_zero_annotations_aspect"`, and `"empty_after_filtering"`.

Notice that `source_aspect_conflict` is **not** an allowed value in this enum. To ensure strict schema compatibility without mutating historical schemas or generating invalid records:
1. **Quarantine Rule**:
   If an annotation row carries `mapping_status = "conflict_source_ontology_aspect_mismatch"`, it is quarantined from both aspect buckets for that source record.
2. **Indeterminate Unit Assignment**:
   A conflicting annotation compromises the curatorial completeness of the source inventory. Therefore, for the affected `(accession, source_id)` pair, both the declared aspect unit and the conflicting derived aspect unit become **indeterminate**:
   - `source_inventory_status = "indeterminate"` (valid enum in `quickgo_concordance.schema.json`)
   - `concordance_status = "not_evaluable"`
   - `primary_non_evaluable_reason = "source_aspect_indeterminate"` (valid enum in `quickgo_concordance.schema.json`; semantically exact because the true aspect assignment of the inventory cannot be deterministically resolved).
3. **Explicit Conflict Diagnostics in Secondary Reasons**:
   To preserve explicit conflict diagnostics without violating the schema, `"source_aspect_conflict"` is appended to `secondary_non_evaluable_reasons` (e.g. `"source_aspect_indeterminate;source_aspect_conflict"`). The schema allows any string or null for `secondary_non_evaluable_reasons`.
4. **No Disguising as Absent Terms**:
   A conflict must **never** be disguised as `source_record_no_terms_aspect` or `empty_after_filtering`.
5. **Future Versioned Schema Option**:
   If downstream requirements ever mandate promoting `source_aspect_conflict` to a first-class `primary_non_evaluable_reason`, that would require a new versioned schema (`data/curated/quickgo_concordance_recomputed.schema.json` under scheme `MFPB_QUICKGO_CONCORDANCE_V2`). In this pilot increment, the historical schema is preserved unchanged.

---

## 5. Transition-Table Contract & Semantics

### 5.1 Fixed Universe Cardinality & Key Correspondence
The transition matrix evaluates changes between the frozen Stage P3 baseline concordance matrix and the PIL-04.1B recomparison concordance matrix.
- Cardinality: **exactly 72 rows** corresponding 1:1 to the 72 comparison units ($12\text{ pairs} \times 3\text{ aspects} \times 2\text{ policies}$).
- Key Relationship:
  - Baseline Concordance ID: `MFP:CONC:<accession>:<protein_id>:<source_id>:<aspect>:<policy_id>`
  - Recomputed Concordance ID: `MFP:CONC:<accession>:<protein_id>:<source_id>:<aspect>:<policy_id>`
  - Transition Row ID: `MFP:TRNS:<accession>:<protein_id>:<source_id>:<aspect>:<policy_id>`
  Every transition row corresponds deterministically to the unique 5-tuple `(accession, protein_id, source_id, aspect, policy_id)`.

### 5.2 Orthogonal Transition Indicators & Set-Content Sensitivity
A row must **never** be classified as "unchanged" solely because its score or evaluability is unchanged. Identical Jaccard values ($J_{\text{recomp}} = J_{\text{base}}$) do not establish identical inventories or identical analytical records (e.g., term sets can change content while preserving cardinality, or counts can shift while ratio remains identical).

The transition contract separates five orthogonal analytical dimensions:
1. **Evaluability Transition** (`evaluability_transition`):
   Enum: `["remains_evaluable", "newly_evaluable", "becomes_non_evaluable", "remains_non_evaluable"]`.
2. **Diagnostic Reason Transition** (`primary_reason_transition`):
   Enum: `["unchanged_null", "unchanged_reason", "reason_changed", "became_evaluable", "became_non_evaluable"]`.
3. **Inventory Count Deltas**:
   Integer deltas: `delta_source_terms_count`, `delta_quickgo_terms_count`, `delta_exact_overlap_count`, `delta_union_terms_count`.
4. **Source Set-Content Sensitivity** (`source_set_content_changed`):
   Boolean flag (`true` if the set of source GO IDs in recomparison $S_{\text{recomp}} \neq S_{\text{base}}$, `false` if identical). Detects term substitutions or reallocations even when total count $|S|$ is unchanged.
5. **Metric Transition** (`metric_transition`):
   Explicitly score-specific enum:
   - `score_identical`: Both non-null and $\Delta J = 0.0000$.
   - `score_increased`: Both non-null and $\Delta J > 0.0000$.
   - `score_decreased`: Both non-null and $\Delta J < 0.0000$.
   - `score_newly_defined`: $J_{\text{base}} = \text{null}$ and $J_{\text{recomp}} \neq \text{null}$.
   - `score_became_null`: $J_{\text{base}} \neq \text{null}$ and $J_{\text{recomp}} = \text{null}$.
   - `remains_null`: Both $J_{\text{base}} = \text{null}$ and $J_{\text{recomp}} = \text{null}$.

### 5.3 Score Delta Precision Consistency
Both baseline and recomparison concordance matrices round and serialize Jaccard similarities to 4 decimal places ($0.0000$ to $1.0000$).
To ensure consistency across serialization, schema ranges, and programmatic checks, the score delta is defined strictly on the serialized four-decimal scores:
$$\Delta J = \begin{cases}
\text{round}(J_{\text{recomp}} - J_{\text{base}}, 4) & \text{if } J_{\text{base}} \neq \text{null} \land J_{\text{recomp}} \neq \text{null} \\
\text{null} & \text{otherwise}
\end{cases}$$

### 5.4 Overall Transition Classification with Explicit Precedence
The field `overall_transition_classification` synthesizes all orthogonal dimensions into an unambiguous summary state governed by strict evaluation precedence:

```
┌────────────────────────────────────────────────────────────────────────┐
│             OVERALL TRANSITION CLASSIFICATION PRECEDENCE               │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Evaluability Changed?                                               │
│    ├── baseline not_evaluable -> recomp evaluable  ──► newly_evaluable │
│    └── baseline evaluable -> recomp not_evaluable  ──► becomes_non_    │
│                                                        evaluable       │
│ 2. Both Evaluable?                                                     │
│    ├── ΔJ > 0.0000 ────────► evaluable_score_increased                 │
│    ├── ΔJ < 0.0000 ────────► evaluable_score_decreased                 │
│    ├── ΔJ == 0.0000 AND (any count delta != 0 OR source_set_changed)   │
│    │               ────────► evaluable_score_identical_inventory_     │
│    │                         changed                                   │
│    └── ΔJ == 0.0000 AND all count deltas == 0 AND !source_set_changed  │
│                    ────────► evaluable_fully_identical                 │
│ 3. Both Non-Evaluable?                                                 │
│    ├── primary_reason differs ──► non_evaluable_reason_changed         │
│    ├── secondary_reasons, inventory_status, or count deltas differ     │
│    │                          ──► non_evaluable_diagnostics_or_        │
│    │                              inventory_changed                    │
│    └── all diagnostics, inventory status, counts, and sets identical   │
│                               ──► non_evaluable_fully_identical        │
└────────────────────────────────────────────────────────────────────────┘
```

#### Analytical Fields Determining "Unchanged"
A row is considered analytically identical (`evaluable_fully_identical` or `non_evaluable_fully_identical`) if and only if all analytical fields match:
`concordance_status`, `primary_non_evaluable_reason`, `secondary_non_evaluable_reasons`, `source_inventory_status`, `quickgo_inventory_status`, `source_terms_count`, `quickgo_terms_count`, `exact_overlap_count`, `union_terms_count`, `source_only_count`, `quickgo_only_count`, `jaccard_similarity`, and underlying source GO ID sets. Runtime metadata (timestamps, run duration, platform environment) are strictly excluded from analytical identity.

### 5.5 Transition Table Field Contract
The transition schema is defined at `data/curated/quickgo_concordance_transition.schema.json` (committed in technical commit `0789e4a7ccb9a0fb37de258a82c03b851d619e95`):

| Field Name | Type | Nullable | Pattern / Enum / Constraints | Description |
|---|:---:|:---:|---|---|
| `transition_id` | string | No | `^MFP:TRNS:[A-Z0-9]+:MFP:(U:[0-9a-f]{16}\|F:[A-Za-z0-9_]+:[0-9a-f]{16}):SRC_[A-Z0-9_]+:(BP\|MF\|CC):[a-z_]+$` | Unique transition key. |
| `accession` | string | No | `^[A-Z0-9]{6,10}$` | Queried UniProtKB accession. |
| `protein_id` | string | No | `^MFP:(U:[0-9a-f]{16}\|F:[A-Za-z0-9_]+:[0-9a-f]{16})$` | Catalog entity identifier. |
| `source_id` | string | No | `^SRC_[A-Z0-9_]+$` | Source database identifier. |
| `aspect` | string | No | `["BP", "MF", "CC"]` | Evaluated GO aspect. |
| `policy_id` | string | No | `["captured_inventory_overlap", "filtered_descriptive_overlap"]` | Concordance policy. |
| `baseline_concordance_status` | string | No | `["evaluable", "not_evaluable"]` | Evaluability in frozen Stage P3 baseline. |
| `recomparison_concordance_status` | string | No | `["evaluable", "not_evaluable"]` | Evaluability in PIL-04.1B recomparison. |
| `evaluability_transition` | string | No | `["remains_evaluable", "newly_evaluable", "becomes_non_evaluable", "remains_non_evaluable"]` | Evaluability transition classification. |
| `baseline_primary_reason` | string | Yes | Enum from baseline concordance schema | Primary reason in baseline, or null if evaluable. |
| `recomparison_primary_reason` | string | Yes | Enum from baseline concordance schema | Primary reason in recomparison, or null. |
| `primary_reason_transition` | string | No | `["unchanged_null", "unchanged_reason", "reason_changed", "became_evaluable", "became_non_evaluable"]` | Diagnostic reason transition. |
| `baseline_source_terms_count` | integer | Yes | $\ge 0$ | Source term count in baseline. |
| `recomparison_source_terms_count` | integer | Yes | $\ge 0$ | Source term count in recomparison. |
| `delta_source_terms_count` | integer | Yes | Integer or null if either side is null | Net change in source terms ($S_{\text{recomp}} - S_{\text{base}}$). |
| `baseline_quickgo_terms_count` | integer | Yes | $\ge 0$ | QuickGO term count in baseline. |
| `recomparison_quickgo_terms_count` | integer | Yes | $\ge 0$ | QuickGO term count in recomparison. |
| `delta_quickgo_terms_count` | integer | Yes | Integer or null if either side is null | Net change in QuickGO terms. |
| `baseline_exact_overlap_count` | integer | Yes | $\ge 0$ | Exact intersection count in baseline. |
| `recomparison_exact_overlap_count` | integer | Yes | $\ge 0$ | Exact intersection count in recomparison. |
| `delta_exact_overlap_count` | integer | Yes | Integer or null if either side is null | Net change in exact intersection count. |
| `baseline_union_terms_count` | integer | Yes | $\ge 0$ | Union count in baseline. |
| `recomparison_union_terms_count` | integer | Yes | $\ge 0$ | Union count in recomparison. |
| `delta_union_terms_count` | integer | Yes | Integer or null if either side is null | Net change in union count. |
| `source_set_content_changed` | boolean | No | `true` or `false` | True if source GO ID set content differs ($S_{\text{recomp}} \neq S_{\text{base}}$). |
| `baseline_jaccard_similarity` | number | Yes | $0.0 \le J \le 1.0$ | Jaccard score in baseline (4 decimals). |
| `recomparison_jaccard_similarity` | number | Yes | $0.0 \le J \le 1.0$ | Jaccard score in recomparison (4 decimals). |
| `delta_jaccard_similarity` | number | Yes | $-1.0 \le \Delta J \le +1.0$ | Null-safe score difference ($J_{\text{recomp}} - J_{\text{base}}$, 4 decimals). |
| `metric_transition` | string | No | `["score_identical", "score_increased", "score_decreased", "score_newly_defined", "score_became_null", "remains_null"]` | Score-specific shift category. |
| `overall_transition_classification` | string | No | `["newly_evaluable", "becomes_non_evaluable", "evaluable_score_increased", "evaluable_score_decreased", "evaluable_score_identical_inventory_changed", "evaluable_fully_identical", "non_evaluable_reason_changed", "non_evaluable_diagnostics_or_inventory_changed", "non_evaluable_fully_identical"]` | Comprehensive summary state. |
| `notes` | string | Yes | — | Diagnostic and curatorial notes. |

### 5.6 Separation of JSON Schema and Programmatic Validation
To prevent overpromising on validation mechanisms:
1. **JSON Schema (Draft 2020-12) Scope**:
   Schema validation operates strictly at the individual row level:
   - Data types, required fields, and nullability.
   - String regex patterns (e.g. `transition_id`, `protein_id`, `accession`).
   - Closed enum memberships (e.g. `evaluability_transition`, `metric_transition`, `overall_transition_classification`).
   - Numerical ranges ($0.0 \le J \le 1.0$, $-1.0 \le \Delta J \le +1.0$, non-negative integers).
   - Row-level conditionals (e.g. if `baseline_concordance_status == "evaluable"`, then `baseline_primary_reason` must be null).
   - **Prerequisite**: Prior to JSON Schema validation, raw CSV records must be parsed: empty strings `""` converted to `None`/`null`, integer strings to `int`, and decimal strings to `float`.
2. **Programmatic Validation Scope (Python Validators & Automated Tests)**:
   Invariants beyond the capability of JSON Schema must be enforced by explicit Python validators:
   - Arithmetic equality of deltas: $\Delta S = S_{\text{recomp}} - S_{\text{base}}$, $\Delta J = \text{round}(J_{\text{recomp}} - J_{\text{base}}, 4)$, etc.
   - Cross-row uniqueness: verifying that all 72 `transition_id` keys are distinct across the table.
   - Foreign-key integrity: verifying that all 72 keys match the baseline concordance matrix and candidate catalog.
   - Fixed universe identity: asserting that the table contains exactly the 72 expected comparison units with zero missing, extra, or duplicated keys.
   - Precedence logic validation for `overall_transition_classification`.

---

## 6. Prospective Runtime Provenance, Determinism & Safe Execution

### 6.1 Prospective Provenance Architecture
Every prospective execution of PIL-04.1B must record an execution manifest (`data/interim/pilot/quickgo_slice_recomparison/manifest.json`) containing complete, verifiable runtime provenance:

1. **Direct Input Dependencies**:
   - `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` (SHA-256 `12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7`)
   - `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv` (SHA-256 `2a6255c5059545d8b1bab06a6d73872d2a064add1c0dd7b25097bd95e47012de`)
   - `data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv` (SHA-256 `981c592f12bceb02e2c7a6404126dc7ad55053b2bd6383919658a5423241b9be`)
   - `data/interim/pilot/source_go_annotations_pilot.csv` (SHA-256 `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda`)
   - `data/interim/pilot/quickgo_slice_enriched/derived_source_go_aspects_pilot.csv` (SHA-256 `e4500d3cf93f2e8861ab7ea5a91a5f9ef55617dd3c6413f4b3abd2c7cf6b204e`)
   - `data/interim/pilot/functional_coverage_pilot.csv` (SHA-256 `c29d28712c613211c6183f49ef304a63d94dd64a40de2ff682641037e2573e8d`)
   - `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv` (SHA-256 `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc`)
2. **Upstream Lineage References**:
   - PIL-04.1A Run Manifest (`data/interim/pilot/quickgo_slice_enriched/manifest.json`, SHA-256 `5fe29c5fdefbbe0d14b755844dcecf9b6ca29afc460eb4aec7b3479b596b077f`)
   - Pinned Ontology Snapshot (`go-basic.obo`, data-version `releases/2026-01-23`, SHA-256 `eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391`)
   - P3 Pilot Run Manifest (`data/interim/pilot/quickgo_slice/manifest.json`, SHA-256 `01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7`)
3. **Execution Environment Provenance**:
   - Current Git HEAD commit hash.
   - Working tree status (`clean` or `dirty`). If uncommitted modifications exist in the execution code, the runner must record `execution_mode: "offline_uncommitted_working_tree"` and compute and record individual SHA-256 digests for all executed code modules and schemas.
   - Exact CLI parameters, active flags, and runtime configuration.
   - ISO 8601 UTC timestamp of execution.
   - Python version, runtime platform, and dependency library versions.

### 6.2 Determinism Requirements
- **Analytical Determinism**: For fixed input CSVs, all emitted analytical CSV artifacts (`quickgo_concordance_pilot_recomputed.csv`, `quickgo_concordance_transition_pilot.csv`) must be **100% bitwise deterministic** and reproducible across platforms.
- **Manifest Flexibility**: Runtime manifests contain run-specific timestamps, execution durations, and platform environments. Byte-identical manifest digests across different execution runs are therefore not required, but input and output dataset digests recorded within them must be exact.

### 6.3 Safe Publication, Staging & Authorization Invariants

1. **Strict Read-Only Enforcement on Historical Directories**:
   Historical baseline directories `data/interim/pilot/quickgo_slice/` and `data/interim/pilot/quickgo_slice_enriched/` are strictly read-only. The runner must enforce hardcoded path checks ensuring that output files, temporary files, and logs are never written to those locations.
2. **Explicit Authorization vs. CLI Flags**:
   Execution of the recomparison pipeline is strictly deferred to **Gate 3** and requires explicit human sign-off. A CLI overwrite flag (such as `--overwrite-recomparison`) is a mechanical safety interlock only; **it does not constitute human authorization**.
3. **Refusal on Existing Target Directory**:
   For the initial pilot execution, if the target directory `data/interim/pilot/quickgo_slice_recomparison/` already exists, execution must **refuse and abort immediately**. This prevents accidental modification or partial clobbering of previously evaluated artifacts.
4. **Run-Unique Staging Path & Crash Cleanup**:
   Outputs must be staged in an isolated, run-unique staging directory incorporating a high-resolution timestamp and process ID:
   `data/interim/pilot/.staging_recomparison_<timestamp>_<pid>/`
   - Using run-unique paths prevents collisions across concurrent or sequential test executions.
   - If an error, assertion failure, or validation failure occurs, cleanup logic must purge **only** the run-unique staging directory created by that specific run, leaving all sibling and destination directories completely untouched.
5. **Path Resolution & Overlap Checks**:
   Before writing any file, the runner must resolve canonical absolute paths (`Path.resolve()`) for all input, staging, and destination directories. It must verify that:
   - Staging and destination paths do not collide or nest within any historical input directory.
   - Staging and destination directories are mutually disjoint.
6. **Publication Strategy & POSIX Replacement Limitations**:
   Standard POSIX filesystem operations (`os.replace` / `Path.rename`) do not support atomic replacement of an existing, non-empty directory. The publication strategy must honestly accommodate this limitation without overpromising:
   - *Case 1 (Target does not exist)*: Staged files and manifest are fully validated against schemas and programmatic validators. Upon complete pass, the staging directory is moved atomically to the target directory via `Path.rename()`.
   - *Case 2 (Target exists and overwrite authorized by human Gate 3 sign-off)*: The pipeline validates all outputs in the staging directory first. Only after 100% successful validation, the existing target directory is removed or backed up to an archival path, and the staging directory is moved into the destination location.
   - *Validation Failure*: If validation fails at any step, the target directory is left completely intact, and the staging directory is wiped. Partial, unverified, or invalid outputs are never published to the target path.
