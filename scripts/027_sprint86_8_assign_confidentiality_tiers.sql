-- ============================================================================
-- Sprint 86.8 · Asignación Inicial Conservadora de confidentiality_tier
-- ============================================================================
-- Autor: Hilo Manus Catastro (Hilo B)
-- Fecha: 2026-05-05
-- Spec: bridge/sprint_86_8_preinvestigation/spec_catastro_confidentiality_tier.md sec Decisión 3
--
-- LÓGICA DE ASIGNACIÓN
--   1. Open weights (Llama, Mistral, Phi, Qwen, DeepSeek-Coder local)
--      → local_only (corre on-device con quantización conocida)
--
--   2. Modelos cloud con confidential computing confirmado
--      (Anthropic Confidential Compute / AWS Nitro Enclaves)
--      → tee_capable
--
--   3. Modelos cloud comerciales con NDA y SOC2/ISO27001
--      (Claude API, GPT-*, Gemini, Cohere, Mistral hosted)
--      → cloud_anonymized_ok
--
--   4. Resto (default por la migration 027): cloud_only
--
-- IDEMPOTENTE: solo actualiza modelos que NO tengan ya un tier promovido.
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- TIER 1 · local_only — open-weights con quantización local conocida
-- ----------------------------------------------------------------------------
UPDATE catastro_modelos
SET confidentiality_tier = 'local_only'
WHERE confidentiality_tier = 'cloud_only'  -- solo si está en default
  AND open_weights = true
  AND (
      -- Llama family
      id LIKE 'llama-%'
      OR id LIKE 'meta-llama-%'
      -- Mistral open-weights (Mistral 7B, Mixtral) — cloud-hosted Mistral va aparte
      OR id LIKE 'mistral-7b%'
      OR id LIKE 'mistral-nemo%'
      OR id LIKE 'mixtral-%'
      -- Microsoft Phi
      OR id LIKE 'phi-%'
      -- Qwen open-weights
      OR id LIKE 'qwen-%'
      OR id LIKE 'qwen2-%'
      OR id LIKE 'qwen3-%'
      -- DeepSeek open-weights local
      OR id LIKE 'deepseek-coder-%'
      OR id LIKE 'deepseek-v3-base%'
      -- Gemma (Google open-weights)
      OR id LIKE 'gemma-%'
      OR id LIKE 'gemma2-%'
      -- StableLM, Falcon, Yi, otros
      OR id LIKE 'stablelm-%'
      OR id LIKE 'falcon-%'
      OR id LIKE 'yi-%'
  );

-- ----------------------------------------------------------------------------
-- TIER 2 · tee_capable — modelos con confidential computing confirmado
-- ----------------------------------------------------------------------------
-- Anthropic Confidential Compute aplica solo a modelos en su API enterprise
-- AWS Bedrock con Nitro Enclaves aplica a Claude/Llama hosted en Bedrock
-- Por ahora dejamos esta lista vacía y se promueve manualmente con evidencia.
-- Comentamos cualquier modelo aquí cuando confirmemos elegibilidad TEE.
--
-- UPDATE catastro_modelos
-- SET confidentiality_tier = 'tee_capable'
-- WHERE confidentiality_tier = 'cloud_only'
--   AND id IN (
--       -- 'claude-opus-4-tee',  -- pendiente confirmar
--       -- 'llama-3-3-70b-bedrock-nitro',  -- pendiente confirmar
--   );

-- ----------------------------------------------------------------------------
-- TIER 3 · cloud_anonymized_ok — cloud LLMs comerciales con NDA + SOC2
-- ----------------------------------------------------------------------------
UPDATE catastro_modelos
SET confidentiality_tier = 'cloud_anonymized_ok'
WHERE confidentiality_tier = 'cloud_only'  -- solo si está en default
  AND open_weights = false
  AND (
      -- Anthropic
      proveedor = 'anthropic'
      OR id LIKE 'claude-%'
      -- OpenAI
      OR proveedor = 'openai'
      OR id LIKE 'gpt-%'
      OR id LIKE 'o1-%'
      OR id LIKE 'o3-%'
      OR id LIKE 'o4-%'
      OR id LIKE 'chatgpt-%'
      -- Google
      OR proveedor = 'google'
      OR id LIKE 'gemini-%'
      OR id LIKE 'palm-%'
      -- Cohere
      OR proveedor = 'cohere'
      OR id LIKE 'command-%'
      -- Mistral hosted (no open-weights)
      OR (proveedor = 'mistral' AND open_weights = false)
      -- DeepSeek API (no abierto)
      OR (proveedor = 'deepseek' AND open_weights = false)
      OR id = 'deepseek-r1'
      OR id = 'deepseek-v3'
      -- xAI
      OR proveedor = 'xai'
      OR id LIKE 'grok-%'
  );

-- ----------------------------------------------------------------------------
-- TIER 4 · cloud_only — default (no se actualiza, ya está)
-- ----------------------------------------------------------------------------
-- Modelos restantes (proveedores no auditados, modelos experimentales en
-- HuggingFace inference, etc.) quedan en cloud_only hasta verificación.

COMMIT;

-- ============================================================================
-- Auditoría post-asignación
-- ============================================================================
-- SELECT confidentiality_tier, COUNT(*)
--   FROM catastro_modelos
--  GROUP BY confidentiality_tier
--  ORDER BY confidentiality_tier;
--
-- Distribución esperada (orden conservador):
--   cloud_only            -> resto (modelos experimentales, no auditados)
--   cloud_anonymized_ok   -> mayoría (Anthropic + OpenAI + Google + xAI)
--   tee_capable           -> 0 inicialmente (promoción manual con evidencia)
--   local_only            -> open-weights con quant local conocida
-- ============================================================================
