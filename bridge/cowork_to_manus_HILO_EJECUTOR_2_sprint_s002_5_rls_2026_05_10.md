# Cowork → Hilo Ejecutor 2 — Sprint S-002.5: Hardening RLS Producción

**Fecha:** 2026-05-10
**Origen:** sesión Cowork con Alfredo
**Destino:** Hilo Ejecutor 2 de Manus (segundo ejecutor con permisos GitHub + Supabase)
**Prioridad:** P0 (Tarea 1) + P1 (Tarea 2) + P2 (Tarea 3 documentación)
**Acción de Alfredo:** pegar el path de este archivo al Hilo Ejecutor 2

---

## Para Hilo Ejecutor 2 — contexto

Cowork ejecutó hoy (2026-05-10) auditoría completa de RLS en producción. Hallazgo brutal: **92 tablas en producción sin Row Level Security**, incluyendo:

- **`tool_secrets` con 8 filas, sin RLS = P0 CRÍTICO.** Si la `anon key` se filtra (eventualmente cuando se deploye Flutter pública), cualquiera puede `SELECT * FROM tool_secrets`.
- **`user_dossier` (1 fila) — datos personales del owner.**
- **5+ tablas P1 del stack del embrión.**

El reporte completo está en `bridge/audit_rls_2026_05_10.md`. Léelo antes de empezar.

**Contexto de paralelismo:** mientras vos hacés esto, el Hilo Ejecutor principal está cerrando Sprint EMBRION-NEEDS-001 (PR de integración mergeado a `main`, esperando deploy Railway), y el Hilo Catastro está haciendo Sprint 88 (macroárea AGENTES). **Cero overlap entre los 3 frentes.**

---

## Objetivo

Activar Row Level Security en las tablas P0 y P1 de Supabase del proyecto `xsumzuhwmivjgftsneov`, con políticas mínimas que permiten al kernel (que usa `service_role`) seguir funcionando, pero bloquean acceso vía `anon key` a datos sensibles.

---

## Pre-flight obligatorio (4 pasos)

### Paso 1 — leer la auditoría completa

`bridge/audit_rls_2026_05_10.md` tiene el inventario clasificado de las 92 tablas con priorización.

### Paso 2 — verificar estado actual

```sql
-- Confirmar que las P0 efectivamente NO tienen RLS hoy
SELECT c.relname, c.relrowsecurity
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('tool_secrets', 'user_dossier', 'monstruo_memory',
                     'error_memory', 'error_memory_patterns', 'episodic_memory',
                     'embrion_budget_state', 'frontend_sessions');
```

Esperás ver `relrowsecurity = false` para todas. Si alguna ya está en `true`, márcalo y skipea esa.

### Paso 3 — confirmar que el kernel usa `service_role`

Verificar que `SUPABASE_SERVICE_ROLE_KEY` está en env vars del kernel en Railway. Si está, las nuevas policies con `auth.role() = 'service_role'` van a permitir al kernel seguir funcionando.

```bash
# En Railway dashboard o CLI
railway variables get --service el-monstruo-kernel | grep SUPABASE
```

Esperás ver `SUPABASE_SERVICE_ROLE_KEY` presente. Si NO está, el kernel está usando anon key y este sprint requiere coordinación adicional.

### Paso 4 — snapshot del estado del kernel pre-sprint

```sql
-- Capturar tasa de éxito de queries del kernel últimas 24h
SELECT count(*) FROM embrion_memoria WHERE created_at > NOW() - INTERVAL '24 hours';
SELECT count(*) FROM monstruo_memory;
SELECT count(*) FROM tool_secrets;
```

Guardar estos números. Vas a comparar contra los mismos valores DESPUÉS del sprint para validar que el kernel sigue accediendo normalmente.

---

## Tareas

### Tarea 1 — P0 Inmediato (1-2 horas)

**perfil_riesgo:** write-risky (cambia gobernanza de seguridad en producción)

Activar RLS en las 2 tablas P0 con policy `service_role_only`:

```sql
-- 0004_enable_rls_p0_critico.sql
BEGIN;

-- tool_secrets — 8 filas con credenciales potenciales
ALTER TABLE public.tool_secrets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON public.tool_secrets
  AS PERMISSIVE FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- user_dossier — datos personales del owner
ALTER TABLE public.user_dossier ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON public.user_dossier
  AS PERMISSIVE FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMIT;
```

**Verificación post-aplicación:**

```sql
-- Confirmar RLS activo en ambas
SELECT relname, relrowsecurity FROM pg_class
WHERE relname IN ('tool_secrets', 'user_dossier');
-- Esperado: ambas con relrowsecurity=true

-- Confirmar policies creadas
SELECT tablename, policyname FROM pg_policies
WHERE tablename IN ('tool_secrets', 'user_dossier');
-- Esperado: 2 policies "service_role_only"
```

**Smoke test del kernel:**
- Llamar al endpoint del kernel `GET /v1/health` en Railway → esperar 200 OK
- Verificar que el embrión sigue procesando (query a `embrion_memoria` últimas 5 min muestra actividad si está corriendo)

**Si el kernel falla:** rollback inmediato:
```sql
ALTER TABLE public.tool_secrets DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_dossier DISABLE ROW LEVEL SECURITY;
```

**Evidencia de cumplimiento:**
- PR con la migración SQL
- Output de la verificación post-aplicación
- Reporte del smoke test del kernel

### Tarea 2 — P1 stack del embrión (2-4 horas)

**perfil_riesgo:** write-risky (mismo razonamiento que Tarea 1, escala mayor)

Mismo patrón para 6 tablas P1:
- `monstruo_memory` (68 filas)
- `error_memory` (34 filas)
- `error_memory_patterns` (0 filas, tabla preparada)
- `episodic_memory` (0 filas, tabla preparada)
- `embrion_budget_state` (recién creada)
- `frontend_sessions` (0 filas, tabla preparada)

```sql
-- 0005_enable_rls_p1_embrion_stack.sql
BEGIN;

ALTER TABLE public.monstruo_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.monstruo_memory
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- ... repetir patrón para las otras 5

COMMIT;
```

**Verificación crítica post-Tarea 2:**

El embrión sigue funcionando. Esto es importante porque `monstruo_memory` y `error_memory` son tablas que el kernel usa activamente.

```sql
-- Verificar que el embrión puede seguir leyendo monstruo_memory
SELECT count(*) FROM monstruo_memory; -- ejecuta como service_role: debe devolver 68
SELECT count(*) FROM error_memory; -- debe devolver 34
```

Si el conteo cambia o los queries fallan, hay problema. Rollback inmediato.

**Evidencia de cumplimiento:**
- PR con migración SQL
- Pre/post snapshot de conteos
- Smoke test del kernel pasando
- Logs del kernel sin errores RLS-related en últimos 30 min

### Tarea 3 — Documentación + sprint S-002.6 propuesto

**perfil_riesgo:** write-safe

Documentar:

1. **DSC nuevo: DSC-S-006 — Política RLS por defecto en tablas nuevas**
   - Toda tabla nueva en producción debe nacer con RLS habilitado
   - Policy mínima: `service_role_only` salvo justificación explícita
   - Linter ideal: pre-commit hook que rechaza migraciones SQL sin `ENABLE ROW LEVEL SECURITY` para nuevas tablas

2. **Postmortem en `bridge/postmortem_sprint_s002_5_rls_2026_05_XX.md`** con:
   - Estado pre-sprint (8 tablas P0+P1 sin RLS)
   - Estado post-sprint (8 tablas con RLS activado)
   - Smoke tests resultados
   - Tablas P2 restantes (85) que requieren Sprint S-002.6 sistemático

3. **Sprint S-002.6 — Hardening RLS sistemático para P2** propuesto en `bridge/sprints_propuestos/`. Es el sprint que cubre las 85 tablas restantes. Tu sprint solo cubre las 8 críticas.

**Evidencia de cumplimiento:**
- DSC-S-006 firmado y agregado al `_INDEX.md`
- Postmortem completo
- Spec del sprint S-002.6 listo para asignación futura

---

## Criterios de éxito objetivos del sprint

Cuando los 5 son ✅, el sprint cierra:

- [ ] **`tool_secrets` con RLS habilitado + policy `service_role_only`**
- [ ] **`user_dossier` con RLS habilitado + policy `service_role_only`**
- [ ] **6 tablas P1 del stack del embrión con RLS habilitado** (monstruo_memory, error_memory, error_memory_patterns, episodic_memory, embrion_budget_state, frontend_sessions)
- [ ] **Smoke test del kernel PASS** post-cada tarea (sin errores 403/permission denied en logs)
- [ ] DSC-S-006 firmado + postmortem + spec S-002.6 propuesto

---

## Reglas operativas durante el sprint

1. **NO modifiques `kernel/embrion_loop.py`.** Zona del Hilo Ejecutor principal.
2. **NO toques `embrion_memoria`** — esa tabla SÍ tiene RLS habilitado actualmente, no la rompas.
3. **NO empieces Tarea 2 hasta que Tarea 1 PASS smoke test.** Aislar problemas si aparecen.
4. **Rollback inmediato si hay cualquier signo de fallo en kernel.** El P0 puede esperar 24 horas más; un kernel caído en producción no.
5. **Coordiná con Hilo Catastro** si vas a tocar tablas que están consumiendo (`catastro_modelos`, `catastro_*`). Probablemente NO necesario para tu sprint pero confirmá.
6. **Reporte cada Tarea cerrada** vía `embrion_memoria` con `tipo='mensaje_alfredo'`, `hilo_origen='manus_ejecutor_2'`, `importancia=8`.

---

## Cierre del sprint

Cuando los 5 criterios estén ✅:

1. 2 PRs mergeados a `main` (uno por Tarea 1, otro por Tarea 2)
2. Migraciones aplicadas en producción
3. Postmortem firmado
4. DSC-S-006 firmado
5. Sprint S-002.6 propuesto en `bridge/sprints_propuestos/`
6. Notificación a Alfredo vía cowork_bridge

---

## Plan de contingencia

Si Tarea 1 falla:
- Rollback inmediato (DISABLE ROW LEVEL SECURITY)
- Reportar a Alfredo con el error exacto
- NO empezar Tarea 2

Si Tarea 1 PASS pero Tarea 2 falla en alguna tabla específica:
- Rollback solo de esa tabla
- Continuar con las que funcionan
- Documentar la que falló para investigación posterior

---

## Si te trabás

Si en cualquier momento te trabás más de 30 min con un blocker concreto, escalá a Alfredo vía cowork_bridge insertando en `embrion_memoria` con `tipo='mensaje_alfredo'`, `hilo_origen='manus_ejecutor_2_blocked'`, importancia=10, contenido con la pregunta exacta + lo que probaste + el error exacto.

---

*Spec listo para ejecución sin ediciones adicionales.*
*Autoridad: Alfredo Góngora, sesión Cowork 2026-05-10.*
*Auditoría base: `bridge/audit_rls_2026_05_10.md`.*
*Cowork está disponible para audit DSC-G-008 v2 al cierre.*
