-- Migration 0022: 3 vistas semánticas DSC-G-007.1
-- Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc)
-- Spec: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_v2_OPCION_B_KICKOFF_2026_05_12.md §T2
-- Mapping documentado verbatim: bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md §3, §4, §5
--
-- Honra el contrato DSC-G-007.1 (4 catastros canónicos) sin duplicar tablas:
--   - catastro_modelos_llm   → sobre catastro_modelos (41 rows, 41 cols)
--   - catastro_agentes_2026  → sobre catastro_agentes (98 rows, 46 cols)
--   - catastro_herramientas_ai → UNION ALL sobre catastro_vision_generativa + tool_registry
--
-- Vistas son CREATE OR REPLACE (idempotentes).
-- Vistas no soportan RLS nativo; protegidas vía REVOKE PUBLIC + GRANT service_role
-- según doctrina §7 Regla Dura sección "vistas materializadas" del repo.

-- ===================================================================
-- VISTA 1: catastro_modelos_llm → catastro_modelos
-- ===================================================================
CREATE OR REPLACE VIEW public.catastro_modelos_llm AS
SELECT
  id                                                          AS key,
  nombre                                                      AS name,
  proveedor                                                   AS provider,
  api_endpoint                                                AS endpoint,
  (capacidades_tecnicas->>'max_tokens')::int                  AS max_tokens,
  COALESCE(precio_input_per_million / 1000.0, NULL)::numeric  AS cost_per_1k_input,
  COALESCE(precio_output_per_million / 1000.0, NULL)::numeric AS cost_per_1k_output,
  (estado = 'active')                                         AS active,
  data_extra                                                  AS metadata
FROM public.catastro_modelos;

COMMENT ON VIEW public.catastro_modelos_llm IS
  'DSC-G-007.1 catastro canónico #1 (LLMs). Vista semántica sobre catastro_modelos. Renames + cast: id→key, nombre→name, proveedor→provider, api_endpoint→endpoint, max_tokens extraído de capacidades_tecnicas jsonb, precio_*_per_million / 1000 → cost_per_1k_*, estado=active → active boolean. Sprint 89 v2 Opción B.';

-- ===================================================================
-- VISTA 2: catastro_agentes_2026 → catastro_agentes
-- ===================================================================
CREATE OR REPLACE VIEW public.catastro_agentes_2026 AS
SELECT
  id                                                AS key,
  nombre                                            AS name,
  COALESCE(data_extra->>'version', NULL)            AS version,
  proveedor                                         AS owner_org,
  COALESCE(data_extra->>'biblia_path', NULL)        AS biblia_path,
  subcapacidades                                    AS capability_tags,
  multi_step_capable                                AS has_native_loop,
  (COALESCE(array_length(tools_nativas, 1), 0) > 0) AS has_native_tools,
  (estado = 'active')                               AS active,
  data_extra                                        AS metadata
FROM public.catastro_agentes;

COMMENT ON VIEW public.catastro_agentes_2026 IS
  'DSC-G-007.1 catastro canónico #2 (Agentes 2026 de las 21 biblias). Vista semántica sobre catastro_agentes. Renames + jsonb extraction: id→key, nombre→name, proveedor→owner_org, version y biblia_path extraídos de data_extra (NULL si no presentes - Catastro-A puede enriquecer con UPDATEs), subcapacidades→capability_tags, multi_step_capable→has_native_loop (proxy semántico), tools_nativas array→has_native_tools boolean, estado=active→active. Sprint 89 v2 Opción B.';

-- ===================================================================
-- VISTA 3: catastro_herramientas_ai → catastro_vision_generativa + tool_registry
-- ===================================================================
CREATE OR REPLACE VIEW public.catastro_herramientas_ai AS
SELECT
  id                          AS key,
  nombre                      AS name,
  'vision_generativa'::text   AS category,
  url_oficial                 AS endpoint,
  CASE
    WHEN api_disponible THEN 'api_key'::text
    ELSE 'none'::text
  END                         AS auth_type,
  NULL::text                  AS rate_limit,
  NULL::numeric               AS cost_per_call,
  ARRAY[]::text[]             AS fallback_tools,
  (estado = 'active')         AS active,
  data_extra                  AS metadata
FROM public.catastro_vision_generativa

UNION ALL

SELECT
  id::text                              AS key,
  tool_name                             AS name,
  category                              AS category,
  COALESCE(metadata->>'endpoint', NULL) AS endpoint,
  CASE
    WHEN secret_env_var IS NOT NULL THEN 'api_key'::text
    ELSE 'none'::text
  END                                   AS auth_type,
  (metadata->>'rate_limit')             AS rate_limit,
  NULL::numeric                         AS cost_per_call,
  ARRAY[]::text[]                       AS fallback_tools,
  is_active                             AS active,
  metadata                              AS metadata
FROM public.tool_registry;

COMMENT ON VIEW public.catastro_herramientas_ai IS
  'DSC-G-007.1 catastro canónico #3 (Herramientas AI verticales). UNION ALL sobre catastro_vision_generativa (38 rows, vision generativa) + tool_registry (tools genéricas con secrets/HITL). Cast uuid→text en tool_registry. category fija a vision_generativa para una rama; usa category real de tool_registry para la otra. auth_type derivado de api_disponible (vision) o secret_env_var IS NOT NULL (tool_registry). Sprint 89 v2 Opción B.';

-- ===================================================================
-- Protección RLS-equivalente para las 3 vistas
-- Doctrina §7 (vistas no soportan RLS nativo): REVOKE PUBLIC + GRANT service_role
-- ===================================================================
REVOKE ALL ON public.catastro_modelos_llm FROM PUBLIC, anon, authenticated;
GRANT SELECT ON public.catastro_modelos_llm TO service_role;

REVOKE ALL ON public.catastro_agentes_2026 FROM PUBLIC, anon, authenticated;
GRANT SELECT ON public.catastro_agentes_2026 TO service_role;

REVOKE ALL ON public.catastro_herramientas_ai FROM PUBLIC, anon, authenticated;
GRANT SELECT ON public.catastro_herramientas_ai TO service_role;

-- ===================================================================
-- Cleanup: borrar vistas con sufijo _view del primer intento (idempotente)
-- ===================================================================
DROP VIEW IF EXISTS public.catastro_modelos_llm_view CASCADE;
DROP VIEW IF EXISTS public.catastro_agentes_2026_view CASCADE;
DROP VIEW IF EXISTS public.catastro_herramientas_ai_view CASCADE;
