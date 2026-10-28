# Propuesta experimental — Presentation Storyboard

**Documento:** guion editable para preparar una presentación científica.  
**Versión:** 0.4 — revisión de B3 y B4.  
**Fecha:** 28 de octubre de 2026.  
**Formato objetivo:** 15 diapositivas, aproximadamente 1 minuto por diapositiva.  
**Idioma:** castellano con terminología técnica en inglés.  
**Estado:** propuesta de trabajo; no equivale a un protocolo congelado ni a resultados experimentales.

> **Nota de edición:** esta versión se ha recompuesto a partir del guion y de las modificaciones aprobadas en la conversación. El archivo completo anterior no estaba disponible entre los archivos accesibles; por tanto, las secciones no reproducidas íntegramente en la conversación no pueden considerarse preservadas literalmente. No se ha modificado ningún repositorio de GitHub.

## Cómo utilizar este documento

Cada sección `S01`–`S15` corresponde a una diapositiva. El contenido visible debe mantenerse breve; las explicaciones metodológicas y los criterios de revisión pertenecen a las speaker notes o al material de apoyo.

- **Mensaje central:** idea que debería retener la audiencia.
- **Contenido visible:** propuesta de texto para la slide, no una especificación exhaustiva.
- **Visual:** diseño conceptual, sin resultados simulados.
- **Speaker notes:** orientación para aproximadamente 60 segundos; ajustar tras ensayar.
- **Estado:** distingue recursos reutilizables, comprobaciones necesarias y desarrollo pendiente.
- **Output / cierre:** producto esperado y condición para interpretarlo.
- **Pregunta de revisión:** decisión que debe discutir el equipo; no implica que la implementación pueda comenzar sin aprobar el diseño completo.

**Terminología:** en la primera aparición se define **EEC — Experimental Evidence Code**; el plural es **Experimental Evidence Codes**. Se utiliza siempre `EEC`, no `ECC`. En este estudio, el annotation set EEC incluye EXP, IDA, IPI, IMP, IGI e IEP. `ALL` identifica las anotaciones recuperadas que cumplen la política de elegibilidad acordada, no una garantía de exhaustividad biológica.

**Límite de fuentes técnicas:** CBBIO/BioData, Protein Information System (PIS) y mfp-bibliography. La auditoría adjunta se utiliza solo para las observaciones de esos componentes; sus afirmaciones sobre ejecución local no se presentan como verificaciones de la instalación actual. [1]

## Cambios incorporados

- Se recupera la divergencia GO-MF–GO-MF como objetivo central de B3; la baja coocurrencia deja de ser un filtro obligatorio de entrada.
- Se priorizan los máximos por proteína y los pares que los alcanzan con `1 − Wang`, `1 − Lin` y MBL, sin combinar sus escalas.
- Se incorpora en B3 la hipótesis de complementariedad: comportamiento coherente con el contraste científico y correlación limitada entre métricas, pendiente de comprobación.
- Se amplía B4 con la asociación MF–MF y su correspondencia con las divergencias de B3.
- Se incorpora en B4 la hipótesis de menor asociación promedio MF–CC para la función moonlighting respecto de la principal.
- Se contextualizan las asociaciones MF–CC mediante su frecuencia y soporte en BioData.
- Se mantienen dos variantes de asociación/coocurrencia: EEC y ALL.
- No se propone ninguna métrica propia ni ningún score compuesto. Las medias y los máximos son resúmenes descriptivos de medidas establecidas.
- B3 y B4 ocupan tres slides; el backlog y los Decision Gates se distribuyen en las dos últimas para conservar 15 slides.

## Narrative map

| Slide | Título | Función narrativa | Tiempo |
|---|---|---|---|
| S01 | Research Proposal | Pregunta y alcance | 1 min |
| S02 | Experimental Roadmap | Seis bloques y dos experimentos centrales | 1 min |
| S03 | Data & API Architecture | Responsabilidades y brechas | 1 min |
| S04 | BioData: Selection & Enrichment | EEC frente a QuickGO enrichment | 1 min |
| S05 | TargetData Snapshot | Dimensión observada y cobertura por comprobar | 1 min |
| S06 | B1: Corpus & Provenance | Identidad y trazabilidad | 1 min |
| S07 | B2: Evidence Sensitivity | EEC y ALL como políticas comparables | 1 min |
| S08 | B3: MF–MF Divergence | Pares y máximos por métrica | 1 min |
| S09 | B3: Extremes & Complementarity | Contraste con BioData y correlaciones | 1 min |
| S10 | B4: Functional–Cellular Association | Asociación MF–MF y MF–CC | 1 min |
| S11 | B5: Reference Comparison | Matching, estabilidad e interpretación | 1 min |
| S12 | B6: Evidence-based Curation | Revisión con evidencia independiente | 1 min |
| S13 | Extensions: PCA & UMAP 3D | Exploración posterior con sequence embeddings | 1 min |
| S14 | Implementation Backlog | Recopilación de pendientes | 1 min |
| S15 | Validation & Decision Gates | Condiciones de inicio y aprobación | 1 min |

**Duración objetivo:** 15 minutos de exposición, sin incluir preguntas. Para una versión de 14 minutos, fusionar S01 y S02. Para 13 minutos, además fusionar S05 y S06. Para 12 minutos, resumir S13 dentro de la slide final. En todos los casos conviene conservar S08–S10 separadas.

## S01 — Research Proposal

**Objetivo narrativo:** presentar una propuesta científica, no un conjunto de resultados.

**Pregunta científica:** ¿Cómo caracterizar la divergencia funcional de TargetData y su relación con los patrones de asociación observados en BioData?

**Mensaje central:** «Estudiar funciones divergentes y su contexto con datos trazables y medidas establecidas.»

**Contenido visible:**

- TargetData: conjunto de proteínas multifuncionales que se caracterizará y curará.
- BioData: corpus de referencia para contextualizar sus patrones funcionales.
- Dos experimentos centrales: MF–MF divergence y Functional–Cellular Association.
- Alcance: caracterización, comparación y curación; sin nuevas métricas propias.

**Visual sugerida:** TargetData y BioData alimentan una secuencia «divergencia → asociación → interpretación».

**Speaker notes — 60 segundos:**

La propuesta busca caracterizar las funciones anotadas en TargetData utilizando BioData como corpus de referencia. Primero se identificarán pares de funciones especialmente disímiles con medidas establecidas. Después se estudiará su asociación funcional y celular, para comprobar si los patrones aportan una interpretación coherente. La presentación propone preguntas, recursos y condiciones de ejecución. No presenta resultados ni pretende convertir un descriptor en una confirmación automática de multifuncionalidad.

**Estado visible:** PROPUESTA — hipótesis y alcance pendientes de aprobación conjunta.

**Output / cierre:** una pregunta central y límites explícitos aceptados por el equipo.

**Pregunta de revisión:** ¿La caracterización y curación constituyen la entrega principal de esta fase?

## S02 — Experimental Roadmap

**Objetivo narrativo:** explicar las dependencias sin confundir bloques científicos con slides.

**Mensaje central:** «Seis bloques conectan la calidad de los datos con la interpretación científica.»

**Contenido visible:**

| Bloque | Pregunta | Output |
|---|---|---|
| B1 — Corpus & Provenance | ¿Qué datos son analizables y de dónde proceden? | Cohort manifest y coverage report |
| B2 — Evidence Sensitivity | ¿Qué cambia entre EEC y ALL? | Annotation sets y sensibilidad |
| B3 — MF–MF Divergence | ¿Qué pares alcanzan los máximos y qué aportan las métricas? | Pairwise results y comparación de extremos |
| B4 — Functional–Cellular Association | ¿Cómo se relacionan esos pares con su asociación funcional y celular? | Asociaciones MF–MF y MF–CC EEC/ALL |
| B5 — Reference Comparison | ¿Persisten los patrones en una referencia comparable? | Contrastes y análisis de estabilidad |
| B6 — Evidence-based Curation | ¿Qué interpretaciones tienen evidencia independiente? | Curated TargetData y case records |

**Visual sugerida:** B1 → B2 → B3 → B4; B5 aporta la referencia y el contraste a B3/B4; B6 recoge los casos interpretables.

**Speaker notes — 60 segundos:**

B1 fija la identidad y cobertura del corpus. B2 establece las políticas de evidencia que se reutilizan en los análisis. B3 estudia divergencia y extremos; B4 estudia asociaciones funcionales y contexto celular. B5 proporciona el diseño de comparación con BioData y sus controles. B6 transforma los resultados en revisión documentada. El orden de presentación no implica ejecutar cada bloque una sola vez de forma lineal: B5 debe definirse antes de contrastar los resultados de B3 y B4.

**Estado visible:** PROPUESTA — diseño completo antes de la ejecución; implementación progresiva después de su aprobación.

**Output / cierre:** dependencias, entregables y límites acordados.

**Pregunta de revisión:** ¿Se aprueba la separación entre divergencia, asociación y curación?

## S03 — Data & API Architecture

**Objetivo narrativo:** distinguir persistencia, acceso y lógica experimental.

**Mensaje central:** «PIS conserva los datos; CBBIO facilita su acceso; el estudio define las comparaciones.»

**Contenido visible:**

- PIS: adquisición, enriquecimiento y persistencia de BioData y TargetData.
- CBBIO: vía preferente de consulta y reutilización de primitivas GO.
- mfp-bibliography: fuentes, identificadores y procedencia de las proteínas de interés.
- Brechas explícitas: QuickGO vía CBBIO y cadena GeOKG todavía pendientes.

**Visual sugerida:** fuentes → PIS/PostgreSQL → API Python CBBIO → análisis; mfp-bibliography enlaza las proteínas con sus fuentes. Marcar conexiones futuras con líneas discontinuas.

**Speaker notes — 60 segundos:**

La arquitectura evita duplicar adquisición y consultas en cada análisis. El objetivo es utilizar al máximo CBBIO y ampliar allí los mecanismos generales cuando sea necesario. Una primitiva disponible no equivale a un bloque experimental ya implementado. Según el estado comunicado, recuperar anotaciones y referencias de QuickGO mediante CBBIO sigue pendiente. GeOKG requiere integración en PIS, consulta de embeddings de términos y cálculo validado de distancias. La instalación activa y sus datos se comprobarán antes del piloto.

**Soporte:** PIS documenta la instalación de BioData; la auditoría aportada describe consultas batch y brechas de integración en CBBIO. [PIS](https://github.com/CBBIO/protein-information-system) [1]

**Estado visible:** DISPONIBLE DOCUMENTADO — infraestructura base. PENDIENTE P01/P02 — QuickGO y evidencias. PENDIENTE P03/P04/P05 — GeOKG.

**Output / cierre:** contrato de responsabilidades y acceso probado a los snapshots elegidos.

**Pregunta de revisión:** ¿Qué versión desplegada de PIS y CBBIO constituirá el baseline técnico?

## S04 — BioData: Selection & Enrichment

**Objetivo narrativo:** distinguir la selección de proteínas del enriquecimiento de sus anotaciones.

**Mensaje central:** «EEC selecciona proteínas; QuickGO amplía sus anotaciones.»

**Contenido visible:**

- Selección UniProt: presencia de alguno de los seis códigos EEC definidos para el estudio.
- QuickGO enrichment: recuperación de anotaciones asociadas y sus referencias PMID o GO_REF.
- BioData: corpus de referencia para comparar TargetData.
- Mantener evidencia y procedencia a nivel de anotación.

**Consulta exacta comunicada por el investigador:**

```yaml
search_criteria: '(go_exp:* OR go_ida:* OR go_ipi:* OR go_imp:* OR go_igi:* OR go_iep:*)'
```

**Visual sugerida:** «UniProt selection: EEC» → «Protein set» → «QuickGO enrichment» → «Annotation sets: EEC / ALL».

**Speaker notes — 60 segundos:**

La consulta selecciona proteínas por códigos de evidencia experimental. Esta decisión de adquisición no implica que todas las anotaciones recuperadas posteriormente tengan esos códigos. El enriquecimiento con QuickGO permite ampliar el conjunto de anotaciones y recuperar sus referencias cuando existan. Dentro del corpus seleccionado se distinguirán EEC y ALL para los análisis. También se conservará la procedencia de cada anotación. El hecho de seleccionar proteínas con evidencia experimental condiciona el corpus y debe quedar registrado en su manifest.

**Estado visible:** WORKFLOW COMUNICADO — selección y enriquecimiento. PENDIENTE P01/P02 — acceso completo vía CBBIO, referencias y comprobación de persistencia.

**Output / cierre:** snapshot BioData con consulta, fecha, identificadores y cobertura de referencias documentados.

**Pregunta de revisión:** ¿Qué snapshot y fecha de corte se utilizarán para construir los perfiles de referencia?

## S05 — TargetData Snapshot

**Objetivo narrativo:** mostrar la dimensión observada sin anticipar la cobertura analítica.

**Mensaje central:** «Hay una base cuantificada; falta determinar cuántas proteínas son evaluables en cada análisis.»

**Contenido visible — consultas SQL aportadas por el investigador:**

| Tabla / subconjunto | Recuento comunicado | Interpretación |
|---|---:|---|
| `protein` | 2.182 | Filas de proteínas; reportadas como proteínas únicas |
| `go_terms` | 9.376 | Filas del catálogo GO almacenado |
| `protein_go_term_annotation` | 96.186 | Filas de anotación proteína–GO |
| `go_terms`, `category = 'F'` | 2.451 | Términos GO-MF almacenados |
| Anotaciones enlazadas a `category = 'F'` | 25.265 | Filas de anotación proteína–GO-MF |

**Visual sugerida:** dos cifras principales —proteínas y anotaciones MF— junto a un panel «coverage audit pendiente».

**Speaker notes — 60 segundos:**

Estos recuentos describen la base TargetData comunicada por el investigador. No demuestran por sí solos cuántas proteínas tienen dos términos MF elegibles, cuántas tienen CC o qué referencias están disponibles. Tampoco permiten reconstruir la distribución por evidencia ni el número de pares utilizables. B1 medirá esas coberturas separadamente. El catálogo de términos y las filas de anotación son unidades distintas y se presentarán como tales.

**Estado visible:** DATOS REPORTADOS — recuentos SQL. PENDIENTE B1 — cobertura, deduplicación y elegibilidad por análisis.

**Output / cierre:** snapshot identificado y denominadores reconciliados con los recuentos de extracción.

**Pregunta de revisión:** ¿Qué identificador de snapshot y fecha deben acompañar estas cifras?

## S06 — B1: Corpus & Provenance

**Objetivo narrativo:** hacer visible la trazabilidad de proteínas y anotaciones.

**Pregunta científica:** ¿Qué registros pueden utilizarse y cómo se conectan con sus fuentes?

**Mensaje central:** «Cada proteína y cada anotación deben conservar sus identificadores de origen.»

**Contenido visible:**

| Entidad | Identificadores de origen | Contexto mínimo |
|---|---|---|
| Proteína | Accession UniProt, ID de fuente y clave interna, cuando existan | Fuente, taxonomía y snapshot |
| Anotación | ID de anotación de origen, si existe; clave interna y vínculo proteína–GO | GO ID, evidence code, proveedor y snapshot |
| Referencia de anotación | PMID o GO_REF conservado literalmente | Relación con la anotación y procedencia |
| Resultado | Protein ID y par de GO IDs | Métrica, política, perfil y estado de cálculo |

**Visual sugerida:** source record → proteína → anotación → referencia → resultado.

**Speaker notes — 60 segundos:**

B1 construirá el registro analítico mínimo y distinguirá identificadores de proteínas, anotaciones y referencias. Si una fuente no proporciona un identificador estable de anotación, no se inventará uno externo: se podrá generar una clave interna documentada preservando los campos originales. Se auditarán duplicados, solapamientos, términos inválidos y cobertura. PMID y GO_REF se conservarán como tipos de referencia diferentes. El resultado será una cohort manifest con denominadores y motivos de no elegibilidad.

**Soporte:** la auditoría identifica normalización y procedencia en mfp-bibliography y brechas en la proyección de evidencias por CBBIO; hay que comprobar el esquema desplegado y los campos realmente poblados. [1]

**Estado visible:** REUTILIZABLE — identidad y consultas base. PENDIENTE P01/P02/P06 — referencias, cobertura y estados explícitos.

**Output / cierre:** D1 — manifest, coverage report y registro de exclusiones o ambigüedades.

**Pregunta de revisión:** ¿Qué campos son obligatorios para cada bloque y cuáles permiten un análisis parcial?

## S07 — B2: Evidence Sensitivity

**Objetivo narrativo:** separar el efecto de la política de evidencia del efecto de disponer de menos términos.

**Pregunta científica:** ¿Cuánto cambian los pares, máximos y asociaciones entre EEC y ALL?

**Mensaje central:** «Aplicar dos políticas de evidencia y cuantificar qué resultados permanecen estables.»

**Contenido visible:**

- EEC: EXP, IDA, IPI, IMP, IGI e IEP.
- ALL: todas las anotaciones elegibles recuperadas bajo una política explícita.
- Comparaciones apareadas por proteína; cobertura y términos retenidos.
- Sensibilidad al número de términos, sin convertir ausencias o errores en cero.

**Visual sugerida:** una proteína se bifurca en EEC y ALL; cada rama conserva número de términos, pares válidos y estado.

**Speaker notes — 60 segundos:**

Los análisis se repetirán con dos conjuntos de anotaciones claramente definidos. La comparación será apareada siempre que la proteína sea evaluable en ambas políticas. Si una política retiene menos términos, puede cambiar el máximo sin que eso refleje necesariamente un cambio biológico. Por ello se reportarán términos, pares y cobertura, y se predefinirá un control de sensibilidad al tamaño del conjunto. Los perfiles IC y de asociación tendrán identificadores para evitar cambios implícitos de referencia.

**Estado visible:** PENDIENTE — selector versionado, sensibilidad y estados auditables. PENDIENTE P01/P02 — evidencias completas vía CBBIO.

**Output / cierre:** D2 — políticas reproducibles, cobertura y comparación EEC/ALL; sensibilidades definidas antes de inspeccionar resultados.

**Pregunta de revisión:** ¿Qué políticas de calificadores, propagación y relaciones GO se fijarán para ambos annotation sets?

## S08 — B3: MF–MF Divergence

**Objetivo narrativo:** explicar qué se mide entre las funciones de una misma proteína.

**Pregunta científica:** ¿Qué pares de funciones moleculares presentan mayor disimilitud en cada proteína?

**Mensaje central:** «Identificar los pares más divergentes mediante métricas establecidas, sin combinar sus escalas.»

**Contenido visible:**

- **Pairwise dissimilarity:** `1 − Wang`, `1 − Lin` y MBL.
- **Primary output:** máximo por proteína, pares que lo alcanzan y cobertura.
- **Annotation sets:** EEC y ALL.
- **GeOKG-GO:** representación complementaria pendiente de integración y validación.

**Visual sugerida:** una proteína conectada a varios términos GO-MF. Tres pequeños paneles destacan conceptualmente el par más divergente según cada métrica, sin asumir que siempre sea el mismo. GeOKG se muestra como una rama discontinua con etiqueta «PENDIENTE». No incluir valores ni resultados hipotéticos.

**Speaker notes — 60 segundos:**

Se calculará la disimilitud de todos los pares GO-MF elegibles de cada proteína. El resultado central será el máximo por métrica, conservando los pares que lo alcanzan y los posibles empates. Wang, Lin y MBL se interpretarán por separado, sin promediarlos entre sí ni construir un índice propio. El análisis se repetirá con EEC y ALL. GeOKG se incorporará posteriormente, cuando su integración, acceso y distancia estén validados. Pairwise divergence designa este análisis término–término, no una cuarta métrica nueva.

**Recursos reutilizables:** CBBIO documenta Wang, Lin y MBL; Lin requiere preparar un perfil de Information Content. [API GO de CBBIO](https://github.com/CBBIO/BioData/blob/main/docs/GO.md)

**Estado visible:** DISPONIBLE DOCUMENTADO — primitivas GO. PENDIENTE P06/P07 — estados, cobertura y máximos. PENDIENTE P03/P04/P05 — GeOKG en PIS, consulta de term embeddings y distancias en CBBIO.

**Output / cierre:** D3a — tabla de pares no ordenados distintos, valores por métrica, máximos y todos sus empates; menos de dos términos elegibles implica `insufficient_terms`. El uso de GeOKG requiere su propio acceptance test.

**Pregunta de revisión:** ¿Se aprueba el máximo como resumen principal y la media como descriptor secundario, sin score compuesto?

## S09 — B3: Extremes & Complementarity

**Objetivo narrativo:** explicar qué convierte un máximo en un resultado científicamente interesante y cómo evaluar redundancia.

**Preguntas científicas:** ¿TargetData presenta máximos más extremos que una muestra comparable de BioData? ¿Las métricas muestran el comportamiento esperado, pero aportan información poco redundante?

**Mensaje central:** «Contrastar los extremos funcionales y evaluar si las métricas ofrecen perspectivas complementarias.»

**Contenido visible:**

- Comparar máximos de TargetData con una matched BioData sample.
- Medir la proporción de proteínas evaluables con máximos extremos por métrica.
- Estudiar correlación y overlap de proteínas y pares destacados.
- **Working hypothesis:** comportamiento coherente con el contraste propuesto y correlación limitada entre métricas.

**Visual sugerida:** panel para distribuciones futuras de máximos y panel para matriz de correlación; añadir un esquema de overlap de pares. No representar resultados simulados ni colorear la matriz como si existieran correlaciones observadas.

**Speaker notes — 60 segundos:**

Se contrastará si TargetData presenta máximos de divergencia más extremos que una muestra comparable de BioData. Además, interesa comprobar si las métricas responden de forma coherente a esa pregunta sin reproducir exactamente la misma información. Se estudiará su correlación sobre las mismas observaciones elegibles y, por separado, la coincidencia de proteínas y pares destacados. Una correlación baja sería compatible con complementariedad, pero también habrá que revisar cobertura, estabilidad y discordancias antes de interpretarla así.

**Precisiones para el protocolo:**

- Separar correlación entre valores de los mismos pares y correlación entre máximos por proteína.
- Evaluar inicialmente una correlación de rangos establecida, como Spearman; no combinar niveles de análisis.
- Los pares de una proteína no se tratarán como réplicas biológicas independientes para la inferencia.
- Registrar empates, saturación y pares evaluables antes de interpretar correlaciones.
- Correlación limitada no demuestra independencia estadística ni complementariedad por sí sola.
- La hipótesis de extremos se evalúa como proporción y magnitud; no se exige que todas las proteínas cumplan el patrón.
- Umbrales y reglas de selección se fijan antes de inspeccionar TargetData; no se optimizan para maximizar la separación observada.
- B5 define el matching y el contraste; esta slide explica su finalidad y no duplica su implementación.

**Estado visible:** PENDIENTE P07/P09 — extremos, matched sampling, correlación y overlap. PENDIENTE P03/P04/P05 — extensión GeOKG y comparación con las otras medidas.

**Output / cierre:** D3b — posicionamiento de máximos en la referencia y concordancia entre medidas; selección trazable de pares para B4 sin exigir consenso total entre métricas.

**Pregunta de revisión:** ¿Qué criterio de extremo, estrategia de matching y análisis de correlación se aprobarán antes de ejecutar el estudio?

## S10 — B4: Functional–Cellular Association

**Objetivo narrativo:** relacionar la divergencia funcional con la asociación MF–MF y el contexto MF–CC.

**Preguntas científicas:** ¿La asociación entre funciones concuerda con las divergencias de B3? ¿La función moonlighting presenta menor asociación promedio con los componentes celulares de la proteína que la función principal?

**Mensaje central:** «Relacionar la divergencia funcional con la coocurrencia entre funciones y con su asociación al contexto celular.»

**Contenido visible:**

- **MF–MF association:** estudiar cuán habitualmente coocurren los pares seleccionados en BioData y contrastarlo con B3.
- **MF–CC association:** comparar la asociación promedio de cada función con los GO-CC de la proteína.
- **Working hypothesis:** menor asociación promedio para la función moonlighting que para la principal.
- **Reference context:** frecuencia y soporte de las parejas MF–CC en BioData, con EEC y ALL.

**Visual sugerida:** dos funciones MF₁ y MF₂ enlazadas por su divergencia B3; junto al enlace, su asociación MF–MF en BioData. Debajo, ambas funciones se conectan al mismo conjunto de CC y se comparan sus asociaciones promedio. Usar «principal» y «moonlighting» solo en casos con roles respaldados por evidencia independiente.

**Speaker notes — 60 segundos:**

B4 añade dos lecturas a los pares identificados en B3. Primero, examina si su coocurrencia en BioData se corresponde con las disimilitudes observadas, sin asumir que distancia y rareza sean equivalentes. Segundo, compara la asociación promedio de cada función con el mismo conjunto de componentes celulares de la proteína. La hipótesis es que la función moonlighting muestre menor asociación que la principal. La frecuencia y el soporte de las parejas MF–CC en BioData ayudarán a contextualizar ese patrón, tanto con EEC como con ALL.

**Diseño analítico de apoyo:**

| Componente | Comparación | Resultado esperado del análisis |
|---|---|---|
| MF–MF | Asociación observada en BioData frente a disimilitud de B3 para el mismo par | Determinar correspondencia, ausencia de relación o discordancias |
| MF–CC por par | Asociación de MF₁ y MF₂ con cada CC elegible | Detectar patrones habituales o poco habituales con soporte |
| MF–CC por función | Promedio de asociación sobre el mismo conjunto de CC evaluables | Contraste apareado entre función principal y moonlighting |
| Contexto en BioData | Frecuencias marginales y conjuntas; soporte por proteínas únicas | Distinguir asociación estimable, baja cobertura y pareja no observada |
| Sensibilidad | Misma definición bajo EEC y ALL | Evaluar estabilidad sin cambiar la fórmula entre políticas |

**Reglas de interpretación y ejecución:**

- Elegir una medida de asociación establecida antes de la ejecución; no diseñar una fórmula propia ni un score combinado.
- Si se considera NPMI u otra medida establecida, documentar su dirección, dominio, soporte y casos límite antes de aprobarla. No queda fijada por esta slide.
- La media por función es un resumen descriptivo de esa medida, no una nueva métrica.
- Comparar ambas funciones sobre los mismos CC evaluables y registrar la cobertura común. Si no existe cobertura suficiente, informar el estado no calculable.
- No sustituir parejas no observadas o errores por cero ni interpretarlos automáticamente como incompatibilidad.
- Contar coocurrencias por proteínas únicas, no por duplicados de filas de anotación.
- Mantener reference profiles identificados para MF–MF EEC/ALL y MF–CC EEC/ALL. BioData es el corpus de referencia; su muestra comparable se utiliza en los contrastes según el diseño de B5.
- No asignar función principal o moonlighting a partir del propio score. Sin evidencia independiente, utilizar MF₁ y MF₂ y limitar el análisis a asociaciones sin rol.
- La hipótesis direccional se contrastará en el subconjunto con roles documentados; no se extenderá automáticamente a toda TargetData.
- Evaluar todos los CC elegibles según una política predefinida, no seleccionar retrospectivamente solo el más raro.
- Coanotación no confirma que la función ocurra en ese compartimento. La conexión BP–MF principal–CC pertenece inicialmente a la revisión contextual con evidencia independiente, no a una relación tripartita inferida ni a una nueva métrica.
- La asociación MF–MF no es un filtro obligatorio previo para B3: también interesa estudiar pares divergentes que sí sean frecuentes.

**Reutilización concreta:** CBBIO permite separar anotaciones por categoría GO; esa partición no equivale a disponer de perfiles de asociación ya implementados y validados. [API GO de CBBIO](https://github.com/CBBIO/BioData/blob/main/docs/GO.md) [1]

**Estado visible:** PENDIENTE P08 — perfiles, asociación y validación MF–MF/MF–CC EEC/ALL. PENDIENTE P01/P02 — anotaciones y referencias QuickGO vía CBBIO. PENDIENTE P10 — roles y evidencia contextual.

**Output / cierre:** D4 — tabla enlazada proteína–par MF–CC, asociación MF–MF, asociaciones MF–CC, promedios por función, frecuencia, soporte, política y referencias. Toda inferencia de roles exige evidencia independiente.

**Pregunta de revisión:** ¿Qué medida establecida se utilizará y qué evidencia permitirá asignar roles en el subconjunto de contraste direccional?

## S11 — B5: Reference Comparison

**Objetivo narrativo:** explicar cómo separar diferencias funcionales de diferencias de composición y cobertura.

**Pregunta científica:** ¿Los patrones de B3 y B4 persisten frente a una referencia BioData comparable?

**Mensaje central:** «Interpretar diferencias tras controlar la composición y la carga de anotación.»

**Contenido visible:**

- Matched sampling: taxonomía, longitud y carga de anotación según disponibilidad.
- No realizar matching sobre las propias divergencias o asociaciones que se van a contrastar.
- Reportar magnitud, incertidumbre, cobertura y estabilidad EEC/ALL.
- Distinguir corpus de referencia para perfiles y muestra para comparación.

**Visual sugerida:** dos capas: BioData_reference genera IC y perfiles de asociación; una muestra comparable permite el contraste con TargetData.

**Speaker notes — 60 segundos:**

B5 define la referencia utilizada por los experimentos anteriores. El matching se basará en características de composición y cobertura, no en las métricas que queremos evaluar. Se distinguirá BioData como corpus para estimar perfiles de la muestra utilizada para comparar distribuciones. Habrá que fijar la política de solapamiento y evitar que el propio caso contribuya de forma no controlada a su referencia. El tamaño de muestra y las repeticiones se justificarán por precisión, disponibilidad y estabilidad; no solo por significación estadística.

**Estado visible:** PENDIENTE P09 — matching, contraste y sensibilidades. PENDIENTE P11 — manifests de perfiles y muestras.

**Output / cierre:** D5 — comparación contextualizada de B3/B4 con incertidumbre y diagnóstico de balance.

**Pregunta de revisión:** ¿Qué matching, política de solapamiento y criterio de precisión son viables en BioData?

## S12 — B6: Evidence-based Curation

**Objetivo narrativo:** conectar los resultados con decisiones auditables sin circularidad.

**Pregunta científica:** ¿Qué interpretaciones funcionales y celulares tienen respaldo independiente?

**Mensaje central:** «Las métricas priorizan la revisión; la evidencia sustenta la interpretación.»

**Contenido visible:**

- Revisar casos extremos, discordantes y una muestra no seleccionada por scores.
- Conservar fuente, identificadores, referencias, revisor y justificación.
- Documentar función principal y moonlighting solo cuando la evidencia permita asignarlas.
- Mantener TargetData_initial y TargetData_curated como versiones distintas.

**Visual sugerida:** ficha de curación con dos columnas: «resultado computacional» y «evidencia independiente».

**Speaker notes — 60 segundos:**

B6 revisará qué significan los casos destacados. La curación conservará incertidumbre y no convertirá un score en evidencia independiente de sí mismo. La función principal y la moonlighting deberán documentarse cuando sea posible; si no, se mantendrán etiquetas neutrales. La relación con un proceso biológico o un compartimento requerirá evidencia contextual. Los cambios de interpretación producirán una nueva versión de TargetData, manteniendo congelado el conjunto inicial utilizado en los análisis.

**Soporte:** la auditoría identifica mecanismos de procedencia reutilizables en mfp-bibliography y la necesidad de un registro de curación específico. [1]

**Estado visible:** PENDIENTE P10 — plantilla y revisión. PENDIENTE P01/P02 — acceso completo a referencias vía CBBIO.

**Output / cierre:** D6 — case records, decisiones trazables y TargetData_curated versionado.

**Pregunta de revisión:** ¿Qué criterios de evidencia y procedimiento de revisión se aprobarán para las asignaciones de rol?

## S13 — Extensions: PCA & UMAP 3D

**Objetivo narrativo:** mostrar dos extensiones exploratorias posteriores al núcleo científico.

**Mensaje central:** «Explorar los sequence embeddings con los resultados funcionales como color, no como resultado implícito de la proyección.»

**Contenido visible:**

- **Extension E1:** PCA 3D sobre sequence embeddings identificados.
- **Extension E2:** UMAP 3D con configuración, versión y seed registradas.
- Colores: máximos B3, asociación B4, evidencia, taxonomía y estado de curación.
- Misma proyección al cambiar el color; sin resultados simulados.

**Visual sugerida:** wireframes vacíos de dos vistas 3D, con catálogo de capas de color y rótulo «EXPLORATORY — PENDIENTE».

**Speaker notes — 60 segundos:**

Estas extensiones se ejecutarán al disponer de datos y resultados trazables. PCA y UMAP utilizarán embeddings de secuencia con modelo y pooling identificados. Los scores funcionales se utilizarán para colorear la proyección principal, no como entradas que determinen su estructura. Las ausencias se mostrarán como tales. Cambiar una métrica de color no debe cambiar las coordenadas. Se documentará variancia explicada para PCA y estabilidad de configuración para UMAP, sin interpretar una separación visual como una prueba suficiente.

**Estado visible:** DIFERIDO P12 — implementaciones PCA/UMAP 3D. Colores GeOKG pendientes de P03/P04/P05. Otras capas dependen de D3–D6.

**Output / cierre:** E1/E2 — vistas interactivas y estáticas, coordenadas y configuración exportables.

**Pregunta de revisión:** ¿Qué sequence embedding y qué capa de color priorizar para la primera exploración?

## S14 — Implementation Backlog

**Objetivo narrativo:** recopilar las dependencias pendientes mencionadas en las slides, sin presentarlas como capacidades existentes.

**Mensaje central:** «Separar infraestructura reutilizable, brechas de API y desarrollo experimental.»

**Contenido visible:**

| Workstream | Pendientes agrupados | Habilita |
|---|---|---|
| Data & evidence | QuickGO, referencias, calificadores y validación del snapshot | B1/B2/B4/B6 |
| GeOKG | Integración PIS → consulta CBBIO → distancia validada | Extensión B3/B5 y capas visuales |
| Experimental analysis | Estados, máximos, correlaciones, asociaciones EEC/ALL y matching | B3/B4/B5 |
| Release & review | Curación, manifests, validación y extensiones 3D | B6 y entregas posteriores |

**Visual sugerida:** dependency lanes, con la cadena GeOKG separada del baseline Wang/Lin/MBL.

**Speaker notes — 60 segundos:**

El backlog recoge tareas que ya han aparecido en el recorrido. QuickGO y GeOKG no deben presentarse como integraciones disponibles en CBBIO. En paralelo, las primitivas GO requieren agregación, estados y validación experimental. GeOKG puede mantenerse como extensión condicionada sin bloquear el baseline una vez aprobado ese alcance. Las duraciones se estimarán tras verificar el acceso y medir un piloto técnico. Aquí se solicita priorización y asignación de responsabilidades, no aprobación implícita de funcionalidades todavía ausentes.

**Estado visible:** PENDIENTE — responsables, dependencias y acceptance tests. No comprometer plazos sin medición.

**Output / cierre:** backlog priorizado con responsable, condición de aceptación y bloque habilitado.

**Pregunta de revisión:** ¿Qué tareas son obligatorias para el baseline y cuáles se aceptan como extensiones condicionadas?

## S15 — Validation & Decision Gates

**Objetivo narrativo:** cerrar la propuesta con condiciones de avance explícitas.

**Mensaje central:** «Aprobar el diseño completo antes de ejecutar, y validar cada dependencia antes de ampliar el alcance.»

**Contenido visible:**

| Gate | Condición de paso |
|---|---|
| G0 — Scientific approval | Preguntas B1–B6, hipótesis y límites aprobados |
| G1 — Data readiness | Snapshots, acceso, evidencias, identificadores y cobertura verificados |
| G2 — Metric contract | Medidas establecidas, políticas, perfiles, máximos y reglas de asociación definidos |
| G3 — Technical pilot | Estados, pruebas y extracción reproducibles; recursos medidos |
| G4 — Full analysis | Contrastes predefinidos, incertidumbre y sensibilidades ejecutados |
| G5 — Team review | Curación, limitaciones, release y decisión sobre extensiones |

**Visual sugerida:** recorrido de gates; una rama lateral condiciona la incorporación de GeOKG a su validación específica.

**Speaker notes — 60 segundos:**

La reunión debe terminar con decisiones sobre alcance, datos, medidas y responsabilidades. Antes de ejecutar habrá que cerrar el criterio de extremo, el matching, los perfiles EEC y ALL y la medida establecida de asociación. Las hipótesis de complementariedad y menor asociación de la función moonlighting no son criterios de éxito técnico: pueden no confirmarse y el estudio seguir siendo informativo. Una vez aprobado el diseño completo, el piloto verificará su implementación. Los cambios posteriores se documentarán como desviaciones o nuevas versiones.

**Estado visible:** PROPUESTA — gates y responsabilidades por acordar. GeOKG y QuickGO permanecen en el backlog hasta superar sus verificaciones.

**Output / cierre:** acta de aprobación con decisiones aceptadas, condicionadas o aplazadas.

**Pregunta de revisión:** ¿Se aprueba esta propuesta como base para congelar el protocolo y preparar el piloto?

## Backlog de apoyo

Esta tabla pertenece a la preparación de la presentación, no debe copiarse íntegra en una slide.

| ID | Tarea pendiente | Ubicación principal | Acceptance criterion propuesto |
|---|---|---|---|
| P01 | Acceso QuickGO y referencias mediante CBBIO | PIS + CBBIO | Recorrido adquisición → persistencia → consulta probado con procedencia |
| P02 | Evidencias, calificadores e identificadores | PIS + CBBIO | Campos preservados y proyectados; cobertura y multiplicidad documentadas |
| P03 | Integrar GeOKG-GO en PIS | PIS | Artefacto de términos identificado, versión, GO mapping y geometría registrados |
| P04 | Consultar term embeddings GeOKG | CBBIO | Lectura batch con cobertura y términos no disponibles explícitos |
| P05 | Distancias GeOKG | CBBIO | Distancia documentada y compatible con el artefacto; acceptance tests aprobados |
| P06 | Missingness y errores | CBBIO + capa experimental | Ninguna ausencia o excepción se convierte silenciosamente en cero |
| P07 | Pares, máximos y complementariedad | Capa experimental, reutilizando CBBIO | Pares auditables, empates, máximos y correlaciones en observaciones comparables |
| P08 | Asociación MF–MF y MF–CC EEC/ALL | Mecanismos generales en CBBIO; contrastes en la capa experimental | Medida establecida, denominadores y soporte validados; promedios y cobertura trazables |
| P09 | Referencia y matched sampling | Capa experimental | Balance documentado, solapamiento controlado y contraste no ajustado por el outcome |
| P10 | Roles y curación independiente | mfp-bibliography + revisión | Evidencia para roles y decisiones; subconjunto direccional B4 identificado |
| P11 | Run manifests y releases | Capa experimental + mecanismos de procedencia | Snapshots, GO, perfiles, código, políticas y seeds identificados |
| P12 | PCA y UMAP 3D | Capa de visualización | Coordenadas, configuración y colores exportables sin resultados simulados |

**Nota de compatibilidad:** estos IDs organizan el backlog de este guion; no se afirma que sean números de issues de GitHub. La auditoría describe trabajo pendiente de integración, estados y análisis específicos; sus estimaciones de esfuerzo no se convierten aquí en compromisos. [1]

## Decision Register

| ID | Decisión por cerrar | Propuesta actual | Condición para aprobar |
|---|---|---|---|
| DEC-01 | Medidas B3 | `1 − Wang`, `1 − Lin`, MBL; GeOKG condicionado | Definir dominio, dirección, IC y errores |
| DEC-02 | Resumen principal | Máximo con todos los pares empatados | Pruebas de elegibilidad y casos límite |
| DEC-03 | Criterio de extremo | Referencia predefinida por métrica | Fijar antes de inspeccionar TargetData |
| DEC-04 | Complementariedad | Correlación de rangos y overlap como análisis separados | Estabilidad y cobertura; no confundir baja correlación con independencia |
| DEC-05 | Medida de asociación B4 | Una medida establecida; ninguna propia | Elegir fórmula publicada, soporte y casos límite |
| DEC-06 | Variantes de evidencia | Misma medida bajo EEC y ALL | Políticas y reference profiles identificados |
| DEC-07 | Hipótesis direccional B4 | Menor asociación promedio de la función moonlighting | Roles independientes y mismos CC evaluables |
| DEC-08 | Muestra BioData | Matching sin usar outcomes B3/B4 | Balance, tamaño y solapamiento documentados |
| DEC-09 | Corpus IC y perfiles | Separar sensibilidad de anotaciones y de perfiles | Identificadores y reglas de construcción congelados |
| DEC-10 | GeOKG | Extensión condicionada | P03–P05 superados |
| DEC-11 | Curación y visualización | Versionar curación; diferir E1/E2 | Evidencia y baseline reproducibles |

## Checklist editorial

- [ ] EEC definido antes de utilizar la abreviación y escrito de forma consistente.
- [ ] BioData descrito únicamente por su papel de corpus de referencia.
- [ ] Conteos TargetData identificados como resultados SQL comunicados, con snapshot por consignar antes de presentar.
- [ ] Identificadores de proteínas y anotaciones diferenciados.
- [ ] Divergencia B3 separada de asociación B4.
- [ ] Máximos, correlaciones y overlap presentados como análisis distintos.
- [ ] Complementariedad y menor asociación moonlighting presentadas como hipótesis, no resultados.
- [ ] No aparecen métricas propias ni un score compuesto.
- [ ] EEC y ALL mantienen la misma definición de asociación y documentan sus perfiles.
- [ ] GeOKG y QuickGO vía CBBIO aparecen como pendientes donde se utilizan y se recogen en S14/S15.
- [ ] No se infiere actividad MF–CC ni una relación BP–MF–CC a partir de coanotación solamente.
- [ ] Ningún diagrama incluye datos o resultados inventados.
- [ ] Las speaker notes se han ensayado y ajustado al minuto por slide.
- [ ] Las fuentes y las observaciones de la auditoría se distinguen de la verificación del despliegue actual.
