-- ============================================================================
-- Sprint 86 Bloque 3 · El Catastro · RPC de persistencia atómica
-- ============================================================================
--
-- Razón de ser:
--   supabase-py 2.29.0 (PostgREST stateless) NO soporta transacciones HTTP.
--   Las 3 operaciones del Catastro (UPSERT modelo + INSERT evento +
--   UPDATE deltas de curadores) DEBEN ejecutarse atómicamente para evitar
--   estados parciales (modelo persistido sin evento, curadores actualizados
--   pero modelo no, etc.).
--
--   La única forma de garantizar atomicidad real con supabase-py es
--   delegar a una función PL/pgSQL que se ejecute en una transacción
--   única del lado del servidor. Eso es exactamente lo que hace
--   `catastro_apply_quorum_outcome`.
--
-- Memento (decisiones contextuales, anti-Dory):
--   1. Idempotencia por p_modelo->>'id' usando UPSERT ON CONFLICT(id).
--   2. p_evento es libre (UUID generado del lado cliente o por DEFAULT).
--   3. p_trust_deltas es jsonb { "fuente": delta_float } y se aplica
--      con UPDATE acumulativo (trust_score = clamp(trust_score + delta, 0, 1)).
--   4. La función NO falla silenciosamente — cualquier error rompe la
--      transacción y devuelve SQLSTATE al cliente.
--   5. Devuelve jsonb con resumen para que el cliente loggee.
--
-- Idempotencia y reintentos:
--   - Si un run del cron se interrumpe a mitad, el siguiente run aplica
--     UPSERT idempotente (mismo id → mismos campos). Los eventos NO son
--     idempotentes (cada llamada inserta un nuevo evento), por eso el
--     pipeline.py controla cuándo llamar a la RPC.
--
-- [Hilo Manus Catastro] · Sprint 86 Bloque 3 · 2026-05-04
-- ============================================================================

CREATE OR REPLACE FUNCTION catastro_apply_quorum_outcome(
    p_modelo jsonb,
    p_evento jsonb,
    p_trust_deltas jsonb DEFAULT '{}'::jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    v_modelo_id text;
    v_evento_id uuid;
    v_curadores_actualizados integer := 0;
    v_curador_key text;
    v_curador_delta numeric;
    v_curador_match_id text;
BEGIN
    -- Validación básica de inputs
    IF p_modelo IS NULL OR p_modelo->>'id' IS NULL THEN
        RAISE EXCEPTION 'catastro_apply_quorum_outcome: p_modelo->>id es obligatorio';
    END IF;

    v_modelo_id := p_modelo->>'id';

    -- ----------------------------------------------------------------
    -- 1. UPSERT catastro_modelos (idempotente por id)
    -- ----------------------------------------------------------------
    INSERT INTO catastro_modelos (
        id, nombre, proveedor,
        macroarea, dominios, subcapacidades,
        estado, tipo, licencia, open_weights, api_endpoint,
        quality_score, quality_delta,
        cost_efficiency, speed_score, reliability_score,
        brand_fit, sovereignty, velocity,
        trono_global, trono_delta, rank_dominio,
        precio_input_per_million, precio_output_per_million,
        capacidades_tecnicas, velocidad,
        limitaciones, fortalezas, debilidades,
        casos_uso_recomendados_monstruo,
        fuentes_evidencia, quorum_alcanzado, confidence,
        curador_responsable,
        data_extra, schema_version,
        ultima_validacion, proxima_revalidacion
    )
    VALUES (
        v_modelo_id,
        p_modelo->>'nombre',
        p_modelo->>'proveedor',
        COALESCE(p_modelo->>'macroarea', 'inteligencia'),
        COALESCE((p_modelo->'dominios')::jsonb, '[]'::jsonb),
        COALESCE((p_modelo->'subcapacidades')::jsonb, '[]'::jsonb),
        COALESCE(p_modelo->>'estado', 'production'),
        COALESCE(p_modelo->>'tipo', 'propietario'),
        p_modelo->>'licencia',
        COALESCE((p_modelo->>'open_weights')::boolean, false),
        p_modelo->>'api_endpoint',
        NULLIF(p_modelo->>'quality_score', '')::numeric,
        NULLIF(p_modelo->>'quality_delta', '')::numeric,
        NULLIF(p_modelo->>'cost_efficiency', '')::numeric,
        NULLIF(p_modelo->>'speed_score', '')::numeric,
        NULLIF(p_modelo->>'reliability_score', '')::numeric,
        NULLIF(p_modelo->>'brand_fit', '')::numeric,
        NULLIF(p_modelo->>'sovereignty', '')::numeric,
        NULLIF(p_modelo->>'velocity', '')::numeric,
        NULLIF(p_modelo->>'trono_global', '')::numeric,
        NULLIF(p_modelo->>'trono_delta', '')::numeric,
        NULLIF(p_modelo->>'rank_dominio', '')::integer,
        NULLIF(p_modelo->>'precio_input_per_million', '')::numeric,
        NULLIF(p_modelo->>'precio_output_per_million', '')::numeric,
        COALESCE((p_modelo->'capacidades_tecnicas')::jsonb, '{}'::jsonb),
        COALESCE((p_modelo->'velocidad')::jsonb, '{}'::jsonb),
        COALESCE((p_modelo->'limitaciones')::jsonb, '[]'::jsonb),
        COALESCE((p_modelo->'fortalezas')::jsonb, '[]'::jsonb),
        COALESCE((p_modelo->'debilidades')::jsonb, '[]'::jsonb),
        COALESCE((p_modelo->'casos_uso_recomendados_monstruo')::jsonb, '[]'::jsonb),
        COALESCE((p_modelo->'fuentes_evidencia')::jsonb, '[]'::jsonb),
        COALESCE((p_modelo->>'quorum_alcanzado')::boolean, false),
        COALESCE((p_modelo->>'confidence')::numeric, 0.50),
        p_modelo->>'curador_responsable',
        COALESCE((p_modelo->'data_extra')::jsonb, '{}'::jsonb),
        COALESCE((p_modelo->>'schema_version')::integer, 1),
        COALESCE(NULLIF(p_modelo->>'ultima_validacion', '')::timestamptz, NOW()),
        NULLIF(p_modelo->>'proxima_revalidacion', '')::timestamptz
    )
    ON CONFLICT (id) DO UPDATE SET
        nombre                            = EXCLUDED.nombre,
        proveedor                         = EXCLUDED.proveedor,
        macroarea                         = EXCLUDED.macroarea,
        dominios                          = EXCLUDED.dominios,
        subcapacidades                    = EXCLUDED.subcapacidades,
        estado                            = EXCLUDED.estado,
        tipo                              = EXCLUDED.tipo,
        licencia                          = EXCLUDED.licencia,
        open_weights                      = EXCLUDED.open_weights,
        api_endpoint                      = EXCLUDED.api_endpoint,
        quality_score                     = EXCLUDED.quality_score,
        quality_delta                     = EXCLUDED.quality_delta,
        cost_efficiency                   = EXCLUDED.cost_efficiency,
        speed_score                       = EXCLUDED.speed_score,
        reliability_score                 = EXCLUDED.reliability_score,
        brand_fit                         = EXCLUDED.brand_fit,
        sovereignty                       = EXCLUDED.sovereignty,
        velocity                          = EXCLUDED.velocity,
        trono_global                      = EXCLUDED.trono_global,
        trono_delta                       = EXCLUDED.trono_delta,
        rank_dominio                      = EXCLUDED.rank_dominio,
        precio_input_per_million          = EXCLUDED.precio_input_per_million,
        precio_output_per_million         = EXCLUDED.precio_output_per_million,
        capacidades_tecnicas              = EXCLUDED.capacidades_tecnicas,
        velocidad                         = EXCLUDED.velocidad,
        limitaciones                      = EXCLUDED.limitaciones,
        fortalezas                        = EXCLUDED.fortalezas,
        debilidades                       = EXCLUDED.debilidades,
        casos_uso_recomendados_monstruo   = EXCLUDED.casos_uso_recomendados_monstruo,
        fuentes_evidencia                 = EXCLUDED.fuentes_evidencia,
        quorum_alcanzado                  = EXCLUDED.quorum_alcanzado,
        confidence                        = EXCLUDED.confidence,
        curador_responsable               = EXCLUDED.curador_responsable,
        data_extra                        = EXCLUDED.data_extra,
        schema_version                    = EXCLUDED.schema_version,
        ultima_validacion                 = EXCLUDED.ultima_validacion,
        proxima_revalidacion              = EXCLUDED.proxima_revalidacion,
        updated_at                        = NOW();

    -- ----------------------------------------------------------------
    -- 2. INSERT catastro_eventos
    -- ----------------------------------------------------------------
    IF p_evento IS NOT NULL AND p_evento <> '{}'::jsonb THEN
        INSERT INTO catastro_eventos (
            id, fecha, tipo, prioridad, modelo_id,
            descripcion, contexto, notificado, curador_origen
        )
        VALUES (
            COALESCE(NULLIF(p_evento->>'id', '')::uuid, gen_random_uuid()),
            COALESCE(NULLIF(p_evento->>'fecha', '')::timestamptz, NOW()),
            COALESCE(p_evento->>'tipo', 'new_model'),
            COALESCE(p_evento->>'prioridad', 'info'),
            COALESCE(p_evento->>'modelo_id', v_modelo_id),
            COALESCE(p_evento->>'descripcion', 'Quorum outcome aplicado por el Catastro'),
            COALESCE((p_evento->'contexto')::jsonb, '{}'::jsonb),
            COALESCE((p_evento->>'notificado')::boolean, false),
            p_evento->>'curador_origen'
        )
        RETURNING id INTO v_evento_id;
    END IF;

    -- ----------------------------------------------------------------
    -- 3. UPDATE deltas en catastro_curadores
    --    p_trust_deltas = { "artificial_analysis": -0.05, "openrouter": 0.0, ... }
    --    Buscamos curador por proveedor matcheable (LIKE) o id directo.
    -- ----------------------------------------------------------------
    IF p_trust_deltas IS NOT NULL AND p_trust_deltas <> '{}'::jsonb THEN
        FOR v_curador_key, v_curador_delta IN
            SELECT key, value::text::numeric
            FROM jsonb_each(p_trust_deltas)
        LOOP
            -- Match canónico: id exacto o proveedor que contiene la fuente
            SELECT id INTO v_curador_match_id
            FROM catastro_curadores
            WHERE id = v_curador_key
               OR lower(proveedor) = lower(v_curador_key)
               OR lower(modelo_llm) LIKE lower('%' || v_curador_key || '%')
            LIMIT 1;

            IF v_curador_match_id IS NOT NULL THEN
                UPDATE catastro_curadores
                SET trust_score = LEAST(1.0, GREATEST(0.0, trust_score + v_curador_delta)),
                    total_validaciones = total_validaciones + 1,
                    aciertos_quorum = aciertos_quorum + CASE WHEN v_curador_delta >= 0 THEN 1 ELSE 0 END,
                    fallos_quorum   = fallos_quorum   + CASE WHEN v_curador_delta <  0 THEN 1 ELSE 0 END,
                    last_run = NOW(),
                    updated_at = NOW()
                WHERE id = v_curador_match_id;

                v_curadores_actualizados := v_curadores_actualizados + 1;
            END IF;
        END LOOP;
    END IF;

    -- ----------------------------------------------------------------
    -- 4. Resultado
    -- ----------------------------------------------------------------
    RETURN jsonb_build_object(
        'modelo_id',                v_modelo_id,
        'evento_id',                v_evento_id,
        'curadores_actualizados',   v_curadores_actualizados,
        'aplicado_at',              NOW()
    );
END;
$$;

-- ============================================================================
-- Permisos: solo service_role puede ejecutarla.
-- (anon y authenticated NO deben tocar el Catastro directamente)
-- ============================================================================
REVOKE ALL ON FUNCTION catastro_apply_quorum_outcome(jsonb, jsonb, jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION catastro_apply_quorum_outcome(jsonb, jsonb, jsonb) TO service_role;

-- ============================================================================
-- Smoke test manual (para correr desde el SQL editor de Supabase):
-- ============================================================================
-- SELECT catastro_apply_quorum_outcome(
--     '{"id": "test-modelo-rpc", "nombre": "Test", "proveedor": "test"}'::jsonb,
--     '{"tipo": "new_model", "prioridad": "info", "descripcion": "smoke test"}'::jsonb,
--     '{"artificial_analysis": 0.0, "openrouter": -0.05}'::jsonb
-- );
