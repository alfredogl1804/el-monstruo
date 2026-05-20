# 13 DO NOT LOSE

**Estado:** EVIDENCE
**Fuente:** assistant_synthesis

## Conceptos Críticos a Preservar

- **El cambio de paradigma de permisos:** Dejar de usar "reglas universales negativas" (ej. "nunca toques main") y pasar a "permisos positivos por sprint" ("en este sprint puedes tocar main en X"). Esto desbloquea la parálisis operativa.
- **La separación de ejecución y auditoría:** Cowork puede ejecutar código, pero **jamás** debe auditar su propio código.
- **El rol de SuperGrok:** Mantener un agente P0/P1 dedicado exclusivamente a encontrar fallas catastróficas (Contrarian).
- **El aprendizaje validado:** Los embriones no deben acumular memoria bruta, sino pericia (soluciones que funcionaron y fueron verificadas).
- **El estado real del Cockpit:** Es un demo read-only. Asumir que es un control plane productivo causará fallas en cadena.
