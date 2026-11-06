# Protein Multifunctionality â€” Experimental Design Proposal

> Documento maestro de trabajo para definir, revisar y presentar la propuesta del proyecto.

| Document control | Valor |
|---|---|
| Document ID | PEC-EXP-001 |
| Version | 0.1.0 |
| Status | Draft for team review â€” no aprobado para full-scale execution |
| Date | 2026-10-27 |
| Language | Castellano; terminologÃ­a tÃ©cnica en inglÃ©s |
| Intended audience | Research team, data engineering, software engineering y scientific reviewers |
| Purpose | Acordar scientific scope, data contracts, experimental blocks, deliverables y decision gates |
| Execution status | Propuesta de diseÃ±o; no contiene resultados experimentales ni estimaciones de coste verificadas |

## Executive Overview

Se propone un estudio de **functional characterization y dataset curation** organizado en seis experimental blocks. El diseÃ±o separa la preparaciÃ³n de datos, la sensibilidad a la evidencia, la divergencia entre funciones, la asociaciÃ³n entre funciÃ³n y compartimento, la comparaciÃ³n con una reference population y la revisiÃ³n biolÃ³gica final.

El principio arquitectÃ³nico es **PIS for data acquisition and persistence â†’ CBBIO Python API for data access and reusable calculations â†’ experimental project for comparisons and interpretation**. Esta separaciÃ³n se apoya en las responsabilidades documentadas de [PIS](https://github.com/CBBIO/protein-information-system/blob/main/README.md), del [BioData client](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md) y de las [GO utilities](https://github.com/CBBIO/BioData/blob/main/docs/GO.md).

**BioData** serÃ¡ la reference population y **TargetData** la cohort de proteÃ­nas multifuncionales que se caracterizarÃ¡ y curarÃ¡. Esta funciÃ³n de TargetData procede del planteamiento del proyecto: no implica que ya se hayan verificado su tamaÃ±o, cobertura, esquema o despliegue. BioData no se considerarÃ¡ un conjunto de verified negative samples.

Los **GeOKG-GO embeddings** se incorporan al B3 para estudiar term-level divergence y al B5 para evaluar metric complementarity y, cuando exista una agregaciÃ³n vÃ¡lida, protein-level comparison. Las visualizaciones **PCA 3D** y **UMAP 3D** quedan como extensiones posteriores a los seis bloques.

**Regla de inicio:** aprobar el protocolo y sus dependencias antes de comenzar el trabajo experimental. La aprobaciÃ³n del diseÃ±o no exige implementar todo a la vez: permite un technical pilot y una ejecuciÃ³n progresiva bajo change control.

## Document Usage

Este archivo es la fuente editable de la propuesta y la base narrativa para preparar un slide deck. No es todavÃ­a un executable protocol, una especificaciÃ³n de API aprobada ni una presentaciÃ³n de resultados.

- **Verified capability:** capacidad identificada en documentaciÃ³n o cÃ³digo enlazado; no equivale a disponibilidad comprobada en el deployment del laboratorio.
- **Project assumption:** recurso o condiciÃ³n prevista por el equipo, pendiente de comprobaciÃ³n operativa.
- **Proposed decision:** elecciÃ³n metodolÃ³gica propuesta para revisiÃ³n; no debe presentarse como una decisiÃ³n ya aprobada.
- **Open decision:** definiciÃ³n que bloquea un decision gate concreto hasta quedar resuelta.
- **Future extension:** funcionalidad fuera del core scope inicial.

Para modificar el documento, conservar los identifiers de blocks, research questions, deliverables y decisions. Registrar los cambios que afecten a interpretaciÃ³n, cohort, mÃ©tricas o scope en el Decision Register y en el Change Log. Los cambios editoriales no requieren un nuevo experimental run; los cambios metodolÃ³gicos posteriores al protocol freeze sÃ­ deben producir una versiÃ³n identificable.

## Contents

- [Research Framework](#research-framework)
- [Scope and Boundaries](#scope-and-boundaries)
- [Terminology](#terminology)
- [Resource Baseline](#resource-baseline)
- [Data Contracts](#data-contracts)
- [Experimental Architecture](#experimental-architecture)
- [B1 â€” Corpus and Evidence](#b1--corpus-and-evidence)
- [B2 â€” Evidence Sensitivity](#b2--evidence-sensitivity)
- [B3 â€” MFâ€“MF Divergence](#b3--mfmf-divergence)
- [B4 â€” MFâ€“CC Association](#b4--mfcc-association)
- [B5 â€” Reference and Complementarity](#b5--reference-and-complementarity)
- [B6 â€” Curation and Interpretation](#b6--curation-and-interpretation)
- [E1 â€” PCA 3D](#e1--pca-3d)
- [E2 â€” UMAP 3D](#e2--umap-3d)
- [Statistical Analysis Plan](#statistical-analysis-plan)
- [Software Responsibility Map](#software-responsibility-map)
- [Reproducibility and Execution](#reproducibility-and-execution)
- [Delivery and Approval](#delivery-and-approval)
- [Decision Register](#decision-register)
- [Risk Register](#risk-register)
- [Slide Deck Storyboard](#slide-deck-storyboard)
- [Review Checklist](#review-checklist)
- [Change Log](#change-log)

## Research Framework

### Central Research Question

> Â¿CÃ³mo se caracteriza la functional diversity de las proteÃ­nas de TargetData, hasta quÃ© punto depende de las anotaciones disponibles y quÃ© informaciÃ³n adicional aportan distintas mÃ©tricas para orientar su curation?

### Scientific Objectives

| ID | Objective | Evidencia prevista |
|---|---|---|
| O1 | Definir una cohort trazable y analizable | Coverage report, identity mapping y exclusion log |
| O2 | Cuantificar sensitivity a las evidence policies | Paired comparisons y annotation-count controls |
| O3 | Caracterizar intra-protein GO-MF divergence | Semantic, topological y embedding-based descriptors |
| O4 | Contextualizar GO-MFâ€“GO-CC co-annotation | Reference association profile y support counts |
| O5 | Evaluar posicionamiento y metric complementarity | Reference comparisons y discordance analysis |
| O6 | Producir decisiones de curation auditables | Evidence records, reviewer decisions y versioned TargetData |

### Working Hypotheses

Estas hipÃ³tesis son contrastables, pero no presuponen diferencias significativas ni una direcciÃ³n favorable a una mÃ©trica concreta.

| ID | Working hypothesis | Block |
|---|---|---|
| H1 | Coverage y corpus composition pueden explicar parte de las diferencias observadas | B1, B5 |
| H2 | Parte de la evidence sensitivity puede deberse a la reducciÃ³n del nÃºmero de tÃ©rminos | B2 |
| H3 | Las representaciones topolÃ³gicas, semÃ¡nticas y GeOKG-GO pueden aportar informaciÃ³n parcialmente complementaria | B3, B5 |
| H4 | Las asociaciones GO-MFâ€“GO-CC poco frecuentes pueden priorizar revisiÃ³n, siempre que exista soporte suficiente | B4, B6 |
| H5 | Algunas diferencias TargetDataâ€“reference pueden persistir tras controlar annotation density y otros confounders | B5 |
| H6 | Las discordancias entre mÃ©tricas y evidencia pueden orientar curation sin constituir una etiqueta biolÃ³gica automÃ¡tica | B6 |

## Scope and Boundaries

### Core Scope

| Included | Expected output |
|---|---|
| Characterization de TargetData con BioData como referencia | Cohort y reference profiles congelados |
| Evidence sensitivity y coverage analysis | Resultados comparables entre annotation policies |
| Intra-protein GO-MFâ€“GO-MF analysis | Descriptors de divergence y term pairs trazables |
| GO-MFâ€“GO-CC co-annotation analysis | Association profiles con soporte explÃ­cito |
| GeOKG-GO en B3 y B5 | Distancias o dissimilarities con contrato geomÃ©trico documentado |
| Reference comparison y metric complementarity | AnÃ¡lisis de redundancia y casos discordantes |
| Evidence-based curation | TargetData versionado y decision log |

### Out of Scope

- Entrenar un nuevo multifunctionality classifier o hacer un benchmark exhaustivo de modelos.
- Interpretar un descriptor elevado como demostraciÃ³n automÃ¡tica de multifunctionality o moonlighting.
- Realizar wet-lab validation.
- Reentrenar GeOKG como requisito inicial.
- RediseÃ±ar PIS o crear un nuevo HTTP service.
- Convertir PCA o UMAP en pruebas confirmatorias de biological separation.
- Implementar de entrada una plataforma de hyperparameter tuning o experimentaciÃ³n masiva.

### Future PEC Integration

El [README de PEC](https://github.com/alexdorocode/protein-embedding-classifier/blob/master/README.md) documenta componentes de dataset construction, training, prediction y experiment orchestration. La propuesta es que PEC consuma posteriormente los datasets y descriptors validados, sin convertir el estudio actual en un training experiment. PEC utiliza los experimental roles **TP (Target Protein)** y **NTP (Non-Target Protein)**; esos roles no se reinterpretarÃ¡n automÃ¡ticamente como multifunctional/non-multifunctional biological labels. [PEC terminology](https://github.com/alexdorocode/protein-embedding-classifier/blob/master/README.md)

Las futuras comparaciones de Target/Non-Target ratios requerirÃ¡n un protocolo separado: definiciÃ³n de labels, selecciÃ³n de samples, homology-aware splits, model selection y evaluaciÃ³n. Ni BioData ni un rol Non-Target deberÃ¡n equipararse automÃ¡ticamente a ausencia biolÃ³gica de multifunctionality.

## Terminology

| Term | Uso en el documento |
|---|---|
| Protein multifunctionality | Propiedad biolÃ³gica bajo estudio; no equivale al nÃºmero de anotaciones GO |
| Moonlighting | Concepto que requiere una definiciÃ³n biolÃ³gica explÃ­cita; no se tratarÃ¡ como sinÃ³nimo automÃ¡tico de toda multifunctionality |
| GO-MF | Aspect Molecular Function de Gene Ontology |
| GO-CC | Aspect Cellular Component de Gene Ontology |
| MFâ€“MF | ComparaciÃ³n entre tÃ©rminos GO-MF dentro de una proteÃ­na, salvo indicaciÃ³n explÃ­cita |
| MFâ€“CC | AsociaciÃ³n estadÃ­stica entre tÃ©rminos GO-MF y GO-CC coanotados |
| TargetData | Cohort objetivo a caracterizar y curar |
| BioData | Nombre del reference dataset/database; tambiÃ©n aparece en el nombre del repositorio CBBIO/BioData |
| CBBIO Python API | Interfaz de biblioteca para consultar datos y reutilizar cÃ¡lculos; no se presupone una REST API |
| Snapshot | VersiÃ³n inmutable e identificable de datos o artefactos |
| Evidence policy | Regla versionada que selecciona anotaciones elegibles |
| Information Content, IC | Descriptor ontolÃ³gico dependiente de un annotation corpus; no confundir con el evidence code IC |
| Descriptor / score | Resultado numÃ©rico; no presupone propiedades matemÃ¡ticas de distance |
| Reference population | PoblaciÃ³n de contextualizaciÃ³n, no un conjunto de verified negatives |
| Coverage | FracciÃ³n de entidades o pares con datos elegibles para un anÃ¡lisis |
| Decision gate | RevisiÃ³n con criterios explÃ­citos para continuar, condicionar o detener una fase |

## Resource Baseline

### Available and Expected Resources

| Resource | Evidence status | Uso previsto | VerificaciÃ³n necesaria |
|---|---|---|---|
| PIS | Verified capability documental | Data acquisition y persistence | Deployment, access y fuentes habilitadas |
| BioData reference snapshot | Project assumption de disponibilidad | IC, co-occurrence y contextualizaciÃ³n | VersiÃ³n, tamaÃ±o real, contenido y overlap |
| TargetData initial snapshot | Project assumption definida por el proyecto | Cohort principal | Identidad, fuentes, coverage y estado de curation |
| CBBIO data access | Verified capability documental | Consultas batch de secuencias, taxonomÃ­a, GO y embeddings | Version compatibility y acceso efectivo a ambos datasets |
| CBBIO GO utilities | Verified capability documental | DAG navigation, semantic similarity y MBL | Comportamiento, parametrizaciÃ³n y tests |
| GeOKG-GO artifact | Recurso previsto por el proyecto | Term embeddings en B3 y B5 | Checkpoint, mapping, geometrÃ­a y cobertura |
| Sequence embeddings | Acceso soportado; disponibilidad concreta no verificada | E1 y E2 | Model, layer, pooling y sequence mapping |
| Scientific references | Disponibilidad pendiente de auditorÃ­a | B6 | PreservaciÃ³n de PMID/DOI y evidencia original |

PIS documenta extracciÃ³n desde UniProt, PDB y GOA y la restauraciÃ³n de BioData desde backups publicados; no se infiere que una instalaciÃ³n concreta contenga ya todo lo necesario. [PIS documentation](https://github.com/CBBIO/protein-information-system/blob/main/README.md)

El client de CBBIO documenta retrieval batch de secuencias, taxonomÃ­a, GO annotations y embeddings, asÃ­ como consultas de disponibilidad de modelos y capas. [BioData API](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md)

Las GO utilities documentan MBL, Wang, Resnik, Lin, Schlicker y group similarity mediante Best Match Average, ademÃ¡s de la preparaciÃ³n del corpus para IC. [GO API](https://github.com/CBBIO/BioData/blob/main/docs/GO.md)

**DistinciÃ³n de implementaciÃ³n:** `CBBIO.BioData` es el PostgreSQL client; `CBBIO.GO` opera sobre OBO files y annotation mappings y puede trabajar sin conexiÃ³n a la base de datos. La referencia a Â«APIÂ» en el diseÃ±o engloba estas interfaces de biblioteca: extraer vÃ­a client y calcular sobre un snapshot local no implica aÃ±adir carga SQL a cada cÃ¡lculo GO. [BioData client](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md) [GO utilities](https://github.com/CBBIO/BioData/blob/main/docs/GO.md)

La revisiÃ³n documental de esta versiÃ³n se ha contrastado con los archivos enlazados. No sustituye un integration test del deployment, una auditorÃ­a completa del repositorio ni el acceso a las bases de datos. Los enlaces a branches son navegables pero mutables; la versiÃ³n aprobada del protocolo deberÃ¡ registrar commits y snapshots inmutables antes de ejecutar.


### Data Preservation Gap

El modelo `ProteinGOTermAnnotation` inspeccionado contiene `protein_id`, `go_id` y `evidence_code`, con una restricciÃ³n de unicidad por pareja proteÃ­naâ€“tÃ©rmino. En ese modelo no se observan campos para bibliographic references o qualifiers. Esta observaciÃ³n estÃ¡ acotada al archivo revisado y no demuestra ausencia en todas las tablas del deployment. [PIS annotation model](https://github.com/CBBIO/protein-information-system/blob/main/protein_information_system/sql/model/entities/go_annotation/go_annotation.py)

**Consecuencia propuesta:** auditar si se preservan mÃºltiples evidencias y referencias para una misma pareja. Un Ãºnico evidence code retenido puede limitar la reconstrucciÃ³n de evidence policies. Si la informaciÃ³n se perdiÃ³ en ingestion, una extensiÃ³n del retrieval API no puede reconstruirla por sÃ­ sola.

## Data Contracts

### Dataset Identity

Se propone separar explÃ­citamente:

- `TargetData_initial`: snapshot congelado para los anÃ¡lisis principales.
- `TargetData_curated`: versiÃ³n derivada despuÃ©s de B6, con cada cambio justificado.
- `BioData_reference`: snapshot utilizado como reference population.
- `Reference_profile`: artefacto derivado de BioData para IC o co-occurrence, con su propia configuraciÃ³n y fingerprint.

TargetData no presupone un schema idÃ©ntico al de BioData. La compatibilidad del client se probarÃ¡ antes de comprometer acceso directo; si hace falta, se definirÃ¡ un adapter fino y trazable, evitando duplicar la lÃ³gica de anÃ¡lisis.

### Minimum Analysis Record

| Field group | Campos propuestos | Requirement |
|---|---|---|
| Identity | `protein_id`, `source_id`, `accessions`, `source_dataset` | Obligatorio para trazabilidad |
| Sequence identity | `sequence_id`, `sequence_hash`, `isoform_policy`, `sequence_length` | Obligatorio cuando se utilicen secuencias o embeddings |
| Taxonomy | `taxonomy_id`, `species` | Necesario para estratificaciÃ³n y controles |
| GO assertion | `go_id`, `go_aspect`, `evidence_code`, `qualifier`, `annotation_source` | Necesario para evidence policies completas |
| Evidence provenance | `reference_ids`, `annotation_date`, `source_release` | Necesario para revisiÃ³n de evidencia; si falta, declarar la limitaciÃ³n |
| Biological curation | `biological_label`, `evidence_level`, `curation_status` | Separado de los experimental roles |
| Experimental role | `cohort_role`, `analysis_eligibility`, `exclusion_reason` | Necesario para reconstruir cada anÃ¡lisis |

Este contrato es una **especificaciÃ³n propuesta**, no una afirmaciÃ³n de que todos los campos existan actualmente.

### GO Processing Policy

Antes de G2 deben fijarse el GO release, los namespaces, las allowed relations, la polÃ­tica de propagation, el tratamiento de obsolete terms/alternative IDs y los filtros de raÃ­ces y calificadores.

Como baseline propuesto, la diversidad intraproteÃ­na se calcularÃ¡ sobre unique eligible asserted terms, sin aÃ±adir automÃ¡ticamente todos los ancestros a la lista de pares. La propagation para IC se tratarÃ¡ por separado y se verificarÃ¡ frente al comportamiento de la biblioteca. Una non-redundant term policy, que suprima redundancia ancestroâ€“descendiente bajo reglas definidas, podrÃ¡ evaluarse como sensitivity analysis sin sustituir silenciosamente el baseline.

Las anotaciones `NOT` no se tratarÃ¡n como positive assertions. Cuando no se conserven qualifiers, el alcance de esta garantÃ­a quedarÃ¡ condicionado a la procedencia y al filtrado upstream. Los cÃ³digos `ND` y `UNKNOWN` se contabilizarÃ¡n en coverage, pero no se aceptarÃ¡n sin mÃ¡s como evidencia positiva especÃ­fica.

### Missingness and Calculation Status

| Status | Significado |
|---|---|
| `ok` | CÃ¡lculo definido y completado |
| `insufficient_terms` | No hay suficientes tÃ©rminos elegibles |
| `missing_annotation` | No hay anotaciones requeridas |
| `missing_embedding` | Falta representaciÃ³n para una entidad o tÃ©rmino |
| `low_support` | Association estimate sin el soporte mÃ­nimo aprobado |
| `unobserved_pair` | Pareja no observada en el reference corpus |
| `unsupported_geometry` | No se ha definido una distancia vÃ¡lida para el artefacto |
| `calculation_error` | Fallo tÃ©cnico o numÃ©rico |

Un resultado no calculable se almacenarÃ¡ como valor ausente acompaÃ±ado de `status`, nunca como cero por defecto. Un cero vÃ¡lido debe poder distinguirse de un error o de falta de datos.

## Experimental Architecture

### Block Map

| Block | Research question | Main deliverable | Downstream use |
|---|---|---|---|
| B1 | Â¿QuÃ© entidades y evidencias son analizables? | D1 â€” Frozen cohort and coverage | Todos los bloques |
| B2 | Â¿CuÃ¡nto dependen los resultados de la evidence policy? | D2 â€” Evidence sensitivity report | InterpretaciÃ³n de B3â€“B5 |
| B3 | Â¿QuÃ© divergencia existe entre GO-MF terms? | D3 â€” Intra-protein divergence table | B5 y B6 |
| B4 | Â¿QuÃ© asociaciones GO-MFâ€“GO-CC son habituales? | D4 â€” Association reference profile | B5 y B6 |
| B5 | Â¿QuÃ© es particular de TargetData y quÃ© aporta cada descriptor? | D5 â€” Reference and complementarity report | B6 |
| B6 | Â¿QuÃ© conclusiones y decisiones de curation tienen soporte? | D6 â€” Curated TargetData and evidence log | Release y futuras fases |

### Dependency Diagram

```mermaid
flowchart TD
    PIS["PIS: acquisition and persistence"] --> REF["BioData reference snapshot"]
    PIS --> TARGET["TargetData initial snapshot"]
    REF --> API["CBBIO Python API"]
    TARGET --> API
    API --> B1["B1: Corpus and Evidence"]
    B1 --> POLICY["B2: Evidence policy specification"]
    POLICY --> B3["B3: MF-MF Divergence"]
    POLICY --> B4["B4: MF-CC Association"]
    GEO["GeOKG-GO artifact"] --> B3
    B3 --> SENS["B2: Sensitivity comparisons"]
    B4 --> SENS
    B3 --> B5["B5: Reference and Complementarity"]
    B4 --> B5
    SENS --> B5
    GEO --> B5
    B5 --> B6["B6: Curation and Interpretation"]
    B6 --> PCA["E1: PCA 3D"]
    B6 --> UMAP["E2: UMAP 3D"]
    SEQ["Sequence embeddings"] --> PCA
    SEQ --> UMAP
```

**Lectura sin Mermaid:** B1 fija la cohort; B2 especifica las policies; B3 y B4 producen los descriptors; B2 completa sus sensitivity comparisons; B5 integra y contextualiza; B6 revisa la evidencia. E1 y E2 consumen los resultados finales. Las extensiones se entregan despuÃ©s del core study, aunque su preparaciÃ³n tÃ©cnica pueda adelantarse bajo aprobaciÃ³n explÃ­cita.

## B1 â€” Corpus and Evidence

### Purpose and Questions

**Purpose:** establecer quÃ© entra al estudio y con quÃ© limitaciones.

- **RQ1.1:** Â¿QuÃ© entidades Ãºnicas contiene TargetData despuÃ©s de resolver identifiers y duplicados?
- **RQ1.2:** Â¿QuÃ© coverage existe para sequence, taxonomy, GO, evidence provenance y embeddings?
- **RQ1.3:** Â¿QuÃ© overlap hay con BioData por accession y por sequence identity?
- **RQ1.4:** Â¿CÃ³mo se distribuyen especies, longitudes, fuentes y annotation counts?

### Resource Stratification

| Layer | Contenido |
|---|---|
| Upstream inputs | TargetData inicial, BioData, source identifiers y provenance |
| Existing capability | Retrieval batch mediante CBBIO; acceso a modelos y capas disponibles |
| Required additions | Identity rules, eligibility policy, source mapping y contratos de campos |
| Resources produced | Frozen cohort, coverage matrix, overlap report y exclusion log |
| Downstream consumers | B2â€“B6; selecciÃ³n del technical pilot; E1/E2 cuando proceda |

Las capacidades de retrieval reutilizables estÃ¡n documentadas en la [BioData API](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md).

### Analysis Plan

1. Resolver source identifiers sin fusionar automÃ¡ticamente proteÃ­nas, isoformas y secuencias.
2. Detectar exact duplicates y documentar la regla de canonicalization.
3. Medir coverage por fuente y organismo; conservar ausencias y ambigÃ¼edades.
4. Definir analysis eligibility por bloque, sin exigir embeddings a quien solo participe en GO analysis.
5. Congelar la cohort y registrar los exclusion reasons.

### Outputs and Exit Criteria

**D1:** manifest, identity mapping, coverage matrix, overlap report y exclusion log.

**Exit criterion:** cada registro tiene identidad resuelta o estado explÃ­cito de ambiguity/exclusion; cada bloque dispone de un denominator reproducible.

**Presentation asset:** cohort flow diagram y coverage heatmap. **Interpretation boundary:** alta coverage no demuestra calidad biolÃ³gica, y baja coverage no demuestra ausencia de funciÃ³n.

## B2 â€” Evidence Sensitivity

### Purpose and Questions

**Purpose:** separar el efecto de la evidence selection del efecto del nÃºmero de tÃ©rminos disponibles.

- **RQ2.1:** Â¿CuÃ¡ntas anotaciones y proteÃ­nas elegibles se retienen con cada policy?
- **RQ2.2:** Â¿CÃ³mo cambian los descriptors de B3 y B4 dentro de la misma proteÃ­na?
- **RQ2.3:** Â¿Los cambios exceden los observados al igualar annotation counts?
- **RQ2.4:** Â¿QuÃ© conclusiones son estables y cuÃ¡les dependen del filtrado?

### Resource Stratification

| Layer | Contenido |
|---|---|
| Upstream inputs | D1, GO snapshot y evidence codes/provenance |
| Existing capability | GO annotation retrieval y GO calculations |
| Required additions | Versioned policy selector y downsampling control si no estÃ¡n cubiertos |
| Resources produced | Evidence policies, retention table y sensitivity results |
| Downstream consumers | B3/B4 para ejecuciÃ³n bajo policies; B5/B6 para interpretaciÃ³n |

### Proposed Evidence Policies

| Policy ID | Eligible evidence codes | Uso |
|---|---|---|
| `ALL_ELIGIBLE` | Todos los cÃ³digos admisibles tras GO processing y qualifier policy | Baseline de coverage |
| `EXP_CONVENTIONAL` | EXP, IDA, IPI, IMP, IGI, IEP | Subconjunto experimental convencional |
| `EXP_EXTENDED` | Los anteriores mÃ¡s HTP, HDA, HMP, HGI, HEP | Sensibilidad a high-throughput evidence |

La guÃ­a de GO separa experimental evidence, high-throughput evidence, author statements y curator statements. TAS no se incluirÃ¡ como experimental evidence; el evidence code IC tampoco. Estos cÃ³digos clasifican el soporte de una anotaciÃ³n, no constituyen una escala universal de calidad. [GO evidence-code guide](https://geneontology.org/docs/guide-go-evidence-codes/)

### Analysis Plan

1. Especificar policies antes de calcular B3/B4.
2. Retener el mismo GO snapshot y los mismos reference profiles en la comparaciÃ³n principal.
3. Comparar descriptors de forma paired en proteÃ­nas calculables bajo ambas policies.
4. Informar tambiÃ©n de las proteÃ­nas que dejan de ser calculables; no limitar el reporte a complete cases.
5. Aplicar repeated downsampling de `ALL_ELIGIBLE` al nÃºmero de tÃ©rminos de la policy comparada, con seeds y repetitions fijadas antes de ejecuciÃ³n.
6. Separar el anÃ¡lisis anterior de una sensibilidad adicional que reconstruya los reference profiles por evidence policy.

La unicidad proteÃ­naâ€“tÃ©rmino del modelo PIS revisado obliga a comprobar si mÃºltiples evidencias por assertion se preservan en otra capa antes de interpretar estas policies como completas. [PIS annotation model](https://github.com/CBBIO/protein-information-system/blob/main/protein_information_system/sql/model/entities/go_annotation/go_annotation.py)

### Outputs and Exit Criteria

**D2:** policy definitions, retention report, paired changes y annotation-count control.

**Exit criterion:** todo cambio se acompaÃ±a de coverage, annotation count y eligibility; missingness no se sustituye por cero.

**Presentation asset:** retention plot y paired-change plot. **Interpretation boundary:** una reducciÃ³n del score al filtrar no se atribuirÃ¡ automÃ¡ticamente a mayor especificidad biolÃ³gica.

## B3 â€” MFâ€“MF Divergence

### Purpose and Questions

**Purpose:** caracterizar diferencias entre unique GO-MF terms de una proteÃ­na.

- **RQ3.1:** Â¿QuÃ© amplitud de divergence muestran los annotation sets?
- **RQ3.2:** Â¿Coinciden semantic similarity, graph distance y GeOKG-GO dissimilarity?
- **RQ3.3:** Â¿QuÃ© pares explican los valores extremos?
- **RQ3.4:** Â¿QuÃ© estabilidad se mantiene entre evidence policies?

### Resource Stratification

| Layer | Contenido |
|---|---|
| Upstream inputs | D1, policies B2, GO snapshot y reference IC profile |
| Existing capability | MBL, Wang, Resnik, Lin y Schlicker en CBBIO |
| Required additions | Pair aggregation con status y GeOKG-GO distance adapter validado |
| Resources produced | Protein descriptors, term-pair table, extreme-pair log y embedding coverage |
| Downstream consumers | B2 sensitivity comparisons, B5 y B6 |

CBBIO documenta estas semantic similarity methods y la preparaciÃ³n de counts para IC. [GO API](https://github.com/CBBIO/BioData/blob/main/docs/GO.md)

### Descriptor Hierarchy

| Family | Proposed role | RestricciÃ³n |
|---|---|---|
| Wang | Primary baseline candidate | Validar implementaciÃ³n y conventions |
| MBL | Secondary topological descriptor | Mantener separada su escala de la similitud |
| Lin / Resnik / Schlicker | IC-dependent sensitivity family | Reference corpus y propagation congelados |
| GeOKG-GO | Complementary learned representation | GeometrÃ­a y artifact contract explÃ­citos |
| DÂ³-MBL / RICD-MBL | Deferred candidates del planteamiento anterior | Sin definiciÃ³n operativa aprobada; no forman parte de los cÃ¡lculos iniciales |

**Primary descriptor propuesto:** media de `1 âˆ’ Wang similarity` sobre pares no ordenados de tÃ©rminos distintos. Su selecciÃ³n debe aprobarse en G2, antes de inspeccionar resultados. Se denomina dissimilarity descriptor; no se presupone que satisfaga todos los axiomas de una mathematical distance.

Para una proteÃ­na con tÃ©rminos elegibles \(T_p\), el descriptor propuesto es:

\[
D_p = \frac{2}{n_p(n_p-1)}\sum_{i<j}\left[1-S_{\mathrm{Wang}}(t_i,t_j)\right],\qquad n_p=|T_p|\geq 2.
\]

Mediana, quantiles y mÃ¡ximo son secondary descriptors. Se conservarÃ¡n `n_terms`, `n_pairs_expected`, `n_pairs_computed` y `pair_coverage`. Una proteÃ­na con menos de dos tÃ©rminos elegibles recibirÃ¡ `insufficient_terms`.

### GeOKG-GO Contract

El repositorio distingue entrenamiento GO mediante `GeOKG_go` y entrenamiento GOA mediante `GeOKG`; no se intercambiarÃ¡n sus artefactos. [GeOKG README](https://github.com/ukjung21/GeOKG/blob/main/README.md)

La implementaciÃ³n incorpora operaciones hiperbÃ³licas, parÃ¡metros de curvature y transformaciones dependientes de relation. Por ello, aplicar cosine a una matriz exportada no equivale automÃ¡ticamente al model-native score. [GeOKG implementation](https://github.com/ukjung21/GeOKG/blob/main/models/geokg.py)

El contract debe registrar checkpoint, checksum, training graph/GO release, GO ID mapping, vector space, curvature, relation parameters necesarios y definiciÃ³n exacta de dissimilarity. Si no hay una Ãºnica distancia simÃ©trica entre tÃ©rminos implÃ­cita en el modelo, no se inventarÃ¡: se aprobarÃ¡ un descriptor explÃ­cito y se limitarÃ¡ su interpretaciÃ³n. Un generic cosine baseline sobre vectors puede estudiarse por separado, correctamente etiquetado.

La comparaciÃ³n principal entre mÃ©tricas usarÃ¡ el mismo conjunto de term pairs calculables. Los resultados sobre todos los pares disponibles para cada mÃ©todo se reportarÃ¡n como anÃ¡lisis adicional, con su coverage.

### Outputs and Exit Criteria

**D3:** descriptor table, term-pair table, GeOKG coverage y calculation-status report.

**Exit criterion:** fÃ³rmula, direcciÃ³n, escala, aggregation y missingness especificados; GeOKG no entra en ejecuciÃ³n hasta validar su contract.

**Presentation asset:** distributions de divergence y ejemplos de pares discordantes. **Interpretation boundary:** GO-MF divergence no se convierte por sÃ­ sola en evidencia de multifunctionality o moonlighting.

## B4 â€” MFâ€“CC Association

### Purpose and Questions

**Purpose:** medir co-annotation patterns entre GO-MF y GO-CC en una reference population.

- **RQ4.1:** Â¿QuÃ© parejas son frecuentes o poco frecuentes dentro del corpus elegible?
- **RQ4.2:** Â¿Con quÃ© support counts se estiman esas asociaciones?
- **RQ4.3:** Â¿QuÃ© perfiles presenta TargetData frente a la referencia?
- **RQ4.4:** Â¿QuÃ© resultados dependen de propagation, evidence policy o taxonomic composition?

### Resource Stratification

| Layer | Contenido |
|---|---|
| Upstream inputs | D1, policies B2, GO-MF/GO-CC annotations y BioData snapshot |
| Existing capability | Retrieval batch y ontology utilities de CBBIO |
| Required additions | Co-occurrence profile builder, support policy y protein aggregation |
| Resources produced | Reference counts, association table y per-protein association descriptors |
| Downstream consumers | B2, B5 y B6 |

El retrieval de GO annotations y los accesos batch se apoyan en la [BioData API](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md); la mÃ©trica de asociaciÃ³n es una propuesta experimental, no una capacidad existente afirmada del client.

### Proposed Association Specification

El baseline propuesto utiliza proteÃ­nas Ãºnicas con al menos un tÃ©rmino GO-MF y uno GO-CC elegibles, de modo que joint y marginal counts comparten el mismo denominator. Cada proteÃ­na contribuye como mÃ¡ximo una vez a cada term pair.

Como candidate association descriptor se propone Normalized Pointwise Mutual Information, NPMI:

\[
\mathrm{NPMI}(m,c)=\frac{\log\left[P(m,c)/(P(m)P(c))\right]}{-\log P(m,c)}.
\]

La definiciÃ³n operativa se aprobarÃ¡ en G2 y distinguirÃ¡ al menos:

- Joint probability cero: registrar `unobserved_pair`; no asignar automÃ¡ticamente un valor de incompatibilidad.
- Joint probability uno: caso degenerado de la expresiÃ³n; registrar el tratamiento explÃ­cito y no dejar que genere NaN silenciosos.
- Support insuficiente: `low_support`, aunque exista una estimaciÃ³n numÃ©rica.
- Rare marginals: reportar los counts junto con el score.
- Propagation y roots: fijar una policy para evitar que tÃ©rminos generales dominen las coocurrencias.

El reference profile excluirÃ¡ TargetData por identificadores y exact sequence matches cuando sea factible. Si el overlap no puede eliminarse, se cuantificarÃ¡ y se realizarÃ¡ una sensibilidad; no se ocultarÃ¡.

### Outputs and Exit Criteria

**D4:** reference profile fingerprint, eligible-universe definition, count tables y association descriptors.

**Exit criterion:** denominadores consistentes; support threshold aprobado; casos lÃ­mite y protein aggregation documentados.

**Presentation asset:** association heatmap con counts y categorÃ­as de soporte. **Interpretation boundary:** una GO-MF y una GO-CC coanotadas en una proteÃ­na no demuestran que esa funciÃ³n se ejecute en ese compartimento. Rareza no equivale a incompatibilidad.

## B5 â€” Reference and Complementarity

### Purpose and Questions

**Purpose:** contextualizar TargetData y seleccionar un panel de descriptors informativos sin confundir reference population con negative class.

- **RQ5.1:** Â¿DÃ³nde se sitÃºa TargetData en las distribuciones de BioData?
- **RQ5.2:** Â¿Persisten diferencias al controlar taxonomÃ­a, longitud y annotation density?
- **RQ5.3:** Â¿QuÃ© mÃ©tricas son redundantes y cuÃ¡les generan discordancias Ãºtiles?
- **RQ5.4:** Â¿QuÃ© aporta GeOKG-GO mÃ¡s allÃ¡ de los descriptors clÃ¡sicos?

### Resource Stratification

| Layer | Contenido |
|---|---|
| Upstream inputs | D1â€“D4, metadatos y GeOKG-GO contract |
| Existing capability | Data retrieval y BMA para semantic similarity entre conjuntos GO |
| Required additions | Reference sampling/matching plan, statistical comparisons y GeOKG set aggregation si se aprueba |
| Resources produced | Contextualized comparisons, redundancy map y discordance case list |
| Downstream consumers | B6, panel final de descriptors y presentation assets |

La API GO documenta BMA entre annotation sets para sus semantic similarity methods; eso no implica que BMA para GeOKG estÃ© ya implementado o validado. [GO API](https://github.com/CBBIO/BioData/blob/main/docs/GO.md)

### Comparison Plan

Se propone combinar una comparaciÃ³n global con anÃ¡lisis estratificados o matched comparisons, cuando exista common support. Las reglas de matching se fijarÃ¡n antes de analizar los outcomes: organism/taxonomic group, sequence length, annotation count y evidence coverage. No se forzarÃ¡n matches de mala calidad ni se extrapolarÃ¡ a estratos sin comparadores adecuados.

La correlaciÃ³n entre descriptors se analizarÃ¡ sobre las mismas proteÃ­nas calculables, con coverage explÃ­cita. La independencia de un descriptor respecto de otro no basta para demostrar utilidad biolÃ³gica; deberÃ¡ conectarse con evidencia y casos interpretables en B6.

### GeOKG-GO Uses

| Use | Propuesta | CondiciÃ³n |
|---|---|---|
| Descriptor comparison | Contrastar intra-protein GeOKG divergence con Wang, MBL e IC-based descriptors | Mismo term-pair support |
| Protein-level comparison | Comparar conjuntos GO mediante una agregaciÃ³n explÃ­cita de term dissimilarities | DefiniciÃ³n simÃ©trica y geomÃ©tricamente justificada |

No se calcularÃ¡n arithmetic centroids de embeddings hiperbÃ³licos como si fueran puntos euclidianos sin justificaciÃ³n. La comparaciÃ³n protein-level es secundaria y puede aplazarse sin redefinir retrospectivamente el objetivo de B3.

### Outputs and Exit Criteria

**D5:** reference comparison report, effect estimates, redundancy analysis y discordance list.

**Exit criterion:** comparaciones acompaÃ±adas de uncertainty, coverage y matching diagnostics; sin presentar BioData como verified NMF class.

**Presentation asset:** effect-size plot, metric correlation matrix y discordance table. **Interpretation boundary:** ninguna comparaciÃ³n descrita constituye una evaluaciÃ³n supervisada MFâ€“NMF ni demuestra causalidad.

## B6 â€” Curation and Interpretation

### Purpose and Questions

**Purpose:** convertir resultados numÃ©ricos en decisiones de curation con evidencia independiente y audit trail.

- **RQ6.1:** Â¿QuÃ© casos tienen soporte suficiente para la etiqueta biolÃ³gica propuesta?
- **RQ6.2:** Â¿QuÃ© discordancias se explican por incomplete data o annotation artefacts?
- **RQ6.3:** Â¿QuÃ© casos continÃºan unresolved despuÃ©s de revisar sus fuentes?
- **RQ6.4:** Â¿QuÃ© conclusiones puede defender el equipo sin exceder la evidencia?

### Resource Stratification

| Layer | Contenido |
|---|---|
| Upstream inputs | D1â€“D5, source records y bibliographic evidence |
| Existing capability | Protein context retrieval mediante CBBIO |
| Required additions | Curation form, reviewer protocol y disagreement resolution |
| Resources produced | Curated TargetData, evidence records, decision log y scientific narrative |
| Downstream consumers | Dataset release, presentation y future PEC experiments |

El acceso al contexto de proteÃ­na estÃ¡ documentado en la [BioData API](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md); la disponibilidad de referencias primarias deberÃ¡ verificarse por separado.

### Review Sampling

La revisiÃ³n incluirÃ¡ casos representativos, extremos, discordantes entre mÃ©tricas, sensibles a evidence policy y una muestra no seleccionada por scores. El presupuesto de revisiÃ³n y la sample selection rule se aprobarÃ¡n antes de abrir las fichas. Cuando sea viable, un segundo reviewer evaluarÃ¡ una parte predefinida, con resoluciÃ³n explÃ­cita de desacuerdos.

### Curation Record

| Field | Contenido |
|---|---|
| Case identity | Protein ID, accessions, organismo y snapshot |
| Biological claim | Funciones cuya coexistencia se evalÃºa y definiciÃ³n aplicada |
| Independent evidence | Referencias originales, experimental context y limitaciones |
| Computed descriptors | Scores, policies, coverage y calculation status |
| Decision | Supported, insufficient evidence, contradictory evidence o unresolved |
| Review trace | Reviewer, fecha, justificaciÃ³n y disagreement resolution |
| Dataset impact | Cambio propuesto y relaciÃ³n con el registro anterior |

Biological label, evidence level y experimental role se mantendrÃ¡n separados. La curaciÃ³n no borrarÃ¡ la historia de TargetData_initial.

### Outputs and Exit Criteria

**D6:** TargetData_curated, evidence records, change set e informe cientÃ­fico.

**Exit criterion:** cada decisiÃ³n tiene fuente, justificaciÃ³n y reviewer; los casos unresolved permanecen visibles. La release puede contener incertidumbre documentada y no exige forzar todas las etiquetas.

**Presentation asset:** case study cards y curation flow. **Interpretation boundary:** no confirmar casos mediante un score y reutilizar despuÃ©s esas etiquetas como validaciÃ³n independiente del mismo score.

## E1 â€” PCA 3D

### Extension Specification

| Element | Propuesta |
|---|---|
| Purpose | Explorar gradients de los descriptors en las principales direcciones de sequence embeddings |
| Input | Embeddings de un model/layer/pooling identificados, unidos por sequence identity |
| Projection | Tres principal components y explained variance por componente |
| Color variables | Divergence, MFâ€“CC association, annotation counts, evidence retention, longitud, taxonomÃ­a, fuente y curation status |
| Interaction | Hover con identificadores, coverage y cÃ¡lculo seleccionado; filtros sin refit silencioso |
| Output | Interactive HTML, static figure, coordinate table y projection manifest |
| Exit criterion | Data join validado, preprocessing registrado y explained variance visible |

La comparaciÃ³n entre colores mantendrÃ¡ las mismas coordenadas. La misma variable conservarÃ¡ color scale y rango entre vistas comparables; missing values tendrÃ¡n una categorÃ­a visual diferenciada. No se compararÃ¡n ejes PC de modelos distintos como si fueran un espacio comÃºn.

Centering, normalization y cualquier scaling se aprobarÃ¡n y registrarÃ¡n explÃ­citamente. No se aplicarÃ¡ standardization por defecto sin justificarla para los embeddings utilizados.

## E2 â€” UMAP 3D

### Extension Specification

| Element | Propuesta |
|---|---|
| Purpose | Explorar local neighborhoods asociados a los descriptors calculados |
| Input | El mismo embedding set utilizado en E1, salvo diferencia declarada |
| Projection | Tres dimensiones; metric, parameters, seed y version registrados |
| Color variables | El mismo catÃ¡logo de E1, sin usar esos scores como input de la proyecciÃ³n principal |
| Stability | PequeÃ±a configuration grid predefinida y comparaciÃ³n entre seeds |
| Output | Interactive HTML, static figure, coordinates y configuration manifest |
| Exit criterion | ConfiguraciÃ³n y estabilidad documentadas; sin selecciÃ³n exclusiva de la vista mÃ¡s atractiva |

Los ejes UMAP no se interpretarÃ¡n como variables biolÃ³gicas. Una separaciÃ³n visual no serÃ¡ una prueba confirmatoria de class separability ni validarÃ¡ un futuro classifier. Un anÃ¡lisis de projection quality o neighborhood preservation puede incorporarse si se aprueba expresamente.

E1 y E2 son deliverables futuros: esta propuesta no contiene proyecciones calculadas ni synthetic demonstration data.

## Statistical Analysis Plan

### Analysis Units

| Analysis | Unidad | Control requerido |
|---|---|---|
| B1 coverage | ProteÃ­na o secuencia, segÃºn denominator declarado | Identity/deduplication policy |
| B2 policy comparison | Misma proteÃ­na bajo varias policies | Paired design y eligibility changes |
| B3 divergence | ProteÃ­na; term pairs como observaciones internas | No tratar pares como biological replicates independientes |
| B4 reference counts | ProteÃ­na Ãºnica por term pair | Marginals y joint counts con el mismo denominator |
| B5 comparison | ProteÃ­na o grupo de proteÃ­nas relacionadas | Stratification, matching y dependencia biolÃ³gica |
| B6 curation | Caso revisado | Review sampling y provenance |

### Estimation and Uncertainty

Como default propuesto, priorizar distributions, effect sizes y 95% confidence intervals. Cuando se utilice bootstrap, el resampling se harÃ¡ por proteÃ­na o por agrupaciÃ³n biolÃ³gica definida, no por term pair. Replications, seeds y clustering rule se aprobarÃ¡n en G2. Si el nÃºmero o la composiciÃ³n de las observaciones no permite una inferencia fiable, el resultado se presentarÃ¡ como descriptive analysis.

Los primary contrasts se especificarÃ¡n antes del full-scale run. Los secondary/exploratory analyses se etiquetarÃ¡n; si se presentan mÃºltiples hypothesis tests, se fijarÃ¡ el multiple-testing correction plan. No se seleccionarÃ¡ retrospectivamente la mÃ©trica que produzca el menor p-value.

### Confounders and Sensitivity

El plan considerarÃ¡ taxonomy, sequence length, annotation density, evidence coverage, source composition y homology/duplicate structure. Ajustar o emparejar por annotation count estima una comparaciÃ³n condicionada distinta de la comparaciÃ³n marginal; ambas se presentarÃ¡n con su interpretaciÃ³n, no como si una reemplazara necesariamente a la otra.

Coverage restriction, term-set preprocessing, overlap handling y reference profile choices serÃ¡n sensitivity dimensions. Un resultado nulo o inestable es un resultado vÃ¡lido; el Ã©xito del proyecto depende de responder las preguntas con trazabilidad, no de obtener diferencias favorables.

## Software Responsibility Map

### Component Ownership

| Capability | Proposed owner | Rationale |
|---|---|---|
| Acquisition y preservaciÃ³n de assertions/references | PIS | Corregir en origen la pÃ©rdida de informaciÃ³n |
| Database access y batch retrieval | CBBIO | Interfaz comÃºn, reusable y testeable |
| Evidence selection como mecanismo general | CBBIO, si se generaliza | Evitar filtros duplicados en cada experimento |
| GO semantic calculations | CBBIO | Reutilizar las capacidades existentes |
| Pair aggregation y status management | CBBIO si tiene uso transversal | Mecanismo reusable, separado de hipÃ³tesis |
| IC/co-occurrence profile builders | CBBIO si se generalizan | Artefactos compartidos con fingerprint |
| GeOKG adapter | CBBIO tras aprobar el contract | Aislar geometrÃ­a y compatibilidad del artefacto |
| Cohort, matching y scientific contrasts | Experimental project | Decisiones especÃ­ficas del estudio |
| Curation y presentation | Experimental project | InterpretaciÃ³n y comunicaciÃ³n cientÃ­fica |
| Future training/benchmarking | PEC | Fase posterior con protocolo propio |

### Extension Acceptance Criteria

Una extensiÃ³n de CBBIO debe tener una responsabilidad general, typed inputs/outputs, documentaciÃ³n de errores, unit tests y tests de integraciÃ³n cuando requiera datos reales. No deberÃ¡ contener IDs de la cohort ni thresholds exclusivos del proyecto hard-coded.

El experimental project consumirÃ¡ la API preferentemente mediante batch operations. Las consultas SQL excepcionales deberÃ¡n quedar aisladas y justificadas; la existencia de raw SQL helpers no convierte el acoplamiento al schema en la opciÃ³n principal. [BioData access documentation](https://github.com/CBBIO/BioData/blob/main/docs/BioData.md)

### Compatibility Audit

Antes de reutilizar cÃ³digo de etapas anteriores, ejecutar contract tests contra las versiones fijadas de CBBIO y del pipeline. Esta propuesta no da por demostrado un defecto concreto de legacy code sin una auditorÃ­a reproducible. El control obligatorio es verificar method names, argument conventions, return types y tratamiento de fallos.

## Reproducibility and Execution

### Run Manifest

Cada run y cada derived table deberÃ¡n permitir recuperar:

- `protocol_id`, `protocol_version`, `run_id` y timestamp.
- BioData y TargetData snapshot IDs/checksums.
- GO release, evidence policy y term processing policy.
- Reference profile fingerprint y eligible-universe definition.
- Code commits, dependency lock y runtime environment.
- Model, checkpoint, layer, pooling y embedding provenance, cuando proceda.
- Metric definition/version, aggregation y missingness policy.
- Seeds, sampling configuration y bootstrap configuration.
- Resources consumidos, execution status y failure log.

### Artifact Layout

La siguiente estructura es una **propuesta de almacenamiento de resultados**, no una descripciÃ³n del repositorio actual:

```text
experiment/
â”œâ”€â”€ protocol/        # Documento, decision register y versiones aprobadas
â”œâ”€â”€ configs/         # Cohort, policies, metrics y execution settings
â”œâ”€â”€ manifests/       # Fingerprints de snapshots, profiles y runs
â”œâ”€â”€ tables/          # Tablas derivadas, status y coverage
â”œâ”€â”€ figures/         # Figuras reproducibles por block
â”œâ”€â”€ curation/        # Evidence records y reviewer decisions
â”œâ”€â”€ reports/         # InterpretaciÃ³n y entregables de revisiÃ³n
â””â”€â”€ presentation/    # Storyboard y futuro slide deck
```

### Pilot and Scaling

El technical pilot incluirÃ¡ registros con diferentes annotation counts, missingness, organismos y cobertura GeOKG. Su objetivo serÃ¡ validar el recorrido completo y medir retrieval time, CPU/GPU time, memory, storage y errores; no elegir la variante que ofrezca mejores resultados cientÃ­ficos.

Los pares de n tÃ©rminos crecen como \(n(n-1)/2\). Por ello, se propone caching por term pair y configuraciÃ³n, batch retrieval y checkpoints por shard. Las concurrency limits deben proteger PostgreSQL. Si es necesario introducir sampling de pares por coste, serÃ¡ un protocol amendment, no una optimizaciÃ³n invisible.

No se comprometen todavÃ­a horas de GPU, volumen de almacenamiento o calendario. El resource budget se aprobarÃ¡ con mediciones del pilot, incluyendo GeOKG artifact loading, reference profile construction, reviewer effort y E1/E2 por separado.

### Test Strategy

| Test family | ComprobaciÃ³n propuesta |
|---|---|
| Identity tests | Aliases, isoformas, duplicate sequences y joins |
| GO policy tests | Roots, obsolete IDs, qualifiers, unknown evidence y namespace separation |
| Metric tests | Identidad, simetrÃ­a cuando aplique, rango documentado y casos lÃ­mite |
| Missingness tests | Ausencia/error distinguibles de cero vÃ¡lido |
| Profile tests | Marginal/joint counts coherentes y corpus fingerprint |
| GeOKG tests | Mapping, dimensionalidad, geometrÃ­a y artefactos incompatibles |
| Reproducibility tests | Resultados repetibles dentro de tolerancias declaradas |
| Integration tests | Acceso a snapshots y compatibilidad del deployment |

## Delivery and Approval

### Deliverable Matrix

| ID | Deliverable | Acceptance evidence |
|---|---|---|
| D0 | Protocol and decision record | Scope aprobado y open decisions bloqueantes resueltas |
| D1 | Frozen cohort and coverage | Manifest, mapping y exclusions reconstruibles |
| D2 | Evidence sensitivity report | Policies y denominadores comparables |
| D3 | MFâ€“MF divergence results | FÃ³rmulas, status, pairs y GeOKG contract |
| D4 | MFâ€“CC reference profile | Universe, counts, support y profile fingerprint |
| D5 | Reference/complementarity report | Effect estimates, uncertainty y controls |
| D6 | Curated TargetData | Evidence records y audit trail |
| D7 | Team proposal presentation | Storyboard derivado del protocolo aprobado |
| E1 | PCA 3D package | Coordinates, preprocessing y explained variance |
| E2 | UMAP 3D package | Coordinates, parameters y stability report |

### Decision Gates

| Gate | Approval scope | Blocking condition |
|---|---|---|
| G0 â€” Scientific approval | Questions, seis blocks, scope y conclusions permitidas | Scope o objetivo central sin acuerdo |
| G1 â€” Data readiness | Access, snapshots, contracts y overlap policy | Campos crÃ­ticos o identity mapping sin resolver |
| G2 â€” Calculation readiness | Metrics, policies, aggregation, statistics y GeOKG contract | FÃ³rmulas o tratamiento de fallos ambiguos |
| G3 â€” Pilot approval | End-to-end correctness, resource budget y tests | Coste no medido o resultados no reproducibles |
| G4 â€” Full-scale release | Main analyses y sensitivities separados | Cambios no registrados o artefactos incompletos |
| G5 â€” Team review | Interpretation, curation y release decisions | Claims sin evidencia o decisiones no auditables |

G0 debe preceder al trabajo experimental. G1â€“G3 son verificaciones controladas previstas por el protocolo, no autorizaciÃ³n para modificar libremente el diseÃ±o. GeOKG en B3 es parte de la propuesta cientÃ­fica; si su artifact contract falla, el equipo debe aprobar un alcance reducido explÃ­cito en lugar de omitirlo silenciosamente. Las extensiones E1/E2 se autorizan y presupuestan por separado.

### Roles

| Role | Responsabilidad |
|---|---|
| Scientific Lead | HipÃ³tesis, scope, interpretaciÃ³n y protocol amendments |
| Data/PIS Owner | Snapshots, provenance, schema y access |
| API/Methods Owner | Contracts, implementations, tests y cÃ¡lculo |
| Analysis Owner | Statistical plan, figures y reproducibility |
| Curation Lead / Reviewer | Evidence records y disagreement resolution |
| Team Approver | AceptaciÃ³n de gates, recursos y deliverables |

Una persona puede cubrir varios roles, pero las responsabilidades deben tener un owner nominal antes del gate que corresponda.

## Decision Register

| ID | Decision | Proposed position | State | Required by |
|---|---|---|---|---|
| DEC-01 | Scope principal | Characterization and curation; no classifier training | Proposed | G0 |
| DEC-02 | Unit identity | Diferenciar proteÃ­na, accession, isoforma y sequence | Open | G1 |
| DEC-03 | TargetData/BioData compatibility | Verificar schema y acceso API; adapter fino si procede | Open | G1 |
| DEC-04 | Provenance preservation | Auditar references, qualifiers y mÃºltiples evidencias | Open | G1 |
| DEC-05 | Evidence policies | ALL_ELIGIBLE, EXP_CONVENTIONAL, EXP_EXTENDED | Proposed | G2 |
| DEC-06 | GO processing | Congelar release y separar asserted terms de IC propagation | Proposed | G2 |
| DEC-07 | Primary MFâ€“MF descriptor | Mean Wang dissimilarity; secundarios separados | Proposed | G2 |
| DEC-08 | GeOKG contract | Confirmar artifact, mapping y geometry antes de ejecuciÃ³n | Open | G2 |
| DEC-09 | MFâ€“CC association | NPMI candidate con universe y support definidos | Proposed | G2 |
| DEC-10 | Protein aggregation B4 | Fijar resumen y regla de elegibilidad | Open | G2 |
| DEC-11 | Reference selection | Excluir overlap y comparar con controles definidos | Proposed | G2 |
| DEC-12 | Statistical settings | Primary contrasts, resampling, matching y multiplicidad | Open | G2 |
| DEC-13 | Curation protocol | Case sampling, reviewers y independent evidence | Open | G3 |
| DEC-14 | Resource budget | Aprobar a partir de mediciones del pilot | Open | G3 |
| DEC-15 | Sequence embeddings | Elegir model/layer/pooling y normalization | Open | E1/E2 |
| DEC-16 | Visualization parameters | Congelar color scales y UMAP stability grid | Open | E1/E2 |
| DEC-17 | Future PEC integration | Protocolo separado de training y sampling ratios | Deferred | Fase futura |

Las open decisions son compromisos de revisiÃ³n con gate asociado, no huecos que deban rellenarse inventando datos. Una resoluciÃ³n debe aÃ±adir fecha, owner, justificaciÃ³n y efectos sobre otras decisiones.

## Risk Register

| Risk | Consecuencia | Mitigation | Block |
|---|---|---|---|
| Provenance incompleta | Policies o curation no reconstruibles | Corregir ingestion o limitar claims explÃ­citamente | B1/B2/B6 |
| Reference/TargetData overlap | ContextualizaciÃ³n parcialmente autorreferente | Exclusion policy y sensitivity | B1/B4/B5 |
| Annotation density bias | Scores altos por mayor nÃºmero de tÃ©rminos | Count controls y paired design | B2/B3/B5 |
| Taxonomic composition | Diferencias debidas a composiciÃ³n | Stratification, matching y common-support checks | B5 |
| GeOKG geometry mismatch | Distancias sin interpretaciÃ³n vÃ¡lida | Artifact contract y geometry tests | B3/B5 |
| Coverage mismatch entre mÃ©tricas | Complementarity aparente por samples distintos | Common-support comparison | B3/B5 |
| Sparse MFâ€“CC pairs | Asociaciones extremas poco fiables | Support counts y low-support status | B4 |
| Pseudoreplication | Uncertainty demasiado optimista | Protein/group-level resampling | B3/B5 |
| Circular curation | ValidaciÃ³n invÃ¡lida del propio score | Independent evidence y sample no seleccionado por score | B6 |
| Projection cherry-picking | Narrativa visual no robusta | Fixed preprocessing y predefined stability grid | E1/E2 |
| Scope creep | Bloqueo del core study | Deferred backlog y protocol amendments | Todos |

## Slide Deck Storyboard

### Presentation Purpose

La primera presentaciÃ³n es de **project proposal**, no de resultados. Su objetivo es acordar questions, scope, resources y approval criteria. Las figuras previstas deben mostrarse como diagramas o specifications; no utilizar resultados inventados ni grÃ¡ficos que aparenten observaciones reales.

El storyboard se deriva de los identifiers del documento. Cada slide debe tener una idea central, un visual Ãºtil y una decisiÃ³n o mensaje verificable; el detalle de fÃ³rmulas, contracts y tests puede trasladarse al appendix.

### Core Narrative

| Slide | English title | Mensaje en castellano | Visual propuesto | Document source |
|---|---|---|---|---|
| S01 | Project Proposal | Se solicita aprobaciÃ³n de un estudio de characterization y curation | Objetivo central y scope boundary | Executive Overview |
| S02 | Research Questions | El proyecto responde seis preguntas conectadas, no una lista abierta de mÃ©tricas | Question map | Research Framework |
| S03 | Scope and Non-Goals | El Ã©xito no exige entrenar un classifier ni demostrar multifunctionality con un score | Included / excluded panel | Scope and Boundaries |
| S04 | Data Ecosystem | PIS, BioData, TargetData y CBBIO tienen responsabilidades distintas | Architecture diagram | Resource Baseline |
| S05 | Data Readiness | Disponibilidad de software no equivale a coverage de datos | Contract matrix y readiness statuses | Data Contracts |
| S06 | Experimental Roadmap | Cada block deja artefactos que habilitan el siguiente | Dependency flow | Experimental Architecture |
| S07 | B1 â€” Corpus and Evidence | Primero se fija quÃ© se analiza y con quÃ© evidencia | Mock layout de coverage, sin datos | B1 |
| S08 | B2 â€” Evidence Sensitivity | Hay que separar evidence filtering de annotation-count effects | Paired-design schematic | B2 |
| S09 | B3 â€” MFâ€“MF Divergence | Se contrastan semantic, topological y learned representations | Descriptor families y term pairs | B3 |
| S10 | GeOKG-GO Integration | El valor aÃ±adido depende de artifact coverage y geometry | Contract y dos usos B3/B5 | B3/B5 |
| S11 | B4 â€” MFâ€“CC Association | Rareza y coanotaciÃ³n no equivalen a mecanismo biolÃ³gico | Count-to-association schematic | B4 |
| S12 | B5 â€” Reference and Complementarity | BioData contextualiza; no constituye una negative class | Comparison/control design | B5 |
| S13 | B6 â€” Curation and Interpretation | Los scores priorizan revisiÃ³n; la evidencia independiente decide | Evidence record y decision flow | B6 |
| S14 | Reproducibility and Resources | Snapshots, manifests y pilot measurements hacen auditable la ejecuciÃ³n | Run manifest y gates | Reproducibility and Execution |
| S15 | 3D Exploration Backlog | PCA/UMAP consumen embeddings de secuencia y colores de los descriptors | Esquema inputs/projection/color | E1/E2 |
| S16 | Risks and Safeguards | Los principales sesgos tienen controles explÃ­citos | Risk-to-control matrix | Risk Register |
| S17 | Approval Request | La reuniÃ³n debe cerrar decisiones y owners por gate | Decision checklist | Delivery and Approval |

### Appendix Candidates

- FÃ³rmula y aggregation del primary divergence descriptor.
- Evidence policies y tratamiento de qualifiers.
- NPMI universe, support y casos lÃ­mite.
- GeOKG artifact contract y diferencias GO/GOA.
- Statistical Analysis Plan y matching diagnostics.
- Data contracts, calculation statuses y test strategy.

### Reuse Rules

1. Extraer mensajes del scope y de las research questions aprobadas, no de resultados esperados.
2. Mantener consistentes los nombres B1â€“B6, D1â€“D7 y E1/E2 entre documento y slides.
3. Conservar hyperlinks a las fuentes tÃ©cnicas en notes o appendix.
4. No trasladar tablas extensas literalmente: seleccionar el mensaje y mantener el detalle en este documento.
5. DespuÃ©s de ejecutar, sustituir las especificaciones visuales por figuras reales y aÃ±adir una referencia al run manifest.
6. Si cambia el scope durante la revisiÃ³n, actualizar primero este documento y despuÃ©s el deck.

## Review Checklist

### Scientific Approval

- [ ] La central research question estÃ¡ aprobada.
- [ ] Los seis blocks tienen inputs, outputs y exit criteria aceptados.
- [ ] Se distingue multifunctionality de moonlighting y de annotation count.
- [ ] BioData no se presenta como verified negative class.
- [ ] GeOKG tiene un uso y un contract definidos.
- [ ] Los primary contrasts y la interpretation boundary estÃ¡n fijados.

### Data and Methods Readiness

- [ ] TargetData_initial y BioData_reference estÃ¡n identificados y accesibles.
- [ ] Identity, isoform y overlap policies estÃ¡n cerradas.
- [ ] References, qualifiers y evidence provenance estÃ¡n auditados.
- [ ] GO snapshot y evidence policies estÃ¡n versionados.
- [ ] Missingness y calculation statuses se aplican sin zeros por defecto.
- [ ] Reference profiles, support thresholds y aggregation estÃ¡n definidos.
- [ ] Contract tests e integration tests son satisfactorios.

### Execution and Communication

- [ ] El pilot tiene propÃ³sito tÃ©cnico y selecciÃ³n documentada.
- [ ] El resource budget y los owners estÃ¡n aprobados.
- [ ] Los protocol amendments quedan registrados.
- [ ] La curation usa evidencia independiente y conserva casos unresolved.
- [ ] Las extensiones E1/E2 tienen presupuesto y configuraciÃ³n propios.
- [ ] El proposal deck se deriva de la versiÃ³n aprobada del documento.

## Change Log

| Version | Date | Change | Status |
|---|---|---|---|
| 0.1.0 | 2026-10-27 | ConsolidaciÃ³n de la propuesta de seis blocks, GeOKG-GO, extensiones PCA/UMAP, data contracts y presentation storyboard | Draft for team review |

<!-- Editing guidance: mantener los IDs estables; registrar decisiones metodolÃ³gicas con owner y fecha. Los valores operativos aÃºn no aprobados se resuelven mediante el Decision Register, no sustituyendo silenciosamente el texto. -->
