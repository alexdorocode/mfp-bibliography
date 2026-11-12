# Anexo 04a — Asociaciones GO entre aspectos

| Campo | Valor |
|---|---|
| Archivo | `04a_asociaciones_interaspecto.md` |
| Versión documental de integración | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha | 2026-10-26 |
| Responsable y validadores | Pendientes de asignar |
| Documento padre | `04_especificacion_metricas.md`, versión 0.1 |
| Núcleo algorítmico recuperado | `go-cross-aspect-npmi@1.0.0` |
| Antecedente | Contenido textual de `Especificacion_metricas_asociacion_GO_BioData_v1.1.md`, generado en conversación PEC el 2026-10-26 tras solicitud de 13:49 CET |
| Dependencias | 02 protocolo, 03 datos/perfiles, 04 resultados/estados comunes, 05 implementación, 06 revisión y 07 pruebas |

> [!NOTE]
> **Document Status & Current Role (Historical Cross-Aspect Association Proposal)**:
> This document is a historical cross-aspect association design dossier. It does **not** describe current repository implementation; cross-aspect metric calculations remain unimplemented and unapproved.
> - **Recovered Content**: Mathematical formulations for cross-aspect association using Normalized Pointwise Mutual Information (NPMI), provisional support/coverage thresholds, and safeguards against unwarranted Cartesian functional triplets have been recovered as proposed designs in [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (§3.6, recovered proposed analytical design).
> - **Traceability**: The original Spanish text and exploratory co-occurrence notes are retained intact for statistical traceability. Section-level mappings are detailed in the [Documentation Recovery Map](../reports/documentation-recovery-map.md#81-reconciled-section-level-recovery-matrix).

## 1. Procedencia, alcance de recuperación y autoridad

El texto v1.1 es accesible en el historial de esta conversación, incluida su definición matemática y sus parámetros propuestos. El archivo físico anterior no se ha recuperado como entrada independiente ni está localizado en el inventario actual. Este anexo reutiliza su núcleo de cálculo; no afirma identidad byte a byte ni aprobación previa. No se inventa una fórmula bajo el nombre v1.1.

Se conservan: NPMI sin suavizado, conteos por proteína única, universos de cobertura dual, exclusión de parejas no observadas o degeneradas, media no ponderada, cobertura con todos los candidatos, valor principal condicionado a cobertura y parejas explicativas. Se reorganizan los contenidos de datos, integración y validación por referencia a 03–07, sin copiarlos como normas paralelas. Si se recupera un original diferente, debe compararse y registrar la divergencia antes de aprobar el anexo.

Todos los parámetros continúan como PROPOSTA. El núcleo no es una implementación verificada en BioData. No se han ejecutado tests, experimentos ni consultas a la base.

Este anexo es la única fuente de fórmulas y reglas específicas de A dentro del paquete. 03 es la fuente de pertenencia, identidad, preparación y universos; 02, comparaciones y perturbaciones. 04 remite aquí, sin duplicar las expresiones. La nomenclatura y leyenda técnica están en 04 §1.

## 2. Fichas de las tres métricas

### 2.1. A(MF,BP)(P)

- ID: `go_assoc_mf_bp`; versión de algoritmo: `go-cross-aspect-npmi@1.0.0`.
- Pregunta: ¿cómo se asocian las actividades y los procesos anotados de P respecto del corpus?
- Naturaleza: asociación empírica de coanotación; no dissimilaridad ni probabilidad de multifuncionalidad.
- Unidad: pareja término MF–término BP; agregado proteína.
- Dominio: términos preparados de ambos aspectos y perfil MF–BP identificado.
- Inputs: T_MF(P), T_BP(P), universo, N, marginales y conjuntos del perfil de 03, umbrales explícitos y procedencia.
- Fórmula, ponderación, agregación y cobertura: §§3–6, compartidas con las otras dos.
- Implementación: PROPOSTA. El módulo `CBBIO/GO.py` leído no contiene un motor NPMI localizado; no se afirma ausencia global en todo el repositorio.
- Interpretación: asociación entre anotaciones registradas, no actividad que participa demostrablemente en cada proceso.
- Coste/ejemplo/pruebas: §§7–8, con X=MF e Y=BP.

### 2.2. A(MF,CC)(P)

- ID: `go_assoc_mf_cc`; misma versión algorítmica.
- Pregunta: ¿cómo se asocian las actividades y los componentes anotados de P respecto del corpus?
- Naturaleza: asociación de coanotación.
- Unidad/dominio: pareja MF–CC y proteína con términos preparados y perfil correspondiente.
- Inputs: T_MF(P), T_CC(P) y perfil de 03 con universo coherente.
- Fórmula, agregación, escala, cobertura, estados y ponderaciones: §§3–6.
- Implementación: PROPOSTA, no ejecución verificada.
- Limitación específica: no demuestra en qué componente se ejecuta una actividad ni que cambie de función al relocalizarse.
- Coste/ejemplo/pruebas: §§7–8, con X=MF e Y=CC.

### 2.3. A(BP,CC)(P)

- ID: `go_assoc_bp_cc`; misma versión algorítmica.
- Pregunta: ¿cómo se asocian los procesos y componentes anotados de P respecto del corpus?
- Naturaleza: asociación de coanotación.
- Unidad/dominio: pareja BP–CC y proteína con ambos aspectos preparados y perfil válido.
- Inputs: T_BP(P), T_CC(P), conteos y recursos de 03.
- Fórmula, agregación, escala, cobertura, estados y ponderaciones: §§3–6.
- Implementación: PROPOSTA, no ejecución verificada.
- Limitación específica: no identifica la actividad molecular que explica la asociación; su aportación incremental es una pregunta de 02, no un hecho.
- Coste/ejemplo/pruebas: §§7–8, con X=BP e Y=CC.

Las tres fichas comparten exactamente el mismo estimador. No se suman, promedian entre sí ni se convierten en un triple MF–BP–CC. Universo y escala conceptual común no hacen intercambiables sus distribuciones.

## 3. Frecuencias y NPMI

Sea R_XY el universo identificado por 03 para el par X,Y: entidades únicas con al menos un término válido en ambos aspectos bajo la política del perfil. Sea N=|R_XY|. n_x y n_y cuentan entidades de ese mismo universo con cada término, y n_xy entidades con ambos. No cuentan filas, referencias o accessions alternativos.

\[
p(x)=n_x/N,\quad p(y)=n_y/N,\quad p(x,y)=n_{xy}/N.
\]

Para 0<p(x,y)<1 y marginales positivos:

\[
s_{XY}(x,y)=\frac{\ln\!\left(\frac{p(x,y)}{p(x)p(y)}\right)}{-\ln p(x,y)}.
\]

Es NPMI, no una nueva fórmula de BioData. La base natural mantiene coherencia con el antecedente; cambiar conjuntamente la base en numerador y denominador no cambia NPMI. No añadir epsilon, pseudoconteos ni truncamiento de valores negativos.

La expresión es simétrica si se intercambian x,y y se usan exactamente el mismo universo y conteos. X,Y describen papeles de aspecto, no dirección causal. Para valores definidos, escala [-1,1]: positivo indica coaparición superior a independencia, cero independencia en frecuencias estimadas, negativo inferior a esa referencia.

Bouma define una convención de −1 para coocurrencia cero como extensión límite [P1]. El contrato aplicado aquí la excluye del scoring por prudencia de soporte, como ya proponía v1.1. No es un requisito matemático universal de NPMI ni significa que el límite no exista.

## 4. Soporte y casos no estimables

Una pareja es estimable solo si ambos términos están en el perfil, soportes marginales y conjunto alcanzan mínimos configurados y 0<n_xy<N.

Parámetros iniciales recuperados: `min_term_support=5`, `min_pair_support=5`. Son propuestas heurísticas para prototipo, no significación ni garantía de precisión. Exigen sensibilidad por 02 y aprobación antes de evaluación. Los marginales se conservan aunque sus valores queden bajo umbral; aplicar soporte no redefine N.

| Prioridad | Condición | Estado de pareja y valor |
|---|---|---|
| 1 | N inválido o conteos imposibles | `INVALID_COUNTS`, null; error de perfil. |
| 2 | Término no representado en perfil | `MISSING_TERM`, null. |
| 3 | Marginales presentes y n_xy=0 | `UNOBSERVED_PAIR`, null. |
| 4 | n_xy=N | `DEGENERATE_JOINT`, null. |
| 5 | Conteos positivos bajo umbral | `LOW_SUPPORT`, null. |
| 6 | Resto válido | `OK`, NPMI. |

Cada pareja recibe un estado primario para contabilidad. Las comprobaciones de 03 exigen intersección no superior a marginales y unión no superior a N. Una pareja no materializada o consulta fallida no se clasifica como cero: es falta de referencia/error hasta acreditar completitud.

GO ID obsoleto o alias se resuelve antes por 03. Una comparación con término no resuelto no se trata como asociación negativa. Si se pasa un par del mismo aspecto por error: `INVALID_ASPECT_PAIR`. La identidad de dos GO ID canónicos no pertenece al dominio de estas comparaciones entre aspectos; no hay diagonal que excluir dentro del producto válido.

## 5. Agregación por proteína

\[
C_{XY}(P)=T_X(P)\times T_Y(P),
\quad V_{XY}(P)=\{(x,y)\in C_{XY}(P):status(x,y)=OK\}.
\]

Si V no está vacío:

\[
A_{available,XY}(P)=\frac{1}{|V_{XY}(P)|}\sum_{(x,y)\in V_{XY}(P)}s_{XY}(x,y).
\]

Cada pareja pesa uno, no su soporte, evidencia o número de artículos. Términos duplicados se cuentan una vez por aspecto; más artículos no multiplican contribuciones. Se consideran todas las combinaciones entre los aspectos, no solo las asociadas positivamente ni un mejor match por término.

Cobertura:

\[
coverage_{XY}(P)=|V_{XY}(P)|/|C_{XY}(P)|.
\]

Un término sin cobertura permanece en T y en el denominador de candidatos. Excluirlo antes ocultaría la falta de soporte. La media disponible es condicional al subconjunto estimable: no imputa las parejas no observadas y puede estar sesgada hacia combinaciones suficientemente frecuentes.

Parámetro recuperado: `min_coverage=0.80`, propuesta no validada. Es específico de A y no se sustituye por el criterio de cobertura completa de las familias internas de 04.

| Caso | Resultado principal | Estado |
|---|---|---|
| Falta algún aspecto, C vacío | value=null; available=null; coverage=null | `INSUFFICIENT_ASPECT_COVERAGE` |
| C no vacío, V vacío | value=null; available=null; coverage=0 | `NO_ESTIMABLE_PAIRS` |
| V no vacío y cobertura menor que umbral | value=null; available=media disponible | `LOW_PAIR_COVERAGE` |
| V no vacío y cobertura igual o superior a umbral | value=media disponible | `OK` |

Una anotación válida por cada aspecto genera una pareja: no hacen falta dos términos por aspecto. Cero términos no equivale a asociación cero. Dos términos en un aspecto y uno en otro generan dos parejas candidatas. No se calculan las tres A como si fueran observaciones independientes.

## 6. Outputs y explicación

El esquema común es 04 §11, con adaptación sin cambio matemático:

- `association_available` del antecedente → `available_mean` en salida larga.
- `value`, `status`, motivo específico y `coverage` se preservan.
- `n_candidate_pairs`/`n_estimable_pairs` → contadores de unidades, además de sus alias si se exportan por compatibilidad.
- `unit_kind=pair`; aspect_x/aspect_y obligatorios; profile_id obligatorio para un resultado aceptado.
- Contadores de estados reconciliables, términos por aspecto, recursos/configuración/backend y procedencia.

Parámetro recuperado `lowest_pairs_k=3`: devolver hasta k parejas estimables con menor NPMI y conteos, ordenadas por NPMI ascendente y GO IDs canónicos en empates. No llamarlas incompatibilidades ni alertas automáticas de moonlighting. Exportar detalle completo es opcional; debe poder regenerarse desde recursos congelados.

No se fija un umbral de NPMI para clasificar proteínas ni se generan p-valores, intervalos de confianza o probabilidades de rigor. El análisis estadístico y cualquier criterio de utilidad pertenecen a 02. OK solo significa cálculo técnicamente aceptable.

## 7. Coste y límites

El conteo exhaustivo por universo requiere trabajo proporcional a la suma sobre entidades de |T_X|·|T_Y| y almacenamiento disperso cuando sea conveniente. Puntuar una proteína requiere |T_X(P)|·|T_Y(P)| consultas lógicas a conteos y posterior agregación. El perfil puede prepararse sin matriz densa; no desaparece el coste de construir la referencia. No existen benchmarks ejecutados en esta redacción.

Las anotaciones estándar son afirmaciones independientes. La coanotación no prueba cuál función ocurre en qué compartimento o proceso. Referencia taxonómica, selección de evidencia y cobertura influyen en frecuencias. Una combinación rara puede ser biológicamente válida; una combinación habitual puede pertenecer a una proteína multifuncional.

Las tres asociaciones pueden correlacionarse; no se asume aportación independiente. Excluir parejas poco soportadas reduce la interpretación de casos raros y debe reportarse. La normalización no convierte escasez en certeza ni corrige automáticamente todos los sesgos del corpus.

## 8. Ejemplos y pruebas numéricas esperadas

Datos abstractos, no correspondientes a proteínas ni perfiles reales, no ejecutados. Asignar X,Y a cualquiera de los tres pares reproduce los mismos resultados si se usan estos mismos conteos.

| N | n_x | n_y | n_xy | Resultado esperado con soporte suficiente |
|---:|---:|---:|---:|---|
| 100 | 20 | 25 | 5 | NPMI=0 por independencia. |
| 100 | 20 | 20 | 10 | ln(2.5)/ln(10), aproximadamente 0.39794. |
| 100 | 50 | 50 | 10 | ln(0.4)/ln(10), aproximadamente −0.39794. |
| 100 | 10 | 10 | 10 | 1 por coaparición exclusiva no universal. |
| 100 | 20 | 20 | 0 | null, UNOBSERVED_PAIR, no −1. |
| 100 | 100 | 100 | 100 | null, DEGENERATE_JOINT. |

Una proteína abstracta con dos parejas válidas de NPMI 0.39794 y −0.39794 tiene media 0 y cobertura 1; no significa que cada pareja sea independiente. Si solo una es estimable y hay dos candidatas, cobertura=1/2 y con el umbral propuesto value=null aunque available_mean exista.

Pruebas adicionales: invertir aspectos con idéntico universo conserva valor; duplicar anotaciones/referencias no modifica conteos; término ausente permanece en denominador; igualdad exacta con umbral publica valor; ausencia de aspecto conserva fila con null; conteos inconsistentes bloquean; mismo cálculo individual/batch; caché no mezcla perfiles. Son expectativas que 07 deberá implementar, no pruebas superadas.

## 9. Decisiones pendientes y aceptación

| ID | Pregunta e impacto | Propuesta justificada | Validador | Bloqueo |
|---|---|---|---|---|
| A-DP-01 | ¿Se ratifica adaptación de v1.1? | Mantener núcleo y documentar reubicación, sin aprobación retrospectiva. | Responsable científico/métricas. | Sí para norma A aceptada, no primer hito interno. |
| A-DP-02 | ¿Universos y solapamiento efectivos cumplen 03? | Usar perfil identificado, referencia no negativa y universos duales coherentes. | Responsable datos/científico. | Sí A. |
| A-DP-03 | ¿Soporte y cobertura provisionales son adecuados? | Sensibilidad de 02, congelación antes de evaluación; sin afinarlos en muestra reservada. | Responsable científico/estadístico. | Sí para interpretación principal A. |
| A-DP-04 | ¿Existe implementación equivalente y probada? | Localizar o desarrollar capacidad reutilizable y pruebas de §8. | Mantenedor BioData y 07. | Sí ejecución A aceptada. |

Aceptación: conteos reconstruibles y consistentes; casos límite sin imputación arbitraria; cobertura íntegra; versiones y procedencia; pruebas numéricas y batch satisfechas en futura implementación; parámetros ratificados. No se declara ninguno de estos criterios verificado mediante ejecución aquí.

## 10. Fuentes y coherencia documental

- Antecedente: contenido v1.1 en conversación PEC de 2026-10-26, solicitud 13:49 CET, con título «Especificación de métricas de asociación entre aspectos de Gene Ontology para BioData». Texto accesible; archivo independiente anterior no localizado en las fuentes accesibles actuales. La leyenda previa se reutiliza por referencia a 04.
- P1. Bouma, G. (2009), «Normalized (Pointwise) Mutual Information in Collocation Extraction», §3.1, ecuación 7: https://svn.spraakdata.gu.se/repos/gerlof/pub/www/Docs/npmi-pfd.pdf . Texto consultado; convención original de cero distinguida del contrato aplicado.
- Código principal inspeccionado: CBBIO/BioData, `CBBIO/GO.py`, commit `ed073bd4df680a3b45ee69943916e196d28b63b6`: https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/GO.py . No se localizó en ese módulo un motor NPMI. No equivale a auditoría exhaustiva del repositorio.
- Los inventarios de proyecto, documentación GO y accesibilidad de datos se encuentran en 03 y 04; no se afirman recursos operacionales ni resultados biológicos.

Coherencia: 01 mantiene alcance positivo; 02 gobierna comparaciones; 03 gobierna identidad, universos y recursos; 04 aporta catálogo y salida común; 05 implementará persistencia/API; 06 revisará evidencia y 07 aceptará implementación. No se duplican aquí reglas de selección de cohortes, filtros experimentales o curación, ni se declara que un score valide multifuncionalidad.
