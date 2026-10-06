# Data Dictionary (Candidate mfp-catalog-candidate-v0.2.0)

## mfp_proteins.csv — grain: one protein entity
- `protein_id` (PK): deterministic SHA-256 digest, scheme MFPB_PROTEIN_ID_V1.
  `MFP:U:<16 hex>` = UniProt-resolved; `MFP:F:<source>:<16 hex>` = source-scoped
  fallback (no accession). One row per normalized UniProt accession.
- `canonical_uniprot_accession`: normalized accession (nullable: fallback entities).
- `canonical_name`, `canonical_organism`: representative raw values (nullable).
- `entity_status`: `resolved` (accession) or `unresolved_identity` (fallback).

## mfp_source_records.csv — grain: one source observation (row)
- PK: (`source_name`, `source_record_id`); `source_record_id` is stable per source
  (row-position based for Multitask/MultitaskProtDB-II snapshots).
- `protein_id` (FK -> mfp_proteins.protein_id): exactly one per record.
- `source_status`: repository POLICY-MAPPED status (MFPB_0_7,
  configs/source_claim_policy_v0.1.yaml), NOT a verbatim source label:
  MoonDB/PlantMP carry the policy-mapped value (e.g. PlantMP raw `likely` ->
  `excluded_likely`); MoonProt carries the loader-generated technical status
  `valid` (not a source evidence label); EMPTY (null) for MultifacetedProtDB
  and MultitaskProtDB-II — never invented.
- `operational_status`: repository administrative bucket (policy-mapped for
  MoonDB/PlantMP; neutral `unresolved` for status-less sources). NOT a
  scientific label.
- `raw_claim_field` / `raw_claim_value`: the VERBATIM source-provided label
  and its source field (MoonDB/PlantMP: field `type`, e.g. `Curated`,
  `Predicted`, `confirmed`, `likely`, `predicted`, original spelling/case);
  the authoritative location of source labels. `source_status` and
  `raw_claim_value` are NOT interchangeable, and source labels are NOT a
  cross-source evidence scale.
- `raw_path`, `raw_sha256` (per-record MoonProt HTML), `raw_file_sha256`
  (whole-file MoonDB/PlantMP/Multifaceted/Multitask artifacts).
- Raw-data columns (`genes_raw`, `annotation_raw`, `go_raw`, `go_moon_raw`,
  `reference_raw`, function/structure metadata): verbatim source data; empty
  (null) when the source provides nothing. Not verified annotations; not
  GO–article support.
- `reference_article_like` / `reference_anomaly`: field-level flags for
  non-article reference values; flagged values are never promoted to
  PMID/DOI.

## mfp_identifiers.csv — grain: one identifier claim per source record
- Natural key: (`protein_id`, `identifier_namespace`, `identifier_value`,
  `source_name`, `source_record_id`); `is_primary` marks the canonical UniProt row.

## mfp_assertions.csv — grain: one administrative assertion per source record
- Types: `source_status` (only when the source provides a status),
  `coverage_status`, `protein_name`, `uniprot_accession`, `operational_status`
  (only for sources with their own status). MultifacetedProtDB and
  MultitaskProtDB-II have zero evidence/status assertions: types limited to
  `coverage_status`, `protein_name`, `uniprot_accession`.
- No scientific evidence claims are created for status-less sources.

## mfp_coverage.csv — grain: one MoonProt MPID (snapshot universe 1..706)
- `status`: `acquired` (702), `known_absent` (1: MPID 103), `unresolved`
  (3: MPIDs 542/543/626). Coverage-only rows: never source records or proteins.
