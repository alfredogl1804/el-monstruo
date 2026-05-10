-- ============================================================================
-- Migration 038 - Sprint 88.2 - Recalibración tronos según consenso 4 sabios
-- ============================================================================
-- Sabios: Gemini 3.1 Pro (5/10), Claude Opus 4.7 (6.5/10), GPT-5.5 Pro (6.5/10),
--         Perplexity (7.5/10 - peso reforzado por Alfredo)
--
-- Paquete aprobado por Alfredo:
--   1. Crear dominio agentes_generalistas_autonomos + Manus como trono
--   2. Trono agentes_desarrollo: Manus -> Devin
--   3. Trono agentes_branding_diseno: Looka -> Canva AI
--   4. Crear dominio agentes_seguridad + 5 productos seed (trono Lakera)
--   5. Crear dominio agentes_observabilidad_evals + 5 productos seed (trono Braintrust)
--   6. REFRESH vista materializada catastro_tronos_agentes
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 0. Ampliar CHECK bonus_curador rango 0-50
-- ----------------------------------------------------------------------------
ALTER TABLE catastro_agentes
  DROP CONSTRAINT IF EXISTS catastro_agentes_bonus_curador_check;

ALTER TABLE catastro_agentes
  ADD CONSTRAINT catastro_agentes_bonus_curador_check
  CHECK (bonus_curador >= 0 AND bonus_curador <= 50);

-- ----------------------------------------------------------------------------
-- 1. Ampliar CHECK dominio para 3 dominios nuevos
-- ----------------------------------------------------------------------------
ALTER TABLE catastro_agentes
  DROP CONSTRAINT IF EXISTS chk_dominio_valido;

ALTER TABLE catastro_agentes
  ADD CONSTRAINT chk_dominio_valido CHECK (dominio IN (
    'agentes_desarrollo',
    'agentes_vibe_coding',
    'agentes_multi_swarm',
    'agentes_investigacion',
    'agentes_ejecutores',
    'agentes_creacion_audiovisual',
    'agentes_branding_diseno',
    'agentes_marketing_ventas',
    'interfaces_usuario',
    'agentes_generalistas_autonomos',
    'agentes_seguridad',
    'agentes_observabilidad_evals'
  ));

-- ----------------------------------------------------------------------------
-- 2. Mover Manus -> agentes_generalistas_autonomos + bonus 10
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET dominio = 'agentes_generalistas_autonomos',
       bonus_curador = 10,
       bonus_curador_razon = 'Trono agentes_generalistas_autonomos según consenso 4/4 sabios. Manus = action engine horizontal end-to-end (frontend/backend/db/auth/Stripe/deploy + escritorio + browser). NO es trono de desarrollo de software técnico (eso es Devin/Claude Code), pero ES trono indiscutido de agente generalista autónomo soberano para Monstruo.',
       updated_at = NOW()
 WHERE id = 'manus';

-- ----------------------------------------------------------------------------
-- 3. INSERT acompañantes en agentes_generalistas_autonomos
-- ----------------------------------------------------------------------------
INSERT INTO catastro_agentes (
  id, nombre, proveedor, macroarea, dominio,
  llm_base_id,
  tiene_sandbox, acceso_filesystem, acceso_internet,
  multi_step_capable, multi_swarm_capable,
  persistencia_memoria, costo_por_uso_tipico,
  estado, open_weights,
  fuentes_evidencia, quorum_alcanzado, confidence,
  validacion_adversarial, data_extra,
  schema_version, ultima_validacion,
  tier_seed, bonus_curador
) VALUES
  ('chatgpt-agent', 'ChatGPT Agent', 'OpenAI', 'agentes', 'agentes_generalistas_autonomos',
    'gpt-5-5',
    true, true, true, true, false,
    'persistent', 'medio',
    'production', false,
    '[{"fuente": "openai.com/agent", "fecha": "2026-04"}]'::jsonb, false, 0.80,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "ChatGPT Agent es generalista autónomo end-to-end con browser+codigo+terminal"}'::jsonb,
    '{"capacidades": ["visual_browser", "code_interpreter", "terminal", "apps", "spreadsheets"]}'::jsonb,
    1, NOW(),
    1, 0
  ),
  ('genspark', 'Genspark', 'MainFunc', 'agentes', 'agentes_generalistas_autonomos',
    NULL,
    true, false, true, true, false,
    'session', 'gratis',
    'production', false,
    '[{"fuente": "genspark.ai", "fecha": "2026-04"}]'::jsonb, false, 0.75,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "Genspark Super Agent + AI Slides + AI Sheets + AI phone calls"}'::jsonb,
    '{"capacidades": ["sparkpages", "agentic_search", "deep_research", "ai_phone_calls"]}'::jsonb,
    1, NOW(),
    1, 0
  ),
  ('comet-browser-perplexity', 'Comet Browser', 'Perplexity', 'agentes', 'agentes_generalistas_autonomos',
    'perplexity-sonar-pro',
    true, false, true, true, false,
    'session', 'gratis',
    'production', false,
    '[{"fuente": "perplexity.ai/comet", "fecha": "2026-05"}]'::jsonb, false, 0.78,
    '{"sabios": ["perplexity"], "consenso": "Comet Browser = agente nativo de navegador con Sonar dentro"}'::jsonb,
    '{"capacidades": ["agentic_browser", "tab_management", "web_navigation"]}'::jsonb,
    1, NOW(),
    1, 0
  )
ON CONFLICT (id) DO UPDATE SET
  dominio = EXCLUDED.dominio,
  data_extra = EXCLUDED.data_extra,
  updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 4. Devin trono agentes_desarrollo: bonus +25
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET bonus_curador = 25,
       bonus_curador_razon = 'Trono agentes_desarrollo según consenso 3/4 sabios (Perplexity dominante). Devin = ingeniería de software autónomo sobre repos reales: orquesta Devins paralelos, VMs aisladas, PRs continuos, MCP, autofix con CI. Supera a Claude Code/Cursor/Codex en autonomía end-to-end de desarrollo.',
       updated_at = NOW()
 WHERE id = 'devin';

-- ----------------------------------------------------------------------------
-- 5. INSERT Canva AI + remover bonus de Looka
-- ----------------------------------------------------------------------------
INSERT INTO catastro_agentes (
  id, nombre, proveedor, macroarea, dominio,
  llm_base_id,
  tiene_sandbox, acceso_filesystem, acceso_internet,
  multi_step_capable, multi_swarm_capable,
  persistencia_memoria, costo_por_uso_tipico,
  estado, open_weights,
  fuentes_evidencia, quorum_alcanzado, confidence,
  validacion_adversarial, data_extra,
  schema_version, ultima_validacion,
  tier_seed, bonus_curador, bonus_curador_razon
) VALUES
  ('canva-ai', 'Canva AI / Brand Kit', 'Canva', 'agentes', 'agentes_branding_diseno',
    NULL,
    false, false, true, true, false,
    'persistent', 'medio',
    'production', false,
    '[{"fuente": "canva.com/canva-ai", "fecha": "2026-05"}, {"fuente": "canva.com/pro/brand-kit", "fecha": "2026-05"}, {"fuente": "MCP server release Apr 2026"}]'::jsonb,
    true, 0.95,
    '{"sabios": ["gemini-3.1-pro", "claude-opus-4.7", "gpt-5.5-pro", "perplexity"], "consenso": "4/4 ACUERDO: Canva AI 2.0 + Brand Kit es trono branding por amplitud (logos+identidad+assets+ecosistema)"}'::jsonb,
    '{"capacidades": ["brand_kit", "ai_design", "magic_studio", "deep_research_integration", "mcp_server"]}'::jsonb,
    1, NOW(),
    1, 15, 'Trono agentes_branding_diseno según consenso 4/4 sabios. Canva AI 2.0 + Brand Kit centraliza logos, colores, fuentes, assets, plantillas, multi-marcas. MCP server desde Apr 2026. Supera a Looka por amplitud y a Adobe Firefly por accesibilidad.'
  )
ON CONFLICT (id) DO UPDATE SET
  bonus_curador = EXCLUDED.bonus_curador,
  bonus_curador_razon = EXCLUDED.bonus_curador_razon,
  updated_at = NOW();

UPDATE catastro_agentes
   SET bonus_curador = 0,
       bonus_curador_razon = 'Bonus removido Sprint 88.2: cedió trono a Canva AI por consenso 4/4 sabios. Looka mantiene Tier 1 como líder específico de logos.',
       updated_at = NOW()
 WHERE id = 'looka';

-- ----------------------------------------------------------------------------
-- 6. CREAR DOMINIO agentes_seguridad + 5 productos seed
-- ----------------------------------------------------------------------------
INSERT INTO catastro_agentes (
  id, nombre, proveedor, macroarea, dominio,
  llm_base_id,
  tiene_sandbox, acceso_filesystem, acceso_internet,
  multi_step_capable, multi_swarm_capable,
  persistencia_memoria, costo_por_uso_tipico,
  estado, open_weights,
  fuentes_evidencia, quorum_alcanzado, confidence,
  validacion_adversarial, data_extra,
  schema_version, ultima_validacion,
  tier_seed, bonus_curador, bonus_curador_razon
) VALUES
  ('lakera', 'Lakera', 'Lakera AI', 'agentes', 'agentes_seguridad',
    NULL, false, false, true, true, false,
    'persistent', 'enterprise', 'production', false,
    '[{"fuente": "lakera.ai/ai-agent-security"}, {"fuente": "Microsoft May 2026 vulnerability disclosure agentic tools"}]'::jsonb,
    true, 0.95,
    '{"sabios": ["gemini-3.1-pro", "claude-opus-4.7", "gpt-5.5-pro", "perplexity"], "consenso": "4/4 OBLIGATORIO Magna: Lakera = AI-native security platform especializada en agentes"}'::jsonb,
    '{"subdominios": ["runtime_prompt_injection_defense", "jailbreak_prevention", "data_exfiltration_protection", "tool_use_abuse"]}'::jsonb,
    1, NOW(),
    1, 20, 'Trono agentes_seguridad según consenso 4/4 sabios (OBLIGATORIO Magna). Lakera = AI-native security platform: prompt-injection defense, jailbreak prevention, GenAI firewall, red-teaming Gandalf masivo, runtime protection, 100+ idiomas, 1M+ tx/aplicación/día. Microsoft May 2026 demostró que prompt-injection en agentes con tools escala a RCE/exfiltración.'
  ),
  ('promptfoo', 'Promptfoo', 'Promptfoo', 'agentes', 'agentes_seguridad',
    NULL, true, true, true, true, false,
    'persistent', 'gratis', 'production', true,
    '[{"fuente": "promptfoo.dev"}]'::jsonb, false, 0.85,
    '{"sabios": ["claude-opus-4.7", "gpt-5.5-pro"], "consenso": "Promptfoo automatiza red-teaming + evals + CI/CD"}'::jsonb,
    '{"subdominios": ["red_teaming_evals", "vulnerability_scanning", "ci_cd_integration"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  ),
  ('garak', 'garak', 'NVIDIA / community', 'agentes', 'agentes_seguridad',
    NULL, true, true, false, true, false,
    'session', 'gratis', 'production', true,
    '[{"fuente": "garak.ai"}]'::jsonb, false, 0.80,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "garak = LLM vulnerability scanner OSS mantenido NVIDIA"}'::jsonb,
    '{"subdominios": ["llm_vulnerability_scanner_open_source"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  ),
  ('snyk-ai-security', 'Snyk AI Security Fabric', 'Snyk', 'agentes', 'agentes_seguridad',
    NULL, false, false, true, true, false,
    'persistent', 'enterprise', 'production', false,
    '[{"fuente": "snyk.io/ai-security-fabric"}]'::jsonb, false, 0.85,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "Snyk = code/supply-chain vulnerability scanning + AI autofix"}'::jsonb,
    '{"subdominios": ["code_vulnerability_scanning", "supply_chain", "ai_autofix"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  ),
  ('semgrep', 'Semgrep / Semgrep Secure 2026', 'Semgrep', 'agentes', 'agentes_seguridad',
    NULL, true, true, true, true, false,
    'persistent', 'medio', 'production', true,
    '[{"fuente": "semgrep.dev/events/semgrep-secure-2026"}]'::jsonb, false, 0.85,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "Semgrep + Semgrep Secure 2026 = code security para vibe coding"}'::jsonb,
    '{"subdominios": ["code_security", "secure_vibe_coding"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  )
ON CONFLICT (id) DO UPDATE SET
  data_extra = EXCLUDED.data_extra,
  updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 7. CREAR DOMINIO agentes_observabilidad_evals + 5 productos seed
-- ----------------------------------------------------------------------------
INSERT INTO catastro_agentes (
  id, nombre, proveedor, macroarea, dominio,
  llm_base_id,
  tiene_sandbox, acceso_filesystem, acceso_internet,
  multi_step_capable, multi_swarm_capable,
  persistencia_memoria, costo_por_uso_tipico,
  estado, open_weights,
  fuentes_evidencia, quorum_alcanzado, confidence,
  validacion_adversarial, data_extra,
  schema_version, ultima_validacion,
  tier_seed, bonus_curador, bonus_curador_razon
) VALUES
  ('braintrust', 'Braintrust', 'Braintrust', 'agentes', 'agentes_observabilidad_evals',
    NULL, false, false, true, true, false,
    'persistent', 'enterprise', 'production', false,
    '[{"fuente": "braintrust.dev"}]'::jsonb, true, 0.90,
    '{"sabios": ["claude-opus-4.7", "gpt-5.5-pro", "perplexity"], "consenso": "3/4: Braintrust = observability platform para construir quality AI"}'::jsonb,
    '{"subdominios": ["agent_observability", "trace_to_eval", "prompt_model_comparison", "quality_gates"]}'::jsonb,
    1, NOW(),
    1, 15, 'Trono agentes_observabilidad_evals según consenso 3/4 sabios. Braintrust convierte production traces en evals, compara prompts/modelos, gates de calidad CI. Para Monstruo: sin trazas + evals los agentes son cajas negras con presupuesto.'
  ),
  ('langsmith', 'LangSmith', 'LangChain', 'agentes', 'agentes_observabilidad_evals',
    NULL, false, false, true, true, false,
    'persistent', 'medio', 'production', false,
    '[{"fuente": "langchain.com/langsmith/observability"}]'::jsonb, false, 0.85,
    '{"sabios": ["gpt-5.5-pro", "perplexity"], "consenso": "LangSmith = trono recomendado si usás LangGraph"}'::jsonb,
    '{"subdominios": ["agent_tracing", "monitoring", "cost_latency_debugging"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  ),
  ('arize-phoenix', 'Phoenix (Arize AI)', 'Arize AI', 'agentes', 'agentes_observabilidad_evals',
    NULL, true, true, true, true, false,
    'persistent', 'gratis', 'production', true,
    '[{"fuente": "phoenix.arize.com"}]'::jsonb, false, 0.85,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "Phoenix = trono soberano OSS para LLM tracing + evaluation"}'::jsonb,
    '{"subdominios": ["llm_tracing_open_source", "agent_evaluation", "self_hosted"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  ),
  ('helicone', 'Helicone', 'Helicone', 'agentes', 'agentes_observabilidad_evals',
    NULL, false, false, true, true, false,
    'session', 'bajo', 'production', true,
    '[{"fuente": "helicone.ai"}]'::jsonb, false, 0.75,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "Helicone = OSS proxy-based observability"}'::jsonb,
    '{"subdominios": ["llm_observability", "logs_caching", "cost_tracking"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  ),
  ('langfuse', 'Langfuse', 'Langfuse', 'agentes', 'agentes_observabilidad_evals',
    NULL, true, true, true, true, false,
    'persistent', 'gratis', 'production', true,
    '[{"fuente": "langfuse.com"}]'::jsonb, false, 0.85,
    '{"sabios": ["gpt-5.5-pro"], "consenso": "Langfuse = OSS líder Apr 2026 LLM observability + evals + prompt mgmt"}'::jsonb,
    '{"subdominios": ["open_source_llm_observability", "tracing_evals_prompt_management"]}'::jsonb,
    1, NOW(),
    1, 0, NULL
  )
ON CONFLICT (id) DO UPDATE SET
  data_extra = EXCLUDED.data_extra,
  updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 8. REFRESH MATERIALIZED VIEW
-- ----------------------------------------------------------------------------
REFRESH MATERIALIZED VIEW catastro_tronos_agentes;

-- ----------------------------------------------------------------------------
-- 9. Verificación
-- ----------------------------------------------------------------------------
DO $$
DECLARE
  v_total INT;
  v_dominios INT;
  v_tronos INT;
BEGIN
  SELECT COUNT(*) INTO v_total FROM catastro_agentes;
  SELECT COUNT(DISTINCT dominio) INTO v_dominios FROM catastro_agentes;
  SELECT COUNT(*) INTO v_tronos FROM catastro_tronos_agentes;
  RAISE NOTICE 'Migracion 038 completa: % agentes, % dominios, % tronos', v_total, v_dominios, v_tronos;
END $$;

COMMIT;
