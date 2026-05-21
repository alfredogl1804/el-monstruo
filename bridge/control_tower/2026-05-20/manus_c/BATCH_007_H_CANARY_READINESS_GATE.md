# BATCH 007 — CÉLULA H: CANARY READINESS GATE

## Objetivo
Establecer los criterios exactos y binarios que deben cumplirse para que T1 autorice la transición del sistema a "Fase 1 Canary" (donde Anti-Dory audita el tráfico real de los agentes, pero solo emite warnings, sin bloquear).

## Pre-Requisitos (Checklist Binario)

1. [ ] **Batch 005 v0.2 Mergeado:** El código base de Anti-Dory está en `main`.
2. [ ] **Supabase Aplicado:** Las migraciones 0050 y 0051 están en producción.
3. [ ] **Post-Merge Tests PASS:** La matriz de la Célula C se ejecutó en `main` y dio 104/104 PASS.
4. [ ] **CVDS Smoke Test PASS:** El Mini Bench de 100 casos (Célula E) y los 20 Hidden Fixtures (Célula F) arrojaron métricas dentro de la tolerancia (Célula G).
5. [ ] **Firma de Cowork:** El agente auditor Cowork ha firmado un DSC aprobando el diseño de seguridad.
6. [ ] **Firma de Perplexity PBA:** El agente arquitecto ha validado que no hay degradación de performance.

## Lista de No-Go (Bloqueadores Inmediatos)

La Fase 1 **NO** puede iniciar si ocurre alguna de las siguientes condiciones:
- Fallo en cualquier unit test del sistema base tras el merge.
- Falso Positivo (FPR) > 10% en el CVDS Smoke Test.
- Falso Negativo (FNR) > 2% en los Known Cases del CVDS Smoke Test.
- Exposición de cualquier secreto o clave privada durante las pruebas.
- Fallo en la verificación de firma `minisign` con la clave pública real.

## Reglas de Parada (Kill Switch durante Canary)

Una vez en Fase 1, el sistema debe revertirse automáticamente a OFF (o ejecutarse el Rollback Plan de la Célula D) si:
- Un agente legítimo es bloqueado (falso HALT) y no puede continuar su tarea.
- La latencia de las respuestas aumenta más de 500ms debido a las validaciones de B8/B9.
- Supabase reporta un aumento inusual de conexiones o errores en las tablas de Anti-Dory.

## Confirmación
- **NO FASE 1:** Este documento es solo la definición de la puerta de enlace. No autoriza el inicio de la Fase 1.
