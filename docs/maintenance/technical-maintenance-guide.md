# Technical Maintenance Guide (five-source catalog)

Surgical maintenance of the current five-source candidate
([`mfp-catalog-candidate-v0.3.0`](../../releases/mfp-catalog-candidate-v0.3.0/); supersedes v0.2.0, which stays immutable and verifiable)
with minimal, traceable changes. Companion documents:
[data-flow map](../architecture/data-flow.md),
[traceability matrix](../architecture/requirements-traceability.md),
[release policy](../release-policy.md), [getting started](../getting-started.md).

## 1. System boundaries

What exists today:

- **Acquisition** (network, manual, policy-governed): only MoonProt, via
  `scripts/acquire_moonprot_smoke.py` / `scripts/acquire_moonprot_batch.py`
  → `data/raw/moonprot/mpid_*.html` + `artifact_index.csv`. Never run
  automatically; see the
  [acquisition protocol](../acquisition-protocols/moonprot.md).
- **Raw manifests**: `data/manifests/source_manifest.csv` (whole-file hashes)
  and `data/manifests/file_checksums.sha256`. Raw data is immutable
  ([ADR-002](../decisions/ADR-002-raw-data-immutability.md)).
- **Source adapters** (offline): `src/mfp_bibliography/moondb_claims.py`,
  `plantmp_claims.py`, `moonprot_parser.py`, `multifacetedprotdb_records.py`,
  `multitaskprotdb_ii_records.py`, each with a `scripts/build_source_*` entry
  point writing `data/interim/` claims or source records.
- **Catalog builder**: `scripts/build_mfp_catalog_mvp.py` — universe gate
  (`validate_moonprot_universe`), raw-input gate
  (`raw_input_verification.verify_catalog_inputs`), identity assignment,
  table writers, `validate_catalog_integrity` pre-write gate,
  `compute_summary_metrics`.
- **Identity rules**: `src/mfp_bibliography/normalization.py`
  (`normalize_uniprot_accession`, `make_protein_id_uniprot`,
  `make_protein_id_fallback`; scheme `MFPB_PROTEIN_ID_V1`,
  [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)). Merging is
  exact normalized UniProt accession only.
- **Validation gates**: repository-level
  `src/mfp_bibliography/validation.py` (run by
  `scripts/validate_repository.py` in CI) and build-level integrity gates.
- **Candidate packaging/verification**: `scripts/package_catalog_candidate.py`
  — package, `--verify-package` (PACKAGE_VERIFY, offline),
  `--verify` (REBUILD_COMPARE).

Deferred: laboratory GO/evidence integration (roadmap Phases D0/D; contract
only in the
[GO annotation contract](../bibliography/go-annotation-evidence-contract.md);
traceability R14–R17 remain documented_only). No verified article-to-GO
relations exist in the candidate.

## 2. Surgical-change table

| Change type | Owner path / function | Contract / ADR | Focused tests | Broader validation / outputs |
|---|---|---|---|---|
| Correct a source parser/adapter | e.g. `src/mfp_bibliography/moondb_claims.py::adapt_moondb_claims`, `plantmp_claims.py`, `moonprot_parser.py::parse_moonprot_html`, `multitaskprotdb_ii_records.py` | [ADR-003](../decisions/ADR-003-provenance-and-transformations.md); source profile | `tests/test_moondb_claims.py` / `test_plantmp_claims.py` / `test_moonprot_parser.py` / `test_multitaskprotdb_ii_records.py` / `test_multifacetedprotdb_records.py` (per source) | rebuild interim CSV → catalog; counts conserved per source; verbatim raw values retained; new candidate if packaged bytes change |
| Add a source | new adapter module + `scripts/build_source_*` + manifest row + `EXPECTED_SOURCES` in `scripts/package_catalog_candidate.py` and `expected_source_record_counts` in the build | source-catalog.md; ADR-003/005; new source profile | per-source test module (pattern of existing ones) | `scripts/validate_repository.py`; catalog + traceability + roadmap updates; new candidate. Onboarding checklist location: UNKNOWN (no single doc codifies it) |
| Change source-status interpretation | `configs/source_claim_policy_v0.1.yaml`, `src/mfp_bibliography/source_claims.py::load_claim_policy`, `effective_status.py::_resolve_effective_status` | [source-claim policy](../source-claim-policy.md), [effective-status contract](../effective-status-contract.md), [ADR-004](../decisions/ADR-004-evidence-label-benchmark-separation.md) | `tests/test_source_claim_policy.py`, `tests/test_effective_status.py` | claims CSVs rebuilt; `operational_status`/assertions re-derived; labels stay verbatim |
| Change accession normalization or protein_id | `src/mfp_bibliography/normalization.py` | [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) — scheme change requires a new ADR | `tests/test_normalization.py`; `TestProteinIdScheme`, `TestCrossProcessDeterminism` in `tests/test_mfp_catalog_mvp.py` | all protein IDs change → full rebuild, migration report, new candidate + contract review |
| Change coverage / known-absent handling | `scripts/build_mfp_catalog_mvp.py` (`load_moonprot_records`, `build_coverage`, `MOONPROT_SNAPSHOT_MPID_MIN/MAX`) | [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md) | `tests/test_moonprot_universe.py`; `TestCoverageOnlyMpids` in `tests/test_mfp_catalog_mvp.py` | `mfp_coverage.csv`; coverage-only MPIDs never become entities |
| Change a catalog column or assertion | `scripts/build_mfp_catalog_mvp.py` (headers, writers, `build_assertions`) | catalog contract `MFPB_0_19_MFP_CATALOG_MVP_V2` — semantic change bumps the contract | `tests/test_mfp_catalog_mvp.py`, `tests/test_catalog_integrity.py` | packaged tables + [DATA_DICTIONARY](../../releases/mfp-catalog-candidate-v0.3.0/DATA_DICTIONARY.md); new candidate |
| Change a raw checksum / provenance binding | `src/mfp_bibliography/raw_input_verification.py::verify_catalog_inputs`; `data/manifests/source_manifest.csv`, `data/raw/moonprot/artifact_index.csv` | [ADR-002](../decisions/ADR-002-raw-data-immutability.md), [ADR-003](../decisions/ADR-003-provenance-and-transformations.md) | `tests/test_raw_input_verification.py` (mismatch/missing/duplicate) | build fails non-zero on tampered input; never edit raw bytes — re-register or re-acquire via policy |
| Change candidate packaging / verification | `scripts/package_catalog_candidate.py` | [release policy](../release-policy.md); candidate note | `tests/test_catalog_candidate.py` (package + REBUILD_COMPARE), `tests/test_candidate_package_verify.py` (PACKAGE_VERIFY) | existing candidate never overwritten; changed package = new candidate version |
| Add GO evidence / reference relations (later) | none yet | [GO annotation contract](../bibliography/go-annotation-evidence-contract.md); R14–R17 | none exist — UNKNOWN until implemented | new tables (`mfp_function_assertions`, `mfp_references`, ...); record-level references must not become function-level support |

## 3. Safe workflow

1. Inspect the baseline: read the candidate
   [`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json)
   (`measured_counts`) and `git status`. Do not assume the working tree is
   clean.
2. Define exactly one behavioral change; write it down before editing.
3. Add a regression fixture that fails before the fix and passes after.
4. Run the focused test module for the owner path, then broader checks:
   `pytest`, `PYTHONPATH=src python scripts/validate_repository.py`, and
   `PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package`.
5. Compare before/after evidence: counts per source, protein entity count,
   PK/FK integrity, unchanged IDs for untouched records, and packaged hashes.
   For rebuilds, `PYTHONPATH=src python scripts/package_catalog_candidate.py --verify`
   (REBUILD_COMPARE) confirms byte-identity against local outputs.
6. Update only the affected documents: traceability rows, data-flow edges,
   source profile, roadmap status, changelog entry.
7. Decide publication: if packaged bytes change, a new candidate version is
   required; the packager refuses in-place overwrites.

Never alter raw evidence (`data/raw/`) or a hashed candidate in place. Do not
use destructive Git cleanup commands; inspect `git status` and revert or
commit normally.

## 4. Version and portability gates

- **Code-only fix** (parser or packaging logic whose outputs are byte-identical):
  candidate bytes stay unchanged; verify with REBUILD_COMPARE locally, then
  PACKAGE_VERIFY. No new candidate.
- **Data / schema / identity / output change**: any change to packaged bytes,
  column semantics, the protein-ID scheme, or the count baseline requires a
  new candidate version (e.g. v0.3.0), a catalog-contract review
  (MFPB_0_19 → MFPB_0_20 when semantics change), and a changelog entry.
- **PACKAGE_VERIFY vs REBUILD_COMPARE**: `--verify-package` is offline and
  needs only the candidate directory; `--verify` compares against a rebuilt
  `data/processed/mfp_catalog_mvp/` and needs local, hash-identical raw and
  interim inputs (not all distributed in Git; see
  [getting started](../getting-started.md)).
- **Clean-clone claims**: a literal clean-clone verification requires the
  candidate and verifier to be committed and a separate clone test to be run.
  No Git tag exists yet; do not claim a tagged or published release.

## 5. Worked example (trace only — not performed)

Change: correct how MultitaskProtDB-II reference values are classified, while
retaining `reference_raw` verbatim.

- Affected paths: `src/mfp_bibliography/multitaskprotdb_ii_records.py`
  (classification into `reference_article_like` / `reference_anomaly`),
  `scripts/build_source_records_multitaskprotdb_ii.py` (interim rebuild),
  `scripts/build_mfp_catalog_mvp.py` only if column semantics move.
- Tests: add a regression fixture to
  `tests/test_multitaskprotdb_ii_records.py` covering the misclassified
  value; `tests/test_mfp_catalog_mvp.py::TestMultitaskIntegration` must keep
  anomalies attached to their original rows.
- Evidence: before — flag states on rows (e.g. the three anomaly rows);
  after — only the classification flags change; `reference_raw`,
  counts, IDs, and all other columns are byte-identical.
- Publication: `mfp_source_records.csv` bytes change → new candidate
  (v0.3.0); update traceability R21 evidence, the
  [MultitaskProtDB-II profile](../source-profiles/multitaskprotdb-ii.md),
  and the changelog.

## 6. Documentation upkeep

- Vision/scope: `docs/project-charter.md` and `README.md`.
- Roadmap: milestone status only — `docs/roadmap/mfp-catalog-implementation-plan.md`.
- Source semantics: `docs/source-profiles/` (MoonProt: acquisition protocol).
- Lasting decisions: `docs/decisions/` (ADRs).
- Requirement ↔ code ↔ test mapping: the
  [traceability matrix](../architecture/requirements-traceability.md).
- Completed history: `CHANGELOG.md`.
- Measured snapshot: the candidate `MANIFEST.json` — the single source of
  truth for counts; docs link to it rather than restating numbers.

Update only the documents a change actually affects; never edit files inside
a packaged candidate.
