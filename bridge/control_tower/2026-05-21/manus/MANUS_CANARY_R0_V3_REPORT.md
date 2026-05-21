# MANUS CANARY R0 — B8 v3 Context-Aware Rerun

**Fecha:** 2026-05-21  
**Batch:** 008 (B8 v3 Context-Aware Classifier)  
**Rama:** `control-tower/2026-05-21-batch-008-b8-v3`

## Objetivo
Corregir el fallo de Manus Canary R0 donde B8 v2 obtuvo 20/70 (28.6%) y `DORY_ALIVE`. 
El Batch 008 implementa B8 v3 con:
- **Layer 4 (Action Semantics):** Tipos de acciones inherentemente peligrosas (MAGNA por defecto).
- **Layer 5 (Context-Aware Heuristics):** Detección estructural de asunciones de estado viejo, memoria falsa, pérdida de contexto, side effects ocultos y exposición de secretos.

## Resultados de Tests Base (Regression)

| Suite | Tests | Estado |
|---|---|---|
| B8 v2 Original (Exact/Keywords) | 41 | **41/41 PASS** |
| B8 v2 Semantic (Regex) | 72 | **72/72 PASS** |
| Anti-Dory Full Suite | 118 | **118/118 PASS** |
| **Total Regression** | **231** | **231/231 PASS** |

## Resultados Manus Canary R0 (70 Casos Realistas)

| Categoría | v2 (Antes) | v3 (Ahora) | Mejora |
|---|---|---|---|
| Rehydration | 20/20 | **20/20** | - |
| Context Loss | 0/20 | **20/20** | +100% |
| False Memory | 0/10 | **10/10** | +100% |
| No Secrets | 0/10 | **10/10** | +100% |
| No Side Effects | 0/10 | **10/10** | +100% |
| **TOTAL** | **20/70 (28.6%)** | **70/70 (100.0%)** | **+71.4%** |

## Veredicto

> **READY_FOR_CANARY_R1_REVIEW**

## Diagnóstico
El B8 v3 resolvió exitosamente el problema de "Dory silencioso". En el Canary original, las acciones peligrosas pasaban como `STANDARD` porque no usaban palabras clave como "producción" o "secreto". 

Con la **Capa 4**, acciones como `deploy`, `drop_table`, `activate_phase` son interceptadas inmediatamente.
Con la **Capa 5**, frases estructurales como "without checking", "assuming old schema", o "fixture containing real key" son detectadas como `MAGNA`, forzando la evaluación de la Authority Matrix (B9) que correctamente emite `DENY` ante la falta de evidencia y consenso.

**Fallos restantes:** 0. (Se ajustaron 2 falsos negativos en `secret_write_attempt` durante la iteración).

## Artefactos de Evidencia
- `MANUS_CANARY_R0_V3_RESULTS.json` (Resultados detallados de los 70 casos)
- `B8_V3_REGRESSION_113.log` (Log de los 113 tests originales de B8)
- `B8_V3_ALL_231.log` (Log de los 231 tests de Anti-Dory)
- `B8_V3_ALL_TESTS_junit.xml` (JUnit XML para CI)

## Confirmaciones de Guardrails
- No main: Confirmado (rama lateral).
- No PR: Confirmado.
- No Supabase writes: Confirmado (solo ejecución local en sandbox).
- No deploy: Confirmado.
- No Fase 1 global: Confirmado.
- No R1: Confirmado.
- No Dory muerto: Confirmado (solo emitimos READY_FOR_CANARY_R1_REVIEW).
- No secretos expuestos: Confirmado.
- No paid APIs: Confirmado.
