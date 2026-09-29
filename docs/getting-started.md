# Getting Started

Ordered guide for a new reader of the five-source candidate
[`releases/mfp-catalog-candidate-v0.2.0/`](../releases/mfp-catalog-candidate-v0.2.0/):
**inspect → offline verify → (optional) local tests → (optional) rebuild**.

## Prerequisites

From [`pyproject.toml`](../pyproject.toml):

- Python **3.11 or newer** (requires-python `>=3.11`).
- Package dependency: `jsonschema>=4.22.0`; development extras: `pytest>=8.2.0`, `pyyaml>=6.0`.

Paths 1–2 below need only a Python 3.11+ interpreter — the verifier script uses
the standard library only, so no `pip install` is required for inspection or
offline verification. Installation is needed only for the optional test and
rebuild paths:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 1. Inspect the packaged CSVs

Open the candidate directory
[`releases/mfp-catalog-candidate-v0.2.0/`](../releases/mfp-catalog-candidate-v0.2.0/)
with any CSV reader. Start with the primary table:

- [`mfp_proteins.csv`](../releases/mfp-catalog-candidate-v0.2.0/mfp_proteins.csv) —
  one row per protein entity (2,322 in v0.2.0; authoritative counts are in
  [`MANIFEST.json`](../releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json),
  key `measured_counts`).
- Provenance and interpretation tables: `mfp_source_records.csv` (one row per
  source observation), `mfp_identifiers.csv`, `mfp_assertions.csv`,
  `mfp_coverage.csv` (MoonProt snapshot coverage statuses only).
- Column definitions and table grains:
  [`DATA_DICTIONARY.md`](../releases/mfp-catalog-candidate-v0.2.0/DATA_DICTIONARY.md).

Optional, no Python needed — verify the packaged file hashes with a standard
checksum tool from inside the candidate directory
(`sha256sum -c checksums.sha256`, or the equivalent on your platform).

Source semantics: [source profiles](source-profiles/) (MoonProt is documented
in its [acquisition protocol](acquisition-protocols/moonprot.md)).
Pipeline architecture: [data-flow map](architecture/data-flow.md).

Planned descriptive analyses of the packaged tables (coverage, overlap,
composition — not validated articles or GO support):
[five-source descriptive study plan](analysis/five-source-descriptive-study-plan.md).

## 2. Verify the package offline (PACKAGE_VERIFY)

Checks internal package integrity only: file inventory, SHA-256 hashes
(`checksums.sha256` and `MANIFEST.json`), CSV row counts against the
manifest, primary-key uniqueness and cross-table foreign keys. It reads
nothing outside the candidate directory — no raw, interim or
`data/processed/` inputs, no network — and never writes into the candidate.
Exit code 0 means the package is consistent; a non-zero exit prints a
`[candidate] ...` diagnostic naming the offending file.

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This is **not** the same as `--verify` (`REBUILD_COMPARE`), which compares the
packaged bytes against a locally rebuilt `data/processed/mfp_catalog_mvp/`
catalog. `--verify` cannot run in a checkout without those rebuilt outputs.

## 3. Optional: run tests locally

```bash
pytest
python scripts/validate_repository.py
```

Caveats, checked against the test suite:

- Most tests read local inputs that are **ignored by `.gitignore` (`data/*`)
  and not distributed in Git**: the 702 MoonProt HTML pages and
  `data/raw/moonprot/artifact_index.csv`, interim source-record CSVs under
  `data/interim/`, and rebuilt outputs under `data/processed/mfp_catalog_mvp/`.
  The full suite has **not** been run in a clean clone and is not expected to
  pass there without those inputs.
- `tests/test_candidate_package_verify.py` (offline PACKAGE_VERIFY tests)
  needs only repository files and the packaged candidate; it was run
  successfully in a tracked-plus-untracked extraction containing no ignored
  data files.
- `scripts/validate_repository.py` validates repository structure and schemas;
  it needs the package importable (`pip install -e .[dev]` as above, or
  `PYTHONPATH=src`).

## 4. Optional: rebuild the catalog

Rebuilding means re-running the commands recorded in the candidate's
[`MANIFEST.json`](../releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json)
(`build_commands`) to regenerate `data/processed/mfp_catalog_mvp/` and
repackage. Two hard prerequisites:

1. **Raw and interim inputs.** Not all are in Git. In Git (tracked): raw
   MoonDB, MultifacetedProtDB, MultitaskProtDB-II and PlantMP artifacts
   (hashes in `data/manifests/source_manifest.csv`). Not in Git (ignored by
   `.gitignore`): the per-MPID MoonProt HTML artifacts and
   `artifact_index.csv`, the interim `source_records_*.csv` files, and the
   prior `data/processed/` outputs.
2. **Hash-identical bytes.** The build verifies every consumed input against
   the recorded SHA-256 hashes and fails on any mismatch.

**Where to obtain the missing inputs:** their distribution outside this
working tree is unresolved — no repository document specifies an alternative
source for the ignored MoonProt and interim artifacts. MoonProt acquisition
is a controlled, policy-governed process documented in the
[acquisition protocol](acquisition-protocols/moonprot.md); it requires
explicit maintainer approval and is not to be re-run automatically. If you
cannot obtain hash-identical inputs, use paths 1–2 (inspect and offline
verify) instead of rebuilding.

Rebuild rules and immutability: [release policy](release-policy.md).
Candidate scope and limitations:
[release notes](releases/mfp-catalog-candidate-v0.2.0.md) and the
[candidate README](../releases/mfp-catalog-candidate-v0.2.0/README.md).

## Clone status caveat

The packaged candidate and the verifier script were working-tree files not
yet committed at the time of writing. `git archive HEAD` therefore omits
them, and offline verification has not been demonstrated in a literal clean
clone. The offline command and its tests were executed in an extraction
containing tracked plus untracked (non-ignored) files — the state a clean
clone will have once these files are committed.
