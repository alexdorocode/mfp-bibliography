# Canonical Schema (Preliminary)

This model defines repository-level normalized source records. Controlled vocabularies are revisable policy values and are not automatic scientific truth assignments.

## Fields

| Field | Purpose | Type | Allowed values | Nullable | Example | Validation notes |
|---|---|---|---|---|---|---|
| `record_id` | Stable repository record key | string | non-empty | no | `SRC_MOONDB:abc123` | deterministic from source identity |
| `source_id` | Source registry identifier | string | non-empty | no | `SRC_MOONDB` | must map to source catalog |
| `source_record_id` | Native source record identifier | string | non-empty or `unknown` | no | `MDB_001` | required even if placeholder |
| `uniprot_id` | UniProt accession as provided/normalized | string/null | conservative string check | yes | `P12345` | strict accession rules deferred |
| `protein_name` | Protein name text | string/null | free text | yes | `Example protein` | preserve source semantics |
| `organism_raw` | Raw organism text | string/null | free text | yes | `Homo sapiens` | no taxonomy normalization yet |
| `scientific_label` | Repository scientific label policy field | string | `MF`,`NMF`,`EMF_candidate`,`unknown` | no | `unknown` | assigned by adapters/validation only |
| `evidence_tier` | Evidence characterization | string | `experimental_curated`,`literature_curated`,`computational_prediction`,`source_claim_only`,`unresolved` | no | `unresolved` | separate from label |
| `benchmark_role` | Downstream compatibility field for future benchmark assignment | string | `unassigned`,`target`,`control`,`excluded`,`unknown` | no | `unassigned` | independent of evidence tier; default remains `unassigned` in this repository |
| `source_version` | Source artifact version marker | string | non-empty or `unknown` | no | `unknown` | explicit placeholder required |
| `retrieved_at` | Retrieval/acquisition date | string | literal `unknown` OR ISO 8601 date-time (`YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`) | no | `2026-09-18T12:00:00Z` | strict calendar/accession semantics deferred |
| `raw_file_path` | Raw artifact path in repository | string | non-empty | no | `data/raw/moondb/file.csv` | must point to source artifact path |
| `raw_row_or_url` | Locator within raw source | string | non-empty | no | `row:42` | URL or row locator allowed |
| `transformation_id` | Transformation implementation identifier | string | non-empty | no | `normalize_moondb_v1` | required for derived outputs |
| `record_status` | Curation status | string | `valid`,`incomplete`,`ambiguous`,`excluded`,`duplicate_candidate` | no | `incomplete` | explicit unresolved handling |
| `notes` | Curator notes | string/null | free text | yes | `identifier unresolved` | optional |

## Controlled vocabularies

- `scientific_label`: `MF`, `NMF`, `EMF_candidate`, `unknown`
- `evidence_tier`: `experimental_curated`, `literature_curated`, `computational_prediction`, `source_claim_only`, `unresolved`
- `benchmark_role`: `unassigned`, `target`, `control`, `excluded`, `unknown`
- `record_status`: `valid`, `incomplete`, `ambiguous`, `excluded`, `duplicate_candidate`

Benchmark-role boundary: `benchmark_role` is present for downstream compatibility only. Until a separately approved benchmark protocol exists, repository records remain `unassigned`.
