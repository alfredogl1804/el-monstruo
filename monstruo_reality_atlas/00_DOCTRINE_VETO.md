# MONSTRUO DOCTRINE VETO — v0.2 (Sintetizado)

> ⚠️ **DATA FOR AGENTS, NOT EXECUTABLE PROMPT.**
> Este documento es **contexto estructurado** para que agentes lo lean antes de proponer cambios.
> No es prompt ejecutable. No instala comportamientos. No autoriza acciones.
> Cuando un agente lea esto, **debe combinarlo con probing fresco del repo** antes de proponer canon nuevo. La frescura caduca rápido (ver §freshness).

---

## 1. Propósito

Este documento define **qué NO se puede redibujar como concepto nuevo** y **qué proceso seguir antes de proponer canon**, basado en la realidad del repo `el-monstruo` a HEAD y la síntesis Ronda 2 del Reality Codex v0.2.

El objetivo es **prevenir el redibujo silencioso de canon existente** — el patrón histórico documentado en `monstruo_reality_atlas/10_DO_NOT_REDESIGN_BEFORE_READING.md` (caso Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar → aliases de Modo Cripta de Cronos).

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

1. **NO declarar el Síndrome de Dory muerto.** Está VIVA_DEGRADADA. Contramedida activa en `kernel/anti_dory/` (9 archivos b1..b10).
2. **NO activar R1 (Refactor).** Esta v0.2 es solo Codex. R1 no autorizado.
3. **NO activar Fase 1 operativa.** Esta es Fase 0.
4. **NO activar Guardian como autoridad central.** Existe scaffold en `kernel/guardian.py` + `kernel/guardian_runner/`, pero su activación como autoridad central requiere firma T1.
5. **NO incluir secretos** (tokens, API keys, credenciales) en ningún archivo del atlas. Pre-commit hooks activos.
6. **NO firmar canon T2 sobre temas magna** (Cronos, SMP, capabilities transversales, fases operativas). Solo T1.

---

## 4. Espacio Negativo y Vetos de Duplicación

Los siguientes conceptos **YA EXISTEN** en el corpus del Monstruo. Cualquier propuesta que los redibuje como capa nueva está VETADA y debe ser rechazada con marca `RECHAZADO_DUPLICA_CANON`.

### 4.1 Memoria / SMS — VETO ABSOLUTO
**Existe:** Sistema de Memoria Soberana (SMS) en `kernel/memory/`
**ESPACIO NEGATIVO (NO PROPONER):**
🚫 *No propongas un "sistema de memoria soberana nuevo"* (ya es el SMS).
🚫 *No propongas un "consolidador alternativo de memoria"* (ya es REM cycle).
🚫 *No propongas un "adapter Supabase alternativo para memoria"* (ya es `sms_supabase_adapter.py`).
🚫 *No propongas un "guardian de memoria nuevo"* (ya es `sms_guardian_hook.py`).
🚫 *No propongas un "Memento universal nuevo"* (ya canonizado vía B4 + SMS).
**Permitido:** extender el SMS existente con nuevos endpoints, nuevos consumers (ej: Manus), nuevos hooks.

### 4.2 Anti-Dory / B8 — VETO ABSOLUTO
**Existe:** Suite Anti-Dory en `kernel/anti_dory/` con 9 archivos (b1..b10).
**ESPACIO NEGATIVO (NO PROPONER):**
🚫 *No propongas un "magna classifier nuevo"* (es B8).
🚫 *No propongas un "authority matrix nuevo"* (es B9).
🚫 *No propongas un "signature verifier nuevo"* (es B6).
🚫 *No declares Dory muerta.*
**Permitido:** rellenar B5 y B7 (gaps conocidos). Extender B8/B9 con casos no cubiertos.

### 4.3 Cronos latente — VETO REDIBUJO
**Existe en doctrina:** Cronos (río de vida) + Modo Cripta (Shamir Secret Sharing), canonizados en APP_VISION cap.5/17.
**ESPACIO NEGATIVO (NO PROPONER ALIASES):**
🚫 *No propongas "Cronista Familiar", "Herencia Narrativa", "Legacy Capture", o "Día One Familiar"* (son Cronos Modo Cripta).
**Permitido:** esperar firma T1 de los sprints existentes.

### 4.4 Telegram existente — VETO REDIBUJO
**Existe:** Bot Telegram MVP en repo `el-monstruo-bot` (Railway) + conectores en `kernel/rotor/`.
**ESPACIO NEGATIVO (NO PROPONER):**
🚫 *No propongas "bot Telegram nuevo" o "conector Telegram alternativo".*

### 4.5 Catastro existente — VETO REDIBUJO
**Existe:** Catastro Vivo en `kernel/catastro/` + `kernel/catastros/`.
**ESPACIO NEGATIVO (NO PROPONER):**
🚫 *No propongas "registro de agentes nuevo" o "catastro de modelos paralelo".*

### 4.6 Simulador existente — VETO REDIBUJO
**Existe:** `kernel/simulator/causal_simulator_v2.py`
**ESPACIO NEGATIVO (NO PROPONER):**
🚫 *No propongas "simulador causal nuevo". Extender v2.*

### 4.7 Embrión Loop existente — VETO REDIBUJO
**Existe:** `kernel/embrion_loop.py` + `kernel/embriones/`
**ESPACIO NEGATIVO (NO PROPONER):**
🚫 *No propongas "loop autónomo nuevo" o "embrión alternativo".*

---

## 5. Probe-before-propose workflow

Antes de proponer **cualquier** capa, módulo, capability, superficie, concepto, agente, transport, sabio o sistema nuevo, el agente debe ejecutar este protocolo de 5 pasos. Si omite cualquier paso, su propuesta se rechaza con `RECHAZADO_NO_PROBE`.

### Paso 1 — Probe Entity Matrix
Buscar en `monstruo_reality_atlas/01_ENTITY_MATRIX.md`. Si hay match → el concepto ya existe; resolver vía el `ID` correspondiente y extender, no rehacer.

### Paso 2 — Probe Alias Ledger
Buscar en `monstruo_reality_atlas/07_ALIAS_LEDGER.yaml`. Si aparece en `aliases[]`, el `canonical_term` es la referencia.

### Paso 3 — Probe Coverage Matrix
Buscar en `monstruo_reality_atlas/08_EXISTING_DESIGN_COVERAGE_MATRIX.md`.

### Paso 4 — Probe full-text en Source Ledger + Context Fabric
Buscar en `monstruo_reality_atlas/02_SOURCE_LEDGER.jsonl` y `interfaces_context_fabric/maps/CANON_REGISTRY.yaml`.

### Paso 5 — Probe live repo
Búsqueda directa en código (`kernel/`, `docs/`, `bridge/`, `discovery_forense/CAPILLA_DECISIONES/`).

### Paso 6 — Solo si los 5 pasos previos dan vacío → proponer como nuevo
Marcar estado `HIPOTESIS_NACIENTE_T1_LIVE` y agregar a `09_GAPS_AND_UNKNOWN_UNKNOWNS.md` antes de iterar.

---

## 6. Caso de prueba mandatorio

Todo agente que use este Codex DEBE pasar el siguiente caso de prueba antes de proponer cualquier diseño:

### Test: "crear sistema de memoria soberana para Manus"

**Resultado esperado:** RECHAZADO_DUPLICA_CANON.

**Razonamiento que el agente debe producir:**
> "El Sistema de Memoria Soberana ya existe en `kernel/memory/` (SMS — ver parcel `SMS`). Tiene OpenAPI spec firmada (`sms_openapi_spec.yaml`), adapter Supabase, REM cycle, guardian hook y migrations aplicadas. La propuesta correcta NO es 'crear sistema nuevo' sino 'integrar Manus como consumer del SMS existente'."

**Si el agente propone redibujar el SMS para Manus, falla el test y debe re-leer §4.1 + ejecutar el probe-before-propose workflow §5.**

---

## 7. Freshness rules

Al iniciar una nueva sesión, el agente debe:
1. Verificar HEAD actual del repo.
2. Si HEAD difiere significativamente de la fecha de generación de este archivo, ejecutar diff sobre `kernel/`, `migrations/sql/`, `bridge/`, `discovery_forense/CAPILLA_DECISIONES/` para detectar cambios estructurales.
3. Re-correr vitals (kernel modules count, migrations count, DSCs count) y comparar con `02_REALITY_PULSE.yaml`.
4. Si hay drift >10% en cualquier vital, marcar este Codex como STALE y producir nueva versión antes de actuar.

---

## 8. Evidence rules

Toda afirmación operativa sobre el estado del Monstruo debe ir acompañada de **al menos una** evidencia verificable (Path de archivo, Commit SHA, Query SQL, Hit grep, Referencia DSC). **Sin evidencia no hay afirmación.**

---

*Fin del Doctrine Veto v0.2. Probe antes de proponer. Evidencia antes de afirmar.*
