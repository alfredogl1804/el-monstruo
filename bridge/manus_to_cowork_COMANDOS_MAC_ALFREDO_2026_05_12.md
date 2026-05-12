---
id: manus_to_cowork_COMANDOS_MAC_ALFREDO_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2-A (orquestador) + Alfredo T1 (operador)
tipo: standby_activo_TC_comandos_copy_paste
prioridad: P2
spec_origen: bridge/cowork_to_manus_HILO_EJECUTOR_1_STANDBY_ACTIVO_2026_05_12.md §2 TC
contexto_relacionado:
  - bridge/manus_to_cowork_T7_SMOKE_CHECKLIST_PR_114_2026_05_12.md (T7 detallado)
  - bridge/T3_TELEGRAM_GUARDIAN_BLOQUEADO_FIRMA_HUMANA.md (T3 spec firmable)
  - bridge/sprints_completados/PAR_BICEFALO_001_brand_engine_CIERRE.md (Brand Engine plan canary)
---

# Comandos Mac Alfredo — preparados copy-paste

> **Yo NO ejecuto ninguno de estos comandos.** Solo los preparo en formato copy-paste para que Alfredo los corra cuando decida activar cada operación.
>
> Cada bloque es **autónomo** — Alfredo puede ejecutar cualquier sección sin ejecutar las otras.

---

## §1 T7 smoke binario PR #114 (MOBILE-REALIGNMENT-001)

**Cuándo:** después de que Cowork mergee PR #114 a `main` (o ahora mismo en branch si Alfredo quiere validar antes del merge).

**Pre-requisito:** macOS con Flutter 3.41.8 stable instalado (`flutter --version` para confirmar).

**Versión completa con explicaciones:** ver `bridge/manus_to_cowork_T7_SMOKE_CHECKLIST_PR_114_2026_05_12.md`.

### §1.1 Smoke post-merge a `main` (camino feliz)

```bash
cd ~/el-monstruo
git checkout main
git pull origin main
cd apps/mobile
flutter clean && flutter pub get
flutter analyze   # esperado: 39 issues found (0 errors)
flutter build macos --debug
open build/macos/Build/Products/Debug/el_monstruo_app.app
```

### §1.2 Smoke pre-merge en branch del sprint (validación early)

```bash
cd ~/el-monstruo
git fetch origin
git checkout sprint/mobile-realignment-001-2026-05-12
git log --oneline -1   # esperado SHA: 2489bbb
cd apps/mobile
flutter clean && flutter pub get
flutter analyze   # esperado: 39 issues
flutter build macos --debug
open build/macos/Build/Products/Debug/el_monstruo_app.app
```

### §1.3 Verificación visual (8 checkpoints binarios)

Marcar mentalmente cada uno al verificarlo. Detalle exhaustivo en checklist completo:

1. App levanta sin crashes
2. BottomNav Daily renderiza 5 tabs (Home, Threads, Pendientes, Conexiones, Perfil)
3. Tab Home muestra ChatScreen
4. Tabs Threads/Pendientes/Conexiones muestran placeholder
5. Tab Perfil proxea SettingsScreen
6. Swipe-down 2 dedos toggle a Cockpit (BottomNav desaparece)
7. Cockpit Drawer accesible con 6 entradas (MOC, FinOps, Sandbox, Memory, Embrion, A2UI)
8. Long-press logo Drawer Cockpit vuelve a Daily

### §1.4 Reporte post-smoke

```bash
# Si VERDE 8/8:
gh pr comment 114 --body "T7 SMOKE BINARIO — VERDE 8/8 checkpoints. Sprint MOBILE-REALIGNMENT-001 declarado COMPLETO 7/7 verde. Mergeable."

# Si ROJO en cualquier checkpoint, crear bridge file:
cat > bridge/alfredo_to_cowork_T7_SMOKE_ROJO_PR_114_$(date +%Y_%m_%d).md <<'EOF'
# T7 SMOKE ROJO PR #114
fecha: 2026-05-12
checkpoint_fallido: <numero(s)>
sintoma: <descripcion>
log_relevante: |
  <pegar últimas 30 líneas de "log stream --process el_monstruo_app">
screenshot: <ruta o adjunto Slack>
EOF
git add bridge/alfredo_to_cowork_T7_SMOKE_ROJO_PR_114_*.md && git commit -m "smoke(rojo): T7 PR #114 fallo checkpoint X" && git push
```

---

## §2 Brand Engine canary activation (`mode=shadow`)

**Cuándo:** cuando Alfredo decida activar Brand Engine para 48-72h de observación shadow antes de promoción a `enforce`.

**Pre-requisito:** PRs PAR_BICEFALO_001 (PR-A, PR-B, PR-C) ya mergeados a `main` (los 3 deberían estar mergeados ya según `bridge/sprints_completados/PAR_BICEFALO_001_brand_engine_CIERRE.md`).

### §2.1 Activación canary (Railway CLI)

```bash
# 1. Verificar Railway CLI logueado en proyecto El Monstruo:
railway whoami
railway environment   # esperado: production

# 2. Setear las dos env vars del canary:
railway variables --set BRAND_ENGINE_ENABLED=true
railway variables --set BRAND_ENGINE_MODE=shadow

# 3. Trigger redeploy (algunos servicios requieren restart explícito):
railway up --detach   # o esperar al próximo auto-deploy si está en watch
```

### §2.2 Activación canary (alternativa via Railway Dashboard)

1. Abrir <https://railway.app/dashboard>
2. Seleccionar proyecto **El Monstruo** → servicio del kernel/embrión
3. Tab **Variables** → **+ New Variable**
4. Agregar:
   - `BRAND_ENGINE_ENABLED` = `true`
   - `BRAND_ENGINE_MODE` = `shadow`
5. Click **Deploy** (botón superior derecho) para redeploy con nuevas vars

### §2.3 Verificación canary activo (post-deploy)

```bash
# Inspeccionar logs Railway en tiempo real:
railway logs --tail 100 | grep -i "brand_engine\|shadow"

# Esperado en logs:
#   "brand_engine_initialized mode=shadow"
#   "brand_engine_validation_recorded verdict=APPROVED|REJECTED"
#   NO esperar mensajes "brand_engine_aborted_response" (eso solo sale en mode=enforce)
```

### §2.4 Inspección post-48h de embrion_validation_log

```bash
# Conectarse a Supabase y revisar tasa de rechazo:
psql "$SUPABASE_DB_URL" -c "
  SELECT 
    DATE(created_at) as dia,
    COUNT(*) as total,
    SUM(CASE WHEN verdict = 'REJECTED' THEN 1 ELSE 0 END) as rechazadas,
    ROUND(100.0 * SUM(CASE WHEN verdict = 'REJECTED' THEN 1 ELSE 0 END) / COUNT(*), 2) as rechazo_pct
  FROM embrion_validation_log
  WHERE created_at >= now() - interval '72 hours'
  GROUP BY DATE(created_at)
  ORDER BY dia DESC;
"

# Criterios de promoción shadow → enforce (per PAR_BICEFALO_001 cierre):
#   - rechazo_pct ≤ 15% sobre 200+ respuestas reales conversacionales
#   - costo_diario_observado ≤ $2.00
#   - latencia p95 ≤ 8 segundos
```

### §2.5 Promoción a `enforce` (si criterios verde)

```bash
railway variables --set BRAND_ENGINE_MODE=enforce
railway up --detach
# Monitorear logs primeras 2h post-promoción:
railway logs --tail 200 | grep -i "brand_engine_aborted_response\|brand_veto"
```

### §2.6 Rollback de emergencia (kill-switch)

```bash
# Desactivación INSTANTÁNEA si Brand Engine bloquea respuestas legítimas en producción:
railway variables --set BRAND_ENGINE_ENABLED=false
railway up --detach
# Sistema vuelve al comportamiento sin Brand Engine inmediatamente (feature flag).
```

---

## §3 Telegram T3 Guardian config (firma humana + activación)

**Cuándo:** cuando Alfredo decida firmar la activación del canal de alertas Guardian → Alfredo (BLOQUEADO desde 2026-05-12 por DSC-HITL-003).

**Spec firmable completo:** `bridge/T3_TELEGRAM_GUARDIAN_BLOQUEADO_FIRMA_HUMANA.md`.

### §3.1 Pre-requisito: crear chat dedicado Guardian (si no existe)

> **Razón:** mezclar alertas Guardian con el chat normal del Embrión rompe el patrón de DSC-HITL-003. Necesita chat exclusivo del Guardian.

1. Telegram → menú → **New Group** → nombre: "Monstruo Guardian Alerts"
2. Agregar el bot del Monstruo al grupo (mismo bot, distinto chat).
3. Obtener el `chat_id` del nuevo grupo:
   ```bash
   # Mandar cualquier mensaje al grupo desde Alfredo, luego:
   curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates" \
     | python3 -c "import json,sys; updates=json.load(sys.stdin)['result']; \
       [print(u['message']['chat']['id'], u['message']['chat'].get('title','-')) \
       for u in updates if 'message' in u]"
   ```
4. Guardar el `chat_id` (suele ser negativo para grupos, ej: `-1002345678901`).

### §3.2 Firma humana via Telegram (formato canónico)

Alfredo envía mensaje al chat del Hilo B (no al chat Guardian) con este formato exacto:

```
FIRMA T3 GUARDIAN TELEGRAM:
chat_id: -1002345678901
ventana_utc: 12:00-23:00
rate_limit_horas: 4
escalamiento_hilo_a: false
```

### §3.3 Setear env vars en Railway (post-firma)

```bash
# 3 env vars del Telegram T3 Guardian:
railway variables --set TELEGRAM_GUARDIAN_CHAT_ID="-1002345678901"
railway variables --set GUARDIAN_TELEGRAM_ALERTS=true
# Variables auxiliares (defaults razonables si no se setean):
railway variables --set GUARDIAN_TELEGRAM_WINDOW_UTC="12:00-23:00"
railway variables --set GUARDIAN_TELEGRAM_RATE_LIMIT_HOURS=4

# Trigger redeploy:
railway up --detach
```

### §3.4 Dry-run de prueba (verificación)

Después del deploy, el Hilo Ejecutor 2 (manus_hilo_b) debe correr:

```bash
# (Esto lo corre Hilo Ejecutor 2, NO Alfredo. Solo lo documento aquí para visibilidad.)
python3 -c "
from kernel.runner.telegram_notifier import TelegramNotifier
import os
n = TelegramNotifier()
chat_id = os.environ['TELEGRAM_GUARDIAN_CHAT_ID']
n.send_message(
    text='[GUARDIAN DRY-RUN] T3 activado — sin degradación real. Confirmá recepción.',
    chat_id=chat_id,
)
"
```

Alfredo confirma recepción del mensaje en el chat Guardian → Hilo Ejecutor 2 cierra T3 con notif Cowork.

### §3.5 Rollback (desactivación)

```bash
# Desactivación INSTANTÁNEA del canal de alertas Guardian:
railway variables --set GUARDIAN_TELEGRAM_ALERTS=false
railway up --detach
# El stub fail-closed vuelve a logear silently sin enviar nada.
```

---

## §4 Notas operativas finales

1. **Yo NO ejecuto ninguno de estos comandos.** Cada uno requiere decisión humana de Alfredo (sign-off T7 smoke, activación canary Brand Engine, firma humana T3 Telegram).

2. **Variables de entorno y secrets:**
   - `$SUPABASE_DB_URL` debe estar seteada en el Mac de Alfredo para los queries §2.4 y §3.
   - Railway CLI requiere `railway login` previo (one-time).
   - Si alguno de los comandos falla por env var no seteada, el comando lo reporta claramente.

3. **Idempotencia:**
   - Setear `railway variables --set X=Y` 2 veces NO rompe nada (idempotente).
   - `flutter clean && flutter pub get` siempre seguros de re-ejecutar.
   - El dry-run del Telegram §3.4 manda 1 mensaje cada vez que se ejecuta — NO ejecutar en loop.

4. **Riesgo de cohabitación cross-hilo:**
   - Si durante T7 smoke Alfredo ve archivos extraños en `git status`, son colisión cross-hilo (Catastro o Ejecutor 2 trabajando en paralelo en el mismo Mac). NO afecta el smoke en sí, pero conviene `git stash` antes de empezar para tener working tree limpio.
   - Recomendación canónica (ya documentada): usar `git worktree` separados por hilo para evitar esto en futuros sprints concurrentes.

5. **Logs y debug:**
   - Logs Flutter macOS app: `log stream --process el_monstruo_app --info --debug`
   - Logs Railway: `railway logs --tail N`
   - Logs Supabase: dashboard web `https://supabase.com/dashboard/project/<id>/logs`

---

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12 — STANDBY ACTIVO TC producido (cero comandos ejecutados, todo preparado copy-paste).
