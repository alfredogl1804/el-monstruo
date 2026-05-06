# `@monstruo/design-tokens`

> Tokens de diseño canónicos del Monstruo. Espejo TS / CSS / Tailwind / Flutter de `kernel/brand/brand_dna.py`. Source of truth única — todo proyecto del portfolio importa de aquí.

**Versión:** 0.1.0  
**DSCs aplicados:** DSC-G-004 (Brand Engine), DSC-MO-002 (paleta forja+graphite+acero)  
**Owner:** Hilo Catastro

---

## ¿Qué resuelve?

Antes de este package, cada proyecto del portfolio tenía que redefinir sus colores, tipografías y spacing. El resultado eran 20 paletas divergentes, naming genérico (`primary`, `secondary`, `gray`) y violaciones del Brand DNA — el caso más doloroso fue el theme de `apps/mobile/lib/theme/monstruo_theme.dart` con `Inspired by ChatGPT, Claude, Gemini latest interfaces` que detonó **DSC-G-008**.

A partir de aquí: todo proyecto nuevo importa este package y nace on-brand sin discutir colores. Los proyectos existentes migran progresivamente.

---

## Paleta canónica

| Familia | Hex base | Caso de uso |
|---|---|---|
| **forja** | `#F97316` (500) | Color de marca, llama, CTA, focus, brasa de forja |
| **graphite** | `#1C1917` (700) | Fondo, metal templado, superficies oscuras |
| **acero** | `#A8A29E` (400) | Neutro medio, texto suave, bordes |

Cada familia tiene escala 50–900. Naming **inviolable**: nunca `primary`, `secondary`, `gray`, `dark`, `light`. Solo `forja-500`, `graphite-700`, `acero-300`.

---

## Tipografía canónica

| Rol | Familia | Filosofía |
|---|---|---|
| **display** | Bebas Neue | Industrial, condensada, brutalismo refinado |
| **body** | Inter | Humanista, legible, default |
| **mono** | JetBrains Mono | Técnica, código y datos crudos |

Escala tipográfica `xs` → `6xl` con razón cuarta perfecta (1.333). 6 estilos compuestos predefinidos: `display-titanic`, `display-magna`, `headline-1/2/3`, `body-large/default/small`, `cta`, `label-micro`, `mono-default/small`.

---

## Cómo se usa

### TypeScript / JavaScript

```ts
import { forja, graphite, acero, textStyle } from "@monstruo/design-tokens";

const ctaStyle = {
  backgroundColor: forja[500],
  color: graphite[800],
  ...textStyle.cta,
};
```

### CSS (sin framework)

```css
@import "@monstruo/design-tokens/css";
@import "@monstruo/design-tokens/css/reset"; /* opcional */

.cta {
  background-color: var(--color-forja-500);
  color: var(--color-text-on-forja);
  font-family: var(--font-family-body);
  font-weight: var(--font-weight-semibold);
  letter-spacing: var(--letter-spacing-wide);
}
```

### Tailwind v4 (recomendado, vigente al 2026-05-06)

```css
/* tu archivo CSS principal */
@import "tailwindcss";
@import "@monstruo/design-tokens/tailwind/theme";
```

Después usás `bg-forja-500`, `text-graphite-700`, `border-acero-300`, `font-display`, etc. en tu HTML/JSX.

### Tailwind v3 (legacy)

```js
// tailwind.config.js
module.exports = {
  presets: [require("@monstruo/design-tokens/tailwind/preset")],
  content: ["./src/**/*.{html,tsx,jsx}"],
};
```

### Flutter / Dart

```dart
import 'package:el_monstruo/tokens/monstruo_tokens.dart';

Container(
  color: MonstruoTokens.forja[500],
  padding: EdgeInsets.all(MonstruoTokens.space4),
  child: Text(
    'CTA',
    style: TextStyle(color: MonstruoTokens.textOnForja),
  ),
)
```

---

## Estructura del package

```
packages/design-tokens/
├── package.json
├── README.md
├── src/
│   ├── colors.ts        — Paleta forja/graphite/acero + escalas + semantic tokens
│   ├── typography.ts    — Familias + escalas + estilos compuestos
│   ├── spacing.ts       — Escala 4px (0–32, pasos discretos)
│   ├── radius.ts        — Border radius (none → full)
│   ├── shadows.ts       — Elevación ember-1/2/3 + brasa (forja glow)
│   ├── animations.ts    — Duraciones (instant→forge) + curvas (ingot, spark, …)
│   └── index.ts         — Barrel export
├── css/
│   ├── tokens.css       — CSS Custom Properties
│   └── reset.css        — Reset mínimo on-brand
├── tailwind/
│   ├── preset.js        — Tailwind v3 preset
│   └── theme.css        — Tailwind v4 @theme
├── flutter/
│   └── monstruo_tokens.dart  — Mirror Dart para apps Flutter
├── tests/
│   └── parity_with_brand_dna.test.js  — Verifica paridad kernel ↔ package
└── docs/
    ├── PALETA.md
    └── COMO_USAR.md
```

---

## Source of truth

El archivo canónico es `kernel/brand/brand_dna.py` (Python, en el kernel del Monstruo). Este package es un **espejo compilado** para consumo de proyectos JS/TS/Flutter.

**Regla:** cualquier cambio de paleta debe hacerse primero en `brand_dna.py` y propagarse aquí. El test `tests/parity_with_brand_dna.test.js` lo enforce.

---

## Cómo se valida

```bash
cd packages/design-tokens
node --test tests/
```

Esperado: 8/8 verde. Los tests verifican:

1. `kernel/brand/brand_dna.py` declara los 3 hex canónicos
2–6. Cada superficie del package (TS, CSS, Tailwind v3, Tailwind v4, Flutter) usa los mismos hex
7. Ningún archivo del package usa naming prohibido (`primary`, `secondary`, `gray`)
8. `package.json` declara metadata canónica del Monstruo

---

## Próximos consumidores

- **Sprint Mobile 1 (Hilo Ejecutor):** reemplazar `apps/mobile/lib/theme/monstruo_theme.dart` (paleta cyan/purple/mint que viola DSC-G-004) por `MonstruoTokens` de `flutter/monstruo_tokens.dart`
- **Marketplace Interiorismo:** importar desde su frontend Tailwind
- **CIP frontend:** importar desde su frontend Next.js
- **Command Center:** ya tiene Brand DNA en kernel, puede consumir vía CSS imports
- **Cualquier empresa-hija nueva:** scaffold web-db-user agrega este package por defecto (TODO: actualizar plantilla scaffold)

---

## Versionado

`0.1.0` — Initial release. Tokens canónicos congelados con base en BRAND_DNA Sprint 82.

Cualquier breaking change requiere bump de minor (0.x.0) y debe estar firmado por DSC-G-004 actualizado.

---

## Anti-patrones (lo que este package NO es)

- ❌ Una colección de colores arbitraria — todo deriva del Brand DNA del kernel
- ❌ Un wrapper de Tailwind UI / shadcn / Material — esos son sistemas de componentes, esto son **tokens** atómicos
- ❌ Una librería de iconos — usar otro package
- ❌ Una librería de componentes React — usar otro package (futuro `@monstruo/forja-ui`)

---

— Hilo Catastro, Sprint Catastro-B 2026-05-06
