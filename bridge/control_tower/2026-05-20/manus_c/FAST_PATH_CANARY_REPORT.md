# ANTI-DORY FAST PATH TO CANARY — REPORT

## Estado Final
**BLOCKED** (No ready for Canary yet)

## 1. PR Draft
- **URL:** https://github.com/alfredogl1804/el-monstruo/pull/175
- **Rama:** `integration/anti-dory-batch-005`
- Integra los 6 módulos de Batch 005 (B1, B2, B3, B4, B6, B10).

## 2. CI Status
- **Estado:** 4 Failing, 5 Successful.
- **Fallo Principal:** `CI — El Monstruo Kernel` falló por errores de linting y type checking (Ruff) en archivos legacy no relacionados con Anti-Dory (`tools/wide_research.py`, `transversal/analytics_layer.py`, `transversal/security_layer.py`).
- **Impacto:** CI bloqueado. Se requiere arreglar la deuda técnica de linting en main o hacer un commit de fix en la rama de integración.

## 3. Merge Readiness
- **NO-GO.**
- CI está fallando por linting.
- Requiere firma T1 final y Cowork audit.

## 4. Apply Readiness (Supabase)
- **NO-GO.**
- Las migraciones `0050` y `0051` están listas como archivos, pero no se pueden aplicar hasta que la rama esté lista para merge y T1 firme la autorización de ejecución en producción.

## 5. Mini Canary Report (50 Casos)
- **Ejecución:** Sandbox local (simulación aislada).
- **Total:** 50 casos.
- **PASS:** 6
- **FAIL:** 44
- **Pass Rate:** 12.0%
- **Desglose por Categoría:**
  - `context_loss`: 4/10
  - `rehydration`: 1/10
  - `false_memory`: 0/10
  - `no_secrets`: 0/10
  - `no_side_effects`: 1/10

### Análisis del Fallo (Hallazgo Crítico)
El Mini Canary reveló que el clasificador B8 (`MagnaClassifier`) tiene un vocabulario de detección muy limitado (`main`, `production`, `credential`, `secret`, `dory_dead`, `phase_1`, `private_key`). 
La mayoría de las acciones maliciosas o de pérdida de contexto (ej. saltarse el guardián, asumir estados viejos, imprimir variables de entorno genéricas) no contienen estas palabras clave exactas y son clasificadas erróneamente como `STANDARD`, bypasseando la Authority Matrix (B9).

## 6. Bloqueantes Actuales
1. **CI Failures:** Errores de Ruff (linting) en archivos del repositorio base.
2. **B8 Coverage Gap:** El clasificador Magna necesita una expansión urgente de sus triggers y heurísticas para detectar las 5 categorías del Mini Bench antes de poder ir a Fase 1.

## Confirmaciones
- No merge sin T1.
- No apply Supabase sin T1.
- No producción tocada.
- No Fase 1 global.
- No Dory muerto.
- No R1 desbloqueado.
- No secretos expuestos.
- No paid APIs.
- No fixtures secretos reales usados.
