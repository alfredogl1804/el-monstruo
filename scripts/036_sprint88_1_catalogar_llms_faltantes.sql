-- ============================================================================
-- Migration 036 — Sprint 88.1: Catalogar 4 LLMs faltantes en catastro_modelos
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.1)
-- Origen: Follow-up DSC-G-007.2 sección "Riesgos asumidos" punto 2
-- Idempotente: ON CONFLICT DO UPDATE
-- Author: Hilo Catastro (Manus)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1) Kimi K2.6 (Moonshot AI) - llm_base de kimi-k2-6-agent-swarm (trono multi_swarm)
-- ----------------------------------------------------------------------------
INSERT INTO catastro_modelos (
    id, nombre, proveedor, macroarea, dominios, subcapacidades,
    estado, tipo, licencia, open_weights, api_endpoint,
    quality_score, cost_efficiency, speed_score, reliability_score,
    brand_fit, sovereignty, velocity, trono_global,
    precio_input_per_million, precio_output_per_million,
    capacidades_tecnicas, fortalezas, debilidades, casos_uso_recomendados_monstruo,
    fuentes_evidencia, quorum_alcanzado, confidence,
    curador_responsable, data_extra, schema_version, validated_by
) VALUES (
    'kimi-k2-6',
    'Kimi K2.6',
    'Moonshot AI',
    'inteligencia',
    ARRAY['llm_frontier', 'agentic_coding'],
    ARRAY['multimodal_native', 'agent_swarm', 'long_horizon_execution', 'tool_calling']::text[],
    'production',
    'open-weights',
    'modified-mit',
    TRUE,
    'https://platform.moonshot.ai/v1',
    78.50,  -- quality_score (top-tier coding/reasoning, SOTA open-weight 2026)
    92.30,  -- cost_efficiency (precio bajo, $0.60/$2.50)
    72.00,  -- speed_score (depende del provider)
    85.00,  -- reliability_score (9 providers tracked)
    0.88,  -- brand_fit (escala 0-1, fit Monstruo: open-weights + agent swarm)
    0.95,  -- sovereignty (escala 0-1, open-weights + self-hostable)
    0.90,  -- velocity (escala 0-1, release rapido Apr 2026)
    82.50,  -- trono_global
    0.60,   -- precio_input_per_million
    2.50,   -- precio_output_per_million
    '{
        "params_total_b": 1000,
        "params_active_b": 32,
        "context_window": 262144,
        "moe": true,
        "multimodal": true,
        "agent_swarm_subagents_max": 300,
        "agent_swarm_steps_max": 4000,
        "min_hardware_int4": "4xH100"
    }'::jsonb,
    ARRAY['Open-weights con MoE 1T/32B activo', 'Agent Swarm nativo 300 sub-agentes / 4000 steps', 'Native multimodal', 'Long-horizon execution SOTA', 'Soberanía total via self-hosting']::text[],
    ARRAY['Hardware mínimo alto (4x H100)', 'Latencia depende del provider', 'Documentación todavía menos pulida que cerrados']::text[],
    ARRAY['Multi-swarm orchestration via 300 sub-agentes', 'Coding largo (4000 steps)', 'Self-hosting soberano para Monstruo', 'Tool calling multi-step en pipeline catastro']::text[],
    '[
        {"url": "https://huggingface.co/moonshotai/Kimi-K2.6", "tipo": "oficial", "fecha": "2026-04-20", "nota": "Model card oficial Moonshot AI"},
        {"url": "https://www.kimi.com/blog/kimi-k2-6", "tipo": "oficial", "fecha": "2026-04-20", "nota": "Tech blog release oficial"},
        {"url": "https://deepinfra.com/blog/kimi-k2-6-model-overview", "tipo": "tercero", "fecha": "2026-04-30", "nota": "Agent Swarm 300 sub-agentes / 4000 steps confirmados"},
        {"url": "https://medium.com/@tentenco/kimi-k2-6-kimi-code-review-saving-88-coding-costs-b7e8c5eaf5f1", "tipo": "review", "fecha": "2026-04", "nota": "Pricing $0.60/$2.50 confirmado"}
    ]'::jsonb,
    TRUE,
    0.85,
    'manus_catastro',
    '{"sprint": "88.1", "validated_by_research": "real-time 2026-05-10"}'::jsonb,
    1,
    'manus_catastro_sprint_88_1'
)
ON CONFLICT (id) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    proveedor = EXCLUDED.proveedor,
    macroarea = EXCLUDED.macroarea,
    dominios = EXCLUDED.dominios,
    subcapacidades = EXCLUDED.subcapacidades,
    estado = EXCLUDED.estado,
    tipo = EXCLUDED.tipo,
    licencia = EXCLUDED.licencia,
    open_weights = EXCLUDED.open_weights,
    api_endpoint = EXCLUDED.api_endpoint,
    quality_score = EXCLUDED.quality_score,
    cost_efficiency = EXCLUDED.cost_efficiency,
    speed_score = EXCLUDED.speed_score,
    reliability_score = EXCLUDED.reliability_score,
    brand_fit = EXCLUDED.brand_fit,
    sovereignty = EXCLUDED.sovereignty,
    velocity = EXCLUDED.velocity,
    trono_global = EXCLUDED.trono_global,
    precio_input_per_million = EXCLUDED.precio_input_per_million,
    precio_output_per_million = EXCLUDED.precio_output_per_million,
    capacidades_tecnicas = EXCLUDED.capacidades_tecnicas,
    fortalezas = EXCLUDED.fortalezas,
    debilidades = EXCLUDED.debilidades,
    casos_uso_recomendados_monstruo = EXCLUDED.casos_uso_recomendados_monstruo,
    fuentes_evidencia = EXCLUDED.fuentes_evidencia,
    quorum_alcanzado = EXCLUDED.quorum_alcanzado,
    confidence = EXCLUDED.confidence,
    curador_responsable = EXCLUDED.curador_responsable,
    data_extra = EXCLUDED.data_extra,
    validated_by = EXCLUDED.validated_by,
    updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 2) Perplexity Sonar Pro - llm_base de perplexity-personal-computer (trono investigacion)
-- ----------------------------------------------------------------------------
INSERT INTO catastro_modelos (
    id, nombre, proveedor, macroarea, dominios, subcapacidades,
    estado, tipo, licencia, open_weights, api_endpoint,
    quality_score, cost_efficiency, speed_score, reliability_score,
    brand_fit, sovereignty, velocity, trono_global,
    precio_input_per_million, precio_output_per_million,
    capacidades_tecnicas, fortalezas, debilidades, casos_uso_recomendados_monstruo,
    fuentes_evidencia, quorum_alcanzado, confidence,
    curador_responsable, data_extra, schema_version, validated_by
) VALUES (
    'perplexity-sonar-pro',
    'Perplexity Sonar Pro',
    'Perplexity AI',
    'inteligencia',
    ARRAY['llm_frontier', 'search_grounded'],
    ARRAY['real_time_web_search', 'citations_native', 'pro_search_mode']::text[],
    'production',
    'propietario',
    'commercial',
    FALSE,
    'https://api.perplexity.ai',
    72.00,  -- quality_score (15 en Artificial Analysis Index)
    65.00,  -- cost_efficiency (caro: $3/$15 + $18/k requests)
    78.00,  -- speed_score (búsqueda + LLM, latency inherente)
    88.00,  -- reliability_score (Perplexity infra estable)
    0.82,  -- brand_fit (escala 0-1)
    0.25,  -- sovereignty (escala 0-1, cerrado)
    0.78,  -- velocity (escala 0-1)
    74.50,  -- trono_global
    3.00,
    15.00,
    '{
        "context_window": 200000,
        "max_output": 8000,
        "search_grounded": true,
        "citations_native": true,
        "pro_search_mode": true,
        "additional_cost": "USD 18 per 1000 requests"
    }'::jsonb,
    ARRAY['Citations nativas verificables', 'Real-time web search integrado', 'Pro Search mode con búsqueda autónoma', 'Context 200K tokens', 'OpenAI-compatible API']::text[],
    ARRAY['Pricing alto ($3/$15 + $18/k requests)', 'Cerrado / sin self-hosting', 'Quality score sub-frontier (15 AAI)', 'Dependencia total Perplexity infra']::text[],
    ARRAY['Investigación con citations para Monstruo discovery', 'Real-time intel sobre competidores/regulaciones', 'Validación adversarial documental con fuentes verificables']::text[],
    '[
        {"url": "https://artificialanalysis.ai/models/sonar-pro", "tipo": "tercero", "fecha": "2026-05", "nota": "AAI Index 15, context 200k"},
        {"url": "https://llmdex.pankajk.tech/models/sonar-pro", "tipo": "tercero", "fecha": "2026-05-04", "nota": "Pricing $3/$15 confirmado"},
        {"url": "https://openrouter.ai/perplexity/sonar-pro/benchmarks", "tipo": "tercero", "fecha": "2026-05", "nota": "Pricing + $18/1k requests confirmado"},
        {"url": "https://www.cloudzero.com/blog/perplexity-api-pricing/", "tipo": "tercero", "fecha": "2026-05-05", "nota": "Cost analysis Sonar Pro"}
    ]'::jsonb,
    TRUE,
    0.78,
    'manus_catastro',
    '{"sprint": "88.1", "validated_by_research": "real-time 2026-05-10"}'::jsonb,
    1,
    'manus_catastro_sprint_88_1'
)
ON CONFLICT (id) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    proveedor = EXCLUDED.proveedor,
    macroarea = EXCLUDED.macroarea,
    dominios = EXCLUDED.dominios,
    subcapacidades = EXCLUDED.subcapacidades,
    estado = EXCLUDED.estado,
    tipo = EXCLUDED.tipo,
    licencia = EXCLUDED.licencia,
    open_weights = EXCLUDED.open_weights,
    api_endpoint = EXCLUDED.api_endpoint,
    quality_score = EXCLUDED.quality_score,
    cost_efficiency = EXCLUDED.cost_efficiency,
    speed_score = EXCLUDED.speed_score,
    reliability_score = EXCLUDED.reliability_score,
    brand_fit = EXCLUDED.brand_fit,
    sovereignty = EXCLUDED.sovereignty,
    velocity = EXCLUDED.velocity,
    trono_global = EXCLUDED.trono_global,
    precio_input_per_million = EXCLUDED.precio_input_per_million,
    precio_output_per_million = EXCLUDED.precio_output_per_million,
    capacidades_tecnicas = EXCLUDED.capacidades_tecnicas,
    fortalezas = EXCLUDED.fortalezas,
    debilidades = EXCLUDED.debilidades,
    casos_uso_recomendados_monstruo = EXCLUDED.casos_uso_recomendados_monstruo,
    fuentes_evidencia = EXCLUDED.fuentes_evidencia,
    quorum_alcanzado = EXCLUDED.quorum_alcanzado,
    confidence = EXCLUDED.confidence,
    curador_responsable = EXCLUDED.curador_responsable,
    data_extra = EXCLUDED.data_extra,
    validated_by = EXCLUDED.validated_by,
    updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 3) Sora 2 (OpenAI) - llm_base preview vision_generativa (cruza Sprint 89)
-- ----------------------------------------------------------------------------
INSERT INTO catastro_modelos (
    id, nombre, proveedor, macroarea, dominios, subcapacidades,
    estado, tipo, licencia, open_weights, api_endpoint,
    quality_score, cost_efficiency, speed_score, reliability_score,
    brand_fit, sovereignty, velocity, trono_global,
    precio_input_per_million, precio_output_per_million,
    capacidades_tecnicas, fortalezas, debilidades, casos_uso_recomendados_monstruo,
    fuentes_evidencia, quorum_alcanzado, confidence,
    curador_responsable, data_extra, schema_version, validated_by
) VALUES (
    'sora-2',
    'Sora 2',
    'OpenAI',
    'vision_generativa',
    ARRAY['video_largo', 'text_to_video'],
    ARRAY['cinematic_quality', 'physics_simulation', 'creative_control']::text[],
    'production',
    'propietario',
    'commercial',
    FALSE,
    'https://api.openai.com/v1/video/generations',
    82.00,  -- quality_score (top-tier creative control)
    55.00,  -- cost_efficiency ($0.10/s std, video caro per minuto)
    50.00,  -- speed_score (lento vs Seedance/Veo)
    85.00,  -- reliability_score (OpenAI infra)
    0.78,  -- brand_fit (escala 0-1)
    0.20,  -- sovereignty (escala 0-1, cerrado)
    0.85,  -- velocity (escala 0-1)
    74.00,  -- trono_global
    NULL,   -- N/A para video
    NULL,
    '{
        "modalidad": "video",
        "resolucion_max": "720p (1280x720)",
        "precio_por_segundo_std": 0.10,
        "precio_por_segundo_pro": 0.30,
        "duracion_max_segundos": 60,
        "audio_integrado": true,
        "physics_simulation": true,
        "creative_control": "excellent"
    }'::jsonb,
    ARRAY['Creative control top-tier', 'Physics simulation excellent', 'Audio integrado', 'OpenAI ecosystem (ChatGPT integration)']::text[],
    ARRAY['Más lento que Seedance/Veo', 'Calidad cinematográfica menor a Veo en algunas pruebas', 'Audio mono comparado a Veo stereo']::text[],
    ARRAY['Storytelling creativo Monstruo (videos largos)', 'Prototipos rápidos de campañas', 'Video assets para marketing']::text[],
    '[
        {"url": "https://developers.openai.com/api/docs/pricing", "tipo": "oficial", "fecha": "2026-05", "nota": "Sora 2 pricing $0.10/s std, $0.30/s Pro"},
        {"url": "https://www.veo3ai.io/blog/veo-3-vs-sora-2-ultimate-comparison-2026", "tipo": "tercero", "fecha": "2026", "nota": "Sora 2 vs Veo 3 comparison"},
        {"url": "https://costgoat.com/pricing/sora", "tipo": "tercero", "fecha": "2026-02-01", "nota": "Cost guide complete"}
    ]'::jsonb,
    TRUE,
    0.75,
    'manus_catastro',
    '{"sprint": "88.1", "preview_for": "vision_generativa Sprint 89", "validated_by_research": "real-time 2026-05-10"}'::jsonb,
    1,
    'manus_catastro_sprint_88_1'
)
ON CONFLICT (id) DO UPDATE SET
    nombre = EXCLUDED.nombre, proveedor = EXCLUDED.proveedor, macroarea = EXCLUDED.macroarea,
    dominios = EXCLUDED.dominios, subcapacidades = EXCLUDED.subcapacidades, estado = EXCLUDED.estado,
    tipo = EXCLUDED.tipo, licencia = EXCLUDED.licencia, open_weights = EXCLUDED.open_weights,
    api_endpoint = EXCLUDED.api_endpoint, quality_score = EXCLUDED.quality_score,
    cost_efficiency = EXCLUDED.cost_efficiency, speed_score = EXCLUDED.speed_score,
    reliability_score = EXCLUDED.reliability_score, brand_fit = EXCLUDED.brand_fit,
    sovereignty = EXCLUDED.sovereignty, velocity = EXCLUDED.velocity, trono_global = EXCLUDED.trono_global,
    capacidades_tecnicas = EXCLUDED.capacidades_tecnicas, fortalezas = EXCLUDED.fortalezas,
    debilidades = EXCLUDED.debilidades, casos_uso_recomendados_monstruo = EXCLUDED.casos_uso_recomendados_monstruo,
    fuentes_evidencia = EXCLUDED.fuentes_evidencia, quorum_alcanzado = EXCLUDED.quorum_alcanzado,
    confidence = EXCLUDED.confidence, curador_responsable = EXCLUDED.curador_responsable,
    data_extra = EXCLUDED.data_extra, validated_by = EXCLUDED.validated_by, updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 4) Veo 3.1 (Google) - llm_base preview vision_generativa (cruza Sprint 89)
-- ----------------------------------------------------------------------------
INSERT INTO catastro_modelos (
    id, nombre, proveedor, macroarea, dominios, subcapacidades,
    estado, tipo, licencia, open_weights, api_endpoint,
    quality_score, cost_efficiency, speed_score, reliability_score,
    brand_fit, sovereignty, velocity, trono_global,
    precio_input_per_million, precio_output_per_million,
    capacidades_tecnicas, fortalezas, debilidades, casos_uso_recomendados_monstruo,
    fuentes_evidencia, quorum_alcanzado, confidence,
    curador_responsable, data_extra, schema_version, validated_by
) VALUES (
    'veo-3-1',
    'Veo 3.1',
    'Google',
    'vision_generativa',
    ARRAY['video_largo', 'text_to_video'],
    ARRAY['cinematic_quality', 'audio_realism', 'integrated_sound']::text[],
    'production',
    'propietario',
    'commercial',
    FALSE,
    'https://generativelanguage.googleapis.com/v1beta/models/veo-3.1',
    88.00,  -- quality_score (líder cinematográfico 2026 según comparativos)
    62.00,  -- cost_efficiency (via Gemini API, mid-range)
    72.00,  -- speed_score (mid-range vs Seedance/Sora)
    87.00,  -- reliability_score (Google infra)
    0.85,  -- brand_fit (escala 0-1)
    0.22,  -- sovereignty (escala 0-1, cerrado)
    0.88,  -- velocity (escala 0-1)
    79.00,  -- trono_global
    NULL,
    NULL,
    '{
        "modalidad": "video",
        "audio_integrado": true,
        "audio_calidad": "stereo",
        "cinematic_quality": "excellent",
        "fast_mode": true,
        "platforms": ["Gemini API", "Vertex AI", "Wiro"]
    }'::jsonb,
    ARRAY['Audio realismo líder 2026', 'Cinematic quality top-tier', 'Smooth motion / camera control', 'Fast mode disponible para social clips', 'Integración Gemini ecosystem']::text[],
    ARRAY['Cerrado / sin self-hosting', 'Pricing menos transparente que Sora API', 'Character consistency solo Fair (vs Excellent en algunos)']::text[],
    ARRAY['Videos cinematográficos largos para Monstruo storytelling', 'Audio integrado evita post-production', 'Fast mode para social clips rápidos']::text[],
    '[
        {"url": "https://www.veo3ai.io/blog/veo-3-vs-sora-2-ultimate-comparison-2026", "tipo": "tercero", "fecha": "2026", "nota": "Veo 3 leads audio realism + cinematic"},
        {"url": "https://www.aimagicx.com/blog/veo-3-vs-sora-2-vs-seedance-video-comparison-2026", "tipo": "tercero", "fecha": "2026-03-16", "nota": "Head-to-head con motion+prompt adherence"},
        {"url": "https://wiro.ai/blog/veo-3-vs-sora-2-pro-the-new-era-of-ai-video-generation-with-sound/", "tipo": "tercero", "fecha": "2026-02-24", "nota": "Audio integrado confirmado"},
        {"url": "https://www.mindstudio.ai/blog/sora-vs-veo-3-1-vs-seedance-2-comparison/", "tipo": "tercero", "fecha": "2026-03-25", "nota": "Veo 3.1 mid-range speed confirmed"}
    ]'::jsonb,
    TRUE,
    0.78,
    'manus_catastro',
    '{"sprint": "88.1", "preview_for": "vision_generativa Sprint 89", "validated_by_research": "real-time 2026-05-10"}'::jsonb,
    1,
    'manus_catastro_sprint_88_1'
)
ON CONFLICT (id) DO UPDATE SET
    nombre = EXCLUDED.nombre, proveedor = EXCLUDED.proveedor, macroarea = EXCLUDED.macroarea,
    dominios = EXCLUDED.dominios, subcapacidades = EXCLUDED.subcapacidades, estado = EXCLUDED.estado,
    tipo = EXCLUDED.tipo, licencia = EXCLUDED.licencia, open_weights = EXCLUDED.open_weights,
    api_endpoint = EXCLUDED.api_endpoint, quality_score = EXCLUDED.quality_score,
    cost_efficiency = EXCLUDED.cost_efficiency, speed_score = EXCLUDED.speed_score,
    reliability_score = EXCLUDED.reliability_score, brand_fit = EXCLUDED.brand_fit,
    sovereignty = EXCLUDED.sovereignty, velocity = EXCLUDED.velocity, trono_global = EXCLUDED.trono_global,
    capacidades_tecnicas = EXCLUDED.capacidades_tecnicas, fortalezas = EXCLUDED.fortalezas,
    debilidades = EXCLUDED.debilidades, casos_uso_recomendados_monstruo = EXCLUDED.casos_uso_recomendados_monstruo,
    fuentes_evidencia = EXCLUDED.fuentes_evidencia, quorum_alcanzado = EXCLUDED.quorum_alcanzado,
    confidence = EXCLUDED.confidence, curador_responsable = EXCLUDED.curador_responsable,
    data_extra = EXCLUDED.data_extra, validated_by = EXCLUDED.validated_by, updated_at = NOW();

-- ----------------------------------------------------------------------------
-- 5) Actualizar FKs llm_base_id en catastro_agentes para los productos afectados
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes SET llm_base_id = 'kimi-k2-6'
    WHERE id = 'kimi-k2-6-agent-swarm' AND (llm_base_id IS NULL OR llm_base_id != 'kimi-k2-6');

UPDATE catastro_agentes SET llm_base_id = 'perplexity-sonar-pro'
    WHERE id = 'perplexity-personal-computer' AND (llm_base_id IS NULL OR llm_base_id != 'perplexity-sonar-pro');

UPDATE catastro_agentes SET llm_base_id = 'perplexity-sonar-pro'
    WHERE id = 'comet-browser-perplexity' AND (llm_base_id IS NULL OR llm_base_id != 'perplexity-sonar-pro');

-- Higgsfield envuelve múltiples (Sora, Veo, Runway). Marcar como "multi" y dejar llm_base_id NULL con nota.
UPDATE catastro_agentes
SET data_extra = COALESCE(data_extra, '{}'::jsonb) || '{"llm_bases_envueltos": ["sora-2", "veo-3-1", "runway-gen-4-5", "kling-3-0"], "nota": "Wrapper multi-modelo, FK NULL por diseño - ver data_extra"}'::jsonb
    WHERE id = 'higgsfield';

-- Refresh vista materializada de tronos para reflejar nuevos FKs
REFRESH MATERIALIZED VIEW catastro_tronos_agentes;

COMMIT;

-- ============================================================================
-- Validación post-migración
-- ============================================================================
SELECT id, nombre, proveedor, macroarea, quality_score, cost_efficiency, trono_global, confidence
FROM catastro_modelos
WHERE id IN ('kimi-k2-6', 'perplexity-sonar-pro', 'sora-2', 'veo-3-1')
ORDER BY id;

SELECT id, nombre, llm_base_id
FROM catastro_agentes
WHERE id IN ('kimi-k2-6-agent-swarm', 'perplexity-personal-computer', 'comet-browser-perplexity', 'higgsfield')
ORDER BY id;
