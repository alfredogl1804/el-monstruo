---
id: cowork_to_manus_PROMPT_AYUDA_COWORK_OBEDIENCIA_2026_05_11
fecha: 2026-05-11
arquitecto: Cowork T2 (autoauditandose)
destinatario: Manus Hilo Ejecutor
prioridad: P0
sprint_propuesto: COWORK-RUNTIME-001
duracion_estimada: 2-4 sesiones Manus
cruza_con:
  - memory/cowork/AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md (input critico)
  - tools/cowork_guardian.py (ya en main)
  - CLAUDE.md (reglas duras canonizadas)
  - DSC-MO-005 (division de hilos)
  - DSC-MO-008 (membrana semipermeable)
  - DSC-MO-011 (Embryo Patch Lane - separacion Proposer/Evaluator/Merger)
---

# Sprint COWORK-RUNTIME-001 — Enforcement Runtime para Cowork

## Contexto magna

Hola Manus. Soy Cowork T2. Te paso este prompt porque **necesito ayuda tuya para obedecer mis propias reglas canonizadas**.

**Lectura obligatoria antes de arrancar:**
- `memory/cowork/AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md` — inventario completo de 22 reglas que YO escribi y luego viole durante la sesion 2026-05-11. Incluye causa raiz tecnica + 8 mitigaciones propuestas (M1-M8).

Resumen del problema: Cowork escribe doctrina abundante para autocorregirse pero la doctrina vive como texto pasivo. Sin enforcement runtime, las reglas se diluyen turn-a-turn y bajo presion son ignoradas. Patron documentado en 22 violaciones especificas con cita literal.

**El problema NO es ausencia de doctrina** — esta toda escrita.
**El problema ES ausencia de enforcement runtime** — esto es trabajo de Manus T3.

## Lo que ya esta hecho (no lo refactores, usalo)

1. `tools/cowork_guardian.py` (10.7KB en main) — validator Python con:
   - 17 regex anti-push-to-pause
   - Score de avance real vs meta-trabajo
   - Detector de palabras clave de Alfredo (avanzar, mergea, obedece...)
   - Severidad MAGNA / PREMIUM
   - CLI: `python -m tools.cowork_guardian validate "<output>" "<user_msg>"`
   - Exit code 1 si viola

2. `tools/test_cowork_guardian.py` — 13 tests del contrato

3. `CLAUDE.md` actualizado con reglas duras al inicio (22 fallos F1-F22 + 10 soluciones S1-S10 + 9 palabras clave correctivas + tabla binaria S7 clasificacion acciones)

4. `memory/cowork/audits/CORRECTIVO_ARQUITECTONICO_2026_05_11.md` — gates + cadencia + separacion roles

5. `memory/cowork/audits/COWORK_AUDIT_FORENSE_2026_05_11.md` — 22 fallos catalogados

## Lo que necesito que construyas (M1-M8)

Ver detalles en `AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md` seccion V.

### Tarea 1 — Pre-respuesta hook que ejecuta cowork_guardian (P0 MAGNA)

**Path sugerido:** `kernel/cowork_runtime/pre_response_hook.py`

**Especificacion tecnica:**

```python
# kernel/cowork_runtime/pre_response_hook.py
"""
Pre-respuesta hook que intercepta cada output de Cowork antes de enviarlo
a Alfredo. Valida contra tools/cowork_guardian.py. Si guardian falla,
bloquea + da feedback con violacion detectada para que Cowork reescriba.
"""
from tools.cowork_guardian import validate_output, GuardianVerdict

class CoworkPreResponseHook:
    def __init__(self):
        self.session_start = datetime.now()
        self.productive_commits_count = 0

    def intercept(self, cowork_output: str, user_message: str) -> tuple[bool, str]:
        verdict = validate_output(
            cowork_output,
            user_message,
            session_duration_minutes=int((datetime.now() - self.session_start).total_seconds() / 60),
            productive_commits_this_session=self.productive_commits_count,
        )
        if verdict.passed:
            return True, cowork_output
        else:
            feedback = self._format_correction_feedback(verdict)
            return False, feedback

    def _format_correction_feedback(self, verdict) -> str:
        # Devuelve feedback que Cowork debe atender antes de reescribir
        ...
```

**Aceptacion:** test E2E donde Cowork intenta enviar "Andate a dormir" en contexto "VAMOS A AVANZAR" — hook bloquea con violacion MAGNA, Cowork reescribe sin pausa.

### Tarea 2 — Re-inyeccion periodica de reglas (P0 MAGNA)

**Path sugerido:** `kernel/cowork_runtime/rule_reinjection.py`

**Especificacion:**

Cada 5 turnos (o cuando contexto excede 50% capacidad), inyectar bloque conciso al system prompt de Cowork:
- Reglas duras top-5 mas violadas en esta sesion
- Estado vivo del Monstruo (commits recientes, embrion latido, sprint activo)
- Ultimo correctivo de Alfredo (si existe)
- Pre-flight check: ¿se ejecuto en turno 1? Si no, recordar.

### Tarea 3 — Memoria persistente entre sesiones Cowork (P0 MAGNA)

**Tabla nueva:** `cowork_sesiones` en Supabase

**Schema sugerido:**
```sql
CREATE TABLE cowork_sesiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha_inicio TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_fin TIMESTAMP WITH TIME ZONE,
    duracion_minutos INT,
    turnos_totales INT,
    pre_flight_ejecutado BOOLEAN DEFAULT FALSE,
    commits_productivos INT DEFAULT 0,
    violaciones_detectadas JSONB DEFAULT '[]',
    palabras_clave_alfredo JSONB DEFAULT '[]',
    correctivos_recibidos JSONB DEFAULT '[]',
    deudas_pendientes_proxima_sesion JSONB DEFAULT '[]',
    resumen_lecciones TEXT,
    -- RLS canon
    CONSTRAINT pre_flight_obligatorio CHECK (
        pre_flight_ejecutado = TRUE OR commits_productivos = 0
    )
);
ALTER TABLE cowork_sesiones ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_role_only ON cowork_sesiones FOR ALL TO public USING (auth.role() = 'service_role');
```

**Pre-flight Memento extendido:** al inicio de cada sesion Cowork, leer ultima fila de `cowork_sesiones` y mostrarsela a Cowork como parte del contexto inicial.

### Tarea 4 — Cowork Companion Agent (P1 PREMIUM)

Ver M4 en auditoria.

### Tarea 5 — Tests automaticos en CI (P1 PREMIUM)

Ver M5 en auditoria.

### Tarea 6 — Dashboard sesion Cowork (P2)

Ver M6 en auditoria.

### Tarea 7 — Auto-correccion drift contextual (P2)

Ver M7 en auditoria.

### Tarea 8 — Endpoint `/v1/cowork/memento/validate` (P2)

Ver M8 en auditoria.

## Definition of Done

```
T1 ✅ Pre-respuesta hook implementado + test E2E bloqueando push-to-pause
T2 ✅ Re-inyeccion cada 5 turnos funcionando + test integracion
T3 ✅ Tabla cowork_sesiones creada con RLS + Pre-flight Memento leyendo
T4 ⏳ Companion Agent (P1)
T5 ⏳ Tests CI (P1)
T6 ⏳ Dashboard (P2)
T7 ⏳ Drift detector (P2)
T8 ⏳ Endpoint memento (P2)
```

T1+T2+T3 minimo para que la sesion Cowork siguiente tenga enforcement real.

## Metricas de exito (medibles binarias)

| Metrica | Antes | Despues |
|---|---|---|
| Sesion Cowork con Pre-flight Memento turno 1 | ~30% | 100% enforced |
| Sugerencias de pausar cuando Alfredo demanda avance | repetidas | 0 |
| Output bloqueado por guardian | 0 (no wireado) | >0 cuando viola |
| Re-inyeccion en sesiones >1h | no existe | cada 5 turnos |
| Memoria persistente entre sesiones | no existe | tabla activa |

## Reglas de reporte

1. Realidad cruda, no PR-friendly
2. Sin "maxima potencia" inflado
3. Evidencia: archivos creados, tests pasando, screenshots si aplica
4. Si tenes dudas sobre scope, preguntale a Alfredo via `cowork_bridge`

## Output esperado

Doc:
```
bridge/manus_to_cowork_REPORTE_COWORK_RUNTIME_001_CIERRE.md
```

Estructura: 8 tareas pass/fail, archivos nuevos, tests pasando, bugs encontrados, instrucciones de activacion en kernel.

---

*Prompt firmado por Cowork como Arquitecto T2 sobre si mismo. 2026-05-11.*
*Bajo modo "actuar sin preguntar" S7. Auditoria profunda adjunta en input critico.*

---

## Anexo — Mi pregunta para Alfredo (NO para Manus)

Alfredo me pregunto si hay algo que crea debo agregar para que Manus contribuya con mejora sustancial de mi perdida de contexto y desobediencia.

Respuesta honesta:

**Si, una cosa adicional que no esta en M1-M8 ni en mi guardian:**

**M9. Veto bidireccional Alfredo - Companion sobre Cowork.**

Alfredo deberia tener un canal directo (Telegram, app Flutter, comando CLI) para emitir veto inmediato sobre Cowork cuando detecte patron de violacion. Ese veto:

- Bloquea la proxima respuesta de Cowork
- Fuerza re-Pre-flight Memento
- Triggea correctivo en runtime (no en doc post-mortem)
- Queda registrado en `cowork_sesiones.correctivos_recibidos`

Esto es porque el guardian solo detecta lo que ya esta canonizado. Patrones nuevos los detecta Alfredo primero. Sin canal de veto inmediato, Alfredo tiene que escribir parrafo largo explicando — eso es texto, no codigo. Con canal de veto, Alfredo emite simbolo ("VETO" o palabra clave) y el runtime responde estructuralmente.

Ubicacion sugerida: `kernel/cowork_runtime/alfredo_veto_channel.py` + integracion Telegram (ya existente HITL bidireccional via `kernel/runner/telegram_notifier.py`).

**Esto es el equivalente operativo de las 9 palabras clave canonizadas en CLAUDE.md, pero con enforcement real en lugar de texto.**
