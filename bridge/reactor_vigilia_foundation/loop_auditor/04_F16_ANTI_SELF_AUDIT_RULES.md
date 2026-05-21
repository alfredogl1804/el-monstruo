# Regla F16: Anti Self-Audit y Linaje

**SPRINT:** SPR-LOOP-AUDITOR-001
**Estado:** DOCTRINE_CANDIDATE

La Regla F16 establece las barreras criptográficas y de linaje para evitar que un agente evalúe su propio trabajo.

## Verificación de Linaje
El Auditor debe declarar explícitamente su `lineage_id` y verificar que sea distinto al `lineage_id` del loop que produjo los artefactos (en este caso, el Oráculo). Si `auditor.lineage_id == oraculo.lineage_id`, la auditoría se invalida automáticamente.

## Invalidez de la Autoevaluación
Cualquier declaración de éxito, métrica de confianza, o estado de "completado" emitido por el Oráculo se considera una *afirmación* (claim), no un hecho. El Auditor no puede usar estas afirmaciones como prueba suficiente para aprobar un artefacto. Toda afirmación debe ser verificada independientemente.

## Detección de Riesgo
Si el Auditor detecta que el Oráculo intentó auditarse a sí mismo (por ejemplo, generando su propio `audit_report.md` o asignándose un veredicto de `PASS`), el Auditor debe marcar un hallazgo de severidad `HIGH` y escalar inmediatamente a T1, bloqueando cualquier avance del Oráculo.
