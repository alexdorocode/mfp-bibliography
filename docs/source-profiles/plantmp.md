# PlantMP Source Profile

## Artifact Identity
- **Source ID**: `SRC_PLANTMP`
- **Formal name**: PlantMP
- **Source status**: `imported`
- **Canonical local artifact path**: `data/raw/plantmp/PlantMP_all.csv`

## Observed Structure (Canonical Raw Input)
- **Filename**: `PlantMP_all.csv`
- **File size**: 53366 bytes (53,366 bytes)
- **SHA-256 checksum**: `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`
- **Encoding**: UTF-8 text
- **Line endings**: LF (Unix-style, `\n`)
- **Trailing newline**: Yes
- **Format**: Comma-separated values (CSV)
- **Delimiter**: Comma (`,`)
- **Header row**: Line 1 (present)
- **Total lines**: 123 (1 header + 112 data rows)
- **Data rows**: 112

## Columns
| Position | Field Name | Data Type | Nullable | Unique | Cardinality | Description |
|---|---|---|---|---|---|---|
| 1 | `order` | integer | No | Yes | 112 | Sequential row identifier |
| 2 | `protein name, gene` | string | No | No | 107 | Protein name and gene identifier (quoted field containing commas) |
| 3 | `uniport_id` | string | No | No | 110 | UniProt accession identifier |
| 4 | `canonical_function_bp` | string | Yes | No | 79 | Canonical biological process function |
| 5 | `canonical_function_mf` | string | Yes | No | 74 | Canonical molecular function |
| 6 | `moonlighting_function_bp` | string | Yes | No | 35 | Moonlighting biological process function |
| 7 | `moonlighting_function_mf` | string | Yes | No | 17 | Moonlighting molecular function |
| 8 | `go_canonical_bp` | string | Yes | No | 83 | Gene Ontology canonical biological process terms |
| 9 | `go_canonical_mf` | string | Yes | No | 81 | Gene Ontology canonical molecular function terms |
| 10 | `go_moonlighting_bp` | string | Yes | No | 25 | Gene Ontology moonlighting biological process terms |
| 11 | `go_moonlighting_mf` | string | Yes | No | 16 | Gene Ontology moonlighting molecular function terms |
| 12 | `plant_species` | string | No | No | 13 | Plant species origin |
| 13 | `pubmed_id` | string | No | No | 56 | PubMed ID reference(s) |
| 14 | `type` | string | No | No | 3 | Source-native category classification |

## Identifier Analysis
- **Primary identifier field**: `uniport_id` (column 3; typo in source-native header preserved verbatim)
- **Identifier type**: UniProt accession
- **Total identifiers**: 112 entries
- **Unique identifiers**: 110 distinct UniProt accessions
- **Repeated observations**: Exactly 2 accessions appear in 2 rows each:
  - `P34788`: Order 2 (`confirmed`) and Order 62 (`confirmed`)
  - `Q9MB58`: Order 25 (`confirmed`) and Order 108 (`predicted`)
- **Format validation**: All 110 accessions match canonical UniProt accession patterns (e.g., `P34788`, `Q9MB58`, `E1AQY1`).
- **Row key candidate**: `order` provides a 1-based unique row index (`plantmp_order_{order}`).

## Raw Category Distribution
- **Column**: `type` (column 14)
- **Observed raw counts** (Unit: CSV data rows, Artifact: `data/raw/plantmp/PlantMP_all.csv`, Version: canonical raw snapshot):
  - `confirmed`: 62 entries (55.4%)
  - `likely`: 12 entries (10.7%)
  - `predicted`: 38 entries (33.9%)
  - Total: 112 data rows
- **Category definitions in source**:
  - `confirmed`: Bibliographically confirmed moonlighting proteins
  - `likely`: Likely/candidate moonlighting proteins
  - `predicted`: Predicted moonlighting proteins (not yet confirmed)

## Integrity Record & Repository Baseline
- **Checksum verified**: `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`
- **File size verified**: 53366 bytes (53,366 bytes)
- **Row count verified**: 112 data rows
- **Raw artifact unchanged**: Confirmed byte-for-byte identical before and after profiling per [ADR-002](../decisions/ADR-002-raw-data-immutability.md).

## Auxiliary Raw Files in Repository & Test Context
The directory `data/raw/plantmp/` contains additional historical raw artifacts:
- `PlantMP MySQL-all-147.csv`: 147 rows (historical unfiltered database export).
- `PlantMP MySQL-confirmed .csv`: 62 rows.
- `PlantMP-predicted.csv`: 38 rows.
- `PlantMP MySQL-likely.csv`: 12 rows.
- **Test context note**: The repository test suite records an unresolved external-artifact verification issue in `test_raw_checksums_unchanged` because the external historical spreadsheet `PlantMP MySQL.xlsx` is absent from the workspace. The pre-existing status of this failure remains unestablished, and its eventual resolution remains an open maintainer verification topic. This condition does not alter the fact that `PlantMP_all.csv` (112 records) is the canonical raw artifact registered in the manifest, validated by `scripts/validate_repository.py`, and packaged in catalog candidate v0.3.0.

## Catalog Integration and Lifecycle Distinctions

### 1. Packaged Candidate v0.3.0 (`releases/mfp-catalog-candidate-v0.3.0/`)
- **Governing contract**: `MFPB_0_19_MFP_CATALOG_MVP_V2`.
- **Unit of record**: Interim claims and catalog source records.
- **Interim claim artifact**: `data/interim/source_claims_plantmp.csv` (112 claim rows under `MFPB_0_8_SOURCE_CLAIMS_CONTRACT_V0`).
- **Packaged outputs**:
  - `mfp_source_records.csv`: Exactly 112 source records with `source_id = SRC_PLANTMP`.
  - `mfp_assertions.csv`: Exactly 112 assertion claims mapped via `configs/source_claim_policy_v0.1.yaml`:
    - `confirmed` → `operational_status = confirmed` (62 claims).
    - `likely` → `operational_status = excluded_likely` (12 claims).
    - `predicted` → `operational_status = predicted` (38 claims).
- **Entity merging**: PlantMP contributes to the 463 merged UniProt entities across candidate sources.

### 2. Committed Implementation
- **Claims adapter**: `src/mfp_bibliography/plantmp_claims.py` and CLI `scripts/build_source_claims_plantmp.py`.
- **Catalog build integration**: `scripts/build_mfp_catalog_mvp.py` ingests the interim claims directly.
- **Functional pilot adapter**: `src/mfp_bibliography/functional_claims_plantmp.py` extracts functional statements, coverage, and source GO annotations under [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md).

### 3. Uncommitted / Pilot Development
- **Integrated pilot cohort**: PlantMP contributes 7 real records (e.g. `plantmp_order_1`, `plantmp_order_2`, `plantmp_order_25`, `plantmp_order_62`, etc.) to the 20-record empirical cohort in `data/interim/pilot/functional_claims_pilot.csv` generated by `scripts/build_functional_claims_pilot.py`.

### 4. Proposed Capabilities
- Full-cohort functional extraction across all 112 records remains **deferred** under ADR-008 Level 3 until pilot evaluation is completed.

## Activity Domain Accounting

| Activity Domain | Status in Candidate v0.3.0 | Status in Development / Pilot | Reference / Governing Boundary |
|---|---|---|---|
| **Catalog Ingestion** | **Integrated**: 112 source records and 112 assertion claims | Fully reproducible offline | Contract `MFPB_0_19_MFP_CATALOG_MVP_V2` |
| **Functional Extraction** | **Verbatim text only**: Preserved in source records; 0 claims | 7-record pilot cohort extracted | [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **GO Annotation Handling** | **Verbatim text only**: Preserved in source records | Structured rows in pilot annotations | Scheme `MFPB_SOURCE_GO_ANNOTATION_V1` |
| **Local Bibliographic Review** | **Verbatim citations only**: PMIDs preserved in records | Formally out of scope for v1 | [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) |

## Open Questions
- What is the exact version of PlantMP that this dataset represents?
- What is the original source URL or DOI for this dataset?
- What license or terms of use apply to this data?
- What is the primary publication describing this dataset?
- What is the exact selection criteria distinguishing `likely` from `confirmed` in the primary source methodology?
