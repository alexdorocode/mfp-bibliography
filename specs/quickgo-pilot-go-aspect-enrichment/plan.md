# Plan: Minimum GO-Aspect Metadata Enrichment (Task PIL-04.1A)

- **Document ID**: `PLAN-PIL-04.1-GO-ASPECT-ENRICHMENT-001`
- **Task Identifier**: `PIL-04.1A` (Route B Increment)
- **Specification Reference**: [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](spec.md)
- **Status**: Executed & Completed Implementation Plan (2026-11-16; Technical Commit: `98530b32cd13d0b8ff5b4ea7a626e691d9426d25`)
- **Authority Level**: Level 5 (Increment Plan)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Staged Execution Strategy

The implementation proceeds in 5 discrete, sequential stages:

```
Stage 1: Contract Schema
  └─ Author data/curated/derived_source_go_aspects.schema.json (Draft 2020-12)
       │
Stage 2: Core Enrichment Engine & OBO Parser
  └─ Implement src/mfp_bibliography/go_aspect_enrichment.py
       │
Stage 3: Comprehensive Test Suite & Synthetic Fixtures
  └─ Implement tests/fixtures/test_go_aspect_enrichment/test_ontology.obo
  └─ Implement tests/test_go_aspect_enrichment.py
       │
Stage 4: CLI Runner & Isolated Execution
  └─ Implement scripts/build_go_aspect_enrichment.py
  └─ Execute offline to generate data/interim/pilot/quickgo_slice_enriched/
       │
Stage 5: Verification Record & Handoff
  └─ Verify acceptance criteria and generate specs/quickgo-pilot-go-aspect-enrichment/verification.md
```

---

## 2. Explicit Write Boundaries & Authorized File Paths

In accordance with [`AGENTS.md`](../../AGENTS.md) §4.2, modifications are strictly confined to these authorized paths:

### 2.1 Specification Package
1. `specs/quickgo-pilot-go-aspect-enrichment/spec.md` (updated with verified counting clarifications)
2. `specs/quickgo-pilot-go-aspect-enrichment/plan.md`
3. `specs/quickgo-pilot-go-aspect-enrichment/tasks.md`
4. `specs/quickgo-pilot-go-aspect-enrichment/verification.md`

### 2.2 Contract Schema
5. `data/curated/derived_source_go_aspects.schema.json`

### 2.3 Implementation Module
6. `src/mfp_bibliography/go_aspect_enrichment.py`

### 2.4 CLI Runner
7. `scripts/build_go_aspect_enrichment.py`

### 2.5 Test Fixtures & Suites
8. `tests/fixtures/test_go_aspect_enrichment/test_ontology.obo`
9. `tests/test_go_aspect_enrichment.py`

### 2.6 Generated Artifacts (Isolated Run Directory)
10. `data/interim/pilot/quickgo_slice_enriched/derived_source_go_aspects_pilot.csv`
11. `data/interim/pilot/quickgo_slice_enriched/manifest.json`

> [!CAUTION]
> **Prohibited Write Scope**:
> - NO modifications to historical P1–P4 files under `data/interim/pilot/quickgo_slice/`.
> - NO modifications to historical schemas in `data/curated/`.
> - NO modifications to `src/mfp_bibliography/quickgo_concordance.py` or existing tests.
> - NO modifications to candidate releases (`releases/`) or raw data (`data/raw/`).
> - NO git staging, commits, or branch operations.

---

## 3. Component Architecture & Detailed Design

### 3.1 Input Contract & Cardinality
- **Primary Input**: `data/interim/pilot/source_go_annotations_pilot.csv` (SHA-256: `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda`).
- **Exact Input Cardinality**: Exactly 353 annotation rows.
- **Row-Preserving Output Cardinality**: Exactly 353 emitted data rows (1:1 preservation).
- **Scope Justification**: By processing all 353 source annotation rows, the engine:
  1. Enriches unassigned/null annotations (141 MoonProt rows, 4 MultitaskProtDB-II rows).
  2. Verifies consistency of declared annotations (95 MultitaskProtDB-II rows, 113 PlantMP rows).
  3. Guarantees 100% backward traceability to Tier A claims without loss of rows.

### 3.2 OBO Parser & Lookup Architecture
`src/mfp_bibliography/go_aspect_enrichment.py` will implement:
1. `OntologySnapshot`: An immutable in-memory lookup index parsed from an OBO 1.2 file:
   - `terms`: Map of `id -> TermRecord(name, namespace, is_obsolete, alt_ids, replaced_by, consider)`
   - `alt_map`: Map of `alt_id -> primary_id`
   - `metadata`: `format_version`, `data_version`, `source_path`, `sha256_digest`.
2. `parse_obo_ontology(path: Path, expected_sha256: Optional[str]) -> OntologySnapshot`:
   - Validates file exists and checks cryptographic SHA-256 digest before parsing.
   - Extracts term definitions, obsolete flags, alt_ids, replaced_by, and consider tags.
3. `enrich_annotation_row(row: Dict[str, str], ontology: OntologySnapshot) -> Dict[str, Any]`:
   - Enforces conservative mapping semantics (§4 of spec):
     - `resolved_primary`: term is active primary; aspect derived from namespace.
     - `resolved_secondary_alt_id`: term is alternate ID; primary resolved; source preserved verbatim.
     - `obsolete_replaced_by`: term is obsolete with replaced_by; replacement recorded in metadata; `resolved_go_id` is null (not automatically substituted); derived aspect is null.
     - `obsolete_unreplaced`: term is obsolete without replacement; consider tags recorded in metadata (never treated as equivalences); derived aspect is null.
     - `unresolved_unknown_id`: term absent from snapshot; resolved to null.
     - `unresolved_malformed_id`: term fails `^GO:\d{7}$`.
     - `conflict_source_ontology_aspect_mismatch`: source declared aspect conflicts with ontology namespace; retained without overwrite; flagged for human review.
4. `build_derived_aspects_table(input_path: Path, ontology: OntologySnapshot) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]`:
   - Processes all rows sequentially, preserving input order.
   - Emits structured summary statistics.

---

## 4. Testing Strategy

1. **Schema Check Tests**:
   - Verify `derived_source_go_aspects.schema.json` is a valid Draft 2020-12 schema.
2. **Synthetic Fixture Unit Tests** (`test_ontology.obo`):
   - Active primary term $\to$ `resolved_primary`.
   - Alternate ID $\to$ `resolved_secondary_alt_id` (primary resolved, source preserved).
   - Obsolete term with `replaced_by` $\to$ `obsolete_replaced_by` (not substituted as resolved_go_id).
   - Obsolete term with `consider` $\to$ `obsolete_unreplaced` (consider tags recorded, never substituted).
   - Unknown GO ID $\to$ `unresolved_unknown_id`.
   - Malformed GO ID $\to$ `unresolved_malformed_id`.
   - Source aspect conflict $\to$ `conflict_source_ontology_aspect_mismatch`.
3. **Traceability & Integrity Tests**:
   - 100% of rows match input `annotation_id`.
   - `source_go_id` and `source_declared_aspect` match input byte-for-byte.
   - Cardinality check: exactly 353 rows emitted.
   - Output validation against JSON schema.
   - Deterministic serialization (repeated runs produce bit-identical files).
