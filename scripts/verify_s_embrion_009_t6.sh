#!/usr/bin/env bash
# =============================================================================
# Sprint S-EMBRION-009 — Tarea T6
# Verificación binaria 24h post-merge T5 backfill 0049
# =============================================================================
#
# Owner: Manus E2
# Fecha entrega: 2026-05-18 ~06:30 UTC (día 0)
# Fecha objetivo de ejecución: 2026-05-19 ~06:30 UTC (día +1, 24h post-T5)
#
# Pre-requisitos:
#   - PR #151 mergeado (commit 473dfa06) — VERIFICADO 2026-05-18 06:30 UTC
#   - Migration 0049 aplicada en prod via MCP — VERIFICADO baseline 21→7+14
#   - Embrion loop deployado en Railway con código de T2/T3/T4 (PR #143)
#   - El sistema corrió 24h con la nueva heurística sin re-detección
#
# Métricas binarias (todas deben ser TRUE para declarar Sprint GREEN):
#
#   M1: 0 logs `embrion_trigger_detected mensaje_alfredo` repetidos con mismo
#       message_id en ventana 24h post-merge
#   M2: count(*) FROM embrion_memoria WHERE consumed_at IS NULL AND
#       tipo='mensaje_alfredo' AND created_at < NOW() - INTERVAL '1 hour'
#       debe ser <= 5 (umbral watchdog)
#   M3: count(*) de mensaje_alfredo con consumed_at NOT NULL debe ser
#       monotónicamente creciente (sin reverts/revivals)
#
# Si M1, M2, M3 verdes → Sprint S-EMBRION-009 GREEN definitivo.
# Si alguno rojo → revertir backfill (comando documentado en 0049 comments) +
#                  diagnóstico binario antes de redeploy.
# =============================================================================

set -euo pipefail

echo "============================================================"
echo "S-EMBRION-009 T6 — Verificación 24h binaria"
echo "Fecha ejecución: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"
echo ""

# -----------------------------------------------------------------------------
# M2 + M3: Queries Supabase via MCP supabase-monstruo
# -----------------------------------------------------------------------------
# Estas queries se ejecutan vía MCP supabase-monstruo execute_sql.
# Manus E2 las correrá en el día +1 desde el hilo activo.
#
# Output esperado se compara contra umbrales binarios.
# -----------------------------------------------------------------------------

cat <<'SQL'

-- M2: Watchdog — mensajes pendientes con > 1h de antigüedad
SELECT count(*) AS pendientes_old
  FROM public.embrion_memoria
 WHERE consumed_at IS NULL
   AND tipo = 'mensaje_alfredo'
   AND created_at < NOW() - INTERVAL '1 hour';
-- Esperado: <= 5 (umbral watchdog)

-- M3: Total consumed (debería ser >= 14, idealmente > 14 si hubo nuevos
-- mensajes respondidos en las 24h)
SELECT count(*) AS total_consumed
  FROM public.embrion_memoria
 WHERE consumed_at IS NOT NULL
   AND tipo = 'mensaje_alfredo';
-- Esperado: >= 14 (baseline post-backfill)

-- M3.b: Total NULL (debería ser <= 7, idealmente igual o menor si los 7 fueron
-- procesados por _detect_trigger post-deploy)
SELECT count(*) AS total_null
  FROM public.embrion_memoria
 WHERE consumed_at IS NULL
   AND tipo = 'mensaje_alfredo';
-- Esperado: <= 7 (baseline post-backfill)

-- M3.c: Sanity check — ningún tipo distinto fue tocado por T5
SELECT count(*) AS otros_consumed
  FROM public.embrion_memoria
 WHERE consumed_at IS NOT NULL
   AND tipo != 'mensaje_alfredo';
-- Esperado: 0

SQL

echo ""
echo "============================================================"
echo "M1 — Railway logs (manual o via Railway API)"
echo "============================================================"
echo ""
cat <<'NOTES'
Verificación M1 requiere acceso a Railway logs del servicio Embrión.

Métrica binaria:
  Buscar patrón: `embrion_trigger_detected mensaje_alfredo` con mismo `message_id`
  apareciendo > 1 vez en ventana 24h.

Comando sugerido (Railway CLI):
  railway logs --service embrion --since 24h | grep "embrion_trigger_detected mensaje_alfredo" | jq -r .message_id | sort | uniq -c | sort -rn | head -5

Esperado: todas las cuentas == 1. Si alguna >= 2 → bucle infinito reincidente, revertir.

Alternativa via API GraphQL (Railway Project ID LikeTickets):
  curl -X POST https://backboard.railway.com/graphql/v2 \
    -H "Authorization: Bearer $RAILWAY_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query":"query { deployment(...) { logs(filter: ...) } }"}'
NOTES

echo ""
echo "============================================================"
echo "Veredicto binario:"
echo "  M1 ✅ + M2 ✅ + M3 ✅ → Sprint S-EMBRION-009 GREEN"
echo "  Cualquier rojo → revertir + diagnóstico binario"
echo "============================================================"
