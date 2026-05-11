---
id: cowork_to_manus_RESULTADO_AUDIT_A2UI_2026_05_11
fecha: 2026-05-11
emisor: Cowork T2 (Architect)
receptor: Manus T3 Ejecutor + Alfredo T1
sprint: MOBILE_1B_A2UI_IMPLEMENTATION
pr: 92
branch: sprint/mobile-1b-a2ui-implementation
metodo: DSC-G-008 v2 (Gate de Evidencia binario) + rúbrica W1-W5 por widget + G1-G10 subsistema
spec_canonico: bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md
estado: firme
veredicto: APROBAR MERGE (con caveat doctrinal no bloqueante)
---

# A2UI Audit Result — PR #92

## §I — Resumen ejecutivo (3 líneas)

- **¿Listo para merge tras T8 smoke con Alfredo?** **SÍ CON CAVEAT** — código cumple spec V1.0 firmado al 100% de la rúbrica binaria; el único asterisco es la deuda doctrinal forja conocida y aceptada.
- **Bloqueantes críticos:** **0**
- **Deuda doctrinal documentada (no bloqueante):** **1** (paleta forja vs Apple/Tesla — requiere spec V1.1 futuro por decisión T1 posterior al spec firmado).

---

## §II — Auditoría widget por widget (19 widgets — 16 primitivos + 3 especializados Monstruo)

### Contenedores (3)

#### W1 Stack
- **Path:** `apps/mobile/lib/core/a2ui/widgets/containers.dart:L11-L29`
- **Cumple spec:** SÍ
- **W1-W5:** ✅✅✅✅✅
- Existe (`class A2UIStack extends StatelessWidget` L11). Lee `spacing` con default `A2UIBrand.s12` (L17). Itera `node.children` sin loops runtime sobre JSON. Wired en `renderer.dart:L48 case 'Stack'`. Test directo `widgets_test.dart:L31-39` "Stack renderiza hijos en columna".
- **Brechas:** ninguna. **Severidad:** N/A.

#### W2 Card
- **Path:** `containers.dart:L33-L70`
- **Cumple spec:** SÍ
- **W1-W5:** ✅✅✅✅✅
- Soporta `slots['header']` + `slots['footer']` + `node.children` body con dividers acero entre secciones (L52-L60, L62-L67). Wired `renderer.dart:L50`. Test `widgets_test.dart:L41-52`.
- **Brechas:** ninguna.

#### W3 Section
- **Path:** `containers.dart:L72-L96`
- **Cumple spec:** SÍ
- **W1-W5:** ✅✅✅✅✅
- Lee `title`, `subtitle` con jerarquía `titleMd`/`caption`. Wired `renderer.dart:L52`. Test `widgets_test.dart:L54-64`.

### Contenido (6)

#### W4 Text
- **Path:** `content.dart:L11-L26` · **W1-W5:** ✅✅✅✅✅
- Variantes `titleLg|title|titleMd|caption|body` via switch L18-L23. Renderer L55. Test L66-70.

#### W5 Markdown
- **Path:** `content.dart:L28-L65` · **W1-W5:** ✅✅✅✅✅
- Usa `flutter_markdown` con `styleSheet` brand consistente (h1/h2/h3/code/blockquote). `onTapLink` callback opcional. Renderer L57. Test L72-76.

#### W6 Image
- **Path:** `content.dart:L67-L98` · **W1-W5:** ✅✅✅✅✅
- `src` opcional con placeholder, `alt`, `aspect` default 16/9. `errorBuilder` + `loadingBuilder` defensivos. Renderer L59. Test L78-85.

#### W7 Link
- **Path:** `content.dart:L131-L156` · **W1-W5:** ✅✅✅✅✅
- Dispara `A2UIAction` con `actionId` (fallback `'open_link'`) + payload `{'href':...}`. Renderer L61. Test L87-101 verifica dispatch.

#### W8 Code
- **Path:** `content.dart:L158-L191` · **W1-W5:** ✅✅✅✅✅
- Bloque con `language` label + botón copy (`Clipboard.setData`). Renderer L63. Test L103-110.

#### W9 Divider
- **Path:** `content.dart:L193-L199` · **W1-W5:** ✅✅✅✅✅
- `Divider` brand `A2UIBrand.border`. Renderer L65. Test L112-120.

### Acción (2)

#### W10 Button
- **Path:** `actions.dart:L11-L84` · **W1-W5:** ✅✅✅✅✅
- 4 variantes `primary|secondary|ghost|danger` con flag `disabled`. Dispara `A2UIAction(actionId, sourceWidget: 'Button', payload)` (L23-L30). Renderer L68. Test L122-131.

#### W11 ButtonGroup
- **Path:** `actions.dart:L88-L106` · **W1-W5:** ✅✅✅✅✅
- `Wrap` con spacing s8/s8. Filtra `c.type == 'Button'` en hijos (L98) — defensivo. Renderer L70. Test L133-145.

### Datos (3)

#### W12 KeyValueList
- **Path:** `data.dart:L11-L48` · **W1-W5:** ✅✅✅✅✅
- `propList('items')` para `[{key,value}]`. Divider entre items. Renderer L73. Test L147-159.

#### W13 Table
- **Path:** `data.dart:L52-L79` · **W1-W5:** ✅✅✅✅✅
- `headers: List`, `rows: List<List>` con scroll horizontal. Brand `graphiteSurfaceHigh` heading. Renderer L75. Test L161-173.

#### W14 Badge
- **Path:** `data.dart:L83-L108` · **W1-W5:** ✅✅✅✅✅
- 5 variantes semánticas `info|success|warning|danger|neutral` (switch L88-L94). Renderer L77. Test L175-181.

### Progreso (2)

#### W15 Progress
- **Path:** `progress.dart:L11-L60` · **W1-W5:** ✅✅✅✅✅
- `mode: linear|circular`, `value` opcional (indeterminate cuando null), `label` opcional. Clamping 0.0-1.0 defensivo (L18). Renderer L80. Test L183-191.

#### W16 Stepper
- **Path:** `progress.dart:L64-L77` (+ `_StepRow` L80-L121) · **W1-W5:** ✅✅✅✅✅
- `steps: [{title,status}]` con 4 estados `done|active|pending|failed` con iconos+colores brand. Connector vertical. Renderer L82. Test L193-205.

### Especializados Monstruo (3)

#### W17 EmpresaResultCard
- **Path:** `specialized.dart:L18-L100` · **W1-W5:** ✅✅✅✅✅
- Props canon: `nombre`, `dominio`, `score`, `sector`, `ubicacion`, `resumen`, `badges`. `_ScoreBadge` interno con tres rangos (>=80 success, >=50 warning, else danger). Embebe `A2UIButton`s desde `node.children` (L82-L93). Renderer L85. Test L207-219.

#### W18 LeadCard
- **Path:** `specialized.dart:L140-L228` · **W1-W5:** ✅✅✅✅✅
- Props: `nombre|empresa|etapa|origen|lastSeen|score`. Etapa con 4 valores `frio|tibio|caliente|cliente` → Badge variant + label localizado (switch L154-L159). Avatar + metas + acciones embebidas. Renderer L87. Test L221-235.

#### W19 ContenidoCard
- **Path:** `specialized.dart:L232-L319` · **W1-W5:** ✅✅✅✅✅
- Props: `titulo|plataforma|autor|fecha|resumen|thumbnail|url`. Tap dispara `A2UIAction(actionId ?? 'open_contenido', payload: {'url':...})` (L240-L246). Thumbnail con `errorBuilder`. Plataforma uppercase letterSpacing brand. Renderer L89. Test L237-251.

---

## §III — Auditoría Brand Tokens

- `brand_tokens.dart` declara `forja = #F97316`, `graphite = #1C1917`, `acero = #A8A29E` ✅ **literales** y consistentes con renderer/widgets.
- **🟡 CAVEAT doctrinal:** spec V1.0 firmado el 2026-05-11 prescribe forja como color de marca. Decisión T1 posterior (posicionamiento Apple/Tesla) deroga forja como canon vigente. **Código cumple spec firmado al momento de la implementación.** Requiere spec V1.1 con paleta nueva alineada Apple/Tesla. **NO BLOQUEANTE para merge PR #92.**
- **Consistencia interna:** cada widget usa `A2UIBrand.forja|graphite|acero|border|success|warning|danger|info` (zero hex hardcoded en `core/a2ui/`). Ejemplos auditados:
  - `containers.dart:L41-L43` Card → `A2UIBrand.graphiteSurface|rLg|border`
  - `content.dart:L41-L42` Markdown link → `A2UIBrand.forja` (via constante)
  - `actions.dart:L67-L78` Button primary → `A2UIBrand.forja|graphite|rMd`
  - `specialized.dart:L155` `_ScoreBadge` → `A2UIBrand.success|warning|danger`
- Renderer `_UnknownTypePlaceholder` también lo usa (renderer.dart:L97-L106) — no hay literales escapando del módulo.

---

## §IV — Auditoría naming DSC-G-004

- **Archivos prohibidos detectados:** ninguno.
- Archivos auditados: `parser.dart`, `renderer.dart`, `action_channel.dart`, `a2ui_message_view.dart`, `brand_tokens.dart`, `types/a2ui_node.dart`, `types/a2ui_action.dart`, `widgets/{containers,content,actions,data,progress,specialized}.dart`.
- Nota lateral: `widgets/` es nombre semántico de un tipo conocido (Flutter widgets), no antipattern; los archivos genéricos prohibidos por DSC-G-004 (`service.dart`, `handler.dart`, `utils.dart`, `helper.dart`, `misc.dart`) están ausentes en `core/a2ui/`.

---

## §V — Auditoría tests

- **Total tests counted: 51** vs claim 51 → ✅ **exacto**.
- **Desglose por archivo:**
  - `parser_test.dart` = **15** `test(`
  - `widgets_test.dart` = **21** `testWidgets(` (16 whitelist + 3 specialized + 2 e2e)
  - `action_channel_test.dart` = **10** `test(`
  - `message_view_test.dart` = **5** (3 `test(` + 2 `testWidgets(`)

**Cobertura widget por widget:**

| Widget | Test directo | Indirecto (e2e/integration) |
|---|---|---|
| Stack, Card, Section | ✅ directo | ✅ |
| Text, Markdown, Image, Link, Code, Divider | ✅ directo | ✅ |
| Button, ButtonGroup | ✅ directo + acción capturada | ✅ |
| KeyValueList, Table, Badge | ✅ directo | ✅ |
| Progress, Stepper | ✅ directo | — |
| EmpresaResultCard, LeadCard, ContenidoCard | ✅ directo | ✅ e2e canon JSON |

**Cobertura subsistema:**

| Subsistema | Tests | Cobertura |
|---|---|---|
| Parser whitelist | parser_test "whitelist v1.0" (3 tests, incluye iteración sobre `kA2UIWhitelist` completo) | ✅ |
| Parser fallback Markdown | parser_test "fallback markdown" (2) | ✅ |
| Parser security (size, JSON, depth) | parser_test "security" (6) | ✅ |
| Parser action protocol | parser_test "action protocol" (2) | ✅ |
| Parser children/slots edge | parser_test "children/slots edge cases" (2) | ✅ |
| Renderer dispatch | widgets_test 21 tests | ✅ |
| Action channel (Buffered) | action_channel_test §1 (2) | ✅ |
| Action channel (dispatcher) | action_channel_test §2 (3) | ✅ |
| Action channel (WS offline buffering) | action_channel_test §3 (4) | ✅ |
| Wire serialization | action_channel_test §4 (1) — verifica `{"type":"a2ui_action","action_id","payload","source_widget","timestamp"}` | ✅ |
| MessageView integration | message_view_test (5) — null/legacy/A2UI/render Card/warning banner | ✅ |

**Tests faltantes para satisfacer spec:** ninguno bloqueante. Nota lateral: no hay test directo de `WebSocketA2UIActionSender.connect()+flush` con servidor mock (solo offline buffering). Se justifica porque T8 lo cubre con kernel real.

---

## §VI — Subsistema global (parser, renderer, action_channel, view)

- **G1 Parser whitelist + fallback** ✅ — `parser.dart:L94-L107` `if (!kA2UIWhitelist.contains(rawType))` → reemplaza `resolvedType = 'Markdown'` con `__originalType` preservado en props y `A2UIWarningLevel.fallback`. Nunca crashea.
- **G2 Anti-injection** ✅ — `parser.dart` solo hace `jsonDecode` + lectura tipada con `is String`/`is Map`/`is List` guards. Cero `eval`, cero reflection, cero dynamic class loading. Profundidad máxima 32 (`kA2UIMaxDepth` L18). Tamaño máximo 256 KB (`kA2UIMaxJsonBytes` L21).
- **G3 Anti-Turing** ✅ — `types/a2ui_node.dart:L20-L34` whitelist es `const Set<String>`, append-only. `_parseNode` recursivo opera sobre estructura sintáctica del JSON; no hay branching sobre contenido del payload. `renderer.dart:L42-L91` es un switch exhaustivo cerrado sobre los 19 tipos + default seguro. Confirmado por header doctrinal del parser L12 "Cero loops/condicionales runtime (anti-Turing)".
- **G4 Renderer correctness** ✅ — `renderer.dart:L42-L93` switch sobre `node.type` con `_buildNode` recursivo pasado como `ChildBuilder`. Default `_UnknownTypePlaceholder` (safety net L93). Mapping completo 19 → 19.
- **G5 Action channel WebSocket protocol** ✅ — `types/a2ui_action.dart:L31-L36` `toJson()` produce literal:
  ```json
  {"type":"a2ui_action","action_id":"...","payload":{...},"source_widget":"...","timestamp":...}
  ```
  Test verifica forma exacta en `action_channel_test.dart:L113-L125`.
- **G6 Action ID uniqueness/payload opcional** ✅ — `actionId` es `String?` opcional en `A2UINode` (L52); `actionPayload` es `Map?` opcional (L55). Parser ignora `action_id` no-string (parser.dart:L150).
- **G7 a2ui_message_view integración + fallback** ✅ — `a2ui_message_view.dart:L40-L62` `tryBuild(payload)` detecta `a2ui_version`, parsea, devuelve `null` si no aplica (legacy), warning banner si hay fallbacks (L83-L107). Test L52-78.
- **G8 message_bubble hook** ✅ — `features/chat/widgets/message_bubble.dart:L497-L507` invoca `A2UIMessageView.tryBuild(payload: message.genuiPayload)` y delega al renderer si no-null. Cero regresión de payloads viejos sin `a2ui_version`.
- **G9 Brand tokens consistencia** ✅ — confirmado §III. Cero hex literal en `core/a2ui/`. Hallazgo lateral: `message_bubble.dart` usa `MonstruoTheme.primary` (no `A2UIBrand`), pero está fuera del subsistema A2UI — es el tema legacy del chat. No es regresión.
- **G10 Naming subsystem** ✅ — confirmado §IV.

---

## §VII — Hallazgos laterales (deuda técnica, mejoras no bloqueantes)

1. **BAJA — `WebSocketA2UIActionSender.connect()` no captura errores de handshake.** `action_channel.dart:L77-L82` hace `WebSocketChannel.connect(Uri.parse(url))` sin try/catch. Si la URL es inválida o el handshake falla, no se reportará via `A2UISendResult`. Mitigación actual: el buffering offline absorbe el peor caso. **Recomendación V1.1:** agregar listener `_channel.stream.listen(..., onError: ...)`.
2. **BAJA — Warning banner en `A2UIMessageView` concatena todos los warnings con `'; '`** (`a2ui_message_view.dart:L57`). Si hay 20 warnings el banner se vuelve ilegible. **Recomendación V1.1:** mostrar primer warning + contador `(+N más)` o truncar.
3. **NOTA — `kA2UIWhitelist` está mencionado en header doctrinal del parser (`parser.dart:L9`) y declarado en `types/a2ui_node.dart:L20`** — solo comentario doctrinal, no duplicación real de código. OK.
4. **NOTA — `_GenUIBubble` legacy fallback (`message_bubble.dart:L519-L549`) sigue presente.** Consistente con G7. No es deuda nueva.
5. **NOTA — `A2UIButtonGroup` filtra silenciosamente hijos no-Button** (`actions.dart:L98`). El spec sugiere "max 4 botones recomendados" pero el código no emite warning si pasan más. Defensivo está bien; doc opcional para V1.1.

---

## §VIII — Hallazgo lateral CI (fuera de scope A2UI)

3 checks rojos en PR #92:
- Lint & Type Check
- Unit Tests
- semgrep

Causa raíz (verificada por Manus previamente): `ModuleNotFoundError: No module named 'sqlglot'` — deuda CI infra del kernel Python (falta `sqlglot` en `requirements-dev.txt` del workflow). Afecta a TODOS los PRs del repo, no solo a este. **NO bloqueante para merge A2UI** — se debe atender en sprint separado de housekeeping CI.

---

## §IX — Recomendación final

**APROBAR MERGE** (con caveat doctrinal documentado, no bloqueante).

**Justificación binaria:**
- 19/19 widgets cumplen W1-W5 = **95/95 cells PASS** (100%)
- 10/10 gates globales G1-G10 PASS
- 51/51 tests claim verificado por conteo de `test(`/`testWidgets(`
- Naming DSC-G-004 limpio (cero archivos prohibidos)
- Anti-injection, anti-Turing, whitelist cerrada, fallback Markdown — todos verificados con evidencia citada
- Protocolo WebSocket exacto al shape firmado, verificado por test directo
- Hook `message_bubble.dart` cero ruptura del flujo legacy
- Brand tokens cumplen spec V1.0; deuda forja es decisión T1 posterior fuera de scope del PR

**Gate restante:** T8 smoke con Alfredo en iPhone físico (último gate del Sprint MOBILE_1B). Tras T8 pass, procede merge bajo regla evolucionada (DSC-G-008 v2 verde + instrucción T1 directa explícita).

**Acciones derivadas post-merge (sprints futuros, NO bloqueantes):**
1. Spec A2UI V1.1 con paleta canónica Apple/Tesla (decisión T1 sobre paleta nueva pendiente).
2. Sprint CI infra: añadir `sqlglot` a `requirements-dev.txt` para desbloquear checks rojos del repo.
3. Patch V1.0.1 opcional: handshake error capture en `WebSocketA2UIActionSender` + truncado de warning banner.

---

## §X — Instrucciones puntuales para Manus si hay fixes

**Vacío — APROBAR MERGE clean.** Los 5 hallazgos del §VII son severidad BAJA o NOTA y se canalizan a sprints futuros (V1.1 + observabilidad WS + UX banner). No requieren cambios en PR #92 antes del merge.

---

## §XI — Falsadores (qué evidencia me haría cambiar el verdict)

- **Si flutter test en iPhone físico (T8) reporta visual broken** o crashes no detectados por tests unitarios → MERGE BLOQUEADO hasta fix.
- **Si Alfredo decide en T8 que la paleta forja en pantalla real es inaceptable** y no quiere mergear con esa deuda visible → MERGE diferido hasta V1.1 con paleta Apple/Tesla aplicada.
- **Si emerge evidencia de regresión** en chat legacy o GenUI legacy via `message_bubble.dart` hook → MERGE BLOQUEADO hasta fix de hook.

---

## §XII — Cierre operativo

Pre-flight Memento ejecutado al inicio: ✅ leídos 3 docs canónicos (`COWORK_BASE_CONOCIMIENTO`, `COWORK_DECISIONES_VIVAS`, `COWORK_AUDIT_FORENSE`) + 4 docs bridge (`a2ui_spec_draft_FIRMADO`, `cowork_to_manus_KICKOFF_MOBILE_1B`, `sprint_MOBILE_1B_A2UI_IMPLEMENTATION`, `cowork_to_manus_PROMPT_AUDIT_APP_FLUTTER_REAL`).

Audit conducido sin `git checkout` (sandbox sin permiso de modificar working tree de Alfredo) — todos los archivos leídos vía `mcp__github-monstruo__get_file_contents` con `ref=sprint/mobile-1b-a2ui-implementation`.

Cowork T2 NO mergeó. Merge pendiente de T1 (Alfredo) tras T8 smoke. PR #92 sigue OPEN.

---

*Audit firmado por Cowork T2 Arquitecto. 2026-05-11. Bajo DSC-G-008 v2 con Gate de Evidencia binario (rúbrica + paths + denominador + falsadores). Sin pseudo-medición salvo emergente de rúbrica binaria. Evidencia citada con path:line. Brand DNA caveat documentado por instrucción T1 explícita derogando forja como canon vigente.*
