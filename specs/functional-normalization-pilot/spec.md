# Specification: Source-Grounded Functional Normalization Pilot

- **Specification ID**: `SPEC-001-FUNCTIONAL-NORMALIZATION-PILOT`
- **Status**: Draft for human review
- **Implementation Authorization**: **Not granted** (awaits human sign-off on ADR-008 Level 2)
- **Target Repository**: `mfp-bibliography`
- **Owner**: Scientific Software Architect & Data Architect
- **Related Documents**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md), [ADR-004](../../docs/decisions/ADR-004-evidence-label-benchmark-separation.md), [ADR-005](../../docs/decisions/ADR-005-deterministic-protein-ids.md), [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), `docs/source-claims-contract.md`.

---

## 1. Objective and Scientific Rationale

### 1.1 Objective
Design and specify an auditable, deterministic, and multiplicity-preserving representation for functional statements extracted from the repository's five raw source databases (`MoonDB`, `MoonProt`, `MultifacetedProtDB`, `MultitaskProtDB-II`, `PlantMP`).

The primary purpose of this pilot increment is **faithful source preservation and structured claim extraction (Tier A)**, strictly decoupled from downstream semantic distance calculations, contextual triplet synthesis, and classifier modeling.

### 1.2 Epistemological Distinctions
To avoid scientific conflation, this specification establishes an explicit six-level distinction:

1. **Original Source Statement**: Verbatim raw text or field value extracted directly from an immutable raw artifact without alteration or interpretation (e.g. `MoonProt Function 1: Glyceraldehyde-3-phosphate dehydrogenase`, `PlantMP canonical_function_bp: photosynthesis`).
2. **Normalized Claim Record**: A structured, repository-internal record representing one functional role observation, carrying deterministic identifiers, extraction locators, and operational review status.
3. **Proposed Mapping**: A rule-based, dictionary, or curated crosswalk connecting a source statement to a standardized biological concept (e.g. mapping EC `1.2.1.12` to `GO:0004365`).
4. **External GO Annotation**: An independent assertion retrieved from QuickGO/GOA containing Gene Ontology term ID, aspect, evidence code, qualifier, and attribution metadata.
5. **Evidence Statement**: Literature citation (PMID, DOI), author statement, or curation record supporting a specific claim.
6. **Human Curation Decision**: An authoritative, signed, and versioned judgment adjudicating claim validity, resolving ambiguities, or approving ground-truth seeds.

> [!IMPORTANT]
> **Multiplicity vs Biological Function**: Extracting $N$ claim statements for a protein does **NOT** prove that the protein possesses $N$ distinct biological functions. Different sources may describe the same biochemical activity using different phrasing, or one source may list sub-processes of a single pathway. Claim segmentation, cross-source deduplication, and functional equivalence are distinct policies that require explicit human definition.

---

## 2. Source Facts, Parser Assets, and Planning Assumptions

To prevent assumptions from overriding repository facts, this section summarizes the empirical realities of each source based on targeted read-only inspection of raw files and existing parser code.

### 2.1 Dimensional Analysis of Source Characteristics

We explicitly distinguish three orthogonal axes:
- **Axis A (Extraction & Preservation Difficulty)**: Structural complexity of parsing raw fields and preserving provenance locators.
- **Axis B (GO Reconciliation & Curation Difficulty)**: Semantic effort needed to map free text to ontology terms or evaluate evidence.
- **Axis C (High-Evidence Eligibility)**: Likelihood that records meet strict experimental standards for an eventual curated gold standard.

These three axes must **never** be collapsed into a single "normalization difficulty" score.

```
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│ Source               │ Axis A (Extraction)  │ Axis B (GO Reconcil.)│ Axis C (Eligibility) │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ MultitaskProtDB-II   │ Low (Clean CSV)      │ Low (GO terms exist) │ Moderate (Lit. mix)  │
│ PlantMP              │ Low (Pre-split CSV)  │ Low (GO terms exist) │ High (Curated subset)│
│ MoonProt             │ Moderate (HTML blocks│ Moderate (Text + EC) │ High (Curated PMIDs) │
│ MoonDB               │ Moderate (TSV split) │ Moderate (Free text) │ Moderate (Cur/EMF)   │
│ MultifacetedProtDB   │ Low (Literal JSON)   │ N/A (No GO or text)  │ Zero (Accession-only)│
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

### 2.2 Source-by-Source Empirical Baseline

#### 1. MultitaskProtDB-II (`SRC_MULTITASKPROTDB_II`)
- **Observed Structure & Fields**: Tabular CSV (`data/raw/multitaskprotdb-ii/proteins.csv`, 694 rows), 15 columns: `UniProt`, `Protein_Name`, `Long_Description`, `Canonical_Function`, `GO`, `Moonlighting_function`, `GO_Moon`, `Organism`, `Human_Disease`, `Drugs`, `Induction`, `PDBs`, `PDB_UniProt`, `Models`, `Reference`.
- **Existing Reusable Parser**: `src/mfp_bibliography/multitaskprotdb_ii_records.py`.
- **Claim Segmentation**: Pre-segmented into canonical (`Canonical_Function`) and moonlighting (`Moonlighting_function`).
- **Reference Granularity**: Single record-level `Reference` column (usually a numeric PMID like `24681012`; occasionally non-numeric text like OMIM/PDB).
- **Explicit GO Identifiers**: Yes. In `GO`, multiline text with explicit aspects (`C:`, `F:`, `P:`), GO IDs, and evidence codes (`IEA:...`). In `GO_Moon`, multiline text with GO IDs and aspect names (`biological_process`, etc.).
- **Source-Native Role Labels**: `Canonical_Function` and `Moonlighting_function`.
- **Missing Information**: Lacks per-function reference linkage; references apply at record level.
- **Proposed Pilot Capability Exercised**: Baseline extraction of tabular pre-segmented roles, multi-line GO parsing with native aspects, and record-level reference preservation.
- **Inspection Scope & Uncertainty**: 694 rows. Non-PMID references (e.g. text notes) must be handled gracefully without conversion to numeric nulls.

#### 2. PlantMP (`SRC_PLANTMP`)
- **Observed Structure & Fields**: Tabular CSV (`data/raw/plantmp/PlantMP_all.csv`, 112 rows), 14 columns: `order`, `protein name, gene`, `uniport_id` (typo in raw header), `canonical_function_bp`, `canonical_function_mf`, `moonlighting_function_bp`, `moonlighting_function_mf`, `go_canonical_bp`, `go_canonical_mf`, `go_moonlighting_bp`, `go_moonlighting_mf`, `plant_species`, `pubmed_id`, `type`.
- **Existing Reusable Parser**: `src/mfp_bibliography/plantmp_claims.py`.
- **Claim Segmentation**: Highly partitioned by role (`canonical` vs `moonlighting`) and by aspect (`bp` vs `mf`).
- **Reference Granularity**: Single `pubmed_id` at record level. Per source publication, this citation documents the moonlighting function.
- **Explicit GO Identifiers**: Yes, formatted with prefixes (e.g. `BP 0042254, 0006412`, `MF 0003729`). No cellular component (CC) terms are provided in the raw table.
- **Source-Native Role Labels**: `canonical` vs `moonlighting`.
- **Source Status Labels**: `type` (`confirmed`, `likely`, `predicted`).
- **Missing Information**: No cellular components; canonical functions lack independent citations.
- **Proposed Pilot Capability Exercised**: Ingestion of role-and-aspect partitioned tabular statements; status-tier separation (`confirmed` vs `predicted`).
- **Inspection Scope & Uncertainty**: 112 rows. Citation assignment must be verified against PlantMP documentation.

#### 3. MoonProt (`SRC_MOONPROT`)
- **Observed Structure & Fields**: Semi-structured HTML files (`data/raw/moonprot/mpid_*.html`, 702 acquired files), parsed into `MoonProtRecord` and `MoonProtFunctionDetail`.
- **Existing Reusable Parser**: `src/mfp_bibliography/moonprot_parser.py`.
- **Claim Segmentation**: Dynamically partitioned into $K$ function blocks (`functions[0]`, `functions[1]`, etc., each with description, PMIDs, EC number, cellular location).
- **Reference Granularity**: Per-function PMIDs (`function.pmids` tuple).
- **Explicit GO Identifiers**: `raw_go_terms` in header, but not partitioned by function block.
- **Source-Native Role Labels**: `Function 1`, `Function 2`, etc. (unranked numbered functions).
- **Missing Information**: GO terms are record-level, unlinked to individual function blocks.
- **Proposed Pilot Capability Exercised**: Ingestion of dynamic $K$-block functional structures and function-specific literature references.
- **Inspection Scope & Uncertainty**: 702 files. Variation in function count ($K \ge 2$) requires robust dynamic array extraction.

#### 4. MoonDB (`SRC_MOONDB`)
- **Observed Structure & Fields**: Tabular TSVs:
  - `all_manual_curated.tsv`: `UniprotAC`, `Function_1_text`, `Function_2_text`, `Publications`, `Species`.
  - `all_EMF_annotation.tsv`: `UniprotKB_AC`, `UniprotKB_ID`, `GO_ID_1`, `GO_Name_1`, `GO_ID_2`, `GO_ID_Name`, probabilities, `Species`.
  - `all_emf_and_curated.tsv`: `#UniProtKB_ac`, `type` (`Curated` vs `Predicted`).
- **Existing Reusable Parser**: `src/mfp_bibliography/moondb_claims.py`.
- **Claim Segmentation**:
  - Curated: `Function_1_text` and `Function_2_text` (free text with condition clauses).
  - EMF: Predicted pairs of GO terms (`GO_ID_1` vs `GO_ID_2`).
- **Reference Granularity**: Comma-separated PMIDs in `Publications` at row grain.
- **Explicit GO Identifiers**: None in manual curated TSV; explicit in EMF TSV.
- **Source-Native Role Labels**: `Function_1` vs `Function_2`.
- **Source Status Labels**: `Curated` vs `Predicted`.
- **Missing Information**: Curated TSV lacks structured GO terms; compartment mentions are embedded in free text.
- **Proposed Pilot Capability Exercised**: Distinguishing algorithmic predictions (EMF) from manual curation; extracting free-text statements.
- **Inspection Scope & Uncertainty**: 351 curated rows, large EMF prediction table.

#### 5. MultifacetedProtDB (`SRC_MULTIFACETEDPROTDB`) — Critical Discrepancy Resolution
- **Observed Structure & Fields**: Single-quoted Python-literal structure (`MultifacetedProtDB_data.json`, 1,103 records), fields: `uniprot`, `name`, `genes`, `annotation`.
- **Existing Reusable Parser**: `src/mfp_bibliography/multifacetedprotdb_records.py`.
- **Empirical Resolution of the "Annotation" Discrepancy**:
  - The audit report and early drafts incorrectly hypothesized that `annotation` was an unsegmented functional text string.
  - **Empirical Fact**: In `MultifacetedProtDB_data.json`, `annotation` is a **numeric float** (e.g. `5.0`, `4.0`, `3.0`, `2.0`), reflecting an annotation score or confidence metric.
  - **Scientific Ruling**: Numeric scores are metadata, **NOT** functional claims. MultifacetedProtDB contains **no discrete functional statements, no GO identifiers, and no literature citations**.
- **Claim Segmentation**: None.
- **Reference Granularity**: None.
- **Explicit GO Identifiers**: None.
- **Source-Native Role Labels**: None.
- **Proposed Pilot Capability Exercised**: **Coverage boundary accounting for records without functional statements**. The pipeline must account for these records with `claim_status = "no_discrete_functional_statements"`, preserving `annotation_raw` as metadata without inventing functional claims.
- **Inspection Scope & Uncertainty**: 1,103 records. Semantic meaning of the numeric score remains undocumented in source files.

---

## 3. Scope and Stratified Requirements

### 3.1 Three-Tier Requirement Stratification

```
[Tier A: Source Claim Preservation] ──► FOCUS OF THIS SPECIFICATION (Pilot Increment)
  └─ Multi-claim extraction, verbatim text, source-record linkage,
     provenance locators, explicit missingness, offline fixtures.
       │
[Tier B: GO Reconciliation & Crosswalk] ──► POST-PILOT INCREMENT (Phase D0/D)
  └─ Pinned go-basic.obo, EC-to-GO mapping, bidirectional QuickGO crosswalk,
     quarantine of negated annotations (NOT qualifiers).
       │
[Tier C: Metric Engine & Experimental Blocks] ──► DEFERRED (Blocks B1–B6)
  └─ Semantic similarity (Wang, MBL, Lin), contextual triplet synthesis,
     NPMI co-annotation association, BioData reference matching.
```

### 3.2 In Scope for the Pilot Specification (Tier A)
- Specifying a relational (one-to-many) functional claim schema (`functional_claims`).
- Specifying a coverage accounting schema (`functional_coverage`).
- Preserving all claims without collapsing into artificial binary slots.
- Explicit tracking of predicted vs curated claims (e.g. MoonDB EMF predictions vs manual curation).
- Preserving source-native references only at the level supported by the source (record-level vs claim-level).
- Explicit accounting for accession-only and incomplete entries.

### 3.3 Explicit Out-of-Scope Items
- No semantic similarity or divergence calculations (deferred to Block B3).
- No contextual triplet construction $\tau = (m, b, c)$ (deferred until DEC-22 defines triplet semantics).
- No automated assignment of cellular compartments from protein co-annotation.
- No live connections to external databases (`TargetData`, `BioData`, `MFPUniProtData`).
- No modifications to the verified catalog baseline (`mfp_catalog_mvp`) or release candidate v0.3.0.

---

## 4. Detailed Functional Requirements (Tier A)

### 4.1 Requirement R-NORM-01: Multiplicity-Preserving Relational Structure
- **Requirement**: Each functional statement observed for a protein must generate a distinct `functional_claim` record linked by foreign key `protein_id` to `mfp_proteins.csv` and by `source_record_id` to `mfp_source_records.csv`.
- **Prohibition**: The implementation must **NEVER** use fixed binary slots (`BP1/MF1/CC1` vs `BP2/MF2/CC2`). Proteins with 1, 2, 3, or more claims must all be represented without data loss or truncation.

### 4.2 Requirement R-NORM-02: Verbatim Text and Provenance Locators
- **Requirement**: Every claim record must capture:
  - `claim_id`: Deterministic identifier under scheme `MFPB_FUNCTIONAL_CLAIM_V1` (`MFP:FC:<source>:<16hex>`).
  - `protein_id`: Canonical protein identifier (`MFP:U:<16hex>` or `MFP:F:<src>:<16hex>`).
  - `source_record_id`: Native source record key.
  - `raw_claim_field`: Name of the source field from which the claim was extracted (e.g. `canonical_function_bp`, `Function_1_text`, `functions[0].description`).
  - `raw_claim_value`: Exact, untranslated verbatim text of the claim.
  - `raw_file_path`: Path to the raw source file in the repository.
  - `raw_row_or_url`: Stable locator within the artifact (row number, line number, or URL).
  - `extraction_method`: Transformation identifier (e.g. `extract_plantmp_claims_v1`).

### 4.3 Requirement R-NORM-03: Reference Granularity Preservation
- **Requirement**: Bibliographic references (PMIDs/DOIs) must only be attached to a functional claim if the raw source explicitly links the reference directly to that specific function.
- **Rule**: If a source provides references only at the source-record level (e.g. MultitaskProtDB-II's general `Reference` column), the references must remain stored as record-level provenance. They must **NOT** be promoted to function-specific evidence statements without external curation.

### 4.4 Requirement R-NORM-04: Predicted vs Curated Assertion Tracking
- **Requirement**: The operational status of each claim must explicitly preserve the source's curation tier:
  - `curated`: Supported by manual literature curation or explicit experimental evidence in the source.
  - `predicted`: Generated by computational algorithms or sequence predictions (e.g. MoonDB EMF predictions, PlantMP predicted subset).
  - `unresolved`: Unclear, disputed, or conflicting source status.
- **Rule**: Computational predictions must never be silently upgraded to `curated` or `resolved`.

### 4.5 Requirement R-NORM-05: Source-Explicit GO vs Proposed Mappings
- **Requirement**: Distinguish Gene Ontology identifiers explicitly provided by the source from candidate GO mappings proposed by repository pipelines:
  - `source_go_id`: GO ID present verbatim in the source file.
  - `source_go_aspect`: GO aspect indicated by the source (if any: BP, MF, CC).
  - `proposed_go_id`: Candidate GO ID mapped via external crosswalks (e.g. EC-to-GO), null if unmapped.
  - `mapping_confidence`: Category indicating mapping lineage (`source_explicit`, `ec_exact_xref`, `unmapped`).

### 4.6 Requirement R-NORM-06: Strict Prohibition of Co-annotation Compartment Inference
- **Requirement**: No Cellular Component (GO-CC) term may be linked to a functional claim based solely on the fact that the term is co-annotated to the same protein in a database.
- **Enforcement**: Any pipeline or adapter that automatically populates a claim's compartment from general protein-level annotations without specific functional linkage is strictly non-compliant.

### 4.7 Requirement R-NORM-07: Explicit Accounting of Incomplete & Accession-Only Cases
- **Requirement**: Proteins lacking explicit functional claims in a source (such as MultifacetedProtDB records or accession-only entries) must remain explicitly accounted for in a dedicated `functional_coverage` table with `claim_status = "no_discrete_functional_statements"`. They must never be silently omitted from denominators, nor may fake claims be fabricated to represent them.

---

## 5. Candidate Data Contracts: `functional_claims` and `functional_coverage`

### 5.1 Data Contract: `functional_claims`
Emitted for records possessing discrete functional statements.

| Field Name | Type | Nullable | Cardinality / Delimiter | Description | Example |
|---|---|---|---|---|---|
| `claim_id` | string | No | Scalar | Deterministic unique key (`MFPB_FUNCTIONAL_CLAIM_V1`). | `MFP:FC:MULTITASK:a1b2c3d4e5f60718` |
| `protein_id` | string | No | Scalar | Foreign key to `mfp_proteins.csv`. | `MFP:U:P04406` |
| `source_id` | string | No | Scalar | Canonical source catalog identifier. | `SRC_MULTITASKPROTDB_II` |
| `source_record_id` | string | No | Scalar | Foreign key to `mfp_source_records.csv`. | `multitaskprotdb_ii_row_1` |
| `claim_index` | integer | No | Scalar | Zero-based index of the claim within the source record. | `0` |
| `claim_role_raw` | string | Yes | Scalar | Verbatim role declared by source (`Canonical_Function`, `Moonlighting_function`, etc.). | `Canonical_Function` |
| `raw_claim_field` | string | No | Scalar | Exact name of the raw field extracted. | `Canonical_Function` |
| `raw_claim_value` | string | No | Scalar | Exact verbatim claim text. | `Ribosomal protein` |
| `claim_assertion_type` | string | No | Scalar | Controlled vocabulary: `curated`, `predicted`, `unresolved`. | `curated` |
| `source_go_ids` | string | Yes | Semicolon-delimited | GO IDs explicitly provided in raw source row for this claim. | `GO:0005840; GO:0003735` |
| `source_go_aspects` | string | Yes | Semicolon-delimited | Aspects indicated by source matching `source_go_ids` order. | `CC; MF` |
| `source_ec_number` | string | Yes | Scalar | EC number explicitly provided in raw source row. | `1.2.1.12` |
| `linked_reference_ids` | string | Yes | Semicolon-delimited | References explicitly tied by the source to this specific claim. | `PMID:11111111` |
| `record_reference_ids` | string | Yes | Semicolon-delimited | Record-level references provided by the source, unlinked to this claim. | `PMID:24681012` |
| `raw_file_path` | string | No | Scalar | Relative path to immutable raw artifact. | `data/raw/multitaskprotdb-ii/proteins.csv` |
| `raw_row_or_url` | string | No | Scalar | Row number, line index, or URL locator. | `row:2` |
| `extraction_method` | string | No | Scalar | Identifier of the extraction parser and version. | `extract_multitask_claims_v0.1` |
| `claim_status` | string | No | Scalar | `valid`, `unsegmented_text`, `incomplete`, `ambiguous`. | `valid` |
| `notes` | string | Yes | Free text | Technical parser notes. | `Record carries multiline embedded aspects` |

### 5.2 Data Contract: `functional_coverage`
Emitted for every source record in the catalog to ensure complete denominator accounting.

| Field Name | Type | Nullable | Description | Example |
|---|---|---|---|---|
| `source_record_id` | string | No | Foreign key to `mfp_source_records.csv`. | `multifacetedprotdb_row_1` |
| `protein_id` | string | No | Foreign key to `mfp_proteins.csv`. | `MFP:U:P36873` |
| `source_id` | string | No | Source catalog identifier. | `SRC_MULTIFACETEDPROTDB` |
| `claims_extracted_count` | integer | No | Number of rows generated in `functional_claims`. | `0` |
| `coverage_status` | string | No | `claims_extracted`, `no_discrete_functional_statements`, `unresolved_identity`, `parse_failure`. | `no_discrete_functional_statements` |
| `metadata_annotation_raw` | string | Yes | Verbatim raw annotation metadata (e.g. float score `5.0`). | `5.0` |
| `notes` | string | Yes | Accounting notes. | `Accession-only record; score preserved as metadata` |

### 5.3 Serialization and Sorting Invariants
- **Character Encoding**: UTF-8 without BOM; LF (`\n`) line endings.
- **Null Serialization and Absence Representation**:
  - In in-memory and JSON representations, absence of value is explicitly represented by `null`. String fields enforce `minLength: 1`, making empty strings (`""`) invalid values to prevent ambiguous representation.
  - In RFC 4180 CSV serialization, `null` values serialize to empty string (`""`).
  - In CSV deserialization to validated record objects, empty string cells (`""`) in nullable columns must be converted to `None` / `null`, while non-nullable fields containing empty strings fail validation.
- **Delimiter and Multivalue Encoding**:
  - Comma (`,`) is the column delimiter for CSV.
  - Semicolon followed by a space (`; `) is the delimiter for multivalue fields (`source_go_ids`, `source_go_aspects`, `linked_reference_ids`, `record_reference_ids`).
  - Original reference strings and raw identifiers must be preserved without modification. Multivalue decoding splits on `;` and strips whitespace, preserving verbatim identifier strings without ad-hoc percent-encoding.
- **Deterministic Total Ordering**:
  - **`functional_claims` Total Tie-Breaking Key**: Records must be deterministically sorted by:
    1. `protein_id` ASC
    2. `source_id` ASC
    3. `source_record_id` ASC
    4. `claim_index` ASC
    5. `claim_id` ASC
    This 5-tuple provides an unambiguous total order even when a source database provides multiple distinct records for the same protein entity.
  - **`functional_coverage` Total Order Key**: Records must be deterministically sorted by:
    1. `protein_id` ASC
    2. `source_id` ASC
    3. `source_record_id` ASC
- **Round-Trip Fidelity**: String values containing commas, quotes, or newlines must be quoted under RFC 4180 rules. Parsing and re-serialization must preserve complete field equivalence.
- **Deterministic Claim Identifier Derivation**:
  - Claim IDs follow scheme `MFPB_FUNCTIONAL_CLAIM_V1`: `MFP:FC:<source_suffix>:<16hex_digest>`.
  - The 16-hex digest is computed via SHA-256 over canonical namespace, source identity, source record locator, claim index, and raw claim field:
    `SHA-256("MFPB_FUNCTIONAL_CLAIM_V1::<source_id>::<source_record_id>::<claim_index>::<raw_claim_field>")[:16]`.
  - Uniqueness is verified across the dataset, and any digest collision must raise a hard validation error.

---

## 6. Integration of the Normalized Protein Dossier Proposal

The proposal to render a **Normalized Protein Dossier** in an IDE/VS Code inspection panel is a valuable downstream visualization tool. To ensure it aids curation without distorting repository architecture, the dossier is formalized as a **read-only downstream inspection view**, strictly decoupled from Tier A preservation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      NORMALIZED PROTEIN DOSSIER                        │
│                   (Downstream Inspection View)                         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Identity & Provenance (UniprotKB, Canonical Name, Taxon, Merges)   │
│ 2. Extracted Claims (All discrete source statements, unflattened)      │
│ 3. Bibliographic Ledger (Record-level vs Claim-linked citations)       │
│ 4. External GO Crosswalk (Retrieved annotations, evidence codes, NOTs) │
│ 5. Downstream Evaluation Eligibility Flags:                            │
│    ├─ Tier A Preservation: PASSED (Source statements intact)           │
│    ├─ GO Reconciliation: PENDING (Phase D0/D crosswalk)                │
│    ├─ Contextual Triplet: DEFERRED (Open Decision DEC-22)              │
│    └─ Golden Standard Profile: PENDING (Requires 100% experimental EXP)│
└────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Architectural Rules for Dossier Integration
1. **Inspection View, Not Ingestion Pivot**: The dossier consumes normalized records; it does not replace raw claim extraction or tabular normalization.
2. **Four Orthogonal Eligibility Flags**:
   - `preservation_valid`: Claim correctly reflects raw source statement with complete provenance (Tier A).
   - `go_reconciliation_eligible`: Statements possess explicit or validated GO mappings (Tier B).
   - `contextual_triplet_candidate`: Functions possess documented compartment and process linkages (Tier C).
   - `high_evidence_profile_eligible`: Statements supported by direct peer-reviewed experimental assays (candidate "Golden Standard" filter).
3. **No Prerequisite Blocking**: Missing taxonomy, sequence hashes, or external GO annotations must **never** block Tier A claim preservation.
4. **Preservation of Raw Multiplicity**: The dossier renders all $K$ extracted claims individually. It must never force them into a binary "Function 1 / Function 2" layout unless the source explicitly labels them as such.
5. **Candidate Golden Standard Status**: Strict acceptance criteria (e.g. experimental-only literature, verified structural domains) represent a candidate filter for future curation subsets, **not** an entry requirement for pilot normalization.

---

## 7. Acceptance Criteria for Future Pilot Implementation

1. **AC-NORM-01 (Multiplicity Invariant)**: Ingesting a source record with $K$ discrete functional blocks produces exactly $K$ rows in `functional_claims`.
2. **AC-NORM-02 (Zero Fabrication on Accession-Only Sources)**: MultifacetedProtDB records generate 0 fake functional claims, but appear in `functional_coverage` with `coverage_status = "no_discrete_functional_statements"` and `metadata_annotation_raw = "5.0"`.
3. **AC-NORM-03 (No Fabricated GO Identifiers)**: No GO ID appears in `source_go_ids` that is not present in the raw input file.
4. **AC-NORM-04 (Provenance Completeness)**: 100% of generated claim records carry valid, resolvable `protein_id` and `source_record_id` keys matching the catalog candidate.
5. **AC-NORM-05 (Deterministic Reproduction)**: Successive executions over identical inputs yield byte-identical outputs across different environments and hash seeds.
6. **AC-NORM-06 (Baseline Preservation)**: Verification command `python scripts/package_catalog_candidate.py --verify-package` passes before and after running the normalization pipeline, proving catalog isolation.
