---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D6 Railway flag permanente
autor: Cowork T2-A
fecha: 2026-05-14
autoridad: T1 Alfredo Góngora "procede" verbatim 2026-05-14 post-D5 GREEN
destinatario: Manus Hilo Ejecutor 1 (manus_hilo_a)
gate_cumplido: 🏛️ D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO
---

# 🚦 D6 — Railway flag `ANTI_DORY_ENABLED=true` permanente

## §1 Estado verificado binariamente

- ✅ **D5 GREEN binariamente validado** (6/6 acceptance criteria — bridge `cowork_D5_GREEN_DECLARADO_2026_05_14.md`)
- ✅ PR #132 mergeado commit `5550ba26` — F-pattern #11 fixed (regex UUID Manus)
- ✅ Manus T+1 absorbió contexto canónico sin reexplicación (verificación visual T1)
- ✅ Anti-Dory broker funciona end-to-end con `attach_context=True` real prod

## §2 Tu alcance binario (E1 only)

**Acción única:** Set Railway env var `ANTI_DORY_ENABLED=true` en el web service prod (donde corre el kernel/orquestador del Monstruo).

```bash
# Comando exacto (Manus E1 ejecuta en su Mac con Railway CLI auth):
railway login                                   # si no estás logged
railway link <project-id-monstruo>              # si no está linked
railway service                                 # confirmar service correcto (web prod, NO cron)
railway variables set ANTI_DORY_ENABLED=true    # set permanente
railway redeploy                                # trigger deploy con nueva env var
```

**NO toques:**
- `ANTI_DORY_CRON_ENABLED` (cron service separado — sigue OFF si está OFF)
- Otras env vars (Supabase, etc.)
- `kernel/anti_dory/` código
- Cualquier migration

## §3 Acceptance criteria binarios (Cowork verificará post-DONE)

| # | Check | Comando | Esperado |
|---|---|---|---|
| 1 | env var set en service correcto | `railway variables get ANTI_DORY_ENABLED` | `true` |
| 2 | Service deployed con env var | Railway dashboard: latest deploy ID + timestamp > ahora | match |
| 3 | Kernel runtime confirma flag ON | logs Railway: buscar `kernel.anti_dory.ANTI_DORY_ENABLED = True` | hit |
| 4 | No regresión otros services | `railway services list` | mismos services pre-D6 |

## §4 Bridge file DONE template

`bridge/manus_to_cowork_D6_RAILWAY_FLAG_DONE_2026_05_14.md`

Frontmatter:
```yaml
---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D6 Railway flag permanente
fecha_done: 2026-05-14T<HH:MM>Z
ejecutor: manus_hilo_a
service_modificado: <nombre del web service>
deploy_id: <Railway deploy id>
env_var_set: ANTI_DORY_ENABLED=true
acceptance_count: 4/4
veredicto: GREEN | RED
---
```

Cuerpo: 4 ACs §3 con evidencia verbatim (CLI output + Railway dashboard screenshots o equivalente).

## §5 Reglas duras NO-CRUCE

- ❌ NO modificar código
- ❌ NO modificar migrations
- ❌ NO tocar otros services o env vars
- ❌ NO emitir frase canónica nueva (D6 cierra activación, no nuevo hito)
- ✅ SÍ logs verification post-deploy
- ✅ SÍ bridge file con evidencia binaria

## §6 Cadencia + secuencia post-D6

**Tiempo estimado:** 5-15 min (config + deploy + verify).

**Post-D6 verde:** Cowork emite kickoff CRUZ-001 a vos inmediato — gate de arranque cumplido (D5-RETEST 6/6 verde ✅ + D6 Railway flag set ✅).

Bridge spec CRUZ-001 FIRMED commit `7ad21713`:
`bridge/sprints_propuestos/sprint_CRUZ_001_DRAFT.md`

## §7 Confirmación protocolo

Responde con:

```
[E1 D6 PRE-FLIGHT]
Confirmo:
- Acción única: railway variables set ANTI_DORY_ENABLED=true en service web prod
- NO tocar ANTI_DORY_CRON_ENABLED ni otras vars
- 4 ACs §3 entendidos
- Bridge DONE con evidencia verbatim

Iniciando. Reporto en ~10-15 min.
```

Iniciá inmediato. Reporto cuando tu bridge DONE llegue.

— Cowork T2-A | autoridad delegada T1 "procede" verbatim 2026-05-14 post-D5 GREEN
