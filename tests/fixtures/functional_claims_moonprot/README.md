# MoonProt Test Fixtures

This directory contains test fixtures for the MoonProt functional claims adapter (`functional_claims_moonprot.py`).

## 1. Real-Source Derived Extracts

Selected real MoonProt HTML records copied directly from `data/raw/moonprot/`:

1. **`real_mpid_1.html` (MoonProt ID 1, UniProt `P78007`)**:
   - Parent Artifact Path: `data/raw/moonprot/mpid_1.html`
   - Parent SHA-256: `1a1a93f573f5d04b5541aa806057b694d258623ec2bbe6147f91dfe3dd13944c` (registered in `data/raw/moonprot/artifact_index.csv`)
   - Structural characteristics: 2 functions ($K=2$); Function 1 has EC `1.1.1.27`, cellular location `cytosol`, PMID `27616280`; Function 2 has description, location `None`, PMID `27616280`; protein-level GO terms present (`GO:0003824`, `GO:0004459`, etc.).
2. **`real_mpid_2.html` (MoonProt ID 2, UniProt `P0AFW0`)**:
   - Parent Artifact Path: `data/raw/moonprot/mpid_2.html`
   - Parent SHA-256: `e74406e97535bc7eaf3d26b1f39fe11f329a8c88bda59bc5a132bdebda249db1`
   - Structural characteristics: Raw UniProt string carries annotation residue (`P0AFW0 (RFAH_ECOLI), Reviewed`), normalizes via first whitespace token to `P0AFW0`; Function 1 has no PMIDs and cellular location `bound to DNA`; Function 2 has PMID `22817892` and cellular location `cytoplasm`.
3. **`real_mpid_7.html` (MoonProt ID 7, UniProt `P10809`)**:
   - Parent Artifact Path: `data/raw/moonprot/mpid_7.html`
   - Parent SHA-256: `e2a9b35ac1048928b9684df6f16c325fc4e2e6fa62b0a1132113740a86dc04e9`
   - Structural characteristics: Human Hsp60; 2 functions; Function 1 location `mitochondrial matrix`, Function 2 location `cell surface` with PMID `11027668`; extensive list of 50+ protein-level GO terms preserved structurally in `source_go_annotations` with `claim_id = null`.
4. **`real_mpid_10.html` (MoonProt ID 10, UniProt `E6KMA1`)**:
   - Parent Artifact Path: `data/raw/moonprot/mpid_10.html`
   - Parent SHA-256: `484bdd3e58400524b23c262c9ae31509900bd26daf8fc5d23451e682f52494d3`
   - Structural characteristics: 6-phosphofructokinase; Function 1 has EC `2.7.1.11`, location `cytoplasm`, no PMIDs; Function 2 has location `cell surface`, PMID `18310038`.
5. **`real_mpid_288.html` (MoonProt ID 288, UniProt `P24228`)**:
   - Parent Artifact Path: `data/raw/moonprot/mpid_288.html`
   - Structural characteristics: **Real-source zero-function case ($K=0$)**; Penicillin-binding protein 4; contains no discrete `Function description` blocks, but has populated `GO terms`; generates 0 claims, coverage status `no_discrete_functional_statements`, and preserves structured GO annotations with `claim_id = null`.

## 2. Synthetic Edge Cases

A dedicated set of minimal synthetic HTML fixtures exercising dynamic blocks, identity boundaries, references, and error conditions:

- **`synthetic_mpid_901_three_functions.html`**:
  - $K=3$ dynamic function blocks (proves the adapter does not assume a fixed 2-function structure).
  - All 3 functions have distinct descriptions, EC numbers, cellular locations, and linked PMIDs (`11111111`, `22222222`, `33333333`).
- **`synthetic_mpid_902_single_function.html`**:
  - $K=1$ single function block; generates exactly 1 claim.
- **`synthetic_mpid_903_missing_uniprot.html`**:
  - Empty UniProt ID field; unresolvable identity -> `unresolved_identity`, `protein_id = null`, 0 claims, 0 annotations.
- **`synthetic_mpid_904_malformed_uniprot.html`**:
  - Malformed UniProt ID string (`INVALID_UNIPROT_ID`); unresolvable identity -> `unresolved_identity`, `protein_id = null`.
- **`synthetic_mpid_905_fallback_identity.html`**:
  - Record without UniProt accession backed by valid catalog fallback identity `MFP:F:SRC_MOONPROT:0000000000000905`.
  - Verifies that valid catalog fallback identities are respected without being converted to null or raising regex errors.
- **`synthetic_mpid_906_multi_pmids.html`**:
  - Function 1 contains multiple PMIDs (`66666661`, `66666662`, `66666663`); Function 2 contains a raw text citation lacking numeric PMIDs (preserved in `notes`).
- **`synthetic_mpid_907_empty_functions_with_go.html`**:
  - 0 functions with explicit GO terms; generates 0 claims, coverage status `no_discrete_functional_statements`, preserves GO annotations with `claim_id = null`.
- **`synthetic_mpid_908_known_absent.html`**:
  - Soft-404 / known absent template matching `MoonProtKnownAbsentError` (e.g. captured MPID 103 behavior).
