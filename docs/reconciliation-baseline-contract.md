# Reconciliation Baseline Contract (MFPB_0_16_RECONCILIATION_BASELINE_CONTRACT_V0)

## Purpose
Define the post-MoonProt comparison contract for the pre-MoonProt baseline. This contract specifies how future MoonProt-acquired records will be compared against the pinned pre-MoonProt baseline.

## Contract ID
`MFPB_0_16_RECONCILIATION_BASELINE_CONTRACT_V0`

## Scope
- **Baseline**: `pre-moonprot-baseline-v0.1` as defined in `docs/releases/pre-moonprot-baseline-v0.1.md`
- **Comparison**: Future MoonProt-acquired records only (no retroactive changes to baseline)
- **Direction**: One-way comparison from baseline to post-MoonProt state

## Comparison Dimensions

### Status Transitions
- **new_curated**: UniProt IDs not in baseline that appear in MoonProt with `curated` status
- **new_predicted**: UniProt IDs not in baseline that appear in MoonProt with `predicted` status
- **new_excluded_likely**: UniProt IDs not in baseline that appear in MoonProt with `excluded_likely` status
- **upgraded**: Baseline `predicted` or `excluded_likely` → MoonProt `curated`
- **downgraded**: Baseline `curated` → MoonProt `predicted` or `excluded_likely`
- **unchanged**: Same effective status in baseline and MoonProt

### ID Classification
- **baseline_only**: UniProt IDs present in baseline but not in MoonProt
- **moonprot_only**: UniProt IDs present in MoonProt but not in baseline
- **shared**: UniProt IDs present in both baseline and MoonProt

### Claim/Source Evidence
- **baseline_claims**: Source claim IDs contributing to each baseline UniProt ID
- **moonprot_claims**: MoonProt source claim IDs for each MoonProt UniProt ID
- **overlap_claims**: Claim IDs present in both baseline sources and MoonProt

### Checksums
- **baseline_output_sha256**: `7522eeeb58ad02578fdab35db6fef43ef82bab12aeee6c3137bc944b63f6d21a`
- **future_moonprot_sha256**: SHA-256 of post-MoonProt effective-status CSV (to be computed)
- **delta_sha256**: SHA-256 of the reconciliation report itself

### Precedence Reapplication
Post-MoonProt records must be aggregated using the same precedence rules:
1. `curated` > `predicted` > `excluded_likely` > `unresolved`

Precedence is reapplied to the union of:
- All baseline source claims (MoonDB + PlantMP)
- All MoonProt-acquired source claims

## Output Requirements

### Reconciliation Report
Must include:
- Baseline checksum verification (pass/fail)
- MoonProt checksum
- Combined checksum (baseline + MoonProt)
- Counts by transition category
- Full list of new UniProt IDs with their effective status
- Full list of upgraded/downgraded UniProt IDs with before/after status
- SHA-256 of the combined effective-status artifact

### Reconciliation Manifest
Must include:
- Reconciliation ID
- Baseline ID and checksum
- MoonProt input checksums
- Combined output checksum
- Timestamp
- Counts by all categories

## Constraints
- Baseline artifacts **must not** be modified
- Baseline checksums **must** be verified before comparison
- No network access during reconciliation validation
- Reconciliation is deterministic and byte-reproducible
- No NMF/control labels introduced during reconciliation
- No changes to raw data, source policies, or aggregation logic

## Explicit Non-Goals
- No retroactive modification of baseline
- No source freeze claim for reconciliation outputs
- No final release claim for reconciliation outputs
- No acquisition of additional data beyond MoonProt
- No merging of baseline with MoonProt into a single committed artifact
