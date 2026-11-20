# Stage P4 Technical Report: Descriptive Concordance Synthesis & Limitation Analysis

- **Document ID**: `REPORT-QUICKGO-PILOT-P4-001`
- **Feature Directory**: `specs/quickgo-pilot-p3/`
- **Target Repository**: `mfp-bibliography`
- **Authority Level**: Level 6 Technical Completion Report (Reporting and Synthesis Only)
- **Status**: Completed (2026-11-16)
- **Baseline Git HEAD**: `21a3c8ef6bc42ae2f7f51ecc6f9ac6b9d9579b7e`
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md)

---

## Executive Summary

This report delivers the descriptive analytical synthesis for **Stage P4** of the `MFP_QuickV1` Evidence Integration Pilot. Stage P4 operates strictly as an offline, read-only evaluation of the frozen Stage P3 outputs. It performs no database mutations, creates no new pipeline code or schemas, and leaves the repository's git-tracked working tree unchanged.

The analysis is bounded to a purposive **eight-protein cohort** evaluated across three external/curated sources (MultitaskProtDB-II, MoonProt, PlantMP) and external Gene Ontology (GO) annotations captured in the frozen database `MFP_QuickV1`. 

### Key Findings
1. **Universe Structure and Evaluability**:
   - The comparison universe comprises **8 cohort accessions**, **12 verified accession–source pairs**, **36 accession–source–aspect comparison units**, and **72 policy-specific comparison rows** (36 under Policy B, 36 under Policy C).
   - Across the 36 comparison units, exactly **10 units (20 rows, 27.78%)** are evaluable under both Policy B and Policy C. Exactly **26 units (52 rows, 72.22%)** are non-evaluable under both policies. Zero units changed evaluability status between Policy B and Policy C.
   - Non-evaluability is driven by four discrete, non-overlapping primary reasons: source GO aspect indeterminacy in MoonProt (15 units / 30 rows, 41.67%), unresolved taxonomic identity for `P34788` (6 units / 12 rows, 16.67%), source records outside the vertical slice (3 units / 6 rows, 8.33%), and observed absence of source annotations for specific aspects (2 units / 4 rows, 5.56%).
2. **Paired Policy Comparison (Policy B vs. Policy C)**:
   - Evaluated across the 10 eligible paired comparison units, Jaccard similarity increased in exactly **5 units** and remained identical in exactly **5 units** ($\Delta J \in [0.0000, +0.0556]$).
   - Verification demonstrates that score increases were **100% driven by the removal of uninformative root terms from the source inventories** (`GO:0003674` for Molecular Function and `GO:0008150` for Biological Process), which reduced the union denominator by 1 while keeping shared specific terms constant. In the external QuickGO capture for these 10 evaluable units, zero ND rows and zero root terms existed.
   - Filtering produced zero empty-after-filtering transitions and zero loss of specific biological terms.
3. **Reference Overlap and Namespace Integrity**:
   - Across the **12 reference-comparison rows** (evaluated at the entity / source-record level under Option A), exactly **7 pairs (58.33%)** are evaluable and complete ($J \in [0.0000, 0.1667]$).
   - Six evaluable pairs share exactly 1 primary citation identifier (`PMID:22817892`, `PMID:27616280`, `PMID:17081979`, `PMID:12690200`, `PMID:14660562`). Exactly 1 evaluable pair (`Q42525` / PlantMP) is genuinely disjoint ($J = 0.0000$, with 2 source PMIDs and 28 QuickGO PMIDs sharing zero overlap).
   - Five pairs (41.67%) are non-evaluable due to taxonomic identity gating (`P34788`, 2 pairs), unlinked database capture (`E6KMA1`, 1 pair), source extraction HTML failure (`P24228`, 1 pair, recorded as indeterminate completeness), or outside-slice status (`A0A0H3CDS3`, 1 pair).
4. **Preservation Reality**:
   - The Stage P3 code, schemas, and tests are versioned in Git at Commit `4906b2e` and Commit `21a3c8e`. However, the interim CSV outputs and fixtures reside under `data/*` (gitignored). While cryptographically anchored by SHA-256 digests in Manifest v1.1, durable physical preservation of these interim artifacts remains pending formal repository storage authorization.

---

## 1. Inspected Baseline & Verified Analytical Inputs

### 1.1 Repository Baseline
- **Repository**: `mfp-bibliography`
- **Current Branch**: `feature/functional-normalization`
- **Published Baseline HEAD**: `21a3c8ef6bc42ae2f7f51ecc6f9ac6b9d9579b7e`
  - *Parent (Commit 1 / Technical)*: `4906b2ee0fded7060038b0055d430ee1297c2f6a`
  - *Pre-P3 Baseline (Commit 2 / Reconciled)*: `dc761e00c8ddec64fce4652f2fca9a783ec6533d`
- **Tracked Working Tree**: Clean; synchronized with `origin/feature/functional-normalization`.
- **Preserved Untracked Artifact**: [`docs/reports/pending-work-triage-2026-11-12.md`](pending-work-triage-2026-11-12.md) (retained without modification).

### 1.2 Independent Manifest Integrity
The Stage P3 execution manifest is stored on disk at `data/interim/pilot/quickgo_slice/manifest.json`. Its integrity is verified by an independent cryptographic digest computed directly from file bytes on disk:
- **Manifest File**: `data/interim/pilot/quickgo_slice/manifest.json`
- **Manifest SHA-256 Digest**: `01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7`
- **Manifest Version**: `v1.1` (`execution_mode: "offline_uncommitted_working_tree"`)

### 1.3 Verified Analytical Input Inventory
The four Stage P3 output CSV files consumed as inputs for this report were cryptographically verified against the recorded SHA-256 digests in Manifest v1.1. All files match bit-for-bit:

| Logical Role | Relative File Path | Row Count | Column Count | Full SHA-256 Digest | Status |
|---|---|:---:|:---:|---|:---:|
| **Coverage Accounting** | `data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv` | 8 | 8 | `981c592f12bceb02e2c7a6404126dc7ad55053b2bd6383919658a5423241b9be` | **VERIFIED** |
| **Normalized Annotations** | `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv` | 156 | 14 | `2a6255c5059545d8b1bab06a6d73872d2a064add1c0dd7b25097bd95e47012de` | **VERIFIED** |
| **Term Concordance** | `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` | 72 | 26 | `12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7` | **VERIFIED** |
| **Reference Concordance** | `data/interim/pilot/quickgo_slice/quickgo_reference_concordance_pilot.csv` | 12 | 18 | `3c7236264424937c81a34fb2a5c64384e8154ef6f184c86f658ab583ba50281a` | **VERIFIED** |

Additionally, all 8 upstream input dependencies recorded in Manifest v1.1 (`tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv`, `tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv`, `tests/fixtures/quickgo_pilot/manifest.json`, `data/interim/pilot/functional_claims_pilot.csv`, `data/interim/pilot/source_go_annotations_pilot.csv`, `data/interim/pilot/functional_coverage_pilot.csv`, `data/interim/pilot/manifest.json`, and `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv`) were verified bit-for-bit against their recorded digests.

---

## 2. Denominator Accounting & Comparison Universe Structure

### 2.1 Separation of Orthogonal Denominators
To prevent statistical confounding and ensure biological integrity, the pilot explicitly separates five non-interchangeable denominators:

```
┌────────────────────────────────────────────────────────────────────────┐
│                       ORTHOGONAL DENOMINATORS                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. COHORT ACCESSIONS (N = 8)                                           │
│    Biological protein identifiers selected for pilot analysis.         │
│                                                                        │
│ 2. ACCESSION-SOURCE PAIRS (N = 12)                                     │
│    Curated records representing a specific protein in a specific DB.   │
│                                                                        │
│ 3. ACCESSION-SOURCE-ASPECT COMPARISON UNITS (N = 36)                   │
│    The primary operational unit of GO comparison: Pair × {BP, CC, MF}. │
│                                                                        │
│ 4. POLICY-SPECIFIC CONCORDANCE ROWS (N = 72)                           │
│    Analytical evaluations: Unit × {Policy B, Policy C}.                │
│                                                                        │
│ 5. REFERENCE-CONCORDANCE ROWS (N = 12)                                 │
│    Publication inventory comparisons evaluated at the pair level.      │
└────────────────────────────────────────────────────────────────────────┘
```

> [!WARNING]
> **Prohibition Against Aggregation**: The 72 comparison rows must **NEVER** be treated as independent biological samples. They represent repeated, paired analytical evaluations of 36 GO aspect slices across 12 source records spanning only 8 protein accessions.

### 2.2 Complete Universe Enumeration
The 12 verified accession–source pairs and their structural distribution:

| Accession | Canonical UniProt Gene/Protein | Catalog Protein ID (`MFP_PROTEIN_ID_V1`) | Source Database (`source_id`) | Source Record ID |
|---|---|---|---|---|
| `A0A0H3CDS3` | KidO / CC_3350 (*C. vibrioides*) | `MFP:U:96deffc7f6cd3504` | `SRC_MULTITASKPROTDB_II` | Outside vertical slice |
| `E6KMA1` | DegP / MPN_653 (*Mycoplasma*) | `MFP:U:c6f1c6ae0e1cb137` | `SRC_MOONPROT` | `moonprot_254` |
| `P0AFW0` | RfaH (*E. coli*) | `MFP:U:9023923ecdd9d57f` | `SRC_MOONPROT` | `moonprot_13` |
| `P0AFW0` | RfaH (*E. coli*) | `MFP:U:9023923ecdd9d57f` | `SRC_MULTITASKPROTDB_II` | `multitask_26` |
| `P24228` | DacB / PBP4 (*E. coli*) | `MFP:U:75a37d1de4bcf985` | `SRC_MOONPROT` | `moonprot_288` |
| `P34788` | RS18 (*S. oleracea* / *A. thaliana*) | `MFP:U:d0cd1a882c7acdf3` | `SRC_MULTITASKPROTDB_II` | `multitask_31` |
| `P34788` | RS18 (*S. oleracea* / *A. thaliana*) | `MFP:U:d0cd1a882c7acdf3` | `SRC_PLANTMP` | `plantmp_1` |
| `P78007` | LDH (*M. pneumoniae*) | `MFP:U:44b217c1cc5847ae` | `SRC_MOONPROT` | `moonprot_239` |
| `Q42525` | HXK1 (*A. thaliana*) | `MFP:U:8272bae0e8df8149` | `SRC_MOONPROT` | `moonprot_1` |
| `Q42525` | HXK1 (*A. thaliana*) | `MFP:U:8272bae0e8df8149` | `SRC_MULTITASKPROTDB_II` | `multitask_33` |
| `Q42525` | HXK1 (*A. thaliana*) | `MFP:U:8272bae0e8df8149` | `SRC_PLANTMP` | `plantmp_2` |
| `Q9Y3E5` | PTH2 / Bit1 (*H. sapiens*) | `MFP:U:c382ca456ad5a4db` | `SRC_MULTITASKPROTDB_II` | `multitask_8` |

---

## 3. Evaluability Landscape & Non-Evaluability Diagnostics

### 3.1 Evaluability Transitions Across 36 Comparison Units
For each of the 36 comparison units, evaluability was evaluated under both Policy B (`captured_inventory_overlap`) and Policy C (`filtered_descriptive_overlap`). Exactly four transition states are mathematically possible:

| Evaluability Transition State | Definition | Unit Count | Percentage ($N = 36$) | Row Count ($N = 72$) | Percentage ($N = 72$) |
|---|---|:---:|:---:|:---:|:---:|
| **Evaluable under Both (B & C)** | Non-empty inventories under both B and C; compatible identity | **10** | **27.78%** (10/36) | **20** | **27.78%** (20/72) |
| **Evaluable only under B** | Non-empty under B, emptied by Policy C filtering | **0** | **0.00%** (0/36) | **0** | **0.00%** (0/72) |
| **Evaluable only under C** | Empty under B, non-empty under C (impossible) | **0** | **0.00%** (0/36) | **0** | **0.00%** (0/72) |
| **Non-evaluable under Both (B & C)** | Empty inventory, indeterminate aspect, unlinked, or gated | **26** | **72.22%** (26/36) | **52** | **72.22%** (52/72) |
| **Total Comparison Universe** | All units accounted for | **36** | **100.00%** | **72** | **100.00%** |

*Key Diagnostic Finding*: Policy C filtering did not cause any unit to drop out of evaluability ($\text{B-only} = 0$). All 10 units evaluable under Policy B remained evaluable under Policy C.

### 3.2 Primary Non-Evaluable Reason Distribution
Among the 26 non-evaluable units (52 rows), non-evaluability is partitioned into mutually exclusive primary reasons governed by the deterministic precedence hierarchy defined in [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md) and the Stage P3 specification:

```
[Precedence 1: unresolved_biological_identity] ──> 6 units (12 rows, 23.08%)
  └─ P34788 (MultitaskProtDB-II: BP, CC, MF; PlantMP: BP, CC, MF)
[Precedence 2: source_record_outside_slice]   ──> 3 units (6 rows, 11.54%)
  └─ A0A0H3CDS3 (MultitaskProtDB-II: BP, CC, MF)
[Precedence 3: source_aspect_indeterminate]    ──> 15 units (30 rows, 57.69%)
  └─ MoonProt records lacking explicit GO aspect tags (E6KMA1, P0AFW0, P24228, P78007, Q42525)
[Precedence 4: source_record_no_terms_aspect]  ──> 2 units (4 rows, 7.69%)
  └─ P0AFW0 (MultitaskProtDB-II: CC); Q42525 (PlantMP: CC)
```

| Primary Non-Evaluable Reason | Precedence Rank | Affected Accessions & Sources | Affected Aspects | Units ($N = 26$) | Rows ($N = 52$) | Percentage of Non-Evaluable Rows |
|---|:---:|---|---|:---:|:---:|:---:|
| `source_aspect_indeterminate` | 4 | MoonProt (`E6KMA1`, `P0AFW0`, `P24228`, `P78007`, `Q42525`) | BP, CC, MF | 15 | 30 | 57.69% (30/52) |
| `unresolved_biological_identity` | 1 | `P34788` (`SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`) | BP, CC, MF | 6 | 12 | 23.08% (12/52) |
| `source_record_outside_slice` | 2 | `A0A0H3CDS3` (`SRC_MULTITASKPROTDB_II`) | BP, CC, MF | 3 | 6 | 11.54% (6/52) |
| `source_record_no_terms_aspect` | 10 | `P0AFW0` (`MULTITASK`), `Q42525` (`PLANTMP`) | CC | 2 | 4 | 7.69% (4/52) |
| **Total Non-Evaluable** | — | — | — | **26** | **52** | **100.00%** |

### 3.3 Secondary Diagnostic Overlap
Secondary non-evaluable reasons capture co-occurring conditions that were superseded by higher-precedence primary reasons. Secondary reasons can overlap and are separated by semicolons in the data:
- `external_zero_annotations_overall` ($N = 6\text{ rows}$): Co-occurs on all 6 rows of `A0A0H3CDS3` / `SRC_MULTITASKPROTDB_II`. The primary reason was `source_record_outside_slice`, but QuickGO also stores zero annotations for this protein.
- `accession_unlinked_in_capture` ($N = 6\text{ rows}$): Co-occurs on all 6 rows of `E6KMA1` / `SRC_MOONPROT`. The primary reason was `source_aspect_indeterminate`, but the QuickGO accession is also unlinked in the database (`protein_id IS NULL`).
- `source_record_no_terms_aspect` ($N = 2\text{ rows}$): Co-occurs on `P34788` / `SRC_PLANTMP` / `CC` (both Policy B and C rows). The primary reason was `unresolved_biological_identity`, but PlantMP also stores zero CC terms for this record.

---

## 4. Paired Policy Analysis: Policy B vs. Policy C

### 4.1 Paired Concordance Results for All 10 Evaluable Units
The 10 comparison units evaluable under both policies were subjected to paired evaluation. All counts and metrics are extracted directly from `quickgo_concordance_pilot.csv`:

| Accession | Source ID | Aspect | Policy B Source ($S_B$) | Policy B QuickGO ($Q_B$) | Policy B Overlap ($O_B$) | Policy B Union ($U_B$) | Policy B Jaccard ($J_B$) | Policy C Source ($S_C$) | Policy C QuickGO ($Q_C$) | Policy C Overlap ($O_C$) | Policy C Union ($U_C$) | Policy C Jaccard ($J_C$) | Score Diff ($\Delta J$) | Direction of Change |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `P0AFW0` | `MULTITASK` | `BP` | 3 | 4 | 2 | 5 | 0.4000 | 3 | 4 | 2 | 5 | 0.4000 | 0.0000 | Identical |
| `P0AFW0` | `MULTITASK` | `MF` | 7 | 6 | 4 | 9 | 0.4444 | 6 | 6 | 4 | 8 | 0.5000 | +0.0556 | **Increased** |
| `Q42525` | `MULTITASK` | `BP` | 14 | 17 | 7 | 24 | 0.2917 | 13 | 17 | 7 | 23 | 0.3043 | +0.0126 | **Increased** |
| `Q42525` | `MULTITASK` | `CC` | 9 | 7 | 4 | 12 | 0.3333 | 9 | 7 | 4 | 12 | 0.3333 | 0.0000 | Identical |
| `Q42525` | `MULTITASK` | `MF` | 11 | 8 | 6 | 13 | 0.4615 | 10 | 8 | 6 | 12 | 0.5000 | +0.0385 | **Increased** |
| `Q42525` | `PLANTMP` | `BP` | 18 | 17 | 3 | 32 | 0.0938 | 17 | 17 | 3 | 31 | 0.0968 | +0.0030 | **Increased** |
| `Q42525` | `PLANTMP` | `MF` | 8 | 8 | 3 | 13 | 0.2308 | 7 | 8 | 3 | 12 | 0.2500 | +0.0192 | **Increased** |
| `Q9Y3E5` | `MULTITASK` | `BP` | 6 | 3 | 3 | 6 | 0.5000 | 6 | 3 | 3 | 6 | 0.5000 | 0.0000 | Identical |
| `Q9Y3E5` | `MULTITASK` | `CC` | 4 | 4 | 3 | 5 | 0.6000 | 4 | 4 | 3 | 5 | 0.6000 | 0.0000 | Identical |
| `Q9Y3E5` | `MULTITASK` | `MF` | 2 | 2 | 1 | 3 | 0.3333 | 2 | 2 | 1 | 3 | 0.3333 | 0.0000 | Identical |

*Summary Metrics Across the 10 Paired Comparisons*:
- Score Increased: **5 units (50.00%)**
- Score Identical: **5 units (50.00%)**
- Score Decreased: **0 units (0.00%)**
- Mean Jaccard under Policy B: **0.3689** (range: 0.0938 to 0.6000)
- Mean Jaccard under Policy C: **0.3818** (range: 0.0968 to 0.6000)
- Mean Score Difference ($\Delta J$): **+0.0129** (range: 0.0000 to +0.0556)

### 4.2 Exclusion Accounting and Cause of Score Changes
A rigorous audit of the exclusion fields in `quickgo_concordance_pilot.csv` reveals the exact mechanism responsible for the score increases:

| Accession | Source ID | Aspect | QuickGO ND Rows (`nd_matching_rows_count`) | QuickGO Root Rows (`root_matching_rows_count`) | Net Excluded QuickGO Rows (`net_excluded_rows_count`) | QuickGO Terms Lost (`terms_lost_after_filtering_count`) | Source Unassessed Rows (`unassessed_evidence_rows_count`) | Source Root Exclusions Detected |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `P0AFW0` | `MULTITASK` | `BP` | 0 | 0 | 0 | 0 | 0 | None |
| `P0AFW0` | `MULTITASK` | `MF` | 0 | 0 | 0 | 0 | 4 | `GO:0003674` removed from Source |
| `Q42525` | `MULTITASK` | `BP` | 0 | 0 | 0 | 0 | 8 | `GO:0008150` removed from Source |
| `Q42525` | `MULTITASK` | `CC` | 0 | 0 | 0 | 0 | 0 | None |
| `Q42525` | `MULTITASK` | `MF` | 0 | 0 | 0 | 0 | 4 | `GO:0003674` removed from Source |
| `Q42525` | `PLANTMP` | `BP` | 0 | 0 | 0 | 0 | 19 | `GO:0008150` removed from Source |
| `Q42525` | `PLANTMP` | `MF` | 0 | 0 | 0 | 0 | 8 | `GO:0003674` removed from Source |
| `Q9Y3E5` | `MULTITASK` | `BP` | 0 | 0 | 0 | 0 | 0 | None |
| `Q9Y3E5` | `MULTITASK` | `CC` | 0 | 0 | 0 | 0 | 0 | None |
| `Q9Y3E5` | `MULTITASK` | `MF` | 0 | 0 | 0 | 0 | 0 | None |

### 4.3 Scientific Interpretation of Policy C Behavior
1. **Source Root Pruning as the Sole Driver**:
   In the external QuickGO capture for these 10 units, there were **zero ND rows** and **zero root-term rows** (`net_excluded_rows_count = 0`). Consequently, the QuickGO term sets ($Q_B = Q_C$) remained completely unaffected.
   In contrast, MultitaskProtDB-II and PlantMP source annotations contained generic root placeholders (`GO:0003674` "molecular_function" and `GO:0008150` "biological_process"). Under Policy C, these root terms were filtered out from the source inventories ($S_C = S_B - 1$).
2. **Mathematical Mechanics of Jaccard Increase**:
   Because the excluded root terms did not exist in QuickGO, they were source-only terms that contributed exclusively to the union denominator ($U_B = |S_B \cup Q_B|$). Removing them reduced the union denominator by 1 ($U_C = U_B - 1$) while leaving the intersection numerator unchanged ($O_C = O_B$).
   $$J_C = \frac{O_B}{U_B - 1} > \frac{O_B}{U_B} = J_B$$
3. **No Unwarranted Biological Inference**:
   The resulting increase in Jaccard similarity is an **arithmetic artifact of pruning uninformative high-level placeholders from the source claim inventory**, NOT proof of superior biological agreement or higher functional confidence.
4. **Preservation of Unassessed Evidence**:
   A total of 43 source annotation rows carried missing evidence codes across these 10 units (e.g. 19 rows in `Q42525` PlantMP BP). In strict compliance with Policy C guarantees, 100% of these rows were classified as `unassessed` and retained in the comparison. None were converted to `ND` or dropped.

---

## 5. Bibliographic Reference Overlap & Namespace Integrity

### 5.1 Descriptive Reference Concordance (12 Pairs under Option A)
Reference concordance was computed at the protein entity / source record level across all 12 cohort pairs, comparing extracted source publication identifiers against QuickGO citations:

| Accession | Source Database | Source Status / Completeness | Source References ($R_{src}$) | QuickGO References ($R_{qgo}$) | Exact Shared Citations ($R_{src} \cap R_{qgo}$) | Source Only | QuickGO Only | Reference Jaccard ($J_{ref}$) | Reference Evaluability Status | Primary Non-Evaluable Reason | Shared Citation Identifiers |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| `A0A0H3CDS3` | `MULTITASK` | Indeterminate | null | 0 | null | null | null | null | `not_evaluable` | `source_record_outside_slice` | None |
| `E6KMA1` | `MOONPROT` | Complete | 1 | null | null | null | null | null | `not_evaluable` | `accession_unlinked_in_capture` | None |
| `P0AFW0` | `MOONPROT` | Complete | 1 | 8 | 1 | 0 | 7 | 0.1250 | `evaluable` | None | `PMID:22817892` |
| `P0AFW0` | `MULTITASK` | Complete | 1 | 8 | 1 | 0 | 7 | 0.1250 | `evaluable` | None | `PMID:22817892` |
| `P24228` | `MOONPROT` | Indeterminate | null | 15 | null | null | null | null | `not_evaluable` | `source_extraction_incomplete` | None |
| `P34788` | `MULTITASK` | Complete | 1 | 20 | 1 | 0 | 19 | null | `not_evaluable` | `unresolved_biological_identity` | `PMID:7913892` |
| `P34788` | `PLANTMP` | Complete | 1 | 20 | 1 | 0 | 19 | null | `not_evaluable` | `unresolved_biological_identity` | `PMID:7913892` |
| `P78007` | `MOONPROT` | Complete | 1 | 6 | 1 | 0 | 5 | 0.1667 | `evaluable` | None | `PMID:27616280` |
| `Q42525` | `MOONPROT` | Complete | 1 | 28 | 1 | 0 | 27 | 0.0357 | `evaluable` | None | `PMID:17081979` |
| `Q42525` | `MULTITASK` | Complete | 1 | 28 | 1 | 0 | 27 | 0.0357 | `evaluable` | None | `PMID:12690200` |
| `Q42525` | `PLANTMP` | Complete | 2 | 28 | 0 | 2 | 28 | 0.0000 | `evaluable` | None | None (disjoint) |
| `Q9Y3E5` | `MULTITASK` | Complete | 1 | 12 | 1 | 0 | 11 | 0.0833 | `evaluable` | None | `PMID:14660562` |

### 5.2 Key Reference Concordance Findings
1. **Low Descriptive Overlap Despite Exact Sharing**:
   - In 6 of the 7 evaluable pairs, the source database cited exactly 1 primary publication, and that exact identifier was present in QuickGO's broader citation inventory ($R_{src} \cap R_{qgo} = 1$).
   - However, because QuickGO captures extensive proteome-scale annotation sets (between 6 and 28 distinct PMIDs per protein), the union denominator is dominated by QuickGO-only citations, resulting in low descriptive Jaccard scores ($J_{ref} \in [0.0357, 0.1667]$).
2. **PlantMP Disjoint Non-Empty Comparison on `Q42525`**:
   - PlantMP cites `PMID:901436` and `PMID:12690178` (2 distinct PMIDs). QuickGO captures 28 distinct PMIDs for `Q42525`.
   - The intersection is exactly 0 ($R_{src} \cap R_{qgo} = \emptyset$). Under the established empty-set convention, because both inventories are non-empty and comparable, $J_{ref} = 0.0000$ with status `evaluable` and completeness `complete`. This reflects genuine identifier divergence between PlantMP's primary sources and QuickGO's annotation literature.
3. **Indeterminate vs. Observed Zero References (`P24228`)**:
   - For `P24228` (MoonProt), HTML extraction failure in the upstream loader prevented inventory extraction. In compliance with the semantic closure rules, this is recorded as `comparison_completeness = "indeterminate"`, `source_references_count = null`, and `primary_non_evaluable_reason = "source_extraction_incomplete"`. It is NOT conflated with an observed zero-reference record.
4. **Namespace Integrity**:
   - In all 12 rows, `source_unresolved_references_count` is 0 (or null where indeterminate). No malformed tokens or narrative strings entered the comparable reference sets.

---

## 6. Candidate Profiles Across the Eight-Accession Cohort

The following profiles summarize the complete empirical observations across all 8 cohort proteins:

### 1. `Q42525` — Hexokinase-1 (HXK1, *Arabidopsis thaliana*)
- **Catalog Identity**: `MFP:U:8272bae0e8df8149` (Verified canonical UniProt entity).
- **Source Representations**: Covered in all 3 sources: MultitaskProtDB-II (`multitask_33`), MoonProt (`moonprot_1`), and PlantMP (`plantmp_2`).
- **QuickGO Capture**: 56 annotation rows, 32 distinct terms, 28 distinct PMIDs (`annotations_available`).
- **Concordance Findings**:
  - MultitaskProtDB-II: Evaluable across all 3 aspects. Concordance is moderate (BP: $J_C = 0.3043$; CC: $J_C = 0.3333$; MF: $J_C = 0.5000$).
  - PlantMP: Evaluable in BP ($J_C = 0.0968$) and MF ($J_C = 0.2500$); CC is non-evaluable because PlantMP provides 0 CC annotations (`source_record_no_terms_aspect`).
  - MoonProt: All 3 aspects non-evaluable due to undeclared GO aspects (`source_aspect_indeterminate`).
- **Reference Overlap**: Multitask and MoonProt share distinct PMIDs with QuickGO (`PMID:12690200` and `PMID:17081979`, respectively; $J_{ref} = 0.0357$). PlantMP cites two older PMIDs (`PMID:901436`, `PMID:12690178`) not captured in QuickGO ($J_{ref} = 0.0000$).

### 2. `Q9Y3E5` — Peptidyl-tRNA hydrolase 2 / Bit1 (PTH2, *Homo sapiens*)
- **Catalog Identity**: `MFP:U:c382ca456ad5a4db`.
- **Source Representations**: Covered in MultitaskProtDB-II (`multitask_8`).
- **QuickGO Capture**: 24 annotation rows, 9 distinct terms, 12 distinct PMIDs (`annotations_available`).
- **Concordance Findings**:
  - Highest observed concordance in the entire cohort: BP ($J = 0.5000$, 3 shared terms), CC ($J = 0.6000$, 3 shared terms: mitochondrion, cytoplasm, cytosol), and MF ($J = 0.3333$, 1 shared term).
  - Policy C produced identical scores ($\Delta J = 0.0000$) because neither source nor QuickGO contained ND or root terms.
- **Reference Overlap**: Shares `PMID:14660562` with QuickGO ($J_{ref} = 0.0833$).

### 3. `P0AFW0` — Transcriptional regulator RfaH (*Escherichia coli*)
- **Catalog Identity**: `MFP:U:9023923ecdd9d57f`.
- **Source Representations**: Covered in MultitaskProtDB-II (`multitask_26`) and MoonProt (`moonprot_13`).
- **QuickGO Capture**: 17 annotation rows, 11 distinct terms, 8 distinct PMIDs (`annotations_available`).
- **Concordance Findings**:
  - MultitaskProtDB-II: Evaluable in BP ($J = 0.4000$) and MF ($J_B = 0.4444 \to J_C = 0.5000$). CC is empty in source (`source_record_no_terms_aspect`).
  - MoonProt: Non-evaluable across all aspects (`source_aspect_indeterminate`).
- **Reference Overlap**: Both Multitask and MoonProt cite `PMID:22817892`, which is captured in QuickGO ($J_{ref} = 0.1250$ for both).

### 4. `P34788` — 40S ribosomal protein S18 (*Spinacia oleracea* / *Arabidopsis thaliana*)
- **Catalog Identity**: `MFP:U:d0cd1a882c7acdf3`.
- **Source Representations**: Covered in MultitaskProtDB-II (`multitask_31`) and PlantMP (`plantmp_1`). Both cite spinach (*Spinacia oleracea*).
- **QuickGO Capture**: 28 annotation rows, 21 distinct terms, 20 distinct PMIDs (`annotations_available`). However, UniProt/QuickGO indexes RS18_ARATH from thale cress (*Arabidopsis thaliana*).
- **Concordance Findings**:
  - All 12 concordance rows and both reference rows are strictly gated as `not_evaluable` ($J = \text{null}$) with primary reason `unresolved_biological_identity`.
  - Diagnostic term accounting reveals substantial technical overlap (e.g. Multitask CC shares 8 terms with QuickGO), demonstrating that accession joins succeed technically while biological comparability remains unresolved upstream.
- **Reference Overlap**: Both sources cite `PMID:7913892`, which is present in QuickGO, but reference scores remain ineligible under the identity gate.

> [!NOTE]
> **Audit Reconciliation Notice (2026-11-18)**:
> The narrative above preserves the historical P4 analytical finding. As documented in the dated [Addendum §11.1](#111-reconciliation-of-p34788-taxonomic-attribution-and-identity-gate), direct inspection of the raw source files on disk demonstrates that PlantMP and MultitaskProtDB-II actually attribute `P34788` to *Arabidopsis thaliana* (PMID 7913892). However, in accordance with ADR-005, the `unresolved_biological_identity` gate remains in effect for Stage P3/P4 and initial PIL-04.1B recomparisons pending a formal curatorial decision under candidate task `PIL-04.3`.

### 5. `P78007` — L-lactate dehydrogenase (LDH, *Mycoplasmoides pneumoniae*)
- **Catalog Identity**: `MFP:U:44b217c1cc5847ae`.
- **Source Representations**: Covered in MoonProt (`moonprot_239`).
- **QuickGO Capture**: 10 annotation rows, 9 distinct terms, 6 distinct PMIDs (`annotations_available`).
- **Concordance Findings**: All 6 concordance rows are non-evaluable due to undeclared GO aspects in MoonProt (`source_aspect_indeterminate`).
- **Reference Overlap**: Evaluable at the entity level; shares `PMID:27616280` with QuickGO ($J_{ref} = 0.1667$).

### 6. `P24228` — Penicillin-binding protein 4 (DacB, *Escherichia coli*)
- **Catalog Identity**: `MFP:U:75a37d1de4bcf985`.
- **Source Representations**: Covered in MoonProt (`moonprot_288`).
- **QuickGO Capture**: 21 annotation rows, 13 distinct terms, 15 distinct PMIDs (`annotations_available`).
- **Concordance Findings**:
  - Source GO annotations were successfully extracted (22 rows, 21 distinct terms), confirming that MoonProt functional claims were preserved.
  - However, because MoonProt lacks aspect tags, all 6 concordance rows are non-evaluable (`source_aspect_indeterminate`).
- **Reference Overlap**: MoonProt record 288 suffered an HTML parse failure during upstream ingestion. The reference inventory is indeterminate (`source_extraction_incomplete`, counts `null`), distinguishing extraction failure from an observed zero-reference record.

### 7. `A0A0H3CDS3` — Bifunctional regulator KidO (*Caulobacter vibrioides*)
- **Catalog Identity**: `MFP:U:96deffc7f6cd3504`.
- **Database Status**: Technical missingness control. Linked in the `protein` table (`A0A0H3CDS3_CAUVN`), but **0 annotations** exist in `protein_go_term_annotation` (`zero_annotations_found`).
- **Source Representation**: Outside the 6-record Multitask vertical slice (`source_record_outside_slice`).
- **Concordance & Reference Findings**: 100% non-evaluable with primary reason `source_record_outside_slice` and secondary reason `external_zero_annotations_overall` / `external_zero_references`.

### 8. `E6KMA1` — DegP protease (*Mycoplasma*)
- **Catalog Identity**: `MFP:U:c6f1c6ae0e1cb137`.
- **Database Status**: Technical linkage control. Present in the `accession` table, but unlinked (`protein_id IS NULL`, `unlinked_in_database`).
- **Source Representation**: Covered in MoonProt (`moonprot_254`, 1 citation).
- **Concordance & Reference Findings**: 100% non-evaluable. Concordance carries primary reason `source_aspect_indeterminate` and secondary reason `accession_unlinked_in_capture`. Reference concordance carries primary reason `accession_unlinked_in_capture`.

---

## 7. Prioritized Follow-Up Matrix: Separating Analysis from Remediation

In accordance with SDD lifecycle principles, Stage P4 strictly documents empirical observations. All engineering fixes, data re-extractions, and curation tasks must be authorized as separate increments:

| Priority | Operational Title | Observed Empirical Limitation | Affected Cases / Units | Likely Scientific or Operational Benefit | Key Dependencies & Uncertainties | Qualitative Effort | Acceptance / Exit Criterion |
|:---:|---|---|---|---|---|:---:|---|
| **P1** | **Upstream MoonProt GO Aspect Disambiguation Protocol** | 100% of MoonProt GO annotations lack aspect tags, causing 15 units (30 rows, 41.67%) to remain non-evaluable. | MoonProt records: `E6KMA1`, `P0AFW0`, `P24228`, `P78007`, `Q42525`. | [Historical/Superseded text]: "Enables evaluable GO concordance across all MoonProt records without inferring new functions." *(Superseded: see §11.2. Namespace enrichment resolves aspect indeterminacy but does not establish evaluability; unlinked controls like E6KMA1 remain non-evaluable).* | Requires an approved ontology lookup mapping existing `GO:[0-9]{7}` IDs to aspects (`BP`, `CC`, `MF`). | Low (deterministic mapping from fixed GO ontology) | 100% of valid MoonProt GO IDs assigned canonical aspect; 0 aspect-indeterminate rows in slice. |
| **P2** | **Investigation of MoonProt Record 288 (`P24228`) HTML Ingestion** | HTML parse failure in MoonProt loader resulted in `coverage_status = "parse_failure"` and indeterminate citation inventory. | `P24228` (`moonprot_288`), 1 reference concordance row. | Restores reference evaluability for DacB; ensures complete citation accounting. | Cause of parse failure unknown; requires inspecting raw HTML artifact without assuming regex fix. | Low (targeted loader bugfix & re-test) | Record 288 parses successfully; citations extracted and verified against raw HTML. |
| **P3** | **Taxonomic Resolution & Orthology Review for `P34788`** | [Historical premise for gate]: Accession `P34788` was recorded as mapping to *S. oleracea* in source claims but *A. thaliana* in UniProt/QuickGO, gating 12 concordance rows. *(Audit correction: raw source records do not support the spinach premise; see §11.1. The historical gate remains active pending formal PIL-04.3 curatorial review; curation will evaluate comparability but does not automatically unlock comparisons).* | `P34788` (Multitask & PlantMP), 12 concordance rows, 2 reference rows. | Resolves biological comparability gate under ADR-005; unlocks high-overlap CC comparisons. | Botanical literature review required; must not automatically swap accessions without curator sign-off. | Medium (curation review & ADR-005 compliance) | Curatorial determination documented; canonical accession assigned or cross-species transfer formally rejected. |
| **P4** | **Database Snapshot Linkage & Missingness Remediation** | `E6KMA1` is unlinked in `MFP_QuickV1`; `A0A0H3CDS3` has zero annotations; candidate v0.3.0 accessions missing. | `E6KMA1`, `A0A0H3CDS3`, candidate entities absent from capture. | Aligns external database coverage with unified catalog candidate release v0.3.0. | Requires coordination with `protein-information-system` and database rebuild. | Medium to High (database re-ingestion) | Accessions linked in database; fresh snapshot exported under repeatable read isolation. |
| **P5** | **Claim-Level Bibliographic Relation Extraction Protocol** | Descriptive protein-level citation overlap cannot prove whether cited papers validate moonlighting functions. | All 12 reference rows and catalog bibliographic claims. | Establishes traceable evidence chains linking specific PMIDs to specific functional claims under ADR-007. | High scientific complexity; requires sentence-, table-, or figure-level evidence parsing. | High (requires full NLP or curatorial pipeline) | Formally approved bibliographic extraction contract with claim-level provenance. |

---

## 8. Artifact Preservation, Availability, and Regeneration Realities

### 8.1 Rigorous Separation of Preservation Dimensions
To ensure transparency regarding repository state, this report explicitly distinguishes four distinct preservation dimensions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESERVATION DIMENSIONS                         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. INTEGRITY VERIFICATION (ACTIVE & VERIFIED)                          │
│    SHA-256 hashes permanently recorded in Manifest v1.1 and docs.     │
│                                                                        │
│ 2. AVAILABILITY (LOCAL ONLY)                                           │
│    Files exist on local developer filesystem under data/interim/.      │
│                                                                        │
│ 3. REGENERATION CAPABILITY (CONDITIONAL)                               │
│    Requires local MFP_QuickV1 database, PIS f54bc4f, and Tier A data. │
│                                                                        │
│ 4. DURABLE PRESERVATION (PENDING AUTHORIZATION)                        │
│    data/interim/ is gitignored; NOT tracked in Git or remote storage. │
└────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Accurate Preservation Disclosure
- **Git Commits Versioned Code, Not Interim Data**: The successful pushes of Commit `4906b2e` and Commit `21a3c8e` versioned the technical engine, schemas, test suites, and specifications. They did **NOT** publish or preserve the gitignored files under `data/interim/pilot/quickgo_slice/`.
- **Durable Preservation is PENDING**: A fresh clone of `mfp-bibliography` from GitHub currently lacks the `data/interim/` directory. Without local provisioning, offline pipeline reruns will fail.
- **Regeneration Requirements**: Byte-identical reproduction of these outputs from scratch requires:
  1. The historical PostgreSQL database snapshot `MFP_QuickV1` (observed `2026-11-12 15:53:22 UTC`).
  2. `protein-information-system` repository at commit `f54bc4f` (preserving bare numeric PMIDs and `GO_REF` CURIEs).
  3. Locally provisioned Tier A interim inputs (`functional_claims_pilot.csv`, `source_go_annotations_pilot.csv`, `functional_coverage_pilot.csv`).
  4. Python 3.12 with dependencies specified in `pyproject.toml`.
  Extraction from a live, evolving QuickGO database will **not** reproduce identical hashes.

### 8.3 Recommended Minimal Preservation Package
Subject to user rights and a separate authorization increment, maintainers should establish a durable preservation arrangement:
- Create an immutable, versioned fixture archive (e.g., `tests/fixtures/quickgo_concordance_p3_slice.tar.gz`) containing the 4 output CSVs and Manifest v1.1, anchored by a recorded sha256 checksum file.
- Alternatively, provision an offline S3/Zenodo/OSF repository storing frozen interim pilot slices.
- Do **NOT** modify `.gitignore` or track large volatile data files directly in the Git repository tree.

---

## 9. Executable Calculation Recipe

To ensure complete scientific auditability, the following compact Python script recomputes the principal summary metrics, evaluability counts, and paired policy comparisons directly from the frozen CSV files:

```python
"""Compact Executable Calculation Recipe for Stage P4 Report Metrics."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

P3_DIR = Path("data/interim/pilot/quickgo_slice")

# 1. Load Datasets
with open(P3_DIR / "quickgo_coverage_pilot.csv") as f:
    cov_rows = list(csv.DictReader(f))

with open(P3_DIR / "quickgo_concordance_pilot.csv") as f:
    conc_rows = list(csv.DictReader(f))

with open(P3_DIR / "quickgo_reference_concordance_pilot.csv") as f:
    ref_rows = list(csv.DictReader(f))

# 2. Denominator Checks
assert len(cov_rows) == 8, f"Expected 8 accessions, got {len(cov_rows)}"
assert len(conc_rows) == 72, f"Expected 72 concordance rows, got {len(conc_rows)}"
assert len(ref_rows) == 12, f"Expected 12 reference rows, got {len(ref_rows)}"

# 3. Evaluability Transitions across 36 Units
units = defaultdict(dict)
for r in conc_rows:
    units[(r["accession"], r["source_id"], r["aspect"])][r["policy_id"]] = r

both_eval = [u for u, p in units.items() if p["captured_inventory_overlap"]["concordance_status"] == "evaluable" 
             and p["filtered_descriptive_overlap"]["concordance_status"] == "evaluable"]
neither_eval = [u for u, p in units.items() if p["captured_inventory_overlap"]["concordance_status"] == "not_evaluable" 
               and p["filtered_descriptive_overlap"]["concordance_status"] == "not_evaluable"]

print(f"Comparison Units: Total={len(units)}, Evaluable Both={len(both_eval)}, Non-Evaluable Both={len(neither_eval)}")

# 4. Paired Policy Calculations
score_diffs = []
for u in both_eval:
    jb = float(units[u]["captured_inventory_overlap"]["jaccard_similarity"])
    jc = float(units[u]["filtered_descriptive_overlap"]["jaccard_similarity"])
    diff = round(jc - jb, 4)
    score_diffs.append((u, jb, jc, diff))

increased = [d for d in score_diffs if d[3] > 0]
identical = [d for d in score_diffs if d[3] == 0]
print(f"Paired Policy Units: Increased={len(increased)}, Identical={len(identical)}, Decreased={len(score_diffs) - len(increased) - len(identical)}")

# 5. Reference Concordance Checks
eval_refs = [r for r in ref_rows if r["reference_concordance_status"] == "evaluable"]
disjoint_refs = [r for r in eval_refs if float(r["jaccard_similarity"]) == 0.0]
print(f"Reference Rows: Total={len(ref_rows)}, Evaluable={len(eval_refs)}, Genuinely Disjoint={len(disjoint_refs)}")
```

---

## 10. Scientific Interpretation Boundaries & Operational Conclusions

### 10.1 Scientific Scope Limitations
1. **Descriptive Integration, Not Biological Validation**: Lexical overlap of Gene Ontology identifiers measures concordance between distinct database curation efforts. High Jaccard similarity does **not** validate biological moonlighting, and low Jaccard similarity does **not** prove absence of function.
2. **Identifier Overlap, Not Literature Support**: Co-occurrence of PubMed IDs at the protein entity level confirms that two curation initiatives consulted the same primary publication. It does **not** confirm that the cited paper supports the specific functional claims made by either database.
3. **No Generalization to Full Catalog**: The findings in this report describe an 8-protein pilot cohort selected purposively to evaluate technical edge cases (taxonomic splits, missingness, aspect gaps). Findings cannot be extrapolated to the full 2,322 entities of candidate release `v0.3.0`.
4. **No Score Thresholds**: This report establishes no arbitrary "acceptable" or "passing" Jaccard cutoffs. Quantitative scores are reported purely as continuous descriptive properties of the paired datasets.

### 10.2 Final Handoff Status
With the completion of this descriptive analysis report, the deliverables authorized for Stage P4 are fulfilled. The repository remains in a clean, auditable state. Any subsequent activities—including Stage P5, catalog promotion, or upstream remediation—require separate human authorization under repository governance.

---

## 11. Addendum: Audit Reconciliation & Clarifications (2026-11-18 / 2026-11-19)

This addendum records the findings of the 2026-11-17/18 focused technical audit regarding two specific analytical reporting elements in this Stage P4 report. Baseline datasets and numerical analytical results are preserved, while narrative sections in Sections 4 and 7 have received explicit audit annotations, labels, and cross-references pointing to this section for binding curatorial and methodological clarifications.

### 11.1 Reconciliation of P34788 Taxonomic Attribution and Identity Gate
1. **Raw Source Evidence on Disk**:
   - `data/raw/plantmp/PlantMP_all.csv` (row 1, line 2): Explicitly attributes `P34788` ("40S ribosomal protein S18, RPS18A") to organism **`Arabidopsis thaliana`**, citing reference **`7913892`** (`confirmed`).
   - `data/raw/multitaskprotdb-ii/proteins.csv` (lines 6934–6958): Explicitly attributes `P34788` ("S18 (40S ribosomal protein S18)") to organism **`Arabidopsis thaliana`**, citing reference **`7913892`**.
   - Neither raw source file contains any textual attribution of accession `P34788` to spinach (*Spinacia oleracea*). Both raw sources catalog the protein as an *Arabidopsis thaliana* entity, coinciding with UniProtKB / QuickGO (`RS18_ARATH`).
2. **Origin of the Spinacia oleracea Attribution**:
   - The *Spinacia oleracea* discrepancy was introduced as a hardcoded text literal in an ad-hoc SQL export query draft in `docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md` (line 781):
     `CASE WHEN cohort.accession = 'P34788' THEN 'PlantMP/Multitask cite Spinacia oleracea; UniProt/QuickGO indexes RS18_ARATH from Arabidopsis thaliana; technical accession join succeeds but biological identity remains an unresolved upstream issue' ...`
   - This note was subsequently incorporated into `quickgo_coverage_pilot.csv` and propagated into the descriptive text of Sections 4 and 7 without independent verification against the raw CSV tables.
3. **Curatorial Disposition and Separation of Truth from Gating**:
   - *Factual Correction*: The statement that PlantMP and MultitaskProtDB-II assign `P34788` to spinach is empirically incorrect relative to the raw source data in the repository.
   - *Preservation of Gate*: Correcting this factual reporting error does **not** autonomously resolve entity comparability or authorize lifting the `unresolved_biological_identity` gate. In accordance with ADR-005 and repository governance, removing an identity gate requires a formal curatorial audit memo (`PIL-04.3 Candidate Task: Traceable Curatorial Review for P34788`).
   - *Immutability of P3/P4 Baseline*: The historical Stage P3 concordance matrix and Stage P4 descriptive findings remain frozen with `P34788` gated as observed ($J = \text{null}$, `primary_non_evaluable_reason = "unresolved_biological_identity"`). The initial recomparison in Task PIL-04.1B must likewise retain this historical gate; any gate modification belongs strictly to a subsequent, separately versioned increment.

### 11.2 Clarification of MoonProt Evaluability Expectations
1. **Scope of Metadata Enrichment (Task PIL-04.1A)**:
   - Task `PIL-04.1A` performed deterministic GO namespace enrichment (`derived_source_go_aspects_pilot.csv`). It did **not** recalculate concordance metrics, compute Jaccard similarities, or demonstrate any evaluability transitions.
2. **Multi-Barrier Evaluability Model**:
   - Resolving aspect indeterminacy removes only one specific obstacle (lack of `BP`, `CC`, or `MF` classification). An annotation unit becomes evaluable if and only if all orthogonal criteria are simultaneously met:
     - Aspect is deterministically assigned (not `source_aspect_indeterminate`).
     - Biological identity is compatible (not `unresolved_biological_identity`).
     - Entity is linked in capture database (not `accession_unlinked_in_capture` or `source_record_outside_slice`).
     - Both source and QuickGO have non-empty inventories for the specific aspect and policy under evaluation ($|S| > 0$ and $|Q| > 0$).
   - **Non-Empty Disjoint Sets**: Crucially, evaluability does **not** require a non-empty intersection ($S \cap Q \neq \emptyset$). If both $|S| > 0$ and $|Q| > 0$ with $S \cap Q = \emptyset$, the comparison yields Jaccard similarity $J = 0.0000$ with `concordance_status = "evaluable"`. This is a valid, evaluable scientific outcome (measurable divergence), fundamentally distinct from a non-evaluable row with null Jaccard.
3. **Independent Obstacle on E6KMA1**:
   - Under the frozen pilot database capture (`MFP_QuickV1`), accession `E6KMA1` carries an independent database linkage defect documented in Section 3.3 and Section 4 (`accession_unlinked_in_capture`, where `protein_id IS NULL`).
   - Consequently, all 6 rows for `E6KMA1` (3 comparison units $\times$ 2 policies) remain non-evaluable even after full aspect disambiguation. This defect is specific to the frozen database capture and must not be generalized to hypothetical future database snapshots.
4. **Supersession of Early Projections**:
   - The statement in Section 7 (Table P1) that aspect disambiguation "enables evaluable GO concordance across all MoonProt records" is superseded.
   - The figure of 30 rows represents the historical count of rows where `source_aspect_indeterminate` was the primary non-evaluable reason. Excluding the 6 rows of `E6KMA1`, at most 24 rows represent a theoretical upper bound of MoonProt rows eligible to become evaluable if both source and QuickGO inventories are non-empty ($|S| > 0$ and $|Q| > 0$).
   - The figure 24 is a theoretical upper bound, NOT an empirical forecast, observed result, or acceptance threshold. Projections such as "+22 evaluable rows" or "42 evaluable rows" are pre-execution analytical hypotheses, **not** verified results. Actual evaluability transitions must be empirically measured and verified by Task PIL-04.1B.
