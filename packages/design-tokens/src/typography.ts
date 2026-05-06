/**
 * El Monstruo — Tokens de Tipografía Canónicos
 *
 * Espejo TS del Brand DNA Python (`kernel/brand/brand_dna.py` BRAND_DNA["visual"]["fonts"]):
 *   - display = Bebas Neue (industrial, condensada, para titulares magna)
 *   - body    = Inter (humanista, legible, default)
 *   - mono    = JetBrains Mono (técnica, para code/datos crudos)
 *
 * Filosofía DSC-MO-002: "brutalismo industrial refinado". Los display NO son
 * decorativos — son brutales y honestos. Los body son legibles sin ser blandos.
 * Los mono son para código/datos crudos, no para decorar UI.
 *
 * Escala tipográfica: razón perfecta cuarta (1.333) escalada desde 12px base.
 * Nunca escalar a ojo.
 */

// ── Familias canónicas ───────────────────────────────────────────────
export const fontFamily = {
  display: '"Bebas Neue", "Bebas", "Impact", system-ui, sans-serif',
  body:
    '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ' +
    '"Helvetica Neue", Arial, sans-serif',
  mono:
    '"JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, ' +
    'Menlo, Consolas, monospace',
} as const;

// ── Escala de tamaños (rem; base 16px = 1rem) ────────────────────────
// Razón cuarta perfecta (1.333), redondeada a múltiplos limpios.
export const fontSize = {
  "xs": "0.75rem", // 12px
  "sm": "0.875rem", // 14px
  "base": "1rem", // 16px
  "lg": "1.125rem", // 18px
  "xl": "1.25rem", // 20px
  "2xl": "1.5rem", // 24px
  "3xl": "2rem", // 32px
  "4xl": "2.5rem", // 40px
  "5xl": "3.5rem", // 56px (display magna)
  "6xl": "4.5rem", // 72px (display titánica, hero del Monstruo)
} as const;

// ── Pesos canónicos ──────────────────────────────────────────────────
// Bebas Neue solo tiene 400 (regular). Inter usa 400/500/600/700.
// JetBrains Mono usa 400/500/700.
export const fontWeight = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;

// ── Line heights ─────────────────────────────────────────────────────
// Display = tight (energía), body = relaxed (lectura), mono = body+
export const lineHeight = {
  tight: 1.0, // Bebas display, headlines impacto
  snug: 1.25, // titulares H2/H3
  normal: 1.5, // body Inter default
  relaxed: 1.65, // párrafos largos
  loose: 1.85, // notas al pie
} as const;

// ── Letter spacing ───────────────────────────────────────────────────
export const letterSpacing = {
  tighter: "-0.04em", // display titánico
  tight: "-0.02em", // headlines
  normal: "0",
  wide: "0.025em", // CTAs en mayúsculas
  wider: "0.05em", // micro-labels (UPPERCASE pequeño)
  widest: "0.1em", // tracking forja-bramante (logos)
} as const;

// ── Estilos compuestos (componibles directamente) ────────────────────
// Cada uno mapea a un caso de uso documentado del Monstruo.
export const textStyle = {
  // Display — Bebas Neue
  "display-titanic": {
    fontFamily: fontFamily.display,
    fontSize: fontSize["6xl"],
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.tight,
    letterSpacing: letterSpacing.tighter,
    textTransform: "uppercase" as const,
  },
  "display-magna": {
    fontFamily: fontFamily.display,
    fontSize: fontSize["5xl"],
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.tight,
    letterSpacing: letterSpacing.tight,
    textTransform: "uppercase" as const,
  },
  // Headlines — Inter heavy
  "headline-1": {
    fontFamily: fontFamily.body,
    fontSize: fontSize["4xl"],
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.snug,
    letterSpacing: letterSpacing.tight,
  },
  "headline-2": {
    fontFamily: fontFamily.body,
    fontSize: fontSize["3xl"],
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.snug,
    letterSpacing: letterSpacing.tight,
  },
  "headline-3": {
    fontFamily: fontFamily.body,
    fontSize: fontSize["2xl"],
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.snug,
    letterSpacing: letterSpacing.normal,
  },
  // Body — Inter regular
  "body-large": {
    fontFamily: fontFamily.body,
    fontSize: fontSize.lg,
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  "body-default": {
    fontFamily: fontFamily.body,
    fontSize: fontSize.base,
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.normal,
  },
  "body-small": {
    fontFamily: fontFamily.body,
    fontSize: fontSize.sm,
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.normal,
  },
  // CTAs / botones — Inter semibold + tracking wide
  "cta": {
    fontFamily: fontFamily.body,
    fontSize: fontSize.base,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.wide,
  },
  // Micro-labels (UPPERCASE pequeño, tracking wide)
  "label-micro": {
    fontFamily: fontFamily.body,
    fontSize: fontSize.xs,
    fontWeight: fontWeight.medium,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.wider,
    textTransform: "uppercase" as const,
  },
  // Mono — JetBrains Mono
  "mono-default": {
    fontFamily: fontFamily.mono,
    fontSize: fontSize.sm,
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  "mono-small": {
    fontFamily: fontFamily.mono,
    fontSize: fontSize.xs,
    fontWeight: fontWeight.regular,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.normal,
  },
} as const;

export type FontFamilyToken = keyof typeof fontFamily;
export type FontSizeToken = keyof typeof fontSize;
export type FontWeightToken = keyof typeof fontWeight;
export type LineHeightToken = keyof typeof lineHeight;
export type LetterSpacingToken = keyof typeof letterSpacing;
export type TextStyleToken = keyof typeof textStyle;
