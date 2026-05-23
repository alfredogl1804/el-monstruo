-- ===================================================================
-- Migration 0051: H5 fix — vista catastro_modelos_llm refleja realidad operativa
-- ===================================================================
-- Sprint: H5 (Auditoría 5 Pasadas 2026-05-16, hallazgo crítico router LLM)
-- Origen: bug histórico Sprint 89 v2 Opción B (migration 0022_catastro_vistas_dsc_g_007_1.sql)
-- Autor: Manus E2 (Hilo Catastros & Coordinación La Forja)
-- Audit: Cowork T2-A — DSC-G-008 v4 + DSC-G-013 v0.1 Coherence Gate Nivel A
-- Fecha: 2026-05-18
--
-- HALLAZGO MAGNO (vía DSC-G-013 Coherence Gate Nivel A):
--   La migration 0022 escribió `(estado = 'active') AS active` pero el CHECK constraint
--   `catastro_modelos_estado_check` NUNCA permitió 'active' en el enum. Valores válidos
--   son: 'production', 'beta', 'open-source', 'deprecated', 'alpha', 'preview'.
--   Resultado: vista nació rota → 41 modelos en `production` invisibles para router LLM.
--   Router cae a fallback hardcoded en cada request.
--
-- TRIPLE DRIFT DETECTADO:
--   1. Vista ↔ CHECK constraint (filtro por valor imposible)
--   2. Realidad operativa ↔ doctrina (41 prod operativos pero invisibles)
--   3. Planning ↔ reality (Manus E2 propuso UPDATE 'active' sin verificar CHECK; Coherence
--      Gate Nivel A bloqueó pre-acción → casi otro F#15 reincidente)
--
-- FIX: redefinir vista para honrar realidad operativa.
--   `estado IN ('active', 'production')` → cubre ambos casos:
--     - 'production' = 41 modelos actuales operativos
--     - 'active' = futura compatibilidad si CHECK constraint se amplía
--
-- IDEMPOTENCIA: CREATE OR REPLACE — re-correr seguro.
-- ATOMICIDAD: BEGIN/COMMIT.
-- REVERSIBILIDAD: 100% via CREATE OR REPLACE con definición anterior:
--   CREATE OR REPLACE VIEW public.catastro_modelos_llm AS
--   SELECT ..., (estado = 'active') AS active, ... FROM public.catastro_modelos;
-- DSC-S-006 RLS: vistas heredan grants de tabla padre. REVOKE/GRANT explícitos en
--   migration 0022 (líneas no tocadas aquí, siguen vigentes).
-- DSC-G-008 v2 scope: 1 archivo, 1 vista CREATE OR REPLACE, 0 datos modificados.
-- ===================================================================

BEGIN;

CREATE OR REPLACE VIEW public.catastro_modelos_llm AS
SELECT
  id                                                          AS key,
  nombre                                                      AS name,
  proveedor                                                   AS provider,
  api_endpoint                                                AS endpoint,
  (capacidades_tecnicas->>'max_tokens')::int                  AS max_tokens,
  COALESCE(precio_input_per_million / 1000.0, NULL)::numeric  AS cost_per_1k_input,
  COALESCE(precio_output_per_million / 1000.0, NULL)::numeric AS cost_per_1k_output,
  (estado IN ('active', 'production'))                        AS active,  -- ← H5 fix
  data_extra                                                  AS metadata
FROM public.catastro_modelos;

COMMENT ON VIEW public.catastro_modelos_llm IS
  'DSC-G-007.1 catastro canónico #1 (LLMs). Vista semántica sobre catastro_modelos. '
  'Sprint 89 v2 Opción B (origen) + H5 fix 2026-05-18: estado=production tratado '
  'como active (bug histórico — `active` nunca existió en CHECK constraint enum). '
  'Reversible 100% via CREATE OR REPLACE con definición anterior. '
  'Cowork T2-A audit DSC-G-008 v4 + DSC-G-013 v0.1 Coherence Gate Nivel A verificado.';

COMMIT;

-- ===================================================================
-- SMOKE TESTS POST-APPLY (esperados):
-- ===================================================================
-- 1) SELECT COUNT(*) FROM catastro_modelos_llm WHERE active = true;
--    Esperado: 41 (todos los modelos en estado='production' ahora visibles)
--
-- 2) SELECT COUNT(*) FROM catastro_modelos_llm WHERE active = false;
--    Esperado: 0 (no hay modelos 'beta', 'open-source', 'deprecated', 'alpha', 'preview' actualmente)
--
-- 3) SELECT key, name, provider, active FROM catastro_modelos_llm
--    WHERE provider IN ('openai', 'anthropic', 'google') ORDER BY name LIMIT 10;
--    Esperado: 10 filas con active=true (gpt-5.5, claude-opus-4-7, gemini-3-pro, etc.)
--
-- 4) SELECT COUNT(*) FROM catastro_modelos_llm cml
--    JOIN catastro_modelos cm ON cml.key = cm.id
--    WHERE cml.active != (cm.estado IN ('active', 'production'));
--    Esperado: 0 (consistencia binaria vista↔tabla)
-- ===================================================================
