<!-- lint_strict -->

# Sprint REMONTOIR-001 v3 — Decisor Dinámico Tiempo Real (deroga v1)

**estado:** FIRME T1 directa ("si autorizado" 2026-05-12 ~11:45 UTC)
**fecha_firma_T1:** 2026-05-12 ~11:45 UTC
**autor_borrador:** Cowork T2-A Arquitecto Orquestador post-detonante T1 ("este tipo de decisiones al ser magna necesitamos que la ia lo decida con una mezcla de razonamiento potente cruzado con validación en tiempo real")
**deroga:** `sprint_REMONTOIR_001_constant_force_quality.md` v1 commit `0de35e6` (hardcoded estático fabricado) + propuesta v2 cherry-pick chain estática (insuficiente arquitectónicamente)
**Hilo principal:** Manus Hilo Ejecutor 2 (queue post ESPIRAL-001 merge)
**ETA recalibrado:** 120-150 min reales (más magno que v1 — incluye decisor dinámico + cache + safety net)
**Objetivo Maestro:** #2 (Calidad Apple/Tesla) + #11 (Autonomía progresiva) + #5 (Validación tiempo real DSC-G-005) + #4 (No equivocarse dos veces)
**Bloqueos pre-arranque:** ESPIRAL-001 mergeado a main
**Resultado esperado:** pieza Remontoir del Reloj Suizo implementada con **decisor dinámico tiempo real** — NO hardcoded fallback chain estática. La IA del Monstruo decide AHORA qué modelo usar con razonamiento potente cruzado con validación Perplexity tiempo real + cache Rubíes + safety net determinístico.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1 + §4)

**Estado actual binario verificado por Cowork 2026-05-12 ~11:45 UTC:**

```bash
ls kernel/remontoir/ → NO EXISTE
ls kernel/adaptive_model_selector.py → EXISTE PARCIAL Y DESINCRONIZADO (T2-B Sesión 2 detectó)
ls kernel/response_cache.py → EXISTE PARCIAL (pieza #7 Rubíes en pipeline RUBIES-001)
ls kernel/validation/perplexity_decorator.py → EXISTE (DSC-V-001 implementado)
```

**Las 8 piezas Reloj Suizo — estado al arranque REMONTOIR-001 v3:**

| # | Pieza | Estado proyectado |
|---|---|---|
| 1 Resorte | `kernel/embrion_budget.py` | ✅ implementado |
| 2 Escape | `kernel/escape/` PR #116 | ✅ mergeado |
| 3 Áncora | `kernel/embrion_scheduler.py` | ✅ implementado |
| 4 Volante | `kernel/embrion_loop.py` | ✅ implementado |
| 5 Espiral | `kernel/espiral/` ESPIRAL-001 | 🟡 en curso |
| 6 Rotor | `kernel/rotor/` PR #113 | ✅ mergeado |
| 7 Rubíes/Caché | `kernel/response_cache.py` parcial | 🟡 RUBIES-001 spec pipeline |
| 8 **Remontoir** | NO existe | ❌ **este sprint** |

### §3 limitaciones declaradas honestamente

- NO verifiqué binariamente qué función hace `kernel/adaptive_model_selector.py` parcial existente
- NO verifiqué binariamente dónde se invoca actualmente decisión de modelo en kernel
- NO verifiqué que Catastro D1+D2 (8 vs 6 Sabios + DSC-V-001 dual) se cerró doctrinalmente antes del kickoff

### §4 consecuencias materiales deducidas + mitigación

| Limitación §3 | Consecuencia material | Mitigación |
|---|---|---|
| adaptive_model_selector existing | Posible duplicación lógica o overlap funcional | T0 obligatorio Ejecutor 2: audit binario antes de T2 |
| Decisión modelo actual no mapeada | Wiring REMONTOIR podría perder calls existentes | T0 grep call sites + T6 wiring inteligente reemplaza no agrega |
| Catastro D1+D2 no cerrado | Posible drift versiones canonizadas | NO bloqueante — spec usa versiones doctrina viva CLAUDE.md (8 Sabios verbatim); Catastro polish post-cierre |

---

## 1. Procedencia doctrinal

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 verbatim:

> "**Remontoir (Constant Force):** Innovación de Greubel Forsey: iguala la fuerza entregada al escape sin importar si el resorte está lleno o vacío → **Estabilizador de Calidad:** Garantiza que el output del agente sea igual de bueno al final del día (presupuesto bajo) que al principio, ajustando el modelo (fallback) dinámicamente."

**Detonante T1 del v3:** *"este tipo de decisiones al ser magna necesitamos que la ia lo decida con una mezcla de razonamiento potente cruzado con validación en tiempo real"* (Alfredo 2026-05-12 ~11:40 UTC).

v1 proponía hardcoded fallback chain estática con versiones fabricadas + costos estimados + quality scores inventados. **F21 reincidente Cowork** reconocido verbatim. v3 corrige arquitectónicamente: NO hardcode, decisor dinámico.

## 2. Patrón arquitectónico v3

### 2.1 Decisor dinámico tiempo real

Para cada request que requiere modelo LLM:

```python
from kernel.validation.perplexity_decorator import requires_perplexity_validation

@requires_perplexity_validation(
    claim_type="model_selection_optimal",
    ttl_hours=24,
    fallback_to_cache=True
)
async def select_model(
    quality_floor: float,
    budget_remaining: Decimal,
    vertical: str,
    pricing_tier: str,
) -> ModelSelection:
    """Decisor dinámico: consulta tiempo real con razonamiento potente.

    Perplexity decide AHORA qué modelo usar basándose en:
    - quality_floor declarativo (0.7 a 0.95)
    - budget_remaining (state del Resorte)
    - pricing actual de cada Sabio (web research tiempo real)
    - benchmarks LiveBench/Arena recientes
    - vertical context (CIP financiero / LIKETICKETS comercial / etc.)

    Cache via Rubíes pieza #7 TTL 24h por (quality_floor + vertical + budget_tier).
    """
```

### 2.2 Cache Rubíes (pieza #7) para no consultar cada request

Key de cache: `(quality_floor_tier, vertical, budget_tier_quintile)`
TTL: 24h default (configurable por consumer)
Invalidación: cuando modelo nuevo lanza (event-driven) o cambios pricing detectados.

### 2.3 Fallback determinístico safety net

Si Perplexity no responde + cache Rubíes miss + budget crítico:

Cadena hardcoded conservadora 8 Sabios canónicos doctrina viva (versiones top verbatim):

```python
SAFETY_NET_CHAIN_8_SABIOS_VERBATIM = [
    # quality_floor ≥ 0.9 (crítico):
    {"sabio": "GPT-5.5 Pro", "reasoning": "high", "role": "primary_critical"},
    {"sabio": "Claude Opus 4.7", "reasoning": "high", "role": "fallback_critical_1"},
    {"sabio": "Gemini 3.1 Pro", "reasoning": "high", "role": "fallback_critical_2"},

    # quality_floor 0.75-0.9 (alto):
    {"sabio": "Grok 4 Heavy", "role": "realtime_xdata_high"},
    {"sabio": "Kimi K2.6 Thinking", "role": "multi_swarm_high"},
    {"sabio": "DeepSeek R1", "role": "opensource_high"},

    # quality_floor 0.6-0.75 (medio):
    {"sabio": "Sonar Pro", "role": "web_grounding_med"},
    {"sabio": "Copilot 365", "role": "m365_compliance_med_via_Azure"},
]
```

**Caveat T2-B Sesión 2:** Copilot 365 NO es raw LLM API. Via Azure OpenAI deployment cuando compliance/M365 lo requiere. Safety net solo lo invoca si vertical declara `requires_m365_compliance=True`.

### 2.4 Quality_floor declarativo escalation

```python
class QualityFloor:
    CRITICAL = 0.95   # CIP financiero, decisiones magnas, DSCs canonization
    HIGH = 0.85       # Embrión loop, brand engine VETO
    MEDIUM = 0.7      # Bulk processing, cache warming
    LOW = 0.5         # Telemetry summarization, log compaction
```

### 2.5 Anti-bloqueo + human-loop

Si N retries (default N=3) + safety net agotado:
- abort grácil con error tipado
- bridge file `human_loop_requests/<timestamp>_remontoir_blocked_<consumer>.md`
- App Flutter notifica Alfredo

**NO impone bloqueo silencioso.** Honra detonante T1 *"no quiero imponer algo que alente a bloquee un proceso"*.

---

## 3. Tareas T0-T9

### T0 — Audit kernel existing (Ejecutor 2 — 15-20 min)

**perfil_riesgo:** read-only audit

Mapear binariamente:
- `kernel/adaptive_model_selector.py` qué función hace
- `kernel/main.py` grep `model_selection|select_model|claude-|gpt-|gemini-|grok-|deepseek-|sonar-|kimi-` call sites
- `kernel/validation/perplexity_decorator.py` patrón existente DSC-V-001
- `kernel/response_cache.py` API actual (pieza #7 parcial)

Reporte forensic JSON en `reports/remontoir_pre_sprint_audit.json` con decisión binaria: **reemplazar adaptive_model_selector** o **componer/extender**.

### T1 — Migración SQL `embrion_model_decision_log` (15-20 min)

**perfil_riesgo:** write-risky

`migrations/sql/0031_embrion_model_decision_log.sql`:

```sql
CREATE TABLE IF NOT EXISTS public.embrion_model_decision_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    consumer TEXT NOT NULL,
    quality_floor NUMERIC(3, 2) NOT NULL CHECK (quality_floor BETWEEN 0 AND 1),
    budget_remaining_at_request NUMERIC(10, 6) NOT NULL,
    vertical TEXT NOT NULL,
    decision_source TEXT NOT NULL CHECK (decision_source IN ('perplexity_dynamic', 'rubies_cache_hit', 'safety_net_hardcoded', 'human_loop_abort')),
    model_selected_sabio TEXT NOT NULL,           -- nombre Sabio canónico DSC-V-001 (verbatim doctrina viva)
    model_selected_id TEXT NOT NULL,              -- model_id concreto (ej: gpt-5.5-pro-reasoning-high)
    quality_estimated NUMERIC(3, 2) CHECK (quality_estimated IS NULL OR quality_estimated BETWEEN 0 AND 1),
    cost_estimated_usd NUMERIC(10, 6),
    perplexity_validation_id UUID,                -- FK a validation_log si vino de Perplexity dinámico
    cache_key TEXT,                               -- key Rubíes si vino de cache
    cache_ttl_remaining_seconds INTEGER,
    fallback_chain_depth INTEGER NOT NULL DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_remontoir_log_created ON public.embrion_model_decision_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_remontoir_log_consumer ON public.embrion_model_decision_log (consumer);
CREATE INDEX IF NOT EXISTS idx_remontoir_log_decision_source ON public.embrion_model_decision_log (decision_source);

ALTER TABLE public.embrion_model_decision_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS embrion_model_decision_log_service_role_only ON public.embrion_model_decision_log;
CREATE POLICY embrion_model_decision_log_service_role_only ON public.embrion_model_decision_log
    FOR ALL TO service_role USING (true) WITH CHECK (true);
```

**Modelo doctrinal:** copy-paste patrón `0018_catastro_repos.sql` (T2-B Sesión 1 reconoció como modelo) + DO blocks idempotentes + REVOKE/GRANT explícito.

### T2 — Core `kernel/remontoir/dynamic_decisor.py` (30-40 min)

**perfil_riesgo:** write-risky (corazón decisor)

```
kernel/remontoir/
  __init__.py
  dynamic_decisor.py        # clase RemontoirDecisor + select_model() con @requires_perplexity_validation
  safety_net.py             # SAFETY_NET_CHAIN_8_SABIOS_VERBATIM + escalation policy
  cache_integration.py      # wrapper sobre response_cache.py para decisiones modelo
  human_loop.py             # abort grácil + bridge file generation
```

API:

```python
class RemontoirDecisor:
    async def select_model(
        consumer: str,
        quality_floor: float,
        budget_remaining: Decimal,
        vertical: str,
    ) -> ModelSelection:
        # 1. Try cache Rubíes (pieza #7)
        # 2. Si miss: @requires_perplexity_validation decisor dinámico
        # 3. Si Perplexity falla: safety_net hardcoded chain
        # 4. Si todo falla: human_loop abort
        # Persistir en embrion_model_decision_log con decision_source
```

### T3 — Safety net hardcoded chain (15-20 min)

**perfil_riesgo:** write-safe (constantes verbatim doctrina viva)

Ver §2.3. Cadena 8 Sabios canónicos verbatim CLAUDE.md doctrina viva. **NO** versiones modificadas por costo — doctrina viva es source of truth para safety net. Decisor dinámico podrá elegir versiones más económicas en tiempo real cuando quality_floor lo permite.

### T4 — Cache Rubíes integration (20-25 min)

**perfil_riesgo:** write-risky (toca pieza #7 parcial)

Wrapper `kernel/remontoir/cache_integration.py` que usa `kernel/response_cache.py` existing API + agrega:
- Key normalization `(quality_floor_tier, vertical, budget_tier_quintile)`
- TTL 24h default per-decision
- Event-driven invalidation (modelo nuevo lanza)

### T5 — Quality_floor escalation policy (10-15 min)

**perfil_riesgo:** write-safe

`kernel/remontoir/escalation.py`:
- Class QualityFloor con constants CRITICAL/HIGH/MEDIUM/LOW
- Mapping vertical → default quality_floor (CIP=CRITICAL, LIKETICKETS=HIGH, MUNDO_DE_TATA=MEDIUM, etc.)
- Anti-bloqueo: N=3 retries máximo antes de human_loop

### T6 — Wiring `embrion_loop.py` markers REMONTOIR_BEGIN/END (15-20 min)

**perfil_riesgo:** write-risky (DSC-MO-006 v1.1 doctrina del silencio)

Identical patrón ROTOR + ESCAPE + ESPIRAL. Cero modificaciones fuera de markers. Si adaptive_model_selector existing tiene call sites, T0 audit decide replace o compose:
- Replace: REMONTOIR_BEGIN/END absorbe call sites adaptive
- Compose: REMONTOIR_BEGIN/END wraps adaptive_model_selector

### T7 — Dashboard `kernel/dashboards/remontoir_history.py` (15-20 min)

**perfil_riesgo:** write-safe

Visualiza:
- 24h/7d/30d veredicto distribution (perplexity_dynamic vs rubies_cache_hit vs safety_net vs human_loop_abort)
- Quality estimated trend per quality_floor tier
- Cost saved per día por cache hit Rubíes
- Fallback chain depth histogram

### T8 — Postmortem placeholder + DSC-MO-016 candidato (10 min)

DSC-MO-016 candidato: **decisor dinámico vs hardcoded estático** — decisión post-7-días-prod. Mide hit rate cache + accuracy Perplexity + frequency human_loop. Si dinámico no aporta valor mensurable post-7-días, downgrade a hardcoded.

### T9 — Reporte cierre DSC-G-008 v3 §4 obligatorio (10-15 min)

Ver §7 + frase canónica:

`⚖️ REMONTOIR-001 v3 — DECLARADO (10/10 verde) — decisor dinámico tiempo real activo + Reloj Suizo 8/8 piezas estructurales`

---

## 4. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Tarea |
|---|---|---|
| DSC-V-001 (validación Perplexity decorator) | `@requires_perplexity_validation` aplicado en decisor dinámico | T2 |
| DSC-G-005 (validación tiempo real obligatoria) | Decisor consulta tiempo real cuando quality_floor crítico | T2 |
| DSC-MO-006 v1.1 (doctrina del silencio) | Markers REMONTOIR_BEGIN/END | T6 |
| DSC-MO-010 (Reloj Suizo 8/8) | Pieza Remontoir implementada con decisor dinámico | T2-T6 |
| DSC-G-008 v3 §4 (deducir consecuencias) | §3 + §4 explícito en reporte final | T9 |
| DSC-S-006 v1.1 (RLS) | embrion_model_decision_log RLS service_role_only | T1 |
| DSC-S-012 (anti-deriva migraciones) | Migration en main pre-prod | T1 |
| DSC-MO-011 (Embryo Patch Lane) | Markers reversibles | T6 |

---

## 5. Criterios de cierre verde

- 10 tareas exit 0 con artifacts + tests verde
- 30+ tests passing sin DB ni red
- Decisor dinámico tested con mock Perplexity + cache hit/miss + safety net fallback + human_loop abort
- Quality_floor escalation tested 4 niveles (CRITICAL/HIGH/MEDIUM/LOW)
- Wiring marcado REMONTOIR_BEGIN/END en embrion_loop.py
- Tabla creada en prod + RLS verificado
- Dashboard HTML generado contra prod
- Cowork audita DSC-G-008 v3 §4 verde + T2-B PBA convergente
- Frase canónica cerrada

## 6. Owner y timing

**Owner técnico principal:** Manus Hilo Ejecutor 2 (post-ESPIRAL-001 merge)
**Owner arquitectónico:** Cowork T2-A (audit DSC-G-008 v3 §4 + PBA Perplexity T2-B trigger 3)
**Owner verificación independiente:** Perplexity T2-B (PBA pre-merge)
**Owner humano final:** Alfredo T1 (firma + decisión override CI si aplica)
**Timing:** post ESPIRAL-001 cerrado. ETA 120-150 min reales.

## 7. Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint REMONTOIR-001 v3 CERRADO. Pieza Constant Force #8 Reloj Suizo activa con DECISOR DINÁMICO tiempo real (DSC-V-001 @requires_perplexity_validation) + cache Rubíes TTL 24h + safety net 8 Sabios doctrina viva verbatim + human_loop anti-bloqueo. NO hardcoded fallback chain estática (v1 fabricada deroada). v3 detonado T1 insight magno: decisiones magnas "necesitamos que la IA lo decida con razonamiento potente cruzado con validación tiempo real". Reloj Suizo 8/8 piezas estructurales con Remontoir cerrado simbólicamente.',
  'manus-hilo-ejecutor-2',
  10
);
```

## 8. Out-of-scope post-cierre

- DSC-MO-016 decisión dinámico vs hardcoded post-7-días (placeholder T8)
- Catastro D1+D2 (8 vs 6 Sabios + DSC-V-001 dual) polish doctrinal post-REMONTOIR
- RUBIES-001 expansion pieza #7 cache semántica magna (Cowork integrará con cache_integration.py de este sprint)

---

**Firma:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa, 2026-05-12 ~11:45 UTC
**Spec magno arquitectónico v3.** Honra detonante T1 insight magno sobre decisor dinámico tiempo real. Deroga v1 hardcoded fabricado. Reloj Suizo doctrinal cerrado en patrón decisor cuando este sprint cierre verde.
