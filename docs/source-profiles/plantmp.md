# PlantMP Source Profile

## Artifact Identity
- **Source ID**: `SRC_PLANTMP`
- **Formal name**: PlantMP
- **Source status**: `imported`
- **Local artifact path**: `data/raw/plantmp/PlantMP_all.csv`

## Observed Structure
- **Filename**: `PlantMP_all.csv`
- **File size**: 53366 bytes
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
- **Primary identifier field**: `uniport_id` (column 3)
- **Identifier type**: UniProt accession
- **Total identifiers**: 112 entries
- **Unique identifiers**: 110 (2 entries are duplicated or shared)
- **Format validation**: Entries appear to be standard UniProt accession codes (e.g., `P34788`, `Q9MB58`, `E1AQY1`)
- **Identifier candidate**: `uniport_id` (column is non-nullable, reasonable cardinality)
- **Note**: `order` column is also unique and identified as an identifier candidate, but represents row sequence numbers rather than biological identifiers

## Raw Category Distribution
- **Column**: `type` (column 14)
- **Source-native categories** (preserved exactly as observed in raw artifact):
  - `confirmed`: 62 entries (55.4%)
  - `likely`: 12 entries (10.7%)
  - `predicted`: 38 entries (33.9%)
- **Category definitions** (as stated in source documentation):
  - `confirmed`: Bibliographically confirmed moonlighting proteins
  - `likely`: Likely/candidate moonlighting proteins
  - `predicted`: Predicted moonlighting proteins (not yet confirmed)
- **Important**: These categories are source-native labels and have NOT been mapped to repository scientific labels (`scientific_label`), evidence tiers (`evidence_tier`), or benchmark roles (`benchmark_role`). They are preserved for future exploration and normalization.

## Integrity Record
- **Checksum verified**: `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`
- **File size verified**: 53366 bytes
- **Row count verified**: 112 data rows
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
- What is the exact version of PlantMP that this dataset represents?
- What is the original source URL or DOI for this dataset?
- What license or terms of use apply to this data?
- What is the primary publication describing this dataset?
- What is the exact definition and selection criteria for each category (`confirmed`, `likely`, `predicted`)?
- Are there additional metadata files or documentation that accompany this dataset?
- What is the relationship between the `canonical_function` and `moonlighting_function` columns?
- Are the GO term columns (`go_canonical_bp`, `go_canonical_mf`, `go_moonlighting_bp`, `go_moonlighting_mf`) standardized or source-specific?
- Why are there 112 data rows when the sum of categories (62 + 12 + 38) equals 112, matching exactly?

## Verification Checklist
- [x] File exists at declared path
- [x] SHA-256 checksum verified
- [x] File size matches manifest
- [x] Row count verified
- [x] Column structure documented
- [x] Encoding confirmed (UTF-8)
- [x] Delimiter confirmed (comma)
- [x] Category distribution documented
- [x] No network access required for profiling
- [x] Raw artifact remains byte-for-byte unchanged

## Generated
- **Profile date**: 2026-09-18
- **Profiler version**: v1.1 (with UTF-8 and quoted CSV field support)
