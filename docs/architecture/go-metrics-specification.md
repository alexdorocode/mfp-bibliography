# Gene Ontology Metrics and Semantic Dissimilarity Specification: Mathematical Formulations, Aggregation Contracts, and Analytical Boundaries

## Document Control & Epistemic Status

| Attribute | Specification Record |
|---|---|
| **Document Title** | Gene Ontology Metrics and Semantic Dissimilarity Specification: Mathematical Formulations, Aggregation Contracts, and Analytical Boundaries |
| **Document ID** | `DOC-SPEC-GO-METRICS-V1` |
| **Document Path** | [`docs/architecture/go-metrics-specification.md`](go-metrics-specification.md) |
| **Document Status** | **Recovered analytical design — proposed, pending scientific and implementation review.**<br>*The filename does not make it an approved executable specification.* |
| **Document Role** | Reference Mathematical Specification and Analytical Design Proposal |
| **Source Material** | Recovered from historical dossiers [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) (§§1–16) and [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md) (§§1–10), addressing recovery-map items (`MAP-04-01`, `MAP-04-02`, `MAP-04-03`, `MAP-04-04`, `MAP-04-05`, `MAP-04A-01` in [`docs/reports/documentation-recovery-map.md`](../reports/documentation-recovery-map.md)), contextualized by [`docs/architecture/scientific-background.md`](scientific-background.md) and [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md). |
| **Target Increment** | `REC-INC-003-GO-METRICS-RECOVERY` (Revision: Status and Provenance Clarification Pass) |
| **Governing Authority** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |
| **Date** | 2026-11-10 |

> [!IMPORTANT]
> **Analytical Scope and Non-Execution Notice**:
> 1. **Proposed Status**: This document specifies proposed mathematical formulations, aggregation rules, and edge-case conventions for Gene Ontology (GO) semantic dissimilarity, information-theoretic measures, and cross-aspect association metrics. It is **NOT** an approved executable specification, binding release contract, or operational pipeline mandate.
> 2. **No Code Implementation Implied**: Nothing in this document authorizes writing metric computation engines into repository source code, executing metric calculations, generating synthetic numerical tables, or querying live databases without formal maintainer approval and scoped Specification-Driven Development (SDD) packages under [`specs/`](../../specs/).
> 3. **Draft Design Identifiers**: All metric identifiers (e.g. `go_mbl_depth_dca_mean`, `go_wang_dissimilarity_mean`) and version numbers (e.g. `0.1.0`, `go-cross-aspect-npmi@1.0.0`) in this document are **proposed design labels recovered from historical research drafts**, NOT released code implementations, deployed endpoints, or active repository interfaces.
> 4. **Repository Responsibility Boundaries**: In accordance with [ADR-001](../decisions/ADR-001-repository-scope.md), `mfp-bibliography` is dedicated to source-evidence cataloging, provenance tracking, and bibliographic infrastructure. Documenting metric designs here recovers historical research proposals; it does **NOT** decide that metric calculation engines belong within this repository rather than in downstream modeling repositories.

---

## 1. Purpose, Epistemic Scope, and Analytical Boundaries

### 1.1 Purpose of Metric Recovery and Epistemic Distinctions
In historical research plans (specifically the PEC-EXP-001 framework documented in [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) and [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md)), semantic dissimilarity metrics on the Gene Ontology Directed Acyclic Graph (DAG) were proposed as descriptive instruments to characterize functional annotation divergence among proteins attributed as multifunctional.

The purpose of this document is to recover the exact mathematical definitions, DAG traversal rules, information-theoretic estimators, and cross-aspect association formulas into an auditable English reference document, while making all analytical dependencies, edge-case conventions, and interpretation boundaries explicit.

To ensure epistemic rigor, this document maintains strict distinctions between five categories of statements:
1. **Definitions Recovered from Historical Sources**: Exact mathematical equations ($d_{\text{MBL}}$, $IC$, $S_a(u)$, $SV$, $W$, $d_W$, $L$, $d_L$, $\text{NPMI}$, $Sim_{\text{Resnik}}$) and conceptual domains recovered directly from historical dossiers `04` and `04a`.
2. **Proposed Analytical and Output Conventions**: Proposed conventions for term preparation (excluding roots from candidate sets), pairwise aggregation (unweighted pair mean), complete coverage requirements for primary scores, diagnostic `available_mean` reporting, and long-format schema layouts. These represent proposed methodological choices awaiting formal evaluation, not binding repository standards.
3. **Open Decisions**: Methodological questions explicitly requiring scientific lead and maintainer resolution ([`DEC-MET-01` through `DEC-MET-06`](#82-register-of-open-decisions)).
4. **Observed Library Behavior**: Reported findings regarding external codebases (`CBBIO/GO.py`, `tanghaibao/goatools`) recovered from historical research audits, distinguished from direct local inspections.
5. **Approved Governing Requirements**: Binding architectural invariants established by accepted Architectural Decision Records ([ADR-001](../decisions/ADR-001-repository-scope.md), [ADR-002](../decisions/ADR-002-raw-data-immutability.md), [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md), [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md)) and repository governance ([`AGENTS.md`](../../AGENTS.md) Sections 5 and 6).

### 1.2 Separation of Interpretation Boundaries
To prevent the misuse of mathematical scores as biological ground truth, this specification establishes strict interpretation boundaries (aligned with [`docs/architecture/scientific-background.md` (§3)](scientific-background.md)):

```
[Mathematical / DAG Metric Layer]
  - Graph distance, information content, semantic similarity, NPMI
  - Strictly descriptive statistics over existing annotation sets
        │
        ▼ (DO NOT CONFLATE)
[Biological & Evidentiary Layer]
  - Physiological mechanisms, active site separation, cellular states
  - Primary experimental assays, literature curation, direct evidence
```

Curators, analysts, and future implementations must strictly enforce the following distinctions:
1. **Annotation Breadth vs Biological Multifunctionality**: A protein annotated with distant GO terms possesses broad or diverse curatorial annotations. This divergence does **not** prove that the protein possesses distinct physical active sites, operates via diverse physiological mechanisms, or constitutes a biological moonlighting protein.
2. **Semantic Dissimilarity vs Demonstrated Mechanism**: Graph distance reflects the hierarchical topology, curatorial granularity, and historical development of the Gene Ontology. It does **not** measure physical distance between binding pockets, structural independence, or biochemical autonomy.
3. **Statistical Co-Occurrence vs Contextual Linkage**: Cross-aspect co-occurrence (e.g. between an enzymatic Molecular Function and a Cellular Component) measures how frequently two terms appear together across a reference proteome. It does **not** demonstrate that the catalytic activity is physically executed within that subcellular compartment.
4. **Empirical Reference Populations vs Validated Negative Controls**: A reference population derived from general proteomic databases (such as the BioData reference corpus) is a contextual statistical background. It is **never a verified negative class (Non-Multifunctional / NMF)**. An unannotated or low-scoring protein represents an annotation gap, not evidence of monofunctionality.
5. **Descriptive Exploration vs Classifier Benchmarking**: Metric distributions are proposed for exploratory descriptive analysis and ranking within declared cohorts. They do **not** possess validated classification thresholds or diagnostic cutoffs. Thresholds must not be invented or labeled as validated standards.
6. **Decoupling from Manual Literature Review**: Metric calculation operates on structured annotation callsets; its availability does **not** require prior manual literature review. Conversely, a high or low metric score does **not** alter the manual review status or candidate eligibility of a catalog protein.

### 1.3 Repository Responsibility and Scope Boundaries
The architectural boundaries of `mfp-bibliography` are established by accepted Architectural Decision Records:
- **[ADR-001](../decisions/ADR-001-repository-scope.md) (Repository Scope)**: Dedicates `mfp-bibliography` to auditable source-evidence infrastructure, data provenance, and bibliographic curation, explicitly deferring machine learning models, classifiers, and embedding workflows to downstream repositories.
- **[ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md) (v1 Scope Descoping)**: Descoping external bibliographic relations and complex enrichment from the baseline catalog release (`v0.3.0`).

To maintain architectural clarity, capabilities are categorized into four distinct implementation tiers:

| Tier | Definition | Scope in `mfp-bibliography` |
|---|---|---|
| **Tier 1: Packaged Candidate Baseline** | Formally packaged release candidates (`mfp-catalog-candidate-v0.3.0`). | Five-source entity cataloging, raw artifact freezing ([ADR-002](../decisions/ADR-002-raw-data-immutability.md)), deterministic identity digests ([ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)), and offline verification (`PACKAGE_VERIFY`). |
| **Tier 2: Committed Implementation** | Merged code in `src/` and `scripts/`. | Source parsers, entity normalization, schema verification, and exploratory overlap analyses. |
| **Tier 3: Uncommitted Experimental Work** | Local prototypes and pilot slices. | Functional normalization pilot (`specs/functional-normalization-pilot/`) and interim slices. |
| **Tier 4: Proposed Future Work** | Unimplemented research proposals. | Metric computation engines (MBL, Wang, Lin, NPMI), downstream analytical views (Product B), and curated benchmark subsets (Product C). |

> [!NOTE]
> **Open Scope Decision**: The presence of this specification in `docs/architecture/` documents the analytical design recovered from research proposals. It does **not** constitute authorization to build metric computation engines in `mfp-bibliography`. Whether metric execution belongs in this repository, in a downstream repository (e.g. `mfp-analysis` or `mfp-dataset-designer`), or as an independent standalone package remains an open governance decision ([`DEC-MET-06`](#82-register-of-open-decisions)).

---

## 2. General Metric Domain, Term Preparation, and Proposed Aggregation Conventions

### 2.1 General Domain and Input Term Sets
All semantic similarity and dissimilarity metrics in this specification operate over structured sets of Gene Ontology terms assigned to normalized protein entities under defined experimental conditions ([`docs/roadmap/04_especificacion_metricas.md` (§3.1)](../roadmap/04_especificacion_metricas.md)).

Let:
- $P$ be a normalized protein entity identified by its deterministic accession or identifier (`protein_id`, e.g. `MFP:U:...` per [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)).
- $X \in \{\text{MF}, \text{BP}, \text{CC}\}$ denote the Gene Ontology aspect: Molecular Function (`molecular_function`), Biological Process (`biological_process`), or Cellular Component (`cellular_component`).
- $c$ denote the evidence filter condition (e.g. `ALL` for all evidence codes, `EXP` for conventional experimental evidence codes `IDA`, `IMP`, `IPI`, `IGI`, `IEP`, `EXP`, or `EXP_EXTENDED`).
- $T_X(P, c)$ denote the prepared, deduplicated set of canonical GO terms assigned to protein $P$ in aspect $X$ under condition $c$.

#### Domain Rules and Governing Invariants
1. **Intra-Aspect Domain Boundary**: For intra-aspect metrics (MBL, Wang, Lin, Resnik), comparisons occur **strictly within a single ontology aspect** ($X$). Terms from different aspects (e.g. comparing a Molecular Function term to a Cellular Component term) reside outside the defined domain of intra-aspect metrics and are categorized as `CROSS_ASPECT`. No artificial root-to-root bridges or graph distances across aspects are defined.
2. **Root Term Exclusion (Proposed Convention)**: The aspect root terms (`GO:0003674` for MF, `GO:0008150` for BP, `GO:0005575` for CC) are proposed to be excluded from the candidate term set $T_X(P, c)$ for scoring. They participate internally in DAG traversals as common ancestors, but do not contribute as primary scoring terms.
3. **Canonical Identifier Resolution**: Secondary, alternate, and obsolete GO identifiers must be resolved to current canonical identifiers prior to input preparation. Obsolete terms lacking a replacement cannot be scored and are classified as `UNRESOLVED_TERM`.
4. **Negation Exclusion (Governing Invariant)**: In accordance with repository rules ([`AGENTS.md`](../../AGENTS.md) Section 5), annotations carrying a `NOT` qualifier represent negative evidence. They must **never** be included in positive functional term sets $T_X(P, c)$ for semantic similarity or dissimilarity scoring.

### 2.2 Admissible Term Pairs and Graph Projections
For a protein with $k = |T_X(P, c)|$ unique prepared terms in aspect $X$:
The candidate pair set $C_X(P, c)$ consists of all unordered, distinct pairs of terms:

$$C_X(P, c) = \left\{ \{t_i, t_j\} : t_i, t_j \in T_X(P, c), \ i < j \right\}$$

The total number of candidate pairs is given by the binomial coefficient:

$$|C_X(P, c)| = \binom{k}{2} = \frac{k(k - 1)}{2}$$

#### Pairing Rules (Proposed Conventions)
- **No Self-Pairs (Diagonal Excluded)**: Pairs of identical terms $\{t_i, t_i\}$ are excluded from protein-level aggregation. They are defined for unit-testing primitive functions (where distance must equal 0 and similarity must equal 1), but do not participate in calculating internal protein dispersion.
- **Ancestor–Descendant Pairs**: Pairs where one term is an ancestor of the other within the DAG are included in $C_X(P, c)$ if both terms were explicitly asserted for the protein, reflecting curatorial granularity differences.
- **No Redundant Aliases**: Terms that resolve to the same canonical GO ID do not generate distinct pairs. Duplicate annotation rows in raw GAFs do not increase $|C_X(P, c)|$.

### 2.3 Proposed Aggregation Conventions and Coverage Guardrails
Let $d(a, b)$ be a pairwise dissimilarity metric evaluated on term pair $\{a, b\}$.
Let $V_X(P, c) \subseteq C_X(P, c)$ be the subset of candidate pairs for which the metric returns a mathematically valid, finite result satisfying all graph and profile preconditions.

The unweighted pairwise arithmetic mean is defined as:

$$\bar{d}_X(P, c) = \frac{1}{|V_X(P, c)|} \sum_{\{a, b\} \in V_X(P, c)} d(a, b)$$

Pairwise coverage is defined as:

$$\text{coverage}_X(P, c) = \frac{|V_X(P, c)|}{|C_X(P, c)|}$$

#### Proposed Cardinality and Coverage Conventions
1. **$k = 0$ (No terms)**: $|C| = 0$. Aggregation is impossible. Output: `value = null`, `available_mean = null`, `coverage = null`, `status = INSUFFICIENT_TERMS`.
2. **$k = 1$ (Single term)**: $|C| = 0$. Dispersion is impossible. Output: `value = null`, `available_mean = null`, `coverage = null`, `status = INSUFFICIENT_TERMS`. (Having only one term does not imply a dissimilarity of zero; internal pairwise distance is undefined).
3. **$k = 2$ (Single pair)**: $|C| = 1$. If valid, $|V| = 1$, `value = d(t_1, t_2)`, `coverage = 1.0`, `status = OK`.
4. **Complete Coverage Rule for Primary Score (Proposed Policy)**: Historical specification [`04_especificacion_metricas.md` (§3.2)](../roadmap/04_especificacion_metricas.md) proposes a conservative reporting convention:
   - If $|V_X(P, c)| = |C_X(P, c)|$ (100% coverage), the primary metric is emitted: `value = \bar{d}`, `status = OK`.
   - If $|V_X(P, c)| < |C_X(P, c)|$ (partial coverage, e.g. one term lacks corpus frequency for Lin), the primary score is withheld: `value = null`, `status = PARTIAL_COVERAGE`.
   - In partial coverage cases, the diagnostic field `available_mean` preserves the average across valid units to prevent silent data loss, while clearly signaling incomplete coverage.
   - This convention is proposed to prevent biased comparisons between proteins whose scores reflect all pairs and those whose scores omit difficult-to-evaluate terms.
5. **Unweighted Pair Contributions**: Each pair carries an equal weight of 1 in the arithmetic mean. Pairs are not weighted by citation count, evidence code hierarchy, or term depth.

### 2.4 Numerical States, Absence, and Undefined Values
To maintain data integrity, metric computation engines must strictly distinguish four distinct states:
1. **Mathematically Undefined**: A calculation that cannot be performed due to mathematical constraints (e.g. zero denominator in Lin, division by zero in empty sets, or disconnected graph components). Represented by `value = null` with an explicit reason code (e.g. `ZERO_IC_DENOMINATOR`).
2. **Insufficient Input**: The entity lacks the minimum number of terms required to define the operation (e.g. $k < 2$ for pairwise dissimilarity; $k = 0$ for Information Content). Represented by `value = null`, `status = INSUFFICIENT_TERMS`.
3. **Excluded Observation**: The candidate pair resides outside the defined metric domain (e.g. cross-aspect term pairs for MBL/Wang/Lin). Handled by domain guards before candidate set formation; if encountered, classified as `CROSS_ASPECT`.
4. **Computed Zero**: A legitimate, finite numerical calculation resulting in $0.0$ (e.g. identical terms in primitive tests, root terms with frequency $1.0$, or zero MBL between identical depths). Represented by `value = 0.0`, `status = OK`. **A computed zero must NEVER be used to represent missing data or undefined calculations.**

### 2.5 Recovered Proposed Evidence Partitions and Input Selection Conditions

> [!NOTE]
> **Recovered Proposed Analytical Partitions — Not an Adopted Experiment Policy or Implemented Filter**:
> The partition definitions in this subsection are recovered from historical research proposals ([`docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§4)](../roadmap/02_protocolo_cientifico_y_analisis.md), [`docs/roadmap/core/experiment_definition.md` (§3.3)](../roadmap/core/experiment_definition.md), and decision `DEC-05`), addressing recovery map item `MAP-02-02`. They document proposed analytical input partitions ($c$) for exploratory semantic dissimilarity comparisons. They do **not** constitute an adopted experimental policy, an engineering release contract, or an active runtime filter. Documenting these historical proposals preserves scientific methodology without authorizing execution or creating a new evidence taxonomy.

#### 1. Recovered Evidence Partition Specifications

In historical experimental plans, three primary input conditions were proposed to evaluate how semantic dissimilarity metrics behave across different levels of curatorial evidence:

| Condition Label & Proposed ID | Included GO Evidence Codes (Established) | Explicitly Excluded Codes & Scope Limits | Membership Nature | Intended Analytical Purpose & Planned Comparisons | Source Provenance | Verification Status | Governance & Approval Status |
|---|---|---|---|---|---|---|---|
| **`ALL`** /<br>`ALL_ELIGIBLE` | **26 explicit codes in historical catalog**: `EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`, `HTP`, `HDA`, `HMP`, `HGI`, `HEP`, `IBA`, `IBD`, `IKR`, `IRD`, `ISS`, `ISO`, `ISA`, `ISM`, `IGC`, `RCA`, `TAS`, `NAS`, `IC`, `ND`, `IEA`.<br>*In `experiment_definition.md`: all admissible codes following GO processing and qualifier policy.* | Unrecognized or novel evidence codes not in the controlled snapshot list are excluded (inventoried via incident report, not automatically ingested).<br>`NOT` qualifiers excluded by qualifier policy. | Exhaustive 26-code catalog in `02` §4.2; rule-governed snapshot in `experiment_definition.md` §3.3. | **Baseline coverage condition**; reference universe for term and co-occurrence background frequencies. Primary contrast baseline against experimental subsets. | [`docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§4.2)](../roadmap/02_protocolo_cientifico_y_analisis.md); [`docs/roadmap/core/experiment_definition.md` (§3.3)](../roadmap/core/experiment_definition.md). | Recovered from historical proposals; code definitions documented locally; formal external sync pending. | Proposed analytical design; governed by decision `DEC-05` (pending Gate G2). |
| **`EXP-convencional`** /<br>`EXP_CONVENTIONAL` | **6 conventional experimental codes**: `EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`.<br>*(Note: `EXP_CONVENTIONAL` is the partition label; `EXP` is an individual GO evidence code [Inferred from Experiment]).* | Explicitly excludes high-throughput experimental codes (`HTP`, `HDA`, `HMP`, `HGI`, `HEP`).<br>Explicitly excludes author statements (`TAS`, `NAS`), curator statements (`IC`), computational/sequence analysis (`ISS`, `ISO`, `ISA`, `ISM`, `IGC`, `RCA`), phylogenetic inference (`IBA`, `IBD`, `IKR`, `IRD`), electronic annotations (`IEA`), and `ND`. | Exhaustive 6-code set. | **Primary experimental contrast** proposed for the evaluation pilot (`EXP_CONVENTIONAL` vs `ALL`). Evaluates pairwise dispersion supported exclusively by small-scale, conventional experimental assays. | [`docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§§4.1–4.3)](../roadmap/02_protocolo_cientifico_y_analisis.md); [`docs/roadmap/core/experiment_definition.md` (§3.3)](../roadmap/core/experiment_definition.md). | Recovered from historical proposals; code meanings verified against standard GO documentation cited in source; formal verification pending external sync. | Proposed analytical design; governed by decision `DEC-05` (pending Gate G2). |
| **`EXP-ampliada`** /<br>`EXP_EXTENDED` | **11 experimental codes**: 6 conventional (`EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`) plus 5 high-throughput experimental codes (`HTP`, `HDA`, `HMP`, `HGI`, `HEP`). | Explicitly excludes author statements (`TAS`, `NAS`), curator statements (`IC`), computational/sequence analysis, phylogenetics, electronic (`IEA`), and `ND`.<br>*(High-throughput separation is methodological, not an inherent universal quality hierarchy).* | Exhaustive 11-code set. | **Secondary planned sensitivity contrast** (`EXP_EXTENDED` vs `ALL`, and `EXP_EXTENDED` vs `EXP_CONVENTIONAL`). Evaluates metric sensitivity to the addition of high-throughput experimental evidence. | [`docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§§4.1–4.3)](../roadmap/02_protocolo_cientifico_y_analisis.md); [`docs/roadmap/core/experiment_definition.md` (§3.3)](../roadmap/core/experiment_definition.md). | Recovered from historical proposals; formal external sync pending. | Proposed analytical design; governed by decision `DEC-05` (pending Gate G2). |

> [!IMPORTANT]
> **Controlled Definition of `ALL` vs Unrestricted Ingestion**:
> In this specification and its source proposals, **`ALL` denotes all controlled evidence categories admissible within a frozen, defined input snapshot**. It does **NOT** denote unrestricted ingestion of every raw database row regardless of technical, syntactic, or qualifier validity. Novel or uncataloged codes encountered in an ingestion snapshot must be quarantined and reported, never silently absorbed into `ALL` or reclassified as experimental. Furthermore, while the `ND` (No biological Data available) code is inventoried as an observed annotation category in raw snapshots, it is **never interpreted as a demonstrated biological function**.

> [!NOTE]
> **Historical Antecedent Conflict Resolved**:
> An earlier project questionnaire (`PEC_Phase0_questionari_abast_cientific.md`, question A4) historically grouped `TAS` (Traceable Author Statement) and `IC` (Inferred by Curator) under a heading that described the set as experimental. Dossier `02` (§4.1) explicitly identified and corrected this conflict based on official Gene Ontology Consortium standards: GO classifies `TAS` as an author statement and `IC` as curator judgment, **neither of which constitutes experimental evidence**. Consequently, `TAS` and `IC` are strictly excluded from both `EXP_CONVENTIONAL` and `EXP_EXTENDED`.

#### 2. Separation of Orthogonal Filtering Dimensions

Evidence-code partition membership is strictly an annotation-level provenance filter. It must **never** be conflated with or used to substitute for independent technical, biological, or curatorial filtering dimensions:

1. **Annotation Polarity and Negation Handling**: Evidence-code filtering selects rows based on the GO evidence code column. It does **not** determine annotation polarity. In accordance with repository rules ([`AGENTS.md`](../../AGENTS.md) Section 5), annotations carrying a `NOT` qualifier represent negative evidence; they must **never** silently become positive functional observations. Negations are filtered by qualifier guards prior to semantic scoring, regardless of whether their evidence code is `EXP` or `IEA`.
2. **Bibliographic Reference Type (`PMID` vs `GO_REF` vs `DOI`)**: Evidence-code filtering does **not** filter by bibliographic identifier format. An annotation supported by a curated `GO_REF` or a DOI without an assigned PubMed ID (`PMID`) is **not** automatically excluded from an evidence partition.
3. **Local Manual Literature Review Status**: Evidence-code filtering operates on structured Layer 2 annotation callsets. It does **not** require prior manual literature adjudication (Product C). An unreviewed external annotation is not automatically excluded from `EXP_CONVENTIONAL` or `EXP_EXTENDED` if its structured GAF evidence code satisfies the partition.
4. **Protein Entity and Isoform Resolution**: Mapping UniProtKB accessions and isoforms to deterministic entity identifiers (`MFPB_PROTEIN_ID_V1` under [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)) occurs in the entity resolution pipeline, not during evidence-code filtering.
5. **Documentary and Full-Text Availability**: Primary publication availability (e.g. open-access vs paywalled articles, or document retrieval failures) governs Layer 3 manual curation feasibility, not Layer 2 GO evidence code filtering.
6. **Gene Ontology Aspect ($X \in \{\text{MF}, \text{BP}, \text{CC}\}$)**: Evidence-code filtering is orthogonal to ontology aspect. Evidence partitions apply uniformly across aspects or within a designated aspect.
7. **Technical Assay Validation**: Specific biochemical validation of an assay cannot be inferred from evidence codes alone.
8. **Final Metric Scoring Eligibility**: Inclusion of an annotation under an evidence partition does not guarantee that a protein can be scored. Entities must independently satisfy term cardinality ($k \ge 2$), DAG connectivity, and coverage guardrails ([§2.3](#23-proposed-aggregation-conventions-and-coverage-guardrails)).
9. **No Cartesian MF–BP–CC Triplet Context**: Co-annotation across aspects does **not** demonstrate that a catalytic Molecular Function is executed within an annotated Cellular Component ([`AGENTS.md`](../../AGENTS.md) Section 5). Complete annotation across all three aspects is **never** required as a prerequisite for intra-aspect metric scoring.

#### 3. Verification Limits and Open Governance Questions

To maintain transparency, the epistemic boundaries of this recovery are explicitly recorded:

1. **Verification Limits**:
   - *Faithful Documentary Recovery*: The historical partitions (`ALL` / `ALL_ELIGIBLE`, `EXP-convencional` / `EXP_CONVENTIONAL`, `EXP-ampliada` / `EXP_EXTENDED`) and their code memberships have been verified directly against historical source documents `docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§4) and `docs/roadmap/core/experiment_definition.md` (§3.3).
   - *Authoritative External Standard Sync Pending*: While code definitions correspond to established Gene Ontology Consortium standards cited in the historical dossiers, live network verification against remote ontology registries is excluded from this increment (performed offline in read-only mode).
   - *Scientific Adoption Separate from Recovery*: Recovering and documenting these proposed partitions satisfies documentation reconciliation (`MAP-02-02`). It does **not** constitute formal experimental adoption, which remains a separate governance decision.
2. **Open Governance Decisions and Unresolved Items**:
   - **`DEC-05` (Evidence Policies Adoption)**: Formal experimental adoption of `ALL_ELIGIBLE`, `EXP_CONVENTIONAL`, and `EXP_EXTENDED` remains pending Gate G2 review.
   - **`DEC-MET-06` (Metric Hosting Scope)**: Whether metric computation engines executing these filters belong in `mfp-bibliography` or in downstream analytical repositories remains an open governance decision.
   - **Annotation-Count Downsampling Calibration**: Historical protocols propose controlling for term count reduction by repeatedly downsampling `ALL_ELIGIBLE` to the term count of the compared experimental policy. The exact repetition count, pseudo-random number generator, and seed schedule remain uncalibrated proposals.
   - **Uncataloged Evidence Codes**: Rules for handling newly created GO Consortium evidence codes in future releases remain to be formalized in an operational protocol.

---

## 3. Metric Inventory: Detailed Specifications

All metric identifiers (e.g. `go_mbl_depth_dca_mean`, `go_term_ic`, `go_wang_dissimilarity_mean`, `go_lin_dissimilarity_mean`, `go_assoc_mf_bp`) and version numbers (e.g. `0.1.0`, `go-cross-aspect-npmi@1.0.0`) in this section are **proposed design labels recovered from historical draft proposals `04` and `04a`**. They do not denote released software implementations.

### 3.1 Minimum Branch Length (MBL)

#### Identification and Scientific Question
- **Proposed Metric Identifier / Version**: `go_mbl_depth_dca_mean` / `0.1.0` (Proposed design version).
- **Scientific Question**: What structural separation exists between the terms assigned to a protein entity within a GO aspect, measured by depth differences to their Deepest Common Ancestor (DCA)?
- **Intended Analytical Role**: Structural graph-distance baseline reflecting hierarchical separation on the DAG.

#### Mathematical Formulation
Let $G = (V_G, E_G)$ be the Gene Ontology Directed Acyclic Graph restricted to aspect $X$ and transitive `is_a` relationships.
Let $h(t)$ be the maximum depth of term $t$ from the aspect root $r$, such that $h(r) = 0$, and for any child $v$ of parent $u$, $h(v) \ge h(u) + 1$.
Let $\text{Anc}^*(t) = \text{Anc}(t) \cup \{t\}$ denote the reflexive ancestor closure of $t$.

For two terms $a, b \in T_X(P, c)$, the set of common ancestors is:

$$H(a, b) = \text{Anc}^*(a) \cap \text{Anc}^*(b)$$

Assuming $H(a, b) \ne \emptyset$ (guaranteed in a single-aspect DAG rooted at $r$):
The maximum depth among all common ancestors defines the Deepest Common Ancestor (DCA) depth:

$$h^*(a, b) = \max_{u \in H(a, b)} h(u)$$

The pairwise MBL structural distance is defined as:

$$d_{\text{MBL}}(a, b) = h(a) + h(b) - 2h^*(a, b)$$

The protein-level aggregated score is the mean over all unique candidate pairs:

$$\bar{d}_{\text{MBL}}(P, X, c) = \frac{1}{|C_X(P, c)|} \sum_{\{a, b\} \in C_X(P, c)} d_{\text{MBL}}(a, b)$$

#### Inputs, Types, and Scale
- **Required Inputs**: Pinned Gene Ontology OBO/OWL graph; transitive `is_a` closure; maximum depth lookup table per term.
- **Output Type & Range**: Pairwise distance is an integer $\ge 0$. Aggregated protein mean is a non-negative real number ($\bar{d} \ge 0$).
- **Direction**: Distance metric; higher values represent greater structural separation on the DAG.
- **Identity Property**: For identical terms, $h^*(a, a) = h(a)$, yielding $d_{\text{MBL}}(a, a) = h(a) + h(a) - 2h(a) = 0$.

#### Documentary Audit: MBL Fallback Algebraic Derivation ($d_f = -1$)
- **Evidence Type**: **Documented static derivation** recovered from historical dossier [`docs/roadmap/04_especificacion_metricas.md` (§4.3, L153–L164)](../roadmap/04_especificacion_metricas.md).
- **Documented Rationale**: In historical dossier `04`, static inspection of remote `CBBIO/GO.py` code noted that its local fallback logic defined:
  $$H_{\text{fallback}} = (\text{Anc}(a) \cap \text{Anc}(b)) \cup \{a, b\}$$
  $$h_f = \max_{u \in H_{\text{fallback}}} h(u), \qquad d_f = h(a) + h(b) - 2h_f$$
  The dossier noted: *"Esta es una consecuencia algebraica del código leído, no un test ejecutado."*
  Because $\{a, b\}$ were included directly in $H_{\text{fallback}}$, if $a$ and $b$ reside on distinct branches with unequal depths (e.g. $h(a) = 1, h(b) = 2$), taking the maximum depth yields $h_f = h(b) = 2$, producing:
  $$d_f = 1 + 2 - 2(2) = 3 - 4 = -1$$
- **Proposed Handling Policy**: The proposed design adopts the primary DCA formulation ($H(a, b) = \text{Anc}^*(a) \cap \text{Anc}^*(b)$) and proposes that any fallback path producing negative distances be classified as an unvalidated implementation path (`status = INVALID_OUTPUT` or `NO_COMMON_ANCESTOR`). This represents a theoretical algebraic consequence documented in historical research, not an executed test suite run in this repository.

#### Analytical Limitations
1. **DCA Depth $\ne$ Shortest Path**: In a tree, $d_{\text{MBL}}$ equals the shortest path length between nodes. In a DAG with multiple inheritance, the shortest path (BFS) may be strictly shorter than the DCA depth difference.
2. **Hierarchical Uniformity Assumption**: MBL assumes that a branch step at depth 1 represents the same biological divergence as a branch step at depth 10, ignoring variations in ontology detail.

---

### 3.2 Information Content (IC) and Protein Mean

#### Identification and Scientific Question
- **Proposed Metric Identifiers / Versions**: Primitive `go_term_ic` / `0.1.0`; Aggregate `go_ic_mean` / `0.1.0` (Proposed design versions).
- **Scientific Question**: How statistically specific or rare are the GO terms annotated to a protein relative to a frozen background reference population?
- **Intended Analytical Role**: Information-theoretic specificity descriptor; serves as a foundational input for Lin and Resnik metrics.

#### Mathematical Formulation
Let $R_X$ be a frozen reference universe of distinct, reconciled protein entities having at least one valid annotation in aspect $X$, with total count $N_X = |R_X| > 0$.
For any term $t$, let $n_X(t)$ be the count of distinct protein entities in $R_X$ whose propagated ancestor closure under authorized relationships contains $t$.
The empirical annotation probability of term $t$ is:

$$p_X(t) = \frac{n_X(t)}{N_X}, \qquad \text{where } 0 < p_X(t) \le 1$$

The Information Content of term $t$ (in natural units, nats) is defined as the negative log-likelihood:

$$IC_X(t) = -\ln p_X(t) = -\ln \left( \frac{n_X(t)}{N_X} \right) = \ln N_X - \ln n_X(t)$$

The protein-level aggregated Information Content is the arithmetic mean across all unique terms in $T_X(P, c)$:

$$\overline{IC}_X(P, c) = \frac{1}{|V_X(P, c)|} \sum_{t \in V_X(P, c)} IC_X(t)$$

where $V_X(P, c) \subseteq T_X(P, c)$ contains all terms with valid, positive frequencies in the reference corpus.

#### Inputs, Types, and Scale
- **Required Inputs**: Frozen reference corpus counts ($n_X(t)$); corpus size ($N_X$); log base $e$ (natural log).
- **Output Type & Range**: Real number $\ge 0$. Bounded in $[0, \ln N_X]$.
- **Direction**: Information specificity metric; higher values indicate rarer, more specific terms.
- **Root Term Value**: Because the aspect root $r$ covers all annotated entities in the aspect ($n_X(r) = N_X$), $p_X(r) = 1.0$, yielding $IC_X(r) = -\ln(1.0) = 0.0$.
- **Aggregated Unit**: Information Content is aggregated across **individual terms**, NOT across term pairs.

#### Edge Cases and Proposed Null-Handling Policy
1. **Uncovered Term ($n_X(t) = 0$)**: If a term is valid in the GO OBO but never observed in the reference corpus, $p(t) = 0$. $IC(t) = -\ln(0)$ is mathematically infinite.
   - **Proposed Handling Policy**: To avoid injecting arbitrary pseudocounts (such as $\epsilon$) into empirical frequencies, the proposed convention classifies the term as `UNCOVERED_TERM` with `value = null`. Under the proposed complete coverage rule, the protein mean becomes `value = null`, `status = PARTIAL_COVERAGE`, while `available_mean` averages the remaining covered terms.
2. **Empty Reference Corpus ($N_X = 0$)**: Output is `null`, `status = EMPTY_REFERENCE`.
3. **Corpus Consistency**: $n_X(t) \le N_X$ must hold for all terms. If $n_X(t) > N_X$, the profile is corrupted (`status = INVALID_PROFILE`).

---

### 3.3 Wang Semantic Dissimilarity

#### Identification and Scientific Question
- **Proposed Metric Identifier / Version**: `go_wang_dissimilarity_mean` / `0.1.0` (Proposed design version).
- **Scientific Question**: How much ancestral DAG topology and semantic structure do the terms of a protein entity fail to share?
- **Intended Analytical Role**: Primary graph-based semantic dissimilarity baseline, independent of corpus frequency counts.

#### Mathematical Formulation
Formulated by Wang et al. (2007) ([`docs/roadmap/04_especificacion_metricas.md` (§6)](../roadmap/04_especificacion_metricas.md)), this metric evaluates the semantic contribution of all ancestors of a term in a sub-DAG.
Let $D_a = (V_{D_a}, E_{D_a})$ be the sub-DAG containing term $a$ and all its ancestors under authorized relations.
For any edge $(u, v) \in E_{D_a}$ where $u$ is a parent of child $v$, let $w(u, v)$ be the semantic contribution factor:
- For `is_a` relationships: $w_{\text{is\_a}} = 0.8$ (proposed parameter).
- For `part_of` relationships: $w_{\text{part\_of}} = 0.6$ (proposed parameter where authorized).

The semantic contribution of ancestor $u$ to term $a$, denoted $S_a(u)$, is defined recursively:

$$S_a(a) = 1.0$$

$$S_a(u) = \max_{(u, v) \in E_{D_a}} \{ w(u, v) \cdot S_a(v) \} \quad \text{for } u \ne a$$

If multiple paths connect $u$ to $a$, the path maximizing semantic contribution is chosen.
The total Semantic Value of term $a$ is the sum of contributions of all its ancestors:

$$SV(a) = \sum_{u \in V_{D_a}} S_a(u)$$

The Wang Semantic Similarity between terms $a$ and $b$ is the proportion of shared ancestral semantic value over total semantic value:

$$W(a, b) = \frac{\sum_{u \in V_{D_a} \cap V_{D_b}} (S_a(u) + S_b(u))}{SV(a) + SV(b)}$$

The Wang Semantic Dissimilarity is defined as:

$$d_W(a, b) = 1.0 - W(a, b)$$

The protein-level aggregated score is the mean over all unique candidate pairs:

$$\bar{d}_W(P, X, c) = \frac{1}{|C_X(P, c)|} \sum_{\{a, b\} \in C_X(P, c)} d_W(a, b)$$

#### Inputs, Types, and Scale
- **Required Inputs**: Pinned Gene Ontology graph; relationship subset and edge weights ($w_{\text{is\_a}} = 0.8$, optional $w_{\text{part\_of}} = 0.6$). Does not require a corpus frequency profile.
- **Output Type & Range**: Real number bounded in $[0.0, 1.0]$.
- **Direction**: Dissimilarity metric; $0.0$ indicates identical terms ($W(a, a) = 1.0$), $1.0$ indicates completely disjoint ancestral subgraphs.
- **Denominator Safety**: Because $S_a(a) = 1.0$ and $S_b(b) = 1.0$, $SV(a) \ge 1.0$ and $SV(b) \ge 1.0$. Thus, $SV(a) + SV(b) \ge 2.0$. The denominator cannot be zero in any valid graph.

#### Analytical Limitations
1. **Ad-Hoc Weighting**: Edge weights ($0.8, 0.6$) are empirical constants proposed by Wang et al. (2007); they do not reflect learned or biological transition probabilities.
2. **No Metric Distance Properties**: Although $d_W \in [0, 1]$, it does not satisfy the triangle inequality and is not a formal mathematical metric.

---

### 3.4 Lin Semantic Dissimilarity

#### Identification and Scientific Question
- **Proposed Metric Identifier / Version**: `go_lin_dissimilarity_mean` / `0.1.0` (Proposed design version).
- **Scientific Question**: What proportion of the information content of two terms is not captured by their Most Informative Common Ancestor (MICA)?
- **Intended Analytical Role**: Information-theoretic semantic dissimilarity measure combining ontology topology with empirical corpus frequencies.

#### Mathematical Formulation
Formulated by Lin (1998) and adapted to Gene Ontology ([`docs/roadmap/04_especificacion_metricas.md` (§7)](../roadmap/04_especificacion_metricas.md)):
Let $H(a, b) = \text{Anc}^*(a) \cap \text{Anc}^*(b)$ be the common ancestor set of terms $a$ and $b$.
The Most Informative Common Ancestor (MICA) is any common ancestor that maximizes Information Content:

$$IC_{\text{shared}}(a, b) = \max_{u \in H(a, b)} IC_X(u)$$

$$\text{MICA}(a, b) = \arg\max_{u \in H(a, b)} IC_X(u)$$

The Lin Semantic Similarity is defined as the ratio of twice the shared information to the sum of individual term information:

$$L(a, b) = \frac{2 \cdot IC_{\text{shared}}(a, b)}{IC_X(a) + IC_X(b)}$$

The Lin Semantic Dissimilarity is:

$$d_L(a, b) = 1.0 - L(a, b)$$

The protein-level aggregated score is the mean over all unique candidate pairs:

$$\bar{d}_L(P, X, c) = \frac{1}{|C_X(P, c)|} \sum_{\{a, b\} \in C_X(P, c)} d_L(a, b)$$

#### Distinction: MICA vs DCA
A critical theoretical requirement is distinguishing MICA from DCA:
- **DCA (Deepest Common Ancestor)**: Maximizes structural depth $h(u)$ from the root.
- **MICA (Most Informative Common Ancestor)**: Maximizes empirical Information Content $IC(u)$.
Because annotation frequency does not vary monotonically with structural depth across all DAG branches, DCA and MICA frequently diverge. Lin dissimilarity strictly requires MICA. Using DCA in place of MICA constitutes a distinct, unapproved metric.

#### Edge Cases and Proposed Zero-Denominator Policy
1. **Positive Denominator ($IC(a) + IC(b) > 0$)**: Formula applies directly. If both terms are covered and their only common ancestor is the root ($IC_{\text{shared}} = 0$), $L(a, b) = 0.0$ and $d_L(a, b) = 1.0$.
2. **Zero Denominator ($IC(a) = IC(b) = 0$)**: Occurs if both terms have frequency $p = 1.0$ in the corpus (e.g. root terms or ubiquitous terms).
   - **Proposed Handling Policy**: When $IC(a) = IC(b) = 0$, $L(a, b) = \frac{0}{0}$ is mathematically undefined. Some libraries adopt conventions that return $1.0$ (assuming identity) or $0.0$ under this condition. In this specification, the proposed analytical policy classifies the result as `ZERO_IC_DENOMINATOR` with `value = null`. This policy is proposed to avoid equating uninformative background terms with maximal similarity or maximal dissimilarity. Both approaches represent distinct modeling choices; the proposed convention reflects the conservative reporting design of historical dossier `04`.
3. **Uncovered Terms**: If either term has $n_X(t) = 0$, $IC(t)$ is undefined, and Lin cannot be evaluated (`UNCOVERED_TERM`).

---

### 3.5 Resnik Semantic Similarity (Contextual Research Inventory)

#### Identification and Scientific Question
- **Metric Formulation**: Resnik Semantic Similarity, $Sim_{\text{Resnik}}(a, b)$ ([`docs/roadmap/core/experiment_definition.md` (§3.3)](../roadmap/core/experiment_definition.md)).
- **Scientific Question**: How much information do two terms share through their most informative common ancestor?
- **Intended Analytical Role**: Pure shared information measure, unnormalized by individual term specificities.

#### Mathematical Formulation
The Resnik similarity between terms $a$ and $b$ is defined solely as the Information Content of their MICA:

$$Sim_{\text{Resnik}}(a, b) = IC(\text{MICA}(a, b)) = \max_{u \in H(a, b)} IC(u)$$

#### Properties, Scale, and Status in Specification
- **Output Type & Range**: Real number in $[0.0, \ln N_X]$ (in nats).
- **Direction**: Similarity measure; $0.0$ indicates that the terms share only the root term (or terms with frequency 1.0), while higher values indicate that they share a rare, highly specific ancestor.
- **Unbounded Nature**: Unlike Lin and Wang, Resnik similarity is **not normalized to $[0, 1]$**. Its maximum possible value varies with the size of the reference corpus ($\ln N$).
- **Dissimilarity Inversion**: Converting Resnik similarity to a dissimilarity measure is non-trivial:
  - Subtracting from maximum corpus information ($d = \ln N - Sim_{\text{Resnik}}$) introduces strong corpus-size sensitivity.
  - Non-linear transforms (e.g. $e^{-Sim_{\text{Resnik}}}$) alter the metric space.
- **Implementation Status in Repository**: In historical dossier [`04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md), Resnik was discussed as a related measure, but was **descoped from the primary intra-aspect suite** in favor of normalized dissimilarity metrics (1-Wang and 1-Lin). It remains recorded here as an unadopted research candidate.

---

### 3.6 Cross-Aspect Associations (NPMI)

#### Identification and Scientific Question
- **Proposed Metric Identifiers / Version**: `go_assoc_mf_bp`, `go_assoc_mf_cc`, `go_assoc_bp_cc` / `go-cross-aspect-npmi@1.0.0` (Proposed design labels).
- **Scientific Question**: How frequently do specific pairs of terms from different ontology aspects co-occur across proteins in a reference corpus, relative to statistical independence?
- **Intended Analytical Role**: Characterizes empirical co-annotation patterns between Molecular Functions, Biological Processes, and Cellular Components, preventing unjustified Cartesian triplet synthesis.

#### Mathematical Formulation
Formulated in historical annex [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md):
Let $X, Y \in \{\text{MF}, \text{BP}, \text{CC}\}$ with $X \ne Y$ denote two distinct ontology aspects.
Let $R_{XY}$ be the dual reference universe: distinct reconciled protein entities annotated with at least one valid term in *both* aspects $X$ and $Y$, with size $N_{XY} = |R_{XY}| > 0$.
For terms $x \in X$ and $y \in Y$:
- $n_x$: number of entities in $R_{XY}$ annotated with $x$ (propagated).
- $n_y$: number of entities in $R_{XY}$ annotated with $y$ (propagated).
- $n_{xy}$: number of entities in $R_{XY}$ annotated with *both* $x$ and $y$.

Empirical marginal and joint probabilities are:

$$p(x) = \frac{n_x}{N_{XY}}, \qquad p(y) = \frac{n_y}{N_{XY}}, \qquad p(x, y) = \frac{n_{xy}}{N_{XY}}$$

Pointwise Mutual Information (PMI) is normalized by the negative self-information of the joint occurrence:

$$s_{XY}(x, y) = \text{NPMI}(x, y) = \frac{\ln \left( \frac{p(x, y)}{p(x) p(y)} \right)}{-\ln p(x, y)} = \frac{\ln p(x, y) - \ln p(x) - \ln p(y)}{-\ln p(x, y)}$$

#### Inputs, Types, and Scale
- **Required Inputs**: Frozen dual-aspect reference corpus ($R_{XY}$); marginal counts ($n_x, n_y$); joint co-occurrence counts ($n_{xy}$).
- **Output Type & Range**: Real number bounded in $[-1.0, 1.0]$.
  - $+1.0$: Complete co-occurrence ($p(x, y) = p(x) = p(y)$).
  - $0.0$: Statistical independence ($p(x, y) = p(x) \cdot p(y)$).
  - Negative values: Co-occurrence less frequent than expected by independence.
- **Symmetry**: $s_{XY}(x, y) = s_{YX}(y, x)$. NPMI is symmetric and carries **no causal or temporal direction**.

#### Proposed Support Filters and Zero-Co-Occurrence Policy
To prevent statistical noise from rare terms, [`docs/roadmap/04a_asociaciones_interaspecto.md` (§4)](../roadmap/04a_asociaciones_interaspecto.md) proposes explicit support thresholds:
- Minimum marginal support: $n_x \ge 5$ and $n_y \ge 5$ (`min_term_support = 5`, provisional).
- Minimum joint support: $n_{xy} \ge 5$ (`min_pair_support = 5`, provisional).

| Condition | Mathematical Context | Proposed Handling Policy in Specification |
|---|---|---|
| $n_{xy} = 0$ (Zero co-occurrence) | Joint frequency reaches zero ($p(x, y) = 0$). Bouma (2009) defines the mathematical limit as $-1.0$. | **Withhold scoring**: `value = null`, `status = UNOBSERVED_PAIR`. Proposed rationale: avoid equating unobserved pairs with active biological exclusion when corpus coverage is sparse. Bouma's limit remains a mathematically coherent alternative convention. |
| $n_{xy} < 5$ or $n_x < 5$ or $n_y < 5$ | Support below provisional threshold. | `value = null`, `status = LOW_SUPPORT`. |
| $n_{xy} = N_{XY}$ (Degenerate joint) | Both terms present in 100% of corpus. | $-\ln(1.0) = 0$ in denominator; division by zero. Classified as `value = null`, `status = DEGENERATE_JOINT`. |

#### Protein-Level Aggregation (Proposed Convention)
For protein $P$ with terms $T_X(P)$ and $T_Y(P)$:
The candidate set is the Cartesian product $C_{XY}(P) = T_X(P) \times T_Y(P)$.
Let $V_{XY}(P) \subseteq C_{XY}(P)$ be the pairs satisfying support thresholds with `status = OK`.
The available protein association mean is:

$$A_{\text{available}, XY}(P) = \frac{1}{|V_{XY}(P)|} \sum_{(x, y) \in V_{XY}(P)} s_{XY}(x, y)$$

Pair coverage is $\text{coverage}_{XY}(P) = |V_{XY}(P)| / |C_{XY}(P)|$.
- **Proposed Coverage Policy**: If $\text{coverage} \ge 0.80$ (provisional threshold), primary `value = A_{\text{available}}`, `status = OK`. If $\text{coverage} < 0.80$, primary `value = null`, `status = LOW_PAIR_COVERAGE`, while `available_mean` preserves the calculation for diagnostic inspection.

---

### 3.7 Evidence, Term, and Bibliographic Descriptors
Historical specification [`04_especificacion_metricas.md` (§9)](../roadmap/04_especificacion_metricas.md) defines a suite of 14 non-similarity descriptors to quantify annotation volume, evidence types, and curatorial coverage:

| Descriptor ID | Unit & Scope | Definition & Mathematical Denominator | Expected Scale |
|---|---|---|---|
| `go_annotation_rows_count` | Raw rows per protein/aspect | Total raw annotation lines passing basic filters before deduplication. | Integer $\ge 0$ |
| `go_terms_asserted_unique_count` | Protein / aspect | Cardinality of canonical unique terms explicitly asserted (roots excluded). | Integer $\ge 0$ |
| `go_terms_propagated_only_count` | Protein / aspect | Cardinality of terms added by ancestor closure that were not in asserted set. | Integer $\ge 0$ |
| `go_terms_unique_count` | Protein / aspect | Total unique terms in final prepared set ($k = \|T_X(P, c)\|$). | Integer $\ge 0$ |
| `go_evidence_rows_count` | Protein / aspect / code | Raw rows carrying a specific GO evidence code (e.g. `IDA`, `IMP`). | Integer $\ge 0$ |
| `go_evidence_codes_count` | Protein / aspect | Distinct evidence codes observed among valid annotations. | Integer $\ge 0$ |
| `go_reference_ids_unique_count` | Protein / aspect | Distinct reference strings (PMID, DOI, GO_REF) linked to annotations. | Integer $\ge 0$ |
| `go_publications_unique_count` | Protein / aspect | Reconciled unique publication entities (aliases resolved). | Integer $\ge 0$ |
| `mfp_publications_unique_count` | Protein / claims | Reconciled unique publications linked to source MFP claims. | Integer $\ge 0$ |
| `go_experimental_term_fraction` | Protein / aspect | Asserted terms with $\ge 1$ conventional experimental code divided by total asserted terms. | Real $[0.0, 1.0]$ |
| `go_experimental_extended_term_fraction` | Protein / aspect | Asserted terms with $\ge 1$ extended experimental code divided by total asserted terms. | Real $[0.0, 1.0]$ |
| `go_term_retention_fraction` | Protein / aspect | Explicit terms retained under condition $c$ divided by terms under `ALL`. | Real $[0.0, 1.0]$ |
| `go_reference_link_coverage` | Protein / aspect | Valid rows with $\ge 1$ normalized reference divided by total valid rows. | Real $[0.0, 1.0]$ |
| `go_publication_resolution_fraction` | Protein / aspect | Candidate reference strings resolved to a known publication entity divided by total candidates. | Real $[0.0, 1.0]$ |

---

## 4. Analytical Dependencies and Parameter Decisions

Any implementation of the metrics in Section 3 depends upon eleven key methodological choices that must be resolved and pinned:

### 4.1 GO Ontology Release and Permitted Relationships
- **Ontology Release**: Calculations depend on the specific Gene Ontology release (e.g. `go-basic.obo` vs full `go.owl`). The exact release date, commit, and file hash must be pinned.
- **Permitted Relationships**:
  - Intra-aspect distance (MBL, Wang, Lin) historically defaults to `is_a` only.
  - Optional inclusion of `part_of` alters ancestor closures and Wang contributions ($w_{\text{part\_of}} = 0.6$, proposed).
  - Regulatory relationships (`regulates`, `positively_regulates`, `negatively_regulates`) are **excluded** by default due to non-transitive or polarity-inverting semantics.

### 4.2 Annotation Snapshot and Evidence Policy
- **GAF / Annotation Release**: Annotations change over time due to ongoing curation. An annotation snapshot must be frozen.
- **Evidence Code Filtering ($c$)**:
  - `ALL`: Includes computational predictions (`IEA`), author statements (`TAS`, `NAS`), and experimental codes.
  - `EXP`: Strictly requires conventional experimental codes (`IDA`, `IMP`, `IPI`, `IGI`, `IEP`, `EXP`).
  - `EXP_EXTENDED`: Includes high-throughput experimental codes (`HTP`, `HDA`, `HMP`, `HGI`, `HEP`).

### 4.3 Negation and Unknown Polarity
- **`NOT` Qualifier Handling**: Annotations carrying a `NOT` qualifier indicate that the protein specifically does *not* possess the property.
- **Governing Rule**: In accordance with [`AGENTS.md`](../../AGENTS.md) Section 5, negated annotations must be preserved as negative evidence and excluded from positive functional term sets $T_X(P, c)$. They cannot be scored with MBL, Wang, or Lin.

### 4.4 Direct Annotations vs Ancestor Propagation
- **Asserted Sets for Intra-Protein Dispersion**: $T_X(P, c)$ contains explicitly asserted terms (with roots excluded). Computing pairwise dispersion across fully propagated closures would artificially inflate pair counts with ancestor-ancestor steps and bias averages toward shallow terms.
- **Propagated Sets for Frequencies and Traversals**: True-path ancestor propagation is mandatory when computing corpus frequency counts $n_X(t)$ and determining common ancestors $H(a, b)$.

### 4.5 Obsolete Terms and Identifier Resolution
- **Secondary vs Primary Identifiers**: Alternate IDs (e.g. merged terms) must be remapped to primary canonical IDs.
- **Obsolete Terms**: Obsolete terms (`is_obsolete: true`) lacking a `replaced_by` tag cannot be positioned in the active DAG and must be classified as `UNRESOLVED_TERM`.

### 4.6 Background Population and Counting Unit
- **Reconciled Entity as Counting Unit**: To avoid counting bias, $N$ and $n(t)$ must count **distinct reconciled protein entities** (canonical UniProtKB accessions or `MFPB_PROTEIN_ID_V1` digests per [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)), NOT annotation rows, alternative isoforms, or species strains.
- **Reference Population Selection**: The background reference population (e.g. reviewed human UniProtKB proteome vs full UniProtKB) defines the counting universe and must be frozen and documented.

### 4.7 Frequency and Information Content Estimation
- **Logarithm Base**: Information Content must use the natural logarithm ($\ln$, base $e$), with units in nats.
- **Monotonicity**: In a valid hierarchical closure, parent count $n(\text{parent}) \ge n(\text{child})$, ensuring $IC(\text{parent}) \le IC(\text{child})$.

### 4.8 Duplicate Occurrences and Set Projections
- Multiple raw GAF rows annotating the same protein to the same GO term (e.g. from different papers or curators) project to a **single unique term** in $T_X(P, c)$. Duplicate rows do not generate multiple pairs.

### 4.9 Pairwise Comparison vs Protein-Level Aggregation
- **Arithmetic Mean vs Best Match Average (BMA)**:
  - BMA measures directional or maximal alignment between two distinct sets (e.g. comparing Protein A to Protein B).
  - This specification evaluates **internal dispersion within a single protein**: unweighted arithmetic mean over all unique pairs $i < j$.

### 4.10 Cross-Aspect Co-Occurrence vs Contextual Biological Relations
- Co-occurrence frequencies in NPMI reflect general database association. They must never be converted into Cartesian product triplets $\tau = (m, b, c)$ asserting specific spatial-activity mechanisms without direct literature evidence.

### 4.11 Numerical Edge-Case Conventions
- Strict enforcement of non-imputation: mathematically undefined operations (`ZERO_IC_DENOMINATOR`, `UNCOVERED_TERM`, `UNOBSERVED_PAIR`) are proposed to produce `null`, never $0.0$ or $\pm 1.0$.

---

## 5. Implementation Audit, Evidence Types, and Repository Responsibility

### 5.1 Local Codebase Audit (`mfp-bibliography`)
A comprehensive, direct local inspection of files in the current repository confirmed the following:
- **Offline Task Execution**: **Zero network requests were performed during this task or increment.** All inspections were conducted strictly on local repository files in compliance with [`AGENTS.md`](../../AGENTS.md) Section 6.
- **`src/mfp_bibliography/`**: Inspected all local module files (`__init__.py`, `normalization.py`, `provenance.py`, `schemas.py`, `source_claims.py`, `validation.py`, `moondb_claims.py`, `plantmp_claims.py`, `multitaskprotdb_ii_records.py`, `multifacetedprotdb_records.py`, `moonprot_parser.py`, `moonprot_client.py`, `targetdata_client.py`, `overlap_audit.py`, `analysis_q1.py` through `q6.py`, `functional_normalization.py`, `functional_claims_moonprot.py`, `functional_claims_plantmp.py`, `functional_claims_multitask.py`). **No metric calculation engines for MBL, Wang, Lin, Resnik, or NPMI exist in `src/`.**
- **[`scripts/build_protein_facets.py`](../../scripts/build_protein_facets.py) (Lines 1–334)**: Inspected locally. This script extracts legacy 2-facet records (`BP1/MF1/CC1` vs `BP2/MF2/CC2`) from raw sources and TargetData; it does **not** implement or execute DAG traversals, semantic similarity metrics, or statistical association calculations.
- **Repository Scope**: In accordance with [ADR-001](../decisions/ADR-001-repository-scope.md), `mfp-bibliography` is maintained strictly as an auditable source-evidence catalog. Metric calculation engines remain proposed future work.

### 5.2 External and Upstream Library Status (Documentary Evidence from Historical Audits)
The following statements describe remote libraries that were **NOT** queried, cloned, or executed in this increment. All statements are **recovered documentary findings** from historical research dossier [`docs/roadmap/04_especificacion_metricas.md` (§2, §15)](../roadmap/04_especificacion_metricas.md):

#### 1. `CBBIO/BioData` (`CBBIO/GO.py`, remote commit `ed073bd4df680a3b45ee69943916e196d28b63b6`)
Historical dossier `04` recorded static inspection of remote commit `ed073bd4`:
- **`minimal_branch_length`**: Method exists, but its local fallback contains the algebraic derivation documented in Section 3.1 ($d_f = -1$).
- **`information_content`**: Exists, but relies on `goatools` term counts; the base logarithm in the user's installed environment was unverified.
- **`_get_wang_ss`**: Instantiates `SsWang` with `is_a` only; does not expose `part_of` weights or relations.
- **`group_similarity`**: Implements Best Match Average (BMA) for comparing two proteins, but does **not** implement the intra-protein pairwise dispersion contract required by this specification.
- **NPMI Engine**: Completely absent from `CBBIO/GO.py`.

#### 2. `tanghaibao/goatools` (remote tree revision `5b88eefcd8284f5d146d36728b4925785b563125`)
Historical dossier `04` recorded static inspection of tree revision `5b88eefc`:
- **`goatools.semantic.min_branch_length`**: Implements DCA depth formula ($h(a) + h(b) - 2h^*$).
- **`goatools.semsim.termwise.wang.SsWang`**: Implements recursive S-values with default $w_{\text{is\_a}} = 0.8$.
- **`goatools.semantic.lin_sim_calc`**: Implements Lin similarity, but introduces default conventions (e.g. returning 1.0 or 0.0 in certain boundary cases) that diverge from the proposed `ZERO_IC_DENOMINATOR` null convention defined in Section 3.4.

---

## 6. Proposed Long-Format Output Schema

When a metric computation engine is implemented, it is proposed to emit results in a standardized long-format structure ([`docs/roadmap/04_especificacion_metricas.md` (§11)](../roadmap/04_especificacion_metricas.md)):

```
[Long-Format Output Row]
  protein_id, metric_id, metric_version, condition_id, term_policy_id,
  aspect, aspect_x, aspect_y, profile_id, ontology_id,
  value, available_mean, status, reason_code,
  n_candidate_units, n_valid_units, coverage, backend_id, backend_version
```

### Proposed Schema Field Definitions

| Field Name | Type | Nullable | Description & Proposed Rule |
|---|---|---|---|
| `protein_id` | string | No | Canonical reconciled entity ID (`MFP:U:...` per [ADR-005](../decisions/ADR-005-deterministic-protein-ids.md)). |
| `metric_id` | string | No | Unique design identifier of metric (e.g. `go_wang_dissimilarity_mean`). |
| `metric_version` | string | No | Semantic version of calculation definition (e.g. `0.1.0`). |
| `condition_id` | string | No | Evidence filtering condition (e.g. `ALL`, `EXP`, `EXP_EXTENDED`). |
| `term_policy_id` | string | No | Term preparation policy (e.g. `asserted_canonical_roots_excluded`). |
| `aspect` | enum | Yes | GO aspect for intra-aspect metrics (`MF`, `BP`, `CC`); null for cross-aspect. |
| `aspect_x`, `aspect_y` | enum | Yes | Source and target aspects for cross-aspect NPMI associations. |
| `profile_id` | string | Yes | Identifier of frozen corpus frequency profile; null for graph-only metrics (Wang, MBL). |
| `ontology_id` | string | No | Pinned GO OBO/OWL release identifier and hash. |
| `value` | float64 | Yes | **Primary score**. Conditioned on complete coverage; null if coverage is partial or input is insufficient. |
| `available_mean` | float64 | Yes | **Diagnostic mean**. Average across valid units even when coverage is partial; null if no valid units. |
| `status` | enum | No | Technical execution status: `OK`, `INSUFFICIENT_TERMS`, `PARTIAL_COVERAGE`, `ZERO_IC_DENOMINATOR`, `UNCOVERED_TERM`, `CROSS_ASPECT`, `INVALID_OUTPUT`. |
| `reason_code` | string | Yes | Specific failure code when `value` is null. |
| `n_candidate_units` | integer | No | Total candidate units ($|C| = k(k-1)/2$ for pairs; $k$ for terms). |
| `n_valid_units` | integer | No | Evaluated units returning valid finite values ($|V|$). |
| `coverage` | float64 | Yes | Proportion of candidate units evaluated ($|V| / |C|$); null if $|C| = 0$. |
| `backend_id` | string | Yes | Execution library and wrapper identifier. |
| `backend_version` | string | Yes | Pinned version of execution library. |

---

## 7. Proposed Verification Plan (Checks, Not Execution)

The following verification suites are proposed for future implementations of this specification.

> [!WARNING]
> **Plan Only — Not Executed**: In accordance with the non-execution boundaries of this task, no test scripts were executed, and no synthetic datasets were computed. These checks define the proposed acceptance criteria for future implementation increments.

### Suite 1: Mathematical Boundary and Identity Checks
- **Test 1.1: Self-Dissimilarity**: For any covered term $a$ with $IC(a) > 0$, primitive functions must evaluate to $d_{\text{MBL}}(a, a) = 0$, $d_W(a, a) = 0.0$, and $d_L(a, a) = 0.0$.
- **Test 1.2: Root Term Properties**:
  - $IC(r) = 0.0$ for aspect root $r$.
  - For any covered term $a$ paired with root $r$, $d_{\text{MBL}}(a, r) = h(a)$, $d_W(a, r) > 0.0$, and $d_L(a, r) = 1.0$ (since $IC_{\text{shared}} = 0$).
- **Test 1.3: DCA Depth vs Asymmetric Fallback**: On an asymmetric two-branch tree ($R \to A \to U$ with $h=0,1,2$ and $R \to B$ with $h=0,1$), verify that MBL on $\{U, B\}$ evaluates to $2 + 1 - 2(0) = 3$. Verify that any implementation returning negative distance is flagged as `INVALID_OUTPUT`.
- **Test 1.4: Zero Denominator in Lin**: On terms where $IC(a) = IC(b) = 0$, verify conformity with the proposed `ZERO_IC_DENOMINATOR` null convention over alternative library defaults.

### Suite 2: Missing-Data and Coverage Cardinality Checks
- **Test 2.1: $k = 0$ and $k = 1$**: Must emit `value = null`, `available_mean = null`, `status = INSUFFICIENT_TERMS`.
- **Test 2.2: Partial Coverage Behavior**: On a set of 3 terms $\{A, B, C\}$ where $C$ is an `UNCOVERED_TERM` ($n_C = 0$):
  - Candidates $|C| = 3$, valid $|V| = 1$ (pair $\{A, B\}$).
  - Primary `value = null`, `status = PARTIAL_COVERAGE`.
  - Diagnostic `available_mean = d(A, B)`.
  - Verify that primary `value` is not emitted and that $C$ is not silently discarded to achieve 100% coverage.

### Suite 3: Directionality and Aggregation Consistency
- **Test 3.1: Pairwise Symmetry**: For all valid pairs, $d(a, b) = d(b, a)$ and $s_{XY}(x, y) = s_{YX}(y, x)$.
- **Test 3.2: Permutation Invariance**: Shuffling the input order of terms in $T_X(P, c)$ must yield identical floating-point output within tolerance ($10^{-12}$).
- **Test 3.3: Duplicate Invariance**: Appending duplicate GAF rows for an already annotated term must not alter $T_X(P, c)$, $|C|$, or the calculated score.

### Suite 4: Numerical Precision and Range Bounds
- **Test 4.1: Float Tolerances**: Assert float equivalence within absolute tolerance $10^{-12}$ and relative tolerance $10^{-9}$.
- **Test 4.2: Range Bounds**:
  - $d_W(a, b) \in [0.0, 1.0]$.
  - $d_L(a, b) \in [0.0, 1.0]$.
  - $s_{XY}(x, y) \in [-1.0, 1.0]$.
  Values exceeding bounds beyond rounding tolerance must raise `INVALID_OUTPUT`.

---

## 8. Provenance, Recovery Coverage, and Open Decisions Register

### 8.1 Source-to-Section Provenance Matrix

The table below documents the full traceability of recovered content to historical dossiers and documentation recovery map items:

| Recovery Map Item ID | Historical Source Path & Heading | Recovered Section in this Document | Epistemic Classification | Recovery Notes & Qualifications |
|---|---|---|---|---|
| **`MAP-04-01`** | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 3. Contrato común de métricas` (L78–L118) | **§2. General Metric Domain & Proposed Aggregation Conventions** | Proposed Analytical Design | Intra-aspect domain, single-pair arithmetic mean, complete coverage proposal, and degenerate cardinality rules recovered. |
| **`MAP-04-02`** | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 4. Ficha MBL clásica` (L119–L176) | **§3.1 Minimum Branch Length (MBL)** | Proposed Analytical Design | Mathematical DCA formulation recovered; CBBIO negative fallback derivation documented from historical audit; proposed DCA policy established. |
| **`MAP-04-03`** | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 5. Ficha Contenido Informativo` (L177–L223) | **§3.2 Information Content (IC)** | Proposed Analytical Design | Term-level natural log (nats) IC formula recovered; proposed uncovered term null policy documented. |
| **`MAP-04-04`** | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 6. Ficha 1−Wang` (L224–L276) | **§3.3 Wang Semantic Dissimilarity** | Proposed Analytical Design | S-value recurrence and Jaccard-like dissimilarity recovered; proposed edge weights ($w_{\text{is\_a}}=0.8, w_{\text{part\_of}}=0.6$) specified. |
| **`MAP-04-05`** | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 7. Ficha 1−Lin` (L277–L326) | **§3.4 Lin Semantic Dissimilarity** | Proposed Analytical Design | MICA Information-theoretic formula recovered; proposed `ZERO_IC_DENOMINATOR` null policy documented. |
| **`MAP-04A-01`** | [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md) <br> `## 2–5. Fichas NPMI` (L25–L138) | **§3.6 Cross-Aspect Associations (NPMI)** | Proposed Analytical Design | Dual-aspect NPMI formulas, provisional support thresholds ($\ge 5$), unobserved pair null convention, and provisional coverage threshold ($0.80$) recovered. |
| *(Research Context)* | [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) (§3.3) | **§3.5 Resnik Semantic Similarity** | Unadopted Research Proposal | Contextual inventory of Resnik similarity; noted as unnormalized and descoped from primary dissimilarity suite. |
| *(Descriptor Suite)* | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 9. Descriptores` (L341–L379) | **§3.7 Evidence & Bibliographic Descriptors** | Proposed Analytical Design | 14 non-similarity count and coverage descriptors recovered. |
| *(Schema Design)* | [`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md) <br> `## 11. Esquema largo` (L406–L439) | **§6. Long-Format Output Schema** | Proposed Analytical Design | Output schema structure recovered as a proposed design layout. |

### 8.2 Register of Open Decisions
Before any metric calculation engine can be implemented or approved, repository maintainers and scientific reviewers must resolve the following six open decisions:

```
[Open Decision Register: GO Metrics & Semantic Dissimilarity]
  ├─ DEC-MET-01: Pinned GO OBO/OWL release and permitted relationship subset
  ├─ DEC-MET-02: Frozen background reference population and counting unit for IC/NPMI
  ├─ DEC-MET-03: Formal adoption of DCA depth formulation vs BFS shortest path for MBL
  ├─ DEC-MET-04: Ratification of Lin zero-denominator policy (null vs imputation)
  ├─ DEC-MET-05: Ratification of NPMI minimum support (5) and coverage (0.80) thresholds
  └─ DEC-MET-06: Repository hosting responsibility for metric engines (in-repo vs downstream)
```

1. **`DEC-MET-01`: Pinned GO Release and Relationship Subset**:
   - *Question*: Which frozen Gene Ontology release (date/hash) and relationship types (`is_a` only vs `is_a` + `part_of`) are authorized for metric calculation?
   - *Status*: Open Question.
   - *Authority*: Scientific Lead & Maintainers.
2. **`DEC-MET-02`: Frozen Reference Population for Information Content**:
   - *Question*: What exact background population (e.g. reviewed human UniProtKB proteome vs full UniProtKB) defines the reference universe $N_X$ and counting unit?
   - *Status*: Open Question.
   - *Authority*: Scientific Lead & Data Architect.
3. **`DEC-MET-03`: MBL Variant Ratification**:
   - *Question*: Shall MBL be formally ratified as the DCA depth difference ($h(a) + h(b) - 2h^*$) or replaced by graph-theoretic shortest path (BFS)?
   - *Status*: Open Question.
   - *Authority*: Scientific Lead & Technical Reviewer.
4. **`DEC-MET-04`: Lin Zero-Denominator Policy**:
   - *Question*: Shall the proposed null convention (`ZERO_IC_DENOMINATOR` $\implies \text{null}$) be ratified over third-party library conventions that return $0.0$ or $1.0$?
   - *Status*: Open Question.
   - *Authority*: Scientific Lead & Statistical Reviewer.
5. **`DEC-MET-05`: NPMI Threshold Ratification**:
   - *Question*: Are the provisional support threshold ($n \ge 5$) and coverage threshold ($0.80$) statistically justified for cross-aspect association screening?
   - *Status*: Open Question.
   - *Authority*: Statistical Reviewer.
6. **`DEC-MET-06`: Repository Hosting Responsibility (In-Repo vs Downstream)**:
   - *Question*: In light of [ADR-001](../decisions/ADR-001-repository-scope.md) dedicating `mfp-bibliography` to source-evidence infrastructure, should metric computation engines be implemented in a downstream analysis repository (e.g. `mfp-analysis`) or within a dedicated sub-package of `mfp-bibliography`?
   - *Status*: Open Question.
   - *Authority*: Maintainers.

---

*End of Gene Ontology Metrics and Semantic Dissimilarity Specification (`DOC-SPEC-GO-METRICS-V1`). Recovered analytical design awaiting maintainer and scientific lead review.*
