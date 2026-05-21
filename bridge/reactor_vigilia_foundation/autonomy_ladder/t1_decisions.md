# T1 DECISIONS PENDING: AUTONOMY LADDER

## Estado
- SPRINT_CANDIDATE_R0

## Decisiones Requeridas de Alfredo (T1)

1. **Aprobación del Policy Engine Base (SPR-AUTONOMY-LADDER-001):**
   - ¿Se aprueba la implementación conceptual de la Escalera A0-A8 como un Policy Engine estricto (schema + registry + preflight check)?

2. **Aprobación del Allowlist R1:**
   - ¿Se aprueban las acciones y paths explícitamente permitidos (y prohibidos) en `r1_self_evolution_allowlist.yaml` para el primer batch del Nightly Builder?

3. **Siguiente Paso Crítico:**
   - Con la Policy Base diseñada (aunque no implementada en runtime), ¿cuál es el siguiente sprint?
     - Opción A: Diseñar el State Fabric (SPR-STATE-FABRIC-001).
     - Opción B: Diseñar el Oráculo de IAs (SPR-ORACLE-AI-001).
     - Opción C: Implementar el Policy Engine en código Python/TypeScript real.
