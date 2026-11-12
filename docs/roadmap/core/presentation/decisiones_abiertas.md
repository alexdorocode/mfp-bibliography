# Decisiones que siguen abiertas — Resumen

Companion de `propuesta_investigacion.pptx` / `.pdf`.
Fuente: [`guion_propuesta.md`](guion_propuesta.md) (v0.4) — Decision Register, backlog de apoyo y preguntas de revisión por slide.
Estado: propuesta de trabajo; nada de lo listado está aprobado todavía.

## Decisiones metodológicas (Decision Register del guion)

| ID | Decisión por cerrar | Propuesta actual |
|---|---|---|
| DEC-01 | Medidas B3 | `1 − Wang`, `1 − Lin`, MBL; GeOKG-GO como extensión condicionada (definir dominio, dirección, IC y errores) |
| DEC-02 | Resumen principal B3 | Máximo por proteína con todos los pares empatados; media solo como descriptor secundario; sin score compuesto |
| DEC-03 | Criterio de extremo | Referencia predefinida por métrica, fijada antes de inspeccionar TargetData |
| DEC-04 | Complementariedad | Correlación de rangos (p. ej. Spearman) y overlap como análisis separados; baja correlación ≠ independencia |
| DEC-05 | Medida de asociación B4 | Una medida establecida (p. ej. NPMI u otra publicada); ninguna fórmula propia; documentar dirección, dominio, soporte y casos límite |
| DEC-06 | Variantes de evidencia | Misma definición de asociación bajo EEC y ALL, con reference profiles identificados |
| DEC-07 | Hipótesis direccional B4 | Menor asociación promedio MF–CC para la función moonlighting; solo en el subconjunto con roles respaldados por evidencia independiente |
| DEC-08 | Muestra BioData (B5) | Matching por taxonomía, longitud y carga de anotación — nunca sobre los outcomes B3/B4; balance, tamaño y solapamiento documentados |
| DEC-09 | Corpus IC y perfiles | Separar sensibilidad de anotaciones y de perfiles; identificadores y reglas congelados |
| DEC-10 | GeOKG | Extensión condicionada a superar P03–P05 |
| DEC-11 | Curación y visualización | Versionar la curación; diferir PCA/UMAP 3D hasta tener baseline reproducible |

## Pendientes operativos (P01–P12 del guion; no son issues de GitHub)

- **P01/P02** — Acceso QuickGO y referencias vía CBBIO; evidencias, calificadores e identificadores preservados (habilita B1/B2/B4/B6).
- **P03–P05** — Cadena GeOKG: integración en PIS → consulta de term embeddings en CBBIO → distancias validadas.
- **P06/P07** — Estados auditables (ausencias ≠ cero), agregación de pares, máximos y correlaciones.
- **P08** — Perfiles de asociación MF–MF y MF–CC EEC/ALL (mecanismos generales en CBBIO; contrastes en la capa experimental).
- **P09** — Referencia y matched sampling en B5.
- **P10** — Roles y curación independiente (mfp-bibliography + revisión).
- **P11** — Run manifests y releases.
- **P12** — PCA y UMAP 3D (diferido).

## Datos y definiciones por consignar antes del piloto

- Identificador y fecha de snapshot para los recuentos de TargetData (2.182 / 9.376 / 96.186 / 2.451 / 25.265) y para BioData.
- Versión desplegada de PIS y CBBIO que constituye el baseline técnico.
- Cobertura analítica real de TargetData (≥ 2 MF elegibles, CC, referencias) — coverage audit de B1.
- Políticas de calificadores, propagación y relaciones GO para EEC y ALL.
- Sequence embedding (modelo y pooling) y capa de color prioritaria para las extensiones 3D.
