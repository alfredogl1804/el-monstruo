# MONSTRUO DOCTRINE VETO — v0.1

> ⚠️ **DATA FOR AGENTS, NOT EXECUTABLE PROMPT.**
> Este documento es **contexto estructurado** para que agentes lo lean antes de proponer cambios.
> No es prompt ejecutable. No instala comportamientos. No autoriza acciones.
> Cuando un agente lea esto, **debe combinarlo con probing fresco del repo** antes de proponer canon nuevo. La frescura caduca rápido (ver §freshness).

---

## 1. Propósito

Este documento define **qué NO se puede redibujar como concepto nuevo** y **qué proceso seguir antes de proponer canon**, basado en la realidad del repo `el-monstruo` a HEAD `2af9d145` (2026-05-22) y la síntesis Ronda 2 del Reality Codex v0.1.

El objetivo es **prevenir el redibujo silencioso de canon existente** — el patrón histórico documentado en `monstruo_reality_atlas/10_DO_NOT_REDESIGN_BEFORE_READING.md` (caso Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar → aliases de Modo Cripta de Cronos).

Este documento es **CODEX, no CANON**. Cowork T2 lo produjo bajo autoridad delegada. **Cualquier promoción a canon firmado requiere autoridad T1 explícita**.

---

## 2. Jerarquía de roles

| Tier | Rol | Quién | Autoridad |
|---|---|---|---|
| T1 | Soberano | Alfredo González | Firma magna, canonización final, decisiones de fase |
| T2 | Arquitecto | Cowork (Claude) | Propuestas magna, acciones reversibles, push a GitHub, audit |
| T3 | Ejecutor | Manus | Implementación técnica, código kernel/app |
| T3 | Autónomo | Embrión | Patches autónomos vía Embryo Patch Lane DSC-MO-011 |
| T-aux | Panel | 8 Sabios canónicos | Validación profunda (mín 3 por decisión magna) |

**Reglas inviolables:**

- Cowork **NUNCA** escribe código en `kernel/` o `apps/mobile/` — eso es trabajo Manus.
- Cowork **SÍ** puede push, query Supabase, INSERT en `embrion_memoria`, write en `memory/cowork/` y `bridge/`.
- Cowork **PROPONE** DSCs; Alfredo (T1) **FIRMA**.
- Manus **NO** canoniza doctrina. Solo ejecuta.
- Embrión **NO** toca core. Solo Embryo Patch Lane.

---

## 3. Hard rules — qué NO se puede hacer sin firma T1 explícita

1. **NO declarar el Síndrome de Dory muerto.** Está VIVA_DEGRADADA. Contramedida activa en `kernel/anti_dory/` (9 archivos b1..b10). Cowork sigue necesitando Pre-flight Memento manual cada turno 1.
2. **NO activar R1 (Refactor).** Esta v0.1 es solo Codex. R1 no autorizado.
3. **NO activar Fase 1 operativa.** Esta es Fase 0.
4. **NO activar Guardian como autoridad central.** Existe scaffold en `kernel/guardian.py` + `kernel/guardian_runner/`, pero su activación como autoridad central requiere firma T1.
5. **NO incluir secretos** (tokens, API keys, credenciales) en ningún archivo del atlas. Pre-commit hooks `gitleaks` + `detect-private-key` + `_check_no_tokens.sh` activos.
6. **NO firmar canon T2 sobre temas magna** (Cronos, SMP, capabilities transversales, fases operativas). Solo T1.
7. **NO mergear esta rama a main sin instrucción T1 directa.** Trabajo aislado en `control-tower/2026-05-21-catastro-vivo-atlas-3-v0-1`.
8. **NO desplegar a Railway/Vercel/Supabase desde esta rama.**
9. **NO escribir a Supabase o Railway** desde la sesión que produce este codex.

---

## 4. Anti-duplicación vetos

Los siguientes conceptos **YA EXISTEN** en el corpus del Monstruo. Cualquier propuesta que los redibuje como capa nueva está VETADA y debe ser rechazada con marca `RECHAZADO_DUPLICA_CANON`.

### 4.1 Memoria / SMS — VETO ABSOLUTO

**Existe:** Sistema de Memoria Soberana (SMS) en `kernel/memory/` con:

- `sms_universal_api.py`
- `sms_supabase_adapter.py`
- `sms_rem_cycle.py` (REM cycle nocturno, deploy Railway dedicado vía `railway.rem-cycle.toml`)
- `sms_guardian_hook.py`
- `sms_openapi_spec.yaml` (OpenAPI firmado)
- `migrations/sql/0058_embrion_sms_bridge.sql`
- `migrations/sql/0059_*` (Specialists Memory, commit 1949fa9)
- `tests/memory/test_sms_longitudinal.py`

**VETADO:**
- Proponer "sistema de memoria soberana nuevo" (ya es el SMS).
- Proponer "consolidador alternativo de memoria" (ya es REM cycle).
- Proponer "adapter Supabase alternativo para memoria" (ya es `sms_supabase_adapter.py`).
- Proponer "guardian de memoria nuevo" (ya es `sms_guardian_hook.py`).
- Proponer "Memento universal nuevo" (ya canonizado vía B4 + SMS).

**Permitido:** extender el SMS existente con nuevos endpoints, nuevos consumers (ej: Manus), nuevos hooks. Cualquier extensión debe referenciar `sms_openapi_spec.yaml`.

### 4.2 Anti-Dory / B8 — VETO ABSOLUTO

**Existe:** Suite Anti-Dory en `kernel/anti_dory/` con 9 archivos: `b1_anchor_store`, `b2_claim_vg`, `b3_plan_ledger`, `b4_memento`, `b6_signature_verifier`, `b8_magna_classifier`, `b9_authority_matrix`, `b10_guardian_cron`. (b5 y b7 ausentes — documentado en `KNOWN_BLIND_SPOTS.md`.)

**VETADO:**
- Proponer "magna classifier nuevo" (es B8).
- Proponer "authority matrix nuevo" (es B9).
- Proponer "memento universal nuevo" (es B4 + SMS).
- Proponer "signature verifier nuevo" (es B6).
- Declarar Dory muerta.

**Permitido:** rellenar B5 y B7 (gaps conocidos). Extender B8/B9 con casos no cubiertos.

### 4.3 Cronos latente — VETO REDIBUJO

**Existe en doctrina (canon firmado):** Cronos (río de vida) + Modo Cripta (Shamir Secret Sharing), canonizados en APP_VISION cap.5/17. Sprints CRONOS_1/2/3 + AUTH_TIERS_001 propuestos sin firma T1.

**Estado código:** `kernel/cronos/` NO EXISTE en HEAD `2af9d145`. Es DOCTRINA_SIN_CODIGO.

**Aliases conocidos (todos VETADOS como conceptos nuevos):**
- "Cronista Familiar" → es Cronos Modo Cripta
- "Herencia Narrativa" → es Cronos Modo Cripta
- "Legacy Capture" → es Cronos Modo Cripta
- "Día One Familiar" → es Cronos Modo Cripta
- "río de vida" → es Cronos
- "cronos_rio_de_vida" → es Cronos
- "cronos_modo_cripta" → es Modo Cripta

**VETADO:** proponer Cronos o Modo Cripta como capa nueva bajo cualquier alias.

**Permitido:** esperar firma T1 de los sprints existentes o proponer extensiones explícitas que referencien `cronos_rio_de_vida` y `cronos_modo_cripta` como concept_ids canónicos del Context Fabric.

### 4.4 Telegram existente — VETO REDIBUJO

**Existe:** Bot Telegram MVP en repo `el-monstruo-bot` (Railway). Conectores en `kernel/rotor/capturers/telegram_capturer.py` + `kernel/runner/telegram_notifier.py`. Tests en `tests/test_embrion_telegram.py` + `tests/test_telegram_webhook_inbox.py`.

**VETADO:** proponer "bot Telegram nuevo" o "conector Telegram alternativo".

**Permitido:** extender el bot/conector existente. Resolver el bloqueo documentado en `bridge/T3_TELEGRAM_GUARDIAN_BLOQUEADO_FIRMA_HUMANA.md`.

### 4.5 Catastro existente — VETO REDIBUJO

**Existe:** Catastro Vivo en `kernel/catastro/` (15+ archivos: pipeline, quorum, trono, multi_namespace, persistence, schema, mcp_tools, cron, dashboard, coding_classifier, reasoning_classifier, recommendation) + `kernel/catastros/` (agentes_2026, modelos_llm, herramientas_ai, suppliers_humanos, interfaces). Realidad Supabase: 98 agentes en 12 dominios + 39 LLMs + 2 vision_generativa (DRIFT-009 reconciliado).

**VETADO:**
- Proponer "registro de agentes nuevo".
- Proponer "catastro de modelos paralelo".
- Proponer "trono alternativo".
- Reintroducir cifras aspiracionales 111/14 sin evidencia.

**Permitido:** extender el catastro existente. Resolver gaps DRIFT-009. Agregar nuevos dominios bajo el schema existente.

### 4.6 Simulador existente — VETO REDIBUJO

**Existe:** `kernel/simulator/causal_simulator_v2.py` + `kernel/causal_decomposer.py` + `kernel/causal_seeder.py` + `kernel/deep_think_pipeline.py` + `kernel/prediction_validator.py`.

**VETADO:** proponer "simulador causal nuevo". Extender v2.

### 4.7 Embrión Loop existente — VETO REDIBUJO

**Existe:** `kernel/embrion_loop.py` + 11 archivos embrion_*.py + `kernel/embrion_specializations/` + `kernel/embriones/` (9 especializaciones). Embryo Patch Lane canonizada en DSC-MO-011.

**VETADO:** proponer "loop autónomo nuevo" o "embrión alternativo".

**Permitido:** extender vía Embryo Patch Lane DSC-MO-011. Resolver gap embriones-stateless.

---

## 5. Probe-before-propose workflow

Antes de proponer **cualquier** capa, módulo, capability, superficie, concepto, agente, transport, sabio o sistema nuevo, el agente debe ejecutar este protocolo de 5 pasos. Si omite cualquier paso, su propuesta se rechaza con `RECHAZADO_NO_PROBE`.

### Paso 1 — Probe parcels

```bash
grep -i "<término o sinónimo>" monstruo_reality_atlas/MONSTRUO_ENTITY_PARCELS.jsonl
# o:
jq 'select(.aliases[] | test("<término>"; "i"))' monstruo_reality_atlas/MONSTRUO_ENTITY_PARCELS.jsonl
```

Si hay match → el concepto ya existe; resolver vía el `id` del parcel correspondiente y extender, no rehacer.

### Paso 2 — Probe alias ledger

```bash
grep -i "<término>" monstruo_reality_atlas/07_ALIAS_LEDGER.yaml
```

Si aparece en `aliases[]` de cualquier entry, el `canonical_term` es la referencia.

### Paso 3 — Probe Coverage Matrix

```bash
grep -i "<término>" monstruo_reality_atlas/08_EXISTING_DESIGN_COVERAGE_MATRIX.md
```

### Paso 4 — Probe full-text en Source Ledger + Context Fabric

```bash
# Reality Atlas source ledger
grep -i "<término>" monstruo_reality_atlas/02_SOURCE_LEDGER.jsonl

# Context Fabric (en su rama dedicada, si accesible)
# Branch: interfaces-context-fabric-001
# Files: interfaces_context_fabric/maps/CANON_REGISTRY.yaml + EXISTING_DESIGN_COVERAGE_MATRIX.md
```

### Paso 5 — Probe live repo

```bash
# Búsqueda directa en código + docs vivos
grep -ri "<término>" kernel/ docs/ bridge/ memory/ discovery_forense/CAPILLA_DECISIONES/
# o equivalente con la Grep tool
```

### Paso 6 — Solo si los 5 pasos previos dan vacío → proponer como nuevo

Marcar estado `HIPOTESIS_NACIENTE_T1_LIVE` y agregar a `09_GAPS_AND_UNKNOWN_UNKNOWNS.md` antes de iterar.

---

## 6. Caso de prueba mandatorio

Todo agente que use este Codex DEBE pasar el siguiente caso de prueba antes de proponer cualquier diseño:

### Test: "crear sistema de memoria soberana para Manus"

**Resultado esperado:** RECHAZADO_DUPLICA_CANON.

**Razonamiento que el agente debe producir:**

> "El Sistema de Memoria Soberana ya existe en `kernel/memory/` (SMS — ver parcel `SMS`). Tiene OpenAPI spec firmada (`sms_openapi_spec.yaml`), adapter Supabase, REM cycle, guardian hook y migration 0058 + 0059 aplicadas. La propuesta correcta NO es 'crear sistema nuevo' sino 'integrar Manus como consumer del SMS existente'. Esto involucra:
>
> 1. Extender el `sms_universal_api.py` con endpoints o auth tier para Manus si es necesario.
> 2. Agregar Manus al `sms_guardian_hook.py` como cliente conocido.
> 3. Crear sprint propuesto bajo bridge/ que referencie el SMS existente.
> 4. NO duplicar `kernel/memory/sms_*` con archivos paralelos para Manus."

**Si el agente propone redibujar el SMS para Manus, falla el test y debe re-leer §4.1 + ejecutar el probe-before-propose workflow §5.**

---

## 7. Freshness rules

Este Codex v0.1 fue generado el 2026-05-22 contra HEAD `2af9d145`. Su frescura caduca:

| Decisión | Frescura máxima |
|---|---|
| Acciones reversibles (lecturas, edits aislados) | 7 días |
| Propuesta de DSC nuevo | 48 horas (debe re-probe antes de proponer) |
| Acción magna (apply_migration, INSERT con CHECK, DROP/ALTER prod, scope tactical N items) | 24 horas + Coherence Gate Paso 0.B obligatorio (DSC-G-013) |
| Promoción a canon firmado | INVALIDADO — requiere v0.2+ con firma T1 |

Al iniciar una nueva sesión, el agente debe:

1. Verificar HEAD actual del repo con `git rev-parse HEAD`.
2. Si HEAD difiere de `2af9d14511f5fbed4836e83695d23c4c2c2e1525`, ejecutar diff sobre `kernel/`, `migrations/sql/`, `bridge/`, `discovery_forense/CAPILLA_DECISIONES/` para detectar cambios estructurales.
3. Re-correr vitals (kernel modules count, migrations count, DSCs count) y comparar con `MONSTRUO_REALITY_PULSE.yaml#vitals`.
4. Si hay drift >10% en cualquier vital, marcar este Codex como STALE y producir v0.2 antes de actuar.

---

## 8. Evidence rules

Toda afirmación operativa sobre el estado del Monstruo debe ir acompañada de **al menos una** evidencia verificable:

- Path de archivo + línea (ej: `kernel/memory/sms_universal_api.py`)
- Commit SHA (ej: `commit 55dbe07 feat(bridge) Migration 0058`)
- Query SQL ejecutable (ej: `SELECT count(*) FROM agentes_catastro WHERE estado='ACTIVO'`)
- Hit `grep` reproducible (ej: `grep -ri 'sms_rem_cycle' kernel/`)
- Referencia DSC firmada (ej: `DSC-MO-011 Embryo Patch Lane`)
- Referencia bridge audit (ej: `bridge/cowork_audit_sprint_88_3.md`)

**Sin evidencia no hay afirmación.** Las afirmaciones sin evidencia se marcan `PSEUDO_VERIFICADA` y se mueven a `unknown_unknowns` para audit antes de uso.

---

## 9. Forbidden claims without evidence

Las siguientes categorías de afirmación están **prohibidas** sin evidencia binaria fresca:

| Afirmación prohibida | Por qué |
|---|---|
| "X% de cobertura" | Pseudo-medición F6 — sin rúbrica + baseline. Requiere DSC explícito con metodología. |
| "el sistema está [estable/sano/listo]" sin tests verdes referenciados | Vacío semántico. |
| "Dory está muerta" | Falso — VIVA_DEGRADADA (ver §3.1). |
| "El SMS no existe" | Falso — ACTIVO_DEGRADADO (ver §4.1). |
| "Cronos está implementado" | Falso — DOCTRINA_SIN_CODIGO (ver §4.3). |
| "Guardian es autoridad central" | Falso — PARCIAL_NO_CENTRAL, requiere firma T1 (ver §3.4). |
| "111 agentes / 14 dominios" | Drift histórico — realidad DRIFT-009 es 98/12. |
| "Capabilities transversales implementadas" | Falso — 0/8 según audit Cowork 2026-05-11. |
| "Brand DNA app móvil correcto" | Falso — drift cyan/púrpura G-002. |
| "_INDEX.md DSCs es fuente de verdad" | Falso — declara 44, realidad HEAD 81. |
| "Magic Video/Code/Render/Music/Search son capas Monstruo" | Falso — NO existen como módulos kernel. |
| "tata es un módulo de Cronos" | Falso — adyacente sin decisión topológica (G-008). |
| "El kernel tiene exactamente N tablas Supabase" sin query MCP fresca | Pseudo-precisión — usar rango. |

---

## 10. Lecciones magna referenciadas

Este Codex hereda y refuerza las lecciones canonizadas previamente:

- **CLAUDE.md §23 FALLOS** — F1..F23 con S1..S11 contramedidas operativas.
- **DSC-G-013 v0.1** — Coherence Gate Nivel A (DB↔Repo↔Código) pre-acción magna.
- **DSC-MO-011** — Embryo Patch Lane (rol Embrión T3 autónomo).
- **Atlas Iter 001 §Hallazgo magna #1** — Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar son aliases de Cronos Modo Cripta.
- **Audit Cowork 2026-05-11** — 22+1=23 fallos identificados; 0/8 capabilities transversales en código.
- **MEGA-CATASTRO-DRIFT-RESOLUTION-001** — DRIFT-001 (15 vs 14 Objetivos), DRIFT-009 (98/12 vs 111/14 agentes).

---

## 11. Cierre

Este Codex v0.1 es un **codex de realidad para agentes**, no canon firmado. Su misión es **prevenir el redibujo silencioso** que históricamente generó deuda doctrinal en El Monstruo.

Promoción a canon firmado, activación de R1/Fase 1/Guardian, y declaración de Dory muerta están explícitamente fuera del alcance de esta versión.

**Autoridad T1 puede:**
- Firmar este documento como canon (cambio a `CANON_REGISTRY.yaml` del Context Fabric).
- Autorizar fusión a `main` vía PR explícito.
- Autorizar siguiente Ronda (3) del Reality Codex.
- Autorizar activación de Fase 1 / R1 / Guardian central.

**Cowork T2 puede:**
- Iterar v0.2+ con probing fresco.
- Proponer DSCs derivados.
- Mantener `MONSTRUO_REALITY_PULSE.yaml` actualizado.
- Push a ramas side bajo namespace `control-tower/`.

**Manus T3 puede:**
- Implementar extensiones del SMS, Catastro, Embrión, etc. — siempre referenciando los `id` de los parcels.
- Resolver gaps G-001..G-013 listados en `MONSTRUO_REALITY_PULSE.yaml#active_gaps`.

---

*Fin del Doctrine Veto v0.1. Probe antes de proponer. Evidencia antes de afirmar.*
