# MoonDB Source Profile

## Overview
- **Source ID**: `SRC_MOONDB`
- **Formal name**: MoonDB
- **Source status**: `imported`
- **Canonical local artifact path**: `data/raw/moondb/all_emf_and_curated.tsv`

## Artifact Facts (Canonical Raw Input)
- **Filename**: `all_emf_and_curated.tsv`
- **File size**: 8331 bytes
- **SHA-256 checksum**: `c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55`
- **Encoding**: ASCII text
- **Line endings**: LF (Unix-style, `\n`)
- **Last line**: No trailing newline
- **Format**: Tab-separated values (TSV)
- **Delimiter**: Tab (`\t`)
- **Header row**: Line 1
- **Total lines**: 352 (1 header + 351 data rows)
- **Data rows**: 351 (all unique accessions)

## Columns
| Position | Field Name | Description | Data Type | Nullable | Unique |
|---|---|---|---|---|---|
| 1 | `#UniProtKB_ac` | UniProtKB accession with `#` prefix in header only | string | No | No |
| 2 | `UniProtKB_ac` | UniProtKB accession (primary identifier) | string | No | Yes |
| 3 | `type` | Classification type | string | No | No |

## Identifier Candidates
- **Primary identifier**: `UniProtKB_ac` (column 2)
- **Uniqueness**: All 351 values in `UniProtKB_ac` are unique
- **Format**: Standard UniProt accession codes (e.g., `Q86VP1`, `P06744`, `O00499`)
- **Note**: Column 1 has the same values as column 2 but with `#` prefix in the header only; data values are identical

## Value Analysis
### Column: `type`
- **Cardinality**: 2 distinct values
- **Observed raw counts** (Unit: TSV data rows / protein accessions, Artifact: `data/raw/moondb/all_emf_and_curated.tsv`, Version: raw snapshot 2026-09-18):
  - `Predicted`: 289 occurrences (82.3%)
  - `Curated`: 62 occurrences (17.7%)
  - Total: 351 data rows

## Missingness
- **No missing values** detected in any column
- All fields are populated for all 351 data rows

## Duplicate Patterns
- **Row-level duplicates**: None detected (all UniProtKB_ac values are unique)
- **Column value duplicates**:
  - Column 1 and Column 2 contain identical values (except for header prefix)

## Parsing Anomalies
- **Header anomaly**: First column header has `#` prefix (`#UniProtKB_ac`) which does not appear in data rows
- **No trailing newline**: File ends without a newline character on the last line
- **No quote characters**: File does not use quoting for any values
- **No escaped characters**: No special characters requiring escaping detected

## Auxiliary Raw Files in Repository (Committed Development; Not Catalog Inputs)
The directory `data/raw/moondb/` contains two additional files committed during development:
- `all_EMF_annotation.tsv`: 102,456 bytes, 774 lines (contains auxiliary GO annotations).
- `all_manual_curated.tsv`: 14,616 bytes, 62 lines (contains auxiliary manual curation metadata).
- **Status**: These auxiliary files are **not** part of the canonical source manifest (`data/manifests/source_manifest.csv`), are **not** ingested into packaged catalog candidate v0.3.0, and are **not** included in the active three-source functional normalization pilot cohort.

## Catalog Integration and Lifecycle Distinctions

### 1. Packaged Candidate v0.3.0 (`releases/mfp-catalog-candidate-v0.3.0/`)
- **Governing contract**: `MFPB_0_19_MFP_CATALOG_MVP_V2`.
- **Unit of record**: Source observation record and assertion claim.
- **Interim claim artifact**: `data/interim/source_claims_moondb.csv` (351 claim rows, hash-bound to `c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55`).
- **Packaged outputs**:
  - `mfp_source_records.csv`: Exactly 351 rows with `source_id = SRC_MOONDB`.
  - `mfp_assertions.csv`: Exactly 351 assertion claims.
- **Operational status mapping** (per `configs/source_claim_policy_v0.1.yaml`):
  - `Curated` → `operational_status = confirmed` (62 claims).
  - `Predicted` → `operational_status = predicted` (289 claims).
- **Entity merging**: All 351 records possess valid UniProt accessions; MoonDB contributes to the 463 merged UniProt entities claimed by $\ge 2$ sources in candidate v0.3.0.

### 2. Committed Implementation
- **Claim adapter**: `src/mfp_bibliography/moondb_claims.py` and CLI `scripts/build_source_claims_moondb.py` generate the validated interim claims artifact.
- **Catalog build integration**: `scripts/build_mfp_catalog_mvp.py` ingests the interim claims, verifies raw input checksums, and produces the MVP tables.

### 3. Uncommitted / Experimental Development
- An earlier experimental script (`scripts/build_protein_facets.py`) attempted to parse auxiliary MoonDB annotation files into an ad-hoc 2-facet model. This experimental approach suffered from unvalidated heuristic parsing and is superseded by the relational claim model defined in proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md).
- MoonDB is **excluded** from the active three-source functional normalization pilot cohort (`data/interim/pilot/`).

### 4. Proposed Capabilities
- Any future extraction of functional assertions or GO terms from MoonDB auxiliary files remains deferred to post-pilot phases under [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md).

## Activity Domain Accounting

| Activity Domain | Status in Candidate v0.3.0 | Status in Development / Pilot | Reference / Governing Boundary |
|---|---|---|---|
| **Catalog Ingestion** | **Integrated**: 351 source records and 351 assertion claims | Fully reproducible offline | Contract `MFPB_0_19_MFP_CATALOG_MVP_V2` |
| **Functional Extraction** | **None**: Raw artifact contains only classification type | Experimental facet parsing superseded by proposed ADR-008 | [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **GO Annotation Handling** | **None**: Canonical raw TSV contains no GO terms | Auxiliary TSV parsing not integrated | [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Local Bibliographic Review** | **None**: No citations in canonical raw TSV | Formally out of scope for v1 | [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) |

## Provenance Notes
- **Source version**: `unknown`
- **Retrieval date**: `unknown`
- **Original artifact location**: `unknown`
- **License / terms**: `to_be_verified`
- **Primary publication**: `to_be_verified`

## Verification Checklist
- [x] File exists at declared path (`data/raw/moondb/all_emf_and_curated.tsv`)
- [x] SHA-256 checksum verified (`c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55`)
- [x] File size matches manifest (8,331 bytes)
- [x] Row count verified (351 data rows)
- [x] Column structure documented
- [x] Encoding confirmed (ASCII)
- [x] No network access required for profiling or ingestion
- [x] Raw artifact remains byte-for-byte unchanged per [ADR-002](../decisions/ADR-002-raw-data-immutability.md)
