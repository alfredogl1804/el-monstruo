# `packages/` — Cimientos compartibles del Monstruo

> Esta carpeta contiene packages reutilizables que cualquier proyecto-hijo del Monstruo (CIP, Marketplace Interiorismo, Roche Bobois, Vivir Sano, Command Center, Mundo Tata, Bot Telegram, futuras empresas-hijas) puede importar para nacer **on-brand desde el día 1**.

---

## Filosofía

> Antes existían 20 paletas divergentes, 8 implementaciones distintas de auth y N tipos de plantilla de proyecto. Esta carpeta es la respuesta. **Source of truth única, espejos compilados, naming canónico inviolable.**

DSCs aplicables: **DSC-G-004** (Brand Engine), **DSC-X-003** (Manus-Oauth), **DSC-G-007.1** (4 Catastros).

---

## Packages

| Package | Versión | Estado | Owner |
|---|---|---|---|
| **`@monstruo/design-tokens`** | `0.1.0` | ✅ FIRMADO | Hilo Catastro |
| `@monstruo/auth-ui` | _pendiente_ | 🟡 ROADMAP | — |
| `@monstruo/forja-ui` | _pendiente_ | 🟡 ROADMAP | — |
| `@monstruo/observability-client` | _pendiente_ | 🟡 ROADMAP | — |

### `@monstruo/design-tokens` 

Tokens canónicos en TS/CSS/Tailwind/Flutter. Espejo compilado de `kernel/brand/brand_dna.py`. Paleta forja+graphite+acero. Cualquier proyecto del portfolio importa de aquí.

- README: `packages/design-tokens/README.md`
- Paleta visual: `packages/design-tokens/docs/PALETA.md`
- Test de paridad: `packages/design-tokens/tests/parity_with_brand_dna.test.js` (8/8 verde)

### `@monstruo/auth-ui` (ROADMAP)

Componentes UI de auth listos: `<SignInWithManusButton />`, `<UserAvatar />`, `<SessionExpiredModal />`. Importa de `@monstruo/design-tokens` para identidad. Por ahora estos componentes viven en `skills/manus-oauth-pattern/templates/` como referencia.

### `@monstruo/forja-ui` (ROADMAP)

Sistema de componentes UI con identidad forja. Botones, inputs, cards, modals. NO es shadcn/Material/Mantine — es nuestro. Cuando se haga, importará de `@monstruo/design-tokens`.

### `@monstruo/observability-client` (ROADMAP)

Cliente unificado para emitir eventos al Command Center. Logging on-brand (`{modulo}_{action}_{result}`), métricas, traces. Wrap sobre Sentry/OpenTelemetry pero con identidad del Monstruo.

---

## Cómo agregar un package nuevo

1. Crear directorio en `packages/{nombre}/`
2. `package.json` con `name: "@monstruo/{nombre}"`, `monstruo: { ...metadata }`, fields canónicos
3. README con propósito + uso + cross-links
4. Tests que verifiquen identidad de marca (no solo tests funcionales)
5. Actualizar este README global

---

## Cross-links

- `kernel/brand/brand_dna.py` — source of truth de identidad visual
- `skills/manus-oauth-pattern/` — patrón canónico de auth (consume design-tokens)
- `docs/templates/biblia-master-plan-template.md` — biblia canónica de proyectos-hijo
- `docs/BRAND_ENGINE_ESTRATEGIA.md` — estrategia de Brand Engine
- DSC-G-004, DSC-X-003, DSC-G-007.1 — restricciones que rigen estos packages

---

— Hilo Catastro, Sprint Catastro-B 2026-05-06
