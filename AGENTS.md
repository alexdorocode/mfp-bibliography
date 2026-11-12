# Agent Guidance and Operational Rules for `mfp-bibliography`

## 1. Repository Purpose and Operational Boundaries

`mfp-bibliography` is an auditable, reproducible, and versioned source-evidence foundation for multifunctional and moonlighting protein research. Its core mission is cataloging, identity resolution, source provenance tracking, and bibliographic evidence curation.

### 1.1 Boundary Distinctions

To ensure compliance with repository governance, agents must distinguish:

1. **Intended Long-Term Capabilities**:
   - Comprehensive multi-source cataloging.
   - Traceable crosswalks between source claims, Gene Ontology (GO) annotations, and literature evidence.
   - Versioned releases supporting downstream functional characterization and curation.
2. **Approved Scope (Current Accepted Baseline)**:
   - Ingestion and freezing of raw data artifacts under [ADR-002](docs/decisions/ADR-002-raw-data-immutability.md).
   - Deterministic entity identity resolution mapping canonical UniProtKB accessions to `MFPB_PROTEIN_ID_V1` identifiers ([ADR-005](docs/decisions/ADR-005-deterministic-protein-ids.md)). Hash identifiers are one-way deterministic digests, not cryptographically or mathematically reversible.
   - Five-source catalog candidate packaging and offline cryptographic verification under [ADR-006](docs/decisions/ADR-006-coverage-only-moonprot-status-rows.md) and candidate release `v0.3.0`.
   - Milestone exclusion: External bibliographic relations and GO enrichment are formally descoped from the catalog baseline per [ADR-007](docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md).
3. **Currently Authorized Tasks**:
   - Specification authoring, contract definition, and documentation preparation only.
   - Implementation code, automated schema writes, pipeline execution, and scientific analysis are **NOT authorized** without explicit human sign-off on a scoped increment.

### 1.2 Explicit Non-Goals (Out of Scope)
- Machine learning model training, feature engineering, classification benchmarks, or embedding generation (reserved for downstream repositories per [ADR-001](docs/decisions/ADR-001-repository-scope.md)).
- Constructing verified negative control sets (Non-Multifunctional Proteins / NMF). **BioData is a contextual reference population, NEVER a verified negative class**.
- Web scraping, live network crawling, or unverified database synchronization during automated builds.

> [!NOTE]
> This document provides operational guidelines for AI coding assistants working in this repository. It is not guaranteed to be loaded automatically by all client environments; agents and human contributors must consult it explicitly before undertaking any task.

---

## 2. Document Authority and Reading Order

When navigating documentation, agents must observe the following precedence hierarchy:

```
[Level 1: Accepted Architectural Decision Records (ADRs)]
  └─ docs/decisions/ADR-*.md (highest authority; durable invariants)
       │
[Level 2: Repository Governance & Data Contracts]
  └─ docs/project-charter.md, docs/release-policy.md,
     docs/source-policy.md, docs/source-claims-contract.md
       │
[Level 3: Technical Architecture & Traceability]
  └─ docs/architecture/data-flow.md,
     docs/architecture/requirements-traceability.md
       │
[Level 4: Approved Implementation Roadmaps & Plans]
  └─ docs/roadmap/mfp-catalog-implementation-plan.md
       │
[Level 5: Approved Increment Specifications]
  └─ specs/<increment>/spec.md, plan.md, tasks.md
       │
[Level 6: Draft Proposals, Research Plans, and Audit Reports]
  └─ docs/audits/*.md,
     docs/archive/proposals-2026-11-catalan/experiment-guio-v2.md,
     docs/archive/proposals-2026-10-spanish/01-07 (historical originals; advisory/evidence only);
     docs/roadmap/core/experimental-master-proposal.md (maintained English proposal; NOT approval to implement)
```

**Key Authority Rules**:
1. **Draft vs Approved**: Documents marked "Draft", "Borrador", or "Proposta de revisió" (including maintained proposals like `docs/roadmap/core/experimental-master-proposal.md` and archived historical drafts like `experiment-guio-v2.md` and `01_dossier_experimento.md`) are proposals for human review. Archival relocation preserves provenance but does not confer approval; they remain advisory proposals and do NOT authorize implementation or architectural changes.
2. **Audit Status**: Audit reports (such as `docs/audits/2026-11-06_repository-sdd-functional-normalization-audit.md`) contain evidence and recommendations. They are NOT approved specifications and must not be treated as implementation mandates.
3. **No Silent Supersession**: A newer file or higher version number never overrides an accepted ADR without a formally accepted superseding ADR.

---

## 3. Language Policy for Production Artifacts

- **Production Language**: All new scientific and technical documentation, specifications, schemas, ADRs, source code, comments, docstrings, tests, and CLI outputs must be written in **English**.
- **Human Collaboration**: Interactive discussion, human feedback, and review comments may continue in English, Catalan, or Spanish.
- **Source Preservation**: Original source statements, verbatim raw values, error messages, and bibliographic quotes must remain in their original language. Never silently translate raw source data.
- **Multilingual History**: Existing documents in Catalan or Spanish remain unchanged; future translations or consolidations must preserve exact identifiers, file paths, and document history.

---

## 4. Specification-Driven Development (SDD) Workflow

No agent may write, edit, or refactor implementation code without an approved, scoped specification.

### 4.1 Minimal Lifecycle
1. **Scope Authorization**: A human-approved ADR authorizing the work increment.
2. **Specification Package**: A directory under `specs/<feature>/` containing:
   - `spec.md`: Functional and scientific requirements, data invariants, and acceptance criteria.
   - `plan.md`: Architectural approach, staged execution, component reuse, dependencies, and testing strategy.
   - `tasks.md`: Sequenced, finely scoped implementation tasks with explicit write boundaries.
   - `verification.md`: Documentation and automated check record.
3. **Scoped Implementation**: Code changes strictly confined to the allowed files declared in each task.
4. **Offline Verification**: All tests and validation scripts must execute and pass offline.
5. **Human Review**: Completed increment submitted for human sign-off.

### 4.2 Explicit Write Boundaries
Every modification must adhere strictly to task-level write boundaries:
- Never edit files outside the explicitly authorized task scope.
- Never modify raw data files under `data/raw/` (append-only per [ADR-002](docs/decisions/ADR-002-raw-data-immutability.md)).
- Never modify packaged release artifacts under `releases/` (immutable candidates).
- Never modify existing accepted ADRs in `docs/decisions/` (corrections require new ADRs).

---

## 5. Scientific and Bioinformatic Invariants

When working with biological claims, Gene Ontology (GO) terms, and protein evidence, agents must enforce these scientific invariants:

1. **No Fabricated GO Mappings**:
   - Never infer or assign GO identifiers via ad-hoc regexes, keyword matching, or heuristic text parsing (e.g. mapping `nucleus` to `GO:0005634`) without an approved, evaluated mapping protocol.
   - Distinct source-native claims must be preserved as separate observations; do not force multiple claims into artificial binary slots (e.g. "Facet 1 vs Facet 2").
2. **No Unwarranted Function–Compartment Linkage**:
   - Co-annotation of a Molecular Function (GO-MF) and a Cellular Component (GO-CC) to the same protein entity does **NOT** prove that the function is executed in that compartment. Never synthesize functional triplets by Cartesian product.
3. **Preservation of Multiplicity**:
   - Do not assume that $N$ source claims equal $N$ distinct biological functions. Maintain separation between raw extracted statements and curated biological assertions.
4. **Qualifier and Evidence Integrity**:
   - GO annotations with `NOT` qualifiers represent negative evidence; they must never be converted or stored as positive functional assertions.
   - Absence of an experimental annotation in a database is an annotation gap, never evidence of absence of function.
5. **Reference Level Support**:
   - Link literature references (PMIDs/DOIs) only at the granularity supported by the source. Never promote a record-level reference to a function-specific support assertion without explicit evidence.

---

## 6. Prohibited Autonomous Actions

Unless explicitly authorized in writing by the user for a specific task, agents must **NEVER**:
- Switch Git branches, create commits, push to remotes, or modify Git staging.
- Install, update, or remove system or Python dependencies (`pip install`, `uv add`, etc.).
- Connect to live or remote databases (`TargetData`, `BioData`, `MFPUniProtData`, PostgreSQL, MySQL).
- Execute network requests, download external files, ontologies, or literature PDFs.
- Run compute-intensive scientific pipelines, metric engines, or notebook workflows.
- Delete, overwrite, or rename immutable raw datasets, existing releases, or accepted ADRs.

---

## 7. Required Agent Handoff Format

At the conclusion of every turn or task, the agent must deliver a concise English summary structured as follows:

```markdown
### Handoff Summary

- **Task ID & Purpose**: [Brief description of the completed increment]
- **Files Created or Modified**: [Exact repository paths]
- **Verification Performed**: [Exact read-only or offline commands run, with status]
- **Operational Limitations**: [What was deferred, unverified, or out of scope]
- **Next Decision / Human Approval Required**: [Exact blocking question or gate]
```
