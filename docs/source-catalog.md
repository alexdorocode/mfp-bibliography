# Source Catalog

Status: all records below are **to_be_verified** templates.

## SRC_MOONPROT
- Source ID: `SRC_MOONPROT`
- Formal name: `MoonProt` (to_be_verified)
- Source status: `to_be_verified`
- Dataset availability in this repository: `not_present`
- Intended acquisition mode: `planned_acquisition`
- Expected unit of record: `to_be_verified`
- Expected identifiers: `UniProt ID`, `to_be_verified`
- Expected evidence character: `to_be_verified`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `http://www.moonlightingproteins.org/protein_detail/?mpid={id}` (planned)
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: confirm robots/terms, implement controlled scraper, verify field labels.

## SRC_MOONDB
- Source ID: `SRC_MOONDB`
- Formal name: `MoonDB`
- Source status: `imported`
- Dataset availability in this repository: `present`
- Intended acquisition mode: `local_import`
- Unit of record: `protein`
- Identifiers: `UniProtKB_ac` (UniProt accession)
- Evidence character: `Predicted`, `Curated`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `unknown`
- Local artifact path: `data/raw/moondb/all_emf_and_curated.tsv`
- Artifact checksum (SHA-256): `c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55`
- File size: `8331` bytes
- Row count: `351` data rows
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: Artifact contains UniProt accessions with type classifications (Predicted: 289, Curated: 62). First column has `#` prefix in header only. No missing values detected. All UniProtKB_ac values are unique.
- Benchmark role: `unassigned`

## SRC_MULTIFACETEDPROTDB
- Source ID: `SRC_MULTIFACETEDPROTDB`
- Formal name: `MultifacetedProtDB`
- Source status: `imported`
- Dataset availability in this repository: `present`
- Intended acquisition mode: `local_import`
- Unit of record: `protein`
- Identifiers: `UniProtKB_ac` (UniProt accession)
- Evidence character: `to_be_verified`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `unknown`
- Local artifact path: `data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt`
- Artifact checksum (SHA-256): `23a68fe6e5d6e8fa25af67786cdd64836e3b28d83316174e1b9f70e638ffabb4`
- File size: `7724` bytes
- Row count: `1` line containing `1103` comma-separated values
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: Single-line CSV format. All 1103 entries are valid UniProt accessions. No header row, no duplicates, no empty values. File has no trailing newline.
- Benchmark role: `unassigned`

## SRC_PLANTMP
- Source ID: `SRC_PLANTMP`
- Formal name: `PlantMP` (to_be_verified)
- Source status: `to_be_verified`
- Dataset availability in this repository: `to_be_imported`
- Intended acquisition mode: `local_import`
- Expected unit of record: `to_be_verified`
- Expected identifiers: `to_be_verified`
- Expected evidence character: `to_be_verified`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `to_be_verified`
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: import existing local artifact into `data/raw/plantmp/`.

## SRC_MULTITASKPROTDB_II
- Source ID: `SRC_MULTITASKPROTDB_II`
- Formal name: `MultitaskProtDB-II` (to_be_verified)
- Source status: `to_be_verified`
- Dataset availability in this repository: `to_be_imported`
- Intended acquisition mode: `local_import`
- Expected unit of record: `to_be_verified`
- Expected identifiers: `to_be_verified`
- Expected evidence character: `to_be_verified`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `to_be_verified`
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: import existing local artifact into `data/raw/multitaskprotdb-ii/`.
