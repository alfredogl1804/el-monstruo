# DSC-S-006 — RLS por defecto en tablas nuevas de Supabase

**Estado:** FIRMADO
**Fecha:** 2026-05-10
**Origen:** Sprint S-002.5 (Hardening RLS Producción)
**Alcance:** GLOBAL (aplica a todas las tablas Supabase del proyecto)
**Categoría:** Seguridad (DSC-S-*)

---

## Contexto

Antes de este DSC, las tablas creadas en Supabase nacían sin Row Level Security. Esto produjo el incidente detectado en `bridge/audit_rls_2026_05_10.md`: 8 tablas P0+P1 expuestas vía la anon key (publishable), incluyendo `tool_secrets` (credenciales) y `user_dossier` (datos personales). El Sprint S-002.5 cerró el incidente activando RLS retroactivamente, pero la **causa raíz** —ausencia de política preventiva— sigue presente.

Sin esta política, cada nueva tabla creada vía migración o vía Supabase Studio queda automáticamente expuesta a la anon key hasta que un humano se acuerde de habilitar RLS y crear policies. Esa "lista mental" no es una garantía de seguridad.

## Decisión

> **Toda tabla nueva en `public` schema de Supabase debe nacer con RLS habilitado y al menos una policy explícita. No existe excepción "por ahora la dejamos abierta y luego ponemos RLS".**

### Reglas duras

1. **Cada migración SQL que crea una tabla DEBE incluir, en el mismo archivo:**
   - `ALTER TABLE <tabla> ENABLE ROW LEVEL SECURITY;`
   - Al menos un `CREATE POLICY` con condición explícita (USING + WITH CHECK).
   - Comentario `COMMENT ON POLICY ... IS 'Sprint X-Y (fecha): justificación';`.

2. **El patrón canónico por defecto es `service_role_only`:**
   ```sql
   CREATE POLICY "service_role_only"
     ON public.<tabla>
     AS PERMISSIVE
     FOR ALL
     TO public
     USING (auth.role() = 'service_role')
     WITH CHECK (auth.role() = 'service_role');
   ```
   Solo el kernel (que usa service_role key) puede leer/escribir.

3. **Si la tabla necesita acceso desde frontend con anon o usuario autenticado**, la policy DEBE expresar la regla de negocio explícita, por ejemplo:
   ```sql
   -- Ejemplo: usuario solo lee sus propias filas
   USING (auth.uid() = user_id)
   ```
   Nunca dejar la tabla sin policy. Una tabla con RLS habilitado pero sin policies bloquea TODO acceso (incluido service_role en algunos casos), lo cual es preferible a fuga, pero es deuda y debe documentarse.

4. **Excepción explícita** (solo con DSC firmado caso por caso): tablas de catálogo público, sin datos sensibles, donde el acceso anon es deseado por diseño. En esos casos:
   ```sql
   CREATE POLICY "anon_read_only"
     ON public.<tabla>
     FOR SELECT
     TO public
     USING (true);
   ```
   Y el DSC del sprint correspondiente debe justificar por qué ese dataset es público.

5. **Validación pre-merge:** el script `scripts/_check_no_tokens.sh` (DSC-G-008) se extiende para incluir un linter que rechaza migraciones con `CREATE TABLE` en schema `public` que no contengan `ENABLE ROW LEVEL SECURITY` y `CREATE POLICY` en el mismo archivo. (Implementación: Sprint S-002.6.)

6. **Auditoría periódica:** cada sprint que toca migraciones SQL DEBE incluir, como tarea de cierre, una query de verificación equivalente a la usada en S-002.5:
   ```sql
   SELECT c.relname AS tabla, c.relrowsecurity AS rls,
          (SELECT count(*) FROM pg_policies WHERE tablename = c.relname AND schemaname = 'public') AS num_policies
   FROM pg_class c
   JOIN pg_namespace n ON n.oid = c.relnamespace
   WHERE n.nspname = 'public' AND c.relkind = 'r'
   ORDER BY c.relrowsecurity ASC, c.relname;
   ```
   Si alguna tabla aparece con `rls=false` o `num_policies=0`, es deuda crítica y bloquea el cierre del sprint.

## Implicaciones

- **Sprints futuros que toquen `migrations/sql/*` deben adherirse a este DSC.** Cualquier migración que cree tabla sin RLS+policy se rechaza en code review.
- **Cowork audita el contenido del SQL** (no solo el reporte) como parte de DSC-G-008 v2.
- **El kernel no requiere cambios** porque ya usa service_role; las policies `service_role_only` son transparentes.
- **El frontend (si lo hay) DEBE usar la anon key con queries que respeten las policies.** Si el frontend rompe post-RLS, la solución no es deshabilitar RLS sino diseñar la policy correctamente.

## Excepciones canonizadas en el momento del DSC

- `embrion_memoria`: ya tiene `relrowsecurity=true` con 0 policies explícitas (estado encontrado pre-S-002.5). Documentar la policy real o agregar una en sprint posterior, pero NO se baja RLS para "limpiar".

## Referencias

- `bridge/audit_rls_2026_05_10.md` (auditoría base)
- `bridge/cowork_to_manus_HILO_EJECUTOR_2_sprint_s002_5_rls_2026_05_10.md` (spec del sprint que cerró el incidente)
- `migrations/sql/0004_enable_rls_p0_critico.sql` (Tarea 1)
- `migrations/sql/0005_enable_rls_p1_embrion_stack.sql` (Tarea 2)
- `bridge/postmortem_sprint_s002_5_rls_2026_05_10.md` (postmortem)
- DSC-S-001 a DSC-S-005 (familia de seguridad)
- DSC-G-008 v2 (validación pre-cierre que extenderá esta regla)
