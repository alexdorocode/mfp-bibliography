# MFP Catalog Candidate v0.3.0 (five-source, documentation-only correction)

- **Status**: CANDIDATE — not the final `mfp_catalog_v1` release, not tagged.
- **Artifact**: `releases/mfp-catalog-candidate-v0.3.0/`
- **Supersedes**: `mfp-catalog-candidate-v0.2.0` (immutable, kept, still
  offline-verifiable via
  `PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package --candidate-id mfp-catalog-candidate-v0.2.0`).
- **Catalog contract**: `MFPB_0_19_MFP_CATALOG_MVP_V2` (unchanged);
  protein ID scheme `MFPB_PROTEIN_ID_V1` (unchanged).

## What changed (documentation only)

- `DATA_DICTIONARY.md`: `source_status` is now described correctly as the
  repository POLICY-MAPPED status (MFPB_0_7) for MoonDB/PlantMP, with
  MoonProt's `valid` as a loader-generated technical status (not a source
  evidence label); `raw_claim_field`/`raw_claim_value` are documented as the
  authoritative verbatim source-label location; labels are not a
  cross-source evidence scale. This resolves the imprecision recorded in the
  [v0.2.0 erratum](mfp-catalog-candidate-v0.2.0.md).
- `README.md`: "Source statuses" section corrected accordingly; a
  "Deferred" section states that a packaged `validation_report.json` is
  deferred to the `mfp_catalog_v1` release (gate 4 of the
  [release contract draft](mfp-catalog-v1-contract-draft.md)).
- `MANIFEST.json`: candidate_id v0.3.0; corrected
  `verification_command` (offline PACKAGE_VERIFY) plus
  `rebuild_compare_command` (REBUILD_COMPARE).
- `checksums.sha256`: regenerated for the changed documentation bytes.

## What did NOT change

- All five catalog CSVs are byte-identical to v0.2.0 (SHA-256 hashes equal
  the v0.2.0 MANIFEST `packaged_outputs`): 2,962 source records
  (MoonDB 351, MoonProt 702, MultifacetedProtDB 1,103, MultitaskProtDB-II
  694, PlantMP 112), 2,322 protein entities, 463 shared-accession merges,
  MoonProt coverage 702/1/3, input hashes and catalog contract unchanged.
- The absolute `raw_path` behavior is intentionally NOT fixed in this
  version (would change catalog bytes; tracked separately).
- The scientific limitations of v0.2.0 carry over unchanged (unresolved
  MPIDs 542/543/626, MPID 103 known absent, reference anomalies
  `multitaskprotdb_ii_row_239/349/422`, no verified article-to-GO
  relations, `canonical_gene`/`taxonomy_id` structurally unpopulated).

## Verification

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```
