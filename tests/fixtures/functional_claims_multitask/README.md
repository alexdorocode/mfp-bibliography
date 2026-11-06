# MultitaskProtDB-II Test Fixtures

This directory contains test fixtures for the MultitaskProtDB-II functional claims adapter (`functional_claims_multitask.py`).

## 1. Real-Source Extract (`multitask_real_extract.csv`)

- **Original Artifact Path**: `data/raw/multitaskprotdb-ii/proteins.csv`
- **Source SHA-256 (Pinned)**: Registered in `data/raw/source_manifest.csv`
- **Method of Acquisition**: Extracted using standard Python CSV parsing (`utf-8-sig`) from specific row locators without modifying field values.
- **Byte-Identity Note**: This extract contains a selected 5-row slice of the 694-row parent artifact. It is **NOT** byte-identical to the parent file.
- **Preserved Source Locators & Characteristics**:
  1. **Row 1 (`multitaskprotdb_ii_row_1`, UniProt `A0A059U5R2`)**:
     - Canonical: MF, BP, CC terms all present in `GO` (`GO:0005840; C:ribosome`, `GO:0003735; F:structural constituent...`, `GO:0006412; P:translation`).
     - Moonlighting: BP terms only in `GO_Moon` (`GO:0008150 biological_process`, `GO:0050896 response to stimulus`). MF and CC absent.
     - Reference: `24814782` (numeric PMID).
  2. **Row 2 (`multitaskprotdb_ii_row_2`, UniProt `A0A0H2Q1X0`)**:
     - Canonical: MF and BP terms present (`GO:0015930; F:glutamate synthase`, `GO:0006537; P:glutamate biosynthetic`). CC absent.
     - Moonlighting: MF terms only (`GO:0003674; F:molecular_function`, `GO:0005488; F:binding`). BP and CC absent.
     - Reference: `20167618` (numeric PMID).
  3. **Row 3 (`multitaskprotdb_ii_row_3`, UniProt `A0A0H3CDS3`)**:
     - Canonical: Carries HTML scraping residue in raw text (`GO" id="GO:0016021"C:integral component...`).
     - Moonlighting: BP terms only.
     - Reference: `22014899`.
  4. **Row 55 (`multitaskprotdb_ii_row_55`, UniProt `B8GW64`)**:
     - Canonical: Carries MF/BP terms in `GO`.
     - Moonlighting: Valid moonlighting statement (`Binds to CreS`), but `GO_Moon` is completely empty (`""`).
     - Reference: `20817753`.
  5. **Row 239 (`multitaskprotdb_ii_row_239`, UniProt `P0ABS8`)**:
     - Canonical and moonlighting statements both present.
     - Reference: Anomalous non-numeric string (`HIV-1 and murine leukemia virus infection (omim:600534)`).

## 2. Synthetic Edge Cases (`multitask_synthetic_edge_cases.csv`)

A dedicated synthetic CSV exercising edge conditions that do not naturally occur in the clean real table:
- Record with missing `Canonical_Function` (only `Moonlighting_function` present).
- Record with missing `Moonlighting_function` (only `Canonical_Function` present).
- Record with both functions empty (0 claims, coverage status `no_discrete_functional_statements`).
- Record with invalid/missing UniProt accession (unresolved identity).
- Record with multiple comma-separated PMIDs (`11111111, 22222222`).
