# 🔥 HALLAZGOS FASE II RECUPERADOS — Lectura OBLIGATORIA antes de procesar proyectos

**Fecha de recuperación:** 2026-05-06
**Origen:** Screenshots de la sesión Discovery Forense Fase II del 2026-05-05 (Manus 1.6 Max, Hilo B - Catastro) que se perdieron por compactación de contexto y fueron recuperados por Alfredo enviando 18 imágenes.
**Estado:** Información validada, integrada y canónica. Estos datos sobreescriben cualquier suposición previa.

---

## 0. Por qué este documento existe

Durante la Fase II Discovery Forense (5 mayo 2026), Manus generó hallazgos críticos que NO quedaron persistidos en el repo. La compactación de contexto los borró de la memoria activa. Alfredo conservó screenshots y los reinyectó al hilo el 6 de mayo. Este documento canoniza esos hallazgos.

**Si Cowork procesa cualquier proyecto sin leer esto, va a operar con información obsoleta o incompleta.**

---

## 1. El Documento Maestro oficial es el MAOC en Notion

**Confirmado por título y por cross-reference en 3 fuentes (Notion, Drive, Dropbox):**

| Atributo | Valor |
|---|---|
| Título canónico | 📕 MAOC – Documento Maestro |
| Plataforma primaria | Notion |
| Mirror Drive | `documento_maestro_v1.md` |
| Sub-versión Notion | `MAOC INTEGRADO - Hilo 5 Feb 2026` |
| Mirror histórico | `Proyecto Fernando Salvador` (contiene MAOC Doc Maestro) |
| Acción para Cowork | Marcarlo como SSOT absoluto en TODOS los prompts maestros |

---

## 2. Las 8 páginas Notion raíz canónicas

Estas son las páginas que Cowork debe conectar al "Mounstruo Cowoork" como contexto base:

| # | Título | URL Notion |
|---|---|---|
| 1 | Plan de Construcción El Monstruo v0.1 | `notion.so/30114c6f8bba81...3d` |
| 2 | Biblia de MCPs para El Monstruo v1.0 | `notion.so/30214c6f8bba81...c6` |
| 3 | Dashboard Sistema Absorción | `notion.so/33a14c6f8bba81...d9` |
| 4 | MAPA INFINITO Roadmap EPIA-SOP | `notion.so/2ec14c6f8bba81...4a` |
| 5 | epia.mx | `notion.so/33814c6f8bba81...e` |
| 6 | Comando Electoral Mérida 2027 | `notion.so/33714c6f8bba81...f5` |
| 7 | MAOC INTEGRADO - Hilo 5 Feb 2026 | `notion.so/2ff14c6f8bba81...4` |
| 8 | Proyecto Fernando Salvador (contiene MAOC Doc Maestro) | `notion.so/2cb14c6f8bba81...02` |

**URLs completas pendientes:** quedaron truncadas en los screenshots. Cowork puede recuperarlas vía `manus-mcp-cli tool call notion-search` con los títulos exactos.

---

## 3. Asimetría SOP/EPIA Drive vs Dropbox

**Hallazgo más importante de la Fase II.** Las dos fuentes están desincronizadas y cada una tiene la versión más completa de un documento distinto.

| Documento | Más completo en | Razón cuantitativa |
|---|---|---|
| **SOP Fundacional v1.2** | **Drive** (`SOP_v1.2_DRIVE.md`, 43KB) | 196 tokens únicos exclusivos en Drive vs 2 en Dropbox. Drive incluye glosario operativo cuantificable, meta-principio resolución conflictos, ciclo de vida normas, protocolo deliberación multi-sabio. |
| **EPIA Fundacional v1.0** | **Dropbox** (`EPIA_FUNDACIONAL_DBX.docx`, 30KB+) | 286 tokens únicos exclusivos en Dropbox vs 8 en Drive. Dropbox incluye capas funcionales del ecosistema, distinción Manus motor vs Sabios deliberación, núcleo vs periferia, destino final. |

**Diff semántico ya ejecutado:** `discovery_forense/sop_epia_diff/` (commit `38664dc`).

**Conclusión accionable para Cowork:**
- Cuando necesite SOP canónico → leer Drive `SOP_v1.2_DRIVE.md`
- Cuando necesite EPIA canónico → leer Dropbox `EPIA_FUNDACIONAL_DBX.docx`
- **Nunca asumir que Drive y Dropbox tienen la misma versión.** Hay drift.
- Después de la canonización Fase III, sincronizar ambas fuentes.

**Pares EQUIVALENTES (no requieren acción):**
- Genealogía SOP/EPIA v2 (sim 1.000)
- SOP+EPIA Reestructuración 6 Sabios (sim 1.000)

---

## 4. El "Agujero Negro": biblias_v41_AUDITED_69_gradeA.zip

**Este es un paquete crítico aún no procesado.**

| Atributo | Valor |
|---|---|
| Ubicación | Google Drive |
| Contenido | 69 herramientas/biblias auditadas calificadas grade A |
| Estado | Sin descomprimir, sin indexar, sin poblar en Supabase/Notion |
| Prioridad | 🔴 ALTA — Cowork debe procesarlo en Fase III Tarea 1 |
| Acción | Descomprimir → indexar → poblar en Notion como base consultable + en Supabase para semantic search |

**Recomendación operativa para Cowork (de la propia Fase II):**
> "Descomprimir las 69 biblias del ZIP y poblarlas en Supabase/Notion como base consultable."

---

## 5. CRISOL/Mena Baduy estuvo escondido en S3

**Resuelto.** Los planes maestros de CRISOL no estaban en Drive ni en Notion sino en buckets S3:

| Documento | Bucket S3 |
|---|---|
| `PLAN_MAESTRO_ESTRATEGICO_v2.md` | `operacion-doble-eje` |
| `PLAN_DEFINITIVO_REAL_CRISOL8.md` | `crisol8-analysis` |
| `ADDENDUM_v3.1_CRISOL8.md` | `crisol8-analysis` |

**Estado actual:** Migrados al repo `crisol-8` (Tarea 2b cerrada el 5 mayo 2026, commits `97341df` + `f7d9c9c`). Cowork puede acceder vía `gh repo clone alfredogl1804/crisol-8`.

---

## 6. Versiones formalizadas en Dropbox que NO están en Drive

| Documento | Solo en Dropbox |
|---|---|
| `ENTREGABLE 2 — DOCUMENTO FUNDACIONAL SOP.docx` | ✅ |
| `EPIA — DOCUMENTO FUNDACIONAL MAESTRO.docx` | ✅ |

Ambos ya están normalizados a `.md` en `discovery_forense/raw_text/dropbox/normalized_md/`.

---

## 7. Proyectos: correcciones a la categorización inicial

### BioGuard — NO es nominal, es proyecto activo
| Atributo | Valor |
|---|---|
| Definición canónica | "App + dispositivo para detección rápida de drogas en muestras biológicas (saliva, hisopo dérmico, opción sangre capilar). Objetivo: prototipo de diagnóstico semicuantitativo para consumo/revisión clínica." |
| Categoría correcta | 🟠 En Diseño (definición clara, sin spec/roadmap operativo) |
| Documentos donde aparece | `02_CLAUDE_AUDITORIA.md`, `02a_CLAUDE_PARTE1.md`, `repaldo sop v3 181025.txt`, `MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md` |
| Cobertura Drive | 4 archivos / 1 plan-like (solo SOP) |
| Cobertura Notion | 43 páginas / 0 plan-like dedicado |

### Top Control PC (= CONTROL TOTAL) — Tracción reciente
| Atributo | Valor |
|---|---|
| Categoría correcta | 🟢 Activo/Core |
| Roadmap activo | ROADMAP_MUNDIAL_V2_CRUCE + ROADMAP_MUNDIAL_V3_DEFINITIVO (ambos con fecha 2026-04-25) |
| Spec maestro | `Arquitectura de Absorción Soberana v2026-04-05 (GPT-5.4)` |
| Cobertura Drive | 39 archivos / 8 plan-like |
| Cobertura Notion | 29 páginas / 2 plan-like |

### Marketplace Muebles — Tiene specs reales
| Atributo | Valor |
|---|---|
| Spec en Drive | `missoni_master_plan` |
| Spec en Notion | `Casa Bosques Catálogo Proveedores v2.0` |
| Cobertura Drive | 11 archivos / 2 plan-like |
| Cobertura Notion | 24 páginas / 2 plan-like |

### Vivir Sano — Fuerte en Notion (no débil)
| Atributo | Valor |
|---|---|
| Categoría correcta | 🟠 En Diseño con foco fuerte |
| Páginas plan-like en Notion | 6 (DOCUMENTO DEFINITIVO, Arquitectura Absorción Soberana, M4 Aspirantes y Candidatura, Biblia v4.1 Meta AI Assistant) |
| Spec central | "Biblia v4.1 Meta AI Assistant" |
| Cobertura Notion | 42 páginas / 6 plan-like (más que cualquier otro proyecto en Notion) |

### Paquete Like + Skills/Etapas — Interconectados con El Monstruo
Comparten roadmap del Monstruo: `ROADMAP_MUNDIAL_V3_DEFINITIVO.md` y `PLAN_DEFINITIVO_MONSTRUO_V4.md`. No procesar estos proyectos sin contexto del Monstruo madre.

---

## 8. Top 30 documentos magna confirmados (P0 vigente)

Estos son los 30 documentos que Cowork debe priorizar en Fase III Indexación:

| # | Documento | Fuente | Contenido |
|---|---|---|---|
| 1 | Plan de Construcción: El Monstruo v0.1 | Notion | Plan magna v0.1 |
| 2 | repaldo sop v3 181025.txt | Drive | SOP v3 bruto |
| 3 | Biblia de MCPs para El Monstruo v1.0 | Notion | Inventario maestro MCPs |
| 4 | EPIA_fundacional_completo_v1 | Drive | EPIA fundacional |
| 5 | Arquitectura de Absorción Soberana — Versión Definitiva (GPT-5.4) | Notion | MASTER PLAN firmado |
| 6 | Identidad_del_Monstruo_fundacional_v1 | Drive | Documento fundacional |
| 7 | A_respaldo_bruto_chat | Drive | Respaldo bruto de chat |
| 8 | ENTREGABLE 2 — DOCUMENTO FUNDACIONAL SOP.docx | Dropbox | SOP fundacional en DBX |
| 9 | MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md | Drive | Corpus completo |
| 10 | biblias_v41_AUDITED_69_gradeA.zip | Drive | 69 biblias grade A (AGUJERO NEGRO) |
| 13 | 00_PROMPT_PROGRAMATICO_DEFINITIVO.md | Drive | Prompt definitivo |
| 14 | 06_PROMPT_DEFINITIVO.md | Drive | Prompt continuidad |
| 17 | SOP_fundacional_v1.2 | Drive | SOP v1.2 con 6 cambios auditoría |
| 20 | 📕 MAOC — Documento Maestro | Notion | El Documento Maestro oficial |
| 21 | 04_Identidad_del_Monstruo_fundacional_v1.txt | Drive | Versión TXT fundacional |
| 22-25 | BIBLIA_MANUS_IMPLEMENTACION_v1/v2.md | Drive (4 copias) | Biblia de ingeniería |
| 27-28 | DOCUMENTO_DEFINITIVO_HILO_HISTORICO_25-26_ABR_2026.md | Drive (2 copias) | Diario "El Día que las IAs Dejaron de Ser Herramientas" |
| 29 | EPIA — DOCUMENTO FUNDACIONAL MAESTRO.docx | Dropbox | EPIA en Dropbox |
| 30 | GENEALOGIA_SOP_EPIA_v2.md | Drive | Mapa genealógico |

**Riesgo de versiones:** El SOP tiene v1.2 (Drive con 6 cambios), v3 bruto del 18 oct 2025 (Drive), Documento Fundacional Maestro (Dropbox). **Hay riesgo de conflicto entre versiones — requiere dedupe con GPT-5.4.**

**Dedupe pendiente:** BIBLIA_MANUS_IMPLEMENTACION_v2 aparece 3 veces; DOCUMENTO_DEFINITIVO_HILO_HISTORICO 2 veces.

---

## 9. Volumen procesado en Fase II

| Métrica | Fase I | Fase II Forense |
|---|---|---|
| Fuentes barridas | 3 | 6 (+S3, +Dropbox, +Asana) |
| Items únicos | 290 | 1,562 (5.4× más) |
| Documentos P0 detectados | ~25 | 325 |
| Documentos abiertos semánticamente | 0 | 30 |

**Reporte forense completo disponible en:** `discovery_forense/REPORTE_FORENSE_MAGNA.md`
**Artifacts JSON:** `phase6_top50.json` (34 KB), `phase6_consolidated.json` (685 KB)

---

## 10. Qué falta (no es trabajo de Manus)

| Pendiente | Owner | Bloqueado por |
|---|---|---|
| Conectar "Mounstruo Cowoork" a las 8 páginas raíz Notion (sección 2 de este doc) | Tú (Alfredo) | -- |
| Push CRISOL al repo `crisol-8` | Cowork | ✅ Ya cerrado el 5 may (commits `97341df` + `f7d9c9c`) |
| Descomprimir `biblias_v41_AUDITED_69_gradeA.zip` y poblar en Supabase/Notion | Cowork | -- |
| Deduplicar SOP/EPIA Drive vs Dropbox usando GPT-5.4 | Cowork | -- |
| Marcar MAOC en Notion como SSOT en todos los prompts maestros | Cowork | -- |

---

## Cómo Cowork debe usar este documento

1. **Antes de cualquier tarea sobre proyectos**, lee este archivo
2. **Antes de procesar SOP o EPIA**, verifica en sección 3 cuál es la fuente canónica para ese documento específico
3. **Antes de marcar un proyecto como "nominal"**, verifica en sección 7 si tiene definición técnica recuperada
4. **Antes de indexar el corpus**, prioriza los 30 documentos de la sección 8 + el ZIP de la sección 4

— Manus (Hilo B - Catastro)
