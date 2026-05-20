# Reglas de Estado de Evidencia

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

Este documento rige la transición del campo `evidence_status` para cada capacidad detectada en el catálogo del Oráculo.

## Los 3 Estados de Evidencia

1. **`STATIC_CATALOG`**
   - **Definición:** La capacidad fue declarada por el Oráculo basada en su conocimiento pre-entrenado o en investigación de documentación web.
   - **Condición:** Es el estado por defecto de todas las capacidades provenientes de M1.
   - **Restricción:** No se puede usar para desbloquear acciones A4-A8. Requiere Risk Overlay R0.

2. **`DOC_VERIFIED`**
   - **Definición:** La capacidad fue verificada leyendo la documentación oficial del proveedor, pero no se pudo ejecutar una llamada API real (ej. falta de fondos, o el proveedor no expone un endpoint `/models`).
   - **Condición:** M2 no usa este estado activamente en este sprint, ya que el objetivo es la verificación empírica, pero se define para completitud arquitectónica.

3. **`REALTIME_VERIFIED`**
   - **Definición:** La capacidad ha sido verificada criptográfica o empíricamente mediante una llamada API real y exitosa.
   - **Condiciones Estrictas (Deben cumplirse TODAS):**
     - Se realizó una petición HTTP a la API oficial.
     - El servidor retornó HTTP 200 OK.
     - El modelo o capacidad se observó directamente en la respuesta (ej. listado en `/models`).
     - Se generó y almacenó un `raw_response_hash` (SHA-256) de la respuesta cruda.
     - El log de la respuesta pasó la regla de redacción de secretos.

## Transiciones Inválidas
- Está estrictamente prohibido marcar una capacidad como `REALTIME_VERIFIED` si la sonda falló (ej. `ACCESS_BLOCKED_API_ERROR`).
- Está estrictamente prohibido marcar una capacidad como `REALTIME_VERIFIED` basándose únicamente en blogs, tweets, o páginas de marketing.

## Overlay de M2
M2 no borra el catálogo estático. M2 genera un archivo `oracle_catalog_m2_realtime_overlay.v0_1.json` que contiene únicamente las actualizaciones de `evidence_status` para las capacidades que lograron ser verificadas. El Auditor o la Cadena aplicarán este overlay sobre el catálogo base.
