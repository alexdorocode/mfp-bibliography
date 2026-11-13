# Stages P1–P2 Completion Report: MFP_QuickV1 Evidence Integration Pilot

| Attribute | Specification Record |
|---|---|
| **Document Title** | Stages P1–P2 Completion Report: MFP_QuickV1 Evidence Integration Pilot |
| **Document ID** | `REPORT-PILOT-QUICKGO-P1-P2-2026-11-12` |
| **Document Location** | [`docs/reports/quickgo-pilot-p1-p2-completion-report.md`](quickgo-pilot-p1-p2-completion-report.md) |
| **Status** | **Completed — Frozen Inputs Ready for Stage P3** |
| **Date** | 2026-11-12 |
| **Revision** | **v1.3 (Final Pre-P3 Bounded Corrections & Specification Alignment)** |
| **Auditor / Architect** | Senior Scientific Software Auditor & Bioinformatics Data Architect |
| **Target Repository** | `mfp-bibliography` (in coordination with `protein-information-system`) |
| **Authority Level** | Level 6: Technical Completion Report for Human Review |
| **Governing Rules** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |

---

### Document Revision History

| Version | Date | Author | Description of Changes |
|---|---|---|---|
| **v1.0** | 2026-11-12 | Scientific Software Auditor | Initial completion report for Stages P1–P2 bounded execution. |
| **v1.1** | 2026-11-12 | Senior Scientific Software Auditor & Data Architect | Precision and consistency correction: (1) Corrected counting units to distinguish rows, pairs (95), triples (137), 4-tuples (156), and distinct references (59 PMIDs, 13 GO_REFs); (2) Documented the CSV empty field $\to$ loader $\to$ Python `None` / JSON `null` conversion sequence; (3) Bounded schema claims to this specific database capture; (4) Recorded ND and GO root-term policies as pending Stage P3 analytical decisions; (5) Clarified `ambiguous_identity` as a reserved, unsupported coverage status for the current cohort. |
| **v1.2** | 2026-11-12 | Senior Scientific Software Auditor & Bioinformatics Data Architect | Task `QUICKGO-PRE-P3-CLOSURE-001`: Reconciled with Stage P3 specification in proposal v1.2, converted documentation links to repository-relative markdown links, and added Section 9 ("Resume Next Session") detailing verified status, exact pending policy decisions, and minimal next action. |
| **v1.3** | 2026-11-12 | Senior Scientific Software Auditor & Bioinformatics Data Architect | Final pre-P3 bounded corrections: (1) Corrected empty-set Jaccard mathematics (0 when one side empty, undefined 0/0 when both empty; pilot convention proposes null to separate coverage gaps from observed disjoint inventories); (2) Removed unsupported ECO crosswalk prerequisite for filtering already captured legacy experimental codes under deferred Policy D; (3) Stated unequivocal 1:1 raw row preservation and deduplication-only-at-comparison rule; (4) Formalized biological identity compatibility as distinct evaluability condition and specified deterministic primary/secondary non-evaluable reason hierarchy; (5) Formulated annotation identifier using capture scope and database row ID, and removed protein_id truncation in concordance keys; (6) Added dedicated normalized coverage contract to proposed P3 deliverables and specified input provisioning requirements for clone reproducibility. |

---

## 1. Executive Summary

This report documents the completion of **Stages P1–P2** of the `MFP_QuickV1` evidence integration pilot, executed under the user's explicit scoped increment authorization.

The goal of this bounded increment was to establish formal validation contracts and obtain validated, frozen raw inputs for the eight-accession cohort from the local database `MFP_QuickV1`.

### 1.1 Deliverable Summary
- **Stage P1 (Contracts & Validation)**: Authoring of formal Draft 2020-12 JSON Schemas for raw annotations and raw coverage, an offline validation library (`quickgo_raw_validator.py`), and a comprehensive offline pytest suite (`test_quickgo_raw_contracts.py`).
- **Stage P2 (Export & Verification)**: Execution of a bounded read-only database export under a single connection with `REPEATABLE READ, READ ONLY` transaction isolation, zero database writes, and generation of a dedicated fixture manifest (`tests/fixtures/quickgo_pilot/manifest.json`).
- **Catalog Baseline Protection**: Verified that release candidate `mfp-catalog-candidate-v0.3.0` remained completely pristine before and after execution (`package_catalog_candidate.py --verify-package`).
- **Stopping Point Respected**: The pipeline stops strictly after export validation. Concordance calculation, transformation pipeline implementation (`build_quickgo_concordance_pilot.py`), and stages P3–P4 remain unimplemented pending separate human authorization.

---

## 2. Files Created or Modified

| Repository File Path | Action | Purpose / Content Description |
|---|---|---|
| [`docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md`](../roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md) | Modified | Aligned query roles, field provenance, taxonomic review flag for P34788, verbatim suspicious PMIDs, CSV null handling sequence, and removed qualitative overlap thresholds. |
| [`data/curated/raw_quickgo_annotations.schema.json`](../../data/curated/raw_quickgo_annotations.schema.json) | Created | Draft 2020-12 schema for raw annotation records exported from `protein_go_term_annotation`. Clarified bounded database scope and reader null conversion. |
| [`data/curated/raw_quickgo_coverage.schema.json`](../../data/curated/raw_quickgo_coverage.schema.json) | Created | Draft 2020-12 schema for raw denominator coverage accounting across the 8 cohort accessions. Clarified `ambiguous_identity` as reserved. |
| [`src/mfp_bibliography/quickgo_raw_validator.py`](../../src/mfp_bibliography/quickgo_raw_validator.py) | Created | Production validation module enforcing schema conformance, tuple uniqueness, reference regexes, and cross-file reconciliation. |
| [`tests/test_quickgo_raw_contracts.py`](../../tests/test_quickgo_raw_contracts.py) | Created | 26 offline unit, contract, and fixture tests covering synthetic edge cases and disk fixture conformance. |
| [`scripts/export_quickgo_pilot_fixtures.py`](../../scripts/export_quickgo_pilot_fixtures.py) | Created | Safe, credential-free exporter executing Query A and Query B inside a single REPEATABLE READ transaction. |
| [`tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv`](../../tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv) | Created | Frozen raw annotation export (156 rows) for the 6 annotated cohort members. |
| [`tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv`](../../tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv) | Created | Frozen raw denominator coverage export (8 rows) accounting for 100% of the cohort. |
| [`tests/fixtures/quickgo_pilot/manifest.json`](../../tests/fixtures/quickgo_pilot/manifest.json) | Created | Dedicated manifest with database provenance, SHA-256 hashes, Git context, reconciliation summary, and capture limitations. |
| [`docs/reports/quickgo-pilot-p1-p2-completion-report.md`](quickgo-pilot-p1-p2-completion-report.md) | Modified | Technical completion report, updated with precision counting units, null handling sequence, Stage P3 planning clarifications, and session continuity. |

---

## 3. Verification Executed

All checks were executed offline or under strict read-only mode:

1. **Schema Syntax Verification**:
   ```bash
   python3 -c "import json, jsonschema; [jsonschema.Draft202012Validator.check_schema(json.load(open(p))) for p in ['data/curated/raw_quickgo_annotations.schema.json', 'data/curated/raw_quickgo_coverage.schema.json']]"
   ```
   *Status: PASSED (Draft 2020-12 valid).*

2. **Scoped Contract & Fixture Test Suite**:
   ```bash
   pytest -q tests/test_quickgo_raw_contracts.py
   ```
   *Status: PASSED (26 of 26 tests passed in 0.44s).*

3. **Candidate Release Immutability Check**:
   ```bash
   python3 scripts/package_catalog_candidate.py --verify-package
   ```
   *Status: PASSED (Candidate mfp-catalog-candidate-v0.3.0 PACKAGE_VERIFY OK: inventory, hashes, row counts, primary keys and foreign keys consistent with MANIFEST.json).*

4. **Frozen Fixture Hash Conformance**:
   Verified that SHA-256 digests of `raw_quickgo_annotations.csv` and `raw_quickgo_coverage.csv` match `tests/fixtures/quickgo_pilot/manifest.json` exactly.

---

## 4. Annotation and Coverage Export Counts (Exact Counting Units)

The bounded export against `MFP_QuickV1` yielded the following verified counts, calculated directly from the frozen fixtures:

### 4.1 Raw Annotations Export Metrics (`raw_quickgo_annotations.csv`)
- **Total Exported Annotation Rows**: **156 rows**
- **Distinct Database Annotation IDs (`database_annotation_id`)**: **156** (strictly unique row primary keys; zero duplicates)
- **Distinct `(database_protein_id, go_id)` Pairs**: **95 pairs** (reconciles 100% with the sum of distinct GO terms across cohort members: $11 + 13 + 21 + 9 + 32 + 9 = 95$)
- **Distinct `(accession, go_id)` Pairs**: **95 pairs**
- **Distinct `(database_protein_id, go_id, evidence_code)` Triples**: **137 triples**
- **Distinct `(database_protein_id, go_id, evidence_code, publication_id)` 4-Tuples**: **156 4-tuples** (identical to row count; zero join-induced duplicates)
- **Reference Breakdown**:
  - Annotation rows with a numeric PMID: **93 rows** (59.62%)
  - Annotation rows with a canonical `GO_REF` CURIE: **63 rows** (40.38%)
  - Annotation rows with a null reference: **0 rows** (0.0%)
  - Annotation rows with an empty string: **0 rows** (0.0%)
  - **Distinct PMID Identifiers**: **59 distinct PMIDs** across the cohort
  - **Distinct `GO_REF` Identifiers**: **13 distinct `GO_REF` CURIEs** across the cohort
- **SHA-256 Digest**: `b8d508f6f980fb3aed676dae7c4d3275b188dcbe58438372280920e6cf704f6a`

### 4.2 Raw Denominator Coverage Export Metrics (`raw_quickgo_coverage.csv`)
- **Total Exported Rows**: **8 rows** (100.0% cohort completeness)
- **Status Breakdown**:
  - `annotations_available`: **6 accessions** (`Q42525`, `Q9Y3E5`, `P0AFW0`, `P34788`, `P78007`, `P24228`)
  - `zero_annotations_found`: **1 accession** (`A0A0H3CDS3`)
  - `unlinked_in_database`: **1 accession** (`E6KMA1`)
  - `absent_from_database`: **0 accessions**
  - `ambiguous_identity`: **0 accessions** (reserved and unsupported in current cohort)
- **SHA-256 Digest**: `249a4cd91117fec229cdaf9c579803dcb89d011e41ec2e5bf0eb0fb35eb8aef1`

---

## 5. Coverage Status and Exact Reconciliation for Every Cohort Accession

| Cohort Accession | Linked Database Protein ID | Database Coverage Status | Identity Review Status | Stored Annotation Rows | Distinct GO Terms | Detailed Fixture Reconciliation |
|---|---|---|---|---|---|---|
| **`Q42525`** | `HXK1_ARATH` | `annotations_available` | `no_discrepancy_noted` | **56** | **32** | 56 rows (33 PMID rows, 23 GO_REF rows). Distinct references: 20 PMIDs, 8 GO_REFs. Triples `(protein, go, ev)`: 49. Quads: 56. |
| **`Q9Y3E5`** | `PTH2_HUMAN` | `annotations_available` | `no_discrepancy_noted` | **24** | **9** | 24 rows (17 PMID rows, 7 GO_REF rows). Distinct references: 9 PMIDs, 3 GO_REFs. Triples `(protein, go, ev)`: 17. Quads: 24. |
| **`P0AFW0`** | `RFAH_ECOLI` | `annotations_available` | `no_discrepancy_noted` | **17** | **11** | 17 rows (9 PMID rows, 8 GO_REF rows). Distinct references: 5 PMIDs, 3 GO_REFs. Triples `(protein, go, ev)`: 17. Quads: 17. |
| **`P34788`** | `RS18_ARATH` | `annotations_available` | `flagged_taxonomic_discrepancy` | **28** | **21** | 28 rows (17 PMID rows, 11 GO_REF rows). Distinct references: 15 PMIDs, 5 GO_REFs. Triples `(protein, go, ev)`: 27. Quads: 28. Upstream taxonomic discrepancy flagged. |
| **`P78007`** | `LDH_MYCPN` | `annotations_available` | `no_discrepancy_noted` | **10** | **9** | 10 rows (3 PMID rows, 7 GO_REF rows). Distinct references: 2 PMIDs, 4 GO_REFs. Triples `(protein, go, ev)`: 9. Quads: 10. |
| **`P24228`** | `DACB_ECOLI` | `annotations_available` | `no_discrepancy_noted` | **21** | **13** | 21 rows (14 PMID rows, 7 GO_REF rows). Distinct references: 10 PMIDs, 5 GO_REFs. Triples `(protein, go, ev)`: 18. Quads: 21. |
| **`A0A0H3CDS3`** | `A0A0H3CDS3_CAUVN` | `zero_annotations_found` | `no_discrepancy_noted` | **0** | **0** | 0 annotation rows in fixture. Technical control for database annotation gaps. |
| **`E6KMA1`** | `null` (`""`) | `unlinked_in_database` | `no_discrepancy_noted` | **0** | **0** | 0 annotation rows in fixture. Technical control for unlinked database accessions (`protein_id IS NULL`). |

---

## 6. Biological Identity Warnings and Upstream Discrepancies

### 6.1 `P34788` Taxonomic Discrepancy
- **Empirical Observation**: `P34788` successfully resolved to database protein `RS18_ARATH` in `MFP_QuickV1`, yielding 28 annotation rows across 21 distinct GO terms.
- **Upstream Conflict**: In source databases (PlantMP Order 1, MultitaskProtDB-II Row 337), `P34788` is attributed to ***Spinacia oleracea* (Spinach)**. In UniProtKB and `MFP_QuickV1`, `P34788` indexes 40S ribosomal protein S18 from ***Arabidopsis thaliana***.
- **Handling in Pilot**: Technical accession matching is decoupled from biological identity confidence. The accession is flagged with `identity_review_status = "flagged_taxonomic_discrepancy"`. Technical join succeeds, but automatic biological claim transference between source descriptions and gene-level QuickGO annotations is blocked.

### 6.2 `Q42525` Source PMID Calibration
- In PlantMP raw records, reference `901436` appears to have a missing digit relative to true PubMed ID `9014361` (Jang et al., 1997). In compliance with repository rules, suspicious PMIDs are preserved verbatim as extracted; candidate corrections remain separately documented notes, not automatic replacements.

---

## 7. Technical Clarifications and Implementation Details

### 7.1 CSV Null Serialization & Reader Conversion Sequence
To prevent ambiguity in contract definitions, the conversion sequence for nullable fields is explicit:
$$\text{CSV empty field (\texttt{""})} \xrightarrow{\text{loader conversion (\texttt{parse\_csv\_value})}} \text{Python \texttt{None} / JSON \texttt{null}} \xrightarrow{\text{schema validation}} \text{Passes } \{\text{"type": ["string", "null"]}\}$$
- In CSV files, JSON `null` is serialized as an empty field (`""`).
- The reader (`read_raw_annotations_csv`) converts empty strings to Python `None` before validating against Draft 2020-12 schemas.
- Literal string tokens such as `"null"` or `"None"` in a CSV field remain strings; they are not converted to null and will fail schema regex validation.

### 7.2 Bounded Scope of Raw Contracts
- The regex pattern `^([0-9]+|GO_REF:[0-9]{7})$` in `raw_quickgo_annotations.schema.json` specifies the supported reference formats for this specific bounded `MFP_QuickV1` capture. It does **not** represent a universal specification of all reference types that QuickGO can return (e.g., AGRICOLA, Reactome).
- Syntactic schema validation confirms format conformance; it does **not** perform external identifier existence checks in PubMed/GO, scientific validity checks, or complete upstream API attribute verification.

### 7.3 Two-Letter Evidence Code Discovery (`ND` & `IC`) and Stage P3 Policy Deferral
- Row 39 (`P34788`, `RS18_ARATH`, `GO:0008150`, `ND`, `GO_REF:0000015`) preserves an annotation to the Biological Process root term `GO:0008150` under evidence code `ND` ("No biological Data available").
- A database-wide query confirmed that `protein_go_term_annotation` contains two valid 2-letter Gene Ontology evidence codes (`IC` and `ND`) among 22 distinct codes. The schema pattern was calibrated to `^[A-Z]{2,3}$`.
- **Planning Clarifications and Invariants for Stage P3**:
  - **Unequivocal Raw Preservation**: Every captured raw annotation row is preserved 1:1 in normalized annotation records (156 raw rows $\to$ 156 normalized annotation rows). Distinct database row IDs (`database_annotation_id`) are preserved intact. Deduplication occurs strictly when constructing comparison term sets ($S$ and $Q$), never by dropping raw observations. Missing source evidence codes are never invented.
  - Faithful raw preservation does **not** automatically imply analytical eligibility.
  - Stage P3 must explicitly define the treatment of `ND` annotations and GO root terms (`GO:0008150`, `GO:0003674`, `GO:0005575`).
  - `ND` evidence codes and root terms are **distinct methodological concepts**: not all root-term annotations carry `ND` evidence, and not all `ND` annotations are to root terms.
  - In Policy C, root terms are excluded unconditionally by term ID, whereas ND filtering excludes annotation rows with evidence code `ND`. A non-root term survives if supported by $\ge 1$ eligible non-ND row.
  - The Stage P3 specification must separate a complete inventory of captured identifiers from any filtered analytical comparison.
  - No filtering policy is implemented or silently approved by this documentation update.

### 7.4 Status Semantics of `ambiguous_identity`
- `ambiguous_identity` was included in the `quickgo_coverage_status` schema enum as a reserved status for potential upstream split or multi-entity mappings.
- In Query B and for the current 8-accession cohort, this status is **unsupported and unused** (0 records).
- It is strictly separate from `identity_review_status` (which flags biological discrepancies like `P34788`).
- Operational detection queries, database joins, and validation requirements for `ambiguous_identity` remain deferred prior to any future cohort expansion where split mappings could occur.

---

## 8. Readiness for Stage P3 and Next Governance Gate

### 8.1 Readiness Verdict
**The frozen inputs for the eight-accession cohort are VALIDATED, FROZEN, AND FULLY READY for Stage P3.**

### 8.2 What Stage P3 Would Consume
If approved, Stage P3 will operate 100% offline, consuming:
1. `tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv`
2. `tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv`
3. `tests/fixtures/quickgo_pilot/manifest.json`
4. Existing Tier A pilot tables: `data/interim/pilot/functional_claims_pilot.csv`, `source_go_annotations_pilot.csv`, `functional_coverage_pilot.csv`

### 8.3 Remaining Analytical Decisions for Stage P3 (Pending Separate Approval)
Prior to implementing Stage P3, the maintainers and scientific lead must decide:
1. **Qualifier Handling Policy**: Formalizing `qualifier_status = "not_captured"` with documented caveats barring negative functional inferences.
2. **Exact Overlap Reporting Metric**: Defining exact term intersection $|S \cap Q|$ and Jaccard similarity across deduplicated `go_id` sets per protein and aspect.
3. **ND Evidence Policy**: Deciding whether `ND` annotations are retained in the full catalog inventory but excluded from specific functional concordance metrics.
4. **GO Root-Term Policy**: Deciding whether root terms (`GO:0008150`, `GO:0003674`, `GO:0005575`) are retained in the full catalog inventory but excluded from functional concordance calculations.
5. **Output Routing**: Confirming isolation under `data/interim/pilot/quickgo_slice/` to preserve candidate release v0.3.0 and Tier A pilot artifacts.

Execution of Stage P3 is **NOT** authorized by the current increment and will not proceed without explicit human sign-off.

---

## 9. Resume Next Session (`QUICKGO-PRE-P3-CLOSURE-001`)

This section establishes the operational checkpoint for resuming work in the next session.

### 9.1 Implementation and Verification Status of Stages P1–P2
- **Status**: **Completed, verified, frozen, and clean.**
- **Contracts**: Draft 2020-12 JSON schemas (`raw_quickgo_annotations.schema.json`, `raw_quickgo_coverage.schema.json`) authored and validated.
- **Validation Engine**: Offline validator `quickgo_raw_validator.py` fully operational.
- **Test Suite**: 26 of 26 tests in `tests/test_quickgo_raw_contracts.py` passing offline.
- **Frozen Fixtures**: Exported and verified under `tests/fixtures/quickgo_pilot/` with cryptographic digests recorded in `manifest.json`.
- **Baseline Protection**: Package integrity check for `mfp-catalog-candidate-v0.3.0` passes cleanly.

### 9.2 Stage P3 Specification Status
- **Status**: **Specification complete in Proposal Revision v1.3 ([`docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md`](../roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md)); awaiting human approval.**
- **Research Question**: Formulated verbatim to govern concordance scope and prevent scope creep.
- **Analytical Policies**: Defined as a unified policy framework (Policies A through E) to maintain separation between raw inventory preservation and filtered analytical comparisons.
- **Comparison Units & Metrics**: Defined on keys `(accession, source_id, aspect, policy_id)`, sets $S$ and $Q$, symmetric difference sets, and conditional Jaccard similarity.
- **Empty-Set Mathematics and Analytical Convention**: In standard mathematics, exactly one set empty yields $\frac{0}{|S \cup Q|} = 0.0$; both sets empty yields a zero denominator ($\frac{0}{0}$, undefined). This pilot proposes $J = \text{null}$ whenever either side is empty as an explicit analytical convention separating insufficient comparison coverage from observed disjoint nonempty inventories ($J = 0.0$).
- **Explicit Evaluability Conditions**: Biological identity compatibility (`identity_review_status == "no_discrepancy_noted"`) is an explicit condition separate from nonempty term sets ($|S| > 0$ and $|Q| > 0$).
- **Simultaneous Non-Evaluable Reasons**: Handled deterministically with a primary code assigned by strict precedence (`unresolved_biological_identity` $\to$ missingness $\to$ zero terms $\to$ empty after filtering) and secondary diagnostics preserving all simultaneous conditions.
- **Accession `P34788` Decoupling**: Technical accession diagnostics are preserved and inspectable while biological comparability is marked unresolved; all 8 accessions remain accounted for in denominator coverage.
- **Deterministic Identifiers**: `annotation_id` bound to capture scope and database integer row PK (`MFP:QGA:<capture_id>:<db_id>`); `concordance_id` uses full comparison key without truncation.
- **Proposed Deliverables**: Includes contracts for every normalized output (`external_quickgo_annotations.schema.json`, `quickgo_coverage.schema.json`, `quickgo_concordance.schema.json`). Explicitly noted: no P3 files may be created now.

### 9.3 Proposed Policies Requiring Explicit Human Approval
Before implementation of Stage P3 can begin, explicit human sign-off is required on the following specific policies:
1. **Root-Term Exclusion in Policy C**: Excluding uninformative GO root terms (`GO:0008150`, `GO:0003674`, `GO:0005575`) from filtered descriptive concordance metrics while preserving them in Policy A/B raw inventories.
2. **`ND` Evidence Exclusion in Policy C**: Excluding annotations with evidence code `ND` ("No biological Data available") from filtered descriptive concordance metrics, with non-root terms surviving if supported by $\ge 1$ eligible non-ND row.
3. **Qualifier Neutrality (`qualifier_status = "not_captured"`) and Caveats**: Treating QuickGO qualifiers as neutral rather than positive assertions, accompanied by explicit caveats prohibiting negative functional inferences from absence of experimental annotations.
4. **Deferred Experimental Sensitivity in Policy D**: Deferring the 6-code legacy experimental sensitivity extension (`EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`) because it is outside minimum Stage P3 scope (not due to an unapproved ECO crosswalk, since legacy codes are already captured as 3-letter strings). Execution of this extension is neither authorized nor implemented in Stage P3.

### 9.4 Technical & Provisioning Prerequisites and Governance Gate
- **Technical & Provisioning Prerequisites**: The frozen raw inputs (`tests/fixtures/quickgo_pilot/`) are locally present and verified, but require commitment to Git to be reproducible from a fresh clone without database access. Implementation of Stage P3 additionally requires authoring and approving implementation contracts (`external_quickgo_annotations.schema.json`, `quickgo_coverage.schema.json`, `quickgo_concordance.schema.json`) and the concordance calculation engine.
- **Environmental Prerequisites**: Zero live database or external network dependencies once fixtures are provisioned.
- **Governance Gate**: **BLOCKED SOLELY ON HUMAN REVIEW AND APPROVAL OF STAGE P3 SPECIFICATION (PROPOSAL v1.3).** In accordance with [`AGENTS.md`](../../AGENTS.md) §1.1, §4, and §6, no implementation of Stage P3 may begin without explicit sign-off.

### 9.5 Next Authorized Activity
- **Current Authorized Scope**: Specification authoring and documentation reconciliation only (`QUICKGO-PRE-P3-CLOSURE-001`).
- **Next Authorized Activity**: **NONE** until human decision on Proposal v1.3 and Stage P3 authorization.

### 9.6 Minimal Next Action for Tomorrow
1. Human maintainer reviews Proposal v1.3 ([`docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md`](../roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md)) and Completion Report v1.3 ([`docs/reports/quickgo-pilot-p1-p2-completion-report.md`](quickgo-pilot-p1-p2-completion-report.md)).
2. Maintainer explicitly decides whether to approve, modify, or reject Proposed Policies A through E.
3. Upon written authorization, the agent implements Stage P3 under a tightly bounded task (authoring schemas, offline concordance calculation engine, isolated output generation, and unit tests).
