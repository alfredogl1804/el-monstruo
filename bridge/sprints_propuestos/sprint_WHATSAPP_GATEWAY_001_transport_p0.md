# Sprint WHATSAPP_GATEWAY_001 — Transport conversacional P0 (sin captura sensible)

**Autor:** Cowork (Arquitecto T2-A) · **Fecha:** 2026-05-27 · **Estado:** DRAFT para firma T1
**Paradigma:** T1-MAGNA-001 = C (invocación primaria). T1-MAGNA-002 = D (sin SMP).
**Owner ejecución:** Manus E1 (backend/gateway). **Lane:** transport puro.
**Objetivo:** Transport conversacional WhatsApp como canal P0 del Monstruo bajo paradigma D (sin SMP), sin captura passive sensible.

## Objetivo
Transport conversacional WhatsApp como canal P0 del Monstruo: el usuario le habla por WhatsApp, el kernel responde por el mismo canal. Abre el mercado LATAM (72% no abre apps nuevas). **NO** captura passive a Cronos (eso depende de SMP, diferido por D).

## Alcance bajo D (crítico)
- ✅ Recibir mensajes entrantes, rutear al kernel (`/v1/agui/run`), responder texto.
- ✅ Comandos básicos, sesión por número.
- ❌ NO persistir conversaciones íntimas a Cronos (requiere SMP).
- ❌ NO redirección "Modo Confidente" silenciosa (requiere SMP).
- Guardarraíl: si el kernel detecta contenido sensible, responde pero NO persiste a memoria soberana hasta SMP.

## Decisiones T1 pendientes (NO inventar)
- **TBD-1:** WhatsApp Cloud API (Meta directo) vs BSP (Twilio/360dialog/etc.). Recomendación Cowork: Cloud API directo para soberanía (Objetivo #12), menos intermediario.
- **TBD-2:** número de WhatsApp Business + verificación Meta Business.

## Tareas
- T1: `apps/whatsapp_gateway/` — webhook receptor (verificación de firma Meta) + cliente de envío.
- T2: puente al kernel — reusar el cliente AG-UI existente (NO duplicar; ver `apps/mobile/gateway/`). Mapear mensaje WhatsApp → run del kernel → respuesta.
- T3: manejo de sesión por número (efímero, sin persistencia sensible bajo D).
- T4: rate-limit + manejo de webhooks de estado (delivered/read).
- T5: tests — webhook signature verification, ruteo, respuesta, NO-persistencia sensible.

## Reglas duras
- Cero secrets en código: `WHATSAPP_TOKEN` / `META_APP_SECRET` vía `os.environ` (DSC-S-001..005).
- Verificación de firma Meta obligatoria en el webhook (anti-spoof).
- Anti-duplicación: reusar puente AG-UI; no reimplementar el cliente del kernel.

## Criterios de Cierre
PR sin auto-merge, audit Cowork DSC-G-008. Verde = mensaje WhatsApp → respuesta del kernel end-to-end en número de prueba, firma verificada, cero persistencia sensible. **Comando reproducible:** `pytest apps/whatsapp_gateway/tests/ -v`. **Artifact:** screenshot del thread WhatsApp ↔ kernel respondiendo. **Verificación firma:** request curl con firma inválida debe rechazar 401.

— Cowork T2-A, DRAFT (local; push pendiente API GitHub)
