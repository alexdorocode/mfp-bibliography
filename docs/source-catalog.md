# Source Catalog

Status: all records below are **to_be_verified** templates.

## SRC_MOONPROT
- Source ID: `SRC_MOONPROT`
- Formal name: `MoonProt`
- Source status: `smoke_tested`
- Dataset availability in this repository: `smoke_sample_only`
- Intended acquisition mode: `controlled_web_acquisition`
- Unit of record: `protein`
- Identifiers: `MoonProt ID`, `UniProt ID`
- Documented fields: `MoonProt ID`, `UniProt ID`, `Name(s)`
- Source version: `unknown`
- Retrieval date: see smoke test report
- Original artifact location: `http://www.moonlightingproteins.org/protein_detail/?mpid={id}`
- Known range: `mpid=1..706`
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: Smoke test completed for MPIDs 1-3. Bulk acquisition blocked pending maintainer contact and terms/license/citation verification.

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
- Formal name: `PlantMP`
- Source status: `imported`
- Dataset availability in this repository: `present`
- Intended acquisition mode: `local_import`
- Unit of record: `protein`
- Identifiers: `uniport_id` (UniProt accession)
- Evidence character: `confirmed`, `likely`, `predicted`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `unknown`
- Local artifact path: `data/raw/plantmp/PlantMP_all.csv`
- Artifact checksum (SHA-256): `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`
- File size: `53366` bytes
- Row count: `112` data rows
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: CSV format with UTF-8 encoding. Contains 15 columns including `type` with values: confirmed (62), likely (12), predicted (38). Column "protein name, gene" contains quoted commas. All rows have data for order, protein name/gene, and uniport_id. File has LF line endings with trailing newline.
- Benchmark role: `unassigned`

## SRC_MULTITASKPROTDB_II
- Source ID: `SRC_MULTITASKPROTDB_II`
- Formal name: `MultitaskProtDB-II`
- Source status: `imported`
- Dataset availability in this repository: `present`
- Intended acquisition mode: `local_import`
- Unit of record: `protein`
- Identifiers: `UniProt` (UniProt accession)
- Evidence character: `to_be_verified`
- Source version: `unknown`
- Retrieval date: `unknown`
- Original artifact location: `unknown`
- Local artifact path: `data/raw/multitaskprotdb-ii/proteins.csv`
- Artifact checksum (SHA-256): `84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482`
- File size: `1324061` bytes
- Row count: `694` data rows
- License / terms: `to_be_verified`
- Primary publication: `to_be_verified`
- Notes and verification tasks: CSV format with UTF-8-SIG encoding (BOM present). Contains 15 columns. Uses CRLF line endings without trailing newline. No source-native category column identified. Models column has Phyre (690) and ITasser (4) values.
- Benchmark role: `unassigned`
