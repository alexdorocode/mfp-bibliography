# ADR-007: `mfp_catalog_v1` Scope Excludes Bibliographic Relations (Deferred)

- **Status**: Accepted

## Context

Roadmap Phase E (`mfp_catalog_v1` release) previously listed Phases D0/D —
the laboratory annotation/evidence contract and the functional-assertion /
bibliographic evidence graph — as dependencies. The five-source candidate
`mfp-catalog-candidate-v0.2.0` contains no verified article-to-GO relations:
all GO and reference text is raw, uninterpreted source data. Holding the v1
release hostage to D0/D would block a catalog that is otherwise complete,
traceable and offline-verifiable, while the roadmap's coverage caveat already
establishes that accurately-declared limitations do not block a release.

## Decision

D0/D (bibliographic relations and pending bibliographic work) are FORMALLY OUT
OF SCOPE for `mfp_catalog_v1`. They are not cancelled: they are DEFERRED to a
future version. The maintainers' scope decision is recorded in the
[release contract draft](../releases/mfp-catalog-v1-contract-draft.md) and the
[roadmap](../roadmap/mfp-catalog-implementation-plan.md).

`mfp_catalog_v1` therefore:

- **includes**: the five-source catalog; exact normalized UniProt accession
  identity merging only; packaged claims and provenance; offline
  PACKAGE_VERIFY validation.
- **excludes**: external bibliographic extraction or enrichment; complete
  article-protein/DOI/PMID/GO relations; exhaustive bibliographic coverage.

The absence of these relations in v1 is NOT absence of evidence about any
protein; per repository rules, absence from a source is never negative
evidence, and record-level references are never promoted to function-level
support.

## Conditions for a future version to incorporate D0/D

A post-v1 version may include D0/D only when all of the following hold:

1. A versioned relation schema exists, distinguishing protein identity,
   source record, functional assertion, GO term, reference and support
   relation (Phase D0 deliverable).
2. Every relation carries per-relation provenance: source or annotation
   system, extraction method, pipeline version, review status, scope and
   role; record-level citations are never promoted to function-level support.
3. Required identifiers (PMID/DOI/GO or source-native identifiers) are
   actually available from the source or annotation system — never invented;
   anomaly-flagged values are never promoted to PMID/DOI.
4. Validation and byte-stable reproduction are defined for the new tables
   (build, package, offline verify), following the same gates as v1.

## Consequences

- Phase E no longer depends on D0/D; the remaining v1 gates (licenses,
  corrected candidate, tag/version policy, packaged validation report) stand
  unchanged.
- Roadmap Phases D0/D are marked deferred to a post-v1 version, not blocked.
- v1 must disclose: no verified article-to-GO relations; no complete
  bibliography; raw reference text only.
- This decision violates no non-negotiable roadmap rule.
