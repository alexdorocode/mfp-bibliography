# Section-Level Documentation Recovery and Disposition Map

## Document Control & Governance Metadata

| Attribute | Specification Record |
|---|---|
| **Document Title** | Section-Level Documentation Recovery and Disposition Map: Methodological Synthesis, Linguistic Convergence, and Controlled Archival Phasing |
| **Document ID** | `REP-DOC-RECOVERY-MAP-2026-11-10-REV2` |
| **Document Path** | [`docs/reports/documentation-recovery-map.md`](documentation-recovery-map.md) |
| **Document Authority** | Architectural and Bibliographic Evidence Governance (Advisory Map prior to Migration) |
| **Target Repository** | `mfp-bibliography` (root: `/home/alexdoro/repositories/mfp-bibliography`) |
| **Review Authority** | Senior Scientific-Software Architect & Bioinformatics Provenance Reviewer |
| **Date** | 2026-11-12 (Revision 2 incorporating `DOC-NAV-ALIGN-001` and Bounded Reconciliation Clarifications) |
| **Governing Rules** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Operational Status** | Reconciled recovery map, directory navigation index alignment, and minimal documentation closure plan. |

---

## 1. Baseline and Scope

### 1.1 Verified Repository State & Working-Tree Baseline (as of 2026-11-12)

To prevent architectural conflation with adjacent local repositories (`BioData`, `protein-information-system`, `mfp-dataset-designer`, `protein-embedding-classifier`), this recovery map applies strictly to the filesystem boundary of `mfp-bibliography`:

- **Active Branch**: `feature/functional-normalization` (tracking `origin/feature/functional-normalization`).
- **HEAD Commit**: `6b76dd08d96c89f5b4fea7e7916bee16569eecd7` (`feat: implement MoonProt dynamic block adapter with bounded authorization and detailed outcomes`).
- **Complete Working-Tree Accounting**:
  - **Unstaged Modified Tracked Files (22 files)**:
    - *Documentation and profile batch*: [`README.md`](../../README.md), [`data/curated/README.md`](../../data/curated/README.md), [`docs/acquisition-protocols/moonprot.md`](../acquisition-protocols/moonprot.md), [`docs/analysis/five-source-descriptive-study-plan.md`](../analysis/five-source-descriptive-study-plan.md), [`docs/canonical-schema.md`](../canonical-schema.md), [`docs/getting-started.md`](../getting-started.md), [`docs/maintenance/biodata-snapshot-and-restore-guide.md`](../maintenance/biodata-snapshot-and-restore-guide.md), [`docs/maintenance/technical-maintenance-guide.md`](../maintenance/technical-maintenance-guide.md), [`docs/releases/mfp-catalog-v1-contract-draft.md`](../releases/mfp-catalog-v1-contract-draft.md), [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md), [`docs/roadmap/mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md), [`docs/source-profiles/moondb.md`](../source-profiles/moondb.md), [`docs/source-profiles/multifacetedprotdb.md`](../source-profiles/multifacetedprotdb.md), [`docs/source-profiles/multitaskprotdb-ii.md`](../source-profiles/multitaskprotdb-ii.md), [`docs/source-profiles/plantmp.md`](../source-profiles/plantmp.md), [`scripts/README.md`](../../scripts/README.md).
    - *Functional normalization pilot specifications & code*: [`specs/functional-normalization-pilot/plan.md`](../../specs/functional-normalization-pilot/plan.md), [`specs/functional-normalization-pilot/tasks.md`](../../specs/functional-normalization-pilot/tasks.md), [`specs/functional-normalization-pilot/verification.md`](../../specs/functional-normalization-pilot/verification.md), [`src/mfp_bibliography/functional_claims_moonprot.py`](../../src/mfp_bibliography/functional_claims_moonprot.py), [`tests/fixtures/functional_claims_multitask/README.md`](../../tests/fixtures/functional_claims_multitask/README.md), [`tests/test_functional_claims_moonprot.py`](../../tests/test_functional_claims_moonprot.py).
  - **Untracked Artifacts (9 files)**:
    - *Recovered English canonical reference documents*: [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (302 lines, 37.5 KB, authored 2026-11-10 19:05), [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) (511 lines, 60.6 KB, authored 2026-11-10 19:47), [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (646 lines, 60.8 KB, authored 2026-11-10 20:25).
    - *Directory navigation indexes (Increment DOC-NAV-ALIGN-001)*: [`docs/architecture/README.md`](../architecture/README.md) (authored 2026-11-12), [`docs/curation/README.md`](../curation/README.md) (authored 2026-11-12).
    - *This recovery map*: [`docs/reports/documentation-recovery-map.md`](documentation-recovery-map.md) (authored 2026-11-10 18:19; reconciled and clarified 2026-11-12).
    - *Integrated functional pilot tooling*: `scripts/build_functional_claims_pilot.py` (27.7 KB, authored 2026-11-10 15:03), `tests/test_functional_pilot_pipeline.py` (15.9 KB, authored 2026-11-10 15:03), `tests/fixtures/functional_claims_moonprot/synthetic_mpid_909_malformed_markup_functions_with_go.html` (366 B).
  - **Staged Changes**: None (0 files in index).
  - **Relevant Ignored Artifacts**:
    - `data/interim/pilot/`: Generated empirical pilot tables (`functional_claims_pilot.csv` with 44 claims, `source_go_annotations_pilot.csv` with 353 annotations, `functional_coverage_pilot.csv` with 20 records, `manifest.json`).
    - `data/interim/reports/`: Pilot execution report (`functional_claims_pilot_report.json`).
- **Pre-existing Verification Limitation**: `tests/test_source_claim_policy.py::TestSourceClaimPolicy::test_raw_checksums_unchanged` fails with `FileNotFoundError` because `data/raw/plantmp/PlantMP MySQL.xlsx` was deleted in commit `a6def6f` (2026-11-06) while still listed in `data/manifests/file_checksums.sha256`. However, repository scaffold validation (`validate_repository.py`) passes 9/9 checks, and candidate release verification (`package_catalog_candidate.py --verify-package`) passes 100% offline for both `mfp-catalog-candidate-v0.3.0` and `v0.2.0`.

### 1.2 Purpose of this Recovery Map

Under [`AGENTS.md`](../../AGENTS.md) Section 3, all new technical and scientific documentation in `mfp-bibliography` must be maintained in English. However, Section 2 establishes that non-English proposals and historical dossiers must **never be deleted or discarded based solely on language or approval status**. 

Historical dossiers under `docs/roadmap/` and `docs/roadmap/core/` contain rigorous mathematical formalizations (Wang/Lin semantic distances, NPMI inter-aspect co-occurrences), gold-standard literature review protocols, and valuable biological justifications for decoupling sequence homology from functional divergence. 

This document defines a **section-level recovery, disposition, and reconciliation map** that:
1. Enumerates every file and section across historical roadmaps (18 files).
2. Identifies reusable scientific and curation methodology to be synthesized into English canonical documents (`docs/architecture/`, `docs/curation/`, `docs/analysis/`).
3. Reconciles existing recovery coverage against the three recovered English canonical documents authored on 2026-11-10.
4. Distinguishes obsolete implementation details (such as live database connections, fixed binary 2-facet models, or treating reference databases as negative controls) from enduring scientific principles.
5. Strictly separates content recovery from contract replacement, future proposals, and historical retention, avoiding misleading aggregated completion percentages.
6. Clearly separates accepted governing contracts (ADR-001..007) from proposed specifications (ADR-008).
7. Provides an evidence-based roadmap and minimal closure plan for subsequent phased migration to `docs/archive/` without data, methodology, or link loss.
8. Operates strictly under bounded write limits: **only authorized documentation paths are modified**.

---

## 2. Complete Inspected-File Inventory and Coverage Limitations

### 2.1 Complete File Inventory (18 Files Accounted For)

Rather than assuming shorthand ranges, all 18 files physically present under `docs/roadmap/` and `docs/roadmap/core/` were inspected at the baseline:

| # | Complete Repository-Relative Path | Format / Size | Physical Lines | Language | Authority Level (AGENTS.md) |
|---|---|---|---|---|---|
| 1 | [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) | Markdown (45,816 bytes) | 487 | Spanish | Level 6 (Draft Proposal v0.1) |
| 2 | [`docs/roadmap/02_protocolo_cientifico_y_analisis.md`](../roadmap/02_protocolo_cientifico_y_analisis.md) | Markdown (61,881 bytes) | 569 | Spanish | Level 6 (Draft Proposal v0.1) |
| 3 | [`docs/roadmap/03_contrato_datos_y_recursos.md`](../roadmap/03_contrato_datos_y_recursos.md) | Markdown (74,038 bytes) | 714 | Spanish | Level 6 (Draft Proposal v0.1) |
| 4 | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) | Markdown (57,667 bytes) | 594 | Spanish | Level 6 (Draft Proposal v0.1) |
| 5 | [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md) | Markdown (16,034 bytes) | 196 | Spanish | Level 6 (Draft Proposal v1.1) |
| 6 | [`docs/roadmap/05_diseno_tecnico.md`](../roadmap/05_diseno_tecnico.md) | Markdown (65,154 bytes) | 726 | Spanish | Level 6 (Draft Proposal v0.1) |
| 7 | [`docs/roadmap/06_manual_revision_bibliografica.md`](../roadmap/06_manual_revision_bibliografica.md) | Markdown (70,900 bytes) | 673 | Spanish | Level 6 (Draft Proposal v0.1) |
| 8 | [`docs/roadmap/07_plan_implementacion_y_validacion.md`](../roadmap/07_plan_implementacion_y_validacion.md) | Markdown (62,262 bytes) | 557 | Spanish | Level 6 (Draft Proposal v0.1) |
| 9 | [`docs/roadmap/mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md) | Markdown (11,201 bytes) | 167 | English | Level 4 (Approved Implementation Plan) |
| 10 | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) | Markdown (41,744 bytes) | 415 | English | Level 6 (Amended Evolution Proposal) |
| 11 | [`docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`](../roadmap/core/Pla%20de%20recerca%20de%20l'experiment%20sobre%20MFPData.md) | Markdown (20,352 bytes) | 349 | Catalan | Level 6 (Research Plan v0.1) |
| 12 | [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md) | Markdown (141,988 bytes) | 2,147 | Catalan / Mixed | Level 6 (Draft Guide v0.2.1) |
| 13 | [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) | Markdown (59,646 bytes) | 874 | English | Level 6 (Draft Proposal v0.1.0) |
| 14 | [`docs/roadmap/core/experiment_guio_v1.md`](../roadmap/core/experiment_guio_v1.md) | Markdown (61,282 bytes) | 874 | English / Corrupted | Level 6 (Mojibake Duplicate) |
| 15 | [`docs/roadmap/core/guion_propuesta.md`](../roadmap/core/guion_propuesta.md) | Markdown (43,280 bytes) | 572 | Spanish | Level 6 (Storyboard v0.4) |
| 16 | [`docs/roadmap/core/presentation/decisiones_abiertas.md`](../roadmap/core/presentation/decisiones_abiertas.md) | Markdown (3,233 bytes) | 40 | Spanish | Level 6 (Slide Notes) |
| 17 | `docs/roadmap/core/presentation/propuesta_investigacion.pdf` | Binary PDF (1,315,698 bytes) | N/A | Spanish | Level 6 (Slide Deck Export) |
| 18 | `docs/roadmap/core/presentation/propuesta_investigacion.pptx` | Binary PPTX (100,094 bytes) | N/A | Spanish | Level 6 (Slide Deck Presentation) |

### 2.2 Inspection Limitations

1. **Binary Presentation Artifacts**: Files `propuesta_investigacion.pdf` and `propuesta_investigacion.pptx` were verified for inventory existence, exact paths, and byte sizes. However, binary slide objects cannot be parsed line-by-line via text utilities. Their textual narrative is represented by `docs/roadmap/core/guion_propuesta.md`, but visual formatting, diagrammatic layout, and graphic slide content remain distinct presentation assets that must not be presumed identical to the text script.
2. **External Relational Database Assertions**: Historical dossiers reference PostgreSQL tables (`TargetData`, `BioData`, `protein_go_term_annotation`). In accordance with repository boundaries ([ADR-001](../decisions/ADR-001-repository-scope.md)) and operational rules, live databases were not queried or accessed.
3. **Primary Literature Full Texts**: The 20 PDF files in `docs/bibliography/` are local reference copies. No programmatic extraction or external downloads were executed.

---

## 3. Document-Level Summary

| Repository-Relative Path | Primary Purpose | Intended Audience | Language | Governance Status | Relationship to Current Implementation |
|---|---|---|---|---|---|
| [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) | Master research dossier defining scope, conceptual framework, and 7 research questions (RQ-01..07). | Scientific Lead, Bioinformatics Researchers | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Conceptual foundation; assumes live BioData connection and 2-facet model superseded by SDD pilot. |
| [`docs/roadmap/02_protocolo_cientifico_y_analisis.md`](../roadmap/02_protocolo_cientifico_y_analisis.md) | Experimental protocol detailing evidence code selection (ALL, EXP-convencional, EXP-ampliada) and statistical perturbation controls. | Data Scientists, Biostatisticians | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Highly reusable evidence definitions; perturbation tests not yet integrated into candidate catalog. |
| [`docs/roadmap/03_contrato_datos_y_recursos.md`](../roadmap/03_contrato_datos_y_recursos.md) | Relational data dictionary, entity reconciliation, and snapshot freeze specifications. | Data Architects, Database Engineers | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Informs SDD epistemological levels; proposed 2-facet tables superseded by relational claims contract. |
| [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) | Mathematical formalization of semantic distance metrics: MBL, Information Content (IC), Wang, and Lin. | Computational Biologists, Algorithm Engineers | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Rigorous metric formulations; metric computation is currently descoped from catalog baseline v1. |
| [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md) | Mathematical formulation of cross-aspect associations (MF-BP, MF-CC, BP-CC) using Normalized Pointwise Mutual Information (NPMI). | Computational Biologists, Statisticians | Spanish | Level 6 Proposal (Draft v1.1, 2026-10-26) | Essential proof against Cartesian product function-compartment linkage; currently out of scope for v1. |
| [`docs/roadmap/05_diseno_tecnico.md`](../roadmap/05_diseno_tecnico.md) | Technical architecture for perturbation pipelines, checkpointing, CLI commands, and caching. | Software Engineers, DevOps | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Largely superseded by pure offline Python CLI architecture (`scripts/`) and candidate verification. |
| [`docs/roadmap/06_manual_revision_bibliografica.md`](../roadmap/06_manual_revision_bibliografica.md) | Exhaustive manual curation protocol for primary literature review, assay classification, and evidence adjudication. | Literature Curators, Biologists | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Gold-standard curation methodology; directly informs post-v1 Phase D0 bibliographic review. |
| [`docs/roadmap/07_plan_implementacion_y_validacion.md`](../roadmap/07_plan_implementacion_y_validacion.md) | Work breakdown schedule, 20 implementation tasks, testing matrix, and execution gates. | Project Managers, Developers | Spanish | Level 6 Proposal (Draft v0.1, 2026-10-26) | Historical project plan; superseded by SDD pilot plan (`specs/functional-normalization-pilot/`). |
| [`docs/roadmap/mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md) | Authoritative roadmap governing baseline catalog releases (v0.1, v0.2.0, candidate v0.3.0, upcoming v1). | Maintainers, Contributors | English | Level 4 Approved Implementation Plan | Active governing plan for candidate catalog; fully aligned with candidate `v0.3.0`. |
| [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) | Bounded evolution proposal establishing the Non-Blocking Preservation Principle and 3-product architecture. | Maintainers, Scientific Lead | English | Level 6 Proposal (`PROP-EVOLUTION-2026-11-10`) | Active governing proposal for documentation recovery and post-v1 Phase D0 bibliographic pilot. |
| [`docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`](../roadmap/core/Pla%20de%20recerca%20de%20l'experiment%20sobre%20MFPData.md) | Catalan research plan outlining 6 research questions and comparison with BioData. | Academic Evaluators, Scientific Lead | Catalan | Level 6 Proposal (Draft v0.1, 2026-11-06) | Historical predecessor; incorporated as Annex B of `experiment-guio-v2.md`. |
| [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md) | Master research proposal PEC-EXP-001 v0.2.1 detailing experimental blocks B0–B6 and decision register DEC-01..29. | Scientific Lead, Evaluators | Catalan / Mixed | Level 6 Proposal (Estat: Proposta de revisió) | Primary comprehensive experimental proposal; embeds massive historical annexes. |
| [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) | Master research proposal PEC-EXP-001 v0.1.0 in English; defines experimental blocks B1–B6 and deliverables. | Scientific Lead, Researchers | English | Level 6 Proposal (Draft v0.1.0, 2026-10-27) | Clean UTF-8 master text; predecessor to v0.2.1; identical text to mojibake duplicate. |
| [`docs/roadmap/core/experiment_guio_v1.md`](../roadmap/core/experiment_guio_v1.md) | Corrupted duplicate of `experiment_definition.md` created via double-encoded UTF-8 saving. | None (Defective file) | English (Mojibake) | Level 6 Proposal (Defective Duplicate) | Exactly 874 lines; textually identical to `experiment_definition.md` upon UTF-8 mojibake repair. |
| [`docs/roadmap/core/guion_propuesta.md`](../roadmap/core/guion_propuesta.md) | 15-slide presentation storyboard detailing experimental rationale and slides S01–S15. | Presenters, Academic Committee | Spanish | Level 6 Historical Record (v0.4, 2026-10-28) | Accompanies slide presentations; contains clear visual pedagogical explanations of B1–B6. |
| [`docs/roadmap/core/presentation/decisiones_abiertas.md`](../roadmap/core/presentation/decisiones_abiertas.md) | Slide presentation summary notes on open decisions for research defense. | Presenters | Spanish | Level 6 Historical Record (2026-10-28) | Summarizes operational hurdles; superseded by decision register DEC-01..29 in `experiment-guio-v2.md`. |
| `docs/roadmap/core/presentation/propuesta_investigacion.pdf` | Slide deck export of research defense presentation. | Academic Committee | Spanish | Level 6 Historical Record (2026-10-28) | Visual slides corresponding to `guion_propuesta.md`. |
| `docs/roadmap/core/presentation/propuesta_investigacion.pptx` | Editable PowerPoint slide deck of research defense presentation. | Presenters | Spanish | Level 6 Historical Record (2026-10-28) | Visual slides corresponding to `guion_propuesta.md`. |

---

## 4. Section-Level Recovery Matrix (Baseline Inventory)

To preserve readability, the baseline recovery matrix is divided into three thematic tables:
- **Table 4.1**: Spanish Historical Research Dossiers (`docs/roadmap/01`–`07` and `04a`).
- **Table 4.2**: Core Research Plans & Proposals (`docs/roadmap/core/`).
- **Table 4.3**: Active Roadmaps & Governance Proposals (`docs/roadmap/` English documents).

### 4.1 Spanish Historical Research Dossiers (`docs/roadmap/01`–`07` and `04a`)

| Item ID | Source Path & Heading | Line Range (Snapshot) | Content Description | Classification | What Remains Useful | What is Outdated / Unsupported | Proposed Disposition | Destination Path & Section | Required Review / Translation | Approval / Dependencies | Priority & Effort | Acceptance Criteria |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `MAP-01-01` | `docs/roadmap/01_dossier_experimento.md` <br> `## 1. Resumen y continuidad` | L40–L51 | Executive summary of experimental corpus audit and rationale for decoupling scores from truth. | Current scientific background | Clear formulation: "positivo atribuido por fuentes, no verdad biológica confirmada". | References legacy PIS/BioData live ingestion pipeline. | Recover to English background | `docs/architecture/scientific-background.md` <br> `§1. Epistemic Foundations` | Translate to English; frame BioData as external reference. | Gate G0 / Scientific Lead | **P1 (High)** <br> Low effort | Section in English defining attributed positive corpus vs biological truth. |
| `MAP-01-02` | `docs/roadmap/01_dossier_experimento.md` <br> `## 2. Convenciones y glosario` | L52–L84 | Terminology glossary and evidentiary status tags (VERIFICAT, PROPOSTA, etc.). | Current scientific background | Clear distinction: MF is Molecular Function, not Multifunctional Protein; open world in GO. | Specific Catalan verification tags from early static inspection. | Recover to English background | `docs/architecture/scientific-background.md` <br> `§2. Conceptual Terminology` | Translate to English; align with repository data contracts. | None | **P2 (Med)** <br> Low effort | Terminology glossary in English clarifying MF vs MFP and open-world GO. |
| `MAP-01-03` | `docs/roadmap/01_dossier_experimento.md` <br> `## 3. Contexto y modelo conceptual` | L85–L120 | Three concepts (annotation amplitude, multifunctionality, moonlighting) and three evidence layers. | Current scientific background | Essential distinction: annotation breadth $\ne$ multifunctionality $\ne$ moonlighting. | Direct queries to live BioData PostgreSQL schema. | Recover to English background | `docs/architecture/scientific-background.md` <br> `§3. Three Evidence Layers` | Translate to English; incorporate 3-product architecture from proposal. | Scientific Lead | **P1 (High)** <br> Med effort | English text establishing the 3 distinct conceptual layers and open-world GO rules. |
| `MAP-01-04` | `docs/roadmap/01_dossier_experimento.md` <br> `## 4. Objetivos y preguntas` | L121–L149 | Primary objective and secondary research questions RQ-01 through RQ-07. | Still-valid future proposal | Research questions evaluating sensitivity, evidence dependency, and metric redundancy. | None in questions themselves; assumes execution within current repo. | Retain as future proposal | Historical proposal retained; English consolidation evaluated in §8.2 | Translate to English; clarify in-repo vs downstream analytical scope. | Scientific Lead | **P2 (Med)** <br> Low effort | Explicit English documentation of RQ-01..07 with clear analytical boundaries. |
| `MAP-01-05` | `docs/roadmap/01_dossier_experimento.md` <br> `## 5–7. Alcance, sistemas y bloques` | L150–L261 | Cohort definitions, system actors, and experimental blocks B0–B6. | Partially outdated but reusable | Decomposition of investigation into discrete blocks (B0..B6). | Assumes live PostgreSQL DB and automated PDF text-mining daemons. | Retain as historical proposal | `docs/archive/proposals-2026-10-spanish/01_dossier_experimento.md` [Proposed Archive] | Add English historical status banner; cite successor contracts. | Archive sign-off | **P3 (Low)** <br> Low effort | Original document preserved in archive with status banner. |
| `MAP-01-06` | `docs/roadmap/01_dossier_experimento.md` <br> `## 10. Qué este estudio no puede demostrar` | L299–L313 | Explicit methodological caveats and negative boundaries of the study. | Current scientific background | Vital caveats: scores do not prove mechanism; absence is not negative proof. | None; methodology remains 100% valid. | Recover to English background | `docs/architecture/scientific-background.md` <br> `§6.2. Explicit Negative Boundaries` | Translate to English; incorporate into repository governance. | Scientific Lead | **P1 (High)** <br> Low effort | Methodological caveats integrated into English architecture documentation. |
| `MAP-02-01` | `docs/roadmap/02_protocolo_cientifico_y_analisis.md` <br> `## 3. Poblaciones y conjuntos` | L94–L109 | Definition of attributed positive, statistical reference, reserved pool, and evaluation samples. | Current scientific background | Clear rule: BioData reference population is NEVER a verified negative class. | References to live database connection and internal sample splits. | Recover to English background | `docs/architecture/scientific-background.md` <br> `§7. Role of BioData` | Translate to English; align with AGENTS.md rule on BioData. | Scientific Lead | **P1 (High)** <br> Low effort | Explicit English definition of reference population vs negative controls. |
| `MAP-02-02` | `docs/roadmap/02_protocolo_cientifico_y_analisis.md` <br> `## 4. Condiciones de evidencia` | L110–L137 | Explicit evidence code partitions: ALL, EXP-convencional (EXP, IDA, IPI, IMP, IGI, IEP), EXP-ampliada (+HTP). | Current scientific background | Rigorous partitioning of GO evidence codes; disallowing TAS/IC as experimental evidence. | Implied immediate implementation across baseline catalog tables. | Consolidate in analytical specs | Evaluated in §8.2 (consolidation into `go-metrics-specification.md` §2.3) | Translate to English; cite GO Consortium evidence classifications. | Scientific Lead | **P1 (High)** <br> Low effort | Formal English specification of ALL, EXP-convencional, and EXP-ampliada. |
| `MAP-02-03` | `docs/roadmap/02_protocolo_cientifico_y_analisis.md` <br> `## 7–8. Perturbaciones y sensibilidad` | L187–L242 | Experimental controls: random term reduction and publication retraction protocols. | Still-valid future proposal | Controls testing whether divergence is driven by term quantity vs composition, or single papers. | Assumes metric computation is implemented in repository baseline. | Retain as future proposal | Evaluated in §8.2 (deferred pending Gate G1 / DEC-MET-06) | Translate to English; frame as future downstream/pilot protocol. | Post-v1 Decision | **P2 (Med)** <br> Med effort | Complete protocol for random term reduction and publication retraction. |
| `MAP-03-01` | `docs/roadmap/03_contrato_datos_y_recursos.md` <br> `## 5. Identidad y reconciliación` | L179–L219 | Entity reconciliation principles, UniProt canonical mapping, and isoform handling. | Historical rationale worth preserving | Rationale for deterministic hashing and cross-source UniProt exact equality. | References ad-hoc hashing superseded by ADR-005 `MFPB_PROTEIN_ID_V1`. | Replaced by accepted contract | Superseded by accepted ADR-005 & `docs/source-claims-contract.md` | Add historical banner noting supersession by ADR-005. | Archive sign-off | **P3 (Low)** <br> Low effort | Historical reconciliation rationale archived with ADR-005 crosswalk. |
| `MAP-03-02` | `docs/roadmap/03_contrato_datos_y_recursos.md` <br> `## 6–7. Modelo canónico propuesto` | L220–L303 | Proposed canonical schema with fixed 2-facet model (`BP1/MF1/CC1` vs `BP2/MF2/CC2`). | Superseded implementation description | Early attempt to model functional facets. | Rigid 2-facet collapsing; arbitrary component assignment; rejected in audit. | Proposed replacement under spec | Replaced under `specs/functional-normalization-pilot/` & proposed ADR-008 | Add historical banner noting replacement by relational schema. | Archive sign-off | **P3 (Low)** <br> Low effort | Retained in archive with clear notice of replacement by relational model. |
| `MAP-04-01` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 3. Contrato común de métricas` | L78–L118 | Common domain, pairwise aggregation, and non-calculability rules. | Still-valid future proposal | Strict aggregation contract: pairwise comparisons within same aspect, handling nulls. | Implied immediate execution in `mfp-bibliography` pipeline. | Recover to English specification | `docs/architecture/go-metrics-specification.md` <br> `§2. General Metric Domain` | Translate to English; enforce metric isolation (no composite index). | Scientific Lead | **P2 (Med)** <br> Med effort | Common mathematical aggregation contract documented in English. |
| `MAP-04-02` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 4. Ficha MBL clásica` | L119–L176 | Minimum Branch Length (MBL) structural distance on GO DAG. | Partially outdated but reusable | Mathematical formulation of shortest undirected path between terms on DAG. | Ad-hoc variants (D3-MBL, RICD-MBL) noted as unverified. | Recover to English specification | `docs/architecture/go-metrics-specification.md` <br> `§3.1. Minimum Branch Length` | Translate to English; document known graph-distance limitations. | Scientific Lead | **P2 (Med)** <br> Low effort | Clean mathematical formulation of MBL with edge-case handling. |
| `MAP-04-03` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 5. Ficha Contenido Informativo` | L177–L223 | Information Content (IC) per term and protein average using corpus frequency. | Still-valid future proposal | Exact formula $IC(t) = -\ln(n(t)/N)$ and protein averaging rules. | Assumes live BioData frequency counts rather than frozen corpus snapshot. | Recover to English specification | `docs/architecture/go-metrics-specification.md` <br> `§3.2. Information Content` | Translate to English; specify requirement for frozen background counts. | Scientific Lead | **P2 (Med)** <br> Low effort | Formal IC specification with corpus-dependency and zero-count safeguards. |
| `MAP-04-04` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 6. Ficha 1−Wang` | L224–L276 | Wang semantic dissimilarity based on DAG topology, weights $w_{is\_a}=0.8, w_{part\_of}=0.6$. | Still-valid future proposal | Complete recursive S-value formulation and Jaccard-like semantic similarity $W(a,b)$. | Unverified whether upstream CBBIO package exposes exact weighting parameters. | Recover to English specification | `docs/architecture/go-metrics-specification.md` <br> `§3.3. Wang Semantic Dissimilarity` | Translate to English; verify compatibility with standalone Python libraries. | Scientific Lead | **P1 (High)** <br> Med effort | Exact mathematical definition of Wang dissimilarity in English. |
| `MAP-04-05` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 7. Ficha 1−Lin` | L277–L326 | Lin information-theoretic dissimilarity using Most Informative Common Ancestor (MICA). | Still-valid future proposal | Exact Lin formula $L(a,b) = \frac{2 IC(MICA)}{IC(a) + IC(b)}$ and non-estimable cases. | Conflation of DCA and MICA in certain third-party libraries. | Recover to English specification | `docs/architecture/go-metrics-specification.md` <br> `§3.4. Lin Semantic Dissimilarity` | Translate to English; define strict denominator-zero conventions. | Scientific Lead | **P1 (High)** <br> Low effort | Rigorous Lin dissimilarity specification with MICA tie-breaking rules. |
| `MAP-04A-01` | `docs/roadmap/04a_asociaciones_interaspecto.md` <br> `## 2–5. Fichas NPMI` | L25–L138 | Mathematical formulation of cross-aspect associations ($A_{MF-BP}, A_{MF-CC}, A_{BP-CC}$) via NPMI. | Current scientific background | Rigorous mathematical proof that MF and CC co-occurrence does not imply spatial activity. | Implied immediate implementation across full catalog. | Recover to English specification | `docs/architecture/go-metrics-specification.md` <br> `§3.6. Cross-Aspect Associations` | Translate to English; emphasize non-conflation of MF and CC. | Scientific Lead | **P1 (High)** <br> Med effort | Complete NPMI association specification preventing Cartesian product triplets. |
| `MAP-05-01` | `docs/roadmap/05_diseno_tecnico.md` <br> `## All Sections` | L1–L726 | Technical system architecture based on PostgreSQL daemons, Redis caches, and RabbitMQ. | Superseded implementation description | Caching concepts and checkpointing strategies. | Heavy external database/server stack; superseded by pure offline CLI repository model. | Replaced by accepted architecture | Replaced by offline CLI; principles in `docs/architecture/data-flow.md` | Add historical banner noting repository pure-Python offline architecture. | Archive sign-off | **P3 (Low)** <br> Low effort | Original proposal archived with historical implementation status banner. |
| `MAP-06-01` | `docs/roadmap/06_manual_revision_bibliografica.md` <br> `## 1–2. Propósito y unidades vinculadas` | L41–L83 | Curation principles: separating source attribution, working claims, GO annotations, and literature decisions. | Current scientific background | 7 linked evidentiary units; non-destructive curation without overwriting source claims. | Assumes immediate integration into v1 baseline catalog (descoped per ADR-007). | Recover to English curation manual | `docs/curation/literature-curation-manual.md` <br> `§1. Purpose & §2. Evidentiary Units` | Translate to English; incorporate Phase D0 pilot framework. | Scientific Lead | **P1 (High)** <br> Med effort | English curation manual establishing the 7 linked units and non-rewrite rules. |
| `MAP-06-02` | `docs/roadmap/06_manual_revision_bibliografica.md` <br> `## 4. Preparación y búsqueda reproducible` | L98–L130 | Review package preparation, blinding against scores/rankings, and lawful access rules. | Current scientific background | Blinding protocols (preventing cognitive bias from scores/labels) and search budgets. | References to internal university proxy bypasses; must enforce AGENTS.md rules. | Recover to English curation manual | `docs/curation/literature-curation-manual.md` <br> `§3. References & §4. Legal Boundaries` | Translate to English; enforce lawful, sanctioned access rules only. | Scientific Lead | **P1 (High)** <br> Med effort | Blinding protocol and lawful access constraints documented in English. |
| `MAP-06-03` | `docs/roadmap/06_manual_revision_bibliografica.md` <br> `## 5–8. Flujo de extracción y adjudicación` | L131–L350 | Step-by-step extraction workflow: verifying molecular correspondence, assay types, and conflict resolution. | Current scientific background | Gold-standard protocol for adjudicating multifunctional claims from experimental literature. | Expectation of high manual curation throughput without dedicated curator FTEs. | Recover to English curation manual | `docs/curation/literature-curation-manual.md` <br> `§5. Locators & §6. Assessment` | Translate to English; align with template in `Q9Y3E5_contextual_adjudication_dossier.md`. | Scientific Lead | **P1 (High)** <br> High effort | Full English literature curation protocol ready for post-v1 Phase D0 execution. |
| `MAP-07-01` | `docs/roadmap/07_plan_implementacion_y_validacion.md` <br> `## All Sections` | L1–L557 | 20-task waterfall implementation schedule across Stages 1–5. | Superseded implementation description | Historical task definitions and risk registers. | Waterfall schedule superseded by Specification-Driven Development (SDD) pilot. | Replaced by accepted workflow | Superseded by SDD pilot lifecycle (`specs/`) | Add historical banner noting replacement by SDD pilot lifecycle. | Archive sign-off | **P3 (Low)** <br> Low effort | Original project plan preserved in archive with SDD cross-reference banner. |

---

### 4.2 Core Research Plans & Proposals (`docs/roadmap/core/`)

| Item ID | Source Path & Heading | Line Range (Snapshot) | Content Description | Classification | What Remains Useful | What is Outdated / Unsupported | Proposed Disposition | Destination Path & Section | Required Review / Translation | Approval / Dependencies | Priority & Effort | Acceptance Criteria |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `MAP-CORE-PLA-01` | `docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md` <br> `## 1–4. Marc científic` | L9–L117 | Initial Catalan research plan: research questions, biological background, and BioData contrast. | Current scientific background | Early articulation of the 6 core research questions and hypothesis formulations. | Mentions unverified PIS daemon extractors and live BioData SQL queries. | Retain as historical record; content merged in v0.2.1 | `docs/roadmap/core/experiment-guio-v2.md` Annex B <br> and `docs/architecture/scientific-background.md` | Add English historical status banner; note integration as Annex B of v0.2.1. | Archive sign-off | **P3 (Low)** <br> Low effort | Preserved in archive with banner noting embedding in `experiment-guio-v2.md`. |
| `MAP-CORE-V2-01` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## Marc científic & Abast` | L30–L89 | Comprehensive scientific framework for PEC-EXP-001 v0.2.1 in Catalan. | Current scientific background | Detailed biological rationale: annotation lag, sequence homology limits, multi-source drift. | Assumes Gate G0 formal sign-off already granted. | Retain Catalan source for provenance; maintained in English proposal | `docs/roadmap/core/experimental-master-proposal.md` <br> and `docs/architecture/scientific-background.md` | Maintained English successor proposal created under ENG-MIG-001; Catalan source preserved with provenance banner. | Scientific Lead (Gate G0) | **P2 (Med)** <br> Low effort | Header banner in Catalan source; English successor proposal actively maintained. |
| `MAP-CORE-V2-02` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## B0–B6: Blocs experimentals` | L194–L473 | Exhaustive specification of experimental blocks B0 through B6. | Still-valid future proposal | Granular design of analysis blocks: B0 RAW, B1 Corpus, B2 Sensitivity, B3 MF-MF, B4 MF-CC, B5 References, B6 Curation. | Assumes immediate automated extraction of triplets from raw literature abstracts. | Retain as future proposal in English successor | `docs/roadmap/core/experimental-master-proposal.md` §7 <br> (B0, B3, B4, B6 recovered; B1, B2 in proposal) | Translated and modularized in English master proposal; scientific execution remains gated by Gate G0. | Scientific Lead (Gate G0) | **P2 (Med)** <br> Med effort | Exhaustive B0–B6 design fully available in maintained English proposal. |
| `MAP-CORE-V2-03` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## Registre de decisions` | L673–L710 | Consolidated decision register containing 29 methodological decisions (DEC-01 to DEC-29). | Still-valid future proposal | Comprehensive inventory of unresolved methodological decisions (thresholds, ties, weights). | Decisions remain unratified by formal maintainer vote. | Reconciled in English successor proposal & governance registers | `docs/roadmap/core/experimental-master-proposal.md` §14, <br> `go-metrics-specification.md` §8.2, `literature-curation-manual.md` §10 | Reconciled in English proposal, distinguishing accepted baseline ADRs (ADR-001, 005, 002, 006) from open experimental items. | Scientific Lead / Maintainers | **P1 (High)** <br> Med effort | Complete 29-decision register reconciled and maintained in English proposal. |
| `MAP-CORE-V2-04` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## Annex A & B` | L913–L2147 | Verbatim embeddings of `experiment_guio_v1.md` (874 lines) and `Pla de recerca` (349 lines). | Retained appendix (organizational duplication) | Embedded copies of historical files. Content is physically present in repo. | Document bloat (1,223 lines of duplicate appendices). Not missing content. | Decoupled in English successor; preserved in Catalan source | `docs/roadmap/core/experimental-master-proposal.md` §19.1 <br> (Decoupled with links to originals) | Decoupled into markdown links in English successor proposal; retained verbatim in Catalan source for provenance. | Scientific Lead | **P2 (Med)** <br> Low effort | English successor modularized without duplicate bloat; source text preserved. |
| `MAP-CORE-DEF-01` | `docs/roadmap/core/experiment_definition.md` <br> `## Research Framework & Terminology` | L66–L146 | Clean UTF-8 English master proposal for PEC-EXP-001 v0.1.0. | Current scientific background | Authoritative English text for experimental concepts, scope boundaries, and terminology. | Historical predecessor to v0.2.1; some parameters refined in v0.2.1. | Retain as clean English predecessor; recover to background | `docs/architecture/scientific-background.md` <br> and `docs/roadmap/core/experiment_definition.md` | Synthesize concepts into canonical background; retain file as historical baseline. | None | **P2 (Med)** <br> Low effort | Canonical background synthesizes clean English definitions. |
| `MAP-CORE-MOJ-01` | `docs/roadmap/core/experiment_guio_v1.md` <br> `## All Sections` | L1–L874 | Defective duplicate of `experiment_definition.md` saved with double-encoded UTF-8 mojibake. | Verified duplicate | Exactly 874 lines; textually identical to `experiment_definition.md` upon UTF-8 repair. | Broken encoding characters (`â€”`, `terminologÃ­a`, `diseÃ±o`); duplicate maintenance liability. | Quarantine / dispose upon maintainer sign-off | `docs/archive/quarantine/experiment_guio_v1.md` [Proposed Quarantine] | None (defective encoding; clean master retained). | Maintainer Sign-off (Gate G4) | **P1 (High)** <br> Low effort | Mojibake duplicate quarantined without content loss; clean master retained. |
| `MAP-CORE-GUI-01` | `docs/roadmap/core/guion_propuesta.md` <br> `## S01–S15: Slides` | L62–L559 | 15-slide storyboard explaining experimental blocks B1–B6 with visual ASCII diagrams. | Historical rationale worth preserving | Highly pedagogical explanations of experimental blocks and rationale for defense. | Tied to specific slide deck structure of historical presentation. | Relocate to presentation directory | `docs/roadmap/core/presentation/guion_propuesta.md` [Proposed Relocation] | Add English status banner noting presentation support role. | None | **P3 (Low)** <br> Low effort | Consolidated with slide presentation artifacts in `presentation/` folder. |
| `MAP-CORE-DEC-01` | `docs/roadmap/core/presentation/decisiones_abiertas.md` <br> `## All Sections` | L1–L40 | Rehearsal notes on open decisions for research defense presentation. | Historical rationale worth preserving | Concise summary of presentation talking points. | Fully superseded by the 29 formal decisions (DEC-01..29) in `experiment-guio-v2.md`. | Retain in presentation directory | `docs/roadmap/core/presentation/decisiones_abiertas.md` | Add brief status note referencing DEC-01..29. | None | **P3 (Low)** <br> Low effort | Historical rehearsal note preserved alongside presentation deck. |

---

### 4.3 Active Roadmaps & Governance Proposals (`docs/roadmap/` English Documents)

| Item ID | Source Path & Heading | Line Range (Snapshot) | Content Description | Classification | What Remains Useful | What is Outdated / Unsupported | Proposed Disposition | Destination Path & Section | Required Review / Translation | Approval / Dependencies | Priority & Effort | Acceptance Criteria |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `MAP-ENG-PLAN-01` | `docs/roadmap/mfp-catalog-implementation-plan.md` <br> `## Current baseline & Phases` | L31–L142 | Level 4 implementation plan detailing Phase 0 (Scaffold), Phase 1 (Baseline), Phase 2 (5-Source), and Phase 3 (v1 Candidate). | Current implementation documentation | Authoritative implementation history and milestone rules for candidate `v0.3.0`. | Historical line 39 inconsistency (resolved in DOC-BATCH-001). | Retain as active Level 4 roadmap | `docs/roadmap/mfp-catalog-implementation-plan.md` <br> `## Phases` | None; actively maintained in English. | Repository Maintainers | **P1 (High)** <br> Low effort | Retained as active roadmap governing catalog baseline releases. |
| `MAP-ENG-EVO-01` | `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` <br> `## Section B & D` | L121–L311 | Non-Blocking Preservation Principle, two initiative boundaries, and three-product architecture. | Still-valid future proposal | Foundational architectural paradigm decoupling source preservation from downstream curation. | None; fully amended under PROP-AMEND-001. | Retain as active Level 6 proposal | `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` <br> `## Section D` | None; actively maintained in English. | Maintainers / Scientific Lead | **P1 (High)** <br> Low effort | Retained as governing proposal for documentation and post-v1 Phase D0. |
| `MAP-ENG-EVO-02` | `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` <br> `## Section F: Pilot` | L336–L359 | Specification for post-v1 Phase D0 three-publication bibliographic evidence pilot. | Still-valid future proposal | Bounded pilot protocol evaluating manual literature review before scaling. | None; strictly bounded to 3 publications. | Retain as active Level 6 proposal | `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` <br> `## Section F` | None; awaiting Phase D0 formal authorization. | Maintainers / Scientific Lead | **P2 (Med)** <br> Low effort | Retained as governing specification for post-v1 Phase D0 execution. |

---

## 5. Topic Overlap and Canonical-Destination Map

### 5.1 Thematic Overlap Synthesis

To prevent content duplication, conflicting specifications, and maintenance fragmentation across the repository, every major scientific and technical topic converges onto an authoritative canonical destination:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      TOPIC CONVERGENCE & RECOVERY ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TOPIC 1: Scientific Background, Evidence Layers & Biological Distinctions       │
│   • Sources: 01_dossier (§1–3), 02_protocolo (§3), experiment_definition (§4)    │
│   • Canonical Destination: docs/architecture/scientific-background.md [AUTHORED]│
├─────────────────────────────────────────────────────────────────────────────────┤
│ TOPIC 2: Manual Literature Curation Protocol & Evidence Adjudication            │
│   • Sources: 06_manual (§1–8), Q9Y3E5 dossier, experiment-guio-v2 (B6)          │
│   • Canonical Destination: docs/curation/literature-curation-manual.md [AUTHORED]│
├─────────────────────────────────────────────────────────────────────────────────┤
│ TOPIC 3: Mathematical GO Semantic Distance & Association Specifications         │
│   • Sources: 04_especificacion (§3–10), 04a_asociaciones (all), v2 (B3–B4)      │
│   • Canonical Destination: docs/architecture/go-metrics-specification.md [AUTH.] │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TOPIC 4: Experimental Perturbation Protocols & Evidence Sensitivity Contrasts   │
│   • Sources: 02_protocolo (§4–11), experiment_definition (B1–B2), v2 (B1–B2)     │
│   • Canonical Destination: Evaluated in §8.2 (consolidation without new file)   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TOPIC 5: Catalog Construction, Baseline Reconciliation & Candidate Releases     │
│   • Sources: mfp-catalog-implementation-plan.md, ADR-001..007, release notes   │
│   • Canonical Destination: docs/roadmap/mfp-catalog-implementation-plan.md [Ext] │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TOPIC 6: Bibliographic Evolution Architecture & 3-Product Framework            │
│   • Sources: bounded-evolution-proposal (Sections A–G), amendment report REV2   │
│   • Canonical Destination: docs/roadmap/bounded-evolution-proposal-*.md [Ext]   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Mojibake Duplicate Pair Analysis (`experiment_guio_v1.md` vs `experiment_definition.md`)

A character-by-character and line-by-line comparison between the two documents confirms the following technical facts:

1. **Physical Inventory & Layout**:
   - `docs/roadmap/core/experiment_definition.md`: Exactly 874 physical lines, 59,646 bytes, valid UTF-8 encoding.
   - `docs/roadmap/core/experiment_guio_v1.md`: Exactly 874 physical lines, 61,282 bytes, corrupted double-encoded UTF-8.
2. **Textual Equality After Documented Encoding Repair**:
   - The 1,636-byte size difference between the two files is entirely explained by multi-byte UTF-8 expansion during double encoding (e.g. byte sequence `0xE2 0x80 0x94` for em-dash `—` was interpreted as ISO-8859-1 and re-encoded as UTF-8 `0xC3 0xA2 0xC2 0x80 0xC2 0x94` (`â€”`); Spanish accented characters `í` (`0xC3 0xAD`) were re-encoded as `0xC3 0x83 0xC2 0xAD` (`Ã­`)).
   - **Empirical Proof**: Applying standard UTF-8 mojibake remediation (decoding UTF-8 bytes to ISO-8859-1 strings) produces **100% textual equality** across all 874 lines between `experiment_guio_v1.md` and `experiment_definition.md`.
3. **Epistemic Distinction: Textual Equality vs Scientific Validation**:
   - Textual equality after encoding repair establishes that `experiment_guio_v1.md` contains **zero unique drafted text or novel information** beyond what is cleanly preserved in `experiment_definition.md`.
   - However, textual equality does **NOT** constitute scientific validation or formal approval of the underlying research claims. Both files represent Draft v0.1.0 proposals; neither was formally ratified as an accepted ADR.
4. **Inbound Reference Inventory**:
   - `docs/roadmap/core/experiment-guio-v2.md` line 12: cites `experiment_guio_v1.md` as an input font and embeds its full text in Annex A (lines 919–1796).
   - Documentation audit and amendment reports cite `experiment_guio_v1.md` as an inspected artifact and audit finding.
   - Zero production code, scripts, schemas, or accepted ADRs reference `experiment_guio_v1.md`.
5. **Proposed Retained Canonical Path & Recommended Disposition**:
   - **Retained Canonical Path**: [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) is retained as the clean, authoritative English v0.1.0 baseline.
   - **Recommended Disposition**: Move [`docs/roadmap/core/experiment_guio_v1.md`](../roadmap/core/experiment_guio_v1.md) to a quarantine directory (`docs/archive/quarantine/experiment_guio_v1.md`) upon explicit maintainer sign-off under Gate G4.
   - **Boundary Enforcement**: This duplicate disposition applies strictly to this verified mojibake pair. It does **NOT** grant approval to archive, relocate, or delete any other document.

---

## 6. Items Requiring Scientific or Governance Decisions

Documentation synthesis cannot bypass human scientific and project governance. The following open decision gates must be formally resolved by the Scientific Lead and Maintainers before related proposals become normative:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      FORMAL DECISION REGISTER (GOVERNANCE GATES)                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ GATE G0: Scientific Research Proposal Adoption (PEC-EXP-001)                    │
│   • Scope: Formal approval of research questions RQ-01..07 and blocks B0–B6.    │
│   • Status: Pending review by Scientific Lead.                                  │
│   • Impact: Until approved, experiment-guio-v2.md remains an unapproved Level 6 │
│     proposal and cannot mandate pipeline implementations.                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ GATE G1: Architectural Boundary for Semantic Distance Metric Execution         │
│   • Scope: Decide whether mathematical metric engines (Wang, Lin, NPMI) belong  │
│     inside mfp-bibliography or are reserved for downstream repositories         │
│     (mfp-dataset-designer / protein-embedding-classifier) under ADR-001.        │
│   • Status: Open architectural question (formalized as DEC-MET-06).             │
│   • Impact: Determines whether go-metrics-specification.md is an in-repo        │
│     computational spec or an external reference interface contract.             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ GATE G2: Literature Curation Manual Adoption for Post-v1 Phase D0               │
│   • Scope: Formally ratify literature-curation-manual.md as the normative       │
│     standard for manual primary literature review.                              │
│   • Status: Ready for human review upon English synthesis (DEC-CUR-01..05).     │
│   • Impact: Authorizes using the protocol for the 3-publication Phase D0 pilot. │
├─────────────────────────────────────────────────────────────────────────────────┤
│ GATE G3: External Reference Population Governance (BioData)                     │
│   • Scope: Formalize the epistemic rule that external background populations    │
│     (BioData) provide frequency baselines, NEVER verified negative controls.   │
│   • Status: Codified in AGENTS.md §1.2; pending formal ADR ratification.        │
│   • Impact: Guarantees compliance with AGENTS.md negative-control prohibition.   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ GATE G4: Mojibake Duplicate Disposal Authorization                              │
│   • Scope: Authorize physical quarantine or removal of experiment_guio_v1.md.   │
│   • Status: Awaiting explicit maintainer confirmation.                          │
│   • Impact: Eliminates corrupted UTF-8 file without loss of content.            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Prioritized Recovery Increments & Execution Status

Document recovery was organized into sequential increments. As of 2026-11-12, **Increments A, B, C, D, and the navigation alignment of Increment E have been completed**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PHASED RECOVERY ROADMAP STATUS                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT A: Core Scientific & Epistemic Foundations in English [COMPLETED]     │
│   • Created: docs/architecture/scientific-background.md (302 lines, 37.5 KB)    │
│   • Synthesizes open-world assumptions, evidence layers, and boundaries.        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT B: Literature Curation Manual in English [COMPLETED]                  │
│   • Created: docs/curation/literature-curation-manual.md (511 lines, 60.6 KB)  │
│   • Synthesizes 7 evidentiary units, blinding protocol, and adjudication rules. │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT C: Mathematical Metrics Specification in English [COMPLETED]          │
│   • Created: docs/architecture/go-metrics-specification.md (646 lines, 60.8 KB) │
│   • Synthesizes MBL, IC, Wang, Lin, NPMI, long-format schema, and test suite.   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT D: Systematic Reconciliation & Gap Clarification [COMPLETED]          │
│   • Completed under DOC-RECOVERY-RECONCILIATION-001 (this reconciled report).   │
│   • All 34 map items tracked across independent recovery & disposition axes.    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT E: Navigation Alignment & Indexing (DOC-NAV-ALIGN-001) [COMPLETED]   │
│   • Updated root README.md with concise architecture and curation index hubs.   │
│   • Created docs/architecture/README.md and docs/curation/README.md indexes.    │
│   • Validated 100% of internal links and section anchors offline.               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT F: Evidence Partitions Consolidation (Action R2) [PENDING APPROVAL]   │
│   • Consolidate GO evidence partitions (ALL, EXP) into go-metrics-spec §2.3.    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INCREMENT G: Status Banners & Archival Preparation (Action R3/R4) [PENDING]     │
│   • Add document-specific English banners to historical and proposal roadmaps.  │
│   • Prepare redirection maps and migrate to docs/archive/ once authorized.      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.1 Archival Prerequisites and Recovery Tracking Table

In accordance with repository governance, **no source file may be archived until its valuable content is fully accounted for in canonical destinations**:

| Source Document | Content Recovered & Destination | Content Retained Only as Historical Record | Unresolved Dependencies | Approval Required Before Relocation |
|---|---|---|---|---|
| `docs/roadmap/01_dossier_experimento.md` | Epistemic foundations, 3 evidence layers, boundaries → [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) | Legacy PIS/BioData live ingestion descriptions; initial exploratory drafting text. | None (Increment A completed). | Maintainer Sign-off |
| `docs/roadmap/02_protocolo_cientifico_y_analisis.md` | Background population rules → [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md); Evidence code partitions evaluated in §8.2 | Specific preliminary statistical test code snippets and historical parameter tables. | Consolidation of evidence partition table (Action R2). | Scientific Lead Sign-off |
| `docs/roadmap/03_contrato_datos_y_recursos.md` | Epistemological separation rules → [`specs/functional-normalization-pilot/spec.md`](../../specs/functional-normalization-pilot/spec.md); deterministic IDs → [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) | Superseded fixed 2-facet relational schemas (`BP1/MF1/CC1` vs `BP2/MF2/CC2`). | None (Already superseded). | Maintainer Sign-off |
| `docs/roadmap/04_especificacion_metricas.md` | Mathematical specifications for MBL, IC, Wang, and Lin → [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) | Upstream CBBIO legacy library call notes and preliminary Python snippets. | None for documentation closure; Gate G1 for implementation. | Maintainer Sign-off |
| `docs/roadmap/04a_asociaciones_interaspecto.md` | Cross-aspect association formulas ($A_{MF-BP}, A_{MF-CC}, A_{BP-CC}$) → [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) | Initial exploratory co-occurrence frequency counts from legacy draft. | None for documentation closure; Gate G1 for implementation. | Maintainer Sign-off |
| `docs/roadmap/05_diseno_tecnico.md` | Checkpointing, atomic writing, and caching principles → [`docs/architecture/data-flow.md`](../architecture/data-flow.md) | Heavy PostgreSQL, Redis, and RabbitMQ server daemon architecture. | None (Already superseded by offline CLI architecture). | Maintainer Sign-off |
| `docs/roadmap/06_manual_revision_bibliografica.md` | Exhaustive literature curation protocol, blinding rules, and adjudication workflow → [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) | Preliminary Spanish templates superseded by `DOSSIER-Q9Y3E5-001`. | None for documentation closure; Gate G2 for Phase D0. | Maintainer Sign-off |
| `docs/roadmap/07_plan_implementacion_y_validacion.md` | Task risk categories and verification concepts → [`docs/architecture/requirements-traceability.md`](../architecture/requirements-traceability.md) | Historical waterfall schedule and preliminary task assignments. | None (Already superseded by SDD pilot plan). | Maintainer Sign-off |
| `docs/roadmap/core/Pla de recerca...md` | Biological context and questions → Annex B of `experiment-guio-v2.md` and [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) | Early Catalan draft notes; historical BioData queries. | Embedded in v0.2.1. | Maintainer Sign-off |
| `docs/roadmap/core/experiment_guio_v1.md` | Zero unique content (100% textually equal to `experiment_definition.md` after UTF-8 repair). | None (Defective mojibake duplicate). | Gate G4 approval. | Maintainer Sign-off |
| `docs/roadmap/core/guion_propuesta.md` | Slide narrative and pedagogical diagrams → `docs/roadmap/core/presentation/` | None (Preserved intact in presentation folder). | None. | Maintainer Sign-off |

---

## 8. Systematic Recovery Reconciliation (`DOC-RECOVERY-RECONCILIATION-001` & Bounded Clarification)

### 8.1 Reconciled Section-Level Recovery Matrix

To prevent conflating recovery completeness, operational roles, contract authorities, and governance approval, each of the 34 map items is tracked across three independent status axes:
- **Content Recovery & Succession Status**:
  - `Fully recovered`: Content synthesized into active English canonical reference documents.
  - `Replaced by accepted contract`: Replaced by an accepted Level 1, 2, or 3 contract (e.g. ADR-005, `data-flow.md`).
  - `Proposed replacement under active spec/schema`: Proposed replacement under an active SDD specification and Draft 2020-12 schema (distinct from accepted ADRs; ADR-008 remains `Proposed`).
  - `Preserved as future proposal`: Active research question, partition design, or procedure preserved for future evaluation; documenting it does NOT authorize execution or violate scope.
  - `Historical context retained`: Contextual background requiring no active replacement; preserved for provenance.
  - `Retained appendix (organizational duplication)`: Verbatim embedded appendix physically present in the repository; organizational cleanup scheduled post-archival (NOT missing scientific content).
  - `Verified duplicate (pending quarantine)`: Defective encoding duplicate with 0 unique text; quarantined pending Gate G4.
- **Intended Operational Role**: `Active reference` / `Future proposal` / `Historical context` / `Defective duplicate`.
- **Disposition Readiness**: `Retain in place` / `Candidate for later archival` / `Blocked by named prerequisite` / `Duplicate disposition pending`.

Scientific and governance approval is recorded independently.

| Item ID | Exact Source Path & Heading | Content Recovery & Succession Status | Intended Operational Role | Disposition Readiness | Exact Destination Path & Heading | Content & Qualifications Recovered | Missing Content / Gaps | Evidentiary Basis & Authority Status | Next Action & Rationale |
|---|---|---|---|---|---|---|---|---|---|
| `MAP-01-01` | `docs/roadmap/01_dossier_experimento.md` <br> `## 1. Resumen y continuidad` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) <br> [`§1.1`](../architecture/scientific-background.md#11-source-attribution-versus-locally-established-conclusions) | Exact quote preserved: "positivo atribuido por fuentes, no verdad biológica confirmada"; evidence chain defined. | None. Legacy live PIS/BioData references appropriately omitted. | `scientific-background.md` L24–L35 (Level 6 Explanatory Reference). | Add English historical status banner upon archival authorization. |
| `MAP-01-02` | `docs/roadmap/01_dossier_experimento.md` <br> `## 2. Convenciones y glosario` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) <br> [`§1.2`](../architecture/scientific-background.md#12-open-world-assumption-and-negative-evidence-in-gene-ontology) & [`§2`](../architecture/scientific-background.md#2-core-conceptual-distinctions) | MF vs MFP distinction; Open-World Assumption in GO; absence is annotation gap, not negative proof; GO `NOT` vs null experimental assays. | Exploratory Catalan status tags (VERIFICAT, PROPOSTA) omitted as obsolete. | `scientific-background.md` L36–L82 (Level 6 Explanatory Reference). | Add English historical banner upon archival authorization. |
| `MAP-01-03` | `docs/roadmap/01_dossier_experimento.md` <br> `## 3. Contexto y modelo conceptual` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) <br> [`§2`](../architecture/scientific-background.md#2-core-conceptual-distinctions) & [`§4`](../architecture/scientific-background.md#4-evidence-layers-and-repository-data-products) | Three domains: annotation breadth, broad multifunctionality, moonlighting (diverse mechanisms, no active-site distance rule). Three evidence layers (claims, GO, literature). | Live PostgreSQL schema details omitted. | `scientific-background.md` L47–L82, L130–L140 (Level 6 Explanatory Reference). | Add English historical banner upon archival authorization. |
| `MAP-01-04` | `docs/roadmap/01_dossier_experimento.md` <br> `## 4. Objetivos y preguntas` | **Preserved as future proposal** | Future proposal | Blocked by named prerequisite (Gate G0) | Retained in historical proposal; concepts in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) [`§2`](../architecture/scientific-background.md#2-core-conceptual-distinctions), [`§8`](../architecture/scientific-background.md#8-epistemic-inventory-separation-of-invariants-explanations-hypotheses-and-open-decisions) and [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) [`§1.2`](../architecture/go-metrics-specification.md#12-separation-of-interpretation-boundaries) | Concepts underlying RQ-01 (overlap), RQ-02 (amplitude vs distance), RQ-05 (Wang vs Lin), RQ-06 (NPMI), and RQ-07 (curation) recovered. | Explicit enumeration of questions RQ-01 through RQ-07 not yet consolidated in active English reference. | Evaluated in §8.2 (Level 6 Proposal). | Keep as future proposal in historical proposal; defer dedicated protocol creation. |
| `MAP-01-05` | `docs/roadmap/01_dossier_experimento.md` <br> `## 5–7. Alcance, sistemas y bloques` | **Historical context retained** | Historical context | Candidate for later archival | Retained in proposal; B0–B6 in [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) §5; curation in `manual`; metrics in `spec` | Concept of phased experimental blocks (B0–B6) retained in English proposals; discrete blocks recovered to dedicated manuals. | Server daemons (PostgreSQL, Redis) discarded as obsolete. | `experiment_definition.md` L179–L473; `go-metrics-specification.md`; `literature-curation-manual.md`. | Add English historical banner upon archival authorization. |
| `MAP-01-06` | `docs/roadmap/01_dossier_experimento.md` <br> `## 10. Qué este estudio no puede demostrar` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) <br> [`§6.2`](../architecture/scientific-background.md#62-explicit-negative-boundaries-what-computational-scores-cannot-demonstrate) | All 10 explicit negative methodological statements synthesized verbatim in English. | None. Full 10-point negative boundary suite recovered. | `scientific-background.md` L204–L217 (Level 6 Explanatory Reference). | Add English historical banner upon archival authorization. |
| `MAP-02-01` | `docs/roadmap/02_protocolo_cientifico_y_analisis.md` <br> `## 3. Poblaciones y conjuntos` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) <br> [`§7.2`](../architecture/scientific-background.md#72-methodological-limitation-not-a-validated-negative-control-cohort) | Empirical reference population serves term/pair frequencies; NEVER a verified negative control class (NMF). Open-world fallacy codified. | Exploratory sampling script percentages omitted. | `scientific-background.md` L220–L238; [`AGENTS.md`](../../AGENTS.md) §1.2 (Binding Rule). | Add English historical banner upon archival authorization. |
| `MAP-02-02` | `docs/roadmap/02_protocolo_cientifico_y_analisis.md` <br> `## 4. Condiciones de evidencia` | **Preserved as future proposal** | Future proposal | Blocked by named prerequisite (Action R2) | Retained in proposal; partitioning principles in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) [`§4`](../architecture/scientific-background.md#4-evidence-layers-and-repository-data-products) | Principle of comparing ALL against EXP subsets recovered. Disallowing TAS/IC as experimental evidence recognized. | Explicit inclusion table of evidence codes (ALL, EXP-convencional, EXP-ampliada) not consolidated in active document. | Evaluated in §8.2 (Level 6 Proposal). | Consolidate evidence partition table into `go-metrics-specification.md` §2.3 (Action R2). |
| `MAP-02-03` | `docs/roadmap/02_protocolo_cientifico_y_analisis.md` <br> `## 7–8. Perturbaciones y sensibilidad` | **Preserved as future proposal** | Future proposal | Blocked by named prerequisite (Gate G1 / DEC-MET-06) | Retained in historical proposal `docs/roadmap/02_protocolo_cientifico_y_analisis.md`; hypothesis H2 in `scientific-background.md` [`§8`](../architecture/scientific-background.md#8-epistemic-inventory-separation-of-invariants-explanations-hypotheses-and-open-decisions) | Concept that sensitivity is driven by term count reduction recovered in hypothesis H2. | Procedural algorithms for random term reduction and publication retraction unrecovered. | Evaluated in §8.2. Documenting proposed procedures does NOT authorize execution or violate scope. | Keep as future proposal; defer procedural recovery until metric execution boundary (Gate G1) is decided. |
| `MAP-03-01` | `docs/roadmap/03_contrato_datos_y_recursos.md` <br> `## 5. Identidad y reconciliación` | **Replaced by accepted contract** | Historical context | Candidate for later archival | Accepted [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) & [`docs/source-claims-contract.md`](../source-claims-contract.md) | Deterministic UniProtKB hashing scheme (`MFPB_PROTEIN_ID_V1`) and source record identity codified in binding architecture. | Ad-hoc exploratory hashing formulas discarded. | ADR-005 (Level 1 Accepted ADR); `source-claims-contract.md` (Level 2 Contract). | Add English historical banner noting supersession by ADR-005. |
| `MAP-03-02` | `docs/roadmap/03_contrato_datos_y_recursos.md` <br> `## 6–7. Modelo canónico propuesto` | **Proposed replacement under active spec/schema** | Historical context | Candidate for later archival | Proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) & [`data/curated/functional_claims.schema.json`](../../data/curated/functional_claims.schema.json) | Relational multi-claim architecture decouples source claims from fixed 2-facet binary slots (`bp1`, `mf1`, `cc1`). | Rigid 2-facet schema discarded as flawed. | ADR-008 is PROPOSED (Level 1 Proposal); Draft 2020-12 schema is active Level 5 artifact. Distinct from accepted ADR. | Add English historical banner noting replacement by relational schema. |
| `MAP-04-01` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 3. Contrato común de métricas` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) <br> [`§2`](../architecture/go-metrics-specification.md#2-general-metric-domain-term-preparation-and-proposed-aggregation-conventions) | Intra-aspect pairwise domain ($T_A \times T_B$), unweighted pair arithmetic mean aggregation, complete coverage requirements, diagnostic `available_mean`. | None. Complete aggregation contract recovered. | `go-metrics-specification.md` L82–L145 (Level 6 Proposed Design). | Add English historical banner upon archival authorization. |
| `MAP-04-02` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 4. Ficha MBL clásica` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) <br> [`§3.1`](../architecture/go-metrics-specification.md#31-minimum-branch-length-mbl) | DCA depth formulation $d_{\text{MBL}}(a, b) = h(a) + h(b) - 2h(c^*)$; CBBIO legacy derivation and negative fallback behavior; BFS shortest-path comparison. | Unverified ad-hoc variants (D3-MBL, RICD-MBL) noted as unverified. | `go-metrics-specification.md` L148–L200 (Level 6 Proposed Design). | Add English historical banner upon archival authorization. |
| `MAP-04-03` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 5. Ficha Contenido Informativo` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) <br> [`§3.2`](../architecture/go-metrics-specification.md#32-information-content-ic-and-protein-mean) | Term-level natural log (nats) formula $IC(t) = -\ln(n(t)/N)$; ancestor propagation rule; corpus dependency; unannotated term null policy. | Live BioData database queries omitted. | `go-metrics-specification.md` L202–L244 (Level 6 Proposed Design). | Add English historical banner upon archival authorization. |
| `MAP-04-04` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 6. Ficha 1−Wang` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) <br> [`§3.3`](../architecture/go-metrics-specification.md#33-wang-semantic-dissimilarity) | S-value recurrence formulation, semantic value $SV(a)$, Jaccard-like similarity $W(a,b)$, dissimilarity $d_W = 1 - W$, weights $w_{\text{is\_a}}=0.8, w_{\text{part\_of}}=0.6$. | None. Complete mathematical formulation recovered. | `go-metrics-specification.md` L246–L295 (Level 6 Proposed Design). | Add English historical banner upon archival authorization. |
| `MAP-04-05` | `docs/roadmap/04_especificacion_metricas.md` <br> `## 7. Ficha 1−Lin` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) <br> [`§3.4`](../architecture/go-metrics-specification.md#34-lin-semantic-dissimilarity) | MICA information-theoretic formula $L(a,b) = \frac{2 IC(c^*)}{IC(a) + IC(b)}$, dissimilarity $d_L = 1 - L$, zero-denominator policy (`ZERO_IC_DENOMINATOR` $\implies \text{null}$). | None. Complete mathematical formulation recovered. | `go-metrics-specification.md` L297–L346 (Level 6 Proposed Design). | Add English historical banner upon archival authorization. |
| `MAP-04A-01` | `docs/roadmap/04a_asociaciones_interaspecto.md` <br> `## 2–5. Fichas NPMI` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) <br> [`§3.6`](../architecture/go-metrics-specification.md#36-cross-aspect-associations-npmi) | Dual-aspect NPMI formulas ($A_{MF-BP}, A_{MF-CC}, A_{BP-CC}$), normalization by $-\ln P(x,y)$, provisional support threshold ($n \ge 5$), unobserved pair null, coverage threshold ($0.80$). | Cartesian triplet inferences explicitly prohibited. | `go-metrics-specification.md` L375–L440 (Level 6 Proposed Design). | Add English historical banner upon archival authorization. |
| `MAP-05-01` | `docs/roadmap/05_diseno_tecnico.md` <br> `## All Sections` | **Replaced by accepted contract** | Historical context | Candidate for later archival | Replaced by offline CLI architecture; principles in [`docs/architecture/data-flow.md`](../architecture/data-flow.md) | Checkpointing, atomic writing, deterministic digests, and manifest validation preserved in architecture. | Heavy PostgreSQL, Redis, RabbitMQ daemon architecture discarded. | `data-flow.md` (Level 3 Architecture); `requirements-traceability.md`. | Add English historical banner noting replacement by pure-Python offline architecture. |
| `MAP-06-01` | `docs/roadmap/06_manual_revision_bibliografica.md` <br> `## 1–2. Propósito y unidades vinculadas` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) <br> [`§1.2`](../curation/literature-curation-manual.md#12-the-non-blocking-preservation-principle) & [`§2.1`](../curation/literature-curation-manual.md#21-the-seven-linked-evidentiary-units) | 7 linked evidentiary units (entity, working claim, annotation, source claim, reference, evidence unit, review decision); Non-Blocking Preservation Principle; non-destructive curation. | Ingestion gating assumptions discarded. | `literature-curation-manual.md` L25–L102 (Level 6 Proposed Procedure). | Add English historical banner upon archival authorization. |
| `MAP-06-02` | `docs/roadmap/06_manual_revision_bibliografica.md` <br> `## 4. Preparación y búsqueda reproducible` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) <br> [`§3`](../curation/literature-curation-manual.md#3-reference-identification-and-ingestion-gating), [`§4`](../curation/literature-curation-manual.md#4-documentary-availability-material-inspected-legal-boundaries-and-permitted-processing), [`§7.2`](../curation/literature-curation-manual.md#72-proposed-blinding-protocol-use-case-dependent-pending-approval) | Reference diversity (PMID, DOI, `GO_REF`); handling ambiguous references without silent substitution; lawful access rules; blinding protocol; granular stopping conditions. | Paywall bypass heuristics strictly eliminated. | `literature-curation-manual.md` L104–L152, L228–L245 (Level 6 Proposed Procedure). | Add English historical banner upon archival authorization. |
| `MAP-06-03` | `docs/roadmap/06_manual_revision_bibliografica.md` <br> `## 5–8. Flujo de extracción y adjudicación` | **Fully recovered** | Active reference | Candidate for later archival | [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) <br> [`§5.1`](../curation/literature-curation-manual.md#51-locator-granularity-requirements), [`§6`](../curation/literature-curation-manual.md#6-scientific-assessment-protocol), [`§9`](../curation/literature-curation-manual.md#9-practical-implementation-tools) | Locator granularity (Figure, Table, Text); molecular correspondence; assay findings vs discussion; nominal support outcomes; negative findings distinct from GO `NOT`; modern moonlighting mechanisms. | Fixed active-site distance rules eliminated. | `literature-curation-manual.md` L154–L214, L325–L445 (Level 6 Proposed Procedure). | Add English historical banner upon archival authorization. |
| `MAP-07-01` | `docs/roadmap/07_plan_implementacion_y_validacion.md` <br> `## All Sections` | **Replaced by accepted contract** | Historical context | Candidate for later archival | Replaced by SDD pilot lifecycle ([`specs/functional-normalization-pilot/`](../../specs/functional-normalization-pilot/)) | Risk categories, verification concepts, and incremental staging preserved in SDD workflow. | 20-task waterfall schedule discarded as obsolete. | `specs/functional-normalization-pilot/plan.md`; `tasks.md` (Level 5 Specifications). | Add English historical banner noting replacement by SDD pilot lifecycle. |
| `MAP-CORE-PLA-01` | `docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md` <br> `## 1–4. Marc científic` | **Historical context retained** | Historical context | Candidate for later archival | Retained as Annex B of `experiment-guio-v2.md` L1798–L2147; background in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) | Early articulation of core research questions and biological background preserved. | Direct BioData SQL extraction details omitted. | `experiment-guio-v2.md` Annex B; `scientific-background.md` (Level 6). | Add English historical banner upon archival authorization. |
| `MAP-CORE-V2-01` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## Marc científic & Abast` | **Fully recovered** | Active reference | Retain in place | Maintained in English proposal [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md); English synthesis in [`scientific-background.md`](../architecture/scientific-background.md); Catalan source preserved for provenance | Biological framework: annotation lag, sequence homology limits, multi-source divergence synthesized in English reference document; complete proposal text maintained in English successor. | Assumes Gate G0 approval granted. | `experimental-master-proposal.md`; `experiment-guio-v2.md` (Level 6 Proposal Under Review). | English successor maintained; Catalan source preserved with provenance banner. |
| `MAP-CORE-V2-02` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## B0–B6: Blocs experimentals` | **Preserved as future proposal** | Future proposal | Blocked by named prerequisite (Gate G0) | Retained in maintained English proposal [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) [§7](../roadmap/core/experimental-master-proposal.md#7-experimental-block-specifications-b0-through-b6); B0 in candidate release v0.3.0; B3/B4 in `go-metrics-specification.md`; B6 in `literature-curation-manual.md` | Blocks B0–B6 fully specified in English successor proposal; experimental execution remains gated by Gate G0. | Blocks B1 (Corpus contrast) and B2 (Sensitivity) remain future proposals. | Evaluated in §8.2 (Level 6 Proposal). | Maintained in English proposal; execution pending Gate G0 authorization. |
| `MAP-CORE-V2-03` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## Registre de decisions` | **Fully recovered** | Active reference | Retain in place | Formalized in [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) [§14](../roadmap/core/experimental-master-proposal.md#14-formal-register-of-open-decisions-dec-01-through-dec-29), [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) [`§8.2`](../architecture/go-metrics-specification.md#82-register-of-open-decisions) & [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) [`§10`](../curation/literature-curation-manual.md#10-open-governance-decisions) | All 29 open decisions categorized in English proposal, connecting DEC-01, DEC-02, DEC-18, DEC-27 to accepted ADRs while preserving unexecuted experimental items. | None. Full 29-decision register maintained in English. | `experimental-master-proposal.md` §14; `go-metrics-specification.md` L606–L643; `literature-curation-manual.md` L450–L472. | Track decisions in maintained English proposal and canonical specifications. |
| `MAP-CORE-V2-04` | `docs/roadmap/core/experiment-guio-v2.md` <br> `## Annex A & B` | **Retained appendix (organizational duplication)** | Historical context | Decoupled in English successor | Decoupled in [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) [§19.1](../roadmap/core/experimental-master-proposal.md#191-disposition-of-historical-annexes); retained verbatim in Catalan source `experiment-guio-v2.md` (lines 919–2147) | Duplicate annex text decoupled into markdown links in English proposal; source text preserved in repository. | Physical duplicate copies remain in Catalan source document. | `experimental-master-proposal.md` §19.1; `experiment-guio-v2.md` L919–L2147. | English successor modularized; Catalan source preserved for historical provenance. |
| `MAP-CORE-DEF-01` | `docs/roadmap/core/experiment_definition.md` <br> `## Research Framework & Terminology` | **Fully recovered** | Historical context | Retain in place | Clean English predecessor proposal retained in place; concepts in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) [`§2`](../architecture/scientific-background.md#2-core-conceptual-distinctions), [`§5`](../architecture/scientific-background.md#5-sequence-similarity-and-functional-interpretation), [`§8`](../architecture/scientific-background.md#8-epistemic-inventory-separation-of-invariants-explanations-hypotheses-and-open-decisions) | Authoritative English definitions of multifunctionality, moonlighting, sequence homology limits, and working hypotheses H1–H4 synthesized. | None. Clean UTF-8 baseline preserved. | `experiment_definition.md`; `scientific-background.md` (Level 6). | Retain in place as clean historical baseline. |
| `MAP-CORE-MOJ-01` | `docs/roadmap/core/experiment_guio_v1.md` <br> `## All Sections` | **Verified duplicate (pending quarantine)** | Defective duplicate | Duplicate disposition pending (Gate G4) | Textually identical to `docs/roadmap/core/experiment_definition.md` (100% equality across all 874 lines after UTF-8 repair) | Proven to contain 0 unique drafted text or novel information. | None. File is a corrupted duplicate. | Empirical proof in §5.2 of this report. | Move to `docs/archive/quarantine/` upon maintainer sign-off under Gate G4. |
| `MAP-CORE-GUI-01` | `docs/roadmap/core/guion_propuesta.md` <br> `## S01–S15: Slides` | **Historical context retained** | Historical context | Candidate for later archival | Preserved intact in `docs/roadmap/core/guion_propuesta.md`; companion to slide decks | 15-slide presentation narrative and ASCII diagrams preserved intact. | Distinguish narrative script from visual binary slides (evaluated in §8.3). | Evaluated in §8.3. | Relocate alongside slide presentations in `docs/roadmap/core/presentation/`. |
| `MAP-CORE-DEC-01` | `docs/roadmap/core/presentation/decisiones_abiertas.md` <br> `## All Sections` | **Historical context retained** | Historical context | Retain in place | Superseded by formal decision register DEC-01..29 and English registers in `spec` & `manual` | Slide defense rehearsal notes preserved in presentation directory. | Superseded by comprehensive decision registers. | `decisiones_abiertas.md`; `experiment-guio-v2.md` §Registre. | Retain in place in presentation directory with brief cross-reference note. |
| `MAP-ENG-PLAN-01` | `docs/roadmap/mfp-catalog-implementation-plan.md` <br> `## Current baseline & Phases` | **Active roadmap retained** | Active reference | Retain in place | Actively maintained Level 4 implementation plan | Authoritative implementation history and milestone rules aligned with candidate `v0.3.0`. | None. Actively maintained in English. | `mfp-catalog-implementation-plan.md` (Level 4 Approved Implementation Plan). | Retain in place as active Level 4 roadmap. |
| `MAP-ENG-EVO-01` | `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` <br> `## Section B & D` | **Preserved as future proposal** | Active reference | Retain in place | Actively maintained Level 6 proposal | Non-Blocking Preservation Principle, two initiative boundaries, and three-product architecture fully ratified in amendment. | None. Actively maintained in English. | `bounded-evolution-proposal-*.md` (Level 6 Proposal). | Retain in place as governing evolution proposal. |
| `MAP-ENG-EVO-02` | `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` <br> `## Section F: Pilot` | **Preserved as future proposal** | Future proposal | Retain in place | Actively maintained Level 6 proposal (§Section F) | Specification for post-v1 Phase D0 three-publication bibliographic evidence trial. | None. Awaiting Phase D0 formal authorization. | `bounded-evolution-proposal-*.md` §Section F (Level 6 Proposal). | Retain in place as governing specification for post-v1 Phase D0 execution. |

---

### 8.2 Evaluation of the Experimental-Protocol Gap and Scope Invariants

A central question in documentation recovery is whether the absence of a dedicated English document—specifically `docs/analysis/experimental-contrast-protocol.md` [Proposed]—constitutes a blocker that requires creating a new document before documentation closure.

An evaluation of the map items associated with this topic (`MAP-01-04`, `MAP-02-01`, `MAP-02-02`, `MAP-02-03`, `MAP-CORE-V2-02`) establishes the following facts:

1. **What is Already Recovered**:
   - **Background Population Epistemology (`MAP-02-01`)**: Fully recovered in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) [`§7.2`](../architecture/scientific-background.md#72-methodological-limitation-not-a-validated-negative-control-cohort) and [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) [`§1.2`](../architecture/go-metrics-specification.md#12-separation-of-interpretation-boundaries). The rule that empirical background populations (BioData) are frequency baselines and **never verified negative controls** is permanently codified in English.
   - **Descriptive Overlap Protocol (`MAP-01-04` / RQ-01)**: The methodology for evaluating cross-source catalog concordance without metric calculations is already formalized in the active English document [`docs/analysis/five-source-descriptive-study-plan.md`](../analysis/five-source-descriptive-study-plan.md).
   - **Metric Formulations (`MAP-CORE-V2-02` / Blocks B3–B4)**: The mathematical definitions of Wang dissimilarity, Lin dissimilarity, MBL, IC, and NPMI are fully recovered in [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md).
   - **Literature Adjudication (`MAP-CORE-V2-02` / Block B6)**: The manual curation workflow is fully recovered in [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md).
2. **What Remains as Future Proposals and Documentary vs Scientific Separation**:
   - **Evidence Code Partitions (`MAP-02-02`)**: The partition categories (ALL vs EXP-convencional vs EXP-ampliada) are referenced in `scientific-background.md` §4, but the exact inclusion table of GO evidence codes (`EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`, `HTP`) is not yet tabulated in an active English document. Creating an entire standalone protocol document solely to hold a 15-line table of evidence codes is architectural overreach. This table should instead be consolidated into [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) §2.3 (Action R2). Crucially, **documentary recovery of this proposed table is separate from its scientific adoption**: the table can be documented as an explicitly proposed reference design awaiting experimental approval without blocking documentation organization.
   - **Procedural Perturbation Protocols (`MAP-02-03`)**: Algorithmic protocols for random term reduction and publication retraction are downstream metric evaluation procedures. Under [ADR-001](../decisions/ADR-001-repository-scope.md) and [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), metric computation is descoped from the v1 baseline catalog. However, **documenting a proposed procedure does NOT itself authorize its execution or violate repository scope**. Methodological preservation under `AGENTS.md` protects research designs. In this case, because metric hosting responsibility remains undecided (Gate G1 / `DEC-MET-06`), keeping the procedural perturbation protocols preserved as explicitly labeled future proposals in historical texts satisfies preservation requirements without creating premature standalone protocols.
   - **Research Questions RQ-01..07 (`MAP-01-04`)**: The research questions represent an academic inquiry proposal (PEC-EXP-001) governed by Gate G0. Preserving them in historical Spanish proposals (`01_dossier_experimento.md`) and Catalan guides (`experiment-guio-v2.md`, now maintained in English as [`experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md)) fully satisfies the Non-Blocking Preservation Principle. They do not block baseline catalog documentation closure.
3. **Smallest Justified Action**:
   - **Do NOT create `docs/analysis/experimental-contrast-protocol.md`**.
   - Consolidate the proposed evidence code partition definitions into [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) §2.3 via Action R2.
   - Keep the perturbation protocols and research questions explicitly classified as **future research proposals** preserved in historical and master proposals.

---

### 8.3 Presentation Assets: Inventory Coverage versus Inspected Narrative Content

To ensure rigorous auditability, the relationship between presentation artifacts must be clarified:

1. **Inspected Narrative Script (`docs/roadmap/core/guion_propuesta.md`)**:
   - The text storyboard was inspected line-by-line across all 572 lines (v0.4, 2026-10-28).
   - It contains the complete spoken narrative, slide-by-slide pedagogical objectives (slides S01–S15), and ASCII diagrams explaining experimental blocks B1–B6.
   - All conceptual assertions in `guion_propuesta.md` are covered by the master proposal (`experiment-guio-v2.md`, maintained in English as [`experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md)) and synthesized in English canonical documents.
2. **Binary Presentation Decks (`propuesta_investigacion.pdf` & `.pptx`)**:
   - These files were verified for physical existence, file format, byte size (PDF: 1,315,698 bytes; PPTX: 100,094 bytes), and repository path.
   - **Coverage Boundary**: Verifying that the binary slide files exist in the repository inventory does **NOT** mean that their visual graphic layouts, typography, embedded chart images, or vector diagrams were inspected or parsed.
   - The binary presentations are retained as historical presentation collateral. In a future reorganization, `guion_propuesta.md` should be moved into `docs/roadmap/core/presentation/` alongside these binary files to consolidate all defense materials in one directory.

---

## 9. Minimal Documentation Closure Plan and Next Increments

### 9.1 Required Actions Before Documentation Closure

To achieve formal documentation closure without data loss or broken links, the four finely scoped actions are tracked as follows:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      MINIMAL DOCUMENTATION CLOSURE ACTIONS                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ACTION R1: Navigation & Index Alignment for Recovered Documents [COMPLETED]     │
│   • Target: README.md, docs/architecture/README.md, docs/curation/README.md     │
│   • Outcome: Recovered canonical documents indexed with exact roles and anchors.│
├─────────────────────────────────────────────────────────────────────────────────┤
│ ACTION R2: Evidence Code Partitions Consolidation (resolving MAP-02-02 gap)    │
│   • Target: docs/architecture/go-metrics-specification.md (§2.3)                │
│   • Purpose: Add proposed definitions for ALL, EXP-convencional, and            │
│     EXP-ampliada partitions without creating a redundant protocol file.         │
│   • Scientific Approval: Separate from documentation recovery (can remain       │
│     explicitly proposed pending formal experimental adoption).                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ACTION R3: Document-Specific English Status Banners on Historical & Proposals   │
│   • Target: docs/roadmap/01-07, 04a, experiment-guio-v2.md, Pla de recerca      │
│   • Purpose: Add document-specific English status banners. Distinguish active   │
│     future proposals (v2) from historical archived drafts (01-07).              │
│   • Scientific Approval: Not needed (compliance with AGENTS.md §3).             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ACTION R4: Reference Redirection Audit & Archival Preparation                   │
│   • Target: docs/reports/documentation-recovery-map.md (update disposition)     │
│   • Purpose: Audit all internal inbound links pointing to historical roadmaps   │
│     and establish redirection paths before physical migration to docs/archive/. │
│   • Scientific Approval: Not needed (technical link audit).                     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Detailed Specification of Remaining Actions

1. **Action R1: Navigation & Index Alignment for Recovered Documents [COMPLETED]**
   - **File Boundaries**: [`README.md`](../../README.md), [`docs/architecture/README.md`](../architecture/README.md), [`docs/curation/README.md`](../curation/README.md).
   - **Delivered Outcome**: Completed under `DOC-NAV-ALIGN-001`. Created directory navigation indexes in `docs/architecture/` and `docs/curation/`; linked all three recovered canonical English documents (`scientific-background.md`, `literature-curation-manual.md`, `go-metrics-specification.md`) with explicit role badges; verified 100% offline resolution of relative paths and section anchors without creating competing indexes.

2. **Action R2: Evidence Code Partitions Consolidation**
   - **Proposed File Boundaries**: [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (inserting subsection §2.3).
   - **Purpose**: Document the explicit definitions and inclusion criteria for the three GO evidence code partitions (`ALL`, `EXP-convencional` [EXP, IDA, IPI, IMP, IGI, IEP], and `EXP-ampliada` [+HTP codes]), resolving the gap identified in `MAP-02-02`.
   - **Dependencies**: None.
   - **Acceptance Criteria**: Exact evidence code grouping formalized in English as a proposed specification with citations to GO Consortium evidence standards; zero new files created.
   - **Scientific Approval Separation**: Documenting the proposed table achieves documentary recovery; formal scientific adoption of the partitions for empirical execution remains an independent post-v1 decision.

3. **Action R3: Document-Specific Status Banners**
   - **Proposed File Boundaries**: Historical files [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) through [`docs/roadmap/07_plan_implementacion_y_validacion.md`](../roadmap/07_plan_implementacion_y_validacion.md), [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md), [`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md), and [`docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`](../roadmap/core/Pla%20de%20recerca%20de%20l'experiment%20sobre%20MFPData.md).
   - **Purpose & Document-Specific Design**:
     - **For historical drafts (`01`–`07`, `04a`, `Pla de recerca`)**: Banner declares the file as a **historical research proposal (Level 6)** preserved for provenance under `AGENTS.md`, with original Spanish/Catalan text preserved without alteration, pointing to canonical English successors.
     - **For active proposals ([`docs/roadmap/core/experiment-guio-v2.md`](../roadmap/core/experiment-guio-v2.md))**: Banner declares the file as a preserved Catalan master proposal under review (Level 6), pointing to its maintained English successor proposal [`experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md).
     - **For active English proposals and roadmaps ([`bounded-evolution-proposal-*.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md), [`mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md))**: Retained as active documents; no historical archival banner applied.
   - **Dependencies**: Completion of this reconciliation.
   - **Acceptance Criteria**: Document-specific banners accurately differentiate active proposals from historical drafts; zero modifications to historical body text; zero broken links.
   - **Scientific Approval Needed**: No (governance formatting).

4. **Action R4: Reference Redirection Audit & Archival Preparation**
   - **Proposed File Boundaries**: Internal link references across `docs/`.
   - **Purpose**: Map every inbound link pointing to `docs/roadmap/01`–`07` and prepare the exact target paths under `docs/archive/proposals-2026-10-spanish/` and `docs/archive/proposals-2026-10-core/` so that when maintainers authorize physical relocation, zero broken links occur.
   - **Dependencies**: Actions R1–R3 completed; Maintainer authorization to create `docs/archive/`.
   - **Acceptance Criteria**: Complete link inventory verifying that all references resolve before and after physical migration.
   - **Scientific Approval Needed**: No (technical link audit).

---

### 9.2 Optional Future Improvements (Post-Closure)

The following improvements are optional, provide secondary cleanup, and do **NOT** block baseline documentation closure:
1. **Decoupling Annexes A & B from `experiment-guio-v2.md`**:
   - Trimming lines 913–2147 of `experiment-guio-v2.md` and replacing the embedded copies of `experiment_guio_v1.md` and `Pla de recerca` with markdown links to their archived paths. This will reduce document size by >55% (from 142 KB to ~60 KB). Must be executed *after* original files are archived.
2. **Relocating `guion_propuesta.md` to `presentation/`**:
   - Moving `docs/roadmap/core/guion_propuesta.md` to `docs/roadmap/core/presentation/` to consolidate all slide presentation assets in a single directory.
3. **Quarantine of Mojibake Duplicate (`MAP-CORE-MOJ-01`)**:
   - Moving `docs/roadmap/core/experiment_guio_v1.md` to `docs/archive/quarantine/` upon maintainer sign-off under Gate G4.
4. **Formulation of Downstream Analysis Protocols**:
   - Authoring dedicated experimental contrast and metric execution protocols IF AND ONLY IF Gate G1 decides that metric computation belongs within this repository.

---

### 9.3 Open Scientific and Governance Decisions (Not Blocking Closure)

The following open decisions are tracked in repository decision registers. They govern future scientific features and pilot execution, but do **NOT** block baseline documentation closure:

1. **Gate G0: Scientific Research Proposal Adoption (PEC-EXP-001)**:
   - *Impact*: Governs whether experimental blocks B1–B6 become approved research protocols; does not block catalog baseline documentation closure.
2. **Gate G1 / `DEC-MET-06`: Metric Engine Hosting Responsibility**:
   - *Impact*: Determines whether metric computation engines are implemented in `mfp-bibliography` or downstream in `mfp-analysis`.
3. **Gate G2 / `DEC-CUR-01`..`05`: Literature Curation Manual Normative Adoption**:
   - *Impact*: Authorizes using `literature-curation-manual.md` for the post-v1 Phase D0 empirical trial.
4. **Gate G3: BioData Reference Population Formalization**:
   - *Impact*: Ratifies the epistemic rule in a formal ADR. Already codified as an operational rule in `AGENTS.md` §1.2.
5. **Gate G4: Mojibake Duplicate Quarantine Authorization**:
   - *Impact*: Eliminates double-encoded UTF-8 file upon maintainer approval.
6. **`DEC-MET-01` to `DEC-MET-05`**:
   - *Impact*: Methodological parameter choices (pinned GO release, Lin zero denominator, NPMI thresholds) required only when implementing metric engines.

---

### 9.4 Coverage Limitations Requiring Maintainer Acknowledgment

Maintainers and reviewers must acknowledge the following technical limitations:
1. **Binary Presentation Deck Inspection**: Slide decks `propuesta_investigacion.pdf` and `.pptx` were verified for existence, byte size, and format, but visual slide design and graphical charts were not parsed. The narrative script was inspected via `guion_propuesta.md`.
2. **Downstream Perturbation Protocols**: Detailed procedural algorithms for random term reduction and publication retraction remain in historical Spanish text pending Gate G1 resolution.
3. **Research Questions (RQ-01..07)**: Preserved in historical proposal text; explicit list is not yet in an active English reference document.

---

### 9.5 Smallest Recommended Next Increment

Following the successful completion of `DOC-NAV-ALIGN-001`, the smallest justified next step is:

- **Increment Identifier**: `DOC-BANNERS-001` (Document-Specific Status Banners — Action R3)
- **Target Files**:
  - Historical Spanish dossiers: `docs/roadmap/01_dossier_experimento.md` through `07_plan_implementacion_y_validacion.md`, `04a_asociaciones_interaspecto.md`
  - Historical Catalan draft: `docs/roadmap/core/Pla de recerca de l'experiment sobre MFPData.md`
  - Active Catalan proposal: `docs/roadmap/core/experiment-guio-v2.md`
- **Objective**: Prepend document-specific English status banners that clearly distinguish active future proposals from historical archived proposals, linking each to its respective canonical English successors without modifying historical body text.
- **Acceptance Criteria**:
  1. Standardized English banners prepended to the 10 files.
  2. Banners on historical dossiers declare them historical proposals (Level 6) preserved for provenance under `AGENTS.md`.
  3. Banner on `experiment-guio-v2.md` declares it an active master proposal under review (`Estat: Proposta de revisió`, Level 6).
  4. Zero modifications to historical body text.
  5. All internal markdown links resolve offline with exit code 0.
  6. `python3 scripts/validate_repository.py` passes with exit code 0.
- **Required Authorization**: Explicit user approval to proceed with `DOC-BANNERS-001`.

---
*End of Reconciled Documentation Recovery and Disposition Map (`REP-DOC-RECOVERY-MAP-2026-11-10-REV2`). Tasks DOC-RECOVERY-RECONCILIATION-001 and DOC-NAV-ALIGN-001 complete. Awaiting maintainer instructions.*
