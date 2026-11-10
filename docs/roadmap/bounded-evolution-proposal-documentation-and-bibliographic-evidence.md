# Bounded Evolution Proposal: Public Documentation Organization & Bibliographic Evidence Pilot

## Document Control & Governance Metadata

| Attribute | Specification Record |
|---|---|
| **Document Title** | Bounded Evolution Proposal: Public Documentation Organization & Bibliographic Evidence Pilot |
| **Document ID** | `PROP-EVOLUTION-2026-11-10` |
| **Document Location** | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) |
| **Authority Level** | **Level 6: Draft Proposal for Human Review** (Advisory & Architectural Proposal; strictly NOT approval to implement) |
| **Author Roles** | Senior Scientific-Software Architect & SDD Documentation Architect |
| **Target Repository** | `mfp-bibliography` (`/home/alexdoro/repositories/mfp-bibliography`) |
| **Creation Date** | 2026-11-10 |
| **Target Milestones** | Initiative 1: Documentation Integrity & English Migration (Pre-v1 Polish); Initiative 2: Post-v1 Phase D0 Bibliographic Evidence Pilot |
| **Governing Rules** | [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md), [ADR-001](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-001-repository-scope.md) through [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Document Language** | English (per repository policy; raw source citations preserved verbatim) |

---

> [!WARNING]
> **Architectural Proposal Notice (Awaiting Human Approval)**
> This document is a bounded evolution proposal submitted to the repository maintainers and scientific lead.
> In accordance with [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md) (§1.1, §2):
> 1. This proposal **does NOT constitute authorization** to edit existing code, alter schemas, migrate files, execute database queries, or contact external services.
> 2. Acceptance of this proposal does not imply approval of downstream metric engines or unreviewed machine-learning classifications.
> 3. All operational actions must proceed through discrete, independently reviewable specification-driven batches governed by explicit human decision gates.

---

## Executive Summary

This proposal outlines a bounded, coordinated strategy to evolve the `mfp-bibliography` repository along two strictly decoupled tracks:

1. **Initiative 1 (Public-Facing Documentation Organization & English Migration)**:
   A lightweight, low-risk documentation remediation program that eliminates entry-point contradictions, repairs 5 broken internal links, updates obsolete candidate version references (`v0.2.0` $\to$ `v0.3.0`), translates isolated Catalan sentences in public guides, indexes all 28 repository scripts and 6 formal JSON schemas, and safely quarantines 7,500 lines of unapproved historical Spanish and Catalan research proposals (`docs/roadmap/01-07`, `docs/roadmap/core/`) into `docs/archive/` with standardized English warning banners. This initiative touches **zero code, zero schemas, and zero data files**, and requires no dependencies on bibliographic feature development.

2. **Initiative 2 (Bibliographic Evidence Pilot)**:
   A specification-driven, offline-first pilot establishing an auditable relation model that links dataset-methodology literature, source-native citations, discrete protein functional claims, and reviewed primary experimental evidence. Grounded in the four prerequisite conditions of accepted [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), this initiative introduces a rigorous nine-entity bibliographic conceptual model, an assisted-processing policy governing non-deterministic tooling (LLMs/parsers), and an initial 3-publication empirical trial (MoonProt 3.0 methodology paper, PTRH2/Bit1 experimental crystallography paper, and the anomalous *E. coli* HolE source citation). It introduces **no new database servers, no graph infrastructure, and no network dependencies**, operating strictly on tabular CSVs and Draft 2020-12 JSON schemas.

---

## Section A: Current Baseline

### A.1 Working Tree State & Repository Verification

A static inspection of `/home/alexdoro/repositories/mfp-bibliography` conducted on 2026-11-10 establishes the following empirical baseline:

- **Current Branch**: `feature/functional-normalization` (tracking `origin/feature/functional-normalization` at commit `a6def6fef01f345f38532d30779d5b576b079580`).
- **HEAD Commit**: `a6def6f` (`Add functional tests for MultitaskProtDB-II claims and coverage schemas`, committed 2026-11-06 20:04:28 +0100 by `alexdorocode <alexdoro2024@gmail.com>`).
- **Repository Verification Status**:
  * Packaging and cryptographic verification: `PYTHONPATH=src python3 scripts/package_catalog_candidate.py --verify-package` passes cleanly with exit code 0 against candidate `v0.3.0` (`releases/mfp-catalog-candidate-v0.3.0/`).
  * Structural verification: `PYTHONPATH=src python3 scripts/validate_repository.py` passes all 9 checks (directory layout, manifest hashes, and schema syntaxes).
  * Executable contract test suite: 98 passing contract tests across `tests/test_functional_contracts.py`, `tests/test_functional_claims_multitask.py`, and `tests/test_source_go_annotations_contract.py`.

### A.2 Working Tree Drift: Modifications and Untracked Files

The audit report [`docs/audits/documentation-audit-2026-11-09.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/audits/documentation-audit-2026-11-09.md) provides snapshot evidence from 2026-11-09. Static inspection reveals that the active working tree has since evolved:

```
[Committed Baseline: a6def6f]
  │
  ├─ Tracked Modifications (9 files):
  │    ├─ specs/functional-normalization-pilot/{plan.md, spec.md, tasks.md, verification.md}
  │    ├─ src/mfp_bibliography/functional_claims_multitask.py
  │    ├─ tests/fixtures/functional_claims_multitask/{README.md, multitask_real_extract.csv, multitask_synthetic_edge_cases.csv}
  │    └─ tests/test_functional_claims_multitask.py
  │
  └─ Untracked Files & Directories (10 entries):
       ├─ data/curated/source_go_annotations.schema.json
       ├─ docs/audits/documentation-audit-2026-11-09.md
       ├─ docs/curation/ (contains Q9Y3E5_contextual_adjudication_dossier.md)
       ├─ docs/reports/multitask-six-record-context-readiness-review.md
       ├─ scripts/build_multitask_slice.py
       ├─ src/mfp_bibliography/functional_claims_plantmp.py       <-- New drift since 2026-11-09 audit
       ├─ tests/fixtures/functional_claims_plantmp/               <-- New drift since 2026-11-09 audit
       ├─ tests/test_build_multitask_slice.py
       ├─ tests/test_functional_claims_plantmp.py                 <-- New drift since 2026-11-09 audit
       └─ tests/test_source_go_annotations_contract.py
```

> [!IMPORTANT]
> **Audit Snapshot vs Current Working-Tree Reality**:
> The 2026-11-09 audit recorded 5 untracked files. Since that audit, three additional untracked entries have appeared: `src/mfp_bibliography/functional_claims_plantmp.py`, `tests/fixtures/functional_claims_plantmp/`, and `tests/test_functional_claims_plantmp.py`. These files represent early adapter work for PlantMP (Stage P3 / TASK-04 under proposed ADR-008). In accordance with [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md), this code remains **unauthorized** pending formal approval of Decision Gate G1. They must not be committed or promoted without explicit user sign-off.

### A.3 Existing Capabilities and Reusable Assets

The repository contains substantial verified infrastructure that must be leveraged without reinvention:

1. **The Immutable Five-Source Catalog Pipeline**:
   - Ingests `MoonDB` (351 rows), `MoonProt` (702 rows), `MultifacetedProtDB` (1,103 rows), `MultitaskProtDB-II` (694 rows), and `PlantMP` (112 rows).
   - Generates 2,962 source records, 2,322 distinct protein entities, and 463 exact-accession merges under deterministic SHA-256 scheme `MFPB_PROTEIN_ID_V1` ([ADR-005](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-005-deterministic-protein-ids.md)).
   - Enforces coverage-only rows for MoonProt administrative non-proteins (MPIDs 103, 542, 543, 626; [ADR-006](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-006-coverage-only-moonprot-status-rows.md)).
   - Verifiable offline via `releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json` and `checksums.sha256`.

2. **Active Specification-Driven Development (SDD) Packages**:
   - [`specs/functional-normalization-pilot/`](file:///home/alexdoro/repositories/mfp-bibliography/specs/functional-normalization-pilot/): Establishes contracts for `functional_claims` (relational one-to-many model), `functional_coverage` (denominator accounting), and `source_go_annotations` (explicit GO preservation).
   - Formulates the 6-level epistemological model ([`spec.md#L19-L31`](file:///home/alexdoro/repositories/mfp-bibliography/specs/functional-normalization-pilot/spec.md#L19-L31)), strictly separating raw source statements, normalized claims, proposed mappings, external GO annotations, literature evidence, and human curation.

3. **Curation Dossiers & Scientific Reviews**:
   - [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/curation/Q9Y3E5_contextual_adjudication_dossier.md): Exhaustive manual evidence curation dossier (`DOSSIER-Q9Y3E5-001`) evaluating human Peptidyl-tRNA hydrolase 2 / Bit1 (`Q9Y3E5`). Demonstrates how to contrast raw database claims against crystallographic data (PDB `1Q7S`, PMID `14660562`) and cellular apoptosis assays (PMID `15006356`).
   - [`docs/reports/multitask-six-record-context-readiness-review.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/reports/multitask-six-record-context-readiness-review.md): Scientific review report (`REV-MULTITASK-6REC-001`) evaluating the 6-record MultitaskProtDB-II pilot package against parent raw data, identifying upstream source anomalies (such as row 239 OMIM string and row 55 duplicated citation).

4. **Literature Reference Assets**:
   - `docs/bibliography/`: Contains 20 primary literature reference PDFs (e.g. `gkaa1101.pdf` for MoonProt 3.0, `baz050.pdf` for PlantMP, `gkt1153.pdf` for MoonProt 2014, `cells-12-00235.pdf`, etc.).
   - While untracked and read-only per boundary rules (no automated PDF parsing), these files represent valuable verified local references.

### A.4 Relationship to ADR-007 and the Functional Pilot

A central architectural question is the relationship between accepted [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) and downstream functional/bibliographic work:

- **ADR-007 Decoupled `mfp_catalog_v1`**:
  Accepted [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) formally descoped Phase D0 (laboratory annotation/evidence contract) and Phase D (bibliographic evidence graph) from the upcoming `mfp_catalog_v1` release. This descope ensured that a complete, offline-verifiable five-source catalog baseline would not be held hostage to complex bibliographic curation.
- **ADR-007 Stated Prerequisites for Post-v1 Work**:
  Crucially, ADR-007 did **not** permanently forbid bibliographic modeling; it explicitly defined four mandatory conditions for a post-v1 release to incorporate bibliographic relations ([`ADR-007#L37-L52`](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md#L37-L52)):
  1. *Versioned Relation Schema*: Distinguishing protein identity, source record, functional assertion, GO term, reference, and support relation.
  2. *Per-Relation Provenance*: Capturing source system, extraction method, pipeline version, and review status; strictly forbidding promotion of record citations to function support.
  3. *Zero Identifier Invention*: Required IDs (PMID, DOI, GO) must come from sources or validated systems, never fabricated.
  4. *Byte-Stable Reproduction*: Validated via deterministic offline verification gates.
- **Harmony with Proposed ADR-008**:
  Proposed [ADR-008](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-008-functional-normalization-pilot-scope.md) establishes an isolated functional normalization pilot on `feature/functional-normalization`. It isolates pilot data outputs in `data/interim/pilot/`, leaving `data/processed/mfp_catalog_mvp/` and `releases/mfp-catalog-candidate-v0.3.0/` 100% immutable and release-ready.
- **Architectural Ruling**:
  Initiative 1 (documentation organization) operates on the general documentation corpus and helps finalize `mfp_catalog_v1` readiness. Initiative 2 (bibliographic evidence pilot) serves as the formal specification and prototype for Phase D0, strictly fulfilling ADR-007's four conditions in an isolated sandbox without interfering with the baseline catalog.

### A.5 Epistemological Baseline: Facts, Proposals, and Unknowns

To maintain absolute scientific transparency, all repository elements are classified into three epistemic tiers:

| Dimension | Observed Facts (Verified in Code / Files) | Proposals (Designed; Awaiting Approval) | Unknowns (Pending Empirical Resolution) |
|---|---|---|---|
| **Catalog Baseline** | 2,962 records, 2,322 entities, candidate v0.3.0 packaged and verified offline ([`MANIFEST.json`](file:///home/alexdoro/repositories/mfp-bibliography/releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)). | Formal release candidate promotion to `mfp_catalog_v1` ([`mfp-catalog-v1-contract-draft.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/releases/mfp-catalog-v1-contract-draft.md)). | Exact upstream retrieval date for raw `MultifacetedProtDB_data.json` remains unknown. |
| **Functional Model** | Stage P2 MultitaskProtDB-II slice extracts 12 claims and 45 GO annotations from 6 records ([`data/interim/pilot/multitask_slice/`](file:///home/alexdoro/repositories/mfp-bibliography/data/interim/pilot/multitask_slice/)). | Proposed ADR-008 stages P3–P4 (PlantMP, MoonProt, MoonDB adapters; integrated CLI). | Whether PlantMP uncurated subset reflects true biological moonlighting or annotation artifact. |
| **Bibliographic Scope** | Descoped from v1 per accepted ADR-007. Raw sources contain unsegmented citation text and OMIM anomalies. | Conceptual 9-entity model, Phase D0 relation schemas, and 3-publication pilot proposed herein. | Full-text redistribution rights and exact licensing boundaries for commercial publisher PDFs. |
| **Documentation State** | 5 broken links; stale v0.2.0 references; contradictory headings in source profiles ([`documentation-audit-2026-11-09.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/audits/documentation-audit-2026-11-09.md)). | 4-batch remediation plan; archival of Spanish dossiers into `docs/archive/`; English synthesis guides. | Long-term ownership of historical Catalan research plans (`docs/roadmap/core/`). |
| **External Systems** | External database dumps (`biodata_mfp_snapshot_20261014.dump`) are untracked external files. | Decoupling downstream research repositories (PEC, PIS) from direct database dependencies. | Availability and schema stability of future external QuickGO / UniProt API updates. |

---

## Section B: Two Initiative Boundaries

The two proposed initiatives address distinct operational concerns, carry different risk profiles, and must be governed by independent approval gates.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     INITIATIVE 1: DOCUMENTATION INTEGRITY                       │
│                        (Pre-v1 Polish & Reorganization)                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Scope: README, Getting-Started, Source Profiles, Curated Schema READMEs, Archive│
│ Risk: Minimal (Documentation-only; zero code/schema modifications)              │
│ Gate DOC-G1: Batch 1 (Links & Versions) -> Gate DOC-G2: Batch 2 (Profiles/Idx)  │
│ Gate DOC-G3: Batch 3 (Archive Spanish Dossiers & Eliminate Mojibake)            │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ Independent; no blocking coupling
┌──────────────────────────────────────▼──────────────────────────────────────────┐
│                   INITIATIVE 2: BIBLIOGRAPHIC EVIDENCE PILOT                    │
│                      (Post-v1 Phase D0 SDD Specification)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Scope: SDD Spec under specs/bibliographic-evidence-pilot/, ADR-009, 3-Pub Trial │
│ Risk: Moderate (Data contracts, assisted extraction policies, curation models)  │
│ Gate BIB-G1: Scope ADR-009 -> Gate BIB-G2: Schemas & Offline Tests              │
│ Gate BIB-G3: 3-Publication Package Adjudication & Phase D0 Evaluation           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### B.1 Initiative 1: Public-Facing Documentation Organization & English Migration

#### Objectives
1. Eliminate all 5 broken internal markdown links identified in the technical audit ([ACT-02, ACT-03, ACT-04](#h-prioritized-action-matrix)).
2. Synchronize all public entry points (`README.md`, `docs/getting-started.md`, `five-source-descriptive-study-plan.md`, `mfp-catalog-v1-contract-draft.md`) to point to current candidate `v0.3.0`, deleting obsolete caveats claiming candidate files are uncommitted.
3. Translate isolated Catalan sentences in public-facing files (e.g. `README.md#L5`) into English.
4. Harmonize source profiles (`multifacetedprotdb.md`, `multitaskprotdb-ii.md`) and implementation roadmap (`mfp-catalog-implementation-plan.md`) to eliminate contradictory "not implemented" banners for fully integrated sources.
5. Create `data/curated/README.md` documenting all 6 formal JSON schemas, and expand `scripts/README.md` to document all 28 scripts.
6. Safely archive 13 unapproved Spanish research dossiers (`docs/roadmap/01-07`) and legacy Catalan plans into `docs/archive/`, prepending clear English status banners and quarantining the mojibake-corrupted duplicate `docs/roadmap/core/experiment_guio_v1.md`.

#### Explicit Non-Goals
- **No full translation of unapproved dossiers**: We will **NOT** translate 7,500 lines of unapproved Spanish/Catalan research proposals. Doing so would expend massive effort on material that violates current repository architecture (ADR-001, ADR-007). English status banners and metadata headers provide complete governance protection.
- **No rewriting of raw strings**: We will **NOT** translate or alter verbatim source strings, raw column names, or error logs.
- **No code changes**: Zero Python scripts or build pipelines will be altered under Initiative 1.

#### Independent Feasibility & Decoupling
Initiative 1 is **100% independent** of any bibliographic modeling. It can be executed immediately in three reviewable documentation batches (Batches 1, 2, and 3), restoring documentation integrity without waiting for scientific decisions on bibliography.

### B.2 Initiative 2: Bibliographic Evidence Pilot

#### Objectives
1. Implement Phase D0 requirements defined in [ADR-007](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) by authoring formal SDD specifications and schemas under `specs/bibliographic-evidence-pilot/`.
2. Formulate a relational, typed bibliographic evidence schema linking proteins, source claims, literature publications, evidence codes, and human review decisions.
3. Establish a rigorous Assisted Processing Policy governing LLM/parser assistance, ensuring complete model/prompt provenance, copyright protection, source locators, and human curation gates.
4. Execute an offline, byte-reproducible 3-publication empirical trial evaluating one dataset-methodology paper, one experimental paper, and one ambiguous case.

#### Explicit Non-Goals
- **No Graph Database Infrastructure**: No Neo4j, triplestores, RDF frameworks, or SPARQL endpoints. Flat RFC 4180 CSV tables with Draft 2020-12 JSON schemas fully satisfy all relational requirements.
- **No Live Network Scraping**: No automated downloading of paywalled publisher PDFs or automated bypassing of Cloudflare anti-bot challenges.
- **No Metric Calculations or Classifiers**: No Wang/Lin/MBL semantic similarity calculations, and no ML training.
- **No Baseline Mutation**: Catalog release candidate `v0.3.0` and baseline tables remain completely untouched.

#### Independent Approval Gates
Initiative 2 requires three sequential human decision gates:
- **Gate BIB-G1**: Approval of proposed `ADR-009` (authorizing bibliographic pilot scope and SDD drafting).
- **Gate BIB-G2**: Approval of candidate relation schemas (`publications.schema.json`, `bibliographic_evidence_relations.schema.json`) and executable contract tests.
- **Gate BIB-G3**: Human review and acceptance of the completed 3-publication curation dossier package.

---

## Section C: Minimum SDD Document Set

In accordance with the Specification-Driven Development workflow defined in [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md) (§4), work on these initiatives must be governed by precise specification packages.

### C.1 Proposed SDD Artifact Inventory

```
specs/
├── documentation-organization-and-migration/          <-- Initiative 1 Package
│   ├── spec.md          (Functional specs: links, banners, index coverage, language rules)
│   ├── plan.md          (Staged execution: Batches 1, 2, 3, and 4)
│   ├── tasks.md         (Task-level write boundaries: DOC-TASK-01 to DOC-TASK-04)
│   └── verification.md  (Automated check log: link checker, validator, diffs)
│
└── bibliographic-evidence-pilot/                      <-- Initiative 2 Package
    ├── spec.md          (Functional specs: 9-entity model, relation contracts, assisted policy)
    ├── plan.md          (Architectural plan: reuse of functional_claims, offline fixtures)
    ├── tasks.md         (Task-level write boundaries: BIB-TASK-01 to BIB-TASK-04)
    └── verification.md  (Validation log: contract tests, schema validation, package verify)
```

### C.2 Detailed Purposes of Proposed SDD Documents

1. **`specs/documentation-organization-and-migration/spec.md`**:
   - *Purpose*: Defines explicit acceptance criteria for repository documentation hygiene: 0 broken links, 100% English production guides, 100% script index coverage (28 scripts), 100% schema index coverage (6 schemas), and standardized archive headers.
   - *Invariants Enforced*: No modification of raw datasets; no alteration of packaged release artifacts; preservation of verbatim raw values.

2. **`specs/documentation-organization-and-migration/plan.md`**:
   - *Purpose*: Sequences documentation fixes into four decoupled batches: Batch 1 (P0 entry points & links), Batch 2 (P1 catalog profiles & indices), Batch 3 (P1 proposal archival & mojibake quarantine), and Batch 4 (P2 English methodology syntheses).
   - *Testing Strategy*: Pre-commit automated relative link verification and repository validation via `scripts/validate_repository.py`.

3. **`specs/documentation-organization-and-migration/tasks.md`**:
   - *Purpose*: Establishes rigid task-level file write boundaries. An agent working on `DOC-TASK-01` may touch only the 9 declared files in Batch 1.

4. **`specs/documentation-organization-and-migration/verification.md`**:
   - *Purpose*: Records audit trails of executed commands, markdown link checker scripts, and file diff counts to guarantee zero unintended mutations.

5. **`docs/decisions/ADR-009-bibliographic-evidence-pilot-scope.md`**:
   - *Purpose*: Establishes durable Level 1 architectural authority for Phase D0. Authorizes the relational bibliographic evidence model, affirms ADR-007 prerequisites, and formally defines assisted extraction boundaries.

6. **`specs/bibliographic-evidence-pilot/spec.md`**:
   - *Purpose*: Defines data structures, cardinality rules, nullability, sorting keys, and controlled vocabularies for publications, evidence relations, and assisted extraction ledgers.
   - *Key Requirement*: Enforces total separation between dataset citations and functional support claims.

7. **`specs/bibliographic-evidence-pilot/plan.md`**:
   - *Purpose*: Details architectural reuse of existing modules (e.g. `functional_claims` deterministic ID generation, `source_go_annotations` parsing) and defines isolated output directories under `data/interim/pilot/bibliographic_slice/`.

8. **`specs/bibliographic-evidence-pilot/tasks.md`**:
   - *Purpose*: Sequences implementation: `BIB-TASK-01` (JSON schemas), `BIB-TASK-02` (contract tests in `tests/`), `BIB-TASK-03` (3-publication offline fixture extract), `BIB-TASK-04` (scientific review dossier).

9. **`specs/bibliographic-evidence-pilot/verification.md`**:
   - *Purpose*: Logs offline test outcomes, JSON schema compliance checks, and hash stability across executions.

### C.3 Reuse of Existing Policies & Data Contracts

The SDD document set will strictly reference and reuse established canonical specifications without duplication:
- **Authority Hierarchy & Scientific Invariants**: Reference [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md) (§2, §5).
- **Raw Immutability & Provenance**: Reference [ADR-002](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-002-raw-data-immutability.md) and [ADR-003](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-003-provenance-and-transformations.md).
- **Label Separation**: Reference [ADR-004](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-004-evidence-label-benchmark-separation.md).
- **Deterministic Entity Identifiers**: Reference [ADR-005](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-005-deterministic-protein-ids.md) (`MFPB_PROTEIN_ID_V1`).
- **Epistemological Levels**: Reference [`specs/functional-normalization-pilot/spec.md#L19-L31`](file:///home/alexdoro/repositories/mfp-bibliography/specs/functional-normalization-pilot/spec.md#L19-L31).

---

## Section D: Bibliographic Conceptual Model

Scientific literature cannot be reduced to a flat list of PMIDs attached to protein accessions. To prevent epistemological conflation, the repository must adopt a formal conceptual model distinguishing nine distinct entities and four operational roles.

### D.1 Nine Core Conceptual Entities

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           1. PUBLICATION (Work of Scholarship)                  │
│                              └── 2. PUBLICATION VERSION (Preprint vs VoR)       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                       │ cited by or describes                   │
│                                       ▼                                         │
│ 3. DATASET / VERSION ─────────► 4. SOURCE RECORD ────────► 5. PROTEIN CLAIM     │
│   (e.g. MoonProt 3.0)             (Raw entry/row)            (Discrete role)    │
│                                                                   │             │
│                                                                   │ supported by│
│                                                                   ▼             │
│ 6. EXPERIMENTAL RESULT ◄────────────────────────────── 7. EVIDENCE LINK         │
│   (Assay, PDB, In Vitro)                                  (Typed relation)      │
│                                                                   ▲             │
│                                                                   │             │
│                           8. AUTOMATED EXTRACTION ────────────────┤             │
│                             (Provisional LLM tuple)               │ verified by │
│                                                                   │             │
│                           9. HUMAN REVIEW DECISION ───────────────┘             │
│                             (Signed curator judgment)                           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

1. **Publication**: An intellectual work of scholarship identified by canonical handles (DOI, PMID, PMCID, title, venue).
2. **Publication Version**: A specific manifestation of the publication (e.g. bioRxiv preprint `v1` vs peer-reviewed Version of Record in *J. Biol. Chem.*).
3. **Dataset / Dataset Version**: A frozen biological collection (e.g. MoonProt 3.0 snapshot, PlantMP 2019 release).
4. **Source Record**: A discrete row or entry within a dataset artifact (e.g. `multitaskprotdb_ii_row_672`).
5. **Protein Claim**: A normalized functional assertion extracted from a source record (e.g. `Peptidyl-tRNA hydrolase 2` or `Inhibitor of transcription`).
6. **Experimental Result**: An empirical finding documented in a publication version (e.g. 2.0 Å crystallographic electron density, enzymatic hydrolase assay, anoikis suppression in cell culture).
7. **Evidence Link**: A directional, typed relation connecting an experimental result in a publication to a specific protein claim.
8. **Automated Extraction**: A candidate assertion generated by an algorithm or language model, carrying extraction provenance; unverified by default.
9. **Human Review Decision**: A signed, versioned expert judgment adjudicating evidence links, resolving ambiguities, and determining ground-truth eligibility.

### D.2 Four Critical Operational Distinctions

A common bioinformatic flaw is treating any cited paper as proof of function. The architecture must strictly distinguish:

1. **A Paper Describing a Dataset** (e.g. Chen et al. 2021 describing MoonProt 3.0):
   - *Role*: Establishes database scope, inclusion/exclusion rules, and curation procedures.
   - *Boundary*: It is **NEVER** experimental evidence for individual protein claims. Linking Chen et al. 2021 as functional proof for all 702 MoonProt proteins is scientifically false.
2. **A Source Record Citing a Paper** (e.g. MultitaskProtDB-II row 672 citing PMID `14660562`):
   - *Role*: Represents an upstream bibliographic pointer showing where database authors sourced information.
   - *Boundary*: Does **NOT** prove that the cited paper supports all (or even any) of the claimed functions.
3. **A Paper Providing Relevant Experimental Evidence** (e.g. de Pereda et al. 2004 providing crystal structure and hydrolase kinetics):
   - *Role*: Reports primary wet-lab assays, controls, and structural data.
   - *Boundary*: Only the specific findings demonstrated by assay constitute evidence. Hypotheses in discussion sections (e.g. "suggests basis for bifunctional activity") are inferences, not experimental proof.
4. **A Reviewer Adjudicating Evidence** (e.g. `DOSSIER-Q9Y3E5-001` curator):
   - *Role*: Evaluates whether primary assays satisfy strict physiological criteria, records limitations, and signs adjudication records.
   - *Boundary*: Human curation adds an auditable evaluation layer; it never overwrites raw source data.

### D.3 Citation $\ne$ Scientific Support: Difficult Evidence States

In accordance with [`06_manual_revision_bibliografica.md`](file:///home/alexdoro/repositories/mfp-bibliography/docs/roadmap/06_manual_revision_bibliografica.md) and [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md) (§5), evidence relations must represent epistemic nuance without loss:

| Evidence State | Definition & Representation | Handling Policy in Schema |
|---|---|---|
| **Ambiguous Evidence** | Literature reports inferences, hypotheses, or weak indirect correlations (e.g. unit-cell contacts in crystal lattice). | Coded with `support_role = "ambiguous_inference"` and `review_status = "unresolved"`. Explicit notes explain ambiguity. |
| **Negative Evidence** | Experimental assays demonstrate absence of activity, or source provides GO `NOT` qualifier. | Coded with `support_role = "refutes"` and `is_negative = true`. **Strict Invariant**: Negative evidence is NEVER converted into a positive claim. |
| **Conflicting Evidence** | Multiple publications report opposing findings regarding enzymatic activity or cellular compartment. | Dual evidence links emitted with opposing support roles (`supports` vs `refutes`), linked by an adjudication record. |
| **Inaccessible Evidence** | Paper is behind a commercial paywall, out of print, or blocked by anti-bot barriers. | Coded with `access_status = "inaccessible"` and `support_role = "not_evaluable"`. **Rule**: Inaccessibility is NOT refutation. |
| **Missing Evidence** | Source provides no citations for a record or claim (e.g. MultifacetedProtDB, or PlantMP canonical functions). | Coded with `evidence_state = "unsupported_by_source"`. Citations must NEVER be fabricated or inferred. |

---

## Section E: Assisted Processing Policy

Language models and automated text extractors are valuable tools for literature triage, but introduce non-determinism, hallucinations, and copyright liabilities. This policy establishes strict guardrails for assisted processing.

### E.1 Access Hierarchy: Metadata vs Abstract vs Full Text

Processing depth must be governed by lawful access:

```
[Tier 1: Public Metadata] (PMID, DOI, Title, Authors, Venue, Year, Open Access License)
  └─ Freely retrievable, fully public, zero copyright barrier.
       │
[Tier 2: Public Abstract] (NCBI PubMed / Europe PMC Abstract Text)
  └─ Freely indexable for screening; captures author claims and high-level summaries.
     CANNOT verify experimental controls, assay sufficiency, or supplementary tables.
       │
[Tier 3: Full Text] (Open Access CC-BY PMC Full Text vs Restricted Paywall)
  └─ Open Access: Programmatic extraction permitted with exact section/passage locators.
  └─ Paywalled / Restricted: Programmatic crawling PROHIBITED; manual human reading only.
```

- **Abstract-Only Rule**: An abstract can establish author assertions, but can **never** certify physiological sufficiency or gold-standard moonlighting validation.
- **Paywall / Anti-Bot Rule**: Agents and scripts must **never** attempt to scrape paywalled publisher sites or solve/bypass CAPTCHA/Cloudflare barriers.

### E.2 Rights, Licensing, and Artifact Boundaries

To protect the repository and users from copyright infringement:
1. **No Proprietary Full-Text Storage**: Commercial publisher PDFs and bulk article full texts must **NEVER** be committed to public Git tracking.
2. **Permitted Public Storage**: Public repository artifacts may store:
   - Canonical bibliographic identifiers (PMID, DOI, PMCID).
   - Verbatim extract locators (e.g. `p. 8113, col. 2, para. 3` or `Figure 2B`).
   - Minimal fair-use quotation fragments strictly required for auditability ($\le 25$ words), accompanied by structured paraphrase.
3. **Private Sandbox Isolation**: Local full-text copies legitimately acquired by human researchers for research purposes must reside in gitignored local paths (e.g. `docs/bibliography/*.pdf`), strictly separated from public releases.

### E.3 Source Locators for Extracted Facts

Every assertion extracted by assisted tooling must be anchored by an immutable locator:
- Format: `loc = "<file_or_doi>::<section>::<page>::<paragraph_or_table_or_figure>"`.
- Floating or unanchored text summaries are invalid and must be rejected by automated validators.

### E.4 Non-Deterministic Generation vs Deterministic Validation

To guarantee repository integrity, automated workflows must maintain an unbreachable wall between generative assistance and deterministic validation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   NON-DETERMINISTIC GENERATION                         │
│                    (Assisted Tooling / LLMs)                           │
├────────────────────────────────────────────────────────────────────────┤
│ • Offline extraction of candidate relation tuples from abstract/text   │
│ • Candidate mapping proposals (e.g. EC -> GO crosswalk suggestions)   │
│ • Provenance logged: model, prompt hash, input text hash, timestamp    │
│ • Output destination: data/interim/assisted_staging/ ONLY             │
│ • Status: strictly "provisional_ai_extraction"                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Automated Schemas & Gates
┌───────────────────────────────────▼────────────────────────────────────┐
│                    DETERMINISTIC VALIDATION                            │
│                  (Automated Code & CI Gates)                           │
├────────────────────────────────────────────────────────────────────────┤
│ • Schema validation against Draft 2020-12 JSON Schemas                 │
│ • Strict regex checks (PMID: ^[0-9]+$, DOI: ^10\..+, GO: ^GO:[0-9]{7}$)│
│ • Referential integrity checks (Foreign Keys match catalog entities)   │
│ • Deterministic tie-breaking sort (Byte-reproducible CSV ordering)     │
│ • Total failure on missing locators or malformed fields                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Mandatory Human Decision Gate
┌───────────────────────────────────▼────────────────────────────────────┐
│                      HUMAN CURATION APPROVAL                           │
│                     (Expert Evidence Curator)                          │
├────────────────────────────────────────────────────────────────────────┤
│ • Independent expert review of candidate assertions & source locators  │
│ • Manual sign-off: curator_id, review_date, adjudication_rationale    │
│ • Formal promotion to "curated" in production tables                   │
│ • ZERO AUTOMATIC PROMOTION OF GENERATED SUMMARIES TO EVIDENCE          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Section F: A Three-Publication Pilot

To test the bibliographic conceptual model and assisted processing policies empirically without risking repository drift, we propose a bounded, offline 3-publication pilot.

### F.1 Three Target Publications (Selected from Local References)

All three publications are grounded in verified local files and database records. No external content acquisition or identifier invention is required.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           THREE-PUBLICATION PILOT                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Publication 1: Dataset-Methodology Paper                                        │
│   • Citation: Chen et al. (2021) "MoonProt 3.0", NAR 49(D1):D368–D372          │
│   • Local Presence: docs/bibliography/gkaa1101.pdf; cited in 06_manual §17.3    │
│   • Epistemic Role: Dataset-level methodology; zero claim-level support         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Publication 2: Primary Experimental Paper                                       │
│   • Citation: de Pereda et al. (2004) "Crystal structure of human Pth2", JBC    │
│   • Local Presence: multitask proteins.csv line 673; Q9Y3E5 dossier §3          │
│   • Epistemic Role: Experimental proof (hydrolase kinetics, 2.0 Å PDB 1Q7S)     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Publication 3: Ambiguous / Anomalous Source Case                                │
│   • Citation / Record: E. coli HolE / DNA pol III theta (P0ABS8)                │
│   • Local Presence: multitask proteins.csv line 240; multitask_real_extract Row5│
│   • Epistemic Role: Corrupted raw OMIM reference; inferred homology claim       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Publication 1: Dataset-Methodology Paper
- **Citation**: C. Chen, D. Arighi, L. Lu, K. Chen, M. A. A. Bonde, G. P. Srivastava, C. H. Wu. *"MoonProt 3.0: an update of the moonlighting proteins database."* **Nucleic Acids Research**, 49(D1):D368–D372, January 2021.
- **Identifiers**: PubMed ID `33170273`; DOI `10.1093/nar/gkaa1101`.
- **Local Evidence**: Untracked PDF verified in `docs/bibliography/gkaa1101.pdf`; cited in `docs/roadmap/06_manual_revision_bibliografica.md` ([§17.3, P2, line 651](file:///home/alexdoro/repositories/mfp-bibliography/docs/roadmap/06_manual_revision_bibliografica.md#L651)).
- **Rationale for Selection**: Authoritative methodology paper for MoonProt 3.0. Describes inclusion criteria (biochemical verification, exclusion of fusions/splice variants) and database statistics.
- **Pilot Function**: Tests the architecture's ability to model dataset-level publications. Acceptance check verifies that the system links this paper to `SRC_MOONPROT` as dataset metadata, while **strictly preventing** its linkage as functional proof to individual MoonProt protein claims.

#### Publication 2: Primary Experimental Paper
- **Citation**: J. M. de Pereda, W. F. Waas, Y. Jan, E. Ruoslahti, P. Schimmel, and J. Pascual. *"Crystal structure of a human peptidyl-tRNA hydrolase reveals a new fold and suggests basis for a bifunctional activity."* **Journal of Biological Chemistry**, 279(9):8111–8115, February 27, 2004.
- **Identifiers**: PubMed ID `14660562`; DOI `10.1074/jbc.M311449200`; PDB `1Q7S`.
- **Local Evidence**: Verbatim citation in `data/raw/multitaskprotdb-ii/proteins.csv` data row 672 (line 673, `Reference = "14660562"`) for `Q9Y3E5` (PTRH2 / Bit1); documented in `docs/curation/Q9Y3E5_contextual_adjudication_dossier.md` ([§3, Article 1, lines 84–100](file:///home/alexdoro/repositories/mfp-bibliography/docs/curation/Q9Y3E5_contextual_adjudication_dossier.md#L84-L100)).
- **Rationale for Selection**: Rigorous experimental study providing 2.0 Å crystallographic resolution, fold topology, and enzymatic peptidyl-tRNA hydrolase activity assays.
- **Pilot Function**: Tests the modeling of direct experimental support. Acceptance check verifies that hydrolase activity is linked with `support_role = "supports"` and experimental evidence code `EXP`, while the paper's bifunctionality hypothesis is captured as `support_role = "ambiguous_inference"`, proving that discussion inferences are not promoted to experimental proof.

#### Publication 3: Ambiguous / Anomalous Source Case
- **Target Record**: *Escherichia coli* DNA polymerase III subunit theta (`P0ABS8`, `MFP:U:77393f79103c4f1a`), cataloged in `data/raw/multitaskprotdb-ii/proteins.csv` line 240 (data row 239) and fixture `multitask_real_extract.csv` Row 5.
- **Raw Reference String**: `"HIV-1 and murine leukemia virus infection (omim:600534)"`.
- **Associated Claim**: Moonlighting function text: *"Exhibits structural and functional similarities to a family of nucleoid-associated regulatory proteins, the Hha/YdgT-like proteins that are also encoded by enterobacterial ORFan genes (a regulatory function can be attributed to HolE)"*.
- **Local Evidence**: Audited in `docs/reports/multitask-six-record-context-readiness-review.md` ([§1, line 27; §4, line 88](file:///home/alexdoro/repositories/mfp-bibliography/docs/reports/multitask-six-record-context-readiness-review.md#L27-L88)).
- **Rationale for Selection**: Represents a "stress test" containing three major real-world data corruptions:
  1. *Corrupted Upstream Reference*: An *E. coli* bacterial protein record carries a human retroviral infection OMIM string in its reference field!
  2. *Inferred Activity*: The claimed moonlighting role is based on structural homology inferences to ORFan genes, not direct assays.
  3. *Unresolved Reference*: No valid PMID or DOI exists in the raw cell.
- **Pilot Function**: Tests the architecture's error-handling and integrity. Acceptance check verifies that the pipeline parses the record without crashing, captures the raw string in `raw_reference_text`, flags `reference_status = "corrupted_source_reference"`, marks `claim_status = "ambiguous"`, and **strictly refuses** to fabricate a fake PMID or promote the text to verified evidence.

### F.2 Acceptance Checks & Stopping / Expansion Criteria

#### Acceptance Checks
1. **AC-BIB-01 (Dataset Isolation)**: The dataset publication (`gkaa1101`) is correctly linked to `SRC_MOONPROT` in `dataset_publications`, with exactly 0 rows generated in `protein_evidence_links`.
2. **AC-BIB-02 (Experimental Precision)**: For `Q9Y3E5`, peptidyl-tRNA hydrolase activity is linked to PMID `14660562` with `evidence_code = "EXP"`, while transcriptional corepression is flagged as unsupported by this article alone.
3. **AC-BIB-03 (Anomaly Resilience)**: For `P0ABS8`, the raw OMIM string is preserved verbatim, `pmid` is set to `null`, `claim_status` is serialized as `ambiguous`, and 0 valid evidence links are synthesized.
4. **AC-BIB-04 (Cryptographic Package Verification)**: The existing catalog verifier `python3 scripts/package_catalog_candidate.py --verify-package` passes before and after pilot execution, confirming complete catalog isolation.

#### Stopping Criteria (When to Abort / Re-evaluate)
- If modeling requires introducing a graph database or external server to execute basic queries.
- If processing requires downloading paywalled full texts or scraping web interfaces.
- If schema validation cannot prevent LLM hallucinations from entering production tables.

#### Expansion Criteria (When to Scale to Full Phase D0)
- 100% passing contract tests on the 3-publication fixture.
- Zero broken foreign keys or digest collisions.
- Written approval from the scientific lead on the curated evidence dossiers.

---

## Section G: Execution Proposal

To ensure complete control and risk management, execution is partitioned into small, independently reviewable batches.

### G.1 Execution Batches

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      SEQUENCED EXECUTION BATCHES                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ BATCH 1: Critical Entry-Point Correction & Broken Link Repair                   │
│   • Status: RECOMMENDED FIRST AUTHORIZED BATCH (Ready for immediate approval)    │
│   • Scope: 9 documentation files; fixes 5 broken links; v0.3.0 alignment        │
│   • Feasibility: F3 (doc-only); Risk: low; Dependencies: none                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ BATCH 2: Catalog Governance, Source Profiles & Script Index Expansion           │
│   • Scope: 11 documentation files; scripts/README.md (28 scripts), schemas      │
│   • Feasibility: F3 (doc-only); Risk: low; Dependencies: Batch 1 completion     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ BATCH 3: Research Proposal Archival & Status Banners                            │
│   • Scope: Segregate docs/roadmap/01-07 to docs/archive/; eliminate mojibake    │
│   • Feasibility: F2; Risk: low; Dependencies: Human Decision Gate G2            │
├─────────────────────────────────────────────────────────────────────────────────┤
│ BATCH 4: English Synthesis of Reusable Methodology & Background                 │
│   • Scope: Author docs/curation/literature-curation-manual.md; CHANGELOG        │
│   • Feasibility: F2; Risk: low; Dependencies: Batch 3 completion                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ BATCH 5: Bibliographic Evidence SDD Package & Schemas                           │
│   • Scope: specs/bibliographic-evidence-pilot/ and ADR-009                     │
│   • Feasibility: F1; Risk: moderate; Dependencies: Human Decision Gate G3       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ BATCH 6: Three-Publication Pilot Extraction & Curation Dossiers                 │
│   • Scope: Offline fixture extract, contract tests, and curation review         │
│   • Feasibility: F2; Risk: low; Dependencies: Batch 5 approval                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### G.2 Recommended First Authorized Batch: `DOC-BATCH-001`

We recommend that the maintainers authorize **`DOC-BATCH-001-ENTRYPOINT-AND-LINKS`** as the immediate next step.

- **Exact Write Boundaries (9 files only)**:
  1. `README.md`
  2. `docs/canonical-schema.md`
  3. `docs/maintenance/biodata-snapshot-and-restore-guide.md`
  4. `docs/maintenance/technical-maintenance-guide.md`
  5. `docs/roadmap/mfp-catalog-implementation-plan.md`
  6. `docs/getting-started.md`
  7. `docs/analysis/five-source-descriptive-study-plan.md`
  8. `docs/releases/mfp-catalog-v1-contract-draft.md`
  9. `tests/fixtures/functional_claims_multitask/README.md`
- **Permitted Modifications**:
  - Translate Catalan line 5 in `README.md` to English: *"This repository prioritizes traceability and reproducibility."*
  - Align link text in `README.md` lines 23 and 37 to `v0.3.0`.
  - Update release notes link in `README.md` line 64 to `docs/releases/mfp-catalog-candidate-v0.3.0.md`.
  - Delete obsolete working-tree clone caveats in `README.md` (lines 99–101) and `docs/getting-started.md` (lines 124–131).
  - Repair broken link `[Z|±HH:MM](Z|±HH:MM)` in `docs/canonical-schema.md`.
  - Replace broken `.dump` link in `docs/maintenance/biodata-snapshot-and-restore-guide.md` with explicit notice that the 4.8 MB file is external.
  - Replace 3 broken links to deleted `go-annotation-evidence-contract.md` with citations to ADR-007 and Phase D0.
  - Correct candidate link target in `five-source-descriptive-study-plan.md` and `mfp-catalog-v1-contract-draft.md` to `v0.3.0`.
  - Correct manifest path typo in `tests/fixtures/functional_claims_multitask/README.md#L7`.
- **Prohibitions**: Zero edits to `src/`, `scripts/`, `data/raw/`, `releases/`, or ADRs.
- **Verification Commands**:
  ```bash
  PYTHONPATH=src python3 scripts/validate_repository.py
  PYTHONPATH=src python3 scripts/package_catalog_candidate.py --verify-package
  ```
- **Rollback Approach**: If any test fails, `git restore` on the 9 target files restores the working tree instantly.

### G.3 Architectural Decisions Requiring User Approval

The following four decision gates require formal human sign-off before downstream implementation:

1. **Decision Gate G1 (Authorization of Batch 1 Documentation Edits)**:
   - *Question*: Do you authorize executing `DOC-BATCH-001-ENTRYPOINT-AND-LINKS` across the 9 declared files to repair broken links and align candidate v0.3.0 references?
2. **Decision Gate G2 (Archival of Spanish Dossiers & Mojibake Disposal)**:
   - *Question*: Do you approve migrating `docs/roadmap/01-07` to `docs/archive/proposals-2026-10-spanish/` with standardized English warning banners, and deleting the mojibake-corrupted duplicate `docs/roadmap/core/experiment_guio_v1.md`?
3. **Decision Gate G3 (ADR-008 Pilot Extension vs Bibliographic SDD Initiation)**:
   - *Question*: Should proposed [ADR-008](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-008-functional-normalization-pilot-scope.md) be formally approved to authorize PlantMP Stage P3 (resolving the untracked working-tree drift), or should we prioritize authoring proposed `ADR-009` for the Bibliographic Evidence Pilot?
4. **Decision Gate G4 (Three-Publication Pilot Execution)**:
   - *Question*: Do you approve the selection of MoonProt 3.0 (methodology), PTRH2/Bit1 (experimental), and *E. coli* HolE (ambiguous anomaly) for the initial offline bibliographic curation trial?

---

## Concise Approval Checklist

Please review the following decisions to authorize the next operational increment:

- [ ] **1. Approve Proposal Baseline**: Confirm that the baseline analysis, initiative boundaries, and epistemic distinctions in this document accurately reflect project priorities.
- [ ] **2. Authorize Batch 1 Execution**: Grant explicit authorization to execute `DOC-BATCH-001-ENTRYPOINT-AND-LINKS` across the 9 declared documentation files.
- [ ] **3. Approve Archival Strategy (Gate G2)**: Authorize creating `docs/archive/` to segregate unapproved Spanish/Catalan research dossiers with English warning banners.
- [ ] **4. Authorize Bibliographic SDD Drafting (Gate G3)**: Authorize drafting proposed `ADR-009` and `specs/bibliographic-evidence-pilot/spec.md` for human review.

---
*End of Proposal. Awaiting Maintainer Decision.*
