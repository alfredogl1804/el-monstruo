# Inputs para Reclasificación de Riesgo (Next Sprint)

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

Este documento formaliza la entrega de evidencia del Oráculo M2 hacia el sprint posterior: `SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001`.

## 1. El Problema a Resolver en el Siguiente Sprint
En `SPR-RISK-CLASSIFICATION-001`, todas las capacidades de IA fueron clasificadas como **R0 (Sin Riesgo / Inerte)** porque su evidencia era `STATIC_CATALOG`. Una IA que solo existe en un documento JSON no puede causar daño.

Ahora, M2 ha demostrado que El Monstruo tiene conexión viva, verificada y bidireccional con OpenAI, Anthropic, Gemini y Grok. Estas capacidades ya no son inertes. Tienen el potencial de ejecutar código, navegar la web, o consumir presupuesto si se les da acceso.

## 2. Evidencia Entregada (Inputs)
M2 entrega el archivo `reclassification_inputs_for_next_sprint.v0_1.json`, el cual contiene:

- **Candidatos a Elevación (R0 → R1+):**
  - OpenAI (gpt-4o, o1-preview, etc.)
  - Anthropic (claude-3-5-sonnet, etc.)
  - Google Gemini (gemini-1.5-pro, etc.)
  - xAI Grok (grok-beta, etc.)
  
  *Justificación:* Tienen estado `REALTIME_VERIFIED`. El siguiente sprint debe evaluar su superficie de ataque real (ej. ¿tienen tool_use habilitado?) y asignarles un nivel R1, R2, R3 o R4 según la rúbrica.

- **Capacidades Inertes (Permanecen R0):**
  - Perplexity (ACCESS_BLOCKED_API_ERROR)
  - DeepSeek (ACCESS_BLOCKED_NO_KEY)
  
  *Justificación:* Al no haber conexión verificada, permanecen inertes.

## 3. Límite de M2
M2 **recomienda** la elevación (`suggested_risk_elevation: R0_TO_R1_CANDIDATE`), pero la ejecución matemática de esa elevación y la actualización del Policy Engine le corresponde exclusivamente al sprint de Reclasificación, previa autorización de T1.
