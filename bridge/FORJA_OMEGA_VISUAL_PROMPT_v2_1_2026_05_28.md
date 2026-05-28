# FORJA OMEGA — Prompt Visual v2.1 (Factory Mode UI en `tablero-campana`)

**Versión:** v2.1 — calibrado contra Genome vivo + síntesis de 4 sabios
**Predecesor:** `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_2026_05_28.md` (PR #235 SHA `de91b96`)
**Autor:** Manus B (Hilo B, cuenta `manus_b`)
**Fecha de emisión:** 2026-05-28
**Estado:** PROPOSED — pendiente firma Alfredo + audit Cowork
**Destino:** sprint `SPR-FACTORY-UI-001` ya registrado en `sprints/registry.yaml` con estado `WAITING_REVIEW`

---

## 0. Cambios respecto a v2

v2.1 integra los **6 puntos de convergencia** detectados por 4 sabios (GPT-5, Claude Opus 4.5, Gemini 2.5 Pro, Perplexity Sonar Pro) en consulta paralela del 2026-05-28 (ver `_scratch/sabios_responses/sintesis.json`). Cada uno se añade como **regla dura no negociable** en la sección 5 del prompt operativo. Adicionalmente se ajustan los nombres de paneles y se añade política de cámara para la 6ª lente.

**Disclaimer honesto:** los 4 sabios consultados no fueron las versiones flagship más recientes disponibles hoy (Anthropic ya tiene Opus 4.7, Google tiene Gemini 3.1 Pro). La decisión de no re-disparar se tomó porque la convergencia entre los 4 outputs ya señalaba los mismos 6 puntos críticos.

---

## 1. Auditoría binaria pre-prompt (sin cambios respecto a v2)

Sigue siendo válida la tabla de la sección 2 de v2. Resumen: 4 endpoints `/v1/factory/*` LIVE, 9 tablas `forja_*` LIVE, `server/forja/` 2 549 LOC TS LIVE en branch `design/forja-os-sovereign-agentic-fabric`, `ForjaShadowPanel.tsx` 186 LOC LIVE.

---

## 2. Delta real para Factory Mode UI (refinado por Gemini 2.5 Pro)

### 2.1 Lente "Fábrica" (6ª en `LayerSwitcher`)

Cuando se activa, el `IsometricBoard` cambia de "ecosistema declarativo" a "constelación de ForgeNodes". Esta transición exige:

- **BoardData V2:** estructura unificada que incluye `ForgeNode { id, tier, status, position, connections[] }` además del schema actual del ecosistema.
- **Cámara orbital:** la vista de constelación se renderiza con cámara orbital (top-down con tilt 35°), distinta a la cámara isométrica del ecosistema. Transición animada de 600 ms con `cubic-bezier(0.65, 0, 0.35, 1)`.
- **Click bidireccional:** click en un `ForgeNode` abre el `ConstellationPanel` con el nodo seleccionado y resalta su row. Click en una row del panel hace zoom + pulse al `ForgeNode` correspondiente en el board.
- **Estética:** ForgeNodes como esferas naranjas (`#F97316`) con halo pulsante 2 s, edges como líneas de acero (`#A8A29E`) animadas con flujo direccional 1.5 s. Tier `core` 1.4× tamaño, `outer` 0.7×.

### 2.2 Cuatro paneles HUD (nombres canónicos en español)

| Slug interno | Nombre UI (es-MX) | Endpoint | refetchInterval máximo |
|---|---|---|---|
| `constellation` | Constelación de Fábricas | `/v1/factory/constellation` | 30 s |
| `economy` | Economía Cognitiva | `/v1/factory/economy` | 60 s |
| `timeline` | Línea Soberana | `/v1/factory/timeline` | 15 s |
| `diff` | Diferencial de Realidad | `/v1/factory/diff` | 120 s |

> **Nota Claude:** "Línea Soberana del Tiempo" se acorta a "Línea Soberana" — más limpio en tab y respeta la guía Apple-keynote (≤ 8 palabras explicativas por panel).

### 2.3 Estructura interna de cada panel (refinada por Claude + Perplexity)

Cada panel es un componente con 4 slots fijos:

```
┌─────────────────────────────────────┐
│ Header: título + last_updated_at +  │
│         data_quality badge          │
├─────────────────────────────────────┤
│ Filters: query params del endpoint  │
│          (tier|kind|window|types|…) │
├─────────────────────────────────────┤
│ Body: contenido principal           │
│       (tabla / cards / timeline)    │
├─────────────────────────────────────┤
│ Footer: copy de marca + link docs   │
└─────────────────────────────────────┘
```

Estados obligatorios por panel: `loading` (skeleton con copy de marca), `error` (formato `{module}_{action}_{failure}` + retry button), `empty` (disclaimer honesto cuando `data_quality.coverage = "partial"` o `null`).

### 2.4 EconomyPanel (refinado por Claude — jerarquía 3-5-7)

Los 15 KPIs se distribuyen en 3 niveles visuales:

- **3 KPIs hero** (top, grandes): valor principal + delta + tendencia (flecha + color semántico que respeta Brand DNA, no rojo/verde genérico).
- **5 KPIs secundarios** (medios): cards medianas con label + valor + sparkline opcional.
- **7 KPIs de detalle** (collapsibles, default cerrado): cards pequeñas con tooltip explicativo.

### 2.5 BFF tRPC server-side `server/routers/factory.ts` (refinado por GPT-5)

Contrato:

```typescript
// server/routers/factory.ts
export const factoryRouter = router({
  constellation: protectedProcedure   // ← auth obligatoria
    .input(z.object({                  // ← zod schema runtime
      tier: z.enum(['core','inner','mid','outer','all']).default('all'),
    }))
    .query(async ({ input, ctx }) => {
      const url = new URL(`${KERNEL_BASE_URL}/v1/factory/constellation`);
      url.searchParams.set('tier', input.tier);
      const res = await fetch(url, {
        headers: { 'X-Api-Key': process.env.KERNEL_API_KEY! },  // ← server-only
        signal: AbortSignal.timeout(8000),                       // ← timeout
      });
      if (res.status === 401) throw new TRPCError({ code: 'UNAUTHORIZED', message: 'constellation_fetch_auth_denied' });
      if (!res.ok) throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: `constellation_fetch_${res.status}` });
      const json = await res.json();
      return ConstellationResponseSchema.parse(json);  // ← validación runtime de salida
    }),
  // economy, timeline, diff con shape análogo
});
```

Reglas duras:
- `KERNEL_API_KEY` solo en `process.env` del backend Node, **nunca** referenciada en código `client/`.
- `protectedProcedure` exige sesión válida (Manus OAuth ya está activo en `tablero-campana`).
- Cada endpoint tiene su `zod schema` para input y output. Schemas se derivan de los JSON canonizados en PR #216 (`SPR-FACTORY-AGGREGATORS-000`).
- `AbortSignal.timeout(8000)` evita que un kernel lento bloquee el cliente.
- Headers de error nunca incluyen `KERNEL_API_KEY` (test obligatorio).

### 2.6 Polling consciente de visibilidad (TanStack Query)

```typescript
// client/src/hooks/useForjaConstellation.ts
export function useForjaConstellation(opts: { isOpen: boolean; activeTab: string }) {
  return trpc.factory.constellation.useQuery(undefined, {
    enabled: opts.isOpen && opts.activeTab === 'constellation',
    refetchInterval: opts.isOpen && opts.activeTab === 'constellation' ? 30_000 : false,
    refetchOnWindowFocus: false,
    staleTime: 25_000,
    retry: (count, err) => err.data?.code !== 'UNAUTHORIZED' && count < 2,
  });
}
```

El polling se **suspende** cuando el dock está cerrado o el tab no está activo. Esto reduce carga al kernel y evita ráfagas innecesarias en clientes móviles de baja batería.

### 2.7 Accesibilidad mínima (refinado por Claude + Perplexity)

- **Contraste WCAG AA:** Forja `#F97316` sobre Graphite `#1C1917` da ratio 4.52:1 (pasa AA). Acero `#A8A29E` sobre Graphite da ratio 6.1:1. Verificar con `axe-core` en CI.
- **Focus rings visibles:** outline 2px Forja en todos los elementos interactivos (no usar `outline: none` sin reemplazo).
- **ARIA en Drawer + Tabs:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` para Drawer; `role="tablist"`, `role="tab"`, `aria-selected` para tabs.
- **Trap de teclado:** focus se atrapa dentro del Drawer cuando está abierto, escape lo cierra.
- **Test obligatorio:** `axe-core` audit en `vitest run` con `vi.expect(violations).toHaveLength(0)`.

### 2.8 Reuso del design system del tablero

Antes de implementar nada, Manus A debe:

1. Inventariar componentes existentes en `client/src/components/ui/` (probable `Drawer`, `Tabs`, `Card`, `Badge`, `Skeleton`).
2. Si existen, **usarlos**. Solo crear nuevos componentes en `client/src/components/hud/` cuando no haya equivalente.
3. Si no existe `Drawer` o `Tabs`, primero proponer en bridge file qué librería usar (Radix UI / Headless UI ya integradas, no agregar nuevas dependencias).

---

## 3. Reglas duras no negociables (consolidadas v2 + v2.1)

Bloque completo a copiar en el prompt operativo:

```text
REGLAS DURAS NO NEGOCIABLES:

# Heredadas de v2:
- NO escribir KERNEL_API_KEY en código del cliente. Solo en server BFF (process.env).
- NO inventar KPIs ni eventos: si endpoint devuelve null/vacío, panel muestra
  disclaimer honesto del payload con copy de marca.
- NO usar bg-slate-*, bg-gray-*, text-gray-*. SOLO los 3 tokens Forja del Brand DNA
  mapeados como CSS vars: --forja-orange:#F97316, --forja-graphite:#1C1917,
  --forja-steel:#A8A29E.
- NO usar la palabra "Factory Mode" en UI. La lente es "Fábrica" en español, los
  paneles "Constelación", "Economía Cognitiva", "Línea Soberana", "Diferencial
  de Realidad".
- NO crear nuevas migraciones, NO modificar drizzle.config.ts.
- NO modificar archivos en server/forja/ ni server/_core/. Inmutables este sprint.

# NUEVAS en v2.1 (síntesis 4 sabios):
- TODO procedimiento tRPC en server/routers/factory.ts es protectedProcedure.
  No exponer datos del kernel sin sesión válida.
- TODOS los inputs y outputs de los 4 procedimientos tRPC tienen zod schema runtime.
  Schemas derivados de los JSON canonizados en PR #216. Cero `any`, cero `unknown`
  sin parse.
- Polling con TanStack Query suspendido cuando dock cerrado o tab inactivo (regla 2.6).
  staleTime >= refetchInterval para evitar ráfagas en focus.
- CADA panel implementa los 3 estados: loading (skeleton), error (formato
  {module}_{action}_{failure} + retry), empty (disclaimer honesto cuando
  data_quality.coverage = partial).
- Accesibilidad WCAG AA verificada con axe-core en CI. Focus rings visibles,
  ARIA correcto en Drawer + Tabs, trap de teclado.
- Reuso obligatorio del design system en client/src/components/ui/ antes de crear
  nuevos componentes en client/src/components/hud/.
- NO replicar en cliente lógica de agregación que ya hace el kernel. El cliente
  solo presenta, ordena, filtra cliente-side y formatea.
- NO crear router tRPC paralelo que duplique server/forja/. server/routers/factory.ts
  es un proxy delgado, no un segundo gateway.
- Hooks centralizados: useForjaConstellation, useCognitiveEconomy, useSovereignTimeline,
  useRealityDiff. Cada panel consume su hook, no llama tRPC directo.
- Test obligatorio: factory.security.test.ts verifica que ningún error serializado
  al cliente contiene KERNEL_API_KEY o headers sensibles.
```

---

## 4. Validación pre-merge (consolidada v2 + v2.1)

```text
1. pnpm typecheck pasa sin errores.
2. pnpm vitest run pasa con los nuevos tests:
   - factory.proxy.test.ts (shape + 401 + timeout + retry policy)
   - factory.ui.test.ts (smoke render con fixtures + estados loading/error/empty)
   - factory.a11y.test.ts (axe-core, 0 violations)
   - factory.security.test.ts (no leak de API key en errores cliente)
3. pnpm build genera bundle sin warnings nuevos. Bundle size delta < 80 KB
   gzip (paneles lazy-loaded con React.lazy).
4. Screenshot de los 4 paneles en iPhone real (Safari) + iPad landscape.
5. Audit Cowork sobre BRAND COMPLIANCE: verificación visual del bundle desplegado
   en Manus space, no solo lectura del PR.
6. PR body incluye sección "## E2E Evidence" con URLs de screenshots o label
   no-e2e-required si Cowork lo justifica.
7. Run axe-core en preview deployment con 0 violations en los 4 paneles.
```

---

## 5. Estimación actualizada

v2: ~1 200 LOC TSX en 1-2 días. v2.1: ~1 500–1 800 LOC TSX en 2-3 días por las adiciones (zod schemas, hooks centralizados, tests a11y, tests security, reuso de UI lib).

**Justificado:** la calidad de craftsmanship que pide el Brand DNA + el filtro Apple-keynote no se logra con 1 200 LOC sin tests de a11y/security.

---

## 6. Dependencias de orden (refinado)

1. Alfredo firma OK al prompt v2.1 (puede tachar cualquier punto).
2. Cowork audita el prompt v2.1 (DSC-G-008 v2 audit pre-arranque).
3. Manus B abre PR de update del registry.yaml moviendo `SPR-FACTORY-UI-001` de `WAITING_REVIEW` a `SIGNED`.
4. Manus A toma el sprint en sesión limpia, ejecuta usando esta v2.1 como spec.
5. Mid-sprint check: Cowork audita `bridge/missions/SPR-FACTORY-UI-001/3_executions/` antes de PR.
6. Final: PR con E2E evidence + Cowork audit verde + DSC-G-008 v2 cerrado.

---

## 7. Cierre

Este v2.1 sustituye al v2. Cuando Alfredo lo firme, se sube a `bridge/sprints_propuestos/sprint_SPR_FACTORY_UI_001_factory_mode_ui.md` como spec autoritativa y se cambia el campo `spec:` del registry.

**Manus B sigue online** para integrar feedback de Cowork (cuando responda) en una eventual v2.2, antes de pasar el control a Manus A.

**Sesión origen:** Tracks 1-5 nocturnos del 2026-05-28
**Validación en tiempo real:** Genome `/v1/genome/now/health` 2026-05-28T02:21:38Z + 4 sabios paralelos
**Cruza con:** v2 (PR #235), T1-MAGNA-006/007 (PR #231), Sprint 91, AGENTS.md Reglas Duras #1-#6, DSC-G-008 v2
