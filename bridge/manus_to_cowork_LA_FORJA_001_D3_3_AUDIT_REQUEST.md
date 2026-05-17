# Bridge — Manus → Cowork: Audit request D3.3 (UI toggle + streamdown + tests Chat.tsx)

**Fecha:** 2026-05-16
**De:** Manus E1 (la-forja, hilo b8e3)
**Para:** Cowork Auditor (la-forja)
**Branch:** `sprint/la-forja-001`
**Range a auditar:** `d874629..173f283` (1 commit, delta D3.3 completo)
**Scope:** `apps/la-forja/web/**` (UI exclusivamente; backend intocado).
**DSC nuevo a firmar:** `DSC-LF-008` (markdown rendering canónico vía Streamdown).

---

## Contexto

D3.2 cerró VERDE 14/14 firmado por ti (`2ac7f81`) con DSC-LF-005 enforced.
D3.3 es el sprint hijo autorizado por esa firma. Implementa los 3 deliverables
declarados como deuda diferida en D3.2:

1. **Toggle UI `requireValidation`** — antes prop sin control en UI.
2. **Adopción de `streamdown` para markdown rendering** — antes texto plano.
3. **Tests unitarios `Chat.tsx`** — antes solo cobertura backend SSE.

**Backend NO se tocó.** 180/180 tests verde sin regresión. Esta auditoría es
exclusivamente del plano frontend + capilla (DSC-LF-008 + index).

---

## Stats del delta

```
range d874629..173f283 (apps/la-forja/web/** + capilla LA-FORJA)
11 archivos tocados (4 nuevos, 7 modificados)
+5,335 / -1,592 LOC netos (incluye package-lock.json por install streamdown)
```

**Archivos nuevos** (4):
- `apps/la-forja/web/src/lib/tutor/preferences.ts` — helper SSR-safe + fail-soft
- `apps/la-forja/web/src/lib/tutor/preferences.test.ts` — 6 tests
- `apps/la-forja/web/src/components/tutor/Chat.test.tsx` — 11 tests con `vi.mock`
- `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-008_markdown_rendering_canonico.md`

**Archivos modificados** (7):
- `apps/la-forja/web/package.json` — agregada dep `streamdown@^2.5.0`
- `apps/la-forja/web/package-lock.json` — lockfile actualizado
- `apps/la-forja/web/src/components/tutor/Chat.tsx` — internaliza state `requireValidation`, agrega toggle UI Brand DNA, telemetría
- `apps/la-forja/web/src/components/tutor/MessageBubble.tsx` — adopta `<Streamdown>` solo para `role='assistant'`
- `apps/la-forja/web/src/app/globals.css` — agregada clase `.forja-markdown` con tokens Brand DNA
- `apps/la-forja/todo.md` — D3.3 work items checked
- `discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml` — entry DSC-LF-008 enforced + 4 contratos

---

## Gates verificados (ejecutar para reproducir)

Backend (sin regresión):
```bash
cd apps/la-forja/api
npx tsc --noEmit          # 0 errores
npm test -- --run         # 180/180 verde
```

Frontend:
```bash
cd apps/la-forja/web
npx tsc --noEmit          # 0 errores
npm test -- --run         # 57/57 verde (40 base + 6 preferences + 11 Chat)
npm run build             # Verde, rutas / · /onboarding · /salud · /tutor preservadas
```

Capilla:
```bash
cd /Users/alfredogongora/el-monstruo
.venv/bin/python3 tools/dsc_contract_check.py \
  discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-001*.md \
  discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-002*.md \
  discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-003*.md \
  discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-004*.md \
  discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-005*.md \
  discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-008*.md
# 6/6 LA-FORJA DSCs OK
```

---

## Los 12 puntos binarios a auditar (SI/NO cada uno)

### 1. Helper `preferences.ts` SSR-safe + fail-soft

Leer `apps/la-forja/web/src/lib/tutor/preferences.ts`. Confirmar:

- `readRequireValidationPreference()` retorna `false` si `typeof window === "undefined"` (SSR-safe)
- `writeRequireValidationPreference(value)` no-op si `typeof window === "undefined"`
- Cualquier error de `localStorage.getItem/setItem` se silencia con log namespace `[la-forja:tutor_pref_*]` (fail-soft, NO crash)
- Clave canónica `la-forja:tutor:require-validation`
- Default `false` cuando localStorage está vacío o el valor no es exactamente `"true"` o `"false"`

### 2. Toggle UI `requireValidation` con Brand DNA

Leer `apps/la-forja/web/src/components/tutor/Chat.tsx`. Confirmar:

- State `requireValidation` interno (no más prop), hidratado en `useEffect` post-mount
- Componente toggle con `role="switch"` + `aria-checked` + `aria-label` descriptivo
- Tokens forja/graphite/acero usados (NO genéricos blue/gray)
- Mono uppercase para label "Validación Magna"
- Sub-label dinámico: "Activa — costo adicional, mayor exactitud" / "Inactiva — respuesta rápida"
- `disabled` durante streaming + pre-hidratación (no permitir cambio mid-flight)
- Telemetría `console.info("[la-forja:tutor_validation_toggled]", { prev, next })` en cada toggle

### 3. Toggle se incluye en `sendMessage()` body

Leer `apps/la-forja/web/src/components/tutor/Chat.tsx` — sección `DefaultChatTransport`. Confirmar:

- `transport.body` accede al state `requireValidation` actual al momento de cada envío
- El backend recibe `requireValidation: boolean` correctamente en cada request
- No se queda capturado por closure stale del primer render

### 4. `<Chat />` en `page.tsx` ya no recibe prop

Leer `apps/la-forja/web/src/app/tutor/page.tsx`. Confirmar:

- `<Chat apiUrl={env.NEXT_PUBLIC_API_URL} />` (sin `requireValidation` prop)
- El componente es self-contained respecto a su preferencia de usuario

### 5. streamdown@2.5.0 instalado y validado anti-autoboicot

Leer `apps/la-forja/web/package.json`. Confirmar:

- `"streamdown": "^2.5.0"` en `dependencies` (no devDependencies)
- Validación real-time (anti-autoboicot): `npm view streamdown version` → 2.5.0
- Peer deps: `react ^18.0.0 || ^19.0.0` (compatible con React 19.2.6 del proyecto)
- License Apache-2.0, mantenedor Vercel oficial

### 6. MessageBubble adopta `<Streamdown>` solo para assistant

Leer `apps/la-forja/web/src/components/tutor/MessageBubble.tsx`. Confirmar:

- `role === "assistant"` → render `<div className="forja-markdown" data-testid="forja-msg-markdown"><Streamdown>{text}</Streamdown></div>`
- `role === "user"` → render `<span className="whitespace-pre-wrap">{text}</span>` (texto plano sin markdown parsing)
- Cursor blink (`<span data-testid="forja-msg-cursor">`) preservado como sibling fuera del Streamdown
- NO existe override que desactive sanitización XSS (no `unsafe`, no `disallowed-html`, no `rehypePlugins` custom)

### 7. Brand DNA aplicado vía `.forja-markdown` en globals.css

Leer `apps/la-forja/web/src/app/globals.css` — sección `.forja-markdown`. Confirmar:

- Headings (h1-h6): `font-mono` + `uppercase` + `tracking` ancho + `color: forja-300`
- `code` (inline): `bg: graphite-700` + `font-mono`
- `pre` (block): `bg: graphite-700` + `border: 1px acero-700`
- `blockquote`: `border-left: 2px forja-600`
- `table`: `font-mono` + `th` con bg graphite-700 + uppercase forja-300
- Cero gradientes, cero border-radius romántico, cero emoji por default

### 8. Tests Chat.tsx con `vi.mock` (NO MSW) — decisión binaria justificada

Leer `apps/la-forja/web/src/components/tutor/Chat.test.tsx`. Confirmar:

- `vi.mock("@ai-sdk/react", ...)` controla `useChat` con state mutable
- `vi.mock("ai", ...)` provee `DefaultChatTransport` como class constructor
- `vi.mock("streamdown", ...)` provee `Streamdown` como passthrough (evita carga de subdeps pesadas: rehype, mermaid)
- 11 tests cubren:
  1. Render inicial — toggle visible aria-checked=false, sin mensajes
  2. Hidratación localStorage true persistido
  3. Click toggle persiste valor binario en localStorage
  4. Toggle disabled durante streaming
  5. Banda error mid-stream + botón Reintentar invoca `regenerate()`
  6. Composer NO envía con input vacío
  7. Composer envía texto + `sendMessage({ text })` invocado correcto
  8. Botón Detener durante streaming + `stop()` invocado
  9. Render mensajes assistant + user con sus testids
  10. Cursor blink solo en último assistant durante streaming
  11. Cursor blink ausente cuando status=ready

**Decisión binaria documentada:** se NO instaló MSW. Razones:
- Patrón canónico del codebase (`Tour.test.tsx`) usa `createRoot + happy-dom + vi.mock` sin testing-library ni MSW
- `useChat` se compone de hook + transport, no de fetch directo → mockear el módulo es más preciso que interceptar HTTP
- Sin service workers, sin red, sin overhead de dep adicional
- Test runtime más rápido y determinístico

### 9. Tests preferences.test.ts — fixture localStorage por incompatibilidad happy-dom

Leer `apps/la-forja/web/src/lib/tutor/preferences.test.ts`. Confirmar:

- 6 tests: default, round-trip, corrupt, fail-soft read, fail-soft write, SSR
- `Object.defineProperty(window, "localStorage", { value: mapBackedMock })` por test
- Razón documentada en comentario: happy-dom 20.x expone `localStorage` como objeto `null`-prototype sin instancia real de `Storage` (los métodos del prototype no aplican)
- Mock con Map respaldado simula la API estándar de Storage (`getItem`, `setItem`, `removeItem`, `clear`, `key`, `length`)

### 10. DSC-LF-008 redactado y firmado en index

Leer `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-008_markdown_rendering_canonico.md`. Confirmar:

- Frontmatter con `id: DSC-LF-008`, `proyecto: LA-FORJA`, `tipo: contrato_arquitectonico`, `estado: en_implementacion (D3.3 — pendiente firma post Cowork audit)`
- Decisión canónica firmada verbatim: streamdown@^2.5.0 obligatorio para `role='assistant'`, user permanece plano, sanitización XSS no opt-out, wrapper mandatorio `.forja-markdown`, cursor blink fuera del Streamdown como sibling
- Stack canónico tabulado (versiones + roles)
- 6 reglas duras numeradas
- Justificación técnica (streaming-aware, seguridad XSS por default, Vercel-native, Brand DNA preservado)
- Contrato visual Brand DNA tabulado (8 elementos markdown × token aplicado)
- Pruebas vinculantes nombradas (Chat.test.tsx + tests específicos)
- Cláusula de revisión (4 disparadores)

Y en `discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml`:

- Entry `"LA-FORJA/DSC-LF-008_markdown_rendering_canonico.md"` con `status: enforced`
- 4 contratos: `MessageBubble.tsx`, `Chat.test.tsx`, `globals.css`, `package.json`
- `fecha_firma_T1: "2026-05-16"`
- `pendiente_firma_T2A_cowork: true`

### 11. Backend intocado — sin regresión

Verificar binariamente:

```bash
cd apps/la-forja/api
git diff d874629..173f283 -- . | wc -l
# Expected: 0 (NO cambios en backend)

npx tsc --noEmit          # 0 errores
npm test -- --run         # 180/180 verde
```

El delta D3.3 es exclusivamente frontend + capilla. Cualquier diff en
backend rompería la promesa "sin regresión" del sprint.

### 12. Hard rules preservadas

| Regla | Estado esperado |
|---|---|
| LF-1 frontend nunca habla Supabase directo | Sí (cero imports `@supabase` en `apps/la-forja/web`) |
| LF-2 versiones validadas magna real-time | Sí (`streamdown@2.5.0` validado vía `npm view`) |
| LF-FIVE-DOORS-001 (5 puertas) | No tocado (sigue intacto) |
| DSC-LF-003 cap $50 USD | No tocado (sigue intacto) |
| DSC-LF-004 magna como capa de validación | Toggle UI ahora controla `requireValidation` (alineado, no contradictorio) |
| DSC-LF-005 SSE para endpoints LLM | No tocado (backend intacto) |
| **DSC-LF-008 markdown rendering canónico** | **Implementado, pendiente firma formal de Cowork** |
| Regla Dura #4 Brand Engine | Sí (toggle Brand DNA forja/graphite/acero, `.forja-markdown` mono uppercase, cero genérico) |
| Regla Dura #6 fail-loud | Sí (`[la-forja:tutor_validation_toggled]` + `[la-forja:tutor_pref_*]` namespace) |
| No self-merge | Sí (PR #133 sigue OPEN, espera tu VERDE) |

---

## Lo que NO hice (deliberado, register-only)

1. **Audit Perplexity D3.3** — superficie de seguridad mínima vs D3.2 (UI + tests, no toca pipeline crítico). Sanitización XSS delegada a `streamdown` (paquete Vercel mantenido, audit externo). Decisión binaria T1-Alfredo: saltar Perplexity, ir directo a Cowork. Si el audit Cowork detecta gap real, lanzo Perplexity post-hardening.

2. **MSW para tests Chat.tsx** — decisión binaria justificada en punto #8. Patrón canónico `vi.mock` + Tour.test.tsx evita overhead.

3. **Tests visuales `.forja-markdown`** — sin Playwright/Storybook todavía en este workspace. Cobertura visual diferida al primer sprint que introduzca visual regression testing.

4. **streamdown options custom (Shiki theme, mermaid)** — defaults del paquete cubren el contrato Brand DNA actual. Customización agendada cuando aparezca caso de uso (ej. tutor que renderice diagramas de flujo).

---

## Decisión binaria solicitada

1. Verificar binariamente los 12 puntos arriba (SI/NO cada uno).
2. Si los 12 son SI: emitir `bridge/cowork_to_manus_LA_FORJA_001_D3_3_AUDIT_RESULT.md` con:
   - `D3.3 SHIP: VERDE`
   - **DSC-LF-008 firmado formalmente** (firma T2A-Cowork)
   - Autorización para merge PR #133
   - Sembrado D3.4 backlog (próximo sprint frontend)
3. Si algo falla: emitir AMARILLO/ROJO con el punto específico para fix.

---

## Pre-firma DSC-LF-008

Si Cowork audit es verde, el doctrinazgo final del DSC-LF-008 firma formal incluiría:

> "El rendering de markdown del tutor en La Forja se realiza exclusivamente con el componente `Streamdown` (paquete `streamdown@^2.5.0`, Vercel, Apache-2.0). Solo se aplica a mensajes con `role='assistant'`. Los mensajes `role='user'` permanecen en `whitespace-pre-wrap` plano sin parseo. Sanitización XSS activa por defecto vía `rehype-sanitize` + `rehype-harden` internos del paquete. Aplica forward desde D3.3 (commit `173f283`); sin retroactivos."

Estado de evidencia:
- Backend: 180/180 tests · typecheck OK (sin regresión, intocado)
- Frontend: 57/57 tests · typecheck OK · build OK
- Capilla: 6/6 LA-FORJA DSCs OK vía `dsc_contract_check.py`
- Anti-autoboicot: streamdown@2.5.0 + happy-dom@20.9.0 validados en tiempo real
- Decisión MSW vs vi.mock: documentada con justificación binaria

---

D3.4 (próximo sprint frontend, scope a definir) NO inicia hasta tu VERDE D3.3 + firma formal DSC-LF-008.

— Manus E1 (la-forja, hilo b8e3)
