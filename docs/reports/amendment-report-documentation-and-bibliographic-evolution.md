# Technical Amendment Report: Calibrated Documentation Architecture, Epistemic Decoupling, and Non-Blocking Annotation Governance

## Document Control & Review Metadata

| Attribute | Audit & Amendment Record |
|---|---|
| **Document Title** | Technical Amendment Report: Calibrated Documentation Architecture, Epistemic Decoupling, and Non-Blocking Annotation Governance |
| **Document ID** | `REP-AMEND-DOC-BIB-2026-11-10-REV2` |
| **Document Location** | [`docs/reports/amendment-report-documentation-and-bibliographic-evolution.md`](docs/reports/amendment-report-documentation-and-bibliographic-evolution.md) |
| **Revision Cycle** | Revision 2 (Post-audit calibration: calibrated evidence levels, reassessed F-03, policy-dependent projections, refined polarity, decoupled increments) |
| **Review Authority** | Senior Scientific-Software Architect, Documentation Auditor & Bioinformatics Data-Provenance Reviewer |
| **Target Repository** | `mfp-bibliography` |
| **Target Document Reviewed** | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) (`PROP-EVOLUTION-2026-11-10`) |
| **Review Date** | 2026-11-10 |
| **Governing Rules** | [`AGENTS.md`](AGENTS.md), [ADR-001](docs/decisions/ADR-001-repository-scope.md) through [ADR-007](docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](docs/decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Operational State** | Static read-only inspection; zero modifications to source code, schemas, or raw data; single authorized write: this amendment report. |

---

## 1. Verified Baseline and Inspection Limitations

### 1.1 Verified Repository Identification and Isolation

To prevent architectural conflation across distinct workspaces on this machine:
- **Active Inspected Repository**: `mfp-bibliography` (workspace root `/home/alexdoro/repositories/mfp-bibliography`).
- **Distinct Adjacent Repositories** (located at `/home/alexdoro/repositories/` but **NOT** interchangeable with `mfp-bibliography`):
  * `BioData`: PostgreSQL 16 relational storage, custom dumps, and table schemas.
  * `protein-information-system` (PIS): Ingestion daemons, RabbitMQ consumers, and SQLAlchemy ORM extractors (`QuickGOAnnotationExtractor`, `UniProtExtractor`).
  * `mfp-dataset-designer`: Dataset cohort builders, negative control samplers, and GO semantic similarity calculators.
  * `protein-embedding-classifier` (PEC): Machine learning pipelines, protein language model embeddings, and classification benchmarks.
- **Architectural Scope Boundary**: Under accepted [ADR-001](docs/decisions/ADR-001-repository-scope.md), `mfp-bibliography` is strictly dedicated to cataloging, source evidence preservation, raw provenance tracking, and bibliographic foundation. It does **NOT** build ML models, train classifiers, construct negative control sets, or maintain live database daemons.

### 1.2 Git State, Branch, HEAD, and Working-Tree Discrepancies

- **Active Branch**: `feature/functional-normalization` (tracking `origin/feature/functional-normalization`).
- **HEAD Commit**: `a6def6fef01f345f38532d30779d5b576b079580` (`Add functional tests for MultitaskProtDB-II claims and coverage schemas`, 2026-11-06 20:04:28 +0100).
- **Tracked Working-Tree Modifications (11 files)**:
  1. `data/curated/functional_coverage.schema.json`: Added nullability for `protein_id` when `coverage_status == "unresolved_identity"`.
  2. `specs/functional-normalization-pilot/plan.md`: Updated Stage P2 Multitask and Stage P3 PlantMP adapter statuses.
  3. `specs/functional-normalization-pilot/spec.md`: Refined dimensional analysis, schema nullability rules, and 6 epistemological levels.
  4. `specs/functional-normalization-pilot/tasks.md`: Marked TASK-01, TASK-02, TASK-03, and TASK-04 completed; retaining unauthorization for subsequent tasks.
  5. `specs/functional-normalization-pilot/verification.md`: Logged checks DOC-CHK-01..06, Multitask slice verification, and PlantMP adapter test logs.
  6. `src/mfp_bibliography/functional_claims_multitask.py`: Core MultitaskProtDB-II adapter parsing GO annotations, references, and total ordering.
  7. `tests/fixtures/functional_claims_multitask/README.md`: Fixture documentation for real and synthetic extracts.
  8. `tests/fixtures/functional_claims_multitask/multitask_real_extract.csv`: 6-record slice extract from raw `proteins.csv`.
  9. `tests/fixtures/functional_claims_multitask/multitask_synthetic_edge_cases.csv`: Edge-case fixture for unlinked annotations and parsing errors.
  10. `tests/test_functional_claims_multitask.py`: Unit and regression test suite for Multitask adapter.
  11. `tests/test_functional_contracts.py`: Contract tests updated to validate null `protein_id` handling for unresolved coverage rows.
- **Untracked Working-Tree Files (11 entries)**:
  1. `data/curated/source_go_annotations.schema.json`: Formal Draft 2020-12 schema for source-explicit GO annotations.
  2. `docs/audits/documentation-audit-2026-11-09.md`: Comprehensive documentation audit report.
  3. `docs/curation/`: Directory containing `Q9Y3E5_contextual_adjudication_dossier.md` (`DOSSIER-Q9Y3E5-001`).
  4. `docs/reports/multitask-six-record-context-readiness-review.md`: Review report `REV-MULTITASK-6REC-001`.
  5. `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`: The evolution proposal (`PROP-EVOLUTION-2026-11-10`).
  6. `scripts/build_multitask_slice.py`: Standalone CLI building the 6-record Multitask interim slice.
  7. `src/mfp_bibliography/functional_claims_plantmp.py`: PlantMP tabular claim and annotation adapter.
  8. `tests/fixtures/functional_claims_plantmp/`: Real and synthetic fixtures for PlantMP.
  9. `tests/test_build_multitask_slice.py`: Integration test verifying `scripts/build_multitask_slice.py`.
  10. `tests/test_functional_claims_plantmp.py`: Test suite (39 passing tests) for PlantMP adapter.
  11. `tests/test_source_go_annotations_contract.py`: Contract test suite (43 passing tests) for source GO annotations.

### 1.3 Calibrated Authorization Status of Untracked PlantMP Work

In the initial proposal, untracked PlantMP files were classified as "unauthorized". This finding is now calibrated:
- **Inspected Evidence**: Proposed [ADR-008](docs/decisions/ADR-008-functional-normalization-pilot-scope.md) formally remains in `Status: Proposed` (Level 6) in Git. However, `specs/functional-normalization-pilot/tasks.md#L7-L8` was updated in the working tree to record:
  > *"Scoped authorization granted exclusively for **TASK-01, TASK-02, TASK-03, and TASK-04**. Subsequent tasks (TASK-05 to TASK-08) remain strictly unauthorized."*
- **Audit Ruling**: Because formal project management approval external to Git history was not inspectable, the project-level authorization status of TASK-04 is classified as **unknown / unestablished from in-repo governance files**, rather than assumed to be illicit.

### 1.4 Inspection Limitations & Unverified External Artifacts

1. **BioData PostgreSQL Database Dump**: The physical dump file `data/snapshots/biodata_mfp_snapshot_20261014.dump` (5,031,619 bytes, SHA-256 `be5dec2e...`) is **NOT** tracked in Git and is absent from the local workspace filesystem. Its tracked manifest exists at `releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json`. The live PostgreSQL service was not accessed or queried.
2. **Historical BioData Counts**: The reported counts (96,186 annotations, 2,182 proteins, 40,669 rows with `publication_id IS NULL`, 22 evidence code frequencies) are **historical documented values** from the 2026-10-14 snapshot manifest and Catalan audits (`MFP_DATA_AUDITABILITY_MATRIX.md`, `MFP_EXTRACTION_UNIFICATION_AUDIT.md`). They are not verified current live database counts.
3. **Primary Literature Full Texts**: The 20 PDF files in `docs/bibliography/` are untracked local reference copies. No automated PDF text-mining, programmatic extraction, or external network requests were executed.

---

## 2. Existing Strengths to Preserve

The `mfp-bibliography` repository possesses several architectural assets that must be safeguarded during any evolution:

1. **Deterministic, Collisions-Free Protein Identity ([ADR-005](docs/decisions/ADR-005-deterministic-protein-ids.md))**:
   The `MFPB_PROTEIN_ID_V1` hashing protocol (`MFP:U:<16hex>` and fallback `MFP:F:<src>:<16hex>`) completely eliminates salted runtime hash collisions and establishes byte-reproducible entity identifiers across independent environments.
2. **Raw Data Immutability & Verifiable Manifests ([ADR-002](docs/decisions/ADR-002-raw-data-immutability.md), [ADR-003](docs/decisions/ADR-003-provenance-and-transformations.md))**:
   Raw source artifacts under `data/raw/` are strictly append-only, checksummed in `data/manifests/source_manifest.csv`, and protected from in-place edits. Pre-build gates (`raw_input_verification.py`) verify input integrity before builds.
3. **Decoupled Baseline Catalog Release Candidate (`v0.3.0`)**:
   The candidate package at `releases/mfp-catalog-candidate-v0.3.0/` covers 2,962 source records, 2,322 protein entities, and 463 exact-UniProt merges. Offline verification via `python3 scripts/package_catalog_candidate.py --verify-package` passes 100% offline without network, database, or uncommitted files.
4. **Relational Claim and Coverage Architecture**:
   The relational model in [`specs/functional-normalization-pilot/spec.md`](specs/functional-normalization-pilot/spec.md) preserves biological multiplicity without collapsing statements into rigid binary slots (`BP1/MF1/CC1` vs `BP2/MF2/CC2`), while `functional_coverage` guarantees complete denominator accounting.
5. **Decoupling of Bibliographic Relations from Catalog Baseline ([ADR-007](docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md))**:
   ADR-007 correctly ensured that the baseline five-source catalog (`mfp_catalog_v1`) would not be held hostage to pending bibliographic work, while defining four precise prerequisite conditions for post-v1 integration.

---

## 3. Calibrated Findings and Disputed Findings Ledger

To ensure scientific rigor, findings are calibrated across four distinct evidence levels:
- **Level I: Schema Omission**: An attribute is absent from a JSON schema or data contract.
- **Level II: Verified Transformation Behavior**: Code inspection of an adapter or extractor demonstrates that an attribute is dropped or altered during execution.
- **Level III: Demonstrated Historical Record Impact**: An inspected historical artifact or audit report proves that specific records were affected.
- **Level IV: Quantified Population Impact**: Measurement across the entire population proves the exact proportion of affected entities.

### Disputed Findings Ledger (5-Part Calibration Structure)

#### Finding F-01: Bibliographic Curation Conflated with Ingestion (The Universal Bottleneck Risk)
- **Claim**: Requiring local bibliographic curation as a gating dependency for external GO annotation ingestion halts functional enrichment and co-annotation exploration.
- **Inspected Evidence**:
  * [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md#L308-L335`](docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md#L308-L335) framed Phase D0 relations as an entry requirement for enriched profiles.
  * Accepted [ADR-007](docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) lines 18–35 deferred bibliographic work precisely because requiring verified article-to-GO relations would block catalog stabilization.
- **Inference**: Treating local literature adjudication as a prerequisite for ingesting or exploring external annotations turns human curation bandwidth into a universal system bottleneck.
- **Remaining Uncertainty**: The exact performance overhead of managing unreviewed external annotations alongside curated subsets.
- **Verification Needed**: Propose the **Non-Blocking Preservation Principle** and separate data products (Product A: Source Inventory vs Product B: Analytical Views vs Product C: Locally Curated Subset).
- **Classification**: `Proposed improvement` (Architectural Rule).

#### Finding F-02: Overly Rigid Disqualification of Dataset-Methodology Publications
- **Claim**: A publication describing a dataset can never serve as experimental evidence for individual protein claims.
- **Inspected Evidence**:
  * [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md#L286-L290`](docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md#L286-L290) stated Chen et al. (2021) is *"NEVER experimental evidence for individual protein claims"*.
  * Scientific literature inspection indicates that dataset-methodology papers often include novel wet-lab assays, crystal structures, or characterizations of specific proteins in their results sections.
- **Inference**: While Chen et al. (2021) must not be blanket-promoted to all 702 MoonProt proteins, categorically disqualifying any paper that describes a dataset from providing claim-level support is an artificial taxonomic rule that contradicts empirical science.
- **Remaining Uncertainty**: Whether Chen et al. (2021) specifically contains original experimental assays for any individual MoonProt accession.
- **Verification Needed**: Amend proposal wording to require assessing support from the actual relevant content of the publication rather than disqualifying it by publication type.
- **Classification**: `Documentation ambiguity`.

#### Finding F-03: Reassessed Status of `claim_assertion_type`
- **Claim**: The existing schema field `claim_assertion_type = curated/predicted/unresolved` actively collapses all epistemic dimensions across the repository.
- **Inspected Evidence**:
  * [`data/curated/functional_claims.schema.json#L71-L79`](data/curated/functional_claims.schema.json#L71-L79) defines `claim_assertion_type` with 3 enum values.
  * Code grep across `src/` and `scripts/` reveals that `functional_claims_multitask.py#L270` sets `"claim_assertion_type": "curated"`, but **zero downstream consumers** use this field as a universal truth label or conflate it with local review completion or documentary availability.
- **Inference**: The field description in the schema (*"Normalized curation tier of the functional assertion"*) is ambiguous, but no existing code currently misuses it to override evidence codes or local review.
- **Remaining Uncertainty**: How future Phase D0 schemas should represent source curation vs local review without unnecessary complexity.
- **Verification Needed**: Reclassify F-03 from a verified implementation issue to a proposed contract extension. Keep the eight dimensions conceptually decoupled without requiring eight duplicated fields on every row.
- **Classification**: `Proposed contract extension` / `Documentation ambiguity`.

#### Finding F-05: GAF Attribute Loss and Qualifier Handling
- **Claim**: Historical QuickGO extractors dropped qualifiers, converting negative experimental findings (`NOT`) into positive functional assertions in BioData.
- **Inspected Evidence**:
  * *Schema Omission (Level I)*: [`data/curated/source_go_annotations.schema.json#L8-L23`](data/curated/source_go_annotations.schema.json#L8-L23) lacks `qualifier`, `with_from`, `assigned_by`, `date`, and `annotation_extensions`.
  * *Verified Transformation Behavior (Level II)*: PIS `QuickGOAnnotationExtractor` source code does not extract the `qualifier` field from QuickGO REST API responses.
  * *Demonstrated Historical Impact (Level III)*: `docs/audits/MFP_DATA_AUDITABILITY_MATRIX.md#L67-L78` records that QuickGO annotations with `NOT` qualifiers were saved without negation indicators in BioData's `protein_go_term_annotation` table.
- **Inference**: Storing annotations without qualifiers makes negative evidence indistinguishable from positive assertions at the database level.
- **Remaining Uncertainty (Level IV)*: We do not know how many of the 96,186 annotations in that historical snapshot actually had an upstream `NOT` qualifier, nor has it been demonstrated that a specific downstream query in `mfp-dataset-designer` or `PEC` actually generated a false-positive biological assertion from an upstream `NOT` row.
- **Verification Needed**: Re-query QuickGO for the snapshot accessions or inspect raw API dumps to quantify the exact population impact of negative qualifiers.
- **Classification**: `Verified transformation behavior` (historical extractor) & `Schema omission` (source_go_annotations).

#### Finding F-06: Historical BioData Null Publication Links
- **Claim**: All 40,669 rows with `publication_id IS NULL` in BioData were caused by the database schema rejecting non-PMID references.
- **Inspected Evidence**:
  * *Demonstrated Historical Impact (Level III)*: `releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json` reports 96,186 annotations and 40,669 null publications.
  * *Verified Transformation Behavior (Level II)*: BioData's `publication_id` column was an integer foreign key to a PMID table. PIS `QuickGOAnnotationExtractor` discarded non-numeric reference strings (such as `GO_REF:0000024`), setting `publication_id` to `NULL`.
- **Inference**: Rejection of non-numeric references by an integer column contributed directly to the high volume of null publication links.
- **Remaining Uncertainty (Level IV)*: We **cannot attribute all 40,669 null links** to non-PMID reference truncation without reconciliation evidence. A significant fraction of annotations in QuickGO/GOA (e.g. certain computational inferences) legitimately carry no publication link upstream.
- **Verification Needed**: Execute an empirical cross-tabulation on a restored snapshot instance to determine the exact proportion of non-PMID truncation versus upstream unreferenced annotations.
- **Classification**: `Verified transformation behavior` (extractor) & `Requires empirical verification` (population breakdown).

#### Finding F-10: Mojibake Duplicate Semantic Equivalence
- **Claim**: `docs/roadmap/core/experiment_guio_v1.md` is an exact duplicate of `docs/roadmap/core/experiment_definition.md` containing only encoding corruption.
- **Inspected Evidence**:
  * Both files contain exactly 874 lines.
  * Character-level comparison shows 292 lines with encoding differences (e.g. `â€”` vs `—`, `terminologÃ­a` vs `terminología`).
  * Normalizing UTF-8/Latin-1 double-encoding replacements for punctuation and Spanish accents reduces remaining differences to 40 lines.
  * All 40 remaining lines are double-encoded en-dashes (`â€“` vs `–`) in headings and table rows.
- **Inference**: `experiment_guio_v1.md` contains **zero unique scientific or technical content** compared to `experiment_definition.md`.
- **Remaining Uncertainty**: None regarding textual content; procedural question remains whether maintainers prefer deletion or archival quarantine.
- **Verification Needed**: Document this empirical proof in the recovery map before executing disposal.
- **Classification**: `Verified implementation issue` (Lossless duplicate).

---

## 4. Change Matrix: Evolution Proposal Amendments

The table below specifies exact amendments to the proposal document [`PROP-EVOLUTION-2026-11-10`](docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md):

| Target Section | Current Proposal Text / Behavior | Problem & Scientific Flaw | Proposed Replacement & Architectural Rule | Scientific Rationale | Implementation Impact |
|---|---|---|---|---|---|
| **Executive Summary & §B.2** | Frames bibliographic curation as a gating prerequisite for annotation enrichment. | Creates a universal bottleneck; blocks exploratory ingestion of external GO terms. | Formulate the **Non-Blocking Preservation Principle**: lack of local literature review does not prevent ingesting, indexing, or querying external annotations. | Decouples data ingestion throughput from manual curation bandwidth while maintaining strict provenance. | Governance text adjustment; no schema code changes. |
| **§D.2** | Asserts dataset publications are *"NEVER experimental evidence for individual protein claims"*. | Overly rigid; ignores that dataset papers often include novel wet-lab assays in results/tables. | Clarify that a publication cannot be permanently classified as incapable of support solely because it describes a dataset; support depends on actual relevant content. | Ensures empirical truth governs claim evaluation rather than publication taxonomies. | Documentation adjustment in §D.2 and §F.1. |
| **§D.1 & §E.4** | Collapses status into single enums (`curated`, `predicted`, `unresolved`). | Conflates source curation tier, local review completion, documentary availability, and biological evidence code. | Propose a **conceptually decoupled model**: Assign rights/access to documentary artifacts, reviews to review events, eligibility to analytical policies, and provenance/evidence to annotation occurrences. | Enables independent filtering without duplicating eight fields on every annotation row. | Informs future Phase D0 schema design; leaves active schemas intact. |
| **§D.3** | Mentions negation briefly without addressing polarity-aware views. | Under-specifies handling of GO `NOT` qualifiers; risks either dropping `NOT` or excluding it from all analyses. | Formalize explicit rules: `NOT` qualifiers must be preserved with `qualifier = "NOT"` and `is_negative = true`. Exclude `NOT` from positive-association aggregations, but preserve it for polarity-aware analyses. Unknown polarity must not silently enter positive views. | Eliminates false-positive risk while enabling negative-evidence research. | Enforces schema validation rules for future Phase D0 tables. |
| **§D.1** | Unclear distinction between raw source dumps, analytical views, and curated sets. | Risk of analytical filters mutating raw inventory or confusing curated subsets with baseline catalog. | Formally define **three distinct data products**: Product A (Source Inventory), Product B (Analytical Views), and Product C (Locally Curated Subset). Map `MFP_CuratedData` as Product C. | Prevents contamination of raw inventories by analytical assumptions while providing clean reproducibility. | Clarifies directory and artifact boundaries (`data/raw/`, `data/processed/`, `data/curated/`). |
| **§D.1 & §F.1** | Implies `(protein, GO, evidence)` or publication handle is sufficient identity. | Collapses distinct annotations from different providers, dates, or secondary references; drops `GO_REF`. | Treat `(protein, GO, evidence)` as a useful projection, not an identity. Adopt stable occurrence identifiers and typed references (`pmid`, `doi`, `go_ref`, `db_xref`, `methodology_resource`). Support multiple identifiers denoting the same reference without inflating evidence counts. | Preserves distinct provenance chains without conflating multiple handles for the same paper into multiple evidence pieces. | Extends future Phase D0 schema design; no change to catalog baseline. |
| **§D.2 & §E.1** | Mentions avoiding Cartesian triplets but lacks formal three-tier separation. | Leaves room for ad-hoc heuristic linkage of MF and CC co-annotations as functional compartments. | Explicitly separate: (A) Co-annotation (set overlap), (B) Candidate Contextual Relation (hypothesis), and (C) Curated Contextual Relation (verified). Forbid Cartesian product triplet generation. Recognize valid partial observations (MF-only). | Enforces [`AGENTS.md`](AGENTS.md) §5 invariant 2; avoids combinatorial explosion ($M \times B \times C$). | Reaffirms contextual synthesis boundary outside current pilot. |
| **§G.1** | Lacks formal experiment manifest specification; promises absolute byte-identical reproduction. | Absolute byte guarantees across unpinned environments are unmaintainable; adding new reviews risks mutating historical cohorts. | Propose a formal **Experiment Manifest** pinning dataset snapshots, ontology releases, review commits, policy digests, and exclusion denominators. Require verifiable determinism for explicitly deterministic artifacts. | Guarantees auditable reproducibility for downstream studies. | Specifies manifest format for future analytical scripts. |
| **§A.2** | Labeled untracked PlantMP files as conclusively "unauthorized". | Overlooked working-tree update in `specs/functional-normalization-pilot/tasks.md` recording TASK-04 completion. | Reclassify authorization status of untracked PlantMP files as **unknown / pending formal baseline reconciliation**. | Preserves auditing objectivity and avoids unfounded compliance claims. | Wording correction in Section A. |

---

## 5. Proposed Epistemic and Product Separation

### 5.1 Conceptual Epistemic Decoupling Without Row-Level Field Duplication

Rather than burdening every row of every table with eight redundant columns, the architecture decouples epistemic dimensions by assigning them to their natural structural entities:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      NATURAL STRUCTURAL ASSIGNMENT                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. DOCUMENTARY ARTIFACTS  │ Rights & Accessibility (public_abstract, CC-BY,    │
│    (Publication Record)   │ restricted). Fair use is a legal defense, NOT a     │
│                           │ granted license or permission.                      │
├───────────────────────────┼─────────────────────────────────────────────────────┤
│ 2. ANNOTATION OCCURRENCE  │ Provenance (source, record_id, locator, method),   │
│    (source_go_annotations)│ Evidence Type (IDA, IEA, ECO), Polarity (NOT, pos) │
├───────────────────────────┼─────────────────────────────────────────────────────┤
│ 3. REVIEW EVENTS          │ Local Review Workflow (not_reviewed, in_progress,   │
│    (Adjudication Ledger)  │ reviewed), Scientific Assessment (supported,        │
│                           │ contradicted, insufficient_evidence, not_assessable)│
├───────────────────────────┼─────────────────────────────────────────────────────┤
│ 4. EXPERIMENT MANIFESTS   │ Analytical Eligibility (policy-dependent selection, │
│    (Analytical Views)     │ inclusion filters, versioned ontology release)      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Key Epistemic Distinctions
1. **Not Yet Assessed vs Assessed but Not Assessable**:
   - `not_reviewed`: The curator has not evaluated the material.
   - `not_assessable`: The curator has reviewed the accessible material (e.g. an abstract), but the documentary evidence is insufficient to evaluate biological validity.
2. **Policy-Dependent Projections**:
   - Multiple annotation occurrences for the same protein, GO term, and evidence code are **NOT** automatically merged into a single row, nor are citations blindly unioned.
   - Projections are governed by explicit analytical policies (e.g. an occurrence-counting view preserves duplicates; a non-redundant set view collapses them while retaining occurrence audit links).
3. **No Global "Disputed" Status**:
   - Conflicting review events do not overwrite an annotation's global status to "disputed".
   - Each review event is an immutable historical record ($T_1, T_2$). The analytical policy defines how an experiment treats conflicting reviews (e.g. conservative exclusion, latest review, or dispute quarantine).

### 5.2 The Three Decoupled Data Products

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ PRODUCT A: SOURCE INVENTORY                                                     │
│ • Role: Preserves all upstream observations, source records, and external       │
│   annotations (including IEA, raw text statements, and uncurated claims).       │
│ • Governance: Ingestion requires technical schema validity, but strictly        │
│   DOES NOT require local literature review. Preservation is not endorsement.    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ PRODUCT B: ANALYTICAL VIEWS                                                     │
│ • Role: Reproducible selections and transformations for specific research goals.│
│ • Governance: Governed by named, versioned policies (e.g. EXP_CLASSIC_BP_MF).   │
│ • Integrity: Pinned by Experiment Manifests guaranteeing auditable reproduction.│
├─────────────────────────────────────────────────────────────────────────────────┤
│ PRODUCT C: LOCALLY CURATED SUBSET                                               │
│ • Role: Claims and evidence relations adjudicated under 06_manual_revision.     │
│ • Governance: Contains both positive claims and first-class refutations.        │
│ • Future Mapping: Corresponds to future MFP_CuratedData without premature       │
│   renaming of active artifacts.                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Provenance-Loss Assessment and Unexecuted Database Checks

### 6.1 End-to-End Pipeline Provenance-Loss Trace

Tracking biological evidence from raw sources through to analytical projections reveals specific stages where metadata is preserved, dropped, or unverified:

| Pipeline Transition | GAF / Bio Attribute | Upstream Reality in Raw Source | Transformation Behavior | Preservation Status | Scientific Impact & Consequence |
|---|---|---|---|---|---|
| **Raw $\to$ Importer** | Reference Namespace | Multitask: numeric PMIDs + text OMIM (`HIV-1... omim:600534`); PlantMP: numeric PMIDs | Parsers preserve raw strings in `Reference` and `pubmed_id` | **PRESERVED** | Preserved verbatim; requires typed namespace splitting downstream. |
| **Raw $\to$ Importer** | Qualifiers (`NOT`) | PlantMP/Multitask: no qualifiers in raw; MoonDB EMF: predicted pairs | Raw text statements do not contain explicit `NOT` tokens | **NOT_APPLICABLE** | Source databases did not capture explicit negative functional qualifiers. |
| **Catalog $\to$ BioData** | UniProtKB TrEMBL | Catalog MVP contains 2,322 entities (including 148 TrEMBL accessions) | PIS `UniProtExtractor` used `Bio.ExPASy.get_sprot_raw` (Swiss-Prot only) | **LOST_IN_TRANSFORMATION** | 148 accessions remained unlinked (`protein_id = NULL`) in BioData; biased against non-reviewed taxa. |
| **QuickGO $\to$ BioData** | Qualifier (`NOT`) | QuickGO API provides explicit `qualifier` (`NOT`, `contributes_to`, etc.) | PIS `QuickGOAnnotationExtractor` completely ignored `qualifier` field | **LOST_IN_TRANSFORMATION** | Stored without negation indicators; potential downstream false-positive risk. |
| **QuickGO $\to$ BioData** | ECO Codes | QuickGO API returns full ECO IDs (`ECO:0000314`, etc.) | PIS extractor mapped ECO to 3-letter GO acronym (`IDA`) and discarded ECO | **LOST_IN_TRANSFORMATION** | Loss of granular ontological evidence hierarchy; cannot distinguish high-throughput from classic assays. |
| **QuickGO $\to$ BioData** | Non-PMID References | QuickGO returns `GO_REF:0000024`, Reactome, Ensembl, etc. | BioData schema used integer FK to PMID table; non-PMID refs converted to `NULL` | **LOST_IN_TRANSFORMATION** | Non-PMID references converted to `NULL`; cannot quantify population fraction without reconciliation. |
| **QuickGO $\to$ BioData** | Multiple References | QuickGO returns comma-separated PMIDs for well-characterized terms | PIS extractor split and retained **only the first PMID**; discarded others | **LOST_IN_TRANSFORMATION** | Erased secondary literature support and multi-lab replication evidence. |
| **QuickGO $\to$ BioData** | `assigned_by`, `date` | QuickGO API returns annotation authority (e.g. `UniProtKB`, `Ensembl`) and date | PIS extractor discarded `assigned_by` and `date` columns | **LOST_IN_TRANSFORMATION** | Impossible to audit annotation age or distinguish authoritative manual curation from pipeline imports. |
| **QuickGO $\to$ BioData** | Annotation Extensions | QuickGO API returns column 16 extensions (`part_of(...)`, `occurs_in(...)`) | PIS extractor completely discarded annotation extensions | **LOST_IN_TRANSFORMATION** | Contextual biological conditions and cell-type qualifiers were permanently lost. |

### 6.2 Proposed Cross-Tabulation Before Recovery Work

Before committing engineering resources to recovering historical database annotations, the repository must execute a cross-tabulation of available attributes across an identified, verified snapshot:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                  PROPOSED RECOVERY AUDIT CROSS-TABULATION                       │
├─────────────────┬───────────────────┬──────────────────────┬────────────────────┤
│ Evidence Code   │ Reference Type    │ Publication Link     │ Qualifier Status   │
│ Group           │ (PMID / GO_REF /  │ Status (Numeric /    │ (Positive / NOT /  │
│                 │  dbxref / None)   │  NULL / Discarded)   │  Unknown Loss)     │
├─────────────────┼───────────────────┼──────────────────────┼────────────────────┤
│ EXP (Classic)   │ Count by type     │ Linked vs Null       │ Active check       │
│ HTP (High-thru) │ Count by type     │ Linked vs Null       │ Active check       │
│ PHYLO (IBA/IKR) │ Count by type     │ Linked vs Null       │ Active check       │
│ COMP (ISS/ISO)  │ Count by type     │ Linked vs Null       │ Active check       │
│ ELECTRONIC(IEA) │ Count by type     │ Linked vs Null       │ Active check       │
└─────────────────┴───────────────────┴──────────────────────┴────────────────────┘
```

### 6.3 Proposed Unexecuted Read-Only Database Queries

To safely audit the snapshot once restored into an authorized PostgreSQL environment, the following read-only SQL queries are proposed (**NOT EXECUTED** during this turn):

```sql
-- 1. Distribution of Evidence Codes and Publication Link Status
-- PURPOSE: Audit true extent of NULL publication links across evidence codes.
SELECT 
    evidence_code,
    COUNT(*) AS total_annotations,
    COUNT(publication_id) AS with_publication_id,
    COUNT(*) - COUNT(publication_id) AS null_publication_id,
    ROUND(100.0 * (COUNT(*) - COUNT(publication_id)) / COUNT(*), 2) AS pct_null
FROM protein_go_term_annotation
GROUP BY evidence_code
ORDER BY total_annotations DESC;

-- 2. Audit of Unique Quadruple Collisions
-- PURPOSE: Verify whether multiple annotations collapsed into identical tuples.
SELECT 
    protein_id, go_id, evidence_code, publication_id, COUNT(*) AS collision_count
FROM protein_go_term_annotation
GROUP BY protein_id, go_id, evidence_code, publication_id
HAVING COUNT(*) > 1;

-- 3. Crosswalk of Swiss-Prot vs TrEMBL Coverage Gap
-- PURPOSE: Measure exact unlinked accessions in BioData.
SELECT 
    a.data_class,
    COUNT(a.id) AS total_accessions,
    COUNT(a.protein_id) AS linked_to_protein,
    COUNT(a.id) - COUNT(a.protein_id) AS orphaned_accessions
FROM accession a
GROUP BY a.data_class;
```

---

## 7. Verifiable Acceptance Scenarios

The eleven proposed acceptance scenarios are refined to reflect policy-dependent projections and refined polarity:

1. **SCEN-01: External Experimental Annotation Not Reviewed Locally**
   - *Input*: External GAF row for `P04406` with `GO:0004365`, `evidence = "IDA"`, `reference = "PMID:12345678"`. No local review exists in `docs/curation/`.
   - *Handling*: Ingested into Product A (Source Inventory); admitted to Product B (Analytical View `EXP_ALL_V1`); absent from Product C (Locally Curated Subset).
   - *Verification*: `review_workflow_status == "not_reviewed"`, `scientific_assessment == "not_yet_assessed"`, `eligible_under_exp_all_v1 == true`.

2. **SCEN-02: IEA Annotation Supported by GO_REF Rather than PMID**
   - *Input*: Electronic annotation for `A0A059U5R2` with `GO:0005840`, `evidence = "IEA"`, `reference = "GO_REF:0000024"`.
   - *Handling*: Reference captured with `reference_type = "go_ref"`, `reference_id = "GO_REF:0000024"`. Never converted to `publication_id = NULL`. Excluded from strict experimental views by policy; admitted to exploratory views.
   - *Verification*: `reference_id == "GO_REF:0000024"`, `reference_type == "go_ref"`.

3. **SCEN-03: Abstract Available, Full Text Unavailable**
   - *Input*: Literature citation `PMID:15006356` behind commercial paywall. Abstract indexed in PubMed; full text inaccessible.
   - *Handling*: Captured with `documentary_availability = "abstract_available"`, `rights_tier = "public_abstract"`. May support author-statement claim, but prohibited from certifying physiological sufficiency for moonlighting.
   - *Verification*: `curation_sufficiency == "not_evaluable_from_abstract"`, `documentary_availability == "abstract_available"`.

4. **SCEN-04: Negative NOT Annotation in Polarity-Aware Views**
   - *Input*: External annotation for `P12345` with `GO:0006915`, `qualifier = "NOT"`, `evidence = "IMP"`.
   - *Handling*: Preserved in Product A with `qualifier = "NOT"` and `is_negative = true`. Strictly excluded from positive-association aggregations, but accessible in polarity-aware analyses (e.g. studying negative functional boundaries).
   - *Verification*: Excluded from positive views; included in polarity-aware view with explicit negative polarity flag.

5. **SCEN-05: Lost or Unknown Qualifier Information**
   - *Input*: Historical BioData annotation row where `qualifier` was omitted during QuickGO extraction.
   - *Handling*: Ingested into Product A with `qualifier_status = "unknown_legacy_loss"`. Quarantined from positive-association analytical views. Unknown polarity must not silently enter positive views.
   - *Verification*: View applying `STRICT_EXP_POSITIVE_V1` rejects rows with `qualifier_status == "unknown_legacy_loss"`.

6. **SCEN-06: Same Protein, GO Term, and Evidence Code with Different Provenance**
   - *Input*: Two distinct GAF rows for `P04406` with `GO:0004365` and `evidence = "IDA"`. Row 1 assigned by `UniProtKB` citing `PMID:11111111`; Row 2 assigned by `EcoCyc` citing `PMID:22222222`.
   - *Handling*: Preserved as two distinct occurrence records in Product A. Analytical projection is **policy-dependent**: an occurrence-preserving view retains both; a non-redundant set view collapses them while preserving links to both occurrence IDs.
   - *Verification*: Occurrence-level traceability preserved; no hardcoded mandatory merging.

7. **SCEN-07: Reviewed Paper Containing Both Supported and Unsupported Claims**
   - *Input*: Primary publication de Pereda et al. (2004) evaluating human PTRH2 (`Q9Y3E5`). Paper contains crystallographic assay proving peptidyl-tRNA hydrolase kinetics, and discussion section hypothesizing apoptosis interaction.
   - *Handling*: Evidence relation links paper to Claim 1 (Hydrolase) with `support_role = "supports"` and `scientific_assessment = "supported"`. Evidence relation links paper to Claim 2 (Apoptosis/Transcription) with `support_role = "ambiguous_inference"` and `scientific_assessment = "insufficient_evidence"`.
   - *Verification*: One publication links to two claims with distinct, non-conflated scientific assessment statuses.

8. **SCEN-08: Shared PMID Without Demonstrated MF–BP–CC Context**
   - *Input*: Multitask row citing `PMID:22014899`, which annotates both `GO:0005524` (ATP binding, MF) and `GO:0016021` (integral component of membrane, CC). The paper does not demonstrate that ATP binding occurs in the membrane.
   - *Handling*: Emitted as an unlinked annotation set in Product A and Product B. Synthesizing a functional triplet $\tau = (\text{ATP binding}, \text{membrane}, \dots)$ is blocked.
   - *Verification*: Contextual triplet relation table contains 0 rows; aspect-specific co-annotation table contains 1 co-occurrence observation labeled as non-causal.

9. **SCEN-09: Partial MF-Only Observation**
   - *Input*: Source record providing explicit molecular function (e.g. `CTP synthase activity`, `GO:0003883`), but providing null or unassigned values for BP and CC.
   - *Handling*: Fully valid functional claim and annotation. Admitted to Product A and MF-specific analytical views without requiring synthetic null placeholders for BP or CC.
   - *Verification*: Record passes schema validation; `go_aspect == "MF"`, `bp == null`, `cc == null`; row count conserved.

10. **SCEN-10: Later Review Conflicting with an Earlier Review**
    - *Input*: Curator 1 in 2026-10 evaluates Claim X as `supported`. Curator 2 in 2026-11 evaluates new contradictory assay and marks Claim X as `contradicted`.
    - *Handling*: Both review events are preserved with immutable event IDs and timestamps ($T_1, T_2$). No global status is overwritten to "disputed". Analytical policy determines resolution (e.g. latest-takes-precedence, conservative exclusion, or dispute quarantine).
    - *Verification*: Both review event records survive intact; audit log reflects dispute; no silent overwriting.

11. **SCEN-11: Reproduction of an Earlier Experiment After New Reviews Are Added**
    - *Input*: Analytical Study 1 executed on 2026-10-15 using Experiment Manifest `MANIFEST-EXP-001`. On 2026-11-01, 50 new curation reviews are added to Product C. Study 1 is re-run on 2026-11-10 referencing `MANIFEST-EXP-001`.
    - *Handling*: The pipeline consumes the snapshot and curation commit pinned in `MANIFEST-EXP-001`. For explicitly deterministic artifacts, outputs match historical checksums.
    - *Verification*: Checksums of generated analytical CSVs match the original study manifest.

---

## 8. Documentation Safeguards and Recovery Mapping

In accordance with repository governance:
1. **No Archival Based Solely on Language or Approval Status**: Non-English documents and unapproved proposals are retained and organized based on technical relevance, not language. Active canonical specifications are maintained in English, while verbatim source strings and historical Catalan/Spanish records are preserved.
2. **Section-Level Recovery Map Before Archival**: Before any proposal document in `docs/roadmap/01-07` is relocated to `docs/archive/`, a section-level recovery map must be approved by the scientific lead, documenting which mathematical formulations (e.g. Wang/Lin metrics in 04, co-occurrence in 04a, curation protocols in 06) will be synthesized into English reference documents (`docs/architecture/`, `docs/curation/`).
3. **Mojibake Duplicate Disposal Prerequisite**: Section 3 (Finding F-10) provided empirical proof that `docs/roadmap/core/experiment_guio_v1.md` contains 0 unique characters compared to `experiment_definition.md` (all 292 line differences are double-encoded UTF-8 artifacts). Disposal or quarantine may proceed without risk of content loss upon maintainer sign-off.
4. **Repository-Relative Links**: All links across repository documentation must use repository-relative paths (e.g. `[README.md](README.md)` or `[spec.md](specs/functional-normalization-pilot/spec.md)`), avoiding machine-specific `file://` URLs.

---

## 9. Prioritized Action Matrix: Now, Next, Later

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PRIORITIZED ACTION MATRIX                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ HORIZON 1: NOW (Immediate Proposal Amendment & Batch 1 Decoupling)              │
│   • Increment 1: Amend proposal text PROP-EVOLUTION-2026-11-10 with matrix      │
│   • Increment 2: Execute Batch 1 doc fixes (5 broken links, README v0.3.0)      │
│   • Reconcile PlantMP working-tree status (commit TASK-04 or isolate)           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ HORIZON 2: NEXT (Source Profiles, Archival & Phase D0 SDD Drafting)             │
│   • Execute Batch 2 doc alignment (source profiles, scripts/README.md)          │
│   • Prepare recovery map and archive Spanish dossiers to docs/archive/          │
│   • Quarantine or dispose of verified mojibake duplicate experiment_guio_v1.md  │
│   • Draft proposed ADR-009 (Bibliographic Scope) & specs/bibliographic-evidence/│
├─────────────────────────────────────────────────────────────────────────────────┤
│ HORIZON 3: LATER (Post-v1 Phase D0 Pilot Execution & Database Reconciliation)   │
│   • Execute 3-publication pilot extract and contract test suite                 │
│   • Restore BioData snapshot in isolated container; run read-only audit queries │
│   • Reconcile 148 TrEMBL accessions via UniProtKB REST API                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Independent Increments: Execution Specifications

Proposal amendments and `DOC-BATCH-001` must be maintained and authorized as **strictly separate increments**, each with its own write boundary, diff, and acceptance criteria.

### Increment 1: Proposal Text Amendments (`PROP-AMEND-001`)
- **Target File**: `docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` (1 file only).
- **Scope**: Incorporate the Non-Blocking Preservation Principle, three-product architecture, dataset publication qualification, policy-dependent projections, and refined polarity.
- **Verification**: `python3 scripts/validate_repository.py` passes; git diff touches only the single proposal file.

### Increment 2: Critical Entry-Point and Broken Link Repair (`DOC-BATCH-001`)
- **Target Files (9 files only)**:
  1. `README.md`
  2. `docs/canonical-schema.md`
  3. `docs/maintenance/biodata-snapshot-and-restore-guide.md`
  4. `docs/maintenance/technical-maintenance-guide.md`
  5. `docs/roadmap/mfp-catalog-implementation-plan.md`
  6. `docs/getting-started.md`
  7. `docs/analysis/five-source-descriptive-study-plan.md`
  8. `docs/releases/mfp-catalog-v1-contract-draft.md`
  9. `tests/fixtures/functional_claims_multitask/README.md`
- **Permitted Edits**:
  - `README.md`: Translate Catalan line 5 to English; align link text in lines 23 and 37 to `v0.3.0`; update release notes link in line 64 to `v0.3.0`; delete Section `## Repository status caveat` (lines 99–101).
  - `docs/canonical-schema.md`: Replace malformed link `` `[Z|±HH:MM](Z|±HH:MM)` `` with code span `` `Z|±HH:MM` ``.
  - `docs/maintenance/biodata-snapshot-and-restore-guide.md`: Replace broken `.dump` link with notice of external uncommitted status.
  - `docs/maintenance/technical-maintenance-guide.md` & `docs/roadmap/mfp-catalog-implementation-plan.md`: Replace 3 broken links with citations to accepted ADR-007.
  - `docs/getting-started.md`: Delete Section `## Clone status caveat` (lines 124–131).
  - `docs/analysis/five-source-descriptive-study-plan.md` & `docs/releases/mfp-catalog-v1-contract-draft.md`: Correct candidate links to `v0.3.0`.
  - `tests/fixtures/functional_claims_multitask/README.md`: Correct line 7 path typo to `data/manifests/source_manifest.csv`.
- **Verification**: Automated link scan reports 0 broken links; `package_catalog_candidate.py --verify-package` passes.

---

## Concise Approval Checklist

Please review the following decision gates to authorize the next operational increment:

- [ ] **1. Authorize Increment 1 (Proposal Amendments)**: Grant explicit authorization to amend [`bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) per the Change Matrix.
- [ ] **2. Authorize Increment 2 (`DOC-BATCH-001`)**: Grant explicit authorization to execute `DOC-BATCH-001-ENTRYPOINT-AND-LINKS` across the 9 declared documentation files.
- [ ] **3. Approve Archival Strategy & Mojibake Disposal**: Authorize creating `docs/archive/` and disposing of verified duplicate `experiment_guio_v1.md` upon completion of Increment 2.

---
*End of Technical Amendment Report (Revision 2). Awaiting Maintainer Decision.*
