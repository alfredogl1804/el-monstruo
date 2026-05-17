---
id: DSC-LF-008
proyecto: LA-FORJA
tipo: contrato_arquitectonico
titulo: "El rendering de markdown del tutor en La Forja se realiza exclusivamente con el componente `Streamdown` (paquete `streamdown@^2.5.0`, Vercel, Apache-2.0). Solo se aplica a mensajes con role='assistant'. Los mensajes role='user' permanecen en `whitespace-pre-wrap` plano sin parseo. Sanitización XSS activa por defecto vía rehype-sanitize + rehype-harden internos del paquete. Aplica forward desde D3.3; sin retroactivos."
estado: en_implementacion (D3.3 — pendiente firma post Cowork audit)
fecha_decision: 2026-05-16 (D3.3 T2)
fecha_implementacion: 2026-05-16 (D3.3 commit pendiente)
fuentes:
  - repo:apps/la-forja/web/src/components/tutor/MessageBubble.tsx (consume `Streamdown` con `data-testid="forja-msg-markdown"`)
  - repo:apps/la-forja/web/src/components/tutor/Chat.test.tsx (mock vi.mock("streamdown") en test layer)
  - repo:apps/la-forja/web/src/app/globals.css (clase `.forja-markdown` con tokens Brand DNA — heading mono uppercase forja-300, code/pre graphite-700, table acero-700)
  - repo:apps/la-forja/web/package.json (dependency `streamdown@^2.5.0`)
  - npm:streamdown@2.5.0 (peer react^18.0.0 || ^19.0.0; license Apache-2.0; mantenedor Vercel)
cruza_con: [DSC-LF-005, DSC-LF-001]
---

# Markdown rendering canónico — Streamdown obligatorio (DSC-LF-008)

## Decisión canónica (texto firmado verbatim)

> **"El rendering de markdown del tutor en La Forja se realiza exclusivamente con el componente `Streamdown` (paquete `streamdown@^2.5.0`, Vercel, Apache-2.0). Solo se aplica a mensajes con `role='assistant'`. Los mensajes `role='user'` permanecen en `whitespace-pre-wrap` plano sin parseo. Sanitización XSS activa por defecto vía `rehype-sanitize` + `rehype-harden` internos del paquete. Aplica forward desde D3.3; sin retroactivos."**

## Stack canónico

| Capa | Versión | Rol |
|---|---|---|
| `streamdown` | ^2.5.0 | Componente React oficial Vercel para markdown streaming-aware. Diseñado específicamente para outputs LLM token-por-token con resilencia a markdown incompleto. |
| `react` / `react-dom` | ^19.2.6 (peer ^18 \|\| ^19) | Host runtime del componente. |
| Tailwind v4 `@theme` | tokens `forja-*`, `graphite-*`, `acero-*` | Brand DNA aplicado vía clase `.forja-markdown` en `globals.css`. |

## Reglas duras

1. **Solo assistant**: el rendering markdown se ejecuta exclusivamente cuando `message.role === "assistant"`. Los mensajes `role="user"` se renderizan con `whitespace-pre-wrap` plano para preservar lo que el usuario escribió sin transformación (incluyendo backticks, markdown crudo o caracteres especiales que no deben interpretarse).

2. **Sanitización por default**: `streamdown` aplica `rehype-sanitize` + `rehype-harden` internamente. **Prohibido** desactivar la sanitización XSS (no se permite `unsafe` ni `disallowed-html`). Si se descubre un caso de markdown legítimo bloqueado por la sanitización, se documenta como Finding y se evalúa allowlist puntual — nunca bypass global.

3. **Wrapper mandatorio `.forja-markdown`**: el `<Streamdown>` siempre se monta dentro de un `<div className="forja-markdown" data-testid="forja-msg-markdown">`. La clase aplica los tokens Brand DNA (mono uppercase headings forja-300, code blocks graphite-700, tablas acero-700, blockquotes border-left forja-600). Esta clase es la única superficie permitida para overrides tipográficos del markdown del tutor.

4. **Cursor blink fuera del Streamdown**: el indicador de streaming (`<span data-testid="forja-msg-cursor">`) se mantiene como sibling del wrapper, nunca dentro del árbol de Streamdown. Esto evita que el componente reinterprete el cursor como contenido markdown y simplifica la lógica de visibilidad (`isStreaming && !isUser`).

5. **Sin reemplazos**: prohibido sustituir `streamdown` por `react-markdown` puro, `markdown-it`, `marked`, `remark` directo o cualquier otro renderer. La elección de `streamdown` es vinculante por su diseño streaming-first y su pareja natural con Vercel AI SDK 6 (DSC-LF-005). Cambios de paquete requieren nueva DSC con audit Cowork.

6. **Mock en test layer**: los tests unitarios (`Chat.test.tsx`, `MessageBubble.test.tsx`) usan `vi.mock("streamdown", () => ({ Streamdown: ({ children }) => children }))` para evitar carga de subdependencias pesadas (rehype, mermaid). El rendering real se valida en e2e/visual y vía `webdev preview` manual antes de cada firma.

## Justificación técnica

- **Streaming-aware**: `streamdown` está diseñado para chunks parciales de markdown (tokens LLM). Renderiza correctamente `\`\`\`tsx\nconst x = ` aún sin cierre, mientras que `react-markdown` puro produce errores de parser o saltos visuales bruscos.

- **Seguridad XSS por default**: `rehype-sanitize` + `rehype-harden` cubren las CVEs comunes de markdown (script injection en images/links, javascript: URIs, on-event handlers en HTML embebido). Esto cumple §1 de las cinco puertas inviolables (DSC-LF-001) sin requerir hardening manual.

- **Vercel-native**: el paquete es mantenido por Vercel, el mismo equipo que el AI SDK 6 (DSC-LF-005). Compatibilidad garantizada con UIMessage parts protocol.

- **Brand DNA preservado**: el wrapper `.forja-markdown` aplica brutalismo industrial (no border-radius romántico, no shadows, mono uppercase para headings, tabla con borders rectos color acero). Cero gradientes, cero emoji por default — Streamdown no inyecta UI propia que viole esto.

## Contrato visual (Brand DNA)

| Elemento markdown | Token aplicado |
|---|---|
| `h1`–`h6` | `font-mono`, `uppercase`, `tracking-[0.15em]`, `color: forja-300` |
| `a` | `color: forja-300`, `underline-offset: 2px`, hover `forja-500` |
| `code` (inline) | `bg: graphite-700`, `font-mono 0.9em`, `radius: var(--radius-forja)` |
| `pre` (block) | `bg: graphite-700`, `border: 1px acero-700`, `radius-forja` |
| `ul/ol` | padding-left 1.4em, sin viñetas decorativas |
| `blockquote` | `border-left: 2px forja-600`, color acero-300 |
| `table` | `border-collapse`, `font-mono 0.9em`; `th` con bg graphite-700 + uppercase forja-300 |
| `hr` | `border-top: 1px acero-700` |

## Pruebas vinculantes

- `apps/la-forja/web/src/components/tutor/Chat.test.tsx` debe contener al menos un test que verifique:
  - `forja-msg-assistant` renderizado con `forja-msg-markdown` wrapper presente
  - `forja-msg-user` SIN wrapper markdown (texto plano `whitespace-pre-wrap`)
  - Cursor blink (`forja-msg-cursor`) solo visible en último mensaje assistant + streaming activo

## Cláusula de revisión

Esta DSC se revisa cuando:
- `streamdown` publique major version (3.x.0) — evaluar breaking changes en sanitización o API.
- `Streamdown` deje de mantenerse o cambie de licencia.
- Se descubra una CVE en `streamdown` o sus subdeps (`rehype-sanitize`, `rehype-harden`, `mermaid`).
- El rol del tutor incluya outputs no-markdown (ej. componentes interactivos, formularios) — requiere extensión, no reemplazo.

## Cierre

DSC-LF-008 firma forward desde D3.3 (commit pendiente). El contract test
visual + los 11 tests de `Chat.test.tsx` + los 6 tests de `preferences.test.ts`
constituyen la frontera de validación binaria. Cualquier regresión que rompa
el wrapper `.forja-markdown`, la sanitización XSS, o el dual-mode (assistant
markdown vs user plano) bloquea merge a `main`.
