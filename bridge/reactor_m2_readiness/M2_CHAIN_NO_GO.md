# M2 Chain No-Go

Este documento especifica explícitamente las acciones y estados que están estrictamente prohibidos (No-Go) durante la fase de M2 Readiness.

## Acciones Prohibidas

- **Activación Permanente No Autorizada:** Cambiar el `kill-switch` a `false` de forma permanente sin la selección explícita de `PERMANENT_ACTIVE_R0` por parte de T1.
- **Escalamiento de Autonomía:** Desbloquear operaciones R1 (read-only externas no seguras) o superiores sin autorización.
- **Auto-Evolución:** Ejecutar cualquier script o loop de Self-Evolution.
- **Mutación de Estado Persistente:** Tocar o escribir en Supabase.
- **Mutación de Memoria:** Tocar o escribir en la memoria persistente, Memento, o Anti-Dory.
- **Runtime Productivo:** Crear o habilitar un runtime productivo.
- **Visión de Aplicación:** Implementar o activar `APP_VISION`.
- **Canonización Prematura:** Establecer canon sin revisión de T1.
- **Cierre Prematuro:** Ejecutar `PRE-IA close`.
- **Modificación de Repositorio:** Crear Pull Requests (PR) o hacer merge a `main`.
- **Exposición de Secrets:** Imprimir, loguear o exponer API keys u otros secrets en texto plano.
- **Llamadas Externas No Seguras:** Realizar llamadas a APIs externas a menos que ya estén validadas como seguras y explícitamente dentro del scope autorizado.
