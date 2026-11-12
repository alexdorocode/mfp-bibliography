# MultifacetedProtDB Source Profile

## Artifact Identity
- **Source ID**: `SRC_MULTIFACETEDPROTDB`
- **Formal name**: MultifacetedProtDB
- **Source status**: `imported`
- **Local artifacts**:
  - `data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt` — registered in
    `data/manifests/source_manifest.csv` and `data/manifests/file_checksums.sha256`.
  - `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` — registered as
    the canonical artifact in `data/manifests/source_manifest.csv` (SHA-256,
    127,250 bytes, row_count_raw=1103) and in `data/manifests/file_checksums.sha256`.

## TXT Artifact (Cross-Check Reference)
- **SHA-256**: `23a68fe6e5d6e8fa25af67786cdd64836e3b28d83316174e1b9f70e638ffabb4` (matches `source_manifest.csv`)
- **Format**: Single-line comma-separated values, no header, no trailing newline; 7724 bytes (7,724 bytes).
- **Content**: UniProtKB accessions only. 1,103 entries, 1,103 unique, 0 duplicates, 0 blanks; all match the UniProt accession pattern and canonical case.
- **Unit of record**: Protein identifier string.

## JSON Artifact (Canonical Raw Input)
- **SHA-256**: `94bc65ded5615dc6a9b2ef37140c27b556fa4b8e387ee1bcd2d40c490625acd2`
- **Format**: Single-quoted Python-literal structure, not strict JSON; parseable with `ast.literal_eval` (strict `json.load` fails). 127,250 bytes.
- **Top-level structure**: One key `protein` → list of 1,103 record dicts.
- **Fields (identical key set in all 1,103 records)**: `uniprot`, `name`, `genes`, `annotation`.
- **Missingness**: 0 missing/empty for all four fields; 0 duplicate `uniprot`; 0 malformed accessions; all accessions canonical case.
- **Raw score distribution** (Unit: JSON record objects, Artifact: `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json`, Version: canonical raw snapshot):
  - `5.0`: 1,071 records (97.1%)
  - `4.0`: 23 records (2.1%)
  - `3.0`: 8 records (0.7%)
  - `2.0`: 1 record (0.1%)
  - Total: 1,103 records
- **Score semantics**: UNKNOWN — preserved verbatim, never mapped to an operational status or evidence tier.
- **Sanitized example**: `{'uniprot': 'P36873', 'name': 'Serine/threonine-protein phosphatase PP1-gamma catalytic subunit', 'annotation': 5.0, 'genes': 'PPP1CC'}`.

## TXT vs JSON Relationship (Measured)
- Populations are **equivalent**: identical 1,103-accession sets, and TXT order equals JSON record order. TXT is an identifier-only projection of the JSON; the JSON is a strict information superset (adds name, genes, annotation).
- Discrepancy: no identifier discrepancies exist (0 in JSON-not-TXT, 0 in TXT-not-JSON).
- **Ingestion selection**: `MultifacetedProtDB_data.json` is selected as the richer, canonical ingestion input. The TXT remains the byte-level identifier cross-check and is never ingested separately.

## Status Semantics
- No source status field exists. Per `configs/source_claim_policy_v0.1.yaml`, `SRC_MULTIFACETEDPROTDB` is an `unmapped_sources` entry: every record gets `operational_status = unresolved` (the policy `default_status`), with the raw status value absent. Records are NOT confirmed/predicted/experimental by inclusion, and `annotation` must not be interpreted as evidence.
- Inclusion in the database is a membership fact only; the claim preserved is "source lists this UniProt with this name/genes/annotation value".

## Historical Ingestion Design Contract (Implemented and Integrated)
- **Row grain**: One claim row per JSON record (1,103).
- **source_record_id rule**: `multifacetedprotdb_row_{1-based index in artifact order}`; `raw_row_or_url` = row index (matches the MoonDB adapter convention).
- **claim_id**: `make_claim_id(source_id, source_record_id, raw_file_path, raw_row_or_url, raw_claim_field)`.
- **Field mapping**: `uniprot_id` ← `uniprot` (canonical, exact-match identity only); `protein_name_raw` ← `name`; `organism_raw` ← absent (empty — do not invent); `raw_claim_field` = `annotation`, `raw_claim_value` = verbatim float text; `genes` preserved as uninterpreted raw data.
- **Identity**: Cross-source merging only via exact normalized UniProt accession (`normalize_uniprot_accession`); no name/gene matching.
- **Duplicates**: Fail the adapter on any duplicate accession (0 observed).
- **Quarantine**: Records with missing/malformed `uniprot` → quarantine table for review, never silently dropped or auto-included. Current count: 0.
- **References/GO**: None present in the artifact; no GO–article relation may be inferred from this source.
- **Provenance**: Whole-file hash grain (`raw_file_sha256` from the manifest); no per-record hash exists.
- **Adapter output**: `data/interim/source_records_multifacetedprotdb.csv`, one row per record.
- **Baseline conservation equation**: 1,103 JSON records = 1,103 interim source records = 1,103 `SRC_MULTIFACETEDPROTDB` catalog source records, 0 dropped, 0 quarantined, and claims accessions = TXT identifier set (1,103).

## Catalog Integration and Lifecycle Distinctions

### 1. Packaged Candidate v0.3.0 (`releases/mfp-catalog-candidate-v0.3.0/`)
- **Governing contract**: `MFPB_0_19_MFP_CATALOG_MVP_V2` (incorporating contract `MFPB_0_18_MFP_CATALOG_MVP_V1`).
- **Interim source records**: `data/interim/source_records_multifacetedprotdb.csv` (1,103 interim source records, one per JSON entry, deterministic `source_record_id = multifacetedprotdb_row_{1-based index}`).
- **Validation report**: `data/interim/source_records_multifacetedprotdb_validation_report.json`.
- **Packaged outputs**:
  - `mfp_source_records.csv`: Exactly 1,103 source records with `source_id = SRC_MULTIFACETEDPROTDB`.
  - `mfp_assertions.csv`: 0 assertion claims emitted (the source has no status field; `status_original` empty, `operational_status = unresolved`).
- **Entity merging**: All 1,103 accessions are valid canonical UniProt accessions; they converge deterministically with entities from other sources sharing identical normalized accessions.

### 2. Committed Implementation
- **Source record adapter**: `src/mfp_bibliography/multifacetedprotdb_records.py` and CLI `scripts/build_source_records_multifacetedprotdb.py` (offline, local-only).
- **Parser guarantees**: Parsed with `ast.literal_eval` (never `eval`); hash verified against the manifest before output; shape, field-set, accession validity and uniqueness enforced with exact diagnostics; no partial outputs.
- **Catalog build integration**: `scripts/build_mfp_catalog_mvp.py` ingests the interim source records directly into the unified catalog tables.

### 3. Uncommitted / Experimental Development
- MultifacetedProtDB is **excluded** from the active three-source functional normalization pilot cohort (`data/interim/pilot/`), as it carries no functional statements, GO annotations, or literature references.

### 4. Proposed Capabilities
- No further extraction or normalization is planned for this source under [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) due to the absence of functional and bibliographic fields.

## Activity Domain Accounting

| Activity Domain | Status in Candidate v0.3.0 | Status in Development / Pilot | Reference / Governing Boundary |
|---|---|---|---|
| **Catalog Ingestion** | **Integrated**: 1,103 source records; 0 evidence claims | Fully reproducible offline | Contract `MFPB_0_18_MFP_CATALOG_MVP_V1` |
| **Functional Extraction** | **None**: No functional descriptions exist in raw artifact | Excluded from pilot cohort | [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **GO Annotation Handling** | **None**: No GO terms exist in raw artifact | Excluded from pilot cohort | [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Local Bibliographic Review** | **None**: No citations exist in raw artifact | Formally out of scope for v1 | [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) |

## Open Questions
- What is the biological meaning of the numeric `annotation` score (5.0, 4.0, 3.0, 2.0)?
- What version of MultifacetedProtDB does this dataset represent?
- What is the original source URL or DOI, and what license applies?
- Is there a primary publication describing this dataset?
- Why do the two artifacts coexist, and which did the source maintainers publish as authoritative?
