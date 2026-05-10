# SPEC: Embrión-Daddy Bidireccional v1
**Estado:** DRAFT (Razonamiento Adversarial)
**Autor:** Manus AI
**Fecha:** 2026-05-10

## 1. Objetivo del Documento
Definir la arquitectura conceptual, los riesgos de seguridad y los mecanismos de mitigación para establecer un canal de comunicación bidireccional asíncrono y seguro entre el "Embrión" (El Monstruo en ejecución autónoma) y "Daddy" (Alfredo, el operador humano). Este documento es puramente analítico y no contiene implementación de código.

## 2. Definición del Problema
Actualmente, el embrión puede enviar propuestas (vía `send_proposal_for_hitl`) y recibir respuestas binarias (aprobar/rechazar) a través de botones en Telegram. Sin embargo, carece de la capacidad de:
1.  **Recibir feedback contextual:** Daddy no puede decir "aprobado, pero cambia X parámetro".
2.  **Responder a preguntas abiertas:** El embrión no puede solicitar información faltante ("¿Qué rama debo usar?").
3.  **Iniciativa de Daddy:** Daddy no puede enviar comandos arbitrarios o inyectar contexto al embrión de forma proactiva sin que este haya emitido una propuesta previa.

## 3. Razonamiento Adversarial (Superficie de Ataque)

La apertura de un canal bidireccional libre amplía drásticamente la superficie de ataque. Si el embrión puede interpretar texto libre de Telegram y ejecutar acciones basadas en él, nos enfrentamos a:

### A. Spoofing de Identidad (El "Falso Daddy")
*   **Riesgo:** Un atacante descubre el endpoint del webhook o el bot de Telegram y envía mensajes haciéndose pasar por Alfredo.
*   **Impacto:** Ejecución de código arbitrario, exfiltración de secretos, destrucción de infraestructura.
*   **Mitigación:** 
    *   Validación estricta de `chat_id` (ya implementada).
    *   Firma criptográfica de payloads en el webhook (ya implementada con `TELEGRAM_WEBHOOK_SECRET`).
    *   **Nuevo:** Autenticación multifactor (MFA) para comandos de alto riesgo (ej. requerir un PIN temporal o confirmación biométrica en el dispositivo móvil antes de ejecutar comandos destructivos).

### B. Prompt Injection (Jailbreak)
*   **Riesgo:** Un mensaje legítimo de Daddy contiene texto reenviado de un tercero malicioso (ej. "Revisa este issue de GitHub: [payload malicioso]"). El embrión procesa el texto y su LLM interno es secuestrado.
*   **Impacto:** El embrión ignora la doctrina del silencio, modifica zonas prohibidas o exfiltra datos.
*   **Mitigación:**
    *   Aislamiento de contexto: Tratar el input de Daddy como *datos* (data payload), no como *instrucciones* (system prompt).
    *   Validación de intenciones (Intent Parsing): Un LLM secundario de baja latencia clasifica el mensaje de Daddy antes de pasarlo al loop principal. Si detecta anomalías, rechaza la entrada.
    *   Sanitización estricta de entradas.

### C. Denegación de Servicio (DoS) Asíncrona
*   **Riesgo:** El embrión se queda esperando indefinidamente una respuesta de Daddy para continuar un ciclo crítico, o Daddy inunda al embrión con comandos contradictorios.
*   **Impacto:** Parálisis del embrión (deadlock) o agotamiento del presupuesto (Budget Tracker exhaustion) por procesamiento excesivo de mensajes.
*   **Mitigación:**
    *   Timeouts estrictos para todas las solicitudes de información (ya implementado parcialmente en `expire_loop`).
    *   Rate limiting en el procesamiento de mensajes entrantes.
    *   Cola de prioridad (Priority Queue) para mensajes de Daddy, descartando comandos obsoletos si llega uno más reciente.

## 4. Arquitectura Propuesta (Concepto)

Para resolver las necesidades manteniendo la seguridad, se propone un modelo de **Buzón Asíncrono Tipado**:

1.  **Canal Estructurado:** Daddy no envía texto libre directamente al cerebro del embrión. Envía comandos estructurados (ej. `/context [texto]`, `/override [proposal_id] [nuevo_param]`).
2.  **Buzón de Entrada (Supabase):** El webhook de Telegram no invoca al embrión directamente. Escribe el mensaje en una nueva tabla `embrion_inbox` con estado `pending`.
3.  **Consumo Reactivo:** En su siguiente ciclo (latido), el embrión lee el `embrion_inbox`.
4.  **Parseo Seguro:** El embrión utiliza un parser determinista (no LLM) para comandos conocidos. Solo usa LLM para interpretar el payload si el comando es explícitamente de tipo `context` o `feedback`.
5.  **Trazabilidad:** Cada mensaje de Daddy se vincula a un `cycle_id` o `proposal_id` específico en `embrion_audit_log`.

## 5. Conclusión
La comunicación bidireccional es el siguiente paso lógico, pero debe implementarse como un sistema de paso de mensajes asíncrono y tipado, nunca como un chat directo con el LLM core del embrión. La seguridad perimetral actual (webhook secret + chat_id) es suficiente para la capa de transporte, pero la capa de aplicación requiere protección contra prompt injection y deadlocks asíncronos.
