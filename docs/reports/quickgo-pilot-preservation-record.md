# Preservation Record: QuickGO Evidence Integration Pilot (Stages P1–P4)

- **Document ID**: `RECORD-QUICKGO-PILOT-PRESERVATION-001`
- **Target Repository**: `mfp-bibliography` (`feature/functional-normalization`)
- **Authority Level**: Level 6 Technical Completion Record (Data Preservation & Reproducibility)
- **Status**: Completed (2026-11-16; Clarification Revision 2026-11-16 distinguishing 5 operational preservation dimensions)
- **Baseline Git HEAD**: `21a3c8ef6bc42ae2f7f51ecc6f9ac6b9d9579b7e`
- **Package Identifier**: `pkg-quickgo-p1-p4-20261116-v1`
- **Governing Invariants**: [ADR-001](../../docs/decisions/ADR-001-repository-scope.md) through [ADR-007](../../docs/decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../../docs/decisions/ADR-008-functional-normalization-pilot-scope.md), [`AGENTS.md`](../../AGENTS.md)
- **Clarification Note**: This document is an evolving Level 6 report in the repository working tree. Clarifications made on 2026-11-16 (post-packaging) refine operational documentation without altering the sealed and immutable preservation package `pkg-quickgo-p1-p4-20261116-v1` created at 16:54:55 UTC.
- **Related Documents**:
  - Stage P3 Verification Record: [`specs/quickgo-pilot-p3/verification.md`](../../specs/quickgo-pilot-p3/verification.md)
  - Stage P4 Descriptive Analysis Report: [`docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md`](quickgo-pilot-p4-descriptive-analysis-report.md)
  - Stage P1–P2 Completion Report: [`docs/reports/quickgo-pilot-p1-p2-completion-report.md`](quickgo-pilot-p1-p2-completion-report.md)
  - Integration Pilot Proposal v1.5: [`docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md`](../roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md)

---

## Executive Summary & Preservation Status

This preservation record documents the assembly, integrity verification, and restoration testing of the bounded preservation package for the completed **QuickGO Evidence Integration Pilot (Stages P1–P4)**. 

To prevent conflating distinct operational dimensions, the preservation status is certified under five explicit criteria:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      PRESERVATION STATUS CERTIFICATION                 │
├────────────────────────────────────────────────────────────────────────┤
│ Criterion A: Local Package Created & Verified ───────> [VERIFIED / OK] │
│ Criterion B: Restoration Test Passed ────────────────> [PASSED / OK]   │
│ Criterion C: Independent Offsite Copy Verified ──────> [PENDING]       │
│ Criterion D: Computational Rerun Verified ───────────> [NOT PERFORMED] │
│ Criterion E: Historical Database Recapture ──────────> [NOT PERFORMED] │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Operational Preservation Declaration**:
> In accordance with scientific data curation standards, data preservation is **NOT operationally complete** while an independent offsite or secondary copy remains pending (Criterion C is Pending). 
> - **Criterion A [VERIFIED / OK]**: A complete, self-contained local package (`pkg-quickgo-p1-p4-20261116-v1`) was assembled with cryptographic sidecars and a structured 42-item inventory.
> - **Criterion B [PASSED / OK]**: An isolated extraction and verification test confirmed 100% bitwise identity across all 42 payload files.
> - **Criterion C [PENDING]**: Transfer to an independent secondary or cloud storage destination awaits human destination approval and transfer authorization.
> - **Criterion D [NOT PERFORMED]**: Full computational pipeline execution was not repeated; analytical outputs were validated against immutable manifests and schemas.
> - **Criterion E [NOT PERFORMED]**: Full database recapture from live upstream services or raw PostgreSQL dumps (`MFP_QuickV1`, 96,265 rows) was not performed and is not required, as the frozen input slices under `data/interim/` are self-contained and cryptographically preserved.

---

## 1. Inspected Repository Baseline & Metadata

- **Repository Root**: `/home/alexdoro/repositories/mfp-bibliography`
- **Active Branch**: `feature/functional-normalization`
- **Published Baseline HEAD**: `21a3c8ef6bc42ae2f7f51ecc6f9ac6b9d9579b7e`
- **Packaging Date**: `2026-11-16 16:54:55 UTC`
- **Package Directory**: `/home/alexdoro/mfp-preservation/quickgo-pilot/pkg-quickgo-p1-p4-20261116-v1`
- **Preservation Archive**: `quickgo-pilot-p1-p4-preservation-payload.tar.gz`
- **Archive Size**: `192,591 bytes` (compressed)
- **Archive SHA-256 Digest**: `f02c6f471bd195e2eb85a595a73352a073f4eb479091caba4e0454fcad97ab63`
- **Sidecar File**: `quickgo-pilot-p1-p4-preservation-payload.tar.gz.sha256`
- **Payload Inventory File**: `inventory.json`
- **Total Payload Files**: `42 files`
- **Total Uncompressed Size**: `753,074 bytes`

---

## 2. Payload Inventory & Scope Classification

The package contains exactly 42 payload files organized by repository-relative paths, classified across three distinct tracking states:
- **Committed Files (32)**: Tracked in Git history up to published HEAD `21a3c8e`.
- **Uncommitted Working-Tree Documents (1)**: The Stage P4 descriptive analysis report (`quickgo-pilot-p4-descriptive-analysis-report.md`).
- **Local Gitignored Artifacts (9)**: Interim pilot inputs and outputs under `data/interim/` (excluded from Git by `.gitignore`).

### 2.1 Complete Artifact Inventory Table

| # | Repository-Relative Path | Logical Role | Size (Bytes) | Full SHA-256 Digest | Status Category |
|---|---|---|:---:|---|:---:|
| 1 | `tests/fixtures/quickgo_pilot/raw_quickgo_annotations.csv` | P3 Input Fixture | 8,538 | `b8d508f6f980fb3aed676dae7c4d3275b188dcbe58438372280920e6cf704f6a` | committed |
| 2 | `tests/fixtures/quickgo_pilot/raw_quickgo_coverage.csv` | P3 Input Fixture | 1,033 | `249a4cd91117fec229cdaf9c579803dcb89d011e41ec2e5bf0eb0fb35eb8aef1` | committed |
| 3 | `tests/fixtures/quickgo_pilot/manifest.json` | P3 Input Manifest | 6,171 | `a6c08b0e4559f0557244e3adaf26d2911461952a8024451f4795044b9ef4c09c` | committed |
| 4 | `data/interim/pilot/functional_claims_pilot.csv` | Tier A Input Slice | 20,710 | `88a1f2521d5d69b70dbd3af11d2191589289bb22feb23a349611d1a563993348` | gitignored_local |
| 5 | `data/interim/pilot/source_go_annotations_pilot.csv` | Tier A Input Slice | 81,927 | `949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda` | gitignored_local |
| 6 | `data/interim/pilot/functional_coverage_pilot.csv` | Tier A Input Slice | 3,702 | `c29d28712c613211c6183f49ef304a63d94dd64a40de2ff682641037e2573e8d` | gitignored_local |
| 7 | `data/interim/pilot/manifest.json` | Tier A Input Manifest | 9,678 | `c6ecaed0306bfb2029427842e4b6b2e223a8b539f34990a05e87ac781a60bf5b` | gitignored_local |
| 8 | `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv` | Candidate Catalog Mapping | 202,213 | `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc` | committed |
| 9 | `releases/mfp-catalog-candidate-v0.3.0/MANIFEST.json` | Candidate Metadata | 3,796 | `3d4f128bc64a85fa6d6cb582ff935e40e34c9c28892697b0a88b560128d5d4fc` | committed |
| 10 | `releases/mfp-catalog-candidate-v0.3.0/DATA_DICTIONARY.md` | Candidate Metadata | 3,339 | `8448ebf532657e4e116e10787e74c8ca12882877a164fe5aa63c328dbf145417` | committed |
| 11 | `releases/mfp-catalog-candidate-v0.3.0/README.md` | Candidate Metadata | 3,161 | `eb7b370607a72d73ca0ec4b95d10a26e8557b6f6345d3ae7a18bb72352a92c3a` | committed |
| 12 | `releases/mfp-catalog-candidate-v0.3.0/checksums.sha256` | Candidate Checksums | 506 | `5a7469a531e03e7a0bf93c9e6ca3a48e7e178122d64bc8c96603513a89a0845a` | committed |
| 13 | `data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv` | P3 Output Annotations | 25,947 | `2a6255c5059545d8b1bab06a6d73872d2a064add1c0dd7b25097bd95e47012de` | gitignored_local |
| 14 | `data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv` | P3 Output Coverage | 1,237 | `981c592f12bceb02e2c7a6404126dc7ad55053b2bd6383919658a5423241b9be` | gitignored_local |
| 15 | `data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv` | P3 Output Concordance | 20,329 | `12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7` | gitignored_local |
| 16 | `data/interim/pilot/quickgo_slice/quickgo_reference_concordance_pilot.csv` | P3 Output Reference Overlap | 2,756 | `3c7236264424937c81a34fb2a5c64384e8154ef6f184c86f658ab583ba50281a` | gitignored_local |
| 17 | `data/interim/pilot/quickgo_slice/manifest.json` | P3 Execution Manifest v1.1 | 4,806 | `01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7` | gitignored_local |
| 18 | `docs/reports/quickgo-pilot-p4-descriptive-analysis-report.md` | P4 Descriptive Report | 42,076 | `66874ebf4ff5653db38a798c8cbe22f216da19c0f33d45ef889b7b998d89e5a1` | uncommitted_untracked |
| 19 | `specs/quickgo-pilot-p3/spec.md` | P3 Increment Specification | 7,645 | `271603511eb9aa80674f76239f150fc957088b8e05cb6211822c6e67cf759b0f` | committed |
| 20 | `specs/quickgo-pilot-p3/plan.md` | P3 Implementation Plan | 2,764 | `3c09bca3b28b2be4ca24ff8608f75f795d2c88f44ff53d4608c0ef0be194a9f3` | committed |
| 21 | `specs/quickgo-pilot-p3/tasks.md` | P3 Task Inventory | 1,852 | `ff9bdf52a0a86d888126786c2e71d3df8e76ae7c768997a3cf1e4a1691a3c754` | committed |
| 22 | `specs/quickgo-pilot-p3/verification.md` | P3 Verification Record | 6,155 | `0a80e1215b3c3c72cae6a4b11fdb1149e29a997d95d1ccf8ceb02d6b49e159aa` | committed |
| 23 | `docs/roadmap/draft-proposal-mfp-quickv1-evidence-integration-pilot.md` | Roadmap Proposal v1.5 | 86,066 | `fdb0cbf1737e19486c91a3299c85675571c6ae79d63c467a90ce36774cbfad1a` | committed |
| 24 | `docs/reports/quickgo-pilot-p1-p2-completion-report.md` | P1–P2 Completion Report | 25,703 | `0374e2d3e0988fb1c699926c9fa74bf561fa40ca7f03eebbc3a055cbdbb41b94` | committed |
| 25 | `data/curated/raw_quickgo_annotations.schema.json` | Schema Raw Annotations | 2,351 | `3fc5e8e8fb8a76e7368be3fc89f41b2c45199201f3db3e66487e41258d408eb6` | committed |
| 26 | `data/curated/raw_quickgo_coverage.schema.json` | Schema Raw Coverage | 3,664 | `cba945674c935ee5ea138e6cb0f455c1417ceef1eb52ae1046fe096184138e53` | committed |
| 27 | `data/curated/external_quickgo_annotations.schema.json` | Schema Normalized Annotations | 3,536 | `40f5f9b0b86ada5155d692dbfc2f506c4d688ef971395d654b9e0847a58fc1ed` | committed |
| 28 | `data/curated/quickgo_coverage.schema.json` | Schema Normalized Coverage | 2,367 | `458cad79a9a225190f5bee65f70d01d5cb17cd841b80ed03066a71276fb07f9f` | committed |
| 29 | `data/curated/quickgo_concordance.schema.json` | Schema Term Concordance | 8,186 | `c1181b192fdb09b415b14c404004111ffa66c32e2bcffe6a526cad18dbfc2dea` | committed |
| 30 | `data/curated/quickgo_reference_concordance.schema.json` | Schema Reference Overlap | 6,222 | `66f33b6d4df8541f13585464992b638cc185becd22853af76e81039a3269458f` | committed |
| 31 | `data/curated/functional_claims.schema.json` | Schema Tier A Claims | 4,704 | `797c2777ae030d939634d989f66085a6cfc62ddb03e0586e24db4fe2fa8bf722` | committed |
| 32 | `data/curated/source_go_annotations.schema.json` | Schema Tier A Annotations | 3,733 | `99e843c0d832ea51d9571ff5d41f3d81944810817dd641775db5ccdc040228bb` | committed |
| 33 | `data/curated/functional_coverage.schema.json` | Schema Tier A Coverage | 2,492 | `80bf73bc24e8e815668e169d2aa62f741c9f4d1565a4487771ea04aeaf22839b` | committed |
| 34 | `src/mfp_bibliography/__init__.py` | Python Package Root | 119 | `471a257521a074094a97495015e165f973792c3066ea3746a5b6cb24bc688005` | committed |
| 35 | `src/mfp_bibliography/quickgo_concordance.py` | Concordance Engine Module | 31,660 | `e7b22c99cfa06376f2445c855184814d6c51a363a0c74f705fb4dd0a68c6cf71` | committed |
| 36 | `src/mfp_bibliography/quickgo_raw_validator.py` | Raw Fixtures Validator | 13,881 | `0014bdf8bb1a4a1599388ffc0b3684a0d8eefc1dd43c7b8db04550875e6e3dfd` | committed |
| 37 | `scripts/build_quickgo_concordance_pilot.py` | Concordance Pipeline CLI | 12,589 | `332a5f757d5da5de7e726a95649a378e81a426b17b249dab696b19ecc22d4c73` | committed |
| 38 | `scripts/export_quickgo_pilot_fixtures.py` | Raw Exporter CLI | 11,481 | `7393d25ffb65ba596da99b9cf959b3aa5cae60eb118c7e00854228965f7cba68` | committed |
| 39 | `scripts/package_catalog_candidate.py` | Catalog Candidate Packager | 31,605 | `602888c3c13ff03c39aa92c556f8f17a94d8cb9a7cc00344d9f67a2168903c72` | committed |
| 40 | `tests/test_quickgo_raw_contracts.py` | Raw Contracts Test Suite | 21,316 | `141b212dbd1b54ecf0bc59ccf919198751db2be7839352e42bc2245b780362f7` | committed |
| 41 | `tests/test_quickgo_concordance.py` | Concordance Test Suite | 20,418 | `72b1d3d6b994f2dd71b05a6ef6cb31f0f0322ba48555e7fc1f2c25608bfa03d6` | committed |
| 42 | `pyproject.toml` | Environment Declarations | 640 | `1734f2a9693eb14d6ae795a9757fc256a943719488a0e0586e926219ee54559b` | committed |

---

## 3. Restoration Verification Test Results

Restoration was tested by extracting the archive into an isolated, temporary restoration sandbox outside the repository (`/home/alexdoro/mfp-preservation/quickgo-pilot/tmp-restoration-test`):

1. **Archive Checksum Verification**:
   - Sidecar checksum: `f02c6f471bd195e2eb85a595a73352a073f4eb479091caba4e0454fcad97ab63`
   - Computed archive digest: `f02c6f471bd195e2eb85a595a73352a073f4eb479091caba4e0454fcad97ab63`
   - *Status*: **PASSED** (Sidecar matches archive byte-for-byte).
2. **Member Path Safety & Traversal Inspection**:
   - Total archive members: **42**.
   - Path checks: 0 absolute paths (`/`), 0 path traversal sequences (`..`), 0 symbolic links, 0 hard links.
   - *Status*: **PASSED** (Archive is strictly relative and safe).
3. **Extraction & Byte-Level Content Verification**:
   - Archive extracted into empty temporary sandbox.
   - All 42 extracted files verified individually against the declared SHA-256 digests in `inventory.json`.
   - Mismatches: **0**.
   - *Status*: **PASSED** (100% bitwise identity verified).
4. **Working Tree and Original Artifact Protection**:
   - The temporary restoration sandbox was completely removed after verification.
   - The original repository working tree and local artifacts remained unmodified.
   - *Status*: **PASSED**.

---

## 4. Provisioning Instructions for Fresh Clones

Because `data/interim/` is excluded from Git by `.gitignore`, a user cloning `mfp-bibliography` freshly from remote cannot execute offline concordance checks without provisioning these interim slices.

### Provisioning Steps
```bash
# 1. Clone repository and checkout pilot branch
git clone https://github.com/alexdorocode/mfp-bibliography.git
cd mfp-bibliography
git checkout feature/functional-normalization

# 2. Extract only the missing interim pilot files from the preservation package
tar -xzf /path/to/quickgo-pilot-p1-p4-preservation-payload.tar.gz data/interim/

# 3. Verify restored interim files against Manifest v1.1
python3 -c "
import json, hashlib
from pathlib import Path
with open('data/interim/pilot/quickgo_slice/manifest.json') as f:
    m = json.load(f)
for p, info in m['input_inventory'].items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == info['sha256']
print('Provisioning verified successfully!')
"
```

---

## 5. Storage Restrictions & Pending Independent Preservation

### 5.1 Access Restrictions
- **Classification**: **RESTRICTED RESEARCH DATA**.
- **Reasoning**: The payload contains third-party biological assertions extracted from MultitaskProtDB-II, MoonProt, and PlantMP, alongside proteomic captures from UniProtKB/QuickGO. While repository code and original documentation are licensed under AGPL-3.0, third-party data artifacts have not been cleared for unrestricted public redistribution.

### 5.2 Independent Storage Status (Criterion C: PENDING)
- **Current State**: The preservation package resides exclusively on local developer storage (`$HOME/mfp-preservation/quickgo-pilot/pkg-quickgo-p1-p4-20261116-v1/`).
- **Limitation**: A local copy on the primary workstation drive does not constitute an independent, offsite disaster recovery backup. Preservation cannot be certified as fully complete while Criterion C remains pending.
- **Exact Remaining Human Action**: Maintainers must approve an authorized secondary preservation destination (such as a restricted institutional S3 bucket, a private/restricted Zenodo repository community, or an encrypted offline cold-storage volume) and grant transfer approval. No upload or network transfer will occur autonomously.
- **Decoupled Continuity**: Preparation of downstream enrichment specifications (such as `specs/quickgo-pilot-go-aspect-enrichment/spec.md`) can proceed immediately. It does not depend on completing Criterion C, as the verified local frozen inputs are fully sufficient for offline specification and derivation.

### 5.3 Upstream Database Recapture Status (Criterion E: NOT PERFORMED)
- **Recapture Boundary**: Complete upstream recapture from live external APIs or raw PostgreSQL instances (`MFP_QuickV1`, 96,265 rows captured on 2026-11-12) was **NOT PERFORMED** and is not required for pilot reuse.
- **Sufficiency of Frozen Inputs**: The historical pilot inputs (`functional_claims_pilot.csv`, `source_go_annotations_pilot.csv`, `functional_coverage_pilot.csv`, `raw_quickgo_annotations.csv`, `raw_quickgo_coverage.csv`) are frozen, cryptographically hashed, and verified. They fully retain and isolate the exact experimental inputs required for offline evaluation and downstream derived increments without requiring a 500 MB database dump.
- **Recapture Limitation Note**: True upstream recapture from scratch would require running `protein-information-system` (commit `f54bc4f`) against the specific PostgreSQL snapshot. Querying an evolving, live QuickGO database will not reproduce identical hashes.

---

## 6. Readiness for Derived Increments: GO-Aspect Enrichment (Task PIL-04.1)

With the completion and preservation of the Stage P1–P4 baseline, the project is positioned to evaluate **GO-Aspect Enrichment (Task PIL-04.1)** as a controlled, derived increment.

> [!NOTE]
> **Nomenclature and Authority Alignment**:
> The informal draft label "Stage P5" appeared in preliminary roadmap proposals (`draft-proposal-mfp-quickv1-evidence-integration-pilot.md`). To avoid conflation with authorized work and maintain alignment with the repository master work breakdown structure, this derived increment is formally specified under stable identifier **`PIL-04.1`** in [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md).

### 6.1 Readiness Assessment Matrix

| Dimension | Status | Operational Reality |
|---|:---:|---|
| **P1–P4 Historical Baseline Preservation** | **READY** | All frozen inputs, outputs, schemas, code, and reports are cryptographically anchored and restorable. |
| **Enrichment Specification Package** | **READY** | Minimum specification prepared at [`specs/quickgo-pilot-go-aspect-enrichment/spec.md`](../../specs/quickgo-pilot-go-aspect-enrichment/spec.md). |
| **Ontology Snapshot Selection** | **PENDING** | A fixed, versioned Gene Ontology release (e.g. `go-basic.obo` releases/2026-01-23) must be formally approved and pinned by SHA-256 before execution. |
| **Aspect Assignment Policy Ratification** | **PENDING** | Maintainers must formally approve the mapping protocol (e.g. mapping MoonProt's explicit `GO:[0-9]{7}` terms to `BP`, `CC`, or `MF` namespaces). |
| **Enrichment Implementation Authorization** | **UNAUTHORIZED** *(Historical snapshot; see 2026-11-18 status note)* | No code, schema edits, pipeline runs, or data mutations for enrichment are authorized at this time. |

> [!NOTE]
> **Reconciliation Status Note (2026-11-18 / 2026-11-19)**:
> This preservation record preserves the operational status snapshot as drafted on 2026-11-16. Subsequently on 2026-11-16, human sign-off was recorded authorizing the implementation of Task `PIL-04.1A` (minimum GO-aspect metadata mapping). The task was implemented locally (commit `98530b32cd13d0b8ff5b4ea7a626e691d9426d25`) and verified offline (`specs/quickgo-pilot-go-aspect-enrichment/verification.md`, commit `421da7e81c450b4bbeca2c637bbbfe0c8db002b4`). Recorded human sign-off is preserved in the specification and verification metadata; the local commit demonstrates local tree modification but not remote publication (the commits remain unpushed on local branch `feature/functional-normalization`).
> For `PIL-04.1B` (concordance recomparison), implementation code and synthetic unit tests have been prepared and reported in the working tree, with technical code review and formal Gate 1 closure pending; Gate 2 technical commit and Gate 3 pilot execution remain unauthorized; consult `specs/quickgo-pilot-concordance-recomparison/verification.md` for current status.

### 6.2 Key Constraints for Future Enrichment
1. **No Inferred Biological Functions**: Aspect disambiguation must strictly map existing, explicitly cited GO identifiers to standard ontology namespaces. It must **NEVER** infer new biological functions or synthesize novel functional triplets.
2. **Realistic Evaluability Expectations**: Aspect disambiguation will resolve the 30 `source_aspect_indeterminate` rows in MoonProt, but will **NOT** make all 52 non-evaluable rows evaluable. The 12 rows gated by taxonomic discrepancy (`P34788`), the 6 rows outside the slice (`A0A0H3CDS3`), and the 4 aspect-empty rows will remain non-evaluable unless separately addressed.

> [!NOTE]
> **Reconciliation Note on Evaluability Scope (2026-11-18 / 2026-11-19)**:
> The historical statement above that aspect disambiguation "will resolve the 30 `source_aspect_indeterminate` rows in MoonProt" requires precision. While Task PIL-04.1A successfully assigned ontology namespaces to all 353 annotation rows, PIL-04.1A did NOT recalculate concordance or demonstrate any evaluability transition. Resolving aspect indeterminacy removes an ontology-tagging blocker; it does not eliminate orthogonal database linkage or biological identity gates, nor does it guarantee that both source and QuickGO have non-empty term sets for a given aspect and policy.
> Crucially, evaluability requires that the source and QuickGO term sets must each be non-empty for the relevant aspect and policy ($|S| > 0$ and $|Q| > 0$), and all other applicable gates must pass. They need not overlap: two non-empty disjoint sets yield Jaccard = 0.0000, which is an evaluable outcome, distinct from a non-evaluable row with null Jaccard.
> Specifically, under the frozen pilot capture, `E6KMA1` (MoonProt) carries an independent, co-occurring blocker (`accession_unlinked_in_capture`, where `protein_id IS NULL` in the capture database). Consequently, `E6KMA1`'s 6 rows (3 comparison units $\times$ 2 policies) remain strictly non-evaluable even after aspect disambiguation. Therefore, the figure 30 represents the historical count of rows where aspect missingness was the primary reason; the figure 24 ($30 - 6$) represents only a theoretical upper bound of MoonProt rows eligible to transition if both source and QuickGO inventories are non-empty, NOT an empirical forecast, observed result, or acceptance threshold. Projections such as +22 or 42 totals are pre-execution hypotheses, not results. Actual transitions must be measured and reported empirically by Task PIL-04.1B.
3. **Decoupled Execution Prerequisites**: Execution requires only human approval of the specification, the pinned ontology snapshot, and an isolated output directory (`data/interim/pilot/quickgo_slice_enriched/`). It does not require offsite backup completion (Criterion C) or a full database dump (Criterion E).
4. **Immutability of Preserved Baseline**: Enrichment must generate separate, derived, versioned output artifacts and a derived manifest, leaving the preserved Stage P3/P4 baseline untouched.
