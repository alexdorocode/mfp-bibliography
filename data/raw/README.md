# Raw Data Policy

`data/raw/` is reserved for immutable source artifacts.

- Do not manually edit files once added.
- Do not add generated/normalized outputs here.

## What is actually in Git

`.gitignore` ignores `data/*`; only files tracked before that rule (or explicitly added) are distributed with a clone:

- **Tracked raw artifacts** (whole-file hashes in `data/manifests/source_manifest.csv`): MoonDB `all_emf_and_curated.tsv`, MultifacetedProtDB `MultifacetedProtDB_data.json`, MultitaskProtDB-II `proteins.csv`, PlantMP CSVs.
- **NOT tracked** (ignored, local only): the per-MPID MoonProt HTML artifacts and `data/raw/moonprot/artifact_index.csv` (702 pages), and everything under `data/interim/` and `data/processed/`.

## Reproducibility limitation

A clone therefore does **not** contain all raw inputs needed to rebuild the catalog: the MoonProt HTML artifacts and their index are local-only. Their distribution outside the original acquisition working tree is unresolved; MoonProt acquisition is a controlled, policy-governed process (see `docs/acquisition-protocols/moonprot.md`) and is not to be re-run automatically. The packaged candidate under `releases/` can always be inspected and verified offline without these inputs (`PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package`); see `docs/getting-started.md`.
