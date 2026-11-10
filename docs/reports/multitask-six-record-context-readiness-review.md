# Scientific Review: MultitaskProtDB-II Six-Record Pilot Package Context Readiness Review

- **Document ID**: `REV-MULTITASK-6REC-001`
- **Target Package**: [`data/interim/pilot/multitask_slice/`](file:///home/alexdoro/repositories/mfp-bibliography/data/interim/pilot/multitask_slice/)
- **Review Type**: Bounded Data-Preservation & Context-Readiness Review (TASK-03 Consolidation)
- **Reviewer Role**: Senior Scientific Data Reviewer & SDD Evaluator
- **Status**: Supported with Limitations

---

## 1. Executive Summary and Package Verdict

### Package Verdict: **Supported with Limitations**

The persistent six-record package at `data/interim/pilot/multitask_slice/` successfully achieves **Tier A source preservation** for its declared scope:
1. **Determinism and Reproducibility**: All data files (`claims.csv`, `source_go_annotations.csv`, `coverage.csv`) and `manifest.json` are 100% byte-identical across independent executions, while volatile execution timestamps are strictly quarantined in `verification_report.json`.
2. **Structural Annotation Decoupling**: The newly implemented `source_go_annotations` relational model captures source-explicit Gene Ontology terms, aspects, and evidence codes directly without corrupting text claim fields or violating schema nullability constraints.
3. **Traceability**: All 6 records resolve against the local baseline catalog (`data/processed/mfp_catalog_mvp/mfp_source_records.csv`) with zero fallback identities.

### Principal Limitations
1. **Re-Indexing of Source Record Identifiers in Slice**:
   - The package serializes rows as `multitaskprotdb_ii_row_1` through `multitaskprotdb_ii_row_6` based on the fixture file order, whereas rows 4, 5, and 6 correspond to rows 55, 239, and 672 in the raw parent database (`proteins.csv`). While mapped in `manifest.json`, consumers must not assume slice row locators match parent database row numbers.
2. **Dead Enum State in Annotation Schema (`raw_only`)**:
   - In `source_go_annotations.schema.json`, `go_id` is a mandatory, non-nullable field constrained by `^GO:[0-9]{7}$`. Consequently, malformed or text-only annotation fragments lacking a 7-digit GO ID cannot be emitted with `annotation_status = "raw_only"` without violating schema validation or fabricating fake GO IDs.
3. **Upstream Source Data Quality Defects**:
   - Row 55 (`B8GW64` / CTP synthase) carries an erroneous reference in the raw database (PMID 22014899, duplicated verbatim from row 3 / KidO). A prior handoff had suggested PMID 20817753, but bibliographic verification reveals that PMID 20817753 is an unrelated study on RNA oligonucleotides; that suggestion is withdrawn without guessing an unverified replacement.
   - Row 239 (`P0ABS8` / DNA polymerase III theta) carries an uncurated non-numeric OMIM disease string (`HIV-1 and murine leukemia virus infection (omim:600534)`).
   - Row 672 was misidentified as "Bleomycin hydrolase (Bit1)" in previous handoffs; the actual biological entity is peptidyl-tRNA hydrolase 2 / Bit1 (`PTRH2`, UniProt `Q9Y3E5`).
4. **Source Preservation $\ne$ Contextual Triplets**:
   - Co-presence of Cellular Component (CC) and Molecular Function (MF) in source records does not prove that activity $m$ is executed in compartment $c$. Triplet synthesis $\tau = (m, b, c)$ requires primary literature adjudication under Decision Gate G2.

---

## 2. Fixture-to-Source Traceability

CSV-aware inspection was performed comparing the 6 fixture records in [`tests/fixtures/functional_claims_multitask/multitask_real_extract.csv`](file:///home/alexdoro/repositories/mfp-bibliography/tests/fixtures/functional_claims_multitask/multitask_real_extract.csv) against the pinned parent dataset [`data/raw/multitaskprotdb-ii/proteins.csv`](file:///home/alexdoro/repositories/mfp-bibliography/data/raw/multitaskprotdb-ii/proteins.csv) (694 data rows, 695 CSV lines including header).

| Fixture Position | Parent CSV Line (1-based) | Parent Data Row (1-based) | Raw Declared Accession | Field-by-Field Preservation Status | Discrepancies |
|---|---|---|---|---|---|
| Record 1 | Line 2 | Row 1 | `A0A059U5R2` | **Exact Match** (all 15 columns identical) | None |
| Record 2 | Line 3 | Row 2 | `A0A0H2Q1X0` | **Exact Match** (all 15 columns identical) | None |
| Record 3 | Line 4 | Row 3 | `A0A0H3CDS3` | **Exact Match** (all 15 columns identical) | Carries raw scraping residue in `GO` |
| Record 4 | Line 56 | Row 55 | `B8GW64` | **Exact Match** (all 15 columns identical) | Carries wrong reference in raw source |
| Record 5 | Line 240 | Row 239 | `P0ABS8` | **Exact Match** (all 15 columns identical) | Carries anomalous reference string |
| Record 6 | Line 673 | Row 672 | `Q9Y3E5` | **Exact Match** (all 15 columns identical) | Previous handoff misidentified protein name |

### Traceability Findings
1. **Exact Field Preservation vs Byte Identity**:
   - `multitask_real_extract.csv` is a 6-row subset extracted with standard UTF-8 parsing (`utf-8-sig`). It is not byte-identical to `proteins.csv` (which contains 694 rows), but every individual field value in the 6 rows matches the raw parent record verbatim without truncation or whitespace normalization.
2. **Scraping Residue Preservation**:
   - In Record 3 (parent row 3), the raw source field `GO` contains web-scraping HTML artifacts: `GO" id="GO:0016021"C:integral component of membrane`. The fixture preserves this verbatim, and the adapter parser successfully recovers `GO:0016021` while retaining the full line in `raw_annotation_text`.

---

## 3. Entity Identity Consistency

Each record was cross-referenced across raw source, candidate fixture, local catalog source records (`mfp_source_records.csv`), and catalog protein entities (`mfp_proteins.csv`):

| Fixture Pos | Raw UniProt | Raw Protein Name | Catalog Canonical Accession | Catalog Entity ID (`protein_id`) | Catalog Entity Status | Identity Consistency Verdict |
|---|---|---|---|---|---|---|
| **1** | `A0A059U5R2` | 60S ribosomal protein L44 | `A0A059U5R2` | `MFP:U:ac159de80a38c3e3` | `resolved` | **Consistent** (TrEMBL unreviewed) |
| **2** | `A0A0H2Q1X0` | Glutamine synthetase | `A0A0H2Q1X0` | `MFP:U:d837d7e36e10762a` | `resolved` | **Consistent** (TrEMBL unreviewed) |
| **3** | `A0A0H3CDS3` | Bifunctional regulator KidO | `A0A0H3CDS3` | `MFP:U:96deffc7f6cd3504` | `resolved` | **Consistent** (TrEMBL unreviewed) |
| **4** | `B8GW64` | CTP synthase | `B8GW64` | `MFP:U:864e9922e9e53a01` | `resolved` | **Consistent** (TrEMBL unreviewed) |
| **5** | `P0ABS8` | DNA polymerase III subunit theta | `P0ABS8` | `MFP:U:77393f79103c4f1a` | `resolved` | **Consistent** (Swiss-Prot reviewed) |
| **6** | `Q9Y3E5` | Pth2/Bit1 peptidyl-tRNA hydrolase 2/Bcl-2 inhibitor of transcription 1 EC:3.1.1.29 | `Q9Y3E5` | `MFP:U:c382ca456ad5a4db` | `resolved` | **Consistent Entity** (Misidentified in prior handoffs) |

### Identity Audit Findings
- **Record 6 Naming Discrepancy**:
  - In earlier handoff documents and `tasks.md`, Record 6 was repeatedly labeled `Bleomycin hydrolase (Bit1)`.
  - Direct inspection of the raw source record and UniProtKB confirms that `Q9Y3E5` is human **Peptidyl-tRNA hydrolase 2 / Bit1** (`PTRH2`). Bleomycin hydrolase is human `BLMH` (`Q13867`). The previous handoff name was an unverified human drafting error. The catalog and raw records correctly identify the entity as `PTRH2`.
- **Organism & Taxon Coverage**:
  - The slice contains 2 eukaryotes (*A. glaucus*, *H. sapiens*) and 4 bacteria (*B. bifidum*, *C. crescentus* [2 strains/proteins], *E. coli*).
  - All 6 entities successfully hash to deterministic `MFP:U:<16hex>` identifiers matching `mfp_proteins.csv`.

---

## 4. Source-to-Package Traceability and Granularity

Counts and linkages were traced from the original raw source records through to the published pilot slice artifacts:

| Original Source Record ID | Slice Source Record ID | Claims Extracted | Canonical GO Anns | Moonlighting GO Anns | Total GO Anns | Linked Claim IDs | Raw Reference String |
|---|---|---|---|---|---|---|---|
| `multitaskprotdb_ii_row_1` | `multitaskprotdb_ii_row_1` | 2 | 3 | 5 | 8 | 8 / 8 linked | `24814782` |
| `multitaskprotdb_ii_row_2` | `multitaskprotdb_ii_row_2` | 2 | 2 | 5 | 7 | 7 / 7 linked | `20167618` |
| `multitaskprotdb_ii_row_3` | `multitaskprotdb_ii_row_3` | 2 | 4 | 4 | 8 | 8 / 8 linked | `22014899` |
| `multitaskprotdb_ii_row_55` | `multitaskprotdb_ii_row_4` | 2 | 5 | 0 | 5 | 5 / 5 linked | `22014899` *(erroneous)* |
| `multitaskprotdb_ii_row_239` | `multitaskprotdb_ii_row_5` | 2 | 5 | 0 | 5 | 5 / 5 linked | `HIV-1... (omim:600534)` |
| `multitaskprotdb_ii_row_672` | `multitaskprotdb_ii_row_6` | 2 | 8 | 4 | 12 | 12 / 12 linked | `14660562` |
| **Total** | — | **12** | **27** | **18** | **45** | **45 / 45 linked** | — |

### Traceability Observations
1. **Claim Linkage**: In all 6 real records, both canonical and moonlighting functional descriptions are present. Consequently, 100% of the 45 extracted GO annotations link to an active claim (`claim_id` matching `MFP:FC:MULTITASKPROTDB_II:...`). Unlinked annotations (`claim_id = null`) occur only in edge-case conditions where text statements are missing (verified via synthetic fixtures).
2. **Reference Granularity**: In MultitaskProtDB-II, references are recorded at the overall record level. In the published slice:
   - Claims store references in `record_reference_ids`.
   - `linked_reference_ids` is strictly `null`.
   - Annotations do not synthesize or promote literature references.
3. **Evidence String Preservation**: Evidence codes (`IEA:UniProtKB-KW`, `IDA:HPA`, `IDA:UniProtKB`, `IMP:UniProtKB`, `IDA:EcoCyc`, etc.) survive intact in `source_go_annotations.csv` under `evidence_raw`. Where the source provides no evidence code (e.g. `GO_Moon` in rows 1, 2, 3), `evidence_raw` is correctly preserved as `null`.

---

## 5. Unparsed Annotation Accounting & Contract Gap Analysis

### Current Parser Behavior on Unrecognizable Fragments
In `src/mfp_bibliography/functional_claims_multitask.py`:
```python
for line in go_text.splitlines():
    line = line.strip()
    if not line:
        continue
    m = _GO_ID_REGEX.search(line)
    if not m:
        continue
    go_id = m.group(0)
```
Any raw line that does not contain a regex-matched `GO:\d{7}` token is skipped during parsing.

### Contract Inconsistency in `source_go_annotations.schema.json`
- **Schema Definition**:
  - `go_id`: Mandatory required property with pattern `^GO:[0-9]{7}$`. Null is not permitted.
  - `annotation_status`: Enum includes `["parsed", "unassigned_aspect", "ambiguous", "raw_only"]`.
- **The Contract Conflict**:
  - The status `"raw_only"` was intended to preserve malformed fragments or raw notes that failed GO parsing.
  - However, because `go_id` is required and non-nullable, emitting a record with status `"raw_only"` for a fragment lacking a valid GO ID causes immediate schema validation failure.
  - Fabricating a placeholder GO ID (e.g. `GO:0000000`) is strictly prohibited by repository scientific invariants.
- **Architectural Resolution & Recommendation**:
  - For the current slice, zero source lines in the 6 real records lack a GO ID (all 45 lines parse a valid GO ID).
  - **Proposed Schema Adjustment**: In a subsequent contract iteration, `go_id` should be modified to `type: ["string", "null"]` with pattern validation applying only when non-null. This will allow true unparseable fragments to be emitted with `annotation_status = "raw_only"` without data fabrication.

---

## 6. Execution Evidence and Verification Status

### Newly Executed Verification Commands
The following read-only commands were executed and verified during this review:

1. **Focused Test Suite (117 tests)**:
   ```bash
   PYTHONPATH=src pytest -v tests/test_schema.py \
                            tests/test_functional_contracts.py \
                            tests/test_source_go_annotations_contract.py \
                            tests/test_functional_claims_multitask.py \
                            tests/test_build_multitask_slice.py \
                            tests/test_multitaskprotdb_ii_records.py
   ```
   *Outcome*: **117 passed in 0.53s**.
2. **Byte-Level Reproducibility Verification**:
   - `build_multitask_slice.py` was executed independently in two separate temporary directories (`/tmp/tmpijrzpuho` and `/tmp/tmptv5j2xwy`).
   - Comparison of generated artifacts confirmed identical SHA-256 digests:
     * `claims.csv`: `2340f819f9dd805a5c538ded0bed4fb750ebfed825b352f4f396ff048b30e392`
     * `source_go_annotations.csv`: `9305c61e067445b6653c6fb1e33df1db04b64e8399c924f43942867e32fd286a`
     * `coverage.csv`: `89f3fee0803c7f327a313b7dd076a99ffdec790fbc82e54dc74ec51850fcf2e5`
     * `manifest.json`: `01bb0aa9839c77ddda5f7961a2867190559f66915545083338e8eba194206d9c`

### Historical Test Evidence (Full Repository Suite)
- In session execution `task-521`, the full suite produced **489 passed and 1 failure**.
- The single failure (`tests/test_source_claim_policy.py::TestSourceClaimPolicy::test_raw_checksums_unchanged`) is due to the pre-existing absence of `data/raw/plantmp/PlantMP MySQL.xlsx` in the workspace.
- The failure was not rerun in this review. It is isolated to PlantMP and does not invalidate the MultitaskProtDB-II slice.

---

## 7. Six Concise Case Cards

### Case Card 1: Record 1 (`multitaskprotdb_ii_row_1`)
- **Entity Identity**:
  - Accession: `A0A059U5R2` | Protein: `60S ribosomal protein L44` | Organism: *Aspergillus glaucus*
  - Entity ID: `MFP:U:ac159de80a38c3e3` | Status: Resolved TrEMBL unreviewed.
- **Original Statements**:
  - Canonical: `Ribosomal protein`
  - Moonlighting: `It supports abiotic stress resistance`
- **Source GO Annotations**:
  - `GO`: `GO:0005840` (CC, ribosome, `IEA:UniProtKB-KW`), `GO:0003735` (MF, structural constituent of ribosome, `IEA:InterPro`), `GO:0006412` (BP, translation, `IEA:InterPro`).
  - `GO_Moon`: `GO:0008150` (BP, biological_process), `GO:0050896` (unassigned, response to stimulus), `GO:0009628` (unassigned, response to abiotic stimulus), `GO:0006950` (unassigned, response to stress), `GO:0006970` (unassigned, response to osmotic stress). All evidence `null`.
- **References**:
  - Raw Reference: `24814782` (PMID 24814782). Record-level granularity.
- **Aspect Distribution**:
  - Canonical: CC, MF, BP all present.
  - Moonlighting: BP present; MF and CC absent.
- **Explicit vs Unproven Context**:
  - Explicit: Ribosome association for translation; general abiotic stress resistance.
  - Unproven: No compartment or molecular mechanism is provided for the stress tolerance function. Whether L44 acts extraribosomally or alters translation patterns under stress is unstated.
- **Pre-Curation Requirements**:
  - Inspect PMID 24814782 to determine if stress tolerance involves an extraribosomal compartment or independent biochemical activity.

---

### Case Card 2: Record 2 (`multitaskprotdb_ii_row_2`)
- **Entity Identity**:
  - Accession: `A0A0H2Q1X0` | Protein: `Glutamine synthetase` | Organism: *Bifidobacterium bifidum*
  - Entity ID: `MFP:U:d837d7e36e10762a` | Status: Resolved TrEMBL unreviewed.
- **Original Statements**:
  - Canonical: `ATP + L-glutamate + NH3 = ADP + phosphate + L-glutamine.` (reaction equation)
  - Moonlighting: `Plasminogen binding`
- **Source GO Annotations**:
  - `GO`: `GO:0015930` (MF, glutamate synthase activity, `IEA:InterPro`), `GO:0006537` (BP, glutamate biosynthetic process, `IEA:InterPro`). CC absent.
  - `GO_Moon`: `GO:0003674` (MF, molecular_function), `GO:0005488` (MF, binding), `GO:0005515` (MF, protein binding), `GO:0005102` (MF, receptor binding), `GO:0046789` (MF, host cell surface receptor binding). All evidence `null`. CC and BP absent.
- **References**:
  - Raw Reference: `20167618` (PMID 20167618). Record-level granularity.
- **Aspect Distribution**:
  - Canonical: MF, BP present; CC absent.
  - Moonlighting: MF present; CC, BP absent.
- **Explicit vs Unproven Context**:
  - Explicit: Catalytic glutamine synthesis and plasminogen receptor binding.
  - Unproven: Cellular localization is absent in both `GO` and `GO_Moon`.
- **Pre-Curation Requirements**:
  - Inspect PMID 20167618 to confirm whether cell wall / surface association is experimentally demonstrated in *B. bifidum*.

---

### Case Card 3: Record 3 (`multitaskprotdb_ii_row_3`)
- **Entity Identity**:
  - Accession: `A0A0H3CDS3` | Protein: `Bifunctional regulator KidO` | Organism: *Caulobacter crescentus*
  - Entity ID: `MFP:U:96deffc7f6cd3504` | Status: Resolved TrEMBL unreviewed.
- **Original Statements**:
  - Canonical: `Activates DivJ`
  - Moonlighting: `Binds to FtsZ`
- **Source GO Annotations**:
  - `GO`: `GO:0016021` (CC, integral component of membrane), `GO:0005622` (CC, intracellular), `GO:0005524` (MF, ATP binding), `GO:0000155` (MF, phosphorelay sensor kinase activity).
  - `GO_Moon`: `GO:0008150` (BP, biological_process), `GO:0000003` (BP, reproduction), `GO:0032505` (BP, reproduction of a single-celled organism), `GO:0043093` (BP, FtsZ-dependent cytokinesis). All evidence `null`.
- **References**:
  - Raw Reference: `22014899` (PMID 22014899). Record-level granularity.
- **Aspect Distribution**:
  - Canonical: CC, MF present; BP absent.
  - Moonlighting: BP present; CC, MF absent.
- **Explicit vs Unproven Context**:
  - Explicit: DivJ kinase activation and FtsZ cytokinesis regulation.
  - Unproven: Membrane association is co-annotated with kinase activity, but whether KidO translocates or acts as a soluble division inhibitor is unproven in source.
- **Pre-Curation Requirements**:
  - Evaluate whether KidO represents true moonlighting or a single cell-cycle regulatory pathway.

---

### Case Card 4: Record 4 (`multitaskprotdb_ii_row_55`, slice `row_4`)
- **Entity Identity**:
  - Accession: `B8GW64` | Protein: `CTP synthase` | Organism: *Caulobacter crescentus*
  - Entity ID: `MFP:U:864e9922e9e53a01` | Status: Resolved TrEMBL unreviewed.
- **Original Statements**:
  - Canonical: `Synthesizes CTP`
  - Moonlighting: `Binds to CreS`
- **Source GO Annotations**:
  - `GO`: `GO:0005524` (MF, ATP binding), `GO:0003883` (MF, CTP synthase activity), `GO:0046872` (MF, metal ion binding), `GO:0044210` (BP, CTP biosynthetic process), `GO:0006541` (BP, glutamine metabolic process). All `IEA`. CC absent.
  - `GO_Moon`: **0 annotations** (`GO_Moon` completely empty in raw source).
- **References**:
  - Raw Reference: `22014899` (Erroneous raw citation; duplicates KidO PMID).
- **Aspect Distribution**:
  - Canonical: MF, BP present; CC absent.
  - Moonlighting: All aspects absent in GO.
- **Explicit vs Unproven Context**:
  - Raw reference (PMID 22014899) is an erroneous duplicate from row 3 (KidO). A prior handoff suggested PMID 20817753 as the replacement, but verification confirms PMID 20817753 is an unrelated morpholino/RNA article (Xiao et al., *RNA* 2010), not CTP synthase. That claim is withdrawn. The actual primary literature linking *C. crescentus* CTP synthase to CreS remains unverified in this package.
- **Pre-Curation Requirements**:
  - Search and verify the correct primary literature for *C. crescentus* CTP synthase / CreS association without guessing unverified PMIDs.

---

### Case Card 5: Record 5 (`multitaskprotdb_ii_row_239`, slice `row_5`)
- **Entity Identity**:
  - Accession: `P0ABS8` | Protein: `DNA polymerase III subunit theta` | Organism: *Escherichia coli*
  - Entity ID: `MFP:U:77393f79103c4f1a` | Status: Resolved Swiss-Prot reviewed.
- **Original Statements**:
  - Canonical: `DNA polymerase III is a complex, multichain enzyme responsible for most of the replicative synthesis in Escherichia coli.`
  - Moonlighting: `Exhibits structural and functional similarities to the transactivation domain of the human p53 tumor suppressor.`
- **Source GO Annotations**:
  - `GO`: `GO:0005829` (CC, cytosol, `IDA:EcoCyc`), `GO:0044776` (CC, DNA polymerase III core complex, `IDA:EcoCyc`), `GO:0003677` (MF, DNA binding, `IEA`), `GO:0003887` (MF, DNA polymerase activity, `IEA`), `GO:0006260` (BP, DNA replication, `IEA`).
  - `GO_Moon`: **0 annotations** (`GO_Moon` completely empty).
- **References**:
  - Raw Reference: `HIV-1 and murine leukemia virus infection (omim:600534)` (Erroneous non-numeric string).
- **Aspect Distribution**:
  - Canonical: CC, MF, BP present.
  - Moonlighting: All aspects absent.
- **Explicit vs Unproven Context**:
  - Moonlighting assertion is a sequence/structure homology observation, not an experimentally validated second biological function in *E. coli*. Reference is uncurated.
- **Pre-Curation Requirements**:
  - High risk of spurious database inclusion. Curation should focus on determining whether theta subunit should be excluded as a false positive.

---

### Case Card 6: Record 6 (`multitaskprotdb_ii_row_672`, slice `row_6`)
- **Entity Identity**:
  - Accession: `Q9Y3E5` | Protein: `Pth2/Bit1 peptidyl-tRNA hydrolase 2/Bcl-2 inhibitor of transcription 1 EC:3.1.1.29`
  - Canonical Name: `Peptidyl-tRNA hydrolase 2, mitochondrial` (Gene: `PTRH2`) | Organism: *Homo sapiens*
  - Entity ID: `MFP:U:c382ca456ad5a4db` | Status: Resolved Swiss-Prot reviewed.
- **Original Statements**:
  - Canonical: `Peptidyl-tRNA hydrolase 2`
  - Moonlighting: `Inhibitor of transcription`
- **Source GO Annotations**:
  - `GO`: `GO:0005829` (CC, cytosol, `IMP:UniProtKB`), `GO:0016020` (CC, membrane, `IDA:UniProtKB`), `GO:0005739` (CC, mitochondrion, `IDA:UniProtKB`), `GO:0004045` (MF, aminoacyl-tRNA hydrolase activity, `IEA`), `GO:0006915` (BP, apoptotic process, `IEA`), `GO:2000811` (BP, negative regulation of anoikis, `IMP`), `GO:0010629` (BP, negative regulation of gene expression, `IMP`), `GO:2000210` (BP, positive regulation of anoikis, `IMP`).
  - `GO_Moon`: `GO:0005654` (CC, nucleoplasm, `IDA:HPA`), `GO:0003677` (MF, DNA binding, `IEA:InterPro`), `GO:0006355` (BP, regulation of transcription, `IEA`), `GO:0006351` (BP, transcription, `IEA`).
- **References**:
  - Raw Reference: `14660562` (PMID 14660562: De Pereda et al., *J. Biol. Chem.* 2004, 279(9):8111–8115; reports crystal structure of human Pth2 at 2.0 Å resolution, PDB `1Q7S`, and in vitro peptidyl-tRNA hydrolase catalytic efficiency).
  - Relevant Complementary Reference: PMID 15006356 (Jan et al., *Cell* 2004, 116(5):751–762; reports Bit1 mitochondrial localization, release into cytoplasm during apoptosis, cytoplasmic Bit1–AES complex formation, and caspase-independent apoptosis regulated by integrins/fibronectin). Note: Prior review text conflated PMID 14660562 with the Cell 2004 paper; they are distinct companion studies from the same research groups.
- **Aspect Distribution**:
  - Canonical: CC, MF, BP all present with experimental IDA/IMP evidence.
  - Moonlighting: CC, MF, BP all present with experimental `IDA:HPA` evidence.
- **Explicit vs Unproven Context**:
  - Explicit in Inspected Literature: Peptidyl-tRNA hydrolase catalytic activity (PMID 14660562); basal mitochondrial localization, apoptotic cytoplasmic release, cytoplasmic AES complex formation, and anoikis regulation (PMID 15006356 abstract).
  - Unproven in Inspected Material: Nuclear localization and direct transcriptional repression are asserted in source co-annotations (`GO:0005654`, `GO:0006355`), but are not established in inspected abstracts. Full primary text is inaccessible behind publisher access controls (Elsevier 403 / paywall).
- **Pre-Curation Requirements**:
  - Distinguish strictly between what is established by inspected primary abstracts (cytoplasmic Bit1–AES apoptotic complex) versus what remains an uninspected downstream hypothesis (nuclear translocation and transcriptional corepression).

---

## 8. Case Recommendations for Contextual Curation

### Recommended First Case: Record 6 (`Q9Y3E5` / `PTRH2` / Bit1)
- **Selection Rationale**:
  1. **Exemplary Evidence Profile**: Carries experimental evidence in both canonical (`IDA:UniProtKB`, `IMP:UniProtKB`) and moonlighting (`IDA:HPA`) annotations.
  2. **Explicit Dual Compartments**: It is the only record in the slice (and one of only 8 in the entire 694-row database) with an explicit cellular compartment in `GO_Moon` (`GO:0005654` nucleoplasm) distinct from canonical CC (`GO:0005739` mitochondrion).
  3. **Multi-Source Benchmark Consensus**: Independently cataloged in MoonProt (`moonprot_258`), MoonDB (`moondb_row_84`), and MultifacetedProtDB (`multifacetedprotdb_row_126`).
  4. **Landmark Primary Literature**: Supported by peer-reviewed studies: De Pereda et al., *JBC* 2004 (PMID 14660562, hydrolase crystal structure & enzymatic assay) and Jan et al., *Cell* 2004 (PMID 15006356, Bit1 apoptosis, integrin/anoikis regulation, and Groucho/TLE corepression).

### Recommended Backup Case: Record 1 (`A0A059U5R2` / 60S ribosomal protein L44)
- **Selection Rationale**:
  1. Clean, verified primary publication (PMID 24814782).
  2. Demonstrates the common curation scenario where moonlighting activity is demonstrated (abiotic stress tolerance), but cellular component is absent from source annotations.
  3. Tests whether literature analysis can resolve whether stress tolerance is extraribosomal or mediated by specialized ribosomes.

---

## 9. Next Separately Authorized Curation Task Proposal

### Proposed Task: `CUR-01: Contextual Evidence Adjudication for Human PTRH2 / Bit1 (Q9Y3E5)`

#### 1. Identity & Scope
- **Target Accession**: UniProtKB `Q9Y3E5` (Human `PTRH2`, Bit1).
- **Primary Source Publication**: PMID 14660562 (De Pereda et al., *J. Biol. Chem.* 2004, 279(9):8111–8115; crystal structure and peptidyl-tRNA hydrolase activity).
- **Complementary Primary Publication**: PMID 15006356 (Jan et al., *Cell* 2004, 116(5):751–762; Bit1 mitochondrial release, AES binding, and transcriptional corepression in anoikis).

#### 2. Specific Questions the Evidence Must Answer
1. **Activity 1 (Canonical)**:
   - What is the molecular activity? (Peptidyl-tRNA hydrolase activity; cleavage of ester bond between tRNA and peptide).
   - In which compartment does Activity 1 occur under basal conditions? (Mitochondrial matrix/membrane).
   - What biological process does Activity 1 support? (Mitochondrial protein synthesis / translation quality control).
2. **Activity 2 (Moonlighting)**:
   - What is the molecular activity? (Transcriptional corepressor; interaction with AES/TLE1).
   - In which compartment does Activity 2 occur? (Nucleus / nucleoplasm, following cytoplasmic release).
   - What is the physiological context/trigger? (Loss of integrin-mediated cell attachment / anoikis).
3. **Physical Entity Identity**:
   - Are both activities performed by the identical gene product without alternative splicing or gene duplication?

#### 3. Human Decisions Required
- **DEC-CUR-01**: **Status: Pending**. Neither autonomous transcriptional repression nor obligate corepressor recruitment can be adjudicated from inspected abstract evidence alone (which only establishes a cytoplasmic Bit1–AES apoptotic complex). Decision remains blocked pending access to primary full-text experimental data.
- **DEC-CUR-02**: Decide how conditional physiological states (basal mitochondrial attachment vs anoikis-induced cytoplasmic release) will be captured when context schemas are formalized.
- **DEC-CUR-03**: Determine catalog policy regarding external literature crosswalks when raw sources cite only one paper (PMID 14660562) while a second paper (PMID 15006356) provides the moonlighting evidence.

#### 4. Possible Adjudication Outcomes
- **Supported Context**: Evidence confirms distinct functions operating in distinct compartments under defined physiological states.
- **Incomplete**: Literature confirms functional duality but compartment of action remains ambiguous.
- **Contradictory**: Evidence disproves one of the source claims or reveals that the activities belong to distinct protein isoforms.
- **Unresolved**: Primary assay details insufficient to distinguish true moonlighting from secondary downstream phenotype.

---

### Verification Summary

```markdown
### Review Verification Record

- **Review Document**: docs/reports/multitask-six-record-context-readiness-review.md
- **Target Slice**: data/interim/pilot/multitask_slice/
- **Verdict**: Supported with Limitations
- **Verification Commands Executed**:
  - PYTHONPATH=src pytest -v tests/test_schema.py tests/test_functional_contracts.py tests/test_source_go_annotations_contract.py tests/test_functional_claims_multitask.py tests/test_build_multitask_slice.py tests/test_multitaskprotdb_ii_records.py (117 passed in 0.53s)
  - scripts/build_multitask_slice.py double execution (byte-reproducibility verified across independent tmpdirs)
- **Traceability Issues Documented**:
  - Re-indexing of slice source_record_id (1..6 vs 1, 2, 3, 55, 239, 672)
  - Protein naming error in prior handoffs (Q9Y3E5 is PTRH2/Bit1, not Bleomycin hydrolase)
  - Erroneous raw citations in source rows 55 and 239
  - Dead enum state raw_only in source_go_annotations.schema.json
```
