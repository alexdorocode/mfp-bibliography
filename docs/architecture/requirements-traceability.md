# Requirements Traceability Matrix

Current verified baseline: 2,268 source records (MoonDB 351, MoonProt 702,
MultifacetedProtDB 1,103, PlantMP 112), 2,013 proteins, 184 merges,
`fallback_identity_records=0`, MoonProt coverage 702/1/3 — from
`data/processed/mfp_catalog_mvp/summary.json`.

Statuses: implemented_verified (behavioral test + verifiable output),
implemented_unverified, partial, documented_only, missing, not_applicable_yet.
A requirement is verified only by a specific test and a reproducible output,
never by documentation alone. Maintenance rule: future changes update only the
affected rows and data-flow edges; the roadmap tracks milestones, this matrix
tracks technical satisfaction.

| ID | Requirement | Status | Contract/ADR | Implementation | Test | Output/evidence | Owner module | Next action |
|---|---|---|---|---|---|---|---|---|
| R1 | MF-only scope, no NMF/negative set | implemented_verified | ADR-001, charter | `scripts/build_mfp_catalog_mvp.py` (no label fields) | `test_mfp_catalog_mvp.py::TestReadme`, `test_source_claim_policy.py` | catalog tables contain no MF/NMF labels | build script | none |
| R2 | Source labels preserved verbatim | implemented_verified | source-claims contract | `build_assertions` (original_value) | `test_moondb_claims.py`, `test_plantmp_claims.py` | `mfp_assertions.csv` original_value | build script | none |
| R3 | Record conservation per source | implemented_verified | ADR-003 | `expected_source_record_counts`, `validate_catalog_integrity` | `test_source_record_count_conserved`, `TestIsolatedBuild` | summary counts 351/702/112 | build script | none |
| R4 | Exact-UniProt-only merges | implemented_verified | roadmap rules, ADR-005 | `assign_protein_ids` | `test_exact_uniprot_merges`, `test_no_name_only_merge` | 45 merges | build script | none |
| R5 | Deterministic protein IDs | implemented_verified | ADR-005 | `normalization.make_protein_id_uniprot` (MFPB_PROTEIN_ID_V1) | `TestProteinIdScheme`, `TestCrossProcessDeterminism` | byte-identical rebuilds | `mfp_bibliography.normalization` | none |
| R6 | Fallback identities (valid, source-scoped) | implemented_verified | ADR-005 | `make_protein_id_fallback` | `test_fallback_ids_are_source_scoped_and_stable`, `test_legitimate_acquired_protein_without_uniprot_keeps_fallback_id` | `fallback_identity_records=0` (no data case) | `mfp_bibliography.normalization` | none |
| R7 | Coverage-only absent/unresolved MPIDs | implemented_verified | ADR-006 | `load_moonprot_records`, `build_coverage` | `TestCoverageOnlyMpids` | MPID 103 coverage-only; 702/1/3 | build script | none |
| R8 | FK/PK integrity, no partial publish | implemented_verified | ADR-003 | `validate_catalog_integrity` (pre-write gate) | `TestIntegrityDetection`, `TestPrimaryKeys`, `TestCatalogReferentialIntegrity` | build exits non-zero on failure | build script | none |
| R9 | Computed summary metrics | implemented_verified | ADR-005/006 | `compute_summary_metrics` | `TestSummaryMetrics` | summary.json values computed, not hard-coded | build script | none |
| R10 | Raw provenance per record/file | implemented_verified | ADR-003 | pre-build gate `raw_input_verification.verify_catalog_inputs`; MoonProt `raw_sha256` (record grain, matches artifact index 702/702); MoonDB/PlantMP `raw_file_sha256` (file grain, from source_manifest.csv) | `test_raw_input_verification.py` (valid/mismatch/missing/duplicate), `test_acquired_moonprot_records_carry_raw_provenance` | mfp_source_records.csv: 702/702 match index; 351+112 rows carry raw_file_sha256 | `mfp_bibliography.raw_input_verification` | none |
| R11 | Raw immutability (consumed inputs) | implemented_verified | ADR-002 | build-time gate verifies consumed artifacts vs source_manifest.csv and artifact_index.csv | `test_changed_byte_detected`, `test_build_fails_before_publishing_on_tampered_input` | build exits non-zero before publishing on tampered input | `mfp_bibliography.raw_input_verification` | full file_checksums.sha256 sweep still manual |
| R12 | MoonProt snapshot universe explicit + fail-closed | implemented_verified | snapshot-scope note in catalog README | `MOONPROT_SNAPSHOT_MPID_MIN/MAX` constants reused by loader and `build_coverage`; `validate_moonprot_universe` gate pre-publish | `test_moonprot_universe.py` (boundaries 1/706, out-of-range raw/index/absent, fail-closed preserving outputs) | coverage exactly 1..706; out-of-scope MPIDs fail non-zero with exact IDs | build script | none (706 is snapshot scope, not a permanent maximum) |
| R13 | Source inclusion policy | implemented_verified | source-catalog.md | three adapters only | per-source count tests | Multifaceted/Multitask raw-only, not in catalog | build script | Phase B/C ingestion |
| R14 | GO annotation/evidence/work grains | documented_only | GO contract, ADR-005 FKs | none (no adapter) | none | none | FUTURE | Phase D0 schemas |
| R15 | Evidence-code inventory + cohort views | documented_only | GO contract | none | none | none | FUTURE | implement inventory + views |
| R16 | Lab identifier quarantine | documented_only | GO contract (Catalog linkage) | none | none | none | FUTURE | implement quarantine table |
| R17 | Article-count policy | documented_only | GO contract (Counting contract) | none | none | none | FUTURE | implement counting functions |
| R18 | Release metadata (hashes, scope, version) | documented_only | release-policy.md | precedent: `docs/releases/pre-moonprot-baseline-v0.1.md` | none for MVP release | MVP not a release | FUTURE | Phase E contract |
| R20 | MultifacetedProtDB ingestion into catalog | implemented_verified | profile, ADR-005/006 rules, contract MFPB_0_18_MFP_CATALOG_MVP_V1 | `build_mfp_catalog_mvp.py::load_multifacetedprotdb_records` (binding checks: transformation_id, raw path, manifest hash) + optional `genes_raw`/`annotation_raw` columns | `test_mfp_catalog_mvp.py::TestMultifacetedIntegration`, `test_multifacetedprotdb_records.py` | 1,103 catalog records, 0 evidence claims, 163 overlaps + 940 new proteins, all 1,073 prior IDs unchanged | build script | none |
| R21 | MultitaskProtDB-II interim source-record adapter | implemented_verified | profile; policy `unmapped_sources` | `multitaskprotdb_ii_records.py` + `scripts/build_source_records_multitaskprotdb_ii.py`; raw hash verified vs manifest before parsing | `test_multitaskprotdb_ii_records.py` (BOM/CRLF, repeated accessions, stable row-bound IDs, malformed accession, hash failure, null status, reference anomalies) | 694 interim records, 685 accessions, 3 field-level reference anomalies, evidence claims 0; NOT YET in catalog | `mfp_bibliography.multitaskprotdb_ii_records` | five-source catalog integration |
| R19 | Known-absent ID not a protein | implemented_verified | ADR-006 | coverage-only path | `TestCoverageOnlyMpids`, `test_mpid_103_retained_in_coverage_with_absent_log_provenance` | 103 absent from all entity tables | build script | none |

Notes:
- The historical migration report
  `data/interim/reports/mfp_catalog_mvp_protein_id_migration_v1.csv` contains a
  retired administrative ID (former MPID 103 entity), annotated in
  `mfp_catalog_mvp_protein_id_migration_v1.notes.md`; it is not a protein.
- Repository validation runs in CI (`.github/workflows/ci.yml`: pytest +
  `scripts/validate_repository.py`) but is not invoked inside the catalog
  build; the build enforces its own integrity gate.

Open risks: full-manifest sweep (all raw files in `file_checksums.sha256`) still not
automated, though consumed inputs are gated.
