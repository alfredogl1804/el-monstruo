#!/usr/bin/env bash
# Queries Fase 2 Cowork (audit roadmap) — Sprint 87 prep
# Usa SUPABASE_DB_URL ya exportada en el environment.
set -uo pipefail

OUT=/tmp/cowork_fase2_output.txt
> "$OUT"

run() {
    local label="$1"
    local sql="$2"
    {
        echo "=== ${label} ==="
        psql "$SUPABASE_DB_URL" -A -t -c "$sql"
        echo
    } >> "$OUT"
}

run_pretty() {
    local label="$1"
    local sql="$2"
    {
        echo "=== ${label} ==="
        psql "$SUPABASE_DB_URL" -c "$sql"
        echo
    } >> "$OUT"
}

# Q1-equiv (endpoint degraded en prod, hago SQL equivalente)
run "Q1_top10_reliability_quorum" \
    "SELECT json_agg(row_to_json(r)) FROM (
        SELECT id, nombre, proveedor,
               round(trono_global::numeric,2) AS trono_global,
               reliability_score,
               jsonb_array_length(fuentes_evidencia) AS fuentes_count
        FROM catastro_modelos
        WHERE quorum_alcanzado=true
        ORDER BY reliability_score DESC NULLS LAST, trono_global DESC
        LIMIT 10
     ) r;"

# Q2-equiv
run "Q2_top10_cost_efficiency" \
    "SELECT json_agg(row_to_json(r)) FROM (
        SELECT id, nombre, proveedor,
               round(trono_global::numeric,2) AS trono_global,
               cost_efficiency,
               precio_input_per_million,
               precio_output_per_million
        FROM catastro_modelos
        ORDER BY cost_efficiency DESC NULLS LAST, trono_global DESC
        LIMIT 10
     ) r;"

# Q3
run "Q3_casos_uso_poblado" \
    "SELECT json_agg(row_to_json(r)) FROM (
        SELECT id, nombre, proveedor,
               round(trono_global::numeric,2) AS trono_global,
               casos_uso_recomendados_monstruo
        FROM catastro_modelos
        WHERE array_length(casos_uso_recomendados_monstruo,1) > 0
          AND quorum_alcanzado=true
        ORDER BY trono_global DESC
        LIMIT 15
     ) r;"

# Q3-conteo agregado
run_pretty "Q3_conteo_casos_uso" \
    "SELECT
        COALESCE(array_length(casos_uso_recomendados_monstruo,1), 0) AS casos_uso_count,
        COUNT(*) AS modelos
     FROM catastro_modelos
     GROUP BY casos_uso_count
     ORDER BY casos_uso_count;"

# Q4
run_pretty "Q4_distribucion_fuentes" \
    "SELECT jsonb_array_length(fuentes_evidencia) AS fuentes_count,
            COUNT(*) AS modelos
     FROM catastro_modelos
     GROUP BY fuentes_count
     ORDER BY fuentes_count DESC;"

# EXTRAS
run_pretty "EXTRA_por_proveedor" \
    "SELECT proveedor, COUNT(*) AS modelos
     FROM catastro_modelos
     GROUP BY proveedor
     ORDER BY modelos DESC;"

run_pretty "EXTRA_cobertura_columnas" \
    "SELECT COUNT(*) AS total,
            COUNT(quality_score) AS q_score,
            COUNT(reliability_score) AS r_score,
            COUNT(cost_efficiency) AS c_eff,
            COUNT(speed_score) AS s_score,
            COUNT(precio_input_per_million) AS p_in,
            COUNT(precio_output_per_million) AS p_out,
            COUNT(api_endpoint) AS api,
            COUNT(licencia) AS licencia,
            COUNT(curador_responsable) AS curador
     FROM catastro_modelos;"

run_pretty "EXTRA_dominios_distribucion" \
    "SELECT unnest(dominios) AS dominio, COUNT(*)
     FROM catastro_modelos
     GROUP BY dominio
     ORDER BY 2 DESC;"

cat "$OUT"
