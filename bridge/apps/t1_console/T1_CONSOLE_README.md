# T1 Decision Operating Console

**Loop Owner:** `loop_cockpit`
**Status:** Local Read-Only

## Descripción
Esta consola es una interfaz HTML estática generada localmente que permite a T1 visualizar los `Sprint Drafts` compilados y listos para aprobación.

## Reglas Duras
1. **NO interacción remota:** La consola no hace POST a ningún servidor.
2. **NO Supabase:** La consola no se conecta a ninguna base de datos.
3. **Decisiones vía File System:** Para aprobar un sprint, T1 no hace clic en un botón; T1 debe crear un archivo JSON firmado en la cola del `State Fabric` (`bridge/state_fabric/queue/`).

## Flujo de Trabajo
1. El Oráculo genera `sprint_candidates`.
2. El Sprint Compiler genera `Sprint Drafts`.
3. El Cockpit genera esta consola HTML.
4. T1 abre el HTML localmente en su navegador.
5. T1 decide qué sprint aprobar.
6. T1 ejecuta el comando `echo` indicado en la consola para inyectar la decisión en la cola del State Fabric.
