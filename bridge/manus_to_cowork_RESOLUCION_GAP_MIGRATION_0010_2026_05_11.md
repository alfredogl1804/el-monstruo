---
id: manus_to_cowork_RESOLUCION_GAP_MIGRATION_0010_2026_05_11
fecha: 2026-05-11
emisor: Manus Hilo Ejecutor (principal)
receptor: Cowork T2 Arquitecto + Alfredo
prioridad: P1
decision_aplicada: Opción C + corrección lateral (autorizada por Alfredo)
estado: ejecutado_pendiente_aplicar_migracion
---

# Resolución del gap migration 0010

## Contexto

Alfredo pidió investigar por qué `migrations/sql/` saltaba del 0009 al 0011 sin 0010. Tras investigación en tres frentes (filesystem, git history all-branches, Supabase Management API) se identificó la causa raíz y se aplicó la Opción C + corrección lateral del reporte binario.

## Causa raíz (verificada)

Tres factores convergentes generaron el slot 0010 vacío en `main`:

1. **Spec firmado de Cowork (líneas 49 y 117-122 del documento `cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11.md`)** asignó el slot `0010_cowork_sesiones_metricas.sql` al pre-trabajo del ramp COWORK-RUNTIME (6 columnas KPI). Este archivo nunca fue creado por Manus T3 porque el ramp aún no arrancó (espera cierre P0 RLS primero).

2. **Sprint S-003.B (Hilo Ejecutor 2)** introdujo en su rama `sprint/s-003-b-audit-middleware-pentest` un `0010_kernel_audit_log_truncate_guard.sql` distinto, colisionando con el slot reservado por la spec anterior. La rama no fue mergeada a main.

3. **El contenido del 0010 del Sprint S-003.B SÍ fue aplicado directamente contra producción Supabase** (los triggers `kal_no_update`, `kal_no_delete` y `kal_no_truncate` existen activos en `public.kernel_audit_log`), pero el archivo no llegó a main. Resultado: deriva DB↔repo.

## Decisión aplicada

**Opción C + corrección lateral.** Alfredo autorizó honrar la asignación original de la spec firmada de Cowork. El slot 0010 queda asignado a `cowork_sesiones_metricas`. El Sprint S-003.B debe renumerar sus migraciones a 0013 y 0014 antes de mergear.

## Artefactos producidos

### 1. `migrations/sql/0010_cowork_sesiones_metricas.sql`

Migración idempotente que agrega 6 columnas a `public.cowork_sesiones`:

| Columna | Tipo | Default | Origen spec |
|---|---|---|---|
| `interceptaciones_count` | integer NOT NULL | 0 | Línea 117 |
| `antipattern_hits` | integer NOT NULL | 0 | Línea 118 |
| `suggest_pause_blocks` | integer NOT NULL | 0 | Línea 119 |
| `preflight_missing_count` | integer NOT NULL | 0 | Línea 120 |
| `semantic_extra_catches` | jsonb NOT NULL | `'[]'::jsonb` | Línea 121 |
| `false_positive_reports` | jsonb NOT NULL | `'[]'::jsonb` | Línea 122 |

Idempotente vía `ADD COLUMN IF NOT EXISTS`. No toca RLS — la policy `service_role_only` heredada de `0009_cowork_sesiones.sql` queda intacta. Aplicar via `scripts/_apply_migration_0010.py` (a crear si no existe siguiendo patrón de `_apply_migration_0011.py`) usando `SUPABASE_SERVICE_KEY` o vía `~/.monstruo/sb_sql.py`.

### 2. `bridge/manus_to_ejecutor2_RENUMERAR_SPRINT_S003B_2026_05_11.md`

Aviso al Hilo Ejecutor 2 indicando que debe renumerar sus migraciones a 0013 y 0014, hacerlas idempotentes, y documentar la deriva en el PR cuando lo abra. Incluye paso a paso técnico, ejemplo de comandos `git mv` y patrón idempotente requerido.

### 3. Este documento (resolución canónica firmada)

## Pregunta abierta para Cowork (resuelta durante la sesión)

Durante la investigación inicial detecté que `migrations/sql/0012_embrion_inbox.sql` aparecía en mi working tree con mtime `2026-05-11 06:55`. Tras verificación de ramas con `git branch --contains`, identifiqué que el archivo pertenece a la rama `sprint/embrion-needs-002-t5-daddy-impl` (commits `597fc35` y `1d1569c` del Hilo Embrion-Daddy T5), **no mergeada a main**. La tabla `embrion_inbox` SÍ existe ya en Supabase prod (verificado via `sb_sql.py`), generando una tercera deriva DB↔repo análoga a la del Sprint S-003.B. Cowork debería coordinar el merge de esa rama o pedir su postmortem si fue ejecución no autorizada.

## Estado de la deriva DB↔repo

| Objeto en Supabase prod | Archivo en `main` | Estado deriva |
|---|---|---|
| Tabla `kernel_audit_log` | NO existe | ⚠️ Deriva — pendiente merge S-003.B renumerado a 0013 |
| Trigger `kal_no_update` | NO existe | ⚠️ Deriva — pendiente merge S-003.B renumerado a 0013 |
| Trigger `kal_no_delete` | NO existe | ⚠️ Deriva — pendiente merge S-003.B renumerado a 0013 |
| Trigger `kal_no_truncate` | NO existe | ⚠️ Deriva — pendiente merge S-003.B renumerado a 0014 |
| Columnas KPI en `cowork_sesiones` | Archivo 0010 creado, no aplicado | 🟡 Repo > DB — falta aplicar migración |
| Tabla `embrion_inbox` | `0012_embrion_inbox.sql` solo en rama `sprint/embrion-needs-002-t5-daddy-impl` (NO mergeada a main) | ⚠️ Deriva — pendiente merge sprint EMBRION-NEEDS-002 T5 |

## Próximos pasos (por orden)

1. **Manus (yo):** commitear los 3 artefactos en rama dedicada y abrir PR a main.
2. **Alfredo o Cowork:** revisar PR y mergear, o pedirme ajustes.
3. **Manus (yo) tras merge:** crear `scripts/_apply_migration_0010.py` siguiendo patrón de `0011`, o aplicar directo via `sb_sql.py`.
4. **Manus (yo) tras aplicar:** correr query de verificación de las 6 columnas y reportar en `bridge/manus_to_cowork_REPORTE_FLAGS_RAMP_READY.md` (punto 4 del pre-trabajo del spec).
5. **Hilo Ejecutor 2:** leer aviso, renumerar S-003.B a 0013/0014 con idempotencia.
6. **Cowork:** verificar el origen del `0012_embrion_inbox.sql`.

## DoD de esta resolución

- [x] Causa raíz identificada y verificada en 3 frentes
- [x] Migración 0010 creada honrando spec firmado
- [x] Aviso a Hilo Ejecutor 2 redactado con instrucciones de renumeración
- [x] Documento de resolución canónica firmado
- [ ] PR a main abierto (siguiente paso)
- [ ] Migración aplicada en producción Supabase
- [ ] Verificación de 6 columnas post-aplicación

---

*Firmado por Manus Hilo Ejecutor (principal), 2026-05-11. Decisión "Opción C + corrección lateral" autorizada por Alfredo tras reporte binario gap_0010.*
