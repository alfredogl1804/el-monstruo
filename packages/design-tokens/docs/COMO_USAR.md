# Cómo usar `@monstruo/design-tokens` en un proyecto-hijo

> Guía paso a paso por stack. Si tu stack no está aquí, agregá un PR con la integración.

---

## Quickstart por stack

### Next.js 15+ (App Router) con Tailwind v4

```bash
pnpm add @monstruo/design-tokens
```

En tu `app/globals.css`:

```css
@import "tailwindcss";
@import "@monstruo/design-tokens/tailwind/theme";
@import "@monstruo/design-tokens/css";
```

En tu componente:

```tsx
export default function CTA() {
  return (
    <button className="bg-forja-500 text-graphite-800 font-display px-6 py-4 rounded-md shadow-brasa">
      Forjá tu producto
    </button>
  );
}
```

### Vite + React + Tailwind v4

```bash
pnpm add -D @monstruo/design-tokens
```

En tu CSS principal:

```css
@import "tailwindcss";
@import "@monstruo/design-tokens/tailwind/theme";
```

### Vite + React + Tailwind v3 (legacy)

```bash
pnpm add -D @monstruo/design-tokens
```

`tailwind.config.js`:

```js
module.exports = {
  presets: [require("@monstruo/design-tokens/tailwind/preset")],
  content: ["./src/**/*.{ts,tsx,html}"],
};
```

### React/Vue/Angular sin Tailwind (CSS variables)

```bash
pnpm add @monstruo/design-tokens
```

En tu CSS principal:

```css
@import "@monstruo/design-tokens/css";
```

Después usás:

```css
.cta {
  background-color: var(--color-forja-500);
  color: var(--color-text-on-forja);
  font-family: var(--font-family-display);
  font-weight: var(--font-weight-bold);
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-brasa);
}
```

### React/JS programático (sin CSS)

```tsx
import { forja, graphite, spacing, radius, textStyle } from "@monstruo/design-tokens";

const ctaStyle = {
  backgroundColor: forja[500],
  color: graphite[800],
  padding: `${spacing[3]} ${spacing[6]}`,
  borderRadius: radius.md,
  ...textStyle.cta,
};

export const CTA = () => <button style={ctaStyle}>Forjá tu producto</button>;
```

### Flutter / Dart

Copiar `packages/design-tokens/flutter/monstruo_tokens.dart` a `lib/tokens/` de tu app Flutter (no hay package npm equivalente — Flutter usa pub.dev, integración pendiente).

```dart
import 'package:el_monstruo/tokens/monstruo_tokens.dart';

ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: MonstruoTokens.forja[500],
    foregroundColor: MonstruoTokens.textOnForja,
    padding: EdgeInsets.symmetric(
      horizontal: MonstruoTokens.space6,
      vertical: MonstruoTokens.space3,
    ),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(MonstruoTokens.radiusMd),
    ),
  ),
  onPressed: () {},
  child: Text('Forjá tu producto'),
)
```

---

## Patrones canónicos

### CTA principal (forja sobre graphite, brasa glow)

| Stack | Snippet |
|---|---|
| Tailwind | `bg-forja-500 text-graphite-800 shadow-brasa` |
| CSS | `background: var(--color-forja-500); color: var(--color-text-on-forja); box-shadow: var(--shadow-brasa);` |
| TS | `backgroundColor: forja[500], color: graphite[800], boxShadow: shadows.brasa` |

### Card (graphite-600 sobre canvas, ember-2 elevation)

| Stack | Snippet |
|---|---|
| Tailwind | `bg-graphite-600 border border-graphite-500 rounded-lg shadow-ember-2 p-6` |
| CSS | `background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); border-radius: var(--radius-lg); box-shadow: var(--shadow-ember-2); padding: var(--spacing-6);` |

### Texto on dark canvas

| Caso | Token |
|---|---|
| Texto principal | `acero-100` (Tailwind: `text-acero-100`) |
| Texto soft | `acero-300` |
| Texto muted | `acero-500` |
| Texto sobre forja-500 | `graphite-800` |

### Estados

| Estado | Color |
|---|---|
| Action default | `forja-500` |
| Action hover | `forja-400` |
| Action pressed | `forja-600` |
| Error | `forja-quemado` (#C0392B) |
| Success | `patina-acero` (#2D6A4F) |
| Warn | `forja-300` |

---

## Anti-patrones

❌ **NO redefinir tokens locales**:

```css
/* MAL */
:root {
  --primary-color: #f97316;
  --bg-color: #1c1917;
}
```

```css
/* BIEN */
@import "@monstruo/design-tokens/css";

.mi-componente {
  background: var(--color-graphite-700);
  color: var(--color-acero-100);
}
```

❌ **NO usar hex literales en componentes** (rompe la fuente única de verdad).

❌ **NO crear "tu propia paleta extendida"** sin actualizar primero `kernel/brand/brand_dna.py` y este package.

❌ **NO usar naming genérico** (`primary`, `secondary`, `gray`, `dark`, `light`) — el test de paridad lo detectará y romperá.

---

## Migración desde un proyecto existente

Si tu proyecto tiene paleta propia con naming genérico, la migración es:

1. Identificar tu paleta actual: `grep -r "primary\|secondary\|gray-" src/`
2. Mapear cada color al equivalente del Monstruo (usar `docs/PALETA.md`)
3. Reemplazar imports/tokens uno a uno
4. Borrar tu archivo `tokens.css` o `colors.ts` local
5. Importar `@monstruo/design-tokens`
6. Correr el linter del Brand DNA: si tu proyecto incluye tests on-brand, rerun

Ejemplo real: `apps/mobile/lib/theme/monstruo_theme.dart` (Sprint Mobile 1, Hilo Ejecutor) está pendiente de migrar de paleta cyan/purple/mint a `flutter/monstruo_tokens.dart` de este package.

---

## Soporte

- README global: `packages/design-tokens/README.md`
- Paleta visual: `packages/design-tokens/docs/PALETA.md`
- Source of truth Python: `kernel/brand/brand_dna.py`
- DSC firma: DSC-G-004 (Brand Engine), DSC-MO-002 (paleta forja+graphite+acero)

— Hilo Catastro, Sprint Catastro-B 2026-05-06
