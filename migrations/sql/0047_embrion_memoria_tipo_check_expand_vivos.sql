-- Migration 0047 — H13 tactical
-- Sprint: DSC-G-013-EVIDENCIA (DB↔Repo Coherence Gate)
-- Autor: Cowork T2-A firmado bajo autorización T1 Opción A (2026-05-17)
-- Aplicada prod via MCP apply_migration: 2026-05-17
--
-- PROBLEMA BINARIO RESUELTO:
--   El CHECK `embrion_memoria_tipo_check` rechazaba silenciosamente 4 tipos
--   que el código del embrion_loop sí intenta insertar:
--     - 'evaluacion'           (embrion_loop.py:1834,2118 — lessons learned)
--     - 'silencio_preverifier' (embrion_loop.py:1147 — observability)
--     - 'contribucion_sabio'   (embrion_loop.py:2353 — importancia=9 ALTA)
--     - 'radar_insight'        (embrion_loop.py:2459 — radar daily)
--   Verificado vía SELECT COUNT(*) WHERE tipo IN (...) = 0 filas en prod.
--   Esto era F21 silente: 4 codepaths perdían escrituras sin error visible.
--
-- SCOPE INTENCIONALMENTE LIMITADO (Opción A T1):
--   - NO incluye 'sprint_closure' (Manus E2 lo mencionó pero NO hay código vivo)
--   - NO incluye tipos strategic S-EMBRION-009 (guardrail, silencio_verificador)
--   Esos se agregarán cuando exista código que los use (anti-aspirational).
--
-- IDEMPOTENCIA: DROP CONSTRAINT IF EXISTS + ADD CONSTRAINT en transacción.
-- REVERSIBLE: rollback emite el constraint original con 9 tipos.
--
-- VERIFICACIÓN POST-APPLY (binaria, 2026-05-17):
--   1) pg_get_constraintdef('embrion_memoria_tipo_check') retorna 13 tipos ✅
--   2) INSERT sintético de los 4 tipos nuevos en BEGIN/ROLLBACK → 4 OK ✅
--   3) Control negativo: INSERT 'tipo_inexistente_xyz' → check_violation ✅
--   4) Smoke residual = 0 filas (rollback funcionó, no contamina dataset) ✅

BEGIN;

ALTER TABLE public.embrion_memoria
  DROP CONSTRAINT IF EXISTS embrion_memoria_tipo_check;

ALTER TABLE public.embrion_memoria
  ADD CONSTRAINT embrion_memoria_tipo_check
  CHECK (tipo IN (
    -- Existentes pre-H13 (9):
    'doctrina',
    'pensamiento',
    'decision',
    'aprendizaje',
    'emocion',
    'latido',
    'reflexion',
    'mensaje_alfredo',
    'respuesta_embrion',
    -- Nuevos H13 vivos en código (4):
    'evaluacion',
    'silencio_preverifier',
    'contribucion_sabio',
    'radar_insight'
  ));

COMMIT;
