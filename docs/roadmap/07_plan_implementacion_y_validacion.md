# Plan de implementación y validación de la experimentación sobre el corpus positivo

| Campo | Valor |
|---|---|
| Archivo | `07_plan_implementacion_y_validacion.md` |
| Versión | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha | 2026-10-26 |
| Responsable | Pendiente de asignar |
| Responsables y revisores de tareas | Roles propuestos; nombres y disponibilidad pendientes de asignar |
| Proyecto | PEC; auditoría y caracterización del corpus positivo atribuido como multifuncional |
| Fuentes | Inventario de §17; código remoto, documentos de proyecto e historial diferenciados |
| Repositorio inspeccionado | `CBBIO/BioData`, commit `ed073bd4df680a3b45ee69943916e196d28b63b6` |
| Dependencias normativas | 01 alcance; 02 protocolo/análisis; 03 datos/recursos; 04 y 04a cálculos; 05 arquitectura; 06 revisión bibliográfica |

Este documento convierte los contratos anteriores en tareas, pruebas y puertas para una ejecución futura. No es un informe de trabajo realizado ni una solicitud de modificar GitHub. No se han ejecutado experimentos, tests, consultas a la base del usuario, exportaciones o notebooks. No se han creado ni modificado repositorios, commits, issues o pull requests. La única actividad computacional de redacción es generar este archivo.

Los seis documentos previos y el anexo permanecen como borradores en el historial accesible; su existencia no equivale a aprobación. Las reglas operativas de este plan son PROPOSTA hasta revisión. No se inventan tamaños de muestra, potencia, snapshots, checksums, PMID, resultados ni duración de tareas.

## Índice

1. Alcance, autoridad y leyenda
2. Punto de partida y riesgos verificados estáticamente
3. Entregas y aceptación por niveles
4. Fases, dependencias y camino crítico
5. Backlog verificable
6. Artefactos operativos a crear
7. Fixtures y estrategia de pruebas
8. Catálogo de pruebas unitarias y de datos
9. Integración, reproducción y operación
10. Matriz requisito → tarea → prueba → evidencia
11. Procedimiento del piloto
12. Gráficas y ficha de proteína
13. Coste y rendimiento por medir
14. Puertas GO / REFORMULAR / AJORNAR
15. Congelación, desviaciones y siguiente fase
16. Decisiones pendientes y checklists
17. Inventario de fuentes y límites
18. Comprobación de coherencia documental

## 1. Alcance, autoridad y leyenda

Se implementará un flujo pequeño de auditoría de positivos atribuidos, no una plataforma general. Quedan fuera del piloto la construcción o validación de negativos, entrenamiento de clasificadores, generación de embeddings, dashboard y orquestación distribuida. La referencia estadística no es una clase negativa y el pool reservado no recibe etiquetas mediante scores.

01 gobierna qué se investiga; 02 cómo se compara y analiza; 03 cómo se reconstruyen datos y recursos; 04/04a qué se calcula; 05 cómo se organiza el software; 06 cómo se revisa literatura. 07 define tareas y evidencia requerida para aceptar implementación/viabilidad; no cambia fórmulas o filtros para que pasen tests.

Estados: VERIFICAT EN CODI = lectura estática, no ejecución; DOCUMENTAT NO VERIFICAT = descripción o testimonio sin comprobación operacional; PROPOSTA = diseño futuro; PENDENT = decisión; NO ACCESSIBLE = no consultable, no inexistente.

Leyenda: GO en contexto biológico es Gene Ontology; «GO» en las puertas significa continuar y no debe confundirse con la ontología. MBL/IC/Wang/Lin/A se definen en 04/04a; MF/BP/CC son aspectos GO; ALL y EXP son condiciones de 02; CLI = interfaz de órdenes; PK/FK = clave primaria/foránea; fixture = conjunto de prueba versionado; oracle = resultado esperado independiente de la implementación probada; checkpoint = salida validada para retomar; NA/null = no estimable/no disponible, nunca cero automático.

No se fijan nombres de personas o fechas comprometidas. Cada tarea será asignada y aprobada antes de ejecutarse. Se puede avanzar con documentación y fixtures sin credenciales; no se exige instalar nada para recibir este plan.

## 2. Punto de partida y riesgos verificados estáticamente

Lectura remota en commit de cabecera, después de README/árbol:

| Evidencia | Estado | Consecuencia para el backlog |
|---|---|---|
| `CBBIO/GO.py`: carga OBO, IC, Lin, Wang, MBL y BMA | VERIFICAT EN CODI [G2] | Reutilizar detrás de adaptadores de 05 y pruebas de conformidad; no declarar métricas validadas. |
| `minimal_branch_length`: ruta delegada y fallback local | VERIFICAT EN CODI [G2] | T09: comprobar variante y bloquear fallback no conforme; no reemplazar por shortest path silenciosamente. |
| `_as_float` convierte algunas ausencias a 0.0 | VERIFICAT EN CODI [G2] | T10/T11: pruebas de guardas antes de publicar IC/Lin/Wang. |
| `prepare_term_counts` filtra IDs y sustituye `_term_counts` | VERIFICAT EN CODI [G2] | T07/T08: contabilidad de pérdidas y perfil fijo sin mutación. |
| `group_similarity` usa BMA entre conjuntos | VERIFICAT EN CODI [G2] | T12: agregación interna nueva conforme a 04, no comparar conjunto consigo mismo. |
| Tests GO incluyen árbol pequeño y aserciones de no negatividad | VERIFICAT EN CODI [G3] | Ampliar con oracles y DAG multiparental; leer tests no equivale a ejecutarlos. |
| Integración puede hacer skip si falta entorno/base/datos | VERIFICAT EN CODI [G4] | No aceptar una puerta requerida basándose en «suite verde» con pruebas omitidas. |
| Cliente visible no fija por sí mismo snapshot repeatable-read | VERIFICAT EN CODI [G5] | T06 y pruebas separadas en base desechable/autorizada. |
| Esquema remoto sin publication_id, distinto del aportado por usuario | Esquema remoto VERIFICAT EN CODI; instalación DOCUMENTAT NO VERIFICAT [G6/C4] | T05/T06 reconocen variantes; T20 documental bloqueada si no existe soporte suficiente. |

Estos riesgos se han localizado, no se han observado fallos en una ejecución real. No se presupone que una ruta concreta de goatools esté instalada. Las dependencias efectivas se fijarán y comprobarán en T01/T08–T11.

Papeles de sistemas: BioData aporta capacidades leídas; PIS tiene papel de adquisición/procedencia documentado en dossier inicial, implementación no inspeccionada; mfp-bibliography es catálogo documentado y sede experimental candidata; PEC es marco del proyecto y clasificador fuera de fase. La integración operativa entre ellos permanece propuesta/no verificada. No se importa el plan histórico de Dataset Designer como selección negativa actual.

## 3. Entregas y aceptación por niveles

### 3.1. Hito vertical H1

Cohorte pequeña identificada, exportación BioData congelada y GO fijada; MBL clásica identificada en 04, IC, 1−Wang y 1−Lin por aspecto bajo ALL, EXP-convencional y EXP-ampliada de 02; estados de cobertura, tabla larga reproducible, dos gráficas F01/F02 y ficha de proteína.

Las variantes EXP se ejecutan según listas ratificadas de 02. Si ampliada y convencional seleccionan lo mismo por ausencia de códigos de alto rendimiento, se registra igualdad de inputs, no se omite una condición ni se declara robustez general. Un cambio de alcance requiere enmienda antes de usarlo como aceptación.

«Implementada» significa que la ruta cumple la definición y sabe devolver NA cuando corresponde. No significa que toda proteína deba tener todos los valores. Tampoco basta que una ruta produzca siempre NA: debe demostrar los casos calculables de fixtures y describir cobertura de aplicación real.

### 3.2. Entregas parciales inequívocas

| Entrega | Contenido permitido | Qué falta para H1 |
|---|---|---|
| H0-inventario | Recursos, mapeo, cobertura y claims sin cálculo aceptado | Cuatro familias, resultados y reporte validado. |
| H1-parcial-datos | Snapshot y preparados equivalentes con métricas bloqueadas enumeradas | Resolver bloqueos técnicos/contractuales. |
| H1-parcial-metricas | Familias aceptadas, tabla de estados y diagnóstico de las bloqueadas | No sustituye aceptación de las cuatro familias. |
| H1-completo-tecnico | Flujo y cuatro familias conformes, tabla, figuras, ficha y reproducción | Aún debe evaluarse viabilidad científica; no valida biología. |
| H2-extensiones | Sensibilidades, asociaciones y calibración/revisión según puertas propias | No se obtiene automáticamente por completar H1. |

Una entrega parcial tendrá `incomplete` y lista de required_metrics_blocked en el informe/manifest. No se esconde quitando columnas, relajando cobertura o marcando la familia como opcional después del fallo.

### 3.3. Tres aceptaciones distintas

- Técnica: cálculos, datos, estados y operación cumplen contratos y pruebas.
- Viabilidad científica: los datos y cobertura permiten responder preguntas acotadas de 02, con sesgos explícitos y coste viable.
- Evidencia biológica: resultado de revisión de claims concretos bajo 06 o futura experimentación; no se obtiene por pasar tests ni por scores elevados.

La aprobación técnica habilita análisis, no una afirmación de moonlighting. Una métrica técnicamente correcta puede ser poco informativa; un corpus con cobertura escasa puede ser un resultado de auditoría útil pero no permitir las comparaciones previstas.

## 4. Fases, dependencias y camino crítico

| Fase | Finalidad | Tareas | Puerta |
|---|---|---|---|
| F0 | Inventario y decisiones mínimas | T00–T02 | P0 contratos mínimos ratificados para implementación. |
| F1 | Schemas, fixtures y evidencia esperada | T03–T05 | P1 pruebas offline disponibles y oracles revisados. |
| F2 | Extracción o recepción y validación | T06–T07 | P2 snapshot y preparados aceptables. |
| F3 | Perfiles y métricas | T08–T12 | P3 cuatro familias conformes o entrega parcial explícita. |
| F4 | Persistencia operativa e informes | T13–T16 | P4 flujo offline reproducible sobre fixtures. |
| F5 | Piloto real de viabilidad | T17–T18 | P5 decisión técnica/científica documentada. |
| F6 | Extensiones de sensibilidad, A y revisión | T19–T22 | Puertas separadas por extensión. |
| F7 | Congelación y evaluación independiente posterior | T23 | P6 protocolo actualizado y siguiente evaluación no contaminada. |

Camino crítico de H1, sin duración comprometida:

```text
T00 → T01/T02 → T03/T04/T05
                    ├→ T06 → T07 → T08 → T10/T11 ┐
                    └→ T09 y pruebas de Wang ───┤
                                               ▼
                                         T12 → T15/T16
T13/T14 y sus pruebas ──────────────────────────┘
                                               ▼
                                            T17 → T18
```

Las ramas de primitivas pueden trabajarse con fixtures antes de tener exportación real. T13/T14 se desarrollan en paralelo, pero son obligatorias antes de aceptar reproducción y recuperación. Una referencia IC aceptable es crítica para IC/Lin, no para inventario o MBL/Wang. T19–T22 no bloquean H1. La calibración manual de desarrollo puede prepararse en paralelo, pero su ejecución/reporte es otra puerta.

## 5. Backlog verificable

Todos los nombres personales están pendientes. Roles abreviados: CO coordinación; RC responsable científico; RD responsable de datos; DEV desarrollo; MT mantenedor BioData; EST revisión estadística; BIB revisión bibliográfica; QA revisor de validación. Una persona podrá asumir varios roles si se declara, procurando revisión independiente del resultado crítico.

Cada tarea se cierra con output y evidencia, no con «código escrito». Las pruebas indicadas se detallan en §§8–9; son propuestas, no ejecutadas. Ninguna tarea solicita crear issues/commits desde esta sesión.

### 5.1. Preparación, datos y métricas

| ID | Objetivo/componente | Inputs → output | Dependencias | Responsable / revisor | Prueba | Criterio de aceptación y bloqueantes |
|---|---|---|---|---|---|---|
| T00 | Registrar alcance, roles y conflictos documentales | 01–06/antecedentes → DECISIONS, OPEN_QUESTIONS, README inicial | Ninguna | CO / RC+QA | U01 | Alcance positivo y todos los bloqueos con validador; bloquea autorización si roles no asignados. |
| T01 | Fijar entorno y backend candidatos | Código/dependencias → inventario exacto y capabilities | T00 | DEV+MT / QA | U02 | Versiones/rutas trazables; rango de dependencia no tratado como instalación. Bloqueo: entorno no disponible para ejecutar. |
| T02 | Resolver decisiones científicas mínimas | 02–04 → condiciones, políticas, métricas y config propuesta | T00 | RC+RD / EST+QA | U01,U03 | Tres condiciones/listas y perfiles ratificados; no parámetros elegidos por resultado. Bloquean decisiones DP aplicables. |
| T03 | Crear contratos ejecutables y configuración estricta | 03–05 → schemas/, plantilla manifest, loader config | T01,T02 | DEV+RD / QA | U03,D01 | Rechaza columnas/valores inválidos y secretos; plantilla no ejecutable distingue nulos de recursos resueltos. |
| T04 | Crear fixtures/oracles versionados | 03/04/04a/06 → fixtures y expectativas revisadas | T02 | DEV / RC+QA | U04–U13 | Esperados derivados independientemente de implementación; incluye casos adversos. Bloqueo: fórmula no ratificada. |
| T05 | Adaptador de esquema/identidad/referencias | Schema remoto, testimonio y 03 → lectores por variante y parsers | T03,T04 | DEV+RD / QA+BIB | D01–D06 | Conserva raw/crosswalk/observabilidad, distingue publicación ausente de columna ausente. Bloqueo: variante real desconocida para base. |
| T06 | Exportación coherente read-only o recepción de snapshot | Origen autorizado o paquete congelado → snapshot completo + descriptor | T05 | RD+DEV / QA | I01,I02,D07 | Completitud/hash/consistencia probados; sin vistas mezcladas ni escritura a origen. Base real requiere autorización externa. |
| T07 | Preparación y cohortes | Snapshot, GO, decisiones/crosswalks → preparados y cobertura | T03–T06 | RD+DEV / RC+QA | D02–D08,I03 | Misma entidad no duplicada; pérdidas y solapamientos explícitos; NOT desconocido no false. Bloqueo: política no aceptada. |
| T08 | Perfil IC verificable y fijo | Referencia preparada+GO+04 → perfil y comprobación de backend | T01,T07 | DEV+MT / RC+QA | U06,U07,I04 | Unidad, cierre, log y denominadores coinciden con contrato o se bloquea variante. |
| T09 | MBL conforme y detección de fallback | Grafo/04/rutas backend → adaptador aceptado o bloqueo | T01,T04 | DEV+MT / RC+QA | U04,U05,U12 | DCA por profundidad distinguido de shortest path; fallback defectuoso no publicado como métrica. Bloqueo: discrepancia histórica no resuelta. |
| T10 | IC y Lin con estados correctos | Perfil+04 → primitivas/guardas y detalle | T04,T08 | DEV / RC+QA | U06–U08,U12 | Cobertura, MICA y cero/NA conformes, no float cero usado como prueba de soporte. |
| T11 | Wang con ruta/relaciones/pesos explícitos | GO+04+backend → adaptador y metadata | T01,T04 | DEV+MT / RC+QA | U09,U12 | Relaciones/pesos efectivos comprobados; no afirmar part_of activo sin configuración. |
| T12 | Agregación y tabla larga | Preparados+primitivas aceptadas → resultados de cuatro familias | T07,T09–T11 | DEV / QA+EST | U10–U12,I05 | Pares únicos sin diagonal, IC por términos, estados y todas las filas previstas; no BMA sustitutivo. |

### 5.2. Operación, piloto y extensiones

| ID | Objetivo/componente | Inputs → output | Dependencias | Responsable / revisor | Prueba | Criterio de aceptación y bloqueantes |
|---|---|---|---|---|---|---|
| T13 | Store, manifests, checkpoints y publicación | 03/05 → artifacts.py y registro de tareas | T03 | DEV / QA | O01–O04 | Lectores solo ven generaciones completas, corrupción/faltantes detectados; filesystem a validar. |
| T14 | Caché y determinismo de subflujos | Specs/input hashes → caché y banco reproducible | T01,T03,T13 | DEV / QA+EST | R01–R04,O05 | Invalidación por todas las dependencias relevantes; cache miss no cero; orden no cambia input sorteado. |
| T15 | Análisis inicial del hito | Tabla larga+02 → cobertura, apareados y tabla analítica | T12,T13 | DEV+EST / RC+QA | I06,U11 | Denominadores e intersecciones visibles; réplicas no son proteínas. No requiere inferencia confirmatoria. |
| T16 | Dos figuras y ficha | Tablas analíticas/claims → F01/F02, ficha e informe renderizable | T15 | DEV / RC+QA | V01,V02 | Preguntas/ejes/NA según §12; no base/red requerida para render. |
| T17 | Ejecutar piloto futuro autorizado | Config real, recursos aceptados y selección congelada → run y logs | T00–T16, puertas aplicables | DEV+RD / QA+RC | I07,R01–R03 | Run completo o parcial declarado; ninguna tarea requerida omitida sin motivo. No se ejecuta aquí. |
| T18 | Revisar salida/coste/viabilidad | Run, pruebas e incidencias → informe y acta de puerta | T17 | RC+QA / EST+CO | GATE-P5 | Técnica y viabilidad separadas; no aceptación por score alto. Bloqueo: evidencia insuficiente para la decisión. |
| T19 | Sensibilidades de términos/representación/referencia | Plan 02 ratificado → motor y resultados de extensión | P5 GO para rama pertinente; T14 | DEV+EST / RC+QA | X01,X02,R04 | Inputs y F0 o perfiles alternativos distinguidos; tamaño de réplica no n biológico. |
| T20 | Retirada de publicaciones | Soportes resolubles+02/03 → intervención y cambios | T05,T07,T12; validación documental | DEV+RD / BIB+QA | U13,X03 | Retira artículo con alias y preserva soporte restante; bloqueada sin referencias/semántica acreditadas. |
| T21 | Asociaciones A | 03+04a+implementación acordada → perfiles y scoring tres A | T03,T07,T13; 04a ratificado | DEV+MT / RC+QA | U14,X04 | Universos/conteos/casos raros/cobertura correctos. No bloquea H1. |
| T22 | Calibración y registro bibliográfico | Muestra de desarrollo 02+manual 06 → plantillas, registros y desacuerdos | T00,T03,T05; selección/roles 06 | BIB+DEV / RC+QA | B01–B03 | Cegamiento, FK, decisiones originales y adjudicación preservados; no revisión biológica ficticia. |
| T23 | Congelar protocolo posterior y evaluación separada | Aprendizaje piloto+02/06 → versión nueva y plan reservado | T18 y extensiones que lo justifiquen | RC+EST / CO+QA | GATE-P6 | Cambios pre/post fechados y conjunto de evaluación no usado para ajuste; no afirmación confirmatoria retrospectiva. |

## 6. Artefactos operativos a crear

Esta sección asigna trabajo explícito, no genera ni presenta los artefactos como existentes. Se crearán solo los necesarios por etapa, sin infraestructura masiva.

| Artefacto | Tarea / momento | Documento normativo | Prueba y evidencia esperada |
|---|---|---|---|
| `README.md` experimental | T00 inicial; T16/T18 actualización | 01/05/07 | U01,V02: distingue código disponible/propuesto, orden de ejecución, exclusiones y estado del piloto. |
| `DECISIONS.md` | T00 antes de implementar; T02/T18/T23 actualizan | Gobernanza 01/02; operación 05 | U01: decisión, estado, motivo, rol validador, fecha real y material ya visto; sin aprobación inventada. |
| `OPEN_QUESTIONS.md` | T00 y mantenimiento por tarea | Pendientes 01–06 | U01: cada incógnita tiene ID, impacto, propuesta, validador y bloqueo; cierre enlaza decisión/evidencia. |
| `configs/pilot.yaml` | T02 borrador; T03 validador; T17 versión efectiva | 02–05 | U03: claves/tipos/recursos/listas explícitas, rechazo de placeholders y secretos; config resuelta archivada. |
| `schemas/` | T03 antes de ingesta/cálculo; extensión T21/T22 cuando corresponda | 03/04/04a/06 | D01,I05,B01: positivos/negativos sintéticos del schema y rechazo de entradas no conformes. |
| `templates/run_manifest.json` | T03 plantilla; T13 uso; T17 valores reales | 03/05 | U03,O01,R01: plantilla distinguible de instancia; instancia con hashes/versiones/tareas y sin DSN/secretos. |
| `templates/functional_claims.csv` | T22 antes de curación; no necesario completo para H1 | 06 §13 y enlaces 03 | B01: cabecera, tipos, enums, FK y claims atómicos; no conflación source_claim/working_claim. |
| `templates/review_records.csv` | T22 antes de doble revisión | 06 §14 y persistencia 05 | B01–B03: evidence/synthesis/adjudication, acceso, cegamiento, sucesión y conservación de originales. |

Las configuraciones de ejemplo de documentos anteriores son PROPOSTA NO EXECUTADA. No se copian como instancias reales con IDs inventados. `schemas/` no necesita cubrir tablas de embeddings/estructura fuera de alcance para aceptar datos GO.

## 7. Fixtures y estrategia de pruebas

### 7.1. Niveles de entorno, separados

1. Unitario offline: datos abstractos y mini-OBO, sin base/red. Prueba fórmulas, dominio y estados.
2. Integración sobre archivos fixture: snapshot sintético versionado y resultado esperado; valida pipeline completo sin PostgreSQL.
3. Integración con PostgreSQL desechable de pruebas: schema/filas sintéticos autorizados, separada de producción. Permite verificar read-only, aislamiento, paginación y fallos controlados. Creación/carga solo en ese entorno futuro autorizado, no en base del usuario ni en esta sesión.
4. Adaptación a base real: solo lectura y con autorización explícita. Verifica esquema real, permisos, proyecciones, completitud y exportación, sin insertar datos, crear tablas o probar fallos destructivos.
5. Piloto científico de viabilidad: datos reales congelados aceptados, no sustituto de los cuatro niveles anteriores ni validación biológica.

La disponibilidad de un snapshot autorizado puede permitir piloto offline sin conexión nueva; se comprobará procedencia/consistencia documentada. La validación del exportador contra base real seguirá pendiente si no se usa ese camino. No declarar que una fixture demuestra la equivalencia del servidor real.

### 7.2. Paquete de fixtures propuesto

`tests/fixtures/` con manifest, versión de generador o archivos, hash a calcular, schema y expected outputs. Incluir:

- Árbol pequeño de 04 con referencia de conteos conocida y oracles analíticos.
- DAG con múltiples padres y un camino directo más corto que la profundidad máxima.
- MICA diferente de DCA y empates controlados.
- Aspectos separados, raíz, término obsoleto, alias y término fuera de perfil.
- Anotaciones vacías/únicas/duplicadas, varias evidencias y NOT conocido/desconocido.
- Dos variantes de schema: remoto y aportado por usuario, identificadas como fixtures, sin fingir dump de instalación.
- Identidades ambiguas, accessions secundarias, formas distintas y secuencias idénticas entre entidades diferentes.
- Referencias alias de un artículo, otro soporte independiente, celda ambigua, referencia no PMID y columna ausente.
- Perturbación compartida entre métricas y revisión con dos registros incompatibles/adjudicación.

Para OBO parseable se usarán IDs en namespace de prueba o formato requerido, explícitamente ficticios, sin atribuir nombres/funciones reales a un GO ID existente. El significado de los nodos abstractos y la separación de fixtures de datos reales quedarán en el manifest.

No generar oracles llamando a la misma función probada y guardar su salida como verdad. Un cálculo manual/analítico o una implementación independiente pequeña revisada debe fijar expectativas; golden files aprobados guardan también su justificación.

## 8. Catálogo de pruebas unitarias y de datos

Los valores numéricos siguientes son expectativas de fixtures de 04/04a, no resultados observados. Se incluyen para transformar el contrato en pruebas, no como nueva definición normativa.

### 8.1. Pruebas unitarias

| ID | Caso y procedimiento futuro | Evidencia esperada para pasar |
|---|---|---|
| U01 | Revisar paquete documental, scope y decisiones mínimas | Todas las tareas/pendientes tienen dueño/revisor por rol; no comandos de negativos/entrenamiento ni aprobación ficticia. |
| U02 | Detectar versiones/símbolos/rutas efectivas | Capabilities identifica versión exacta y ruta; backend desconocido bloquea aceptación. No confundir pyproject con instalación. |
| U03 | Config/manifest válidos e inválidos | Rechaza claves desconocidas, IDs no resueltos, seed ausente en plan aleatorio y secretos; defaults ratificados visibles. |
| U04 | MBL árbol R→A→U y R→B | Valores de 04: U–A=1, U–B=3, A–B=2; agregado de tres términos=2. |
| U05 | MBL DAG con atajo y fallback local | La variante profundidad/DCA se distingue de shortest path; ruta fallback no conforme se bloquea, no se recorta a cero. |
| U06 | Conteos IC por entidades y aspectos | Raíz y marginales coinciden con oracles; duplicar alias/filas no cambia N ni conteos. |
| U07 | IC cubierto, universal y ausente | Bajo fixture de cuatro entidades: IC(A)=ln2 e IC(U)=ln4; universal cubierto=0, no cubierto=null, N=0 bloqueado. |
| U08 | Lin MICA, cero y dominio | U–A da d=1/3 en fixture; MICA no sustituido por DCA; denominador nulo, falta de perfil y cross-aspect con estado explícito. |
| U09 | Wang y relación efectiva | Hermanos is_a con peso 0.8 dan W=4/9 y d=5/9; cambiar relación/peso activo cambia variante; peso no activo no se anuncia como utilizado. |
| U10 | Agregación con 0/1/2 términos y duplicados | Sin pares no hay media cero; dos distintos una pareja; diagonal excluida; IC por términos; orden no altera resultado. |
| U11 | Cobertura parcial y denominadores | Unidades no cubiertas permanecen candidatas; available_mean no sustituye value; pérdida de calculabilidad aparece en tabla. |
| U12 | Inyección de None/NaN/Inf, negativos y excepciones | Guardas impiden cero o d=1 ficticios; output imposible/error se propaga y no se publica como OK. |
| U13 | Referencias múltiples y retirada de soporte | GAF alias de una referencia no son dos artículos; retirar artículo elimina alias pero preserva otro soporte; unknown no se interpreta arbitrariamente como OR/AND. |
| U14 | NPMI en fixtures de 04a | Independencia=0; coaparición exclusiva no universal=1; conteo conjunto cero y universal=null con motivos; soporte y cobertura en límites correctos. |

La rama MBL fallback puede tener un test de caracterización que documente su resultado algebraico no conforme, pero ese test no cuenta como aceptación de la métrica. El test relevante de aceptación comprueba que el sistema la rechaza o que una versión corregida y declarada cumple contrato. No esconder el bloqueo con xfail de una prueba obligatoria.

### 8.2. Pruebas de datos

| ID | Requisito de 03 | Prueba y resultado esperado |
|---|---|---|
| D01 | Schema/tipos/claves por variante | Fixtures con columnas ausentes, tipos indebidos, PK duplicadas y nulls provocan severidad/acción correcta. |
| D02 | FK y mapeos | Enlaces huérfanos, IDs locales de distinto ámbito y secundarios ambiguos se registran; no first match ni desaparición por join. |
| D03 | Claims y procedencia | Varias categorías originales sobreviven al merge de entidad; no colapso binario definitivo. |
| D04 | Formas/taxonomía/duplicación | Misma secuencia no fusiona automáticamente taxones/isoformas; conflictos bloquean unidad conforme a política. |
| D05 | GO/NOT/relaciones/evidencias | Código desconocido, NOT desconocido, alias, obsoleto y raíz tratados por 03/02; no añadir false o evidencia experimental derivada. |
| D06 | Publicaciones/identificadores | PMID/DOI/local/GO_REF diferenciados; columna ausente, source_null y not_exported no equivalentes. |
| D07 | Snapshot/versiones/compatibilidad | Hash alterado, OBO/perfil incompatible o extracción inconsistente bloquean recurso; no «latest» dinámico. |
| D08 | Cohortes/exclusiones/solapamientos | Pertenencias y exclusiones reconciliadas; referencia no negativa; intersecciones detectadas según política. |

No se exige que el dato raw sea perfecto para describirlo: se exige que errores se detecten y cuarentenen o limiten de forma trazable. Los denominadores se reconcilian por registros/entidades sin contar varias veces una misma fila con varios motivos.

## 9. Integración, reproducción y operación

### 9.1. Integración propuesta

| ID | Prueba futura | Criterio de aceptación |
|---|---|---|
| I01 | Exportador contra fixture PostgreSQL desechable | Identifica schema y conserva columnas/claves; lectura read-only con vista estable; no DDL en exportación. Pruebas de permisos denegados solo sobre datos de test. |
| I02 | Adaptador sobre base real autorizada, o validación de paquete recibido | Descriptor/privilegios/aislamiento/proyección y procedencia verificables. No probar escrituras en producción; consultar privilegios y parámetros y registrar política. |
| I03 | Raw→canónico→términos sobre fixtures | Tablas lógicas y pérdidas iguales al oracle; acceso a red/base bloqueado durante cómputo offline. |
| I04 | Construir/cargar perfil y puntuar varias condiciones | Mismo profile_id, miembros y conteos antes/después; no reconstrucción al filtrar o retirar. |
| I05 | Primitivas→agregación→tabla larga | Misma entidad/aspecto/condición aparece con cada métrica prevista o estado; PK, status y contadores válidos. |
| I06 | Tabla larga→análisis | Diferencias solo en pares válidos; transiciones sobre todos los elegibles; datos ausentes no sesgan ocultamente el denominador. |
| I07 | Flujo offline completo y CLI propuesta | Plan completo, manifest final, tabla, dos figuras y ficha generables sin base/red; fallos de componente no desaparecen. |

I01 puede usar escritor auxiliar en una base de test para demostrar estabilidad ante cambios concurrentes. Eso no autoriza escritura a la base real. Si el origen falla a mitad de extracción, reiniciar una vista coherente conforme a 05; no mezclar consultas de sesiones nuevas bajo un snapshot aceptado. La regla de PostgreSQL y el momento de fijación se verifican contra P3.

### 9.2. Reproductibilidad

| ID | Ensayo de reproducción | Evidencia exigida |
|---|---|---|
| R01 | Dos reconstrucciones limpias del mismo snapshot/config/código | Inputs, universos, conteos y tablas lógicas idénticos por clave/hash de 03; ninguna dependencia no fijada. |
| R02 | Individual/batch, orden permutado y límites de partición distintos | Mismos conjuntos, status, cobertura y resultados dentro de tolerancia aceptada; sin dobles filas o pérdidas. |
| R03 | Caché fría, caliente y represa de run interrumpido | Mismo contenido científico normalizado que ejecución completa; trazabilidad muestra qué se reutilizó. |
| R04 | Réplicas con semilla fija y orden de planificación distinto | Mismas selecciones de términos por unidad/repetición, compartidas entre métricas; seed cambia recurso de réplica, no F0. |

Campos volátiles excluidos de comparación científica: run_id/attempt_id cuando corresponda, timestamps de operación, duración, rutas de staging y orden físico de archivos. Nunca excluir valores, status, motivos, claves de entidades, semillas, perfiles, versiones, denominadores o exclusiones para hacer coincidir resultados. Cualquier otro campo volátil debe estar en allowlist revisada de 05.

Conteos, IDs, pertenencias y status se comparan exactamente. Propuesta de 04 para floats: tolerancia absoluta 1e−12 y relativa 1e−9, ratificada antes de probar; no es umbral biológico ni permiso para diferencias de implementación. En el mismo entorno/ruta determinista se espera igualdad lógica estable; si difiere, investigar. Un hash de floats comparables diferente no equivale por sí solo a fallo si la comparación numérica admitida explica diferencias, pero inputs/conteos no usan tolerancia. Reportar ambas comprobaciones.

Si se cambia backend/plataforma y el patrón excede tolerancia, no ampliar el margen a posteriori para pasar: justificar variante/corrección y versionar. No comparar solo puntuaciones finales: inputs distintos que casualmente dan la misma media no son reproducción aceptada.

### 9.3. Fallos controlados, caché e idempotencia

| ID | Inyección/escenario | Comportamiento esperado |
|---|---|---|
| O01 | Cortar antes de commit marker o durante escritura | Lectores no consumen staging; generación previa permanece válida; manifiesto no declara completo el parcial. |
| O02 | Archivo truncado, hash inválido o tarea faltante | Detectar corrupción/incompletitud; no reutilizar checkpoint por mera existencia. |
| O03 | Reanudar tras error de lote; repetir misma tarea | Solo tareas compatibles reutilizadas; sin duplicación; nuevo attempt y registro de fallos. |
| O04 | Dos escritores o filesystem incompatible | Lock/rechazo o publicación coordinada; no sobrescritura silenciosa; atomicidad/durabilidad no supuestas en NFS/object store. |
| O05 | Cambiar GO, perfil, versión, pesos, condición, umbral o término | Claves de caché cambian cuando el output/estado depende del cambio; sin reutilización incompatible ni cache miss=0. |

Probar también fallo de figura separado de fallo científico: se puede rehacer render desde tablas completas sin recalcular perfiles. Unexpected exception no se convierte en NA de dominio ni en cero; se detiene la rama y el hito queda incompleto salvo política explícita de fallo local recuperable.

### 9.4. Extensiones y revisión

| ID | Prueba | Resultado esperado |
|---|---|---|
| X01 | Reducción de términos versus filas | La intervención de 02 selecciona conjuntos correctos, replica tamaños y separa pérdida de soporte; no duplica unidades biológicas. |
| X02 | Sensibilidad de representación/referencia | Cambios de query con F0 distinto de cambios de perfil; recursos alternativos identificados y contabilidad visible. |
| X03 | Retirada documental | Artículo con alias, soporte alternativo, soporte conjunto acreditado y ambigüedad producen comportamientos de 03/06, sin eliminación excesiva. |
| X04 | Conteos/asociaciones tres pares | Cada universo coherente; no compartir marginales incompatibles; cero no observado no tratado como asociación negativa robusta. |
| B01 | Importar plantillas 06 con casos válidos/erróneos | FK/enums/campos condicionales, null y targets correctos; conservación de fuente e interpretación por separado. |
| B02 | Paquete ciego y detección de filtración | Sin score/estrato en archivos, nombres, orden o notas; ruptura se registra; no etiqueta biológica derivada del score. |
| B03 | Dos revisiones, desacuerdo y adjudicación | Originals locked se preservan, nueva decisión enlazada; acuerdo preadjudicación y no evaluables diferenciados. |

## 10. Matriz requisito → tarea → prueba → evidencia esperada

Los requisitos RN son localizadores de trazabilidad de este plan, no nuevas normas científicas.

| RN / requisito | Documento rector | Tarea | Prueba | Evidencia futura esperada |
|---|---|---|---|---|
| RN01 Alcance positivo y referencia no negativa | 01 | T00,T02 | U01,D08 | Acta/README y manifests de pertenencia sin construcción negativa. |
| RN02 Listas EXP y parámetros explícitos | 02 | T02,T03 | U03,D05 | Config resuelta y diff frente al protocolo ratificado. |
| RN03 Identidad/procedencia/claims | 03 | T05,T07 | D02–D04,I03 | Crosswalk, disposiciones e informe de pérdidas. |
| RN04 Extracción coherente/read-only | 03/05 | T06 | I01,I02,D07 | Informe de schema, permisos, vista y completitud; sin credenciales. |
| RN05 MBL definida y conforme | 04 | T09 | U04,U05 | Reporte de ruta y oracle, bloqueo explícito de fallback no aceptado. |
| RN06 IC/Lin perfil, ceros, MICA | 03/04 | T08,T10 | U06–U08,U12 | Conteos, denominador, base y detalle de casos límite. |
| RN07 Wang relaciones/pesos | 04 | T11 | U09,U12 | Variante efectiva y coincidencia analítica de fixture. |
| RN08 Medias, NA y cobertura | 04 | T12,T15 | U10,U11,I05,I06 | Tabla larga completa y contabilidad de unidades. |
| RN09 Referencias múltiples/retirada | 03/06 | T05,T20 | U13,X03 | Parser/alias acreditados, soporte restante y estados. |
| RN10 F0 inmutable | 02/03/05 | T08,T19 | I04,X02 | Fingerprints de perfil iguales en perturbaciones principales. |
| RN11 Equivalencia, semillas y orden | 02–05 | T14,T17 | R01–R04 | Equivalence report y banco de selecciones reales cuando existan. |
| RN12 Atomicidad/represa/caché | 05 | T13,T14 | O01–O05 | Registro de fallos controlados y manifest de recuperación. |
| RN13 Figuras/ficha sin cálculo oculto | 02/05 | T16 | V01,V02,I07 | Figura con denominadores y tabla de datos trazable. |
| RN14 Curación independiente | 02/06 | T22 | B01–B03 | Paquetes, registros ciegos y adjudicación conservada. |
| RN15 A según anexo y no motor supuesto | 03/04a | T21 | U14,X04 | Conformidad de conteos/estados de tres A. |
| RN16 Cambios pre/post y evaluación independiente | 02/06 | T18,T23 | GATE-P5/P6 | Registro de desviaciones y nueva congelación, sin validación retrospectiva. |

El expediente de aceptación registrará para cada fila: versión del requisito, caso de prueba, resultado real, artefacto, revisor y decisión. Ahora no se rellena con resultados inexistentes.

## 11. Procedimiento del piloto

### 11.1. Entrada

Debe existir una cohorte pequeña con pertenencia/identidad trazable, elegida con reglas previas de 02 y sin seleccionar por scores ya vistos. Se podrán cubrir de forma deliberada variedad de fuente/cobertura para viabilidad, describiéndolo como muestra de desarrollo y no como probabilística representativa si no lo es. Tamaño y presupuesto se deciden antes de selección con recursos reales; no se presupone un n aprobado ni potencia.

Los casos artificiales de raíz, vacíos o errores se prueban en fixtures; no se fuerza a que el piloto real contenga todos esos casos ni se buscan ejemplos por score para aparentar validación. Si no hay casos calculables suficientes para determinada comparación, la viabilidad de esa rama es reformular/ajornar, no inventar valores.

Condiciones de entrada: puertas P0–P4 aplicables; autorización de uso/exportación; schema y políticas de datos revisados; GO y perfil fijados; cuatro backends aceptados; config resuelta y plan de tareas; pruebas offline registradas y extract path validado si se utiliza.

### 11.2. Secuencia futura

1. Registrar decisión de inicio, contratos/versiones y qué resultados previos se conocen.
2. Recibir o exportar snapshot coherente y verificar fingerprints; no enriquecer dinámicamente durante reconstrucción.
3. Preparar entidades/claims/anotaciones, emitir cobertura/exclusiones y validar cohortes/solapamientos.
4. Construir o cargar perfil IC aceptado y fijar semántica GO; registrar dependencias efectivas.
5. Generar plan de outputs para cada entidad/aspecto/condición/métrica, incluyendo filas esperables sin valor.
6. Calcular cuatro familias con F0 fijo; guardar detalle/contadores/estados y completar checkpoints validados.
7. Construir análisis descriptivo apareado y transiciones de calculabilidad de 02.
8. Generar F01/F02 y ficha de proteína desde tablas publicadas, sin base/red.
9. Repetir cómputo/reconstrucción sobre los mismos inputs y comparar; ensayar represa/caché con fixtures o copia de trabajo, no alterar datos raw.
10. Emitir informe de salida, coste, limitaciones y decisión de puerta; ningún score eleva por sí mismo el estado biológico.

La reducción aleatoria del plan mínimo científico E03 y preparación bibliográfica E09 de 02 siguen siendo compromisos de etapa posterior al circuito visual básico si no se ejecutan junto a H1. Se indicará su estado pendiente y no se llamará «plan científico mínimo completado» a H1 técnico solamente.

### 11.3. Registro de incidencias y salida

Informe futuro mínimo: alcance/cohorte y selección, recursos/manifests, versiones y backend por familia, pruebas reales y skips, cobertura por condición, errores vs NA, resultados/figuras, pérdidas y sesgos, costes observados, desviaciones, tareas pendientes y recomendación por puerta. Separar observación, interpretación e hipótesis nuevas.

Resultados inesperados no se «corrigen» eligiendo otra seed, otro perfil o excluyendo casos post hoc. Registrar, reproducir y abrir tarea con impacto. Si se arregla código, identificar qué resultados previos quedan invalidados y repetir la rama completa afectada.

## 12. Gráficas y ficha de proteína

No se generan gráficos de datos ficticios presentados como resultados. V01/V02 son pruebas propuestas de presentación.

### F01 — Disponibilidad de resultados por condición

- Pregunta: ¿qué parte de la cohorte elegible tiene resultados calculables en cada condición y familia?
- Eje x: condiciones ALL, EXP-convencional y EXP-ampliada, con paneles por métrica/aspecto.
- Eje y: número de entidades o proporción sobre el mismo total elegible declarado; si se muestran ambos, rotularlos sin ambigüedad.
- Segmentos: OK, no estimables por dominio/cobertura, bloqueados y errores operativos diferenciados; status específicos agrupados con leyenda y detalle tabular.
- No estimables: permanecen en la barra/denominador; no se pintan como valor numérico cero de la métrica.
- Prueba V01: suma de segmentos igual a elegibles, categorías no perdidas, datos de gráfico exportables y coincidentes con tabla.

### F02 — Cambio apareado ALL–EXP

- Pregunta: ¿cómo cambian valores en las mismas proteínas y qué casos dejan de ser calculables?
- Panel principal: x=valor ALL, y=valor EXP-convencional o EXP-ampliada, panel por familia/aspecto, línea de igualdad. No mezclar escalas de IC/MBL y dissimilaridades.
- Panel complementario de la misma figura: distribución de diferencia EXP−ALL conforme a 02, con número apareado válido. No es diferencia de medias de dos cohortes distintas.
- No estimables: no se imputan en el scatter; anotar fuera del área de valores sus transiciones y remitir F01/tabla de estados. No unirlos a un punto de origen artificial.
- Prueba V02: misma intersección de IDs que tabla apareada; signo de diferencia, ejes, unidades, perfiles y n correctos; si no hay pares válidos se muestra aviso y distribución no estimable, no figura vacía interpretada como estabilidad.

Ficha: identidad y fuente/atribución, anotaciones/evidencia, recursos, valores/estados, términos/parejas explicativas cuando existan y referencias por origen. Debe señalar si no hay publicación observable o revisión. No incluir decisión global de confianza ni afirmar funciones a partir de scores. Las fichas ciegas de 06 son otro producto: no incluyen métricas aunque esta ficha analítica sí pueda mostrarlas.

## 13. Coste y rendimiento por medir

| Medida a recoger en ejecución futura | Uso |
|---|---|
| Tiempo de lectura/exportación y volumen por tabla | Detectar extracción repetida/materialización excesiva. |
| Tiempo de preparación y filas/entidades perdidas | Coste de joins, parsing, crosswalk y validación. |
| Tiempo/coste de perfil y tamaño de universo | Separar construir referencia de puntuar consultas. |
| Pares candidatos, únicos consultados y hits/misses de caché | Comprobar reutilización sin ocultar conteo. |
| Tiempo por familia y agregación, distribución por tamaño de términos | Identificar proteínas/cierres costosos sin inventar latencia universal. |
| Pico de memoria/proceso, tamaño de artefactos y scratch | Justificar tamaño de lotes y workers limitados. |
| Tiempo de render e importación curatorial | Separar presentación y revisión del cálculo. |
| Número de retries/fallos/checkpoints y tareas recuperadas | Evaluar fiabilidad/coste de operación. |

Presupuestos de tiempo, memoria, almacenamiento y revisión humana permanecen provisionales y sin cifra comprometida. Se acordarán según entorno y recursos antes de ejecutar. Si se supera un límite, detener/cerrar tarea según política y revisar coste; no reducir muestra o réplicas después de ver resultados sin desviación registrada.

Cuellos de botella plausibles no medidos: `query_all` con fetchall, preparación de todos los subgrafos Wang, pares repetidos, crecimiento de coocurrencias y multiplicación de perturbaciones. Estrategia inicial de 05: secuencial, una extracción, preprocessing compartido, pares necesarios y caché versionada; paralelismo limitado solo tras medición. No dashboard, GPU ni distribución como solución por defecto.

## 14. Puertas GO / REFORMULAR / AJORNAR

Puertas por rama: GO habilita el siguiente paso indicado, no todo el programa ni una afirmación biológica. GO se interpreta aquí como «continuar».

| Puerta | GO: evidencia verificable | REFORMULAR | AJORNAR | Revisión |
|---|---|---|---|---|
| P0 Contratos mínimos | Alcance/roles, listas y decisiones necesarias ratificadas, conflictos visibles | Definiciones incompatibles o demasiado amplias para ejecución | Falta autoridad para aprobar | CO+RC+RD |
| P1 Fixtures/contratos | Casos válidos/adversos y oracles revisados, schemas probados | Tests circulares o faltan casos críticos | No hay capacidad de ejecutar pruebas offline | QA+RC |
| P2 Datos | Snapshot coherente y reconstruible, identidad/NOT/observabilidad autorizadas y denominadores | Ingesta limitada requiere alcance degradado explícito | Sin datos autorizados o corrupción no resuelta | RD+QA+RC |
| P3 Métricas | Cuatro familias cumplen contrato con ruta/versiones y estados verificables | MBL/Lin/IC/Wang difieren: corregir/adoptar variante por enmienda | Familia no disponible o no verificable | MT+QA+RC |
| P4 Flujo | Offline fixture completo, recuperación/reproducción y presentación correctas | Mezcla de perfiles, estados o tareas perdida | Entorno/persistencia no verificable | DEV+QA |
| P5 Piloto | H1 técnico completo; preguntas de viabilidad evaluables y límites declarados; costes observados compatibles con presupuesto acordado | Cobertura o confusores impiden pregunta original: acotar, sin ocultar hallazgo | Falta recursos, soporte o evidencia para decidir | RC+EST+QA+CO |
| P6 Siguiente evaluación | Protocolo/manual/ranking/endpoint congelados y muestra reservada independiente según 02 | Material de evaluación usado para ajuste: nueva evaluación o carácter exploratorio | No existe evidencia/presupuesto adecuado | RC+EST+BIB+CO |

Una batería con pruebas obligatorias skipped/xfail no satisface P1/P3/P4 de la rama afectada. Se puede aprobar otra rama y declarar la pendiente. Pruebas de extensión opcional pueden omitirse antes de implementarla, con reporte, pero no se cuentan como pasadas.

Para viabilidad no se exige media alta o gran cambio de métrica. Un perfil estable o una ausencia de señal pueden ser resultados legítimos. Si no hay cobertura suficiente para el objetivo, reportarlo como conclusión de auditoría y reformular, no bajar umbrales de 04 después de inspeccionar para «salvar» el resultado.

Validación biológica solo puede expresarse por claims revisados y material de 06, con alcance. Ni P5 ni tests otorgan automáticamente la etiqueta de moonlighting a ninguna proteína.

## 15. Congelación, desviaciones y siguiente fase

Distinguir cuatro tiempos: borrador previo; versión autorizada para piloto; cambios posteriores al piloto con resultados ya conocidos; versión congelada para evaluación independiente. El encabezado 0.1 no demuestra preregistro ni aprobación.

Cada desviación registra ID, fecha, propuesta/decisión, documento normativo afectado, versión previa/nueva, motivo, resultados/material ya consultados, rol responsable/revisor, outputs invalidados y necesidad de repetir. Revisión editorial sin cambio semántico se distingue de cambios de inclusión, perfil, fórmula, soporte o endpoint. No reescribir el historial para que decisiones exploratorias parezcan previas.

Después de T18: revisar costes/cobertura, decidir qué sensibilidades/A/curación desarrollar y actualizar documentos responsables por enmienda. Después de desarrollo, T23 congela endpoint bibliográfico y regla de priorización/validación de 02/06 antes de abrir material reservado. Un nuevo conjunto de positivos no es negativo, y una evaluación independiente no se obtiene cambiando solo el run_id.

Si se cambia una fórmula o se corrige backend, versionar métrica/código, invalidar cachés pertinentes y recomputar outputs afectados. Un nuevo OBO o datos genera recursos nuevos. Parámetros efectivos se archivan en config y manifest; no se dejan únicamente en celdas o narrativa.

La fase posterior sigue separada: no se autoriza selección de negativos ni entrenamiento por completar el piloto. Requerirían otro alcance/protocolo.

## 16. Decisiones pendientes y checklists

### 16.1. Decisiones de este plan

| ID | Decisión | Estado |
|---|---|---|
| D07-01 | H1 exige cuatro familias y tres condiciones según 02 | PROPOSTA conservada de 01–05 y encargo actual. |
| D07-02 | Entregas parciales no equivalen a aceptación completa | Regla explícita del encargo; operación propuesta. |
| D07-03 | Técnicamente correcto, científicamente viable y biológicamente sustentado son niveles distintos | Regla de interpretación del paquete. |
| D07-04 | Tests por requisitos con oracles y fixtures antes de piloto real | PROPOSTA operativa; no tests ejecutados. |
| D07-05 | No benchmark temporal, muestra o potencia ficticios | Restricción del encargo; presupuestos por decidir. |

### 16.2. Pendientes accionables

| ID | Pregunta/impacto | Propuesta provisional justificada | Quién valida | Bloqueo |
|---|---|---|---|---|
| DP-01 | ¿Quién asume roles, sede y aceptación? | Roles de §5 y revisión independiente en críticos; sin disponibilidad supuesta. | Coordinación | Sí autorización e integración estable. |
| DP-02 | ¿Qué listas/condiciones/políticas y recursos se ratifican? | Formalizar decisiones mínimas 02–04 antes de fijar config. | RC+RD+EST | Sí comparación válida. |
| DP-03 | ¿Qué schema real y semántica bibliográfica existen? | Descriptor efectivo, parsers por formato y observabilidad; no elegir remoto frente a usuario sin evidencia. | RD+MT+BIB | Sí ingesta; retirada por bloque. |
| DP-04 | ¿Qué rutas exactas conforman MBL/IC/Wang/Lin? | Tests U04–U12 y versión efectiva; bloquear no conformes. | MT+RC+QA | Sí H1 completo. |
| DP-05 | ¿Qué cohorte y tamaño/budget permiten piloto? | Selección previa de viabilidad según 02, sin cifras históricas como aprobación. | RC+RD+CO | Sí T17. |
| DP-06 | ¿Hay snapshot autorizado o exportación por validar? | Paquete coherente aceptado o extracción read-only separada; no pedir acceso para redactar. | RD/administración de datos | Sí datos reales, no fixtures. |
| DP-07 | ¿Se ratifican tolerancias y serialización? | Valores provisionales 04 y normas 03/05; no ampliarlos para ocultar divergencia. | QA+RC/EST | Sí aceptación numérica. |
| DP-08 | ¿Qué almacenamiento y garantías soportan represa? | Generaciones/checkpoints de 05, ensayo de fallo local controlado. | DEV+infraestructura+QA | Sí P4. |
| DP-09 | ¿Qué límites de coste y paralelismo? | Medir secuencial y acordar presupuesto antes de ampliar. | CO+DEV+RC | No redactar; sí ejecución bajo presupuesto. |
| DP-10 | ¿Qué manual/muestra/endpoints se usarán después? | Calibración 06 y congelación 02 antes de evaluar; no reutilizar desarrollo. | BIB+RC+EST | No H1; sí revisión/evaluación. |
| DP-11 | ¿Cómo se resolverán riesgos de privacidad/licencias? | Manifest sin secretos, permisos de recursos y textos de 03/06. | Responsables datos/licencias | Sí usos restringidos/publicación. |

### 16.3. Checklist de preparación del piloto

- [ ] Alcance positivo y exclusiones confirmados; roles/responsables asignados.
- [ ] Contratos aplicables 01–05 autorizados para el piloto, sin aprobación asumida por su redacción.
- [ ] Listas de las tres condiciones y significado de EXP ratificados en 02.
- [ ] Referencia y solapamientos, unidad/identidad y política GO definidos en 03.
- [ ] Esquema real o snapshot recibido identificados; limitaciones NOT/publicaciones acreditadas.
- [ ] GO/crosswalks/perfiles y versiones efectivos fijados; ninguna descarga latest oculta.
- [ ] Cuatro métricas con ruta/versiones aceptadas y fixtures numéricos/adversos probados.
- [ ] Config real validada, semillas de etapas aleatorias resueltas y manifiestos sin secretos.
- [ ] Extracción/ingesta validada por el camino que realmente se usará.
- [ ] Reproducción/represa/caché verificadas offline y tareas previstas reconciliables.
- [ ] Cohorte seleccionada antes de scores y regla/tamaño/budget registrados, sin potencia supuesta.
- [ ] Plan F01/F02, ficha e informe preparado y revisión de licencias/acceso completada.

### 16.4. Checklist de aceptación de salida

- [ ] Recursos/manifests corresponden a lo realmente usado y su integridad es verificable.
- [ ] Todas las entidades/familias/condiciones previstas tienen resultado o estado; ningún fallo desaparece.
- [ ] Las cuatro familias requeridas cumplen contrato; bloqueos no ocultos como opcionales.
- [ ] Cobertura y transiciones se reportan sobre denominadores explícitos, sin NA=0.
- [ ] F0 no cambia en condiciones/perturbaciones principales.
- [ ] Tabla normalizada reproducida y comparación de inputs/resultados documentada.
- [ ] F01/F02 y ficha derivan de tablas, muestran n/limitaciones y no llaman verdad a scores.
- [ ] Pruebas realizadas, skipped/xfail/fallidas y motivos aparecen en el expediente.
- [ ] Incidencias, exclusiones, costes observados y desviaciones están registrados.
- [ ] Informe separa aceptación técnica, viabilidad y revisión biológica pendiente.
- [ ] Puerta GO/REFORMULAR/AJORNAR firmada por roles requeridos, con alcance y razón.
- [ ] Cambios posteriores y siguiente fase independiente definidos; sin entrega negativa/entrenamiento.

No se marcan casillas en esta redacción: todavía no hay evidencia de ejecución del piloto.

## 17. Inventario de fuentes y límites

### 17.1. Lectura remota de BioData

Repositorio https://github.com/CBBIO/BioData ; revisión https://github.com/CBBIO/BioData/commit/ed073bd4df680a3b45ee69943916e196d28b63b6 . Se comenzó por README/árbol y se fijaron las lecturas siguientes. La recuperación web de portada falló, pero el connector GitHub permitió lectura. Leer código no conecta al PostgreSQL del laboratorio.

| ID | Localizador y símbolos/secciones | Evidencia y límite |
|---|---|---|
| G1 | [README.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/README.md), What Is In This Repo; Running Tests | DOCUMENTAT NO VERIFICAT para capacidades anunciadas; no ejecución. |
| G2 | [CBBIO/GO.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/GO.py), `prepare_term_counts`, `information_content`, `semantic_similarity`, `group_similarity`, `minimal_branch_length`, `_as_float`, fallback | VERIFICAT EN CODI: archivo leído, rutas y riesgos estáticos. |
| G3 | [tests/test_go.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_go.py), fixture mini-OBO y tests IC/Lin/Wang/MBL/errores | VERIFICAT EN CODI: tests leídos y limitados; no resultados ejecutados. |
| G4 | [tests/test_biodata_integration.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_biodata_integration.py), `integration_client`, tests proteína/GO/query | VERIFICAT EN CODI: skips por config/conexión/datos; no aceptación de nueva extracción. |
| G5 | [CBBIO/BioData.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/BioData.py), `BioDataClient.__init__`, `query_all`, `transaction`, `get_protein_go_annotations`, métodos de accesiones/metadatos | Código visible leído; respuesta truncada posteriormente, no auditoría exhaustiva. |
| G6 | [sql/schema.sql](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/sql/schema.sql), tablas y constraints de anotaciones/protein/accession/go_terms | VERIFICAT EN CODI: dump remoto no necesariamente igual a instalación. |
| G7 | [docs/GO.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/docs/GO.md), Loading/IC/Similarity/Group Similarity | Documentación leída, ejemplos no ejecutados. |

La versión instalada de goatools y su comportamiento completo son NO ACCESSIBLE aquí; 04 contiene contraste upstream, no certificación de instalación. No se solicita instalar nada para entregar el plan.

### 17.2. Fuentes primarias de soporte consultadas

- P1. Pytest, «How to use skip and xfail to deal with tests that cannot succeed»: https://docs.pytest.org/en/stable/how-to/skipping.html , consultado 2026-10-26. Skip/xfail se reportan por separado; una suite verde no prueba ejecución de todos los requisitos. La política de aceptación es propuesta del proyecto, no exigencia de pytest.
- P2. Gene Ontology Consortium, GAF 2.2: https://geneontology.org/docs/go-annotation-file-gaf-format-2.2/ , consultado 2026-10-26, Reference, Relation y Gene Product Form ID. Respalda casos de parser, no resultados biológicos del corpus.
- P3. PostgreSQL, «SET TRANSACTION»: https://www.postgresql.org/docs/current/sql-set-transaction.html , consultado 2026-10-26, aislamiento, momento de fijación y read-only. No demuestra configuración del servidor del usuario.

Las fuentes primarias de fórmulas y moonlighting se mantienen en 04/04a/06; 07 convierte sus contratos en expectativas y no inventa DOI/PMID ni atribuye validación científica a estas pruebas de software.

### 17.3. Antecedentes disponibles y no accesibles

- 01–06 v0.1 y anexo 04a: contenido completo de generación visible en historial PEC de esta conversación. Archivos físicos previos no recuperados como entradas independientes de esta sesión; no se supone clon, aprobación o presencia en GitHub.
- `Dossier_extensio_PIS_BioData_PEC_v0.1.md`: adjunto localizado en sesiones previas y contenido visible en historial, §§6,8,10–11; propuesta inicial de piloto/validación, no implementación.
- `Especificacion_metricas_asociacion_GO_BioData_v1.1.md`: texto de generación visible en historial tras solicitud 2026-10-26 13:49 CET; archivo independiente no localizado en las fuentes accesibles actuales. 04a declara recuperación textual, no preservación byte a byte.
- Propuestas de experimentación/infraestructura, solicitudes 2026-10-26 20:29/20:56 CET: accesibles como conversación, no código ejecutado.
- C4: esquema `\d protein_go_term_annotation` con publicación aportado por usuario, solicitud 20:56 CET; DOCUMENTAT NO VERIFICAT sobre la instalación. Diferencia G6 no resuelta aquí.
- `mfp_bibliographic_catalog_vision.md`: documento localizado y recuperado en turnos anteriores, contenido accesible en historial, Purpose/Identity Model/Provenance. En esta exploración no se volvió a recuperar el archivo solicitado; no se inventa contenido nuevo. Catálogo de atribuciones, no clasificador ni revisión hecha.
- `canonical_multifunctional_protein_data_dossier.md`: extractos previos accesibles en historial; heterogeneidad y procedencia, no prueba de enforcement o cohortes efectivas.
- `dataset_designer_functional_contract.md`, §§6–9: Project File recuperado en esta consulta. Traza exclusiones y validación, pero selección negativa histórica no se traslada al piloto.
- `Appendix_Z_Revision_and_Reproducibility_Plan.md`, Z.1 y bloque A: extractos recuperados en consulta, integridad de afirmaciones; no resultados actuales.
- `PEC_FUNCTIONAL_CONTRACT.md`, §1: Project File recuperado; papel documentado de clasificador, fuera de la fase.
- `PEC_PRAGMATIC_RESEARCH_AND_ORGANIZATION_GUIDE.md` y `PEC_Reproducible_Benchmark_Audit_2026.md`: material recuperado de planes históricos de benchmark. No son autoridad para introducir MF:NMF o entrenamiento en este encargo.
- `PEC_Phase0_questionari_abast_cientific.md`, A4 y bloques de alcance: recuperado. Conflictos de categorías experimentales/labels ya explicitados por 02; no se selecciona una política histórica silenciosamente.

NO ACCESSIBLE: base real, credenciales, datos/exportaciones, pruebas ejecutadas, costes reales, adjudicaciones, disponibilidad de revisores y corpus final reconciliado. Repositorios PIS y mfp-bibliography no inspeccionados remotamente; sus roles solo documentales/propuestos. Las rutas operativas configs/schemas/templates son tareas futuras, no archivos existentes acreditados.

### 17.4. Límites de este plan

Una especificación extensa no demuestra que el piloto sea viable. Puede haber datos sin soporte, dependencias incompatibles, recursos restringidos o preguntas no evaluables. El plan permite declarar esas limitaciones y entregar partes útiles sin falsear aceptación completa. No ofrece una fecha o coste garantizado ni una conclusión biológica anticipada.

## 18. Comprobación de coherencia documental

- Con [01_dossier_experimento.md](01_dossier_experimento.md): alcance positivo e hito preservados; ninguna tarea de negativos, entrenamiento o dashboard obligatorio.
- Con [02_protocolo_cientifico_y_analisis.md](02_protocolo_cientifico_y_analisis.md): listas, comparaciones, réplicas, muestras y evaluación permanecen allí; el circuito visual H1 no se confunde con completar todo el plan científico mínimo.
- Con [03_contrato_datos_y_recursos.md](03_contrato_datos_y_recursos.md): pruebas de identidad, soporte, observabilidad, universos y equivalencia aplican sus reglas, no las reescriben.
- Con [04_especificacion_metricas.md](04_especificacion_metricas.md) y [04a_asociaciones_interaspecto.md](04a_asociaciones_interaspecto.md): oracles y guardas remiten a esas definiciones; no se cambian umbrales para pasar tests y A no se asume implementada.
- Con [05_diseno_tecnico.md](05_diseno_tecnico.md): componentes/CLI/store/caché/represa se convierten en tareas y evidencia; sin plataforma nueva ni ejecución implícita.
- Con [06_manual_revision_bibliografica.md](06_manual_revision_bibliografica.md): plantillas/cegamiento/decisiones se validan como proceso y no como verdad desde métricas.

Los enlaces son destinos del paquete documental, no certificación de aprobación. Las reglas viven en documentos y los valores efectivos en configuración/manifiestos reales. Estado final: plan para ejecución futura con backlog, camino crítico, pruebas, puertas y pendientes explícitos; ninguna tarea o prueba se declara realizada por esta redacción.
