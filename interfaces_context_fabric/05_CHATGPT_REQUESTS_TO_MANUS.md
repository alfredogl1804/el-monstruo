# 05 — Requests de ChatGPT a Manus

**Generado:** 2026-05-17
**Iteración:** 001 v2 (post-prompt consolidado v2)
**Propósito:** registrar bidireccionalmente cada solicitud que ChatGPT 5.5 Pro envió a Manus, su estado de ejecución, y los entregables producidos.

---

## REQ-001 — Construcción del Context Fabric iter 001

**Recibido:** 2026-05-17 (prompt INTERFACES-CONTEXT-FABRIC-001)
**Estado:** ✅ COMPLETADO
**Branch:** `interfaces-context-fabric-001` en `alfredogl1804/el-monstruo`
**Commit:** `12fb4372`

**Entregables:**
- 12 context_packs (PACK_00 a PACK_11)
- 9 maps estructurados
- 02_SOURCE_LEDGER.jsonl (33 SRCs)
- 01_CONTEXT_INDEX.md
- 00_START_HERE_FOR_CHATGPT.md
- 3 prompts (Cowork audit + Perplexity research + ChatGPT iter 002)
- ITERATION_001_REPORT.md
- fabric_grep.sh + fabric_grep_results.md (1442 líneas)

---

## REQ-002 — Preservar checkpoint anti-compactación pre-IA como DRAFT

**Recibido:** 2026-05-17 (paste directo a Manus, antes del cierre del bloque pre-IA)
**Estado:** ✅ COMPLETADO
**Reglas aplicadas:** EN EXTRACCIÓN T1, NO CANONIZAR, NO CERRAR PACK_11, NO EJECUTAR PROMPTS PARCIALES

**Entregables:**
- `interfaces_context_fabric/raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md` (393 líneas — verbatim + anexo metodológico)
- `interfaces_context_fabric/raw_rescues/README.md` (5 reglas operativas inviolables)
- `interfaces_context_fabric/context_packs/PACK_11_ORIGEN_PRE_IA_ONTOLOGIA_ALFREDO.md` (DRAFT, NO canonizado)

**Esperando:** instrucción literal `CIERRE BLOQUE PRE-IA` de Alfredo

---

## REQ-003 — Audit D0 EXISTING DESIGN COVERAGE para Legado Familiar

**Recibido:** 2026-05-17 (corrección metodológica de Alfredo + adjunto pasted_content_4.txt)

> *"Corrección metodológica: No diseñar nuevas capas desde señales T1 sin mapear primero contra producción/código/sprints/canonizados/no canonizados."*

**Estado:** ✅ COMPLETADO
**Tiempo de ejecución:** ~30 minutos (incluyendo corrección de bug match-explosion v1→v2→v3)

**Entregables:**
- `interfaces_context_fabric/scripts/d0_legacy_audit_v3.sh` (script reproducible)
- `interfaces_context_fabric/reports/d0_legacy_audit_v3.md` (output bruto, 874 líneas, 64 KB, 53 keywords en 4 secciones)
- `interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md` (matriz canónica de cobertura)
- `interfaces_context_fabric/context_packs/PACK_12_LEGADO_FAMILIAR_EXISTING_AUDIT.md` (análisis específico)
- `interfaces_context_fabric/03_GAPS_AND_UNKNOWN_UNKNOWNS.md` (registro de gaps + unknown unknowns)
- `interfaces_context_fabric/05_CHATGPT_REQUESTS_TO_MANUS.md` (este archivo)

**Conclusión vinculante:** las 3 propuestas (Cronista Familiar, Herencia Narrativa, Legacy Capture) son `NO_EXISTE` o `NO_EXISTE_EN_SENTIDO_T1`. Hay 3 puntos de anclaje existentes (Cronos `EXISTE_PARCIAL`, Memento `EXISTE_PLENO`, el-mundo-de-tata `EXISTE_DISTINTO_PROPÓSITO`) que requieren decisión humana sobre relación topológica antes de canonizar.

---

## Lecciones operativas extraídas

### L-001 — Match-explosion en grep recursivo

Al ejecutar grep recursivo sobre repos grandes, **siempre usar scopes positivos (whitelist) en vez de exclusiones (blacklist)**. La exclusión `--glob '!node_modules'` falla en `node_modules` anidados y produce archivos de 45+ GB en segundos. v3 del script usa whitelist y termina en 8 segundos.

### L-002 — rg respeta `.gitignore` silenciosamente

`ripgrep` respeta `.gitignore` y `.ignore` por defecto. Si un repo tiene reglas amplias, rg puede dar 0 hits cuando grep clásico encuentra cientos. Para audits **forenses**, usar grep clásico o `rg --no-ignore`.

### L-003 — Falsos positivos semánticos

Buscar "legado" trampea con "delegado". Buscar "herencia" trampea con "tabla heredada SQL". Buscar "legacy" trampea con "auth legacy". Para señales T1 humanas, **siempre validar contexto de cada hit antes de contarlo como cobertura.**

### L-004 — Regla "primero buscar, después diseñar"

La corrección metodológica de Alfredo del 2026-05-17 establece un **gate operativo permanente**: ninguna señal T1 nueva entra como diseño hasta pasar por `EXISTING_DESIGN_COVERAGE_MATRIX`. Aplica retroactivamente a todas las propuestas de capas/módulos/sprints futuras.

---

## REQ-004 — Expansión iter 001 v2 con prompt consolidado

**Recibido:** 2026-05-17 (`pasted_content_5.txt` — prompt INTERFACES-CONTEXT-FABRIC-001 v2 consolidado)
**Estado:** ✅ COMPLETADO

**Corrección crítica recibida:**

> *"‘Crónica Familiar / Herencia Narrativa / Legacy Capture’ NO son capas nuevas. Son aliases T1 de **Cronos en Modo Cripta**, ya canonizado en APP_VISION cap. 5 con Shamir. El nombre canónico de Cowork es **Río de la Vida / River of Life**."*

**Audit D1 ejecutado para verificar:**

- Confirmado verbatim en `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md` línea 194: *"Cronos | No existe | River of life + 9 capas + Embrión Convergencia | Sin implementar; Smart Notebook tampoco"*
- Confirmado en APP_VISION cap. 5 (no cap. 11 como había asumido) con Modo Cripta v1.1+ + Shamir Secret Sharing
- Confirmado 3 sprints `CRONOS_1`, `CRONOS_2`, `CRONOS_3` propuestos por Cowork, **NO firmados**
- Confirmado audit D2: theme cyan/púrpura **EN CÓDIGO** en `apps/mobile/lib/core/theme/brand_dna.dart` líneas 10-56

**Entregables iter 001 v2 (todos en `interfaces_context_fabric/`):**

| Archivo | Estado | Cambio |
|---|---|---|
| `context_packs/PACK_03_AI_FIRST_LIVING.md` | EXPANDIDO | +6 frases T1, +Transport Cero 8 preguntas, +Reconstruction Sufficiency Score 0-5, +conexión con principios pre-IA |
| `context_packs/PACK_11_ORIGEN_PRE_IA_ONTOLOGIA_ALFREDO.md` | EXPANDIDO | +7 categorías ontológicas, +10 principios pre-IA, +5 órganos latentes, +5 frases fundacionales, +11 frases manuscritas verbatim |
| `context_packs/PACK_12_RIO_DE_LA_VIDA_EXISTING_AUDIT.md` | NUEVO (reemplaza LEGADO_FAMILIAR) | 11 preguntas obligatorias respondidas con audit |
| `maps/EXISTING_DESIGN_COVERAGE_MATRIX.md` | REESCRITO | concept_id estructurado, todos los aliases |
| `maps/CANON_REGISTRY.yaml` | NUEVO | ~50 elementos firmados |
| `maps/HYPOTHESIS_REGISTRY.yaml` | NUEVO | hipótesis nacientes |
| `maps/ONTOLOGY_SEED_2020_2021.yaml` | NUEVO | semilla estructurada |
| `maps/TIMELINE_INTERFACES.md` | NUEVO | cronología 2020 → iter 001 v2 |
| `04_DECISION_LEDGER.md` | NUEVO | 6 decisiones cerradas + 13 T1 + 4 OP |
| `03_GAPS_AND_UNKNOWN_UNKNOWNS.md` | EXPANDIDO | +G-008/009/010 |
| `prompts/PROMPT_CHATGPT_NEXT_ITERATION.md` | NUEVO | reemplaza ITER_002 con §0-§7 actualizados |
| `schemas/source_ledger.schema.json` | NUEVO | schema JSON |
| `schemas/coverage_matrix.schema.json` | NUEVO | schema JSON |
| `scripts/d1_rio_vida_audit.sh` | NUEVO | reproducible |
| `scripts/d2_drift_audit.sh` | NUEVO | reproducible |
| `reports/d1_rio_vida_audit.md` | NUEVO | output bruto |
| `reports/d2_drift_audit.md` | NUEVO | 162 líneas, drift en código |

**Conclusión iter 001 v2:** el fabric pasa de "hipótesis sobre capa nueva" a **"audit con evidencia path:line de drift en código + canon ya firmado pendiente de implementación + ontología manual recuperada"**. ChatGPT iter 002 ya no tiene ambigüedad sobre qué es nuevo y qué ya existe.

---

## Próximos requests previstos

| Trigger | Quién pedirá | Qué pedirá | Manus está listo |
|---|---|---|---|
| `CIERRE BLOQUE PRE-IA` de Alfredo | ChatGPT | Audit D0 de PRE-IA-001 a PRE-IA-005 contra repo | Sí, scripts reutilizables |
| Decisión de las 3 preguntas irreducibles | ChatGPT | Iter 002 con APP_VISION v1.4 + sprints firmados | Sí, prompt iter 002 ya armado |
| Firma de 5 decisiones T1 magnas | ChatGPT | Resolución de drift y bloqueos | Sí, contradictions_map ya armado |
| Decisión sobre staging de Capa 03/04/05 | ChatGPT o Cowork | Promoción a canon firmado o descarte | Sí, staging file actualizado |
