# MFP Catalog Candidate v0.2.0 (five-source, accession-first)

- **Status**: CANDIDATE — not the final `mfp_catalog_v1` release.
- **Artifact**: `releases/mfp-catalog-candidate-v0.2.0/`
- **Catalog contract**: `MFPB_0_19_MFP_CATALOG_MVP_V2`; protein ID scheme
  `MFPB_PROTEIN_ID_V1`.

## Contents
Byte-identical copies of the validated catalog outputs
(`mfp_proteins.csv`, `mfp_source_records.csv`, `mfp_identifiers.csv`,
`mfp_assertions.csv`, `mfp_coverage.csv`) plus `MANIFEST.json`,
`checksums.sha256`, `DATA_DICTIONARY.md` and `README.md`.

## Measured counts (from `summary.json`, re-verified at packaging)
- Source records: 2,962 — MoonDB 351, MoonProt 702, MultifacetedProtDB 1,103,
  MultitaskProtDB-II 694 (685 accessions; 9 repeated as separate observations),
  PlantMP 112.
- Protein entities: 2,322 (one per normalized UniProt accession).
- Shared-accession merges: 463 (accessions claimed by ≥2 sources — a separate
  metric, not records-minus-proteins).
- MoonProt coverage: 702 acquired / 1 known absent (MPID 103) / 3 unresolved
  (MPIDs 542, 543, 626) — coverage-only, never protein entities.

## Identity and integrity
- Merging only by exact normalized UniProt accession equality (ADR-005).
- PK/FK integrity, per-source conservation, input binding (raw + interim hashes
  and transformation ids) re-verified before publishing; a failing check
  publishes nothing, and an existing candidate is never overwritten with
  different bytes.
- Packaging is byte-stable (no volatile fields); reproduction commands are in
  `MANIFEST.json`; `checksums.sha256` covers every packaged file.

## Limitations
- No verified article-to-GO relationships exist yet; all GO/reference text is
  raw, uninterpreted source data.
- MultitaskProtDB-II reference anomalies (rows
  `multitaskprotdb_ii_row_239/349/422`) remain raw and unverified; never
  promoted to PMID/DOI.
- MultifacetedProtDB and MultitaskProtDB-II have no source evidence status;
  their `operational_status=unresolved` is administrative, not a scientific
  label.
- No complete MoonProt coverage or complete bibliography is claimed. This is
  not an MF-vs-NMF dataset, classifier, negative set or ML benchmark.

## Verification

Two distinct verification modes exist for this candidate.

### PACKAGE_VERIFY (offline; works in a clean clone)

Checks internal package integrity only: file inventory, packaged SHA-256
hashes (`checksums.sha256` and `MANIFEST.json`), CSV row counts against the
manifest, primary-key uniqueness and cross-table foreign keys. Reads only
files inside `releases/mfp-catalog-candidate-v0.2.0/`; requires no raw
inputs, interim files, `data/processed/` outputs, network, Git tags or
catalog rebuild. Never writes into the candidate.

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

### REBUILD_COMPARE (requires locally rebuilt outputs)

The historical `MANIFEST.json` field `verification_command`
(`... --verify`) is a REBUILD_COMPARE command: it compares the packaged
bytes against locally rebuilt outputs in
`data/processed/mfp_catalog_mvp/`. It therefore requires external,
hash-identical raw and interim inputs (including the 702 MoonProt HTML
artifacts and `artifact_index.csv`, which are not distributed in Git) and
cannot run in a clean, offline clone. It is not a package-integrity check.

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify
```

Any change to packaged bytes requires a new candidate version; the
packager refuses to overwrite an existing candidate with different bytes.

Tests: `tests/test_catalog_candidate.py` (packaging, REBUILD_COMPARE),
`tests/test_candidate_package_verify.py` (offline PACKAGE_VERIFY).
