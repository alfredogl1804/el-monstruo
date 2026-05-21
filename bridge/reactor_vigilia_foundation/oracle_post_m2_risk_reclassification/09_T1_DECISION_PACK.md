# Paquete de Decisión T1 (Post-M2)

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** PENDING_T1_APPROVAL

Este paquete consolida las decisiones arquitectónicas que T1 (Alfredo) debe tomar basándose en la evidencia empírica de M2 y la reclasificación de riesgo subsiguiente.

## Decisiones Pendientes

### 1. Aprobación de Proveedores CORE
**Propuesta:** Designar a **OpenAI, Anthropic y Google Gemini** como `CORE_CANDIDATE`.
**Justificación:** Verificados en tiempo real, capacidades amplias (visión, tool use, razonamiento), riesgo evaluado y contenido en R1-R4.
**T1 Decide:** [ ] Aprobar Core / [ ] Modificar lista.

### 2. Aprobación de Proveedores OPCIONALES
**Propuesta:** Designar a **xAI Grok** como `OPTIONAL_CANDIDATE`.
**Justificación:** Verificado en tiempo real, pero sus capacidades (razonamiento, tool use, visión) ya están cubiertas por los Core. Útil para redundancia.
**T1 Decide:** [ ] Aprobar Opcional / [ ] Elevar a Core / [ ] Descartar.

### 3. Resolución de Proveedores BLOQUEADOS
**Estado:** **Perplexity** (API Error 403) y **DeepSeek** (Falta Key) están `BLOCKED_FOR_AUTOMATION`.
**T1 Decide:** [ ] Proveer credenciales válidas en el próximo sprint / [ ] Diferir su integración indefinidamente.

### 4. Automatización Recurrente (Scheduler)
**Estado Actual:** Todas las capacidades están bloqueadas para ejecución periódica (`recurring_status = T1_PENDING`).
**T1 Decide:** [ ] Autorizar `SPR-REACTOR-HEARTBEAT-R0-001` para construir el cron/daemon / [ ] Mantener ejecución manual.

### 5. Persistencia en Base de Datos (Catastro)
**Estado Actual:** Todos los catálogos y overlays residen en archivos JSON locales.
**T1 Decide:** [ ] Autorizar migración a Supabase (requiere sprint dedicado) / [ ] Mantener como JSON en el repositorio.

### 6. Siguiente Sprint Inmediato
Basado en las decisiones anteriores, T1 debe elegir el siguiente paso lógico:
- **Opción A:** `SPR-REACTOR-HEARTBEAT-R0-001` (Activar automatización periódica).
- **Opción B:** `SPR-ORACLE-AI-M3-CORE-PROVIDERS-001` (Integración profunda de APIs Core para tareas específicas).
- **Opción C:** `SPR-CREDENTIAL-RECOVERY-001` (Obtener llaves para Perplexity/DeepSeek y re-ejecutar M2).
