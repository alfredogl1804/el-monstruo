# ALLOWED R0 ACTIONS

Si el latido toma la decisión `RUN_ORACLE_CHAIN_R0` o `RUN_AUDIT_ONLY_R0`, solo puede ejecutar acciones que cumplan con los siguientes criterios:

## Criterios R0 (Seguridad Absoluta)

1. **Local Only:** Sin llamadas de red externas.
2. **Read-Only State:** Puede leer el State Fabric, pero solo escribir deltas/overlays o hacer append al event_log.
3. **No Side Effects:** Sin despliegues, sin commits, sin mutaciones a la base de datos (Supabase).

## Acciones Específicas Permitidas

- **`read_state` (A0):** Leer el estado actual.
- **`write_log` (A1):** Agregar un evento al event log.
- **`write_overlay` (A2):** Crear un archivo JSON de overlay.
- **`write_report` (A3):** Generar un reporte en Markdown.
- **`run_local_chain` (A3):** Orquestar loops locales que cumplan con A0-A3.

Cualquier otra acción solicitada al Dispatcher durante el latido debe ser denegada.
