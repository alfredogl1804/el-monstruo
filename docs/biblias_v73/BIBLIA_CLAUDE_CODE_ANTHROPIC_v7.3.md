## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Claude Code (Anthropic)</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>v2.1.119 (24 abril 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>Claude Code no tiene un precio independiente, sino que se incluye en los planes de suscripción de Claude. Los planes disponibles son:
- **Gratis**: $0/mes, con capacidades básicas.
- **Pro**: $17/mes (con suscripción anual, $200 facturados por adelantado) o $20/mes (facturación mensual). Incluye Claude Code, Claude Cowork, más uso, acceso a proyectos ilimitados, Research, Claude para Excel, PowerPoint y Word.
- **Max**: Desde $100/mes. Incluye todo lo del plan Pro, más 5x o 20x más uso que Pro, límites de salida más altos para todas las tareas, acceso anticipado a funciones avanzadas y acceso prioritario en momentos de alto tráfico.
También es posible pagar por uso a través de la API de Anthropic, con precios de $5 por millón de tokens de entrada y $25 por millón de tokens de salida para Opus 4.6.</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>Claude Code se posiciona como una herramienta de codificación agéntica robusta, destacando por su capacidad para entender bases de código completas y ejecutar tareas complejas mediante lenguaje natural. Su integración con los modelos Claude Opus 4.7 le otorga una ventaja en capacidades de razonamiento y rendimiento en benchmarks como SWE-bench. Sin embargo, enfrenta competencia de herramientas con mejor UX como Cursor y otras CLI de IA como Roocode y OpenCode. Los recientes problemas de calidad en abril de 2026 afectaron su reputación, pero la rápida respuesta de Anthropic y las mejoras continuas buscan mantener su liderazgo en el segmento de asistentes de codificación avanzados.</td>
</tr>
</table>
<br>
## L02 — NOVEDADES Y CAMBIOS RECIENTES (ABRIL 2026)
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Cambios Clave desde Marzo 2026</td>
<td>Desde el 20 de marzo de 2026, Claude Code ha experimentado varias actualizaciones y cambios significativos:

**Cambios de Rendimiento y Calidad (Marzo-Abril 2026):**
*   **4 de marzo:** Se cambió el esfuerzo de razonamiento predeterminado de `high` a `medium` para reducir la latencia, lo que resultó en una disminución de la calidad. Se revirtió el 7 de abril, estableciendo `xhigh` como predeterminado para Opus 4.7 y `high` para otros modelos.
*   **26 de marzo:** Se implementó un cambio para borrar el pensamiento antiguo de las sesiones inactivas, pero un error causó que se borrara en cada turno, provocando olvido y repetición. Se corrigió el 10 de abril (v2.1.101).
*   **16 de abril:** Se añadió una instrucción de prompt del sistema para reducir la verbosidad de Claude Opus 4.7, lo que afectó negativamente la calidad de la codificación. Se revirtió el 20 de abril.

**Nuevas Características y Mejoras (Semanas 13-17 de 2026):**
*   **Semana 17 (20-24 de abril):** Lanzamiento de `/ultrareview` en vista previa de investigación pública (agentes de búsqueda de errores en la nube), resumen de sesión, temas personalizados y rediseño de Claude Code en la web.
*   **Semana 16 (13-17 de abril):** Claude Opus 4.7 se convierte en el modelo predeterminado en Max y Team Premium con un nuevo nivel de esfuerzo `xhigh`. Introducción de Routines en Claude Code en la web, `/ultrareview` para revisión de código multi-agente paralela, herramienta `/usage` y binarios nativos para la CLI.
*   **Semana 15 (6-10 de abril):** Vista previa temprana de Ultraplan (borrador de planes en la nube), herramienta Monitor para eventos en segundo plano, `/loop` auto-ajustable, `/team-onboarding` y `/autofix-pr`.
*   **Semana 14 (30 de marzo - 3 de abril):** Uso de la computadora en la CLI (vista previa de investigación), lecciones interactivas `/powerup`, renderizado de pantalla alternativa sin parpadeos, anulación del tamaño de resultado de MCP por herramienta y ejecutables de plugins en el `PATH` de Bash.
*   **Semana 13 (23-27 de marzo):** Modo automático (vista previa de investigación), uso de la computadora en la aplicación de escritorio, auto-corrección de PR en la web, búsqueda de transcripciones, herramienta nativa de PowerShell para Windows y ganchos `if` condicionales.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más importante de los últimos 40 días es la admisión por parte de Anthropic de una disminución en la calidad de Claude Code durante marzo y abril de 2026. Esto se debió a cambios en el esfuerzo de razonamiento predeterminado, un error en el almacenamiento en caché de sesiones y una instrucción de prompt para reducir la verbosidad, que afectaron negativamente la inteligencia y el rendimiento del asistente de codificación. Anthropic ha revertido los cambios problemáticos y ha restablecido los límites de uso para los suscriptores.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>Anthropic admitió que, debido a una serie de "errores de ingeniería" y cambios en el prompt del sistema, la calidad de Claude Code disminuyó notablemente durante marzo y abril de 2026, lo que generó quejas de los usuarios. La compañía tuvo que revertir algunos cambios y restablecer los límites de uso para todos los suscriptores como compensación.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>120k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://github.com/anthropics/claude-code, https://www.anthropic.com/news/claude-opus-4-7, https://releasebot.io/updates/anthropic, https://www.youtube.com/watch?v=VpdUP_e9aP0, https://www.startuphub.ai/ai-news/reviews/2026/claude-ai-complete-guide-2026, https://platform.claude.com/docs/en/release-notes/overview, https://www.ai.cc/blogs/claude-opus-4-7-released-anthropic-best-coding-ai-2026/, https://www.anthropic.com/engineering/april-23-postmortem, https://code.claude.com/docs/en/whats-new/2026-w17, https://code.claude.com/docs/en/whats-new/2026-w15, https://claude.com/pricing, https://www.ssdnodes.com/blog/claude-code-pricing-in-2026-every-plan-explained-pro-max-api-teams/, https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration, https://martinalderson.com/posts/no-it-doesnt-cost-anthropic-5k-per-claude-code-user/, https://www.claudelog.com/claude-code-pricing/, https://support.claude.com/en/articles/11049762-choosing-a-claude-plan, https://www.verdent.ai/guides/claude-code-pricing-2026, https://dev.to/soulentheo/every-ai-coding-cli-in-2026-the-complete-map-30-tools-compared-4gob, https://code.claude.com/docs/en/whats-new
