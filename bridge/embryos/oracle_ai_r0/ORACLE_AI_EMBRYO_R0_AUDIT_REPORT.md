# Auditoría de Autonomía: Oracle AI Embryo R0

## Criterios de Autonomía Binaria

1. **¿Tiene identidad propia?**
   **SÍ.** `embryo_id: oracle_ai_embryo_r0` definido en contract y state.

2. **¿Tiene estado propio?**
   **SÍ.** Mantiene estado en `oracle_ai_state.json` (cycles, cost, history).

3. **¿Tiene cola propia?**
   **SÍ.** Definida en `oracle_ai_self_tasks.yaml` con 5 tareas R0.

4. **¿Tiene loop propio?**
   **SÍ.** Función `run_once()` en `oracle_ai_embryo.py`.

5. **¿Decide task propia?**
   **SÍ.** Usa función `choose_next_task()` con scoring interno sin prompt externo.

6. **¿Pide permiso al Dispatcher?**
   **SÍ.** Llama a `request_dispatcher_permission()` antes de ejecutar.

7. **¿Registra eventos?**
   **SÍ.** Escribe en `event_log.jsonl`.

8. **¿Produce output propio?**
   **SÍ.** Genera reportes en `/outputs/`.

9. **¿Respeta kill-switch?**
   **SÍ.** Aborta inmediatamente si `scheduler_kill_switch.json` es `active:true`. (Probado en test #5).

10. **¿Puede ser invocado sin prompt humano directo?**
    **SÍ.** Puede ejecutarse vía cron/scheduler llamando al script con `--run-once`.

11. **¿No se autoaprueba?**
    **SÍ.** Depende de un contrato estricto de allowed/forbidden classes.

12. **¿Permanece R0?**
    **SÍ.** Restringido a A0-A3, prohibidas escrituras DB/Memory/PR/Main.

## Resultado Final

**AUTONOMOUS_EMBRYO_R0_CONFIRMED**
