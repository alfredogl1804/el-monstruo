/**
 * El Monstruo — Tokens de Spacing
 *
 * Escala base 4px. Razón geométrica × 2 cada paso mayor (4, 8, 16, 32, 64).
 * Pasos intermedios para ajuste fino. Sin spacing arbitrario.
 *
 * Filosofía: "templanza industrial" — espacios deliberados, no rellenos
 * decorativos. Cada paso tiene un caso de uso documentado.
 */

// ── Escala canónica (rem; 0.25rem = 4px en base 16) ──────────────────
export const spacing = {
  "0": "0",
  "0.5": "0.125rem", // 2px — separación micro (íconos pegados)
  "1": "0.25rem", // 4px — base
  "1.5": "0.375rem", // 6px — gap inline tight
  "2": "0.5rem", // 8px — gap default
  "3": "0.75rem", // 12px — padding compacto
  "4": "1rem", // 16px — padding default
  "5": "1.25rem", // 20px — separación de secciones cortas
  "6": "1.5rem", // 24px — section padding mediano
  "8": "2rem", // 32px — section padding grande
  "10": "2.5rem", // 40px — separación entre bloques
  "12": "3rem", // 48px — separación magna entre módulos
  "16": "4rem", // 64px — separación titánica (hero ↔ content)
  "20": "5rem", // 80px — top padding hero
  "24": "6rem", // 96px — separación de manifiesto
  "32": "8rem", // 128px — paus entre capítulos
} as const;

export type SpacingToken = keyof typeof spacing;
