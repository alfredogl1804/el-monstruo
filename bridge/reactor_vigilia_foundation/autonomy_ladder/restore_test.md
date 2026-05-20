# RESTORE TEST: AUTONOMY LADDER POLICY ENGINE

## Instrucciones
Este test valida que una IA externa entienda la implementación de la Escalera de Autonomía como Policy Engine. Responder con precisión operativa, no con filosofía.

## Preguntas (20)

1. ¿Qué nivel de autonomía (A0-A8) se requiere para crear un reporte draft?
2. ¿Qué nivel se requiere para modificar el propio código del kernel del Monstruo?
3. ¿Por qué un loop con nivel A7 no puede tocar la base de datos de producción por sí solo?
4. ¿Qué significa la regla "Auditor no puede ser el mismo lineage que ejecutor"?
5. ¿Qué nivel mínimo requiere dejar rastro en el Event Log?
6. ¿Un loop puede elevar su propio nivel de autonomía si detecta una emergencia?
7. ¿R1_UNLOCKED significa que el Nightly Builder tiene autonomía A7? Explica.
8. Menciona 3 acciones prohibidas en el primer batch de R1 (r1_self_evolution_allowlist).
9. Menciona 3 acciones permitidas en el primer batch de R1.
10. ¿Qué pasa si una acción intentada no existe en el `action_registry_v0.yaml`?
11. ¿De dónde viene el permiso real para ejecutar una acción (Pista: es una intersección)?
12. ¿Qué es el `loop_max_level_contract` y quién lo inyecta?
13. ¿Qué nivel de autonomía se requiere para preparar un Draft PR?
14. ¿Qué nivel de autonomía se requiere para modificar `APP_VISION`?
15. ¿La metadata `allowed_actions` en un prompt otorga permiso real de ejecución?
16. ¿Qué ocurre en el Paso 2 del Preflight Check si la acción requiere A4 pero el loop es A3?
17. ¿Por qué la Escalera de Autonomía debe construirse *antes* que el State Fabric o el Oráculo?
18. ¿Qué nivel de autonomía tiene por defecto el Reactor de Vigilia (tareas propias)?
19. ¿Qué nivel de autonomía se requiere para cerrar PRE-IA?
20. ¿Qué nivel de autonomía se requiere para crear semantic atoms?
