---
id: sprint_PAR_BICEFALO_001_brand_engine
fecha_spec: 2026-05-11
arquitecto: Cowork T2
ejecutor: Manus Ejecutor 2 (= Hilo B = manus_hilo_b)
autoridad_T1: Alfredo aprobó 2026-05-11 (chat directo: "ok me parece bien aun no entiendo bien como funcionarian pero confio, vamos a hacerlo")
estado: spec_firme_listo_para_arranque
prioridad: P0
duracion_estimada: 4-6 horas Manus (1 sprint completo)
desbloquea:
  - DSC-MO-006 par bicéfalo a producción
  - DSC-G-014 "v1.0 PRODUCTO COMERCIALIZABLE" deja de ser bloqueante
  - Obj #2 Apple/Tesla quality con gate funcional
  - Obj #11 Multiplicación Embriones 72% → 100%
  - Capa 2 IE de ~72% a cerca de 100% con esta sola pieza
cruza_con:
  - DSC-MO-006 (Par bicéfalo siempre)
  - DSC-MO-011 (Embryo Patch Lane v1 — 9 gates obligatorios)
  - DSC-MO-010 (Reloj Suizo / Mainspring $30/día)
  - DSC-S-006 (RLS por defecto)
  - DSC-G-004 (naming canónico — prohibido service/handler/utils/helper)
  - Sprint COWORK-RUNTIME-001 (patrón "código no texto" aplicado a embriones)
referencias_paths_verificados:
  - kernel/embrion_loop.py (existente, doctrina del silencio)
  - kernel/embriones/ (carpeta existente con 7+ embriones especializados según COWORK_BASE_CONOCIMIENTO)
  - kernel/embrion_self_verifier.py (existente, sirve como template arquitectónico)
  - kernel/embrion_write_policy.py (existente, patrón HITL replicable)
  - migrations/sql/0011_rls_catastro_vision_generativa.sql (último número aplicado)
notificacion_embrion_memoria_pendiente: a insertar tras commit de este spec
---

# Sprint PAR_BICEFALO_001 — Brand Engine como segundo embrión

## Decisión T1 canónica

Alfredo (T1) aprobó 2026-05-11 que el segundo Embrión del par bicéfalo sea **Brand Engine**. Decisión irreversible salvo orden T1 explícita posterior. Default T2 ratificado por T1.

## Identidad del segundo Embrión

**Nombre:** Brand Engine
**Naming técnico:** `brand_engine` (cumple DSC-G-004, no usa service/handler/utils)
**Rol arquitectónico:** validador VETO sobre output del Embrión 1 antes de salir al transport
**Personalidad:** implacable, preciso, magnánimo (Brand DNA del Monstruo aplicado a sí mismo)
**No es:** generador de respuesta, ni decisor de contenido, ni curador de memoria
**Es:** filtro de calidad de output, gate canónico Apple/Tesla, anti-PR-friendly

## Arquitectura técnica

### Flujo del par bicéfalo

```
Trigger (mensaje_alfredo, latido_autonomo, etc.)
       │
       ▼
Embrión 1 (existente, kernel/embrion_loop.py)
   - Self-Verifier 3D pre-LLM
   - Pre-Verifier de INPUT (PR #101 cuando se active)
   - Genera respuesta vía LLM
   - Self-Verifier post-LLM
       │
       ▼ (respuesta candidata)
Brand Engine (NUEVO, kernel/embriones/brand_engine.py)
   - Validación 4D (tono, honestidad, doctrina, calidad)
   - Decisión: APPROVED | REJECTED | TIMEOUT
       │
       ├─ APPROVED → output sale al transport (Flutter/Telegram/WhatsApp)
       │
       └─ REJECTED → vuelve al Embrión 1 con razón estructurada
                     - Reintento máx 2 veces (control de costo)
                     - Si supera reintentos, sale con tag silencio_brand_veto
```

### Las 4 dimensiones de validación

| Dimensión | Qué evalúa | Criterio binario | Falla si |
|---|---|---|---|
| **D1 Brand DNA tono** | ¿La voz suena a Monstruo o a chatbot genérico? | Reconocible Monstruo (forja+graphite+acero, directo, magnánimo) | Voz corporativa, frases tipo "estoy aquí para ayudarte" |
| **D2 Honestidad pura** | ¿Admite lo que no sabe o infla? | Reconoce limitaciones explícitamente | Aproximaciones presentadas como certezas, "claro que sí" sin evidencia |
| **D3 Consistencia doctrinal** | ¿Contradice algún DSC canonizado? | Cero contradicción con DSCs `estado=firme` | Cita doctrina inventada, niega DSCs existentes |
| **D4 Calidad Apple/Tesla** | ¿Pasaría el test "esto daría orgullo en keynote"? | Craft visible, no rellenado | Listas largas innecesarias, repetición, formato sobre-cargado |

Las 4 son evaluadas por **un Sabio canónico interno** (Claude Opus 4.7 default, fallback GPT-5.5 Pro si Anthropic API falla). NO LLM-as-judge externo no controlado.

### Configuración runtime

Archivo `kernel/embriones/brand_engine_config.yaml` con criterios EXPLÍCITOS por dimensión:

```yaml
brand_engine_v1:
  enabled: false  # Blue-Green por default
  mode: shadow    # shadow|enforce
  evaluator_llm: claude-opus-4.7
  evaluator_fallback: gpt-5.5
  max_reintentos_embrion_1: 2
  budget_diario_usd: 10.0
  budget_alerta_telegram_usd: 8.0
  budget_kill_switch_usd: 12.0
  dimensiones:
    D1_brand_tono:
      enabled: true
      umbral_pass: 0.7
      criterios:
        - "voz Monstruo reconocible (directo, magnánimo, implacable)"
        - "evita frases corporativas-genéricas tipo 'estoy aquí para ayudarte'"
        - "evita disclaimers innecesarios de IA"
    D2_honestidad_pura:
      enabled: true
      umbral_pass: 0.8
      criterios:
        - "admite explícitamente lo que no sabe"
        - "cita evidencia para claims factuales"
        - "no infla con 'claro que sí' sin sustancia"
    D3_consistencia_doctrina:
      enabled: true
      umbral_pass: 0.9
      criterios:
        - "no contradice DSCs estado=firme"
        - "no inventa canonizaciones nuevas"
        - "no usa naming prohibido DSC-G-004"
    D4_calidad_apple_tesla:
      enabled: true
      umbral_pass: 0.7
      criterios:
        - "craft visible (no rellenado)"
        - "estructura mínima necesaria"
        - "evita listas largas innecesarias"
```

Alfredo (T1) puede editar este archivo en cualquier momento. Los criterios son entrenables, no rígidos.

### Tabla nueva: `embrion_validation_log`

Migración `migrations/sql/0012_embrion_validation_log.sql`:

```sql
BEGIN;

CREATE TABLE public.embrion_validation_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    embrion_1_memoria_id UUID REFERENCES public.embrion_memoria(id),
    respuesta_candidata TEXT NOT NULL,
    veredicto TEXT NOT NULL CHECK (veredicto IN ('approved','rejected','timeout','error')),
    d1_brand_tono_score NUMERIC(3,2),
    d2_honestidad_score NUMERIC(3,2),
    d3_doctrina_score NUMERIC(3,2),
    d4_apple_tesla_score NUMERIC(3,2),
    razon_rejection TEXT,
    sugerencia_reintento TEXT,
    reintentos_count INTEGER DEFAULT 0,
    cost_usd NUMERIC(10,6) DEFAULT 0.0,
    latency_ms INTEGER,
    evaluator_llm TEXT,
    mode TEXT NOT NULL CHECK (mode IN ('shadow','enforce'))
);

ALTER TABLE public.embrion_validation_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON public.embrion_validation_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

CREATE INDEX idx_validation_log_created_at ON public.embrion_validation_log(created_at DESC);
CREATE INDEX idx_validation_log_veredicto ON public.embrion_validation_log(veredicto);

COMMIT;
```

Aplicar vía `scripts/_apply_migration_0012.py` siguiendo template de `_apply_migration_0011.py`.

## Las 9 gates de Embryo Patch Lane (DSC-MO-011) aplicadas

| Gate | Cumplimiento en este sprint |
|---|---|
| G1 Frontera inmutable + no self-merge | ✅ Brand Engine no puede modificar `kernel/embrion_loop.py`, `kernel/embrion_self_verifier.py`, ni el config propio sin PR humano |
| G2 Regression suite determinista | Test harness 50+ casos (`tests/embriones/test_brand_engine.py`) con fixtures de respuestas conocidas pass/fail |
| G3 Sandbox sin secretos + datos sintéticos | Tests usan respuestas mockeadas, no llaman LLM real en CI |
| G4 A/B contra versión anterior | Replay sobre últimas 100 respuestas del Embrión 1 — ¿qué hubiera bloqueado Brand Engine? |
| G5 Review PR humano | Alfredo o Cowork mergea — verificación binaria de tests + diff + budget cap |
| G6 Canary deployment | `mode=shadow` por default → loguea sin bloquear → análisis 24h → `mode=enforce` |
| G7 Blue-Green | `enabled=false` por default — flag activación manual posterior |
| G8 Fuzzing diferencial | Aplicable a parser del config YAML |
| G9 Static analysis + secret scan | Hooks pre-commit existentes |

## Tareas (T1-T8)

### T1 — Estructura `kernel/embriones/brand_engine/`

Crear módulo siguiendo naming canónico DSC-G-004:
- `brand_engine.py` (clase `BrandEngine` con método `validate(respuesta_candidata) -> ValidationResult`)
- `dimensions/` (un archivo por dimensión: `brand_tono.py`, `honestidad.py`, `doctrina.py`, `apple_tesla.py`)
- `config_loader.py` (lee YAML)
- `__init__.py`

NO usar `service.py`, `handler.py`, `utils.py`, `helper.py`, `misc.py`.

### T2 — Implementar las 4 dimensiones

Cada dimensión:
- Recibe `respuesta_candidata: str` + `criterios: list[str]` + `umbral_pass: float`
- Llama al Sabio configurado con prompt estructurado
- Retorna `DimensionResult(score: float, pass: bool, reason: str|None)`

Prompts vivirán en `kernel/embriones/brand_engine/prompts/`.

### T3 — Migración SQL 0012

Aplicar la migración descrita arriba. Verificar RLS funcional con role anon, authenticated, service_role.

### T4 — Hook en `kernel/embrion_loop.py`

Wiring después de Self-Verifier post-LLM, antes de envío al transport. Solo aplica si `BRAND_ENGINE_ENABLED=true`. Fail-open: si Brand Engine lanza excepción, sale el flujo normal (no se rompe el embrión existente).

### T5 — Config YAML + loader

Implementar `config_loader.py` que lee `brand_engine_config.yaml`. Validación schema con Pydantic. Reload por request (no por startup) para que Alfredo pueda editar y ver cambios sin redeploy.

### T6 — Tests harness

50+ casos en `tests/embriones/test_brand_engine.py`:
- 10 respuestas que deben pasar las 4 dimensiones (`approved`)
- 10 respuestas con falla D1 (tono corporativo)
- 10 respuestas con falla D2 (PR-friendly inflada)
- 10 respuestas con falla D3 (contradice DSC)
- 10 respuestas con falla D4 (sobre-cargada)

LLM evaluator mockeado en CI. Solo en local con env var `BRAND_ENGINE_TEST_LIVE=true` corre contra Claude real.

### T7 — Replay A/B contra últimas 100 respuestas

Script `scripts/_brand_engine_replay_analysis.py` que:
- Toma últimas 100 filas de `embrion_memoria WHERE tipo='respuesta_embrion'`
- Aplica Brand Engine en `mode=shadow`
- Reporta cuántas hubieran sido bloqueadas + por qué dimensión
- Output a `bridge/manus_to_cowork_REPORTE_BRAND_ENGINE_REPLAY_2026_05_XX.md`

### T8 — PR a `main` + reporte cierre

PR título: `[Sprint PAR_BICEFALO_001] Brand Engine como segundo embrión (DSC-MO-006 a producción)`
Cuerpo: tests pass/fail, LOC agregadas, replay analysis resumen, costo estimado en producción, próxima activación.
Reporte cierre: `bridge/manus_to_cowork_REPORTE_PAR_BICEFALO_001_CIERRE.md`.

## Definition of Done

- ✅ 8/8 tareas T1-T8 cerradas
- ✅ Migración 0012 aplicada en producción + RLS verificada
- ✅ 50+ tests passing
- ✅ Replay analysis ejecutado y reportado
- ✅ PR mergeado a main por Cowork bajo verificación binaria
- ✅ `BRAND_ENGINE_ENABLED=false`, `BRAND_ENGINE_MODE=shadow` por default
- ✅ Activación manual posterior por decisión Cowork/Alfredo

## Restricciones duras

- **No tocar `kernel/embrion_loop.py` más allá del hook necesario** (doctrina del silencio)
- **No tocar `apps/mobile/`** (Hilo Ejecutor Oficial trabajando en MOBILE_1B PR #92)
- **No tocar `cowork/canonization-jornada-2026-05-10`** (directiva c2aab4aa)
- **No rotar claves/secrets** (decisión T1 explícita 2026-05-11)
- **No exceder budget cap diario $10 USD** durante desarrollo (test live solo con env var explícita)
- **DSC-G-004 naming canónico** (cero service/handler/utils/helper/misc)

## Output esperado del Hilo Ejecutor 2

`bridge/manus_to_cowork_REPORTE_PAR_BICEFALO_001_CIERRE.md` con:
- 8 tareas T1-T8 con commit hash de cada una
- LOC agregadas (esperado: ~800-1200 LOC kernel/embriones/brand_engine/ + ~600 LOC tests)
- Migración 0012 SHA + verificación RLS
- 50+ tests con tiempo total
- Replay analysis: cuántas respuestas bloqueadas + ejemplos
- Costo en CI vs costo proyectado en producción
- PR number + merge_commit_sha post-merge
- Cualquier ambigüedad encontrada → preguntar en bridge antes de improvisar

## Cronograma esperado

- **Hilo Ejecutor 2** arranca este sprint **después de cerrar D-2 cleanup `scheduled_tasks`** (ETA ~7h tras D-1 activación)
- Sprint completo: 4-6h reales
- Activación `mode=shadow` tras merge
- 24h de shadow → análisis → decisión sobre `mode=enforce`
- Si shadow es limpio (≥80% concordancia con expectativa Cowork) → activación enforce

## Siguiente sprint downstream

Después de `PAR_BICEFALO_001` cerrado verde + activado enforce, el siguiente sprint canónico es **Sprint 87 Pagos del Monstruo** (Stripe + Stripe Connect) para cerrar Obj #1 monetización D1. Eso completa la cadena: par bicéfalo → calidad gateada → pagos → v1.0 PRODUCTO COMERCIALIZABLE.

---

*Spec firmado por Cowork T2 Arquitecto, 2026-05-11. Bajo autoridad T1 directa de Alfredo. Sin cadencia magna excedida (este es spec ejecutable, no audit canónico — clasificación S7 "Write archivo nuevo en bridge/" = ACTUAR sin preguntar). DSC-MO-006 + DSC-MO-011 aplicados verbatim. Paths verificados binariamente esta sesión.*
