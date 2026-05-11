-- ============================================================================
-- Migration 037 — Sprint 88.1: Calibrar empates score 55 con bonus_curador
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.1)
-- Origen: Follow-up DSC-G-007.2 sección "Riesgos asumidos" punto 3
-- Idempotente: UPDATE con razón documentada
-- Author: Hilo Catastro (Manus)
-- ============================================================================
--
-- DECISIONES:
--   1) Higgsfield (audiovisual, score 55): se mantiene como trono + bonus +5
--      Razón: Investigación 2026 (scribehow, ltx.studio Apr 28) confirma que
--      Higgsfield es el "wrapper agéntico multi-modelo" con mejor value/dollar
--      para Monstruo (orquestación multi-tool, no agente single-model).
--      Veo 3.1 ya está catalogado como modelo base en macroárea vision_generativa
--      (no compite directamente como agente envolvente).
--
--   2) Kittl (branding, score 55): se DESTITUYE como trono. Looka asume.
--      Razón: Investigación 2026 (alloypress, logomakerr, gradually.ai, sologo)
--      muestra a Looka como líder consensual en AI logo/branding generators.
--      Kittl tiene 0 menciones en rankings top 2026 vs Looka que aparece en
--      4+ rankings independientes. Mismo score técnico (55) → desempate por
--      evidencia de adopción real.
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1) Higgsfield: bonus +5 documentado, mantiene trono audiovisual
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
SET bonus_curador = 5,
    bonus_curador_razon = 'Sprint 88.1 calibración empate audiovisual: Higgsfield es el wrapper agéntico multi-modelo (envuelve Sora-2, Veo-3.1, Runway Gen-4.5, Kling 3.0) con mejor value/dollar para arsenal Monstruo, según evidencia 2026 (scribehow.com, ltx.studio Apr 28). Veo 3.1 catalogado por separado en catastro_modelos macroárea vision_generativa.',
    updated_at = NOW()
WHERE id = 'higgsfield';

-- ----------------------------------------------------------------------------
-- 2) Looka: bonus +1 documentado, asume trono branding
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
SET bonus_curador = 1,
    bonus_curador_razon = 'Sprint 88.1 calibración empate branding: Looka asume trono sobre Kittl. Mismo score técnico (55) pero Looka aparece como líder en 4+ rankings independientes 2026 (alloypress, logomakerr, gradually.ai, sologo) mientras Kittl tiene 0 menciones en top 2026.',
    updated_at = NOW()
WHERE id = 'looka';

-- ----------------------------------------------------------------------------
-- 3) Kittl: documentar destitución del trono (sin bonus)
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
SET data_extra = COALESCE(data_extra, '{}'::jsonb) || '{"sprint_88_1_calibracion": "Destituido como trono dominio branding por evidencia 2026 insuficiente. Reemplazado por Looka. Sigue en Tier 1 del catastro como producto válido, simplemente no es el trono."}'::jsonb,
    updated_at = NOW()
WHERE id = 'kittl';

-- ----------------------------------------------------------------------------
-- 4) Refresh vista materializada de tronos
-- ----------------------------------------------------------------------------
REFRESH MATERIALIZED VIEW catastro_tronos_agentes;

COMMIT;

-- ============================================================================
-- Validación post-calibración
-- ============================================================================
SELECT dominio, trono_id, trono_nombre, score, bonus_curador
FROM catastro_tronos_agentes
WHERE dominio IN ('agentes_creacion_audiovisual', 'agentes_branding_diseno')
ORDER BY dominio;
