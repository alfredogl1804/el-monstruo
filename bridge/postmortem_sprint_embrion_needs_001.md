# Postmortem: Sprint EMBRION-NEEDS-001

**Fecha:** 2026-05-10  
**Autor:** Manus Hilo Ejecutor 1 (cuenta principal)  
**Estado del Sprint:** CERRADO  
**Sprint sucesor:** EMBRION-NEEDS-002 (en cierre)

## 1. Resumen Ejecutivo

El Sprint **EMBRION-NEEDS-001** marcó la transición arquitectónica más relevante de El Monstruo desde su nacimiento: el paso de un sistema de ejecución autónoma ciega hacia un modelo gobernado por un **Human-in-the-Loop (HITL) real y bidireccional**. Por primera vez, el embrión propone, espera, escucha y obedece — y el operador humano no necesita estar frente al kernel para autorizarlo.

El sprint cerró las cuatro tareas planificadas (Self-Verifier, Budget Tracker, Write Policy con HITL real y Telegram HITL bidireccional) y validó el ciclo completo en producción con un evento real: Alfredo aprobó la propuesta `6cc845f1-…` desde Telegram, la base de datos registró `approved_by=telegram:7712993094`, y el cron worker (Sprint 002 T1) la ejecutó automáticamente minutos después.

## 2. Timeline y Logros Clave

| Tarea | Entregable | PR / Artefacto | Estado |
| --- | --- | --- | --- |
| T1 — Self-Verifier | `kernel/embrion_self_verifier.py` + tests | merge directo | Cerrado |
| T2 — Budget Tracker | `kernel/embrion_budget.py` con cap/latido y cap diario | merge directo | Cerrado |
| T3 — Write Policy con HITL real | `kernel/embrion_write_policy.py` (propose/approve/reject/expire) | PR #42 (admin merge) | Cerrado |
| T4 — Telegram HITL bidireccional | Notifier extendido + webhook + auth + smoke E2E | PRs #44, #45, #46, #48 | Cerrado |

El smoke E2E real consistió en una propuesta autoejecutada por el embrión, enviada a Telegram con teclado inline (Aprobar/Rechazar), aprobada por Alfredo desde su teléfono, persistida en `embrion_write_proposals` y posteriormente ejecutada por el cron worker `proposal-worker` en Railway.

## 3. Decisiones Técnicas Relevantes

La primera decisión estructural fue **no usar SDK oficial de Telegram**. Se eligió consumir la API HTTP directamente con `httpx` para mantener la superficie de dependencias mínima, evitar versionados opacos y conservar control absoluto de los payloads (especialmente del teclado inline y los `callback_query`). Esto se alineó con la doctrina del silencio: cualquier cosa que toque al embrión debe ser legible y verificable, no una caja negra.

La segunda decisión fue usar **webhook en lugar de long polling**. Polling habría obligado a tener un loop dedicado en el kernel sondeando Telegram cada N segundos, consumiendo presupuesto y creando una superficie temporal de fallos. El webhook es reactivo, gratuito en términos de CPU y permite que la firma de seguridad viva en la URL.

La tercera decisión, la más delicada, fue **abrir un endpoint público para Telegram**. Como Telegram no envía cabeceras `X-API-Key`, hubo que añadir `/v1/embrion/telegram/webhook` a `PUBLIC_INGEST_PATHS` en `kernel/auth.py`. La defensa se mueve a tres capas dentro del handler: (a) validación del secret token en la URL, (b) validación estricta del `chat_id` autorizado, (c) clasificación del tipo de update antes de cualquier lectura de Supabase.

Finalmente, se decidió que la persistencia de propuestas viviría en `embrion_write_proposals` con su propia migración (`migrations/sql/0004_embrion_write_proposals.sql`) y no en `embrion_memoria`. Esto permite consultas de cron worker eficientes y aísla el ciclo HITL de la memoria narrativa del embrión.

## 4. Bugs y Roces Encontrados

Durante el sprint emergieron tres clases de problemas que conviene fijar para sprints futuros.

El primero fue un **mismatch de firma en `send_proposal_for_hitl`**. El notifier exponía una firma compacta mientras los call sites pasaban kwargs descriptivos (`risk_level`, `target`, `reason`, `cost_estimate_usd`, `expires_at`). Se consolidó la firma definitiva con kwargs explícitos y se actualizó la documentación del módulo.

El segundo fue un **error de estructura al leer respuestas de Telegram**: la API devuelve un envelope `{"ok": true, "result": {…}}`, pero algunas rutas asumían acceso directo a `message_id`. Se centralizó el unwrap en helpers internos del notifier para que ningún consumidor toque el envelope crudo.

El tercero, y el que más drenó tiempo, fue el **branch drift silencioso**. El repositorio aloja simultáneamente al menos cuatro hilos activos (Ejecutor Técnico Embrión, RLS Hardening, Catastro y Bridge) y la rama activa cambia sin previo aviso entre invocaciones de shell. Se establece como regla operativa: verificar `git branch --show-current` inmediatamente antes de cualquier `git add`/`git commit` y usar stash inmediato para archivos que no pertenezcan al hilo activo.

## 5. Lecciones Aprendidas

La primera lección es que **HITL real significa probar en producción**. Ningún mock de Telegram captura la latencia real, los modos de fallo de la red móvil o el comportamiento exacto del rendering de teclados inline. La validación E2E con un dispositivo físico de Alfredo aprobando una propuesta real fue el único hito que cerró el sprint con confianza plena.

La segunda lección es que **simplificar integraciones gana siempre**. Renunciar al SDK de Telegram y usar httpx directo redujo la deuda futura y permitió ajustar payloads sin pelear contra abstracciones.

La tercera lección es que **la concurrencia de hilos en un mismo repo necesita disciplina ritual, no técnica**. Ninguna herramienta de git previene el branch drift porque el problema es operativo, no técnico. La regla `verificar-stashear-commitear` es la única defensa.

## 6. Cierre

El Sprint EMBRION-NEEDS-001 se declara **CERRADO**. La infraestructura base para el control humano sobre las acciones del embrión está operativa, validada en producción y documentada. El embrión respira, propone, espera y obedece.

> **Frase canónica de cierre:** "El Monstruo respira, pero ahora la correa está en nuestras manos — y el embrión la siente."
