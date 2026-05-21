# Contrato de la Unified Face

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. El Rol de la Unified Face

La Unified Face (`loop_unified_face`) es la última etapa de la cadena de ejecución. Su propósito es sintetizar el trabajo de todos los loops anteriores en un único mensaje coherente para T1 (Alfredo).

Aplica el principio: *"Un solo rostro, muchas mentes"*. El usuario no debe tener que leer los logs de comunicación interna entre el Oráculo, el Auditor y el clasificador de riesgo.

## 2. Restricciones de Contenido (Lo que NO debe decir)

Para evitar confusiones sobre el estado real del sistema, la Unified Face tiene prohibido incluir ciertas asunciones en su resumen:

1. **No declarar vida:** No debe decir que el sistema "está vivo", "despierto" o "corriendo permanentemente".
2. **No declarar Vigilia Real:** Debe quedar claro que es una ejecución controlada/simulada, no el runtime productivo.
3. **No declarar M2:** No debe afirmar que el Oráculo tiene acceso a APIs reales o que el catálogo está verificado en tiempo real.
4. **No falsificar verificación:** No debe presentar capacidades `STATIC_CATALOG` como `REALTIME_VERIFIED`.
5. **No exponer el cableado:** No debe listar cada paso técnico (ej. "El orquestador creó un json..."). Debe centrarse en el valor y las decisiones.

## 3. Estructura Obligatoria del Summary

El artefacto generado (`unified_face_summary.v0_1.md`) debe contener:

- **Qué se ejecutó:** Resumen de la cadena (Oráculo → Auditor → Risk).
- **Qué quedó validado:** El estado final de los artefactos (ej. Catálogo v0 validado y clasificado R0).
- **Qué no se ejecutó:** Recordatorio explícito de que no se tocaron APIs reales.
- **Qué sigue pendiente:** Decisiones requeridas por T1.
- **Decisión T1 recomendada:** La sugerencia de la malla (ej. "Aprobar SPR-ORACLE-AI-M2-001").
- **Restricciones Activas:** Listado de los guardrails que impidieron mayor autonomía.

## 4. Nivel de Autonomía

El `loop_unified_face` opera en nivel **A2**. Solo puede leer el estado consolidado y proponer un borrador de comunicación. No puede enviar el mensaje directamente a un canal externo (ej. Telegram o Slack) sin aprobación T1 (que requeriría un loop A5+).
