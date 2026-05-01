# BIBLIA: GEMINI 3.1 PRO (GOOGLE DEEPMIND)
**Versión:** Gemini 3.1 Pro Preview (19 Febrero 2026)
**Fecha de Actualización:** 30 de Abril de 2026
**Score de Completitud:** 75%

---

## L01 — Identidad Estratégica

Gemini 3.1 Pro es el modelo más capaz de Google DeepMind al 30 de abril de 2026. Tiene capacidades agénticas nativas, soporte MCP integrado, y Deep Research Max para investigación autónoma de hasta 60 minutos.

| Atributo | Valor |
|---------|-------|
| Empresa | Google DeepMind |
| Versión | 3.1 Pro Preview |
| Fecha lanzamiento | 19 Febrero 2026 |
| Ventana de contexto | 1,048,576 tokens (1M) |
| Tokens de salida máx | 65,536 |

---

## L02 — Agent Mode

| Capacidad | Estado | Detalle |
|-----------|--------|---------|
| Gestión de Gmail | ✅ | Automatización de correos |
| Planificación de viajes | ✅ | Tareas multi-paso |
| Administración de tareas | ✅ | Gestión autónoma |
| Gemini Code Assist Agent | ✅ | Generación y ejecución de código |
| Conexión a servicios externos via MCP | ✅ | Cualquier servidor MCP |
| Gemini Enterprise Agent Platform | ✅ | Plataforma para construir agentes empresariales |

**Limitación conocida:** Usuarios reportan que flujos de trabajo agénticos pueden ser "débiles" — el modelo lucha con herramientas externas y repite su plan en lugar de ejecutar.

---

## L03 — Deep Research Max

| Parámetro | Valor |
|-----------|-------|
| Tiempo máximo de ejecución | 60 minutos |
| Búsquedas web por tarea | Hasta 160 |
| Soporte MCP | ✅ Nativo |
| Visualizaciones nativas | ✅ |
| Acceso a datos empresariales | ✅ |
| Deep Research estándar | < 20 minutos, 5 informes/mes |
| Deep Research Max | Disponible en planes Pro y Ultra |

---

## L04 — Integración MCP

Gemini 3.1 Pro tiene **soporte MCP nativo** — comprende patrones de llamada a herramientas via MCP sin configuración adicional. Google integró MCP en toda su infraestructura API, creando una capa unificada que abarca todos los servicios de Google Cloud.

---

## L05 — Precios

| Tipo | Precio |
|------|--------|
| Tokens de entrada (≤200k) | $2.00 / 1M tokens |
| Tokens de salida | $12.00 / 1M tokens |
| Tokens de entrada (>200k) | $18.00 / 1M tokens |
| Tokens de salida (contexto largo) | $18.00 / 1M tokens |
| Prueba gratuita | $300 en créditos por 90 días |

---

## L06 — Comparación vs. Manus en Tareas de Agente

| Dimensión | Gemini 3.1 Pro | Manus AI |
|-----------|---------------|---------|
| Contexto | 1M tokens | ~200k tokens activos |
| Multi-agente | Limitado | ✅ Hasta 250 agentes paralelos |
| Browser interactivo | ✅ | ✅ |
| Sandbox de código | ✅ (Code Assist) | ✅ (VM Ubuntu) |
| Wide Research | ❌ | ✅ (diferenciador clave) |
| Persistencia entre sesiones | Limitada | ✅ (archivos en sandbox) |
| Agentes paralelos | No documentado | Hasta 250 |

---

**Fuentes:** blog.google, deepmind.google, documentación oficial Gemini API
