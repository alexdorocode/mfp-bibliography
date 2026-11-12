# Repository Historical Archive

## 1. Purpose and Epistemic Status of the Archive

This directory preserves historical research proposals, preliminary protocols, exploratory specifications, presentation collateral, and working drafts from the formative phases of the `mfp-bibliography` project (October–November 2026).

> [!IMPORTANT]
> - **Historical Evidence and Provenance Only**: Documents in this archive are preserved strictly for historical auditability, methodological provenance, and retrospective verification. They do **NOT** represent active technical architecture, approved specifications, or implementation mandates.
> - **Precedence Hierarchy**: Under repository governance ([`AGENTS.md`](../../AGENTS.md) §2), archived documents reside at Level 6 (lowest authority). They never supersede Accepted Architectural Decision Records (ADRs), repository data contracts, active specifications under `specs/`, or canonical Level 3 architecture under `docs/architecture/`.
> - **No Blanket Authority**: An archived original provides authoritative evidence of its *historical wording, native terminology, and proposed ideas at the date of authoring*. It does **not** constitute proof that its scientific claims, algorithmic assumptions, or database designs are valid, approved, or implemented.
> - **Language and Maintenance Invariants**: In accordance with [`AGENTS.md`](../../AGENTS.md) §3, all maintained documentation and active proposals are authored and maintained in English. Historical originals in Catalan and Spanish are preserved in their native language to maintain an unbroken audit trail; they are not actively updated or translated in place.

---

## 2. Directory Structure

```
docs/archive/
├── README.md                          # This archival navigation index
├── proposals-2026-10-spanish/         # Foundational eight-part Spanish research dossier series (2026-10)
│   ├── 01_dossier_experimento.md
│   ├── 02_protocolo_cientifico_y_analisis.md
│   ├── 03_contrato_datos_y_recursos.md
│   ├── 04_especificacion_metricas.md
│   ├── 04a_asociaciones_interaspecto.md
│   ├── 05_diseno_tecnico.md
│   ├── 06_manual_revision_bibliografica.md
│   └── 07_plan_implementacion_y_validacion.md
└── proposals-2026-11-catalan/         # Early Catalan research plans and working guides (2026-11)
    ├── experiment-guio-v2.md
    └── Pla de recerca de l'experiment sobre MFPData.md
```

*(Note: Companion presentation collateral remains organized under [`docs/roadmap/core/presentation/`](../roadmap/core/presentation/).)*

---

## 3. Inventory of Archived Documents and Successor Crosswalk

The table below maps each preserved historical original to its documentary role, date of creation, and its maintained English successor document and section:

| Archived Document Path | Language & Date | Historical Documentary Role | Maintained English Successor Document & Section | Epistemic Successor Role |
|---|---|---|---|---|
| [`proposals-2026-10-spanish/01_dossier_experimento.md`](proposals-2026-10-spanish/01_dossier_experimento.md) | Spanish (2026-10-28) | Foundational research proposal and study design dossier. | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§§1–8) & [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) | Explanatory reference; unadopted master experimental proposal (PEC-EXP-001). |
| [`proposals-2026-10-spanish/02_protocolo_cientifico_y_analisis.md`](proposals-2026-10-spanish/02_protocolo_cientifico_y_analisis.md) | Spanish (2026-10-28) | Scientific protocol, evidence partitions, and sensitivity testing proposals. | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§7.2) & [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (§2.5 & Appendix) | Explanatory reference; proposed evidence code partitions and sensitivity procedures (MAP-02-03). |
| [`proposals-2026-10-spanish/03_contrato_datos_y_recursos.md`](proposals-2026-10-spanish/03_contrato_datos_y_recursos.md) | Spanish (2026-10-28) | Preliminary data contract and relational schema proposals. | [`docs/source-claims-contract.md`](../source-claims-contract.md), [`docs/decisions/ADR-005-deterministic-protein-ids.md`](../decisions/ADR-005-deterministic-protein-ids.md), & [`specs/functional-normalization-pilot/spec.md`](../../specs/functional-normalization-pilot/spec.md) | Accepted data contracts and active SDD pilot specification. |
| [`proposals-2026-10-spanish/04_especificacion_metricas.md`](proposals-2026-10-spanish/04_especificacion_metricas.md) | Spanish (2026-10-28) | Mathematical metric definitions, aggregation conventions, and schema designs. | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (§§2–6) | Recovered proposed analytical design (unadopted, descoped under ADR-001/ADR-007). |
| [`proposals-2026-10-spanish/04a_asociaciones_interaspecto.md`](proposals-2026-10-spanish/04a_asociaciones_interaspecto.md) | Spanish (2026-10-28) | Cross-aspect association designs (NPMI) and inter-aspect triplet guardrails. | [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (§3.6) | Recovered proposed analytical design (unadopted). |
| [`proposals-2026-10-spanish/05_diseno_tecnico.md`](proposals-2026-10-spanish/05_diseno_tecnico.md) | Spanish (2026-10-28) | Preliminary daemon and database architecture (PostgreSQL/RabbitMQ). | [`docs/architecture/data-flow.md`](../architecture/data-flow.md) & [`docs/architecture/requirements-traceability.md`](../architecture/requirements-traceability.md) | Accepted Level 3 architecture; offline reproducible pure-Python execution model. |
| [`proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](proposals-2026-10-spanish/06_manual_revision_bibliografica.md) | Spanish (2026-10-28) | Literature curation manual and manual review protocol. | [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) | Maintained proposed manual literature adjudication protocol (pending Gate G2). |
| [`proposals-2026-10-spanish/07_plan_implementacion_y_validacion.md`](proposals-2026-10-spanish/07_plan_implementacion_y_validacion.md) | Spanish (2026-10-28) | Waterfall implementation schedule (20 tasks). | [`docs/roadmap/mfp-catalog-implementation-plan.md`](../roadmap/mfp-catalog-implementation-plan.md) & [`specs/functional-normalization-pilot/plan.md`](../../specs/functional-normalization-pilot/plan.md) | Active implementation plan and SDD engineering packages. |
| [`proposals-2026-11-catalan/Pla de recerca de l'experiment sobre MFPData.md`](proposals-2026-11-catalan/Pla%20de%20recerca%20de%20l%27experiment%20sobre%20MFPData.md) | Catalan (2026-11-04) | Initial Catalan research plan (v0.1) for experiment PEC-EXP-001. | [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) (Annex B) & [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) | Unadopted master research proposal and explanatory background reference. |
| [`proposals-2026-11-catalan/experiment-guio-v2.md`](proposals-2026-11-catalan/experiment-guio-v2.md) | Catalan (2026-11-06) | Comprehensive Catalan working guide (v0.2.1) for experiment PEC-EXP-001. | [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) | Maintained English master research proposal (unadopted, pending Gate G0). |
| [`docs/roadmap/core/presentation/guion_propuesta.md`](../roadmap/core/presentation/guion_propuesta.md) | Spanish (2026-10-28) | Storyboard and speaker notes script for 15-slide research presentation. | Companion to slide decks in [`docs/roadmap/core/presentation/`](../roadmap/core/presentation/) | Historical presentation collateral. |

---

## 4. Archival Governance Invariants

1. **Read-Only Provenance**: Files in `docs/archive/` are frozen historical records. They must not be edited, rewritten, or refactored.
2. **Relative Link Maintenance**: When files are relocated into the archive, relative hyperlinks targeting active documentation outside the archive are updated to preserve navigation integrity without modifying the substantive historical text.
3. **No Unwarranted Promotion**: Citing an archived document does not elevate its status. An archived document remains an unapproved historical proposal unless a formal ADR explicitly adopts a specific procedure or finding.
