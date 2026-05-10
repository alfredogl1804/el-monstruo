-- ============================================================================
-- Migration 040 — Sprint 88.3: Macroárea VISION_GENERATIVA
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.3) — Tarea 3
-- Origen: Validación adversarial Perplexity (12 sub-dominios canónicos)
-- Input: /home/ubuntu/upload/pasted_content_19.txt (JSON Perplexity)
-- Decisión arquitectónica: tabla separada catastro_vision_generativa
--   porque dimensiones técnicas son distintas a catastro_agentes
--   (duracion_max_clip_sec, audio_nativo, licensing_risk, consent_required).
-- Idempotente: ON CONFLICT DO UPDATE
-- Author: Hilo Catastro (Manus B)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1) CREATE TABLE catastro_vision_generativa
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catastro_vision_generativa (
    id                          TEXT PRIMARY KEY,
    nombre                      TEXT NOT NULL,
    proveedor                   TEXT NOT NULL,
    macroarea                   TEXT NOT NULL DEFAULT 'vision_generativa'
        CHECK (macroarea = 'vision_generativa'),
    subdominio_primario         TEXT NOT NULL,
    subdominios_secundarios     TEXT[] NOT NULL DEFAULT '{}',
    url_oficial                 TEXT,

    -- Capacidades técnicas específicas vision generativa
    modalidad_input             TEXT[] NOT NULL DEFAULT '{}',
    modalidad_output            TEXT[] NOT NULL DEFAULT '{}',
    duracion_max_clip_sec       INTEGER,
    resolucion_max              TEXT,
    audio_nativo                BOOLEAN NOT NULL DEFAULT FALSE,
    multi_shot_capable          BOOLEAN NOT NULL DEFAULT FALSE,
    consistencia_personaje      BOOLEAN NOT NULL DEFAULT FALSE,
    api_disponible              BOOLEAN NOT NULL DEFAULT FALSE,
    mcp_server_disponible       BOOLEAN NOT NULL DEFAULT FALSE,

    -- Doctrina + cumplimiento
    licensing_risk              TEXT NOT NULL DEFAULT 'low'
        CHECK (licensing_risk IN ('low', 'medium', 'high')),
    consent_required            BOOLEAN NOT NULL DEFAULT FALSE,
    c2pa_provenance             BOOLEAN NOT NULL DEFAULT FALSE,
    watermark_native            BOOLEAN NOT NULL DEFAULT FALSE,

    -- Estado + comercialización
    estado                      TEXT NOT NULL DEFAULT 'production'
        CHECK (estado IN ('production', 'beta', 'preview', 'open-source', 'deprecated', 'alpha')),
    costo_por_uso_tipico        TEXT
        CHECK (costo_por_uso_tipico IS NULL OR costo_por_uso_tipico IN ('gratis', 'bajo', 'medio', 'alto', 'enterprise')),
    open_weights                BOOLEAN NOT NULL DEFAULT FALSE,

    -- Curaduría + scoring
    tier_seed                   SMALLINT NOT NULL DEFAULT 1
        CHECK (tier_seed IN (1, 2)),
    bonus_curador               SMALLINT NOT NULL DEFAULT 0
        CHECK (bonus_curador >= 0 AND bonus_curador <= 50),
    bonus_curador_razon         TEXT,
    score_subdominio_origen     INTEGER,
    riesgo_adversarial          TEXT,

    -- Validación
    fuentes_evidencia           JSONB NOT NULL DEFAULT '[]'::jsonb,
    validacion_adversarial      JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_extra                  JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence                  NUMERIC(3,2) NOT NULL DEFAULT 0.50
        CHECK (confidence >= 0.00 AND confidence <= 1.00),

    -- Timestamps
    schema_version              SMALLINT NOT NULL DEFAULT 1,
    ultima_validacion           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    proxima_revalidacion        TIMESTAMP WITH TIME ZONE,
    created_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 2) CHECK constraint subdominio_primario (12 valores canónicos)
-- ----------------------------------------------------------------------------
ALTER TABLE catastro_vision_generativa
  DROP CONSTRAINT IF EXISTS chk_subdominio_primario_valido;

ALTER TABLE catastro_vision_generativa
  ADD CONSTRAINT chk_subdominio_primario_valido CHECK (subdominio_primario IN (
    'imagen_estatica_premium',
    'video_clip_generativo',
    'video_narrativo_cinematico',
    'avatar_humano_animado',
    'realtime_video_agents_characters',
    'lip_sync_visual_dubbing',
    'tts_voces_sinteticas',
    'musica_generada',
    'efectos_sonido_sfx',
    'generative_editing_inpainting',
    'upscaling_restauracion_enhancement',
    '3d_mocap_assets'
  ));

-- ----------------------------------------------------------------------------
-- 3) Índices
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_cvg_subdominio_primario
    ON catastro_vision_generativa (subdominio_primario);
CREATE INDEX IF NOT EXISTS idx_cvg_proveedor
    ON catastro_vision_generativa (proveedor);
CREATE INDEX IF NOT EXISTS idx_cvg_licensing_risk
    ON catastro_vision_generativa (licensing_risk);

COMMIT;
BEGIN;

-- ----------------------------------------------------------------------------
-- 4) INSERT 38 productos seed (Perplexity validation)
-- ----------------------------------------------------------------------------

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'midjourney_v7',
    $$Midjourney v7$$,
    $$Midjourney$$,
    'imagen_estatica_premium',
    '{}'::TEXT[],
    $$https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version$$,
    'low',
    False,
    1,
    10,
    $$Trono imagen_estatica_premium según Perplexity (validación adversarial). Midjourney v7 default desde 2025: precision de prompts, texturas, cuerpos, manos, Draft Mode + Omni Reference. Score subdominio 95/100.$$,
    95,
    $$low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.$$,
    $$[{"fuente": "https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 95, "riesgo_adversarial": "low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.", "criterio_inclusion": "Modelos o plataformas cuyo output principal es imagen estatica de alta calidad, con control estetico, estilo, referencias, texto legible, seguridad o API productiva."}$$::jsonb,
    $${"es_trono_de": ["imagen_estatica_premium"], "subdominios_aparece": ["imagen_estatica_premium"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'imagen_4',
    $$Imagen 4$$,
    $$Google$$,
    'imagen_estatica_premium',
    '{}'::TEXT[],
    $$https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate$$,
    'low',
    False,
    1,
    0,
    NULL,
    95,
    $$low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.$$,
    $$[{"fuente": "https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 95, "riesgo_adversarial": "low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.", "criterio_inclusion": "Modelos o plataformas cuyo output principal es imagen estatica de alta calidad, con control estetico, estilo, referencias, texto legible, seguridad o API productiva."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["imagen_estatica_premium"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'flux_2',
    $$FLUX.2$$,
    $$Black Forest Labs$$,
    'imagen_estatica_premium',
    ARRAY['generative_editing_inpainting']::TEXT[],
    $$https://bfl.ai/models/flux-2$$,
    'low',
    False,
    1,
    0,
    NULL,
    95,
    $$low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.$$,
    $$[{"fuente": "https://bfl.ai/models/flux-2", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 95, "riesgo_adversarial": "low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.", "criterio_inclusion": "Modelos o plataformas cuyo output principal es imagen estatica de alta calidad, con control estetico, estilo, referencias, texto legible, seguridad o API productiva."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["imagen_estatica_premium", "generative_editing_inpainting"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'ideogram_3',
    $$Ideogram 3.0$$,
    $$Ideogram$$,
    'imagen_estatica_premium',
    ARRAY['generative_editing_inpainting']::TEXT[],
    $$https://ideogram.ai/features/3.0/$$,
    'low',
    False,
    1,
    0,
    NULL,
    95,
    $$low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.$$,
    $$[{"fuente": "https://ideogram.ai/features/3.0/", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 95, "riesgo_adversarial": "low: dominio maduro con lideres claros; riesgo principal es mezclar estetica, API, diseno con texto y edicion.", "criterio_inclusion": "Modelos o plataformas cuyo output principal es imagen estatica de alta calidad, con control estetico, estilo, referencias, texto legible, seguridad o API productiva."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["imagen_estatica_premium", "generative_editing_inpainting"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'veo_3_1',
    $$Veo 3.1$$,
    $$Google$$,
    'video_clip_generativo',
    ARRAY['video_narrativo_cinematico']::TEXT[],
    $$https://gemini.google/overview/video-generation/$$,
    'low',
    False,
    1,
    10,
    $$Trono video_clip_generativo según Perplexity. Veo 3.1 genera clips 8s con audio nativo, referencias múltiples y video vertical (Gemini). Score subdominio 85/100. Acompañantes fuertes: Runway Gen-4.5 (top Artificial Analysis), Luma Ray2.$$,
    85,
    $$medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.$$,
    $$[{"fuente": "https://gemini.google/overview/video-generation/", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 85, "riesgo_adversarial": "medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.", "criterio_inclusion": "Modelos que generan clips unitarios de video, normalmente menores a 60 segundos, desde texto, imagen, video o audio."}$$::jsonb,
    $${"es_trono_de": ["video_clip_generativo"], "subdominios_aparece": ["video_clip_generativo", "video_narrativo_cinematico"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'runway_gen_4_5',
    $$Runway Gen-4.5$$,
    $$Runway$$,
    'video_clip_generativo',
    ARRAY['video_narrativo_cinematico']::TEXT[],
    $$https://runwayml.com/research/introducing-runway-gen-4.5$$,
    'low',
    False,
    1,
    10,
    $$Trono video_narrativo_cinematico según Perplexity. Runway Gen-4.5 top Artificial Analysis Text-to-Video benchmark (1247 Elo). Visual fidelity + prompt adherence + motion quality + creative control. Score subdominio 55/100 (no valida cine 60s+ nativo, solo workflow narrativo).$$,
    85,
    $$medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.$$,
    $$[{"fuente": "https://runwayml.com/research/introducing-runway-gen-4.5", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 85, "riesgo_adversarial": "medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.", "criterio_inclusion": "Modelos que generan clips unitarios de video, normalmente menores a 60 segundos, desde texto, imagen, video o audio."}$$::jsonb,
    $${"es_trono_de": ["video_narrativo_cinematico"], "subdominios_aparece": ["video_clip_generativo", "video_narrativo_cinematico"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'luma_ray_2',
    $$Luma Ray2$$,
    $$Luma AI$$,
    'video_clip_generativo',
    '{}'::TEXT[],
    $$https://lumalabs.ai/ray2$$,
    'low',
    False,
    1,
    0,
    NULL,
    85,
    $$medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.$$,
    $$[{"fuente": "https://lumalabs.ai/ray2", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 85, "riesgo_adversarial": "medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.", "criterio_inclusion": "Modelos que generan clips unitarios de video, normalmente menores a 60 segundos, desde texto, imagen, video o audio."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["video_clip_generativo"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'seedance_2_0',
    $$Seedance 2.0$$,
    $$ByteDance$$,
    'video_clip_generativo',
    '{}'::TEXT[],
    $$https://seed.bytedance.com/en/seedance2_0$$,
    'low',
    False,
    1,
    0,
    NULL,
    85,
    $$medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.$$,
    $$[{"fuente": "https://seed.bytedance.com/en/seedance2_0", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 85, "riesgo_adversarial": "medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.", "criterio_inclusion": "Modelos que generan clips unitarios de video, normalmente menores a 60 segundos, desde texto, imagen, video o audio."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["video_clip_generativo"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'pika',
    $$Pika$$,
    $$Pika Labs$$,
    'video_clip_generativo',
    '{}'::TEXT[],
    $$https://pika.art$$,
    'low',
    False,
    1,
    0,
    NULL,
    85,
    $$medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.$$,
    $$[{"fuente": "https://pika.art", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 85, "riesgo_adversarial": "medium: dominio real, pero algunas versiones comerciales no siempre estan confirmadas oficialmente y la duracion nativa sigue siendo corta.", "criterio_inclusion": "Modelos que generan clips unitarios de video, normalmente menores a 60 segundos, desde texto, imagen, video o audio."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["video_clip_generativo"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'kling_3_0',
    $$Kling 3.0$$,
    $$Kuaishou$$,
    'video_narrativo_cinematico',
    '{}'::TEXT[],
    $$https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-launches-30-model-ushering-era-where-everyone-can-be$$,
    'medium',
    False,
    1,
    0,
    NULL,
    55,
    $$high: no debe validarse como cine 60s+ nativo; la evidencia oficial apunta a clips cortos y workflows de stitching, extension y storyboarding.$$,
    $$[{"fuente": "https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-launches-30-model-ushering-era-where-everyone-can-be", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 55, "riesgo_adversarial": "high: no debe validarse como cine 60s+ nativo; la evidencia oficial apunta a clips cortos y workflows de stitching, extension y storyboarding.", "criterio_inclusion": "Pipelines y modelos orientados a storytelling, control cinematografico, multi-shot, extension, continuidad de personajes o produccion de escenas, aunque los clips nativos sean cortos."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["video_narrativo_cinematico"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'sora_2',
    $$Sora 2$$,
    $$OpenAI$$,
    'video_narrativo_cinematico',
    '{}'::TEXT[],
    $$https://developers.openai.com/api/docs/guides/video-generation$$,
    'medium',
    False,
    1,
    0,
    NULL,
    55,
    $$high: no debe validarse como cine 60s+ nativo; la evidencia oficial apunta a clips cortos y workflows de stitching, extension y storyboarding.$$,
    $$[{"fuente": "https://developers.openai.com/api/docs/guides/video-generation", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 55, "riesgo_adversarial": "high: no debe validarse como cine 60s+ nativo; la evidencia oficial apunta a clips cortos y workflows de stitching, extension y storyboarding.", "criterio_inclusion": "Pipelines y modelos orientados a storytelling, control cinematografico, multi-shot, extension, continuidad de personajes o produccion de escenas, aunque los clips nativos sean cortos."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["video_narrativo_cinematico"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'higgsfield',
    $$Higgsfield$$,
    $$Higgsfield$$,
    'video_narrativo_cinematico',
    '{}'::TEXT[],
    $$https://higgsfield.ai$$,
    'medium',
    False,
    1,
    0,
    NULL,
    55,
    $$high: no debe validarse como cine 60s+ nativo; la evidencia oficial apunta a clips cortos y workflows de stitching, extension y storyboarding.$$,
    $$[{"fuente": "https://higgsfield.ai", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 55, "riesgo_adversarial": "high: no debe validarse como cine 60s+ nativo; la evidencia oficial apunta a clips cortos y workflows de stitching, extension y storyboarding.", "criterio_inclusion": "Pipelines y modelos orientados a storytelling, control cinematografico, multi-shot, extension, continuidad de personajes o produccion de escenas, aunque los clips nativos sean cortos."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["video_narrativo_cinematico"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'synthesia',
    $$Synthesia$$,
    $$Synthesia$$,
    'avatar_humano_animado',
    ARRAY['lip_sync_visual_dubbing']::TEXT[],
    $$https://www.synthesia.io/features/avatars$$,
    'medium',
    True,
    1,
    10,
    $$Trono avatar_humano_animado según Perplexity. Synthesia 240+ stock avatars, avatar personal con consentimiento, voice cloning, escenas con Veo 3. Enterprise-grade. HeyGen como creator/localization Tier 1. Score subdominio 90/100.$$,
    90,
    $$medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.$$,
    $$[{"fuente": "https://www.synthesia.io/features/avatars", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 90, "riesgo_adversarial": "medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.", "criterio_inclusion": "Plataformas que generan presentadores, humanos sinteticos, avatares de marca, talking heads, full-body avatars o videos corporativos/localizados con identidad humana."}$$::jsonb,
    $${"es_trono_de": ["avatar_humano_animado"], "subdominios_aparece": ["avatar_humano_animado", "lip_sync_visual_dubbing"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'heygen',
    $$HeyGen$$,
    $$HeyGen$$,
    'avatar_humano_animado',
    ARRAY['lip_sync_visual_dubbing']::TEXT[],
    $$https://www.heygen.com$$,
    'medium',
    True,
    1,
    0,
    NULL,
    90,
    $$medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.$$,
    $$[{"fuente": "https://www.heygen.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 90, "riesgo_adversarial": "medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.", "criterio_inclusion": "Plataformas que generan presentadores, humanos sinteticos, avatares de marca, talking heads, full-body avatars o videos corporativos/localizados con identidad humana."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["avatar_humano_animado", "lip_sync_visual_dubbing"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'akool',
    $$AKOOL$$,
    $$AKOOL$$,
    'avatar_humano_animado',
    ARRAY['lip_sync_visual_dubbing']::TEXT[],
    $$https://akool.com$$,
    'medium',
    True,
    1,
    0,
    NULL,
    90,
    $$medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.$$,
    $$[{"fuente": "https://akool.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 90, "riesgo_adversarial": "medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.", "criterio_inclusion": "Plataformas que generan presentadores, humanos sinteticos, avatares de marca, talking heads, full-body avatars o videos corporativos/localizados con identidad humana."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["avatar_humano_animado", "lip_sync_visual_dubbing"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'hedra',
    $$Hedra$$,
    $$Hedra$$,
    'avatar_humano_animado',
    '{}'::TEXT[],
    $$https://www.hedra.com$$,
    'medium',
    True,
    1,
    0,
    NULL,
    90,
    $$medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.$$,
    $$[{"fuente": "https://www.hedra.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 90, "riesgo_adversarial": "medium: dominio maduro, pero conviene separar talking-head, avatar corporativo, full-body avatar y realtime avatar.", "criterio_inclusion": "Plataformas que generan presentadores, humanos sinteticos, avatares de marca, talking heads, full-body avatars o videos corporativos/localizados con identidad humana."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["avatar_humano_animado"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'runway_characters',
    $$Runway Characters$$,
    $$Runway$$,
    'realtime_video_agents_characters',
    '{}'::TEXT[],
    $$https://runwayml.com$$,
    'medium',
    True,
    1,
    10,
    $$Trono realtime_video_agents_characters según Perplexity. Runway Characters: video agents en tiempo real con apariencia, voz, personalidad, conocimiento, acciones configurables. Dominio emergente estratégico. Score subdominio 68/100.$$,
    68,
    $$medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.$$,
    $$[{"fuente": "https://runwayml.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 68, "riesgo_adversarial": "medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.", "criterio_inclusion": "Agentes audiovisuales o personajes sinteticos conversacionales en tiempo real, con apariencia, voz, personalidad, conocimiento o acciones configurables."}$$::jsonb,
    $${"es_trono_de": ["realtime_video_agents_characters"], "subdominios_aparece": ["realtime_video_agents_characters"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'inworld_realtime_tts_2',
    $$Realtime TTS-2$$,
    $$Inworld$$,
    'realtime_video_agents_characters',
    ARRAY['tts_voces_sinteticas']::TEXT[],
    $$https://inworld.ai/blog/realtime-tts-2$$,
    'medium',
    True,
    1,
    0,
    NULL,
    68,
    $$medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.$$,
    $$[{"fuente": "https://inworld.ai/blog/realtime-tts-2", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 68, "riesgo_adversarial": "medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.", "criterio_inclusion": "Agentes audiovisuales o personajes sinteticos conversacionales en tiempo real, con apariencia, voz, personalidad, conocimiento o acciones configurables."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["realtime_video_agents_characters", "tts_voces_sinteticas"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'openai_gpt_realtime_2',
    $$GPT-Realtime-2$$,
    $$OpenAI$$,
    'realtime_video_agents_characters',
    ARRAY['tts_voces_sinteticas']::TEXT[],
    $$https://techcrunch.com/2026/05/07/openai-launches-new-voice-intelligence-features-in-its-api/$$,
    'medium',
    True,
    1,
    0,
    NULL,
    68,
    $$medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.$$,
    $$[{"fuente": "https://techcrunch.com/2026/05/07/openai-launches-new-voice-intelligence-features-in-its-api/", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 68, "riesgo_adversarial": "medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.", "criterio_inclusion": "Agentes audiovisuales o personajes sinteticos conversacionales en tiempo real, con apariencia, voz, personalidad, conocimiento o acciones configurables."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["realtime_video_agents_characters", "tts_voces_sinteticas"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'synthesia_avatar',
    $$Synthesia Avatars$$,
    $$Synthesia$$,
    'realtime_video_agents_characters',
    '{}'::TEXT[],
    $$https://www.synthesia.io/features/avatars$$,
    'medium',
    True,
    1,
    0,
    NULL,
    68,
    $$medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.$$,
    $$[{"fuente": "https://www.synthesia.io/features/avatars", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 68, "riesgo_adversarial": "medium: dominio emergente con pocos benchmarks publicos, dudas de latencia extremo a extremo, coste e identidad persistente.", "criterio_inclusion": "Agentes audiovisuales o personajes sinteticos conversacionales en tiempo real, con apariencia, voz, personalidad, conocimiento o acciones configurables."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["realtime_video_agents_characters"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'sync_labs',
    $$sync. labs$$,
    $$sync. labs$$,
    'lip_sync_visual_dubbing',
    '{}'::TEXT[],
    $$https://sync.so$$,
    'medium',
    True,
    1,
    10,
    $$Trono lip_sync_visual_dubbing según Perplexity. sync.labs API especializada en lipsync. Distinto a TTS y avatar: modifica boca sobre video existente. Score subdominio 82/100. Riesgos: consentimiento, deepfake, multi-speaker.$$,
    82,
    $$medium: riesgo de consentimiento, deepfake, calidad en multi-speaker y sincronizacion en emociones extremas.$$,
    $$[{"fuente": "https://sync.so", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 82, "riesgo_adversarial": "medium: riesgo de consentimiento, deepfake, calidad en multi-speaker y sincronizacion en emociones extremas.", "criterio_inclusion": "Herramientas que modifican boca, rostro o performance visual de video existente para sincronizar voz, idioma o doblaje."}$$::jsonb,
    $${"es_trono_de": ["lip_sync_visual_dubbing"], "subdominios_aparece": ["lip_sync_visual_dubbing"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'elevenlabs_tts',
    $$ElevenLabs Text to Speech$$,
    $$ElevenLabs$$,
    'tts_voces_sinteticas',
    '{}'::TEXT[],
    $$https://elevenlabs.io/text-to-speech$$,
    'medium',
    True,
    1,
    10,
    $$Trono tts_voces_sinteticas según Perplexity. ElevenLabs biblioteca + clonación líder 2026. OpenAI/Inworld Tier 1 para realtime. Score subdominio 95/100. Requiere flags consent + voice cloning + uso comercial.$$,
    95,
    $$medium: dominio maduro, pero requiere flags de consentimiento, voice cloning, identidad y uso comercial.$$,
    $$[{"fuente": "https://elevenlabs.io/text-to-speech", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 95, "riesgo_adversarial": "medium: dominio maduro, pero requiere flags de consentimiento, voice cloning, identidad y uso comercial.", "criterio_inclusion": "Modelos o plataformas que convierten texto o instrucciones en voz sintetica, con control de voz, idioma, expresion, clonacion o streaming."}$$::jsonb,
    $${"es_trono_de": ["tts_voces_sinteticas"], "subdominios_aparece": ["tts_voces_sinteticas"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'openai_gpt_4o_mini_tts',
    $$gpt-4o-mini-tts$$,
    $$OpenAI$$,
    'tts_voces_sinteticas',
    '{}'::TEXT[],
    $$https://developers.openai.com/api/docs/guides/text-to-speech$$,
    'medium',
    True,
    1,
    0,
    NULL,
    95,
    $$medium: dominio maduro, pero requiere flags de consentimiento, voice cloning, identidad y uso comercial.$$,
    $$[{"fuente": "https://developers.openai.com/api/docs/guides/text-to-speech", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 95, "riesgo_adversarial": "medium: dominio maduro, pero requiere flags de consentimiento, voice cloning, identidad y uso comercial.", "criterio_inclusion": "Modelos o plataformas que convierten texto o instrucciones en voz sintetica, con control de voz, idioma, expresion, clonacion o streaming."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["tts_voces_sinteticas"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'suno_v5_5',
    $$Suno v5.5$$,
    $$Suno$$,
    'musica_generada',
    '{}'::TEXT[],
    $$https://suno.com/blog/v5-5$$,
    'high',
    False,
    1,
    10,
    $$Trono musica_generada según Perplexity. Suno v5.5 canción completa. Udio licensing strategic agreements UMG = challenger licenciado. Score subdominio 80/100. licensing_risk=high obligatorio.$$,
    80,
    $$high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.$$,
    $$[{"fuente": "https://suno.com/blog/v5-5", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 80, "riesgo_adversarial": "high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.", "criterio_inclusion": "Plataformas que generan canciones, composiciones, instrumentales, loops o musica usable en productos, media o creacion artistica."}$$::jsonb,
    $${"es_trono_de": ["musica_generada"], "subdominios_aparece": ["musica_generada"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'udio',
    $$Udio$$,
    $$Udio$$,
    'musica_generada',
    '{}'::TEXT[],
    $$https://www.universalmusic.com/universal-music-group-and-udio-announce-udios-first-strategic-agreements-for-new-licensed-ai-music-creation-platform/$$,
    'high',
    False,
    1,
    0,
    NULL,
    80,
    $$high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.$$,
    $$[{"fuente": "https://www.universalmusic.com/universal-music-group-and-udio-announce-udios-first-strategic-agreements-for-new-licensed-ai-music-creation-platform/", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 80, "riesgo_adversarial": "high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.", "criterio_inclusion": "Plataformas que generan canciones, composiciones, instrumentales, loops o musica usable en productos, media o creacion artistica."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["musica_generada"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'aiva',
    $$AIVA$$,
    $$AIVA$$,
    'musica_generada',
    '{}'::TEXT[],
    $$https://www.aiva.ai$$,
    'high',
    False,
    1,
    0,
    NULL,
    80,
    $$high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.$$,
    $$[{"fuente": "https://www.aiva.ai", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 80, "riesgo_adversarial": "high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.", "criterio_inclusion": "Plataformas que generan canciones, composiciones, instrumentales, loops o musica usable en productos, media o creacion artistica."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["musica_generada"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'mubert',
    $$Mubert$$,
    $$Mubert$$,
    'musica_generada',
    ARRAY['efectos_sonido_sfx']::TEXT[],
    $$https://mubert.com$$,
    'high',
    False,
    1,
    0,
    NULL,
    80,
    $$high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.$$,
    $$[{"fuente": "https://mubert.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 80, "riesgo_adversarial": "high: dominio real, pero legalmente sensible por licencias, training data, publishing y uso comercial.", "criterio_inclusion": "Plataformas que generan canciones, composiciones, instrumentales, loops o musica usable en productos, media o creacion artistica."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["musica_generada", "efectos_sonido_sfx"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'elevenlabs_sfx',
    $$ElevenLabs Sound Effects$$,
    $$ElevenLabs$$,
    'efectos_sonido_sfx',
    '{}'::TEXT[],
    $$https://elevenlabs.io/sound-effects$$,
    'low',
    False,
    1,
    10,
    $$Trono efectos_sonido_sfx según Perplexity. ElevenLabs SFX producto hosted. Stable Audio Open OSS Tier 1. Score subdominio 70/100 (menos maduro que music+TTS).$$,
    70,
    $$medium: menos maduro que musica y TTS; faltan sincronia frame-accurate, integracion NLE, stems y licencias por industria.$$,
    $$[{"fuente": "https://elevenlabs.io/sound-effects", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 70, "riesgo_adversarial": "medium: menos maduro que musica y TTS; faltan sincronia frame-accurate, integracion NLE, stems y licencias por industria.", "criterio_inclusion": "Generacion de foley, ambience, production elements, text-to-sound, sound design y efectos de sonido no musicales."}$$::jsonb,
    $${"es_trono_de": ["efectos_sonido_sfx"], "subdominios_aparece": ["efectos_sonido_sfx"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'stable_audio_open',
    $$Stable Audio Open$$,
    $$Stability AI$$,
    'efectos_sonido_sfx',
    '{}'::TEXT[],
    $$https://stability.ai/news-updates/introducing-stable-audio-open$$,
    'low',
    False,
    1,
    0,
    NULL,
    70,
    $$medium: menos maduro que musica y TTS; faltan sincronia frame-accurate, integracion NLE, stems y licencias por industria.$$,
    $$[{"fuente": "https://stability.ai/news-updates/introducing-stable-audio-open", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 70, "riesgo_adversarial": "medium: menos maduro que musica y TTS; faltan sincronia frame-accurate, integracion NLE, stems y licencias por industria.", "criterio_inclusion": "Generacion de foley, ambience, production elements, text-to-sound, sound design y efectos de sonido no musicales."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["efectos_sonido_sfx"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'stable_audio_2_5',
    $$Stable Audio 2.5$$,
    $$Stability AI$$,
    'efectos_sonido_sfx',
    '{}'::TEXT[],
    $$https://stability.ai/stable-audio$$,
    'low',
    False,
    1,
    0,
    NULL,
    70,
    $$medium: menos maduro que musica y TTS; faltan sincronia frame-accurate, integracion NLE, stems y licencias por industria.$$,
    $$[{"fuente": "https://stability.ai/stable-audio", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 70, "riesgo_adversarial": "medium: menos maduro que musica y TTS; faltan sincronia frame-accurate, integracion NLE, stems y licencias por industria.", "criterio_inclusion": "Generacion de foley, ambience, production elements, text-to-sound, sound design y efectos de sonido no musicales."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["efectos_sonido_sfx"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'adobe_firefly_video_editor',
    $$Adobe Firefly Video Editor$$,
    $$Adobe$$,
    'generative_editing_inpainting',
    ARRAY['upscaling_restauracion_enhancement']::TEXT[],
    $$https://blog.adobe.com/en/publish/2026/04/15/adobe-extends-leadership-video-unleashing-new-ai-powered-creation-firefly-reinventing-color-editors-in-premiere$$,
    'low',
    False,
    1,
    10,
    $$Trono generative_editing_inpainting según Perplexity. Adobe Firefly Video Editor (Apr 2026) suite creativa para edición semántica. FLUX.2 + Runway Tier 1. Score subdominio 88/100.$$,
    88,
    $$medium: riesgo de solapamiento con postproduccion si no se define como edicion semantica generativa.$$,
    $$[{"fuente": "https://blog.adobe.com/en/publish/2026/04/15/adobe-extends-leadership-video-unleashing-new-ai-powered-creation-firefly-reinventing-color-editors-in-premiere", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 88, "riesgo_adversarial": "medium: riesgo de solapamiento con postproduccion si no se define como edicion semantica generativa.", "criterio_inclusion": "Edicion semantica de imagen o video: inpainting, outpainting, object removal/replacement, expansion generativa, edicion por texto o referencia."}$$::jsonb,
    $${"es_trono_de": ["generative_editing_inpainting"], "subdominios_aparece": ["generative_editing_inpainting", "upscaling_restauracion_enhancement"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'runway',
    $$Runway$$,
    $$Runway$$,
    'generative_editing_inpainting',
    ARRAY['upscaling_restauracion_enhancement']::TEXT[],
    $$https://runwayml.com$$,
    'low',
    False,
    1,
    0,
    NULL,
    88,
    $$medium: riesgo de solapamiento con postproduccion si no se define como edicion semantica generativa.$$,
    $$[{"fuente": "https://runwayml.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 88, "riesgo_adversarial": "medium: riesgo de solapamiento con postproduccion si no se define como edicion semantica generativa.", "criterio_inclusion": "Edicion semantica de imagen o video: inpainting, outpainting, object removal/replacement, expansion generativa, edicion por texto o referencia."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["generative_editing_inpainting", "upscaling_restauracion_enhancement"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'topaz_video',
    $$Topaz Video$$,
    $$Topaz Labs$$,
    'upscaling_restauracion_enhancement',
    '{}'::TEXT[],
    $$https://www.topazlabs.com/topaz-video$$,
    'low',
    False,
    1,
    10,
    $$Trono upscaling_restauracion_enhancement según Perplexity. Topaz Video estándar de la industria para upscaling+restauración objetiva. Magnific Tier 1 para upscaling creativo multimodal. Score subdominio 86/100.$$,
    86,
    $$medium: separar restauracion objetiva de upscaling creativo que inventa detalle.$$,
    $$[{"fuente": "https://www.topazlabs.com/topaz-video", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 86, "riesgo_adversarial": "medium: separar restauracion objetiva de upscaling creativo que inventa detalle.", "criterio_inclusion": "Mejora, restauracion, denoise, sharpen, super-resolution, frame interpolation o upscaling creativo de imagen/video."}$$::jsonb,
    $${"es_trono_de": ["upscaling_restauracion_enhancement"], "subdominios_aparece": ["upscaling_restauracion_enhancement"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'magnific',
    $$Magnific$$,
    $$Magnific$$,
    'upscaling_restauracion_enhancement',
    '{}'::TEXT[],
    $$https://www.magnific.com$$,
    'low',
    False,
    1,
    0,
    NULL,
    86,
    $$medium: separar restauracion objetiva de upscaling creativo que inventa detalle.$$,
    $$[{"fuente": "https://www.magnific.com", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 86, "riesgo_adversarial": "medium: separar restauracion objetiva de upscaling creativo que inventa detalle.", "criterio_inclusion": "Mejora, restauracion, denoise, sharpen, super-resolution, frame interpolation o upscaling creativo de imagen/video."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["upscaling_restauracion_enhancement"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'meshy',
    $$Meshy$$,
    $$Meshy$$,
    '3d_mocap_assets',
    '{}'::TEXT[],
    $$https://www.meshy.ai/features/text-to-3d$$,
    'low',
    False,
    1,
    10,
    $$Trono 3d_mocap_assets según Perplexity. Meshy text-to-3D + image-to-3D. Tripo Tier 1 challenger. Move AI + Autodesk Flow Studio para mocap. Score subdominio 78/100.$$,
    78,
    $$medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.$$,
    $$[{"fuente": "https://www.meshy.ai/features/text-to-3d", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 78, "riesgo_adversarial": "medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.", "criterio_inclusion": "Generacion de modelos 3D, text-to-3D, image-to-3D, texturizado, assets para juegos/VFX/arquitectura, markerless mocap y performance capture."}$$::jsonb,
    $${"es_trono_de": ["3d_mocap_assets"], "subdominios_aparece": ["3d_mocap_assets"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'tripo',
    $$Tripo$$,
    $$Tripo AI$$,
    '3d_mocap_assets',
    '{}'::TEXT[],
    $$https://www.tripo3d.ai$$,
    'low',
    False,
    1,
    0,
    NULL,
    78,
    $$medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.$$,
    $$[{"fuente": "https://www.tripo3d.ai", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 78, "riesgo_adversarial": "medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.", "criterio_inclusion": "Generacion de modelos 3D, text-to-3D, image-to-3D, texturizado, assets para juegos/VFX/arquitectura, markerless mocap y performance capture."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["3d_mocap_assets"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'move_ai',
    $$Move AI$$,
    $$Move AI$$,
    '3d_mocap_assets',
    '{}'::TEXT[],
    $$https://move.ai$$,
    'low',
    False,
    1,
    0,
    NULL,
    78,
    $$medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.$$,
    $$[{"fuente": "https://move.ai", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 78, "riesgo_adversarial": "medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.", "criterio_inclusion": "Generacion de modelos 3D, text-to-3D, image-to-3D, texturizado, assets para juegos/VFX/arquitectura, markerless mocap y performance capture."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["3d_mocap_assets"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();

INSERT INTO catastro_vision_generativa (
    id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
    licensing_risk, consent_required,
    tier_seed, bonus_curador, bonus_curador_razon,
    score_subdominio_origen, riesgo_adversarial,
    fuentes_evidencia, validacion_adversarial, data_extra,
    confidence
) VALUES (
    'autodesk_flow_studio_ai_mocap',
    $$Autodesk Flow Studio AI MoCap$$,
    $$Autodesk$$,
    '3d_mocap_assets',
    '{}'::TEXT[],
    $$https://help.wonderdynamics.com/ai-mocap-system/$$,
    'low',
    False,
    1,
    0,
    NULL,
    78,
    $$medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.$$,
    $$[{"fuente": "https://help.wonderdynamics.com/ai-mocap-system/", "fecha": "2026-05-10", "validador": "Perplexity"}]$$::jsonb,
    $${"sabios": ["perplexity"], "consenso": "Validado por Perplexity adversarial sobre macro\u00e1rea VISION_GENERATIVA", "subdominio_origen_score": 78, "riesgo_adversarial": "medium: riesgos de topologia, rigging, PBR, exportacion limpia, compatibilidad DCC y derechos de assets.", "criterio_inclusion": "Generacion de modelos 3D, text-to-3D, image-to-3D, texturizado, assets para juegos/VFX/arquitectura, markerless mocap y performance capture."}$$::jsonb,
    $${"es_trono_de": [], "subdominios_aparece": ["3d_mocap_assets"]}$$::jsonb,
    0.85
)
ON CONFLICT (id) DO UPDATE SET
    subdominios_secundarios = EXCLUDED.subdominios_secundarios,
    bonus_curador = EXCLUDED.bonus_curador,
    bonus_curador_razon = EXCLUDED.bonus_curador_razon,
    data_extra = EXCLUDED.data_extra,
    updated_at = NOW();


COMMIT;

-- ----------------------------------------------------------------------------
-- 5) MATERIALIZED VIEW catastro_tronos_vision_generativa
--    DISTINCT ON subdominio, ordenado por score (fórmula soberana adaptada)
-- ----------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS catastro_tronos_vision_generativa CASCADE;

CREATE MATERIALIZED VIEW catastro_tronos_vision_generativa AS
SELECT DISTINCT ON (subdominio_primario)
    subdominio_primario AS subdominio,
    id AS trono_id,
    nombre AS trono_nombre,
    proveedor,
    tier_seed,
    open_weights,
    estado,
    licensing_risk,
    consent_required,
    bonus_curador,
    bonus_curador_razon,
    score_subdominio_origen,
    (
        (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
      + (CASE WHEN api_disponible THEN 15 ELSE 0 END)
      + (CASE WHEN mcp_server_disponible THEN 10 ELSE 0 END)
      + (CASE WHEN audio_nativo THEN 10 ELSE 0 END)
      + (CASE WHEN multi_shot_capable THEN 10 ELSE 0 END)
      + (CASE WHEN consistencia_personaje THEN 10 ELSE 0 END)
      + (CASE WHEN c2pa_provenance THEN 5 ELSE 0 END)
      + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
      + (CASE WHEN licensing_risk = 'low' THEN 5 ELSE 0 END)
      + bonus_curador
    ) AS score,
    now() AS calculado_at
FROM catastro_vision_generativa
ORDER BY subdominio_primario,
         (
            (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
          + (CASE WHEN api_disponible THEN 15 ELSE 0 END)
          + (CASE WHEN mcp_server_disponible THEN 10 ELSE 0 END)
          + (CASE WHEN audio_nativo THEN 10 ELSE 0 END)
          + (CASE WHEN multi_shot_capable THEN 10 ELSE 0 END)
          + (CASE WHEN consistencia_personaje THEN 10 ELSE 0 END)
          + (CASE WHEN c2pa_provenance THEN 5 ELSE 0 END)
          + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
          + (CASE WHEN licensing_risk = 'low' THEN 5 ELSE 0 END)
          + bonus_curador
         ) DESC,
         open_weights DESC, tier_seed ASC, id ASC;

CREATE UNIQUE INDEX idx_catastro_tronos_vision_generativa_subdominio
    ON catastro_tronos_vision_generativa (subdominio);

-- ----------------------------------------------------------------------------
-- 6) Verificación
-- ----------------------------------------------------------------------------
DO $$
DECLARE
  v_total INT;
  v_subdominios INT;
  v_tronos INT;
BEGIN
  SELECT COUNT(*) INTO v_total FROM catastro_vision_generativa;
  SELECT COUNT(DISTINCT subdominio_primario) INTO v_subdominios FROM catastro_vision_generativa;
  SELECT COUNT(*) INTO v_tronos FROM catastro_tronos_vision_generativa;

  RAISE NOTICE 'Sprint 88.3 VISION_GENERATIVA: % productos, % subdominios, % tronos',
    v_total, v_subdominios, v_tronos;

  IF v_subdominios <> 12 THEN
    RAISE EXCEPTION 'Esperado 12 subdominios, encontrados %', v_subdominios;
  END IF;
  IF v_tronos <> 12 THEN
    RAISE EXCEPTION 'Esperado 12 tronos, encontrados %', v_tronos;
  END IF;
END $$;

-- ============================================================================
-- FIN MIGRACION 040
-- ============================================================================
