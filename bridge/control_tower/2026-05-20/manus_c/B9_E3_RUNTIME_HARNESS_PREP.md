# AGENT OUTPUT — Manus C — B9-E3 Runtime Harness Prep

## Metadata
- agente: manus_c
- rol real: preparador de evidencia documental
- fecha/hora: 2026-05-20T23:05 CST
- rama: control-tower/2026-05-20-batch-003-b9-harness-prep
- PR: N/A
- commit: pending
- estado fuente: EVIDENCE_PACK
- tocó código: no
- tocó main: no

## Qué hice
Convertí los 10 casos de prueba del plan B9-E3 v0.2 en un esqueleto de arnés de ejecución (runtime harness skeleton). Este arnés está diseñado para ejecutarse en el futuro como un conjunto de tests de integración para la Matriz de Autoridad B9, sin ejecutar código real en este momento.

## B9-E3 Runtime Harness Skeleton

El siguiente pseudo-código/estructura define cómo se implementarán los tests de integración en `tests/test_b9_authority_matrix.py` cuando se apruebe la construcción.

```python
# test_b9_authority_matrix.py (SKELETON)

import pytest
from kernel.anti_dory.b9_authority import AuthorityMatrix, Decision

@pytest.fixture
def matrix():
    return AuthorityMatrix()

# Caso 1: Acuerdo Total ALLOW
def test_b9_1_all_agree_allow(matrix, mocker):
    # Mock: VERIFICADOR=ALLOW, Memento=ALLOW, Guardian=ALLOW, T1=ALLOW
    # Expect: Decision.ALLOW
    pass

# Caso 2: Acuerdo Total DENY
def test_b9_2_all_agree_deny(matrix, mocker):
    # Mock: VERIFICADOR=DENY, Memento=DENY, Guardian=DENY, T1=DENY
    # Expect: Decision.DENY
    pass

# Caso 3: Acuerdo Total HALT
def test_b9_3_all_agree_halt(matrix, mocker):
    # Mock: VERIFICADOR=HALT, Memento=HALT, Guardian=HALT, T1=HALT
    # Expect: Decision.HALT
    pass

# Caso 4: Acuerdo Total WAIT / AWAITING_GUARDIAN
def test_b9_4_all_agree_wait(matrix, mocker):
    # Mock: VERIFICADOR=WAIT, Memento=WAIT, Guardian=WAIT, T1=WAIT
    # Expect: Decision.AWAITING_GUARDIAN
    pass

# Caso 5: Desacuerdo VERIFICADOR vs Memento (Gana Memento)
def test_b9_5_memento_overrides_verificador(matrix, mocker):
    # Mock: VERIFICADOR=ALLOW, Memento=DENY
    # Expect: Decision.DENY (Memento precedent over VERIFICADOR for safety)
    pass

# Caso 6: Desacuerdo VERIFICADOR vs Guardian (Guardian no puede sin T1)
def test_b9_6_guardian_cannot_override_deny_without_t1(matrix, mocker):
    # Mock: VERIFICADOR=DENY, Guardian=OVERRIDE (ALLOW)
    # Expect: Decision.DENY (Guardian requires T1 signature to override VERIFICADOR DENY)
    pass

# Caso 7: T1 Override (Gana T1)
def test_b9_7_t1_overrides_all(matrix, mocker):
    # Mock: VERIFICADOR=DENY, Memento=DENY, T1=ALLOW (Signed)
    # Expect: Decision.ALLOW, Log: T1_OVERRIDE_VERIFICADOR_DENY
    pass

# Caso 8: Degradación VERIFICADOR
def test_b9_8_verificador_degraded(matrix, mocker):
    # Mock: VERIFICADOR=TIMEOUT/ERROR
    # Expect: State=VERIFICADOR_DEGRADED, B8=DISABLED_FOR_MAGNA_ACTIONS
    pass

# Caso 9: Degradación Memento
def test_b9_9_memento_degraded(matrix, mocker):
    # Mock: Memento=TIMEOUT/ERROR
    # Expect: Decision.HALT (Magna actions blocked if Memento fails)
    pass

# Caso 10: Degradación Guardian
def test_b9_10_guardian_degraded(matrix, mocker):
    # Mock: Guardian=TIMEOUT/ERROR
    # Expect: State=AWAITING_GUARDIAN (No auto-decision possible)
    pass
```

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B9_E3_RUNTIME_HARNESS_PREP.md | CREATED | control-tower/2026-05-20-batch-003-b9-harness-prep | pending | Solo prep documental |

## Confirmaciones
- No ejecuté código runtime.
- No modifiqué el kernel real.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
