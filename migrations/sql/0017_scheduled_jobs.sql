-- ============================================================================
-- Migracion: 0017_scheduled_jobs
-- Autor: Manus (Hilo Ejecutor 1)
-- Fecha: 2026-05-11
--
-- Proposito:
-- Materializacion retroactiva de la tabla scheduled_jobs (5ta deriva DB-repo).
-- La tabla ya existe en produccion (Supabase xsumzuhwmivjgftsneov) con datos,
-- 20 columnas, constraints, 4 indices, trigger updated_at, RLS habilitado y
-- policy service_role_only. La 0008_rls_p2_completion.sql solo le aplica RLS
-- pero nunca creo la tabla en main.
--
-- Es la tabla padre referenciada por el FK de public.job_executions (0016).
-- DEBE mergearse ANTES de la 0016 para que el FK sea satisfacible en un
-- deploy desde cero. Si se ejecuta sobre prod (donde ya existe), todos los
-- patrones idempotentes la dejan intacta.
-- ============================================================================

-- 1. Tabla y columnas (idempotente: crea si no existe)
CREATE TABLE IF NOT EXISTS public.scheduled_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    thread_id text,
    title text NOT NULL,
    instruction text NOT NULL,
    run_at timestamp with time zone NOT NULL,
    timezone text NOT NULL DEFAULT 'America/Mexico_City'::text,
    channel text NOT NULL DEFAULT 'telegram'::text,
    status text NOT NULL DEFAULT 'scheduled'::text,
    recurrence text,
    max_retries integer NOT NULL DEFAULT 1,
    retry_count integer NOT NULL DEFAULT 0,
    last_error text,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    task_type text DEFAULT 'default'::text,
    estimated_cost_usd double precision DEFAULT 0.0,
    success_rate double precision DEFAULT 1.0,
    moc_priority_score double precision DEFAULT 50.0,
    last_prioritized_at timestamp with time zone
);

-- 2. Asegurar columnas si la tabla ya existia pero incompleta
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS user_id text NOT NULL;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS thread_id text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS title text NOT NULL;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS instruction text NOT NULL;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS run_at timestamp with time zone NOT NULL;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS timezone text NOT NULL DEFAULT 'America/Mexico_City'::text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS channel text NOT NULL DEFAULT 'telegram'::text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'scheduled'::text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS recurrence text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS max_retries integer NOT NULL DEFAULT 1;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS retry_count integer NOT NULL DEFAULT 0;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS last_error text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS created_at timestamp with time zone NOT NULL DEFAULT now();
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NOT NULL DEFAULT now();
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS task_type text DEFAULT 'default'::text;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS estimated_cost_usd double precision DEFAULT 0.0;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS success_rate double precision DEFAULT 1.0;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS moc_priority_score double precision DEFAULT 50.0;
ALTER TABLE public.scheduled_jobs ADD COLUMN IF NOT EXISTS last_prioritized_at timestamp with time zone;

-- 3. CHECK constraint en status (idempotente via DO block)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'scheduled_jobs_status_check'
    ) THEN
        ALTER TABLE public.scheduled_jobs
            ADD CONSTRAINT scheduled_jobs_status_check
            CHECK (status = ANY (ARRAY['scheduled'::text, 'running'::text, 'completed'::text, 'failed'::text, 'cancelled'::text]));
    END IF;
END $$;

-- 4. Indices (IF NOT EXISTS nativo, incluye un indice parcial WHERE)
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_user_id
    ON public.scheduled_jobs USING btree (user_id);

CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_status_run_at
    ON public.scheduled_jobs USING btree (status, run_at)
    WHERE (status = 'scheduled'::text);

CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_moc_score
    ON public.scheduled_jobs USING btree (moc_priority_score DESC, run_at)
    WHERE (status = 'scheduled'::text);

-- 5. Funcion del trigger updated_at (CREATE OR REPLACE es idempotente)
CREATE OR REPLACE FUNCTION public.update_scheduled_jobs_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$function$;

-- 6. Trigger updated_at (DROP IF EXISTS antes de CREATE para idempotencia)
DROP TRIGGER IF EXISTS trg_scheduled_jobs_updated_at ON public.scheduled_jobs;
CREATE TRIGGER trg_scheduled_jobs_updated_at
    BEFORE UPDATE ON public.scheduled_jobs
    FOR EACH ROW
    EXECUTE FUNCTION public.update_scheduled_jobs_updated_at();

-- 7. RLS y Policy (idempotentes via DO block)
ALTER TABLE public.scheduled_jobs ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'scheduled_jobs'
          AND policyname = 'service_role_only'
    ) THEN
        CREATE POLICY "service_role_only" ON public.scheduled_jobs
            AS PERMISSIVE FOR ALL TO public
            USING (auth.role() = 'service_role'::text)
            WITH CHECK (auth.role() = 'service_role'::text);
    END IF;
END $$;

-- 8. Comentarios
COMMENT ON TABLE public.scheduled_jobs IS 'Cola de jobs programados de El Monstruo (Sprint S-002.x). Tabla padre de job_executions. Materializado en 0017 (5ta deriva DB-repo).';
COMMENT ON COLUMN public.scheduled_jobs.moc_priority_score IS 'Score de priorizacion MOC (0-100, default 50). DESC index sobre status=scheduled.';
COMMENT ON COLUMN public.scheduled_jobs.recurrence IS 'Expresion cron-like opcional para jobs recurrentes (NULL = one-shot).';
