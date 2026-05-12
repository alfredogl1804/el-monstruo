---
id: cowork_to_manus_HILO_EJECUTOR_2_GATE_VERDE_ESPIRAL_001_KICKOFF_2026_05_12
fecha: 2026-05-12T09:00:00Z
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 2 (libre post ESCAPE-001 PR #116 mergeado)
tipo: gate_verde_kickoff_espiral_001
prioridad: P0
autoridad_T1: spec ESPIRAL-001 ratificada T1 "si avanza" 2026-05-12 ~08:38 UTC commit `0de35e6`
---

# Gate VERDE Ejecutor 2 — ESPIRAL-001 (pieza #5 magna Reloj Suizo)

## §1 Resumen ejecutivo

PR #116 ESCAPE-001 mergeado commit `5f38b9c2` con PBA T2-B convergencia 6/6 VERDE + 5 caveats verbatim declarados + Migration 0024 aplicada Supabase prod ~08:58 UTC.

**Gate VERDE para arrancar ESPIRAL-001 inmediatamente.** Spec firmado T1 ratificada commit `0de35e6` archivo `bridge/sprints_propuestos/sprint_ESPIRAL_001_homeostasis_dinamica.md`.

## §2 Pre-flight check obligatorio

```bash
cd ~/el-monstruo && git status && git pull origin main

# Verificar PR #116 mergeado:
gh pr view 116 --json state,merged
# Esperado: state=MERGED, merged=true

# Verificar tabla escape_pulse_log existe en prod:
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name='escape_pulse_log';"
# Esperado: 1

# Verificar kernel/escape/ existe:
ls kernel/escape/__init__.py kernel/escape/throttler.py kernel/escape/config.py kernel/escape/dashboard.py
# Esperado: 4 archivos

# Verificar wiring ESCAPE_BEGIN/END en embrion_loop:
grep -n "ESCAPE_BEGIN\|ESCAPE_END" kernel/embrion_loop.py
# Esperado: 2 marcadores

# Verificar siguiente migration libre (ESPIRAL T1 toma probable 0026 post-Catastro 0023+0025):
ls migrations/sql/ | sort | tail -5
```

Si pre-flight rojo, reportar bridge `bridge/manus_to_cowork_ESPIRAL_PREFLIGHT_BLOCKED_2026_05_12.md`.

## §3 Tareas T1-T6 ESPIRAL-001 (recordatorio de spec firmado)

T1: Migración `0026_embrion_homeostasis_log.sql` (15-20 min) — RLS service_role_only + sin DATE(TIMESTAMPTZ)
T2: Core `kernel/espiral/homeostasis.py` (25-35 min) — clase `Hairspring` + sense_deviation + apply_correction + return_to_canonical
T3: Wiring `embrion_loop.py` marcadores ESPIRAL_BEGIN/END (15-20 min) — análogo ROTOR + ESCAPE
T4: Integración `kernel/escape/registry.py` apply_temporal_override (15-20 min)
T5: Dashboard `kernel/dashboards/espiral_history.py` (15-20 min)
T6: Postmortem placeholder + DSC-MO-015 candidato (10 min)

**ETA target:** 80-110 min reales
**Frase canónica de cierre:** `🌀 ESPIRAL-001 — DECLARADO (6/6 verde)`

## §4 Reglas duras NO-CRUCE (estado 2026-05-12 ~09:00 UTC)

5 hilos en vuelo simultáneos. **NO tocar:**

1. **PR #110** Pre-Response Hook OBSERVE-ONLY — `feat/t1-pre-response-hook-observe-only` (Perplexity T2-B), CI pending. **NO tocar `kernel/cowork_runtime/pre_response_hook.py`.**
2. **PR #107** catastro-c-slice-001 — holding.
3. **Hilo Catastro** post MEGA-CIERRE-HOY cerrado — bandwidth libre, NO duplicar trabajo.
4. **Hilo Ejecutor 1** post TA3 Railway flags — bandwidth libre, **NO tocar `kernel/cowork_runtime/`**.
5. **Hilo Perplexity T2-B** activo PBA — disponible para próximos audits.

**SÍ podés tocar:**
- `kernel/espiral/` (crear desde cero)
- `kernel/embrion_loop.py` SOLO entre marcadores ESPIRAL_BEGIN/END (NO tocar ROTOR ni ESCAPE markers)
- `kernel/escape/registry.py` función `apply_temporal_override()` nueva (NO refactorizar core throttler)
- `kernel/dashboards/espiral_history.py` (nuevo)
- `migrations/sql/0026_embrion_homeostasis_log.sql` (verificar libre con `ls migrations/sql/`)
- `tests/test_espiral_*.py` (nuevos)

## §5 Audit DSC-G-008 v3 §4 obligatorio en reporte cierre

Al cerrar el sprint, tu reporte DEBE incluir explícitamente:
- §3 limitaciones honestas (qué NO pudiste verificar desde sandbox)
- §4 consecuencias materiales deducidas (qué podría existir bajo cada limitación + mitigación pre/post merge)

Sin §4 explícito → audit Cowork candidato a regresión post-T2-B PBA convergencia. Esta cláusula entró firme T1 2026-05-12 commit `46f0ee6`.

## §6 Permiso de merge

- **PRs write-safe** (T5 dashboard, T6 placeholder): push directo bajo DSC-G-008 v3 +6 gates VERDE +50 LOC.
- **PRs write-risky** (T1 migración, T2 Hairspring core, T3 wiring, T4 registry): PR limpio + tag `[ESPIRAL-001]`, Cowork audita DSC-G-008 v3 + T2-B PBA trigger 3.
- **Self-merge prohibido** para write-risky.

## §7 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint ESPIRAL-001 CERRADO. Pieza Hairspring/Homeostasis #5 magna Reloj Suizo activa. Feedback negativo dinámico ajusta pulse_intervals del Escape detectando deviation ventana móvil 15min. Tabla embrion_homeostasis_log RLS service_role_only. Cowork audita DSC-G-008 v3 verde + T2-B PBA convergente.',
  'manus-hilo-ejecutor-2',
  9
);
```

## §8 Autoridad y cierre

- T1 (Alfredo) ratificó firma simbólica ESPIRAL-001 2026-05-12 ~08:38 UTC ("si avanza")
- T2-A (Cowork) firma kickoff post-ESCAPE merge + apply migration prod verde
- T3 (Hilo Ejecutor 2) ejecuta autónomamente bajo §4 reglas duras

**Camino completo Reloj Suizo post-ESPIRAL:**
- REMONTOIR-001 (pieza #8 Constant Force) FIRME T1 ratificada — gate VERDE post-ESPIRAL merge
- RUBIES-001 (pieza #7 cache semántica expansión) FIRME T2-A — pipeline post-REMONTOIR cierra 8/8 piezas estructurales Reloj Suizo

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 09:00 UTC
**Gate VERDE:** ESPIRAL-001 spec FIRME T1, ESCAPE-001 PR #116 mergeado + Migration 0024 prod verde + PBA T2-B convergente. Ejecutor 2 puede arrancar T1 inmediatamente.
