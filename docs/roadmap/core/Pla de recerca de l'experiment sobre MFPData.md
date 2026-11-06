# Pla de recerca: anotacions GO, evidència i divergència funcional a MFPUniProtData

**Estat:** esborrany per a validació (v0.1). Cap decisió d'aquest document s'ha d'implementar fins que sigui revisada.





## 1. Resum

L'experiment proposat estudia **com es descriuen les proteïnes multifuncionals (MF) de MFPUniProtData mitjançant anotacions GO i quina evidència les sustenta**. Planteja tres preguntes: (1) quina qualitat i quin tipus d'evidència tenen les anotacions; (2) si les funcions d'una mateixa proteïna són semànticament divergents; (3) si aquesta divergència i l'associació amb components cel·lulars canvien en restringir l'anàlisi a evidència experimental.

El pla manté l'orientació **evidence-first** que ja havies considerat: primer determinar què està documentat i amb quin suport, i després interpretar les mètriques sobre GO. També conserva l'abast MF-only del projecte: no hi ha etiquetes NMF, benchmark de classificació ni afirmació sobre multifuncionalitat de proteïnes externes al catàleg.[^1][^2]

## 2. Punt de partida

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

La informació raw de cada proteina ve de cadescun dels documents que es brinde les bases de dades o hem extret d'alguna manera. Les dades es troben a 

(mfp-bibliography) alexdoro@galactica:~/repositories/mfp-bibliography$ tree data/raw/
data/raw/
├── moondb
│   ├── all_emf_and_curated.tsv
│   ├── all_EMF_annotation.tsv
│   └── all_manual_curated.tsv
├── moonprot
│   ├── artifact_index.csv
│   ├── mpid_100.html
    ...

├── multifacetedprotdb
│   ├── MultifacetedProtDB_data.json
│   └── MultifacetedProtDB_data.txt
├── multitaskprotdb-ii
│   └── proteins.csv
├── plantmp
│   ├── PlantMP MySQL-all-147.csv
│   ├── PlantMP MySQL-confirmed .csv
│   ├── PlantMP MySQL-likely.csv
│   ├── PlantMP MySQL.xlsx
│   ├── PlantMP_all.csv
│   └── PlantMP-predicted.csv
└── README.md

6 directories, 716 files

--
El que hem de comparar es la infoamció que som capaços d'extreure de la raw data, veure la covertura que tenim de les hipotesis, estudiar com es la coincidencia entre els termes extrets de QuickGO, veure el suport de les anotacions es troben a RAW data, mitjançant la informació recollida a MFPUniProtData. Un cop fet aixo, hem de estudiar les anotacions, veure el suport que tenim en cada especie. Aleshores podrem fer la comparació de veure si les anotacions de les proteines del las quals no tenim mes infomació que el seu ACCESION, podem veure que si segueixen les metriques de dissimilitud funcional.

Sobre tot el gran experiment a fer es estudiar la distancia en notació simple i en tripletes, per veure si ens es possible identificar proteines que segueixin disimilituds semblants a la GROUNDTRUTH ben anotada.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


### 2.1 Fets verificats pel que has aportat

| Element | Dada |
|---|---|
| Base de dades | `MFPUniProtData`, PostgreSQL (servidor 16.13) |
| Proteïnes a `protein` | 2.182 |
| Taules | `accession`, `chain`, `go_terms`, `protein`, `protein_go_term_annotation`, `sequence`, `sequence_embedding_type`, `sequence_embeddings`, `state`, `structural_alignment_types`, `structure`, `structure_3di` |
| `protein_go_term_annotation` | `id`, `protein_id`, `go_id`, `evidence_code` (no nul), `publication_id` (nul·lable) |
| `go_terms` | `go_id`, `category`, `description` |

El que **no** s'ha mostrat (nombre d'anotacions, distribució de codis, cobertura de `publication_id`, valors de `category`) es tracta com a desconegut i es mesura a la Fase 0.

De les taules amb les que comptem tenim MFPUniProtData, i també tenim BioData. BioData es la nostre referencia. El univers contra el que comparem. Aqui tenim un total de 137213 de les quals ens quedarem amb les que estiguin dins dels tamanys de les proteines que tenim, estratificant per tamany i taxonomia, de tal manera que ens seribira per poder comparar si les metriques obtingues de les proteines candidatas a mfp. Les dues bases de dades tenen les mateixes taules. i s'accedeixen amb el comando

> psql -h localhost -U usuario [DB]
pw: clave

> DB: BioData || MFP_UniProtData

Al que aspirem es a poder acabar produïnt un MFP_GroundTruthData, per poder experimentar i desenvlolupar les seguents fases del projecte.


### 2.2 Observacions de l'esquema

- **Unicitat amb `publication_id` nul.** La restricció única inclou una columna que admet nuls. PostgreSQL tracta normalment els nuls com a diferents dins d'una restricció única, de manera que podrien coexistir files idèntiques sense referència. Cal comprovar-ho empíricament i, si cal, usar `NULLS NOT DISTINCT` (PostgreSQL 15 o posterior) o una clau normalitzada. Això és una inferència a validar, no un error confirmat.
- **No hi ha jerarquia GO.** `go_terms` no conté arestes pare-fill. Cal una versió fixada de l'ontologia per calcular ancestres, especificitat o distàncies.
- **Camps GAF absents.** El format GAF 2.2 inclou relació/qualificador, `With/From`, data, `assigned_by` i extensions. Si no s'han conservat, no es pot distingir una anotació positiva d'una negada ni reconstruir la font de la inferència.[^3]
- **Referència única.** GAF permet una sola referència principal per línia; una clau amb una sola `publication_id` és coherent amb aquest model, però cal verificar com s'han tractat referències múltiples.[^4]

## 3. Marc científic

### 3.1 Evidència GO

Els codis d'evidència s'agrupen en experimentals (EXP, IDA, IPI, IMP, IGI, IEP), d'alt rendiment (HTP, HDA, HMP, HGI, HEP), filogenètics, computacionals, de declaració d'autor, de curador i electrònics (IEA). Les anotacions experimentals de la literatura primària són les més valorades i s'usen per estudiar enriquiments i funcions. Els IEA deriven de transferència o càlcul i no han estat revisats manualment.[^5][^6]

Dues regles de GO són rellevants per a la neteja: IPI amb activitat catalítica es considera una evidència massa feble i es marca per revisió, i les anotacions directes a *protein binding* són poc informatives.[^7]



### 3.2 Divergència funcional

PrOnto calcula dues mètriques de dissimilitud entre termes GO: probabilitats de coocurrència en anotacions de proteïnes (AP) i en anotacions de parells que interaccionen (IP); el llindar per defecte és p = 0,05. Utilitza totes les anotacions independentment del codi d'evidència. MoonDB usa aquestes mètriques, agrupament de la xarxa d'interaccions i herència d'anotacions per identificar proteïnes multifuncionals extremes (EMF).[^8][^9][^10]

Això crea un contrast metodològic útil: l'experiment pot mesurar quant canvia la divergència en usar només evidència experimental respecte a totes les anotacions.

### 3.3 Context documental

PlantMP separa proteïnes confirmades, probables i predites, amb criteris diferents per a cada categoria. Per tant, la procedència d'una proteïna a MFPUniProtData no s'ha de tractar com a equivalent d'una etiqueta uniforme de moonlighting.[^11]

## 4. Preguntes i hipòtesis

| ID | Pregunta | Hipòtesi operativa | Falsabilitat |
|---|---|---|---|
| Q1 | Quina part de les anotacions és experimental, no experimental o electrònica? | Les distribucions difereixen entre aspectes (MF, BP, CC) | Taula de freqüències per codi i aspecte |
| Q2 | Quina part té publicació associada? | La cobertura és menor per a codis no experimentals | Proporció de `publication_id` no nul per grup |
| Q3 | Les proteïnes tenen funcions BP/MF semànticament divergents? | La divergència és superior a un fons aleatori comparable | Comparació amb distribucions nul·les |
| Q4 | La divergència depèn del filtre d'evidència? | Restringir a evidència experimental canvia el rànquing de parells | Correlació de rangs i parells conservats |
| Q5 | Quins CC s'associen a termes MF/BP divergents? | Hi ha CC enriquits respecte a l'esperat | Test d'enriquiment amb correcció per proves múltiples |
| Q6 | L'evidència documentada concorda amb les anotacions de GO? | Part de les funcions descrites a la bibliografia no apareix com a terme explícit | Revisió manual d'una mostra |

Les hipòtesis són provisionals: cap s'ha de considerar acceptada abans de la validació.

## 5. Disseny experimental

### Fase 0. Auditoria i congelació

1. Registrar versions: PostgreSQL, data d'extracció de UniProt i QuickGO, versió de GO i, si és possible, esquema i hash d'un export.
2. Crear un export immutable de les taules rellevants (CSV o Parquet) amb manifest de checksums.
3. Executar consultes de perfilat: nombre d'anotacions, proteïnes sense anotacions, termes per proteïna, valors de `evidence_code` i `category`, nuls i duplicats a `publication_id`, anotacions a termes obsolets o no presents a l'ontologia.
4. Documentar què significa cada codi de `category` abans de qualsevol anàlisi.

*Criteri d'acceptació:* informe de perfilat revisat i export reproduïble.

### Fase 1. Normalització

- Carregar una versió fixada de l'ontologia GO i registrar ancestres per terme.
- Reparar o marcar termes obsolets, alternatius i fusionats; GO documenta regles automàtiques per a això.[^7]
- Agrupar els codis en classes (experimental, alt rendiment, filogenètic, computacional, autor, curador, electrònic).
- Excloure o analitzar per separat termes massa genèrics quan la mètrica ho requereixi.
- Resoldre duplicats segons la política validada.

*Decisió pendent:* com tractar HTP/HDA/HMP/HGI/HEP, ja que són experimentals però d'alt rendiment.

### Fase 2. Capes d'anàlisi

| Capa | Anotacions incloses | Finalitat |
|---|---|---|
| A | Totes | Referència comparable amb PrOnto |
| B | Experimentals de baix rendiment | Capa conservadora |
| C | B més alt rendiment | Sensibilitat a HTP |
| D | Experimentals + curador/autor | Evidència no automàtica ampliada |
| E | Excloent IEA | Prova de robustesa |

### Fase 3. Mètriques

1. **Perfil per proteïna:** nombre de termes per aspecte, especificitat, nombre de referències úniques i proporció per classe d'evidència.
2. **Divergència interna:** distància semàntica entre termes de la mateixa proteïna (mètode final a decidir, vegeu §8) i, quan sigui possible, dissimilitud basada en coocurrència segons PrOnto.[^9]
3. **Associació MF–CC:** freqüència de coocurrència entre termes funcionals i cel·lulars, amb mesures d'enriquiment i correcció per comparacions múltiples.
4. **Estabilitat:** coeficients de correlació de rangs i índex de Jaccard entre capes.

### Fase 4. Controls

- **Nul per permutació:** mantenir el nombre de termes per proteïna i barrejar assignacions dins de blocs d'especificitat comparable.
- **Control de mida:** estratificar o ajustar pel nombre d'anotacions, ja que les proteïnes molt anotades poden produir més parells divergents.
- **Sensibilitat:** repetir amb diferents llindars de p-valor i amb i sense termes genèrics.
- **Replicació:** si es disposa de dades externes, usar-les com a validació separada, no per ajustar paràmetres.

### Fase 5. Contrast bibliogràfic

Seleccionar una mostra estratificada (per font, organisme i classe d'evidència) i comparar la funció descrita per l'article amb els termes GO assignats. Cada cas es classifica: coincidència, terme més general, terme absent, terme no suportat o impossible de valorar. La revisió humana és obligatòria, ja que GO exigeix revisió manual d'associacions suggerides per IA abans d'acceptar-les.[^12]

## 6. Resultats esperats

- Informe de perfilat de MFPUniProtData amb limitacions de dades.
- Taules de distribució d'evidència per aspecte i classe.
- Rànquing de parells de termes i proteïnes amb alta divergència per capa.
- Anàlisi de sensibilitat a l'evidència.
- Taula d'associacions MF–CC amb mida d'efecte i incertesa.
- Mostra anotada bibliogràficament amb criteris explícits.

## 7. Risc i limitacions

| Risc | Impacte | Mitigació |
|---|---|---|
| Biaix d'estudi: les proteïnes més estudiades tenen més anotacions | Pot inflar la divergència | Control per nombre d'anotacions |
| Termes genèrics | Distorsionen distàncies | Sensibilitat amb exclusions |
| Pèrdua de camps GAF | Limita la interpretació de negacions i inferències | Documentar absències; recuperar camps si cal |
| Evidència mixta | Conclusions dependents del filtre | Anàlisi per capes |
| Duplicats amb `publication_id` nul | Recomptes incorrectes | Prova d'unicitat |
| Absència d'un fons negatiu | No es pot afirmar especificitat de MF | Interpretar com a descripció del catàleg, no com a classificació |
| Evolució de GO i UniProt | Resultats no reproduïbles | Congelar versions |

## 8. Decisions pendents

1. Mètrica semàntica principal: coocurrència tipus PrOnto, mesura basada en contingut d'informació o ambdues.
2. Tractament d'alt rendiment, IEA i termes genèrics.
3. Si s'inclouen proteïnes sense anotació experimental en l'anàlisi principal.
4. Si MF–CC s'analitza sobre tots els parells o només sobre els associats amb funcions MF/BP divergents.
5. Quins camps GAF es poden recuperar de QuickGO per a anotacions existents.
6. Tamany i mètode de selecció de la mostra bibliogràfica.

## 9. Integració amb la bibliografia

Els articles ja seleccionats poden ajudar a definir les fonts de MFPUniProtData i les limitacions de cada recurs, però no hauran de fixar automàticament criteris científics. Proposta mínima:

- Fitxa breu per article amb aportació, límits i estat de revisió.
- `docs/research/experiment-plan.md` com a contracte d'experiment.
- Una especificació separada per a cada pas implementable, amb criteris d'acceptació verificables.
- Cap acció de l'agent que modifiqui definicions o llindars sense aprovació humana.

## 10. Calendari orientatiu

| Etapa | Entregable | Dependència |
|---|---|---|
| 0 | Perfilat i congelació | Accés a la base |
| 1 | Normalització i capes | Fase 0 validada |
| 2 | Mètriques i controls | Decisions de §8 |
| 3 | Contrast bibliogràfic | Resultats preliminars |
| 4 | Informe final | Totes les anteriors |

No s'estimen dates: depenen de la revisió i de la mida de les anotacions encara no mesurada.

## 11. Criteris per validar el pla

- L'abast MF-only es manté sense classificació NMF.
- Totes les preguntes són mesurables amb les taules disponibles o amb extensions explicitades.
- Els resultats es poden reproduir amb versions congelades.
- Les conclusions distingeixen anotació, evidència i interpretació.
- Hi ha una decisió explícita sobre cada punt obert abans d'implementar.

## Apèndix A. Consultes inicials suggerides

Aquestes consultes són de perfilat i no modifiquen dades.

```sql
MFP_UniProtData=# SELECT COUNT(*) FROM protein_go_term_annotation;

SELECT evidence_code, COUNT(*) AS n
FROM protein_go_term_annotation
GROUP BY evidence_code ORDER BY n DESC;

SELECT category, COUNT(*) FROM go_terms GROUP BY category;

SELECT COUNT(*) AS sense_publicacio
FROM protein_go_term_annotation
WHERE publication_id IS NULL;

SELECT protein_id, go_id, evidence_code, COUNT(*)
FROM protein_go_term_annotation
WHERE publication_id IS NULL
GROUP BY protein_id, go_id, evidence_code
HAVING COUNT(*) > 1;
 count 
-------
 96186
(1 row)

 evidence_code |   n   
---------------+-------
 IEA           | 22694
 IDA           | 20562
 IPI           | 18013
 IBA           |  7810
 IMP           |  5773
 TAS           |  5217
 ISS           |  4616
 EXP           |  3762
 NAS           |  2277
 HDA           |  1980
 ISO           |  1743
 IGI           |   577
 IC            |   307
 IEP           |   299
 RCA           |   176
 HTP           |   140
 ISM           |    96
 ISA           |    83
 ND            |    27
 HMP           |    20
 HEP           |    13
 IKR           |     1
(22 rows)

      category      | count 
--------------------+-------
 cellular_component |    33
 C                  |  1000
 biological_process |   214
 P                  |  5561
 molecular_function |   117
 F                  |  2451
(6 rows)

 sense_publicacio 
------------------
            40669
(1 row)

 protein_id | go_id | evidence_code | count 
------------+-------+---------------+-------
(0 rows)

```

## Apèndix B. Límits d'aquesta versió

No s'ha pogut accedir a la base de dades ni al repositori privat des d'aquest entorn; el pla es basa en la sortida de `psql` que has aportat, en el context previ del projecte i en la documentació pública de GO i UniProt. Aquests documents confirmen les regles generals, però no els valors reals de MFPUniProtData.

---

## References

1. [Hi ha una nova dada important a tot aixo. Hem deixit que finalment considerem tota la informació que donen els laboratoris sobre els termes que s'està experimentant, hem de primer veure quins termes podem dedurïr de la bibliografia, que la majora es ...

...r el mòdul parser a `src/mfp_bibliography/go_normalization.py`.
     * Definir l'esquema a `data/curated/go_annotations.schema.json`.
     * Crear un script d'execució determinista a `scripts/normalize_go_annotations.py` amb tests unitaris associats.](https://www.perplexity.ai/search/8962e874-0f1a-4645-96bb-065a51f5a63e) - Sí: aquesta informació justifica un viratge important. Jo passaria d’un estudi centrat primer en les...

2. [El problema es que aqui no estem treballant amb NMF, nomes amb MF, ja que estem en el estudi bibliografic del problema, no estem definint un dataset on hi han MF i no NMF, volem ser capaços de produir un fixter unificat de totes les proteines MF que ...

...─ test_overlap_audit.py
    ├── test_plantmp_claims.py
    ├── test_profiling.py
    ├── test_provenance.py
    ├── test_schema.py
    ├── test_source_claim_policy.py
    ├── test_source_claims.py
    └── test_validation.py

39 directories, 901 files](https://www.perplexity.ai/search/0d40d339-7abe-4dec-a185-cdf4b29a6380) - Tens raó: aquest repositori no és un projecte de classificació MF vs NMF. És un repositori bibliogrà...

3. [geneontology.github.io › docs › go-annotation-fileGO Association File (GAF) format - Gene Ontology Resource](https://geneontology.github.io/docs/go-annotation-file-gaf-format-2.1/) - See the GO evidence code guide for the list of valid evidence codes for GO annotations

4. [GO Association file format: GAF 2.0](https://geneontology.org/docs/go-annotation-file-gaf-format-2.0/) - This guide lays out the format specifications for the deprecated *G* ene *A* ssociation *F* ile (GAF...

5. [Primer on the Gene Ontology - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6377150/) - Annotations based on direct experimental evidence found in the primary literature are denoted with t...

6. [Evidence | UniProt help](https://www.uniprot.org/help/evidences) - Experimental evidence codes · EXP: Inferred from Experiment = ECO:0000269 · IDA: Inferred from Direc...

7. [go-site/metadata/rules/README.md at master · geneontology/go-site](https://github.com/geneontology/go-site/blob/master/metadata/rules/README.md) - The GAF 2.2 spec is here: http://geneontology.org/docs/go-annotation-file-gaf-format-2.2/ .

8. [MoonDB 2.0: an updated database of extreme multifunctional and ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC6323955/) - PrOnto database: GO term functional dissimilarity inferred from biological data.
Front.
Genet.

9. [www.ncbi.nlm.nih.gov › pmc › articlesPrOnto database : GO term functional dissimilarity inferred ...](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4452890/) - We have therefore developed PrOnto, a web-based tool that provides two metrics of GO *functional dis...

10. [Redefining protein moonlighting](https://pmc.ncbi.nlm.nih.gov/articles/PMC4627267/) - We developed two measures of functional dissimilarity [4], one based on the frequency with which the...

11. [PlantMP: a database for moonlighting plant proteins - PMC - NIH](https://pmc.ncbi.nlm.nih.gov/articles/PMC6482322/) - per B Su · 2019 · Citat per 29 — The database contains searchable UniProt IDs and names, canonical a...

12. [Contributing GO annotations](https://www.geneontology.org/docs/contributing-to-go/) - - a precise evidence code
- all other mandatory elements listed in the GAF 2.2 documentation

