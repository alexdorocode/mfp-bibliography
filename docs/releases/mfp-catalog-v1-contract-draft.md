# Release Contract Draft — `mfp_catalog_v1`

**Status: DRAFT — not a release.** Nothing in this document declares,
versions, or publishes a release. The five-source candidates
[`mfp-catalog-candidate-v0.2.0`](../../releases/mfp-catalog-candidate-v0.2.0/)
(superseded, immutable) and
[`mfp-catalog-candidate-v0.3.0`](../../releases/mfp-catalog-candidate-v0.3.0/)
(current) are NOT `mfp_catalog_v1` ([roadmap Phase E](../roadmap/mfp-catalog-implementation-plan.md)).

- **Proposed release label:** `mfp_catalog_v1` (exact tag string to be
  decided at release time; no tag exists yet).
- **Draft owner:** repository maintainers.
- **Pending decisions:** source-data terms verification; tag/version policy.
  Corrected candidate packaging: DONE — [v0.3.0](mfp-catalog-candidate-v0.3.0.md)
  packaged. Repository license: DECIDED — AGPL-3.0-only
  for project-authored code and documentation (working tree: `LICENSE`,
  `NOTICE`); third-party data excluded. Scope decision recorded: D0/D
  formally out of scope for v1, deferred to a future version
  ([ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)).
  See the checklist below.

## 1. Scope

A versioned, byte-reproducible bibliographic and provenance catalog of
multifunctional/moonlighting proteins from five sources. Measured counts are
defined by the candidate manifest
([`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json),
`measured_counts`): 2,962 source records (MoonDB 351, MoonProt 702,
MultifacetedProtDB 1,103, MultitaskProtDB-II 694, PlantMP 112); 2,322 protein
entities; 463 cross-source shared accessions.

Not an MF-vs-NMF dataset, classifier, negative set, ML benchmark, or a
completed GO–article evidence graph
([ADR-001](../decisions/ADR-001-repository-scope.md)).

### v1 includes

- The five-source catalog (tables and grains per the packaged
  `DATA_DICTIONARY.md`).
- Identity merging only by exact normalized UniProt accession.
- Packaged source claims and end-to-end provenance.
- Offline PACKAGE_VERIFY validation of the packaged release.

### v1 excludes (formally out of scope — [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md))

- External bibliographic extraction or enrichment.
- Complete article-protein/DOI/PMID/GO relations.
- Exhaustive bibliographic coverage.

The ABSENCE of these relations in v1 is NOT absence of evidence about any
protein: absence from a source is never negative evidence, and record-level
references are never promoted to function-level support. D0/D are deferred,
not cancelled.

## 2. Identification

- Cross-source merging ONLY by exact normalized UniProt accession equality;
  no name, gene, organism or fuzzy matching; no external enrichment
  ([ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)).
- Deterministic protein IDs, scheme `MFPB_PROTEIN_ID_V1`.
- Provenance end to end; source claims verbatim
  ([ADR-002](../decisions/ADR-002-raw-data-immutability.md),
  [ADR-003](../decisions/ADR-003-provenance-and-transformations.md)).

## 3. Required release contents, schema, hashes, validation, reproduction

Per the [release policy](../release-policy.md), every release MUST contain:

1. Catalog tables: `mfp_proteins.csv`, `mfp_source_records.csv`,
   `mfp_identifiers.csv`, `mfp_assertions.csv`, `mfp_coverage.csv`
   (grains per the packaged `DATA_DICTIONARY.md`).
2. A release `MANIFEST.json`: release label, catalog contract ID, protein ID
   scheme, measured counts, input and output SHA-256 hashes, build commands.
3. `checksums.sha256` covering every packaged file.
4. `DATA_DICTIONARY.md` — CORRECTED (see blocker 3).
5. A packaged **validation report** artifact (release-policy requirement not
   yet present in candidate v0.2.0).
6. Release README declaring scope, limitations, hashes, schema version and
   reproduction order.

**Reproduction order (offline after inputs are in place):**

```bash
PYTHONPATH=src python scripts/build_mfp_catalog_mvp.py      # rebuild catalog
PYTHONPATH=src python scripts/package_catalog_candidate.py  # package (new version)
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package  # PACKAGE_VERIFY (offline)
```

`--verify` (REBUILD_COMPARE) compares packaged bytes against locally rebuilt
`data/processed/` outputs and requires hash-identical inputs not all
distributed in Git ([getting started](../getting-started.md)).

## 4. Required disclosures

- Source-provided labels are verbatim in `raw_claim_value`; repository
  policy-mapped `source_status` is reported separately and never called
  verbatim; MoonProt `valid` is a loader-generated technical status
  ([candidate erratum](mfp-catalog-candidate-v0.2.0.md)).
- Absence from a source is never negative evidence.
- MoonProt snapshot coverage: 702 acquired / 1 known absent (MPID 103) /
  3 unresolved (MPIDs 542, 543, 626) over the declared 1–706 universe
  ([ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md)).
  NO complete MoonProt coverage and NO complete bibliography is claimed.
- NO verified article-to-GO relations exist; GO/reference text is raw,
  uninterpreted source data.
- MultitaskProtDB-II reference anomalies (rows
  `multitaskprotdb_ii_row_239/349/422`) remain raw; not PMIDs/DOIs.
- `canonical_gene` and `taxonomy_id` are never populated by the builder;
  their emptiness is structural, not missing source metadata.
- Source labels are source-specific claims, not a shared evidence scale
  ([ADR-004](../decisions/ADR-004-evidence-label-benchmark-separation.md)).

## 5. Limitations (declarable, non-blocking)

- Retrieval dates unknown for the MultifacetedProtDB artifact and the
  MultitaskProtDB-II profile completeness review is open
  ([source profiles](../source-profiles/)).
- MoonProt acquisition is policy-governed; raw MoonProt HTML artifacts are
  not distributed in Git ([acquisition protocol](../acquisition-protocols/moonprot.md)).
- MultifacetedProtDB and MultitaskProtDB-II provide no source status; their
  `operational_status=unresolved` is administrative, never evidence.
- Status vocabularies are source-specific; no cross-source comparison.

## 6. Blockers before RELEASED

1. **Phase D0/D — APPROVED DESCOPE** (maintainers' decision,
   [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)):
   D0/D are formally out of scope for `mfp_catalog_v1` and deferred to a
   future version. NOT a blocker. A future version may incorporate D0/D only
   with: a versioned relation schema; per-relation provenance (extraction
   method, pipeline version, review status, scope, role); identifiers
   actually available from sources (never invented; anomalies never promoted
   to PMID/DOI); and defined validation/byte-stable reproduction for the new
   tables (ADR-007).
2. **Licenses:** resolve `terms_not_recorded` terms for the four tracked raw
   artifacts (`data/manifests/source_manifest.csv`). The repository license is
   decided: AGPL-3.0-only for project-authored code and documentation
   (`LICENSE`, `NOTICE`); third-party data is excluded from that grant and
   remains governed by its upstream terms.
3. **Corrected candidate — DONE:** candidate
   [v0.3.0](mfp-catalog-candidate-v0.3.0.md) packages the corrected
   `DATA_DICTIONARY.md` (erratum,
   [mfp-catalog-candidate-v0.2.0.md](mfp-catalog-candidate-v0.2.0.md)); catalog
   CSVs are byte-identical to v0.2.0. NOT a blocker.
4. **Tag/version policy and validation report:** define the tag string and
   versioning rules, and package a validation-report artifact.

## 7. Redistribution

This repository claims **no redistribution permission for any third-party
source dataset**. Tracked raw third-party artifacts are governed by their own
`terms_not_recorded` terms; distribution decisions precede any public release.

## 8. DRAFT → RELEASED checklist

| # | Item | Required decision / owner | Done when |
|---|---|---|---|
| 1 | Phase D0/D scope | Maintainers: **APPROVED DESCOPE** recorded ([ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)) | ADR accepted; roadmap updated; no non-negotiable rule violated |
| 2 | Source licenses | Maintainers: verify terms for 4 manifest entries | `license_or_terms` resolved in manifest |
| 3 | Repository license | Maintainers: DECIDED — AGPL-3.0-only (code/docs), third-party data excluded | `LICENSE` and `NOTICE` updated; README section updated |
| 4 | Corrected candidate | Maintainers: DONE — v0.3.0 packaged | v0.3.0 passes PACKAGE_VERIFY; dictionary corrected; CSVs byte-identical |
| 5 | Tag/version policy | Maintainers: define tag string + policy | Release policy updated; tag created at release |
| 6 | Validation report | Maintainers: package report artifact | Present in release; referenced by MANIFEST |
| 7 | Release contents | Maintainers: assemble per §3 | All §3 items present, hashes verified |
| 8 | Review | Maintainers: contract review vs ADRs/policy | Contract marked RELEASED; changelog entry added |

No version, date, or tag is invented by this draft.
