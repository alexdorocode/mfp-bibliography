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
  - Unit test suite `tests/test_functional_claims_schema.py` covering synthetic edge cases (single claim, multiple claims, missing fields, numeric scores).
- **Entry Prerequisites**: Formal human approval of ADR-008 Level 2.
- **Exit Evidence**: `jsonschema.Draft202012Validator.check_schema()` passes; synthetic contract tests execute and pass offline.
- **Deferred Behavior**: No parsing of real source files; no adapter implementation.
- **Human Approval Needed**: Formal review and sign-off on authored JSON Schemas.

---

### Stage P2: First Offline Vertical Slice (Recommended Source: MultitaskProtDB-II)
- **Purpose**: Implement and verify a complete, isolated offline vertical slice for a single source exhibiting clean tabular structure and explicit GO term aspects before expanding across sources.
- **First-Source Rationale**:
  - `MultitaskProtDB-II` is the primary candidate because it already separates roles into `Canonical_Function` and `Moonlighting_function`, provides explicit multiline GO strings with native aspects (`C:`, `F:`, `P:`) and IEA evidence codes, and has an existing robust parser (`src/mfp_bibliography/multitaskprotdb_ii_records.py`).
- **Inputs**:
  - Pinned MultitaskProtDB-II fixture records from manifest.
  - Reusable parser `multitaskprotdb_ii_records.py`.
  - Normalization helpers `normalization.py`.
- **Outputs**:
  - Modular adapter `src/mfp_bibliography/functional_claims_multitask.py`.
  - Offline unit tests `tests/test_functional_claims_multitask.py`.
  - Real-source extract and edge-case fixtures in `tests/fixtures/functional_claims_multitask/`.
- **Entry Prerequisites**: Stage P1 schemas and contract tests passing.
- **Exit Evidence**: Generated claims validate 100% against schema; record-level references remain unpromoted to claims; offline verification passes.
- **Deferred Behavior**: No full-source pipeline execution; no writing to `data/interim/pilot/`; no external database connections; no GO DAG distance calculations; no external literature retrieval.
- **Human Approval Needed**: Review of the single-source vertical slice adapter and test suite.

---

### Stage P3: Capability Expansion Across Sources
- **Purpose**: Incrementally expand adapter coverage to exercise distinct source capabilities and boundary conditions:
  1. **PlantMP**: Ingests tabular statements separated by role and aspect (`bp` vs `mf`); tests curation tier separation (`confirmed` vs `predicted`).
  2. **MoonProt**: Ingests dynamic $K$-block functional structures (`functions[0]`, `functions[1]`) and function-specific references (`function.pmids`).
  3. **MoonDB**: Ingests manual curation text statements while cleanly segregating algorithmic predictions (EMF) as `claim_assertion_type = "predicted"`.
  4. **MultifacetedProtDB**: Exercises coverage boundary accounting; ingests records into `functional_coverage` with `coverage_status = "no_discrete_functional_statements"` and float metadata, generating 0 fake claims.
- **Inputs**:
  - Manifest records for PlantMP, MoonProt, MoonDB, MultifacetedProtDB.
  - Existing parsers (`plantmp_claims.py`, `moonprot_parser.py`, `moondb_claims.py`, `multifacetedprotdb_records.py`).
- **Outputs**:
  - Source-specific adapter modules and corresponding unit test suites.
  - Coverage accounting module `src/mfp_bibliography/functional_coverage.py`.
- **Entry Prerequisites**: Stage P2 vertical slice verified and approved.
- **Exit Evidence**: All target capabilities tested with 100% offline unit tests; zero data loss on accession-only records.
- **Deferred Behavior**: External ontology reconciliation and metric divergence.
- **Human Approval Needed**: Review of adapter test results.

---

### Stage P4: Integrated Tier A Review and Handoff
- **Purpose**: Execute an integrated pilot run over the complete pilot manifest, verify 100% denominator accounting, validate deterministic outputs, prove catalog baseline isolation, and package an auditable handoff report.
- **Inputs**:
  - All five source adapters.
  - Pilot cohort manifest.
  - Release verification script `scripts/package_catalog_candidate.py`.
- **Outputs**:
  - Integrated tables: `data/interim/pilot/functional_claims_pilot.csv` and `data/interim/pilot/functional_coverage_pilot.csv`.
  - Validation report: `data/interim/reports/functional_claims_pilot_report.json`.
  - Clean handoff specification for future Tier B (Phase D0/D).
- **Entry Prerequisites**: Stage P3 adapters completed and tested.
- **Exit Evidence**:
  - Byte-identical reproduction across different `PYTHONHASHSEED` runs.
  - Packaged catalog candidate release verification passes (`package_catalog_candidate.py --verify-package`).
  - Processed working catalog verification passes (`validate_catalog_integrity`).
- **Deferred Behavior**: External GO DAG semantic similarity, contextual triplets, BioData background frequency matching.
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
