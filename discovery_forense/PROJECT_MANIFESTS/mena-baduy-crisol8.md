# Mena Baduy Crisol-8 — Manifest para Cowork

Slug: mena-baduy-crisol8
Categoría: Activo
Última actualización: 2026-05-06
Generado por: Manus map paralelo

## 1. Definición canónica
Mena Baduy Crisol-8 es una operación electoral OSINT activa dirigida contra Renán Barrera Concha y sus aliados políticos en el estado de Yucatán. El proyecto se centra en la investigación digital profunda, la conformación de dossiers legales y la amplificación mediática de los hallazgos.

El objetivo principal es recopilar, analizar y estructurar evidencia digital y documental para impactar en la coyuntura electoral 2026-2027 en Mérida y Yucatán, proveyendo inteligencia accionable para estrategias políticas y mediáticas.

## 2. Estado actual
| Métrica | Valor |
| --- | --- |
| Fase | Producción (Sprint discovery Fase III) |
| Mercado | Mérida, Yucatán, México (Coyuntura electoral 2026-2027) |
| Stack técnico | OSINT tools, S3, GitHub, Notion, Drive |
| Modelo de negocio | Operación política / Inteligencia |
| Última actividad | 2026-05-06 (migración 50 archivos a docs discovery-forense-2026-05-05) |

## 3. Ubicaciones canónicas (dónde vive el conocimiento)
| Fuente | Ubicación | Cómo accederla desde Cowork |
| --- | --- | --- |
| Skill | `el-monstruo` | Leer skill canónico para referencia general |
| Repo GitHub | `crisol-8` (PRIVATE) | Acceso vía GitHub CLI (`gh repo view`) |
| Drive | 82 archivos, 15 planes (top: `plan_de_investigacion_ampliado`) | Búsqueda vía `gws` CLI |
| Notion | Páginas dispersas (planes, dossiers, validaciones) | Búsqueda vía Notion MCP |
| Dropbox | — | — |
| S3 | `crisol8-analysis`, `crisol8-evidence`, `crisol8-raw-scrapes`, `operacion-doble-eje` | Acceso vía AWS CLI / S3 tools |

## 4. Decisiones / pendientes clave
1. **Consolidación de Notion**: Organizar páginas dispersas en un hub centralizado. (Estado: Pendiente, Bloqueante: N, Impacto: Medio)
2. **Operativa continua**: Mantener el flujo de recolección OSINT y actualización de dossiers. (Estado: En progreso, Bloqueante: N, Impacto: Alto)
3. **Estrategia de amplificación**: Definir canales y tiempos para la amplificación mediática de la Fase III. (Estado: Pendiente, Bloqueante: N, Impacto: Alto)

## 5. Próximos pasos sugeridos para Cowork
1. Consolidar y estructurar la información dispersa en Notion creando un índice maestro del proyecto.
2. Revisar los 50 archivos migrados recientemente (`discovery-forense-2026-05-05`) para extraer insights clave.
3. Sincronizar los hallazgos de los buckets S3 (`crisol8-evidence`) con los dossiers legales en Drive.
4. Monitorear la actividad de los objetivos en tiempo real para alimentar la operación continua.

## 6. Riesgos / notas críticas
- **Seguridad Operacional (OPSEC)**: Riesgo alto de exposición al manejar datos sensibles y evidencia legal.
- **Dispersión de información**: Múltiples fuentes (S3, Drive, Notion) requieren sincronización constante para evitar pérdida de contexto.
- **Tiempos electorales**: La ventana de oportunidad es estricta (2026-2027), requiriendo agilidad en la amplificación mediática.

## 7. Cross-links a otros proyectos del portfolio
- **El Monstruo**: Relación de dependencia (Skill canónico y marco operativo general).
- **Operación Doble Eje**: Relación de datos (Comparte bucket S3 `operacion-doble-eje`).