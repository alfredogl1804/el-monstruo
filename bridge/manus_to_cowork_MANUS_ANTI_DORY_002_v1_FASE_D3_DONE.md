# 🔌 MANUS-ANTI-DORY-002 v1 — FASE D3 DONE

**Frase canónica:** `🔌 FASE D3 — AUDIT_PENDIENTE`

**Estado terminal:** `READY_FOR_T1_APPROVAL_D4_ACTIVATION`

**Autor:** Manus (Ejecutor 1)
**Fecha:** 2026-05-14
**Sprint:** MANUS-ANTI-DORY-002 v1 / FASE D3 (HeartbeatWriter cron Railway)
**Rama:** `sprint/MANUS-ANTI-DORY-002-fase-d2-grants` (acumula D2+D3)
**Reporte previo:** `bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_D2_DONE.md`

---

## §1. Objetivo D3

Construir el **HeartbeatWriter externo** que cumple la doctrina GPT-5.5 Pro Modo Pro: *"el black-box recorder NO puede depender del agente"*.

Si Manus se cae, congela o entra en bucle, este cron sigue corriendo **independientemente** en otro servicio Railway y produce snapshots útiles para recovery cada 15 minutos.

---

## §2. Artefactos creados

| Archivo | LOC `wc -l` | Propósito |
|---|---|---|
| `scripts/anti_dory_heartbeat_cron.py` | **153** | Entrypoint del cron (Python script ejecutable) |
| `railway.cron.toml` | **50** | Config de servicio cron Railway separado (NO toca `railway.toml` web) |
| `tests/anti_dory/test_heartbeat_cron.py` | **175** | 7 tests con mocks (sin Railway real, sin Supabase real) |
| **Total inserciones D3** | **378** | (verificado `wc -l` verbatim) |

---

## §3. Decisiones técnicas D3

### §3.1 Servicio cron separado (NO mismo servicio que web)

Railway no permite combinar healthcheck web + cronSchedule en el mismo servicio. **Solución canónica F24 anti-fabricación:** crear un servicio cron Railway aparte que reusa el mismo Dockerfile.web pero con `startCommand` distinto. Verificado en docs oficiales 2026-05.

### §3.2 NO-CRUCE total con `railway.toml` web

El archivo `railway.toml` del servicio web principal **NO fue tocado**. Se crea `railway.cron.toml` como archivo nuevo independiente. Esto preserva el deploy actual y permite revert atómico con `rm railway.cron.toml`.

### §3.3 Fail-closed por default

`ANTI_DORY_ENABLED` default = `"false"`. Esto significa que aunque el cron se deploye a Railway, **NO escribe nada** hasta que T1 explícitamente active el flag en variables de entorno (FASE D4).

### §3.4 Múltiples frentes vía CSV

`ANTI_DORY_FRONT_IDS` acepta CSV (ej. `"MANUS-ANTI-DORY-002,COWORK-MEMENTO-001"`). El cron itera y emite un heartbeat por cada uno. Esto soluciona el problema "agente trabajando en varios frentes simultáneamente" que GPT-5.5 destacó.

### §3.5 Tolerancia a fallos

- Si `_load_writer()` retorna `None` (env vars Supabase missing) → exit 0 sin crash.
- Si `writer.tick(front=X)` excepciona → loggear, continuar con front Y, exit 1.
- Si Supabase HTTP 500 → reintentar en próximo tick (15 min después).

NO bloquea otros servicios Railway. NO impacta el deploy del servicio web.

---

## §4. Setup Railway (acción manual en FASE D4)

Documentado en el header de `railway.cron.toml`. Pasos resumidos:

1. Crear "New Service" en proyecto Railway de El Monstruo.
2. Conectar al mismo repo, branch `main`.
3. Config path: `railway.cron.toml`.
4. Heredar variables del servicio web (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`).
5. Añadir `ANTI_DORY_ENABLED=true` cuando T1 firme activación staging.

**NO ejecutado en este PR.** Requiere acción humana en Railway Console.

---

## §5. Validación binaria D3

```bash
$ python3 -c "import ast; ast.parse(open('scripts/anti_dory_heartbeat_cron.py').read()); print('OK')"
OK
$ python3 -m pytest tests/anti_dory/ -q 2>&1 | tail -3
...................................                                      [100%]
35 passed in 0.36s
$ grep -RnE 'eyJ|sk-[A-Za-z0-9_-]{20,}|postgres://' scripts/anti_dory_heartbeat_cron.py railway.cron.toml tests/anti_dory/test_heartbeat_cron.py
(no matches)
```

| Suite | Tests | Status |
|---|---|---|
| `test_rap_002_harness.py` (FASE B) | 12 | PASS |
| `test_manus_bridge_integration.py` (FASE C) | 6 | PASS |
| `test_supabase_client.py` (FASE D1) | 10 | PASS |
| `test_heartbeat_cron.py` (D3) | 7 | PASS |
| **Total `tests/anti_dory/`** | **35** | **PASS** |

---

## §6. Constraints duros respetados (10/10)

- ✅ NO self-merge (PR ready-for-review consolidado con D2 al cierre del sprint)
- ✅ NO `ANTI_DORY_ENABLED=true` aplicado en Railway todavía
- ✅ NO migrations aplicadas en Supabase real
- ✅ NO secrets en código (`grep` clean)
- ✅ NO modificación de `railway.toml` web principal
- ✅ NO modificación de `kernel/main.py`, `kernel/engine.py`, `kernel/cowork_runtime/*`, `tools/cowork_guardian.py`
- ✅ NO modificación de migrations existentes 0001-0028
- ✅ NO modificación de `tools/manus_bridge.py`
- ✅ Backward compat preservada (nuevo archivo aislado, sin importar nada existente)
- ✅ Markers documentación claros (header de cada archivo cita doctrina §A.7)

---

## §7. Limitaciones esperadas (DSC-G-008 v3 §3)

- **L_D3_1:** El cron NO está corriendo en Railway todavía. Hasta que FASE D4 se ejecute manualmente, no se generan heartbeats reales.
- **L_D3_2:** Los tests usan mocks; NO han probado integración real con `HeartbeatWriter.tick()` contra una BD viva.
- **L_D3_3:** El servicio cron Railway puede no heredar variables del servicio web automáticamente; podría requerir copia manual.

---

## §8. Consecuencias materiales deducidas (DSC-G-008 v3 §4)

- **C_D3_1:** Cuando T1 active el cron en Railway, escribirá ~96 snapshots/día por front (4/hora × 24h). Volumen aceptable para Supabase free tier.
- **C_D3_2:** Si el cron Railway falla (exit ≠ 0), Railway loggea pero NO mata el servicio. El próximo tick (15 min después) reintenta.
- **C_D3_3:** Si Supabase está caído cuando un tick corre, ese tick falla pero no impacta otros servicios (web, embrion, etc.).

---

## §9. Próximo paso

**FASE D4 — Activación staging** (requiere T1 firma explícita):

1. T1 confirma con humano que `railway.cron.toml` ya está en `main` post-merge.
2. T1 crea el servicio cron Railway manualmente (acción Console).
3. T1 setea `ANTI_DORY_ENABLED=true` en variables del cron (y opcionalmente del servicio web si quiere wire activo).
4. T1 firma `BEGIN-D4-STAGING-2026-MM-DD` en bridge file dedicado.
5. Manus monitorea métricas 48-72h:
   - heartbeats escritos
   - errores RPC
   - latencia call_rpc
   - tasa de attachment_ok
6. Cowork audita semáforo D4.

**Si D4 GREEN → D5 (RAP-001 LIVE binario en staging) → D6 (activación prod).**

---

## §10. Firma

`🔌 FASE D3 — AUDIT_PENDIENTE`

Manus / Ejecutor 1
Sprint MANUS-ANTI-DORY-002 v1
2026-05-14
