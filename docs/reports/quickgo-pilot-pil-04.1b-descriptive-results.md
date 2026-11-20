# Stage PIL-04.1B Technical Report: Descriptive Concordance Synthesis & Transition Analysis

- **Document ID**: `REPORT-QUICKGO-PILOT-PIL-04.1B-DESCRIPTIVE-001`
- **Feature Directory**: `specs/quickgo-pilot-concordance-recomparison/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 6 Technical Completion Report (Reporting and Synthesis Only; Not Implementation Approval)
- **Status**: **Completed Descriptive Report** (Gate 4 human approval granted for v0 execution)
- **Execution Commit HEAD**: `41521ba5d55636a3b74ed6f6616501542543a48d`
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5
- **Upstream References**:
  - Stage P3 Concordance Baseline Report & Matrix ([`specs/quickgo-pilot-p3/spec.md`](../../specs/quickgo-pilot-p3/spec.md); `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv`)
  - Stage P4 Descriptive Analysis Report ([`docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`](quickgo-pilot-p4-descriptive-analysis-report.md))
  - Stage PIL-04.1A GO Aspect Metadata Enrichment ([`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md); `derived_source_go_aspects_pilot.csv`)
  - Stage PIL-04.1B Recomparison Specification ([`specs/quickgo-pilot-concordance-recomparison/spec.md`](../../specs/quickgo-pilot-concordance-recomparison/spec.md))

---

## Executive Summary

This report delivers the descriptive analytical synthesis for **Stage PIL-04.1B: QuickGO Pilot Concordance Recomparison & Transition Analysis**. The analysis evaluates the empirical impact of incorporating ontology-derived Gene Ontology (GO) aspect metadata (produced in Task PIL-04.1A) into the multi-source concordance evaluation pipeline against external QuickGO annotations (`MFP_QuickV1`).

The evaluation operates on the purposive **eight-protein cohort** across three curated source databases (MultitaskProtDB-II, MoonProt, PlantMP) and two concordance policies (Policy B: raw captured inventory overlap; Policy C: filtered descriptive overlap). The comparison universe comprises exactly **12 protein–source pairs**, **36 comparison units** ($12\text{ pairs} \times 3\text{ GO aspects}$), and **72 policy-specific comparison rows** ($36\text{ units} \times 2\text{ policies}$).

### Key Empirical Findings

1. **Evaluability Expansion Across Before/After Marginals**:
   - In the frozen Stage P3 baseline, the marginal distribution was **20 of 72 rows (27.78%) evaluable** and **52 of 72 rows (72.22%) non-evaluable**.
   - In the PIL-04.1B recomparison, the marginal distribution is **42 of 72 rows (58.33%) evaluable** and **30 of 72 rows (41.67%) non-evaluable**.
   - Across before/after marginal distributions, this represents an evaluability increase of **$+30.56\text{ percentage points}$** (calculated as $100 \times (42/72 - 20/72) = 100 \times (11/36) \approx +30.56\text{ pp}$, rounded) and a corresponding non-evaluability decrease of **$-30.56\text{ percentage points}$** (calculated as $100 \times (30/72 - 52/72) = 100 \times (-11/36) \approx -30.56\text{ pp}$, rounded).
   - In the $2 \times 2$ transition matrix, exactly **20 rows remain evaluable** (`remains_evaluable`, 27.78%), **22 rows become newly evaluable** (`newly_evaluable`, 30.56%), **0 rows become non-evaluable** (`becomes_non_evaluable`, 0.00%), and **30 rows remain non-evaluable** (`remains_non_evaluable`, 41.67%). Zero previously evaluable comparisons were lost.
2. **Verified Field and Inventory Equality on Declared-Aspect Baseline**:
   - For all 20 rows that were evaluable in Stage P3 (originating from MultitaskProtDB-II and PlantMP, where source GO aspects were explicitly declared), equality between baseline and recomparison was verified across all concordance fields and inventory sets:
     * Concordance metrics: `source_terms_count`, `quickgo_terms_count`, `exact_overlap_count`, `union_terms_count`, `source_only_count`, `quickgo_only_count`, `jaccard_similarity`.
     * Transition schema metric deltas: `delta_source_terms_count = 0`, `delta_quickgo_terms_count = 0`, `delta_exact_overlap_count = 0`, `delta_union_terms_count = 0`, `delta_jaccard_similarity = 0.0000`.
     * Derived cross-matrix comparisons: `source_only_count` and `quickgo_only_count` were verified to be identical between baseline and recomparison matrices for all 20 rows ($S_{\text{only},\text{recomp}} == S_{\text{only},\text{base}}$ and $Q_{\text{only},\text{recomp}} == Q_{\text{only},\text{base}}$).
     * Inventory set invariance: `source_set_content_changed = false`, with element-by-element set equality between `recomparison_source_sets` and `baseline_source_sets`.
     * Classification: all 20 rows are categorized as `overall_transition_classification = "evaluable_fully_identical"` (20/20 rows).
3. **Characterization of Newly Evaluable Comparisons**:
   - All 22 newly evaluable rows ($11\text{ comparison units} \times 2\text{ policies}$) correspond to MoonProt records where source GO aspects were historically unassigned and were resolved to active GO terms in Task PIL-04.1A.
   - Observed Jaccard similarity for these 11 units spans from $0.3333$ to $1.0000$:
     * `P0AFW0` / MoonProt: BP = $0.5000$, MF = $0.8333$
     * `P24228` / MoonProt: BP = $0.3333$, CC = $0.3333$, MF = $0.7500$
     * `P78007` / MoonProt: BP = $0.6667$, CC = $1.0000$, MF = $1.0000$
     * `Q42525` / MoonProt: BP = $0.5789$, CC = $0.3333$, MF = $0.5385$
   - Observed Jaccard similarity is identical between Policy B and Policy C ($J_B == J_C$) for all 11 units. At the QuickGO side, diagnostic filtering counters show `nd_matching_rows_count = 0`, `root_matching_rows_count = 0`, `net_excluded_rows_count = 0`, and `terms_lost_after_filtering_count = 0`, confirming that retained QuickGO terms are identical between policies ($|Q_B| = |Q_C|$). At the source side, MoonProt annotations in this slice have unassessed evidence (`evidence_raw` is null), and none are root terms or have ND evidence, yielding identical `source_terms_count` ($|S_B| = |S_C|$).
4. **Diagnostic Reason Transitions**:
   - Eight rows ($4\text{ units} \times 2\text{ policies}$) remain non-evaluable but undergo a primary reason transition according to diagnostic evaluation precedence:
     * `E6KMA1` / MoonProt (BP, CC, MF; 6 rows): shifted from `source_aspect_indeterminate` to `accession_unlinked_in_capture`. Resolving source term aspects cleared the higher-priority aspect indeterminacy barrier and exposed the capture linkage barrier according to engine precedence (`quickgo_coverage_status = "unlinked_in_database"`).
     * `P0AFW0` / MoonProt (CC; 2 rows): shifted from `source_aspect_indeterminate` to `source_record_no_terms_aspect`. All 10 active source annotations for `P0AFW0` in MoonProt mapped exclusively to BP (5) and MF (5); zero annotations mapped to CC, resulting in an empty source CC inventory ($|S| = 0$).
   - Twenty-two rows ($11\text{ units} \times 2\text{ policies}$) maintain unchanged non-evaluable reasons:
     * Biological identity gate: `P34788` (12 rows across MultitaskProtDB-II and PlantMP) remains strictly blocked as `unresolved_biological_identity`.
     * Outside-slice boundary: `A0A0H3CDS3` (6 rows) remains `source_record_outside_slice`.
     * Empty aspect inventories: `P0AFW0` Multitask CC (2 rows) and `Q42525` PlantMP CC (2 rows) remain `source_record_no_terms_aspect`.
5. **Methodological Governance & Limitations**:
   - The historical Stage P3 non-evaluability rate ($72.22\%$) remains an immutable historical baseline. The PIL-04.1B rate ($41.67\%$) is presented side-by-side as a comparative outcome of metadata enrichment, not as a replacement.
   - Higher evaluability and high Jaccard scores in MoonProt reflect the technical resolution of a source cataloging gap; they do **not** demonstrate increased biological accuracy, nor do they validate multifunctionality.

---

## 1. Verified Analytical Inputs & Cryptographic Provenance

All source tables, schemas, upstream lineage references, and published artifacts for the original Gate 3 execution (v0) were verified prior to analysis. The execution manifest (`c52b251...`) records input and output dataset digests for the run. Crucially, the manifest's `output_dataset_digests` dictionary records exclusively the two generated tabular datasets; the SHA-256 digest of `manifest.json` itself is verified and reported separately, as a manifest payload cannot record its own content digest internally.

Furthermore, we explicitly distinguish between **digests directly recomputed on disk** from workspace files versus **upstream metadata citations** recorded in lineage records:

### 1.1 Consumed Input Datasets (7 Recomputed Disk Digests)
These 7 datasets represent the exact files supplied via CLI arguments, directly verified on disk via SHA-256 computation and matching `manifest.json` under `input_dataset_digests`:

| Input Dataset Role | Repository File Path | Directly Recomputed SHA-256 Digest | Status |
|---|---|---|:---:|
| `baseline_concordance` | `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` | `12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7` | **VERIFIED ON DISK** |
| `normalized_annotations` | `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv` | `2a6255c5059545d8b1bab06a6d73872d2a064add1c0dd7b25097bd95e47012de` | **VERIFIED ON DISK** |
| `raw_coverage` | `data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv` | `981c592f12bceb02e2c7a6404126dc7ad55053b2bd6383919658a5423241b9be` | **VERIFIED ON DISK** |
| `source_annotations` | `data/interim/pilot/source_go_annotations_pilot.csv` | `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda` | **VERIFIED ON DISK** |
| `derived_aspects` | `data/interim/pilot/quickgo_slice_enriched/derived_source_go_aspects_pilot.csv` | `e4500d3cf93f2e8861ab7ea5a91a5f9ef55617dd3c6413f4b3abd2c7cf6b204e` | **VERIFIED ON DISK** |
| `functional_coverage` | `data/interim/pilot/functional_coverage_pilot.csv` | `c29d28712c613211c6183f49ef304a63d94dd64a40de2ff682641037e2573e8d` | **VERIFIED ON DISK** |
| `catalog_proteins` | `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv` | `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc` | **VERIFIED ON DISK** |

> [!NOTE]
> **Source Annotations Path Resolution**: The source annotations dataset consumed by the recomparison runner is located at `data/interim/pilot/source_go_annotations_pilot.csv` (SHA-256 `949e5050...`), situated directly in `data/interim/pilot/`, exactly as recorded in the execution manifest. It is distinct from historical slice subdirectories.

### 1.2 Upstream Lineage Manifests & Historical Baseline References
These records provide upstream lineage tracking recorded in the execution manifest under `upstream_lineage_manifests`. Note that while manifest files on disk are verified directly, external ontology releases are lineage metadata citations:

| Lineage / Baseline Role | Reference / File Path | SHA-256 Digest | Provenance Source | Status |
|---|---|---|---|:---:|
| Stage P3 Run Manifest | `data/interim/pilot/quickgo_slice/manifest.json` | `01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7` | Recomputed from disk | **VERIFIED ON DISK** |
| PIL-04.1A Run Manifest | `data/interim/pilot/quickgo_slice_enriched/manifest.json` | `5fe29c5fdefbbe0d14b755844dcecf9b6ca29afc460eb4aec7b3479b596b077f` | Recomputed from disk | **VERIFIED ON DISK** |
| Pinned Ontology Snapshot | Upstream release `releases/2026-01-23` (`go.obo`) | `eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391` | Upstream lineage manifest citation (PIL-04.1A) | **METADATA CITED** |

### 1.3 Published PIL-04.1B Recomparison Artifacts (v0 Execution)
The original Gate 3 execution published 3 output artifacts atomically under `data/interim/pilot/quickgo_slice_recomparison/`. The two tabular CSV datasets are recorded in `output_dataset_digests`, while the manifest SHA-256 is verified independently:

| Output Artifact Role | Repository File Path | Directly Recomputed SHA-256 Digest | In Manifest `output_dataset_digests`? | Status |
|---|---|---|:---:|:---:|
| Recomputed Concordance Matrix | `data/interim/pilot/quickgo_slice_recomparison/quickgo_concordance_pilot_recomputed.csv` | `1f7149dc995a89a49f23b30124526d02c05bb24ec79ab2cd0e7bf035132ecd88` | **Yes** | **VERIFIED ON DISK** |
| Concordance Transition Matrix | `data/interim/pilot/quickgo_slice_recomparison/quickgo_concordance_transition_pilot.csv` | `950fecac5dfc0e14e8ef627a6b1b770d41f0ce14ed314d2dff4d1f26b03659b5` | **Yes** | **VERIFIED ON DISK** |
| PIL-04.1B Run Manifest | `data/interim/pilot/quickgo_slice_recomparison/manifest.json` | `c52b251ba72b2863639904fc4339a2a5ed35a307772a87b0e0fc0b110b89cade` | *Reported separately* | **VERIFIED ON DISK** |

### 1.4 Code and Schema Contracts at Execution HEAD
The runner script, engine module, and JSON schemas were verified on disk at commit `41521ba5d55636a3b74ed6f6616501542543a48d` and match the digests recorded in the manifest's `code_and_schema_digests`:

- **Execution Git Commit**: `41521ba5d55636a3b74ed6f6616501542543a48d` (parent: `cd1053dce16f1f843a773419faf3ca9e002d6ab3`)
- **Execution Mode**: 100% offline, zero live network access, deterministic execution.
- **Pipeline Runner**: `scripts/build_quickgo_concordance_recomparison.py` (SHA-256 `2c3f034eb98c7ef7821bc9c717ac5112424c0de85d8f6ce4f4814406dadde70a`; verified on disk).
- **Core Engine Module**: `src/mfp_bibliography/quickgo_concordance.py` (SHA-256 `8c33be009f25e84ac2c9ed583dff13340046d688426561a1255455d132d4d432`; verified on disk).
- **Concordance Schema**: `data/curated/quickgo_concordance.schema.json` (SHA-256 `c1181b192fdb09b415b14c404004111ffa66c32e2bcffe6a526cad18dbfc2dea`; verified on disk).
- **Transition Schema Contract**: `data/curated/quickgo_concordance_transition.schema.json` (SHA-256 `03ab66d79f83a9f4e43846e43fa7f78be5c40e9d157c7938d04ccc3d9ed5fe82`; verified on disk).

---

## 2. Comparison Universe & Analytical Units

A fundamental requirement of this analysis is avoiding false equivalence between tabular rows and biological protein entities.

### 2.1 Cohort Architecture
The comparison universe is built upon **8 purposive UniProtKB accessions**:
1. `A0A0H3CDS3` — (*C. crescentus* / MultitaskProtDB-II; negative control, outside vertical slice)
2. `E6KMA1` — (*S. cerevisiae* / MoonProt; positive control, unlinked in QuickGO capture)
3. `P0AFW0` — RfaH (*E. coli* / MoonProt & MultitaskProtDB-II; transformer moonlighting protein)
4. `P24228` — GCLM (*H. sapiens* / MoonProt; moonlighting metabolic protein)
5. `P34788` — BiP (*A. thaliana* / MultitaskProtDB-II & PlantMP; taxonomic identity conflict control)
6. `P78007` — Fez1 (*H. sapiens* / MoonProt; moonlighting protein)
7. `Q42525` — HXK1 (*A. thaliana* / MoonProt, MultitaskProtDB-II & PlantMP; multi-source anchor)
8. `Q9Y3E5` — PTH2 / Bit1 (*H. sapiens* / MultitaskProtDB-II; mitochondrial peptidyl-tRNA hydrolase)

### 2.2 Relational Expansion Hierarchy & Source Groupings
The tabular rows derive from a strict mathematical hierarchy:
$$\text{8 Accessions} \longrightarrow \text{12 Accession–Source Pairs} \longrightarrow \text{36 Comparison Units} \longrightarrow \text{72 Policy Rows}$$

```
┌────────────────────────────────────────────────────────────────────────┐
│                      COMPARISON UNIVERSE STRUCTURE                     │
├────────────────────────────────────────────────────────────────────────┤
│ 8 Cohort Accessions                                                    │
│   ├── A0A0H3CDS3 (1 pair: MultitaskProtDB-II)                          │
│   ├── E6KMA1     (1 pair: MoonProt)                                    │
│   ├── P0AFW0     (2 pairs: MoonProt, MultitaskProtDB-II)               │
│   ├── P24228     (1 pair: MoonProt)                                    │
│   ├── P34788     (2 pairs: MultitaskProtDB-II, PlantMP)                │
│   ├── P78007     (1 pair: MoonProt)                                    │
│   ├── Q42525     (3 pairs: MoonProt, MultitaskProtDB-II, PlantMP)      │
│   └── Q9Y3E5     (1 pair: MultitaskProtDB-II)                          │
│                                                                        │
│ 12 Exact Pairs Grouped by Curated Source Database                      │
│   ├── SRC_MOONPROT (5 pairs):                                          │
│   │     E6KMA1, P0AFW0, P24228, P78007, Q42525                         │
│   ├── SRC_MULTITASKPROTDB_II (5 pairs):                                │
│   │     A0A0H3CDS3, P0AFW0, P34788, Q42525, Q9Y3E5                     │
│   └── SRC_PLANTMP (2 pairs):                                           │
│         P34788, Q42525                                                 │
│                                                                        │
│ Total: 12 Pairs × 3 Aspects (BP, CC, MF) = 36 Comparison Units        │
│ Total: 36 Units × 2 Policies (Policy B, Policy C) = 72 Analytical Rows │
└────────────────────────────────────────────────────────────────────────┘
```

#### Reconciliation of Cross-Source Accession Mappings
Direct inspection of the frozen Stage P3 baseline (`quickgo_concordance_pilot.csv`), the recomputed matrix (`quickgo_concordance_pilot_recomputed.csv`), and the pipeline engine constant (`VERIFIED_COHORT_PAIRS` in `src/mfp_bibliography/quickgo_concordance.py`) confirms exact 100% agreement across all 12 pairs:
- **`A0A0H3CDS3`**: Present exclusively in **MultitaskProtDB-II** (`SRC_MULTITASKPROTDB_II`). It is absent from PlantMP and MoonProt. The 6 comparison rows with `primary_non_evaluable_reason = "source_record_outside_slice"` (3 aspects $\times$ 2 policies) originate solely from `SRC_MULTITASKPROTDB_II`.
- **`P24228`**: Present exclusively in **MoonProt** (`SRC_MOONPROT`). It is absent from MultitaskProtDB-II and PlantMP.
- **`Q42525`**: Present across **all three sources** (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`), forming 3 distinct protein–source pairs (18 comparison rows).
- **`P34788`**: Present in **MultitaskProtDB-II** and **PlantMP** (2 pairs; 12 comparison rows, all held under `unresolved_biological_identity`).
- **`P0AFW0`**: Present in **MoonProt** and **MultitaskProtDB-II** (2 pairs; 12 comparison rows).
- **`Q9Y3E5`**: Present exclusively in **MultitaskProtDB-II** (1 pair; 6 comparison rows).
- **`E6KMA1`**: Present exclusively in **MoonProt** (1 pair; 6 comparison rows).
- **`P78007`**: Present exclusively in **MoonProt** (1 pair; 6 comparison rows).

Every comparison row is uniquely and deterministically identified by the compound 5-tuple:
$$\text{concordance\_id} = \text{MFP:CONC}:\langle\text{accession}\rangle:\langle\text{protein\_id}\rangle:\langle\text{source\_id}\rangle:\langle\text{aspect}\rangle:\langle\text{policy\_id}\rangle$$
Across all 72 rows, zero key collisions, null keys, or key discrepancies exist between the baseline and recomparison matrices.

---

## 3. Quantitative Evaluability Analysis

### 3.1 Evaluability Expansion and Marginal Shifts
- **Baseline Marginals (Stage P3)**: 20 evaluable rows ($27.78\%$) vs. 52 non-evaluable rows ($72.22\%$) out of $N = 72$.
- **Recomparison Marginals (PIL-04.1B)**: 42 evaluable rows ($58.33\%$) vs. 30 non-evaluable rows ($41.67\%$) out of $N = 72$.
- **Marginal Shifts (Before vs. After)**:
  * Evaluability marginal shift: calculated as $100 \times (42/72 - 20/72) = 100 \times (11/36) \approx \mathbf{+30.56\text{ pp}}$, rounded.
  * Non-evaluability marginal shift: calculated as $100 \times (30/72 - 52/72) = 100 \times (-11/36) \approx \mathbf{-30.56\text{ pp}}$, rounded.
  * *Note on Metric Attribution*: The $\pm 30.56\text{ pp}$ shift belongs strictly to the comparison between before/after marginal distributions, and not to the internal joint transition cells.

### 3.2 Full $2 \times 2$ Evaluability Transition Matrix

The transition table tracks the row-level classification shift between Stage P3 and Stage PIL-04.1B:

| Baseline P3 Status \ Recomparison PIL-04.1B Status | Evaluable (Recomputed) | Non-Evaluable (Recomputed) | Total Baseline (P3 Marginals) |
|---|:---:|:---:|:---:|
| **Evaluable (P3)** | **20** (`remains_evaluable`, $27.78\%$) | **0** (`becomes_non_evaluable`, $0.00\%$) | **20** ($27.78\%$) |
| **Non-Evaluable (P3)** | **22** (`newly_evaluable`, $30.56\%$) | **30** (`remains_non_evaluable`, $41.67\%$) | **52** ($72.22\%$) |
| **Total Recomputed (PIL-04.1B Marginals)** | **42** ($58.33\%$) | **30** ($41.67\%$) | **72** ($100.00\%$) |
| **Marginal Shift ($\Delta\text{pp}$ from exact fractions)** | **$+30.56\text{ pp}$** ($+\frac{11}{36}$) | **$-30.56\text{ pp}$** ($-\frac{11}{36}$) | — |

#### Verification of Totals and Marginals
- Sum of internal cells: $20 + 0 + 22 + 30 = 72$ ($100.0\%$).
- Baseline marginal check: $20\text{ (eval)} + 52\text{ (non-eval)} = 72$.
- Recomparison marginal check: $42\text{ (eval)} + 30\text{ (non-eval)} = 72$.
- The zero-cell (`becomes_non_evaluable = 0`) confirms that no previously evaluable unit was broken or dropped by the enrichment pipeline.

### 3.3 Breakdown by Concordance Policy & Gene Ontology Aspect

The expansion operates symmetrically across both evaluation policies and impacts all three biological aspects:

| Policy / Aspect Combination | Sample Size ($N$) | Baseline P3 Evaluable | Recomputed Evaluable | Policy Marginal Shift | Newly Evaluable (Cells) | Remains Non-Eval. |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Policy B (`captured_inventory_overlap`)** | **36** | **10** ($27.78\%$) | **21** ($58.33\%$) | **$+30.56\text{ pp}$** | **11** ($30.56\%$) | **15** ($41.67\%$) |
| — Biological Process (BP) | 12 | 4 ($33.33\%$) | 8 ($66.67\%$) | $+33.33\text{ pp}$ | 4 | 4 |
| — Cellular Component (CC) | 12 | 2 ($16.67\%$) | 5 ($41.67\%$) | $+25.00\text{ pp}$ | 3 | 7 |
| — Molecular Function (MF) | 12 | 4 ($33.33\%$) | 8 ($66.67\%$) | $+33.33\text{ pp}$ | 4 | 4 |
| **Policy C (`filtered_descriptive_overlap`)** | **36** | **10** ($27.78\%$) | **21** ($58.33\%$) | **$+30.56\text{ pp}$** | **11** ($30.56\%$) | **15** ($41.67\%$) |
| — Biological Process (BP) | 12 | 4 ($33.33\%$) | 8 ($66.67\%$) | $+33.33\text{ pp}$ | 4 | 4 |
| — Cellular Component (CC) | 12 | 2 ($16.67\%$) | 5 ($41.67\%$) | $+25.00\text{ pp}$ | 3 | 7 |
| — Molecular Function (MF) | 12 | 4 ($33.33\%$) | 8 ($66.67\%$) | $+33.33\text{ pp}$ | 4 | 4 |
| **All Policies by Aspect ($N = 24$ each)** | | | | | | |
| — Biological Process (BP) | 24 | 8 ($33.33\%$) | 16 ($66.67\%$) | $+33.33\text{ pp}$ | 8 | 8 ($33.33\%$) |
| — Cellular Component (CC) | 24 | 4 ($16.67\%$) | 10 ($41.67\%$) | $+25.00\text{ pp}$ | 6 | 14 ($58.33\%$) |
| — Molecular Function (MF) | 24 | 8 ($33.33\%$) | 16 ($66.67\%$) | $+33.33\text{ pp}$ | 8 | 8 ($33.33\%$) |

---

## 4. Traceable Diagnostic Reason Analysis

A critical scientific requirement is distinguishing changes in overall evaluability from diagnostic reason transitions within non-evaluable comparisons.

### 4.1 Summary of Primary Reason Transitions ($N = 72$)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRIMARY REASON TRANSITIONS (N = 72)                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Became Evaluable (became_evaluable) ──────────────────► 22 rows     │
│    (All transitioned from source_aspect_indeterminate)                 │
│                                                                        │
│ 2. Reason Changed While Non-Evaluable (reason_changed) ──►  8 rows     │
│    • E6KMA1 (BP, CC, MF; 6 rows): indeterminate -> unlinked in capture │
│    • P0AFW0 (CC; 2 rows): indeterminate -> no terms in aspect          │
│                                                                        │
│ 3. Unchanged Non-Evaluable Reason (unchanged_reason) ────► 22 rows     │
│    • P34788 (Multitask & PlantMP; 12 rows): unresolved identity        │
│    • A0A0H3CDS3 (Multitask; 6 rows): outside slice                     │
│    • P0AFW0 & Q42525 (CC; 4 rows): no terms in aspect                  │
│                                                                        │
│ 4. Unchanged Evaluable Status (unchanged_null) ──────────► 20 rows     │
│    (Historical evaluable units from Multitask and PlantMP)             │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Detailed Diagnostic Path Analysis

#### 1. Transition to Evaluable (`became_evaluable`, 22 rows / 11 units $\times$ 2 policies)
In the Stage P3 baseline, MoonProt annotations were loaded without aspect assignments, causing the runner to halt evaluation at the source-inventory check with `primary_non_evaluable_reason = "source_aspect_indeterminate"`.
In Task PIL-04.1B, the join engine matched each annotation against `derived_source_go_aspects_pilot.csv` (1:1 bijection on `annotation_id`). The active ontology lookups provided unambiguous aspect buckets (`BP`, `CC`, or `MF`), clearing the indeterminacy blocker:
- `P0AFW0` / `SRC_MOONPROT`: BP (2 rows), MF (2 rows) $\to$ **4 rows**
- `P24228` / `SRC_MOONPROT`: BP (2 rows), CC (2 rows), MF (2 rows) $\to$ **6 rows**
- `P78007` / `SRC_MOONPROT`: BP (2 rows), CC (2 rows), MF (2 rows) $\to$ **6 rows**
- `Q42525` / `SRC_MOONPROT`: BP (2 rows), CC (2 rows), MF (2 rows) $\to$ **6 rows**

#### 2. Precedence-Driven Diagnostic Shift: `E6KMA1` MoonProt (6 rows)
- **Baseline Reason**: `source_aspect_indeterminate`
- **Recomputed Reason**: `accession_unlinked_in_capture`
- **Diagnostic Precedence Mechanism**: The concordance engine determines the primary non-evaluable reason by strict evaluation precedence: source aspect indeterminacy check takes precedence over external capture coverage checks. In the Stage P3 baseline, MoonProt source annotations lacked aspect metadata, so the primary blocker selected was `source_aspect_indeterminate`. After aspect enrichment under Task PIL-04.1A, source annotations have unambiguous aspect assignments; according to engine precedence, the evaluation then identifies the external coverage capture barrier (`quickgo_coverage_status = "unlinked_in_database"`), assigning `primary_non_evaluable_reason = "accession_unlinked_in_capture"`.
- **Curatorial Interpretation**: This shift reflects diagnostic evaluation precedence rather than a new defect. The unlinked status in the QuickGO database capture was already present in Stage P3, but was masked by the higher-priority source-aspect check.

#### 3. Empty Aspect Inventory: `P0AFW0` MoonProt CC (2 rows)
- **Baseline Reason**: `source_aspect_indeterminate`
- **Recomputed Reason**: `source_record_no_terms_aspect`
- **Mechanism**: MoonProt contains exactly 10 source GO annotations for `P0AFW0` (`MFP:U:9023923ecdd9d57f`) in `source_go_annotations_pilot.csv`. Under Task PIL-04.1A ontology enrichment, exactly 5 annotations resolved to Biological Process (`source_terms_count = 5`) and 5 annotations resolved to Molecular Function (`source_terms_count = 5`). Exactly zero annotations resolved to Cellular Component. Under repository invariants ([`AGENTS.md`](../../AGENTS.md) §5), no GO term may be heuristically mapped to an unassociated compartment. Consequently, the source CC inventory is genuinely empty ($|S| = 0$, `source_inventory_status = "empty"`).
- **Curatorial Interpretation**: Resolving source aspects correctly classified `P0AFW0` CC as having no source terms for that aspect, matching the behavior of `P0AFW0` in MultitaskProtDB-II and resolving consistency with §5.2.

#### 4. Gated Controls Preserved Without Mutation (22 rows)
- **Taxonomic / Biological Identity Gate (`P34788`, 12 rows)**:
  `P34788` (*A. thaliana* BiP) was flagged in Stage P3 with taxonomic identity discrepancies across databases. Under [ADR-005](../../docs/decisions/ADR-005-deterministic-protein-ids.md) and [`spec.md`](spec.md) §1.2, ontology aspect derivation must never bypass or alter biological identity gates. All 12 rows (MultitaskProtDB-II and PlantMP across BP, CC, MF under both policies) remain strictly non-evaluable with `primary_non_evaluable_reason = "unresolved_biological_identity"`.
- **Outside-Slice Control (`A0A0H3CDS3`, 6 rows)**:
  `A0A0H3CDS3` (*C. crescentus*) originates exclusively from MultitaskProtDB-II (`SRC_MULTITASKPROTDB_II`) and lies outside the vertical slice boundaries. All 6 comparison rows (BP, CC, MF under Policy B and Policy C) remain strictly non-evaluable with `primary_non_evaluable_reason = "source_record_outside_slice"`.
- **Pre-existing Empty Aspect Inventories (4 rows)**:
  `P0AFW0` / Multitask CC (2 rows) and `Q42525` / PlantMP CC (2 rows) had zero source terms declared in the baseline and continue to have zero source terms (`source_record_no_terms_aspect`).

---

## 5. Jaccard Metric Concordance Analysis

To maintain scientific integrity, comparisons of Jaccard similarity ($J = \frac{|S \cap Q|}{|S \cup Q|}$) must never impute arbitrary numeric values (such as zero) to undefined/non-evaluable states, nor calculate score differences against a null baseline.

### 5.1 Baseline Evaluable Cohort ($N = 20\text{ rows}$, 10 units $\times$ 2 policies)
This cohort comprises the 10 comparison units evaluable in both Stage P3 and Stage PIL-04.1B:

| Concordance Unit Key | Aspect | Policy ID | $J_{\text{base}}$ | $J_{\text{recomp}}$ | `delta_jaccard_similarity` | $|S|$ | $|Q|$ | $|S \cap Q|$ | Overall Transition Classification |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `P0AFW0` / `SRC_MULTITASKPROTDB_II` | BP | `captured_inventory_overlap` | 0.4000 | 0.4000 | 0.0000 | 3 | 4 | 2 | `evaluable_fully_identical` |
| `P0AFW0` / `SRC_MULTITASKPROTDB_II` | BP | `filtered_descriptive_overlap` | 0.4000 | 0.4000 | 0.0000 | 3 | 4 | 2 | `evaluable_fully_identical` |
| `P0AFW0` / `SRC_MULTITASKPROTDB_II` | MF | `captured_inventory_overlap` | 0.4444 | 0.4444 | 0.0000 | 8 | 5 | 4 | `evaluable_fully_identical` |
| `P0AFW0` / `SRC_MULTITASKPROTDB_II` | MF | `filtered_descriptive_overlap` | 0.5000 | 0.5000 | 0.0000 | 7 | 5 | 4 | `evaluable_fully_identical` |
| `Q42525` / `SRC_MULTITASKPROTDB_II` | BP | `captured_inventory_overlap` | 0.2917 | 0.2917 | 0.0000 | 14 | 17 | 7 | `evaluable_fully_identical` |
| `Q42525` / `SRC_MULTITASKPROTDB_II` | BP | `filtered_descriptive_overlap` | 0.3043 | 0.3043 | 0.0000 | 13 | 17 | 7 | `evaluable_fully_identical` |
| `Q42525` / `SRC_MULTITASKPROTDB_II` | CC | `captured_inventory_overlap` | 0.3333 | 0.3333 | 0.0000 | 9 | 7 | 4 | `evaluable_fully_identical` |
| `Q42525` / `SRC_MULTITASKPROTDB_II` | CC | `filtered_descriptive_overlap` | 0.3333 | 0.3333 | 0.0000 | 9 | 7 | 4 | `evaluable_fully_identical` |
| `Q42525` / `SRC_MULTITASKPROTDB_II` | MF | `captured_inventory_overlap` | 0.4615 | 0.4615 | 0.0000 | 12 | 7 | 6 | `evaluable_fully_identical` |
| `Q42525` / `SRC_MULTITASKPROTDB_II` | MF | `filtered_descriptive_overlap` | 0.5000 | 0.5000 | 0.0000 | 11 | 7 | 6 | `evaluable_fully_identical` |
| `Q42525` / `SRC_PLANTMP` | BP | `captured_inventory_overlap` | 0.0938 | 0.0938 | 0.0000 | 18 | 17 | 3 | `evaluable_fully_identical` |
| `Q42525` / `SRC_PLANTMP` | BP | `filtered_descriptive_overlap` | 0.0968 | 0.0968 | 0.0000 | 17 | 17 | 3 | `evaluable_fully_identical` |
| `Q42525` / `SRC_PLANTMP` | MF | `captured_inventory_overlap` | 0.2308 | 0.2308 | 0.0000 | 9 | 7 | 3 | `evaluable_fully_identical` |
| `Q42525` / `SRC_PLANTMP` | MF | `filtered_descriptive_overlap` | 0.2500 | 0.2500 | 0.0000 | 8 | 7 | 3 | `evaluable_fully_identical` |
| `Q9Y3E5` / `SRC_MULTITASKPROTDB_II` | BP | `captured_inventory_overlap` | 0.5000 | 0.5000 | 0.0000 | 3 | 5 | 3 | `evaluable_fully_identical` |
| `Q9Y3E5` / `SRC_MULTITASKPROTDB_II` | BP | `filtered_descriptive_overlap` | 0.5000 | 0.5000 | 0.0000 | 3 | 5 | 3 | `evaluable_fully_identical` |
| `Q9Y3E5` / `SRC_MULTITASKPROTDB_II` | CC | `captured_inventory_overlap` | 0.6000 | 0.6000 | 0.0000 | 4 | 4 | 3 | `evaluable_fully_identical` |
| `Q9Y3E5` / `SRC_MULTITASKPROTDB_II` | CC | `filtered_descriptive_overlap` | 0.6000 | 0.6000 | 0.0000 | 4 | 4 | 3 | `evaluable_fully_identical` |
| `Q9Y3E5` / `SRC_MULTITASKPROTDB_II` | MF | `captured_inventory_overlap` | 0.3333 | 0.3333 | 0.0000 | 3 | 3 | 1 | `evaluable_fully_identical` |
| `Q9Y3E5` / `SRC_MULTITASKPROTDB_II` | MF | `filtered_descriptive_overlap` | 0.3333 | 0.3333 | 0.0000 | 3 | 3 | 1 | `evaluable_fully_identical` |

#### Verified Invariance Across Fields and Sets
For all 20 rows in this baseline evaluable cohort:
- **Verified Concordance Fields**: Equality between baseline and recomparison was verified across all metrics: `source_terms_count`, `quickgo_terms_count`, `exact_overlap_count`, `union_terms_count`, `source_only_count`, `quickgo_only_count`, and `jaccard_similarity`.
- **Verified Metric Transition Deltas (Transition Schema)**:
  * `delta_source_terms_count = 0` (20 of 20 rows)
  * `delta_quickgo_terms_count = 0` (20 of 20 rows)
  * `delta_exact_overlap_count = 0` (20 of 20 rows)
  * `delta_union_terms_count = 0` (20 of 20 rows)
  * `delta_jaccard_similarity = 0.0000` (20 of 20 rows)
- **Derived Concordance Comparisons (Cross-Matrix)**:
  `source_only_count` and `quickgo_only_count` are columns of the concordance matrices rather than delta fields in the transition schema. A derived cross-matrix comparison confirmed that both counts are identical between baseline and recomparison matrices across all 20 rows ($S_{\text{only},\text{recomp}} == S_{\text{only},\text{base}}$ and $Q_{\text{only},\text{recomp}} == Q_{\text{only},\text{base}}$).
- **Verified Inventory Sets**:
  * `source_set_content_changed = false` (20 of 20 rows)
  * `recomparison_source_sets == baseline_source_sets` (element-by-element set equality verified across all comparable inventories)
- **Transition Classification**: All 20 rows are categorized as `overall_transition_classification = "evaluable_fully_identical"`.

### 5.2 Newly Evaluable Cohort ($N = 22\text{ rows}$, 11 units $\times$ 2 policies)
For these units, $J_{\text{base}} = \text{null}$ and $J_{\text{recomp}} \in [0.3333, 1.0000]$. The metric transition is formally categorized as `score_newly_defined`:

| Comparison Unit Key (MoonProt) | Aspect | Policy ID | $J_{\text{base}}$ | $J_{\text{recomp}}$ | `delta_jaccard_similarity` | $|S_{\text{recomp}}|$ | $|Q_{\text{recomp}}|$ | $|S \cap Q|$ | Overall Transition Classification |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `P0AFW0` / `SRC_MOONPROT` | BP | `captured_inventory_overlap` | null | 0.5000 | null | 5 | 4 | 3 | `newly_evaluable` |
| `P0AFW0` / `SRC_MOONPROT` | BP | `filtered_descriptive_overlap` | null | 0.5000 | null | 5 | 4 | 3 | `newly_evaluable` |
| `P0AFW0` / `SRC_MOONPROT` | MF | `captured_inventory_overlap` | null | 0.8333 | null | 5 | 6 | 5 | `newly_evaluable` |
| `P0AFW0` / `SRC_MOONPROT` | MF | `filtered_descriptive_overlap` | null | 0.8333 | null | 5 | 6 | 5 | `newly_evaluable` |
| `P24228` / `SRC_MOONPROT` | BP | `captured_inventory_overlap` | null | 0.3333 | null | 12 | 4 | 4 | `newly_evaluable` |
| `P24228` / `SRC_MOONPROT` | BP | `filtered_descriptive_overlap` | null | 0.3333 | null | 12 | 4 | 4 | `newly_evaluable` |
| `P24228` / `SRC_MOONPROT` | CC | `captured_inventory_overlap` | null | 0.3333 | null | 2 | 2 | 1 | `newly_evaluable` |
| `P24228` / `SRC_MOONPROT` | CC | `filtered_descriptive_overlap` | null | 0.3333 | null | 2 | 2 | 1 | `newly_evaluable` |
| `P24228` / `SRC_MOONPROT` | MF | `captured_inventory_overlap` | null | 0.7500 | null | 7 | 7 | 6 | `newly_evaluable` |
| `P24228` / `SRC_MOONPROT` | MF | `filtered_descriptive_overlap` | null | 0.7500 | null | 7 | 7 | 6 | `newly_evaluable` |
| `P78007` / `SRC_MOONPROT` | BP | `captured_inventory_overlap` | null | 0.6667 | null | 3 | 2 | 2 | `newly_evaluable` |
| `P78007` / `SRC_MOONPROT` | BP | `filtered_descriptive_overlap` | null | 0.6667 | null | 3 | 2 | 2 | `newly_evaluable` |
| `P78007` / `SRC_MOONPROT` | CC | `captured_inventory_overlap` | null | 1.0000 | null | 2 | 2 | 2 | `newly_evaluable` |
| `P78007` / `SRC_MOONPROT` | CC | `filtered_descriptive_overlap` | null | 1.0000 | null | 2 | 2 | 2 | `newly_evaluable` |
| `P78007` / `SRC_MOONPROT` | MF | `captured_inventory_overlap` | null | 1.0000 | null | 5 | 5 | 5 | `newly_evaluable` |
| `P78007` / `SRC_MOONPROT` | MF | `filtered_descriptive_overlap` | null | 1.0000 | null | 5 | 5 | 5 | `newly_evaluable` |
| `Q42525` / `SRC_MOONPROT` | BP | `captured_inventory_overlap` | null | 0.5789 | null | 13 | 17 | 11 | `newly_evaluable` |
| `Q42525` / `SRC_MOONPROT` | BP | `filtered_descriptive_overlap` | null | 0.5789 | null | 13 | 17 | 11 | `newly_evaluable` |
| `Q42525` / `SRC_MOONPROT` | CC | `captured_inventory_overlap` | null | 0.3333 | null | 9 | 7 | 4 | `newly_evaluable` |
| `Q42525` / `SRC_MOONPROT` | CC | `filtered_descriptive_overlap` | null | 0.3333 | null | 9 | 7 | 4 | `newly_evaluable` |
| `Q42525` / `SRC_MOONPROT` | MF | `captured_inventory_overlap` | null | 0.5385 | null | 12 | 8 | 7 | `newly_evaluable` |
| `Q42525` / `SRC_MOONPROT` | MF | `filtered_descriptive_overlap` | null | 0.5385 | null | 12 | 8 | 7 | `newly_evaluable` |

### 5.3 Policy B vs. Policy C Invariant Analysis on Newly Evaluable Rows

For all 11 newly evaluable units, Jaccard similarity is equal between Policy B and Policy C ($J_B == J_C$). Inspection of the underlying diagnostic filtering counters and inventories confirms:

- **QuickGO-Side Filtering Verification**:
  * In all 11 units, `nd_matching_rows_count = 0` (zero QuickGO annotation rows supported exclusively by `ND` evidence).
  * In all 11 units, `root_matching_rows_count = 0` (zero QuickGO annotation rows matching root terms).
  * Consequently, `net_excluded_rows_count = 0` (zero QuickGO annotation rows excluded by Policy C).
  * In terms of distinct GO terms: `terms_lost_after_filtering_count = 0` and `terms_retained_via_other_rows_count = 0`.
  * Retained QuickGO terms count is identical between policies (`quickgo_terms_count` in Policy B equals `quickgo_terms_count` in Policy C; $|Q_B| = |Q_C|$).
  * *Important Distinction*: `net_excluded_rows_count` represents excluded annotation rows, not distinct GO terms; in these 11 units, both annotation row exclusions and unique terms lost are zero.
- **Source-Side Filtering Verification**:
  * MoonProt annotation records in this slice have unassigned evidence (`evidence_raw` is null), reflected in `unassessed_evidence_rows_count` matching source annotation counts.
  * None of the resolved active GO terms for these MoonProt records are root terms or have `ND` evidence; hence `source_terms_count` is identical between Policy B and Policy C ($|S_B| = |S_C|$).
- **Jaccard Equality**:
  With both $|S|$ and $|Q|$ invariant between Policy B and Policy C and identical overlap $|S \cap Q|$, Jaccard similarity is equal across both policies ($J_B = J_C$).
- **Scope Boundary**:
  Statements regarding upstream `NOT` qualifier filtering are excluded as no explicit upstream evidence was evaluated for this comparison.

---

## 6. Curatorial Invariants & Interpretive Limitations

To adhere to repository governance and bioinformatic rigor:

1. **Separation of Cataloging Resolution and Biological Verification**:
   The transition of MoonProt units from `source_aspect_indeterminate` to `evaluable` represents the successful curation of a technical metadata gap (mapping cited GO identifiers to their active namespace). **It does not validate the biological claims of moonlighting function asserted by MoonProt**.
2. **Proper Interpretation of High Jaccard Values**:
   High Jaccard similarities (e.g., $1.0000$ for `P78007` in CC and MF) demonstrate high textual vocabulary agreement between MoonProt's curated annotations and QuickGO's annotations for that accession. They do **not** prove that the protein performs multiple distinct molecular functions in those cellular compartments.
3. **Absence of Cartesian Functional Synthesis**:
   Co-occurrence of high concordance in BP ($0.6667$), CC ($1.0000$), and MF ($1.0000$) for `P78007` does **not** permit synthesizing functional triplets (e.g., asserting that function $X$ is executed in compartment $Y$). Under [`AGENTS.md`](../../AGENTS.md) §5, distinct aspect observations remain strictly separate.
4. **Preservation of Immutable Historical Baselines**:
   The $72.22\%$ non-evaluability rate established in Stage P3 and documented in Stage P4 remains the historical benchmark for un-enriched source claims. The $41.67\%$ non-evaluability rate observed in PIL-04.1B reflects the specific outcome of Task PIL-04.1A enrichment; it does not replace or erase the historical findings.
5. **No General Extrapolation**:
   These findings are strictly confined to the purposive 8-protein pilot cohort. Generalizing to the broader multi-thousand protein candidate catalog (`mfp_proteins.csv`) requires full catalog-scale pipeline execution under an approved roadmap increment.

---

## 7. Conclusions & Next Steps

Task PIL-04.1B successfully demonstrated that ontology-derived aspect enrichment expands evaluable concordance coverage from $27.78\%$ to $58.33\%$ across the pilot slice while strictly preserving the mathematical fidelity of declared-aspect comparisons.

- **Gate 1**: Contract specification and portable synthetic tests — **COMPLETED** (Commit `0789e4a`).
- **Gate 2**: Code commit and technical review — **COMPLETED** (Commit `0789e4a`).
- **Gate 2B**: Test suite historical serialization fix — **COMPLETED** (Commit `41521ba`).
- **Gate 3**: Offline pilot execution and published artifact verification — **COMPLETED** (`quickgo_slice_recomparison/`).
- **Gate 4**: Descriptive synthesis and results documentation — **COMPLETED & APPROVED** (Report `REPORT-QUICKGO-PILOT-PIL-04.1B-DESCRIPTIVE-001`). Gate 4 human approval granted for v0 execution.
