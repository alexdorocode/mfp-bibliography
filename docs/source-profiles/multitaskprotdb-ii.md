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
