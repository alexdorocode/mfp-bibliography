# Implementation Plan: Functional-Normalization Pilot

- **Plan ID**: `PLAN-001-FUNCTIONAL-NORMALIZATION-PILOT`
- **Specification Reference**: [`specs/functional-normalization-pilot/spec.md`](spec.md)
- **Status**: Draft for human review
- **Implementation Authorization**: **Not granted** (awaits human sign-off on ADR-008 Level 2)

---

## 1. Staged Pilot Execution Strategy (Stages P0–P4)

To ensure incremental verification, source data enters the pipeline through five discrete planning stages (P0–P4). These stages represent technical planning phases, not a new decision-gate numbering scheme.

```
[Stage P0: Source & Contract Verification]
  └─ Resolve source discrepancies (MultifacetedProtDB), freeze fixture manifest.
       │
[Stage P1: Executable Contract Preparation]
  └─ Author schemas & synthetic positive/negative contract tests. Review gate.
       │
[Stage P2: First Offline Vertical Slice (MultitaskProtDB-II)]
  └─ End-to-end extraction, catalog linkage, validation, and coverage for primary source.
       │
[Stage P3: Capability Expansion Across Sources]
  └─ Incremental integration: PlantMP, MoonProt, MoonDB, and MultifacetedProtDB boundary check.
       │
[Stage P4: Integrated Tier A Review & Handoff]
  └─ Cross-source audit, byte reproducibility, catalog isolation, and handoff to Phase D0.
```

---

### Stage P0: Source and Contract Verification
- **Purpose**: Verify source-field realities directly from local artifacts, resolve documented contradictions (e.g. MultifacetedProtDB numeric score vs text claim), and freeze a small explicit record manifest for pilot testing without arbitrary consensus cutoffs.
- **Inputs**:
  - Raw source artifacts (`data/raw/`).
  - Source profiles (`docs/source-profiles/`).
  - Pre-build gate `raw_input_verification.py`.
- **Outputs**:
  - Verified source-fact inventory (Section 2 of `spec.md`).
  - Pilot record manifest listing exact candidate `source_record_id` and `protein_id` entries across all five sources.
- **Entry Prerequisites**: User instruction authorizing specification revisions.
- **Exit Evidence**: Complete resolution of field types (e.g. MultifacetedProtDB `annotation` verified as float); explicit fixture manifest approved.
- **Deferred Behavior**: No schema writes, no code implementation, no data transformations.
- **Human Approval Needed**: Confirmation of pilot candidate record list.

---

### Stage P1: Executable Contract Preparation
- **Purpose**: Establish machine-enforceable JSON Schemas (`functional_claims.schema.json` and `functional_coverage.schema.json`) and executable contract tests asserting all invariants before writing extraction adapters.
- **Inputs**:
  - `specs/functional-normalization-pilot/spec.md` (data contract definitions).
  - Existing validator helper `src/mfp_bibliography/schemas.py`.
- **Outputs**:
  - `data/curated/functional_claims.schema.json` (Draft 2020-12).
  - `data/curated/functional_coverage.schema.json` (Draft 2020-12).
  - `data/curated/source_go_annotations.schema.json` (Draft 2020-12).
  - Unit test suite `tests/test_functional_contracts.py` and `tests/test_source_go_annotations_contract.py` covering synthetic edge cases (single claim, multiple claims, missing fields, numeric scores, source annotations without text).
- **Entry Prerequisites**: Formal human approval of ADR-008 Level 2.
- **Exit Evidence**: `jsonschema.Draft202012Validator.check_schema()` passes; synthetic contract tests execute and pass offline.
- **Deferred Behavior**: No parsing of real source files; no adapter implementation.
- **Human Approval Needed**: Formal review and sign-off on authored JSON Schemas.

---

### Stage P2: First Offline Vertical Slice (MultitaskProtDB-II Consolidated Slice)
- **Purpose**: Implement and verify a complete, isolated offline vertical slice for a single source exhibiting clean tabular structure, explicit GO term aspects, and structured evidence strings. Consolidate into a persistent, reviewable six-record pilot package.
- **First-Source Rationale**:
  - `MultitaskProtDB-II` is the primary candidate because it already separates roles into `Canonical_Function` and `Moonlighting_function`, provides explicit multiline GO strings with native aspects (`C:`, `F:`, `P:`) and evidence codes (`IEA`, `IDA`), and has an existing robust parser (`src/mfp_bibliography/multitaskprotdb_ii_records.py`).
- **Inputs**:
  - Pinned MultitaskProtDB-II 6-record real extract fixture (`tests/fixtures/functional_claims_multitask/multitask_real_extract.csv`).
  - Local catalog mapping `data/processed/mfp_catalog_mvp/mfp_source_records.csv`.
  - Normalization helpers `normalization.py`.
- **Outputs**:
  - Modular adapter `src/mfp_bibliography/functional_claims_multitask.py` supporting claims, structured source GO annotations, and coverage.
  - Offline slice builder script `scripts/build_multitask_slice.py`.
  - Persistent, verified six-record package under `data/interim/pilot/multitask_slice/`:
    - `claims.csv` (12 claims)
    - `source_go_annotations.csv` (45 annotations)
    - `coverage.csv` (6 coverage records)
    - `manifest.json` (byte-stable manifest)
    - `verification_report.json` (isolated volatile runtime metadata)
  - Offline unit tests:
    - `tests/test_functional_claims_multitask.py` (21 tests)
    - `tests/test_source_go_annotations_contract.py` (44 tests)
    - `tests/test_build_multitask_slice.py` (2 tests)
- **Entry Prerequisites**: Stage P1 schemas and contract tests passing.
- **Exit Evidence**: All 6 real records validate 100% against schemas; double generation in separate temporary directories proves byte-stability; catalog cross-referencing succeeds without fallback identities; offline verification passes.
- **Deferred Behavior**: No full-source pipeline execution; no cohort expansion; no external database connections; no GO DAG distance calculations; no external literature retrieval; no contextual triplets.
- **Human Approval Needed**: Review of the single-source vertical slice adapter, test suite, and persistent package artifacts.

---

### Stage P3: Capability Expansion Across Sources
- **Purpose**: Incrementally expand adapter coverage to exercise distinct source capabilities and boundary conditions:
  1. **PlantMP (Completed under bounded authorization; identity correction verified)**:
     - **Authoritative Input Convention**: Grounded strictly in `data/raw/plantmp/PlantMP_all.csv` (112 data rows, SHA-256 `97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9`), registered in `data/manifests/source_manifest.csv`. Rejects combining overlapping raw exports (e.g. `PlantMP MySQL-all-147.csv`) without explicit deduplication and provenance rules.
     - **Minimal Fixture Scope & Rationale**:
       - Real extract fixture (`plantmp_real_extract.csv`, 7 rows) covers all native status categories (`confirmed`, `likely`, `predicted`), accession normalization with raw non-breaking space (Order 2 / `P92980\xa0`), multi-record shared accessions (Order 62 & 68 / `Q8VYA3`), missing text with explicit GO (Order 64 & 75), and anomalous reference strings (`26638082 (Homolog of POT7)`, `Predicted in 23835195`).
       - Synthetic edge cases (`plantmp_synthetic_edge_cases.csv`, 9 rows) covers single-statement rows, text without GO, 100% empty rows (denominator accounting), missing text with explicit GO (`claim_id = null`), unresolvable accessions (`unresolved_identity`), unmapped native statuses (`disputed`), multi-PMID references, and annotated `likely` references.
     - **Identity Resolution & Catalog Linkage Correction**:
       - Removed fabricated sentinel entity `MFP:U:0000000000000000` emitted on `unresolved_identity`. Emits `protein_id = null` for scientifically honest representation without non-existent entities.
       - Implemented catalog verification: checks presence in supplied catalog lookup, validates row accession syntax, and enforces agreement between catalog entity ID and row accession derivation.
       - Disallowed silent promotion: a syntactically valid accession absent from the supplied catalog is strictly marked `unresolved_identity` (`protein_id = null`, 0 claims, 0 annotations).
       - Preserved legitimate shared entities across duplicate source records (Orders 62 and 68).
       - Ensured multiple unresolved records are not collapsed into a shared fake entity.
     - **Preservation Invariants**:
       - Pre-partitioned BP and MF statements are grouped by functional role (`canonical` vs `moonlighting`) via `group_claims_by_role()` without assuming they represent independent biological functions.
       - Native statuses map per policy: `confirmed` -> `curated`, `predicted` -> `predicted`, `likely` -> `unresolved` (policy `excluded_likely`; never silently promoted to `curated`), unmapped -> `unresolved`. Raw values strictly preserved in `notes`.
       - Record-level references (`pubmed_id`) remain in `record_reference_ids` without artificial `PMID:` prefix injection; `linked_reference_ids = null`.
       - Source GO annotations emitted under `MFPB_SOURCE_GO_ANNOTATION_V1` with native aspects (`BP`, `MF`). Unavailable metadata (`term_name`, `evidence_raw`) remains `null`. No cellular component (CC) terms are inferred, and no contextual triplets are constructed.
     - **Coverage-Contract Amendment & Identity Verification (Completed)**:
       - Contract amendment to `data/curated/functional_coverage.schema.json` implemented via Draft 2020-12 conditional validation:
         - `protein_id` remains in `required` and typed as `["string", "null"]`.
         - When `coverage_status == "unresolved_identity"`, `protein_id` must be `null`.
         - For all other coverage statuses, `protein_id` must match `^MFP:(U:[0-9a-f]{16}|F:[A-Za-z0-9_]+:[0-9a-f]{16})$`.
         - Missing properties and empty strings are rejected.
       - Corrected unanchored promotion: when `catalog_lookup` is omitted and `allow_unanchored` is False, the PlantMP adapter strictly treats unanchored rows as `unresolved_identity` (`protein_id = null`, 0 claims) rather than deriving synthetic unanchored entity IDs. File-level extraction defaults `catalog_lookup` to `load_plantmp_catalog_lookup()`.
       - Verified across 39 PlantMP unit tests and 37 functional contract tests. Blocker fully resolved.
  2. **MoonProt (Completed under bounded authorization)**:
     - **Reusable Existing Parser**: Reuses `MoonProtRecord` and parsing logic from `src/mfp_bibliography/moonprot_parser.py` without creating a redundant HTML parser.
     - **Dynamic K-Block Function Preservation**: Preserves one claim per explicit function block (`functions[0]`, `functions[1]`, ...) without assuming a fixed two-function structure (verified on real-source $K=0$ case MPID 288, $K=1$, $K=2$, and $K=3$ synthetic cases).
     - **Function-Level References**: PMIDs extracted from function blocks are preserved in `linked_reference_ids` with `PMID:` prefix; `record_reference_ids` remains null (MoonProt citations are function-specific).
     - **No Triplet or Compartment Inference**: Cellular location text is preserved in claim notes (`cellular_location: ...`) without inferring cellular component (CC) terms or constructing contextual triplets.
     - **Protein-Level GO Terms Preservation**: Protein-level `GO terms` in MoonProt are NOT distributed across function claims; they are preserved structurally in `source_go_annotations` with `claim_id = null`.
     - **Catalog Linkage & Fallback Entities**: Grounded in authoritative catalog via `load_moonprot_catalog_lookup()` (702 records in `mfp_source_records.csv`). Supports both canonical UniProt entities (`MFP:U:...`) and valid catalog fallback identities (`MFP:F:SRC_MOONPROT:...`).
     - **Honest Null on Unresolved Identity**: Missing/malformed accessions or uncataloged records emit `protein_id = null` and `coverage_status = "unresolved_identity"` with 0 claims/annotations, fully adhering to Draft 2020-12 coverage contract without fabricating sentinels.
     - **Deterministic Total Ordering**: Enforces 5-tuple claim sorting, 6-tuple annotation sorting, and 3-tuple coverage sorting (`protein_id or "" ASC`). Verified across 22 offline tests.
  3. **MoonDB (Unauthorized)**: Ingests manual curation text statements while cleanly segregating algorithmic predictions (EMF) as `claim_assertion_type = "predicted"`.
  4. **MultifacetedProtDB (Unauthorized)**: Exercises coverage boundary accounting; ingests records into `functional_coverage` with `coverage_status = "no_discrete_functional_statements"` and float metadata, generating 0 fake claims.
- **Inputs**:
  - Manifest records for PlantMP (`PlantMP_all.csv`), MoonProt (`data/raw/moonprot/`, `artifact_index.csv`), MoonDB, MultifacetedProtDB.
  - Existing parsers (`plantmp_claims.py`, `moonprot_parser.py`, `moondb_claims.py`, `multifacetedprotdb_records.py`).
- **Outputs**:
  - Bounded adapter `src/mfp_bibliography/functional_claims_plantmp.py` and test suite `tests/test_functional_claims_plantmp.py` (39 tests passing).
  - Bounded adapter `src/mfp_bibliography/functional_claims_moonprot.py` and test suite `tests/test_functional_claims_moonprot.py` (22 tests passing).
  - Coverage schema `data/curated/functional_coverage.schema.json` and contract test suite `tests/test_functional_contracts.py` (37 tests passing).
  - Subsequent source-specific adapter modules and test suites (unauthorized/deferred).
  - Coverage accounting module `src/mfp_bibliography/functional_coverage.py`.
- **Entry Prerequisites**: Stage P2 vertical slice verified and approved; bounded human authorization for PlantMP, coverage contract amendment, MultitaskProtDB-II fix, and MoonProt adapter.
- **Exit Evidence**: PlantMP adapter tested with 100% offline unit tests (39 passed); MultitaskProtDB-II aligned (21 passed); MoonProt adapter tested with 100% offline unit tests (22 passed); schema contract amendment implemented, validated, and verified (37 passed). All 174 tests passing together.
- **Deferred Behavior**: External ontology reconciliation and metric divergence; full-source builds or persistent datasets for PlantMP or MoonProt; MoonDB and MultifacetedProtDB implementation.
- **Human Approval Needed**: Formal review of MoonProt adapter and Stage A/B handoff before proceeding to subsequent sources.

---

### Stage P4: Integrated Tier A Review and Handoff
- **Purpose**: Execute an integrated pilot run over the empirical multi-source cohort, verify 100% denominator accounting, validate deterministic outputs, prove catalog baseline isolation, and package an auditable handoff report.
- **Inputs**:
  - Three authoritative source adapters (MultitaskProtDB-II, PlantMP, MoonProt).
  - Empirical 20-record cohort specification across Multitask (6), PlantMP (8), and MoonProt (6).
  - Release verification script `scripts/package_catalog_candidate.py`.
- **Outputs**:
  - Integrated tables:
    - `data/interim/pilot/functional_claims_pilot.csv` (44 claims)
    - `data/interim/pilot/source_go_annotations_pilot.csv` (353 structured source GO annotations)
    - `data/interim/pilot/functional_coverage_pilot.csv` (20 coverage records)
    - `data/interim/pilot/manifest.json` (byte-stable manifest with SHA-256 digests)
  - Validation report: `data/interim/reports/functional_claims_pilot_report.json`.
  - Comprehensive pipeline unit test suite `tests/test_functional_pilot_pipeline.py`.
- **Entry Prerequisites**: Stage P3 adapters completed and tested.
- **Exit Evidence**:
  - 100% Draft 2020-12 schema validation across all emitted records.
  - Byte-identical reproduction across different `PYTHONHASHSEED` runs (0 vs 42).
  - Packaged catalog candidate release verification passes (`package_catalog_candidate.py --verify-package`).
  - Cross-source shared entity deduplication and total ordering (`MFP:U:8272bae0e8df8149` / `Q42525` across all 3 sources).
- **Deferred Behavior**: External GO DAG semantic similarity, contextual triplets, BioData background frequency matching, MoonDB and MultifacetedProtDB ingestion.
- **Human Approval Needed**: Final human evaluation and sign-off on the completed Tier A pilot.

---

## 2. Reusable Components and Dependency Management

### 2.1 Reusable Repository Components
1. **`mfp_bibliography.normalization`**:
   - `normalize_uniprot_accession()`: Used to clean and uppercase raw accessions.
   - `make_protein_id_uniprot()`: Generates deterministic protein IDs under `MFPB_PROTEIN_ID_V1`.
2. **`mfp_bibliography.raw_input_verification`**:
   - `verify_catalog_inputs()`: Reused to ensure raw artifacts match manifest digests before any processing begins.
3. **`mfp_bibliography.moonprot_parser`**:
   - `MoonProtRecord` and `MoonProtFunctionDetail`: Directly consumed by the MoonProt adapter.
4. **`mfp_bibliography.schemas`**:
   - `build_validator()`: Standard validator builder wrapping `jsonschema.Draft202012Validator`.

### 2.2 Dependency Isolation
- **Active Dependencies**: Pure Python standard library (`csv`, `hashlib`, `json`, `pathlib`, `ast`) + `jsonschema` + `pytest`.
- **Deferred Dependencies**: `psycopg2` (database), `goatools` (ontology DAG), `scipy`/`numpy` (statistical metrics). The pilot requires **zero** dependency additions to `pyproject.toml` or `uv.lock`.

---

## 3. Data Integrity and Baseline Protection

To protect existing releases and working datasets:
1. **Output Directory Isolation**: All pilot outputs are strictly written to `data/interim/pilot/`. Production catalog directories (`data/processed/mfp_catalog_mvp/`) and release directories (`releases/`) are write-protected.
2. **Dual-Check Integrity Invariant**:
   - **Candidate Release Protection**: Executing `scripts/package_catalog_candidate.py --verify-package` checks that packaged release candidate artifacts under `releases/` remain 100% byte-identical.
   - **Working Catalog Integrity**: Executing internal validation checks confirms that working tables in `data/processed/mfp_catalog_mvp/` are untouched.
   - *These two checks test distinct artifacts; passing one does not automatically prove the other.*

---

## 4. Human Approval Gates

The implementation plan is bounded by three explicit human review gates:

1. **Gate 1: Authorization of ADR-008 Level 2**: Authorizes writing schemas to `data/curated/` and creating test files in `tests/`. (Blocks Stage P1).
2. **Gate 2: Contract and Schema Approval**: Authorizes implementing source extraction adapters following schema and contract test review. (Blocks Stage P2).
3. **Gate 3: Pilot Acceptance and Handoff Sign-off**: Authorizes accepting the Tier A pilot results and evaluating progression to Phase D0 (Tier B). (Blocks Stage P4 exit).
