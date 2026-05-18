# 00 — START HERE FOR CHATGPT

**MONSTRUO REALITY ATLAS — iteración 001**
**Reconstruido: 2026-05-17 (post-fallo FUSE mount sync)**
**Owner del proyecto:** Alfredo Góngora
**Repo:** github.com/alfredogl1804/el-monstruo
**Rama:** monstruo-reality-atlas-001

---

## Qué es este atlas

Atlas universal del Monstruo. Cataloga la realidad operativa completa del proyecto: repos accesibles, producción viva, conceptos canonizados, sprints en vuelo, aliases de nomenclatura, drift entre código y doctrina, gaps explícitos.

**Su propósito principal:** liberar a Alfredo de tener que recordar nombres exactos de conceptos. Si Alfredo escribe "Cronista Familiar" o "Herencia Narrativa" o "Día One Familiar", el atlas resuelve esos aliases al concept_id canónico (`cronos_modo_cripta`).

## Reglas operativas inviolables

1. **No redibujar lo cubierto**. Si un concepto ya está en `05_CANON_REGISTRY.md` con estado `FIRMADO_VIGENTE`, no lo redefinís — lo extendés con evidencia nueva o proponés deprecación con justificación.

2. **Verdad por evidencia**. Toda afirmación en este atlas tiene un `source_id` que apunta a un archivo real en el repo, con `path:line` o blob SHA. Si no hay evidencia, el campo se etiqueta `REQUIERE_VERIFICACION` o `HIPOTESIS_NACIENTE`.

3. **No canonizar hipótesis nacientes**. Si Alfredo dijo "está naciendo" o el concepto solo vive en chat, el estado es `HIPOTESIS_NACIENTE_T1_LIVE`. Ningún agente promueve a canon sin firma explícita de Alfredo.

4. **Aliases se resuelven, no se reescriben**. Si dos términos refieren al mismo concept_id, ambos quedan en `07_ALIAS_LEDGER.yaml` con `canonical_term` y `aliases[]`.

5. **Drift se documenta, no se corrige solo**. Si código contradice doctrina firmada, el drift se captura en `domains/` con path:line y se eleva como decisión T1, no se "limpia" silenciosamente.

## Orden de lectura para ChatGPT

Para tomar ownership del atlas en menos de 30 minutos, ChatGPT lee en este orden:

1. **`00_START_HERE_FOR_CHATGPT.md`** (este archivo)
2. **`01_SCOPE_AND_RULES.md`** — alcance y reglas operativas extendidas
3. **`10_DO_NOT_REDESIGN_BEFORE_READING.md`** — guardarraíl crítico contra reinventar lo existente
4. **`08_EXISTING_DESIGN_COVERAGE_MATRIX.md`** — la pieza más importante: 50+ conceptos catalogados
5. **`07_ALIAS_LEDGER.yaml`** — resolución de aliases canónicos
6. **`05_CANON_REGISTRY.md`** — registro consolidado de canon firmado vigente
7. **`06_SPRINT_REGISTRY.md`** — sprints propuestos y firmados
8. **`09_GAPS_AND_UNKNOWN_UNKNOWNS.md`** — qué falta y qué no sabemos que no sabemos
9. **`ITERATION_001_REPORT.md`** — resumen ejecutivo de esta iteración

Después, ChatGPT consulta on-demand:
- **`maps/`** (8 maps) — cuando necesite vista por dimensión específica
- **`domains/`** (5+ domain packs) — cuando necesite profundidad sobre un dominio
- **`02_SOURCE_LEDGER.jsonl`** — cuando necesite verificar fuentes
- **`prompts/`** — cuando necesite enviar trabajo a Cowork, Perplexity o Manus

## Hallazgos magna de iter 001

1. **"Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar"** son aliases del concept_id `cronos_modo_cripta`, ya canonizado en `docs/EL_MONSTRUO_APP_VISION_v1.md` capítulo 5 con Shamir Secret Sharing. Nombre canónico Cowork: `río de vida / river of life`. Verificado verbatim línea 194 del audit Cowork 2026-05-11.

2. **Drift binario brand DNA** confirmado en código: `apps/mobile/lib/core/theme/brand_dna.dart` líneas 10-56 usa `primary=#00E5FF` (cyan ChatGPT) y `secondary=#BB86FC` (púrpura Material), contradiciendo doctrina firmada DSC-MO-002 (forja `#F97316` + graphite `#1C1917` + acero `#A8A29E`).

3. **Capabilities 0/8 transversales en código** — la audit Cowork 2026-05-11 confirmó que ninguna de las 8 capabilities del kernel está implementada al 100%.

4. **Command Center solo tiene 7 superficies** vs 12-15 canon Cockpit en APP_VISION.

5. **14 sprints en `bridge/sprints_propuestos/` están en estado `PROPUESTO_SIN_FIRMA`**, bloqueando arranque de implementación.

6. **5 decisiones T1 magna pendientes** (audit Cowork §8) más 4 nuevas detectadas en este atlas.

7. **Checkpoint pre-IA 2020-2021** preservado en `interfaces_context_fabric/raw_rescues/` (rama `interfaces-context-fabric-001`) con 10 hipótesis y 5 órganos latentes. EN_EXTRACCION_T1, no canonizado.

## Relación con el Context Fabric

El **Context Fabric** (`interfaces_context_fabric/` en rama `interfaces-context-fabric-001`) es un atlas previo de 49 archivos enfocado **exclusivamente en la dimensión INTERFACES** del Monstruo. Tiene 12 PACKs canónicos, 9 maps, 3 prompts a sabios, y raw_rescues.

El **Reality Atlas** (este, `monstruo_reality_atlas/` en rama `monstruo-reality-atlas-001`) es el atlas **universal** que cubre TODO el Monstruo: repos, producción, canon, sprints, aliases, gaps, no solo interfaces.

**No duplicar**. Si ChatGPT busca dimensión interfaces en profundidad, va al fabric. Si busca atlas universal con resolución de aliases y coverage matrix, va a este atlas.

## Qué NO hacer

- No empezar a escribir APP_VISION v1.4 sin confirmación explícita de Alfredo.
- No firmar sprints propuestos sin pasar por la regla de cierre canónica del Monstruo (`bash scripts/_check_no_tokens.sh` + audit Cowork + DSC firmado).
- No promover hipótesis nacientes a canon sin firma de Alfredo.
- No "limpiar" drift en código sin captura previa como decisión T1.
- No reinventar conceptos que ya están en `08_EXISTING_DESIGN_COVERAGE_MATRIX.md`.

## Confirmaciones requeridas tras la lectura

ChatGPT debe confirmar a Alfredo:
1. Que leyó los 9 archivos del orden de lectura.
2. Las 5 contradicciones más urgentes que detectó.
3. El orden de ataque propuesto para iter 002.
4. Las preguntas irreducibles que requieren intervención humana de Alfredo (máximo 5).

Hasta recibir respuesta de Alfredo, ChatGPT no escribe doctrina nueva.

---

*Fin de start. Procedé con `01_SCOPE_AND_RULES.md`.*
