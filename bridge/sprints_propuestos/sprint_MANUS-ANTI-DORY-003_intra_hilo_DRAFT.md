---
sprint_id: MANUS-ANTI-DORY-003
version: v0.1
titulo: Anti-Dory Pieza 5 — degradación intra-hilo de un mismo agente Manus
estado: 🟡 DRAFT — espera convergencia 3 Sabios + firma T1
autor_spec: Cowork T2-A
fecha_draft: 2026-05-18
autorizacion_t1: "firmo 5" verbatim 2026-05-18 (MAGNA-CIERRE-002)
pieza_anti_dory: 5 (NUEVA — ortogonal a las 4 actuales)
hermanos: PIEZAS 1-4 Anti-Dory (cross-agente, MEMENTO calibration, CRUZ-001 cross-sesión Cowork, VERIFICADOR-001 pre-emit blocking)
caveat_titulo: "Anti-Dory intra-hilo Manus — degradación contextual de un mismo agente a lo largo de horas. No es cross-agente ni cross-sesión."
---

# MANUS-ANTI-DORY-003 v0.1 — Anti-Dory intra-hilo Manus

> **Hipótesis:** Un mismo hilo Manus (E1, E2, Catastro) acumula degradación contextual a lo largo de una sesión multi-hora — modelo mental desactualizado de estado del repo, asunciones sobre numeración/nombres, drift de scope. Las 4 piezas Anti-Dory actuales NO cubren este vector porque atacan cross-agente o cross-sesión, no intra-hilo.

## §1 Problema binario observado

**Evidencia magna fresca HOY 2026-05-17/18:**

### §1.1 F#15 — Manus E2 numeración off by 10

Manus E2 acabó de aplicar migrations 0038-0046 (LA-FORJA D5.1) en su hilo. Horas después en el mismo hilo, propuso numerar H13 como 0037 + H14 como 0036. Realidad binaria: ambos números ocupados. **Drift planning↔reality dentro del mismo hilo del mismo agente.**

Esto NO es drift cross-agente (1 sola entidad) ni cross-sesión (1 sola sesión). Es **degradación intra-hilo** — el contexto del propio Manus E2 quedó stale respecto al estado del repo que él mismo modificó horas antes.

### §1.2 Bleed scope LA-FORJA-001 D5.2

Manus E2 cherry-picked de rama equivocada que incluía commit `600d05a` ajeno al sprint D5.2. Detectado por Cowork pre-merge (rebase quirúrgico requerido). **Drift planning↔HEAD branch dentro del mismo hilo.**

### §1.3 Otros casos documentados pre-HOY

- D5 RAP-001 HTTP 400: Manus E1 sent `{prompt: ...}` payload incorrecto (formato deprecated del mismo módulo que él había refactorizado en sprints previos)
- D5-RETEST HTTP 404: `project_id="el_monstruo"` asumido por Manus E1 — no existía en su account Manus (que él mismo configuró)

**Patrón común:** Manus modifica su entorno operativo + horas/turnos después olvida el cambio + asume estado pre-modificación.

## §2 Diferencia binaria vs PIEZAS 1-4

| Pieza | Vector cubierto | Cobertura intra-hilo |
|---|---|---|
| **1** MANUS-ANTI-DORY-002 (D5 GREEN) | Cross-agente Manus | ❌ No cubre |
| **2** MEMENTO calibration | Cross-output Cowork (log) | ❌ No cubre |
| **3** CRUZ-001 (firmada) | Cross-sesión Cowork | ❌ No cubre |
| **4** VERIFICADOR-001 (firmada) | Pre-emit Cowork blocking | ❌ No cubre |
| **5 (este)** | **Intra-hilo Manus degradación** | ✅ Único vector restante |

Las 4 piezas actuales atacan Dory cross-entity. La PIEZA 5 ataca Dory intra-entity multi-hora.

## §3 Diseño binario propuesto (3 alternativas pre-Sabios)

### §3.1 Alternativa A — Pre-flight intra-hilo cada N turnos

Manus DEBE ejecutar mini pre-flight cada **N=10 turnos** o cada **2h** (lo que ocurra primero):

```bash
# Refresh estado operativo del repo del hilo
git fetch origin && git log --oneline origin/main..HEAD
ls migrations/sql/ | tail -5

# Refresh modelo mental del estado de tareas
gh pr list --state open --author @me | head -5
```

Output del refresh debe **modificar el modelo mental** del agente (escribir/leer notas in-context).

### §3.2 Alternativa B — Snapshot persistente intra-hilo

Cada hilo Manus persiste un `manus_thread_snapshot` cada N minutos a `thread_snapshots` (tabla ya existente PIEZA 1) con:
- Último PR mergeado por este hilo
- Último número migration aplicada por este hilo
- Branch HEAD actual
- Modelo mental: "creo que próximo libre es X"

Pre-acción magna, Manus consulta su propio snapshot + verifica drift contra realidad fresca.

### §3.3 Alternativa C — Híbrida (recomendada Cowork pre-Sabios)

A + B combinadas:
- A: pre-flight ligero cada N turnos (rápido, in-memory)
- B: snapshot persistente cada 30min (lento, durable, recuperable post-crash)

Costo: ~10% overhead operativo. Beneficio: cierra el último vector Dory documentado.

## §4 Acceptance criteria binarios

| # | Check | Comando |
|---|---|---|
| 1 | Mini pre-flight ejecutado cada N=10 turnos en hilo Manus | grep registro `manus_intra_preflight_executed` en `runtime_events` |
| 2 | Snapshot persistido cada ≤30min en sesiones >1h | `SELECT count(*) FROM thread_snapshots WHERE actor_type='manus' AND created_at > now() - interval '1 hour'` ≥ 2 |
| 3 | Pre-acción magna consulta snapshot | logger output `manus_intra_snapshot_consulted=true` |
| 4 | F#15-like patterns detectados pre-acción | métrica `count_intra_drift_detected_preaction / count_intra_drift_total > 0.8` |
| 5 | Cero falsos positivos (gate bloquea acción válida) | reporte 7d post-merge: `count_false_blocks = 0` |
| 6 | Latencia overhead ≤ 10% turno medio | benchmark pre/post |

## §5 Limitaciones declaradas (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_M1 | Pre-flight cada N=10 turnos puede ser demasiado frecuente (overhead) o insuficiente (drift entre refreshes) | Tuning post-experimento T+14d con métrica latencia/drift_detected |
| L_M2 | Snapshot intra-hilo duplica estado que ya existe en repo/DB | Aceptable: redundancia es feature anti-Dory, no bug |
| L_M3 | Self-snapshot del propio agente puede tener mismo sesgo (Manus cree que aplicó 0046 cuando aplicó 0045) | Snapshot incluye query real al repo/DB, no solo modelo mental |
| L_M4 | Crash mid-snapshot deja estado parcial | Atomicidad transaccional + retry exponential backoff |
| L_M5 | Cobertura inicial limitada a Manus (E1, E2, Catastro) | Cowork ya tiene CRUZ-001 (Pieza 3) — no necesita Pieza 5 también |

## §6 NO-CRUCE reglas duras

- ❌ NO crear nuevas tablas (reusar `thread_snapshots` PIEZA 1)
- ❌ NO modificar `pre_response_hook.py` (CRUZ-001 + VERIFICADOR-001 lo tocan)
- ❌ NO bloquear hilo Manus por gate intra-hilo si latencia > 2x baseline (rollback automático)
- ✅ SÍ agregar `tools/_manus_intra_preflight.sh` (script bash invocable por hilo Manus)
- ✅ SÍ extender Manus runtime con cron snapshot intra-hilo cada 30min

## §7 Owner + cadencia

**Owner sugerido:** Manus E1 (autoría draft original previo) bajo gate post-CRUZ-001 implementation cerrada.

**Cadencia esperada:** 5-7 días implementación + 14 días experimento T+14d + canonización v1 post-experimento verde.

## §8 Convergencia 3 Sabios requerida

Spec DRAFT firmado por Cowork T2-A bajo autorización T1 "firmo 5". Para canonización vivo requiere convergencia ≥2/3 de:

- **Perplexity Sonar T2-B** — ¿literatura técnica reconoce "intra-hilo Dory" como vector separado? ¿alternativas existentes?
- **GPT-5.5 Pro Pensamiento** — adversarial: ¿es over-engineering? ¿F#15 + bleed scope son evidencia suficiente para Pieza 5 nueva o solo síntomas de Pieza 1 mal calibrada?
- **Claude Opus 4.7 Pensamiento** — metodología: ¿alt A vs B vs C? ¿latencia overhead ≤10% es tolerable? ¿limitaciones cubiertas?

---

**Status:** `🟡 DRAFT — espera convergencia 3 Sabios + firma T1`
**Cowork T2-A firma DRAFT bajo autorización T1 "firmo 5" verbatim 2026-05-18.**

**Sources:**
- F#15 evidencia: [bridge H13 §3](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_H13_VEREDICTO_2026_05_17.md)
- Bleed scope D5.2 evidencia: [bridge rebase request](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_LA_FORJA_D5_2_REBASE_REQUEST_2026_05_17.md)
- PIEZAS 1-4 (hermanos): `bridge/sprints_propuestos/sprint_CRUZ_001_DRAFT.md` + `sprint_VERIFICADOR_001_DRAFT.md`
- DSC-G-008 v3 §4 (audit + limitaciones doctrina)
