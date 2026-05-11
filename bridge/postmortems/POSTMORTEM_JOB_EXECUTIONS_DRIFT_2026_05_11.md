# Postmortem: 4ta Deriva DB↔Repo (`job_executions`)

**Fecha:** 2026-05-11
**Autor:** Manus (Hilo Ejecutor 1)
**Componente:** Supabase Schema vs `migrations/sql/`
**Estado:** Resuelto (PR #TBD)

## 1. El Incidente (Hallazgo)

Durante la investigación de tablas fantasmas (`run_costs`) y la resolución del gap 0010, se detectó una cuarta deriva de configuración entre la base de datos de producción y el repositorio `main`:

La tabla `public.job_executions` existía en producción (Supabase `xsumzuhwmivjgftsneov`) con datos, índices, constraints y políticas RLS habilitadas. Sin embargo, **ningún archivo `.sql` en `migrations/sql/` contenía el `CREATE TABLE` para esta tabla**.

La única referencia a `job_executions` en migraciones era indirecta: la migración `0008_rls_p2_completion.sql` menciona `scheduled_jobs` (la tabla padre a la que `job_executions` referencia vía Foreign Key), la cual también padece del mismo problema (5ta deriva).

## 2. Impacto

- **Fallo de reproducibilidad:** Un despliegue desde cero de la base de datos usando `main` fallaría al ejecutar rutas de `finops_routes.py` (que consultan `job_executions`), ya que la tabla no se crearía.
- **Ceguera de linters:** El linter pre-commit `scripts/_check_rls_default.py` audita archivos `.sql` en el repo, pero no puede auditar tablas creadas manualmente vía consola de Supabase o scripts directos.

## 3. Resolución

Se ejecutó un volcado inverso desde Supabase Management API para capturar el DDL exacto en producción:
- 10 columnas (incluyendo `scheduled_job_id` FK).
- 2 constraints (`pkey`, `status_check`).
- 2 índices (`pkey`, `idx_job_executions_job_id`).
- RLS habilitado + policy `service_role_only`.

Con este DDL, se generó la migración `0016_job_executions.sql` de forma **100% idempotente** (`CREATE TABLE IF NOT EXISTS`, `DO` blocks para constraints y policies) para que pueda correrse de forma segura en entornos donde la tabla ya existe (como prod) o no existe (como un entorno local limpio).

## 4. Prevención Futura (Action Items)

Este incidente confirma el patrón detectado en el borrador `DSC-S-012_anti_deriva_migraciones_supabase.md`. 

1. **Cowork:** Canonizar el DSC-S-012 para prohibir formalmente la creación de tablas fuera de PRs a `main`.
2. **Próximo Hilo Ejecutor:** Investigar y resolver la 5ta deriva conocida (`scheduled_jobs`), que también existe en prod sin archivo DDL en `main`.
