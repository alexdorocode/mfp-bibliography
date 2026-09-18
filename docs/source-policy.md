# Source Policy

1. **Raw-data immutability**: files under `data/raw/` are append-only source artifacts.
2. **No manual raw edits**: corrections are new artifacts or documented superseding entries, never in-place edits.
3. **Reproducible transformations**: every transformation must be script/function based and versioned.
4. **Provenance preservation**: every derived record must carry source and locator metadata.
5. **Reversible normalization**: normalized fields must retain the ability to trace back to source locators.
6. **Duplicate handling**: potential duplicates are flagged as `duplicate_candidate`; no silent merges.
7. **Missing values and unresolved identifiers**: retain explicit `unknown`/null markers and review queues.
8. **Claim separation**: source claims are not repository-level scientific assertions by default.
9. **No silent exclusions**: dropped or filtered records must be explicitly logged with rationale.
