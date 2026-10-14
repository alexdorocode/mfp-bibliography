# Auditoria Tècnica: Extracció, Normalització, Unificació i Persistència del Corpus de Proteïnes Multifuncionals (MFP)

- **Auditor**: Auditor Tècnic Senior de Pipelines Bioinformàtics, Investigador en Multifuncionalitat Proteica i Arquitecte de Sistemes d'Experimentació Científica Reproduïble
- **Data de l'Auditoria**: 2026-10-14
- **Abast**: Repositoris `mfp-bibliography`, `protein-information-system` (PIS), `mfp-dataset-designer` i instància viva de la base de dades PostgreSQL `BioData`.
- **Estat de la Verificació**: AUDITORIA COMPLETADA AMB INSPECCIÓ DIRECTA DE CODI I DADES VIVES (sense modificacions, consultes de només lectura).

---

## 1. Marc d'Auditoria i Objectius

Aquesta auditoria examina la cadena completa de processament de dades bioinformàtiques per a proteïnes atribuïdes com a multifuncionals (MFP), des dels fitxers originals dels cinc repositoris de referència fins a la seva persistència a la base de dades `BioData`, l'extracció d'anotacions funcionals mitjançant QuickGO i el mòdul de càlcul de mètriques semàntiques de Gene Ontology (GO).

### Distinció Epistemològica Fonamental
- **Observat**: Dades, codi, esquemes, claus i comportaments verificats directament mitjançant inspecció de codi font i execució de consultes SQL de només lectura sobre la base de dades activa.
- **Inferit**: Deduccions lògiques basades en la comparació entre disseny documentat (contractes, docstrings) i comportament real mesurat.
- **Proposat**: Accions correctives, adaptadors o protocols mínims requerits per assolir reproduïbilitat cientificotècnica.

### Advertiments Crítics de Domini Biopericial
1. **Absència d'anotació experimental no implica absència de funció**: La manca d'anotacions GO experimentals reflecteix el biaix d'anotació de la literatura i el finançament biomèdic, no la monofuncionalitat d'un polipèptid.
2. **Volum d'anotacions o PMIDs no és prova de multifuncionalitat**: Proteïnes intensament estudiades (com p53 o GAPDH) acumulen centenars d'articles degut al biaix de recerca històric (*research bias*). La multifuncionalitat requereix la demostració de funcions bioquímiques o fisiològiques fisiològicament autònomes i molecularment diferents.

---

## 2. Fase 1: Localització, Arquitectura i Reconstrucció del Sistema

### 2.1 Repositoris i Localitzacions Reals

L'ecosistema analitzat s'estructura en tres repositoris complementaris a `/home/alexdoro/repositories/`:

1. **`mfp-bibliography`** (`branch: moonprot-offline-preparation`, commit `700c1890e2f02703e4a1070a350054c2e88ef07f`):
   - Responsable de la recepció immutabilitzada dels catàlegs raw, extracció de registres d'origen, normalització d'identificadors UniProt, unificació d'entitats proteiques i governança del catàleg (`releases/mfp-catalog-candidate-v0.3.0`).
2. **`protein-information-system` (PIS)** (`branch: feature/quickgo-annotations-v2`):
   - Sistema operatiu d'extracció de dades massives, gestió de cues RabbitMQ, models ORM SQLAlchemy i persistència relacional a PostgreSQL (`BioData`).
3. **`mfp-dataset-designer`** (`branch: develop-standardizing-0`):
   - Mòdul encarregat del filtratge de cohorts, adaptadors de lectura de BioData, càlcul de mètriques de distància/similitud semàntica GO i generació de conjunts de dades positius/control.

### 2.2 Reconstrucció del Flux de Dades Extrem a Extrem

```
[Font Original: 5 DBs]
   │
   ▼ (Descàrrega manual / snapshot local)
[Registres Raw] (TSV, JSON, CSV, HTML)
   │
   ▼ [Parsers de Font / Adapters: mfp_bibliography]
   ├─ MoonDB: all_emf_and_curated.tsv -> source_claims_moondb.csv
   ├─ PlantMP: PlantMP_all.csv -> source_claims_plantmp.csv
   ├─ MoonProt: mpid_*.html -> moonprot_parser.py -> SourceRecord
   ├─ MultifacetedProtDB: MultifacetedProtDB_data.json -> multifacetedprotdb_records.py
   └─ MultitaskProtDB-II: proteins.csv -> multitaskprotdb_ii_records.py
   │
   ▼ [Normalització d'Identificadors: mfp_bibliography.normalization]
   │  - Stripping de prefixos, validació d'accession UniProt [A-NR-Z][0-9][A-Z][A-Z0-9]{3}[0-9]
   │  - Generació de protein_id determinista (MFPB_PROTEIN_ID_V1)
   │
   ▼ [Unificació i Deduplicació: scripts/build_mfp_catalog_mvp.py]
   │  - Agrupació per accession canònic UniProt -> mfp_proteins.csv (2.322 entitats)
   │
   ▼ [Importació a BioData: PIS AccessionManager]
   │  - Lectura de mfp_proteins.csv -> Inserció a taula public.accession (2.321 + 9 = 2.330 files)
   │
   ▼ [Extracció UniProt: PIS UniProtExtractor]
   │  - Descàrrega SwissProt via Bio.ExPASy.get_sprot_raw
   │  - Creació de public.protein (2.182 files, indexades per entry_name)
   │  - Creació de public.sequence (2.160 seqüències úniques)
   │  - Enllaç accession.protein_id = protein.id (2.182 enllaçats, 148 orfes)
   │
   ▼ [Extracció QuickGO: PIS QuickGOAnnotationExtractor]
   │  - Consulta REST API QuickGO per geneProductId=UniProtKB:{code}
   │  - Filtratge d'accessions amb protein_id IS NOT NULL
   │  - Inserció a public.go_terms (9.376 termes)
   │  - Inserció a public.protein_go_term_annotation (96.186 anotacions)
   │
   ▼ [Càlcul de Mètriques: mfp-dataset-designer]
      - GOSimilarityCalculator / GOMetricsCalculator (INEXECUTABLE / DEPENDÈNCIA TRENCADA)
```

### 2.3 Components, Símbols i Localitzacions

| Etapa | Component / Mòdul | Símbol / Funció | Fitxer i Línies |
| :--- | :--- | :--- | :--- |
| **Parser MoonProt** | `mfp_bibliography.moonprot_parser` | `parse_moonprot_html` | [`moonprot_parser.py#L125-L210`](file:///home/alexdoro/repositories/mfp-bibliography/src/mfp_bibliography/moonprot_parser.py#L125-L210) |
| **Parser MultifacetedProtDB** | `mfp_bibliography.multifacetedprotdb_records` | `parse_literal_payload`, `load_source_records` | [`multifacetedprotdb_records.py#L49-L125`](file:///home/alexdoro/repositories/mfp-bibliography/src/mfp_bibliography/multifacetedprotdb_records.py#L49-L125) |
| **Normalització Accessions** | `mfp_bibliography.normalization` | `normalize_uniprot_accession`, `make_protein_id_uniprot` | [`normalization.py#L25-L75`](file:///home/alexdoro/repositories/mfp-bibliography/src/mfp_bibliography/src/mfp_bibliography/normalization.py) |
| **Constructor Catàleg** | `scripts.build_mfp_catalog_mvp` | `load_moondb_claims`, `load_plantmp_claims`, `build_coverage` | [`build_mfp_catalog_mvp.py#L205-L420`](file:///home/alexdoro/repositories/mfp-bibliography/scripts/build_mfp_catalog_mvp.py#L205-L420) |
| **Carregador Accessions PIS** | `AccessionManager` | `load_accessions_from_csv`, `_process_new_accessions` | [`accessions.py#L76-L183`](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/accessions.py#L76-L183) |
| **Extractor UniProt PIS** | `UniProtExtractor` | `process`, `store_entry`, `get_or_create_protein` | [`uniprot.py#L116-L230`](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/uniprot.py#L116-L230) |
| **Extractor QuickGO PIS** | `QuickGOAnnotationExtractor` | `enqueue`, `_fetch_all_annotations`, `store_entry` | [`quick_go_extractor.py#L89-L355`](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L89-L355) |
| **Models ORM BioData** | SQLAlchemy Entities | `Accession`, `Protein`, `GOTerm`, `ProteinGOTermAnnotation` | [`quick_go_extractor.py#L8-L12`](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L8-L12) |
| **Adaptador BioData** | `mfp_dataset_designer.cohort.biodata_adapter` | `validate_sql_query`, `adapt_biodata_row` | [`biodata_adapter.py#L65-L280`](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/cohort/biodata_adapter.py#L65-L280) |
| **Mòdul Mètriques GO** | `mfp_dataset_designer.metrics.go_similarity` | `GOSimilarityCalculator` | [`go_similarity.py#L17-L280`](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_similarity.py#L17-L280) |
| **Calculador Mètriques GO** | `mfp_dataset_designer.metrics.go_calculator` | `GOMetricsCalculator` | [`go_calculator.py#L34-L240`](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_calculator.py#L34-L240) |

---

## 3. Fase 2: Auditoria de l'Extracció QuickGO i Persistència a BioData

L'auditoria del codi font de [`QuickGOAnnotationExtractor`](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py) i de les 96.186 files persistides a la taula `protein_go_term_annotation` de `BioData` revela serioses discrepàncies entre la documentació declarada i el comportament real:

### 3.1 Paràmetres d'Extracció i Endpoint
- **Endpoint**: `https://www.ebi.ac.uk/QuickGO/services/annotation/search` ([L33](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L33)).
- **Paràmetres utilitzats**:
  - `geneProductId`: `UniProtKB:{normalized_accession}` ([L152](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L152)).
  - `includeFields`: `"goName"` ([L201](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L201)).
  - `limit`: `page_size` (configurat a 100) ([L202](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L202)).
  - `page`: paginació incremental $1, 2, \dots$ fins a `len(annotations) >= numberOfHits` o `page_results` buit ([L217-L235](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L217-L235)).
- **Resiliència HTTP**: Implementa `urllib3.util.Retry` amb 5 reintents, backoff exponencial factor 1.0 per codis d'estat 429, 500, 502, 503, 504 ([L60-L69](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L60-L69)).

### 3.2 Falsedat Documental en el Docstring de `store_entry`
- **Declarat al docstring** ([L243-L244](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L243-L244)):
  > *"Annotations whose reference is not a PMID are skipped and are not inserted into ProteinGOTermAnnotation."*
- **Comportament real al codi** ([L300-L330](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L300-L330)):
  El mètode `extract_publication_id` retorna `None` si la referència no comença per `PMID:`. L'objecte `ProteinGOTermAnnotation` és creat i inserit amb `publication_id = None`.
- **Dada empírica verificada a BioData**:
  - Total anotacions: **96.186**
  - Anotacions amb `publication_id` no nul: **55.517 (57,72%)**
  - Anotacions amb `publication_id IS NULL`: **40.669 (42,28%)**
  - *Conclusió*: **40.669 anotacions sense PMID no van ser descartades**, sinó persistides amb referència nul·la.

### 3.3 Pèrdua Crítica de Qualifiers i Qualificadors Negatius (`NOT`)
- **Vulnerabilitat Biològica Crítica**: El camp `qualifier` de QuickGO (p. ex. `NOT`, `enables`, `contributes_to`, `involved_in`) **no és ni tan sols llegit pel parser** ([L278-L330](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L278-L330)).
- **Impacte**: Una anotació de recerca que hagi determinat experimentalment que una proteïna **NO** té activitat cinasa (`qualifier = "NOT"`, `go_id = "GO:0004672"`) s'ha desat a la base de dades exactament igual que una anotació positiva. Aquest és un risc **BLOCKER** per a qualsevol estudi de multifuncionalitat si no es corregeix o filtra.

### 3.4 Pèrdua i Truncament de Referències
- El mètode `extract_publication_id` ([L437-L457](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L437-L457)):
  1. Si `reference` és una llista de múltiples referències (p. ex. `["PMID:12345", "PMID:67890"]`), **només retorna el primer element** (`return publication_id` a L447). Totes les publicacions posteriors es perden definitivament.
  2. Si la referència és un identificador que no és PubMed (p. ex. `GO_REF:0000002` o `DOI:10.1016/...`), el valor s'esborra i es desa com a `NULL`.
  3. Elimina el prefix `PMID:`, desant únicament la cadena numèrica a la columna `publication_id` (VARCHAR).

### 3.5 Matriu de Cicles de Vida dels Camps QuickGO

| Camp API QuickGO | Llegit pel Parser? | Persistit a BioData? | Exportable per a Anàlisi? | Destí / Motiu de Pèrdua |
| :--- | :--- | :--- | :--- | :--- |
| `geneProductId` | Sí | Sí | Sí | Taula `accession.code` / enllaç a `protein.id` |
| `goId` | Sí | Sí | Sí | Columna `protein_go_term_annotation.go_id` |
| `goName` | Sí | Sí | Sí | Columna `go_terms.description` |
| `goAspect` | Sí | Sí | Sí | Columna `go_terms.category` |
| `goEvidence` | Sí | Sí | Sí | Columna `protein_go_term_annotation.evidence_code` |
| `evidenceCode` (ECO) | Opcional | **NO** | **NO** | Ignorat (només filtrat si s'especifica a conf) |
| `qualifier` (NOT) | **NO** | **NO** | **NO** | **PERDUT TOTALMENT** (Greu anomalia) |
| `reference` (PMID) | Sí (primer) | Sí (numèric) | Sí | Columna `publication_id` (prefix suprimit) |
| `reference` (no-PMID) | Sí | **NO** | **NO** | **PERDUT** (Convertit en `NULL`) |
| `reference` (múltiples) | Sí | Parcial (1r) | Parcial | **PERDUTS** elements 2..N |
| `assignedBy` | **NO** | **NO** | **NO** | PERDUT |
| `date` | **NO** | **NO** | **NO** | PERDUT |
| `extensions` | **NO** | **NO** | **NO** | PERDUT |
| `withFrom` | **NO** | **NO** | **NO** | PERDUT |
| `taxonId` | **NO** | **NO** | **NO** | PERDUT (S'assumeix el de la proteïna) |

### 3.6 Temporalitat i Homogeneïtat Temporal
- Totes les files de `accession` i `protein` van ser creades en una finestra de 12 minuts: **2026-10-13 13:07:54 a 13:19:30 UTC**.
- La base de dades viva reflecteix una extracció en bloc executada en una única sessió de cues RabbitMQ.
- **Limitació**: No es conserven els JSONs de resposta raw de QuickGO ni logs d'auditoria per transacció; la reconstrucció depèn exclusivament de l'estat persistit a la base de dades.

---

## 4. Fase 3: Auditoria d'Identitat, Unificació i Procedència

### 4.1 Semàntica Real de les Sis Taules Principals de BioData

```
┌─────────────────────────┐           ┌────────────────────────┐
│        accession        │           │        protein         │
├─────────────────────────┤           ├────────────────────────┤
│ code (PK, varchar)      │           │ id (PK, entry_name)    │◄───┐
│ primary (boolean)       │           │ sequence_id (FK, int)  │    │
│ tag (varchar)           │           │ organism (varchar)     │    │
│ protein_id (FK) ────────┼──────────►│ taxonomy_id (varchar)  │    │
│ created_at / updated_at │           │ data_class (varchar)   │    │
└─────────────────────────┘           └───────────┬────────────┘    │
                                                  │                 │
                                                  ▼                 │
┌─────────────────────────┐           ┌────────────────────────┐    │
│        sequence         │           │protein_go_term_annot...│    │
├─────────────────────────┤           ├────────────────────────┤    │
│ id (PK, int)            │◄──────────┤ id (PK, int)           │    │
│ sequence (varchar)      │           │ protein_id (FK) ───────┼────┘
│ sequence_hash (varchar) │           │ go_id (FK) ────────────┼────┐
└─────────────────────────┘           │ evidence_code (varchar)│    │
                                      │ publication_id (varch.)│    │
                                      └────────────────────────┘    │
┌─────────────────────────┐                                         │
│          chain          │           ┌────────────────────────┐    │
├─────────────────────────┤           │        go_terms        │    │
│ id (PK, int)            │           ├────────────────────────┤    │
│ name / structure_id     │           │ go_id (PK, varchar)    │◄───┘
│ sequence_id (FK)        │           │ category (varchar)     │
│ accession_code (FK)     │           │ description (varchar)  │
└─────────────────────────┘           └────────────────────────┘
```

1. **`protein.id` no és un Accession UniProt**:
   - `protein.id` emmagatzema l'Entry Name mnemònic de SwissProt (p. ex. `P53_HUMAN` o `HIS4_ARATH`), **NO** l'accession alfanumèric canònic (`P04637`).
2. **Cardinalitat `accession` $\to$ `protein`**:
   - Relació molts-a-un. Múltiples accessions (p. ex. accessions secundaris o obsolets) poden apuntar al mateix `protein.id`.
3. **Taula `chain`**: Té exactament **0 files**. Tota la informació estructural de cadenes PDB està absent en aquesta snapshot.
4. **Taula `sequence`**: 2.160 files. Diferència amb proteïnes ($2.182 - 2.160 = 22$): 22 proteïnes comparteixen seqüència idèntica amb una altra entrada a la base de dades.

### 4.2 L'Anomalia dels 148 Accessions No Enllaçats i la Caiguda de TrEMBL

L'auditoria de la taula `accession` ha revelat que dels 2.330 accessions:
- **2.182** estan enllaçats a una proteïna (`protein_id IS NOT NULL`).
- **148** tenen `protein_id IS NULL`.

Aquesta pèrdua d'un 6,4% de la cohort s'explica per dues causes tècniques identificades al codi:

1. **Dependència estricta de Swiss-Prot via `Bio.ExPASy.get_sprot_raw`** ([L134](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/uniprot.py#L134)):
   - `UniProtExtractor` intenta descarregar únicament entrades revisades (Swiss-Prot). Per a proteïnes que només existeixen a TrEMBL (sense revisar) o amb accessions obsolets no redirigits, BioPython llença `ValueError("No SwissProt record found...")`.
   - L'error s'atrapa, la tasca s'aborta i l'accession roman a la base de dades amb `protein_id = NULL`. Això afecta **133 accessions**.
2. **Desajust de Mnemònics de MoonProt (15 accessions)**:
   - MoonProt va bolcar mnemònics bruts barrejats amb text (p. ex. `A0A0H2US80_STRPN`). `UniProtExtractor` va resoldre l'accession canònic `A0A0H2US80`, però va inserir una fila nova a `accession` per al codi canònic i va deixar la fila original (`A0A0H2US80_STRPN`) amb `protein_id = NULL`.
3. **Impacte en l'extracció QuickGO**:
   - Com que `QuickGOAnnotationExtractor.enqueue()` filtra expressament `Accession.protein_id.isnot(None)` ([L98](file:///home/alexdoro/repositories/protein-information-system/protein_information_system/operation/extraction/quick_go_extractor.py#L98)), **cap d'aquests 148 accessions no va ser mai consultat a QuickGO**.

### 4.3 Reconciliació Numèrica Completa per Font

A continuació es detalla la reconciliació empírica pas a pas:

```
Fonts Raw (2.962 registres)
   │
   ├── MoonDB: 351 registres raw -> 351 accessions únics -> 351 entitats unificades
   ├── MoonProt: 702 registres raw -> 657 accessions únics (45 observacions repetides)
   ├── MultifacetedProtDB: 1.103 registres raw -> 1.103 accessions únics
   ├── MultitaskProtDB-II: 694 registres raw -> 685 accessions únics (9 obs. repetides)
   └── PlantMP: 112 registres raw -> 110 accessions únics (2 obs. repetides)
   │
   ▼ Deduplicació Inter-Fonts: 463 accessions compartits per >= 2 fonts
[Entitats Proteiques Canòniques Unificades al Catàleg]: 2.322
   │
   ├── Inserits a BioData Accession: 2.321 (1 accession invàlid "NA" descartat)
   ├── Accessions afegits per UniProtExtractor: +9 (accessions primaris resolts)
   └── Total Accession a BioData: 2.330
   │
   ├── Resolució SwissProt fallida (TrEMBL/obsolets/mnemònics): -148
   └── Entitats Proteiques Persistides a BioData: 2.182 (2.173 del catàleg + 9 secundàries)
   │
   ├── Proteïnes sense cap anotació a QuickGO: -15
   └── Entitats Proteiques amb Anotacions GO: 2.167 (2.158 del catàleg)
   │
   ├── Entitats amb Anotacions GO Experimentals (EXP classic): 1.800 (1.796 del catàleg)
   ├── Entitats amb Anotacions GO Exp + HTP: 1.814 (1.810 del catàleg)
   └── Entitats amb Referències Bibliogràfiques (PMID): 1.819 (1.815 del catàleg)
```

#### Taula de Reconciliació per Font Original

| Font Original | Registres Raw | Accessions Únics | Entitats Canòniques (Catàleg) | Resolts a BioData Protein | Amb Anotacions GO | Amb Evidència EXP | Amb Referències (PMID) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SRC_MOONDB** | 351 | 351 | 351 | 351 (100%) | 351 (100%) | 346 (98,6%) | 348 (99,1%) |
| **SRC_MOONPROT** | 702 | 657 | 657 | 580 (88,3%) | 579 (88,1%) | 429 (65,3%) | 430 (65,4%) |
| **SRC_MULTIFACETEDPROTDB** | 1.103 | 1.103 | 1.103 | 1.103 (100%) | 1.103 (100%) | 1.068 (96,8%) | 1.075 (97,5%) |
| **SRC_MULTITASKPROTDB_II** | 694 | 685 | 685 | 602 (87,9%) | 591 (86,3%) | 412 (60,1%) | 414 (60,4%) |
| **SRC_PLANTMP** | 112 | 110 | 110 | 108 (98,2%) | 104 (94,5%) | 68 (61,8%) | 76 (69,1%) |
| **TOTAL CATÀLEG (ÚNIC)** | **2.962** | **2.322** | **2.322** | **2.173 (93,6%)** | **2.158 (92,9%)** | **1.796 (77,3%)** | **1.815 (78,2%)** |

*Definició de termes*:
- *Observació repetida (intra-font)*: Múltiples files de la mateixa base de dades que declaren el mateix accession UniProt per a diferents funcions o isoformes.
- *Solapament inter-font*: Un mateix accession atribuït simultàniament per 2 o més bases de dades independents (463 accessions).

---

## 5. Fase 4: Auditoria del Motor de Mètriques Semàntiques GO

L'auditoria dels fitxers [`go_similarity.py`](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_similarity.py) i [`go_calculator.py`](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_calculator.py) a `mfp-dataset-designer` ha determinat que el mòdul de mètriques és **INEXECUTABLE** en el seu estat actual:

### 5.1 Diagnosi Tècnica de Fallada
1. **Dependència Inexistent (`CBBIO.GO`)**:
   - `go_similarity.py` línia 14 conté: `from CBBIO.GO import GOOntology`.
   - El paquet `CBBIO` no està instal·lat, no està a PyPI, no és submòdul git ni existeix al disc.
   - La seva importació falla immediatament amb `ModuleNotFoundError: No module named 'CBBIO'`.
2. **Incoherència de Signatura d'API**:
   - `go_calculator.py` invoca mètodes a `GOSimilarityCalculator` que **no existeixen**:
     - `compute_similarity_matrix(...)` ([L100](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_calculator.py#L100))
     - `get_term_mbl(...)` ([L132](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_calculator.py#L132))
     - `compute_similarity(...)` ([L215](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_calculator.py#L215))
3. **Emmudiment d'Errors Silenciós**:
   - Totes les crides estan embolicades en blocs `try...except Exception` que atrapen l'error, escriuen un warning i **retornen 0.0 de forma silenciosa** ([L122-L126](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_calculator.py#L122-L126)). Si s'executés, el codi produiria matrius buides de zeros sense fallar explícitament.
4. **Falta de Tests Reals (Mocking Total)**:
   - A `tests/test_pec_metrics.py`, tots els tests decoren les proves amb:
     `@patch("src.pec.metrics.go_similarity.HAS_CBBIO", True)` i `@patch("src.pec.metrics.go_similarity.GOOntology")`.
     Totes les crides a similituds retornen valors mockejats fixos (`0.8`, `0.5`).
   - No s'ha executat mai cap test amb termes GO reals ni amb fitxers `.obo` reals.

### 5.2 Avaluació per Mètrica Declarada

| Mètrica | Implementada? | Executable? | Testada? | Utilitzable per a ALL vs EXP? | Fórmula / Variant Exacta | Tipus de Mesura |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Resnik** | Stub | **NO** | Mock | **NO** | $IC(MICA)$ (delegada a CBBIO) | Similitud $[0, \infty)$ |
| **Lin** | Stub | **NO** | Mock | **NO** | $\frac{2 \cdot IC(MICA)}{IC(c_1) + IC(c_2)}$ | Similitud $[0, 1]$ |
| **Schlicker** | Stub | **NO** | Mock | **NO** | Lin $\cdot (1 - e^{-IC(MICA)})$ | Similitud $[0, 1]$ |
| **Jiang-Conrath**| Stub | **NO** | Mock | **NO** | No implementada a `go_similarity.py` | Distància / Similitud |
| **Wang (GOGO)** | Stub | **NO** | Mock | **NO** | Basada en graf DAG (pes semàntic $S_A(t)$) | Similitud $[0, 1]$ |
| **MBL** | Stub | **NO** | Mock | **NO** | Minimal Branch Length (camí més curt al DAG) | **Distància** $[0, \infty)$ |

### 5.3 Problemes Metodològics Estructurals
1. **Confusió de Similitud i Distància**:
   - A `go_similarity.py` ([L278](file:///home/alexdoro/repositories/mfp-dataset-designer/src/mfp_dataset_designer/metrics/go_similarity.py#L278)), el codi calcula `score = abs(sim_wang_avg - mbl_avg)`, restant una distància entera/decimal (MBL) d'una similitud normalitzada entre 0 i 1 (Wang). Això manca de sentit mètric dimensional.
2. **Mescla de Subontologies (BP, MF, CC)**:
   - No hi ha cap separació de namespaces. Els termes de Biological Process, Molecular Function i Cellular Component es barregen en una única llista per proteïna. El càlcul de similitud semàntica entre un terme BP i un terme MF no està definit ontològicament (tenen arrels diferents sense MICA comú).
3. **Càlcul d'Information Content (IC)**:
   - No existeix cap mecanisme de recàlcul d'IC separat per a la cohort ALL versus la cohort EXP.

---

## 6. Fase 5: Auditoria de Referències Bibliogràfiques i Recomptes de Papers

### 6.1 Naturalesa de les Referències
- **BioData (`protein_go_term_annotation`)**:
  - Les referències són **exclusivament PMIDs numèrics** (55.517 files).
  - Totes les referències no-PMID (DOIs, `GO_REF`, Reactome) van ser descartades per l'extractor.
  - Per a anotacions amb múltiples publicacions, només es va conservar la primera.
- **Bases de Dades Font (Catàleg MFP)**:
  - MoonDB: 0 referències (no incloses al TSV de descàrrega).
  - MoonProt: 0 referències extretes (l'extractor offline descarta l'HTML de referències).
  - MultifacetedProtDB: 0 referències (no presents a l'objecte JSON).
  - PlantMP: 112 referències al fitxer raw `PlantMP_all.csv`, però no traslladades a `source_claims_plantmp.csv`.
  - MultitaskProtDB-II: 694 files, de les quals 691 contenen PMIDs numèrics directes i 3 contenen anomalies de text (OMIM, PDB).

### 6.2 Estadístiques Bibliogràfiques Mesurades a BioData

| Mètrica Bibliogràfica | Valor Observat a BioData | Observacions / Biaixos |
| :--- | :--- | :--- |
| **Total Anotacions GO** | 96.186 | 100% de la snapshot |
| **Anotacions amb PMID** | 55.517 (57,72%) | La resta (42,28%) té `publication_id IS NULL` |
| **PMIDs Únics Totals a GO** | 18.109 articles | Identificadors PubMed únics |
| **PMIDs Únics per Proteïna (ALL)** | Mitjana: **14,58** \| Mediana: **7,0** (Min: 0, Max: 437) | 348 proteïnes tenen 0 PMIDs a GO |
| **PMIDs Únics per Proteïna (EXP)** | Mitjana: **12,77** \| Mediana: **6,0** (Min: 0, Max: 432) | 370 proteïnes tenen 0 PMIDs experimentals |
| **Termes GO sostinguts per PMID** | Mitjana: **2,17** \| Mediana: **1,0** (Min: 1, Max: 20) | La majoria d'articles donen suport a 1 o 2 termes |
| **Parella (Proteïna, Terme) amb PMID**| 27.072 associacions úniques | Mitjana de 2,03 articles per terme en una proteïna |
| **Parelles amb Suport Multi-Paper** | 7.536 associacions (27,84%) | $\ge 2$ articles independents per a la mateixa funció |
| **Solapament Font vs GO (MultitaskProtDB-II)**| **148 de 466 PMIDs (31,76%)** | **68,24% dels articles citats per la font no són a QuickGO** |

---

## 7. Classificació de Riscos de l'Ecosistema

| Id Risc | Gravetat | Component Afectat | Descripció del Risc | Mitigació Requerida |
| :--- | :---: | :--- | :--- | :--- |
| **RSK-01** | **BLOCKER** | `mfp-dataset-designer` | Mòdul de mètriques GO inexecutable per dependència fantasma `CBBIO.GO`. | Substitució per un motor basat directament en `goatools` pur. |
| **RSK-02** | **BLOCKER** | QuickGO Extractor | Ignorància total del qualificador `NOT`, tractant negacions com a funcions positives. | Descartar files històriques no auditables o marcar com a caveat d'anàlisi. |
| **RSK-03** | **HIGH** | PIS UniProtExtractor | Pèrdua del 6,4% de la cohort (148 proteïnes) degut al fracàs amb entrades TrEMBL i mnemònics. | Resolució d'accessions TrEMBL via REST API d'UniProtKB. |
| **RSK-04** | **HIGH** | `mfp_dataset_designer` | Manca de separació d'aspectes GO (BP, MF, CC), barrejant ontologies no comparables. | Estratificació de l'anàlisi mètrica separadament per subontologia. |
| **RSK-05** | **MEDIUM** | QuickGO Extractor | Truncament de referències múltiples i descartament de referències no-PMID. | Documentar que els recomptes de literatura representen cotes inferiors. |
| **RSK-06** | **MEDIUM** | Catàleg Font | 68,2% de desacoblament entre els articles de les fonts i les anotacions GO. | Mantenir separats els papers d'atribució MFP dels papers d'anotació GO. |

