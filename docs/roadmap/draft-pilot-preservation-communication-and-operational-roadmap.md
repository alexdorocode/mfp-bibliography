# Operational Roadmap & Specification: Pilot Preservation, Scientific Communication, and Controlled Continuity

| Metadata Attribute | Value |
|---|---|
| **Document Title** | Operational Roadmap & Specification: Pilot Preservation, Scientific Communication, and Controlled Continuity |
| **Document ID** | `ROADMAP-PILOT-PRESERVATION-COMMUNICATION-2026-11-16` |
| **Document Location** | `docs/roadmap/draft-pilot-preservation-communication-and-operational-roadmap.md` |
| **Target Repository** | `mfp-bibliography` (`feature/functional-normalization`) |
| **Authority Level** | Level 6: Technical Proposal & Operational Blueprint (Advisory Draft; Implementation Requires Human Sign-Off) |
| **Status** | **Draft Proposal (Pending Human Review)** |
| **Date** | 2026-11-16 |
| **Revision** | **v1.8 (Canonical Enrichment Specification Synchronization & Track A Decision Scoping)** |
| **Author** | Senior Scientific Software Architect & Bioinformatics Data Auditor |
| **Governing Rules** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Canonical Reference Documents** | - Stage P3 Verification: [`specs/quickgo-pilot-p3/verification.md`](../../specs/quickgo-pilot-p3/verification.md)<br>- Stage P4 Analysis Report: [`docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`](../reports/quickgo-pilot-p4-descriptive-analysis-report.md)<br>- Preservation Record: [`docs/reports/quickgo-pilot-preservation-record.md`](../reports/quickgo-pilot-preservation-record.md)<br>- Canonical GO-Aspect Enrichment Spec: [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md) |

---

### Revision History

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| **v1.0** | 2026-11-16 | Architect & Auditor | Initial draft synthesizing pilot preservation, results communication, Marp presentation deck, and scientific continuity tracks. |
| **v1.5** | 2026-11-16 | Senior Auditor | Post-sufficiency review adjustments: identified P34788 raw taxonomic reality and P24228 markup cause. |
| **v1.6** | 2026-11-16 | Senior Architect & Reviewer | Reconciled with local preservation package `pkg-quickgo-p1-p4-20261116-v1` (42 payload files; Criterion B passed, Criterion C pending); decoupled parallel tracks (Track A vs Track B); added system boundaries (mfp-bibliography, PIS, PEC) and `MFP_CuratedData` definition. |
| **v1.7** | 2026-11-16 | Senior Architect & Reviewer | Coordination corrections & authorization alignment: recorded enrichment spec drafting as authorized; reclassified P34788/P24228 as candidate tasks; formalized P34788 provisional status; reduced decisions to 2 genuine Track A approvals. |
| **v1.8** | 2026-11-16 | Senior Architect & Reviewer | **Bounded synchronization update**: (1) Synchronized reference to confirmed canonical specification [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md); (2) Subdivided PIL-04.1 into `PIL-04.1A` (GO-aspect metadata mapping, pending implementation authorization) and `PIL-04.1B` (concordance recomputation, deferred & unauthorized); (3) Explicitly marked ontology downloads, parser repair, identity remediation, staging, and commits as outside authorization; (4) Clarified that listed decisions govern Track A only; (5) Framed post-enrichment evaluability as an analytical hypothesis to be evaluated against future technical verification. |

---

## 1. Project Orientation & Executive Summary

### 1.1 Four Core Orienting Questions

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. WHY DOES THIS PROJECT MATTER?                                                │
│    Multifunctional and moonlighting proteins perform multiple disparate         │
│    biochemical roles from a single polypeptide chain. Functional databases      │
│    catalog them with heterogeneous text, inconsistent GO terms, and unlinked    │
│    citations. mfp-bibliography builds an auditable, reproducible, and versioned │
│    source-evidence foundation to evaluate whether external proteome-scale       │
│    annotations (QuickGO) corroborate or diverge from source claims, without     │
│    conflating lexical matching with biological truth or gaps with negative data.│
│                                                                                 │
│ 2. WHAT EXISTS RIGHT NOW?                                                       │
│    • Candidate catalog release v0.3.0 (2,322 entities, verified offline).        │
│    • Stages P1–P2 frozen input fixtures (raw_quickgo_annotations.csv, coverage).│
│    • Stage P3 offline concordance engine and 4 Draft 2020-12 curated schemas    │
│      (Commit 4906b2e; 653/653 test suite passing offline).                      │
│    • Stage P4 descriptive concordance analysis across 8 purposive proteins      │
│      (docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md).            │
│    • Local preservation package pkg-quickgo-p1-p4-20261116-v1 assembled and     │
│      verified offline (42 payload files; Criterion B passed).                   │
│    • Canonical GO-aspect enrichment specification authored                      │
│      (specs/quickgo-pilot-go-aspect-enrichment/spec.md).                        │
│                                                                                 │
│ 3. WHAT DOES IT NOT YET ESTABLISH?                                              │
│    • Lexical overlap is descriptive; it does NOT prove biological function.     │
│    • Shared literature citations (PMIDs) do NOT prove functional claim support. │
│    • Findings from 8 proteins cannot be generalized to the 2,322 catalog cases. │
│    • The baseline is NOT durably preserved offsite (Criterion C is pending).    │
│    • Predicted post-enrichment evaluability is an analytical hypothesis, NOT an │
│      established empirical result until verified by implementation tests.       │
│    • Negative control sets or ML training labels are NOT established (BioData   │
│      is a reference population, never a negative class).                        │
│                                                                                 │
│ 4. WHAT ARE THE NEXT TWO EXECUTABLE INCREMENTS?                                 │
│    • Track A (PIL-01): Complete baseline closure by authorizing an independent  │
│      preservation copy (Criterion C) and committing the P4 report.              │
│    • Track B (PIL-04.1A / Proposed Stage Label "P5"): GO-aspect metadata        │
│      mapping specification completed; implementation pending explicit human     │
│      authorization instruction; concordance recomputation (PIL-04.1B) deferred. │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 System Ecosystem Boundaries

To prevent scope creep, duplication of effort, and architectural drift, repository boundaries are strictly defined across three related systems:

| System / Repository | Primary Operational Ownership | Interface with Pilot | Governing Boundary |
|---|---|---|---|
| **`mfp-bibliography`**<br>*(This Repository)* | Auditable source cataloging, deterministic identity resolution ([`MFPB_PROTEIN_ID_V1`](../decisions/ADR-005-deterministic-protein-ids.md)), raw claim provenance, descriptive concordance engines, and release packaging ([`releases/`](../../releases/)). | Owns Stages P1–P4 fixtures, concordance schemas, offline engines, preservation packages, and analytical reports. | [ADR-001](../decisions/ADR-001-repository-scope.md), [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md). Strictly offline; no ML models. |
| **`protein-information-system`**<br>*(PIS - Upstream Sister System)* | Upstream database infrastructure, management of proteome-scale ingestion pipelines (UniProtKB, QuickGO), and hosting database snapshots (`MFP_QuickV1`, `BioData`). | Provided read-only SQL transaction capture of frozen raw input fixtures for Stages P1–P2 (`f54bc4f`). | External database boundary. No automated live network crawling or direct SQL execution during catalog builds. |
| **`PEC`**<br>*(Protein Embedding Classifier)* | Downstream machine learning workflows: protein sequence/structure representation learning, embedding generation, classification benchmarking, and predictive evaluation. | Intended downstream consumer of future reviewed, versioned curated products; strictly decoupled from descriptive cataloging. | [docs/project-charter.md#L24-L27](../project-charter.md#L24-L27). Downstream modeling must not redefine raw provenance. |

- **Existing Data Exchanges**: Read-only extraction from PIS database snapshot `MFP_QuickV1` (observed `2026-11-12 15:53:22 UTC`) into frozen, static tabular fixtures (`tests/fixtures/quickgo_pilot/`). Candidate entity mappings provided by `releases/mfp-catalog-candidate-v0.3.0/`.
- **Proposed Interfaces**: Versioned exports of curated functional assertions and verified reference concordance slices from `mfp-bibliography` to PEC for downstream benchmark evaluation. Automated live synchronization between PIS and `mfp-bibliography` remains unauthorized.

### 1.3 Operational Meaning of `MFP_CuratedData`

Originating in historical proposal [`docs/roadmap/core/experimental-master-proposal.md`](core/experimental-master-proposal.md) and [proposed ADR-008 Level 3](../decisions/ADR-008-functional-normalization-pilot-scope.md#L42-L44), **`MFP_CuratedData`** denotes a planned, versioned scientific data product distinct from the raw catalog. Its inclusion criteria and review requirements are governed by strict operational rules:
1. **Explicit Relation Schema**: Conforms to the four post-v1 conditions of [accepted ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md#L37-L52), distinguishing protein entity, source observation, functional claim, GO term, literature citation, and curatorial support relation.
2. **Neutrality and Evidence Reality**: Does **NOT** require that all entries carry positive experimental verdicts. Neutral qualifiers (`qualifier_status = "not_captured"`), negative annotations (`NOT` qualifiers), and unassessed evidence codes are legitimate biological states that must be accurately preserved, not forced into artificial positives or deleted.
3. **Exploration without Exhaustive Literature Review**: Capturing and exploring external Gene Ontology annotations (as performed in P1–P4) does **NOT** require prior exhaustive sentence-by-sentence literature curation of every cited paper. Literature curation is an independent, higher-level evaluative tier.

---

## 2. Multi-Layered Scientific Data Lifecycle

The repository's scientific workflow is organized across four related, decoupled layers rather than a single linear pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-LAYERED SCIENTIFIC DATA LIFECYCLE                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  LAYER 1: CATALOG INVENTORY & ENTITY RESOLUTION [IMPLEMENTED & VERIFIED]        │
│  data/raw/ ──► Source Adapters ──► Deterministic Hashing ──► Candidate v0.3.0   │
│  (5 Sources)   (moondb, plantmp,    (MFPB_PROTEIN_ID_V1)     (releases/)        │
│                 moonprot, etc.)                                                 │
│                                                                                 │
│  LAYER 2: EXTERNAL ANNOTATION INTEGRATION PILOT [IMPLEMENTED & LOCAL ARCHIVE]   │
│  PIS Snapshot ──► Tier A Fixtures ──► Concordance Engine ──► Descriptive Report │
│  (MFP_QuickV1)    (tests/fixtures/)   (quickgo_concordance)  (P4 Report: §2–§5) │
│                                                │                                │
│                                                ▼                                │
│                                      [Preservation Package]                     │
│                                      (pkg-quickgo-p1-p4)                        │
│                                      • Local Payload: VERIFIED                  │
│                                      • Independent Copy: PENDING                │
│                                                                                 │
│  LAYER 3: SCIENTIFIC ENRICHMENT & CURATION [TRACK B PARALLEL INCREMENTS]        │
│  Preserved Baseline ──► Pinned Ontology Mapping ──► Curatorial Dossiers ──►    │
│  (P1–P4 Slice)          (go-basic.obo / PIL-04.1A)  (11-field protocol)         │
│                         [Proposed Label "P5"]                                   │
│                                                              │                  │
│                                                              ▼                  │
│                                                    [MFP_CuratedData Release]    │
│                                                    (ADR-007 / ADR-008 Level 3)  │
│                                                                                 │
│  LAYER 4: DOWNSTREAM REPRESENTATION & MODELING [OUT OF REPOSITORY SCOPE]        │
│  Reviewed Release ──► Embeddings & Featurization ──► Classification Benchmarks  │
│  (Curated Product)    (PEC / Downstream Workflow)    (ML Evaluation)            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Rigorous Accounting of Input Fixture Locations
To maintain absolute audit transparency, the lifecycle explicitly distinguishes between git-tracked fixtures and ignored local files:
- **Git-Tracked Input Fixtures**: `tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv`, `raw_quickgo_coverage.csv`, and `manifest.json` are committed in Git history (Commit `e714e97`).
- **Local Gitignored Artifacts**: The Tier A intermediate inputs (`data/interim/pilot/functional_claims_pilot.csv`, `source_go_annotations_pilot.csv`, `functional_coverage_pilot.csv`) and Stage P3 output tables (`data/interim/pilot/quickgo_slice/*.csv`) reside on local developer storage under `.gitignore` rules (`data/*`).
- **Preservation Bridge**: The local preservation package `pkg-quickgo-p1-p4-20261116-v1` captures both categories (all 42 files), ensuring complete byte-level restorable reproducibility independently of Git tracking status.

---

## 3. Technical Baseline: Verified, Reported, and Pending

This baseline reconciles the codebase state with the canonical preservation record ([`docs/reports/quickgo-pilot-preservation-record.md`](../reports/quickgo-pilot-preservation-record.md)):

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: DIRECTLY VERIFIED IN CODEBASE & DISK REPOSITORIES                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ • Branch: feature/functional-normalization @ Commit 21a3c8e.                    │
│ • P3 Implementation Committed: Commit 4906b2e (quickgo_concordance.py,          │
│   build_quickgo_concordance_pilot.py, 4 Draft 2020-12 JSON schemas, 39 tests).  │
│ • Full Test Suite: 653/653 tests passing offline (51.98s; pytest).              │
│ • Stage P4 Descriptive Report: Completed and verified offline                   │
│   (docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md).               │
│ • Local Preservation Package Created: pkg-quickgo-p1-p4-20261116-v1 located at  │
│   /home/alexdoro/mfp-preservation/quickgo-pilot/ (192,591 bytes compressed).    │
│ • Restoration Verification (Criterion B): PASSED. 42 payload files restored     │
│   to a simulated clean environment and verified bit-for-bit against SHA-256.    │
│ • Candidate Release v0.3.0: Pristine and verified offline (package_verify PASS).│
│ • Canonical Enrichment Specification: Authored and verified at                  │
│   specs/quickgo-pilot-go-aspect-enrichment/spec.md (SPEC-PIL-04.1).             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: DOCUMENTED & CERTIFIED ANALYTICAL FINDINGS (REPORTED IN P4)             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ • Comparison Universe: 8 accessions, 12 pairs, 36 units, 72 policy rows.        │
│ • Evaluability: Exactly 10 units evaluable (27.8%) and 26 non-evaluable (72.2%) │
│   under both Policy B and Policy C. Zero status transitions between policies.   │
│ • Non-Evaluability Drivers: 15 MoonProt aspect missingness, 6 P34788 identity   │
│   gate, 3 outside slice (A0A0H3CDS3), 2 empty aspect (P0AFW0 CC, Q42525 CC).    │
│ • Policy C Mechanics: Jaccard increased in 5 units (+0.003 to +0.056), identical│
│   in 5, decreased in 0. 100% driven by source root-term pruning (GO:0003674 /   │
│   GO:0008150), reducing the union denominator by 1 while QuickGO terms remained │
│   unchanged (zero ND rows, zero root rows in QuickGO capture).                   │
│ • Bibliographic Overlap: 7 evaluable pairs (6 share 1 PMID; 1 disjoint pair in   │
│   Q42525 PlantMP with J=0.0000; 5 non-evaluable).                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: PENDING ACTIONS, DISCREPANCIES, AND OPEN AUDIT FINDINGS                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│ • Independent Preservation Copy (Criterion C): PENDING. Package exists only on  │
│   local disk; independent offsite copy requires explicit maintainer approval.   │
│ • Documentary Commit Status: Stage P4 report and preservation record are        │
│   completed on disk but currently UNTRACKED in Git.                             │
│ • P34788 Candidate Correction (Provisional Finding): Inspection of raw files    │
│   (data/raw/plantmp/PlantMP_all.csv and multitask/proteins.csv) indicates both  │
│   sources cite Arabidopsis thaliana and PMID 7913892. This constitutes a        │
│   provisional candidate correction requiring formal curatorial review before   │
│   any gate change; historical P3/P4 results and the original identity gate     │
│   remain strictly preserved as observed.                                        │
│ • P24228 Upstream Extraction Bug (Candidate Task): Local raw file mpid_288.html │
│   is present; extraction failed due to unclosed quotes in PDB table markup.     │
│   Parser repair constitutes a candidate task requiring its own authorization.  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Two Coordinated Workstreams (Decoupled Parallel Execution)

To prevent communication deliverables from blocking scientific progress, the roadmap is organized into two independent, parallel tracks:

```
                               ┌─────────────────────────────────┐
                               │    CURRENT VERIFIED BASELINE    │
                               │  Commit 21a3c8e + Local Package │
                               └────────────────┬────────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 │                                                             │
                 ▼                                                             ▼
     [TRACK A: CLOSURE & COMMUNICATION]             [TRACK B: SCIENTIFIC ENRICHMENT]
     Operational Owner: Lead / Auditor              Operational Owner: Technical Agent / Architect
     ─────────────────────────────────              ─────────────────────────────────────────────
     • PIL-01: Baseline Closure (Offsite            • PIL-04.1A: GO-Aspect Metadata Mapping
       copy & P4/record git commit)                   (Spec authored; implementation pending auth)
     • PIL-02: Reader Guidance (docs/pilot/)        • PIL-04.1B: Concordance Recomputation
     • PIL-03: Presentation Deck (Marp) &             (Deferred & Unauthorized)
       Oral Narrative Companion                     • PIL-04.2: P24228 Parser Repair (Candidate)
                                                    • PIL-04.3: P34788 Curatorial Review (Candidate)
                                                    • PIL-04.4: 11-Field Curation Protocol
                                                    • PIL-04.5: Cohort Expansion Framework
     Prerequisite: Human approval of offsite        Prerequisite: PIL-04.1A implementation
     destination & document staging.                requires explicit human authorization.
```

### 4.1 Track A: Closure, Preservation, and Communication
Track A focuses on certifying the historical baseline, publishing documentation, and preparing communication assets:
- **`PIL-01.1` Offsite Independent Preservation Copy**: Authorize an approved offsite destination (e.g. restricted institutional storage or cold archive) to fulfill Criterion C of [`docs/reports/quickgo-pilot-preservation-record.md`](../reports/quickgo-pilot-preservation-record.md).
- **`PIL-01.2` Publication of Stage P4 & Preservation Records**: Review and commit `docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md` and `docs/reports/quickgo-pilot-preservation-record.md` to git tracking on `feature/functional-normalization`.
- **`PIL-01.3` (Optional Development Improvement) Distributable Fixtures**: Evaluate whether creating a Git-tracked fixture archive (`tests/fixtures/archives/`) is necessary, balancing clean-clone developer convenience against licensing and repository bloat. Reclassified as an optional improvement, not a mandatory prerequisite.
- **`PIL-02` Reader Guidance & Documentation Suite**: Author standalone Markdown documentation in `docs/pilot/` ([§4.3](#43-proposed-minimal-document-specifications)) once separately authorized.
- **`PIL-03` Presentation Deliverables**: Finalize the 12-slide Marp deck and oral companion guide for committee review.

### 4.2 Track B: Scientific & Technical Enrichment (PIL-04.1 / Proposed Stage Label "P5")
Track B advances the biological utility of the catalog without mutating historical results:
- **`PIL-04.1A` GO-Aspect Metadata Mapping (Proposed Stage Label "P5")**:
  - *Canonical Specification*: Formally specified in [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md) (`SPEC-PIL-04.1-GO-ASPECT-ENRICHMENT`).
  - *Evidence-Based Authorization Boundaries (Preserved Snapshot)*:
    1. **Specification Drafting**: **ALREADY AUTHORIZED & COMPLETED** (authored by the technical agent).
    2. **Implementation & Execution**: **PENDING EXPLICIT HUMAN AUTHORIZATION** (retained as pending authorization until explicitly confirmed by maintainers).
    3. **Ontology Acquisition**: **NOT AUTHORIZED** by this task (downloading external files requires explicit sign-off).
    4. **Git Staging, Commits, and Push**: **PENDING EXPLICIT APPROVAL**.
  > [!NOTE]
  > **Reconciliation Status Note (2026-11-18 / 2026-11-19)**:
  > The boundaries above record the governance snapshot as drafted on 2026-11-16. Subsequently on 2026-11-16, human sign-off was recorded authorizing the implementation of Task `PIL-04.1A`. Local implementation was committed under technical commit `98530b32cd13d0b8ff5b4ea7a626e691d9426d25` and verified offline in `specs/quickgo-pilot-go-aspect-enrichment/verification.md` (commit `421da7e81c450b4bbeca2c637bbbfe0c8db002b4`). Recorded human authorization is preserved in the increment specification and verification records; Git commits establish local implementation and testing on branch `feature/functional-normalization`, but do not constitute authorization themselves, and these commits remain unpushed to the remote repository (`origin`).
  > For `PIL-04.1B`, implementation code and 33 synthetic unit tests are present and reported passing in the local working tree (`specs/quickgo-pilot-concordance-recomparison/verification.md`), but technical code review and formal Gate 1 closure remain pending, and Gate 2 technical commit and Gate 3 pilot execution remain deferred and unauthorized. Readers must refer directly to B's verification record for its current status; this reconciliation pass grants no authorization for Gate 2 or Gate 3.
  - *Hard Scientific Invariants*: Aspect assignment is **namespace enrichment of existing identifiers, NOT discovery of new protein functions**. Must strictly distinguish native source aspect (`null`) from derived aspect (`BP/CC/MF`). Must handle secondary (`alt_id`) and obsolete terms explicitly. Must write to separate, versioned derived artifacts (`data/interim/pilot/quickgo_slice_enriched/`) without overwriting historical P3/P4 outputs.
  - *Evaluability Hypothesis Bounding*: Predicted post-enrichment evaluability (e.g. resolving aspect indeterminacy for MoonProt rows) is an **analytical hypothesis**, NOT an established empirical result. Final evaluability counts must be verified against the technical verification record once implementation is authorized and executed.
- **`PIL-04.1B` Concordance Recomputation (Deferred)**:
  - *Status*: **Deferred & Unauthorized**. Dependent upon completion and verification of `PIL-04.1A`. Recomputes concordance metrics under derived aspects in separate, derived tables.
- **`PIL-04.2` Candidate Task: MoonProt HTML Parser Repair for `P24228`**:
  - *Status*: Parallelizable candidate task requiring its own explicit authorization (not authorized by prior prompts).
  - *Scope*: Implement a robust tokenizer in `src/mfp_bibliography/parsers/moonprot.py` to extract Function 1, Function 2, and PMID 16411754 from frozen local file `data/raw/moonprot/mpid_288.html`. Zero live network requests.
- **`PIL-04.3` Candidate Task: Traceable Curatorial Review for `P34788`**:
  - *Status*: Parallelizable candidate task requiring its own explicit authorization (not authorized by prior prompts).
  - *Scope*: Author a formal curatorial audit memo evaluating the raw source evidence for *Arabidopsis thaliana* (PMID 7913892). Does not retroactively alter historical P3/P4 tables; serves as candidate input for post-P4 enrichment increments.
- **`PIL-04.4` Claim-Level Literature Curation Protocol**: Establish formal 11-field curation dossiers linking assertions to literature passages and ECO evidence codes (deferred post-enrichment).
- **`PIL-04.5` Cohort Expansion & Source Refresh Framework**: Define criteria for expanding beyond 8 proteins, requiring orthogonal isolation of cohort size, source database versions, and filtering policies (deferred post-enrichment).

> [!IMPORTANT]
> **No Artificial Inter-Track Blockers**: Track B does **NOT** depend on completing Track A's slide deck or documentation suite. Track B proceeds under its decoupled authorization boundaries.

---

## 5. Separation of Preservation Archives from Distributable Fixtures

To avoid conflating distinct data management requirements, the roadmap establishes clear boundaries between preservation archives and repository fixtures:

| Attribute | External Preservation Archive (`pkg-quickgo-p1-p4`) | Git-Tracked Distributable Fixture Archive (Optional) |
|---|---|---|
| **Primary Purpose** | Comprehensive disaster recovery and bit-level audit of the entire execution state (code, inputs, interim, outputs, manifests, reports). | Developer convenience for fresh-clone offline testing without manual interim data provisioning. |
| **Physical Location** | Local preservation directory (`$HOME/mfp-preservation/`) transitioning to offsite storage (Criterion C). | Repository directory `tests/fixtures/archives/` (if authorized). |
| **Measured Size** | **192,591 bytes** compressed (753,074 bytes uncompressed across 42 files). | Projected ~15–20 KB (restricted strictly to the 4 P3 output CSVs and Manifest v1.1). |
| **Redistribution Rights** | **Restricted Research Data**. Contains third-party biological assertions extracted from upstream sources not cleared for open redistribution. | **Restricted**. Tracking in a public git repository requires explicit legal/rights review; small size does not equal public distributability. |
| **Roadmap Classification** | **Mandatory Operational Asset** (already assembled and verified under Criterion A/B). | **Optional Development Improvement** (`PIL-01.3`). Reclassified as non-blocking. |

---

## 6. Scientific and Methodological Guardrails

All subsequent documentation, presentation materials, and enrichment specifications must enforce these scientific invariants:

1. **Policy C Mechanics & Evidence Retention**:
   Policy C excludes explicit `ND` (No Data) annotations and generic GO root terms (`GO:0003674`, `GO:0008150`, `GO:0005575`). In strict compliance with Policy C, **unassessed evidence codes are retained** in the comparison unless another approved exclusion applies.
2. **Lexical Concordance vs. Biological Validation**:
   Exact GO-identifier overlap is a continuous descriptive metric of database agreement. High Jaccard similarity does **NOT** validate biological moonlighting, and low Jaccard does **NOT** prove absence of function.
3. **Citation Co-Occurrence vs. Functional Support**:
   Shared PubMed IDs at the protein entity level confirm common literature consultation. They do **NOT** prove that the cited paper corroborates specific functional claims made by either database.
4. **Namespace Enrichment vs. Functional Discovery & Evaluability Hypothesis**:
   Assigning standard GO namespaces (`BP`, `CC`, `MF`) to existing source GO terms under `PIL-04.1A` is structural disambiguation. It is **NOT** the discovery of new biological activities. Predicted post-enrichment evaluability is an **analytical hypothesis**, NOT an established empirical result; final evaluability must be referenced to the technical verification record once executed.
5. **Catalog Packaging vs. Claim-Level Curation**:
   Packaging raw source statements into candidate releases (`v0.3.0`) preserves extraction provenance. It does **NOT** constitute scientifically curated claim-level knowledge.
6. **Schema Validation vs. Scientific Assessment**:
   Draft 2020-12 schema validation proves structural compliance and data integrity. It does **NOT** prove biological accuracy.
7. **Score Threshold Prohibitions**:
   No arbitrary quantitative cutoff (e.g. $J \ge 0.5$) establishes annotation "quality". Quantitative scores must be reported as continuous descriptive properties.
8. **Provisional Status of `P34788` Raw-Data Finding**:
   The empirical observation that PlantMP and Multitask raw sources cite *Arabidopsis thaliana* is a **provisional candidate correction requiring traceable curatorial review**. It does **NOT** constitute an already completed reversal of the historical identity gate; historical P3/P4 results remain gated as observed.
9. **Status of Stage P4**:
   Stage P4 is a **completed and verified descriptive analytical evaluation**, not an unimplemented pipeline stage.

---

## 7. Master Task Inventory (PIL Identifiers & Ownership)

| Task Code | Track | Workstream & Title | Status / Authorization State | Real Prerequisites | Responsible Role | Canonical Deliverables / Location |
|---|:---:|---|:---:|---|:---:|---|
| **`PIL-01.1`** | A | Offsite Preservation Copy | Pending Destination Approval | Human approval of offsite destination | Auditor / Lead | Offsite transfer receipt; Criterion C certified |
| **`PIL-01.2`** | A | Publication of P4 & Preservation Records | Ready to Commit | Lead review of untracked reports | Lead / Researcher | Tracked git commits on `feature/functional-normalization` |
| **`PIL-01.3`** | A | Distributable Fixture Archive | Optional Improvement | Rights evaluation for repo tracking | Agent / Reviewer | Optional `tests/fixtures/archives/` package |
| **`PIL-02.1`** | A | Master Pilot Index & Reading Guide | Ready for Authoring | `PIL-01.2` (Tracked P4 report) | Agent | `docs/pilot/README.md` |
| **`PIL-02.2`** | A | Methodology & Denominators Guide | Ready for Authoring | `PIL-01.2` | Agent | `docs/pilot/methodology-and-scope.md` |
| **`PIL-02.3`** | A | Analytical Tables & Figures Guide | Ready for Authoring | `PIL-01.2` | Agent | `docs/pilot/tables-and-figures.md` |
| **`PIL-02.4`** | A | Boundary & Limitation Dossier | Ready for Authoring | `PIL-01.2` | Joint Review | `docs/pilot/limitations-and-exclusions.md` |
| **`PIL-03.1`** | A | 12-Slide Master Deck (Marp) | Ready for Authoring | `PIL-02` suite draft | Agent / Researcher | `docs/pilot/slides-deck.md` (Proposed Material) |
| **`PIL-03.2`** | A | Presentation Companion & Script | Ready for Authoring | `PIL-03.1` | Agent / Lead | `docs/pilot/presentation-companion.md` |
| **`PIL-03.3`** | A | Pre-Presentation Audit & Sign-Off | Ready for Review | `PIL-03.2` | Human Lead | Signed presentation checklist |
| **`PIL-04.1A`**| B | GO-Aspect Metadata Mapping | **Spec Completed; Implementation Pending Auth** *(See 2026-11-18 Status Note in §4.2: Implemented & Verified locally on 2026-11-16; unpushed)* | Explicit human implementation instruction; ontology download unauthorized | Technical Agent | [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md) |
| **`PIL-04.1B`**| B | Concordance Recomputation | **Deferred & Unauthorized** *(Gate 1 code/tests present in working tree; technical review pending; Gate 2/3 unauthorized; see B's verification.md)* | Verification of PIL-04.1A mapping | Technical Agent | `data/interim/pilot/quickgo_slice_enriched/` |
| **`PIL-04.2`** | B | Local MoonProt Parser Fix (`P24228`) | **Candidate Task** (Requires Authorization) | Explicit human task authorization | Agent | Repaired tokenizer; regression tests |
| **`PIL-04.3`** | B | Curatorial Review of `P34788` | **Candidate Task** (Requires Authorization) | Explicit human task authorization | Researcher | Curatorial audit memo; candidate resolution |
| **`PIL-04.4`** | B | 11-Field Literature Curation Protocol | Deferred Post-Enrichment | None (Methodological design) | Joint Review | `data/curated/claim_curation.schema.json` |
| **`PIL-04.5`** | B | Cohort Expansion Framework | Deferred Post-Enrichment | Track B completion | Architect | Multi-variable isolation protocol |

---

## 8. Proposed Presentation Material: 12-Slide Script (Draft for Review)

> [!NOTE]
> **Status Notice**: The following 12-slide script represents **proposed presentation material** prepared for review. It is not an already generated, compiled, or officially approved slide deck. Rendering to PDF/HTML will occur under task `PIL-03.1`.

```markdown
<!-- slide 1: Title & Context -->
# Evidence Integration Pilot: QuickGO & MFP Catalog
## Descriptive Set-Theoretic Concordance & Upstream Data Integration Realities

- **Presenter**: Senior Scientific Software Architect & Bioinformatics Researcher
- **Context**: `mfp-bibliography` / Stage P4 Technical Evaluation
- **Core Message**: Concordance between primary moonlighting databases and proteome-scale GO annotations is strictly conditioned by upstream capture depth, structural metadata gaps, and identity resolution.

*Oral Script (1 min)*: Welcome. We present an empirical evaluation of how primary multifunctionality databases intersect with QuickGO annotations across an 8-protein pilot cohort. This is an audit of data structures and reproducibility, not a machine learning benchmark.

<!-- slide 2: Guiding Question & Scientific Boundaries -->
# Research Question & Operational Scope

### The Guiding Question
> *"For a purposively selected eight-accession cohort, what exact GO-identifier and reference overlap is observed between source-explicit annotations and the frozen MFP_QuickV1 capture, and how do coverage, identity, and capture limitations constrain this comparison?"*

### Explicit Scientific Boundaries
- **Descriptive Concordance**: Measures lexical overlap; does **NOT** validate biological moonlighting.
- **Reference Population**: QuickGO/BioData is a background reference, **NEVER** a negative class.
- **Purposive Cohort**: Evaluates technical edge cases; cannot be extrapolated to the full 2,322 entities.

*Oral Script (1.5 min)*: Frame the scope early. We evaluate set-theoretic intersection. Absence of annotation is an annotation gap, never evidence of absence of function.

<!-- slide 3: Denominator Accounting & Comparison Universe -->
# Comparison Universe & Denominator Hierarchy

To prevent statistical confounding, analysis enforces 5 orthogonal denominators:

```
┌───────────────────────────────────────────────────────────────────────┐
│ 1. COHORT ACCESSIONS (N = 8)                                          │
│    Biological protein identifiers selected for structural diversity. │
│ 2. ACCESSION-SOURCE PAIRS (N = 12)                                    │
│    Curated records across MoonProt, MultitaskProtDB-II, and PlantMP.  │
│ 3. ACCESSION-SOURCE-ASPECT COMPARISON UNITS (N = 36)                  │
│    Primary operational unit of GO comparison: Pair × {BP, CC, MF}.    │
│ 4. POLICY-SPECIFIC CONCORDANCE ROWS (N = 72)                          │
│    Analytical evaluations: Unit × {Policy B, Policy C}.               │
│ 5. REFERENCE-CONCORDANCE ROWS (N = 12)                                │
│    Publication inventory comparisons evaluated at the pair level.     │
└───────────────────────────────────────────────────────────────────────┘
```

> [!WARNING]
> Comparison rows are repeated observations; they must **NEVER** be pooled as independent samples.

*Oral Script (1.5 min)*: Clarify the numbers. 72 rows represent repeated evaluations across 36 aspect units and 12 pairs spanning 8 accessions.

<!-- slide 4: Data Flow & Offline Pipeline Architecture -->
# Offline Pipeline Architecture & Verification

```
  [Frozen Database MFP_QuickV1]
               │ (REPEATABLE READ / Read-Only SQL Export)
               ▼
  [Tier A Fixtures: tests/fixtures/quickgo_pilot/]
    ├─ raw_quickgo_annotations.csv (156 rows)
    ├─ raw_quickgo_coverage.csv (8 accessions)
    └─ manifest.json (Frozen SHA-256 digests)
               │
               ▼ (100% Offline Python Concordance Engine)
  [Interim Pilot Slices: data/interim/pilot/quickgo_slice/]
    ├─ quickgo_concordance_pilot.csv (72 rows)
    ├─ quickgo_reference_concordance_pilot.csv (12 rows)
    └─ manifest.json (Manifest v1.1)
```
- **Reproducibility**: 100% offline; bit-identical execution from frozen fixtures.
- **Test Suite**: 653 automated tests passing offline (51.98s).

*Oral Script (1 min)*: Highlight engineering rigor. Zero network requests during execution; bit-stable reproduction verified by SHA-256.

<!-- slide 5: The Evaluability Ceiling -->
# The Evaluability Ceiling: 72.2% Non-Evaluable

Across the 36 Comparison Units, only **10 units (27.8%)** are evaluable:

| Category | Primary Non-Evaluable Reason | Affected Units | % of Non-Evaluable |
|---|---|:---:|:---:|
| **Evaluable** | Both inventories complete & comparable | **10** | — |
| **Non-Evaluable** | `source_aspect_indeterminate` (MoonProt) | 15 | 57.7% |
| | `unresolved_biological_identity` (`P34788`) | 6 | 23.1% |
| | `source_record_outside_slice` (`A0A0H3CDS3`) | 3 | 11.5% |
| | `source_record_no_terms_aspect` (Empty Aspect)| 2 | 7.7% |
| **Total** | | **36** | **100.0%** |

- **Key Takeaway**: Non-evaluability is driven by upstream data structure gaps, not biological incompatibility.

*Oral Script (2 min)*: The central finding. Nearly three quarters of comparisons could not be scored. Walk through why: MoonProt omitted GO aspects; P34788 had a flagged identity gate; one control was outside the slice. We do not replace empty sets with zeros.

<!-- slide 6: Paired Policy Comparison -->
# Paired Policy Comparison: Policy B vs. Policy C

Evaluated across the **10 eligible paired comparison units**:

| Accession | Source | Aspect | Policy B Jaccard ($J_B$) | Policy C Jaccard ($J_C$) | $\Delta J$ | Direction |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `P0AFW0` | MULTITASK | BP | 0.4000 | 0.4000 | 0.0000 | Identical |
| `P0AFW0` | MULTITASK | MF | 0.4444 | 0.5000 | **+0.0556** | Increased |
| `Q42525` | MULTITASK | BP | 0.2917 | 0.3043 | **+0.0126** | Increased |
| `Q42525` | MULTITASK | CC | 0.3333 | 0.3333 | 0.0000 | Identical |
| `Q42525` | MULTITASK | MF | 0.4615 | 0.5000 | **+0.0385** | Increased |
| `Q42525` | PLANTMP | BP | 0.0938 | 0.0968 | **+0.0030** | Increased |
| `Q42525` | PLANTMP | MF | 0.2308 | 0.2500 | **+0.0192** | Increased |
| `Q9Y3E5` | MULTITASK | BP, CC, MF | 0.3333–0.6000 | 0.3333–0.6000 | 0.0000 | Identical |

- **Summary**: 5 units increased ($\Delta J \in [+0.003, +0.056]$); 5 units identical; 0 decreased.

*Oral Script (1.5 min)*: Present the scores objectively. Under Policy C (filtering generic root terms), half the scores increased slightly. But why did they increase? Move immediately to Slide 7.

<!-- slide 7: Deconstructing the Score Increase -->
# Deconstructing Policy C: Arithmetic vs. Biology

Why did Jaccard similarity increase under Policy C?

### The Exclusion Mechanism
1. **QuickGO Filtering**: Exactly **0 rows excluded** (zero ND terms, zero root terms in QuickGO capture). QuickGO term sets remained identical ($Q_C = Q_B$).
2. **Source Filtering**: Generic root terms (`GO:0003674`, `GO:0008150`) were removed from Multitask and PlantMP ($S_C = S_B - 1$).
3. **Mathematical Impact**:
   $$J_C = \frac{|S_C \cap Q_C|}{|S_C \cup Q_C|} = \frac{|S_B \cap Q_B|}{|S_B \cup Q_B| - 1} > J_B$$

> [!IMPORTANT]
> Score increases are an **arithmetic artifact of pruning high-level placeholders from the denominator**, NOT evidence of superior biological concordance.

*Oral Script (1.5 min)*: Methodological rigor. We proved mathematically that the gain was 100% arithmetic denominator shrinkage from removing unshared source placeholders.

<!-- slide 8: Bibliographic Concordance -->
# Bibliographic Concordance: Entity-Level Citations

Comparing publication inventories across all **12 Accession–Source Pairs**:

| Outcome | Pair Count | Characteristics |
|---|:---:|---|
| **Shared Primary Reference** | **6** | Source cites 1 PMID; QuickGO shares that exact PMID ($R_{src} \cap R_{qgo} = 1$). Low Jaccard ($0.036–0.167$) due to QuickGO proteome breadth (up to 28 PMIDs). |
| **Genuinely Disjoint Sets** | **1** | `Q42525` / PlantMP cites 2 PMIDs; QuickGO cites 28 PMIDs; **Zero shared** ($J = 0.0000$). |
| **Non-Evaluable** | **5** | Identity gated (`P34788`, 2); Unlinked capture (`E6KMA1`, 1); HTML parser failure (`P24228`, 1); Outside slice (`A0A0H3CDS3`, 1). |

- **Key Takeaway**: Co-occurrence of PMIDs confirms common literature consultation, but does **NOT** prove functional claim corroboration.

*Oral Script (2 min)*: In 6 pairs, the databases read the exact same paper. But in PlantMP Q42525, they cite completely disjoint literature. Stress ADR-007: citation matching != functional corroboration.

<!-- slide 9: Diagnostic Case Studies -->
# Diagnostic Case Studies: Technical vs. Biological Reality

### Case 1: `Q42525` (Hexokinase-1, *A. thaliana*)
- PlantMP cites 2 PMIDs for moonlighting activity; QuickGO cites 28 PMIDs for glycolytic enzymes. Complete reference divergence ($J=0.0000$), yet both describe the same biological entity.

### Case 2: `P0AFW0` (Transcriptional regulator RfaH, *E. coli*)
- Perfect sharing of primary literature (`PMID:22817892`). Molecular function concordance $J=0.5000$; Cellular component non-evaluable due to zero source annotations.

### Case 3: Missingness Controls (`A0A0H3CDS3`, `E6KMA1`)
- Accurately captured database missingness: `E6KMA1` has `protein_id IS NULL`; `A0A0H3CDS3` has 0 annotations in QuickGO.

*Oral Script (1.5 min)*: Ground the statistics in real biological cases. Hexokinase is a famous plant moonlighting protein. Show how our pipeline accurately flagged missingness controls without crashing.

<!-- slide 10: Auditor Findings on Upstream Discrepancies -->
# Auditor Investigation: P24228 & P34788

Direct inspection of raw repository files reveals critical auditor insights:

### 1. `P24228` (D-alanyl-D-alanine carboxypeptidase DacB)
- **Status in P4**: Non-evaluable reference concordance (`source_extraction_incomplete`).
- **Audit Finding**: Local raw HTML `mpid_288.html` is present. Extraction failed due to an unclosed quotation mark in the PDB table markup (`href="...2EXB>`). Constitutes a candidate parser fix requiring authorization.

### 2. `P34788` (40S ribosomal protein S18)
- **Status in P4**: Gated by `unresolved_biological_identity` ("PlantMP cites Spinach").
- **Audit Finding**: Raw source inspection indicates both cite *Arabidopsis thaliana*. This represents a provisional candidate correction requiring formal curatorial review before any gate change; historical P3/P4 results remain gated.

*Oral Script (2 min)*: Demonstrates deep technical mastery. We audited the raw files on disk. P24228 was an HTML syntax error in MoonProt. P34788 was an unverified query note. Both are solvable offline without live scraping.

<!-- slide 11: Preservation Certification & Package Status -->
# Preservation Architecture & Package Certification

Preservation status certified under [`RECORD-QUICKGO-PILOT-PRESERVATION-001`](../reports/quickgo-pilot-preservation-record.md):

```
┌────────────────────────────────────────────────────────────────────────┐
│ Criterion A: Local Package Created & Verified ───────> [VERIFIED / OK] │
│ Criterion B: Restoration Test Passed ────────────────> [PASSED / OK]   │
│ Criterion C: Independent Offsite Copy Verified ──────> [PENDING]       │
│ Criterion D: Computational Rerun Verified ───────────> [NOT PERFORMED] │
└────────────────────────────────────────────────────────────────────────┘
```
- **Package `pkg-quickgo-p1-p4-20261116-v1`**: 42 payload files (192,591 bytes compressed) anchored by SHA-256 digest `f02c6f47...`.
- **Restoration**: 100% offline restoration verified in clean directory.

*Oral Script (1 min)*: Transparent preservation status. Local package is assembled and restorable; independent offsite copy is pending formal authorization.

<!-- slide 12: Decoupled Roadmap & Track A Decisions Requested -->
# Continuation Roadmap: Track A Decisions Requested

```
  [TRACK A: CLOSURE & PRESENTATION] ──► Authorize offsite copy & publish P4
                                                │
                                                ▼ (Parallel / Decoupled)
  [TRACK B: SCIENTIFIC ENRICHMENT]  ──► GO-Aspect Metadata Mapping (PIL-04.1A)
                                        (Canonical spec authored; impl pending auth)
```

### Track A Decisions Requested from Maintainers Today:
1. **Authorize Track A Offsite Copy**: Approve destination for independent preservation copy (Criterion C).
2. **Authorize P4 & Preservation Record Publication**: Approve staging and committing `quickgo-pilot-p4-descriptive-analysis-report.md` and `quickgo-pilot-preservation-record.md` to Git.

*Oral Script (1.5 min)*: The decisions requested today concern Track A baseline closure and documentation publication only. Track B implementation and candidate remediation will require their own separate authorizations when reached.
```

---

## 9. Definition of Done: "Pilot Ready for Presentation"

The pilot is officially declared **"Ready for Presentation"** when all 8 criteria below are satisfied:

1. **Denominators Fully Enumerated**: 100% of the 8 accessions, 12 pairs, 36 comparison units, and 72 policy rows are enumerated in documentation with zero dropped rows.
2. **Deterministic Non-Evaluability Audit**: Every non-evaluable unit carries an explicit, mutually exclusive primary reason code conforming to the P3 hierarchy.
3. **Local Preservation Package Certified**: Local package `pkg-quickgo-p1-p4-20261116-v1` has passed restoration verification (Criterion B: PASSED), with Criterion C status transparently declared.
4. **Standalone Communication Suite Drafted**: Directory `docs/pilot/` contains complete Markdown files answering methodology, result, and limitation questions.
5. **Traceability Closure**: Every number, percentage, and Jaccard score appearing in slides is traceable to a specific CSV column in `quickgo_concordance_pilot.csv` or `quickgo_reference_concordance_pilot.csv`.
6. **Scientific Guardrails Enforced**: Zero slides equate Jaccard similarity with biological proof, equate shared PMIDs with functional corroboration, or pool comparison rows as independent observations.
7. **Offline Delivery Verification**: The entire presentation deck and oral companion can be reviewed and rendered without active internet or database connections.
8. **Explicit Human Sign-Off**: Human maintainers approve the slide narrative and agree that historical P1–P4 results remain frozen.

---

## 10. Immediate Actionable Plan & Human Approvals Required

### 10.1 Immediate Executable Next Steps
1. **Step 1 (Track A - Offsite Preservation Authorization)**: Human maintainers designate an approved external/cloud storage destination to fulfill Criterion C.
2. **Step 2 (Track A - Report Git Staging)**: Add `docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md` and `docs/reports/quickgo-pilot-preservation-record.md` to git tracking on `feature/functional-normalization`.
3. **Step 3 (Track B - Canonical Specification Reference)**: Technical agent has authored the canonical specification at [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md). Implementation of `PIL-04.1A` remains pending explicit human authorization; concordance recomputation (`PIL-04.1B`), ontology downloads, candidate parser repairs, and git operations remain unauthorized.

### 10.2 Genuine Unresolved Human Decisions (Track A Only)

> [!NOTE]
> **Scope of Listed Decisions**: The decisions below concern **Track A baseline closure and documentation publication only**. They do NOT constitute an exhaustive list of all future scientific or technical approvals (e.g., Track B implementation, candidate remediation tasks, release tagging, and offsite transfers each require separate explicit approvals when reached).

- [ ] **Decision 1 (Track A Offsite Preservation Destination)**: Do you authorize an approved destination (e.g. restricted institutional storage) to establish an independent offsite copy of preservation package `pkg-quickgo-p1-p4-20261116-v1`?
- [ ] **Decision 2 (Track A Report Publication)**: Do you approve staging and committing the completed Stage P4 report and the preservation record to Git?

---
*End of Operational Roadmap and Specification.*
