# Effective Status Aggregation Contract (MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0)

## Purpose
Define the derived per-UniProt aggregation contract for a future cross-source
effective-status table. This contract specifies how validated source claims are
aggregated into a single effective status per UniProt ID.

## Contract ID
`MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0`

## Input
- Validated source claims only (from MoonDB, PlantMP, or other imported sources)
- Source claims preserve every source row and raw label
- No raw mutation or source-claim modification

## Aggregation Rules

### Grouping
- Group **only** by non-empty `uniprot_id`
- Blank/missing UniProt IDs do not aggregate; produce explicit excluded records
- Duplicates remain distinct claims and affect `claim_count`

### Precedence (highest to lowest)
1. `curated`
2. `predicted`
3. `excluded_likely`
4. `unresolved`

The effective status is the highest-precedence status present in the grouped claims.

### Constraints
- `predicted` and `excluded_likely` are never NMF/control
- No claim implies no NMF conclusion
- Output never includes MF/NMF, evidence tier, benchmark role, target/control eligibility
- Aggregation is deterministic and order-independent

## Output Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `uniprot_id` | string | UniProt accession (grouping key) |
| `effective_status` | string | Highest-precedence operational status |
| `source_ids` | array[string] | All contributing source IDs |
| `claim_ids` | array[string] | All contributing claim IDs |
| `status_set` | array[string] | All distinct operational statuses in group |
| `has_curated_claim` | boolean | True if any claim has status `curated` |
| `has_predicted_claim` | boolean | True if any claim has status `predicted` |
| `has_excluded_likely_claim` | boolean | True if any claim has status `excluded_likely` |
| `has_unresolved_claim` | boolean | True if any claim has status `unresolved` |
| `claim_count` | integer | Total number of claims in group |
| `source_count` | integer | Number of distinct sources in group |
| `aggregation_policy_id` | string | Policy identifier (contract version) |
| `transformation_id` | string | Transformation identifier |
| `record_status` | string | Record status |
| `notes` | string|null | Optional notes |

## Schema
See `data/curated/effective_status.schema.json` for JSON Schema validation.

## Implementation
Pure aggregation helper: `src/mfp_bibliography/effective_status.py`

## Explicit Non-Goals
- No real effective-status CSV creation from MoonDB/PlantMP
- No NMF/control label inference
- No raw HTML, index, checksums, results, or error log modification
- No MoonProt docs, raw artifacts, manifests, policies, adapters, or audits modification
