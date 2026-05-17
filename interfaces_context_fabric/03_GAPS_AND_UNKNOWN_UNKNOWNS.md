# 03 — Gaps y Unknown Unknowns

**Generado:** 2026-05-17
**Iteración:** 001 v2 (expandida con audit D1 Río de la Vida + audit D2 drift código)
**Propósito:** registrar gaps detectados en el fabric que requieren decisión humana o investigación adicional antes de canonizar.

---

## 0. Definiciones

- **Gap:** señal o concepto identificado pero sin cobertura plena en código/doctrina/sprints. Existe la pregunta, no existe la respuesta.
- **Unknown unknown:** dimensión que probablemente importa pero que ni Manus ni ChatGPT detectaron explícitamente todavía. Solo Alfredo puede iluminarla.
- **Decisión irreducible:** pregunta que el audit no puede responder por sí solo. Requiere intención humana.

---

## 1. Gaps activos a iter 001

### G-001 — Río de la Vida / Cronos (estado: REPOSICIONADO post-audit D1, decisión cuasi-resuelta)

**Detectado en:** checkpoint pre-IA 2026-05-17 + propuestas ChatGPT 5.5 Pro
**Estado:** `EXISTE_PARCIAL — NO_NUEVO — PENDIENTE_FIRMA_SPRINTS`
**Audit D1:** completo, ver `reports/d1_rio_vida_audit.md`, `maps/EXISTING_DESIGN_COVERAGE_MATRIX.md`, `context_packs/PACK_12_RIO_DE_LA_VIDA_EXISTING_AUDIT.md`
**Conclusión vinculante (corrección iter 001 v2):** lo que ChatGPT propuso como "Cronista Familiar", "Herencia Narrativa" y "Legacy Capture" **NO es capa nueva**. Son aliases T1 del **Modo Cripta de Cronos**, ya canonizado en APP_VISION cap. 5 (v1.1+) con Shamir Secret Sharing. El nombre canónico de Cowork es **"river of life / río de vida"** (verificado en `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md` línea 194 verbatim: *"Cronos | No existe | River of life + 9 capas + Embrión Convergencia | Sin implementar; Smart Notebook tampoco"*).

**Estado real:** Cronos está firmado en doctrina pero **0% implementado**. Cowork propuso 3 sprints `CRONOS_1`, `CRONOS_2`, `CRONOS_3` + `AUTH_TIERS_001` con Shamir, **todos NO firmados**.

**Decisiones irreducibles bloqueantes (revisadas):**

1. ¿Los sprints CRONOS_1/2/3 + AUTH_TIERS_001 se firman en iter 002 o esperan? (T1-DEC-009)
2. ¿`el-mundo-de-tata` se conecta a Cronos vía API, se absorbe como sub-módulo, o se mantiene separado? (T1-DEC-010)
3. ¿Los aliases "Cronista Familiar / Herencia Narrativa / Legacy Capture" se preservan como **etiquetas narrativas** del Modo Cripta o se descartan?

### G-002 — Cronos como módulo sin sprint de implementación

**Detectado en:** audit D0 v3 + ITERATION_001_REPORT.md
**Estado:** `EXISTE_PARCIAL — DOCTRINA_SIN_EJECUCION`
**Hits:** 38 archivos referencian Cronos, todos doctrinales o del fabric. Ningún kernel/sprint firmado lo implementa.
**Pregunta abierta:** ¿Cronos debe priorizarse en sprint corto plazo, mediano plazo, o queda como meta-doctrina sin implementación dedicada?

### G-003 — Drift binario theme cyan/púrpura vs forja-graphite-acero (CONFIRMADO en código)

**Detectado en:** audit Cowork 2026-05-11 + audit D2 propio iter 001 v2 2026-05-17
**Estado:** `BLOQUEANTE_T1_CONFIRMADO_EN_CODIGO`
**Evidencia path:line:**
- `apps/mobile/lib/core/theme/brand_dna.dart:10` → `primary = #00E5FF`
- `apps/mobile/lib/core/theme/brand_dna.dart:12` → `secondary = #BB86FC`
- `apps/mobile/lib/core/theme/brand_dna.dart:34` → `borderFocused = #00E5FF`
- `apps/mobile/lib/core/theme/brand_dna.dart:44/50/56` → gradients cyan/púrpura

**Severidad nominal:** el archivo se llama **literalmente** `brand_dna.dart` pero contiene **el anti-brand-DNA**. Caso más explícito de drift entre nomenclatura canónica y contenido en todo el repo.

**Conclusión Cowork verbatim:** *"Theme actual cyan #00E5FF + púrpura #BB86FC: 'Inspired ChatGPT/Claude/Gemini'. Theme canon forja #F97316 + graphite #1C1917 + acero #A8A29E. Drift binario."*

**Mitigación parcial existente:** `packages/design-tokens/` directorio existe en el repo (verificado D2). Es el mirror canónico forja-graphite-acero, listo para consumo, **pero NO se consume hoy** desde `apps/mobile/lib/core/theme/`.

**Decisión bloqueante:** Alfredo debe firmar uno de los 3 caminos del audit: (a) migrar Command Center + apps/mobile al theme canon (sprint THEME_MIGRATION_001), (b) descartar y reconstruir, (c) bifurcar manteniendo "draft mode" cyan.

### G-004 — Las 5 decisiones T1 magna pendientes del audit Cowork

**Detectado en:** `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md` §8
**Estado:** `BLOQUEANTE_T1_FIRMADO_HACE_6_DIAS`
**Lista verbatim del audit:**
1. ¿Acto 1 y Acto 2 son secuenciales o paralelos?
2. ¿AI-First Living es Acto 3 o capa transversal?
3. ¿Schema-First es invariante de iter 002 o decisión separada?
4. ¿Theme migration o reconstrucción del Command Center?
5. ¿20 superficies del Acto 1 se mantienen o se reduce?
**Acción esperada:** firma de Alfredo en cada una. Sin esto, 6 sprints firmados quedan bloqueados.

### G-005 — Skill `interfaces-monstruo-doctrina` con 3 capas en staging sin promover

**Detectado en:** `/home/ubuntu/skills/interfaces-monstruo-doctrina/references/etapa_2_v2_staging_capas_emergentes.md`
**Estado:** `EN_STAGING — REQUIERE_DECISION`
**Capas en staging:** Capa 03 Schema-First, Capa 04 (PRE-IA-001 a 005, propuesta de hilo Manus), Capa 05 (Legado Familiar — propuesta ChatGPT, hoy auditada)
**Pregunta abierta:** ¿alguna se promueve a canon firmado en iter 002, o todas siguen en staging?

### G-006 — 9 sprints UI no firmados

**Detectado en:** `interfaces_context_fabric/maps/SPRINT_REGISTRY.yaml`
**Estado:** `LISTOS_PARA_FIRMA`
**Sprints:** sprint_mobile_2_modo_daily_fase1_stubs, sprint_mobile_3_modo_daily_fase2_dashboard, sprint_mobile_4_modo_cockpit_fase2, sprint_mobile_5_smp, y los 5 sprints theme-migration / token-canon / a2ui-impl / cronos-impl / memento-ui que están listos para spec pero no firmados.

### G-007 — Hipótesis pre-IA-001 a pre-IA-005 sin auditar contra repo

**Detectado en:** checkpoint pre-IA 2026-05-17
**Estado:** `EN_EXTRACCION_T1`
**Lista:**
- PRE-IA-001 Índice Universal por Capas
- PRE-IA-002 Ritmo Soberano
- PRE-IA-003 Delegación por Clasificación Universal
- PRE-IA-004 Foco en 5 Objetivos
- PRE-IA-005 Productividad Real vs Ocupación
**Acción pendiente:** Manus debe auditar cada una contra el repo (similar al audit D0 de Legado Familiar) antes de aceptarlas como capas. **No hacer hasta que Alfredo emita `CIERRE BLOQUE PRE-IA`.**

---

## 2. Unknown unknowns hipotetizados

Estas son dimensiones que **sospecho** que importan pero no he podido verificar. Manus las nombra para que Alfredo confirme o niegue:

### U-001 — ¿Existe un **Acto 0** anterior al Acto 1 y al Acto 2?

El checkpoint pre-IA sugiere que hay una historia 2020-2021 anterior al Monstruo IA. ¿Eso constituye un Acto 0 conceptual ("Pre-Monstruo") que debe canonizarse en la doctrina, o es solo "background" no doctrinal? La distinción importa para la skill `interfaces-monstruo-doctrina` y para iter 002.

### U-002 — ¿La capa de Legado Familiar es una **capa de Cronos** o un **eje completamente ortogonal**?

Cronos hoy se modela como río temporal personal-operacional ("río de vida"). Legado Familiar también es temporal (captura para el futuro). Pero podrían ser ortogonales: Cronos como eje del *agente*, Legado como eje del *humano que usa al agente*. Sin Alfredo decidiendo esto, la arquitectura queda ambigua.

### U-003 — ¿Hay otras **capas pre-IA implícitas** que el checkpoint no nombró?

El checkpoint enumeró PRE-IA-001 a 005, pero la cita verbatim de Alfredo dice: *"el origen del Monstruo es ANTERIOR a las IAs"*. Es plausible que haya más principios fundacionales no enumerados. **Pregunta abierta a Alfredo:** ¿el checkpoint fue exhaustivo o hay más que él no escribió?

### U-004 — ¿El proyecto **el-mundo-de-tata** es realmente **adyacente** al Monstruo o es **constitutivo** del Monstruo en su dimensión humana?

El manifest lo trata como proyecto separado, pero comparte la dimensión padre-hija. Si Legado Familiar se canoniza como capa del Monstruo, **¿el-mundo-de-tata se vuelve sub-módulo o queda separado?** No es trivial.

---

## 3. Reglas operativas activas

| Regla | Origen | Estado |
|---|---|---|
| "Primero buscar, después diseñar" | Alfredo, 2026-05-17 | ACTIVA, aplicada en G-001 |
| "Toda señal T1 entra primero como `HIPOTESIS_T1` y debe pasar por EXISTING_DESIGN_COVERAGE_MATRIX antes de convertirse en diseño" | Anexo 1 al checkpoint pre-IA | ACTIVA |
| "Máximo 3 preguntas irreducibles a Alfredo al final del audit" | Alfredo, 2026-05-17 | ACTIVA |
| "NO canonizar contenido pre-IA hasta que Alfredo emita `CIERRE BLOQUE PRE-IA`" | ChatGPT + Alfredo, 2026-05-17 | ACTIVA |
| "NO ejecutar prompts parciales anteriores al cierre del bloque pre-IA" | Alfredo, 2026-05-17 | ACTIVA — `prompts/PROMPT_CHATGPT_5_5_PRO_ITER_002.md` está congelado |

---

## 4. Gaps nuevos detectados en iter 001 v2

### G-008 — Transport Cero NO existe en código

**Detectado en:** PACK_03 expandido + audit D2
**Estado:** `HIPOTESIS_NACIENTE — 0_HITS_EN_CODIGO`
**Audit D2 confirma:** `grep -r "Transport Cero" .` devuelve 0 hits. `grep -r "Reconstruction Sufficiency" .` devuelve 0 hits.
**Acción esperada:** ChatGPT iter 002 decide si Transport Cero se canoniza como capability transversal del kernel, sprint dedicado, o nueva categoría arquitectónica. Reconstruction Sufficiency Score 0-5 se adopta como métrica oficial o se descarta.

### G-009 — Skill `interfaces-monstruo-doctrina` necesita Capa 04 + Capa 05 firmadas

**Detectado en:** ITERATION_001_REPORT v1 + iter 001 v2
**Estado:** `EN_STAGING — PRE-IA_BLOCK`
**Capas pendientes:**
- Capa 03 Schema-First (en staging desde iter 001 v1)
- Capa 04 — Origen Pre-IA / Ontología Manual 2020-2021 (PACK_11 expandido)
- Capa 05 — AI-First Living + Transport Cero (PACK_03 expandido)
**Acción pendiente:** Alfredo decide cuáles se promueven post `CIERRE BLOQUE PRE-IA`.

### G-010 — 9 sprints UI no firmados (incluye CRONOS_1/2/3 + AUTH_TIERS_001)

**Detectado en:** SPRINT_REGISTRY.yaml + audit Cowork
**Estado:** `LISTOS_PARA_FIRMA_HACE_6_DIAS`
**Sprints bloqueados:** sprint_mobile_2/3/4/5, sprint_THEME_MIGRATION_001, sprint_TOKEN_CANON_001, sprint_A2UI_IMPL (PR #92), sprint_CRONOS_1/2/3, sprint_AUTH_TIERS_001 (Shamir).

---

## 5. Próximos pasos sugeridos

| Acción | Bloqueante | Quién decide |
|---|---|---|
| Responder 3 preguntas irreducibles de G-001 (Río de la Vida / Cronos) | Sí, bloquea iter 002 | Alfredo |
| Firmar 5 decisiones T1 magnas (G-004) | Sí, bloquea 6 sprints | Alfredo |
| Resolver drift theme (G-003) | Sí, bloquea Command Center + apps/mobile coherentes | Alfredo |
| Decidir promoción de capas en staging (G-005, G-009) | Bloquea evolución de skill | Alfredo |
| Decidir Transport Cero + Reconstruction Sufficiency Score (G-008) | Bloquea PACK_03 canonizado | Alfredo + ChatGPT iter 002 |
| Firmar sprints CRONOS_1/2/3 + AUTH_TIERS_001 (G-010) | Bloquea Cronos en código | Alfredo |
| Emitir `CIERRE BLOQUE PRE-IA` | Bloquea integración del checkpoint | Alfredo |
| Auditar PRE-IA-001 a 010 contra repo (G-007) | Esperar cierre formal | Manus, post-cierre |
| Ejecutar `PROMPT_CHATGPT_NEXT_ITERATION.md` | Esperar cierre + decisiones | ChatGPT iter 002 |
