-- Migration 0012 — embrion_inbox + embrion_audit_log
-- Sprint: EMBRION-NEEDS-002 Tarea 5 (Embrión-Daddy bidireccional, implementación)
-- Spec firmado: discovery_forense/SPECS/EMBRION_DADDY_BIDIRECCIONAL_v1.md (blob 3aecf93, PR #81)
-- Kickoff: bridge/cowork_to_manus_T5_EMBRION_DADDY_KICKOFF_2026_05_11.md
-- Doctrina aplicada: DSC-S-006 v1.1 (RLS por defecto, service_role_only)
-- Autor: Hilo Ejecutor 2 (manus_hilo_ejecutor_2)
-- Fecha: 2026-05-11
--
-- DOS TABLAS:
--   1) embrion_inbox       — Buzón Asíncrono Tipado para mensajes Daddy → Embrión.
--   2) embrion_audit_log   — Auditoría específica del procesamiento del inbox.
--
-- DECISIÓN CA6 (documentada en postmortem T5):
--   Se crea embrion_audit_log nueva (NO se reutiliza kernel_audit_log) porque
--   kernel_audit_log audita HTTP requests al kernel (request_id, method, path,
--   response_status, source_ip), schema que NO encaja para auditar procesamiento
--   de mensajes del inbox (inbox_id, cycle_id, proposal_id, command_type, decision).
--
-- Idempotencia: CREATE TABLE IF NOT EXISTS + CREATE POLICY IF NOT EXISTS.

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- TABLA 1: embrion_inbox
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.embrion_inbox (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id_origen      TEXT            NOT NULL,
    comando             TEXT            NOT NULL,
    tipo_comando        TEXT            NOT NULL,
    payload             JSONB           NOT NULL DEFAULT '{}'::jsonb,
    estado              TEXT            NOT NULL DEFAULT 'pending',
    priority            INTEGER         NOT NULL DEFAULT 5,
    rate_limit_bucket   TEXT            NOT NULL DEFAULT 'default',
    cycle_id            BIGINT          NULL,
    proposal_id         UUID            NULL,
    superseded_by       UUID            NULL,
    parser_result       JSONB           NULL,
    intent_class        TEXT            NULL,
    requires_mfa        BOOLEAN         NOT NULL DEFAULT FALSE,
    mfa_pin_hash        TEXT            NULL,
    mfa_expires_at      TIMESTAMPTZ     NULL,
    error_reason        TEXT            NULL,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    processed_at        TIMESTAMPTZ     NULL,
    expires_at          TIMESTAMPTZ     NOT NULL DEFAULT (NOW() + INTERVAL '30 minutes'),

    CONSTRAINT embrion_inbox_estado_chk
        CHECK (estado IN (
            'pending',
            'processing',
            'processed',
            'rejected',
            'expired',
            'requires_mfa'
        )),
    CONSTRAINT embrion_inbox_tipo_comando_chk
        CHECK (tipo_comando IN (
            '/context',
            '/override',
            '/help',
            '/status',
            '/answer',
            '/feedback',
            'unauthorized_origin',
            'unknown'
        )),
    CONSTRAINT embrion_inbox_priority_chk
        CHECK (priority BETWEEN 1 AND 10)
);

COMMENT ON TABLE  public.embrion_inbox IS
    'Buzón Asíncrono Tipado del Embrión. Daddy → Embrión via Telegram. Sprint EMBRION-NEEDS-002 Tarea 5.';
COMMENT ON COLUMN public.embrion_inbox.estado IS
    'pending → processing → processed | rejected | expired | requires_mfa';
COMMENT ON COLUMN public.embrion_inbox.tipo_comando IS
    'Comando parseado deterministicamente. unknown/unauthorized_origin son terminales.';
COMMENT ON COLUMN public.embrion_inbox.superseded_by IS
    'Si dos /override mismo proposal_id, el viejo queda expired con superseded_by=nuevo_id.';
COMMENT ON COLUMN public.embrion_inbox.intent_class IS
    'Clasificación del sanitizer: safe | attack | jailbreak | uncertain.';

CREATE INDEX IF NOT EXISTS embrion_inbox_estado_priority_idx
    ON public.embrion_inbox (estado, priority DESC, created_at ASC)
    WHERE estado IN ('pending', 'processing');

CREATE INDEX IF NOT EXISTS embrion_inbox_proposal_id_idx
    ON public.embrion_inbox (proposal_id)
    WHERE proposal_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS embrion_inbox_expires_at_idx
    ON public.embrion_inbox (expires_at)
    WHERE estado IN ('pending', 'processing', 'requires_mfa');

CREATE INDEX IF NOT EXISTS embrion_inbox_rate_limit_idx
    ON public.embrion_inbox (rate_limit_bucket, created_at DESC);

-- RLS — patrón service_role_only (DSC-S-006 v1.1)
ALTER TABLE public.embrion_inbox ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'embrion_inbox'
          AND policyname = 'service_role_only'
    ) THEN
        CREATE POLICY service_role_only
            ON public.embrion_inbox
            AS PERMISSIVE
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

REVOKE ALL ON public.embrion_inbox FROM PUBLIC, anon, authenticated;
GRANT ALL ON public.embrion_inbox TO service_role;

-- ─────────────────────────────────────────────────────────────────────────────
-- TABLA 2: embrion_audit_log
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.embrion_audit_log (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    inbox_id        UUID            NULL,
    cycle_id        BIGINT          NULL,
    proposal_id     UUID            NULL,
    command_type    TEXT            NOT NULL,
    decision        TEXT            NOT NULL,
    parser_result   JSONB           NULL,
    intent_class    TEXT            NULL,
    payload_redacted JSONB          NULL,
    chat_id_origen  TEXT            NULL,
    source          TEXT            NOT NULL DEFAULT 'embrion_inbox',
    notes           TEXT            NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT embrion_audit_log_decision_chk
        CHECK (decision IN (
            'enqueued',
            'parsed_ok',
            'parse_failed',
            'sanitize_rejected',
            'consumed',
            'processed_ok',
            'processed_failed',
            'expired',
            'superseded',
            'requires_mfa',
            'mfa_validated',
            'unauthorized'
        )),
    CONSTRAINT embrion_audit_log_source_chk
        CHECK (source IN ('embrion_inbox', 'embrion_loop', 'telegram_writer'))
);

COMMENT ON TABLE public.embrion_audit_log IS
    'Trazabilidad del procesamiento de mensajes del inbox. CA6 Sprint EMBRION-NEEDS-002 T5.';

CREATE INDEX IF NOT EXISTS embrion_audit_log_inbox_id_idx
    ON public.embrion_audit_log (inbox_id)
    WHERE inbox_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS embrion_audit_log_cycle_id_idx
    ON public.embrion_audit_log (cycle_id)
    WHERE cycle_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS embrion_audit_log_created_at_idx
    ON public.embrion_audit_log (created_at DESC);

-- RLS — service_role_only
ALTER TABLE public.embrion_audit_log ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'embrion_audit_log'
          AND policyname = 'service_role_only'
    ) THEN
        CREATE POLICY service_role_only
            ON public.embrion_audit_log
            AS PERMISSIVE
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

REVOKE ALL ON public.embrion_audit_log FROM PUBLIC, anon, authenticated;
GRANT ALL ON public.embrion_audit_log TO service_role;

COMMIT;

-- Verificación post-migración (correr manualmente):
--   SELECT tablename, rowsecurity FROM pg_tables
--   WHERE tablename IN ('embrion_inbox', 'embrion_audit_log');
--   -- Esperado: ambas rowsecurity=true
--
--   SELECT policyname FROM pg_policies
--   WHERE tablename IN ('embrion_inbox', 'embrion_audit_log');
--   -- Esperado: ambas con 'service_role_only'
