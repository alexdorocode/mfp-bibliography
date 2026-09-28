# MultifacetedProtDB Source Profile

## Artifact Identity
- **Source ID**: `SRC_MULTIFACETEDPROTDB`
- **Formal name**: MultifacetedProtDB
- **Source status**: `imported`
- **Local artifacts**:
  - `data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt` — registered in
    `data/manifests/source_manifest.csv` and `file_checksums.sha256`.
  - `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` — registered as
    the canonical artifact in `data/manifests/source_manifest.csv` (SHA-256,
    127250 bytes, row_count_raw=1103) and in `file_checksums.sha256`.

## TXT artifact (verified)
- **SHA-256**: `23a68fe6e5d6e8fa25af67786cdd64836e3b28d83316174e1b9f70e638ffabb4` (matches `source_manifest.csv`)
- **Format**: Single-line comma-separated values, no header, no trailing newline; 7724 bytes.
- **Content**: UniProtKB accessions only. 1,103 entries, 1,103 unique, 0 duplicates, 0 blanks; all match the UniProt accession pattern and canonical case.
- **Unit of record**: protein identifier.

## JSON artifact (verified)
- **SHA-256**: `94bc65ded5615dc6a9b2ef37140c27b556fa4b8e387ee1bcd2d40c490625acd2` (not in any manifest).
- **Format**: single-quoted Python-literal structure, not strict JSON; parseable with `ast.literal_eval` (strict `json.load` fails). 127,250 bytes.
- **Top-level structure**: one key `protein` → list of 1,103 record dicts.
- **Fields (identical key set in all 1,103 records)**: `uniprot`, `name`, `genes`, `annotation`.
- **Missingness**: 0 missing/empty for all four fields; 0 duplicate `uniprot`; 0 malformed accessions; all accessions canonical case.
- **`annotation`**: float, values 5.0 (1,071), 4.0 (23), 3.0 (8), 2.0 (1). Semantics UNKNOWN — preserved verbatim, never mapped to a status or evidence label.
- **Sanitized example**: `{'uniprot': 'P36873', 'name': 'Serine/threonine-protein phosphatase PP1-gamma catalytic subunit', 'annotation': 5.0, 'genes': 'PPP1CC'}`.

## TXT vs JSON relationship (measured)
- Populations are **equivalent**: identical 1,103-accession sets, and TXT order equals JSON record order. TXT is an identifier-only projection of the JSON; the JSON is a strict information superset (adds name, genes, annotation).
- Discrepancy: only the JSON lacks manifest registration; no identifier discrepancies exist (0 in JSON-not-TXT, 0 in TXT-not-JSON).

## Canonical ingestion input (selected)
- **`MultifacetedProtDB_data.json`** — richer, same population, deterministic order.
- Registered in `source_manifest.csv` and `file_checksums.sha256`; the manifest row for
  `SRC_MULTIFACETEDPROTDB` now points at the canonical JSON (registration completed from
  measured local bytes; no hashes fabricated).
- The TXT remains the identifier-set cross-check; it is never ingested as records.
- Do not concatenate both artifacts; TXT adds no records and no fields.

## Status semantics
- No source status field exists. Per `configs/source_claim_policy_v0.1.yaml`, `SRC_MULTIFACETEDPROTDB` is an `unmapped_sources` entry: every claim gets `operational_status = unresolved` (the policy `default_status`), with the raw status value absent. Records are NOT confirmed/predicted/experimental by inclusion, and `annotation` must not be interpreted as evidence.
- Inclusion in the database is a membership fact only; the claim preserved is "source lists this UniProt with this name/genes/annotation value".

## Proposed ingestion contract (not implemented)
- **Row grain**: one claim row per JSON record (1,103).
- **source_record_id rule**: `multifacetedprotdb_row_{1-based index in artifact order}`; `raw_row_or_url` = row index (matches the MoonDB adapter convention).
- **claim_id**: `make_claim_id(source_id, source_record_id, raw_file_path, raw_row_or_url, raw_claim_field)` (existing helper).
- **Field mapping**: `uniprot_id` ← `uniprot` (canonical, exact-match identity only); `protein_name_raw` ← `name`; `organism_raw` ← absent (empty — do not invent); `raw_claim_field` = `annotation`, `raw_claim_value` = verbatim float text; `genes` preserved as an additional raw claim or in `notes` (decide at adapter time; never identity-bearing).
- **Identity**: cross-source merging only via exact normalized UniProt accession (`normalize_uniprot_accession`); no name/gene matching.
- **Duplicates**: fail the adapter on any duplicate accession (0 expected today).
- **Quarantine**: records with missing/malformed `uniprot` → quarantine table for review, never silently dropped or auto-included. Current count: 0.
- **References/GO**: none present in the artifact; no GO–article relation may be inferred from this source.
- **Provenance**: whole-file hash grain (`raw_file_sha256` from the manifest, as for MoonDB/PlantMP); no per-record hash exists.
- **Smallest adapter output**: `data/interim/source_claims_multifacetedprotdb.csv`, one row per record, validating against `data/curated/source_claims.schema.json`.
- **Baseline conservation equation**: 1,103 JSON records = 1,103 claim rows = 1,103 `SRC_MULTIFACETEDPROTDB` catalog source records, 0 dropped, 0 quarantined, and claims accessions = TXT identifier set (1,103). Final catalog protein/merge counts are NOT predicted here.
- **Tests needed**: record-count conservation; duplicate-accession failure; `unresolved` status (never confirmed/predicted); `annotation` preserved verbatim; empty `organism_raw` not invented; deterministic `claim_id`/`source_record_id`; strict parser rejects ambiguous structure; TXT-vs-JSON identifier cross-check.

## Adapter status (integrated into the catalog, contract MFPB_0_18_MFP_CATALOG_MVP_V1)
- Implemented: `src/mfp_bibliography/multifacetedprotdb_records.py` +
  `scripts/build_source_records_multifacetedprotdb.py` (offline, local-only).
- Output: `data/interim/source_records_multifacetedprotdb.csv` — 1,103 interim
  source records, one per JSON entry, deterministic
  `source_record_id = multifacetedprotdb_row_{1-based index}`; plus
  `source_records_multifacetedprotdb_validation_report.json`.
- Parsed with `ast.literal_eval` (never `eval`); the artifact is a single-quoted
  Python literal, NOT strict JSON. Hash verified against the manifest before
  output; shape, field-set, accession validity and uniqueness enforced with
  exact diagnostics; no partial outputs.
- Status: `status_original` empty (the source has no status field);
  `operational_status = unresolved` (policy `unmapped_sources` default).
  `annotation` values preserved verbatim; semantics unknown.
- TXT cross-check passes (identical 1,103-accession set).
- Catalog integration done: 1,103 JSON records = 1,103 interim source records =
  1,103 catalog source records; evidence claims remain 0 (the source has no
  status field; `source_status` empty, no status/evidence assertions emitted;
  `genes_raw`/`annotation_raw` preserved as uninterpreted raw data).

## Open Questions
- What is the biological meaning of the numeric `annotation` score?
- What version of MultifacetedProtDB does this dataset represent?
- What is the original source URL or DOI, and what license applies?
- Is there a primary publication describing this dataset?
- Why do the two artifacts coexist, and which did the source publish as authoritative?
