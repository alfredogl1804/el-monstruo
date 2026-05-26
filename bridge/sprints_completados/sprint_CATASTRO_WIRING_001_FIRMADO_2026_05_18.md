---
sprint_id: CATASTRO-WIRING-001
version: v1
titulo: Wiring real /v1/catastro/recommend ↔ Embrión Loop (audit binario + fix si aplica)
estado: 🟢 FIRMADO — Cowork T2-A bajo autorización T1 magna "firmo 5" 2026-05-18
autor_spec: Cowork T2-A
fecha_firma: 2026-05-18
owner_ejecucion: Manus Hilo Catastro
trabajo_previo: bridge/manus_to_cowork_HILO_CATASTRO_REACTIVACION_2026_05_18.md (drift binario 0/3 + 2 hipótesis ranked)
gate_arranque: este spec firmado + invariantes Catastro respetadas
hermanos_doctrinales: DSC-MO-009 (arsenal seleccionable Catastro), DSC-G-008 v4 (audit), DSC-S-016 (anti-fabricación)
---

# Sprint CATASTRO-WIRING-001 — Wiring real /v1/catastro/recommend ↔ Embrión Loop

> **Objetivo magno:** validar binariamente si el Embrión Loop consume la recomendación del Catastro al elegir modelo/agente. Si no consume → fix wiring. Si consume → validar invariante (ranking respetado, sin override hardcoded). Cierra dependencia magna entre 2 sistemas vivos del Monstruo.

## §1 Problema binario observado

Bridge Catastro 2026-05-18 confirma drift binario 0 en 3/4 entidades + 39 LLMs production + 98 agentes con `trono_global`, `fortalezas`, `debilidades`, `capacidades`. **El Catastro está vivo y completo.**

PERO **NO está confirmado** que `kernel/embrion_loop.py` consuma `/v1/catastro/recommend` al elegir modelo o agente para una tarea. Si no consume:
- 39 LLMs + 98 agentes en DB son **peso muerto** (datos sin consumidor real)
- Cualquier decisión Embrión usa hardcoded → viola DSC-MO-009 (arsenal seleccionable)
- F21 estructural latente: Catastro canonizado, consumidor inexistente

## §2 Objetivo binario del sprint

**Validar empíricamente si el invariante "Embrión consume Catastro para selección modelo/agente" se cumple en producción.**

Output binario esperado:
- **CASO A:** Embrión NO consume → bridge reporta hallazgo + fix wiring spec (mini-PR `kernel/embrion_loop.py`)
- **CASO B:** Embrión SÍ consume pero hay override hardcoded → bridge reporta override + fix scope mínimo
- **CASO C:** Embrión SÍ consume sin override → bridge reporta verde + cierre formal invariante

## §3 Métricas de éxito binarias

| # | Métrica | Esperado |
|---|---|---|
| 1 | Audit grep estático `embrion_loop.py` | `grep -nE "catastro\|/v1/catastro/recommend"` retorna ≥1 hit o 0 hits (binario observable) |
| 2 | Audit runtime: ¿se llama el endpoint en path de selección? | trace Langfuse + log structured: invocación contada por turno embrión ≥0 |
| 3 | % decisiones Embrión que pasan por Catastro | numerador: invocaciones `/v1/catastro/recommend` / denominador: decisiones de modelo o agente en ventana 1h |
| 4 | Override hardcoded detectado | `grep -nE "model.*=.*['\"]\w+['\"]" embrion_loop.py` con scope filtrado |
| 5 | Bridge reporta CASO A/B/C binario con evidencia | path bridge + commit hash referenciado |

**Threshold éxito sprint:**
- **CASO A:** mini-PR fix wiring mergeado + verificación post-merge invariante 100% (todas las decisiones pasan por Catastro)
- **CASO B:** override removido O justificado con DSC explícito
- **CASO C:** reporte binario + DSC nuevo "invariante Catastro→Embrión validado" firmado Cowork

## §4 Archivos esperados a tocar

**SOLO READ (auditoría binaria):**
- `kernel/embrion_loop.py` (grep + análisis estático)
- `kernel/cowork_runtime/` (si Catastro se invoca desde Cowork también)
- `apps/*/` (consumidores potenciales)
- Logs Langfuse + Supabase `run_costs` traces

**SOLO WRITE (si CASO A o B requiere fix):**
- `kernel/embrion_loop.py` (mini-PR con marker `CATASTRO_WIRING_BEGIN/END`)
- `tests/test_catastro_wiring.py` (test de regresión: invariante "selección pasa por Catastro")
- `bridge/manus_to_cowork_HILO_CATASTRO_WIRING_001_RESULT_<fecha>.md` (reporte)

**NO TOCAR:**
- ❌ Catastro tablas DB (audit-only, sin DELETE/UPDATE de modelos/agentes/dominios)
- ❌ `/v1/catastro/recommend` endpoint (asumimos correcto si responde 200 con ranking válido)
- ❌ Pagos / Stripe / cuentas reales
- ❌ APP_VISION / PRE-IA
- ❌ Migrations nuevas

## §5 Pre-flight checks obligatorios

Antes de arrancar audit:

```bash
# Verificar Catastro tablas presentes
psql -c "SELECT count(*) FROM catastro_modelos WHERE estado='production';"
# Esperado: 39

# Verificar endpoint /v1/catastro/recommend responde
curl -X POST https://el-monstruo-kernel.up.railway.app/v1/catastro/recommend \
  -H "Content-Type: application/json" \
  -d '{"task_type": "test", "constraints": {}}'
# Esperado: 200 con ranking JSON

# Inventario estático embrion_loop.py
grep -nE "catastro|recommend" kernel/embrion_loop.py
# Esperado: ≥1 hit O 0 hits (binario)

# Verificación coherence gate Nivel A (DSC-G-013 v0.1, CLAUDE.md Paso 0.B)
ls migrations/sql/ | tail -3
# No aplica acción magna directa, pero buen check estructural
```

## §6 Snapshot forense (si aplica — DSC-S-005)

- **CASO A** (fix wiring): snapshot pre-PR del `embrion_loop.py` actual + sample de 10 decisiones reciente del Embrión registradas en logs. Path: `discovery_forense/INCIDENTES/CATASTRO_WIRING_001_pre_fix_<fecha>.json`.
- **CASO B** (override removido): snapshot del override actual + razón documentada antes de remover. Path mismo formato.
- **CASO C** (verde): NO requiere snapshot (no se modifica nada).

## §7 Cierre verde — gates DSC-G-008 v4

Audit Cowork DSC-G-008 v4 sobre cualquier mini-PR resultante:
- G1 diff línea por línea (espera <50 LOC en CASO A, <20 LOC en CASO B)
- G2 feature flag si fix tiene shadow mode (no obligatorio si fix es trivial)
- G3 cero secrets
- G4 test regresión presente (`test_catastro_wiring.py`)
- G5 scope limpio (NO toca pagos, NO toca migrations)
- G6 no-duplicate de main
- §4 (v4) error-path coverage para LLM calls (Catastro recommend timeout/error → fallback verbatim documentado)

## §8 Limitaciones declaradas (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_W1 | Audit estático grep puede tener falsos negativos (strings dinámicos, imports indirectos) | Combinar grep + runtime trace Langfuse + log structured (3 fuentes ortogonales) |
| L_W2 | "100% decisiones pasan por Catastro" puede ser difícil de medir si Embrión cachea recomendaciones | Definir "decisión Catastro-mediada" = "consulta Catastro O usa cache <24h de Catastro" |
| L_W3 | Endpoint /v1/catastro/recommend puede tener bugs propios (out of scope) | Spec follow-up `CATASTRO-ENDPOINT-AUDIT-001` si Manus detecta bug en endpoint |
| L_W4 | CASO B (override hardcoded) puede tener razón legítima histórica | Manus reporta razón verbatim — Cowork decide si justifica DSC o requiere fix |
| L_W5 | Si Embrión está caído (kernel Railway), audit runtime no es posible | Fall-back: audit estático solo (CASO 0) + retry runtime cuando Embrión esté UP |

## §9 NO-CRUCE reglas duras

- ❌ NO modificar tablas Catastro (audit-only)
- ❌ NO modificar `/v1/catastro/recommend` endpoint
- ❌ NO drop tablas legacy duplicadas (es Rank 2, sprint separado)
- ❌ NO activar nuevos feature flags Railway sin firma T1 adicional
- ❌ NO touch `kernel/cowork_runtime/` (CRUZ-001 + VERIFICADOR-001 colisión inter-sprint)
- ✅ SÍ extender `embrion_loop.py` con markers `CATASTRO_WIRING_BEGIN/END` si fix requerido
- ✅ SÍ agregar `tests/test_catastro_wiring.py` nuevo
- ✅ SÍ usar coherence gate Nivel A DSC-G-013 v0.1 antes de cualquier action de riesgo

## §10 Hallazgo lateral del Catastro (no bloqueante, registrado)

Manus detectó schema drift en prompt T1 original:
- `catastro_llms` (no existe) → real es `catastro_modelos`
- `estado='vivo'` (no existe) → real es `'production'` o `'open-source'`
- `catastro_dominios` (no es tabla) → real es campo array
- `catastro_vision_generativa` (2 esperados) → real 38 herramientas paralelas

**Recomendación post-sprint:** actualizar catálogo canónico Alfredo (cualquier doc que tenga estos nombres) para reflejar schema real. **NO scope de este sprint** — registro doctrinal en `COWORK_DECISIONES_VIVAS.md` próxima sesión.

## §11 Owner + cadencia

**Owner ejecución:** Manus Hilo Catastro.

**Cadencia esperada:**
- Día 1 (~3-4h): audit estático + runtime trace + clasificación CASO A/B/C
- Día 1-2 (~2-4h si CASO A o B): mini-PR fix + tests + audit Cowork DSC-G-008 v4
- Día 2 (~1h): merge + verificación post-merge + bridge cierre

**Total estimado:** 5-8h (sprint S).

## §12 Trayectoria post-firma

1. **HOY:** Manus Catastro arranca audit (sin tocar código). Bridge intermedio en 1-2h con clasificación CASO A/B/C.
2. **HOY+2-4h:** si CASO A o B → bridge con propuesta mini-PR + audit Cowork DSC-G-008 v4.
3. **HOY+4-8h:** merge + bridge cierre + frase canónica.
4. **POST-SPRINT:** decisión sobre Rank 2 cleanup legacy (sprint separado, deuda técnica).

---

**Status:** `🟢 FIRMADO — Manus Catastro arranca cuando esté ready`
**Cowork T2-A firma con autoridad delegada T2 bajo autorización T1 magna "firmo 5" verbatim 2026-05-18.**

**Sources:**
- Bridge reactivación Catastro: [`manus_to_cowork_HILO_CATASTRO_REACTIVACION_2026_05_18.md`](https://github.com/alfredogl1804/el-monstruo/blob/monstruo-reality-atlas-001/bridge/manus_to_cowork_HILO_CATASTRO_REACTIVACION_2026_05_18.md)
- DSC-MO-009 arsenal seleccionable Catastro
- DSC-G-008 v4 audit doctrine
- DSC-G-013 v0.1 coherence gate Nivel A (CLAUDE.md Paso 0.B)
