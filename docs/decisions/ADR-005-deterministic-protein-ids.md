# ADR-005: Deterministic Protein IDs (Scheme MFPB_PROTEIN_ID_V1)

- **Status**: Accepted

## Context

The MVP catalog build assigned `protein_id` with `abs(hash(...)) % 10**6`. Python's
string `hash()` is salted per process, so the same inputs produced different IDs in
different runs, breaking byte reproducibility and making the IDs unusable as stable
foreign keys for the planned GO/evidence integration. The `10**6` modulo space also
risked silent collisions merging distinct accessions.

## Decision

Protein IDs are deterministic SHA-256 digests under versioned scheme
`MFPB_PROTEIN_ID_V1`:

- UniProt-resolved records: `MFP:U:<16 hex>` from the canonical accession
  (strip, first whitespace token, uppercase).
- Records without UniProt: source-scoped fallback `MFP:F:<source>:<16 hex>`
  from `(source_name, local_key)`; one entity per source record, never merged
  by display text.
- One canonical normalization function is reused at every identity site
  (`mfp_bibliography.normalization.normalize_uniprot_accession`).
- Digest length is 16 hex chars (documented); the build performs explicit
  collision detection and fails loudly if two distinct canonical keys claim the
  same ID.
- Cross-source automatic merging remains limited to exact normalized UniProt
  accession equality.

## Consequences

- IDs in the prior MVP snapshot (process-local `hash()` values) are not valid
  references; they are superseded by V1 IDs. A one-to-one migration report
  covers the existing snapshot (`data/interim/reports/
  mfp_catalog_mvp_protein_id_migration_v1.csv`). This migration is not a final
  release.
- Builds are byte-reproducible across processes and hash seeds, verified by
  tests that rebuild under different `PYTHONHASHSEED` values.
- Any future change to the scheme requires a new version ID and an updated ADR.

## Alternatives considered

- Keeping `hash()` with a fixed `PYTHONHASHSEED`: fragile, still collision-prone
  under modulo reduction, and undocumented as a runtime requirement.
- Full 64-hex digests: unnecessary for current scale; 16 hex with explicit
  collision detection is documented and checked.

## Deferred questions

- Whether fallback entities without UniProt should later be merged through a
  documented review workflow (never automatic).
