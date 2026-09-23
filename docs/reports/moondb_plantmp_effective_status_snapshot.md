# MoonDB + PlantMP Effective Status Snapshot (MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT)

## Contract ID
`MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT`

## Status
This is an **auditable local snapshot contract** for an uncommitted derived artifact.
This is **not** a final release and **must not** be called a source freeze.

## Snapshot Overview
- **Inputs**: 463 source claims (351 MoonDB + 112 PlantMP)
- **Output Records**: 461 effective-status records
- **Exclusions**: 0 (no blank/missing UniProt IDs in inputs)
- **Output SHA-256**: `7522eeeb58ad02578fdab35db6fef43ef82bab12aeee6c3137bc944b63f6d21a`

## Effective Status Distribution
- `curated`: 124
- `predicted`: 326
- `excluded_likely`: 11

## Generation
The derived artifact is generated locally by running:
```bash
PYTHONPATH=src python scripts/generate_effective_status_moondb_plantmp.py
```

The generator:
- Reads both source-claim CSVs
- Validates every input claim
- Aggregates only non-empty `uniprot_id`
- Uses precedence: `curated > predicted > excluded_likely > unresolved`
- Produces deterministic output (byte-reproducible reruns)

## Snapshot Manifest
A JSON snapshot manifest is emitted alongside the CSV output at:
`data/interim/reports/effective_status_moondb_plantmp_snapshot.json`

The manifest includes:
- Snapshot ID
- Generated timestamp
- Input paths and SHA-256 checksums
- Input claim counts by source
- Output path and SHA-256
- Output record count
- Status distribution
- Exclusions count
- Aggregation policy ID
- Transformation/script ID
- Schema version
- Reproducibility statement

## Schema
See `data/interim/reports/effective_status_snapshot.schema.json` for the manifest schema.

## Reproducibility
Generation is byte-reproducible: running the generator twice on the same inputs
produces identical output SHA-256 checksums. Only the timestamp in the manifest
differs between runs.

## Explicit Non-Guarantees
- No real CSV, report, or manifest outputs are committed to the repository
- This is not a source freeze or release
- No MF/NMF labels, controls, benchmark roles, or training cohorts are created
- Raw data, source claims, policies, schemas, and MoonProt docs are unchanged
