# Pre-MoonProt Baseline v0.1 (MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT)

## Baseline ID
`pre-moonprot-baseline-v0.1`

## Status
This is a **checksum-pinned local pre-MoonProt baseline**. This is **not** a final release, **not** a source freeze, and **must not** be called a release dataset.

## Input Artifacts (SHA-256)

| Input | Path | SHA-256 | Claims |
|---|---|---|---|
| MoonDB source claims | `data/interim/source_claims_moondb.csv` | `b257ff15abb81d895b8b297cf7659e5aa0136439ee127370371589600a80f5e6` | 351 |
| PlantMP source claims | `data/interim/source_claims_plantmp.csv` | `a355555a1ad7c858d922281c66bfa54c4b7b754e09c3fe29e7016c0e081738ce` | 112 |
| Effective status schema | `data/curated/effective_status.schema.json` | `5847d496c6ab1bf815a23d726e8d03b7a08cb561b85189202002b98960eea833` | - |

## Derived Artifacts (SHA-256)

| Artifact | Path | SHA-256 | Records |
|---|---|---|---|
| Effective status CSV | `data/interim/effective_status_moondb_plantmp.csv` | `7522eeeb58ad02578fdab35db6fef43ef82bab12aeee6c3137bc944b63f6d21a` | 461 |
| Snapshot manifest | `data/interim/reports/effective_status_moondb_plantmp_snapshot.json` | `0a923176c0a0ff95866a3c74217a41f1f7ee65372f3440d9446ff58135bf4723` | - |
| JSON report | `data/interim/reports/effective_status_moondb_plantmp_report.json` | `518faa810b19e989059af4e866f676aa13f87596c73db197142d075986bba267` | - |
| MD report | `data/interim/reports/effective_status_moondb_plantmp_report.md` | `90f18bc904df1b400be684f0f8302e3955c4f6056d7a8ccdf8adf5bf647817ed` | - |

## Audit Artifacts (SHA-256)

| Artifact | Path | SHA-256 |
|---|---|---|
| Overlap audit JSON | `data/interim/reports/moondb_plantmp_overlap_audit.json` | `94810f6db751810599ad77d45e3a434adef34a9b557479e810a847de37dfa876` |
| Overlap audit MD | `data/interim/reports/moondb_plantmp_overlap_audit.md` | `8fc41dc5c95397f39f859b59a5f0a98f662e3e782e6c8fd5cea2471acdff49e7` |

## Counts
- **Input claims**: 463 (351 MoonDB + 112 PlantMP)
- **Output records**: 461
- **Unique UniProt IDs**: 461
- **curated**: 124
- **predicted**: 326
- **excluded_likely**: 11
- **unresolved**: 0
- **Exclusions**: 0

## Policy and Transformation IDs
- **Aggregation policy ID**: `MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0`
- **Transformation ID**: `effective_status_moondb_plantmp_v0`
- **Snapshot schema version**: `MFPB_0_15_SNAPSHOT_V0`
- **Snapshot ID**: `moondb_plantmp_effectivestatus_5f5ff03a1682538f`

## Generation
The derived artifact is generated locally by running:
```bash
PYTHONPATH=src python3 scripts/generate_effective_status_moondb_plantmp.py
```

## Reproducibility Statement
Generation is byte-reproducible: running the generator twice on the same inputs produces identical output SHA-256 checksums. Only the `generated_at` timestamp in the manifest differs between runs.

## Verification
To verify this baseline:
1. Rerun the generator: `PYTHONPATH=src python3 scripts/generate_effective_status_moondb_plantmp.py`
2. Compare the output SHA-256 of `data/interim/effective_status_moondb_plantmp.csv` with the pinned hash above
3. All hashes must match exactly

## Explicit Non-Guarantees
- No real CSV, report, or manifest outputs are committed to the repository
- This is not a source freeze or final release
- No MF/NMF labels, controls, benchmark roles, or training cohorts are created
- Raw data, source claims, policies, schemas, and MoonProt docs are unchanged
- No network access required or permitted for verification
- No new MoonProt records acquired for this baseline
