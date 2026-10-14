# Full de Ruta MVP: Anàlisi Descriptiva Reproduïble de Proteïnes Multifuncionals (MFP) a `mfp-bibliography`

- **Autor**: Auditor Tècnic Senior de Pipelines Bioinformàtics, Investigador en Multifuncionalitat Proteica i Arquitecte de Sistemes d'Experimentació Científica Reproduïble
- **Data**: 2026-10-14
- **Repositori Objectiu**: `/home/alexdoro/repositories/mfp-bibliography`
- **Estat**: PLA D'EXPERIMENTACIÓ LLEUGER I DETERMINISTA (Sense dependències d'APIs externes)

---

## 1. Resum Executiu

### 1.1 Què podem analitzar avui (amb dades locals i snapshot existent)
1. **La cohort unificada de 2.322 proteïnes MFP** (`mfp_catalog_mvp`), amb traçabilitat completa als 2.962 registres de les 5 bases de dades de referència.
2. **La persistència real a BioData de 2.173 proteïnes del catàleg**, amb 96.186 anotacions GO i 9.376 termes GO.
3. **La distribució empírica de codis d'evidència GO**, comparant la cohort completa (**ALL**: 2.158 proteïnes amb GO) enfront del subconjunt amb evidència experimental clàssica (**EXP**: 1.796 proteïnes) i experimental d'alt rendiment (**EXP+HTP**: 1.810 proteïnes).
4. **La bibliometria associada a les anotacions GO**, analitzant 55.517 anotacions sostingudes per 18.109 PMIDs únics (mitjana de 14,58 articles/proteïna en ALL i 12,77 en EXP).
5. **El grau de desacoblament bibliogràfic**: Demostració empírica que el 68,24% dels articles citats a MultitaskProtDB-II no apareixen en cap anotació GO a BioData.

### 1.2 Què NO podem concloure (ni s'ha d'afirmar a l'article)
1. **No es pot concloure que una proteïna sense anotacions GO experimentals sigui monofuncional**: 362 proteïnes del catàleg a BioData no tenen codis EXP a causa del biaix d'estudi històric (*annotation lag*).
2. **No es pot concloure que molts PMIDs o moltes anotacions provin multifuncionalitat**: GAPDH (437 PMIDs) o p53 reflecteixen hiper-recerca mèdica, no necessàriament més funcions moleculars discretes.
3. **No es pot afirmar que les anotacions actuals estiguin lliures d'afirmacions negatives**: A causa de la pèrdua del qualificador `NOT` durant l'extracció QuickGO, no es pot garantir l'absència de negacions funcionals.
4. **No es pot determinar de forma automàtica quin PMID dóna suport a quina de les funcions multifuncionals**: Les dades actuals no vinculen articles amb la funció canònica versus la funció *moonlighting*.

### 1.3 Què falta per començar
1. **Exportar i congelar una snapshot reproducible de BioData** (dump consistent `.sql` / `.dump` i manifest SHA-256).
2. **Implementar un adaptador mínim de similitud semàntica GO a `mfp-bibliography`** basat directament en `goatools` pur, substituint el mòdul trencat de `mfp-dataset-designer`.
3. **Descarregar i congelar el fitxer d'ontologia `go-basic.obo`** amb checksum SHA-256 fixat al repositori.

### 1.4 Les Cinc Accions Següents Immediates
1. **Executar el dump i manifest de snapshot de BioData** (`pg_dump` PostgreSQL 16 aïllat).
2. **Generar els fitxers Parquet/CSV analítics a `data/processed/biodata_snapshot_v1/`** mitjançant consulta SQL de només lectura.
3. **Crear l'adaptador autònom `src/mfp_bibliography/metrics/go_similarity_adapter.py`** (utilitzant `goatools` i separant BP, MF i CC).
4. **Executar la comparació de mètriques ALL versus EXP** sobre les 1.796 proteïnes comunes amb evidència experimental.
5. **Generar les taules de cobertura bibliogràfica i els primers 3 gràfics descriptius de la cohort**.

---

## 2. Fase 7: Pla de Snapshot Relacional i Integritat de Dades

El pla de snapshot congela l'estat exacte de la base de dades PostgreSQL `BioData` sense alterar la base de dades viva.

### 2.1 Especificació Tècnica del Dump
- **Motor i Versió**: PostgreSQL 16.13 (Debian 16.13-1.pgdg12+1) x86_64.
- **Client**: `pg_dump (PostgreSQL) 16.13`.
- **Comanda d'execució (sense bloqueig de taules)**:
  ```bash
  docker exec pgvectorsql pg_dump \
    -U usuario \
    -d BioData \
    --format=custom \
    --compress=6 \
    --no-owner \
    --no-privileges \
    --table=public.accession \
    --table=public.protein \
    --table=public.sequence \
    --table=public.go_terms \
    --table=public.protein_go_term_annotation \
    --file=/tmp/biodata_mfp_snapshot_20261014.dump
  
  # Copiar fora del contenidor cap a la ubicació d'arxiu
  docker cp pgvectorsql:/tmp/biodata_mfp_snapshot_20261014.dump \
    releases/snapshots/biodata_mfp_snapshot_20261014.dump
  ```

### 2.2 Inventari d'Artefactes i Metadades del Manifest

El fitxer de metadades `releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json` registrarà:
- `snapshot_id`: `"biodata_mfp_snapshot_20261014_v1"`
- `server_version`: `"PostgreSQL 16.13"`
- `created_at`: `"2026-10-14T09:30:00Z"`
- `git_commits`:
  - `mfp-bibliography`: `700c1890e2f02703e4a1070a350054c2e88ef07f`
  - `protein-information-system`: `feature/quickgo-annotations-v2`
  - `mfp-dataset-designer`: `develop-standardizing-0`
- `table_row_counts`:
  - `accession`: 2.330
  - `protein`: 2.182
  - `sequence`: 2.160
  - `go_terms`: 9.376
  - `protein_go_term_annotation`: 96.186
  - `chain`: 0
- `input_catalog_sha256`: `a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc` (`mfp_proteins.csv`)
- `ontology_source`: `go-basic.obo` (Gene Ontology Consortium, data de descàrrega i SHA-256)

### 2.3 Protocol de Restauració en Base de Dades Aïllada
Per verificar la reproductibilitat, el dump serà restaurat en una base de dades aïllada de test:
```bash
docker exec pgvectorsql createdb -U usuario BioData_Isolated_Test
docker exec pgvectorsql pg_restore -U usuario -d BioData_Isolated_Test \
  --clean --if-exists /tmp/biodata_mfp_snapshot_20261014.dump

# Consulta de verificació de consistència
docker exec pgvectorsql psql -U usuario -d BioData_Isolated_Test -c "
SELECT 'accession' AS t, count(*) FROM accession UNION ALL
SELECT 'protein', count(*) FROM protein UNION ALL
SELECT 'go_terms', count(*) FROM go_terms UNION ALL
SELECT 'protein_go_term_annotation', count(*) FROM protein_go_term_annotation;
"
```

### 2.4 Declaració de Límit Temporal
> **Important**: Aquesta snapshot és una captura d'estat de les taules persistides a data 2026-10-13/14. No constitueix una reconstrucció històrica de les respostes HTTP de l'API QuickGO, les quals no es van enregistrar raw en el moment de l'execució del pipeline PIS.

---

## 3. Fase 8: Full de Ruta MVP a `mfp-bibliography`

Aquest full de ruta està dissenyat amb tasques petites, modulars i dependents que utilitzen exclusivament les dades locals i eines Python ja disponibles a l'entorn.

```
[Tasca 1: Snapshot & Export]
       │
       ▼
[Tasca 2: Validació & Reconciliació]
       │
       ▼
[Tasca 3: Adaptador Mètric goatools] ◄── [Congelació go-basic.obo]
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[Tasca 4: Execució ALL vs EXP]   [Tasca 5: Taula Cobertura & Refs]
       │                                 │
       ├─────────────────────────────────┘
       ▼
[Tasca 6: Gràfics Descriptius]
       │
       ▼
[Tasca 7: Casos Prioritaris Revisió]
       │
       ▼ (Extensió)
[Tasca 8: Control Downsampling Aleatori]
```

---

### Tasca 1: Congelació de la Snapshot i Exportació Analítica
- **Objectiu**: Extreure de BioData un conjunt de fitxers analítics tabulars immutables (`.parquet` o `.csv`) a `data/interim/biodata_export/`.
- **Dependències**: Base de dades `BioData` accessible en mode lectura.
- **SQL de només lectura a executar**:
  ```sql
  -- Exportació d'anotacions consolidades amb metadades de proteïna
  SELECT 
      a.code AS uniprot_accession,
      p.id AS protein_entry_name,
      p.organism,
      p.taxonomy_id,
      p.data_class AS swiss_prot_status,
      ga.go_id,
      gt.category AS go_aspect,
      gt.description AS go_name,
      ga.evidence_code,
      ga.publication_id AS pmid
  FROM accession a
  JOIN protein p ON a.protein_id = p.id
  JOIN protein_go_term_annotation ga ON ga.protein_id = p.id
  JOIN go_terms gt ON ga.go_id = gt.go_id
  ORDER BY a.code, ga.go_id, ga.evidence_code;
  ```
- **Criteri d'Acceptació**:
  - Exactament 96.186 files exportades.
  - Generació de `data/interim/biodata_export/biodata_annotations.csv` amb el seu hash SHA-256.

---

### Tasca 2: Validació i Reconciliació Determinista
- **Objectiu**: Vincular les files exportades de BioData amb les entitats unificades del catàleg `mfp-catalog-candidate-v0.3.0`.
- **Dependències**: Tasca 1 i `releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv`.
- **Criteri d'Acceptació**:
  - Script `scripts/reconcile_catalog_with_biodata.py` executat.
  - Verificació que exactament 2.173 proteïnes del catàleg es resolen a BioData.
  - Documentació explícita de les 149 proteïnes no enllaçades en un informe de discrepàncies `data/interim/reports/unlinked_accessions_report.csv`.

---

### Tasca 3: Implementació de l'Adaptador Autònom de Mètriques (`goatools`)
- **Objectiu**: Proporcionar a `mfp-bibliography` un motor de similitud semàntica executable que substitueixi el mòdul trencat de `mfp-dataset-designer`.
- **Dependències**: Paquet `goatools` (ja instal·lat a l'entorn de Python) i fitxer `data/raw/ontology/go-basic.obo`.
- **Mòdul a crear**: `src/mfp_bibliography/metrics/go_similarity_adapter.py`.
- **Especificacions Tècniques Obligatòries**:
  1. **Separació estricta d'aspectes**: El càlcul de similitud s'ha d'executar separadament per a `BP` (Biological Process), `MF` (Molecular Function) i `CC` (Cellular Component). Mai barrejar termes de diferents ontologies.
  2. **Càlcul d'Information Content (IC)**:
     - $IC(c) = -\log \frac{freq(c)}{freq(root)}$
     - Permetre el càlcul d'IC sobre el corpus ALL i el recàlcul sobre el corpus EXP per avaluar l'efecte del biaix d'anotació.
  3. **Mètrica Wang (basada en graf DAG)**:
     - Càlcul pur a partir de la topologia del graf GO, independent de la freqüència d'anotació.
  4. **Mètriques Resnik i Lin**:
     - Càlcul basat en el Most Informative Common Ancestor ($MICA$).
  5. **MBL (Minimal Branch Length)**:
     - Documentar i tractar MBL estrictament com a **distància**, mai restant-la directament d'una similitud.
  6. **Agregació a nivell de proteïna**:
     - Implementar BMA (Best Match Average) i mitjana de màxims per parelles de termes.
  7. **Casos extrems**:
     - 0 termes $\to$ `NaN` o `0.0` explícit.
     - 1 terme $\to$ no computable per parelles (indicar `n_terms = 1`).
- **Criteri d'Acceptació**:
  - Test unitari a `tests/test_go_similarity_adapter.py` verificant valors exactes en un mini-DAG de control amb asseveracions numèriques sense mocks.

---

### Tasca 4: Comparació Reproduïble ALL versus EXP
- **Objectiu**: Quantificar l'impacte de restringir les anotacions a l'evidència experimental.
- **Dependències**: Tasques 2 i 3.
- **Cohorts de Comparació**:
  - Cohort A (**ALL**): Totes les anotacions de la proteïna (IEA, ISS, IDA, EXP, etc.).
  - Cohort B (**EXP Clàssica**): Només `EXP`, `IDA`, `IPI`, `IMP`, `IGI`, `IEP`.
  - Cohort C (**EXP + HTP**): EXP clàssica + `HTP`, `HDA`, `HMP`, `HEP`.
- **Mètriques a comparar per proteïna**:
  - Recompte de termes ($\Delta N_{terms} = N_{ALL} - N_{EXP}$).
  - Profunditat mitjana dels termes al DAG GO.
  - Similitud semàntica interna mitjana (Wang BMA, Lin BMA, Resnik BMA) per a BP i MF.
  - Pèrdua de resolució: nombre de proteïnes que passen de $\ge 2$ termes a $<2$ termes en EXP.
- **Criteri d'Acceptació**:
  - Taula analítica `data/processed/metrics/mfp_go_metrics_all_vs_exp.csv` generada.

---

### Tasca 5: Taula de Cobertura Bibliogràfica i Referències
- **Objectiu**: Construir la taula d'evidència bibliogràfica a nivell de proteïna i terme.
- **Dependències**: Tasca 1.
- **Indicadors a tabular per proteïna**:
  1. Nombre de PMIDs únics totals (ALL).
  2. Nombre de PMIDs únics en anotacions experimentals (EXP).
  3. Proporció d'anotacions sostingudes per literatura ($\frac{N_{pub}}{N_{annot}}$).
  4. Nombre d'articles aportats per la base de dades font (MultitaskProtDB-II).
  5. Nombre d'articles compartits entre la font i QuickGO.
- **Criteri d'Acceptació**:
  - Generació de `data/processed/metrics/mfp_bibliographic_coverage.csv`.

---

### Tasca 6: Generació de Gràfics Descriptius
- **Objectiu**: Visualització descriptiva dels patrons d'anotació i biaixos de literatura.
- **Dependències**: Tasques 4 i 5.
- **Figures a generar a `analysis/figures/`**:
  1. `fig1_annotation_drop_all_vs_exp.png`: Histograma i corba de densitat del recompte de termes per proteïna (ALL vs EXP).
  2. `fig2_pmid_distribution_per_protein.png`: Distribució logarítmica de PMIDs per proteïna (mostrant la cua llarga del biaix d'estudi).
  3. `fig3_semantic_similarity_shift.png`: Scatter plot / Violin plot de la similitud semàntica interna de BP i MF en ALL versus EXP.
  4. `fig4_source_go_pmid_overlap.png`: Diagrama de Venn / barres del solapament d'articles entre bases de dades de multifuncionalitat i anotacions GOA.
- **Criteri d'Acceptació**:
  - Script autònom `scripts/plot_descriptive_analysis.py` que executa sense errors i desa les figures en format d'alta resolució (300 DPI).

---

### Tasca 7: Llista de Casos Prioritaris per a Revisió Manual per Experts
- **Objectiu**: Seleccionar una mostra dirigida de 30 proteïnes d'alt interès per a validació manual.
- **Dependències**: Tasques 4 i 5.
- **Criteris de Selecció**:
  - 10 proteïnes d'**alt consens** ($\ge 3$ bases de dades font) però amb **baixes anotacions experimentals** ($\le 2$ termes EXP).
  - 10 proteïnes d'**alt consens** amb **alta divergència semàntica** (baixa similitud Wang BP $\le 0.3$).
  - 10 proteïnes amb **fort desacoblament bibliogràfic** (molts PMIDs a QuickGO però 0 a la base de dades font, o viceversa).
- **Criteri d'Acceptació**:
  - Document `docs/analysis/priority_curation_cases.md` amb els identificadors, noms, fonts i justificació de la selecció.

---

### Tasca 8 (Extensió Metodològica): Control de Reducció Aleatòria d'Anotacions (*Downsampling Control*)
- **Objectiu**: Demostrar si el canvi de similitud semàntica entre ALL i EXP es deu a la pèrdua de soroll computacional (IEA) o simplement a la reducció del nombre de termes.
- **Protocol**:
  - Per a cada proteïna amb $N_{ALL}$ termes i $N_{EXP}$ termes experimentals ($N_{EXP} < N_{ALL}$):
  - Fer 100 mostrejos aleatoris de $N_{EXP}$ termes extrets de la llista ALL.
  - Calcular la similitud semàntica mitjana d'aquests conjunts aleatoris i comparar-la amb la similitud del conjunt EXP real.
- **Criteri d'Acceptació**:
  - Script `scripts/run_downsampling_control.py` implementat i documentat com a addenda metodològica.

---

## 4. Classificació de Tasques: Mínimes vs Ajornables

| Fase | Tasca | Estat | Caràcter | Justificació Tècnica |
| :--- | :--- | :---: | :---: | :--- |
| **Pla Snapshot** | Tasca 1: Snapshot & Exportació | Pendent | **MÍNIMA** | Prerequisit absolut d'immutabilitat |
| **Consistència** | Tasca 2: Validació i Reconciliació | Pendent | **MÍNIMA** | Evita analitzar mostres incongruents |
| **Motor Mètric** | Tasca 3: Adaptador `goatools` | Pendent | **MÍNIMA** | Desbloqueja l'anàlisi semàntica |
| **Comparació** | Tasca 4: ALL versus EXP | Pendent | **MÍNIMA** | Nucli de la pregunta biològica |
| **Bibliografia** | Tasca 5: Cobertura Bibliogràfica | Pendent | **MÍNIMA** | Auditoria del suport en papers |
| **Visualització** | Tasca 6: Gràfics Descriptius | Pendent | **MÍNIMA** | Lliurable visual descriptiu |
| **Curació** | Tasca 7: Llista de Casos Prioritaris | Pendent | **MÍNIMA** | Pont cap a la revisió per experts |
| **Control** | Tasca 8: Downsampling Control | Pendent | *AJORNABLE* | Extensió metodològica avançada |
| **Re-extracció** | Re-extracció TrEMBL (149 accs) | Pendent | *AJORNABLE* | No bloqueja l'anàlisi del 93,6% de la cohort |
| **Estructures** | Càrrega de PDB / Taula `chain` | Pendent | *AJORNABLE* | Fora de l'abast de la primera MVP |
| **Ontologia** | WikiPathways / Coocurrència GO | Pendent | *EXCLÒS* | Exclòs expressament de la fase actual |

