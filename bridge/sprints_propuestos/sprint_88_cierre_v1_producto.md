# Sprint 88 — Cierre v1.0 PRODUCTO COMERCIALIZABLE

**Estado:** Propuesto
**Hilo:** Ejecutor (Manus)
**ETA (recalibrado):** 30-60 min reales con velocity demostrada (Manus cierra sprints en 15 min)
**Objetivo Maestro:** #1 (Crear valor real medible) + #6 (Velocidad sin sacrificar calidad) + #14 (Guardian de los Objetivos — Critic Score)
**Bloqueos:** Ninguno
**Resultado esperado:** Critic Score ≥ 80 + traffic ingestion operando + repos GitHub Pages limpios + validación humana de Alfredo

---

## 0. Procedencia — Por qué este sprint existe

Sprint 87.2 cerró **VERDE en todo lo declarado** (commit Manus `fb6d55e`):

✅ Pipeline E2E orquestación 12/12 pasos | Capa Memento aplicada | Brand DNA error naming | Anti-Dory disciplina | Paralelismo zonificado tercer caso consecutivo | LLM-as-parser + sanitización schema | 36 tests nuevos + 80+ acumulados PASS | Migración 028 Supabase prod | ETA real 5h dentro banda

PERO en el cierre 87.2 firmamos una distinción operativa que vale firmar como semilla:

> **v1.0 BACKEND FUNCIONAL ≠ v1.0 PRODUCTO COMERCIALIZABLE.**
> - v1.0 BACKEND = orquestación E2E demostrablemente correcta → ✅ cerrado
> - v1.0 PRODUCTO = Critic Score ≥ 80 + veredicto NO `descartar` + traffic ingestion operando + repos limpios → ❌ aún NO

Critic Score actual con frase canónica de Alfredo: **1/100** (sub-scores estética 0, cta_claridad 0, profesionalismo 0). Gemini Vision juzga honestamente: el HTML que produce el pipeline NO es comercializable.

**Sprint 88 cierra esa brecha** atacando las 4 notas técnicas que Manus dejó documentadas en el cierre 87.2.

---

## 1. Audit pre-sprint — Las 4 notas técnicas con severidad real

| Nota técnica del cierre 87.2 | Severidad | Bloque que la ataca |
|---|---|---|
| Middleware bloquea `/v1/traffic/ingest` (401) | 🔴 Crítico | 3.A.1 |
| Creativo HTML 1/100 (estética + cta_claridad + profesionalismo en 0) | 🔴 Crítico | 3.A.2 |
| Repos GitHub Pages acumulados sin cleanup | 🟠 Medio | 3.B.1 |
| `provider` no propagado a `output_payload` | 🟡 Cosmético | 3.B.2 |

Severidad real evaluada contra Critic Score: las 2 críticas SÍ mueven el score, las 2 menores son hygiene de cierre.

**Velocity demostrada:** Manus cierra sprints en 15 min. Las 4 tareas son chicas + bien acotadas. ETA 30-60 min realista.

---

## 2. Bloque 3.A — Críticos (mueven Critic Score de 1 → ≥ 80)

### 3.A.1 — Bypass middleware en `/v1/traffic/ingest`

**Problema:** middleware de auth global devuelve 401 al endpoint `/v1/traffic/ingest`. El endpoint debe ser público — es ingesta de eventos de traffic externo (campañas, anuncios, attribution) que no firma con JWT.

**Solución:**
- Agregar `/v1/traffic/ingest` a la allowlist del middleware en `kernel/middleware/auth.py`
- Validación cambia de `JWT obligatorio` a `firma HMAC opcional + rate limit`
- Si HMAC presente → validar contra `TRAFFIC_INGEST_SECRET`, taggear evento como `signed=true`
- Si HMAC ausente → aceptar pero taggear como `signed=false` para auditoría posterior

**Tests:**
- `test_traffic_ingest_no_auth_passes` (200 con payload válido sin headers)
- `test_traffic_ingest_with_hmac_signs` (200 + `signed=true` en metadata)
- `test_traffic_ingest_invalid_hmac_rejects` (401 cuando HMAC viene mal firmado)
- `test_traffic_ingest_rate_limit_kicks_in` (429 después de N requests/min)

**Aceptación:** `curl -X POST .../v1/traffic/ingest` desde fuera devuelve 200 sin auth header.

---

### 3.A.2 — Conectar `kernel/embriones/creativo/` al pipeline (Path B)

**Problema:** Critic Score 1/100 viene del HTML que escupe el nodo `creativo` actual en `kernel/nodes.py`. La carpeta `kernel/embriones/creativo/` ya existe con embriones especializados (estética, cta, profesionalismo) que NO están conectados al pipeline real. Path A sería reescribir el creativo monolítico — caro y lento. Path B es conectar los embriones existentes al pipeline orchestrator.

**Solución (Path B):**
- Engine `creativo` actual queda como fallback
- Agregar `kernel/embriones/creativo/orchestrator.py` que orchestre los 3 embriones (estética → cta → profesionalismo) en cascada
- Orchestrator acepta `briefing` + `audience` + `vertical`, produce HTML con score esperado ≥ 80
- Engine `creativo` decide cuál usar según flag `EMBRYONIC_CREATIVE_ENABLED` (default true después de validación)
- Critic Score loopback: si HTML producido tiene score < 60, reintentar con embrión específico que falla más bajo

**Tests:**
- `test_orchestrator_produces_html_score_above_80` (3 verticales × 3 audiences = 9 casos)
- `test_orchestrator_fallback_when_embryon_fails` (embrión cta down → fallback al monolítico, log warning)
- `test_critic_score_loopback_retries_failing_axis` (mock score 30 en estética → reintenta hasta 80 o 3 intentos)

**Aceptación:** `Critic Score ≥ 80` validado por Gemini Vision en al menos 9/12 outputs canónicos del eval suite.

---

## 3. Bloque 3.B — Hygiene de cierre (no mueven Critic Score, pero son bloqueantes para v1.0 PRODUCTO)

### 3.B.1 — Cleanup de repos GitHub Pages acumulados

**Problema:** durante 87.x se crearon repos GitHub Pages temporales por cada eval (`monstruo-eval-XYZ`, `monstruo-creative-test-N`, etc.). Hay ~12-20 repos huérfanos en la org. Ensucian el namespace y son superficie de ataque innecesaria.

**Solución:**
- Listar repos con prefijo `monstruo-eval-*` y `monstruo-creative-test-*` en la org
- Para cada uno: verificar último commit, si > 7 días → archivar
- Si > 30 días → delete (con confirmación humana de Alfredo si > 5 deletes)
- Mantener exactamente 1 repo canónico `monstruo-pages-canonical/` para hosting de outputs canónicos del eval suite

**Aceptación:** ≤ 3 repos `monstruo-*` activos en la org post-cleanup.

---

### 3.B.2 — Propagar `provider` al `output_payload`

**Problema:** el `output_payload` que devuelve el kernel al gateway omite el campo `provider` (qué modelo procesó la request). Cosmético pero rompe debugging downstream — Alfredo no puede ver desde la app Flutter qué modelo escupió cada respuesta.

**Solución:**
- En `kernel/agui_adapter.py` agregar `provider` al schema de `output_payload`
- En `kernel/nodes.py` (nodo `execute`) propagar `state.provider` al output
- Schema de gateway/kernel actualizado en `apps/mobile/gateway/schemas.py` para reflejar el campo
- Flutter ya tiene el field en el modelo `MessageResponse` — solo falta el binding

**Tests:**
- `test_output_payload_includes_provider` (provider="claude-opus-4.7" llega íntegro)
- `test_provider_propagated_through_dispatch` (cuando hay dispatch externo, provider="perplexity")

**Aceptación:** App Flutter muestra el provider correcto debajo de cada respuesta.

---

## 4. Aceptación de cierre v1.0 PRODUCTO COMERCIALIZABLE

**Definición de Listo (las 4 tienen que ser verde simultáneo):**

1. ✅ `/v1/traffic/ingest` operando público + tests pasando (3.A.1)
2. ✅ Critic Score ≥ 80 en eval suite canónico (3.A.2)
3. ✅ Repos GitHub Pages limpios (3.B.1)
4. ✅ `provider` propagado y visible en app Flutter (3.B.2)

**Validación humana de Alfredo (mandatoria — NO solo automática):**

Sprint 88 es uno de los 2 hitos donde la cierre se firma con ojo humano (el otro es Mobile 5). Alfredo abre la app Flutter, manda un mensaje, ve la respuesta, evalúa estética + cta + profesionalismo a ojo. Si Alfredo dice "esto SÍ es comercializable" → 🏛️ **v1.0 PRODUCTO COMERCIALIZABLE — DECLARADO**.

**Reporte al bridge:** `bridge/manus_to_cowork_REPORTE_SPRINT88_<fecha>.md` con tabla de evidencia (4 filas, una por bloque) + screenshot del Critic Score loop antes/después + screenshot del eval suite canónico.

---

## 5. Semillas listas para firmar empíricamente al cierre

- **Semilla 43 — Paralelismo zonificado funcional** (3 casos empíricos consecutivos: 87.0, 87.1, 87.2 — el 4to es Sprint 88 + Catastro-B + Mobile 1 simultáneos)
- **Semilla 51 — Tests con prod real antes de declarar cierre** (anti-Dory aplicado al CI/CD — el bypass middleware se valida contra prod, no mock)
- **Semilla 53 → DSC-G-008 ya firmado** (validar codebase antes de specs — esta spec misma es ejemplo)
- **Semilla 54 — Critic Score como gate de cierre v1.0** (no es solo número informativo, bloquea cierre formal)

---

## 6. Notas técnicas

1. **Backward compatibility:** ningún cambio rompe contratos AG-UI. Provider en output_payload es campo nuevo, ya estaba en schema Flutter.
2. **Embriones creativo fallback:** si `EMBRYONIC_CREATIVE_ENABLED=false`, kernel cae al creativo monolítico — zero downtime de migración.
3. **GitHub Pages cleanup:** delete > 5 repos requiere confirmación humana — Manus no hace cleanup masivo solo.
4. **Critic Score loopback:** límite duro de 3 reintentos para evitar bucles infinitos cuando el eval no puede subir de un score plateau.

---

**Cowork (Hilo A), spec corregida 2026-05-06 post-incidente DSC-G-008**
**Spec previa CONTAMINADA por sub-agente (kernel v0.50.0, Critic Score 78, /v1/run, /v1/ingest, review_html_quality, Rollout viernes) — descartada por audit de Manus Hilo Ejecutor.**
