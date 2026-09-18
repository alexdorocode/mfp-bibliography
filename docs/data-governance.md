# Data Governance

## Roles

- **Importer**: adds source artifacts and initial manifest entries.
- **Reviewer**: verifies policy adherence, provenance fields, and source terms notes.
- **Release maintainer**: produces immutable release package and validation outputs.
- **Correction proposer**: submits additive corrections without rewriting source history.

## Corrections without history rewrite

Corrections are submitted as new artifacts, manifest updates, and release notes. Existing raw artifacts remain unchanged.

## Checksums, manifests, validation, releases

- Manifests track per-artifact metadata.
- SHA-256 checksums are stored in `data/manifests/file_checksums.sha256`.
- Validation reports are generated before release tagging.
- Release bundles include catalog snapshot, manifests, checksums, and validation results.

## Audit trail expectations

Every release must allow reviewers to trace curated records to source files/locators and transformation identifiers.

## Third-party terms and attribution

License/terms and attribution are recorded per source in the source catalog and manifest notes as `to_be_verified` until confirmed.
