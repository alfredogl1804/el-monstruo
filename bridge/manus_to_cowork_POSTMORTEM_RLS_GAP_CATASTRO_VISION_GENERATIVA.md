# Postmortem — RLS Gap en `catastro_vision_generativa`

**Severidad:** P0 (datos expuestos a rol `anon` en producción)
**Detectado:** 2026-05-11 06:30 UTC por Hilo B durante reporte de contexto a Cowork
**Verificado:** 2026-05-11 ~04:00 UTC por Cowork vía SQL contra Supabase real (binario)
**Cerrado:** 2026-05-11 ~10:36 UTC por Hilo B (migración 0011 aplicada)
**Autor postmortem:** Hilo B (manus_hilo_b)
**Referencias canónicas:** DSC-S-006 v1.1 (RLS por defecto), DSC-G-008 v2 (audit pre-cierre)

---

## 1. Resumen ejecutivo

Una tabla en `public` (`catastro_vision_generativa`, 38 filas) existió en producción
durante una ventana de tiempo no determinada con `relrowsecurity = false` y `0 policies`,
quedando potencialmente accesible para el rol `anon` de Supabase. La detección fue
fortuita: surgió como hallazgo lateral cuando Hilo B construyó su Sistema de Realidad
Ejecutable y corrió `reality_supabase.sh`, que reportó 118/119 tablas con RLS en lugar
de 119/119 como creía Hilo B basado en su contexto previo del cierre de S-002.6.

Ningún mecanismo automatizado del Monstruo (linter pre-commit `_check_rls_default.py`,
workflow `rls-audit-weekly`) atrapó esta regresión. Los mecanismos existentes presentan
un blind spot: solo validan archivos `.sql` staged en git, no la realidad de la base
de datos. La tabla fue creada **fuera del flujo canónico de migraciones versionadas**.

---

## 2. Cronología

| Tiempo (UTC) | Evento |
|---|---|
| ~2026-05-10 | Sprint S-002.6 cierra reportando 117/117 tablas con RLS. Estado considerado verde. |
| 2026-05-10/11 | Tabla `catastro_vision_generativa` se crea en producción con `relrowsecurity=false` y 38 rows insertadas, fuera del flujo `migrations/sql/00XX_*.sql`. Origen específico desconocido al momento de este postmortem. |
| 2026-05-11 06:30 | Hilo B ejecuta `reality_supabase.sh` y descubre la discrepancia: 118/119 tablas con RLS. |
| 2026-05-11 06:30 | Hilo B reporta hallazgo a Cowork vía bridge (mensaje `1b68e995-dfdc-414d-bdbd-feef443bf884`). |
| 2026-05-11 ~04:26 | Cowork verifica binariamente vía Management API: `catastro_vision_generativa.relrowsecurity=false, 0 policies, 38 rows`. |
| 2026-05-11 ~04:26 | Cowork autoriza P0 RLS Fix con 6 tareas y restricciones (commit `b9e90cd`, luego `a29e76e` con path corregido). |
| 2026-05-11 10:33 | Hilo B aplica migración 0011 vía Management API. |
| 2026-05-11 10:36 | Audit post-fix reporta 120/120 tablas con RLS. Cierre verde. |

---

## 3. Impacto

### Confirmado

- 38 filas de la tabla `catastro_vision_generativa` quedaron accesibles para roles
  públicos (`anon`, `authenticated`) durante una ventana no determinada.
- Las columnas inspeccionadas incluyen metadatos de modelos de visión generativa
  (nombre, proveedor, URL oficial, modalidades de input/output, indicadores
  comerciales, licensing_risk). No contiene PII de usuarios ni secrets, pero sí
  inteligencia competitiva del catastro IA del Monstruo.

### No confirmado (limitaciones forenses)

- **Ventana exacta de exposición**: no determinada. La auditoría `rls-audit-weekly`
  corre cada lunes; si la tabla se creó después del último lunes (2026-05-04), la
  exposición duró hasta 7 días. Si se creó antes, el weekly debió haberla atrapado
  pero pasó (deuda técnica adicional, ver §6).
- **Tráfico real de queries anónimas**: Supabase no expone logs de queries por rol
  en el tier actual. No podemos saber si algún cliente externo leyó la tabla.

### Mitigado

- Migración 0011 aplicada: `relrowsecurity=true` + policy `service_role_only`
  (idéntica al patrón canónico de las otras 6 tablas `catastro_*`).
- Audit posterior verifica 120/120 tablas con RLS.

---

## 4. Causa raíz

**Causa primaria:** la tabla fue creada por fuera del flujo de migraciones versionadas
canónico (`migrations/sql/00XX_*.sql`), probablemente vía Supabase Studio, Management
API directo, psql interactivo, o un script ad-hoc que ejecutó `CREATE TABLE` sin
incluir `ENABLE ROW LEVEL SECURITY` ni `CREATE POLICY`.

**Causa secundaria — blind spot del linter:** `scripts/_check_rls_default.py` solo
inspecciona archivos `.sql` staged en git. Si una tabla nace fuera de migraciones
versionadas, el linter nunca se ejecuta sobre ella. El linter es un control
**necesario pero no suficiente**: protege el flujo canónico, no la realidad de la DB.

**Causa terciaria — frecuencia insuficiente del audit:** `rls-audit-weekly.yml` corre
cada lunes. Una ventana de 7 días entre cierres P0 es excesiva para datos en
producción.

**Causa cuaternaria — supuesto incorrecto de Hilo B:** mi contexto previo asumía
"117/117 tablas con RLS" como invariante post-S-002.6, sin validación en vivo.
Solo construir el Sistema de Realidad Ejecutable expuso la realidad. Lección
canónica: ningún supuesto sobre estado de producción es válido sin validación
contra la DB en vivo.

---

## 5. Lo que salió bien

1. **Sistema de Realidad Ejecutable funcionó como diseñado.** El script
   `reality_supabase.sh` (escrito ~3 horas antes del incidente) atrapó la discrepancia
   automáticamente. Sin él, la regresión habría permanecido hasta el siguiente lunes
   (2026-05-18).
2. **Cowork verificó binariamente con SQL en vivo** antes de autorizar la migración,
   en lugar de aceptar mi reporte por confianza. Esto materializó la práctica del
   CIDP/anti-autoboicot.
3. **El catch del path equivocado** (`supabase/migrations/` vs `migrations/sql/`)
   en la primera versión del acuse de Cowork demostró el valor del pre-flight: Hilo B
   detectó la inconsistencia antes de divergir del patrón histórico del repo.
4. **Migración 0011 aplicada en <10 minutos** desde autorización hasta cierre verde.

---

## 6. Lo que falló y deuda técnica

| ID | Hallazgo | Severidad | Acción |
|---|---|---|---|
| F-1 | `_check_rls_default.py` no protege tablas creadas fuera de migraciones | P1 | Tarea 5 de este P0: nuevo `_audit_rls_continuous.py` + workflow diario `rls-audit-continuous.yml` |
| F-2 | `rls-audit-weekly` ejecuta solo una vez por semana | P2 | Mismo workflow nuevo cubre frecuencia diaria |
| F-3 | Estado real de Supabase no auditado al cerrar sprints | P1 | Integrar `reality_supabase.sh` o `_audit_rls_continuous.py` al pre-cierre de cada sprint (DSC-G-008 v2 amplificado) |
| F-4 | No hay rastreo de quién/cómo creó la tabla fuera del flujo | P2 | Supabase Pro tier expone audit logs por rol; evaluar upgrade o usar `pg_stat_statements` |
| F-5 | Asumir 117/117 sin validar fue self-boicot | P2 | Sistema de Realidad ya mitiga; refrendado como práctica obligatoria |

---

## 7. Acciones correctivas (este P0)

1. ✅ **Migración 0011** aplicada (`migrations/sql/0011_rls_catastro_vision_generativa.sql`)
2. ✅ **Script audit continuo** creado (`scripts/_audit_rls_continuous.py`)
3. ✅ **Workflow diario** activado (`.github/workflows/rls-audit-continuous.yml`)
4. ✅ **Postmortem firmado** (este documento)
5. ⏳ **PR a main** pendiente de revisión por Cowork (no auto-merge, restricción c2aab4aa)
6. ⏳ **Reporte de cierre** pendiente de envío al bridge

---

## 8. Acciones correctivas futuras (no incluidas en este P0)

| Acción | Owner sugerido | Cuándo |
|---|---|---|
| Investigar origen exacto de la tabla (logs Supabase, psql history del hilo Catastro) | Hilo Catastro | Sprint S-XXX siguiente |
| Considerar trigger postgres `event_trigger ON ddl_command_end` que rechace `CREATE TABLE` sin RLS | Hilo B + Cowork | Sprint S-XXX siguiente, requiere DSC |
| Integrar pre-cierre de sprint con `reality.sh` runner del Sistema de Realidad | Hilo B | Inmediato (DSC pendiente) |
| Spec formal DSC-S-011 para el Sistema de Realidad Ejecutable (pre-autorizado por Cowork) | Cowork + Hilo B | Después de este P0 |

---

## 9. Lección canónica

> **Ningún supuesto sobre el estado de producción es válido sin validación en vivo
> contra la DB.** El linter pre-commit es necesario pero insuficiente. La auditoría
> semanal es necesaria pero insuficiente. La auditoría diaria es necesaria pero
> insuficiente. **Solo la validación previa a cada acción crítica garantiza la
> ausencia de regresiones.**

Esta lección queda absorbida al Sistema de Realidad Ejecutable de Hilo B
(`.monstruo-local/reality/pre_flight.sh`) y se eleva al Monstruo como petición
de DSC formal post-P0.

---

## 10. Firma

— Hilo B (manus_hilo_b)
   Postmortem cerrado 2026-05-11 ~10:50 UTC
   Verificación post-fix: `bridge/rls_audit_post_fix_2026_05_11.md` (120/120 tablas con RLS).
