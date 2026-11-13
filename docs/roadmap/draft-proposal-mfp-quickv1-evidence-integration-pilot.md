# Draft Experimental Proposal: Bounded Evidence Integration Pilot between `mfp-bibliography` and `MFP_QuickV1`

| Attribute | Specification Record |
|---|---|
| **Document Title** | Draft Experimental Proposal: Bounded Evidence Integration Pilot between `mfp-bibliography` and `MFP_QuickV1` |
| **Document ID** | `PROP-PILOT-QUICKGO-2026-11-12` |
| **Document Location** | [`docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md`](draft-proposal-mfp-quickv1-evidence-integration-pilot.md) |
| **Status** | **Draft — P1–P2 Completed & Verified; P3 Specification Reconciled Awaiting Scope Authorization** |
| **Date** | 2026-11-12 |
| **Revision** | **v1.3 (Final Pre-P3 Bounded Corrections & Specification Alignment)** |
| **Auditor / Architect** | Senior Scientific Software Auditor & Bioinformatics Data Architect |
| **Target Repository** | `mfp-bibliography` (in coordination with `protein-information-system`) |
| **Authority Level** | Level 6: Draft Proposal for Human Review (strictly NOT authorization to implement or modify databases/code) |
| **Governing Rules** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |

---

### Document Revision History

| Version | Date | Author | Description of Changes |
|---|---|---|---|
| **v1.0** | 2026-11-12 | Scientific Software Auditor | Initial draft synthesizing empirical findings from read-only inspection of `MFP_QuickV1` and outlining pilot feasibility. |
| **v1.1** | 2026-11-12 | Senior Scientific Software Auditor & Data Architect | Comprehensive realignment: (1) Replaced inner joins in export with left-joined coverage accounting for all 8 cohort accessions; (2) Separated raw extraction contracts from normalized schemas; (3) Replaced "unverified positive" / "quarantine" terminology with neutral `qualifier_status = "not_captured"`; (4) Documented `P34788` species discrepancy (*Spinacia oleracea* vs *Arabidopsis thaliana*) as an unresolved upstream biological identity issue; (5) Calibrated `Q42525` PMID claims to verified references; (6) Reclassified technical controls (`A0A0H3CDS3`, `E6KMA1`) as database missingness controls; (7) Clarified roadmap governance regarding ADR-007 descoping and ADR-008 Level 2 boundaries; (8) Isolated output artifacts under `data/interim/pilot/quickgo_slice/`. |
| **v1.2** | 2026-11-12 | Senior Scientific Software Auditor & Data Architect | Formal P3 specification reconciliation under `QUICKGO-PRE-P3-CLOSURE-001`: (1) Formulated explicit research question and strict non-objectives; (2) Reconciled Stage P1–P2 completed raw contracts vs deferred Stage P3 normalized schemas; (3) Added unified Single P3 Policy Table (Policies A–E) defining complete inventory, unfiltered overlap, filtered comparison (ND and root-term exclusions), experimental sensitivity extension, and neutral qualifier policy; (4) Formalized comparison unit `(accession, source_id, aspect, policy_id)` and empty-set Jaccard conventions with explicit non-evaluable reasons; (5) Recorded exact input file paths and SHA-256 digests; (6) Reconciled 2-letter evidence code patterns (`^[A-Z]{2,3}$`) and replaced qualitative status enums with `evaluable`/`not_evaluable`; (7) Updated machine-specific links to repository-relative markdown links. |
| **v1.3** | 2026-11-12 | Senior Scientific Software Auditor & Data Architect | Final pre-P3 bounded corrections: (1) Corrected empty-set Jaccard mathematics (0 when one side empty, undefined 0/0 when both empty; pilot convention proposes null to separate coverage gaps from observed disjoint inventories); (2) Removed unsupported ECO crosswalk prerequisite for filtering already captured legacy experimental codes under deferred Policy D; (3) Stated unequivocal 1:1 raw row preservation and deduplication-only-at-comparison rule; (4) Formalized biological identity compatibility as distinct evaluability condition and specified deterministic primary/secondary non-evaluable reason hierarchy; (5) Formulated annotation identifier using capture scope and database row ID, and removed protein_id truncation in concordance keys; (6) Added dedicated normalized coverage contract to proposed P3 deliverables and specified input provisioning requirements for clone reproducibility. |

---

> [!WARNING]
> **Draft Proposal & Operational Boundary Notice**
> This document is a **draft experimental proposal** prepared for the scientific lead and repository maintainers.
> In accordance with repository governance ([`AGENTS.md` §1.1, §4, §6](../../AGENTS.md)):
> 1. This document **does NOT authorize** implementing Stage P3/P4 pipeline code, database migrations, schema edits, or live external network requests.
> 2. Database access during Stages P1–P2 was conducted strictly under **session-level read-only transactions** (`SET default_transaction_read_only = ON;`), causing zero writes, schema changes, or background mutations.
> 3. No credentials or passwords appear in this document. All SQL query templates and command examples use environment variable placeholders.

---

## 1. Executive Summary

### 1.1 Purpose, Proposed Research Question, and Bounded Scope
This proposal specifies a small, offline integration pilot designed to evaluate how source-native functional evidence cataloged in `mfp-bibliography` can be systematically cross-referenced against external Gene Ontology annotations currently stored in the local database `MFP_QuickV1`.

#### Explicit Proposed Research Question
> **"For a purposively selected eight-accession cohort, what exact GO-identifier and reference overlap is observed between source-explicit annotations and the frozen MFP_QuickV1 capture, and how do coverage, identity, and capture limitations constrain this comparison?"**

#### Explicit Scientific Scope & Boundaries (Non-Objectives)
In compliance with repository governance ([`AGENTS.md` §1.2, §5](../../AGENTS.md)):
- **Bounded Descriptive Integration Pilot**: Evaluates set-theoretic overlap and reference matching for 8 specific cohort proteins.
- **NOT a Representative Catalog Estimate**: Findings from this purposive 8-protein cohort cannot be generalized to the full 2,322 entities of the catalog candidate release.
- **NOT Biological Validation of Multifunctionality**: Lexical overlap of Gene Ontology terms between source records and external annotations does not confirm or refute moonlighting activity.
- **NOT Literature Adjudication**: Co-occurrence of PMIDs at the protein level does not verify whether cited papers validate specific functional assertions.
- **NOT Classifier Training or Semantic Embedding**: BioData / `MFP_QuickV1` is a contextual reference population, never a negative class. No machine learning models, negative control sets, or semantic embeddings will be constructed.
- **NOT a Complete Reconstruction of QuickGO Responses**: The pilot evaluates only the attributes retained in the local database capture, without attempting to reconstruct full GAF/GPAD records from the live QuickGO API.

### 1.2 Feasibility Verdict & Separation of Evidence Levels
An offline evidence integration pilot across the 8-protein cohort is **FEASIBLE UNDER BOUNDED CHANGES**. Stages P1–P2 have successfully delivered frozen, validated input fixtures on disk.

To maintain strict scientific auditability, the proposal distinguishes four distinct levels of knowledge:
- **Empirical Database Findings**: Concrete facts verified through direct read-only SQL inspection of `MFP_QuickV1` on `2026-11-12 15:53:22 UTC` (96,265 annotation rows; coexistence of bare numeric PMIDs and canonical `GO_REF` CURIEs; 149 unlinked accessions; 15 zero-annotation proteins; complete absence of qualifier and ECO columns).
- **Tested Upstream Extractor Behavior**: Functionality verified in the `protein-information-system` (PIS) codebase (`feature/quickgo-annotations-v2`, commit `f54bc4f`), which preserves bare numeric PMIDs and `GO_REF:[0-9]{7}` strings within `publication_id`.
- **Database Capture Limitations**: Biological and administrative attributes dropped during upstream ingestion (e.g., `qualifier`, `eco_code`, `assigned_by`, `date`, `with_from`, `extensions`). These cannot be reconstructed from the database snapshot and must be recorded as uncaptured.
- **Proposed Pilot Functionality**: The analytical pipeline, JSON schemas, coverage accounting, and concordance metrics defined in this document, which remain **unimplemented proposals** awaiting human review and governance sign-off.

### 1.3 Key Verification Findings (Stages P1–P2 Baseline)
1. **Verified `GO_REF` and `PMID` Coexistence**:
   Read-only SQL inspection confirmed that `protein_go_term_annotation` in `MFP_QuickV1` stores **both** bare numeric PubMed identifiers (55,506 rows, 57.66%) and canonical `GO_REF` CURIEs with intact prefixes and 7-digit formatting (37,901 rows, 39.37%) in column `publication_id`.
2. **Exact Reference Reconciliation**:
   The database total of 96,265 annotation rows reconciles **100.0%** across mutually exclusive reference categories:
   $$\text{Total Annotations (96,265)} = \text{PMID (55,506)} + \text{Canonical GO\_REF (37,901)} + \text{NULL (2,858)}$$
   There are exactly **0 empty strings**, **0 malformed GO_REFs**, and **0 unmapped non-PMID strings** in `publication_id`. Exactly 2,849 of the 2,858 `NULL` rows (99.68%) correspond to the Traceable Author Statement (`TAS`) evidence code.
3. **Database Scope and Denominator Gaps**:
   `MFP_QuickV1` contains 2,181 proteins and 2,330 accessions derived from an earlier proteomic snapshot (`BioData`), not the unified 2,322 entities of catalog candidate `v0.3.0`.
   - **149 accessions** in `accession` have `protein_id IS NULL` (e.g., `E6KMA1`, `A0A0H2Q1X0`).
   - **15 proteins** in `protein` have **0 annotations** in `protein_go_term_annotation` (e.g., `A0A0H3CDS3`).
   - Certain candidate v0.3.0 accessions (e.g., `Q9LIA4`, `Q9SJE9`, `Q9XIU3`) are entirely absent from `MFP_QuickV1`.
4. **Complete Qualifier Absence and Polarity Neutrality**:
   `MFP_QuickV1` contains **no `qualifier` column**. Because neither positive relation qualifiers (e.g., `enables`, `contributes_to`) nor negative qualifiers (e.g., `NOT`) were stored, annotations have **unknown biological polarity**. They are admitted into the pilot with neutral policy status `qualifier_status = "not_captured"`.
5. **Frozen Fixture Verification**:
   The bounded read-only export executed in Stage P2 yielded **156 annotation rows** across the 6 annotated cohort members, and **8 coverage rows** accounting for 100% of the cohort. All rows conform strictly to Draft 2020-12 schemas.

---

## 2. Context & Empirical Database Baseline

### 2.1 Repository States
- **`mfp-bibliography`**:
  - *Location*: Repository root
  - *Branch*: `feature/functional-normalization`
  - *Status*: Clean working tree for tracked files. 644 offline unit, contract, and pipeline tests passing.
  - *Governing Authority*: Candidate release `v0.3.0` packaged under [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md); functional normalization pilot governed by proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md).
- **`protein-information-system` (PIS)**:
  - *Branch*: `feature/quickgo-annotations-v2` (Commit `f54bc4f`)
  - *Status*: Clean working tree. Implements `QuickGOAnnotationExtractor.extract_publication_id()` preserving both bare numeric PMIDs and canonical `GO_REF:[0-9]{7}` CURIEs.
  - *Target Database*: `MFP_QuickV1` on `localhost:5432`.

### 2.2 Inspection Safeguards and Snapshot Consistency
In accordance with user authorization and repository governance:
- All database queries were executed using explicit session-level read-only transactions:
  ```sql
  SET default_transaction_read_only = ON;
  ```
- No write, update, create, alter, or drop statements were executed.
- Query connections avoided credential exposure in shell history, process arguments, or disk logs.
- Active connection profiling via `pg_stat_activity` confirmed zero concurrent write processes or active background workers during the inspection window. All empirical measurements reflect a stable point-in-time snapshot observed on `2026-11-12 15:53:22 UTC`. The Stage P2 export executed within an explicit `BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY` block.

---

## 3. User-Reported versus Independently Observed Measurements

All counts were recorded inside a single read-only transaction on `2026-11-12 15:53:22 UTC`:

| Metric / Table Field | User-Reported Count | Independently Observed Count | Discrepancy | Verification Status |
|---|---|---|---|---|
| **`protein_go_term_annotation` total rows** | 96,265 | **96,265** | 0 | **VERIFIED EXACT** |
| **Numeric PMID rows** (`publication_id ~ '^[0-9]+$'`) | 55,506 | **55,506** | 0 | **VERIFIED EXACT** |
| **GO_REF rows** (`publication_id LIKE 'GO_REF%'`) | 37,901 | **37,901** | 0 | **VERIFIED EXACT** |
| **Canonical GO_REF rows** (`^GO_REF:[0-9]{7}$`) | *(unspecified)* | **37,901** | 0 | **100% CANONICAL** |
| **Distinct GO_REF identifiers** | *(unspecified)* | **29** | — | Top: `GO_REF:0000033` (7,810 rows) |
| **Distinct PMID identifiers** | *(unspecified)* | **18,108** | — | Min: 1, Max: 437 per protein |
| **NULL `publication_id` rows** | *(unspecified)* | **2,858** | — | 2,849 are `TAS` evidence |
| **Empty string `publication_id` rows** | *(unspecified)* | **0** | 0 | **ZERO EMPTY STRINGS** |
| **Other non-empty `publication_id` rows** | *(unspecified)* | **0** | 0 | **ZERO OTHER FORMATS** |
| **`protein` total rows** | 2,181 | **2,181** | 0 | **VERIFIED EXACT** |
| **`go_terms` total rows** | 9,335 | **9,335** | 0 | **VERIFIED EXACT** |
| **`accession` total rows** | *(unspecified)* | **2,330** | — | 2,330 distinct codes |
| **Accessions with `protein_id IS NULL`** | *(unspecified)* | **149** | — | Unlinked in database capture |
| **Proteins with 0 annotations** | *(unspecified)* | **15** | — | E.g., `A0A0H3CDS3` (KidO) |
| **Distinct `(protein_id, go_id)` pairs** | *(unspecified)* | **46,943** | — | Avg 2.05 rows per pair |

### Mutually Exclusive Reference Reconciliation:
$$\begin{aligned}
\text{Total Rows} &= 96,265 \\
&= 55,506 \text{ (Numeric PMIDs, 57.66\%)} \\
&\quad + 37,901 \text{ (Canonical GO\_REFs, 39.37\%)} \\
&\quad + 2,858 \text{ (NULL References, 2.97\%)} \\
&\quad + 0 \text{ (Empty Strings)} + 0 \text{ (Other Formats)}
\end{aligned}$$

---

## 4. Database Schema Architecture, Capabilities, and Limitations

### 4.1 Relational Architecture and Entity Linkage
The database structure governing Gene Ontology evidence in `MFP_QuickV1` consists of four primary tables:

```
┌───────────────────────┐             ┌─────────────────────────┐
│       accession       │             │         protein         │
├───────────────────────┤             ├─────────────────────────┤
│ code (PK, varchar)    │             │ id (PK, varchar)        │
│ primary (boolean)     │──(N:1 FK)──►│ data_class, gene_name   │
│ protein_id (FK, varch)│             │ organism, taxonomy_id   │
└───────────────────────┘             └─────────────────────────┘
                                                   │
                                                (1:N FK)
                                                   ▼
┌───────────────────────┐             ┌─────────────────────────┐
│       go_terms        │             │protein_go_term_annotat. │
├───────────────────────┤             ├─────────────────────────┤
│ go_id (PK, varchar)   │◄──(1:N FK)──│ id (PK, int auto)       │
│ category (varchar)    │             │ protein_id (FK, varchar)│
│ description (varchar) │             │ go_id (FK, varchar)     │
└───────────────────────┘             │ evidence_code (varchar) │
                                      │ publication_id (varchar)│
                                      └─────────────────────────┘
```

### 4.2 Meaning of Uniqueness in `protein_go_term_annotation`
The table enforces a composite unique constraint:
```sql
CONSTRAINT uq_pga_protein_go_evidence_publication 
UNIQUE (protein_id, go_id, evidence_code, publication_id)
```
- **Operational Meaning**: An annotation row in `MFP_QuickV1` is not an atomic protein-term assertion, but a **(Protein, GO Term, Evidence Code, Reference) 4-tuple**.
- **Multi-Reference Expansion**: When multiple publications support the same term and evidence code, each publication generates a distinct row:
  - 65,076 tuples have exactly 1 reference.
  - 6,779 tuples have $>1$ references, generating 31,189 rows.
  - Extreme cases reflect intensive historical research: for human p53 (`P04637`), term `GO:0005515` (protein binding) under evidence `IPI` is supported by **120 distinct publication rows**.
- **Cardinality Hierarchy**:
  $$\text{Annotation Rows (96,265)} \ne \text{(Protein, GO, Evidence) Triples (71,855)} \ne \text{(Protein, GO) Pairs (46,943)} \ne \text{Annotated Proteins (2,166)}$$

### 4.3 Evidence Code & GO Aspect Distributions
- **Aspects in `go_terms`**:
  Stored heterogeneously as single-letter codes (`P`, `F`, `C`) and long-form strings (`biological_process`, `molecular_function`, `cellular_component`). Normalized aspect distribution:
  - **Molecular Function (MF)**: 40,891 annotation rows (42.48%) across 2,564 terms.
  - **Biological Process (BP)**: 30,494 annotation rows (31.68%) across 5,741 terms.
  - **Cellular Component (CC)**: 24,880 annotation rows (25.85%) across 1,030 terms.
- **Evidence Codes**:
  Distributed across 22 codes, including two-letter codes (`IC`, `ND`) and three-letter codes (`EXP`, `IDA`, `IEA`, `IBA`, `IPI`, `IMP`, etc.).
  - Electronic annotations (`IEA`, 22,691 rows) and biological ancestor annotations (`IBA`, 7,810 rows) are supported **100% by `GO_REF` CURIEs**.
  - Experimental codes (`IDA`, `IPI`, `IMP`, `EXP`, etc., totaling 51,132 rows) are supported **98.0% by PMIDs**.
  - No-data annotations (`ND`, 39 rows in database) are supported by `GO_REF` CURIEs (e.g. `GO_REF:0000015`).

### 4.4 Verified Database Limitations & Missing Attributes

| Attribute | Standard QuickGO GAF/GPAD Field | Present in `MFP_QuickV1`? | Capture Status in Database | Analytical Handling in Pilot |
|---|---|---|---|---|
| **UniProt Accession** | `DB_Object_ID` | Yes (in `accession`) | Direct string | Mapped to catalog `protein_id` via candidate v0.3.0 |
| **Protein Entity ID** | Swiss-Prot ID | Yes (in `protein`) | Primary key string | Retained as `database_protein_id` for provenance |
| **GO Identifier** | `GO_ID` | Yes (`go_terms`, `pga`) | `^GO:[0-9]{7}$` | Validated term identifier |
| **GO Aspect / Category** | `Aspect` | Yes (in `go_terms`) | `P`/`F`/`C` or strings | Normalized to controlled vocab: `BP`, `MF`, `CC` |
| **Evidence Code** | `Evidence_Code` | Yes (`pga`) | 2- or 3-letter code | Retained verbatim (`^[A-Z]{2,3}$`) |
| **Publication Reference** | `DB:Reference` | Yes (`pga`) | Bare PMID or `GO_REF` | Classify `reference_type`: `pmid`, `go_ref`, `null` |
| **Qualifier (`NOT`, enables)** | `Qualifier` | **NO** (0 columns) | **NOT CAPTURED** | Assigned neutral `qualifier_status = "not_captured"` |
| **ECO Code** | `ECO_Evidence_Code` | **NO** (0 columns) | **NOT CAPTURED** | Retained as schema `null` (CSV empty string `""`) |
| **Assigned By (Provider)** | `Assigned_By` | **NO** (0 columns) | **NOT CAPTURED** | Retained as schema `null` (CSV empty string `""`) |
| **Annotation Date** | `Date` | **NO** (0 columns) | **NOT CAPTURED** | Excluded from output schema |
| **With / From** | `With_From` | **NO** (0 columns) | **NOT CAPTURED** | Excluded from output schema |
| **Annotation Extensions** | `Annotation_Extension` | **NO** (0 columns) | **NOT CAPTURED** | Excluded from output schema |
| **Target Accession** | Query Accession | **NO** (indirect FK) | **PARTIAL** (via `accession`) | Reconciled via cohort accession mapping |
| **Acquisition Run ID** | Pipeline Metadata | **NO** (0 columns) | **NOT CAPTURED** | Recorded as capture metadata in manifest |

---

## 5. Proposed Pilot Cohort and Scientific Reconciliation

The cohort contains **8 empirical proteins**: 6 core candidate proteins and 2 technical controls for database missingness.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   RECOMMENDED INTEGRATION PILOT COHORT                 │
├────────────────────────────────────────────────────────────────────────┤
│ Core Empirical Candidates:                                             │
│ 1. Q42525 (Arabidopsis) : 3-source shared protein (MoonProt/PlantMP/MT)│
│ 2. Q9Y3E5 (Human Bit1)  : Explicit moonlighting CC (GO:0005654) + PMID │
│ 3. P0AFW0 (E. coli)     : 2-source shared protein (MoonProt / MT)      │
│ 4. P34788 (Spinach / AT): Cross-species upstream discrepancy           │
│ 5. P78007 (MoonProt 1)  : Function-specific linked PMIDs               │
│ 6. P24228 (MoonProt 288): Real parse failure (0 claims, 22 source GO)  │
│                                                                        │
│ Technical Missingness Controls:                                        │
│ 7. A0A0H3CDS3 (KidO)    : Zero QuickGO annotations (annotation gap)    │
│ 8. E6KMA1 (DegP)        : Unlinked accession in DB (protein_id = NULL) │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Detailed Empirical Candidate Profiles

#### 1. `Q42525` (Hexokinase-1 / HXK1, *Arabidopsis thaliana*)
- **Catalog Identity**: `MFP:U:8272bae0e8df8149`
- **Source Presence**: Shared across **three sources**: MoonProt (MPID 359), PlantMP (Order 25, confirmed), MultitaskProtDB-II (Row 524).
- **Source Claims**: 8 extracted claims (canonical glycolytic kinase activity vs moonlighting nuclear glucose-sensing signaling).
- **Source GO Annotations**: 96 annotation rows across 53 distinct GO terms.
- **Source Literature Calibration**:
  - MultitaskProtDB-II cites PMID `12690200` (verified present in QuickGO).
  - MoonProt cites PMID `17081979` (verified present in QuickGO).
  - PlantMP cites `901436` (raw text missing a digit, corresponding to candidate PubMed `9014361` for Jang et al., 1997) and `12690178` (not observed in the inspected `MFP_QuickV1` records). Suspicious PMID `901436` is preserved verbatim in source claims; candidate correction `9014361` remains a separately documented note, NOT an automatic replacement.
  - *Calibrated Claim*: Exactly **2 source PMIDs** (`12690200`, `17081979`) are verified present in `MFP_QuickV1`.
- **QuickGO in `MFP_QuickV1`**: 56 annotation rows across 32 distinct GO terms (33 PMIDs, 23 GO_REFs; 20 distinct PMIDs, 8 distinct GO_REFs; 49 triples).
- **Role in Pilot**: Positive cross-source multi-evidence integration test case.

#### 2. `Q9Y3E5` (Peptidyl-tRNA hydrolase 2 / Bit1, *Homo sapiens*)
- **Catalog Identity**: `MFP:U:c382ca456ad5a4db`
- **Source Presence**: MultitaskProtDB-II (Row 672).
- **Source Claims**: 2 claims (canonical mitochondrial hydrolase vs moonlighting pro-apoptotic nuclear corepressor).
- **Source GO Annotations**: 12 annotations across 12 terms. Uniquely features an explicit source moonlighting Cellular Component term: `GO:0005654` (nucleoplasm).
- **Source Literature**: Cites PMID `14660562` (crystallographic assay) and `15297880`.
- **QuickGO in `MFP_QuickV1`**: 24 annotation rows across 9 distinct GO terms (`database_protein_id = "PTH2_HUMAN"`; 17 PMIDs, 7 GO_REFs; 9 distinct PMIDs, 3 distinct GO_REFs; 17 triples).
- **Concordance Note**: Term `GO:0005654` (nucleoplasm) is **present in source records but not observed in the inspected `MFP_QuickV1` records**, illustrating that source databases capture compartment-specific moonlighting annotations omitted in standard proteomic snapshots.
- **Role in Pilot**: Test case for compartment-specific claims and literature adjudication.

#### 3. `P0AFW0` (Transcriptional regulator RfaH, *Escherichia coli*)
- **Catalog Identity**: `MFP:U:9023923ecdd9d57f`
- **Source Presence**: Shared across MoonProt (MPID 2) and MultitaskProtDB-II (Row 242).
- **Source Claims**: 4 claims (transcriptional elongation antiterminator vs ribosomal recruitment factor).
- **Source GO Annotations**: 21 annotations across 13 distinct terms.
- **Source Literature**: Cites PMID `22817892` (verified present in QuickGO).
- **QuickGO in `MFP_QuickV1`**: 17 annotation rows across 11 distinct GO terms (9 PMIDs, 8 GO_REFs; 5 distinct PMIDs, 3 distinct GO_REFs; 17 triples).
- **Role in Pilot**: Bacterial positive control for dual-role transcriptional regulation.

#### 4. `P34788` (40S ribosomal protein S18, *Spinacia oleracea* / *Arabidopsis thaliana*)
- **Catalog Identity**: `MFP:U:d0cd1a882c7acdf3`
- **Source Presence**: Shared across PlantMP (Order 1, confirmed) and MultitaskProtDB-II (Row 337).
- **Upstream Taxonomic Discrepancy**:
  - Source databases (PlantMP and MultitaskProtDB-II) catalog `P34788` as derived from ***Spinacia oleracea* (Spinach)**.
  - UniProtKB and `MFP_QuickV1` index `P34788` as `RS18_ARATH` from ***Arabidopsis thaliana* (Mouse-ear cress)**.
  - *Scientific Assessment*: This is an **unresolved upstream biological identity issue** originating in the source databases. Technical accession matching (`P34788`) succeeds identically in both systems (`quickgo_coverage_status = "annotations_available"`), but database coverage and biological identity confidence are strictly orthogonal. The record is flagged with `identity_review_status = "flagged_taxonomic_discrepancy"`, preventing automatic biological claim transference between source functional claims and gene-level QuickGO annotations.
- **Source Claims**: 5 claims (structural ribosome component vs transcription factor binding).
- **Source GO Annotations**: 38 annotations across 26 distinct terms.
- **Source Literature**: Cites PMID `7913892` (verified present in QuickGO).
- **QuickGO in `MFP_QuickV1`**: 28 annotation rows across 21 distinct GO terms (17 PMIDs, 11 GO_REFs; 15 distinct PMIDs, 5 distinct GO_REFs; 27 triples). Includes root term annotation `GO:0008150` under evidence `ND`.
- **Role in Pilot**: Audit case for cross-species upstream discrepancies and identity boundaries.

#### 5. `P78007` (L-lactate dehydrogenase / LDH, *Mycoplasmoides pneumoniae*)
- **Catalog Identity**: `MFP:U:44b217c1cc5847ae`
- **Source Presence**: MoonProt (MPID 1).
- **Source Claims**: 2 claims (canonical glycolysis vs moonlighting extracellular fibronectin/heparin-binding cytoadherence).
- **Source GO Annotations**: 10 annotations across 10 terms.
- **Source Literature**: Cites function-specific linked PMID `27616280` on Function 1 (verified present in QuickGO).
- **QuickGO in `MFP_QuickV1`**: 10 annotation rows across 9 distinct terms (3 PMIDs, 7 GO_REFs; 2 distinct PMIDs, 4 distinct GO_REFs; 9 triples).
- **Role in Pilot**: High-concordance bacterial model demonstrating dynamic claim-level citation linkage.

#### 6. `P24228` (Penicillin-binding protein 4 / DacB, *Escherichia coli*)
- **Catalog Identity**: `MFP:U:75a37d1de4bcf985`
- **Source Presence**: MoonProt (MPID 288).
- **Source Claims**: **0 claims** due to upstream HTML syntax defect in raw data (unclosed quote in PDB link), correctly classified in repository coverage as `coverage_status = "parse_failure"`.
- **Source GO Annotations**: 22 protein-level annotations preserved with `claim_id = null`.
- **Source Literature**: None extracted from HTML.
- **QuickGO in `MFP_QuickV1`**: 21 annotation rows across 13 distinct terms (14 PMIDs, 7 GO_REFs; 10 distinct PMIDs, 5 distinct GO_REFs; 18 triples).
- **Role in Pilot**: Decoupled control demonstrating that external QuickGO annotations and protein-level source GO terms can be retrieved and evaluated even when source claim text parsing fails.

#### 7. `A0A0H3CDS3` (Bifunctional regulator KidO, *Caulobacter vibrioides*)
- **Catalog Identity**: `MFP:U:96deffc7f6cd3504`
- **Source Presence**: MultitaskProtDB-II (Row 3). Note: Row 3 was not part of the 20-record Tier A pilot slice; therefore, source annotations are marked `non_evaluable_reason = "source_record_outside_slice"`.
- **QuickGO in `MFP_QuickV1`**: **0 annotation rows** (verified: present in `protein` table as `A0A0H3CDS3_CAUVN`, but 0 rows in `protein_go_term_annotation`).
- **Role in Pilot**: **Technical missingness control for annotation gaps**. Validates that the pipeline handles proteins with zero stored external annotations gracefully, outputting `quickgo_coverage_status = "zero_annotations_found"` without crashing or dropping the protein from denominator accounting.

#### 8. `E6KMA1` (DegP protease, *Mycoplasma*)
- **Catalog Identity**: `MFP:U:03d8d73b0a233958`
- **Source Presence**: MoonProt (MPID 10, present in Tier A pilot slice with 12 source GO annotations).
- **QuickGO in `MFP_QuickV1`**: Present in `accession` table, but **`protein_id IS NULL`** (unlinked in database capture).
- **Role in Pilot**: **Technical missingness control for unlinked database accessions**. Validates that the pipeline marks `quickgo_coverage_status = "unlinked_in_database"` rather than inventing an entity or silently dropping the accession from denominator coverage.

---

## 6. Scientific Operational Definition of Concordance

### 6.1 Comparison Unit and Principal Output Key
To prevent conflation across sources, aspects, and filtering rules, the principal comparison key in Stage P3 is:
$$\mathbf{K} = (\text{accession}, \text{source\_id}, \text{aspect}, \text{policy\_id})$$

- **Cohort Universe**: Evaluated for all 8 cohort accessions across each source database where records exist in `data/interim/pilot/` (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`).
- **Union-of-Sources Aggregation**: An optional accession-level summary across all sources is treated as an explicit, separate aggregation (`source_id = "ALL_SOURCES"`), never mixed into primary source-level rows.
- **Unique Term Sets**: $S$ and $Q$ represent sets of distinct canonical Gene Ontology identifiers (`go_id`, matching `^GO:[0-9]{7}$`) extracted for that accession and aspect under the specified policy.
  - **No Ancestor Expansion**: Comparison is evaluated on exact identifier equality; no DAG term propagation or True Path Rule expansion is performed in P3.
  - **No Semantic Matching or Obsolete Replacement**: Lexical matching only; obsolete terms are not automatically mapped to replacements.

### 6.2 Comparison Metrics and Set Definitions
For each comparison unit $\mathbf{K}$, the following integer counts and set metrics are computed:
- $\text{source\_terms\_count} = |S|$
- $\text{quickgo\_terms\_count} = |Q|$
- $\text{exact\_overlap\_count} = |S \cap Q|$
- $\text{union\_terms\_count} = |S \cup Q|$
- $\text{source\_only\_count} = |S \setminus Q|$
- $\text{quickgo\_only\_count} = |Q \setminus S|$

### 6.3 Evaluability Convention & Empty-Set Behavior
For this pilot, the Jaccard similarity metric $J(S, Q) = \frac{|S \cap Q|}{|S \cup Q|}$ enforces the following mathematical principles, evaluability conditions, and analytical conventions:

1. **Nonempty Disjoint Sets**: When $|S| > 0$ and $|Q| > 0$ with $|S \cap Q| = 0$:
   $$J(S, Q) = 0.0, \quad \text{concordance\_status} = \text{"evaluable"}$$
   Both inventories were observed and evaluated; their term sets share zero elements, representing observed term-level discordance across nonempty sets.

2. **Empty-Set Mathematics and Analytical Convention**:
   - In standard set mathematics:
     - **Exactly one set empty** ($|S| = 0 \text{ and } |Q| > 0$, or $|S| > 0 \text{ and } |Q| = 0$): the ordinary formula yields $\frac{0}{|S \cup Q|} = 0.0$.
     - **Both sets empty** ($|S| = 0 \text{ and } |Q| = 0$): the ordinary formula has a zero denominator ($\frac{0}{0}$), which is mathematically undefined.
   - **Analytical Convention Proposed for this Pilot**: The pilot proposes $J(S, Q) = \text{null}$ whenever either side is empty ($|S| = 0$ or $|Q| = 0$), accompanied by $\text{concordance\_status} = \text{"not\_evaluable"}$. This explicit analytical convention separates **insufficient comparison coverage** (e.g. database unlinking, annotation absence, or elimination via filtering) from **observed disjoint nonempty inventories**. Emitting $0.0$ when an inventory is empty would falsely equate an unobserved or filtered-out record with confirmed functional divergence.

3. **Explicit Evaluability Conditions**:
   A comparison unit $\mathbf{K} = (\text{accession}, \text{source\_id}, \text{aspect}, \text{policy\_id})$ is evaluable (`concordance_status = "evaluable"`) if and only if:
   - **Biological Identity Compatibility**: `identity_review_status == "no_discrepancy_noted"`. If biological identity comparability is unresolved or flagged (e.g. `flagged_taxonomic_discrepancy`), the record is marked `not_evaluable` for biological functional concordance.
   - **Nonempty Comparison Sets**: Both source and external sets contain $\ge 1$ eligible term ($|S| > 0$ and $|Q| > 0$).
   If either condition fails, `concordance_status = "not_evaluable"` and $J(S, Q) = \text{null}$.

4. **Deterministic Handling of Simultaneous Non-Evaluable Reasons**:
   When multiple non-evaluable conditions occur simultaneously, they are handled deterministically without discarding any observed limitation:
   - `primary_non_evaluable_reason`: A single governing diagnostic assigned by strict deterministic precedence:
     1. `unresolved_biological_identity`: Biological discrepancy precludes valid claim comparison, regardless of term counts (e.g. `P34788`).
     2. `source_record_outside_slice`: Accession's source record was omitted from the pilot slice (e.g. `A0A0H3CDS3`).
     3. `external_accession_unlinked`: Accession is unlinked in `MFP_QuickV1` (`protein_id IS NULL`, e.g. `E6KMA1`).
     4. `external_zero_annotations`: Linked protein exists in `MFP_QuickV1`, but contains 0 stored annotations for this aspect.
     5. `source_record_no_go_terms`: Source record exists in pilot slice but contains zero source GO terms for this aspect.
     6. `empty_after_filtering`: Terms were captured initially, but 100% were excluded under Policy C filtering.
   - `secondary_non_evaluable_reasons`: A structured list (or semicolon-delimited string in tabular exports) preserving all other simultaneous conditions (e.g., if a record has both flagged identity and zero source GO terms, `primary` is `unresolved_biological_identity` and `secondary` preserves `source_record_no_go_terms`). No observed limitation is discarded merely because another exists.

5. **Accession `P34788` Decoupling**:
   - Technical accession join succeeds identically in database export (`quickgo_coverage_status = "annotations_available"`, 28 rows, 21 distinct GO terms in `MFP_QuickV1`).
   - `P34788` and all other 7 cohort accessions remain 100% accounted for in denominator coverage.
   - Technical accession-level diagnostics are fully preserved and inspectable.
   - Biological comparability is flagged as unresolved (`identity_review_status = "flagged_taxonomic_discrepancy"`) because source databases cite *Spinacia oleracea* while UniProtKB/QuickGO indexes *Arabidopsis thaliana* (RS18_ARATH). Automatic biological claim transference and identity-compatible concordance evaluation remain blocked.

---

## 7. Multi-Stage Data Architecture & Contract Specifications

### 7.1 Multi-Stage Progression
The pilot separates raw ingestion, normalization, and comparative analytics into four decoupled stages:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PILOT DATA ARCHITECTURE                         │
├────────────────────────────────────────────────────────────────────────┤
│ STAGE A: DATABASE EXPORT (Raw DB Extraction — COMPLETED IN P2)         │
│ Fixtures: tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv     │
│           tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv        │
│ Manifest: tests/fixtures/quickgo_pilot/manifest.json                   │
│                                                                        │
│ STAGE B: CATALOG MAPPING & NORMALIZATION (Offline Logic — PROPOSED P3) │
│ Input:  Stage A raw fixtures + candidate v0.3.0 entity mapping         │
│ Logic:  src/mfp_bibliography/quickgo_concordance.py                    │
│                                                                        │
│ STAGE C: VALIDATED ANNOTATION RECORDS (Contract Storage — PROPOSED P3) │
│ Output: data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv │
│ Schema: data/curated/external_quickgo_annotations.schema.json          │
│                                                                        │
│ STAGE D: COVERAGE AND CONCORDANCE OUTPUTS (Analytics — PROPOSED P3)    │
│ Output: data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv    │
│         data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv │
│         data/interim/pilot/quickgo_slice/manifest.json                 │
└────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Field Provenance Across Contracts

| Contract | Field Name | Provenance Category | Derivation Description |
|---|---|---|---|
| **Raw Annotations (A)** | `database_annotation_id` | Direct Database Export | `protein_go_term_annotation.id` (database row PK for tracing) |
| **Raw Annotations (A)** | `accession` | Direct Database Export | `accession.code` |
| **Raw Annotations (A)** | `database_protein_id` | Direct Database Export | `protein.id` |
| **Raw Annotations (A)** | `go_id` | Direct Database Export | `protein_go_term_annotation.go_id` |
| **Raw Annotations (A)** | `raw_category` | Direct Database Export | `go_terms.category` |
| **Raw Annotations (A)** | `evidence_code` | Direct Database Export | `protein_go_term_annotation.evidence_code` (2 or 3 uppercase letters) |
| **Raw Annotations (A)** | `publication_id` | Direct Database Export | `protein_go_term_annotation.publication_id` (emitted as empty string `""` when null) |
| **Raw Coverage (A)** | `accession` | Cohort Query Input | Cohort input accession code |
| **Raw Coverage (A)** | `database_protein_id` | SQL LEFT JOIN Result | `protein.id` (emitted as empty string `""` when unlinked or absent) |
| **Raw Coverage (A)** | `quickgo_coverage_status` | CASE Logic on Counts | 5-way status: `annotations_available`, `zero_annotations_found`, `unlinked_in_database`, `absent_from_database`, `ambiguous_identity` |
| **Raw Coverage (A)** | `identity_review_status` | Pilot Review Setting | Explicit flag: `flagged_taxonomic_discrepancy` (P34788) vs `no_discrepancy_noted` |
| **Raw Coverage (A)** | `stored_annotation_rows` | SQL COUNT(pga.id) | Count of actual annotation rows in `protein_go_term_annotation` |
| **Raw Coverage (A)** | `distinct_go_terms` | SQL COUNT(DISTINCT) | Count of distinct GO terms in `protein_go_term_annotation` |
| **Raw Coverage (A)** | `notes` | CASE Diagnostic Text | Diagnostic narrative notes (emitted as empty string `""` when null) |
| **Annotation (C - Proposed)** | `annotation_id` | Deterministic Identifier | `MFP:QGA:<capture_id>:<database_annotation_id>` (unambiguous serialization binding capture scope to preserved database integer row PK) |
| **Annotation (C - Proposed)** | `protein_id` | Catalog Lookup | Catalog entity ID (`MFP:U:[0-9a-f]{16}`) via `mfp_proteins.csv` |
| **Annotation (C - Proposed)** | `uniprot_accession` | Mapped / Normalized | Canonical accession matching input cohort |
| **Annotation (C - Proposed)** | `database_protein_id` | Retained from Raw | Traced from raw export |
| **Annotation (C - Proposed)** | `database_annotation_id`| Retained from Raw | Database row primary key from raw export |
| **Annotation (C - Proposed)** | `capture_id` | Pipeline Constant | Identifier of database capture: `"MFP_QuickV1_20261112"` |
| **Annotation (C - Proposed)** | `go_id` | Retained from Raw | Validated `^GO:[0-9]{7}$` |
| **Annotation (C - Proposed)** | `go_aspect` | Normalized Vocabulary | Normalized from `raw_category` (`BP`, `MF`, `CC`) |
| **Annotation (C - Proposed)** | `evidence_code` | Retained from Raw | Standard code matching `^[A-Z]{2,3}$` |
| **Annotation (C - Proposed)** | `reference_type` | Classified Namespace | `pmid`, `go_ref`, or `null` |
| **Annotation (C - Proposed)** | `reference_id` | Preserved Raw String | Numeric string, `GO_REF` CURIE, or null |
| **Annotation (C - Proposed)** | `qualifier_status` | Policy Setting | Fixed neutral setting: `"not_captured"` |
| **Annotation (C - Proposed)** | `assigned_by` | Uncaptured Attribute | Explicit schema null (CSV empty string `""`) |
| **Annotation (C - Proposed)** | `source_database` | Constant Origin | `"MFP_QuickV1"` |
| **Coverage (D - Proposed)** | `accession` | Retained from Raw | Input cohort accession |
| **Coverage (D - Proposed)** | `protein_id` | Catalog Lookup | Catalog entity ID or null if uncataloged |
| **Coverage (D - Proposed)** | `database_protein_id` | Retained from Raw | Database protein ID or null if unlinked |
| **Coverage (D - Proposed)** | `quickgo_coverage_status` | Retained from Raw | 5-way coverage status |
| **Coverage (D - Proposed)** | `identity_review_status` | Retained from Raw | `flagged_taxonomic_discrepancy` vs `no_discrepancy_noted` |
| **Coverage (D - Proposed)** | `stored_annotation_rows` | Retained from Raw | Total annotation rows in fixture |
| **Coverage (D - Proposed)** | `distinct_go_terms` | Retained from Raw | Total distinct GO terms in fixture |
| **Concordance (D - Proposed)**| `concordance_id` | Deterministic Key | `MFP:CONC:<accession>:<protein_id>:<source_id>:<aspect>:<policy_id>` (full comparison key without truncation) |
| **Concordance (D - Proposed)**| `policy_id` | Analytical Dimension | `"captured_inventory_overlap"` or `"filtered_descriptive_overlap"` |
| **Concordance (D - Proposed)**| `exact_overlap_count` | Set Intersection | $|S \cap Q|$ |
| **Concordance (D - Proposed)**| `union_terms_count` | Set Union | $|S \cup Q|$ |
| **Concordance (D - Proposed)**| `jaccard_similarity` | Set Calculation | $|S \cap Q| / |S \cup Q|$ or null if non-evaluable |
| **Concordance (D - Proposed)**| `concordance_status` | Evaluability Setting | `"evaluable"` or `"not_evaluable"` |
| **Concordance (D - Proposed)**| `primary_non_evaluable_reason` | Governing Diagnostic | Primary reason code assigned by strict deterministic precedence |
| **Concordance (D - Proposed)**| `secondary_non_evaluable_reasons` | Preserved Diagnostics | Semicolon-delimited list of all simultaneous observed limitations |
| **Concordance (D - Proposed)**| `identity_review_status` | Propagated Flag | Preserved from coverage to guard interpretation |

### 7.3 CSV Representation versus JSON Schema Contracts
$$\text{CSV empty field (\texttt{""})} \xrightarrow{\text{loader conversion (\texttt{parse\_csv\_value})}} \text{Python \texttt{None} / JSON \texttt{null}} \xrightarrow{\text{schema validation}} \text{Passes } \{\text{"type": ["string", "null"]}\}$$
- In CSV output files, JSON `null` is serialized as an **empty field (`""`)**, never the literal string `"null"` or `"None"`.
- Literal string tokens such as `"null"` or `"None"` in a CSV field remain strings and fail pattern validation.
- Loaders parse empty string fields as Python `None` / JSON `null` before schema validation.

---

## 8. Proposed Stage P3 Policy Specifications

The following unified policy table defines the concrete proposed configuration for Stage P3 implementation, submitted for human review:

### 8.1 Unified P3 Policy Table

| Policy Dimension | Proposed Setting / Identifier | Operational Definition & Rule | Exclusion & Aggregation Mechanics | Evidence Caveat & Boundary |
|---|---|---|---|---|
| **A. Complete Inventory** | `policy_id = "complete_inventory"` | Preserve every captured annotation row from `raw_quickgo_annotations.csv`. Normalization must not delete, collapse, or drop observations. | Normalized rows map 1:1 to raw fixture rows (156 raw rows $\to$ 156 normalized annotation rows). Distinct database row IDs preserved intact. Deduplication occurs ONLY when constructing comparison sets. | Preserves provenance and observation multiplicity; establishes no biological assertions. Missing source evidence codes are never invented. |
| **B. Captured-Identifier Comparison** | `policy_id = "captured_inventory_overlap"` | Unfiltered descriptive overlap view over captured GO identifiers between source records ($S$) and QuickGO ($Q$). | Deduplication collapses repeated rows to unique `go_id` set per $(accession, source, aspect)$ before set operations. | Labelled as **inventory overlap**, NOT agreement of verified positive functional assertions. |
| **C. Filtered Descriptive Comparison** | `policy_id = "filtered_descriptive_overlap"` | Filtered descriptive view excluding: (1) Annotations with evidence code `ND`; (2) Annotations to root terms `GO:0008150`, `GO:0003674`, `GO:0005575`. | ND and root filters operate as separate orthogonal rules: (1) Root filter excludes root terms by term ID unconditionally; (2) ND filter excludes annotation rows with evidence code `ND`. A non-root term survives if $\ge 1$ eligible non-ND row retains it for that protein and aspect. Distinct exclusion counts tracked. | Distinct rules with separate exclusion tracking. Not an experimental-only partition. |
| **D. Experimental-Code Sensitivity** | *Deferred Extension* (`policy_id = "experimental_only_extension"`) | Restricted to 6 legacy experimental codes (`EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`). Deferred as an optional subsequent extension because it is outside minimum Stage P3 scope. | The 6 legacy experimental codes are already captured as 3-letter strings in the raw fixture and require no external ontology crosswalk to filter. However, to keep Stage P3 bounded and focused on descriptive inventory overlap, this extension is deferred and is neither authorized nor implemented in Stage P3. | Evaluates curated literature support independently from electronic inferences (`IEA`, `IBA`). Not authorized or implemented in Stage P3. |
| **E. Qualifier Polarity Policy** | `qualifier_status = "not_captured"` | Fixed neutral status reflecting that `qualifier` was not stored in `MFP_QuickV1`. | All QuickGO annotations emit `not_captured`. No positive or negative polarity inferred. | Must NOT override reviewed negative annotations (`NOT`) or infer absence of function. |

### 8.2 Identity and Reference Policies
1. **Identity Policy**:
   - `identity_review_status` is propagated intact across all coverage and concordance outputs.
   - For `P34788`: Inventory data is preserved and technical accession diagnostics are permitted, but biological comparability is marked unresolved (`flagged_taxonomic_discrepancy`). It is excluded from summaries restricted to identity-compatible comparisons.
   - `no_discrepancy_noted` indicates absence of detected discrepancy, NOT independently validated identity.
   - Split / multiple-entity mappings: if encountered, halt the affected comparison rather than making an arbitrary assignment.
2. **Reference Policy**:
   - Reference type (`pmid`, `go_ref`, `null`) is strictly orthogonal to evidence code (`IDA`, `IEA`, `ND`, etc.).
   - `GO_REF` CURIEs are not equated with computational evidence; PMIDs are not equated with experimental evidence.
   - Protein-level reference intersection ($|R_{src} \cap R_{qgo}|$) measures shared literature citations; it does **NOT** prove claim-level functional support.
   - Suspicious source PMIDs (e.g. `901436`) are preserved verbatim; suggested corrections remain separately documented notes.

---

## 9. Stage P3 Input Fixtures, Identifiers, and Reproducibility

### 9.1 Required Frozen Input Paths and Checksums

| Input Artifact Description | Exact Repository File Path | Verified SHA-256 Digest |
|---|---|---|
| **Frozen QuickGO Annotations** | `tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv` | `b8d508f6f980fb3aed676dae7c4d3275b188dcbe58438372280920e6cf704f6a` |
| **Frozen QuickGO Coverage** | `tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv` | `249a4cd91117fec229cdaf9c579803dcb89d011e41ec2e5bf0eb0fb35eb8aef1` |
| **Frozen QuickGO Manifest** | `tests/fixtures/quickgo_pilot/manifest.json` | Recorded in fixture directory |
| **Tier A Functional Claims** | `data/interim/pilot/functional_claims_pilot.csv` | `88a1f2521d5d69b70dbd3af11d2191589289bb22feb23a349611d1a563993348` |
| **Tier A Source GO Annotations** | `data/interim/pilot/source_go_annotations_pilot.csv` | `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda` |
| **Tier A Functional Coverage** | `data/interim/pilot/functional_coverage_pilot.csv` | `c29d28712c613211c6183f49ef304a63d94dd64a40de2ff682641037e2573e8d` |
| **Tier A Pilot Manifest** | `data/interim/pilot/manifest.json` | `c6ecaed0306bfb2029427842e4b6b2e223a8b539f34990a05e87ac781a60bf5b` |
| **Candidate Entity Mapping** | `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv` | `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc` |

### 9.2 Deterministic Identifier Scheme
- Normalized QuickGO annotations receive deterministic IDs:
  $$\text{annotation\_id} = \text{"MFP:QGA:"} + \text{capture\_id} + \text{":"} + \text{database\_annotation\_id}$$
  where `capture_id = "MFP_QuickV1_20261112"` and `database_annotation_id` is the preserved integer primary key string from `protein_go_term_annotation.id`.
- Concordance records receive full comparison keys without protein_id truncation:
  $$\text{concordance\_id} = \text{"MFP:CONC:"} + \text{accession} + \text{":"} + (\text{protein\_id} \text{ if present else "UNMAPPED"}) + \text{":"} + \text{source\_id} + \text{":"} + \text{aspect} + \text{":"} + \text{policy\_id}$$

### 9.3 Input Provisioning and Fresh-Clone Reproducibility
The frozen raw inputs (`tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv`, `raw_quickgo_coverage.csv`, `manifest.json`) are currently present locally in the working directory.
- **Fresh Clone Boundary**: In a clean checkout from remote origin, these files are not reproducible without an explicit provisioning step: either committing the frozen fixtures directly to Git (authorizing their persistence), or re-running `scripts/export_quickgo_pilot_fixtures.py` against a local running instance of `MFP_QuickV1`.
- **Implementation Boundary**: Execution of Stage P3 additionally requires prior authoring and approval of implementation schemas (`external_quickgo_annotations.schema.json`, `quickgo_coverage.schema.json`, `quickgo_concordance.schema.json`) and the concordance calculation engine (`quickgo_concordance.py`).
- Therefore, readiness claims must not assert "no technical blockers" without explicitly noting that fixture commitment to Git and contract authoring are necessary prerequisites.

---

## 10. Proposed Stage P3 Deliverables and Acceptance Criteria

### 10.1 Proposed Stage P3 Implementation Files (Not Created in this Turn)
> [!IMPORTANT]
> No P3 files may be created now. The following list defines the planned deliverables for a separately authorized Stage P3 increment:

- Schemas (Contracts for all normalized outputs):
  - `data/curated/external_quickgo_annotations.schema.json` (Contract for `quickgo_annotations_pilot.csv`, enforcing 1:1 mapping with raw fixture rows, `annotation_id` serialization, and neutral qualifier status)
  - `data/curated/quickgo_coverage.schema.json` (Contract for normalized `quickgo_coverage_pilot.csv`, defining field compatibility with raw coverage: adds catalog `protein_id`, retains 5-way coverage status, identity review status, counts, and notes)
  - `data/curated/quickgo_concordance.schema.json` (Contract for `quickgo_concordance_pilot.csv`, defining full comparison keys, evaluability status, primary and secondary reason diagnostics, set counts, and Jaccard similarity)
- Source Code & CLI:
  - `src/mfp_bibliography/quickgo_concordance.py`
  - `scripts/build_quickgo_concordance_pilot.py`
- Tests & Synthetic Fixtures:
  - `tests/test_quickgo_concordance.py`
  - `tests/fixtures/quickgo_concordance/`

### 10.2 Stage P3 Acceptance Tests
1. **Disjoint Nonempty Sets**: Evaluates to $J(S, Q) = 0.0$ with `concordance_status = "evaluable"`.
2. **Empty / Filtered-Empty Sets**: Evaluates to $J(S, Q) = \text{null}$ with explicit `primary_non_evaluable_reason` and `secondary_non_evaluable_reasons`.
3. **Independent Filtering Rules**: ND exclusion and root-term exclusion operate as distinct rules with separate tracking; non-root terms survive if supported by $\ge 1$ eligible non-ND row.
4. **Term Retention via Disjunctive Support**: A term supported by both an ND annotation and a non-ND annotation is retained under Policy C.
5. **Taxonomic Discrepancy Flagging**: `P34788` retains `identity_review_status = "flagged_taxonomic_discrepancy"`, decoupling technical accession join from biological comparability.
6. **Two-Letter Evidence Code Support**: Evidence codes `ND` and `IC` pass schema and pipeline validation.
7. **Complete Denominator Accounting**: Exactly 8 cohort accessions accounted for across coverage and concordance.
8. **100% Offline Execution**: Zero dependencies on live databases or external APIs once fixtures are provisioned.
9. **Release Candidate Protection**: Candidate v0.3.0 baseline verification passes before and after execution.

---

## 11. Governance Alignment & Required Decisions

Connecting `mfp-bibliography` with external QuickGO data from `MFP_QuickV1` is an exploratory pilot requiring three formal governance gates:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        REQUIRED DECISION GATES                         │
├────────────────────────────────────────────────────────────────────────┤
│ GATE 1: REPOSITORY GOVERNANCE AUTHORIZATION                            │
│ Authorize Phase D0 exploratory pilot connecting source records with     │
│ local MFP_QuickV1 snapshot.                                            │
│                                                                        │
│ GATE 2: SCIENTIFIC POLICY RATIFICATION                                 │
│ Approve unified P3 policy table (Policies A–E): complete inventory,   │
│ unfiltered overlap, filtered comparison (ND & root exclusions),        │
│ deferred experimental sensitivity, and neutral qualifier policy.       │
│                                                                        │
│ GATE 3: PIPELINE IMPLEMENTATION AUTHORIZATION                          │
│ Authorize implementation of Stage P3 schemas, adapter, and CLI.        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Code Locations & Verified SQL Export Queries

### 12.1 Code References
- Exporter Script: [`scripts/export_quickgo_pilot_fixtures.py`](../../scripts/export_quickgo_pilot_fixtures.py)
- Validator Module: [`src/mfp_bibliography/quickgo_raw_validator.py`](../../src/mfp_bibliography/quickgo_raw_validator.py)
- Contract Tests: [`tests/test_quickgo_raw_contracts.py`](../../tests/test_quickgo_raw_contracts.py)
- Frozen Fixtures: [`tests/fixtures/quickgo_pilot/`](../../tests/fixtures/quickgo_pilot/)

### 12.2 Verified Read-Only Export Queries

```sql
-- Query A: Raw Annotations Export (inner joins, actual rows only)
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;

\copy (SELECT pga.id AS database_annotation_id, a.code AS accession, p.id AS database_protein_id, pga.go_id, gt.category AS raw_category, pga.evidence_code, pga.publication_id FROM (VALUES ('Q42525'), ('Q9Y3E5'), ('P0AFW0'), ('P34788'), ('P78007'), ('P24228'), ('A0A0H3CDS3'), ('E6KMA1')) AS cohort(accession) JOIN accession a ON a.code = cohort.accession JOIN protein p ON a.protein_id = p.id JOIN protein_go_term_annotation pga ON pga.protein_id = p.id JOIN go_terms gt ON pga.go_id = gt.go_id ORDER BY a.code, gt.category, pga.go_id, pga.evidence_code, pga.publication_id, pga.id) TO 'raw_quickgo_annotations.csv' WITH CSV HEADER;

-- Query B: Raw Denominator Coverage Export (left joins, all 8 cohort members retained)
\copy (SELECT cohort.accession, p.id AS database_protein_id, CASE WHEN a.code IS NULL THEN 'absent_from_database' WHEN a.protein_id IS NULL THEN 'unlinked_in_database' WHEN COUNT(pga.id) = 0 THEN 'zero_annotations_found' ELSE 'annotations_available' END AS quickgo_coverage_status, CASE WHEN cohort.accession = 'P34788' THEN 'flagged_taxonomic_discrepancy' ELSE 'no_discrepancy_noted' END AS identity_review_status, COUNT(pga.id) AS stored_annotation_rows, COUNT(DISTINCT pga.go_id) AS distinct_go_terms, CASE WHEN cohort.accession = 'P34788' THEN 'PlantMP/Multitask cite Spinacia oleracea; UniProt/QuickGO indexes RS18_ARATH from Arabidopsis thaliana; technical accession join succeeds but biological identity remains an unresolved upstream issue' WHEN cohort.accession = 'E6KMA1' THEN 'Accession present in accession table but unlinked (protein_id IS NULL)' WHEN cohort.accession = 'A0A0H3CDS3' THEN 'Linked protein found in protein table but zero annotations stored in protein_go_term_annotation' ELSE NULL END AS notes FROM (VALUES ('Q42525'), ('Q9Y3E5'), ('P0AFW0'), ('P34788'), ('P78007'), ('P24228'), ('A0A0H3CDS3'), ('E6KMA1')) AS cohort(accession) LEFT JOIN accession a ON a.code = cohort.accession LEFT JOIN protein p ON a.protein_id = p.id LEFT JOIN protein_go_term_annotation pga ON pga.protein_id = p.id GROUP BY cohort.accession, a.code, a.protein_id, p.id ORDER BY cohort.accession) TO 'raw_quickgo_coverage.csv' WITH CSV HEADER;

COMMIT;
```
