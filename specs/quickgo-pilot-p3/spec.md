# Specification: Stage P3 Offline Concordance Engine & Normalization

- **Document ID**: `SPEC-QUICKGO-PILOT-P3-001`
- **Feature Directory**: `specs/quickgo-pilot-p3/`
- **Target Repository**: `mfp-bibliography`
- **Authority Level**: Level 5 (Approved Increment Specification)
- **Status**: Implemented and Verified (2026-11-16; Commit `4906b2ee0fded7060038b0055d430ee1297c2f6a`, parent `dc761e00c8ddec64fce4652f2fca9a783ec6533d`)
- **Proposal Reference**: `docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md` (v1.5)
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), [`AGENTS.md`](../../AGENTS.md)

---

## 1. Scope & Objective

This specification governs the implementation and execution of **Stage P3 (Concordance Pipeline & Comparative Analysis)** of the `MFP_QuickV1` integration pilot. It delivers:
1. Four formal JSON Schema contracts (Draft 2020-12) for normalized pilot outputs.
2. An offline concordance engine (`quickgo_concordance.py`) and CLI runner (`build_quickgo_concordance_pilot.py`).
3. Execution and generation of four normalized CSV outputs and a run manifest isolated under `data/interim/pilot/quickgo_slice/`.
4. Comprehensive unit and contract tests verifying inventory preservation, empty-set null conventions, Policy C exclusion accounting, namespace-aware citation comparison, and deterministic bitwise stability.

### Non-Goals
- External database connection, API requests, or web downloads (100% offline).
- Modifying frozen raw schemas, fixtures, Tier A inputs, candidate releases, or ADRs.
- Classifier training, GO semantic similarity, ontology True Path expansion, or contextual functional triplet generation.
- Literature full-text parsing or scientific claim adjudication.

---

## 2. Input Dependencies & Invariants

All 8 input dependencies must have verified SHA-256 digests prior to execution:
1. `tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv` (`b8d508f6...4f6a`) [156 rows] (Git tracked)
2. `tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv` (`249a4cd9...aef1`) [8 rows] (Git tracked)
3. `tests/fixtures/quickgo_pilot/manifest.json` (`a6c08b0e...c09c`) (Git tracked)
4. `data/interim/pilot/functional_claims_pilot.csv` (`88a1f252...3348`) [44 rows] (Provisioned locally; Git ignored)
5. `data/interim/pilot/source_go_annotations_pilot.csv` (`949e5050...dda`) [353 rows] (Provisioned locally; Git ignored)
6. `data/interim/pilot/functional_coverage_pilot.csv` (`c29d2871...2e8d`) [20 rows] (Provisioned locally; Git ignored)
7. `data/interim/pilot/manifest.json` (`c6ecaed0...bf5b`) (Provisioned locally; Git ignored)
8. `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv` (`a2e6cde1...5bfc`) [2,322 rows] (Release candidate package)

> [!NOTE]
> Offline execution requires local provisioning of items 4–7 (`data/interim/pilot/`). A clean repository clone cannot reproduce interim pipeline runs without provisioning these fixtures.

---

## 3. Comparison Universes & Cardinalities

### 3.1 Denominator Coverage Universe (8 rows)
All 8 cohort accessions (`Q42525`, `Q9Y3E5`, `P0AFW0`, `P34788`, `P78007`, `P24228`, `A0A0H3CDS3`, `E6KMA1`) must be accounted for in `quickgo_coverage_pilot.csv`.

### 3.2 Gene Ontology Concordance Universe (72 rows)
The concordance universe $\mathbf{K} = (\text{accession}, \text{source\_id}, \text{aspect}, \text{policy\_id})$ consists of:
- **12 Verified (Accession, Source) Pairs**:
  1. `(Q42525, SRC_MOONPROT)`
  2. `(Q42525, SRC_MULTITASKPROTDB_II)`
  3. `(Q42525, SRC_PLANTMP)`
  4. `(Q9Y3E5, SRC_MULTITASKPROTDB_II)`
  5. `(P0AFW0, SRC_MOONPROT)`
  6. `(P0AFW0, SRC_MULTITASKPROTDB_II)`
  7. `(P34788, SRC_MULTITASKPROTDB_II)`
  8. `(P34788, SRC_PLANTMP)`
  9. `(P78007, SRC_MOONPROT)`
  10. `(P24228, SRC_MOONPROT)`
  11. `(E6KMA1, SRC_MOONPROT)`
  12. `(A0A0H3CDS3, SRC_MULTITASKPROTDB_II)`
- **3 GO Aspects**: `BP` (Biological Process), `MF` (Molecular Function), `CC` (Cellular Component).
- **2 Approved Policies**: `captured_inventory_overlap` (Policy B), `filtered_descriptive_overlap` (Policy C).
- **Total Cardinality**: $12 \times 3 \times 2 = \mathbf{72 \text{ rows}}$.

### 3.3 Reference Concordance Universe (12 rows under Option A)
The reference comparison unit $\mathbf{K}_{\text{ref}} = (\text{accession}, \text{protein\_id}, \text{source\_id})$ consists of exactly the 12 verified pairs evaluated at the protein entity / source record level.

---

## 4. Evaluability Rules & Mathematical Conventions

1. **Jaccard Formula**:
   $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
2. **Empty-Set Null Convention**:
   When $|A| = 0$ or $|B| = 0$, $J(A, B) = \text{null}$ and `status = "not_evaluable"`.
3. **Disjoint Non-Empty Sets**:
   When $|A| > 0$, $|B| > 0$, and $|A \cap B| = 0$, $J(A, B) = 0.0$ and `status = "evaluable"` (provided identity is compatible).
4. **Biological Identity Compatibility**:
   `identity_review_status == "no_discrepancy_noted"` is an inclusion gate. For `P34788` (`flagged_taxonomic_discrepancy`), counts are reported but $J = \text{null}$, `concordance_status = "not_evaluable"`, and `primary_non_evaluable_reason = "unresolved_biological_identity"`.
5. **Indeterminate vs Empty Inventories**:
   - When an inventory cannot be established (e.g. `source_record_outside_slice`, QuickGO `unlinked_in_database`, or undeclared aspect in MoonProt), term counts are `null` (not 0!).
   - When an inventory is observed to have 0 terms for an aspect (e.g. PlantMP for CC, or QuickGO for an aspect with 0 annotations), term count is `0`.
6. **Policy C Filtering Rules**:
   - Root terms (`GO:0008150`, `GO:0003674`, `GO:0005575`) are unconditionally excluded.
   - Rows carrying `evidence_code == "ND"` are excluded at row level.
   - Missing evidence codes are treated as unassessed (never classified as ND or non-ND).
   - A non-root term survives if at least one retained row carries it.
   - Exclusion accounting tracks `nd_matching_rows_count`, `root_matching_rows_count`, `nd_root_overlap_rows_count`, and net non-double-counted exclusions.
   - If sets were nonempty under Policy B but emptied under Policy C, reason is `empty_after_filtering`. If already empty, `empty_after_filtering` is never assigned.
7. **Reference Overlap Normalization & Semantic Closure**:
   - Namespace prefixes (`PMID:`, `GO_REF:`) are strictly preserved without cross-namespace conversion.
   - Numeric-to-PMID interpretation is strictly source-aware: applied only to known numeric citation fields (`multitaskprotdb_ii` and `plantmp`). Syntactic interpretability is descriptive comparison within standard namespaces, not external publication existence verification or claim-level evidence adjudication.
   - Opaque or unstructured reference tokens (e.g. text notes, homology commentary) are preserved diagnostically in `unresolved_reference_ids` and counted in `source_unresolved_references_count`, but strictly excluded from comparable identifier sets.
   - The PlantMP zero-overlap result on `Q42525` represents two nonempty, genuinely disjoint comparable identifier sets (`PMID:901436`, `PMID:12690178` vs QuickGO's 28 PMIDs), yielding $J = 0.0$, `evaluable`, and `complete`.
   - For `P24228` (MoonProt HTML parse failure), citation extraction failure represents an indeterminate reference inventory, yielding `source_references_count = null`, `shared_references_count = null`, `jaccard_similarity = null`, `reference_concordance_status = "not_evaluable"`, `comparison_completeness = "indeterminate"`, and `primary_non_evaluable_reason = "source_extraction_incomplete"`.
