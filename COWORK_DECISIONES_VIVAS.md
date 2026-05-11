
### 2026-05-11 — Sprint EMBRION-NEEDS-002 Tarea 5 (Embrión-Daddy Bidireccional)
*   **Decisión:** Crear tabla dedicada `embrion_audit_log` en lugar de reusar `kernel_audit_log`.
*   **Justificación:** El schema de `kernel_audit_log` está acoplado a requests HTTP (IP, method, path), mientras que el inbox requiere trazabilidad de decisiones autónomas (`cycle_id`, `command_type`, `decision`).
*   **Decisión:** Integración del inbox en `embrion_loop.py` distribuida en tres bloques (`_detect_trigger`, MFA en `_check_and_think`, y cierre con `mark_processed`).
*   **Justificación:** Mantener la coherencia de la status machine y garantizar que comandos de alto riesgo no pasen a `_think` sin autorización (MFA stub).
*   **Decisión:** Smoke E2E real diferido a post-merge.
*   **Justificación:** El código nuevo (webhook, inbox) no existe en el kernel de producción actual (`v0.84.8`). El test E2E requiere deploy en Railway.
