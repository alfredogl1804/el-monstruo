-- ============================================================================
-- Migration 039 — Sprint 88.3: Documentar tronos definitivos AGENTES
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.3) — cierre macroárea AGENTES previo a VISION_GENERATIVA
-- Origen:
--   - Validación adversarial 4 sabios sobre tronos post-038
--   - Decisión Alfredo: Cowork = trono natural agentes_desarrollo (envuelve Claude Code + doctrina)
--   - Decisión Alfredo: Devin = Tier 1 acompañante (NO trono, pero Tier 1 por madurez)
--
-- DECISION ARQUITECTONICA Sprint 88.3 (Manus B):
--   Para honrar simultáneamente "Cowork trono + Devin Tier 1 acompañante" sin
--   romper la fórmula soberana del Catastro:
--     - Devin promovido tier=2 -> tier=1 (refleja madurez Apr 2026)
--     - Devin bonus reducido 25 -> 0 (no necesita bonus para Tier 1; estaba
--       inflado para forzar trono que después se descartó)
--     - Cowork bonus 0 -> +20 con razón "doctrina del Monstruo" (DSC firmados,
--       audit cross-hilo, Skills, Computer Use - capacidades únicas que ningún
--       otro agente de desarrollo tiene)
--   Resultado fórmula:
--     Cowork: 30+10+10+10+10+5+20 = 95  (trono)
--     Devin:  30+10+10+10+10+5+0  = 75  (Tier 1 acompañante)
--
-- Idempotente: UPDATE
-- Author: Hilo Catastro (Manus B)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1) Cowork: bonus +20 con razón documentada (doctrina del Monstruo)
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET bonus_curador = 20,
       bonus_curador_razon = 'Trono agentes_desarrollo por doctrina del Monstruo (Sprint 88.3). Bonus +20 documenta capacidades únicas de Claude Cowork sobre cualquier otro agente de desarrollo: (a) DSC firmados con audit cross-hilo, (b) Skills nativas que enseñan al modelo arquitectura específica del proyecto, (c) Computer Use sobre el sandbox del usuario, (d) memoria de la doctrina del Monstruo (Brand Engine, 14 Objetivos, 7 Capas, 4 Capas Arquitectónicas). Cowork no es solo Claude Code: es Claude Code + memoria perpetua de la marca. Score final 95 supera a Devin (75) que es trono natural en repos sin doctrina. Decisión Alfredo + 4 sabios.',
       updated_at = NOW()
 WHERE id = 'claude-cowork';

-- ----------------------------------------------------------------------------
-- 2) Devin: tier=2 -> tier=1, bonus 25 -> 0, razón Tier 1 acompañante
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET tier_seed = 1,
       bonus_curador = 0,
       bonus_curador_razon = 'Tier 1 acompañante en agentes_desarrollo (Sprint 88.3). Devin = ingeniería de software autónoma sobre repos reales (Devins paralelos, VMs aisladas, PRs continuos, MCP, autofix con CI, SWE-bench top). Promovido tier=2 -> tier=1 para reflejar madurez Apr 2026 (consenso 3/4 sabios). Bonus 25 -> 0 porque Sprint 88.3 confirma que Cowork mantiene trono por doctrina del Monstruo, no por inflación de bonus. Score natural 75 lo deja como segundo más fuerte: usar Devin cuando autonomía pura sobre repo importa más que doctrina. Para repos del Monstruo: Cowork. Para repos sin doctrina: Devin.',
       updated_at = NOW()
 WHERE id = 'devin';

-- ----------------------------------------------------------------------------
-- 3) Promptfoo: bonus +5 (Sprint 88.3 documentación + soberanía)
--    Score natural 75 (tier1+sandbox+fs+net+multistep+production) +5 = 80.
--    Lakera tiene bonus +20 pero score base 50 (no sandbox/fs) → 70. Promptfoo gana.
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET bonus_curador = 5,
       bonus_curador_razon = 'Trono agentes_seguridad por soberanía + score natural (Sprint 88.3). Promptfoo OSS self-hosted (sandbox, fs, net, CI/CD integration) supera a Lakera enterprise (bonus +20 pero score base 50 por no tener sandbox/fs). Cumple Obj #12 (Soberanía: cero dependencia externa). Bonus +5 reconoce su rol activo en CI/CD del Monstruo (red-teaming + evals automatizados). Lakera queda como Tier 1 acompañante para defensa runtime cuando se necesite scale enterprise.',
       updated_at = NOW()
 WHERE id = 'promptfoo';

-- ----------------------------------------------------------------------------
-- 4) arize-phoenix: bonus +5 (Sprint 88.3 documentación + soberanía)
--    Score natural 75 +5 = 80. Braintrust 60+15=75. Phoenix gana por 5 pts.
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET bonus_curador = 5,
       bonus_curador_razon = 'Trono agentes_observabilidad_evals por soberanía + score natural (Sprint 88.3). Phoenix (Arize AI) OSS self-hosted (sandbox, fs, net, OpenTelemetry, OpenLLMetry compatible) supera a Braintrust enterprise (bonus +15, score base 60). Cumple Obj #12 (Soberanía). Bonus +5 reconoce integración con stack OSS del Monstruo (Langfuse acompañante también, pero Phoenix tiene mejor doctrina de tracing). Braintrust queda como Tier 1 acompañante para gates de calidad enterprise.',
       updated_at = NOW()
 WHERE id = 'arize-phoenix';

-- ----------------------------------------------------------------------------
-- 5) Manus: razón ya documentada en migración 038. Sprint 88.3 refuerza:
-- ----------------------------------------------------------------------------
UPDATE catastro_agentes
   SET bonus_curador_razon = 'Trono agentes_generalistas_autonomos según consenso 4/4 sabios + decisión Alfredo (Sprint 88.3 confirma). Manus = action engine horizontal end-to-end (frontend/backend/db/auth/Stripe/deploy + escritorio + browser + sandbox real). Es el HILO en el que Alfredo trabaja hoy. Score 95 (tier=1 + 6 capacidades + bonus 10) trono indiscutido. Acompañantes: ChatGPT Agent (OpenAI), Genspark, Comet Browser (Perplexity).',
       updated_at = NOW()
 WHERE id = 'manus';

COMMIT;

-- ----------------------------------------------------------------------------
-- 6) REFRESH MATERIALIZED VIEW
-- ----------------------------------------------------------------------------
REFRESH MATERIALIZED VIEW catastro_tronos_agentes;

-- ----------------------------------------------------------------------------
-- 7) Verificación final: 12 dominios, 12 tronos, Cowork trono desarrollo
-- ----------------------------------------------------------------------------
DO $$
DECLARE
  v_total INT;
  v_dominios INT;
  v_tronos INT;
  v_cowork_trono BOOLEAN;
  v_devin_tier INT;
  v_devin_bonus INT;
BEGIN
  SELECT COUNT(*) INTO v_total FROM catastro_agentes;
  SELECT COUNT(DISTINCT dominio) INTO v_dominios FROM catastro_agentes;
  SELECT COUNT(*) INTO v_tronos FROM catastro_tronos_agentes;
  SELECT EXISTS(
    SELECT 1 FROM catastro_tronos_agentes
    WHERE dominio = 'agentes_desarrollo' AND trono_id = 'claude-cowork'
  ) INTO v_cowork_trono;
  SELECT tier_seed, bonus_curador INTO v_devin_tier, v_devin_bonus
    FROM catastro_agentes WHERE id = 'devin';

  RAISE NOTICE 'Sprint 88.3 cierre: % agentes, % dominios, % tronos. Cowork trono desarrollo: %. Devin tier=%, bonus=%.',
    v_total, v_dominios, v_tronos, v_cowork_trono, v_devin_tier, v_devin_bonus;

  IF v_dominios <> 12 THEN
    RAISE EXCEPTION 'Esperado 12 dominios, encontrados %', v_dominios;
  END IF;
  IF v_tronos <> 12 THEN
    RAISE EXCEPTION 'Esperado 12 tronos, encontrados %', v_tronos;
  END IF;
  IF NOT v_cowork_trono THEN
    RAISE EXCEPTION 'Cowork debe ser trono de agentes_desarrollo';
  END IF;
  IF v_devin_tier <> 1 OR v_devin_bonus <> 0 THEN
    RAISE EXCEPTION 'Devin debe ser tier=1, bonus=0 (Tier 1 acompañante). Encontrado tier=%, bonus=%', v_devin_tier, v_devin_bonus;
  END IF;
END $$;

-- ============================================================================
-- FIN MIGRACION 039
-- ============================================================================
