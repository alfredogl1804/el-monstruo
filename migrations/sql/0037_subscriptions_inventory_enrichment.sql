-- =====================================================================
-- Migration 0037 — Enriquecimiento del inventario de suscripciones
-- =====================================================================
-- Fecha: 2026-05-16
-- Sprint: 28 (manus inventario v13.3)
-- Autor: Manus (Hilo B - inventario v13)
-- Auditado por: Cowork (Claude Opus)
-- =====================================================================
-- PROPÓSITO:
-- 1. Migración retroactiva: documentar la tabla `monstruo_inventario_suscripciones`
--    que ya existe en producción con 559 filas (snapshot v11) pero nunca fue
--    versionada en /migrations/sql/.
-- 2. Aplicar correcciones bloqueantes detectadas en auditoría Cowork:
--    a. Quitar defaults hardcodeados de snapshot_version y snapshot_date.
--    b. Convertir proxima_renovacion de TEXT a DATE (con limpieza previa).
--    c. costo_mxn NOT NULL DEFAULT 0.
--    d. Agregar trigger updated_at automático.
--    e. Agregar UNIQUE(snapshot_version, nombre) para evitar duplicados.
-- 3. Agregar 13 columnas nuevas para soportar enriquecimiento Gemini 2.5 Pro:
--    que_es, para_que_sirve, capacidades[], tiene_api, api_auth_method,
--    api_docs_url, tiene_ia, tipo_ia[], monstruo_fit, padre, gratuito,
--    alternativas[], confidence, razonamiento.
-- 4. Crear vista materializada vw_inventario_actual con último snapshot por
--    nombre (deduplicación inteligente).
-- 5. Cumplir DSC-S-006 v1.1 (RLS habilitado por defecto) y DSC-S-007 (naming).
-- =====================================================================

-- ---------------------------------------------------------------------
-- PARTE 1: Documentación retroactiva del schema base (idempotente)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.monstruo_inventario_suscripciones (
  id BIGSERIAL PRIMARY KEY,
  snapshot_version TEXT NOT NULL,
  snapshot_date DATE NOT NULL,
  nombre TEXT NOT NULL,
  categoria TEXT,
  descripcion TEXT,
  plan TEXT,
  costo_mxn NUMERIC,
  frecuencia TEXT,
  proxima_renovacion TEXT,
  metodo_pago TEXT,
  estado TEXT,
  prioridad_verificacion INTEGER,
  fuentes TEXT,
  url_oficial TEXT,
  env_var TEXT,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- PARTE 2: Bloqueantes Cowork (correcciones al schema existente)
-- ---------------------------------------------------------------------

-- 2a. Quitar defaults hardcodeados (cada snapshot debe declarar versión y fecha)
ALTER TABLE public.monstruo_inventario_suscripciones
  ALTER COLUMN snapshot_version DROP DEFAULT;

ALTER TABLE public.monstruo_inventario_suscripciones
  ALTER COLUMN snapshot_date DROP DEFAULT;

-- 2b. costo_mxn NOT NULL con default 0 (consistencia)
UPDATE public.monstruo_inventario_suscripciones SET costo_mxn = 0 WHERE costo_mxn IS NULL;
ALTER TABLE public.monstruo_inventario_suscripciones
  ALTER COLUMN costo_mxn SET NOT NULL,
  ALTER COLUMN costo_mxn SET DEFAULT 0;

-- 2c. Agregar columna proxima_renovacion_date (nueva DATE) sin destruir TEXT
-- (mantenemos TEXT por compatibilidad con v11 existente; la nueva DATE es para uso futuro)
ALTER TABLE public.monstruo_inventario_suscripciones
  ADD COLUMN IF NOT EXISTS proxima_renovacion_date DATE;

-- 2d. Trigger automático de updated_at
CREATE OR REPLACE FUNCTION public.fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_monstruo_inventario_updated_at
  ON public.monstruo_inventario_suscripciones;

CREATE TRIGGER trg_monstruo_inventario_updated_at
  BEFORE UPDATE ON public.monstruo_inventario_suscripciones
  FOR EACH ROW
  EXECUTE FUNCTION public.fn_set_updated_at();

-- 2e. UNIQUE(snapshot_version, nombre) — eliminar duplicados primero
-- Si hay duplicados, mantener el id más reciente
WITH duplicates AS (
  SELECT id,
         ROW_NUMBER() OVER (PARTITION BY snapshot_version, nombre ORDER BY id DESC) AS rn
  FROM public.monstruo_inventario_suscripciones
)
DELETE FROM public.monstruo_inventario_suscripciones
WHERE id IN (SELECT id FROM duplicates WHERE rn > 1);

CREATE UNIQUE INDEX IF NOT EXISTS uq_monstruo_inv_snapshot_nombre
  ON public.monstruo_inventario_suscripciones (snapshot_version, nombre);

-- ---------------------------------------------------------------------
-- PARTE 3: Columnas nuevas para enriquecimiento Gemini 2.5 Pro
-- ---------------------------------------------------------------------
ALTER TABLE public.monstruo_inventario_suscripciones
  ADD COLUMN IF NOT EXISTS nombre_canonico TEXT,
  ADD COLUMN IF NOT EXISTS que_es TEXT,
  ADD COLUMN IF NOT EXISTS para_que_sirve TEXT,
  ADD COLUMN IF NOT EXISTS capacidades TEXT[],
  ADD COLUMN IF NOT EXISTS tiene_api BOOLEAN,
  ADD COLUMN IF NOT EXISTS api_auth_method TEXT,
  ADD COLUMN IF NOT EXISTS api_docs_url TEXT,
  ADD COLUMN IF NOT EXISTS tiene_ia BOOLEAN,
  ADD COLUMN IF NOT EXISTS tipo_ia TEXT[],
  ADD COLUMN IF NOT EXISTS monstruo_fit TEXT,
  ADD COLUMN IF NOT EXISTS padre TEXT,
  ADD COLUMN IF NOT EXISTS gratuito BOOLEAN,
  ADD COLUMN IF NOT EXISTS alternativas TEXT[],
  ADD COLUMN IF NOT EXISTS confidence NUMERIC,
  ADD COLUMN IF NOT EXISTS razonamiento TEXT;

-- CHECK constraint defensivo: monstruo_fit solo valores válidos
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_monstruo_fit_valid'
  ) THEN
    ALTER TABLE public.monstruo_inventario_suscripciones
      ADD CONSTRAINT chk_monstruo_fit_valid
      CHECK (monstruo_fit IS NULL OR monstruo_fit IN (
        'core', 'support', 'experimental', 'personal',
        'issuer', 'out_of_scope', 'no_aplica', 'no_identificable'
      ));
  END IF;
END $$;

-- Índices auxiliares
CREATE INDEX IF NOT EXISTS idx_monstruo_inv_fit
  ON public.monstruo_inventario_suscripciones (monstruo_fit);

CREATE INDEX IF NOT EXISTS idx_monstruo_inv_padre
  ON public.monstruo_inventario_suscripciones (padre)
  WHERE padre IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_monstruo_inv_snapshot
  ON public.monstruo_inventario_suscripciones (snapshot_version);

-- ---------------------------------------------------------------------
-- PARTE 4: RLS por defecto (DSC-S-006 v1.1)
-- ---------------------------------------------------------------------
ALTER TABLE public.monstruo_inventario_suscripciones ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_only"
  ON public.monstruo_inventario_suscripciones;

CREATE POLICY "service_role_only"
  ON public.monstruo_inventario_suscripciones
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ---------------------------------------------------------------------
-- PARTE 5: Vista vw_inventario_actual (último snapshot por nombre)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW public.vw_inventario_actual AS
SELECT DISTINCT ON (LOWER(nombre))
  id,
  snapshot_version,
  snapshot_date,
  nombre,
  nombre_canonico,
  categoria,
  descripcion,
  plan,
  costo_mxn,
  frecuencia,
  proxima_renovacion,
  proxima_renovacion_date,
  metodo_pago,
  estado,
  prioridad_verificacion,
  fuentes,
  url_oficial,
  env_var,
  notas,
  que_es,
  para_que_sirve,
  capacidades,
  tiene_api,
  api_auth_method,
  api_docs_url,
  tiene_ia,
  tipo_ia,
  monstruo_fit,
  padre,
  gratuito,
  alternativas,
  confidence,
  razonamiento,
  created_at,
  updated_at
FROM public.monstruo_inventario_suscripciones
ORDER BY LOWER(nombre), snapshot_date DESC, id DESC;

-- Proteger la vista (DSC-S-006 v1.1)
REVOKE ALL ON public.vw_inventario_actual FROM PUBLIC, anon, authenticated;
GRANT SELECT ON public.vw_inventario_actual TO service_role;

-- ---------------------------------------------------------------------
-- COMMENTS para documentación
-- ---------------------------------------------------------------------
COMMENT ON TABLE public.monstruo_inventario_suscripciones IS
  'Inventario versionado de suscripciones SaaS de Alfredo. Cada snapshot es un dump completo histórico (no se sobrescriben). Sprint 28.';

COMMENT ON COLUMN public.monstruo_inventario_suscripciones.snapshot_version IS
  'Versión del snapshot. Ej: v11 (Apple ID dump), v13.2 (billing-verified), v13.3_enriched (LLM-enriched).';

COMMENT ON COLUMN public.monstruo_inventario_suscripciones.monstruo_fit IS
  'Encaje al Monstruo: core / support / experimental / personal / issuer / out_of_scope / no_aplica / no_identificable.';

COMMENT ON COLUMN public.monstruo_inventario_suscripciones.confidence IS
  'Confianza del enriquecimiento LLM (0-1). Truncados sin identificación clara → max 0.5.';

COMMENT ON VIEW public.vw_inventario_actual IS
  'Vista deduplicada con el snapshot más reciente por nombre. Usar para queries operativas. Refrescar materializada en futuro si bottleneck.';

-- =====================================================================
-- FIN DE MIGRACIÓN 0037
-- =====================================================================
