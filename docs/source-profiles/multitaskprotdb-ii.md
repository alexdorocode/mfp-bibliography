# MultitaskProtDB-II Source Profile

## Artifact Identity
- **Source ID**: `SRC_MULTITASKPROTDB_II`
- **Formal name**: MultitaskProtDB-II
- **Source status**: `imported`
- **Local artifact path**: `data/raw/multitaskprotdb-ii/proteins.csv`

## Observed Structure (Canonical Raw Input)
- **Filename**: `proteins.csv`
- **File size**: 1324061 bytes (1,324,061 bytes)
- **SHA-256 checksum**: `84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482`
- **Encoding**: UTF-8 with BOM (UTF-8-SIG)
- **Line endings**: CRLF (Windows-style, `\r\n`)
- **Trailing newline**: No
- **Format**: Comma-separated values (CSV)
- **Delimiter**: Comma (`,`)
- **Header row**: Line 1 (present)
- **Total physical lines**: 14,291 (1 header + 14,290 lines; high line count caused by quoted multi-line fields)
- **Data rows**: 694

## Columns
| Position | Field Name | Data Type | Nullable | Unique | Cardinality | Description |
|---|---|---|---|---|---|---|
| 1 | `UniProt` | string | No | No | 685 | UniProt accession identifier |
| 2 | `Protein_Name` | string | No | No | 517 | Protein name |
| 3 | `Long_Description` | integer | Yes | No | 1 | Long description (100% empty/null) |
| 4 | `Canonical_Function` | string | No | No | 457 | Canonical function description |
| 5 | `GO` | string | No | No | 555 | Gene Ontology terms with evidence codes |
| 6 | `Moonlighting_function` | string | No | No | 557 | Moonlighting function description |
| 7 | `GO_Moon` | string | Yes | No | 495 | Gene Ontology terms for moonlighting functions |
| 8 | `Organism` | string | Yes | No | 184 | Organism name |
| 9 | `Human_Disease` | string | Yes | No | 129 | Human disease associations |
| 10 | `Drugs` | string | Yes | No | 79 | Drug associations |
| 11 | `Induction` | integer | Yes | No | 1 | Induction information (100% empty/null) |
| 12 | `PDBs` | string | Yes | No | 601 | Protein Data Bank identifiers |
| 13 | `PDB_UniProt` | string | Yes | No | 301 | PDB to UniProt mapping |
| 14 | `Models` | string | No | No | 2 | Modeling method/structure prediction |
| 15 | `Reference` | string | Yes | No | 469 | Reference information (PubMed identifiers & anomalies) |

## Identifier Analysis
- **Primary identifier field**: `UniProt` (column 1)
- **Identifier type**: UniProt accession
- **Total identifiers**: 694 entries
- **Unique identifiers**: 685 distinct UniProt accessions
- **Repeated observations**: 9 accessions appear in 2 data rows each with differing annotations (differing in `Protein_Name`, `GO`, `Moonlighting_function`/`Canonical_Function`, `GO_Moon`, `Organism` and `Reference`, e.g. rows 15/16 for A1KFR2).
- **Format validation**: All 685 accessions match the 6- or 10-character canonical UniProt accession pattern.

## Raw Category Distribution
- **No explicit source-native category column** exists in the raw artifact.
- **Models column distribution** (structural/modeling categories):
  - `Phyre`: 690 entries (99.4%)
  - `ITasser`: 4 entries (0.6%)
- **Important**: These values are preserved as observed structural modeling method identifiers. They are excluded from policy mapping and are NOT interpreted as evidence of multifunctionality.

## Integrity Record
- **Checksum verified**: `84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482`
- **File size verified**: 1324061 bytes (1,324,061 bytes)
- **Row count verified**: 694 data rows
- **Raw artifact unchanged**: Confirmed byte-for-byte identical before and after profiling per [ADR-002](../decisions/ADR-002-raw-data-immutability.md).

## Field Inventory and Missingness (Measured on 694 Rows)
| Field | Missing | Notes |
|---|---|---|
| `UniProt` | 0 | 685 unique across 694 rows; canonical case; all match accession pattern |
| `Protein_Name` | 0 | Raw protein name |
| `Long_Description` | 694 | 100% empty — never invent content |
| `Canonical_Function` | 0 | Free-text function statement; source data, not GO evidence |
| `GO` | 0 | GO annotations with evidence codes (e.g., `GO:0005840; C:ribosome; IEA:UniProtKB-KW.`); codes seen include IEA, IDA, TAS, IMP, IBA, IPI, NAS, IEP |
| `Moonlighting_function` | 0 | Free-text moonlighting function statement |
| `GO_Moon` | 11 | GO annotations for moonlighting functions |
| `Organism` | 1 | Row for Q6L047 lacks organism — preserved as empty/null |
| `Human_Disease` | 556 | Disease text; metadata, not evidence |
| `Drugs` | 611 | Drug text; metadata |
| `Induction` | 694 | 100% empty |
| `PDBs` | 77 | PDB identifiers; structural metadata |
| `PDB_UniProt` | 389 | Structural metadata |
| `Models` | 0 | Phyre (690) / ITasser (4); structural metadata |
| `Reference` | 1 | Bare PubMed numbers (e.g., `24814782`); 2 anomalies: row 239 `HIV-1 and murine leukemia virus infection (omim:600534)` and row 422 `4ENL`; row 349 missing reference |

## Status Semantics
- There is NO source-native status/label field. Database membership is a membership fact only. Per `configs/source_claim_policy_v0.1.yaml`, `SRC_MULTITASKPROTDB_II` is placed in `unmapped_sources`, assigning neutral `operational_status = unresolved`.
- Evidence claims in candidate v0.3.0 remain 0 (no status assertions emitted).

## Historical Ingestion Design Contract (Implemented and Integrated as Fifth Source)
- **Row grain policy**: One input row → one interim source record, keyed by `source_record_id = multitaskprotdb_ii_row_{1-based file row}`. The 9 same-accession rows remain distinct source records sharing one protein entity.
- **Identity**: Exact normalized UniProt accession only (`normalize_uniprot_accession`).
- **Conservation equation**: 694 raw rows = 694 interim source records = 694 catalog source records; 0 dropped; 685 protein-accession entities (9 shared).
- **Hash binding**: Verifies raw file SHA-256 against `source_manifest.csv` before output.
- **Adapter output**: `data/interim/source_records_multitaskprotdb_ii.csv`.

## Catalog Integration and Lifecycle Distinctions

### 1. Packaged Candidate v0.3.0 (`releases/mfp-catalog-candidate-v0.3.0/`)
- **Governing contract**: `MFPB_0_19_MFP_CATALOG_MVP_V2`.
- **Unit of record**: Interim source records and catalog source records.
- **Interim artifact**: `data/interim/source_records_multitaskprotdb_ii.csv` (694 interim source records).
- **Packaged outputs**:
  - `mfp_source_records.csv`: Exactly 694 source records with `source_id = SRC_MULTITASKPROTDB_II`.
  - `mfp_assertions.csv`: 0 assertion claims emitted (`operational_status = unresolved`).
- **Verbatim preservation**: Free-text functions (`Canonical_Function`, `Moonlighting_function`), GO blocks (`GO`, `GO_Moon`), references, and structural metadata are preserved verbatim in `mfp_source_records.csv`.
- **Reference anomalies**: The 3 reference anomalies (2 non-article strings, 1 missing) are retained verbatim and flagged at field level; never coerced into PMIDs.

### 2. Committed Implementation
- **Source record adapter**: `src/mfp_bibliography/multitaskprotdb_ii_records.py` and CLI `scripts/build_source_records_multitaskprotdb_ii.py` (offline, local-only).
- **Catalog build integration**: `scripts/build_mfp_catalog_mvp.py` integrates the 694 records as the fifth source.
- **Functional pilot adapter**: `src/mfp_bibliography/functional_claims_multitask.py` extracts discrete functional statements and GO annotations for pilot records under [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md).

### 3. Uncommitted / Pilot Development
- **Multitask slice package**: `scripts/build_multitask_slice.py` builds and verifies a persistent 6-record pilot slice in `data/interim/pilot/multitask_slice/` (covering `functional_claims_slice.csv`, `functional_coverage_slice.csv`, `source_go_annotations_slice.csv`, and `manifest.json`).
- **Integrated pilot cohort**: MultitaskProtDB-II contributes 6 real records to the 20-record empirical cohort in `data/interim/pilot/functional_claims_pilot.csv` generated by `scripts/build_functional_claims_pilot.py`.

### 4. Proposed Capabilities
- Full-cohort functional extraction across all 694 records remains **deferred** under ADR-008 Level 3 until pilot results are evaluated and approved.

## Activity Domain Accounting

| Activity Domain | Status in Candidate v0.3.0 | Status in Development / Pilot | Reference / Governing Boundary |
|---|---|---|---|
| **Catalog Ingestion** | **Integrated**: 694 source records (685 distinct accessions) | Fully reproducible offline | Contract `MFPB_0_19_MFP_CATALOG_MVP_V2` |
| **Functional Extraction** | **Verbatim text only**: Preserved in source records; 0 claims | 6-record slice and pilot cohort extracted | [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **GO Annotation Handling** | **Verbatim text only**: Preserved with evidence codes | Structured rows in pilot annotations | Scheme `MFPB_SOURCE_GO_ANNOTATION_V1` |
| **Local Bibliographic Review** | **Verbatim citations only**: PMIDs + 2 anomalies preserved | Formally out of scope for v1 | [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) |

## Open Questions
- What is the exact version of MultitaskProtDB-II that this dataset represents?
- What is the original source URL or DOI for this dataset?
- What license or terms of use apply to this data?
- What is the primary publication describing this dataset?
- Whether GO/GO_Moon blocks should be decomposed into structured GO-annotation interim rows across all 694 records in post-v1 phases.
- Whether bare PubMed numbers in `Reference` should be formally normalized to a PMID namespace.
