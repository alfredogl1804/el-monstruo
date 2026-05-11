-- =============================================================================
-- Migracion 0010 - cowork_sesiones: 6 columnas KPI para ramp COWORK-RUNTIME
-- =============================================================================
-- Sprint    : COWORK-RUNTIME-001 (acción #3 cierre — ramp de los 9 flags)
-- Origen    : bridge/cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11.md
--             (pre-trabajo obligatorio Manus, punto #4, líneas 49 y 117-122)
-- Doctrina  : DSC-S-006 v1.1 (RLS por defecto), DSC-S-007 (naming canónico)
-- Hilo      : Manus Hilo Ejecutor (firmado bajo división DSC-MO-005)
-- Decisión  : Opción C del reporte binario gap_0010 (2026-05-11) — Alfredo firmó
--             que este slot honra la spec original de Cowork (anterior a colisión
--             de numeración del Sprint S-003.B audit middleware).
--
-- Contexto:
--   El spec firmado por Cowork T2 Arquitecto requiere registrar 6 métricas de
--   ramp en `cowork_sesiones` (líneas 117-122 del documento canónico). Sin estas
--   columnas no se puede medir tasa de falso positivo, efectividad del hook,
--   detecciones de antipatterns ni catches del semantic detector — métricas
--   bloqueantes para autorizar cada flip diario del ramp Día 1→Día 5.
--
-- Diseño:
--   - 6 columnas counter o jsonb, NOT NULL con default 0 / '[]'::jsonb.
--   - Idempotente vía `ADD COLUMN IF NOT EXISTS` (Postgres 9.6+).
--   - No toca RLS ni policies existentes — la tabla ya está en service_role_only
--     desde 0009_cowork_sesiones.sql (DSC-S-006 v1.1).
--   - Comments en cada columna para autodocumentación.
--
-- Atomicidad: BEGIN/COMMIT, single-transaction.
--
-- Aplicar via: `python3 scripts/_apply_migration_0010.py` o equivalente
--             usando SUPABASE_SERVICE_KEY (DSC-S-007). Verificar post-aplicación
--             que las 6 columnas existen con la query de verificación al final.
-- =============================================================================

BEGIN;

-- 1. interceptaciones_count: cuántas veces el hook bloqueó o marcó en la sesión
ALTER TABLE public.cowork_sesiones
  ADD COLUMN IF NOT EXISTS interceptaciones_count integer NOT NULL DEFAULT 0;

COMMENT ON COLUMN public.cowork_sesiones.interceptaciones_count IS
  'Métrica ramp: número de intercepciones del hook (T1) durante la sesión. ' ||
  'Incrementado por COWORK_HOOK_ENABLED en shadow o enforce mode. Spec líneas 117-122.';

-- 2. antipattern_hits: F1-F22 detectados (suma de todas las violaciones del catálogo)
ALTER TABLE public.cowork_sesiones
  ADD COLUMN IF NOT EXISTS antipattern_hits integer NOT NULL DEFAULT 0;

COMMENT ON COLUMN public.cowork_sesiones.antipattern_hits IS
  'Métrica ramp: total de antipatterns F1-F22 detectados en la sesión (T6). ' ||
  'Counter agregado; el detalle por antipattern queda en violaciones_detectadas (jsonb).';

-- 3. suggest_pause_blocks: específicamente regex anti-pause (subset de interceptaciones)
ALTER TABLE public.cowork_sesiones
  ADD COLUMN IF NOT EXISTS suggest_pause_blocks integer NOT NULL DEFAULT 0;

COMMENT ON COLUMN public.cowork_sesiones.suggest_pause_blocks IS
  'Métrica ramp: bloqueos del regex anti-pause (subset de interceptaciones_count). ' ||
  'Sirve para medir efectividad de la regla específica que motivó M9 cura síndrome Dory.';

-- 4. preflight_missing_count: sesiones donde Cowork NO leyó los 6 docs Pre-flight
ALTER TABLE public.cowork_sesiones
  ADD COLUMN IF NOT EXISTS preflight_missing_count integer NOT NULL DEFAULT 0;

COMMENT ON COLUMN public.cowork_sesiones.preflight_missing_count IS
  'Métrica ramp: número de violaciones de COWORK_PREFLIGHT_REQUIRED (T5) en la sesión. ' ||
  'Si > 0 con MODE=enforce, la sesión debió haber sido bloqueada al inicio.';

-- 5. semantic_extra_catches: lista detallada de qué atrapó el semantic que regex no atrapó
ALTER TABLE public.cowork_sesiones
  ADD COLUMN IF NOT EXISTS semantic_extra_catches jsonb NOT NULL DEFAULT '[]'::jsonb;

COMMENT ON COLUMN public.cowork_sesiones.semantic_extra_catches IS
  'Métrica ramp: array de objetos {timestamp, texto, reasoning_semantic} ' ||
  'representando catches del companion agent semántico (T2) que el regex no detectó. ' ||
  'Justifica el ROI del costo de inferencia adicional del semantic detector.';

-- 6. false_positive_reports: array de reportes de Alfredo confirmando blocks espurios
ALTER TABLE public.cowork_sesiones
  ADD COLUMN IF NOT EXISTS false_positive_reports jsonb NOT NULL DEFAULT '[]'::jsonb;

COMMENT ON COLUMN public.cowork_sesiones.false_positive_reports IS
  'Métrica ramp: array de objetos {timestamp, block_id, reason, alfredo_comment} ' ||
  'donde Alfredo marcó manualmente "ese block fue espurio" via Telegram veto (M9) ' ||
  'o chat. Criterio DoD del ramp: tasa < 5% durante 5 días consecutivos.';

COMMIT;

-- =============================================================================
-- Verificación post-aplicación esperada:
--
--   SELECT column_name, data_type, column_default
--   FROM information_schema.columns
--   WHERE table_name = 'cowork_sesiones'
--     AND table_schema = 'public'
--     AND column_name IN (
--       'interceptaciones_count',
--       'antipattern_hits',
--       'suggest_pause_blocks',
--       'preflight_missing_count',
--       'semantic_extra_catches',
--       'false_positive_reports'
--     )
--   ORDER BY column_name;
--
--   → 6 filas devueltas. Counters integer con default 0; jsonb con default '[]'.
--
-- Verificación de RLS preservada (la tabla NO debe haber cambiado su policy):
--
--   SELECT policyname, cmd, qual FROM pg_policies
--   WHERE schemaname='public' AND tablename='cowork_sesiones';
--
--   → service_role_only existente desde 0009 sigue intacto.
-- =============================================================================
