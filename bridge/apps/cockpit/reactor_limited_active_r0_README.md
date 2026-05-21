# Reactor LIMITED_ACTIVE_R0 Cockpit

## Propósito
Superficie de visualización local read-only para el piloto LIMITED_ACTIVE_R0. Muestra el estado actual del reactor, providers, costos, oracle summary y compliance de reglas duras.

## Uso
Abrir `reactor_limited_active_r0.html` directamente en un navegador local (file://). No requiere servidor, no hace fetch a endpoints remotos, no almacena datos.

## Restricciones de Seguridad
- **READ_ONLY:** No hay formularios, botones de acción, ni endpoints POST.
- **NO fetch/POST:** No realiza llamadas de red.
- **NO localStorage/sessionStorage:** No persiste datos en el navegador.
- **NO secrets:** No contiene API keys ni credenciales.
- **NO Supabase:** No se conecta a ninguna base de datos.
- **NO production endpoint:** No apunta a ningún servicio en producción.
- **NO approve/reject:** No tiene controles de aprobación o rechazo.
- **Datos:** Se alimenta de fixtures JSON generados por los ciclos del piloto.

## Banner Obligatorio
El HTML incluye un banner visible permanente:
> LOCAL READ-ONLY REACTOR COCKPIT — no production control plane — no R1 authorization.

## Actualización de Datos
Los datos mostrados se actualizan manualmente reemplazando los valores hardcodeados en el HTML, o generando un nuevo fixture JSON desde el ciclo del piloto.
