# Roadmap: Scaling Functional & Bibliographic Evidence Validation to MoonProt, MultitaskProtDB-II, and PlantMP

| Metadata Attribute | Value |
|---|---|
| **Document Title** | Roadmap: Scaling Functional & Bibliographic Evidence Validation to MoonProt, MultitaskProtDB-II, and PlantMP |
| **Document ID** | `ROADMAP-PILOT-TO-THREE-SOURCE-VALIDATION-2026-11-20` |
| **Document Location** | `docs/roadmap/pilot-to-three-source-validation-roadmap.md` |
| **Target Repository** | `mfp-bibliography` (`feature/functional-normalization`) |
| **Authority Level** | Level 4/6 Advisory Technical & Scientific Proposal (Authorizes no implementation, pipeline execution, exports, or policy modifications without human sign-off) |
| **Status** | **Draft — Pending Human Review** |
| **Authoring Date** | 2026-11-20 |
| **Inspected HEAD** | `f9d9fba58a5a03a949c346a5956b8795b312b24d` |
| **Historical Baseline Reference** | `f9d9fba58a5a03a949c346a5956b8795b312b24d` (PIL-04.1B v0 Documentary Closure Commit) |
| **Governing Documents** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Related Specifications & Reports** | - Inventory Audit Specification Package: [`specs/three-source-inventory-audit/spec.md`](../../specs/three-source-inventory-audit/spec.md)<br>- PIL-04.1B Descriptive Report: [`docs/reports/quickgo-pilot-pil-04.1b-descriptive-results.md`](../reports/quickgo-pilot-pil-04.1b-descriptive-results.md)<br>- PIL-04.1B Specification Package: [`specs/quickgo-pilot-concordance-recomparison/spec.md`](../../specs/quickgo-pilot-concordance-recomparison/spec.md)<br>- PIL-04.1A Specification Package: [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md)<br>- Stage P4 Descriptive Report: [`docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`](../reports/quickgo-pilot-p4-descriptive-analysis-report.md)<br>- Pilot Preservation Record: [`docs/reports/quickgo-pilot-preservation-record.md`](../reports/quickgo-pilot-preservation-record.md)<br>- Preservation & Communication Roadmap: [`docs/roadmap/draft-pilot-preservation-communication-and-operational-roadmap.md`](draft-pilot-preservation-communication-and-operational-roadmap.md) |

---

> [!IMPORTANT]
> **Advisory Scope & Execution Boundary Notice**:
> This document is a strategic, architectural, and scientific roadmap for the planned extension of the functional and bibliographic concordance system. Under repository governance ([`AGENTS.md`](../../AGENTS.md) §1, §4) and [ADR-001](../decisions/ADR-001-repository-scope.md), this roadmap is an **advisory proposal only**. It does **NOT** authorize pipeline execution, code modifications, database synchronization, network scraping, or candidate release generation. Each staged phase defined herein requires explicit human sign-off on a dedicated Specification-Driven Development (SDD) increment package (`spec.md`, `plan.md`, `tasks.md`, `verification.md`) before implementation may proceed.

---

## 1. Executive Summary & Strategic Context

The `mfp-bibliography` project establishes an auditable, reproducible, and versioned source-evidence foundation for multifunctional and moonlighting protein research. Following the formal documentary closure of Stage PIL-04.1B v0 (recorded in [`docs/reports/quickgo-pilot-pil-04.1b-descriptive-results.md`](../reports/quickgo-pilot-pil-04.1b-descriptive-results.md) at commit `f9d9fba58a5a03a949c346a5956b8795b312b24d`), the pilot system demonstrated that incorporating ontology-derived Gene Ontology (GO) aspect metadata expands concordance evaluability by $+30.56\text{ percentage points}$ (from $27.78\%$ to $58.33\%$) without perturbing previously evaluable scores or altering underlying raw source annotations.

However, the pilot architecture operates under rigid constraints: hardcoded cohort pairs, frozen input cardinalities ($72$ comparison rows, $353$ source annotations), and an analytical scope bounded to an eight-protein test slice.

This roadmap charts the rigorous, phased path required to transition from that purposive pilot to a scaled, verified evidence evaluation system spanning the three primary curated moonlighting protein databases in the catalog:
1. **MoonProt** ($702$ source records in release candidate `v0.3.0`, mapping to $657$ unique protein entities)
2. **MultitaskProtDB-II** ($694$ source records in release candidate `v0.3.0`, mapping to $685$ unique protein entities)
3. **PlantMP** ($112$ source records in release candidate `v0.3.0`, mapping to $110$ unique protein entities)

Across these three databases, the bounded dataset comprises exactly **$1,508$ source records**, representing **$1,452$ source-entity pairs** ($657 + 685 + 110$) and **$1,179$ unique protein entities** in the integrated multi-source union (canonical UniProtKB accessions resolved to deterministic `MFPB_PROTEIN_ID_V1` identifiers).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                STRATEGIC ORIENTATION                                   │
│                                                                                        │
│  PIL-04.1B v0 Baseline (Closed)           Extended Three-Source Validation (Proposed)  │
│  ──────────────────────────────           ───────────────────────────────────────────  │
│  • 8 Purposive Proteins                   • 1,508 Curated Source Records               │
│  • 12 Source–Accession Pairs              • 1,179 Unique Protein Entities (Union)      │
│  • 353 Annotation Rows                    • Multi-Source Overlaps & Union Preserved    │
│  • Hardcoded Pipeline Contract            • Parameterized Streaming / Batch Engine     │
│  • Source vs QuickGO Evaluation           • Source vs QuickGO + Source vs Source       │
│  • Bounded Pilot Feasibility              • Production-Grade Scientific Evidence Base  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Document Precedence, Authority & Invariants

All activities, task specifications, and technical workflows proposed in this roadmap must adhere strictly to the repository authority hierarchy ([`AGENTS.md`](../../AGENTS.md) §2):

1. **Level 1 — Accepted Architectural Decision Records (ADRs)**:
   - [ADR-001](../decisions/ADR-001-repository-scope.md): Repository scope strictly confined to source cataloging, identity resolution, provenance tracking, and evidence curation. Machine learning (ML), classification benchmarks, negative controls (NMF), and feature embeddings are strictly out of scope.
   - [ADR-002](../decisions/ADR-002-raw-data-immutability.md): Raw data files under `data/raw/` are immutable and append-only.
   - [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md): Entity identity resolution maps canonical UniProtKB accessions to deterministic `MFPB_PROTEIN_ID_V1` hashes.
   - [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md): Multi-source catalog packaging and offline cryptographic verification.
   - [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md): External bibliographic relations and GO enrichment are formally descoped from the catalog baseline. Citation matching does not equal functional corroboration.
2. **Level 2 — Repository Governance & Data Contracts**:
   - [`docs/project-charter.md`](../project-charter.md), [`docs/source-claims-contract.md`](../source-claims-contract.md).
3. **Level 5 — Approved Increment Specifications**:
   - `specs/<feature>/spec.md`, `plan.md`, `tasks.md`, `verification.md`.
4. **Level 6 — Advisory Drafts & Proposals**:
   - This document (`docs/roadmap/pilot-to-three-source-validation-roadmap.md`) belongs to Level 6. It provides advisory planning and requires human approval before spawning Level 5 specifications.

---

## 3. Baseline & Current State Technical Audit

An exhaustive read-only inspection of the codebase, schemas, tests, interim data artifacts, and execution scripts was conducted at commit `f9d9fba58a5a03a949c346a5956b8795b312b24d`. Every finding is classified according to empirical verification status:
- **`[VERIFIED]`**: Inspected directly in tracked or local repository code and data files.
- **`[REPORTED]`**: Stated in documentation, manifests, or past audit reports; not independently recalculated in this turn.
- **`[PROPOSED]`**: Architectural design, candidate remediation, or planned extension pending execution.

### 3.1 Pilot Engine & Runner Restrictions

1. **Hardcoded Cohort Specification in Library Code `[VERIFIED]`**:
   In [`src/mfp_bibliography/quickgo_concordance.py`](../../src/mfp_bibliography/quickgo_concordance.py#L28-L45), the constant `VERIFIED_COHORT_PAIRS` explicitly enumerates the $12$ (accession, source) pairs:
   ```python
   VERIFIED_COHORT_PAIRS: List[Tuple[str, str]] = [
       ("Q42525", "SRC_MOONPROT"),
       ("Q42525", "SRC_MULTITASKPROTDB_II"),
       ("Q42525", "SRC_PLANTMP"),
       ("Q9Y3E5", "SRC_MULTITASKPROTDB_II"),
       ("P0AFW0", "SRC_MOONPROT"),
       ("P0AFW0", "SRC_MULTITASKPROTDB_II"),
       ("P34788", "SRC_MULTITASKPROTDB_II"),
       ("P34788", "SRC_PLANTMP"),
       ("P78007", "SRC_MOONPROT"),
       ("P24228", "SRC_MOONPROT"),
       ("E6KMA1", "SRC_MOONPROT"),
       ("A0A0H3CDS3", "SRC_MULTITASKPROTDB_II"),
   ]
   ```
   Both `build_concordance_matrix` (line 404) and `build_reference_concordance` (line 781) fall back to this hardcoded list whenever the `pairs` argument is omitted.
2. **Production Runner Contract Invariants `[VERIFIED]`**:
   In [`scripts/build_quickgo_concordance_recomparison.py`](../../scripts/build_quickgo_concordance_recomparison.py#L40-L90), the pipeline execution is strictly bound to `PILOT_PRODUCTION_CONTRACT`:
   - `FROZEN_PILOT_ROW_COUNT = 353` (asserted on both `source_annotations` and `derived_aspects`).
   - `FROZEN_PILOT_UNIVERSE_COUNT = 72` (asserted on the resulting concordance matrix).
   - `FROZEN_PILOT_EXPECTED_DIGESTS`: Exactly 7 hardcoded SHA-256 digests verifying frozen input files.
   - `FROZEN_UPSTREAM_MANIFEST_DIGESTS`: Cryptographic digests of Stage P3 and Task PIL-04.1A manifests.
   *Architectural Implication*: The current script `build_quickgo_concordance_recomparison.py` cannot execute on any cohort other than the 8 pilot proteins without raising an assertion error. Scaling requires a parameterized, modular execution contract.
3. **Pipeline Data Dependencies `[VERIFIED]`**:
   Execution requires a strict linear dependency chain:
   $$\text{Raw Source Files} \xrightarrow{\text{Extraction}} \text{Source Claims/Annotations} \xrightarrow{\text{Ontology Enrichment}} \text{Derived Aspects} \xrightarrow{\text{QuickGO Capture}} \text{Concordance Matrix}$$
   - Identity: Resolved via `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv` (`a2e6cde1eebcb...`).
   - Ontology: Pinned to `releases/2026-01-23` (`go.obo`, digest `eee63704b5fe1c4...`).
4. **Primary Non-Evaluability Hierarchy & Reason Codes `[VERIFIED]`**:
   The concordance engine enforces a strict precedence ladder for assigning primary non-evaluable reasons when Jaccard similarity cannot be computed:
   1. `unresolved_biological_identity` (flagged in identity review; e.g. `P34788`)
   2. `missing_capture_record` (accession absent from QuickGO capture slice)
   3. `accession_unlinked_in_capture` (`protein_id IS NULL` in capture; e.g. `E6KMA1`)
   4. `source_aspect_indeterminate` (GO aspect missing or unmapped; e.g. MoonProt before PIL-04.1A)
   5. `source_record_outside_slice` (source record not captured in vertical slice; e.g. `A0A0H3CDS3`)
   6. `source_record_no_terms_aspect` (protein has source terms, but 0 in evaluated aspect; e.g. `P0AFW0` CC)
   7. `quickgo_no_terms_aspect` (QuickGO has annotations, but 0 in evaluated aspect)
   8. `zero_annotations_found` (0 total annotations found in database)

### 3.2 Test Suite Architecture & Coverage Boundaries

1. **Tier A Synthetic Unit Tests `[VERIFIED]`**:
   [`tests/test_quickgo_concordance_recomparison.py`](../../tests/test_quickgo_concordance_recomparison.py) contains 36 Tier A unit tests (`test_tier_a_*`). These tests operate on isolated, in-memory synthetic datasets, testing:
   - Annotation joins (cardinality mismatches, duplicate IDs, contradictory fields).
   - Ontology mapping cases (active terms, alt_ids, obsolete terms, unknown terms).
   - Transition matrix classifications (all 9 transition categories, relational arithmetic, floating-point tolerances).
   - Runner safety guards (staging cleanup on failure, collision prevention, input immutability).
   *Coverage Quality*: Tier A provides high structural code coverage for transition logic and schema validation without accessing local data files.
2. **Tier B Local Baseline Regression & Opt-In Gate `[VERIFIED]`**:
   The test suite includes exactly one Tier B regression test: `test_tier_b_local_baseline_regression` (lines 1714–1785).
   - Gate 3 Requirement: The test skips automatically unless `RUN_TIER_B_LOCAL_REGRESSION=1` is explicitly set in the execution environment.
   - Local Artifact Requirement: It skips if any of the 6 required interim artifacts under `data/interim/pilot/` are missing from disk.
   - Verification Scope: Compares recomputed output against Stage P3 baseline row-by-row, column-by-column, and asserts serialized byte SHA-256 equivalence.

### 3.3 Data Availability on Clean Clones vs Local Working Trees

1. **Git-Tracked Artifacts (Distributed with Fresh Clone) `[VERIFIED]`**:
   - Entire candidate release package: `releases/mfp-catalog-candidate-v0.3.0/` ($4.8\text{ MB}$, containing `mfp_source_records.csv`, `mfp_proteins.csv`, `mfp_assertions.csv`, `mfp_identifiers.csv`, `mfp_coverage.csv`, `MANIFEST.json`).
   - Tracked raw files: `data/raw/multitaskprotdb-ii/proteins.csv` ($1.3\text{ MB}$), `data/raw/plantmp/PlantMP_all.csv` ($53\text{ KB}$), `data/raw/plantmp/PlantMP MySQL-all-147.csv` ($74\text{ KB}$).
   - Schemas: `data/curated/quickgo_concordance.schema.json`, `quickgo_concordance_transition.schema.json`.
   - Source code and scripts: `src/mfp_bibliography/`, `scripts/`, `tests/`.
2. **Git-Ignored Artifacts (Local Only, Absent from Fresh Clone) `[VERIFIED]`**:
   Per `.gitignore` and [`data/raw/README.md`](../../data/raw/README.md):
   - `data/raw/moonprot/mpid_*.html` ($702$ individual raw HTML files) and `data/raw/moonprot/artifact_index.csv`.
   - All directories under `data/interim/` (including `data/interim/pilot/quickgo_slice/`, `data/interim/pilot/source_go_annotations_pilot.csv`, `derived_source_go_aspects_pilot.csv`).
   - All directories under `data/processed/`.
   *Critical Finding*: An automated build or CI run on a fresh clone cannot run Tier B tests or re-execute the pilot without external provisioning of the frozen interim inputs and MoonProt raw HTML artifacts.

### 3.4 Historical Lineage & Execution Disentanglement

To ensure scientific rigor, four distinct execution milestones must never be conflated:

| Milestone / Run | Scope & Nature | Inputs / Commits | Evaluability | Status & Authority |
|---|---|---|---|---|
| **Historical P3 / P4** | Original 8-protein pilot baseline against QuickGO slice | Unassigned MoonProt aspects; 12 pairs; 72 rows | $20/72$ ($27.78\%$) evaluable; $52/72$ ($72.22\%$) non-evaluable | Frozen historical baseline; documented in `quickgo-pilot-p4-descriptive-analysis-report.md` |
| **Stage PIL-04.1A** | Ontology aspect enrichment of 353 pilot annotations | Pinned `go.obo` (`releases/2026-01-23`); commits `98530b3` & `421da7e` | Enriched 353 annotation rows; MoonProt aspects resolved | Completed offline; retrospective spec amendment pending in working tree |
| **Stage PIL-04.1B v0** | First recomparison execution & transition analysis | Baseline P3 + PIL-04.1A; output staged in `quickgo_slice_recomparison` | $42/72$ ($58.33\%$) evaluable; $30/72$ ($41.67\%$) non-evaluable ($+30.56\text{ pp}$) | **Formally Approved Baseline** for Gate 4 closure (Commit `f9d9fba58a5a03a...`) |
| **Stage PIL-04.1B v1** | Detached worktree reproduction audit | Pinned commit `41521ba`; output in `quickgo_slice_recomparison_v1` | Identical marginals ($42/72$ vs $30/72$) | **Preserved technical reproduction**, pending formal acceptance; does NOT supersede baseline v0 |

---

## 4. Scope Definition & Universe Reconciliation

A frequent ambiguity in multi-database bioinformatics is what it means to "cross" or "integrate" datasets. In `mfp-bibliography`, this concept encompasses **three distinct mathematical and biological operations** that must be maintained separately:

```
                            THREE INTEGRATION CONCEPTS
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
  [1. INTEGRATED UNION]        [2. ENTITY OVERLAPS]         [3. CONCORDANCE]
  Full outer join retaining    Structural intersection      Evaluates functional /
  all 1,179 entities &         between source accessions:   bibliographic agreement:
  1,508 source records with    • M ∩ T = 237 (inclusive)    • Source vs QuickGO
  provenance attribution.      • M ∩ P = 9   (inclusive)    • Source vs Source
  (DO NOT COLLAPSE)            • T ∩ P = 31  (inclusive)    (Jaccard & Citations)
                               • M ∩ T ∩ P = 4 (DO NOT CUT)
```

### 4.1 Concept 1: The Integrated Union with Record-Level Provenance

The primary mission of `mfp-bibliography` is to construct an exhaustive, transparent inventory of all published multifunctional protein claims, retaining complete source-level attribution per record.

#### Exact Evidence, Paths & Keys
The numbers below were computed directly from candidate release `v0.3.0` via a lightweight read-only inspection:
- **Inspected Artifact**: [`releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv`](../../releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv) ($2.3\text{ MB}$, SHA-256 `89daf82e254c0294...`).
- **Source Filtering Key**: Column `source_name` filtered by `SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, and `SRC_PLANTMP`.
- **Entity Resolution Keys**: Column `protein_id` (deterministic `MFPB_PROTEIN_ID_V1` hash per [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)) and column `uniprot_id` (canonical UniProtKB accession).
- **Field Population vs Biological Identity**: In this candidate release slice (`v0.3.0`), 100% of rows have populated `protein_id` and `uniprot_id` fields (0 null values observed). However, structural field population must be strictly distinguished from mapping consistency (relational integrity between tables and accessions) and validated biological identity (taxonomic, sequence, and functional correctness). The absence of null values indicates structural field population in the candidate release table, NOT that biological identity is validated.

#### Reconciling Record Cardinalities and Entity Cardinalities
A crucial distinction must be drawn between **source records** (rows documenting curated claims) and **unique protein entities** (distinct biological macromolecules):

$$\begin{aligned}
\text{Total 3-Source Records} &= 702\text{ (MoonProt)} + 694\text{ (Multitask)} + 112\text{ (PlantMP)} = 1,508\text{ source records} \\
\text{Sum of Unique Entities per Source} &= 657\text{ (MoonProt)} + 685\text{ (Multitask)} + 110\text{ (PlantMP)} = 1,452\text{ source-entity pairs} \\
\text{Internal Record Multiplicity Surplus} &= (702 - 657) + (694 - 685) + (112 - 110) = 45 + 9 + 2 = 56\text{ surplus records}
\end{aligned}$$

- **MoonProt (`SRC_MOONPROT`)**: $702$ records map to $657$ unique protein entities ($45$ surplus records representing internal multiplicity pending classification).
- **MultitaskProtDB-II (`SRC_MULTITASKPROTDB_II`)**: $694$ records map to $685$ unique protein entities ($9$ surplus records representing internal multiplicity pending classification).
- **PlantMP (`SRC_PLANTMP`)**: $112$ records map to $110$ unique protein entities ($2$ surplus records representing internal multiplicity pending classification).
- **Characterization of Multiplicity**: These 56 surplus records represent internal record multiplicity pending classification (e.g. multi-curation entries, distinct functional role blocks, or alternative isoforms across MPIDs/rows within the same database), not erroneous duplicates.
- **Invariant**: The catalog union must **never discard source records** that exist in only one database. A protein documented solely in MoonProt ($415$ unique entities) or solely in MultitaskProtDB-II ($421$ unique entities) remains fully preserved in the catalog union.

### 4.2 Concept 2: Structural Entity Overlaps Across Databases

Entity overlap quantifies the extent to which independent curation efforts captured the same biological macromolecules:

$$\begin{aligned}
|M| &= 657 \text{ unique protein entities in MoonProt} \\
|T| &= 685 \text{ unique protein entities in MultitaskProtDB-II} \\
|P| &= 110 \text{ unique protein entities in PlantMP}
\end{aligned}$$

#### Standard Pairwise Intersections (Inclusive of the Triple Intersection)
In standard mathematical set notation, pairwise intersections **include** the elements present in the triple intersection:
- $|M \cap T| = 237$ protein entities share curation between MoonProt and MultitaskProtDB-II (inclusive of the $4$ triple-intersection entities).
- $|M \cap P| = 9$ protein entities share curation between MoonProt and PlantMP (inclusive of the $4$ triple-intersection entities).
- $|T \cap P| = 31$ protein entities share curation between MultitaskProtDB-II and PlantMP (inclusive of the $4$ triple-intersection entities).
- $|M \cap T \cap P| = 4$ protein entities belong to all three databases (`Q42525`, `Q75NZ0`, `Q9ZVD5`, `Q9ZVR7`).

#### Mutually Disjoint Venn Partitions (Exclusive Components)
To understand database uniqueness without double-counting, the 3-source universe partitions into seven mutually exclusive subsets:
1. **Present only in MoonProt (absent from MultitaskProtDB-II and PlantMP)**: $|M \setminus (T \cup P)| = 657 - 233 - 5 - 4 = 415$ protein entities.
2. **Present only in MultitaskProtDB-II (absent from MoonProt and PlantMP)**: $|T \setminus (M \cup P)| = 685 - 233 - 27 - 4 = 421$ protein entities.
3. **Present only in PlantMP (absent from MoonProt and MultitaskProtDB-II)**: $|P \setminus (M \cup T)| = 110 - 5 - 27 - 4 = 74$ protein entities.
4. **Present in MoonProt and MultitaskProtDB-II only (absent from PlantMP)**: $|(M \cap T) \setminus P| = 237 - 4 = 233$ protein entities.
5. **Present in MoonProt and PlantMP only (absent from MultitaskProtDB-II)**: $|(M \cap P) \setminus T| = 9 - 4 = 5$ protein entities.
6. **Present in MultitaskProtDB-II and PlantMP only (absent from MoonProt)**: $|(T \cap P) \setminus M| = 31 - 4 = 27$ protein entities.
7. **Present in all three databases (Triple Intersection)**: $|M \cap T \cap P| = 4$ protein entities.

#### Rigorous Summation to the Integrated Union
Summing the seven disjoint partitions proves the total number of unique protein entities:
$$415 + 421 + 74 + 233 + 5 + 27 + 4 = 1,179 \text{ unique protein entities}$$
Equivalently, applying the formal Inclusion-Exclusion Principle across the inclusive sets confirms the exact same total:
$$\begin{aligned}
|M \cup T \cup P| &= |M| + |T| + |P| - |M \cap T| - |M \cap P| - |T \cap P| + |M \cap T \cap P| \\
&= 657 + 685 + 110 - 237 - 9 - 31 + 4 \\
&= 1,452 - 277 + 4 = 1,179 \text{ unique protein entities}
\end{aligned}$$

#### Clarification of the "99.66%" Loss Metric Across Denominators

> [!CAUTION]
> **Catastrophic Risk of Restricting Analysis to the Triple Intersection**:
> If the scaled validation pipeline were naively configured to evaluate only proteins present across *all three* databases ($M \cap T \cap P$), the cohort would **collapse to exactly 4 proteins** (`Q42525`, `Q75NZ0`, `Q9ZVD5`, `Q9ZVR7`). The exact impact depends strictly on the level of abstraction and denominator chosen:
> 1. **Unique Integrated Protein Entities**:
>    - Denominator: $|M \cup T \cup P| = 1,179$ unique protein entities.
>    - Retained in triple intersection: $4$ entities ($0.34\%$).
>    - Discarded / unrepresented: $1,179 - 4 = 1,175$ entities.
>    - Loss proportion: $100 \times (1,175 / 1,179) \approx \mathbf{99.66\%}$ of unique protein entities.
> 2. **Source–Entity Pairs**:
>    - Denominator: Total source-entity pairs across the three databases = $1,452$ pairs.
>    - Retained in triple intersection: Exactly $12$ pairs ($4\text{ entities} \times 3\text{ sources}$).
>    - Discarded / unrepresented: $1,452 - 12 = 1,440$ pairs.
>    - Loss proportion: $100 \times (1,440 / 1,452) \approx \mathbf{99.17\%}$ of source-entity pairs.
> 3. **Source Records**:
>    - Denominator: Total source records across the three databases = $1,508$ records.
>    - Retained in triple intersection: Exactly $12$ records across candidate release `v0.3.0` correspond to those 4 proteins ($3$ records per protein: 1 in MoonProt, 1 in Multitask, 1 in PlantMP, with zero internal multiplicity observed for these 4 accessions).
>    - Discarded / unrepresented: $1,508 - 12 = 1,496$ records.
>    - Loss proportion: $100 \times (1,496 / 1,508) \approx \mathbf{99.20\%}$ of source records.
> 4. **Functional Annotations & Claims**:
>    - Full annotation extraction across all 1,508 records is scheduled for Phase B (`TASK-EXT-04`). Any percentage loss of annotations is currently **pending measurement** and must not be assumed equal to entity counts.

The system architecture must therefore preserve the full integrated union ($1,179$ entities across $1,508$ records) and evaluate pairwise and individual evidence sets while tracking membership in the integrated union.

### 4.3 Concept 3: Functional & Bibliographic Concordance

Concordance measures semantic and evidentiary agreement. This must be decoupled into two distinct comparative tracks:

1. **Source vs QuickGO Concordance (External Reference Track)**:
   - Evaluates whether independent database curators annotate the same GO terms and literature citations as the canonical UniProt-GOA / QuickGO repository (`MFP_QuickV1`).
   - Extended from PIL-04.1B: Computes Jaccard similarity across Molecular Function (MF), Biological Process (BP), and Cellular Component (CC) under Policies B and C.
2. **Source vs Source Concordance (Cross-Curator Consensus Track)**:
   - Directly compares assertions, GO annotations, and cited PMIDs between MoonProt, MultitaskProtDB-II, and PlantMP for shared protein entities (e.g. comparing MoonProt vs Multitask for the $237$ overlapping proteins) **without requiring QuickGO as an intermediary**.
   - Evaluates whether different curation teams independently reached the same functional conclusions from primary literature.

### 4.4 Demarcation from Downstream Machine Learning (PEC)

Per [ADR-001](../decisions/ADR-001-repository-scope.md), `mfp-bibliography` is strictly an evidence, identity, and provenance repository.
- **Out of Scope**: Training classifiers, engineering feature vectors, generating sequence or graph embeddings, constructing synthetic benchmark splits, or defining "Non-Multifunctional Proteins" (NMF).
- **BioData Invariant**: Uncharacterized reference proteins from UniProtKB/Swiss-Prot constitute a **contextual reference population**, NEVER a verified negative class.

---

## 5. Dataset Preparation & Ingestion Inventory

An inventory of raw data assets, extraction modules, identifier hygiene, and metadata completeness across the three target databases was compiled from repository manifests and local files:

| Source Attribute | MoonProt | MultitaskProtDB-II | PlantMP |
|---|---|---|---|
| **Snapshot / Version** | 2026-09-22 web crawl snapshot | Database dump snapshot (2026-09-22) | Database dump snapshot (2026-09-22) |
| **Raw Repository Path** | `data/raw/moonprot/` | `data/raw/multitaskprotdb-ii/proteins.csv` | `data/raw/plantmp/PlantMP_all.csv` |
| **Raw Data Tracking in Git** | **Untracked / Ignored** ($702$ HTML files) | **Tracked in Git** ($1.3\text{ MB}$, SHA-256 in manifest) | **Tracked in Git** ($53\text{ KB}$, SHA-256 in manifest) |
| **Catalog Candidate Records** | $702$ records (`releases/.../v0.3.0`) | $694$ records (`releases/.../v0.3.0`) | $112$ records (`releases/.../v0.3.0`) |
| **Unique UniProt Accessions** | $657$ accessions | $685$ accessions | $110$ accessions |
| **Internal Record Multiplicity** | $45$ surplus records ($702 - 657$) | $9$ surplus records ($694 - 685$) | $2$ surplus records ($112 - 110$) |
| **Identifier Ambiguity** | Accessions parsed from HTML tables | Clean UniProt column (UTF-8 BOM present) | Header misspelled as `uniport_id` |
| **Taxonomy & Sequence** | Organism string present; taxid unmapped | Organism string present; taxid unmapped | Plant species text present; orders recorded |
| **GO Terms Availability** | Extracted in raw text; **aspect omitted** | Extracted in `GO` & `GO_Moon` with aspect | Split by `canonical` and `moonlighting` |
| **Ontology Resolution Need** | **Mandatory** (requires `go_aspect_enrichment`) | Minor (some alt_ids / obsolete terms) | Minor (some alt_ids / obsolete terms) |
| **Bibliographic Identifiers** | PMIDs in HTML references; some anomalies | PMIDs in `Reference` column | PMIDs in `pubmed_id` column |
| **Known Extraction Bugs** | `P24228` unclosed quote in `mpid_288.html` | None reported in pilot slice | Identity review open on `P34788` |
| **Distribution Restrictions** | MoonProt crawl subject to acquisition policy | Public academic dataset | Public academic dataset |

> [!NOTE]
> **Pending Measurements**:
> Precise counts of active GO terms, obsolete terms, secondary `alt_id` occurrences, and non-resolving CURIEs across the full $1,508$-record universe have not been compiled to avoid unauthorized full-pipeline runs. Compiling these metrics is formally scheduled as Task `TASK-EXT-04` in Phase B and detailed in [`specs/three-source-inventory-audit/spec.md`](../../specs/three-source-inventory-audit/spec.md).

---

## 6. Phased Implementation Plan

Scaling from the 8-protein pilot to the 1,508-record three-source system is structured into seven sequential phases (Phases A through G). Each phase is governed by entry prerequisites, acceptance criteria, explicit stop criteria, and assigned technical roles.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               PHASED EXECUTION PIPELINE                                │
│                                                                                        │
│  [Phase A: Preservation & Baseline Hygiene]      ──► Baseline reproducibility secured  │
│                           │                                                            │
│  [Phase B: 3-Source Coverage & Identity Audit]   ──► Complete 1,508-record inventory   │
│                           │                                                            │
│  [Phase C: Engine Generalization & Batching]     ──► Scalable parameterized runner     │
│                           │                                                            │
│  [Phase D: Expanded Stratified Pilot]            ──► Validation on challenge cohort    │
│                           │                                                            │
│  [Phase E: Independent Quality & Science Audit]  ──► Peer review of discrepancies      │
│                           │                                                            │
│  [Phase F: Volume, Performance & Benchmarks]     ──► Resource profiling at scale       │
│                           │                                                            │
│  [Phase G: Controlled Production & Packaging]    ──► Release candidate v0.4.0-evidence │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase A: Preservation & Baseline Hygiene

- **Objective & Core Question**: How do we ensure that the completed, approved PIL-04.1B v0 baseline remains 100% reproducible and protected from regressions as the codebase evolves?
- **Starting Evidence**: Closed descriptive report [`docs/reports/quickgo-pilot-pil-04.1b-descriptive-results.md`](../reports/quickgo-pilot-pil-04.1b-descriptive-results.md) (`f9d9fba58a...`), preservation package `pkg-quickgo-p1-p4-20261116-v1`.
- **Preconditions**: Empty index on `feature/functional-normalization`, HEAD at `f9d9fba58a...`.
- **Responsible Roles**: Data Quality & Curation Specialist, Software Architect.

#### Task Breakdown
- **`TASK-EXT-01`**: Author formal preservation certification report documenting local preservation bundle checksums (`f02c6f47...`) and offsite archive location (resolving Criterion C of [`docs/reports/quickgo-pilot-preservation-record.md`](../reports/quickgo-pilot-preservation-record.md)).
- **`TASK-EXT-02`**: Stage and commit pending documentary amendment to [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md) in a dedicated, isolated commit. *(Note: This is repository documentary maintenance; it is NOT a computational or technical dependency for authoring Phase B specifications).*
- **`TASK-EXT-03`**: Establish a non-destructive regression fixture directory containing the 8-protein pilot inputs to allow offline Tier B regression tests to run on any environment.

- **Acceptance Criteria**: Working tree clean; preservation package verified offline; Tier B tests executable without relying on uncommitted disk artifacts.
- **Stop Criteria**: If Tier B regression fails to match the frozen Stage P3 baseline SHA-256 digests byte-for-byte, stop immediately.
- **Effort & Uncertainty**: Low effort (1–2 days); very low uncertainty.

---

### Phase B: Comprehensive Coverage & Biological Identity Audit of 3 Sources

- **Objective & Core Question**: What is the exact biological identity, taxonomic concordance, and GO annotation availability across all 1,508 records in MoonProt, MultitaskProtDB-II, and PlantMP?
- **Starting Evidence**: `releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv`, raw CSVs for Multitask and PlantMP, local MoonProt HTML artifacts.
- **Responsible Roles**: Scientific Bioinformatics Auditor, Data Quality Specialist.

#### Task Breakdown
- **`TASK-EXT-04`**: Author specification package [`specs/three-source-inventory-audit/spec.md`](../../specs/three-source-inventory-audit/spec.md) defining schemas and accounting criteria for the 1,508 source records.
- **`TASK-EXT-05`**: Implement read-only audit script to extract and tabulate all cited UniProt accessions, check UniProtKB status, flag secondary/merged accessions, and compute taxon IDs.
- **`TASK-EXT-06`**: Perform formal curatorial review and adjudication of identity anomalies (e.g. evaluating conflicting evidence on `P34788` plant source attributions between historical notes citing Spinach and raw source text citing *Arabidopsis thaliana*).
- **`TASK-EXT-07`**: Compile full GO inventory across all 1,508 records: classify active terms, obsolete terms, alt_ids, and map aspects via `go.obo` (`releases/2026-01-23`).

- **Acceptance Criteria**: Audit report published documenting 100% of the 1,508 records; zero ambiguous UniProt accessions unclassified; explicit quarantine list established for non-resolving entities.
- **Stop Criteria & Indicative Quarantine Thresholds (Proposed)**:
  > [!TIP]
  > **Policy Proposal Pending Human Decision**: If the proportion of unresolvable or corrupted identifiers exceeds an indicative threshold (proposed tentatively at $>5\%$ of records, subject to formal PI sign-off), Phase B audit execution shall pause for curatorial review rather than proceeding automatically to engine generalization.
- **Effort & Uncertainty**: Moderate effort (1–2 weeks); low uncertainty on data parsing, moderate uncertainty on curatorial taxonomy resolution.

---

### Phase C: Generalization of Concordance Engine & Contract Modularization

- **Objective & Core Question**: How do we refactor the concordance evaluation runner from hardcoded pilot constants into a streaming, batch-capable engine while preserving frozen pilot contracts?
- **Starting Evidence**: [`src/mfp_bibliography/quickgo_concordance.py`](../../src/mfp_bibliography/quickgo_concordance.py), [`scripts/build_quickgo_concordance_recomparison.py`](../../scripts/build_quickgo_concordance_recomparison.py).
- **Responsible Roles**: Pipeline & Software Architect, Senior Software Engineer.

#### Task Breakdown
- **`TASK-EXT-08`**: Author SDD package `specs/concordance-engine-generalization/` (`spec.md`, `plan.md`, `tasks.md`).
- **`TASK-EXT-09`**: Refactor `quickgo_concordance.py` to decouple `VERIFIED_COHORT_PAIRS` into configurable cohort providers; ensure default behavior remains unchanged for pilot tests.
- **`TASK-EXT-10`**: Generalize `PilotInputContract` in `build_quickgo_concordance_recomparison.py` into `ConcordanceExecutionContract`, supporting dynamic cohort sizes, custom input manifests, and streaming chunk validators.
- **`TASK-EXT-11`**: Implement memory-bounded generator processing to ensure concordance matrices with $>10,000$ evaluation rows execute within $<1\text{ GB}$ RSS memory.

- **Acceptance Criteria**: 100% of Tier A unit tests pass; pilot runner passes bit-for-bit regression when supplied with `PILOT_PRODUCTION_CONTRACT`; engine processes arbitrary (accession, source) lists without code edits.
- **Stop Criteria**: If refactored engine alters any pilot output byte, halt and revert refactoring.
- **Effort & Uncertainty**: Moderate effort (1 week); low uncertainty.

---

### Phase D: Expanded Bounded Pilot on Stratified Representative Sample

- **Objective & Core Question**: How does the generalized engine behave when evaluated against complex edge cases and a statistically representative cross-section of the 3 databases?
- **Starting Evidence**: Audit report from Phase B, generalized engine from Phase C.
- **Responsible Roles**: Scientific Bioinformatics Auditor, Software Architect.

#### Task Breakdown
- **`TASK-EXT-12`**: Author SDD package `specs/expanded-concordance-pilot/` defining sampling stratification rules and cohort composition.
- **`TASK-EXT-13`**: Assemble Cohort 1 (Technical Stress Cases: `P24228` parser repair, `P34788` curatorial review outcome, `E6KMA1` unlinked capture, multi-isoform entries).
- **`TASK-EXT-14`**: Assemble Cohort 2 (Stratified Sample: $50$ proteins selected across taxa, GO term densities, and cross-source overlap depth).
- **`TASK-EXT-15`**: Execute offline concordance evaluation for Cohorts 1 and 2 against external QuickGO data and cross-source claims; produce transition and concordance matrices.

- **Acceptance Criteria**: 100% of evaluated rows accounted for; primary non-evaluability reasons assigned deterministically; zero unhandled parser crashes.
- **Stop Criteria**: If unexpected unhandled exception occurs during evaluation, stop and quarantine the offending record.
- **Effort & Uncertainty**: Moderate effort (1–2 weeks); moderate uncertainty regarding edge-case parsing behaviors.

---

### Phase E: Independent Scientific & Technical Quality Audit

- **Objective & Core Question**: Are the concordance scores, primary reason transitions, and bibliographic alignments biologically sound and free from systemic bias?
- **Starting Evidence**: Evaluation matrices from Phase D.
- **Responsible Roles**: Lead Maintainer / PI, Scientific Bioinformatics Auditor (Independent Reviewer).

#### Task Breakdown
- **`TASK-EXT-16`**: Author independent scientific review memorandum evaluating observed Jaccard distributions across biological functions (enzymes vs structural vs regulatory proteins).
- **`TASK-EXT-17`**: Audit bibliographic concordance: verify citation overlap vs literature divergence (e.g. assessing whether low Jaccard scores reflect complementary literature rather than conflicting claims per [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)).
- **`TASK-EXT-18`**: Review quarantined records and formulate final curatorial recommendations.

- **Acceptance Criteria**: Formal audit memo signed off by scientific lead; all discrepancy investigations documented with transparent rationales.
- **Stop Criteria**: If audit identifies systematic misclassification in the primary reason hierarchy, halt pipeline scaling.
- **Effort & Uncertainty**: Moderate effort (1 week); low technical uncertainty.

---

### Phase F: Volume, Batching, Recovery, and Performance Benchmarks

- **Objective & Core Question**: What are the empirical runtime, memory, and disk requirements to execute all $1,508$ source records, and does batched execution produce results identical to a single run?
- **Starting Evidence**: Generalized engine from Phase C, full dataset inventory from Phase B.
- **Responsible Roles**: Pipeline & Software Architect, DevOps/Infrastructure Engineer.

#### Task Breakdown
- **`TASK-EXT-19`**: Author benchmarking protocol `docs/benchmarks/three-source-scale-protocol.md`.
- **`TASK-EXT-20`**: Execute volume and batching benchmark: partition $1,508$ records into batches of $100$, $250$, and $500$ records; compare concatenated output against monolithic run to assert mathematical equivalence.
- **`TASK-EXT-21`**: Profile memory high-water mark, CPU core utilization, and disk I/O throughput; document resource envelope.

- **Acceptance Criteria**: Batched execution verified byte-for-byte identical to monolithic run; total execution time $<30\text{ minutes}$ on standard workstation; peak RSS memory $<2\text{ GB}$.
- **Stop Criteria**: If batch partitioning produces numerical or sorting divergence against monolithic output, halt.
- **Effort & Uncertainty**: Low effort (3–5 days); low uncertainty.

---

### Phase G: Controlled Full-Scale Production Execution & Candidate Release

- **Objective & Core Question**: How do we package and publish the final verified multi-source concordance evidence dataset as an immutable candidate release?
- **Starting Evidence**: All acceptance criteria from Phases A through F satisfied.
- **Responsible Roles**: Lead Maintainer / PI, Software Architect.

#### Task Breakdown
- **`TASK-EXT-22`**: Author release specification `specs/release-v0.4.0-evidence/spec.md`.
- **`TASK-EXT-23`**: Execute offline full-scale production run across all $1,508$ source records and $1,179$ protein entities.
- **`TASK-EXT-24`**: Generate cryptographic manifests, SHA-256 checksums, and dataset dictionary.
- **`TASK-EXT-25`**: Package immutable candidate release `releases/mfp-evidence-candidate-v0.4.0/` under [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md).

- **Acceptance Criteria**: Candidate release packaged with 100% offline verification; zero unverified warnings; formal human sign-off recorded.
- **Stop Criteria**: Any schema validation failure or checksum mismatch immediately aborts release packaging.
- **Effort & Uncertainty**: Moderate effort (1 week); low uncertainty once Phase F passes.

---

## 7. Pre-Scale Validation Design

Before executing full-scale production across $1,508$ records, validation must be conducted on two complementary cohorts:

```
                            PRE-SCALE VALIDATION COHORTS
                                        │
         ┌──────────────────────────────┴──────────────────────────────┐
         ▼                                                             ▼
  [COHORT 1: TECHNICAL STRESS CASES]            [COHORT 2: STRATIFIED SAMPLE]
  Targeted validation on known edge cases:      Representative sampling across
  • Markup syntax errors (P24228)               3 strata to estimate baseline
  • Taxonomic identity review (P34788)          system performance:
  • Unlinked capture missingness (E6KMA1)       • Taxon (Bacteria, Plant, Metazoa)
  • Slice boundary controls (A0A0H3CDS3)        • GO Density (Low, Moderate, Rich)
  • Multi-isoform / alternative splicing        • Overlap Depth (1, 2, or 3 sources)
```

### 7.1 Stratified Sampling Methodology

To avoid bias, Cohort 2 must not be cherry-picked based on high Jaccard scores or complete GO annotations. Stratification operates across three orthogonal axes:

1. **Taxonomic Stratum**:
   - Bacteria ($~40\%$ of sample)
   - Metazoa / Human ($~35\%$ of sample)
   - Viridiplantae / Plants ($~25\%$ of sample, ensuring adequate PlantMP coverage)
2. **GO Annotation Density Stratum**:
   - Sparse ($1$–$2$ GO terms per protein)
   - Moderate ($3$–$8$ GO terms per protein)
   - Rich ($>8$ GO terms per protein)
3. **Database Overlap Stratum**:
   - Single-source unique ($1$ source only: MoonProt-only, Multitask-only, PlantMP-only)
   - Two-source shared ($2$ sources: MoonProt + Multitask, Multitask + PlantMP, MoonProt + PlantMP)
   - Three-source shared (All $4$ proteins in the triple intersection: `Q42525`, `Q75NZ0`, `Q9ZVD5`, `Q9ZVR7`)

### 7.2 Six-Dimension Readiness Matrix

A candidate execution is declared ready for production scaling only when all six quality dimensions meet mandatory criteria:

| Dimension | Mandatory Integrity Criteria (Hard Stop) | Scientific Evaluation Criteria (Lead Sign-Off) |
|---|---|---|
| **1. Entity Identity** | 100% of rows have valid `MFPB_PROTEIN_ID_V1` hash; zero unmapped UniProt IDs without explicit quarantine status. | Verification of taxonomic assignments and handling of obsolete/merged accessions. |
| **2. Extraction Correctness** | 100% raw-source text fidelity; parser executes with zero unhandled exceptions; trailing delimiters handled. | Verification of multi-role claim segmentation (canonical vs moonlighting). |
| **3. Ontological Resolution** | All GO CURIEs match `go.obo` release `releases/2026-01-23`; zero aspect assignments synthesized by heuristic guessing. | Assessment of obsolete term mappings and secondary identifier redirects. |
| **4. Coverage Accounting** | Complete denominator reconciliation: $N_{\text{evaluable}} + N_{\text{non-evaluable}} = N_{\text{total}}$; zero dropped rows. | Evaluation of primary non-evaluability distribution across source databases. |
| **5. Concordance Integrity** | $J \in [0.0000, 1.0000]$ or null with primary reason; set operations mathematically exact ($U = A \cup B$, $I = A \cap B$). | Scientific interpretation of low concordance cases (literature gap vs annotation divergence). |
| **6. Reproducibility & Scaling** | 100% deterministic bit-for-bit output across repeated runs; memory bounded $<2\text{ GB}$; batch equivalence verified. | Acceptability of total runtime and resource footprint for CI/CD environments. |

---

## 8. Incident, Discrepancy & Continuity Register

To preserve institutional knowledge and prevent historical mistakes from resurfacing, seven key technical incidents and continuity constraints are formally registered with their current empirical status:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CONTINUITY & INCIDENT REGISTER STATUS                           │
│                                                                                        │
│  1. P24228 MoonProt Parser Markup Bug   ──► Diagnosed in HTML; candidate task PIL-04.2 │
│  2. P34788 Taxonomic Identity Review    ──► Identity review open; pending adjudication │
│  3. E6KMA1 Unlinked Capture Precedence  ──► Engine precedence verified; barrier exposed│
│  4. A0A0H3CDS3 Slice Boundary Control   ──► Negative control boundary confirmed        │
│  5. Descoping Bibliographic Relations   ──► ADR-007 enforced; no artificial promotion │
│  6. Reproduction v1 Acceptance Status   ──► Preserved; pending formal acceptance       │
│  7. PIL-04.1A Pending Spec Amendment    ──► Retrospective text pending in working tree │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Incident 1: MoonProt HTML Parser Markup Anomaly (`P24228`)
- **Historical Symptom**: In Stage P4 reference concordance, `P24228` was flagged as non-evaluable due to `source_extraction_incomplete`.
- **Root Cause Audit `[VERIFIED]`**: Local raw HTML file `data/raw/moonprot/mpid_288.html` is present on disk. Extraction failed due to malformed HTML markup in the PDB cross-reference table (`href="...2EXB>` missing a closing double quotation mark), which truncated subsequent bibliographic parsing.
- **Current Status**: Raw file is intact. The parser repair is formally designated as candidate task `PIL-04.2` and scheduled under Phase D (`TASK-EXT-13`). In the interim baseline, historical P3/P4 results remain gated as observed.

### 8.2 Incident 2: Biological Identity Review (`P34788`)
- **Historical Symptom**: In Stage P4, comparisons involving `P34788` were gated by `unresolved_biological_identity` based on an early query note suggesting a taxonomic conflict involving Spinach (*Spinacia oleracea*).
- **Audit Findings `[VERIFIED]`**: Inspection of raw source tables (`data/raw/plantmp/PlantMP_all.csv` Order 1 and `data/raw/multitaskprotdb-ii/proteins.csv` row 337) shows that both tables cite *Arabidopsis thaliana* for UniProt accession `P34788`.
- **Current Status**: This discrepancy constitutes an **open biological identity review pending formal curatorial adjudication** (`TASK-EXT-06`). The species assignment and biological identity must not be pre-judged or predetermined by this roadmap; historical P3/P4 results remain gated until an authorized curatorial review signs off on the resolution.

### 8.3 Incident 3: Unlinked QuickGO Capture & Precedence (`E6KMA1`)
- **Historical Symptom**: Shifted from `source_aspect_indeterminate` in Stage P3 to `accession_unlinked_in_capture` in PIL-04.1B v0.
- **Root Cause Audit `[VERIFIED]`**: In the QuickGO raw capture slice, `E6KMA1` is present but has `protein_id IS NULL` (accession not linked in the target database capture). Resolving source term aspects in PIL-04.1A cleared the higher-priority aspect indeterminacy barrier and exposed the underlying capture linkage barrier according to engine precedence.
- **Current Status**: Fully verified and documented in [`docs/reports/quickgo-pilot-pil-04.1b-descriptive-results.md`](../reports/quickgo-pilot-pil-04.1b-descriptive-results.md). Serves as a reference behavior test for engine diagnostic precedence.

### 8.4 Incident 4: Slice Boundary Control (`A0A0H3CDS3`)
- **Historical Symptom**: All 6 comparison rows for `A0A0H3CDS3` / MultitaskProtDB-II evaluated to `source_record_outside_slice`.
- **Root Cause Audit `[VERIFIED]`**: `A0A0H3CDS3` was deliberately included in the pilot cohort as a boundary control. QuickGO contained zero annotations for this accession in the captured vertical slice.
- **Current Status**: Verified expected behavior. Demonstrates that the engine properly assigns `source_record_outside_slice` rather than synthesizing an artificial zero Jaccard score.

### 8.5 Incident 5: Decoupling of Claim-to-Publication Relations (ADR-007)
- **Governance Mandate**: [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) explicitly descopes external bibliographic relations and GO enrichment from the catalog baseline.
- **Scientific Implication**: Databases record citations at the record level, not at the individual functional claim level. The concordance engine must never promote record-level literature citations to claim-specific support without explicit experimental evidence. Citation concordance and functional concordance are independent metrics.

### 8.6 Incident 6: Acceptance Status of Reproduction Run v1
- **Execution Event**: An independent technical reproduction (v1) was executed on 2026-11-19 in detached worktree `mfp-bibliography-gate3` writing to `data/interim/pilot/quickgo_slice_recomparison_v1`.
- **Audit Finding `[VERIFIED]`**: The v1 execution ran cleanly and reproduced the exact marginal counts ($42/72$ evaluable, $30/72$ non-evaluable) and SHA-256 output digests.
- **Governance Status `[VERIFIED]`**: The v1 reproduction is **preserved locally on disk, pending formal human acceptance**; it **does NOT supersede the historical reference v0** (Commit `f9d9fba58a5a03a949c346a5956b8795b312b24d`), which remains the sole formally approved baseline for Gate 4 documentary closure.

### 8.7 Incident 7: Pending Documentary Amendment of PIL-04.1A
- **Status in Working Tree `[VERIFIED]`**: [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md) contains unstaged modifications documenting the retrospective execution of Task PIL-04.1A on 2026-11-16 (commits `98530b3` and `421da7e`).
- **Remediation Plan**: Under `TASK-EXT-02` (Phase A), this specification amendment will be formally staged and committed in its own isolated commit. It represents documentary hygiene and does not block independent read-only specifications.

---

## 9. Decision Register & Operational Recommendations

### 9.1 Summary of Current Project State

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CURRENT STATE CLASSIFICATION                              │
│                                                                                        │
│  [COMPLETED & ACCEPTED]                                                                │
│  • PIL-04.1B v0 Documentary Closure (Commit f9d9fba58a...)                             │
│  • Descriptive results report published (REPORT-QUICKGO-PILOT-PIL-04.1B-DESCRIPTIVE-001)│
│  • Five-source catalog candidate v0.3.0 packaged and frozen under ADR-006              │
│  • Pilot preservation local bundle pkg-quickgo-p1-p4-20261116-v1 verified              │
│                                                                                        │
│  [PENDING AUTHORIZATION / IN REVIEW]                                                   │
│  • Reproduction v1: Preserved locally, pending formal acceptance; does not replace v0 │
│  • Phase A Task Package (PIL-04.1A spec amendment commit & preservation report)        │
│  • Phase B Specification Package (specs/three-source-inventory-audit/)                 │
│  • Curatorial identity adjudication of P34788 (open review) and P24228 parser fix     │
│  • Indicative quarantine thresholds (e.g. tentative >5% unresolvable IDs proposal)    │
│                                                                                        │
│  [UNACCREDITED PRACTICES & ASSUMPTIONS]                                                │
│  • Reducing analysis to the 4-protein triple intersection (scientifically invalid)     │
│  • Running unconstrained automated pipelines without an approved SDD specification    │
│  • Predetermining the species or outcome of P34788 without formal curatorial review    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Critical Path & Parallelization Strategy

```
  [DOCUMENTARY HYGIENE]
  Commit PIL-04.1A Spec Amendment (Task-EXT-02) ──► Non-blocking documentary clean-up

  [CRITICAL PATH]
  Phase B Spec & Audit ──► Phase C (Engine) ──► Phase D (Pilot) ──► Phase G (Release)
             │                     ▲
  [PARALLEL CURATION TRACK]        │
  Curatorial Identity Review ──────┴────────────────────────────────────────────────
  (P34788 adjudication & P24228 markup investigation)
```
- **Independence of Critical Path**: Committing the PIL-04.1A retrospective documentary amendment is an independent repository maintenance action; it is **NOT a technical prerequisite** for drafting the Phase B inventory specification ([`specs/three-source-inventory-audit/spec.md`](../../specs/three-source-inventory-audit/spec.md)).
- **Parallel Track**: Curatorial adjudication of taxonomic discrepancies (`P34788`) and parser debugging (`P24228`) can proceed in parallel with Phase C engine refactoring, provided that neither track modifies shared working files without coordination.

### 9.3 Criteria for Declaring "Ready for Full 3-Source Execution"

The system shall be formally declared **"Ready for Full Three-Source Execution"** only when all seven gates are certified:

1. **Inventory Completeness**: 100% of the $1,508$ source records audited, with valid `MFPB_PROTEIN_ID_V1` hashes and zero unmapped accessions.
2. **Quarantine Accounting**: All unresolved biological identity or extraction failures isolated in an auditable quarantine table with explicit reason codes.
3. **Contract Parameterization**: Engine operates via configurable execution contracts without hardcoded accession lists.
4. **Regression Invariance**: Generalized engine verified to reproduce the frozen 8-protein pilot baseline bit-for-bit.
5. **Pre-Scale Pilot Acceptance**: Expanded pilot (Cohorts 1 and 2) completed, with zero unhandled exceptions and full denominator accounting.
6. **Batch Equivalence**: Concatenation of partitioned batch executions proven mathematically and serialized identical to monolithic execution.
7. **Human Gate Sign-Off**: Lead Maintainer / PI signs off on the Phase E scientific review memo.

### 9.4 Immediate Recommended Minimum Increment

To initiate this roadmap without violating repository boundaries, the immediate recommended next step is:

> [!TIP]
> **Recommended Increment: Authoring `specs/three-source-inventory-audit/` Package**:
> - **Objective**: Compile a comprehensive, fully reconciled inventory of coverage and biological identity across all $1,508$ records from MoonProt, MultitaskProtDB-II, and PlantMP before attempting any engine generalization.
> - **Scientific Boundary**: This increment does **NOT** require increasing Jaccard similarity or resolving every ambiguous biological case. Its purpose is complete accounting, characterization of duplicates, and transparent quarantine.
> - **Deliverables**:
>   1. `spec.md`: Scope, accounting criteria, and schemas for auditing the $1,508$ records.
>   2. `plan.md`: Read-only execution strategy, schema definitions, and quarantine policies.
>   3. `tasks.md`: Fine-grained task inventory (`TASK-EXT-04` through `TASK-EXT-07`) with explicit read/write boundaries.
>   4. `verification.md`: Planned offline checks.
>
> *Operational Boundary*: Authoring this specification involves **zero pipeline execution, zero network access, and zero modification of raw data**.

### 9.5 Specific Decisions Requiring Human Sign-Off

The following decisions require explicit human review and sign-off before subsequent work can begin:

1. **Acceptance of Roadmap Scope**: Approve this roadmap document (`ROADMAP-PILOT-TO-THREE-SOURCE-VALIDATION-2026-11-20`) as the guiding technical blueprint.
2. **Approval of Next Increment Scope**: Authorize drafting the specification package for Phase B ([`specs/three-source-inventory-audit/spec.md`](../../specs/three-source-inventory-audit/spec.md)).
3. **Authorization of Phase A Staging**: Confirm whether to stage and commit the pending retrospective amendment in `specs/quickgo-pilot-go-aspect-enrichment/spec.md` as an isolated documentary maintenance commit.
4. **Curatorial Mandate & Quarantine Policies**:
   - Confirm the formal mandate for an open curatorial identity review of `P34788` (evaluating evidence without predetermining the species).
   - Review and decide on the proposed indicative quarantine threshold (tentatively $>5\%$ unresolvable identifiers).

---

*Roadmap authoring concluded at 2026-11-20. Authored under branch `feature/functional-normalization` at commit `f9d9fba58a5a03a949c346a5956b8795b312b24d`.*
