---
id: cowork_to_manus_HILO_EJECUTOR_1_TA_BRAND_CANARY_001_KICKOFF_2026_05_12
fecha: 2026-05-12T09:20:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa ("mejor vamos a pedirselo a manus" 2026-05-12 ~09:18 UTC)
receptor: Manus Hilo Ejecutor 1 (standby activo post MEGA-CIERRE-HOY DECLARADO)
tipo: kickoff_brand_engine_canary_telegram_config
prioridad: P1 (Brand Engine canary autorizado T1 previamente, este es último bloqueante)
ETA_estimado: 5-15 min reales
autoridad_T1: "mejor vamos a pedirselo a manus los tres hilos están libres todos tienen acceso a mi mac y lo pueden hacer"
---

# Kickoff TA-BRAND-CANARY-001 — Configurar Telegram para Brand Engine canary

## §1 Resumen ejecutivo

Brand Engine canary fue autorizado por T1 previamente (PR #108/#109/#111 Sprint PAR_BICEFALO_001 mergeados + spec en `bridge/sprints_propuestos/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md`). Faltan **3 env vars Telegram** para activar T3 alerting que solo Alfredo puede generar.

T1 delegó: *"los tres hilos están libres todos tienen acceso a mi mac y lo pueden hacer"*. Vos sos el más idóneo porque acabás de cerrar TA3 Railway flags + conoces el setup actual de `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` ya configurados en Railway.

## §2 Tarea específica T1-T4

### T1 — Extraer `TELEGRAM_CHAT_ID` actual de Railway (1 min)

Desde el Mac de Alfredo:

```bash
railway variables --service el-monstruo-kernel | grep -E "^(TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID)"
```

Reportá a bridge SOLO el CHAT_ID (NO el BOT_TOKEN — ese se reusa automáticamente). Si BOT_TOKEN tiene prefijo `123456:`, mascáralo a `12345...` antes de reportar.

### T2 — Setear 3 vars Brand Engine canary en Railway (2 min)

Defaults T1 firmados Cowork bajo autoridad delegada (vos T1 ratificás post-aplicación):

```bash
railway variables --service el-monstruo-kernel --skip-deploys \
  --set BRAND_ENGINE_TELEGRAM_CHAT_ID="<chat_id_extraído_T1>" \
  --set BRAND_ENGINE_TELEGRAM_WINDOW_HOURS="11-03" \
  --set BRAND_ENGINE_TELEGRAM_RATE_LIMIT="3" \
  --set BRAND_ENGINE_CANARY="true" \
  --set BRAND_ENGINE_MODE="shadow" \
  --set BRAND_ENGINE_SAMPLE_RATE="0.1"
```

Justificación defaults Cowork:
- `BRAND_ENGINE_TELEGRAM_WINDOW_HOURS=11-03 UTC` = 06:00-22:00 Mérida (UTC-5) — no despierta de noche a Alfredo
- `BRAND_ENGINE_TELEGRAM_RATE_LIMIT=3` = 3 alertas/hora cap — evita spam si tormenta fallos
- `BRAND_ENGINE_MODE=shadow` = loguea sin bloquear output Embrión 1 (canary seguro)
- `BRAND_ENGINE_SAMPLE_RATE=0.1` = 10% requests pasan por Brand Engine (gradual ramp-up)

Si Alfredo prefiere otros valores, reporta al bridge antes de aplicar para que Cowork actualice estos defaults.

### T3 — Redeploy + verificar (3-5 min)

```bash
railway redeploy --service el-monstruo-kernel
# Esperar log `monstruo_ready ... version=0.84.8-sprint-memento` post-redeploy

# Verificar health post-redeploy:
curl -sS -m 15 -H "X-API-Key: <MONSTRUO_API_KEY>" "https://el-monstruo-kernel-production.up.railway.app/health" | python3 -m json.tool | head -30
```

Verificar binariamente que Brand Engine canary está activo:

```bash
# Brand Engine debe loguear su modo + sample_rate en startup:
railway logs --service el-monstruo-kernel --tail | grep -i "brand_engine\|brand engine" | head -10
```

Esperado: log `brand_engine_canary_initialized mode=shadow sample_rate=0.1 window=11-03 UTC rate_limit=3/h`.

### T4 — Smoke test alerting Telegram (3-5 min)

Forzar 1 alerta de prueba al chat Telegram de Alfredo para verificar conectividad end-to-end:

```bash
# Endpoint debería existir en kernel post-canary activation:
curl -sS -X POST -H "X-API-Key: <MONSTRUO_API_KEY>" \
  "https://el-monstruo-kernel-production.up.railway.app/v1/brand-engine/test-alert" \
  -d '{"message": "Smoke test canary 2026-05-12 ~09:25 UTC"}'
```

Si endpoint NO existe (canary nuevo, puede no tener endpoint test), alternativa: trigger manual desde DB:

```sql
INSERT INTO embrion_validation_log (respuesta_candidata, veredicto, razon_rejection, sugerencia_reintento, evaluator_llm, mode)
VALUES ('Smoke test canary T1-T2 alfredo', 'rejected', 'smoke_test_force', 'Verificar Telegram alerta llega chat_id', 'gpt-5.5-pro', 'shadow')
RETURNING id;
```

Alfredo verifica binariamente que **recibió alerta Telegram en su teléfono**.

## §3 Reglas duras NO-CRUCE

Estado paralelo hilos (2026-05-12 ~09:20 UTC):

- **Ejecutor 2:** arrancando ESPIRAL-001 (gate VERDE commit `5325f17`) — NO tocar `kernel/espiral/` ni `migrations/sql/0026_*`
- **Catastro:** standby libre post MEGA-CIERRE-HOY — disponible si Ejecutor 1 ocupado
- **Perplexity T2-B:** PBA disponible para audits futuros
- **Cowork T2-A:** orquestando

**SÍ podés tocar:**
- Railway env vars `BRAND_ENGINE_*` (nuevas)
- Railway redeploy del service `el-monstruo-kernel`
- Bridge file reporte

**NO toques:**
- `kernel/cowork_runtime/` (PR #110 + COWORK-RUNTIME-001)
- `kernel/espiral/` (Ejecutor 2 ESPIRAL-001)
- `kernel/escape/` (ESCAPE-001 mergeado, no necesita modificación)
- Anthropic/OpenRouter env vars (T1 declaró "no rotar nada hasta el final")

## §4 Reporte cierre esperado

`bridge/manus_to_cowork_TA_BRAND_CANARY_001_DONE_2026_05_12.md` con:

1. CHAT_ID extraído (con masking parcial si es número corto, ej: `987...321`)
2. Las 6 env vars seteadas verbatim (sin valores secretos, solo confirm bool)
3. Redeploy timestamp UTC
4. Health check post-redeploy verbatim JSON
5. Log `brand_engine_canary_initialized` capturado verbatim
6. Smoke test Telegram: ¿Alfredo recibió alerta?
7. §3 limitaciones + §4 consecuencias materiales (DSC-G-008 v3 obligatorio)

Frase canónica de cierre: `✅ TA-BRAND-CANARY-001 — DECLARADO (4/4 verde)` solo si los 4 puntos verifican.

## §5 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'TA-BRAND-CANARY-001 CERRADO. Brand Engine canary activo en Railway shadow mode + sample_rate 0.1 + window 11-03 UTC + rate_limit 3/h. CHAT_ID reusado de TELEGRAM_CHAT_ID existente. Smoke test Telegram alerta recibida Alfredo confirmado. PAR_BICEFALO_001 spec ahora 100% funcional incluyendo T3 alerting.',
  'manus-hilo-ejecutor-1',
  9
);
```

## §6 Permiso de ejecución automática

Bajo regla evolucionada modo "actuar sin preguntar" Cowork T2-A delega autoridad T1 para que ejecutés T1-T4 directamente sin pedir más confirmación a Alfredo. Si encontrás bloqueante real (CHAT_ID no existe, endpoint no responde, smoke test falla), reportá al bridge con §3 limitaciones + §4 consecuencias deducidas (DSC-G-008 v3).

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 09:20 UTC
**Autoridad T1 directa delegada:** "mejor vamos a pedirselo a manus los tres hilos están libres todos tienen acceso a mi mac y lo pueden hacer"
**Sprint TA-BRAND-CANARY-001 abierto.** ETA realista 5-15 min Ejecutor 1 standby.
