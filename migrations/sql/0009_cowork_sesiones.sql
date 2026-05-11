-- =============================================================================
-- 0009_cowork_sesiones.sql
-- =============================================================================
-- Sprint   : COWORK-RUNTIME-001
-- Tarea    : T3 MAGNA P0
-- Objetivo : Memoria persistente entre sesiones Cowork
-- Origen   : memory/cowork/AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md (M3)
-- Doctrina : DSC-S-006 (RLS por defecto), DSC-S-007 (naming canonico)
-- Hilo     : Manus T3 ejecutor (firmado bajo division DSC-MO-005)
--
-- Contexto:
--   El sustrato Cowork (Claude) no preserva contexto entre sesiones. Cada
--   nueva sesion arranca con sindrome de Dory operacional: olvida violaciones
--   detectadas, lecciones aprendidas, deudas pendientes y correctivos previos.
--
--   Esta tabla es la fuente de verdad de "estado vivo Cowork" para el
--   Pre-flight Memento extendido. Al inicio de cada sesion Cowork se lee
--   la ultima fila y se inyecta como contexto inicial.
--
-- RLS: service_role_only (canon DSC-S-006).
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.cowork_sesiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha_inicio TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    fecha_fin TIMESTAMP WITH TIME ZONE,
    duracion_minutos INT,
    turnos_totales INT NOT NULL DEFAULT 0,
    pre_flight_ejecutado BOOLEAN NOT NULL DEFAULT FALSE,
    commits_productivos INT NOT NULL DEFAULT 0,
    violaciones_detectadas JSONB NOT NULL DEFAULT '[]'::jsonb,
    palabras_clave_alfredo JSONB NOT NULL DEFAULT '[]'::jsonb,
    correctivos_recibidos JSONB NOT NULL DEFAULT '[]'::jsonb,
    deudas_pendientes_proxima_sesion JSONB NOT NULL DEFAULT '[]'::jsonb,
    resumen_lecciones TEXT,
    sprint_activo TEXT,
    kernel_version TEXT,
    embrion_ultimo_latido TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),

    -- Pre-flight obligatorio: si hay commits productivos sin pre-flight,
    -- es violacion sistemica de F11 canonizado por Cowork mismo.
    CONSTRAINT pre_flight_obligatorio CHECK (
        pre_flight_ejecutado = TRUE OR commits_productivos = 0
    )
);

-- Indice para Pre-flight Memento extendido: leer ultima sesion rapido.
CREATE INDEX IF NOT EXISTS idx_cowork_sesiones_fecha_inicio
    ON public.cowork_sesiones (fecha_inicio DESC);

-- Indice para queries de salud por estado (sesiones abiertas vs cerradas).
CREATE INDEX IF NOT EXISTS idx_cowork_sesiones_fecha_fin_null
    ON public.cowork_sesiones (fecha_fin)
    WHERE fecha_fin IS NULL;

-- Trigger para updated_at automatico.
CREATE OR REPLACE FUNCTION public.cowork_sesiones_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_cowork_sesiones_updated_at ON public.cowork_sesiones;
CREATE TRIGGER trg_cowork_sesiones_updated_at
    BEFORE UPDATE ON public.cowork_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION public.cowork_sesiones_set_updated_at();

-- =============================================================================
-- RLS canon DSC-S-006: cerrado por defecto, solo service_role.
-- =============================================================================
ALTER TABLE public.cowork_sesiones ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS service_role_only ON public.cowork_sesiones;
CREATE POLICY service_role_only ON public.cowork_sesiones
    FOR ALL
    TO public
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY service_role_only ON public.cowork_sesiones IS
    'Sprint COWORK-RUNTIME-001 / T3 MAGNA. Solo el backend operativo (service_role) escribe y lee. Cierra brecha M3 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.';

COMMENT ON TABLE public.cowork_sesiones IS
    'Memoria persistente entre sesiones Cowork. Pre-flight Memento extendido lee ultima fila al inicio de cada sesion para curar sindrome de Dory operacional.';

COMMIT;

-- =============================================================================
-- Rollback (manual):
--   BEGIN;
--   DROP TRIGGER IF EXISTS trg_cowork_sesiones_updated_at ON public.cowork_sesiones;
--   DROP FUNCTION IF EXISTS public.cowork_sesiones_set_updated_at();
--   DROP TABLE IF EXISTS public.cowork_sesiones CASCADE;
--   COMMIT;
-- =============================================================================
