# Scripts

Navigation table for the scripts currently present in this directory. All are
offline (no network) except the two controlled MoonProt acquisition CLIs, which
are policy-governed and must be run manually with explicit approval (see
`docs/acquisition-protocols/moonprot.md`); nothing here scrapes on its own.

| Script | Purpose | Input | Output | Offline / network |
|---|---|---|---|---|
| `validate_repository.py` | Validate repository structure, manifest header, and JSON schemas | `data/curated/` schemas, `data/manifests/source_manifest.csv` | JSON report to stdout | offline |
| `build_manifest.py` | Safe skeleton CLI for future source-manifest generation | manifest sources | manifest scaffold | offline |
| `normalize_source_records.py` | Placeholder CLI for future source-specific normalization adapters | — | — | offline |
| `profile_source.py` | Read-only profiling of local source artifacts; fails explicitly on malformed input | local source artifacts | structured JSON | offline |
| `build_source_claims_moondb.py` | Adapt MoonDB raw artifact to source claims | `data/raw/moondb/` + manifest + policy | `data/interim/source_claims_moondb.csv` | offline |
| `build_source_claims_plantmp.py` | Adapt PlantMP raw artifact to source claims | `data/raw/plantmp/` + manifest + policy | `data/interim/source_claims_plantmp.csv` | offline |
| `build_source_records_multifacetedprotdb.py` | Ingest MultifacetedProtDB raw artifact to interim source records (hash-bound) | `data/raw/multifacetedprotdb/MultifacetedProtDB_data.json` | `data/interim/source_records_multifacetedprotdb.csv` | offline |
| `build_source_records_multitaskprotdb_ii.py` | Ingest MultitaskProtDB-II raw artifact to interim source records (hash-bound) | `data/raw/multitaskprotdb-ii/proteins.csv` | `data/interim/source_records_multitaskprotdb_ii.csv` | offline |
| `build_mfp_catalog_mvp.py` | Build the catalog: universe and raw-input gates, protein IDs, tables, summary (pre-write integrity gate) | interim claims/records + `data/raw/moonprot/*.html` + absent log | `data/processed/mfp_catalog_mvp/` tables, `summary.json` | offline |
| `package_catalog_candidate.py` | Package the validated catalog as the reproducible candidate; also verifies it (see below) | `data/processed/mfp_catalog_mvp/` | `releases/mfp-catalog-candidate-v0.2.0/` | offline |
| `parse_moonprot_fixture.py` | Parse local MoonProt HTML fixtures deterministically | local HTML fixture files | JSON to stdout | offline |
| `audit_moondb_plantmp_overlap.py` | Read-only MoonDB/PlantMP overlap audit | `data/interim/source_claims_{moondb,plantmp}.csv` | `data/interim/reports/moondb_plantmp_overlap_audit.{json,md}` | offline |
| `audit_moondb_plantmp_snapshot.py` | Quality audit of the local MoonDB + PlantMP effective-status snapshot | snapshot artifacts | audit report | offline |
| `generate_effective_status_moondb_plantmp.py` | Generate effective-status artifact from MoonDB and PlantMP claims | `data/interim/source_claims_{moondb,plantmp}.csv` | `data/interim/effective_status_moondb_plantmp.csv` + reports | offline |
| `acquire_moonprot_smoke.py` | Controlled MoonProt smoke acquisition (MPIDs 1–3; dry-run by default) | MoonProt site (HTTP) | `data/raw/moonprot/` HTML + logs | network; manual, policy-governed |
| `acquire_moonprot_batch.py` | Controlled MoonProt batch acquisition (explicit IDs/ranges, max 100) | MoonProt site (HTTP) | `data/raw/moonprot/` HTML + index + logs | network; manual, policy-governed |

## Verification modes of `package_catalog_candidate.py`

- `--verify-package` — **PACKAGE_VERIFY** (offline; works in a clone): checks
  inventory, packaged SHA-256 hashes, CSV row counts, primary keys and
  cross-table foreign keys against the candidate `MANIFEST.json`. Reads only
  files inside `releases/mfp-catalog-candidate-v0.2.0/`.
- `--verify` — **REBUILD_COMPARE**: compares packaged bytes against a locally
  rebuilt `data/processed/mfp_catalog_mvp/` catalog; requires external,
  hash-identical raw/interim inputs not all distributed in Git.
- Default (no flag) — package: rebuild-and-package workflow; refuses to
  overwrite an existing candidate with different bytes. Any changed package
  requires a new candidate version.

See `docs/getting-started.md` for the user paths and
`docs/architecture/data-flow.md` for the pipeline map.
