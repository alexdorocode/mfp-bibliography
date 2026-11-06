# Synthetic Fixtures for Functional Normalization Contracts

This directory contains **purely synthetic test fixtures** designed to verify:
1. JSON Schema syntax and validation for `functional_claims` and `functional_coverage`.
2. Cross-record dataset invariants (uniqueness, referential integrity, tie-breaking ordering, denominator coverage).
3. CSV serialization, round-trip fidelity, null vs empty-string representation, and delimiter escaping.

> [!IMPORTANT]
> **No Real Biological Data**: The identifiers, accessions, statements, and scores in these fixtures are synthetic placeholders (`P00001`, `MFP:U:0123456789abcdef`, `synthetic enzyme activity`). They do not represent real experimental findings, curated scientific assertions, or approved biological ground truth.
