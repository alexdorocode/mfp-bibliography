# MultitaskProtDB-II Source Profile

## Artifact Identity
- **Source ID**: `SRC_MULTITASKPROTDB_II`
- **Formal name**: MultitaskProtDB-II
- **Source status**: `imported`
- **Local artifact path**: `data/raw/multitaskprotdb-ii/proteins.csv`

## Observed Structure
- **Filename**: `proteins.csv`
- **File size**: 1324061 bytes
- **SHA-256 checksum**: `84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482`
- **Encoding**: UTF-8 with BOM (UTF-8-SIG)
- **Line endings**: CRLF (Windows-style, `\r\n`)
- **Trailing newline**: No
- **Format**: Comma-separated values (CSV)
- **Delimiter**: Comma (`,`)
- **Header row**: Line 1 (present)
- **Total lines**: 14,291 (1 header + 14,290 lines)
- **Data rows**: 694

## Columns
| Position | Field Name | Data Type | Nullable | Unique | Cardinality | Description |
|---|---|---|---|---|---|---|
| 1 | `UniProt` | string | No | No | 685 | UniProt accession identifier |
| 2 | `Protein_Name` | string | No | No | 517 | Protein name |
| 3 | `Long_Description` | integer | Yes | No | 1 | Long description (mostly empty/null) |
| 4 | `Canonical_Function` | string | No | No | 457 | Canonical function description |
| 5 | `GO` | string | No | No | 555 | Gene Ontology terms |
| 6 | `Moonlighting_function` | string | No | No | 557 | Moonlighting function description |
| 7 | `GO_Moon` | string | Yes | No | 495 | Gene Ontology terms for moonlighting functions |
| 8 | `Organism` | string | Yes | No | 184 | Organism name |
| 9 | `Human_Disease` | string | Yes | No | 129 | Human disease associations |
| 10 | `Drugs` | string | Yes | No | 79 | Drug associations |
| 11 | `Induction` | integer | Yes | No | 1 | Induction information (mostly empty/null) |
| 12 | `PDBs` | string | Yes | No | 601 | Protein Data Bank identifiers |
| 13 | `PDB_UniProt` | string | Yes | No | 301 | PDB to UniProt mapping |
| 14 | `Models` | string | No | No | 2 | Modeling method/structure prediction |
| 15 | `Reference` | string | Yes | No | 469 | Reference information |

## Identifier Analysis
- **Primary identifier field**: `UniProt` (column 1)
- **Identifier type**: UniProt accession
- **Total identifiers**: 694 entries
- **Unique identifiers**: 685 (9 entries are duplicated or shared)
- **Format validation**: Entries appear to be standard UniProt accession codes
- **Note**: No identifier candidate detected by profiler due to non-unique values; however, `UniProt` is the primary identifier column

## Raw Category Distribution
- **No explicit source-native category column** identified in the raw artifact
- **Models column distribution** (observed structural/modeling categories):
  - `Phyre`: 690 entries (99.4%)
  - `ITasser`: 4 entries (0.6%)
- **Important**: These values are observed in the data but are NOT mapped to repository scientific labels (`scientific_label`), evidence tiers (`evidence_tier`), or benchmark roles (`benchmark_role`). They are preserved as observed structural modeling method identifiers.

## Integrity Record
- **Checksum verified**: `84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482`
- **File size verified**: 1,324,061 bytes
- **Row count verified**: 694 data rows
- **Raw artifact unchanged**: Confirmed byte-for-byte identical before and after profiling
- **No mutations**: No modifications, renames, re-encoding, or overwrites performed on raw artifact

## Repository Interpretation
- **Unit of record**: protein
- **Source version**: `unknown` (not provided in artifact or accompanying documentation)
- **Retrieval date**: `unknown` (not provided in artifact or accompanying documentation)
- **Original artifact location**: `unknown` (not provided)
- **License / terms**: `to_be_verified` (requires source confirmation)
- **Primary publication**: `to_be_verified` (requires source confirmation)
- **Benchmark role**: `unassigned` (per repository policy, no scientific mapping implemented)

## Open Questions
- What is the exact version of MultitaskProtDB-II that this dataset represents?
- What is the original source URL or DOI for this dataset?
- What license or terms of use apply to this data?
- What is the primary publication describing this dataset?
- What is the relationship between `Canonical_Function` and `Moonlighting_function` columns?
- Are the GO term columns (`GO`, `GO_Moon`) standardized or source-specific in their format?
- What do the `Models` values (Phyre, ITasser) represent in the context of this dataset?
- Why does the file have 14,291 lines but only 694 data rows?
- Why do some columns have integer data type (e.g., `Long_Description`, `Induction`)?

## Verification Checklist
- [x] File exists at declared path
- [x] SHA-256 checksum verified
- [x] File size matches manifest
- [x] Row count verified
- [x] Column structure documented
- [x] Encoding confirmed (UTF-8-SIG with BOM)
- [x] Delimiter confirmed (comma)
- [x] Line ending confirmed (CRLF)
- [x] No network access required for profiling
- [x] Raw artifact remains byte-for-byte unchanged

## Generated
- **Profile date**: 2026-09-18
- **Profiler version**: v1.2 (with UTF-8-SIG BOM support and quoted CSV field support)

---

## Measured Analysis (2026-09-28, accession-first ingestion profiling)

### Hash and structure verification (re-measured)
- SHA-256 recomputed from local bytes: `84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482` — matches `source_manifest.csv` and `file_checksums.sha256`; manifest untouched.
- 1,324,061 bytes; UTF-8-SIG (BOM); CRLF line terminators inside records; no trailing newline; comma delimiter; header row present; 694 data rows, all with exactly 15 fields; 0 fully duplicated rows. The 14,291 physical lines come from quoted multi-line fields (GO, GO_Moon, Reference).

### Row grain (measured)
- Grain is NOT one-protein-per-row: 694 rows carry 685 distinct accessions; 9 accessions appear in 2 rows each, and the paired rows differ in `Protein_Name`, `GO`, `Moonlighting_function`/`Canonical_Function`, `GO_Moon`, `Organism` and `Reference` (e.g., rows 15/16 for A1KFR2). The source itself is not protein-normalized; the closest description is "protein annotation entry".
- 0 multi-accession cells (no cell contains two accessions); 0 non-canonical-case accessions; all 685 accessions match the 6- or 10-character UniProt accession pattern.

### Key statistics
- Stable source key candidate: `(row number in artifact order)` — `UniProt` is NOT unique (9 duplicates).
- Missing keys: 0 (no row lacks an accession). Duplicate keys: 9 (differing annotation rows, not redundant copies). Multi-accession records: 0.

### Field inventory and missingness (694 rows)
| Field | Missing | Notes |
|---|---|---|
| `UniProt` | 0 | unique 685/694; canonical case; all match accession pattern |
| `Protein_Name` | 0 | name raw value |
| `Long_Description` | 694 | 100% empty — never invent content |
| `Canonical_Function` | 0 | free-text function; source data, not GO evidence |
| `GO` | 0 | GO annotations WITH evidence codes (e.g., `GO:0005840; C:ribosome; IEA:UniProtKB-KW.`); codes seen include IEA, IDA, TAS, IMP, IBA, IPI, NAS, IEP |
| `Moonlighting_function` | 0 | free-text moonlighting function |
| `GO_Moon` | 11 | GO annotations for moonlighting functions, same format |
| `Organism` | 1 | row for Q6L047 lacks organism — store absent |
| `Human_Disease` | 556 | disease text; metadata, not evidence |
| `Drugs` | 611 | drug text; metadata |
| `Induction` | 694 | 100% empty |
| `PDBs` | 77 | PDB identifiers; structural metadata |
| `PDB_UniProt` | 389 | structural metadata |
| `Models` | 0 | Phyre (690) / ITasser (4); excluded_fields per policy — structural metadata, never evidence |
| `Reference` | 1 | bare PubMed numbers (e.g., `24814782`); no `PMID:` prefix; 0 multi-value cells; 2 anomalies: `HIV-1 and murine leukemia virus infection (omim:600534)` and `4ENL` (PDB-like) — quarantine candidates, not article IDs |

### Labels vs membership
- There is NO source status/label field. Database membership is a membership fact only. No confirmed/predicted/experimental label may be inferred; `Models`, `PDBs`, `PDB_UniProt`, `Human_Disease`, `Drugs` are structural/administrative metadata, never evidence of multifunctionality.
- GO/GO_Moon content is source-provided annotation data. Per the GO contract, it is preserved as raw source data; evidence codes are retained verbatim; a record-level `Reference` is a record-level citation only and NEVER becomes GO-level support (no GO–article relation exists in this source).
- Policy gap: `SRC_MULTITASKPROTDB_II` is not yet in `source_claim_policy_v0.1.yaml` `unmapped_sources` (only its `Models` field is excluded). The ingestion contract REQUIRES adding it to `unmapped_sources` so the neutral `operational_status = unresolved` applies; no invented claim.

### Ingestion contract (proposed; NOT implemented — fifth source NOT integrated)
- **Row grain policy**: one input row → one interim source record, keyed by `source_record_id = multitaskprotdb_ii_row_{1-based file row}` (row order is stable and the accession is not unique). The 9 same-accession rows remain 9 distinct source records sharing one protein entity — no record is dropped, merged or de-duplicated.
- **Identity**: protein identity via exact normalized UniProt accession only (`normalize_uniprot_accession`); no name/gene/organism matching. Multiple rows of one accession converge on one protein entity automatically via the accession; no protein merging beyond that.
- **Quarantine rules**: rows with missing/malformed accession (none today); `Reference` values that are not article-like identifiers (2 measured anomalies) must be preserved verbatim and quarantined from any future article-relation work, never coerced into PMIDs. Nothing is silently discarded.
- **Conservation equation**: 694 raw rows = 694 interim source records = 694 catalog source records; 0 dropped; 0 quarantined for accession reasons; 685 protein-accession identities (9 shared). Catalog protein/merge counts are NOT predicted here.
- **Hash binding**: raw→interim: adapter verifies the recomputed file SHA-256 against `source_manifest.csv` before output; interim→catalog: every interim row carries `raw_file_path` + `raw_file_sha256` + `transformation_id` and the catalog loader fails closed on any mismatch (same pattern as MultifacetedProtDB).
- **Minimal adapter output**: `data/interim/source_records_multitaskprotdb_ii.csv` with per-row: source id, `source_record_id`, `uniprot_raw`, `uniprot_normalized`, `protein_name_raw`, `organism_raw`, function texts (`canonical_function_raw`, `moonlighting_function_raw`), GO blocks (`go_raw`, `go_moon_raw`) preserved verbatim, `reference_raw`, structural metadata (`pdbs_raw`, `pdb_uniprot_raw`, `models_raw`), `status_original` empty, `operational_status=unresolved` (after policy update), raw path/hash, transformation id. No evidence claims; no GO–article relations.
- **Tests needed**: hash mismatch; encoding/BOM+CRLF parse; 694-record conservation; the 9 same-accession rows remain distinct records with one protein entity; missing organism stored absent (Q6L047); 2 malformed `Reference` values preserved and flagged; no status/evidence assertions; deterministic `source_record_id`; GO text preserved verbatim.

### Metric note (verified, not changed)
- Current summary `exact_uniprot_merges = 184` counts normalized accessions claimed by ≥2 sources in the four-source catalog; the integration note's "163 overlaps" counts MultifacetedProtDB accessions already present among the previous three sources' proteins. They agree exactly: 45 (old three-source merges) + 163 (MF∩old proteins) − 24 (already merged among old sources and also in MF) = 184. No counts were altered.

### Adapter status (interim; NOT integrated into the catalog)
- Policy: `SRC_MULTITASKPROTDB_II` added to `unmapped_sources` in
  `configs/source_claim_policy_v0.1.yaml` (neutral `operational_status=unresolved`).
- Implemented: `src/mfp_bibliography/multitaskprotdb_ii_records.py` +
  `scripts/build_source_records_multitaskprotdb_ii.py` (offline, local-only).
- Output: `data/interim/source_records_multitaskprotdb_ii.csv` — 694 interim
  source records (685 distinct accessions; the 9 same-accession rows remain
  distinct records), plus
  `source_records_multitaskprotdb_ii_validation_report.json`.
- `source_record_id = multitaskprotdb_ii_row_{1-based data-row position}` is
  bound to source ID, the pinned raw SHA-256
  (`84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482`) and row
  position; a future reordered snapshot requires a new transformation version,
  never silent ID reuse. Hash verified against the manifest before parsing;
  UTF-8-SIG/BOM + CRLF handled; GO/GO_Moon/functions/references/structure
  metadata preserved verbatim; evidence claims = 0.
- Reference anomalies flagged at FIELD level, rows retained verbatim:
  2 `not_article_identifier` (rows 239: OMIM-style text; 422: `4ENL`) and
  1 `missing` (row 349). Never converted to PMID/DOI.
- Conservation: 694 raw rows = 694 interim source records; 0 excluded.

### Unresolved decisions
- Whether GO/GO_Moon blocks should be additionally decomposed into structured GO-annotation interim rows under the GO contract in Phase D (source data either way).
- Whether `Reference` values should be normalized to a PMID namespace at all (requires identity rules; record-level only).
- Version/URL/license remain `unknown`/`to_be_verified`.
