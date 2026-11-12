# Architecture and Technical Specifications

This directory contains technical architecture documentation, canonical scientific foundations, and analytical metric specifications for `mfp-bibliography`.

## Document Index and Authority Levels

| Document | Role & Epistemic Status | Primary Scope | Authority Level ([`AGENTS.md`](../../AGENTS.md)) |
|---|---|---|---|
| [`scientific-background.md`](scientific-background.md) | **Explanatory Reference** | Epistemic foundations, attribution vs biological truth, three conceptual domains (annotation breadth, multifunctionality, moonlighting), open-world GO limits, and reference population boundaries (BioData). | Level 6 (Canonical Explanatory Reference) |
| [`data-flow.md`](data-flow.md) | **Accepted Technical Architecture** | Offline transformation pipelines, stage boundaries, and candidate catalog assembly. | Level 3 (Technical Architecture) |
| [`requirements-traceability.md`](requirements-traceability.md) | **Accepted Technical Architecture** | Systematic traceability matrix mapping catalog invariants (R1–R12) to tests, contracts, and code. | Level 3 (Technical Architecture) |
| [`go-metrics-specification.md`](go-metrics-specification.md) | **Recovered Proposed Analytical Design** | Mathematical formulations of GO DAG distances (MBL, IC, Wang, Lin, NPMI), pairwise aggregation contracts, long-format schema design, and test suite. *Recovered design proposal pending review; does not imply implemented code.* | Level 6 (Proposed Analytical Design) |
| [`experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md) | **Maintained English Research Proposal** | Multi-source evidence concordance, functional dissimilarity, contextual triplets, and literature adjudication framework (`PEC-EXP-001`). *Active research proposal under review; not an implemented pipeline or approved experimental policy.* | Level 6 (Research Proposal Under Review) |

---

## Overview of Recovered and Active Documents

### 1. Scientific Background and Methodological Foundations
- **Path**: [`scientific-background.md`](scientific-background.md)
- **Status**: Explanatory Reference (Level 6).
- **Purpose**: Synthesizes the core epistemic principles recovered from historical research dossiers (`docs/archive/proposals-2026-10-spanish/01_dossier_experimento.md`, `02_protocolo_cientifico_y_analisis.md`, `docs/roadmap/core/experiment_definition.md`):
  - Strict separation between external source attribution and locally established biological truth ([§1.1](scientific-background.md#11-source-attribution-versus-locally-established-conclusions)).
  - Open-World Assumption (OWA) in Gene Ontology and distinction between GO `NOT` qualifiers and experimental null findings ([§1.2](scientific-background.md#12-open-world-assumption-and-negative-evidence-in-gene-ontology)).
  - Clear boundaries separating annotation breadth, broad multifunctionality, and protein moonlighting ([§2](scientific-background.md#2-core-conceptual-distinctions)).
  - Prohibition against synthesizing Cartesian function–compartment triplets ([§3.2](scientific-background.md#32-the-prohibited-inference-inventing-context-from-mere-co-annotation)).
  - Three conceptual evidence layers (claims, GO, literature) decoupled from repository data products ([§4](scientific-background.md#4-evidence-layers-and-repository-data-products)).
  - Limits of sequence similarity for moonlighting transfer ([§5](scientific-background.md#5-sequence-similarity-and-functional-interpretation)).
  - Ten explicit negative boundaries on computational scores ([§6.2](scientific-background.md#62-explicit-negative-boundaries-what-computational-scores-cannot-demonstrate)).
  - Methodological limitations of empirical background populations: BioData is a reference frequency baseline, **never a verified negative control class** ([§7.2](scientific-background.md#72-methodological-limitation-not-a-validated-negative-control-cohort)).

### 2. Gene Ontology Metrics and Semantic Dissimilarity Specification
- **Path**: [`go-metrics-specification.md`](go-metrics-specification.md)
- **Status**: Recovered Proposed Analytical Design (Level 6).
- **Purpose**: Recovers the mathematical formulations, DAG traversal rules, and edge-case handling proposed in historical dossiers (`docs/archive/proposals-2026-10-spanish/04_especificacion_metricas.md`, `04a_asociaciones_interaspecto.md`):
  - General intra-aspect pairwise domain and unweighted pair arithmetic mean aggregation contract ([§2](go-metrics-specification.md#2-general-metric-domain-term-preparation-and-proposed-aggregation-conventions)).
  - Detailed formulations for Minimum Branch Length ([§3.1](go-metrics-specification.md#31-minimum-branch-length-mbl)), Information Content in nats ([§3.2](go-metrics-specification.md#32-information-content-ic-and-protein-mean)), Wang semantic dissimilarity ([§3.3](go-metrics-specification.md#33-wang-semantic-dissimilarity)), and Lin dissimilarity ([§3.4](go-metrics-specification.md#34-lin-semantic-dissimilarity)).
  - Cross-aspect statistical associations using Normalized Pointwise Mutual Information (NPMI, [§3.6](go-metrics-specification.md#36-cross-aspect-associations-npmi)).
  - Long-format output schema design ([§6](go-metrics-specification.md#6-proposed-long-format-output-schema)).
  - Register of open decisions (`DEC-MET-01` to `DEC-MET-06`, [§8.2](go-metrics-specification.md#82-register-of-open-decisions)), including whether metric calculation engines belong in this repository or in downstream packages under [ADR-001](../decisions/ADR-001-repository-scope.md).

### 3. Catalog Data Flow
- **Path**: [`data-flow.md`](data-flow.md)
- **Status**: Accepted Technical Architecture (Level 3).
- **Purpose**: Defines the deterministic, offline transformation pipeline that builds the five-source candidate catalog from immutable raw inputs.

### 4. Requirements Traceability Matrix
- **Path**: [`requirements-traceability.md`](requirements-traceability.md)
- **Status**: Accepted Technical Architecture (Level 3).
- **Purpose**: Maps catalog requirements R1 through R12 to specific test suites, contract definitions, and verified pipeline outputs.

### 5. Experimental Master Proposal (Research Framework PEC-EXP-001)
- **Path**: [`docs/roadmap/core/experimental-master-proposal.md`](../roadmap/core/experimental-master-proposal.md)
- **Status**: Maintained English research proposal — under review; not an implemented pipeline or approved experimental policy (Level 6).
- **Purpose**: Maintained English successor to Catalan master proposal [`experiment-guio-v2.md`](../archive/proposals-2026-11-catalan/experiment-guio-v2.md), governing the conceptual research framework `PEC-EXP-001`:
  - Reading conventions and four epistemic statement categories ([§1](../roadmap/core/experimental-master-proposal.md#1-document-reading-conventions-and-epistemic-governance)).
  - Eleven core research questions (O1–O11) and ten hypotheses (H1–H10) ([§2](../roadmap/core/experimental-master-proposal.md#2-scientific-framework-epistemic-foundations)).
  - Seven experimental blocks (B0 through B6) covering raw parsing, cohort harmonization, sensitivity stratification, intra-protein dissimilarity, cross-aspect associations, reference contrasts, and manual literature adjudication ([§7](../roadmap/core/experimental-master-proposal.md#7-experimental-block-specifications-b0-through-b6)).
  - Governance decision gates (G0 through G5) and comprehensive decision register (`DEC-01` through `DEC-29`) ([§13](../roadmap/core/experimental-master-proposal.md#13-governance-deliverable-matrix-and-decision-gates), [§14](../roadmap/core/experimental-master-proposal.md#14-formal-register-of-open-decisions-dec-01-through-dec-29)).
  - Explicit non-execution notice: new experimentation is strictly gated by Gate G0; computational pipelines and metric engines remain unapproved and unexecuted.

---

## Related Governing Contracts and Decision Records

- **Repository Purpose & Scope**: [ADR-001](../decisions/ADR-001-repository-scope.md) (source cataloging and evidence infrastructure; ML and classifiers reserved for downstream).
- **Raw Data Immutability**: [ADR-002](../decisions/ADR-002-raw-data-immutability.md) (append-only frozen source files).
- **Deterministic Entity Identity**: [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) (`MFPB_PROTEIN_ID_V1` hashing scheme).
- **Candidate Release Scope**: [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) (descoping external relations from catalog baseline v1).
- **Proposed Functional Normalization Extension**: [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) (staged pilot extension; status: `Proposed`).
