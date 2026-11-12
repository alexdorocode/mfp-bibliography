# Literature Curation Manual: Protocols for Bibliographic Verification, Evidence Localization, and Contextual Adjudication of Multifunctional Claims

## Document Control & Epistemic Status

| Attribute | Specification Record |
|---|---|
| **Document Title** | Literature Curation Manual: Protocols for Bibliographic Verification, Evidence Localization, and Contextual Adjudication of Multifunctional Claims |
| **Document ID** | `DOC-MAN-LITERATURE-CURATION-V1` |
| **Document Path** | [`docs/curation/literature-curation-manual.md`](literature-curation-manual.md) |
| **Document Status** | **Proposed procedure — pending scientific and maintainer approval.**<br>*Not yet a governing policy; no code implementation implied.* |
| **Document Role** | Reference Curation Manual and Operational Protocol Proposal |
| **Source Material** | Recovered from historical dossier [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) (§§1–18), recovery-map items (`MAP-06-01`, `MAP-06-02`, `MAP-06-03` in [`docs/reports/documentation-recovery-map.md`](../reports/documentation-recovery-map.md)), contextual adjudication dossier [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md), amended evolution proposal [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md), and scientific background [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md). |
| **Target Increment** | `REC-INC-002-LITERATURE-CURATION-MANUAL` (Revision: `REC-INC-002-COHERENCE`) |
| **Governing Authority** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Date** | 2026-11-10 |

> [!IMPORTANT]
> **Adjudication Scope and Non-Implementation Warning**:
> 1. **Proposed Status**: This manual documents proposed operational protocols for bibliographic evidence curation, text localization, and contextual adjudication in `mfp-bibliography`. It is **NOT** currently an approved governing policy, binding data contract, or operational release standard.
> 2. **No Code Implementation Implied**: Nothing in this manual authorizes writing automated curation pipelines, modifying production database schemas, creating new release artifacts, or scraping external literature databases without explicit maintainer approval and formal Specification-Driven Development (SDD) increment packages under [`specs/`](../../specs/).
> 3. **Authority Hierarchy**: In any conflict between documents, repository authority strictly follows [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) (Level 1), Governance Contracts (Level 2), and Architecture (Level 3) over this proposed manual (Level 6), as established in [`AGENTS.md`](../../AGENTS.md).

---

## 1. Purpose, Scope, and the Non-Blocking Preservation Principle

### 1.1 Purpose of Literature Curation in `mfp-bibliography`
The core mission of `mfp-bibliography` is cataloging, identity resolution, source provenance tracking, and bibliographic evidence curation for multifunctional and moonlighting protein research ([ADR-001](../decisions/ADR-001-repository-scope.md)). Within this framework, manual literature curation serves a specific epistemic role:
- **Quality Enhancement and Contextual Adjudication**: Literature curation enables researchers to evaluate whether external claims and Gene Ontology annotations are directly supported by primary experimental findings, assess the molecular construct tested, and evaluate physiological relevance.
- **Support for Proposed Curated Subsets (Product C)**: Curated evidence dossiers are designed to support proposed downstream benchmark datasets, gold-standard evaluation sets, and contextual adjudication profiles, as outlined in the repository product architecture ([`docs/architecture/scientific-background.md` (§2.2)](../architecture/scientific-background.md)).
- **Decoupled Evaluation**: Literature curation evaluates evidence independently of computational semantic metrics, structural dissimilarity scores, or machine learning models.

### 1.2 The Non-Blocking Preservation Principle
A central architectural principle formulated for `mfp-bibliography` is the **Non-Blocking Preservation Principle**:

> [!NOTE]
> **Core Architectural Principle**: Literature curation is an evaluative and quality-enhancement activity designed for downstream curated subsets (Product C). It is **not an ingestion gate** for the source catalog (Product A) or exploratory analytical views (Product B). Non-blocking preservation is an architectural guideline and does not independently authorize new pipeline execution or repository writes.

The absence of local literature review or inability to access primary full text does **NOT** prevent:
1. **Preserving an External Source Claim**: Claims asserted by upstream databases (MoonProt, MoonDB, MultitaskProtDB-II, PlantMP) are recorded in accordance with repository source contracts and immutable raw artifact preservation ([ADR-002](../decisions/ADR-002-raw-data-immutability.md), [ADR-003](../decisions/ADR-003-provenance-and-transformations.md)).
2. **Retaining an External GO Annotation**: Gene Ontology annotations imported from authoritative resources are preserved with their original evidence codes (e.g. `IDA`, `IMP`, `IPI`, `ISS`, `IEA`) and source references without requiring prior local paper inspection.
3. **Querying Unreviewed Sources or Annotations**: Researchers may query, filter, and inspect unreviewed candidate records in the catalog.
4. **Using Unreviewed Data in Exploratory Analyses**: Cross-source overlap studies, descriptive distributions, and semantic distance calculations may proceed on unreviewed catalog data, provided epistemic caveats are explicitly stated.

#### Explicit Negative Guardrails (What Must NOT Be Required)
Curators, contributors, and automated tooling must strictly uphold these negative guardrails:
- **Do NOT require full text** before an external claim or GO annotation can be preserved in the catalog.
- **Do NOT require a PubMed ID** for non-literature evidence types (e.g. computational predictions, sequence models, structural homology, or internal database curator assertions).
- **Do NOT require local literature review** before external GO annotations are retained.
- **Do NOT require complete Molecular Function, Biological Process, and Cellular Component $(m, b, c)$ functional triplets** before recording an observation. Partial, standalone, or single-aspect claims must be preserved without forced artificial contextualization.

### 1.3 Operating Modes: Targeted Statements vs Entity-Level Syntheses
To accommodate distinct scientific needs, this manual defines two operating modes:
1. **Targeted Statement Review**: Focuses on a single biological statement, working claim, GO annotation, or bibliographic reference. The curator evaluates whether the specific cited experiment directly demonstrates that property for the specified entity.
2. **Entity-Level Synthesis Review**: Evaluates the collective body of evidence for a protein entity across all its asserted functions, determining whether functional multiplicity is supported, whether separate physiological contexts are demonstrated, and whether the observed multiplicity is compatible with operational criteria for protein moonlighting.

---

## 2. Evidentiary Units and Decoupled Architecture

### 2.1 The Seven Linked Evidentiary Units
To prevent conflating distinct types of scientific evidence, this manual adopts the decoupled relational architecture formulated in historical dossier [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md` (§2)](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) and mapped in `MAP-06-01`. 

Curation links seven distinct evidentiary units without collapsing them:

```
[1. Protein Entity: entity_id (MFP:U:... or source ID)]
        │
        ├───► [4. Original Source Attribution: source_claim_id]
        │            │
        │            ▼
        ├───► [2. Working Functional Claim: working_claim_id] ◄───┐
        │            ▲                                            │
        │            │                                            │
        ├───► [3. Structured GO Annotation: annotation_row_id]    │
        │                                                         │
        ├───► [5. Publication / Reference: reference_id]          │
        │            │                                            │
        │            ▼                                            │
        └───► [6. Evidence Unit: experiment_locator]              │
                     │                                            │
                     ▼                                            │
              [7. Review Decision: review_record_id] ─────────────┘
```

| Curation Unit | Definition & Scope | Key Identifier | Permitted Operations | Prohibited Inferences |
|---|---|---|---|---|
| **1. Protein Entity** | Normalized molecular entity or unresolved source candidate. | `entity_id` (deterministic digest `MFP:U:...` per [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) where resolved; source ID where unresolved) | Cross-referencing to UniProtKB canonical accessions or tracking source-native IDs. | Transferring evidence across family members or paralogs without explicit notation. |
| **2. Working Functional Claim** | An atomic, verifiable assertion describing a discrete molecular activity, process contribution, or localization. | `working_claim_id` | Decomposing composite source statements into testable atomic claims. | Forcing distinct GO synonyms or aspects into artificial binary slots ("Facet 1 vs 2"). |
| **3. Structured GO Annotation** | Association between a gene product and a GO term, with relation, evidence code, and cited reference. | `annotation_row_id` | Tracking ontology releases and evidence codes (`IDA`, `IMP`, etc.). | Converting co-annotated MF and CC terms into an inferred spatial-activity triplet. |
| **4. Original Source Attribution** | Verbatim assertion made by an external source catalog (MoonProt, MoonDB, etc.). | `source_claim_id` | Verbatim preservation with source provenance. | Modifying or deleting raw source text to match downstream curation conclusions. |
| **5. Publication / Reference** | Bibliographic reference anchor cited by a source or GO annotation. | `reference_id` (PMID, DOI, `GO_REF`, etc.) | Cross-referencing and metadata resolution. | Presuming full-text reading or experimental support based solely on citation presence. |
| **6. Evidence Unit** | A discrete experimental result, assay read-out, figure panel, or table in a document. | `experiment_locator` (Figure, Table, Page, Passage) | Precise localization of supporting or opposing observations. | Citing an entire paper's title or abstract as direct evidence for a detailed mechanism. |
| **7. Review Decision** | A dated, attributable curatorial judgment evaluating a specific claim against inspected evidence. | `review_record_id` | Adjudicating support, recording limitations, noting dissent. | Silently overwriting prior reviews or asserting biological certainty from a metric score. |

### 2.2 Relational Non-Destructive Principles
1. **Source Claims Are Immutable**: Curatorial evaluations never alter or replace raw source assertions. The source attribution remains frozen; curatorial assessments are recorded in separate, versioned review records.
2. **Reference Specificity**: A publication may provide direct evidence for one function while completely failing to address a second asserted function. Support must be evaluated per claim, not globally per publication.
3. **Data Reuse Recognition**: Multiple publications may report or re-analyze the same underlying dataset. Multiple citations do not guarantee independent experimental replications.
4. **Primary Literature vs Narrative Reviews**: Review articles and database cross-references may point to primary literature, but curators must evaluate and cite the primary experimental report rather than counting review commentary as independent evidence.

---

## 3. Reference Identification and Ingestion Gating

### 3.1 Diversity of Reference Anchors
In biological curation, claims and annotations are supported by diverse reference types:
- **PubMed Identifiers (PMID)**: Standard numeric identifiers for biomedical literature indexed in MEDLINE/PubMed (e.g. `14660562`, `15006356`).
- **Digital Object Identifiers (DOI)**: Persistent digital identifiers for journal articles, book chapters, datasets, or preprints (e.g. `10.1074/jbc.M311449200`).
- **Gene Ontology Reference Identifiers (`GO_REF`)**: Curated reference descriptions documenting standard GO curation methods, electronic projection pipelines, or cross-database mappings (e.g. `GO_REF:0000033` for UniProtKB-KW mappings, `GO_REF:0000002` for electronic projection).
- **Source-Native Database Accessions**: Internal database record citations, curator notes, or web references from source catalogs lacking a formal PMID.

### 3.2 Handling Unresolved, Ambiguous, or Missing References
A robust curation procedure must accommodate bibliographic anomalies without halting execution across unrelated claims:
- **`reference_unresolved`**: Recorded when a cited reference string cannot be mapped to a valid PMID, DOI, or repository identifier. The claim is retained in the catalog; its review status on this reference branch is marked `reference_unresolved`.
- **`reference_mismatch`**: Recorded when a cited identifier resolves to a document whose title, authors, or subject matter do not match the entity or claim (e.g. a typographical error in an upstream database). Curators document the discrepancy as an issue code and request crosswalk verification. **Curators must NEVER silently substitute a plausible-looking paper without an auditable crosswalk update.**
- **Multiple References in GAF 2.2**: In Gene Association Files, the `DB:Reference` field may contain multiple piped identifiers (e.g. `PMID:15006356|DOI:10.1016/S0092-8674(04)00204-1`). Curation tools must recognize these as alternative identifiers for a single bibliographic work, avoiding artificial inflation of citation counts.

---

## 4. Documentary Availability, Material Inspected, Legal Boundaries, and Permitted Processing

### 4.1 Separating Availability, Inspection, and Assessment Scope
To prevent ambiguity, curation must distinguish three orthogonal dimensions:
1. **Documentary Availability**: What documentary material is accessible through authorized channels (e.g. `metadata_only`, `abstract_only`, `full_text`, `full_text_plus_supplement`, `inaccessible`).
2. **Material Actually Inspected**: What sections the curator actually examined (e.g. title/abstract, specific results section, experimental methods, supplementary tables, crystallography coordinates). Access to a document does not prove that all sections were read.
3. **Assessment Scope**: What specific biological property, molecular construct, or context is under evaluation (e.g. enzymatic turnover, binding partner, subcellular compartment).

```
[Documentary Availability] ──► [Material Actually Inspected] ──► [Assessment Scope]
  (What files are accessible)    (What portions were examined)    (What property is evaluated)
```

| Dimension | Permitted Values / States | Critical Distinctions & Negative Invariants |
|---|---|---|
| **Documentary Availability** | `metadata_only`<br>`abstract_only`<br>`full_text`<br>`full_text_plus_supplement`<br>`inaccessible` | Access to full text does **NOT** guarantee complete or reproducible methods.<br>Access to supplements does **NOT** establish that raw data were inspected. |
| **Material Actually Inspected** | Textual description of sections examined (e.g. "Abstract and Figure 2B"; "Results Section 3"; "PDB header only") | Curators must explicitly state which sections were read. An uninspected section must not be cited as evidence. |
| **Assessment Scope** | Property evaluated (e.g. `catalytic_activity`, `complex_formation`, `subcellular_localization`) | Evaluating one property does not imply evaluation of all functions of an entity. |

### 4.2 Legal Boundaries and Compliance with AGENTS.md
Curators and automated assistants must adhere strictly to repository governance and lawful access rules ([`AGENTS.md`](../../AGENTS.md) Section 6):
- **Lawful Channels Only**: Material must be accessed solely through open-access repositories (PMC, Europe PMC, publisher open-access pages), institutional subscriptions, or authorized local archives.
- **Strict Prohibition on Paywall Bypass**: Curators and agents must **NEVER** bypass or attempt to defeat paywalls, login gates, subscription barriers, IP/proxy restrictions, CAPTCHAs, or anti-bot challenge systems (e.g. Cloudflare Turnstile, Altcha, HTTP 403 blocks).
- **Documentary Access vs Licensing Rights**: Viewing an article under personal or institutional subscription does not grant redistribution rights. Curators must respect applicable copyright terms, open-access licenses (e.g. Creative Commons), and verified repository restrictions. Extensive article bodies, full-text dumps, or copyright-protected figures must **NEVER** be committed into public repository git history. Brief excerpts or marked paraphrases with precise locators should be used to anchor curatorial judgments.

### 4.3 Practical Bounds on Partial and Abstract Inspection
The extent to which an abstract or partial text can support a claim depends on what is explicitly reported and what property is being evaluated:
- **Case-Specific Illustration ([`DOSSIER-Q9Y3E5-001`](Q9Y3E5_contextual_adjudication_dossier.md))**: In the review of human PTRH2/Bit1, inspected abstracts directly stated peptidyl-tRNA hydrolase catalytic efficiency and anoikis phenotypes, but omitted assay controls, submitochondrial resolution, and nuclear corepressor assays. Those specific uninspected properties were classified as `not_established_by_inspected_material`.
- **Non-Generalization Rule**: Abstract limitations observed in one study must **NOT** be generalized into universal rules for all scientific literature. An abstract in one journal may report quantitative affinity constants, specific point mutations, or direct binding partners, while another may report only high-level phenotypes.
- **Operational Boundary**: If an essential property requires inspecting assay methods, controls, or data figures that were not inspected, the curator must classify that specific property as `not_established_by_inspected_material` or `insufficient_evidence`, keeping the decision strictly pending rather than guessing.

---

## 5. Evidence Localization and Assisted Extraction

### 5.1 Locator Granularity Requirements
To ensure reproducibility and auditability, every positive or negative curatorial finding must record an exact locator. Another independent curator must be able to navigate directly to the evidence:
- **Figure / Panel Locators**: e.g. `Figure 2B`, `Figure 4 (panels C and D)`.
- **Table Locators**: e.g. `Table 1`, `Supplementary Table S3`.
- **Textual Locators**: e.g. `Results, section "Bit1 releases into cytosol", paragraph 3, lines 12–15`; `Page 8113, right column, paragraph 2`.
- **Supporting Excerpts & Paraphrases**: A brief excerpt or marked paraphrase sufficient to anchor the evidence under applicable terms and licenses, accompanying the locator to verify exact phrasing without reproducing substantial portions of copyrighted text.

### 5.2 Assisted Extraction and AI Tool Boundaries
Natural language processing, search utilities, and machine learning tools may be employed to assist curators in scanning literature, highlighting keywords, or proposing candidate passages:
- **Assisted Extraction vs Human Adjudication**: Computational tools produce *candidate extractions*; they do **NOT** produce validated evidence. Candidate text generated by tools must be clearly tagged (`claim_origin = "literature_extracted"` or `reviewer_proposed_for_review`).
- **Human Curation Gate**: No machine-extracted passage may be promoted to a verified evidence unit or entered into a downstream curated benchmark without explicit human inspection and sign-off.
- **Audit Trail**: When an assisted extraction tool is utilized, the curation record must document the tool name, model version, search prompt/query, and timestamp.

---

## 6. Scientific Assessment Protocol

### 6.1 Molecular Correspondence and Construct Identity
Curators must verify that the physical biological entity tested in the paper corresponds to the target protein in the catalog:
- **`matched`**: The tested entity, species/strain, isoform, and sequence correspond directly to the catalog entity.
- **`partial_match`**: Probable match, but minor discrepancies exist (e.g. truncated construct, synthetic epitope tag, uncharacterized splice variant). The discrepancy must be documented.
- **`different_entity`**: The assay was performed on a homolog, paralog, ortholog, or different organism. Direct support cannot be claimed for the target entity (must be classified as `transferred` evidence; see Section 6.5).
- **`unresolved`**: The published report lacks sufficient sequence, accession, or strain information to verify molecular identity.

### 6.2 Experimental Findings versus Author Interpretations
Curators must enforce a strict distinction between empirical observations and author commentary:
1. **Direct Assay Readouts**: What was physically measured (e.g. spectrophotometric absorbance indicating tRNA ester cleavage; band intensity in co-immunoprecipitation; cell death percentage after anoikis induction).
2. **Author Hypotheses and Discussions**: Interpretations or proposed models offered in the Discussion section (e.g. suggesting that a crystallographic crystal packing contact represents a physiological protein-protein interaction site).
3. **Citations of Prior Literature**: Statements in the Introduction or Discussion asserting a function by referencing earlier papers. Curators must trace and inspect the original primary citation.
4. **Crystallographic Contacts**: As observed in PDB entry `1Q7S` ([`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md` (§3)](Q9Y3E5_contextual_adjudication_dossier.md)), intermolecular contacts in an asymmetric crystal lattice represent a structural hypothesis for a putative interaction surface, **not** direct proof of a physiological complex in living cells.

### 6.3 Explicit Support Outcome Categories
Support is evaluated per claim and per evidence unit using explicit nominal categories:

| Support Category | Operational Definition | Example Application |
|---|---|---|
| `supports` | The inspected experimental evidence directly demonstrates the asserted property for the specified entity under the defined conditions. | Recombinant PTRH2 releases tRNA from peptidyl-tRNA with measured catalytic efficiency in vitro ([`STMT-01`](Q9Y3E5_contextual_adjudication_dossier.md)). |
| `partially_supports` | The evidence supports a narrower, related, or incomplete aspect of the claim, leaving key elements unestablished. | AES binding is demonstrated in cytoplasm, but full-length TLE1 corepressor binding is not shown ([`STMT-07`](Q9Y3E5_contextual_adjudication_dossier.md)). |
| `opposes` / `contradiction` | An interpretable, well-controlled experiment yields results incompatible with the claim under equivalent conditions. | An assay demonstrates that a proposed catalytic active-site mutation has no effect on turnover in a well-controlled system, contradicting the claim that this specific residue is essential for catalysis (without refuting the wild-type protein's broader activity). |
| `insufficient_evidence` | The tested assay, controls, or data quality are inadequate to support the inference, though the claim is addressed. | A single uncalibrated Western blot with no loading control or molecular weight markers. |
| `not_addressed` | The cited document does not report, test, or discuss the target property for the entity. | A paper cited by an upstream source for apoptosis that only reports crystallographic coordinates and hydrolase activity. |
| `not_assessable` | Documentary inaccessibility, illegibility, or lack of molecular identity prevents evaluation. | Full article behind an impassable paywall; abstract provides no experimental data. |

### 6.4 Handling Negative, Null, and Inconclusive Findings
In alignment with [`docs/architecture/scientific-background.md` (§1.2)](../architecture/scientific-background.md):
- **Null and Negative Findings**: When a primary study tests a function and finds no detectable activity or interaction under specific assay conditions, the curator records this as an empirical negative finding with full experimental context (assay detection limit, concentration range, controls).
- **Separation from Gene Ontology `NOT`**: Curators must **NEVER force experimental null or negative findings into imported GO `NOT` annotations**. In Gene Ontology, `NOT` is a formalized ontology qualifier assigned by dedicated consortia curators. Local experimental observations must remain recorded in curation dossiers without corrupting imported ontology callsets.

### 6.5 Modern Moonlighting Mechanisms (Alignment with REC-INC-001)
Curators must apply modern biochemical criteria for protein moonlighting as established in [`docs/architecture/scientific-background.md` (§2.1)](../architecture/scientific-background.md):
1. **Diverse Structural Mechanisms**: Moonlighting does **NOT** require a single rigid structural archetype. Diverse mechanisms are documented:
   - Oligomerization state changes (e.g. monomer active in catalysis, dimer/tetramer active in transcription).
   - Conformational switches or disordered-to-ordered transitions.
   - Differential interaction surfaces or surface patch moonlighting.
   - Post-translational modifications or ligand-gated functional switching.
2. **Rejection of Active-Site Distance Requirements**: **There is NO universal minimum distance between active sites.** Curators must not disqualify or penalize a candidate moonlighting protein because its functional sites are proximal, overlapping, or structurally unresolved.
3. **Qualified Sequence Homology Transfer**: Sequence similarity may reliably transfer a canonical enzymatic activity, but it does **NOT** guarantee conservation of a secondary moonlighting function or its cellular context. When evidence is derived from a homolog, curators must mark `support_class = "transferred"`, identify the donor entity, and evaluate whether experimental confirmation exists in the target organism.

---

## 7. Review Events, Disagreement, and Escalation

### 7.1 Review Roles and Operating Configurations
Curation may operate under different configurations depending on the scientific use case and available resources:
- **Single-Curator Review**: A single qualified curator reviews the evidence package and authors a contextual dossier. Suitable for exploratory documentation, pilot analyses, and preliminary reference mapping.
- **Double Review with Adjudication (Proposed Evaluation Mode)**: Two independent reviewers evaluate the same evidence package, followed by adjudicator comparison. Proposed for formal benchmark calibration studies pending approval (`DEC-CUR-05`).
- **Review Roles**:
  - *Primary Reviewer*: Conducts initial review and assigns support classifications.
  - *Secondary Reviewer*: Conducts independent duplicate review when double review is authorized.
  - *Adjudicator*: Compares independent reviews, evaluates disagreements, and formulates an adjudication record.
  - *Scientific Lead / Maintainer*: Resolves policy escalations and approves manual updates.

### 7.2 Proposed Blinding Protocol (Use-Case Dependent, Pending Approval)
Where formal benchmark evaluation studies require blinding to minimize confirmation bias:
- **Specification of Blinding**: Reviewers are blinded strictly to *computational semantic scores* (MBL, Wang, Lin, NPMI), *upstream catalog confidence tiers*, and *predictive model classifications*. Curators are **NOT** blinded to necessary biological facts, protein accessions, organism names, or the text of cited articles.
- **Use-Case Dependency**: Double-blinding is a proposed option for formal metric evaluation studies, not a mandatory prerequisite for exploratory dossiers or pilot curation.
- **Blinding Breach Logging**: If a curator inadvertently encounters score metrics or external model predictions during a blinded review, a blinding breach note is recorded (`blinding_status = "breached"`), documenting the exposure without invalidating unrelated assessments.

### 7.3 Multi-Review Tracking and Non-Destructive History
- **Historical Traceability**: Prior review records are preserved historically and not silently overwritten.
- **Adjudication Records**: Adjudications are recorded as distinct review entries (`record_kind = "adjudication"`), linked to prior reviews via `related_review_ids_json`.
- **Versioned Updates**: When newly accessible literature or corrections emerge, an updated review record is created, citing the prior record via `supersedes_review_id`.

### 7.4 Granular Stopping Conditions
Stopping conditions apply specifically to the **affected claim, reference, or review branch**. An issue on one reference or claim does **NOT** require stopping an entire entity-level review when independent claims or references remain assessable:
1. **Search Budget Exhausted (`budget_exhausted`)**: Authorized search routes and databases for a specific reference are exhausted without locating the paper. The curator halts search on *that specific reference branch* and records `status = "unresolved (budget_exhausted)"`.
2. **Document Inaccessible (`inaccessible_material`)**: A specific article is gated behind publisher paywalls or anti-bot challenge barriers with no lawful open access copy. The curator halts review of *that specific document* and records `status = "not_assessable (inaccessible_material)"`.
3. **Reference Mismatch (`reference_mismatch`)**: A cited identifier points to an unrelated paper or wrong accession. The curator halts review of *that specific reference link*, documents the issue, and files a crosswalk notice.
4. **Molecular Identity Unresolved (`unresolved_entity`)**: A published study fails to specify the organism, gene, or sequence, preventing correlation with the target entity. The curator marks *that specific evidence unit* as `unresolved_entity`.

### 7.5 Escalation Points Requiring Maintainer or Scientific Lead Decisions
The curator must escalate the issue to the Scientific Lead or Maintainer under the following conditions:
- **Direct Scientific Contradiction**: Two peer-reviewed primary studies directly contradict each other using equivalent, rigorous assays, and the contradiction cannot be resolved by context or construct differences.
- **Authoritative Retraction or Expression of Concern**: A cited paper is subject to a formal publisher retraction, editorial expression of concern, or substantive erratum altering its experimental conclusions.
- **Systemic Crosswalk Misalignment**: An entire source catalog or batch exhibits systematic misalignments between accessions, claims, and PMIDs.
- **Suspected Scientific Misconduct or Fraud**: Published figures exhibit apparent duplication or manipulation documented in post-publication peer review.

---

## 8. Analytical Use and Downstream Products

### 8.1 Proposed Downstream Data Products (Products A, B, and C)
Literature review records are designed to feed the repository data architecture in distinct ways:

```
[Raw Sources & GAFs (Preserved Artifacts)]
        │
        ▼
[Product A: Source Registry (Candidate Baseline)] ──────────────────────┐
  - Attributed source claims preserved                                  │
  - Ingestion unaffected by local literature review status              │
        │                                                               │
        ▼                                                               │
[Product B: Proposed Analytical Views & Metric Tables]                  │
  - Cross-source overlap exploration                                    │
  - Semantic distance calculations (MBL, Wang, Lin, NPMI)               │
  - Filterable by review status, but unreviewed data remains usable     │
        │                                                               │
        ▼                                                               │
[Product C: Proposed Locally Curated Subsets & Benchmark Callsets] ◄────┘
  - Contextual Adjudication Dossiers (e.g. Q9Y3E5)
  - Explicit evidence-support classifications
  - Gold-standard candidate evaluation sets
```

### 8.2 Catalog Eligibility vs Curation Completion
- **Catalog Admission Governed by Existing Contracts**: Admission to the catalog (Product A) is governed strictly by the applicable existing source contracts and architectural decisions ([ADR-005](../decisions/ADR-005-deterministic-protein-ids.md) for deterministic protein identifiers where canonical UniProtKB accessions exist; [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md) for status rows). Where an upstream source provides an entry with unresolved identity or source-native identifiers, it is cataloged or tracked according to that source's contract. This manual does **NOT** introduce independent admission or eligibility rules.
- **Curation Completion**: Literature curation is **NOT an eligibility gate for catalog inclusion**. A protein candidate remains valid in the source registry regardless of whether manual literature review has been initiated or completed.
- **Curated Benchmark Scope**: Downstream curated subsets (Product C) may restrict their scope to proteins with completed, adjudicated literature dossiers, clearly distinguishing curated ground-truth sets from the comprehensive catalog.

---

## 9. Practical Implementation Tools

### 9.1 Practical Curator Checklist
Curators should follow this practical checklist during review:

```markdown
### Literature Curation Step-by-Step Checklist

1. [ ] Target Claim Identification
   - Identify the biological statement or GO annotation being assessed.
   - Record entity identifier (UniProtKB accession, source-native ID, or internal ID).
2. [ ] Bibliographic Verification
   - Verify cited reference identifier (PMID, DOI, GO_REF, or source accession).
   - Check for errata, retractions, or corrigenda where accessible.
3. [ ] Documentary Availability & Inspection Declaration
   - Record availability: metadata_only, abstract_only, full_text, full_text_plus_supplement, inaccessible.
   - Record material actually inspected (e.g. title/abstract, methods, figures).
   - Ensure retrieval uses lawful, sanctioned channels only (no paywall/bot-check bypass).
4. [ ] Molecular Correspondence Check
   - Verify organism, gene symbol, isoform, and construct tested.
   - Assign identity status: matched, partial_match, different_entity, unresolved.
5. [ ] Assay & Evidence Localization
   - Identify assay, perturbation, and controls where inspected.
   - Record exact locator: Figure panel, Table, Page, or passage.
   - Record brief supporting excerpt or marked paraphrase under applicable terms.
6. [ ] Scientific Assessment
   - Distinguish direct observation from author interpretation or review citations.
   - Assign support outcome: supports, partially_supports, opposes, insufficient_evidence, not_addressed, not_assessable.
   - Note negative, null, or inconclusive findings without forcing them into GO NOT.
   - Evaluate moonlighting mechanisms (no active-site distance rules; qualified homology transfer).
7. [ ] Dossier Recording & Status Tracking
   - Record reviewer ID, date, access boundaries, and limitations.
   - Record review status (e.g. draft, completed, locked, or provisional).
   - Apply stopping conditions to affected branches; escalate if unresolvable contradictions occur.
```

### 9.2 Proposed Minimal Review-Record Template
The modular layout below illustrates a flexible, human-readable structure for evidence reviews in curation dossiers.

> [!NOTE]
> **Illustrative Example Only**: This template provides an illustrative layout for documentation dossiers (such as [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md)). It does **NOT** constitute an approved database schema, JSON Schema, or binding data contract. Fields may be marked N/A with justification.

#### Core Record (Minimal Required Fields)
```markdown
### Review Record: [REVIEW_RECORD_ID]
- **Target Entity**: `[UniProtKB_Accession, source-native ID, or internal ID]` (`[MFPB_PROTEIN_ID_V1 or unresolved]`)
- **Target Claim / Statement**: `[Brief statement of biological property or working_claim_id]`
- **Reviewer / Curator ID**: `[Curator_ID]`
- **Review Date**: `YYYY-MM-DD`
- **Review Status**: `[draft | completed | locked | provisional | superseded]`
- **Overall Review Outcome**: `[supports | partially_supports | opposes | insufficient_evidence | not_addressed | not_assessable]`
```

#### Optional Module A: Bibliographic Resolution & Access
```markdown
- **Reference Identifier**: `PMID:[Number]` / `DOI:[String]` / `GO_REF:[Number]` / `Source_Citation:[String]`
- **Reference Resolution Status**: `[resolved | reference_unresolved | reference_mismatch | methodological_reference]`
- **Documentary Availability**: `[metadata_only | abstract_only | full_text | full_text_plus_supplement | inaccessible]`
- **Material Actually Inspected**: `[e.g. Title and abstract text; PDB coordinate header; Results section 3]`
- **Assessment Scope**: `[e.g. Peptidyl-tRNA hydrolase catalytic activity; mitochondrial localization]`
- **Rights & Licensing Status**: `[open_access | institutional_access | metadata_only | no_reproduction]`
```

#### Optional Module B: Experimental Evidence
*(Use when inspecting empirical primary studies; mark N/A for methodological or unresolved references)*
```markdown
- **Tested Construct & Organism**: `[e.g. Recombinant human full-length protein expressed in E. coli]`
- **Molecular Correspondence**: `[matched | partial_match | different_entity | unresolved]`
- **Assay Type & Perturbation**: `[e.g. In vitro spectrophotometric esterase assay; anoikis survival curve]`
- **Controls Inspected**: `[e.g. Catalytically dead mutant, vehicle alone, substrate-free control; or not reported in inspected text]`
- **Exact Locator**: `[e.g. Figure 2B, Page 8112; Results section 3, paragraph 2]`
- **Supporting Excerpt / Paraphrase**: `"[Brief excerpt or marked paraphrase sufficient to anchor finding]"`
- **Direct Observation**: `[What was physically measured by the assay]`
- **Authors' Interpretation**: `[Conclusion asserted by article authors]`
- **Reviewer Scientific Assessment**: `[Curator assessment of what is strictly supported]`
- **Curatorial Limitations**: `[e.g. In vitro only; physiological in vivo relevance unverified; full text inaccessible]`
```

#### Optional Module C: Methodological / Inferred Evidence
*(Use for `GO_REF`, electronic projections, sequence homology models, or computational predictions)*
```markdown
- **Methodological Reference Type**: `[e.g. GO_REF:0000033 UniProtKB-KW mapping; sequence homology model]`
- **Inference Basis**: `[e.g. Curated keyword rule; BLAST transfer; phylogenetic co-occurrence]`
- **Donor Entity (if transferred)**: `[Donor protein ID, organism, and experimental evidence code; or N/A]`
- **Methodological Assessment**: `[Evaluation of rule validity or transfer confidence within scope]`
```

#### Optional Module D: Adjudication & Versioning
*(Use when recording adjudication, consensus review, or version supersession)*
```markdown
- **Record Kind**: `[adjudication | consensus | revision]`
- **Related Review IDs**: `[REV-..., REV-...]`
- **Supersedes Review ID**: `[REV-... or N/A]`
- **Adjudication Rationale**: `[Explanation of consensus, resolution of disagreement, or reason for update]`
```

### 9.3 Summary of Granular Stopping Conditions
| Condition Code | Triggering Scenario | Scope of Stopping | Required Action |
|---|---|---|---|
| `budget_exhausted` | Search routes/databases exhausted without locating cited paper. | **Affected reference branch only** | Mark reference as `unresolved (budget_exhausted)`; log query date; continue review of assessable references. |
| `inaccessible_material` | Paper behind paywall or anti-bot barrier with no lawful open access copy. | **Affected document branch only** | Mark document as `not_assessable (inaccessible_material)`; record abstract/metadata if available; continue review of accessible documents. |
| `reference_mismatch` | Cited PMID/DOI describes an unrelated topic, organism, or protein entity. | **Affected reference link only** | Mark link as `reference_mismatch`; document discrepancy; file crosswalk notice; continue review of valid references. |
| `unresolved_entity` | Published paper lacks sequence, accession, or construct details needed for matching. | **Affected evidence unit only** | Mark evidence unit as `unresolved_entity`; document limitation; assessable claims on known constructs proceed. |

### 9.4 Escalation Decision Matrix
| Escalation Trigger | Authority Required | Action Protocol |
|---|---|---|
| Direct assay contradiction between reputable primary papers. | Adjudicator / Scientific Lead | Document conflicting evidence units; record `support_outcome = "opposes"` / `conflicting`; do not average or vote by journal prestige. |
| Authoritative retraction notice or expression of concern. | Scientific Lead / Maintainer | Verify retraction notice; document retraction scope; downgrade affected evidence units; do not delete historical record. |
| Systemic crosswalk misalignment affecting multiple records. | Maintainer / Data Architect | Halt batch curation; open bug report on ingestion crosswalk; await catalog patch. |
| Suspected data manipulation or fraudulent publication. | Scientific Lead | Document objective published critiques/errata; mark evidence units as disputed; escalate to project governance. |

### 9.5 Practical Desk-Check Demonstration
To verify that this modular curation procedure represents diverse real-world cases without forcing irrelevant fields or unsupported conclusions, three documented cases from existing repository documentation were evaluated:

#### Desk-Check 1: An Unresolved Reference
- **Scenario**: An upstream catalog cites an erroneous or missing citation string that cannot be resolved to a PubMed record.
- **Representation**:
  - *Core Record*: Target entity recorded via source ID or canonical ID; claim recorded; curator ID and date logged; `Overall Review Outcome = "not_assessable"`.
  - *Module A*: `Reference Identifier = "CITED_ID_12345"`, `Reference Resolution Status = "reference_unresolved"`, `Documentary Availability = "inaccessible"`, `Material Actually Inspected = "Source catalog metadata only"`.
  - *Module B*: All experimental fields (assay, controls, locator) marked **N/A (unresolved reference)**.
  - *Outcome*: The procedure represents the bibliographic gap accurately without forcing an arbitrary biological refutation or halting review of independent claims for the same entity.

#### Desk-Check 2: A Methodological Reference (`GO_REF`)
- **Scenario**: A GO annotation supported by `GO_REF:0000033` (UniProtKB-KW to GO mapping) with evidence code `IEA`.
- **Representation**:
  - *Core Record*: Target entity recorded; claim recorded; curator ID and date logged; `Overall Review Outcome = "supports"` (for the mapping rule).
  - *Module A*: `Reference Identifier = "GO_REF:0000033"`, `Reference Resolution Status = "methodological_reference"`, `Documentary Availability = "metadata_only"`, `Material Actually Inspected = "Gene Ontology Consortium mapping documentation"`.
  - *Module B*: All experimental assay fields marked **N/A (methodological reference)**.
  - *Module C*: `Methodological Reference Type = "GO_REF:0000033"`, `Inference Basis = "Curated mapping between UniProtKB keyword and GO Molecular Function"`.
  - *Outcome*: The methodological mapping is documented cleanly without requiring a non-existent PubMed ID or forcing primary assay fields.

#### Desk-Check 3: An Experimental Claim with Partial Support
- **Scenario**: Human PTRH2/Bit1 interaction with Groucho/TLE corepressors ([`DOSSIER-Q9Y3E5-001` (`STMT-07`)](Q9Y3E5_contextual_adjudication_dossier.md)).
- **Representation**:
  - *Core Record*: `Target Entity = "Q9Y3E5"` (`MFP:U:c382ca456ad5a4db`), `Target Claim = "Bit1 interacts with full-length Groucho/TLE corepressors"`, `Overall Review Outcome = "partially_supports"`.
  - *Module A*: `Reference Identifier = "PMID:15006356"`, `Reference Resolution Status = "resolved"`, `Documentary Availability = "abstract_only"`, `Material Actually Inspected = "Title and abstract text"`, `Assessment Scope = "Protein-protein interaction with AES / TLE family"`.
  - *Module B*: `Tested Construct & Organism = "Mammalian cell culture"`, `Molecular Correspondence = "matched"`, `Exact Locator = "Title and abstract text"`, `Direct Observation = "Cytoplasmic Bit1 forms a physical complex with AES, a small Groucho/TLE protein"`, `Reviewer Scientific Assessment = "AES binding is directly supported; direct binding to full-length TLE1 corepressor is not established in the abstract"`, `Curatorial Limitations = "Full text inaccessible behind Elsevier paywall; interaction with full-length TLE1 uninspected"`.
  - *Outcome*: The distinction between what was directly supported (AES complex) and what was unestablished (direct TLE1 binding) is captured precisely, respecting documentary access boundaries without forcing an unsubstantiated binary label.

---

## 10. Open Governance Decisions

Before this manual can transition from a **Proposed Procedure** to an **Approved Normative Standard**, repository governance and maintainers must formally resolve the following open decisions:

```
[Open Decision Register: Literature Curation]
  ├─ DEC-CUR-01: Formal adoption of curation workflow for Phase D0 pilot
  ├─ DEC-CUR-02: Approved software tools and privacy constraints for assisted extraction
  ├─ DEC-CUR-03: Curator qualification standards and peer review sign-off protocols
  ├─ DEC-CUR-04: Repository schema formalization for structured review tables
  └─ DEC-CUR-05: Double-blinding criteria for evaluation benchmarks vs exploratory dossiers
```

### 10.1 `DEC-CUR-01`: Formal Adoption of Curation Workflow for Phase D0
- **Question**: Shall this curation protocol be formally adopted as the standard manual for Phase D0 post-v1 contextual adjudication and pilot curation?
- **Current Status**: **Proposed**.
- **Impact**: Authorizes authoring production curation dossiers under [`docs/curation/`](.) using these standardized headings and rules.
- **Authority**: Maintainers & Scientific Lead.

### 10.2 `DEC-CUR-02`: Approved Software Tools for Assisted Extraction
- **Question**: Which natural language processing, text-mining, or large language model (LLM) tools are permitted for assisted literature extraction, and what data-privacy and licensing constraints apply?
- **Current Status**: **Open Question**.
- **Impact**: Defines boundaries for computational assistance, preventing transmission of non-public or copyrighted literature text to unapproved third-party cloud services.
- **Authority**: Maintainers & Technical Architect.

### 10.3 `DEC-CUR-03`: Curator Qualification and Conflict-of-Interest Standards
- **Question**: What scientific qualifications, training calibration, and conflict-of-interest declarations are required for curators authoring and adjudicating dossiers?
- **Current Status**: **Open Question**.
- **Impact**: Establishes peer-review requirements for promoting draft dossiers to approved benchmark callsets.
- **Authority**: Scientific Lead.

### 10.4 `DEC-CUR-04`: Repository Schema Formalization for Structured Review Tables
- **Question**: Should structured review tables (`review_records`, `functional_claims`) be formalized into binding repository data contracts and schemas, distinguishing them from the existing functional claims pilot?
- **Current Status**: **Deferred**.
- **Impact**: Requires formal SDD specification and data contract definition before any code or schema implementation. Does not prescribe an unapproved directory structure.
- **Authority**: Maintainers & Data Architect.

### 10.5 `DEC-CUR-05`: Criteria for Double-Blinded Review vs Single-Curator Review
- **Question**: What specific criteria determine when double-blinded review (blinding curators to GO semantic scores and catalog tiers) is required (e.g. formal benchmark calibration) versus single-curator review for exploratory dossiers?
- **Current Status**: **Open Question**.
- **Impact**: Balances curation throughput for exploratory dossiers against statistical rigor for formal benchmark validation.
- **Authority**: Scientific Lead & Statistical Reviewer.

---

## 11. Section-Level Provenance and Traceability Matrix

The table below provides comprehensive traceability for every substantive section and procedure in this manual, mapping recovered material to historical dossiers, recovery-map items, existing dossiers, and repository governance:

| Manual Section & Topic | Source Document & Heading | Recovery Map Item | Existing Dossier / Architectural Precedent | Epistemic Classification | Status & Dependencies |
|---|---|---|---|---|---|
| **§1.1 Purpose & Role** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 1. Propósito, autoridad y leyenda` | `MAP-06-01` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§2.2) | Recovered Procedural Recommendation | Proposed procedure; non-blocking role defined. |
| **§1.2 Non-Blocking Preservation** | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) (§3.3) | `MAP-06-01` | [ADR-001](../decisions/ADR-001-repository-scope.md), [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) | Proposed Architectural Principle | Invariant: review never gates catalog ingestion. |
| **§1.3 Operating Modes** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 2. Catálogo, revisión y decisión` | `MAP-06-01` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§4) | Recovered Procedural Recommendation | Supports both atomic statements and entity syntheses. |
| **§2.1 Seven Curation Units** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 2. Catálogo, revisión y decisión` (L65–L83) | `MAP-06-01` | [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) | Recovered Procedural Recommendation | Decouples entity, claim, annotation, source, reference, evidence, decision. |
| **§2.2 Relational Principles** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 2. Catálogo, revisión y decisión` | `MAP-06-01` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§1.1) | Recovered Procedural Recommendation | Preserves source claims without overwriting. |
| **§3.1 Reference Diversity** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 4.2. Referencias e identidad` | `MAP-06-02` | GAF 2.2 format specification | Recovered Procedural Recommendation | Accepts PMIDs, DOIs, `GO_REF`, database IDs. |
| **§3.2 Unresolved References** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 4.2 & 9.2. Texto inaccesible` | `MAP-06-02` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§1.2) | Recovered Procedural Recommendation | Records `reference_mismatch`; no silent replacement. |
| **§4.1 Availability & Inspection** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 4.3 & 7.6. Estado de acceso` | `MAP-06-02` | Separated availability, inspection, and scope | Recovered Procedural Recommendation | Explicit declaration: availability vs material inspected. |
| **§4.2 Legal Boundaries** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 4.3. Búsqueda delimitada` (L125) | `MAP-06-02` | [`AGENTS.md`](../../AGENTS.md) (§6, Prohibited Autonomous Actions) | Existing Governing Requirement | Strict ban on paywall/bot-check bypass. |
| **§4.3 Partial Inspection Limits** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 9.2. Texto inaccesible` | `MAP-06-02` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§3, §4) | Case-Specific Practice from Dossier | Case study of abstract limits without universalization. |
| **§5.1 Precise Locators** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 5.2. Ficha de extracción` (L157) | `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§4) | Recovered Procedural Recommendation | Exact Figure panel, Table, Page, or passage required. |
| **§5.2 Assisted Extraction** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 16.3. Protección de textos` (L595) | `MAP-06-03` | [`AGENTS.md`](../../AGENTS.md) (§1.1, Scope Boundaries) | Proposed Practice | Machine-extracted text distinct from curated evidence. |
| **§6.1 Molecular Identity** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 5.1 & 7.1. Identidad del objeto` | `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§1) | Recovered Procedural Recommendation | Verified correspondence: matched, partial, different, unresolved. |
| **§6.2 Observation vs Discussion** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 5.1. Secuencia de revisión` | `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§3, §5.1) | Recovered Procedural Recommendation | Measured result separated from hypothesis/discussion. |
| **§6.3 Support Outcomes** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 6 & 7.4. Correspondencia` | `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§4, §6) | Recovered Procedural Recommendation | `supports`, `partially_supports`, `opposes`, `insufficient_evidence`, `not_addressed`, `not_assessable`. |
| **§6.4 Negative Evidence** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 9.3. Contradicciones` | `MAP-06-03` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§1.2) | Recovered Procedural Recommendation | Null assays recorded with context; never forced into GO `NOT`. |
| **§6.5 Moonlighting Mechanisms** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 8. Multifuncionalidad amplia` | `MAP-06-03` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§2.1) | Recovered Procedural Recommendation | Diverse mechanisms; no active-site distance rules; qualified homology transfer. |
| **§7.1 Review Roles** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 10.1. Roles` | `MAP-06-02` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (Header) | Recovered Procedural Recommendation | Single-curator vs double-review configurations. |
| **§7.2 Blinding Protocols** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 4.1 & 10.3. Cegamiento` | `MAP-06-02` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§3.2) | Proposed Practice (Use-Case Dependent) | Blinding against scores/rankings; breach documentation. |
| **§7.3 Multi-Review Immutability** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 11. Desacuerdos y actualización` | `MAP-06-03` | Non-destructive auditability principles | Recovered Procedural Recommendation | Reviews preserved; adjudications append new records. |
| **§7.4 Granular Stopping** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 4.3 & 16. Criterios de parada` | `MAP-06-02` | Branch-specific stopping rules | Recovered Procedural Recommendation | Stopping applies to affected branch without halting entity. |
| **§7.5 Escalation Points** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 11 & 16.2. Pendientes` | `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§6) | Recovered Procedural Recommendation | Direct contradictions, retractions, crosswalk breaks. |
| **§8.1 Downstream Products** | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) (§3.3) | `MAP-06-01` | [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§2.2) | Proposed Architectural Model | Products A, B, and C decoupled. |
| **§8.2 Candidate Eligibility** | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) (§3.3) | `MAP-06-01` | [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md), [ADR-006](../decisions/ADR-006-coverage-only-moonprot-status-rows.md) | Existing Governing Requirement | Admission governed by existing source contracts, not manual review. |
| **§9.1 Practical Checklist** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 5.1. Secuencia de revisión` | `MAP-06-03` | Synthesis of workflow steps | Recovered Procedural Recommendation | Practical step-by-step verification checklist. |
| **§9.2 Modular Template** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 14. Plantilla review_records.csv` | `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§4) | Proposed Illustrative Tool | Modular core + optional modules; not a binding schema. |
| **§10. Open Decisions** | [`docs/archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md`](../archive/proposals-2026-10-spanish/06_manual_revision_bibliografica.md) <br> `## 16.2. Pendientes accionables` | `MAP-06-01`, `MAP-06-02`, `MAP-06-03` | [`docs/curation/Q9Y3E5_contextual_adjudication_dossier.md`](Q9Y3E5_contextual_adjudication_dossier.md) (§6) | Decisions Still Requiring Approval | `DEC-CUR-01` through `DEC-CUR-05` formally enumerated. |

---

*End of Literature Curation Manual (`DOC-MAN-LITERATURE-CURATION-V1`). Proposed procedure awaiting maintainer and scientific lead review.*
