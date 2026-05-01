# Biblia de Implementación: Claude Cowork / Managed Agents (Anthropic)

**Fecha de Lanzamiento:** 8 de abril de 2026
**Versión:** Managed Agents v1 (Claude Cowork)
**Arquitectura Principal:** Desacoplamiento de Cerebro (Brain), Manos (Hands/Sandbox) y Sesión (Session Log).

## 1. Visión General y Diferenciador Único

Claude Cowork es la interfaz de usuario para la arquitectura subyacente de **Managed Agents** de Anthropic. Su diferenciador técnico más importante es el **desacoplamiento radical** de los componentes del agente. En lugar de tener un bucle de agente monolítico que vive dentro del mismo contenedor donde se ejecuta el código, Anthropic separó el sistema en tres entidades independientes: el cerebro (el modelo y su arnés), las manos (el sandbox de ejecución) y la sesión (el registro de eventos duradero).

Esta arquitectura resuelve tres problemas críticos que afectan a la mayoría de los agentes: la fragilidad del entorno de ejecución, la vulnerabilidad a la inyección de prompts (prompt injection) para el robo de credenciales, y la pérdida de contexto en tareas de horizonte largo ("context anxiety").

## 2. Arquitectura Técnica: El Desacoplamiento

### 2.1. El Cerebro (Brain / Harness)
El "arnés" (harness) es el código que envuelve al modelo Claude. Ya no vive dentro del contenedor de ejecución. Llama al contenedor como si fuera cualquier otra herramienta: `execute(name, input) -> string`. Si el contenedor muere, el arnés lo captura como un error de llamada a herramienta y se lo pasa a Claude, quien puede decidir reintentar aprovisionando un nuevo contenedor.

### 2.2. Las Manos (Hands / Sandbox)
El contenedor de ejecución (sandbox) se trata como "ganado" (cattle), no como "mascota" (pet). Es efímero y desechable. Si falla, se inicializa uno nuevo con una receta estándar: `provision({resources})`. No hay necesidad de intentar recuperar un contenedor fallido.

### 2.3. La Sesión (Session Log)
El registro de sesión vive fuera del arnés y del sandbox. Es un registro duradero de eventos. Si el arnés falla, un nuevo arnés puede reiniciarse con `wake(sessionId)`, usar `getSession(id)` para recuperar el registro de eventos y reanudar desde el último evento. Durante el bucle del agente, el arnés escribe en la sesión con `emitEvent(id, event)`.

## 3. Seguridad y Manejo de Credenciales

En diseños acoplados, el código no confiable generado por el LLM se ejecuta en el mismo contenedor que las credenciales, haciendo que una inyección de prompt pueda robar tokens. Managed Agents resuelve esto asegurando que los tokens **nunca sean accesibles desde el sandbox** donde se ejecuta el código de Claude.

- **Integración Git:** El token de acceso del repositorio se usa para clonar el repo durante la inicialización del sandbox y se conecta al remoto git local. Los comandos `git push` y `pull` funcionan desde dentro del sandbox sin que el agente maneje el token directamente.
- **Herramientas MCP (Model Context Protocol):** Los tokens OAuth se almacenan en una bóveda (vault) segura externa. Claude llama a las herramientas MCP a través de un proxy dedicado. Este proxy toma un token asociado con la sesión, obtiene las credenciales correspondientes de la bóveda y realiza la llamada al servicio externo. El arnés nunca tiene conocimiento de las credenciales.

## 4. Gestión de Contexto Largo (Más allá de la Ventana de Contexto)

Las tareas largas a menudo exceden la ventana de contexto de Claude. Las soluciones estándar (como resumir o recortar contexto) implican decisiones irreversibles sobre qué descartar, lo que puede llevar a fallos si se necesita información antigua más adelante.

En Managed Agents, **la sesión no es la ventana de contexto de Claude**. La sesión actúa como un objeto de contexto duradero que vive *fuera* de la ventana de contexto.

- **Interrogación de Contexto:** La interfaz `getEvents()` permite al cerebro interrogar el contexto seleccionando porciones posicionales del flujo de eventos. El cerebro puede retomar la lectura desde donde la dejó, retroceder unos eventos antes de un momento específico, o releer el contexto antes de una acción crítica.
- **Transformación en el Arnés:** Los eventos recuperados pueden ser transformados por el arnés antes de pasar a la ventana de contexto de Claude (ej. para optimizar el caché de prompts). La sesión garantiza el almacenamiento recuperable, mientras que el arnés maneja la ingeniería de contexto específica para el modelo actual.

## 5. Lecciones para el Monstruo

La arquitectura de Managed Agents ofrece un blueprint claro para robustecer al Monstruo:

1.  **Sandboxes Efímeros:** El Monstruo debe tratar sus entornos de ejecución de código como desechables. Si un script falla catastróficamente o el entorno se corrompe, debe poder aprovisionar uno nuevo limpio y continuar, en lugar de intentar arreglar el entorno roto.
2.  **Bóveda de Credenciales Externa:** Implementar un proxy para llamadas a APIs externas donde el código generado por el LLM solo interactúe con el proxy, y este último inyecte las credenciales reales almacenadas de forma segura, previniendo el robo de tokens.
3.  **Estado Fuera del Contexto:** El `StateWriterTool` implementado recientemente es un paso en la dirección correcta, pero debe evolucionar hacia un registro de eventos interrogable (`getEvents()`) que permita al Monstruo "paginar" a través de su historial a largo plazo sin saturar su ventana de contexto activa.

---
*Referencias:*
[1] Anthropic Engineering Blog: Scaling Managed Agents: Decoupling the brain from the hands (Abril 2026)
