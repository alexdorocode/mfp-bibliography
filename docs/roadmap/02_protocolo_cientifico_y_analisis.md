# Protocolo científico y plan de análisis: auditoría del corpus positivo atribuido como multifuncional

| Campo | Valor |
|---|---|
| Archivo | `02_protocolo_cientifico_y_analisis.md` |
| Versión | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha | 2026-10-26 |
| Responsable | Pendiente de asignar |
| Revisores científico, estadístico y técnico | Pendientes de asignar |
| Documento rector de alcance | `01_dossier_experimento.md`, versión 0.1, contenido accesible en conversación |
| Dependencias | 03 datos; 04 y candidato 04a métricas; 05 arquitectura; 06 curación; 07 implementación y aceptación |
| Fuentes | Inventario de §19: documentos de proyecto, conversación, lectura remota de BioData y documentación oficial GO |
| Revisión BioData inspeccionada | `ed073bd4df680a3b45ee69943916e196d28b63b6` |

> [!NOTE]
> **Document Status & Current Role (Historical Experimental Protocol)**:
> This document is a historical experimental protocol and statistical analysis design proposal. It does **not** describe current repository implementation, and formal scientific and implementation approval remains pending.
> - **Recovered Content**: Epistemological rules for reference populations (establishing that BioData is a statistical frequency baseline and never a validated negative control class) have been recovered in [`docs/architecture/scientific-background.md`](../architecture/scientific-background.md) (§7.2, explanatory reference). Proposed Gene Ontology evidence code partitions (`ALL`, `EXP-convencional`, `EXP-ampliada`) have been recovered as proposed analytical designs in [`docs/architecture/go-metrics-specification.md`](../architecture/go-metrics-specification.md) (§2.5, recovered proposed analytical design).
> - **Retained Proposals**: Procedural protocols for random term reduction and publication retraction are preserved in this text as future research proposals.
> - **Traceability**: The original Spanish text is retained intact for scientific provenance and auditability. Section-level mappings are detailed in the [Documentation Recovery Map](../reports/documentation-recovery-map.md#81-reconciled-section-level-recovery-matrix).

Este protocolo desarrolla comparaciones, controles e interpretación antes de un futuro piloto. No autoriza por sí mismo su ejecución. No se ha conectado a la base del usuario ni se han ejecutado experimentos, tests, remuestreos o notebooks. Solo se han leído fuentes y código remoto y se ha generado este documento. No se ha modificado ningún repositorio.

Las decisiones metodológicas nuevas son PROPOSTA hasta su revisión. No se presenta este borrador como preregistro, ni se atribuye a las decisiones una aprobación inexistente. Los valores efectivos vivirán en `configs/pilot.yaml` y el manifiesto; aquí se definen reglas y recomendaciones, sin inventar tamaños de cohortes, potencia, snapshots, checksums, PMID ni resultados.

## Índice

1. Responsabilidad documental, términos y estados
2. Preguntas, hipótesis y nivel de inferencia
3. Poblaciones, conjuntos e independencia
4. Condiciones de evidencia
5. Congelación de recursos y perfiles
6. Matriz experimental: plan mínimo y extensiones
7. Reducción aleatoria de términos
8. Retirada de publicaciones
9. Sensibilidad a representación y corpus de referencia
10. Comparadores simples y factores de confusión
11. Unidades, exclusiones y valores ausentes
12. Revisión bibliográfica y evaluación independiente
13. Estimandos, incertidumbre y análisis estadístico
14. Figuras y tablas previstas
15. Criterios de utilidad y límites de interpretación
16. Piloto, evaluación posterior y desviaciones
17. Decisiones pendientes, riesgos y gobernanza
18. Criterios verificables de aceptación
19. Fuentes y evidencia técnica
20. Dependencias y comprobación de coherencia

## 1. Responsabilidad documental, términos y estados

01 gobierna el objetivo y el alcance: caracterizar y auditar positivos atribuidos, no construir negativos ni entrenar clasificadores. 02 gobierna el diseño de comparaciones y análisis. 03 gobernará identidad, políticas de datos, universos y recursos; 04, fórmulas y agregaciones; 05, arquitectura; 06, reglas de revisión bibliográfica; 07, implementación y aceptación técnica.

Las listas de códigos de §4 son la propuesta experimental cuya representación computable deberá recoger 03 por referencia a este apartado. No deben existir dos listas divergentes. Tampoco se duplican aquí las fórmulas de MBL, IC, Wang, Lin o NPMI ni sus umbrales de calculabilidad: corresponde a 04/04a definirlos y a 03 identificar los recursos.

| Término | Explicación |
|---|---|
| GO | Gene Ontology. |
| MF / BP / CC | Función molecular / proceso biológico / componente celular. MF no significa proteína multifuncional. |
| MFP | Proteína atribuida como multifuncional; la atribución no se convierte en verdad confirmada por inclusión. |
| MBL | Minimum Branch Length, descriptor estructural cuya variante debe validar 04. |
| IC | Contenido informativo; distinto del código de evidencia GO `IC`, Inferred by Curator. |
| NPMI | Información mutua puntual normalizada; base candidata de las asociaciones A. |
| PMID / DOI / GO_REF | Identificador PubMed / identificador de objeto digital / referencia GO. No son equivalentes ni garantías de evidencia independiente. |
| Réplica de perturbación | Sorteo o retirada artificial sobre una proteína; no es otra proteína ni una réplica biológica. |
| Estimando | Cantidad que una comparación pretende describir, con población y denominador explícitos. |
| Perfil | Conteos, política y recursos congelados usados para puntuar términos y parejas. |
| Confirmatorio | Análisis fijado y fechado antes de examinar la evaluación reservada. En esta versión es solo un diseño candidato. |

Estados empleados: VERIFICAT EN CODI (lectura estática, no ejecución); DOCUMENTAT NO VERIFICAT (descripción o antecedente no comprobado operacionalmente); PROPOSTA (diseño nuevo); PENDENT (decisión sin resolver); NO ACCESSIBLE (recurso no consultable en esta sesión).

## 2. Preguntas, hipótesis y nivel de inferencia

Se conservan los identificadores RQ de 01.

| RQ | Pregunta operativa | Análisis previsto y estatus |
|---|---|---|
| RQ-01 | ¿Qué entidades, fuentes, anotaciones y referencias están representadas y qué falta? | Descripción exhaustiva del material congelado; no test de población universal. |
| RQ-02 | ¿Qué diversidad describen los descriptores dentro de cada aspecto? | Atlas descriptivo por proteína/aspecto. |
| RQ-03 | ¿Qué contexto adicional aportan las asociaciones entre aspectos? | Exploratorio, condicionado a implementación y cobertura. |
| RQ-04 | ¿Qué cambia al seleccionar evidencia y cuánto explica perder términos? | Contrastes apareados y reducción aleatoria equivalente; primario descriptivo del piloto. |
| RQ-05 | ¿De qué publicaciones y representación de términos depende el perfil? | Retiradas documentales y sensibilidades, sin causalidad biológica. |
| RQ-06 | ¿Qué concordancias y discrepancias identifica la revisión bibliográfica? | Revisión con trazabilidad; no se equipara revisión de fuente original con corroboración independiente. |
| RQ-07 | ¿Hay aportación respecto de conteos simples y entre métricas? | Exploratorio en piloto; evaluación independiente posterior como candidata confirmatoria. |

### 2.1. Hipótesis de trabajo, no preregistradas

- HE-01: la diferencia ALL–EXP puede reflejar composición específica de términos y no solo reducción de cantidad. Se estudiará el contraste con subconjuntos de tamaño equivalente; un efecto nulo o indeterminado también es admisible.
- HE-02: retirar determinadas publicaciones puede cambiar el perfil funcional o su calculabilidad; la fragilidad documental no demuestra falsedad biológica.
- HE-03: los descriptores pueden aportar explicaciones complementarias después de considerar cobertura, organismo y fuente. No se presupone independencia entre ellos.
- HE-04: una regla de priorización congelada puede mejorar el rendimiento de revisión respecto de reglas simples. No se presupone qué métrica, dirección o combinación lo conseguirá.

No se plantea que «EXP produce siempre más o menos divergencia», que mayor IC signifique mayor rigor, o que menor asociación A demuestre moonlighting.

### 2.2. Análisis confirmatorio candidato

Tras el piloto podrá registrarse una comparación principal de priorización, con un único resultado bibliográfico, regla, dirección y presupuesto de revisión definidos antes de abrir la evaluación reservada (§12). El resultado primario candidato será la diferencia en rendimiento de revisión bajo igual presupuesto. El piloto no valida esa regla y no se reutilizará como evaluación independiente.

No se calculará potencia ni se afirmará suficiencia muestral sin conocer población elegible, coste de curación, frecuencia del resultado y efecto mínimo relevante. Si esos elementos no permiten una evaluación informativa, la fase posterior se declarará descriptiva o inconclusa.

## 3. Poblaciones, conjuntos e independencia

| Conjunto | Definición operativa de uso en 02 | Contrato de pertenencia |
|---|---|---|
| Positivo atribuido | Entidades reconciliadas con al menos una atribución preservada de las fuentes incluidas, sin confirmar por ello todas las funciones. | 03: identidad, fuentes y registro de inclusión. |
| Referencia estadística | Entidades destinadas a estimar IC y coocurrencias. No es una clase negativa. | 03: elegibilidad, taxonomía, política de anotaciones, universos y solapamientos; 04: estimador. |
| Pool reservado | Conjunto identificado para posibles trabajos futuros, sin etiqueta negativa validada. | 03; no participa en comparaciones de clase en esta fase. |
| Muestra bibliográfica de desarrollo | Parte del positivo revisada para probar manual y reglas en el piloto. | Muestreo de §12, identidad en 03. |
| Muestra bibliográfica de evaluación | Material no utilizado para ajustar reglas, umbrales o manual final. | Selección congelada tras desarrollo y antes de consultar sus resultados. |

Los análisis conservarán fuente y tipo original de atribución como metadatos, no nuevas clases biológicas impuestas por GO. Una proteína presente en varias fuentes no se contará varias veces como observación independiente; su pertenencia múltiple se conservará.

03 resolverá solapamientos positivo–referencia y referencia–evaluación. Propuesta provisional: referencia externa congelada para la evaluación principal; si solo existe referencia solapada, declarar análisis interno y añadir sensibilidad con exclusión de la cohorte cuando sea viable. No recalcular una referencia distinta por proteína de forma implícita.

La separación de muestras bibliográficas no garantiza independencia de literatura: se registrarán referencias compartidas, familias y organismos cuando existan. Una evaluación basada en la misma publicación que originó la anotación valida trazabilidad/concordancia, no corroboración experimental externa.

## 4. Condiciones de evidencia

### 4.1. Antecedentes y conflicto explícito

El dossier inicial pide distinguir ALL, experimental convencional y experimental con alto rendimiento [S1, §6.3]. El cuestionario histórico `PEC_Phase0_questionari_abast_cientific.md`, A4, incluye TAS e IC bajo un texto que llama experimental al conjunto. GO clasifica TAS como declaración de autor e IC como juicio curatorial, no como evidencia experimental [S5, A4; P1]. No se modifica silenciosamente ese antecedente: para el nuevo estudio se propone la corrección terminológica siguiente, pendiente de ratificación en DP-01.

No se ha localizado una aprobación formal de las tres listas para este experimento. Las listas de esta sección son PROPOSTA contrastada con documentación GO, no definiciones ya aprobadas.

### 4.2. Listas explícitas propuestas

| Condición | Códigos admitidos | Papel |
|---|---|---|
| ALL | EXP, IDA, IPI, IMP, IGI, IEP, HTP, HDA, HMP, HGI, HEP, IBA, IBD, IKR, IRD, ISS, ISO, ISA, ISM, IGC, RCA, TAS, NAS, IC, ND, IEA | Conjunto amplio, antes de las reglas comunes de validez y positividad de 03. |
| EXP-convencional | EXP, IDA, IPI, IMP, IGI, IEP | Contraste experimental principal propuesto. |
| EXP-ampliada | EXP, IDA, IPI, IMP, IGI, IEP, HTP, HDA, HMP, HGI, HEP | Sensibilidad al añadir alto rendimiento. |

ALL significa todas las categorías admitidas del snapshot bajo una lista controlada, no «todas las funciones conocidas». Los códigos nuevos o desconocidos se inventarían en el informe de incidencias y se resolverían antes de la ejecución correspondiente; no se incorporarían automáticamente ni se reclasificarían como EXP.

ND se contabiliza como categoría observada; no se interpreta como función demostrada. El tratamiento de anotaciones raíz/ND para las métricas pertenece a 03/04. La falta de `NOT` en el esquema no autoriza a asumir que todas las filas sean positivas: 03 debe verificar la ingesta o autorizar una limitación explícita.

La documentación GO reconoce alto rendimiento como evidencia experimental. Su separación es metodológica, no una jerarquía universal de calidad [P1].

### 4.3. Condiciones de la primera entrega

La primera entrega incluye ALL, EXP-convencional y EXP-ampliada. El contraste designado principal del piloto será EXP-convencional menos ALL; EXP-ampliada menos ALL y EXP-ampliada menos EXP-convencional se reportarán como secundarios planificados. Si no existen códigos de alto rendimiento, se informará la igualdad de conjuntos sin atribuirla a un hallazgo de robustez general.

Una reducción formal de la entrega a dos condiciones exige enmienda registrada, no omisión silenciosa. Las listas deberán congelarse en la configuración efectiva antes de calcular resultados.

## 5. Congelación de recursos y perfiles

Antes de puntuar la cohorte se congelarán, según 03–05: snapshot, identidad, pertenencia de referencia, GO, versión de código y dependencia, política de anotaciones de referencia, representación de términos, universos de conteo y parámetros de soporte/cobertura de 04.

Se propone construir los perfiles principales con la referencia bajo ALL y la política de representación principal que acuerde 03. IC y coocurrencias pueden necesitar universos diferentes, pero cada perfil debe tener denominadores consistentes y quedar identificado. No se obliga a que las tres A compartan universo; esa decisión se hereda de 03/04 y se reporta.

### 5.1. Comparación principal: solo cambia el input evaluado

Para ALL–EXP, reducción aleatoria, retirada de publicaciones y reducción de redundancia de la proteína evaluada:

- Se mantienen fijos los perfiles principales y GO.
- Se modifica el conjunto evaluado según la perturbación.
- Se registra cuántos términos o parejas dejan de ser estimables.

No se llama a una reconstrucción de IC o coocurrencias dentro de cada perturbación. Si una proteína evaluada pertenece a la referencia, sus conteos permanecerían en ella durante este análisis y esa dependencia se declararía; la alternativa sin solapamiento se trata como perfil distinto.

### 5.2. Cuándo se recalcula

Se recalcula exclusivamente al estudiar deliberadamente un sistema de referencia alternativo: composición taxonómica, submuestreo de referencia, política de evidencia, propagación o cambios de versión. Cada alternativa conserva inputs evaluados fijos y genera un identificador de perfil diferente.

Para una política alternativa de representación, distinguir:

1. Cambio solo en los términos evaluados con perfil original: efecto sobre la representación de la consulta.
2. Cambio solo de perfil con consulta original: efecto de referencia.
3. Cambio coherente de ambos: sensibilidad del sistema completo, sin atribuir el cambio a una sola causa.

Nunca mezclar estas tres preguntas en la misma columna de diferencias sin identificarlas.

## 6. Matriz experimental: plan mínimo y extensiones

Notación: P0 = cohorte piloto reconciliada; P = positivo completo elegible; BV = evaluación bibliográfica reservada; R0 = referencia principal; F0 = GO y perfiles principales fijos; M = MBL, IC, 1−Wang, 1−Lin por aspecto, según 04; A = tres asociaciones condicionales a implementación aceptada. Estas etiquetas no son identificadores reales de recursos.

| ID / nivel | RQ | Cohorte | Condición | Perturbación | Perfil fijo o cambio declarado | Métricas | Comparador | Salida | Criterio de interpretación |
|---|---|---|---|---|---|---|---|---|---|
| E00 / mínimo | 01 | P0 | Datos observados | Ninguna | Recursos inventariados | Cobertura/descriptores | Registros de entrada | Inventario e incidencias | Describe disponible, no población universal. |
| E01 / mínimo | 02 | P0 | ALL | Ninguna | F0 | M | Conteos simples | Tabla y distribuciones | Atlas, sin umbral de multifuncionalidad. |
| E02 / mínimo | 04 | P0 | Tres condiciones | Filtro de evidencia | F0 | M | ALL | Diferencias y transiciones de estado | Cambio condicionado a casos apareados. |
| E03 / mínimo | 04 | P0 elegible | ALL vs cada EXP | Subconjuntos de tamaño EXP | F0 | M | Reducción aleatoria | Contraste observado frente a distribución condicional | Composición frente a cantidad, no causalidad. |
| E04 / extensión | 03 | P0/P elegible | Tres condiciones | Ninguna/filtro | F0 | A | Conteos y cobertura | Asociaciones, soporte y pérdidas | Habitualidad, no vínculo mecanístico. |
| E05 / extensión | 04 | P0/P elegible | ALL | Reducción gradual de términos | F0 | M y A aceptadas | Sin reducción | Curvas de sensibilidad y calculabilidad | Respuesta a pérdida de términos. |
| E06 / extensión | 05 | P0/P con soporte resoluble | ALL y EXP-convencional | Una publicación por vez | F0 | M y A aceptadas | Condición sin retirada | Dependencia documental | No prueba de falsedad. |
| E07 / extensión | 05 | Misma cohorte | ALL | Redundancia/ancestros | F0; luego alternativas separadas | M/A aceptadas | Representación principal | Valores y cobertura | Representación, referencia o efecto conjunto distinguidos. |
| E08 / extensión | 03,07 | Consulta fija | ALL | Submuestreo/composición de R0 | Un perfil por alternativa | IC, Lin y A | Perfil principal | Sensibilidad y soporte común | Dependencia del contexto estadístico. |
| E09 / mínimo preparatorio | 06 | Muestra de desarrollo | Material bibliográfico | Revisión sin scores | F0 si se presentan luego | Descriptores disponibles | Evidencia revisada | Fichas y registro | Viabilidad del manual, no validación final. |
| E10 / extensión posterior | 06,07 | BV | Política congelada | Priorización a presupuesto igual | Referencia de evaluación congelada | Regla seleccionada tras piloto | Aleatoria, conteos, MBL | Rendimiento y diferencia con incertidumbre | Utilidad solo para el resultado curatorial fijado. |
| E11 / extensión | 01–07 | P | Protocolo final | Solo las aprobadas | Versiones congeladas | Aceptadas | Mismos comparadores | Informe global | No convertir exploración previa en confirmación. |

Plan mínimo: E00–E03 y preparación E09; la entrega computacional inicial comprende tabla reproducible, dos figuras y ficha. Las asociaciones, retiradas y curación exhaustiva no bloquean ese hito si se declaran como no ejecutadas. Completar el mínimo no equivale a completar toda la investigación.

## 7. Reducción aleatoria de términos

### 7.1. Unidad y marco del sorteo

El marco es el conjunto de términos únicos válidos de cada proteína y aspecto bajo ALL, después de la preparación común de 03 y antes de añadir ancestros derivados. El sorteo es uniforme sin reemplazo dentro de ese conjunto. No se sortean filas, evidencias o publicaciones.

Para E03, el tamaño objetivo de cada aspecto será exactamente el número de términos que conserva esa proteína en la condición EXP correspondiente. Esto genera un control de cantidad apareado a la misma proteína. Si el objetivo coincide con ALL, la reducción es determinista; si es cero, se informa pérdida total sin fabricar una métrica. Cuando existen pocos subconjuntos posibles, podrá enumerarse el conjunto completo en vez de repetir sorteos, dejando constancia de ello.

Se propone un banco de subconjuntos por proteína/aspecto/tamaño/repetición compartido entre métricas. Las dos condiciones EXP que tengan igual tamaño reutilizarán el mismo banco. Así no se atribuye a una métrica una diferencia de azar en inputs.

### 7.2. Niveles y réplicas propuestos

Para E05 se proponen fracciones de retención 100%, 75%, 50% y 25%. Son niveles de estrés computacional, no tamaños muestrales ni umbrales biológicos. El tamaño objetivo será el entero inferior de la fracción por el número de términos, con mínimo uno solo cuando el conjunto original no sea vacío; el caso sin reducción queda identificado y los tamaños repetidos no se cuentan como niveles independientes. La pérdida total ya se documenta donde ocurra por filtros/retiradas.

Propuesta para el piloto: 200 réplicas por tamaño no determinista. Evaluar convergencia de los resúmenes y coste sin seleccionar el número por significación. Cualquier ampliación se registra; antes de evaluación posterior se congela el número definitivo. No es una afirmación de precisión garantizada.

La semilla maestra efectiva se fijará en configuración antes de ejecutar. 05 derivará subflujos estables por etapa, proteína, aspecto, tamaño y repetición; se registrarán generador y versión. No se utilizará un hash no estable dependiente de la sesión ni se cambiará la semilla hasta obtener un patrón preferido.

### 7.3. Asociaciones entre aspectos

Cuando se amplíe a A, se igualará simultáneamente el vector de tamaños de los aspectos que intervienen. Se sortearán términos de cada aspecto, no parejas del producto cartesiano. Los términos sorteados de un aspecto se reutilizarán en las A que lo compartan. No se preserva artificialmente cobertura de NPMI; su pérdida es parte de la respuesta.

### 7.4. Comparación y cobertura

Para cada proteína/métrica se comparará el valor EXP observado con la distribución de valores de subconjuntos ALL del mismo tamaño. Se informarán diferencia respecto de la mediana de las réplicas y posición descriptiva dentro de esa distribución, junto con la proporción de réplicas calculables. No se denominará a esa posición p-valor exacto: la asignación de evidencias no es una aleatorización experimental.

Los cuantiles sobre réplicas calculables son condicionales a calculabilidad. Se mostrará también la masa de réplicas no estimables. No se comparará un valor EXP válido con una distribución que ha descartado silenciosamente la mayoría de las réplicas.

La reducción de filas sería otra intervención: puede retirar solo un soporte y dejar intacto el término. Si se estudia, tendrá otro ID y no sustituirá E03.

## 8. Retirada de publicaciones

### 8.1. Unidad documental

E06 retirará una publicación identificada y normalizada por vez dentro de la proteína, no una cadena sin interpretar. PMID y DOI de un mismo artículo se unificarán solo si hay correspondencia validada en 03. GO_REF y referencias de base no son necesariamente publicaciones y se analizarán como retirada de referencia en una extensión separada. Valores nulos no forman una «publicación desconocida» compartida.

Antes de retirar se congelará el grafo de soporte que vincula anotaciones, referencias y procedencia. El significado de una celda con múltiples referencias debe ser resuelto por 03; la decisión de qué significa soporte suficiente se coordinará con 06.

### 8.2. Regla experimental propuesta de preservación de soporte

- Si una afirmación tiene soportes documentados alternativos, se retira solo el soporte del artículo seleccionado; la afirmación permanece si conserva otro soporte admisible.
- Si una afirmación requiere conjuntamente varias referencias y se conoce ese requisito, retirar una rompe ese conjunto de soporte; puede sobrevivir otro conjunto independiente completo.
- Si la semántica de la agrupación es ambigua, no se fuerza OR ni AND. La afirmación se marca como soporte ambiguo y queda fuera del análisis documental principal; podrán reportarse límites bajo ambas interpretaciones como sensibilidad.
- Si el término sigue sustentado por otra anotación admisible, permanece en el conjunto de términos de la proteína.
- Un soporte sin referencia resuelta se conserva como dato observado, pero no se presenta como corroboración independiente. Una sensibilidad documental estricta puede restringir la base a soportes resolubles, con su denominador explícito.

La forma de almacenar estas relaciones pertenece a 03, no a un cambio automático del esquema de BioData.

### 8.3. Recalcular la consulta, no la referencia

Tras retirar: reconstruir anotaciones sustentadas, volver a aplicar la condición de evidencia seleccionada y la representación de términos y recalcular métricas con F0. No se elimina el artículo de todo R0 en E06. Una retirada global de referencia sería otra intervención con perfil nuevo.

Reportar para cada retirada: términos perdidos por aspecto, cambio de métrica, cambio de cobertura y transición de calculabilidad. Resumir por proteína la mediana de cambios y el máximo cambio absoluto observado; este máximo es una estadística de sensibilidad documental y aumenta potencialmente con el número de referencias examinadas. Se comparará dentro de estratos de cantidad de referencias y no se usará como alarma universal.

Si solo existe una referencia y desaparecen los términos, el resultado es dependencia de un soporte registrado y pérdida de calculabilidad, no cero ni falsedad de la función. E06 no requiere sorteo de réplicas cuando se retiran exhaustivamente todas las publicaciones elegibles de una proteína.

## 9. Sensibilidad a representación y corpus de referencia

### 9.1. Redundancia y ancestros

Comparar como análisis separados las representaciones que 03 declare y 04 pueda interpretar: términos explícitos únicos, reducción conservadora de ancestros redundantes y cierre ancestral. No se fijan aquí relaciones ontológicas normativas ni se presupone que el código las use todas.

Primero variar solo la consulta con F0; después, si interesa, ejecutar el diseño de referencia alternativa de §5.2. Registrar cambio de número de términos y de soporte. Un cierre ancestral que crea muchos términos no demuestra más actividades. La semántica de propagación positiva y negativa difiere según GO [P2].

### 9.2. Composición y tamaño del corpus

Diseños propuestos, uno por vez:

- Submuestreo de R0 a fracciones 75%, 50% y 25%, estratificado por el grupo taxonómico definido en 03; 100% es referencia. Propuesta inicial: 50 reconstrucciones por fracción, con semillas registradas, revisable por viabilidad antes de evaluación.
- Perfiles específicos por taxón y perfil global, sobre las mismas consultas elegibles, sin comparar universos no declarados.
- Perfiles construidos con políticas de evidencia distintas, separando cambio de política y cambio de tamaño mediante referencia reducida a tamaño comparable cuando sea viable.
- Sensibilidad sin solapamiento entre referencia y positivo o evaluación, si la referencia principal contiene esos solapamientos.

El submuestreo por proteínas no representa toda la incertidumbre de anotación ni variabilidad de curación. Cuando los perfiles dejan sin soporte términos/parejas, informar por separado el efecto en cobertura y los cambios sobre soporte común. No comparar solo medias de conjuntos diferentes.

Los perfiles alternativos nunca reemplazan silenciosamente al principal por producir resultados más atractivos. La robustez es relativa al contexto examinado; no se exige que IC o NPMI sean invariantes a cambiar el corpus, porque dependen de él.

## 10. Comparadores simples y factores de confusión

### 10.1. Comparadores mínimos y denominadores

Se usarán conceptos derivados de los contratos de 03/04:

| Indicador | Denominador o unidad |
|---|---|
| Número de términos | Términos únicos válidos por proteína/aspecto y condición. |
| Número de referencias | Referencias normalizadas distintas ligadas a soportes admisibles; reportar PMID, artículos reconciliados y otros namespaces por separado. |
| Proporción experimental convencional | Número de términos ALL con al menos un soporte convencional dividido por términos ALL del mismo aspecto. |
| Proporción experimental ampliada | Igual, incluyendo alto rendimiento según §4. |
| Retención de términos | Términos de condición filtrada divididos por términos ALL del mismo aspecto. |
| Cobertura del resultado | Unidad calculable sobre unidad candidata según 04: términos para IC o parejas para métricas de parejas. |
| Concentración documental | Distribución de anotaciones/términos por publicación, con universo resoluble indicado; no llamada replicación. |

Si el denominador es cero, la proporción es no definida. Cero referencias resolubles es un conteo observado, no evidencia de ausencia de literatura. Si se describen proporciones a nivel de filas, se etiquetarán como tales y no se mezclarán con proporciones de términos.

### 10.2. Control descriptivo de confusores

Examinar organismo, fuente de atribución, número de términos, especificidad/profundidad disponible, cantidad de referencias y cobertura. Usar primero estratificación y gráficos; niveles definidos sin seleccionar cortes por su resultado bibliográfico. Las fuentes pueden solaparse: no duplicar la proteína para obtener una aparente muestra mayor.

Las correlaciones crudas y dentro de estratos se presentarán juntas. Como extensión exploratoria, podrán emplearse ajustes asociativos parsimoniosos, con fórmula y variables congeladas antes de la evaluación correspondiente. No son clasificadores de multifuncionalidad ni análisis causales. No ajustar automáticamente por todos los descriptores correlacionados ni llamar «efecto independiente» a un coeficiente ajustado.

## 11. Unidades, exclusiones y valores ausentes

Unidad principal: proteína reconciliada. Aspectos, condiciones, parejas y réplicas son observaciones anidadas o repetidas. La unidad bibliográfica elemental es una afirmación revisada; el análisis principal de rendimiento se resumirá por proteína para no dar más peso a las más anotadas. Las referencias compartidas pueden conectar varias proteínas.

Exclusiones de la cohorte y resolución de duplicados se gobiernan en 03, con contabilidad completa. No exigir embeddings ni campos de entrenamiento para este estudio. No excluir una proteína de todo el inventario por carecer de una métrica concreta. No descartar después de ver scores extremos.

Para cada análisis se publicarán: total de entidades reconciliadas, elegibles para la operación, calculables en cada condición, intersección apareada y motivos de pérdida. Las exclusiones posteriores al congelado requieren registro.

| Situación | Tratamiento analítico |
|---|---|
| Falta de anotaciones o aspecto | Estado explícito; conservar en inventario. |
| Métrica insuficientemente sustentada | Valor ausente con motivo; no imputar cero. |
| Error de software | Separar de insuficiencia biológica; investigar y versionar corrección. |
| Publicación no accesible o decisión curatorial no resuelta | Categoría no evaluable, no negativa. |
| Duplicado de anotación | Conservar trazabilidad bruta; no multiplicar términos ni soporte proteico. |
| Alias bibliográfico no reconciliado | No contar como artículo independiente confirmado. |
| Perfil faltante | Bloquea esa métrica, no la descripción de todas las demás. |

Las diferencias numéricas se calculan solo cuando ambos resultados son válidos. Además se analiza la transición de estado para todos los elegibles. Esto evita concluir estabilidad únicamente sobre supervivientes. La falta de datos puede ser informativa y no se presupone ausencia al azar.

## 12. Revisión bibliográfica y evaluación independiente

### 12.1. Muestreo del piloto

Dos brazos separados:

1. Muestra probabilística de desarrollo: seleccionada sin scores, estratificada por fuente y cobertura conocida antes de calcularlos; considerar organismo si la composición lo permite. Si hay fuentes múltiples, definir estratos mutuamente excluyentes por patrón de pertenencia o una asignación predeclarada, sin duplicación.
2. Muestra dirigida de desarrollo: casos discordantes, cambios grandes o baja calculabilidad, seleccionados con reglas registradas después de los cálculos. Sirve para entender fallos y mejorar el manual, no para estimar prevalencia global.

No se fijan tamaños ficticios. Las cifras 60/30/30 mencionadas en conversación fueron ilustrativas, no aprobadas ni justificadas por potencia. DP-06 fijará tamaño y esfuerzo antes del muestreo. Si el presupuesto es limitado, se reduce alcance de revisión de forma explícita, no se afirma validación suficiente.

### 12.2. Reglas de revisión

06 definirá extracción de funciones, contexto, experimentos, nivel de texto consultado, categorías y adjudicación. Los revisores iniciales no verán scores ni razón de priorización cuando sea compatible con la tarea; verán identidad y material necesarios. Se fijará un procedimiento para desacuerdos y se reportarán acuerdos y categorías, no solo una decisión consensuada final.

Se distinguirán dos resultados de revisión, sin combinarlos: diversidad funcional sustentada y limitación/discrepancia documental. Ninguno convierte automáticamente los demás casos en negativos. La definición estricta de moonlighting solo se aplica si 06 la adopta explícitamente; el estudio no impone una ontología nueva del campo.

### 12.3. Evaluación posterior

Después del desarrollo, congelar manual, regla de priorización, dirección, resultado primario y presupuesto de revisión. Seleccionar una muestra de evaluación probabilística nueva, excluyendo desarrollo, con probabilidades de inclusión conocidas. No usar sus resultados para ajustar reglas y volver a medirlas.

En el conjunto de evaluación se revisará material suficiente para comparar reglas sobre el mismo universo de candidatos. Una opción es revisar completamente la muestra seleccionada y luego evaluar el top-k de cada regla dentro de ella; no atribuir ese rendimiento al corpus completo sin diseño que lo permita. Mantener separados top-k de muestra y top-k global.

Comparadores: priorización aleatoria con presupuesto igual; número de términos; referencias únicas; proporción experimental; MBL. Cada dirección y desempate se congelará antes de evaluar. No construir un score compuesto mediante entrenamiento en esta fase.

El resultado primario candidato será proporción de proteínas con la categoría de revisión preseleccionada entre las k revisadas prioritariamente, con diferencia frente al comparador principal. k es presupuesto operativo que se decidirá antes de evaluación, no valor inventado aquí. Las métricas no calculables se conservarán como «sin prioridad calculable» con una regla de asignación de presupuesto residual congelada y se mostrará también rendimiento restringido al soporte común.

Las decisiones inciertas se reportarán por separado; se harán límites de rendimiento contando los casos no resueltos como ninguno o todos del resultado objetivo, sin llamarlos verdad negativa/positiva. La dependencia bibliográfica compartida se documentará: muestra nueva de proteínas no equivale a literatura independiente nueva.

## 13. Estimandos, incertidumbre y análisis estadístico

### 13.1. Estimandos principales del piloto

- Cobertura: proporción calculable por métrica/aspecto/condición sobre entidades elegibles declaradas.
- Diferencia apareada: para cada proteína, valor de condición filtrada menos ALL; resumen principal mediana de las diferencias, con cuartiles y distribución. No sustituir por diferencia de medianas marginales.
- Transición de calculabilidad: tabla conjunta de estados ALL–condición.
- Contraste de composición: valor EXP menos mediana de réplicas ALL de tamaño equivalente para la misma proteína; resumen por proteínas elegibles.
- Sensibilidad documental: cambios tras retirada y pérdida de calculabilidad por proteína, incluyendo concentración del soporte.
- Redundancia: correlación de Spearman por par de métricas/aspecto sobre intersección de resultados válidos, con tamaño y cobertura de esa intersección.

No se comparan diferencias absolutas de MBL, IC y escalas normalizadas como si sus unidades fueran iguales. Las comparaciones de magnitud se hacen dentro de cada métrica; estandarizaciones, si se introducen, tendrán definición previa en el plan de análisis, no se usarán para un índice biológico.

### 13.2. Tres fuentes de variación diferentes

| Fuente | Qué se puede resumir | Qué no representa |
|---|---|---|
| Réplicas de reducción | Distribución condicional de cambios para una proteína y tamaño. | Intervalo de confianza poblacional ni réplicas biológicas. |
| Muestreo de proteínas | Incertidumbre del estimando para la población de muestreo bajo el diseño. | Incertidumbre de GO, curación o literatura omitida. |
| Reconstrucción de perfiles | Sensibilidad/variación del sistema de referencia bajo perturbaciones definidas. | Toda la incertidumbre de frecuencias biológicas. |

Para el corpus completo descrito, conteos y medias son descripciones de esa población finita observada; no necesitan intervalos para «recontar» lo ya observado. Si se reportan intervalos para extender inferencias, se declarará el objetivo de muestreo y supuestos. No se presume que fuentes y organismos observados representen todas las proteínas multifuncionales.

### 13.3. Remuestreo e incertidumbre propuestos

Para diferencias y correlaciones, propuesta inicial de intervalos descriptivos del 95% mediante 2.000 remuestreos apareados de proteínas o grupos independientes, con semillas fijadas. Son parámetros propuestos, no garantía de cobertura con muestras pequeñas. Los mismos índices se aplicarán a condiciones y métricas comparadas. Cada proteína conserva todas sus filas, aspectos y resúmenes de perturbaciones.

En muestras estratificadas, respetar estratos y pesos de inclusión; no tratar una muestra dirigida como probabilística. Si hay grupos de homología identificados o publicaciones compartidas, evaluar dependencia mediante grupos o componentes conectados. Con pocos grupos, componentes gigantes o estructura cruzada no resoluble, no presentar bootstrap ingenuo como robusto: limitar inferencia a descripción y reportar la limitación.

Para rendimiento top-k, recalcular selección y rendimiento dentro de cada remuestreo del universo evaluado, manteniendo la regla congelada; no remuestrear solo los aciertos del top-k observado. Si el diseño o tamaño no permite un intervalo defendible, reportar estimación, conteos y análisis de límites sin precisión ficticia.

### 13.4. Multiplicidad

El piloto es exploratorio: se priorizan estimaciones, distribuciones y limitaciones y no se seleccionan métricas por p-valores. No se harán centenares de tests por proteína ni se interpretarán posiciones en réplicas como significación confirmatoria.

La evaluación posterior podrá definir una sola comparación primaria de priorización. Si se añaden contrastes inferenciales secundarios, enumerar previamente familia completa por resultado, métrica, aspecto y condición. Propuesta: control de error familiar con Holm al 5% para los secundarios que se presenten como confirmatorios; el alfa es provisional y debe ratificarse. Exploraciones adicionales se etiquetan sin convertirlas en confirmatorias por aplicar una corrección.

No usar «no significativo» como equivalencia, robustez o redundancia demostrada. No aplicar Friedman/Nemenyi a aspectos o semillas como si fueran tareas independientes. No introducir selección de resultados según qué prueba da significación.

## 14. Figuras y tablas previstas

| ID | Producto | Contenido y denominador |
|---|---|---|
| T01 | Flujo y cobertura | Entradas, reconciliadas, elegibles, calculables y perdidas por motivo. |
| T02 | Evidencias y referencias | Conteos de filas y términos separados; referencias por namespace. |
| T03 | Métricas | Una fila conceptual por proteína, condición, aspecto y métrica, con perfiles y estados. |
| T04 | Contrastes | Diferencias apareadas y transiciones de calculabilidad, con intersección visible. |
| T05 | Perturbaciones | Réplicas/retiradas, tamaños, cobertura y resúmenes por proteína. |
| T06 | Revisión | Selección, material consultado, categorías, desacuerdos y adjudicación. |
| F01 | Cobertura por condición | Barritas de estados sobre el total elegible, no solo casos válidos. |
| F02 | Comparación ALL–EXP | Dispersión apareada y distribución de diferencias, panel por métrica/aspecto. |
| F03 | Atlas | Distribuciones y asociación con cantidad de términos/referencias. |
| F04 | Correlaciones | Spearman, tamaño de intersección y cobertura por celda. |
| F05 | Control de cantidad | Cambio observado frente a réplicas condicionales, no intervalos poblacionales. |
| F06 | Dependencia documental | Retirada, soporte perdido y estados; ajuste descriptivo por cantidad de referencias. |
| F07 | Referencia alternativa | Cambio de valor y cobertura, con identificación de cada perfil. |
| F08 | Evaluación curatorial | Rendimiento a presupuesto igual, incertidumbre o límites y casos no resueltos. |

Las dos figuras de la primera entrega serán F01 y F02. Una ficha de proteína mostrará afirmaciones originales, anotaciones, métricas y referencias diferenciadas, sin presentar un score global de confianza. Su plantilla es responsabilidad de 05/06.

Todas las figuras identificarán versión de ejecución, población y condiciones. No unir escalas distintas en un eje común sin transformación explicada ni ocultar resultados no estimables.

## 15. Criterios de utilidad y límites de interpretación

### 15.1. Criterios previos por familia

| Familia | Utilidad candidata | Señal de redundancia | Motivo de no evaluabilidad |
|---|---|---|---|
| MBL | Comparador estructural simple con casos interpretables. | Reproduce otros descriptores sin ventaja explicativa u operativa. | Variante/ruta no validada, valores imposibles o soporte insuficiente. |
| IC | Describe especificidad y ayuda a interpretar granularidad. | Resume casi exclusivamente cobertura ya observada sin nueva pregunta útil. | Perfil no definido o términos no cubiertos. |
| 1−Wang | Aporta lectura estructural que diferencia casos de MBL. | Coincidencia de orden y casos sin explicación adicional. | Dependencia o comportamiento no aceptado por 04/07. |
| 1−Lin | Añade dimensión informativa respecto de topología. | No añade interpretación o priorización después de comparadores. | Perfil IC y casos límite no resueltos. |
| A | Explica coanotaciones interaspecto y prioriza contextos revisables. | Las tres A o conteos explican los mismos casos sin ganancia. | Motor no localizado/aceptado, cobertura o soporte insuficientes. |

### 15.2. Regla de clasificación de utilidad

- Útil para descripción: cálculo técnicamente aceptado, población de aplicación explícita y propiedad interpretable demostrada mediante casos y sensibilidades. No requiere «predecir rigor» si esa no es su pregunta.
- Útil para priorización: mejora del resultado curatorial preseleccionado frente al comparador, bajo evaluación independiente y presupuesto igual, con incertidumbre suficientemente acotada según el criterio congelado antes de evaluarla.
- Potencialmente redundante: asociación elevada acompañada de coincidencia de casos/prioridad y ausencia de aportación incremental observada. Correlación sola no basta para declararla redundante.
- No avaluable: falta de implementación aceptada, denominadores, cobertura o evidencia independiente suficiente.
- Inconclusa: resultados compatibles con varias interpretaciones o precisión insuficiente.

No hay umbral aprobado de correlación, cobertura global, ganancia mínima o cambio tolerable. El piloto puede proponerlos con justificación científica y coste de uso; deben congelarse antes de la evaluación posterior. Los umbrales de soporte por pareja de 04a no se copian ni se convierten en criterios universales de utilidad.

### 15.3. Inferencias prohibidas

No se afirmará que un score demuestra moonlighting, que poca anotación demuestra monofuncionalidad, que un único PMID invalida una función, que EXP es verdad y ALL ruido, que coanotación prueba localización de actividad ni que la muestra dirigida estima prevalencia global. No se evaluará discriminación frente a una clase negativa inexistente en este diseño.

## 16. Piloto, evaluación posterior y desviaciones

### 16.1. Congelación previa al piloto

Registrar antes del primer cálculo: versión documental aceptada para piloto, recursos y esquema de 03, implementación y variantes de 04, condiciones de §4, matriz mínima, marcos de muestreo, parámetros efectivos, semillas y figuras primarias. No es preregistro salvo depósito formal documentado; no se afirma que tal depósito exista.

El piloto evalúa viabilidad, cobertura, costes y coherencia del manual, no confirma HE-01–04. Se permite aprender de él, pero todo cambio posterior debe identificarse como posterior a resultados.

### 16.2. Congelación antes de evaluación posterior

Crear nueva versión con: regla seleccionada, endpoint de revisión, comparador principal, dirección, k, marco de muestreo, tratamiento de no calculables/no resueltos, dependencias, incertidumbre y multiplicidad. Separar material de desarrollo y reservado. Si se ha examinado el material reservado para ajustar decisiones, deja de ser reservado; se necesita otra evaluación o rebajar las conclusiones.

### 16.3. Registro de desviaciones

Cada cambio registrará ID, fecha, versión previa/nueva, motivo, datos/resultados ya vistos, persona/rol solicitante y validador, alcance, efecto sobre comparabilidad y necesidad de nueva ejecución. Un arreglo de software que cambia resultados exige nueva versión y repetir todos los resultados afectados; no corregir solo los casos ilustrados.

Las cifras propuestas en conversación para réplicas o muestra no eran aprobaciones. La presente propuesta conserva la dirección de trabajo, no las convierte retrospectivamente en decisiones preespecificadas.

## 17. Decisiones pendientes, riesgos y gobernanza

### 17.1. Registro de decisiones de esta versión

| ID | Decisión | Estado |
|---|---|---|
| D02-01 | Mantener alcance positivo y referencia no negativa | Fijado por encargo y coherente con 01. |
| D02-02 | Condiciones, contrastes y perfiles fijos según §§4–5 | PROPOSTA; antecedente S1 compatible. |
| D02-03 | Primera entrega con las dos variantes EXP | PROPOSTA explícita, sin omisión automática de ampliada. |
| D02-04 | No confundir réplicas de perturbación y muestra biológica | PROPOSTA metodológica de este protocolo. |
| D02-05 | Separar desarrollo y evaluación bibliográfica | PROPOSTA conservada de C2 y 01. |
| D02-06 | Parámetros efectivos en configuración y manifiesto | Dirección fijada por encargo; esquema en 03/05. |

### 17.2. Decisiones abiertas accionables

| ID | Pregunta e impacto | Propuesta provisional justificada | Quién valida | Bloqueo |
|---|---|---|---|---|
| DP-01 | ¿Se ratifican las listas y la corrección TAS/IC? Afecta comparaciones. | Adoptar §4 y registrar conflicto histórico; categorías respaldadas por GO. | Responsable científico y datos. | Sí para E02 y primer hito completo. |
| DP-02 | ¿Qué esquema y procedencia son efectivos? Afecta soporte y NOT. | 03 verificará exportación frente a G4 y esquema aportado; limitar análisis si faltan campos. | Responsable datos/BioData e ingesta. | Sí para ingesta válida; documental especialmente. |
| DP-03 | ¿Qué R0 y política de solapamiento? Afecta IC/A e independencia. | Referencia congelada diferenciada, preferiblemente externa para evaluación. | Responsables científico y datos; 03. | Sí para IC/Lin/A, no inventario. |
| DP-04 | ¿Son válidas las rutas y agregaciones? Afecta interpretación numérica. | Resolver riesgos G2 antes de aceptar métricas, sin parche silencioso. | Revisor de métricas y mantenedor; 04/07. | Sí para métricas afectadas. |
| DP-05 | ¿Se aceptan niveles, réplicas y esquema de semillas? Afecta coste/Monte Carlo. | §§7 y 9 como arranque, convergencia y coste evaluados sin buscar significación. | Responsable científico, estadístico y técnico. | Sí para perturbaciones; no E01. |
| DP-06 | ¿Qué tamaños/estratos y presupuesto de revisión son viables? Afecta inferencia. | Decidir tras inventario y recursos humanos, antes de muestrear; no invocar potencia no calculada. | Coordinación científica y revisores. | Sí para muestreo bibliográfico. |
| DP-07 | ¿Cómo se representan múltiples referencias y soportes alternativos/conjuntos? | Resolver en 03/06; excluir ambigüedad del principal y mostrar sensibilidad. | Responsable datos y curación. | Sí para E06, no atlas. |
| DP-08 | ¿Qué representación y propagación principales? Afecta métricas y perfiles. | Considerar términos explícitos únicos; ratificar con 03/04 y separar sensibilidades. | Responsables científico/datos/métricas. | Sí para puntuación comparable. |
| DP-09 | ¿Qué resultado curatorial y ganancia mínima definen utilidad? | No decidir por scores; elegir después de desarrollo y antes de BV, manteniendo dos resultados separados. | Responsable científico y estadístico; 06. | No piloto; sí evaluación posterior. |
| DP-10 | ¿Qué grupos permiten inferencia dependiente? | Inventariar homología/referencias sin inventar clusters; limitar inferencia si no hay grupos suficientes. | Responsable estadístico y datos. | No descripción; sí intervalos inferenciales defendibles. |
| DP-11 | ¿Se ratifican IC del 95%, 2.000 remuestreos y Holm al 5%? | Parámetros provisionales de §13; congelar antes de análisis inferencial. | Responsable estadístico/científico. | No inventario; sí inferencia posterior. |
| DP-12 | ¿Quién aprueba protocolo y enmiendas? | Asignar roles, registrar aprobación específica para piloto y después evaluación. | Coordinación del proyecto. | Sí para declarar ejecución autorizada. |

### 17.3. Riesgos de interpretación

Cobertura informativa, sesgo de literatura y taxonomía, selección de casos extremos, apoyo bibliográfico compartido, deriva de versiones y pérdida de metadatos son riesgos activos. Ninguno se resuelve añadiendo más tests estadísticos. El informe los vinculará a análisis afectados y a restricciones de conclusión.

## 18. Criterios verificables de aceptación

Esta tabla acepta el protocolo documental, no afirma que la implementación o un experimento hayan pasado pruebas.

| ID | Verificación exigida antes de etapa afectada |
|---|---|
| AC02-01 | RQ y matriz cubren objetivos de 01 sin negativos ni entrenamiento. |
| AC02-02 | Listas explícitas y contraste principal ratificados; discrepancia TAS/IC registrada. |
| AC02-03 | Recursos y perfiles identificables; perturbaciones principales no reconstruyen F0. |
| AC02-04 | Reducción distingue términos de filas, tamaños, réplicas, semillas y no estimables. |
| AC02-05 | Retirada preserva soporte restante y distingue PMID, otros namespaces y ambigüedad. |
| AC02-06 | Denominadores, intersecciones y transiciones de calculabilidad especificados. |
| AC02-07 | Muestras de desarrollo y evaluación distinguibles y sin reutilización oculta. |
| AC02-08 | Incertidumbre de perturbación, muestreo y perfiles separada. |
| AC02-09 | Criterios de utilidad, multiplicidad y límites definidos antes de evaluación correspondiente. |
| AC02-10 | Parámetros efectivos y desviaciones se registrarán en configuración y manifiesto. |
| AC02-11 | Riesgos de código revisados en 04/07 antes de interpretar métricas. |
| AC02-12 | Responsables y validadores asignados y aceptación documentada; pendiente actualmente. |

## 19. Fuentes y evidencia técnica

### 19.1. Inspección de BioData

Consulta remota de lectura el 2026-10-26. Se comenzó por README y árbol raíz; la revisión recuperada en los enlaces del árbol es `ed073bd4df680a3b45ee69943916e196d28b63b6`. Las lecturas posteriores se fijaron a ese commit. La portada web no se pudo recuperar, pero el connector GitHub sí permitió leer archivos. No se inspeccionó una instalación local.

| ID | Fuente y símbolos/secciones | Estado y conclusión limitada |
|---|---|---|
| G1 | [README.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/README.md), What Is In This Repo; Running Tests | DOCUMENTAT NO VERIFICAT: describe cliente, GO y tests; no demuestra ejecución. |
| G2 | [CBBIO/GO.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/GO.py), `GOOntology.prepare_term_counts`, `information_content`, `semantic_similarity`, `minimal_branch_length`, `group_similarity`, `_as_float`, `_fallback_min_branch_length` | VERIFICAT EN CODI: métodos localizados y delegación a goatools; validez operacional no probada. |
| G3 | [tests/test_go.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_go.py), `test_go_ic_and_similarity`, `test_go_wang_similarity_without_counts`, `test_minimal_branch_length` y tests de errores | VERIFICAT EN CODI: tests sobre ontología pequeña leídos, no ejecutados ni garantía de todos los casos. |
| G4 | [sql/schema.sql](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/sql/schema.sql), `public.protein_go_term_annotation`, `uq_pga_protein_go`, `protein`, `accession` | VERIFICAT EN CODI: esquema remoto sin publication_id y unicidad proteína–GO, diferente del aportado por usuario. |
| G5 | [docs/GO.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/docs/GO.md), Information Content and Semantic Similarity; Group similarity; Full Workflow Example | DOCUMENTAT NO VERIFICAT para los ejemplos. El ejemplo de corpus total no fija una referencia científicamente aceptada para este estudio. |

Implicaciones para el protocolo, sin reimplementar 04:

- `prepare_term_counts` filtra términos no presentes y reasigna `_term_counts`; perfiles reconstruidos pueden cambiar el patrón de referencia. Debe evitarse dentro de perturbaciones principales y contabilizar pérdidas. [G2]
- `_as_float` convierte `None` y ciertas conversiones fallidas a cero. Antes de interpretar un cero o 1−similitud debe verificarse que no represente ausencia oculta. No se afirma que haya ocurrido en la base real. [G2]
- MBL tiene ruta delegada y fallback; este último incorpora ambos términos al conjunto de candidatos por profundidad. Requiere verificación de simetría, no negatividad y ramas distintas antes de aceptarlo como MBL clásica. [G2; G3]
- Wang dispone de rutas de compatibilidad; una ruta puede solicitar conteos. No se asume comportamiento idéntico en cualquier versión de goatools a partir de la tabla documental. [G2; G5]
- `group_similarity` usa mejores correspondencias entre dos conjuntos; no equivale a agregación de divergencia interna por pares. [G2]
- No se ha localizado el motor NPMI en el módulo GO consultado; no se afirma ausencia en todo el repositorio. A es condicional a 04/07.

No existe protocolo aprobado localizado que permita calificar estas observaciones de incumplimientos de una norma experimental vigente. Son riesgos frente a los requisitos propuestos que deberán resolver los contratos correspondientes.

### 19.2. Materiales previos y documentos del proyecto

| ID | Localizador legible | Disponibilidad, uso y limitación |
|---|---|---|
| S1 | `Dossier_extensio_PIS_BioData_PEC_v0.1.md`, 2026-10-19, §§3–8, 10–11 | Adjunto localizado y leído en esta sesión; propuesta inicial, no aprobación ni implementación. |
| S2 | `canonical_multifunctional_protein_data_dossier.md`, versión 1.0, 2026-08-29, resumen, §§1–4 y 7 | Project File localizado; extractos accesibles en exploración. Heterogeneidad y procedencia; no se verificó enforcement. |
| S3 | `mfp_bibliographic_catalog_vision.md`, Purpose; Scope and Non-Goals; Scientific Interpretation | Localizado y leído en el historial accesible de la exploración de 01; no código remoto del catálogo. Afirma catálogo de atribuciones, no clasificador ni selección negativa. |
| S4 | `dataset_designer_functional_contract.md`, §§2–6 | Localizado en inventario y contenido previo accesible en conversación. Contrato histórico de datasets; no gobierna esta fase positiva. |
| S5 | `PEC_Phase0_questionari_abast_cientific.md`, A4, B2–B5, F2–F6, G | Project File recuperado en esta sesión. Decisiones históricas con contexto de clasificación y conflicto explícito TAS/IC. |
| S6 | `chapter_I_research_definition_and_experimental_axes_v1.md`, §§2–5 | Project File recuperado. Alcance histórico más amplio; no se traslada entrenamiento a 02. |
| S7 | `Appendix_Z_Revision_and_Reproducibility_Plan.md`, Z.1 y bloques A/C/E | Project File parcialmente recuperado. Principio de separar diseño, código y resultados; no pruebas ejecutadas. |
| C1 | `01_dossier_experimento.md`, versión 0.1, generado en conversación PEC tras solicitud 2026-10-26 21:16 CET | Texto completo visible en historial, incluidas RQ-01–07, hito y pendientes. Archivo previo no disponible como entrada independiente en el inventario actual; no se afirma nueva lectura física ni aprobación. |
| C2 | Propuestas de experimentación e infraestructura, conversación PEC, solicitudes 2026-10-26 20:29 y 20:56 CET | Accesibles en conversación; direcciones de trabajo, no protocolos aprobados. |
| C3 | `Especificacion_metricas_asociacion_GO_BioData_v1.1.md`, conversación PEC, solicitud 2026-10-26 13:49 CET | Contenido generado visible en historial; archivo independiente no localizado en las fuentes accesibles actuales. Candidato 04a, sin aprobación formal. |
| C4 | Esquema `\d protein_go_term_annotation` aportado por usuario y extracto API, conversación 2026-10-26 20:56 CET | DOCUMENTAT NO VERIFICAT para instalación: incluye publication_id. Diverge de G4; 03 debe resolver versión real, no elegir silenciosamente. |

La existencia del dossier inicial y del contenido previo permite reutilización documental, no reconstruir resultados ni afirmar aprobación. No se adoptan automáticamente cifras históricas de corpus ni mapeos de etiquetas; 03 reconciliará las poblaciones.

Papeles: PIS está documentado en S1 como adquisición/procedencia, pero su repositorio no se inspeccionó; BioData tiene capacidades GO localizadas en G2; mfp-bibliography tiene papel de catálogo documentado en S3 y posible sede experimental propuesta; PEC es el marco del proyecto y su clasificador no se ejecuta aquí. Integraciones no demostradas se mantienen como PROPOSTA.

### 19.3. Documentación científica primaria consultada

- P1. Gene Ontology Consortium, «Guide to GO evidence codes», https://geneontology.org/docs/guide-go-evidence-codes/ , consultada el 2026-10-26. Texto recuperado: categorías, lista experimental convencional, alto rendimiento, TAS e IC.
- P2. Gene Ontology Consortium, «Introduction to GO annotations», https://geneontology.org/docs/go-annotations/ , consultada el 2026-10-26. Texto recuperado: mundo abierto, independencia de anotaciones, referencias válidas, propagación, NOT y contexto GO-CAM.

Los procedimientos estadísticos de 02 se presentan como propuestas explícitas de diseño, no como resultados publicados o validación empírica de estas métricas. No se inventan DOI o PMID. La revisión metodológica de fórmulas de métricas corresponde a 04. No se ha consultado texto completo de artículos individuales del corpus.

### 19.4. Fuentes no accesibles y límites

NO ACCESSIBLE: base desplegada, exportaciones, credenciales, notebooks ejecutados y resultados reales. Repositorios/implementaciones de PIS y mfp-bibliography no inspeccionados remotamente. Código interno de goatools no auditado aquí; debe fijarse y verificarse en 04/07.

Archivos formales 03–07 y anexo 04a con esos nombres: no localizados en las fuentes accesibles. Sus contratos se requieren, no se finge que estén acordados. Los archivos generados en turnos previos no reaparecen como entradas físicas; se utiliza el contenido visible de conversación y se declara su procedencia.

Limitaciones de inferencia: selección no aleatoria de fuentes, anotación incompleta, dependencia de curación y organismos, falta potencial de relaciones/NOT y semántica de soporte, evaluación bibliográfica no necesariamente independiente de GO. No bloquean toda descripción; sí condicionan cada afirmación y análisis correspondiente.

## 20. Dependencias y comprobación de coherencia

| Documento | Qué aporta a 02 | Qué recibe de 02 |
|---|---|---|
| [01_dossier_experimento.md](01_dossier_experimento.md) | Objetivo, alcance, RQ e hito. | Matriz de análisis y límites operativos sin cambiar alcance. |
| [03_contrato_datos_y_recursos.md](03_contrato_datos_y_recursos.md) | Identidad, conjuntos, soporte, recursos, políticas y solapamientos. | Condiciones de evidencia, intervenciones y denominadores que debe poder representar. |
| [04_especificacion_metricas.md](04_especificacion_metricas.md) y candidato [04a_asociaciones_interaspecto.md](04a_asociaciones_interaspecto.md) | Fórmulas, agregación, casos límite y calculabilidad. | Comparaciones y necesidad de conservar cobertura e inputs para interpretación. |
| [05_diseno_tecnico.md](05_diseno_tecnico.md) | Ejecución reproducible de recursos y módulos. | Flujo de perfiles fijos/alternativos, réplicas compartidas y artefactos analíticos. |
| [06_manual_revision_bibliografica.md](06_manual_revision_bibliografica.md) | Resultados curatoriales, reglas y adjudicación. | Muestreo, cegamiento y separación desarrollo/evaluación. |
| [07_plan_implementacion_y_validacion.md](07_plan_implementacion_y_validacion.md) | Pruebas y puertas técnicas. | Matriz mínima, dependencias y criterios documentales; no declaración de pruebas pasadas. |

Los enlaces son destinos documentales previstos, no prueba de existencia de archivos aprobados.

Comprobación final: 02 conserva el alcance de 01; no redefine identidad ni universos de 03; no duplica fórmulas de 04; no impone arquitectura de 05; no sustituye el manual 06; no certifica pruebas de 07. Fija comparaciones propuestas antes del piloto y separa explícitamente lo que podrá aprenderse de él de lo que deberá congelarse para una evaluación posterior. No se declara ninguna hipótesis apoyada, resultado obtenido o experimento ejecutado.
