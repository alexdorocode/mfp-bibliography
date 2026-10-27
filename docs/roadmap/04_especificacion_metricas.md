# Especificación de métricas GO para la auditoría del corpus positivo

| Campo | Valor |
|---|---|
| Archivo | `04_especificacion_metricas.md` |
| Versión documental | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha | 2026-10-26 |
| Responsable y revisores científico/técnico | Pendientes de asignar |
| Fuentes | Inventario trazable de §15; código remoto, antecedentes y fuentes primarias diferenciados |
| Dependencias | 01 alcance; 02 protocolo; 03 datos/recursos; 04a asociaciones; 05 arquitectura; 06 curación; 07 aceptación |
| BioData consultado | `CBBIO/BioData`, commit `ed073bd4df680a3b45ee69943916e196d28b63b6` |
| Dependencia comparativa consultada | `tanghaibao/goatools`, árbol observado `5b88eefcd8284f5d146d36728b4925785b563125`; no identifica la versión instalada por el usuario |

Este catálogo define cálculos propuestos y contrasta sus requisitos con el código leído. No acredita operación de una base, entorno o notebook. No se han ejecutado experimentos, tests ni benchmarks; los ejemplos son deducciones matemáticas, no resultados de ejecución. No se han modificado repositorios.

## Índice

1. Autoridad, alcance y leyenda
2. Inventario y estado real de implementación
3. Contrato común de dominio, pares y agregación
4. Ficha MBL clásica identificada en el proyecto
5. Ficha IC por término y media proteica
6. Ficha 1−Wang
7. Ficha 1−Lin
8. Asociaciones interaspecto y fuente normativa única
9. Fichas de descriptores de evidencia, términos y cobertura
10. Estados, ausencia y estabilidad numérica
11. Esquema largo de resultados propuesto
12. Ejemplos sintéticos y pruebas esperadas
13. Disponibilidad para primera entrega y coste
14. Decisiones, pendientes y aceptación
15. Inventario de fuentes y límites
16. Dependencias y comprobación de coherencia

## 1. Autoridad, alcance y leyenda

Este documento gobierna fórmulas, dominio, agregación, cobertura e interpretación numérica. El anexo [04a_asociaciones_interaspecto.md](04a_asociaciones_interaspecto.md) es la única fuente de las fórmulas y reglas específicas de las tres asociaciones. No se repiten aquí sus expresiones ni umbrales. 03 gobierna población y preparación de datos; 02, condiciones de evidencia, perturbaciones e inferencia; 06, juicio bibliográfico. Una regla de cálculo no decide qué proteína es biológicamente positiva.

La fase solo audita y caracteriza positivos atribuidos. No selecciona negativos ni entrena clasificadores. El corpus estadístico de referencia no es clase negativa y el pool reservado no se etiqueta mediante estas métricas. No se construye un índice global de confianza ni se considera que una puntuación pruebe multifuncionalidad o moonlighting.

| Acrónimo/símbolo | Significado |
|---|---|
| GO | Gene Ontology. |
| MF/BP/CC | Función molecular/proceso biológico/componente celular. MF no significa proteína multifuncional. |
| MBL | Etiqueta utilizada por el proyecto para `minimal_branch_length`; su semántica concreta se identifica en §4, no se deduce del acrónimo. |
| IC | Information Content, contenido informativo. El código de evidencia GO `IC` es otro concepto. |
| DCA | Deepest Common Ancestor, ancestro común de máxima profundidad. |
| MICA | Most Informative Common Ancestor, ancestro común con mayor IC. No tiene por qué coincidir con DCA. |
| DAG | Grafo dirigido acíclico; no es necesariamente un árbol. |
| NPMI | Información mutua puntual normalizada, base de A. |
| BMA | Best Match Average; mejores correspondencias entre dos conjuntos, no dispersión interna. |
| P, X, c | Proteína reconciliada, aspecto GO y condición de evidencia. |
| T | Conjunto preparado de términos de P en X bajo c y política de 03. |
| k | Número de términos únicos de T. |
| Anc_R(t) | Ancestros de t bajo relaciones R, incluyendo t cuando se indica con asterisco. |
| C, V | Unidades candidatas y unidades válidas/estimables de una agregación. |
| NA / null | Valor no disponible; nunca equivalente automático a cero. |

Estados de evidencia: VERIFICAT EN CODI = código leído, no ejecución; DOCUMENTAT NO VERIFICAT = documentación/antecedente, no verificación operacional; PROPOSTA = definición de este borrador; PENDENT = decisión sin resolver; NO ACCESSIBLE = recurso no consultado, no inexistencia. Los IDs/versions propuestos no son funciones o endpoints existentes.

## 2. Inventario y estado real de implementación

| Familia | Código o documento observado | Estado y diferencia con objetivo |
|---|---|---|
| MBL | G2 `GOOntology.minimal_branch_length`; ruta `goatools.semantic.min_branch_length` y fallback local | VERIFICAT EN CODI: método localizado. Definición delegada depende de versión; fallback diverge de la definición candidata (§4). |
| IC | G2 `prepare_term_counts`, `information_content`; U1 `TermCounts`, `get_info_content` | VERIFICAT EN CODI: delegación y estado. Base logarítmica efectiva del backend no demostrada solo por este wrapper. |
| Wang | G2 `semantic_similarity` rama wang y `_get_wang_ss`; U2/U3 `SsWang`, `DagA` | VERIFICAT EN CODI: rutas y defaults observados; no garantiza pesos/relaciones del entorno instalado. |
| Lin | G2 rama lin; U1 `lin_sim`, `lin_sim_calc`, `most_informative_common_ancestor` | VERIFICAT EN CODI para fuentes consultadas. La dependencia comparativa no es certificación de release instalada. |
| Medias proteicas internas | G2 ofrece `group_similarity` con BMA | El BMA existente no implementa la dispersión interna propuesta. Las medias de §3 son PROPOSTA. |
| Asociaciones A | Antecedente v1.1 en conversación y anexo 04a generado con esta entrega | PROPOSTA; motor NPMI no localizado en G2, sin afirmar ausencia en todo el repositorio. |
| Referencias | G5 esquema sin publicación; esquema aportado por usuario sí la incluye | Recuperación condicionada a resolver 03; no disponible por defecto por el nombre de columna. |

La revisión remota comenzó por README y árbol. `pyproject.toml` declara `goatools >=1.5.2,<2.0.0`, no una versión instalada exacta [G6]. Se intentó recuperar fuentes bajo una ruta `v1.5.2` y falló; se leyó la rama predeterminada de upstream mediante connector y se obtuvo la revisión del árbol. Esa lectura permite contraste, no afirmar qué versión ejecutaría BioData. Las tres fuentes upstream se identifican además por blob en §15 para auditar el contenido observado.

No se exige una refactorización global para redactar ni se adjudica al código un incumplimiento de protocolo aprobado: el paquete 01–04 sigue en borrador. Sí se registran divergencias que deben resolverse antes de aceptar cálculos.

## 3. Contrato común de dominio, pares y agregación

### 3.1. Inputs y resolución

El input es el conjunto preparado y sus soportes de 03, no la tabla raw sin política. Identidad, NOT, obsoletos, raíces, condiciones ALL/EXP, términos explícitos/propagados y pertenencia de referencia se resuelven allí. 04 recibe también los contadores de pérdidas previas para no ocultarlas.

La preparación principal propuesta en 03 usa términos explícitos únicos y excluye raíces de la lista puntuable. Los ancestros y raíces pueden intervenir internamente en las fórmulas. Una raíz en el detalle de ancestros no se añade automáticamente a T.

Pares entre aspectos diferentes no se puntúan con MBL, Wang o Lin en este experimento. Se desglosan MF, BP y CC y se utilizan A para coanotación entre aspectos. No se asigna una distancia artificial entre raíces ni se usa `branch_dist` para unir ontologías.

### 3.2. Pares internos admisibles

Para MBL, 1−Wang y 1−Lin:

\[
C_X(P,c)=\{\{t_i,t_j\}:t_i,t_j\in T_X(P,c),\ i<j\},
\qquad |C_X(P,c)|=k(k-1)/2.
\]

Se incluyen ancestro–descendiente y términos de ramas diferentes dentro del aspecto. Se excluyen diagonal, pares ordenados repetidos y duplicados por alias. La comparación de un término consigo mismo se define para tests de primitivas, pero no entra en la media proteica. No se reduce redundancia adicional dentro de 04; una política distinta de 03 genera otro input.

Sea V el subconjunto de C para el que la primitiva devuelve un resultado finito y válido bajo esta especificación. No basta que el wrapper produzca un float. Agregación principal propuesta:

\[
\bar d_X(P,c)=\frac{\sum_{\{a,b\}\in V_X(P,c)}d(a,b)}{|V_X(P,c)|}.
\]

Cada pareja pesa uno. No se pondera por evidencia, publicaciones, frecuencia ni profundidad adicional. Se retorna media disponible y cobertura |V|/|C|. Propuesta conservadora para estas tres familias: valor principal solo con cobertura completa; si es parcial, `value=null`, `available_mean` conserva el diagnóstico y `status=PARTIAL_COVERAGE`. No se elimina un término no cubierto para mejorar el denominador de Lin. Este criterio no sustituye el umbral propio de A en 04a.

Si k=0 o 1: sin parejas, media y cobertura null, `INSUFFICIENT_TERMS`. Si k=2: una pareja; valor principal igual a su resultado si válida. Una duplicación de la misma anotación no transforma k=1 en k=2.

### 3.3. IC y descriptores

IC medio se agrega por términos, no por pares. Sus candidatos son todos los términos preparados y válidos de T, incluidos los no cubiertos por el perfil para el denominador de cobertura. §5 define la regla. Los conteos y proporciones tienen dominio y ausencia propios (§9), no heredan mecánicamente el mínimo de dos términos.

Máximos/mínimos y pares extremos podrán devolverse como explicación, sin sustituir la media principal. Un extremo más elevado por disponer de más parejas no prueba más diversidad biológica. Desempates explicativos: GO ID canónico lexicográfico, después del valor, para evitar dependencia del orden de entrada.

### 3.4. Versionado de cálculo

Cada ID debe separar fórmula/agregación de parámetros y perfil efectivo. Cambiar fórmula, dominio, tratamiento de cero o cobertura principal exige nueva versión de métrica. Cambiar referencia produce nuevo profile_id y configuración; cambiar relaciones/pesos produce otro recurso semántico/versionado aunque no cambie el nombre de familia. No usar el mismo metric_version para un fallback distinto sin advertir la variante.

## 4. Ficha MBL clásica identificada en el proyecto

### 4.1. Identificación y pregunta

| Campo | Especificación |
|---|---|
| ID/versión propuesta | `go_mbl_depth_dca_mean` / `0.1.0` |
| Nombre operativo | MBL por diferencias de profundidad al ancestro común más profundo; no camino mínimo por defecto. |
| Pregunta | ¿Qué separación estructural resume esta variante de MBL dentro de un aspecto? |
| Naturaleza | Descriptor estructural de pares y media; no se afirma distancia métrica formal. |
| Recursos/unidad | OBO fijado y DAG is_a, sin IC; pareja de términos y proteína/aspecto. |
| Dominio | Términos activos resueltos del mismo aspecto y con ancestro común admisible. |

El nombre «Minimum Branch Length» está documentado en el contexto del proyecto, pero el significado normativo se fija por la función encontrada y la fórmula siguiente. No se extrapola a cualquier medida llamada MBL en otros trabajos.

### 4.2. Fórmula candidata identificada en la delegación

Sea h(t) la profundidad máxima desde la raíz siguiendo `is_a`; h(raíz)=0. Sea H(a,b)=Anc_is_a*(a) ∩ Anc_is_a*(b), con ambos términos incluidos en su propio cierre. Para H no vacío:

\[
h^*(a,b)=\max_{u\in H(a,b)}h(u),
\qquad d_{MBL}(a,b)=h(a)+h(b)-2h^*(a,b).
\]

Si hay varios ancestros de profundidad máxima, el valor es el mismo; para explicar se devolverá un GO ID con desempate lexicográfico declarado o el conjunto de empates. No usar el ancestro con más IC: eso es otra medida.

No hay normalización adicional, ponderación por relación ni división por profundidad máxima. En un árbol esta fórmula coincide con longitud de camino entre términos; en un DAG con múltiples caminos no tiene por qué coincidir con el camino ascendente más corto. U1 diferencia explícitamente `min_branch_length` de `shortest_path`. No sustituir una por otra silenciosamente.

Relaciones: variante identificada usa parentesco `is_a` y `depth`; no incluye automáticamente `part_of` ni todas las relaciones del OBO. Configurar otras relaciones sería una nueva variante, no la misma MBL clásica.

### 4.3. Implementación leída y divergencia

G2 llama a `goatools.semantic.min_branch_length` si existe. U1 observa la fórmula de profundidad/DCA anterior; el entorno real queda pendiente de versión/verificación.

El fallback local de G2 no usa el cierre común correcto. Define:

\[
H_{fallback}=(Anc(a)\cap Anc(b))\cup\{a,b\},
\quad h_f=\max_{u\in H_{fallback}}h(u),
\quad d_f=h(a)+h(b)-2h_f.
\]

Los extremos a y b se incorporan aunque no sean ancestros comunes. En ramas distintas y profundidades diferentes esa expresión puede ser negativa. Esta es una consecuencia algebraica del código leído, no un test ejecutado. No se acepta ese fallback como implementación de la ficha; si es la ruta disponible, se bloquea MBL hasta verificación/corrección versionada o se emite solo diagnóstico de implementación, no valor científico.

G3 incluye expectativas de 1 y 3 en dos pares de un árbol pequeño, pero no demuestra que la ruta fallback pase esos tests. No se declara ninguna ejecución.

### 4.4. Agregación, escala, cobertura y límites

Media por §3, pares únicos sin diagonal y sin peso. Escala entera no negativa por pareja válida, media real ≥0; mayor valor representa más separación según esta variante. Sin cota universal independiente del grafo. Devuelve valor, disponible, estados y par más separado.

Término idéntico: primitiva 0. Ancestro–descendiente: diferencia de profundidades, no necesariamente número mínimo de aristas en DAG. Raíz como extremo: h(t), en test; no entra como término puntuable principal por 03. Sin ancestro admisible: `NO_COMMON_ANCESTOR`; distinto aspecto: `CROSS_ASPECT`; término no resuelto: `UNRESOLVED_TERM`; obsoleto sin resolver: no puntuable; negativo o no finito: `INVALID_OUTPUT`, no truncar a cero.

Coste previsto: preparación del DAG y ancestros; por pareja, intersección de ancestros y búsqueda de profundidad máxima. Con caché de ancestros, coste proporcional a tamaños de cierres; por proteína, cuadrático en k para enumerar pares. No hay benchmark medido.

Ejemplo abstracto: árbol R→A→U y R→B, profundidades 0,1,2,1. d(U,A)=1, d(U,B)=3, d(A,B)=2. Para T={U,A,B}, media=2. El fallback local para U,B produciría -1 por la expresión leída, por lo que debe rechazarse. No es predicción de un experimento real.

Limitación: separación de ramas o profundidad no demuestra funciones independientes ni rigor bibliográfico; en DAG no es sinónimo de shortest path.

## 5. Ficha IC por término y media proteica

| Campo | Especificación |
|---|---|
| IDs/versiones propuestas | Primitiva `go_term_ic` / `0.1.0`; agregado `go_ic_mean` / `0.1.0` |
| Pregunta | ¿Qué especificidad estadística tienen los términos de la proteína respecto de una referencia? |
| Naturaleza | Descriptor informativo; no similitud ni medida de calidad. |
| Unidad | Término; agregado por proteína/aspecto. |
| Inputs | Perfil IC de 03, conteos por entidad reconciliada, universo por aspecto, cierre de referencia, OBO y condición de query. |
| Dominio | Término canónico del aspecto con conteo positivo y denominador válido. |

### 5.1. Fórmula y parámetros

Sea R_X el universo de referencia con anotación elegible en X según 03; N_X=|R_X|. Sea n_X(t) el número de entidades distintas cuyo conjunto de referencia, después del cierre autorizado, contiene t. Entonces:

\[
p_X(t)=n_X(t)/N_X,\qquad IC_X(t)=-\ln p_X(t),\quad 0<p_X(t)\leq1.
\]

Base propuesta: logaritmo natural, unidad nats. No se añaden pseudoconteos ni epsilon. Una base diferente requiere declarar la variante; no comparar IC medios de bases o perfiles distintos como valores intercambiables.

La propagación se define en 03 y se identifica en profile_id. Para una jerarquía coherente y cierre completo, n(ancestro)≥n(descendiente). Si la raíz cubre todo el universo de aspecto, IC(raíz)=0. La raíz se excluye como término puntuable principal, pero permanece en el perfil y en ancestros compartidos. Un término no raíz observado en todas las entidades también tiene IC=0: cero no significa ausencia del perfil.

N=0: `EMPTY_REFERENCE`. n=0 o término no contado: `UNCOVERED_TERM`, valor null, nunca infinito ni cero imputado. n>N o conteos incompatibles: `INVALID_PROFILE`. Un término activo del OBO no es automáticamente cubierto por la referencia.

### 5.2. Backend frente a contrato

G2 construye `TermCounts` tras filtrar IDs y delega en `get_info_content`; U1 observado cuenta conjuntos de genes/productos, propaga ancestros y usa conteos de raíces por aspecto como denominador de `get_term_freq`. Esto es compatible en intención con la unidad propuesta si cada key representa una entidad única y el cierre alcanza la raíz, pero no lo demuestra para la dependencia instalada.

En U1 `get_info_content` obtiene `tinfo` de un subDAG y puede devolver cero si no hay entrada. No se ha leído aquí toda la construcción de tinfo para acreditar su base exacta en la versión instalada. Por tanto, el adaptador debe verificar conteos, cobertura y base antes de aceptar el float de la API. G2 `_as_float` también transforma algunas ausencias en cero. No basta aplicar una prueba IC>=0.

### 5.3. Agregación proteica

C=T, V=términos de T con IC válido. Media disponible:

\[
\overline{IC}_{available}(P,X,c)=\frac{1}{|V|}\sum_{t\in V} IC_X(t).
\]

Cobertura |V|/k si k>0. Propuesta principal: exigir cobertura completa; de lo contrario `value=null`, `available_mean` diagnóstico y estado parcial/no cubierto. Sin términos, null y `INSUFFICIENT_TERMS`. Con uno válido, media=su IC. Con dos, media aritmética de ambos. Cada término pesa uno aunque tenga muchos soportes. No calcular IC medio por parejas ni por filas.

Outputs: valor, perfil, n/N por término en detalle, número candidato/válido, cobertura y motivos. Mayor valor implica rareza/especificidad relativa en ese corpus, no mejor evidencia. Escala ≥0, sin cota universal entre corpus; con conteos enteros positivos y N fijo, máximo ln N.

Coste: construir cierres de referencia y conteos; consulta de un término aproximadamente acceso a perfil; agregado O(k). No estimación de tiempos ni memoria garantizada.

Ejemplo sintético: N=4, n(A)=2 y n(U)=1: IC(A)=ln2, IC(U)=ln4; media de {A,U}=1.5 ln2. Raíz con n=4 produce 0; término sin observaciones produce null. Pruebas completas en §12.

## 6. Ficha 1−Wang

| Campo | Especificación |
|---|---|
| ID/versión propuesta | `go_wang_dissimilarity_mean` / `0.1.0` |
| Pregunta | ¿Cuánta estructura semántica ancestral dejan de compartir los términos de una proteína? |
| Naturaleza | Dissimilaridad derivada de similitud; no distancia métrica formal afirmada. |
| Inputs/unidad | Grafo, relaciones y pesos identificados; pareja del mismo aspecto y agregado proteico. No corpus de frecuencias como dependencia conceptual. |
| Dominio | Términos canónicos resueltos, mismo aspecto, grafo y parámetros compatibles. |

### 6.1. Definición

Para un término a, D_a contiene a y sus ancestros bajo las relaciones autorizadas. Cada arista padre u→hijo v tiene peso w(u,v), con 0<w<1. Definir:

\[
S_a(a)=1,\qquad
S_a(u)=\max_{(u,v)\in E(D_a)}\{w(u,v)S_a(v)\}\quad(u\ne a).
\]

La recurrencia se aplica solo a los hijos del subgrafo que conducen a a; si hay varios caminos se toma máxima contribución, no suma de rutas. Sea:

\[
SV(a)=\sum_{u\in D_a}S_a(u),
\quad W(a,b)=\frac{\sum_{u\in D_a\cap D_b}(S_a(u)+S_b(u))}{SV(a)+SV(b)},
\quad d_W(a,b)=1-W(a,b).
\]

El artículo primario P1 y U2/U3 sustentan la formulación; no validan este experimento ni sus agregados por proteína.

### 6.2. Relaciones y pesos: disponibles versus propuestos

G2 `_get_wang_ss` construye `SsWang(self.go_ids, self._dag)` sin pasar relaciones ni pesos. En U2 consultado, `relationships=None` activa solo `is_a`; su peso predeterminado es 0.8. Que el diccionario upstream también contenga 0.6 para `part_of` y regulación no significa que estas relaciones estén activas.

Propuesta principal compatible con la ruta localizada: variante explícita `is_a_only`, w_is_a=0.8, condicionada a comprobar versión y ruta efectiva. Extensión opcional `is_a_part_of`: w_is_a=0.8, w_part_of=0.6, con relaciones cargadas y backend configurado explícitamente. No activar regulates por defecto ni afirmar que la API CBBIO actual expone esa configuración. P1 presenta esos factores, pero el estado real de la carga y cálculo se verifica en 05/07.

La ruta alternativa de G2 busca `semantic.wang_sim` y puede intentar una firma con conteos tras TypeError. Esa compatibilidad no cambia el objetivo conceptual, pero exige registrar implementación/ruta; no aceptar un algoritmo distinto por compartir nombre.

### 6.3. Agregación y casos

Media por §3, todos los pares únicos i<j de mismo aspecto, sin diagonal, pesos uno a nivel de pareja. Los pesos de arista pertenecen a la primitiva; no multiplicar después por profundidad o evidencia.

Escala propuesta [0,1], simétrica y W(a,a)=1, d_W(a,a)=0. No se afirma desigualdad triangular ni otras propiedades de distancia formal. Diferentes términos pueden tener valores cercanos; no fijar corte de función independiente.

Una raíz activa tiene SV=1 y permite cálculo primitivo; no es query principal. Con disyunción de ancestros y términos válidos en un grafo declarado desconectado, numerador vacío da W=0 y d=1, reportando `DISCONNECTED_GRAPH` como advertencia. Si la desconexión contradice el recurso esperado, es error de integridad, no máxima divergencia aceptada sin revisión. Comparación cross-aspect no se admite aunque un backend devuelva cero.

Cero denominador no puede ocurrir con S_a(a)=S_b(b)=1 y pesos válidos; si aparece: `INVALID_GRAPH_OR_IMPLEMENTATION`. Término ausente/obsoleto no resuelto: estado no estimable, no d=1. Cobertura completa para principal según §3; nulos no se convierten en dissimilaridad máxima.

Outputs: valor/agregado, cobertura, relaciones, pesos, versión y ruta backend, parejas explicativas. Coste: preparación de subgrafos ancestrales y contribuciones por término; por pareja, intersección y suma de cierres; O(k²) parejas, con cachés dependientes de grafo y pesos. El código actual prepara todos `go_ids` en una ruta: no se promete coste limitado solo a términos consultados.

Ejemplo mínimo: R→A y R→B con w=0.8; SV(A)=SV(B)=1.8, W(A,B)=1.6/3.6=4/9, d=5/9. Con relación `part_of` alternativa de peso 0.6 la contribución cambia solo si esa arista está activa. No es resultado ejecutado.

Limitación: depende de representación del grafo y pesos; una relación etiquetada no se usa porque exista en el OBO, sino porque esté incluida y recorrida en la variante efectiva.

## 7. Ficha 1−Lin

| Campo | Especificación |
|---|---|
| ID/versión propuesta | `go_lin_dissimilarity_mean` / `0.1.0` |
| Pregunta | ¿Qué proporción de información de los términos no queda recogida en la información ancestral compartida? |
| Naturaleza | Dissimilaridad informativa derivada; no distancia métrica formal afirmada. |
| Inputs | Perfil IC aceptado de §5/03, OBO y relaciones para ancestros compatibles con ese perfil. |
| Unidad/dominio | Pareja mismo aspecto, términos y ancestros con cobertura válida; media proteica. |

### 7.1. Fórmula y selección MICA

Para H(a,b)=Anc_R*(a)∩Anc_R*(b), sea MICA cualquier ancestro admisible de mayor IC:

\[
IC_{shared}(a,b)=\max_{u\in H(a,b)}IC(u),
\quad L(a,b)=\frac{2IC_{shared}(a,b)}{IC(a)+IC(b)},
\quad d_L(a,b)=1-L(a,b).
\]

Se incluyen extremos en su propio cierre. Se exige que H no sea vacío y que el perfil sea válido para los candidatos. Ancestros con conteo cero cuando ambos descendientes están cubiertos indican incoherencia del cierre/perfil, no una oportunidad para escoger otro ancestro por conveniencia. Empates de IC no cambian valor; desempate explicativo lexicográfico sobre candidatos empatados.

Propuesta principal para la relación ancestral de Lin: `is_a`, consistente con la consulta de common parents observada en U1; otras relaciones requieren otra variante explícita. El perfil puede contar con cierre más amplio si lo declara 03, pero no se confunde el cierre de conteo con el conjunto de ancestros entre los que se selecciona MICA.

DCA y MICA no son intercambiables. En U1 consultado la selección MICA maximiza IC, después profundidad y GO ID para desempates. Eso no permite asumir que toda versión admitida por pyproject haga lo mismo. G2 delega sin especificar variante ni exponer el ancestro elegido.

### 7.2. Cero, ausencia y validez

Propuesta matemática principal:

- Si IC(a)+IC(b)>0 y ambos términos cubiertos: aplicar fórmula, incluso si uno tiene IC cero. Con perfil coherente, su información compartida es cero y L=0.
- Si IC(a)=IC(b)=0: `ZERO_IC_DENOMINATOR`, null. No imponer similitud 1 por identidad ni 0 por defecto en esta variante.
- Si a=b e IC(a)>0: L=1 y d=0; test de primitiva, fuera de media interna.
- Raíz frente a término de IC>0: L=0 y d=1 en test; raíz no query principal.
- Ausencia de término o cobertura: null, no asumir IC=0.
- Sin ancestro admisible: `NO_COMMON_ANCESTOR`, no L=0 imputado.
- IC compartido superior al de un extremo o valores fuera de [0,1] más allá de tolerancia: `INVALID_PROFILE_OR_OUTPUT`.

U1 `lin_sim_calc` introduce convenciones específicas: exige IC de ambos no cero para su rama de fórmula, devuelve 1 para identidad con cero y 0 en ciertos casos de información compartida cero. La propuesta para denominador nulo es distinta deliberadamente. G2 `_as_float` puede transformar un None en 0, ocultando el problema. El adaptador debe detectar esos casos antes de la llamada o validar con perfil explícito; no reinterpretar el float como evidencia suficiente. Esta divergencia exige aprobación y versión, no se presenta como conducta existente.

### 7.3. Agregación, escala, coste y ejemplo

Media por §3; pares únicos mismo aspecto, sin diagonal ni pesos por evidencia. Escala [0,1] con IC coherente y denominador positivo; mayor valor, menos información compartida proporcional. Un d=0 entre términos distintos es posible con frecuencias/IC iguales, por lo que no implica identidad conceptual.

Outputs: value/available_mean, perfil IC, cobertura, estados, pareja extrema y MICA/IC de extremos en detalle explicativo. Coste: perfil IC previamente construido; intersección de ancestros y máximo por pareja, más O(k²) enumeración. No benchmark medido.

Ejemplo: IC(A)=ln2, IC(U)=ln4, MICA(U,A)=A. L=2/3, d=1/3. Dos ramas cuya única información compartida sea raíz IC=0 producen L=0, d=1 si los extremos están cubiertos y denominador positivo.

Limitación: resultado corpus-dependiente, no prueba de autonomía funcional; no comparar variantes con perfiles distintos como si fueran la misma medición.

## 8. Asociaciones interaspecto y fuente normativa única

Se recupera el contenido textual de v1.1 desde el historial accesible de esta conversación, no un archivo físico previo ni una versión aprobada en GitHub. Se reutiliza su núcleo en el anexo entregado [04a_asociaciones_interaspecto.md](04a_asociaciones_interaspecto.md), que declara procedencia, diferencias editoriales y límites. No se afirma preservación byte a byte del archivo descargable original.

| ID propuesto | Versión del núcleo | Naturaleza/unidad | Pregunta y fuente normativa |
|---|---|---|---|
| `go_assoc_mf_bp` | `go-cross-aspect-npmi@1.0.0` | Asociación; pareja MF–BP y proteína | Habitualidad de coanotaciones actividad–proceso; 04a §§3–8. |
| `go_assoc_mf_cc` | Misma | Asociación; pareja MF–CC y proteína | Habitualidad actividad–componente; 04a §§3–8. |
| `go_assoc_bp_cc` | Misma | Asociación; pareja BP–CC y proteína | Habitualidad proceso–componente; 04a §§3–8. |

Las fichas completas, fórmulas, universo dual, marginales, normalización, direccionalidad simétrica, soporte, agregación y ejemplos numéricos están únicamente en 04a. El perfil efectivo lo gobierna 03; la invariancia durante perturbaciones, 02. Aquí solo se establece su pertenencia al catálogo y correspondencia de salida (§11).

No se usa 1−A como otra métrica ni se suman las tres asociaciones. El soporte escaso y la ausencia de coocurrencia tienen estados propios en el anexo; la simetría estadística no implica causalidad o actividad en un lugar concreto. El artículo de Bouma define NPMI y una convención de −1 para cero; el contrato aplicado del anexo opta por no puntuar cero como decisión explícita del proyecto, no como obligación de la definición original [P3].

## 9. Fichas de descriptores de evidencia, términos y cobertura

Versiones propuestas de todos los descriptores: `0.1.0`. Son conteos/proporciones operacionales, no scores de certeza. Inputs son tablas preparadas, raw y enlaces de 03, bajo condiciones de 02. No se afirma que existan funciones equivalentes verificadas en BioData. Duplicados de entidad y alias se resuelven en 03; no se pondera por artículos ni tipo de evidencia salvo para el indicador que explícitamente lo cuenta.

### 9.1. Catálogo y fórmulas

| ID | Unidad/dominio | Definición completa y denominador | Dirección/escala y ausencia |
|---|---|---|---|
| `go_annotation_rows_count` | Proteína/aspecto/condición, bruto observable | Número de filas raw que pasan condición antes de deduplicación de términos; duplicados raw se conservan identificados. Sin denominador. | Entero ≥0; 0 solo si extracción completa no encuentra filas; extracción desconocida→null. |
| `go_terms_asserted_unique_count` | Proteína/aspecto/condición | Cardinalidad de términos canónicos explícitos únicos después de reglas de 03; raíces excluidas si política principal. | Entero ≥0; no informa por sí solo diversidad independiente. |
| `go_terms_propagated_only_count` | Misma | Cardinalidad de términos derivados por cierre que no están en el conjunto explícito seleccionado; política y relaciones identificadas. | Sin cierre solicitado: NOT_APPLICABLE, no confundir con cero derivado de cierre realizado. |
| `go_terms_unique_count` | Conjunto puntuable | Cardinalidad del conjunto final único de la representación seleccionada. No suma dos veces un término explicit+derived. | Entero ≥0; ámbito de representación obligatorio. |
| `go_evidence_rows_count` | Proteína/aspecto/código | Número de filas admisibles con ese código en el bruto disponible. | No número de experimentos independientes; grado de completitud de ingesta indicado. |
| `go_evidence_codes_count` | Proteína/aspecto | Número de códigos distintos observados entre soportes admisibles. | Entero ≥0; no jerarquía de rigor. |
| `go_reference_ids_unique_count` | Proteína/ámbito GO | Número de pares namespace+ID normalizado distintos vinculados a anotaciones admisibles. | Alias de un artículo pueden ser varios IDs; no llamar papers a este conteo. |
| `go_publications_unique_count` | Proteína/ámbito GO | Número de identidades bibliográficas reconciliadas de tipo publicación; aliases validados cuentan una vez. | Unknown no crea publicación ficticia; indicar cobertura de reconciliación. |
| `mfp_publications_unique_count` | Proteína/ámbito claim MFP | Igual sobre enlaces de claims, no anotaciones GO. | No mezclar con anterior sin unión explícita e identificación de procedencia. |
| `go_experimental_term_fraction` | Proteína/aspecto; ALL completo observable | Número de términos explícitos únicos ALL con al menos un soporte EXP-convencional, dividido por número de términos explícitos únicos ALL de ese aspecto. | [0,1]; denominador cero→null; no ratio de filas. |
| `go_experimental_extended_term_fraction` | Misma | Igual usando lista EXP-ampliada de 02. | [0,1]; mismos requisitos. |
| `go_term_retention_fraction` | Proteína/aspecto/condición vs ALL | Número de términos explícitos de condición divididos por términos explícitos ALL; comprobar subconjunto. | [0,1]; ALL vacío→null; no interpretarlo como pérdida de biología. |
| `go_reference_link_coverage` | Proteína/aspecto/condición | Filas de anotación admisibles con al menos una referencia de cualquier namespace normalizada, dividido por filas admisibles observadas. | [0,1]; no «fracción de papers revisados»; denominador cero→null. |
| `go_publication_resolution_fraction` | Proteína/ámbito | Grupos de referencia cuyo destino publicación está reconciliado, dividido por grupos que el parser clasifica como candidatos a publicación. | No inferible si parser no sabe delimitar grupos; entonces null. No castigar GO_REF como publicación fallida. |
| `go_metric_unit_coverage` | Proteína/métrica | Unidades válidas dividido por candidatas; para IC términos, para MBL/Wang/Lin pares, para A según anexo. | Candidatas=0→null; válidas=0 con candidatas>0→0; no reemplaza value. |

Las condiciones experimentales se aplican antes de producir términos explícitos; los ancestros propagados no reciben códigos experimentales inventados. Para proporciones experimentales se usa soporte de términos explícitos, no el cierre. Conteos de publicaciones GO y MFP permanecen separados aunque puedan enlazar al mismo artículo.

### 9.2. Campos comunes de las fichas de descriptores

Pregunta: cantidad, tipo, retención o cobertura de evidencia registrada. Naturaleza: descriptor, nunca similitud. Recursos: snapshot, condición y política de 03; sin perfil IC salvo que se informe cobertura de ese perfil. Agregación proteica: conteo de conjunto/filas o cociente indicado, sin media sobre parejas adicional. Ponderación: ninguna. Tratamiento de duplicados: distinguir filas originales, IDs distintos y artículos reconciliados como la tabla exige.

Outputs: valor, numerador, denominador nullable para conteos, unidad, scope, condición, status/reason y procedencia. Coste: recorridos de filas y construcción de conjuntos, lineal esperado en tamaño de entrada con estructuras hash; no benchmark ni garantía de memoria.

Limitaciones: mayor cantidad puede reflejar curación, organism bias o repetición documental; una referencia no demuestra lectura ni independencia experimental. Esquema antiguo con una fila por proteína–GO puede subrepresentar códigos y soportes: describir «filas registradas», no «toda evidencia».

Ejemplo sintético: dos términos explícitos X,Y; X tiene dos filas y dos IDs que son alias del mismo artículo, uno de sus soportes convencional; Y tiene una fila de otro código y sin referencia. Filas=3, términos=2, IDs de referencia=2, publicaciones reconciliadas=1, fracción experimental de términos=1/2, cobertura de enlace por filas depende de cuáles tengan enlace: si dos filas lo tienen, 2/3. Son cantidades distintas por definición.

Pruebas esperadas: duplicar una referencia alias no altera publications_unique; añadir soporte del mismo término no altera terms_unique; sin ALL no hay proporción; sin columna bibliográfica no reportar 0 publicaciones como ausencia observada. No se ejecutan aquí.

## 10. Estados, ausencia y estabilidad numérica

### 10.1. Orden y preservación

La capa de resultados no debe convertir errores de backend en ausencia biológica. Precedencia propuesta: recurso/implementación no aceptado; integridad; identidad/GO no resuelto; dominio/aspecto; insuficiencia de unidades; perfil/cobertura; cálculo matemático; validación numérica; agregación.

| Status o reason | Uso |
|---|---|
| `NOT_IMPLEMENTED_OR_ACCEPTED` | No hay ruta validada para el contrato; no emitir score científico. |
| `INVALID_RESOURCE` / `INVALID_PROFILE` | Incompatibilidad o conteos inválidos. |
| `UNRESOLVED_TERM` / `CROSS_ASPECT` | Input sin resolución o fuera de dominio. |
| `INSUFFICIENT_TERMS` | Cero/uno para pares, cero para IC agregado. |
| `UNCOVERED_TERM` / `NO_COMMON_ANCESTOR` | Falta soporte informativo o ancestro admisible. |
| `ZERO_IC_DENOMINATOR` | Lin sin información total positiva. |
| `PARTIAL_COVERAGE` / `NO_VALID_UNITS` | Valor principal ausente; detalle de unidades disponible cuando existe. |
| `INVALID_OUTPUT` / `ERROR` | Resultado imposible o error operativo, no cero. |
| `NOT_APPLICABLE` | Operación no definida para esa configuración, por ejemplo cierre no solicitado. |
| `OK` | Cumplimiento técnico del contrato, no validación biológica. |

Los nombres específicos A se conservan en 04a; el esquema largo admitirá status principal y reason específico. Un valor cero con status OK significa cero calculado conforme a definición; null significa ausencia explícita.

### 10.2. Política numérica propuesta

Usar doble precisión y orden de suma estable. Propuesta de tolerancia de tests: absoluta 1e−12 y relativa 1e−9 para floats; conteos y MBL entera exactos. Ratificar por 07. No añadir epsilon al denominador para resolver casos no definidos.

Si una similitud sale fuera de [0,1] más allá de tolerancia: error. Para desbordamientos minúsculos de redondeo puede normalizarse al borde únicamente bajo regla versionada, conservando valor bruto y ajuste. Nunca corregir grandes valores, negativos MBL o falta de cobertura con clipping.

## 11. Esquema largo de resultados propuesto

Una fila por proteína, métrica, versión, condición, aspecto o par, representación, perfil y perturbación. `protein_id` en esta salida significa entity_id canónico de 03; `biodata_protein_id` se conserva por separado con ámbito local. No inferir equivalencia de strings.

| Campo | Tipo/nulo | Regla |
|---|---|---|
| `run_id` | string NN | Ejecución real cuando exista, no ID inventado aquí. |
| `protein_id` | string NN | Entidad reconciliada de 03. |
| `biodata_protein_id`, `database_scope` | string nullable | Enlace local si disponible; no PK global. |
| `metric_id`, `metric_version` | string NN | ID de cálculo y definición. |
| `condition_id`, `term_policy_id` | string NN | Selección/representación efectivas. |
| `aspect`, `aspect_x`, `aspect_y` | enum nullable | Un aspecto para intraaspecto; par para A; exactamente el ámbito apropiado. |
| `profile_id` | string nullable | Estadístico IC/A; null legítimo para MBL/Wang sin frecuencias. |
| `ontology_id`, `semantic_resource_id` | string nullable según métrica | Grafo y relaciones/pesos/ruta identificables. |
| `perturbation_id`, `replicate_id` | string nullable | Baseline null; identifican intervención, no otra entidad biológica. |
| `value` | float64 nullable | Resultado principal; exportación puede rotular «valor», sin crear una segunda medida. |
| `available_mean` | float64 nullable | Diagnóstico sobre unidades válidas, no sustituto silencioso. |
| `status` | enum NN | Estado técnico principal. |
| `reason_code`, `reason_detail` | string nullable | Motivo preciso de ausencia/error o limitación. |
| `n_terms_input`, `n_terms_selected` | integer ≥0 nullable | Antes de preparación según 03 y conjunto T, distinguidos. |
| `n_terms_x`, `n_terms_y` | integer ≥0 nullable | Para asociaciones. |
| `unit_kind` | enum NN | term/pair/row/reference/proportion. |
| `n_candidate_units`, `n_valid_units` | integer ≥0 nullable | Denominador y numerador de cobertura; no ficción para indicadores sin ese concepto. |
| `n_invalid_units_by_reason` | map/JSON nullable | Conteo mutuamente excluyente por razón primaria; suma reconcilia candidatos. |
| `coverage` | float64 nullable | Según unidad; candidatas cero→null. |
| `numerator`, `denominator` | integer nullable | Para proporciones definidas; no para IC ni MBL. |
| `backend_id`, `backend_version`, `implementation_route` | string nullable | No dar por comprobada la instalada por pyproject. |
| `input_fingerprint`, `config_id` | string NN en ejecución aceptada | Identidad real de inputs y parámetros. |
| `explanation_ref`, `warnings` | string/array nullable | Enlace a detalle de términos/parejas y limitaciones. |

Los contadores anteriores no sustituyen informe de pérdidas raw. El detalle de pareja/termo conserva term IDs, valor, status, perfil y explicación de ancestros cuando procede. `association_available` del anexo se mapea a `available_mean` sin cambiar el cálculo; estados y contadores A se preservan.

No se obliga a que todos los contadores estén poblados en todas las métricas. La PK física y schemas serán implementados en 05/07; `schemas/` y `templates/run_manifest.json` son artefactos a crear, no existentes verificados.

## 12. Ejemplos sintéticos y pruebas esperadas

Todas las letras R,A,B,U,V representan nodos abstractos; no GO ID reales ni cohortes del estudio. Las deducciones siguientes no se han comprobado ejecutando código. 07 las convertirá en pruebas. Las condiciones de datos se resuelven primero por 03.

### 12.1. Árbol y referencia abstractos

Grafo is_a: R raíz; A y B hijos de R; U hijo de A. Profundidades 0,1,1,2. Referencia abstracta de cuatro entidades con conjuntos explícitos {U}, {A}, {B}, {B}. Cierre is_a incluye ancestros una vez por entidad. Conteos R=4,A=2,U=1,B=2.

| Prueba | Deducción esperada |
|---|---|
| MBL(U,A) / MBL(U,B) / MBL(A,B) | 1 / 3 / 2 para DCA por profundidad. |
| Media MBL de {U,A,B} | (1+3+2)/3=2, diagonal excluida. |
| Fallback local para U,B | La expresión de G2 da −1; se debe rechazar como INVALID_OUTPUT o bloquear ruta. |
| IC(R), IC(A), IC(U), IC(B) | 0, ln2, ln4, ln2 bajo la definición propuesta. |
| Media IC de {A,U} | (ln2+ln4)/2=1.5 ln2; dos unidades término, no una pareja. |
| Lin(U,A) y 1−Lin | 2/3 y 1/3. |
| Lin(U,B) y 1−Lin | 0 y 1; extremos cubiertos, MICA raíz. |
| Wang(A,B), is_a 0.8 | 4/9; dissimilaridad 5/9. |
| Wang(U,A), is_a 0.8 | (0.8+1+0.64+0.8)/(2.44+1.8)=81/106; dissimilaridad 25/106. |

### 12.2. DAG con camino corto y largo

Añadir una arista directa R→U, conservando R→A→U. h(U)=2 por el camino largo. MBL_depth(U,R)=2 aunque la arista directa da camino mínimo ascendente de longitud 1. Esto demuestra por definición que no se debe etiquetar la variante como BFS shortest path en un DAG.

Añadir V hijo de A y de B sirve para comprobar que no se reduce a árbol y que los cierres no duplican el ancestro R. Para Wang se toma máximo de contribuciones de rutas, no suma que podría inflar SV.

### 12.3. Casos de dominio obligatorios

| Caso | Resultado esperado |
|---|---|
| T vacío | Medias internas y media IC null; conteo de términos 0 si extracción completa. |
| T={A} | Medias por pares null; IC medio ln2. |
| T={A,A} por filas duplicadas | Conjunto único {A}; no pareja válida creada. |
| T={A,B} | Una pareja; denominador 1. |
| Primitiva a=a con IC>0 | MBL=0, dW=0, dL=0; diagonal fuera de agregado. |
| Primitiva a=a con IC=0 | MBL/dW definidos; Lin ZERO_IC_DENOMINATOR bajo propuesta, distinto de algunas convenciones de backend. |
| Término raíz explícito | Se excluye por política principal de 03, se cuenta la pérdida; raíz sigue en ancestros. |
| IC no raíz=0 | Cubierto si n=N; válido para IC, no «missing». Lin depende del denominador total. |
| Dos extremos distintos con IC=0 | Lin null; no forzar d=1 ni 0. |
| Un extremo IC=0 y otro positivo | Con perfil coherente, Lin=0 y d=1. |
| Término fuera del perfil IC pero válido en GO | IC/Lin sin cobertura; MBL/Wang pueden seguir calculables. |
| Sin ancestro común | MBL/Lin no estimables; Wang depende de grafo desconectado válido y advertencia de §6. |
| Pares entre MF y BP | Rechazados para MBL/Wang/Lin; no se usan ceros de backend. |
| ID obsoleto/alias | Resolver en 03; nunca tratar dos alias de un término como dos funciones. |
| Cobertura IC parcial en {A,U,Z} con Z no cubierto | Candidatos=3, válidos=2, coverage=2/3, available_mean definido, value null. |
| Lin en {A,U,Z} con Z no cubierto | Tres pares candidatos, solo A–U válido, coverage=1/3, value null. |

### 12.4. MICA no necesariamente DCA

Construir dos ancestros comunes C y D con h(C)>h(D) pero IC(C)<IC(D), respetando monotonía en las rutas. Lin debe usar D para el valor compartido; MBL usa la mayor profundidad C. Con los mismos inputs, versiones de backend que seleccionan ancestro por profundidad en Lin no son equivalentes a esta definición y requieren otro ID/versión.

### 12.5. Invariantes transversales

Permutar filas o términos no altera resultados; duplicar una anotación no modifica conjuntos o conteos por entidad; incorporar referencia alias no aumenta artículos; cambiar condición no reconstruye F0; valores y estatus individuales equivalen al batch; invalidar caché al cambiar perfil/GO/pesos. Los resultados flotantes se comparan con tolerancia aprobada y las PK/conteos de inputs exactamente. Ninguna de estas pruebas se declara ejecutada.

Los ejemplos numéricos NPMI y reglas específicas de rareza están en 04a, para no duplicar fuente normativa.

## 13. Disponibilidad para primera entrega y coste

| Cálculo | Puede formar parte del hito de 01/02 | Condición pendiente antes de aceptarlo |
|---|---|---|
| Conteos/coverage básicos | Sí, candidatos prioritarios | Observabilidad y contratos 03; no contar nulos como cero. |
| MBL_depth | Sí, condicional | Versión de ruta delegada y prueba de profundidad/DCA; fallback local no aceptado sin resolución. |
| IC medio | Sí, condicional | Perfil, base ln, denominador y guardas de cobertura. |
| 1−Wang medio | Sí, condicional | Ruta efectiva, is_a y peso explícito; no suponer part_of activado. |
| 1−Lin medio | Sí, condicional | MICA, perfil IC, política de ceros y agregación. |
| A de 04a | Extensión posterior, no bloquea primer hito | Motor y perfiles aceptados, parámetros ratificados y tests de escasez. |
| Publicaciones/retirada | Condicional para bloque documental | Esquema/publication_id/parser y soporte de 03/06. |

La primera entrega sigue siendo MBL, IC, 1−Wang y 1−Lin bajo las tres condiciones propuestas en 02, con estados, dos figuras y ficha. Si una métrica falla su puerta, declarar entrega parcial o enmienda aprobada; no sustituirla silenciosamente por otra.

Sea k número de términos, a tamaño típico de cierre ancestral y U número de parejas únicas consultadas. Se espera reutilizar primitivas por pareja/recursos y agregar por proteína; almacenar solo parejas necesarias, no toda matriz GO. El trabajo de pares por proteína es O(k²); IC agregado O(k). La construcción de perfiles depende del corpus y cierre. Es una estimación algorítmica, sin tiempos, hardware ni benchmark inventados. 05 medirá costes de implementación y 07 definirá pruebas.

## 14. Decisiones, pendientes y aceptación

### 14.1. Decisiones registradas

| ID | Decisión | Estado |
|---|---|---|
| D04-01 | Separar significado de primitiva y agregación proteica | PROPOSTA, no implementación existente. |
| D04-02 | MBL identificada como profundidad/DCA, no shortest path automático | Verificación estática en G2/U1; adopción de variante pendiente. |
| D04-03 | Sin diagonal y una sola contribución por pareja única | PROPOSTA normativa de §3. |
| D04-04 | Cobertura completa principal para IC/MBL/Wang/Lin | PROPOSTA conservadora; no cambia umbral propio de A. |
| D04-05 | Lin con denominador cero no estimable | PROPOSTA distinta de algunas convenciones de backend, registrada. |
| D04-06 | Asociaciones con única fuente en anexo recuperado de historial | PROPOSTA de integración editorial, sin afirmar identidad de bytes ni aprobación previa. |

### 14.2. Pendientes accionables

| ID | Pregunta e impacto | Propuesta justificada | Validador requerido | Bloqueo |
|---|---|---|---|---|
| DP-01 | ¿Qué versión exacta de goatools y qué rutas se usarán? | Fijar release/commit real; no equiparar rango de pyproject con entorno. | Mantenedor y revisor técnico. | Sí para aceptación de primitivas. |
| DP-02 | ¿Coincide MBL histórica con profundidad/DCA y cómo se resuelve fallback? | Adoptar ID explícito solo tras comparación con código histórico; bloquear fallback negativo. | Revisor científico/métricas y mantenedor. | Sí MBL del hito. |
| DP-03 | ¿Base y denominador IC coinciden con 03 y §5? | Verificar tinfo/conteos de dependencia instalada; adaptación versionada si diverge. | Revisor IC y responsable de datos. | Sí IC/Lin. |
| DP-04 | ¿Qué relaciones/pesos Wang se ratifican? | Principal is_a_only 0.8 compatible con ruta observada; part_of como variante explícita. | Responsable científico y mantenedor GO. | Sí Wang aceptado. |
| DP-05 | ¿MICA y política de cero Lin quedan aprobados? | Fórmula estricta §7; no aceptar el cero del wrapper sin contexto. | Responsable científico/métricas. | Sí Lin. |
| DP-06 | ¿Se ratifica cobertura completa para principales intraaspecto? | Evitar sesgo de medias de subconjuntos; conservar disponible diagnóstico. | Responsable científico/estadístico. | Sí publicación del principal. |
| DP-07 | ¿Cómo incorporar 04a y parámetros provisionales v1.1? | Anexo adaptado con procedencia explícita y sin repetir fórmulas aquí. | Responsable de métricas y datos. | No primer hito; sí A. |
| DP-08 | ¿Son observables referencias, NOT y condiciones? | Guardas de 03 y parser, no reconstrucción ficticia. | Responsable de datos/curación. | Por bloque afectado. |
| DP-09 | ¿Tolerancias y serialización se aceptan? | Ratificar §10/11 en 05/07; exactitud para conteos. | Responsable técnico. | Sí pruebas de aceptación, no redacción. |
| DP-10 | ¿Quién revisa y aprueba versión? | Asignar roles y registrar alcance/fecha. | Coordinación del proyecto. | Sí para declarar uso autorizado. |

### 14.3. Criterios verificables de aceptación

AC04-01: cada salida identifica cálculo, dominio, recursos y versión; AC04-02: primitivas de backend comparadas con definiciones y fixtures; AC04-03: fallback no cambia semántica en silencio; AC04-04: términos/pares únicos y denominadores correctos; AC04-05: cero, raíz, sin cobertura y cross-aspect distinguidos; AC04-06: floats inválidos no se publican; AC04-07: detalle y agregado reconciliables; AC04-08: fixtures multi-parent, MICA≠DCA y NA implementadas en 07; AC04-09: anexo A y sus cambios identificados; AC04-10: aprobación de responsables registrada. Todos son requisitos futuros, no pruebas pasadas.

## 15. Inventario de fuentes y límites

### 15.1. BioData, lectura de esta sesión

Todas las URL G apuntan al commit BioData de cabecera.

| ID | Ruta/símbolos | Evidencia |
|---|---|---|
| G1 | [README.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/README.md), What Is In This Repo y Running Tests | Documento leído, no ejecución. |
| G2 | [CBBIO/GO.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/GO.py), métodos y helpers detallados en §§2–7 | Código completo leído. Fórmulas locales y rutas verificadas estáticamente. |
| G3 | [tests/test_go.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_go.py), tests IC/similitud/Wang/MBL/errores y fixture OBO | Tests leídos, no ejecutados; algunas aserciones solo comprueban no negatividad. |
| G4 | [docs/GO.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/docs/GO.md), Information Content; Group similarity; Utilities | Documentación, sin acreditar entorno. |
| G5 | [sql/schema.sql](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/sql/schema.sql), anotaciones, proteínas, go_terms | Esquema leído; sin publication_id remoto, diferencia con información de usuario tratada por 03. |
| G6 | [pyproject.toml](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/pyproject.toml), project.dependencies | Rango goatools observado, no versión instalada; resto de dependencias no se exige instalar para este dossier. |

### 15.2. Dependencia upstream comparativa

Repo `tanghaibao/goatools`; revisión de árbol recuperada `5b88eefcd8284f5d146d36728b4925785b563125`. Las lecturas de archivos ocurrieron sobre rama predeterminada de esa consulta, no sobre una instalación. Para identificar exactamente lo devuelto se conservan SHA de blob; no se promete equivalencia con una release de BioData.

- U1. [goatools/semantic.py](https://github.com/tanghaibao/goatools/blob/5b88eefcd8284f5d146d36728b4925785b563125/goatools/semantic.py), blob `ea7668b0f3c9adc8bbad33fd45e36b1d9945959d`; `TermCounts`, `get_info_content`, `lin_sim_calc`, `most_informative_common_ancestor`, `min_branch_length`, `shortest_path`.
- U2. [goatools/semsim/termwise/wang.py](https://github.com/tanghaibao/goatools/blob/5b88eefcd8284f5d146d36728b4925785b563125/goatools/semsim/termwise/wang.py), blob `b9cb1d00e31008139ef7a5f55607462c11045f5e`; `SsWang`, `_init_rels`, `_init_edge_weight_factor`, `get_sim`.
- U3. [goatools/semsim/termwise/dag_a.py](https://github.com/tanghaibao/goatools/blob/5b88eefcd8284f5d146d36728b4925785b563125/goatools/semsim/termwise/dag_a.py), blob `a846e0edd9d38320620ccfaeb94c873fb71c4d5d`; `DagA._init_go2svalue`.

Si al aceptar el entorno se usa otra fuente, se requiere comparación explícita de comportamiento, no editar estas referencias retrospectivamente.

### 15.3. Fuentes científicas consultadas

- P1. Wang, J. Z., Du, Z., Payattakool, R., Yu, P. S. y Chen, C.-F. (2007), «A new method to measure the semantic similarity of GO terms», Bioinformatics 23(10), 1274–1281. DOI verificado en página editorial: https://doi.org/10.1093/bioinformatics/btm087 . Texto editorial recuperado de https://academic.oup.com/bioinformatics/article/23/10/1274/197095 , en particular §§2.1–2.2 y 5; ecuaciones gráficas parcialmente no extraídas, contrastadas con U2/U3. No se transfieren sus resultados de validación al presente estudio.
- P2. Lin, D. (1998), «An Information-Theoretic Definition of Similarity», ICML 1998. Registro primario: https://icml.cc/Conferences/1998/papers/paper37.html . Se consultó metadato/resumen por búsqueda, no texto completo verificable: la fórmula GO/MICA se fundamenta operativamente en U1, no se atribuye a una lectura completa del artículo. Falló la recuperación del PDF localizado.
- P3. Bouma, G. (2009), «Normalized (Pointwise) Mutual Information in Collocation Extraction», §3.1, ecuación 7. Texto recuperado de https://svn.spraakdata.gu.se/repos/gerlof/pub/www/Docs/npmi-pfd.pdf . Sustenta NPMI, no valida coanotación proteica ni umbrales del proyecto.

### 15.4. Materiales previos y accesibilidad

- `Dossier_extensio_PIS_BioData_PEC_v0.1.md`, §§6–10: adjunto identificado en el inventario y contenido accesible en historial. Propuestas originales D³/RICD/NDE, no aprobadas ni fórmulas definitivas.
- `canonical_multifunctional_protein_data_dossier.md`: Project File localizado y extractos de definiciones/procedencia recuperados; no certificado de implementación.
- `dataset_designer_functional_contract.md`, §6.2: Project File recuperado; enumera métricas pero no fija por sí solo fórmulas actuales; selección negativa histórica fuera de alcance.
- `mfp_bibliographic_catalog_vision.md`, Scientific Interpretation e Identity Model: contenido de exploraciones previas accesible en conversación; catálogo de atribuciones, no código remoto auditado.
- Documentos 01, 02 y 03 v0.1: contenido completo visible en historial PEC de solicitudes de 2026-10-26 21:16, 22:21 y 22:26 CET. Archivos físicos anteriores no localizados como entradas del inventario actual. Se usan como borradores, no como documentos aprobados.
- Especificación v1.1 de asociaciones: contenido completo de generación visible en conversación tras solicitud 2026-10-26 13:49 CET; archivo físico previo no recuperado. El anexo declara adaptación de ese contenido, no restauración byte a byte.
- Propuestas de experimentación/infraestructura: conversación PEC de 2026-10-26 20:29/20:56 CET, accesibles. Son diseño, no ejecución.

NO ACCESSIBLE: base instalada y datos reales, versión exacta de goatools instalada, snapshots y resultados del usuario. Código remoto de PIS, mfp-bibliography y PEC no auditado en esta consulta. PIS tiene rol de adquisición propuesto en dossier inicial, BioData cálculo localizado, mfp-bibliography catálogo documentado y repositorio experimental candidato, PEC marco/clasificador fuera de fase. No se confunden ni se da por demostrada su integración.

05–07 como archivos formales: no localizados en las fuentes accesibles. El presente anexo 04a se crea en esta entrega; su existencia no significa aprobación. No se ejecuta ninguna prueba ni se crean recursos experimentales con datos ficticios.

## 16. Dependencias y comprobación de coherencia

01 conserva alcance; 02 define contrastes y condiciones y no recibe una jerarquía de verdad por scores; 03 aporta términos, identidad, recursos y conteos sin fijar fórmulas; 04a concentra la norma A; 05 implementará adaptadores/rutas/formatos; 06 valorará evidencia, no las métricas; 07 convertirá expectativas en tests y aceptará resultados. Los enlaces a archivos pendientes no acreditan su aprobación.

Para avanzar se requiere ratificar decisiones por bloque y registrar parámetros efectivos en `configs/pilot.yaml` y manifiesto reales. No se fijan aquí snapshot_id, tamaño de cohorte, PMID, hash de datos, resultado o tiempo de ejecución. Conclusión documental: catálogo desarrollado y divergencias explicitadas; ninguna métrica se declara operacionalmente validada por esta redacción.
