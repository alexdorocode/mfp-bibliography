# Five-Source Descriptive Study Plan (candidate `mfp-catalog-candidate-v0.2.0`)

> **Scope warning.** These are analyses of *catalog coverage, overlap and
> composition*. They are NOT counts of validated articles, GO-supported
> functions, or the biological prevalence of multifunctionality. No
> statistical significance claims are made or implied.

Design-only document. Inputs are exclusively the packaged CSVs in
[`releases/mfp-catalog-candidate-v0.2.0/`](../../releases/mfp-catalog-candidate-v0.2.0/);
grains and columns follow its
[`DATA_DICTIONARY.md`](../../releases/mfp-catalog-candidate-v0.2.0/DATA_DICTIONARY.md).
Authoritative counts:
[`MANIFEST.json`](../../releases/mfp-catalog-candidate-v0.2.0/MANIFEST.json)
(`measured_counts`).

## Pipeline (minimal)

1. **Verify offline first**:
   `PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package`
   (PACKAGE_VERIFY; exit 0 required before analysis).
2. **Read packaged CSVs only** — no `data/raw/`, `data/interim/` or
   `data/processed/` dependency, no network, no rebuild.
3. **Record provenance** in `analysis_manifest.json`: candidate path, catalog
   contract `MFPB_0_19_MFP_CATALOG_MVP_V2`, protein ID scheme
   `MFPB_PROTEIN_ID_V1`, and the packaged-input SHA-256 hashes copied from
   `MANIFEST.json` (`packaged_outputs`).
4. **Emit outputs to a NEW location** `analysis/five-source-v0.2.0/`
   (deterministic aggregate CSVs + figures). Never write inside the hashed
   candidate. At implementation time the directory must be added to
   `.gitignore` and outputs treated as reproducible, not immutable evidence.
5. **Validate conservation** (invariants below) after every aggregate; abort
   non-zero on violation. Empty fields are counted as missing, never imputed.
6. **Figures**: implemented with the Python standard library only —
   deterministic, escaped SVG written directly by each analysis script. No
   external plotting package is required or assumed; aggregate CSVs and
   figures are always produced together.

## Questions (prioritized)

### Reproduction index (Q1–Q6)

Prerequisite: the packaged candidate must be intact; every command below
runs the offline PACKAGE_VERIFY gate first
(`PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package`)
and publishes nothing if it fails. All commands accept optional
`--candidate-dir` and `--output-dir` flags; defaults below. Numeric results
live in each output's provenance manifest, not here.

| Question | Command (default output) |
|---|---|
| Q1 | `PYTHONPATH=src python scripts/analyze_question1.py` → `analysis/five-source-v0.2.0/q1_records_vs_entities/` |
| Q2 | `PYTHONPATH=src python scripts/analyze_question2.py` → `analysis/five-source-v0.2.0/q2_source_overlap/` |
| Q3 | `PYTHONPATH=src python scripts/analyze_question3.py` → `analysis/five-source-v0.2.0/q3_sources_per_protein/` |
| Q4 | `PYTHONPATH=src python scripts/analyze_question4.py` → `analysis/five-source-v0.2.0/q4_moonprot_coverage/` |
| Q5 (v2) | `PYTHONPATH=src python scripts/analyze_question5.py` → `analysis/five-source-v0.2.0/q5_status_labels_v2/` |
| Q6 | `PYTHONPATH=src python scripts/analyze_question6.py` → `analysis/five-source-v0.2.0/q6_canonical_completeness/` |

Outputs are deterministic and byte-stable; reruns are idempotent for
identical bytes and refuse to overwrite different bytes (use a new analysis
version instead).

### Q1. Source records vs protein entities (separate units)
Title: "Records per source and unique protein entities".
Research question: how do source-observation counts relate to merged
entities? Inputs: `mfp_source_records.csv`, `mfp_proteins.csv`; join key
`protein_id` (record → protein). Units: source record (denominator 2,962)
and protein entity (denominator 2,322) — reported as two panels, never
mixed. Aggregation: count rows per `source_name`; count distinct
`protein_id` once. Missing status: none involved. Invariant: per-source
counts equal `source_record_counts` (351/702/1103/694/112); distinct
proteins = 2,322. Allowed: describing catalog coverage. Forbidden:
subtracting entities from records as a "merge count" (merges are a separate
metric, 463, accessions claimed by ≥2 sources).

### Q2. Source overlap by exact source set
Title: "Protein overlap across sources (exclusive combinations)".
Research question: which source combinations claim the same proteins?
Input: `mfp_source_records.csv`; key: distinct `(protein_id, source_name)`
pairs (deduplicate within source: a source claiming a protein twice counts
once). Unit: protein entity; denominator 2,322. Aggregation: each protein is
assigned to exactly one **exclusive** combination (its exact set of claiming
sources), so combination bins are mutually exclusive and sum to 2,322;
inclusive pairwise co-occurrence may be reported as a secondary matrix where
each pair is counted once per protein that has both sources. Missing status:
absence from a source is absence of a claim, never negative evidence.
Invariant: proteins with ≥2 sources = 463 = `exact_uniprot_merge_count`.
Allowed: overlap description. Forbidden: interpreting overlap as
confirmation, quality, or biological importance.

### Q3. Sources-per-protein distribution
Title: "Number of distinct sources per protein".
Research question: how concentrated is multi-source membership? Inputs and
keys: as Q2 (distinct `(protein_id, source_name)`). Unit: protein entity;
denominator 2,322; bins = 1..5 sources. Invariant: bins sum to 2,322 (current
candidate: 1 source 1,859; 2 sources 361; 3 sources 83; 4 sources 19; 5
sources 0). Allowed: distribution description. Forbidden: reading
"more sources" as stronger evidence of multifunctionality.

### Q4. MoonProt MPID coverage
Title: "MoonProt snapshot coverage (MPIDs 1–706)".
Research question: what does the acquired snapshot cover? Input:
`mfp_coverage.csv`; unit: MPID; denominator 706 (declared snapshot universe).
Aggregation: count `status` values. Invariant: 702 acquired / 1 known absent
(MPID 103) / 3 unresolved (542, 543, 626); contiguous 1..706. Allowed:
describing acquisition gaps. Forbidden: treating known-absent or unresolved
MPIDs as negative examples, non-proteins in analyses, or evidence about
absent proteins.

### Q5. Source-status composition (original statuses only)
Title: "Source-provided status labels, by source".
Research question: what status labels do sources themselves provide? Input:
`mfp_source_records.csv` only. Unit: source record; denominators:
per-source record counts. Q5 v2 (the current, provenance-corrected result)
groups SOURCE-PROVIDED labels by `raw_claim_value` (verbatim spelling and
case, after verifying `raw_claim_field` per source); the repository's
policy-mapped `source_status` (e.g. PlantMP `likely` → `excluded_likely`)
is reported SEPARATELY and is never called verbatim; `SRC_MOONPROT`'s
`valid` is a loader-generated technical status, shown apart from
source-provided labels and never as an experimental evidence tier.
`SRC_MULTIFACETEDPROTDB` (1,103) and `SRC_MULTITASKPROTDB_II` (694) provide
no source status and appear as `not_provided`. Invariant: availability
counts per source (including `not_provided`) sum to `source_record_counts`.
Allowed: composition description. Forbidden: cross-source label
harmonization, ranking sources by label mixes, or calling
`operational_status` a scientific label.

The packaged `DATA_DICTIONARY.md` description of `source_status` is
imprecise — see the
[candidate erratum](../releases/mfp-catalog-candidate-v0.2.0.md) and the
[Q5 v2 output README](../../analysis/five-source-v0.2.0/q5_status_labels_v2/README.md)
for the corrected semantics. The earlier Q5 v1 output is superseded, not
deleted; it remains byte-unchanged on disk and must not be cited.

### Q6. (Optional) Metadata completeness in `mfp_proteins.csv`
Title: "Completeness of canonical protein fields".
Research question: how complete are packaged metadata fields? Input:
`mfp_proteins.csv` only; unit: protein entity; denominator 2,322. Fields
actually present and comparable: `canonical_uniprot_accession` (2,322),
`entity_status` (2,322), `canonical_name` (2,056), `canonical_organism`
(763). `canonical_gene` and `taxonomy_id` are empty throughout — defer them.
Invariant: field counts ≤ 2,322 and denominators stated. Allowed:
completeness reporting. Forbidden: interpreting missing metadata as source
error or protein absence.

## Deferred analyses
GO–article support, article counting, function prevalence, and any
article-level figure are deferred: the candidate contains no verified
article-to-GO relations (see
[release notes](../releases/mfp-catalog-candidate-v0.2.0.md)). Cross-source
label comparison beyond verbatim display is out of scope
([ADR-004](../decisions/ADR-004-evidence-label-benchmark-separation.md)).
