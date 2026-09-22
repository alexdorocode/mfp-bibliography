# Source Claims Contract v0

- **Contract ID**: `MFPB_0_8_SOURCE_CLAIMS_CONTRACT_V0`
- **Schema file**: `data/curated/source_claims.schema.json`
- **Status**: active, schema-only; no adapters, no claims CSV, no cross-source joins

This contract defines the normalized **per-source claim** model: one record per
source-local field observation. It builds on `MFPB_0_7_SOURCE_CLAIM_POLICY_V0`
(`docs/source-claim-policy.md`), which maps source-native labels to operational
statuses. It is separate from the preliminary canonical source-record model
(`docs/canonical-schema.md`), which remains unchanged.

## Fields

| Field | Purpose | Type | Allowed values | Nullable | Example |
|---|---|---|---|---|---|
| `claim_id` | Stable claim key | string | non-empty | no | `SRC_MOONDB:1f2e3d4c5b6a7980` |
| `source_id` | Source registry identifier | string | non-empty | no | `SRC_MOONDB` |
| `source_record_id` | Native source record identifier | string | non-empty or `unknown` | no | `MDB_001` |
| `uniprot_id` | UniProt accession as provided | string/null | conservative string check | yes | `P12345` |
| `protein_name_raw` | Protein name exactly as in source | string/null | free text | yes | `Example protein` |
| `organism_raw` | Organism text exactly as in source | string/null | free text | yes | `Homo sapiens` |
| `raw_claim_field` | Source-native claim field name | string | non-empty | no | `type` |
| `raw_claim_value` | Source-native claim value | string | non-empty; `unknown` placeholder allowed | no | `Curated` |
| `operational_status` | Policy-resolved status | string | `curated`,`predicted`,`excluded_likely`,`unresolved` | no | `curated` |
| `primary_target_eligible` | Primary-target benchmark eligibility | boolean | true only for `curated` | no | `true` |
| `control_eligible` | Control benchmark eligibility | boolean | always `false` | no | `false` |
| `raw_file_path` | Raw artifact path in repository | string | non-empty | no | `data/raw/moondb/all_emf_and_curated.tsv` |
| `raw_row_or_url` | Locator within raw artifact | string | non-empty | no | `row:42` |
| `source_version` | Source artifact version marker | string | non-empty or `unknown` | no | `unknown` |
| `retrieved_at` | Retrieval date-time | string | literal `unknown` OR ISO 8601 date-time | no | `2026-09-22T10:00:00Z` |
| `transformation_id` | Transformation implementation identifier | string | non-empty | no | `claim_normalization_v0` |
| `record_status` | Curation status | string | `valid`,`incomplete`,`ambiguous`,`excluded`,`duplicate_candidate` | no | `valid` |
| `notes` | Curator notes | string/null | free text | yes | `identifier unresolved` |

## Guarantees

1. **Claim identity**: `claim_id` is deterministic from source identity and
   locator (`source_id`, `source_record_id`, `raw_file_path`,
   `raw_row_or_url`, `raw_claim_field`), via the `make_claim_id` helper in
   `src/mfp_bibliography/source_claims.py`.
2. **Curated-only target eligibility**: `primary_target_eligible=true` is
   permitted only for `operational_status=curated`; a `curated` claim with
   `primary_target_eligible=false` is a mismatch and is rejected. Both
   directions are enforced by the schema.
3. **Never control**: `control_eligible` is `false` for every claim. No claim
   is NMF by implication; absence of a claim never implies NMF.
4. **Raw provenance always required**: `raw_claim_field` and `raw_claim_value`
   are required even for `unresolved` claims; `raw_file_path` and
   `raw_row_or_url` are always required.
5. **No cross-source merging**: claims preserve duplicates and source-local
   rows. Cross-source aggregation, deduplication, and joins are out of scope
   for this contract.
6. **No derived status**: `effective_status` is forbidden in this contract.
   Any future derived effective status is a separate, explicitly approved
   artifact.

## Validation

Use `validate_claim` from `src/mfp_bibliography/source_claims.py` to validate
one in-memory claim record against the schema.
`scripts/validate_repository.py` checks that the schema file exists and is a
valid Draft 2020-12 schema.
