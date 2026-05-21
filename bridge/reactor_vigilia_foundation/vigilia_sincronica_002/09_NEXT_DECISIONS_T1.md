# Decisiones Pendientes T1

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

Al finalizar exitosamente este sprint, la arquitectura de Vigilia Sincrónica (orquestador, handoffs, dispatcher, loops, state fabric) está validada end-to-end en un entorno controlado (M1).

Las siguientes decisiones requieren la autoridad de T1 (Alfredo) para avanzar:

## 1. Evolución a M2 (APIs Reales)
- **Propuesta:** Autorizar `SPR-ORACLE-AI-M2-001`.
- **Implicación:** El Oráculo conectará con OpenAI, Anthropic, Perplexity, etc., para verificar las capacidades en tiempo real, cambiando la evidencia de `STATIC_CATALOG` a `REALTIME_VERIFIED`.
- **Riesgo:** Consumo de créditos/tokens. Requiere inyección de secrets al sandbox.

## 2. Reclasificación de Riesgo Post-M2
- **Propuesta:** Una vez verificado en M2, ejecutar un sprint para actualizar el `capability_risk_overlay` de R0 a los niveles reales (R1-R4) según la superficie de ataque confirmada.
- **Implicación:** Permitirá desbloquear acciones de mayor autonomía (A2-A5) para las capacidades verificadas.

## 3. Despliegue del Daemon (Runtime)
- **Propuesta:** Autorizar el desarrollo de un scheduler/daemon ligero que ejecute la cadena periódicamente.
- **Implicación:** El Monstruo comenzará a operar en "background" (Vigilia real).
- **Riesgo:** Requiere infraestructura persistente (Persistent Computing) fuera del sandbox efímero.

## 4. Expansión de Loops
- **Propuesta:** Instanciar el `loop_vigia` o el `loop_memoria_memento` para integrarlos a la cadena.
- **Implicación:** Aumenta la complejidad de la cadena, pero añade monitoreo de anomalías o compactación de memoria.
