# Verification Record: Three-Source Catalog Inventory & Biological Identity Audit Specification

- **Document ID**: `VERIF-THREE-SOURCE-INVENTORY-AUDIT-001`
- **Feature Directory**: `specs/three-source-inventory-audit/`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 5 (Increment Verification Record; Documentary Contract Verification Only)
- **Status**: **Documentary Verification Completed; Implementation & Execution Strictly Deferred Pending Human Authorization**
- **Baseline Git HEAD**: `f9d9fba58a5a03a949c346a5956b8795b312b24d`
- **Specification Reference**: [`specs/three-source-inventory-audit/spec.md`](spec.md)
- **Plan Reference**: [`specs/three-source-inventory-audit/plan.md`](plan.md)
- **Tasks Reference**: [`specs/three-source-inventory-audit/tasks.md`](tasks.md)
- **Roadmap Reference**: [`docs/roadmap/pilot-to-three-source-validation-roadmap.md`](../../docs/roadmap/pilot-to-three-source-validation-roadmap.md)
- **Verification Date**: 2026-11-20
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md) §1, §4, §5

---

## 1. Executive Summary & Verification Matrix

This verification record registers the read-only pre-implementation checks, baseline input table audits, and contract integrity reconciliations performed during the authoring and consistency review of the **Three-Source Catalog Inventory & Biological Identity Audit** specification package.

In strict adherence to repository SDD protocol ([`AGENTS.md`](../../AGENTS.md) §4), **no implementation code was written, no pipeline was executed, no test suite was run, and no database or network calls were made**. All implementation and execution activities remain formally deferred pending human review and sign-off.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             DOCUMENTARY VERIFICATION STATUS (CURRENT TURN: 2026-11-20)                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Git Repository HEAD & Empty Index Check ────────────────────────► [VERIFIED / OK]   │
│ 2. Candidate Release v0.3.0 Tables Presence & Digests ─────────────► [VERIFIED / OK]   │
│ 3. 3-Source Record Census & Multiplicity Breakdown ────────────────► [VERIFIED / OK]   │
│ 4. Triple Intersection 3-Tier Reconciliation (4 / 12 / 12) ────────► [VERIFIED / OK]   │
│ 5. Relative Markdown File Link Integrity ──────────────────────────► [VERIFIED / OK]   │
│ 6. Implementation Code, Schemas & Synthetic Tests (Gate 1) ────────► [PENDING AUTH]    │
│ 7. Technical Code Review & Pre-Commit Audit (Gate 2) ──────────────► [PENDING AUTH]    │
│ 8. Offline Read-Only Audit Pipeline Execution (Gate 3) ────────────► [PENDING AUTH]    │
│ 9. Published Audit Tables & Descriptive Synthesis (Gate 4) ────────► [PENDING AUTH]    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Documentary Verification Checks Performed

### 2.1 Check 1: Git Repository Baseline & Empty Index Audit
- **Command Run**: `git rev-parse HEAD; git branch --show-current; git status --short`
- **Observed HEAD**: `f9d9fba58a5a03a949c346a5956b8795b312b24d` (PIL-04.1B v0 closure commit).
- **Observed Branch**: `feature/functional-normalization`.
- **Index State**: Empty (`0` staged files).
- **Working Tree State**: Unstaged edits in `specs/quickgo-pilot-go-aspect-enrichment/spec.md` and untracked reports preserved intact (clean index, not clean tree).
- **Status**: **VERIFIED / OK**.

### 2.2 Check 2: Candidate Release v0.3.0 Artifact Inspection
- **Artifacts Verified**:
  * `releases/mfp-catalog-candidate-v0.3.0/mfp_source_records.csv`: SHA-256 `89daf82e254c02943a98d11e7391504596ba86c607f33bf10bf39ae64b023129`
  * `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv`: SHA-256 `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc`
  * `releases/mfp-catalog-candidate-v0.3.0/mfp_identifiers.csv`: SHA-256 `27afb04dd673ca81ea8f11b20b034fe8d4cb5a1efd41f140b1921306b2d9513c`
  * `releases/mfp-catalog-candidate-v0.3.0/mfp_assertions.csv`: SHA-256 `b3843dcdc99f6c172ce2ff49480024d12c4f239a52e326e23f86a4d80dc14fd5`
  * `releases/mfp-catalog-candidate-v0.3.0/mfp_coverage.csv`: SHA-256 `46889dcad5cab7907803c2f9e3ec127ad44da67dc133b03a56ff7de8bce9ad49`
  * `releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json`: SHA-256 `ae811d28bad3bdd05be8df2d02607e056b4b4f5df7151c783b1bbac934c5963e`
- **Status**: **VERIFIED / OK**.

### 2.3 Check 3: Three-Source Census & Multiplicity Breakdown
- **Method**: In-memory Python inspection of `mfp_source_records.csv` filtering `source_name` $\in$ (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`).
- **Results**:
  * MoonProt: $702$ records, $657$ unique protein entities, $45$ surplus records representing internal multiplicity.
  * MultitaskProtDB-II: $694$ records, $685$ unique protein entities, $9$ surplus records representing internal multiplicity.
  * PlantMP: $112$ records, $110$ unique protein entities, $2$ surplus records representing internal multiplicity.
  * Total: $1,508$ source records, $1,452$ source-entity pairs, $56$ surplus multiplicity records, $1,179$ unique protein entities in the integrated union ($M \cup T \cup P$).
  * Total Row Conservation: Total accounted physical rows equal total loaded physical rows ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}} = 1,508$ in `v0.3.0`).
  * Field Population: 0 null `protein_id` values and 0 null `uniprot_id` values observed ($100\%$ populated fields).
- **Status**: **VERIFIED / OK**.

### 2.4 Check 4: Triple Intersection 3-Tier Reconciliation
- **Method**: Direct verification of the four triple-intersection accessions (`Q42525`, `Q75NZ0`, `Q9ZVD5`, `Q9ZVR7`) across all candidate release source records.
- **Results**:
  * Tier 1 (Integrated Entities): Exactly $4$ unique protein entities (`MFP:U:8272bae0e8df8149`, `MFP:U:1b3a3b365f7440ca`, `MFP:U:72945c7a1c04dc9f`, `MFP:U:d0e5610e8f1019a2`).
  * Tier 2 (Source-Entity Pairs): Exactly $12$ pairs ($4 \times 3$ sources).
  * Tier 3 (Source Records in `v0.3.0`): Exactly $12$ records (`moonprot_359`, `moonprot_253`, `moonprot_249`, `moonprot_565`; `multitaskprotdb_ii_row_524`, `568`, `683`, `684`; `plantmp_order_25`, `60`, `51`, `44`). Zero internal multiplicity observed for these 4 accessions.
  * Loss Proportions if Restricted to Triple Intersection:
    - Entity loss: $(1,179 - 4) / 1,179 = 1,175 / 1,179 \approx 99.66\%$ of unique protein entities.
    - Record loss: $(1,508 - 12) / 1,508 = 1,496 / 1,508 \approx 99.20\%$ of source records.
    - Annotation loss: **Pending measurement** in Phase B.
- **Status**: **VERIFIED / OK**.

### 2.5 Check 5: Documentation Link Integrity Audit
- **Method**: Regex extraction of all relative markdown links in `spec.md`, `plan.md`, `tasks.md`, `verification.md`, and `docs/roadmap/pilot-to-three-source-validation-roadmap.md`.
- **Target Verification**: 100% of referenced files exist on disk. Zero broken relative links.
- **Status**: **VERIFIED / OK**.

---

## 3. Mandatory Integrity Invariants vs Indicative Scientific Thresholds

To maintain strict scientific governance, the audit contract distinguishes between non-negotiable data integrity invariants and unapproved policy proposals:

### 3.1 Operational Failures vs Evaluable Integrity Invariants
The audit contract strictly distinguishes operational execution halts from evaluable data integrity evaluations:

#### A. Operational Halt Conditions (`execution_failure`)
The audit runner halts execution immediately with a non-zero exit code on operational failures that prevent reading, parsing, or safely publishing outputs:
- Missing mandatory candidate release tables or reference ontology files.
- Unparseable CSV syntax or corrupted file formats.
- Target destination directory specified in `--output-dir` already exists (no overwrite option permitted).
- Generated output tables fail Draft 2020-12 JSON schema validation prior to publication.
- *Non-Conformance Invariant*: Any operational failure that prevents evaluating data integrity can **NEVER** produce a declaration of `integrity_conforming`.

#### B. Evaluable Data Integrity Invariants (`integrity_conforming` vs `non_conforming_integrity_violation`)
When inputs are readable and parseable, the runner completes execution, produces valid diagnostic tables and quarantine register (`execution_success`), and evaluates structural integrity invariants. The run is classified as `non_conforming_integrity_violation` if any invariant is violated:
1. **Total Row Conservation**: The principal accounting invariant mandates total row conservation: $N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}}$. Every physical row loaded within the 3-source perimeter must be accounted for and traceable in the output. Zero rows dropped. Evaluability is defined per check, not as a global mutually exclusive partition with quarantine. Quarantined entities are reported as affected source–record keys ($N_{\text{affected\_keys}} = |\{\text{distinct } (source\_name, source\_record\_id) \text{ with } \ge 1 \text{ incident}\}|$), strictly separated from physical rows and from total incident rows ($N_{\text{incidents}}$) in `three_source_quarantine_register.csv`. The values $1,508$, $1,452$, and $1,179$ are empirical properties of candidate release `v0.3.0`, not hardcoded universal invariants.
2. **Source-Record Key Uniqueness**: The compound key `(source_name, source_record_id)` must be unique across physical rows. If two physical rows share a key, both rows are preserved in accounting ($N_{\text{loaded\_rows}} = N_{\text{accounted\_rows}} = 2$), exactly one unique key is counted ($N_{\text{unique\_keys}} = 1$), each occurrence is traceable via a distinct, stable `row_locator` (`<artifact_relative_path>#record:<data_record_index>`, where index is 1-based parsed CSV data record excluding header), and collision incidents are logged under compound key `(source_name, source_record_id, row_locator, primary_reason_code)` without colliding with each other or losing any occurrence. This structural collision must not be confused with legitimate source–entity multiplicity (where distinct keys reference the same `protein_id`), which is valid domain curation.
3. **Deterministic Partition Sum**: The sum of the 7 disjoint Venn regions must equal the total number of unique protein entities in the union ($1,179$ in `v0.3.0`).
4. **Scoped Referential Integrity**: Every foreign key check within the 3-source perimeter (`SRC_MOONPROT`, `SRC_MULTITASKPROTDB_II`, `SRC_PLANTMP`) must resolve without orphan records.
5. **Offline Identity Decoupling**: Explicitly separates syntax regex, relational integrity, and biological identity. An accession must never be treated as a validated biological identity merely because its syntax is valid or its status is active; each conclusion is strictly limited to what the local versioned reference certifies. In the absence of an authoritative, versioned local reference certifying biological identity and taxon, biological identity must be recorded as `biological_identity_unassessed_in_inventory`, never passed or failed. Zero network queries.
6. **Typology of Missingness**: Non-evaluable fields are categorized into `field_empty`, `observed_absence`, `attribute_unrepresented_in_source`, `extraction_error`, and `check_impossible_missing_dependency`. The cause of missingness must never be deduced solely from an empty column.
7. **Independent Status Dimensions**: Execution status (`execution_success`/`failure`), verification coverage (`complete_verification`/`partial_verification_raw_missing`), and integrity conformance (`integrity_conforming`/`non_conforming_integrity_violation`) are strictly decoupled. Internal multiplicity, unclassified multiplicity, or absent optional raw dependencies do not imply non-conformance. Structural integrity violations (broken scoped foreign keys, dropped rows, key collisions) prevent declaring integrity conformance.
8. **Gate 3 Manifest Boundary & Reproducibility**: Gate 3 `manifest.json` records **ONLY** Gate 3 tabular outputs; narrative reports from Gate 4 are strictly excluded. Exact bitwise determinism applies to tabular datasets given identical inputs and CLI arguments.
9. **Input Immutability & Safe Staging**: All input files opened read-only. Target directory must not exist prior to run (no overwrite option; fresh destination required for every run); outputs staged in temporary directory and validated against schemas before atomic promotion.

### 3.2 Indicative Scientific Policy Proposals (Pending Human Decision)
The following criteria are **proposals for human consideration** and are **NOT** automatically activated or enforced as hardcoded pipeline rules:
1. **Quarantine Tolerance Threshold (Tentative $>5\%$)**:
   - The roadmap suggested that if $>5\%$ of records contain unresolvable identifiers, execution should pause for review.
   - *Status*: **Unapproved Proposal**. This threshold is an unactivated indicative proposal and does not block running a descriptive inventory audit. Prior to Gate 3, human review is strictly confined to verifying inputs, configuration, and execution authorization; audit findings and quarantine results are reviewed subsequently in Gate 4.
2. **Biological Identity Corrections (e.g. `P34788`)**:
   - *Status*: **Pending Curatorial Adjudication**. The audit records raw table evidence and historical query notes neutrally; no automated identity reassignments are permitted without a formal sign-off memo.

---

## 4. Pending Implementation & Execution Status

All downstream implementation tasks remain strictly deferred:

| Gate | Task ID | Description | Technical State | Authorization State |
|---|---|---|---|---|
| **Gate 1** | `TASK-AUD-01` | Author output schemas (`summary` and `quarantine`) | Not Started | **Deferred Pending Authorization** |
| **Gate 1** | `TASK-AUD-02` | Implement `three_source_auditor.py` | Not Started | **Deferred Pending Authorization** |
| **Gate 1** | `TASK-AUD-03` | Implement `audit_three_source_inventory.py` | Not Started | **Deferred Pending Authorization** |
| **Gate 1** | `TASK-AUD-04` | Author Tier A synthetic tests (mocks only; zero pipeline runs) | Not Started | **Deferred Pending Authorization** |
| **Gate 2** | `TASK-AUD-05` | Technical code review & Git commit (code, tests & schemas) | Not Started | **Deferred Pending Authorization** |
| **Gate 3** | `TASK-AUD-06` | Read-only audit execution on v0.3.0 (tables & manifest only) | Not Started | **Deferred Pending Authorization** |
| **Gate 4** | `TASK-AUD-07` | Narrative report & closeout review (`three-source-inventory-audit-report.md`) | Not Started | **Deferred Pending Authorization** |
