/**
 * El Monstruo — Tokens de Animación
 *
 * Filosofía: el Monstruo no rebota. No "bouncy springs". El ritmo es
 * deliberado, mecánico, industrial. Curvas asimétricas que sugieren
 * peso (como una pieza de metal que cae con inercia).
 *
 * Duraciones discretas — instant / quick / steady / massive — cada una
 * tiene un caso de uso, no se elige a ojo.
 */

// ── Duraciones canónicas ─────────────────────────────────────────────
export const duration = {
  instant: "60ms", // micro-feedback (hover, active)
  quick: "120ms", // transiciones de estado UI (toggle, tab)
  steady: "240ms", // entrada/salida de paneles, popovers
  ample: "400ms", // transiciones magna (modales, drawers)
  massive: "640ms", // hero choreography, escenas iniciales
  forge: "960ms", // animaciones de forja (logo render, splash)
} as const;

// ── Curvas (cubic-bezier) ────────────────────────────────────────────
// Naming con identidad: nada de "ease-in-out".
export const easing = {
  // Lineal — para opacidad pura, no usar para movimiento
  flat: "cubic-bezier(0, 0, 1, 1)",
  // Curva de "metal pesado cayendo" — inicio rápido, asentamiento
  ingot: "cubic-bezier(0.16, 0.84, 0.44, 1)",
  // Curva de "extracción de pieza forjada" — salida con peso
  extract: "cubic-bezier(0.55, 0, 0.84, 0.16)",
  // Curva neutral para transiciones de UI standard
  standard: "cubic-bezier(0.4, 0, 0.2, 1)",
  // Curva de "chispa" — aceleración brusca, frenado seco (atención)
  spark: "cubic-bezier(0.7, 0, 0.3, 1)",
} as const;

// ── Transiciones predefinidas ────────────────────────────────────────
export const transition = {
  "color-quick": `color ${duration.quick} ${easing.standard}`,
  "bg-quick": `background-color ${duration.quick} ${easing.standard}`,
  "border-quick": `border-color ${duration.quick} ${easing.standard}`,
  "transform-steady": `transform ${duration.steady} ${easing.ingot}`,
  "opacity-quick": `opacity ${duration.quick} ${easing.flat}`,
  "all-steady": `all ${duration.steady} ${easing.standard}`,
} as const;

export type DurationToken = keyof typeof duration;
export type EasingToken = keyof typeof easing;
export type TransitionToken = keyof typeof transition;
