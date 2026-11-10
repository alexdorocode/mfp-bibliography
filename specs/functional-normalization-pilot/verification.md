# Verification: Functional-Normalization SDD Package and Governance Baseline

- **Document ID**: `VERIF-001-FUNCTIONAL-NORMALIZATION-PILOT`
- **Specification Reference**: [`specs/functional-normalization-pilot/spec.md`](spec.md)
- **Plan Reference**: [`specs/functional-normalization-pilot/plan.md`](plan.md)
- **Tasks Reference**: [`specs/functional-normalization-pilot/tasks.md`](tasks.md)
- **Status**: Check 1 (TASK-01), Check 2 (TASK-02), Check 3 (TASK-03), and Check 4a (TASK-04) executed and **PASSED** under scoped authorization. Data-preservation review completed. Checks 4b to 8 remain **NOT RUN** (subsequent tasks strictly unauthorized).

---

## 1. Documentation Checks Performed

The following static document and structural checks were completed and verified:

| Check ID | Target Artifact | Verification Rule | Outcome |
|---|---|---|---|
| **DOC-CHK-01** | `AGENTS.md` | Grounded in accepted ADRs; establishes 3-level operational boundaries; clarifies SHA-256 digests as deterministic one-way digests (not reversible); defines reading order, English language mandate, scientific invariants, prohibited autonomous actions, and required handoff format. No gate-numbering inventions. | **PASSED** |
| **DOC-CHK-02** | `docs/decisions/ADR-008-functional-normalization-pilot-scope.md` | Uses sequential identifier (`ADR-008`); status is `Proposed`; documents that ADR-007 was a milestone-specific exclusion for `mfp_catalog_v1` rather than a permanent ban; establishes 3 decoupled decision levels; strictly preserves catalog baseline. | **PASSED** |
| **DOC-CHK-03** | `specs/functional-normalization-pilot/spec.md` | Status is `Draft for human review`; establishes 6 epistemological levels; details dimensional analysis (Axes A, B, C); resolves MultifacetedProtDB float score discrepancy; separates Tiers A, B, C; integrates Normalized Protein Dossier as a downstream view with 4 orthogonal flags; defines relational `functional_claims` and `functional_coverage` contracts; defines total 5-tuple tie-breaking key. | **PASSED** |
| **DOC-CHK-04** | `specs/functional-normalization-pilot/plan.md` | Details staged pilot strategy (Stages P0 to P4); justifies MultitaskProtDB-II as Stage P2 first offline vertical slice; defines dual-check integrity invariant separating release package verification (`package_catalog_candidate.py --verify-package`) from working catalog file integrity (`validate_catalog_integrity`); reuses normalization helpers; defers heavy dependencies; defines human approval gates. | **PASSED** |
| **DOC-CHK-05** | `specs/functional-normalization-pilot/tasks.md` | Eight finely scoped sequential tasks (TASK-01 to TASK-08); records completion of TASK-01, TASK-02, and TASK-03; keeps subsequent tasks strictly unauthorized. | **PASSED** |
| **DOC-CHK-06** | Git Working Tree | No tracked files restored or modified; no untracked PDFs or research drafts altered; zero commits or staging operations performed; `.gitignore` updated strictly to unignore curated schemas without broadly unignoring `data/`. | **PASSED** (Verified via `git status`) |

---

## 2. Audit Overreach, Unverified Claims, and Risk Register

The technical audit report (`docs/audits/2026-11-06_repository-sdd-functional-normalization-audit.md`) provided extensive valuable analysis. However, as an advisory document, several of its recommendations and cited metrics contain unverified assumptions, draft proposals, or overreach that must be explicitly quarantined:

### 2.1 MultifacetedProtDB Numeric Score vs Functional Text Discrepancy
- **Audit Statement / Early Draft Assumption**: The audit report and early research drafts treated MultifacetedProtDB's `annotation` field as an unsegmented text string of functional claims requiring natural language parsing or dictionary segmentation.
- **Empirical Reality from Raw Artifact**: Direct static inspection of `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` and `src/mfp_bibliography/multifacetedprotdb_records.py` proves that `annotation` is a **numeric float** (e.g. `5.0`, `4.0`, `3.0`, `2.0`), representing an annotation score or confidence metric. MultifacetedProtDB contains **no discrete functional statements, no GO identifiers, and no literature citations**.
- **Architectural Resolution**: Numeric scores are metadata, not functional claims. Under Requirement `R-NORM-07` and Acceptance Criterion `AC-NORM-02`, MultifacetedProtDB records must be accounted for in `functional_coverage` with `coverage_status = "no_discrete_functional_statements"`, preserving `metadata_annotation_raw = "5.0"`. **Zero fake claims may be fabricated.**

### 2.2 Unapproved Pilot Size, Source Ordering, and Golden Standard Filters
- **Audit Proposal**: The audit recommended a 50-protein consensus cohort based on $\ge 3$ sources, an arbitrary source ranking, and a pinned ontology file `data/raw/ontology/go-basic-2026-10-01.obo`.
- **Clarification**: Neither the 50-protein count, nor the $\ge 3$ source threshold, nor any fixed source hierarchy has been approved by the scientific lead. The user-provided source ranking is a design input, not an approved scientific policy. In implementation, empirical extraction order is driven by data characteristics and technical decoupling: Stage P2 begins with `MultitaskProtDB-II` (tabular, pre-segmented roles, explicit GO aspects), while MultifacetedProtDB exercises the coverage boundary.
- **Candidate "Golden Standard" Filtering**: Strict acceptance criteria (e.g. 100% experimental evidence, known structural domains) represent a candidate filter for future curation subsets in downstream analysis, **not** an entry gate for Tier A source claim preservation.

### 2.3 Proposed Raw File Alterations (Strictly Prohibited)
- **Audit Observation**: The audit flagged filenames with spaces (e.g. `data/raw/plantmp/PlantMP MySQL-confirmed .csv`).
- **Clarification**: Any recommendation to rename, move, or clean files in `data/raw/` is **strictly rejected**. Under [ADR-002](file:///home/alexdoro/repositories/mfp-bibliography/docs/decisions/ADR-002-raw-data-immutability.md), all files under `data/raw/` are immutable append-only artifacts pinned by SHA-256 in `source_manifest.csv`. Inconvenient filenames must be handled via programmatic path mapping or adapter logic, never by modifying raw files.

### 2.4 QuickGO Qualifier Loss vs Schema Columns
- **Audit Note**: The audit noted the critical loss of `NOT` qualifiers in upstream QuickGO data.
- **Clarification**: Merely adding a `qualifier` column to a new JSON Schema does **not** reconstruct previously lost information from an existing database dump. Unless a fresh re-extraction from QuickGO with qualifier preservation is authorized, historical annotations lacking explicit qualifier confirmation must be treated with documented caveats or quarantined as unverified.

### 2.5 Triplet Semantics and Working Glossary Definitions
- **Audit Proposal**: The audit's glossary proposed a formal definition of a functional triplet as $\tau = (m, b, c)$.
- **Clarification**: Under roadmap `experiment-guio-v2.md`, the formal definition of a triplet is an **explicit open decision (DEC-22)** assigned to Decision Gate G2. Defining it in an audit glossary does not constitute biological consensus or operational approval. Contextual triplets remain strictly out of scope for the Tier A pilot.

### 2.6 Downstream Normalized Protein Dossier Integration
- **Proposal**: An IDE/VS Code inspection dossier panel displaying identity, claims, citations, and GO crosswalks.
- **Clarification**: The dossier is accepted as a **downstream, read-only inspection view**. It must never displace tabular claim normalization or serve as an ingestion gate. Four orthogonal eligibility flags (`preservation_valid`, `go_reconciliation_eligible`, `contextual_triplet_candidate`, `high_evidence_profile_eligible`) decouple Tier A preservation from downstream biological criteria. Missing taxonomy or sequence hashes must never block Tier A claim preservation.

---

## 3. Implementation Verification Checklist

```markdown
### Verification Checklist

- [x] Check 1: Schema Syntax Check (TASK-01 / Contract Extension)
      Command: python3 -c "import json, jsonschema; [jsonschema.Draft202012Validator.check_schema(json.load(open(p))) for p in ['data/curated/functional_claims.schema.json', 'data/curated/functional_coverage.schema.json', 'data/curated/source_go_annotations.schema.json']]"
      Status: PASSED (Draft 2020-12 valid syntax confirmed for all three schemas)

- [x] Check 2: Schema & Contract Unit Tests (TASK-02 / Contract Extension)
      Command: PYTHONPATH=src pytest -v tests/test_functional_contracts.py tests/test_source_go_annotations_contract.py
      Status: PASSED (77 tests passed: 33 functional contracts + 44 source annotation contracts)

- [x] Check 3: MultitaskProtDB-II Adapter & Slice Builder Unit Tests (TASK-03)
      Command: PYTHONPATH=src pytest -v tests/test_functional_claims_multitask.py tests/test_build_multitask_slice.py
      Status: PASSED (23 tests passed: 21 adapter tests + 2 slice builder tests; 6 real rows and 8 synthetic edge cases validated)

- [x] Check 3b: Persistent Package Byte-Reproducibility & Verification (TASK-03)
      Command: PYTHONPATH=src python3 scripts/build_multitask_slice.py
      Status: PASSED (Package generated twice in separate temporary directories; 100% byte-identical SHA-256 digests across claims.csv, source_go_annotations.csv, coverage.csv, and manifest.json; published to data/interim/pilot/multitask_slice/)

- [x] Check 4a: PlantMP Tabular Adapter & Unit Tests (TASK-04)
      Command: PYTHONPATH=src pytest -v tests/test_functional_claims_plantmp.py
      Status: PASSED (30 tests passed: 7 real rows and 9 synthetic edge cases validated; native status, BP/MF grouping without independent function assumption, record references, source GO annotations without CC, and total ordering verified)

- [ ] Check 4b: Adapter Unit Tests for Remaining Sources (TASK-05 to TASK-06)
      Command: pytest tests/test_functional_claims_*.py
      Status: NOT RUN (implementation not authorized; awaits Decision Gate 2)

- [ ] Check 5: Pipeline Execution Gate (TASK-07)
      Command: PYTHONPATH=src python scripts/build_functional_claims_pilot.py
      Status: NOT RUN (implementation not authorized; awaits Decision Gate 2)

- [ ] Check 6: Catalog Baseline Invariant Verification (TASK-07 / TASK-08)
      Command 6a (Candidate release): PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
      Command 6b (Working catalog): python scripts/validate_catalog_integrity.py (or test equivalent)
      Status: NOT RUN (implementation not authorized)

- [ ] Check 7: Byte-Reproducibility Verification (TASK-08)
      Command: Compare SHA-256 of functional_claims_pilot.csv and functional_coverage_pilot.csv across PYTHONHASHSEED=0 and 42
      Status: NOT RUN (implementation not authorized)

- [ ] Check 8: Downstream Dossier Inspection Verification
      Command: PYTHONPATH=src python scripts/render_protein_dossier.py --protein-id MFP:U:P04406 --dry-run
      Status: NOT RUN (implementation not authorized)

- [ ] Check 9: Repository Scaffold Validation
      Command: python scripts/validate_repository.py
      Status: NOT RUN (implementation not authorized)
```

---

## 4. What Has and Has Not Been Demonstrated

### 4.1 What Has Been Demonstrated
1. **Valid Draft 2020-12 Schemas**: All three schemas (`functional_claims.schema.json`, `functional_coverage.schema.json`, and `source_go_annotations.schema.json`) compile without errors and enforce field constraints, types, and closed object validation (`additionalProperties: false`).
2. **Schema Visibility in Version Control**: `.gitignore` was updated strictly to unignore curated schemas (`!data/curated/*.schema.json`) without broadly unignoring `data/`. `git check-ignore` exits with code 1 ("not ignored") and `git status` displays them as tracked/untracked candidates.
3. **MultitaskProtDB-II Production Adapter**: `src/mfp_bibliography/functional_claims_multitask.py` successfully extracts claims, structured source GO annotations, and coverage from MultitaskProtDB-II CSV format, correctly mapping roles to `Canonical_Function` and `Moonlighting_function`.
4. **Reference Granularity & Exact Preservation Invariant**: MultitaskProtDB-II citations are strictly stored in `record_reference_ids` without artificial `PMID:` prefix injection (e.g. `24814782`, `11111111, 22222222`, `HIV-1...`), with `linked_reference_ids = None`.
5. **Real-Source-Derived Extraction**: A 6-row real extract (`multitask_real_extract.csv`, including Row 672 / `Q9Y3E5`) was extracted and tested, generating 12 claims, 45 source GO annotations, and 6 coverage records that all validate 100% against JSON Schemas.
6. **Edge Case Handling**: Verified handling of missing statements, empty `GO_Moon`, invalid accessions (`unresolved_identity`), multi-reference strings, missing function text with explicit GO data, and multiple annotations with repeated GO IDs and distinct evidence (`multitask_synthetic_edge_cases.csv`).
7. **Structured Source GO Annotations**: Implemented `source_go_annotations.schema.json` and adapter support preserving each annotation occurrence with verbatim raw fragment, explicit GO ID, aspect (`BP`, `MF`, `CC`, or unassigned), term name, evidence code (`IEA`, `IDA`), and optional claim linkage (`claim_id = null` when text is absent).
8. **Source-Explicit CC Preservation**: Row 672 confirms that CC explicitly present in `GO_Moon` (e.g. `GO:0005654` nucleoplasm) is preserved as a source assertion on moonlighting claims and in `source_go_annotations`, while canonical CC annotations are strictly excluded from moonlighting.
9. **Deterministic Total Ordering**: Emitted claims follow the 5-tuple tie-breaking sort key `(protein_id, source_id, source_record_id, claim_index, claim_id)`. Emitted annotations follow the 6-tuple sort key `(protein_id, source_id, source_record_id, source_field, annotation_index, annotation_id)`. Emitted coverage follows `(protein_id or "", source_id, source_record_id)`.
10. **Denominator Accounting**: 100% denominator coverage consistency is maintained across records and claims.
11. **Persistent Six-Record Package Generation**: `scripts/build_multitask_slice.py` generated the verified package under `data/interim/pilot/multitask_slice/`: `claims.csv` (12 claims), `source_go_annotations.csv` (45 annotations), `coverage.csv` (6 records), `manifest.json`, and `verification_report.json`.
12. **Byte-Stability & Reproducibility**: Proved 100% byte-identical reproduction across independent runs in separate temporary directories (identical SHA-256 digests for all deterministic files).
13. **Catalog Linkage Verification**: All 6 real records resolve against `data/processed/mfp_catalog_mvp/mfp_source_records.csv` without fallback identities.
14. **PlantMP Bounded Adapter, Identity Correction & Offline Suite (TASK-04)**: `src/mfp_bibliography/functional_claims_plantmp.py` extracts claims, structured source GO annotations (`MFPB_SOURCE_GO_ANNOTATION_V1`), and coverage adhering strictly to contracts. 39 unit tests pass offline (`tests/test_functional_claims_plantmp.py`), proving: (a) native canonical/moonlighting roles and pre-split raw fields preserved; (b) BP/MF statements grouped without assuming independent biological functions; (c) curation tiers mapped strictly per policy (`confirmed` -> `curated`, `likely` -> `unresolved` / `excluded_likely`, `predicted` -> `predicted`); (d) record-level references preserved verbatim in `record_reference_ids` without synthetic `PMID:` prefix; (e) unavailable metadata (`source_ec_number`, `term_name`, `evidence_raw`) remains `null`; (f) zero cellular component (CC) terms inferred and zero triplets constructed; (g) missing text with explicit GO annotations handled without fabricating fake text claims; (h) total tie-breaking determinism and 100% denominator coverage; (i) elimination of fabricated sentinel entity `MFP:U:0000000000000000`; (j) catalog verification and elimination of silent promotion for valid-looking accessions absent from catalog; (k) catalog linkage agreement enforcement; (l) preservation of legitimate shared entities across duplicate source records; (m) accounting of unresolved records without fake claims or annotation foreign keys; (n) focused negative tests (missing accession, malformed accession, absent from catalog, mismatched linkage, multiple unresolved not collapsed); (o) conditional nullability verification under Draft 2020-12 coverage schema (honest null for `unresolved_identity`, regex pattern for resolved statuses, rejection of non-null unresolved, null resolved, missing, empty, malformed, and uncataloged IDs).
15. **MultitaskProtDB-II Coverage Contract Alignment**: `src/mfp_bibliography/functional_claims_multitask.py` was updated to replace the legacy sentinel `MFP:U:0000000000000000` with honest `protein_id = None` on `unresolved_identity`, and to sort coverage by `protein_id or "" ASC`. All 21 tests in `tests/test_functional_claims_multitask.py` pass without error.

### 4.2 What Has NOT Been Demonstrated
1. **Full-Source Dataset Extraction**: The adapters have not been run across the complete datasets (`proteins.csv` 694 rows or `PlantMP_all.csv` 112 rows) for persistent dataset publishing; only bounded fixture slices were verified.
2. **Adapters for Remaining Sources**: MoonProt adapter implementation (TASK-05) was deferred and not implemented under this instruction. No adapter logic was written for MoonProt, MoonDB, or MultifacetedProtDB (TASK-05 and TASK-06 remain unauthorized/deferred).
3. **Integrated Pilot Pipeline**: `scripts/build_functional_claims_pilot.py` was not created or executed (TASK-07 remains unauthorized).
4. **Catalog Baseline Verification**: Candidate release package verification (`package_catalog_candidate.py --verify-package`) was not run because no integrated pipeline was executed.
5. **Ontology Reconciliation**: No GO crosswalk, OBO mapping, or semantic distance calculations were performed (Tier B / Phase D0 deferred).
6. **Biological Assertion Truth or Atomic Triplet Validation**: No claim of biological truth or verified atomic triplet generation is made.

---

## 5. Contract Nuances, Resolutions, and Boundary Gaps

1. **Total Tie-Breaking Sort Key**:
   - `spec.md` Section 5.4 was updated to adopt explicit tie-breaking keys:
     - Claims (5-tuple): `(protein_id ASC, source_id ASC, source_record_id ASC, claim_index ASC, claim_id ASC)`.
     - Annotations (6-tuple): `(protein_id ASC, source_id ASC, source_record_id ASC, source_field ASC, annotation_index ASC, annotation_id ASC)`.
     - Coverage (3-tuple): `(protein_id or "" ASC, source_id ASC, source_record_id ASC)`.
     This guarantees total determinism even when multiple records from the same source describe the same protein entity or have unresolved identities.
2. **Multivalue & Verbatim Reference Preservation**:
   - Original `Reference` values survive exactly at the extracted-field level without synthetic prefixing (no artificial `PMID:` prepending). Verbatim strings (e.g. `24814782`, `11111111, 22222222`, `HIV-1 and murine leukemia virus infection (omim:600534)`) are preserved intact in `record_reference_ids`, with anomalous non-numeric references flagged in `notes`.
3. **Missing Function Text with Explicit GO Annotations (Resolved via Contract Extension)**:
   - When a source record has a populated `GO` field but empty `Canonical_Function` text:
     - `functional_claims` emits zero fake text claims, preserving `raw_claim_value` non-nullability.
     - `source_go_annotations` emits the structured annotation records with `claim_id = null`, preserving the source observations structurally without loss.
     - `functional_coverage` notes the presence of unextracted annotations in `notes`.
4. **Structured Evidence Code Preservation**:
   - Rather than relying solely on claim `notes`, evidence codes (e.g. `IEA:UniProtKB-KW`, `IDA:HPA`) are preserved in dedicated `evidence_raw` fields in `source_go_annotations.csv`.
5. **Null vs Empty-String Representations in RFC 4180 CSV**:
   - In JSON, absent values are represented by explicit `null`. String fields enforce `minLength: 1`, rejecting empty strings `""`. In CSV, `null` serializes to `""`, and CSV deserialization converts empty strings in nullable columns back to `None` / `null`.
6. **Known Missing RAW XLSX File and Fixture Integrity**:
   - The test suite in `tests/test_source_claim_policy.py` exhibits a known failure for `data/raw/plantmp/PlantMP MySQL.xlsx` due to a historical checksum entry in `file_checksums.sha256`.
   - Direct investigation confirmed that required PlantMP fixture integrity is unaffected: the authoritative raw artifact registered in `data/manifests/source_manifest.csv` is `data/raw/plantmp/PlantMP_all.csv` (53,366 bytes, SHA-256 `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`, 112 data rows), which exists and matches its manifest digest exactly.
   - All real-source extracts and synthetic edge cases for the PlantMP adapter derive from and validate against this authoritative artifact. Neither the PlantMP adapter nor any pilot fixture relies on `PlantMP MySQL.xlsx`.
7. **Coverage Schema Conditional Nullability Amendment (Resolved)**:
   - `data/curated/functional_coverage.schema.json` was amended using Draft 2020-12 conditional validation:
     - `protein_id` remains in `required` and typed as `["string", "null"]` at the property level.
     - `allOf` condition: if `coverage_status == "unresolved_identity"`, `protein_id` must be `null`; otherwise, `protein_id` must match `^MFP:(U:[0-9a-f]{16}|F:[A-Za-z0-9_]+:[0-9a-f]{16})$`.
     - Missing `protein_id` and empty strings `""` are rejected.
     - Scientific semantics: `unresolved_identity` records processing inability to establish a valid catalog linkage; it does not assert biological non-existence.
   - PlantMP adapter unanchored promotion resolved: row extractor defaults to `allow_unanchored=False`, refusing to promote unanchored accessions without catalog lookup.
   - Comprehensive test suite in `tests/test_functional_contracts.py` (37 passed) and `tests/test_functional_claims_plantmp.py` (39 passed) verifies schema syntax validity/invalidity and catalog referential integrity distinctly. Contract blocker is fully resolved.

---

## 6. Scientific Destination & Gap Assessment for Inspected MultitaskProtDB-II Cases

The MultitaskProtDB-II adapter is a **source-preservation increment (Tier A)**. It does not synthesize validated atomic functional triplets $\tau = (m, b, c)$.

### 6.1 Inspected Real Records Summary

| Row Locator | UniProt | Protein Name | Canonical MF/BP/CC Presence | Moonlighting MF/BP/CC Presence | Reference Type |
|---|---|---|---|---|---|
| `row:1` | `A0A059U5R2` | 60S ribosomal protein L44 | **CC** (GO:0005840), **MF** (GO:0003735), **BP** (GO:0006412) | **BP** only (GO:0008150, GO:0050896); MF and CC absent | `24814782` (verbatim raw numeric, row grain) |
| `row:2` | `A0A0H2Q1X0` | Glutamine synthetase | **MF** (GO:0015930), **BP** (GO:0006537); CC absent | **MF** only (GO:0003674, GO:0005488); BP and CC absent | `20167618` (verbatim raw numeric, row grain) |
| `row:3` | `A0A0H3CDS3` | Bifunctional regulator KidO | **CC** (GO:0016021, GO:0005622), **MF** (GO:0005524); BP absent | **BP** only (GO:0008150, GO:0000003); MF and CC absent | `22014899` (verbatim raw numeric, row grain) |
| `row:55` | `B8GW64` | CTP synthase | **MF**, **BP** present; CC absent | **None** (`GO_Moon` completely empty); text statement only (`Binds to CreS`) | `20817753` (verbatim raw numeric, row grain) |
| `row:239` | `P0ABS8` | DNA polymerase III subunit theta | **CC**, **MF**, **BP** present in `GO` | **None** (`GO_Moon` empty); text statement only | `HIV-1 and murine leukemia virus infection (omim:600534)` (verbatim raw text, row grain) |
| `row:672` | `Q9Y3E5` | Bleomycin hydrolase (Bit1) | **CC** (GO:0005829, GO:0016020, GO:0005739), **MF** (GO:0004185, GO:0008233), **BP** (GO:0006508) | **CC** (GO:0005654 nucleoplasm), **MF** (GO:0003677), **BP** (GO:0006355) | `15297880` (verbatim raw numeric, row grain) |

### 6.2 Gap Assessment

1. **Explicit Functional Contexts**:
   - MultitaskProtDB-II explicitly distinguishes exactly two functional observations: `Canonical_Function` and `Moonlighting_function`.
   - In 683/694 rows, source-explicit GO lines accompany both roles.
2. **Aspect Distribution & Status of Previously Reported Percentages**:
   - *Audit / Exploratory Note*: Earlier handoffs cited preliminary aspect presence percentages across the 694 rows (Canonical: MF 97%, BP 91%, CC 81%; Moonlighting: MF 60%, BP 49%, CC 1.2%).
   - *Provenance & Methodological Limitation*: These numbers were obtained from an ad-hoc, ephemeral shell one-liner executing unanchored substring matching (e.g. `'C:' in text`). They are **unverified exploratory observations**, not certified repository metrics, and must NOT be used for cohort selection or downstream assertions.
   - *Verified Invariant*: CC is very rare in `GO_Moon` (only 8 rows out of 694). When explicitly present (as in Row 672 / `Q9Y3E5`), it is preserved faithfully on the moonlighting claim without copying canonical CC terms.
3. **Context Relationships are Unresolved**:
   - When CC, MF, and BP terms appear together in `GO`, the source provides **no relational linkage** asserting that molecular function $m$ is executed in cellular compartment $c$ during biological process $b$. They are independent co-annotations.
   - Performing a Cartesian product to synthesize triplets $\tau = (m, b, c)$ would fabricate unproven biological assertions in violation of repository governance.
4. **Literature Reference Granularity**:
   - The citation in `Reference` applies to the overall protein entry. It does not provide claim-specific or compartment-specific evidence.
5. **Requirements for Emitting Validated Triplets**:
   - Primary literature verification proving that a specific activity operates within a specific cellular compartment.
   - Controlled vocabulary curation under an approved mapping protocol.
   - Formal adjudication under open decision DEC-22 (Decision Gate G2).

### 6.3 Proposal for Subsequent End-to-End Curation Task

To bridge the gap between Tier A source preservation and validated functional triplets, we propose a subsequent, separately authorized **end-to-end curation task** over a small benchmark cohort (3–5 real proteins):
- **Cohort Selection Criteria**: Select entries exhibiting heterogeneous evidence profiles (e.g. 1 entry with explicit CC in `GO_Moon`, 1 entry with empty `GO_Moon`, 1 entry with complex canonical co-annotations) without making unverified assumptions about dataset-wide completeness.
- **Traceability Chain**: `Source Statement` → `Primary Literature Context Verification` → `GO DAG Mapping (go-basic.obo)` → `Adjudicated Triplet (or explicit incomplete status)`.
- This task should be conducted under a dedicated specification package after completion of the Tier A source adapters.
