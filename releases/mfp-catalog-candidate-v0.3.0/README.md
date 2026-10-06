# MFP Catalog Candidate mfp-catalog-candidate-v0.3.0

**STATUS: CANDIDATE — this is NOT the final v1 release.**

Accession-first bibliographic and analytical candidate catalog of
multifunctional/moonlighting proteins (MF/MFP) from five sources:
MoonDB (351),
MoonProt (702),
MultifacetedProtDB (1103),
MultitaskProtDB-II (694),
PlantMP (112).

## Scope and identity
- Catalog contract: MFPB_0_19_MFP_CATALOG_MVP_V2; protein ID scheme: MFPB_PROTEIN_ID_V1.
- Identity rule: cross-source merging ONLY by exact normalized UniProt accession
  equality. No name, gene, organism or fuzzy matching; no external enrichment.
- Every source observation links to its protein via `protein_id`; per-source
  labels are preserved verbatim and are source-specific claims, never global
  truth labels. Absence from a source is never negative evidence.

## Count definitions (kept separate)
- Source-record count: 2962 — one row per source observation.
- Unique protein entities: 2322 — one per normalized accession.
- Shared-accession merges: 463 — accessions claimed by
  two or more sources. This is a separate metric; it is NOT
  source-record-count minus protein-entity-count.
- Repeated observations within a source also exist (e.g. MultitaskProtDB-II
  annotation-entry grain: 9 accessions with 2 rows each).

## Source statuses
- Verbatim source-provided labels live in `raw_claim_value` (contextualized by
  `raw_claim_field`; MoonDB/PlantMP field `type`), preserved with original
  spelling/case.
- `source_status` is the repository POLICY-MAPPED status (MFPB_0_7), not a
  verbatim label; MoonProt's `source_status=valid` is a loader-generated
  technical status, not a source evidence label.
- MultifacetedProtDB and MultitaskProtDB-II have NO explicit source evidence
  status. Their `operational_status=unresolved` is a neutral administrative
  policy value, NOT a scientific label and NOT evidence.
- Source labels are source-specific; they are NOT a cross-source evidence
  scale and are never compared or harmonized across sources.

## Deferred
- A packaged `validation_report.json` artifact is deferred to the
  `mfp_catalog_v1` release (release-contract gate 4); this candidate is
  verified by the offline PACKAGE_VERIFY command below.

## Limitations
- No verified article-to-GO relationships exist in this candidate. All
  reference and GO text is raw, uninterpreted source data.
- MultitaskProtDB-II reference anomalies (rows
  multitaskprotdb_ii_row_239/349/422) remain raw and unverified; they are not
  PMIDs/DOIs.
- MoonProt MPIDs 542, 543 and 626 are unresolved; MPID 103 is known absent
  (coverage-only). MoonProt coverage is 702/1/3 — NOT complete MoonProt
  coverage is claimed, and no complete bibliography is claimed.
- Known-absent and unresolved MoonProt MPIDs never create protein entities
  (ADR-006).
- Not an MF-vs-NMF dataset; no negative set; no classifier or ML benchmark.

## Reproduction
See `MANIFEST.json` (`build_commands`, `verification_command` = offline
PACKAGE_VERIFY, `rebuild_compare_command` = REBUILD_COMPARE against locally
rebuilt outputs) and `checksums.sha256`. Byte-stable across runs and Python
hash seeds.
