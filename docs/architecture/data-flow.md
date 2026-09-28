# Catalog Data Flow (Current State)

Verified baseline (`data/processed/mfp_catalog_mvp/summary.json`): 2,268 source
records (MoonDB 351, MoonProt 702, MultifacetedProtDB 1,103, PlantMP 112),
2,013 protein entities, 184 exact UniProt merges, coverage 702/1/3.

## Acquisition vs offline transformation

Acquisition (network-dependent, run manually, writes `data/raw/`) is separate
from offline transformation (no network; rebuilds interim/processed outputs
deterministically). The catalog builder never performs acquisition.

```
MoonProt:  acquire_moonprot_smoke.py / acquire_moonprot_batch.py
           → mfp_bibliography/moonprot_client.py (HTTP, mocked in tests)
           → data/raw/moonprot/mpid_*.html
MoonDB:    raw CSV already local → data/raw/moondb/
PlantMP:   raw CSV already local → data/raw/plantmp/
```

## Offline transformation pipeline

| Step | Entry point | Module / function | Inputs | Outputs | Validation boundary |
|---|---|---|---|---|---|
| MoonDB claims | `scripts/build_source_claims_moondb.py` | `moondb_claims.adapt_moondb_claims` | `data/raw/moondb/` + manifest + policy | `data/interim/source_claims_moondb.csv` | manifest provenance row required; policy-mapped status |
| PlantMP claims | `scripts/build_source_claims_plantmp.py` | `plantmp_claims.adapt_plantmp_claims` | `data/raw/plantmp/` + manifest + policy | `data/interim/source_claims_plantmp.csv` | same pattern |
| MoonProt universe gate | `scripts/build_mfp_catalog_mvp.py` (pre-build) | `validate_moonprot_universe` (constants `MOONPROT_SNAPSHOT_MPID_MIN/MAX`, snapshot scope, not a permanent maximum) | raw filenames, artifact index, absent log | pass/fail (no writes) | out-of-scope MPIDs fail non-zero with exact IDs |
| Raw input verification | `scripts/build_mfp_catalog_mvp.py` (pre-build gate) | `mfp_bibliography/raw_input_verification.py::verify_catalog_inputs` | consumed raw artifacts + `data/manifests/source_manifest.csv` + `data/raw/moonprot/artifact_index.csv` | pass/fail (no writes) | fails non-zero on mismatch, missing/duplicate entry, or missing file |
| MultifacetedProtDB records | `scripts/build_source_records_multifacetedprotdb.py` | `multifacetedprotdb_records.load_source_records` (Python-literal parse, binding to registered hash) | `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` | `data/interim/source_records_multifacetedprotdb.csv` | shape/accession/hash validation; no partial output |
| Catalog build | `scripts/build_mfp_catalog_mvp.py` | `load_moondb_claims`, `load_plantmp_claims`, `load_moonprot_records` (uses `moonprot_parser.parse_moonprot_html`), `assign_protein_ids`, `build_identifiers`, `build_assertions`, `build_coverage` | claims CSVs + `data/raw/moonprot/*.html` + absent log | `data/processed/mfp_catalog_mvp/` tables + `summary.json` + README | `validate_catalog_integrity` gate before any write; non-zero exit blocks publishing |
| Repository validation | `scripts/validate_repository.py` | `validation.validate_repository` | schemas, manifests | JSON report | run in CI (`.github/workflows/ci.yml`), not inside the build |

Identity rules live in `mfp_bibliography/normalization.py`
(`normalize_uniprot_accession`, `make_protein_id_uniprot`,
`make_protein_id_fallback`, scheme `MFPB_PROTEIN_ID_V1`, ADR-005).

## Coverage-only status rows

Known-absent and unresolved MoonProt MPIDs never create source records or
protein entities (ADR-006); they appear only in `mfp_coverage.csv` with
absent-log provenance.

## Not implemented yet

- MultitaskProtDB-II: RAW_ONLY (`data/raw/`, source profile exists; not in
  catalog). MultifacetedProtDB is integrated as the fourth catalog source with
  zero evidence claims (no status field in the source).
- Laboratory GO/evidence integration: FUTURE (contract only:
  `docs/bibliography/go-annotation-evidence-contract.md`, Phase D0/D).

## Where to change what

- Source parsing: `src/mfp_bibliography/{moondb,plantmp}_claims.py`,
  `moonprot_parser.py`.
- Identity rules: `src/mfp_bibliography/normalization.py` (scheme change needs
  a new ADR).
- Catalog outputs: `scripts/build_mfp_catalog_mvp.py` (headers, writers).
- Coverage: same script, `load_moonprot_records` / `build_coverage`.
- Validation: same script, `validate_catalog_integrity`,
  `compute_summary_metrics`; repo-wide: `src/mfp_bibliography/validation.py`.
- Documentation: `docs/roadmap/` (milestones), this directory (technical
  map), `docs/decisions/` (ADRs), `docs/source-profiles/` (source facts).

## Open risks

- The pre-build gate covers consumed artifacts only; a full sweep of
  `data/manifests/file_checksums.sha256` (all raw files) is not automated.
