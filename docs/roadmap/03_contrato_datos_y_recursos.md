# Contrato de datos y recursos para la auditoría del corpus positivo atribuido como multifuncional

| Campo | Valor |
|---|---|
| Archivo | `03_contrato_datos_y_recursos.md` |
| Versión | 0.1 |
| Estado | borrador para revisión, no aprobado |
| Fecha | 2026-10-26 |
| Responsable | Pendiente de asignar |
| Revisión de datos, científica y técnica | Pendiente de asignar |
| Proyecto | PEC; auditoría y caracterización de positivos atribuidos |
| Fuentes y dependencias | Inventario de §18; documentos 01, 02, 04/04a, 05, 06 y 07 |
| Repositorio inspeccionado | `CBBIO/BioData` |
| Commit consultado | `ed073bd4df680a3b45ee69943916e196d28b63b6` |

Este contrato propone cómo reconstruir inputs idénticos desde una misma exportación y recursos congelados, sin decisiones implícitas. No es una migración SQL, una certificación de la base desplegada ni una implementación ya disponible. Los nombres de tablas canónicas y artefactos que siguen son propuestas de intercambio, no tablas existentes en PostgreSQL.

No se han ejecutado consultas a la base del usuario, experimentos, tests ni notebooks. Se ha realizado lectura remota y documental y se ha generado este archivo. No se han creado ni modificado repositorios, commits, issues o pull requests.

## Índice

1. Propósito, autoridad y convenciones
2. Fuentes de verdad y capacidades observadas
3. Inventario relacional verificado
4. Diccionario de campos existentes
5. Identidad y reconciliación
6. Modelo canónico conceptual propuesto
7. Diccionario canónico y procedencia
8. Referencias y soporte documental
9. Política GO y preparación determinista
10. Cohortes, referencia y pool reservado
11. Snapshots y compatibilidad
12. Contratos de perfiles estadísticos
13. Tablas de entrada/salida y reconstrucción
14. Demostración de equivalencia
15. Validaciones e incidencias
16. Ejemplo sintético
17. Decisiones, pendientes y criterios de aceptación
18. Inventario de fuentes y limitaciones
19. Dependencias y comprobación final de coherencia

## 1. Propósito, autoridad y convenciones

01 gobierna objetivo y alcance; 02, comparaciones, intervenciones y análisis; 03, datos, recursos, identidad y transformaciones; 04, fórmulas y agregaciones; 05, arquitectura; 06, valoración bibliográfica; 07, pruebas y aceptación de implementación. El presente contrato no redefine fórmulas ni categorías curatoriales.

La fase estudia el corpus positivo atribuido como multifuncional. No selecciona ni valida negativos y no entrena clasificadores. Referencia estadística y pool reservado no son sinónimos de clase negativa. Un valor GO no confirma multifuncionalidad ni moonlighting.

Estados de evidencia, conservados literalmente:

| Estado | Significado |
|---|---|
| VERIFICAT EN CODI | Implementación o esquema leído, no necesariamente ejecutado ni equivalente a la instalación del usuario. |
| DOCUMENTAT NO VERIFICAT | Documento o información aportada sin verificación operacional. |
| PROPOSTA | Regla de este borrador, sujeta a aprobación. |
| PENDENT | Decisión necesaria aún no cerrada. |
| NO ACCESSIBLE | Recurso no consultable en esta sesión; no demuestra inexistencia. |

Salvo que se indique fuente y estado distintos, las normas de transformación y el modelo canónico son PROPOSTA. «Debe» expresa el requisito propuesto para una futura ejecución aceptada, no su cumplimiento actual.

Glosario: PK = clave primaria; FK = clave foránea; UQ = restricción de unicidad; NN = no admite nulo; NULL = ausencia explícita; 1:N = uno a muchos; N:M = muchos a muchos; GO = Gene Ontology; MF/BP/CC = función molecular/proceso biológico/componente celular; MFP = proteína multifuncional; IC = contenido informativo, distinto del código GO `IC`; PMID/DOI/GO_REF = identificadores de referencia; OBO = formato de ontología; GAF = Gene Association File; API = interfaz de programación; SHA-256 = algoritmo de huella digital propuesto; JSON/CSV/Parquet = formatos de intercambio. Snapshot significa copia congelada identificable, no una copia ya disponible.

## 2. Fuentes de verdad y capacidades observadas

### 2.1. Tres capas que no se intercambian

1. Esquema del repositorio: `sql/schema.sql` en commit fijado [G2]. Define estructura, no contenido real.
2. Esquema aportado por el usuario: salida `\dt` y `\d protein_go_term_annotation` de conversación [C4]. Testimonio de una instalación, no inspección directa.
3. Exportación de trabajo: NO ACCESSIBLE y no creada aquí. Su estructura efectiva deberá describirse y validarse antes del piloto.

El adaptador debe identificar explícitamente qué variante lee. Un campo ausente en el repositorio no se elimina de la exportación que lo contenga; un campo no exportado no se reconstruye suponiendo su valor.

### 2.2. Divergencia comprobada

| Elemento | Esquema remoto G2 | Esquema aportado C4 | Consecuencia |
|---|---|---|---|
| `publication_id` | No declarado | varchar nullable | Verificar versión real y parser antes de análisis documental. |
| PK anotación | `(id, protein_id, go_id)` | `id` | No usar `id` como única clave del bruto remoto. |
| UQ anotación | `(protein_id, go_id)` | `(protein_id, go_id, evidence_code, publication_id)` | Puede cambiar la capacidad de conservar varios soportes. |
| Índices de anotación | Los declarados en dump remoto | Índices específicos GO, proteína y publicación | No se presume una migración concreta ni rendimiento. |

No se conoce el proceso que produjo la diferencia. El esquema remoto limita una pareja proteína–GO a una fila y, por sí solo, no representa múltiples evidencias independientes para esa pareja. No se deduce cómo se ingirieron ni si se perdieron datos históricos. [G2, `uq_pga_protein_go`]

### 2.3. Cliente y pérdidas de información

VERIFICAT EN CODI:

- `BioDataClient.get_protein_by_accession` une `accession.code` con `protein.id` mediante `accession.protein_id`; no demuestra que `protein.id` sea una accession UniProt. [G3]
- `get_protein_go_annotations` selecciona GO ID, categoría, descripción y evidencia; no selecciona la clave de fila, publicación, relación o fecha de anotación. [G3]
- `GOAnnotation` en `CBBIO/types.py` solo contiene `go_id`, `category`, `description`, `evidence_code`. El alias `ProteinID = str` no define un namespace global. [G4]
- `get_protein_species_taxonomy` y `get_protein_sequences` ofrecen lecturas por lotes, con disponibilidad dependiente de las filas. [G3]
- `query_all` permite una proyección explícita; `transaction` no fija por sí mismo aislamiento de snapshot y depende de autocommit. [G3]

La API de alto nivel puede servir para cálculo una vez preparado el input, pero no es una exportación sin pérdida de evidencia. 05 deberá implementar un adaptador de lectura autorizado que conserve columnas efectivas. No se propone modificar la API ni el esquema remoto desde este documento.

## 3. Inventario relacional verificado

Inventario basado en declaraciones y FK de G2; filas y cardinalidades observadas de la base real: NO ACCESSIBLE.

| Entidad existente | PK | Relaciones declaradas y cardinalidad permitida | Papel en esta fase |
|---|---|---|---|
| `protein` | `id` | 0..1 `sequence_id`; varias proteínas pueden compartir secuencia | Identidad local y metadatos. |
| `accession` | `code` | 0..1 proteína por fila, 0..N accessions por proteína | Crosswalk local; sin namespace declarado. |
| `sequence` | `id` | 0..N proteínas y cadenas; hash nullable con índice único | Duplicación de secuencia y control de identidad. |
| `go_terms` | `go_id` | 0..N anotaciones | Etiquetas locales; no sustituye GO congelado. |
| `protein_go_term_annotation` | compuesta en remoto | Cada fila apunta a una proteína y un GO; UQ pareja | Evidencia mínima remota. |
| `structure` | `id` | Cada estructura apunta a una proteína; 0..N por proteína | Fuera del input mínimo. |
| `chain` | `id` | Estructura obligatoria; secuencia y accession opcionales | No usar como identidad proteica de GO. |
| `state` | `id` | Cadena y estructura obligatorias | Fuera del input mínimo. |
| `structure_3di` | `id` | Un estado por fila; 0..N filas por estado | Fuera del alcance métrico actual. |
| `sequence_embedding_type` | `id` | `name` único | No necesario para esta fase. |
| `sequence_embeddings` | `id` | Secuencia y tipo obligatorios; UQ secuencia/tipo/capa | No necesario ni criterio de inclusión. |
| `structural_alignment_types` | `id` | No FK de uso declarada en el dump leído | Fuera del input mínimo. |

Las cadenas se relacionan con accessions y secuencias; ese camino no autoriza a transferir funciones de un fragmento estructural a toda la proteína.

## 4. Diccionario de campos existentes

Todos los campos de esta sección son reales en G2, VERIFICAT EN CODI. Tipos y nulabilidad son los declarados allí, no resultados del catálogo de una base desplegada. La columna «transformación» describe una propuesta de exportación, no comportamiento actual de ingesta. Los grupos de campos indicados comparten los atributos descritos.

### 4.1. Núcleo de anotaciones y GO

| Campo | Tipo / nulo | Clave y cardinalidad | Significado/origen | Validación y transformación propuesta |
|---|---|---|---|---|
| `protein_go_term_annotation.id` | integer / NN | Parte de PK compuesta remota | Identificador de fila local | Conservar junto con proteína, GO y snapshot; no asumir unicidad de id aislado. |
| `.protein_id` | varchar / NN | FK protein.id; una proteína por fila | Entidad anotada local | Resolver FK antes de unir; conservar raw. |
| `.go_id` | varchar / NN | FK go_terms.go_id; un término por fila | Identificador GO | Conservar bruto y resolución contra GO congelado. |
| `.evidence_code` | varchar / NN | Sin dominio SQL de códigos | Evidencia registrada | Validar vocabulario de 02 §4; no inferir calidad a partir de texto. |
| `go_terms.go_id` | varchar / NN | PK | Término local | Verificar existencia/alias/obsolescencia en recurso fijado. |
| `.category` | varchar / NN | Una cadena por término | Aspecto local | Mapear solo valores declarados; comparar con namespace GO. |
| `.description` | varchar / nullable | 0..1 por término | Descripción local | Preservar; no usar nombre como clave. |

Campo `publication_id`: DOCUMENTAT NO VERIFICAT en C4, varchar nullable, 0..1 celda por fila, sin FK declarada en el material aportado. No significa necesariamente PMID ni una sola referencia biológica. Exportar como `reference_raw` si existe, con observabilidad `present` o `source_null`. Si la columna no existe, `column_absent`; no producir una columna llena de nulos sin explicar la causa.

### 4.2. Proteínas

| Campo(s) en `protein` | Tipo / nulo | Clave/cardinalidad | Significado y validación/transformación |
|---|---|---|---|
| `id` | varchar / NN | PK; una fila local | Preservar como local, no normalizar como UniProt sin evidencia. |
| `sequence_id` | integer / nullable | FK sequence.id, 0..1 | Verificar enlace; ausencia no equivale a secuencia vacía. |
| `taxonomy_id` | varchar / nullable | Sin FK taxonómica | Conservar raw; validar y resolver contra taxonomía congelada si se usa. |
| `organism` | varchar / nullable | 0..1 texto | Nombre declarado; no fusionar entidades por coincidencia textual. |
| `data_class` | varchar / nullable | Sin vocabulario/semántica impuesta por SQL | No usar como etiqueta MFP ni condición primaria sin contrato de procedencia. |
| `molecule_type` | varchar / nullable | 0..1 | Conservar y auditar si se utiliza para elegibilidad. |
| `description`, `gene_name`, `organelle`, `comments`, `seqinfo` | varchar / nullable cada uno | 0..1 texto por campo | Preservar como metadatos; no identificadores ni evidencia automática. |
| `protein_existence` | integer / nullable | Sin CHECK de rango en dump | Conservar; no confundir con score de multifuncionalidad. |
| `disappeared` | boolean / nullable | Tres estados posibles | true/false/desconocido distintos; no deducir causa de retirada. |
| `created_date`, `sequence_update_date`, `annotation_update_date` | date / nullable cada uno | 0..1 por campo | Fechas a nivel de proteína; no sustituyen fecha de cada anotación ni publicación. |
| `created_at`, `updated_at` | timestamp sin zona / nullable cada uno | 0..1 por campo | Preservar sin inventar zona horaria; informar la zona de origen si se conoce. |

### 4.3. Accessions y secuencias

| Campo | Tipo / nulo | Clave/cardinalidad | Significado y validación/transformación |
|---|---|---|---|
| `accession.code` | varchar / NN | PK local | Cadena local, no namespace explícito. Conservar y clasificar solo por evidencia de origen. |
| `accession.protein_id` | varchar / nullable | FK; 0..1 proteína por código | Enlaces nulos quedan sin resolver, no descartados por inner join silencioso. |
| `accession.primary` | boolean / nullable | No restricción de única primaria por proteína | No asumir que hay exactamente una primaria ni que sea primaria UniProt. |
| `accession.tag` | varchar / nullable | Sin catálogo verificado | No inferir namespace o estado sin inspección de valores y origen. |
| `accession.created_at`, `.updated_at` | timestamp sin zona / nullable | Metadatos locales | Preservar; no historia completa de redirects. |
| `sequence.id` | integer / NN | PK | Identidad local de secuencia. |
| `sequence.sequence` | varchar / NN | Una cadena por fila | Validar longitud, caracteres y normalización; conservar bruto. |
| `sequence.sequence_hash` | varchar / nullable | Índice único; algoritmo no declarado | No asumir SHA-256 ni usarlo como huella canónica hasta verificarlo. |

### 4.4. Campos periféricos inventariados, no inputs obligatorios

Para cerrar el inventario sin convertirlo en requisito de exportación:

| Tabla | Campos NN en G2 | Campos nullable en G2 | Claves y uso |
|---|---|---|---|
| `chain` | id integer; name varchar; structure_id varchar | sequence_id integer; accession_code varchar | PK id; FK a structure, sequence y accession. |
| `structure` | id, protein_id, file_path varchar | method varchar; resolution double precision; created_at/updated_at timestamp sin zona | PK id; file_path UQ; FK protein. |
| `state` | id integer; model_id, file_path, structure_id varchar; chain_id integer | Ninguno | PK id; FK chain/structure. |
| `structure_3di` | id integer; state_id integer | embedding varchar; created_at/updated_at timestamp sin zona | PK id; FK state. |
| `sequence_embedding_type` | id integer; name varchar | description, task_name, model_name varchar | PK id; name UQ. |
| `sequence_embeddings` | id, sequence_id, embedding_type_id, layer_index integer; embedding halfvec; created_at/updated_at timestamp sin zona | shape integer[] | PK id; FK sequence/type; UQ secuencia/tipo/capa. |
| `structural_alignment_types` | id integer; name varchar | description, task_name varchar | PK id. |

Origen de todos ellos: esquema remoto G2. En el piloto se excluyen de la exportación mínima por no ser necesarios; no se afirma ausencia de datos. No se validan dimensiones de embeddings ni archivos estructurales para aceptar inputs GO.

## 5. Identidad y reconciliación

### 5.1. Ámbitos de identificadores

- `source_record_id`: único solo dentro de una fuente y release; se utiliza junto a esos ámbitos.
- `protein.id`: clave local del snapshot BioData; el esquema no acredita unicidad global o persistencia entre bases.
- `accession.code`: clave local de tabla sin namespace SQL. Los ejemplos de API no convierten todos sus valores en accessions UniProt.
- `entity_id`: identificador canónico propuesto del experimento, cuya relación con fuentes y bases vive en un crosswalk versionado. No se sobrescribe `protein.id`.

No se une un entero de publicación ni un identificador de fuente con otro sistema solo porque coincide su texto. Las claves canónicas y de bruto incluyen namespace y ámbito.

### 5.2. Orden determinista propuesto

1. Preservar valores brutos y ámbito de cada identificador.
2. Normalizar solo con parser versionado por namespace: retirar espacios periféricos; no eliminar guiones de isoformas ni cambiar indiscriminadamente mayúsculas de IDs sensibles a caja.
3. Buscar coincidencia exacta dentro del namespace y release declarados.
4. Aplicar crosswalk congelado de accessions primarias/secundarias y cambios históricos cuando exista evidencia explícita.
5. Validar cardinalidad, taxonomía e isoforma; si hay más de un candidato incompatible, no escoger el primero.
6. Resolver por regla documentada o revisión; registrar evidencia, decisión y estado.
7. Generar `entity_id` desde una clave de anclaje estable y un namespace de catálogo fijado; algoritmo determinista y crosswalk se congelan. Los cambios de identidad generan una nueva versión y tabla de sucesión, no renumeración silenciosa.

No se fusiona por nombre, gen, descripción, organismo textual ni similitud difusa. Se preserva el criterio conservador del catálogo [S2, Identity Model], pero no se identifica su `protein_id` derivado con el `protein.id` de BioData.

### 5.3. Secundarias, redirects e isoformas

UniProt documenta que las accessions secundarias pueden conservarse en varias entradas después de una separación. Por eso una secundaria no garantiza un destino único en todas las releases [P3]. El crosswalk debe contener relación, fuente, release, fecha de resolución y cardinalidad; no basta convertir una secundaria en la primera primaria disponible.

Las isoformas tienen identificadores específicos; no se elimina su sufijo para transferir funciones a la forma canónica [P4]. Propuesta principal: conservar ámbito de forma cuando existe y no colapsar formas explícitas. Si una atribución es específica de isoforma y BioData solo permite una entidad más amplia, marcar `form_scope_mismatch`; puede entrar al inventario, pero no transferir evidencia específica automáticamente. La taxonomía incompatible bloquea la fusión aunque el identificador parezca coincidir.

### 5.4. Duplicados y secuencias

- Varios registros de fuente o accessions que apuntan a la misma entidad: una entidad analítica, todas las atribuciones y procedencias retenidas.
- Misma accession con entidades candidatas incompatibles: colisión; cuarentena de mapeo hasta resolución.
- Secuencia idéntica en entidades diferentes: grupo de duplicación, no fusión automática de funciones u organismos.
- Distintos registros con el mismo hash: verificar también secuencia normalizada y longitud antes de afirmar identidad; una huella no sustituye control de contenido.
- Variantes de secuencia o taxonomía para una entidad: conflicto que no se resuelve tomando el registro más reciente sin regla.

Propuesta para normalización de secuencia de control: remover espacios ASCII, convertir letras a mayúscula y conservar caracteres ambiguos, gaps o terminaciones para validación; no borrarlos ni sustituirlos silenciosamente. El conjunto aceptable de caracteres se versiona. Secuencias inválidas siguen trazables; no bloquean automáticamente métricas GO si identidad y ámbito están resueltos.

Conflicto histórico: el dossier canónico sugiere deduplicación por secuencia; el catálogo preserva identidad por accession. Para esta auditoría se propone entidad reconciliada como unidad principal y grupos de secuencia como metadato de dependencia, sin fusionar taxones o claims. Debe ratificarse y registrarse el cambio de contexto [S1–S2; DP-02].

## 6. Modelo canónico conceptual propuesto

Este modelo describe archivos/tablas de intercambio, no una migración de BioData:

```text
source_release 1 ── N source_record 1 ── N source_claim
                         │                  │
                         └── identifier     └── claim_reference ── reference
                                  │
                            identity_mapping
                                  │
                              entity 1 ── N entity_identifier
                                  │
               ┌──────────────────┼─────────────────┐
        local_entity_link    cohort_membership   annotation
               │                                    │
       BioData protein.id                 support_group / annotation_reference
                                                    │
                                                reference
                                                    │
                                            reference_identifier

annotation N ── 1 go_term_resolution ── GO release
annotation 1 ── N term_derivation ── prepared_term
reference/IC profile ── universe_member ── entity
```

`annotation_reference` y `claim_reference` son relaciones distintas, aunque apunten al mismo artículo. `support_group` solo se necesita si la fuente representa soporte compuesto; no impone esa semántica a GAF.

Todas las tablas canónicas tienen versión de esquema y procedencia de artefacto. Las claves técnicas son strings deterministas, no números consecutivos dependientes del orden de lectura. Las tablas brutas preservan multiplicidad y posición original; las derivadas separan conjuntos de términos de filas de evidencia.

## 7. Diccionario canónico y procedencia

### 7.1. Convenciones comunes

En las tablas siguientes todos los campos son PROPOSTA. `!` significa obligatorio no nulo en una fila aceptada; `?`, nullable con motivo explícito. Listas se representan como relaciones hijas o arrays tipados según el esquema final, nunca como cadenas separadas por comas sin contrato. Fechas de adquisición usan ISO 8601 con zona cuando se conoce; fechas biológicas sin zona conservan tipo date. Un campo fuente ausente no se rellena con un valor deducido sin registrar derivación.

Cada fila derivada enlaza `provenance_id!`; el registro de procedencia contiene `artifact_id!`, `raw_locator!` y `transform_id!`. Las claves, cardinalidades y reglas se describen por tabla; validaciones comunes: PK únicas, FK válidas, strings no vacíos, tipos y vocabularios versionados. 05 fijará la representación física sin alterar semántica.

### 7.2. Fuentes, entidades y claims

| Tabla / granularidad | Campos, tipo y nulabilidad | Clave/cardinalidad y origen | Significado, validación y transformación |
|---|---|---|---|
| `source_releases`: una versión de fuente | source_release_id string!; source_name string!; version_raw string?; acquired_at timestamp!; license_status enum!; artifact_id string! | PK release; 1:N records; proveedor/exportación | Versión desconocida se declara, no se inventa. Integridad byte a byte del artefacto. |
| `source_records`: una ocurrencia original | record_id string!; source_release_id string!; source_local_id string?; row_locator string!; raw_payload JSON!; parse_status enum! | PK record; FK release; fila/raw original | Conservar duplicados originales con localizador distinto; un ID repetido se registra. |
| `source_claims`: una atribución original | claim_id string!; record_id string!; category_raw string?; evidence_raw JSON?; functions_raw JSON?; extraction_status enum! | PK claim; FK record; 0:N claims por record | Categoría ausente no se sustituye por «curated». Presencia en catálogo puede registrarse como afirmación de inclusión con semántica explícita. |
| `entities`: una identidad analítica | entity_id string!; anchor_namespace string!; anchor_value string!; identity_policy_id string!; entity_scope enum!; identity_status enum! | PK entity; crosswalk congelado | Ámbito entry/isoform/source_unresolved; sin propiedad binaria de verdad multifuncional. |
| `identity_mappings`: una decisión por identificador y destino candidato | mapping_id string!; record_id string!; identifier_namespace string!; identifier_raw string!; identifier_normalized string?; entity_id string?; mapping_status enum!; mapping_rule_id string!; evidence_locator string? | PK mapping; FK record y entity nullable; N:M candidatos | resolved/ambiguous/unresolved/rejected; destino nulo permitido sin desaparecer. Decisión de revisión con versión, no first match. |
| `local_entity_links`: enlace a una base concreta | snapshot_scope string!; biodata_protein_id string!; entity_id string!; link_status enum!; provenance_id string! | Clave compuesta por ámbito/local/entity; entidad y bruto local | Un enlace aceptado único por ámbito/local para la política; conflictos no duplican el conteo. |
| `entity_identifiers`: alias normalizados | entity_id string!; namespace string!; value string!; role enum!; source_release_id string!; validity_raw JSON? | Clave de identidad/namespace/valor/release/rol | primary/secondary/isoform/local/unknown; no exigir una primaria si la fuente no la acredita. |
| `entity_metadata`: metadato con procedencia | entity_id string!; field_name string!; value_raw JSON?; value_normalized JSON?; observation_status enum!; provenance_id string! | Clave entity/field/provenance | Taxonomía, secuencia, nombres y fechas; conservar discrepancias, no elegir una sin regla. |

Campos `evidence_raw` y `functions_raw` preservan la expresión fuente; no se presentan como revisión científica. Las decisiones curatoriales posteriores viven en 06 y enlazan a claim/annotation sin sobrescribirlos.

### 7.3. Anotaciones, resolución GO y soporte

| Tabla / granularidad | Campos, tipo y nulabilidad | Clave/cardinalidad y origen | Validación y transformación |
|---|---|---|---|
| `annotation_rows`: una fila observada | annotation_row_id string!; artifact_id string!; source_row_key JSON!; local_protein_id string!; entity_id string?; go_id_raw string!; evidence_raw string!; reference_raw string?; provenance_id string! | PK row; filas de exportación; entity FK nullable | Clave raw compuesta preservada; sin deduplicación destructiva. `reference_raw` con observabilidad independiente. |
| `annotation_metadata`: datos no siempre presentes | annotation_row_id string!; relation_raw string?; is_not boolean?; aspect_raw string?; assigned_by string?; annotation_date date?; with_from_raw string?; extension_raw string?; product_form_raw string?; taxon_raw string? | Una fila por annotation; origen enriquecido solo si conservado | null en is_not significa desconocido, no false. Contexto y operadores intactos. |
| `field_observability`: estado de cada campo | object_id string!; field_name string!; state enum!; detail string?; provenance_id string! | PK objeto/campo; o declaración de ámbito + excepción | present/source_null/column_absent/not_exported/not_accessible/not_applicable/derived; no confundir causas. |
| `go_term_resolution`: una decisión por input GO y release | ontology_id string!; go_id_raw string!; canonical_go_id string?; resolution_status enum!; aspect string?; resolution_rule_id string! | PK ontology/raw; OBO y crosswalk fijados | canonical/alt_id/obsolete_replaced/obsolete_unresolved/missing/conflict; no alias por nombre. |
| `prepared_terms`: un término por entidad/aspecto/condición/política | entity_id string!; aspect enum!; condition_id string!; term_policy_id string!; go_id string!; membership_origin enum! | PK por cinco campos; conjunto derivado | MF/BP/CC; explicit/derived/mixed; no replicar por artículos o filas. |
| `term_derivations`: trazabilidad del conjunto | prepared_term_key JSON!; annotation_row_id string!; derivation_type enum!; relation_path JSON?; transform_id string! | N:M entre términos preparados y evidencia | Para ancestros, conservar término semilla y relaciones o subgrafo reproducible; nunca crear una publicación experimental ficticia. |
| `annotation_dispositions`: resultado de cada regla | annotation_row_id string!; condition_id string!; policy_id string!; disposition enum!; reason_codes array! | PK fila/condición/política | accepted/quarantined/excluded; toda pérdida contabilizada; varias razones no multiplican filas originales. |

`prepared_terms` no reemplaza `annotation_rows`. Solo el primero se convierte en mapping para las funciones GO; el segundo sostiene la auditoría de evidencias y retiradas de publicaciones.

### 7.4. Referencias, cohortes y recursos

| Tabla | Campos principales, tipo y nulabilidad | Clave/cardinalidad y validación |
|---|---|---|
| `references` | reference_id string!; reference_kind enum!; identity_status enum!; metadata_status enum! | PK; publication/GO_reference/database_record/unknown; identidad no acredita lectura. |
| `reference_identifiers` | reference_id string!; namespace string!; value_raw string!; value_normalized string?; provenance_id string! | PK ref/namespace/value/provenance; alias solo con evidencia explícita. |
| `annotation_references` | annotation_row_id string!; reference_id string!; raw_group_locator string!; relationship_semantics enum!; provenance_id string! | N:M; evidencia fuente, no atribuciones MFP. |
| `claim_references` | claim_id string!; reference_id string!; role_raw string?; provenance_id string! | N:M separada de la anterior; permite solapamiento sin equiparar papeles. |
| `support_groups` | support_group_id string!; annotation_row_id string!; semantics enum!; source_format string!; member_reference_ids array! | Solo cuando necesario: alias_single_reference/alternative/joint/unknown, con evidencia del formato. |
| `cohort_membership` | cohort_id string!; entity_id string!; role enum!; inclusion_status enum!; reason_codes array!; policy_id string! | PK cohorte/entidad; positive_attributed/reference/reserved/development/evaluation; no negativo implícito. |
| `resource_registry` | resource_id string!; resource_kind enum!; source_uri string?; source_version string?; acquired_at timestamp!; bytes_hash string!; license_status enum! | PK; recursos efectivamente adquiridos; no inventar hash antes de disponer bytes. |
| `transform_registry` | transform_id string!; code_commit string!; policy_id string!; input_resource_ids array!; parameters_resource_id string!; environment_id string! | PK; transformación exacta, sin credenciales. |
| `issues` | issue_id string!; severity enum!; rule_id string!; object_type string!; object_id string!; observed JSON?; action enum!; status enum!; resolution_provenance string? | PK; ninguna incidencia desaparece por sobrescritura de raw. |

Los arrays que son conjuntos se serializan ordenados; los grupos con operadores conservan estructura y orden semántico. Los esquemas finales deberán especificar también enums y claves completas; se proponen artefactos `schemas/`, no se afirma que existan.

## 8. Referencias y soporte documental

### 8.1. Identificadores locales versus bibliográficos

`publication_id` es solo un nombre de columna observado en C4. El parser debe identificar si su contenido es un identificador local, PMID, DOI, GO_REF, otra referencia de base o expresión compuesta. No asignar namespace PMID a números por intuición.

PMID se conserva como cadena de dígitos validada, no como float; DOI como identificador normalizado por una regla versionada, conservando el texto original y sin eliminar contenido significativo; GO_REF y otras referencias conservan namespace. Un ID local solo enlaza al catálogo de publicaciones correspondiente si existe crosswalk documentado.

Referencias no resueltas, campo vacío y columna ausente son estados distintos. La recuperación de título/resumen es enriquecimiento versionado, no lectura del artículo completo ni verificación experimental.

### 8.2. Corrección explícita de la ambigüedad anterior

La especificación oficial GAF 2.2 indica que la columna Reference puede contener varios identificadores para una sola referencia única. Un pipe en esa columna no significa varios artículos independientes ni soporte OR/AND [P1, Reference, columna 6]. Los operadores de With/From y Annotation Extension tienen reglas diferentes [P1, columnas 8 y 16].

Por tanto, se precisa la propuesta general de 02 §8: antes de decidir soportes alternativos o conjuntos se interpreta el formato concreto. Para una línea GAF 2.2 válida, los IDs bibliográficos se modelan como alias de una referencia; no se aplican reglas genéricas OR/AND. Para `publication_id` de origen no acreditado, la semántica permanece unknown hasta documentación del parser o fuente. Esta precisión debe incorporarse como aclaración de 02, no ocultarse como una decisión previamente aprobada.

### 8.3. Deducción de soporte y retirada

Al retirar un artículo según 02 se retira la identidad bibliográfica reconciliada y todos sus alias de esa afirmación. Otro alias del mismo artículo no cuenta como soporte superviviente. Otra fila admisible que sustente el mismo término con una referencia diferente puede preservarlo. Referencias ambiguas no autorizan afirmar independencia ni eliminar todos sus términos arbitrariamente.

No existe FK remota verificada hacia publicaciones; el modelo canónico no puede prometer una bibliografía completa a partir de G2. Las referencias de claims MFP pueden existir en archivos de fuente aunque falten en GO; y viceversa. Su origen se conserva separadamente [S2, Target Product y Provenance Requirements].

## 9. Política GO y preparación determinista

### 9.1. Recurso y compatibilidad

Registrar archivo GO exacto, URI si se conoce, `data-version` o release declarado, formato, bytes_hash, fecha de adquisición, parser, versión de goatools y opciones efectivas de carga. La fecha de descarga no sustituye release. `go_terms.description` no determina el significado de un término en una release distinta.

El aspecto canónico se obtiene del namespace del recurso congelado: molecular_function→MF, biological_process→BP, cellular_component→CC. Si la fuente declara F/P/C o mf/bp/cc, el parser hace un mapeo explícito. Diferencias entre categoría local y GO se registran; el namespace de GO fijado gobierna el cálculo, no se modifica el bruto.

### 9.2. Estado de los términos

- ID canónico activo: conservar.
- `alt_id` inequívoco de la release: mapear al término canónico y registrar decisión.
- Término obsoleto con reemplazo único explícito: registrar candidato; solo aplicar si la política versionada autoriza ese tipo de reemplazo y no hay conflicto de aspecto/identidad.
- Varias alternativas, solo `consider`, reemplazo obsoleto o no resuelto: cuarentena para cálculo principal, conservar para revisión.
- Ausente del OBO: no fabricar un término ni deducirlo por nombre.

El conjunto de obsoletos/aliases debe inventariarse antes de filtrarlos. Cargar solo términos activos y luego usar `filter_valid_terms` no basta para distinguir obsolescencia y error tipográfico. G6 muestra que utilidades de filtrado descartan IDs; el adaptador debe auditar pérdidas antes de invocarlas.

### 9.3. Evidencia, NOT y relaciones

Las condiciones y listas de evidencia se referencian desde 02 §4; no se duplican aquí. La configuración resuelta debe contener la lista efectiva y su versión. Códigos desconocidos bloquean esa clasificación hasta resolución o excepción aprobada, no se convierten en experimental. TAS y código IC no se rebautizan como experimentales.

Relación producto–término, negación y relación entre términos GO son campos conceptualmente distintos. `find_relation` de G6 informa parentesco, no etiqueta ontológica de arista ni relación de anotación.

Propuesta de tres modos explícitos de aptitud:

| Modo de procedencia | Condición | Uso permitido |
|---|---|---|
| `source_complete` | Relación/NOT y procedencia exportadas y validadas | Selección positiva conforme a política. |
| `positive_ingest_attested` | Campo no conservado, pero proceso de ingesta y versión acreditan exclusión de NOT | Cálculo limitado al contrato de ingesta acreditado; limitación visible. |
| `legacy_unknown` | No se conoce relación/negación y no hay acreditación | Inventario; cálculo descriptivo degradado solo con aprobación explícita, sin afirmar filtro completo. |

`is_not=null` no se transforma en false. Las anotaciones NOT se preservan, pero no se cuentan como presencia positiva ni como ausencia estadística. Conflictos positivos/negativos aplicables al mismo ámbito y contexto se registran; no resolverlos con una eliminación global basada solo en GO ID. Hasta revisión, las unidades afectadas no pasan al cálculo principal estricto. La inferencia negativa requiere sus propias reglas, no el mismo cierre positivo [P1; P2].

### 9.4. Representación principal y variantes

Propuesta principal `asserted_unique`: términos explícitos del snapshot después de selección de evidencia, identidad y resolución GO; un término por entidad/aspecto/condición. «Explícito» significa almacenado, no necesariamente experimental o directamente observado en laboratorio.

Excluir raíces del conjunto métrico principal y contabilizar ND/raíces en calidad. Deduplicar términos sin perder soportes. La política de redundancia y el cierre ancestral se versionan como variantes separadas de sensibilidad de 02.

Para cierre positivo opcional se propone `is_a` y `part_of`, mismo aspecto, sin raíces en el conjunto puntuado. No utilizar `has_part` ni `regulates` como sustitutos de esas relaciones: GO distingue su semántica de agrupación [P2]. Reducción conservadora de redundancia inicial: retirar un ancestro explícito solo cuando otro término seleccionado lo subsume por `is_a` bajo esa política, preservando ambos en raw y derivación. 04 verificará que el algoritmo utiliza las relaciones configuradas; pasarlas en un manifiesto no garantiza que el backend las recorra.

Preparación de query y conteo de referencia pueden tener políticas diferentes si se declaran. El cierre interno necesario para IC no debe confundirse con expandir la lista de términos que se puntúa. Cambiar la representación genera otra identidad de input/perfil, no una sobrescritura.

### 9.5. Extensiones, With/From y formas

Cuando estén disponibles, conservar sin aplanar extensiones, With/From y forma específica del producto. El GAF distingue entidad principal y Gene Product Form ID para isoformas y formas procesadas [P1]. No propagar automáticamente una anotación de forma a todas las isoformas ni convertir contexto celular de una extensión en una anotación CC independiente.

Si faltan extensiones, declarar que el cálculo usa coanotación no contextualizada; no afirmar que carecen de relevancia biológica o que la proteína no tiene contexto específico.

## 10. Cohortes, referencia y pool reservado

Todas las pertenencias se congelan como datos, no consultas dinámicas a «todos los positivos actuales».

### 10.1. Cohorte positiva atribuida

Incluir en inventario todos los registros de las fuentes seleccionadas con estado de parsing, aunque no se resuelvan. Una entidad entra en el subconjunto analítico cuando existe atribución trazable, reconciliación aceptada y al menos un aspecto elegible para alguna operación; no se exige que todas las métricas sean calculables. Entidades sin anotaciones permanecen en la cobertura del corpus, no se eliminan del denominador general.

No exigir embeddings, estructura o un número de artículos como prueba de positividad. El ámbito taxonómico lo declara la configuración según 01/02; taxonomía desconocida impide análisis por taxón o referencia taxonómica, no borra el registro original. Claims conflictivos se conservan; clasificación derivada de evidencia pertenece a 06.

### 10.2. Referencia estadística

Propuesta principal: entidades reconciliadas de un corpus identificado, con taxonomía y anotaciones seleccionadas según política congelada, no exclusivamente positivas por conveniencia. No se afirma que sea libre de multifuncionalidad.

Antes de conteos: resolver alias para que una entidad no contribuya varias veces, aplicar política GO y excluir/quarantinar conflictos de identidad. Un término puede aparecer varias veces en raw pero contribuir una vez por entidad. La pertenencia de universo por aspecto se deriva antes de filtrar por soporte de término o pareja; no cambiar N tras consultar una pareja rara.

### 10.3. Solapamientos y temporalidad

Propuesta `external_frozen`: para la evaluación principal, referencia disjunta de entidades positivas evaluadas. Si no es viable, `internal_overlap_declared` como análisis exploratorio explícito, con sensibilidad disjunta cuando sea posible. Un cambio de modo obliga a nuevo manifiesto y revisión de inferencia; no ejecutar leave-one-out silencioso. El borrador v1.1 de asociaciones proponía referencia externa y este contrato conserva esa dirección como propuesta, no como hecho aprobado.

Reportar intersecciones por entidad y, si existen, por secuencia/familia y referencia bibliográfica. Disyunción de entidades no acredita independencia biológica o documental. Desarrollo y evaluación bibliográfica no se solapan por entidad; la regla de grupo de dependencia deberá fijarse para la evaluación de 02.

Fechas: distinguir release de fuente, fecha de anotación, adquisición, extracción y revisión. Una exportación de hoy sin historia de anotaciones no permite un análisis temporal histórico. Los joins temporales no usan información posterior al corte sin declararlo.

### 10.4. Pool reservado

Puede congelarse su lista y procedencia sin utilizarlo. Su selección no se optimiza mediante scores ni se etiqueta como negativo. Solapamientos con positivo/referencia se registran; su eventual uso futuro requiere otro protocolo. Su ausencia no bloquea el primer hito si existe referencia válida.

## 11. Snapshots y compatibilidad

### 11.1. Contenido mínimo propuesto

- Exportación bruta de las tablas necesarias, conservando claves, nulos y columnas efectivas.
- Descripción del esquema desplegado y versión si se conoce; no solo G2.
- Artefactos de fuentes MFP y sus atribuciones; metadatos de licencia.
- OBO y, si se necesita, crosswalk taxonómico/bibliográfico e identidad congelados.
- Pertenencias de cohortes y política resuelta.
- Versiones de código, dependencias, parsers y transformaciones.
- Informe de observabilidad, validación e incidencias.
- Manifiesto que enumera archivos y hashes a calcular sobre bytes reales.

Un snapshot analítico no equivale a backup restaurable de todo PostgreSQL. Si se promete restauración completa, debe existir dump y procedimiento aparte validado por 07. No exportar credenciales ni incluir DSN con contraseña en manifiestos.

### 11.2. Coherencia de extracción

05 implementará exportación de lectura en una vista transaccional coherente o desde un backup consistente. Una colección de consultas en momentos diferentes sin garantía se etiqueta `consistency_unverified`; no se presenta como snapshot atómico. La función `transaction` observada en G3 no garantiza ese aislamiento por sí sola.

Conservar sentencia/proyección y parámetros de extracción sin secretos, versión de base y zona horaria de sesión si afecta serialización. Los registros del lado izquierdo sin match se reportan; no resolver cobertura mediante inner joins que los oculten.

### 11.3. Identificador y manifiesto

`snapshot_id` se asignará solo al material realmente exportado; no se rellena en este borrador. Registrar fecha UTC de extracción, origen lógico no secreto, schema fingerprint, archivos, hashes físicos, hashes lógicos canónicos, licencia y estado de consistencia. La identidad de recurso puede derivarse del hash de un descriptor canónico excluyendo su propio identificador y campos volátiles; algoritmo y versión explícitos.

`templates/run_manifest.json` y `schemas/` son artefactos a crear en 05/07. El manifiesto deberá referenciar versiones de 01–04/04a, configuración efectiva, snapshot, cohortes, OBO, identidad, políticas, perfiles, entorno y código. No se incluyen valores ficticios para que parezca ejecutado.

### 11.4. Licencias y compatibilidad

Cada fuente declarará licencia conocida/desconocida, URL o texto accesible y restricciones de redistribución. «Desconocida» no significa permiso académico asumido. Un recurso puede permitir análisis interno y bloquear publicación del paquete raw hasta aclaración.

Compatibilidad exige: namespaces y ámbitos reconciliables, GO/políticas declarados, release y parser identificables, unidades de conteo y universos consistentes. El mismo nombre de archivo o fecha cercana no acredita compatibilidad. Un perfil preparado con otra política no se reutiliza como F0 sin reidentificarlo.

## 12. Contratos de perfiles estadísticos

Las fórmulas y conversiones a puntuaciones pertenecen a 04. Aquí se fija qué conteos y población deben poder reconstruirse. Los perfiles no almacenan etiquetas negativas ni sustituyen evidencia experimental.

### 12.1. IC: propuesta objetivo y verificación pendiente

Unidad de conteo: entidad proteica reconciliada, no fila, publicación o accession alternativo. Propuesta de universo por aspecto: entidades de la referencia con al menos un término válido seleccionado en ese aspecto. Cada entidad contribuye como máximo una vez por término tras el cierre de referencia autorizado. N por aspecto se conserva junto con marginales y pertenencia de universo.

El cierre propuesto es el positivo de referencia explícitamente versionado; no se asume equivalente al de `goatools.TermCounts`. La documentación de CBBIO y G6 verifican delegación, no el denominador interno. 04 debe inspeccionar dependencia/versiones y demostrar equivalencia con el objetivo. Si difiere, registrar la variante efectiva o aprobar una modificación; no publicar un IC de backend con el denominador de este contrato si no coincide. Esto bloquea aceptar IC/Lin del piloto hasta resolución, no el inventario.

Persistir o permitir regenerar: `profile_id`, snapshot, corpus, universo por aspecto, N, conteos por término, política de evidencia por referencia a 02, política de cierre, OBO, versión de estimador/dependencia, cobertura y checksums. Un término ausente del perfil no se trata como especificidad infinita o cero por defecto.

### 12.2. Coocurrencias interaspecto

Para cada par MF–BP, MF–CC y BP–CC:

- Universo: referencia con al menos un término válido en ambos aspectos, bajo la política del perfil.
- N: entidades únicas de ese universo, antes de filtros de soporte.
- Marginal de cada término: entidades del mismo universo con el término.
- Conjunto: entidades del mismo universo con ambos términos; una contribución por pareja y entidad.
- Parejas por proteína: producto cartesiano de conjuntos preparados, sin duplicación por evidencias.

Los tres universos pueden ser diferentes; guardar los tres, no intercambiar marginales globales entre perfiles. Un universo común de cobertura triple es otra sensibilidad identificada de 02, no una corrección silenciosa.

Persistencia conceptual propuesta:

| Tabla | Clave y campos |
|---|---|
| `profile_manifest` | profile_id; familia; recursos/políticas/versiones; hashes; estados. |
| `profile_universe_members` | profile_id, universe_id, entity_id; inclusión y razón. |
| `profile_universes` | profile_id, universe_id; aspecto/par; N; política de elegibilidad. |
| `profile_term_counts` | profile_id, universe_id, go_id; count entero no negativo. |
| `profile_pair_counts` | profile_id, universe_id, go_x, go_y; joint_count entero no negativo. |

Todos son modelos propuestos, no tablas SQL existentes. Si se omiten ceros en almacenamiento disperso, se exige completitud certificable del conteo: ausencia de clave solo significa cero cuando términos y universo son conocidos y el materializado está completo. Un cache miss o fallo de consulta es desconocido, no cero.

### 12.3. Soporte, cobertura y versiones

04a gobierna umbrales de scoring y casos no estimables. Cambiar umbrales puede reutilizar conteos si no cambia universo/política, pero exige nueva configuración de puntuación. Cambiar referencia, evidencia, identidad, GO, cierre o unidad exige nuevo perfil.

Los perfiles principales se congelan antes de evaluar condiciones y perturbaciones, según 02. La retirada de una publicación de una proteína evaluada no elimina esa publicación de toda la referencia. Sensibilidades que cambian la referencia crean perfiles alternativos y se identifican como tales.

## 13. Tablas de entrada/salida y reconstrucción

### 13.1. Capas de artefactos propuestas

| Capa | Archivos/tablas propuestos | Transformación permitida |
|---|---|---|
| Bruta | `biodata_protein_raw`, `biodata_accession_raw`, `biodata_sequence_raw`, `biodata_go_terms_raw`, `biodata_annotations_raw`, fuentes originales | Serialización sin pérdida y registro de esquema; no limpieza destructiva. |
| Reconciliada | source_records, source_claims, entities, identity_mappings, local_entity_links, referencias y enlaces | Reglas deterministas y crosswalks congelados, con incidencias. |
| Preparada | annotation_dispositions, prepared_terms, term_derivations, cohort_membership | Selección por condición y política, preservando evidencia. |
| Referencia | profile_manifest, universos, miembros y conteos | Conteo coherente y versionado, no evaluación biológica. |
| Calidad | issues, observabilidad, coverage_report, equivalence_report | Contabilidad de cada entrada y resultado de validación. |

No se exportan todas las tablas de estructura/embeddings por defecto; una exportación ampliada tendrá otro alcance de recurso.

### 13.2. Orden de reconstrucción

1. Validar archivos brutos, descriptor y checksums físicos.
2. Validar esquema efectivo y detectar variante; cualquier columna necesaria no exportada es incidencia.
3. Parsear fuentes y referencias preservando cada valor original.
4. Aplicar crosswalk y decisiones congeladas de identidad.
5. Resolver GO y metadatos contra recursos congelados.
6. Aplicar reglas de elegibilidad/positividad y condiciones de 02.
7. Generar términos únicos y derivaciones por condición/política.
8. Derivar universos desde la referencia preparada y contar sin multiplicidad documental.
9. Emitir tablas de cobertura, incidencias y representación canónica de inputs.

No realizar enriquecimiento web durante reconstrucción. Si falta un crosswalk o decisión manual requerida, fallar de forma explícita o excluir la unidad con razón según política; nunca consultar «la última versión» para continuar.

## 14. Demostración de equivalencia de inputs reconstruidos

La equivalencia no se demuestra porque dos ejecuciones produzcan el mismo número de proteínas. Se distinguen:

1. Igualdad de origen: mismos hashes físicos de todos los artefactos raw y recursos.
2. Igualdad de contrato: mismas versiones de schema, políticas, crosswalks, decisiones curatoriales que afecten selección, parámetros y transformaciones.
3. Igualdad lógica: mismos registros tipados, relaciones y multiplicidades en tablas canónicas y preparados, independientemente del orden físico o compresión.
4. Igualdad para el cálculo: mismos conjuntos por entidad/aspecto/condición, mismos miembros de universo y conteos; no solo puntuaciones finales.

### 14.1. Canonicalización propuesta

- Esquema explícito con orden de columnas fijo por versión, tipos y distinción null/string vacío.
- Identificadores normalizados solo conforme a política; Unicode NFC en campos canónicos textuales, conservando raw intacto.
- Enteros sin ceros decimales añadidos; booleanos tipados; fechas/timestamps sin reinterpretar zonas desconocidas; sin NaN en campos enteros o JSON lógico.
- Orden de filas por clave completa y, en empates de bruto, localizador/multiplicidad; no eliminar duplicados para obtener hash igual.
- Arrays de conjuntos ordenados; expresiones con operadores mantienen árbol y semántica.
- Serialización JSON canónica del contrato, UTF-8, claves ordenadas y separadores fijados por versión; una fila tipada por línea con terminador LF. Hash SHA-256 sobre ese flujo. El algoritmo de 05 debe especificar escaping y representación temporal exacta y quedar probado en 07.

Parquet es un formato de almacenamiento propuesto, pero dos archivos equivalentes pueden diferir en bytes por metadatos o compresión. Por ello se conservan hash físico y hash lógico; no se exige byte igualdad de Parquet para demostrar igualdad lógica.

### 14.2. Evidencia exigida a una futura prueba

Reconstruir dos veces desde el mismo paquete congelado en procesos limpios, sin red ni consultas dinámicas, y emitir `equivalence_report`: recursos comparados, versiones, recuentos, claves, hashes lógicos por tabla, conjuntos de términos, universos y conteos. Si falla un hash, producir diff por clave y campo y causa, no solo un booleano.

Criterio propuesto: cero diferencias en las tablas lógicas de input y conteos para una misma versión. Las tolerancias de resultados flotantes pertenecen a 04/07; no se usan para declarar equivalentes identidades o conteos diferentes. Si se renombran IDs de manera isomorfa, eso es otra equivalencia semántica bajo un crosswalk explícito, no igualdad exacta de input.

No se ha realizado esta prueba. El presente documento define cómo demostrarla después.

## 15. Validaciones e incidencias

### 15.1. Severidad y acción

| Nivel | Significado | Acción |
|---|---|---|
| FATAL | Paquete no interpretable: corrupción, schema desconocido, recursos incompatibles o identidad de snapshot no verificable | Bloquear reconstrucción del recurso afectado. |
| ERROR | Unidad ambigua/incoherente: FK rota, identidad conflictiva, aspecto incompatible o conteo imposible | Cuarentena de unidad y bloquear análisis afectado hasta resolución o exclusión explícita. |
| WARNING | Dato limitado pero utilizable para una finalidad: taxonomía ausente, referencia no resuelta, metadata parcial | Mantener, limitar usos y reportar; aprobación explícita si afecta el objetivo principal. |
| INFO | Transformación prevista o resumen: alias resuelto, términos deduplicados | Registrar sin ocultar procedencia. |

Severidad puede ser por fase: falta de referencias puede permitir atlas GO pero bloquear retirada documental. Una excepción no convierte ERROR en dato correcto; registra autorización, razón, alcance y versión.

### 15.2. Reglas mínimas

| ID | Tipo | Comprobación | Severidad/alcance |
|---|---|---|---|
| V01 | Estructural | Tipos, columnas, claves y nulos según variante efectiva | FATAL de recurso si no interpretable. |
| V02 | Referencial | FK y enlaces entity/local/GO/reference válidos; left-unmatched contados | ERROR de unidad. |
| V03 | Identidad | Una resolución aceptada por clave, namespace y ámbito; candidatos preservados | ERROR si ambiguo. |
| V04 | Claims | Cada atribución conserva fuente, record, release y vocabulario original o ausencia explícita | ERROR si se pierde trazabilidad. |
| V05 | GO | IDs, aspectos, obsoletos y reemplazos contra recurso fijado | ERROR de término o WARNING según uso. |
| V06 | Evidencia | Vocabulario 02 y estado de relación/NOT conocido o limitación aprobada | Bloqueo de condición afectada. |
| V07 | Referencias | Parser correcto por formato; alias no duplican artículos; unknown no se presenta como PMID | ERROR para intervención documental. |
| V08 | Duplicación | Filas, términos y entidades diferenciados; no aumento de soporte por aliases | ERROR de conteo; raw se conserva. |
| V09 | Temporalidad | Fecha de anotación distinta de fecha proteína/descarga; corte reproducible | WARNING o bloqueo de análisis temporal. |
| V10 | Perfiles | N y marginales del mismo universo; conjuntos compatibles; conteos no exceden N ni marginales | ERROR de perfil. |
| V11 | Cobertura | Denominadores antes/después por condición/aspecto/métrica visibles; ningún null se convierte en cero | ERROR analítico si oculto. |
| V12 | Integridad | Hashes físicos/lógicos y transformaciones comparables | FATAL si recurso alterado sin nueva versión. |
| V13 | Licencia | Estado y restricciones por recurso | Bloquea redistribución si no autorizada; uso interno según revisión. |
| V14 | Equivalencia | Reconstrucciones iguales según §14 | Bloquea declarar reproducibilidad si falla. |

Para coocurrencias, además de soporte no negativo, intersección no mayor que cada marginal y unión no mayor que N. Los tests concretos y cobertura de casos pertenecen a 07.

### 15.3. Informe de incidencias y cobertura

Cada incidencia incluirá regla/versión, severidad, objeto, valor observado, expectativa, artefacto/localizador, etapa, acción, estado, resolución y validador cuando exista. Los campos sensibles se redactarán sin perder capacidad de diagnóstico.

El informe debe reconciliar número de registros raw con aceptados, excluidos y en cuarentena por unidad y etapa, distinguiendo múltiples motivos de una misma fila. La cobertura se informará sobre corpus inventariado y sobre subconjunto analítico, sin ocultar entidades sin GO. Las tres causas «dato ausente», «no exportado» y «no accesible» se contabilizan separadamente cuando se conocen.

## 16. Ejemplo sintético, no biológico y no ejecutado

Todos los símbolos siguientes son etiquetas abstractas reservadas para explicar el contrato. `SYN_*` no representa accession, PMID, DOI, GO ID, snapshot real ni una secuencia biológica. No son filas aptas para producción ni para el validador de namespaces biológicos.

### 16.1. Fuentes y mapeo

| Registro sintético | Atribución original | Identificador abstracto | Resolución ilustrativa |
|---|---|---|---|
| SYN_RECORD_A | «categoría declarada A» | SYN_ALIAS_OLD | Crosswalk explícito lo vincula a SYN_ENTITY_1. |
| SYN_RECORD_B | «categoría declarada B» | SYN_ALIAS_CURRENT | Mismo destino bajo evidencia de identidad, sin fusionar las categorías. |
| SYN_RECORD_C | «inclusión en catálogo» | SYN_ALIAS_AMBIGUOUS | Dos destinos incompatibles: queda ambiguous, sin elección automática. |

Dos claims distintos siguen siendo dos claims aunque A y B se vinculen a una entidad. C permanece en inventario y fuera del cálculo hasta resolución.

### 16.2. Anotaciones y referencia

| Fila abstracta | Entidad | Término abstracto | Referencia abstracta | Interpretación |
|---|---|---|---|---|
| SYN_ANN_A | SYN_ENTITY_1 | SYN_TERM_X | SYN_REF_ID_A y SYN_REF_ID_B | El formato fuente acredita que ambos IDs son alias del mismo SYN_ARTICLE_1. |
| SYN_ANN_B | SYN_ENTITY_1 | SYN_TERM_X | SYN_ARTICLE_2 | Otro soporte, si la fuente lo acredita. |
| SYN_ANN_C | SYN_ENTITY_1 | SYN_TERM_Y | null | Anotación observada con referencia ausente, no artículo desconocido global. |

El conjunto de términos contiene X e Y una vez cada uno; X no cuenta tres veces por referencias. Retirar SYN_ARTICLE_1 elimina sus dos alias y el soporte de A, pero X puede permanecer por B bajo política aceptada. Si el soporte de B fuera ambiguo, se registra esa limitación; no se fabrica independencia.

Si la entidad pertenece a referencia, cada término cuenta a lo sumo una vez por entidad. El número de claims o alias no cambia los marginales. Este ejemplo no define ninguna puntuación ni demuestra equivalencia computacional: solo ilustra granularidad y preservación de soporte.

## 17. Decisiones, pendientes y criterios de aceptación

### 17.1. Decisiones registradas

| ID | Decisión | Estado |
|---|---|---|
| D03-01 | Separar esquema remoto, testimonio de instalación y snapshot efectivo | VERIFICAT EN CODI para remoto y DOCUMENTAT NO VERIFICAT para instalación; contrato PROPOSTA. |
| D03-02 | Conservar raw, claims y referencias separadas de conjuntos métricos | PROPOSTA coherente con antecedentes. |
| D03-03 | Referencias múltiples se interpretan por formato; GAF referencia única con posibles alias | Fuente primaria P1; aclaración propuesta de 02 §8. |
| D03-04 | Entidad local no es ID global; crosswalk versionado obligatorio | PROPOSTA fundada en G2–G4. |
| D03-05 | Referencia externa congelada preferida; solapamiento interno explícito | PROPOSTA conservada de 02 y borrador 04a. |
| D03-06 | Conjuntos únicos para métricas; soportes completos para auditoría | PROPOSTA; no aprobación formal localizada. |

### 17.2. Pendientes accionables

| ID | Pregunta e impacto | Propuesta provisional justificada | Quién valida | ¿Bloquea? |
|---|---|---|---|---|
| DP-01 | ¿Qué esquema tiene la exportación real y qué versión de cliente la lee? | Exportar descriptor efectivo y comparar con G2/C4, sin migración automática. | Responsable BioData y datos. | Sí para ingesta del piloto. |
| DP-02 | ¿Se ratifica entidad por identidad reconciliada sin colapso automático por secuencia? | Mantener claims/taxones e informar grupos de secuencia, resolver conflicto histórico con S1. | Responsable científico y de datos. | Sí para conteos por entidad. |
| DP-03 | ¿Qué acredita namespace, primarias/secundarias, redirects e isoformas? | Crosswalk versionado, exacto y sin mapeo first match; ambiguos a cuarentena. | Responsable de datos y curación. | Sí para unidades no resueltas; no resto del inventario. |
| DP-04 | ¿Se conservó NOT/relación/assigned_by/extensiones? | Auditar fuente/ingesta; modos de aptitud explícitos de §9.3. | Responsable de ingesta y revisión científica. | Sí para declarar selección estricta; análisis degradado requiere aprobación. |
| DP-05 | ¿Qué significa publication_id y proviene de qué formato? | Parser por fuente; GAF alias de una referencia, otros casos unknown. | Responsable de datos/bibliografía. | No atlas; sí retiro documental. |
| DP-06 | ¿Qué GO, taxonomía y fuentes exactas se congelan? | Recursos identificados con bytes y versión, no «latest». | Responsable científico/datos. | Sí para análisis que los requiera. |
| DP-07 | ¿Qué referencia y solapamientos son viables? | Modo externo preferido; interno solo declarado y revisado. | Responsable científico; coordinación con 02. | Sí para IC/Lin/A aceptadas. |
| DP-08 | ¿TermCounts coincide con unidad, cierre y denominador objetivo? | Verificar dependencia antes de aceptar perfil, documentar variante si diverge. | Responsable de métricas/mantenedor; 04/07. | Sí IC/Lin, no inventario. |
| DP-09 | ¿Se ratifican reglas de reemplazo GO y representación principal? | §9 como propuesta; no usar consider para sustitución automática. | Responsable científico y GO. | Sí preparación comparable. |
| DP-10 | ¿Cómo se calculan IDs y serialización canónica final? | Anclaje/crosswalk estable y hashes lógicos de §14; especificación técnica en 05. | Arquitectura y responsable de datos. | Sí equivalencia exacta; no redacción. |
| DP-11 | ¿Qué licencias permiten redistribución? | Declarar desconocidas, separar uso interno y publicación; no asumir permiso. | Responsable de fuentes y coordinación. | Según recurso/uso. |
| DP-12 | ¿Quién aprueba contrato y excepciones? | Asignar roles y registrar aceptación por bloque, sin personas inventadas. | Coordinación del proyecto. | Sí para declarar piloto autorizado. |

### 17.3. Criterios de aceptación futura

- AC03-01: esquema desplegado/exportado identificado y diferencias con remoto resueltas o limitadas explícitamente.
- AC03-02: cada identificador local tiene ámbito y crosswalk auditable; colisiones no resueltas no cuentan doble.
- AC03-03: todas las atribuciones originales sobreviven con fuente, release y procedencia.
- AC03-04: filas de evidencia, términos únicos y artículos reconciliados no se confunden.
- AC03-05: relación/NOT y otras ausencias tienen observabilidad conocida y uso autorizado.
- AC03-06: GO/políticas/condiciones son reproducibles sin consulta externa dinámica.
- AC03-07: positivo, referencia y reservado tienen pertenencias y solapamientos declarados, sin clase negativa implícita.
- AC03-08: perfiles tienen universos, denominadores y versiones consistentes y verificables contra 04.
- AC03-09: cada pérdida tiene incidencia y el informe reconcilia entradas/salidas.
- AC03-10: dos reconstrucciones cumplen equivalencia lógica exacta de inputs y conteos.
- AC03-11: `schemas/` y `templates/run_manifest.json` se crean y validan antes de usarlos como contratos ejecutables.
- AC03-12: aprobación de responsables documentada; actualmente pendiente.

Estos criterios no se declaran satisfechos por redactar el contrato. Una limitación que afecta a bibliografía no detiene automáticamente la descripción GO; sí impide declarar completada la operación documental afectada.

## 18. Inventario de fuentes y limitaciones

### 18.1. Lectura remota del repositorio

Repositorio: https://github.com/CBBIO/BioData

Commit fijado, recuperado del árbol remoto: https://github.com/CBBIO/BioData/commit/ed073bd4df680a3b45ee69943916e196d28b63b6

Se comenzó por README y árbol raíz; las lecturas siguientes se fijaron al commit. La consulta web de la portada falló, pero la lectura del connector GitHub funcionó. No se presupone rama instalada ni actualización del servidor del usuario.

| ID | Ruta y símbolos/secciones | Estado y alcance |
|---|---|---|
| G1 | [README.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/README.md), What Is In This Repo; Database Setup | DOCUMENTAT NO VERIFICAT: descripción del repositorio, no evidencia de instalación. |
| G2 | [sql/schema.sql](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/sql/schema.sql), CREATE TABLE, PK, UQ, índices y FK de las doce tablas | VERIFICAT EN CODI: esquema leído; no contenido real. |
| G3 | [CBBIO/BioData.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/BioData.py), `BioDataClient.query_all`, `transaction`, `get_protein`, `get_protein_by_accession`, `list_accessions_for_protein`, `get_protein_go_annotations`, `get_protein_species_taxonomy`, `get_protein_sequences` | VERIFICAT EN CODI para símbolos visibles. Respuesta truncada en parte posterior; no se atribuye contenido no leído. |
| G4 | [CBBIO/types.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/types.py), `ProteinID`, `GOAnnotation` | VERIFICAT EN CODI: tipos y campos leídos; str no define namespace. |
| G5 | [docs/BioData.md](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/docs/BioData.md), Proteins and Sequences; GO Annotations; Raw SQL Helpers | DOCUMENTAT NO VERIFICAT para ejemplos. Ejemplos de accession/length no prueban columnas reales en protein; G2/G3 gobiernan esa descripción. |
| G6 | [CBBIO/GO.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/CBBIO/GO.py), `load_go`, `term`, `filter_valid_terms`, `split_annotations_by_category`, `prepare_term_counts`, `find_relation` | VERIFICAT EN CODI: lectura del módulo; delegación a goatools, sin auditoría interna de dependencia. |
| G7 | [tests/test_biodata_integration.py](https://github.com/CBBIO/BioData/blob/ed073bd4df680a3b45ee69943916e196d28b63b6/tests/test_biodata_integration.py), fixture `integration_client`, `test_integration_protein_access_and_sequences`, `test_integration_go_fetch_methods` | VERIFICAT EN CODI: tests leídos, no ejecutados. La fixture permite skip sin entorno o datos; su existencia no acredita validación de publicaciones/procedencia. |

No se inspeccionó íntegramente el código de ingesta ni una migración que explique C4. No se extrapola desde G7 una batería de pruebas ya pasada ni un contrato de referencias que no aparece en el tipo G4.

### 18.2. Documentos y conversación accesibles

| ID | Fuente/localizador legible | Uso y disponibilidad |
|---|---|---|
| S1 | `canonical_multifunctional_protein_data_dossier.md`, versión 1.0, 2026-08-29, resumen y políticas de identidad/releases en historial accesible | Project File localizado y extractos recuperados; declaraciones de implementación no verificadas. No se adoptan automáticamente sus reglas de labels/negativos. |
| S2 | `mfp_bibliographic_catalog_vision.md`, Identity Model; Scientific Interpretation; Target Product; Provenance Requirements | Project File localizado y leído en esta consulta. Catálogo de atribuciones, no clasificador. |
| S3 | `dataset_designer_functional_contract.md`, §§2–6, 8 | Project File localizado y leído. Antecedente de trazabilidad; selección negativa fuera de esta fase. |
| S4 | `Dossier_extensio_PIS_BioData_PEC_v0.1.md`, 2026-10-19, §§3–8 | Adjunto identificado en inventario y contenido accesible en conversación; propuesta, no implementación. |
| C1 | `01_dossier_experimento.md`, v0.1; conversación PEC, solicitud 2026-10-26 21:16 CET | Contenido completo visible en historial. Archivo anterior no recuperado como entrada física; alcance rector, aún borrador. |
| C2 | `02_protocolo_cientifico_y_analisis.md`, v0.1; conversación PEC, solicitud 2026-10-26 22:21 CET | Contenido visible en historial; comparaciones y filtros propuestos, no aprobados. §8 precisa lectura de referencias por formato. |
| C3 | `Especificacion_metricas_asociacion_GO_BioData_v1.1.md`; conversación PEC, solicitud 2026-10-26 13:49 CET | Texto visible en historial; archivo independiente no localizado en las fuentes accesibles actuales. Candidato a 04a, no contrato aprobado. |
| C4 | Salidas `\dt`, `\d protein_go_term_annotation` y documentación API aportadas por usuario, solicitud 2026-10-26 20:56 CET | DOCUMENTAT NO VERIFICAT sobre instalación; contraste con G2 conservado. |
| C5 | Propuestas de experimentación e infraestructura, solicitudes 2026-10-26 20:29 y 20:56 CET | Accesibles en conversación; origen del flujo, no prueba de ejecución. |

Los recuentos de corpus de antecedentes no se usan como tamaños efectivos del snapshot. Las decisiones curatoriales o mapeos históricos de categorías no sustituyen preservación de claims.

PIS figura en S4 como responsable propuesto de adquisición y procedencia; implementación no inspeccionada. BioData tiene cliente y GO verificados estáticamente en G3/G6. mfp-bibliography tiene papel de catálogo documentado en S2 y posible sede experimental propuesta; integración no demostrada. PEC es el marco del proyecto; su clasificador no gobierna este input. No se usan los cuatro nombres como sinónimos.

### 18.3. Fuentes primarias externas consultadas

- P1. Gene Ontology Consortium, «Gene Association File (GAF) format», GAF 2.2, https://geneontology.org/docs/go-annotation-file-gaf-format-2.2/ , consultado 2026-10-26. Campos, cardinalidad y semántica de Reference, Relation, With/From, Taxon, Annotation Extension y Gene Product Form ID.
- P2. Gene Ontology Consortium, «Relations in the Gene Ontology», https://geneontology.org/docs/ontology-relations/ , consultado 2026-10-26. Diferencia de is_a, part_of, has_part y regulates para agrupación.
- P3. UniProt, «Accession», https://www.uniprot.org/help/accession_numbers , contenido recuperado por búsqueda 2026-10-26. Primarias/secundarias, fusiones y separaciones; sin resolver accessions concretas del corpus.
- P4. UniProt, «Alternative products», https://www.uniprot.org/help/alternative_products , contenido recuperado por búsqueda 2026-10-26. Identificadores específicos de isoforma; sin inferencia sobre registros no consultados.

No se inventan PMID ni DOI. No se ha leído literatura biológica específica de las proteínas ni ejecutado validación de identidad con servicios externos.

### 18.4. No accesible, no exportado y desconocido

Base real y datos: NO ACCESSIBLE. Snapshot y manifiestos reales: no aportados ni generados. Repositorio de ingesta PIS e integración remota mfp-bibliography: no inspeccionados. Archivos formales 04–07 y 04a con esos nombres: no localizados en las fuentes accesibles. `schemas/` y `templates/run_manifest.json` del experimento: a crear, no se afirma existencia. Código interno/versiones efectivas de goatools y algoritmo local de sequence_hash: pendientes de verificación.

«No exportado» solo se usa si se acredita que el campo existe en origen y se omitió de la proyección; «no accesible» cuando no se ha podido comprobar; «ausente en esquema remoto» solo para G2. Ninguna de estas etiquetas demuestra inexistencia global de información en el laboratorio.

## 19. Dependencias y comprobación final de coherencia

| Documento | Relación con este contrato |
|---|---|
| [01_dossier_experimento.md](01_dossier_experimento.md) | Mantiene alcance positivo y tres conjuntos con funciones distintas; no se crean negativos. |
| [02_protocolo_cientifico_y_analisis.md](02_protocolo_cientifico_y_analisis.md) | Gobierna filtros/listas y perturbaciones; 03 aporta soporte reconstruible, universos y aclaración específica de GAF Reference. Cualquier ajuste se registra, no se presupone aprobado. |
| [04_especificacion_metricas.md](04_especificacion_metricas.md) y candidato [04a_asociaciones_interaspecto.md](04a_asociaciones_interaspecto.md) | Reciben conteos, universos y estados; gobiernan fórmulas, agregación y umbrales. Deben verificar coincidencia de backend IC y relaciones. |
| [05_diseno_tecnico.md](05_diseno_tecnico.md) | Implementará formatos, exportación coherente, IDs, canonicalización y manifiestos sin cambiar semántica. |
| [06_manual_revision_bibliografica.md](06_manual_revision_bibliografica.md) | Valora evidencia y categorías; 03 conserva claims/referencias sin asignar certeza automática. |
| [07_plan_implementacion_y_validacion.md](07_plan_implementacion_y_validacion.md) | Implementará pruebas de FK, identidad, conteos, pérdida y equivalencia; aquí no se declara ninguna superada. |

Los enlaces son destinos documentales del paquete, no prueba de archivos aprobados. Comprobación final: este contrato no cambia el objetivo de 01, no duplica el análisis de 02, no fija fórmulas de 04, no sustituye arquitectura de 05, curación de 06 ni ejecución de pruebas de 07. Define una propuesta operativa para reconstruir inputs a partir de recursos idénticos y documenta los pendientes que impiden aceptar determinados bloques, sin bloquear la redacción del resto.
