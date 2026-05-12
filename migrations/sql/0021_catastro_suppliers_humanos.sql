-- Migration 0021: catastro_suppliers_humanos
-- Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc)
-- Spec: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_v2_OPCION_B_KICKOFF_2026_05_12.md §T1
-- Mapping documentado: bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md
--
-- Crea la única tabla del DSC-G-007.1 que NO existe en prod.
-- Los otros 3 catastros canónicos (modelos_llm, agentes_2026, herramientas_ai)
-- se honran como VISTAS en migración 0022 sobre tablas existentes.
--
-- RLS desde nacimiento (DSC-S-006 v1.1): service_role_only.
-- Idempotente (IF NOT EXISTS): seguro para re-aplicar.

CREATE TABLE IF NOT EXISTS public.catastro_suppliers_humanos (
  key         TEXT        PRIMARY KEY,
  name        TEXT        NOT NULL,
  role        TEXT,
  availability TEXT,
  skills      TEXT[],
  contact     JSONB       DEFAULT '{}'::jsonb,
  active      BOOLEAN     DEFAULT true,
  last_active TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

-- RLS doctrina canónica (DSC-S-006 v1.1 + DSC-G-007.1)
ALTER TABLE public.catastro_suppliers_humanos ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS service_role_only ON public.catastro_suppliers_humanos;
CREATE POLICY service_role_only
  ON public.catastro_suppliers_humanos
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Índice opcional para consultas por role/availability
CREATE INDEX IF NOT EXISTS idx_catastro_suppliers_humanos_role
  ON public.catastro_suppliers_humanos (role)
  WHERE active = true;

CREATE INDEX IF NOT EXISTS idx_catastro_suppliers_humanos_availability
  ON public.catastro_suppliers_humanos (availability)
  WHERE active = true;

-- Comentario doctrinal para auditoría
COMMENT ON TABLE public.catastro_suppliers_humanos IS
  'DSC-G-007.1 catastro canónico #4. Suppliers humanos del Monstruo (Alfredo, Manus, Embrión, futuros). Creada por Sprint 89 v2 Opción B 2026-05-12. Tabla nueva (única faltante del DSC). Los otros 3 catastros se honran como VISTAS en migración 0022.';
