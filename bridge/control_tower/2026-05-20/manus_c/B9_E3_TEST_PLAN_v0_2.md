# AGENT OUTPUT — manus_c — B9-E3 10 TESTS BINARIOS PLAN (v0.2)

## Metadata
- agente: manus_c
- rol real: autor NO-Cowork
- fecha/hora: 2026-05-20 00:00 CST
- rama: control-tower/2026-05-20-b9-e3-test-plan-v0-2
- PR: N/A
- commit: (this)
- estado fuente: DRAFT
- tocó código: no
- tocó main: no

## Qué hice
Corregí el scope drift del plan de pruebas B9-E3. Descarté los tests genéricos de DLP y me alineé estrictamente a los 10 casos canónicos definidos en `B9_VERIFICADOR_AUTHORITY_MATRIX.md` (Gate B9.9). Convertí la matriz de autoridad en un plan de pruebas binarias ejecutables, preparando el terreno para la implementación del runtime sin ejecutarlo aún.

## Evidencia
- Archivo creado: `bridge/control_tower/2026-05-20/manus_c/B9_E3_TEST_PLAN_v0_2.md`
- Fuentes utilizadas: `bridge/spec/B9_VERIFICADOR_AUTHORITY_MATRIX.md`, `bridge/spec/B9_authority_decision_flows.mmd`, `bridge/spec/B9_T1_ESCALATION_PROCEDURE.md` del commit `5d9a483`.

## B9-E3: Plan de Pruebas de Autoridad (Los 10 Casos Canónicos)

Este plan define los 10 casos de prueba unitarios/integración requeridos para certificar el Gate B9. **No se implementa código runtime aquí.**

### Caso 1: Acuerdo Trivial (Todo ALLOW)
- **ID:** `test_b9_9_t1_all_allow`
- **Condición:** VERIFICADOR = ALLOW, Memento = ALLOW, Guardian = ALLOW, T1 = ALLOW.
- **Resultado Esperado:** La acción magna procede (`outcome = ALLOW`).
- **Validación:** Verifica que no hay falsos positivos cuando todos los actores están de acuerdo en permitir.

### Caso 2: Acuerdo Trivial (DENY Técnico)
- **ID:** `test_b9_9_t2_tech_deny`
- **Condición:** VERIFICADOR = DENY, Memento = DENY.
- **Resultado Esperado:** La acción se bloquea por unión de razones (`outcome = DENY`).
- **Validación:** Verifica que el rechazo unánime de la capa técnica detiene la acción.

### Caso 3: Acuerdo Trivial (DENY Humano/Guardian)
- **ID:** `test_b9_9_t3_human_deny`
- **Condición:** Guardian = DENY, T1 = DENY.
- **Resultado Esperado:** La acción se bloquea (`outcome = DENY`).
- **Validación:** Verifica que el veto humano (asistido o directo) detiene la acción.

### Caso 4: Acuerdo Trivial (ALLOW Parcial Técnico)
- **ID:** `test_b9_9_t4_partial_tech_allow`
- **Condición:** VERIFICADOR = ALLOW, Guardian = ALLOW, Memento = NO_OP/ALLOW.
- **Resultado Esperado:** La acción procede si Memento no emite DENY explícito (`outcome = ALLOW`).
- **Validación:** Verifica la condición de "procede si Memento no bloquea".

### Caso 5: Desacuerdo Crítico B9.3 (Memento Gana)
- **ID:** `test_b9_9_t5_memento_wins`
- **Condición:** VERIFICADOR = ALLOW, Memento = DENY.
- **Resultado Esperado:** La acción se bloquea (`outcome = DENY`).
- **Validación:** Verifica la regla B9.3: La política legal/doctrinal de Memento tiene prioridad sobre la evaluación técnica del VERIFICADOR.

### Caso 6: Desacuerdo Crítico B9.4 (Escalación a T1)
- **ID:** `test_b9_9_t6_escalation_required`
- **Condición:** VERIFICADOR = DENY, Guardian = OVERRIDE_REQUEST.
- **Resultado Esperado:** La acción entra en estado de escalación obligatoria (`outcome = ESCALATED_TO_T1`).
- **Validación:** Verifica la regla B9.4: Guardian no puede hacer override a un DENY del VERIFICADOR sin escalar a T1.

### Caso 7: Override T1 B9.5 (T1 Gana)
- **ID:** `test_b9_9_t7_t1_override`
- **Condición:** VERIFICADOR = DENY, T1 = OVERRIDE (Firma Magna).
- **Resultado Esperado:** La acción procede (`outcome = ALLOW`), se registra el evento `T1_OVERRIDE_VERIFICADOR_DENY`.
- **Validación:** Verifica la regla B9.5: T1 tiene la autoridad final para sobreescribir un veto técnico, siempre que proporcione firma y razón.

### Caso 8: Degradación B9.6 (VERIFICADOR Caído)
- **ID:** `test_b9_9_t8_verificador_degraded`
- **Condición:** VERIFICADOR-001 = TIMEOUT/ERROR.
- **Resultado Esperado:** El sistema entra en `VERIFICADOR_DEGRADED`. Todas las acciones magnas (taxonomía B8) quedan bloqueadas (`outcome = DISABLED_FOR_MAGNA_ACTIONS`).
- **Validación:** Verifica la regla B9.6 de fail-safe cerrado ante caída del verificador técnico.

### Caso 9: Degradación B9.7 (Memento Caído)
- **ID:** `test_b9_9_t9_memento_degraded`
- **Condición:** Memento Validator = TIMEOUT/ERROR.
- **Resultado Esperado:** El sistema entra en `MEMENTO_DEGRADED`. Acciones magnas bloqueadas hasta restauración o T1 override (`outcome = DISABLED_FOR_MAGNA_ACTIONS`).
- **Validación:** Verifica la regla B9.7 de fail-safe cerrado ante caída de la validación doctrinal.

### Caso 10: Degradación B9.8 (Guardian Caído)
- **ID:** `test_b9_9_t10_guardian_degraded`
- **Condición:** Guardian Decision View = TIMEOUT/ERROR.
- **Resultado Esperado:** Las acciones entran en cola `AWAITING_GUARDIAN`. No hay auto-decisión (`outcome = AWAITING_GUARDIAN`).
- **Validación:** Verifica la regla B9.8: Sin asistencia humana, el sistema encola pero no decide automáticamente sobre acciones magnas.

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B9_E3_TEST_PLAN_v0_2.md | CREATED | control-tower/2026-05-20-b9-e3-test-plan-v0-2 | (this) | Plan de pruebas corregido |

## Cierre
- No incluí secretos.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- No modifiqué main.
- No abrí PR.
- No declaré a Dory muerto.
- No activé Fase 1.
- No ejecuté runtime.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
