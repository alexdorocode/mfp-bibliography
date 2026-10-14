# Matriu de Capacitats d'Auditoria i Nivells d'Anàlisi del Corpus MFP

- **Auditor**: Auditor Tècnic Senior de Pipelines Bioinformàtics, Investigador en Multifuncionalitat Proteica i Arquitecte de Sistemes d'Experimentació Científica Reproduïble
- **Data de l'Auditoria**: 2026-10-14
- **Artefacte d'Avaluació**: Dades de catàleg `mfp_catalog_mvp` (`mfp-bibliography`), esquema relacional de `BioData` (PostgreSQL 16) i mòduls d'anàlisi de `mfp-dataset-designer`.
- **Objectiu**: Determinar amb rigor el nivell d'auditoria aplicable a cada subcohort de dades segons les dades realment persistides.

---

## 1. Resum Executiu de Capacitats

La capacitat d'auditoria no és homogènia en tot el corpus: depèn directament de la font original de cada proteïna, del seu estat de revisió a UniProtKB (Swiss-Prot vs TrEMBL) i de les limitacions estructurals del pipeline d'ingesta.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAPACITAT GLOBAL D'AUDITORIA                          │
├──────────────────────────────────────────────────┬──────────────────────────┤
│ A. Auditoria Estructural i Integritat Relacional │ SUPPORTED (5/6 taules)   │
│ B. Traçabilitat Raw → Proteïna Unificada → Font  │ PARTIAL (93,6% cohort)   │
│ C. Auditoria d'Anotacions i Evidència GO         │ PARTIAL (Caveat: NOT)    │
│ D. Comparació Reproduïble ALL versus EXP         │ BLOCKED (Codi mètric)    │
│ E. Anàlisi de Referències Bibliogràfiques        │ PARTIAL (Només PMIDs)    │
│ F. Revisió Suport Experimental a Funcions Dif.   │ BLOCKED (Manca mapatge)  │
└──────────────────────────────────────────────────┴──────────────────────────┘
```

---

## 2. Avaluació Detallada de Capacitats d'Auditoria

### Capacitat A: Auditoria Estructural i Integritat de Dades
- **Estat**: **SUPPORTED** (per a 5 de les 6 taules; **BLOCKED** per a `chain`).
- **Evidència Observada**:
  - Les taules `accession`, `protein`, `sequence`, `go_terms` i `protein_go_term_annotation` tenen claus primàries (PK) i claus foranes (FK) definides i validades per PostgreSQL.
  - La restricció d'unicitat `uq_pga_protein_go_evidence_publication` a `(protein_id, go_id, evidence_code, publication_id)` impedeix duplicats exactes de quàdruples d'anotació.
  - La taula `chain` conté exactament **0 files** (tota la informació estructural PDB associada està descarregada o no enllaçada en aquesta snapshot).
- **Cohort Aplicable**: 2.182 proteïnes a `protein`, 2.330 accessions a `accession`.
- **Camps Necessaris**: PKs, FKs, `sequence_hash` (SHA-256), `data_class`.
- **Camps Absents**: Contingut a la taula `chain`, mètriques de resolució estructural.
- **Biaixos i Limitacions**: La integritat relacional és forta a nivell de base de dades, però `protein.id` utilitza mnemònics SwissProt en comptes de l'accession canònic alfanumèric.
- **Conclusió que Permet**: Verificació determinista de la integritat referencial entre accessions, proteïnes, seqüències i anotacions GO a BioData.
- **Conclusió que NO Permet**: Anàlisi d'estructures 3D o correspondències de cadenes PDB a partir de la snapshot actual.
- **Reparació Mínima Necessària**: Cap per a la capa de seqüència i anotació GO; cal poblar `chain` i `structure` si es volen fer anàlisis estructurals.

---

### Capacitat B: Traçabilitat Raw $\to$ Proteïna Unificada $\to$ Font Original
- **Estat**: **PARTIAL** (93,6% de la cohort del catàleg; **BLOCKED** per a 149 entrades).
- **Evidència Observada**:
  - A `mfp-bibliography`, el catàleg `mfp-catalog-candidate-v0.3.0` unifica 2.962 registres d'origen en 2.322 entitats canòniques mitjançant el protocol deterministic `MFPB_PROTEIN_ID_V1`.
  - La traçabilitat `raw_path` $\to$ `source_record_id` $\to$ `protein_id` està completament preservada a `mfp_source_records.csv` per a MoonDB, MultifacetedProtDB i MultitaskProtDB-II.
  - **Ruptura de traçabilitat a BioData**: Dels 2.322 accessions canònics, 148 accessions van quedar amb `protein_id = NULL` a BioData perquè `UniProtExtractor` depèn estrictament de `Bio.ExPASy.get_sprot_raw` (Swiss-Prot). Les proteïnes unificades de TrEMBL (133) i les que contenien mnemònics d'origen bruts (15) van quedar desconnectades de la taula `protein`.
- **Cohort Aplicable**:
  - Subcohort Swiss-Prot (revisada): 2.173 proteïnes (93,6% del catàleg) $\to$ **SUPPORTED**.
  - Subcohort TrEMBL / mnemònics: 149 proteïnes (6,4% del catàleg) $\to$ **BLOCKED**.
- **Camps Necessaris**: `uniprot_id`, `canonical_uniprot_accession`, `source_name`, `source_record_id`, `accession.protein_id`.
- **Camps Absents**: Mapatge directe a BioData per als 148 accessions no enllaçats.
- **Biaixos i Limitacions**: Exclusió sistemàtica d'organismes i proteïnes no revisades a Swiss-Prot (especialment bacteris i plantes menys caracteritzats de MoonProt i PlantMP).
- **Conclusió que Permet**: Reconstrucció exacta de l'origen de dades per a les 2.173 proteïnes compartides entre el catàleg i BioData.
- **Conclusió que NO Permet**: Declarar que BioData conté la totalitat del corpus de multifuncionalitat unificat.
- **Reparació Mínima Necessària**: Executar una ingesta per a les 149 entrades no resoltes utilitzant la REST API d'UniProtKB (`rest.uniprot.org/uniprotkb/`) que admet tant Swiss-Prot com TrEMBL.

---

### Capacitat C: Auditoria d'Anotacions i Evidència GO
- **Estat**: **PARTIAL** (Anotacions positives i codis d'evidència GO verificats; **BLOCKED** per a qualificadors `NOT` i codis ECO).
- **Evidència Observada**:
  - BioData conté 96.186 files d'anotació cobrint 22 codis d'evidència GO (des d'IEA fins a IDA, IPI, EXP, etc.).
  - **Pèrdua de Qualifiers (Risc Crític)**: `QuickGOAnnotationExtractor` no llegeix el camp `qualifier`. Totes les anotacions amb qualificador negatiu (`NOT`) van ser guardades com a anotacions funcionals positives sense cap distinció a `protein_go_term_annotation`.
  - **Pèrdua d'ECO**: El codi d'evidència ontològic ECO (`ECO:0000314`, etc.) no es persisteix; només es desa l'acrònim GO (`IDA`, etc.).
  - **Truncament de Referències**: Per a anotacions amb més d'un article a QuickGO, només es va desar el primer PMID. Les referències no-PMID es van descartar (`NULL`).
- **Cohort Aplicable**: 2.167 proteïnes amb almenys una anotació GO a BioData.
- **Camps Necessaris**: `go_id`, `evidence_code`, `category`, `publication_id`.
- **Camps Absents**: `qualifier`, `evidenceCode` (ECO), referències secundàries, `assigned_by`, `date`.
- **Biaixos i Limitacions**: Risc de falsos positius funcionals si la literatura conté anotacions de negació experimental (`NOT`).
- **Conclusió que Permet**: Estratificació de termes GO per codi d'evidència general (ALL vs EXP classic vs EXP+HTP).
- **Conclusió que NO Permet**: Garantir al 100% que cap terme de la cohort sigui una negació experimental documentada.
- **Reparació Mínima Necessària**: Filtrar les anotacions que històricament podrien contenir qualificadors `NOT`, o documentar-ho explícitament com a limitació metodològica heretada de la snapshot.

---

### Capacitat D: Comparació Reproduïble ALL versus EXP
- **Estat**: **BLOCKED** utilitzant el mòdul existent a `mfp-dataset-designer`; **PARTIAL** a nivell analític de dades SQL.
- **Evidència Observada**:
  - El mòdul `mfp_dataset_designer.metrics.go_similarity` importa una llibreria no instal·lada i absent (`CBBIO.GO`), fallant en la importació.
  - La classe `GOMetricsCalculator` invoca mètodes inexistents a `GOSimilarityCalculator` i captura silenciosament els errors retornant `0.0`.
  - Els tests de mètriques estan basats en mocks que retornen constants i mai han provat un càlcul real.
  - A nivell de dades a BioData, la separació ALL vs EXP és immediatament computable mitjançant SQL (`evidence_code IN ('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP')`), cobrint 1.800 proteïnes amb evidència clàssica i 1.814 amb EXP+HTP.
  - No hi ha cap separació d'aspectes GO (BP, MF, CC), la qual cosa distorsiona qualsevol similitud semàntica.
- **Cohort Aplicable**: 1.800 proteïnes amb evidència clàssica; 2.167 proteïnes per a ALL.
- **Camps Necessaris**: Subconjunts d'anotacions per proteïna filtrats per `evidence_code`, ontologia `go-basic.obo` versionada, motor semàntic funcional.
- **Camps Absents**: Motor de mètriques executable a `mfp-dataset-designer`.
- **Biaixos i Limitacions**: La cohort EXP redueix el nombre de termes per proteïna (de mitjana ~44 a ~18 termes), augmentant la probabilitat de proteïnes amb 0 o 1 terme (on les mètriques per parelles retornen 0).
- **Conclusió que Permet**: Comparació de recomptes i distribucions d'anotacions i cobertura de termes entre ALL i EXP.
- **Conclusió que NO Permet**: Càlcul directe de mètriques Resnik, Lin, Schlicker, Wang o Jiang amb el codi actual de `mfp-dataset-designer` sense un adaptador nou.
- **Reparació Mínima Necessària**: Implementar a `mfp-bibliography` un adaptador lleuger basat exclusivament en `goatools` (paquet estàndard ja instal·lat), amb separació estricta de subontologies (BP, MF, CC).

---

### Capacitat E: Anàlisi de Referències Bibliogràfiques
- **Estat**: **PARTIAL** (Auditoria de PMIDs a BioData **SUPPORTED**; Traçabilitat creuada amb fonts **PARTIAL**).
- **Evidència Observada**:
  - BioData conté 55.517 anotacions associades a 18.109 PMIDs numèrics únics.
  - 1.819 proteïnes tenen almenys una referència a BioData.
  - La distribució de PMIDs per proteïna presenta una mitjana de 14,58 articles en ALL i 12,77 en EXP (amb un màxim de 437 articles per a proteïnes com GAPDH o p53).
  - En les bases de dades d'origen, només MultitaskProtDB-II preserva referències directes (466 PMIDs únics).
  - El solapament entre els PMIDs de MultitaskProtDB-II i els de QuickGO a BioData és de només el **31,76% (148 de 466)**. El 68,24% dels articles citats per la font no apareixen a les anotacions GO de la proteïna.
- **Cohort Aplicable**: 1.819 proteïnes amb PMIDs a BioData; 602 proteïnes de MultitaskProtDB-II.
- **Camps Necessaris**: `publication_id` a BioData, `reference_raw` a `mfp_source_records.csv`.
- **Camps Absents**: PMIDs a MoonDB, MoonProt i MultifacetedProtDB; DOIs i enllaços d'articles complets.
- **Biaixos i Limitacions**: Fort biaix de recerca (*publication bias*): proteïnes intensament investigades concentren milers de termes i desenes de papers, mentre que proteïnes d'organismes model secundaris tenen 0 o 1 paper.
- **Conclusió que Permet**: Càlcul del nombre de PMIDs únics per proteïna, quantificació de l'esforç bibliogràfic independent d'IEA, i mesura del desacoblament entre literatura de multifuncionalitat i anotacions GOA.
- **Conclusió que NO Permet**: Afirmar que els articles de QuickGO demostren la multifuncionalitat de la proteïna.
- **Reparació Mínima Necessària**: Mantenir estrictament separats el recompte d'articles GOA de l'evidència de multifuncionalitat de la font.

---

### Capacitat F: Revisió del Suport Experimental a Funcions Diferents
- **Estat**: **BLOCKED** (Manca de relacions estructurades a les dades persistides).
- **Evidència Observada**:
  - Ni QuickGO ni BioData associen les anotacions GO a "funció canònica" versus "funció moonlighting/multifuncional". Totes les anotacions estan aplanades a `protein_go_term_annotation`.
  - Cap registre de BioData conté etiquetes de funció primària vs secundària.
  - A `mfp-bibliography`, d'acord amb la decisió arquitectural **ADR-007**, el graf de relacions bibliogràfiques article-funció va ser formalment **posposat** (*descoped/deferred*) per a versions posteriors a la v1.
- **Cohort Aplicable**: Cap (0% del corpus disposa d'aquest enllaç automàtic estructurat).
- **Camps Necessaris**: Esquema de relació ternària `(proteïna, funció_1, funció_2, article_suport_1, article_suport_2)`.
- **Camps Absents**: Absents a BioData i absents al catàleg MVP v0.3.0.
- **Biaixos i Limitacions**: La demostració que un sol polipèptid realitza dues funcions diferents requereix revisió per experts o mineria de textos especialitzada de les seccions de resultats dels articles.
- **Conclusió que Permet**: Cap conclusió automatitzada sobre la demostració simultània de funcions independents.
- **Conclusió que NO Permet**: No es pot inferir que un PMID que dóna suport a un terme GO doni suport a la condició multifuncional de la proteïna.
- **Reparació Mínima Necessària**: Dissenyar un protocol de curació manual dirigit per prioritats (subconjunt pilot de 50 proteïnes d'alt consens entre fonts).

---

## 3. Matriu Consolidada per Subcohorts

| Subcohort d'Anàlisi | N Proteïnes | A. Integritat Estructural | B. Traçabilitat Font | C. Evidència GO | D. ALL vs EXP Mètriques | E. Referències Bib. | F. Funcions Diferents |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Consens Multi-Font ($\ge 2$ fonts)** | 463 | SUPPORTED | SUPPORTED | PARTIAL | BLOCKED* | PARTIAL | BLOCKED |
| **Mono-Font Swiss-Prot (Revisat)** | 1.710 | SUPPORTED | SUPPORTED | PARTIAL | BLOCKED* | PARTIAL | BLOCKED |
| **Mono-Font TrEMBL / Mnemònics** | 149 | SUPPORTED | BLOCKED | BLOCKED | BLOCKED | BLOCKED | BLOCKED |
| **Amb Evidència Experimental (EXP)** | 1.800 | SUPPORTED | PARTIAL | PARTIAL | BLOCKED* | PARTIAL | BLOCKED |
| **MultitaskProtDB-II amb Papers** | 466 | SUPPORTED | SUPPORTED | PARTIAL | BLOCKED* | SUPPORTED | BLOCKED |
| **TOTAL CORPUS UNIFICAT** | **2.322** | **SUPPORTED** | **PARTIAL** | **PARTIAL** | **BLOCKED\*** | **PARTIAL** | **BLOCKED** |

*\*Nota*: BLOCKED degut al codi de `mfp-dataset-designer`, però desbloquejable immediatament mitjançant l'adaptador mínim de `goatools` proposat al Full de Ruta MVP.

