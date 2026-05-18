# 01 — SCOPE AND RULES

## Alcance del atlas

El **MONSTRUO REALITY ATLAS** cubre la totalidad del proyecto El Monstruo a un nivel de granularidad operativa, no especulativa. El alcance incluye los siguientes ejes de análisis. El primero es el **inventario de repositorios accesibles** del usuario `alfredogl1804` en GitHub, agrupados por relevancia (core del Monstruo, proyectos adyacentes, artefactos de pipeline E2E). El segundo es el **inventario de producción viva**: aplicaciones desplegadas en Vercel, Railway, Cloudflare Workers o cualquier infraestructura que haya llegado a runtime. El tercero es el **registro de canon firmado**: APP_VISION, DSCs, AGENTS.md, audits Cowork firmados, specs aprobadas. El cuarto es el **registro de sprints**: propuestos, firmados, en vuelo, completados. El quinto es el **ledger de aliases** que resuelve nomenclatura disjunta entre Alfredo, Cowork, ChatGPT y código. El sexto es la **coverage matrix** que cataloga 50+ conceptos del Monstruo con concept_id, evidencia, status y aliases. El séptimo es el **registro de drift** entre código y doctrina, con paths line:line. El octavo es el registro de **gaps y unknown unknowns** explícitos.

El atlas no cubre el diseño detallado de cada superficie de UI (eso está en el Context Fabric) ni la arquitectura interna de cada módulo del kernel (eso está en `kernel/*/README.md` de cada módulo).

## Reglas operativas inviolables

### Regla 1 — No redibujar lo cubierto

Si un concepto tiene estado `FIRMADO_VIGENTE` en `05_CANON_REGISTRY.md`, ningún agente puede redefinirlo. Lo único permitido es extenderlo con evidencia nueva o proponer deprecación con justificación firmada por Alfredo. Esta regla previene que ChatGPT, Cowork, Perplexity o Manus reinventen conceptos ya canonizados solo porque no los encontraron a primera vista.

### Regla 2 — Verdad por evidencia

Toda afirmación tiene un campo `source_id` que apunta a un archivo real con `path:line` o blob SHA verificable vía `gh api`. Las afirmaciones sin evidencia se etiquetan `REQUIERE_VERIFICACION` o `HIPOTESIS_NACIENTE`. La validación contra realidad presente es obligatoria, no opcional.

### Regla 3 — No canonizar hipótesis nacientes

Si Alfredo dijo verbatim "está naciendo", "es una hipótesis", "estoy explorando" o el concepto solo vive en chat sin documento firmado, el estado canónico es `HIPOTESIS_NACIENTE_T1_LIVE`. Ningún agente promueve a canon sin firma explícita de Alfredo en formato DSC.

### Regla 4 — Aliases se resuelven, no se reescriben

Si dos términos refieren al mismo concept_id, ambos se preservan en `07_ALIAS_LEDGER.yaml` con un campo `canonical_term` y un array `aliases[]`. La resolución es bidireccional: ChatGPT puede consultar tanto por el alias como por el canónico y obtener el concept_id correcto.

### Regla 5 — Drift se documenta, no se corrige solo

Si código contradice doctrina firmada (caso típico: brand DNA del app móvil con cyan/púrpura vs DSC-MO-002 firmado con forja/graphite/acero), el drift se captura en `domains/` con path:line y se eleva como decisión T1 firmada. No se "limpia" silenciosamente con un commit, porque eso oculta la divergencia.

### Regla 6 — Verificación de existencia obligatoria

Después de cualquier operación de escritura/commit/push, el agente verifica con `gh api` que el archivo existe en el remoto. Si `gh api` devuelve HTTP 404, NO declarar verde. Reintentar hasta confirmación binaria.

### Regla 7 — Trazabilidad bidireccional con sabios

Cada vez que ChatGPT pide algo a Manus, queda registrado en `prompts/` con request_id. Cada respuesta de Manus incluye el request_id que satisface. Esta trazabilidad evita pérdida de contexto en handoffs.

### Regla 8 — Preservación de raw_rescues

Cualquier checkpoint, transcripción o documento entregado por Alfredo o un sabio externo se preserva verbatim en `raw_rescues/` antes de cualquier interpretación. Las interpretaciones derivadas viven en archivos separados con marcado explícito de su origen.

## Interacción con AGENTS.md raíz

Este atlas opera bajo las **8 Reglas Duras** de `AGENTS.md` raíz del repo `el-monstruo`. En particular son críticas la **Regla 1** (15 Objetivos Maestros aplican a TODO), **Regla 6** (Cero secrets en plaintext), **Regla 8** (Plano de identidad auditable), **Regla 7** (RLS universal) cuando se toquen tablas Supabase. Cualquier acción del atlas que viole AGENTS.md se rechaza.

## Roles de los sabios y de Manus

- **Alfredo Góngora** — único firmante T1 magna. Decide canonización.
- **ChatGPT 5.5 Pro** — arquitecto de doctrina. Toma ownership de iteraciones de APP_VISION.
- **Cowork (Claude Sonnet)** — auditor de contenido. Audita specs antes de cierre de sprint. Solo Cowork puede declarar "audit verde" para sprints que toquen kernel/scripts/apps.
- **Perplexity Sonar Reasoning Pro** — investigador real-time. Valida hipótesis con web actual.
- **Manus** — ejecutor técnico. Construye archivos, hace commits, audita repos, ejecuta scripts. NO firma canon, NO decide arquitectura.

## Política de commits para este atlas

Todos los commits que modifiquen `monstruo_reality_atlas/` deben:
1. Pasar `bash scripts/_check_no_tokens.sh` (regla 6 AGENTS.md) si tocan código.
2. Llevar mensaje en formato `atlas(scope): descripción` o `atlas(iter-NNN): descripción`.
3. Incluir referencia al `request_id` si responden a un pedido de un sabio.
4. Verificarse vía `gh api` post-push antes de declarar el sprint cerrado.

---

*Procedé con `10_DO_NOT_REDESIGN_BEFORE_READING.md`.*
