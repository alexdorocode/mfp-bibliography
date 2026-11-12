# Scientific Background and Methodological Foundations

## Document Control & Epistemic Status

| Attribute | Specification Record |
|---|---|
| **Document Title** | Scientific Background and Methodological Foundations: Epistemic Decoupling, Evidence Layers, and Semantic Ontology Boundaries |
| **Document ID** | `DOC-ARCH-SCIENTIFIC-BACKGROUND-V1` |
| **Document Path** | [`docs/architecture/scientific-background.md`](scientific-background.md) |
| **Document Role** | Canonical Explanatory Reference Document |
| **Document Status** | **Explanatory Scientific Background Only**. This document synthesizes recovered scientific concepts, biological distinctions, and methodological rationale from historical research dossiers ([`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md), [`docs/roadmap/02_protocolo_cientifico_y_analisis.md`](../roadmap/02_protocolo_cientifico_y_analisis.md), [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md)). **It is NOT an approved experimental protocol, implementation specification, binding data contract, or operational curation policy.** |
| **Review Authority** | Senior Scientific-Software Architect & Bioinformatics Data-Provenance Reviewer |
| **Date** | 2026-11-10 |
| **Governing Governance** | [`AGENTS.md`](../../AGENTS.md), [ADR-001](../decisions/ADR-001-repository-scope.md) through [ADR-007](../decisions/ADR-007-v1-scope-descope-bibliographic-relations.md), proposed [ADR-008](../decisions/ADR-008-functional-normalization-pilot-scope.md) |

> [!NOTE]
> **Reading and Authority Notice**:
> This document provides explanatory context for the scientific rationale underlying entity cataloging, functional assertion tracking, and bibliographic curation in `mfp-bibliography`. It does not authorize software implementations or pipeline executions. Algorithmic implementations and data transformations are governed strictly by accepted Architectural Decision Records (ADRs) and formal Specification-Driven Development (SDD) increment packages under [`specs/`](../../specs/).

---

## 1. Epistemic Foundations: Attribution versus Biological Verification

### 1.1 Source Attribution versus Locally Established Conclusions
A foundational principle of this repository is the strict separation between **source attribution** and **verified biological truth**:
- **Source Attribution**: When an external source (such as MoonProt, MoonDB, MultitaskProtDB-II, or PlantMP) lists a protein entity as a "moonlighting protein" or "multifunctional protein", this statement is recorded, cataloged, and preserved verbatim as an **attributed claim with full cryptographic provenance** ([ADR-002](../decisions/ADR-002-raw-data-immutability.md), [ADR-003](../decisions/ADR-003-provenance-and-transformations.md)).
- **Locally Established Conclusions**: Recording a source assertion does **NOT** constitute a scientific endorsement, empirical verification, or biological certification by `mfp-bibliography`. An "attributed positive" in this repository means an entity claimed as multifunctional by one or more upstream databases, not a confirmed biological ground truth established by independent laboratory testing.

As formulated in historical dossier [`docs/roadmap/01_dossier_experimento.md` (§1, L40–L51)](../roadmap/01_dossier_experimento.md):
> *"«Positivo» significa aquí atribuido como tal por una fuente, no verdad biológica confirmada por este experimento."*

This repository preserves the exact chain of evidence without collapsing divergent source semantics into a single flattened label:

$$\text{Raw Source Artifact} \longrightarrow \text{Original Record \& Verbatim Text} \longrightarrow \text{Normalized Entity (UniProtKB)} \longrightarrow \text{Discrete Functional Claims}$$

### 1.2 Open-World Assumption and Negative Evidence in Gene Ontology
Biological knowledge represented in the Gene Ontology (GO) operates under the **Open-World Assumption (OWA)**:
- **Absence is an Annotation Gap, Not Negative Evidence**: If a protein is not annotated with a specific GO Molecular Function (GO-MF), Biological Process (GO-BP), or Cellular Component (GO-CC), this indicates only that the association has not been curated or asserted in the database. Under the open-world assumption, unannotated properties represent unknown biological space, not demonstration of functional absence.
- **GO `NOT` Annotations versus Negative Experimental Results**:
  - In Gene Ontology, the `NOT` qualifier is an explicit curatorial assertion stating that a gene product was evaluated and specifically determined *not* to possess an expected activity, process, or component (e.g. `NOT enables GO:0004396`), often correcting an erroneous computational prediction or documenting a notable evolutionary loss.
  - Under repository rules ([`AGENTS.md`](../../AGENTS.md) Section 5), imported GO annotations carrying a `NOT` qualifier represent negative evidence and must be preserved as such; they must never be converted or stored as positive functional assertions.
  - Crucially, a GO `NOT` qualifier must be distinguished from general experimental negative, null, or inconclusive results reported in primary literature. Inconclusive assays, assay-detection limits, negative findings under specific non-physiological conditions, or absence of binding in a single in vitro system do not automatically warrant a global GO `NOT` assertion. Literature adjudication must evaluate whether an experimental finding demonstrates a confirmed biological absence or merely reflects conditional assay limitations, and repository curation must not imply that every negative experimental finding should be transformed into an imported GO `NOT` assertion.

---

## 2. Core Conceptual Distinctions

Historical dossiers ([`docs/roadmap/01_dossier_experimento.md` (§3.2, L103–L110)](../roadmap/01_dossier_experimento.md) and [`docs/roadmap/core/experiment_definition.md` (§Terminology, L126–L146)](../roadmap/core/experiment_definition.md)) emphasize that three frequently conflated concepts must be treated as distinct:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      THREE DISTINCT CONCEPTUAL DOMAINS                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. ANNOTATION BREADTH (Curatorial / Representational Property)                  │
│    • Volume, granularity, and diversity of GO terms annotated to a protein.     │
│    • Driven by curation depth, publication popularity, and experimental bias.   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 2. BROAD MULTIFUNCTIONALITY (General Biological Property)                       │
│    • Participation in multiple distinct biochemical roles or biological paths. │
│    • May include pleiotropy, multi-domain proteins, and multi-subunit complexes.│
├─────────────────────────────────────────────────────────────────────────────────┤
│ 3. PROTEIN MOONLIGHTING (Biological Category of Multifunctionality)             │
│    • Single polypeptide chain performing two or more physiologically distinct,  │
│      autonomous biochemical or biophysical functions.                           │
│    • Involves diverse mechanisms; excludes fusions, splices, and fragments.     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

1. **Annotation Breadth (Representational)**:
   The total count and topological spread of GO terms attached to a protein. Highly researched model proteins (e.g. human glyceraldehyde-3-phosphate dehydrogenase, GAPDH) accumulate hundreds of annotations across diverse physiological processes due to intense research attention rather than unique biochemical architecture. Conflating annotation volume with biological multifunctionality introduces severe literature-bias artifacts.
2. **Broad Multifunctionality (Phenomenological)**:
   A protein executing multiple biochemical activities or participating in multiple cellular processes under an explicit operational definition. This broad class includes multi-domain proteins containing distinct catalytic subunits, multi-enzyme complexes, and broad pleiotropic regulators.
3. **Protein Moonlighting (Category of Multifunctionality)**:
   A biological category of multifunctionality involving diverse structural and physiological mechanisms through which a **single polypeptide chain** executes two or more autonomous, physiologically distinct biochemical or biophysical functions.
   - **Diverse Underlying Mechanisms**: Moonlighting does not represent a single biochemical mechanism and does not universally require distinct, spatially separated active sites. Diverse mechanisms documented in biological literature include differential oligomeric states (e.g. monomeric vs multimeric activities), allosteric conformational switching, utilization of distinct surface patches or interaction interfaces, and shared or overlapping catalytic regions with altered substrate specificities.
   - **Unadopted Historical Hypotheses**: Any past proposal suggesting a universal requirement for a minimum physical distance between active sites represents an unadopted historical hypothesis; spatial separation is not a mandatory or general exclusionary criterion for moonlighting.
   - **Exclusionary Criteria Documented in Literature**: Standard literature definitions distinguish moonlighting from other sources of multiple cellular effects by excluding:
     - Multiple functions arising from distinct structural domains created by gene duplication or chimeric domain fusion.
     - Splice isoforms derived from differential transcriptional splicing of a single gene.
     - Distinct functional fragments generated by proteolytic cleavage.
     - Broad participation in an interconnected physiological pathway (an enzyme is not moonlighting merely because its catalytic product triggers multiple downstream physiological consequences).

---

## 3. Gene Ontology Constraints and Multi-Aspect Relationships

### 3.1 Independent Nature of Standard GO Annotations and Explicit Context in Extensions / GO-CAM
In standard Gene Ontology representations (such as traditional GAF 2.2 association lines), annotations are pairwise, isolated assertions linking a gene product to an individual ontology term:

$$\langle \text{Protein}, \text{Relationship}, \text{GO Term}, \text{Evidence Code}, \text{Reference} \rangle$$

Standard GO annotations do not inherently carry joint multi-aspect context. However, Gene Ontology supports explicit contextual representation through modern curation frameworks:
- **Annotation Extensions (GAF Column 16)**: Standardized relational expressions that explicitly bind an annotation to biological context, such as specifying the compartment in which an activity occurs (`occurs_in(GO:0005737)`), dependent target genes, or specific substrate contexts.
- **GO-CAM (Gene Ontology Causal Activity Models)**: Graph-based models that explicitly link molecular activities to their upstream/downstream processes, biological pathways, and specific subcellular locations within an integrated causal model.

Where a data source or curated model explicitly supplies such contextual relationships, they are preserved and respected.

### 3.2 The Prohibited Inference: Inventing Context from Mere Co-Annotation
The bioinformatic error identified in repository audits ([`docs/audits/2026-11-06_repository-sdd-functional-normalization-audit.md`](../audits/2026-11-06_repository-sdd-functional-normalization-audit.md)) is **inventing shared biological context from mere co-annotation** when no such link is asserted by the source.

As codified in [`AGENTS.md`](../../AGENTS.md) Section 5:
> **No Unwarranted Function–Compartment Linkage**: Co-annotation of a Molecular Function (GO-MF) and a Cellular Component (GO-CC) to the same protein entity does **NOT** prove that the function is executed in that compartment. Never synthesize functional triplets by Cartesian product.

The prohibited inference is fabricating a contextual connection (such as taking independent annotations $\text{MF}_1, \text{MF}_2$ and $\text{CC}_1, \text{CC}_2$ and generating Cartesian triplets $\{(\text{MF}_1, \text{CC}_1), (\text{MF}_1, \text{CC}_2), \dots\}$) without source-native annotation extensions, GO-CAM graphs, or primary experimental literature evidence demonstrating that specific execution context.

For example, if a moonlighting protein is annotated with:
- $\text{MF}_1$: `phosphoglucose isomerase activity` (`GO:0004632`)
- $\text{MF}_2$: `cytokine activity` (`GO:0005125`)
- $\text{CC}_1$: `cytoplasm` (`GO:0005737`)
- $\text{CC}_2$: `extracellular space` (`GO:0005615`)

It is biologically known that phosphoglucose isomerase functions catalytically in the cytoplasm, whereas as a cytokine (neuroleukin/autocrine motility factor) it acts in the extracellular environment. Forming the ungrounded Cartesian product:

$$\{\text{MF}_1, \text{MF}_2\} \times \{\text{CC}_1, \text{CC}_2\} = \{(\text{MF}_1, \text{CC}_1), (\text{MF}_1, \text{CC}_2), (\text{MF}_2, \text{CC}_1), (\text{MF}_2, \text{CC}_2)\}$$

synthesizes false assertions (e.g. asserting that cytokine signaling takes place in the cytoplasm, or that glycolysis isomerization occurs extracellularly) that lack primary experimental literature support.

### 3.3 Statistical Association versus Biological Mechanism
Historical proposals ([`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md)) explore statistical co-occurrence metrics, such as Normalized Pointwise Mutual Information (NPMI), to measure the background co-occurrence frequency of MF–CC or MF–BP term pairs:

$$\text{NPMI}(m, c) = \frac{\ln\left(\frac{P(m, c)}{P(m)P(c)}\right)}{-\ln P(m, c)}$$

Methodological safeguards recovered from historical specifications include:
- A low background co-occurrence frequency between a molecular function and a cellular component indicates statistical rarity in annotation databases, but does **not** prove physiological moonlighting.
- High statistical co-occurrence reflects widespread cellular co-annotation, not functional mechanism.
- Cross-aspect associations remain descriptive exploratory metrics; they must not be converted into automated classification gates or composite scores without experimental adjudication.

---

## 4. Evidence Layers and Repository Data Products

### 4.1 The Three Conceptual Layers of Evidence
Historical dossier [`docs/roadmap/01_dossier_experimento.md` (§3.3, L111–L120)](../roadmap/01_dossier_experimento.md) establishes three distinct conceptual layers of evidence:

| Evidence Layer | Core Scientific Question | Nature of Information | Evidentiary Relationship |
|---|---|---|---|
| **Layer 1: Source Attribution Claims** | *Who presents this protein as multifunctional or moonlighting, and under what source-native category?* | Verbatim statements, raw category labels (`confirmed`, `predicted`, `likely`), raw text descriptions. | Preserves upstream source provenance; never altered or silently updated. |
| **Layer 2: Gene Ontology Associations** | *What structured ontology associations are registered for this entity, and what evidence codes support them?* | Standardized GO terms, aspects (MF, BP, CC), evidence codes (EXP, IDA, IPI, IEA, etc.). | Structured annotations; may capture only a subset of attributed functions; subject to open-world limits. |
| **Layer 3: Primary Literature Evidence** | *What does the experimental material actually demonstrate about function, physical entity, and cellular context?* | Primary publications, assay methodologies, physical constructs, purified complexes, author statements. | Independent empirical foundation; can support, contextualize, qualify, or leave unresolved Layers 1 and 2. |

### 4.2 Decoupling Evidence Layers from Repository Data Products
In the amended evolution proposal ([`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md` (§Section D)](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md)), the repository establishes a **three-product architecture**:
- **Product A**: Source Evidence Registry (the catalog baseline).
- **Product B**: Analytical Views & Population Characterization.
- **Product C**: Locally Curated & Reviewed Subsets.

> [!IMPORTANT]
> **No One-to-One Equivalence**:
> The three conceptual evidence layers do **NOT** map one-to-one to the three repository data products. The evidence layers describe the *epistemological origin and nature of the biological evidence*, whereas the data products define *engineering release packaging, governance boundaries, and analytical views*.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              EVIDENCE LAYERS vs REPOSITORY DATA PRODUCTS                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CONCEPTUAL EVIDENCE LAYERS                REPOSITORY DATA PRODUCTS              │
│                                                                                 │
│ Layer 1: Source Attribution Claims ───┐   ┌──► Product A: Source Evidence Reg.  │
│                                       ├───┤    (Frozen raw catalog baseline;    │
│ Layer 2: Gene Ontology Associations ──┤   │     verbatim source records)        │
│                                       │   │                                     │
│ Layer 3: Primary Literature Evidence ─┘   ├──► Product B: Analytical Views      │
│                                           │    (Population contrasts, evidence  │
│                                           │     partitions, metric sensitivity) │
│                                           │                                     │
│                                           └──► Product C: Locally Curated Subset│
│                                                (Adjudicated dossiers, gold-     │
│                                                 standard literature reviews)    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

- **Product A (Source Evidence Registry)** primarily encapsulates Layer 1 (raw source claims and entity resolution), but also records raw uninterpreted GO text and bibliographic locators (PMIDs) as provided by upstream sources.
- **Product B (Analytical Views)** evaluates entities across both Layer 1 claims and Layer 2 GO annotations under controlled evidence partitions (e.g. comparing ALL annotations against EXP-conventional subsets).
- **Product C (Locally Curated Subsets)** centers on rigorous Layer 3 primary literature adjudication, but directly evaluates and cross-references the claims of Layer 1 and the term validity of Layer 2.

---

## 5. Sequence Similarity and Functional Interpretation

### 5.1 Sequence Similarity and Functional Transfer
In computational biology, sequence similarity (evaluated via BLAST, FASTA, or HMM profile alignments) provides an important foundation informing functional transfer across homologous proteins. Conserved domain architectures and active-site residues frequently provide strong initial evidence for shared canonical enzymatic mechanisms.

However, historical analysis ([`docs/roadmap/core/experiment_definition.md` (§Research Framework, L66–L95)](../roadmap/core/experiment_definition.md)) highlights an essential scientific qualification:
- **Incomplete Context from Sequence Similarity Alone**: Sequence similarity can inform functional transfer, but it does not, by itself, establish conservation of every moonlighting function or its specific biological context.
- **Diverse Structural and Regulatory Determinants**: Moonlighting functions often depend on features whose evolutionary conservation does not strictly parallel overall catalytic sequence conservation, including:
  - Surface interaction patches, peripheral binding motifs, or disordered regions that diverge rapidly across orthologs without affecting primary catalytic domains.
  - Quaternary assembly dynamics, oligomeric transitions, or conditional allosteric switches.
  - Lineage-specific protein-protein interactions, differential subcellular targeting signals, or post-translational modification sites.
- **Consequences for Automated Annotation**: Uncritical functional transfer based strictly on sequence similarity can lead to both false positive assertions (propagating a lineage-specific moonlighting function to homologs where the interaction interface is absent) and false negative omissions (failing to recognize newly evolved secondary functions in well-known enzyme scaffolds). Dedicated experimental evidence and primary literature curation remain necessary to establish whether a moonlighting capability is conserved across species.

### 5.2 Annotation Lag and Verification Gaps
Secondary moonlighting functions documented in biochemical literature often experience decades of **annotation lag** before appearing in structured ontology databases. Relying solely on automated GO annotations or sequence similarity systematically underestimates non-canonical multifunctionality, necessitating dedicated literature curation.

---

## 6. Limits and Methodological Interpretation of Computational Scores

### 6.1 What Semantic Distance and Association Metrics Measure
Computational metrics defined in historical proposals ([`docs/roadmap/04_especificacion_metricas.md`](../roadmap/04_especificacion_metricas.md)) quantify mathematical properties on structured graphs or corpus frequency distributions:
- **Topological Graph Distances (e.g. 1 − Wang)**: Measure the ancestral graph overlap and edge weighting between terms on the directed acyclic graph (DAG).
- **Information-Theoretic Dissimilarities (e.g. 1 − Lin)**: Measure the ratio of shared ancestral information content (MICA) against the individual term information contents within an annotation corpus.
- **Structural Path Distances (e.g. Minimum Branch Length, MBL)**: Measure the shortest path length between term nodes in the ontology hierarchy.
- **Statistical Associations (e.g. NPMI)**: Measure normalized co-occurrence deviations from independent marginal probabilities across a defined database snapshot.

### 6.2 Explicit Negative Boundaries: What Computational Scores Cannot Demonstrate
To protect scientific integrity, historical dossier [`docs/roadmap/01_dossier_experimento.md` (§10, L299–L313)](../roadmap/01_dossier_experimento.md) establishes ten explicit methodological limits that must be observed across all research activities:

1. **Scores Do Not Prove Biological Reality**: A high semantic dissimilarity score (e.g. $1 - \text{Wang} \approx 0.95$) describes topological divergence between annotated terms; it does **not** prove physiological multifunctionality or moonlighting mechanism.
2. **Missing Scores Do Not Prove Monofunctionality**: An uncalculated metric, low annotation density, or lack of accessible literature does **not** prove that a protein is monofunctional.
3. **Source Concepts Are Not Homogeneous**: Different upstream sources employ divergent biological definitions (e.g. MoonProt focuses on experimental moonlighting, while MultitaskProtDB-II incorporates diverse multitask models); positive inclusion across sources does not mean they represent the identical biological phenomenon.
4. **Annotation Multiplicity Does Not Equal Functional Multiplicity**: Multiple annotations or multiple PMIDs do not inherently prove distinct physiological functions; they may represent redundant descriptions of a single activity or repeated re-curations of the same original experiment.
5. **Cross-Aspect Co-Annotation Does Not Prove Spatiotemporal Execution**: Co-annotation between MF and CC does not demonstrate localization, simultaneity, or causality.
6. **Static Code Reading Does Not Prove Execution Equivalence**: Static verification of code and schema invariants does not certify execution results in unexecuted runtime environments.
7. **Revising Source References Is Not Independent Corroboration**: Reviewing the exact primary paper cited by an upstream source validates extraction fidelity and claim provenance; it does not constitute independent scientific replication.
8. **Discordant Cases Do Not Predict Population Prevalence**: Targeted analysis of discordant edge cases does not allow unbiased extrapolation of error rates across the entire protein population.
9. **Scores Do Not Establish Classification Discriminability**: In the absence of an empirically validated negative control cohort, computational metric distributions cannot claim to discriminate positive from negative multifunctionality classes.
10. **Exploratory Statistical Profiles Are Not Governing Benchmarks**: Analytical profiles constructed for descriptive evaluation do not automatically constitute standardized benchmarks for machine learning classification.

---

## 7. Role and Methodological Limitations of the BioData Reference Population

### 7.1 Study-Specific Role of the Available Reference Population
In the historical experimental framework ([`docs/roadmap/02_protocolo_cientifico_y_analisis.md` (§3, L94–L109)](../roadmap/02_protocolo_cientifico_y_analisis.md) and [`docs/roadmap/core/experiment_definition.md` (§Resource Baseline, L147–L178)](../roadmap/core/experiment_definition.md)), an external dataset/database referred to as **`BioData`** (derived from UniProtKB and QuickGO extracts) was utilized to provide an empirical background population.

In this context, the reference population serves specific, bounded computational roles:
- Providing background term frequencies $n(t)$ and corpus size $N$ to calculate term Information Content ($IC(t) = -\ln(n(t)/N)$).
- Providing background pair frequencies to compute marginal probabilities for statistical cross-aspect associations (NPMI).
- Providing a broader distribution of single-protein annotation breadths against which the attributed positive cohort can be descriptively contrasted.

### 7.2 Methodological Limitation: Not a Validated Negative Control Cohort
A paramount operational and scientific constraint governed by [`AGENTS.md`](../../AGENTS.md) Section 1.2 is:
> **BioData is a contextual reference population, NEVER a verified negative class.**

For the purposes of this experiment and repository baseline:
- **Unvalidated Status**: The available `BioData` reference population has **not** been biologically screened, experimentally verified, or curatively adjudicated as a true "Non-Multifunctional Protein" (NMF) negative control set.
- **The Open-World Fallacy**: Because Gene Ontology operates under the Open-World Assumption, treating unannotated or sparsely annotated proteins in `BioData` as "confirmed negative" monofunctional controls commits the fundamental logical error of equating *absence of evidence* with *evidence of absence*.
- **Scope of Limitation**: This statement represents a **study-specific methodological limitation of the available reference dataset**, reflecting the fact that no verified negative class was constructed or validated for this baseline. It does **not** assert a permanent theoretical impossibility or prohibit future, rigorously designed scientific investigations from developing validated negative-control cohorts through established biological and experimental criteria.

---

## 8. Epistemic Inventory: Separation of Invariants, Explanations, Hypotheses, and Open Decisions

To prevent confusion with the formal document authority hierarchy defined in [`AGENTS.md`](../../AGENTS.md) Section 2, concepts in this document are categorized into **named epistemic categories**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CATEGORIZED EPISTEMIC INVENTORY                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY: ESTABLISHED REPOSITORY INVARIANTS (Normative Rules)                   │
│   • Raw data immutability and cryptographic manifest binding (ADR-002).         │
│   • Deterministic entity resolution via canonical UniProtKB (ADR-005).          │
│   • Decoupling bibliographic relations from baseline catalog v1 (ADR-007).      │
│   • Prohibition against synthesizing Cartesian triplets (AGENTS.md).           │
│   • BioData reference population is never a verified negative class (AGENTS.md).│
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY: RECOVERED METHODOLOGICAL EXPLANATIONS (Advisory Foundations)          │
│   • Separation of attribution claims from locally verified truth (01_dossier).  │
│   • Conceptual separation: annotation breadth vs multifunctionality vs moon-    │
│     lighting as a diverse mechanistic category (01_dossier, exp_definition).    │
│   • Distinction between imported GO NOT and experimental negative/null outcomes.│
│   • Independent standard GO annotations vs explicit extensions / GO-CAM.       │
│   • Three conceptual evidence layers vs three repository data products.         │
│   • The 10 explicit negative statements on what scores cannot prove (01_dossier)│
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY: HISTORICAL WORKING HYPOTHESES (Unproven Scientific Proposals)         │
│   • H1: Coverage and composition explain observed multi-source divergence.      │
│   • H2: Evidence sensitivity is partly driven by term count reduction.          │
│   • H3: Topological, semantic, and embedding distances provide complementary    │
│     curation triage signals.                                                    │
│   • H4: Low-frequency cross-aspect associations indicate candidate moonlighting.│
│   • Unadopted hypothesis: universal active-site physical distance criteria.     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY: OPEN GOVERNANCE & SCIENTIFIC DECISIONS (Pending Approval)             │
│   • Gate G0: Formal adoption of master research proposal PEC-EXP-001 v0.2.1.    │
│   • Gate G1: Boundary decision on in-repo vs downstream metric computation.     │
│   • Gate G2: Adoption of literature curation manual as normative standard.      │
│   • Gate G4: Authorization to quarantine the verified mojibake duplicate.       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Compact Section-Level Provenance and Traceability

The following table records the precise documentary origins of the concepts synthesized in this document, linking each concept to its source heading and line range in the inspected baseline:

| Section in this Document | Synthesized Scientific Topic | Primary Source Document & Exact Heading | Snapshot Line Range | Epistemic Classification | Claims / Definitions Needing Subsequent Primary-Source Verification |
|---|---|---|---|---|---|
| **§1.1** | Source attribution vs locally confirmed truth | [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) <br> `## 1. Resumen y continuidad` | L40–L51 | Recovered Methodological Explanation | None (Core epistemic governance rule). |
| **§1.2** | Open-world assumption & `NOT` qualifiers vs experimental null results | [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) <br> `## 3. Contexto y modelo conceptual` | L109–L110 | Recovered Methodological Explanation | Adjudication criteria for converting literature negative results into curatorial statements. |
| **§2.1** | Breadth vs multifunctionality vs moonlighting (diverse mechanisms) | [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) <br> `### 3.2. Tres conceptos...` | L103–L110 | Recovered Methodological Explanation | Operational biological criteria distinguishing moonlighting from other classes of multifunctionality require primary literature validation in Phase D0. |
| **§3.1–3.2** | Independent annotations & Cartesian triplet ban; explicit context in extensions / GO-CAM | [`docs/roadmap/02_protocolo_cientifico_y_analisis.md`](../roadmap/02_protocolo_cientifico_y_analisis.md) <br> `## 1. Responsabilidad documental...` | L43–L64 | Established Invariant (AGENTS.md) | None (Codified bioinformatic invariant). |
| **§3.3** | Cross-aspect NPMI associations & limits | [`docs/roadmap/04a_asociaciones_interaspecto.md`](../roadmap/04a_asociaciones_interaspecto.md) <br> `## 2–3. Fichas de las tres métricas` | L25–L85 | Historical Proposal | Statistical significance thresholds for NPMI co-occurrence rarity require empirical evaluation. |
| **§4.1** | Three layers of evidence | [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) <br> `### 3.3. Tres capas de evidencia` | L111–L120 | Recovered Methodological Explanation | None (Conceptual evidence framework). |
| **§4.2** | Decoupling evidence layers from data products | [`docs/roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md`](../roadmap/bounded-evolution-proposal-documentation-and-bibliographic-evidence.md) <br> `## Section D` | L215–L311 | Established Architecture (Amended Proposal) | None (Architectural model ratified in amendment). |
| **§5.1–5.2** | Sequence similarity and qualified functional transfer | [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) <br> `## Research Framework` | L66–L95 | Recovered Methodological Explanation | Structural mechanisms of non-homologous functional divergence require experimental verification per protein family. |
| **§6.1–6.2** | 10 explicit negative limits on computational scores | [`docs/roadmap/01_dossier_experimento.md`](../roadmap/01_dossier_experimento.md) <br> `## 10. Qué este estudio no puede demostrar` | L299–L313 | Recovered Methodological Explanation | Mathematical equivalence of specific third-party library implementations (CBBIO, GOSemSim) requires code verification. |
| **§7.1–7.2** | BioData reference population role & study-specific limitations | [`docs/roadmap/02_protocolo_cientifico_y_analisis.md`](../roadmap/02_protocolo_cientifico_y_analisis.md) <br> `## 3. Poblaciones, conjuntos e independencia` | L94–L109 | Study-Specific Limitation (AGENTS.md) | Verification of exact background frequency distributions across UniProt releases. |
| **§8** | Epistemic inventory & named category separation | [`docs/roadmap/core/experiment_definition.md`](../roadmap/core/experiment_definition.md) <br> `### Working Hypotheses` | L83–L95 | Historical Working Hypotheses | Formal testing of hypotheses H1–H6 depends on Gate G0 scientific authorization. |

---
*End of Scientific Background and Methodological Foundations (`DOC-ARCH-SCIENTIFIC-BACKGROUND-V1`).*
