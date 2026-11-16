# Specification: Pinned GO Aspect Partitioning & Metadata Enrichment

- **Document ID**: `SPEC-PIL-04.1-GO-ASPECT-ENRICHMENT`
- **Task Identifier**: `PIL-04.1` (Route B Extension; Master Work Breakdown Structure)
- **Feature Directory**: `specs/quickgo-pilot-go-aspect-enrichment/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Specification; Task PIL-04.1A Authorized & Executed Offline; Task PIL-04.1B Deferred)
- **Status**: Implemented and Verified (2026-11-16)
- **Historical Roadmap Context**: Extends the preliminary draft proposal `draft-proposal-mfp-quickv1-evidence-integration-pilot.md` (where it was informally sketched as "Stage P5"). Formally authorized on 2026-11-16 as bounded task `PIL-04.1A` (minimum GO-aspect metadata enrichment) under Route B of `docs/roadmap/draft-pilot-preservation-communication-and-operational-roadmap.md`, while concordance recomputation (`PIL-04.1B`) remains deferred.
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5
- **Related Documents**:
  - Stage P3 Specification: [`specs/quickgo-pilot-p3/spec.md`](../quickgo-pilot-p3/spec.md)
  - Stage P4 Descriptive Analysis Report: [`docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`](../../docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md)
  - Preservation Record: [`docs/reports/quickgo-pilot-preservation-record.md`](../../docs/reports/quickgo-pilot-preservation-record.md)
  - Communication & Operational Roadmap: [`docs/roadmap/draft-pilot-preservation-communication-and-operational-roadmap.md`](../../docs/roadmap/draft-pilot-preservation-communication-and-operational-roadmap.md)

---

## 1. Scope, Objective & Operational Distinction

### 1.1 Purpose
This specification governs the design, data contracts, and mapping semantics for **Task PIL-04.1: Pinned GO Aspect Partitioning & Metadata Enrichment**.

The objective is to deterministically derive standardized Gene Ontology namespaces (`biological_process` $\to$ `BP`, `cellular_component` $\to$ `CC`, `molecular_function` $\to$ `MF`) for source-native annotations that lack explicit aspect classifications, particularly MoonProt annotations where `go_aspect` is null in the frozen pilot inputs.

### 1.2 Operational Distinction: Metadata Enrichment vs. Functional Inference
In accordance with repository scientific invariants ([`AGENTS.md`](../../AGENTS.md) §5):
- **Ontology Metadata Enrichment**: This task performs deterministic lexical and graph-metadata lookups against an immutable, pinned Gene Ontology snapshot. It resolves existing, explicitly cited `GO:[0-9]{7}` identifiers to their official namespace and status.
- **NOT Functional Discovery**: This task does **NOT** infer new biological functions, predict moonlighting activities, synthesize contextual functional triplets, evaluate semantic similarity graphs, or alter biological evidence.
- **NOT an Overwrite of Historical Baseline**: The preserved Stage P1–P4 artifacts, inputs, outputs, schemas, and manifests remain 100% frozen and immutable. All enrichment outputs are written to a separate, versioned output directory.

### 1.3 Nomenclature: Task PIL-04.1 vs. "Stage P5"
Preliminary draft roadmaps informally used the working label "Stage P5" to denote post-pilot GO enrichment. To eliminate ambiguity, prevent conflating unapproved draft ideas with authorized work, and maintain traceability across repository agents:
- The informal label **"Stage P5"** is recognized as historical proposal shorthand.
- The formal, stable specification identifier for this work is **`PIL-04.1`**, positioned in **Route B (Controlled Scientific Extensions)** of the project master work breakdown structure.
- **Current Authorization Status**: Bounded Task **`PIL-04.1A`** (minimum GO-aspect metadata enrichment) was formally authorized by human sign-off on 2026-11-16, executed offline, and committed in technical commit [`98530b32cd13d0b8ff5b4ea7a626e691d9426d25`](file:///home/alexdoro/repositories/mfp-bibliography). Task **`PIL-04.1B`** (concordance recomputation) remains strictly deferred and unauthorized.

---

## 2. Counting Ambiguity Resolution & Comparison Universes

To prevent analytical conflation between annotation observations, unique terms, records, and concordance units, the specification establishes strict definitions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      FIVE NON-INTERCHANGEABLE METRICS                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. SOURCE ANNOTATION ROWS (N = 353 in input)                           │
│    • MoonProt:            141 rows (all 141 have go_aspect == null)    │
│    • MultitaskProtDB-II:   99 rows (38 BP, 26 CC, 31 MF, 4 unassigned) │
│    • PlantMP:             113 rows (65 BP, 48 MF, 0 CC)                │
│                                                                        │
│ 2. UNIQUE SOURCE GO IDENTIFIERS (N = 205 in input slice)               │
│    • MoonProt:            122 unique GO terms                          │
│    • MultitaskProtDB-II:   80 unique GO terms                          │
│    • PlantMP:              73 unique GO terms                          │
│                                                                        │
│ 3. AFFECTED SOURCE RECORDS (N = 7 records)                             │
│    • MoonProt:              6 records (5 in 8-protein cohort)          │
│    • MultitaskProtDB-II:    1 record (4 unassigned rows)               │
│                                                                        │
│ 4. ACCESSION-SOURCE-ASPECT COMPARISON UNITS (N = 36 units in P4)       │
│    • Evaluable in P4:      10 units (27.8%)                            │
│    • Non-evaluable in P4:  26 units (72.2%)                            │
│      - MoonProt aspect indeterminate: 15 comparison units              │
│        (5 cohort proteins × 3 GO aspects)                              │
│      - P34788 botanical discrepancy:   6 comparison units              │
│      - A0A0H3CDS3 outside slice:       3 comparison units              │
│      - Empty source CC inventories:    2 comparison units              │
│                                                                        │
│ 5. POLICY-SPECIFIC CONCORDANCE ROWS (N = 72 rows in P4)                │
│    • 36 rows under Policy B, 36 rows under Policy C.                   │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Resolution of Counting Ambiguity**:
> The phrase *"15 MoonProt indeterminate terms"* in conversational handoffs was an informal misnomer. It referred strictly to the **15 comparison units** (5 cohort proteins × 3 GO aspects) in the Stage P4 concordance matrix that were gated by `source_aspect_indeterminate`. In reality, MoonProt contributes **141 source annotation rows** citing **122 unique GO identifiers** across 6 records.

### 2.1 Scope & Row-Preserving Mapping Contract
- **Contract Type**: Row-preserving (1:1 bijective mapping across all input annotation rows).
- **Exact Input Cardinality**: Exactly 353 annotation rows from `data/interim/pilot/source_go_annotations_pilot.csv`.
- **Exact Output Cardinality**: Exactly 353 derived annotation rows emitted in `derived_source_go_aspects_pilot.csv`.
- **Verified Cross-Tabulation of Aspect Comparability**:
  - **Rows with Valid Declared Aspect (`BP`, `CC`, `MF`)**: Exactly **208 rows** (95 in MultitaskProtDB-II, 113 in PlantMP, 0 in MoonProt).
  - **Declared-Aspect Obsolete Rows (Non-Comparable)**: Exactly **8 rows** (3 in MultitaskProtDB-II, 5 in PlantMP). Because obsolete terms receive `derived_aspect = null`, conflict assessment is **not applicable / not performed**.
  - **Strictly Comparable Active Rows**: Exactly **200 rows** (92 in MultitaskProtDB-II, 108 in PlantMP) possessing both a valid declared aspect and an active derived ontology aspect.
  - **Conflict Count**: Exactly **0 conflicts** observed across all 200 comparable rows ($0/200 = 0.0\%$).
  - **Undeclared / Unassigned Rows**: Exactly **145 rows** (141 MoonProt with null aspect, 4 MultitaskProtDB-II with `unassigned`). All 4 unassigned Multitask rows resolved to active `BP` terms. MoonProt rows yielded 134 active primary, 3 active alternate IDs, and 4 obsolete terms.
- **Contract Justification**:
  1. Complete row coverage enriches both unassigned annotations (141 MoonProt rows, 4 MultitaskProtDB-II rows) and audits source-declared aspects (95 Multitask rows, 113 PlantMP rows) against the ontology snapshot.
  2. Guarantees 100% backward traceability to Tier A records without omitting rows.
  3. Precludes speculative predictions of evaluability; acceptance is based strictly on mapping accuracy and schema conformity, not on concordance scores or Jaccard values.

---

## 3. Scientific & Operational Questions

The specification addresses two precise questions:

1. **Deterministic Namespace Assignment**:
   *"Given 353 source-native GO annotations in `source_go_annotations_pilot.csv` (including 141 MoonProt annotations with null aspects and 4 MultitaskProtDB-II unassigned annotations), how can standardized GO namespaces (`BP`, `CC`, `MF`) be deterministically derived using a pinned ontology snapshot while preserving source provenance and flagging obsolete or secondary identifiers?"*

2. **Source Consistency & Conflict Isolation**:
   *"How consistently do source-declared aspects in MultitaskProtDB-II and PlantMP agree with the ontology snapshot namespaces, and how are discrepancies isolated for human curatorial review without silent data corruption?"*

---

## 3. Input Dependencies & Invariants

All inputs are frozen, read-only artifacts verified by cryptographic SHA-256 digests.

### 3.1 Primary Input Table
- **File Path**: `data/interim/pilot/source_go_annotations_pilot.csv`
- **File Size**: 81,927 bytes
- **Row Count**: 353 rows (header + 353 data rows)
- **SHA-256 Digest**: `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda`
- **Required Fields**:
  1. `annotation_id` (string, unique key: `MFP:SGA:...`)
  2. `protein_id` (string, canonical hash: `MFP:U:...`)
  3. `source_id` (enum: `SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`)
  4. `source_record_id` (string, native identifier)
  5. `claim_id` (string, nullable)
  6. `source_field` (string, e.g. `GO terms`)
  7. `annotation_index` (integer)
  8. `raw_annotation_text` (string, verbatim extracted text)
  9. `go_id` (string, formatted identifier `GO:\d{7}`)
  10. `go_aspect` (string, source-declared aspect: `BP`, `CC`, `MF`, `unassigned`, or empty/null)
  11. `term_name` (string, source-provided term label)
  12. `evidence_raw` (string, nullable)
  13. `annotation_status` (string)
  14. `notes` (string, nullable)

### 3.2 Secondary Context & Identity Tables (Read-Only)
- **Candidate Catalog Mapping**: `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv`
  - SHA-256: `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc` (2,322 rows).
  - Used strictly to confirm canonical accession resolution (`MFP_PROTEIN_ID_V1`).
- **P3 Execution Manifest**: `data/interim/pilot/quickgo_slice/manifest.json`
  - SHA-256: `01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7` (Manifest v1.1).

---

## 4. Pinned Ontology Artifact Selection & Acquisition Policy

### 4.1 Required Artifact Characteristics
To ensure offline reproducibility and deterministic mapping:
1. **Format**: Standard OBO specification 1.2 (`go-basic.obo`).
2. **Content**: Basic filtered Gene Ontology DAG containing:
   - Term identifiers (`id: GO:\d{7}`)
   - Primary names (`name: ...`)
   - Namespaces (`namespace: biological_process | cellular_component | molecular_function`)
   - Obsolete flags (`is_obsolete: true`)
   - Alternate identifiers (`alt_id: GO:\d{7}`)
   - Replacement references (`replaced_by: GO:\d{7}`)
   - Curatorial advisory suggestions (`consider: GO:\d{7}`)
3. **Immutability**: Pinned to an exact release version and SHA-256 checksum before any code execution.

### 4.2 Local Workstation Inspection & Candidate Analysis
Inspection of existing local filesystem storage identified two candidate ontology snapshots:

| Candidate Snapshot | Local Filesystem Location | Release Tag / Version | File Size | Full SHA-256 Digest | Status |
|---|---|---|:---:|---|:---:|
| **Candidate 1 (Approved & Executed)** | `/home/alexdoro/repositories/mfp-dataset-designer/go-basic.obo` | `releases/2026-01-23` | 31,933,366 bytes | `eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391` | Verified Local (Preceding Snapshot) |
| **Candidate 2 (Secondary)** | `/home/alexdoro/repositories/FANTASIA/go-basic.obo` | `releases/2025-10-10` | 31,048,155 bytes | `4e3ce039a6ad3d45e2752097625330152cc8ae97d35d824c7fcb0735b45d0fc3` | Verified Local |

### 4.3 Selection Rationale & Provenance Definition
- **Provenance Definition**: Candidate 1 (`releases/2026-01-23`, SHA-256 `eee63704...`) is a fixed Gene Ontology snapshot preceding the pilot capture, **not a strictly date-aligned ontology release**. Terms absent from this snapshot remain unresolved relative to this version, but are not declared globally invalid.
- **Portability & Execution Parameters**: The enrichment engine and CLI runner accept `--ontology-obo` as an explicit path parameter and cryptographically verify the expected SHA-256 digest (`--expected-ontology-sha256`) before execution. Reusable code contains zero hardcoded absolute workstation dependencies. Durable provisioning of this ontology dependency must be addressed separately from the sealed P1–P4 preservation package.

---

## 5. Safe Mapping Semantics & Data Contract

To prevent loss of provenance, data corruption, or false functional equivalence, mapping must enforce strict separation between source assertions and derived ontology metadata.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               PROVENANCE-PRESERVING SEPARATION                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   SOURCE-NATIVE ASSERTION (Immutable)            DERIVED ONTOLOGY METADATA              │
│   ┌─────────────────────────────────────┐        ┌────────────────────────────────────┐ │
│   │ source_go_id:          GO:0000013   │        │ resolved_go_id:       GO:0008360   │ │
│   │ source_declared_aspect: null        │───────►│ derived_aspect:       BP           │ │
│   │ raw_annotation_text:   ...          │        │ mapping_status:       resolved_alt │ │
│   │ annotation_id:         MFP:SGA:...  │        │ ontology_release:     2026-01-23   │ │
│   └─────────────────────────────────────┘        └────────────────────────────────────┘ │
│                                                                                         │
│   Rule: source_go_id and source_declared_aspect are NEVER modified, overwritten,        │
│         or silently harmonized.                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Semantic Handling by Identifier Status

| Identifier Category | Ontology Condition | Derived Identifier (`resolved_go_id`) | Derived Aspect (`derived_aspect`) | Mapping Status (`mapping_status`) | Action & Safeguard |
|---|---|:---:|:---:|---|---|
| **Active Primary Identifier** | Term exists with `id: GO:XXXXXXX`; `is_obsolete` is false or absent | `GO:XXXXXXX` (identical) | `BP`, `CC`, or `MF` (from `namespace`) | `resolved_primary` | Standard deterministic lookup. |
| **Secondary / Alternate Identifier** | `GO:XXXXXXX` matches an `alt_id` of a primary term `GO:YYYYYYY` | `GO:YYYYYYY` (primary term) | Primary term's namespace | `resolved_secondary_alt_id` | `source_go_id` is preserved verbatim as `GO:XXXXXXX`. Never overwrite raw source string. |
| **Obsolete with Replacement** | Term has `is_obsolete: true` and `replaced_by: GO:ZZZZZZZ` | `null` | `null` | `obsolete_replaced_by` | Source ID preserved. Replacement documented in `replaced_by_go_id` metadata. **Zero automated substitution** into `resolved_go_id`; `derived_aspect` remains null per Rule C. |
| **Obsolete without Replacement** | Term has `is_obsolete: true` and NO `replaced_by` tag | `null` | `null` | `obsolete_unreplaced` | `consider` tags documented in `consider_go_ids` metadata. **Prohibition**: NEVER follow `consider:` tags as automated replacements. `consider` tags are curatorial suggestions, not equivalents. `derived_aspect` remains null. |
| **Unknown Identifier** | `GO:XXXXXXX` not found in primary terms, `alt_id`, or obsolete records | `null` | `null` | `unresolved_unknown_id` | Flagged as unmapped relative to this snapshot. No heuristic guessing. |
| **Malformed Identifier** | String fails regular expression `^GO:\d{7}$` | `null` | `null` | `unresolved_malformed_id` | Preserved verbatim in `raw_annotation_text`. Flagged as malformed. |
| **Source / Ontology Aspect Conflict** | Source declared aspect (e.g. `BP`), but ontology maps to different namespace (e.g. `MF`) | `GO:XXXXXXX` | Ontology namespace | `conflict_source_ontology_aspect_mismatch` | **Quarantine**: Source aspect retained. Record flagged for curatorial review; not silently coerced. Evaluated strictly over the **200 comparable active rows** having both declared and derived aspects. Non-comparable obsolete rows (8 rows) have `derived_aspect = null` (conflict check not applicable). Zero conflicts observed ($0/200 = 0.0\%$). |

### 5.2 Mandatory Prohibitions & Scientific Guardrails
In accordance with [`AGENTS.md`](../../AGENTS.md) §5:
1. **No Qualifier Inference**: Never assign default qualifiers (`enables`, `involved_in`, `located_in`, `NOT`). If source lacks qualifiers, qualifier fields remain null or unassigned.
2. **No Graph Enrichment / True Path Expansion**: Do not add ancestor terms, parent terms, or root terms. Mapping is strictly 1:1 term-to-aspect lookup.
3. **No Claim Consolidation**: Every row in `source_go_annotations_pilot.csv` produces exactly one row in the derived mapping table. Never group, merge, or collapse distinct source annotations.
4. **No Taxonomic or Identity Repair**: Do not attempt to fix species discrepancies (e.g. `P34788`) within this metadata task.
5. **No Cross-Protein Claim Transfer**: Mappings apply strictly to the specific protein annotation in which they were cited.

---

## 6. Target Output Location & Data Contract

### 6.1 Isolated Output Directory
To protect the historical P3/P4 baseline:
- **Output Directory**: `data/interim/pilot/quickgo_slice_enriched/`
- **Output Artifact**: `derived_source_go_aspects_pilot.csv`
- **Output Schema**: `data/curated/derived_source_go_aspects.schema.json`
- **Output Manifest**: `data/interim/pilot/quickgo_slice_enriched/manifest.json`
- **Historical Immutability**: Zero modifications to `data/interim/pilot/quickgo_slice/` or `data/interim/pilot/source_go_annotations_pilot.csv`.

### 6.2 Output Table Schema (`derived_source_go_aspects_pilot.csv`)

| Column Name | Type | Nullable | Description & Constraints |
|---|:---:|:---:|---|
| `annotation_id` | string | No | Foreign key matching `source_go_annotations_pilot.csv` (`MFP:SGA:...`). |
| `protein_id` | string | No | Canonical hash identifier (`MFP:U:...`). |
| `source_id` | string | No | Source database (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`). |
| `source_record_id` | string | No | Native source record key. |
| `source_go_id` | string | No | Verbatim cited GO identifier from source. |
| `source_declared_aspect` | string | Yes | Verbatim source-declared aspect (`BP`, `CC`, `MF`, `unassigned`, or null). |
| `resolved_go_id` | string | Yes | Canonical primary GO identifier from ontology; null if unresolved/malformed. |
| `derived_aspect` | string | Yes | Derived namespace: `BP`, `CC`, `MF`, or null. |
| `mapping_status` | string | No | Explicit status enum (see §5.1). |
| `term_name_resolved` | string | Yes | Official term name from ontology snapshot. |
| `ontology_release` | string | No | Recorded release version string (e.g. `releases/2026-01-23`). |
| `ontology_sha256` | string | No | Pinned SHA-256 digest of the ontology file used for lookup. |
| `mapping_timestamp` | string | No | ISO 8601 UTC execution timestamp. |
| `notes` | string | Yes | Diagnostic notes regarding obsoletion, alt_id, or curatorial conflicts. |

---

## 7. Decoupled Staging: Minimum Enrichment vs. Subsequent Recomparison

To isolate experimental variables and avoid confounding metadata validation with concordance metrics, this specification enforces strict two-stage decoupling:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        STAGED EXTENSION WORKFLOW                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   STAGE 1: MINIMUM ENRICHMENT (Task PIL-04.1A)                         │
│   • Input: Frozen source annotations + Pinned go-basic.obo             │
│   • Action: Generate derived_source_go_aspects_pilot.csv               │
│   • Validation: 100% trace backward linkage; schema adherence          │
│   • Acceptance Gate: Human review of mapping table & unresolved cases  │
│                                                                        │
│                                  │                                     │
│                                  ▼ (Requires Separate Sign-Off)        │
│                                                                        │
│   STAGE 2: CONCORDANCE RECOMPARISON (Task PIL-04.1B - DEFERRED)        │
│   • Input: Enriched aspects + QuickGO capture                          │
│   • Action: Run concordance engine with derived aspect inputs          │
│   • Output: quickgo_concordance_pilot_v1.1.csv (in separate directory) │
│   • Evaluation: Evaluability shift and paired Policy B vs C analysis   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 7.1 Stage 1: Minimum Enrichment (`PIL-04.1A`)
- **Deliverable**: `derived_source_go_aspects_pilot.csv` and validation report.
- **Scope**: Deterministic ontology lookup only.
- **Merit**: Bounded, fast, zero risk of metric gaming. Evaluates strictly whether terms exist, whether secondary IDs are tracked, and whether aspect namespaces are deterministically resolved.

### 7.2 Stage 2: Concordance Recomparison (`PIL-04.1B`) — **DEFERRED**
- **Rationale for Deferral**:
  1. **Separation of Concerns**: Verifying ontology lookup accuracy must precede using those lookups in concordance pipelines.
  2. **Preventing Metric Gaming**: Acceptance of metadata enrichment must be based on curatorial and ontological correctness, **NOT on whether Jaccard scores increase or whether more rows become evaluable**.
  3. **Preserving Presentation Timeline**: Route A communication and slide decks describe the baseline pilot (with its 72.2% non-evaluability). Re-running concordance prematurely risks confusing baseline reporting with experimental extensions.
- **Authorization**: Neither Stage 1 nor Stage 2 is authorized for implementation at this time.

---

## 8. Separation of Metadata Enrichment from Evaluability Assessment

In accordance with user authorization for Task PIL-04.1A:
- **No Evaluability Predictions**: Post-enrichment concordance evaluability depends on concordance rules, slice boundaries, and identity resolutions that belong strictly to Task PIL-04.1B (which remains deferred).
- **No Score Computation**: Zero Jaccard similarities, zero concordance matrices, and zero evaluability transitions are computed or claimed in this increment.
- **Independent Orthogonal Gates**: The Stage P4 descriptive analysis documented that non-evaluability in the pilot was driven by multiple distinct causes (MoonProt aspect indeterminacy, `P34788` botanical identity discrepancy, `A0A0H3CDS3` slice boundaries, and empty source inventories). Resolving ontology namespaces does not alter or remediate those independent orthogonal barriers.
- **Evaluation Metric**: Acceptance for PIL-04.1A is based exclusively on mapping contract correctness, schema adherence, backward traceability, and deterministic stability across the 353 annotation rows.

---

## 9. Acceptance Criteria & Implementation Prerequisites

### 9.1 Acceptance Criteria for Task PIL-04.1A (Stage 1)
When authorized for execution, `PIL-04.1A` must satisfy all criteria:
1. **Complete Inventory Traceability**: Exactly 353 rows processed; 100% of rows match an existing `annotation_id` in `source_go_annotations_pilot.csv`.
2. **Immutable Source Preservation**: `source_go_id` and `source_declared_aspect` match raw inputs byte-for-byte.
3. **Structured Mapping Status**: 100% of rows assigned an explicit `mapping_status` enum value. Zero unhandled exceptions.
4. **Secondary Identifier Safety**: Terms matching `alt_id` have `source_go_id` preserved, `resolved_go_id` set to canonical primary ID, and status set to `resolved_secondary_alt_id`.
5. **Obsolete Term Protection**: Zero `consider:` tags accepted as automated equivalences.
6. **Isolated Outputs**: Outputs written strictly to `data/interim/pilot/quickgo_slice_enriched/`. Zero modifications to historical P1–P4 files.
7. **Offline Bitwise Stability**: Two consecutive runs produce bit-identical CSV files matching the execution manifest.
8. **Schema Validation**: Output CSV passes Draft 2020-12 JSON Schema validation.

### 9.2 Execution Prerequisites
Implementation must not commence until:
1. Human sign-off is granted on this specification (`SPEC-PIL-04.1-GO-ASPECT-ENRICHMENT`).
2. Human maintainers approve the pinned ontology snapshot (Candidate 1: `releases/2026-01-23` or an authorized external archive download).
3. A formal implementation task package (`plan.md`, `tasks.md`, `verification.md`) is approved under repository SDD rules.
4. Working tree baseline is verified and clean of conflicting uncommitted changes.
