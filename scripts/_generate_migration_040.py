#!/usr/bin/env python3
"""Genera 040_sprint88_3_vision_generativa.sql a partir del JSON de Perplexity.

Lee el archivo JSON con 12 sub-dominios y produce:
  1. CREATE TABLE catastro_vision_generativa con columnas específicas
  2. CHECK constraints (subdominio, licensing_risk, consent_required)
  3. INSERT de productos seed únicos (38 productos)
  4. UPDATE bonus_curador para tronos
  5. CREATE MATERIALIZED VIEW catastro_tronos_vision_generativa
"""
import json
import sys
from pathlib import Path
from textwrap import dedent

# Reglas de negocio para flags por subdominio
LICENSING_RISK_BY_SUBDOMINIO = {
    "musica_generada": "high",  # Suno/Udio: training data + publishing legalmente sensible
    "lip_sync_visual_dubbing": "medium",  # consentimiento + deepfake risk
    "avatar_humano_animado": "medium",  # consentimiento de identidad
    "realtime_video_agents_characters": "medium",  # identidad realtime
    "tts_voces_sinteticas": "medium",  # voice cloning
    "video_narrativo_cinematico": "medium",  # uso comercial sora 2 deprecation
    "imagen_estatica_premium": "low",
    "video_clip_generativo": "low",
    "efectos_sonido_sfx": "low",
    "generative_editing_inpainting": "low",
    "upscaling_restauracion_enhancement": "low",
    "3d_mocap_assets": "low",
}

CONSENT_REQUIRED_BY_SUBDOMINIO = {
    "avatar_humano_animado": True,
    "realtime_video_agents_characters": True,
    "lip_sync_visual_dubbing": True,
    "tts_voces_sinteticas": True,  # cuando hay clonación
    "musica_generada": False,  # no consent issue, sí licensing
    "video_narrativo_cinematico": False,
    "imagen_estatica_premium": False,
    "video_clip_generativo": False,
    "efectos_sonido_sfx": False,
    "generative_editing_inpainting": False,
    "upscaling_restauracion_enhancement": False,
    "3d_mocap_assets": False,
}

# Tronos por subdominio (del JSON Perplexity)
# Bonus_curador asignado: trono = 10, acompañante seed = 0
BONUS_TRONOS = {
    "midjourney_v7": (10, "Trono imagen_estatica_premium según Perplexity (validación adversarial). Midjourney v7 default desde 2025: precision de prompts, texturas, cuerpos, manos, Draft Mode + Omni Reference. Score subdominio 95/100."),
    "veo_3_1": (10, "Trono video_clip_generativo según Perplexity. Veo 3.1 genera clips 8s con audio nativo, referencias múltiples y video vertical (Gemini). Score subdominio 85/100. Acompañantes fuertes: Runway Gen-4.5 (top Artificial Analysis), Luma Ray2."),
    "runway_gen_4_5": (10, "Trono video_narrativo_cinematico según Perplexity. Runway Gen-4.5 top Artificial Analysis Text-to-Video benchmark (1247 Elo). Visual fidelity + prompt adherence + motion quality + creative control. Score subdominio 55/100 (no valida cine 60s+ nativo, solo workflow narrativo)."),
    "synthesia": (10, "Trono avatar_humano_animado según Perplexity. Synthesia 240+ stock avatars, avatar personal con consentimiento, voice cloning, escenas con Veo 3. Enterprise-grade. HeyGen como creator/localization Tier 1. Score subdominio 90/100."),
    "runway_characters": (10, "Trono realtime_video_agents_characters según Perplexity. Runway Characters: video agents en tiempo real con apariencia, voz, personalidad, conocimiento, acciones configurables. Dominio emergente estratégico. Score subdominio 68/100."),
    "sync_labs": (10, "Trono lip_sync_visual_dubbing según Perplexity. sync.labs API especializada en lipsync. Distinto a TTS y avatar: modifica boca sobre video existente. Score subdominio 82/100. Riesgos: consentimiento, deepfake, multi-speaker."),
    "elevenlabs_tts": (10, "Trono tts_voces_sinteticas según Perplexity. ElevenLabs biblioteca + clonación líder 2026. OpenAI/Inworld Tier 1 para realtime. Score subdominio 95/100. Requiere flags consent + voice cloning + uso comercial."),
    "suno_v5_5": (10, "Trono musica_generada según Perplexity. Suno v5.5 canción completa. Udio licensing strategic agreements UMG = challenger licenciado. Score subdominio 80/100. licensing_risk=high obligatorio."),
    "elevenlabs_sfx": (10, "Trono efectos_sonido_sfx según Perplexity. ElevenLabs SFX producto hosted. Stable Audio Open OSS Tier 1. Score subdominio 70/100 (menos maduro que music+TTS)."),
    "adobe_firefly_video_editor": (10, "Trono generative_editing_inpainting según Perplexity. Adobe Firefly Video Editor (Apr 2026) suite creativa para edición semántica. FLUX.2 + Runway Tier 1. Score subdominio 88/100."),
    "topaz_video": (10, "Trono upscaling_restauracion_enhancement según Perplexity. Topaz Video estándar de la industria para upscaling+restauración objetiva. Magnific Tier 1 para upscaling creativo multimodal. Score subdominio 86/100."),
    "meshy": (10, "Trono 3d_mocap_assets según Perplexity. Meshy text-to-3D + image-to-3D. Tripo Tier 1 challenger. Move AI + Autodesk Flow Studio para mocap. Score subdominio 78/100."),
}


def slugify(s: str) -> str:
    return s.replace("_", "-").replace(".", "").lower()


def main() -> int:
    candidates = [
        Path(__file__).parent / "_pasted_content_19.json",
        Path("/home/ubuntu/upload/pasted_content_19.txt"),
        Path("/mnt/desktop/el-monstruo/scripts/_pasted_content_19.json"),
    ]
    json_path = next((p for p in candidates if p.exists()), None)
    if not json_path:
        print("ERROR: No se encuentra pasted_content_19.txt", file=sys.stderr)
        return 1

    data = json.loads(json_path.read_text())

    # Recolectar productos únicos por id_slug (deduplicar)
    productos = {}  # id_slug -> dict
    subdominios_canonicos = []

    for sd in data:
        subdom = sd["subdominio"]
        subdominios_canonicos.append(subdom)
        trono_id = sd["trono_id"]
        for seed in sd["seeds"]:
            id_slug = seed["id_slug"]
            if id_slug not in productos:
                productos[id_slug] = {
                    "id_slug": id_slug,
                    "nombre": seed["nombre"],
                    "proveedor": seed["proveedor"],
                    "url": seed["url"],
                    "subdominios": [subdom],
                    "es_trono_de": [],
                    "score_subdominio_origen": sd["score"],
                    "criterio_de_inclusion": sd["criterio_de_inclusion"],
                    "riesgo_adversarial": sd["riesgo_adversarial"],
                }
            else:
                productos[id_slug]["subdominios"].append(subdom)
            if trono_id == id_slug:
                productos[id_slug]["es_trono_de"].append(subdom)

    # Asignar subdominio primario = primer subdominio en que aparece
    # (en el orden del JSON, se respeta orden canónico)

    # Generar SQL
    sql_parts = []

    sql_parts.append(dedent("""\
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
    """))

    # Generar INSERTs por producto
    for slug, p in productos.items():
        primario = p["subdominios"][0]
        secundarios = [s for s in p["subdominios"][1:] if s != primario]
        es_trono = bool(p["es_trono_de"])

        bonus = 0
        bonus_razon = "NULL"
        if slug in BONUS_TRONOS:
            bonus, razon = BONUS_TRONOS[slug]
            bonus_razon = "$$" + razon + "$$"

        licensing = LICENSING_RISK_BY_SUBDOMINIO.get(primario, "low")
        consent = CONSENT_REQUIRED_BY_SUBDOMINIO.get(primario, False)

        # Defaults conservadores por subdominio
        # No infiero más datos técnicos (duracion_max, resolucion, etc.) porque
        # Perplexity no los entregó. Quedan NULL para investigación posterior.
        sec_arr = "ARRAY[" + ",".join(f"'{s}'" for s in secundarios) + "]::TEXT[]" if secundarios else "'{}'::TEXT[]"
        evidencia = json.dumps([{"fuente": p["url"], "fecha": "2026-05-10", "validador": "Perplexity"}])
        validacion = json.dumps({
            "sabios": ["perplexity"],
            "consenso": "Validado por Perplexity adversarial sobre macroárea VISION_GENERATIVA",
            "subdominio_origen_score": p["score_subdominio_origen"],
            "riesgo_adversarial": p["riesgo_adversarial"],
            "criterio_inclusion": p["criterio_de_inclusion"],
        })
        data_extra = json.dumps({
            "es_trono_de": p["es_trono_de"],
            "subdominios_aparece": p["subdominios"],
        })

        sql_parts.append(dedent(f"""\
            INSERT INTO catastro_vision_generativa (
                id, nombre, proveedor, subdominio_primario, subdominios_secundarios, url_oficial,
                licensing_risk, consent_required,
                tier_seed, bonus_curador, bonus_curador_razon,
                score_subdominio_origen, riesgo_adversarial,
                fuentes_evidencia, validacion_adversarial, data_extra,
                confidence
            ) VALUES (
                '{slug}',
                $${p["nombre"]}$$,
                $${p["proveedor"]}$$,
                '{primario}',
                {sec_arr},
                $${p["url"]}$$,
                '{licensing}',
                {consent},
                1,
                {bonus},
                {bonus_razon},
                {p["score_subdominio_origen"]},
                $${p["riesgo_adversarial"]}$$,
                $${evidencia}$$::jsonb,
                $${validacion}$$::jsonb,
                $${data_extra}$$::jsonb,
                0.85
            )
            ON CONFLICT (id) DO UPDATE SET
                subdominios_secundarios = EXCLUDED.subdominios_secundarios,
                bonus_curador = EXCLUDED.bonus_curador,
                bonus_curador_razon = EXCLUDED.bonus_curador_razon,
                data_extra = EXCLUDED.data_extra,
                updated_at = NOW();
        """))

    # Vista materializada de tronos
    sql_parts.append(dedent("""\

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
    """))

    out_path = Path(__file__).parent / "040_sprint88_3_vision_generativa.sql"
    out_path.write_text("\n".join(sql_parts))
    print(f"✓ Generated {out_path.name} ({out_path.stat().st_size} bytes)")
    print(f"  Productos seed: {len(productos)}")
    print(f"  Subdominios: {len(set(subdominios_canonicos))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
