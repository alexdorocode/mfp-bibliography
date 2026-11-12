# Dossier del experimento: caracterización funcional y auditoría de evidencia del corpus positivo atribuido como multifuncional

| Campo | Valor |
|---|---|
| Archivo | `01_dossier_experimento.md` |
| Versión | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha de redacción y consulta remota | 2026-10-26 |
| Responsable | Pendiente de asignar |
| Revisión científica y técnica | Pendiente de asignar |
| Proyecto | PEC; experimento de auditoría del corpus positivo |
| Repositorio técnico inspeccionado | `CBBIO/BioData` |
| Revisión remota inspeccionada | `ed073bd4df680a3b45ee69943916e196d28b63b6` |
| Antecedente principal | `Dossier_extensio_PIS_BioData_PEC_v0.1.md`, borrador de 2026-10-19 |
| Dependencias documentales | Documentos 02–07 y candidato a anexo 04a, descritos en §12 |
| Fuentes | Inventario y localizadores en §14; código, documentación de proyecto y conversación diferenciados |

> [!NOTE]
> **Document Status & Current Role (Historical Research Dossier)**:
> This document is a historical research proposal and foundational design dossier. It does **not** describe current repository implementation, and formal scientific and implementation approval remains pending.
> - **Recovered Content**: Selected conceptual foundations (epistemic distinctions between source claims and biological truth, the three evidence layers, and the ten explicit negative methodological boundaries) have been recovered into canonical English documentation in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (explanatory reference).
> - **Retained Proposals**: Secondary research questions (RQ-01 through RQ-07) and phased experimental block concepts are preserved in this text as future research proposals.
> - **Traceability**: The original Spanish text is retained intact for scientific provenance and auditability. Section-level mappings are detailed in the [Documentation Recovery Map](../reports/documentation-recovery-map.md#81-reconciled-section-level-recovery-matrix).

Este documento actualiza y delimita el dossier inicial; no abre una línea experimental paralela. Su responsabilidad es explicar el objetivo, alcance, preguntas, límites y articulación del estudio. No sustituye los contratos especializados de protocolo, datos, métricas, arquitectura, revisión bibliográfica o aceptación de software.

No se ha ejecutado ningún experimento, prueba, consulta a la base de datos del usuario ni notebook. La actividad realizada para redactar este dossier se limita a lectura de fuentes accesibles, inspección estática remota mediante el connector GitHub y generación de este documento. No se han modificado repositorios ni creado commits, incidencias o solicitudes de cambio.

## Índice

1. Resumen y continuidad del dossier inicial
2. Convenciones, glosario y estados de evidencia
3. Contexto, motivación y modelo conceptual
4. Objetivos y preguntas de investigación
5. Alcance, conjuntos y exclusiones
6. Actores, sistemas y evidencia técnica
7. Bloques experimentales y trazabilidad de preguntas
8. Resultados esperados
9. Primera entrega vertical
10. Qué este estudio no puede demostrar
11. Decisiones, riesgos y cuestiones abiertas
12. Dependencias documentales e índice anotado
13. Criterios de finalización y aceptación del dossier
14. Inventario de fuentes y limitaciones de consulta
15. Comprobación final de coherencia

## 1. Resumen y continuidad del dossier inicial

El estudio examinará un corpus de proteínas que una o varias fuentes presentan como multifuncionales. Se analizará qué anotaciones GO tienen, qué propiedades describen las métricas y qué soporte bibliográfico permite sostener las atribuciones originales. «Positivo» significa aquí atribuido como tal por una fuente, no verdad biológica confirmada por este experimento.

El dossier inicial distinguía adquisición y procedencia con PIS, cálculo reutilizable con BioData e interpretación en el proyecto científico. Se conserva esa separación como diseño propuesto, pero la inspección actual solo verifica determinadas capacidades del repositorio BioData. La integración efectiva con PIS y con el repositorio experimental no se da por demostrada. [S1, §§3–6; G1–G5]

Se conservan del antecedente: trazabilidad, recursos congelados, separación de anotaciones originales y resultados derivados, sensibilidad a evidencias, revisión de casos y prohibición de convertir puntuaciones en verdad biológica. Se actualiza el catálogo de trabajo: MBL clásica, contenido informativo, dissimilaridades derivadas de Wang y Lin y asociaciones entre los tres pares de aspectos GO. Las denominaciones preliminares D³-MBL, RICD-MBL y NDE del dossier inicial no se consideran métricas aprobadas ni implementaciones verificadas. [S1, §7; C1–C3]

La fase no construye ni valida negativos y no entrena clasificadores. Los planes históricos de PEC para clasificación y Dataset Designer se mantienen como contexto de otros trabajos, no como entregables de esta fase. [S3–S6]

La utilidad esperada consiste en producir un catálogo interpretable de evidencia y limitaciones y en evaluar si los descriptores ayudan a revisar el corpus mejor que indicadores simples. No se anticipa que todas las métricas sean útiles ni que el corpus resulte homogéneo.

## 2. Convenciones, glosario y estados de evidencia

### 2.1. Términos principales

| Término | Significado |
|---|---|
| GO | Gene Ontology: ontología de actividades moleculares, procesos biológicos y componentes celulares. |
| MF | Molecular Function, función molecular; no significa proteína multifuncional. |
| BP | Biological Process, proceso biológico. |
| CC | Cellular Component, componente celular. |
| MFP | Multifunctional protein, proteína multifuncional en sentido amplio. |
| Moonlighting | Funciones fisiológicamente diferenciadas de una misma cadena polipeptídica, bajo una definición operativa que debe concretar 06; no toda amplitud funcional satisface esa definición. |
| MBL | Minimum Branch Length; nombre del descriptor estructural cuya variante implementada debe verificar 04. |
| IC | Information Content, contenido informativo. No confundir con el código GO `IC`, Inferred by Curator. |
| NPMI | Normalized Pointwise Mutual Information, base estadística propuesta para asociaciones interaspecto. |
| PMID | Identificador de una publicación en PubMed; no es un indicador automático de calidad. |
| OBO | Formato de representación de ontologías utilizado por el recurso GO local. |
| API | Interfaz de programación; en este caso funciones Python, no un servicio HTTP supuesto. |
| Snapshot | Exportación congelada e identificable de datos; no implica que ya exista. |
| Manifiesto | Registro de recursos, versiones, configuración y procedencia de una ejecución. |

### 2.2. Clasificación de afirmaciones

| Estado | Uso |
|---|---|
| VERIFICAT EN CODI | Se ha leído una implementación o esquema versionado. No implica ejecución correcta ni equivalencia con la instalación del usuario. |
| DOCUMENTAT NO VERIFICAT | Se ha leído una descripción, contrato o información aportada, pero no se ha verificado su operación. |
| PROPOSTA | Diseño planteado para este experimento, sin aprobación formal ni ejecución. |
| PENDENT | Decisión o información necesaria todavía no resuelta. |
| NO ACCESSIBLE | Recurso que no se ha podido consultar como artefacto o implementación en esta sesión. |

Se mantienen estas etiquetas literalmente para facilitar su comparación con el encargo. Las afirmaciones normativas nuevas siguen siendo PROPOSTA hasta aprobación. El asentimiento conversacional a la dirección general no equivale a aprobación de cada umbral o política técnica.

## 3. Contexto, motivación y modelo conceptual

### 3.1. Heterogeneidad de las atribuciones

El antecedente `canonical_multifunctional_protein_data_dossier.md` distingue fuentes centradas en moonlighting curado, multifuncionalidad amplia y predicciones de multifuncionalidad extrema. El catálogo bibliográfico exige conservar cada afirmación y su procedencia, en lugar de convertirlas en una única etiqueta de verdad. Estas son reglas documentadas de proyecto, no verificación independiente de cada registro biológico. [S2, resumen y §3; S3, Scientific Interpretation]

El estudio debe permitir reconstruir esta cadena:

```text
artefacto de fuente → registro original → atribución y vocabulario originales
                                      ↓
                             entidad proteica reconciliada
                                      ↓
anotaciones GO y referencias → descriptores → revisión → interpretación documentada
```

La revisión produce una interpretación derivada. No sobrescribe la afirmación original ni resuelve silenciosamente etiquetas incompatibles.

### 3.2. Tres conceptos que no deben confundirse

- Amplitud de anotación GO: cantidad y diversidad de términos registrados. Puede incluir términos generales y específicos o varias descripciones relacionadas.
- Multifuncionalidad amplia: pluralidad de actividades o roles según una definición explícita y la evidencia disponible.
- Moonlighting: categoría más específica que requiere valorar funciones diferenciadas y explicaciones alternativas según 06.

GO adopta una interpretación de mundo abierto: que una anotación falte no significa que la propiedad biológica esté ausente. Además, las anotaciones estándar son afirmaciones independientes; su coaparición no vincula automáticamente una actividad con un proceso y una localización concretos. [P1, Standard GO annotations y Standard GO annotation principles]

### 3.3. Tres capas de evidencia

| Capa | Pregunta | Relación con las demás |
|---|---|---|
| Atribución de fuente MFP | ¿Quién presenta esta proteína como multifuncional y bajo qué categoría? | Conserva el criterio original. |
| Anotación GO | ¿Qué asociación producto–término se registra y cómo se sustenta? | Puede representar solo parte de las funciones atribuidas. |
| Evidencia bibliográfica revisada | ¿Qué demuestra el material realmente examinado sobre la función y su contexto? | Puede apoyar, matizar o dejar sin resolver las otras capas. |

Un código de evidencia describe el tipo de soporte de una anotación, no una puntuación universal de credibilidad. La documentación GO distingue categorías experimentales, filogenéticas, computacionales, declaraciones de autor, juicios curatoriales y anotaciones automáticas. [P2]

## 4. Objetivos y preguntas de investigación

### 4.1. Objetivo principal

Auditar y caracterizar la representación funcional y la trazabilidad de la evidencia del corpus positivo atribuido como multifuncional, relacionando anotaciones GO, descriptores computacionales y revisión bibliográfica sin equiparar ninguno de ellos a una prueba automática de multifuncionalidad o moonlighting.

### 4.2. Objetivos secundarios

1. Describir cobertura, composición y procedencia del corpus efectivamente reconciliado.
2. Caracterizar dimensiones estructurales, informativas y de coanotación.
3. Examinar sensibilidad a selección de anotaciones y dependencia documental.
4. Evaluar correspondencia entre lo descrito por GO y las funciones revisadas en literatura.
5. Determinar aportación incremental frente a conteos simples y redundancia entre métricas.
6. Producir resultados trazables y un registro explícito de no calculabilidad y de incertidumbre.

### 4.3. Preguntas de investigación

| ID | Pregunta |
|---|---|
| RQ-01 | ¿Qué entidades, atribuciones, organismos, anotaciones y referencias están efectivamente representados y qué falta? |
| RQ-02 | ¿Qué diversidad funcional describen las métricas dentro de cada aspecto GO? |
| RQ-03 | ¿Qué contexto adicional describen las asociaciones MF–BP, MF–CC y BP–CC? |
| RQ-04 | ¿Cómo cambian resultados y calculabilidad al modificar la selección de anotaciones? |
| RQ-05 | ¿Hasta qué punto los perfiles dependen de publicaciones concretas o de redundancia de anotación? |
| RQ-06 | ¿Qué concordancias, discrepancias y vacíos aparecen al contrastar con bibliografía revisada? |
| RQ-07 | ¿Qué métricas aportan información útil más allá de indicadores simples y bajo qué límites? |

La definición de hipótesis, estimadores de efecto y análisis confirmatorios pertenece a 02. Este dossier no presupone una dirección universal de efecto ni fija cortes de aceptación biológica.

## 5. Alcance, conjuntos y exclusiones

### 5.1. Conjuntos con funciones diferentes

| Conjunto | Función en esta fase | No significa |
|---|---|---|
| Corpus positivo atribuido | Objeto de caracterización y auditoría. | Positivos confirmados por el presente estudio. |
| Corpus estadístico de referencia | Estimar IC y frecuencias de asociación según 03 y 04. | Clase negativa ni grupo libre de multifuncionalidad. |
| Pool reservado | Registrar una población disponible para trabajos posteriores, si se decide conservarla. | Negativos seleccionados o validados. |

La pertenencia, identidad y posible solapamiento se resolverán en 03. No se impone aquí disyunción, una taxonomía concreta ni una regla de elegibilidad. El pool puede no ser necesario para el primer hito; su ausencia no debe bloquearlo si existe una referencia adecuada.

### 5.2. Dentro del alcance

- Reconciliación y descripción del material accesible.
- Cálculos GO cuyo significado y disponibilidad hayan sido verificados para la ejecución.
- Sensibilidad a evidencia, representación de términos y publicaciones, condicionada a los campos conservados.
- Revisión bibliográfica del material seleccionado con trazabilidad de lectura.
- Evaluación de utilidad descriptiva y de priorización de revisión.
- Síntesis de limitaciones de datos, software e inferencia.

### 5.3. Exclusiones

No son entregables: selección o validación de negativos, ratios MF:NMF, entrenamiento o evaluación de clasificadores, generación de embeddings, descubrimiento automático de moonlighting, validación de laboratorio, reconstrucción causal de todos los contextos GO, migraciones de producción ni despliegue obligatorio de un dashboard.

### 5.4. Trabajos futuros separados

Un protocolo posterior podría consumir artefactos revisados para construir datasets o evaluar modelos. Exigiría objetivos, políticas de etiquetas y controles de circularidad propios. Este dossier no autoriza esa transición ni convierte resultados inciertos en negativos.

## 6. Actores, sistemas y evidencia técnica

### 6.1. Mapa de responsabilidades

| Actor o sistema | Papel respaldado por fuentes | Relación propuesta con el estudio |
|---|---|---|
| PIS | DOCUMENTAT NO VERIFICAT: adquisición y procedencia en S1, §§3–4; repositorio e implementación no inspeccionados. | Proveer datos y enriquecimiento cuando se confirme su contrato; no se supone integración operativa. |
| BioData | VERIFICAT EN CODI: cliente PostgreSQL y utilidades GO en G2–G3. | Reutilizar acceso y cálculo donde satisfagan 03–05; no incorporar decisiones particulares como defaults universales. |
| Repositorio experimental | PROPOSTA: lugar de cohortes, protocolo, orquestación y resultados. | Consumir BioData y conservar artefactos científicos. Ubicación por validar. |
| `mfp-bibliography` | DOCUMENTAT NO VERIFICAT: catálogo de atribuciones y bibliografía, no clasificador, según S3. | Candidato a alojar el experimento o suministrar el catálogo. Integración remota no verificada. |
| PEC | DOCUMENTAT NO VERIFICAT: clasificador consumidor de embeddings según S5, §1. | Marco del proyecto; su pipeline de entrenamiento queda fuera de esta fase. |
| Revisión científica | PROPOSTA: valoración de afirmaciones y adjudicación. | Personas y responsabilidades pendientes de asignar. |

No se infiere que PIS y BioData sean el mismo código ni que todos los repositorios compartan esquema o identidad. Tampoco se confunden las capacidades de embeddings anunciadas por BioData con el alcance distinto del clasificador PEC. [G1, What Is In This Repo; S5, §1]

### 6.2. Lectura estática de BioData y límites de disponibilidad

Todas las rutas G1–G6 se consultaron en el commit fijado en cabecera. Los localizadores de §14 identifican los símbolos. «Verificado» se refiere a existencia y comportamiento visible del código, no a resultados de ejecución.

| Elemento | Hallazgo y clasificación | Consecuencia |
|---|---|---|
| Carga GO | VERIFICAT EN CODI: `GOOntology.__init__` y `load_go` utilizan `goatools` sobre un OBO y no necesitan conexión de base. [G2] | Base reutilizable; la versión efectiva OBO y dependencia deben fijarse. |
| IC y Lin | VERIFICAT EN CODI: `prepare_term_counts` construye `TermCounts`; `information_content` y rama `lin` delegan en `goatools`. [G2] | Capacidad localizada; semántica de la dependencia y perfil efectivo deben verificar 03–04. |
| Wang | VERIFICAT EN CODI: `semantic_similarity` dispone de rutas de compatibilidad y `_get_wang_ss`. Una ruta de compatibilidad puede requerir conteos tras un `TypeError`. [G2] | No basta asumir independencia operacional del entorno basándose en la tabla documental. |
| MBL | VERIFICAT EN CODI: `minimal_branch_length` delega en `goatools.semantic.min_branch_length` si está disponible y usa fallback en otro caso. [G2] | No se presume equivalencia con cualquier MBL histórica. La primera entrega es condicional a validación. |
| Agregación | VERIFICAT EN CODI: `group_similarity` calcula mejores correspondencias entre dos conjuntos. [G2] | No se identifica con divergencia interna por pares de una proteína; adaptador y contrato en 04–05. |
| Extracción | VERIFICAT EN CODI: `BioDataClient.query_all`, `get_protein_by_accession`, `get_protein_species_taxonomy` y `get_protein_go_annotations` contienen consultas de lectura. [G3] | Hay puntos de reutilización; no se han conectado a una base. |
| Referencias | VERIFICAT EN CODI: la consulta de `get_protein_go_annotations` no selecciona `publication_id`; el esquema remoto tampoco lo declara. [G3–G4] | No garantiza recuperar los PMID que el usuario declara tener en su instalación. |
| Asociaciones A | PENDENT: no se localiza un motor NPMI en el módulo GO leído. [G2] | Propuesta condicional; no se afirma ausencia en todo el repositorio. |
| Tests | VERIFICAT EN CODI: G5 contiene tests de IC, Lin, Wang, MBL y errores sobre una ontología pequeña. | Tests leídos, no ejecutados; no demuestran cobertura de todos los casos ni reproducibilidad del piloto. |

### 6.3. Divergencias y riesgos identificados

1. Esquema remoto frente al aportado por el usuario. G4 declara anotaciones sin `publication_id`, clave primaria compuesta y unicidad por proteína–GO. La salida `\d` aportada en la conversación añade publicación y una unicidad diferente. Ambos testimonios se conservan: pueden corresponder a versiones distintas. El documento 03 debe identificar el esquema real del snapshot; no se elige uno silenciosamente. [G4; C4]
2. Conversión de ausencia a cero. `_as_float` devuelve `0.0` para `None` y ciertos valores no convertibles. Esto es visible en G2 y puede ocultar estados no calculables si la dependencia devuelve tales valores. No se afirma que haya ocurrido en datos reales. Debe resolverse antes de interpretar IC o dissimilaridades. [G2, `_as_float`]
3. Fallback MBL. `_fallback_min_branch_length` incorpora ambos términos al conjunto candidato tras intersectar ancestros y elige por profundidad. La inspección revela una ruta que requiere pruebas específicas de simetría, no negatividad y pares de ramas distintas; no se ha demostrado equivalencia con la delegación. [G2, `_fallback_min_branch_length`; G5, `test_minimal_branch_length`]
4. Filtros silenciosos. `prepare_term_counts`, `filter_valid_terms` y `split_annotations_by_category` descartan determinados términos inválidos. El experimento necesitará contabilizar esas pérdidas fuera del cálculo. [G2]
5. Etiquetas de relación. `find_relation` devuelve categorías de parentesco, no los tipos ontológicos `is_a` o `part_of`. No debe presentarse como una auditoría de aristas etiquetadas. [G2, `find_relation`]

No existe protocolo formalmente aprobado localizado que permita declarar un incumplimiento normativo del software. Sí hay riesgos respecto de las necesidades de trazabilidad planteadas en la conversación, que 04, 05 y 07 deben convertir en verificaciones explícitas.

## 7. Bloques experimentales y trazabilidad de preguntas

Los bloques son PROPOSTA de organización. El procedimiento exacto y las comparaciones pertenecen a 02.

### B0. Identificación y descripción del corpus

Reconciliar entidades y atribuciones, inventariar cobertura y separar datos disponibles de declarados. Producir contabilidad de entradas, exclusiones y registros pendientes. Ninguna cifra histórica fija el tamaño efectivo.

### B1. Caracterización mediante métricas GO

Examinar MBL, IC, 1−Wang y 1−Lin por aspecto, y asociaciones MF–BP, MF–CC y BP–CC cuando exista implementación aceptada. Mantener soporte, cobertura y explicación por términos o parejas. La selección no implica independencia estadística ni superioridad de una familia.

### B2. Sensibilidad a anotaciones

Comparar las condiciones ALL y variantes EXP definidas en 02, distinguiendo cambio de valores y pérdida de calculabilidad. Los controles de reducción y representación de términos deberán separar efectos de composición y cobertura. No se fijan aquí listas de códigos ni parámetros. [S1, §6.3; P2]

### B3. Dependencia de publicaciones

Examinar qué soporte conserva el perfil cuando se retiran referencias según reglas de 02 y 03. La viabilidad depende de resolver cardinalidad y significado de `publication_id`; la operación no puede simularse si se ha perdido el soporte original.

### B4. Contraste bibliográfico

Revisar afirmaciones funcionales y las referencias que realmente las sustentan, con evidencia de lectura, contexto y discrepancias. Separar trazabilidad de la anotación, apoyo a cada función y apoyo a la atribución multifuncional. El manual 06 gobernará categorías, revisión independiente y adjudicación.

### B5. Síntesis de utilidad y limitaciones

Comparar descriptores con indicadores simples, documentar redundancias, fragilidad y casos discordantes. Una métrica puede describir especificidad sin medir rigor. Los resultados negativos sobre utilidad también constituyen un resultado válido.

### Matriz RQ → bloque → artefacto → documento responsable

| RQ | Bloque | Artefacto previsto | Documento responsable del método o contrato |
|---|---|---|---|
| RQ-01 | B0 | Inventario y tabla de cobertura con incidencias | 03; análisis descriptivo en 02 |
| RQ-02 | B1 | Resultados por proteína/aspecto y figuras | 04; comparación en 02 |
| RQ-03 | B1 | Resultados interaspecto, soporte y parejas explicativas | 04/04a; perfiles en 03 |
| RQ-04 | B2 | Comparaciones apareadas y pérdida de calculabilidad | 02; políticas de datos en 03 |
| RQ-05 | B2–B3 | Tabla de perturbaciones y dependencias documentales | 02 y 03; cálculo en 04 |
| RQ-06 | B4 | Fichas, registro de revisión y discrepancias | 06; muestreo en 02 |
| RQ-07 | B5 | Informe de aportación incremental y limitaciones | 02; criterios técnicos en 07 |

05 implementará los flujos sin redefinir las decisiones científicas de las otras columnas.

## 8. Resultados esperados como artefactos

| Artefacto | Contenido esperado, no resultado anticipado | Custodia normativa |
|---|---|---|
| Inventario de corpus | Entidades, fuentes, atribuciones y estado de reconciliación | 03 |
| Tabla de cobertura | Disponibilidad de anotaciones, referencias y métricas | 03 y 04 |
| Resultados por proteína | Valores, estados, condiciones y procedencia | 04; serialización en 05 |
| Figuras | Distribuciones, comparaciones y disponibilidad de casos | 02; generación en 05 |
| Ficha de proteína | Atribuciones, anotaciones, métricas y referencias distinguibles | 05 y 06 |
| Registro bibliográfico | Afirmaciones revisadas, evidencia consultada, decisión y justificación | 06 |
| Informe del experimento | Respuestas acotadas a RQ, incidencias y límites | 02 |
| Manifiesto de ejecución | Recursos, configuración efectiva y versiones | 03 y 05 |

Los nombres físicos, esquemas y formatos definitivos se acordarán en 03–05. No se afirma que estos artefactos ya existan. No se rellenan identificadores, checksums, resultados ni tiempos ficticios.

## 9. Primera entrega vertical

### 9.1. Objetivo de la entrega

Una cohorte pequeña identificada, una exportación BioData congelada y GO fijada deben permitir producir MBL, IC, 1−Wang y 1−Lin bajo ALL y las variantes EXP definidas en 02, junto con estados de cobertura, una tabla reproducible, dos gráficas y una ficha de proteína.

Las funciones subyacentes se han localizado en código, pero su disponibilidad para esta entrega es condicional a verificar versiones, dependencias, tratamiento de ausencia y contratos de agregación. No se anuncia que las cuatro métricas estén listas para usar por defecto. [G2–G5]

### 9.2. Condiciones de entrada y salida

| Elemento | Requisito para una futura ejecución |
|---|---|
| Cohorte | Identidad, pertenencia y atribución trazables; tamaño decidido en 02 y consignado en configuración. |
| Exportación | Versión del esquema identificada y recursos validados según 03. |
| GO | Recurso y revisión efectivos fijados y registrados, sin presuponer un OBO local existente. |
| Métricas | Definiciones verificadas por 04 y controles técnicos de 07. |
| Condiciones | ALL y variantes EXP acordadas en 02; evidencia no observable se declara, no se inventa. |
| Salida | Tabla de valores y estados, dos gráficas con denominadores y ficha trazable. |
| Reproducción | Configuración y manifiesto suficientes para reconstrucción posterior en un entorno autorizado. |

02 seleccionará las dos figuras; 05 definirá su generación. Si falta una métrica obligatoria, puede emitirse una entrega parcial, pero no declarar completado este hito sin resolución o cambio de alcance aprobado. Las asociaciones A no bloquean el primer hito; requieren su propia aceptación antes de B1 completo.

## 10. Qué este estudio no puede demostrar

1. Que una puntuación GO valida multifuncionalidad o moonlighting.
2. Que poca anotación, una métrica ausente o ausencia de literatura accesible demuestran monofuncionalidad.
3. Que todas las fuentes positivas representan el mismo concepto biológico.
4. Que varias anotaciones o varios PMID implican funciones independientes o replicaciones independientes.
5. Que la coanotación entre aspectos demuestra localización funcional, causalidad o simultaneidad.
6. Que el código leído funciona correctamente en un entorno no ejecutado o coincide con la instalación del usuario.
7. Que revisar el artículo original de una anotación constituye corroboración externa independiente.
8. Que una muestra dirigida de casos discordantes permite estimar prevalencia de errores en todo el corpus.
9. Que las métricas discriminan positivos frente a negativos: no hay evaluación de clase negativa en esta fase.
10. Que un perfil estadístico construido aquí queda automáticamente autorizado para futuros benchmarks predictivos.

Los límites 2 y 5 son coherentes con el mundo abierto y la independencia de anotaciones estándar declarados por GO. [P1]

## 11. Decisiones, riesgos y cuestiones abiertas

### 11.1. Decisiones de alcance y diseño

| ID | Decisión | Estado | Base o siguiente paso |
|---|---|---|---|
| DA-01 | Estudiar el corpus positivo; excluir negativos y entrenamiento | Alcance fijado por el encargo actual | C0; no es aprobación de todos los detalles del borrador. |
| DA-02 | Mantener las tres capas de evidencia y la procedencia original | Dirección explícita del encargo | S1–S3; concretar contratos en 03 y 06. |
| DA-03 | Reutilizar BioData sin equiparar README e implementación | Dirección del encargo | Lectura estática G1–G6. |
| DA-04 | Núcleo experimental en código y visualización desacoplada | PROPOSTA aceptada como dirección conversacional, pendiente de diseño detallado | C2; responsabilidad de 05. |
| DA-05 | Primera entrega vertical antes de ampliación | Dirección conservada del encargo | §9; aceptación concreta en 07. |
| DA-06 | No adoptar automáticamente reglas de etiquetas históricas | PROPOSTA de control de conflicto | S2/S3; revisión científica explícita. |

### 11.2. Decisiones pendientes

Los responsables que siguen son roles requeridos, no personas designadas. «Bloquea» se refiere a la ejecución afectada, no a la redacción del resto del dossier.

| ID | Pregunta e impacto | Propuesta provisional justificada | Validación requerida | ¿Bloquea el piloto? |
|---|---|---|---|---|
| DP-01 | ¿Qué entidades forman la cohorte y cómo se reconcilian? Determina denominadores. | Usar un subconjunto identificable con atribuciones preservadas, sin tomar cifras históricas como objetivo obligatorio. | Responsable científico y responsable de datos; 02–03. | Sí, el inicio del piloto. |
| DP-02 | ¿Qué esquema y versión alimentarán el snapshot? Afecta recuperación de evidencias y PMID. | Contrastar exportación real con G4 y C4 antes de fijar adaptadores; no migrar automáticamente. | Responsable BioData y datos; 03–05. | Sí para ingesta; publicaciones especialmente. |
| DP-03 | ¿Se conservaron relaciones, NOT y fuente? Afecta interpretabilidad. | Auditar ingesta; si no es recuperable, declarar el alcance degradado y solicitar aprobación explícita. | Responsable de ingesta y revisión científica; 03. | Sí para una afirmación de filtrado completo; no necesariamente para descripción limitada. |
| DP-04 | ¿Qué corpus sostiene IC y asociaciones? Afecta significado estadístico. | Referencia identificada separadamente del positivo, sin llamarla negativa; elegibilidad y solapamiento en 03. | Responsable científico y datos. | Sí para IC/Lin y asociaciones; no para inventario. |
| DP-05 | ¿Es aceptable la ruta MBL y la conversión a cero? Afecta integridad de resultados. | Verificación dirigida de G2 y dependencia, con pruebas específicas y sin parche silencioso. | Mantenedor técnico y revisor de métricas; 04/07. | Sí para completar el hito con las métricas afectadas. |
| DP-06 | ¿Qué filtros y representación de términos se comparan? Afecta comparabilidad. | Formalizar ALL y variantes EXP en 02/03, sin copiar listas normativas aquí. | Responsable científico. | Sí para B2 y hito comparativo. |
| DP-07 | ¿Qué significan valores y cardinalidad de publication_id? Afecta retirada de soporte. | Preservar bruto y resolver namespaces/relaciones antes de perturbaciones. | Responsable de datos y curación; 03/06. | No para atlas; sí para B3. |
| DP-08 | ¿Dónde vive el repositorio experimental? Afecta propiedad del código. | Evaluar mfp-bibliography como sede, conservando algoritmos genéricos en BioData. | Responsables científicos y técnicos; 05. | No para redactar; sí antes de integrar código estable. |
| DP-09 | ¿Qué manual y muestra se usarán para revisión? Afecta validez del contraste. | Separar muestra descriptiva y dirigida y revisión inicial sin scores; tamaños en 02, reglas en 06. | Coordinación científica y revisores. | No para cálculo; sí para B4. |
| DP-10 | ¿Cómo se incorpora 04a y qué umbrales se validan? Afecta asociaciones A. | Recuperar y versionar el borrador v1.1; no tratar defaults previos como aprobados. | Revisor de métricas y mantenedor BioData; 04/07. | No para primer hito; sí para asociaciones. |
| DP-11 | ¿Quién aprueba el paquete documental? Afecta gobernanza. | Asignar roles de revisión y registrar fecha y alcance de cada aceptación. | Coordinación del laboratorio/proyecto. | Sí para declarar piloto autorizado, no para trabajo preparatorio. |

### 11.3. Riesgos y respuesta prevista

| Riesgo | Respuesta y documento responsable |
|---|---|
| Fuentes heterogéneas convertidas en etiqueta única | Conservar afirmaciones y taxonomía de evidencia; 03/06. |
| Sesgo por intensidad de estudio o organismo | Estratificación y comparadores simples; 02. |
| Ausencias convertidas en cero | Estados verificables y auditoría de adaptadores; 04/05/07. |
| Misma bibliografía usada para construir y contrastar anotaciones | Separar trazabilidad y corroboración; 02/06. |
| Dependencia de versiones de goatools o rutas alternativas | Versionado y pruebas de comportamiento; 04/07. |
| Sobrediseño de infraestructura | Entrega vertical y ampliación guiada por coste observado; 05/07. |
| Recuperación solo de resúmenes | Declarar nivel de texto examinado y limitar inferencia; 06. |
| Duplicación de normas entre documentos | Custodia única y enlaces; §12. |

### 11.4. Conflictos explícitos entre antecedentes

- S1 menciona un inventario de 2.328 proteínas pendiente de reconciliación; S3 describe otro baseline de catálogo con un tamaño y una cobertura menores. Son descripciones de alcance diferente, no dos recuentos intercambiables. Ninguno fija el denominador de esta versión. DP-01 resolverá identidad y cobertura.
- S2 propone mapeos de fuentes a niveles y reglas de promoción/degradación; S3 insiste en preservar afirmaciones sin convertirlas en verdad binaria. Este estudio conserva las afirmaciones y remite cualquier valoración derivada a revisión explícita; no adopta automáticamente los mapeos de S2.
- S4 y S6 contienen objetivos de selección negativa y clasificación históricos. No se eliminan, pero no gobiernan esta fase.
- G4 y C4 discrepan en estructura de anotaciones. DP-02 impide asumir equivalencia entre repositorio e instalación.
- El antecedente 04a usa una propuesta concreta de universo y solapamiento; aquí no se fija otra política. 03 y 04 deben reconciliarla antes de ejecutar y registrar cualquier cambio justificado.

## 12. Dependencias documentales e índice anotado

Los enlaces siguientes son destinos previstos dentro del paquete documental. No prueban que esos archivos ya existan o estén aprobados.

| Documento | Qué gobierna exclusivamente | Reutilización y estado accesible |
|---|---|---|
| [02_protocolo_cientifico_y_analisis.md](02_protocolo_cientifico_y_analisis.md) | Hipótesis, muestreo, condiciones, comparaciones, análisis y límites inferenciales operativos. | Reutilizar C1 y S1 §6. Archivo formal no localizado en las fuentes accesibles. |
| [03_contrato_datos_y_recursos.md](03_contrato_datos_y_recursos.md) | Identidad, cohortes, campos, políticas de datos, perfiles y snapshots. | Reutilizar S1 §8, S2/S3 y auditoría G3–G4/C4. Archivo formal no localizado. |
| [04_especificacion_metricas.md](04_especificacion_metricas.md) | Definiciones, agregación, parámetros semánticos y casos límite. | Reutilizar G2/G5 y borrador de asociaciones. Archivo formal no localizado. |
| [05_diseno_tecnico.md](05_diseno_tecnico.md) | Componentes, adaptadores, formatos de implementación, ejecución y visualización. | Reutilizar C2, sin confundir comandos propuestos con existentes. Archivo formal no localizado. |
| [06_manual_revision_bibliografica.md](06_manual_revision_bibliografica.md) | Evidencia de lectura, categorías, reglas de revisión y adjudicación. | Reutilizar S3 y C1. Archivo formal no localizado. |
| [07_plan_implementacion_y_validacion.md](07_plan_implementacion_y_validacion.md) | Tareas, pruebas, puertas de aceptación técnica y secuencia de implementación. | Reutilizar S1 §§10–11 y riesgos G2–G5. Archivo formal no localizado. |
| [04a_asociaciones_interaspecto.md](04a_asociaciones_interaspecto.md) | Anexo candidato de 04 para las tres asociaciones; no un segundo contrato autónomo. | Existe contenido v1.1 en la conversación bajo otro nombre; archivo binario previo no recuperado en esta sesión ni anexo con este nombre localizado. |

El contenido previo de `Especificacion_metricas_asociacion_GO_BioData_v1.1.md` consta en el historial de esta conversación. Se puede reutilizar como borrador identificando su procedencia, no como archivo aprobado alojado en un repositorio. Su incorporación a 04a requiere recuperación/versionado y revisión de coherencia con 03.

### 12.1. Flujo de dependencia

```text
01: objetivo y alcance
  ├── 02: protocolo y análisis
  ├── 03: datos y recursos
  └── 06: revisión bibliográfica
          ↓ contratos coordinados
04 + 04a: significado de los cálculos
          ↓
05: implementación de esos contratos
          ↓
07: pruebas y aceptación del piloto
```

El flujo no obliga a terminar documentos completos en cascada. Exige que cada etapa que vaya a ejecutarse tenga sus decisiones mínimas resueltas y sus referencias cruzadas consistentes.

Las reglas viven en los documentos responsables. Los valores efectivos de ejecución vivirán en `configs/pilot.yaml` y en el manifiesto. No se ha localizado ni ejecutado esa configuración. Este dossier no incluye una configuración ficticia ni asigna valores de cohorte, soporte, cobertura o remuestreo.

## 13. Criterios de finalización y aceptación del dossier

La aceptación de 01 es documental y no equivale a aceptación del software o del experimento.

| ID | Comprobación verificable | Evidencia de cumplimiento requerida |
|---|---|---|
| AC-01 | Alcance positivo y exclusiones inequívocos | §§1, 4, 5 y 10 consistentes. |
| AC-02 | Preguntas trazables a bloques y artefactos | Matriz de §7 sin RQ huérfanas. |
| AC-03 | Sistemas y propuestas separados | Tabla §6 con fuentes y estados. |
| AC-04 | Lectura remota identificable | Commit, rutas y símbolos de §14; divergencias registradas. |
| AC-05 | Antecedentes accesibles y ausentes declarados | Inventario §14 sin atribuir aprobación inexistente. |
| AC-06 | No duplicación normativa | §12 asigna fórmulas, filtros y políticas a sus responsables. |
| AC-07 | Pendientes accionables | Cada DP incluye pregunta, impacto, propuesta, validador y bloqueo. |
| AC-08 | Primera entrega verificable | §9 y condiciones de aceptación futura en 07. |
| AC-09 | Límites explícitos | §10 y riesgos sin conclusiones biológicas anticipadas. |
| AC-10 | Revisión formal registrada | Responsable, revisores, fecha y observaciones de aprobación aún pendientes. |

La revisión editorial realizada al redactar no satisface AC-10. El documento permanece «borrador para revisión, no aprobado». Se puede continuar la redacción de 02–07 con los pendientes visibles sin fingir autorización de una ejecución.

## 14. Inventario de fuentes y limitaciones de consulta

### 14.1. Código y documentación remota consultados

Repositorio: https://github.com/CBBIO/BioData

Revisión fijada: https://github.com/CBBIO/BioData/commit/ed073bd4df680a3b45ee69943916e196d28b63b6

El connector permitió leer árbol raíz, directorios CBBIO y tests y archivos siguientes. La recuperación web inicial de la portada falló; no impidió consultar por GitHub. El commit corresponde a la revisión recuperada, no a una certificación de la versión instalada por el usuario.

| ID | Localizador y secciones/símbolos | Alcance real de lectura |
|---|---|---|
| G1 | [README.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/README.md), What Is In This Repo; Documentation; Running Tests | Leído como documentación, no prueba de ejecución. |
| G2 | [CBBIO/GO.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/GO.py), `GOOntology`, `prepare_term_counts`, `information_content`, `semantic_similarity`, `group_similarity`, `minimal_branch_length`, `_fallback_min_branch_length`, `_as_float` | Código leído completo en la respuesta del connector. No se inspeccionó internamente el código de goatools. |
| G3 | [CBBIO/BioData.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/BioData.py), `BioDataClient.query_all`, `transaction`, `get_protein_by_accession`, `get_protein_go_annotations`, `get_protein_species_taxonomy` | Respuesta truncada en parte posterior; afirmaciones limitadas a símbolos visibles. `transaction` no fija por sí mismo aislamiento de snapshot y depende de autocommit. |
| G4 | [sql/schema.sql](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/sql/schema.sql), `CREATE TABLE public.protein_go_term_annotation`, constraints; tablas `protein`, `accession`, `go_terms` | Esquema leído; no representa necesariamente la base desplegada. |
| G5 | [tests/test_go.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_go.py), fixtures y tests de IC, Lin, Wang, MBL, errores y BMA | Tests leídos, nunca ejecutados. BMA significa Best Match Average, mejores correspondencias entre conjuntos. |
| G6 | [docs/GO.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/docs/GO.md), Loading the Ontology; Information Content and Semantic Similarity; Full Workflow Example | Documentación leída; ejemplos no ejecutados. |

No se afirma auditoría exhaustiva de todo el repositorio ni ausencia global de funciones no localizadas. No se inspeccionaron todos los tests de cliente ni los módulos probing y embeddings, al no ser necesarios para definir este alcance.

### 14.2. Materiales de proyecto y conversación

| ID | Fuente, ruta o localizador legible | Disponibilidad y uso |
|---|---|---|
| S1 | `Dossier_extensio_PIS_BioData_PEC_v0.1.md`, 2026-10-19, §§1–8 y 10–15 | Adjunto accesible en el contexto de conversación; antecedente reutilizado, no aprobado. |
| S2 | `canonical_multifunctional_protein_data_dossier.md`, versión 1.0, 2026-08-29, resumen y §§1–4, 7 | Project File localizado; contenido recuperado parcialmente por exploración. Sus afirmaciones de enforcement no se verificaron en código. |
| S3 | `mfp_bibliographic_catalog_vision.md`, Purpose; Scope and Non-Goals; Scientific Interpretation; Current Baseline | Project File localizado y leído en la exploración. Baseline documentado, no ejecutado ni reconciliado aquí. |
| S4 | `dataset_designer_functional_contract.md`, versión 1.0, 2026-08-04, §§2–6 y 10–12 | Project File localizado. Antecedente histórico de construcción de datasets, no protocolo de esta fase. |
| S5 | `PEC_FUNCTIONAL_CONTRACT.md`, §1 y responsabilidades | Project File localizado; alcance del clasificador documentado, sin reinspección remota de PEC. |
| S6 | `PEC_PRAGMATIC_RESEARCH_AND_ORGANIZATION_GUIDE.md`, versión 1.0, 2026-08-29, §§1–5 | Project File localizado; plan histórico MF:NMF excluido del alcance actual. |
| C0 | Encargo de redacción de `01_dossier_experimento.md`, conversación PEC, 2026-10-26 21:16 CET | Fuente de alcance actual y condiciones de redacción. |
| C1 | Propuesta de experimentación y respuesta asociada, conversación PEC, solicitud 2026-10-26 20:29 CET | Accesible en historial; propuesta, no protocolo aprobado. |
| C2 | Propuesta de infraestructura y respuesta asociada, conversación PEC, solicitud 2026-10-26 20:56 CET | Accesible en historial; diseño conceptual no ejecutado. |
| C3 | Generación de especificación v1.1, conversación PEC, solicitud 2026-10-26 13:49 CET; nombre `Especificacion_metricas_asociacion_GO_BioData_v1.1.md` | Contenido textual visible en historial; archivo generado previamente no disponible como entrada independiente en el inventario actual. No se afirma checksum ni ubicación en GitHub. |
| C4 | Salidas `\dt` y `\d protein_go_term_annotation` y extracto de API aportados por el usuario, solicitud de infraestructura 2026-10-26 20:56 CET | DOCUMENTAT NO VERIFICAT para la instalación. No hubo conexión a esa base. |

Otros contratos de Dataset Designer figuran en el inventario, pero no se atribuye contenido no recuperado ni se presume equivalencia entre versiones.

### 14.3. Fuentes científicas primarias de documentación consultadas

- P1. Gene Ontology Consortium, «Introduction to GO annotations», https://geneontology.org/docs/go-annotations/ ; página consultada el 2026-10-26. Base de independencia de anotaciones, mundo abierto, relaciones y referencia mínima.
- P2. Gene Ontology Consortium, «Guide to GO evidence codes», https://geneontology.org/docs/guide-go-evidence-codes/ ; página consultada el 2026-10-26. Base de categorías de evidencia y distinción entre experimental y alto rendimiento.

No se han revisado artículos individuales de las proteínas ni se atribuyen PMID, resultados experimentales o validación bibliográfica concreta. La revisión de fórmulas y bibliografía metodológica específica corresponde a 04; aquí no se inventan DOI ni referencias para sustituirla.

### 14.4. Recursos no accesibles o no localizados

- Base PostgreSQL desplegada, datos y credenciales: NO ACCESSIBLE en esta sesión; no se intentó conectarse.
- Repositorio e implementación de PIS: no localizados en las fuentes accesibles inspeccionadas.
- Código remoto de mfp-bibliography y su integración efectiva con BioData: no inspeccionado; documentación accesible S3, implementación no verificada.
- Archivos formales 02–07 y anexo con nombre `04a_asociaciones_interaspecto.md`: no localizados en las fuentes accesibles.
- Archivo descargable previo v1.1 como entrada recuperable: no localizado en el inventario actual; sí consta su contenido en conversación C3.
- Exportaciones congeladas, identificadores de ejecución, checksums y resultados del piloto: no aportados ni generados.
- Texto completo de publicaciones de proteínas individuales: no consultado.

Estas limitaciones impiden certificar disponibilidad operacional y conclusiones biológicas, pero no impiden definir el alcance ni documentar dependencias reales.

## 15. Comprobación final de coherencia

- Con 02: se definen RQ y bloques, no hipótesis confirmatorias, filtros ni parámetros efectivos.
- Con 03: se separan conjuntos y se registran divergencias de esquema, sin imponer identidad, elegibilidad o solapamiento.
- Con 04: se enumera el catálogo y su estado técnico, sin fijar fórmulas ni agregaciones normativas; 04a es un anexo candidato no aprobado.
- Con 05: se distinguen sistemas y capacidades verificadas, sin convertir la arquitectura conversacional en implementación existente.
- Con 06: se exige trazabilidad de afirmaciones y lectura, sin inventar revisión de literatura ni reglas de adjudicación aprobadas.
- Con 07: se define el objetivo de la primera entrega y sus dependencias, sin declarar tests ni experimentos ejecutados.

Resultado: dossier de entrada redactado con alcance positivo explícito y pendientes localizados. La aprobación, asignación de responsables y autorización del piloto siguen pendientes.
