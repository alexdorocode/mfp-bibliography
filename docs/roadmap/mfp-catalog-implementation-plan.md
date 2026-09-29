# MFP Catalog Implementation Roadmap

## Metadata

- **Document status:** living
- **Owner:** repository maintainers
- **Last reviewed:** 2026-09-28
- **Update rule:** update after each completed, blocked, superseded, or materially re-scoped milestone.

## Documentation governance

- **Vision** ([project charter](../project-charter.md)): stable scope and success definition.
- **Roadmap** (this document): phase status and next work.
- **Source profiles** ([source-profiles/](../source-profiles/)): source semantics and ingestion facts.
- **ADRs** ([decisions/](../decisions/)): durable architecture and policy decisions.
- **Changelog** ([CHANGELOG.md](../../CHANGELOG.md)): completed externally visible changes.

Evidence-bearing counts must be linked to reproducible outputs (generated artifacts, reports, checksums), never manually maintained as an independent source of truth.

## Non-negotiable rules

- MF/MFP-only catalog: no MF-vs-NMF dataset, classifier, negative set, or ML benchmark.
- Absence from a source is never negative evidence.
- Provenance is preserved end to end; source claims are retained verbatim.
- Source terms (predicted, likely, curated, confirmed, candidate, unresolved) are source-specific claims or metadata, not a global binary truth label.
- Automatic cross-source identity merging is limited to exact normalized UniProt accession equality; no fuzzy, name, gene, or organism matching, and no external enrichment.
- No silent deletion of records or claims; no inferred enrichment.
- Bibliographic references are modeled as sourced relations, not intrinsic protein properties.
- Semantic or schema changes follow release/version discipline (see [release policy](../release-policy.md) and ADRs).

## Current baseline (snapshot)

Snapshot as of 2026-09-28; counts from `data/processed/mfp_catalog_mvp/summary.json`.

- **Build command:** `PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py`
- 2,962 source records; 2,322 protein entities; 463 exact-UniProt merges.
- Included sources: MoonProt 702 (see [acquisition protocol](../acquisition-protocols/moonprot.md)); MoonDB 351 ([profile](../source-profiles/moondb.md)); PlantMP 112 ([profile](../source-profiles/plantmp.md)); MultifacetedProtDB 1,103 ([profile](../source-profiles/multifacetedprotdb.md)); MultitaskProtDB-II 694 ([profile](../source-profiles/multitaskprotdb-ii.md), annotation-entry grain; 685 accessions; evidence claims 0).
- MoonProt coverage-only MPIDs ([ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md)): MPID 103 known absent; MPIDs 542, 543, 626 unresolved (identifiers, not counts). They carry no source records or protein entities.
- [MultifacetedProtDB](../source-profiles/multifacetedprotdb.md) and [MultitaskProtDB-II](../source-profiles/multitaskprotdb-ii.md): raw data only, not ingested.

## Phases

### Phase A — Baseline catalog stabilization

- **Status:** completed.
- **Objective:** reproducible MVP catalog from MoonProt, MoonDB, and PlantMP with full provenance.
- **Evidence:** `summary.json` counts above; `tests/test_mfp_catalog_mvp.py`.
- **Smallest deliverable:** MVP catalog under `data/processed/mfp_catalog_mvp/`.
- **Acceptance criteria:** record counts conserved; every record traceable to its source; deduplication only via exact normalized UniProt accession.
- **Out of scope:** negative sets, external enrichment, fuzzy merging.
- **Blockers / limitations:** none for the MVP scope; unresolved MoonProt MPIDs remain open.
- **Next action:** none; superseded by Phases B–E.

### Phase B — MultifacetedProtDB profiling and ingestion

- **Status:** completed (catalog contract MFPB_0_18_MFP_CATALOG_MVP_V1). The source provides no status/evidence field: 1,103 records ingested as source data with zero invented claims; `operational_status` is derived-administrative only.
- **Objective:** profile the raw artifact and ingest records and claims as source-specific assertions.
- **Evidence:** raw data in `data/raw/multifacetedprotdb/`; [source profile](../source-profiles/multifacetedprotdb.md).
- **Smallest deliverable:** completed source profile plus populated `mfp_assertions` rows.
- **Acceptance criteria:** each claim retains its original source label verbatim; provenance complete.
- **Out of scope:** new data acquisition; relabeling or transforming source claims.
- **Blockers / limitations:** retrieval date of the raw artifact is unknown locally.
- **Next action:** none; ingestion is complete (traceability R20). Open limitation: the raw artifact's retrieval date is unknown locally.

### Phase C — MultitaskProtDB-II profiling and ingestion

- **Status:** completed (catalog contract MFPB_0_19_MFP_CATALOG_MVP_V2). 694 annotation-entry rows ingested; repeated accessions are distinct observations; zero invented claims; reference anomalies stay attached to their rows.
- **Objective:** same treatment as Phase B for MultitaskProtDB-II.
- **Evidence:** raw data in `data/raw/multitaskprotdb-ii/`; [source profile](../source-profiles/multitaskprotdb-ii.md).
- **Smallest deliverable:** records ingested with complete provenance.
- **Acceptance criteria:** deduplication only by exact normalized UniProt accession.
- **Out of scope:** fuzzy or inferred merges.
- **Blockers / limitations:** profile completeness not yet reviewed against the raw artifact.
- **Next action:** ingestion is complete (traceability R21, contract `MFPB_0_19_MFP_CATALOG_MVP_V2`); remaining open item is the profile-completeness review against the raw artifact.

### Phase D0 — Annotation and evidence data contract

- **Status:** planned — laboratory integration is explicitly deferred: the five-source candidate contains no verified article-to-GO relations, and no laboratory-system implementation has started.
- **Objective:** define versioned schemas, controlled vocabularies, identifiers,
  provenance requirements, validation rules, and interchange contract for the
  laboratory annotation-retrieval system.
- **Smallest deliverable:** an ADR plus JSON/CSV schema definitions and
  representative fixtures.
- **Acceptance criteria:** the contract distinguishes protein identity,
  source record, functional assertion, GO term, reference, and support relation;
  supports assertion-level and record-level citations; and specifies required
  provenance fields.
- **Out of scope:** bulk annotation retrieval or bibliographic metadata
  enrichment.
- **Next action:** produce an entity-relationship model and field dictionary;
  GO evidence-code and reference semantics are governed by the
  [GO annotation, evidence-code and bibliography contract](../bibliography/go-annotation-evidence-contract.md).

### Phase D — Functional assertions and bibliographic evidence graph

- **Status:** planned — explicitly deferred until the candidate is stabilized and Phase D0's contract exists; no implementation started.
- **Objective:** represent protein–function/GO–reference relations with
  assertion-level provenance, using the laboratory annotation-retrieval system.
- **Evidence:** existing `mfp_proteins`, `mfp_source_records`,
  `mfp_assertions`, and `mfp_identifiers` outputs; laboratory system contract
  to be documented.
- **Smallest deliverable:** versioned schemas and a fixture-backed prototype
  producing `mfp_function_assertions`, `mfp_references`,
  `mfp_assertion_references`, and `mfp_record_references`.
- **Acceptance criteria:**
  - every assertion is linked to one protein and provenance source;
  - GO IDs remain optional and free-text functions are retained;
  - every reference relation declares its scope and role;
  - record-level references are not promoted to function-level support;
  - extraction method, pipeline version, and review status are recorded;
  - no identifier or reference is assigned across distinct protein entities
    without an explicit assertion-level provenance path.
- **Out of scope:** inferring unsupported GO mappings, treating citations as
  universal proof of every function, external enrichment without provenance,
  and global truth labels.
- **Blockers / limitations:** laboratory-system output contract, controlled
  vocabularies, and source-specific functional-field coverage must be defined.
- **Next action:** write the bibliographic and functional assertion data
  contract before implementation.

### Phase E — Reproducible `mfp_catalog_v1` release

- **Status:** planned.
- **Objective:** publish a versioned, byte-reproducible catalog with total traceability.
- **Evidence:** checksum-pinned precedent in [pre-MoonProt baseline v0.1](../releases/pre-moonprot-baseline-v0.1.md); five-source candidate packaged at [mfp-catalog-candidate-v0.2.0](../releases/mfp-catalog-candidate-v0.2.0.md).
- **Smallest deliverable:** packaged catalog CSV plus relational tables, versioned.
- **Acceptance criteria:** release declares scope, limitations, file hashes, schema version, and reproduction order.
- **Out of scope:** claims of complete MoonProt coverage while MPIDs remain unresolved.
- **Blockers / limitations:** depends on Phases B–D0-D.
- **Next action:** draft the final `mfp_catalog_v1` release contract; the candidate v0.2.0 under `releases/` is NOT final v1.

## Coverage caveat

Unresolved MoonProt MPIDs block any claim of complete MoonProt coverage. They do not automatically block a catalog release that accurately declares its scope and limitations.

## Roadmap update checklist

1. Update each phase's status (completed, in progress, blocked, planned).
2. Refresh the baseline snapshot and link counts to reproducible outputs.
3. Record the concrete next action for every active phase.
4. Check source profiles for changed source semantics or ingestion facts.
5. Add an ADR for any durable architecture or policy decision.
6. Record externally visible changes in `CHANGELOG.md`.
7. Verify counts against generated artifacts, never manual notes.
8. Confirm planned work violates no rule in "Non-negotiable rules".
- Functional claims, GO terms, and references are separate entities.
  A reference is linked to a functional assertion only when the source or
  annotation system provides an explicit assertion-level relation.
- A record-level citation must not be promoted to support for every function
  or GO term in that record.
- GO IDs are optional controlled identifiers; free-text functions must be
  retained when no defensible GO mapping exists.
- Evidence codes, qualifiers, relation types, provenance, extraction method,
  review status, and pipeline version must be retained whenever available.
- Bibliographic retrieval output is versioned, auditable, and additive; it
  does not overwrite raw-source claims or prior releases.