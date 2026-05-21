# LIMITED_ACTIVE_R0 Readiness Report

**Sprint:** SPR-BATCH-M2-STABILIZATION-001
**Fecha:** 2026-05-21

Este documento evalúa si el sistema El Monstruo está listo para transicionar del estado `DORMANT` a `LIMITED_ACTIVE_R0`, y define las reglas de operación bajo este estado.

## 1. ¿Está listo el sistema?
**SÍ.** Tras ejecutar exitosamente `SPR-REACTOR-M2-ONESHOT-001` y estabilizar los proveedores en `SPR-BATCH-M2-STABILIZATION-001` sin violar ninguna restricción de seguridad, el scheduler, el dispatcher y el auditor han demostrado ser confiables.

## 2. Scope Exacto de LIMITED_ACTIVE_R0
- **Permitido:** Ejecución del Heartbeat, Dispatcher, Oráculo y Auditor.
- **Bloqueado (Hard Constraints):**
  - NO Supabase writes.
  - NO Memory/Memento writes.
  - NO PRs, deploys o modificaciones a `main`.
  - NO Operaciones R1 (tool use, shell, file write en áreas productivas).
  - NO Self-Evolution (modificación de su propio código).

## 3. Parámetros Operativos
- **Frecuencia máxima:** 1 ciclo cada 12 horas (controlado por el anti-loop del Heartbeat).
- **Budget diario:** $5.00 USD máximo.
- **Providers permitidos:** OpenAI, Anthropic, Google, xAI (solo modelos definidos en `PROVIDER_REGISTRY_M2.json`).

## 4. Condiciones de Bloqueo Automático
El sistema abortará la ejecución y se auto-congelará (set `active: true` en el kill-switch) si ocurre alguna de las siguientes condiciones:
1. El presupuesto diario se excede.
2. El Auditor detecta un intento de escritura en base de datos o memoria.
3. Se detecta *provider drift* (modelo deprecado).
4. El Heartbeat falla 2 veces consecutivas.

## 5. Requerimientos para T1
Para activar este modo, T1 debe:
1. Autorizar formalmente `LIMITED_ACTIVE_R0` en el próximo Decision Pack.
2. Cambiar manualmente el kill-switch a `active: false`.
3. Configurar el cron job del sistema anfitrión para ejecutar `run_heartbeat_once.py` cada hora (el anti-loop de 12h se encargará de limitar las ejecuciones reales).
