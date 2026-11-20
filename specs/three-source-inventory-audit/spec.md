# Specification: Three-Source Catalog Inventory & Biological Identity Audit

- **Document ID**: `SPEC-THREE-SOURCE-INVENTORY-AUDIT-001`
- **Feature Directory**: `specs/three-source-inventory-audit/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Specification; Contract & Accounting Rules Defined)
- **Status**: **Draft Specification — Pending Human Review & Authorization to Implement**
- **Baseline Git HEAD**: `f9d9fba58a5a03a949c346a5956b8795b312b24d`
- **Upstream Roadmaps & Specifications**:
  - Technical Roadmap: [`docs/roadmap/pilot-to-three-source-validation-roadmap.md`](../../docs/roadmap/pilot-to-three-source-validation-roadmap.md) (Phase B, Tasks `TASK-EXT-04` through `TASK-EXT-07`)
  - Catalog Candidate Baseline: `releases/mfp-catalog-candidate-v0.3.0/` ([ADR-006](../../docs/decisions/ADR-006-coverage-only-moonprot-status-rows.md))
  - Stage PIL-04.1B Descriptive Report: [`docs/reports/quickgo-pilot-pil-04.1b-descriptive-results.md`](../../docs/reports/quickgo-pilot-pil-04.1b-descriptive-results.md)
  - GO Aspect Enrichment Spec: [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../quickgo-pilot-go-aspect-enrichment/spec.md)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Purpose, Operational Boundaries & Non-Goals

### 1.1 Purpose
This specification defines the strict scientific, data, and accounting contracts for executing a **comprehensive, local, and reproducible inventory audit** of the three primary curated moonlighting protein sources in the repository:
1. **MoonProt** (`SRC_MOONPROT`)
2. **MultitaskProtDB-II** (`SRC_MULTITASKPROTDB_II`)
3. **PlantMP** (`SRC_PLANTMP`)

The core mission of the audit is to establish an empirical baseline of what is present, what is missing, what is structurally consistent, and what requires curatorial review across these three databases before undertaking any generalization of the concordance engine or full-catalog execution.

### 1.2 Boundary Distinctions: Normalized Catalog vs Raw Data Layers
A strict architectural distinction must be maintained between two data layers:
1. **Normalized Catalog Layer (Primary Audit Target)**:
   - The tables packaged under candidate release `releases/mfp-catalog-candidate-v0.3.0/`.
   - The audit inspects whether the normalized entities, identifiers, assertions, and coverage records satisfy referential integrity and complete denominator accounting.
2. **Raw Source Data Layer (Conditional Cross-Check)**:
   - The raw files stored under `data/raw/`.
   - MultitaskProtDB-II (`data/raw/multitaskprotdb-ii/proteins.csv`) and PlantMP (`data/raw/plantmp/PlantMP_all.csv`) are tracked in Git and mandatory for raw cross-verification.
   - MoonProt raw HTML artifacts (`data/raw/moonprot/mpid_*.html`) and their index (`artifact_index.csv`) are **untracked/gitignored** per [`data/raw/README.md`](../../data/raw/README.md). Checks requiring these raw HTML files are **conditional**: if absent from the execution environment, the audit must pass `--allow-missing-raw`, log an explicit notice (`raw_dependency_absent_on_clone`), record skipped checks, and report MoonProt coverage explicitly as partial verification (`partial_verification_raw_missing`), never as a fully validated source layer, and proceed with the catalog audit without runner failure.

### 1.3 Scientific Non-Goals (Explicitly Out of Scope)
Under repository governance ([`AGENTS.md`](../../AGENTS.md) §1, §5, §6) and [ADR-001](../../docs/decisions/ADR-001-repository-scope.md), the audit must **NEVER**:
- Automatically correct biological identities, rewrite taxa, or alter source accessions.
- Delete, merge, or collapse internal multiplicity records under the assumption that they are erroneous duplicates.
- Pre-judge or reassign `P34788` without a formal curatorial adjudication record.
- Execute network calls, download external databases, or crawl web portals.
- Train machine learning models, generate feature embeddings, or synthesize negative control sets (NMF).
- Enforce arbitrary thresholds (such as the unapproved indicative $>5\%$ quarantine threshold) as automatic blocking gates for running a descriptive inventory audit.
- Silently drop unmapped or ambiguous records; all non-evaluable cases must be explicitly accounted for in an auditable quarantine register.

---

## 2. Input Contracts & Execution Environment

The audit operates in a 100% offline, read-only mode against frozen local artifacts:

### 2.1 Candidate Release Tables (Mandatory)
The audit validates and analyzes the candidate release candidate package `releases/mfp-catalog-candidate-v0.3.0/`:

| Artifact Path | Expected Role in Audit | Frozen SHA-256 Checksum |
|---|---|---|
| [`releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv`](../../releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv) | Primary source record inventory ($1,508$ rows for the 3 sources in `v0.3.0`) | `89daf82e254c02943a98d11e7391504596ba86c607f33bf10bf39ae64b023129` |
| [`releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv`](../../releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv) | Entity resolution and canonical accession mapping | `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc` |
| [`releases/mfp-catalog-candidate-v0.3.0/mfp_identifiers.csv`](../../releases/mfp-catalog-candidate-v0.3.0/mfp_identifiers.csv) | Secondary cross-references and accession history | `27afb04dd673ca81ea8f11b20b034fe8d4cb5a1efd41f140b1921306b2d9513c` |
| [`releases/mfp-catalog-candidate-v0.3.0/mfp_assertions.csv`](../../releases/mfp-catalog-candidate-v0.3.0/mfp_assertions.csv) | Normalized functional claims and assertions | `b3843dcdc99f6c172ce2ff49480024d12c4f239a52e326e23f86a4d80dc14fd5` |
| [`releases/mfp-catalog-candidate-v0.3.0/mfp_coverage.csv`](../../releases/mfp-catalog-candidate-v0.3.0/mfp_coverage.csv) | Entity-level source coverage statuses | `46889dcad5cab7907803c2f9e3ec127ad44da67dc133b03a56ff7de8bce9ad49` |
| [`releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json) | Release package manifest and metadata | `ae811d28bad3bdd05be8df2d02607e056b4b4f5df7151c783b1bbac934c5963e` |

### 2.2 Raw Data Sources (Tracked vs Conditional)
- **Tracked in Git (Mandatory Cross-Check)**:
  * MultitaskProtDB-II: `data/raw/multitaskprotdb-ii/proteins.csv` (SHA-256 recorded in `data/manifests/source_manifest.csv`).
  * PlantMP: `data/raw/plantmp/PlantMP_all.csv` (SHA-256 recorded in `data/manifests/source_manifest.csv`).
- **Conditional / Local-Only (Optional Cross-Check)**:
  * MoonProt: `data/raw/moonprot/artifact_index.csv` and `data/raw/moonprot/mpid_*.html`.
  * *Degradation Policy*: If `data/raw/moonprot/` is absent, the auditor passes `--allow-missing-raw`, skips raw HTML syntax cross-checks, sets MoonProt raw audit status to `partial_verification_raw_missing` (recording skipped checks), and performs the complete audit on the normalized catalog records without runner failure.

### 2.3 Reference Ontology Snapshot (Mandatory)
- Pinned Gene Ontology OBO snapshot: `releases/2026-01-23` (`go.obo`, SHA-256 `eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391`).
- Used to validate CURIE formats, active vs obsolete terms, secondary `alt_id` mappings, and GO aspect assignments.

### 2.4 Declared QuickGO Capture Slice (Conditional)
- External QuickGO annotations are evaluated **only if a local capture slice is explicitly declared** (e.g. `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv`).
- If no full-catalog QuickGO snapshot is declared, QuickGO coverage is formally classified as `quickgo_coverage_unassessed_in_inventory`.

---

## 3. Evaluation Units, Entities & Keys

To prevent semantic conflation, the audit operates across seven distinct evaluation units:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              HIERARCHY OF EVALUATION UNITS                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. SOURCE RECORD          │ Row in mfp_source_records.csv (Key: source_record_id)      │
│ 2. SOURCE–ENTITY PAIR     │ Unique tuple (source_name, protein_id)                     │
│ 3. INTEGRATED ENTITY      │ Macromolecule digest MFPB_PROTEIN_ID_V1 (Key: protein_id)  │
│ 4. FUNCTIONAL ASSERTION   │ Extracted claim in mfp_assertions.csv (Key: claim_id)      │
│ 5. SOURCE GO ANNOTATION   │ Explicit GO term attached to record (Key: annotation_id)   │
│ 6. BIBLIOGRAPHIC CITATION │ Curated literature reference (Key: reference_curie / pmid) │
│ 7. QUARANTINE INCIDENT    │ Event row in quarantine register (Key: 4-part incident key)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Unit Definitions & Keys
1. **Source Record (`source_record_id`)**:
   - The primary observational unit. Represents one record extracted from a specific database snapshot.
   - Format: `moonprot_<mpid>`, `multitaskprotdb_ii_row_<idx>`, `plantmp_order_<order>`.
   - *Uniqueness Scope*: While prefix conventions provide uniqueness across candidate release `v0.3.0`, referential integrity formally enforces the compound key `(source_name, source_record_id)` as the guaranteed unique referential key and fallback across all tables.
2. **Source–Entity Pair (`(source_name, protein_id)`)**:
   - Associates an integrated protein entity with an individual source database.
   - A single protein present in both MoonProt and Multitask produces two source-entity pairs.
3. **Integrated Protein Entity (`protein_id`)**:
   - The canonical macromolecular entity identified by deterministic hash `MFPB_PROTEIN_ID_V1` ([ADR-005](../../docs/decisions/ADR-005-deterministic-protein-ids.md)).
   - Formula: `MFP:U:` + $\text{SHA-256}(\text{canonical\_uniprot\_accession})[0:16]$.
4. **Functional Assertion (`claim_id`)**:
   - A distinct biological assertion extracted from a source record (e.g. canonical function vs moonlighting function).
5. **Source GO Annotation (`source_go_annotation_id`)**:
   - An individual GO term cited in source metadata.
6. **Bibliographic Reference (`reference_curie` / `pmid`)**:
   - Literature citations associated at the record level.
7. **Quarantine Incident Event (`(source_name, source_record_id, row_locator, primary_reason_code)`)**:
   - An individual finding or anomaly logged in `three_source_quarantine_register.csv`.
   - **Compound Primary Key**: `(source_name, source_record_id, row_locator, primary_reason_code)`. Incorporates `row_locator` to ensure that identical incident reason codes occurring on distinct physical rows that share the same source–record key do not collide.
   - **`row_locator` Definition**: Stably formatted relative to the input artifact root without depending on machine-specific absolute filesystem paths: `<artifact_relative_path>#record:<data_record_index>` (e.g. `releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv#record:142`). Here `data_record_index` is the 1-based index of parsed CSV data records, strictly excluding the CSV header row. It must **NOT** be confused with a physical text line number, as multi-line quoted CSV fields can span several text lines.
   - **Multiple Findings Policy**: If multiple findings of the same `primary_reason_code` arise on the exact same physical occurrence (identical source record and `row_locator`), the auditor enforces a single deterministic policy: deterministic aggregation of details into `evidence_detail` (e.g. sorted, semicolon-delimited text), ensuring a single incident row per reason code per occurrence without emitting duplicate keys.
   - A single source record occurrence may trigger multiple distinct reason codes (e.g. malformed syntax AND missing attribute), resulting in multiple incident rows. In the census and total accounting, that source record key is counted **exactly once** under affected source–record keys ($N_{\text{affected\_keys}}$).

### 3.2 Four Accounting Metrics, Row Conservation & Key Uniqueness
To prevent semantic conflation and ensure strict accounting, the audit distinguishes four independent quantitative metrics:
1. **Loaded Physical Rows ($N_{\text{loaded\_rows}}$)**:
   The count of physical rows loaded from candidate release table `mfp_source_records.csv` within the 3-source perimeter ($1,508$ rows in `v0.3.0`).
2. **Distinct Source-Record Keys ($N_{\text{unique\_keys}}$)**:
   The count of distinct compound keys $|(source\_name, source\_record\_id)|$ loaded ($1,508$ in `v0.3.0`).
3. **Accounted Rows ($N_{\text{accounted\_rows}}$)**:
   The count of input physical rows fully accounted for and traceable in the audit output.
4. **Logged Incidents ($N_{\text{incidents}}$)**:
   The total count of incident event rows emitted into `three_source_quarantine_register.csv`.

#### Primary Row Conservation Invariant
The principal accounting invariant across the entire audit pipeline is:
$$N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$$
Every physical input row loaded must be accounted for and traceable to output tables. Zero rows may be dropped, silently excluded, or collapsed. Deduplication must never be performed prior to accounting.

#### Source-Record Key Uniqueness Validation vs Source–Entity Multiplicity
Key uniqueness and biological multiplicity represent fundamentally different dimensions:
- **Key Uniqueness Validation (Structural Check)**:
  Validated as an independent integrity check. If two or more physical rows share the exact same `(source_name, source_record_id)` key:
  * Both physical rows are retained and accounted for in $N_{\text{accounted\_rows}}$ (no deduplication prior to accounting).
  * The collision is logged as a structural integrity violation (`source_record_key_collision`) in `three_source_quarantine_register.csv`.
  * Each occurrence remains individually traceable via its distinct, stable `row_locator` (`<artifact_relative_path>#record:<data_record_index>`).
  * A key collision violates integrity and triggers `non_conforming_integrity_violation`.
- **Source–Entity Multiplicity (Domain Curation)**:
  Occurs when multiple distinct source records (different `source_record_id` keys) reference the exact same `protein_id` within a source database. This reflects legitimate curation (e.g. separate entries for canonical vs moonlighting functions, isoform disambiguation, or re-annotation history). Source–entity multiplicity is **NOT** a key collision, is fully preserved, and does **NOT** by itself constitute an error or non-conformance.

#### Strict Separation of Rows, Keys, and Incidents & Deduplicated Affected Keys Accounting
To avoid conflating physical rows, identifiers, and anomalies, the audit maintains a strict separation:
- **Count of Affected Source–Record Keys ($N_{\text{affected\_keys}}$)**:
  The deduplicated count of keys with at least one logged incident is termed **count of affected source–record keys**:
  $$N_{\text{affected\_keys}} = |\{\text{distinct } (source\_name, source\_record\_id) \text{ with } \ge 1 \text{ incident}\}|$$
  It must **NEVER** be termed "affected physical rows" when key collisions exist, because two colliding rows share a single key ($N_{\text{affected\_rows}} \ge N_{\text{affected\_keys}}$). The audit strictly distinguishes:
  1. $N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$: total physical input rows loaded and accounted for.
  2. $N_{\text{unique\_keys}}$: total distinct source–record keys loaded.
  3. $N_{\text{affected\_keys}}$: total distinct source–record keys associated with $\ge 1$ incident.
  4. $N_{\text{incidents}}$: total incident event rows emitted in the quarantine register ($N_{\text{affected\_keys}} \le N_{\text{incidents}}$).
- **Check-Level Evaluability**:
  Evaluability is defined **per check**, not as a global binary partition of records. Evaluability and quarantine are not mutually exclusive global buckets; a record may be fully evaluable for relational integrity (Check 2) while triggering an incident for attribute availability (Check 5) or ontology conformance (Check 6).

#### Reference Baselines vs Universal Invariants
> [!IMPORTANT]
> The figures **$1,508$ source records**, **$1,452$ source-entity pairs**, and **$1,179$ unique protein entities** are empirical properties of candidate release `v0.3.0`. They are reference baselines, **NOT** hardcoded invariants of the audit contract itself. If a future release or local audit recalculates different numbers, the audit tool must account for all loaded rows ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$) and report discrepancies, not force data into historical figures.

---

## 4. Comprehensive Audit Checks & Verification Invariants

The audit executes eight structured checks across the three sources:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              STRUCTURED AUDIT CHECKS                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ CHECK 1: Cardinalities & Disjoint Venn Partitions                                      │
│ CHECK 2: Relational Referential Integrity Across Scoped Perimeters                     │
│ CHECK 3: Internal Record Multiplicity Characterization                                 │
│ CHECK 4: Accession Syntax, Relational Consistency & Biological Identity                │
│ CHECK 5: Attribute Availability (Taxonomy, Sequences, Functions, GO, PMIDs)            │
│ CHECK 6: Ontological Conformance (CURIEs, Alt IDs, Obsoletes, Aspects)                 │
│ CHECK 7: Typology of Missingness & Error Classification                                │
│ CHECK 8: QuickGO Snapshot Coverage Reconciliation (Conditional)                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Check 1: Cardinalities & Disjoint Venn Partitions
- **Source Record Cardinality**:
  Calculate $N_{\text{records}}(S)$ for $S \in \{\text{MoonProt}, \text{Multitask}, \text{PlantMP}\}$.
  Verify that the sum matches the total 3-source record population ($N_{\text{total}} = 1,508$ rows in `v0.3.0`).
- **Unique Entity Cardinality**:
  Calculate $|M|$, $|T|$, $|P|$ as distinct sets of `protein_id`.
- **Inclusive Intersections**:
  Calculate standard pairwise set intersections $|M \cap T|$, $|M \cap P|$, $|T \cap P|$ and triple intersection $|M \cap T \cap P|$.
- **Mutually Disjoint Venn Partitions**:
  Calculate the exact size of the 7 mutually exclusive regions:
  1. $R_1$: Present only in MoonProt (absent from Multitask and PlantMP): $|M \setminus (T \cup P)|$
  2. $R_2$: Present only in Multitask (absent from MoonProt and PlantMP): $|T \setminus (M \cup P)|$
  3. $R_3$: Present only in PlantMP (absent from MoonProt and Multitask): $|P \setminus (M \cup T)|$
  4. $R_4$: Present in MoonProt and Multitask only (absent from PlantMP): $|(M \cap T) \setminus P|$
  5. $R_5$: Present in MoonProt and PlantMP only (absent from Multitask): $|(M \cap P) \setminus T|$
  6. $R_6$: Present in Multitask and PlantMP only (absent from MoonProt): $|(T \cap P) \setminus M|$
  7. $R_7$: Present in all three databases (Triple Intersection): $|M \cap T \cap P|$
- **Inclusion-Exclusion Verification**:
  Assert that $\sum_{i=1}^7 |R_i| = |M \cup T \cup P|$.

### 4.2 Check 2: Relational Referential Integrity Across Scoped Perimeters
Before evaluating foreign key relationships, the audit strictly bounds referential integrity checks to the perimeter of the three target sources (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`):
- **Source Record Key Uniqueness**:
  Validate that every physical row in `mfp_source_records.csv` within the 3-source perimeter possesses a unique compound key `(source_name, source_record_id)`. If collisions occur, retain all colliding rows, trace each with its distinct, stable `row_locator` (`<artifact_relative_path>#record:<data_record_index>`), and record a `source_record_key_collision` incident for each colliding occurrence under compound key `(source_name, source_record_id, row_locator, primary_reason_code)`.
- **Source Records to Proteins**:
  Every `protein_id` in `mfp_source_records.csv` within the 3-source perimeter must exist in `mfp_proteins.csv`. Zero orphan records permitted.
- **Source Records to Identifiers**:
  Every 3-source record with a populated `uniprot_id` must have a corresponding entry in `mfp_identifiers.csv` with `identifier_type = "uniprot_accession"`.
- **Assertions to Source Records**:
  Every assertion in `mfp_assertions.csv` within the 3-source perimeter must link to a valid compound key `(source_name, source_record_id)` and `protein_id`.
- **Coverage to Proteins**:
  Every protein entity in `mfp_coverage.csv` for the three sources must map to at least one 3-source record.

### 4.3 Check 3: Internal Multiplicity Characterization
- Identify all accessions where $N_{\text{records}}(\text{source}, \text{accession}) > 1$.
- Classify the multiplicity mechanism for each occurrence using an explicit enumeration:
  * `multi_role_entries`: Database segments canonical and moonlighting claims into separate records.
  * `isoform_disambiguation`: Different records correspond to distinct sequence variants.
  * `re_annotation_history`: Historical entries updated with distinct citations or text.
  * `multiplicity_unclassified`: Assigned when available source evidence is insufficient to distinguish the precise curatorial or functional mechanism.
- Verify that multiplicity records are **fully preserved** across all audit tables and never collapsed, deduplicated, or dropped.

### 4.4 Check 4: Accession Syntax, Relational Consistency & Biological Identity
The audit strictly decouples three distinct layers of identity validation:
1. **Accession Syntax Conformance**:
   - Evaluated purely offline via the official UniProtKB accession regex:
     `^[A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2}$|^[O,P,Q][0-9][A-Z, 0-9]{3}[0-9]$`
   - Classifies accessions as syntactically valid or malformed (`syntax_valid_uniprot_regex`).
2. **Relational Consistency Across Release Tables**:
   - Verifies whether `protein_id` and `uniprot_id` exist consistently in `mfp_proteins.csv` and `mfp_identifiers.csv`.
3. **Biological Identity Status (Strictly Local Reference-Gated)**:
   - An accession must **NEVER** be classified as a validated biological identity merely because its syntax matches the UniProt regex or because an active accession status is detected.
   - Every identity conclusion must be strictly limited to what the specific local versioned reference certifies:
     * Syntax validation regex certifies only *syntactic format* (`syntax_valid_uniprot_regex`).
     * An accession mapping table (if provided) certifies only *accession lifecycle status* (`accession_status_active`, `accession_status_secondary_merged`).
     * Biological entity identity, organism match, and taxonomic congruence (`verified_canonical_entity`, `demutualized_taxonomy`) require an explicit local cross-reference certifying the taxon and sequence. In the absence of an authoritative, versioned local reference certifying biological identity and taxon, the check **MUST** record `biological_identity_unassessed_in_inventory`. It must **NEVER** classify biological identity as validated or failed, and must **NEVER** issue external network calls.

### 4.5 Check 5: Attribute Availability Matrix
Compile completeness metrics across each database for:
1. Organism string and Taxonomy ID.
2. Canonical function description (free text vs structured).
3. Moonlighting function description (free text vs structured).
4. Raw GO terms string.
5. Parsed GO CURIEs and aspect declarations.
6. Evidence codes (e.g. `IEA`, `IDA`, `EXP` or unassessed).
7. Bibliographic references (PMID, DOI, or unparsed citation).

### 4.6 Check 6: Ontological Conformance
Validate all parsed GO terms against pinned `go.obo` (`releases/2026-01-23`):
- `active_term`: Active term in GO. Aspect assigned directly from ontology.
- `secondary_alt_id`: Obsolete alias; maps deterministically to an active primary term.
- `obsolete_term`: Term marked `is_obsolete: true` without active replacement.
- `unknown_curie`: CURIE not present in reference ontology.
- `malformed_token`: String does not match `GO:\d{7}` regex.

### 4.7 Check 7: Typology of Missingness & Error Classification
Classify all non-evaluable fields into mutually exclusive categories without conflation:
- `field_empty`: Column exists in source schema and release table, but the value is empty, blank, or null.
  * *Invariant*: An empty column must never be automatically assumed to represent intentional biological absence or an extraction bug without independent corroborating evidence.
- `observed_absence`: Source metadata or documentation explicitly specifies that the entity lacks the attribute or that the feature was not observed.
- `attribute_unrepresented_in_source`: The source database schema or curation model does not track the attribute (e.g. MoonProt does not track GO aspect distinctions; PlantMP does not track UniProt evidence codes).
- `extraction_error`: Verified parsing defect, delimiter collision, or markup truncation in upstream extraction (e.g. `P24228` unclosed quote).
- `check_impossible_missing_dependency`: Check cannot be evaluated due to unprovisioned local dependency (e.g. untracked MoonProt raw HTMLs on a clean git clone).

### 4.8 Check 8: QuickGO Snapshot Coverage Reconciliation (Conditional)
The audit strictly decouples inclusion in the source vertical slice from coverage in the external QuickGO capture:
- Being outside a source vertical slice is distinct from being absent in QuickGO annotations:
  * An accession omitted from a source vertical slice cannot be cited as evidence of absence in the QuickGO capture.
- If a local QuickGO snapshot is declared, evaluate:
  * `linked_in_quickgo`: Protein entity exists in capture and has linked annotations.
  * `unlinked_in_quickgo`: Accession exists but `protein_id IS NULL` in capture slice (e.g. `E6KMA1`).
  * `zero_annotations`: Accession captured but contains 0 annotations.
  * `outside_capture_slice`: Accession omitted from the declared QuickGO capture slice.
- If no snapshot is declared, emit status `quickgo_coverage_unassessed_in_inventory`.

### 4.9 Independent Execution Status, Verification Coverage & Integrity Conformance
The audit strictly decouples three independent, orthogonal dimensions of outcome:

1. **Execution Status (Operational / Process Level)**:
   - Evaluates whether the audit script completed execution or halted due to an operational failure.
   - Values:
     * `execution_success`: The runner completed all audit steps and emitted all required artifacts (exit code 0).
     * `execution_failure`: The runner aborted due to an operational error (e.g. missing mandatory input files, unparseable CSV syntax, existing output directory, or JSON schema validation failure on output; exit code != 0).
   - *Rule*: Any operational failure (`execution_failure`) that prevents evaluating data integrity can **NEVER** produce a declaration of `integrity_conforming`.

2. **Verification Coverage (Data Layer Scope)**:
   - Evaluates the completeness of input layers available in the execution environment.
   - Values:
     * `complete_verification`: All mandatory release tables, tracked raw files, and optional inputs (e.g. MoonProt raw HTMLs) were present and audited.
     * `partial_verification_raw_missing`: Audit executed with `--allow-missing-raw` because optional untracked raw inputs (MoonProt HTMLs) were absent. Catalog tables are fully audited, but raw cross-checks are recorded as omitted.
   - *Rule*: Partial verification due to absent optional raw files is an informative coverage status; it does **NOT** constitute an integrity violation.

3. **Integrity Conformance (Structural & Invariant Compliance)**:
   - Evaluates whether candidate release tables satisfy all non-negotiable relational and accounting invariants.
   - Values:
     * `integrity_conforming`: All structural invariants are satisfied: $N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$, zero source-record key collisions, zero orphan records across scoped perimeters, zero broken scoped foreign keys, and 100% schema validation.
     * `non_conforming_integrity_violation`: One or more non-negotiable integrity invariants were violated (e.g. $N_{\text{loaded\_rows}} \neq N_{\text{accounted\_rows}}$, source-record key collisions, orphan records in release tables, broken scoped foreign keys, schema validation failure).
   - *Rule on Multiplicity & Curatorial Observations*: The presence of internal multiplicity, unclassified multiplicity mechanisms (`multiplicity_unclassified`), descriptive curatorial notices, or unassessed external annotations does **NOT** by itself imply non-conformance. Multiplicity and curatorial caveats are factual properties of the data, not structural defects.

---

## 5. Output Data Contracts, Reproducibility & Staging

The audit execution produces four structured deliverables in declared repository locations:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              PROPOSED AUDIT DELIVERABLES                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. docs/reports/three-source-inventory-audit-report.md      (Human narrative; Gate 4)  │
│ 2. data/curated/audit/three_source_inventory_summary.csv     (Aggregated metrics; Gate 3)│
│ 3. data/curated/audit/three_source_quarantine_register.csv   (Itemized table; Gate 3)   │
│ 4. data/curated/audit/manifest.json                          (Run provenance; Gate 3)   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Human-Readable Audit Report (Gate 4 Deliverable)
- Path: `docs/reports/three-source-inventory-audit-report.md`
- Narrative synthesis documenting:
  * Complete record and entity census across MoonProt, MultitaskProtDB-II, and PlantMP.
  * Disjoint Venn partition breakdown and verification of inclusion-exclusion formula.
  * Multiplicity inventory explaining the nature of surplus records.
  * Attribute completeness tables.
  * Identification of candidate curatorial review cases (e.g. `P34788`, `P24228`).
- Authored during Gate 4 scientific review; **NOT** an output of Gate 3 execution.

### 5.2 Summary Metrics Table (`three_source_inventory_summary.csv`)
- Path: `data/curated/audit/three_source_inventory_summary.csv`
- Header:
  `metric_category,source_name,metric_name,cardinality,denominator,percentage,verification_status,notes`
- Encodes all census figures, completeness fractions, and partition cardinalities.

### 5.3 Quarantine Register Table (`three_source_quarantine_register.csv`)
- Path: `data/curated/audit/three_source_quarantine_register.csv`
- Header:
  `source_record_id,source_name,row_locator,protein_id,uniprot_id,quarantine_category,primary_reason_code,evidence_detail,curatorial_action_required`
- Every record requiring curatorial attention, identity review, or with extraction errors is isolated with an explicit reason code. Zero silent exclusions.
- Granularity & Compound Key: **One row per incident event** (Compound Primary Key: `(source_name, source_record_id, row_locator, primary_reason_code)`). Including `row_locator` in the incident identity guarantees that identical reason codes occurring on distinct physical rows sharing the same source–record key do not collide.
- `row_locator` Definition: Stably formatted relative to the repository/input artifact root (`<artifact_relative_path>#record:<data_record_index>`), independent of absolute machine paths. `data_record_index` is the 1-based index of parsed CSV data records, excluding the header row (represents a parsed logical CSV record, never a raw line of text).
- Multiple Findings Policy: If multiple findings sharing the same primary reason code occur on the exact same occurrence (identical source record and `row_locator`), details are deterministically aggregated into `evidence_detail` (e.g. sorted, semicolon-delimited), preserving a single incident row per reason code per occurrence.
- Key Collision Representation: If physical rows share an identical key, distinct `row_locator` values ensure both colliding occurrences are logged and represented without key collisions in the register and without dropping either occurrence.
- Deduplicated Accounting: The census reports **affected source–record keys** ($N_{\text{affected\_keys}}$) as unique `(source_name, source_record_id)` tuples, strictly separated from affected physical rows and from total incident event rows ($N_{\text{incidents}}$).

### 5.4 Audit Run Manifest (`manifest.json`)
- Path: `data/curated/audit/manifest.json`
- Generated at Gate 3: records **ONLY** Gate 3 outputs (`three_source_inventory_summary.csv`, `three_source_quarantine_register.csv`). It does **NOT** include human narrative reports (`docs/reports/three-source-inventory-audit-report.md`), which are authored subsequently in Gate 4.
- Conforms to repository provenance schema:
  * `input_dataset_digests`: SHA-256 of all candidate release files and raw sources consumed.
  * `output_dataset_digests`: SHA-256 of the generated tabular data files.
  * `execution_metadata`: Timestamp, execution environment, Git commit HEAD, parameter settings, execution status, verification coverage, and integrity conformance.
- *Reproducibility Invariant*: Exact bitwise determinism applies to tabular datasets (`three_source_inventory_summary.csv`, `three_source_quarantine_register.csv`) given identical inputs and CLI arguments. Manifest identity is evaluated by its embedded `input_dataset_digests` and `output_dataset_digests`, since the manifest file itself contains runtime execution metadata (timestamp, duration).

### 5.5 Atomic Staging, Schema Pre-Validation & Path Collision Protection
To guarantee filesystem integrity:
1. **Target Directory Non-Existence Check**: The runner halts immediately if the destination path specified in `--output-dir` already exists. There is no overwrite option in this increment; every audit execution requires a new, non-existent destination directory.
2. **Atomic Staging Directory**: All outputs are generated into a temporary staging directory on the same filesystem.
3. **Pre-Publication Schema Validation**: All tabular outputs are validated against Draft 2020-12 JSON schemas before moving. If validation fails, staging is discarded, leaving the workspace untouched.
4. **Atomic Promotion**: Validated files are promoted atomically to the target directory.

---

## 6. Acceptance Criteria & Pre-Implementation Prerequisites

### 6.1 Acceptance Criteria
When implementation and execution are authorized, the audit increment must satisfy:
1. **100% Row Accounting**: Total row conservation $N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$ ($1,508$ rows for candidate `v0.3.0`). Evaluability evaluated per check; quarantined entities reported as affected source–record keys ($N_{\text{affected\_keys}}$), strictly separated from physical rows and incident rows. Zero dropped rows.
2. **Key Uniqueness & Referential Integrity**: Source-record keys validated for uniqueness; colliding rows preserved and traced with distinct stable row locators (`#record:<data_record_index>`); incident compound key `(source_name, source_record_id, row_locator, primary_reason_code)` prevents incident key collisions; 100% of candidate release cross-table foreign keys within the 3-source perimeter verified using compound key fallback `(source_name, source_record_id)`.
3. **Multiplicity Preservation**: All internal multiplicity records documented without merging or loss; unclassified instances marked `multiplicity_unclassified`.
4. **Offline Determinism**: Script executes 100% offline; repeated executions produce identical SHA-256 digests for tabular datasets.
5. **Schema Validation**: All generated CSV tables validate against Draft 2020-12 JSON schemas.
6. **Independent Status Reporting**: Execution status (`execution_success` vs `execution_failure`), verification coverage (`complete_verification` vs `partial_verification_raw_missing`), and integrity conformance (`integrity_conforming` vs `non_conforming_integrity_violation`) recorded as separate dimensions. Violations of integrity invariants prevent declaring conformance; multiplicity or partial coverage do not. An operational failure preventing evaluation never yields `integrity_conforming`.

### 6.2 Pre-Implementation Prerequisites
Implementation must not commence until:
1. Human sign-off is granted on this specification (`SPEC-THREE-SOURCE-INVENTORY-AUDIT-001`).
2. Human maintainers review and approve the task breakdown (`tasks.md`) and implementation plan (`plan.md`).
3. An explicit authorization gate is opened for code implementation (Gate 1).
4. Git index is confirmed clean of unrelated foreign changes (`0` staged files), with untracked files and working tree edits preserved intact.
