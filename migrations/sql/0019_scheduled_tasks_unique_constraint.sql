-- Migracion: 0019_scheduled_tasks_unique_constraint
-- Sprint: D-2 cleanup destructivo scheduled_tasks (Hilo Ejecutor 2)
-- Autorizado por: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1
-- Fecha: 2026-05-11
-- Doctrina:
--   * DSC-S-006 RLS por defecto: scheduled_tasks ya tiene RLS habilitado pre-existente
--   * DSC-S-012 Anti-deriva: migration en repo SIEMPRE antes de aplicar a prod
--
-- Objetivo: agregar UNIQUE(name, embrion_id) a scheduled_tasks para que el bug
-- de duplicacion (cada arranque del kernel insertaba 5 filas nuevas) sea
-- imposible a nivel SQL. La migration solo PUEDE aplicarse cuando la tabla
-- ya no tiene duplicados (el constraint rechaza la creacion si hay duplicados),
-- por lo tanto la migration es PRUEBA BINARIA POST-CLEANUP.
--
-- Idempotente: usa IF NOT EXISTS en el chequeo defensivo.

BEGIN;

-- Pre-check defensivo: si ya existe el constraint, salir sin error.
DO $$
DECLARE
  constraint_exists boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'scheduled_tasks_name_embrion_unique'
      AND conrelid = 'public.scheduled_tasks'::regclass
  ) INTO constraint_exists;

  IF constraint_exists THEN
    RAISE NOTICE 'Constraint scheduled_tasks_name_embrion_unique ya existe — skip';
    RETURN;
  END IF;

  -- Agregar constraint UNIQUE(name, embrion_id)
  -- Falla con error 23505 (unique_violation) si hay duplicados en la tabla.
  ALTER TABLE public.scheduled_tasks
    ADD CONSTRAINT scheduled_tasks_name_embrion_unique
    UNIQUE (name, embrion_id);

  RAISE NOTICE 'Constraint scheduled_tasks_name_embrion_unique creado OK';
END
$$;

COMMIT;

-- Verificacion post-aplicacion (esta query la corre el applier).
-- SELECT conname, contype, conrelid::regclass
-- FROM pg_constraint
-- WHERE conrelid = 'public.scheduled_tasks'::regclass
--   AND conname = 'scheduled_tasks_name_embrion_unique';
