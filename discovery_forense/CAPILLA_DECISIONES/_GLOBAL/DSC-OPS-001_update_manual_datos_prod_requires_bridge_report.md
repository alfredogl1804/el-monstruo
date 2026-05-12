---
id: DSC-OPS-001
proyecto: GLOBAL
tipo: restriccion_operativa
titulo: "Todo UPDATE/DELETE manual sobre tablas productivas requiere bridge file reporte con SQL exacto + rollback path"
estado: borrador
fecha: 2026-05-12
fecha_firma_T1: PENDIENTE
autor_borrador: Cowork T2-A (post-D-5 cierre)
autor_propuesta_original: Manus Hilo Ejecutor 1 (durante Sprint D-5 — declaró UPDATE manual a scheduled_tasks next_run=NOW())
autorización_T1: PENDIENTE
fuentes:
  - bridge/manus_to_cowork_REPORTE_SPRINT_D5_2026_05_12.md (Ejecutor 1 declaró UPDATE manual)
  - DSC-S-012 (patrón análogo para migraciones schema)
cruza_con: [DSC-S-012, DSC-G-017, DSC-S-006 v1.1]
contrato_ejecutable_propuesto: pre-commit hook + bridge file template + audit log query
contrato_ejecutable_estado: aspiracional — sprint Cowork ~1h para implementar hook anti-update-sin-reporte
---

# DSC-OPS-001 — UPDATE manual datos prod requiere bridge file reporte

## Decisión

**Cualquier `UPDATE` / `DELETE` / `INSERT` masivo manual sobre tablas productivas de Supabase (filtros `WHERE` específicos sobre rows existentes, no migraciones schema) requiere reporte verbatim al bridge antes de ejecutarse, con SQL exacto + rollback path + razón operativa.**

Reglas duras derivadas:

1. **Diferenciación clara con DSC-S-012:** DSC-S-012 cubre migraciones de **schema** (`CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX`). DSC-OPS-001 cubre operaciones de **datos** (`UPDATE`, `DELETE`, `INSERT` masivo) sobre rows existentes en producción.

2. **Formato obligatorio del bridge file:**
   - Path: `bridge/manus_to_cowork_OPERACION_DATOS_PROD_<tabla>_<accion>_<fecha>.md`
   - Header con: `tabla`, `accion`, `rows_afectados_estimadas`, `razon_operativa`
   - SQL verbatim que se va a ejecutar (sin secrets)
   - **Rollback path explícito:** SQL inverso O backup row antes del UPDATE/DELETE O razón por la que rollback es imposible
   - `firmante_T1` (si requiere firma T1) o `autoridad_T2` (si es decisión arquitectónica reversible)

3. **Cuándo aplica el reporte:**
   - SÍ aplica: `UPDATE` con filtro `WHERE id IN (...)` o `WHERE column='valor'`
   - SÍ aplica: `DELETE` con cualquier filtro WHERE
   - SÍ aplica: `INSERT` masivo (>10 rows en operación atómica)
   - NO aplica: operaciones normales del kernel (Embrión escribiendo `embrion_memoria`, etc.)
   - NO aplica: testing local sin producción
   - NO aplica: schema changes (eso es DSC-S-012)

4. **Excepción operacional declarada:** si la urgencia operacional requiere ejecutar antes del reporte (ej: recuperación de incidente), reporte retroactivo dentro de 30 min con marca `[OPERACION_REACTIVA]` en el header + razón verbatim de por qué la urgencia no permitió pre-reporte.

5. **Cowork puede ejecutar `UPDATE`/`DELETE` vía MCP Supabase bajo dos condiciones:** (a) firma T1 explícita en chat de la sesión actual, (b) bridge file con rollback path documentado pre-ejecución.

---

## Por qué

### Evidencia binaria de la necesidad (Sprint D-5)

Hilo Ejecutor 1, durante Sprint D-5, hizo:

```sql
-- UPDATE manual scheduled_tasks para desbloquear las 3 zombies post-fix
UPDATE public.scheduled_tasks
SET next_run = NOW()
WHERE name IN ('causal_seeding', 'prediction_validation', 'vanguard_scan');
```

Esto fue **operacionalmente legítimo** (necesario para validar fix end-to-end sin esperar 24h naturales). Pero **quedó sin rastro doctrinal** — solo se mencionó en passing en el reporte D-5.

Resultado: si alguien re-investiga el incidente en 3 meses, el UPDATE manual queda invisible. Sin rastro, las 3 zombies parecerían haberse "auto-curado" por D-5 magic.

### Patrón análogo: DSC-S-012 (migraciones schema)

DSC-S-012 (firmado 2026-05-11) canoniza que migraciones SQL aplicadas inadvertidamente requieren PR retroactivo con marca `[DERIVA-RESUELTA]`. **Mismo principio aplica a operaciones de datos.**

DSC-OPS-001 extiende DSC-S-012 al dominio "operaciones de datos sobre rows existentes". El criterio es idéntico: **toda mutación de prod debe tener rastro trazable.**

### Por qué no es overhead innecesario

- 30 segundos extra escribir bridge file con SQL + rollback path
- Versus: incidentes futuros sin trazabilidad que requieren días de investigación forense
- ROI obvio post-3 meses de operación

---

## Contrato ejecutable propuesto

**Estado:** aspiracional (DSC-G-017 satisfied via marca explícita).

**Implementación pendiente** (sprint Cowork-puro ~1h):

1. **Pre-commit hook `data-ops-bridge-check`:**
   - Detecta scripts Python con strings `UPDATE` / `DELETE` / `INSERT` masivo sobre tablas `public.*`
   - Verifica que exista bridge file `OPERACION_DATOS_PROD_*` con misma fecha + tabla + acción
   - Si no existe → exit 1

2. **Bridge file template** en `bridge/templates/OPERACION_DATOS_PROD_TEMPLATE.md` con front-matter estructurado

3. **Audit log query** en `tools/_check_data_ops_audit.py`:
   - Verifica que cada UPDATE/DELETE masivo en `embrion_memoria` (audit log) tiene bridge file correspondiente
   - Genera reporte `reports/data_ops_audit_<fecha>.md`

ETA: 1h de Cowork-puro post-firma T1.

---

## Trazabilidad

- **Origen:** propuesta de Hilo Ejecutor 1 al cerrar Sprint D-5 con honestidad sobre UPDATE manual a scheduled_tasks
- **Cruza con:** DSC-S-012 (anti-deriva migraciones, patrón análogo schema), DSC-G-017 (DSC-as-Contract), DSC-S-006 v1.1 (RLS desde nacimiento — tablas con RLS service_role_only se benefician de este DSC porque solo Cowork+Manus pueden mutarlas)
- **Cierre operativo:** habilita auditoría forense a 3+ meses para incidentes que involucran mutaciones de datos no documentadas

---

**estado:** borrador — pendiente firma T1 explícita + audit T2-B + contrato ejecutable (sprint Cowork). Cowork NO canoniza unilateralmente.
