# Preflight Check — M2 One-Shot

Este documento registra la validación de las condiciones previas antes de ejecutar la cadena M2 en modo one-shot.

## Constraints de Ejecución (T1 Decision)

| Constraint | Requisito | Estado |
|------------|-----------|--------|
| **Kill-switch inicial** | `active: false` (solo para esta corrida) | PASS |
| **Scheduler permanente** | NO activo | PASS |
| **Anti-loop** | Limpio (ventana de 12h) | PASS |
| **Dispatcher** | Disponible | PASS |
| **Oráculo shadow** | Disponible | PASS |
| **Auditor** | Disponible | PASS |
| **Providers verificados** | 4/6 (OpenAI, Anthropic, Google, xAI) | PASS |
| **Providers excluidos** | Perplexity, DeepSeek | PASS |
| **Budget cap** | 2.00 USD | PASS |
| **Max calls per provider**| 1 | PASS |
| **Retries** | 0 | PASS |

## Reglas Duras a Cumplir Durante la Ejecución

- El Oráculo shadow solo debe producir un *candidate report*.
- El Auditor solo debe revisar el reporte.
- Ningún loop puede escribir en memoria (Supabase, Memento, Anti-Dory).
- Ningún loop puede crear PRs o hacer deploy.
- Ningún loop puede modificar `APP_VISION`, canon o ejecutar `PRE-IA close`.
- Ningún loop puede desbloquear operaciones R1.
- Ningún loop puede autoaprobarse.

*La ejecución de la cadena M2 procederá solo si todos los constraints en "PENDING" se cambian a "PASS" y el kill-switch se desactiva temporalmente.*
