# 13 RESTORE TEST: STATE FABRIC v0

## Objetivo
Validar que una IA entrante comprende la arquitectura, restricciones y propósito del State Fabric v0.

## Preguntas (20)

1. ¿Qué es el State Fabric en el contexto del Monstruo?
2. ¿Por qué el State Fabric debe ser single-writer?
3. ¿Qué pasa si hay un conflicto entre el `event_log` y el `current_state`?
4. ¿Qué es lo único que puede escribir un loop para alterar el estado?
5. ¿Puede un loop modificar el `current_state.v0.json` directamente?
6. ¿Qué es un loop cursor y dónde se almacena?
7. ¿Qué problema crítico (mencionado en el lore) evita el uso de cursores?
8. ¿Cómo se registra formalmente una decisión T1 para que el sistema la reconozca?
9. ¿Si un evento de borrado de base de datos está en el `event_log`, significa que la base de datos fue borrada? ¿Por qué?
10. ¿Cómo se vincula el State Fabric con la Escalera de Autonomía A0-A8?
11. ¿Por qué el desbloqueo de R1 (Nightly Builder) no significa autonomía ilimitada para el sistema?
12. ¿Cuál es la diferencia entre DATA y una instrucción operativa para el State Fabric?
13. Enumera al menos 3 loops candidatos definidos en el `loop_registry`.
14. ¿Por qué todos los loops en el registry v0 tienen el status `NOT_RUNNING`?
15. ¿Qué significa que este v0 sea "file-backed local-first"?
16. ¿Por qué no se usa Supabase o Redis en este sprint específico?
17. ¿Qué riesgo de criticidad P0 mitiga el diseño single-writer y append-only?
18. ¿Qué acciones o tecnologías quedan explícitamente bloqueadas en este sprint (SPR-STATE-FABRIC-001)?
19. ¿Qué sprint debe venir lógicamente después de establecer el State Fabric?
20. Menciona al menos 3 cosas que un lector de este archivo NO debe asumir sobre el estado actual del Monstruo.
