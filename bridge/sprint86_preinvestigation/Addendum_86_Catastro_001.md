# Addendum 86-Catastro-001 · 2026-05-04

**Autor:** [Hilo Manus Catastro]
**Estado:** Pendiente de OK por Cowork

## Cambios al SPEC SPRINT 86 v1 incorporando hallazgos de pre-investigación

### Cambio 1 — De scrapers a clientes API

**SPEC v1 sección "Fuentes de alimentación" dice:**
"8 primarias programáticas (Artificial Analysis, LMArena, HF Leaderboards, Papers With Code, GitHub Radar, Replicate/FAL/Together, anuncios vendor, pricing pages) + N secundarias por dominio. Pipeline diario automatizado asume scraping HTML para extraer métricas."

**Realidad validada:**
Validación en tiempo real (2026-05-04) demostró que 6 de las 8 fuentes primarias tienen API REST oficial gratuita o de bajo costo. El scraping de LMArena está explícitamente prohibido por ToS, pero publican un dataset oficial en Hugging Face.

**Spec v2 dice:**
"El pipeline diario se alimentará mediante **clientes API REST oficiales**, no scrapers HTML.
- **Artificial Analysis:** API REST oficial (`/data/llms/models`, `/data/media/*`), header `x-api-key`.
- **LMArena:** HuggingFace dataset oficial (`lmarena-ai/leaderboard-dataset`).
- **HF Open LLM:** Datasets server REST API.
- **Replicate, FAL, Together:** APIs REST oficiales para catálogo y pricing.
El Sprint 86 construirá clientes API (`kernel/catastro/sources/*.py`) en lugar de parsers de DOM. Esto reduce ~70% la deuda de mantenimiento y baja el costo de ejecución a ~$0.30/día."

---

### Cambio 2 — Quinta tabla `catastro_curadores`

**SPEC v1 sección "Stack" dice:**
"Supabase (Postgres + pgvector) + Next.js + FastAPI + MCP server. Tablas principales: `catastro_modelos`, `catastro_historial`, `catastro_eventos`, `catastro_quorum_log`."

**Realidad validada:**
El mecanismo anti-alucinación sugerido por Cowork requiere trackear la confiabilidad de los 10 curadores-LLM a lo largo del tiempo para evitar que un modelo degrade la calidad del Catastro si empieza a fallar el cuórum.

**Spec v2 dice:**
"El schema Supabase incluirá una **quinta tabla: `catastro_curadores`**. Esta tabla almacenará el `trust_score`, `total_validaciones`, `fallos_quorum`, y un flag `requiere_hitl`. El Trust Score se actualizará dinámicamente en cada corrida del pipeline. Si un curador baja de cierto threshold, el sistema levanta flag HITL (Human-in-the-loop) para revisión."

---

### Cambio 3 — Ola 6 de Credenciales (Provisioning Catastro)

**SPEC v1 sección "Pre-requisitos" dice:**
"Sprint 85 cerrado verde. Credenciales OPENAI/ANTHROPIC/GEMINI auditadas y rotadas."

**Realidad validada:**
El cambio a clientes API (Cambio 1) requiere 4 tokens nuevos específicos para el Catastro que no existían en el ecosistema.

**Spec v2 dice:**
"Pre-requisito adicional: **Ola 6 de credenciales completada**. El `[Hilo Manus Credenciales]` debe aprovisionar 4 keys con scope mínimo y patrón de nombrado `{provider}-api-key-monstruo-2026-05`:
1. `ARTIFICIAL_ANALYSIS_API_KEY` (Categoría C)
2. `REPLICATE_API_TOKEN` (Categoría B/C)
3. `FAL_API_KEY` (Categoría B/C)
4. `HF_TOKEN` (Categoría C, read scope)
*(Nota: `TOGETHER_API_KEY` se procesa en la Ola 5 junto con el resto de LLM providers).* Estas keys deben inyectarse en el entorno de ejecución de Railway del kernel."

---

### Cambio 4 — Eliminación de dependencia "6 respuestas"

**SPEC v1 (vía commit `7e5dea4`) dice:**
"sprint 85: priorizo calidad sobre preview pane - critico visual obligatorio + 6 respuestas para sprint 86"

**Realidad validada:**
Cowork clarificó (Decisión 3, 2026-05-04) que esas 6 respuestas pertenecían al diseño obsoleto del Sprint 86 como "Live Preview Pane". El Sprint 86 actual es exclusivamente El Catastro.

**Spec v2 dice:**
"Las '6 respuestas técnicas' del commit `7e5dea4` **no son bloqueantes ni aplicables** al Sprint 86. El Live Preview Pane queda diferido al Sprint 87+. El Sprint 86 se enfoca 100% en el pipeline de datos, schema Supabase y MCP Server de El Catastro."

---

### Notas adicionales de implementación (Reuso)

Durante la pre-investigación se confirmó que el Sprint 86 heredará patrones y código de:
- **Brand Engine (Sprint 82):** Validación de nombres y reportes.
- **Vanguard:** Lógica base de clientes HTTP con rate limit (`semantic_scholar.py`) y generación de digests.
- **Error Memory:** Registro de fallos de cuórum para evitar reintentos inútiles.
- **FastMCP Server:** Montaje de las 5 tools del Catastro sobre el hub existente.

*(Este addendum no altera los 14 Objetivos Maestros, la fórmula del Trono Score, ni la arquitectura conceptual del Quorum Validator).*
