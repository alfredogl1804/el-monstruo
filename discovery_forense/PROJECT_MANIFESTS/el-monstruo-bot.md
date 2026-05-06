# El Monstruo Bot Telegram — Manifest para Cowork

Slug: el-monstruo-bot
Categoría: Activo
Última actualización: 2026-05-06
Generado por: Manus map paralelo

## 1. Definición canónica
El Monstruo Bot Telegram es la interfaz móvil del ecosistema El Monstruo. Actúa como el punto de contacto principal para que Alfredo interactúe con su asistente IA soberano desde cualquier lugar.

El proyecto resuelve la necesidad de tener acceso inmediato y portátil a las capacidades del ecosistema, permitiendo recibir alertas en tiempo real, consultar el estado de diversos proyectos y ejecutar comandos remotos sin necesidad de acceder a una computadora. Está diseñado exclusivamente para el uso personal y operativo de Alfredo.

## 2. Estado actual
| Métrica | Detalle |
|---|---|
| Fase | Producción MVP |
| Mercado | Uso interno / Personal |
| Stack técnico | Python, python-telegram-bot, Railway, Supabase, APIs del ecosistema |
| Modelo de negocio | — (Herramienta interna) |
| Última actividad | 2026-04-26 |

## 3. Ubicaciones canónicas (dónde vive el conocimiento)
| Fuente | Ubicación | Cómo accederla desde Cowork |
|---|---|---|
| Skill | `el-monstruo-bot` | Leer archivo `/home/ubuntu/skills/el-monstruo-bot/SKILL.md` |
| Repo GitHub | `el-monstruo-bot` (PRIVATE) | Clonar vía `gh repo clone el-monstruo-bot` |
| Drive | Por confirmar | Por confirmar via búsqueda Cowork |
| Notion | Por confirmar | Por confirmar via búsqueda Cowork |
| Dropbox | Por confirmar | Por confirmar via búsqueda Cowork |
| S3 | Por confirmar | Por confirmar via búsqueda Cowork |
| Deploy | Railway | Acceder al dashboard de Railway del proyecto |

## 4. Decisiones / pendientes clave
1. **Roadmap de evolución post-MVP**: Definir qué nuevas funcionalidades (features) añadir al bot en las próximas iteraciones. (Estado: Pendiente, Bloqueante: No, Impacto: Alto)
2. **Integración de nuevos comandos**: Evaluar la adición de comandos específicos para interactuar con nuevos módulos del ecosistema. (Estado: Pendiente, Bloqueante: No, Impacto: Medio)

## 5. Próximos pasos sugeridos para Cowork
1. Leer el skill canónico `el-monstruo-bot` para absorber el contexto de desarrollo, despliegue y el roadmap actual.
2. Revisar el repositorio en GitHub para analizar la arquitectura del código y las integraciones existentes con Supabase y otras APIs.
3. Proponer un borrador inicial del roadmap de evolución post-MVP basado en las capacidades actuales del ecosistema El Monstruo.
4. Verificar el estado del despliegue en Railway y los logs recientes para asegurar la estabilidad del MVP.

## 6. Riesgos / notas críticas
- Dependencia crítica de la disponibilidad de Railway y las APIs del ecosistema para el funcionamiento del bot.
- Seguridad: Al ser una interfaz móvil con acceso a comandos remotos y estado de proyectos, es vital asegurar que solo Alfredo tenga acceso (autenticación/autorización estricta en Telegram).

## 7. Cross-links a otros proyectos del portfolio
- **El Monstruo**: Proyecto padre / Ecosistema principal (Relación: Interfaz móvil del core).
- **Supabase**: Base de datos y backend (Relación: Integración de datos).