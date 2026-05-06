# Prompt para Cowork — Briefing Fase III Discovery Forense

**Fecha:** 2026-05-05
**Emisor:** Manus (Hilo B sandbox Linux remoto)
**Receptor:** Cowork (Hilo A sandbox Linux remoto, app Claude desktop)
**Repo coordinación:** `alfredogl1804/el-monstruo` (rama `main`)

---

## Cómo usarlo

1. Abre la app Claude desktop → tab **Cowork**
2. Abre tu chat existente "Review and explain Claude project" o crea uno nuevo
3. Pega el prompt completo de abajo (entre las líneas)
4. Cowork ejecutará con todo el contexto

---

## PROMPT (copiar todo lo que sigue hasta "FIN PROMPT")

```
Cowork, soy Alfredo. Manus completó las tareas que le tocaban en Fase III del Discovery Forense y dejó listo el ecosistema para que tú arranques las tuyas. Aquí va el briefing completo. Confirma cuando termines de leer y procede.

═══════════════════════════════════════════════════
ARQUITECTURA OPERATIVA (verificada 2026-05-05)
═══════════════════════════════════════════════════

Hilo A (tú, Cowork): sandbox Linux remoto en app Claude desktop, sin acceso al Mac de Alfredo, con conectores OAuth nativos.

Hilo B (Manus): sandbox Linux remoto en plataforma Manus, con MCPs vía manus-mcp-cli y mounts FUSE al Mac de Alfredo en /mnt/desktop/.

Tú y Manus son canales paralelos. NO comparten filesystem. Coordinan por: (a) commits a github.com/alfredogl1804/el-monstruo, (b) archivo bridge/manus_to_cowork.md.

Conectores que tienes activos en Cowork desktop: Notion (Omnicom Inc workspace), Supabase, Google Drive, GitHub.

Conectores que NO tienes y que están delegados a Manus: AWS S3, Dropbox.

═══════════════════════════════════════════════════
LO QUE MANUS YA HIZO (verificable en repo)
═══════════════════════════════════════════════════

Commit 6b2b644: Smoke test funcional de 4 MCPs en Claude Code terminal del Mac (Notion, Supabase, S3, Dropbox), todos PASS. Migración a user-scope. Bridge file inicial.

Commit aecda60: Tarea 2a completada. Descargados desde S3 al directorio discovery_forense/crisol_plans/ del repo:
- operacion-doble-eje/ (1.3MB, 31 archivos .md y .json) → Plan Maestro Mena Baduy, Plan Definitivo CRISOL8, Mapa de Conexiones, Reporte Gebhardt
- crisol8-analysis/ (300KB, 22 archivos) → Hallazgos Wide Research, Cadena de Amplificación, análisis SQL/JSON
También: discovery_forense/NOTION_PAGINAS_RAIZ_PARA_CONECTAR.md con las 8 páginas raíz del corpus.

Commit 38664dc: Tarea 4 completada. Diff semántico SOP/EPIA Drive vs Dropbox en discovery_forense/sop_epia_diff/. Hallazgos críticos:
- SOP Fundacional v1.2: el .md de Drive es MÁS COMPLETO que el .docx de Dropbox (196 tokens únicos en Drive vs 2 en Dropbox). Versión canónica recomendada: SOP_v1.2_DRIVE.md.
- EPIA Fundacional v1.0: el .docx de Dropbox es MÁS COMPLETO que el .txt de Drive (286 tokens únicos en Dropbox vs 8 en Drive). Versión canónica recomendada: EPIA_FUNDACIONAL_DBX.md o .docx.
- Otros pares (Genealogía SOP/EPIA v2, Reestructuración 6 Sabios) están sincronizados.
Reporte completo en discovery_forense/sop_epia_diff/REPORTE_FINAL_DIFF_SOP_EPIA.md.

Commit 9eeb7a9: Notion desbloqueado. Alfredo conectó la integración "Mounstruo Cowoork" al workspace Omnicom Inc vía Notion AI desde el panel "Pedir a la IA". Las 8 páginas raíz del corpus son accesibles.

═══════════════════════════════════════════════════
TUS TAREAS PENDIENTES (Fase III, lado Hilo A)
═══════════════════════════════════════════════════

TAREA 1 — Biblias ZIP a Notion
Lee el ZIP de biblias del Monstruo (ubicación a confirmar en el bridge file o en Drive con el conector que tienes), descomprime, y crea las páginas correspondientes en Notion bajo la página raíz "🏗️ Plan de Construcción: El Monstruo v0.1" (ID: 30114c6f8bba813ba7aec5d7d3b8da3d). Usa la jerarquía del ZIP como jerarquía Notion. Si tienes dudas sobre dónde anclar, anclar en una sub-página nueva titulada "Biblias canónicas — Discovery Forense Fase III".

TAREA 2b — Push planes CRISOL al repo crisol-8
Los planes están listos en discovery_forense/crisol_plans/ del repo el-monstruo. Crea un repo nuevo privado alfredogl1804/crisol-8 (gh repo create alfredogl1804/crisol-8 --private), copia el contenido, agrega un README con índice, commitea y pushea. Después actualiza bridge/manus_to_cowork.md con el link al nuevo repo.

TAREA 3 — Indexar dataset forense en Supabase pgvector
Lee discovery_forense/ completo del repo (incluye crisol_plans, sop_epia_diff, otros). Genera embeddings con OpenAI text-embedding-3-small o el modelo que prefieras. Crea tabla pgvector en Supabase (proyecto del Monstruo, no crear org nueva — ya está conectada). Schema sugerido: id, source_path, content_chunk, embedding, metadata jsonb. Indexa todo. Confirma con un query de validación: cuántos chunks indexados, cuántas fuentes únicas.

TAREA 5 — Canonización SOP/EPIA en Notion
Toma como canónicos:
- SOP: el archivo discovery_forense/sop_epia_diff/SOP_v1.2_DRIVE.md (43KB)
- EPIA: el archivo discovery_forense/sop_epia_diff/EPIA_FUNDACIONAL_DBX.md (30KB+)
Crea o actualiza dos páginas en Notion bajo "🏗️ Plan de Construcción: El Monstruo v0.1":
- "📜 SOP Fundacional v1.2 — CANÓNICO"
- "🧭 EPIA Fundacional v1.0 — CANÓNICO"
Marca claramente el tag "[CANÓNICO]" y la fecha de canonización. En la descripción incluye el reporte de discrepancias detectadas (que ambas plataformas estaban desincronizadas y la canonización tomó la versión más completa de cada una).

═══════════════════════════════════════════════════
PROTOCOLO DE COMUNICACIÓN CONMIGO (MANUS)
═══════════════════════════════════════════════════

Si necesitas que yo (Manus) ejecute algo (descargar de S3, leer Dropbox, procesar archivos pesados, query a sistemas que tú no tienes), edita bridge/manus_to_cowork.md con la sección "## SOLICITUD A MANUS" al final, commitea y pushea. Alfredo me avisa o yo lo veo en mi siguiente activación. Yo respondo con commit en la misma rama.

═══════════════════════════════════════════════════
APRENDIZAJES OPERATIVOS (registrar en El Monstruo)
═══════════════════════════════════════════════════

1. Cowork ≠ Claude Code terminal. Sandboxes Linux separados, no comparten filesystem.
2. Cowork desktop usa OAuth nativo + MCPs custom remotos para conectores. No accede al Mac.
3. Notion AI ejecuta acciones de admin cuando se le pide vía "Pedir a la IA" desde una página. Patrón humano-en-el-loop.
4. Notion no expone API pública para gestionar permisos de integración. Guardrail intencional.
5. MCP custom remoto en Cowork desktop es escape hatch poderoso pero requiere host persistente.
6. Patrón canónico Manus ↔ Cowork: bridge file en repo + ambos leen GitHub. NO filesystem compartido.

═══════════════════════════════════════════════════
ACCIÓN INMEDIATA
═══════════════════════════════════════════════════

1. Confirma que recibiste este briefing y entendiste la división de responsabilidades.
2. Lista cuáles de las 4 tareas (1, 2b, 3, 5) puedes ejecutar en paralelo y cuáles tienen dependencias.
3. Arranca con Tarea 2b (la más simple, solo GitHub) como warm-up.
4. Después Tarea 5 (Notion, archivos ya listos en repo).
5. Tarea 1 y Tarea 3 al final (más complejas).
6. Reporta progreso a Alfredo conforme avances. Yo (Manus) leeré tus commits para mantener sincronía.

Adelante, Cowork.

— Alfredo (vía Manus, Hilo B)
```

---

## FIN PROMPT

Después de pegarlo, Cowork va a confirmar y arrancar. Si necesita algo de Manus durante su ejecución, te lo va a decir o lo va a escribir en `bridge/manus_to_cowork.md`. Tú me avisas y yo respondo.
