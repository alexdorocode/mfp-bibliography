# PlantMP Test Fixtures

This directory contains test fixtures for the PlantMP functional claims adapter (`functional_claims_plantmp.py`).

## 1. Real-Source Extract (`plantmp_real_extract.csv`)

- **Parent Artifact Path**: `data/raw/plantmp/PlantMP_all.csv`
- **Source SHA-256 (Pinned)**: `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9` (registered in `data/manifests/source_manifest.csv`)
- **Extraction Method**: Selected 7-row slice extracted directly from `PlantMP_all.csv` via standard Python CSV parsing (`utf-8`) preserving exact verbatim values without modification.
- **Byte-Identity Note**: This extract contains a selected 7-row slice of the 112-row parent artifact. It is **NOT** byte-identical to the parent file.
- **Preserved Source Locators & Characteristics**:
  1. **Order 1 (`plantmp_order_1`, UniProt `P34788`)**:
     - Status: `confirmed`.
     - Roles/Aspects: `canonical_function_bp` and `canonical_function_mf` populated; `moonlighting_function_bp` populated; `moonlighting_function_mf` empty (`""`).
     - GO Identifiers: `go_canonical_bp` (`BP 0042254, 0006412, 0006413`), `go_canonical_mf` (`MF 0003729, 0019843`), `go_moonlighting_bp` (`BP 0008150, 0032501, 0007275, 0048513, 0009888, 0048507, 0048509`).
     - Reference: Standard numeric PMID (`7913892`).
  2. **Order 2 (`plantmp_order_2`, UniProt `P92980\xa0`)**:
     - Status: `confirmed`.
     - Normalization: Carries raw non-breaking space `\xa0` in `uniport_id` in raw artifact; normalizes to `P92980` and resolves to `MFP:U:f3d2cc26494101eb`.
     - Roles/Aspects: Canonical BP/MF and Moonlighting BP populated; Moonlighting MF empty.
     - Reference: `8917600`.
  3. **Order 5 (`plantmp_order_5`, UniProt `E1AQY1`)**:
     - Status: `confirmed`.
     - Roles/Aspects: All 4 functional text fields and all 4 GO fields fully populated (`canonical_function_bp`, `canonical_function_mf`, `moonlighting_function_bp`, `moonlighting_function_mf`).
     - Reference: `24721550`.
  4. **Order 62 (`plantmp_order_62`, UniProt `Q8VYA3`)**:
     - Status: `confirmed`.
     - Multi-Record Identity: First occurrence of shared accession `Q8VYA3` (paired with Order 68); tests deterministic tie-breaking by `source_record_id ASC`.
     - Reference: `20126659`.
  5. **Order 64 (`plantmp_order_64`, UniProt `Q8LPL8`)**:
     - Status: `likely` (exercises normalized policy handling -> `claim_assertion_type = "unresolved"`).
     - Missing Text with GO Data: `canonical_function_bp` is empty, but `go_canonical_bp` is populated (`BP 0006811, 0006813, 0071805`); `moonlighting_function_bp` is empty, but `go_moonlighting_bp` is populated (`BP 0006171`).
     - Reference: Anomalous descriptive reference string (`26638082 (Homolog of POT7)`).
  6. **Order 68 (`plantmp_order_68`, UniProt `Q8VYA3`)**:
     - Status: `likely`.
     - Multi-Record Identity: Second occurrence of shared accession `Q8VYA3`; tests total tie-breaking order across distinct statuses (`confirmed` vs `likely`).
     - Reference: `20126659 (Homolog of WAKL10)`.
  7. **Order 75 (`plantmp_order_75`, UniProt `Q8GX94`)**:
     - Status: `predicted` (exercises `claim_assertion_type = "predicted"`).
     - Missing Text with GO Data: `canonical_function_bp` is empty with GO populated; `moonlighting_function_bp` is empty with GO populated.
     - Reference: Textual anomalous reference string (`Predicted in 23835195`).

## 2. Synthetic Edge Cases (`plantmp_synthetic_edge_cases.csv`)

A dedicated synthetic CSV exercising boundary and error conditions:
- **Record 1 (`P11111`)**: Single statement (only `canonical_function_bp` present, all others empty).
- **Record 2 (`P22222`)**: Only moonlighting statement present (only `moonlighting_function_mf` present).
- **Record 3 (`P33333`)**: Text statements present without any GO annotations (tests "Text without GO").
- **Record 4 (`P44444`)**: No-statement record (all 4 text fields and all 4 GO fields empty -> `claims_extracted_count = 0`, `coverage_status = "no_discrete_functional_statements"`).
- **Record 5 (`P55555`)**: All function text descriptions empty, but explicit GO annotations present in `go_canonical_bp` and `go_moonlighting_mf`. Emits 0 claims in `functional_claims`, preserves structured annotations in `source_go_annotations` with `claim_id = null`, and notes unextracted annotations in `functional_coverage`.
- **Record 6 (`INVALID_ACC`)**: Unresolvable UniProt accession -> `coverage_status = "unresolved_identity"`, `protein_id = null`, 0 claims, 0 annotations (no fabricated sentinel entities). Validated under Draft 2020-12 conditional schema requiring `protein_id = null` when `coverage_status = "unresolved_identity"`.
- **Record 7 (`P77777`)**: Unmapped native status `type = "disputed"` -> `claim_assertion_type = "unresolved"`.
- **Record 8 (`P88888`)**: Multiple comma-separated PMIDs in `pubmed_id` (`11111111, 22222222`).
- **Record 9 (`P99999`)**: `type = "likely"` with annotated PMID (`21088220 (Homolog of PEPR1)`), verifying that `likely` maps to `unresolved` without silent promotion to `curated`.
