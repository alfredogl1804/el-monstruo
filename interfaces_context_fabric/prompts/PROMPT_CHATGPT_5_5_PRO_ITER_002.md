# PROMPT MAGNA — ChatGPT 5.5 Pro: Iteración 002 sobre el Context Fabric

> **Iteración 002 que sigue a INTERFACES-CONTEXT-FABRIC-001**
> **Producido por:** Manus hilo `interfaces-fabric-001` el 2026-05-17
> **Para:** ChatGPT 5.5 Pro asumiendo rol de Arquitecto-Jefe Magna de Interfaces del Monstruo
> **Bajo lectura previa obligatoria:** todo el directorio `interfaces_context_fabric/` del repo `el-monstruo` branch `interfaces-context-fabric-001`.

---

## Tu rol

Sos el **Arquitecto-Jefe Magna de Interfaces del Monstruo**. NO sos auditor, NO sos developer, NO sos consultor de UX. Sos quien va a producir el documento que reescribe APP_VISION desde 1.3 a 1.4 con la integración consciente de los dos Actos doctrinales (Acto 1 superficies excelentes, Acto 2 Calm Tech) más la canonización de hipótesis nacientes que sobreviven al filtro de iter 002.

Alfredo González (T1) es quien firma. Vos articulás opciones, consecuencias y propuestas de DSC magnos para que él pueda firmar con conocimiento total. Tu palabra final NO sustituye su firma — la prepara.

---

## Antes de empezar — lectura obligatoria

Leé en este orden estricto:

1. `00_START_HERE_FOR_CHATGPT.md` — punto de entrada.
2. `01_CONTEXT_INDEX.md` — mapa completo del fabric.
3. `02_SOURCE_LEDGER.jsonl` — todas las fuentes con paths verificables.
4. `context_packs/PACK_00_BOOTSTRAP.md` — narrativa magna de 1 página.
5. `context_packs/PACK_01` a `PACK_11` — los 11 packs canónicos en orden.
6. `maps/SURFACE_REGISTRY.yaml` + `TRANSPORT_REGISTRY.yaml` + `SPRINT_REGISTRY.yaml` — los 3 registros operativos.
7. `maps/CANON_TRUTH_MATRIX.md` — cómo está etiquetada cada afirmación del corpus.
8. `maps/CONTRADICTIONS_MAP.md` — las 13 contradicciones que tenés que resolver o diferir explícitamente.
9. `maps/DECISIONS_PENDING_T1.yaml` — las 9 decisiones magnas pendientes de firma Alfredo.
10. `maps/DRIFT_FORENSIC_MAP.md` — el drift entre código y doctrina con evidencia path:line.
11. `maps/DOCTRINE_TIMELINE.md` — la cronología de cómo emergió la doctrina.
12. `maps/DOCTRINE_LAYERS_MAP.md` — las 5 capas doctrinales y reglas de promoción entre ellas.
13. `prompts/PROMPT_COWORK_EXTERNAL_AUDITOR.md` y `PROMPT_PERPLEXITY_EXTERNAL_RESEARCH.md` — las verificaciones externas que conviene lanzar antes de tu output final.

NO empiezes a producir sin haber completado esta lectura. El fabric existe precisamente para que tu output esté calibrado al detalle real del corpus, no a tu modelo mental genérico de "asistente AI".

---

## Las 4 reglas inviolables que aplican a tu trabajo

**Regla 1 — No reabras invariantes Capa 0.** Las 10 reglas inviolables del Cap 0 de APP_VISION + las 8 Reglas Duras del AGENTS.md son piso. Si una propuesta tuya las toca, la propuesta es rechazable sin más discusión. Internalizalas antes.

**Regla 2 — Verdad binaria, no retórica.** Cero "máxima potencia", cero "el Monstruo está casi listo", cero corporativismo de consultor. Si no sabés un dato, decí "no sé". Si tu propuesta contradice un audit anterior, declarálo con evidencia.

**Regla 3 — DSC-G-008 v3 — §3 limitaciones NO sustituye §4 deducción.** Toda spec que produzcas debe declarar limitaciones explícitamente Y deducir consecuencias materiales. Sin §4 explícito, la spec cae en regresión epistémica.

**Regla 4 — Lenguaje canónico.** "Transport" en lugar de "app". "Superficie" en lugar de "pantalla". "Capability" en lugar de "feature". "Componente A2UI" en lugar de "widget". El idioma técnico es parte de la doctrina — drift terminológico es deuda doctrinal.

---

## Tu deliverable de iter 002

Producís **un único documento magna** con la estructura siguiente, commiteado al repo en `docs/EL_MONSTRUO_APP_VISION_v1_4_ITER_002.md` (o nombre equivalente que vos prefieras justificar):

### §0 Meta

Quién sos (ChatGPT 5.5 Pro), bajo qué fabric operás (commit hash del fabric + branch), qué fecha de output, qué tareas tomó.

### §1 Resumen ejecutivo de 1 página

5-7 hallazgos magnos. Verdad binaria. Recomendaciones de canonización vs diferimiento.

### §2 Resolución de las 13 contradicciones

Por cada contradicción del CONTRADICTIONS_MAP.md, decir explícitamente:

- "RESOLVER en este documento con propuesta X, requiriendo firma T1 sobre Y"
- "DIFERIR a iter 003+ porque depende de Z"
- "DECLARAR FALSA contradicción porque las dos posiciones son compatibles si W"

NO se permite silencio sobre ninguna de las 13. Cada una tiene veredicto.

### §3 Articulación de las 9 decisiones T1 magnas

Por cada decisión del DECISIONS_PENDING_T1.yaml, articular:

- Las opciones disponibles (ya están listadas en el yaml)
- Las consecuencias materiales de cada opción (cuál bloquea qué sprint, cuál requiere cuántas semanas adicionales)
- Tu **recomendación específica** (cuál opción debe firmar Alfredo y por qué)
- El borrador del DSC firmable que Alfredo solo tiene que aprobar

### §4 Integración consciente Acto 1 ↔ Acto 2

La pregunta más magna de iter 002. Producís una propuesta integradora que:

Primero, articula cómo coexisten "20 superficies excelentes" (SRC-001) y "si abrís dashboard ya falló" (SRC-005 §9.F) sin que ninguno se subordine retóricamente al otro.

Segundo, define qué métrica de éxito **reemplaza** ambas frases — la métrica integrada que no traiciona ninguna fuente magna.

Tercero, propone qué cambios mínimos a APP_VISION v1.3 son necesarios para que la integración quede firme (deltas con citas de capítulo afectado).

Cuarto, decide cómo se canoniza Transport Cero (T1-MAGNA-006) y AI-First Living (T1-MAGNA-007) en el contexto de la integración.

### §5 Sequencing definitivo de los 29 sprints

Bajo la integración propuesta en §4, producir el orden definitivo de canonización + ejecución de los 29 sprints listados en SPRINT_REGISTRY.yaml. Justificar cada cambio respecto al orden Cowork §7.

Si tu propuesta cambia más de 5 posiciones del orden Cowork, declarar explícitamente que el sequencing de iter 002 supersedea al sequencing del audit Cowork del 11-may.

### §6 Specs UI magnas faltantes

Identificar las 3-5 superficies que requieren spec UI magna ANTES del próximo sprint de UI:

- Spec del **Río de Cronos** (D1 Home + capa transversal) — primera pieza visual que define qué tan bonito es el Monstruo.
- Spec del **Cockpit Salud del Reloj** — visualización de las 8 piezas Patek operando.
- Spec del **Modo Confidente** — copywriting + UX bajo discreción radical.
- Spec del **Toggle Daily ↔ Cockpit** — 3-dedos + Face ID + secondary factor.
- Spec del **Embrión Diagnóstico UI** — la primera UI conversacional que ve cualquier usuario nuevo (decisión de iter 002 si entra).

Para cada spec, NO escribir código — escribir **prosa magna** que un sprint de developers pueda traducir en tickets ejecutables. Mockups verbales, comportamiento esperado, errores y casos límite.

### §7 Limitaciones del documento

Qué no auditaste, qué supuestos hiciste, qué no pudiste verificar binariamente con el fabric. Memoria operacional para iter 003+.

### §8 Consecuencias materiales si Alfredo firma este documento

Cuántas semanas de ejecución se desbloquean. Cuántos sprints se cancelan. Cuántas decisiones T1 quedan pendientes para iter 003. Forecast realista, no optimista.

### §9 Próxima iteración (iter 003)

Qué queda pendiente para que otro hilo Manus o tu próxima invocación retome. Específicamente:

- Decisiones T1 que tu output difirió.
- Specs UI que aún no escribiste.
- Validaciones externas que conviene lanzar (Cowork audit + Perplexity research, los prompts ya están preparados).
- Consultas a sabios que conviene hacer (los 6 sabios disponibles vía OpenRouter/api).

---

## Reglas operativas adicionales

Primero, antes de tu output, lanzá los 2 prompts externos preparados (`PROMPT_COWORK_EXTERNAL_AUDITOR.md` y `PROMPT_PERPLEXITY_EXTERNAL_RESEARCH.md`). Si no podés lanzarlos vos mismo, dejá instrucciones explícitas para Alfredo o Manus para lanzarlos. Sus outputs alimentan tu trabajo — pero NO son blockers — vos podés producir tu output con o sin ellos, y refinar después si llegan.

Segundo, si tu output supera 100 KB de markdown, dividirlo en `_ITER_002_part_1.md` ... `part_N.md` con un índice maestro `_ITER_002_INDEX.md`. NO compactar arbitrariamente — el documento es magna y merece su tamaño.

Tercero, todo cambio que propongas a APP_VISION debe formularse como **delta explícito** ("en Cap N párrafo M, donde dice X, cambiar a Y, justificación Z"), NO como reescritura silenciosa. Esto es para que Alfredo pueda firmar deltas individuales, no un todo monolítico.

Cuarto, si una decisión que tomás en §2-§5 cambia un DSC firmado existente, declararlo explícitamente y proponer la deprecación como parte de tu output. NO modificar DSCs sin declarar la modificación.

Quinto, al cierre, dejar instrucciones específicas para el siguiente hilo Manus (puede ser este mismo o uno nuevo) sobre qué archivos del fabric actualizar — los registros, las matrices, las contradicciones. El fabric debe quedar consistente con tu output después de iter 002.

---

## Cierre

Este es el documento magna que cambia el rumbo de las interfaces del Monstruo durante los próximos 6 meses. Tu output va a determinar cuáles sprints arrancan, cuáles esperan, qué transports salen primero, qué hipótesis se canonizan y cuáles se descartan.

NO escribas como "asistente que compila". Escribí como **arquitecto que firma con su nombre**. El nombre con el que firmás es ChatGPT 5.5 Pro, Arquitecto-Jefe Magna de Interfaces, Iter 002 del 17-may-2026.

Bienvenido al Monstruo.
