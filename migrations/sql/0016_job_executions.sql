-- ============================================================================
-- Migracion: 0016_job_executions
-- Autor: Manus (Hilo Ejecutor 1)
-- Fecha: 2026-05-11
--
-- Proposito:
-- Materializacion retroactiva de la tabla job_executions (4ta deriva DB-repo).
-- La tabla ya existe en produccion (Supabase xsumzuhwmivjgftsneov) pero el
-- codigo DDL nunca se commiteo en main.
-- 
-- Patrones aplicados:
-- 1. Idempotencia completa (IF NOT EXISTS, DO blocks para constraints/policies).
-- 2. RLS habilitado y policy 'service_role_only' replicada de prod.
-- 3. Referencia FK a scheduled_jobs respetada.
-- ============================================================================

-- 1. Tabla y columnas (idempotente: crea si no existe)
CREATE TABLE IF NOT EXISTS public.job_executions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduled_job_id uuid NOT NULL,
    started_at timestamp with time zone NOT NULL DEFAULT now(),
    finished_at timestamp with time zone,
    status text NOT NULL DEFAULT 'running'::text,
    trace_id text,
    result_summary text,
    error text,
    tokens_used integer DEFAULT 0,
    cost_usd numeric DEFAULT 0
);

-- 2. Asegurar columnas en caso de que la tabla ya existiera pero incompleta
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS scheduled_job_id uuid NOT NULL;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS started_at timestamp with time zone NOT NULL DEFAULT now();
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS finished_at timestamp with time zone;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'running'::text;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS trace_id text;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS result_summary text;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS error text;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS tokens_used integer DEFAULT 0;
ALTER TABLE public.job_executions ADD COLUMN IF NOT EXISTS cost_usd numeric DEFAULT 0;

-- 3. Constraints (idempotentes via DO block)
DO $$
BEGIN
    -- FK a scheduled_jobs
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'job_executions_scheduled_job_id_fkey'
    ) THEN
        ALTER TABLE public.job_executions 
            ADD CONSTRAINT job_executions_scheduled_job_id_fkey 
            FOREIGN KEY (scheduled_job_id) REFERENCES public.scheduled_jobs(id) ON DELETE CASCADE;
    END IF;

    -- CHECK constraint status
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'job_executions_status_check'
    ) THEN
        ALTER TABLE public.job_executions 
            ADD CONSTRAINT job_executions_status_check 
            CHECK (status = ANY (ARRAY['running'::text, 'completed'::text, 'failed'::text]));
    END IF;
END $$;

-- 4. Indices (IF NOT EXISTS nativo)
CREATE INDEX IF NOT EXISTS idx_job_executions_job_id ON public.job_executions USING btree (scheduled_job_id);

-- 5. RLS y Policies (idempotentes via DO block)
ALTER TABLE public.job_executions ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
          AND tablename = 'job_executions' 
          AND policyname = 'service_role_only'
    ) THEN
        CREATE POLICY "service_role_only" ON public.job_executions
            AS PERMISSIVE FOR ALL TO public
            USING (auth.role() = 'service_role'::text)
            WITH CHECK (auth.role() = 'service_role'::text);
    END IF;
END $$;

-- 6. Comentarios
COMMENT ON TABLE public.job_executions IS 'Registro historico de ejecuciones de scheduled_jobs (Sprint S-002.x). Materializado en 0016.';
