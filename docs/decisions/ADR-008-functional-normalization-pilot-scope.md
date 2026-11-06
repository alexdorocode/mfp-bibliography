# ADR-008: Bounded Scope Extension for a Functional-Normalization Pilot

- **Status**: Proposed
- **Date**: 2026-11-06
- **Deciders**: Repository Maintainers, Scientific Lead, Data Architect

## Context

The repository has established an immutable, byte-reproducible five-source catalog candidate (`mfp-catalog-candidate-v0.3.0`, packaged under `releases/`) covering 2,962 source records and 2,322 protein entities under deterministic scheme `MFPB_PROTEIN_ID_V1` ([ADR-005](ADR-005-deterministic-protein-ids.md)).

Earlier, [ADR-007](ADR-007-v1-scope-descope-bibliographic-relations.md) formally descoped bibliographic relations and external Gene Ontology (GO) enrichment from the initial catalog milestone (`mfp_catalog_v1`):

> "Roadmap Phase E (`mfp_catalog_v1` release) previously listed Phases D0/D — the laboratory annotation/evidence contract and the functional-assertion / bibliographic evidence graph — as dependencies... D0/D (bibliographic relations and pending bibliographic work) are FORMALLY OUT OF SCOPE for `mfp_catalog_v1`. They are not cancelled: they are DEFERRED to a future version." (ADR-007, lines 7–20)

ADR-007 also specified explicit prerequisite conditions under which a post-v1 version may incorporate functional assertions and bibliographic relations:
1. A versioned relation schema distinguishing protein identity, source record, functional assertion, GO term, reference, and support relation.
2. Complete per-relation provenance (source, extraction method, pipeline version, review status).
3. Availability of required identifiers from sources without invention.
4. Byte-stable reproduction and offline validation gates.

The research proposal `docs/roadmap/core/experiment-guio-v2.md` outlines an extensive scientific study spanning seven experimental blocks (B0–B6), 11 objectives, and 29 open decisions. Simultaneously, experimental code on `feature/functional-normalization` (`functional_normalization.py`) attempted an unverified normalization across all 2,322 catalog entities, but suffered from severe architectural flaws: a rigid 2-facet binary structure, unvalidated keyword regexes, arbitrary cellular component assignments, and external database coupling (documented in `docs/audits/2026-11-06_repository-sdd-functional-normalization-audit.md`).

A clear scope boundary is required to allow progressive, specification-driven research without prematurely committing the repository to the full experimental study or invalidating the catalog baseline.

## Decision

We propose a **bounded, staged extension** of repository scope dedicated exclusively to authoring and executing an offline **functional-normalization pilot**, subject to three strictly decoupled authorization levels:

1. **Level 1: Authorization to Prepare Specifications (Active User Authorization)**:
   - Author formal Specification-Driven Development (SDD) packages under `specs/` (specifications, plans, tasks, verification checklists).
   - Author proposed scope ADRs and agent guidelines.
   - *This level authorizes documentation and specification drafting ONLY. It does NOT authorize writing schemas to `data/curated/`, creating implementation code, running tests, or generating scientific outputs.*

2. **Level 2: Authorization to Implement a Bounded Pilot (Proposed; Pending Human Decision)**:
   - Implement schemas (`data/curated/functional_claims.schema.json`) and contract tests in `tests/`.
   - Implement offline, source-grounded claim extraction and normalization restricted to an isolated, multi-source pilot slice.
   - Require 100% offline execution using existing raw artifacts and local fixtures; strictly no live database connections or network downloads.
   - Defer semantic similarity metric engines, contextual triplet synthesis, and reference population comparisons.
   - Preserve the existing catalog baseline (`mfp_catalog_mvp`) and release packages (`releases/mfp-catalog-candidate-v0.3.0/`) as completely independent, immutable artifacts.
   - *Implementation will not proceed until this level receives explicit human sign-off.*

3. **Level 3: Authorization for Full Experimental Execution (Deferred)**:
   - Full-scale execution of Blocks B1–B6, semantic divergence calculations, NPMI associations, BioData reference matching, and curation releases (`MFP_CuratedData`) remains **deferred** until the pilot is completed, evaluated, and approved by the scientific lead.

## Relationship to ADR-007

This decision affirms that **ADR-007 established a milestone-specific exclusion for `mfp_catalog_v1`, not a permanent repository boundary**. 

By restricting the initial functional-normalization work to an isolated pilot specification that strictly fulfills ADR-007's four conditions (versioned schema, explicit provenance, no invented identifiers, offline verification), this decision enables scientific progression while maintaining the integrity and release readiness of `mfp_catalog_v1`.

## Consequences

- **Catalog Baseline Preservation**: The tables in `data/processed/mfp_catalog_mvp/` and the packaged candidates under `releases/` remain completely untouched. Pilot outputs will write to isolated paths (e.g. `data/interim/pilot/` or `data/processed/pilot/`).
- **Separation of Concerns**: Precludes the conflation of raw claim extraction with semantic similarity metric calculation or classifier training.
- **Architectural Hygiene**: Retires the ad-hoc 2-facet model (`BP1/MF1/CC1` vs `BP2/MF2/CC2`) in favor of a relational, one-to-many claim model that honors biological multiplicity.
- **Dependency Isolation**: Postpones the introduction of heavy scientific dependencies (`goatools`, `psycopg2`, `scipy`) until metric blocks are formally scheduled.

## Alternatives Considered

1. **Full Adoption of `experiment-guio-v2.md` (Blocks B0–B6)**: Rejected as premature. The roadmap contains 29 open decisions and unverified metric engines. Implementing the entire proposal at once invites architectural drift and untestable scope bloat.
2. **Strict Adherence to Catalog-Only Scope (Rejecting All Normalization)**: Rejected. Source databases contain valuable functional statements and citations that require structured normalization to support downstream research.
3. **Continuing with the Existing `functional_normalization.py` Code**: Rejected. The existing implementation violates core repository rules (regex heuristics, arbitrary CC assignments, unhandled mono-source cases).

## Deferred Questions

- Selection of the exact pilot cohort size and inclusion criteria (to be formalized in `specs/functional-normalization-pilot/spec.md`).
- Policy for handling QuickGO annotations with missing or unverified qualifiers (to be addressed in pilot review).
- Definition and mathematical formalization of contextual functional triplets (deferred to Block B3 under DEC-22).
