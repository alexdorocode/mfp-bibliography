# ADR-006: Coverage-Only MoonProt Status Rows

- **Status**: Accepted

## Context

MoonProt MPID 103 is known absent (soft-404, recorded in the acquisition absent
log), and MPIDs 542, 543 and 626 are unresolved (no raw artifact). Until this
decision, the catalog build materialized the known-absent MPID as a source
record and a fallback protein entity, so an administrative absence occupied a
row in `mfp_proteins` (1,074 entities included one non-protein).

## Decision

MoonProt `known_absent` and `unresolved` MPIDs are coverage-only status rows:

- They never create source records, protein entities, identifiers, source
  assertions, fallback identities, or any protein ID eligible for GO
  annotation attachment.
- Only successfully parsed acquired HTML contributes MoonProt source records.
- MPID 103 remains exactly one `known_absent` coverage row carrying its
  absent-log provenance (URL, HTTP status, soft-404 marker, detection
  timestamp). MPIDs 542/543/626 remain `unresolved` coverage rows. Nothing
  else is inferred about these identifiers.
- The source-record conservation check compares against eligible acquired
  records, not all coverage rows; raw files that fail to parse fail the build
  loudly instead of being dropped.
- A legitimate acquired protein without a UniProt accession still receives a
  stable source-scoped fallback ID; this decision bans only status rows, not
  valid fallback identities.

## Consequences

- MVP counts: 1,165 source records (702 MoonProt), 1,073 protein entities,
  45 exact UniProt merges, `fallback_identity_records = 0`.
- The ID migration report for the prior snapshot includes a retired mapping
  for MPID 103's former administrative ID; it is annotated in
  `data/interim/reports/mfp_catalog_mvp_protein_id_migration_v1.notes.md`
  and the retired ID must not be referenced as a protein.
- Real-protein IDs under MFPB_PROTEIN_ID_V1 are unchanged.

## Alternatives considered

- Keeping known-absent records as `unresolved_identity` entities: conflates
  absence with protein observation and invites annotation of a non-protein.

## Deferred questions

- None; unresolved MPIDs remain an acquisition-scope question, not a catalog
  question.
