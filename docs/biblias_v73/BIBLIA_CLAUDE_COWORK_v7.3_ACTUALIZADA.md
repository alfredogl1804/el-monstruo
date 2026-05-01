# BIBLIA: CLAUDE COWORK (ANTHROPIC)
**Versión:** Claude Opus 4.7 (16 Abril 2026)
**Fecha de Actualización:** 30 de Abril de 2026
**Score de Completitud:** 75%

---

## L01 — Identidad Estratégica

Claude Cowork es el producto de agente autónomo de Anthropic, diseñado para ejecutar tareas largas y complejas de forma autónoma en el entorno de escritorio del usuario. Opera como un "compañero de trabajo" que puede delegar tareas, programarlas y ejecutarlas sin supervisión continua.

| Atributo | Valor |
|---------|-------|
| Empresa | Anthropic |
| Modelo base | Claude Opus 4.7 (lanzado 16 abril 2026) |
| Tipo | Agente autónomo de escritorio + web |
| Diferenciador | Corre en VM Linux aislada en el OS del host |
| Estado actual | Beta (tareas programadas) |

---

## L02 — Capacidades de Agente Autónomo

| Capacidad | Estado | Detalle |
|-----------|--------|---------|
| Ejecución autónoma de tareas | ✅ | Describe resultado + frecuencia, Claude ejecuta |
| Tareas programadas | ✅ Beta | Revisar email, generar reportes semanales |
| Browser (Chrome) | ✅ | Investigación web via conector Chrome |
| Slack | ✅ | Extrae info, envía mensajes |
| Control de pantalla | ✅ | Abre apps sin integración directa |
| GitHub | ✅ | Lee issues, PRs, commits |
| Excel/PowerPoint/Word | ✅ | Productos dedicados de Anthropic |
| Aprobación antes de ejecutar | ✅ | Muestra plan de acción para aprobación |

---

## L03 — Límites de Contexto

| Plan | Contexto | Tokens de salida |
|------|---------|-----------------|
| Pro ($20/mes) | 200,000 tokens | 8,192 default |
| Max 5x ($100/mes) | 1,000,000 tokens (Opus 4.6+) | 65,536 |
| Max 20x ($200/mes) | 1,000,000 tokens | 65,536 |

**Nota:** Claude Opus 4.6 fue el primer modelo con 1M tokens de contexto (disponible desde 13 marzo 2026). Claude Opus 4.7 probablemente hereda esta capacidad.

---

## L04 — Precios y Planes

| Plan | Precio | Para qué |
|------|--------|---------|
| Pro | $20/mes o $17/mes anual | Tareas rápidas |
| Max 5x | $100/mes | Uso diario intensivo |
| Max 20x | $200/mes | Delegación masiva durante el día |

**Importante:** Cowork consume límites de uso más rápido que el chat estándar.

---

## L05 — Diferencias vs. Claude Opus 4.7 Estándar

| Dimensión | Claude Opus 4.7 Estándar | Claude Cowork |
|-----------|--------------------------|---------------|
| Modo de operación | Conversacional | Agente autónomo |
| Ejecución | Responde en el chat | Ejecuta en VM Linux aislada |
| Duración de tarea | Una respuesta | Horas/días |
| Herramientas | Limitadas al chat | Browser, Slack, pantalla, archivos |
| Supervisión | Siempre presente | Puede trabajar sin supervisión |
| Programación | No | Sí (Beta) |

---

## L06 — Integraciones Empresariales

| Herramienta | Tipo de Integración | Capacidad |
|-------------|--------------------|-----------| 
| Chrome | Conector | Investigación web, extracción de datos |
| Slack | Conector | Leer/escribir mensajes, extraer métricas |
| Notion | Conector | Leer/escribir documentos |
| GitHub | Conector | Issues, PRs, commits |
| Linear | Conector | Gestión de problemas |
| CRM | Conector | Notas de clientes |
| Excel | Producto dedicado | Análisis, generación de libros |
| PowerPoint | Producto dedicado | Presentaciones automáticas |
| Word | Producto dedicado | Documentos |

---

## L07 — Arquitectura Técnica

Claude Cowork corre en una **máquina virtual Linux aislada** dentro del sistema operativo del host. Esto le permite:
- Acceder a archivos locales del usuario (con permiso)
- Ejecutar código en un entorno seguro
- Interactuar con aplicaciones del escritorio
- Mantener estado persistente entre sesiones

---

## L08 — Gaps de Conocimiento (Para Semana 2)

1. ¿Cuántas tareas paralelas puede ejecutar simultáneamente?
2. ¿Cómo maneja el contexto cuando supera 1M tokens?
3. ¿Qué pasa si una tarea falla a la mitad?
4. ¿Tiene acceso a internet sin el conector Chrome?
5. ¿Puede crear y ejecutar código arbitrario?

---

**Fuentes:** anthropic.com/news, claude.com/product/cowork, blog.pluto.security, support.claude.com
