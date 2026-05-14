# AGENTS.md — apps/la-forja/

**Heredado de**: `el-monstruo/AGENTS.md` (Reglas Duras 1-8). Esta versión extiende sin contradecir.

## Antes de tocar este directorio

```bash
python3 ~/.monstruo/guardian.py
```

Si no se ejecuta exitosamente, NO hacer nada. Aplican las mismas precondiciones del repo raíz.

## Reglas específicas de La Forja (extensión)

### LF-1: Soberanía sobre infraestructura del Monstruo

La Forja **DEBE** usar la infraestructura del Monstruo y nunca crear stacks paralelos. Esto significa:

- DB: Supabase del Monstruo (no Supabase nuevo)
- Auth: Supabase Auth + Google OAuth (Manus OAuth NO permitido)
- Storage: S3 ya configurado en Railway del Monstruo
- Observabilidad: Langfuse del Monstruo
- Secretos: Railway env vars del kernel del Monstruo
- Cron: Railway Schedules del proyecto el-monstruo-kernel

Cualquier excepción requiere DSC firmado en mismo PR.

### LF-2: Modelos IA validados magna obligatorio

Cualquier referencia a modelos IA, SDKs, frameworks o versiones requiere validación magna en tiempo real (Manus directo + Perplexity Sonar) antes de ser commiteada. Esto es complemento de Regla Dura del repo raíz sobre validación tiempo real, pero La Forja lo eleva a obligatoriedad por código.

### LF-3: Cinco puertas binarias, nunca más

La Forja tiene exactamente 5 puertas: `manus_apple`, `manus_google`, `cowork_local`, `kernel_monstruo`, `simulador`. Agregar una sexta puerta requiere SPEC nuevo + audit Cowork + firma T1.

### LF-4: Capa transversal única de validación tiempo real

Perplexity Sonar Reasoning Pro es la ÚNICA capa de validación externa permitida. Consejo de 6 Sabios fue eliminado del scope por decisión T1-Alfredo el 15 mayo 2026. NO reintroducir sin DSC explícito.

### LF-5: RLS desde nacimiento, sin excepciones

Toda tabla nueva en `apps/la-forja/migrations/` nace con RLS habilitado y al menos una policy explícita en la misma migración. Esto es Regla Dura #7 del repo raíz, pero La Forja la audita en CI específico.

### LF-6: Telemetría Test Bench obligatoria

Toda interacción del usuario T1-Padre con La Forja DEBE generar al menos un evento en `forja_telemetry`. Esto incluye: confusión detectada, simplificación pedida, abandono de tarea, completitud de sprint. Sin telemetría, la Misión Emergente C falla.

### LF-7: Rate limit hard-cap $50/mes/usuario

Cualquier usuario que llegue al cap de $50/mes/usuario es bloqueado en backend. Solo T1-Alfredo puede desbloquear binariamente desde `forja_budget`. Esta regla protege presupuesto del Monstruo.

### LF-8: Coordinación con Manus E2 (VERIFICADOR-001)

Manus E2 tiene lock activo declarativo desde 14 mayo 2026 sobre `tools/`, `kernel/`, `scripts/cowork_*`. La Forja **NO** toca estos directorios. Si E2 levanta el lock, se requiere bridge file explícito antes de coordinar scopes.

### LF-9: Coordinación con Cowork

Cowork audita el SPEC v3.1 con DSC-G-008 v3 antes de cualquier código de negocio. Cowork también audita los entregables D6 con `_check_no_tokens.sh` + audit binario de contenido. La Forja NO se mergea sin firma Cowork explícita en bridge file.

### LF-10: Anti-Dory embebido como showcase

La Forja es la primera app del Monstruo que consume su propia medicina (Sprint MANUS-ANTI-DORY-002). Toda sesión >5h debe generar resumen automático cada 1h en `forja_threads.canonical_summary`. Esta regla NO se diseña — se prueba en producción.

## Tests obligatorios antes de declarar D1-D6 verde

| Día | Test obligatorio |
|---|---|
| D1 | `bash scripts/_check_rls_default.py apps/la-forja` exit 0 |
| D2 | `pnpm --filter la-forja-api test` 100% PASS |
| D3 | `pnpm --filter la-forja-web build` exit 0 |
| D4 | `curl http://localhost:8081/api/auth/google` HTTP 302 |
| D5 | 13/13 ACs binarios verde con outputs reproducibles en bridge file |
| D6 | `bash scripts/_check_no_tokens.sh` + Cowork audit binario verde |

## Doctrina de fallas

Si La Forja cae en producción mientras T1-Padre la usa, runbook §12 del SPEC aplica. Notificación a T1-Alfredo es prioritaria sobre auto-recuperación. NO ocultar fallas con auto-restart silencioso.

## Modelo de contribución

Solo Manus E1 escribe código en este directorio durante D1-D6. Cowork audita pero no escribe. T1-Alfredo dirige y firma. T1-Padre prueba y reporta telemetría sin escribir código (sería sesgo de constructor).

Post-D6, contribuciones nuevas requieren PR + DSC-G-008 v3 audit + firma T1-Alfredo. NO self-merge. NO excepciones.
