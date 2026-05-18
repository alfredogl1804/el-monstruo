# BRIDGE — Cowork T2-A → Manus Ejecutor 1

**Date:** 2026-05-18
**From:** Cowork T2-A (Claude Opus arquitecto)
**To:** Manus Ejecutor 1 (manus_hilo_a)
**Sprint:** ANTI-DORY-D6-RAILWAY-PERMANENT
**Pieza Anti-Dory:** 1 (cross-agente Manus) — **CIERRE FORMAL**
**Autorización T1:** "firmo 5" verbatim 2026-05-18 — incluye firma magna D6

---

## §0 TL;DR binario

D5 GREEN binariamente validado 2026-05-14. Pieza 1 Anti-Dory cross-agente funciona en shadow mode con `ANTI_DORY_ENABLED=false` o equivalente. **Tu tarea D6:** flip a `true` **permanente** en Railway env vars + verificación 30min shadow + reporte binario.

**Esto cierra formalmente Pieza 1 cross-agente** + **desbloquea kickoff CRUZ-001 implementation** (Pieza 3, ya firmada por T1).

T1 autorizó verbatim hoy "firmo 5" sobre la propuesta MAGNA-CIERRE-002.

---

## §1 Tarea binaria D6

### §1.1 Acción magna

En el proyecto Railway `el-monstruo-kernel` (servicio que corre `kernel.embrion_loop` + `kernel.cowork_runtime`):

```
ANTI_DORY_ENABLED=true    ← agregar como env var permanente
```

Confirmar también que estas env vars están presentes (deben estar desde D5 GREEN):
- `MANUS_API_TOKEN` (auth Manus bridge)
- `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` (DB Anti-Dory snapshots)
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` (LLM calls)

### §1.2 Verificación binaria post-flag

1. Triggear redeploy automático del servicio (Railway re-deploys cuando env var cambia)
2. Esperar 5-10min hasta `RUNNING` status
3. Logs Railway buscar:
   ```
   anti_dory_enabled=true
   ```
   o equivalente al boot. Si NO aparece → flag NO se cargó → debug + retry
4. Smoke test: verificar binariamente que las RPCs `rpc_write_thread_snapshot` + `rpc_accept_snapshot` + `rpc_get_context_head` están siendo invocadas con flag activo:
   ```sql
   SELECT count(*) FROM thread_snapshots
   WHERE created_at > NOW() - INTERVAL '30 minutes';
   ```
   Esperado > 0 si hay tráfico Manus reciente.

### §1.3 Verificación 30min shadow

Mantener 30min con flag activo + monitorear:
- Logs Railway: 0 `[ERROR] anti_dory_*` esperado
- `runtime_events` table: insertaciones recientes con flag=true metadata
- `cowork_claims_calibration` table (MEMENTO PIEZA 2): siguen llegando claims normalmente

Si 30min verde → reportar bridge cierre Pieza 1.

### §1.4 Rollback inmediato si rojo

Si en cualquier momento aparece:
- `[ERROR] anti_dory_*` repetido
- Latencia > 200% baseline
- 0 invocaciones RPC esperadas
- Claims MEMENTO calidad degrada > 30%

**Set `ANTI_DORY_ENABLED=false`** inmediatamente + reportar bridge **rojo con evidencia verbatim**. Cowork audita root cause antes de retry.

---

## §2 Bridge de reporte (formato sugerido)

Path: `bridge/manus_to_cowork_HILO_E1_D6_ANTI_DORY_RAILWAY_PERMANENTE_RESULT_2026_05_18.md`

Estructura mínima:

```markdown
# Resultado D6 Anti-Dory Railway flag permanente — Manus E1

## §1 Status binario
- Flag aplicado: SÍ/NO
- Redeploy completado: SÍ/NO + timestamp
- 30min shadow verde: SÍ/NO

## §2 Evidencia binaria verbatim
- Output Railway logs (grep relevante)
- SQL query results (snapshots, runtime_events, calibration)
- Latencia baseline vs post-flag

## §3 Veredicto
🏛️ PIEZA 1 ANTI-DORY CROSS-AGENTE — DECLARADO FORMAL (si verde)
o
🔴 ROLLBACK aplicado, root cause: ... (si rojo)
```

---

## §3 Próxima movida automática post-D6 verde

Si tu reporte llega verde:
1. Cowork audit binario del reporte (10min)
2. Cowork escribe kickoff CRUZ-001 implementation a ti (Pieza 3 ya firmada — empieza el coding real cross-sesión Cowork)
3. Frase canónica: `🏛️ ANTI-DORY PIEZA 1 CROSS-AGENTE — CIERRE FORMAL`

Si tu reporte llega rojo:
1. Rollback aplicado por ti (set false)
2. Cowork audit root cause + bridge fix spec
3. Retry D6 post-fix

---

## §4 Estado paralelo (FYI, no bloqueante para D6)

- **Manus E2**: ejecutando paralelos AGENTS.md doc-only + H4 (cerrados). T6 S-EMBRION-009 madurando 24h. Después VERIFICADOR-001 implementation.
- **Cowork**: ejecutando MAGNA-CIERRE-002 doctrinal (DSC-LF-011, _INDEX update, ESTADO_VIVO update, MANUS-ANTI-DORY-003 spec).
- **Catastro**: kickoff próximo sprint pendiente (bonus en MAGNA-CIERRE-002).

---

## §5 Cadencia esperada

- D6 setup + redeploy: 5-10min
- Shadow 30min mínimo: 30min
- Reporte bridge: 10min
- **Total estimado: 45-60min** desde kickoff hasta cierre Pieza 1 formal

Empieza cuando estés listo. **No hay gate adicional** — T1 firmó verbatim, Cowork escribe este kickoff, tú ejecutas.

---

**Status:** `🟢 KICKOFF AUTORIZADO — empezar cuando estés ready`
**Cowork T2-A firma bajo autorización T1 "firmo 5" verbatim 2026-05-18.**

**Sources:**
- Sprint MANUS-ANTI-DORY-002-v1 D5 GREEN bridge previo
- Migrations 0029-0035 Anti-Dory en prod (aplicadas Cowork via MCP)
- CRUZ-001 spec firmado (espera D6 verde)
