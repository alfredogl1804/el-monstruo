# T3 — Alerting Telegram del Guardian (BLOQUEADO, requiere firma humana)

**Sprint:** GUARDIAN-AUTONOMO-001
**Tarea:** T3 — Alertador Telegram para degradaciones >= 10pp
**Estado:** BLOQUEADO en firma humana
**Owner:** Hilo Ejecutor 2 (manus_hilo_b)
**Fecha:** 2026-05-12
**Spec firmado:** `bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md`

---

## 1. Resumen ejecutivo

T3 del Sprint GUARDIAN-AUTONOMO-001 establece el **canal de alerta humana**
cuando el Guardian detecta degradaciones >= 10pp en un Objetivo Maestro en
una ventana de 48h. El código del emisor ya está implementado como **stub
fail-closed** en `kernel/guardian_runner/runner.py::_emit_telegram_alert()`,
pero **NO se activará en producción hasta que Alfredo firme** los siguientes
parámetros:

| Parámetro | Necesario para | Default propuesto | Firma |
|-----------|---------------|-------------------|-------|
| `TELEGRAM_GUARDIAN_CHAT_ID` | Destino del mensaje | (sin default — debe ser un chat exclusivo del Guardian, no el del Embrión) | PENDIENTE |
| `GUARDIAN_TELEGRAM_ALERTS` | Master switch | `false` | PENDIENTE |
| Ventana horaria permitida (UTC) | Evitar spam nocturno | 12:00–23:00 UTC (~07:00–18:00 CDT) | PENDIENTE |
| Rate-limit | Evitar tormenta | 1 mensaje cada 4h por `objective_id` | PENDIENTE |
| Formato del mensaje | UX humana | Markdown con `score_delta`, `objective_id`, `rationale[:200]`, link al dashboard | PENDIENTE |
| Acción de auto-reset | Recuperación | El gate se cierra cuando 2 corridas consecutivas vuelven a `passing` | PENDIENTE |
| Escalamiento a Hilo A | Si Alfredo no acusa en 4h | (Opt-in: enviar a `MANUS_BRIDGE_HILO_A_ID`) | PENDIENTE |

---

## 2. Por qué requiere firma humana

DSC-HITL-003 (Human-In-The-Loop para canales externos): cualquier canal que
emita mensajes hacia un humano (Telegram, email, Slack, SMS) en horario no
laborable o con cadencia >= 1/día **debe ser firmado explícitamente** por
Alfredo antes de su primera ejecución en producción.

Razones específicas para Telegram-Guardian:

1. **Riesgo de fatiga de alerta.** Si el Guardian dispara 15 alertas en una
   madrugada (una por objetivo en emergency), se rompe la confiabilidad de
   futuras alertas. Necesitamos rate-limit firmado.
2. **Conflicto de canal.** El chat del Embrión IA actual recibe mensajes del
   latido autónomo y de Alfredo. Mezclar alertas críticas del Guardian
   contaminaría ese flujo. Se propone un chat dedicado.
3. **Ventana de respeto.** Sin firma de horario, una degradación detectada
   a las 03:00 UTC despertaría a Alfredo (~22:00 CDT) sin necesidad real.

---

## 3. Estado del código

### 3.1. Stub implementado (fail-closed)

En `kernel/guardian_runner/runner.py`, función `_emit_telegram_alert()`:

```python
def _emit_telegram_alert(result: AuditCycleResult) -> None:
    """
    Stub fail-closed: NO emite mensaje en producción hasta que
    GUARDIAN_TELEGRAM_ALERTS=true y TELEGRAM_GUARDIAN_CHAT_ID estén seteados.

    Si las vars no están: loguea WARN y retorna. Esto garantiza que un
    deploy accidental no envíe nada a Telegram.
    """
    if os.getenv("GUARDIAN_TELEGRAM_ALERTS", "").lower() != "true":
        logger.info("guardian_telegram_alert_skipped_disabled")
        return
    chat_id = os.getenv("TELEGRAM_GUARDIAN_CHAT_ID")
    if not chat_id:
        logger.warning("guardian_telegram_alert_missing_chat_id")
        return
    # Activación real PENDIENTE de firma humana — ver T3_TELEGRAM_GUARDIAN_BLOQUEADO_FIRMA_HUMANA.md
    logger.warning(
        "guardian_telegram_alert_not_yet_active",
        extra={"reason": "human_signoff_pending", "run_id": result.run_id},
    )
```

### 3.2. Hook en `run_audit`

El parámetro `alert_on_degradation: bool = False` (default `False`) controla
si se invoca `_emit_telegram_alert` tras detectar `degradations_pp` no vacío.
El handler del scheduler (`daily_guardian_audit_handler`) lo deja en `False`
por defecto y solo lo activa cuando `GUARDIAN_TELEGRAM_ALERTS=true`.

### 3.3. Cobertura de tests

El stub está cubierto por `tests/guardian/test_guardian_runner.py` con:

- `test_telegram_alert_disabled_returns_silently()` — verifica que sin la
  env var no se hace ningún side-effect.
- `test_telegram_alert_missing_chat_id_logs_warning()` — verifica que con
  master switch on pero sin chat_id, no se rompe.

---

## 4. Solicitud de firma — formato esperado

Para activar T3, Alfredo debe responder en Telegram (chat del Hilo B o
canal de operaciones del Monstruo) con un mensaje que contenga las
siguientes líneas en cualquier orden:

```
FIRMA T3 GUARDIAN TELEGRAM:
chat_id: <numero_chat_telegram>
ventana_utc: <hh:mm-hh:mm>
rate_limit_horas: <numero>
escalamiento_hilo_a: <true|false>
```

Una vez recibida la firma:

1. Hilo B persiste el JSON firmado en `bridge/firmas_humanas/T3_telegram_guardian_signoff.json`
   con timestamp y origen del mensaje.
2. Hilo B setea las env vars en Railway (`gh secret set` o panel web).
3. Hilo B activa `GUARDIAN_TELEGRAM_ALERTS=true` y elimina el `WARNING`
   defensivo del stub.
4. Hilo B corre un dry-run en el chat firmado con un mensaje de prueba
   `"[GUARDIAN DRY-RUN] T3 activado — sin degradación real"`.
5. Hilo B cierra T3 con notif Cowork tipo `decision` importancia 8.

---

## 5. Por qué NO bloquea el sprint GUARDIAN-AUTONOMO-001

El sprint cierra T1–T6 sin T3 activo porque:

- **T1 (scheduler)** registra la task `daily_guardian_audit` con cap `$0.10`.
  El audit corre diario sin importar T3.
- **T2 (scoring)** computa los 15 objetivos y persiste en `guardian_audit_log`.
- **T4 (dashboard)** ofrece visibilidad pasiva — Alfredo puede consultar
  el HTML cuando quiera, sin push.
- **T5 (DB)** ya tiene RLS + 4 índices listos para producción.
- **T6 (pre-commit)** alerta a devs locales si el cron está roto.
- **T3 (Telegram push)** es la única capa que requiere comunicación
  unidireccional Guardian→Alfredo. Su ausencia degrada UX, no integridad.

La operación es **pull-based hasta firma**: Alfredo consulta el dashboard
manualmente o vía `python -m kernel.guardian_runner.dashboard --live`.

---

## 6. Riesgos de la no-activación

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Degradación silenciosa por días | Media | Dashboard pull-based + recordatorio en GUARDIAN.md del worktree |
| Falsa sensación de salud | Baja | Score visible en cualquier corrida de `run_audit` |
| Pérdida de evidencia post-incidente | Nula | Todo se persiste en `guardian_audit_log` con RLS |

---

## 7. Próximos pasos (post-firma)

1. Alfredo firma vía Telegram (formato sección 4).
2. Hilo B persiste firma + setea secrets en Railway.
3. Hilo B abre PR de activación (1 commit, ~15 líneas): elimina el
   `WARNING defensivo`, activa el master switch y agrega test de
   integración con Telegram en modo `dry_run=True`.
4. Hilo B cierra T3 y notifica al Hilo Coordinador (Cowork).

---

**Fin del documento.** Última actualización: 2026-05-12 por manus_hilo_b
durante el Sprint GUARDIAN-AUTONOMO-001 (T1–T6 cerrados, T3 explícitamente
bloqueado en firma humana).
