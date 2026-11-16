# Plan: Stage P3 Offline Concordance Engine & Normalization

- **Document ID**: `PLAN-QUICKGO-PILOT-P3-001`
- **Specification Reference**: [`specs/quickgo-pilot-p3/spec.md`](spec.md)
- **Status**: Executed & Completed Implementation Plan (2026-11-16; Commit `4906b2ee0fded7060038b0055d430ee1297c2f6a`)

---

## 1. Staged Execution Strategy

The implementation proceeds in 5 discrete, sequential stages:

```
Stage 1: Contract Schemas
  └─ Author 4 Draft 2020-12 JSON schemas in data/curated/
       │
Stage 2: Core Concordance Engine & Validator
  └─ Implement src/mfp_bibliography/quickgo_concordance.py
       │
Stage 3: Comprehensive Test Suite & Synthetic Fixtures
  └─ Implement tests/test_quickgo_concordance.py & fixtures
       │
Stage 4: CLI Runner & Offline Execution
  └─ Implement scripts/build_quickgo_concordance_pilot.py
  └─ Execute offline to generate data/interim/pilot/quickgo_slice/
       │
Stage 5: Verification & Proposal Revision Consolidation
  └─ Verify 16 acceptance criteria, run regressions, update docs
```

---

## 2. Component Architecture & Reuse

- **Reuse**:
  - `jsonschema.Draft202012Validator` for strict schema checking.
  - CSV empty string $\to$ `None` parsing pattern from `quickgo_raw_validator.py`.
  - Deterministic identifier generators from `mfp_bibliography` conventions.
  - Verification utilities from `scripts/package_catalog_candidate.py`.
- **New Modules**:
  - `src/mfp_bibliography/quickgo_concordance.py`: Normalization loaders, Policy B/C set constructors, diagnostic assigners, reference normalizers, and cross-record validators.
  - `scripts/build_quickgo_concordance_pilot.py`: End-to-end runner reading the 8 verified inputs, writing outputs to `data/interim/pilot/quickgo_slice/`, and generating `manifest.json`.

---

## 3. Testing Strategy

1. **Schema Check Tests**: Verify all 4 JSON Schemas are valid Draft 2020-12 documents.
2. **Edge-Case Unit Tests**:
   - Bijective 156-row annotation mapping.
   - Denominator coverage (8 accessions).
   - Universe enumeration (72 rows).
   - Disjoint nonempty sets $\to J = 0.0$, evaluable.
   - One-sided empty $\to J = \text{null}$, not_evaluable.
   - Both-sided empty $\to J = \text{null}$, not_evaluable.
   - Identity incompatibility gate (`P34788`) $\to J = \text{null}$, unresolved identity reason.
   - Policy C exclusion accounting (ND, root, overlap, non-double-counting).
   - Missing evidence code handling (unassessed, never classified as ND/non-ND).
   - Reference normalization, distinct namespaces (`PMID:` vs `GO_REF:`), no cross-conversion.
   - Deterministic row ordering and bitwise stability.
3. **Fixture Integration Tests**: Run concordance on actual disk fixtures and verify outputs against schemas.
