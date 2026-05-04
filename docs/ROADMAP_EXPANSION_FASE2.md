# El Monstruo — Roadmap de Expansión: Fase 2 "Paridad Total"

**Objetivo:** Cubrir el 100% de las capacidades de Manus (y superarlas) manteniendo soberanía total.

**Autor:** Manus AI (Hilo B — Asesor Estratégico)
**Fecha:** 3 de mayo de 2026
**Estado:** Propuesta para validación con Cowork

---

## 1. Estado Actual vs Manus

El Monstruo cubre actualmente el **50%** de las capacidades de Manus. La siguiente tabla muestra el gap completo con la solución investigada para cada capacidad faltante.

| Capacidad | Manus | El Monstruo Hoy | Solución Propuesta | MCP | Complejidad | Días |
|---|---|---|---|---|---|---|
| Web Search | Nativo | Perplexity + Cloudflare | Ya cubierto | — | — | 0 |
| Code Execution | Sandbox nativo | E2B Sandbox | Ya cubierto | — | — | 0 |
| GitHub Integration | gh CLI | GitHub REST API | Ya cubierto | — | — | 0 |
| Deploy Estático | WebDev nativo | GitHub Pages | Ya cubierto (Sprint 84) | — | — | 0 |
| Deploy Backend | WebDev nativo | Railway API | Ya cubierto (Sprint 84) | — | — | 0 |
| LLM Multi-modelo | Interno | OpenAI/Anthropic/Google/xAI/Perplexity | Ya cubierto (Sabios) | — | — | 0 |
| Email | Gmail MCP | Gmail SMTP | Ya cubierto | — | — | 0 |
| Notion | Notion MCP | Notion API | Ya cubierto | — | — | 0 |
| Scheduled Tasks | Nativo | schedule_task tool | Ya cubierto | — | — | 0 |
| Brand Engine / Design | No tiene | Design System Engine | Ventaja Monstruo | — | — | 0 |
| Error Memory | No tiene | error_memory.py | Ventaja Monstruo | — | — | 0 |
| Autonomía (Embrión) | No tiene | embrion_loop.py | Ventaja Monstruo | — | — | 0 |
| **Browser Real** | Chromium completo | Solo markdown/text | **Playwright + Browserbase** | Sí | Hard | 5 |
| **Google Workspace** | Drive/Docs/Sheets/Slides | No tiene | **Google APIs + MCP servers** | Sí | Medium | 4 |
| **Generación de Imágenes** | DALL-E/nativo | No tiene | **Replicate API (Flux)** | Sí | Easy | 2 |
| **Procesamiento de Imágenes** | Pillow/nativo | No tiene | **Pillow + Cloudinary** | Sí | Easy | 2 |
| **Generación de Video** | Nativo | No tiene | **Replicate (Kling/Runway)** | Sí | Medium | 3 |
| **Audio/TTS/STT** | ElevenLabs/nativo | API key existe, no integrado | **ElevenLabs MCP** | Sí | Easy | 2 |
| **Slides/Presentaciones** | Nativo | No tiene | **python-pptx + MCP** | Sí | Easy | 3 |
| **Pagos (Stripe/PayPal)** | PayPal MCP | No tiene | **Stripe MCP** | Sí | Easy | 3 |
| **Paralelismo** | map() nativo | Single-thread | **Temporal** | Sí | Hard | 5 |
| **Data Analysis/Viz** | pandas/plotly | No tiene | **pandas MCP server** | Sí | Easy | 3 |
| **Calendar/Tasks** | Google Calendar MCP | Solo schedule_task | **Google Calendar MCP + Todoist** | Sí | Easy | 3 |
| **File Storage/Sharing** | S3/nativo | Dropbox key existe, no integrado | **Dropbox MCP** | Sí | Easy | 3 |

**Total de días estimados para paridad completa: 38 días de desarrollo** (distribuidos en sprints de 2-3 días).

---

## 2. Arquitectura de Integración

Todas las nuevas capacidades se integran a través del **MCP Hub** existente del kernel (Sprint 55.1). La arquitectura es:

```
Embrión → Task Planner → Tool Broker → MCP Hub → [MCP Servers]
                                          ↓
                                    Tool Registry (Supabase)
                                          ↓
                              ┌─────────────────────────┐
                              │   MCP Servers Nuevos     │
                              ├─────────────────────────┤
                              │ Playwright MCP           │
                              │ Google Drive MCP         │
                              │ Google Calendar MCP      │
                              │ ElevenLabs MCP           │
                              │ Replicate MCP            │
                              │ Stripe MCP               │
                              │ Dropbox MCP              │
                              │ pandas MCP               │
                              │ PowerPoint MCP           │
                              │ Todoist MCP              │
                              └─────────────────────────┘
```

El principio es **MCP-first**: cada capacidad nueva se agrega como un MCP server que el kernel descubre y usa dinámicamente via el MCP Hub. Esto significa:

1. **Sin cambios al kernel core** — solo se registran nuevos servers
2. **Hot-plug** — se pueden agregar/remover sin restart
3. **Tool Masking** — si un server cae, la herramienta se enmascara sin romper el contexto
4. **Métricas automáticas** — el MCP Hub ya trackea uso por server

Para las capacidades que requieren integración más profunda (Browser Real y Paralelismo), se necesitan cambios arquitectónicos en el kernel.

---

## 3. Plan de Sprints

Los sprints están ordenados por **impacto/esfuerzo** — las capacidades de mayor impacto y menor esfuerzo van primero.

### Sprint 85: Audio Soberano (2 días)
**Impacto: Alto | Esfuerzo: Bajo**

El Monstruo ya tiene la API key de ElevenLabs. Solo falta conectar el MCP server.

| Tarea | Detalle |
|---|---|
| Instalar ElevenLabs MCP | `pip install elevenlabs-mcp` en el kernel |
| Registrar en MCP Hub | Agregar server config en mcp_hub_config |
| Registrar tools en Supabase | text_to_speech, speech_to_text, voice_clone |
| Test E2E | Embrión genera audio narrado de un reporte |

**Resultado:** El Monstruo puede narrar reportes, generar podcasts, transcribir audio.

**Costo mensual estimado:** $6/mes (Starter plan ElevenLabs)

---

### Sprint 86: Generación de Imágenes (2 días)
**Impacto: Alto | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Instalar Replicate MCP | Server MCP para Replicate (Flux, SDXL) |
| Registrar en MCP Hub | generate_image, edit_image tools |
| Integrar con Brand Engine | Logos y assets usan design tokens |
| Test E2E | Embrión genera logo + banner para una marca nueva |

**Resultado:** El Monstruo genera imágenes de calidad profesional para las herramientas que crea.

**Costo estimado:** ~$0.003 por imagen (Flux Schnell), ~$0.05 por imagen (Flux Pro)

---

### Sprint 87: Dropbox + File Storage (3 días)
**Impacto: Medio | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Instalar Dropbox MCP | ngs/dropbox-mcp-server |
| Registrar en MCP Hub | upload_file, download_file, list_files, share_file |
| Crear carpeta estructura | /El-Monstruo/proyectos/, /El-Monstruo/assets/ |
| Test E2E | Embrión guarda reporte en Dropbox y comparte link |

**Resultado:** El Monstruo tiene almacenamiento persistente y puede compartir archivos.

**Costo:** Gratis (2GB free tier, ya tienes cuenta)

---

### Sprint 88: Slides y Presentaciones (3 días)
**Impacto: Medio | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Instalar PowerPoint MCP | Office-PowerPoint-MCP-Server |
| Registrar en MCP Hub | create_presentation, add_slide, add_chart |
| Template system | Templates base alineados con Brand Engine |
| Test E2E | Embrión crea pitch deck de 10 slides para un producto |

**Resultado:** El Monstruo genera presentaciones profesionales autónomamente.

**Costo:** Gratis (open source)

---

### Sprint 89: Data Analysis y Visualización (3 días)
**Impacto: Medio | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Instalar pandas MCP | marlonluo2018/pandas-mcp-server |
| Registrar en MCP Hub | analyze_data, create_chart, describe_dataset |
| Integrar con E2B | Ejecutar análisis en sandbox aislado |
| Test E2E | Embrión analiza CSV de ventas y genera reporte con gráficas |

**Resultado:** El Monstruo analiza datos y genera visualizaciones como Manus.

**Costo:** Gratis (open source)

---

### Sprint 90: Google Workspace (4 días)
**Impacto: Alto | Esfuerzo: Medio**

| Tarea | Detalle |
|---|---|
| Configurar Google OAuth | Service Account para APIs de Google |
| Instalar Google Drive MCP | google-drive-mcp-server |
| Instalar Google Calendar MCP | google-calendar-mcp |
| Registrar en MCP Hub | 8+ tools (create_doc, read_sheet, create_event, etc.) |
| Test E2E | Embrión crea un Google Doc con reporte y agenda reunión en Calendar |

**Resultado:** El Monstruo interactúa con todo Google Workspace.

**Costo:** Gratis (Google APIs free tier es generoso)

**Requisito:** Alfredo debe crear un Google Cloud Project y Service Account (una vez, 10 minutos).

---

### Sprint 91: Procesamiento de Imágenes (2 días)
**Impacto: Medio | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Integrar Pillow en kernel | Ya disponible en Python, solo crear tool wrapper |
| Crear image_processing tool | crop, resize, rotate, watermark, format_convert, composite |
| Registrar en Tool Registry | 6 sub-acciones |
| Test E2E | Embrión procesa screenshots de una web y genera thumbnails |

**Resultado:** El Monstruo manipula imágenes programáticamente.

**Costo:** Gratis (Pillow es open source)

---

### Sprint 92: Calendar + Task Management (3 días)
**Impacto: Medio | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Instalar Todoist MCP | todoist-mcp-server |
| Integrar con schedule_task | Sincronizar tareas programadas con Todoist |
| Dashboard de tareas | Vista en Command Center de tareas pendientes |
| Test E2E | Embrión crea proyecto en Todoist con milestones |

**Resultado:** El Monstruo gestiona proyectos y calendarios.

**Costo:** Gratis (Todoist free tier)

---

### Sprint 93: Pagos con Stripe (3 días)
**Impacto: Alto | Esfuerzo: Bajo**

| Tarea | Detalle |
|---|---|
| Instalar Stripe MCP | Stripe official MCP server |
| Registrar en MCP Hub | create_invoice, create_checkout, list_payments |
| Integrar con deploy_app | Apps deployadas pueden tener pagos integrados |
| Test E2E | Embrión crea landing page con checkout de Stripe funcional |

**Resultado:** El Monstruo puede monetizar las herramientas que crea.

**Costo:** Gratis hasta que proceses pagos (2.9% + 30¢ por transacción)

**Requisito:** Alfredo debe crear cuenta Stripe y obtener API keys.

---

### Sprint 94: Generación de Video (3 días)
**Impacto: Medio | Esfuerzo: Medio**

| Tarea | Detalle |
|---|---|
| Instalar Replicate MCP (video) | Modelos Kling v2.0, Runway Gen-3 |
| Registrar en MCP Hub | generate_video, image_to_video |
| Integrar con Brand Engine | Videos usan paleta de colores de marca |
| Test E2E | Embrión genera video promocional de 10 segundos para un producto |

**Resultado:** El Monstruo genera videos cortos para marketing.

**Costo:** ~$0.10-0.50 por video (depende del modelo y duración)

---

### Sprint 95: Browser Real (5 días)
**Impacto: Crítico | Esfuerzo: Alto**

Este es el sprint más complejo pero más transformador. Sin browser real, El Monstruo es ciego a la web visual.

| Tarea | Detalle |
|---|---|
| Integrar Playwright | Headless Chromium en el kernel |
| Browserbase como fallback | Cloud browser para sites que bloquean headless |
| Crear browser_agent tool | navigate, click, fill_form, screenshot, extract_data |
| Integrar con Embrión | El Embrión puede "ver" páginas web y actuar |
| Anti-detection | Stealth mode para evitar bloqueos |
| Test E2E | Embrión navega a un competidor, extrae precios, y genera reporte |

**Resultado:** El Monstruo puede interactuar con cualquier sitio web como un humano.

**Costo:** Browserbase: $0.01/min de sesión. Self-hosted Playwright: gratis pero consume RAM.

**Decisión arquitectónica:** Playwright local para sites simples, Browserbase para sites con anti-bot. El MCP Hub rutea automáticamente.

---

### Sprint 96: Paralelismo (5 días)
**Impacto: Crítico | Esfuerzo: Alto**

El Monstruo actualmente es single-thread. Para competir con Manus necesita ejecutar múltiples tareas simultáneamente.

| Tarea | Detalle |
|---|---|
| Evaluar Temporal vs asyncio nativo | Temporal para durabilidad, asyncio para simplicidad |
| Implementar task_pool | Pool de workers que ejecutan sub-tareas en paralelo |
| Integrar con Embrión | El Embrión puede lanzar N investigaciones simultáneas |
| Queue system | Cola de tareas con prioridades y retry |
| Test E2E | Embrión investiga 10 competidores en paralelo y consolida |

**Resultado:** El Monstruo puede hacer wide research como Manus.

**Costo:** Self-hosted Temporal: gratis. Cloud: $100/mes.

**Recomendación:** Empezar con asyncio nativo (Python ya lo soporta) y migrar a Temporal solo si se necesita durabilidad cross-restart.

---

## 4. Timeline Visual

```
Mayo 2026:
  Sprint 85 (Audio)          ██ 2d
  Sprint 86 (Imágenes)       ██ 2d
  Sprint 87 (Dropbox)        ███ 3d
  Sprint 88 (Slides)         ███ 3d

Junio 2026:
  Sprint 89 (Data/Viz)       ███ 3d
  Sprint 90 (Google WS)      ████ 4d
  Sprint 91 (Image Proc)     ██ 2d
  Sprint 92 (Calendar)       ███ 3d

Julio 2026:
  Sprint 93 (Stripe)         ███ 3d
  Sprint 94 (Video)          ███ 3d
  Sprint 95 (Browser)        █████ 5d
  Sprint 96 (Paralelismo)    █████ 5d
```

**Paridad total con Manus: ~12 semanas (fin de julio 2026)**

---

## 5. Presupuesto Mensual Post-Expansión

| Servicio | Costo Mensual |
|---|---|
| Railway (kernel + DB) | ~$5-20 |
| ElevenLabs (audio) | $6 |
| Replicate (imágenes + video) | ~$5-15 |
| Browserbase (browser cloud) | ~$10-30 |
| Google APIs | Gratis |
| Stripe | Solo comisión por transacción |
| Dropbox | Gratis (2GB) |
| Temporal (si cloud) | $0 (self-hosted) |
| Todo lo demás (open source) | $0 |
| **Total estimado** | **$26-71/mes** |

Comparado con Manus Pro ($39/mes con límites) o Devin ($500/mes), El Monstruo soberano con paridad total costaría entre $26-71/mes sin límites de uso.

---

## 6. Después de la Paridad: Ventajas Únicas

Una vez alcanzada la paridad con Manus, El Monstruo tendrá capacidades que **ningún otro agente tiene**:

1. **Soberanía total** — Todo el código, datos, y decisiones son de Alfredo
2. **Brand Engine** — Ningún agente comercial tiene un sistema de marca integrado
3. **Error Memory** — Aprendizaje persistente de errores (Manus no tiene)
4. **Embrión autónomo** — Loop de pensamiento propio (Manus solo ejecuta cuando le pides)
5. **Sabios multi-modelo** — Consulta a 6+ LLMs simultáneamente para decisiones
6. **FCS Scoring** — Evaluación objetiva de calidad de output
7. **Colmena** — Red de agentes especializados
8. **Magna Classifier** — Routing inteligente de deploy
9. **Cost Optimizer** — Optimización autónoma de costos de API
10. **Agents Radar** — Monitoreo de competencia en tiempo real

**Estas 10 capacidades son exclusivas de El Monstruo.** Ningún agente comercial las tiene porque son personalizaciones profundas que solo un sistema soberano puede tener.

---

## 7. Criterio de Priorización

Los sprints están ordenados por la fórmula:

> **Prioridad = (Impacto en capacidad × Frecuencia de uso) / (Esfuerzo × Costo)**

Los primeros 4 sprints (Audio, Imágenes, Dropbox, Slides) son todos de **alto impacto, bajo esfuerzo, y costo mínimo**. Representan el 80% del valor con el 20% del esfuerzo.

Los últimos 2 sprints (Browser Real y Paralelismo) son los más complejos pero los más transformadores. Sin ellos, El Monstruo tiene paridad en features pero no en profundidad de ejecución.

---

## 8. Decisión Requerida

Alfredo debe decidir:

1. **¿Validar este roadmap con Cowork?** — Cowork puede optimizar el orden y la arquitectura
2. **¿Empezar Sprint 85 (Audio) inmediatamente?** — Es el de menor riesgo y ya tiene la API key
3. **¿Crear Google Cloud Project?** — Necesario para Sprint 90 (Google Workspace)
4. **¿Crear cuenta Stripe?** — Necesario para Sprint 93 (Pagos)

---

*Documento generado por Manus AI (Hilo B) — 3 de mayo de 2026*
*Basado en investigación paralela de 12 capacidades con datos verificados*
