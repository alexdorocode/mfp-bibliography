# Manual de revisión bibliográfica de afirmaciones funcionales y atribuciones de multifuncionalidad

| Campo | Valor |
|---|---|
| Archivo | `06_manual_revision_bibliografica.md` |
| Versión | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha | 2026-10-26 |
| Responsable | Pendiente de asignar |
| Revisores científicos, adjudicador y coordinación | Pendientes de asignar |
| Proyecto | PEC; auditoría del corpus positivo atribuido como multifuncional |
| Fuentes | Inventario de §17: catálogo bibliográfico, antecedentes, código remoto y fuentes primarias |
| Revisión BioData consultada | `ed073bd4df680a3b45ee69943916e196d28b63b6` |
| Dependencias | 01 alcance; 02 muestreo/análisis; 03 identidad/datos; 04/04a métricas; 05 infraestructura; 07 aceptación |

> [!NOTE]
> **Document Status & Current Role (Historical Literature Curation Manual)**:
> This document is a historical literature curation manual. It does **not** describe current repository implementation; initial assumptions regarding curation as an ingestion gate have been superseded by the Non-Blocking Preservation Principle, and formal operational approval remains pending under Gate G2.
> - **Recovered Content**: The literature review workflow (the seven linked evidentiary units, non-destructive curation, reference resolution, blinding protocol, and evidence adjudication rules) has been recovered as a proposed procedure in [`docs/curation/literature-curation-manual.md`](../curation/literature-curation-manual.md) (proposed procedure pending approval).
> - **Traceability**: The original Spanish text is retained intact for curatorial methodology traceability. Section-level mappings are detailed in the [Documentation Recovery Map](../reports/documentation-recovery-map.md#81-reconciled-section-level-recovery-matrix).

Este manual propone un procedimiento replicable de contraste bibliográfico. No ejecuta una revisión completa, no valida proteínas reales ni convierte scores GO en decisiones biológicas. No se han consultado artículos individuales del corpus para adjudicar funciones, ejecutado experimentos, pruebas, consultas a la base del usuario o notebooks. No se han modificado repositorios ni creado commits, issues o pull requests.

El texto es desarrollado y utilizable para preparar la calibración, pero su adopción operacional requiere asignación de roles, resolución de pendientes y aprobación. Las reglas nuevas son PROPOSTA, no un consenso universal ni un protocolo ya aprobado.

## Índice

1. Propósito, autoridad y leyenda
2. Catálogo, revisión y decisión: unidades vinculadas
3. Evidencia técnica disponible y limitaciones de origen
4. Preparación de material y búsqueda reproducible
5. Flujo de extracción y ficha de evidencia
6. Clasificación del soporte y evaluación de ensayos
7. Categorías de revisión en ejes separados
8. Multifuncionalidad amplia y compatibilidad con moonlighting
9. Procedimiento de síntesis y situaciones difíciles
10. Revisión independiente, calibración y cegamiento
11. Desacuerdos, adjudicación y actualización
12. Acuerdo entre revisores
13. Plantilla propuesta functional_claims.csv
14. Plantilla propuesta review_records.csv
15. Ejemplos sintéticos resueltos
16. Decisiones, riesgos y criterios de finalización
17. Inventario de fuentes, accesibilidad y límites
18. Dependencias y comprobación final de coherencia

## 1. Propósito, autoridad y leyenda

El objetivo es que dos revisores puedan valorar la misma afirmación mediante reglas comunes, localizar el soporte que han utilizado y documentar discrepancias sin estar obligados a concluir que una proteína es o no es multifuncional. La falta de texto o soporte localizado no significa refutación.

Se audita un corpus positivo atribuido por fuentes, no una clase positiva confirmada por inclusión. No se construyen negativos ni se entrenan clasificadores. Referencia estadística y pool reservado mantienen sus funciones de 01/03; no son objetos de clasificación negativa por este manual.

01 define objetivo/alcance; 02 selecciona muestras, compara resultados y separa desarrollo/evaluación; 03 resuelve identidades y referencias; 04/04a define métricas; 05 transporta y conserva los registros; 06 define el juicio bibliográfico; 07 acepta implementación. Este manual no cambia fórmulas GO ni selecciona un nuevo tamaño de muestra.

| Término | Significado |
|---|---|
| MFP | Proteína multifuncional en sentido amplio; una atribución original no equivale a confirmación. |
| GO | Gene Ontology. |
| MF / BP / CC | Función molecular / proceso biológico / componente celular. MF no significa proteína multifuncional. |
| Claim | Afirmación concreta cuyo contenido y procedencia se conservan. |
| PMID / DOI / GO_REF | Identificador PubMed / identificador de objeto digital / referencia interna GO. |
| GAF | Gene Association File; su campo Reference tiene semántica específica. |
| Evidencia directa | Resultado sobre la entidad y propiedad concretas; no implica por sí solo función fisiológica o suficiencia. |
| Evidencia contextual | Resultado que restringe o apoya contexto sin establecer la propiedad completa. |
| Transferencia | Inferencia desde otra entidad, especie, forma o sistema; debe identificarse. |
| Adjudicación | Resolución documentada de desacuerdo después de preservar revisiones independientes. |
| Cegamiento | Ocultación de scores y selección derivada a revisores iniciales; no anonimización molecular imposible. |

Estados de evidencia documental: VERIFICAT EN CODI = lectura estática; DOCUMENTAT NO VERIFICAT = descripción no comprobada operacionalmente; PROPOSTA = diseño; PENDENT = información/decisión por resolver; NO ACCESSIBLE = fuente no consultable, no inexistente.

## 2. Catálogo, revisión y decisión: unidades vinculadas

`mfp_bibliographic_catalog_vision.md` describe un catálogo de entidades, afirmaciones originales y procedencia; explícitamente no crea negativos ni un benchmark. La fuente conserva su categoría y la revisión añade una interpretación derivada, sin sobrescribirla [S1, Purpose; Scientific Interpretation].

| Unidad | Qué contiene | Enlaces requeridos | Qué no autoriza |
|---|---|---|---|
| Proteína/entidad | Identidad reconciliada, organismo y ámbito de forma | entity_id y crosswalk 03 | Transferir toda evidencia de una familia a cada miembro. |
| Afirmación funcional de trabajo | Una propiedad, entidad y contexto definidos | working_claim_id, fuente o anotación origen | Tratar varios sinónimos GO como funciones distintas. |
| Anotación GO | Asociación producto–concepto, relación, evidencia y referencia disponibles | annotation_row_id y release GO | Dar soporte a todos los roles de la proteína porque tiene un PMID. |
| Atribución multifuncional original | Lo que una fuente dice del conjunto de funciones | source_claim_id, registro, fuente/release | Reemplazar criterio fuente por uno universal no acordado. |
| Publicación/referencia | Artículo o referencia identificada y reconciliada | reference_id e IDs según 03 | Presumir lectura o resultado experimental. |
| Unidad de evidencia | Resultado específico de un experimento/material | pasaje/figura/página y contexto | Usar el título como evidencia de todo el artículo. |
| Decisión de revisión | Juicio de revisor sobre un target y material precisos | review_record_id, manual/versiones y justificación | Borrar decisiones previas o generar certeza con un score. |

Una publicación puede sustentar una función y no otra. Varias publicaciones pueden reutilizar los mismos datos. Varias anotaciones pueden estar basadas en un mismo resultado. Una revisión narrativa puede señalar literatura primaria, pero no se cuenta como experimento independiente de los que cita.

La plantilla functional_claims de §13 define afirmaciones de trabajo, no sustituye la tabla `source_claims` de 03. Distinguir `working_claim_id` y `source_claim_id` evita confundir extracción analítica y afirmación original.

## 3. Evidencia técnica disponible y limitaciones de origen

Lectura remota de BioData en el commit de cabecera, comenzando por README y árbol:

- VERIFICAT EN CODI: `sql/schema.sql` define `protein_go_term_annotation` con id, protein_id, go_id y evidence_code, sin publication_id, y unicidad por pareja proteína–GO [G3]. No demuestra contenido del servidor.
- DOCUMENTAT NO VERIFICAT: la salida de esquema del usuario añade publication_id y otras restricciones. 03 debe identificar la variante del snapshot; no se elige una silenciosamente [C4].
- VERIFICAT EN CODI: `BioDataClient.get_protein_go_annotations(protein_id)` consulta términos y evidencias, pero no devuelve publicación ni clave raw; `GOAnnotation` en types.py tampoco contiene referencias [G2/G4]. No usar esa salida como ficha bibliográfica completa.
- VERIFICAT EN CODI: métodos `get_protein_by_accession`, `get_protein_species_taxonomy` y `get_protein_sequences` permiten lectura de metadatos; no demuestran namespace global ni identidad de formas [G2].
- VERIFICAT EN CODI: `tests/test_biodata_integration.py` contiene pruebas GO/proteína condicionadas a entorno y datos, con skip posible. No se han ejecutado ni demuestran conservación de cada PMID o una revisión manual [G5].

La documentación `docs/BioData.md` describe consultas GO, no acredita un módulo de adjudicación. No se ha inspeccionado todo el repositorio para afirmar ausencia global de curación; el registro de revisión de este manual sigue siendo PROPOSTA [G6].

Roles: BioData proporciona acceso/cálculo localizado; PIS figura en el dossier inicial como adquisición/procedencia propuesta, sin implementación aquí inspeccionada; mfp-bibliography tiene papel de catálogo documentado y es sede experimental candidata; PEC es el marco del proyecto, no el revisor ni un clasificador ejecutado. No se asigna a PIS recuperación de textos, PMID o curación no verificada.

## 4. Preparación de material y búsqueda reproducible

### 4.1. Paquete de revisión

La coordinación genera desde recursos de 03 y selección de 02 un paquete versionado con:

- Clave ciega de revisión y vínculo interno controlado a entidad/target.
- Identidad molecular necesaria, organismo, forma y posibles ambigüedades.
- Claims y anotaciones a revisar, conservando texto bruto y formulación atómica de trabajo.
- Referencias GO y de fuentes MFP identificadas por procedencia separada.
- Definición GO y release cuando se evalúa una anotación, no solo el nombre del término.
- Estado de acceso a referencias y reglas del nivel de búsqueda autorizado.
- Versión de manual e inventario de targets previstos.

No entregar scores, rankings, cambios de métricas, pares «discordantes», colores de alerta o estratos de score antes de la primera decisión. Tampoco revelarlos mediante nombre de archivo, carpeta, orden de presentación o notas. Una ficha genérica que motive «caso de alta divergencia» rompe el cegamiento aunque no muestre el número.

Las categorías de fuente pueden inducir expectativa. Ocultar sellos operativos como GOLD y prioridades derivadas cuando no sean necesarios; el texto fuente que deba contrastarse se conserva y su exposición se registra. No se promete cegamiento completo al nombre de proteína, autores o contenido del artículo.

### 4.2. Referencias e identidad

Aplicar 03 para publication_id local, PMID/DOI y alias. No asignar namespace por apariencia. En GAF 2.2 varios IDs en Reference pueden identificar un solo artículo; no multiplicar soporte por alias [P4, Reference]. Referencias GO y MFP pueden apuntar al mismo documento sin compartir el mismo papel.

Si un ID resuelve a otro artículo, registrar `reference_mismatch` y solicitar corrección de crosswalk. No sustituirlo silenciosamente por una publicación cuyo título parezca apropiado. Si se corrige antes de revisar, publicar nueva versión de paquete y conservar la anterior.

### 4.3. Búsqueda delimitada y registro de acceso

Propuesta inicial: primero referencias ya vinculadas; después, solo si lo autoriza el plan de 02, rastreo de las citas primarias que sustentan la afirmación y búsqueda suplementaria con estrategia congelada. No exigir una revisión sistemática exhaustiva para esta auditoría acotada.

Registrar por intento: target, recurso consultado, consulta o identificador exacto, fecha, filtros/corte, resultado de acceso y documentos nuevos hallados. Usar canales legales: editor, repositorios abiertos, biblioteca autorizada o contacto documentado. No eludir paywalls, credenciales o restricciones.

El presupuesto de búsqueda y las condiciones de parada se fijarán en configuración antes de revisión: por ejemplo, agotar referencias vinculadas y rutas de acceso permitidas hasta el límite operativo aprobado. No se inventa aquí un tiempo por proteína. Un revisor puede registrar `budget_exhausted` y una decisión no resuelta sin inferir que no hay literatura.

Nuevas referencias se guardan como ampliación versionada, con su ruta de descubrimiento y fecha. No se incorporan retrospectivamente al snapshot GO original ni alteran condiciones de puntuación. La revisión tendrá fecha de corte y estado de búsquedas, no un «siempre actualizado» indeterminado.

## 5. Flujo de extracción y ficha de evidencia

### 5.1. Secuencia de revisión de cada target

1. Verificar qué afirma exactamente el target: actividad, proceso, localización, efecto o multifuncionalidad.
2. Verificar correspondencia molecular: organismo, gen/parálogo, accession, forma, secuencia y constructo cuando estén disponibles.
3. Comprobar documento y nivel de texto accesible; consultar resultados, métodos y suplemento pertinente cuando estén disponibles.
4. Extraer cada experimento que aporta o limita soporte. Separar resultados de los autores y conclusiones del revisor.
5. Asignar tipo de soporte, contexto, suficiencia y estado de identidad según §§6–7.
6. Para atribuciones multifuncionales, evaluar funciones individuales antes de su relación (§8).
7. Registrar pasaje/localizador, controles, limitaciones y búsqueda incompleta. Bloquear la decisión inicial antes de discutirla con el otro revisor.

No basta leer un abstract para declarar que se han examinado los métodos ni reutilizar una frase de introducción como resultado del artículo. GO recomienda curar a la definición del término, identificar el objeto de anotación y el tipo de evidencia, no solo el nombre [P1, Gene product; Approaching an article; Choosing the right GO term].

### 5.2. Ficha de extracción desarrollada

| Bloque | Contenido a registrar | Regla de interpretación |
|---|---|---|
| Identidad | Entidad, organismo/cepa si pertinente, forma, isoforma/parálogo, constructo, etiqueta, límites de secuencia | «Gen con el mismo nombre» no basta para identidad. |
| Afirmación fuente | Cita breve o paráfrasis marcada, categoría y localizador | No reescribir el claim como si ya estuviera comprobado. |
| Propiedad funcional | Actividad/reacción, blanco, proceso, localización o fenotipo, con granularidad explícita | No elevar localización a actividad ni efecto global a función molecular. |
| Contexto | Tejido/célula, estado fisiológico, condición, compartimento, concentración/tiempo relevantes | Contextos distintos pueden explicar discrepancias. |
| Ensayo | Qué se mide, preparación, lectura y unidades informadas | Distinguir medición de inferencia. |
| Intervención | Knockout, mutación, inhibición, rescate, sobreexpresión u observación; perturbaciones combinadas | Evaluar especificidad y efectos secundarios relevantes. |
| Controles | Negativos/positivos del ensayo, vehículo, pureza, expresión, viabilidad, carga, localización o rescate pertinentes | «No reportado/no consultable» distinto de «control ausente demostrado». |
| Resultado | Dirección y magnitud/cifras si necesarias y leídas, variabilidad y tipo de réplica si se informa | No inventar n, p, tamaños de efecto o réplicas biológicas desde barras de error. |
| Trazabilidad | Figura/panel, tabla, suplemento, sección, página o párrafo | Debe permitir a otro revisor localizar el soporte. |
| Interpretación autores | Conclusión atribuida al artículo | Puede exceder lo que el revisor considera sustentado. |
| Interpretación revisor | Inferencia explícita y razón, incluyendo alternativas | Separada de cita/paráfrasis fuente. |
| Limitaciones | Constructo, contexto artificial, confusión por contaminación/homología, material no accesible | No reducir todos los problemas a una puntuación. |
| Independencia documental | Experimento nuevo, mismo dataset, revisión o relación desconocida con otras referencias | Distintos PMID no garantizan replicación. |

No es obligatorio un tipo universal de ensayo para todas las funciones. Los controles relevantes se justifican para la inferencia concreta. La ausencia de una demostración causal estricta limita la atribución, pero no borra un resultado contextual legítimo.

## 6. Clasificación del soporte y evaluación de ensayos

El tipo de soporte se asigna por unidad de evidencia, no a toda la proteína. No es una escala ordinal universal.

| Código | Definición e inclusión | Exclusiones/casos fronterizos |
|---|---|---|
| `direct` | La entidad adecuada es ensayada y la lectura mide la propiedad reclamada dentro del contexto definido | Medir localización puede ser directo para CC, no para una actividad enzimática. Un constructo puede medir actividad propia pero no probar la forma endógena. |
| `contextual` | Observación o perturbación vincula la entidad a un contexto/proceso sin medir o aislar la propiedad completa | Expresión diferencial, co-localización o fenotipo global no prueban por sí solos una segunda actividad autónoma. Puede ser soporte adecuado para un claim de contexto más estrecho. |
| `transferred` | La atribución al target se infiere desde otra entidad/forma/especie mediante relación identificada | Un ensayo directo en el homólogo sigue siendo transferencia para el target. Registrar donor y regla, no renombrarlo direct. |
| `author_statement` | La fuente afirma la propiedad sin resultado verificable localizado en el material revisado | Buscar referencia primaria si el procedimiento lo permite. No equivale a experimento. |
| `mixed` | Síntesis con varios tipos documentados, sin tipo único | Solo para síntesis; no evita separar las unidades experimentales. |
| `not_assessable` | Falta material o correspondencia suficiente para clasificar el soporte | No soporte negativo. |

### 6.1. In vitro y relevancia fisiológica

Un ensayo bioquímico in vitro con entidad/pureza/controles adecuados puede sustentar directamente una actividad en esas condiciones. No demuestra automáticamente que sea una función fisiológicamente relevante. Registrar origen, concentraciones, sustratos, tasas si informadas, condiciones y alternativas como actividad inespecífica/contaminación.

Evidencia fisiológica puede incluir observación y perturbación en un sistema pertinente, con controles y correspondencia molecular suficientes. Un fenotipo de pérdida de función puede ser indirecto o pleiotrópico y no asigna por sí solo la actividad molecular causal. El rescate refuerza una atribución según diseño, pero no garantiza que dos funciones estén separadas.

Sobreexpresión o localización ectópica no se invalidan por nombre; se registran sus límites para extrapolación endógena. Una función puede depender de complejos o interacciones: «autónoma» no exige proteína aislada funcionando sin socios.

### 6.2. Homología y evidencia transferida

Registrar donor, organismo/forma, evidencia original, relación de homología afirmada y limitaciones. No deducir conservación de moonlighting porque se conserve la función principal. MoonProt enfatiza que el homólogo puede o no compartir ambas funciones [P2, Information included about individual proteins; P3].

Los códigos GO describen la base de anotación y no sustituyen la lectura. Se conserva código original, y el revisor puede señalar discordancia sin reescribirlo en el snapshot. Una inferencia por interacción física puede apoyar unión o asociación a complejo, no necesariamente regulación, catálisis o función autónoma [P1].

## 7. Categorías de revisión en ejes separados

No se produce un score numérico global de confianza. Los siguientes ejes son obligatorios cuando proceden; los valores desconocidos son explícitos, no ceros.

### 7.1. Identidad del objeto examinado

| Valor | Criterio |
|---|---|
| `matched` | Entidad y ámbito molecular/contextual suficientes para relacionar evidencia y target. |
| `partial_match` | Correspondencia probable, pero falta un componente relevante como forma o secuencia exacta; explicar. |
| `different_entity` | Evidencia corresponde a otro homólogo, organismo o forma no equivalente al target. Puede alimentar transferred, no direct del target. |
| `unresolved` | Información insuficiente para decidir identidad. |

Esto es juicio de correspondencia bibliográfica, no modificación del crosswalk 03. Una corrección requiere incidencia y revisión de datos con trazabilidad.

### 7.2. Naturaleza de la propiedad reclamada

Valores nominales: `molecular_activity`, `process_contribution`, `localization`, `binding_or_complex`, `phenotype_or_effect`, `structural_role`, `multiple_properties`, `unclear`.

Se descompone `multiple_properties` en claims atómicos cuando sea viable. Dos procesos pueden reflejar la misma actividad; binding puede ser función relevante o solo interacción observada según especificidad, consecuencias y definición. No se cuenta automáticamente cada GO ID como función.

### 7.3. Contexto de evidencia

Campos separados:

- `assay_context`: in_vitro / cellular / organismal / computational / mixed / unknown.
- `physiological_relevance`: supported / plausible_not_demonstrated / not_established / conflicting / not_assessable.
- `evidence_limitations`: lista de incidencias descriptivas, no penalización aritmética.

`not_established` significa que lo revisado no establece relevancia fisiológica, no que sea fisiológicamente imposible. `supported` requiere explicar qué datos la sostienen; no se activa por tener un organismo en la ficha.

### 7.4. Correspondencia del resultado con el claim

| Valor | Inclusión | Exclusión y frontera |
|---|---|---|
| `supports` | Evidencia localizada respalda el contenido y contexto declarado | No implica suficiencia global ni independencia funcional. |
| `partially_supports` | Respalda una parte o formulación más estrecha | Explicitar qué parte permanece sin resolver. |
| `not_addressed` | Documento examinado no trata la propiedad del target | No refuta la propiedad. |
| `opposes` | Resultado interpretable es contrario al claim bajo el mismo ámbito/contexto | No usar por silencio del artículo o ensayo sin sensibilidad acreditada. |
| `mixed` | Hay resultados favorables y opuestos/discordantes relevantes | Conservar unidades por separado, no decidir por mayoría de papers. |
| `not_assessable` | No hay texto o identidad/material suficiente | No convertir en not_addressed si no se pudo comprobar contenido. |

### 7.5. Suficiencia y limitaciones de la evidencia revisada

| Valor | Regla operacional |
|---|---|
| `sufficient_within_context` | Claim acotado respaldado con identidad adecuada, evidencia pertinente y limitaciones que no impiden esa inferencia. Localizador y justificación obligatorios. |
| `partial` | Parte del claim sustentada o extrapolación necesaria no resuelta. |
| `insufficient` | Material examinado no basta para sostener el claim, aunque puede existir evidencia no consultada. |
| `conflicting` | Evidencia pertinente incompatible no resuelta dentro del conjunto revisado. |
| `not_evaluable` | Acceso, referencia, identidad o nivel de detalle impiden valoración. |

La suficiencia se refiere al target y material revisados, no a un sello de calidad de revista o a todos los resultados del artículo. No imponer dos papers como requisito universal: uno puede contener evidencia suficiente o varios repetir la misma evidencia insuficiente. Un texto completo con métodos débiles no adquiere suficiencia por ser accesible.

### 7.6. Estado de acceso y completitud

`access_status`: full_text / abstract_only / metadata_only / inaccessible / reference_unresolved.

`review_completion`: complete_for_declared_scope / partial / blocked. «Complete» significa que se ha aplicado el alcance de revisión declarado, no que se conoce toda la literatura. `issue_codes` puede incluir reference_mismatch, missing_methods, form_scope_mismatch, retraction_notice, duplicate_data, conflicting_context, budget_exhausted, blinding_breach u otros códigos versionados.

Retracción/corrección: registrar aviso y alcance del cambio con fuente verificada; no asumir que todo estudio relacionado es falso. Evidencia afectada se reevalúa, no se borra. Una duda no documentada no se presenta como mala conducta.

## 8. Multifuncionalidad amplia y compatibilidad con moonlighting

### 8.1. Fuente y definición operacional

Se usa como referencia explícita, no consenso impuesto, la selección de MoonProt 3.0: funciones bioquímicas/biofísicas distintas, fisiológicamente relevantes, de una misma cadena; no efectos pleiotrópicos, varios aspectos de una función, misma función en distintas localizaciones, variantes de splicing o miembros distintos de una familia [P2, Materials and Methods]. La página oficial también excluye atribuciones explicadas por fusiones y fragmentos proteolíticos [P3].

El dossier canónico documenta fuentes con multifuncionalidad amplia y predicciones, no todas con ese criterio [S2]. Se conserva cada etiqueta original. No se degrada un registro fuente porque use un concepto más amplio: se informa la relación entre su definición y la operacional adoptada aquí.

### 8.2. Evaluación de funciones y pares

Primero revisar cada función individual. Después crear una síntesis sobre al menos dos working_claim_id, no inferirla a partir de número de referencias/GO. Para el par registrar:

1. ¿Son propiedades diferenciadas y no sinónimos, ancestro–descendiente o pasos descriptivos de una misma actividad?
2. ¿Existe evidencia en la misma entidad y ámbito de forma, no una función por parálogo/isoforma?
3. ¿Está sustentada la relevancia fisiológica de ambas según el material disponible?
4. ¿Puede explicarse la pluralidad por una misma actividad con efectos en varios procesos o lugares?
5. ¿Hay explicaciones de fusión, producto alternativo o fragmentación que cambien la unidad molecular?
6. ¿Qué datos permiten separar las actividades/roles y qué alternativas permanecen?

Pruebas de separación de función mediante mutaciones, rescates o condiciones específicas pueden fortalecer el razonamiento, pero no se exigen como único mecanismo universal ni se infieren si no están en el artículo. Las funciones pueden ejercerse en condiciones, conformaciones o asociaciones distintas sin ocurrir simultáneamente [P2, Discussion].

### 8.3. Casos frontera y explicaciones

| Situación | Tratamiento |
|---|---|
| Proteína multidominio/fusión con actividades separadas | Puede sustentar multifuncionalidad amplia, pero si la pluralidad está explicada por fusión no satisface el criterio MoonProt usado. No deducir fusión solo por tener dominios. |
| Una función por isoforma | No atribuir las dos a una misma cadena por agregación de gen; identidad de forma debe resolverse. |
| Una función en precursor y otra en fragmento | No asumir ambas en la cadena intacta; registrar formas y explicación por procesamiento. |
| Tag/fusión experimental | Diferenciar del origen evolutivo de la proteína; evaluar artefacto del constructo sin excluir automáticamente función endógena. |
| Varios procesos causados por la misma actividad | Describir amplitud de roles; no moonlighting por conteo de BP. |
| Misma actividad en dos compartimentos | Localización plural, no segunda función por sí misma. |
| Interacción o unión no específica | No convertirla sin justificación en función fisiológica diferenciada. |
| Dos actividades in vitro y fisiología no establecida | Pluralidad de actividad in vitro puede quedar sustentada; moonlighting fisiológico no resuelto. |
| Ausencia de pruebas de separación funcional | No afirmar autonomía; puede permanecer unresolved, sin exigir que el campo esté resuelto definitivamente. |

### 8.4. Categorías de síntesis separadas

Para multifuncionalidad amplia, campo `broad_mfp_assessment`:

- `supported_within_scope`: al menos dos funciones/roles diferenciados sustentados según la definición amplia explícita registrada; conservar contexto y si se trata de actividades o roles.
- `partially_supported`: solo una parte de la pluralidad o su diferenciación está sustentada.
- `not_established_in_reviewed_material`: no se establece pluralidad en lo revisado; no etiqueta negativa.
- `conflicting`: evidencia pertinente incompatible no resuelta.
- `not_evaluable`: acceso/identidad/material no permiten decidir.
- `not_assessed`: target de evidencia individual para el que no se ha realizado síntesis.

Para compatibilidad con definición MoonProt usada, campo `moonlighting_assessment`:

- `compatible_with_operational_criteria`: todas las condiciones afirmativas relevantes de §8.2 sustentadas y sin explicación excluyente acreditada; no declaración universal de verdad.
- `boundary_explanation_identified`: existe evidencia concreta de explicación excluida por esa definición, como isoformas distintas o misma actividad; registrar cuál, sin declarar monofuncionalidad.
- `unresolved`: pluralidad, fisiología, identidad o diferenciación no suficientes para aplicar la definición.
- `conflicting`: evidencia incompatible dentro del alcance revisado.
- `not_evaluable`: material o acceso impiden valoración.
- `not_assessed`: no se ha realizado esa síntesis.

Ningún valor depende de MBL, IC, Wang, Lin o A. No se infiere una categoría de la otra: multifuncionalidad amplia sustentada no implica moonlighting; incompatibilidad con esta definición no niega funciones múltiples.

## 9. Procedimiento de síntesis y situaciones difíciles

### 9.1. Decisión por anotación versus por atribución

Para GO, comparar con la definición de la release fijada, relación/NOT/extensión y forma de 03. Una anotación a proceso puede tener soporte válido por fenotipo sin probar una segunda función molecular. Para una atribución MFP, revisar todas las funciones necesarias de esa afirmación y documentar el material que falta; no seleccionar solo el par con score extremo.

No crear términos GO nuevos o reemplazos curatoriales en raw. Sugerencias se guardan como propuestas versionadas e incidencias que 03/04 pueden considerar en otra ejecución, no como cambios del input original.

### 9.2. Texto inaccesible y revisión parcial

- Solo metadatos: se puede validar identidad bibliográfica, no métodos ni función fisiológica.
- Solo abstract: registrar exactamente qué afirmaciones/resultados explicita; no asumir controles o detalles omitidos. Propuesta principal: no adjudicar suficiencia plena ni compatibilidad moonlighting como si se hubieran leído métodos; conservar valoración parcial del resumen.
- Texto completo sin suplemento necesario: marcar parte revisada y limitación; no declarar completa la evidencia inaccesible.
- Referencia no localizada: registrar rutas de búsqueda y límite aplicado; `not_evaluable`, no refutación.
- Referencia incorrecta confirmada: issue reference_mismatch; anotación puede carecer de soporte en esa referencia, sin que la función quede negada.

En revisión parcial, el conjunto de claims revisados y pendientes queda enumerado. No elevar una valoración de una función a una decisión de toda la proteína ni rellenar categorías pendientes como negativas para completar tablas.

### 9.3. Contradicciones

Verificar primero identidad, forma, condición, dosis y ensayo. Una aparente contradicción puede corresponder a contextos distintos. Si persiste sobre la misma afirmación, conservar resultados favorables/opuestos y clasificar conflicting, sin votar por número de artículos ni prestigio de la revista. Un resultado no significativo o sin sensibilidad suficiente no es evidencia de ausencia funcional; debe explicitarse su alcance.

Un homólogo con ambas funciones no resuelve la evidencia faltante del target. Una revisión o catálogo puede dirigir la búsqueda, pero la decisión de soporte experimental enlaza al experimento realmente consultado.

## 10. Revisión independiente, calibración y cegamiento

### 10.1. Roles

Coordinación selecciona y prepara según 02/03; dos revisores aplican manual independientemente; adjudicador resuelve o registra desacuerdo persistente. Responsable de datos atiende referencias/identidad; responsable científico valida cambios de criterio. No se designan personas concretas sin evidencia.

Cada revisor declara conflictos de interés relevantes para la evidencia o autoría; se propone reasignación cuando comprometa independencia. No hay nombres ni conflictos reales atribuidos en este borrador.

### 10.2. Calibración de desarrollo

1. Formación con manual y ejemplos sintéticos de §15.
2. Revisión independiente de material de desarrollo seleccionado por 02.
3. Comparación de discrepancias por eje y ejemplos de interpretación.
4. Ajustar definiciones/localizadores y documentar cambios; conservar las decisiones previas como calibración.
5. Repetir si hay ambigüedades sistemáticas que impiden aplicar categorías; no cambiar criterios para que coincidan con scores.
6. Congelar versión para evaluación posterior.

El tamaño y alcance de doble revisión no se inventan aquí: lo decide 02 antes de muestreo con recursos reales. La propuesta preferida es doble revisión de todos los targets de evaluación curatorial; si solo se duplica una submuestra, esta se selecciona independientemente de discrepancias previstas y se reporta su alcance, sin extrapolar acuerdo a toda la revisión.

### 10.3. Cegamiento y apertura de resultados

La primera valoración se cierra antes de mostrar decisiones ajenas y scores. Las consultas de aclaración se canalizan por coordinación y se ofrecen simétricamente, evitando revelar selección por score. El orden se puede aleatorizar con semilla de 02 y no ordenar por valor métrico.

Después del cierre y adjudicación inicial, un análisis explicativo puede mostrar métricas para interpretar discordancias; esa segunda fase se identifica como no ciega y no sustituye la primera medición de acuerdo. Si se descubre nueva evidencia durante discusión, ofrecer el mismo material a ambos y crear nueva ronda; no editar una decisión previa en silencio.

Una ruptura de cegamiento se registra, con cuándo ocurrió y qué información se vio. No invalida automáticamente todo el trabajo, pero exige sensibilidad y límites según 02. El objetivo no es ocultar la identidad necesaria, sino evitar que las métricas definan la supuesta referencia de validación.

## 11. Desacuerdos, adjudicación y actualización

Cada revisor entrega registros fechados y bloqueados para la ronda. Se comparan solo targets y evidencia comparables. Los desacuerdos se clasifican: identidad, alcance del claim, interpretación de experimento, acceso a material, suficiencia, diferenciación funcional o aplicación de definición.

La adjudicación conserva dos entradas independientes y crea una tercera con rol adjudication, IDs de entradas de origen, justificación y evidencia. Puede confirmar una categoría, producir una tercera interpretación o dejar unresolved/conflicting. No exige consenso a costa de ocultar incertidumbre.

Si las lecturas consultaron material distinto, armonizar primero el paquete y realizar nueva ronda independiente si procede. No usar esa ronda armonizada para reportar un acuerdo inicial artificialmente mejor.

Actualizaciones por nueva evidencia, corrección de mapeo o cambio de manual crean nuevas versiones. `supersedes_review_id` documenta sucesión dentro del target/rol apropiado; la adjudicación enlaza todas las revisiones resueltas en `related_review_ids_json`, no sustituye el historial. La decisión aplicable es una vista versionada, no «última fila» sin contexto.

No se actualiza la evaluación reservada para optimizar reglas métricas y luego se vuelve a presentar como independiente. Si cambia el manual después de examinarla, 02 determinará nueva evaluación o carácter exploratorio.

## 12. Acuerdo entre revisores

### 12.1. Qué se compara

Calcular antes de adjudicación, por versión de manual y ronda, sobre targets con doble revisión independiente. Reportar tabla de contingencia y acuerdo observado por eje nominal: identidad, soporte, correspondencia, suficiencia y síntesis cuando sean aplicables. No mezclar categorías de targets atómicos con síntesis ni interpretar not_assessed como desacuerdo sustantivo de multifuncionalidad.

Propuesta para dos revisores y categorías nominales mutuamente excluyentes: kappa de Cohen no ponderado, además de acuerdo bruto y frecuencias marginales. El registro primario de Cohen (1960) identifica el coeficiente para escalas nominales; no se ha leído texto completo a través del editor en esta sesión [P5]. El método aquí se propone explícitamente, no se atribuye una validación al corpus.

No usar kappa ponderado: los ejes de este manual no forman una escala única de peor a mejor. Para etiquetas múltiples de limitaciones, reportar cada etiqueta como variable binaria y sus frecuencias/acuerdo; un promedio no sustituye la matriz. Si después se usa una escala ordinal real, debe definirse su orden/pesos antes del análisis y no asumirlos a posteriori.

### 12.2. Ausencias, incertidumbre y límites

Distinguir falta de revisión de la categoría legítima not_evaluable. Reportar cobertura de doble revisión, número de targets comparables y estados de acceso de ambos. Puede calcularse acuerdo sobre todas las categorías nominales aplicables y, como sensibilidad, sobre material evaluable por ambos; siempre mostrar denominadores y selección.

Con categorías muy desequilibradas, acuerdo bruto alto puede coexistir con kappa bajo; si el denominador de kappa es nulo, informar no estimable, no asignar 1. No adoptar cortes universales «bueno/excelente» ni inventar valores. El acuerdo no demuestra exactitud biológica: ambos pueden compartir error o material sesgado.

La incertidumbre se obtendrá mediante el esquema de 02, remuestreando proteínas o grupos dependientes y manteniendo juntas sus afirmaciones, no cada fila como independiente. Pocos grupos, referencias compartidas o muestra dirigida limitan generalización; en esos casos priorizar tablas y descripción sin intervalo engañoso. Si se desea un método para más revisores o faltantes complejos, requerirá enmienda y revisión estadística antes de usarlo.

## 13. Plantilla propuesta `templates/functional_claims.csv`

Es una propuesta desarrollada de schema, no archivo existente ni tabla real de BioData. Se usa una fila por afirmación de trabajo, entidad y contexto suficientemente atómicos. Los catálogos de claims fuente de 03 permanecen separados; una claim de trabajo puede enlazar varios orígenes sin reescribirlos.

### 13.1. Cabecera propuesta

```csv
schema_version,working_claim_id,entity_id,target_scope,source_claim_ids_json,annotation_row_ids_json,source_record_ids_json,source_assertion_raw,working_claim_text,claim_origin,property_kind,organism_raw,taxonomy_id,product_form_raw,molecular_scope_status,context_text,go_ids_json,ontology_id,go_relation_raw,reference_ids_json,reference_provenance,provenance_id,extraction_status,missing_fields_json,notes
```

### 13.2. Diccionario

`!` obligatorio no vacío; `?` nullable con motivo registrado. Todos los identificadores son strings conforme a 03, no números de fila del CSV. Los arrays JSON se serializan como JSON válido dentro de una celda CSV escapada, no como listas de texto ambiguas. La representación física exacta se implementará en 05 y schemas/07.

| Campo | Tipo/obligación | Valores o validación |
|---|---|---|
| schema_version | string! | Versión real del schema adoptado; no versión ficticia de ejecución. |
| working_claim_id | string! PK | Determinista o asignado en registro versionado; estable para la misma formulación/contexto, con cambio explícito si se descompone. |
| entity_id | string! FK | Entidad de 03; si no hay entidad reconciliada se conserva en inventario de origen y no se fuerza esta fila aceptada. |
| target_scope | enum! | entry / isoform / processed_form / construct / unresolved_scope. |
| source_claim_ids_json | array string! | Puede ser [] si origen es solo GO; FK a 03. |
| annotation_row_ids_json | array string! | Puede ser [] si origen es solo fuente/literatura. |
| source_record_ids_json | array string! | Orígenes disponibles; validación de FK. |
| source_assertion_raw | text? | Texto fuente preservado o referencia/localizador que lo delimita; no texto del revisor presentado como original. |
| working_claim_text | text! | Una afirmación verificable en lenguaje natural, entidad y propiedad/contexto definidos. |
| claim_origin | enum! | source_mfp / go_annotation / literature_extracted / reviewer_proposed_for_review. |
| property_kind | enum! | Valores de §7.2; no inferir a partir de score. |
| organism_raw | text? | Denominación original; no resuelve identidad por sí sola. |
| taxonomy_id | string? | ID normalizado de 03, sin fabricar si falta. |
| product_form_raw | text? | Forma/isoforma/constructo declarado. |
| molecular_scope_status | enum! | resolved / partial / ambiguous / unknown; estado de datos inicial, no juicio final del revisor. |
| context_text | text? | Contexto reivindicado; desconocido se indica en missing_fields. |
| go_ids_json | array string! | IDs de 03 si existen; [] permitido sin proponer GO ficticios. |
| ontology_id | string? | Obligatorio si se comparan definiciones GO; recurso real congelado. |
| go_relation_raw | text? | Relación/NOT originales si disponibles. |
| reference_ids_json | array string! | Referencias ya reconciliadas de 03, [] permitido si falta vínculo. |
| reference_provenance | enum! | go / mfp_source / literature_search / mixed / unknown; mixed conserva enlaces por origen en 03. |
| provenance_id | string! FK | Artefacto y localizador fuente. |
| extraction_status | enum! | ready / needs_identity / needs_reference / needs_atomic_split / incomplete. |
| missing_fields_json | array string! | Campos ausentes y motivos en observabilidad 03; [] si no faltan. |
| notes | text? | Incidencias no cubiertas; no score oculto ni razón métrica de selección. |

Regla: al menos un vínculo de procedencia verificable y, según origen, una fuente/anotación o extracción bibliográfica. No exigir PMID para todas las filas: ausencia referencial es parte del estudio. Formular una hipótesis nueva no la convierte en claim fuente; `reviewer_proposed_for_review` debe distinguirse y excluirse del recuento de atribuciones originales.

## 14. Plantilla propuesta `templates/review_records.csv`

Es una propuesta de registro amplio y normalizado por target/evidencia/ronda/revisor. No se rellena aquí con publicaciones, identidades o decisiones reales. El almacenamiento puede dividirse en tablas hijas en 05 conservando esta semántica de intercambio.

### 14.1. Granularidad y claves

Tres `record_kind`:

- evidence: una decisión por target, referencia y experimento/localizador; permite varias filas para el mismo paper.
- synthesis: una valoración sobre un target y el conjunto de evidencia declarado; reference_id puede ser null, pero reviewed_reference_ids_json enumera material.
- adjudication: una decisión posterior enlazada a las revisiones concretas, sin borrarlas.

`target_type`: functional_claim / go_annotation / mfp_assertion / entity_synthesis. `target_id` enlaza respectivamente a working_claim_id, annotation_row_id, source_claim_id o entity_id. Para síntesis de varias funciones, linked_working_claim_ids_json enumera los claims. Una fila atómica no debe rellenar una evaluación global de toda la proteína.

### 14.2. Cabecera propuesta

```csv
schema_version,review_record_id,record_kind,target_type,target_id,entity_id,linked_working_claim_ids_json,reference_id,reviewed_reference_ids_json,experiment_locator,reviewer_id,review_role,round_id,manual_version,review_package_id,created_at,access_status,review_completion,identity_assessment,tested_entity_raw,tested_organism_raw,tested_form_raw,assay_context,assay_description,intervention_description,controls_description,result_description,source_conclusion,reviewer_interpretation,evidence_locator,short_quote,excerpt_rights_status,support_class,donor_entity_id,physiological_relevance,claim_correspondence,evidence_sufficiency,functional_relation,boundary_flags_json,broad_mfp_assessment,moonlighting_assessment,issue_codes_json,limitations,search_log_ref,independence_note,blinding_status,blinding_breach_note,related_review_ids_json,supersedes_review_id,decision_rationale,record_status
```

### 14.3. Diccionario y campos obligatorios

| Campo(s) | Tipo/obligación | Regla |
|---|---|---|
| schema_version, review_record_id | string! | Versión de schema y PK única; no reusar ID para modificar decisión cerrada. |
| record_kind | enum! | evidence / synthesis / adjudication. |
| target_type, target_id, entity_id | enum/string! | Dominio y FK según §14.1 y 03. |
| linked_working_claim_ids_json | array string! | [] para target sin descomposición aún; síntesis multifuncional necesita claims considerados o justificación de no evaluabilidad. |
| reference_id | string? | Requerido en evidence salvo referencia unresolved; no inventar un artículo para poder importar. |
| reviewed_reference_ids_json | array string! | Referencias examinadas; [] exige estado de acceso/motivo coherentes. |
| experiment_locator | text? | Identificador del ensayo/panel dentro del documento; obligatorio en evidence que afirma resultado localizado. |
| reviewer_id | string! | ID interno, sin exigir nombre público; mapeo protegido. |
| review_role | enum! | reviewer / adjudicator; coordination no emite decisión científica sin rol. |
| round_id, manual_version, review_package_id | string! | Ronda y versiones reales, necesarias para comparar revisiones. |
| created_at | timestamp! | Fecha real de decisión con zona; no rellenada por este borrador. |
| access_status | enum! | Valores de §7.6; synthesis sobre acceso mixto añade mixed como valor explícito y detalle por evidencia. |
| review_completion | enum! | complete_for_declared_scope / partial / blocked. |
| identity_assessment | enum! | matched / partial_match / different_entity / unresolved. |
| tested_entity_raw, tested_organism_raw, tested_form_raw | text? | Objeto realmente estudiado; ausencia se explica, no se copia target automáticamente. |
| assay_context | enum! | Valores §7.3; para síntesis mixed permitido. |
| assay_description, intervention_description, controls_description, result_description | text? | Obligatorios cuando se afirma soporte experimental suficiente, salvo not_applicable o not_reported explícitos justificados por tipo de claim. |
| source_conclusion | text? | Conclusión fuente, cita/paráfrasis marcada; no juicio revisor. |
| reviewer_interpretation | text! | Inferencia del revisor o explicación de por qué no puede inferir. |
| evidence_locator | text? | Figura/panel/página/sección/párrafo/tabla/suplemento/URL y versión; requerido para supports/opposes salvo no evaluable. |
| short_quote | text? | Fragmento mínimo opcional; una paráfrasis con localizador basta si no procede cita literal. |
| excerpt_rights_status | enum! | paraphrase_only / quotation_reviewed / permission_or_license / restricted / no_excerpt. No es autorización legal automática. |
| support_class | enum! | direct / contextual / transferred / author_statement / mixed / not_assessable. |
| donor_entity_id | string? | Requerido si transferred y donor conocido; si no resuelto, tested_entity_raw y limitación obligatorios. |
| physiological_relevance | enum! | Valores §7.3. |
| claim_correspondence | enum! | supports / partially_supports / not_addressed / opposes / mixed / not_assessable. |
| evidence_sufficiency | enum! | sufficient_within_context / partial / insufficient / conflicting / not_evaluable. |
| functional_relation | enum! | distinct_supported / same_activity_or_nested / unresolved / conflicting / not_assessed; solo síntesis de pares justifica distinct_supported. |
| boundary_flags_json | array enum! | fusion_explained / distinct_isoforms / proteolytic_forms / different_homologs / same_activity_multiple_roles / construct_artifact_possible / physiological_scope_unresolved; [] no prueba ausencia de todos los límites. |
| broad_mfp_assessment | enum! | Valores §8.4; evidence individual usa not_assessed. |
| moonlighting_assessment | enum! | Valores §8.4; no inferida desde broad_mfp. |
| issue_codes_json | array string! | Vocabulario de incidencias versionado; [] permitido. |
| limitations | text! | Limitaciones pertinentes o declaración justificada de ninguna identificada en alcance revisado; no implica perfección. |
| search_log_ref | string? | Registro de búsqueda/acceso, obligatorio si se declara no localizado o presupuesto agotado. |
| independence_note | text! | Datos nuevos/reutilizados/revisión/unknown con fundamento; no exigir papers distintos como independencia. |
| blinding_status | enum! | blinded_to_scores / breached / post_unblinding / not_applicable; los dos últimos solo donde corresponda, no como atajo. |
| blinding_breach_note | text? | Obligatorio si breached. |
| related_review_ids_json | array string! | Revisiones fuente de adjudicación; [] en primera revisión. |
| supersedes_review_id | string? | Entrada previa reemplazada como versión aplicable, conservada históricamente. |
| decision_rationale | text! | Razón de categorías y condiciones no satisfechas. |
| record_status | enum! | draft / locked / superseded; solo locked participa en acuerdo de esa ronda. |

### 14.4. Validaciones cruzadas

1. Toda FK enlaza al paquete 03; un target GO no se confunde con un claim MFP.
2. `direct` y `different_entity` son incompatibles como soporte directo del target, salvo que se registre evidencia sobre donor y se clasifique transferred para el target.
3. `metadata_only`/`inaccessible` no permiten `sufficient_within_context` experimental o `compatible_with_operational_criteria` sin otros registros consultados que sustenten una synthesis; el registro individual mantiene su límite.
4. `not_assessed` no significa que una función no exista; es ausencia de evaluación de ese eje.
5. Synthesis con moonlighting compatible exige referencias y claims vinculados y justificación de identidad, diferenciación y fisiología, no dos PMID por regla automática.
6. Adjudication requiere rol adjudicator, entradas locked previas y motivo; no modifica originales.
7. Una frase que compara score y juicio en una revisión inicial cegada es incidencia de cegamiento.
8. CSV usa UTF-8, escape estándar de comillas y saltos, arrays JSON válidos y representación de null acordada por 03/05. Campos textuales «NA» no se convierten automáticamente en null. Exportación para hojas de cálculo debe prevenir fórmulas activas sin alterar raw.

`templates/functional_claims.csv`, `templates/review_records.csv` y sus schemas son artefactos a crear según 05/07. Las cabeceras de este documento son propuestas normativas del borrador, no plantillas instaladas.

## 15. Ejemplos sintéticos resueltos

Los tres ejemplos son escenarios inventados únicamente para calibración. Las etiquetas SYN_* no son proteínas, artículos, organismos, PMID, DOI, GO IDs o decisiones reales. No se han ejecutado ensayos ni revisado publicaciones con esos nombres.

### 15.1. SYN_CASE_DIRECT — Soporte directo y funciones diferenciadas

Material ficticio: SYN_ENTITY_A, forma íntegra de SYN_ORGANISM_A. SYN_DOC_A describe una actividad catalítica con preparación controlada; SYN_DOC_B describe unión específica a una estructura y una consecuencia celular bajo condiciones fisiológicas pertinentes. La identidad molecular de ambas se acredita en el escenario, hay controles de expresión/viabilidad y resultados de separación funcional que preservan una actividad al alterar la otra. No se identifica una explicación por isoformas, fragmentos o fusión.

Extracción: dos working_claim_id, una por función; ensayos y contextos diferentes, cada uno con su localizador sintético (SYN_PANEL_A y SYN_PANEL_B), sin asumir que cada documento sustenta ambas. Source_conclusion se conserva como afirmación ficticia de autores; reviewer_interpretation explica qué datos separan actividades y relevancia fisiológica.

Resultado esperado del ejemplo:

- Registros evidence: identity matched; support direct; claim supports; sufficiency sufficient_within_context para cada claim acotado.
- Síntesis: functional_relation distinct_supported; broad_mfp supported_within_scope; moonlighting compatible_with_operational_criteria dentro del escenario.
- Límite: compatibilidad operacional de lo revisado, no certeza universal ni conclusión basada en GO. Dos documentos no son la razón de suficiencia: lo son los datos especificados.

Desacuerdo razonable: un revisor cree que el segundo ensayo solo prueba localización; debe citar qué lectura apoya esa interpretación y asignar contextual/partial. La adjudicación examina el localizador, no el score.

### 15.2. SYN_CASE_TRANSFER — Función del homólogo, no del target

Material ficticio: la fuente atribuye dos funciones a SYN_ENTITY_TARGET en SYN_ORGANISM_T. SYN_DOC_C estudia SYN_ENTITY_DONOR de SYN_ORGANISM_D y demuestra ambas allí; la atribución al target se basa en homología sin ensayo del target para la segunda función.

Resultado esperado:

- Evidencia sobre donor puede ser directa para donor; para target: identity different_entity, support transferred, donor explícito.
- Un claim formulado «la fuente predice por homología esta función» puede estar correctamente descrito como inferencia; el claim «la función fue demostrada en target» no queda directamente sustentado.
- Para función real del target: correspondencia parcial según claim acotado; sufficiency partial/insufficient para demostración fisiológica del target; relevancia not_established o not_assessable según material.
- Síntesis target: broad_mfp partially_supported si primera función tiene soporte propio; moonlighting unresolved. No se etiqueta como negativo ni como refutado.

Desacuerdo razonable: si el material identifica explícitamente target en un experimento adicional omitido del paquete, es nueva evidencia; nueva versión/round para ambos, no corrección informal de un único registro.

### 15.3. SYN_CASE_UNRESOLVED — Abstract, forma desconocida y referencia ambigua

Material ficticio: SYN_ENTITY_B tiene una atribución amplia. Solo se dispone del resumen de SYN_DOC_D, que menciona dos roles sin aclarar forma/isoforma ni métodos; el supuesto segundo identificador bibliográfico no está reconciliado. Se agotan las rutas de acceso autorizadas y se guarda el log.

Resultado esperado:

- access abstract_only; identidad unresolved o partial_match según el resumen; review_completion partial.
- Extraer la afirmación del resumen como author_statement o soporte clasificable limitado solo si realmente describe un resultado; no inventar ensayo o controles.
- claim correspondence not_assessable/partially_supports según la afirmación concreta; sufficiency not_evaluable para la síntesis fisiológica.
- broad_mfp not_evaluable; moonlighting not_evaluable; referencias/forma pendientes.
- No localizable o inaccesible no se codifica opposes ni «monofuncional». La decisión procesal puede cerrarse con resultado no resuelto y una tarea pendiente explícita.

Dos revisores pueden discrepar entre partial y not_evaluable: se conserva el eje y la razón, sin forzar consenso biológico. Un futuro texto completo puede justificar nueva decisión, manteniendo la anterior.

## 16. Decisiones, riesgos y criterios de finalización

### 16.1. Decisiones registradas

| ID | Decisión | Estado |
|---|---|---|
| D06-01 | Catálogo, revisión y síntesis son capas distintas | PROPOSTA coherente con S1 y alcance 01. |
| D06-02 | Juicios separados de identidad, soporte, contexto, suficiencia y relación funcional | PROPOSTA, no score global. |
| D06-03 | Definición MoonProt explícita como marco operacional, no consenso impuesto | Basada en P2/P3; adopción para comparación pendiente. |
| D06-04 | No acceso/no localizado no son refutación | Regla del encargo y propuesta operativa. |
| D06-05 | Revisión independiente antes de scores y adjudicación | PROPOSTA conservada de 02/05. |
| D06-06 | Plantillas y vocabularios versionados | PROPOSTA para implementación en 05/07, no tablas existentes. |

### 16.2. Pendientes accionables

| ID | Pregunta e impacto | Propuesta provisional justificada | Quién valida | ¿Bloquea? |
|---|---|---|---|---|
| DP-01 | ¿Se ratifican categorías/ejes y aplicación operacional MoonProt? Afecta consistencia. | Usar §§7–8 conservando diferencias de fuente y valores no resueltos; probar en calibración, no imponer nueva definición al campo. | Responsable científico y revisores. | Sí revisión formal; no diseño/cálculo GO. |
| DP-02 | ¿Qué material de identidad y referencias existe realmente? Afecta correspondencia. | Resolver con 03 antes de paquetes; no asumir publicación en API remota. | Responsable datos/BioData. | Por target afectado. |
| DP-03 | ¿Qué búsqueda suplementaria, corte y presupuesto están autorizados? | Referencias vinculadas primero, ampliación versionada y parada declarada en configuración. | Coordinación científica/bibliográfica y 02. | Sí para comparabilidad de búsqueda. |
| DP-04 | ¿Qué muestra y extensión de doble revisión son viables? | Muestreo de 02, sin estratos score en paquete inicial; no inventar n. | Responsable científico/estadístico. | Sí inicio de muestreo curatorial. |
| DP-05 | ¿Quién revisa y adjudica y qué conflictos existen? | Asignar roles, declaración de intereses y preservar entradas. | Coordinación del proyecto. | Sí adjudicación/aceptación. |
| DP-06 | ¿Cómo congelar cegamiento y registrar rupturas? | Paquete neutro, primera ronda locked y apertura después; pruebas de 05/07. | Coordinación y responsable técnico. | Sí evaluación independiente. |
| DP-07 | ¿Se ratifican kappa nominal y análisis por ejes? | Acuerdo bruto/contingencias obligatorios; kappa e incertidumbre solo si diseño defendible. | Responsable estadístico/científico. | No lectura piloto; sí informe de acuerdo formal. |
| DP-08 | ¿Licencias y permisos permiten conservar/compartir textos o citas? | Referencias/localizadores y paráfrasis por defecto, fragmentos mínimos justificados, acceso restringido a copias. | Responsable de información/licencias y coordinación. | Sí redistribución restringida; no resto del manual. |
| DP-09 | ¿Qué endpoint curatorial se usará en evaluación de métricas? | Elegir en 02 antes de evaluación reservada, sin combinar diversidad y problemas documentales. | Responsable científico/estadístico. | No calibración; sí evaluación posterior. |
| DP-10 | ¿Cómo se implementan schemas y actualizaciones? | Validar plantillas y append-only lógico en 05/07; crosswalk de targets, no IDs improvisados. | Responsable técnico/datos. | Sí importación aceptada. |
| DP-11 | ¿Cuándo puede una revisión abstract-only considerarse suficiente para un claim más estrecho? | Conservar resultados explícitos limitados, pero no suficiencia de síntesis moonlighting sin evidencia restante; revisar excepciones antes de evaluación. | Revisor científico. | Por claim; no revisión de todo corpus. |

### 16.3. Protección de textos, notas y decisiones

No reproducir artículos completos ni grandes bloques para justificar una decisión. Registrar cita bibliográfica, enlace permitido y localizador; preferir paráfrasis marcada y fragmento mínimo estrictamente necesario cuando sea legalmente admisible. No se fija un número universal de palabras que garantice legalidad.

Copias completas obtenidas legítimamente se conservan solo bajo licencia/permisos aplicables y acceso autorizado; no se incorporan automáticamente al repositorio público. Acceso abierto no elimina obligación de atribución ni todas las condiciones. Material con copyright, datos personales de revisores y rutas internas pueden requerir separación de paquete privado y reporte público.

Mantener mapping protegido de reviewer_id y claves ciegas; no publicar correos, credenciales o notas internas. Citas, traducciones y paráfrasis se distinguen y preservan versión del documento consultado. Herramientas de IA pueden ayudar a localizar o resumir material autorizado, pero no inventar pasajes ni firmar decisiones como si fueran lectura humana independiente; si se usan, registrar herramienta, alcance y verificación humana, y evitar que expongan material restringido.

### 16.4. Criterio de finalización y aceptación verificable

Dos revisores deben poder aplicar el manual al mismo material, producir decisiones trazables y documentar desacuerdos sin forzar una conclusión. Cierre procedimental no exige resolver biológicamente cada proteína.

- AC06-01: targets y enlaces proteína/claim/anotación/atribución/referencia identificables según 03.
- AC06-02: cada resultado de soporte tiene localizador y contexto o motivo explícito de no evaluabilidad.
- AC06-03: fuente e interpretación del revisor están separadas.
- AC06-04: evidencia de donor/in vitro/contextual no se presenta como demostración fisiológica del target sin fundamento.
- AC06-05: no se deduce multifuncionalidad desde scores, GO count o PMID count.
- AC06-06: ejes y categorías admiten partial/unresolved/not_evaluable y no generan negativos.
- AC06-07: decisiones iniciales independientes y cegadas quedan preservadas, incluidas rupturas.
- AC06-08: desacuerdos/adjudicación tienen IDs, versiones y razones sin sobrescribir originales.
- AC06-09: acuerdo se informa antes de adjudicar con denominadores y limitaciones, sin valores inventados.
- AC06-10: plantillas/schema y restricciones de texto se validan antes de importar/publicar.
- AC06-11: muestras de desarrollo/evaluación y cambios posteriores se distinguen según 02.
- AC06-12: responsables asignados y aprobación registrada; pendiente actualmente.

No se declara que una calibración haya ocurrido o que dos revisores ya alcancen ningún nivel de acuerdo.

## 17. Inventario de fuentes, accesibilidad y límites

### 17.1. Código y documentación de BioData

Repositorio https://github.com/CBBIO/BioData ; revisión https://github.com/CBBIO/BioData/commit/ed073bd4df680a3b45ee69943916e196d28b63b6 . Se empezó por README/árbol; tras fallo de lectura web de portada, el connector permitió lectura remota fijada al commit. No implica acceso a base de datos.

| ID | Ruta y símbolo/sección | Qué se consultó y qué no acredita |
|---|---|---|
| G1 | [README.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/README.md), What Is In This Repo; Documentation | Descripción y árbol, no pruebas operativas. |
| G2 | [CBBIO/BioData.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/BioData.py), `get_protein_by_accession`, `get_protein_species_taxonomy`, `get_protein_sequences`, `get_protein_go_annotations` | Código visible; respuesta truncada en parte posterior, sin auditoría exhaustiva de módulo. |
| G3 | [sql/schema.sql](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/sql/schema.sql), protein/accession/anotaciones y constraints | Esquema remoto, no contenido real. |
| G4 | [CBBIO/types.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/types.py), `GOAnnotation` y `ProteinID` | Tipo de GO sin referencia y alias str, no identidad global. |
| G5 | [tests/test_biodata_integration.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_biodata_integration.py), fixture, tests proteína y GO | Tests leídos, no ejecutados; skips posibles. |
| G6 | [docs/BioData.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/docs/BioData.md), GO Annotations; Proteins and Sequences | Documentación leída; no demuestra conservación de bibliografía. |

No se concluye ausencia global de capacidades no localizadas. El registro manual propuesto no se atribuye a tablas actuales ni a PIS.

### 17.2. Materiales de proyecto y conversación

- S1. `mfp_bibliographic_catalog_vision.md`, Project File localizado y leído, Purpose, Target Product, Scope and Non-Goals, Scientific Interpretation, Identity Model y Provenance Requirements. Es una visión de catálogo, no evidencia de código remoto ni aprobación de este manual.
- S2. `canonical_multifunctional_protein_data_dossier.md`, versión 1.0, 2026-08-29; extractos recuperados, resumen y registro de fuentes. Heterogeneidad fuente; mapeos históricos a tiers no se adoptan como evaluación de evidencia ya realizada.
- S3. `dataset_designer_functional_contract.md`, contenido previamente recuperado accesible en historial; antecedente de datos, no manual bibliográfico ni protocolo negativo aplicable a esta fase.
- S4. `PEC_FUNCTIONAL_CONTRACT.md`, §1, Project File recuperado en esta consulta. Papel documentado del clasificador; no inspección remota de PEC ni entrenamiento aquí.
- S5. `Appendix_Z_Revision_and_Reproducibility_Plan.md`, Z.1 y bloque A, extractos recuperados. Separación entre intención, implementación y evidencia; no resultados actuales.
- C1. `Dossier_extensio_PIS_BioData_PEC_v0.1.md`, adjunto identificado previamente y texto visible en historial; §§4, 6 y 10 separan referencias y revisión. Propuesta inicial, no aprobada.
- C2. `Especificacion_metricas_asociacion_GO_BioData_v1.1.md`: contenido textual visible en historial de solicitud 2026-10-26 13:49 CET; archivo físico independiente no localizado en las fuentes accesibles actuales. Reutilizado en anexo 04a del turno correspondiente, sin aprobación atribuida.
- C3. Propuestas de experimentación/infraestructura, solicitudes 2026-10-26 20:29/20:56 CET; historial accesible. Base de flujo, no revisión ejecutada.
- C4. Esquema con publication_id y API aportados por usuario en solicitud 2026-10-26 20:56 CET; testimonio de instalación no inspeccionada.
- C5. Documentos 01–05 y anexo 04a v0.1, contenidos completos de generación visibles en historial PEC. No se afirma recuperación de sus archivos físicos anteriores en un clon local ni aprobación formal. 07 formal no localizado en las fuentes accesibles.

No se utiliza un número histórico de proteínas como tamaño efectivo de revisión ni se inventa muestra o potencia. Los materiales históricos de clasificación no amplían este alcance.

### 17.3. Fuentes primarias externas

- P1. Balakrishnan, R., Harris, M. A., Huntley, R., Van Auken, K. y Cherry, J. M. (2013). «A guide to best practices for Gene Ontology (GO) manual annotation». Database, bat054. https://doi.org/10.1093/database/bat054 ; página editorial consultada: https://academic.oup.com/database/article/doi/10.1093/database/bat054/338636 . Secciones recuperadas: Overview, objeto de anotación, evidencia y curación; no se afirma verificación de todos los suplementos. Las listas actuales de códigos del experimento se gobiernan en 02, no se sustituyen por la tabla histórica de 2013.
- P2. Chen, C. et al. (2021). «MoonProt 3.0: an update of the moonlighting proteins database». Nucleic Acids Research 49(D1), D368–D372. https://doi.org/10.1093/nar/gkaa1101 . Texto editorial recuperado: selección, información de funciones/organismo/secuencia y discusión. Define criterios de una fuente, no todos los subtipos del corpus.
- P3. MoonProt, página oficial, Introduction: https://www.moonlightingproteins.org/ , consultada el 2026-10-26. Exclusiones de fusión, splicing y fragmentos y distinción respecto de familias. La cifra introductoria histórica no se usa como tamaño actual del recurso.
- P4. Gene Ontology Consortium, GAF 2.2: https://geneontology.org/docs/go-annotation-file-gaf-format-2.2/ , consultado el 2026-10-26. Reference, With/From y Gene Product Form ID; no equivalencia entre IDs y artículos independientes.
- P5. Cohen, J. (1960). «A Coefficient of Agreement for Nominal Scales». Educational and Psychological Measurement 20(1), 37–46. https://doi.org/10.1177/001316446002000104 . Registro editorial consultado; texto completo restringido no leído en esta sesión. Kappa se propone como método y no se atribuyen resultados o umbrales al artículo sin consulta.

No se inventan DOI o PMID. Ninguna referencia de metodología se usa como validación de funciones concretas del corpus. No se ha realizado revisión biológica de artículos asociados a proteínas individuales.

### 17.4. No accesible y límites

NO ACCESSIBLE: base desplegada, exportaciones, credenciales, textos/licencias individuales del corpus y revisiones reales. Implementaciones remotas de PIS y mfp-bibliography no inspeccionadas; el catálogo sí se consultó como documento. El acceso a código GitHub no es acceso a BioData PostgreSQL ni a sus artículos.

Limitaciones: sesgo de literatura y organismo, material incompleto, alias mal resueltos, evidencia transferida, definiciones fuente heterogéneas, revisión parcial, variación de criterio y dependencia documental. La doble revisión mejora trazabilidad y detecta discrepancias, no garantiza verdad. Falta de acceso o incertidumbre pueden cerrar una revisión como no evaluable sin bloquear el resto del corpus.

## 18. Dependencias y comprobación final de coherencia

- Con [01_dossier_experimento.md](01_dossier_experimento.md): conserva auditoría del positivo y límites; sin negativos o clasificación.
- Con [02_protocolo_cientifico_y_analisis.md](02_protocolo_cientifico_y_analisis.md): muestreo, comparaciones, endpoint y análisis de incertidumbre permanecen allí; 06 define cómo se produce la referencia curatorial sin reutilizar evaluación para ajustar reglas.
- Con [03_contrato_datos_y_recursos.md](03_contrato_datos_y_recursos.md): identidad, references/alias y procedencia se consumen sin reimplementarlas ni reinterpretar publication_id; se conserva precisión GAF.
- Con [04_especificacion_metricas.md](04_especificacion_metricas.md) y 04a: scores no determinan categorías ni se muestran en primera ronda; no se cambian fórmulas.
- Con [05_diseno_tecnico.md](05_diseno_tecnico.md): plantillas, bloqueo de rondas, cegamiento y transporte son contratos a implementar; no se exige dashboard.
- Con [07_plan_implementacion_y_validacion.md](07_plan_implementacion_y_validacion.md): validará schemas, referencias, conservación de decisiones y criterios de proceso; no se declara prueba superada.

Los enlaces son destinos documentales, no certificación de aprobación. Los valores efectivos de revisión y recursos vivirán en configuración/manifiesto reales; este manual no los rellena ficticiamente. Resultado de redacción: procedimiento replicable propuesto con ejes, plantillas, casos frontera y pendientes explícitos. Su criterio de finalización es permitir discrepancia documentada entre revisores sin forzar una conclusión biológica.
