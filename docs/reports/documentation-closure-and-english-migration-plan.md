# Documentation Closure and English-Language Migration Plan

| Attribute | Specification Record |
|---|---|
| **Document Title** | Documentation Closure and English-Language Migration Plan |
| **Document ID** | `REP-DOC-CLOSURE-ENG-MIGRATION-2026-11-12` |
| **Document Path** | [`docs/reports/documentation-closure-and-english-migration-plan.md`](documentation-closure-and-english-migration-plan.md) |
| **Document Status** | **Approved Planning Deliverable — Bounded Audit and Phased Implementation Plan** |
| **Document Role** | Governance Audit, Language Compliance Inventory, and Phased English Migration Specification |
| **Governing Authority** | [`AGENTS.md`](../../AGENTS.md) Section 3, [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Date** | 2026-11-12 |
| **Closure Verdict** | **NOT READY FOR DOCUMENTATION CLOSURE** (Blocker: Active Master Research Proposal in Catalan) |

---

## 1. Executive Summary & Mandatory Language Policy

### 1.1 Objective and Scope
In accordance with repository governance ([`AGENTS.md`](../../AGENTS.md) Section 3) and the mandate of task `DOC-CLOSURE-AND-ENGLISH-MIGRATION-PLAN-001`, this document establishes the definitive inventory, compliance status, and phased migration roadmap to ensure that **all active, maintained, or updated project documentation is written in English**.

This requirement is mandatory for production and research maintenance. No language exceptions are permitted for active documentation.

### 1.2 The Three Categorical Distinctions of the Language Policy

To balance linguistic accessibility with scientific auditability, the repository enforces three strict distinctions:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    REPOSITORY LANGUAGE COMPLIANCE HIERARCHY                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY A: ACTIVE DOCUMENTATION [MANDATORY ENGLISH]                            │
│   • All explanatory, operational, architectural, and planning documents.       │
│   • INCLUDES ACTIVE PROPOSALS: Being unapproved does not exempt a document.     │
│   • An English status banner does NOT make a non-English active document valid. │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY B: HISTORICAL ORIGINALS [SOURCE LANGUAGE PERMITTED]                    │
│   • Historical source drafts, research notes, and legacy audit artifacts.       │
│   • Permitted to remain in Spanish/Catalan ONLY when retained for provenance.   │
│   • MUST NOT remain the sole active reference for ongoing or future work.       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY C: VERBATIM MATERIAL [STRICT SOURCE PRESERVATION]                      │
│   • Source dataset values, accession IDs, schema fields, code symbols.          │
│   • Exact filenames, historical quotes, and original error logs.                │
│   • Must NEVER be translated or normalized; role clarified via English prose.  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

1. **Category A: Active Documentation (Mandatory English)**:
   - Every document that defines current architecture, guides repository operations, specifies data contracts, or articulates actively maintained future research proposals must be in English.
   - **Active Proposals Included**: A proposal currently under review (such as [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md)) is actively maintained research documentation. Its lack of formal experimental approval does **not** exempt it from English compliance.
   - **Banner Inadequacy**: An English status notice (such as those inserted under `DOC-BANNERS-001`) serves as a transparency alert; it does **not** convert a non-English text into a compliant active document.
   - **No Artificial Reclassification**: An active proposal must never be reclassified as historical solely to avoid the effort of producing an English version.
2. **Category B: Historical Originals (Source Language Retained for Provenance)**:
   - Early Spanish research dossiers (`docs/roadmap/01_dossier_experimento.md` through `07_plan_implementacion_y_validacion.md`) and early Catalan exploratory drafts (`Pla de recerca...md`) may remain in their original language provided their valuable scientific content has been recovered into canonical English reference documents.
   - They serve as immutable documentary records for provenance and historical auditability.
3. **Category C: Verbatim Material (Strict Invariant Preservation)**:
   - Source-native strings, category names (e.g. `confirmed`, `predicted`), database identifiers (`MPID00001`, `Q9Y3E5`), field names (`protein_id`, `aspect`), and exact quoted passages must remain unaltered in their original language and syntax.

### 1.3 Formal Closure Verdict
- **Verdict**: **NOT READY FOR FINAL DOCUMENTATION CLOSURE**.
- **Identified Blocker**: The active master research proposal ([`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md), v0.2.1, 2026-11-06) is written in Catalan. Because it remains an active proposal under review governing the experimental roadmap (PEC-EXP-001), repository rules mandate that an authoritative English successor be established before closure can be declared.

---

## 2. Working Tree Baseline and Preservation State

In accordance with Section 3 of `AGENTS.md`, this review was conducted in strictly read-only mode. The repository baseline at the time of evaluation is recorded below:

- **Git Branch**: `feature/functional-normalization`
- **HEAD Commit**: `6b76dd08d96c89f5b4fea7e7916bee16569eecd7`
- **Staged Changes**: `0` files staged (`git diff --cached` is empty).
- **Tracked Modifications (32 files)**:
  - *Documentation Entry Points & Batches*: [`README.md`](../../README.md), [`data/curated/README.md`](../../data/curated/README.md), [`scripts/README.md`](../../scripts/README.md), [`docs/source-profiles/`](../source-profiles/) (`moondb.md`, `multifacetedprotdb.md`, `multitaskprotdb-ii.md`, `plantmp.md`), [`docs/acquisition-protocols/moonprot.md`](../acquisition-protocols/moonprot.md).
  - *Maintenance & Analysis Drafts*: [`docs/canonical-schema.md`](../canonical-schema.md), [`docs/getting-started.md`](../getting-started.md), [`docs/analysis/five-source-descriptive-study-plan.md`](../analysis/five-source-descriptive-study-plan.md), [`docs/maintenance/`](../maintenance/) (`biodata-snapshot-and-restore-guide.md`, `technical-maintenance-guide.md`), [`docs/releases/mfp-catalog-v1-contract-draft.md`](../releases/mfp-catalog-v1-contract-draft.md).
  - *Governing Roadmaps*: [`docs/roadmap/mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md), [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md).
  - *Historical Roadmaps & Proposals (English Banners Inserted)*: [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) through [`07_plan_implementacion_y_validacion.md`](../roadmap/07_plan_implementacion_y_validacion.md), [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md), [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md), [`docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`](../roadmap/core/Pla%20de%20recerca%20de%20l'experiment%20sobre%20MFPData.md).
  - *Functional Normalization Pilot Slices (Code, Tests, Specs)*: [`specs/functional-normalization-pilot/`](../../specs/functional-normalization-pilot/) (`plan.md`, `tasks.md`, `verification.md`), [`src/mfp_bibliography/functional_claims_moonprot.py`](../../src/mfp_bibliography/functional_claims_moonprot.py), [`tests/test_functional_claims_moonprot.py`](../../tests/test_functional_claims_moonprot.py), [`tests/fixtures/functional_claims_multitask/README.md`](../../tests/fixtures/functional_claims_multitask/README.md).
- **Untracked Artifacts (9 files)**:
  - *Recovered English Canonical Documentation*: [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md), [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md), [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md).
  - *Navigation Directory Indexes*: [`docs/architecture/README.md`](../architecture/README.md), [`docs/curation/README.md`](../curation/README.md).
  - *Audit & Reconciliation Reports*: [`docs/reports/documentation-recovery-map.md`](documentation-recovery-map.md).
  - *Functional Pilot Pipelines & Fixtures*: [`scripts/build_functional_claims_pilot.py`](../../scripts/build_functional_claims_pilot.py), [`tests/test_functional_pilot_pipeline.py`](../../tests/test_functional_pilot_pipeline.py), [`tests/fixtures/functional_claims_moonprot/synthetic_mpid_909_malformed_markup_functions_with_go.html`](../../tests/fixtures/functional_claims_moonprot/synthetic_mpid_909_malformed_markup_functions_with_go.html).

---

## 3. Comprehensive Repository Documentation Inventory and Language Classification

An exhaustive scan across all 79 authored Markdown files in the repository (excluding `.git/`, `.venv/`, `.pytest_cache/`, and raw data dumps in `data/raw/`) evaluated each document against its operational role, maintenance status, and language compliance:

| Repository-Relative Path | Documentary Role & Level | Maintenance Status | Primary Language | Compliance Classification | Required Action |
|---|---|---|---|---|---|
| [`README.md`](../../README.md) | Root Index & Overview (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`AGENTS.md`](../../AGENTS.md) | Operational Governance (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`CHANGELOG.md`](../../CHANGELOG.md) | Release History (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | Contributor Guide (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`SECURITY.md`](../../SECURITY.md) | Security Policy (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/project-charter.md`](../project-charter.md) | Project Governance (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/data-governance.md`](../data-governance.md) | Data Governance (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/release-policy.md`](../release-policy.md) | Release Policy (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/source-policy.md`](../source-policy.md) | Source Policy (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/source-claim-policy.md`](../source-claim-policy.md) | Source Claim Policy (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/source-claims-contract.md`](../source-claims-contract.md) | Data Contract (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/source-catalog.md`](../source-catalog.md) | Catalog Registry (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/canonical-schema.md`](../canonical-schema.md) | Data Contract (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/effective-status-contract.md`](../effective-status-contract.md) | Data Contract (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/reconciliation-baseline-contract.md`](../reconciliation-baseline-contract.md) | Data Contract (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/getting-started.md`](../getting-started.md) | User Guide (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/decisions/ADR-001`](../decisions/ADR-001-repository-scope.md) to [`ADR-008`](../decisions/ADR-008-functional-normalization-pilot-scope.md) | Architectural Decisions (Level 1) | Active / Maintained | English | Compliant | No change required. |
| [`docs/architecture/README.md`](../architecture/README.md) | Directory Hub (Level 3) | Active / Maintained | English | Compliant | No change required. |
| [`docs/architecture/data-flow.md`](../architecture/data-flow.md) | Technical Architecture (Level 3) | Active / Maintained | English | Compliant | No change required. |
| [`docs/architecture/requirements-traceability.md`](../architecture/requirements-traceability.md) | Technical Architecture (Level 3) | Active / Maintained | English | Compliant | No change required. |
| [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) | Explanatory Reference (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) | Proposed Analytical Design (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/curation/README.md`](../curation/README.md) | Directory Hub (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) | Proposed Procedure (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](../curation/Q9Y3E5_contextual_adjudication_dossier.md) | Exemplar Dossier (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/source-profiles/`](../source-profiles/) (`moondb`, `plantmp`, etc.) | Source Documentation (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/acquisition-protocols/`](../acquisition-protocols/) (`moonprot`, etc.) | Acquisition Protocols (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/analysis/five-source-descriptive-study-plan.md`](../analysis/five-source-descriptive-study-plan.md) | Descriptive Study Plan (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/maintenance/`](../maintenance/) (`biodata`, `technical`) | Operations Guides (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/releases/`](../releases/) (`v0.1`, `v0.2.0`, `v0.3.0`, `v1-contract`) | Release Candidates (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`docs/reports/documentation-recovery-map.md`](documentation-recovery-map.md) | Recovery Map & Audit (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/reports/amendment-report-*.md`](amendment-report-documentation-and-bibliographic-evolution.md) | Governance Audit (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/roadmap/mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md) | Approved Plan (Level 4) | Active / Maintained | English | Compliant | No change required. |
| [`docs/roadmap/bounded-evolution-proposal-*.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) | Evolution Proposal (Level 6) | Active / Maintained | English | Compliant | No change required. |
| [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) | Historical Dossier (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/02_protocolo_cientifico_y_analisis.md`](../roadmap/02_protocolo_cientifico_y_analisis.md) | Historical Protocol (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/03_contrato_datos_y_recursos.md`](../roadmap/03_contrato_datos_y_recursos.md) | Historical Contract (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) | Historical Specification (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md) | Historical Annex (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/05_diseno_tecnico.md`](../roadmap/05_diseno_tecnico.md) | Historical Technical Plan (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/06_manual_revision_bibliografica.md`](../roadmap/06_manual_revision_bibliografica.md) | Historical Manual (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/07_plan_implementacion_y_validacion.md`](../roadmap/07_plan_implementacion_y_validacion.md) | Historical Plan (Level 6) | Historical Original | Spanish | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/core/Pla de recerca...md`](../roadmap/core/Pla%20de%20recerca%20de%20l'experiment%20sobre%20MFPData.md) | Historical Plan v0.1 (Level 6) | Historical Original | Catalan | Compliant Historical | Retain intact; candidate for later archival. |
| [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) | Historical Predecessor (Level 6) | Historical Original | Spanish / English | Compliant Historical | Retain intact; clean historical baseline. |
| [`docs/roadmap/core/experiment_guio_v1.md`](../roadmap/core/experiment_guio_v1.md) | Defective Duplicate (Level 6) | Defective Duplicate | English / Mojibake | Quarantined Duplicate | Relocate to quarantine under Gate G4. |
| [`docs/roadmap/core/guion_propuesta.md`](../roadmap/core/guion_propuesta.md) | Slide Storyboard (Level 6) | Historical Original | Spanish | Compliant Historical | Consolidate in presentation folder. |
| [`docs/roadmap/core/presentation/decisiones_abiertas.md`](../roadmap/core/presentation/decisiones_abiertas.md) | Rehearsal Notes (Level 6) | Historical Original | Spanish | Compliant Historical | Retain in presentation folder. |
| **[`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md)** | **Master Research Proposal (Level 6)** | **Active Proposal Under Review** | **Catalan** | **NON-COMPLIANT ACTIVE DOCUMENT** | **Produce English Successor (`ENG-MIG-001`).** |
| [`docs/audits/MFP_DATA_AUDITABILITY_MATRIX.md`](../audits/MFP_DATA_AUDITABILITY_MATRIX.md) | Legacy Audit (Level 6) | Historical Evidence | Catalan | Historical Evidence | Retain intact as snapshot collateral. |
| [`docs/audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md`](../audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md) | Legacy Audit (Level 6) | Historical Evidence | Catalan | Historical Evidence | Retain intact as snapshot collateral. |
| [`docs/experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md`](../experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md) | Early MVP Roadmap (Level 6) | Historical Original | Catalan | Historical Original | Retain intact as snapshot collateral. |
| [`scripts/README.md`](../../scripts/README.md) | Script Directory Index (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`data/*/README.md`](../../data/raw/README.md) (7 files) | Data Directory Indexes (Level 2) | Active / Maintained | English | Compliant | No change required. |
| [`releases/*/README.md`](../../releases/mfp-catalog-candidate-v0.3.0/README.md) (4 files) | Candidate Catalogs (Level 2) | Packaged Candidate | English | Compliant | No change required. |
| [`specs/functional-normalization-pilot/`](../../specs/functional-normalization-pilot/) (4 files) | Pilot Specifications (Level 5) | Active / Maintained | English | Compliant | No change required. |
| [`tests/fixtures/*/README.md`](../../tests/fixtures/functional_claims_moonprot/README.md) (5 files) | Test Fixture Guides (Level 5) | Active / Maintained | English | Compliant | No change required. |

---

## 4. Special Case Analysis: The Active Experimental Master Proposal

### 4.1 Epistemic Character of `experiment-guio-v2.md`
[`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md) (Edition 0.2.1, 2026-11-06) is the central master proposal defining the overarching research framework (`PEC-EXP-001`). 

It spans 2,154 lines and organizes the investigation into:
- 1 central research question, 11 secondary questions, and 4 working hypotheses (H1–H4).
- 7 experimental blocks: B0 (Raw & Evidence), B1 (Corpus & Coverage), B2 (Evidence Sensitivity), B3 (Functional Divergence), B4 (Function & Compartment), B5 (Reference Proteome Contrast), B6 (Literature Curation).
- 2 exploratory visual extensions: E1 (PCA 3D) and E2 (UMAP 3D).
- 8 deliverable definitions (D0–D7) and 6 decision gates (G0–G5).
- A formalized register of 29 open decisions (`DEC-01` through `DEC-29`).

### 4.2 Overlap Analysis with Existing Canonical English Documents
An analysis of textual and conceptual overlap demonstrates that significant sections of `experiment-guio-v2.md` have already been formalized into canonical English reference documents:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              OVERLAP OF `experiment-guio-v2.md` WITH CANONICAL DOCUMENTS        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ RECOVERED IN CANONICAL ENGLISH DOCUMENTS                                        │
│   • Conceptual Foundations & Boundaries ──► docs/architecture/scientific-      │
│     (Epistemic limits, homology lag)        background.md                       │
│   • Blocks B3 & B4 (Semantic Dissimilarity) ► docs/architecture/go-metrics-     │
│     (MBL, IC, Wang, Lin, NPMI, DEC-08..20)   specification.md                   │
│   • Block B6 (Literature Curation Protocol) ► docs/curation/literature-         │
│     (Evidentiary units, blinding, DEC-24..29)curation-manual.md                 │
│   • Block B0 (Entity Packaging & Digests) ──► Candidate Catalog v0.3.0 &        │
│     (Deterministic IDs, raw freezing)        specs/functional-normalization/    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ UNIQUE UNTRANSLATED CONTENT REQUIRING ENGLISH SUCCESSOR                         │
│   • Block B1: Corpus contrast & five-source catalog concordance rules.          │
│   • Block B2: Evidence robustness stratification & repeated downsampling.       │
│   • Block B5: Reference proteome comparison & GeOKG metric complementarity.     │
│   • Extensions E1 & E2: PCA 3D and UMAP 3D visual projection designs.           │
│   • Statistical Analysis Plan: Paired differences, complete coverage policies.   │
│   • Software Responsibilities & Execution Run Manifests.                        │
│   • Deliverable Matrix (D0–D7), Gate Definitions (G0–G5), Decision Map.         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Structural Strategy: Modular Synthesis vs Historical Annex Bloat
A major discovery of this audit is that **1,235 lines (57.3%) of `experiment-guio-v2.md` consist of embedded historical annexes**:
- **Annex A (lines 926–1803, 878 lines)**: An embedded verbatim copy of the earlier bilingual/Spanish draft `experiment_definition.md` (`experiment_guio_v1.md`).
- **Annex B (lines 1804–2154, 351 lines)**: An embedded verbatim copy of the early Catalan research plan `Pla de recerca de l'experiment sobre MFPData.md`.

**Strategic Recommendation**:
1. **Do NOT translate or replicate Annexes A and B** into the active English master proposal. Translating obsolete historical drafts would bloat the proposal and recreate redundant maintenance overhead.
2. The active English successor must retain **traceable Markdown hyperlinks** to the physical original files (`experiment_definition.md` and `Pla de recerca...md`), explicitly noting their historical provenance.
3. The active English successor should be structured as a **self-contained executive research proposal**:
   - It will directly specify the experimental architecture, block progression (B0–B6), statistical contracts, and decision gates.
   - For granular mathematical derivations (MBL/Lin/Wang/NPMI) and curatorial workflows, it will reference [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) and [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md), preventing conflicting duplicates.

### 4.4 Proposed English Successor Path and Metadata
- **Proposed English Path**: `docs/roadmap/core/experimental-master-proposal.md` [Proposed English Successor]
- **Document Title**: *Experimental Master Proposal: Multi-Source Evidence Concordance, Functional Dissimilarity, and Literature Adjudication Framework (PEC-EXP-001)*
- **Document Role**: Active Master Research Proposal Under Review (Level 6 Proposal).
- **Epistemic Invariant**: The English document must preserve all proposed, unapproved, and tentative statements as such. It must **not** silently approve the research programme or imply that metric computation engines belong in the baseline catalog repository.

---

## 5. Bounded Documentation-Closure Check

### 5.1 Navigation Integrity
- Root [`README.md`](../../README.md) provides a concise navigation hub directing users to directory READMEs in [`docs/architecture/`](../architecture/README.md) and [`docs/curation/`](../curation/README.md).
- All three recovered canonical documents ([`scientific-background.md`](../architecture/scientific-background.md), [`literature-curation-manual.md`](../curation/literature-curation-manual.md), [`go-metrics-specification.md`](../architecture/go-metrics-specification.md)) are prominently discoverable with unambiguous status badges.
- **Closure Finding**: Navigation is compliant for existing English assets; will require linking `experimental-master-proposal.md` once produced.

### 5.2 Authority and Status Separation
- Level 1 accepted Architectural Decision Records ([ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)) remain strictly distinguished from Level 1 proposed ADR-008.
- Recovered Level 6 analytical designs and proposed curation protocols are explicitly marked as *proposed designs pending review*, never conflated with implemented capabilities or binding repository standards.
- **Closure Finding**: Fully compliant.

### 5.3 Recovery Completeness
- All 34 items in the [Documentation Recovery Map](documentation-recovery-map.md) have explicit, non-conflated dispositions.
- The evidence code partition gap (`MAP-02-02`) was cleanly resolved under `DOC-EVIDENCE-PARTITIONS-001` by adding §2.5 to [`go-metrics-specification.md`](../architecture/go-metrics-specification.md).
- Status banners have been added to all 8 historical Spanish dossiers and the Catalan drafts under `DOC-BANNERS-001`.
- **Closure Finding**: Fully compliant.

### 5.4 Historical Dependencies
- A critical audit check was performed: *Does any active English document depend on an untranslated historical text for an essential definition, algorithm, or operational procedure?*
- **Finding**: No active operational instructions depend on Spanish/Catalan texts. However, the overarching experimental research programme (`PEC-EXP-001`) as an integrated, multi-block research design currently exists in full detail only in Catalan ([`experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md)). This constitutes the primary remaining substantive dependency blocking documentation closure.

### 5.5 Verification Statements & Pre-Existing Manifest Limitation
- Candidate catalog packaging verification (`package_catalog_candidate.py --verify-package`) executes offline and passes 100% for candidate `v0.3.0` and `v0.2.0`.
- The repository validator (`scripts/validate_repository.py`) passes 9/9 checks.
- **Preserved Known Limitation**: As recorded in prior audits, running the full test suite (`pytest`) encounters an assertion failure in `test_source_claim_policy.py` due to the historical deletion of `data/raw/plantmp/PlantMP MySQL.xlsx` in commit `a6def6f` (2026-11-06) while still referenced in `data/manifests/file_checksums.sha256`. Standing repository governance forbids editing frozen manifests or creating dummy files without explicit authorization. Verification reports accurately separate catalog packaging verification from this isolated test assertion.

---

## 6. Phased English Migration Roadmap

To achieve full documentation closure without disruptive or monolithic PRs, the remaining work is divided into three finely bounded increments:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       PHASED ENGLISH MIGRATION ROADMAP                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT ENG-MIG-001: Active Master Proposal English Successor [CRITICAL PATH] │
│   • Target: Create docs/roadmap/core/experimental-master-proposal.md            │
│   • Content: Translate & synthesize the 36 active Catalan sections of           │
│     experiment-guio-v2.md (L1–L919). Decouple Annexes A/B as linked originals. │
│   • Update banner on experiment-guio-v2.md to note English succession.          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT ENG-MIG-002: Historical Collateral Notices & Consistency [ADVISORY]   │
│   • Target: docs/audits/ (MFP_DATA_AUDITABILITY_MATRIX, EXTRACTION_UNIFICATION) │
│     and docs/experiments/ (MFP_BIBLIOGRAPHIC_MVP_ROADMAP).                      │
│   • Content: Add brief English historical provenance banners to early 2026-10-14│
│     Catalan audit artifacts confirming their status as frozen snapshot records. │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT ENG-MIG-003: Final Navigation Alignment & Closure Declaration         │
│   • Target: README.md, docs/architecture/README.md, documentation-recovery-map. │
│   • Content: Link experimental-master-proposal.md as active research proposal;  │
│     declare full repository English compliance.                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Increment ENG-MIG-001: Active Master Proposal English Successor
- **Target File to Create**: `docs/roadmap/core/experimental-master-proposal.md` [Proposed]
- **Target File to Edit**: [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md) (update status banner to cite English successor).
- **Scope & Method**:
  - Full faithful English translation of lines 1–919 of `experiment-guio-v2.md` (the core research design).
  - Decouple Annexes A and B: replace 1,235 lines of embedded duplicate text with traceable links to `experiment_definition.md` and `Pla de recerca...md`.
  - Preserve exact IDs for blocks (B0–B6), gates (G0–G5), deliverables (D0–D7), hypotheses (H1–H4), and decisions (`DEC-01`–`DEC-29`).
  - Cross-reference `go-metrics-specification.md` and `literature-curation-manual.md` for shared technical formulas.
- **Acceptance Criteria**: All explanatory prose in English; zero missing research questions or block specifications; 100% relative link resolution offline.

### 6.2 Increment ENG-MIG-002: Historical Collateral Notices
- **Target Files to Edit**:
  - `docs/audits/MFP_DATA_AUDITABILITY_MATRIX.md`
  - `docs/audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md`
  - `docs/experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md`
- **Scope & Method**: Add standard English historical notices confirming their status as frozen 2026-10-14 audit collateral supporting the BioData restore guide. Body prose remains unchanged.
- **Acceptance Criteria**: English notices present; body content untouched.

### 6.3 Increment ENG-MIG-003: Final Navigation Alignment & Closure Declaration
- **Target Files to Edit**:
  - [`README.md`](../../README.md)
  - [`docs/architecture/README.md`](../architecture/README.md)
  - [`docs/reports/documentation-recovery-map.md`](documentation-recovery-map.md)
- **Scope & Method**: Link `experimental-master-proposal.md` in root and architecture indexes; update recovery map to reflect completion of English migration; issue formal closure declaration.
- **Acceptance Criteria**: Zero broken links; zero unindexed active documents.

---

## 7. Optional Archival Relocation Plan (Deferred Execution)

When repository maintainers formally authorize physical archival of historical drafts, the following relocations should be executed under a dedicated increment (`DOC-ARCHIVE-EXEC-001`):

| Current Repository Path | Proposed Archival Destination | Inbound Links to Update | Relative Internal Links Requiring Adjustment |
|---|---|---|---|
| `docs/roadmap/01_dossier_experimento.md` | `docs/archive/proposals-2026-10-spanish/01_dossier_experimento.md` | `documentation-recovery-map.md`, `scientific-background.md` | `../architecture/` $\to$ `../../architecture/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/02_protocolo_cientifico_y_analisis.md` | `docs/archive/proposals-2026-10-spanish/02_protocolo_cientifico_y_analisis.md` | `documentation-recovery-map.md`, `go-metrics-specification.md` | `../architecture/` $\to$ `../../architecture/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/03_contrato_datos_y_recursos.md` | `docs/archive/proposals-2026-10-spanish/03_contrato_datos_y_recursos.md` | `documentation-recovery-map.md`, `specs/.../spec.md` | `../decisions/` $\to$ `../../decisions/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/04_especificacion_metricas.md` | `docs/archive/proposals-2026-10-spanish/04_especificacion_metricas.md` | `documentation-recovery-map.md`, `go-metrics-specification.md` | `../architecture/` $\to$ `../../architecture/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/04a_asociaciones_interaspecto.md` | `docs/archive/proposals-2026-10-spanish/04a_asociaciones_interaspecto.md` | `documentation-recovery-map.md`, `go-metrics-specification.md` | `../architecture/` $\to$ `../../architecture/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/05_diseno_tecnico.md` | `docs/archive/proposals-2026-10-spanish/05_diseno_tecnico.md` | `documentation-recovery-map.md`, `data-flow.md` | `../architecture/` $\to$ `../../architecture/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/06_manual_revision_bibliografica.md` | `docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md` | `documentation-recovery-map.md`, `literature-curation-manual.md` | `../curation/` $\to$ `../../curation/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/07_plan_implementacion_y_validacion.md` | `docs/archive/proposals-2026-10-spanish/07_plan_implementacion_y_validacion.md` | `documentation-recovery-map.md`, `specs/.../plan.md` | `../../specs/` $\to$ `../../../specs/`, `../reports/` $\to$ `../../reports/` |
| `docs/roadmap/core/Pla de recerca...md` | `docs/archive/proposals-2026-10-catalan/Pla_de_recerca_MFPData.md` | `documentation-recovery-map.md`, `experiment-guio-v2.md` | `../../architecture/` $\to$ `../../../architecture/` |
| `docs/roadmap/core/experiment-guio-v2.md` | `docs/archive/proposals-2026-11-catalan/experiment-guio-v2.md` *(post-migration)* | `documentation-recovery-map.md`, `experimental-master-proposal.md` | `../../architecture/` $\to$ `../../../architecture/` |
| `docs/roadmap/core/experiment_guio_v1.md` | `docs/archive/quarantine/experiment_guio_v1.md` *(Gate G4)* | `documentation-recovery-map.md`, `bounded-evolution-proposal-*.md` | Isolate duplicate; zero outbound links needed. |

> [!IMPORTANT]
> **Archival Execution Prohibited in this Increment**:
> The table above is a preparatory planning mapping. In accordance with task constraints, **no files have been moved, renamed, deleted, or quarantined**.

---

## 8. Git Staging and Consolidation Plan

The working tree currently contains 42 modified or untracked files accumulated across multiple documentation recovery passes and the functional normalization pilot. To ensure atomic, auditable commits, the following five reviewable commit packages are proposed:

### Commit Group 1: Documentation Entry Points & Directory Navigation
- **Paths**:
  - `README.md`
  - `docs/architecture/README.md`
  - `docs/curation/README.md`
  - `data/curated/README.md`
  - `scripts/README.md`
- **Scope**: Clean navigation hubs, directory indices, and role badges.

### Commit Group 2: Canonical English Architecture & Curation Documents
- **Paths**:
  - `docs/architecture/scientific-background.md`
  - `docs/architecture/go-metrics-specification.md`
  - `docs/curation/literature-curation-manual.md`
- **Scope**: Recovered canonical English specifications for scientific foundations, semantic dissimilarity metrics, and literature adjudication.

### Commit Group 3: Documentation Recovery Map & Governance Planning Reports
- **Paths**:
  - `docs/reports/documentation-recovery-map.md`
  - `docs/reports/documentation-closure-and-english-migration-plan.md`
- **Scope**: Auditable recovery inventory and English migration roadmap.

### Commit Group 4: Historical Status Notices on Legacy Roadmaps
- **Paths**:
  - `docs/roadmap/01_dossier_experimento.md` through `07_plan_implementacion_y_validacion.md`
  - `docs/roadmap/04a_asociaciones_interaspecto.md`
  - `docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`
  - `docs/roadmap/core/experiment-guio-v2.md`
- **Scope**: Insertion of document-specific English status banners.

### Commit Group 5: Functional Normalization Pilot Code, Tests & Specifications
- **Paths**:
  - `specs/functional-normalization-pilot/plan.md`, `spec.md`, `tasks.md`, `verification.md`
  - `src/mfp_bibliography/functional_claims_moonprot.py`
  - `scripts/build_functional_claims_pilot.py`
  - `tests/test_functional_claims_moonprot.py`
  - `tests/test_functional_pilot_pipeline.py`
  - `tests/fixtures/functional_claims_moonprot/...`
  - `tests/fixtures/functional_claims_multitask/README.md`
- **Scope**: Tier 3 experimental pilot code and unit test suite.

> [!NOTE]
> **No Git Operations Performed**: In accordance with task rules, no files were staged, committed, stashed, or reset.

---

## 9. Final Closure Verification Checklist

The criteria for declaring final documentation closure for the repository are summarized below:

- [x] All general explanatory and operational documentation is in English.
- [ ] **All active proposals are in English** *(Blocked by `experiment-guio-v2.md`; will be resolved by `ENG-MIG-001`)*.
- [x] Historical non-English originals are clearly identified with English status notices.
- [x] Technical literals and verbatim source strings remain faithfully preserved.
- [x] Current implementation, experimental pilots, and proposed designs are strictly distinguished.
- [x] Navigation points to canonical English references without competing indexes.
- [x] Recovery dispositions and open governance gates are explicit.
- [x] Internal links and section anchors resolve offline without broken references.

---

## 10. Documentation Closure Verification and Formal Outcome (ENG-MIG-003)

**Date**: 2026-11-12  
**Evaluation Scope**: Verification of English successor migration, navigation alignment, metadata and decision reconciliation, and conditional documentation closure.

### 10.1 English Successor Path and Documentary Role
- **Path**: [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md)
- **Framework Identifier**: `PEC-EXP-001` (`DOC-PROPOSAL-PEC-EXP-001-ENG`)
- **Documentary Role**: **Maintained English research proposal under review** (Level 6 Proposal Under Review).
- **Epistemic Invariant**: This document is an active scientific research proposal, **not** an implemented pipeline, binding release contract, or approved experimental policy.
- **Source Preservation**: The Catalan source [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md) is preserved in place for historical provenance, with its English status notice explicitly linking to this maintained English successor.

### 10.2 Navigation Updates Completed
Entry-point indices have been updated to make the maintained English research proposal discoverable while maintaining clear epistemic boundaries:
1. [`README.md`](../../README.md): Added under `## Documentation and Specifications` as `Maintained English research proposal — under review; not an implemented pipeline or approved experimental policy.`
2. [`docs/architecture/README.md`](../architecture/README.md): Added to the document index table and given an overview section (§5) detailing its role, structure, and Level 6 authority status under review.
3. [`docs/reports/documentation-recovery-map.md`](documentation-recovery-map.md): Updated items `MAP-CORE-V2-01` through `MAP-CORE-V2-04` across Table 1 (Inventory) and Table 2 (Reconciled Status Table), distinguishing the maintained English successor from the preserved Catalan source, without altering recovery category totals.
4. **Secondary References**: Added explicit successor links to [`docs/decisions/ADR-008-functional-normalization-pilot-scope.md`](../decisions/ADR-008-functional-normalization-pilot-scope.md) and [`specs/functional-normalization-pilot/verification.md`](../../specs/functional-normalization-pilot/verification.md) while preserving original design provenance and decision content.

### 10.3 Version and Status Reconciliation Outcome
1. **Edition and Version Metadata**:
   - The unsupported "Edition 1.0.0-draft" label was removed.
   - The scientific proposal edition was accurately reconciled to **Edition `0.2.1`** (`2026-11-06`, `PEC-EXP-001`), matching the source proposal.
   - English language migration metadata is recorded separately: *Maintained English Successor (Migrated: 2026-11-12)*.
   - Section 18.1 (Edition History) and Section 19 (Coverage Appendix) were updated accordingly.
2. **Decision and Gate Statuses**:
   - Section 13.2 was reconciled to distinguish:
     - *Gate Definitions*: G0 through G5 defined as structured governance checkpoints for the research workflow.
     - *Prerequisites*: Gate G0 is a mandatory prerequisite that must precede any new experimental computation.
     - *Evidence of Actual Execution*: None of the experimental gates (G0 through G5) have been executed or passed for `PEC-EXP-001`.
     - *Catalog Baseline Distinction*: Baseline operations corresponding to raw file freezing (ADR-002), entity hashing (ADR-005), and candidate v0.3.0 packaging (ADR-006) belong to the accepted catalog baseline, but do not constitute retrospective execution of experimental Gate G1.
   - Section 14 (Decision Register) was reconciled into a 6-column matrix recording `Source Position`, `Source State` (`Proposed`, `Open`, or `Deferred`), `Required by Gate`, and `Relationship to Accepted Repository Baseline`.
   - Specifically reconciled:
     - `DEC-01`: Governed and ratified by accepted [ADR-001](../decisions/ADR-001-repository-scope.md) (classifier training out of scope).
     - `DEC-02`: Governed and ratified by accepted [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) (deterministic entity hashing).
     - `DEC-18`: Governed and ratified by accepted [ADR-002](../decisions/ADR-002-raw-data-immutability.md) (raw artifact immutability).
     - `DEC-27`: Governed by accepted [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md) candidate packaging (composite key unicity).
     - `DEC-17`: Deferred / Out of scope per accepted [ADR-001](../decisions/ADR-001-repository-scope.md).
     - All other experimental decisions (DEC-03..DEC-16, DEC-19..DEC-26, DEC-28..DEC-29) remain open or proposed pending future gate reviews.

### 10.4 Coverage and Language Checks Performed
- **Main-Body Coverage**: All 36 Catalan main-body sections from `experiment-guio-v2.md` (lines 1–919) are faithfully translated and structured in `experimental-master-proposal.md`, as verified in Section 19.
- **Annex Disposition**: Substantive content from historical annexes is decoupled into clean markdown links pointing to existing files (`experiment_definition.md` and `Pla de recerca de l'experiment sobre MFPData.md`), eliminating 1,223 lines of duplicate text bloat while preserving full provenance.
- **Active Language Audit**: Zero active, maintained, or recommended documentation files in the repository contain non-English prose. All historical non-English files are clearly marked with standardized English status notices.
- **Link and Anchor Integrity**: Offline validation verified 0 broken relative links and 0 broken section anchors across all modified and newly created documentation.

### 10.5 Remaining Limitations and Deferred Items
Documentation closure is strictly confined to the agreed documentation and language migration scope. It does **not** imply:
1. **Scientific Approval**: The master research proposal `PEC-EXP-001` remains an unapproved proposal under review; Gate G0 has not been granted.
2. **Pipeline Implementation**: Metric engines, semantic dissimilarity calculations, cross-aspect associations, and embedding manifolds remain unexecuted and descoped from the catalog baseline.
3. **Pre-Existing Manifest Issue**: The pre-existing mismatch regarding `PlantMP MySQL.xlsx` in `file_checksums.sha256` remains untouched in accordance with raw data immutability rules.
4. **Archival and Git Consolidation**: Physical moving of historical dossiers to `docs/archive/` and Git commit staging/consolidation remain optional operational tasks deferred to maintainer discretion under separate authorizations.

### 10.6 Formal Closure Verdict

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENTATION CLOSURE VERDICT                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                    STATUS: READY FOR DOCUMENTATION CLOSURE                      │
│                                                                                 │
│  All active and maintained documentation across the repository is in English.  │
│  The maintained English research proposal is discoverable and reconciled.      │
│  Historical originals are preserved with explicit English status notices.       │
│  Internal links and section anchors resolve offline with zero broken targets.   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

*End of Documentation Closure and English-Language Migration Plan (`REP-DOC-CLOSURE-ENG-MIGRATION-2026-11-12`).*
