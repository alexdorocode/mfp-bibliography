# Releases

Release artifacts and release notes for immutable catalog snapshots are tracked from this directory. Git tags are applied when a release is published; no tag has been published yet. The current artifact, `mfp-catalog-candidate-v0.3.0/`, is a CANDIDATE — not the final `mfp_catalog_v1` release and not a tagged release. It supersedes `mfp-catalog-candidate-v0.2.0/` (documentation-only correction of source-status semantics; all catalog CSVs are byte-identical; v0.2.0 remains immutable and verifiable via `--candidate-id`).

New readers: start with [../docs/getting-started.md](../docs/getting-started.md), then the
candidate directory [mfp-catalog-candidate-v0.3.0/](mfp-catalog-candidate-v0.3.0/).

Each packaged candidate can be verified offline, from a clean clone, without
rebuilt outputs or raw inputs:

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This checks package-internal integrity only (inventory, hashes, row counts,
primary and foreign keys against the candidate's `MANIFEST.json`). Comparing
packaged bytes against locally rebuilt outputs is a separate REBUILD_COMPARE
step (`--verify`); see `docs/release-policy.md` and the candidate's release
notes under `docs/releases/`.
