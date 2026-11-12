# Bounded Evolution Proposal: Public Documentation Organization & Bibliographic Evidence Pilot

## Document Control & Governance Metadata

| Attribute | Specification Record |
|---|---|
| **Document Title** | Bounded Evolution Proposal: Public Documentation Organization & Bibliographic Evidence Pilot |
| **Document ID** | `PROP-EVOLUTION-2026-11-10-AMEND1` |
| **Document Location** | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) |
| **Authority Level** | **Level 6: Draft Proposal for Human Review** (Advisory & Architectural Proposal; strictly NOT approval to implement) |
| **Author Roles** | Senior Scientific-Software Architect & SDD Documentation Architect |
| **Target Repository** | `mfp-bibliography` |
| **Revision Cycle** | Amendment 1 (Incorporates Non-Blocking Preservation Principle, three-product architecture, calibrated evidence findings, policy-dependent projections, refined polarity, and decoupled execution increments) |
| **Creation Date** | 2026-11-10 |
| **Target Milestones** | Initiative 1: Documentation Integrity & English Migration (Pre-v1 Polish); Initiative 2: Post-v1 Phase D0 Bibliographic Evidence Pilot |
| **Governing Rules** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Document Language** | English (per repository policy; raw source citations preserved verbatim) |

---

> [!WARNING]
> **Architectural Proposal Notice (Awaiting Human Approval)**
> This document is a bounded evolution proposal submitted to the repository maintainers and scientific lead.
> In accordance with [`AGENTS.md`](../../AGENTS.md) (§1.1, §2):
> 1. This proposal **does NOT constitute authorization** to edit existing code, alter schemas, migrate files, execute database queries, or contact external services.
> 2. Acceptance of this proposal does not imply approval of downstream metric engines or unreviewed machine-learning classifications.
> 3. All operational actions must proceed through discrete, independently reviewable specification-driven batches governed by explicit human decision gates.

---

## Executive Summary

This proposal outlines a bounded, coordinated strategy to evolve the `mfp-bibliography` repository along two strictly decoupled tracks:

1. **Initiative 1 (Public-Facing Documentation Organization & English Migration)**:
   A lightweight, low-risk documentation remediation program that eliminates entry-point contradictions, repairs 5 broken internal links, updates obsolete candidate version references (`v0.2.0` $\to$ `v0.3.0`), translates isolated Catalan sentences in public guides, indexes all 28 repository scripts and 6 formal JSON schemas, and prepares for the safe, section-mapped archival of historical Spanish and Catalan research proposals (`docs/roadmap/01-07`, `docs/roadmap/core/`) into `docs/archive/` with standardized English warning banners. This initiative touches **zero code, zero schemas, and zero data files**, and requires no dependencies on bibliographic feature development.

2. **Initiative 2 (Bibliographic Evidence Pilot)**:
   A specification-driven, offline-first pilot establishing an auditable relation model that links dataset-methodology literature, source-native citations, discrete protein functional claims, and reviewed primary experimental evidence. Grounded in the four prerequisite conditions of accepted [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), this initiative adopts the **Non-Blocking Preservation Principle**, decouples repository data into three distinct products (Source Inventory, Analytical Views, Locally Curated Subsets), enforces strict polarity handling, establishes an assisted-processing policy for non-deterministic tooling, and executes an initial 3-publication empirical trial. It introduces **no new database servers, no graph infrastructure, and no network dependencies**, operating strictly on tabular CSVs and Draft 2020-12 JSON schemas.

---

## Section A: Current Baseline

### A.1 Working Tree State & Repository Verification

A static inspection of `mfp-bibliography` established the following empirical baseline:

- **Current Branch**: `feature/functional-normalization` (tracking `origin/feature/functional-normalization` at commit `a6def6fef01f345f38532d30779d5b576b079580`).
- **HEAD Commit**: `a6def6f` (`Add functional tests for MultitaskProtDB-II claims and coverage schemas`, committed 2026-11-06 20:04:28 +0100 by `alexdorocode <alexdoro2024@gmail.com>`).
- **Repository Verification Status**:
  * Packaging and cryptographic verification: `PYTHONPATH=src python3 scripts/package_catalog_candidate.py --verify-package` passes cleanly with exit code 0 against candidate `v0.3.0` ([`releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)).
  * Structural verification: `PYTHONPATH=src python3 scripts/validate_repository.py` passes all 9 checks (directory layout, manifest hashes, and schema syntaxes).
  * Executable contract test suite: 193 passing contract and adapter tests across functional normalization suites.

### A.2 Working Tree Modifications and Untracked Work

The audit report [`docs/audits/documentation-audit-2026-11-09.md`](../audits/documentation-audit-2026-11-09.md) provides snapshot evidence from 2026-11-09. Static inspection reveals that the active working tree contains:

- **Tracked Working-Tree Modifications (11 files)**:
  1. `data/curated/functional_coverage.schema.json`: Added nullability for `protein_id` when `coverage_status == "unresolved_identity"`.
  2. `specs/functional-normalization-pilot/plan.md`: Updated Stage P2 Multitask and Stage P3 PlantMP adapter statuses.
  3. `specs/functional-normalization-pilot/spec.md`: Refined dimensional analysis, schema nullability rules, and 6 epistemological levels.
  4. `specs/functional-normalization-pilot/tasks.md`: Marked TASK-01, TASK-02, TASK-03, and TASK-04 completed; retaining unauthorization for subsequent tasks.
  5. `specs/functional-normalization-pilot/verification.md`: Logged checks DOC-CHK-01..06, Multitask slice verification, and PlantMP adapter test logs.
  6. `src/mfp_bibliography/functional_claims_multitask.py`: Core MultitaskProtDB-II adapter parsing GO annotations, references, and total ordering.
  7. `tests/fixtures/functional_claims_multitask/README.md`: Fixture documentation for real and synthetic extracts.
  8. `tests/fixtures/functional_claims_multitask/multitask_real_extract.csv`: 6-record slice extract from raw `proteins.csv`.
  9. `tests/fixtures/functional_claims_multitask/multitask_synthetic_edge_cases.csv`: Edge-case fixture for unlinked annotations and parsing errors.
  10. `tests/test_functional_claims_multitask.py`: Unit and regression test suite for Multitask adapter.
  11. `tests/test_functional_contracts.py`: Contract tests updated to validate null `protein_id` handling for unresolved coverage rows.
- **Untracked Working-Tree Files (11 entries)**:
  `data/curated/source_go_annotations.schema.json`, `docs/audits/documentation-audit-2026-11-09.md`, `docs/curation/` (containing `Q9Y3E5_contextual_adjudication_dossier.md`), `docs/reports/multitask-six-record-context-readiness-review.md`, `docs/reports/amendment-report-documentation-and-bibliographic-evolution.md`, this evolution proposal, `scripts/build_multitask_slice.py`, `src/mfp_bibliography/functional_claims_plantmp.py`, `tests/fixtures/functional_claims_plantmp/`, `tests/test_build_multitask_slice.py`, `tests/test_functional_claims_plantmp.py`, `tests/test_source_go_annotations_contract.py`.

> [!NOTE]
> **Authorization Status of Untracked PlantMP Work**:
> While proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) formally remains in `Status: Proposed` (Level 6) in Git, `specs/functional-normalization-pilot/tasks.md#L7-L8` records TASK-04 as authorized and completed. Because formal project management approval external to Git history was not inspectable, the project-level authorization status of TASK-04 is classified as **unknown / unestablished from in-repo governance files**, rather than assumed to be illicit.

### A.3 Existing Capabilities and Reusable Assets

1. **The Immutable Five-Source Catalog Pipeline**:
   - Ingests `MoonDB` (351 rows), `MoonProt` (702 rows), `MultifacetedProtDB` (1,103 rows), `MultitaskProtDB-II` (694 rows), and `PlantMP` (112 rows).
   - Generates 2,962 source records, 2,322 distinct protein entities, and 463 exact-accession merges under deterministic SHA-256 scheme `MFPB_PROTEIN_ID_V1` ([ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)).
   - Enforces coverage-only rows for MoonProt administrative non-proteins (MPIDs 103, 542, 543, 626; [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md)).
   - Verifiable offline via `releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json` and `checksums.sha256`.
2. **Active Specification-Driven Development (SDD) Packages**:
   - [`specs/functional-normalization-pilot/`](../../specs/functional-normalization-pilot/): Establishes contracts for `functional_claims` (relational one-to-many model), `functional_coverage` (denominator accounting), and `source_go_annotations` (explicit GO preservation).
   - Formulates the 6-level epistemological model ([`spec.md#L19-L31`](../../specs/functional-normalization-pilot/spec.md#L19-L31)), strictly separating raw source statements, normalized claims, proposed mappings, external GO annotations, literature evidence, and human curation.
3. **Curation Dossiers & Scientific Reviews**:
   - [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](../curation/Q9Y3E5_contextual_adjudication_dossier.md): Manual evidence curation dossier (`DOSSIER-Q9Y3E5-001`) evaluating human Peptidyl-tRNA hydrolase 2 / Bit1 (`Q9Y3E5`). Contrasts raw database claims against crystallographic data (PDB `1Q7S`, PMID `14660562`) and cellular apoptosis assays (PMID `15006356`).
   - [`docs/reports/multitask-six-record-context-readiness-review.md`](../reports/multitask-six-record-context-readiness-review.md): Scientific review report (`REV-MULTITASK-6REC-001`) evaluating the 6-record MultitaskProtDB-II pilot package against parent raw data, identifying upstream source anomalies (such as row 239 OMIM string and row 55 duplicated citation).
4. **Literature Reference Assets**:
   - `docs/bibliography/`: Contains 20 primary literature reference PDFs (e.g. `gkaa1101.pdf` for MoonProt 3.0, `baz050.pdf` for PlantMP, `gkt1153.pdf` for MoonProt 2014, etc.). Untracked and read-only per boundary rules (no automated PDF parsing).

### A.4 Relationship to ADR-007 and the Functional Pilot

- **ADR-007 Decoupled `mfp_catalog_v1`**:
  Accepted [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) formally descoped Phase D0 (laboratory annotation/evidence contract) and Phase D (bibliographic evidence graph) from `mfp_catalog_v1` so the baseline release could ship independently.
- **ADR-007 Stated Prerequisites for Post-v1 Work**:
  ADR-007 explicitly defined four mandatory conditions for a post-v1 release to incorporate bibliographic relations ([`ADR-007#L37-L52`](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md#L37-L52)):
  1. *Versioned Relation Schema*: Distinguishing protein identity, source record, functional assertion, GO term, reference, and support relation.
  2. *Per-Relation Provenance*: Capturing source system, extraction method, pipeline version, and review status; strictly forbidding promotion of record citations to function support.
  3. *Zero Identifier Invention*: Required IDs (PMID, DOI, GO) must come from sources or validated systems, never fabricated.
  4. *Byte-Stable Reproduction*: Validated via deterministic offline verification gates.
- **Harmony with Proposed ADR-008 and Non-Blocking Ingestion**:
  Proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) establishes an isolated functional normalization pilot on `feature/functional-normalization`, writing to `data/interim/pilot/` and leaving baseline tables immutable.
  Initiative 2 serves as the formal specification and prototype for Phase D0, strictly fulfilling ADR-007's four conditions while ensuring that local bibliographic curation does **NOT** block external annotation ingestion or exploratory analysis.

### A.5 Epistemological Baseline: Facts, Proposals, and Unknowns

| Dimension | Observed Facts (Verified in Code / Files) | Proposals (Designed; Awaiting Approval) | Unknowns (Pending Empirical Resolution) |
|---|---|---|---|
| **Catalog Baseline** | 2,962 records, 2,322 entities, candidate v0.3.0 packaged and verified offline ([`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)). | Promotion of candidate to `mfp_catalog_v1` ([`mfp-catalog-v1-contract-draft.md`](../releases/mfp-catalog-v1-contract-draft.md)). | Upstream retrieval date for raw `MultifacetedProtDB_data.json` remains unknown. |
| **Functional Model** | Stage P2 Multitask slice extracts 12 claims and 45 GO annotations from 6 records ([`data/interim/pilot/multitask_slice/`](../../data/interim/pilot/multitask_slice/)). | Proposed ADR-008 stages P3–P4 (PlantMP, MoonProt, MoonDB adapters; integrated CLI). | Causal breakdown of historical BioData null publication links remains unresolved. |
| **Bibliographic Scope** | Descoped from v1 per accepted ADR-007. Raw sources contain unsegmented citation text and OMIM anomalies. | Conceptual model, Non-Blocking Preservation Principle, 3-product separation, Phase D0 relation schemas. | Full-text redistribution rights and exact licensing boundaries for commercial publisher PDFs. |
| **Documentation State** | 5 broken links; stale v0.2.0 references; contradictory headings in source profiles ([`documentation-audit-2026-11-09.md`](../audits/documentation-audit-2026-11-09.md)). | Decoupled 2-increment plan; section-mapped archival of Spanish dossiers into `docs/archive/`. | Formal approval status of draft research plans in `docs/roadmap/core/`. |
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
│ Increment 2 (DOC-BATCH-001): Broken links & candidate v0.3.0 alignment          │
│ Future Batch 2: Profile harmonization & script/schema index expansion           │
│ Future Batch 3: Section-mapped proposal archival & mojibake duplicate disposal  │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ Independent; no blocking coupling
┌──────────────────────────────────────▼──────────────────────────────────────────┐
│                   INITIATIVE 2: BIBLIOGRAPHIC EVIDENCE PILOT                    │
│                      (Post-v1 Phase D0 SDD Specification)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Scope: SDD Spec under specs/bibliographic-evidence-pilot/, ADR-009, 3-Pub Trial │
│ Risk: Moderate (Data contracts, assisted extraction policies, curation models)  │
│ Increment 1 (PROP-AMEND-001): Amending this evolution proposal document         │
│ Future Gate BIB-G1: Scope ADR-009 -> Gate BIB-G2: Schemas & Offline Tests       │
│ Future Gate BIB-G3: 3-Publication Package Adjudication & Phase D0 Evaluation    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### B.1 Initiative 1: Public-Facing Documentation Organization & English Migration

#### Objectives
1. Eliminate all 5 broken internal markdown links identified in the technical audit.
2. Synchronize all public entry points (`README.md`, `docs/getting-started.md`, `five-source-descriptive-study-plan.md`, `mfp-catalog-v1-contract-draft.md`) to point to current candidate `v0.3.0`, deleting demonstrably obsolete clone caveats.
3. Translate isolated Catalan sentences in public-facing files (e.g. `README.md#L5`) into English.
4. Harmonize source profiles (`multifacetedprotdb.md`, `multitaskprotdb-ii.md`) and implementation roadmap (`mfp-catalog-implementation-plan.md`) to eliminate contradictory "not implemented" banners for fully integrated sources.
5. Create `data/curated/README.md` documenting all 6 formal JSON schemas, and expand `scripts/README.md` to document all 28 scripts.
6. Prepare a section-level recovery map before archiving 13 unapproved Spanish research dossiers (`docs/roadmap/01-07`) and legacy Catalan plans into `docs/archive/`, prepending clear English status banners.
7. Quarantine or dispose of the mojibake duplicate `docs/roadmap/core/experiment_guio_v1.md` after recording character-level encoding equivalence to `experiment_definition.md`.

#### Explicit Non-Goals
- **No archival based solely on language**: Material is organized by current relevance and approval status, not by language. Verbatim source strings and historical Catalan/Spanish records remain preserved.
- **No full translation of unapproved dossiers**: We will **NOT** translate 7,500 lines of unapproved Spanish/Catalan research proposals. Doing so would expend massive effort on material that violates current repository architecture (ADR-001, ADR-007). English status banners and section recovery maps provide complete governance protection.
- **No code changes**: Zero Python scripts or build pipelines will be altered under Initiative 1.

#### Independent Feasibility & Decoupling
Initiative 1 is **100% independent** of any bibliographic modeling. It can proceed immediately without waiting for scientific decisions on bibliography.

### B.2 Initiative 2: Bibliographic Evidence Pilot

#### Objectives
1. Implement Phase D0 requirements defined in [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) by authoring formal SDD specifications and schemas under `specs/bibliographic-evidence-pilot/`.
2. Formulate a relational, typed bibliographic evidence schema linking proteins, source claims, literature publications, evidence codes, and human review decisions.
3. Formally establish the **Non-Blocking Preservation Principle** and three-product architecture.
4. Establish an Assisted Processing Policy governing LLM/parser assistance, ensuring complete model/prompt provenance, copyright protection, source locators, and human curation gates.
5. Execute an offline, byte-reproducible 3-publication empirical trial evaluating one dataset-methodology paper, one experimental paper, and one ambiguous case.

#### Explicit Non-Goals
- **No Graph Database Infrastructure**: No Neo4j, triplestores, RDF frameworks, or SPARQL endpoints. Flat RFC 4180 CSV tables with Draft 2020-12 JSON schemas fully satisfy all relational requirements.
- **No Live Network Scraping**: No automated downloading of paywalled publisher PDFs or automated bypassing of Cloudflare anti-bot challenges.
- **No Metric Calculations or Classifiers**: No Wang/Lin/MBL semantic similarity calculations, and no ML training.
- **No Baseline Mutation**: Catalog release candidate `v0.3.0` and baseline tables remain completely untouched.

---

## Section C: Minimum SDD Document Set

In accordance with [`AGENTS.md`](../../AGENTS.md) (§4), work on these initiatives must be governed by precise specification packages:

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

### C.1 Reuse of Existing Policies & Data Contracts

The SDD document set will strictly reference established canonical specifications without duplication:
- **Authority Hierarchy & Scientific Invariants**: Reference [`AGENTS.md`](../../AGENTS.md) (§2, §5).
- **Raw Immutability & Provenance**: Reference [ADR-002](../decisions/ADR-002-raw-data-immutability.md) and [ADR-003](../decisions/ADR-003-provenance-and-transformations.md).
- **Label Separation**: Reference [ADR-004](../decisions/ADR-004-evidence-label-benchmark-separation.md).
- **Deterministic Entity Identifiers**: Reference [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) (`MFPB_PROTEIN_ID_V1`).
- **Epistemological Levels**: Reference [`specs/functional-normalization-pilot/spec.md#L19-L31`](../../specs/functional-normalization-pilot/spec.md#L19-L31).

---

## Section D: Bibliographic Conceptual Model and Product Architecture

### D.1 The Non-Blocking Preservation Principle

To resolve Finding F-01, repository governance formally establishes:

> [!IMPORTANT]
> **The Non-Blocking Preservation Principle**
> Lack of local bibliographic review does not, by itself, prevent preserving, indexing, querying, or using an external annotation in an explicitly permitted exploratory analysis.
> Inclusion in a locally reviewed subset or reference dataset requires the policy defined for that product and scientific purpose.
> **Preservation is not endorsement.**

#### Boundaries That the Principle Does NOT Override:
1. Rights and access restrictions.
2. Security requirements.
3. Technical integrity checks (e.g. valid syntax, checksums).
4. Semantic exclusions (e.g. negative sets, fabricated GO terms, illegitimate Cartesian product triples).
5. The approved boundaries of the current increment.

#### Raw Preservation Without Schema Rejection:
- Raw preservation does **NOT** require conformance to normalized annotation schemas.
- Records failing normalization, carrying unassigned aspects, or exhibiting syntactic anomalies must remain preserved as raw observations with diagnostics or in quarantine, never discarded silently.

### D.2 Three Decoupled Data Products

Data processed by the repository is partitioned into three distinct products:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ PRODUCT A: SOURCE INVENTORY                                                     │
│ • Preserved raw observations, source records, and external annotations (ALL).  │
│ • Ingestion does NOT require local review; incompleteness explicitly declared.  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ PRODUCT B: ANALYTICAL VIEWS                                                     │
│ • Reproducible selections/projections governed by named, versioned policies.     │
│ • Example: View B1 (EXP Classic BP/MF), View B2 (Exploratory All-Evidence).     │
│ • Pinned by Experiment Manifests guaranteeing auditable reproduction.           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ PRODUCT C: LOCALLY CURATED SUBSET                                               │
│ • Claims and relations directly assessed under an approved curation policy.     │
│ • First-class outcomes: Supported, Refuted (negative), and Disputed/Ambiguous.   │
│ • Corresponds to future MFP_CuratedData without premature renaming.             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

- **Product A (Source Inventory)**: Ingests external annotations (including IEA, raw text statements, external GO terms) with complete provenance and declared limitations. Ingestion requires structural validity, but strictly does not require local paper review.
- **Product B (Analytical Views)**: Slices generated by applying explicit, versioned inclusion policies (e.g. `EXP_CLASSIC_BP_MF_V1`, `ALL_EVIDENCE_EXPLORATORY_V1`). Projections are policy-dependent: multiple annotations are **NOT** automatically merged into a single tuple, nor are citations blindly unioned. Occurrence-level traceability is preserved.
- **Product C (Locally Curated Subset)**: Evaluated claims and evidence relations. Curated outputs must refer to an explicitly approved, versioned curation policy (such as a future formal adoption of [`06_manual_revision_bibliografica.md`](06_manual_revision_bibliografica.md), which currently serves as methodological background). Refutations (`contradicted`) and unresolved cases are first-class curated records.

### D.3 Conceptual Epistemic Decoupling Without Row-Level Redundancy

To prevent collapsing orthogonal concepts without bloating every row of every table, dimensions are assigned to their natural structural entities:

1. **Documentary Artifacts (Publication Records)**:
   - Rights & Accessibility: `metadata_only`, `abstract_available`, `full_text_available`, `inaccessible`, `restricted`.
   - **Legal Precaution**: Fair use is an affirmative legal doctrine/defense, **NOT** an established license or granted permission.
2. **Annotation Occurrences (`source_go_annotations`)**:
   - Provenance (`source_id`, `source_record_id`, `raw_locator`, `extraction_method`).
   - Biological Evidence Type (source-native codes `IDA`, `IEA`, etc., and ECO mappings).
   - Polarity (`qualifier`: `NOT`, `contributes_to`, or positive assertion).
3. **Review Events (Adjudication Ledger)**:
   - Local Review Workflow: `not_reviewed`, `review_in_progress`, `review_completed`.
   - Scientific Assessment: `supported`, `partially_supported`, `contradicted`, `insufficient_evidence`, `not_assessable`.
   - **No Global Disputed Status**: Conflicting review events do not overwrite an annotation's global status to "disputed". Each review event is an immutable historical record ($T_1, T_2$). The analytical policy determines how a view resolves or quarantines conflicts.
4. **Experiment Manifests (Analytical Views)**:
   - Analytical Eligibility: Pinned by inclusion policy, versioned ontology release, and exclusion denominators.

#### Semantic Distinctions in Assessment:
- `not_assessed`: The material/annotation has not been reviewed or evaluated.
- `insufficient_evidence`: The reviewed evidence was inspected, but does not provide sufficient empirical support for the claim.
- `not_assessable`: The accessible material (e.g. an abstract) is structurally incapable of evaluation (e.g. key details are in inaccessible supplementary tables).

### D.4 Refined Polarity Handling

- `NOT` qualifiers must be preserved with `qualifier = "NOT"` and `is_negative = true`.
- **Refinement**: `NOT` is excluded specifically from **positive-association aggregations**, not from every possible polarity-aware analysis. Polarity-aware studies may legitimately query or aggregate negative annotations.
- **Unknown Polarity**: Annotations with lost or unknown qualifiers must **NOT** silently enter positive views; they are quarantined from positive-association analytical views.

### D.5 Annotation Identity and Typed Reference Modeling

- Protein–GO–evidence is a **useful projection**, not a sufficient annotation identity or deduplication key. Multiple independent annotations can exist for the same protein, GO term, and evidence code from different providers (`assigned_by`), different literature references, or different dates.
- **Occurrence Identifiers**: Stable occurrence digests are derived from source provenance and occurrence index, rather than assuming cross-release continuity without a defined identity rule.
- **Typed References**: Supported via explicit namespaces (`pmid:14660562`, `doi:10.1074/...`, `go_ref:0000024`, `reactome:R-HSA-...`). Multiple identifiers denoting the same reference (e.g. PMID and DOI for the same article) must not be counted as multiple independent pieces of evidence.
- **Dataset-Methodology Publications**: While a dataset paper must not be blanket-promoted to all constituent records, it cannot be permanently classified as incapable of claim-level support solely because it describes a dataset. Support must be evaluated from the actual relevant content of the publication.

### D.6 Separation of Co-Annotation from Contextual Relations

In accordance with [`AGENTS.md`](../../AGENTS.md) (§5 invariant 2):
1. **Co-Annotation**: Terms associated with the same entity in a defined snapshot (e.g. Protein P has GO-MF and GO-CC). It represents exploratory set overlap, **NOT** proof of functional linkage.
2. **Candidate Contextual Relation**: An explicit hypothesis connecting function, process, location, and conditions: $\tau = (m, b, c, \text{conditions})$.
3. **Curated Contextual Relation**: Specific connections verified against primary experimental literature demonstrating that function $m$ operates in compartment $c$ during process $b$.
- **Strict Prohibition**: Generating Cartesian-product MF $\times$ BP $\times$ CC combinations as asserted biological relations is forbidden.
- **Partial Observations**: Valid observations do not require all three aspects. MF-only or BP-only observations are fully valid and preserved.
- **Increment Boundary**: Contextual relation synthesis is outside the current pilot. This is an increment boundary, not a permanent rejection; if pursued later, it requires an approved ADR amending repository scope.

---

## Section E: Assisted Processing Policy

### E.1 Access Hierarchy: Metadata vs Abstract vs Full Text

Processing depth must be governed by lawful access:
1. **Tier 1 (Public Metadata)**: Freely retrievable, fully public, zero copyright barrier.
2. **Tier 2 (Public Abstract)**: Indexed in PubMed / Europe PMC. May establish author claims, but can **never** certify physiological sufficiency or gold-standard moonlighting validation.
3. **Tier 3 (Full Text)**: Open Access (CC-BY) full text permits programmatic extraction with exact locators. Paywalled / proprietary text must not be scraped or crawled programmatically; manual reading only.

### E.2 Rights, Licensing, and Artifact Boundaries

1. Commercial publisher PDFs and bulk full texts must **NEVER** be committed to public Git tracking.
2. Public repository artifacts store only canonical identifiers, exact extract locators (`file::section::page::para/fig`), and minimal fair-use quotation fragments ($\le 25$ words) accompanied by structured paraphrase.
3. Local research copies reside in gitignored local paths (e.g. `docs/bibliography/*.pdf`), strictly separated from public releases.

### E.3 Non-Deterministic Generation vs Deterministic Validation

- Non-deterministic generative tools (LLMs) operate only as drafting aids, writing candidate tuples to `data/interim/assisted_staging/` with `status = "provisional_ai_extraction"`.
- Tool, prompt hash, input text hash, and timestamp provenance must be logged.
- Automated CI gates enforce deterministic validation (schemas, regexes, foreign keys).
- **Strict Rule**: Automated extraction is **NEVER** automatically promoted to curated evidence without human review.

---

## Section F: A Three-Publication Pilot

The three target publications are grounded in verified local files and database records:

### Publication 1: Dataset-Methodology Paper
- **Citation**: C. Chen, D. Arighi, L. Lu, K. Chen, M. A. A. Bonde, G. P. Srivastava, C. H. Wu. *"MoonProt 3.0: an update of the moonlighting proteins database."* **Nucleic Acids Research**, 49(D1):D368–D372, January 2021.
- **Identifiers**: PubMed ID `33170273`; DOI `10.1093/nar/gkaa1101`.
- **Local Evidence**: Local copy in `docs/bibliography/gkaa1101.pdf`; cited in [`docs/roadmap/06_manual_revision_bibliografica.md#L651`](06_manual_revision_bibliografica.md#L651).
- **Role in Pilot**: Tests modeling dataset-level publications. Linked to `SRC_MOONPROT` as dataset metadata; prohibited from blanket promotion to individual MoonProt protein claims unless specific experimental content for that claim is demonstrated.

### Publication 2: Primary Experimental Paper
- **Citation**: J. M. de Pereda, W. F. Waas, Y. Jan, E. Ruoslahti, P. Schimmel, and J. Pascual. *"Crystal structure of a human peptidyl-tRNA hydrolase reveals a new fold and suggests basis for a bifunctional activity."* **Journal of Biological Chemistry**, 279(9):8111–8115, February 27, 2004.
- **Identifiers**: PubMed ID `14660562`; DOI `10.1074/jbc.M311449200`; PDB `1Q7S`.
- **Local Evidence**: Verbatim citation in `data/raw/multitaskprotdb-ii/proteins.csv` row 672 for `Q9Y3E5` (PTRH2 / Bit1); documented in [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](../curation/Q9Y3E5_contextual_adjudication_dossier.md).
- **Role in Pilot**: Tests direct experimental support. Peptidyl-tRNA hydrolase activity linked with `support_role = "supports"` (`EXP`), while discussion bifunctionality hypothesis is captured as `support_role = "ambiguous_inference"`, proving discussion inferences are not promoted to experimental proof.

### Publication 3: Ambiguous / Anomalous Source Case
- **Target Record**: *Escherichia coli* DNA polymerase III subunit theta (`P0ABS8`), cataloged in `data/raw/multitaskprotdb-ii/proteins.csv` line 240 and fixture `multitask_real_extract.csv` Row 5.
- **Raw Reference String**: `"HIV-1 and murine leukemia virus infection (omim:600534)"`.
- **Associated Claim**: Inferred homology to ORFan genes: *"Exhibits structural and functional similarities to a family of nucleoid-associated regulatory proteins..."*
- **Role in Pilot**: Tests anomaly handling. Pipeline parses record without crashing, preserves raw string in `raw_reference_text`, flags `reference_status = "corrupted_source_reference"`, marks `claim_status = "ambiguous"`, and strictly refuses to fabricate a fake PMID.

---

## Section G: Execution Proposal

Execution is partitioned into small, independently reviewable increments with strict boundaries.

### G.1 Decoupled Immediate Increments

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ INCREMENT 1: PROPOSAL AMENDMENTS (PROP-AMEND-001)                               │
│ • Target: docs/roadmap/bounded-evolution-proposal-documentation-and-...md       │
│ • Scope: Incorporate Non-Blocking Principle, 3 products, calibrated findings    │
│ • Write Boundary: 1 file only. Zero code, schema, data, or release changes.     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT 2: ENTRY-POINT & BROKEN LINK REPAIR (DOC-BATCH-001)                   │
│ • Target: 9 declared documentation files only.                                  │
│ • Scope: Repair 5 broken links; translate README line 5; candidate v0.3.0 links │
│ • Write Boundary: 9 files only. Zero code, schema, data, or release changes.     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ FUTURE BATCHES (Subject to separate authorizations):                            │
│ • Batch 2: Catalog governance, source profiles, script/schema index expansion   │
│ • Batch 3: Section-mapped proposal archival & mojibake duplicate disposal       │
│ • Batch 4: Phase D0 Bibliographic SDD package & 3-publication trial             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### G.2 Verifiable Determinism Over Absolute Guarantees

In accordance with scientific software engineering principles:
- Absolute byte-identical reproduction guarantees across unpinned environments are unmaintainable.
- Instead, the repository enforces **verifiable requirements for explicitly deterministic artifacts**:
  * Catalog candidate packages are pinned by SHA-256 manifests (`MANIFEST.json`, `checksums.sha256`) and verified offline via `python3 scripts/package_catalog_candidate.py --verify-package`.
  * Analytical views are pinned by **Experiment Manifests** defining consumed input snapshot digests, ontology versions, curation snapshot commits, and inclusion policy digests.
  * Pinned execution dependencies are declared in `pyproject.toml` (Python $\ge 3.11$, `jsonschema>=4.22.0`).

### G.3 Documentation Safeguards & Mojibake Duplicate Audit Record

1. **Section-Level Recovery Mapping**: Prior to any future archival of Spanish dossiers `docs/roadmap/01-07`, an approved section recovery map must trace which mathematical and curation protocols will be synthesized into English canonical guides.
2. **Audit Record for Mojibake Duplicate**:
   - Original file: `docs/roadmap/core/experiment_guio_v1.md` (SHA-256: `be805e5c4090e371e4fd3a07b2469efdb01934a627db17fecf69b9b1910d4556`, 59,646 bytes, 874 lines).
   - Canonical retained file: `docs/roadmap/core/experiment_definition.md` (SHA-256: `4cd8569b20eccd796551498d2b4f2f4af5bf4a5a5ab814143082a17c967ce557`, 58,871 bytes, 874 lines).
   - Encoding repair transformation: Replacing double UTF-8 / Latin-1 sequences (`â€”` $\to$ `—`, `â€“` $\to$ `–`, `Ã­` $\to$ `í`, `Ã©` $\to$ `é`, `Ã±` $\to$ `ñ`, etc.) results in **100% textual equality** with `experiment_definition.md`.
   - Inbound references: Embedded verbatim in `docs/roadmap/core/experiment-guio-v2.md` Annex 1.
   - **Explicit Caveat**: This character-level comparison proves textual identity after encoding normalization, but does NOT constitute an independent scientific validation of the underlying research proposal.

---

## Concise Approval Checklist

Please review the following decision gates:

- [ ] **1. Authorize Increment 1 (Proposal Amendments)**: Grant authorization to amend this proposal document per the Revision 2 Change Matrix.
- [ ] **2. Authorize Increment 2 (`DOC-BATCH-001`)**: Grant authorization to execute `DOC-BATCH-001-ENTRYPOINT-AND-LINKS` across the 9 declared documentation files.
- [ ] **3. Future Archival Decision Gate**: Retain requirement for section-level recovery mapping and mojibake duplicate disposal audit prior to executing any file moves or deletions.

---
*End of Bounded Evolution Proposal (Amendment 1). Awaiting Maintainer Decision.*
