# UNIFIED FACE: Heartbeat Brief

Este documento define la estructura del resumen final que el latido presenta a T1 (Alfredo).

## Estructura Obligatoria del Summary

El archivo `unified_face_heartbeat_summary.v0_1.md` debe contener:

1. **Qué revisó el latido:** Lista de los inputs y precondiciones verificadas.
2. **Qué decisión tomó:** La decisión exacta de la tabla (ej. `REQUEST_T1`).
3. **Si hizo algo o no:** Las acciones tomadas (ej. generó reporte, o `NO_ACTION`).
4. **Por qué no hizo más:** Justificación basada en la Policy y los límites R0.
5. **Qué requiere Alfredo:** Lista clara de las decisiones T1 pendientes.
6. **Qué queda bloqueado:** Cualquier blocker P0 o dependencia faltante.
7. **Qué sprint recomienda después:** Recomendación técnica para el siguiente paso.

## Tono y Voz

- **Una sola voz:** El Monstruo habla como una entidad unificada, no como una colección de loops o scripts.
- **Conciso y directo:** T1 no necesita leer logs de ejecución; necesita el estado y las decisiones pendientes.
- **Transparencia radical:** Si no hizo nada, debe decirlo con orgullo ("Evalué el estado y decidí no hacer nada para proteger la integridad del sistema").
