# Bibliographic and Evidence Curation

This directory contains literature curation protocols, operational review procedures, and reference contextual adjudication dossiers for `mfp-bibliography`.

## Document Index and Authority Levels

| Document | Role & Epistemic Status | Primary Scope | Authority Level ([`AGENTS.md`](../../AGENTS.md)) |
|---|---|---|---|
| [`literature-curation-manual.md`](literature-curation-manual.md) | **Proposed Procedure — Pending Approval** | Protocols for manual primary literature curation, 7 decoupled evidentiary units, Non-Blocking Preservation Principle, evidence localization, and review adjudication. *Proposed operational manual; pending scientific and maintainer approval.* | Level 6 (Proposed Operational Procedure) |
| [`Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) | **Reference Contextual Review Profile** | Empirical adjudication dossier for human PTRH2 / Bit1 (`Q9Y3E5`), illustrating locator granularity, partial abstract assessment limits, and claim-level support categories. | Level 6 (Reference Curation Dossier) |

---

## Overview of Curation Documents

### 1. Literature Curation Manual
- **Path**: [`literature-curation-manual.md`](literature-curation-manual.md)
- **Status**: Proposed procedure pending approval (Level 6).
- **Purpose**: Recovers and updates the primary literature curation methodology formulated in historical dossier `docs/roadmap/06_manual_revision_bibliografica.md`:
  - **The Non-Blocking Preservation Principle** ([§1.2](literature-curation-manual.md#12-the-non-blocking-preservation-principle)): Manual curation is an evaluative and quality-enhancement activity for downstream curated subsets (Product C); it is **never an ingestion gate** for source preservation (Product A) or exploratory views (Product B).
  - **Seven Linked Evidentiary Units** ([§2.1](literature-curation-manual.md#21-the-seven-linked-evidentiary-units)): Decouples protein entity, working claim, GO annotation, source attribution, bibliographic reference, evidence unit, and review decision.
  - **Documentary Availability vs Inspection** ([§4.1](literature-curation-manual.md#41-separating-availability-inspection-and-assessment-scope)): Curators must explicitly document what text/sections were examined.
  - **Lawful Access Boundaries** ([§4.2](literature-curation-manual.md#42-legal-boundaries-and-compliance-with-agentsmd)): Strictly enforces `AGENTS.md` rules against paywall and bot-check bypassing.
  - **Evidence Localization** ([§5.1](literature-curation-manual.md#51-locator-granularity-requirements)): Requires exact Figure, Table, or passage locators.
  - **Nominal Support Outcomes** ([§6.3](literature-curation-manual.md#63-explicit-support-outcome-categories)): Explicit categories (`supports`, `partially_supports`, `opposes`, `insufficient_evidence`, `not_addressed`, `not_assessable`).
  - **Modern Moonlighting Criteria** ([§6.5](literature-curation-manual.md#65-modern-moonlighting-mechanisms-alignment-with-rec-inc-001)): Recognizes diverse biochemical mechanisms and rejects arbitrary active-site distance rules.
  - **Register of Open Decisions** ([§10](literature-curation-manual.md#10-open-governance-decisions)): Tracks decisions `DEC-CUR-01` through `DEC-CUR-05` (including blinding rules, NLP/LLM assisted extraction boundaries, and curator qualification standards).

### 2. Contextual Adjudication Dossier: Human PTRH2 / Bit1 (`Q9Y3E5`)
- **Path**: [`Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md)
- **Status**: Reference Contextual Review Profile (Level 6).
- **Purpose**: A concrete empirical evaluation of human PTRH2 / Bit1 (`PTH2_HUMAN`), demonstrating:
  - Adjudication across 12 discrete working claims and 45 source GO annotations.
  - Case study on the limits of abstract-only inspection vs full-text requirements.
  - Claim-level support scoring without asserting unverified biological certification.

---

## Related Architectural and Governance Documents

- **Repository Purpose & Scope**: [ADR-001](../decisions/ADR-001-repository-scope.md) (source-evidence foundation; literature relations descoped from v1 baseline).
- **v1 Milestone Descoping**: [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) (bibliographic relations and GO enrichment deferred to post-v1).
- **Scientific Background**: [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (foundational biological and epistemic principles).
- **Bibliographic Evolution Proposal**: [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) (governing proposal for post-v1 Phase D0 empirical trial).
