-- Sprint 88 - Migración 034: agregar columna bonus_curador
-- DSC-G-007.4 - Desempate documentado de tronos por curador humano
--
-- bonus_curador permite ajustar el score de trono en empates con razón
-- explícita documentada en bonus_curador_razon. Solo +1, +2 o +3.
--
-- Refresca la vista materializada catastro_tronos_agentes para incluir el bonus.
--
-- 2026-05-10 — Manus (Hilo Catastro), validado por Alfredo

BEGIN;

ALTER TABLE catastro_agentes
    ADD COLUMN IF NOT EXISTS bonus_curador SMALLINT NOT NULL DEFAULT 0
        CHECK (bonus_curador >= 0 AND bonus_curador <= 5);

ALTER TABLE catastro_agentes
    ADD COLUMN IF NOT EXISTS bonus_curador_razon TEXT;

COMMENT ON COLUMN catastro_agentes.bonus_curador IS
    'Bonus aditivo (0-5) que el curador asigna en desempates de tronos. '
    'Requiere bonus_curador_razon documentada. DSC-G-007.4.';

-- Bonus aplicados Sprint 88 (validados por Alfredo 2026-05-10)
UPDATE catastro_agentes SET
    bonus_curador = 1,
    bonus_curador_razon = 'Desempate vibe-coding: Lovable tiene mayor adopción 2026 (top 3 vibe-coding según Vibe Coding Academy, Taskade, RTSLabs). Sobre Base44 (alfabético) y Bolt (mismo score).'
WHERE id = 'lovable';

UPDATE catastro_agentes SET
    bonus_curador = 1,
    bonus_curador_razon = 'Desempate investigación: Perplexity Personal Computer (lanzado 2026-05-07) es arsenal directo del Monstruo, mientras Glean es enterprise-knowledge-search nicho. TechCrunch + Reddit r/perplexity_ai validaron lanzamiento.'
WHERE id = 'perplexity-personal-computer';

UPDATE catastro_agentes SET
    bonus_curador = 1,
    bonus_curador_razon = 'Desempate interfaces_usuario: Claude.ai es la interfaz que el Monstruo usa hoy (Cowork, Skills, Computer Use). ChatGPT Frontier es enterprise, no aplica al stack Monstruo.'
WHERE id = 'claude-ai';

COMMIT;

-- Re-crear vista materializada con bonus_curador integrado
DROP MATERIALIZED VIEW IF EXISTS catastro_tronos_agentes CASCADE;

CREATE MATERIALIZED VIEW catastro_tronos_agentes AS
SELECT DISTINCT ON (dominio)
    dominio,
    id AS trono_id,
    nombre AS trono_nombre,
    tier_seed,
    open_weights,
    estado,
    bonus_curador,
    bonus_curador_razon,
    (
        (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
      + (CASE WHEN multi_swarm_capable THEN 15 ELSE 0 END)
      + (CASE WHEN tiene_sandbox THEN 10 ELSE 0 END)
      + (CASE WHEN acceso_filesystem THEN 10 ELSE 0 END)
      + (CASE WHEN acceso_internet THEN 10 ELSE 0 END)
      + (CASE WHEN multi_step_capable THEN 10 ELSE 0 END)
      + (CASE WHEN persistencia_memoria = 'external_db' THEN 10 ELSE 0 END)
      + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
      + bonus_curador
    ) AS score,
    now() AS calculado_at
FROM catastro_agentes
ORDER BY dominio,
         (
            (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
          + (CASE WHEN multi_swarm_capable THEN 15 ELSE 0 END)
          + (CASE WHEN tiene_sandbox THEN 10 ELSE 0 END)
          + (CASE WHEN acceso_filesystem THEN 10 ELSE 0 END)
          + (CASE WHEN acceso_internet THEN 10 ELSE 0 END)
          + (CASE WHEN multi_step_capable THEN 10 ELSE 0 END)
          + (CASE WHEN persistencia_memoria = 'external_db' THEN 10 ELSE 0 END)
          + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
          + bonus_curador
         ) DESC,
         open_weights DESC, tier_seed ASC, id ASC;

CREATE UNIQUE INDEX idx_catastro_tronos_agentes_dominio
    ON catastro_tronos_agentes (dominio);
