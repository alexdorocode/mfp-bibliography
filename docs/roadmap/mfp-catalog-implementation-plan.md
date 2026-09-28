# Full de ruta d'implementació del catàleg MFP

## Objectiu del producte

Lliurar un únic CSV de proteïnes MF deduplicades (`mfp_proteins`), acompanyat de taules relacionals de procedència (`mfp_source_records`), identificadors (`mfp_identifiers`), afirmacions d'origen (`mfp_assertions`) i cobertura (`mfp_coverage`).

## Punt de partida

- 1.166 registres d'origen; 1.074 entitats proteiques; 45 fusions exactes per accesió UniProt normalitzada.
- MoonProt: 703; MoonDB: 351; PlantMP: 112.
- Llacunes de MoonProt: 103 absent coneguts; 542/543/626 sense resoldre.
- MultifacetedProtDB i MultitaskProtDB-II: només dades brutes, sense ingestió.

## Fases

### Fase 1 — Auditoria de la línia base

- **Propòsit:** validar recomptes, fusions i estat de resolució abans d'ampliar fonts.
- **Lliurable mínim:** informe d'auditoria amb recomptes reproduïbles per font.
- **Criteris d'acceptació:** els números coincideixen amb la línia base congelada; cap etiqueta d'origen es converteix en veritat binària MF.
- **Fora de l'abast:** NMF/negatives, enriquiment extern, coincidència difusa.

### Fase 2 — Ingestió de MultifacetedProtDB

- **Propòsit:** integrar registres i afirmacions com a reclamacions específiques de la font.
- **Lliurable mínim:** perfil de font i taula `mfp_assertions` poblada.
- **Criteris d'acceptació:** cada afirmació conserva l'etiqueta original (predicted, likely, curated, confirmed, unresolved).
- **Fora de l'abast:** adquisició de dades noves, transformacions.

### Fase 3 — Ingestió de MultitaskProtDB-II

- **Propòsit:** mateix tractament que la Fase 2 per a MultitaskProtDB-II.
- **Lliurable mínim:** registres ingerits amb procedència completa.
- **Criteris d'acceptació:** deduplicació només per accesió UniProt normalitzada exacta.
- **Fora de l'abast:** fusiò difusa o inferida.

### Fase 4 — Propagació d'identificadors bibliogràfics

- **Propòsit:** propagar DOI/PMID entre registres fusionats d'una mateixa entitat.
- **Lliurable mínim:** `mfp_identifiers` coherent amb les fusions exactes.
- **Criteris d'acceptació:** cap identificador propagat entre entitats diferents.
- **Fora de l'abast:** cerca bibliogràfica externa.

### Fase 5 — Llançament reproduïble `mfp_catalog_v1`

- **Propòsit:** publicar el catàleg amb traçabilitat total.
- **Lliurable mínim:** CSV més taules relacionals, empaquetades i versionades.
- **Criteris d'acceptació:** vegeu les regles de veracitat del llançament.
- **Fora de l'abast:** afirmacions de cobertura completa no suportades.

## Model de dades

`mfp_proteins` (entitats úniques), `mfp_source_records` (registres per font), `mfp_identifiers` (UniProt, DOI, PMID), `mfp_assertions` (reclamacions literals de cada font), `mfp_coverage` (estats: present, absent conegut, no resolt), i taules futures de relacions de referència.

## Regles de veracitat del llançament

- Mai afirmar cobertura completa de MoonProt mentre romanguin identificadors no resolts.
- El llançament ha d'estipar abast, limitacions, hashos de fitxers, versió d'esquema i ordre de reproducció.

## Propera tasca d'implementació

Perfilatge de la font MultifacetedProtDB i ingestió de les seves afirmacions.
