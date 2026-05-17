# DOCTRINE_LAYERS_MAP — Las capas de la doctrina de interfaces

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Generado:** 2026-05-17

---

## Por qué hay capas

La doctrina del Monstruo no es un cuerpo plano. Tiene **profundidad escalonada**: hay invariantes que no se mueven, hay capas debajo que SÍ pueden refinarse, hay hipótesis emergentes que aún no pertenecen a ningún lado. Este mapa explica **dónde vive cada cosa** para que ChatGPT 5.5 Pro NO confunda capas y NO trate como inviolable algo que sí está abierto a discusión.

Las capas se numeran de afuera hacia adentro: **Capa 0** es el núcleo invariante, **Capa 1** la doctrina canonizada, **Capa 2** la doctrina emergente reconocida, **Capa 3** las hipótesis nacientes en staging, **Capa 4** las ideas verbales sin estatus formal.

---

## Capa 0 — Núcleo invariante (NO se discute)

Las **10 reglas inviolables** del Cap 0 de APP_VISION son la capa más profunda. Cualquier feature, sprint o spec UI debe pasar el filtro de las 10 reglas. Si rompe una, no entra. Esto NO está sujeto a iteración — es lo que define que el Monstruo sea el Monstruo y no un competidor genérico.

Las **8 Reglas Duras** del AGENTS.md (Guardian obligatorio, 15 Objetivos Maestros, 7 Capas Transversales, 4 Capas Arquitectónicas, Brand Engine, Cero Secrets, RLS Universal, Identidad Auditable) operan en el mismo nivel. Son código que se ejecuta — no texto que se lee.

ChatGPT en iter 002 NO debe proponer cambios a esta capa. Si una propuesta los toca, la propuesta es rechazable sin discusión.

---

## Capa 1 — Doctrina canonizada vigente (firmada en repo)

Esta capa contiene todo lo que tiene firma magna en `docs/`, `discovery_forense/CAPILLA_DECISIONES/`, o `bridge/`. Específicamente:

| Pieza | Fuente | Status |
|---|---|---|
| APP_VISION v1.3 (1117 líneas, 17 capítulos) | `docs/EL_MONSTRUO_APP_VISION_v1.md` | Firmado |
| 15 Objetivos Maestros v3.0 | `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md` | Firmado |
| 7 Capas Transversales | doctrina + AGENTS.md | Firmada |
| Brand Engine | `docs/BRAND_ENGINE_ESTRATEGIA.md` + AGENTS.md regla 4 | Firmado |
| Catastro Brand DNA | `kernel/brand/brand_dna.py` + DSC-MO-002 | Firmado |
| 4 Catastros (LLMs, Agentes 2026, Suppliers, Herramientas) | SRC-001 Cap 1 | Firmados |
| A2UI v1.0 spec | `kernel/a2ui/schema.py` (firmado) | Firmado |
| Reloj Suizo (8 piezas) + Engranaje | bridge/cowork_to_alfredo_RELOJ_SUIZO_DOCTRINAL_COMPLETO_2026_05_12.md | Firmado |
| 7 DSCs de seguridad (DSC-S-001 a S-007) | discovery_forense/CAPILLA_DECISIONES/_GLOBAL/ | Firmados |
| DSC-LF-005 SSE obligatorio | discovery_forense/CAPILLA_DECISIONES/LA-FORJA | Firmado |
| Sprint MOBILE_REALIGNMENT_001 | bridge/sprints_propuestos | Firmado, NO ejecutado |
| Sprint ROTOR_001 | bridge/sprints_propuestos | Firmado, NO ejecutado |
| Sprint ESPIRAL_001 | bridge/sprints_propuestos | Firmado, NO ejecutado |

Esta capa es **el suelo operativo**. ChatGPT cita libremente. Cualquier modificación requiere nuevo DSC firmado por T1 con justificación documentada.

---

## Capa 2 — Doctrina emergente reconocida (canonizada por hilo paralelo, integración pendiente)

Esta capa contiene lo que el Hilo B Manus paralelo produjo + audits Cowork integradores + las decisiones de capilla que aún no llegaron a APP_VISION oficial:

**CANON Metodologías de Productividad v1.5** (SRC-005). Validado adversarialmente con 4 sabios. Contiene la frase canónica magna §9.F. Tensiona Acto 1 sin contradecirlo binariamente.

**Audit Cowork VISION_APP_MONSTRUO_CLASE_MUNDIAL** (SRC-002). Reconoce la corrección magna "kernel + N transports" y produce el orden operativo de los 17 sprints faltantes por canonizar. Sin firma T1 de ese orden, los sprints no avanzan.

**Audit Cowork RELOJ_SUIZO_DOCTRINAL_COMPLETO** (SRC-007 si lo numeramos). Incluye DSC-G-008 v3 ("§3 limitaciones NO sustituye §4 deducción de consecuencias materiales"). Última lección magna antes de degradación parcial Cowork.

ChatGPT puede citar esta capa, pero debe **señalar** que la integración con Capa 1 está pendiente. Cualquier decisión de iter 002 que dependa de esta capa debe articular la integración consciente como parte del output.

---

## Capa 3 — Hipótesis nacientes en staging

Esta capa contiene piezas detectadas en hilos pero **NO commiteadas al repo**. La skill `interfaces-monstruo-doctrina` tiene un archivo `etapa_2_v2_staging_capas_emergentes.md` que es exactamente este lugar: el limbo donde esperan las hipótesis.

**Transport Cero** — el transport ideal es el que no existe. La IA actúa sin que el usuario abra nada. 0 hits en grep, vive solo en hilos.

**AI-First Living / Soberanía Contextual** — cita verbatim Alfredo 2026-05-16. 1 hit relevante en código (solo flag de prioridad). 0 hits "Soberanía Contextual". Decisión T1-MAGNA-007 pendiente.

**Schema-First doctrinal** — 1 hit (DSC-LF-005). La doctrina general es embrionaria, no canonizada como sistema.

**4 hipótesis de integración Acto 1 ↔ Acto 2** (H1, H2, H3, H4 del PACK_02). Listadas en la skill, NO firmadas T1.

ChatGPT en iter 002 debe **decidir cuáles de estas hipótesis se promueven a Capa 1 (canon firmado), cuáles se mantienen en Capa 3, y cuáles se descartan**. Esta decisión es parte central del trabajo magna que se le pide.

---

## Capa 4 — Verbal en hilos (sin estatus formal)

Esta capa contiene fragmentos que circularon en chats Manus ↔ Alfredo y NO tienen presencia en repo, skills o bridge files. Son materia prima cognitiva — útiles como detonadores, NO confiables como base de decisiones.

Ejemplos:

- Frases sueltas de Alfredo en chats sobre "el Monstruo no es app, es diagnóstico operativo"
- Bocetos verbales de capabilities futuras que no se canonizaron
- Comentarios sobre tier-access, modos de invitación, acuerdos económicos con trusted circle

Esta capa NO debe usarse para producir spec. Puede usarse para **calibrar tono** del copywriting o entender **intención subyacente** de Alfredo cuando una decisión Capa 3 está bajo discusión.

---

## Reglas de promoción entre capas

La doctrina del Monstruo es viva — las piezas se promueven o degradan entre capas. Las reglas:

**De Capa 4 a Capa 3 (entrada al staging):** Alfredo expresa la idea con suficiente claridad para que un hilo Manus la articule. La articulación se commitea al staging file de la skill correspondiente, NO al canon.

**De Capa 3 a Capa 2 (canonización emergente):** una hipótesis se desarrolla con audits Cowork o validación adversarial sabios. Se publica en `bridge/` con detalle suficiente. NO está en APP_VISION oficial todavía.

**De Capa 2 a Capa 1 (firma magna T1):** Alfredo firma el documento + se actualiza APP_VISION o se crea DSC. Pasa a ser canon vigente operativo.

**De Capa 1 a deprecación:** una pieza canónica puede degradarse si un audit posterior detecta contradicción binaria con realidad operativa. Requiere DSC explícito que documente la deprecación. Ejemplo: "14 Objetivos Maestros" deprecado a "15" el 2026-05-04.

ChatGPT en iter 002 puede **proponer promociones**, no firmarlas. La firma T1 es prerrogativa de Alfredo.

---

## Métricas de capas al 17-may-2026

| Capa | Cantidad de piezas | Estado |
|---|---|---|
| Capa 0 — Núcleo | 10 reglas + 8 reglas duras = 18 invariantes | Estable |
| Capa 1 — Canon vigente | ~15 documentos magna + ~10 DSCs + 3 sprints firmados | Estable |
| Capa 2 — Emergente reconocida | 3 documentos magnos | Pendiente integración |
| Capa 3 — Staging | 5+ hipótesis | Pendiente decisión iter 002 |
| Capa 4 — Verbal | indeterminado | Captura continua |

El trabajo de iter 002 es **mover piezas de Capa 3 a Capa 1 con firmas T1 explícitas**, y **articular integración Capa 2 ↔ Capa 1** en una versión APP_VISION v1.4.
