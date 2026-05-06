/**
 * El Monstruo — Design Tokens (entrypoint)
 *
 * Espejo TS de `kernel/brand/brand_dna.py`. Source of truth canónica.
 *
 * Uso:
 *   import { forja, graphite, acero, textStyle } from '@monstruo/design-tokens';
 *   const ctaBg = forja[500];
 *
 * Nunca importar `primary` o `secondary`. No existen aquí.
 *
 * DSCs aplicados: G-004 (Brand DNA), MO-002 (paleta forja+graphite+acero).
 */

export {
  forja,
  graphite,
  acero,
  semantic,
  FORJA_BASE,
  GRAPHITE_BASE,
  ACERO_BASE,
  FORBIDDEN_NAMES,
  getColor,
} from "./colors.js";
export type {
  ForjaScale,
  GraphiteScale,
  AceroScale,
  SemanticToken,
} from "./colors.js";

export {
  fontFamily,
  fontSize,
  fontWeight,
  lineHeight,
  letterSpacing,
  textStyle,
} from "./typography.js";
export type {
  FontFamilyToken,
  FontSizeToken,
  FontWeightToken,
  LineHeightToken,
  LetterSpacingToken,
  TextStyleToken,
} from "./typography.js";

export { spacing } from "./spacing.js";
export type { SpacingToken } from "./spacing.js";

export { radius } from "./radius.js";
export type { RadiusToken } from "./radius.js";

export { shadow } from "./shadows.js";
export type { ShadowToken } from "./shadows.js";

export { duration, easing, transition } from "./animations.js";
export type {
  DurationToken,
  EasingToken,
  TransitionToken,
} from "./animations.js";

// ── Metadata del package ─────────────────────────────────────────────
export const PACKAGE_VERSION = "0.1.0";
export const SOURCE_OF_TRUTH = "kernel/brand/brand_dna.py";
export const CANONICAL_PALETTE = ["forja", "graphite", "acero"] as const;
