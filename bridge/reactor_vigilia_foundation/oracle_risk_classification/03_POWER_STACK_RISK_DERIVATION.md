# Derivación de Riesgo de Power Stacks

**SPRINT:** SPR-RISK-CLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Un "Power Stack" es la combinación de una capacidad de IA (el modelo) con las herramientas, APIs y contextos necesarios para ejecutar una aplicación específica dentro del Monstruo. El riesgo de un Power Stack no es simplemente el riesgo del modelo subyacente.

## Regla de Derivación Base

El `risk_class` de un Power Stack se determina tomando el **máximo nivel de riesgo** entre:
1. La capacidad base (el modelo de IA).
2. Las herramientas o APIs adicionales incluidas en el stack.
3. Los efectos secundarios (side effects) del caso de uso propuesto.

## Modificadores de Riesgo (Elevadores)

Si un Power Stack combina ciertos elementos de alto impacto, su nivel de riesgo base se incrementa (se eleva un nivel, hasta un máximo de R5):

- **Combinación Sensible:** Si el stack incluye `API Real` + `Datos de Usuario (user_data_touch)` + `Escritura de Artefacto (write artifact)`, el riesgo sube al menos un nivel (ej. de R2 a R3).
- **Ejecución Autónoma de Código:** Si el stack incluye la capacidad de ejecutar el código que escribe (ej. sandbox con permisos de red), el riesgo sube automáticamente a R5.
- **Modificación de Estado Global:** Si el stack tiene acceso de escritura a Supabase o al State Fabric de manera no supervisada, el riesgo sube a R5.

## Ejemplo de Derivación

**Capacidad Base:** GPT-4o Vision (Análisis de imágenes)
- *Riesgo Base (Asumiendo API Real):* R1 (Lectura aislada)

**Power Stack Propuesto:** GPT-4o Vision + Acceso a capturas de pantalla del entorno local de Alfredo + Escritura de reporte de auditoría UI.
- *Herramienta:* Captura de pantalla local -> Toca datos del usuario -> R2
- *Acción:* Escritura de reporte -> Escritura limitada -> R3
- *Derivación Final:* El Power Stack se clasifica como **R3**, a pesar de que el modelo base solo se usaba para R1 en aislamiento.
