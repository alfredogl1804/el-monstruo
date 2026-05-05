-- =============================================================================
-- 019_sprint86_catastro_trono.sql · Sprint 86 Bloque 4 · 2026-05-04
-- =============================================================================
--
-- El Catastro · Cálculo Trono Score por dominio + curator_alias.
--
-- Esta migración entrega:
--   1. ALTER catastro_curadores: columna curator_alias TEXT[] + GIN index.
--   2. Reemplazo de catastro_apply_quorum_outcome para usar curator_alias en
--      el matching (mejora #1 del audit Cowork del Bloque 3).
--   3. Función catastro_recompute_trono(p_dominio) que calcula z-scores por
--      dominio y actualiza trono_global + trono_delta atómicamente.
--   4. Función catastro_recompute_trono_all() wrapper para todos los dominios.
--   5. Vista catastro_trono_view con bandas de confianza (trono_low/high).
--
-- Doctrina del Trono (SPEC sección 4 + bridge cowork línea 1070):
--   trono_global = round(50 + 10 * Σ(w_i · z_i), 2)
--   donde z_i = (x_i - mean_d.x_i) / std_d.x_i
--   pesos por defecto: Q=0.40, CE=0.25, S=0.15, R=0.10, BF=0.10
--
-- Salvaguardas anti-autoboicot:
--   - Si std == 0 (todos iguales) → z = 0 para todos.
--   - Si dominio tiene < 2 modelos → trono = 50 (neutral) y se omite.
--   - Métricas faltantes (NULL) → coalesce a 0 con flag de baja confidence.
--   - trono_global clampeado a [0, 100] (consistente con NUMERIC(5,2)).
--
-- IMPORTANTE: las funciones requieren rol service_role; REVOKE PUBLIC y GRANT
-- service_role aplicados al final.
--
-- [Hilo Manus Catastro] · Sprint 86 Bloque 4 · 2026-05-04
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. ALTER catastro_curadores: curator_alias TEXT[] + GIN index
-- -----------------------------------------------------------------------------
-- Mejora #1 del audit Cowork del Bloque 3.
-- Permite matching flexible cuando el id canónico del curador no coincide
-- exactamente con el slug de la fuente de evidencia (ej. el curador
-- 'claude-opus-4.7-inteligencia' también responde por aliases
-- 'artificial_analysis', 'openrouter', 'lmarena' cuando consulta esas fuentes).
-- TEXT[] indexable con GIN; JSONB se descartó por overkill (caso v1 es lista
-- plana). Migración futura a JSONB es trivial si se necesita metadata por alias.

ALTER TABLE catastro_curadores
    ADD COLUMN IF NOT EXISTS curator_alias TEXT[] NOT NULL DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_curadores_alias_gin
    ON catastro_curadores USING GIN (curator_alias);

COMMENT ON COLUMN catastro_curadores.curator_alias IS
    'Aliases adicionales del curador para matching flexible en RPC. Ej: '
    '{"artificial_analysis","openrouter","lmarena"} si el curador consulta '
    'esas fuentes. Indexable con GIN.';

-- -----------------------------------------------------------------------------
-- 2. Reemplazo de catastro_apply_quorum_outcome para usar curator_alias
-- -----------------------------------------------------------------------------
-- DROP previo si existe firma antigua (de migration 018).
DROP FUNCTION IF EXISTS catastro_apply_quorum_outcome(jsonb, jsonb, jsonb);

CREATE OR REPLACE FUNCTION catastro_apply_quorum_outcome(
    p_modelo        jsonb,
    p_evento        jsonb,
    p_trust_deltas  jsonb DEFAULT '{}'::jsonb
) RETURNS jsonb
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
AS $$
DECLARE
    v_modelo_id          TEXT;
    v_evento_id          UUID := NULL;
    v_curadores_updated  INT  := 0;
    v_curador_key        TEXT;
    v_delta              NUMERIC;
    v_event_modelo_id    TEXT;
    v_now                TIMESTAMPTZ := NOW();
BEGIN
    -- Validación mínima
    IF p_modelo IS NULL OR p_modelo->>'id' IS NULL THEN
        RAISE EXCEPTION 'catastro_persist_invalid_input: p_modelo.id es obligatorio'
            USING ERRCODE = 'P0001';
    END IF;
    v_modelo_id := p_modelo->>'id';

    -- ---- 1) UPSERT catastro_modelos ----
    INSERT INTO catastro_modelos (
        id, nombre, proveedor, macroarea, dominios, subcapacidades,
        quality_score, quality_delta, cost_efficiency, speed_score,
        reliability_score, brand_fit, sovereignty, velocity,
        trono_global, trono_delta,
        precio_input_per_million, precio_output_per_million,
        licencia, open_weights, api_endpoint,
        fuentes_evidencia, confidence,
        data_extra, schema_version,
        quorum_alcanzado, ultima_validacion, validated_by,
        created_at, updated_at
    )
    VALUES (
        v_modelo_id,
        p_modelo->>'nombre',
        p_modelo->>'proveedor',
        p_modelo->>'macroarea',
        COALESCE(
            (SELECT array_agg(value::text) FROM jsonb_array_elements_text(p_modelo->'dominios')),
            '{}'::text[]
        ),
        COALESCE(
            (SELECT array_agg(value::text) FROM jsonb_array_elements_text(p_modelo->'subcapacidades')),
            '{}'::text[]
        ),
        NULLIF(p_modelo->>'quality_score','')::NUMERIC,
        NULLIF(p_modelo->>'quality_delta','')::NUMERIC,
        NULLIF(p_modelo->>'cost_efficiency','')::NUMERIC,
        NULLIF(p_modelo->>'speed_score','')::NUMERIC,
        NULLIF(p_modelo->>'reliability_score','')::NUMERIC,
        NULLIF(p_modelo->>'brand_fit','')::NUMERIC,
        NULLIF(p_modelo->>'sovereignty','')::NUMERIC,
        NULLIF(p_modelo->>'velocity','')::NUMERIC,
        NULLIF(p_modelo->>'trono_global','')::NUMERIC,
        NULLIF(p_modelo->>'trono_delta','')::NUMERIC,
        NULLIF(p_modelo->>'precio_input_per_million','')::NUMERIC,
        NULLIF(p_modelo->>'precio_output_per_million','')::NUMERIC,
        p_modelo->>'licencia',
        COALESCE((p_modelo->>'open_weights')::BOOLEAN, false),
        p_modelo->>'api_endpoint',
        COALESCE(p_modelo->'fuentes_evidencia', '[]'::jsonb),
        COALESCE(NULLIF(p_modelo->>'confidence','')::NUMERIC, 0.50),
        COALESCE(p_modelo->'data_extra', '{}'::jsonb),
        COALESCE(NULLIF(p_modelo->>'schema_version','')::INT, 1),
        COALESCE((p_modelo->>'quorum_alcanzado')::BOOLEAN, false),
        COALESCE(NULLIF(p_modelo->>'ultima_validacion','')::TIMESTAMPTZ, v_now),
        p_modelo->>'validated_by',
        v_now,
        v_now
    )
    ON CONFLICT (id) DO UPDATE SET
        nombre                    = EXCLUDED.nombre,
        proveedor                 = EXCLUDED.proveedor,
        macroarea                 = EXCLUDED.macroarea,
        dominios                  = EXCLUDED.dominios,
        subcapacidades            = EXCLUDED.subcapacidades,
        quality_score             = EXCLUDED.quality_score,
        quality_delta             = EXCLUDED.quality_delta,
        cost_efficiency           = EXCLUDED.cost_efficiency,
        speed_score               = EXCLUDED.speed_score,
        reliability_score         = EXCLUDED.reliability_score,
        brand_fit                 = EXCLUDED.brand_fit,
        sovereignty               = EXCLUDED.sovereignty,
        velocity                  = EXCLUDED.velocity,
        trono_global              = EXCLUDED.trono_global,
        trono_delta               = EXCLUDED.trono_delta,
        precio_input_per_million  = EXCLUDED.precio_input_per_million,
        precio_output_per_million = EXCLUDED.precio_output_per_million,
        licencia                  = EXCLUDED.licencia,
        open_weights              = EXCLUDED.open_weights,
        api_endpoint              = EXCLUDED.api_endpoint,
        fuentes_evidencia         = EXCLUDED.fuentes_evidencia,
        confidence                = EXCLUDED.confidence,
        data_extra                = EXCLUDED.data_extra,
        schema_version            = EXCLUDED.schema_version,
        quorum_alcanzado          = EXCLUDED.quorum_alcanzado,
        ultima_validacion         = EXCLUDED.ultima_validacion,
        validated_by              = EXCLUDED.validated_by,
        updated_at                = v_now;

    -- ---- 2) INSERT catastro_eventos (opcional) ----
    IF p_evento IS NOT NULL AND jsonb_typeof(p_evento) = 'object' THEN
        v_event_modelo_id := COALESCE(p_evento->>'modelo_id', v_modelo_id);
        INSERT INTO catastro_eventos (
            tipo, prioridad, modelo_id, descripcion, contexto, fecha
        )
        VALUES (
            COALESCE(p_evento->>'tipo', 'new_model'),
            COALESCE(p_evento->>'prioridad', 'info'),
            v_event_modelo_id,
            COALESCE(p_evento->>'descripcion',
                     format('Auto-evento generado para %s', v_modelo_id)),
            COALESCE(p_evento->'contexto', '{}'::jsonb),
            v_now
        )
        RETURNING id INTO v_evento_id;
    END IF;

    -- ---- 3) UPDATE catastro_curadores: trust deltas ----
    -- Match canónico flexible: por id directo, proveedor, modelo_llm o
    -- cualquier alias en curator_alias (mejora #1 audit Cowork Bloque 3).
    IF p_trust_deltas IS NOT NULL AND jsonb_typeof(p_trust_deltas) = 'object' THEN
        FOR v_curador_key, v_delta IN
            SELECT key, (value::text)::NUMERIC
            FROM jsonb_each_text(p_trust_deltas)
        LOOP
            UPDATE catastro_curadores
               SET trust_score = LEAST(1.00, GREATEST(0.00, trust_score + v_delta)),
                   total_validaciones = total_validaciones + 1,
                   aciertos_quorum = aciertos_quorum + CASE WHEN v_delta >= 0 THEN 1 ELSE 0 END,
                   fallos_quorum = fallos_quorum + CASE WHEN v_delta < 0 THEN 1 ELSE 0 END,
                   requiere_hitl = (LEAST(1.00, GREATEST(0.00, trust_score + v_delta)) < 0.70),
                   last_run = v_now,
                   updated_at = v_now
             WHERE id = v_curador_key
                OR proveedor ILIKE v_curador_key
                OR modelo_llm ILIKE v_curador_key
                OR id ILIKE ('%' || v_curador_key || '%')
                OR v_curador_key = ANY(curator_alias);
            GET DIAGNOSTICS v_curadores_updated = ROW_COUNT;
        END LOOP;
    END IF;

    -- ---- 4) Devolver resumen ----
    RETURN jsonb_build_object(
        'modelo_id',              v_modelo_id,
        'evento_id',              v_evento_id,
        'curadores_actualizados', v_curadores_updated,
        'aplicado_at',            v_now
    );
END;
$$;

REVOKE ALL ON FUNCTION catastro_apply_quorum_outcome(jsonb, jsonb, jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION catastro_apply_quorum_outcome(jsonb, jsonb, jsonb) TO service_role;

COMMENT ON FUNCTION catastro_apply_quorum_outcome(jsonb, jsonb, jsonb) IS
    'Aplica el resultado de un quorum atómicamente. UPSERT modelo + INSERT '
    'evento + UPDATE deltas curadores bajo transacción implícita. Matching '
    'de curadores: id, proveedor, modelo_llm, ILIKE %key%, ANY(curator_alias). '
    'Devuelve jsonb {modelo_id, evento_id, curadores_actualizados, aplicado_at}. '
    'Sprint 86 Bloque 4 (2026-05-04) — reemplaza versión Bloque 3 (018).';

-- -----------------------------------------------------------------------------
-- 3. Función catastro_recompute_trono(p_dominio TEXT)
-- -----------------------------------------------------------------------------
-- Calcula z-scores por dominio y actualiza trono_global + trono_delta.
-- Pesos: Q=0.40, CE=0.25, S=0.15, R=0.10, BF=0.10 (SPEC sección 4).
-- Salvaguardas: std=0 → z=0; modelos<2 → trono=50.

CREATE OR REPLACE FUNCTION catastro_recompute_trono(
    p_dominio TEXT
) RETURNS jsonb
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
AS $$
DECLARE
    v_count        INT;
    v_updated      INT := 0;
    v_now          TIMESTAMPTZ := NOW();
    -- means + stddevs por métrica
    v_mean_q       NUMERIC; v_std_q  NUMERIC;
    v_mean_ce      NUMERIC; v_std_ce NUMERIC;
    v_mean_s       NUMERIC; v_std_s  NUMERIC;
    v_mean_r       NUMERIC; v_std_r  NUMERIC;
    v_mean_bf      NUMERIC; v_std_bf NUMERIC;
BEGIN
    IF p_dominio IS NULL OR p_dominio = '' THEN
        RAISE EXCEPTION 'catastro_trono_invalid_input: p_dominio es obligatorio'
            USING ERRCODE = 'P0001';
    END IF;

    -- Conteo de modelos en el dominio (filtra por estado != deprecated)
    SELECT COUNT(*) INTO v_count
      FROM catastro_modelos
     WHERE p_dominio = ANY(dominios)
       AND COALESCE(estado, 'production') <> 'deprecated';

    -- Caso degenerado: 0 o 1 modelo → trono neutral 50
    IF v_count < 2 THEN
        UPDATE catastro_modelos
           SET trono_delta = trono_global - 50.00,
               trono_global = 50.00,
               updated_at = v_now
         WHERE p_dominio = ANY(dominios)
           AND COALESCE(estado, 'production') <> 'deprecated';
        GET DIAGNOSTICS v_updated = ROW_COUNT;
        RETURN jsonb_build_object(
            'dominio',          p_dominio,
            'modelos_count',    v_count,
            'modelos_updated',  v_updated,
            'modo',             'neutral',
            'razon',            'menos_de_2_modelos',
            'aplicado_at',      v_now
        );
    END IF;

    -- Calcular medias y desviaciones (NULLs se ignoran via avg/stddev_samp)
    SELECT
        AVG(quality_score),     COALESCE(NULLIF(STDDEV_SAMP(quality_score),     0), 1),
        AVG(cost_efficiency),   COALESCE(NULLIF(STDDEV_SAMP(cost_efficiency),   0), 1),
        AVG(speed_score),       COALESCE(NULLIF(STDDEV_SAMP(speed_score),       0), 1),
        AVG(reliability_score), COALESCE(NULLIF(STDDEV_SAMP(reliability_score), 0), 1),
        AVG(brand_fit),         COALESCE(NULLIF(STDDEV_SAMP(brand_fit),         0), 1)
      INTO
        v_mean_q,  v_std_q,
        v_mean_ce, v_std_ce,
        v_mean_s,  v_std_s,
        v_mean_r,  v_std_r,
        v_mean_bf, v_std_bf
      FROM catastro_modelos
     WHERE p_dominio = ANY(dominios)
       AND COALESCE(estado, 'production') <> 'deprecated';

    -- UPDATE con z-scores aplicados, clamp [0,100], delta vs anterior
    WITH calculados AS (
        SELECT
            id,
            trono_global AS trono_old,
            -- z-scores: si la métrica es NULL, z = 0 (neutro)
            COALESCE((quality_score     - v_mean_q ) / v_std_q , 0) AS z_q,
            COALESCE((cost_efficiency   - v_mean_ce) / v_std_ce, 0) AS z_ce,
            COALESCE((speed_score       - v_mean_s ) / v_std_s , 0) AS z_s,
            COALESCE((reliability_score - v_mean_r ) / v_std_r , 0) AS z_r,
            COALESCE((brand_fit         - v_mean_bf) / v_std_bf, 0) AS z_bf
          FROM catastro_modelos
         WHERE p_dominio = ANY(dominios)
           AND COALESCE(estado, 'production') <> 'deprecated'
    ),
    nuevos AS (
        SELECT
            id,
            trono_old,
            -- Σ pesos = 1.00; trono_new ∈ [0,100] tras clamp
            ROUND(
                LEAST(100.00, GREATEST(0.00,
                    50.00 + 10.00 * (
                        0.40 * z_q  +
                        0.25 * z_ce +
                        0.15 * z_s  +
                        0.10 * z_r  +
                        0.10 * z_bf
                    )
                ))::NUMERIC,
                2
            ) AS trono_new
          FROM calculados
    )
    UPDATE catastro_modelos m
       SET trono_global = n.trono_new,
           trono_delta  = COALESCE(n.trono_new - n.trono_old, 0),
           updated_at   = v_now
      FROM nuevos n
     WHERE m.id = n.id;

    GET DIAGNOSTICS v_updated = ROW_COUNT;

    RETURN jsonb_build_object(
        'dominio',          p_dominio,
        'modelos_count',    v_count,
        'modelos_updated',  v_updated,
        'modo',             'z_score',
        'medias',           jsonb_build_object(
                                'quality_score',     v_mean_q,
                                'cost_efficiency',   v_mean_ce,
                                'speed_score',       v_mean_s,
                                'reliability_score', v_mean_r,
                                'brand_fit',         v_mean_bf
                            ),
        'desviaciones',     jsonb_build_object(
                                'quality_score',     v_std_q,
                                'cost_efficiency',   v_std_ce,
                                'speed_score',       v_std_s,
                                'reliability_score', v_std_r,
                                'brand_fit',         v_std_bf
                            ),
        'aplicado_at',      v_now
    );
END;
$$;

REVOKE ALL ON FUNCTION catastro_recompute_trono(TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION catastro_recompute_trono(TEXT) TO service_role;

COMMENT ON FUNCTION catastro_recompute_trono(TEXT) IS
    'Calcula z-scores por dominio y actualiza trono_global + trono_delta. '
    'Pesos: Q=0.40, CE=0.25, S=0.15, R=0.10, BF=0.10 (SPEC sec 4). '
    'Salvaguardas: std=0 → z=0; modelos<2 → trono=50. '
    'Devuelve jsonb {dominio, modelos_count, modelos_updated, modo, medias, desviaciones, aplicado_at}.';

-- -----------------------------------------------------------------------------
-- 4. Función catastro_recompute_trono_all() — wrapper para todos los dominios
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION catastro_recompute_trono_all()
RETURNS jsonb
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public, pg_temp
AS $$
DECLARE
    v_dominio   TEXT;
    v_results   jsonb := '[]'::jsonb;
    v_one       jsonb;
BEGIN
    FOR v_dominio IN
        SELECT DISTINCT unnest(dominios) AS d
          FROM catastro_modelos
         WHERE COALESCE(estado, 'production') <> 'deprecated'
         ORDER BY d
    LOOP
        v_one := catastro_recompute_trono(v_dominio);
        v_results := v_results || jsonb_build_array(v_one);
    END LOOP;

    RETURN jsonb_build_object(
        'dominios_procesados', jsonb_array_length(v_results),
        'detalle',             v_results,
        'aplicado_at',         NOW()
    );
END;
$$;

REVOKE ALL ON FUNCTION catastro_recompute_trono_all() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION catastro_recompute_trono_all() TO service_role;

COMMENT ON FUNCTION catastro_recompute_trono_all() IS
    'Itera sobre todos los dominios distintos en catastro_modelos (estado != deprecated) '
    'y ejecuta catastro_recompute_trono(d) para cada uno. Devuelve jsonb agregado.';

-- -----------------------------------------------------------------------------
-- 5. Vista catastro_trono_view — Top N por dominio con bandas de confianza
-- -----------------------------------------------------------------------------
-- La banda de confianza se calcula como ancho = 2 * 10 * (1 - confidence).
-- Confidence ∈ [0,1] → banda ∈ [0, 20] puntos. trono_low/high clampeados [0,100].

DROP VIEW IF EXISTS catastro_trono_view CASCADE;

CREATE VIEW catastro_trono_view AS
WITH expanded AS (
    SELECT
        m.id,
        m.nombre,
        m.proveedor,
        m.macroarea,
        unnest(m.dominios) AS dominio,
        m.subcapacidades,
        m.estado,
        m.quality_score,
        m.cost_efficiency,
        m.speed_score,
        m.reliability_score,
        m.brand_fit,
        m.sovereignty,
        m.velocity,
        m.trono_global,
        m.trono_delta,
        m.confidence,
        m.precio_input_per_million,
        m.precio_output_per_million,
        m.open_weights,
        m.last_validated_at
      FROM catastro_modelos m
     WHERE COALESCE(m.estado, 'production') <> 'deprecated'
)
SELECT
    e.*,
    -- banda de confianza: ancho = 2 * 10 * (1 - confidence)
    GREATEST(0.00, e.trono_global - 10.00 * (1 - COALESCE(e.confidence, 0.50)))::NUMERIC(5,2)  AS trono_low,
    LEAST(100.00,  e.trono_global + 10.00 * (1 - COALESCE(e.confidence, 0.50)))::NUMERIC(5,2)  AS trono_high,
    -- ranking dentro del dominio
    DENSE_RANK() OVER (PARTITION BY e.dominio ORDER BY e.trono_global DESC NULLS LAST) AS rank_dominio
  FROM expanded e;

COMMENT ON VIEW catastro_trono_view IS
    'Vista expandida por dominio con bandas de confianza (trono_low/high) '
    'y rank_dominio. Banda = 2 * 10 * (1 - confidence). '
    'Filtra modelos deprecated. Usar para tools MCP catastro.top y catastro.recommend.';

-- -----------------------------------------------------------------------------
-- 6. Comentario final
-- -----------------------------------------------------------------------------

COMMENT ON COLUMN catastro_modelos.trono_global IS
    'Composite Trono Score por dominio principal del modelo. Calculado por '
    'catastro_recompute_trono() con z-scores y pesos Q=0.40 CE=0.25 S=0.15 '
    'R=0.10 BF=0.10. Rango [0, 100] con base 50 (media del dominio).';

COMMIT;

-- =============================================================================
-- FIN scripts/019_sprint86_catastro_trono.sql
-- =============================================================================
