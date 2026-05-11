# Postmortem: Sprint EMBRION-NEEDS-002 Tarea 5 (Embrión-Daddy Bidireccional)

**Autor:** Hilo Ejecutor 2 (`manus_hilo_ejecutor_2`)
**Fecha:** 2026-05-11
**Estado:** PR Creado (Pendiente Audit Cowork DSC-G-008 v2)

## Resumen Ejecutivo

La Tarea 5 implementó el canal bidireccional determinista entre Alfredo (Daddy) vía Telegram y el ciclo autónomo del Embrión. Se reemplazó la invocación directa y bloqueante del loop por una arquitectura asíncrona basada en una cola (`embrion_inbox`), garantizando trazabilidad, rate limiting y protección contra inyecciones de prompt.

El desarrollo se completó con **96 tests PASS**, superando ampliamente el mínimo de 48 requerido en el kickoff.

## Decisiones Técnicas Tomadas

1. **Tabla de Auditoría (CA6):**
   El spec original sugería reutilizar `kernel_audit_log`. Sin embargo, tras inspeccionar el schema en producción, se determinó que está acoplado a requests HTTP (IP, user agent, method). Se decidió crear una tabla dedicada `embrion_audit_log` en la misma migración 0012, optimizada para la trazabilidad de decisiones autónomas y comandos del inbox.

2. **Integración en el Loop (CA5):**
   La integración se realizó en tres bloques quirúrgicos y revertibles (`CA*_INBOX_BEGIN/END`):
   - En `_detect_trigger`: Inyección de comandos con prioridad 9 (por debajo de `mensaje_alfredo=10` y por encima de `contribucion_sabio=7`).
   - En `_check_and_think`: Intercepción de comandos de alto riesgo para forzar MFA (stub).
   - Al cierre de `_check_and_think`: Marcado del comando como `processed` o `rejected` para trazabilidad completa.
   Aunque el spec sugería <50 líneas, la separación en tres bloques requirió 81 líneas totales para garantizar la correctitud de la status machine y la trazabilidad.

3. **MFA Stub (CA7):**
   Se implementó un stub para la autenticación multifactor. Los comandos de alto riesgo (ej. `/override`) se marcan como `requires_mfa`, generan un PIN (sha256) con expiración de 10 minutos, y notifican a Alfredo vía Telegram sin ejecutar el comando. La materialización completa queda diferida a la Tarea 5b.

4. **Smoke E2E Diferido (CA10):**
   El test end-to-end real (Telegram → Kernel → Supabase → Telegram) requiere que el código esté desplegado. Dado que el kernel en producción (`v0.84.8-sprint-memento`) no conoce los nuevos endpoints, este paso se difirió para ejecutarse inmediatamente después del merge y auto-deploy en Railway.

## Resultados de Tests

| Componente | Tests PASS | Cobertura Principal |
|---|---|---|
| Parser | 26 | Comandos canónicos, idempotencia, edge cases. |
| Sanitizer | 31 | 12 ataques (SQLi, cmd-inject, jailbreak) con recall 100%. |
| Inbox Core | 20 | Enqueue, consume, expire, audit. |
| Webhook | 11 | Autorización, parseo de update, fallback. |
| Loop Integration | 8 | Prioridades, MFA stub, manejo de excepciones. |
| **Total** | **96** | *(2 tests reales contra Supabase skippeados por falta de service_role en venv local)* |

## Próximos Pasos

1. Audit de código por parte de Cowork (DSC-G-008 v2).
2. Merge a `main` y auto-deploy en Railway.
3. Ejecución del Smoke E2E real diferido (CA10).
4. Planificación de Tarea 5b (MFA Materialización).
