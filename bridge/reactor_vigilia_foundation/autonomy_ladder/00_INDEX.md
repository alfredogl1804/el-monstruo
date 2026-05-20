# 00 INDEX — AUTONOMY LADDER POLICY ENGINE

## Estado del Sprint
- **ID:** SPR-AUTONOMY-LADDER-001
- **Status:** DRAFT_R0
- **Contexto:** T1 aprobó la Stack Vertical y la Escalera A0-A8 (commit `210ab5a`). Este sprint convierte la escalera conceptual en una policy base operativa y machine-readable.

## Archivos en este paquete (12)

1. `00_INDEX.md` — Este archivo.
2. `01_AUTONOMY_LADDER_A0_A8.md` — Definición oficial de los 9 niveles.
3. `02_POLICY_ENGINE_PRINCIPLES.md` — Reglas de evaluación de permisos.
4. `autonomy_policy.schema.yaml` — Schema estructural para validar policies.
5. `autonomy_policy_v0.yaml` — Policy base R0.
6. `action_registry_v0.yaml` — Catálogo de acciones mapeadas a niveles A0-A8.
7. `loop_max_level_contract.yaml` — Plantilla de contrato para inicializar loops.
8. `r1_self_evolution_allowlist.yaml` — Allowlist estricto para el primer batch R1.
9. `preflight_decision_table.md` — Matriz de decisión antes de ejecutar acciones.
10. `examples.md` — Ejemplos de evaluación de permisos.
11. `restore_test.md` — 20 preguntas de validación.
12. `t1_decisions.md` — Decisiones pendientes de firma para activar este policy engine.

## Reglas de Implementación
- No hay runtime activo. Todo es diseño R0.
- No se implementa el State Fabric ni el Oráculo todavía.
- R1_UNLOCKED no significa autonomía ilimitada; requiere validación contra esta policy.
