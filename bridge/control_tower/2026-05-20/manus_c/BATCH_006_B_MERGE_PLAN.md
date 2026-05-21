# BATCH 006 — CÉLULA B: MERGE PLAN

## Objetivo
Definir la estrategia segura para integrar las 6 ramas de código de Batch 005 v0.2 hacia `main`, previniendo conflictos y asegurando que CI pase en cada paso.

## Ramas a Mergear (Batch 005 v0.2)

1. `control-tower/2026-05-20-batch-005-b1-anchor-store-v0-2` (SQL 0050 + b1_anchor_store.py)
2. `control-tower/2026-05-20-batch-005-b3-plan-ledger-v0-2` (SQL 0051 + b3_plan_ledger.py)
3. `control-tower/2026-05-20-batch-005-b2-claim-vg` (b2_claim_vg.py)
4. `control-tower/2026-05-20-batch-005-b4-memento-integration` (b4_memento.py)
5. `control-tower/2026-05-20-batch-005-b10-guardian-cron` (b10_guardian_cron.py)
6. `control-tower/2026-05-20-batch-005-b6-e6-verification-harness` (b6_signature_verifier.py)

## PR Strategy y Orden de Merge

Dado que los módulos de `kernel/anti_dory/` son ortogonales en esta fase inicial, el riesgo de conflictos es bajo. Sin embargo, para mantener el historial limpio y CI verde, se propone un **Mega-PR de Integración**:

### Paso 1: Crear Rama de Integración
Crear una rama temporal desde `main`:
`git checkout -b integration/anti-dory-batch-005`

### Paso 2: Merge Secuencial a Integration
Mergear cada rama localmente resolviendo conflictos (si los hubiera en `__init__.py`):
```bash
git merge origin/control-tower/2026-05-20-batch-005-b1-anchor-store-v0-2
git merge origin/control-tower/2026-05-20-batch-005-b3-plan-ledger-v0-2
git merge origin/control-tower/2026-05-20-batch-005-b2-claim-vg
git merge origin/control-tower/2026-05-20-batch-005-b4-memento-integration
git merge origin/control-tower/2026-05-20-batch-005-b10-guardian-cron
git merge origin/control-tower/2026-05-20-batch-005-b6-e6-verification-harness
```

### Paso 3: Resolución de Conflictos Esperados
El único archivo con alto riesgo de conflicto es `kernel/anti_dory/__init__.py` y `tests/anti_dory/__init__.py`.
**Estrategia de resolución:** Aceptar todas las adiciones, asegurando que todos los módulos queden expuestos.

### Paso 4: Ejecución Global de Tests
En la rama de integración, ejecutar la suite completa para asegurar que no hay regresiones cruzadas:
`python3 -m pytest tests/anti_dory/ -v`
*(Esperado: 104 PASS)*

### Paso 5: Abrir PR a Main
Abrir un solo PR desde `integration/anti-dory-batch-005` hacia `main`.
- **Título:** `feat(anti_dory): Integración Batch 005 Real Runtime`
- **Revisores:** Cowork + Perplexity PBA
- **CI Expectations:** Github Actions debe pasar (pytest, linter, rls-check).

## Confirmación
- **NO PR ABIERTO AÚN:** Este documento es solo el plan.
- Requiere autorización explícita de T1 para proceder con el merge y la apertura del PR.
