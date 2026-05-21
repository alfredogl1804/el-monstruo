# BATCH 006 — CÉLULA A: SUPABASE APPLY PLAN

## Objetivo
Definir el procedimiento exacto, determinístico y seguro para aplicar las migraciones de Anti-Dory (Batch 005 v0.2) a Supabase Production, minimizando riesgo y estableciendo pre-checks obligatorios.

## Orden de Migraciones

1. `0050_anti_dory_anchor_store.sql`
2. `0051_anti_dory_plan_ledger.sql`

*Nota: La numeración fue corregida en Batch 005 v0.2 para evitar colisión con `0009_cowork_sesiones.sql` y `0010_cowork_sesiones_metricas.sql` (violación DSC-G-013).*

## Pre-Checks Obligatorios (Antes de Aplicar)

1. **Backup:** Verificar que el backup automático diario de Supabase (PITR) se haya ejecutado exitosamente en las últimas 24 horas.
2. **Estado de Migraciones:** Ejecutar `SELECT * FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 5;` para confirmar que `0050` y `0051` no existen.
3. **Bloqueo de Escrituras (Opcional):** Si el tráfico es alto, pausar temporalmente operaciones que dependan de las tablas de `anti_dory` (actualmente ninguna, por ser nuevas).
4. **Validación de Archivos:** Verificar el hash SHA-256 de los archivos `.sql` locales contra los del repositorio en `main` (después del merge).

## SQL Apply Checklist (Paso a Paso)

### Paso 1: Aplicar 0050 (Anchor Store)
```bash
# Ejecutar desde el CLI de Supabase (requiere login y link al proyecto)
supabase db push --include 0050_anti_dory_anchor_store.sql
```
*Alternativa manual:* Copiar el contenido de `0050_anti_dory_anchor_store.sql` y ejecutarlo en el SQL Editor de Supabase Dashboard.

### Paso 2: Aplicar 0051 (Plan Ledger)
```bash
supabase db push --include 0051_anti_dory_plan_ledger.sql
```
*Alternativa manual:* Copiar el contenido de `0051_anti_dory_plan_ledger.sql` y ejecutarlo en el SQL Editor.

## Verification Queries (Post-Apply)

Ejecutar estas consultas para confirmar el éxito:

```sql
-- Verificar Anchor Store
SELECT count(*) FROM anti_dory_anchor_store;
-- Esperado: 0 (o el número de anchors iniciales si se insertaron)

-- Verificar Plan Ledger
SELECT count(*) FROM anti_dory_plan_ledger;
-- Esperado: 0

-- Verificar RLS
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'anti_dory%';
-- Esperado: rowsecurity = true para ambas tablas

-- Verificar Policies
SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public' AND tablename LIKE 'anti_dory%';
-- Esperado: policies de service_role para ambas tablas
```

## Rollback SQL (En caso de fallo)

Si alguna migración falla o causa inestabilidad, ejecutar inmediatamente:

```sql
-- Rollback 0051 (Plan Ledger)
DROP TABLE IF EXISTS anti_dory_plan_ledger CASCADE;
DELETE FROM supabase_migrations.schema_migrations WHERE version = '0051';

-- Rollback 0050 (Anchor Store)
DROP TABLE IF EXISTS anti_dory_anchor_store CASCADE;
DELETE FROM supabase_migrations.schema_migrations WHERE version = '0050';
```

## Confirmación
- **NO APPLY:** Este documento es solo un plan. No se ha ejecutado ninguna migración en Supabase.
- Requiere autorización explícita de T1 para proceder con la ejecución real.
