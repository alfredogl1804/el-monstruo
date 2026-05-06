/**
 * El Monstruo — Tokens de Border Radius
 *
 * Filosofía: brutalismo industrial refinado.
 * Lo crudo y lo metálico tiende a ángulos rectos. Suavizamos solo cuando
 * la usabilidad lo exige (botones tactiles, inputs). NUNCA pills genéricas
 * por moda.
 */

export const radius = {
  none: "0", // metal cortado a sierra
  sm: "0.25rem", // 4px — chips, badges técnicos
  md: "0.5rem", // 8px — cards, inputs
  lg: "0.75rem", // 12px — botones magna
  xl: "1rem", // 16px — modales premium
  "2xl": "1.5rem", // 24px — heros con curvatura suave
  full: "9999px", // pill completa (raro: solo avatares + tags fila)
} as const;

export type RadiusToken = keyof typeof radius;
