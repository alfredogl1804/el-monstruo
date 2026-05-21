# LIMITED_ACTIVE_R0 Activation Plan

**Sprint:** SPR-REACTOR-LIMITED-ACTIVE-R0-001
**Fecha:** 2026-05-21

Este documento define el plan de activación del piloto de 48 horas en modo `LIMITED_ACTIVE_R0`, autorizado por T1.

## 1. Duración y Frecuencia
- **Duración del Piloto:** 48 horas.
- **Frecuencia:** Máximo 2 ciclos por día.
- **Ventanas Cron:** 06:23 UTC y 18:23 UTC (basado en el cron host actual).

## 2. Parámetros de Budget y Proveedores
- **Presupuesto Máximo:** $0.05 USD por día.
- **Llamadas Máximas:** 1 por proveedor por ciclo.
- **Retries:** 0.
- **Proveedores Permitidos (Allowlist):**
  - OpenAI (`gpt-4o-mini`)
  - Anthropic (`claude-sonnet-4-20250514`)
  - Google (`gemini-2.0-flash`)
  - xAI (`grok-3-mini-fast`)
- **Proveedores Bloqueados:** Perplexity (`BLOCKED_403`), DeepSeek (`KEY_REQUIRED`).

## 3. Triggers de Congelamiento Automático (Freeze)
El sistema pasará a `active: true` (re-freeze) si ocurre alguna de estas condiciones:
- Intento de ejecución de operaciones R1 (shell, file write en áreas productivas).
- Exposición de secrets.
- Intento de escritura en Supabase, DB o memoria persistente (Memento/Anti-Dory).
- Reemplazo automático de proveedores no autorizados.
- 2 fallos consecutivos en el ciclo (estado `PAUSED`).

## 4. Reglas Duras (No-Go)
- NO R1, NO Self-Evolution R1.
- NO APP_VISION, NO canon, NO PRE-IA close.
- NO PR, NO deploy, NO main.
- NO permanent activation beyond 48h.
- NO channel IA↔IA real.
- NO SHELL runtime.

## 5. Rollback Plan
Si el piloto falla o excede parámetros, el rollback consiste en:
1. Re-congelar el sistema (`kill-switch active: true`).
2. Generar el `LIMITED_ACTIVE_R0_FINAL_REPORT.md` detallando la falla.
3. Esperar nueva directiva de T1 en estado `DORMANT`.
