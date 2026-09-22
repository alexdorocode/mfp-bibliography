# Source Claim Policy v0.1

- **Policy ID**: `MFPB_0_7_SOURCE_CLAIM_POLICY_V0`
- **Config file**: `configs/source_claim_policy_v0.1.yaml`
- **Status**: active, declarative only

This policy defines how source-native claim labels map to repository operational
statuses. It does not create claim tables, canonical records, adapters, or
cross-source joins. Every source claim remains preserved individually; nothing
in this policy discards or overwrites source claims.

## Operational status vocabulary

| Status | Meaning |
|---|---|
| `curated` | Source-curated or confirmed claim; future MF-positive candidate. |
| `predicted` | Source prediction; exploratory only; never NMF/control. |
| `excluded_likely` | Likely claim; excluded operationally but retained audibly. |
| `unresolved` | Default for unknown, missing, or unmapped values. |

No claim is NMF by implication: absence of a claim never implies NMF.

## Label mappings

| Source | Field | Raw value | Operational status |
|---|---|---|---|
| `SRC_MOONDB` | `type` | `Curated` | `curated` |
| `SRC_MOONDB` | `type` | `Predicted` | `predicted` |
| `SRC_PLANTMP` | `type` | `confirmed` | `curated` |
| `SRC_PLANTMP` | `type` | `likely` | `excluded_likely` |
| `SRC_PLANTMP` | `type` | `predicted` | `predicted` |

Unknown or missing values resolve to `unresolved` for every source.

## Unmapped sources and fields

- `SRC_MULTIFACETEDPROTDB` has no observed status field; all its claims are
  `unresolved`.
- `SRC_MULTITASKPROTDB_II` `Models` values (`Phyre`, `ITasser`, etc.) are
  structural metadata, not claim evidence, and must never be mapped.

## Derived precedence

For the same UniProt ID, a future derived effective status resolves as:

`curated > predicted > excluded_likely > unresolved`

Precedence affects only that future derived effective status. All source
claims are preserved unchanged regardless of precedence resolution.
