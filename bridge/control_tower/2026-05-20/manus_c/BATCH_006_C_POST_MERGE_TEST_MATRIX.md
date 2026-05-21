# BATCH 006 — CÉLULA C: POST-MERGE TEST MATRIX

## Objetivo
Definir la matriz de pruebas obligatoria que debe ejecutarse *después* del merge a `main` y *antes* de autorizar la Fase 1 (Canary). Esta matriz garantiza que el sistema base no se haya degradado por la introducción de Anti-Dory.

## 1. Unit Tests Core (Anti-Dory)
Debe ejecutarse la suite completa de Anti-Dory para confirmar que la integración no rompió dependencias internas.
- **Comando:** `python3 -m pytest tests/anti_dory/ -v`
- **Criterio de Éxito:** 104/104 PASS (incluyendo B1-B10).
- **Tolerancia:** 0 FAIL.

## 2. Integration Tests (State Fabric)
Verificar que la capa de persistencia actual (Supabase) no entra en conflicto con las nuevas estructuras de `b1_anchor_store` y `b3_plan_ledger`.
- **Prueba 1:** Escribir un log estándar en Supabase. (Debe pasar).
- **Prueba 2:** Intentar escribir un anchor falso sin pasar por `b1_anchor_store`. (Debe fallar si RLS está bien configurado).
- **Prueba 3:** Verificar que la lectura de memoria legacy sigue funcionando.

## 3. Guardian Compatibility Tests
Verificar que el script `guardian.py` existente no se rompe con la presencia de `b10_guardian_cron.py` (que debe estar en feature flag OFF).
- **Comando:** `python3 ~/.monstruo/guardian.py`
- **Criterio de Éxito:** Debe imprimir "IDENTIDAD RESTAURADA" sin lanzar excepciones relacionadas con Anti-Dory.

## 4. Memento Compatibility Tests
Asegurar que la estructura actual de Memento no choca con `b4_memento.py`.
- **Prueba:** Generar un resumen de sesión simulado y guardarlo.
- **Criterio de Éxito:** Guardado exitoso, sin bloqueos por parte del validador de Anti-Dory (ya que Fase 1 está OFF).

## Criterio de Bloqueo para Fase 1
**No se puede autorizar la Fase 1 (Canary) si CUALQUIERA de las pruebas anteriores falla.** 
Cualquier fallo indica una regresión en el sistema base, lo cual viola el principio de "Safe Runtime".

## Confirmación
- **NO EJECUCIÓN:** Este documento es solo la matriz de pruebas. No se ha ejecutado ninguna prueba post-merge.
- Requiere autorización explícita de T1 para proceder con la ejecución real una vez que el merge a `main` esté completo.
