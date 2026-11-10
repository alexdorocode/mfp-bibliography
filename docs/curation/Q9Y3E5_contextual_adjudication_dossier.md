# Contextual Evidence Dossier: Human PTRH2 / Bit1 (`Q9Y3E5`)

- **Document ID**: `DOSSIER-Q9Y3E5-001`
- **Target Accession**: UniProtKB [`Q9Y3E5`](file:///home/alexdoro/repositories/mfp-bibliography/data/processed/mfp_catalog_mvp/mfp_proteins.csv#L1) (`PTH2_HUMAN`)
- **Deterministic Entity ID**: `MFP:U:c382ca456ad5a4db`
- **Target Slice Record**: `multitaskprotdb_ii_row_6` ([`data/interim/pilot/multitask_slice/`](file:///home/alexdoro/repositories/mfp-bibliography/data/interim/pilot/multitask_slice/))
- **Original Source Record**: `multitaskprotdb_ii_row_672` ([`data/raw/multitaskprotdb-ii/proteins.csv`](file:///home/alexdoro/repositories/mfp-bibliography/data/raw/multitaskprotdb-ii/proteins.csv))
- **Status**: `Draft — bibliographic verification and contextual evidence review; not approved biological adjudication`
- **Reviewer / Curator Role**: Scientific Evidence Curator & SDD Evaluator
- **Revision Date**: 2026-11-09 (Post-audit correction cycle)

---

> [!IMPORTANT]
> **Adjudication Scope and Boundary Notice**:
> This document establishes a verified bibliographic and contextual evidence baseline for the candidate multifunctional protein PTRH2/Bit1.
> In accordance with repository governance ([ADR-008](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-008-functional-normalization-architecture.md) and [`AGENTS.md`](file:///home/alexdoro/repositories/mfp-bibliography/AGENTS.md)), this dossier:
> 1. **Does NOT approve biological labels** or grant final moonlighting certification.
> 2. **Does NOT generate or emit validated functional triplets** $\tau = (m, b, c)$ into production catalogs.
> 3. **Maintains strict separation** between raw source statements, structured Gene Ontology annotations, and primary literature findings.
> 4. **Labels access limitations explicitly** and refuses to assert experimental findings that cannot be directly inspected in lawfully accessible primary sources.

---

## 1. Verified Protein and Gene Identity

The physical entity was resolved and cross-checked against UniProtKB/Swiss-Prot and the local repository catalog:

| Attribute | Verified Canonical Value | Source-Native / Raw Representation | Status & Notes |
|---|---|---|---|
| **UniProtKB Accession** | `Q9Y3E5` | `Q9Y3E5` | Canonical primary accession |
| **UniProtKB Entry Name** | `PTH2_HUMAN` | Not declared in raw source | Reviewed Swiss-Prot entry |
| **Gene Symbol** | `PTRH2` | `Pth2/Bit1` | Canonical HGNC symbol |
| **Gene Aliases** | `BIT1`, `PTH2`, `CGI-147` | `Bit1`, `Pth2` | Common literature synonyms |
| **Protein Name** | Peptidyl-tRNA hydrolase 2, mitochondrial | `Pth2/Bit1 peptidyl-tRNA hydrolase 2/Bcl-2 inhibitor of transcription 1 EC:3.1.1.29` | Verbatim raw string contains merged synonyms and EC |
| **Enzyme Commission** | EC:3.1.1.29 | `EC:3.1.1.29` | Peptidyl-tRNA hydrolase |
| **Organism** | *Homo sapiens* | Not declared explicitly in row | Human (NCBI Taxonomy ID: `9606`) |
| **Catalog Entity ID** | `MFP:U:c382ca456ad5a4db` | Deterministic SHA-256 digest | Matches `mfp_proteins.csv` |
| **Catalog Source ID** | `multitaskprotdb_ii_row_672` | Data row 672 (line 673) | Matches `mfp_source_records.csv` |

### Distinction from Prior Misidentifications
- In earlier drafting notes and `tasks.md`, Record 6 was mistakenly referred to as "Bleomycin hydrolase (Bit1)".
- **Verification**: Human Bleomycin hydrolase is an entirely distinct protein encoded by `BLMH` (UniProtKB [`Q13867`](https://www.uniprot.org/uniprotkb/Q13867), EC:3.4.22.40, chromosome 17q11.2).
- The entity cataloged under `Q9Y3E5` is Peptidyl-tRNA hydrolase 2 / Bit1 (`PTRH2`, chromosome 17q25.1). The prior reference to Bleomycin hydrolase was an unsupported drafting error and is formally dismissed.

---

## 2. Internal Locator Integrity and Slice Provenance

A critical requirement of SDD verification is documenting locator transitions across raw, fixture, catalog, and interim pilot slices.

```
[Raw Database: data/raw/multitaskprotdb-ii/proteins.csv]
  └─ CSV Line 673 (1-based data row 672) ──► multitaskprotdb_ii_row_672
       │
[Local MVP Catalog: data/processed/mfp_catalog_mvp/mfp_source_records.csv]
  └─ Maps multitaskprotdb_ii_row_672 ───────► MFP:U:c382ca456ad5a4db
       │
[Test Fixture: tests/fixtures/functional_claims_multitask/multitask_real_extract.csv]
  └─ Row 6 of 6-record slice extract
       │
[Pilot Slice: data/interim/pilot/multitask_slice/claims.csv]
  └─ Re-indexed as ────────────────────────► multitaskprotdb_ii_row_6
```

### Locator Traceability Assessment
1. **Raw Database Locator**:
   - `multitaskprotdb-ii/proteins.csv` contains 694 data rows. The record for `Q9Y3E5` is at 1-based data row 672 (line 673).
   - In `data/processed/mfp_catalog_mvp/mfp_source_records.csv`, this record is registered with `source_record_id = "multitaskprotdb_ii_row_672"`.
2. **Interim Slice Locator Shift**:
   - The pilot slice builder (`scripts/build_multitask_slice.py`) processed `multitask_real_extract.csv` where this record was placed at row 6.
   - Consequently, in `data/interim/pilot/multitask_slice/claims.csv` and `source_go_annotations.csv`, the record is serialized as `multitaskprotdb_ii_row_6`.
3. **Traceability Accounting**:
   - The re-indexing relationship is explicitly recorded in `data/interim/pilot/multitask_slice/manifest.json`:
     `"source_record_id": "multitaskprotdb_ii_row_6"` with parent provenance documented.
   - **Pre-Curation Finding**: Any automated join between the full catalog and the pilot slice must map through `manifest.json` or use `canonical_accession = "Q9Y3E5"` / `protein_id = "MFP:U:c382ca456ad5a4db"`, rather than assuming slice row numbers equal parent database row numbers.

---

## 3. Bibliographic Evidence Baseline & Material Inspected

To ground the claims, external literature was consulted through official public citation metadata, abstracts, and structural repositories.

### Article 1: Primary Structural and Catalytic Characterization (Raw Source Citation)

- **Citation**: J. M. de Pereda, W. F. Waas, Y. Jan, E. Ruoslahti, P. Schimmel, and J. Pascual. *"Crystal structure of a human peptidyl-tRNA hydrolase reveals a new fold and suggests basis for a bifunctional activity."* **Journal of Biological Chemistry**, 279(9):8111–8115, February 27, 2004 (Electronic publication December 5, 2003).
- **Identifiers**:
  - PubMed ID: `14660562`
  - DOI: `10.1074/jbc.M311449200`
  - Protein Data Bank (PDB): **`1Q7S`** (Confirmed via PubMed and RCSB PDB)
- **Crystallographic Resolution**: **2.0 Å** (2.00 Å)
- **Inspection Status**: *Abstract inspected; PDB entry 1Q7S structure metadata inspected; Full text inaccessible* (ScienceDirect/Elsevier paywall and Cloudflare anti-bot 403 block on automated retrieval; no open-access repository copy in PMC or Europe PMC).
- **Source Linkage**: Verbatim citation in raw MultitaskProtDB-II (`Reference = "14660562"`).
- **Core Scientific Findings (Directly from Inspected Abstract & PDB Metadata)**:
  1. **Enzymatic Hydrolase Activity**: Peptidyl-tRNA hydrolase activity releases tRNA from the premature translation termination product peptidyl-tRNA. Recombinant *H. sapiens* Pth2 catalytic efficiency is comparable to archaeal *Sulfolobus solfataricus* Pth2 and higher than bacterial *E. coli* Pth.
  2. **Active Site Architecture**: Active site mapped to two close loops containing highly conserved residues, presenting an architecture unrelated to *E. coli* Pth.
  3. **Structural Fold**: Solved at 2.0 Å resolution. Features a novel $\alpha/\beta$ fold consisting of a central **four-stranded antiparallel $\beta$-sheet** core surrounded by two $\alpha$-helices on each side.
  4. **Bifunctionality Hypothesis**: Intermolecular contacts in the crystal asymmetric unit cell suggest a likely surface for protein-protein interactions related to Pth2-mediated apoptosis.
- **Critical Distinction**: The crystallographic contact in the asymmetric unit cell is an inference/hypothesis of a putative interaction surface, **not** direct proof of a physiological binding partner or cellular mechanism in vivo.

---

### Article 2: Discovery of Bit1 Apoptosis Regulation and Interaction with AES

- **Citation**: Y. Jan, M. Matter, J. Pai, Y. Chen, J. Pilch, M. Komatsu, E. Ong, M. Fukuda, and E. Ruoslahti. *"A mitochondrial protein, Bit1, mediates apoptosis regulated by integrins and Groucho/TLE corepressors."* **Cell**, 116(5):751–762, March 5, 2004.
- **Identifiers**:
  - PubMed ID: `15006356`
  - DOI: `10.1016/S0092-8674(04)00204-1`
- **Inspection Status**: *Abstract inspected; MeSH metadata inspected; Full text inaccessible* (Cell / Elsevier subscription barrier and Cloudflare 403 block on direct programmatic retrieval; no open-access repository copy in PMC or Europe PMC).
- **Relationship to Source Citation**: Published contemporaneously in March 2004 from the same research groups.
- **Core Scientific Findings (Directly from Inspected Abstract)**:
  1. **Subcellular Localization**: Bit1 identified as a mitochondrial protein.
  2. **Apoptotic Release**: Released from mitochondria into the cytoplasm during apoptosis.
  3. **Complex Formation**: Cytoplasmic Bit1 forms a physical complex with AES (a small Groucho/transducin-like enhancer of split [TLE] protein).
  4. **Cell Death Phenotype**: Bit1 and AES induce cell death with characteristics of caspase-independent apoptosis.
  5. **Integrin / ECM Regulation**: Cell attachment to fibronectin counteracts the apoptotic effect of Bit1 and AES. Overexpression of Bit1 enhances anoikis; suppression reduces it.
- **Critical Inspection Limitation**: The abstract does **not** explicitly state nuclear translocation, nucleoplasm localization, or direct transcriptional repression assays. While the article title mentions Groucho/TLE corepressors and subsequent literature discusses nuclear corepression, those specific experimental assertions cannot be verified from the abstract alone and remain uninspected.

---

### Article 3: Erratum for Cell 2004 Publication

- **Citation**: Erratum: *"A mitochondrial protein, Bit1, mediates apoptosis regulated by integrins and groucho/TLE corepressors."* **Cell**, 122(3):485–486, August 12, 2005.
- **Identifiers**:
  - PubMed: Linked via `CommentsCorrections RefType="ErratumIn"` to PMID `15006356`
  - DOI: `10.1016/j.cell.2005.07.022`
- **Inspection Status**: *Metadata only; Inaccessible material* (Publisher access barrier on ScienceDirect / Cloudflare 403; not indexed as an independent abstract on PubMed).
- **Documented Relevance from Authoritative Metadata**:
  - Publication metadata indicates author name spelling corrections/clarifications in the author line (e.g., Ya-Huei Jan, Jean-Tzung Pai, Ya-Li Chen, Masahiro Komatsu, Eric Ong, Michiko Fukuda).
  - The substantive text of the correction notice is inaccessible under open-access programmatic consultation. In strict compliance with SDD standards, its content is not guessed or presumed.

---

## 4. Auditable Claim–Evidence Table

The table below breaks down every asserted biological property into a discrete, auditable statement evaluated against the lawfully inspected primary material.

| ID | Exact Biological Statement | Source PMID / DOI | Short Supporting Quotation | Locator | Experimental System & Organism | Perturbation or Assay | What Was Directly Observed | Authors' Interpretation | Remaining Inference / Uncertainty | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **STMT-01** | Human Pth2/Bit1 possesses enzymatic peptidyl-tRNA hydrolase activity (EC:3.1.1.29) that releases tRNA from peptidyl-tRNA. | PMID 14660562<br>DOI 10.1074/jbc.M311449200 | *"Peptidyl-tRNA hydrolase (Pth) activity releases tRNA from the premature translation termination product peptidyl-tRNA... Here we report the crystallographic structure of the Homo sapiens Pth2 at a 2.0-A resolution as well as its catalytic properties. Its catalytic efficiency is comparable with that reported for the archaeal Sulfolobus solfataricus Pth2..."* | Abstract | In vitro biochemical assay using recombinant *Homo sapiens* Pth2 protein | In vitro enzymatic assay measuring catalytic cleavage of peptidyl-tRNA substrate compared to archaeal and bacterial homologs | Catalytic efficiency is comparable to *S. solfataricus* Pth2 and higher than *E. coli* Pth; active site mapped to two conserved loops | *H. sapiens* Pth2 is a bona fide enzymatic peptidyl-tRNA hydrolase with a novel fold | In vivo turnover rate of peptidyl-tRNA in human mitochondria is not demonstrated in abstract | **Supported** |
| **STMT-02** | Bit1 is localized to mitochondria under basal conditions. | PMID 15006356<br>DOI 10.1016/S0092-8674(04)00204-1 | *"...we identified Bit1, a mitochondrial protein that is released into the cytoplasm during apoptosis."* | Abstract | Mammalian cell culture (*Homo sapiens* / mammalian cells) | Cell screening and subcellular tracking in cell adhesion / survival assays | Bit1 resides in the mitochondrial fraction under basal conditions | Bit1 is a mitochondrial protein | Specific submitochondrial compartment (matrix vs membrane vs intermembrane space) is not specified in abstract | **Supported** |
| **STMT-03** | Bit1 is released from mitochondria into the cytoplasm upon apoptosis / loss of cell adhesion (anoikis). | PMID 15006356<br>DOI 10.1016/S0092-8674(04)00204-1 | *"...we identified Bit1, a mitochondrial protein that is released into the cytoplasm during apoptosis. Cytoplasmic Bit1 forms a complex with AES..."* | Abstract | Mammalian cell culture | Induction of apoptosis / loss of ECM attachment | Translocation of Bit1 from mitochondria to the cytoplasm | Release into cytoplasm is a physiological event triggered by apoptosis | Specific permeabilization / release channel mechanism is not described in abstract | **Supported** |
| **STMT-04** | Cytoplasmic Bit1 physically forms a complex with AES (Amino-terminal Enhancer of Split). | PMID 15006356<br>DOI 10.1016/S0092-8674(04)00204-1 | *"Cytoplasmic Bit1 forms a complex with AES, a small Groucho/transducin-like enhancer of split (TLE) protein..."* | Abstract | Mammalian cell culture / protein interaction assay | Detection of complex formation in cytoplasm | Physical complex between cytoplasmic Bit1 and AES protein | Bit1–AES complex is an active signaling unit formed in the cytoplasm | In vitro binding affinity ($K_d$) and structural interface are not detailed in abstract | **Supported** |
| **STMT-05** | Cytoplasmic Bit1 and AES induce caspase-independent apoptosis, counteracted by integrin attachment to fibronectin. | PMID 15006356<br>DOI 10.1016/S0092-8674(04)00204-1 | *"...and induces cell death with characteristics of caspase-independent apoptosis. Cell attachment to fibronectin counteracts the apoptotic effect of Bit1 and AES. Increasing Bit1 expression enhances anoikis, while suppressing the expression reduces it."* | Abstract | Mammalian cell culture on fibronectin vs suspension | Expression modulation (overexpression and suppression) and substrate adhesion | Bit1+AES induces caspase-independent apoptosis; fibronectin suppresses death; overexpression increases anoikis, suppression decreases it | Bit1 pathway is an integrin-regulated mechanism controlling anoikis | Downstream caspase-independent death executioners are not identified in abstract | **Supported** |
| **STMT-06** | Bit1 or the Bit1–AES complex translocates into the nucleus / nucleoplasm to execute downstream functions. | PMID 15006356<br>PMID 14660562 | None in inspected abstracts | Abstract / Metadata | Not assessed in inspected material | Inaccessible full-text assays | Nuclear accumulation is not reported in inspected abstracts | Cannot be assessed without full text | Secondary database annotations assert nucleoplasm localization (`GO:0005654`, `IDA:HPA`), but primary paper assertion is unverified | **Not established by inspected material** |
| **STMT-07** | Bit1 interacts with full-length Groucho/TLE corepressors (such as TLE1). | PMID 15006356 | Title: *"...regulated by integrins and Groucho/TLE corepressors."*<br>Abstract: *"...AES, a small Groucho/transducin-like enhancer of split (TLE) protein..."* | Title & Abstract | Mammalian system | Inspected abstract specifically describes AES interaction | AES is identified as a Groucho/TLE family member forming a complex with Bit1 | Pathway involves Groucho/TLE regulation | Whether Bit1 binds full-length TLE1 directly or acts through AES dimerization is not established in abstract | **Partially supported** (AES confirmed; full TLE1 direct binding not established) |
| **STMT-08** | Bit1 acts as a transcriptional repressor or directly regulates promoter transcription. | PMID 15006356<br>PMID 14660562 | None in inspected abstracts | Abstract / Metadata | Not assessed in inspected material | Inaccessible full-text assays | Transcriptional repression assays (e.g. luciferase reporters) are not reported in abstracts | Cannot be assessed without full text | Source database records "Inhibitor of transcription", but primary experimental demonstration cannot be inspected in abstract | **Not established by inspected material** |

---

## 5. Contextual Synthesis & Scientific Invariants

### 1. Distinction Between Interaction, Process, and Molecular Activity
- **Autonomous Catalytic Activity**: Peptidyl-tRNA hydrolase activity (cleavage of aminoacyl-tRNA ester bond) is demonstrated biochemically using purified recombinant protein ([`STMT-01`](#4-auditable-claim-evidence-table)).
- **Protein-Protein Interaction**: Binding to AES in the cytoplasm is directly evidenced ([`STMT-04`](#4-auditable-claim-evidence-table)).
- **Biological Process Involvement**: Promoting caspase-independent cell death and regulating anoikis sensitivity is demonstrated in cellular assays ([`STMT-05`](#4-auditable-claim-evidence-table)).
- **Molecular Corepression Activity**: Autonomous or recruited transcriptional repression cannot be asserted as an established molecular activity without accessible full-text evidence ([`STMT-08`](#4-auditable-claim-evidence-table)).
- **Crystallographic Contacts**: Asymmetric unit contacts observed in PDB `1Q7S` represent a structural surface hypothesis for protein-protein interaction, not physiological proof of AES or corepressor complex formation.

### 2. Verified Cellular State Transition
The inspected primary literature supports a clear, condition-dependent physiological transition:

```
[State A: Basal / Adherent Cells]
  - Subcellular Location: Mitochondria
  - Physiological Status: Attached to extracellular matrix (fibronectin) via integrins
  - Molecular State: Intact mitochondrial residence; peptidyl-tRNA hydrolase potential
       │
       ▼ (Trigger: Loss of cell-ECM attachment / anoikis induction)
       │
[State B: Apoptotic / Detached Cells]
  - Subcellular Location: Cytoplasm (translocated from mitochondria)
  - Molecular State: Physical complex with AES
  - Physiological Outcome: Caspase-independent apoptosis / anoikis execution
```

### 3. Bioinformatic Invariant Enforcement
In raw MultitaskProtDB-II, `GO` lists `GO:0005739` (mitochondrion) and `GO:0004045` (hydrolase), while `GO_Moon` lists `GO:0005654` (nucleoplasm) and `GO:0006355` (regulation of transcription).
- **Rule**: Co-annotation in a flat tabular record does **not** justify synthesizing functional triplets $\tau = (m_i, b_j, c_k)$ by Cartesian product.
- **Biochemical Reality**: Peptidyl-tRNA hydrolase activity in the nucleus is completely unsupported. Transcriptional regulation in mitochondria is unsupported. The functions operate under mutually exclusive cellular states and distinct compartments.

---

## 6. Outcome Assessment and Pending Decision Gates

### Provisional Verdict: **Context Partially Supported (With Declared Access Boundaries)**

- **Supported Baseline**:
  1. Primary enzymatic activity (peptidyl-tRNA hydrolase, EC:3.1.1.29) is supported in vitro (`STMT-01`).
  2. Basal mitochondrial localization (`STMT-02`) and apoptotic release into the cytoplasm (`STMT-03`) are supported in mammalian cells.
  3. Cytoplasmic interaction with AES (`STMT-04`) and induction of caspase-independent apoptosis counteracted by fibronectin attachment (`STMT-05`) are supported.
- **Unestablished / Inaccessible Scope**:
  1. Nuclear translocation (`STMT-06`), full-length TLE1 direct binding (`STMT-07`), and direct transcriptional repression (`STMT-08`) are **not established** by the lawfully inspected abstract/metadata material. Full primary articles are inaccessible behind publisher access controls.

### Status of Decision Gates

| Decision Gate | Decision Topic | Status | Detailed Rationale |
|---|---|---|---|
| **DEC-CUR-01** | **Autonomous Activity vs Complex Corepression** | **KEPT STRICTLY PENDING** | Neither "autonomous transcriptional repression" nor "recruited corepressor complex activity" is established by the inspected primary abstracts. Adjudicating between them would force a choice based on missing evidence. This gate remains blocked until lawful access to full-text experimental assays is obtained. |
| **DEC-CUR-02** | **Physiological State Modeling in Catalog Schemas** | **DEFERRED** | The experimental conditions (basal adherent vs apoptotic detached) are preserved in the text of this dossier. Final triplet schema formalization is deferred until Level 2 schema expansion is authorized. |
| **DEC-CUR-03** | **Multi-Source Citation Overrides** | **OPEN GOVERNANCE QUESTION** | MultitaskProtDB-II cited only PMID 14660562, which reports hydrolase activity and crystal structure. PMID 15006356 provides the anoikis/AES evidence. Repository governance must decide whether to store multi-source bibliographic crosswalks in catalog metadata. |

---

## 7. Correction History

This section maintains an auditable record of corrections made during the review of this provisional dossier.

| Correction ID | Target Section | Previous Erroneous / Unsupported Attribution | Corrected Verified Attribution | Authoritative Source / Evidence |
|---|---|---|---|---|
| **CORR-01** | Section 3 (Article 1) | PDB IDs reported as `1RB0` (free) and `1RB2` (bound) | PDB ID is **`1Q7S`** (`1RB0`/`1RB2` are unrelated enzymes, HPPK and DHFR) | RCSB PDB entry `1Q7S`; PubMed DataBankList for PMID 14660562 |
| **CORR-02** | Section 3 (Article 1) | Crystallographic resolution reported as 1.7 Å | Crystallographic resolution is **2.0 Å** (2.00 Å) | Abstract of PMID 14660562; RCSB PDB entry `1Q7S` |
| **CORR-03** | Section 3 (Article 1) | Core fold reported as "six-stranded parallel $\beta$-sheet" | Core fold is a **four-stranded antiparallel $\beta$-sheet** flanked by $\alpha$-helices | Abstract of PMID 14660562 |
| **CORR-04** | Section 3 & 4 (Article 2) | Asserted nuclear translocation and nuclear corepressor complex formation as established findings of PMID 15006356 | Downgraded to **not established by inspected material**; inspected abstract describes cytoplasmic release, AES complex, and caspase-independent cell death, not nuclear localization | Abstract of PMID 15006356; full text inaccessible behind Elsevier paywall/403 |
| **CORR-05** | Section 3 (Erratum) | Erratum omitted or undocumented | Formally documented Erratum (*Cell* 122:485–486; DOI `10.1016/j.cell.2005.07.022`) as *Metadata only / Inaccessible material* correcting author names; content not invented | PubMed CommentsCorrections on PMID 15006356 |
| **CORR-06** | Section 6 (Decisions) | Asked user to choose between autonomous repression vs corepressor recruitment | **Kept DEC-CUR-01 strictly pending**; refused to force a decision on missing evidence | Auditable Claim–Evidence Table (`STMT-06`, `STMT-08`) |

---

## 8. Verification Record

```markdown
### Provisional Dossier Verification Record

- **Target Entity**: Q9Y3E5 / PTRH2 / Bit1 (MFP:U:c382ca456ad5a4db)
- **Target Slice Record**: multitaskprotdb_ii_row_6 (parent: multitaskprotdb_ii_row_672)
- **Status**: Draft — bibliographic verification and contextual evidence review; not approved biological adjudication
- **Material Inspected**:
  - PMID 14660562 (De Pereda et al., JBC 2004): Abstract inspected; RCSB PDB 1Q7S metadata inspected (2.0 Å, 1Q7S)
  - PMID 15006356 (Jan et al., Cell 2004): Abstract inspected; MeSH metadata inspected (mitochondrial release, AES, anoikis)
  - Cell 2005 Erratum (DOI 10.1016/j.cell.2005.07.022): Metadata only (author line corrections); body inaccessible
- **Material Inaccessible**:
  - Full text of PMID 14660562 and PMID 15006356 (Elsevier / ScienceDirect paywall and Cloudflare 403 block)
- **Invariants Enforced**:
  - Separation between autonomous catalytic activity, protein binding, process involvement, and crystal contact hypotheses
  - Zero Cartesian triplet synthesis
  - Zero git commits, staging operations, or database writes
```
