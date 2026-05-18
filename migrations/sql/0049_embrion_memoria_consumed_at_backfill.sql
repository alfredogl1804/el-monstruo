-- =============================================================================
-- Migración 0049 — Sprint S-EMBRION-009 — Tarea T5
-- Backfill conservador de embrion_memoria.consumed_at
-- =============================================================================
--
-- Contexto:
--   Migration 0048 (T1) agregó la columna consumed_at NULL. Las filas pre-existentes
--   quedaron NULL. Esta migration marca como consumed los mensaje_alfredo que YA
--   tienen evidencia binaria de haber sido respondidos (respuesta_embrion en
--   ventana de 5 minutos posterior). Cero falsos positivos por diseño.
--
-- Spec verbatim:
--   Spec textual del comment de migration 0048 (líneas 76-83) +
--   autorización Cowork T2-A en bridge cowork_to_manus_HILO_EJECUTOR_2_COLA_CERRADA_2026_05_18.md
--   ("autorizo proceder con T5 + T6 ... sin restricciones de scope adicionales").
--
-- Estrategia:
--   UPDATE conservador: marca consumed_at = NOW() solo si EXISTS respuesta_embrion
--   con created_at en ventana (m.created_at, m.created_at + 5min). Sin ventana →
--   no marca (queda NULL → será procesado FIFO por _detect_trigger post-deploy de
--   T2/T3, que ya filtra consumed_at IS NULL).
--
-- Por qué ventana de 5 minutos:
--   - Suficientemente amplia para cubrir latencia normal del Embrión (típicamente
--     1-30s, con cola hasta ~2min en producción Railway observada).
--   - Suficientemente estrecha para evitar correlacionar respuesta_embrion de un
--     mensaje posterior con un mensaje_alfredo viejo no respondido (falso positivo).
--   - Match con la heurística histórica del sistema antes del sprint.
--
-- Cumplimiento DSC:
--   - DSC-S-006 (RLS por defecto): policy "service_role_only" FOR ALL ya cubre
--     UPDATE por service_role. No requiere policy nueva.
--   - DSC-G-008 v2: archivo entregado a Cowork para audit content antes del merge.
--   - Idempotencia: UPDATE con WHERE consumed_at IS NULL — re-correr no afecta
--     filas ya marcadas en una corrida previa. Seguro re-aplicar.
--   - Atomicidad: BEGIN/COMMIT. Rollback inmediato si falla.
--   - Reversibilidad: revert manual con
--       UPDATE embrion_memoria SET consumed_at = NULL
--         WHERE consumed_at IS NOT NULL AND created_at < '2026-05-18T07:00:00Z'
--         AND tipo = 'mensaje_alfredo';
--     (cota temporal estricta para no afectar marcados post-deploy de T2/T3).
--
-- Numeración:
--   0049 verificado disponible (último aplicado: 0048_embrion_memoria_consumed_at
--   por Cowork T2-A 2026-05-17/18 vía MCP supabase-monstruo, mergeado en PR #142).
--
-- Aplicar con (modo canónico post-H12):
--   MCP supabase-monstruo apply_migration tool (Cowork autoridad T1 delegada).
--
-- Smoke test post-aplicación obligatorio:
--   1. SELECT count(*) FROM embrion_memoria
--        WHERE tipo = 'mensaje_alfredo' AND consumed_at IS NOT NULL;
--      → > 0 si había mensajes respondidos pre-deploy (esperado en prod actual).
--
--   2. SELECT count(*) FROM embrion_memoria
--        WHERE tipo = 'mensaje_alfredo' AND consumed_at IS NULL;
--      → cantidad de mensajes "pendientes legítimos" (sin respuesta histórica).
--        Estos serán procesados por _detect_trigger FIFO post-deploy.
--
--   3. Verificar que NINGÚN row con tipo != 'mensaje_alfredo' fue tocado:
--      SELECT count(*) FROM embrion_memoria
--        WHERE tipo != 'mensaje_alfredo' AND consumed_at IS NOT NULL;
--      → debe ser 0 (ningún cambio fuera del scope del UPDATE).
-- =============================================================================
BEGIN;

-- T5 — Backfill conservador
-- Spec verbatim del comment de migration 0048 + autorización Cowork bridge 2026-05-18.
UPDATE public.embrion_memoria m
   SET consumed_at = NOW()
 WHERE m.tipo = 'mensaje_alfredo'
   AND m.consumed_at IS NULL
   AND EXISTS (
       SELECT 1
         FROM public.embrion_memoria r
        WHERE r.tipo = 'respuesta_embrion'
          AND r.created_at > m.created_at
          AND r.created_at < m.created_at + INTERVAL '5 minutes'
   );

COMMIT;

-- =============================================================================
-- Notas post-aplicación:
-- =============================================================================
--
-- 1. Cobertura esperada en prod (estimación):
--    El bucle infinito H1 generó múltiples mensaje_alfredo en POST_MERGE_PROOF
--    y ATTACHMENT_PROOF_ANTI_DORY (36 rows borrados tácticamente en H1 DELETE).
--    Las filas restantes pre-deploy son históricas reales — la mayoría tienen
--    respuesta_embrion correlacionada → serán marcadas consumed por este backfill.
--
-- 2. Mensajes legítimamente pendientes (sin respuesta) NO se tocan:
--    Quedan con consumed_at NULL. _detect_trigger los procesará FIFO post-deploy
--    de T2/T3 (que filtra consumed_at IS NULL). Cierre del círculo del sprint.
--
-- 3. T6 (verificación 24h Railway + watchdog) corre POST este backfill.
--    Métrica esperada en T6: 0 logs `embrion_trigger_detected mensaje_alfredo`
--    repetidos con mismo message_id. Si > 0 → revertir + investigar (no-op
--    silencioso del UPDATE).
-- =============================================================================
