# MoonDB Source Profile

## Overview
- **Source ID**: `SRC_MOONDB`
- **Formal name**: MoonDB
- **Source status**: `imported`
- **Local artifact path**: `data/raw/moondb/all_emf_and_curated.tsv`

## Artifact Facts
- **Filename**: `all_emf_and_curated.tsv`
- **File size**: 8331 bytes
- **SHA-256 checksum**: `c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55`
- **Encoding**: ASCII text
- **Line endings**: LF (Unix-style, `\n`)
- **Last line**: No trailing newline

## Structure
- **Format**: Tab-separated values (TSV)
- **Delimiter**: Tab (`\t`)
- **Header row**: Line 1
- **Total lines**: 352 (1 header + 351 data rows)
- **Data rows**: 351

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
- **Values**:
  - `Predicted`: 289 occurrences (82.3%)
  - `Curated`: 62 occurrences (17.7%)

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

## Benchmark Role
- **Assignment**: `unassigned`
- **Rationale**: No evidence tier or scientific label assignments have been made per task constraints

## Provenance Notes
- **Source version**: `unknown`
- **Retrieval date**: `unknown`
- **Original artifact location**: `unknown`
- **License / terms**: `to_be_verified`
- **Primary publication**: `to_be_verified`

## Verification Checklist
- [x] File exists at declared path
- [x] SHA-256 checksum verified
- [x] File size matches manifest
- [x] Row count verified
- [x] Column structure documented
- [x] Encoding confirmed (ASCII)
- [x] No network access required for profiling
- [x] Raw artifact remains byte-for-byte unchanged

## Generated
- **Profile date**: 2026-09-18
- **Profiler version**: v1.0 (initial profiling)
