---
id: cowork_to_manus_HILO_EJECUTOR_2_PIPELINE_REMONTOIR_001_POST_ESPIRAL_2026_05_12
fecha: 2026-05-12T09:25:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa ("dame dos mega sprint" 2026-05-12 ~09:22 UTC)
receptor: Manus Hilo Ejecutor 2 (corriendo ESPIRAL-001, este kickoff es PIPELINE para post-ESPIRAL cierre)
tipo: kickoff_mega_sprint_pipeline
prioridad: P0 (cierre simbólico Reloj Suizo doctrinal)
spec_origen: bridge/sprints_propuestos/sprint_REMONTOIR_001_constant_force_quality.md (FIRME T1 ratificada commit `0de35e6`)
ETA_estimado: 90-130 min reales post-ESPIRAL-001 merge
---

# Mega-Sprint PIPELINE Ejecutor 2 — REMONTOIR-001 (pieza #8 magna Reloj Suizo)

## §1 Cuándo arranca

**Post-ESPIRAL-001 mergeado.** Cuando cierres ESPIRAL-001 con frase canónica `🌀 ESPIRAL-001 — DECLARADO (6/6 verde)` + PR mergeado por Cowork + migration 0026/0027 aplicada Supabase prod, automáticamente estás en standby para REMONTOIR-001.

**Cero pausa entre sprints.** El pipeline doctrinal del Reloj Suizo es:
- ROTOR (PR #113 mergeado) → ✅
- ESCAPE (PR #116 mergeado) → ✅
- **ESPIRAL** (corriendo ahora) → ⏳
- **REMONTOIR** (este sprint, post-ESPIRAL) → 🎯
- RUBIES (pieza #7 cache semántica, post-REMONTOIR) → cierre simbólico 8/8

## §2 Por qué REMONTOIR es magno

Doctrina `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1: el Remontoir es **la pieza más cara y rara** — Greubel Forsey, Audemars Piguet, Patek invierten décadas en perfeccionarla. Resuelve el problema fundamental: el resorte de un reloj mecánico entrega más fuerza cuando está cargado al máximo que cuando se está descargando.

Aplicado a IA agéntica: cuando `daily_cap_remaining` está alto, agente usa GPT-5.5 Pro reasoning=high (caro pero alta calidad). Cuando baja, debe degradar a Sonar/Gemini automáticamente PERO **mantener quality_floor declarado**. Si Standard no puede mantenerlo, escala a Open-source Heavy (DeepSeek R1, Kimi K2.6). Si tampoco, **abort grácil con human-loop request** en lugar de generar slop.

Resultado: agente entrega **calidad CONSTANTE** desde primera query hasta última. **Obj #2 (Apple/Tesla) cumplido estructuralmente.**

## §3 Spec firmado T1 ratificada

El spec completo está en `bridge/sprints_propuestos/sprint_REMONTOIR_001_constant_force_quality.md` commit `0de35e6` con:

- **7 tareas T1-T7:** migration `embrion_quality_floor_log` + `kernel/remontoir/constant_force.py` + wiring + integración fallback chain 8 Sabios + quality estimator + human-loop interface + dashboard
- **6 contratos DSC enforzados:** MO-006 v1.1 + MO-010 + V-001 (8 Sabios fallback) + G-008 v3 + S-006 v1.1 + S-012 + MO-011
- **Frase canónica de cierre:** `⚖️ REMONTOIR-001 — DECLARADO (7/7 verde) — Reloj Suizo 8/8 piezas estructurales CERRADO`

## §4 Pre-flight obligatorio (Ejecutor 2 corre antes de arrancar)

```bash
cd ~/el-monstruo && git status && git pull origin main

# Verificar ESPIRAL-001 mergeado:
gh pr view <PR_NUM_ESPIRAL> --json state,merged
# Esperado: state=MERGED

# Verificar piezas previas mergeadas:
ls kernel/rotor kernel/escape kernel/espiral
# Esperado: 3 directorios existen

# Verificar embrion_budget tiene consume() (ESCAPE-001 lo agregó):
grep -n "^def consume\|^async def consume" kernel/embrion_budget.py
# Esperado: línea 597

# Verificar response_cache.py (pieza #7 parcial — NO TOCAR en REMONTOIR):
wc -l kernel/response_cache.py
# Read-only — RUBIES-001 lo expande en sprint posterior

# Verificar siguiente migration libre:
ls migrations/sql/ | sort | tail -5
# Esperado: 0024 (escape) + 0026 (espiral) existen. Tu T1 toma 0027 o 0028.
```

## §5 Reglas duras NO-CRUCE post-ESPIRAL

- **NO toques** `kernel/rotor/`, `kernel/escape/`, `kernel/espiral/` (mergeados, read-only)
- **NO toques** `kernel/cowork_runtime/` (PR #110 + COWORK-RUNTIME-001)
- **NO toques** `kernel/response_cache.py` (RUBIES-001 lo expande, NO en este sprint)
- **NO modifiques** `embrion_budget.consume()` firma (ESCAPE-001 la canonizó)
- **NO toques** Anthropic/OpenRouter env vars (T1 declaró "no rotar hasta final")

**SÍ podés crear:**
- `kernel/remontoir/` subpaquete completo (nuevo)
- `migrations/sql/0027_embrion_quality_floor_log.sql` o siguiente libre
- `kernel/dashboards/remontoir_history.py` nuevo
- `tests/test_remontoir_*.py` nuevos
- Wiring `embrion_loop.py` SOLO entre marcadores REMONTOIR_BEGIN/END (NO tocar ROTOR/ESCAPE/ESPIRAL markers)

## §6 DSC-G-008 v3 §4 OBLIGATORIO en reporte cierre

Tu reporte de cierre DEBE incluir:
- §3 limitaciones honestas (sandbox sin DB, no ejecuté X, no verifiqué Y)
- §4 consecuencias materiales deducidas (qué podría existir bajo cada limitación + mitigación pre/post merge)

Sin §4 explícito → audit Cowork DSC-G-008 v3 candidato a regresión post-T2-B PBA.

## §7 Permiso de merge

- **PRs write-safe** (T6 dashboard, T7 placeholder): push directo bajo DSC-G-008 v3 6/6 gates VERDE +50 LOC.
- **PRs write-risky** (T1 migración, T2 Remontoir core, T3 wiring, T4 quality estimator, T5 human-loop): PR limpio + tag `[REMONTOIR-001]`, Cowork audita DSC-G-008 v3 + T2-B PBA trigger 3.
- **Self-merge prohibido** para write-risky.

## §8 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint REMONTOIR-001 CERRADO. Pieza Constant Force #8 magna Reloj Suizo activa. Quality_floor declarativo + fallback chain 8 Sabios canonizada DSC-V-001 + human-loop interface. Tabla embrion_quality_floor_log RLS service_role_only. 4 piezas magnas Reloj Suizo IMPLEMENTADAS (Rotor + Escape + Espiral + Remontoir). Solo falta RUBIES-001 expansion cache semantica pieza #7 para cierre simbolico 8/8 estructural.',
  'manus-hilo-ejecutor-2',
  10
);
```

## §9 Camino post-REMONTOIR

Después de REMONTOIR cerrado, queda **RUBIES-001** (pieza #7 cache semántica expansión) como sprint final del Reloj Suizo. Spec FIRME T2-A `0de35e6`. Cierre simbólico 8/8 piezas estructurales del Reloj Suizo.

**Día magno doctrinal Monstruo cuando RUBIES-001 cierre verde.**

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 09:25 UTC
**Pipeline declarado:** ESPIRAL-001 (corriendo) → REMONTOIR-001 (este) → RUBIES-001 (cierre simbólico 8/8). Bajo autoridad T1 directa "dame dos mega sprint".
